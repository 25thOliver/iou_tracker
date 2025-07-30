from django.shortcuts import render

# debts/views.py
from rest_framework import generics, status, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum, Avg, Count
from django.utils import timezone
from decimal import Decimal

from .models import Debt, PaymentPlan, PaymentRecord, ReminderTemplate, ReminderLog
from .serializers import (
    DebtListSerializer, DebtDetailSerializer, DebtCreateUpdateSerializer,
    PaymentPlanSerializer, PaymentPlanCreateSerializer,
    PaymentRecordSerializer, PaymentRecordCreateSerializer,
    ReminderTemplateSerializer, SendReminderSerializer, DebtStatsSerializer
)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class DebtListCreateView(generics.ListCreateAPIView):
    """
    GET: List all debts with filtering and search
    POST: Create a new debt
    """
    queryset = Debt.objects.all()
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['debtor_name', 'debtor_email', 'description']
    ordering_fields = ['created_at', 'amount', 'due_date', 'reminder_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DebtCreateUpdateSerializer
        return DebtListSerializer
    
    def get_queryset(self):
        queryset = Debt.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by overdue
        is_overdue = self.request.query_params.get('overdue')
        if is_overdue == 'true':
            queryset = queryset.filter(
                due_date__lt=timezone.now().date(),
                status='active'
            )
        
        # Filter by payment plan
        has_payment_plan = self.request.query_params.get('has_payment_plan')
        if has_payment_plan == 'true':
            queryset = queryset.filter(payment_plan_offered=True)
        elif has_payment_plan == 'false':
            queryset = queryset.filter(payment_plan_offered=False)
        
        # Filter by amount range
        min_amount = self.request.query_params.get('min_amount')
        max_amount = self.request.query_params.get('max_amount')
        if min_amount:
            queryset = queryset.filter(amount__gte=min_amount)
        if max_amount:
            queryset = queryset.filter(amount__lte=max_amount)
        
        return queryset

class DebtDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve debt details with related data
    PUT/PATCH: Update debt
    DELETE: Delete debt
    """
    queryset = Debt.objects.all()
    lookup_field = 'id'
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return DebtCreateUpdateSerializer
        return DebtDetailSerializer

class PaymentPlanCreateView(generics.CreateAPIView):
    """Create a payment plan for a debt"""
    serializer_class = PaymentPlanCreateSerializer
    
    def perform_create(self, serializer):
        debt = get_object_or_404(Debt, id=self.kwargs['debt_id'])
        
        # Calculate next due date based on frequency
        start_date = serializer.validated_data['start_date']
        frequency = serializer.validated_data['frequency']
        
        if frequency == 'weekly':
            next_due = start_date + timezone.timedelta(weeks=1)
        elif frequency == 'bi_weekly':
            next_due = start_date + timezone.timedelta(weeks=2)
        elif frequency == 'monthly':
            next_due = start_date + timezone.timedelta(days=30)
        else:  # custom
            next_due = start_date + timezone.timedelta(days=7)  # default to weekly
        
        payment_plan = serializer.save(
            debt=debt,
            next_due_date=next_due
        )
        
        # Update debt to reflect payment plan offered
        debt.payment_plan_offered = True
        debt.save()

class PaymentPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete a payment plan"""
    queryset = PaymentPlan.objects.all()
    serializer_class = PaymentPlanSerializer
    lookup_field = 'id'

class PaymentRecordCreateView(generics.CreateAPIView):
    """Record a payment for a debt"""
    serializer_class = PaymentRecordCreateSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        debt = get_object_or_404(Debt, id=self.kwargs['debt_id'])
        context['debt'] = debt
        return context
    
    def perform_create(self, serializer):
        debt = get_object_or_404(Debt, id=self.kwargs['debt_id'])
        payment_amount = serializer.validated_data['amount']
        
        # Create the payment record
        payment = serializer.save(debt=debt)
        
        # Update the debt amount
        debt.amount -= payment_amount
        
        # If debt is fully paid, mark as paid
        if debt.amount <= 0:
            debt.status = 'paid'
            debt.date_paid = timezone.now()
            debt.amount = Decimal('0.00')
        
        debt.save()
        
        # Update payment plan if exists
        if hasattr(debt, 'payment_plan'):
            payment_plan = debt.payment_plan
            payment.payment_plan = payment_plan
            payment.save()
            
            # Update installments paid
            payment_plan.paid_installments += 1
            
            # Check if payment plan is completed
            if payment_plan.paid_installments >= payment_plan.total_installments:
                payment_plan.status = 'completed'
            
            payment_plan.save()

class PaymentRecordListView(generics.ListAPIView):
    """List all payments for a debt"""
    serializer_class = PaymentRecordSerializer
    
    def get_queryset(self):
        debt_id = self.kwargs['debt_id']
        return PaymentRecord.objects.filter(debt_id=debt_id)

class ReminderTemplateListCreateView(generics.ListCreateAPIView):
    """List and create reminder templates"""
    queryset = ReminderTemplate.objects.filter(is_active=True)
    serializer_class = ReminderTemplateSerializer
    ordering = ['tone', 'min_reminder_count']

class ReminderTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update or delete reminder template"""
    queryset = ReminderTemplate.objects.all()
    serializer_class = ReminderTemplateSerializer
    lookup_field = 'id'

@api_view(['POST'])
def send_reminder(request, debt_id):
    """Send a reminder email for a specific debt"""
    debt = get_object_or_404(Debt, id=debt_id)
    serializer = SendReminderSerializer(data=request.data)
    
    if serializer.is_valid():
        # This is where we'll integrate with Celery task
        # For now, we'll just create a reminder log entry
        
        if serializer.validated_data.get('template_id'):
            template = get_object_or_404(
                ReminderTemplate, 
                id=serializer.validated_data['template_id']
            )
            subject = template.subject_template
            message = template.body_template
        else:
            template = None
            subject = serializer.validated_data['custom_subject']
            message = serializer.validated_data['custom_message']
        
        # Replace template variables
        context = {
            'name': debt.debtor_name,
            'amount': debt.amount,
            'description': debt.description,
            'due_date': debt.due_date,
            'days_overdue': debt.days_overdue,
            'reminder_count': debt.reminder_count + 1,
        }
        
        for key, value in context.items():
            subject = subject.replace(f'{{{key}}}', str(value))
            message = message.replace(f'{{{key}}}', str(value))
        
        # Create reminder log
        reminder_log = ReminderLog.objects.create(
            debt=debt,
            template_used=template,
            subject=subject,
            message_body=message,
            recipient_email=debt.debtor_email,
            status='sent'  # In real implementation, this would be set by email service
        )
        
        # Update debt reminder tracking
        debt.reminder_count += 1
        debt.last_reminder_sent = timezone.now()
        debt.save()
        
        return Response({
            'message': 'Reminder sent successfully',
            'reminder_id': reminder_log.id
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def debt_statistics(request):
    """Get debt statistics dashboard data"""
    # Basic counts and sums
    total_debts = Debt.objects.count()
    active_debts = Debt.objects.filter(status='active').count()
    paid_debts = Debt.objects.filter(status='paid').count()
    overdue_debts = Debt.objects.filter(
        due_date__lt=timezone.now().date(),
        status='active'
    ).count()
    
    # Financial stats
    total_amount_owed = Debt.objects.filter(status='active').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    total_amount_paid = Debt.objects.aggregate(
        total=Sum('original_amount') - Sum('amount')
    )
    total_amount_paid = (
        (total_amount_paid['total__sum'] or Decimal('0.00')) - 
        (total_amount_paid['amount__sum'] or Decimal('0.00'))
    )
    
    average_debt = Debt.objects.filter(status='active').aggregate(
        avg=Avg('amount')
    )['avg'] or Decimal('0.00')
    
    # Reminder stats
    total_reminders = ReminderLog.objects.count()
    
    stats_data = {
        'total_debts': total_debts,
        'total_amount_owed': total_amount_owed,
        'total_amount_paid': total_amount_paid,
        'active_debts': active_debts,
        'overdue_debts': overdue_debts,
        'paid_debts': paid_debts,
        'average_debt_amount': average_debt,
        'total_reminders_sent': total_reminders,
    }
    
    serializer = DebtStatsSerializer(stats_data)
    return Response(serializer.data)

@api_view(['GET'])
def overdue_debts(request):
    """Get all overdue debts"""
    overdue_debts = Debt.objects.filter(
        due_date__lt=timezone.now().date(),
        status='active'
    ).order_by('due_date')
    
    serializer = DebtListSerializer(overdue_debts, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def mark_debt_paid(request, debt_id):
    """Mark a debt as fully paid"""
    debt = get_object_or_404(Debt, id=debt_id)
    
    debt.status = 'paid'
    debt.date_paid = timezone.now()
    debt.amount = Decimal('0.00')
    debt.save()
    
    return Response({
        'message': 'Debt marked as paid',
        'debt_id': debt.id
    }, status=status.HTTP_200_OK)

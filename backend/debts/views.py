# debts/views.py - Updated with authentication and permissions
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated # Add this import
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from decimal import Decimal
from django.utils import timezone
import uuid

from .models import Debt, PaymentPlan, PaymentRecord, ReminderTemplate, ReminderLog
from .serializers import (
    DebtListSerializer, DebtDetailSerializer, DebtCreateUpdateSerializer,
    PaymentPlanSerializer, PaymentPlanCreateSerializer,
    PaymentRecordSerializer, PaymentRecordCreateSerializer,
    ReminderTemplateSerializer, SendReminderSerializer, DebtStatsSerializer
)
from .permissions import IsCreditor, IsDebtRelated, IsCreditorOrDebtor
from .filters import DebtFilter
from notifications.tasks import (
    send_debt_created_notification_task,
    send_payment_confirmation_task,
    send_debt_reminder_task
)
import logging

logger = logging.getLogger(__name__)

class DebtListCreateView(generics.ListCreateAPIView):
    """List and create debts - users only see their own debts as creditor"""
    serializer_class = DebtListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = DebtFilter
    search_fields = ['debtor_name', 'debtor_email', 'description']
    ordering_fields = ['date_created', 'due_date', 'amount', 'status']
    ordering = ['-date_created']

    def get_queryset(self):
        """Filter debts to show only those where user is creditor or debtor (by email)"""
        from django.db.models import Q
        user = self.request.user
        return Debt.objects.filter(Q(creditor=user) | Q(debtor_email=user.email))

    def get_serializer_class(self):
        """Use different serializers for list vs create"""
        if self.request.method == 'POST':
            return DebtCreateUpdateSerializer
        return DebtListSerializer

    def perform_create(self, serializer):
        """Set the current user as creditor when creating debt and log notification"""
        debt = serializer.save(creditor=self.request.user)

        # Send notification to debtor about new debt
        try:
            send_debt_created_notification_task.delay(debt.id)
            logger.info(f"Debt created notification queued for debt {debt.id}")
        except Exception as e:
            logger.error(f"Failed to queue debt created notification: {str(e)}")

        # Create notification log for creditor
        try:
            from notifications.models import NotificationLog
            NotificationLog.objects.create(
                user=self.request.user,
                notification_type='debt_created',
                channel='app',
                status='sent',
                subject=f"New Debt Created: {debt.amount} for {debt.debtor_name}",
                message_body=f"You created a new debt for {debt.debtor_name} ({debt.debtor_email}) of {debt.amount} ({debt.description})",
                related_object_id=str(debt.id)
            )
            # Also create notification log for debtor if they exist as a user
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                debtor_user = User.objects.filter(email=debt.debtor_email).first()
                if debtor_user:
                    NotificationLog.objects.create(
                        user=debtor_user,
                        notification_type='debt_created',
                        channel='app',
                        status='sent',
                        subject=f"New Debt Assigned: {debt.amount} from {self.request.user.get_full_name() or self.request.user.username}",
                        message_body=f"A new debt of {debt.amount} ({debt.description}) was assigned to you by {self.request.user.get_full_name() or self.request.user.username}.",
                        related_object_id=str(debt.id)
                    )
            except Exception as e:
                logger.error(f"Failed to create notification log for debtor: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to create notification log: {str(e)}")



class DebtDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a debt - only by creditor"""
    serializer_class = DebtDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        """Allow access to debts where user is creditor or debtor (by email)"""
        from django.db.models import Q
        user = self.request.user
        return Debt.objects.filter(Q(creditor=user) | Q(debtor_email=user.email))

    def get_serializer_class(self):
        """Use update serializer for PUT/PATCH requests"""
        if self.request.method in ['PUT', 'PATCH']:
            return DebtCreateUpdateSerializer
        return DebtDetailSerializer


class PaymentPlanListView(generics.ListAPIView):
    """List payment plans for user's debts"""
    serializer_class = PaymentPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Only show payment plans for user's debts"""
        return PaymentPlan.objects.filter(debt__creditor=self.request.user)


class PaymentPlanDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a payment plan"""
    serializer_class = PaymentPlanSerializer
    permission_classes = [permissions.IsAuthenticated, IsDebtRelated]
    lookup_field = 'id'

    def get_queryset(self):
        return PaymentPlan.objects.filter(debt__creditor=self.request.user)


class PaymentPlanCreateView(generics.CreateAPIView):
    """Create a payment plan for a debt"""
    serializer_class = PaymentPlanCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Ensure user owns the debt before creating payment plan"""
        debt = serializer.validated_data['debt']
        if debt.creditor != self.request.user:
            raise permissions.PermissionDenied("You can only create payment plans for your own debts.")

        # Calculate next_due_date logic
        from datetime import timedelta
        frequency = serializer.validated_data['frequency']
        frequency_days = {
            'weekly': 7,
            'biweekly': 14,
            'monthly': 30,
            'quarterly': 90
        }

        next_due = timezone.now().date() + timedelta(days=frequency_days.get(frequency, 30))
        serializer.save(next_due_date=next_due)


class PaymentRecordListView(generics.ListAPIView):
    """List payment records for user's debts"""
    serializer_class = PaymentRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Only show payments for user's debts"""
        return PaymentRecord.objects.filter(debt__creditor=self.request.user)


class PaymentRecordCreateView(generics.CreateAPIView):
    """Create a payment record for a debt"""
    serializer_class = PaymentRecordCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """Ensure user owns the debt and update debt amount"""
        debt = serializer.validated_data['debt']
        if debt.creditor != self.request.user:
            raise permissions.PermissionDenied("You can only record payments for your own debts.")

        payment_amount = serializer.validated_data['amount']

        # Save the payment record
        payment = serializer.save()

        # Update debt amount
        debt.amount -= payment_amount
        if debt.amount <= 0:
            debt.amount = Decimal('0.00')
            debt.status = 'paid'
            debt.date_paid = timezone.now()
        debt.save()

        # Update payment plan if exists
        if hasattr(debt, 'payment_plan'):
            payment_plan = debt.payment_plan
            payment_plan.paid_installments += 1
            if payment_plan.paid_installments >= payment_plan.total_installments:
                payment_plan.status = 'completed'
            payment_plan.save()


class ReminderTemplateListCreateView(generics.ListCreateAPIView):
    """List and create reminder templates - could be user-specific or global"""
    queryset = ReminderTemplate.objects.all()
    serializer_class = ReminderTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]


class ReminderTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a reminder template"""
    queryset = ReminderTemplate.objects.all()
    serializer_class = ReminderTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_reminder(request, debt_id):
    """Send a reminder for a specific debt - only by creditor"""
    try:
        debt = Debt.objects.get(id=debt_id, creditor=request.user)
    except Debt.DoesNotExist:
        return Response({'error': 'Debt not found or access denied'}, status=status.HTTP_404_NOT_FOUND)

    serializer = SendReminderSerializer(data=request.data)
    if serializer.is_valid():
        custom_subject = serializer.validated_data.get('custom_subject', '')
        custom_message = serializer.validated_data.get('custom_message', '')
        template_id = serializer.validated_data.get('template_id')

        try:
            message = ""
            template = None # Initialize template to None

            # Determine subject and message
            if template_id:
                try:
                    template = ReminderTemplate.objects.get(id=template_id)
                    subject = template.subject_template
                    message = template.body_template
                except ReminderTemplate.DoesNotExist:
                    return Response({'error': 'Template not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                # Provide default subject and message if custom ones are not provided
                subject = custom_subject or f"Reminder: Debt for {debt.description}"
                message = custom_message or f"Friendly reminder: You owe {debt.amount} for {debt.description}"

            # Replace template variables in subject
            subject = subject.replace('{debtor_name}', debt.debtor_name)
            subject = subject.replace('{amount}', str(debt.amount))
            subject = subject.replace('{description}', debt.description)
            subject = subject.replace('{due_date}', str(debt.due_date) if debt.due_date else 'N/A')

            # Replace template variables in message
            message = message.replace('{debtor_name}', debt.debtor_name)
            message = message.replace('{amount}', str(debt.amount))
            message = message.replace('{description}', debt.description)
            message = message.replace('{due_date}', str(debt.due_date) if debt.due_date else 'N/A')

            # Create reminder log
            reminder_log = ReminderLog.objects.create(
                debt=debt,
                recipient_email=debt.debtor_email,
                subject=subject,
                message_body=message,
                status='sent', # Set initial status, adjust if email sending is asynchronous
                template_used=template
            )

            debt.reminder_count += 1
            debt.last_reminder_sent = timezone.now()
            debt.save()

            send_debt_reminder_task.delay(debt.id) # Queue the notification task

            return Response({'message': 'Reminder sent successfully', 'reminder_id': reminder_log.id}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error sending reminder for debt {debt_id}: {str(e)}")
            return Response({'error': 'Failed to send reminder'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def debt_statistics(request):
    """Get debt statistics for the authenticated user"""
    user_debts = Debt.objects.filter(creditor=request.user)

    # Basic counts
    total_debts = user_debts.count()
    active_debts = user_debts.filter(status='active').count()
    paid_debts = user_debts.filter(status='paid').count()
    overdue_debts = user_debts.filter(
        due_date__lt=timezone.now().date(),
        status='active'
    ).count()

    # Financial stats
    total_amount_owed = user_debts.filter(status='active').aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')

    # Calculate amount paid (original - current)
    original_total = user_debts.aggregate(
        total=Sum('original_amount')
    )['total'] or Decimal('0.00')

    current_total = user_debts.aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')

    total_amount_paid = original_total - current_total

    average_debt = user_debts.filter(status='active').aggregate(
        avg=Avg('amount')
    )['avg'] or Decimal('0.00')

    # Reminder stats
    total_reminders = ReminderLog.objects.filter(debt__creditor=request.user).count()

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
@permission_classes([IsAuthenticated])
def overdue_debts(request):
    """Get overdue debts for the authenticated user"""
    overdue = Debt.objects.filter(
        creditor=request.user,
        due_date__lt=timezone.now().date(),
        status='active'
    )

    serializer = DebtListSerializer(overdue, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_debt_paid(request, debt_id):
    """Mark a debt as paid - only by creditor"""
    try:
        debt = Debt.objects.get(id=debt_id, creditor=request.user)
    except Debt.DoesNotExist:
        return Response({'error': 'Debt not found or access denied'}, status=status.HTTP_404_NOT_FOUND)

    debt.status = 'paid'
    debt.amount = Decimal('0.00')
    debt.date_paid = timezone.now()
    debt.save()

    return Response({
        'message': 'Debt marked as paid successfully!',
        'debt_id': debt.id
    }, status=status.HTTP_200_OK)

# Add this to your existing views...

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_dashboard(request):
    """Get user dashboard with notification summary"""
    try:
        # Existing dashboard logic
        user_debts = Debt.objects.filter(
            Q(creditor=request.user) | Q(debtor=request.user)
        )

        total_owed_to_user = user_debts.filter(
            creditor=request.user, status='active'
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        total_user_owes = user_debts.filter(
            debtor=request.user, status='active'
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        # Add notification statistics
        from notifications.models import NotificationLog
        recent_notifications = NotificationLog.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]

        notification_summary = {
            'total_notifications': NotificationLog.objects.filter(user=request.user).count(),
            'unread_count': recent_notifications.filter(status='sent').count(),
            'recent_notifications': [
                {
                    'type': log.notification_type,
                    'channel': log.channel,
                    'status': log.status,
                    'created_at': log.created_at
                }
                for log in recent_notifications
            ]
        }

        return Response({
            'total_owed_to_user': total_owed_to_user,
            'total_user_owes': total_user_owes,
            'active_debts_count': user_debts.filter(status='active').count(),
            'settled_debts_count': user_debts.filter(status='settled').count(),
            'notifications': notification_summary
        })

    except Exception as e:
        logger.error(f"Error getting user dashboard: {str(e)}")
        return Response({
            'error': 'Failed to get dashboard data'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# iou-tracker/iou_tracker_backend/urls.py - Updated main URLs

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/debts/', include('debts.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/health/', lambda request: HttpResponse('OK')),
]


# iou-tracker/notifications/management/commands/setup_default_templates.py

from django.core.management.base import BaseCommand
from notifications.models import NotificationTemplate

class Command(BaseCommand):
    help = 'Setup default notification templates'

    def handle(self, *args, **options):
        templates = [
            {
                'name': 'Debt Reminder Email',
                'notification_type': 'debt_reminder',
                'channel': 'email',
                'subject_template': 'Friendly Reminder: Outstanding Debt of ${amount}',
                'body_template': '''Hi {user_name},

This is a friendly reminder about your outstanding debt with {creditor_name}.

Amount: ${amount}
Description: {description}
Due Date: {due_date}

Please consider settling this debt as soon as possible.

Best regards,
IOU Tracker Team'''
            },
            {
                'name': 'Debt Reminder SMS',
                'notification_type': 'debt_reminder',
                'channel': 'sms',
                'subject_template': '',
                'body_template': 'Hi {user_name}, reminder: You owe ${amount} to {creditor_name} for "{description}". Due: {due_date}. Please settle soon. -IOU Tracker'
            },
            {
                'name': 'Payment Confirmation Email',
                'notification_type': 'payment_confirmation',
                'channel': 'email',
                'subject_template': 'Payment Received: ${amount} from {debtor_name}',
                'body_template': '''Hi {user_name},

Great news! We've recorded a payment from {debtor_name}.

Payment Amount: ${amount}
Payment Date: {payment_date}
Debt Description: {debt_description}
Remaining Balance: ${remaining_amount}

Thank you for using IOU Tracker!

Best regards,
IOU Tracker Team'''
            },
            {
                'name': 'Payment Confirmation SMS',
                'notification_type': 'payment_confirmation',
                'channel': 'sms',
                'subject_template': '',
                'body_template': 'Payment received: ${amount} from {debtor_name} on {payment_date}. Remaining: ${remaining_amount}. -IOU Tracker'
            },
            {
                'name': 'Debt Created Email',
                'notification_type': 'debt_created',
                'channel': 'email',
                'subject_template': 'New Debt Record: ${amount} from {creditor_name}',
                'body_template': '''Hi {user_name},

{creditor_name} has created a new debt record for you.

Amount: ${amount}
Description: {description}
Due Date: {due_date}
Created: {created_date}

Please review this debt record in the IOU Tracker app.

Best regards,
IOU Tracker Team'''
            },
            {
                'name': 'Debt Created SMS',
                'notification_type': 'debt_created',
                'channel': 'sms',
                'subject_template': '',
                'body_template': 'New debt: ${amount} from {creditor_name} for "{description}". Due: {due_date}. Check IOU Tracker app. -IOU Tracker'
            }
        ]

        created_count = 0
        for template_data in templates:
            template, created = NotificationTemplate.objects.get_or_create(
                notification_type=template_data['notification_type'],
                channel=template_data['channel'],
                defaults=template_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created template: {template.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} notification templates')
        )

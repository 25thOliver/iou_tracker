# debts/serializers.py
from rest_framework import serializers
from .models import Debt, PaymentPlan, PaymentRecord, ReminderTemplate, ReminderLog
from decimal import Decimal

class PaymentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentRecord
        fields = [
            'id', 'amount', 'payment_method', 'reference_number', 
            'notes', 'date_paid', 'verified'
        ]
        read_only_fields = ['id', 'date_paid']

class PaymentPlanSerializer(serializers.ModelSerializer):
    payments = PaymentRecordSerializer(many=True, read_only=True)
    completion_percentage = serializers.ReadOnlyField()
    remaining_amount = serializers.ReadOnlyField()
    
    class Meta:
        model = PaymentPlan
        fields = [
            'id', 'installment_amount', 'frequency', 'total_installments',
            'paid_installments', 'start_date', 'next_due_date', 'status',
            'completion_percentage', 'remaining_amount', 'payments', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class ReminderLogSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source='template_used.name', read_only=True)
    
    class Meta:
        model = ReminderLog
        fields = [
            'id', 'subject', 'recipient_email', 'sent_at', 'status',
            'template_name', 'opened_at', 'clicked_at'
        ]
        read_only_fields = ['id', 'sent_at']

class DebtListSerializer(serializers.ModelSerializer):
    """Serializer for debt list view - lighter fields"""
    is_overdue = serializers.ReadOnlyField()
    days_overdue = serializers.ReadOnlyField()
    amount_paid = serializers.ReadOnlyField()
    
    class Meta:
        model = Debt
        fields = [
            'id', 'debtor_name', 'debtor_email', 'amount', 'original_amount',
            'description', 'status', 'due_date', 'reminder_count',
            'payment_plan_offered', 'is_overdue', 'days_overdue', 
            'amount_paid', 'created_at'
        ]

class DebtDetailSerializer(serializers.ModelSerializer):
    """Serializer for debt detail view - all fields and related data"""
    payment_plan = PaymentPlanSerializer(read_only=True)
    payments = PaymentRecordSerializer(many=True, read_only=True)
    reminder_logs = ReminderLogSerializer(many=True, read_only=True)
    is_overdue = serializers.ReadOnlyField()
    days_overdue = serializers.ReadOnlyField()
    amount_paid = serializers.ReadOnlyField()
    
    class Meta:
        model = Debt
        fields = [
            'id', 'debtor_name', 'debtor_email', 'debtor_phone', 'amount',
            'original_amount', 'description', 'due_date', 'status',
            'reminder_count', 'last_reminder_sent', 'payment_plan_offered',
            'notes', 'is_overdue', 'days_overdue', 'amount_paid',
            'payment_plan', 'payments', 'reminder_logs', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'reminder_count', 'last_reminder_sent', 'created_at', 'updated_at'
        ]

class DebtCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating debts"""
    
    class Meta:
        model = Debt
        fields = [
            'debtor_name', 'debtor_email', 'debtor_phone', 'amount',
            'description', 'due_date', 'notes'
        ]
    
    def create(self, validated_data):
        # Set original_amount to amount when creating
        validated_data['original_amount'] = validated_data['amount']
        return super().create(validated_data)
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value

class PaymentPlanCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payment plans"""
    
    class Meta:
        model = PaymentPlan
        fields = [
            'installment_amount', 'frequency', 'total_installments', 'start_date'
        ]
    
    def validate(self, data):
        debt = self.context.get('debt')
        if debt:
            total_plan_amount = data['installment_amount'] * data['total_installments']
            if total_plan_amount < debt.amount:
                raise serializers.ValidationError(
                    "Total payment plan amount must be at least equal to the debt amount"
                )
        return data

class PaymentRecordCreateSerializer(serializers.ModelSerializer):
    """Serializer for recording payments"""
    
    class Meta:
        model = PaymentRecord
        fields = [
            'amount', 'payment_method', 'reference_number', 'notes'
        ]
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Payment amount must be greater than 0")
        
        debt = self.context.get('debt')
        if debt and value > debt.amount:
            raise serializers.ValidationError("Payment amount cannot exceed remaining debt")
        
        return value

class ReminderTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReminderTemplate
        fields = [
            'id', 'name', 'tone', 'subject_template', 'body_template',
            'min_reminder_count', 'max_reminder_count', 'min_days_overdue',
            'max_days_overdue', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class SendReminderSerializer(serializers.Serializer):
    """Serializer for sending manual reminders"""
    template_id = serializers.UUIDField(required=False)
    custom_subject = serializers.CharField(max_length=200, required=False)
    custom_message = serializers.CharField(required=False)
    
    def validate(self, data):
        if not data.get('template_id') and not (data.get('custom_subject') and data.get('custom_message')):
            raise serializers.ValidationError(
                "Either provide a template_id or both custom_subject and custom_message"
            )
        return data

class DebtStatsSerializer(serializers.Serializer):
    """Serializer for debt statistics"""
    total_debts = serializers.IntegerField()
    total_amount_owed = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_amount_paid = serializers.DecimalField(max_digits=10, decimal_places=2)
    active_debts = serializers.IntegerField()
    overdue_debts = serializers.IntegerField()
    paid_debts = serializers.IntegerField()
    average_debt_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_reminders_sent = serializers.IntegerField()
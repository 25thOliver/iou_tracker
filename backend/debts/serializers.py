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
    is_owed_to_me = serializers.SerializerMethodField()

    class Meta:
        model = Debt
        fields = [
            'id', 'debtor_name', 'debtor_email', 'amount', 'original_amount',
            'currency', 'description', 'status', 'due_date', 'reminder_count',
            'payment_plan_offered', 'is_overdue', 'days_overdue',
            'amount_paid', 'is_owed_to_me', 'created_at'
        ]

    def get_is_owed_to_me(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.creditor == request.user
        return False

class DebtDetailSerializer(serializers.ModelSerializer):
    """Serializer for debt detail view - all fields and related data"""
    payment_plan = PaymentPlanSerializer(read_only=True)
    payments = PaymentRecordSerializer(many=True, read_only=True)
    reminder_logs = ReminderLogSerializer(many=True, read_only=True)
    is_overdue = serializers.ReadOnlyField()
    days_overdue = serializers.ReadOnlyField()
    amount_paid = serializers.ReadOnlyField()
    is_owed_to_me = serializers.SerializerMethodField()

    class Meta:
        model = Debt
        fields = [
            'id', 'debtor_name', 'debtor_email', 'debtor_phone', 'amount',
            'original_amount', 'currency', 'description', 'due_date', 'status',
            'reminder_count', 'last_reminder_sent', 'payment_plan_offered',
            'notes', 'is_overdue', 'days_overdue', 'amount_paid',
            'payment_plan', 'payments', 'reminder_logs', 'is_owed_to_me', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'reminder_count', 'last_reminder_sent', 'created_at', 'updated_at'
        ]

    def get_is_owed_to_me(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.creditor == request.user
        return False

from django.contrib.auth import get_user_model

User = get_user_model()

class DebtCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating debts, handling frontend 'debtor' and 'creditor' names"""
    # Expose the model's debtor_name field but make it not required for input, as it's set from 'debtor'
    debtor_name = serializers.CharField(required=False)
    debtor = serializers.CharField(write_only=True) # To capture the 'debtor' name from frontend
    # Rename 'creditor' to 'creditor_name' to avoid direct conflict with model's 'creditor' field (ForeignKey)
    creditor_name = serializers.CharField(write_only=True, required=False) # To capture the 'creditor' name from frontend

    class Meta:
        model = Debt
        fields = [
            'debtor_name', # Now explicitly managed in the serializer and can be optional
            'debtor',      # Write-only field for incoming debtor name
            'creditor_name', # Write-only field for incoming creditor name
            'amount', 'description', 'due_date', 'notes',
            'debtor_phone', 'debtor_email'
        ]
        extra_kwargs = {
            'debtor_email': {'required': False}, # Make explicit that email is not required from input
            'debtor_phone': {'required': False}, # Make explicit that phone is not required from input
            'creditor': {'required': False}, # Ensure the model's ForeignKey 'creditor' field is not required for input
        }

    def create(self, validated_data):
        # Pop the write_only fields first
        debtor_name_from_frontend = validated_data.pop('debtor')
        creditor_name_from_frontend = validated_data.pop('creditor_name', None)

        # Assign the derived debtor_name to the model's debtor_name field
        validated_data['debtor_name'] = debtor_name_from_frontend

        # Set original_amount to amount when creating
        validated_data['original_amount'] = validated_data['amount']

        # Handle creditor lookup and assignment
        if creditor_name_from_frontend:
            try:
                # Assuming 'username' is the field for the user's name
                creditor_user = User.objects.get(username=creditor_name_from_frontend)
                validated_data['creditor'] = creditor_user
            except User.DoesNotExist:
                # If creditor user not found, set creditor to None as per model's null=True
                validated_data['creditor'] = None
                # Optionally, you might want to log this or raise a more specific validation error
                # raise serializers.ValidationError({"creditor": f"Creditor user '{creditor_name_from_frontend}' not found."})
        else:
            # If no creditor name was provided, ensure the creditor field is set to None
            validated_data['creditor'] = None

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
    debt = serializers.PrimaryKeyRelatedField(queryset=Debt.objects.all())

    class Meta:
        model = PaymentRecord
        fields = [
            'debt', 'amount', 'payment_method', 'reference_number', 'notes'
        ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Payment amount must be greater than 0")

        # The debt is now directly available via self.initial_data.get('debt')
        # or self.validated_data['debt'] after is_valid()
        # So we can remove the context dependency here if it's no longer needed for validation
        # If debt is needed for validation logic here, it should be accessed as self.initial_data.get('debt')
        # or ensure it's passed in context if not directly in fields.
        # Given it's now in fields, it will be in validated_data.
        # We need to retrieve the Debt object here for comparison.
        debt_id = self.initial_data.get('debt')
        if debt_id:
            try:
                debt = Debt.objects.get(id=debt_id)
                if value > debt.amount:
                    raise serializers.ValidationError("Payment amount cannot exceed remaining debt")
            except Debt.DoesNotExist:
                # This case should ideally be caught by the PrimaryKeyRelatedField validation already
                pass

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

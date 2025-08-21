# debts/models.py
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid

class Debt(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('disputed', 'Disputed'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # The person who owes money
    debtor_name = models.CharField(max_length=200)
    debtor_email = models.EmailField(blank=True, null=True)
    debtor_phone = models.CharField(max_length=20, blank=True, null=True)

    # Debt details
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    original_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    currency = models.CharField(max_length=3, default='KES')
    description = models.TextField(help_text="What was the money for?")

    # Dates
    date_created = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(blank=True, null=True)
    date_paid = models.DateTimeField(blank=True, null=True)

    # Status and tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    last_reminder_sent = models.DateTimeField(blank=True, null=True)
    reminder_count = models.IntegerField(default=0)
    payment_plan_offered = models.BooleanField(default=False)

    # Optional: link to Django user (if you want user accounts)
    creditor = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    # Metadata
    notes = models.TextField(blank=True, help_text="Internal notes about this debt")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['debtor_email']),
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return f"{self.debtor_name} owes {self.currency}{self.amount} for {self.description[:50]}"

    @property
    def is_overdue(self):
        if self.due_date and self.status == 'active':
            from django.utils import timezone
            return timezone.now().date() > self.due_date
        return False

    @property
    def days_overdue(self):
        if self.is_overdue:
            from django.utils import timezone
            return (timezone.now().date() - self.due_date).days
        return 0

    @property
    def amount_paid(self):
        return self.original_amount - self.amount


class PaymentPlan(models.Model):
    FREQUENCY_CHOICES = [
        ('weekly', 'Weekly'),
        ('bi_weekly', 'Bi-weekly'),
        ('monthly', 'Monthly'),
        ('custom', 'Custom'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('defaulted', 'Defaulted'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    debt = models.OneToOneField(Debt, on_delete=models.CASCADE, related_name='payment_plan')

    # Plan details
    installment_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    total_installments = models.IntegerField(validators=[MinValueValidator(1)])
    paid_installments = models.IntegerField(default=0)

    # Dates
    start_date = models.DateField()
    next_due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment plan for {self.debt.debtor_name}: {self.debt.currency}{self.installment_amount} {self.frequency}"

    @property
    def completion_percentage(self):
        if self.total_installments > 0:
            return (self.paid_installments / self.total_installments) * 100
        return 0

    @property
    def remaining_amount(self):
        return self.installment_amount * (self.total_installments - self.paid_installments)


class PaymentRecord(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('check', 'Check'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    debt = models.ForeignKey(Debt, on_delete=models.CASCADE, related_name='payments')
    payment_plan = models.ForeignKey(
        PaymentPlan,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='payments'
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    date_paid = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date_paid']

    def __str__(self):
        return f"{self.debt.currency}{self.amount} payment from {self.debt.debtor_name} on {self.date_paid.date()}"


class ReminderTemplate(models.Model):
    TONE_CHOICES = [
        ('gentle', 'Gentle'),
        ('humorous', 'Humorous'),
        ('professional', 'Professional'),
        ('persistent', 'Persistent'),
        ('final_notice', 'Final Notice'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    tone = models.CharField(max_length=20, choices=TONE_CHOICES)
    subject_template = models.CharField(max_length=200)
    body_template = models.TextField()

    # Conditions for when to use this template
    min_reminder_count = models.IntegerField(default=0)
    max_reminder_count = models.IntegerField(blank=True, null=True)
    min_days_overdue = models.IntegerField(default=0)
    max_days_overdue = models.IntegerField(blank=True, null=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['tone', 'min_reminder_count']

    def __str__(self):
        return f"{self.name} ({self.tone})"


class ReminderLog(models.Model):
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('bounced', 'Bounced'),
        ('opened', 'Opened'),
        ('clicked', 'Clicked'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    debt = models.ForeignKey(Debt, on_delete=models.CASCADE, related_name='reminder_logs')
    template_used = models.ForeignKey(ReminderTemplate, on_delete=models.SET_NULL, null=True)

    subject = models.CharField(max_length=200)
    message_body = models.TextField()
    recipient_email = models.EmailField()

    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    error_message = models.TextField(blank=True)

    # Email tracking (optional)
    opened_at = models.DateTimeField(blank=True, null=True)
    clicked_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"Reminder to {self.recipient_email} on {self.sent_at.date()}"

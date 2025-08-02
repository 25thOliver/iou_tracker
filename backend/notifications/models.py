# Create new app: python manage.py startapp notifications
# iou-tracker/notifications/models.py

from django.db import models
from django.contrib.auth.models import User
from debts.models import Debt, PaymentRecord

class NotificationPreference(models.Model):
    """User preferences for notifications"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    
    # Notification type preferences
    debt_reminders_email = models.BooleanField(default=True)
    debt_reminders_sms = models.BooleanField(default=False)
    payment_confirmations_email = models.BooleanField(default=True)
    payment_confirmations_sms = models.BooleanField(default=False)
    debt_created_email = models.BooleanField(default=True)
    debt_created_sms = models.BooleanField(default=False)
    
    # Timing preferences
    reminder_frequency_days = models.PositiveIntegerField(default=7)  # Weekly reminders
    quiet_hours_start = models.TimeField(default='22:00:00')  # 10 PM
    quiet_hours_end = models.TimeField(default='08:00:00')    # 8 AM
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Notification preferences for {self.user.username}"

class NotificationTemplate(models.Model):
    """Templates for different types of notifications"""
    NOTIFICATION_TYPES = [
        ('debt_reminder', 'Debt Reminder'),
        ('payment_confirmation', 'Payment Confirmation'),
        ('debt_created', 'Debt Created'),
        ('payment_received', 'Payment Received'),
        ('debt_settled', 'Debt Settled'),
    ]
    
    CHANNEL_TYPES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
    ]
    
    name = models.CharField(max_length=100)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    channel = models.CharField(max_length=10, choices=CHANNEL_TYPES)
    subject_template = models.CharField(max_length=200, help_text="For emails only")
    body_template = models.TextField()
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['notification_type', 'channel']
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.get_channel_display()}"

class NotificationLog(models.Model):
    """Log of all notifications sent"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('delivered', 'Delivered'),
        ('bounced', 'Bounced'),
        ('clicked', 'Clicked'),
    ]
    
    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    debt = models.ForeignKey(Debt, on_delete=models.CASCADE, null=True, blank=True)
    payment_record = models.ForeignKey(PaymentRecord, on_delete=models.CASCADE, null=True, blank=True)
    
    notification_type = models.CharField(max_length=50)
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES)
    recipient = models.CharField(max_length=200)  # Email or phone number
    subject = models.CharField(max_length=200, blank=True)
    message_body = models.TextField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    external_id = models.CharField(max_length=100, blank=True, null=True)  # Twilio/SendGrid message ID
    error_message = models.TextField(blank=True, null=True)
    
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} to {self.recipient} - {self.status}"

class ScheduledNotification(models.Model):
    """Scheduled notifications to be sent later"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    debt = models.ForeignKey(Debt, on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=50)
    channel = models.CharField(max_length=10, choices=[('email', 'Email'), ('sms', 'SMS')])
    
    scheduled_for = models.DateTimeField()
    is_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['scheduled_for']
    
    def __str__(self):
        return f"Scheduled {self.notification_type} for {self.user.username} at {self.scheduled_for}"
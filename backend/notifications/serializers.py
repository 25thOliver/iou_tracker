# iou-tracker/notifications/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import NotificationPreference, NotificationLog, NotificationTemplate

class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            'email_enabled', 'sms_enabled', 'phone_number',
            'debt_reminders_email', 'debt_reminders_sms',
            'payment_confirmations_email', 'payment_confirmations_sms',
            'debt_created_email', 'debt_created_sms',
            'reminder_frequency_days', 'quiet_hours_start', 'quiet_hours_end'
        ]
    
    def validate_phone_number(self, value):
        """Validate phone number format"""
        if value and not value.startswith('+'):
            raise serializers.ValidationError("Phone number must start with country code (e.g., +1)")
        return value

class NotificationLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    debt_description = serializers.CharField(source='debt.description', read_only=True)
    # Frontend-friendly fields
    title = serializers.CharField(source='subject', read_only=True)
    message = serializers.CharField(source='message_body', read_only=True)
    read = serializers.SerializerMethodField()

    class Meta:
        model = NotificationLog
        fields = [
            'id', 'user', 'notification_type', 'channel', 'recipient',
            'subject', 'title', 'message', 'status', 'read',
            'sent_at', 'delivered_at', 'created_at',
            'debt_description', 'error_message'
        ]
        read_only_fields = ['id', 'created_at', 'sent_at', 'delivered_at']

    def get_read(self, obj):
        return obj.status in ('read', 'delivered', 'clicked')

class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'name', 'notification_type', 'channel',
            'subject_template', 'body_template', 'is_active'
        ]

class SendNotificationSerializer(serializers.Serializer):
    """Serializer for manually sending notifications"""
    notification_type = serializers.ChoiceField(choices=[
        'debt_reminder', 'payment_confirmation', 'debt_created'
    ])
    debt_id = serializers.IntegerField(required=False)
    payment_record_id = serializers.IntegerField(required=False)
    custom_message = serializers.CharField(required=False, max_length=500)

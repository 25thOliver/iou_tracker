# iou-tracker/notifications/services.py

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.models import User
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from .models import NotificationLog, NotificationTemplate, NotificationPreference
from debts.models import Debt, PaymentRecord

logger = logging.getLogger('notifications')

class NotificationService:
    """Base notification service class"""
    
    def __init__(self):
        self.email_enabled = getattr(settings, 'NOTIFICATION_SETTINGS', {}).get('EMAIL_ENABLED', True)
        self.sms_enabled = getattr(settings, 'NOTIFICATION_SETTINGS', {}).get('SMS_ENABLED', True)
    
    def send_notification(self, user: User, notification_type: str, context: Dict[str, Any], 
                         debt: Optional[Debt] = None, payment_record: Optional[PaymentRecord] = None):
        """Send notification via preferred channels"""
        try:
            # Get user preferences
            preferences = self._get_user_preferences(user)
            
            results = []
            
            # Send email if enabled
            if self._should_send_email(preferences, notification_type):
                email_result = self._send_email(user, notification_type, context, debt, payment_record)
                results.append(email_result)
            
            # Send SMS if enabled
            if self._should_send_sms(preferences, notification_type):
                sms_result = self._send_sms(user, notification_type, context, debt, payment_record)
                results.append(sms_result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error sending notification to {user.username}: {str(e)}")
            return []
    
    def _get_user_preferences(self, user: User) -> NotificationPreference:
        """Get or create user notification preferences"""
        preferences, created = NotificationPreference.objects.get_or_create(
            user=user,
            defaults={
                'email_enabled': True,
                'sms_enabled': False,
            }
        )
        return preferences
    
    def _should_send_email(self, preferences: NotificationPreference, notification_type: str) -> bool:
        """Check if email should be sent for this notification type"""
        if not self.email_enabled or not preferences.email_enabled:
            return False
        
        type_mapping = {
            'debt_reminder': preferences.debt_reminders_email,
            'payment_confirmation': preferences.payment_confirmations_email,
            'debt_created': preferences.debt_created_email,
        }
        
        return type_mapping.get(notification_type, True)
    
    def _should_send_sms(self, preferences: NotificationPreference, notification_type: str) -> bool:
        """Check if SMS should be sent for this notification type"""
        if not self.sms_enabled or not preferences.sms_enabled or not preferences.phone_number:
            return False
        
        type_mapping = {
            'debt_reminder': preferences.debt_reminders_sms,
            'payment_confirmation': preferences.payment_confirmations_sms,
            'debt_created': preferences.debt_created_sms,
        }
        
        return type_mapping.get(notification_type, False)

class EmailService(NotificationService):
    """Email notification service using SendGrid"""
    
    def _send_email(self, user: User, notification_type: str, context: Dict[str, Any], 
                   debt: Optional[Debt] = None, payment_record: Optional[PaymentRecord] = None) -> Dict[str, Any]:
        """Send email notification"""
        try:
            # Get email template
            template = self._get_template(notification_type, 'email')
            if not template:
                logger.warning(f"No email template found for {notification_type}")
                return {'success': False, 'error': 'Template not found'}
            
            # Render subject and body
            subject = self._render_template(template.subject_template, context)
            body = self._render_template(template.body_template, context)
            
            # Create notification log entry
            log_entry = NotificationLog.objects.create(
                user=user,
                debt=debt,
                payment_record=payment_record,
                notification_type=notification_type,
                channel='email',
                recipient=user.email,
                subject=subject,
                message_body=body,
                status='pending'
            )
            
            # Send email
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=body,
                fail_silently=False
            )
            
            # Update log entry
            log_entry.status = 'sent'
            log_entry.sent_at = datetime.now(timezone.utc)
            log_entry.save()
            
            logger.info(f"Email sent successfully to {user.email} for {notification_type}")
            return {'success': True, 'log_id': log_entry.id}
            
        except Exception as e:
            logger.error(f"Failed to send email to {user.email}: {str(e)}")
            if 'log_entry' in locals():
                log_entry.status = 'failed'
                log_entry.error_message = str(e)
                log_entry.save()
            return {'success': False, 'error': str(e)}

class SMSService(NotificationService):
    """SMS notification service using Twilio"""
    
    def __init__(self):
        super().__init__()
        self.twilio_client = None
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    def _send_sms(self, user: User, notification_type: str, context: Dict[str, Any], 
                 debt: Optional[Debt] = None, payment_record: Optional[PaymentRecord] = None) -> Dict[str, Any]:
        """Send SMS notification"""
        try:
            if not self.twilio_client:
                return {'success': False, 'error': 'Twilio not configured'}
            
            # Get user phone number
            preferences = self._get_user_preferences(user)
            if not preferences.phone_number:
                return {'success': False, 'error': 'No phone number on file'}
            
            # Get SMS template
            template = self._get_template(notification_type, 'sms')
            if not template:
                logger.warning(f"No SMS template found for {notification_type}")
                return {'success': False, 'error': 'Template not found'}
            
            # Render message body
            body = self._render_template(template.body_template, context)
            
            # Create notification log entry
            log_entry = NotificationLog.objects.create(
                user=user,
                debt=debt,
                payment_record=payment_record,
                notification_type=notification_type,
                channel='sms',
                recipient=preferences.phone_number,
                message_body=body,
                status='pending'
            )
            
            # Send SMS
            message = self.twilio_client.messages.create(
                body=body,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=preferences.phone_number
            )
            
            # Update log entry
            log_entry.status = 'sent'
            log_entry.external_id = message.sid
            log_entry.sent_at = datetime.now(timezone.utc)
            log_entry.save()
            
            logger.info(f"SMS sent successfully to {preferences.phone_number} for {notification_type}")
            return {'success': True, 'log_id': log_entry.id, 'message_sid': message.sid}
            
        except TwilioException as e:
            logger.error(f"Twilio error sending SMS to {user.username}: {str(e)}")
            if 'log_entry' in locals():
                log_entry.status = 'failed'
                log_entry.error_message = str(e)
                log_entry.save()
            return {'success': False, 'error': str(e)}
        except Exception as e:
            logger.error(f"Failed to send SMS to {user.username}: {str(e)}")
            if 'log_entry' in locals():
                log_entry.status = 'failed'
                log_entry.error_message = str(e)
                log_entry.save()
            return {'success': False, 'error': str(e)}
    
    def _get_template(self, notification_type: str, channel: str) -> Optional[NotificationTemplate]:
        """Get notification template"""
        try:
            return NotificationTemplate.objects.get(
                notification_type=notification_type,
                channel=channel,
                is_active=True
            )
        except NotificationTemplate.DoesNotExist:
            return None
    
    def _render_template(self, template_string: str, context: Dict[str, Any]) -> str:
        """Render template with context"""
        try:
            # Simple template rendering - you might want to use Django's template engine
            return template_string.format(**context)
        except KeyError as e:
            logger.warning(f"Missing template variable: {e}")
            return template_string

# Combined service class
class NotificationManager(EmailService, SMSService):
    """Combined notification manager for both email and SMS"""
    
    def send_debt_reminder(self, debt: Debt):
        """Send debt reminder notification"""
        context = {
            'user_name': debt.debtor.get_full_name() or debt.debtor.username,
            'creditor_name': debt.creditor.get_full_name() or debt.creditor.username,
            'amount': debt.amount,
            'description': debt.description,
            'due_date': debt.due_date.strftime('%B %d, %Y') if debt.due_date else 'No due date',
            'debt_id': debt.id,
        }
        
        return self.send_notification(
            user=debt.debtor,
            notification_type='debt_reminder',
            context=context,
            debt=debt
        )
    
    def send_payment_confirmation(self, payment_record: PaymentRecord):
        """Send payment confirmation notification"""
        context = {
            'user_name': payment_record.debt.creditor.get_full_name() or payment_record.debt.creditor.username,
            'debtor_name': payment_record.debt.debtor.get_full_name() or payment_record.debt.debtor.username,
            'amount': payment_record.amount,
            'remaining_amount': payment_record.debt.remaining_amount,
            'payment_date': payment_record.created_at.strftime('%B %d, %Y'),
            'debt_description': payment_record.debt.description,
        }
        
        return self.send_notification(
            user=payment_record.debt.creditor,
            notification_type='payment_confirmation',
            context=context,
            debt=payment_record.debt,
            payment_record=payment_record
        )
    
    def send_debt_created_notification(self, debt: Debt):
        """Send debt created notification to debtor"""
        context = {
            'user_name': debt.debtor.get_full_name() or debt.debtor.username,
            'creditor_name': debt.creditor.get_full_name() or debt.creditor.username,
            'amount': debt.amount,
            'description': debt.description,
            'due_date': debt.due_date.strftime('%B %d, %Y') if debt.due_date else 'No due date',
            'created_date': debt.created_at.strftime('%B %d, %Y'),
        }
        
        return self.send_notification(
            user=debt.debtor,
            notification_type='debt_created',
            context=context,
            debt=debt
        )
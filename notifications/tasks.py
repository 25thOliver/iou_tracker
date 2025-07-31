# iou-tracker/notifications/tasks.py

from celery import shared_task
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.utils import timezone
from notifications.services import NotificationManager
from .models import ScheduledNotification, NotificationLog
from debts.models import Debt, PaymentRecord
import logging

logger = logging.getLogger('notifications')

@shared_task(bind=True, max_retries=3)
def send_notification_task(self, user_id, notification_type, context, debt_id=None, payment_record_id=None):
    """Background task to send notifications"""
    try:
        user = User.objects.get(id=user_id)
        debt = Debt.objects.get(id=debt_id) if debt_id else None
        payment_record = PaymentRecord.objects.get(id=payment_record_id) if payment_record_id else None

        notification_manager = NotificationManager()
        results = notification_manager.send_notification(
            user=user,
            notification_type=notification_type,
            context=context,
            debt=debt,
            payment_record=payment_record
        )

        logger.info(f"Notification task completed for user {user.username}: {results}")
        return results

    except Exception as e:
        logger.error(f"Notification task failed: {str(e)}")
        # Retry the task
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        raise

@shared_task
def send_debt_reminder_task(debt_id):
    """Background task to send debt reminder"""
    try:
        debt = Debt.objects.get(id=debt_id)
        notification_manager = NotificationManager()
        results = notification_manager.send_debt_reminder(debt)

        logger.info(f"Debt reminder sent for debt {debt_id}: {results}")
        return results

    except Debt.DoesNotExist:
        logger.error(f"Debt {debt_id} not found for reminder")
        return {'error': 'Debt not found'}
    except Exception as e:
        logger.error(f"Failed to send debt reminder for debt {debt_id}: {str(e)}")
        raise

@shared_task
def send_payment_confirmation_task(payment_record_id):
    """Background task to send payment confirmation"""
    try:
        payment_record = PaymentRecord.objects.get(id=payment_record_id)
        notification_manager = NotificationManager()
        results = notification_manager.send_payment_confirmation(payment_record)

        logger.info(f"Payment confirmation sent for payment {payment_record_id}: {results}")
        return results

    except PaymentRecord.DoesNotExist:
        logger.error(f"Payment record {payment_record_id} not found")
        return {'error': 'Payment record not found'}
    except Exception as e:
        logger.error(f"Failed to send payment confirmation for payment {payment_record_id}: {str(e)}")
        raise

@shared_task
def send_debt_created_notification_task(debt_id):
    """Background task to send debt created notification"""
    try:
        debt = Debt.objects.get(id=debt_id)
        notification_manager = NotificationManager()
        results = notification_manager.send_debt_created_notification(debt)

        logger.info(f"Debt created notification sent for debt {debt_id}: {results}")
        return results

    except Debt.DoesNotExist:
        logger.error(f"Debt {debt_id} not found for creation notification")
        return {'error': 'Debt not found'}
    except Exception as e:
        logger.error(f"Failed to send debt created notification for debt {debt_id}: {str(e)}")
        raise

@shared_task
def process_scheduled_notifications():
    """Process and send scheduled notifications"""
    try:
        now = timezone.now()
        scheduled_notifications = ScheduledNotification.objects.filter(
            scheduled_for__lte=now,
            is_sent=False
        )

        processed_count = 0
        for scheduled_notification in scheduled_notifications:
            try:
                # Send the notification based on type
                if scheduled_notification.notification_type == 'debt_reminder':
                    send_debt_reminder_task.delay(scheduled_notification.debt.id)

                # Mark as sent
                scheduled_notification.is_sent = True
                scheduled_notification.save()
                processed_count += 1

            except Exception as e:
                logger.error(f"Failed to process scheduled notification {scheduled_notification.id}: {str(e)}")

        logger.info(f"Processed {processed_count} scheduled notifications")
        return processed_count

    except Exception as e:
        logger.error(f"Failed to process scheduled notifications: {str(e)}")
        raise

@shared_task
def send_daily_debt_reminders():
    """Send daily debt reminders for overdue debts"""
    try:
        today = timezone.now().date()

        # Find overdue debts that haven't been reminded recently
        overdue_debts = Debt.objects.filter(
            due_date__lt=today,
            status='active'
        )

        sent_count = 0
        for debt in overdue_debts:
            # Check if reminder was sent recently
            recent_reminder = NotificationLog.objects.filter(
                debt=debt,
                notification_type='debt_reminder',
                status='sent',
                sent_at__gte=timezone.now() - timedelta(days=1)
            ).exists()

            if not recent_reminder:
                send_debt_reminder_task.delay(debt.id)
                sent_count += 1

        logger.info(f"Queued {sent_count} daily debt reminders")
        return sent_count

    except Exception as e:
        logger.error(f"Failed to send daily debt reminders: {str(e)}")
        raise

@shared_task
def cleanup_old_notification_logs():
    """Clean up old notification logs (older than 90 days)"""
    try:
        cutoff_date = timezone.now() - timedelta(days=90)
        deleted_count = NotificationLog.objects.filter(
            created_at__lt=cutoff_date
        ).delete()[0]

        logger.info(f"Cleaned up {deleted_count} old notification logs")
        return deleted_count

    except Exception as e:
        logger.error(f"Failed to cleanup notification logs: {str(e)}")
        raise

@shared_task
def update_notification_status():
    """Update notification statuses by checking with external services"""
    try:
        # This would typically check with Twilio/SendGrid for delivery status
        # For now, we'll just mark old pending notifications as failed
        cutoff_time = timezone.now() - timedelta(hours=1)

        updated_count = NotificationLog.objects.filter(
            status='pending',
            created_at__lt=cutoff_time
        ).update(
            status='failed',
            error_message='Notification timed out'
        )

        logger.info(f"Updated {updated_count} timed-out notifications")
        return updated_count

    except Exception as e:
        logger.error(f"Failed to update notification statuses: {str(e)}")
        raise

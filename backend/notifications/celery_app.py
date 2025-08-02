# iou-tracker/notifications/celery_app.py

from celery import Celery
import os

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iou_tracker_backend.settings')

app = Celery('iou_tracker_notifications')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Schedule periodic tasks
from celery.schedules import crontab

app.conf.beat_schedule = {
    'process-scheduled-notifications': {
        'task': 'notifications.tasks.process_scheduled_notifications',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'send-daily-debt-reminders': {
        'task': 'notifications.tasks.send_daily_debt_reminders',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9 AM
    },
    'cleanup-old-notification-logs': {
        'task': 'notifications.tasks.cleanup_old_notification_logs',
        'schedule': crontab(hour=2, minute=0, day_of_week=1),  # Weekly on Monday at 2 AM
    },
    'update-notification-status': {
        'task': 'notifications.tasks.update_notification_status',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
}

app.conf.timezone = 'UTC'
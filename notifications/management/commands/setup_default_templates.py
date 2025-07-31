# iou-tracker/notifications/management/commands/setup_default_templates.py

from django.core.management.base import BaseCommand
from notifications.models import NotificationTemplate
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Setup default notification templates'

    def handle(self, *args, **options):
        templates_to_create = [
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
                'subject_template': '', # SMS usually doesn't have a separate subject field
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
            },
            # You can add more templates here for 'payment_received' and 'debt_settled'
            # as defined in notifications/models.py if needed.
            # Example for Payment Received Email:
            # {
            #     'name': 'Payment Received Email',
            #     'notification_type': 'payment_received',
            #     'channel': 'email',
            #     'subject_template': 'You Received a Payment!',
            #     'body_template': '''Hi {user_name},
            #
            # {debtor_name} has made a payment of ${amount} for the debt: "{description}".
            #
            # Best regards,
            # IOU Tracker Team'''
            # },
            # Example for Debt Settled Email:
            # {
            #     'name': 'Debt Settled Email',
            #     'notification_type': 'debt_settled',
            #     'channel': 'email',
            #     'subject_template': 'Debt Settled: {description}',
            #     'body_template': '''Hi {user_name},
            #
            # The debt "{description}" with {other_party_name} has been settled.
            #
            # Best regards,
            # IOU Tracker Team'''
            # },
        ]

        created_count = 0
        for template_data in templates_to_create:
            template, created = NotificationTemplate.objects.get_or_create(
                notification_type=template_data['notification_type'],
                channel=template_data['channel'],
                defaults={
                    'name': template_data['name'],
                    'subject_template': template_data['subject_template'],
                    'body_template': template_data['body_template'],
                    'is_active': True
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created notification template: {template.name} ({template.channel})'))
            else:
                self.stdout.write(self.style.WARNING(f'Notification template already exists: {template.name} ({template.channel}) - Skipping'))
                # Optionally, update existing templates if needed
                # template.name = template_data['name']
                # template.subject_template = template_data['subject_template']
                # template.body_template = template_data['body_template']
                # template.save()
                # self.stdout.write(self.style.SUCCESS(f'Updated notification template: {template.name} ({template.channel})'))

        if created_count > 0:
            self.stdout.write(self.style.SUCCESS(f'\nSuccessfully created {created_count} new notification templates.'))
        else:
            self.stdout.write(self.style.WARNING('\nNo new notification templates were created (they might already exist).'))

# iou-tracker/notifications/views.py

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import NotificationPreference, NotificationLog, NotificationTemplate
from .serializers import (
    NotificationPreferenceSerializer, NotificationLogSerializer,
    NotificationTemplateSerializer, SendNotificationSerializer
)
from .tasks import send_notification_task, send_debt_reminder_task
from debts.models import Debt, PaymentRecord
import logging

User = get_user_model()

logger = logging.getLogger('notifications')

class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    """Get and update user notification preferences"""
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        preference, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return preference

class NotificationLogListView(generics.ListAPIView):
    """List user's notification history"""
    serializer_class = NotificationLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return NotificationLog.objects.filter(
            user=self.request.user
        ).order_by('-created_at')

class NotificationListCreateView(generics.ListCreateAPIView):
    queryset = NotificationLog.objects.all()
    serializer_class = NotificationLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only show notifications for the authenticated user
        return NotificationLog.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        # Assign the current user as the recipient of the notification
        serializer.save(user=self.request.user)

class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = NotificationLog.objects.all()
    serializer_class = NotificationLogSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id' # Use 'id' as the lookup field

    def get_queryset(self):
        # Ensure users can only access their own notifications
        return NotificationLog.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        # Special handling for marking as read
        if 'read' in self.request.data and self.request.data['read'] is True:
            instance = serializer.save(status='read') # Assuming 'read' is a valid status
            # You might want to update a 'read_at' timestamp here too
            # instance.read_at = timezone.now()
            # instance.save()
        else:
            serializer.save()

class NotificationTemplateListView(generics.ListAPIView):
    """List available notification templates (admin only)"""
    serializer_class = NotificationTemplateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return NotificationTemplate.objects.all()
        return NotificationTemplate.objects.filter(is_active=True)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_manual_notification(request):
    """Manually send a notification"""
    serializer = SendNotificationSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        notification_type = data['notification_type']

        try:
            # Validate debt ownership for debt-related notifications
            debt = None
            payment_record = None

            if data.get('debt_id'):
                debt = Debt.objects.get(
                    Q(creditor=request.user) | Q(debtor=request.user),
                    id=data['debt_id']
                )

            if data.get('payment_record_id'):
                payment_record = PaymentRecord.objects.get(
                    id=data['payment_record_id'],
                    debt__creditor=request.user
                )

            # Send notification based on type
            if notification_type == 'debt_reminder' and debt:
                task = send_debt_reminder_task.delay(debt.id)
                return Response({
                    'message': 'Debt reminder sent successfully',
                    'task_id': task.id
                })

            # For other notification types, you can add similar logic
            return Response({
                'message': f'{notification_type} notification queued successfully'
            })

        except Debt.DoesNotExist:
            return Response({
                'error': 'Debt not found or access denied'
            }, status=status.HTTP_404_NOT_FOUND)
        except PaymentRecord.DoesNotExist:
            return Response({
                'error': 'Payment record not found or access denied'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error sending manual notification: {str(e)}")
            return Response({
                'error': 'Failed to send notification'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_notification(request):
    """Test notification system with sample data"""
    try:
        from .services import NotificationManager

        notification_manager = NotificationManager()

        # Test context
        context = {
            'user_name': request.user.get_full_name() or request.user.username,
            'creditor_name': 'Test Creditor',
            'amount': '50.00',
            'description': 'Test debt for notification system',
            'due_date': 'December 31, 2025',
            'debt_id': 'TEST_ID',
        }

        results = notification_manager.send_notification(
            user=request.user,
            notification_type='debt_reminder',
            context=context
        )

        return Response({
            'message': 'Test notification sent',
            'results': results
        })

    except Exception as e:
        logger.error(f"Error sending test notification: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_stats(request):
    """Get notification statistics for the user"""
    try:
        user_logs = NotificationLog.objects.filter(user=request.user)

        stats = {
            'total_notifications': user_logs.count(),
            'sent_notifications': user_logs.filter(status='sent').count(),
            'failed_notifications': user_logs.filter(status='failed').count(),
            'email_notifications': user_logs.filter(channel='email').count(),
            'sms_notifications': user_logs.filter(channel='sms').count(),
            'recent_notifications': user_logs.filter(
                created_at__gte=request.user.date_joined
            ).count() if request.user.date_joined else 0
        }

        # Notification types breakdown
        notification_types = user_logs.values('notification_type').distinct()
        type_stats = {}
        for nt in notification_types:
            nt_type = nt['notification_type']
            type_stats[nt_type] = user_logs.filter(notification_type=nt_type).count()

        stats['by_type'] = type_stats

        return Response(stats)

    except Exception as e:
        logger.error(f"Error getting notification stats: {str(e)}")
        return Response({
            'error': 'Failed to get notification statistics'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

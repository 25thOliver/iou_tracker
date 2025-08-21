from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import IOU
from .serializers import IOUSerializer
from notifications.models import NotificationLog

class IOUListCreateView(generics.ListCreateAPIView):
    serializer_class = IOUSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return IOUs created by the current user"""
        return IOU.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        """Set the created_by field to the current user and log notification"""
        iou = serializer.save(created_by=self.request.user)
        try:
            NotificationLog.objects.create(
                user=self.request.user,
                notification_type='iou_created',
                channel='email',
                recipient=self.request.user.email or (self.request.user.username or ''),
                status='sent',
                subject=f"New IOU Created: {iou.amount} {iou.currency}",
                message_body=f"You created an IOU: {iou.debtor} owes {iou.creditor} {iou.amount} {iou.currency} for '{iou.description or ''}'.",
            )
        except Exception:
            pass

class IOUDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = IOUSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        """Return IOUs created by the current user"""
        return IOU.objects.filter(created_by=self.request.user)

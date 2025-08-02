# iou-tracker/notifications/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.NotificationListCreateView.as_view(), name='notification-list-create'),
    path('<uuid:id>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    path('preferences/', views.NotificationPreferenceView.as_view(), name='notification_preferences'),
    path('history/', views.NotificationLogListView.as_view(), name='notification_history'),
    path('templates/', views.NotificationTemplateListView.as_view(), name='notification_templates'),
    path('send/', views.send_manual_notification, name='send_manual_notification'),
    path('test/', views.test_notification, name='test_notification'),
    path('stats/', views.notification_stats, name='notification_stats'),
]

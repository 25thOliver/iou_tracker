# iou_tracker_backend/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from rest_framework.decorators import api_view
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework.response import Response

@api_view(['GET'])
def api_root(request):
    """API root endpoint with available endpoints"""
    return Response({
        'message': 'Welcome to IOU Tracker API',
        'version': '1.0',
        'endpoints': {
            'debts': '/api/debts/',
            'debt_detail': '/api/debts/{id}/',
            'create_payment': '/api/debts/{id}/payments/create/',
            'create_payment_plan': '/api/debts/{id}/payment-plan/',
            'send_reminder': '/api/debts/{id}/send-reminder/',
            'reminder_templates': '/api/debts/reminder-templates/',
            'debt_statistics': '/api/debts/stats/',
            'overdue_debts': '/api/debts/overdue/',
            'admin': '/admin/',
        },
        'documentation': {
            'filtering': 'Use ?status=active, ?overdue=true, ?has_payment_plan=true',
            'search': 'Use ?search=debtor_name_or_email',
            'ordering': 'Use ?ordering=-created_at or ?ordering=amount',
            'pagination': 'Use ?page=2&page_size=10'
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root, name='api-root'),
    path('api/debts/', include('debts.urls')),
]

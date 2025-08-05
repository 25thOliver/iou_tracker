# debts/urls.py
from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'debts'

urlpatterns = [
    # Debt management endpoints
    path('', views.DebtListCreateView.as_view(), name='debt-list-create'),
    path('<uuid:id>/', views.DebtDetailView.as_view(), name='debt-detail'),
    path('<uuid:debt_id>/send-reminder/', views.send_reminder, name='send-reminder'),
    path('<uuid:debt_id>/mark-paid/', views.mark_debt_paid, name='mark-debt-paid'),

    # Payment plan endpoints (related to a specific debt)
    path('<uuid:debt_id>/payment-plan/', views.PaymentPlanCreateView.as_view(), name='create-payment-plan'),
    # Generic payment plan list/detail views (if needed, not tied to a specific debt)
    path('payment-plans/', views.PaymentPlanListView.as_view(), name='payment-plan-list'),
    path('payment-plans/<uuid:id>/', views.PaymentPlanDetailView.as_view(), name='payment-plan-detail'),

    # Payment record endpoints (related to a specific debt)
    path('<uuid:debt_id>/payments/create/', views.PaymentRecordCreateView.as_view(), name='create-payment'),
    # Generic payment record list view
    path('payments/', views.PaymentRecordListView.as_view(), name='payment-list'),

    # Reminder template endpoints
    path('reminder-templates/', views.ReminderTemplateListCreateView.as_view(), name='reminder-template-list-create'),
    path('reminder-templates/<uuid:id>/', views.ReminderTemplateDetailView.as_view(), name='reminder-template-detail'),

    # Statistics and reporting endpoints
    path('stats/', views.debt_statistics, name='debt-stats'),
    path('overdue/', views.overdue_debts, name='overdue-debts'),
]

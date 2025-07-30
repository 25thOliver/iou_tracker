# debts/urls.py
from django.urls import path
from . import views

app_name = 'debts'

urlpatterns = [
    # Debt management endpoints
    path('', views.DebtListCreateView.as_view(), name='debt-list-create'),
    path('<uuid:id>/', views.DebtDetailView.as_view(), name='debt-detail'),
    path('<uuid:debt_id>/mark-paid/', views.mark_debt_paid, name='mark-debt-paid'),
    
    # Payment endpoints
    path('<uuid:debt_id>/payments/', views.PaymentRecordListView.as_view(), name='payment-list'),
    path('<uuid:debt_id>/payments/create/', views.PaymentRecordCreateView.as_view(), name='payment-create'),
    
    # Payment plan endpoints
    path('<uuid:debt_id>/payment-plan/', views.PaymentPlanCreateView.as_view(), name='payment-plan-create'),
    path('payment-plans/<uuid:id>/', views.PaymentPlanDetailView.as_view(), name='payment-plan-detail'),
    
    # Reminder endpoints
    path('<uuid:debt_id>/send-reminder/', views.send_reminder, name='send-reminder'),
    path('reminder-templates/', views.ReminderTemplateListCreateView.as_view(), name='reminder-template-list'),
    path('reminder-templates/<uuid:id>/', views.ReminderTemplateDetailView.as_view(), name='reminder-template-detail'),
    
    # Analytics and utility endpoints
    path('stats/', views.debt_statistics, name='debt-statistics'),
    path('overdue/', views.overdue_debts, name='overdue-debts'),
]
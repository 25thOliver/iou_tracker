# debts/urls.py - Simplified version
from django.urls import path
from . import views, auth_views

app_name = 'debts'

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', auth_views.UserRegistrationView.as_view(), name='register'),
    path('auth/login/', auth_views.UserLoginView.as_view(), name='login'),
    path('auth/logout/', auth_views.logout_view, name='logout'),
    path('auth/dashboard/', auth_views.user_dashboard, name='user_dashboard'),
    path('auth/health/', auth_views.auth_health_check, name='auth_health'),

    # Debt management endpoints
    path('debts/', views.DebtListCreateView.as_view(), name='debt-list-create'),
    path('debts/<uuid:id>/', views.DebtDetailView.as_view(), name='debt-detail'),
    path('debts/<uuid:debt_id>/reminder/', views.send_reminder, name='send-reminder'),
    path('debts/<uuid:debt_id>/mark-paid/', views.mark_debt_paid, name='mark-debt-paid'),
    
    # Payment plan endpoints
    path('payment-plans/', views.PaymentPlanListView.as_view(), name='payment-plan-list'),
    path('payment-plans/create/', views.PaymentPlanCreateView.as_view(), name='payment-plan-create'),
    path('payment-plans/<uuid:id>/', views.PaymentPlanDetailView.as_view(), name='payment-plan-detail'),
    
    # Payment record endpoints
    path('payments/', views.PaymentRecordListView.as_view(), name='payment-list'),
    path('payments/create/', views.PaymentRecordCreateView.as_view(), name='payment-create'),
    
    # Reminder template endpoints
    path('reminder-templates/', views.ReminderTemplateListCreateView.as_view(), name='reminder-template-list-create'),
    path('reminder-templates/<uuid:id>/', views.ReminderTemplateDetailView.as_view(), name='reminder-template-detail'),
    
    # Statistics and reporting endpoints
    path('stats/', views.debt_statistics, name='debt-stats'),
    path('overdue/', views.overdue_debts, name='overdue-debts'),
]
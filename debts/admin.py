# debts/admin.py
from django.contrib import admin
from .models import Debt, PaymentPlan, PaymentRecord, ReminderTemplate, ReminderLog

@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ['debtor_name', 'amount', 'status', 'due_date', 'reminder_count', 'created_at']
    list_filter = ['status', 'payment_plan_offered', 'created_at']
    search_fields = ['debtor_name', 'debtor_email', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'reminder_count']
    
    fieldsets = (
        ('Debtor Information', {
            'fields': ('debtor_name', 'debtor_email', 'debtor_phone')
        }),
        ('Debt Details', {
            'fields': ('amount', 'original_amount', 'description', 'due_date')
        }),
        ('Status & Tracking', {
            'fields': ('status', 'payment_plan_offered', 'reminder_count', 'last_reminder_sent')
        }),
        ('Metadata', {
            'fields': ('id', 'notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    list_display = ['debt', 'installment_amount', 'frequency', 'paid_installments', 'total_installments', 'status']
    list_filter = ['frequency', 'status']

@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ['debt', 'amount', 'payment_method', 'date_paid', 'verified']
    list_filter = ['payment_method', 'verified', 'date_paid']

@admin.register(ReminderTemplate)
class ReminderTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'tone', 'min_reminder_count', 'max_reminder_count', 'is_active']
    list_filter = ['tone', 'is_active']

@admin.register(ReminderLog)
class ReminderLogAdmin(admin.ModelAdmin):
    list_display = ['debt', 'recipient_email', 'status', 'sent_at']
    list_filter = ['status', 'sent_at']
    readonly_fields = ['sent_at']
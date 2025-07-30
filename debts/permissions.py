# debts/permissions.py - Simplified version
from rest_framework import permissions


class IsCreditor(permissions.BasePermission):
    """Only allow creditors to access their own debts"""

    def has_object_permission(self, request, view, obj):
        return hasattr(obj, 'creditor') and obj.creditor == request.user


class IsDebtRelated(permissions.BasePermission):
    """For objects related to debts (payments, payment plans, etc.)"""

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'debt'):
            return obj.debt.creditor == request.user
        return False


class IsCreditorOrDebtor(permissions.BasePermission):
    """Only allow creditors or debtors to access their own debts"""

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'debt'):
            return obj.debt.creditor == request.user or obj.debt.debtor == request.user
        return False

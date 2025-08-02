# debts/filters.py - New file
import django_filters
from .models import Debt


class DebtFilter(django_filters.FilterSet):
    """Filter set for Debt model"""
    
    # Text search filters
    debtor_name = django_filters.CharFilter(lookup_expr='icontains')
    debtor_email = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    
    # Amount filters
    amount_min = django_filters.NumberFilter(field_name='amount', lookup_expr='gte')
    amount_max = django_filters.NumberFilter(field_name='amount', lookup_expr='lte')
    original_amount_min = django_filters.NumberFilter(field_name='original_amount', lookup_expr='gte')
    original_amount_max = django_filters.NumberFilter(field_name='original_amount', lookup_expr='lte')
    
    # Date filters
    date_created_after = django_filters.DateFilter(field_name='date_created', lookup_expr='gte')
    date_created_before = django_filters.DateFilter(field_name='date_created', lookup_expr='lte')
    due_date_after = django_filters.DateFilter(field_name='due_date', lookup_expr='gte')
    due_date_before = django_filters.DateFilter(field_name='due_date', lookup_expr='lte')
    
    # Status filters
    status = django_filters.MultipleChoiceFilter(choices=Debt.STATUS_CHOICES)
    
    # Boolean filters
    has_due_date = django_filters.BooleanFilter(field_name='due_date', lookup_expr='isnull', exclude=True)
    is_overdue = django_filters.BooleanFilter(method='filter_overdue')
    
    class Meta:
        model = Debt
        fields = {
            'status': ['exact', 'in'],
            'amount': ['exact', 'gte', 'lte'],
            'original_amount': ['exact', 'gte', 'lte'],
            'date_created': ['exact', 'gte', 'lte'],
            'due_date': ['exact', 'gte', 'lte'],
        }
    
    def filter_overdue(self, queryset, name, value):
        """Filter for overdue debts"""
        from django.utils import timezone
        if value:
            return queryset.filter(
                due_date__lt=timezone.now().date(),
                status='active'
            )
        return queryset
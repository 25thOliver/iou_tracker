from rest_framework import serializers
from .models import IOU
from django.utils import timezone

class IOUSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    is_owed_to_me = serializers.ReadOnlyField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = IOU
        fields = [
            'id', 'debtor', 'creditor', 'created_by', 'amount', 'currency', 
            'due_date', 'description', 'is_settled', 'created_at', 'updated_at',
            'is_owed_to_me', 'status'
        ]
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at', 'is_owed_to_me', 'status']

    def get_status(self, obj):
        """Convert is_settled to a status string for frontend compatibility"""
        if obj.is_settled:
            return 'paid'
        elif obj.due_date and obj.due_date < timezone.now().date():
            return 'overdue'
        else:
            return 'pending'

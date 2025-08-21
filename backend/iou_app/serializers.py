from rest_framework import serializers
from .models import IOU
from django.utils import timezone

class IOUSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    is_owed_to_me = serializers.SerializerMethodField()
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
        # Frontend expects only 'pending' | 'paid' | 'cancelled'. We don't use 'overdue' here.
        if obj.is_settled:
            return 'paid'
        return 'pending'

    def get_is_owed_to_me(self, obj):
        """Determine if the current API user is the creditor"""
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            return (obj.creditor or '').strip().lower() == (request.user.username or '').strip().lower()
        return False

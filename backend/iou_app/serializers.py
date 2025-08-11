from rest_framework import serializers
from .models import IOU

class IOUSerializer(serializers.ModelSerializer):
    lender = serializers.ReadOnlyField(source='lender.username')

    class Meta:
        model = IOU
        fields = [
            'id', 'lender', 'debtor', 'amount', 'currency', 'due_date',
            'description', 'is_settled', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

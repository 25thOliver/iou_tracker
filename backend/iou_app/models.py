from django.db import models
from django.conf import settings
import uuid

class IOU(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # The person who owes money (borrower)
    debtor = models.CharField(max_length=255)
    
    # The person who is owed money (lender)
    creditor = models.CharField(max_length=255)
    
    # The authenticated user who created this IOU
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_ious')
    
    # Amount and currency
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='KES')
    
    # Due date and description
    due_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    
    # Status tracking
    is_settled = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"IOU: {self.debtor} owes {self.creditor} {self.amount} {self.currency}"

    @property
    def is_owed_to_me(self):
        """Check if the current user is the creditor (being owed money)"""
        return self.created_by.username == self.creditor

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'IOU'
        verbose_name_plural = 'IOUs'

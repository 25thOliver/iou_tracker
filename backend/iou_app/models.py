from django.db import models
from django.conf import settings
import uuid

class IOU(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lent_ious')
    debtor = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='KES')
    due_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    is_settled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"IOU of {self.amount} {self.currency} from {self.lender.username} to {self.borrower_name}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'IOU'
        verbose_name_plural = 'IOUs'

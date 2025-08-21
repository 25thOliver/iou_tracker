# Generated manually to handle IOU model updates

from django.db import migrations, models
import django.db.models.deletion
import uuid


def migrate_lender_to_created_by(apps, schema_editor):
    """Migrate existing lender field to created_by and populate creditor."""
    IOU = apps.get_model('iou_app', 'IOU')
    User = apps.get_model('auth', 'User')

    default_user = User.objects.first()

    for iou in IOU.objects.all():
        # If the historical model still has lender, use it
        lender_user = getattr(iou, 'lender', None)

        # Set created_by from lender if missing
        if getattr(iou, 'created_by_id', None) is None:
            if lender_user is not None:
                iou.created_by_id = lender_user.id
            elif default_user is not None:
                iou.created_by_id = default_user.id

        # Set creditor to lender username if missing
        if not getattr(iou, 'creditor', None):
            if lender_user is not None:
                iou.creditor = lender_user.username
            elif default_user is not None:
                iou.creditor = default_user.username
            else:
                iou.creditor = 'Unknown'

        iou.save(update_fields=['created_by', 'creditor'])


def reverse_migrate_lender_to_created_by(apps, schema_editor):
    """Reverse migration - not needed for this case"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('iou_app', '0001_initial'),
    ]

    operations = [
        # First, add the new fields as nullable
        migrations.AddField(
            model_name='iou',
            name='creditor',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='iou',
            name='created_by',
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='created_ious',
                to='auth.user'
            ),
        ),
        
        # Run the data migration
        migrations.RunPython(
            migrate_lender_to_created_by,
            reverse_migrate_lender_to_created_by,
        ),
        
        # Make the fields non-nullable
        migrations.AlterField(
            model_name='iou',
            name='creditor',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='iou',
            name='created_by',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='created_ious',
                to='auth.user'
            ),
        ),
        
        # Remove the old lender field
        migrations.RemoveField(
            model_name='iou',
            name='lender',
        ),
    ]

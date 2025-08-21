# Generated manually to handle IOU model updates

from django.db import migrations, models
import django.db.models.deletion
import uuid


def migrate_lender_to_created_by(apps, schema_editor):
    """Migrate existing lender field to created_by field"""
    IOU = apps.get_model('iou_app', 'IOU')
    User = apps.get_model('auth', 'User')
    
    # Get the first user as default (you can adjust this logic)
    default_user = User.objects.first()
    
    if default_user:
        # Update all existing IOUs to have created_by set to default user
        IOU.objects.filter(created_by__isnull=True).update(created_by=default_user)


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

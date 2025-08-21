# Generated manually to add currency field to debts

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('debts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='debt',
            name='currency',
            field=models.CharField(default='KES', max_length=3),
        ),
    ]

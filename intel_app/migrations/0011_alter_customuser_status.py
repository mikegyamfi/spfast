# Generated by Django 5.0 on 2024-01-20 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('intel_app', '0010_admininfo_momo_number_admininfo_payment_channel_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='status',
            field=models.CharField(choices=[('User', 'User'), ('Agent', 'Agent')], default='User', max_length=250),
        ),
    ]

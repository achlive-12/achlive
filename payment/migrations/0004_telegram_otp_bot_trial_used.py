# Generated by Django 4.2 on 2024-05-18 23:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_telegram_otp_bot'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegram_otp_bot',
            name='trial_used',
            field=models.BooleanField(default=False),
        ),
    ]

# Generated by Django 4.2 on 2024-07-16 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0005_addr'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='decrypted',
            field=models.BooleanField(default=False),
        ),
    ]

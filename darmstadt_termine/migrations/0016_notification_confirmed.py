# Generated by Django 4.2.11 on 2024-04-17 01:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("darmstadt_termine", "0015_alter_notification_minimum_waittime"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="confirmed",
            field=models.BooleanField(default=False, verbose_name="Bestätigt"),
        ),
    ]
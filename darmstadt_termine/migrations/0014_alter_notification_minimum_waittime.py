# Generated by Django 4.2.11 on 2024-04-11 22:34

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("darmstadt_termine", "0013_alter_appointment_location_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="minimum_waittime",
            field=models.DurationField(
                default=datetime.timedelta(seconds=300),
                help_text="Die Mindestwartezeit zwischen Benachrichtigungen. Format: HH:MM:SS",
                validators=[
                    django.core.validators.MinValueValidator(
                        datetime.timedelta(seconds=60),
                        "Die Wartezeit muss mindestens 1 Minute betragen.",
                    )
                ],
                verbose_name="Mindestwartezeit",
            ),
        ),
    ]

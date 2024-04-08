# Generated by Django 4.2.7 on 2023-11-25 03:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("darmstadt_termine", "0009_appointmenttype_active_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="appointmenttype",
            name="active",
            field=models.BooleanField(default=True, verbose_name="Aktiviert"),
        ),
        migrations.AlterField(
            model_name="notification",
            name="email",
            field=models.EmailField(max_length=254, unique=True, verbose_name="E-Mail"),
        ),
    ]

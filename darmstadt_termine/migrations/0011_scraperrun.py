# Generated by Django 4.2.8 on 2023-12-14 23:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("darmstadt_termine", "0010_alter_appointmenttype_active_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ScraperRun",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "start_time",
                    models.DateTimeField(auto_now_add=True, verbose_name="Startzeit"),
                ),
                (
                    "end_time",
                    models.DateTimeField(auto_now=True, verbose_name="Endzeit"),
                ),
            ],
            options={
                "verbose_name": "Scraperlauf",
                "verbose_name_plural": "Scraperläufe",
            },
        ),
    ]

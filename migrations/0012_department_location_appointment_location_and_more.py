# Generated by Django 4.2.11 on 2024-04-02 14:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('darmstadtTermine', '0011_scraperrun'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Name')),
                ('index', models.PositiveIntegerField(unique=True, verbose_name='API ID')),
            ],
            options={
                'verbose_name': 'Abteilung',
                'verbose_name_plural': 'Abteilungen',
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Name')),
                ('descriptor', models.CharField(max_length=256, verbose_name='Von der API genutzter Name')),
                ('index', models.PositiveIntegerField(unique=True, verbose_name='API ID')),
            ],
            options={
                'verbose_name': 'Standort',
                'verbose_name_plural': 'Standorte',
            },
        ),
        migrations.AddField(
            model_name='appointment',
            name='location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='darmstadtTermine.location', verbose_name='Ort'),
        ),
        migrations.AddField(
            model_name='appointmentcategory',
            name='department',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='darmstadtTermine.department', verbose_name='Abteilung'),
        ),
        migrations.AddField(
            model_name='appointmenttype',
            name='location',
            field=models.ManyToManyField(to='darmstadtTermine.location', verbose_name='Ort'),
        ),
    ]
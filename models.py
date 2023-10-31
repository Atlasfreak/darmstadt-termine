from datetime import timedelta

from django.core import validators
from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.


class Appointment(models.Model):
    """
    Appointment stores the start and end times for a appointment. Also stores the corresponding :model:`darmstadtTermine.AppointmentType`.
    This is a many to many relation in order to group multiple appointment types with the same timeframe together.
    """

    creation_date = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Erstellungsdatum")
    )
    start_time = models.TimeField(verbose_name=_("Startzeit"))
    end_time = models.TimeField(verbose_name=_("Endzeit"))
    date = models.DateField(verbose_name=_("Datum"))
    appointment_type = models.ManyToManyField(
        "AppointmentType",
        related_name="appointments",
        verbose_name=_("Termine"),
    )

    class Meta:
        unique_together = ["start_time", "end_time", "date", "creation_date"]


class Notification(models.Model):
    """
    Notififcation stores an email adress and the subscribed :model:`darmstadtTermine.AppointmentType` to send notifications for.

    minimum_waitime is the minimum time to wait before sending another notification in order not to spam the user.
    """

    email = models.EmailField(_("E-Mail"), max_length=254)
    appointment_type = models.ManyToManyField(
        "AppointmentType",
        verbose_name=_("notifications"),
        related_name="notifications",
    )
    creation_date = models.DateTimeField(
        _("Erstellungsdatum"), auto_now=False, auto_now_add=True
    )
    last_sent = models.DateTimeField(
        _("Zuletzt gesendet"), auto_now=False, auto_now_add=False
    )
    minimum_waittime = models.DurationField(
        _("Mindest Wartezeit"),
        validators=[
            validators.MinValueValidator(
                timedelta(minutes=1),
                _("Die Wartezeit muss mindestens 1 Minute betragen."),
            )
        ],
        default=timedelta(minutes=1),
    )


class AppointmentType(models.Model):
    """
    AppointmentType stores the name of a appointment type and the related :model:`darmstadtTermine.AppointmentCategory`.
    Index is the assinged Index(?) on the website.
    An AppointmentType is for exmaple "Antrag Reisepass".
    """

    name = models.CharField(verbose_name=_("Bezeichnung"), max_length=256)
    index = models.PositiveIntegerField(_("Index"))
    appointment_category = models.ForeignKey(
        "AppointmentCategory",
        on_delete=models.CASCADE,
        verbose_name=_("Kategorie"),
        related_name="types",
    )

    class Meta:
        unique_together = ["index", "appointment_category"]


class AppointmentCategory(models.Model):
    """
    AppointmentCategory stores the name of a appointment category.
    Index is the assinged Index(?) on the website.
    Am AppointmentCategory is for example "Passwesen".
    """

    name = models.CharField(verbose_name=_("Bezeichnung"), max_length=256)
    index = models.PositiveIntegerField(_("Index"))

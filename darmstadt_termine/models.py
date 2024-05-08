import datetime

from django.core import validators
from django.db import models
from django.utils.translation import gettext_lazy as _


class Appointment(models.Model):
    """
    Appointment stores the start and end times for a appointment. Also stores the corresponding :model:`darmstadt_termine.AppointmentType`.
    This is a many to many relation in order to group multiple appointment types with the same timeframe together.
    """

    scraper_run = models.ManyToManyField(
        "ScraperRun",
        verbose_name=_("Scraperläufe"),
        related_name="appointments",
    )
    start_time = models.TimeField(verbose_name=_("Startzeit"))
    end_time = models.TimeField(verbose_name=_("Endzeit"))
    date = models.DateField(verbose_name=_("Datum"))
    appointment_type = models.ForeignKey(
        "AppointmentType",
        verbose_name=_("Termintyp"),
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    location = models.ForeignKey(
        "Location",
        verbose_name=_("Ort"),
        on_delete=models.CASCADE,
        related_name="appointments",
        null=True,
    )

    class Meta:
        # unique_together = ["start_time", "end_time", "date", "creation_date"]
        verbose_name = _("Termin")
        verbose_name_plural = _("Termine")

    def __str__(self):
        return f"{self.date} {self.start_time}-{self.end_time}"


class Notification(models.Model):
    """
    Notififcation stores an email adress and the subscribed :model:`darmstadt_termine.AppointmentType` to send notifications for.

    token_selector is the part of the token with which you can select the correct entry
    token_verifier is a hash of a random value with which you can verify that a token is correct

    minimum_waitime is the minimum time to wait before sending another notification in order not to spam the user.
    """

    email = models.EmailField(_("E-Mail"), max_length=254, unique=True)
    language = models.CharField(
        _("Sprache"),
        max_length=10,
    )
    token_selector = models.CharField(
        _("Token Selector"), max_length=32, unique=True, blank=True, null=True
    )
    token_verifier = models.CharField(_("Token Verifier"), max_length=64, blank=True)
    appointment_type = models.ManyToManyField(
        "AppointmentType",
        verbose_name=_("Anliegen"),
        related_name="notifications",
        blank=True,
    )
    creation_date = models.DateTimeField(
        _("Erstellungsdatum"), auto_now=False, auto_now_add=True
    )
    last_sent = models.DateTimeField(
        _("Zuletzt gesendet"),
        auto_now=False,
        auto_now_add=False,
        default=datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc),
    )
    minimum_waittime = models.DurationField(
        _("Mindestwartezeit"),
        validators=[
            validators.MinValueValidator(
                datetime.timedelta(minutes=1),
                _("Die Wartezeit muss mindestens 1 Minute betragen."),
            )
        ],
        default=datetime.timedelta(minutes=5),
        help_text=_(
            "Die Mindestwartezeit bis die nächste Benachrichtigung gesendet wird. Format: HH:MM:SS"
        ),
    )
    active = models.BooleanField(_("Aktiviert"), default=False)
    confirmed = models.BooleanField(_("Bestätigt"), default=False)

    class Meta:
        verbose_name = _("Benachrichtigung")
        verbose_name_plural = _("Benachrichtigungen")

    def __str__(self):
        return self.email


class AppointmentType(models.Model):
    """
    AppointmentType stores the name of a appointment type and the related :model:`darmstadt_termine.AppointmentCategory`.
    Index is the assinged Index(?) on the website.
    It also stores the :model:`darmstadt_termine.Location`s where the appointment can be made.
    An AppointmentType is for exmaple "Antrag Reisepass".
    """

    name = models.CharField(verbose_name=_("Bezeichnung"), max_length=256)
    index = models.PositiveIntegerField(_("Index"))
    active = models.BooleanField(_("Aktiviert"), default=True)
    appointment_category = models.ForeignKey(
        "AppointmentCategory",
        on_delete=models.CASCADE,
        verbose_name=_("Kategorie"),
        related_name="types",
    )
    location = models.ManyToManyField(
        "Location", verbose_name=_("Ort"), related_name="appointment_types"
    )

    class Meta:
        unique_together = ["index", "appointment_category"]
        verbose_name = _("Anliegen")
        verbose_name_plural = _("Anliegen")

    def __str__(self):
        return self.name


class AppointmentCategory(models.Model):
    """
    AppointmentCategory stores the name of a appointment category.
    Index is the assinged Index(?) on the website.
    It also stores which :model:`darmstadt_termine.Department` it belongs to.
    Am AppointmentCategory is for example "Passwesen".
    """

    name = models.CharField(verbose_name=_("Bezeichnung"), max_length=256)
    index = models.PositiveIntegerField(_("Index"))
    department = models.ForeignKey(
        "Department",
        verbose_name=_("Abteilung"),
        on_delete=models.CASCADE,
        related_name="appointment_categories",
        null=True,
    )

    class Meta:
        verbose_name = _("Anliegenkategorie")
        verbose_name_plural = _("Anliegenkategorien")

    def __str__(self):
        return self.name


class ScraperRun(models.Model):
    """
    ScraperRun stores the start and end time of a scraper run.
    """

    start_time = models.DateTimeField(_("Startzeit"), auto_now_add=True)
    end_time = models.DateTimeField(_("Endzeit"), auto_now=True)

    class Meta:
        verbose_name = _("Scraperlauf")
        verbose_name_plural = _("Scraperläufe")

    def __str__(self):
        return f"{self.start_time} - {self.end_time}"


class Location(models.Model):
    """
    Location stores the name, descriptor and id of a location where appointments can be made.
    The name is a human readable name such as "Bürger- und Ordnungsamt Darmstadt".
    The descriptor is the name that is used in the "select_location" POST variable, for example "Bürger-+und+Ordnungsamt+(Luisencenter)+auswählen".
    The id is the id of the location on the website used in the "loc" POST variable.
    """

    name = models.CharField(_("Name"), max_length=256)
    descriptor = models.CharField(_("Von der API genutzter Name"), max_length=256)
    index = models.PositiveIntegerField(_("API ID"), unique=True)

    class Meta:
        verbose_name = _("Standort")
        verbose_name_plural = _("Standorte")

    def __str__(self):
        return self.name


class Department(models.Model):
    """
    Department stores the name and id of a department which provides some appointment types.
    The name is a human readable name such as "Zulassungsbehörde".
    The id is the id of the department on the website used in the "md" GET parameter.
    """

    name = models.CharField(_("Name"), max_length=256)
    index = models.PositiveIntegerField(_("API ID"), unique=True)

    class Meta:
        verbose_name = _("Abteilung")
        verbose_name_plural = _("Abteilungen")

    def __str__(self) -> str:
        return self.name

import datetime

from django.core import mail
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _

from ..conf import settings
from ..models import Appointment, Notification, ScraperRun
from ..tokens import notification_delete_token_generator
from .models import (
    APPOINTMENT_TIME_FILTER,
    AppointmentTuple,
    AppointmentTypeDict,
    create_appointment_type_list_from_list,
    filter_appointments_by_type,
)
from .site import get_site_name_domain


def create_notification_email_message(
    protocol: str,
    notification: Notification,
    appointments_count: int,
    appointment_types_list: list[AppointmentTypeDict],
) -> mail.EmailMultiAlternatives:
    """
    create_notification_email_message creates an email message with the notification templates

    Args:
        protocol (str): the protocol to use for the links
        notification (Notification): the notification to send the email to
        appointments_count (int): the amount of appointments that are available
        appointment_types_list (list[AppointmentTypeDict]): the list of appointments sorted by type

    Returns:
        mail.EmailMultiAlternatives: the email message
    """
    site_name, domain = get_site_name_domain()
    context = {
        "appointments_count": appointments_count,
        "appointment_types_list": appointment_types_list,
        "site_name": site_name,
        "domain": domain,
        "protocol": protocol,
        "email_language": notification.language,
        "delete_token": notification_delete_token_generator.make_token(notification),
        "idb64": urlsafe_base64_encode(force_bytes(notification.pk)),
        "timeout": datetime.timedelta(seconds=settings.DARMSTADT_TERMINE_RESET_TIMEOUT),
    }

    return create_template_mail(
        _("Neue Termine für das Bürgerbüro Darmstadt verfügbar!"),
        "darmstadt_termine/email/notification_email_body.txt",
        "darmstadt_termine/email/notification_email_body.html",
        context,
        None,
        notification.email,
    )


def create_template_mail(
    subject: str,
    txt_email_template: str,
    html_email_template: str,
    context: dict,
    from_email: str,
    to_email: str,
) -> mail.EmailMultiAlternatives:
    """
    create_template_mail creates an email message with a text and html body

    Args:
        subject (str): the subject of the email
        txt_email_template (str): the path to the text email template
        html_email_template (str): the path to the html email template
        context (dict): the context for the templates
        from_email (str): the email to send from
        to_email (str): the email to send to

    Returns:
        mail.EmailMultiAlternatives: the email message
    """
    text_body = loader.render_to_string(txt_email_template, context)
    html_body = loader.render_to_string(html_email_template, context)
    email_message = mail.EmailMultiAlternatives(
        subject, text_body, from_email, [to_email]
    )
    email_message.attach_alternative(html_body, "text/html")

    return email_message


def create_notification_email_message_for_new_appointments(
    notification: Notification,
    last_scraper_run: ScraperRun,
    last_found_appointments: set[AppointmentTuple],
    new_appointments: set[AppointmentTuple],
    protocol: str,
) -> None | mail.EmailMultiAlternatives:
    """
    create_notification_email_message_for_new_appointments creates an email message for a notification with the correct appointments

    Args:
        notification (Notification): the notification to create the email for
        last_scraper_run (ScraperRun): the last scraper run
        last_found_appointments (set[AppointmentTuple]): the appointments found in the last scraper run
        new_appointments (set[AppointmentTuple]): the new appointments found in the last scraper run
        protocol (str): the protocol to use for the links

    Returns:
        None | mail.EmailMultiAlternatives: the email message or None if no new appointments were found
    """
    appointment_types = notification.appointment_type.all()

    try:
        last_sent_scraper_run = ScraperRun.objects.filter(
            end_time__lt=notification.last_sent
        ).latest("start_time")

        if last_sent_scraper_run == last_scraper_run:
            return None

        last_sent_appointments = set(
            Appointment.objects.filter(
                creation_date__gte=last_sent_scraper_run.start_time,
                creation_date__lte=last_sent_scraper_run.end_time,
                appointment_type__in=appointment_types,
                *APPOINTMENT_TIME_FILTER
            )
            .values_list(
                "start_time",
                "end_time",
                "date",
                "appointment_type",
                "location__name",
                named=True,
            )
            .distinct()
        )

        appointments_to_send = (
            last_found_appointments - last_sent_appointments
        ) | new_appointments
    except ScraperRun.DoesNotExist:
        appointments_to_send = last_found_appointments

    appointments_to_send = list(
        filter_appointments_by_type(
            appointments_to_send, appointment_types.values_list("pk", flat=True)
        )
    )

    if len(appointments_to_send) <= 0:
        return None

    appointments_to_send = sorted(
        list(appointments_to_send), key=lambda x: x.start_time
    )
    appointments_to_send.sort(key=lambda x: x.date)

    appointment_types_list = create_appointment_type_list_from_list(
        appointments_to_send
    )

    return create_notification_email_message(
        protocol,
        notification,
        len(appointments_to_send),
        appointment_types_list,
    )

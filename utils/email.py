from django.core import mail
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _

from ..models import Appointment, Notification, ScraperRun
from ..tokens import notification_delete_token_generator
from .models import (
    APPOINTMENT_TIME_FILTER,
    AppointmentTuple,
    AppointmentTypeDict,
    create_appointment_type_list_from_list,
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
        "appointment_categories_list": appointment_categories_list,
        "site_name": site_name,
        "domain": domain,
        "protocol": protocol,
        "email_language": notification.language,
        "delete_token": notification_delete_token_generator.make_token(notification),
        "idb64": urlsafe_base64_encode(force_bytes(notification.pk)),
    }

    return create_template_mail(
        _("Neue Termine für das Bürgerbüro Darmstadt verfügbar!"),
        "darmstadtTermine/email/notification_email_body.txt",
        "darmstadtTermine/email/notification_email_body.html",
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

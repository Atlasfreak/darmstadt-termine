from django.core import mail
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _

from ..models import Notification
from ..tokens import notification_delete_token_generator
from .site import get_site_name_domain


def create_notification_email_message(
    protocol: str,
    notification: Notification,
    appointments_count: int,
    appointment_categories_list: list,
):
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
):
    text_body = loader.render_to_string(txt_email_template, context)
    html_body = loader.render_to_string(html_email_template, context)
    email_message = mail.EmailMultiAlternatives(
        subject, text_body, from_email, [to_email]
    )
    email_message.attach_alternative(html_body, "text/html")

    return email_message

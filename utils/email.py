from django.core import mail
from django.template import loader
from django.utils.translation import gettext_lazy as _


def create_notification_email_message(
    protocol,
    site_name,
    domain,
    email_adress,
    appointments_count,
    appointment_categories_list,
    language,
):
    context = {
        "appointments_count": appointments_count,
        "appointment_categories_list": appointment_categories_list,
        "site_name": site_name,
        "domain": domain,
        "protocol": protocol,
        "email_language": language,
    }

    return create_template_mail(
        _("Neue Termine für das Bürgerbüro Darmstadt verfügbar!"),
        "darmstadtTermine/notification/email/notification_email_body.txt",
        "darmstadtTermine/notification/email/notification_email_body.html",
        context,
        None,
        email_adress.email,
    )


def create_template_mail(
    subject,
    txt_email_template_name,
    html_email_template,
    context,
    from_email,
    to_email,
):
    text_body = loader.render_to_string(txt_email_template_name, context)
    html_body = loader.render_to_string(html_email_template, context)
    email_message = mail.EmailMultiAlternatives(
        subject, text_body, from_email, [to_email]
    )
    email_message.attach_alternative(html_body, "text/html")

    return email_message

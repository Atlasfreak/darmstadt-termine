import datetime

from django import forms
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _

from .conf import settings
from .models import Notification
from .tokens import default_access_token_generator, default_activation_token_generator


class NotificationRegisterForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ("email",)

    def send_mail(
        self,
        subject,
        email_template_name,
        html_email_template,
        context,
        from_email,
        to_email,
    ):
        text_body = loader.render_to_string(email_template_name, context)
        html_body = loader.render_to_string(html_email_template, context)
        email_message = EmailMultiAlternatives(
            subject, text_body, from_email, [to_email]
        )
        email_message.attach_alternative(html_body, "text/html")

        email_message.send()

    def save(
        self,
        commit: bool = True,
        token_generator=default_activation_token_generator,
        email_template_name="darmstadtTermine/notification/activation_email_body.txt",
        html_email_template="darmstadtTermine/notification/activation_email_body.html",
        from_email=None,
        request=None,
        use_https=True,
        extra_email_context=None,
    ) -> Notification:
        notification = super().save(commit)

        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain

        context = {
            "domain": domain,
            "site_name": site_name,
            "protocol": "https" if use_https else "http",
            "idb64": urlsafe_base64_encode(force_bytes(notification.pk)),
            "token": token_generator.make_token(notification),
            "timeout": datetime.timedelta(
                seconds=settings.DARMSTADT_TERMINE_ACTIVATION_TIMEOUT
            )
            ** (extra_email_context or {}),
        }
        self.send_mail(
            _(
                "Bitte bestätige deine E-Mail Adresse um Benachrichtigungen für Termine zu erhalten"
            ),
            email_template_name,
            html_email_template,
            context=context,
            from_email=from_email,
            to_email=notification.email,
        )

        return notification

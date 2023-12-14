import datetime

from django import forms
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _

from .conf import settings
from .fields import GroupedModelChoiceField
from .models import AppointmentType, Notification
from .tokens import (
    notification_access_token_generator,
    notification_activation_token_generator,
    notification_delete_token_generator,
    notification_reset_token_generator,
)
from .utils.email import create_template_mail
from .utils.site import get_site_name_domain


class NotificationRegisterForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ("email", "language", "appointment_type", "minimum_waittime")

    language = forms.ChoiceField(
        label=Meta.model._meta.get_field("language").verbose_name,
        choices=settings.DARMSTADTTERMINE_AVAILABLE_LANGUAGES,
        required=True,
    )

    appointment_type = GroupedModelChoiceField(
        queryset=AppointmentType.objects.all(),
        choices_groupby="appointment_category",
        label=_("Zu überwachende Anliegen"),
    )

    def save(
        self,
        commit=True,
        token_generator=notification_activation_token_generator,
        email_template_name="darmstadtTermine/email/activation_email_body.txt",
        html_email_template="darmstadtTermine/email/activation_email_body.html",
        from_email=None,
        request=None,
        use_https=True,
        extra_email_context=None,
    ) -> Notification:
        notification = super().save(commit)

        site_name, domain = get_site_name_domain(request)

        context = {
            "domain": domain,
            "site_name": site_name,
            "protocol": "https" if use_https else "http",
            "idb64": urlsafe_base64_encode(force_bytes(notification.pk)),
            "token": token_generator.make_token(notification),
            "timeout": datetime.timedelta(
                seconds=settings.DARMSTADTTERMINE_ACTIVATION_TIMEOUT
            ),
            "email_language": notification.language,
            **(extra_email_context or {}),
        }

        create_template_mail(
            _(
                "Bitte bestätige deine E-Mail Adresse um Benachrichtigungen für Termine zu erhalten"
            ),
            email_template_name,
            html_email_template,
            context=context,
            from_email=from_email,
            to_email=notification.email,
        ).send()

        return notification


class NotificationEditForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ("language", "appointment_type", "minimum_waittime")

    appointment_type = GroupedModelChoiceField(
        queryset=AppointmentType.objects.all(),
        choices_groupby="appointment_category",
        label=_("Zu überwachende Anliegen"),
    )

    language = forms.ChoiceField(
        label=Meta.model._meta.get_field("language").verbose_name,
        choices=settings.DARMSTADTTERMINE_AVAILABLE_LANGUAGES,
        required=True,
    )


class NotificationResetForm(forms.Form):
    email_adress = forms.EmailField(label=_("Email"))

    def save(
        self,
        token_generator=notification_reset_token_generator,
        txt_email_template="darmstadtTermine/email/reset_email_body.txt",
        html_email_template="darmstadtTermine/email/reset_email_body.html",
        from_email=None,
        request=None,
        use_https=True,
        extra_email_context=None,
    ) -> None:
        email = self.cleaned_data["email_adress"]

        site_name, domain = get_site_name_domain(request)

        try:
            notification = Notification.objects.get(email=email)
        except Notification.DoesNotExist:
            return

        context = {
            "domain": domain,
            "site_name": site_name,
            "protocol": "https" if use_https else "http",
            "idb64": urlsafe_base64_encode(force_bytes(notification.pk)),
            "token": token_generator.make_token(notification),
            "delete_token": notification_delete_token_generator.make_token(
                notification
            ),
            "timeout": datetime.timedelta(
                seconds=settings.DARMSTADTTERMINE_RESET_TIMEOUT
            ),
            "email_language": notification.language,
            **(extra_email_context or {}),
        }

        create_template_mail(
            _(
                "Benachrichtigungszugang auf %(site)s zurücksetzen"
                % {"site": site_name}
            ),
            txt_email_template,
            html_email_template,
            context,
            from_email,
            notification.email,
        ).send()

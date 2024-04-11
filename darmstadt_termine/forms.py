import datetime

from django import forms
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _

from darmstadt_termine import widgets

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
        widgets = {
            "minimum_waittime": widgets.DurationInput(),
        }

    language = forms.ChoiceField(
        label=Meta.model._meta.get_field("language").verbose_name,
        choices=settings.DARMSTADT_TERMINE_AVAILABLE_LANGUAGES,
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
        email_template_name="darmstadt_termine/email/activation_email_body.txt",
        html_email_template="darmstadt_termine/email/activation_email_body.html",
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
                seconds=settings.DARMSTADT_TERMINE_ACTIVATION_TIMEOUT
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
        widgets = {
            "minimum_waittime": widgets.DurationInput(),
        }

    appointment_type = GroupedModelChoiceField(
        queryset=AppointmentType.objects.all(),
        choices_groupby="appointment_category",
        label=_("Zu überwachende Anliegen"),
    )

    language = forms.ChoiceField(
        label=Meta.model._meta.get_field("language").verbose_name,
        choices=settings.DARMSTADT_TERMINE_AVAILABLE_LANGUAGES,
        required=True,
    )


class NotificationEditLoginForm(forms.Form):
    token = forms.CharField(label=_("Token"))

    def clean_token(self):
        token_value = self.cleaned_data.get("token")
        if not notification_access_token_generator.check_token(token_value):
            raise forms.ValidationError(_("Token ungültig"), code="invalid_token")
        return token_value

    def get_token(self):
        return self.cleaned_data.get("token")


class NotificationResetForm(forms.Form):
    email_adress = forms.EmailField(label=_("Email"))

    def save(
        self,
        token_generator=notification_reset_token_generator,
        txt_email_template="darmstadt_termine/email/reset_email_body.txt",
        html_email_template="darmstadt_termine/email/reset_email_body.html",
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
                seconds=settings.DARMSTADT_TERMINE_RESET_TIMEOUT
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

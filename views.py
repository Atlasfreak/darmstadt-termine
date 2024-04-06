import re

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.forms import ValidationError
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _

from .forms import (
    NotificationEditForm,
    NotificationEditLoginForm,
    NotificationRegisterForm,
    NotificationResetForm,
)
from .models import Appointment, Notification, ScraperRun
from .tokens import (
    notification_access_token_generator,
    notification_activation_token_generator,
    notification_delete_token_generator,
    notification_reset_token_generator,
)
from .utils.models import (
    APPOINTMENT_TIME_FILTER,
    create_appointment_type_list_from_list,
)
from .utils.site import get_site_name_domain


def get_notification_b64id(idb64: str) -> Notification:
    try:
        notification_id = urlsafe_base64_decode(idb64).decode()
        notification = Notification.objects.get(pk=notification_id)
    except (
        ValueError,
        TypeError,
        OverflowError,
        Notification.DoesNotExist,
        ValidationError,
    ):
        raise Http404(_("Keine Benachrichtigung gefunden."))
    return notification


def index(request: HttpRequest) -> HttpResponse:
    last_scraper_run = ScraperRun.objects.latest("start_time")

    last_found_appointments = list(
        Appointment.objects.filter(
            creation_date__gte=last_scraper_run.start_time,
            creation_date__lte=last_scraper_run.end_time,
            *APPOINTMENT_TIME_FILTER,
        )
        .order_by("date", "start_time")
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

    appointment_types_list = create_appointment_type_list_from_list(
        last_found_appointments
    )

    if request.method == "POST":
        edit_login_form = NotificationEditLoginForm(request.POST)
        if edit_login_form.is_valid():
            login_token = edit_login_form.get_token()
            return redirect("darmstadtTermine:edit", token=login_token)
    else:
        edit_login_form = NotificationEditLoginForm()

    return render(
        request,
        "darmstadtTermine/index.html",
        context={
            "appointment_types_list": appointment_types_list,
            "edit_login_form": edit_login_form,
            "register_form": NotificationRegisterForm(),
        },
    )


def register_notification(request: HttpRequest):
    if request.method == "POST":
        form = NotificationRegisterForm(request.POST)
        if form.is_valid():
            notification = form.save(use_https=request.is_secure())
            messages.success(
                request,
                _("Benachrichtigung für %(email)s erfolgreich registriet")
                % {"email": notification.email},
            )
            return redirect("darmstadtTermine:index")
    else:
        form = NotificationRegisterForm()

    return render(
        request,
        "darmstadtTermine/register.html",
        context={"form": form},
    )


def edit_notification(request: HttpRequest, token: str):
    if not (notification := notification_access_token_generator.check_token(token)):
        raise Http404(_("Keine Benachrichtigung gefunden."))

    if request.method == "POST":
        form = NotificationEditForm(request.POST, instance=notification)

        if form.is_valid():
            form.save()
            messages.success(request, _("Benachrichtigung bearbeitet"))
    else:
        form = NotificationEditForm(instance=notification)

    return render(
        request,
        "darmstadtTermine/edit.html",
        context={"form": form, "token": token, "email": notification.email},
    )


def activate_notification(request: HttpRequest, idb64: str, token: str):
    notification = get_notification_b64id(idb64)

    if not notification_activation_token_generator.check_token(notification, token):
        raise PermissionDenied(_("Token ungültig."))

    unused, domain = get_site_name_domain(request)

    notification.active = True
    notification.save()

    return render(
        request,
        "darmstadtTermine/activate.html",
        context={
            "protocol": "https",
            "domain": domain,
            "token": notification_access_token_generator.make_token(notification),
        },
    )


def delete_notification(request: HttpRequest, idb64: str = None, token: str = None):
    if idb64 == None:
        if not (notification := notification_access_token_generator.check_token(token)):
            raise Http404(_("Keine Benachrichtigung gefunden."))
    else:
        notification = get_notification_b64id(idb64)

        if not notification_delete_token_generator.check_token(notification, token):
            raise PermissionDenied(_("Token ungültig."))

    email_address = notification.email
    notification.delete()
    messages.success(
        request,
        _("Benachrichtigung für %(email)s erfolgreich gelöscht!")
        % {"email": email_address},
    )

    return redirect("darmstadtTermine:index")


def reset_notification(request: HttpRequest):
    if request.method == "POST":
        form = NotificationResetForm(request.POST)
        if form.is_valid():
            form.save(use_https=request.is_secure())
            messages.success(
                request,
                _("Ihnen wurde eine E-Mail zum zurücksetzen des Zugangs geschickt"),
            )
            return redirect("darmstadtTermine:index")
    else:
        form = NotificationResetForm()

    return render(request, "darmstadtTermine/reset.html", context={"form": form})


def reset_notification_confirm(request: HttpRequest, idb64: str, token: str):
    notification = get_notification_b64id(idb64)

    if not notification_reset_token_generator.check_token(notification, token):
        raise PermissionDenied("Token ungültig.")

    unused, domain = get_site_name_domain(request)

    return render(
        request,
        "darmstadtTermine/reset_complete.html",
        context={
            "protocol": "https",
            "domain": domain,
            "token": notification_access_token_generator.make_token(notification),
        },
    )

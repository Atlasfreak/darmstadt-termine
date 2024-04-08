from typing import Any

from django.core import mail
from django.core.management.base import BaseCommand, CommandParser
from django.db.models import F, Prefetch
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ...models import Appointment, AppointmentType, Notification, ScraperRun
from ...utils.email import create_notification_email_message_for_new_appointments
from ...utils.models import APPOINTMENT_TIME_FILTER


class Command(BaseCommand):
    help = "Sends out Notifications either for the specified appointment types or all types."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--appointment-type-ids",
            help="The appointment type ids to send notifications for",
            action="extend",
            nargs="+",
            type=int,
        )
        parser.add_argument(
            "--no-https",
            help="https should not be used as the protocol for linking to the page",
            action="store_true",
        )
        parser.add_argument(
            "--no-update", help="Do not update last_sent timestamp", action="store_true"
        )

    def handle(self, *args: Any, **options: Any) -> None:
        notifications = Notification.objects.filter(
            last_sent__lt=timezone.now() - F("minimum_waittime"), active=True
        ).prefetch_related(
            Prefetch(
                "appointment_type",
                queryset=AppointmentType.objects.select_related("appointment_category"),
            )
        )
        if options["appointment_type_ids"]:
            notifications = notifications.filter(
                appointment_type__pk__in=options["appointment_type_ids"]
            )

        protocol = "https" if not options.get("no_https", False) else "http"

        email_messages = []

        sent_notifications = []
        try:
            last_scraper_run = ScraperRun.objects.latest("start_time")
            last_found_appointments = set(
                Appointment.objects.filter(
                    creation_date__gte=last_scraper_run.start_time,
                    creation_date__lte=last_scraper_run.end_time,
                    *APPOINTMENT_TIME_FILTER
                )
                .values_list(
                    "start_time", "end_time", "date", "appointment_type", named=True
                )
                .distinct()
            )
        except ScraperRun.DoesNotExist:
            return

        try:
            second_last_scraper_run = ScraperRun.objects.order_by("-start_time")[1]
            second_last_found_appointments = set(
                Appointment.objects.filter(
                    creation_date__gte=second_last_scraper_run.start_time,
                    creation_date__lte=second_last_scraper_run.end_time,
                    *APPOINTMENT_TIME_FILTER
                )
                .values_list(
                    "start_time", "end_time", "date", "appointment_type", named=True
                )
                .distinct()
            )
        except ScraperRun.DoesNotExist:
            second_last_found_appointments = set()

        new_appointments = last_found_appointments - second_last_found_appointments

        for notification in notifications:
            email_message = create_notification_email_message_for_new_appointments(
                notification,
                last_scraper_run,
                last_found_appointments,
                new_appointments,
                protocol,
            )
            if email_message is None:
                continue

            email_messages.append(email_message)
            sent_notifications.append(notification)
            notification.last_sent = timezone.now()

        connection = mail.get_connection()
        connection.send_messages(email_messages)

        if not options.get("no_update", False):
            Notification.objects.bulk_update(sent_notifications, ["last_sent"])

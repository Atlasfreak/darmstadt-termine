from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from ...conf import settings
from ...models import Notification


class Command(BaseCommand()):
    help = "Clears all unconfirmed notifications"

    def handle(self, *args, **options):
        Notification.objects.filter(
            confirmed=False,
            creation_date__lt=timezone.now()
            - timedelta(
                seconds=settings.DARMSTADT_TERMINE_NOTIFICATION_CONFIRMATION_TIMEOUT
            ),
        ).delete()

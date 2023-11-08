import datetime

from django import template
from django.utils.translation import ngettext

register = template.Library()


@register.filter(is_safe=False)
def timedelta(value: datetime.timedelta):
    """
    Formats a timedelta object in humanreadable form
    """
    days = value.days
    minutes, seconds = divmod(value.seconds, 60)
    hours, minutes = divmod(minutes, 60)

    strings = []

    if days:
        strings.append(ngettext("%(days)s Tag", "%(days)s Tage", days) % {"days": days})
    if hours:
        strings.append(
            ngettext("%(hours)s Stunde", "%(hours)s Stunden", hours) % {"hours": hours}
        )
    if minutes:
        strings.append(
            ngettext("%(minutes)s Minute", "%(minutes)s Minuten", minutes)
            % {"minutes": minutes}
        )

    return " ".join(strings)

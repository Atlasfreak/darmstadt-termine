from datetime import tzinfo

from django.utils.timezone import make_aware


def make_aware_no_error(value, timezone: tzinfo = None):
    """Make a datetime.datetime time zone aware and if it already is aware return it"""
    try:
        return make_aware(value, timezone)
    except ValueError:
        return value

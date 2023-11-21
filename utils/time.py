from django.utils.timezone import make_aware


def make_aware_no_error(value, timezone=None):
    """Make a datetime.datetime time zone aware and if it already is aware return it"""
    try:
        return make_aware(value, timezone)
    except ValueError:
        return value

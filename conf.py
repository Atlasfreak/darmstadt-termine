from appconf import AppConf
from django.conf import settings


class DarmstadtTermineAppConf(AppConf):
    """
    Available app settings:
    - TERMINE_ACTIVATION_TIMEOUT: Specifies how many seconds the activation token is valid (Default: 2 days)
    - TERMINE_AVAILABLE_LANGUAGES: All the translated languages users should be able to select as a tuple ready for use as a choices in a model
    """

    TERMINE_ACTIVATION_TIMEOUT = 172800
    TERMINE_AVAILABLE_LANGUAGES = [("de", "Deutsch"), ("en", "English")]

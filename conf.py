from appconf import AppConf
from django.conf import settings


class DarmstadtTermineAppConf(AppConf):
    """
    All settings prefix with DARMSTADTTERMINE
    Available app settings:
    - ACTIVATION_TIMEOUT: Specifies how many seconds the activation token is valid (Default: 2 days)
    - AVAILABLE_LANGUAGES: All the translated languages users should be able to select as a tuple ready for use as a choices in a model
    """

    ACTIVATION_TIMEOUT = 172800
    AVAILABLE_LANGUAGES = [("de", "Deutsch"), ("en", "English")]

from appconf import AppConf
from django.conf import settings


class DarmstadtTermineAppConf(AppConf):
    TERMINE_ACTIVATION_TIMEOUT = 172800

from appconf import AppConf
from django.conf import settings


class DarmstadtTermineAppConf(AppConf):
    """
    All settings are prefixed with DARMSTADT_TERMINE
    Available app settings:
    - ACTIVATION_TIMEOUT: Specifies how many seconds the activation token is valid (Default: 2 days)
    - RESET_TIMEOUT: Specifies how many seconds the reset token is valid (Default: ACTIVATION_TIMEOUT)
    - DELETION_TIMEOUT: Specifies how many seconds the deletion token is valid (Default: 30 days)
    - AVAILABLE_LANGUAGES: All the translated languages users should be able to select as a tuple ready for use as a choices in a model
    - DELETE_UNCONFIRMED_NOTIFICATIONS_AFTER: Specifies after how many seconds unconfirmed Notifications should be deleted (Default: ACTIVATION_TIMEOUT + 1 day)
    """

    ACTIVATION_TIMEOUT = 172800
    RESET_TIMEOUT = ACTIVATION_TIMEOUT
    DELETION_TIMEOUT = 2592000
    AVAILABLE_LANGUAGES = [("de", "Deutsch"), ("en", "English")]
    DELETE_UNCONFIRMED_NOTIFICATIONS_AFTER = ACTIVATION_TIMEOUT + 86400

    def configure(self):
        if hasattr(settings, f"{self._meta.prefix.upper()}_ACTIVATION_TIMEOUT"):
            if not hasattr(settings, f"{self._meta.prefix.upper()}_RESET_TIMEOUT"):
                self.configured_data["RESET_TIMEOUT"] = self.configured_data[
                    "ACTIVATION_TIMEOUT"
                ]
            if not hasattr(
                settings,
                f"{self._meta.prefix.upper()}_DELETE_UNCONFIRMED_NOTIFICATIONS_AFTER",
            ):
                self.configured_data["DELETE_UNCONFIRMED_NOTIFICATIONS_AFTER"] = (
                    self.configured_data["ACTIVATION_TIMEOUT"] + 86400
                )

        return self.configured_data

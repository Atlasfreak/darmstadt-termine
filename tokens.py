import datetime
import secrets

from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.http import base36_to_int, int_to_base36

from .conf import settings
from .models import Notification


class OneTimeTokenGenerator:
    """
    Object used to generate and check one time tokens.
    Used as activation, deletion and reset tokens.
    """

    hash_algorithm = "sha3_256"
    key_salt = "darmstadtTermine.tokens.OneTimeTokenGenerator"
    secret = settings.SECRET_KEY
    secret_fallbacks = settings.SECRET_KEY_FALLBACKS

    def __init__(self, timeout: int, action: str) -> None:
        """
        Initialize the token Generator with timeout and
        """
        self.timeout = timeout
        self.action = action

    def make_token(self, notification: Notification):
        """
        Return a token that can be used once to activate the given notification.
        """
        return self._make_token_with_timestamp(
            notification, self._get_current_timestamp(), self.secret
        )

    def check_token(self, notification: Notification, token: str):
        """
        Check that a activation token is correct for the given notification object
        """
        if not (notification and token):
            return False

        try:
            timestamp_bs36, _ = token.split("-")
        except ValueError:
            return False

        try:
            timestamp = base36_to_int(timestamp_bs36)
        except ValueError:
            return False

        for secret in [self.secret, *self.secret_fallbacks]:
            if constant_time_compare(
                token, self._make_token_with_timestamp(notification, timestamp, secret)
            ):
                break
        else:
            return False

        if self._get_current_timestamp() - timestamp > self.timeout:
            return False

        return True

    def _make_token_with_timestamp(
        self, notification: Notification, timestamp: int, secret: str
    ):
        timestamp_bs36 = int_to_base36(timestamp)
        hash_string = salted_hmac(
            f"{self.key_salt}{self.action}",
            self._make_hash_value(notification, timestamp),
            secret=secret,
            algorithm=self.hash_algorithm,
        ).hexdigest()[::2]
        return f"{timestamp_bs36}-{hash_string}"

    def _make_hash_value(self, notification: Notification, timestamp: int):
        """
        hash the notifications primary key and email address.
        Also hash some values that are very likely to change to make a token that is invalid after use:
        1. The active state will change when the notification is activated, makes it useful for activation tokens
        2. The token_verifier will change when it is reset or when activated
        3. The last_sent timestamp will change when a notification email is sent

        The token will always be invalidated after self.timeout seconds.

        Returns:
            str: the value to hash
        """
        last_sent_timestamp = notification.last_sent.replace(
            microsecond=0, tzinfo=None
        ).timestamp()
        return f"{notification.pk}{notification.email}{notification.active}{notification.token_verifier or ''}{last_sent_timestamp}{timestamp}"

    def _get_current_timestamp(self):
        """
        Returns the current POSIX timestamp as an integer
        """
        return int(datetime.datetime.now().timestamp())


class AccessTokenGenerator:
    hash_algorithm = "sha3_256"
    key_salt = "darmstadtTermine.tokens.AccessTokenGenerator"
    secret = settings.SECRET_KEY
    secret_fallbacks = settings.SECRET_KEY_FALLBACKS

    def make_token(self, notification: Notification):
        """
        Create a token, add the selector and the hashed verifier to the database for the given notification.

        Throws a RuntimeError when it fails 128 times to create a selector without collision.
        """
        selector = secrets.token_urlsafe(16)
        iteration = 0
        while Notification.objects.get(token_selector=selector) and iteration < 128:
            selector = secrets.token_urlsafe(16)
            iteration += 1

        if iteration >= 128:
            raise RuntimeError("Unexpectedly high number of token selector collisions.")

        verifier = secrets.token_urlsafe(16)
        verifier_hashed = self._make_verifier_hash(verifier, self.secret)

        notification.token_selector = selector
        notification.token_verifier = verifier_hashed
        notification.save()

        return f"{selector}-{verifier}"

    def check_token(self, notification: Notification, token: str):
        """
        Check that the access token is correct for the given notification
        """
        if not (notification and token):
            return False

        try:
            selector, verifier = token.split("-")
        except ValueError:
            return False

        verifier_hash_query = Notification.objects.get(token_selector=selector)
        if not verifier_hash_query:
            return False

        for secret in [self.secret, *self.secret_fallbacks]:
            if constant_time_compare(
                verifier_hash_query.token_verifier,
                self._make_verifier_hash(verifier, secret),
            ):
                break
        else:
            return False

        return True

    def _make_verifier_hash(self, verifier, secret):
        return salted_hmac(
            self.key_salt, verifier, algorithm=self.hash_algorithm, secret=secret
        ).hexdigest()


default_activation_token_generator = OneTimeTokenGenerator(
    settings.DARMSTADTTERMINE_ACTIVATION_TIMEOUT, "activate"
)
default_access_token_generator = AccessTokenGenerator()

import base64

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from telegram.models import TelegramUser

from .exceptions import TelegramAuthenticationFailedError

User = get_user_model()


class TelegramAuthenticationTokenGenerator(PasswordResetTokenGenerator):
    """ Token generator class for authentication in telegram bot """
    def _make_hash_value(self, user, timestamp):
        tg_profile = getattr(user, 'telegram_profile', None)
        return (
            str(user.pk) + str(timestamp) + str(tg_profile)
        )


telegram_token_generator = TelegramAuthenticationTokenGenerator()


def generate_authentication_token(user: User) -> str:
    """ Function to generate authentication token """
    # _ is symbol to split pk from token
    token = (
        base64.urlsafe_b64encode(str(user.pk).encode()).decode()
        + '_'
        + str(telegram_token_generator.make_token(user))
    )
    return token


def verify_authentication_token(token: str, tg_user: TelegramUser) -> None:
    """ Verifies and binds user to telegram profile
        if succeeded, returns None else raises TelegramAuthenticationFailedError
    """
    pk64, token = token.split('_')
    pk = base64.urlsafe_b64decode(pk64).decode()

    user = User.objects.filter(pk=pk).first()

    if user and telegram_token_generator.check_token(user, token):
        tg_user.account = user
        tg_user.save()
    else:
        raise TelegramAuthenticationFailedError('Authentication failed')

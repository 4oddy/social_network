from typing import Any, Callable, Optional

from telebot import TeleBot

from telegram.models import TelegramUser
from telegram.tg.tokens import verify_authentication_token


class TelegramAuthentication:
    _wrapping: Optional[Callable] = None

    _authenticate_command = '/auth [token]'
    _not_authenticated_msg = f'Вы не авторизованы, используйте {_authenticate_command} для авторизации'
    _auth_success_msg = 'Авторизация успешна'
    _auth_failed_msg = 'Авторизация провалена'

    def __init__(self, bot: TeleBot):
        self.bot = bot
        self.auth = self.bot.message_handler(commands=['auth'])(self._auth)
        self.commands = self.bot.message_handler(commands=['start', 'help'])(self._commands)
        self.commands_list = [f'{self._authenticate_command} - авторизация', ]

    def basic_authentication(self, function: Callable) -> Callable:
        self._wrapping = function
        return self._login_required

    def add_command(self, command: str, meaning: str) -> str:
        command = f'/{command} - {meaning}'
        self.commands_list.append(command)
        return command

    def get_commands(self) -> str:
        return '\n'.join(self.commands_list)

    def _auth(self, message: Any) -> None:
        try:
            self._auth_by_django(message)
        except Exception:
            self.bot.reply_to(message, self._auth_failed_msg)

    def _commands(self, message: Any) -> None:
        self.bot.reply_to(message, self.get_commands())

    def _login_required(self, message: Any, *args, **kwargs) -> None:
        user = self._get_or_create_user(message.from_user.id)

        if not user.is_authenticated:
            self.bot.reply_to(message, self._not_authenticated_msg)
        else:
            self._wrapping(message, user, *args, **kwargs)

    @staticmethod
    def _get_or_create_user(user_id: int) -> TelegramUser:
        obj, _ = TelegramUser.objects.get_or_create(telegram_id=user_id)
        return obj

    def _auth_by_django(self, message: Any) -> None:
        token = message.text.split()[1]
        tg_user = self._get_or_create_user(message.from_user.id)

        verify_authentication_token(token, tg_user)

        self.bot.reply_to(message, self._auth_success_msg)

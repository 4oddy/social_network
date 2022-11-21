from telebot import TeleBot

from typing import Callable, Any, Optional

from django.contrib.auth import authenticate

from ...models import TelegramUser


class TelegramAuthentication:
    _function: Optional[Callable] = None

    _not_authenticated_msg = 'Вы не авторизованы, используйте /auth [username] [password] для авторизации'
    _auth_success_msg = 'Авторизация успешна'
    _auth_failed_msg = 'Авторизация провалена'

    def __init__(self, bot: TeleBot):
        self.bot = bot
        self.auth = self.bot.message_handler(commands=['auth'])(self._auth)
        self.commands = self.bot.message_handler(commands=['start', 'help'])(self._commands)
        self.commands_list = ['/auth [username] [password] - авторизация', ]

    def basic_authentication(self, function: Callable) -> Callable:
        self._function = function
        return self._login_required

    def add_command(self, command: str) -> str:
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
            self._function(message, user, *args, **kwargs)

    @staticmethod
    def _get_or_create_user(user_id: int) -> TelegramUser:
        obj, _ = TelegramUser.objects.get_or_create(telegram_id=user_id)
        return obj

    def _auth_by_django(self, message: Any) -> None:
        username, password = message.text.split()[1:]
        user = authenticate(username=username, password=password)

        if user is not None:
            tg_user = self._get_or_create_user(message.from_user.id)
            tg_user.account = user
            tg_user.save()
            self.bot.reply_to(message, self._auth_success_msg)
        else:
            raise Exception()

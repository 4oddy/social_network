from telebot import TeleBot

from typing import Callable, Any, Optional

from django.contrib.auth import authenticate

from ...models import TelegramUser


class TelegramAuthentication:
    bot: Optional[TeleBot] = None
    _function: Optional[Callable] = None

    def __init__(self):
        self.auth = self.bot.message_handler(commands=['auth'])(self.auth)

        self._not_authenticated_msg = 'Вы не авторизованы, используйте /auth [username] [password] для авторизации'
        self._auth_success_msg = 'Авторизация успешна'
        self._auth_failed_msg = 'Авторизация провалена'

    @classmethod
    def set_bot(cls, bot: TeleBot) -> None:
        cls.bot = bot

    def basic_authentication(self, function: Callable) -> Callable:
        self._function = function
        return self.login_required

    def login_required(self, message: Any, *args, **kwargs) -> None:
        user = self._create_or_get_user(message.from_user.id)

        if not user.is_authenticated:
            self.bot.reply_to(message, self._not_authenticated_msg)
        else:
            self._function(message, user, *args, **kwargs)

    def auth(self, message: Any) -> None:
        try:
            self._auth_by_django(message)
        except Exception:
            self.bot.reply_to(message, self._auth_failed_msg)

    @staticmethod
    def _create_or_get_user(user_id: int) -> TelegramUser:
        obj, _ = TelegramUser.objects.get_or_create(telegram_id=user_id)
        return obj

    def _auth_by_django(self, message: Any) -> None:
        username, password = message.text.split()[1:]
        user = authenticate(username=username, password=password)

        if user is not None:
            tg_user = self._create_or_get_user(message.from_user.id)
            tg_user.account = user
            tg_user.save()
            self.bot.reply_to(message, self._auth_success_msg)
        else:
            raise Exception()

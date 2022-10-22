from abc import ABC, abstractmethod

from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model

from telegram.tg.bot import bot

User = get_user_model()


class AbstractSenderNotifies(ABC):
    @abstractmethod
    def send_notify(self, subject: str, body: str, to: int) -> None:
        pass


class EmailSenderNotifies(AbstractSenderNotifies):
    def send_notify(self, subject: str, body: str, to: int) -> None:
        """ Simple sending email """
        email = EmailMessage(subject=subject, body=body, to=[User.objects.get(id=to).email])
        email.send()


class TelegramSenderNotifies(AbstractSenderNotifies):
    def send_notify(self, subject: str, body: str, to: int) -> None:
        """ Sending message in Telegram """
        user = User.objects.get(id=to)
        if hasattr(user, 'telegram_profile'):
            tg_user = user.telegram_profile
            if tg_user.send_emails:
                bot.send_message(tg_user.telegram_id, f'{subject}\n{body}')


class SenderNotifiesAggregator(AbstractSenderNotifies):
    def __init__(self, senders: list[AbstractSenderNotifies]):
        self.senders = senders

    def send_notify(self, subject: str, body: str, to: int) -> None:
        for sender in self.senders:
            sender.send_notify(subject, body, to)

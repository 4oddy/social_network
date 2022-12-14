from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class TelegramUser(models.Model):
    telegram_id = models.IntegerField(verbose_name='ID', null=False)
    account = models.OneToOneField(User, verbose_name='Аккаунт', null=True, related_name='telegram_profile',
                                   on_delete=models.CASCADE)
    send_emails = models.BooleanField(verbose_name='Отправлять сообщения', default=True)

    class Meta:
        verbose_name = 'Telegram пользователь'
        verbose_name_plural = 'Telegram пользователи'

    def switch_sending_emails(self):
        self.send_emails = True if not self.send_emails else False
        self.save()
        return self.send_emails

    @property
    def is_authenticated(self):
        if self.account is not None:
            return True
        return False

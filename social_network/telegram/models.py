from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()


class TelegramUser(models.Model):
    telegram_id = models.IntegerField(verbose_name='ID', null=False)
    account = models.ForeignKey(User, verbose_name='Аккаунт', null=True, related_name='telegram_profile',
                                on_delete=models.CASCADE)
    send_emails = models.BooleanField(verbose_name='Отправлять сообщения', default=True)

    class Meta:
        verbose_name = 'Telegram пользователь'
        verbose_name_plural = 'Telegram пользователи'

    @property
    def is_authenticated(self):
        if self.account is not None:
            return True
        return False

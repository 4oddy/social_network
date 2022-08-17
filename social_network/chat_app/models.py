from django.db import models

from django.contrib.auth import get_user_model


User = get_user_model()


class Message(models.Model):
    text = models.CharField(verbose_name='Текст сообщения', max_length=150)
    sender = models.ForeignKey(User, verbose_name='Отправитель', null=True, on_delete=models.SET_NULL,
                               related_name='sent_messages')
    receiver = models.ForeignKey(User, verbose_name='Получатель', null=True, on_delete=models.SET_NULL,
                                 related_name='received_messages')

    date_of_sending = models.DateTimeField(auto_now_add=True)
    date_of_updating = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

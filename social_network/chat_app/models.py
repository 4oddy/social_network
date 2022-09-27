from django.db import models

from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.http import HttpRequest

import uuid

User = get_user_model()

exposed_request: HttpRequest = HttpRequest()


class AbstractDialog(models.Model):
    name = models.CharField(verbose_name='Имя', max_length=50)
    owner = models.ForeignKey(User, verbose_name='Создатель', null=True, on_delete=models.SET_NULL)
    date_of_creating = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    uid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class AbstractMessage(models.Model):
    text = models.TextField(verbose_name='Текст сообщения')
    sender = models.ForeignKey(User, verbose_name='Отправитель', null=True, on_delete=models.SET_NULL)
    group = models.ForeignKey(AbstractDialog, null=True, on_delete=models.SET_NULL)
    date_of_sending = models.DateTimeField(verbose_name='Дата отправки', auto_now_add=True)

    class Meta:
        abstract = True


class Conservation(AbstractDialog):
    members = models.ManyToManyField(User, verbose_name='Участники', related_name='conservations')

    class Meta:
        verbose_name = 'Беседа'
        verbose_name_plural = 'Беседы'

    def get_absolute_url(self):
        return reverse('chat:conservation_page', kwargs={'group_name': self.name})


class Dialog(AbstractDialog):
    owner = models.ForeignKey(User, verbose_name='Первый пользователь', null=True, on_delete=models.SET_NULL,
                              related_name='dialogs_first_user')
    second_user = models.ForeignKey(User, verbose_name='Второй пользователь', null=True, on_delete=models.SET_NULL,
                                    related_name='dialogs_second_user')

    class Meta:
        verbose_name = 'Диалог'
        verbose_name_plural = 'Диалоги'

    def __str__(self):
        return f'{self.owner} - {self.second_user}'

    def get_companion(self, user: User = None) -> User:
        """ This method gets your companion
            Takes 1 positional argument: user
            If user is defined, it will return second user of dialog
            If user is none, it will return second user of dialog by request_exposer middleware
             (core.middleware.request_exposer)
        """
        if user:
            return self.owner if self.owner != user else self.second_user
        return self.owner if self.owner != exposed_request.user else self.second_user

    def get_absolute_url(self):
        return reverse('chat:dialog_page', kwargs={'companion_name': self.get_companion().username})


class ConservationMessage(AbstractMessage):
    group = models.ForeignKey(Conservation, verbose_name='Беседа', on_delete=models.CASCADE,
                              default=None, related_name='messages')

    class Meta:
        verbose_name = 'Сообщение беседы'
        verbose_name_plural = 'Сообщения беседы'


class DialogMessage(AbstractMessage):
    group = models.ForeignKey(Dialog, verbose_name='Диалог', on_delete=models.CASCADE,
                              default=None, related_name='messages')

    class Meta:
        verbose_name = 'Сообщение диалога'
        verbose_name_plural = 'Сообщения диалога'

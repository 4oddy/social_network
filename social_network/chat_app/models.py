from django.db import models

from django.contrib.auth import get_user_model
from django.shortcuts import reverse

import uuid

User = get_user_model()


class AbstractDialog(models.Model):
    name = models.CharField(verbose_name='Имя', max_length=50)
    owner = models.ForeignKey(User, verbose_name='Создатель', null=True, on_delete=models.SET_NULL)
    date_of_creating = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)
    uid = models.CharField(max_length=23, unique=True, default=None)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.uid = self._create_uuid()

        return super(AbstractDialog, self).save()

    def _create_uuid(self):
        uid = str(uuid.uuid4())[:23]

        while Dialog.objects.filter(uid=uid).exists():
            uid = str(uuid.uuid4())[:23]

        return uid


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

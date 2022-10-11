from django.db import models

from django.conf import settings
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import EmailValidator
from django.shortcuts import reverse

from .validators import custom_username_validator
from .exceptions import SelfRequestedException

import uuid


class CustomUser(AbstractUser):
    class Devices(models.TextChoices):
        PC = 'pc', 'Computer'
        MOBILE = 'mobile', 'Mobile'

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=50,
        unique=True,
        validators=[username_validator, custom_username_validator],
        error_messages={
            "unique": "Такое имя пользователя занято.",
        },
    )

    email = models.EmailField(unique=True, validators=[EmailValidator])
    image = models.ImageField(verbose_name='Фотография профиля',
                              upload_to='images/user_images', default=settings.DEFAULT_USER_IMAGE)
    last_online = models.DateTimeField(verbose_name='Последний онлайн',
                                       auto_now=True, blank=True, null=True)
    device = models.CharField(verbose_name='Устройство', max_length=6, choices=Devices.choices, default=Devices.PC)
    friends = models.ManyToManyField('self')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def get_absolute_url(self):
        return reverse('main:user_page', kwargs={'username': self.username})

    @property
    def is_online(self):
        if self.last_online:
            return (timezone.now() - self.last_online) < timezone.timedelta(minutes=2)
        return False

    @property
    def is_mobile(self):
        if self.device == self.Devices.MOBILE:
            return True
        return False

    def clean(self):
        if len(self.first_name) > 50:
            raise ValidationError({'first_name': 'Максимальная длина: 50'})

        if len(self.last_name) > 50:
            raise ValidationError({'last_name': 'Максимальная длина: 50'})

    @staticmethod
    def make_friends(first_user, second_user):
        if first_user not in second_user.friends.all() and second_user not in first_user.friends.all():
            first_user.friends.add(second_user)
            second_user.friends.add(first_user)

    @staticmethod
    def delete_friends(first_user, second_user):
        if first_user in second_user.friends.all() and second_user in first_user.friends.all():
            first_user.friends.remove(second_user)
            second_user.friends.remove(first_user)


class FriendRequest(models.Model):
    class RequestStatuses(models.TextChoices):
        CREATED = 'c', 'CREATED'
        ACCEPTED = 'a', 'ACCEPTED'
        DENIED = 'd', 'DENIED'

    from_user = models.ForeignKey(CustomUser, null=False, verbose_name='От кого',
                                  related_name='from_user_request', on_delete=models.CASCADE)
    to_user = models.ForeignKey(CustomUser, null=False, verbose_name='Кому',
                                related_name='to_user_request', on_delete=models.CASCADE)
    request_status = models.CharField(verbose_name='Статус заявки', max_length=1, choices=RequestStatuses.choices,
                                      default=RequestStatuses.CREATED)
    date_of_request = models.DateTimeField(verbose_name='Дата заявки', auto_now_add=True)

    class Meta:
        verbose_name = 'Заявка в друзья'
        verbose_name_plural = 'Заявки в друзья'

    def accept(self):
        if self.request_status != 'a':
            first_user, second_user = self.from_user, self.to_user

            CustomUser.make_friends(first_user, second_user)

            self.request_status = 'a'
            self.save()

    def deny(self):
        self.request_status = 'd' if self.request_status != 'd' else self.request_status
        self.save()

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if self.from_user == self.to_user:
            raise SelfRequestedException('Пользователь не может отправить заявку в друзья самому себе')
        return super(FriendRequest, self).save()


class Post(models.Model):
    title = models.CharField(verbose_name='Заголовок', max_length=50, null=True, blank=True)
    description = models.TextField(verbose_name='Текст', null=True, blank=True)
    owner = models.ForeignKey(CustomUser, verbose_name='Автор',
                              null=False, blank=False, on_delete=models.CASCADE, related_name='posts')
    post_uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    date_of_creating = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    date_of_update = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'

    def clean(self):
        if not self.title and not self.description:
            raise ValidationError('Пост не может быть пустым')

        if len(str(self.title)) > 50:
            raise ValidationError({'title': 'Максимальная длина: 50'})

    def get_absolute_url(self):
        return reverse('main:post_page', kwargs={'post_uuid': self.post_uuid})


class Comment(models.Model):
    owner = models.ForeignKey(CustomUser, verbose_name='Владелец', related_name='comments', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, verbose_name='Пост', related_name='post_comments', on_delete=models.CASCADE)
    text = models.CharField(verbose_name='Текст', max_length=200)
    uid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def clean(self):
        if len(self.text) > 200:
            raise ValidationError({'text': 'Максимальная длина: 200'})

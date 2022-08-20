from django.db import models

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
                              upload_to='images/user_images', default='images/user_images/empty_staff.png')
    last_online = models.DateTimeField(verbose_name='Последний онлайн',
                                       auto_now=True, blank=True, null=True)
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

    def clean(self):
        if len(self.first_name) > 50:
            raise ValidationError({'first_name': 'Максимальная длина: 50'})

        if len(self.last_name) > 50:
            raise ValidationError({'last_name': 'Максимальная длина: 50'})


class FriendRequest(models.Model):
    request_statuses = (
        ('c', 'CREATED'),
        ('a', 'ACCEPTED'),
        ('d', 'DENIED')
    )

    from_user = models.ForeignKey(CustomUser, verbose_name='От кого',
                                  related_name='from_user_request', on_delete=models.CASCADE)
    to_user = models.ForeignKey(CustomUser, verbose_name='Кому',
                                related_name='to_user_request', on_delete=models.CASCADE)
    request_status = models.CharField(verbose_name='Статус заявки', max_length=1, choices=request_statuses, default='c')
    date_of_request = models.DateTimeField(verbose_name='Дата заявки', auto_now_add=True)

    class Meta:
        verbose_name = 'Заявка в друзья'
        verbose_name_plural = 'Заявки в друзья'

    def accept(self):
        if self.request_status != 'a':
            first_user, second_user = self.from_user, self.to_user

            first_user.friends.add(second_user)
            second_user.friends.add(first_user)

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
    description = models.CharField(verbose_name='Текст', max_length=150, null=True, blank=True)
    owner = models.ForeignKey(CustomUser, verbose_name='Автор',
                              null=False, blank=False, on_delete=models.CASCADE, related_name='posts')
    post_uuid = models.CharField(max_length=23, unique=True, default=None)
    date_of_creating = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    date_of_update = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.post_uuid = self._create_uuid()

        return super(Post, self).save()

    def clean(self):
        if not self.title and not self.description:
            raise ValidationError('Пост не может быть пустым')

        if len(str(self.title)) > 50:
            raise ValidationError('Максимальная длина: 50')

        if len(str(self.description)) > 150:
            raise ValidationError('Максимальная длина: 150')

    def get_absolute_url(self):
        return reverse('main:post_page', kwargs={'post_uuid': self.post_uuid})

    def _create_uuid(self):
        post_uuid = str(uuid.uuid4())[:23]

        while Post.objects.filter(post_uuid=post_uuid).exists():
            post_uuid = str(uuid.uuid4())[:23]

        return post_uuid

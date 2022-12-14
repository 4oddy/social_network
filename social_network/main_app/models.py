import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.db import models
from django.shortcuts import reverse
from django.utils import timezone

from .managers import PostManager
from .validators import custom_username_validator


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
    image = models.ImageField(verbose_name='Фотография профиля', upload_to='images/user_images',
                              default=settings.DEFAULT_USER_IMAGE)
    last_online = models.DateTimeField(verbose_name='Последний онлайн', auto_now=True)
    device = models.CharField(verbose_name='Устройство', max_length=6, choices=Devices.choices, default=Devices.PC)
    friends = models.ManyToManyField('self')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def clean(self):
        if len(self.first_name) > 50:
            raise ValidationError({'first_name': 'Максимальная длина: 50'})

        if len(self.last_name) > 50:
            raise ValidationError({'last_name': 'Максимальная длина: 50'})

    def get_absolute_url(self):
        return reverse('main:user_page', kwargs={'username': self.username})

    def get_name(self):
        return self.first_name if self.first_name else self.username

    @property
    def is_online(self):
        if self.last_online:
            return (timezone.now() - self.last_online) < timezone.timedelta(minutes=2)  # online lasts for 2 minutes
        return False

    @property
    def is_mobile(self):
        if self.device == self.Devices.MOBILE:
            return True
        return False

    @staticmethod
    def in_friendship(first, second):
        return first in second.friends.all() and second in first.friends.all()

    @classmethod
    def make_friends(cls, first_user, second_user):
        if not cls.in_friendship(first_user, second_user):
            first_user.friends.add(second_user)
            second_user.friends.add(first_user)

    @classmethod
    def delete_friends(cls, first_user, second_user):
        if cls.in_friendship(first_user, second_user):
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
    request_status = models.CharField(verbose_name='Статус заявки', max_length=1,
                                      choices=RequestStatuses.choices, default=RequestStatuses.CREATED)
    date_of_request = models.DateTimeField(verbose_name='Дата заявки', auto_now_add=True)

    class Meta:
        verbose_name = 'Заявка в друзья'
        verbose_name_plural = 'Заявки в друзья'

        constraints = [
            models.CheckConstraint(
                check=~models.Q(from_user=models.F('to_user')),
                name='check_self_request'
            ),  # prohibits creating of request to yourself
            models.UniqueConstraint(
                fields=('from_user', 'to_user'),
                name='unique_request'
            )  # prohibits creating of existing request
        ]

    def clean(self):
        super().clean()

        if self.from_user == self.to_user:
            raise ValidationError('Отправитель заявки не может быть её получателем')

        if self.find_friend_request(self.from_user, self.to_user):
            raise ValidationError('Такая заявка уже существует')

    def accept(self):
        """ Accepts friend request and makes friends """
        if self.request_status != self.RequestStatuses.ACCEPTED:
            first_user, second_user = self.from_user, self.to_user

            CustomUser.make_friends(first_user, second_user)

            self.request_status = self.RequestStatuses.ACCEPTED
            self.save()

    def deny(self):
        """ Denies friend request """
        if self.request_status != self.RequestStatuses.DENIED and self.request_status != self.RequestStatuses.ACCEPTED:
            self.request_status = self.RequestStatuses.DENIED
            self.save()

    @staticmethod
    def find_friend_request(first_user, second_user):
        """ Find friend request related to first_user and second_user """
        request = FriendRequest.objects.filter(models.Q(from_user=first_user) & models.Q(to_user=second_user) |
                                               models.Q(from_user=second_user) & models.Q(to_user=first_user)).first()
        return request

    @property
    def is_accepted(self):
        return self.request_status == self.RequestStatuses.ACCEPTED

    @property
    def is_denied(self):
        return self.request_status == self.RequestStatuses.DENIED


class Post(models.Model):
    title = models.CharField(verbose_name='Заголовок', max_length=50, null=True, blank=True)
    description = models.TextField(verbose_name='Текст', null=True, blank=True)
    owner = models.ForeignKey(CustomUser, verbose_name='Автор', null=False, blank=False,
                              on_delete=models.CASCADE, related_name='posts')
    post_uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    date_of_creating = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    date_of_update = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    objects = PostManager()

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        ordering = ['-date_of_creating']

    def get_absolute_url(self):
        return reverse('main:post_page', kwargs={'post_uuid': self.post_uuid})

    def clean(self):
        if not self.title and not self.description:
            raise ValidationError('Пост не может быть пустым')


class Comment(models.Model):
    owner = models.ForeignKey(CustomUser, verbose_name='Владелец', related_name='comments', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, verbose_name='Пост', related_name='post_comments', on_delete=models.CASCADE)
    text = models.CharField(verbose_name='Текст', max_length=200)
    uid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

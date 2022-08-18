from django.test import TestCase
from django.shortcuts import reverse
from django.contrib.auth import get_user_model

from datetime import datetime

from .models import FriendRequest
from .services import create_friend_request

User = get_user_model()


class TestUser(TestCase):
    def setUp(self) -> None:
        self.username = f'test{datetime.now().strftime("%d%m%Y%H%M%S")}'
        self.password = self.username
        self.email = self.username + '@mail.ru'

        self.user = User.objects.create_user(username=self.username, email=self.email,
                                             password=self.password)

        for i in range(5):
            self.username = f'test{datetime.now().strftime("%d%m%Y%H%M%S") + str(i)}'
            self.password = self.username
            self.email = self.username + '@mail.ru'

            User.objects.create_user(username=self.username, email=self.email, password=self.password)

        self.users_queryset = User.objects.all()

    def test_login_by_username(self):
        self.client.login(username=self.username, password=self.username)

        for user in self.users_queryset:
            response = self.client.get(reverse('main:user_page', kwargs={'username': user.username}))
            self.assertEqual(response.status_code, 200)

    def test_login_by_email(self):
        self.client.login(username=self.email, password=self.password)

        for user in self.users_queryset:
            response = self.client.get(reverse('main:user_page', kwargs={'username': user.username}))
            self.assertEqual(response.status_code, 200)

    def test_friend_request(self):
        for user in self.users_queryset:
            if user != self.user:
                request = FriendRequest.objects.create(from_user=self.user, to_user=user)
                self.assertEqual(request.request_status, 'c')

    def test_custom_friend_request(self):
        for user in self.users_queryset:
            if user != self.user:
                request = create_friend_request(from_user=self.user, to_user_id=user.pk)
                self.assertEqual(request.request_status, 'c')

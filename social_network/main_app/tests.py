from django.test import TestCase
from django.shortcuts import reverse
from django.contrib.auth import get_user_model

from datetime import datetime

from .models import FriendRequest, Post
from .services import create_friend_request, delete_from_friendship, find_friend_request, in_friendship

User = get_user_model()


class TestUser(TestCase):
    def setUp(self):
        # creating main user
        self.username = f'test{datetime.now().strftime("%d%m%Y%H%M%S")}'
        self.password = self.username
        self.email = self.username + '@mail.ru'

        self.user = User.objects.create_user(username=self.username, email=self.email,
                                             password=self.password)

        # creating 5 random users
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
                # test if request created
                request = FriendRequest.objects.create(from_user=self.user, to_user=user)
                self.assertEqual(request.request_status, 'c')

                # test if request accepted
                request.accept()
                self.assertEqual(request.request_status, 'a')

                # test if in friendship
                self.assertTrue(in_friendship(self.user, user))

                # test deletion from friendship
                delete_from_friendship(self.user, user)
                self.assertFalse(find_friend_request(first_user=self.user, second_user=user))
                self.assertFalse(in_friendship(self.user, user))

    def test_custom_friend_request_first(self):
        for user in self.users_queryset:
            if user != self.user:
                request = create_friend_request(from_user=self.user, to_user_id=user.pk)
                self.assertEqual(request.request_status, 'c')

                request.accept()
                self.assertEqual(request.request_status, 'a')

                self.assertTrue(in_friendship(self.user, user))

                delete_from_friendship(self.user, user)
                self.assertFalse(find_friend_request(first_user=self.user, second_user_id=user.pk))
                self.assertFalse(in_friendship(self.user, user))

    def test_custom_friend_request_second(self):
        for user in self.users_queryset:
            if user != self.user:
                request = create_friend_request(from_user=self.user, to_user=user)
                self.assertEqual(request.request_status, 'c')

                request.accept()
                self.assertEqual(request.request_status, 'a')

                self.assertTrue(in_friendship(self.user, user))

                delete_from_friendship(self.user, user)
                self.assertFalse(find_friend_request(first_user=self.user, second_user=user))
                self.assertFalse(in_friendship(self.user, user))

    def test_custom_friend_request_third(self):
        for user in self.users_queryset:
            if user != self.user:
                request = create_friend_request(from_user_id=self.user.pk, to_user=user)
                self.assertEqual(request.request_status, 'c')

                request.accept()
                self.assertEqual(request.request_status, 'a')

                self.assertTrue(in_friendship(self.user, user))

                delete_from_friendship(self.user, user)
                self.assertFalse(find_friend_request(first_user_id=self.user.pk, second_user=user))
                self.assertFalse(in_friendship(self.user, user))

    def test_custom_friend_request_fourth(self):
        for user in self.users_queryset:
            if user != self.user:
                request = create_friend_request(from_user_id=self.user.pk, to_user_id=user.pk)
                self.assertEqual(request.request_status, 'c')

                request.accept()
                self.assertEqual(request.request_status, 'a')

                self.assertTrue(in_friendship(self.user, user))

                delete_from_friendship(self.user, user)
                self.assertFalse(find_friend_request(first_user_id=self.user.pk, second_user_id=user.pk))
                self.assertFalse(in_friendship(self.user, user))


class TestPost(TestCase):
    def setUp(self):
        # creating main user
        self.username = f'test{datetime.now().strftime("%d%m%Y%H%M%S")}'
        self.password = self.username
        self.email = self.username + '@mail.ru'

        self.user = User.objects.create_user(username=self.username, email=self.email,
                                             password=self.password)

    def create_post(self, data):
        response = self.client.post(reverse('main:create_post'), data=data)
        return response

    def test_creating_positive(self):
        self.client.login(username=self.username, password=self.password)
        self.create_post(data={'title': 'test_post', 'description': 'test'})
        self.assertTrue(Post.objects.filter(owner=self.user, title='test_post').exists())

    def test_creating_negative(self):
        self.client.login(username=self.username, password=self.password)
        self.create_post({'title': '', 'description': ''})
        self.assertFalse(Post.objects.filter(owner=self.user).exists())

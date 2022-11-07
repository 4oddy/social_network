from django.test import TestCase
from django.shortcuts import reverse
from django.contrib.auth import get_user_model

from core.utils import generate_user_data

from .models import FriendRequest, Post
from .services import create_friend_request, delete_from_friendship

User = get_user_model()


class TestUser(TestCase):
    def setUp(self):
        # creating main user
        self.user = User.objects.create_user(**generate_user_data())

        # creating second user
        self.second_user = User.objects.create_user(**generate_user_data())

    def test_login_by_username(self):
        self.client.login(username=self.user.username, password=self.user.username)
        response = self.client.get(reverse('main:user_page', kwargs={'username': self.user.username}))
        self.assertEqual(response.status_code, 200)

    def test_login_by_email(self):
        self.client.login(username=self.user.email, password=self.user.username)
        response = self.client.get(reverse('main:user_page', kwargs={'username': self.user.username}))
        self.assertEqual(response.status_code, 200)

    def test_friend_request(self):
        # test if request created
        request = FriendRequest.objects.create(from_user=self.user, to_user=self.second_user)
        self.assertEqual(request.request_status, request.RequestStatuses.CREATED)

        # test if request denied
        request.deny()
        self.assertEqual(request.request_status, request.RequestStatuses.DENIED)

        # test if request accepted
        request.accept()
        self.assertEqual(request.request_status, request.RequestStatuses.ACCEPTED)

        # test if in friendship
        self.assertTrue(User.in_friendship(self.user, self.second_user))

        # test deletion from friendship
        delete_from_friendship(self.user, self.second_user)
        self.assertFalse(FriendRequest.find_friend_request(first_user=self.user, second_user=self.second_user))
        self.assertFalse(User.in_friendship(self.user, self.second_user))

    def test_custom_friend_request(self):
        request = create_friend_request(from_user=self.user, to_user_id=self.second_user.pk)
        self.assertEqual(request.request_status, request.RequestStatuses.CREATED)

        request.deny()
        self.assertEqual(request.request_status, request.RequestStatuses.DENIED)

        request.accept()
        self.assertEqual(request.request_status, request.RequestStatuses.ACCEPTED)

        self.assertTrue(User.in_friendship(self.user, self.second_user))

        delete_from_friendship(self.user, self.second_user)
        self.assertFalse(FriendRequest.find_friend_request(first_user=self.user, second_user=self.second_user))
        self.assertFalse(User.in_friendship(self.user, self.second_user))

    def test_negative_self_friend_request(self):
        try:
            create_friend_request(from_user=self.user, to_user_id=self.user.id)
        except Exception:
            pass
        else:
            self.fail('Test Failed! Request has been created')

    def test_negative_existing_friend_request(self):
        create_friend_request(from_user=self.user, to_user_id=self.second_user.pk)

        try:
            create_friend_request(from_user=self.user, to_user_id=self.second_user.pk)
        except Exception:
            pass
        else:
            self.fail('Test Failed! Request has been created')

        try:
            create_friend_request(from_user=self.second_user, to_user_id=self.user.pk)
        except Exception:
            pass
        else:
            self.fail('Test Failed! Request has been created')


class TestPost(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(**generate_user_data())

        self._create_post_url = reverse('main:create_post')

    def create_post(self, data):
        response = self.client.post(self._create_post_url, data=data)
        return response

    def test_creating_positive(self):
        self.client.login(username=self.user.username, password=self.user.username)
        self.create_post(data={'title': 'test_post', 'description': 'test'})
        self.assertTrue(Post.objects.filter(owner=self.user, title='test_post').exists())

    def test_creating_negative(self):
        self.client.login(username=self.user.username, password=self.user.username)
        self.create_post({'title': '', 'description': ''})
        self.assertFalse(Post.objects.filter(owner=self.user).exists())

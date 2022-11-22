from django.shortcuts import reverse

from .base import BaseTestUser, User

from ..models import FriendRequest
from ..services import delete_from_friendship


class TestUser(BaseTestUser):
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

    def test_negative_self_friend_request(self):
        with self.assertRaises(Exception):
            FriendRequest.objects.create(from_user=self.user, to_user=self.user)

    def test_negative_existing_friend_request(self):
        FriendRequest.objects.create(from_user=self.user, to_user=self.second_user)

        with self.assertRaises(Exception):
            FriendRequest.objects.create(from_user=self.user, to_user=self.second_user)

        with self.assertRaises(Exception):
            FriendRequest.objects.create(from_user=self.second_user, to_user=self.user)

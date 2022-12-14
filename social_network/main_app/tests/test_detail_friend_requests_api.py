from django.contrib.auth import get_user_model

from core.tests.common import assertions, reverse, status

from ..models import FriendRequest
from .base import BaseTestFriendRequest

User = get_user_model()


class TestDetailFriendRequestAPI(BaseTestFriendRequest,
                                 assertions.StatusCodeAssertionsMixin,
                                 assertions.InstanceAssertionsMixin):
    @staticmethod
    def build_url(pk):
        return reverse('main:requests-detail', args=[pk])

    @staticmethod
    def build_accept_url(pk):
        return reverse('main:requests-accept', args=[pk])

    @staticmethod
    def build_deny_url(pk):
        return reverse('main:requests-deny', args=[pk])

    def test_detail_unauthorized(self):
        request = self.create_request(from_user=self.user, to_user=self.second_user)

        response = self.client.get(self.build_url(request.pk))
        self.assert_status_equal(response, status.HTTP_401_UNAUTHORIZED)

    def test_detail_authorized(self):
        request = self.create_request(from_user=self.user, to_user=self.second_user)

        response = self.client_auth.get(self.build_url(request.pk))
        self.assert_status_equal(response, status.HTTP_200_OK)

    def test_detail_user_cannot_view_other_requests(self):
        request = self.create_request(from_user=self.third_user, to_user=self.second_user)

        response = self.client_auth.get(self.build_url(request.pk))
        self.assert_status_equal(response, status.HTTP_404_NOT_FOUND)

    def test_destroy_friend_request(self):
        request = self.create_request(from_user=self.user, to_user=self.second_user)

        response = self.client_auth.delete(self.build_url(request.pk))
        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        self.assert_instance_does_not_exist(FriendRequest, from_user=self.user, to_user=self.second_user)

    def test_user_cannot_destroy_incoming_request(self):
        request = self.create_request(from_user=self.second_user, to_user=self.user)

        response = self.client_auth.delete(self.build_url(request.pk))
        self.assert_status_equal(response, status.HTTP_403_FORBIDDEN)

    def test_accept_friend_request(self):
        request = self.create_request(from_user=self.second_user, to_user=self.user)

        response = self.client_auth.get(self.build_accept_url(request.pk))
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertTrue(User.in_friendship(self.user, self.second_user))

        response = self.client_auth.get(self.build_accept_url(request.pk))
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    def test_sender_cannot_accept_request(self):
        request = self.create_request(from_user=self.user, to_user=self.second_user)

        response = self.client_auth.get(self.build_accept_url(request.pk))
        self.assert_status_equal(response, status.HTTP_403_FORBIDDEN)

    def test_destroy_request_after_accepting(self):
        request = self.create_request(from_user=self.second_user, to_user=self.user)

        response = self.client_auth.get(self.build_accept_url(request.pk))
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertTrue(User.in_friendship(self.user, self.second_user))

        response = self.client_auth.delete(self.build_url(request.pk))
        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        self.assert_instance_does_not_exist(FriendRequest, from_user=self.second_user, to_user=self.user)
        self.assertFalse(User.in_friendship(self.user, self.second_user))

    def test_deny_friend_request(self):
        request = self.create_request(from_user=self.second_user, to_user=self.user)

        response = self.client_auth.get(self.build_deny_url(request.pk))
        self.assert_status_equal(response, status.HTTP_200_OK)

        response = self.client_auth.get(self.build_deny_url(request.pk))
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    def test_sender_cannot_deny_request(self):
        request = self.create_request(from_user=self.user, to_user=self.second_user)

        response = self.client_auth.get(self.build_deny_url(request.pk))
        self.assert_status_equal(response, status.HTTP_403_FORBIDDEN)

from core.tests.common import assertions, reverse, status

from ..models import FriendRequest
from .base import BaseTestFriendRequest


class CreateFriendRequestTestAPI(BaseTestFriendRequest,
                                 assertions.StatusCodeAssertionsMixin,
                                 assertions.InstanceAssertionsMixin):
    def setUp(self):
        super(CreateFriendRequestTestAPI, self).setUp()
        self.base_url = reverse('main:requests-list')

    def test_create_request_unauthorized(self):
        response = self.client.post(self.base_url, data={'to_user': self.user.pk})
        self.assert_status_equal(response, status.HTTP_401_UNAUTHORIZED)

    def test_create_request_authorized(self):
        response = self.client_auth.post(self.base_url, data={'to_user': self.second_user.pk})
        self.assert_status_equal(response, status.HTTP_201_CREATED)
        self.assert_instance_exists(FriendRequest, from_user=self.user, to_user=self.second_user)

    def test_create_request_user_not_exists(self):
        response = self.client_auth.post(self.base_url, data={'to_user': 99})
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    def test_create_existing_request(self):
        self.create_request(from_user=self.user, to_user=self.second_user)

        response = self.client_auth.post(self.base_url, data={'to_user': self.second_user.pk})
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    def test_create_self_request(self):
        response = self.client_auth.post(self.base_url, data={'to_user': self.user.pk})
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assert_instance_does_not_exist(FriendRequest, from_user=self.user, to_user=self.user)

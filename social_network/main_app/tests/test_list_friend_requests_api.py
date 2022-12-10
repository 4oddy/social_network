from .common import reverse, assertions, status

from .base import BaseTestFriendRequest


class TestListFriendRequestAPI(BaseTestFriendRequest, assertions.StatusCodeAssertionsMixin):
    def setUp(self):
        super(TestListFriendRequestAPI, self).setUp()
        self.base_url = reverse('main:requests-list')

    def test_list_unauthorized(self):
        response = self.client.get(self.base_url)
        self.assert_status_equal(response, status.HTTP_401_UNAUTHORIZED)

    def test_list_authorized_no_requests(self):
        response = self.client_auth.get(self.base_url)
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_list_authorized_one_request(self):
        self.create_request(from_user=self.user, to_user=self.second_user)

        response = self.client_auth.get(self.base_url)
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_user_cannot_view_other_requests(self):
        self.create_request(from_user=self.second_user, to_user=self.third_user)

        response = self.client_auth.get(self.base_url)
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

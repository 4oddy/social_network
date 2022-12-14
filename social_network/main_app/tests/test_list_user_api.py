from core.tests.common import assertions, reverse, status

from .base import BaseTestUser


class TestListUserAPI(BaseTestUser, assertions.StatusCodeAssertionsMixin):
    def setUp(self):
        super(TestListUserAPI, self).setUp()
        self.base_url = reverse('main:users-list')

    def test_users_list_unauthorized(self):
        response = self.client.get(self.base_url)
        self.assert_status_equal(response, status.HTTP_401_UNAUTHORIZED)

    def test_users_list_authorized(self):
        response = self.client_auth.get(self.base_url)
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

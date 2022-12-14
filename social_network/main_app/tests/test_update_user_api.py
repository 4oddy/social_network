from core.tests.common import assertions, reverse, status

from .base import BaseTestUser


class TestUpdateUserAPI(BaseTestUser, assertions.StatusCodeAssertionsMixin):
    def setUp(self):
        super(TestUpdateUserAPI, self).setUp()
        self.base_url = reverse('main:users-update_user')
        self.data = {'first_name': 'Pablo', 'last_name': 'Escobar'}

    def test_update_unauthorized(self):
        response = self.client.put(self.base_url)
        self.assert_status_equal(response, status.HTTP_401_UNAUTHORIZED)

    def test_update_authorized_put(self):
        response = self.client_auth.put(self.base_url, data=self.data)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(self.user.first_name, self.data['first_name'])
        self.assertEqual(self.user.last_name, self.data['last_name'])

    def test_update_authorized_patch(self):
        response = self.client_auth.patch(self.base_url, data=self.data)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(self.user.first_name, self.data['first_name'])
        self.assertEqual(self.user.last_name, self.data['last_name'])

from .base import BaseTestDialogs

from core.tests.common import status, reverse, assertions


class TestListDialogsAPI(BaseTestDialogs, assertions.StatusCodeAssertionsMixin):
    def setUp(self):
        super().setUp()
        self.base_url = reverse('chat:dialogs-list')

    def test_list_unauthorized(self):
        response = self.client.get(self.base_url)
        self.assert_status_equal(response, status.HTTP_401_UNAUTHORIZED)

    def test_list_authorized(self):
        response = self.client_auth.get(self.base_url)
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)

    def test_list_one_dialog(self):
        self.create_group(owner=self.user, second_user=self.second_user)

        response = self.client_auth.get(self.base_url)
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_list_user_cannot_view_other_dialogs(self):
        self.create_group(owner=self.second_user, second_user=self.third_user)

        response = self.client_auth.get(self.base_url)
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)

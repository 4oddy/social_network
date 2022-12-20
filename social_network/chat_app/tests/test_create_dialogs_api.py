from core.tests.common import assertions, reverse, status

from ..models import Dialog
from .base import BaseTestDialogs


class TestCreateDialogsAPI(BaseTestDialogs,
                           assertions.StatusCodeAssertionsMixin,
                           assertions.InstanceAssertionsMixin):
    def setUp(self):
        super().setUp()
        self.base_url = reverse('chat:dialogs-list')

    def test_create_dialog_unauthorized(self):
        response = self.client.post(self.base_url, data={'second_user_id': self.user.pk})
        self.assert_status_equal(response, status.HTTP_401_UNAUTHORIZED)

    def test_create_self_dialog(self):
        response = self.client_auth.post(self.base_url, data={'second_user_id': self.user.pk})
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assert_instance_does_not_exist(Dialog, owner=self.user, second_user=self.user)

    def test_create_existing_dialog(self):
        self.user.make_friends(self.user, self.second_user)

        self.create_group(owner=self.user, second_user=self.second_user)

        response = self.client_auth.post(self.base_url, data={'second_user_id': self.second_user.pk})
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    def test_create_user_does_not_exist(self):
        response = self.client_auth.post(self.base_url, data={'second_user_id': 99})
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assert_instance_does_not_exist(Dialog, owner=self.user, second_user=99)

    def test_create_dialog_not_in_friends(self):
        response = self.client_auth.post(self.base_url, data={'second_user_id': self.second_user.pk})
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assert_instance_does_not_exist(Dialog, owner=self.user, second_user=self.second_user)

    def test_create_dialog_authorized(self):
        self.user.make_friends(self.user, self.second_user)

        response = self.client_auth.post(self.base_url, data={'second_user_id': self.second_user.pk})
        self.assert_status_equal(response, status.HTTP_201_CREATED)
        self.assert_instance_exists(Dialog, owner=self.user, second_user=self.second_user)

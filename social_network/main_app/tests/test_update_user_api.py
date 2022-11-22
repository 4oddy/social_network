from django.shortcuts import reverse

from rest_framework import status

from djet.assertions import StatusCodeAssertionsMixin

from .base import BaseTestUser


class TestUpdateUserAPI(BaseTestUser, StatusCodeAssertionsMixin):
    def setUp(self):
        super(TestUpdateUserAPI, self).setUp()
        self.base_url = reverse('main:users-update_user')

        self.first_name = 'Pablo'
        self.last_name = 'Escobar'

    def test_update_unauthorized(self):
        response = self.client.put(self.base_url)
        self.assert_status_equal(response, status.HTTP_401_UNAUTHORIZED)

    def test_update_authorized_put(self):
        data = {'first_name': self.first_name, 'last_name': self.last_name}

        response = self.client_auth.put(self.base_url, data=data)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(self.user.first_name, self.first_name)
        self.assertEqual(self.user.last_name, self.last_name)

    def test_update_authorized_patch(self):
        data = {'first_name': self.first_name, 'last_name': self.last_name}

        response = self.client_auth.patch(self.base_url, data=data)

        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(self.user.first_name, self.first_name)
        self.assertEqual(self.user.last_name, self.last_name)

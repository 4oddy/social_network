from django.shortcuts import reverse

from rest_framework import status

from djet.assertions import StatusCodeAssertionsMixin

from .base import BaseTestUser


class TestUpdateUserAPI(BaseTestUser, StatusCodeAssertionsMixin):
    def setUp(self):
        super(TestUpdateUserAPI, self).setUp()
        self.base_url = reverse('main:users-update_user')

    def test_update_unauthorized(self):
        response = self.client.put(self.base_url)
        self.assert_status_equal(response, status.HTTP_401_UNAUTHORIZED)

from django.shortcuts import reverse

from rest_framework import status

from djet.assertions import StatusCodeAssertionsMixin

from .base import BaseTestUser


class TestDetailUserAPI(BaseTestUser, StatusCodeAssertionsMixin):
    @staticmethod
    def build_url(pk):
        return reverse('main:users-detail', args=[pk])

    def test_detail_unauthorized(self):
        response = self.client.get(self.build_url(self.user.pk))
        self.assert_status_equal(response, status.HTTP_401_UNAUTHORIZED)

    def test_detail_authorized(self):
        response = self.client_auth.get(self.build_url(self.user.pk))
        self.assert_status_equal(response, status.HTTP_200_OK)

    def test_detail_myself(self):
        response = self.client_auth.get(self.build_url(0))
        self.assert_status_equal(response, status.HTTP_200_OK)

    def test_detail_not_found(self):
        response = self.client_auth.get(self.build_url(99))
        self.assert_status_equal(response, status.HTTP_404_NOT_FOUND)

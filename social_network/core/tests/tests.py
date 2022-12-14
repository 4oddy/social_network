from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from core.utils import generate_user_data

User = get_user_model()


def create_authenticated_api_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


class BaseTest(TestCase):
    def setUp(self):
        # creating main user
        self.user = User.objects.create_user(**generate_user_data())

        # creating second user
        self.second_user = User.objects.create_user(**generate_user_data())

        self.client_auth = create_authenticated_api_client(self.user)

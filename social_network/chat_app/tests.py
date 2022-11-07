from django.test import TestCase

from django.contrib.auth import get_user_model

from rest_framework.test import APIClient

from core.utils import generate_user_data

User = get_user_model()


class BaseGroupTest(TestCase):
    group_url: str

    def setUp(self) -> None:
        self.user = User.objects.create_user(**generate_user_data())
        client = APIClient()

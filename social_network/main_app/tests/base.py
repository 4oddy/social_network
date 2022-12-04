from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient

from core.utils import generate_user_data

from ..models import Post

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


class BaseTestUser(BaseTest):
    pass


class BaseTestPost(BaseTest):
    @staticmethod
    def create_post(owner, title='test', description=None):
        return Post.objects.create(title=title, description=description, owner=owner)


class BaseTestFriendRequest(BaseTest):
    def setUp(self):
        super(BaseTestFriendRequest, self).setUp()
        self.third_user = User.objects.create_user(**generate_user_data())

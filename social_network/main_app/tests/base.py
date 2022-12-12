from django.contrib.auth import get_user_model

from core.tests.tests import BaseTest
from core.utils import generate_user_data

from ..models import Post, FriendRequest

User = get_user_model()


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

    @staticmethod
    def create_request(from_user, to_user):
        return FriendRequest.objects.create(from_user=from_user, to_user=to_user)

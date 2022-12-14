from core.tests.common import assertions, reverse, status

from ..models import Post
from .base import BaseTestPost


class TestCreatePostAPI(BaseTestPost,
                        assertions.StatusCodeAssertionsMixin,
                        assertions.InstanceAssertionsMixin):
    def setUp(self):
        super(TestCreatePostAPI, self).setUp()

        self.base_url = reverse('main:posts-list')
        self.data = {'title': 'test', 'description': 'test'}

    def test_create_unauthorized(self):
        response = self.client.post(self.base_url, data=self.data)
        self.assert_status_equal(response, status.HTTP_401_UNAUTHORIZED)

    def test_create_authorized(self):
        response = self.client_auth.post(self.base_url, data=self.data)
        self.assert_status_equal(response, status.HTTP_201_CREATED)
        self.assert_instance_exists(Post, owner=self.user, **self.data)

    def test_create_empty_post(self):
        response = self.client_auth.post(self.base_url)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)
        self.assert_instance_does_not_exist(Post, owner=self.user)

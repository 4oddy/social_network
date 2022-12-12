from core.tests.common import reverse, status, assertions

from .base import BaseTestPost


class TestListPostAPI(BaseTestPost, assertions.StatusCodeAssertionsMixin):
    def setUp(self):
        super(TestListPostAPI, self).setUp()

        self.base_url = reverse('main:posts-list')
        self.friends_posts_url = reverse('main:posts-friends_posts')
        self.user_posts_url = reverse('main:posts-user_posts')

    def test_list_posts_unauthorized(self):
        response = self.client.get(self.base_url)
        self.assert_status_equal(response, status.HTTP_401_UNAUTHORIZED)

    def test_list_posts_authorized(self):
        response = self.client_auth.get(self.base_url)
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)

    def test_list_posts_exists(self):
        self.create_post(owner=self.user)

        response = self.client_auth.get(self.base_url)
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_friends_posts(self):
        self.create_post(owner=self.second_user)

        self.user.make_friends(self.user, self.second_user)

        response = self.client_auth.get(self.friends_posts_url)
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_user_posts(self):
        self.create_post(owner=self.user)

        response = self.client_auth.get(self.user_posts_url)
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

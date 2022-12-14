from PIL import Image

from core.tests.common import assertions, reverse, status

from .base import BaseTestUser


class TestDetailUserAPI(BaseTestUser, assertions.StatusCodeAssertionsMixin):
    def setUp(self):
        super(TestDetailUserAPI, self).setUp()

        self.delete_image_url = reverse('main:users-delete_profile_image')
        self.friends_url = reverse('main:users-friends', args=[self.user.pk])

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
        self.assertEqual(response.data['username'], self.user.username)

    def test_detail_not_found(self):
        response = self.client_auth.get(self.build_url(99))
        self.assert_status_equal(response, status.HTTP_404_NOT_FOUND)

    def test_delete_image_unauthorized(self):
        response = self.client.get(self.delete_image_url)
        self.assert_status_equal(response, status.HTTP_401_UNAUTHORIZED)

    def test_delete_default_image(self):
        response = self.client_auth.get(self.delete_image_url)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    def test_delete_image(self):
        self.user.image = Image.new('RGB', (100, 100))
        response = self.client_auth.get(self.delete_image_url)
        self.assert_status_equal(response, status.HTTP_200_OK)

    def test_user_friends_unauthorized(self):
        response = self.client.get(self.friends_url)
        self.assert_status_equal(response, status.HTTP_401_UNAUTHORIZED)

    def test_user_has_no_friends(self):
        response = self.client_auth.get(self.friends_url)
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_user_has_friend(self):
        self.user.friends.add(self.second_user)
        response = self.client_auth.get(self.friends_url)
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

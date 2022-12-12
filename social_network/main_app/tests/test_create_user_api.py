from django.contrib.auth import get_user_model

from core.tests.common import reverse, assertions, status

from .base import BaseTestUser, generate_user_data

User = get_user_model()


class UserCreateTestAPI(BaseTestUser,
                        assertions.StatusCodeAssertionsMixin,
                        assertions.InstanceAssertionsMixin):
    def setUp(self):
        super(UserCreateTestAPI, self).setUp()
        self.base_url = reverse('main:users-list')

        self.user_data = generate_user_data()

    def test_create_user_unauthorized(self):
        response = self.client.post(self.base_url, data=self.user_data)

        self.assert_status_equal(response, status.HTTP_201_CREATED)
        self.assertTrue('password' not in response.data)
        self.assert_instance_exists(User, username=self.user_data['username'])
        user = User.objects.get(username=self.user_data['username'])
        self.assertTrue(user.check_password(self.user_data['password']))

    def test_not_create_user_username_exists(self):
        User.objects.create_user(**self.user_data)

        response = self.client.post(self.base_url, data=self.user_data)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    def test_create_user_missing_required_fields(self):
        response = self.client.post(self.base_url)
        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

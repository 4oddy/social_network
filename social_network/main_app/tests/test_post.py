from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.test import TestCase

from core.utils import generate_user_data

from ..models import Post

User = get_user_model()


class TestPost(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(**generate_user_data())

        self._create_post_url = reverse('main:create_post')

    def create_post(self, data):
        response = self.client.post(self._create_post_url, data=data)
        return response

    def test_creating_positive(self):
        self.client.login(username=self.user.username, password=self.user.username)
        self.create_post(data={'title': 'test_post', 'description': 'test'})
        self.assertTrue(Post.objects.filter(owner=self.user, title='test_post').exists())

    def test_creating_negative(self):
        self.client.login(username=self.user.username, password=self.user.username)
        self.create_post({'title': '', 'description': ''})
        self.assertFalse(Post.objects.filter(owner=self.user).exists())

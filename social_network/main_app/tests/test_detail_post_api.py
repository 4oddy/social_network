from core.tests.common import reverse, status, assertions

from .base import BaseTestPost

from ..models import Post


class TestDetailPostAPI(BaseTestPost,
                        assertions.StatusCodeAssertionsMixin,
                        assertions.InstanceAssertionsMixin):
    def setUp(self):
        super(TestDetailPostAPI, self).setUp()
        self.post = self.create_post(self.user)

    @staticmethod
    def build_url(pk):
        return reverse('main:posts-detail', args=[pk])

    @staticmethod
    def build_comments_url(pk):
        return reverse('main:posts-comments', args=[pk])

    @staticmethod
    def build_leave_comment_url(pk):
        return reverse('main:posts-leave_comment', args=[pk])

    def test_detail_unauthorized(self):
        response = self.client.get(self.build_url(self.post.pk))
        self.assert_status_equal(response, status.HTTP_401_UNAUTHORIZED)

    def test_detail_authorized(self):
        response = self.client_auth.get(self.build_url(self.post.pk))
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertTrue(self.user.username == response.json()['owner']['username'])

    def test_detail_comments(self):
        response = self.client_auth.get(self.build_comments_url(self.post.pk))
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)

    def test_detail_leave_comment(self):
        response = self.client_auth.post(self.build_leave_comment_url(self.post.pk), data={'text': 'test'})
        self.assert_status_equal(response, status.HTTP_201_CREATED)
        self.assertTrue(self.user.username == response.json()['owner']['username'])

    def test_detail_comment_exists(self):
        self.client_auth.post(self.build_leave_comment_url(self.post.pk), data={'text': 'test'})

        response = self.client_auth.get(self.build_comments_url(self.post.pk))
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_delete_own_post(self):
        post = self.create_post(self.user, title='test-delete')

        response = self.client_auth.delete(self.build_url(post.pk))
        self.assert_status_equal(response, status.HTTP_204_NO_CONTENT)
        self.assert_instance_does_not_exist(Post, owner=self.user, title='test-delete')

    def test_cannot_delete_not_own_post(self):
        post = self.create_post(self.second_user)

        response = self.client_auth.delete(self.build_url(post.pk))
        self.assert_status_equal(response, status.HTTP_403_FORBIDDEN)
        self.assert_instance_exists(Post, owner=self.second_user)

    def test_update_own_post(self):
        post = self.create_post(self.user, title='test-update')

        response = self.client_auth.put(self.build_url(post.pk), data={'title': 'test-updated'})
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual('test-updated', response.json()['title'])

    def test_cannot_update_not_own_post(self):
        post = self.create_post(self.second_user, title='test-update')

        response = self.client_auth.put(self.build_url(post.pk), data={'title': 'test-updated'})
        self.assert_status_equal(response, status.HTTP_403_FORBIDDEN)

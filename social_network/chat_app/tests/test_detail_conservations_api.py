from core.tests.common import assertions, reverse, status

from ..models import ConservationMessage
from .base import BaseTestConservations


class TestDetailConservationsAPI(BaseTestConservations,
                                 assertions.StatusCodeAssertionsMixin,
                                 assertions.InstanceAssertionsMixin):
    def setUp(self):
        super().setUp()
        self.conservation = self.create_group(name='test',
                                              owner=self.user,
                                              members=[self.user, self.second_user])

    @staticmethod
    def build_url(pk):
        return reverse('chat:conservations-detail', args=(pk,))

    @staticmethod
    def build_send_message_url(pk):
        return reverse('chat:conservations-send_message', args=(pk,))

    @staticmethod
    def build_group_messages_url(pk):
        return reverse('chat:conservations-group_messages', args=(pk,))

    def test_detail_unauthorized(self):
        response = self.client.get(self.build_url(self.conservation.pk))
        self.assert_status_equal(response, status.HTTP_401_UNAUTHORIZED)

    def test_detail_authorized(self):
        response = self.client_auth.get(self.build_url(self.conservation.pk))
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(response.json()['owner']['username'], self.user.username)

    def test_detail_404(self):
        response = self.client_auth.get(self.build_url(99))
        self.assert_status_equal(response, status.HTTP_404_NOT_FOUND)

    def test_send_message_unauthorized(self):
        response = self.client.post(self.build_send_message_url(self.conservation.pk),
                                    data={'text': 'test'})
        self.assert_status_equal(response, status.HTTP_401_UNAUTHORIZED)

    def test_send_message_authorized(self):
        response = self.client_auth.post(self.build_send_message_url(self.conservation.pk),
                                         data={'text': 'test'})
        self.assert_status_equal(response, status.HTTP_201_CREATED)
        self.assert_instance_exists(ConservationMessage, sender=self.user, text='test')

    def test_group_no_messages(self):
        response = self.client_auth.get(self.build_group_messages_url(self.conservation.pk))
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)

    def test_group_message_exists(self):
        self.send_message(sender=self.user, text='test', group=self.conservation)

        response = self.client_auth.get(self.build_group_messages_url(self.conservation.pk))
        self.assert_status_equal(response, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

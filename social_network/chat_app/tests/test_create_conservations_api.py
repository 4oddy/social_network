from core.tests.common import assertions, reverse, status

from ..models import Conservation
from .base import BaseTestConservations


class TestCreateConservationsAPI(BaseTestConservations,
                                 assertions.StatusCodeAssertionsMixin,
                                 assertions.InstanceAssertionsMixin):
    def setUp(self):
        super().setUp()
        self.base_url = reverse('chat:conservations-list')

    def test_create_conservation_unauthorized(self):
        response = self.client.post(self.base_url, data={'name': 'test',
                                                         'members': []})
        self.assert_status_equal(response, status.HTTP_401_UNAUTHORIZED)

    def test_create_conservation_with_no_members(self):
        response = self.client_auth.post(self.base_url, data={'name': 'test',
                                                              'members': []})

        self.assert_status_equal(response, status.HTTP_201_CREATED)
        self.assert_instance_exists(Conservation, owner=self.user, name='test')

        conservation = Conservation.objects.get(owner=self.user, name='test')
        self.assertTrue(self.user in conservation.members.all())

    def test_create_conservation_with_owner(self):
        response = self.client_auth.post(self.base_url, data={'name': 'test',
                                                              'members_id': [self.user.pk]})

        self.assert_status_equal(response, status.HTTP_201_CREATED)
        self.assert_instance_exists(Conservation, owner=self.user, name='test')

        conservation = Conservation.objects.get(owner=self.user, name='test')
        self.assertTrue(self.user in conservation.members.all())

    def test_create_conservation_with_not_friend(self):
        response = self.client_auth.post(self.base_url, data={'name': 'test',
                                                              'members_id': [self.second_user.pk]})

        self.assert_status_equal(response, status.HTTP_400_BAD_REQUEST)

    def test_create_conservation_with_friend(self):
        self.user.make_friends(self.user, self.second_user)

        response = self.client_auth.post(self.base_url, data={'name': 'test',
                                                              'members_id': [self.second_user.pk]})

        self.assert_status_equal(response, status.HTTP_201_CREATED)
        self.assert_instance_exists(Conservation, owner=self.user, name='test')

        conservation = Conservation.objects.get(owner=self.user, name='test')
        self.assertTrue(self.user in conservation.members.all())
        self.assertTrue(self.second_user in conservation.members.all())

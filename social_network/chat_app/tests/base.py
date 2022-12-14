from django.contrib.auth import get_user_model

from core.tests.tests import BaseTest
from core.utils import generate_user_data

from ..models import Conservation, Dialog

User = get_user_model()


class BaseTestGroups(BaseTest):
    def setUp(self):
        super().setUp()
        self.third_user = User.objects.create_user(**generate_user_data())

    def create_group(self, **kwargs):
        raise NotImplementedError


class BaseTestDialogs(BaseTestGroups):
    @staticmethod
    def create_group(owner, second_user):
        return Dialog.objects.create(owner=owner, second_user=second_user, name=second_user)


class BaseTestConservations(BaseTestGroups):
    @staticmethod
    def create_group(self, name, owner, members):
        return Conservation.objects.create(name=name, owner=owner, members=members)

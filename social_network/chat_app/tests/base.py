from django.contrib.auth import get_user_model

from core.tests.tests import BaseTest
from core.utils import generate_user_data

from ..models import Conservation, ConservationMessage, Dialog, DialogMessage

User = get_user_model()


class BaseTestGroups(BaseTest):
    def setUp(self):
        super().setUp()
        self.third_user = User.objects.create_user(**generate_user_data())

    @staticmethod
    def create_group(**kwargs):
        raise NotImplementedError

    @staticmethod
    def send_message(sender, text, group):
        raise NotImplementedError


class BaseTestDialogs(BaseTestGroups):
    @staticmethod
    def create_group(owner, second_user):
        return Dialog.objects.create(owner=owner, second_user=second_user, name=second_user)

    @staticmethod
    def send_message(sender, text, group):
        return DialogMessage.objects.create(sender=sender, text=text, group=group)


class BaseTestConservations(BaseTestGroups):
    @staticmethod
    def create_group(name, owner, members):
        conservation = Conservation.objects.create(name=name, owner=owner)
        conservation.members.set(members)
        return conservation

    @staticmethod
    def send_message(sender, text, group):
        return ConservationMessage.objects.create(sender=sender, text=text, group=group)

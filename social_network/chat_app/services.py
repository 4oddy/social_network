from abc import ABC, abstractmethod

from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.db.models import Q, QuerySet

from core.utils import get_current_date

from .exceptions import DialogExistsError, NotInFriendsError, SelfDialogError
from .models import (AbstractDialog, AbstractMessage, Conservation,
                     ConservationMessage, Dialog, DialogMessage)

User = get_user_model()


def _check_not_friends(user: User, checking_value: list[User]) -> list[str]:
    """ Check what people from checking_value are not in friends with user """
    not_in_friends = list(map(
        lambda not_friend: not_friend.username,
        filter(lambda friend: friend not in user.friends.all() and friend != user, checking_value))
    )
    return not_in_friends


class AbstractGetter(ABC):
    @abstractmethod
    async def get_group(self, *args, **kwargs) -> AbstractDialog:
        pass

    @abstractmethod
    def get_user_groups(self, user: User) -> QuerySet[AbstractDialog]:
        pass


class AbstractCreatorGroups(ABC):
    @abstractmethod
    def create_group(self, **kwargs):
        pass


class AbstractSaver(ABC):
    @abstractmethod
    async def save_message(self, user: User, message: str, group: AbstractDialog) -> AbstractMessage:
        pass


class GetterConservations(AbstractGetter):
    """ Class to manage logic of getting conservations """

    @sync_to_async
    def get_group(self, **kwargs) -> Conservation | None:
        group = Conservation.objects.filter(**kwargs).first()
        return group

    def get_user_groups(self, user: User) -> QuerySet[Conservation]:
        """ Get all conservations of user """
        return Conservation.objects.select_related('owner').\
            prefetch_related('members').filter(Q(members=user))


class GetterDialogs(AbstractGetter):
    """ Class to manage logic of getting dialogs"""

    dialogs = Dialog.objects.select_related('owner', 'second_user')

    def get_group_sync(self, user: User,
                       companion: User | None = None,
                       companion_username: str | None = None) -> Dialog | None:

        # search by companion id
        if companion:
            dialog = self.dialogs.filter(
                Q(owner=user)
                & Q(name=companion.username)
                & Q(second_user=companion)
                | Q(owner=companion)
                & Q(name=user.username)
                & Q(second_user=user)).first()

        # search by companion username
        elif companion_username:
            dialog = self.dialogs.filter(
                Q(owner=user)
                & Q(name=companion_username)
                & Q(second_user__username=companion_username)
                | Q(owner__username=companion_username)
                & Q(name=user.username)
                & Q(second_user=user)).first()
        else:
            raise TypeError('You have to define companion or companion_username')

        return dialog

    def get_user_groups(self, user: User) -> QuerySet[Dialog]:
        dialogs = self.dialogs.filter(Q(owner=user) | Q(second_user=user))
        return dialogs

    get_group = sync_to_async(get_group_sync)


class CreatorConservations(AbstractCreatorGroups):
    @staticmethod
    def create_group(**kwargs) -> Conservation:
        """ Create conservation """
        owner = kwargs.get('owner')
        members = kwargs.pop('members', None)

        if members is not None:
            not_in_friends = _check_not_friends(owner, members)

            if any(not_in_friends):
                raise NotInFriendsError(not_in_friends)

            if owner not in members:
                members.append(owner)

        conservation = Conservation.objects.create(**kwargs)
        conservation.members.set(members)
        return conservation


class CreatorDialogs(AbstractCreatorGroups):
    _getter = GetterDialogs()

    def create_group(self, owner: User, second_user: User) -> Dialog:
        """ Create dialog between owner and second_user
            The name of the dialog will be second_user.username
        """
        if owner == second_user:
            raise SelfDialogError()

        if not User.in_friendship(owner, second_user):
            raise NotInFriendsError(second_user)

        if self._getter.get_group_sync(user=owner, companion=second_user):
            raise DialogExistsError()

        return Dialog.objects.create(owner=owner,
                                     name=second_user.username,
                                     second_user=second_user)


class SaverConservationMessages(AbstractSaver):
    """ Class to manage logic of saving conservation messages """

    @sync_to_async
    def save_message(self, user: User, message: str, group: Conservation) -> ConservationMessage:
        msg = ConservationMessage.objects.create(text=message, sender=user, group=group)
        return msg


class SaverDialogMessages(AbstractSaver):
    """ Class to manage logic of saving dialog messages """

    @sync_to_async
    def save_message(self, user: User, message: str, group: Dialog) -> DialogMessage:
        msg = DialogMessage.objects.create(text=message, sender=user, group=group)
        return msg


class SenderMessages:
    """ Class to manage logic of sending messages """

    def __init__(self, saver: AbstractSaver):
        self._saver = saver
        self._channel_layer = get_channel_layer()

    async def send_message(self, sender: User, message: str, group: AbstractDialog) -> AbstractMessage:
        """ Method sends message to current channel layer """
        sender_dict = self._generate_data_for_sending(sender)

        group_uuid = str(group.uid)

        message_instance = await self._saver.save_message(user=sender, message=message, group=group)

        await self._channel_layer.group_send(
            group_uuid,
            {
                'type': 'chat_message',
                'message': message,
                'sender_dict': sender_dict
            }
        )

        return message_instance

    @staticmethod
    def _generate_data_for_sending(sender: User) -> dict:
        """ Method to generate data which will be sent to frontend """
        data = {
            'username': sender.username,
            'image_url': sender.image.url,
            'profile_url': sender.get_absolute_url(),
            'date': get_current_date()
        }
        return data

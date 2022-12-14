from abc import ABC, abstractmethod

from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404

from core.utils import get_current_date

from .models import (AbstractDialog, AbstractMessage, Conservation,
                     ConservationMessage, Dialog, DialogMessage)

User = get_user_model()


class AbstractGetter(ABC):
    @abstractmethod
    async def get_group(self, *args, **kwargs) -> AbstractDialog:
        pass

    @abstractmethod
    def get_user_groups(self, user: User) -> QuerySet[AbstractDialog]:
        pass


class AbstractSaver(ABC):
    @abstractmethod
    async def save_message(self, user: User, message: str, group: AbstractDialog) -> AbstractMessage:
        pass


class AbstractCreatorGroups(ABC):
    @abstractmethod
    def create_group(self, **kwargs):
        pass


class CreatorConservations(AbstractCreatorGroups):
    @staticmethod
    def create_group(**kwargs) -> Conservation:
        return Conservation.objects.create(**kwargs)


class CreatorDialogs(AbstractCreatorGroups):
    @staticmethod
    def create_group(owner: User, second_user: User) -> Dialog:
        return Dialog.objects.create(owner=owner, name=second_user.username, second_user=second_user)


class GetterConservations(AbstractGetter):
    """ Class to manage logic of getting conservations """

    @sync_to_async
    def get_group(self, **kwargs) -> Conservation:
        group = get_object_or_404(Conservation, **kwargs)
        return group

    def get_user_groups(self, user: User) -> QuerySet[Conservation]:
        return Conservation.objects.select_related('owner').prefetch_related('members').filter(Q(members=user))


class GetterDialogs(AbstractGetter):
    """ Class to manage logic of getting dialogs"""
    @staticmethod
    def get_group_sync(user: User,
                       companion: User | None = None,
                       companion_username: str | None = None) -> Dialog | None:
        if companion:
            dialog = Dialog.objects.select_related('owner', 'second_user').filter(
                Q(owner=user) & Q(name=companion.username) & Q(second_user=companion) |
                Q(owner=companion) & Q(name=user.username) & Q(second_user=user)).first()
        elif companion_username:
            dialog = Dialog.objects.select_related('owner', 'second_user').filter(
                Q(owner=user) & Q(name=companion_username) & Q(second_user__username=companion_username) |
                Q(owner__username=companion_username) & Q(name=user.username) & Q(second_user=user)).first()
        else:
            raise TypeError('You have to define companion or companion_username')

        return dialog

    def get_user_groups(self, user: User) -> QuerySet[Dialog]:
        dialogs = Dialog.objects.select_related('owner', 'second_user').filter(Q(owner=user) | Q(second_user=user))
        return dialogs

    get_group = staticmethod(sync_to_async(get_group_sync))


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
        sender_dict = {
            'username': sender.username,
            'image_url': sender.image.url,
            'profile_url': sender.get_absolute_url(),
            'date': get_current_date()
        }

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

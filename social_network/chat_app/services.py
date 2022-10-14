from abc import ABC, abstractmethod

from asgiref.sync import sync_to_async, async_to_sync
from channels.layers import get_channel_layer
from django.forms import model_to_dict

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q, QuerySet

from .models import AbstractDialog, AbstractMessage, Conservation, ConservationMessage, Dialog, DialogMessage
from .exceptions import SelfDialogCreated

from core.utils import get_current_date

User = get_user_model()


class AbstractGetter(ABC):
    @abstractmethod
    async def get_group(self, name: str | User, owner: User) -> AbstractDialog:
        pass

    @abstractmethod
    def get_user_groups(self, user: User) -> QuerySet[AbstractDialog]:
        pass


class AbstractSaver(ABC):
    @abstractmethod
    async def save_message(self, user: User, message: str, group: AbstractDialog) -> AbstractMessage:
        pass


class GetterConservations(AbstractGetter):
    """ Class to manage logic of getting conservations """

    @sync_to_async
    def get_group(self, name: str, owner: User | None) -> Conservation:
        if owner is not None:
            group = get_object_or_404(Conservation, owner=owner, name=name)
        else:
            group = get_object_or_404(Conservation, name=name)
        return group

    def get_user_groups(self, user: User) -> QuerySet[Conservation]:
        return Conservation.objects.filter(Q(members=user))


class GetterDialogs(AbstractGetter):
    """ Class to manage logic of getting dialogs"""

    @sync_to_async
    def get_group(self, user: User, companion: User | None = None, companion_username: str | None = None) -> Dialog:
        if companion:
            if companion.username == user.username:
                raise SelfDialogCreated('Пользователь не может начать диалог с самим собой')

            dialog = Dialog.objects.select_related('owner', 'second_user').filter(
                Q(owner=user) & Q(name=companion.username) & Q(second_user=companion) |
                Q(owner=companion) & Q(name=user.username) & Q(second_user=user)).first()

            if dialog is None:
                dialog = Dialog.objects.create(name=companion.username, owner=user, second_user=companion)

        elif companion_username:
            if companion_username == user.username:
                raise SelfDialogCreated('Пользователь не может начать диалог с самим собой')

            dialog = Dialog.objects.select_related('owner', 'second_user').filter(
                Q(owner=user) & Q(name=companion_username) & Q(second_user__username=companion_username) |
                Q(owner__username=companion_username) & Q(name=user.username) & Q(second_user=user)).first()

            if dialog is None:
                second_user = get_object_or_404(User, username=companion_username)
                dialog = Dialog.objects.create(name=companion_username, owner=user, second_user=second_user)
        else:
            raise TypeError('You have to define companion or companion_username')

        return dialog

    def get_user_groups(self, user: User) -> QuerySet[Dialog]:
        dialogs = Dialog.objects.filter(Q(owner=user) | Q(second_user=user))
        return dialogs

    get_group_sync = async_to_sync(get_group)


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
        self._saver: AbstractSaver = saver
        self._channel_layer = get_channel_layer()

    async def send_message(self, sender: User, message: str, group: AbstractDialog) -> None:
        sender_dict: dict = await sync_to_async(model_to_dict)(sender, fields=('username',))
        sender_dict['image_url'] = sender.image.url
        sender_dict['profile_url'] = sender.get_absolute_url()

        group_uuid = str(group.uid)

        await self._saver.save_message(user=sender, message=message, group=group)

        sender_dict['date'] = get_current_date()

        await self._channel_layer.group_send(
            group_uuid,
            {
                'type': 'chat_message',
                'message': message,
                'sender_dict': sender_dict
            }
        )

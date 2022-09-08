from abc import ABC, abstractmethod

from asgiref.sync import sync_to_async, async_to_sync
from channels.layers import get_channel_layer
from django.forms import model_to_dict

from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import AbstractDialog, Conservation, ConservationMessage, Dialog, DialogMessage
from .exceptions import SelfDialogCreated

User = get_user_model()


class AbstractGetter(ABC):
    @abstractmethod
    def get_group(self, name: str, owner: User):
        pass


class AbstractSaver(ABC):
    @abstractmethod
    def save_message(self, user: User, message: str, group: AbstractDialog):
        pass


class GetterConservations(AbstractGetter):
    """ Class to manage logic of getting conservations """

    @sync_to_async
    def get_group(self, name: str, owner: User):
        if owner is not None:
            group = get_object_or_404(Conservation, owner=owner, name=name)
        else:
            group = get_object_or_404(Conservation, name=name)
        return group


class GetterDialogs(AbstractGetter):
    """ Class to manage logic of getting dialogs"""

    @sync_to_async
    def get_group(self, companion_name: str, user: User):
        if companion_name == user.username:
            raise SelfDialogCreated('Пользователь не может начать диалог с самим собой')

        dialog: Dialog = Dialog.objects.filter(Q(owner=user) & Q(name=companion_name) &
                                               Q(second_user__username=companion_name) |
                                               Q(owner__username=companion_name) & Q(name=user.username) &
                                               Q(second_user=user)).first()

        if dialog is None:
            second_user: User = get_object_or_404(User, username=companion_name)

            dialog = Dialog.objects.create(name=companion_name, owner=user, second_user=second_user)

        return dialog

    get_group_sync = async_to_sync(get_group)


class SaverConservationMessages(AbstractSaver):
    """ Class to manage logic of saving conservation messages """

    @sync_to_async
    def save_message(self, user: User, message: str, group: Conservation):
        msg = ConservationMessage.objects.create(text=message, sender=user, group=group)
        return msg


class SaverDialogMessages(AbstractSaver):
    """ Class to manage logic of saving dialog messages """

    @sync_to_async
    def save_message(self, user: User, message: str, group: Dialog):
        msg = DialogMessage.objects.create(text=message, sender=user, group=group)
        return msg


class SenderMessages:
    """ Class to manage logic of sending messages """

    def __init__(self, saver: AbstractSaver):
        self._saver: AbstractSaver = saver
        self._channel_layer = get_channel_layer()

    async def send_message(self, sender: User, message: str, group: AbstractDialog):
        sender_dict: dict = await sync_to_async(model_to_dict)(sender, fields=('username', ))
        sender_dict['image_url'] = sender.image.url
        sender_dict['profile_url'] = sender.get_absolute_url()

        await self._saver.save_message(user=sender, message=message, group=group)

        await self._channel_layer.group_send(
            group.uid,
            {
                'type': 'chat_message',
                'message': message,
                'sender_dict': sender_dict
            }
        )

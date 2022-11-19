import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

from .services import (AbstractGetter, AbstractSaver, GetterConservations, GetterDialogs,
                       SaverDialogMessages, SaverConservationMessages, SenderMessages)

from .models import AbstractDialog, Dialog

User = get_user_model()


class BaseChatConsumer(AsyncWebsocketConsumer):
    _getter: AbstractGetter
    _saver: AbstractSaver
    _sender: SenderMessages

    async def connect(self):
        self.user: str = self.scope['user']
        self.group_uuid: str = self.scope['url_route']['kwargs']['group_uuid']
        self.group: AbstractDialog = await self._getter.get_group(uid=self.group_uuid)
        self.group_uuid = str(self.group.uid)

        await self.channel_layer.group_add(
            self.group_uuid,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.group_uuid,
            self.channel_name
        )

        await self.close()

    async def receive(self, text_data=None, bytes_data=None):
        data: dict = json.loads(text_data)

        message: str = data['message']

        if message:
            sender: User = self.user

            await self._sender.send_message(sender=sender, message=message, group=self.group)

    async def chat_message(self, event: dict):
        message = event['message']
        sender_dict = event['sender_dict']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender_dict': sender_dict
        }))


class ConservationConsumer(BaseChatConsumer):
    _getter: GetterConservations = GetterConservations()
    _saver: SaverConservationMessages = SaverConservationMessages()
    _sender: SenderMessages = SenderMessages(saver=_saver)


class DialogConsumer(BaseChatConsumer):
    _getter: GetterDialogs = GetterDialogs()
    _saver: SaverDialogMessages = SaverDialogMessages()
    _sender: SenderMessages = SenderMessages(saver=_saver)

    async def connect(self):
        self.user: str = self.scope['user']
        self.group_name: str = self.scope['url_route']['kwargs']['group_name']
        self.group: Dialog = await self._getter.get_group(companion_username=self.group_name, user=self.user)
        self.group_uuid = str(self.group.uid)

        await self.channel_layer.group_add(
            self.group_uuid,
            self.channel_name
        )

        await self.accept()

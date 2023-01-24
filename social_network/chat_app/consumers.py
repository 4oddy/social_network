import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

from .services import (AbstractGetter, GetterConservations, GetterDialogs,
                       SaverConservationMessages, SaverDialogMessages,
                       SenderMessages)

User = get_user_model()


class BaseChatConsumer(AsyncWebsocketConsumer):
    _getter: AbstractGetter
    _sender: SenderMessages

    async def connect(self):
        self.user = self.scope['user']
        self.group_uuid = self.scope['url_route']['kwargs']['group_uuid']
        self.group = await self._getter.get_group(uid=self.group_uuid)

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
        data = json.loads(text_data)

        message = data['message']

        if message:
            sender = self.user
            await self._sender.send_message(sender=sender,
                                            message=message,
                                            group=self.group)

    async def chat_message(self, event: dict):
        message = event['message']
        sender_dict = event['sender_dict']

        await self.send(text_data=json.dumps({
            'message': message,
            'sender_dict': sender_dict
        }))


class ConservationConsumer(BaseChatConsumer):
    _getter: GetterConservations = GetterConservations()
    _sender: SenderMessages = SenderMessages(saver=SaverConservationMessages())


class DialogConsumer(BaseChatConsumer):
    _getter: GetterDialogs = GetterDialogs()
    _sender: SenderMessages = SenderMessages(saver=SaverDialogMessages())

    async def connect(self):
        self.user = self.scope['user']
        self.group_name = self.scope['url_route']['kwargs']['group_name']
        self.group = await self._getter.get_group(companion_username=self.group_name,
                                                  user=self.user)
        self.group_uuid = str(self.group.uid)

        await self.channel_layer.group_add(
            self.group_uuid,
            self.channel_name
        )

        await self.accept()

from rest_framework import serializers

from asgiref.sync import async_to_sync

from main_app.api.serializers import UserSerializer

from .. import models
from .. import services


class BaseGroupSerializer(serializers.ModelSerializer):
    owner = UserSerializer()

    class BaseMeta:
        model = models.AbstractDialog
        fields = '__all__'


class DialogSerializer(BaseGroupSerializer):
    second_user = UserSerializer()

    class Meta(BaseGroupSerializer.BaseMeta):
        model = models.Dialog


class ConservationSerializer(BaseGroupSerializer):
    members = UserSerializer(many=True)

    class Meta(BaseGroupSerializer.BaseMeta):
        model = models.Conservation


class DialogMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DialogMessage
        fields = '__all__'


class ConservationMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ConservationMessage
        fields = '__all__'


class BaseCreatingMessageSerializer(serializers.ModelSerializer):
    _saver: services.AbstractSaver
    _sender: services.SenderMessages

    class BaseMeta:
        model = models.AbstractMessage
        exclude = ('group', )
        read_only_fields = ('sender', )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['sender'] = self.context['request'].user.pk
        return data

    def create(self, validated_data):
        sync_send_message = async_to_sync(self._sender.send_message)
        message = sync_send_message(sender=self.context['request'].user, message=validated_data['text'],
                                    group=self.context['group'])
        return message


class CreateDialogMessageSerializer(BaseCreatingMessageSerializer):
    _saver = services.SaverDialogMessages()
    _sender = services.SenderMessages(saver=_saver)

    class Meta(BaseCreatingMessageSerializer.BaseMeta):
        model = models.DialogMessage


class CreateConservationMessageSerializer(BaseCreatingMessageSerializer):
    _saver = services.SaverConservationMessages()
    _sender = services.SenderMessages(saver=_saver)

    class Meta(BaseCreatingMessageSerializer.BaseMeta):
        model = models.ConservationMessage

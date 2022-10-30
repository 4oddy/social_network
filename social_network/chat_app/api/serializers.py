from rest_framework import serializers

from asgiref.sync import async_to_sync

from main_app.api.serializers import UserSerializer

from .. import models
from .. import services


class BaseGroupSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class BaseMeta:
        model = models.AbstractDialog
        fields = '__all__'


class DialogSerializer(BaseGroupSerializer):
    second_user = UserSerializer(read_only=True)

    class Meta(BaseGroupSerializer.BaseMeta):
        model = models.Dialog
        read_only_fields = ('name', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        context = kwargs.pop('context')

        if context.pop('creating', None):
            user = context['request'].user
            self.fields['second_user'] = serializers.PrimaryKeyRelatedField(queryset=user.friends.all(),
                                                                            write_only=True)

    def create(self, validated_data):
        dialog = services.GetterDialogs().get_group_sync(user=self.context['request'].user,
                                                         companion=validated_data['second_user'])
        return dialog


class ConservationSerializer(BaseGroupSerializer):
    members = UserSerializer(many=True)

    class Meta(BaseGroupSerializer.BaseMeta):
        model = models.Conservation

    def to_internal_value(self, data):
        self.fields['members'] = serializers.PrimaryKeyRelatedField(queryset=self.context['request'].user.friends.all(),
                                                                    write_only=True, many=True)
        return super().to_internal_value(data)

    def create(self, validated_data):
        owner = self.context['request'].user
        conservation = models.Conservation.objects.create(owner=owner, name=validated_data['name'])
        validated_data['members'].append(owner)
        conservation.members.set(validated_data['members'])
        return conservation


class BaseMessageSerializer(serializers.ModelSerializer):
    class BaseMeta:
        model = models.AbstractDialog
        fields = '__all__'


class DialogMessageSerializer(BaseMessageSerializer):
    class Meta(BaseMessageSerializer.BaseMeta):
        model = models.DialogMessage


class ConservationMessageSerializer(BaseMessageSerializer):
    class Meta(BaseMessageSerializer.BaseMeta):
        model = models.ConservationMessage


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

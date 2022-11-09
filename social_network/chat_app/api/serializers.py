from rest_framework import serializers

from django.contrib.auth import get_user_model

from asgiref.sync import async_to_sync

from main_app.api.serializers import UserSerializer

from .. import models, services

User = get_user_model()


class BaseGroupSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class BaseMeta:
        model = models.AbstractDialog
        fields = '__all__'


class DialogSerializer(BaseGroupSerializer):
    second_user = UserSerializer(read_only=True)
    second_user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)

    class Meta(BaseGroupSerializer.BaseMeta):
        model = models.Dialog
        read_only_fields = ('name', )

    def validate_second_user_id(self, value):
        user = self.context['request'].user

        if value == user:
            raise serializers.ValidationError('Нельзя начать диалог с собой')

        if value not in user.friends.all():
            raise serializers.ValidationError('Не в друзьях')
        return value

    def create(self, validated_data):
        dialog = services.GetterDialogs().get_group_sync(user=self.context['request'].user,
                                                         companion=validated_data['second_user_id'])
        return dialog


class ConservationSerializer(BaseGroupSerializer):
    members = UserSerializer(many=True, read_only=True)
    members_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, many=True)

    class Meta(BaseGroupSerializer.BaseMeta):
        model = models.Conservation

    def validate_members_id(self, value):
        user = self.context['request'].user
        check = all([val in user.friends.all() for val in value if val != user])
        if not check:
            raise serializers.ValidationError('Не в друзьях')
        return value

    def create(self, validated_data):
        owner = self.context['request'].user
        members = validated_data['members_id']
        conservation = models.Conservation.objects.create(owner=owner, name=validated_data['name'])

        if owner not in members:
            members.append(owner)

        conservation.members.set(members)
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

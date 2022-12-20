from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from rest_framework import serializers

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

    def create(self, validated_data):
        owner = self.context['request'].user
        second_user = validated_data['second_user_id']
        dialog = services.CreatorDialogs.create_group(owner=owner, second_user=second_user)
        return dialog

    def validate(self, attrs):
        owner = self.context['request'].user
        second_user = attrs.get('second_user_id')

        if services.GetterDialogs.get_group_sync(user=owner, companion=second_user):
            raise serializers.ValidationError('Диалог уже существует')

        return super().validate(attrs)

    def validate_second_user_id(self, value):
        user = self.context['request'].user

        if value == user:
            raise serializers.ValidationError('Нельзя начать диалог с собой')

        if value not in user.friends.all():
            raise serializers.ValidationError('Не в друзьях')
        return value


class ConservationSerializer(BaseGroupSerializer):
    members = UserSerializer(many=True, read_only=True)
    members_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, many=True)

    class Meta(BaseGroupSerializer.BaseMeta):
        model = models.Conservation

    def validate_members_id(self, value):
        user = self.context['request'].user

        not_in_friends = list(map(
            lambda friend: friend.username,
            filter(lambda friend: friend not in user.friends.all() and friend != user, value))
        )

        if any(not_in_friends):
            raise serializers.ValidationError({'not_in_friends': not_in_friends})
        return value

    def create(self, validated_data):
        owner = self.context['request'].user
        members = validated_data['members_id']
        conservation = services.CreatorConservations.create_group(owner=owner,
                                                                  name=validated_data['name'],
                                                                  members=members)
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

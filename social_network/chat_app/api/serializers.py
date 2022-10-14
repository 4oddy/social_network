from rest_framework import serializers

from main_app.api.serializers import UserSerializer

from .. import models


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
    class BaseMeta:
        model = models.AbstractMessage
        exclude = ('group', )
        read_only_fields = ('sender', )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['sender'] = self.context['request'].user.pk
        return data


class CreateDialogMessageSerializer(BaseCreatingMessageSerializer):
    class Meta(BaseCreatingMessageSerializer.BaseMeta):
        model = models.DialogMessage


class CreateConservationMessageSerializer(BaseCreatingMessageSerializer):
    class Meta(BaseCreatingMessageSerializer.BaseMeta):
        model = models.ConservationMessage

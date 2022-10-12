from rest_framework import serializers

from main_app.api.serializers import UserSerializer

from .. import models


class DialogSerializer(serializers.ModelSerializer):
    owner = UserSerializer()
    second_user = UserSerializer()

    class Meta:
        model = models.Dialog
        fields = '__all__'


class ConservationSerializer(serializers.ModelSerializer):
    owner = UserSerializer()
    members = UserSerializer(many=True)

    class Meta:
        model = models.Conservation
        fields = '__all__'


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
        fields = '__all__'
        extra_kwargs = {'sender': {'read_only': True}}

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

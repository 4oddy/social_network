from rest_framework import serializers

from django.contrib.auth import get_user_model

from main_app.models import FriendRequest
from main_app.services import create_friend_request

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'image', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'image', 'email')
        extra_kwargs = {'username': {'read_only': True}, 'email': {'read_only': True}}


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = '__all__'
        extra_kwargs = {'request_status': {'read_only': True}}

    def create(self, validated_data):
        request = create_friend_request(from_user=validated_data['from_user'], to_user_id=validated_data['to_user'].id)
        return request

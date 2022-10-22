from rest_framework import serializers

from django.contrib.auth import get_user_model

from main_app.models import FriendRequest, Post, Comment
from main_app.services import create_friend_request, find_friend_request

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'image', 'email', 'password', 'is_online', 'last_online',
                  'date_joined')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'image', 'email')
        read_only_fields = ('username', 'email')


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = '__all__'
        read_only_fields = ('request_status', 'from_user')

    def create(self, validated_data):
        request = create_friend_request(from_user=self.context['request'].user, to_user_id=validated_data['to_user'].id)
        return request

    def validate(self, attrs):
        from_user = self.context['request'].user
        to_user = attrs['to_user']

        if from_user == to_user:
            raise serializers.ValidationError('Отправитель заявки не может быть её получателем')

        if find_friend_request(from_user, to_user):
            raise serializers.ValidationError('Такая заявка уже существует')

        return super().validate(attrs)


class PostSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('owner', 'post')

from rest_framework import serializers

from django.contrib.auth import get_user_model

from ..models import FriendRequest, Post, Comment
from ..services import send_friend_request_email

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'username', 'image', 'email', 'password', 'is_online', 'last_online',
                  'date_joined')
        read_only_fields = ('date_joined', )
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
        request = FriendRequest.objects.create(from_user=self.context['request'].user,
                                               to_user=validated_data['to_user'])
        send_friend_request_email(from_user=request.from_user, to_user=request.to_user)
        return request

    def validate(self, attrs):
        from_user = self.context['request'].user
        to_user = attrs['to_user']

        if from_user == to_user:
            raise serializers.ValidationError('Отправитель заявки не может быть её получателем')

        if FriendRequest.find_friend_request(from_user, to_user):
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

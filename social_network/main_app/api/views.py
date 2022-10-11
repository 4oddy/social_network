from rest_framework import viewsets, mixins, permissions, status
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from django.db.models import Q

from . import serializers
from .permissions import IsInFriendRequest

from main_app.models import FriendRequest

User = get_user_model()


class UserView(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin):
    serializer_class = serializers.UserSerializer
    permission_classes = [
        permissions.AllowAny
    ]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return [self.request.user]

    def get_object(self):
        if self.request.user.is_authenticated:
            return self.request.user


class UserFriendsView(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = serializers.UserSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_queryset(self):
        return self.request.user.friends.all()


class FriendRequestView(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin,
                        mixins.DestroyModelMixin, mixins.RetrieveModelMixin):
    serializer_class = serializers.FriendRequestSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsInFriendRequest
    ]

    def get_queryset(self):
        queryset = FriendRequest.objects.filter(Q(from_user=self.request.user) | Q(to_user=self.request.user))
        return queryset

    def create(self, request, *args, **kwargs):
        from_user = self.request.data.get('from_user', self.request.user.pk)
        if self.request.user.pk == from_user:
            serializer = self.serializer_class(data=request.data)

            if serializer.is_valid():
                if serializer.create(validated_data=serializer.validated_data) is not None:
                    return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)

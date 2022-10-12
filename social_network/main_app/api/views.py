from rest_framework import viewsets, mixins, permissions, status
from rest_framework.response import Response

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Q

from . import serializers
from . import permissions as custom_permissions

from main_app.models import FriendRequest
from main_app.services import delete_from_friendship

User = get_user_model()


class UserView(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin):
    serializer_class = serializers.UserSerializer
    permission_classes = [
        permissions.AllowAny
    ]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return User.objects.all()

    def get_object(self):
        if self.kwargs['pk'] == '0':
            return self.request.user
        return get_object_or_404(User, pk=self.kwargs['pk'])


class UserUpdateView(viewsets.GenericViewSet, mixins.UpdateModelMixin):
    serializer_class = serializers.UserUpdateSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_object(self):
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
        custom_permissions.IsInFriendRequest
    ]

    def get_queryset(self):
        queryset = FriendRequest.objects.filter(Q(from_user=self.request.user) | Q(to_user=self.request.user))
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})

        if serializer.is_valid():
            if serializer.create(validated_data=serializer.validated_data) is not None:
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()

            if instance.request_status == instance.RequestStatuses.ACCEPTED:
                delete_from_friendship(first=instance.from_user, second=instance.to_user)
            else:
                if request.user == instance.from_user:
                    self.perform_destroy(instance)
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)

        except Exception:
            pass
        return Response(status=status.HTTP_204_NO_CONTENT)


class AcceptFriendRequestView(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = serializers.AcceptOrDenyFriendRequestSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            from_user = serializer.validated_data.get('from_user')
            to_user = request.user

            request = get_object_or_404(FriendRequest, from_user=from_user, to_user=to_user)
            request.accept()
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DenyFriendRequestView(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = serializers.AcceptOrDenyFriendRequestSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            from_user = serializer.validated_data.get('from_user')
            to_user = request.user

            request = get_object_or_404(FriendRequest, from_user=from_user, to_user=to_user)
            request.deny()
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

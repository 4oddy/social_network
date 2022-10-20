from rest_framework import viewsets, mixins, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.db.models import Q

from . import serializers
from . import permissions as custom_permissions

from main_app.models import FriendRequest
from main_app.services import delete_from_friendship, send_email_changed_settings

User = get_user_model()


class UserView(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin):
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return User.objects.all()

    def get_object(self):
        self.serializer_class = serializers.UserUpdateSerializer
        self.permission_classes.append(permissions.IsAuthenticated)

        if self.request.user.is_authenticated:
            if self.kwargs['pk'] == '0':
                return self.request.user
            return get_object_or_404(User, pk=self.kwargs['pk'])

    def get_permissions(self):
        permission_classes = [
            permissions.AllowAny,
        ]

        if self.action == 'update_user' or self.action == 'friends':
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'update_user':
            return serializers.UserUpdateSerializer
        return serializers.UserSerializer

    @action(detail=False, methods=['PUT', 'PATCH'])
    def update_user(self, request):
        serializer = self.get_serializer(instance=request.user, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        send_email_changed_settings(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'])
    def friends(self, request):
        serializer = self.get_serializer(request.user.friends.all(), many=True)
        return Response(serializer.data)


class FriendRequestView(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin,
                        mixins.DestroyModelMixin, mixins.RetrieveModelMixin):
    serializer_class = serializers.FriendRequestSerializer

    def get_queryset(self):
        queryset = FriendRequest.objects.filter(Q(from_user=self.request.user) | Q(to_user=self.request.user))
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})

        if serializer.is_valid():
            request = serializer.create(validated_data=serializer.validated_data)
            if request is not None:
                return Response(serializer.to_representation(request), status=status.HTTP_201_CREATED)
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

    def get_permissions(self):
        permission_classes = [
            permissions.IsAuthenticated,
            custom_permissions.IsInFriendRequest
        ]

        if self.action in ('accept', 'deny'):
            permission_classes.append(custom_permissions.CanAcceptOrDenyFriendRequest)
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['GET'])
    def accept(self, request, pk=None):
        friend_request = self.get_object()
        friend_request.accept()
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'])
    def deny(self, request, pk=None):
        friend_request = self.get_object()
        friend_request.deny()
        return Response(status=status.HTTP_200_OK)

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from main_app.models import Comment, FriendRequest, Post
from main_app.services import (delete_from_friendship,
                               send_email_changed_settings)

from ..services import send_friend_request_email
from . import permissions as custom_permissions
from . import serializers

User = get_user_model()


class UserView(viewsets.GenericViewSet, mixins.ListModelMixin,
               mixins.CreateModelMixin, mixins.RetrieveModelMixin):
    queryset = User.objects.all()

    def get_object(self):
        if self.kwargs['pk'] == '0':
            return self.request.user
        return get_object_or_404(User, pk=self.kwargs['pk'])

    def get_permissions(self):
        permission_classes = [
            permissions.AllowAny,
        ]

        if self.action in ('update_user', 'delete_profile_image',
                           'friends', 'retrieve', 'list'):
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action in ('update_user', ):
            return serializers.UserUpdateSerializer
        return serializers.UserSerializer

    @action(detail=False, methods=['PUT', 'PATCH'], url_name='update_user')
    def update_user(self, request):
        serializer = self.get_serializer(instance=request.user,
                                         data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        send_email_changed_settings(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'], url_name='delete_profile_image')
    def delete_profile_image(self, request):
        if request.user.image != settings.DEFAULT_USER_IMAGE:
            request.user.image = settings.DEFAULT_USER_IMAGE
            request.user.save()
            return Response({'success': True})
        return Response({'success': False},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['GET'], url_name='friends')
    def friends(self, request, pk=None):
        serializer = self.get_serializer(self.get_object().friends.all(), many=True)
        return Response(serializer.data)


class FriendRequestView(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin,
                        mixins.DestroyModelMixin, mixins.RetrieveModelMixin):
    serializer_class = serializers.FriendRequestSerializer

    def perform_create(self, serializer):
        obj = serializer.save(from_user=self.request.user)
        send_friend_request_email(from_user=obj.from_user, to_user=obj.to_user)

    def get_queryset(self):
        queryset = FriendRequest.objects.filter(Q(from_user=self.request.user)
                                                | Q(to_user=self.request.user))
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.request_status == instance.RequestStatuses.ACCEPTED:
            delete_from_friendship(first=instance.from_user,
                                   second=instance.to_user)
        else:
            if request.user == instance.from_user:
                self.perform_destroy(instance)
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_permissions(self):
        permission_classes = [
            permissions.IsAuthenticated
        ]

        if self.action in ('accept', 'deny'):
            permission_classes.append(custom_permissions.CanAcceptOrDenyFriendRequest)
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['GET'], url_name='accept')
    def accept(self, request, pk=None):
        friend_request = self.get_object()

        if not friend_request.is_accepted:
            friend_request.accept()
            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={'error': 'Заявка уже принята'})

    @action(detail=True, methods=['GET'], url_name='deny')
    def deny(self, request, pk=None):
        friend_request = self.get_object()

        if not friend_request.is_denied and not friend_request.is_accepted:
            friend_request.deny()
            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST,
                        data={'error': 'Заявка уже отклонена или принята'})


class PostView(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_serializer_class(self):
        if self.action in ('comments', 'leave_comment'):
            return serializers.CommentSerializer
        return serializers.PostSerializer

    def get_permissions(self):
        permission_classes = [
            permissions.IsAuthenticated
        ]

        if self.action != 'leave_comment':
            permission_classes.append(custom_permissions.CanEditOrDeletePost)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if self.action == 'comments':
            return Comment.objects.select_related('owner', 'post').\
                filter(post=self.kwargs['pk'])
        return Post.objects.select_related('owner').all()

    @action(detail=False, methods=['GET'], url_name='friends_posts')
    def friends_posts(self, request):
        serializer = self.get_serializer(self.get_queryset().
                                         friends_posts(request.user), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['GET'], url_name='user_posts')
    def user_posts(self, request):
        serializer = self.get_serializer(self.get_queryset().
                                         get_posts(request.user), many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CommentSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user,
                        post=self._get_post_by_pk(self.kwargs['post_id']))

    def get_queryset(self):
        return Comment.objects.select_related('owner', 'post').\
            filter(post=self.kwargs['post_id'])

    @staticmethod
    def _get_post_by_pk(pk):
        return get_object_or_404(Post, pk=pk)

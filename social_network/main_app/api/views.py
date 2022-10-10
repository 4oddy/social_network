from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import permissions

from django.contrib.auth import get_user_model

from .serializers import UserSerializer

User = get_user_model()


class UserView(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [
        permissions.AllowAny
    ]


class UserFriendsView(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = UserSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_queryset(self):
        return self.request.user.friends.all()

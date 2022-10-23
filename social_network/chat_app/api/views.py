from rest_framework import viewsets, mixins, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from . import serializers
from .. import services


class BaseGroupView(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    permission_classes = [
        permissions.IsAuthenticated
    ]

    _getter: services.AbstractGetter

    _creating_message_serializer: serializers.BaseCreatingMessageSerializer
    _group_serializer: serializers.BaseGroupSerializer

    def get_queryset(self):
        return self._getter.get_user_groups(self.request.user)

    def get_serializer_class(self):
        if self.action == 'send_message':
            return self._creating_message_serializer
        return self._group_serializer

    @action(detail=True, methods=['POST'])
    def send_message(self, request, pk=None):
        group = self.get_object()
        serializer = self.get_serializer(data=request.data, context={'request': request, 'group': group})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class DialogView(BaseGroupView, mixins.CreateModelMixin):
    _getter = services.GetterDialogs()

    _creating_message_serializer = serializers.CreateDialogMessageSerializer
    _group_serializer = serializers.DialogSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request, 'creating': True})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'id': serializer.data['id'], 'success': True})


class ConservationView(BaseGroupView, mixins.CreateModelMixin):
    _getter = services.GetterConservations()

    _creating_message_serializer = serializers.CreateConservationMessageSerializer
    _group_serializer = serializers.ConservationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'id': serializer.data['id'], 'success': True})

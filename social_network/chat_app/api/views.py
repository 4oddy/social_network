from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .. import models, services
from . import serializers


class BaseGroupView(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                    mixins.CreateModelMixin):
    permission_classes = [
        permissions.IsAuthenticated
    ]

    _getter: services.AbstractGetter

    _message_model: models.AbstractMessage

    _message_serializer: serializers.BaseMessageSerializer
    _creating_message_serializer: serializers.BaseCreatingMessageSerializer
    _group_serializer: serializers.BaseGroupSerializer

    def get_queryset(self):
        return self._getter.get_user_groups(self.request.user)

    def get_serializer_class(self):
        if self.action == 'send_message':
            return self._creating_message_serializer
        elif self.action == 'group_messages':
            return self._message_serializer
        return self._group_serializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'id': serializer.data['id'], 'success': True}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['POST'], url_name='send_message')
    def send_message(self, request, pk=None):
        group = self.get_object()
        serializer = self.get_serializer(data=request.data, context={'request': request, 'group': group})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['GET'], url_name='group_messages')
    def group_messages(self, request, pk=None):
        group = self.get_object()
        serializer = self.get_serializer(self._message_model.objects.filter(group=group), many=True)
        return Response(serializer.data)


class DialogView(BaseGroupView):
    _getter = services.GetterDialogs()

    _message_model = models.DialogMessage

    _message_serializer = serializers.DialogMessageSerializer
    _creating_message_serializer = serializers.CreateDialogMessageSerializer
    _group_serializer = serializers.DialogSerializer


class ConservationView(BaseGroupView):
    _getter = services.GetterConservations()

    _message_model = models.ConservationMessage

    _message_serializer = serializers.ConservationMessageSerializer
    _creating_message_serializer = serializers.CreateConservationMessageSerializer
    _group_serializer = serializers.ConservationSerializer

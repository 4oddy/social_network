from rest_framework import viewsets, mixins, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from asgiref.sync import async_to_sync

from . import serializers, permissions as custom_permissions
from .. import services, exceptions


class BaseGroupView(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    _saver: services.AbstractSaver
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
        dialog = self.get_object()

        serializer = self.get_serializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            sender = services.SenderMessages(saver=self._saver)

            try:
                async_to_sync(sender.send_message)(sender=request.user,
                                                   message=serializer.validated_data['text'],
                                                   group=dialog)
            except exceptions.UserNotInGroup:
                return Response(status=status.HTTP_403_FORBIDDEN)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors)


class DialogView(BaseGroupView):
    _saver = services.SaverDialogMessages()
    _getter = services.GetterDialogs()

    _creating_message_serializer = serializers.CreateDialogMessageSerializer
    _group_serializer = serializers.DialogSerializer


class ConservationView(BaseGroupView):
    _saver = services.SaverConservationMessages()
    _getter = services.GetterConservations()

    _creating_message_serializer = serializers.CreateConservationMessageSerializer
    _group_serializer = serializers.ConservationSerializer

from rest_framework import viewsets, mixins, permissions, status
from rest_framework.response import Response

from asgiref.sync import async_to_sync

from . import serializers
from .. import services, exceptions


class DialogView(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = serializers.DialogSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_queryset(self):
        return services.GetterDialogs.get_user_dialogs(self.request.user)


class ConservationView(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = serializers.ConservationSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get_queryset(self):
        return services.GetterConservations.get_user_conservations(self.request.user)


class BaseSendMessageView(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = serializers.BaseCreatingMessageSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]
    saver: services.AbstractSaver

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})

        if serializer.is_valid():
            sender = services.SenderMessages(saver=self.saver)

            try:
                async_to_sync(sender.send_message)(sender=request.user,
                                                   message=serializer.validated_data['text'],
                                                   group=serializer.validated_data['group'])
            except exceptions.UserNotInGroup:
                return Response(status=status.HTTP_403_FORBIDDEN)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        return Response(data=serializer.errors)


class SendDialogMessageView(BaseSendMessageView):
    serializer_class = serializers.CreateDialogMessageSerializer
    saver = services.SaverDialogMessages()


class SendConservationMessageView(BaseSendMessageView):
    serializer_class = serializers.CreateConservationMessageSerializer
    saver = services.SaverConservationMessages()

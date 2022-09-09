from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

from .models import ConservationMessage, Conservation, DialogMessage, Dialog
from .services import GetterDialogs

User = get_user_model()

getter = GetterDialogs()


class ConservationPage(LoginRequiredMixin, TemplateView):
    template_name = 'chat_page.html'

    def get_context_data(self, **kwargs):
        context: dict = super().get_context_data()

        group_name: str = self.kwargs['group_name']

        context['group_type']: str = 'conservation'
        context['group_name']: str = group_name
        context['conservation'] = get_object_or_404(Conservation, name=group_name)
        context['messages']: ConservationMessage = ConservationMessage.objects.select_related('sender').filter(
            group__name=group_name)

        return context


class DialogPage(LoginRequiredMixin, TemplateView):
    template_name = 'chat_page.html'

    def get_context_data(self, **kwargs):
        context: dict = super().get_context_data()

        companion_name: str = self.kwargs['companion_name']

        context['group_type']: str = 'dialog'
        context['group_name']: str = companion_name

        dialog: Dialog = getter.get_group_sync(user=self.request.user,
                                               companion_name=companion_name)
        if dialog:
            context['dialog'] = dialog
            context['companion'] = dialog.owner if self.request.user != dialog.owner else dialog.second_user

            context['messages']: DialogMessage = DialogMessage.objects.select_related('sender').\
                filter(group__owner=dialog.owner,
                       group__second_user=dialog.second_user)

        return context

    def get(self, *args, **kwargs):
        companion_name = self.kwargs['companion_name']

        if self.request.user.username == companion_name:
            return HttpResponseBadRequest()

        second_user = get_object_or_404(User, username=companion_name)

        if second_user in self.request.user.friends.all() and self.request.user in second_user.friends.all():
            return super().get(*args, **kwargs)

        return HttpResponseForbidden('Вы не в друзьях с ' + companion_name)

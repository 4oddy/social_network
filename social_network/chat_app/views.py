from django.http import HttpResponseBadRequest
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
        context['group']: Conservation = get_object_or_404(Conservation, name=group_name)
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

        dialog: Dialog = getter.get_group_sync(user=self.request.user, companion_name=companion_name)

        context['messages']: DialogMessage = DialogMessage.objects.select_related('sender').\
            filter(group__owner=dialog.owner,
                   group__second_user=dialog.second_user)

        return context

    def get(self, *args, **kwargs):
        if self.request.user.username == self.kwargs['companion_name']:
            return HttpResponseBadRequest()
        return super().get(*args, **kwargs)

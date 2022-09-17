from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model

from .models import ConservationMessage, Conservation, DialogMessage, Dialog
from .services import GetterDialogs, GetterConservations

User = get_user_model()

getter_dialogs = GetterDialogs()


class ConservationPage(LoginRequiredMixin, TemplateView):
    template_name = 'chat_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        group_name = self.kwargs['group_name']

        context['group_type'] = 'conservation'
        context['group_name'] = group_name
        context['conservation'] = get_object_or_404(Conservation, name=group_name)
        context['messages'] = ConservationMessage.objects.select_related('sender').filter(
            group__name=group_name)

        return context


class DialogPage(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        context = dict()

        companion_name = self.kwargs['companion_name']

        context['group_type'] = 'dialog'
        context['group_name'] = companion_name

        if self.request.user.username == companion_name:
            return HttpResponseBadRequest()

        second_user = get_object_or_404(User, username=companion_name)

        if second_user in self.request.user.friends.all() and self.request.user in second_user.friends.all():
            dialog: Dialog = getter_dialogs.get_group_sync(user=self.request.user, companion=second_user)

            context['dialog'] = dialog
            context['companion'] = dialog.get_companion(user=self.request.user)

            context['messages'] = DialogMessage.objects.select_related('sender'). \
                filter(group__owner=dialog.owner,
                       group__second_user=dialog.second_user)

            return render(self.request, 'chat_page.html', context=context)

        return HttpResponseForbidden('Вы не в друзьях с ' + companion_name)


class UserGroupsPage(LoginRequiredMixin, TemplateView):
    template_name = 'groups_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user

        user_conservations = GetterConservations.get_user_conservations(user)
        user_dialogs = getter_dialogs.get_user_dialogs(user)

        context['conservations'] = user_conservations
        context['dialogs'] = user_dialogs

        return context

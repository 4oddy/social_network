from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.generic import CreateView, TemplateView, View

from .forms import CreateConservationForm
from .models import Conservation, ConservationMessage, DialogMessage
from .services import CreatorDialogs, GetterConservations, GetterDialogs

User = get_user_model()

getter_dialogs = GetterDialogs()
getter_conservations = GetterConservations()

creator_dialogs = CreatorDialogs()


class ConservationPage(LoginRequiredMixin, TemplateView):
    template_name = 'chat_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        uid = self.kwargs['group_uuid']

        conservation = get_object_or_404(Conservation, uid=uid)

        context['group_type'] = 'conservation'
        context['group_name'] = uid
        context['conservation'] = conservation
        context['messages'] = ConservationMessage.objects.select_related('sender').filter(group=conservation)

        return context

    def render_to_response(self, context, **response_kwargs):
        if self.request.user not in context['conservation'].members.all():
            return HttpResponseForbidden('Пользователь не состоит в беседе')
        return super().render_to_response(context, **response_kwargs)


class DialogPage(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        context = dict()

        companion_name = self.kwargs['companion_name']

        if self.request.user.username == companion_name:
            return HttpResponseBadRequest('Пользователь не может начать диалог сам с собой')

        context['group_type'] = 'dialog'
        context['group_name'] = companion_name

        second_user = get_object_or_404(User, username=companion_name)

        if User.in_friendship(self.request.user, second_user):
            dialog = getter_dialogs.get_group_sync(user=self.request.user, companion=second_user)
            if not dialog:
                dialog = creator_dialogs.create_group(owner=self.request.user, second_user=second_user)
            context['dialog'] = dialog
            context['companion'] = dialog.get_companion(user=self.request.user)
            context['messages'] = DialogMessage.objects.select_related('sender').filter(group=dialog)
            return render(self.request, 'chat_page.html', context=context)
        return HttpResponseForbidden('Вы не в друзьях с ' + companion_name)


class UserGroupsPage(LoginRequiredMixin, TemplateView):
    template_name = 'groups_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user

        user_conservations = getter_conservations.get_user_groups(user)
        user_dialogs = getter_dialogs.get_user_groups(user)

        context['conservations'] = user_conservations
        context['dialogs'] = user_dialogs
        return context


class CreateConservationPage(LoginRequiredMixin, CreateView):
    template_name = 'create_conservation_page.html'
    form_class = CreateConservationForm

    def get_form(self, form_class=None):
        form = self.get_form_class()(self.request.POST if self.request.POST else None)
        form.fields['members'].queryset = self.request.user.friends.all()
        return form

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.owner = self.request.user
        obj.save()

        form.save_m2m()

        obj.members.add(self.request.user)
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('chat:groups_page')

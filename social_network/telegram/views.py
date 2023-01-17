from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.http import HttpResponseBadRequest

from .tg.tokens import generate_authentication_token


class GenerateTokenView(LoginRequiredMixin, TemplateView):
    template_name = 'generate_token_tg.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['token'] = generate_authentication_token(self.request.user)
        return context

    def get(self, request, *args, **kwargs):
        if getattr(request.user, 'telegram_profile', None) is None:
            return super().get(request, *args, **kwargs)
        return HttpResponseBadRequest()

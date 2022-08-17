from django.views.generic.edit import CreateView

from .forms import MessageForm


class Chat(CreateView):
    template_name = 'chat_page.html'
    form_class = MessageForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        username = self.kwargs['username']
        context['username'] = username
        return context

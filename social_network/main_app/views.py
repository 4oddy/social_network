from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import View, DetailView
from django.contrib.auth.views import LoginView
from django.contrib.auth import login as auth_login
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, reverse

from .models import FriendRequest, Post
from .forms import (CustomUserCreationForm, FindUserForm, CustomAuthenticationForm,
                    UserSettingsForm, PostCreatingForm)
from .tasks import send_email
from .services import find_users, find_friend_request
from .utils import get_current_date

User = get_user_model()


# func to get data from hidden form's fields
def get_data_for_action(request):
    user_path = request.POST['current_path']
    from_user_id = request.user.pk
    from_user = request.user
    to_user_id = request.POST['user_id']

    return {'user_path': user_path, 'from_user_id': from_user_id, 'from_user': from_user,
            'to_user_id': to_user_id}


def get_username_from_kwargs(kwargs):
    return kwargs['username'].replace('@', '')


class MainPage(TemplateView):
    template_name = 'main_page.html'


class UserProfilePage(LoginRequiredMixin, TemplateView):
    template_name = 'user_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        from_user = self.request.user
        to_user_username = get_username_from_kwargs(self.kwargs)

        # if it is profile of request's user
        own_profile = context['own_profile'] = from_user.username == to_user_username

        context['posts'] = None

        if own_profile:
            user = from_user
            context['profile'] = user

        else:
            user = get_object_or_404(User.objects.prefetch_related('friends'), username=to_user_username)
            context['profile'] = user

        friends = user.friends.all()

        if friends is None:
            context['friend_amount'] = 0
        else:
            context['friend_amount'] = len(friends)
            context['friends'] = friends

        if not own_profile:
            context['in_friendship'] = False
            context['already_requested'] = False
            context['requested_to_you'] = False

            # checking for friend request from request user
            req = FriendRequest.objects.filter(from_user=from_user, to_user=user).first()
            req_status = req.request_status if req else None

            if req and req_status == 'c' or req_status == 'd':
                context['already_requested'] = True
                context['request_status'] = req_status

            else:
                # checking for friend request from page being viewed
                req = FriendRequest.objects.filter(from_user=user, to_user=from_user).first()
                req_status = req.request_status if req else None

                if req and req_status != 'a':
                    context['requested_to_you'] = True

                # if in friendship
                elif friends and from_user in friends:
                    context['in_friendship'] = True

        posts = Post.objects.select_related('owner').filter(owner=user)

        if posts.exists():
            context['posts'] = posts[::-1]

        return context


class FriendsListPage(LoginRequiredMixin, TemplateView):
    template_name = 'friends_page.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        username = get_username_from_kwargs(self.kwargs)

        if self.request.user.username != username:
            user = get_object_or_404(User.objects.prefetch_related('friends'), username=username)
        else:
            user = self.request.user

        context['profile'] = user
        context['friends'] = user.friends.all()

        return context


class RegisterUserPage(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'register_user_page.html'
    success_url = '/'


class UserSettingsPage(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'user_settings.html'
    form_class = UserSettingsForm

    def get(self, request, *args, **kwargs):
        self.object = request.user
        return super().get(request, *args, **kwargs)

    def get_object(self, *args, **kwargs):
        return self.request.user

    def post(self, request, *args, **kwargs):
        user = request.user

        if settings.SEND_EMAILS:
            name = user.first_name

            if not name:
                name = user.username

            email_body = settings.DEFAULT_EMAIL_SETTINGS_CHANGED_BODY.format(name=name, date=get_current_date())

            send_email.delay(subject=settings.DEFAULT_EMAIL_SETTINGS_CHANGED_SUBJECT, body=email_body, to=[user.email])

        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('main:user_page', kwargs={'username': self.request.user.username})


class CustomLoginPage(LoginView):
    template_name = 'login_page.html'
    form_class = CustomAuthenticationForm

    def form_valid(self, form):
        """Security check complete. Log the user in."""
        user = form.get_user()
        auth_login(self.request, user)

        if settings.SEND_EMAILS:
            name = user.first_name
            username = user.username

            if not name:
                name = user.username

            email_body = settings.DEFAULT_EMAIL_LOGIN_BODY.format(name=name, username=username, date=get_current_date())

            send_email.delay(subject=settings.DEFAULT_EMAIL_LOGIN_SUBJECT, body=email_body, to=[user.email])

        return HttpResponseRedirect(self.get_success_url())


class FindUserPage(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        form = FindUserForm()
        context = {'form': form}
        return render(self.request, 'find_user_page.html', context)

    def post(self, *args, **kwargs):
        context = {}
        form = FindUserForm(self.request.POST)
        context['form'] = form

        if form.is_valid():
            username = form.cleaned_data['username'].lower()

            context['user_exists'] = False
            context['more_than_one'] = False

            users_queryset = find_users(username)

            if len(users_queryset) > 0:
                context['user_exists'] = True

                if len(users_queryset) > 1:
                    context['more_than_one'] = True

                context['users'] = users_queryset

        return render(self.request, 'find_user_page.html', context)


class CreateFriendRequest(LoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        data = get_data_for_action(self.request)

        FriendRequest.objects.create(from_user_id=data['from_user_id'], to_user_id=data['to_user_id'])

        if settings.SEND_EMAILS:
            from_user = User.objects.filter(pk=data['from_user_id']).first()
            to_user = User.objects.get(pk=data['to_user_id']).first()

            name = to_user.first_name

            if not name:
                name = to_user.username

            username = from_user.username

            email_body = settings.DEFAULT_EMAIL_FRIEND_REQUEST_BODY.format(name=name, name_requested=username,
                                                                           date=get_current_date())

            send_email.delay(subject=settings.DEFAULT_EMAIL_FRIEND_REQUEST_SUBJECT, body=email_body, to=[to_user.email])

        return redirect(data['user_path'])


class CancelFriendRequest(LoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        data = get_data_for_action(self.request)
        req = FriendRequest.objects.filter(from_user_id=data['from_user_id'], to_user_id=data['to_user_id']).first()

        if req:
            req.delete()

        return redirect(data['user_path'])


class AcceptFriendRequest(LoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        data = get_data_for_action(self.request)
        req = FriendRequest.objects.filter(from_user_id=data['to_user_id'], to_user=data['from_user']).first()

        if req:
            req.accept()

        return redirect(data['user_path'])


class DenyFriendRequest(LoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        data = get_data_for_action(self.request)
        req = FriendRequest.objects.filter(from_user_id=data['to_user_id'], to_user_id=data['from_user_id']).first()

        if req:
            req.deny()

        return redirect(data['user_path'])


class DeleteFriend(LoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        data = get_data_for_action(self.request)
        user = get_object_or_404(User, pk=data['to_user_id'])

        request = find_friend_request(data['from_user'], user)

        if data['from_user'] in user.friends.all() and user in data['from_user'].friends.all():
            user.friends.remove(data['from_user'])
            data['from_user'].friends.remove(user)

        request.delete() if request else None

        return redirect(data['user_path'])


class CreatePost(LoginRequiredMixin, CreateView):
    form_class = PostCreatingForm
    template_name = 'post_creating.html'

    def form_valid(self, form):
        user = self.request.user
        obj = form.save(commit=False)
        obj.owner = user
        obj.save()
        return redirect(reverse('main:user_page', kwargs={'username': user.username}))


class PostPage(LoginRequiredMixin, DetailView):
    template_name = 'post_page.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        return get_object_or_404(Post.objects.select_related('owner'), post_uuid=self.kwargs['post_uuid'])

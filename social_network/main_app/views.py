from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import View, DetailView
from django.contrib.auth.views import LoginView
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, reverse
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseBadRequest

from .models import FriendRequest, Post

from .forms import (CustomUserCreationForm, FindUserForm, CustomAuthenticationForm,
                    UserSettingsForm, PostCreatingForm, PostEditingForm)

from .services import (find_users, get_data_for_action,
                       get_username_from_kwargs, create_friend_request, send_email_login,
                       send_email_changed_settings, delete_from_friendship)

User = get_user_model()


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
            context['allowed_to_edit'] = True if own_profile else False

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

    def get_object(self, *args, **kwargs):
        return self.request.user

    def post(self, request, *args, **kwargs):
        send_email_changed_settings(request.user)

        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('main:user_page', kwargs={'username': self.request.user.username})


class DeleteProfileImage(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        if self.request.user.image != settings.DEFAULT_USER_IMAGE:
            self.request.user.image = settings.DEFAULT_USER_IMAGE
            self.request.user.save()
            return HttpResponse()
        return HttpResponseBadRequest()


class CustomLoginPage(LoginView):
    template_name = 'login_page.html'
    form_class = CustomAuthenticationForm


class FindUserPage(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        context = {}
        form = FindUserForm({'username': self.request.GET.get('username')})

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

        create_friend_request(from_user=data['from_user'], to_user_id=data['to_user_id'])

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

        delete_from_friendship(data['from_user'], user)

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allowed_to_edit'] = False

        if self.request.user == self.get_object().owner:
            context['allowed_to_edit'] = True

        return context


class DeletePostPage(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'delete_post_page.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        return get_object_or_404(Post.objects.select_related('owner'), post_uuid=self.kwargs['post_uuid'])

    def get_success_url(self):
        return reverse('main:user_page', kwargs={'username': self.request.user})

    def render_to_response(self, context, **response_kwargs):
        if self.request.user == self.get_object().owner:
            return super().render_to_response(context, **response_kwargs)
        return HttpResponseForbidden('Вы не можете удалить эту запись')


class EditPostPage(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'edit_post_page.html'
    form_class = PostEditingForm
    context_object_name = 'post'

    def get_object(self, queryset=None):
        return get_object_or_404(Post.objects.select_related('owner'), post_uuid=self.kwargs['post_uuid'])

    def get_success_url(self):
        return reverse('main:user_page', kwargs={'username': self.request.user})

    def render_to_response(self, context, **response_kwargs):
        if self.request.user == self.get_object().owner:
            return super().render_to_response(context, **response_kwargs)
        return HttpResponseForbidden('Вы не можете изменять эту запись')

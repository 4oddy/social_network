from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import View, DetailView, TemplateView
from django.contrib.auth.views import LoginView
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseBadRequest
from django.contrib.auth import get_user_model

from .models import FriendRequest, Post, Comment

from .forms import (CustomUserCreationForm, FindUserForm, CustomAuthenticationForm,
                    UserSettingsForm, PostCreatingForm, PostEditingForm, CommentForm,
                    FriendRequestForm)

from .services import (find_users, get_data_for_action,
                       get_username_from_kwargs, send_email_changed_settings,
                       delete_from_friendship, get_request_info, get_user_for_view)

User = get_user_model()


class MainPage(LoginRequiredMixin, TemplateView):
    template_name = 'main_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.select_related('owner').friends_posts(self.request.user)
        return context


class UserProfilePage(LoginRequiredMixin, TemplateView):
    template_name = 'user_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        from_user = self.request.user
        to_user_username = get_username_from_kwargs(self.kwargs)

        own_profile = context['own_profile'] = from_user.username == to_user_username

        user = get_user_for_view(from_user=from_user, to_user_username=to_user_username)
        friends = user.friends.all()

        context['profile'] = user
        context['friends'], context['friends_amount'] = friends, len(friends)

        if not own_profile:
            already_friends = context['in_friendship'] = User.in_friendship(from_user, user)

            if not already_friends:
                request_info = get_request_info(from_user, user)
                context = context | request_info

        posts = Post.objects.select_related('owner').get_posts(user)

        context['posts'] = posts
        context['allowed_to_edit'] = True if own_profile else False

        return context


class FriendsListPage(LoginRequiredMixin, TemplateView):
    template_name = 'friends_page.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)

        username = get_username_from_kwargs(self.kwargs)

        user = get_user_for_view(from_user=self.request.user, to_user_username=username)

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

        form = FriendRequestForm(data={'from_user': data['from_user'], 'to_user': data['to_user_id']})

        if form.is_valid():
            form.save()

        return redirect(data['user_path'])


class CancelFriendRequest(LoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        data = get_data_for_action(self.request)

        if data['to_user_id']:
            req = FriendRequest.objects.filter(from_user=data['from_user'], to_user_id=data['to_user_id']).first()

            if req:
                req.delete()

        return redirect(data['user_path'])


class AcceptFriendRequest(LoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        data = get_data_for_action(self.request)

        if data['to_user_id']:
            req = FriendRequest.objects.filter(from_user_id=data['to_user_id'], to_user=data['from_user']).first()

            if req:
                req.accept()

        return redirect(data['user_path'])


class DenyFriendRequest(LoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        data = get_data_for_action(self.request)

        if data['to_user_id']:
            req = FriendRequest.objects.filter(from_user_id=data['to_user_id'], to_user=data['from_user']).first()

            if req:
                req.deny()

        return redirect(data['user_path'])


class DeleteFriend(LoginRequiredMixin, View):
    def post(self, *args, **kwargs):
        data = get_data_for_action(self.request)

        if data['to_user_id']:
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

        if self.request.user == self.get_object().owner:
            context['allowed_to_edit'] = True

        comments = Comment.objects.select_related('owner').filter(post__post_uuid=self.kwargs['post_uuid'])
        context['comments'] = comments

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


class CreateComment(LoginRequiredMixin, CreateView):
    template_name = 'comment_creating_page.html'
    form_class = CommentForm

    def form_valid(self, form):
        user = self.request.user
        obj = form.save(commit=False)
        obj.owner = user
        obj.post = get_object_or_404(Post, post_uuid=self.kwargs['post_uuid'])
        obj.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('main:post_page', kwargs={'post_uuid': self.kwargs['post_uuid']})

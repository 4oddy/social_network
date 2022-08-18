from django.urls import path, reverse_lazy
from django.contrib.auth.views import LogoutView, PasswordResetView, PasswordResetConfirmView, PasswordResetDoneView

from .views import (UserProfilePage, MainPage, RegisterUserPage,
                    FindUserPage, CreateFriendRequest, CancelFriendRequest,
                    AcceptFriendRequest, DenyFriendRequest, DeleteFriend,
                    FriendsListPage, CustomLoginPage, UserSettingsPage, CreatePost,
                    PostPage, DeletePostPage, EditPostPage)

from .forms import CustomPasswordResetForm

app_name = 'main'


urlpatterns = [
    path('', MainPage.as_view(), name='main_page'),

    path('<str:username>/', UserProfilePage.as_view(), name='user_page'),
    path('<str:username>/friends/', FriendsListPage.as_view(), name='friends_page'),

    path('accounts/find_user/', FindUserPage.as_view(), name='find_user'),
    path('accounts/login/', CustomLoginPage.as_view(), name='login_page'),
    path('accounts/logout/', LogoutView.as_view(), name='logout_page'),
    path('accounts/register/', RegisterUserPage.as_view(), name='register_page'),
    path('accounts/settings/', UserSettingsPage.as_view(), name='user_settings_page'),
    path('accounts/change_password/', PasswordResetView.as_view(template_name='password/change_password.html',
                                                                email_template_name=
                                                                'password/password_reset_email.html',
                                                                subject_template_name=
                                                                'password/password_reset_subject.txt',
                                                                form_class=CustomPasswordResetForm,
                                                                success_url=reverse_lazy('main:password_reset_done')),
         name='change_password_page'),

    path('accounts/password_reset_done/',
         PasswordResetDoneView.as_view(template_name='password/password_reset_done.html'), name='password_reset_done'),

    path('accounts/password_reset_confirm/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(success_url='/', template_name='password/password_reset.html'),
         name='password_reset_confirm'),

    path('actions/add_friend/', CreateFriendRequest.as_view(), name='create_friend_request'),
    path('actions/cancel_request/', CancelFriendRequest.as_view(), name='cancel_friend_request'),
    path('actions/accept_request/', AcceptFriendRequest.as_view(), name='accept_friend_request'),
    path('actions/deny_request/', DenyFriendRequest.as_view(), name='deny_friend_request'),
    path('actions/delete_friend/', DeleteFriend.as_view(), name='delete_friend'),

    path('posts/create_post/', CreatePost.as_view(), name='create_post'),
    path('posts/<slug:post_uuid>/', PostPage.as_view(), name='post_page'),
    path('posts/<slug:post_uuid>/delete/', DeletePostPage.as_view(), name='delete_post_page'),
    path('posts/<slug:post_uuid>/edit/', EditPostPage.as_view(), name='edit_post_page')
]

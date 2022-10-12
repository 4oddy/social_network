from rest_framework.routers import DefaultRouter

from . import views


accounts_router = DefaultRouter()
friend_requests_router = DefaultRouter()

accounts_router.register('users', views.UserView, basename='user')
accounts_router.register('user_update', views.UserUpdateView, basename='user_update')
accounts_router.register('user_friends', views.UserFriendsView, basename='friends')

friend_requests_router.register('friend_requests', views.FriendRequestView, basename='request')
friend_requests_router.register('accept_friend_request', views.AcceptFriendRequestView, basename='accept_request')
friend_requests_router.register('deny_friend_request', views.DenyFriendRequestView, basename='dent_request')

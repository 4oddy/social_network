from rest_framework.routers import DefaultRouter

from . import views


accounts_router = DefaultRouter()
friend_requests_router = DefaultRouter()

accounts_router.register('user', views.UserView, basename='user')
accounts_router.register('user_friends', views.UserFriendsView, basename='friends')

friend_requests_router.register('friend_requests', views.FriendRequestView, basename='request')

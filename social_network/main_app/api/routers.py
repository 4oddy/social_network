from rest_framework.routers import DefaultRouter

from . import views


accounts_router = DefaultRouter()
friend_requests_router = DefaultRouter()

accounts_router.register('users', views.UserView, basename='users')

friend_requests_router.register('friend_requests', views.FriendRequestView, basename='requests')

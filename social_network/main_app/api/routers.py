from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register('users', views.UserView, basename='users')
router.register('friend_requests', views.FriendRequestView, basename='requests')
router.register('posts', views.PostView, basename='posts')
router.register('posts/(?P<post_id>[0-9]+)/comments', views.CommentViewSet, basename='comments')

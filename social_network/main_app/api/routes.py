from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()

router.register('user', views.UserView, basename='user')
router.register('user_friends', views.UserFriendsView, basename='friends')

from rest_framework.routers import DefaultRouter

from . import views


groups_router = DefaultRouter()

groups_router.register('dialogs', views.DialogView, basename='dialogs')
groups_router.register('conservations', views.ConservationView, basename='conservations')

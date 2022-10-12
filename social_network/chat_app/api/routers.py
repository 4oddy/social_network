from rest_framework.routers import DefaultRouter

from . import views


dialog_router = DefaultRouter()
conservation_router = DefaultRouter()

dialog_router.register('dialogs', views.DialogView, basename='dialogs')
dialog_router.register('send_message', views.SendDialogMessageView, basename='send_dialog_message')

conservation_router.register('conservations', views.ConservationView, basename='conservations')
conservation_router.register('send_message', views.SendConservationMessageView, basename='send_conservation_message')

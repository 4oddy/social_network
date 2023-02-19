from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register('dialogs', views.DialogView, basename='dialogs')
router.register('conservations', views.ConservationView, basename='conservations')

from django.urls import path

from .views import ConservationPage, DialogPage

app_name = 'chat'

urlpatterns = [
    path('conservations/<str:group_name>/', ConservationPage.as_view(), name='conservation_page'),
    path('dialogs/<str:companion_name>/', DialogPage.as_view(), name='dialog_page')
]

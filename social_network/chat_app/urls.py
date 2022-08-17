from django.urls import path

from .views import Chat

urlpatterns = [
    path('<str:username>/', Chat.as_view())
]

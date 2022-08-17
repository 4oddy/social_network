from django.urls import path

from .consumer import ChatConsumer

websocket_urlpatterns = [
    path('chatting/<str:username>/', ChatConsumer.as_asgi())
]

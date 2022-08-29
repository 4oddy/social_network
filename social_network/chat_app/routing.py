from django.urls import path

from .consumers import ConservationConsumer, DialogConsumer

websocket_urlpatterns = [
    path('chatting/conservation/<str:group_name>/', ConservationConsumer.as_asgi()),
    path('chatting/dialog/<str:group_name>/', DialogConsumer.as_asgi())
]

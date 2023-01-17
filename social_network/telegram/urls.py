from django.urls import path

from .views import GenerateTokenView


app_name = 'telegram'


urlpatterns = [
    path('generate_auth_token/', GenerateTokenView.as_view(), name='generate_token')
]

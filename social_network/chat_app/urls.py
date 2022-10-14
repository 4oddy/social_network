from django.urls import path, include

from .views import ConservationPage, DialogPage, UserGroupsPage, CreateConservationPage

from .api import routers


app_name = 'chat'

urlpatterns = [
    path('', UserGroupsPage.as_view(), name='groups_page'),
    path('create_conservation/', CreateConservationPage.as_view(), name='create_conservation_page'),
    path('conservations/<str:group_name>/', ConservationPage.as_view(), name='conservation_page'),
    path('dialogs/<str:companion_name>/', DialogPage.as_view(), name='dialog_page'),

    path('api/', include(routers.groups_router.urls)),
]

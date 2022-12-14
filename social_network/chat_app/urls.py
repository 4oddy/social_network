from django.urls import include, path

from .api import routers
from .views import (ConservationPage, CreateConservationPage, DialogPage,
                    UserGroupsPage)

app_name = 'chat'


urlpatterns = [
    path('', UserGroupsPage.as_view(), name='groups_page'),
    path('create_conservation/', CreateConservationPage.as_view(), name='create_conservation_page'),
    path('conservations/<str:group_uuid>/', ConservationPage.as_view(), name='conservation_page'),
    path('dialogs/<str:companion_name>/', DialogPage.as_view(), name='dialog_page'),

    path('api/v1/', include(routers.groups_router.urls)),
]

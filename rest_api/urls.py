from django.urls import path

from .views import *

urlpatterns = [
    # access
    path("login", login, name="login"),
    path("logout", logout, name="logout"),
    path("clients", new_client, name="new-client"),
]

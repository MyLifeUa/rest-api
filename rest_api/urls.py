from django.urls import path

from .views import *

urlpatterns = [
    # access
    path("login", login, name="login"),
    path("logout", logout, name="logout"),

    path("admins", new_admin, name="new-admin"),

    path("clients", new_client, name="new-client"),
    path("clients", update_client, name="update-client"),
]

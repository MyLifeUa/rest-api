from django.conf.urls import url
from django.urls import path

from .views import *

urlpatterns = [
    # access
    path("login", login, name="login"),
    path("logout", logout, name="logout"),

    path("admins", new_admin, name="new-admin"),

    path("clients", new_client, name="new-client"),
    url("^clients/(?P<email>.+)", client_rud, name="client-rud"),

    path("doctors", new_doctor, name="new-doctor"),
    url("^doctors/(?P<email>.+)", doctor_rud, name="doctor-rud"),

]

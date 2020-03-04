from django.conf.urls import url
from django.urls import path

from .views import *

urlpatterns = [
    # access
    path("login", login, name="login"),
    path("logout", logout, name="logout"),
]

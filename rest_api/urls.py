from django.conf.urls import url
from django.urls import path

from .views import *

urlpatterns = [
    # access
    path("login", login, name="login"),
    path("logout", logout, name="logout"),

    path("admins", new_admin, name="new-admin"),
    url("^admins/(?P<email>.+)", admin_rud, name="admin-rud"),

    path("clients", new_client, name="new-client"),
    url("^clients/(?P<email>.+)", client_rud, name="client-rud"),

    path("doctors", new_doctor, name="new-doctor"),
    url("^doctors/(?P<email>.+)", doctor_rud, name="doctor-rud"),

    # Meal History
    path("food-logs", new_food_log, name="new-food-log"),
    url("^food-logs/(?P<food_log_filter>.+)", food_log_rud, name="food-log-rud"),

    # Ingredients
    path("ingredients", new_ingredient, name="new-ingredient"),
    
    # Meal
    path("meals", new_meal, name="new-meal"),
    # Doctor patient association
    path("doctor-patient-association", new_doctor_patient_association, name="new-doctor-patient-association"),

]

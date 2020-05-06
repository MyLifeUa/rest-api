from django.conf.urls import url
from django.urls import path

from .views import *

urlpatterns = [
    # Access
    path("login", login, name="login"),
    path("logout", logout, name="logout"),

    # Admins
    path("admins", new_admin, name="new-admin"),
    url("^admins/(?P<email>.+)", admin_rud, name="admin-rud"),

    # Clients
    path("clients", new_client, name="new-client"),
    url("^clients/(?P<email>.+)", client_rud, name="client-rud"),
    url("^client-photo/(?P<email>.+)", client_photo, name="client-photo"),
    path("doctor-clients", doctor_get_all_patients, name="doctor-clients"),

    # Doctors
    path("doctors", new_doctor, name="new-doctor"),
    url("^doctors/(?P<email>.+)", doctor_rud, name="doctor-rud"),

    # Meal History
    path("food-logs", new_food_log, name="new-food-log"),
    url("^food-logs/(?P<food_log_filter>.+)", food_log_rud, name="food-log-rud"),

    # Ingredients
    path("ingredients", ingredients, name="new-ingredient"),
    path("ingredients/<int:ingredient_id>", ingredient_rud, name="ingredient-rud"),

    # Meals
    path("meals", meals, name="new-meal"),

    # Doctor patient association
    path("doctor-patient-association", doctor_patient_association_cd, name="doctor-patient-association-cd"),

    # List doctors from an hospital
    path("hospital-doctors", list_hospital_doctors, name="list-hospital-doctors"),

    # Check email is taken
    url("^check-email/(?P<email>.+)", check_email, name="check-email"),

    # Add fitbit token
    path("fitbit-token", add_fitbit_token, name="add-fitbit-token"),

    # Image Classification
    path("image-classification", classify_image, name="classify-image"),

    # Barcode Classification
    path("barcode-classification", classify_barcode, name="classify-barcode"),

    # Check token is valid
    path("check-token", check_token, name="check-token"),

    # Health Statistics
    url("^health-stats/nutrients/ratio/(?P<email>.+)/(?P<date>.+)", nutrients_ratio, name="nutrients-ratio"),
    url("^health-stats/nutrients/total/(?P<email>.+)/(?P<date>.+)", nutrients_total, name="nutrients-total"),
    url("^health-stats/nutrients/history/(?P<email>.+)", nutrients_history, name="nutrients-history"),
    url("^health-stats/body/history/(?P<email>.+)", body_history, name="body-history"),
    url("^health-stats/body/heart-rate/(?P<email>.+)", body_avg_heart_rate, name="body-avg-heart-rate"),
    url("^health-stats/my-life/(?P<email>.+)", my_life_stat, name="stat-my-life"),

    # Expo Tokens
    path("expo-tokens", expo_tokens_post_and_get, name="expo-tokens-get-and-post"),

    # Reload Database
    path("reload-db", reload_db, name="reload-db"),
]

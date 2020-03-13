from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from rest_api.models import Doctor, CustomAdmin, Client


def get_role(username, request=None):
    role = None
    try:
        if username is None:
            username = request.user.username

        if User.objects.get(username=username).is_superuser:
            role = "admin"
        elif User.objects.get(username=username).groups.all()[0].name in ["clients_group"]:
            role = "client"
        elif User.objects.get(username=username).groups.all()[0].name in ["doctors_group"]:
            role = "doctor"

    except User.DoesNotExist:
        role = None

    return role


def who_am_i(request):
    token = Token.objects.get(user=request.user).key
    username = request.user.username
    role = get_role(username)

    return token, username, role


def verify_authorization(role, group):
    return role == group


def is_self(role, group, username, email):
    return verify_authorization(role, group) and username == email


def is_doctor_admin(doctor_username, admin_username):
    doctor_hospital = Doctor.objects.get(user__auth_user__username=doctor_username).hospital
    admin_hospital = CustomAdmin.objects.get(auth_user__username=admin_username).hospital
    return admin_hospital == doctor_hospital


def is_client_doctor(doctor_username, client_username):
    doctor = Doctor.objects.get(user__auth_user__username=doctor_username)
    client = Client.objects.get(user__auth_user__username=client_username)
    return client.doctor == doctor

from django.contrib.auth.models import Group
from django.db import Error

from .models import *
from .constants import *


def add_client(data):
    email = data.get("email")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    password = data.get("password")
    height = data.get("height")
    weight_goal = data.get("weight_goal")

    # treat nullable fields
    phone_number = data.get("phone_number") if "phone_number" in data else None
    photo = data.get("photo") if "photo" in data else DEFAULT_USER_IMAGE
    birth_date = data.get("birth_date") if "birth_date" in data else None

    if User.objects.filter(username=email).exists():
        error_message = "Email already taken. User was not added to the db."
        return False, error_message

    try:
        # create a user
        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        # create custom user
        custom_user = CustomUser.objects.create(
            auth_user=user,
            phone_number=phone_number,
            photo=photo,
            birth_date=birth_date,
        )

    except Error:
        error_message = "Error while creating new user!"
        return False, error_message
    try:
        # link the user to a client
        Client.objects.create(user=custom_user, height=height, weight_goal=weight_goal)

    except Exception:
        user.delete()
        error_message = "Error while creating new client!"
        return False, error_message

    # check if the client group exists, else create it
    # finally add client to group
    try:
        if not Group.objects.filter(name="clients_group").exists():
            Group.objects.create(name="clients_group")

        clients_group = Group.objects.get(name="clients_group")
        clients_group.user_set.add(user)

    except Exception:
        user.delete()
        error_message = "Error while creating new client!"
        return False, error_message

    state_message = "Client was registered successfully!"
    return True, state_message


def add_admin(data):
    email = data.get("email")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    password = data.get("password")
    hospital = data.get("hospital")

    if User.objects.filter(username=email).exists():
        error_message = "Email already taken. User was not added to the db."
        return False, error_message

    try:
        # create a user
        user = User.objects.create_superuser(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )

    except Error:
        error_message = "Error while creating new user!"
        return False, error_message
    try:
        # link the user to an admin
        CustomAdmin.objects.create(auth_user=user, hospital=hospital)

    except Exception:
        user.delete()
        error_message = "Error while creating new admin!"
        return False, error_message

    state_message = "Admin registered successfully!"
    return True, state_message

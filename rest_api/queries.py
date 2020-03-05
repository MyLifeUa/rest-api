from django.contrib.auth.models import Group
from django.db import Error

from .constants import *
from .models import *


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
        error_message = "There's already a user with the specified email! User was not added to the db."
        return False, error_message, email

    try:
        # create a user
        user = User.objects.create_user(username=email, email=email, first_name=first_name, last_name=last_name,
                                        password=password)
        # create custom user
        custom_user = CustomUser.objects.create(auth_user=user, phone_number=phone_number, photo=photo,
                                                birth_date=birth_date)

    except Error as e:
        print(e)
        error_message = "Error while creating new user!"
        return False, error_message, email
    try:
        # link the user to a client
        Client.objects.create(user=custom_user, height=height, weight_goal=weight_goal)

    except Exception:
        user.delete()
        error_message = "Error while creating new client!"
        return False, error_message, email

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
        return False, error_message, email

    state_message = "Client was registered successfully!"
    return True, state_message, email

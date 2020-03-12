from django.contrib.auth.models import Group
from django.db import Error, transaction

from .models import *
from .constants import *


def add_client(data):
    email = data.get("email")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    password = data.get("password")
    height = data.get("height")
    weight_goal = data.get("weight_goal")
    birth_date = data.get("birth_date")

    # treat nullable fields
    phone_number = data.get("phone_number") if "phone_number" in data else None
    photo = data.get("photo") if "photo" in data else DEFAULT_USER_IMAGE

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


def update_client(request, email):
    data, state, message = request.data, None, None

    auth_user = User.objects.filter(username=email)
    if not auth_user.exists():
        state, message = False, "User does not exist!"
        return state, message

    user = CustomUser.objects.filter(auth_user=auth_user[0])
    if not user.exists():
        state, message = False, "User does not exist!"
        return state, message

    client = Client.objects.filter(user=user[0])
    if not client.exists():
        state, message = False, "User is not a client!"
        return state, message

    try:
        if "email" in data:
            email = data.get("email")
            auth_user.update(email=email)
            auth_user.update(username=email)

        if "first_name" in data:
            first_name = data.get("first_name")
            auth_user.update(first_name=first_name)

        if "last_name" in data:
            last_name = data.get("last_name")
            auth_user.update(last_name=last_name)

        if "password" in data:
            user = User.objects.get(username=email)
            auth_user.set_password(data.get("password"))
            auth_user.save()

        if "phone_number" in data:
            phone_number = data.get("phone_number")
            user.update(phone_number=phone_number)

        if "photo" in data:
            photo = data.get("photo")
            user.update(photo=photo)

        if "birth_date" in data:
            birth_date = data.get("birth_date")
            user.update(birth_date=birth_date)

        if "height" in data:
            height = data.get("height")
            client.update(height=height)

        if "weight_goal" in data:
            weight_goal = data.get("weight_goal")
            client.update(weight_goal=weight_goal)

        if state is None:
            state = True
            message = "Client successfully updated!"

    except Exception:
        state, message = False, "Error while updating client!"

    return state, message


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


def delete_user(user):
    try:
        user.delete()
        state, message = True, "User successfully deleted"
    except Error:
        state, message = False, "Error while deleting user"

    finally:
        return state, message


def add_doctor(data, hospital):
    email = data.get("email")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    password = data.get("password")
    birth_date = data.get("birth_date")

    # treat nullable fields
    phone_number = data.get("phone_number") if "phone_number" in data else None
    photo = data.get("photo") if "photo" in data else DEFAULT_USER_IMAGE

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

    except Error:
        error_message = "Error while creating new user!"
        return False, error_message

    try:
        custom_user = CustomUser.objects.create(
            auth_user=user,
            phone_number=phone_number,
            photo=photo,
            birth_date=birth_date,
        )

    except Error:
        error_message = "Error while creating new custom_user!"
        return False, error_message

    try:
        # link the user to a doctor
        Doctor.objects.create(user=custom_user, hospital=hospital)

    except Exception:
        user.delete()
        error_message = "Error while creating new doctor!"
        return False, error_message

    # check if the doctor group exists, else create it
    # finally add client to group
    try:
        if not Group.objects.filter(name="doctors_group").exists():
            Group.objects.create(name="doctors_group")

        doctors_group = Group.objects.get(name="doctors_group")
        doctors_group.user_set.add(user)

    except Exception:
        user.delete()
        error_message = "Error while creating new doctor!"
        return False, error_message

    state_message = "Doctor registered successfully!"
    return True, state_message


def update_doctor(request, email):
    data, state, message = request.data, None, None

    auth_user = User.objects.filter(username=email)
    if not auth_user.exists():
        state, message = False, "User does not exist!"
        return state, message

    user = CustomUser.objects.filter(auth_user=auth_user[0])
    if not user.exists():
        state, message = False, "User does not exist!"
        return state, message

    doctor = Doctor.objects.filter(user=user[0])
    if not doctor.exists():
        state, message = False, "User is not a doctor!"
        return state, message

    try:
        if "email" in data:
            email = data.get("email")
            auth_user.update(email=email)
            auth_user.update(username=email)

        if "first_name" in data:
            first_name = data.get("first_name")
            auth_user.update(first_name=first_name)

        if "last_name" in data:
            last_name = data.get("last_name")
            auth_user.update(last_name=last_name)

        if "password" in data:
            user = User.objects.get(username=email)
            auth_user.set_password(data.get("password"))
            auth_user.save()

        if "phone_number" in data:
            phone_number = data.get("phone_number")
            user.update(phone_number=phone_number)

        if "photo" in data:
            photo = data.get("photo")
            user.update(photo=photo)

        if "birth_date" in data:
            birth_date = data.get("birth_date")
            user.update(birth_date=birth_date)

        if state is None:
            state = True
            message = "Doctor successfully updated!"

    except Exception:
        state, message = False, "Error while updating client!"

    return state, message

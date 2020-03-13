from django.contrib.auth.models import Group
from django.db import Error, transaction

from .models import *
from .constants import *
from .serializers import ClientSerializer, DoctorSerializer


def add_user(data, is_superuser=False):
    email = data.get("email")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    password = data.get("password")

    if not is_superuser:
        birth_date = data.get("birth_date")

        # treat nullable fields
        phone_number = data.get("phone_number") if "phone_number" in data else None
        photo = data.get("photo") if "photo" in data else DEFAULT_USER_IMAGE

    if User.objects.filter(username=email).exists():
        error_message = "Email already taken. User was not added to the db."
        return False, error_message

    try:
        if is_superuser:
            # create a user
            user = User.objects.create_superuser(username=email, email=email, first_name=first_name,
                                                 last_name=last_name, password=password)

        else:
            # create a user
            auth_user = User.objects.create_user(username=email, email=email, first_name=first_name,
                                                 last_name=last_name, password=password)

            # create custom user
            user = CustomUser.objects.create(auth_user=auth_user, phone_number=phone_number, photo=photo,
                                             birth_date=birth_date)

    except Error:
        error_message = "Error while creating new user!"
        return False, error_message

    return True, user


def update_user(data, auth_user, user):
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


def delete_user(user):
    try:
        user.delete()
        state, message = True, "User successfully deleted"

    except Error:
        state, message = False, "Error while deleting user"

    finally:
        return state, message


def add_client(data):
    height = data.get("height")
    weight_goal = data.get("weight_goal")

    state, content = add_user(data)
    if not state:
        return state, content

    custom_user = content
    user = custom_user.auth_user

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
        clients_group, created = Group.objects.get_or_create(name="clients_group")
        clients_group.user_set.add(user)

    except Exception:
        user.delete()
        error_message = "Error while creating new client!"
        return False, error_message

    state_message = "Client was registered successfully!"
    return True, state_message


def update_client(request, email):
    data = request.data
    state = True
    message = "Client successfully updated!"

    client = Client.objects.filter(user__auth_user__username=email)
    if not client.exists():
        state, message = False, "User does not exist or user is not a client!"
        return state, message

    try:
        auth_user = User.objects.filter(username=email)
        user = CustomUser.objects.filter(auth_user=auth_user[0])

        update_user(data, auth_user, user)

        if "height" in data:
            height = data.get("height")
            client.update(height=height)

        if "weight_goal" in data:
            weight_goal = data.get("weight_goal")
            client.update(weight_goal=weight_goal)

    except Exception:
        state, message = False, "Error while updating client!"

    return state, message


def get_client(email):
    client = Client.objects.filter(user__auth_user__username=email)
    if not client.exists():
        state, message = False, "User does not exist or user is not a client!"
        return state, message

    state, message = True, ClientSerializer(client[0]).data
    return state, message


def add_admin(data):
    hospital = data.get("hospital")

    state, content = add_user(data, is_superuser=True)
    if not state:
        return state, content

    user = content

    try:
        # link the user to an admin
        CustomAdmin.objects.create(auth_user=user, hospital=hospital)

    except Exception:
        user.delete()
        error_message = "Error while creating new admin!"
        return False, error_message

    state_message = "Admin registered successfully!"
    return True, state_message


def add_doctor(data, hospital):
    state, content = add_user(data)
    if not state:
        return state, content

    custom_user = content
    user = custom_user.auth_user

    try:
        # link the user to a doctor
        Doctor.objects.create(user=custom_user, hospital=hospital)

    except Exception:
        user.delete()
        error_message = "Error while creating new doctor!"
        return False, error_message

    # check if the doctor group exists, else create it
    # finally add doctor to group
    try:
        doctors_group, created = Group.objects.get_or_create(name="doctors_group")
        doctors_group.user_set.add(user)

    except Exception:
        user.delete()
        error_message = "Error while creating new doctor!"
        return False, error_message

    state_message = "Doctor registered successfully!"
    return True, state_message


def update_doctor(request, email):
    data = request.data
    state = True
    message = "Doctor successfully updated!"

    doctor = Doctor.objects.filter(user__auth_user__username=email)
    if not doctor.exists():
        state, message = False, "User does not exist or user is not a doctor!"
        return state, message

    try:
        auth_user = User.objects.filter(username=email)
        user = CustomUser.objects.filter(auth_user=auth_user[0])

        update_user(data, auth_user, user)

    except Exception:
        state, message = False, "Error while updating client!"

    return state, message


def get_doctor(email):
    doctor = Doctor.objects.filter(user__auth_user__username=email)
    if not doctor.exists():
        state, message = False, "User does not exist or user is not a doctor!"
        return state, message

    state, message = True, DoctorSerializer(doctor[0]).data
    return state, message

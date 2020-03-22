from django.contrib.auth.models import Group
from django.db import Error, transaction

from .models import *
from .constants import *
from .serializers import ClientSerializer, DoctorSerializer, AdminSerializer, MealHistorySerializer


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


def update_user(data, auth_user, user=None):
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

    if "phone_number" in data and user is not None:
        phone_number = data.get("phone_number")
        user.update(phone_number=phone_number)

    if "photo" in data and user is not None:
        photo = data.get("photo")
        user.update(photo=photo)

    if "birth_date" in data and user is not None:
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


def update_admin(request, username):
    data = request.data
    state = True
    message = "Admin successfully updated!"

    admin = CustomAdmin.objects.filter(auth_user__username=username)
    if not admin.exists():
        state, message = False, "User does not exist or user is not a admin!"
        return state, message

    try:
        auth_user = User.objects.filter(username=username)

        update_user(data, auth_user)

    except Exception:
        state, message = False, "Error while updating client!"

    return state, message


def get_admin(username):
    admin = CustomAdmin.objects.filter(auth_user__username=username)
    if not admin.exists():
        state, message = False, "User does not exist or user is not a admin!"
        return state, message

    state, message = True, AdminSerializer(admin[0]).data
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


def add_food_log(data, email):
    day = data.get("day")
    type_of_meal = data.get("type_of_meal")
    meal_id = data.get("meal")

    client = Client.objects.filter(user__auth_user__username=email)

    if not client.exists():
        state, message = False, "Client does not exist."
        return state, message  

    current_client = Client.objects.get(user__auth_user__username=email)

    meal_history_with_type_of_meal = MealHistory.objects.filter(day=day, type_of_meal=type_of_meal,
                                                                client=current_client)

    if not meal_history_with_type_of_meal.exists():  # Food log does not exist yet
        try:

            meal = Meal.objects.filter(id=meal_id)

            if not meal.exists():
                state, message = False, "Meal does not exist."
                return state, message

            current_meal = Meal.objects.get(id=meal_id)

            MealHistory.objects.create(day=day, type_of_meal=type_of_meal, client=current_client,
                                       meal=current_meal)

        except Exception as e:
            print(e)
            error_message = "Error while creating new food log!"
            return False, error_message
    else:  # Food log exists for this day and for this type of meal

        error_message = "Food log already exists for this day and type of meal."
        return False, error_message

    state_message = "The food log was created with success"
    return True, state_message


def delete_food_log(meal_history):
    try:
        meal_history.delete()
        state, message = True, "Food log successfully deleted"

    except Error:
        state, message = False, "Error while deleting user"

    finally:
        return state, message


def get_food_log(email, day):
    current_client = Client.objects.get(user__auth_user__username=email)

    meal_history = MealHistory.objects.filter(day=day, client=current_client)

    if not meal_history.exists():
        state, message = False, "Food log does not exist."
        return state, message

    state, message = True, [MealHistorySerializer(r).data for r in meal_history]

    return state, message


from django.contrib.auth.models import Group
from requests import get
from django.db.models import Q
from django.db import Error

from my_life_rest_api.settings import ML_URL
from .models import *
from .constants import *
from .serializers import *
from .utils import get_total_nutrients, get_nutrients_info, get_calories_daily_goal, get_nutrients_left_values, \
    get_nutrient_history


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
        pwd_user = User.objects.get(username=auth_user[0].username)
        pwd_user.set_password(data.get("password"))
        pwd_user.save()

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
    current_weight = data.get("current_weight")
    sex = data.get("sex")

    state, content = add_user(data)
    if not state:
        return state, content

    custom_user = content
    user = custom_user.auth_user

    try:
        # link the user to a client
        Client.objects.create(user=custom_user, height=height, current_weight=current_weight, weight_goal=weight_goal,
                              sex=sex)

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

        if "current_weight" in data:
            current_weight = data.get("current_weight")
            client.update(current_weight=current_weight)

        if "weight_goal" in data:
            weight_goal = data.get("weight_goal")
            client.update(weight_goal=weight_goal)

        if "sex" in data:
            sex = data.get("sex")
            client.update(sex=sex)

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
    number_of_servings = data.get("number_of_servings")

    client = Client.objects.filter(user__auth_user__username=email)

    if not client.exists():
        state, message = False, "Client does not exist."
        return state, message

    current_client = Client.objects.get(user__auth_user__username=email)

    try:

        meal = Meal.objects.filter(id=meal_id)

        if not meal.exists():
            state, message = False, "Meal does not exist."
            return state, message

        current_meal = Meal.objects.get(id=meal_id)

        MealHistory.objects.create(day=day, type_of_meal=type_of_meal, client=current_client,
                                   meal=current_meal, number_of_servings=number_of_servings)

    except Exception:
        message = "Error while creating new food log!"
        return False, message

    message = "The food log was created with success"
    return True, message


def delete_food_log(meal_history):
    try:
        meal_history.delete()
        state, message = True, "Food log successfully deleted"

    except Error:
        state, message = False, "Error while deleting user"

    return state, message


def get_food_log(email, day):
    current_client = Client.objects.get(user__auth_user__username=email)

    meal_history = MealHistory.objects.filter(day=day, client=current_client)

    state, message = True, [MealHistorySerializer(r).data for r in meal_history]

    return state, message


def update_food_log(request, meal_history):
    data = request.data
    state = True
    message = "Food log successfully updated!"

    try:
        if "day" in data:
            day = data.get("day")
            meal_history.update(day=day)

        if "type_of_meal" in data:
            type_of_meal = data.get("type_of_meal")
            meal_history.update(type_of_meal=type_of_meal)

        if "meal" in data:
            meal_id = data.get("meal")

            meal = Meal.objects.filter(id=meal_id)

            if not meal.exists():
                state, message = False, "Meal does not exist."
                return state, message

            current_meal = Meal.objects.get(id=meal_id)

            meal_history.update(meal=current_meal)

        if "number_of_servings" in data:
            number_of_servings = data.get("number_of_servings")
            meal_history.update(number_of_servings=number_of_servings)

    except Exception:
        state, message = False, "Error while updating Food log!"

    return state, message


def add_ingredient(data):
    name = data.get("name")
    calories = data.get("calories")
    carbs = data.get("carbs")
    fat = data.get("fat")
    proteins = data.get("proteins")

    try:
        Ingredient.objects.create(name=name, calories=calories, carbs=carbs, fat=fat, proteins=proteins)

    except Exception:
        error_message = "Error while creating new ingredient!"
        return False, error_message

    state_message = "The ingredient was created with success"
    return True, state_message


def update_ingredient(data, ingredient_id):
    state = True
    message = "Ingredient successfully updated!"

    ingredient = Ingredient.objects.filter(id=ingredient_id)
    if not ingredient.exists():
        state, message = False, "Ingredient does not exist!"
        return state, message

    try:
        if "calories" in data:
            calories = data.get("calories")
            ingredient.update(calories=calories)

        if "proteins" in data:
            proteins = data.get("proteins")
            ingredient.update(proteins=proteins)

        if "fat" in data:
            fat = data.get("fat")
            ingredient.update(fat=fat)

        if "carbs" in data:
            carbs = data.get("carbs")
            ingredient.update(carbs=carbs)

        if "name" in data:
            name = data.get("name")
            ingredient.update(name=name)

    except Exception:
        state, message = False, "Error while updating ingredient!"

    return state, message


def delete_ingredient(ingredient_id):
    state = True
    message = "Ingredient successfully deleted!"

    try:
        ingredient = Ingredient.objects.get(id=ingredient_id)
        ingredient.delete()

    except Ingredient.DoesNotExist:
        state, message = False, "Ingredient does not exist!"

    return state, message


def get_ingredients():
    return True, [IngredientSerializer(ingredient).data for ingredient in Ingredient.objects.all()]


def get_ingredient(ingredient_id):
    try:
        ingredient = Ingredient.objects.get(id=ingredient_id)

    except Ingredient.DoesNotExist:
        state, message = False, "Ingredient does not exist!"
        return state, message

    return True, IngredientSerializer(ingredient).data


def add_new_meal(data, username, role="admin"):
    name = data.get("name")
    category = data.get("category")
    ingredients = data.get("ingredients")

    # treat nullable fields
    client = Client.objects.get(user__auth_user__username=username) if role == "client" else None

    if not ingredients:
        error_message = "Error while creating new meal!"
        return False, error_message

    try:
        # create new meal
        meal = Meal.objects.create(name=name, category=category, client=client)

    except Exception:
        error_message = "Error while creating new meal!"
        return False, error_message

    try:
        # add ingredients quantities
        for ingredient_json in ingredients:
            ingredient = Ingredient.objects.get(id=ingredient_json["id"])
            Quantity.objects.create(meal=meal, ingredient=ingredient, quantity=ingredient_json["quantity"])

    except Ingredient.DoesNotExist:
        meal.delete()
        error_message = "Ingredient does not exist!"
        return False, error_message

    state_message = "Meal created successfully!"
    return True, state_message


def get_meals(username):
    client = Client.objects.get(user__auth_user__username=username)
    return True, [MealSerializer(meal).data for meal in Meal.objects.filter(Q(client__isnull=True) | Q(client=client))]


def add_doctor_patient_association(data, email):
    client_username = data.get("client")

    client = Client.objects.filter(user__auth_user__username=client_username)

    current_doctor = Doctor.objects.get(user__auth_user__username=email)

    if not client.exists():
        state, message = False, "Patient does not exist."
        return state, message

    current_client = Client.objects.get(user__auth_user__username=client_username)

    if current_client.doctor is None:
        client.update(doctor=current_doctor)
    else:
        error_message = "The patient already has a doctor associated."
        return False, error_message

    state_message = "The Doctor patient association was created with success"
    return True, state_message


def delete_doctor_patient_association(email):
    try:
        client = Client.objects.filter(user__auth_user__username=email)
        client.update(doctor=None)
        state, message = True, "Doctor patient association successfully deleted"

    except Exception:
        state, message = False, "Error while deleting Doctor patient association"

    return state, message


def doctor_get_all_patients(username):
    try:
        doctor = Doctor.objects.get(user__auth_user__username=username)

        state = True
        message = [ClientSerializer(client).data for client in Client.objects.filter(doctor=doctor)]

    except Doctor.DoesNotExist:
        state = False
        message = "Operation not allowed: you are not a doctor!"

    except Exception:
        state = False
        message = "Error while fetching doctor clients' data!"

    return state, message


def get_hospital_doctors(email):
    admin_hospital = CustomAdmin.objects.get(auth_user__username=email).hospital

    doctors = Doctor.objects.filter(hospital=admin_hospital)

    state, message = True, [DoctorSerializer(r).data for r in doctors]

    return state, message


def add_fitbit_token(data, email):
    fitbit_access_token = data.get("access_token")
    fitbit_refresh_token = data.get("refresh_token")

    client = Client.objects.filter(user__auth_user__username=email)

    try:
        client.update(fitbit_access_token=fitbit_access_token, fitbit_refresh_token=fitbit_refresh_token)
        state, message = True, "The fitbit token was added with success"

    except Exception:
        state, message = False, "Error while adding fitbit token."

    return state, message


def classify_image(image_b64):
    if image_b64 == "":
        state = False
        message = "Missing parameters"

    else:
        params = {"image_b64": image_b64}
        response = get(url=ML_URL, params=params)

        state = False
        message = "Error while trying to classifying food"

        if response.status_code == 200:
            data = eval(response.text)

            if data:  # check if list is not empty
                state = True
                message = {"food": data[-1]["label"]}  # get the last element (the one ml module has most confident)

    return state, message


def get_client_doctor(username):
    client = Client.objects.get(user__auth_user__username=username)

    try:
        doctor = client.doctor
        state = True
        message = DoctorSerializer(doctor).data if doctor is not None else None
    except Exception:
        state, message = False, "Error while adding fitbit token."

    return state, message


def get_nutrients_ratio(username, day):
    client = Client.objects.get(user__auth_user__username=username)

    meal_history = MealHistory.objects.filter(day=day, client=client)

    if not meal_history.exists():
        state = False
        message = "The specified day has no history yet."

    else:
        initial_info = get_total_nutrients(meal_history)

        message = get_nutrients_info(client, initial_info)
        state = True

    return state, message


def get_nutrients_total(username, day):
    client = Client.objects.get(user__auth_user__username=username)

    meal_history = MealHistory.objects.filter(day=day, client=client)

    if not meal_history.exists():
        state = False
        message = "The specified day has no history yet."

    else:
        initial_info = get_total_nutrients(meal_history)

        message = get_nutrients_left_values(client, initial_info)
        state = True

    return state, message


def get_nutrients_history(username, params):
    metric = params["metric"]
    if metric not in ["calories", "fat", "carbs", "proteins"]:
        state = False
        message = "Invalid metric!"
        return state, message

    period = params["period"]
    if period not in ["week", "month", "3-months"]:
        state = False
        message = "Invalid period!"
        return state, message

    client = Client.objects.get(user__auth_user__username=username)

    return True, get_nutrient_history(client, metric, period)

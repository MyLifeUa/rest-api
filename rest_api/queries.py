import fitbit
from django.contrib.auth.models import Group
from django.db import Error
from django.db.models import Q
from requests import get

from my_life_rest_api.settings import ML_URL
from .constants import *
from .models import *
from .serializers import *
from .utils import *


def add_user(data, is_admin=False):
    email = data.get("email")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    password = data.get("password")

    if not is_admin:
        birth_date = data.get("birth_date")

        # treat nullable fields
        phone_number = data.get("phone_number") if "phone_number" in data else None
        photo = data.get("photo") if "photo" in data else DEFAULT_USER_IMAGE

    if User.objects.filter(username=email).exists():
        error_message = "Email already taken. User was not added to the db."
        return False, error_message

    try:
        if is_admin:
            # create a user
            user = User.objects.create_user(username=email, email=email, first_name=first_name, last_name=last_name,
                                            password=password)

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

    return state, message


def add_admin(data):
    hospital = data.get("hospital")

    state, content = add_user(data, is_admin=True)
    if not state:
        return state, content

    user = content

    try:
        # link the user to an admin
        HospitalAdmin.objects.create(auth_user=user, hospital=hospital)

    except Exception:
        user.delete()
        error_message = "Error while creating new admin!"
        return False, error_message

    try:
        admins_group, created = Group.objects.get_or_create(name="admins_group")
        admins_group.user_set.add(user)

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

    admin = HospitalAdmin.objects.filter(auth_user__username=username)
    if not admin.exists():
        state, message = False, "User does not exist or user is not a admin!"
        return state, message

    try:
        auth_user = User.objects.filter(username=username)

        update_user(data, auth_user)

    except Exception:
        state, message = False, "Error while updating admin!"

    return state, message


def get_admin(username):
    admin = HospitalAdmin.objects.filter(auth_user__username=username)
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

    is_diabetic = data.get("is_diabetic", False)
    has_high_colesterol = data.get("has_high_colesterol", False)

    state, content = add_user(data)
    if not state:
        return state, content

    custom_user = content
    user = custom_user.auth_user

    try:
        # link the user to a client
        Client.objects.create(user=custom_user, height=height, current_weight=current_weight, weight_goal=weight_goal,
                              sex=sex, 
                              is_diabetic=is_diabetic, has_high_colesterol=has_high_colesterol)

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

        if "is_diabetic" in data:
            is_diabetic = data.get("is_diabetic")
            client.update(is_diabetic=is_diabetic)

        if "has_high_colesterol" in data:
            has_high_colesterol = data.get("has_high_colesterol")
            client.update(has_high_colesterol=has_high_colesterol)

    except Exception as e:
        print(e)
        state, message = False, "Error while updating client!"

    return state, message


def get_client(email):
    try:
        client = Client.objects.get(user__auth_user__username=email)

    except Client.DoesNotExist:
        state = False
        message = "User does not exist or user is not a client!"
        return state, message

    try:
        message = ClientSerializer(client).data
        message["steps"] = ""
        message["heart_rate"] = ""
        message["distance"] = ""

        fitbit_access_token = client.fitbit_access_token
        fitbit_refresh_token = client.fitbit_refresh_token

        if fitbit_access_token is not None and fitbit_refresh_token is not None:
            fitbit_api = fitbit.Fitbit(CLIENT_FITBIT_ID, CLIENT_FITBIT_SECRET, system="en_UK", oauth2=True,
                                       access_token=fitbit_access_token, refresh_token=fitbit_refresh_token,
                                       refresh_cb=client.refresh_cb)

            message["steps"] = fitbit_api.time_series("activities/steps", period="1d")["activities-steps"][0]["value"]
            message["distance"] = fitbit_api.time_series("activities/distance", period="1d")["activities-distance"][0][
                "value"]

            data = fitbit_api.time_series("activities/heart", period="1m")["activities-heart"]
            heart_rates = sorted(filter(lambda e: "restingHeartRate" in e["value"], data), key=lambda e: e["dateTime"],
                                 reverse=True)
            message["heart_rate"] = heart_rates[0]["value"]["restingHeartRate"]
        state = True

    except Exception:
        client.fitbit_access_token = None
        client.fitbit_refresh_token = None
        client.save()
        state = False
        message = "Error while trying to fetch client information"

    return state, message


def get_client_photo(email):
    try:
        client = Client.objects.get(user__auth_user__username=email)
        state = True
        message = {"photo": client.user.photo}

    except Client.DoesNotExist:
        state = False
        message = "User does not exist or user is not a client!"
        return state, message

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

    alerts = None

    client = Client.objects.filter(user__auth_user__username=email)

    if not client.exists():
        state, message = False, "Client does not exist."
        return state, message, alerts

    current_client = Client.objects.get(user__auth_user__username=email)

    try:

        meal = Meal.objects.filter(id=meal_id)

        if not meal.exists():
            state, message = False, "Meal does not exist."
            return state, message, alerts

        current_meal = Meal.objects.get(id=meal_id)

        number_of_servings = float(number_of_servings)
        calories = number_of_servings * current_meal.calories
        proteins = number_of_servings * current_meal.proteins
        carbs = number_of_servings * current_meal.carbs
        fat = number_of_servings * current_meal.fat

        inserted_item = MealHistory.objects.create(day=day, type_of_meal=type_of_meal, client=current_client,
                                                   meal=current_meal, number_of_servings=number_of_servings,
                                                   calories=calories, proteins=proteins, carbs=carbs, fat=fat)

        alerts = process_meal_history_insert(current_client, inserted_item)

    except Exception:
        message = "Error while creating new food log!"
        return False, message, alerts

    message = "The food log was created with success"
    return True, message, alerts


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

    data = group_meals(meal_history, current_client)

    state, message = True, data

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

            populate_nutrient_values_meal_history(meal_history, meal=current_meal)

            meal_history.update(meal=current_meal)

        if "number_of_servings" in data:
            number_of_servings = float(data.get("number_of_servings"))
            meal_history.update(number_of_servings=number_of_servings)
            populate_nutrient_values_meal_history(meal_history, number_of_servings=number_of_servings)

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
        # add ingredients quantities and nutrient values
        for ingredient_json in ingredients:
            if 'id' in ingredient_json:
                ingredient = Ingredient.objects.get(id=ingredient_json["id"])
            elif 'name' in ingredient_json:
                ingredient = Ingredient.objects.get(name=ingredient_json["name"])
            quantity = ingredient_json["quantity"]
            Quantity.objects.create(meal=meal, ingredient=ingredient, quantity=quantity)
            populate_nutrient_values(Meal.objects.filter(id=meal.id), Ingredient.objects.get(id=ingredient.id),
                                     quantity)

    except Ingredient.DoesNotExist:
        meal.delete()
        error_message = "Ingredient does not exist!"
        return False, error_message

    state_message = "Meal created successfully!"
    return True, state_message

def add_new_ingredient(data):
    try:
        name = data.get("name")
        calories = data.get("calories")
        carbs = data.get("carbs")
        fat = data.get("fat")
        proteins = data.get("proteins")
    except Exception:
        error_message = "Error creating new ingredient! Request incomplete."
        return False, error_message

    try:
        ingredient = Ingredient.objects.create(name=name, calories=calories, carbs=carbs, fat=fat, proteins=proteins)
    except Exception:
        error_message = "Error while creating new ingredient!"
        return False, error_message

    state_message = "Ingredient created successfully!"
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
    admin_hospital = HospitalAdmin.objects.get(auth_user__username=email).hospital

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
        message = "Error while trying to classify food"

        if response.status_code == 200:
            data = eval(response.text)

            if data:  # check if list is not empty
                food = data[-1]["label"]  # get the last element (the one ml module has most confident)

                try:
                    meal = Meal.objects.get(name__iexact=food)
                    message = MealSerializer(meal).data
                    state = True

                except Meal.DoesNotExist:
                    message = "Recognized meal does not exist in the system!"

    return state, message


def classify_barcode(username, barcode):
    if barcode == "":
        state = False
        message = "Missing parameter: 'barcode'"

    else:
        response = get_product(barcode)

        state = False
        message = "Product not found."

        if response.get("status") == 1:
            product_name = response.get("product").get("product_name")

            message = "Error while trying to classify product"

            if product_name is not None:

                try:
                    client = Client.objects.get(user__auth_user__username=username)
                    meals = Meal.objects.filter(Q(client__isnull=True) | Q(client=client))
                    meal = meals.filter(name__iexact=product_name)[0]
                    message = MealSerializer(meal).data
                    state = True

                except Exception:
                    message = "Item does not exist in the system!"

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


def get_body_history(username, params):
    metric = params["metric"]
    if metric not in ["steps", "distance", "calories", "floors", "heart"]:
        state = False
        message = "Invalid metric!"
        return state, message

    period = params["period"]
    if period not in ["week", "month", "3-months"]:
        state = False
        message = "Invalid period!"
        return state, message

    client = Client.objects.get(user__auth_user__username=username)

    fitbit_access_token = client.fitbit_access_token
    fitbit_refresh_token = client.fitbit_refresh_token

    if fitbit_access_token is None or fitbit_refresh_token is None:
        state = False
        message = "You have not integrated your Fitbit device yet!"
        return state, message

    try:
        fitbit_api = fitbit.Fitbit(CLIENT_FITBIT_ID, CLIENT_FITBIT_SECRET, system="en_UK", oauth2=True,
                                   access_token=fitbit_access_token, refresh_token=fitbit_refresh_token,
                                   refresh_cb=client.refresh_cb)

        message = get_body_history_values(fitbit_api, metric, period)
        state = True

    except Exception:
        client.fitbit_access_token = None
        client.fitbit_refresh_token = None
        client.save()
        state, message = False, "Error while accessing fitbit information."

    return state, message


def get_body_avg_heart_rate(username):
    client = Client.objects.get(user__auth_user__username=username)

    fitbit_access_token = client.fitbit_access_token
    fitbit_refresh_token = client.fitbit_refresh_token

    if fitbit_access_token is None or fitbit_refresh_token is None:
        state = False
        message = "You have not integrated your Fitbit device yet!"
        return state, message

    try:
        fitbit_api = fitbit.Fitbit(CLIENT_FITBIT_ID, CLIENT_FITBIT_SECRET, system="en_UK", oauth2=True,
                                   access_token=fitbit_access_token, refresh_token=fitbit_refresh_token,
                                   refresh_cb=client.refresh_cb)

        message = get_client_heart_rate_chart(client, fitbit_api)
        state = True

    except Exception:
        client.fitbit_access_token = None
        client.fitbit_refresh_token = None
        client.save()
        state, message = False, "Error while accessing fitbit information."

    return state, message


def get_my_life_stat(username):
    client = Client.objects.get(user__auth_user__username=username)

    fitbit_access_token = client.fitbit_access_token
    fitbit_refresh_token = client.fitbit_refresh_token

    if fitbit_access_token is None or fitbit_refresh_token is None:
        message = get_my_life_stats(client)
        state = True

    else:
        try:
            fitbit_api = fitbit.Fitbit(CLIENT_FITBIT_ID, CLIENT_FITBIT_SECRET, system="en_UK", oauth2=True,
                                       access_token=fitbit_access_token, refresh_token=fitbit_refresh_token,
                                       refresh_cb=client.refresh_cb)

            message = get_my_life_stats(client, fitbit_api)
            state = True

        except Exception:
            client.fitbit_access_token = None
            client.fitbit_refresh_token = None
            client.save()
            state, message = False, "Error while accessing fitbit information."

    return state, message


def new_expo_token(data, username):
    client = Client.objects.get(user__auth_user__username=username)
    expo_token = data["expo_token"]

    ExpoToken.objects.create(client=client, token=expo_token)

    return True, "Expo Token registered successfully"


def get_client_expo_tokens(username):
    client = Client.objects.get(user__auth_user__username=username)

    return True, [token.token for token in ExpoToken.objects.filter(client=client)]


def delete_client_expo_tokens(data, username):
    token = data.get("expo_token")
    client = Client.objects.get(user__auth_user__username=username)

    if token is None:
        ExpoToken.objects.filter(client=client).delete()
        message = "All client's expo tokens were deleted successfully"
    else:
        ExpoToken.objects.filter(client=client, token=token).delete()
        message = "Client's token was successfully deleted"

    return True, message


def reload_database():
    try:
        #######################################
        #            WIPE DATABASE            #
        #######################################
        User.objects.all().delete()
        Ingredient.objects.all().delete()
        Meal.objects.all().delete()

        #######################################
        #          CREATE DJANGO ADMIN      #
        #######################################
        User.objects.create_superuser("admin", "admin@ua.pt", "admin")

        #######################################
        #          CREATE USERS - ADMINS      #
        #######################################
        success, state = add_admin({
            "hospital": "Hospital São João",
            "email": "antonio.martins@saojoao.pt",
            "first_name": "António",
            "last_name": "Martins",
            "password": "letmein",
            "birth_date": "1970-10-01",
            "phone_number": "910845367"
        })
        cur_success = success
        success, state = add_admin({
            "hospital": "Hospital Santo António",
            "email": "rui.almeida@santoantonio.pt",
            "first_name": "Rui",
            "last_name": "Almeida",
            "password": "qwerty",
            "birth_date": "1971-03-04",
            "phone_number": "910547367"
        })
        cur_success = cur_success and success
        success, state = add_admin({
            "hospital": "Hospital da Luz",
            "email": "pedro.silva@luz.pt",
            "first_name": "Pedro",
            "last_name": "Silva",
            "password": "ola",
            "birth_date": "1980-12-03",
            "phone_number": "910443377"
        })
        cur_success = cur_success and success

        #######################################
        #          CREATE USERS - CLIENTS     #
        #######################################
        success, state = add_client({
            "height": 180,
            "weight_goal": 75,
            "current_weight": 90,
            "sex": "M",
            "email": "vasco.almeida@gmail.com",
            "first_name": "Vasco",
            "last_name": "Almeida",
            "password": "olaola",
            "birth_date": "1975-11-05",
            "phone_number": "936545567"
        })
        cur_success = cur_success and success
        success, state = add_client({
            "height": 170,
            "weight_goal": 70,
            "current_weight": 85,
            "sex": "F",
            "email": "ana.almeida@gmail.com",
            "first_name": "Ana",
            "last_name": "Almeida",
            "password": "olaolaola",
            "birth_date": "1977-09-03",
            "phone_number": "936735367"
        })
        cur_success = cur_success and success
        success, state = add_client({
            "height": 190,
            "weight_goal": 80,
            "current_weight": 100,
            "sex": "M",
            "email": "miguel.silva@gmail.com",
            "first_name": "Miguel",
            "last_name": "Silva",
            "password": "12345ola",
            "birth_date": "1990-10-04",
            "phone_number": "966735367"
        })
        cur_success = cur_success and success
        success, state = add_client({
            "height": 184,
            "weight_goal": 80,
            "current_weight": 90,
            "sex": "M",
            "email": "miguel.oliveira@gmail.com",
            "first_name": "Miguel",
            "last_name": "Oliveira",
            "password": "qwerty98765",
            "birth_date": "1990-12-07",
            "phone_number": "966434367"
        })
        cur_success = cur_success and success
        success, state = add_client({
            "height": 165,
            "weight_goal": 70,
            "current_weight": 90,
            "sex": "M",
            "email": "antonio.silva@gmail.com",
            "first_name": "António",
            "last_name": "Silva",
            "password": "12345olaola",
            "birth_date": "1991-10-04",
            "phone_number": "965735367"
        })
        cur_success = cur_success and success
        success, state = add_client({
            "height": 168,
            "weight_goal": 80,
            "current_weight": 90,
            "sex": "M",
            "email": "miguel.pedroseiro@gmail.com",
            "first_name": "Miguel",
            "last_name": "Pedroseiro",
            "password": "pedrosorules",
            "birth_date": "1980-10-04",
            "phone_number": "936735367"
        })
        cur_success = cur_success and success
        success, state = add_client({
            "height": 170,
            "weight_goal": 60,
            "current_weight": 75,
            "sex": "F",
            "email": "fatima.silva@gmail.com",
            "first_name": "Fátima",
            "last_name": "Silva",
            "password": "qwertyola",
            "birth_date": "1990-05-04",
            "phone_number": "964755367"
        })
        cur_success = cur_success and success
        success, state = add_client({
            "height": 180,
            "weight_goal": 70,
            "current_weight": 75,
            "sex": "F",
            "email": "laura.silva@gmail.com",
            "first_name": "Laura",
            "last_name": "Silva",
            "password": "12345ola",
            "birth_date": "1998-10-04",
            "phone_number": "916735367"
        })
        cur_success = cur_success and success
        success, state = add_client({
            "height": 195,
            "weight_goal": 90,
            "current_weight": 110,
            "sex": "M",
            "email": "pedro.pereira@gmail.com",
            "first_name": "Pedro",
            "last_name": "Pereira",
            "password": "pedropedro",
            "birth_date": "1980-11-04",
            "phone_number": "966725567"
        })
        cur_success = cur_success and success
        success, state = add_client({
            "height": 160,
            "weight_goal": 70,
            "current_weight": 100,
            "sex": "M",
            "email": "miguel.pereira@gmail.com",
            "first_name": "Miguel",
            "last_name": "Pereira",
            "password": "12345ola",
            "birth_date": "1990-10-10",
            "phone_number": "916735360"
        })
        cur_success = cur_success and success
        success, state = add_client({
            "height": 180,
            "weight_goal": 70,
            "current_weight": 100,
            "sex": "F",
            "email": "manuela.silva@gmail.com",
            "first_name": "Manuela",
            "last_name": "Silva",
            "password": "12345ola",
            "birth_date": "1990-10-10",
            "phone_number": "912684259"
        })
        cur_success = cur_success and success
        success, state = add_client({
            "height": 172,
            "weight_goal": 80,
            "current_weight": 98,
            "sex": "M",
            "email": "antonio.almeida@gmail.com",
            "first_name": "António",
            "last_name": "Almeida",
            "password": "12345ola",
            "birth_date": "1990-10-11",
            "phone_number": "968124520"
        })
        cur_success = cur_success and success
        success, state = add_client({
            "height": 174,
            "weight_goal": 75,
            "current_weight": 99,
            "sex": "M",
            "email": "paulo.silva@gmail.com",
            "first_name": "Paulo",
            "last_name": "Silva",
            "password": "12345ola",
            "birth_date": "1990-10-20",
            "phone_number": "930407895"
        })
        cur_success = cur_success and success
        success, state = add_client({
            "height": 170,
            "weight_goal": 80,
            "current_weight": 110,
            "sex": "M",
            "email": "andre.silva@gmail.com",
            "first_name": "André",
            "last_name": "Silva",
            "password": "12345ola",
            "birth_date": "1990-06-04",
            "phone_number": "910348305"
        })
        cur_success = cur_success and success
        success, state = add_client({
            "height": 165,
            "weight_goal": 70,
            "current_weight": 100,
            "sex": "M",
            "email": "miguel.matos@gmail.com",
            "first_name": "Miguel",
            "last_name": "Matos",
            "password": "12345ola",
            "birth_date": "1980-10-04",
            "phone_number": "930438012"
        })
        cur_success = cur_success and success
        success, state = add_client({
            "height": 165,
            "weight_goal": 70,
            "current_weight": 100,
            "sex": "M",
            "email": "miguel.pedroso@gmail.com",
            "first_name": "Miguel",
            "last_name": "Pedroso",
            "password": "12345ola",
            "birth_date": "1980-06-04",
            "phone_number": "915005009"
        })
        cur_success = cur_success and success
        success, state = add_client({
            "height": 165,
            "weight_goal": 70,
            "current_weight": 100,
            "sex": "M",
            "email": "alberto.matos@gmail.com",
            "first_name": "Alberto",
            "last_name": "Matos",
            "password": "12345ola",
            "birth_date": "1988-10-04",
            "phone_number": "910002068"
        })
        cur_success = cur_success and success
        success, state = add_client({
            "height": 165,
            "weight_goal": 70,
            "current_weight": 100,
            "sex": "M",
            "email": "alberto.marques@gmail.com",
            "first_name": "Alberto",
            "last_name": "Marques",
            "password": "12345ola",
            "birth_date": "1980-10-06",
            "phone_number": "930002789"
        })
        cur_success = cur_success and success
        success, state = add_client({
            "height": 165,
            "weight_goal": 70,
            "current_weight": 100,
            "sex": "M",
            "email": "agostinho.matos@gmail.com",
            "first_name": "Agostinho",
            "last_name": "Matos",
            "password": "12345ola",
            "birth_date": "1980-12-12",
            "phone_number": "913000555"
        })
        cur_success = cur_success and success
        success, state = add_client({
            "height": 165,
            "weight_goal": 70,
            "current_weight": 100,
            "sex": "F",
            "email": "albertina.matos@gmail.com",
            "first_name": "Albertina",
            "last_name": "Matos",
            "password": "12345ola",
            "birth_date": "1978-10-04",
            "phone_number": "908000458"
        })
        cur_success = cur_success and success

        #######################################
        #          CREATE USERS - DOCTORS     #
        #######################################
        success, state = add_doctor({
            "email": "andre.almeida@gmail.com",
            "first_name": "André",
            "last_name": "Almeida",
            "password": "qwerty12345",
            "birth_date": "1980-05-10",
            "phone_number": "966565565"
        },
            hospital='Hospital São João')
        cur_success = cur_success and success
        success, state = add_doctor({
            "email": "rui.pereira@gmail.com",
            "first_name": "Rui",
            "last_name": "Pereira",
            "password": "asdfgh",
            "birth_date": "1985-05-04",
            "phone_number": "964275097"
        },
            hospital='Hospital Santo António')
        cur_success = cur_success and success
        success, state = add_doctor({
            "email": "joao.pereira@gmail.com",
            "first_name": "João",
            "last_name": "Pereira",
            "password": "987654",
            "birth_date": "1985-09-16",
            "phone_number": "914608627"
        },
            hospital='Hospital da Luz')
        cur_success = cur_success and success

        #######################################
        #    CREATE USERS - DOCTOR-PATIENT    #
        #######################################
        success, state = add_doctor_patient_association({"client": "vasco.almeida@gmail.com"},
                                                        email="andre.almeida@gmail.com")
        cur_success = cur_success and success
        success, state = add_doctor_patient_association({"client": "albertina.matos@gmail.com"},
                                                        email="andre.almeida@gmail.com")
        cur_success = cur_success and success
        success, state = add_doctor_patient_association({"client": "agostinho.matos@gmail.com"},
                                                        email="andre.almeida@gmail.com")
        cur_success = cur_success and success
        success, state = add_doctor_patient_association({"client": "alberto.marques@gmail.com"},
                                                        email="andre.almeida@gmail.com")
        cur_success = cur_success and success
        success, state = add_doctor_patient_association({"client": "alberto.matos@gmail.com"},
                                                        email="andre.almeida@gmail.com")
        cur_success = cur_success and success
        success, state = add_doctor_patient_association({"client": "miguel.pedroso@gmail.com"},
                                                        email="andre.almeida@gmail.com")
        cur_success = cur_success and success
        success, state = add_doctor_patient_association({"client": "miguel.matos@gmail.com"},
                                                        email="andre.almeida@gmail.com")
        cur_success = cur_success and success
        success, state = add_doctor_patient_association({"client": "andre.silva@gmail.com"},
                                                        email="andre.almeida@gmail.com")
        cur_success = cur_success and success
        success, state = add_doctor_patient_association({"client": "paulo.silva@gmail.com"},
                                                        email="andre.almeida@gmail.com")
        cur_success = cur_success and success
        success, state = add_doctor_patient_association({"client": "antonio.almeida@gmail.com"},
                                                        email="andre.almeida@gmail.com")
        cur_success = cur_success and success

        success, state = add_doctor_patient_association({"client": "ana.almeida@gmail.com"},
                                                        email="rui.pereira@gmail.com")
        cur_success = cur_success and success
        success, state = add_doctor_patient_association({"client": "manuela.silva@gmail.com"},
                                                        email="rui.pereira@gmail.com")
        cur_success = cur_success and success
        success, state = add_doctor_patient_association({"client": "miguel.pereira@gmail.com"},
                                                        email="rui.pereira@gmail.com")
        cur_success = cur_success and success
        success, state = add_doctor_patient_association({"client": "pedro.pereira@gmail.com"},
                                                        email="rui.pereira@gmail.com")
        cur_success = cur_success and success

        success, state = add_doctor_patient_association({"client": "miguel.silva@gmail.com"},
                                                        email="joao.pereira@gmail.com")
        cur_success = cur_success and success

        #######################################
        #          CREATE INGREDIENTS         #
        #######################################
        flour = Ingredient.objects.create(name="Flour", calories=364, carbs=76.3, fat=1, proteins=10.3)
        water = Ingredient.objects.create(name="Water", calories=0, carbs=0, fat=0, proteins=0)
        sugar = Ingredient.objects.create(name="Sugar", calories=389, carbs=99.8, fat=0, proteins=0)
        salt = Ingredient.objects.create(name="Salt", calories=0, carbs=0, fat=0, proteins=0)
        oil = Ingredient.objects.create(name="Oil", calories=884, carbs=0, fat=100, proteins=0)
        tomato_sauce = Ingredient.objects.create(name="Tomato Sauce", calories=82, carbs=18.9, fat=0.5, proteins=4.3)
        pepper = Ingredient.objects.create(name="Pepper", calories=251, carbs=64, fat=3.3, proteins=10.4)
        mozzarella_cheese = Ingredient.objects.create(name="Mozzarella Cheese", calories=300, carbs=2.2, fat=22.4,
                                                      proteins=22.2)
        pork = Ingredient.objects.create(name="Pork", calories=275, carbs=0.8, fat=10, proteins=19)
        egg = Ingredient.objects.create(name="Egg", calories=143, carbs=0.7, fat=9.5, proteins=12.6)
        garlic = Ingredient.objects.create(name="Garlic", calories=149, carbs=33.1, fat=0.5, proteins=6.4)
        onion = Ingredient.objects.create(name="Onion", calories=32, carbs=7.5, fat=0.1, proteins=0.8)
        cheese = Ingredient.objects.create(name="Cheese", calories=264, carbs=0, fat=21.1, proteins=18.5)

        #######################################
        #            CREATE MEALS             #
        #######################################
        meal = {"name": "Pizza", "category": "Fast Food",
                "ingredients": [{"id": water.id, "quantity": 42}, {"id": flour.id, "quantity": 39.4},
                                {"id": sugar.id, "quantity": 0.8}, {"id": salt.id, "quantity": 1.25},
                                {"id": oil.id, "quantity": 1.25}, {"id": tomato_sauce.id, "quantity": 15.63},
                                {"id": pepper.id, "quantity": 1.88}, {"id": mozzarella_cheese.id, "quantity": 15.7}]}
        success, state = add_new_meal(meal, None)
        cur_success = cur_success and success

        meal = {"name": "Hamburger", "category": "Fast Food",
                "ingredients": [{"id": pork.id, "quantity": 85}, {"id": salt.id, "quantity": 10},
                                {"id": pepper.id, "quantity": 10}, {"id": egg.id, "quantity": 50},
                                {"id": garlic.id, "quantity": 5}, {"id": onion.id, "quantity": 15},
                                {"id": cheese.id, "quantity": 28}]}
        success, state = add_new_meal(meal, None)
        cur_success = cur_success and success

        try:
            meals_json, ingredients_json = load_from_files('../db_data/')
            # print(meals_json)
            # print(ingredients_json)
        except Exception as e:
            print(e)

        for ingredient in ingredients_json:
            success, state = add_new_ingredient(ingredient)
            if not success:
                print(ingredient)
            cur_success = cur_success and success

        for meal in meals_json:
            success, state = add_new_meal(meal, None)
            if not success:
                print(meal)
            cur_success = cur_success and success

        return cur_success

    except Exception:
        return False

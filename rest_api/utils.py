from datetime import datetime, date, timedelta

from django.contrib.auth.models import User
from django.db.models import Sum
from rest_framework.authtoken.models import Token

from rest_api.models import Doctor, HospitalAdmin, Client, MealHistory
from rest_api.serializers import MealHistorySerializer

FAT_IMPORTANCE = 9
CARBS_IMPORTANCE = 4
PROTEINS_IMPORTANCE = 4

FAT_RATIO = 0.3
CARBS_RATIO = 0.5
PROTEINS_RATIO = 0.2


def get_role(username, request=None):
    role = None
    try:
        if username is None:
            username = request.user.username

        if User.objects.get(username=username).is_superuser:
            role = "django-admin"
        elif User.objects.get(username=username).groups.all()[0].name in ["admins_group"]:
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
    admin_hospital = HospitalAdmin.objects.get(auth_user__username=admin_username).hospital
    return admin_hospital == doctor_hospital


def is_client_doctor(doctor_username, client_username):
    if not get_role(client_username) == "client":
        return False

    doctor = Doctor.objects.get(user__auth_user__username=doctor_username)
    client = Client.objects.get(user__auth_user__username=client_username)
    return client.doctor == doctor


# populate meal nutrient values with values from ingredient passed or ingredients queried
def populate_nutrient_values(meal, ingredient=None, quantity=None):
    # if already have ingredient and quantity, use those
    if ingredient is not None and quantity is not None:
        old_meal = meal[0]
        new_calories = old_meal.calories + quantity * ingredient.calories / 100
        meal.update(calories=new_calories)
        new_proteins = old_meal.proteins + quantity * ingredient.proteins / 100
        meal.update(proteins=new_proteins)
        new_fat = old_meal.fat + quantity * ingredient.fat / 100
        meal.update(fat=new_fat)
        new_carbs = old_meal.carbs + quantity * ingredient.carbs / 100
        meal.update(carbs=new_carbs)
    # else query
    else:
        entries = meal.quantity_set.all()
        meal.update(calories=sum(entry.quantity * entry.ingredient.calories / 100 for entry in entries))
        meal.update(proteins=sum(entry.quantity * entry.ingredient.proteins / 100 for entry in entries))
        meal.update(fat=sum(entry.quantity * entry.ingredient.fat / 100 for entry in entries))
        meal.update(carbs=sum(entry.quantity * entry.ingredient.carbs / 100 for entry in entries))


def populate_nutrient_values_meal_history(meal_history, meal=None, number_of_servings=None):
    if meal is None:
        meal = meal_history[0].meal
    if number_of_servings is None:
        number_of_servings = meal_history[0].number_of_servings
    meal_history.update(calories=number_of_servings * meal.calories)
    meal_history.update(proteins=number_of_servings * meal.proteins)
    meal_history.update(carbs=number_of_servings * meal.carbs)
    meal_history.update(fat=number_of_servings * meal.fat)


def is_valid_date(date, date_pattern):
    ret_val = True

    try:
        datetime.strptime(date, date_pattern)
    except ValueError:
        ret_val = False

    return ret_val


def get_total_nutrients(meal_history):
    total_calories = round(sum(entry.calories for entry in meal_history), 0)
    total_carbs = round(sum(entry.carbs for entry in meal_history), 0)
    total_fat = round(sum(entry.fat for entry in meal_history), 0)
    total_proteins = round(sum(entry.proteins for entry in meal_history), 0)

    nutrients_info = {
        "calories": {"total": total_calories},
        "carbs": {"total": total_carbs},
        "fat": {"total": total_fat},
        "proteins": {"total": total_proteins},
    }

    return nutrients_info


def get_client_age(birth_date):
    today = date.today()

    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    return age


def get_calories_daily_goal(client):
    sex = client.sex
    weight = client.current_weight
    weight_goal = client.weight_goal
    height = client.height
    age = get_client_age(client.user.birth_date)

    if sex == "M":
        daily_cal_goal = (10 * weight) + (6.25 * height) - (5 * age) + 5

    else:
        daily_cal_goal = (10 * weight) + (6.25 * height) - (5 * age) - 161

    daily_cal_goal *= 1.55

    if weight_goal > weight:
        daily_cal_goal += 500
    else:
        daily_cal_goal -= 500

    return round(daily_cal_goal, 0)


def get_daily_goals(client):
    calories_goal = get_calories_daily_goal(client)
    carbs_goal = round(CARBS_RATIO * calories_goal / CARBS_IMPORTANCE, 0)
    fat_goal = round(FAT_RATIO * calories_goal / FAT_IMPORTANCE, 0)
    protein_goal = round(PROTEINS_RATIO * calories_goal / PROTEINS_IMPORTANCE, 0)

    return {"calories": calories_goal, "carbs": carbs_goal, "fat": fat_goal, "proteins": protein_goal}


def get_nutrients_info(client, info_dict):
    total_calories = info_dict["calories"]["total"]
    total_carbs = CARBS_IMPORTANCE * info_dict["carbs"]["total"]
    total_fat = FAT_IMPORTANCE * info_dict["fat"]["total"]
    total_proteins = PROTEINS_IMPORTANCE * info_dict["proteins"]["total"]
    total_others = total_calories - (total_carbs + total_fat + total_proteins)

    info_dict["carbs"]["ratio"] = round(total_carbs / total_calories * 100, 0)
    info_dict["fat"]["ratio"] = round(total_fat / total_calories * 100, 0)
    info_dict["proteins"]["ratio"] = round(total_proteins / total_calories * 100, 0)
    info_dict["others"] = {"ratio": round(total_others / total_calories * 100, 0)}

    goals = get_daily_goals(client)

    info_dict["carbs"]["goals"] = {"total": round(goals["carbs"], 0), "ratio": CARBS_IMPORTANCE * 100}
    info_dict["fat"]["goals"] = {"total": round(goals["fat"], 0), "ratio": FAT_RATIO * 100}
    info_dict["proteins"]["goals"] = {"total": round(goals["proteins"], 0), "ratio": PROTEINS_RATIO * 100}
    info_dict["calories"]["goals"] = round(goals["calories"], 0)

    return info_dict


def get_nutrients_left_values(client, info_dict):
    total_calories = info_dict["calories"]["total"]
    total_carbs = info_dict["carbs"]["total"]
    total_fat = info_dict["fat"]["total"]
    total_proteins = info_dict["proteins"]["total"]

    goals = get_daily_goals(client)

    carbs_goal = round(goals["carbs"], 0)
    fat_goal = round(goals["fat"], 0)
    calories_goal = round(goals["calories"], 0)
    proteins_goal = round(goals["proteins"], 0)

    left_carbs = total_carbs - carbs_goal
    left_calories = total_calories - calories_goal
    left_fat = total_fat - fat_goal
    left_proteins = total_proteins - proteins_goal

    info_dict["carbs"]["goal"] = carbs_goal
    info_dict["carbs"]["left"] = left_carbs
    info_dict["fat"]["goal"] = fat_goal
    info_dict["fat"]["left"] = left_fat
    info_dict["proteins"]["goal"] = proteins_goal
    info_dict["proteins"]["left"] = left_proteins
    info_dict["calories"]["goal"] = calories_goal
    info_dict["calories"]["left"] = left_calories

    return info_dict


def get_nutrient_history(client, metric, period):
    end_date = date.today()
    num_days = 0
    if period == "week":
        num_days = 7
    elif period == "month":
        num_days = 30
    elif period == "3-months":
        num_days = 3 * 30

    start_date = end_date - timedelta(days=num_days)

    history = MealHistory.objects.filter(client=client, day__gt=start_date, day__lte=end_date).values_list("day")

    if metric == "calories":
        history_per_day = history.annotate(Sum("calories"))
    elif metric == "fat":
        history_per_day = history.annotate(Sum("fat"))
    elif metric == "carbs":
        history_per_day = history.annotate(Sum("carbs"))
    elif metric == "proteins":
        history_per_day = history.annotate(Sum("proteins"))

    total_history = [{"day": str(start_date + timedelta(days=x)), "value": 0} for x in range(1, num_days + 1)]
    day_array = [entry["day"] for entry in total_history]

    for entry in history_per_day:
        day, value = str(entry[0]), entry[1]
        empty_history_idx = day_array.index(day)
        total_history[empty_history_idx] = {"day": day, "value": value}

    calories_goal = get_calories_daily_goal(client)
    goal = None
    if metric == "calories":
        goal = calories_goal
    elif metric == "fat":
        goal = calories_goal * FAT_RATIO / FAT_IMPORTANCE
    elif metric == "carbs":
        goal = calories_goal * CARBS_RATIO / CARBS_IMPORTANCE
    elif metric == "proteins":
        goal = calories_goal * PROTEINS_RATIO / PROTEINS_IMPORTANCE

    return {"goal": round(goal, 0), "history": total_history}


def group_meals(meal_history, client):
    types_of_meal = ["breakfast", "lunch", "dinner", "snack"]

    total_calories = round(sum(meal.calories for meal in meal_history))
    calories_goal = get_calories_daily_goal(client)
    calories_left = total_calories - calories_goal
    data = {"total_calories": total_calories, "calories_goal": calories_goal, "calories_left": calories_left}

    for type_of_meal in types_of_meal:
        meals = [MealHistorySerializer(meal).data for meal in meal_history if
                 meal.type_of_meal.lower() == type_of_meal.lower()]
        data[type_of_meal] = {"total_calories": round(sum(entry["calories"] for entry in meals), 0), "meals": meals}

    return data


def get_body_history_values(api, metric, period):
    if period == "week":
        period = "1w"
    elif period == "month":
        period = "1m"
    elif period == "3-months":
        period = "3m"

    response = api.time_series(f"activities/{metric}", period=period)[f"activities-{metric}"]

    if metric == "heart":
        response = [{"dateTime": e["dateTime"],
                     "value": e["value"]["restingHeartRate"] if "restingHeartRate" in e["value"] else 0} for e in
                    response]

    history = {"metric": metric, "history": response}

    if metric in ["steps", "distance", "calories", "floors"]:
        goals = api.activities_daily_goal()["goals"]
        history["goal"] = goals["caloriesOut"] if metric == "calories" else goals[str(metric)]

    return history

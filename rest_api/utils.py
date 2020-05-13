from datetime import datetime, date, timedelta

import requests
from django.contrib.auth.models import User
from django.db.models import Sum
from rest_framework.authtoken.models import Token

from rest_api.models import Doctor, HospitalAdmin, Client, MealHistory
from rest_api.serializers import MealHistorySerializer

API_URL = "https://%s.openfoodfacts.org"

FAT_IMPORTANCE = 9
CARBS_IMPORTANCE = 4
PROTEINS_IMPORTANCE = 4

FAT_RATIO = 0.3
CARBS_RATIO = 0.5
PROTEINS_RATIO = 0.2

HEART_RATE_CHART = {
    "M": {"18-25": {"49-61": "Excellent", "62-65": "Good", "66-73": "Average", "74-81": "Fair", "82": "Poor"},
          "26-35": {"49-61": "Excellent", "62-65": "Good", "66-74": "Average", "75-81": "Fair", "82": "Poor"},
          "36-45": {"50-62": "Excellent", "63-66": "Good", "67-75": "Average", "76-82": "Fair", "83": "Poor"},
          "46-55": {"50-63": "Excellent", "64-67": "Good", "68-71": "Average", "72-83": "Fair", "84": "Poor"},
          "56-65": {"51-61": "Excellent", "62-67": "Good", "68-71": "Average", "72-81": "Fair", "81": "Poor"},
          "66+": {"50-61": "Excellent", "62-65": "Good", "66-69": "Average", "70-79": "Fair", "80": "Poor"}},
    "F": {"18-25": {"54-65": "Excellent", "66-69": "Good", "70-78": "Average", "79-84": "Fair", "85": "Poor"},
          "26-35": {"54-64": "Excellent", "65-68": "Good", "69-76": "Average", "77-82": "Fair", "83": "Poor"},
          "36-45": {"54-64": "Excellent", "65-69": "Good", "70-78": "Average", "79-84": "Fair", "85": "Poor"},
          "46-55": {"54-65": "Excellent", "66-69": "Good", "70-77": "Average", "78-83": "Fair", "84": "Poor"},
          "56-65": {"54-64": "Excellent", "65-68": "Good", "69-73": "Average", "74-83": "Fair", "84": "Poor"},
          "66+": {"55-64": "Excellent", "65-68": "Good", "69-72": "Average", "73-84": "Fair", "85": "Poor"}}}


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
    total_calories = round(sum(entry.calories for entry in meal_history))
    total_carbs = round(sum(entry.carbs for entry in meal_history))
    total_fat = round(sum(entry.fat for entry in meal_history))
    total_proteins = round(sum(entry.proteins for entry in meal_history))

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

    return round(daily_cal_goal)


#TODO: improve this...
def get_daily_goals(client):
    if client.is_diabetic and client.has_high_colesterol:
        carbs_ratio = CARBS_RATIO
        fat_ratio = FAT_RATIO
        proteins_ratio = PROTEINS_RATIO
    elif client.is_diabetic:
        carbs_ratio = 0.4
        fat_ratio = 0.3
        proteins_ratio = 0.3
    elif client.has_high_colesterol:
        carbs_ratio = 0.5
        fat_ratio = 0.2
        proteins_ratio = 0.3
    else:
        carbs_ratio = CARBS_RATIO
        fat_ratio = FAT_RATIO
        proteins_ratio = PROTEINS_RATIO

    calories_goal = get_calories_daily_goal(client)
    carbs_goal = round(carbs_ratio * calories_goal / CARBS_IMPORTANCE)
    fat_goal = round(fat_ratio * calories_goal / FAT_IMPORTANCE)
    protein_goal = round(proteins_ratio * calories_goal / PROTEINS_IMPORTANCE)

    return {"calories": calories_goal, "carbs": carbs_goal, "fat": fat_goal, "proteins": protein_goal}


def get_nutrients_info(client, info_dict):
    total_calories = info_dict["calories"]["total"]
    total_carbs = CARBS_IMPORTANCE * info_dict["carbs"]["total"]
    total_fat = FAT_IMPORTANCE * info_dict["fat"]["total"]
    total_proteins = PROTEINS_IMPORTANCE * info_dict["proteins"]["total"]
    total_others = total_calories - (total_carbs + total_fat + total_proteins)

    info_dict["carbs"]["ratio"] = round(total_carbs / total_calories * 100)
    info_dict["fat"]["ratio"] = round(total_fat / total_calories * 100)
    info_dict["proteins"]["ratio"] = round(total_proteins / total_calories * 100)
    info_dict["others"] = {"ratio": round(total_others / total_calories * 100)}

    goals = get_daily_goals(client)

    info_dict["carbs"]["goals"] = {"total": round(goals["carbs"]), "ratio": round(CARBS_RATIO * 100)}
    info_dict["fat"]["goals"] = {"total": round(goals["fat"]), "ratio": round(FAT_RATIO * 100)}
    info_dict["proteins"]["goals"] = {"total": round(goals["proteins"]), "ratio": round(PROTEINS_RATIO * 100)}
    info_dict["calories"]["goals"] = round(goals["calories"])

    return info_dict


def get_nutrients_left_values(client, info_dict):
    total_calories = info_dict["calories"]["total"]
    total_carbs = info_dict["carbs"]["total"]
    total_fat = info_dict["fat"]["total"]
    total_proteins = info_dict["proteins"]["total"]

    goals = get_daily_goals(client)

    carbs_goal = round(goals["carbs"])
    fat_goal = round(goals["fat"])
    calories_goal = round(goals["calories"])
    proteins_goal = round(goals["proteins"])

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

    return {"goal": round(goal), "history": total_history}


def group_meals(meal_history, client):
    types_of_meal = ["breakfast", "lunch", "dinner", "snack"]

    total_calories = round(sum(meal.calories for meal in meal_history))
    calories_goal = get_calories_daily_goal(client)
    calories_left = total_calories - calories_goal
    data = {"total_calories": total_calories, "calories_goal": calories_goal, "calories_left": calories_left}

    for type_of_meal in types_of_meal:
        meals = [MealHistorySerializer(meal).data for meal in meal_history if
                 meal.type_of_meal.lower() == type_of_meal.lower()]
        data[type_of_meal] = {"total_calories": round(sum(entry["calories"] for entry in meals)), "meals": meals}

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


def get_client_heart_rate_chart(client, api):
    sex = client.sex
    age = get_client_age(client.user.birth_date)

    message = {"scale": None, "scale_sizes": None, "avg_heart_rate": None, "label": None, "sex": sex}

    heart_rate_chart_all_ages = HEART_RATE_CHART[sex]

    if age <= 25:
        heart_rate_chart = heart_rate_chart_all_ages["18-25"]
    elif 26 <= age <= 35:
        heart_rate_chart = heart_rate_chart_all_ages["26-35"]
    elif 36 <= age <= 45:
        heart_rate_chart = heart_rate_chart_all_ages["36-45"]
    elif 46 <= age <= 55:
        heart_rate_chart = heart_rate_chart_all_ages["46-55"]
    elif 56 <= age <= 65:
        heart_rate_chart = heart_rate_chart_all_ages["56-65"]
    else:
        heart_rate_chart = heart_rate_chart_all_ages["66+"]

    message["scale"] = heart_rate_chart

    response = api.time_series("activities/heart", period="1m")["activities-heart"]
    heart_rate_history = [e["value"]["restingHeartRate"] for e in response if "restingHeartRate" in e["value"]]
    history_len = len(heart_rate_history)
    avg_heart_rate = sum(heart_rate_history) / history_len if history_len != 0 else 60
    message["avg_heart_rate"] = round(avg_heart_rate, 1)

    heart_rate_chart_indexes = heart_rate_chart.keys()
    scale_sizes = []
    actual_index = None
    for index in heart_rate_chart_indexes:
        index_lst = index.split("-")
        if len(index_lst) == 2:
            min, max = index_lst
            scale_sizes.append(int(max) - int(min) + 1)
            if int(min) <= avg_heart_rate <= int(max):
                actual_index = index
        else:
            scale_sizes.append(100 - int(index) + 1)
            if avg_heart_rate >= int(index):
                actual_index = index

    message["scale_sizes"] = scale_sizes
    message["label"] = heart_rate_chart[actual_index]
    return message


def get_my_life_stats(client, api=None):
    # current week
    current_end_date = date.today()
    current_start_date = current_end_date - timedelta(days=6)

    # previous week
    previous_end_date = date.today() - timedelta(days=7)
    previous_start_date = previous_end_date - timedelta(days=6)

    if api is None:
        current_week_my_life, current_week_my_life_label = get_my_life_value_nutrients_only(current_start_date,
                                                                                            current_end_date, client)
        previous_week_my_life, previous_week_my_life_label = get_my_life_value_nutrients_only(previous_start_date,
                                                                                              previous_end_date, client)

    else:
        current_week_my_life, current_week_my_life_label = get_my_life_value_fitbit(current_start_date,
                                                                                    current_end_date, client, api)
        previous_week_my_life, previous_week_my_life_label = get_my_life_value_fitbit(previous_start_date,
                                                                                      previous_end_date, client, api)

    if current_week_my_life == 0:
        current_week_my_life = 0.1

    if previous_week_my_life == 0:
        previous_week_my_life = 0.1

    increase = 100 * (current_week_my_life - previous_week_my_life) / previous_week_my_life

    scale = {"0-2": "Poor", "2-4": "Average", "4-5": "Excellent"}
    scale_sizes = [2, 2, 1]

    return {"scale": scale, "scale_sizes": scale_sizes,
            "current_week": {"value": current_week_my_life, "label": current_week_my_life_label},
            "previous_week": {"value": previous_week_my_life, "label": previous_week_my_life_label},
            "increase": round(increase), "sex": client.sex}


def get_my_life_value_nutrients_only(start_date, end_date, client):
    calories_goal = get_calories_daily_goal(client)

    history = MealHistory.objects.filter(client=client, day__gt=start_date, day__lte=end_date).values_list("day")
    calories_history = [round(entry[1]) for entry in history.annotate(Sum("calories"))]
    total_week_calories = sum(calories_history)
    total_week_calories_goal = calories_goal * len(calories_history)

    difference = total_week_calories - total_week_calories_goal
    diff_ratio = round(difference / total_week_calories_goal * 100) if total_week_calories_goal != 0 else 100

    my_life_metric, label = evaluate_difference_ratio(client, diff_ratio)

    return round(my_life_metric, 1), label


def get_my_life_value_fitbit(start_date, end_date, client, api):
    calories_goal = get_calories_daily_goal(client)
    total_week_calories_goal = 7 * calories_goal

    fitbit_history = api.time_series("activities/calories", base_date=str(end_date), period="1w")[
        "activities-calories"]
    fitbit_calories = [int(entry["value"]) for entry in fitbit_history]
    total_week_fitbit_calories = sum(fitbit_calories) + (7 - len(fitbit_calories)) * calories_goal

    history = MealHistory.objects.filter(client=client, day__gt=start_date, day__lte=end_date).values_list("day")
    calories_history = [round(entry[1]) for entry in history.annotate(Sum("calories"))]
    total_week_calories = sum(calories_history) + (7 - len(calories_history)) * calories_goal

    difference = total_week_calories - total_week_fitbit_calories
    diff_ratio = round(difference / total_week_calories_goal * 100)

    my_life_metric, label = evaluate_difference_ratio(client, diff_ratio)

    return round(my_life_metric, 1), label


def evaluate_difference_ratio(client, diff_ratio):
    mult_factor = 1 if client.weight_goal > client.current_weight else -1
    diff_ratio *= mult_factor

    if diff_ratio < 0:
        if diff_ratio < -100:
            diff_ratio = -100
        old_range = 0 - (-100)
        new_range = 2 - 0
        my_life_metric = (((diff_ratio - (-100)) * new_range) / old_range) + 0
        label = "Poor"

    elif 0 <= diff_ratio <= 15:
        old_range = 15 - 0
        new_range = 4 - 2
        my_life_metric = (((diff_ratio - 0) * new_range) / old_range) + 2
        label = "Average"

    elif 16 <= diff_ratio <= 25:
        old_range = 25 - 16
        new_range = 5 - 4
        my_life_metric = (((diff_ratio - 16) * new_range) / old_range) + 4
        label = "Excellent"

    else:
        if diff_ratio > 100:
            diff_ratio = 100
        old_range = 100 - 26
        new_range = 2 - 0
        my_life_metric = (((100 - diff_ratio) * new_range) / old_range) + 0
        label = "Poor"

    return my_life_metric, label


def process_meal_history_insert(client, inserted_item):
    goals = get_daily_goals(client)
    calories_goal = goals["calories"]
    fat_goal = goals["fat"]
    carbs_goal = goals["carbs"]
    proteins_goal = goals["proteins"]

    calories = inserted_item.calories
    fat = inserted_item.fat
    carbs = inserted_item.carbs
    proteins = inserted_item.proteins

    alerts = {"bad": [], "good": []}

    if calories > 0.5 * calories_goal:
        alerts["bad"].append("Your calories goal today is {:.0f} and this has {:.0f}.".format(calories_goal, calories))
    if fat > 0.5 * fat_goal:
        alerts["bad"].append("Your fat goal today is {:.0f} grams and this has {:.0f} grams.".format(fat_goal, fat))
    if carbs > 0.5 * carbs_goal:
        alerts["bad"].append(
            "Your carbs goal today is {:.0f} grams and this has {:.0f} grams.".format(carbs_goal, carbs))
    if proteins > 0.5 * proteins_goal:
        alerts["bad"].append(
            "Your proteins goal today is {:.0f} grams and this has {:.0f} grams.".format(proteins_goal, proteins))

    if proteins > 10:
        alerts["good"].append("This food is high on protein.")

    return alerts


def get_product(barcode, locale="world"):
    url = build_url(geography=locale, parameters=barcode)
    return fetch(url)


def build_url(geography="world", parameters=None):
    geo_url = API_URL % geography
    base_url = "/".join([geo_url, "api", "v0", "product", parameters])
    return base_url


def fetch(path, json_file=True):
    if json_file:
        path = "%s.json" % path

    response = requests.get(path)
    return response.json()

def load_from_files(data_dir):
    ingredients = []
    meals = []

    import sys, os, json

    cur_dir = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(cur_dir, data_dir)

    for f in os.listdir(path):
        if not 'json' in f or 'test' in f:
            continue
        file_path = os.path.join(path, f)
        with open(file_path, 'r', encoding='us-ascii') as ff:
            content = ff.read()
            contents_json = json.loads(content)
            if 'ingredients' in f:
                for ingredient in contents_json:
                    ingredients.append(ingredient)
            elif 'meals' in f:
                for meal in contents_json:
                    meals.append(meal)
    
    return meals, ingredients

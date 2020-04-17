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

# populate meal nutrient values with values from ingredient passed or ingredients queried
def populate_nutrient_values(meal, ingredient=None, quantity=None):
    # if already have ingredient and quantity, use those
    if ingredient is not None and quantity is not None: 
        new_calories = meal.calories + quantity * ingredient.calories / 100
        meal.update(calories=new_calories)
        new_proteins = meal.proteins + quantity * ingredient.proteins / 100
        meal.update(proteins=new_proteins)
        new_fat = meal.fat = quantity * ingredient.fat / 100
        meal.update(fat=new_fat)
        new_carbs = meal.carbs = quantity * ingredient.carbs / 100
        meal.update(carbs=new_carbs)
    # else query
    else:
        entries = meal.quantity_set.all()
        meal.update(calories = sum(entry.quantity * entry.ingredient.calories / 100 for entry in entries))
        meal.update(proteins = sum(entry.quantity * entry.ingredient.proteins / 100 for entry in entries))
        meal.update(fat = sum(entry.quantity * entry.ingredient.fat / 100 for entry in entries))
        meal.update(carbs = sum(entry.quantity * entry.ingredient.carbs / 100 for entry in entries))

def populate_nutrient_values_meal_history(meal_history, meal=None, number_of_servings=None):
    if meal is None:
        meal = meal_history.meal
    if number_of_servings is None:
        number_of_servings = meal_history.number_of_servings
    meal_history.update(calories = number_of_servings * meal.fat)
    meal_history.update(proteins = number_of_servings * meal.proteins)
    meal_history.update(carbs = number_of_servings * meal.carbs)
    meal_history.update(fat = number_of_servings * meal.fat)
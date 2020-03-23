from django.contrib.auth.models import User
from django.db import models


class CustomAdmin(models.Model):
    auth_user = models.OneToOneField(
        User, on_delete=models.CASCADE, unique=True, primary_key=True
    )
    hospital = models.CharField(max_length=100)


class CustomUser(models.Model):
    auth_user = models.OneToOneField(
        User, on_delete=models.CASCADE, unique=True, primary_key=True
    )
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    photo = models.TextField(null=True, blank=True)
    birth_date = models.DateField()


class Doctor(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, unique=True, primary_key=True
    )
    hospital = models.CharField(max_length=100)


class Client(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, unique=True, primary_key=True
    )
    height = models.FloatField()
    weight_goal = models.FloatField()
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)


class Ingredient(models.Model):
    calories = models.FloatField()
    proteins = models.FloatField()
    fat = models.FloatField()
    carbs = models.FloatField()
    name = models.CharField(max_length=30)


class Meal(models.Model):
    name = models.CharField(max_length=30)
    category = models.CharField(max_length=30)
    # https://docs.djangoproject.com/en/3.0/topics/db/models/#extra-fields-on-many-to-many-relationships
    ingredients = models.ManyToManyField(Ingredient, through="Quantity")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)


class Quantity(models.Model):
    ingredient = person = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    quantity = models.FloatField()


class MealHistory(models.Model):
    day = models.DateField()
    type_of_meal = models.CharField(max_length=25)
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    number_of_servings = models.FloatField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE)


class Exercise(models.Model):
    name = models.CharField(max_length=50)
    target_body_area = models.CharField(max_length=25)
    difficulty = models.IntegerField()


class Set(models.Model):
    exercise = models.ForeignKey(Exercise, on_delete=models.SET_NULL, null=True, blank=True)
    number_of_reps = models.IntegerField()
    time = models.FloatField()


class Workout(models.Model):
    workout_sets = models.ManyToManyField(Set)
    rest_time = models.DurationField()  # https://docs.djangoproject.com/en/3.0/ref/models/fields/#durationfield
    difficulty = models.IntegerField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE)

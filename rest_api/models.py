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


class MealCatalog(models.Model):
    name = models.CharField(max_length=30)
    type_of_meal = models.CharField(max_length=30)
    ingredients = models.ManyToManyField(Ingredient)


class Meal(models.Model):
    name = models.CharField(max_length=30)
    number_of_servings = models.FloatField()
    type_of_meal = models.CharField(max_length=30)
    ingredients = models.ManyToManyField(Ingredient)
    meal_from_catalog = models.ForeignKey(MealCatalog, on_delete=models.SET_NULL, null=True, blank=True)


class MealHistory(models.Model):
    day = models.DateField()
    meals = models.ManyToManyField(Meal)


class Exercise(models.Model):
    name = models.CharField(max_length=50)
    target_body_area = models.CharField(max_length=25)
    difficulty = models.IntegerField()


class Set(models.Model):
    exercise = models.OneToOneField(Exercise, on_delete=models.CASCADE)
    number_of_reps = models.IntegerField()
    time = models.FloatField()


class Workout(models.Model):
    workout_sets = models.ManyToManyField(Set)
    rest_time = models.DurationField()  # https://docs.djangoproject.com/en/3.0/ref/models/fields/#durationfield
    difficulty = models.IntegerField()

from django.contrib.auth.models import User
from django.db import models


class CustomUser(models.Model):
    auth_user = models.OneToOneField(
        User, on_delete=models.CASCADE, unique=True, primary_key=True
    )
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    photo = models.TextField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)


class Doctor(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, unique=True, primary_key=True
    )


class Client(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, unique=True, primary_key=True
    )
    height = models.FloatField(null=True, blank=True)
    weight_goal = models.FloatField(null=True, blank=True)


class Item(models.Model):
    name = models.CharField(max_length=20)
    calories = models.FloatField()
    proteins = models.FloatField()
    fat = models.FloatField()
    carbs = models.FloatField()
    number_of_servings = models.FloatField()


class Ingredient(models.Model):
    item = models.OneToOneField(
        Item, on_delete=models.CASCADE, unique=True, primary_key=True
    )


class Meal(models.Model):
    item = models.OneToOneField(
        Item, on_delete=models.CASCADE, unique=True, primary_key=True
    )
    ingredients = models.ManyToManyField(Ingredient)


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
    rest_time = (
        models.DurationField()
    )  # https://docs.djangoproject.com/en/3.0/ref/models/fields/#durationfield
    difficulty = models.IntegerField()



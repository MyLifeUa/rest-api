from django.db import models
from django.contrib.auth.models import User

# Create your models here.
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
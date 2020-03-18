from django.contrib import admin
from .models import *

admin.site.register(Ingredient)
admin.site.register(MealCatalog)
admin.site.register(Meal)
admin.site.register(MealHistory)
from django.contrib import admin

from .models import *

admin.site.register(Client)
admin.site.register(Doctor)
admin.site.register(HospitalAdmin)

admin.site.register(Ingredient)
admin.site.register(Quantity)
admin.site.register(Meal)
admin.site.register(MealHistory)

from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class ClientSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    height = serializers.FloatField()
    current_weight = serializers.FloatField()
    weight_goal = serializers.FloatField()

    def get_id(self, obj):
        return obj.user.auth_user.id

    def get_email(self, obj):
        return obj.user.auth_user.email

    def get_name(self, obj):
        return obj.user.auth_user.get_full_name()

    def get_phone_number(self, obj):
        return obj.user.phone_number

    def get_photo(self, obj):
        return obj.user.photo


class DoctorSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    hospital = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj.user.auth_user.id

    def get_email(self, obj):
        return obj.user.auth_user.email

    def get_name(self, obj):
        return obj.user.auth_user.get_full_name()

    def get_phone_number(self, obj):
        return obj.user.phone_number

    def get_photo(self, obj):
        return obj.user.photo

    def get_hospital(self, obj):
        return obj.hospital


class AdminSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    hospital = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj.auth_user.id

    def get_email(self, obj):
        return obj.auth_user.email

    def get_first_name(self, obj):
        return obj.auth_user.first_name

    def get_last_name(self, obj):
        return obj.auth_user.last_name

    def get_hospital(self, obj):
        return obj.hospital


class Meal(serializers.Serializer):  # TODO Finish this implementation, started to implement the MealHistorySerializer
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    number_of_servings = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj.id

    def get_name(self, obj):
        return obj.name

    def get_number_of_servings(self, obj):
        return obj.number_of_servings

    def get_category(self, obj):
        return obj.category


class MealHistorySerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    day = serializers.SerializerMethodField()
    type_of_meal = serializers.SerializerMethodField()
    meal_name = serializers.SerializerMethodField()
    number_of_servings = serializers.SerializerMethodField()
    meal_category = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj.id

    def get_day(self, obj):
        return obj.day

    def get_type_of_meal(self, obj):
        return obj.type_of_meal

    def get_meal_name(self, obj):
        return obj.meal.name

    def get_number_of_servings(self, obj):
        return obj.meal.number_of_servings

    def get_meal_category(self, obj):
        return obj.meal.category

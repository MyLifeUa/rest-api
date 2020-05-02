from rest_framework import serializers


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class ClientSerializer(serializers.Serializer):
    email = serializers.SerializerMethodField()
    password = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    birth_date = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    height = serializers.FloatField(required=True)
    current_weight = serializers.FloatField(required=True)
    weight_goal = serializers.FloatField(required=True)
    sex = serializers.CharField(required=True)

    def get_email(self, obj):
        return obj.user.auth_user.email

    def get_password(self, obj):
        return obj.user.auth_user.password

    def get_first_name(self, obj):
        return obj.user.auth_user.first_name

    def get_last_name(self, obj):
        return obj.user.auth_user.last_name

    def get_birth_date(self, obj):
        return obj.user.birth_date

    def get_phone_number(self, obj):
        return obj.user.phone_number

    def get_photo(self, obj):
        return obj.user.photo


class DoctorSerializer(serializers.Serializer):
    email = serializers.SerializerMethodField()
    password = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    birth_date = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()

    def get_email(self, obj):
        return obj.user.auth_user.email

    def get_password(self, obj):
        return obj.user.auth_user.password

    def get_first_name(self, obj):
        return obj.user.auth_user.first_name

    def get_last_name(self, obj):
        return obj.user.auth_user.last_name

    def get_birth_date(self, obj):
        return obj.user.birth_date

    def get_phone_number(self, obj):
        return obj.user.phone_number

    def get_photo(self, obj):
        return obj.user.photo


class AdminSerializer(serializers.Serializer):
    email = serializers.SerializerMethodField()
    password = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    hospital = serializers.CharField(required=True)

    def get_email(self, obj):
        return obj.auth_user.email

    def get_password(self, obj):
        return obj.user.auth_user.password

    def get_first_name(self, obj):
        return obj.auth_user.first_name

    def get_last_name(self, obj):
        return obj.auth_user.last_name


class MealHistorySerializer(serializers.Serializer):
    day = serializers.CharField(required=True)
    type_of_meal = serializers.CharField(required=True)
    number_of_servings = serializers.FloatField(required=True)
    meal = serializers.SerializerMethodField()

    def get_meal(self, obj):
        return obj.meal.id


class IngredientSerializer(serializers.Serializer):
    calories = serializers.FloatField(required=True)
    proteins = serializers.FloatField(required=True)
    fat = serializers.FloatField(required=True)
    carbs = serializers.FloatField(required=True)
    name = serializers.CharField(required=True)


class IngredientMinSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    quantity = serializers.FloatField()


class MealSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    category = serializers.CharField(required=True)
    ingredients = serializers.ListField(child=IngredientMinSerializer())


class ClientEmailSerializer(serializers.Serializer):
    client = serializers.CharField(required=True)


class ClientFitbitToken(serializers.Serializer):
    access_token = serializers.CharField(required=True)
    refresh_token = serializers.CharField(required=True)


class ExpoTokenSerializer(serializers.Serializer):
    expo_token = serializers.CharField(required=True)

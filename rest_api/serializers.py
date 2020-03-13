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
    name = serializers.SerializerMethodField()
    hospital = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj.auth_user.id

    def get_email(self, obj):
        return obj.auth_user.email

    def get_name(self, obj):
        return obj.auth_user.get_full_name()

    def get_hospital(self, obj):
        return obj.hospital

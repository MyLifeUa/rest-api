from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


def get_role(username, request=None):
    try:
        if username is None:
            username = request.user.username

        if User.objects.get(username=username).is_superuser:
            return "admin"
        elif User.objects.get(username=username).groups.all()[0].name in ["clients_group"]:
            return "client"
        elif User.objects.get(username=username).groups.all()[0].name in ["doctors_group"]:
            return "doctor"
        else:
            return None

    except User.DoesNotExist:
        return None


def who_am_i(request):
    token = Token.objects.get(user=request.user).key
    username = request.user.username
    role = get_role(username)

    return token, username, role


def verify_authorization(role, group):
    return role == group

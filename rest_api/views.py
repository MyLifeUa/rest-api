from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import *

from rest_api.models import *


def get_user_type(username, request=None):
    """
    This method is used to know the type of the user that is requesting some info.
    :param username:
    :param request:
    :return:
    """
    try:
        if username is None:
            username = request.user.username

        if User.objects.get(username=username).is_superuser:
            return "admin"
        elif User.objects.get(username=username).groups.all()[0].name in [
            "clients_group"
        ]:
            return "client"
        elif User.objects.get(username=username).groups.all()[0].name in [
            "doctors_group"
        ]:
            return "doctor"
        else:
            return None

    except User.DoesNotExist:
        return None


def who_am_i(request):
    """
    This method is used to know the username, token and type of the user that is requesting some info.
    :param request:
    :return:
    """
    token = Token.objects.get(user=request.user).key
    username = request.user.username
    user_type = get_user_type(username)

    return token, username, user_type


@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    """
    Functions that logs int the requester user. If there is a existing token, it returns that one.
    Otherwise, creates a new token for valid users.
    :param request: Who has made the request.
    :return: Response 200 with user_type, data and token, if everything goes smoothly.
    Or Response 404 for not found error.
    """
    """
    login_serializer = UserLoginSerializer(data=request.data)
    if not login_serializer.is_valid():
        return Response(login_serializer.errors, status=HTTP_400_BAD_REQUEST)

    user = authenticate(
        username=login_serializer.data["username"],
        password=login_serializer.data["password"],
    )
    if not user:
        message = "Credenciais para o login inválidas!"
        return Response({"detail": message}, status=HTTP_404_NOT_FOUND)

    # TOKEN STUFF
    token, _ = Token.objects.get_or_create(user=user)

    # token_expire_handler will check, if the token is expired it will generate new one
    is_expired, token = token_expire_handler(
        token
    )  # The implementation will be described further
    user_serialized = UserSerializer(user)

    return Response(
        {
            "user_type": get_user_type(user.username),
            "data": user_serialized.data,
            "token": token.key,
        },
        status=HTTP_200_OK,
    )
    """

    return Response(status=HTTP_200_OK)


@csrf_exempt
@api_view(["GET"])
def logout(request):
    """
    Functions that logs out the requester user and deletes the token associated with that user.
    :param request: Who has made the request
    :return: Response 200.
    """
    auth_token = request.META["HTTP_AUTHORIZATION"].split()[1]
    try:
        Token.objects.get(key=auth_token).delete()
    except Token.DoesNotExist:
        pass
    return Response(status=HTTP_200_OK)

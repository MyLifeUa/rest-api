from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_403_FORBIDDEN

from rest_api import queries
from rest_api.authentication import token_expire_handler
from rest_api.serializers import UserSerializer, UserLoginSerializer
from .utils import *


@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    login_serializer = UserLoginSerializer(data=request.data)
    if not login_serializer.is_valid():
        return Response(login_serializer.errors, status=HTTP_400_BAD_REQUEST)

    user = authenticate(
        username=login_serializer.data["username"],
        password=login_serializer.data["password"],
    )
    if not user:
        message = "Invalid login credentials!"
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
            "role": get_role(user.username),
            "data": user_serialized.data,
            "token": token.key,
        },
        status=HTTP_200_OK,
    )


@csrf_exempt
@api_view(["GET"])
def logout(request):
    auth_token = request.META["HTTP_AUTHORIZATION"].split()[1]
    try:
        Token.objects.get(key=auth_token).delete()
    except Token.DoesNotExist:
        pass
    return Response(status=HTTP_200_OK)


@api_view(["POST"])
@permission_classes((AllowAny,))
def new_client(request):
    data = request.data
    if not (
        "email" in data
        and "first_name" in data
        and "last_name" in data
        and "password" in data
        and "height" in data
        and "weight_goal" in data
    ):
        return Response(
            {"state": "Error", "message": "Missing parameters"},
            status=HTTP_400_BAD_REQUEST,
        )
    state, message, username = queries.add_client(data)
    state, status = (
        ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)
    )

    return Response({"state": state, "message": message}, status=status)


@api_view(["POST"])
def new_admin(request):
    token, username, role = who_am_i(request)

    if not verify_authorization(role, "admin"):
        state = "Error"
        message = "You do not have permissions to add a new admin"
        status = HTTP_403_FORBIDDEN
        return Response(
            {"role": role, "state": state, "message": message, "token": token},
            status=status,
        )

    data = request.data

    if not (
            "email" in data
            and "first_name" in data
            and "last_name" in data
            and "password" in data
            and "hospital" in data
    ):
        state = "Error"
        message = "Missing parameters"
        status = HTTP_400_BAD_REQUEST
        return Response(
            {"role": role, "state": state, "message": message, "token": token},
            status=status,
        )

    state, message, username = queries.add_admin(data)
    state, status = (
        ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)
    )

    return Response(
        {"role": role, "state": state, "message": message, "token": token},
        status=status,
    )

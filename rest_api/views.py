from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
)
from rest_api import queries, documentation_serializers as doc
from rest_api.authentication import token_expire_handler
from .utils import *
from .models import MealHistory
from .serializers import *


@swagger_auto_schema(method="post", request_body=doc.UserLoginSerializer)
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    login_serializer = UserLoginSerializer(data=request.data)
    if not login_serializer.is_valid():
        return Response(login_serializer.errors, status=HTTP_400_BAD_REQUEST)

    user = authenticate(username=login_serializer.data["username"], password=login_serializer.data["password"])

    if not user:
        message = "Invalid login credentials!"
        return Response({"detail": message}, status=HTTP_404_NOT_FOUND)

    # TOKEN STUFF
    token, _ = Token.objects.get_or_create(user=user)

    # token_expire_handler will check, if the token is expired it will generate new one
    is_expired, token = token_expire_handler(token)
    user_serialized = UserSerializer(user)

    return Response({"role": get_role(user.username), "data": user_serialized.data, "token": token.key},
                    status=HTTP_200_OK)


@csrf_exempt
@api_view(["GET"])
def logout(request):
    auth_token = request.META["HTTP_AUTHORIZATION"].split()[1]
    try:
        Token.objects.get(key=auth_token).delete()
    except Token.DoesNotExist:
        pass
    return Response(status=HTTP_200_OK)


@swagger_auto_schema(method="post", request_body=doc.AdminSerializer)
@api_view(["POST"])
def new_admin(request):
    token, username, role = who_am_i(request)

    if not verify_authorization(role, "admin"):
        state = "Error"
        message = "You do not have permissions to add a new admin"
        status = HTTP_403_FORBIDDEN
        return Response({"role": role, "state": state, "message": message, "token": token},
                        status=status)

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
        return Response({"role": role, "state": state, "message": message, "token": token}, status=status)

    state, message = queries.add_admin(data)
    state, status = ("Success", HTTP_201_CREATED) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@swagger_auto_schema(method="put", request_body=doc.AdminSerializer)
@api_view(["GET", "PUT", "DELETE"])
def admin_rud(request, email):
    if request.method == "PUT":
        return update_admin(request, email)
    elif request.method == "DELETE":
        return delete_admin(request, email)
    elif request.method == "GET":
        return get_admin(request, email)


def update_admin(request, email):
    token, username, role = who_am_i(request)

    # default possibility
    state = "Error"
    message = "You do not have permissions to update this account"
    status = HTTP_403_FORBIDDEN

    if is_self(role, "admin", username, email):
        state, message = queries.update_admin(request, email)
        status = HTTP_200_OK if state else HTTP_400_BAD_REQUEST

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


def delete_admin(request, email):
    token, username, role = who_am_i(request)

    try:
        user = User.objects.get(username=email)
    except User.DoesNotExist:
        state = "Error"
        message = "User does not exist!"
        status = HTTP_400_BAD_REQUEST
        return Response({"role": role, "state": state, "message": message, "token": token},
                        status=status)

    # default possibility
    state = "Error"
    message = "You don't have permissions to delete this account"
    status = HTTP_403_FORBIDDEN

    if is_self(role, "admin", username, email):
        state, message = queries.delete_user(user)
        state, status = ("Success", HTTP_204_NO_CONTENT) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


def get_admin(request, email):
    token, username, role = who_am_i(request)

    # default possibility
    state = "Error"
    message = "You don't have permissions to access this account info"
    status = HTTP_403_FORBIDDEN

    if is_self(role, "admin", username, email):
        state, message = queries.get_admin(username)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@swagger_auto_schema(method="post", request_body=doc.ClientSerializer)
@api_view(["POST"])
@permission_classes((AllowAny,))
def new_client(request):
    data = request.data
    if not ("email" in data
            and "first_name" in data
            and "last_name" in data
            and "password" in data
            and "height" in data
            and "current_weight" in data
            and "weight_goal" in data
            and "birth_date" in data):
        return Response({"state": "Error", "message": "Missing parameters"}, status=HTTP_400_BAD_REQUEST)

    state, message = queries.add_client(data)
    state, status = ("Success", HTTP_201_CREATED) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"state": state, "message": message}, status=status)


@swagger_auto_schema(method="put", request_body=doc.ClientSerializer)
@api_view(["GET", "PUT", "DELETE"])
def client_rud(request, email):
    if request.method == "PUT":
        return update_client(request, email)
    elif request.method == "DELETE":
        return delete_client(request, email)
    elif request.method == "GET":
        return get_client(request, email)


def update_client(request, email):
    token, username, role = who_am_i(request)

    # default possibility
    state = "Error"
    message = "You do not have permissions to update this account"
    status = HTTP_403_FORBIDDEN

    if is_self(role, "client", username, email):
        state, message = queries.update_client(request, email)
        status = HTTP_200_OK if state else HTTP_400_BAD_REQUEST

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


def delete_client(request, email):
    token, username, role = who_am_i(request)

    try:
        user = User.objects.get(username=email)
    except User.DoesNotExist:
        state = "Error"
        message = "User does not exist!"
        status = HTTP_400_BAD_REQUEST
        return Response({"role": role, "state": state, "message": message, "token": token},
                        status=status)

    # default possibility
    state = "Error"
    message = "You don't have permissions to delete this account"
    status = HTTP_403_FORBIDDEN

    if is_self(role, "client", username, email):
        state, message = queries.delete_user(user)
        state, status = ("Success", HTTP_204_NO_CONTENT) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


def get_client(request, email):
    token, username, role = who_am_i(request)

    # default possibility
    state = "Error"
    message = "You don't have permissions to access this account info"
    status = HTTP_403_FORBIDDEN

    if is_self(role, "client", username, email):
        state, message = queries.get_client(username)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    elif verify_authorization(role, "doctor") and is_client_doctor(username, email):
        state, message = queries.get_client(email)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@swagger_auto_schema(method="post", request_body=doc.DoctorSerializer)
@api_view(["POST"])
def new_doctor(request):
    token, username, role = who_am_i(request)

    if not verify_authorization(role, "admin"):
        state = "Error"
        message = "You do not have permissions to add a new doctor"
        status = HTTP_403_FORBIDDEN
        return Response({"role": role, "state": state, "message": message, "token": token},
                        status=status)

    data = request.data
    if not (
            "email" in data
            and "first_name" in data
            and "last_name" in data
            and "password" in data
            and "birth_date" in data

    ):
        state = "Error"
        message = "Missing parameters"
        status = HTTP_400_BAD_REQUEST
        return Response({"role": role, "state": state, "message": message, "token": token}, status=status)

    admin_hospital = CustomAdmin.objects.get(auth_user__username=username).hospital
    state, message = queries.add_doctor(data, admin_hospital)
    state, status = ("Success", HTTP_201_CREATED) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@swagger_auto_schema(method="put", request_body=doc.DoctorSerializer)
@api_view(["GET", "PUT", "DELETE"])
def doctor_rud(request, email):
    if request.method == "PUT":
        return update_doctor(request, email)
    elif request.method == "DELETE":
        return delete_doctor(request, email)
    elif request.method == "GET":
        return get_doctor(request, email)


def update_doctor(request, email):
    token, username, role = who_am_i(request)

    # default possibility
    state = "Error"
    message = "You do not have permissions to update this account"
    status = HTTP_403_FORBIDDEN

    if is_self(role, "doctor", username, email):
        state, message = queries.update_doctor(request, email)
        status = HTTP_200_OK if state else HTTP_400_BAD_REQUEST

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


def delete_doctor(request, email):
    token, username, role = who_am_i(request)
    try:
        user = User.objects.get(username=email)
    except User.DoesNotExist:
        state = "Error"
        message = "User does not exist!"
        status = HTTP_400_BAD_REQUEST
        return Response({"role": role, "state": state, "message": message, "token": token}, status=status)

    state = "Error"
    message = "You do not have permissions to delete this account"
    status = HTTP_403_FORBIDDEN

    if is_self(role, "doctor", username, email):
        state, message = queries.delete_user(user)
        state, status = ("Success", HTTP_204_NO_CONTENT) if state else ("Error", HTTP_400_BAD_REQUEST)

    elif verify_authorization(role, "admin") and is_doctor_admin(email, username):
        state, message = queries.delete_user(user)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


def get_doctor(request, email):
    token, username, role = who_am_i(request)

    # default possibility
    state = "Error"
    message = "You don't have permissions to access this account info"
    status = HTTP_403_FORBIDDEN

    if is_self(role, "doctor", username, email):
        state, message = queries.get_doctor(username)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    elif verify_authorization(role, "client") and is_client_doctor(email, username):
        state, message = queries.get_doctor(email)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    elif verify_authorization(role, "admin") and is_doctor_admin(email, username):
        state, message = queries.get_doctor(email)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@swagger_auto_schema(method="post", request_body=doc.MealHistorySerializer)
@api_view(["POST"])
def new_food_log(request):
    token, username, role = who_am_i(request)

    if not verify_authorization(role, "client"):
        state = "Error"
        message = "You do not have permissions to add a new food log."
        status = HTTP_403_FORBIDDEN
        return Response({"role": role, "state": state, "message": message, "token": token},
                        status=status)

    data = request.data
    if not (
            "day" in data
            and "type_of_meal" in data
            and "meal" in data

    ):
        state = "Error"
        message = "Missing parameters"
        status = HTTP_400_BAD_REQUEST
        return Response({"role": role, "state": state, "message": message, "token": token}, status=status)

    state, message = queries.add_food_log(data, username)
    state, status = ("Success", HTTP_201_CREATED) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@swagger_auto_schema(method="put", request_body=doc.MealHistorySerializer)
@api_view(["GET", "PUT", "DELETE"])
def food_log_rud(request, food_log_filter):
    if request.method == "PUT":
        return update_food_log(request, food_log_filter)
    elif request.method == "DELETE":
        return delete_food_log(request, food_log_filter)
    elif request.method == "GET":
        return get_food_log(request, food_log_filter)


def update_food_log(request, food_log_id):
    token, username, role = who_am_i(request)

    try:
        meal_history = MealHistory.objects.filter(id=food_log_id)
        current_meal_history = MealHistory.objects.get(id=food_log_id)
    except MealHistory.DoesNotExist:
        state = "Error"
        message = "Food Log does not exist!"
        status = HTTP_400_BAD_REQUEST
        return Response({"role": role, "state": state, "message": message, "token": token},
                        status=status)

    # default possibility
    state = "Error"
    message = "You do not have permissions to update this food log"
    status = HTTP_403_FORBIDDEN

    if is_self(role, "client", username, current_meal_history.client.user.auth_user.username):
        state, message = queries.update_food_log(request, current_meal_history, meal_history)
        status = HTTP_200_OK if state else HTTP_400_BAD_REQUEST

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


def delete_food_log(request, food_log_id):
    token, username, role = who_am_i(request)

    try:
        meal_history = MealHistory.objects.get(id=food_log_id)
    except MealHistory.DoesNotExist:
        state = "Error"
        message = "Food Log does not exist!"
        status = HTTP_400_BAD_REQUEST
        return Response({"role": role, "state": state, "message": message, "token": token},
                        status=status)

    # default possibility
    state = "Error"
    message = "You don't have permissions to delete this food log"
    status = HTTP_403_FORBIDDEN

    if is_self(role, "client", username, meal_history.client.user.auth_user.username):
        state, message = queries.delete_food_log(meal_history)
        state, status = ("Success", HTTP_204_NO_CONTENT) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


def get_food_log(request, day):
    token, username, role = who_am_i(request)

    # default possibility
    state = "Error"
    message = "You don't have permissions to access this food log"
    status = HTTP_403_FORBIDDEN

    if verify_authorization(role, "client"):
        state, message = queries.get_food_log(username, day)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@swagger_auto_schema(method="post", request_body=doc.ClientEmailSerializer)
@api_view(["POST"])
def new_doctor_patient_association(request):
    token, username, role = who_am_i(request)

    if not verify_authorization(role, "doctor"):
        state = "Error"
        message = "You do not have permissions to add a new doctor patient association."
        status = HTTP_403_FORBIDDEN
        return Response({"role": role, "state": state, "message": message, "token": token},
                        status=status)

    data = request.data
    if not (
            "client" in data

    ):
        state = "Error"
        message = "Missing parameters"
        status = HTTP_400_BAD_REQUEST
        return Response({"role": role, "state": state, "message": message, "token": token}, status=status)

    state, message = queries.add_doctor_patient_association(data, username)
    state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@swagger_auto_schema(method="post", request_body=doc.IngredientSerializer)
@api_view(["POST"])
def new_ingredient(request):
    token, username, role = who_am_i(request)

    data = request.data

    if not ("calories" in data and "proteins" in data and "fat" in data and "carbs" in data and "name" in data):
        state = "Error"
        message = "Missing parameters"
        status = HTTP_400_BAD_REQUEST
        return Response({"role": role, "state": state, "message": message, "token": token}, status=status)

    state, message = queries.add_ingredient(data)
    state, status = ("Success", HTTP_201_CREATED) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@swagger_auto_schema(method="post", request_body=doc.MealSerializer)
@api_view(["POST"])
def new_meal(request):
    token, username, role = who_am_i(request)

    data = request.data
    if not ("name" in data and "category" in data and "ingredients" in data):
        state = "Error"
        message = "Missing parameters"
        status = HTTP_400_BAD_REQUEST
        return Response({"role": role, "state": state, "message": message, "token": token}, status=status)

    state, message = queries.add_new_meal(data, username, role)
    state, status = ("Success", HTTP_201_CREATED) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)

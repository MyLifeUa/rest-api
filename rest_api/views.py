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
)

from rest_api import queries, documentation_serializers as doc
from rest_api.authentication import token_expire_handler
from .serializers import *
from .utils import *


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


@api_view(["GET"])
@permission_classes((AllowAny,))
def check_email(request, email):
    status = HTTP_200_OK
    state = "Success"

    email_exists = User.objects.filter(username=email).exists()
    message = True if email_exists else False

    return Response({"state": state, "message": message}, status=status)


@api_view(["GET"])
def check_token(request):
    token, username, role = who_am_i(request)

    status = HTTP_200_OK
    state = "Success"
    message = "Token is active"

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@swagger_auto_schema(method="post", request_body=doc.AdminSerializer)
@api_view(["POST"])
def new_admin(request):
    token, username, role = who_am_i(request)

    if not verify_authorization(role, "django-admin"):
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

    if is_self(role, "admin", username, email) or verify_authorization(role, "django-admin"):
        state, message = queries.delete_user(user)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

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
            and "sex" in data
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
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

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


@api_view(["GET"])
def client_photo(request, email):
    token, username, role = who_am_i(request)

    # default possibility
    state = "Error"
    message = "You don't have permissions to access this account info"
    status = HTTP_403_FORBIDDEN

    if is_self(role, "client", username, email):
        state, message = queries.get_client_photo(username)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    elif verify_authorization(role, "doctor") and is_client_doctor(username, email):
        state, message = queries.get_client_photo(email)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "username": username, "state": state, "message": message, "token": token},
                    status=status)


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

    admin_hospital = HospitalAdmin.objects.get(auth_user__username=username).hospital
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
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

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


@swagger_auto_schema(methods=["post", "delete"], request_body=doc.ClientEmailSerializer)
@api_view(["GET", "POST", "DELETE"])
def doctor_patient_association_cd(request):
    if request.method == "POST":
        return new_doctor_patient_association(request)
    elif request.method == "GET":
        return get_client_doctor(request)
    elif request.method == "DELETE":
        return delete_doctor_patient_association(request)


def new_doctor_patient_association(request):
    token, username, role = who_am_i(request)

    if not verify_authorization(role, "doctor"):
        state = "Error"
        message = "You do not have permissions to add a new doctor patient association."
        status = HTTP_403_FORBIDDEN
        return Response({"role": role, "state": state, "message": message, "token": token},
                        status=status)

    data = request.data
    if not ("client" in data):
        state = "Error"
        message = "Missing parameters"
        status = HTTP_400_BAD_REQUEST
        return Response({"role": role, "state": state, "message": message, "token": token}, status=status)

    state, message = queries.add_doctor_patient_association(data, username)
    state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


def delete_doctor_patient_association(request):
    token, username, role = who_am_i(request)

    data = request.data
    if not ("client" in data):
        state = "Error"
        message = "Missing parameters"
        status = HTTP_400_BAD_REQUEST
        return Response({"role": role, "state": state, "message": message, "token": token}, status=status)

    email = data.get("client")

    try:
        user = Client.objects.get(user__auth_user__username=email)
    except User.DoesNotExist:
        state = "Error"
        message = "User does not exist!"
        status = HTTP_400_BAD_REQUEST
        return Response({"role": role, "state": state, "message": message, "token": token},
                        status=status)
    doctor_from_user = user.doctor

    if doctor_from_user is None:
        state = "Error"
        message = "The patient has no doctor associated"
        status = HTTP_400_BAD_REQUEST
        return Response({"role": role, "state": state, "message": message, "token": token},
                        status=status)

    # default possibility
    state = "Error"
    message = "You don't have permissions to delete this doctor patient association"
    status = HTTP_403_FORBIDDEN

    if is_self(role, "client", username, email):
        state, message = queries.delete_doctor_patient_association(email)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    elif is_self(role, "doctor", username, doctor_from_user.user.auth_user.username):
        state, message = queries.delete_doctor_patient_association(email)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


def get_client_doctor(request):
    token, username, role = who_am_i(request)

    state = "Error"
    message = "You don't have permissions to access this information."
    status = HTTP_403_FORBIDDEN

    if verify_authorization(role, "client"):
        state, message = queries.get_client_doctor(username)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@api_view(["GET"])
def doctor_get_all_patients(request):
    token, username, role = who_am_i(request)

    # default possibility
    state = "Error"
    message = "You do not have permissions to update this account"
    status = HTTP_403_FORBIDDEN

    if verify_authorization(role, "doctor"):
        state, message = queries.doctor_get_all_patients(username)
        status = HTTP_200_OK if state else HTTP_400_BAD_REQUEST

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@swagger_auto_schema(method="post", request_body=doc.MealHistorySerializer)
@api_view(["POST"])
def new_food_log(request):
    token, username, role = who_am_i(request)

    if not verify_authorization(role, "client"):
        state = "Error"
        message = "You do not have permissions to add a new food log."
        status = HTTP_403_FORBIDDEN
        return Response({"role": role, "state": state, "message": message, "token": token}, status=status)

    data = request.data
    if not (
            "day" in data
            and "type_of_meal" in data
            and "meal" in data
            and "number_of_servings" in data

    ):
        state = "Error"
        message = "Missing parameters"
        status = HTTP_400_BAD_REQUEST
        return Response({"role": role, "state": state, "message": message, "token": token}, status=status)

    state, message, alerts = queries.add_food_log(data, username)
    state, status = ("Success", HTTP_201_CREATED) if state else ("Error", HTTP_400_BAD_REQUEST)

    final_response = {"role": role, "state": state, "message": message, "token": token}
    if state and (alerts is not None or not alerts):
        final_response["alerts"] = alerts

    return Response(final_response, status=status)


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
        state, message = queries.update_food_log(request, meal_history)
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
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


def get_food_log(request, day):
    token, username, role = who_am_i(request)

    # default possibility
    state = "Error"
    message = "You don't have permissions to access this food log"
    status = HTTP_403_FORBIDDEN

    if verify_authorization(role, "client"):
        message = "Invalid date: It should be in the format YYYY-mm-dd"
        status = HTTP_400_BAD_REQUEST

        if is_valid_date(day, "%Y-%m-%d"):
            state, message = queries.get_food_log(username, day)
            state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@swagger_auto_schema(method="post", request_body=doc.IngredientSerializer)
@api_view(["POST", "GET"])
def ingredients(request):
    if request.method == "POST":
        return new_ingredient(request)
    elif request.method == "GET":
        return get_ingredients(request)


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


def get_ingredients(request):
    token, username, role = who_am_i(request)

    state = "Error"
    message = "You don't have permissions to access the list of ingredients."
    status = HTTP_403_FORBIDDEN

    if verify_authorization(role, "client"):
        state, message = queries.get_ingredients()
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@swagger_auto_schema(method="put", request_body=doc.IngredientSerializer)
@api_view(["GET", "PUT", "DELETE"])
def ingredient_rud(request, ingredient_id):
    if request.method == "PUT":
        return update_ingredient(request, ingredient_id)
    elif request.method == "DELETE":
        return delete_ingredient(request, ingredient_id)
    elif request.method == "GET":
        return get_ingredient(request, ingredient_id)


def update_ingredient(request, ingredient_id):
    token, username, role = who_am_i(request)

    data = request.data

    state, message = queries.update_ingredient(data, ingredient_id)
    status = HTTP_200_OK if state else HTTP_400_BAD_REQUEST

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


def delete_ingredient(request, ingredient_id):
    token, username, role = who_am_i(request)

    state, message = queries.delete_ingredient(ingredient_id)
    status = HTTP_200_OK if state else HTTP_400_BAD_REQUEST

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


def get_ingredient(request, ingredient_id):
    token, username, role = who_am_i(request)

    state, message = queries.get_ingredient(ingredient_id)
    status = HTTP_200_OK if state else HTTP_400_BAD_REQUEST

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@swagger_auto_schema(method="post", request_body=doc.MealSerializer)
@api_view(["GET", "POST"])
def meals(request):
    if request.method == "POST":
        return new_meal(request)
    elif request.method == "GET":
        return get_meals(request)


def new_meal(request):
    token, username, role = who_am_i(request)

    data = request.data
    if not ("name" in data and "category" in data and "ingredients" in data):
        state = "Error"
        message = "Missing parameters"
        status = HTTP_400_BAD_REQUEST
        return Response({"role": role, "state": state, "message": message, "token": token}, status=status)

    state, message = queries.add_new_meal(data, username, role)
    state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


def get_meals(request):
    token, username, role = who_am_i(request)

    state = "Error"
    message = "You don't have permissions to access the list of meals."
    status = HTTP_403_FORBIDDEN

    if verify_authorization(role, "client"):
        state, message = queries.get_meals(username)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@api_view(["GET"])
def list_hospital_doctors(request):
    token, username, role = who_am_i(request)

    # default possibility
    state = "Error"
    message = "You don't have permissions to access the list of doctors."
    status = HTTP_403_FORBIDDEN

    if verify_authorization(role, "admin"):
        state, message = queries.get_hospital_doctors(username)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@swagger_auto_schema(methods=["post"], request_body=doc.ClientFitbitToken)
@api_view(["POST"])
def add_fitbit_token(request):
    token, username, role = who_am_i(request)

    if not verify_authorization(role, "client"):
        state = "Error"
        message = "You do not have permissions to add a new fitbit token."
        status = HTTP_403_FORBIDDEN
        return Response({"role": role, "state": state, "message": message, "token": token},
                        status=status)

    data = request.data
    if not ("access_token" in data and "refresh_token" in data):
        state = "Error"
        message = "Missing parameters"
        status = HTTP_400_BAD_REQUEST
        return Response({"role": role, "state": state, "message": message, "token": token}, status=status)

    state, message = queries.add_fitbit_token(data, username)
    state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@api_view(["POST"])
def classify_image(request):
    token, username, role = who_am_i(request)

    # default possibility
    state = "Error"
    message = "You don't have permissions to access this information."
    status = HTTP_403_FORBIDDEN

    data = request.data

    if verify_authorization(role, "client"):
        image_b64 = data["image_b64"] if "image_b64" in data else ""

        state, message = queries.classify_image(image_b64)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@api_view(["GET"])
def classify_barcode(request):
    token, username, role = who_am_i(request)

    # default possibility
    state = "Error"
    message = "You don't have permissions to access this information."
    status = HTTP_403_FORBIDDEN

    if verify_authorization(role, "client"):
        barcode = request.GET.get("barcode", "")

        state, message = queries.classify_barcode(username, barcode)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@api_view(["GET"])
def nutrients_ratio(request, email, date):
    token, username, role = who_am_i(request)

    message = "Invalid date: It should be in the format yyyy-mm-dd"
    status = HTTP_400_BAD_REQUEST

    if is_valid_date(date, "%Y-%m-%d"):

        # default possibility
        state = "Error"
        message = "You don't have permissions to access this information."
        status = HTTP_403_FORBIDDEN

        if is_self(role, "client", username, email):
            state, message = queries.get_nutrients_ratio(username, date)
            state, status = ("Success", HTTP_200_OK)

        elif verify_authorization(role, "doctor") and is_client_doctor(username, email):
            state, message = queries.get_nutrients_ratio(email, date)
            state, status = ("Success", HTTP_200_OK)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@api_view(["GET"])
def nutrients_total(request, email, date):
    token, username, role = who_am_i(request)

    message = "Invalid date: It should be in the format yyyy-mm-dd"
    status = HTTP_400_BAD_REQUEST

    if is_valid_date(date, "%Y-%m-%d"):

        # default possibility
        state = "Error"
        message = "You don't have permissions to access this information."
        status = HTTP_403_FORBIDDEN

        if is_self(role, "client", username, email):
            state, message = queries.get_nutrients_total(username, date)
            state, status = ("Success", HTTP_200_OK)

        elif verify_authorization(role, "doctor") and is_client_doctor(username, email):
            state, message = queries.get_nutrients_total(email, date)
            state, status = ("Success", HTTP_200_OK)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@api_view(["GET"])
def nutrients_history(request, email):
    token, username, role = who_am_i(request)

    # default possibility
    state = "Error"
    message = "You don't have permissions to access this information."
    status = HTTP_403_FORBIDDEN

    metric = request.GET.get("metric", "calories")
    period = request.GET.get("period", "week")

    params = {"metric": metric, "period": period}

    if is_self(role, "client", username, email):
        state, message = queries.get_nutrients_history(username, params)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    elif verify_authorization(role, "doctor") and is_client_doctor(username, email):
        state, message = queries.get_nutrients_history(email, params)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@api_view(["GET"])
def body_history(request, email):
    token, username, role = who_am_i(request)

    # default possibility
    state = "Error"
    message = "You don't have permissions to access this information."
    status = HTTP_403_FORBIDDEN

    metric = request.GET.get("metric", "steps")
    period = request.GET.get("period", "week")

    params = {"metric": metric, "period": period}

    if is_self(role, "client", username, email):
        state, message = queries.get_body_history(username, params)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    elif verify_authorization(role, "doctor") and is_client_doctor(username, email):
        state, message = queries.get_body_history(email, params)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@api_view(["GET"])
def body_avg_heart_rate(request, email):
    token, username, role = who_am_i(request)

    # default possibility
    state = "Error"
    message = "You don't have permissions to access this information."
    status = HTTP_403_FORBIDDEN

    if is_self(role, "client", username, email):
        state, message = queries.get_body_avg_heart_rate(username)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    elif verify_authorization(role, "doctor") and is_client_doctor(username, email):
        state, message = queries.get_body_avg_heart_rate(email)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@api_view(["GET"])
def my_life_stat(request, email):
    token, username, role = who_am_i(request)

    # default possibility
    state = "Error"
    message = "You don't have permissions to access this information."
    status = HTTP_403_FORBIDDEN

    if is_self(role, "client", username, email):
        state, message = queries.get_my_life_stat(username)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    elif verify_authorization(role, "doctor") and is_client_doctor(username, email):
        state, message = queries.get_my_life_stat(email)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@swagger_auto_schema(methods=["post", "delete"], request_body=doc.ExpoTokenSerializer)
@api_view(["GET", "POST", "DELETE"])
def expo_tokens_post_and_get(request):
    if request.method == "POST":
        return new_expo_token(request)
    elif request.method == "GET":
        return get_client_expo_tokens(request)
    elif request.method == "DELETE":
        return delete_client_expo_tokens(request)


def new_expo_token(request):
    token, username, role = who_am_i(request)

    state = "Error"
    message = "You don't have permissions to access the list of meals."
    status = HTTP_403_FORBIDDEN

    if verify_authorization(role, "client"):

        data = request.data
        if "expo_token" not in data:
            state = "Error"
            message = "Missing parameter: 'expo_token'"
            status = HTTP_400_BAD_REQUEST
            return Response({"role": role, "state": state, "message": message, "token": token}, status=status)

        state, message = queries.new_expo_token(data, username)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


def get_client_expo_tokens(request):
    token, username, role = who_am_i(request)

    state = "Error"
    message = "You don't have permissions to access the list of meals."
    status = HTTP_403_FORBIDDEN

    if verify_authorization(role, "client"):
        state, message = queries.get_client_expo_tokens(username)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


def delete_client_expo_tokens(request):
    token, username, role = who_am_i(request)

    state = "Error"
    message = "You don't have permissions to access the list of meals."
    status = HTTP_403_FORBIDDEN

    if verify_authorization(role, "client"):
        data = request.data
        state, message = queries.delete_client_expo_tokens(data, username)
        state, status = ("Success", HTTP_200_OK) if state else ("Error", HTTP_400_BAD_REQUEST)

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)


@api_view(["GET"])
def reload_db(request):
    token, username, role = who_am_i(request)

    # default possibility
    state = "Error"
    message = "You don't have permissions to perform this action."
    status = HTTP_403_FORBIDDEN

    if verify_authorization(role, "django-admin"):
        state_ = queries.reload_database()

        state = "Success" if state_ else "Error"
        status = HTTP_200_OK if state_ else HTTP_400_BAD_REQUEST
        message = "DB reloaded with success!" if state_ else "Error while reloading DB!"

    return Response({"role": role, "state": state, "message": message, "token": token}, status=status)

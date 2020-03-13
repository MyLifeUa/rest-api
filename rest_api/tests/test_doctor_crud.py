from django.contrib.auth.models import User, Group
from datetime import date

from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN)
from rest_framework.test import APITestCase
from ..models import CustomAdmin, Client, CustomUser, Doctor


class DoctorRegistrationTest(APITestCase):

    def login(self, username, password):
        return self.client.post("/login", {"username": username, "password": password})

    def create_user_and_login(self, role, username, email, password):
        if role == "client":
            user = User.objects.create_user(username, email, password)
            clients_group = Group.objects.get_or_create(name="clients_group")[0]
            clients_group.user_set.add(user)
        elif role == "admin":
            User.objects.create_superuser(username, email, password)
        elif role == "custom_admin":
            auth_user = User.objects.create_superuser(username, email, password)
            CustomAdmin.objects.create(auth_user=auth_user, hospital="Hospital de São João")

        response = self.login("vasco", "pwd")
        token = response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

    def test_new_doctor_missing_authentication(self):
        response = self.client.post("/doctors",
                                    {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco",
                                     "last_name": "Ramos"})
        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)

    def test_new_admin_missing_authorization(self):
        self.create_user_and_login("client", "vasco", "vr@ua.pt", "pwd")
        response = self.client.post("/doctors",
                                    {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco",
                                     "last_name": "Ramos"})
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_new_doctor_missing_parameters(self):
        self.create_user_and_login("custom_admin", "vasco", "vr@ua.pt", "pwd")
        response = self.client.post("/doctors", {"email": "vr@ua.pt"})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        response = self.client.post("/doctors", {"email": "vr@ua.pt", "password": "pwd"})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        response = self.client.post("/doctors",
                                    {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco"})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_new_doctor_right_parameters(self):
        self.create_user_and_login("custom_admin", "vasco", "vr@ua.pt", "pwd")
        response = self.client.post("/doctors",
                                    {"email": "j.vasconcelos99@ua.pt", "password": "pwd", "first_name": "Vasco",
                                     "last_name": "Ramos", "birth_date": "2020-03-04"})
        self.assertEqual(response.status_code, HTTP_200_OK)


class DoctorUpdateTest(APITestCase):

    def login(self, username, password):
        return self.client.post("/login", {"username": username, "password": password})

    def create_user_and_login(self, role, username, email, password):
        if role == "client":
            user = User.objects.create_user(username, email, password)
            clients_group = Group.objects.get_or_create(name="clients_group")[0]
            clients_group.user_set.add(user)
        elif role == "admin":
            User.objects.create_superuser(username, email, password)
        elif role == "custom_admin":
            auth_user = User.objects.create_superuser(username, email, password)
            CustomAdmin.objects.create(auth_user=auth_user, hospital="Hospital de São João")

        response = self.login("vasco", "pwd")
        token = response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

    def setUp(self):
        self.create_user_and_login("custom_admin", "vasco", "vr@ua.pt", "pwd")

        self.client.post("/doctors",
                         {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco", "last_name": "Ramos",
                          "birth_date": "2020-03-04"})
        response = self.client.post("/login", {"username": "vr@ua.pt", "password": "pwd"})
        token = response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

    def test_update_nothing(self):
        response = self.client.put("/doctors/vr@ua.pt", {})
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_update_wrong_parameters(self):
        response = self.client.put("/doctors/vr@ua.pt", {"aaaa": "aaa"})
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_update_wrong_parameters_type(self):
        response = self.client.put("/doctors/vr@ua.pt", {"birth_date": 2})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_correct_update(self):
        response = self.client.put("/doctors/vr@ua.pt", {"last_name": "joao"})
        self.assertEqual(response.status_code, HTTP_200_OK)


class DoctorDeleteTest(APITestCase):

    def login(self, username, password):
        return self.client.post("/login", {"username": username, "password": password})

    def create_user_and_login(self, role, username, email, password):
        if role == "client":
            user = User.objects.create_user(username, email, password)
            clients_group = Group.objects.get_or_create(name="clients_group")[0]
            clients_group.user_set.add(user)
        elif role == "admin":
            User.objects.create_superuser(username, email, password)
        elif role == "custom_admin":
            auth_user = User.objects.create_superuser(username, email, password)
            CustomAdmin.objects.create(auth_user=auth_user, hospital="Hospital de São João")

        response = self.login("vasco", "pwd")
        token = response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

    def setUp(self):
        self.create_user_and_login("custom_admin", "vasco", "vr@ua.pt", "pwd")

        self.client.post("/doctors",
                         {"email": "v@ua.pt", "password": "pwd", "first_name": "Vasco", "last_name": "Ramos",
                          "birth_date": "2020-03-04"})
        response = self.client.post("/login", {"username": "v@ua.pt", "password": "pwd"})
        token = response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

    def test_delete_non_existent_user(self):
        response = self.client.delete("/doctors/vr99@ua.pt")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_delete_non_doctor_account(self):
        User.objects.create_superuser("admin", "admin@ua.pt", "pwd")
        response = self.client.delete("/doctors/admin")
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_delete_other_doctor_account(self):
        self.create_user_and_login("custom_admin", "vasco99", "vr@ua.pt", "pwd")
        self.client.post("/doctors", {"email": "ze@ua.pt", "password": "pwd", "first_name": "Ze",
                                      "last_name": "Costa", "birth_date": "2020-03-04"})
        response = self.client.post("/login", {"username": "v@ua.pt", "password": "pwd"})
        token = response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        response = self.client.delete("/doctors/ze@ua.pt")
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_admin_delete_doctor_account(self):
        self.create_user_and_login("custom_admin", "vasco99", "vr@ua.pt", "pwd")
        self.client.post("/doctors", {"email": "ze@ua.pt", "password": "pwd", "first_name": "Ze",
                                      "last_name": "Costa", "birth_date": "2020-03-04"})

        response = self.client.delete("/doctors/ze@ua.pt")
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_delete_self(self):
        response = self.client.delete("/doctors/v@ua.pt")
        self.assertEqual(response.status_code, HTTP_200_OK)


class GetDoctorTest(APITestCase):
    def setUp(self):
        self.client.post("/clients",
                         {"email": "tos@ua.pt", "password": "pwd", "first_name": "Tomas",
                          "last_name": "Ramos", "height": 1.60, "weight_goal": 65,"birth_date":"2020-03-04"})  # Client without a doctor

        auth_user = User.objects.create_user("ana@ua.pt", "ana@ua.pt", "pwd")
        user = CustomUser.objects.create(auth_user=auth_user, birth_date=date(2020, 12, 31))
        self.doctor = Doctor.objects.create(user=user, hospital="Hospital")
        doctors_group = Group.objects.get_or_create(name="doctors_group")[0]
        doctors_group.user_set.add(auth_user)  # Doctor

        self.client.post("/clients",
                         {"email": "ana99@ua.pt", "password": "pwd", "first_name": "Tomas",
                          "last_name": "Ramos", "height": 1.60, "weight_goal": 65,"birth_date":"2020-03-04"})  # Client with doctor

    def login(self, username, pwd):
        response = self.client.post("/login", {"username": username, "password": pwd})
        token = response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

    def test_get_doctor_info_other_client(self):
        self.login("tos@ua.pt", "pwd")
        response = self.client.get("/doctors/ana@ua.pt")
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)



    def test_get_doctor_self_info(self):
        self.login("ana@ua.pt", "pwd")
        response = self.client.get("/doctors/ana@ua.pt")
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_get_doctor_info_client_doctor(self):
        Client.objects.filter(user__auth_user__username="ana99@ua.pt").update(doctor=self.doctor)
        self.login("ana99@ua.pt", "pwd")
        response = self.client.get("/doctors/ana@ua.pt")
        self.assertEqual(response.status_code, HTTP_200_OK)

from django.contrib.auth.models import User
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN
)
from rest_framework.test import APITestCase

from .utils import login, create_user_and_login
from ..models import Client, Doctor


class DoctorRegistrationTest(APITestCase):
    def test_new_doctor_missing_authentication(self):
        response = self.client.post("/doctors", {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco",
                                                 "last_name": "Ramos"})
        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)

    def test_new_doctor_missing_authorization(self):
        create_user_and_login(self.client, "client", "vasco", "vr@ua.pt", "pwd")
        response = self.client.post("/doctors",
                                    {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco",
                                     "last_name": "Ramos"})
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_new_doctor_missing_parameters(self):
        create_user_and_login(self.client, "custom_admin", "vasco", "vr@ua.pt", "pwd")
        response = self.client.post("/doctors", {"email": "vr@ua.pt"})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        response = self.client.post("/doctors", {"email": "vr@ua.pt", "password": "pwd"})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        response = self.client.post("/doctors",
                                    {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco"})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_new_doctor_right_parameters(self):
        create_user_and_login(self.client, "custom_admin", "vasco", "vr@ua.pt", "pwd")
        response = self.client.post("/doctors",
                                    {"email": "j.vasconcelos99@ua.pt", "password": "pwd", "first_name": "Vasco",
                                     "last_name": "Ramos", "birth_date": "2020-03-04"})
        self.assertEqual(response.status_code, HTTP_201_CREATED)


class DoctorUpdateTest(APITestCase):
    def setUp(self):
        create_user_and_login(self.client, "custom_admin", "vasco", "vr@ua.pt", "pwd")

        response = self.client.post("/doctors", {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco",
                                                 "last_name": "Ramos", "birth_date": "2020-03-04"})
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        login(self.client, "vr@ua.pt", "pwd")

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
    def setUp(self):
        create_user_and_login(self.client, "custom_admin", "vasco", "vr@ua.pt", "pwd")

        response = self.client.post("/doctors",
                                    {"email": "v@ua.pt", "password": "pwd", "first_name": "Vasco", "last_name": "Ramos",
                                     "birth_date": "2020-03-04"})
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        login(self.client, "v@ua.pt", "pwd")

    def test_delete_non_existent_user(self):
        response = self.client.delete("/doctors/vr99@ua.pt")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_delete_non_doctor_account(self):
        User.objects.create_superuser("admin", "admin@ua.pt", "pwd")
        response = self.client.delete("/doctors/admin")
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_delete_other_doctor_account(self):
        create_user_and_login(self.client, "custom_admin", "vasco99", "vr@ua.pt", "pwd")
        response = self.client.post("/doctors",
                                    {"email": "ze@ua.pt", "password": "pwd", "first_name": "Ze", "last_name": "Costa",
                                     "birth_date": "2020-03-04"})
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        login(self.client, "v@ua.pt", "pwd")

        response = self.client.delete("/doctors/ze@ua.pt")
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_client_delete_doctor_account(self):
        response = self.client.post("/clients", {"email": "joana@ua.pt", "password": "pwd", "first_name": "Vasco",
                                                 "last_name": "Ramos", "height": 1.60, "weight_goal": 65,
                                                 "current_weight": 90, "sex": "Male",
                                                 "birth_date": "2020-03-04"})
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        login(self.client, "joana@ua.pt", "pwd")

        response = self.client.delete("/doctors/v@ua.pt")
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_admin_delete_doctor_account(self):
        response = self.client.delete("/doctors/v@ua.pt")
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_delete_self(self):
        response = self.client.delete("/doctors/v@ua.pt")
        self.assertEqual(response.status_code, HTTP_200_OK)


class GetDoctorTest(APITestCase):
    def setUp(self):
        # Client without a doctor
        response = self.client.post("/clients", {"email": "tos@ua.pt", "password": "pwd", "first_name": "Tomas",
                                                 "last_name": "Ramos", "height": 1.60, "weight_goal": 65,
                                                 "current_weight": 90, "sex": "Male",
                                                 "birth_date": "2020-03-04"})
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        create_user_and_login(self.client, "custom_admin", "vasco", "vr@ua.pt", "pwd")

        response = self.client.post("/doctors", {"email": "ana@ua.pt", "password": "pwd", "first_name": "Vasco",
                                                 "last_name": "Ramos", "birth_date": "2020-03-04"})
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.doctor = Doctor.objects.get(user__auth_user__username="ana@ua.pt")

        # Client with doctor
        self.client.post("/clients",
                         {"email": "ana99@ua.pt", "password": "pwd", "first_name": "Tomas", "last_name": "Ramos",
                          "sex": "Male",
                          "height": 1.60, "weight_goal": 65, "current_weight": 90, "birth_date": "2020-03-04"})
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        Client.objects.filter(user__auth_user__username="ana99@ua.pt").update(doctor=self.doctor)

    def test_get_doctor_info_other_client(self):
        login(self.client, "tos@ua.pt", "pwd")
        response = self.client.get("/doctors/ana@ua.pt")
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_get_doctor_self_info(self):
        login(self.client, "ana@ua.pt", "pwd")
        response = self.client.get("/doctors/ana@ua.pt")
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_get_doctor_info_client_doctor(self):
        login(self.client, "ana99@ua.pt", "pwd")
        response = self.client.get("/doctors/ana@ua.pt")
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_get_doctor_info_admin(self):
        response = self.client.get("/doctors/ana@ua.pt")
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_get_doctor_info_other_hospital_admin(self):
        create_user_and_login(self.client, "custom_admin", "ant@ua.pt", "ant@ua.pt", "pwd", "Other Hospital")
        response = self.client.get("/doctors/ana@ua.pt")
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

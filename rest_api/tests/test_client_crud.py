from datetime import date

from django.contrib.auth.models import User, Group
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN
)
from rest_framework.test import APITestCase

from rest_api.models import CustomUser, Doctor, Client
from rest_api.tests.utils import login


class ClientRegistrationTest(APITestCase):
    def test_new_client_missing_parameters(self):
        response = self.client.post("/clients", {"email": "vr@ua.pt"})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        response = self.client.post("/clients", {"email": "vr@ua.pt", "password": "pwd"})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        response = self.client.post("/clients",
                                    {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco"})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        response = self.client.post("/clients",
                                    {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco",
                                     "last_name": "Ramos"})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        response = self.client.post("/clients",
                                    {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco",
                                     "last_name": "Ramos", "height": 111})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_new_client_right_parameters(self):
        response = self.client.post("/clients",
                                    {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco",
                                     "last_name": "Ramos", "height": 1.60, "weight_goal": 65, "current_weight": 90,
                                     "sex": "Male",
                                     "birth_date": "2020-03-04"})
        self.assertEqual(response.status_code, HTTP_201_CREATED)


class ClientUpdateTest(APITestCase):
    def setUp(self):
        response = self.client.post("/clients", {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco",
                                                 "last_name": "Ramos", "height": 1.60, "weight_goal": 65, "sex": "Male",
                                                 "current_weight": 90,
                                                 "birth_date": "2020-03-04"})
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        login(self.client, "vr@ua.pt", "pwd")

    def test_update_nothing(self):
        response = self.client.put("/clients/vr@ua.pt", {})
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_update_wrong_parameters(self):
        response = self.client.put("/clients/vr@ua.pt", {"aaaa": "aaa"})
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_update_wrong_parameters_type(self):
        response = self.client.put("/clients/vr@ua.pt", {"height": "aaa"})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_correct_update(self):
        response = self.client.put("/clients/vr@ua.pt", {"height": 2})
        self.assertEqual(response.status_code, HTTP_200_OK)


class ClientDeleteTest(APITestCase):
    def setUp(self):
        response = self.client.post("/clients",
                                    {"email": "v@ua.pt", "password": "pwd", "first_name": "Vasco", "last_name": "Ramos",
                                     "height": 1.60, "weight_goal": 65, "current_weight": 90, "sex": "Male",
                                     "birth_date": "2020-03-04"})
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        login(self.client, "v@ua.pt", "pwd")

    def test_delete_non_existent_user(self):
        response = self.client.delete("/clients/vr@ua.pt")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_delete_non_client_account(self):
        User.objects.create_superuser("admin", "admin@ua.pt", "pwd")
        response = self.client.delete("/clients/admin")
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_delete_other_client_account(self):
        response = self.client.post("/clients", {"email": "ze@ua.pt", "password": "pwd", "first_name": "Ze",
                                                 "last_name": "Costa", "height": 1.60, "weight_goal": 65,
                                                 "current_weight": 90, "sex": "Male",
                                                 "birth_date": "2020-03-04"})
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        response = self.client.delete("/clients/ze@ua.pt")
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_delete_self(self):
        response = self.client.delete("/clients/v@ua.pt")
        self.assertEqual(response.status_code, HTTP_200_OK)


class GetClientTest(APITestCase):
    def setUp(self):
        response = self.client.post("/clients", {"email": "tos@ua.pt", "password": "pwd", "first_name": "Tomas",
                                                 "last_name": "Ramos", "height": 1.60, "weight_goal": 65,
                                                 "current_weight": 90, "sex": "Male",
                                                 "birth_date": "2020-03-04"})
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        # create doctor
        auth_user = User.objects.create_user("ana@ua.pt", "ana@ua.pt", "pwd")
        user = CustomUser.objects.create(auth_user=auth_user, birth_date=date(2020, 12, 31))
        self.doctor = Doctor.objects.create(user=user, hospital="Hospital")
        doctors_group = Group.objects.get_or_create(name="doctors_group")[0]
        doctors_group.user_set.add(auth_user)

    def test_get_client_info_other_client(self):
        response = self.client.post("/clients", {"email": "vr@ua.pt", "password": "pwd", "first_name": "Tomas",
                                                 "last_name": "Ramos", "height": 1.60, "weight_goal": 65,
                                                 "current_weight": 90, "sex": "Male",
                                                 "birth_date": "2020-03-04"})
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        login(self.client, "vr@ua.pt", "pwd")
        response = self.client.get("/clients/tos@ua.pt")
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_get_client_info_client_no_doctor(self):
        login(self.client, "ana@ua.pt", "pwd")
        response = self.client.get("/clients/tos@ua.pt")
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_get_client_self_info(self):
        login(self.client, "tos@ua.pt", "pwd")
        response = self.client.get("/clients/tos@ua.pt")
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_get_client_info_client_doctor(self):
        Client.objects.filter(user__auth_user__username="tos@ua.pt").update(doctor=self.doctor)
        login(self.client, "ana@ua.pt", "pwd")
        response = self.client.get("/clients/tos@ua.pt")
        self.assertEqual(response.status_code, HTTP_200_OK)

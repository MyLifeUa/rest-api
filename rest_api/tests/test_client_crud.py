from django.contrib.auth.models import User
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN)
from rest_framework.test import APITestCase


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
                                     "last_name": "Ramos", "height": 1.60, "weight_goal": 65,"birth_date":"2020-03-04"})
        self.assertEqual(response.status_code, HTTP_200_OK)


class ClientUpdateTest(APITestCase):
    def setUp(self):
        self.client.post("/clients", {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco",
                                      "last_name": "Ramos", "height": 1.60, "weight_goal": 65,"birth_date":"2020-03-04"})
        response = self.client.post("/login", {"username": "vr@ua.pt", "password": "pwd"})
        token = response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

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
        self.client.post("/clients", {"email": "v@ua.pt", "password": "pwd", "first_name": "Vasco",
                                      "last_name": "Ramos", "height": 1.60, "weight_goal": 65,"birth_date":"2020-03-04"})
        response = self.client.post("/login", {"username": "v@ua.pt", "password": "pwd"})
        token = response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

    def test_delete_non_existent_user(self):
        response = self.client.delete("/clients/vr@ua.pt")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_delete_non_client_account(self):
        User.objects.create_superuser("admin", "admin@ua.pt", "pwd")
        response = self.client.delete("/clients/admin")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_delete_other_client_account(self):
        self.client.post("/clients", {"email": "ze@ua.pt", "password": "pwd", "first_name": "Ze",
                                      "last_name": "Costa", "height": 1.60, "weight_goal": 65,"birth_date":"2020-03-04"})
        response = self.client.delete("/clients/ze@ua.pt")
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_delete_self(self):
        response = self.client.delete("/clients/v@ua.pt")
        self.assertEqual(response.status_code, HTTP_200_OK)
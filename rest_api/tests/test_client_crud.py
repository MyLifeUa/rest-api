from django.contrib.auth.models import User, Group
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.test import APITestCase


class ClientRegistrationTest(APITestCase):
    def setUp(self):
        user = User.objects.create_user("vasco", "vr@ua.pt", "pwd")
        clients_group = Group.objects.get_or_create(name="clients_group")[0]
        clients_group.user_set.add(user)

    def login(self):
        return self.client.post("/login", {"username": "vasco", "password": "pwd"})

    def logout(self, token=None):
        if token is not None:
            self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        return self.client.get("/logout")

    def test_new_client_missing_parameters(self):
        response = self.client.post("/clients", {"email": "vr@ua.pt"})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        response = self.client.post(
            "/clients", {"email": "vr@ua.pt", "password": "pwd"}
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        response = self.client.post(
            "/clients", {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco"}
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        response = self.client.post(
            "/clients",
            {
                "email": "vr@ua.pt",
                "password": "pwd",
                "first_name": "Vasco",
                "last_name": "Ramos",
            },
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        response = self.client.post(
            "/clients",
            {
                "email": "vr@ua.pt",
                "password": "pwd",
                "first_name": "Vasco",
                "last_name": "Ramos",
                "height": 111,
            },
        )
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_new_client_right_parameters(self):
        response = self.client.post(
            "/clients",
            {
                "email": "vr@ua.pt",
                "password": "pwd",
                "first_name": "Vasco",
                "last_name": "Ramos",
                "height": 1.60,
                "weight_goal": 65,
            },
        )
        self.assertEqual(response.status_code, HTTP_200_OK)

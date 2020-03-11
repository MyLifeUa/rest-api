from django.contrib.auth.models import User, Group
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
from rest_framework.test import APITestCase


class AdminRegistrationTest(APITestCase):
    def login(self):
        return self.client.post("/login", {"username": "vasco", "password": "pwd"})

    def test_new_admin_missing_authentication(self):
        response = self.client.post("/admins", {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco",
                                                "last_name": "Ramos", "hospital": "Centro Hospitalar de São João"})
        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)

    def test_new_admin_missing_authorization(self):
        user = User.objects.create_user("vasco", "vr@ua.pt", "pwd")
        clients_group = Group.objects.get_or_create(name="clients_group")[0]
        clients_group.user_set.add(user)
        response = self.login()
        token = response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.post("/admins", {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco",
                                                "last_name": "Ramos", "hospital": "Centro Hospitalar de São João"})
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_new_admin_missing_parameters(self):
        User.objects.create_superuser("vasco", "vr@ua.pt", "pwd")
        response = self.login()
        token = response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.post("/admins", {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco",
                                                "last_name": "Ramos"})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_new_admin_right_parameters(self):
        User.objects.create_superuser("vasco", "vr@ua.pt", "pwd")
        response = self.login()
        token = response.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        response = self.client.post("/admins", {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco",
                                                "last_name": "Ramos", "hospital": "Centro Hospitalar de São João"})
        self.assertEqual(response.status_code, HTTP_200_OK)

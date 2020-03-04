from django.contrib.auth.models import User, Group
from rest_framework.status import *
from rest_framework.test import APITestCase


# Create your tests here.
class AuthenticationTest(APITestCase):
    def setUp(self):
        user = User.objects.create_user("vasco", "vr@ua.pt", "pwd")
        clients_group = Group.objects.get_or_create(name="clients_group")[0]
        clients_group.user_set.add(user)

    def tearDown(self):
        # Clean up run after every test method.
        pass

    def test_request_with_no_auth_when_it_needs_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token 1234wrtyre")
        response = self.client.get("/logout")
        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)

    def test_request_with_no_auth_when_it_does_not_need_auth(self):
        response = self.client.post("/login", {"username": "vasco", "password": "pwd"})
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_auth_with_stole_old_token(self):
        # first login
        response = self.client.post("/login", {"username": "vasco", "password": "pwd"})
        token = response.data["token"]

        # first logout
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        self.client.get("/logout")
        self.assertEqual(response.status_code, HTTP_200_OK)

        # second login
        response = self.client.post("/login", {"username": "vasco", "password": "pwd"})

        # second logout
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        self.client.get("/logout")
        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)

from django.contrib.auth.models import User, Group
from rest_framework.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_200_OK,
)
from rest_framework.test import APITestCase


class AuthenticationTest(APITestCase):
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

    def tearDown(self):
        # Clean up run after every test method.
        pass

    def test_request_with_no_auth_when_it_needs_auth(self):
        response = self.logout()
        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)

    def test_request_with_no_auth_when_it_does_not_need_auth(self):
        response = self.login()
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_request_with__auth_when_it_needs_auth(self):
        response = self.login()
        self.assertEqual(response.status_code, HTTP_200_OK)
        token = response.data["token"]
        self.logout(token)
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_auth_with_stole_old_token(self):
        # first login
        response = self.client.post("/login", {"username": "vasco", "password": "pwd"})
        self.assertEqual(response.status_code, HTTP_200_OK)
        token = response.data["token"]

        # first logout
        self.logout(token)
        self.assertEqual(response.status_code, HTTP_200_OK)

        # second login
        response = self.client.post("/login", {"username": "vasco", "password": "pwd"})

        # second logout
        self.logout(token)
        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)

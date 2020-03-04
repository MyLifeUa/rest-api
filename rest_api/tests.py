from rest_framework.status import *
from rest_framework.test import APITestCase


# Create your tests here.
class AuthenticationTest(APITestCase):
    def setUp(self):
        pass

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

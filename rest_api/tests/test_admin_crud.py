from rest_framework.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
)
from rest_framework.test import APITestCase

from rest_api.tests.utils import create_user_and_login


class AdminRegistrationTest(APITestCase):


    def test_new_admin_missing_authentication(self):
        response = self.client.post("/admins", {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco",
                                                "last_name": "Ramos", "hospital": "Centro Hospitalar de São João"})
        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)

    def test_new_admin_missing_authorization(self):
        create_user_and_login(self.client, "client", "vasco", "vr@ua.pt", "pwd")
        response = self.client.post("/admins", {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco",
                                                "last_name": "Ramos", "hospital": "Centro Hospitalar de São João"})
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_new_admin_missing_parameters(self):
        create_user_and_login(self.client, "admin", "vasco", "vr@ua.pt", "pwd")
        response = self.client.post("/admins", {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco",
                                                "last_name": "Ramos"})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_new_admin_right_parameters(self):
        create_user_and_login(self.client, "admin", "vasco", "vr@ua.pt", "pwd")
        response = self.client.post("/admins", {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco",
                                                "last_name": "Ramos", "hospital": "Centro Hospitalar de São João"})
        self.assertEqual(response.status_code, HTTP_200_OK)

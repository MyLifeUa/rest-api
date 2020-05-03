from rest_framework.status import (
    HTTP_401_UNAUTHORIZED,
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
)
from rest_framework.test import APITestCase

from rest_api.tests.utils import create_user_and_login, login


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
        self.assertEqual(response.status_code, HTTP_201_CREATED)


class AdminUpdateTest(APITestCase):
    def setUp(self):
        # create admin
        create_user_and_login(self.client, "custom_admin", "ana@ua.pt", "ana@ua.pt", "pwd")

    def test_update_nothing(self):
        response = self.client.put("/admins/ana@ua.pt", {})
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_update_wrong_parameters(self):
        response = self.client.put("/admins/ana@ua.pt", {"aaaa": "aaa"})
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_correct_update(self):
        response = self.client.put("/admins/ana@ua.pt", {"first_name": "Ana"})
        self.assertEqual(response.status_code, HTTP_200_OK)


class AdminDeleteTest(APITestCase):
    def setUp(self):
        # create admin
        create_user_and_login(self.client, "custom_admin", "ana@ua.pt", "ana@ua.pt", "pwd")

    def test_delete_non_existent_user(self):
        response = self.client.delete("/admins/vr@ua.pt")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_delete_other_admin_account(self):
        # create other admin
        create_user_and_login(self.client, "custom_admin", "admin@ua.pt", "admin@ua.pt", "pwd")

        self.client.delete("admins/admin@ua.pt")

    def test_delete_self(self):
        response = self.client.delete("/admins/ana@ua.pt")
        self.assertEqual(response.status_code, HTTP_200_OK)


class GetAdminTest(APITestCase):
    def setUp(self):
        # create admin
        create_user_and_login(self.client, "custom_admin", "ana@ua.pt", "ana@ua.pt", "pwd")

    def test_client_get_admin_info(self):
        # create client
        response = self.client.post("/clients", {"email": "tos@ua.pt", "password": "pwd", "first_name": "Tomas",
                                                 "last_name": "Ramos", "height": 1.60, "weight_goal": 65,
                                                 "current_weight": 90, "sex": "Male",
                                                 "birth_date": "2020-03-04"})
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        login(self.client, "tos@ua.pt", "pwd")

        response = self.client.get("/admins/ana@ua.pt")
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_doctor_same_hospital_get_admin_info(self):
        response = self.client.post("/doctors", {"email": "jose@ua.pt", "password": "pwd", "first_name": "Vasco",
                                                 "last_name": "Ramos", "birth_date": "2020-03-04"})
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        login(self.client, "jose@ua.pt", "pwd")

        response = self.client.get("/admins/ana@ua.pt")
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_doctor_different_hospital_get_admin_info(self):
        # create other admin
        create_user_and_login(self.client, "custom_admin", "admin@ua.pt", "admin@ua.pt", "pwd")

        # create doctor from different hospital
        response = self.client.post("/doctors", {"email": "jose@ua.pt", "password": "pwd", "first_name": "Vasco",
                                                 "last_name": "Ramos", "birth_date": "2020-03-04"})
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        response = self.client.get("/admins/ana@ua.pt")
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_other_admin_get_admin_info(self):
        # create other admin
        create_user_and_login(self.client, "custom_admin", "admin@ua.pt", "admin@ua.pt", "pwd")

        response = self.client.get("/admins/ana@ua.pt")
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_get_admin_self_info(self):
        response = self.client.get("/admins/ana@ua.pt")
        self.assertEqual(response.status_code, HTTP_200_OK)

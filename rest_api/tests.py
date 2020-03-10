from django.contrib.auth.models import User, Group
from rest_framework.status import HTTP_401_UNAUTHORIZED, HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.test import APITestCase


# Create your tests here.
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
        response = self.client.post("/login", {"username": "vasco", "password": "pwd"})
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


class ClientRegistrationTest(APITestCase):
    def tearDown(self):
        # Clean up run after every test method.
        pass

    def test_new_client_missing_parameters(self):
        response = self.client.post("/clients", {"email": "vr@ua.pt"})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        response = self.client.post("/clients", {"email": "vr@ua.pt", "password": "pwd"})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        response = self.client.post("/clients", {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco"})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        response = self.client.post("/clients", {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco",
                                                 "last_name": "Ramos"})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        response = self.client.post("/clients", {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco",
                                                 "last_name": "Ramos", "height": 111})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_new_client_right_parameters(self):
        response = self.client.post("/clients", {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco",
                                                 "last_name": "Ramos", "height": 1.60, "weight_goal": 65})
        self.assertEqual(response.status_code, HTTP_200_OK)


class AdminRegistrationTest(APITestCase):
    def tearDown(self):
        # Clean up run after every test method.
        pass

    def test_new_admin_missing_authentication(self):
        response = self.client.post("/admins", {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco",
                                                "last_name": "Ramos", "hospital": "Centro Hospitalar de São João"})
        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)

    """
    def test_new_admin_missing_authorization(self):

    def test_new_admin_missing_parameters(self):
        response = self.client.post("/clients", {"email": "vr@ua.pt"})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        response = self.client.post("/clients", {"email": "vr@ua.pt", "password": "pwd"})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        response = self.client.post("/clients", {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco"})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        response = self.client.post("/clients", {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco",
                                                 "last_name": "Ramos"})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        response = self.client.post("/clients", {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco",
                                                 "last_name": "Ramos", "height": 111})
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

    def test_new_admin_right_parameters(self):
        response = self.client.post("/clients", {"email": "vr@ua.pt", "password": "pwd", "first_name": "Vasco",
                                                 "last_name": "Ramos", "height": 1.60, "weight_goal": 65})
        self.assertEqual(response.status_code, HTTP_200_OK)
    """

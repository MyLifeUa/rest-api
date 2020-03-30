from rest_framework.test import APITestCase
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
)


class HelloWorldTest(APITestCase):
    def test_hello_world_wrong_request_type(self):
        response = self.client.post("/hello-word")
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_hello_world_correct_request_typen(self):
        response = self.client.get("/hello-word")
        self.assertEqual(response.status_code, HTTP_200_OK)

from rest_framework.test import APITestCase
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_405_METHOD_NOT_ALLOWED
)

'''
class HelloWorldTest(APITestCase):
    def test_hello_world_wrong_request_type(self):
        response = self.client.post("/hello-world")
        self.assertEqual(response.status_code, HTTP_405_METHOD_NOT_ALLOWED)

    def test_hello_world_correct_request_type(self):
        response = self.client.get("/hello-world")
        self.assertEqual(response.status_code, HTTP_200_OK)
'''
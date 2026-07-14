"""CRDS API tests."""

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient


class APIAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="operator", password="testpass123")

    def test_health_endpoint_public(self):
        response = self.client.get("/healthz")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_protected_endpoint_requires_auth(self):
        response = self.client.get("/monitor/status")
        self.assertEqual(response.status_code, 401)

    def test_jwt_login_and_access(self):
        login = self.client.post(
            "/api/auth/login/",
            {"username": "operator", "password": "testpass123"},
            format="json",
        )
        self.assertEqual(login.status_code, 200)
        token = login.json()["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get("/monitor/status")
        self.assertEqual(response.status_code, 200)

    def test_model_info_endpoint(self):
        login = self.client.post(
            "/api/auth/login/",
            {"username": "operator", "password": "testpass123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.json()['access']}")
        response = self.client.get("/api/model/info")
        self.assertEqual(response.status_code, 200)
        self.assertIn("loaded", response.json())

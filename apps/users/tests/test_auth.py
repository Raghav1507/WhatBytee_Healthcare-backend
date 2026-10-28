"""Tests for authentication endpoints."""
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class AuthTests(APITestCase):
    """Covers register, login, token refresh, logout, and /me."""

    def setUp(self):
        self.register_url = "/api/auth/register/"
        self.login_url = "/api/auth/login/"
        self.me_url = "/api/auth/me/"
        self.refresh_url = "/api/auth/token/refresh/"

    # ------------------------------------------------------------------ register
    def test_register_success(self):
        payload = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "Str0ngPass!23",
            "password2": "Str0ngPass!23",
        }
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["email"], "john@example.com")
        self.assertNotIn("password", response.data["data"])
        self.assertTrue(User.objects.filter(email="john@example.com").exists())

    def test_register_duplicate_email_rejected(self):
        payload = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "password": "Str0ngPass!23",
            "password2": "Str0ngPass!23",
        }
        self.client.post(self.register_url, payload, format="json")
        # Second attempt with same email (case-insensitive).
        payload["email"] = "JANE@EXAMPLE.COM"
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data["error"]["details"])

    def test_register_password_mismatch(self):
        payload = {
            "name": "Sam",
            "email": "sam@example.com",
            "password": "Str0ngPass!23",
            "password2": "DifferentPass!23",
        }
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password2", response.data["error"]["details"])

    def test_register_weak_password_rejected(self):
        payload = {
            "name": "Weak",
            "email": "weak@example.com",
            "password": "123",
            "password2": "123",
        }
        response = self.client.post(self.register_url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_fields(self):
        response = self.client.post(self.register_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        details = response.data["error"]["details"]
        for field in ("name", "email", "password", "password2"):
            self.assertIn(field, details)

    # --------------------------------------------------------------------- login
    def test_login_success_returns_jwt(self):
        User.objects.create_user(
            email="login@example.com", password="Str0ngPass!23", name="Login User"
        )
        response = self.client.post(
            self.login_url,
            {"email": "login@example.com", "password": "Str0ngPass!23"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data["data"]
        self.assertIn("access", data)
        self.assertIn("refresh", data)
        self.assertEqual(data["user"]["email"], "login@example.com")

    def test_login_wrong_password(self):
        User.objects.create_user(
            email="wrong@example.com", password="Str0ngPass!23", name="W"
        )
        response = self.client.post(
            self.login_url,
            {"email": "wrong@example.com", "password": "bad-password"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_unknown_email(self):
        response = self.client.post(
            self.login_url,
            {"email": "ghost@example.com", "password": "whatever123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # -------------------------------------------------------------- token refresh
    def test_token_refresh(self):
        User.objects.create_user(
            email="refresh@example.com", password="Str0ngPass!23", name="R"
        )
        login = self.client.post(
            self.login_url,
            {"email": "refresh@example.com", "password": "Str0ngPass!23"},
            format="json",
        )
        refresh = login.data["data"]["refresh"]
        response = self.client.post(
            self.refresh_url, {"refresh": refresh}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data["data"])

    # ------------------------------------------------------------------------ me
    def test_me_requires_auth(self):
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_profile(self):
        User.objects.create_user(
            email="me@example.com", password="Str0ngPass!23", name="Me User"
        )
        login = self.client.post(
            self.login_url,
            {"email": "me@example.com", "password": "Str0ngPass!23"},
            format="json",
        )
        token = login.data["data"]["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["email"], "me@example.com")

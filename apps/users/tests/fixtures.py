"""Shared test fixtures for the API test suite."""
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

User = get_user_model()


class BaseTestCase(APITestCase):
    """Provides two users plus authenticated clients for permission tests."""

    @classmethod
    def setUpTestData(cls):
        cls.user_a = User.objects.create_user(
            email="alice@example.com",
            password="Str0ngPass!23",
            name="Alice Owner",
        )
        cls.user_b = User.objects.create_user(
            email="bob@example.com",
            password="Str0ngPass!23",
            name="Bob Other",
        )

    def authenticate(self, user=None, password="Str0ngPass!23"):
        """Log a user in and attach the JWT to the test client."""
        from rest_framework_simplejwt.tokens import RefreshToken

        user = user or self.user_a
        token = str(RefreshToken.for_user(user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return token

    def login(self, email, password):
        """Perform a real login through the API and use the returned token."""
        response = self.client.post(
            "/api/auth/login/",
            {"email": email, "password": password},
            format="json",
        )
        if response.status_code == 200:
            access = response.data["data"]["access"]
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        return response

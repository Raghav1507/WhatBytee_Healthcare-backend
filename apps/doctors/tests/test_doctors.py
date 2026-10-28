"""Tests for doctor CRUD endpoints."""
from rest_framework import status
from rest_framework.test import APITestCase

from apps.doctors.models import Doctor
from apps.users.models import User


class DoctorApiTests(APITestCase):
    """Covers the full /api/doctors/ lifecycle."""

    def setUp(self):
        self.url = "/api/doctors/"
        self.user = User.objects.create_user(
            email="docowner@example.com", password="Str0ngPass!23", name="Owner"
        )
        self.other = User.objects.create_user(
            email="docother@example.com", password="Str0ngPass!23", name="Other"
        )
        self._auth(self.user)

    def _auth(self, user, password="Str0ngPass!23"):
        from rest_framework_simplejwt.tokens import RefreshToken

        token = str(RefreshToken.for_user(user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def _payload(self, **overrides):
        payload = {
            "name": "House",
            "specialization": "Diagnostic Medicine",
            "email": "house@example.com",
            "phone": "+1 555 0199",
            "license_number": "LIC-001",
            "years_of_experience": 12,
            "hospital": "Princeton-Plainsboro",
        }
        payload.update(overrides)
        return payload

    # ------------------------------------------------------------------ auth
    def test_list_requires_authentication(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ----------------------------------------------------------------- create
    def test_create_doctor(self):
        response = self.client.post(self.url, self._payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["name"], "House")
        self.assertEqual(response.data["data"]["full_name"], "Dr. House")
        self.assertTrue(Doctor.objects.filter(created_by=self.user).exists())

    def test_create_doctor_missing_fields(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        details = response.data["error"]["details"]
        for field in ("name", "specialization"):
            self.assertIn(field, details)

    def test_duplicate_license_rejected(self):
        self.client.post(self.url, self._payload(), format="json")
        response = self.client.post(
            self.url, self._payload(email="other@example.com"), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unrealistic_experience_rejected(self):
        response = self.client.post(
            self.url, self._payload(years_of_experience=200), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ------------------------------------------------------------------- list
    def test_list_only_returns_own_doctors(self):
        self.client.post(self.url, self._payload(), format="json")
        Doctor.objects.create(
            name="Foreman",
            specialization="Neurology",
            created_by=self.other,
        )
        response = self.client.get(self.url)
        results = response.data["data"]["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "House")

    def test_search_by_specialization(self):
        self.client.post(self.url, self._payload(), format="json")
        self.client.post(
            self.url,
            self._payload(
                name="Cuddy", specialization="Admin", email="c@example.com",
                license_number="LIC-002",
            ),
            format="json",
        )
        response = self.client.get(f"{self.url}?specialization=cardio")
        # "Diagnostic Medicine" does not contain "cardio"; expect 0.
        self.assertEqual(response.data["data"]["count"], 0)
        response = self.client.get(f"{self.url}?search=diagnostic")
        self.assertEqual(response.data["data"]["count"], 1)

    # ----------------------------------------------------------------- detail
    def test_retrieve_own_doctor(self):
        created = self.client.post(self.url, self._payload(), format="json")
        doctor_id = created.data["data"]["id"]
        response = self.client.get(f"{self.url}{doctor_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], "House")

    def test_cannot_retrieve_other_users_doctor(self):
        foreign = Doctor.objects.create(
            name="Foreign", specialization="Other", created_by=self.other
        )
        response = self.client.get(f"{self.url}{foreign.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ----------------------------------------------------------------- update
    def test_update_doctor(self):
        created = self.client.post(self.url, self._payload(), format="json")
        doctor_id = created.data["data"]["id"]
        response = self.client.put(
            f"{self.url}{doctor_id}/",
            self._payload(name="Updated Doc", specialization="Cardiology"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["specialization"], "Cardiology")

    def test_cannot_update_other_users_doctor(self):
        foreign = Doctor.objects.create(
            name="Foreign", specialization="Other", created_by=self.other
        )
        response = self.client.put(
            f"{self.url}{foreign.id}/", self._payload(name="Hack"), format="json"
        )
        # Scoped querysets hide other users' records entirely (404), which
        # avoids leaking the existence of doctor IDs.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ----------------------------------------------------------------- delete
    def test_delete_doctor(self):
        created = self.client.post(self.url, self._payload(), format="json")
        doctor_id = created.data["data"]["id"]
        response = self.client.delete(f"{self.url}{doctor_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Doctor.objects.filter(id=doctor_id).exists())

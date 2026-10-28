"""Tests for patient CRUD endpoints."""
from rest_framework import status
from rest_framework.test import APITestCase

from apps.patients.models import Patient
from apps.users.models import User


class PatientApiTests(APITestCase):
    """Covers the full /api/patients/ lifecycle."""

    def setUp(self):
        self.url = "/api/patients/"
        self.user = User.objects.create_user(
            email="owner@example.com", password="Str0ngPass!23", name="Owner"
        )
        self.other = User.objects.create_user(
            email="other@example.com", password="Str0ngPass!23", name="Other"
        )
        self._auth(self.user)

    def _auth(self, user, password="Str0ngPass!23"):
        from rest_framework_simplejwt.tokens import RefreshToken

        token = str(RefreshToken.for_user(user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def _payload(self, **overrides):
        payload = {
            "name": "Patient Zero",
            "age": 30,
            "gender": "male",
            "phone": "+1 555 0100",
            "email": "patient@example.com",
            "address": "123 Main St",
        }
        payload.update(overrides)
        return payload

    # ------------------------------------------------------------------ auth
    def test_list_requires_authentication(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ----------------------------------------------------------------- create
    def test_create_patient(self):
        response = self.client.post(self.url, self._payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["name"], "Patient Zero")
        self.assertEqual(response.data["data"]["created_by"], "owner@example.com")
        self.assertTrue(Patient.objects.filter(created_by=self.user).exists())

    def test_create_patient_invalid_age(self):
        response = self.client.post(
            self.url, self._payload(age=-1), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_patient_invalid_gender(self):
        response = self.client.post(
            self.url, self._payload(gender="unknown"), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_patient_invalid_phone(self):
        response = self.client.post(
            self.url, self._payload(phone="not-a-phone"), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_missing_required_fields(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        details = response.data["error"]["details"]
        for field in ("name", "age", "gender"):
            self.assertIn(field, details)

    # ------------------------------------------------------------------- list
    def test_list_only_returns_own_patients(self):
        self.client.post(self.url, self._payload(name="Mine"), format="json")
        # Create a patient owned by the other user directly.
        Patient.objects.create(
            name="Theirs", age=50, gender="female", created_by=self.other
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data["data"]["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Mine")

    def test_search_filter(self):
        self.client.post(self.url, self._payload(name="Alice"), format="json")
        self.client.post(self.url, self._payload(name="Bob"), format="json")
        response = self.client.get(f"{self.url}?search=alice")
        results = response.data["data"]["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Alice")

    # ----------------------------------------------------------------- detail
    def test_retrieve_own_patient(self):
        created = self.client.post(self.url, self._payload(), format="json")
        patient_id = created.data["data"]["id"]
        response = self.client.get(f"{self.url}{patient_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], "Patient Zero")

    def test_cannot_retrieve_other_users_patient(self):
        foreign = Patient.objects.create(
            name="Foreign", age=40, gender="other", created_by=self.other
        )
        response = self.client.get(f"{self.url}{foreign.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ----------------------------------------------------------------- update
    def test_update_patient(self):
        created = self.client.post(self.url, self._payload(), format="json")
        patient_id = created.data["data"]["id"]
        response = self.client.put(
            f"{self.url}{patient_id}/",
            self._payload(name="Updated Name", age=31),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], "Updated Name")

    def test_partial_update_patient(self):
        created = self.client.post(self.url, self._payload(), format="json")
        patient_id = created.data["data"]["id"]
        response = self.client.patch(
            f"{self.url}{patient_id}/", {"address": "New Address"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["address"], "New Address")

    def test_cannot_update_other_users_patient(self):
        foreign = Patient.objects.create(
            name="Foreign", age=40, gender="other", created_by=self.other
        )
        response = self.client.put(
            f"{self.url}{foreign.id}/", self._payload(name="Hack"), format="json"
        )
        # Scoped querysets hide other users' records entirely (404), which
        # avoids leaking the existence of patient IDs.
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ----------------------------------------------------------------- delete
    def test_delete_patient(self):
        created = self.client.post(self.url, self._payload(), format="json")
        patient_id = created.data["data"]["id"]
        response = self.client.delete(f"{self.url}{patient_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Patient.objects.filter(id=patient_id).exists())

    def test_delete_nonexistent_patient(self):
        import uuid

        response = self.client.delete(f"{self.url}{uuid.uuid4()}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

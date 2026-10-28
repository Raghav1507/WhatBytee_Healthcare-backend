"""Tests for patient-doctor mapping endpoints."""
import uuid

from rest_framework import status
from rest_framework.test import APITestCase

from apps.doctors.models import Doctor
from apps.mappings.models import PatientDoctorMapping
from apps.patients.models import Patient
from apps.users.models import User


class MappingApiTests(APITestCase):
    """Covers assignment, listing, lookup by patient, and removal."""

    def setUp(self):
        self.url = "/api/mappings/"
        self.user = User.objects.create_user(
            email="mapowner@example.com", password="Str0ngPass!23", name="Owner"
        )
        self.other = User.objects.create_user(
            email="mapother@example.com", password="Str0ngPass!23", name="Other"
        )
        self._auth(self.user)

        self.patient = Patient.objects.create(
            name="Pat", age=30, gender="male", created_by=self.user
        )
        self.doctor = Doctor.objects.create(
            name="Who", specialization="Internal Medicine", created_by=self.user
        )

    def _auth(self, user, password="Str0ngPass!23"):
        from rest_framework_simplejwt.tokens import RefreshToken

        token = str(RefreshToken.for_user(user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # ------------------------------------------------------------------ auth
    def test_list_requires_authentication(self):
        self.client.credentials()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # --------------------------------------------------------------- create
    def test_assign_doctor_to_patient(self):
        payload = {"patient": str(self.patient.id), "doctor": str(self.doctor.id)}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertTrue(
            PatientDoctorMapping.objects.filter(
                patient=self.patient, doctor=self.doctor
            ).exists()
        )

    def test_assign_duplicate_doctor_rejected(self):
        payload = {"patient": str(self.patient.id), "doctor": str(self.doctor.id)}
        self.client.post(self.url, payload, format="json")
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("doctor", response.data["error"]["details"])

    def test_cannot_assign_to_foreign_patient(self):
        foreign_patient = Patient.objects.create(
            name="Foreign", age=40, gender="female", created_by=self.other
        )
        payload = {"patient": str(foreign_patient.id), "doctor": str(self.doctor.id)}
        response = self.client.post(self.url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("patient", response.data["error"]["details"])

    def test_assign_invalid_ids(self):
        response = self.client.post(
            self.url,
            {"patient": str(uuid.uuid4()), "doctor": str(uuid.uuid4())},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ----------------------------------------------------------------- list
    def test_list_mappings(self):
        self.client.post(
            self.url,
            {"patient": str(self.patient.id), "doctor": str(self.doctor.id)},
            format="json",
        )
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["count"], 1)

    # ---------------------------------------------------- get doctors by patient
    def test_get_doctors_for_patient(self):
        PatientDoctorMapping.objects.create(
            patient=self.patient, doctor=self.doctor, assigned_by=self.user
        )
        response = self.client.get(f"{self.url}{self.patient.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data["data"]
        self.assertEqual(data["patient_id"], str(self.patient.id))
        self.assertEqual(data["count"], 1)
        self.assertEqual(data["assigned_doctors"][0]["doctor"]["name"], "Who")

    def test_get_doctors_for_foreign_patient_404(self):
        foreign = Patient.objects.create(
            name="Foreign", age=20, gender="other", created_by=self.other
        )
        response = self.client.get(f"{self.url}{foreign.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # -------------------------------------------------------------- delete
    def test_remove_mapping(self):
        mapping = PatientDoctorMapping.objects.create(
            patient=self.patient, doctor=self.doctor, assigned_by=self.user
        )
        response = self.client.delete(f"{self.url}{mapping.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(PatientDoctorMapping.objects.filter(id=mapping.id).exists())

    def test_remove_nonexistent_mapping(self):
        response = self.client.delete(f"{self.url}{uuid.uuid4()}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cannot_remove_other_users_mapping(self):
        foreign_patient = Patient.objects.create(
            name="Foreign", age=20, gender="other", created_by=self.other
        )
        foreign_mapping = PatientDoctorMapping.objects.create(
            patient=foreign_patient, doctor=self.doctor, assigned_by=self.other
        )
        response = self.client.delete(f"{self.url}{foreign_mapping.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

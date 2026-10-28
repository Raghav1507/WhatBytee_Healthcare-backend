"""Patient-Doctor mapping model - assigns a doctor to a patient."""
import uuid

from django.conf import settings
from django.db import models

from apps.doctors.models import Doctor
from apps.patients.models import Patient


class PatientDoctorMapping(models.Model):
    """Join table linking a patient to an assigned doctor."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="mappings",
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="mappings",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="assigned_mappings",
    )
    notes = models.TextField(blank=True, default="")
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "patient_doctor_mappings"
        ordering = ["-assigned_at"]
        # A doctor can only be assigned to a given patient once.
        constraints = [
            models.UniqueConstraint(
                fields=["patient", "doctor"],
                name="unique_patient_doctor_mapping",
            )
        ]
        indexes = [
            models.Index(fields=["patient"], name="idx_mapping_patient"),
            models.Index(fields=["doctor"], name="idx_mapping_doctor"),
        ]

    def __str__(self):
        return f"{self.patient} -> {self.doctor}"

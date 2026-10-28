"""Patient model - a healthcare record created and owned by a user."""
import uuid

from django.conf import settings
from django.db import models

from core.validators import age_validators, phone_validator


class Gender(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"
    OTHER = "other", "Other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say", "Prefer not to say"


class Patient(models.Model):
    """Represents a patient registered by an authenticated user."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    age = models.PositiveSmallIntegerField(validators=age_validators)
    gender = models.CharField(max_length=20, choices=Gender.choices)
    phone = models.CharField(
        max_length=20,
        validators=[phone_validator],
        blank=True,
        default="",
    )
    email = models.EmailField(max_length=255, blank=True, default="")
    address = models.TextField(blank=True, default="")
    medical_history = models.TextField(
        blank=True,
        default="",
        help_text="Optional free-text medical history / notes.",
    )

    # Ownership: only the creator can read/update/delete this record.
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patients",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "patients"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["created_by", "name"], name="idx_patient_owner_name"),
            models.Index(fields=["created_at"], name="idx_patient_created_at"),
        ]

    def __str__(self):
        return f"{self.name} ({self.age}, {self.get_gender_display()})"

    @property
    def doctors(self):
        """Doctors currently assigned to this patient."""
        return self.mappings.select_related("doctor").values_list(
            "doctor", flat=True
        )

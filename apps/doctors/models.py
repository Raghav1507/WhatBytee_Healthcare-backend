"""Doctor model - a healthcare professional record."""
import uuid

from django.conf import settings
from django.db import models

from core.validators import phone_validator


class Doctor(models.Model):
    """Represents a doctor added by an authenticated user."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    specialization = models.CharField(
        max_length=120,
        help_text="e.g. Cardiology, Dermatology, Pediatrics.",
    )
    email = models.EmailField(max_length=255, unique=True, blank=True, default="")
    phone = models.CharField(
        max_length=20,
        validators=[phone_validator],
        blank=True,
        default="",
    )
    license_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        default="",
        help_text="Medical license / registration number.",
    )
    years_of_experience = models.PositiveSmallIntegerField(
        default=0,
        help_text="Years of professional practice.",
    )
    hospital = models.CharField(max_length=200, blank=True, default="")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctors",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "doctors"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["specialization"], name="idx_doctor_specialization"),
            models.Index(fields=["created_at"], name="idx_doctor_created_at"),
        ]

    def __str__(self):
        return f"Dr. {self.name} ({self.specialization})"

"""Serializers for patient-doctor mappings."""
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from apps.doctors.serializers import DoctorSerializer

from .models import PatientDoctorMapping


class MappingSerializer(serializers.ModelSerializer):
    """Full representation of a patient-doctor mapping with nested names."""

    patient_name = serializers.CharField(source="patient.name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.name", read_only=True)
    doctor_specialization = serializers.CharField(
        source="doctor.specialization", read_only=True
    )
    assigned_by = serializers.EmailField(source="assigned_by.email", read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = (
            "id",
            "patient",
            "patient_name",
            "doctor",
            "doctor_name",
            "doctor_specialization",
            "notes",
            "assigned_by",
            "assigned_at",
        )
        read_only_fields = ("id", "assigned_by", "assigned_at")


class MappingCreateSerializer(serializers.ModelSerializer):
    """Serializer used when creating a mapping - validates ownership and
    duplicates."""

    class Meta:
        model = PatientDoctorMapping
        fields = ("id", "patient", "doctor", "notes")
        read_only_fields = ("id",)

    def __init__(self, *args, **kwargs):
        """Drop DRF's auto-generated UniqueTogetherValidator so duplicates are
        reported on the `doctor` field with a friendlier message instead of a
        generic `non_field_errors` entry."""
        super().__init__(*args, **kwargs)
        self.validators = [
            v
            for v in self.validators
            if not isinstance(v, UniqueTogetherValidator)
        ]

    def validate(self, attrs):
        request = self.context.get("request")
        patient = attrs.get("patient")
        doctor = attrs.get("doctor")

        # Ensure the requesting user owns the patient record.
        if request and patient.created_by != request.user:
            raise serializers.ValidationError(
                {"patient": "You can only assign doctors to patients you created."}
            )

        # Prevent duplicate assignments.
        if PatientDoctorMapping.objects.filter(
            patient=patient, doctor=doctor
        ).exists():
            raise serializers.ValidationError(
                {"doctor": "This doctor is already assigned to the patient."}
            )
        return attrs


class PatientDoctorListSerializer(serializers.ModelSerializer):
    """Used by GET /api/mappings/<patient_id>/ to list doctors for a patient."""

    doctor = DoctorSerializer(read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = ("id", "doctor", "notes", "assigned_at")

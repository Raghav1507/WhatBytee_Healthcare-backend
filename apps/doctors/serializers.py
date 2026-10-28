"""Serializers for doctor records with full validation."""
from rest_framework import serializers

from .models import Doctor


class DoctorSerializer(serializers.ModelSerializer):
    """Full representation of a doctor."""

    created_by = serializers.EmailField(source="created_by.email", read_only=True)
    full_name = serializers.SerializerMethodField()
    patient_count = serializers.SerializerMethodField()

    class Meta:
        model = Doctor
        fields = (
            "id",
            "name",
            "full_name",
            "specialization",
            "email",
            "phone",
            "license_number",
            "years_of_experience",
            "hospital",
            "patient_count",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_by", "created_at", "updated_at")

    def get_full_name(self, obj):
        return f"Dr. {obj.name}"

    def get_patient_count(self, obj):
        return obj.mappings.count()

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError(
                "Name must be at least 2 characters long."
            )
        return value

    def validate_email(self, value):
        return value.lower() if value else value

    def validate_years_of_experience(self, value):
        if value > 80:
            raise serializers.ValidationError(
                "Years of experience seems unrealistic (max 80)."
            )
        return value

    def validate_specialization(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError(
                "Specialization must be at least 2 characters long."
            )
        return value


class DoctorCreateUpdateSerializer(serializers.ModelSerializer):
    """Slim serializer for create/update operations."""

    class Meta:
        model = Doctor
        fields = (
            "id",
            "name",
            "specialization",
            "email",
            "phone",
            "license_number",
            "years_of_experience",
            "hospital",
        )
        read_only_fields = ("id",)

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError(
                "Name must be at least 2 characters long."
            )
        return value

    def validate_email(self, value):
        return value.lower() if value else value

    def validate_years_of_experience(self, value):
        if value > 80:
            raise serializers.ValidationError(
                "Years of experience seems unrealistic (max 80)."
            )
        return value

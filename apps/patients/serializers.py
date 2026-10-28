"""Serializers for patient records with full validation."""
from rest_framework import serializers

from .models import Gender, Patient


class PatientSerializer(serializers.ModelSerializer):
    """Full representation of a patient, including owner and denormalized data."""

    created_by = serializers.EmailField(source="created_by.email", read_only=True)
    gender_display = serializers.CharField(source="get_gender_display", read_only=True)
    doctor_count = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = (
            "id",
            "name",
            "age",
            "gender",
            "gender_display",
            "phone",
            "email",
            "address",
            "medical_history",
            "doctor_count",
            "created_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_by", "created_at", "updated_at")

    def get_doctor_count(self, obj):
        return obj.mappings.count()

    def validate_age(self, value):
        if not 0 <= value <= 150:
            raise serializers.ValidationError("Age must be between 0 and 150.")
        return value

    def validate_email(self, value):
        return value.lower() if value else value

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError(
                "Name must be at least 2 characters long."
            )
        return value


class PatientDetailSerializer(PatientSerializer):
    """Patient detail payload including the list of assigned doctors."""

    doctors = serializers.SerializerMethodField()

    class Meta(PatientSerializer.Meta):
        fields = (*PatientSerializer.Meta.fields, "doctors")

    def get_doctors(self, obj):
        # Imported lazily to avoid a circular import with the mapping serializer.
        from apps.doctors.serializers import DoctorSerializer

        doctors = [m.doctor for m in obj.mappings.select_related("doctor")]
        return DoctorSerializer(doctors, many=True).data


class PatientCreateUpdateSerializer(serializers.ModelSerializer):
    """Slim serializer for create/update - hides computed/owner fields."""

    class Meta:
        model = Patient
        fields = (
            "id",
            "name",
            "age",
            "gender",
            "phone",
            "email",
            "address",
            "medical_history",
        )
        read_only_fields = ("id",)

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError(
                "Name must be at least 2 characters long."
            )
        return value

    def validate_age(self, value):
        if not 0 <= value <= 150:
            raise serializers.ValidationError("Age must be between 0 and 150.")
        return value

    def validate_gender(self, value):
        valid = {choice.value for choice in Gender}
        if value not in valid:
            raise serializers.ValidationError(
                f"Invalid gender. Choose one of: {', '.join(sorted(valid))}."
            )
        return value

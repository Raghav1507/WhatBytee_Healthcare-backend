"""Patient-doctor mapping views.

Endpoint design notes
---------------------
The spec requires both:

* ``GET    /api/mappings/<patient_id>/`` - doctors assigned to a patient
* ``DELETE /api/mappings/<id>/``         - remove a doctor from a patient

Both share the same URL shape, so a single ``MappingDetailView`` disambiguates
by HTTP method: ``GET`` interprets the path parameter as a *patient id*, while
``DELETE`` interprets it as a *mapping id*.
"""
from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.patients.models import Patient
from core.exceptions import success_response

from .models import PatientDoctorMapping
from .serializers import (
    MappingCreateSerializer,
    MappingSerializer,
    PatientDoctorListSerializer,
)


class MappingListCreateView(generics.ListCreateAPIView):
    """``GET /api/mappings/`` - list mappings owned by the authenticated user.

    ``POST /api/mappings/`` - assign a doctor to a patient.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return MappingCreateSerializer
        return MappingSerializer

    def get_queryset(self):
        # A mapping is visible if the user owns the patient OR created the doctor.
        user = self.request.user
        return (
            PatientDoctorMapping.objects.filter(
                Q(patient__created_by=user) | Q(doctor__created_by=user)
            )
            .select_related("patient", "doctor", "assigned_by")
            .distinct()
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mapping = serializer.save(assigned_by=request.user)
        data = MappingSerializer(mapping).data
        return success_response(
            data=data,
            message="Doctor assigned to patient successfully.",
            status_code=status.HTTP_201_CREATED,
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)


class MappingDetailView(APIView):
    """Handles ``GET`` (by patient id) and ``DELETE`` (by mapping id)."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        """Return all doctors assigned to the given patient."""
        try:
            patient = Patient.objects.get(pk=pk, created_by=request.user)
        except (Patient.DoesNotExist, ValueError, ValidationError):
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "not_found",
                        "message": "Patient not found or you do not have access.",
                        "details": None,
                    },
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        mappings = (
            PatientDoctorMapping.objects.filter(patient=patient)
            .select_related("doctor", "patient")
            .order_by("-assigned_at")
        )
        serializer = PatientDoctorListSerializer(mappings, many=True)
        return success_response(
            data={
                "patient_id": str(patient.id),
                "patient_name": patient.name,
                "assigned_doctors": serializer.data,
                "count": mappings.count(),
            }
        )

    def delete(self, request, pk):
        """Remove a doctor from a patient via the mapping id."""
        try:
            mapping = (
                PatientDoctorMapping.objects.select_related(
                    "patient", "patient__created_by", "doctor"
                )
                .get(pk=pk)
            )
        except (PatientDoctorMapping.DoesNotExist, ValueError, ValidationError):
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "not_found",
                        "message": "Mapping not found.",
                        "details": None,
                    },
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Only the patient owner (or the mapping's assigner) may remove it.
        if (
            mapping.patient.created_by != request.user
            and mapping.assigned_by != request.user
        ):
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "permission_denied",
                        "message": "You do not have permission to remove this mapping.",
                        "details": None,
                    },
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        mapping.delete()
        return success_response(message="Doctor removed from patient successfully.")


class MappingDeleteView(generics.DestroyAPIView):
    """Alternative explicit delete route: ``DELETE /api/mappings/<id>/remove/``.

    Kept for clarity; the primary delete lives in ``MappingDetailView``.
    """

    permission_classes = [permissions.IsAuthenticated]
    queryset = PatientDoctorMapping.objects.all()

    def get_queryset(self):
        user = self.request.user
        return PatientDoctorMapping.objects.filter(
            Q(patient__created_by=user) | Q(assigned_by=user)
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response(message="Doctor removed from patient successfully.")

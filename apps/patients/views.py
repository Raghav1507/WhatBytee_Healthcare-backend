"""Patient CRUD views - secured to the authenticated owner."""
from django.db.models import Q
from rest_framework import generics, permissions, status

from core.exceptions import success_response
from core.permissions import IsOwnerOrReadOnly

from .models import Patient
from .serializers import (
    PatientCreateUpdateSerializer,
    PatientDetailSerializer,
    PatientSerializer,
)


class PatientListCreateView(generics.ListCreateAPIView):
    """`GET /api/patients/` and `POST /api/patients/`.

    - List: returns only patients created by the authenticated user,
      with optional search (`?search=`) and ordering (`?ordering=`).
    - Create: creates a patient owned by the authenticated user.
    """

    permission_classes = [permissions.IsAuthenticated]
    permission_classes_by_method = {
        "GET": [permissions.IsAuthenticated],
        "POST": [permissions.IsAuthenticated],
    }

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PatientCreateUpdateSerializer
        return PatientSerializer

    def get_queryset(self):
        user = self.request.user
        qs = (
            Patient.objects.filter(created_by=user)
            .select_related("created_by")
            .prefetch_related("mappings")
        )
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(email__icontains=search)
                | Q(phone__icontains=search)
            )
        ordering = self.request.query_params.get("ordering", "-created_at")
        allowed_orderings = {
            "created_at",
            "-created_at",
            "name",
            "-name",
            "age",
            "-age",
        }
        if ordering in allowed_orderings:
            qs = qs.order_by(ordering)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        patient = serializer.save(created_by=request.user)
        data = PatientDetailSerializer(patient).data
        return success_response(
            data=data,
            message="Patient created successfully.",
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


class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """`GET/PUT/PATCH/DELETE /api/patients/<id>/`.

    Owners can read, update, and delete their own patients; other users
    receive a 404 so patient existence is not leaked.
    """

    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return PatientCreateUpdateSerializer
        return PatientDetailSerializer

    def get_queryset(self):
        return (
            Patient.objects.filter(created_by=self.request.user)
            .select_related("created_by")
            .prefetch_related("mappings__doctor")
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(data=serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        data = PatientDetailSerializer(instance).data
        return success_response(
            data=data, message="Patient updated successfully."
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response(message="Patient deleted successfully.")

"""Doctor CRUD views - secured to the authenticated owner."""
from django.db.models import Q
from rest_framework import generics, permissions, status

from core.exceptions import success_response
from core.permissions import IsOwnerOrReadOnly

from .models import Doctor
from .serializers import DoctorCreateUpdateSerializer, DoctorSerializer


class DoctorListCreateView(generics.ListCreateAPIView):
    """`GET /api/doctors/` and `POST /api/doctors/`.

    - List: all doctors visible to the authenticated user, with optional
      `?search=` and `?specialization=` filters.
    - Create: adds a new doctor owned by the authenticated user.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return DoctorCreateUpdateSerializer
        return DoctorSerializer

    def get_queryset(self):
        qs = (
            Doctor.objects.filter(created_by=self.request.user)
            .select_related("created_by")
            .prefetch_related("mappings")
        )
        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(specialization__icontains=search)
                | Q(email__icontains=search)
                | Q(hospital__icontains=search)
            )
        specialization = self.request.query_params.get("specialization")
        if specialization:
            qs = qs.filter(specialization__icontains=specialization)
        ordering = self.request.query_params.get("ordering", "-created_at")
        allowed = {"created_at", "-created_at", "name", "-name", "specialization"}
        if ordering in allowed:
            qs = qs.order_by(ordering)
        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        doctor = serializer.save(created_by=request.user)
        data = DoctorSerializer(doctor).data
        return success_response(
            data=data,
            message="Doctor created successfully.",
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


class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """`GET/PUT/PATCH/DELETE /api/doctors/<id>/` for the owning user."""

    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return DoctorCreateUpdateSerializer
        return DoctorSerializer

    def get_queryset(self):
        return Doctor.objects.filter(
            created_by=self.request.user
        ).select_related("created_by")

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
        data = DoctorSerializer(instance).data
        return success_response(data=data, message="Doctor updated successfully.")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return success_response(message="Doctor deleted successfully.")

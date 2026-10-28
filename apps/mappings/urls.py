"""URL routes for patient-doctor mappings."""
from django.urls import path

from . import views

app_name = "mappings"

urlpatterns = [
    path("", views.MappingListCreateView.as_view(), name="mapping-list-create"),
    # GET    /api/mappings/<patient_id>/  -> doctors for a patient
    # DELETE /api/mappings/<id>/          -> remove a mapping
    path(
        "<uuid:pk>/",
        views.MappingDetailView.as_view(),
        name="mapping-detail",
    ),
]

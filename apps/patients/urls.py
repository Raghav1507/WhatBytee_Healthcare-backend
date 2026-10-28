"""URL routes for patient management."""
from django.urls import path

from . import views

app_name = "patients"

urlpatterns = [
    path("", views.PatientListCreateView.as_view(), name="patient-list-create"),
    path("<uuid:pk>/", views.PatientDetailView.as_view(), name="patient-detail"),
]

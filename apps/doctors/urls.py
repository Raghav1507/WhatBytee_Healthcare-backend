"""URL routes for doctor management."""
from django.urls import path

from . import views

app_name = "doctors"

urlpatterns = [
    path("", views.DoctorListCreateView.as_view(), name="doctor-list-create"),
    path("<uuid:pk>/", views.DoctorDetailView.as_view(), name="doctor-detail"),
]

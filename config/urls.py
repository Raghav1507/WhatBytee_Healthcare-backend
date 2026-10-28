"""Root URL configuration for the healthcare API."""
from django.contrib import admin
from django.urls import include, path

from core.views import api_root, api_tester, health_check

admin.site.site_header = "Healthcare Admin"
admin.site.site_title = "Healthcare Admin Portal"
admin.site.index_title = "Welcome to the Healthcare Admin"

urlpatterns = [
    # Friendly root index + health probe (no auth required).
    path("", api_root, name="api-root"),
    path("api/health/", health_check, name="health-check"),
    path("api/", api_root, name="api-root-alias"),

    # Interactive browser test console (signup/login/patients UI).
    path("test/", api_tester, name="api-tester"),

    # Django admin (protected by Django session auth).
    path("admin/", admin.site.urls),

    # Authentication: register / login / refresh / logout / me
    path("api/auth/", include("apps.users.urls")),

    # Domain APIs
    path("api/patients/", include("apps.patients.urls")),
    path("api/doctors/", include("apps.doctors.urls")),
    path("api/mappings/", include("apps.mappings.urls")),
]

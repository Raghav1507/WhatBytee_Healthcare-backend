"""Lightweight API root and health-check views.

Served at ``/`` so opening the base URL in a browser returns something useful
instead of Django's default 404 page.
"""
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render


def api_root(request):
    """A friendly index of every available API group."""
    return JsonResponse(
        {
            "service": "Healthcare Backend API",
            "status": "ok",
            "documentation": "See README.md and postman_collection.json",
            "authentication": {
                "type": "JWT (Bearer token)",
                "header": "Authorization: Bearer <access_token>",
            },
            "endpoints": {
                "auth": {
                    "register": "/api/auth/register/",
                    "login": "/api/auth/login/",
                    "token_refresh": "/api/auth/token/refresh/",
                    "logout": "/api/auth/logout/",
                    "me": "/api/auth/me/",
                },
                "patients": {
                    "list_create": "/api/patients/",
                    "detail": "/api/patients/<id>/",
                },
                "doctors": {
                    "list_create": "/api/doctors/",
                    "detail": "/api/doctors/<id>/",
                },
                "mappings": {
                    "list_create": "/api/mappings/",
                    "doctors_for_patient": "/api/mappings/<patient_id>/",
                    "remove": "/api/mappings/<id>/  (DELETE)",
                },
                "admin": "/admin/",
                "test_console": "/test/",
            },
        },
        json_dumps_params={"indent": 2},
    )


def health_check(request):
    """Liveness probe: verifies the app and database are reachable."""
    db_ok = True
    try:
        connection.ensure_connection()
    except Exception:
        db_ok = False

    return JsonResponse(
        {
            "status": "healthy" if db_ok else "degraded",
            "database": "up" if db_ok else "down",
        },
        status=200 if db_ok else 503,
    )


def api_tester(request):
    """Interactive browser console for exercising the API (signup/login/etc.)."""
    return render(request, "api_tester.html")

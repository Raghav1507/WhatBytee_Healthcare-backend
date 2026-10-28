"""Centralized API exception handling.

Every unhandled exception raised inside a DRF view is converted into a
consistent JSON envelope:

    {
        "success": false,
        "error": {
            "code": "validation_error",
            "message": "Unable to create account.",
            "details": { ... }
        }
    }

This gives API consumers a predictable contract regardless of the error.
"""
import logging

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    NotFound,
    PermissionDenied,
    Throttled,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)

# Human friendly default messages per code.
DEFAULT_MESSAGES = {
    "validation_error": "Invalid input provided.",
    "authentication_failed": "Authentication credentials were not provided or are invalid.",
    "not_authenticated": "Authentication credentials were not provided.",
    "permission_denied": "You do not have permission to perform this action.",
    "not_found": "The requested resource was not found.",
    "method_not_allowed": "HTTP method not allowed for this endpoint.",
    "throttled": "Request was throttled. Please slow down and try again.",
    "bad_request": "Bad request.",
    "conflict": "The request conflicts with the current state of the resource.",
    "rate_limited": "Too many requests. Please try again later.",
    "api_error": "A server error occurred. Please try again later.",
}


def _code_for(status_code: int) -> str:
    """Map an HTTP status code to a stable machine-readable error code."""
    mapping = {
        status.HTTP_400_BAD_REQUEST: "bad_request",
        status.HTTP_401_UNAUTHORIZED: "authentication_failed",
        status.HTTP_403_FORBIDDEN: "permission_denied",
        status.HTTP_404_NOT_FOUND: "not_found",
        status.HTTP_405_METHOD_NOT_ALLOWED: "method_not_allowed",
        status.HTTP_409_CONFLICT: "conflict",
        status.HTTP_429_TOO_MANY_REQUESTS: "rate_limited",
    }
    return mapping.get(status_code, "api_error")


def _code_for_exception(exc: APIException, status_code: int) -> str:
    """Derive a precise error code from a DRF exception when possible."""
    if isinstance(exc, ValidationError):
        return "validation_error"
    if isinstance(exc, (NotFound, Http404)):
        return "not_found"
    if isinstance(exc, (PermissionDenied, DjangoPermissionDenied)):
        return "permission_denied"
    if isinstance(exc, Throttled):
        return "throttled"
    return getattr(exc, "default_code", None) or _code_for(status_code)


def api_exception_handler(exc, context):
    """Custom DRF exception handler producing a uniform error envelope."""
    # Let DRF resolve the exception into a response first.
    response = drf_exception_handler(exc, context)

    if response is None:
        # Unhandled non-API exception (bug) - log it and return a safe 500.
        logger.exception("Unhandled API exception: %s", exc, exc_info=exc)
        return Response(
            {
                "success": False,
                "error": {
                    "code": "api_error",
                    "message": DEFAULT_MESSAGES["api_error"],
                    "details": None,
                },
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    status_code = response.status_code
    code = _code_for_exception(exc, status_code)
    message = getattr(exc, "detail", None)

    # `detail` may be a string, a list, or a nested dict of field errors.
    details = None
    if not isinstance(message, str):
        details = message
        message = DEFAULT_MESSAGES.get(code, DEFAULT_MESSAGES["api_error"])
    else:
        message = str(message)

    response.data = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details,
        },
    }
    return response


def success_response(data=None, message="OK", status_code=status.HTTP_200_OK):
    """Build a uniform success envelope used by the API views."""
    return Response(
        {"success": True, "message": message, "data": data},
        status=status_code,
    )

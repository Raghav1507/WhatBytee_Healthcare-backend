"""Reusable object-level permissions."""
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """Object-level permission: only the creator may edit/delete.

    Expects the protected model to expose a `created_by` attribute.
    Safe methods (GET, HEAD, OPTIONS) remain open to any authenticated user.
    """

    message = "You may only modify records that you created."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return getattr(obj, "created_by", None) == request.user


class IsOwner(BasePermission):
    """Object-level permission: strict owner-only access."""

    message = "You may only access your own records."

    def has_object_permission(self, request, view, obj):
        return getattr(obj, "created_by", None) == request.user

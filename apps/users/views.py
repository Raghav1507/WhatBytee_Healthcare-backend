"""Authentication views: register, login (JWT), token refresh, profile."""
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from core.exceptions import success_response

from .serializers import RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    """`POST /api/auth/register/` - create a new user account.

    Public (no authentication required) and rate-limited to prevent abuse.
    """

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = UserSerializer(user).data
        return success_response(
            data=data,
            message="User registered successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """`POST /api/auth/login/` - exchange credentials for a JWT pair.

    Returns `access` and `refresh` tokens plus the user's profile.
    """

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code != status.HTTP_200_OK:
            return response
        return success_response(
            data=response.data,
            message="Login successful.",
            status_code=status.HTTP_200_OK,
        )


class TokenRefreshView(TokenRefreshView):
    """`POST /api/auth/token/refresh/` - exchange a refresh token for a new
    access token."""

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code != status.HTTP_200_OK:
            return response
        return success_response(
            data=response.data,
            message="Token refreshed successfully.",
            status_code=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """`POST /api/auth/logout/` - blacklist the provided refresh token.

    Requires authentication. Stateless JWTs cannot be revoked server-side
    without a blacklist; this endpoint accepts the refresh token so it can be
    invalidated (enable the simplejwt blacklist app in production).
    """

    permission_classes = [permissions.IsAuthenticated]

    def _error(self, message, code="bad_request", status_code=status.HTTP_400_BAD_REQUEST):
        return Response(
            {
                "success": False,
                "error": {"code": code, "message": message, "details": None},
            },
            status=status_code,
        )

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return self._error("A `refresh` token is required.")
        try:
            RefreshToken(refresh_token)
        except TokenError:
            return self._error("Invalid or expired refresh token.")
        return success_response(message="Logout successful.")


class MeView(generics.RetrieveAPIView):
    """`GET /api/auth/me/` - return the authenticated user's profile."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return success_response(data=serializer.data)

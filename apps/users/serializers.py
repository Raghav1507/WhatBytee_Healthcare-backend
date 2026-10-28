"""Serializers for authentication: registration, login, and profile."""
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Public representation of a user (never exposes password)."""

    class Meta:
        model = User
        fields = ("id", "name", "email", "phone", "is_active", "date_joined")
        read_only_fields = ("id", "is_active", "date_joined")


class RegisterSerializer(serializers.ModelSerializer):
    """Handles `POST /api/auth/register/`.

    Validates the password with Django's built-in password validators and
    enforces confirmation on the client-supplied `password` field.
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        max_length=128,
        style={"input_type": "password"},
        help_text="Password must be at least 8 characters.",
    )
    password2 = serializers.CharField(
        write_only=True,
        min_length=8,
        max_length=128,
        style={"input_type": "password"},
        help_text="Repeat the password for confirmation.",
    )

    class Meta:
        model = User
        fields = ("id", "name", "email", "phone", "password", "password2")
        read_only_fields = ("id",)

    def validate_email(self, value):
        """Email must be unique (case-insensitive)."""
        normalized = value.lower()
        if User.objects.filter(email__iexact=normalized).exists():
            raise serializers.ValidationError(
                "A user with that email already exists."
            )
        return normalized

    def validate(self, attrs):
        """Ensure both password fields match and satisfy Django's validators."""
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password2": "Passwords do not match."}
            )
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        """Create the user; drop the confirmation field first."""
        validated_data.pop("password2", None)
        return User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            name=validated_data["name"],
            phone=validated_data.get("phone", ""),
        )


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Extends the stock JWT serializer to include user details in the token
    payload and return profile data alongside the tokens."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Custom claims embedded in both access and refresh tokens.
        token["name"] = user.name
        token["email"] = user.email
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data

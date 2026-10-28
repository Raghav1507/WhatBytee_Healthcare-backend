"""Shared field validators used across the clinical apps."""
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator

phone_validator = RegexValidator(
    regex=r"^\+?[\d\s\-()]{7,20}$",
    message="Phone number may only contain digits, spaces, +, -, and parentheses.",
)

age_validators = [MinValueValidator(0), MaxValueValidator(150)]

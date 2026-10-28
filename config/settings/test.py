"""Test settings - fast in-memory database, password hashing disabled."""
from .base import *

DEBUG = False
SECRET_KEY = "test-secret-key-not-for-production"

# In-memory SQLite keeps the test suite fast; swap in PostgreSQL by
# exporting DB_* env vars and overriding DATABASES if you prefer.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# No throttling during tests so they run at full speed. Views that declare
# their own `throttle_classes` ignore the empty default list, so the rates
# themselves are also raised very high to avoid cross-test 429s.
REST_FRAMEWORK = {
    **REST_FRAMEWORK,
    "DEFAULT_THROTTLE_CLASSES": [],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100000/minute",
        "user": "100000/minute",
        "auth": "100000/minute",
    },
}

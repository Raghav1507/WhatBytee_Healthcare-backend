"""Production settings - hardened security, no debug, HTTPS aware."""
from .base import *
from .base import env

DEBUG = False

SECRET_KEY = env("SECRET_KEY")  # must be provided in production
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# ------------------------------------------------------------------------------
# Security hardening (enable when serving over HTTPS)
# ------------------------------------------------------------------------------
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=True)
CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=True)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0
SECURE_HSTS_PRELOAD = SECURE_HSTS_SECONDS > 0

# CORS: explicit allow-list only, never "*" in production.
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")

# Use a real email backend in production (configure via env as needed).
EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)

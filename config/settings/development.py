"""Development settings - local work, verbose errors, relaxed hosts."""
from .base import *
from .base import env

DEBUG = True

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["*"])

# Show full Django REST Framework browsable-style tracebacks in the console.
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (
    "rest_framework.renderers.JSONRenderer",
)

LOGGING["loggers"]["django"]["level"] = "DEBUG"

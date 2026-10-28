"""Settings package entry point.

The active environment is selected with the `DJANGO_ENV` variable:

    DJANGO_ENV=development  (default)
    DJANGO_ENV=production
    DJANGO_ENV=test
"""
import os

_env = os.environ.get("DJANGO_ENV", "development").lower()

if _env == "production":
    from .production import *
elif _env == "test":
    from .test import *
else:
    from .development import *

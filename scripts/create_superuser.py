"""Create an admin/superuser for the Django admin site.

Usage:
    python scripts/create_superuser.py            # uses env vars below
    python scripts/create_superuser.py a@b.com "Pass!word" "Admin Name"

Environment variables (optional):
    SUPERUSER_EMAIL, SUPERUSER_PASSWORD, SUPERUSER_NAME
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

import config.bootstrap  # noqa: F401

django.setup()

from django.contrib.auth import get_user_model  # noqa: E402

User = get_user_model()


def main():
    email = (
        sys.argv[1]
        if len(sys.argv) > 1
        else os.environ.get("SUPERUSER_EMAIL", "admin@example.com")
    )
    password = (
        sys.argv[2]
        if len(sys.argv) > 2
        else os.environ.get("SUPERUSER_PASSWORD", "AdminPass!123")
    )
    name = (
        sys.argv[3]
        if len(sys.argv) > 3
        else os.environ.get("SUPERUSER_NAME", "Site Admin")
    )

    if User.objects.filter(email=email).exists():
        print(f"User {email} already exists - skipping.")
        return

    User.objects.create_superuser(email=email, password=password, name=name)
    print(f"Superuser created: {email}")


if __name__ == "__main__":
    main()

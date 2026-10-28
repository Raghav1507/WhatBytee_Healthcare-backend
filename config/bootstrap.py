"""Bootstrap helper: load `.env` into ``os.environ`` *before* Django's
settings module is imported.

This makes the ``DJANGO_ENV`` variable inside ``.env`` effective for selecting
the active settings module (development / production / test).
"""
import os
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


def load_env_file(path: Path = ENV_PATH) -> None:
    """Parse a simple ``KEY=VALUE`` .env file into ``os.environ``.

    Values already present in the real environment are never overwritten,
    so exported shell variables always win over file values.
    """
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


load_env_file()

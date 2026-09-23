"""Isolated model registry, never deployment or database execution settings.

This module retains the development guard and dummy backend. Auth/contenttypes
load maintained Django model definitions only, not routes or authentication.
"""

from glow_api.settings import *  # noqa: F403

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "glow_persistence.apps.PersistenceDesignConfig",
]
DATABASES = {"default": {"ENGINE": "django.db.backends.dummy"}}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "auth.User"

"""Intentionally database-free Django settings for isolated development/tests."""

import os

from django.core.exceptions import ImproperlyConfigured

from .configuration import ConfigurationError, load_configuration
from .telemetry import LOGGING as LOGGING
from .telemetry import Event, configure_logging, emit_event

configure_logging()
try:
    GLOW_CONFIGURATION = load_configuration(os.environ)
except ConfigurationError as exc:
    emit_event(Event.CONFIGURATION_REJECTED, outcome="rejected", error_code="configuration_invalid")
    raise ImproperlyConfigured(str(exc)) from None

GLOW_ENV = GLOW_CONFIGURATION.environment
# Public, development-only placeholder. There is no auth, session or signing
# endpoint. Production cannot start with this settings module.
SECRET_KEY = "glow-isolated-fixture-only-not-a-production-secret"
DEBUG = False
# Android's emulator reaches the host loopback through this explicit alias.
# This is a Host-header allowlist, not permission to bind to a public interface.
ALLOWED_HOSTS = list(GLOW_CONFIGURATION.allowed_hosts)

ROOT_URLCONF = "glow_api.urls"
WSGI_APPLICATION = "glow_api.wsgi.application"
INSTALLED_APPS = ["rest_framework"]
MIDDLEWARE = [
    "glow_api.telemetry.CorrelationMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
# No ORM driver or database connection exists. This intentionally uses Django's
# dummy backend rather than SQLite or an in-memory SQL database.
DATABASES = {"default": {"ENGINE": "django.db.backends.dummy"}}
USE_TZ = True
TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-us"
USE_I18N = False
APPEND_SLASH = False
DATA_UPLOAD_MAX_MEMORY_SIZE = 16_384
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "UNAUTHENTICATED_USER": None,
    "UNAUTHENTICATED_TOKEN": None,
}

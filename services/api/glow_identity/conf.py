"""SV1's settings fragment (the SV1 brief's D2, D3, D5 and D8).

What a settings module that serves sign-in adds. It holds no key, password or connection: the
settings module that uses it supplies ``SECRET_KEY``, ``HEADLESS_JWT_PRIVATE_KEY``,
``DATABASES`` (never with ``ATOMIC_REQUESTS``) and ``ALLOWED_HOSTS`` from its own secret
references. The proof's identity settings read the two keys from files generated for one run
(D10); P11 supplies them as secret references. No mail provider, SMTP setting, frontend URL,
social provider, multi-factor authentication, login by code or browser client is configured.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "rest_framework",
    "allauth",
    "allauth.account",
    "allauth.headless",
    # D5: UserSession's primary key is AccountSession.auth_session_ref.
    "allauth.usersessions",
    "glow_persistence.apps.PersistenceDesignConfig",
    "glow_identity.apps.IdentityConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

# D3: email and password through allauth's own backend; no username login.
AUTHENTICATION_BACKENDS = ["allauth.account.auth_backends.AuthenticationBackend"]

# D3: Django's hashers (its default list, unchanged) and its four validators, minimum 10.
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 10},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

SETTINGS: dict[str, Any] = {
    "INSTALLED_APPS": INSTALLED_APPS,
    "MIDDLEWARE": MIDDLEWARE,
    "AUTHENTICATION_BACKENDS": AUTHENTICATION_BACKENDS,
    "AUTH_PASSWORD_VALIDATORS": AUTH_PASSWORD_VALIDATORS,
    "AUTH_USER_MODEL": "auth.User",
    "ROOT_URLCONF": "glow_identity.urls",
    "DEFAULT_AUTO_FIELD": "django.db.models.BigAutoField",
    "USE_TZ": True,
    "TIME_ZONE": "UTC",
    "LANGUAGE_CODE": "en-us",
    "USE_I18N": False,
    "DEBUG": False,
    "APPEND_SLASH": False,
    "DATA_UPLOAD_MAX_MEMORY_SIZE": 16_384,
    "SECURE_CONTENT_TYPE_NOSNIFF": True,
    # D2: the database session store, whose expiry D2 aligns with AccountSession.expires_at.
    "SESSION_ENGINE": "django.contrib.sessions.backends.db",
    # D3: allauth's rate limits keep their defaults and use Django's cache. One process here;
    # P11 needs a shared cache for more than one worker.
    "CACHES": {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "glow-identity",
        }
    },
    # D8: the mail seam. The fixture backend records each message and has no network code.
    "EMAIL_BACKEND": "glow_identity.mail.FixtureEmailBackend",
    "DEFAULT_FROM_EMAIL": "Glow <no-reply@example.invalid>",
    # -- allauth's account app (D3, D4, D5, D8) --
    "ACCOUNT_ADAPTER": "glow_identity.adapter.GlowAccountAdapter",
    "ACCOUNT_LOGIN_METHODS": {"email"},
    "ACCOUNT_SIGNUP_FIELDS": ["email*", "password1*"],
    "ACCOUNT_UNIQUE_EMAIL": True,
    "ACCOUNT_EMAIL_VERIFICATION": "mandatory",
    "ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED": True,
    "ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED": True,
    # D3: no mail to an address that has no account; the unknown-account mail builds a link,
    # which raises in headless-only mode.
    "ACCOUNT_EMAIL_UNKNOWN_ACCOUNTS": False,
    "ACCOUNT_PREVENT_ENUMERATION": True,
    # D3: one address per account; the new one is verified by code before it replaces the old.
    "ACCOUNT_CHANGE_EMAIL": True,
    # D3 (correction C1, DM-47): changing, removing or marking an address primary needs a
    # reauthentication by password within the last 300 seconds (allauth's default
    # ACCOUNT_REAUTHENTICATION_TIMEOUT), in the same session; a sign-in does not count.
    "ACCOUNT_REAUTHENTICATION_REQUIRED": True,
    # D8: the account-change notices, for every member (G-04, UST-16).
    "ACCOUNT_EMAIL_NOTIFICATIONS": True,
    # D5 and D6: a password change ends every session, the current one included.
    "ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE": True,
    # D3: off in SV1.
    "ACCOUNT_LOGIN_BY_CODE_ENABLED": False,
    # -- allauth headless (D2, D3) --
    "HEADLESS_ONLY": True,
    "HEADLESS_CLIENTS": ("app",),
    "HEADLESS_SERVE_SPECIFICATION": False,
    "HEADLESS_TOKEN_STRATEGY": "glow_identity.strategy.GlowJWTTokenStrategy",
    "HEADLESS_JWT_ALGORITHM": "RS256",
    "HEADLESS_JWT_ACCESS_TOKEN_EXPIRES_IN": 300,
    "HEADLESS_JWT_REFRESH_TOKEN_EXPIRES_IN": 30 * 24 * 60 * 60,
    "HEADLESS_JWT_STATEFUL_VALIDATION_ENABLED": True,
    "HEADLESS_JWT_ROTATE_REFRESH_TOKEN": True,
    # -- allauth usersessions (D5, D6) --
    "USERSESSIONS_ADAPTER": "glow_identity.sessions.GlowUserSessionsAdapter",
    "USERSESSIONS_TRACK_ACTIVITY": False,
    # -- the one Glow route (D7) --
    "REST_FRAMEWORK": {
        "DEFAULT_AUTHENTICATION_CLASSES": [],
        "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
        "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
        "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
        "UNAUTHENTICATED_USER": None,
        "UNAUTHENTICATED_TOKEN": None,
    },
    # -- Glow's own (D2, D6) --
    # The AccountSession's lifetime from sign-in, an absolute limit (no operation extends it);
    # Nathan decides the members' limit before P11 serves sign-in.
    "GLOW_IDENTITY_SESSION_LIFETIME": timedelta(days=30),
    # The provider name glow_chat's adapter is built with; its session and account operations
    # do not use it. P11 sets the served provider.
    "GLOW_IDENTITY_CHAT_PROVIDER": "fixture",
}


def settings() -> dict[str, Any]:
    """A copy of the fragment, for a settings module's ``globals().update(...)``."""
    copied: dict[str, Any] = {}
    for name, value in SETTINGS.items():
        if isinstance(value, list):
            value = list(value)
        elif isinstance(value, dict):
            value = {k: (list(v) if isinstance(v, list) else v) for k, v in value.items()}
        copied[name] = value
    return copied

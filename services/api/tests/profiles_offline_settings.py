"""Settings for the profile tests that need Django but no database (SV2 Stage A).

SV1's identity fragment (``glow_identity.conf``) with SV2's (``glow_profiles.conf``), the profile
URL configuration and Django's dummy database backend. The ``SECRET_KEY`` and the JWT signing key
are generated for each test process: never committed, printed or logged. The served runtime never
loads this module.
"""

import secrets

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from glow_identity import conf as _identity
from glow_profiles import conf as _profiles

globals().update(_identity.settings())

INSTALLED_APPS = [*_identity.INSTALLED_APPS, *_profiles.INSTALLED_APPS]
ROOT_URLCONF = "tests.profiles_offline_urls"
SECRET_KEY = secrets.token_hex(32)
HEADLESS_JWT_PRIVATE_KEY = (
    rsa.generate_private_key(public_exponent=65537, key_size=2048)
    .private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    .decode("ascii")
)
DATABASES = {"default": {"ENGINE": "django.db.backends.dummy"}}
ALLOWED_HOSTS = ["testserver"]

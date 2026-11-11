"""Settings for the discovery tests that need Django but no database (SV3 Stage A).

SV1's identity fragment, SV2's and SV3's, the discovery URL configuration and Django's dummy
database backend. The ``SECRET_KEY`` and the JWT signing key are generated for each test process:
never committed, printed or logged. No compatibility provider is selected (the runtime's case); a
test selects the fixture adapter for itself. The served runtime never loads this module.
"""

import secrets

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from glow_discovery import conf as _discovery
from glow_identity import conf as _identity
from glow_profiles import conf as _profiles

globals().update(_identity.settings())

INSTALLED_APPS = [*_identity.INSTALLED_APPS, *_profiles.INSTALLED_APPS, *_discovery.INSTALLED_APPS]
ROOT_URLCONF = "tests.discovery_offline_urls"
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

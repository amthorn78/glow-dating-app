"""Settings for the identity tests that need no database (SV1).

The identity fragment (``glow_identity.conf``) with Django's dummy database backend. The
``SECRET_KEY`` and the JWT signing key are generated for each test process, as the SV1 brief's
D2 asks: never committed, printed or logged. The served runtime never loads this module.
"""

import secrets

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from glow_identity import conf as _identity

globals().update(_identity.settings())

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

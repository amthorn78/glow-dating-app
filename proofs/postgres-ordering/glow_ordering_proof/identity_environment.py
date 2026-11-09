"""The identity suite's two keys (the SV1 brief's D2 and D10), read from files.

The identity settings take the JWT signing key and their own ``SECRET_KEY``, both generated for
one run by whoever creates the disposable database: in CI, the credentials step writes them to
the job's protected temporary directory. Each is named by a variable that holds its *path*,
never the key: ``::add-mask::`` takes one line, so a multi-line key in a variable would leave
lines unmasked (DM-45 2.2). The proof's committed ``SECRET_KEY`` placeholder is refused here,
because allauth encrypts the session key into every token's ``sid`` with a key derived from
``SECRET_KEY``, and Django signs each session's password hash with it.

Pure functions over a mapping and the file system, so the offline tests show each refusal. A
refusal names a variable, never a path's contents or a value.
"""

from __future__ import annotations

import os
import stat
from collections.abc import Mapping
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

SECRET_KEY_FILE = "PROOF_IDENTITY_SECRET_KEY_FILE"
JWT_KEY_FILE = "PROOF_IDENTITY_JWT_KEY_FILE"
IDENTITY_NAMES = (SECRET_KEY_FILE, JWT_KEY_FILE)

# The ordering proof's committed placeholder (glow_ordering_proof/settings.py): never a key here.
PLACEHOLDER_SECRET_KEY = "p06-db-proof-placeholder-not-a-secret"
MIN_SECRET_KEY_LENGTH = 50
MIN_RSA_BITS = 2048
MAX_FILE_BYTES = 16_384


class RefusedSecret(Exception):
    """A key file the identity settings refuse to start with."""


def _read_private_file(environ: Mapping[str, str], name: str) -> str:
    if name not in environ:
        raise RefusedSecret(f"{name} is missing; it names a key file generated for this run")
    path = environ[name]
    if not path.startswith("/"):
        raise RefusedSecret(f"{name} must be an absolute path")
    try:
        status = os.stat(path)
    except OSError:
        raise RefusedSecret(f"{name} does not name a readable file") from None
    if not stat.S_ISREG(status.st_mode):
        raise RefusedSecret(f"{name} does not name a regular file")
    if status.st_mode & 0o077:
        raise RefusedSecret(f"{name} must name a file readable only by its owner (mode 0600)")
    if status.st_size == 0 or status.st_size > MAX_FILE_BYTES:
        raise RefusedSecret(f"{name} names a file of the wrong size")
    try:
        return Path(path).read_text(encoding="ascii")
    except (OSError, UnicodeDecodeError):
        raise RefusedSecret(f"{name} does not name a readable ASCII file") from None


def secret_key(environ: Mapping[str, str]) -> str:
    """The identity settings' ``SECRET_KEY``: generated for the run, at least 50 characters,
    never the proof's committed placeholder."""
    value = _read_private_file(environ, SECRET_KEY_FILE).strip()
    if (
        len(value) < MIN_SECRET_KEY_LENGTH
        or len(set(value)) < 5
        or PLACEHOLDER_SECRET_KEY in value
        or value.startswith("django-insecure")
        or any(character.isspace() for character in value)
    ):
        raise RefusedSecret(f"{SECRET_KEY_FILE} does not hold a key generated for this run")
    return value


def jwt_private_key(environ: Mapping[str, str]) -> str:
    """The JWT signing key: an unencrypted PEM RSA private key of at least 2048 bits (RS256,
    allauth's default algorithm)."""
    pem = _read_private_file(environ, JWT_KEY_FILE)
    try:
        key = serialization.load_pem_private_key(pem.encode("ascii"), password=None)
    except (TypeError, ValueError):
        raise RefusedSecret(
            f"{JWT_KEY_FILE} does not hold an unencrypted PEM private key"
        ) from None
    if not isinstance(key, rsa.RSAPrivateKey) or key.key_size < MIN_RSA_BITS:
        raise RefusedSecret(f"{JWT_KEY_FILE} must hold an RSA key of at least {MIN_RSA_BITS} bits")
    return pem


def pem_body_lines(pem: str) -> tuple[str, ...]:
    """The key's base64 lines, for the check that none appears in any output."""
    return tuple(
        line.strip()
        for line in pem.splitlines()
        if line.strip() and not line.startswith("-----") and len(line.strip()) >= 16
    )

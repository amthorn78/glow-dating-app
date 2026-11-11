"""The keyed tie-break (the SV3 brief's D6; DM-60 Q2) and the cursor's binding (D7; Q4).

**The tie-break** orders a batch's candidates within a band by
``salted_hmac(TIE_BREAK_SALT, "<batch>:<profile>", algorithm="sha256")``, under the settings'
``SECRET_KEY``, as ``glow_profiles/idempotency.py`` keys SV2's stored digests. A client knows the
batch's ID (the page names it) and each candidate's profile ID (the card carries it), so an unkeyed
hash would let it compute the order and read band boundaries from where the served order departs
from it; this one cannot be computed without the key. A new batch has a new ID, so the order is
stable within a batch and says nothing between batches.

The selection computes it in SQL, so that one statement orders and bounds the batch (D2): the HMAC's
own construction over PostgreSQL's core ``sha256``, with the key's inner and outer pads computed
here from ``salted_hmac``'s own key derivation (``sql_pads``). The proof pins the statement's value
to ``salted_hmac``'s for the same batch and profiles. The pads are secrets: never logged, printed or
returned; they travel only as statement parameters.

**A cursor** names the batch and an offset, with a MAC over the viewer's account, the collection,
the batch and the offset, keyed the same way with a salt of its own: a cursor the server did not
issue to this viewer, for this collection, is refused (with the generic stale response) before any
row is read. It grants nothing: the page still checks the batch's owner, collection, state, expiry
and versions.
"""

from __future__ import annotations

import hashlib
import re
from uuid import UUID

from django.conf import settings
from django.utils.crypto import constant_time_compare, salted_hmac

TIE_BREAK_SALT = "glow_discovery.tie_break"
CURSOR_SALT = "glow_discovery.cursor"
# A cursor: the batch's 32 hexadecimal digits, the two-digit offset and the 64-digit MAC, joined
# by dots: 100 characters, the contract's bound and pattern (PageRequest.cursor).
CURSOR = re.compile(r"([0-9a-f]{32})\.([0-9]{2})\.([0-9a-f]{64})")
BLOCK = 64


def tie_break(batch_id: UUID, profile_id: UUID) -> bytes:
    """The tie-break key in Python, for the proof's pin and the API's tests."""
    return bytes(
        salted_hmac(TIE_BREAK_SALT, f"{batch_id}:{profile_id}", algorithm="sha256").digest()
    )


def sql_pads() -> tuple[bytes, bytes]:
    """The inner and outer pads of the tie-break's HMAC key: ``salted_hmac``'s key is
    ``sha256(salt + SECRET_KEY)``, padded with zeros to SHA-256's 64-byte block (RFC 2104)."""
    key = hashlib.sha256((TIE_BREAK_SALT + str(settings.SECRET_KEY)).encode("utf-8")).digest()
    key = key.ljust(BLOCK, b"\x00")
    return bytes(b ^ 0x36 for b in key), bytes(b ^ 0x5C for b in key)


def _mac(viewer: UUID, collection: str, batch_id: UUID, offset: int) -> str:
    message = f"{viewer}:{collection}:{batch_id}:{offset:02d}"
    return str(salted_hmac(CURSOR_SALT, message, algorithm="sha256").hexdigest())


def cursor(viewer: UUID, collection: str, batch_id: UUID, offset: int) -> str:
    if not 0 <= offset <= 99:
        raise ValueError("offset out of range")
    return f"{batch_id.hex}.{offset:02d}.{_mac(viewer, collection, batch_id, offset)}"


def read_cursor(value: str, viewer: UUID, collection: str) -> tuple[UUID, int] | None:
    """The batch and offset a cursor names, or ``None`` for one not issued to this viewer for this
    collection (forged, another viewer's or another collection's)."""
    found = CURSOR.fullmatch(value)
    if found is None:
        return None
    batch_id, offset = UUID(hex=found.group(1)), int(found.group(2))
    if not constant_time_compare(found.group(3), _mac(viewer, collection, batch_id, offset)):
        return None
    return batch_id, offset

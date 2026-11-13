"""The cursor's binding (the SV3 brief's D7; DM-60 Q4).

**A cursor** names the batch and an offset, with a MAC over the viewer's account, the collection,
the batch and the offset, ``salted_hmac`` under the settings' ``SECRET_KEY`` with a salt of its own
and SHA-256, as ``glow_profiles/idempotency.py`` keys SV2's stored digests: a cursor the server did
not issue to this viewer, for this collection, is refused (with the generic stale response) before
any batch or other member's row is read. It grants nothing: the page still checks the batch's
owner, collection, state, expiry and versions. The MAC is computed here, in Python, and never
enters a statement.

**The tie-break** has no key (D6; DM-61 K2, replacing DM-60 Q2's keyed hash): the selection draws a
random value for each candidate (``predicates.TIE_BREAK``), so nothing here orders a batch.
"""

from __future__ import annotations

import re
from uuid import UUID

from django.utils.crypto import constant_time_compare, salted_hmac

CURSOR_SALT = "glow_discovery.cursor"
# A cursor: the batch's 32 hexadecimal digits, the two-digit offset and the 64-digit MAC, joined
# by dots: 100 characters, the contract's bound and pattern (PageRequest.cursor).
CURSOR = re.compile(r"([0-9a-f]{32})\.([0-9]{2})\.([0-9a-f]{64})")


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

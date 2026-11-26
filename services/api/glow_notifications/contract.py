"""F12's routes' contract (``gapp-api-v1``; the SV4 brief's D19 and D20, with DM-101's AM6 and AM7),
sealed until integration. No schema changes: ``NotificationSettings``, ``DeviceIntent`` and
``NotificationIntent`` are served as ``main`` has them.

**The requests.** The body is decoded as SV2's, SV3's and chat's routes decode theirs (no
``NaN`` or ``Infinity``; a number with a zero fraction is an integer), and must be a JSON object;
``glow_domain.notifications``'s parsers then take it exactly as the contract has it, the token
becoming a ``ProviderToken`` at once. The requesting installation comes from the
``Glow-Installation-Id`` header (``INSTALLATION_HEADER``), a lower-case UUID, the contract's
``device_id`` pattern, on all three routes: it is the domain's ``Caller.device_id``, never an
intent's field, and a ``DeviceIntent``'s ``device_id`` must equal it (``forbidden``).

**The responses.** ``NotificationSettings`` for the requesting installation: its registration's
version and state (``active`` or ``revoked``) and the account's two settings; never a token, a
reference or an installation identifier. An installation with no registration for the account is
``not_found`` on the read (the contract's ``device_state`` has no ``none``).

**The refusals** (D19, AM6), each the contract's ``Error``, naming a code and never a value:
``REFUSALS`` maps every reason the routes can meet to one code and whether it is retryable. Each
session reason, at SV1's door or inside the locks, is ``unauthenticated``: these routes concern
only the member's own account and installation, so no cause of another member's is at stake. A
deadlock is ``state_conflict``, retryable, and any other database error ``state_conflict``, as
``glow_domain.chat_projections.error_for`` maps them; a reason the table does not hold is
``state_conflict`` too, which the mapping test keeps from happening.

**The installation identifier** works as a capability for a transfer (AM7): a signed-in member who
presents another account's installation revokes that account's registration of it. So it is never
served, logged or shown: no answer carries it, and a refusal is logged by its reason code only.
"""

from __future__ import annotations

import json
import math
from typing import Any

from glow_domain import chat
from glow_domain import notifications as n
from glow_profiles.contract import Invalid

# The contract's error codes (gapp-api-v1's ``Error``) these routes answer.
INVALID_REQUEST = "invalid_request"
UNAUTHENTICATED = "unauthenticated"
FORBIDDEN = "forbidden"
NOT_FOUND = "not_found"
STATE_CONFLICT = "state_conflict"
STALE_VERSION = "stale_version"
IDEMPOTENCY_CONFLICT = "idempotency_conflict"
PROVIDER_UNAVAILABLE = "provider_unavailable"

# The request header naming the requesting installation (D19), as WSGI presents it.
INSTALLATION_HEADER = "HTTP_GLOW_INSTALLATION_ID"

# The ORM adapter's own reasons, beside the domain's (``glow_notifications.persistence``).
# A register's other account (a transfer) changed under the locks (D18), or its row is gone.
TRANSFER_CHANGED = "transfer_changed"
# The device command needs the token store, which only the proof's chat settings name (D16).
NO_TOKEN_STORE = "no_token_store"
# A registration's row missing at its lock: rows are never deleted, so a state that changed.
REGISTRATION_MISSING = "deviceregistration_missing"
# The requesting session's row missing at its lock: the lock's ``<table>_missing`` form.
SESSION_ROW_MISSING = "accountsession_missing"
# The read's explicit absence: no registration of the installation for the account.
REGISTRATION_ABSENT = "registration_absent"

REFUSALS: dict[str, tuple[str, bool]] = {
    # The member's own session and account, at the door or inside the locks: the domain's forms,
    # SV2's lock's and the session lock's ``<table>_missing`` form.
    chat.SESSION_MISSING: (UNAUTHENTICATED, False),
    n.SESSION_NOT_OWNER: (UNAUTHENTICATED, False),
    chat.ACCOUNT_MISSING: (UNAUTHENTICATED, False),
    "account_missing": (UNAUTHENTICATED, False),
    chat.ACCOUNT_NOT_ACTIVE: (UNAUTHENTICATED, False),
    chat.SESSION_NOT_VALID: (UNAUTHENTICATED, False),
    chat.SESSION_EXPIRED: (UNAUTHENTICATED, False),
    chat.SESSION_EPOCH_STALE: (UNAUTHENTICATED, False),
    SESSION_ROW_MISSING: (UNAUTHENTICATED, False),
    # The request: a malformed header or intent; another installation's device_id.
    n.INTENT_INVALID: (INVALID_REQUEST, False),
    n.WRONG_INSTALLATION: (FORBIDDEN, False),
    # CommandMeta: a stale version; another intent under a used key.
    n.STALE_VERSION: (STALE_VERSION, False),
    chat.IDEMPOTENCY_CONFLICT: (IDEMPOTENCY_CONFLICT, False),
    # A transition F12 does not list; the bound (D25); a transfer whose other account changed
    # under the locks; a registration's row gone at its lock; the in-memory fixture's capacity.
    n.TRANSITION_FORBIDDEN: (STATE_CONFLICT, False),
    n.REGISTRATION_NOT_ACTIVE: (STATE_CONFLICT, False),
    n.REGISTRATION_BOUND: (STATE_CONFLICT, False),
    TRANSFER_CHANGED: (STATE_CONFLICT, False),
    REGISTRATION_MISSING: (STATE_CONFLICT, False),
    n.FIXTURE_CAPACITY: (STATE_CONFLICT, False),
    # The token store: its refusal (retryable), or none named (D16; the served runtime's case).
    n.TOKEN_STORE_REFUSED: (PROVIDER_UNAVAILABLE, True),
    NO_TOKEN_STORE: (PROVIDER_UNAVAILABLE, False),
    # The read's explicit absence.
    REGISTRATION_ABSENT: (NOT_FOUND, False),
}


def refusal(outcome: str, reason: str) -> tuple[str, bool]:
    """A refused, failed or absent result as the contract's ``Error`` code and whether it is
    retryable."""
    if outcome == "deadlock":
        return STATE_CONFLICT, True
    if outcome == "error":
        return STATE_CONFLICT, False
    if outcome == "absent":
        return REFUSALS[REGISTRATION_ABSENT]
    return REFUSALS.get(reason, (STATE_CONFLICT, False))


def _reject_constant(name: str) -> Any:
    raise ValueError("a non-finite number is not JSON")


def _number(literal: str) -> Any:
    value = float(literal)
    if math.isfinite(value) and value.is_integer():
        return int(value)
    return value


def parse(body: bytes) -> dict[str, Any]:
    """The body as a JSON object, or ``Invalid``; decoded as SV2's, SV3's and chat's ``parse`` do.
    The intent's own rules are the domain parsers'."""
    try:
        value = json.loads(
            body.decode("utf-8"), parse_constant=_reject_constant, parse_float=_number
        )
    except (UnicodeDecodeError, ValueError, RecursionError):
        raise Invalid("notification intent") from None
    if not isinstance(value, dict):
        raise Invalid("notification intent")
    return value


def settings(view: n.NotificationSettingsView) -> dict[str, Any]:
    """``NotificationSettings``: the requesting installation's registration's version and state and
    the account's settings, from an allowlist of the DTO's keys."""
    return {
        "kind": "notifications",
        "version": int(view.version),
        "match_notifications": bool(view.match_notifications),
        "message_notifications": bool(view.message_notifications),
        "device_state": "active" if view.device_state == "active" else "revoked",
    }

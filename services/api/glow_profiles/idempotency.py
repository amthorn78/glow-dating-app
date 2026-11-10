"""The idempotency records of SV2's commands (the contract's "Pagination, idempotency and stale
state"; the SV2 brief's D17; DM-52 12.1).

Deduplication is by actor, operation and key (``IdempotencyRecord.intent_dedup``), checked after
the command's authorization (P06.DB 5.4: authorize, then deduplicate). The record binds the
command's whole canonical intent, every field but its key, by a **keyed** digest:
``salted_hmac(<a salt naming the operation>, <the canonical intent>, algorithm="sha256")``, 64
hexadecimal characters, under the settings' ``SECRET_KEY`` (the run's generated key in the
proof). An unkeyed digest of a short value (an orientation, a set, a birth date and time) could
be reversed by trying every value; this one cannot be reproduced without the key. The same key
with the same intent replays the receipt, after current authorization, with a current
projection; with another intent it is ``idempotency_conflict``; only a command that committed
gets a record.

**Retention is provisional:** the record's ``expires_at`` is 24 hours after the command. The
contract leaves retention to A05 ("no duration is invented"), but the model requires a value; the
session's report names this one for the manager. An expired record is removed when its key is
reused, and the command is then judged as new, so its expected version decides (no blind replay).
The sensitive-fields consent's withdrawal deletes the records of the commands that carried the
two fields or their sets (D6).
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from django.utils.crypto import salted_hmac

from glow_persistence.models import IdempotencyRecord
from glow_profiles.tx import IDEMPOTENCY_CONFLICT, Refused

RECORD_LIFETIME = timedelta(hours=24)
SALT_PREFIX = "glow_profiles.idempotency."
NEW = "new"
REPLAY = "replay"


def canonical(intent: dict[str, Any]) -> str:
    """The command's whole intent but its key, as one deterministic JSON text."""
    body = dict(intent)
    meta = dict(body.get("meta") or {})
    meta.pop("idempotency_key", None)
    body["meta"] = meta
    return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(operation: str, intent: dict[str, Any]) -> str:
    """D17: the keyed digest of the canonical intent; never an unkeyed hash."""
    keyed = salted_hmac(SALT_PREFIX + operation, canonical(intent), algorithm="sha256")
    return str(keyed.hexdigest())


def decide(actor_id: UUID, operation: str, key: str, request_digest: str, now: datetime) -> Any:
    """``NEW`` or the record to replay, or ``idempotency_conflict``. Runs after the account row
    lock, so two commands of one actor never decide at once."""
    record = (
        IdempotencyRecord.objects.select_for_update()
        .filter(actor_id=actor_id, operation=operation, key=key)
        .first()
    )
    if record is None:
        return NEW
    if record.expires_at <= now:
        record.delete()
        return NEW
    if record.request_digest != request_digest:
        raise Refused(IDEMPOTENCY_CONFLICT, "idempotency_conflict")
    return record


def store(
    actor_id: UUID,
    operation: str,
    key: str,
    request_digest: str,
    *,
    result_ref: UUID,
    result_version: int,
    now: datetime,
) -> None:
    IdempotencyRecord.objects.create(
        actor_id=actor_id,
        operation=operation,
        key=key,
        request_digest=request_digest,
        result_ref=result_ref,
        result_version=result_version,
        outcome_code="committed",
        state="completed",
        expires_at=now + RECORD_LIFETIME,
    )

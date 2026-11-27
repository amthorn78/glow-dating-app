"""The sweeps (SV4 B2; its brief's D24 and D25, with DM-101's AM11 and DM-103's AO1), one sealed
entry point, ``run_sweeps``, which one management command runs (``notification_sweeps``). Sealed
until integration: the served runtime installs no ``glow_notifications`` and so lists no command of
it, and imports none of this; SV5 schedules it. It reaches the token store only through B1's
factory hook (``glow_notifications.providers``) and refuses without it (``provider_unavailable``).
Each step is its own short transactions, bounded per run (``ROWS_PER_STEP``), in D24's order:

1. **Expired sessions** (SV1's limit; F-9): each ``AccountSession`` still ``valid`` past its
   ``expires_at``, found by ``expires_at`` and never through the actor (once allauth purges a
   ``UserSession``, the actor refuses before its expiry check), ordered by ``expires_at`` and id, is
   marked by ``glow_chat``'s ``expire_session`` as it is, through SV1's ``expire_found`` (its D6:
   "marks an expired ``AccountSession`` when it is found"), which writes ``session_expired``, whose
   ``logout`` the deliverer then runs. ``expires_at`` is written only by ``open_session``, so the
   unlocked selection is stable.
2. **Inert registrations** (D23's suspension and deletion, which move only the epoch): each
   ``active`` registration whose session is not current (revoked, expired, past its expiry, at a
   stale epoch, or of an account not ``active``) is revoked as ``logout`` under the device commands'
   locks (``glow_notifications.logout``: the account row, then the registration), judged again on
   the rows as locked, and its token discarded after the commit.
3. **The ledger's retention** (D25): each ledger row whose event was settled (``delivered`` or
   ``dead_letter``) ``LEDGER_RETENTION`` ago is removed, measured from the event's ``updated_at``,
   which its settling save writes last (the application's clock) and nothing changes after. A
   settled event is never delivered again, so a removed row cannot cause a repeat.
4. **The pending discards' retry** (D24 with AO1): the sweep takes a pending discard only once it is
   older than ``DISCARD_AGE``, longer than any command's run, against its ``created_at`` (the
   application's clock, as the ORM writes it), in three steps. **First,** it deletes the row by its
   key in its own committed transaction, which takes no account, session or registration lock, so
   the commands' lock order is never reversed; if that delete removed no row, a save consumed it
   first or another discard took it, and the sweep stops. **Next,** it reads the registrations,
   taking no lock; if one holds the reference (a failed re-read's handle), the sweep stops there
   and discards nothing, so the holder keeps its token and its later retire succeeds. **Last,** it
   calls the store; if the discard fails, it writes the row again under a new key, so no command
   still holding the old key can save that reference. A read of the registrations that fails is
   answered as a failed discard (nothing discarded; the row written again under a new key), and a
   delete that fails leaves its row for the next run. A process stop between the delete and the
   store's answer, or a failed read or discard and a failed rewrite, can leave a token in no row:
   the sweep's custody exception, beside D18's. The sweep writes no non-null ``token_secret_ref``.

Nothing here logs or returns a token, a reference or an installation; the report holds counts only.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import partial
from typing import Any
from uuid import UUID

from django.db import connection, transaction
from django.db.models.functions import Now
from django.utils import timezone

from glow_domain import notifications as n
from glow_identity.revocation import RevocationError, expire_found
from glow_notifications import logout, providers
from glow_notifications.delivery import ProviderUnavailable, run_transaction
from glow_notifications.persistence import discard_after_commit
from glow_persistence.models import (
    AccountSession,
    DeviceRegistration,
    NotificationLedgerEntry,
    PendingTokenDiscard,
)
from glow_profiles.tx import Tx, clock, signal

logger = logging.getLogger("glow_notifications.sweeps")

# The prompt's additions, provisional for SV5: at most this many rows per step per run; and a
# pending discard is taken only once it is older than this, longer than any command's run (the
# served runtime's worker timeout is 10 seconds, the chat lease 30).
ROWS_PER_STEP = 500
DISCARD_AGE = timedelta(minutes=15)
# SV4's D25 (DM-101's AM12): a ledger row is removed this long after its event was settled
# (delivered or dead-lettered). Provisional: A05 owns retention, beside SV2's 24 hours for the
# request keys. A settled event is never delivered again, so a removed row cannot cause a repeat.
LEDGER_RETENTION = timedelta(days=30)

# Step 2's candidates, read with no lock: every active registration whose session is not current.
INERT = (
    "SELECT r.id, r.account_id FROM glow_persistence_deviceregistration r"
    " JOIN glow_persistence_accountsession s ON s.id = r.session_id"
    " JOIN glow_persistence_appaccount a ON a.id = r.account_id"
    " WHERE r.state = %s AND (s.state <> %s OR s.expires_at <= clock_timestamp()"
    " OR s.epoch <> a.session_epoch OR a.state <> %s)"
    " ORDER BY r.id LIMIT %s"
)
SESSION = (
    "SELECT account_id, state, epoch, expires_at FROM glow_persistence_accountsession WHERE id = %s"
)


@dataclass(frozen=True)
class SweepReport:
    """What one run did, as counts only."""

    sessions_marked: int = 0
    sessions_failed: int = 0
    registrations_revoked: int = 0
    registrations_failed: int = 0
    ledger_removed: int = 0
    # The pending discards: taken (the sweep's delete removed the row), gone (it removed none: a
    # save or another discard took it), held (a registration holds the reference: nothing
    # discarded), discarded, rewritten (a failed discard written again under a new key), lost (a
    # failed discard and a failed rewrite: the custody exception).
    discards_taken: int = 0
    discards_gone: int = 0
    discards_held: int = 0
    discarded: int = 0
    rewritten: int = 0
    lost: int = 0
    # A pending discard whose delete failed (left as it was, for the next run).
    discards_failed: int = 0


def run_sweeps() -> SweepReport:
    """D24's sweeps, in order, each bounded per run. Refuses before any statement without the token
    store's factory (``provider_unavailable``), and inside a caller's transaction."""
    tokens = providers.token_store()
    if tokens is None:
        raise ProviderUnavailable()
    if connection.in_atomic_block or not connection.get_autocommit():
        raise RuntimeError("transaction_open")
    marked, marking_failed = _expired_sessions()
    revoked, revoking_failed = _inert_registrations(tokens)
    removed = _retention()
    pending = _pending_discards(tokens)
    return SweepReport(
        sessions_marked=marked,
        sessions_failed=marking_failed,
        registrations_revoked=revoked,
        registrations_failed=revoking_failed,
        ledger_removed=removed,
        **pending,
    )


# -- 1. expired sessions ---------------------------------------------------------------------------


def _expired_sessions() -> tuple[int, int]:
    """Each session still ``valid`` past its ``expires_at``, by ``expires_at`` and id, never through
    the actor, marked by ``expire_session`` (through SV1's ``expire_found``)."""
    found = list(
        AccountSession.objects.filter(state="valid", expires_at__lte=Now())
        .order_by("expires_at", "id")
        .values_list("id", flat=True)[:ROWS_PER_STEP]
    )
    marked = failed = 0
    for session_id in found:
        try:
            expire_found(UUID(str(session_id)))
        except RevocationError as error:
            reason = str(error)
            logger.warning("notification sweep: a session not marked: %s", reason)
            failed += 1
            continue
        marked += 1
    return marked, failed


# -- 2. inert registrations ----------------------------------------------------------------------


def _inert(
    row: logout.Row, account: logout.Account, session: tuple[Any, ...] | None, now: datetime
) -> bool:
    """Whether the registration's session is not current, on the rows as locked."""
    if session is None or account.state != "active":
        return True
    session_account, state, epoch, expires_at = session
    return (
        UUID(str(session_account)) != row.account_id
        or state != "valid"
        or expires_at <= now
        or int(epoch) != account.session_epoch
    )


def _revoke_inert(tx: Tx, registration_id: UUID, account_id: UUID) -> tuple[str, ...]:
    """One inert registration, in its own transaction: its account row first (held in any state),
    then the registration, judged again on the rows as locked, with the time read after them."""
    account = logout.lock_account_held(tx, account_id)
    if account is None:
        return ()
    rows = logout.lock_registrations(tx, [registration_id])
    signal(tx.probe, "after_locks")
    now = clock(tx)
    sessions: dict[UUID, tuple[Any, ...] | None] = {}
    for row in rows:
        tx.cursor.execute(SESSION, [row.session_id])
        found = tx.cursor.fetchone()
        sessions[row.id] = None if found is None else tuple(found)
    return logout.revoke(
        rows,
        lambda row: (
            row.account_id == account_id and _inert(row, account, sessions.get(row.id), now)
        ),
    )


def _inert_registrations(tokens: n.TokenStore) -> tuple[int, int]:
    with connection.cursor() as cursor:
        cursor.execute(INERT, ["active", "valid", "active", ROWS_PER_STEP])
        found = [(UUID(str(row[0])), UUID(str(row[1]))) for row in cursor.fetchall()]
    revoked = failed = 0
    for registration_id, account_id in found:
        outcome, reason, retired = run_transaction(
            partial(_revoke_inert, registration_id=registration_id, account_id=account_id), None
        )
        if outcome != "ok" or retired is None:
            logger.warning("notification sweep: a registration not revoked: %s", reason)
            failed += 1
            continue
        # After the commit: each retired token discarded; a failed discard waits for step 4.
        discard_after_commit(tokens, retired)
        revoked += len(retired)
    return revoked, failed


# -- 3. the ledger's retention (D25) ---------------------------------------------------------------


def _retention() -> int:
    cutoff = timezone.now() - LEDGER_RETENTION
    settled = {"event__state__in": ("delivered", "dead_letter"), "event__updated_at__lte": cutoff}
    ids = list(
        NotificationLedgerEntry.objects.filter(**settled)
        .order_by("event__updated_at", "id")
        .values_list("id", flat=True)[:ROWS_PER_STEP]
    )
    if not ids:
        return 0
    removed, _ = NotificationLedgerEntry.objects.filter(pk__in=ids, **settled).delete()
    return int(removed)


# -- 4. the pending discards' retry (AO1) --------------------------------------------------------


def _again(value: str, counts: dict[str, int]) -> None:
    """The row written again under a new key (a new primary key), so no command still holding the
    old key can save that reference; if that fails too, the reference is held by no row (the
    sweep's custody exception), which one fixed line records, never the reference."""
    try:
        PendingTokenDiscard.objects.create(token_secret_ref=value)
    except Exception:  # noqa: BLE001 - the custody exception; never the reference
        logger.warning("notification sweep: a reference held by no row: its rewrite failed")
        counts["lost"] += 1
        return
    counts["rewritten"] += 1


def _pending_discards(tokens: n.TokenStore) -> dict[str, int]:
    cutoff = timezone.now() - DISCARD_AGE
    found = list(
        PendingTokenDiscard.objects.filter(created_at__lte=cutoff)
        .order_by("created_at", "id")
        .values_list("id", "token_secret_ref")[:ROWS_PER_STEP]
    )
    counts = dict.fromkeys(
        (
            "discards_taken",
            "discards_gone",
            "discards_held",
            "discarded",
            "rewritten",
            "lost",
            "discards_failed",
        ),
        0,
    )
    for key, value in found:
        # First: the row deleted by its key, in its own committed transaction, which takes no
        # account, session or registration lock. A failed delete leaves the row as it was.
        try:
            with transaction.atomic(durable=True):
                deleted, _ = PendingTokenDiscard.objects.filter(pk=key).delete()
        except Exception:  # noqa: BLE001 - a result by type only; the row stays for the next run
            logger.warning("notification sweep: a pending discard not taken: its delete failed")
            counts["discards_failed"] += 1
            continue
        if deleted != 1:
            # A save consumed it first, or another discard took it: stop.
            counts["discards_gone"] += 1
            continue
        counts["discards_taken"] += 1
        # Next: the registrations, read with no lock. A holder keeps its token. A failed read
        # cannot tell, so nothing is discarded and the row is written again, as for a failed
        # discard: the next run takes it afresh.
        try:
            held = DeviceRegistration.objects.filter(token_secret_ref=value).exists()
        except Exception:  # noqa: BLE001 - a result by type only; never the reference
            _again(str(value), counts)
            continue
        if held:
            counts["discards_held"] += 1
            continue
        # Last: the store; a failed discard written again under a new key.
        try:
            tokens.discard(n.TokenReference(str(value)))
        except Exception:  # noqa: BLE001 - whatever the store raised is a failed discard
            _again(str(value), counts)
            continue
        counts["discarded"] += 1
    return counts

"""F12's ``logout`` by the system (SV4 B2; its brief's D23 and D24, with DM-101's AM11), which the
notification deliverer runs for a session's end and the sweep for an inert registration. Sealed
until integration: it runs only under the disposable-database proof's chat settings, and the served
runtime imports none of it.

**The locks** are the device commands' (``glow_notifications.persistence``), in their order: the
registration's account row ``FOR NO KEY UPDATE`` first (SV2's ``lock_account``, the account
writer's lock since SV3's C1), held whatever the account's state, then the registrations it may
change by primary key, ``FOR UPDATE``, in key order, in one statement
(``REGISTRATIONS_FOR_UPDATE``).
B1's transfer reads its holder again under both accounts' locks and locks the holder's registration
only after, which is safe only because every writer of ``DeviceRegistration`` locks its account
first; these writers keep that rule (B1's record, "Limits and deviations"). No session row is
locked: the session has ended, and no writer locks a session and then an account.

**The revocation** (``revoke``): each registration still ``active`` and still the one its caller
names (made or last rotated by the ending session, or still inert) becomes ``revoked``,
``ended_by`` ``logout``, its version advanced and its reference cleared, and the reference moves to
a pending discard in the same transaction (``persistence.hold_for_discard``); after the commit the
caller discards each through the token store (``persistence.discard_after_commit``), and a failed
discard waits for the sweep. A registration already revoked, or rotated since by another session,
is no change. Nothing here writes a non-null ``token_secret_ref``, logs or returns a token or a
reference, or names an installation.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from uuid import UUID

from django.utils import timezone

from glow_domain import chat
from glow_notifications.persistence import hold_for_discard
from glow_persistence.models import AppAccount, DeviceRegistration
from glow_profiles.tx import Refused, Tx, lock_account

# The registrations a logout may change, by primary key, in key order, in one statement, with the
# session that made or last rotated each.
REGISTRATIONS_FOR_UPDATE = (
    "SELECT id, account_id, session_id, state, version, token_secret_ref"
    " FROM glow_persistence_deviceregistration WHERE id = ANY(%s) ORDER BY id FOR UPDATE"
)


@dataclass(frozen=True)
class Account:
    """The account row as locked: its state and its session epoch."""

    state: str
    session_epoch: int


@dataclass(frozen=True)
class Row:
    """A registration's row as locked. The reference is held only to move it to a pending
    discard; it is never logged or returned."""

    id: UUID
    account_id: UUID
    session_id: UUID
    state: str
    version: int
    token_secret_ref: str | None


def lock_account_held(tx: Tx, account_id: UUID) -> Account | None:
    """The account row ``FOR NO KEY UPDATE`` through SV2's ``lock_account``, first, held in any
    state: its lock is taken before ``lock_account`` judges it, as B1's transfer holds the other
    account's. ``None`` once the row is gone (its registrations went with it)."""
    try:
        lock_account(tx, account_id)
    except Refused as refused:
        if refused.reason != chat.ACCOUNT_NOT_ACTIVE:
            return None
    found = AppAccount.objects.filter(pk=account_id).values_list("state", "session_epoch").first()
    return None if found is None else Account(str(found[0]), int(found[1]))


def session_registrations(session_id: UUID) -> list[UUID]:
    """The ``active`` registrations the session made or last rotated, read under its account's
    lock, which every writer of a registration takes first."""
    return [
        UUID(str(value))
        for value in DeviceRegistration.objects.filter(
            session_id=session_id, state="active"
        ).values_list("id", flat=True)
    ]


def lock_registrations(tx: Tx, ids: Iterable[UUID]) -> list[Row]:
    """The registrations by primary key, ``FOR UPDATE``, in key order, after the account's lock."""
    wanted = sorted(set(ids))
    if not wanted:
        return []
    tx.cursor.execute(REGISTRATIONS_FOR_UPDATE, [wanted])
    return [Row(*row) for row in tx.cursor.fetchall()]


def revoke(rows: Iterable[Row], still: Callable[[Row], bool]) -> tuple[str, ...]:
    """Inside the transaction that holds the locks: each row still ``active`` for which ``still``
    holds, on the row as locked, revoked as ``logout``, and its reference held for its discard.
    Returns the retired references, for the caller to discard after the commit."""
    retired: list[str] = []
    stamp = timezone.now()
    for row in rows:
        if row.state != "active" or not still(row):
            continue
        assert row.token_secret_ref is not None
        DeviceRegistration.objects.filter(pk=row.id).update(
            state="revoked",
            version=row.version + 1,
            token_secret_ref=None,
            ended_by="logout",
            updated_at=stamp,
        )
        retired.append(row.token_secret_ref)
    hold_for_discard(retired)
    return tuple(retired)

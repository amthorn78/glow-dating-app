"""The notification deliverer (SV4 B2; its brief's D21 to D23, D25 and D26, with DM-101's AM8 to
AM11), sealed until integration: one at a time, in process, under the disposable-database proof's
chat settings only; the served runtime imports none of it, and SV5 composes the worker and its
schedule. It reaches the push transport and the token store only through B1's factory hooks
(``glow_notifications.providers``), which only the proof's chat settings name; without either it
refuses before any statement (``provider_unavailable``).

It takes exactly four event types, in delivery order (``available_at``, then the database's
``sequence``): its own two in ``glow-notifications-1``, ``notify_match`` (written by SV3's like) and
``notify_message`` (written by chat's delivery receipt), and chat's ``session_revoked`` and
``session_expired`` in ``glow-chat-1``, whose one consumer it is (D23; AM11). Chat's deliverer takes
neither of the first two: it reads only chat's delivered types.

**A notification** (D22), on the chat deliverer's pattern (lease, call, receipt):

1. **Lease and check,** in one transaction: the event locked by its key (``FOR UPDATE``) and, when
   due, leased with one more attempt; then the send's checks, on facts read under share locks, in
   this order: both accounts, the match (and, for a message, its submission), the profiles, the
   consents and the block rows, then the recipient's settings and registrations (and those
   registrations' sessions), with the time read after the locks. The checks are the composer's
   (``send_refusal``: the recipient rule, the match ``active`` with no block either way, both
   accounts ``active``, both profiles ``visible``, both latest onboarding consents ``accepted``),
   then the recipient's setting for the kind, then an active device. ``Match`` records no completer,
   so the facts give the composer's ``completed_by`` as the participant who is not the event's
   recipient: the recipient rule rests on the like's writer (AM8). On the first delivery the
   recipient's active devices then are fixed as ledger rows (``NotificationLedgerEntry``,
   ``pending``; at most B1's bound of 10, D25). A refusal settles the event with no push.
2. **Call,** outside any transaction, as soon as the lease commits: one push per fixed device not
   yet recorded and still active, through the transport's port, naming the device by its reference
   (never its token), with the ledger key (the event with the installation, P06.3) as the
   idempotency key, and P06.3's content (``push_content``): the title ``Glow``, one fixed sentence
   per kind, the kind and a fixed route; no identifier, name, text or count.
3. **Receipt,** in a second transaction: the event locked again and, if the lease is still this
   one, each accepted send (or ``repeat``) recorded ``sent``; the event is ``delivered`` when every
   fixed device is recorded or was no longer active at this attempt's check. A failed call is
   retried with backoff (``BACKOFF``, doubled for each further attempt), then dead-lettered after
   ``MAX_ATTEMPTS``. Unlike chat's, a retried event's ``available_at`` moves by its backoff, so it
   holds no later event: notification events are independent, and a logout must not wait behind a
   push (AM9).

**The window** (AM10), a recorded limit: whatever the check reads, changed after it and before the
transport accepts, does not stop that push: a block or an unmatch, either account's suspension or
deletion, a pause, a restriction, a withdrawn consent, a setting turned off, or the registration
revoked or transferred or its session ended. Its content says nothing about the other member, and
the window is the same for a block and an unmatch (D26). It is kept short: each attempt runs its own
check, no call follows an earlier attempt's check, and the calls start as soon as the lease's
transaction commits. P11B's transport resolves a reference only when it calls (PV05).

**A session's end** (D23): F12's ``logout`` (``glow_notifications.logout``). The event is leased
as a notification's is; then one transaction takes the device commands' locks (the session's
account row ``FOR NO KEY UPDATE``, held whatever the account's state, then that session's
``active`` registrations ``FOR UPDATE``), revokes each (``ended_by`` ``logout``), moves its
reference to a pending discard and settles the event; after the commit each token is discarded. A
registration already revoked, or rotated since by another session, is no change.

Every transaction refuses a caller's (``transaction_open``); a deadlock or any other database error
is a result by type only, and nothing is retried inside a delivery. Nothing here logs or returns a
token, a reference, an installation identifier or any member's value: a ``Delivery`` names the
event, its type, its outcome, its attempts, a reason code and counts. A ``DeliveryProbe`` may
observe the deliverer at its hold points; each only signals and waits.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Literal
from uuid import UUID

from django.db import IntegrityError, connection, transaction
from django.db.models import F, Q
from django.db.models.functions import Now
from django.utils import timezone

from glow_domain import chat
from glow_domain import notifications as n
from glow_domain.chat import ONBOARDING_CONSENT_PURPOSE, TransactionProbe
from glow_domain.chat import TransactionTrace as Trace
from glow_notifications import logout, providers
from glow_notifications.persistence import discard_after_commit
from glow_persistence.models import AccountSession, NotificationLedgerEntry, OutboxEvent
from glow_profiles.tx import Tx, caller_transaction_open, clock, signal

logger = logging.getLogger("glow_notifications.delivery")

# The prompt's additions, provisional for SV5: chat's attempts and lease (pinned equal to
# ``glow_chat.delivery``'s by a test), and a backoff of 30 seconds, doubled for each further
# attempt.
MAX_ATTEMPTS = 5
LEASE = timedelta(seconds=30)
BACKOFF = timedelta(seconds=30)

DEADLOCK_DETECTED = "40P01"
TRANSACTION_OPEN = "transaction_open"
PROVIDER_UNAVAILABLE = "provider_unavailable"

# The four types, each in its own schema (D22, D23; AM11), and no other.
TYPES: frozenset[tuple[str, str]] = frozenset(
    {(n.NOTIFICATIONS_SCHEMA_VERSION, kind) for kind in n.EVENT_KINDS}
    | {(n.CHAT_SCHEMA_VERSION, ending) for ending in n.SESSION_ENDINGS}
)
SELECTED = Q(
    schema_version=n.NOTIFICATIONS_SCHEMA_VERSION, event_type__in=tuple(n.EVENT_KINDS)
) | Q(schema_version=n.CHAT_SCHEMA_VERSION, event_type__in=n.SESSION_ENDINGS)

# The event, locked by its key (the lease's and the receipt's first lock).
EVENT_FOR_UPDATE = (
    "SELECT id, schema_version, event_type, aggregate_id, payload_ref, state, attempts,"
    " available_at, lease_expires_at FROM glow_persistence_outboxevent WHERE id = %s FOR UPDATE"
)
# Identifiers, read before the facts' locks, which never change: a message's match (its
# binding's), and a match's pair.
SUBMISSION_MATCH = (
    "SELECT b.match_id FROM glow_persistence_messagesubmission s"
    " JOIN glow_persistence_chatbinding b ON b.id = s.binding_id WHERE s.id = %s"
)
MATCH_PAIR = "SELECT account_low_id, account_high_id FROM glow_persistence_match WHERE id = %s"
# The facts, each read under a share lock, in the check's order (D22).
ACCOUNT_SHARED = (
    "SELECT state, session_epoch FROM glow_persistence_appaccount WHERE id = %s FOR SHARE"
)
MATCH_SHARED = (
    "SELECT state, account_low_id, account_high_id FROM glow_persistence_match"
    " WHERE id = %s FOR SHARE"
)
SUBMISSION_SHARED = (
    "SELECT actor_id, state FROM glow_persistence_messagesubmission WHERE id = %s FOR SHARE"
)
PROFILES_SHARED = (
    "SELECT account_id, state FROM glow_persistence_profile"
    " WHERE account_id = ANY(%s) ORDER BY id FOR SHARE"
)
CONSENT_SHARED = (
    "SELECT state FROM glow_persistence_consentdecision WHERE account_id = %s AND purpose = %s"
    " ORDER BY version DESC LIMIT 1 FOR SHARE"
)
BLOCKS_SHARED = (
    "SELECT state FROM glow_persistence_block"
    " WHERE (actor_id = %s AND target_id = %s) OR (actor_id = %s AND target_id = %s)"
    " ORDER BY id FOR SHARE"
)
SETTINGS_SHARED = (
    "SELECT match_notifications, message_notifications FROM glow_persistence_notificationsettings"
    " WHERE account_id = %s FOR SHARE"
)
REGISTRATIONS_SHARED = (
    "SELECT id, installation_id, state, token_secret_ref, session_id"
    " FROM glow_persistence_deviceregistration WHERE account_id = %s ORDER BY id FOR SHARE"
)
SESSIONS_SHARED = (
    "SELECT id, account_id, state, epoch, expires_at FROM glow_persistence_accountsession"
    " WHERE id = ANY(%s) ORDER BY id FOR SHARE"
)

DeliveryOutcome = Literal["delivered", "refused", "retry", "dead_letter", "lost_lease", "error"]


class ProviderUnavailable(RuntimeError):
    """No push transport or token store is named (the served runtime's case): a refusal before
    any statement. The message is a fixed code."""

    def __init__(self) -> None:
        super().__init__(PROVIDER_UNAVAILABLE)


@dataclass(frozen=True)
class Delivery:
    """What one delivery did: the event, its type, its outcome, its attempts, a reason code (never
    a value), the pushes the transport accepted now (or answered ``repeat`` for), and the
    registrations a logout revoked."""

    event_id: UUID
    event_type: str
    outcome: DeliveryOutcome
    attempts: int
    code: str = ""
    sent: int = 0
    revoked: int = 0


@dataclass(frozen=True)
class DeliveryProbe:
    """Hold points a caller may observe the deliverer at; each only signals and waits (DM-13 2.1).
    ``lease``: the lease's transaction; ``after_lease``: after it commits, before any call;
    ``settle``: the receipt's or the logout's transaction."""

    lease: TransactionProbe | None = None
    after_lease: Callable[[], None] | None = None
    settle: TransactionProbe | None = None


@dataclass(frozen=True)
class _Event:
    """The event's row as locked."""

    id: UUID
    schema_version: str
    event_type: str
    aggregate_id: UUID
    payload_ref: UUID
    state: str
    attempts: int
    available_at: datetime
    lease_expires_at: datetime | None


@dataclass(frozen=True)
class _Push:
    """One push the lease allows: its ledger row, its installation and its device's reference,
    handed to the transport only."""

    ledger_id: UUID
    installation_id: UUID
    reference: str


@dataclass(frozen=True)
class _Lease:
    event_id: UUID
    event_type: str
    attempts: int
    kind: n.NotificationKind | None = None
    pushes: tuple[_Push, ...] = ()
    session_id: UUID | None = None
    # Set when the lease's transaction settled the event itself (a refusal, or nothing to send).
    settled: Delivery | None = None


@dataclass(frozen=True)
class _Facts:
    """``DeliveryFacts`` over the rows the lease read under its locks."""

    match_id: UUID
    match_facts: n.MatchFacts | None
    submission_id: UUID | None
    message_facts: n.MessageFacts | None
    members: Mapping[UUID, n.MemberFacts]

    def match(self, match_id: UUID) -> n.MatchFacts | None:
        return self.match_facts if match_id == self.match_id else None

    def message(self, submission_id: UUID) -> n.MessageFacts | None:
        return self.message_facts if submission_id == self.submission_id else None

    def member(self, account_id: UUID) -> n.MemberFacts | None:
        return self.members.get(account_id)


def run_transaction[T](
    body: Callable[[Tx], T], probe: TransactionProbe | None
) -> tuple[str, str, T | None]:
    """One transaction: ``("ok", "", value)``, or a failure and its reason (never a value). A
    deadlock or any other database error is a result by type only; nothing is retried. It refuses
    a caller's transaction (``transaction_open``) before any statement."""
    try:
        # Inside the ``try``: reading autocommit may open the connection.
        if caller_transaction_open():
            return "error", TRANSACTION_OPEN, None
        with transaction.atomic(durable=True):
            cursor = connection.cursor()
            # The transaction's first statement: its backend and its start.
            cursor.execute("SELECT pg_backend_pid(), now()")
            pid, started = cursor.fetchone()
            if probe is not None and probe.on_begin is not None:
                probe.on_begin(int(pid))
            value = body(Tx(cursor, Trace(int(pid), started), probe))
            signal(probe, "before_commit")
    except Exception as exc:  # noqa: BLE001 - a result the caller judges; never retried
        cause = exc.__cause__
        # The driver's DeadlockDetected, by its SQLSTATE: the API installs no driver.
        if getattr(cause, "sqlstate", None) == DEADLOCK_DETECTED:
            return "deadlock", "DeadlockDetected", None
        if isinstance(exc, IntegrityError):
            return "error", f"IntegrityError:{type(cause).__name__}", None
        return "error", type(exc).__name__, None
    return "ok", "", value


def _one(tx: Tx, statement: str, args: list[Any]) -> tuple[Any, ...] | None:
    tx.cursor.execute(statement, args)
    row = tx.cursor.fetchone()
    return None if row is None else tuple(row)


def _all(tx: Tx, statement: str, args: list[Any]) -> list[tuple[Any, ...]]:
    tx.cursor.execute(statement, args)
    return [tuple(row) for row in tx.cursor.fetchall()]


def _lock_event(tx: Tx, event_id: UUID) -> _Event | None:
    """The event's row, by its key, ``FOR UPDATE``."""
    row = _one(tx, EVENT_FOR_UPDATE, [event_id])
    if row is None:
        return None
    return _Event(
        UUID(str(row[0])),
        str(row[1]),
        str(row[2]),
        UUID(str(row[3])),
        UUID(str(row[4])),
        str(row[5]),
        int(row[6]),
        row[7],
        row[8],
    )


def _write(event: _Event, **changes: Any) -> None:
    """Inside the event's transaction, under its lock: the changes, the version advanced, and
    ``updated_at`` from the application's clock, which the retention measures a settled event
    from (D25)."""
    OutboxEvent.objects.filter(pk=event.id).update(
        **changes, version=F("version") + 1, updated_at=timezone.now()
    )


def _delivered(event: _Event, now: datetime) -> None:
    """Settled, ``delivered``, its lease cleared."""
    _write(event, state="delivered", delivered_at=now, lease_expires_at=None)


def backoff(attempts: int) -> timedelta:
    """The wait before the next attempt after ``attempts`` failed: ``BACKOFF``, doubled for each
    further attempt."""
    factor: int = 2 ** max(0, attempts - 1)
    return BACKOFF * factor


def _again(event: _Event, now: datetime, reason: str, *, sent: int = 0) -> Delivery:
    """Inside the event's transaction: released for a retry after its backoff, its
    ``available_at`` moved (AM9), or dead-lettered after ``MAX_ATTEMPTS``."""
    if event.attempts < MAX_ATTEMPTS:
        _write(
            event,
            state="pending",
            lease_expires_at=None,
            available_at=now + backoff(event.attempts),
        )
        return Delivery(event.id, event.event_type, "retry", event.attempts, reason, sent=sent)
    _write(event, state="dead_letter", lease_expires_at=None)
    return Delivery(event.id, event.event_type, "dead_letter", event.attempts, reason, sent=sent)


class NotificationDelivery:
    """The notification outbox's one deliverer, one at a time (D22, D23)."""

    def __init__(self) -> None:
        transport = providers.push_transport()
        tokens = providers.token_store()
        if transport is None or tokens is None:
            raise ProviderUnavailable()
        self._transport = transport
        self._tokens = tokens

    def __repr__(self) -> str:
        return "NotificationDelivery(<sealed>)"

    # -- which events, in which order --------------------------------------------------------

    @staticmethod
    def _due_ids(count: int) -> list[UUID]:
        """The first ``count`` due events of the four types, in delivery order: pending, or leased
        with its lease run out, and available now."""
        ids = (
            OutboxEvent.objects.filter(SELECTED)
            .filter(Q(state="pending") | Q(state="leased", lease_expires_at__lte=Now()))
            .filter(available_at__lte=Now())
            .order_by("available_at", "sequence")
            .values_list("id", flat=True)[:count]
        )
        return [UUID(str(value)) for value in ids]

    def deliver_next(self, probe: DeliveryProbe | None = None) -> Delivery | None:
        """Deliver the head of the notification outbox, or return ``None`` when none is due."""
        head = self._due_ids(1)
        return self._deliver(head[0], probe or DeliveryProbe()) if head else None

    def deliver_due(self, *, limit: int, batch: int = 100) -> list[Delivery]:
        """Deliver due events in order until none is due or ``limit`` is reached. A retried event
        has moved by its backoff, so it is not due again in the same pass and holds no later one;
        a database error stops the pass."""
        done: list[Delivery] = []
        while len(done) < limit:
            progressed = False
            for event_id in self._due_ids(min(batch, limit - len(done))):
                delivery = self._deliver(event_id, DeliveryProbe())
                if delivery is None:
                    continue
                done.append(delivery)
                progressed = True
                if delivery.outcome == "error":
                    return done
            if not progressed:
                break
        return done

    # -- one event -----------------------------------------------------------------------------

    def _deliver(self, event_id: UUID, probe: DeliveryProbe) -> Delivery | None:
        outcome, reason, lease = run_transaction(lambda tx: self._lease(tx, event_id), probe.lease)
        if outcome != "ok":
            logger.warning("notification delivery: the lease failed: %s", reason)
            return Delivery(event_id, "", "error", 0, reason)
        if lease is None:
            return None
        if probe.after_lease is not None:
            probe.after_lease()
        if lease.settled is not None:
            return lease.settled
        if lease.session_id is not None:
            return self._logout(lease, probe.settle)
        return self._call_and_receipt(lease, probe.settle)

    def _lease(self, tx: Tx, event_id: UUID) -> _Lease | None:
        """The lease's transaction: the event locked by its key and, when due, leased with one
        more attempt; for a notification, the checks and, on its first delivery, the fixed
        devices."""
        event = _lock_event(tx, event_id)
        if event is None or event.state not in ("pending", "leased"):
            return None
        if (event.schema_version, event.event_type) not in TYPES:
            return None
        now = clock(tx)
        if event.available_at > now:
            return None
        if event.state == "leased" and event.lease_expires_at is not None:
            if event.lease_expires_at > now:
                return None  # held by a live lease
        attempts = event.attempts + 1
        _write(event, state="leased", lease_expires_at=now + LEASE, attempts=attempts)
        if event.event_type in n.SESSION_ENDINGS:
            return _Lease(event.id, event.event_type, attempts, session_id=event.payload_ref)
        return self._check(tx, event, attempts, n.EVENT_KINDS[event.event_type])

    def _check(self, tx: Tx, event: _Event, attempts: int, kind: n.NotificationKind) -> _Lease:
        """D22's checks on facts read under share locks, in the check's order, then the setting
        and the devices; a refusal settles the event with no push."""
        recipient = event.payload_ref
        submission_id: UUID | None = None
        match_id: UUID | None = event.aggregate_id
        if kind == "message":
            submission_id = event.aggregate_id
            found = _one(tx, SUBMISSION_MATCH, [submission_id])
            match_id = None if found is None else UUID(str(found[0]))
        if match_id is None:
            return self._refused(tx, event, attempts, n.MESSAGE_MISSING)
        pair = _one(tx, MATCH_PAIR, [match_id])
        if pair is None:
            return self._refused(tx, event, attempts, chat.MATCH_MISSING)
        trigger: n.Trigger = (
            n.MatchActivated(event.id, match_id, recipient)
            if submission_id is None
            else n.MessageAccepted(event.id, match_id, submission_id, recipient)
        )
        low_id, high_id = UUID(str(pair[0])), UUID(str(pair[1]))
        # The locks, in the check's order: both accounts (the lower first), the match (and its
        # message), the profiles, the consents and the block rows, then the recipient's settings,
        # registrations and their sessions.
        accounts = {
            account_id: _one(tx, ACCOUNT_SHARED, [account_id]) for account_id in (low_id, high_id)
        }
        matched = _one(tx, MATCH_SHARED, [match_id])
        submission = None if submission_id is None else _one(tx, SUBMISSION_SHARED, [submission_id])
        profiles = {
            UUID(str(row[0])): str(row[1]) for row in _all(tx, PROFILES_SHARED, [[low_id, high_id]])
        }
        consents: dict[UUID, str | None] = {}
        for account_id in (low_id, high_id):
            latest = _one(tx, CONSENT_SHARED, [account_id, ONBOARDING_CONSENT_PURPOSE])
            consents[account_id] = None if latest is None else str(latest[0])
        blocks = _all(tx, BLOCKS_SHARED, [low_id, high_id, high_id, low_id])
        chosen = _one(tx, SETTINGS_SHARED, [recipient])
        registrations = _all(tx, REGISTRATIONS_SHARED, [recipient])
        active = [row for row in registrations if row[2] == "active" and row[3] is not None]
        session_ids = sorted({UUID(str(row[4])) for row in active})
        sessions = {UUID(str(row[0])): row for row in _all(tx, SESSIONS_SHARED, [session_ids])}
        signal(tx.probe, "after_locks")
        now = clock(tx)

        facts = _Facts(match_id, None, submission_id, None, {})
        if matched is not None:
            participants = (UUID(str(matched[1])), UUID(str(matched[2])))
            facts = _Facts(
                match_id,
                n.MatchFacts(
                    str(matched[0]),
                    participants,
                    # AM8: Match records no completer, so the participant who is not the recipient.
                    participants[1] if recipient == participants[0] else participants[0],
                    any(row[0] == "active" for row in blocks),
                ),
                submission_id,
                None
                if submission is None
                # Its match is its binding's, read with the event's identifiers above.
                else n.MessageFacts(match_id, UUID(str(submission[0])), str(submission[1])),
                {
                    account_id: n.MemberFacts(
                        str(found[0]),
                        profiles.get(account_id),
                        consents[account_id],
                    )
                    for account_id, found in accounts.items()
                    if found is not None
                },
            )
        refusal = n.send_refusal(trigger, facts)
        if refusal:
            return self._refused(tx, event, attempts, refusal)
        if chosen is None or not bool(chosen[0] if kind == "match" else chosen[1]):
            return self._refused(tx, event, attempts, n.SETTING_OFF)

        own = accounts.get(recipient)

        def current(row: tuple[Any, ...]) -> bool:
            """The composer's rule: a registration whose session is the recipient's current one
            (valid, unexpired, at the account's epoch, of an ``active`` account)."""
            session = sessions.get(UUID(str(row[4])))
            return (
                session is not None
                and own is not None
                and own[0] == "active"
                and UUID(str(session[1])) == recipient
                and session[2] == "valid"
                and session[4] > now
                and int(session[3]) == int(own[1])
            )

        devices = {UUID(str(row[1])): str(row[3]) for row in active if current(row)}
        fixed = list(
            NotificationLedgerEntry.objects.filter(event_id=event.id).values_list(
                "id", "installation_id", "state"
            )
        )
        if not fixed:
            # The first delivery: the recipient's active devices now are fixed (D25).
            if not devices:
                return self._refused(tx, event, attempts, n.NO_ACTIVE_DEVICE)
            NotificationLedgerEntry.objects.bulk_create(
                [
                    NotificationLedgerEntry(event_id=event.id, installation_id=installation)
                    for installation in sorted(devices)
                ]
            )
            fixed = list(
                NotificationLedgerEntry.objects.filter(event_id=event.id).values_list(
                    "id", "installation_id", "state"
                )
            )
        pending = sorted(
            (UUID(str(row[0])), UUID(str(row[1]))) for row in fixed if row[2] == "pending"
        )
        if not pending:
            return self._settled(event, attempts, now, "delivered", n.ALREADY_DELIVERED)
        pushes = tuple(
            _Push(ledger_id, installation, devices[installation])
            for ledger_id, installation in sorted(pending, key=lambda item: str(item[1]))
            if installation in devices
        )
        if not pushes:
            # Every fixed device left is no longer active.
            return self._settled(event, attempts, now, "delivered", n.NO_ACTIVE_DEVICE)
        return _Lease(event.id, event.event_type, attempts, kind=kind, pushes=pushes)

    def _refused(self, tx: Tx, event: _Event, attempts: int, reason: str) -> _Lease:
        logger.debug("notification delivery refused: %s", reason)
        return self._settled(event, attempts, clock(tx), "refused", reason)

    @staticmethod
    def _settled(
        event: _Event, attempts: int, now: datetime, outcome: DeliveryOutcome, reason: str
    ) -> _Lease:
        """Inside the lease's transaction: the event settled with no push."""
        _delivered(event, now)
        done = Delivery(event.id, event.event_type, outcome, attempts, reason)
        return _Lease(event.id, event.event_type, attempts, settled=done)

    # -- a notification's call and receipt ---------------------------------------------------

    def _call_and_receipt(self, lease: _Lease, probe: TransactionProbe | None) -> Delivery:
        assert lease.kind is not None
        content = n.push_content(lease.kind)
        recorded: list[UUID] = []
        failed = 0
        for push in lease.pushes:
            request = n.PushRequest(
                n.TokenReference(push.reference),
                n.ledger_key(lease.event_id, push.installation_id),
                content,
            )
            try:
                answer = self._transport.send(request)
            except Exception:  # noqa: BLE001 - whatever the transport raises is a failed call
                failed += 1
                continue
            if answer in ("accepted", "repeat"):
                recorded.append(push.ledger_id)
            else:
                failed += 1
        outcome, reason, done = run_transaction(
            lambda tx: self._receipt(tx, lease, recorded, failed), probe
        )
        if outcome != "ok" or done is None:
            logger.warning("notification delivery: the receipt failed: %s", reason)
            return Delivery(lease.event_id, lease.event_type, "error", lease.attempts, reason)
        return done

    @staticmethod
    def _receipt(tx: Tx, lease: _Lease, recorded: list[UUID], failed: int) -> Delivery:
        """The receipt's transaction: the event locked again; if the lease is still this one,
        each accepted send recorded, and the event delivered, retried or dead-lettered."""
        event = _lock_event(tx, lease.event_id)
        if event is None or event.state != "leased" or event.attempts != lease.attempts:
            return Delivery(lease.event_id, lease.event_type, "lost_lease", lease.attempts)
        now = clock(tx)
        if recorded:
            NotificationLedgerEntry.objects.filter(pk__in=recorded, state="pending").update(
                state="sent", version=F("version") + 1, updated_at=timezone.now()
            )
        if failed:
            return _again(event, now, n.TRANSPORT_UNAVAILABLE, sent=len(recorded))
        _delivered(event, now)
        return Delivery(event.id, event.event_type, "delivered", event.attempts, sent=len(recorded))

    # -- a session's end: F12's logout (D23) -------------------------------------------------

    def _logout(self, lease: _Lease, probe: TransactionProbe | None) -> Delivery:
        session_id = lease.session_id
        assert session_id is not None
        retired: list[str] = []

        def body(tx: Tx) -> Delivery:
            event = _lock_event(tx, lease.event_id)
            if event is None or event.state != "leased" or event.attempts != lease.attempts:
                return Delivery(lease.event_id, lease.event_type, "lost_lease", lease.attempts)
            # An identifier, read before the locks: a session's account never changes.
            account_id = (
                AccountSession.objects.filter(pk=session_id)
                .values_list("account_id", flat=True)
                .first()
            )
            if account_id is not None and (
                logout.lock_account_held(tx, UUID(str(account_id))) is not None
            ):
                rows = logout.lock_registrations(tx, logout.session_registrations(session_id))
                signal(tx.probe, "after_locks")
                retired[:] = logout.revoke(rows, lambda row: row.session_id == session_id)
            _delivered(event, clock(tx))
            return Delivery(
                event.id, event.event_type, "delivered", event.attempts, revoked=len(retired)
            )

        outcome, reason, done = run_transaction(body, probe)
        if outcome != "ok" or done is None:
            logger.warning("notification logout failed: %s", reason)
            return self._release(lease, reason)
        if done.outcome == "delivered":
            # After the commit: each retired token discarded; a failed discard waits for the sweep.
            discard_after_commit(self._tokens, retired)
        return done

    @staticmethod
    def _release(lease: _Lease, reason: str) -> Delivery:
        """A logout whose transaction failed: in a transaction of its own, the lease released for
        a retry after its backoff, or the event dead-lettered after ``MAX_ATTEMPTS``."""

        def body(tx: Tx) -> Delivery:
            event = _lock_event(tx, lease.event_id)
            if event is None or event.state != "leased" or event.attempts != lease.attempts:
                return Delivery(lease.event_id, lease.event_type, "lost_lease", lease.attempts)
            return _again(event, clock(tx), reason)

        outcome, failure, done = run_transaction(body, None)
        if outcome != "ok" or done is None:
            return Delivery(lease.event_id, lease.event_type, "error", lease.attempts, failure)
        return done

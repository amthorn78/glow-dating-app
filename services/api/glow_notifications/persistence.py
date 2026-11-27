"""The ORM adapter behind ``glow_domain.notifications.NotificationPersistence`` (SV4 B1; its brief's
D18, with DM-101's AM3 to AM5): F12's devices and settings over ``glow_persistence``'s models. It
runs only under the disposable-database proof's chat settings; the served runtime imports none of
it. It carries P06.DB's protocol (its brief, D5), as ``glow_chat``'s adapter does:

- **One transaction** for each command and each read, at READ COMMITTED (the connection's
  isolation level), never inside a transaction its caller holds (``transaction_open``); rows are
  locked by primary key; every check runs in code on the rows as locked, with the database's clock
  read after the locks; a locked read that finds no row is a refusal; a deadlock or any other
  database error is a result, by type only, and nothing is retried.
- **The locks** (AM3). A device or settings command locks the account row ``FOR NO KEY UPDATE``
  (SV2's ``lock_account``, the account writer's lock since SV3's C1), then the requesting
  session's row ``FOR SHARE``, as chat's send and reads lock theirs, so the command and its
  session's end (``glow_chat``'s sign-out and expiry lock that row ``FOR UPDATE``) are ordered and
  no command commits for a session whose end committed first; then the registrations it changes,
  by primary key, ``FOR UPDATE``. A register that takes an installation from another account (a
  transfer) locks both accounts, the lower first, after reading the other account's identifier with
  no lock, and refuses (``transfer_changed``) if the installation's active registration changed
  under the locks. The settings read takes the account and session rows ``FOR SHARE``, so it reads
  one committed state of the settings and the registration. Every check is read under the locks:
  the session's state, expiry and epoch, the account's state, the registration's state and version.
- **Idempotency** (AM5): SV2's ``IdempotencyRecord`` through SV2's keyed digest
  (``glow_profiles.idempotency``: ``salted_hmac`` under ``SECRET_KEY``), over the canonical
  intent, the token included, and the requesting installation from the header, so a replay with
  another token, or the same body under the same key from another installation, is
  ``idempotency_conflict``; the token itself is never stored. Deduplication follows the session's
  checks (P06.DB 5.4: authorize, then deduplicate). The record is written here, with F12's receipt
  code (``register``, ``rotate``, ``revoke`` or ``settings``), as SV3's interactions write theirs;
  its lifetime is SV2's provisional 24 hours.
- **Custody** (AM4; B1-C1, DM-102's AN1). The token store's ``put`` runs before the command's
  transaction, never inside it, so no external call holds a lock. **Its handle comes first:**
  before the transaction, the new reference's pending discard (``PendingTokenDiscard``) is written
  in its own statement, and only if no registration and no pending discard already holds that
  reference; a reference already held is the store's refusal (``token_store_refused``) and is not
  discarded, and if the write fails the store discards the reference at once and the command
  answers its error. The transaction that saves the reference on a registration deletes its
  pending discard, and refuses (``state_conflict``) unless it deletes exactly that one row. A
  command whose outcome is known and did not save the reference (a refusal, a deadlock, a replay,
  or a failure raised before the transaction's body returned) discards it at once, as a retired
  one is; one whose outcome is unknown (a failure after the body returned, at the commit) leaves
  the handle to SV4 B2's sweep (``_run`` tells the two apart). So every reference the store holds
  has a registration or a pending discard, except after a process stop, or a failed write and a
  failed discard, between the ``put`` and the handle. A reference the command retires (a
  rotation's old one, a revocation's, a transfer's) moves from the registration's row to a pending
  discard in the command's own transaction; after the commit the store discards it and its pending
  row is removed, and a failed discard leaves the row waiting for the sweep. A reference is held
  only by an active registration's row, a pending discard's row and (SV4 B2) the push request
  handed to the transport; no read, log line, answer, exception or receipt holds a token or a
  reference.
- **The bound** (D25): an account holds at most ``MAX_ACTIVE_REGISTRATIONS`` active
  registrations, counted under its account lock; a registration beyond them is refused
  (``registration_bound``); a rotation adds none.
- **Versions** are P06.3's: a registration's ``version`` is the installation's view revision, and
  a settings change advances every registration of the account in the same transaction.

The refusals are reason codes (``glow_notifications.contract`` maps each to the contract's code).
There is no switch: no test-only branch, flag or hook that changes a lock, a check or a write. A
``TransactionProbe`` may observe a command at its hold points; it only signals and waits.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal
from uuid import UUID, uuid4

from django.db import IntegrityError, connection, transaction
from django.db.models import F
from django.utils import timezone

from glow_domain import chat
from glow_domain import notifications as n
from glow_domain.chat import TransactionProbe
from glow_domain.chat import TransactionTrace as Trace
from glow_notifications.contract import (
    NO_TOKEN_STORE,
    REGISTRATION_MISSING,
    SESSION_ROW_MISSING,
    TRANSFER_CHANGED,
)
from glow_persistence.models import (
    AppAccount,
    DeviceRegistration,
    IdempotencyRecord,
    NotificationSettings,
    PendingTokenDiscard,
)
from glow_profiles import idempotency
from glow_profiles.tx import (
    Refused,
    Tx,
    caller_transaction_open,
    clock,
    lock_account,
    read_account_shared,
    signal,
)

logger = logging.getLogger("glow_notifications.persistence")

DEADLOCK_DETECTED = "40P01"
TRANSACTION_OPEN = "transaction_open"

DEVICE_OPERATION = "notifications.device"
SETTINGS_OPERATION = "notifications.settings"
# AM5: the requesting installation, from the header, bound into the digest beside the intent. No
# intent of the contract has a field of this name.
INSTALLATION_FIELD = "glow_installation_id"

# The requesting session's row, FOR SHARE (AM3): after the account's lock, before the
# registrations'.
SESSION_SHARED = (
    "SELECT account_id, state, expires_at, epoch FROM glow_persistence_accountsession"
    " WHERE id = %s FOR SHARE"
)
# The registrations a command changes, by primary key, in key order, in one statement.
REGISTRATIONS_FOR_UPDATE = (
    "SELECT id, account_id, installation_id, state, version, token_secret_ref"
    " FROM glow_persistence_deviceregistration WHERE id = ANY(%s) ORDER BY id FOR UPDATE"
)

# B1-C1 (DM-102's AN1): the new reference's handle, its pending discard, written in one statement
# before the command's transaction (autocommit), and only if no registration and no pending
# discard holds the reference: no row is returned when one does (the registration's ``NOT EXISTS``,
# or the pending discards' uniqueness, ``ON CONFLICT``), and a failed write raises.
HANDLE_WRITE = (
    "INSERT INTO glow_persistence_pendingtokendiscard"
    " (id, created_at, updated_at, version, token_secret_ref)"
    " SELECT %s, %s, %s, 1, %s WHERE NOT EXISTS ("
    "SELECT 1 FROM glow_persistence_deviceregistration WHERE token_secret_ref = %s)"
    " ON CONFLICT (token_secret_ref) DO NOTHING RETURNING id"
)

Failure = Literal["refused", "deadlock", "error"]


class _Refused(Exception):
    """A refusal inside a command or a read: an internal reason code, never a value."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class _Rollback(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass(frozen=True)
class _Row:
    """A registration's row as locked."""

    id: UUID
    account_id: UUID
    installation_id: UUID
    state: str
    version: int
    token_secret_ref: str | None


@dataclass(frozen=True)
class _Done:
    """What a transaction's body leaves: its result, the references it retired (discarded after
    the commit) and whether it saved the command's new reference."""

    result: n.CommandResult | n.ReadResult
    retired: tuple[str, ...] = ()
    saved: bool = False


def _digest(operation: str, intent: Mapping[str, Any], caller: n.Caller) -> str:
    """AM5: SV2's keyed digest of the canonical intent, the token included, and of the requesting
    installation from the header."""
    return idempotency.digest(operation, {**intent, INSTALLATION_FIELD: str(caller.device_id)})


def _holder(installation_id: UUID, account_id: UUID) -> tuple[UUID, UUID] | None:
    """The registration, of another account, that holds the installation active: its ID and its
    account's."""
    found = (
        DeviceRegistration.objects.filter(installation_id=installation_id, state="active")
        .exclude(account_id=account_id)
        .values_list("id", "account_id")
        .first()
    )
    return None if found is None else (UUID(str(found[0])), UUID(str(found[1])))


def _own(caller: n.Caller) -> UUID | None:
    """The account's registration of the requesting installation, if any: its ID."""
    found = (
        DeviceRegistration.objects.filter(
            account_id=caller.account_id, installation_id=caller.device_id
        )
        .values_list("id", flat=True)
        .first()
    )
    return None if found is None else UUID(str(found))


def _view(caller: n.Caller) -> n.NotificationSettingsView | None:
    """F12's private projection for the requesting installation: its registration's version and
    state, and the account's settings (both off until changed). Never a token or a reference."""
    registration = (
        DeviceRegistration.objects.filter(
            account_id=caller.account_id, installation_id=caller.device_id
        )
        .values_list("version", "state")
        .first()
    )
    if registration is None:
        return None
    chosen = (
        NotificationSettings.objects.filter(account_id=caller.account_id)
        .values_list("match_notifications", "message_notifications")
        .first()
    )
    match, message = chosen if chosen is not None else (False, False)
    state: n.RegistrationState = "active" if registration[1] == "active" else "revoked"
    return n.NotificationSettingsView(int(registration[0]), bool(match), bool(message), state)


class OrmNotificationPersistence:
    """``NotificationPersistence`` over ``glow_persistence``'s models. ``tokens`` is the token store
    the factory hook gives (``glow_notifications.providers``); only the device command needs it."""

    def __init__(self, *, tokens: n.TokenStore | None = None) -> None:
        self._tokens = tokens

    def __repr__(self) -> str:
        return "OrmNotificationPersistence(<sealed>)"

    # -- transaction plumbing --------------------------------------------------------------

    @staticmethod
    def _run(
        body: Callable[[Tx], _Done], probe: TransactionProbe | None
    ) -> tuple[str, str, Any, bool]:
        """One transaction: ``("ok", "", done, True)``, or a failure, its reason (never a value) and
        whether its outcome is known. A refusal rolls back; a deadlock or any other database error
        is a result by type only.

        **The split** (B1-C1; DM-102's AN1) falls where the body returns. A failure raised before
        it returned (a refusal, a deadlock, any database error inside the body, the one-active-row
        constraint's ``IntegrityError`` included, or one at the transaction's start) rolled the
        transaction back: its outcome is known. One raised after it returned, as the block exits
        (at the commit, or at the ``before_commit`` hold point before it), is unknown: the commit
        may have taken effect. The answer served is the same either way."""
        returned = False
        try:
            with transaction.atomic(durable=True):
                cursor = connection.cursor()
                # The transaction's first statement: its backend and its start.
                cursor.execute("SELECT pg_backend_pid(), now()")
                pid, started = cursor.fetchone()
                if probe is not None and probe.on_begin is not None:
                    probe.on_begin(int(pid))
                tx = Tx(cursor, Trace(int(pid), started), probe)
                try:
                    done = body(tx)
                except _Refused as refused:
                    raise _Rollback(refused.reason) from None
                returned = True
                signal(probe, "before_commit")
        except _Rollback as rollback:
            return "refused", rollback.reason, None, True
        except Exception as exc:  # noqa: BLE001 - a result the caller judges; never retried
            known = not returned
            cause = exc.__cause__
            # The driver's DeadlockDetected, by its SQLSTATE: the API installs no driver.
            if getattr(cause, "sqlstate", None) == DEADLOCK_DETECTED:
                return "deadlock", "DeadlockDetected", None, known
            if isinstance(exc, IntegrityError):
                return "error", f"IntegrityError:{type(cause).__name__}", None, known
            return "error", type(exc).__name__, None, known
        return "ok", "", done, True

    @staticmethod
    def _failed(outcome: str, reason: str) -> n.CommandResult:
        failure: Failure = "deadlock" if outcome == "deadlock" else "error"
        return n.CommandResult("refused" if outcome == "refused" else failure, reason)

    # -- the locks -------------------------------------------------------------------------

    @staticmethod
    def _lock_own_account(tx: Tx, account_id: UUID) -> Any:
        """The member's account row, ``FOR NO KEY UPDATE`` (SV2's ``lock_account``), first; it must
        be ``active``."""
        try:
            return lock_account(tx, account_id)
        except Refused as refused:
            raise _Refused(refused.reason) from None

    @staticmethod
    def _lock_other_account(tx: Tx, account_id: UUID) -> None:
        """A transfer's other account row, ``FOR NO KEY UPDATE``, in any state (SV3's
        ``_lock_pair``: its lock is taken before ``lock_account`` judges it). A row gone is the
        other account changed under the locks."""
        try:
            lock_account(tx, account_id)
        except Refused as refused:
            if refused.reason != chat.ACCOUNT_NOT_ACTIVE:
                raise _Refused(TRANSFER_CHANGED) from None

    @staticmethod
    def _lock_session(tx: Tx, caller: n.Caller) -> tuple[Any, ...]:
        """The requesting session's row, ``FOR SHARE`` (AM3)."""
        tx.cursor.execute(SESSION_SHARED, [caller.session_id])
        row = tx.cursor.fetchone()
        if row is None:
            raise _Refused(SESSION_ROW_MISSING)
        return tuple(row)

    @staticmethod
    def _check_session(
        caller: n.Caller, epoch: int, session: tuple[Any, ...], now: datetime
    ) -> None:
        """The domain's session rule, on the rows as locked: the session is the account's, valid,
        unexpired and at the account's epoch (the account's ``active`` state is checked at its
        lock)."""
        account_id, state, expires_at, session_epoch = session
        if account_id != caller.account_id:
            raise _Refused(n.SESSION_NOT_OWNER)
        if state != "valid":
            raise _Refused(chat.SESSION_NOT_VALID)
        if expires_at <= now:
            raise _Refused(chat.SESSION_EXPIRED)
        if session_epoch != epoch:
            raise _Refused(chat.SESSION_EPOCH_STALE)

    @staticmethod
    def _lock_registrations(tx: Tx, ids: Iterable[UUID | None]) -> dict[UUID, _Row]:
        """The registrations a command changes, by primary key, ``FOR UPDATE``, in key order."""
        wanted = sorted({row_id for row_id in ids if row_id is not None})
        if not wanted:
            return {}
        tx.cursor.execute(REGISTRATIONS_FOR_UPDATE, [wanted])
        found = {row[0]: _Row(*row) for row in tx.cursor.fetchall()}
        if set(found) != set(wanted):
            raise _Refused(REGISTRATION_MISSING)
        return found

    # -- idempotency ---------------------------------------------------------------------

    @staticmethod
    def _decide(caller: n.Caller, operation: str, key: str, digest: str, now: datetime) -> Any:
        """SV2's decision, after the session's checks: ``None`` for a new command, else the record
        to replay; another intent under the key is ``idempotency_conflict``."""
        try:
            found = idempotency.decide(caller.account_id, operation, key, digest, now)
        except Refused as refused:
            raise _Refused(refused.reason) from None
        return None if isinstance(found, str) else found

    @staticmethod
    def _store(
        caller: n.Caller,
        operation: str,
        key: str,
        digest: str,
        *,
        outcome_code: str,
        result_ref: UUID,
        result_version: int,
        now: datetime,
    ) -> n.Receipt:
        """The committed command's record (SV2's, with F12's receipt code, as SV3's ``_store``)."""
        IdempotencyRecord.objects.create(
            actor_id=caller.account_id,
            operation=operation,
            key=key,
            request_digest=digest,
            result_ref=result_ref,
            result_version=result_version,
            outcome_code=outcome_code,
            state="completed",
            expires_at=now + idempotency.RECORD_LIFETIME,
        )
        return n.Receipt(digest, outcome_code, caller.device_id, result_version)

    @staticmethod
    def _replayed(caller: n.Caller, record: Any) -> _Done:
        receipt = n.Receipt(
            str(record.request_digest),
            str(record.outcome_code),
            caller.device_id,
            int(record.result_version),
        )
        return _Done(n.CommandResult("replayed", receipt=receipt, settings=_view(caller)))

    # -- custody ---------------------------------------------------------------------------

    @staticmethod
    def _hold_for_discard(references: Iterable[str]) -> None:
        """Inside the command's transaction: each retired reference moves to a pending discard."""
        PendingTokenDiscard.objects.bulk_create(
            [PendingTokenDiscard(token_secret_ref=value) for value in references]
        )

    @staticmethod
    def _write_handle(reference: n.TokenReference) -> UUID | None:
        """B1-C1 (DM-102's AN1): before the command's transaction, in its own statement, the new
        reference's pending discard, its handle: its ID, or ``None`` when a registration or a
        pending discard already holds the reference (``HANDLE_WRITE``); raises when the write fails,
        nothing written. Alone, the statement tells the two apart: no row returned is a reference
        held, an error a failed write."""
        stamp = timezone.now()
        with connection.cursor() as cursor:
            cursor.execute(HANDLE_WRITE, [uuid4(), stamp, stamp, reference.value, reference.value])
            row = cursor.fetchone()
        return None if row is None else UUID(str(row[0]))

    @staticmethod
    def _held_since(reference: n.TokenReference, handle: UUID) -> bool:
        """Under concurrency, the handle's statement can miss a holder: its ``NOT EXISTS`` reads
        the statement's snapshot, so a save of the same reference that deletes that reference's
        handle and commits while the statement waits on the pending discards' uniqueness leaves
        a registration the statement does not see. So the registrations are read again, in a new
        snapshot, once the handle is written; if one holds the reference now, the handle's row is
        removed by its key and the reference is the store's refusal. A save must delete the
        reference's one pending discard (``_consume_handle``), so no holder can appear after this
        read. Raises if the read fails; the row is then left for SV4 B2's sweep, which takes none
        a registration holds (D24)."""
        if DeviceRegistration.objects.filter(token_secret_ref=reference.value).exists():
            PendingTokenDiscard.objects.filter(pk=handle).delete()
            return True
        return False

    @staticmethod
    def _consume_handle(handle: UUID | None, fresh: n.TokenReference) -> None:
        """Inside the transaction that saves the new reference, under the command's locks, after
        the registrations': its handle's row deleted, and a refusal unless exactly that one row
        was (B1-C1; DM-102's AN1), so a save and SV4 B2's sweep, which removes a pending discard
        before it calls the store (D24), cannot both win."""
        deleted, _ = PendingTokenDiscard.objects.filter(
            pk=handle, token_secret_ref=fresh.value
        ).delete()
        if deleted != 1:
            raise _Refused(n.TOKEN_HANDLE_MISSING)

    def _discard_unwritten(self, reference: n.TokenReference) -> None:
        """The handle's write failed, so no row holds the reference: the store discards it at
        once. If that fails too, the token is held by no row (the custody limit, AN1)."""
        try:
            assert self._tokens is not None
            self._tokens.discard(reference)
        except Exception:  # noqa: BLE001 - recorded by a fixed line; the reference is never logged
            logger.warning("notification token reference held by no row: its discard failed")

    def _discard(self, references: Iterable[str]) -> None:
        """After the commit: each retired reference discarded through the store, and its pending
        row removed; a failed discard leaves the row waiting for SV4 B2's sweep."""
        for value in references:
            try:
                assert self._tokens is not None
                self._tokens.discard(n.TokenReference(value))
            except Exception:  # noqa: BLE001 - kept for the sweep, whatever the store raised
                logger.warning("notification token discard failed; kept for retry")
                continue
            try:
                PendingTokenDiscard.objects.filter(token_secret_ref=value).delete()
            except Exception:  # noqa: BLE001 - the row waits; a second discard changes nothing
                logger.warning("notification pending discard not removed: error")

    # -- F12: the owner's read ---------------------------------------------------------------

    def read(self, caller: n.Caller, *, probe: TransactionProbe | None = None) -> n.ReadResult:
        """The owner's own settings for the requesting installation (D19), under the account and
        session rows' share locks; an installation with no registration for the account is an
        explicit absence."""
        if caller_transaction_open():
            return n.ReadResult("error", TRANSACTION_OPEN)

        def body(tx: Tx) -> _Done:
            try:
                read_account_shared(tx, caller.account_id)
            except Refused as refused:
                raise _Refused(refused.reason) from None
            epoch = (
                AppAccount.objects.filter(pk=caller.account_id)
                .values_list("session_epoch", flat=True)
                .first()
            )
            session = self._lock_session(tx, caller)
            signal(tx.probe, "after_locks")
            now = clock(tx)
            self._check_session(caller, int(epoch or 0), session, now)
            view = _view(caller)
            return _Done(
                n.ReadResult("absent") if view is None else n.ReadResult("read", settings=view)
            )

        outcome, reason, done, _known = self._run(body, probe)
        if done is not None:
            assert isinstance(done.result, n.ReadResult)
            return done.result
        failure: Failure = "deadlock" if outcome == "deadlock" else "error"
        return n.ReadResult("refused" if outcome == "refused" else failure, reason)

    # -- F12: register, rotate and revoke --------------------------------------------------

    def device(
        self, caller: n.Caller, intent: object, *, probe: TransactionProbe | None = None
    ) -> n.CommandResult:
        """A ``DeviceIntent`` for the requesting installation: ``register`` (F12's register, or
        its rotate for an installation already active for the account) or ``revoke``."""
        if self._tokens is None:
            return n.CommandResult("refused", NO_TOKEN_STORE)
        if caller_transaction_open():
            return n.CommandResult("error", TRANSACTION_OPEN)
        try:
            command = n.parse_device_intent(intent)
        except n.IntentError:
            return n.CommandResult("refused", n.INTENT_INVALID)
        if command.device_id != caller.device_id:
            return n.CommandResult("refused", n.WRONG_INSTALLATION)
        assert isinstance(intent, Mapping)
        digest = _digest(DEVICE_OPERATION, intent, caller)
        fresh: n.TokenReference | None = None
        handle: UUID | None = None
        if command.action == "register":
            assert command.token is not None
            # AM4: the store takes the token before the command's transaction, never inside it.
            try:
                fresh = self._tokens.put(command.token)
            except Exception:  # noqa: BLE001 - whatever the store raises is its refusal
                return n.CommandResult("refused", n.TOKEN_STORE_REFUSED)
            if not isinstance(fresh, n.TokenReference):
                return n.CommandResult("refused", n.TOKEN_STORE_REFUSED)
            # B1-C1 (DM-102's AN1): the reference's handle, before the transaction.
            try:
                handle = self._write_handle(fresh)
            except Exception as exc:  # noqa: BLE001 - a result, by type only; never retried
                self._discard_unwritten(fresh)
                return n.CommandResult("error", type(exc).__name__)
            try:
                held = handle is None or self._held_since(fresh, handle)
            except Exception as exc:  # noqa: BLE001 - the handle waits for SV4 B2's sweep
                return n.CommandResult("error", type(exc).__name__)
            if held:
                # Another holder's reference (the store broke its port, AN11): never discarded.
                return n.CommandResult("refused", n.TOKEN_STORE_REFUSED)
        outcome, reason, done, known = self._run(
            lambda tx: self._device(tx, caller, command, digest, fresh, handle), probe
        )
        if fresh is not None and (done is None or not done.saved):
            # Not saved (AN1): a known outcome discards the reference at once, as a retired one
            # is; an unknown one (a failure at the commit) leaves its handle to SV4 B2's sweep.
            if known:
                self._discard([fresh.value])
        if done is None:
            return self._failed(outcome, reason)
        self._discard(done.retired)
        assert isinstance(done.result, n.CommandResult)
        return done.result

    def _device(
        self,
        tx: Tx,
        caller: n.Caller,
        command: n.DeviceCommand,
        digest: str,
        fresh: n.TokenReference | None,
        handle: UUID | None,
    ) -> _Done:
        # Before the locks, identifiers only: the other account that holds the installation
        # active, for a register (a transfer).
        seen = (
            _holder(command.device_id, caller.account_id) if command.action == "register" else None
        )
        other = None if seen is None else seen[1]
        accounts = {caller.account_id} if other is None else {caller.account_id, other}
        account: Any = None
        for account_id in sorted(accounts):  # the lower first
            if account_id == caller.account_id:
                account = self._lock_own_account(tx, account_id)
            else:
                self._lock_other_account(tx, account_id)
        session = self._lock_session(tx, caller)
        now = clock(tx)
        self._check_session(caller, int(account.session_epoch), session, now)
        key = command.meta.idempotency_key
        record = self._decide(caller, DEVICE_OPERATION, key, digest, now)
        if record is not None:
            return self._replayed(caller, record)
        holder = (
            _holder(command.device_id, caller.account_id) if command.action == "register" else None
        )
        # D18: the other account that holds the installation active, read again under the locks;
        # any change since it was read with no lock (another holder, or none, or one where none
        # was) is a refusal, never a transfer from an account this command did not lock.
        if (None if holder is None else holder[1]) != other:
            raise _Refused(TRANSFER_CHANGED)
        own = _own(caller)
        rows = self._lock_registrations(tx, [own, None if holder is None else holder[0]])
        signal(tx.probe, "after_locks")
        current = rows.get(own) if own is not None else None
        if command.meta.expected_version != (0 if current is None else current.version):
            raise _Refused(n.STALE_VERSION)
        if command.action == "revoke":
            return self._revoke(caller, command, digest, current, now)
        assert fresh is not None
        held = None if holder is None else rows[holder[0]]
        return self._register(caller, command, digest, current, held, fresh, handle, now)

    def _revoke(
        self,
        caller: n.Caller,
        command: n.DeviceCommand,
        digest: str,
        current: _Row | None,
        now: datetime,
    ) -> _Done:
        if current is None or current.state != "active":
            # F12 lists revoke from active only; every unlisted transition is refused.
            raise _Refused(n.TRANSITION_FORBIDDEN)
        assert current.token_secret_ref is not None
        version = current.version + 1
        DeviceRegistration.objects.filter(pk=current.id).update(
            state="revoked",
            version=version,
            token_secret_ref=None,
            ended_by="revoke",
            updated_at=timezone.now(),
        )
        retired = (current.token_secret_ref,)
        self._hold_for_discard(retired)
        receipt = self._store(
            caller,
            DEVICE_OPERATION,
            command.meta.idempotency_key,
            digest,
            outcome_code="revoke",
            result_ref=current.id,
            result_version=version,
            now=now,
        )
        result = n.CommandResult(
            "applied", receipt=receipt, settings=_view(caller), transition="revoke"
        )
        return _Done(result, retired=retired)

    def _register(
        self,
        caller: n.Caller,
        command: n.DeviceCommand,
        digest: str,
        current: _Row | None,
        held: _Row | None,
        fresh: n.TokenReference,
        handle: UUID | None,
        now: datetime,
    ) -> _Done:
        transition = "rotate" if current is not None and current.state == "active" else "register"
        if transition == "register":
            active = DeviceRegistration.objects.filter(
                account_id=caller.account_id, state="active"
            ).count()
            if active >= n.MAX_ACTIVE_REGISTRATIONS:
                # D25: a registration beyond the bound; a rotation adds none.
                raise _Refused(n.REGISTRATION_BOUND)
        retired: list[str] = []
        stamp = timezone.now()
        if held is not None:
            # The transfer (F12; data model): the earlier account's registration of the
            # installation is revoked first, in the same unit of work, its token discarded.
            if held.state != "active" or held.installation_id != command.device_id:
                raise _Refused(TRANSFER_CHANGED)
            assert held.token_secret_ref is not None
            DeviceRegistration.objects.filter(pk=held.id).update(
                state="revoked",
                version=held.version + 1,
                token_secret_ref=None,
                ended_by="transfer",
                updated_at=stamp,
            )
            retired.append(held.token_secret_ref)
        # B1-C1 (DM-102's AN1): the save consumes the new reference's handle, or refuses.
        self._consume_handle(handle, fresh)
        if current is None:
            created = DeviceRegistration.objects.create(
                account_id=caller.account_id,
                installation_id=command.device_id,
                session_id=caller.session_id,
                state="active",
                version=1,
                token_secret_ref=fresh.value,
            )
            registration_id, version = UUID(str(created.pk)), 1
        else:
            if transition == "rotate":
                assert current.token_secret_ref is not None
                retired.append(current.token_secret_ref)
            version = current.version + 1
            DeviceRegistration.objects.filter(pk=current.id).update(
                state="active",
                version=version,
                session_id=caller.session_id,
                token_secret_ref=fresh.value,
                ended_by=None,
                updated_at=stamp,
            )
            registration_id = current.id
        self._hold_for_discard(retired)
        receipt = self._store(
            caller,
            DEVICE_OPERATION,
            command.meta.idempotency_key,
            digest,
            outcome_code=transition,
            result_ref=registration_id,
            result_version=version,
            now=now,
        )
        result = n.CommandResult(
            "applied", receipt=receipt, settings=_view(caller), transition=transition
        )
        return _Done(result, retired=tuple(retired), saved=True)

    # -- F12: settings -----------------------------------------------------------------------

    def settings(
        self, caller: n.Caller, intent: object, *, probe: TransactionProbe | None = None
    ) -> n.CommandResult:
        """A ``NotificationIntent``: the account's settings, from an installation whose
        registration is ``active``; every registration of the account advances (P06.3's
        versions)."""
        if caller_transaction_open():
            return n.CommandResult("error", TRANSACTION_OPEN)
        try:
            command = n.parse_settings_intent(intent)
        except n.IntentError:
            return n.CommandResult("refused", n.INTENT_INVALID)
        assert isinstance(intent, Mapping)
        digest = _digest(SETTINGS_OPERATION, intent, caller)

        def body(tx: Tx) -> _Done:
            account = self._lock_own_account(tx, caller.account_id)
            session = self._lock_session(tx, caller)
            now = clock(tx)
            self._check_session(caller, int(account.session_epoch), session, now)
            key = command.meta.idempotency_key
            record = self._decide(caller, SETTINGS_OPERATION, key, digest, now)
            if record is not None:
                return self._replayed(caller, record)
            ids = DeviceRegistration.objects.filter(account_id=caller.account_id).values_list(
                "id", flat=True
            )
            rows = self._lock_registrations(tx, [UUID(str(row_id)) for row_id in ids])
            signal(tx.probe, "after_locks")
            current = next(
                (row for row in rows.values() if row.installation_id == caller.device_id), None
            )
            if current is None or current.state != "active":
                # F12 lists settings from active only.
                raise _Refused(n.REGISTRATION_NOT_ACTIVE)
            if command.meta.expected_version != current.version:
                raise _Refused(n.STALE_VERSION)
            stamp = timezone.now()
            # Every installation's view of the account's settings advances together.
            DeviceRegistration.objects.filter(pk__in=list(rows)).update(
                version=F("version") + 1, updated_at=stamp
            )
            chosen = (
                NotificationSettings.objects.filter(account_id=caller.account_id)
                .values_list("id", "version")
                .first()
            )
            if chosen is None:
                NotificationSettings.objects.create(
                    account_id=caller.account_id,
                    match_notifications=command.match_notifications,
                    message_notifications=command.message_notifications,
                    version=1,
                )
            else:
                NotificationSettings.objects.filter(pk=chosen[0]).update(
                    match_notifications=command.match_notifications,
                    message_notifications=command.message_notifications,
                    version=int(chosen[1]) + 1,
                    updated_at=stamp,
                )
            receipt = self._store(
                caller,
                SETTINGS_OPERATION,
                key,
                digest,
                outcome_code="settings",
                result_ref=current.id,
                result_version=current.version + 1,
                now=now,
            )
            return _Done(n.CommandResult("applied", receipt=receipt, settings=_view(caller)))

        outcome, reason, done, _known = self._run(body, probe)
        if done is None:
            return self._failed(outcome, reason)
        assert isinstance(done.result, n.CommandResult)
        return done.result

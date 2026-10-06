"""The persistence adapter behind ``glow_domain.chat.ContactPersistence`` (P06.2 Stage A).

It carries P06.DB's reference design (its brief, D5) into the app, as written:

- every writer runs in one ``transaction.atomic()`` at READ COMMITTED (the connection's
  isolation level) and locks rows by primary key with ``SELECT ... FOR UPDATE`` in one
  canonical order: the lower account, the higher account, the match, then the sending
  session's ``AccountSession`` row (5.3; sign-out and expiry lock that row, 5.1);
- every check runs in code on the rows as locked, and every value a check uses is read
  after the locks, inside the same transaction (5.5); a locked read that finds no row
  is a refusal, never "absent, so create";
- the time the checks use is ``clock_timestamp()`` read after the locks (5.2);
- the send authorizes first and deduplicates second (5.4), and writes its
  ``MessageSubmission`` and ``OutboxEvent`` in the same transaction;
- deletion is the lifecycle transition, never a hard row delete (5.6).

P06.2's D5 adds three revocations, each joining the same protocol (DM-13 4.1): a
paused or restricted profile and a withdrawn onboarding consent refuse a send. Their
writers take the account row lock first and bump the version of the row the send
checks (the profile's, or the consent decision's), and the send reads that state under
its account locks. Stage B1 makes match activation run the same profile and consent
checks under its account locks (CX5), and adds the token grant (F1; DM-14 item 3): the
account row and the session row locked ``FOR SHARE`` in the send's order, the time from
``clock_timestamp()`` under those locks, and every check of ``grant_chat_token`` on the
locked rows, so a grant that waits on an epoch bump refuses after it, and a grant that
commits before the bump has an issue time before the bump's cut-off, from one clock.

There is no switch here: no test-only branch, flag or hook that changes a lock, a
check or a write (DM-13 2.1). A ``TransactionProbe`` may observe a writer at its hold
points; it only signals and waits.

Each new provider identifier (user, channel, message) is ``secrets.token_hex(16)``,
committed before any provider call so a retry reuses it; it is never derived from an
account ID, name or email, and never logged. A new ``ChatIdentity`` is ``pending`` and
gets its own outbox event, written before the channel's (CX4; DM-15 3.1 to 3.5); the
provider's receipt of its provisioning makes it ``active``.
"""

from __future__ import annotations

import secrets
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from django.db import IntegrityError, connection, transaction
from django.db.models import Q

from glow_chat import events
from glow_domain import chat, chat_tokens
from glow_domain.chat import ContactResult, SendCommand, SendReceipt, TransactionProbe
from glow_domain.chat import TransactionTrace as Trace
from glow_persistence.models import (
    AccountSession,
    AppAccount,
    Block,
    ChatBinding,
    ChatIdentity,
    ConsentDecision,
    DeletionJob,
    DeletionTombstone,
    Match,
    MessageSubmission,
    OutboxEvent,
    Profile,
)

DEADLOCK_DETECTED = "40P01"


def new_provider_ref() -> str:
    """A random, opaque provider identifier: 32 lowercase hexadecimal characters."""
    return secrets.token_hex(16)


class _Refused(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class _Rollback(Exception):
    def __init__(self, reason: str, trace: Trace) -> None:
        super().__init__(reason)
        self.reason = reason
        self.trace = trace


@dataclass
class _Tx:
    """One writer's transaction: its cursor, its trace, its probe and the events it
    wrote."""

    cursor: Any
    trace: Trace
    probe: TransactionProbe | None
    events: list[UUID] = field(default_factory=list)


class OrmContactPersistence:
    """``ContactPersistence`` over ``glow_persistence``'s models."""

    def __init__(self, *, provider: str) -> None:
        if not provider or not provider.isascii() or not provider.isidentifier():
            raise ValueError("a provider name is required")
        self.provider = provider

    # -- transaction plumbing -----------------------------------------------------------

    @staticmethod
    def _signal(probe: TransactionProbe | None, name: str) -> None:
        callback = getattr(probe, name, None) if probe is not None else None
        if callback is not None:
            callback()

    @staticmethod
    def _clock(cursor: Any) -> datetime:
        cursor.execute("SELECT clock_timestamp()")
        value = cursor.fetchone()[0]
        assert isinstance(value, datetime)
        return value

    def _run(
        self, body: Callable[[_Tx], ContactResult], probe: TransactionProbe | None
    ) -> ContactResult:
        """One transaction. A refusal rolls back and returns a result; a deadlock or any
        other database error becomes a result; nothing is retried."""
        trace: Trace | None = None
        try:
            with transaction.atomic():
                cursor = connection.cursor()
                # The transaction's first statement: its backend and its start.
                cursor.execute("SELECT pg_backend_pid(), now()")
                pid, started = cursor.fetchone()
                trace = Trace(int(pid), started)
                if probe is not None and probe.on_begin is not None:
                    probe.on_begin(int(pid))
                tx = _Tx(cursor, trace, probe)
                try:
                    result = body(tx)
                except _Refused as refused:
                    raise _Rollback(
                        refused.reason, replace(trace, ended_at=self._clock(cursor))
                    ) from refused
                self._signal(probe, "before_commit")
                result = replace(result, trace=result.trace or trace, events=tuple(tx.events))
        except _Rollback as rollback:
            return ContactResult("refused", rollback.reason, trace=rollback.trace)
        except Exception as exc:  # noqa: BLE001 - a result the caller judges; never retried
            cause = exc.__cause__
            # The driver's DeadlockDetected, by its SQLSTATE: the API installs no driver.
            if getattr(cause, "sqlstate", None) == DEADLOCK_DETECTED:
                return ContactResult("deadlock", "DeadlockDetected", trace=trace)
            if isinstance(exc, IntegrityError):
                return ContactResult("error", f"IntegrityError:{type(cause).__name__}", trace=trace)
            return ContactResult("error", type(exc).__name__, trace=trace)
        return result

    @staticmethod
    def _lock(model: Any, pk: UUID) -> Any:
        """A row by primary key, ``FOR UPDATE``. No state filter joins the locked read:
        an absent row is a refusal (5.5)."""
        row = model.objects.select_for_update().filter(pk=pk).first()
        if row is None:
            raise _Refused(f"{model.__name__.lower()}_missing")
        return row

    @staticmethod
    def _event(
        tx: _Tx,
        event_type: str,
        *,
        aggregate_id: UUID,
        aggregate_version: int,
        available_at: datetime,
        payload_ref: UUID,
    ) -> None:
        event = OutboxEvent.objects.create(
            aggregate_id=aggregate_id,
            aggregate_version=aggregate_version,
            event_type=event_type,
            schema_version=events.CHAT_SCHEMA_VERSION,
            dedup_key=f"{event_type}:{aggregate_id}:{aggregate_version}",
            payload_ref=payload_ref,
            state="pending",
            available_at=available_at,
        )
        tx.events.append(event.id)

    @staticmethod
    def _bump_eligibility(account: Any) -> None:
        account.eligibility_version += 1
        account.version += 1
        account.save(update_fields=["eligibility_version", "version", "updated_at"])

    @staticmethod
    def _contact_state_checks(low_id: UUID, high_id: UUID) -> None:
        """P06.2 D5, under both account locks: both profiles visible, and both accounts'
        latest onboarding consent accepted. The send and match activation (CX5) share
        these checks, so the two refuse the same states."""
        profiles = dict(
            Profile.objects.filter(account_id__in=(low_id, high_id)).values_list(
                "account_id", "state"
            )
        )
        if profiles.get(low_id) != "visible" or profiles.get(high_id) != "visible":
            raise _Refused(chat.PROFILE_UNAVAILABLE)
        for account_id in (low_id, high_id):
            latest = (
                ConsentDecision.objects.filter(
                    account_id=account_id, purpose=chat.ONBOARDING_CONSENT_PURPOSE
                )
                .order_by("-version")
                .values_list("state", flat=True)
                .first()
            )
            if latest != "accepted":
                raise _Refused(chat.CONSENT_NOT_CURRENT)

    # -- match activation ----------------------------------------------------------------

    def activate_match(
        self, first: UUID, second: UUID, *, probe: TransactionProbe | None = None
    ) -> ContactResult:
        """The proof's and the conformance run's way to make a match, not F09's
        activation (CX5; DM-15 6.3). Under both account locks it checks the accounts'
        state, an active block, an existing pair, and the send's own profile and consent
        checks (P06.2 B1); reciprocal likes and current two-person eligibility are
        checked by the activation P11 wires (F09), under the same locks. No runtime path
        calls this method.

        Each member without a ``ChatIdentity`` gets one, ``pending``, with its own outbox
        event written before the channel's (CX4; DM-15 3.1 and 3.5): the provisioning is
        delivered before the channel that names the user, and an identity that already
        exists from an earlier match gets no second event."""

        def body(tx: _Tx) -> ContactResult:
            if first == second:
                raise _Refused(chat.NOT_A_MEMBER)
            low_id, high_id = sorted((first, second))
            low = self._lock(AppAccount, low_id)
            self._signal(tx.probe, "after_first_lock")
            high = self._lock(AppAccount, high_id)
            self._signal(tx.probe, "after_locks")
            now = self._clock(tx.cursor)
            if low.state != "active" or high.state != "active":
                raise _Refused(chat.ACCOUNT_NOT_ACTIVE)
            if (
                Block.objects.filter(state="active")
                .filter(
                    Q(actor_id=low_id, target_id=high_id) | Q(actor_id=high_id, target_id=low_id)
                )
                .exists()
            ):
                raise _Refused(chat.BLOCKED)
            if Match.objects.filter(account_low_id=low_id, account_high_id=high_id).exists():
                # One pair record; rematch policy is unset (A05).
                raise _Refused(chat.MATCH_EXISTS)
            # CX5: the send's profile and consent checks, on the rows read under the
            # account locks that every writer of them takes (DM-13 4.1).
            self._contact_state_checks(low_id, high_id)
            match = Match.objects.create(
                account_low_id=low_id, account_high_id=high_id, state="active"
            )
            for account in (low, high):
                if not ChatIdentity.objects.filter(
                    account_id=account.id, provider=self.provider
                ).exists():
                    identity = ChatIdentity.objects.create(
                        account=account,
                        provider=self.provider,
                        user_ref=new_provider_ref(),
                        state="pending",
                    )
                    # Before the channel's event: delivered as the user's provisioning.
                    self._event(
                        tx,
                        events.IDENTITY_CREATED,
                        aggregate_id=identity.id,
                        aggregate_version=1,
                        available_at=now,
                        payload_ref=identity.id,
                    )
            binding = ChatBinding.objects.create(
                match=match, provider=self.provider, channel_ref=new_provider_ref(), state="pending"
            )
            self._event(
                tx,
                events.MATCH_ACTIVATED,
                aggregate_id=match.id,
                aggregate_version=1,
                available_at=now,
                payload_ref=binding.id,
            )
            return ContactResult("applied", match_id=match.id)

        return self._run(body, probe)

    # -- the token grant (P06.2 B1; F1, DM-14 item 3) -------------------------------------

    @staticmethod
    def _lock_shared(table: str, pk: UUID, columns: tuple[str, ...], cursor: Any) -> Any:
        """A row by primary key, ``FOR SHARE``: the grant reads what a bump or a sign-out
        writes ``FOR UPDATE``, so it waits for a writer in flight and reads its result; it
        excludes no other reader. An absent row is a refusal (5.5)."""
        cursor.execute(
            f"SELECT {', '.join(columns)} FROM {table} WHERE id = %s FOR SHARE",
            [pk],
        )
        row = cursor.fetchone()
        if row is None:
            raise _Refused(f"{table.removeprefix('glow_persistence_')}_missing")
        return row

    def grant_token(
        self, session_id: UUID, *, probe: TransactionProbe | None = None
    ) -> ContactResult:
        def body(tx: _Tx) -> ContactResult:
            # Only the session's account is read before the locks: it never changes, and
            # the locked row is checked against it (F2).
            session_account = (
                AccountSession.objects.filter(pk=session_id)
                .values_list("account_id", flat=True)
                .first()
            )
            if session_account is None:
                raise _Refused(chat.SESSION_MISSING)
            account_id: UUID = session_account
            # The send's order: the account, then the session (points 1 and 2).
            account_state, session_epoch = self._lock_shared(
                "glow_persistence_appaccount", account_id, ("state", "session_epoch"), tx.cursor
            )
            self._signal(tx.probe, "after_first_lock")
            locked_account, session_state, epoch, expires_at = self._lock_shared(
                "glow_persistence_accountsession",
                session_id,
                ("account_id", "state", "epoch", "expires_at"),
                tx.cursor,
            )
            self._signal(tx.probe, "after_locks")
            now = self._clock(tx.cursor)
            if locked_account != account_id:
                raise _Refused(chat.SESSION_CHANGED)
            identity = (
                ChatIdentity.objects.filter(account_id=account_id, provider=self.provider)
                .values_list("user_ref", "state")
                .first()
            )
            user_ref, identity_state = identity if identity is not None else (None, None)
            # Every check of the rule, on the locked rows, with the database's time (5.1:
            # "active" means provisioned and not deactivated).
            granted = chat_tokens.grant_chat_token(
                account=chat_tokens.TokenAccount(str(account_state), int(session_epoch)),
                session=chat_tokens.TokenSession(str(session_state), int(epoch), expires_at),
                user_ref=user_ref,
                identity_active=identity_state == "active",
                now=now,
            )
            self._signal(tx.probe, "before_commit")
            if isinstance(granted, chat_tokens.TokenRefusal):
                raise _Refused(granted.code)
            return ContactResult("granted", grant=granted, session_id=session_id)

        return self._run(body, probe)

    # -- sessions ---------------------------------------------------------------------

    def open_session(
        self,
        account_id: UUID,
        *,
        auth_session_ref: str,
        lifetime: timedelta,
        probe: TransactionProbe | None = None,
    ) -> ContactResult:
        def body(tx: _Tx) -> ContactResult:
            account = self._lock(AppAccount, account_id)
            self._signal(tx.probe, "after_first_lock")
            self._signal(tx.probe, "after_locks")
            now = self._clock(tx.cursor)
            if account.state != "active":
                raise _Refused(chat.ACCOUNT_NOT_ACTIVE)
            tx.cursor.execute(
                "SELECT %s::timestamptz + make_interval(secs => %s)",
                [now, lifetime.total_seconds()],
            )
            expires_at = tx.cursor.fetchone()[0]
            session = AccountSession.objects.create(
                account=account,
                auth_session_ref=auth_session_ref,
                epoch=account.session_epoch,
                state="valid",
                expires_at=expires_at,
            )
            return ContactResult("applied", session_id=session.id)

        return self._run(body, probe)

    def sign_out(self, session_id: UUID, *, probe: TransactionProbe | None = None) -> ContactResult:
        return self._end_session(session_id, "revoked", probe)

    def expire_session(
        self, session_id: UUID, *, probe: TransactionProbe | None = None
    ) -> ContactResult:
        return self._end_session(session_id, "expired", probe)

    def _end_session(
        self, session_id: UUID, new_state: str, probe: TransactionProbe | None
    ) -> ContactResult:
        def body(tx: _Tx) -> ContactResult:
            # 5.1: the session row the send locks, by primary key.
            session = self._lock(AccountSession, session_id)
            self._signal(tx.probe, "after_first_lock")
            self._signal(tx.probe, "after_locks")
            now = self._clock(tx.cursor)
            if session.state != "valid":
                return ContactResult("no_change", f"already_{session.state}", session_id=session.id)
            session.state = new_state
            session.version += 1
            fields = ["state", "version", "updated_at"]
            if new_state == "revoked":
                session.revoked_at = now
                fields.append("revoked_at")
            session.save(update_fields=fields)
            self._event(
                tx,
                events.SESSION_REVOKED if new_state == "revoked" else events.SESSION_EXPIRED,
                aggregate_id=session.id,
                aggregate_version=session.version,
                available_at=now,
                payload_ref=session.id,
            )
            return ContactResult("applied", session_id=session.id)

        return self._run(body, probe)

    # -- the send -----------------------------------------------------------------------

    def send(self, command: SendCommand, *, probe: TransactionProbe | None = None) -> ContactResult:
        def body(tx: _Tx) -> ContactResult:
            # Only identifiers are read before the locks: a match's pair and a session's
            # account never change. Every value a check uses is read under the locks.
            pair = (
                Match.objects.filter(pk=command.match_id)
                .values_list("account_low_id", "account_high_id")
                .first()
            )
            session_account = (
                AccountSession.objects.filter(pk=command.session_id)
                .values_list("account_id", flat=True)
                .first()
            )
            if pair is None:
                raise _Refused(chat.MATCH_MISSING)
            if session_account is None:
                raise _Refused(chat.SESSION_MISSING)
            low_id, high_id = pair
            if session_account not in (low_id, high_id):
                raise _Refused(chat.NOT_A_MEMBER)
            actor_id = session_account
            other_id = high_id if actor_id == low_id else low_id

            low = self._lock(AppAccount, low_id)
            self._signal(tx.probe, "after_first_lock")
            high = self._lock(AppAccount, high_id)
            match = self._lock(Match, command.match_id)
            session = self._lock(AccountSession, command.session_id)
            self._signal(tx.probe, "after_locks")
            now = self._clock(tx.cursor)

            # P06.DB 5.6: the checks, in code, on the rows as locked.
            if match.state != "active":
                raise _Refused(chat.MATCH_NOT_ACTIVE)
            if (match.account_low_id, match.account_high_id) != (low_id, high_id):
                raise _Refused(chat.MATCH_CHANGED)
            if session.account_id != actor_id:
                # F2: the locked session's account against the pre-lock read.
                raise _Refused(chat.SESSION_CHANGED)
            if low.state != "active" or high.state != "active":
                raise _Refused(chat.ACCOUNT_NOT_ACTIVE)
            if session.state != "valid":
                raise _Refused(chat.SESSION_NOT_VALID)
            if session.expires_at <= now:
                raise _Refused(chat.SESSION_EXPIRED)
            actor = low if actor_id == low_id else high
            if session.epoch != actor.session_epoch:
                raise _Refused(chat.SESSION_EPOCH_STALE)
            if (
                Block.objects.filter(state="active")
                .filter(
                    Q(actor_id=actor_id, target_id=other_id)
                    | Q(actor_id=other_id, target_id=actor_id)
                )
                .exists()
            ):
                raise _Refused(chat.BLOCKED)
            if match.contact_version != command.contact_version:
                raise _Refused(chat.STALE_CONTACT_VERSION)
            # P06.2 D5: both profiles visible, and both accounts' latest onboarding
            # consent accepted, read under the account locks every writer of them takes.
            self._contact_state_checks(low_id, high_id)

            # 5.4: authorized; now deduplicate.
            existing = MessageSubmission.objects.filter(
                actor_id=actor_id, idempotency_key=command.idempotency_key
            ).first()
            if existing is not None:
                if existing.request_digest != command.request_digest:
                    raise _Refused(chat.IDEMPOTENCY_CONFLICT)
                return ContactResult(
                    "replayed",
                    receipt=SendReceipt(
                        existing.id, existing.contact_version, existing.request_digest
                    ),
                    trace=replace(tx.trace, ended_at=self._clock(tx.cursor)),
                    session_id=command.session_id,
                    match_id=command.match_id,
                )

            binding = ChatBinding.objects.filter(match_id=command.match_id).first()
            if binding is None or binding.state not in ("pending", "active"):
                raise _Refused(chat.BINDING_NOT_ACTIVE)
            submission = MessageSubmission.objects.create(
                binding=binding,
                actor_id=actor_id,
                contact_version=match.contact_version,
                idempotency_key=command.idempotency_key,
                request_digest=command.request_digest,
                text=command.text,
                # The provider message ID, chosen now so a retried delivery reuses it.
                provider_message_ref=new_provider_ref(),
                state="pending",
            )
            self._event(
                tx,
                events.MESSAGE_SUBMITTED,
                aggregate_id=submission.id,
                aggregate_version=1,
                available_at=now,
                payload_ref=submission.id,
            )
            return ContactResult(
                "authorized",
                receipt=SendReceipt(submission.id, match.contact_version, command.request_digest),
                session_id=command.session_id,
                match_id=command.match_id,
            )

        return self._run(body, probe)

    # -- block, unblock, unmatch ----------------------------------------------------------

    def block(
        self, actor_id: UUID, target_id: UUID, *, probe: TransactionProbe | None = None
    ) -> ContactResult:
        def body(tx: _Tx) -> ContactResult:
            if actor_id == target_id:
                # F5: refused before any lock or write, not left to the no-self constraint.
                raise _Refused(chat.SELF_TARGET)
            low_id, high_id = sorted((actor_id, target_id))
            # 5.3: the lower account first, whoever acts.
            accounts = {low_id: self._lock(AppAccount, low_id)}
            self._signal(tx.probe, "after_first_lock")
            accounts[high_id] = self._lock(AppAccount, high_id)
            match = (
                Match.objects.select_for_update()
                .filter(account_low_id=low_id, account_high_id=high_id)
                .first()
            )
            block = (
                Block.objects.select_for_update()
                .filter(actor_id=actor_id, target_id=target_id)
                .first()
            )
            self._signal(tx.probe, "after_locks")
            now = self._clock(tx.cursor)

            changed = block is None or block.state != "active"
            if block is None:
                block = Block.objects.create(actor_id=actor_id, target_id=target_id, state="active")
            elif block.state != "active":
                block.state = "active"
                block.version += 1
                block.save(update_fields=["state", "version", "updated_at"])
            if changed:
                actor = accounts[actor_id]
                actor.blocks_version += 1
                actor.version += 1
                actor.save(update_fields=["blocks_version", "version", "updated_at"])
                self._event(
                    tx,
                    events.BLOCK_CHANGED,
                    aggregate_id=block.id,
                    aggregate_version=block.version,
                    available_at=now,
                    payload_ref=block.id,
                )
            contact_version: int | None = None
            if match is not None and match.state == "active":
                match.state = "restricted"
                match.contact_version += 1
                match.version += 1
                match.save(update_fields=["state", "contact_version", "version", "updated_at"])
                contact_version = match.contact_version
                # D6: delivered as the removal of both members.
                self._event(
                    tx,
                    events.CONTACT_REVOKED,
                    aggregate_id=match.id,
                    aggregate_version=match.contact_version,
                    available_at=now,
                    payload_ref=match.id,
                )
            if not changed and contact_version is None:
                raise _Refused(chat.ALREADY_BLOCKED)
            return ContactResult(
                "applied",
                match_id=match.id if match is not None else None,
                detail={"contact_version": contact_version},
            )

        return self._run(body, probe)

    def unblock(
        self, actor_id: UUID, target_id: UUID, *, probe: TransactionProbe | None = None
    ) -> ContactResult:
        def body(tx: _Tx) -> ContactResult:
            low_id, high_id = sorted((actor_id, target_id))
            accounts = {low_id: self._lock(AppAccount, low_id)}
            self._signal(tx.probe, "after_first_lock")
            accounts[high_id] = self._lock(AppAccount, high_id)
            block = (
                Block.objects.select_for_update()
                .filter(actor_id=actor_id, target_id=target_id)
                .first()
            )
            self._signal(tx.probe, "after_locks")
            now = self._clock(tx.cursor)
            if block is None or block.state != "active":
                raise _Refused(chat.NO_ACTIVE_BLOCK)
            block.state = "removed"
            block.version += 1
            block.save(update_fields=["state", "version", "updated_at"])
            actor = accounts[actor_id]
            actor.blocks_version += 1
            actor.version += 1
            actor.save(update_fields=["blocks_version", "version", "updated_at"])
            self._event(
                tx,
                events.BLOCK_CHANGED,
                aggregate_id=block.id,
                aggregate_version=block.version,
                available_at=now,
                payload_ref=block.id,
            )
            # The match stays as it is: an unblock never restores contact (DB06).
            return ContactResult("applied")

        return self._run(body, probe)

    def unmatch(
        self, actor_id: UUID, match_id: UUID, *, probe: TransactionProbe | None = None
    ) -> ContactResult:
        def body(tx: _Tx) -> ContactResult:
            pair = (
                Match.objects.filter(pk=match_id)
                .values_list("account_low_id", "account_high_id")
                .first()
            )
            if pair is None:
                raise _Refused(chat.MATCH_MISSING)
            low_id, high_id = pair
            if actor_id not in (low_id, high_id):
                raise _Refused(chat.NOT_A_MEMBER)
            self._lock(AppAccount, low_id)
            self._signal(tx.probe, "after_first_lock")
            self._lock(AppAccount, high_id)
            match = self._lock(Match, match_id)
            self._signal(tx.probe, "after_locks")
            now = self._clock(tx.cursor)
            if (match.account_low_id, match.account_high_id) != (low_id, high_id):
                # F2: the locked match's pair against the pre-lock read.
                raise _Refused(chat.MATCH_CHANGED)
            if match.state == "unmatched":
                return ContactResult("no_change", "already_unmatched", match_id=match.id)
            match.state = "unmatched"
            match.contact_version += 1
            match.version += 1
            match.save(update_fields=["state", "contact_version", "version", "updated_at"])
            self._event(
                tx,
                events.CONTACT_REVOKED,
                aggregate_id=match.id,
                aggregate_version=match.contact_version,
                available_at=now,
                payload_ref=match.id,
            )
            return ContactResult(
                "applied", match_id=match.id, detail={"contact_version": match.contact_version}
            )

        return self._run(body, probe)

    # -- the account-wide revocations (5.3: the account row, not each match) ----------

    def suspend(self, account_id: UUID, *, probe: TransactionProbe | None = None) -> ContactResult:
        return self._revoke_account(account_id, "suspended", probe)

    def delete(self, account_id: UUID, *, probe: TransactionProbe | None = None) -> ContactResult:
        return self._revoke_account(account_id, "deletion_pending", probe)

    def _revoke_account(
        self, account_id: UUID, new_state: str, probe: TransactionProbe | None
    ) -> ContactResult:
        def body(tx: _Tx) -> ContactResult:
            account = self._lock(AppAccount, account_id)
            self._signal(tx.probe, "after_first_lock")
            self._signal(tx.probe, "after_locks")
            now = self._clock(tx.cursor)
            if account.state == new_state:
                return ContactResult("no_change", f"already_{new_state}")
            if account.state in ("deletion_pending", "deleted"):
                raise _Refused(chat.ACCOUNT_DELETED)
            account.state = new_state
            account.session_epoch += 1
            account.eligibility_version += 1
            account.version += 1
            account.save(
                update_fields=[
                    "state",
                    "session_epoch",
                    "eligibility_version",
                    "version",
                    "updated_at",
                ]
            )
            if new_state == "deletion_pending":
                # 5.6: the lifecycle transition, with its job and tombstone; never a hard
                # delete, so committed authorizations remain.
                job = DeletionJob.objects.create(
                    account=account, subject_id=account.id, state="access_revoked"
                )
                DeletionTombstone.objects.create(
                    subject_id=account.id, deletion=job, revoked_at=now
                )
            # D6: delivered as the deactivation of the provider user.
            self._event(
                tx,
                events.ACCESS_REVOKED,
                aggregate_id=account.id,
                aggregate_version=account.session_epoch,
                available_at=now,
                payload_ref=account.id,
            )
            # DM-13 5.1: every session-epoch bump revokes the user's provider tokens.
            self._event(
                tx,
                events.SESSION_EPOCH_BUMPED,
                aggregate_id=account.id,
                aggregate_version=account.session_epoch,
                available_at=now,
                payload_ref=account.id,
            )
            return ContactResult("applied", detail={"session_epoch": account.session_epoch})

        return self._run(body, probe)

    # -- P06.2 D5: profile state and consent ------------------------------------------

    def pause_profile(
        self, account_id: UUID, *, probe: TransactionProbe | None = None
    ) -> ContactResult:
        return self._set_profile(account_id, "paused", ("visible",), events.PROFILE_PAUSED, probe)

    def resume_profile(
        self, account_id: UUID, *, probe: TransactionProbe | None = None
    ) -> ContactResult:
        return self._set_profile(account_id, "visible", ("paused",), events.PROFILE_RESUMED, probe)

    def restrict_profile(
        self, account_id: UUID, *, probe: TransactionProbe | None = None
    ) -> ContactResult:
        return self._set_profile(
            account_id, "restricted", ("visible", "paused"), events.PROFILE_RESTRICTED, probe
        )

    def _set_profile(
        self,
        account_id: UUID,
        new_state: str,
        from_states: tuple[str, ...],
        event_type: str,
        probe: TransactionProbe | None,
    ) -> ContactResult:
        def body(tx: _Tx) -> ContactResult:
            # DM-13 4.1: the account row first, in the canonical order, then its profile.
            account = self._lock(AppAccount, account_id)
            self._signal(tx.probe, "after_first_lock")
            profile = Profile.objects.select_for_update().filter(account_id=account_id).first()
            if profile is None:
                raise _Refused(chat.PROFILE_MISSING)
            self._signal(tx.probe, "after_locks")
            now = self._clock(tx.cursor)
            if profile.state == new_state:
                return ContactResult("no_change", f"already_{new_state}")
            if profile.state not in from_states:
                raise _Refused(chat.PROFILE_UNAVAILABLE)
            profile.state = new_state
            profile.version += 1
            profile.save(update_fields=["state", "version", "updated_at"])
            self._bump_eligibility(account)
            self._event(
                tx,
                event_type,
                aggregate_id=profile.id,
                aggregate_version=profile.version,
                available_at=now,
                payload_ref=profile.id,
            )
            return ContactResult("applied", detail={"profile_version": profile.version})

        return self._run(body, probe)

    def withdraw_consent(
        self, account_id: UUID, *, probe: TransactionProbe | None = None
    ) -> ContactResult:
        return self._decide_consent(account_id, "withdrawn", None, probe)

    def accept_consent(
        self, account_id: UUID, *, policy_version: str, probe: TransactionProbe | None = None
    ) -> ContactResult:
        if not policy_version:
            raise ValueError("a policy version is required")
        return self._decide_consent(account_id, "accepted", policy_version, probe)

    def _decide_consent(
        self,
        account_id: UUID,
        decision: str,
        policy_version: str | None,
        probe: TransactionProbe | None,
    ) -> ContactResult:
        def body(tx: _Tx) -> ContactResult:
            # DM-13 4.1: the account row first. Decisions are append-only; the new one
            # carries the next version, which is what the send reads as the latest.
            account = self._lock(AppAccount, account_id)
            self._signal(tx.probe, "after_first_lock")
            self._signal(tx.probe, "after_locks")
            now = self._clock(tx.cursor)
            latest = (
                ConsentDecision.objects.filter(
                    account_id=account_id, purpose=chat.ONBOARDING_CONSENT_PURPOSE
                )
                .order_by("-version")
                .first()
            )
            if decision == "withdrawn":
                if latest is None:
                    raise _Refused(chat.NO_CONSENT)
                if latest.state == "withdrawn":
                    return ContactResult("no_change", "already_withdrawn")
                version_text = latest.policy_version
            else:
                assert policy_version is not None
                if (
                    latest is not None
                    and latest.state == "accepted"
                    and latest.policy_version == policy_version
                ):
                    return ContactResult("no_change", "already_accepted")
                version_text = policy_version
            row = ConsentDecision.objects.create(
                account=account,
                purpose=chat.ONBOARDING_CONSENT_PURPOSE,
                policy_version=version_text,
                state=decision,
                decided_at=now,
                version=1 if latest is None else latest.version + 1,
            )
            self._bump_eligibility(account)
            self._event(
                tx,
                events.CONSENT_WITHDRAWN if decision == "withdrawn" else events.CONSENT_ACCEPTED,
                aggregate_id=account.id,
                aggregate_version=row.version,
                available_at=now,
                payload_ref=row.id,
            )
            return ContactResult("applied", detail={"consent_version": row.version})

        return self._run(body, probe)

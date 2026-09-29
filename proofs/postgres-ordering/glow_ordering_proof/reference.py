"""The reference design under proof (D5): READ COMMITTED with row locks.

Every writer runs in one ``transaction.atomic()`` at READ COMMITTED and locks rows by
primary key with ``SELECT ... FOR UPDATE`` in the canonical order: the lower account,
the higher account, the match, then the sending session's ``AccountSession`` row.
State is checked in code after the locks (5.5); time is read after the locks (5.2);
the send authorizes first and deduplicates second (5.4); an empty locked read is a
refusal (5.5); deletion is the lifecycle transition (5.6). Each writer records one
proof-log row in its transaction, so the commit-order oracle can read its commit time.

``Design`` holds the switches the negative controls flip. The reference is
``Design()`` with every switch at its default; each control breaks exactly one
guarantee, and the suite must see that control fail (item 6.3).

P06.2 carries this design into the app's persistence adapter; the stand-in
``auth_session_ref`` generator is not carried (D2).
"""

from __future__ import annotations

import secrets
from collections.abc import Callable
from datetime import datetime
from typing import Any
from uuid import UUID

import psycopg.errors
from django.db import IntegrityError, connection, transaction
from django.db.models import Q
from glow_persistence.models import (
    AccountSession,
    AppAccount,
    Block,
    ChatBinding,
    DeletionJob,
    DeletionTombstone,
    Match,
    MessageSubmission,
    OutboxEvent,
)

from glow_ordering_proof.design import REFERENCE, Design
from glow_ordering_proof.interface import Hooks, Receipt, Result, SendRequest, Timing
from glow_ordering_proof.observe import ProofLog

SCHEMA_VERSION = "p06db-proof-1"


class _Refused(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class ReferenceSubject:
    """``OrderingSubject`` as the reference design, over the reviewed models."""

    def __init__(self, log: ProofLog, design: Design = REFERENCE) -> None:
        self.log = log
        self.design = design

    # -- transaction plumbing -------------------------------------------------------

    def _begin(self, hooks: Hooks | None) -> tuple[Any, Timing]:
        """The first statement of the transaction: the backend pid and the transaction's
        start time. The pid reaches the harness before any lock is attempted."""
        cursor = connection.cursor()
        cursor.execute("SELECT pg_backend_pid(), now()")
        pid, started = cursor.fetchone()
        if hooks and hooks.on_begin:
            hooks.on_begin(int(pid))
        return cursor, Timing(backend_pid=int(pid), started_at=started)

    def _time(self, cursor: Any) -> datetime:
        """5.2: the time the checks use, read after the locks. The control reads the
        transaction's start time instead."""
        if self.design.time_source == "clock_timestamp":
            cursor.execute("SELECT clock_timestamp()")
        else:
            cursor.execute("SELECT now()")
        value = cursor.fetchone()[0]
        assert isinstance(value, datetime)
        return value

    def _run(self, body: Callable[[Any, Timing], Result], hooks: Hooks | None) -> Result:
        """One transaction. A refusal rolls back and returns a Result; a deadlock or any
        other database error becomes a Result the case can judge; nothing is retried."""
        timing: Timing | None = None
        try:
            with transaction.atomic():
                cursor, timing = self._begin(hooks)
                try:
                    return body(cursor, timing)
                except _Refused as refused:
                    ended = self._clock(cursor)
                    raise _Rollback(
                        refused.reason, Timing(timing.backend_pid, timing.started_at, ended)
                    ) from refused
        except _Rollback as rollback:
            return Result("refused", rollback.reason, timing=rollback.timing)
        except Exception as exc:  # noqa: BLE001 - judged by the case, never retried
            cause = exc.__cause__
            if isinstance(cause, psycopg.errors.DeadlockDetected):
                return Result("deadlock", "DeadlockDetected", timing=timing)
            if isinstance(exc, IntegrityError):
                return Result("error", f"IntegrityError:{type(cause).__name__}", timing=timing)
            return Result("error", f"{type(exc).__name__}", timing=timing)

    @staticmethod
    def _clock(cursor: Any) -> datetime:
        cursor.execute("SELECT clock_timestamp()")
        value = cursor.fetchone()[0]
        assert isinstance(value, datetime)
        return value

    def _lock(self, model: Any, pk: UUID, *, lock: bool = True, state: str | None = None) -> Any:
        """A row by primary key, ``FOR UPDATE`` when ``lock``. With the 5.5 control the
        state filter joins the locked read and an absent row is returned as None."""
        query = model.objects.select_for_update() if lock else model.objects
        if self.design.filter_state_in_lock and state is not None:
            return query.filter(pk=pk, state=state).first()
        row = query.filter(pk=pk).first()
        if row is None:
            raise _Refused(f"{model.__name__.lower()}_missing")
        return row

    @staticmethod
    def _hook(hooks: Hooks | None, name: str) -> None:
        callback = getattr(hooks, name, None) if hooks else None
        if callback is not None:
            callback()

    @staticmethod
    def _outbox(
        *,
        event_type: str,
        aggregate_id: UUID,
        aggregate_version: int,
        available_at: datetime,
        payload_ref: UUID,
    ) -> None:
        OutboxEvent.objects.create(
            aggregate_id=aggregate_id,
            aggregate_version=aggregate_version,
            event_type=event_type,
            schema_version=SCHEMA_VERSION,
            dedup_key=f"{event_type}:{aggregate_id}:{aggregate_version}",
            payload_ref=payload_ref,
            state="pending",
            available_at=available_at,
        )

    def _ordered(self, first: UUID, second: UUID) -> tuple[UUID, UUID]:
        if self.design.canonical_order:
            low, high = sorted((first, second))
            return low, high
        return first, second

    # -- the send ----------------------------------------------------------------

    def send(self, request: SendRequest, *, hooks: Hooks | None = None) -> Result:
        design = self.design

        def body(cursor: Any, timing: Timing) -> Result:
            # Only identifiers are read before the locks; every value the checks use is
            # re-read under them (5.5). Match pairs and a session's account are immutable.
            pair = (
                Match.objects.filter(pk=request.match_id)
                .values_list("account_low_id", "account_high_id")
                .first()
            )
            session_account = (
                AccountSession.objects.filter(pk=request.session_id)
                .values_list("account_id", flat=True)
                .first()
            )
            if pair is None:
                raise _Refused("match_missing")
            if session_account is None:
                raise _Refused("session_missing")
            low_id, high_id = pair
            if session_account not in (low_id, high_id):
                raise _Refused("not_a_member")
            actor_id = session_account
            other_id = high_id if actor_id == low_id else low_id

            low = self._lock(AppAccount, low_id, lock=design.lock_accounts, state="active")
            self._hook(hooks, "after_first_lock")
            high = self._lock(AppAccount, high_id, lock=design.lock_accounts, state="active")
            match = self._lock(Match, request.match_id, lock=design.lock_match, state="active")
            session = self._lock(
                AccountSession, request.session_id, lock=design.lock_session, state="valid"
            )
            self._hook(hooks, "after_locks")
            now = self._time(cursor)

            # 5.6: the checks, in code, on the rows as locked.
            if match is not None:
                if match.state != "active":
                    raise _Refused("match_not_active")
                if (match.account_low_id, match.account_high_id) != (low_id, high_id):
                    raise _Refused("match_changed")
            for account in (low, high):
                if account is not None and account.state != "active":
                    raise _Refused("account_not_active")
            if session is not None:
                if session.state != "valid":
                    raise _Refused("session_not_valid")
                if session.expires_at <= now:
                    raise _Refused("session_expired")
                actor = low if actor_id == low_id else high
                if actor is not None and session.epoch != actor.session_epoch:
                    raise _Refused("session_epoch_stale")
            if (
                Block.objects.filter(state="active")
                .filter(
                    Q(actor_id=actor_id, target_id=other_id)
                    | Q(actor_id=other_id, target_id=actor_id)
                )
                .exists()
            ):
                raise _Refused("blocked")
            if design.check_contact_version and match is not None:
                if match.contact_version != request.contact_version:
                    raise _Refused("stale_contact_version")

            def deduplicate() -> Result | None:
                existing = MessageSubmission.objects.filter(
                    actor_id=actor_id, idempotency_key=request.idempotency_key
                ).first()
                if existing is None:
                    return None
                if existing.request_digest != request.request_digest:
                    raise _Refused("idempotency_conflict")
                return Result(
                    "replayed",
                    receipt=Receipt(existing.id, existing.contact_version, existing.request_digest),
                    timing=Timing(timing.backend_pid, timing.started_at, self._clock(cursor)),
                )

            # 5.4: authorize (every check above), then deduplicate. The control
            # ``_send_dedup_first`` looks the receipt up before any check instead.
            replayed = deduplicate()
            if replayed is not None:
                return replayed

            binding = ChatBinding.objects.filter(match_id=request.match_id).first()
            if binding is None or binding.state != "active":
                raise _Refused("binding_not_active")
            contact_version = (
                match.contact_version if match is not None else request.contact_version
            )
            submission = MessageSubmission.objects.create(
                binding=binding,
                actor_id=actor_id,
                contact_version=contact_version,
                idempotency_key=request.idempotency_key,
                request_digest=request.request_digest,
                text=request.text,
                state="pending",
            )
            self._outbox(
                event_type="message_submitted",
                aggregate_id=submission.id,
                aggregate_version=1,
                available_at=now,
                payload_ref=submission.id,
            )
            self.log.record(
                cursor,
                kind="send",
                outcome="authorized",
                submission_id=submission.id,
                match_id=request.match_id,
                actor_id=actor_id,
                session_id=request.session_id,
                contact_version=contact_version,
                epoch=session.epoch if session is not None else None,
            )
            return Result(
                "authorized",
                receipt=Receipt(submission.id, contact_version, request.request_digest),
                timing=timing,
            )

        if not design.authorize_before_dedup:
            return self._send_dedup_first(request, hooks, body)
        return self._run(body, hooks)

    def _send_dedup_first(
        self,
        request: SendRequest,
        hooks: Hooks | None,
        body: Callable[[Any, Timing], Result],
    ) -> Result:
        """The 5.4 control: the receipt lookup runs before any authorization check, so a
        retry after a revocation gets the old receipt as if it were current."""

        def broken(cursor: Any, timing: Timing) -> Result:
            actor_id = (
                AccountSession.objects.filter(pk=request.session_id)
                .values_list("account_id", flat=True)
                .first()
            )
            existing = MessageSubmission.objects.filter(
                actor_id=actor_id, idempotency_key=request.idempotency_key
            ).first()
            if existing is not None and existing.request_digest == request.request_digest:
                return Result(
                    "replayed",
                    receipt=Receipt(existing.id, existing.contact_version, existing.request_digest),
                    timing=timing,
                )
            return body(cursor, timing)

        return self._run(broken, hooks)

    # -- the revocations of contact -----------------------------------------------

    def block(self, actor_id: UUID, target_id: UUID, *, hooks: Hooks | None = None) -> Result:
        def body(cursor: Any, timing: Timing) -> Result:
            first, second = self._ordered(actor_id, target_id)
            accounts = {}
            accounts[first] = self._lock(AppAccount, first)
            self._hook(hooks, "after_first_lock")
            accounts[second] = self._lock(AppAccount, second)
            low_id, high_id = sorted((actor_id, target_id))
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
            self._hook(hooks, "after_locks")
            now = self._time(cursor)

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
                self._outbox(
                    event_type="block_changed",
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
                self._outbox(
                    event_type="contact_revoked",
                    aggregate_id=match.id,
                    aggregate_version=match.contact_version,
                    available_at=now,
                    payload_ref=match.id,
                )
            if not changed and contact_version is None:
                raise _Refused("already_blocked")
            self.log.record(
                cursor,
                kind="block",
                outcome="applied",
                match_id=match.id if match is not None else None,
                actor_id=actor_id,
                target_id=target_id,
                contact_version=contact_version,
            )
            return Result("applied", detail={"contact_version": contact_version})

        return self._run(body, hooks)

    def unblock(self, actor_id: UUID, target_id: UUID, *, hooks: Hooks | None = None) -> Result:
        def body(cursor: Any, timing: Timing) -> Result:
            first, second = self._ordered(actor_id, target_id)
            accounts = {first: self._lock(AppAccount, first)}
            self._hook(hooks, "after_first_lock")
            accounts[second] = self._lock(AppAccount, second)
            low_id, high_id = sorted((actor_id, target_id))
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
            self._hook(hooks, "after_locks")
            now = self._time(cursor)
            if block is None or block.state != "active":
                raise _Refused("no_active_block")
            block.state = "removed"
            block.version += 1
            block.save(update_fields=["state", "version", "updated_at"])
            actor = accounts[actor_id]
            actor.blocks_version += 1
            actor.version += 1
            actor.save(update_fields=["blocks_version", "version", "updated_at"])
            self._outbox(
                event_type="block_changed",
                aggregate_id=block.id,
                aggregate_version=block.version,
                available_at=now,
                payload_ref=block.id,
            )
            # The match is left as it is: contact does not come back (DB06).
            self.log.record(
                cursor,
                kind="unblock",
                outcome="applied",
                match_id=match.id if match is not None else None,
                actor_id=actor_id,
                target_id=target_id,
            )
            return Result("applied")

        return self._run(body, hooks)

    def unmatch(self, actor_id: UUID, match_id: UUID, *, hooks: Hooks | None = None) -> Result:
        def body(cursor: Any, timing: Timing) -> Result:
            pair = (
                Match.objects.filter(pk=match_id)
                .values_list("account_low_id", "account_high_id")
                .first()
            )
            if pair is None:
                raise _Refused("match_missing")
            low_id, high_id = pair
            if actor_id not in (low_id, high_id):
                raise _Refused("not_a_member")
            self._lock(AppAccount, low_id)
            self._hook(hooks, "after_first_lock")
            self._lock(AppAccount, high_id)
            match = self._lock(Match, match_id)
            self._hook(hooks, "after_locks")
            now = self._time(cursor)
            if match.state == "unmatched":
                return Result("no_change", "already_unmatched", timing=timing)
            match.state = "unmatched"
            match.contact_version += 1
            match.version += 1
            match.save(update_fields=["state", "contact_version", "version", "updated_at"])
            self._outbox(
                event_type="contact_revoked",
                aggregate_id=match.id,
                aggregate_version=match.contact_version,
                available_at=now,
                payload_ref=match.id,
            )
            self.log.record(
                cursor,
                kind="unmatch",
                outcome="applied",
                match_id=match.id,
                actor_id=actor_id,
                contact_version=match.contact_version,
            )
            return Result("applied", detail={"contact_version": match.contact_version})

        return self._run(body, hooks)

    # -- the account-wide revocations (5.3: the account row, not each match) -------

    def suspend(self, account_id: UUID, *, hooks: Hooks | None = None) -> Result:
        return self._revoke_account(account_id, "suspended", hooks)

    def delete(self, account_id: UUID, *, hooks: Hooks | None = None) -> Result:
        return self._revoke_account(account_id, "deletion_pending", hooks)

    def _revoke_account(self, account_id: UUID, new_state: str, hooks: Hooks | None) -> Result:
        def body(cursor: Any, timing: Timing) -> Result:
            account = self._lock(AppAccount, account_id)
            self._hook(hooks, "after_first_lock")
            self._hook(hooks, "after_locks")
            now = self._time(cursor)
            if account.state == new_state:
                return Result("no_change", f"already_{new_state}", timing=timing)
            if account.state in ("deletion_pending", "deleted"):
                raise _Refused("account_deleted")
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
                # 5.6: the lifecycle transition, with the job and tombstone the data model
                # names; never a hard delete, so committed authorizations remain.
                job = DeletionJob.objects.create(
                    account=account, subject_id=account.id, state="access_revoked"
                )
                DeletionTombstone.objects.create(
                    subject_id=account.id, deletion=job, revoked_at=now
                )
            self._outbox(
                event_type="access_revoked",
                aggregate_id=account.id,
                aggregate_version=account.session_epoch,
                available_at=now,
                payload_ref=account.id,
            )
            self.log.record(
                cursor,
                kind="suspend" if new_state == "suspended" else "delete",
                outcome="applied",
                actor_id=account.id,
                epoch=account.session_epoch,
            )
            return Result("applied", detail={"session_epoch": account.session_epoch})

        return self._run(body, hooks)

    # -- the minimal sign-in and its revocations (item 3) ----------------------------

    def sign_in(
        self, account_id: UUID, *, ttl_seconds: float, hooks: Hooks | None = None
    ) -> Result:
        def body(cursor: Any, timing: Timing) -> Result:
            account = self._lock(AppAccount, account_id)
            self._hook(hooks, "after_first_lock")
            self._hook(hooks, "after_locks")
            now = self._time(cursor)
            if account.state != "active":
                raise _Refused("account_not_active")
            cursor.execute("SELECT %s::timestamptz + make_interval(secs => %s)", [now, ttl_seconds])
            expires_at = cursor.fetchone()[0]
            session = AccountSession.objects.create(
                account=account,
                # A stand-in for the adapter-provided non-secret identifier (D2); random and
                # unique, not a credential, not carried into the app.
                auth_session_ref=f"standin-{secrets.token_hex(16)}",
                epoch=account.session_epoch,
                state="valid",
                expires_at=expires_at,
            )
            self.log.record(
                cursor,
                kind="sign_in",
                outcome="applied",
                actor_id=account.id,
                session_id=session.id,
                epoch=session.epoch,
            )
            return Result("applied", session_id=session.id, timing=timing)

        return self._run(body, hooks)

    def sign_out(self, session_id: UUID, *, hooks: Hooks | None = None) -> Result:
        return self._end_session(session_id, "revoked", hooks)

    def expire_session(self, session_id: UUID, *, hooks: Hooks | None = None) -> Result:
        return self._end_session(session_id, "expired", hooks)

    def _end_session(self, session_id: UUID, new_state: str, hooks: Hooks | None) -> Result:
        def body(cursor: Any, timing: Timing) -> Result:
            # 5.1: the session row the send locks, by primary key.
            session = self._lock(AccountSession, session_id)
            self._hook(hooks, "after_first_lock")
            self._hook(hooks, "after_locks")
            now = self._time(cursor)
            if session.state != "valid":
                return Result("no_change", f"already_{session.state}", timing=timing)
            session.state = new_state
            session.version += 1
            fields = ["state", "version", "updated_at"]
            if new_state == "revoked":
                session.revoked_at = now
                fields.append("revoked_at")
            session.save(update_fields=fields)
            event_type = "session_revoked" if new_state == "revoked" else "session_expired"
            self._outbox(
                event_type=event_type,
                aggregate_id=session.id,
                aggregate_version=session.version,
                available_at=now,
                payload_ref=session.id,
            )
            self.log.record(
                cursor,
                kind="sign_out" if new_state == "revoked" else "expire",
                outcome="applied",
                actor_id=session.account_id,
                session_id=session.id,
                epoch=session.epoch,
            )
            return Result("applied", session_id=session.id, timing=timing)

        return self._run(body, hooks)


class _Rollback(Exception):
    def __init__(self, reason: str, timing: Timing) -> None:
        super().__init__(reason)
        self.reason = reason
        self.timing = timing

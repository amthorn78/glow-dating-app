"""The oracle-level controls (P06.2; DM-13 2.1; P06.DB's carried item 4, CX1).

The app's adapter carries no fault switch, so the only way to show that the oracle can
still see a violation in the adapter's rows is to write such rows directly and require
the oracle to flag them. Each control here plants one violation in a fresh world, in the
row shape of the subject under test: for the reference design, a submission with its
proof-log row; for the adapter, a submission with its ``message_submitted`` event in
the same transaction and its call row. The oracle, reading that subject's evidence,
must report the control's declared rule under the control's run tag. A control whose
rule does not appear, or that hits a harness error, fails the job.

These controls do not depend on the subject: the same plant runs against both, except
the two for D5 (O10), which the reference design excludes (P06.DB 5.6).
"""

from __future__ import annotations

import secrets
import time
import uuid
from dataclasses import dataclass
from typing import Any, Protocol
from uuid import UUID

from django.db import connection, transaction

from glow_ordering_proof import oracle
from glow_ordering_proof.cases import Context, World, make_world
from glow_ordering_proof.controls import ControlResult, Signal
from glow_ordering_proof.observe import LogContext, ProofLog, db_clock

SCHEMA = oracle.ADAPTER_SCHEMA


@dataclass(frozen=True)
class PlantedControl:
    id: str
    rule: str
    guarantee: str
    plant: str  # what it writes
    d5: bool = False

    @property
    def run_tag(self) -> str:
        return f"control:{self.id}"

    @property
    def signal(self) -> Signal:
        return Signal(oracle=frozenset({self.rule}))


PLANTED: tuple[PlantedControl, ...] = (
    PlantedControl(
        "oracle.misattributed_actor",
        "O9",
        "CX1: the actor is the session's account",
        "a submission whose actor is the other member, with the sender's session",
    ),
    PlantedControl(
        "oracle.non_member_actor",
        "O9",
        "CX1: the actor is a member of the match",
        "a submission whose actor is not a member of its match",
    ),
    PlantedControl(
        "oracle.send_after_contact_revocation",
        "O2",
        "DB06 contact revocation before the send",
        "an unmatch, then a submission committed after it",
    ),
    PlantedControl(
        "oracle.send_after_session_end",
        "O3",
        "DB09 sign-out before the send",
        "a sign-out of the session, then a submission through it",
    ),
    PlantedControl(
        "oracle.send_after_account_revocation",
        "O4",
        "DB06/DB09 suspension before the send",
        "a suspension of the other member, then a submission",
    ),
    PlantedControl(
        "oracle.send_after_expiry",
        "O5",
        "CX2: the checks run before the session's expiry",
        "a submission whose transaction began after its session expired",
    ),
    PlantedControl(
        "oracle.wrong_contact_version",
        "O6",
        "DB06 the contact version as of the commit",
        "a submission at a contact version no revocation set",
    ),
    PlantedControl(
        "oracle.witness_in_another_transaction",
        "O1",
        "the send's witness commits in its transaction",
        "a submission whose send witness commits in a later transaction",
    ),
    PlantedControl(
        "oracle.unwitnessed_revocation",
        "O0",
        "every revocation has its witness",
        "a match unmatched and its contact version bumped, with no witness",
    ),
    PlantedControl(
        "oracle.send_while_paused",
        "O10",
        "P06.2 D5 a paused profile refuses a send",
        "a pause of the other member's profile, then a submission",
        d5=True,
    ),
    PlantedControl(
        "oracle.send_after_consent_withdrawn",
        "O10",
        "P06.2 D5 a withdrawn consent refuses a send",
        "a withdrawal of the other member's onboarding consent, then a submission",
        d5=True,
    ),
)
PLANTED_BY_ID = {control.id: control for control in PLANTED}


def planted_for(*, d5: bool) -> tuple[PlantedControl, ...]:
    return tuple(control for control in PLANTED if d5 or not control.d5)


class Planter(Protocol):
    def submission(
        self,
        world: World,
        *,
        actor: UUID,
        session: UUID,
        contact_version: int = 1,
        same_transaction: bool = True,
    ) -> UUID: ...

    def contact_revocation(self, world: World, *, witness: bool = True) -> None: ...

    def session_end(self, session: UUID) -> None: ...

    def account_revocation(self, account: UUID) -> None: ...

    def pause(self, account: UUID) -> None: ...

    def withdraw(self, account: UUID) -> None: ...


def _models() -> Any:
    from glow_persistence import models

    return models


def _new_submission(world: World, actor: UUID, contact_version: int) -> Any:
    m = _models()
    binding = m.ChatBinding.objects.get(match_id=world.match)
    return m.MessageSubmission.objects.create(
        binding=binding,
        actor_id=actor,
        contact_version=contact_version,
        idempotency_key=f"planted-{uuid.uuid4().hex}",
        request_digest="0" * 64,
        text="planted",
        provider_message_ref=secrets.token_hex(16),
        state="pending",
    )


def _bump_match(world: World) -> int:
    m = _models()
    match = m.Match.objects.select_for_update().get(pk=world.match)
    match.state = "unmatched"
    match.contact_version += 1
    match.version += 1
    match.save(update_fields=["state", "contact_version", "version", "updated_at"])
    return int(match.contact_version)


def _end_session(session: UUID) -> Any:
    m = _models()
    row = m.AccountSession.objects.select_for_update().get(pk=session)
    row.state = "revoked"
    row.revoked_at = db_clock()
    row.version += 1
    row.save(update_fields=["state", "revoked_at", "version", "updated_at"])
    return row


def _suspend(account: UUID) -> Any:
    m = _models()
    row = m.AppAccount.objects.select_for_update().get(pk=account)
    row.state = "suspended"
    row.session_epoch += 1
    row.version += 1
    row.save(update_fields=["state", "session_epoch", "version", "updated_at"])
    return row


class ReferencePlanter:
    """Rows in the reference design's shape: its proof-log rows are its witnesses."""

    def __init__(self, log: ProofLog) -> None:
        self.log = log

    def submission(
        self,
        world: World,
        *,
        actor: UUID,
        session: UUID,
        contact_version: int = 1,
        same_transaction: bool = True,
    ) -> UUID:
        m = _models()
        epoch = m.AccountSession.objects.filter(pk=session).values_list("epoch", flat=True).get()
        with transaction.atomic(), connection.cursor() as cursor:
            row = _new_submission(world, actor, contact_version)
            if same_transaction:
                self._send_row(cursor, world, row.id, actor, session, contact_version, epoch)
        if not same_transaction:
            with transaction.atomic(), connection.cursor() as cursor:
                self._send_row(cursor, world, row.id, actor, session, contact_version, epoch)
        assert isinstance(row.id, UUID)
        return row.id

    def _send_row(
        self,
        cursor: Any,
        world: World,
        submission: UUID,
        actor: UUID,
        session: UUID,
        contact_version: int,
        epoch: int,
    ) -> None:
        self.log.record(
            cursor,
            kind="send",
            outcome="authorized",
            submission_id=submission,
            match_id=world.match,
            actor_id=actor,
            session_id=session,
            contact_version=contact_version,
            epoch=epoch,
        )

    def contact_revocation(self, world: World, *, witness: bool = True) -> None:
        with transaction.atomic(), connection.cursor() as cursor:
            version = _bump_match(world)
            if witness:
                self.log.record(
                    cursor,
                    kind="unmatch",
                    outcome="applied",
                    match_id=world.match,
                    actor_id=world.low,
                    contact_version=version,
                )

    def session_end(self, session: UUID) -> None:
        with transaction.atomic(), connection.cursor() as cursor:
            row = _end_session(session)
            self.log.record(
                cursor,
                kind="sign_out",
                outcome="applied",
                actor_id=row.account_id,
                session_id=session,
                epoch=row.epoch,
            )

    def account_revocation(self, account: UUID) -> None:
        with transaction.atomic(), connection.cursor() as cursor:
            row = _suspend(account)
            self.log.record(
                cursor, kind="suspend", outcome="applied", actor_id=account, epoch=row.session_epoch
            )

    def pause(self, account: UUID) -> None:
        raise RuntimeError("the reference design carries no D5 writer")

    def withdraw(self, account: UUID) -> None:
        raise RuntimeError("the reference design carries no D5 writer")


class AdapterPlanter:
    """Rows in the adapter's shape: its submissions with their ``message_submitted``
    events, its revocations' outbox events and consent decisions, and the call row that
    gives an authorization its context."""

    def __init__(self, log: ProofLog) -> None:
        self.log = log

    @staticmethod
    def _event(event_type: str, aggregate: UUID, version: int, payload: UUID) -> None:
        m = _models()
        m.OutboxEvent.objects.create(
            aggregate_id=aggregate,
            aggregate_version=version,
            event_type=event_type,
            schema_version=SCHEMA,
            dedup_key=f"{event_type}:{aggregate}:{version}",
            payload_ref=payload,
            state="pending",
            available_at=db_clock(),
        )

    def submission(
        self,
        world: World,
        *,
        actor: UUID,
        session: UUID,
        contact_version: int = 1,
        same_transaction: bool = True,
    ) -> UUID:
        with transaction.atomic(), connection.cursor() as cursor:
            cursor.execute("SELECT now()")
            started = cursor.fetchone()[0]
            row = _new_submission(world, actor, contact_version)
            if same_transaction:
                self._event("message_submitted", row.id, 1, row.id)
        if not same_transaction:
            with transaction.atomic():
                self._event("message_submitted", row.id, 1, row.id)
        self.log.record_call(
            kind="send",
            outcome="authorized",
            submission_id=row.id,
            match_id=world.match,
            session_id=session,
            started_at=started,
        )
        assert isinstance(row.id, UUID)
        return row.id

    def contact_revocation(self, world: World, *, witness: bool = True) -> None:
        with transaction.atomic():
            version = _bump_match(world)
            if witness:
                self._event("contact_revoked", world.match, version, world.match)

    def session_end(self, session: UUID) -> None:
        with transaction.atomic():
            row = _end_session(session)
            self._event("session_revoked", session, row.version, session)

    def account_revocation(self, account: UUID) -> None:
        with transaction.atomic():
            row = _suspend(account)
            self._event("access_revoked", account, row.session_epoch, account)
            self._event("session_epoch_bumped", account, row.session_epoch, account)

    def pause(self, account: UUID) -> None:
        m = _models()
        with transaction.atomic():
            profile = m.Profile.objects.select_for_update().get(account_id=account)
            profile.state = "paused"
            profile.version += 1
            profile.save(update_fields=["state", "version", "updated_at"])
            self._event("profile_paused", profile.id, profile.version, profile.id)

    def withdraw(self, account: UUID) -> None:
        m = _models()
        with transaction.atomic():
            latest = (
                m.ConsentDecision.objects.filter(account_id=account, purpose=oracle.ONBOARDING)
                .order_by("-version")
                .first()
            )
            m.ConsentDecision.objects.create(
                account_id=account,
                purpose=oracle.ONBOARDING,
                policy_version=latest.policy_version,
                state="withdrawn",
                decided_at=db_clock(),
                version=latest.version + 1,
            )


def _plant(control: PlantedControl, ctx: Context, world: World, planter: Planter) -> None:
    low, high, session = world.low, world.high, world.session_low

    def send(**changes: Any) -> None:
        planter.submission(world, **{"actor": low, "session": session, **changes})

    match control.id:
        case "oracle.misattributed_actor":
            send(actor=high)
        case "oracle.non_member_actor":
            send(actor=ctx.fixtures.create_account())
        case "oracle.send_after_contact_revocation":
            planter.contact_revocation(world)
            send()
        case "oracle.send_after_session_end":
            planter.session_end(session)
            send()
        case "oracle.send_after_account_revocation":
            planter.account_revocation(high)
            send()
        case "oracle.send_after_expiry":
            _after_expiry(ctx, world, planter)
        case "oracle.wrong_contact_version":
            send(contact_version=2)
        case "oracle.witness_in_another_transaction":
            send(same_transaction=False)
        case "oracle.unwitnessed_revocation":
            planter.contact_revocation(world, witness=False)
        case "oracle.send_while_paused":
            planter.pause(high)
            send()
        case "oracle.send_after_consent_withdrawn":
            planter.withdraw(high)
            send()
        case _:
            raise ValueError(f"no plant for {control.id}")


def _after_expiry(ctx: Context, world: World, planter: Planter) -> None:
    from glow_ordering_proof.dbreads import session_row

    short = ctx.subject.sign_in(world.low, ttl_seconds=1.0)
    if short.session_id is None:
        raise RuntimeError(f"short-lived sign-in failed: {short.label()}")
    expires_at = session_row(short.session_id)[2]
    while db_clock() <= expires_at:
        time.sleep(0.01)
    planter.submission(world, actor=world.low, session=short.session_id)


def run_planted(control: PlantedControl, ctx: Context, planter: Planter) -> ControlResult:
    """Plant the control's violation in a fresh world under its run tag, then require
    the oracle, reading this subject's evidence, to report its rule under that tag."""
    ctx.log.context = LogContext(run_tag=control.run_tag, variant=f"{ctx.name}:planted")
    error = ""
    try:
        world = make_world(ctx)
        _plant(control, ctx, world, planter)
    except Exception as exc:  # noqa: BLE001 - a harness error disqualifies the control
        error = f"harness error: {type(exc).__name__}: {exc}"
    report = ctx.evidence.evaluate(run_tag=control.run_tag)
    rules = sorted({v.rule for v in report.violations})
    met = control.signal.met((), rules, harness_failed=bool(error))
    signal = f"oracle: {len(report.violations)} violation(s) ({', '.join(rules) or '-'})"
    if error:
        signal = f"{error} | {signal}"
    elif not met:
        signal = f"not the declared signal: {signal}"
    return ControlResult(
        control.id,
        control.guarantee,
        "planted",
        control.plant,
        "planted rows",
        met,
        signal,
        None,
        len(report.violations),
        declared=control.signal.describe(),
    )

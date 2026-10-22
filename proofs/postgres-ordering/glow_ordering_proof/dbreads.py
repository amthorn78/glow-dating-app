"""What the database says: the reads the cases judge by. Models are imported inside
each function so the case plan stays importable without Django."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from django.db import connection

from glow_ordering_proof.observe import LOG_TABLE, ProofLog


def match_row(match_id: UUID) -> tuple[str, int]:
    from glow_persistence.models import Match

    row = Match.objects.filter(pk=match_id).values_list("state", "contact_version").get()
    return str(row[0]), int(row[1])


def account_row(account_id: UUID) -> tuple[str, int, int]:
    from glow_persistence.models import AppAccount

    row = (
        AppAccount.objects.filter(pk=account_id)
        .values_list("state", "session_epoch", "blocks_version")
        .get()
    )
    return str(row[0]), int(row[1]), int(row[2])


def session_row(session_id: UUID) -> tuple[str, int, datetime]:
    from glow_persistence.models import AccountSession

    row = (
        AccountSession.objects.filter(pk=session_id)
        .values_list("state", "epoch", "expires_at")
        .get()
    )
    return str(row[0]), int(row[1]), row[2]


def block_state(actor: UUID, target: UUID) -> str | None:
    from glow_persistence.models import Block

    row = (
        Block.objects.filter(actor_id=actor, target_id=target)
        .values_list("state", flat=True)
        .first()
    )
    return None if row is None else str(row)


def submissions_of(match_id: UUID) -> list[tuple[UUID, int, str]]:
    from glow_persistence.models import MessageSubmission

    rows = MessageSubmission.objects.filter(binding__match_id=match_id).values_list(
        "id", "contact_version", "idempotency_key"
    )
    return [(row[0], int(row[1]), str(row[2])) for row in rows]


def outbox_count(event_type: str, aggregate_id: UUID) -> int:
    from glow_persistence.models import OutboxEvent

    return int(OutboxEvent.objects.filter(event_type=event_type, aggregate_id=aggregate_id).count())


def submission_commit(submission_id: UUID) -> datetime:
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT pg_xact_commit_timestamp(xmin) FROM glow_persistence_messagesubmission"
            " WHERE id = %s",
            [submission_id],
        )
        value = cursor.fetchone()[0]
    assert isinstance(value, datetime)
    return value


def log_commit(log: ProofLog, kind: str) -> datetime | None:
    """The commit time of the current case's log row of ``kind`` (the latest, if several)."""
    context = log.context
    with connection.cursor() as cursor:
        cursor.execute(
            f"SELECT pg_xact_commit_timestamp(xmin) FROM {LOG_TABLE}"
            " WHERE run_tag = %s AND case_id = %s AND kind = %s ORDER BY id DESC LIMIT 1",
            [context.run_tag, context.case_id, kind],
        )
        row = cursor.fetchone()
    value = row[0] if row else None
    assert value is None or isinstance(value, datetime)
    return value


def profile_row(account_id: UUID, event_type: str) -> tuple[str, int, int]:
    """(the profile's state, its version, how many ``event_type`` events name it)."""
    from glow_persistence.models import OutboxEvent, Profile

    state, version, profile_id = (
        Profile.objects.filter(account_id=account_id).values_list("state", "version", "id").get()
    )
    events = OutboxEvent.objects.filter(event_type=event_type, aggregate_id=profile_id).count()
    return str(state), int(version), int(events)


def consent_row(account_id: UUID) -> tuple[str, int] | None:
    """The latest onboarding consent decision: (state, version), or None."""
    from glow_persistence.models import ConsentDecision

    row = (
        ConsentDecision.objects.filter(account_id=account_id, purpose="onboarding")
        .order_by("-version")
        .values_list("state", "version")
        .first()
    )
    return None if row is None else (str(row[0]), int(row[1]))


def deletion_recorded(account_id: UUID) -> tuple[bool, bool, bool]:
    """(DeletionJob with access revoked, DeletionTombstone, the account row still exists)."""
    from glow_persistence.models import AppAccount, DeletionJob, DeletionTombstone

    return (
        bool(DeletionJob.objects.filter(subject_id=account_id, state="access_revoked").exists()),
        bool(DeletionTombstone.objects.filter(subject_id=account_id).exists()),
        bool(AppAccount.objects.filter(pk=account_id).exists()),
    )


def activation_commit(match_id: UUID) -> datetime | None:
    """P06.2 B1: the commit time of a match's activation, from its ``match_activated``
    outbox event (written in the activation's transaction)."""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT pg_xact_commit_timestamp(xmin) FROM glow_persistence_outboxevent"
            " WHERE event_type = 'match_activated' AND aggregate_id = %s",
            [match_id],
        )
        row = cursor.fetchone()
    value = row[0] if row else None
    assert value is None or isinstance(value, datetime)
    return value


def match_between(low: UUID, high: UUID) -> tuple[UUID, str] | None:
    """P06.2 B1: the pair's match, if one exists: (id, state)."""
    from glow_persistence.models import Match

    row = (
        Match.objects.filter(account_low_id=low, account_high_id=high)
        .values_list("id", "state")
        .first()
    )
    return None if row is None else (row[0], str(row[1]))


def identity_row(account_id: UUID) -> tuple[str, str | None, datetime | None] | None:
    """P06.2 B1: the account's chat identity: (state, reconcile_code, tokens_revoked_before)."""
    from glow_persistence.models import ChatIdentity

    row = (
        ChatIdentity.objects.filter(account_id=account_id)
        .values_list("state", "reconcile_code", "tokens_revoked_before")
        .first()
    )
    return None if row is None else (str(row[0]), row[1], row[2])


def event_times(event_type: str, aggregate_id: UUID) -> tuple[datetime, datetime] | None:
    """P06.2 B1: an outbox event's (available_at, created_at): the database clock the
    writer read under its locks, and the app's clock at the row's save."""
    from glow_persistence.models import OutboxEvent

    row = (
        OutboxEvent.objects.filter(event_type=event_type, aggregate_id=aggregate_id)
        .order_by("-aggregate_version")
        .values_list("available_at", "created_at")
        .first()
    )
    return None if row is None else (row[0], row[1])

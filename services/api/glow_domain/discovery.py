"""Bounded synchronous fixture discovery; no authentication, durable cursor or contact grant."""

import re
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from typing import Literal, Protocol, TypedDict
from uuid import uuid4

from .eligibility import PredicateOutcome
from .eligibility_facts import FixtureEligibilityRepository, _text, age_on
from .fixture_coherence import (
    FixtureReadGuard,
    FixtureRevision,
    acquire_guard,
    capture_revisions,
    guard_is_current,
)
from .identity import AccountId, require_nonblank
from .provider_contracts import FailureCode
from .provider_fixtures import (
    CandidateWork,
    FixtureCompatibilityBatchService,
    require_fixture_environment,
)
from .trusted_eligibility import (
    EligibilityDecisionState,
    EvidenceProblem,
    EvidenceUnavailable,
    PairEvidenceVersion,
)

DiscoveryMode = Literal["recommended", "broader"]
PAGE_SIZE = 2
MAX_CANDIDATES = 20
MAX_QUEUES = 2
QUEUE_LIFETIME_MS = 300_000


def _require_handle(value: str, field: str) -> None:
    if type(value) is not str or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}", value) is None:
        raise ValueError(f"{field} must be a bounded opaque fixture identifier.")


class PublicCompatibility(TypedDict):
    status: Literal["pending"]
    source: Literal["fixture"]


class PublicDiscoveryCard(TypedDict):
    profile_id: str
    display_name: str
    age: int
    summary: str
    compatibility: PublicCompatibility
    media_delivery_refs: list[str]


class DiscoveryPage(TypedDict):
    mode: Literal["fixture"]
    contract_version: Literal["gapp-dev-v1"]
    kind: Literal["discovery_page"]
    viewer_id: str
    session_id: str
    discovery_mode: DiscoveryMode
    queue_id: str | None
    request_id: str
    state: str
    items: list[PublicDiscoveryCard]
    next_cursor: str | None


class FixtureDiscoveryClock:
    """Explicit fixture time, with a retained cell for callback-time changes."""

    def __init__(self, now_ms: int) -> None:
        self._revision = FixtureRevision()
        self.set(now_ms)

    def set(self, now_ms: int) -> None:
        if type(now_ms) is not int or now_ms < 0:
            raise ValueError("Fixture time requires nonnegative integer milliseconds.")
        self._now_ms = now_ms
        self._revision.advance()

    def read(self) -> int:
        return self._now_ms

    def today(self) -> date:
        return datetime.fromtimestamp(self._now_ms / 1000, UTC).date()

    def publication_guard(self) -> FixtureReadGuard:
        return capture_revisions(self._revision)


class FixtureDiscoveryAuthority:
    """Composition-selected fictional actor; identical replacement still revokes queues."""

    def __init__(self, viewer: AccountId, session_id: str) -> None:
        self._revision = FixtureRevision()
        self.replace(viewer, session_id)

    def replace(self, viewer: AccountId | None, session_id: str | None) -> None:
        if (viewer is None) != (session_id is None):
            raise ValueError("Actor and session must be present or absent together.")
        if viewer is not None and not isinstance(viewer, AccountId):
            raise TypeError("Fixture actor requires an application identity.")
        if session_id is not None:
            _require_handle(session_id, "session_id")
        self._viewer, self._session_id = viewer, session_id
        self._revision.advance()

    def read(self) -> tuple[AccountId | None, str | None]:
        return self._viewer, self._session_id

    def publication_guard(self) -> FixtureReadGuard:
        return capture_revisions(self._revision)


@dataclass(frozen=True)
class DiscoveryMember:
    account_id: AccountId
    profile_id: str
    recommendation_priority: int

    def __post_init__(self) -> None:
        if not isinstance(self.account_id, AccountId):
            raise TypeError("Population members require application identities.")
        require_nonblank(self.profile_id, "profile_id")
        if type(self.recommendation_priority) is not int:
            raise TypeError("Synthetic priority requires an integer.")


class FixtureDiscoverySource(FixtureEligibilityRepository):
    """One fact owner projects allowlisted fields, without copied readiness flags.

    Population size is bounded on writes. Fact and media updates use the existing
    participation cells; selecting never scans an unbounded source collection.
    """

    def replace_population(self, members: tuple[DiscoveryMember, ...]) -> None:
        if type(members) is not tuple or len(members) > MAX_CANDIDATES:
            raise ValueError("Development populations permit at most twenty members.")
        if any(type(member) is not DiscoveryMember for member in members):
            raise TypeError("Population members require immutable typed records.")
        if len({member.account_id for member in members}) != len(members) or len(
            {member.profile_id for member in members}
        ) != len(members):
            raise ValueError("Population identities must be distinct.")
        if not hasattr(self, "_population_revision"):
            self._population_revision = FixtureRevision()
        self._members = members
        self._population_revision.advance()

    def select(self, mode: DiscoveryMode) -> tuple[DiscoveryMember, ...]:
        return tuple(
            sorted(
                getattr(self, "_members", ()),
                key=lambda member: (
                    member.recommendation_priority if mode == "recommended" else 0,
                    member.profile_id,
                ),
            )
        )

    def population_guard(self) -> FixtureReadGuard:
        if not hasattr(self, "_population_revision"):
            self.replace_population(())
        return capture_revisions(self._population_revision)

    def project(self, member: DiscoveryMember) -> PublicDiscoveryCard | None:
        facts = self._participants.get(member.account_id)
        if facts is None or facts.profile_id != member.profile_id:
            return None
        day = (
            date.fromisoformat(self._last_day)
            if self._last_day
            not in {
                "unavailable",
                None,
            }
            else None
        )
        age = age_on(facts.birth_date, day)
        if age is None or not 18 <= age <= 120:
            return None
        for value, maximum in (
            (member.profile_id, 100),
            (facts.display_name, 80),
            (facts.summary, 500),
        ):
            if (
                type(value) is not str
                or _text(value) is not PredicateOutcome.PASS
                or len(value) > maximum
            ):
                return None
            if any(0xD800 <= ord(character) <= 0xDFFF for character in value):
                return None
        if facts.display_name is None or facts.summary is None:
            return None
        references = [
            media.delivery_ref
            for media in facts.approved_media or ()
            if media.owner_id == member.account_id
            and media.profile_id == member.profile_id
            and media.generation == facts.generation
            and media.state == "approved"
            and self._policy is not None
            and media.policy_version == self._policy.media_version
            and type(media.delivery_ref) is str
            and len(media.delivery_ref) <= 128
            and re.fullmatch(r"fixture-approved-[A-Za-z0-9_-]+", media.delivery_ref)
        ]
        if not 1 <= len(references) <= 4 or len(set(references)) != len(references):
            return None
        return {
            "profile_id": member.profile_id,
            "display_name": facts.display_name,
            "age": age,
            "summary": facts.summary,
            "compatibility": {"status": "pending", "source": "fixture"},
            "media_delivery_refs": references,
        }


def _capture_card(value: object, member: DiscoveryMember) -> PublicDiscoveryCard | None:
    """Closed immutable-value capture before the final guards; no caller getters."""
    if (
        type(value) is not dict
        or any(type(key) is not str for key in value)
        or set(value)
        != {
            "profile_id",
            "display_name",
            "age",
            "summary",
            "compatibility",
            "media_delivery_refs",
        }
    ):
        return None
    for name, maximum in (("profile_id", 100), ("display_name", 80), ("summary", 500)):
        text = value[name]
        if (
            type(text) is not str
            or _text(text) is not PredicateOutcome.PASS
            or len(text) > maximum
            or any(0xD800 <= ord(character) <= 0xDFFF for character in text)
        ):
            return None
    if value["profile_id"] != member.profile_id:
        return None
    compatibility = value["compatibility"]
    if (
        type(compatibility) is not dict
        or any(type(key) is not str for key in compatibility)
        or any(type(item) is not str for item in compatibility.values())
        or set(compatibility) != {"status", "source"}
        or (compatibility != {"status": "pending", "source": "fixture"})
    ):
        return None
    age, media = value["age"], value["media_delivery_refs"]
    if (
        type(age) is not int
        or not 18 <= age <= 120
        or type(media) is not list
        or not 1 <= len(media) <= 4
    ):
        return None
    if any(
        type(ref) is not str
        or len(ref) > 128
        or re.fullmatch(
            r"fixture-approved-[A-Za-z0-9_-]+",
            ref,
        )
        is None
        for ref in media
    ) or len(set(media)) != len(media):
        return None
    return {
        "profile_id": value["profile_id"],
        "display_name": value["display_name"],
        "age": age,
        "summary": value["summary"],
        "media_delivery_refs": list(media),
        "compatibility": {"status": "pending", "source": "fixture"},
    }


@dataclass(frozen=True)
class _MemberCapture:
    member: DiscoveryMember
    version: PairEvidenceVersion
    facts_guard: FixtureReadGuard
    mapping_guard: FixtureReadGuard


@dataclass
class _Queue:
    queue_id: str
    viewer: AccountId
    session_id: str
    mode: DiscoveryMode
    expires_at: int
    members: tuple[_MemberCapture, ...]
    guards: tuple[FixtureReadGuard, ...]
    bindings: tuple[object, ...]
    cursors: dict[int, str] = field(default_factory=dict)
    valid: bool = True


class DiscoveryConsumption(Protocol):
    """App interaction state; its retained revision participates in queue freshness."""

    def publication_guard(self, viewer: AccountId) -> FixtureReadGuard: ...

    def excludes(self, viewer: AccountId, candidate: AccountId) -> bool: ...


class FixtureDiscoveryService:
    """Two finite mode queues; explicit refresh, repeatable opaque page handles.

    Caller owns mode-specific page progress. No cursor repeats page one; a cursor
    repeats its page. Replays reacquire authorization and never advance state.
    Changes require explicit refresh. No public projections are cached.
    """

    def __init__(
        self,
        *,
        environment: str,
        source: FixtureDiscoverySource,
        batch: FixtureCompatibilityBatchService,
        authority: FixtureDiscoveryAuthority,
        clock: FixtureDiscoveryClock,
        consumption: DiscoveryConsumption | None = None,
    ) -> None:
        require_fixture_environment(environment)
        if batch.eligibility.repository is not source:
            raise ValueError("Discovery and eligibility must share their fact source.")
        self.environment, self.source, self.batch = environment, source, batch
        self.authority, self.clock = authority, clock
        self.consumption = consumption
        self._queues: dict[DiscoveryMode, _Queue] = {}

    def page(
        self,
        *,
        viewer: AccountId,
        session_id: str,
        mode: DiscoveryMode,
        request_id: str,
        cursor: str | None = None,
        refresh: bool = False,
    ) -> DiscoveryPage:
        require_fixture_environment(self.environment)
        if type(viewer) is not AccountId or mode not in {"recommended", "broader"}:
            raise ValueError("Discovery requires a typed actor and supported mode.")
        _require_handle(session_id, "session_id")
        _require_handle(request_id, "request_id")
        if (
            type(viewer.value) is not str
            or _text(viewer.value) is not PredicateOutcome.PASS
            or not 1 <= len(viewer.value) <= 100
            or any(0xD800 <= ord(character) <= 0xDFFF for character in viewer.value)
        ):
            raise ValueError("Discovery actor must fit the public identity contract.")
        if type(refresh) is not bool or (cursor is not None and type(cursor) is not str):
            raise TypeError("Discovery controls require their exact declared types.")
        if refresh and cursor is not None:
            raise ValueError("Refresh cannot continue an old queue.")
        response: DiscoveryPage = {
            "mode": "fixture",
            "contract_version": "gapp-dev-v1",
            "kind": "discovery_page",
            "viewer_id": viewer.value,
            "session_id": session_id,
            "discovery_mode": mode,
            "queue_id": None,
            "request_id": request_id,
            "state": "reload_required",
            "items": [],
            "next_cursor": None,
        }
        request_bindings = self._bindings()
        if self.batch.eligibility.repository is not self.source:
            return response
        authority_guard, time_guard = acquire_guard(self.authority), acquire_guard(self.clock)
        now = self.clock.read()  # exactly one numeric lifetime observation per request
        identity = self.authority.read()
        if type(now) is not int or now < 0:
            return response
        if authority_guard is None or time_guard is None or identity != (viewer, session_id):
            self._queues.clear()
            return response
        if not guard_is_current(authority_guard) or not guard_is_current(time_guard):
            self._queues.clear()
            return response
        queue = self._queues.get(mode)
        if refresh:
            queue = None
            self._queues.pop(mode, None)
        if queue is None:
            if cursor is not None:
                return response
            queue = self._new_queue(viewer, session_id, mode, now, authority_guard, time_guard)
            if queue is None:
                return response
            self._queues[mode] = queue
        response["queue_id"] = queue.queue_id
        if any(old is not new for old, new in zip(request_bindings, self._bindings(), strict=True)):
            queue.valid = False
            return response
        if (queue.viewer, queue.session_id) != (viewer, session_id):
            self._queues.clear()
            return response
        if (
            not queue.valid
            or not self._bindings_current(queue)
            or now >= queue.expires_at
            or not all(guard_is_current(guard) for guard in queue.guards)
            or not all(self._member_current(member) for member in queue.members)
        ):
            queue.valid = False
            return response
        offset = 0
        if cursor is not None:
            matched = [index for index, token in queue.cursors.items() if token == cursor]
            if len(matched) != 1:
                return response
            offset = matched[0]
        if offset >= len(queue.members):
            if not guard_is_current(time_guard) or not guard_is_current(authority_guard):
                queue.valid = False
                return response
            response["state"] = "empty" if not queue.members else "exhausted"
            return response
        selected = queue.members[offset : offset + PAGE_SIZE]
        work = tuple(
            CandidateWork(item.member.account_id, f"{queue.queue_id}-{offset + index}")
            for index, item in enumerate(selected)
        )
        result = self.batch.evaluate(viewer, work)
        projected: list[tuple[_MemberCapture, PublicDiscoveryCard]] = []
        partial = False
        for captured, outcome in zip(selected, result.entries, strict=True):
            # Only transient provider failures retain an eligible pending card. Stale,
            # absent or mismatched mappings/guards never get a projection.
            if outcome.state not in {"evaluated", "failed"}:
                partial = True
                continue
            if outcome.state == "failed" and (
                outcome.compatibility is None
                or outcome.compatibility.failure
                not in {
                    FailureCode.TIMEOUT,
                    FailureCode.OUTAGE,
                }
            ):
                partial = True
                continue
            card = _capture_card(self.source.project(captured.member), captured.member)
            current = self.batch.eligibility.evaluate(
                viewer,
                captured.member.account_id,
                captured.version,
            )
            if card is None or current.state is not EligibilityDecisionState.READY:
                partial = True
                continue
            if (
                outcome.compatibility is None
                or outcome.compatibility.output is None
                or (
                    outcome.compatibility.output.result.status.value
                    in {"unavailable", "unsupported"}
                )
            ):
                partial = True
            projected.append((captured, card))
        # All callbacks finish above: projection and clock-capable eligibility.
        # Only concrete cells and owned primitive DTOs are used below.
        shared_current = (
            self._bindings_current(queue)
            and guard_is_current(authority_guard)
            and guard_is_current(time_guard)
            and all(guard_is_current(guard) for guard in queue.guards)
        )
        items = [
            card for member, card in projected if shared_current and self._member_current(member)
        ]
        all_current = shared_current and all(
            self._member_current(member) for member in queue.members
        )
        if not all_current:
            queue.valid = False
            response["state"] = "partial" if items else "reload_required"
            response["items"] = items
            return response
        response["items"] = items
        response["state"] = "partial" if partial else "ready"
        next_offset = offset + len(selected)
        if next_offset < len(queue.members):
            if next_offset not in queue.cursors:
                queue.cursors[next_offset] = uuid4().hex
            response["next_cursor"] = queue.cursors[next_offset]
        return response

    def _bindings(self) -> tuple[object, ...]:
        return (
            self.source,
            self.batch,
            self.batch.eligibility.repository,
            self.batch.mappings,
            self.batch.provider,
            self.authority,
            self.clock,
            self.consumption,
        )

    def _bindings_current(self, queue: _Queue) -> bool:
        return all(old is new for old, new in zip(queue.bindings, self._bindings(), strict=True))

    @staticmethod
    def _member_current(member: _MemberCapture) -> bool:
        return guard_is_current(member.facts_guard) and guard_is_current(member.mapping_guard)

    def _new_queue(
        self,
        viewer: AccountId,
        session_id: str,
        mode: DiscoveryMode,
        now: int,
        authority_guard: FixtureReadGuard,
        time_guard: FixtureReadGuard,
    ) -> _Queue | None:
        callback = getattr(self.source, "population_guard", None)
        try:
            population_guard = callback() if callable(callback) else None
        except EvidenceUnavailable:
            population_guard = None
        if not guard_is_current(population_guard):
            return None
        if type(population_guard) is not FixtureReadGuard:
            return None
        consumption_guard = acquire_guard(self.consumption, viewer) if self.consumption else None
        if self.consumption is not None and consumption_guard is None:
            return None
        members = self.source.select(mode)
        if (
            type(members) is not tuple
            or len(members) > MAX_CANDIDATES
            or any(type(member) is not DiscoveryMember for member in members)
        ):
            return None
        if len({member.account_id for member in members}) != len(members):
            return None
        retained: list[_MemberCapture] = []
        excluded_guards: list[FixtureReadGuard] = []
        for member in members:
            if self.consumption is not None and self.consumption.excludes(
                viewer, member.account_id
            ):
                continue
            decision = self.batch.eligibility.evaluate(viewer, member.account_id)
            if decision.problem is EvidenceProblem.POLICY_PENDING:
                return None
            facts_guard = acquire_guard(self.source, viewer, member.account_id)
            if facts_guard is None:
                return None
            if (
                decision.state is not EligibilityDecisionState.READY
                or decision.evidence_version is None
            ):
                excluded_guards.append(facts_guard)
                continue
            mapping_guard = acquire_guard(self.batch.mappings, viewer, member.account_id)
            if mapping_guard is None:
                return None
            current = self.batch.eligibility.evaluate(
                viewer, member.account_id, decision.evidence_version
            )
            if current.state is not EligibilityDecisionState.READY:
                excluded_guards.append(facts_guard)
                continue
            retained.append(
                _MemberCapture(member, decision.evidence_version, facts_guard, mapping_guard)
            )
        return _Queue(
            uuid4().hex,
            viewer,
            session_id,
            mode,
            now + QUEUE_LIFETIME_MS,
            tuple(retained),
            (
                authority_guard,
                time_guard,
                population_guard,
                *excluded_guards,
                *((consumption_guard,) if consumption_guard else ()),
            ),
            self._bindings(),
        )

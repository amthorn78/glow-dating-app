"""P05.3 internal fixture commands: guarded memory swaps, never HTTP/SQL/contact.

Composition supplies session, registry, source and store. Immutable receipts are
separate from freshly authorized projections. External reads finish before a
concrete revision comparison and single owned-state replacement.
"""

import hashlib
import json
import re
from collections.abc import Callable
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any
from uuid import uuid4

from .discovery import DiscoveryMode, DiscoveryPage, FixtureDiscoveryService
from .fixture_coherence import (
    FixtureReadGuard,
    FixtureRevision,
    acquire_guard,
    capture_revisions,
    guard_is_current,
)
from .identity import AccountId
from .provider_fixtures import require_fixture_environment
from .trusted_eligibility import EligibilityDecisionState

MAX_VERSION = 9_007_199_254_740_991
MAX_RECEIPTS = 200
MAX_EVENTS = 200
MAX_IDENTITIES = 20
# At most 190 unordered pairs can each incur one system revocation.
MAX_REVOCATIONS = MAX_IDENTITIES * (MAX_IDENTITIES - 1) // 2
UUID_PATTERN = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
CORPUS = Path(__file__).resolve().parents[3] / "packages/contracts/fixtures/interactions-v1.json"


@dataclass(frozen=True)
class FixtureIdentity:
    account_id: AccountId
    profile_id: str
    account_uuid: str
    profile_uuid: str


class FixtureIdentityRegistry:
    """Bounded app-owned mapping, never accepted from a command payload."""

    def __init__(self, identities: tuple[FixtureIdentity, ...]) -> None:
        self._revision = FixtureRevision()
        self.replace(identities)

    def replace(self, identities: tuple[FixtureIdentity, ...]) -> None:
        if type(identities) is not tuple or not 1 <= len(identities) <= MAX_IDENTITIES:
            raise ValueError("A bounded fixture identity table is required.")
        if any(type(row) is not FixtureIdentity for row in identities):
            raise ValueError("Fixture identities require typed immutable records.")
        for row in identities:
            if type(row.account_id) is not AccountId or type(row.profile_id) is not str:
                raise ValueError("Invalid fixture identity.")
            if any(
                type(value) is not str or UUID_PATTERN.fullmatch(value) is None
                for value in (row.account_uuid, row.profile_uuid)
            ):
                raise ValueError("Fixture bridge UUIDs must satisfy production identifiers.")
        for attribute in ("account_id", "profile_id", "account_uuid", "profile_uuid"):
            if len({getattr(row, attribute) for row in identities}) != len(identities):
                raise ValueError("Ambiguous fixture identity table.")
        if {row.account_uuid for row in identities} & {row.profile_uuid for row in identities}:
            raise ValueError("Account and profile identities must differ.")
        self.identities = identities
        self._revision.advance()

    def account(self, identity: AccountId) -> FixtureIdentity | None:
        return next((row for row in self.identities if row.account_id == identity), None)

    def profile(self, identity: str) -> FixtureIdentity | None:
        return next((row for row in self.identities if row.profile_uuid == identity), None)

    def publication_guard(self) -> FixtureReadGuard:
        return capture_revisions(self._revision)


def load_identity_registry() -> FixtureIdentityRegistry:
    corpus = json.loads(CORPUS.read_text())
    return FixtureIdentityRegistry(
        tuple(
            FixtureIdentity(**{**row, "account_id": AccountId(row["account_id"])})
            for row in corpus["identities"]
        )
    )


@dataclass(frozen=True)
class Direction:
    object_id: str
    actor: AccountId
    target: AccountId
    state: str
    version: int
    guards: tuple[FixtureReadGuard, ...]
    bindings: tuple[object, ...]
    matchable: bool = True


@dataclass(frozen=True)
class Match:
    match_id: str
    pair: tuple[str, str]
    participants: tuple[AccountId, AccountId]
    state: str
    version: int
    guards: tuple[FixtureReadGuard, ...]
    bindings: tuple[object, ...]


@dataclass(frozen=True)
class Block:
    object_id: str
    actor: AccountId
    target: AccountId
    state: str
    version: int


@dataclass(frozen=True)
class Receipt:
    digest: str
    outcome_code: str
    object_ref: str
    committed_version: int
    target: AccountId

    def public(self) -> dict[str, Any]:
        return {
            "outcome_code": self.outcome_code,
            "object_ref": self.object_ref,
            "committed_version": self.committed_version,
        }


@dataclass(frozen=True)
class LogicalEvent:
    event_id: str
    kind: str
    aggregate_id: str
    aggregate_version: int
    contract_version: str = "gapp-interactions-fixture-v1"

    def public(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "kind": self.kind,
            "aggregate_id": self.aggregate_id,
            "aggregate_version": self.aggregate_version,
            "contract_version": self.contract_version,
        }


@dataclass(frozen=True)
class _State:
    directions: dict[tuple[AccountId, AccountId], Direction] = field(default_factory=dict)
    matches: dict[tuple[str, str], Match] = field(default_factory=dict)
    blocks: dict[tuple[AccountId, AccountId], Block] = field(default_factory=dict)
    receipts: dict[tuple[AccountId, str, str], Receipt] = field(default_factory=dict)
    events: tuple[LogicalEvent, ...] = ()
    discretionary_events: int = 0


class FixtureInteractionRepository:
    """One process-local unit of work. Capacity refuses; no receipt eviction."""

    def __init__(self, *, environment: str) -> None:
        require_fixture_environment(environment)
        self._revision = FixtureRevision()
        self._state = _State()
        self._consumption_revisions: dict[AccountId, FixtureRevision] = {}
        self._pending: dict[tuple[AccountId, str, str], str] = {}

    def publication_guard(self, viewer: AccountId | None = None) -> FixtureReadGuard:
        if viewer is None:
            # Commands retain the global unit-of-work revision to avoid lost writes.
            return capture_revisions(self._revision)
        if viewer not in self._consumption_revisions:
            self._consumption_revisions[viewer] = FixtureRevision()
        return capture_revisions(self._consumption_revisions[viewer])

    @staticmethod
    def _exclusions(state: _State) -> dict[AccountId, set[AccountId]]:
        excluded: dict[AccountId, set[AccountId]] = {}
        for actor, target in state.directions:
            excluded.setdefault(actor, set()).add(target)
        for match in state.matches.values():
            actor, target = match.participants
            excluded.setdefault(actor, set()).add(target)
            excluded.setdefault(target, set()).add(actor)
        for block in state.blocks.values():
            if block.state == "active":
                excluded.setdefault(block.actor, set()).add(block.target)
                excluded.setdefault(block.target, set()).add(block.actor)
        return excluded

    def _consumption_changes(self, staged: _State) -> tuple[AccountId, ...]:
        """Stage only observers whose discovery exclusions will actually change."""
        before, after = self._exclusions(self._state), self._exclusions(staged)
        return tuple(
            viewer
            for viewer in before.keys() | after.keys()
            if before.get(viewer, set()) != after.get(viewer, set())
        )

    def blocked(self, actor: AccountId, target: AccountId) -> bool:
        return any(
            row is not None and row.state == "active"
            for row in (
                self._state.blocks.get((actor, target)),
                self._state.blocks.get((target, actor)),
            )
        )

    def excludes(self, viewer: AccountId, candidate: AccountId) -> bool:
        return (
            (viewer, candidate) in self._state.directions
            or self.blocked(viewer, candidate)
            or any(
                viewer in match.participants and candidate in match.participants
                for match in self._state.matches.values()
            )
        )

    @property
    def counts(self) -> dict[str, int]:
        state = self._state
        return {
            "directions": len(state.directions),
            "matches": len(state.matches),
            "blocks": len(state.blocks),
            "receipts": len(state.receipts),
            "events": len(state.events),
            "pending": len(self._pending),
        }

    @property
    def events(self) -> tuple[LogicalEvent, ...]:
        return self._state.events


@dataclass(frozen=True)
class ActionBatch:
    batch_id: str
    version: int
    queue_id: str
    mode: DiscoveryMode
    viewer: AccountId
    session_id: str
    profile_ids: tuple[str, ...]
    registry_guard: FixtureReadGuard
    registry: FixtureIdentityRegistry


@dataclass(frozen=True)
class CommandResult:
    code: str
    value: dict[str, Any] | None = None


def _capture_intent(value: object) -> dict[str, Any] | None:
    """Exact-type closed production decoder, compared with shared schema tests."""
    if type(value) is not dict or any(type(key) is not str for key in value):
        return None
    operation = value.get("operation")
    if type(operation) is not str or operation not in {"interaction", "unmatch", "block"}:
        return None
    fields = (
        {"operation", "meta"}
        | ({"match_id"} if operation == "unmatch" else {"target_profile_id", "action"})
        | ({"batch_id", "batch_version"} if operation == "interaction" else set())
    )
    if set(value) != fields:
        return None
    meta = value["meta"]
    if (
        type(meta) is not dict
        or any(type(key) is not str for key in meta)
        or set(meta) != {"idempotency_key", "expected_version"}
    ):
        return None
    key, version = meta["idempotency_key"], meta["expected_version"]
    if (
        type(key) is not str
        or not 1 <= len(key) <= 100
        or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]*", key) is None
        or type(version) is not int
        or not 0 <= version <= MAX_VERSION
    ):
        return None
    for name in ("match_id", "target_profile_id", "batch_id"):
        if name in value and (
            type(value[name]) is not str or UUID_PATTERN.fullmatch(value[name]) is None
        ):
            return None
    if operation == "interaction" and (
        type(value["batch_version"]) is not int
        or not 1 <= value["batch_version"] <= MAX_VERSION
        or type(value["action"]) is not str
        or value["action"] not in {"like", "pass"}
    ):
        return None
    if operation == "block" and (
        type(value["action"]) is not str or value["action"] not in {"block", "unblock"}
    ):
        return None
    return {**value, "meta": dict(meta)}


class FixtureInteractionService:
    """Session-bound interaction composition; commands never choose their actor."""

    def __init__(
        self,
        *,
        environment: str,
        discovery: FixtureDiscoveryService,
        registry: FixtureIdentityRegistry,
        repository: FixtureInteractionRepository,
        policy_version: str | None = "development-interactions-1",
    ) -> None:
        require_fixture_environment(environment)
        self.discovery, self.registry, self.repository = discovery, registry, repository
        self._policy_revision = FixtureRevision()
        self.environment, self.policy_version = environment, policy_version
        discovery.consumption = repository
        self._batches: dict[DiscoveryMode, ActionBatch] = {}
        self.before_commit: Callable[[], None] = lambda: None

    @property
    def policy_version(self) -> str | None:
        return self._policy_version

    @policy_version.setter
    def policy_version(self, value: str | None) -> None:
        if value is not None and type(value) is not str:
            raise ValueError("Interaction policy requires an explicit version or absence.")
        self._policy_version = value
        self._policy_revision.advance()

    def _authority_bindings(self) -> tuple[object, ...]:
        return (
            self.registry,
            self.discovery.source,
            self.discovery.batch.mappings,
            self.discovery.batch.eligibility.repository,
            self.repository,
            self.discovery.clock,
        )

    def _authority_current(self, bindings: tuple[object, ...]) -> bool:
        return all(
            old is new for old, new in zip(bindings, self._authority_bindings(), strict=True)
        )

    def page(
        self,
        *,
        mode: DiscoveryMode,
        request_id: str,
        cursor: str | None = None,
        refresh: bool = False,
    ) -> tuple[DiscoveryPage, ActionBatch | None]:
        actor, session = self.discovery.authority.read()
        if actor is None or session is None:
            raise ValueError("No trusted fixture session.")
        registry = self.registry
        registry_guard = registry.publication_guard()
        page = self.discovery.page(
            viewer=actor,
            session_id=session,
            mode=mode,
            request_id=request_id,
            cursor=cursor,
            refresh=refresh,
        )
        queue_id = page["queue_id"]
        if (
            queue_id is None
            or page["state"] not in {"ready", "partial"}
            or not guard_is_current(registry_guard)
            or self.registry is not registry
        ):
            self._batches.pop(mode, None)
            return page, None
        previous = self._batches.get(mode)
        batch_id = previous.batch_id if previous and previous.queue_id == queue_id else str(uuid4())
        allowed = tuple(
            row.profile_uuid
            for card in page["items"]
            for row in self.registry.identities
            if row.profile_id == card["profile_id"]
        )
        batch = ActionBatch(
            batch_id, 1, queue_id, mode, actor, session, allowed, registry_guard, registry
        )
        self._batches[mode] = batch
        return page, batch

    def _actor(self) -> tuple[AccountId, str] | None:
        actor, session = self.discovery.authority.read()
        if actor is None or session is None:
            return None
        identity = self.registry.account(actor)
        if identity is None or not self._target_current(identity):
            return None
        facts = self.discovery.source._participants.get(actor)
        if (
            facts is None
            or facts.session_state != "valid"
            or facts.account_state not in {"active", "suspended", "deletion_pending"}
        ):
            return None
        return actor, session

    def _target_current(self, target: FixtureIdentity) -> bool:
        facts = self.discovery.source._participants.get(target.account_id)
        return (
            facts is not None
            and facts.account_state != "deleted"
            and facts.profile_id == target.profile_id
            and sum(
                person.profile_id == target.profile_id
                for person in self.discovery.source._participants.values()
            )
            == 1
        )

    def _bindings(self) -> tuple[object, ...]:
        return (
            self.discovery,
            self.registry,
            self.repository,
            self.discovery.source,
            self.discovery.batch,
            self.discovery.batch.eligibility,
            self.discovery.batch.eligibility.repository,
            self.discovery.batch.mappings,
            self.discovery.authority,
            self.discovery.clock,
            self.discovery.consumption,
            self.policy_version,
        )

    def _pair(self, actor: AccountId, target: AccountId) -> tuple[str, str] | None:
        first, second = self.registry.account(actor), self.registry.account(target)
        if first is None or second is None:
            return None
        left, right = sorted((first.account_uuid, second.account_uuid))
        return left, right

    def _match(self, match_id: str) -> Match | None:
        return next(
            (m for m in self.repository._state.matches.values() if m.match_id == match_id), None
        )

    def _match_between(self, actor: AccountId, target: AccountId) -> Match | None:
        """Existing aggregates retain their pair key across registry incarnations."""
        return next(
            (
                match
                for match in self.repository._state.matches.values()
                if actor in match.participants and target in match.participants
            ),
            None,
        )

    def _guards(
        self, actor: AccountId, target: AccountId, *, mappings: bool = True
    ) -> tuple[FixtureReadGuard, ...] | None:
        guards = (
            acquire_guard(self.discovery.authority),
            acquire_guard(self.discovery.clock),
            acquire_guard(self.registry),
            acquire_guard(self.repository),
            acquire_guard(self.discovery.source, actor, target),
            (
                acquire_guard(self.discovery.batch.mappings, actor, target)
                if mappings
                else capture_revisions(self.repository._revision)
            ),
        )
        if any(guard is None for guard in guards):
            return None
        return tuple(guard for guard in guards if guard is not None)

    def _batch_guards(
        self,
        intent: dict[str, Any],
        actor: AccountId,
        session: str,
        target: FixtureIdentity,
        mode: DiscoveryMode,
    ) -> tuple[FixtureReadGuard, ...] | None:
        batch = self._batches.get(mode)
        queue = self.discovery._queues.get(mode)
        now = self.discovery.clock.read()
        if (
            batch is None
            or queue is None
            or type(now) is not int
            or batch.batch_id != intent["batch_id"]
            or batch.version != intent["batch_version"]
            or batch.registry is not self.registry
            or batch.viewer != actor
            or batch.session_id != session
            or target.profile_uuid not in batch.profile_ids
            or queue.queue_id != batch.queue_id
            or not queue.valid
            or now >= queue.expires_at
            or not self.discovery._bindings_current(queue)
        ):
            return None
        member = next(
            (
                m
                for m in queue.members
                if m.member.account_id == target.account_id
                and m.member.profile_id == target.profile_id
            ),
            None,
        )
        if member is None:
            return None
        guards = (*queue.guards, member.facts_guard, member.mapping_guard, batch.registry_guard)
        return guards if all(guard_is_current(guard) for guard in guards) else None

    def command(self, raw: object, *, mode: DiscoveryMode = "recommended") -> CommandResult:
        require_fixture_environment(self.environment)
        intent = _capture_intent(raw)
        if intent is None or mode not in {"recommended", "broader"}:
            return CommandResult("invalid_request")
        bindings = self._bindings()
        authority_guard = acquire_guard(self.discovery.authority)
        actor_context = self._actor()
        if actor_context is None or not guard_is_current(authority_guard):
            return CommandResult("unavailable")
        actor, session = actor_context
        operation = intent["operation"]
        match = self._match(intent["match_id"]) if operation == "unmatch" else None
        if operation == "unmatch":
            if match is None or actor not in match.participants:
                return CommandResult("unavailable")
            other = next(person for person in match.participants if person != actor)
            target = self.registry.account(other)
        else:
            target = self.registry.profile(intent["target_profile_id"])
        if target is None or target.account_id == actor:
            return CommandResult("unavailable")
        # Unmatch remains available when target facts/visibility are unavailable.
        if operation != "unmatch" and not self._target_current(target):
            return CommandResult("unavailable")
        pair = match.pair if match is not None else self._pair(actor, target.account_id)
        guards = self._guards(actor, target.account_id, mappings=operation == "interaction")
        if pair is None or guards is None:
            return CommandResult("unavailable")
        guards = (authority_guard, *guards) if authority_guard else guards
        guards = (*guards, capture_revisions(self._policy_revision))
        key = (actor, operation, intent["meta"]["idempotency_key"])
        canonical = json.dumps(
            {**intent, "meta": {"expected_version": intent["meta"]["expected_version"]}},
            sort_keys=True,
            separators=(",", ":"),
        )
        digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        old_receipt = self.repository._state.receipts.get(key)
        pending = self.repository._pending.get(key)
        if (old_receipt is not None and old_receipt.digest != digest) or (
            pending is not None and pending != digest
        ):
            return CommandResult("idempotency_conflict")
        if old_receipt is not None:
            return self._result(actor, target, operation, old_receipt, replayed=True)
        if pending is not None:
            return CommandResult("in_progress")
        if len(self.repository._state.receipts) + len(self.repository._pending) >= MAX_RECEIPTS:
            return CommandResult("capacity_exceeded")
        pending_repository = self.repository
        pending_repository._pending[key] = digest
        try:
            state = self.repository._state
            directions, matches, blocks = (
                dict(state.directions),
                dict(state.matches),
                dict(state.blocks),
            )
            events = list(state.events)
            expected = intent["meta"]["expected_version"]
            if operation == "interaction":
                if self.policy_version != "development-interactions-1":
                    return CommandResult("policy_unresolved")
                current = directions.get((actor, target.account_id))
                if expected != (current.version if current else 0):
                    return CommandResult("stale_version")
                action_state = "liked" if intent["action"] == "like" else "passed"
                if current and current.state != action_state:
                    return CommandResult(
                        "policy_unresolved" if current.state == "passed" else "state_conflict"
                    )
                if pair in matches or self._match_between(actor, target.account_id) is not None:
                    return CommandResult("policy_unresolved")
                batch_guards = self._batch_guards(intent, actor, session, target, mode)
                if batch_guards is None:
                    return CommandResult("stale_batch")
                guards = (*guards, *batch_guards)
                if self.repository.blocked(actor, target.account_id):
                    return CommandResult("unavailable")
                if self.discovery.batch.eligibility.repository is not self.discovery.source:
                    return CommandResult("unavailable")
                decision = self.discovery.batch.eligibility.evaluate(actor, target.account_id)
                if decision.state is not EligibilityDecisionState.READY:
                    return CommandResult("unavailable")
                # Source/registry/mapping cells survive after session/queue consumption.
                durable_guards = (guards[2], guards[3], guards[5], guards[6], guards[7])
                row = current or Direction(
                    str(uuid4()),
                    actor,
                    target.account_id,
                    action_state,
                    1,
                    durable_guards,
                    self._authority_bindings(),
                )
                directions[(actor, target.account_id)] = row
                reciprocal = directions.get((target.account_id, actor))
                if (
                    row.state == "liked"
                    and row.matchable
                    and reciprocal
                    and reciprocal.state == "liked"
                    and reciprocal.matchable
                    and self._authority_current(reciprocal.bindings)
                    and all(guard_is_current(guard) for guard in reciprocal.guards)
                ):
                    match = Match(
                        str(uuid4()),
                        pair,
                        (actor, target.account_id),
                        "active",
                        1,
                        (*row.guards, *reciprocal.guards, *durable_guards),
                        self._authority_bindings(),
                    )
                    matches[pair] = match
                    events.append(LogicalEvent(str(uuid4()), "match_created", match.match_id, 1))
                receipt = Receipt(digest, row.state, row.object_id, row.version, target.account_id)
            elif operation == "unmatch":
                assert match is not None
                if expected != match.version:
                    return CommandResult("stale_version")
                version = match.version + (match.state != "unmatched")
                if version > MAX_VERSION:
                    return CommandResult("capacity_exceeded")
                if match.state != "unmatched":
                    match = replace(match, state="unmatched", version=version)
                    matches[match.pair] = match
                    events.append(
                        LogicalEvent(str(uuid4()), "contact_revoked", match.match_id, version)
                    )
                receipt = Receipt(digest, "unmatched", match.match_id, version, target.account_id)
            else:
                block = blocks.get((actor, target.account_id))
                if expected != (block.version if block else 0):
                    return CommandResult("stale_version")
                action_state = "active" if intent["action"] == "block" else "removed"
                if action_state == "removed" and (block is None or block.state == "removed"):
                    return CommandResult("state_conflict")
                changed = block is None or block.state != action_state
                version = (block.version if block else 0) + changed
                if version > MAX_VERSION:
                    return CommandResult("capacity_exceeded")
                block = Block(
                    block.object_id if block else str(uuid4()),
                    actor,
                    target.account_id,
                    action_state,
                    version,
                )
                blocks[(actor, target.account_id)] = block
                if changed:
                    events.append(
                        LogicalEvent(str(uuid4()), "block_changed", block.object_id, version)
                    )
                if action_state == "active":
                    for direction_key in ((actor, target.account_id), (target.account_id, actor)):
                        previous_direction = directions.get(direction_key)
                        if previous_direction:
                            directions[direction_key] = replace(previous_direction, matchable=False)
                existing = self._match_between(actor, target.account_id)
                if action_state == "active" and existing and existing.state == "active":
                    if existing.version >= MAX_VERSION:
                        return CommandResult("capacity_exceeded")
                    existing = replace(existing, state="restricted", version=existing.version + 1)
                    matches[existing.pair] = existing
                    events.append(
                        LogicalEvent(
                            str(uuid4()), "contact_revoked", existing.match_id, existing.version
                        )
                    )
                receipt = Receipt(
                    digest,
                    "blocked" if action_state == "active" else "unblocked",
                    block.object_id,
                    version,
                    target.account_id,
                )
            event_count = state.discretionary_events + len(events) - len(state.events)
            if event_count > MAX_EVENTS:
                return CommandResult("capacity_exceeded")
            receipts = {**state.receipts, key: receipt}
            staged = _State(directions, matches, blocks, receipts, tuple(events), event_count)
            consumption_changes = self.repository._consumption_changes(staged)
            self.before_commit()
            # Last callback above; final comparison invokes no source or clock.
            if any(
                old is not new for old, new in zip(bindings, self._bindings(), strict=True)
            ) or not all(guard_is_current(guard) for guard in guards):
                return CommandResult("stale_version")
            self.repository._state = staged
            self.repository._revision.advance()
            for viewer in consumption_changes:
                # An observer may have registered during the last callback.
                revision = self.repository._consumption_revisions.get(viewer)
                if revision is not None:
                    revision.advance()
        finally:
            pending_repository._pending.pop(key, None)
        return self._result(actor, target, operation, receipt, replayed=False)

    def _refresh_match(self, match: Match) -> Match:
        """Relevant source incarnation changes permanently restrict active matches."""
        if match.state != "active":
            return match
        actor, target = match.participants
        bindings = self._bindings()
        guard = self.repository.publication_guard()
        source_guard = acquire_guard(self.discovery.source, actor, target)
        decision = self.discovery.batch.eligibility.evaluate(actor, target)
        valid = (
            self.policy_version == "development-interactions-1"
            and decision.state is EligibilityDecisionState.READY
            and not self.repository.blocked(actor, target)
            and all(guard_is_current(item) for item in match.guards)
            and self._authority_current(match.bindings)
            and guard_is_current(source_guard)
        )
        if any(old is not new for old, new in zip(bindings, self._bindings(), strict=True)):
            return replace(match, state="restricted")
        if not guard_is_current(guard):
            return self._match(match.match_id) or replace(match, state="restricted")
        if valid:
            return match
        if match.version >= MAX_VERSION:
            # Cannot publish a same-version state transition or wrap a revision.
            # The retained mismatch still denies every projection/contact read.
            return replace(match, state="restricted")
        updated = replace(match, state="restricted", version=match.version + 1)
        state = self.repository._state
        event = LogicalEvent(str(uuid4()), "contact_revoked", match.match_id, updated.version)
        self.repository._state = replace(
            state, matches={**state.matches, match.pair: updated}, events=(*state.events, event)
        )
        self.repository._revision.advance()
        return updated

    def match_projection(self, match_id: str) -> dict[str, Any] | None:
        bindings = self._bindings()
        authority_guard = acquire_guard(self.discovery.authority)
        context = self._actor()
        match = self._match(match_id)
        if context is None or match is None or context[0] not in match.participants:
            return None
        match = self._refresh_match(match)
        actor = context[0]
        other = next(person for person in match.participants if person != actor)
        target = self.registry.account(other)
        if target is None or not self._target_current(target):
            return None
        if (
            self.repository.blocked(actor, other)
            or not guard_is_current(authority_guard)
            or any(old is not new for old, new in zip(bindings, self._bindings(), strict=True))
            or (
                match.state == "active" and not all(guard_is_current(item) for item in match.guards)
            )
            or (match.state == "active" and not self._authority_current(match.bindings))
            or self._match(match_id) is not match
        ):
            return None
        return {
            "kind": "match",
            "match_id": match.match_id,
            "version": match.version,
            "other_profile_id": target.profile_uuid,
            "state": match.state,
        }

    def matches(self) -> tuple[dict[str, Any], ...]:
        return tuple(
            value
            for match in tuple(self.repository._state.matches.values())
            if (value := self.match_projection(match.match_id)) is not None
        )

    def contact_decision(self, match_id: str) -> dict[str, Any]:
        projection = self.match_projection(match_id)
        return {
            "match_current": projection is not None and projection["state"] == "active",
            "contact_version": projection["version"] if projection else None,
            "send_allowed": False,
            "provider_state": "not_configured",
        }

    def _result(
        self,
        actor: AccountId,
        target: FixtureIdentity,
        operation: str,
        receipt: Receipt,
        *,
        replayed: bool,
    ) -> CommandResult:
        bindings = self._bindings()
        authority_guard = acquire_guard(self.discovery.authority)
        context = self._actor()
        if context is None or context[0] != actor:
            return CommandResult("unavailable")
        projection: dict[str, Any] | None = None
        if operation == "unmatch":
            projection = self.match_projection(receipt.object_ref)
        elif operation == "block":
            row = self.repository._state.blocks.get((actor, target.account_id))
            if row and self._target_current(target):
                projection = {
                    "kind": "block",
                    "target_profile_id": target.profile_uuid,
                    "state": row.state,
                    "version": row.version,
                }
        elif self._target_current(target) and not self.repository.blocked(actor, target.account_id):
            match = self._match_between(actor, target.account_id)
            if match:
                match = self._refresh_match(match)
            current = self.repository._state.directions.get((actor, target.account_id))
            guards = self._guards(actor, target.account_id)
            eligible = self.discovery.batch.eligibility.evaluate(actor, target.account_id)
            if (
                current
                and current.matchable
                and self.policy_version == "development-interactions-1"
                and self._authority_current(current.bindings)
                and all(guard_is_current(item) for item in current.guards)
                and eligible.state is EligibilityDecisionState.READY
                and (match is None or match.state == "active")
                and guards
                and all(guard_is_current(item) for item in guards)
            ):
                projection = {
                    "kind": "interaction",
                    "target_profile_id": target.profile_uuid,
                    "version": current.version,
                    "state": current.state,
                    "match_id": match.match_id if match else None,
                }
        if not guard_is_current(authority_guard) or any(
            old is not new for old, new in zip(bindings, self._bindings(), strict=True)
        ):
            return CommandResult("unavailable")
        return CommandResult(
            "committed",
            {
                "kind": "interaction_command_result",
                "receipt": receipt.public(),
                "replayed": replayed,
                "current_projection": projection,
            },
        )


class FixtureInteractionWorker:
    """No dispatch: bounded logical delivery observations never grant contact."""

    def __init__(self, service: FixtureInteractionService) -> None:
        self.service = service
        self._seen: set[str] = set()

    def consume(self, event: LogicalEvent) -> str:
        if type(event) is not LogicalEvent or event not in self.service.repository.events:
            return "unavailable"
        if event.event_id in self._seen:
            return "duplicate"
        if len(self._seen) >= MAX_EVENTS + MAX_REVOCATIONS:
            return "capacity_exceeded"
        self._seen.add(event.event_id)
        if event.kind == "match_created":
            projection = self.service.match_projection(event.aggregate_id)
            if (
                projection is None
                or projection["state"] != "active"
                or projection["version"] != event.aggregate_version
            ):
                return "stale"
        return "observed_no_delivery"

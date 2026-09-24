"""Development-only acquisition from immutable app-owned facts.

This repository is selected in process by composition, never by a request. It
has no authentication, database or production adapter. Its monotonic counters
model invalidation; atomic persistent acquisition remains a P11 requirement.
"""

import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, date, datetime

from .eligibility import BlockState, EligibilitySnapshot, PairPolicyInputs, PredicateOutcome
from .fixture_coherence import FixtureReadGuard, FixtureRevision, capture_revisions
from .identity import AccountId, require_nonblank
from .trusted_eligibility import (
    BoundPairPolicy,
    PairEligibilityEvidence,
    PairEvidenceVersion,
    PolicyReadiness,
)

PASS = PredicateOutcome.PASS
FAIL = PredicateOutcome.FAIL
UNKNOWN = PredicateOutcome.UNKNOWN


def _optional_strings(instance: object, fields: tuple[str, ...]) -> None:
    if any(
        getattr(instance, field) is not None and not isinstance(getattr(instance, field), str)
        for field in fields
    ):
        raise TypeError("Fact fields require strings or explicit missing values.")


@dataclass(frozen=True, repr=False)
class MediaFact:
    asset_id: str
    owner_id: AccountId
    profile_id: str
    generation: int
    state: str | None
    policy_version: str | None
    delivery_ref: str | None

    def __post_init__(self) -> None:
        require_nonblank(self.asset_id, "asset_id")
        require_nonblank(self.profile_id, "profile_id")
        if not isinstance(self.owner_id, AccountId):
            raise TypeError("Media owner requires an application AccountId.")
        if type(self.generation) is not int or self.generation < 1:
            raise ValueError("Media generation requires a positive integer.")
        _optional_strings(self, ("state", "policy_version", "delivery_ref"))


@dataclass(frozen=True, repr=False)
class ParticipantFacts:
    account_id: AccountId
    generation: int
    source_id: str
    profile_id: str | None
    birth_date: str | None
    account_state: str | None
    session_state: str | None
    verified: bool | None
    consent_state: str | None
    consent_version: str | None
    display_name: str | None
    summary: str | None
    visibility: str | None
    moderation: str | None
    chart_state: str | None
    attribute: str | None
    preference_dimension: str | None
    preference_version: str | None
    accepted_options: tuple[str, ...] | None
    approved_media: tuple[MediaFact, ...] | None

    def __post_init__(self) -> None:
        if not isinstance(self.account_id, AccountId):
            raise TypeError("Participant facts require an application AccountId.")
        if type(self.generation) is not int or self.generation < 1:
            raise ValueError("Participant generation requires a positive integer.")
        require_nonblank(self.source_id, "source_id")
        _optional_strings(
            self,
            (
                "profile_id",
                "birth_date",
                "account_state",
                "session_state",
                "consent_state",
                "consent_version",
                "display_name",
                "summary",
                "visibility",
                "moderation",
                "chart_state",
                "attribute",
                "preference_dimension",
                "preference_version",
            ),
        )
        if self.verified is not None and type(self.verified) is not bool:
            raise TypeError("Verification requires boolean or missing source evidence.")
        if self.accepted_options is not None and (
            not isinstance(self.accepted_options, tuple)
            or any(not isinstance(value, str) for value in self.accepted_options)
        ):
            raise TypeError("Accepted options must be an immutable tuple of strings.")
        if self.approved_media is not None and (
            not isinstance(self.approved_media, tuple)
            or any(not isinstance(value, MediaFact) for value in self.approved_media)
        ):
            raise TypeError("Media facts must be an immutable tuple of MediaFact records.")


@dataclass(frozen=True)
class DevelopmentEligibilityPolicy:
    version: str = "development-eligibility-1"
    consent_version: str = "development-consent-1"
    preference_version: str = "development-preferences-1"
    media_version: str = "development-media-1"
    minimum_age: int = 18
    leap_birthday: str = "march_1"
    effective_from: str = "2026-01-01"
    effective_until: str | None = None
    readiness: str = "resolved"

    def __post_init__(self) -> None:
        _optional_strings(
            self,
            (
                "version",
                "consent_version",
                "preference_version",
                "media_version",
                "leap_birthday",
                "effective_from",
                "effective_until",
                "readiness",
            ),
        )
        if type(self.minimum_age) is not int:
            raise TypeError("Policy age requires an integer.")


DEVELOPMENT_POLICY = DevelopmentEligibilityPolicy()


def civil_date(value: str | None) -> date | None:
    if value is None or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value) is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def age_on(birth_date: str | None, today: date | None) -> int | None:
    """Same UTC civil-date/March-1 leap convention as onboarding/policy.ts."""
    birth = civil_date(birth_date)
    if birth is None or today is None or birth > today:
        return None
    return today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))


def policy_ready(policy: DevelopmentEligibilityPolicy | None, today: date | None) -> bool:
    if policy is None or today is None:
        return False
    if (
        policy.version != DEVELOPMENT_POLICY.version
        or policy.consent_version != DEVELOPMENT_POLICY.consent_version
        or policy.preference_version != DEVELOPMENT_POLICY.preference_version
        or policy.media_version != DEVELOPMENT_POLICY.media_version
        or policy.minimum_age != 18
        or policy.leap_birthday != "march_1"
        or policy.readiness != "resolved"
    ):
        return False
    start = civil_date(policy.effective_from)
    end = civil_date(policy.effective_until)
    return (
        start is not None
        and start <= today
        and (policy.effective_until is None or end is not None and start < end and today < end)
    )


def _all(*values: PredicateOutcome) -> PredicateOutcome:
    return FAIL if FAIL in values else UNKNOWN if UNKNOWN in values else PASS


def _state(value: str | None, positive: str, negative: tuple[str, ...]) -> PredicateOutcome:
    return PASS if value == positive else FAIL if value in negative else UNKNOWN


def _text(value: str | None) -> PredicateOutcome:
    # Same explicit White_Space + BOM set as the closed app contract, without
    # Python/JavaScript strip/trim disagreement or normalization of stored text.
    nonblank = (
        r"[^\u0009-\u000d\u0020\u0085\u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000\ufeff]"
    )
    return UNKNOWN if value is None else PASS if re.search(nonblank, value) else FAIL


def _media(person: ParticipantFacts, policy: DevelopmentEligibilityPolicy) -> PredicateOutcome:
    if person.approved_media is None:
        return UNKNOWN
    if not person.approved_media:
        return FAIL
    seen: set[str] = set()
    outcomes: list[PredicateOutcome] = []
    for asset in person.approved_media:
        if (
            asset.asset_id in seen
            or asset.owner_id != person.account_id
            or asset.profile_id != person.profile_id
            or asset.generation != person.generation
            or asset.asset_id in (person.account_id.value, person.profile_id)
        ):
            return UNKNOWN
        seen.add(asset.asset_id)
        state = _state(
            asset.state,
            "approved",
            (
                "selected",
                "uploading",
                "quarantined",
                "pending",
                "removed",
                "restricted",
                "rejected",
            ),
        )
        policy_current = (
            UNKNOWN
            if asset.policy_version is None
            else (PASS if asset.policy_version == policy.media_version else FAIL)
        )
        outcomes.append(_all(state, policy_current, _text(asset.delivery_ref)))
    return PASS if PASS in outcomes else UNKNOWN if UNKNOWN in outcomes else FAIL


def participant_snapshot(
    person: ParticipantFacts,
    policy: DevelopmentEligibilityPolicy,
    today: date | None,
    revision: str,
) -> EligibilitySnapshot:
    age = age_on(person.birth_date, today)
    consent = _state(person.consent_state, "accepted", ("withdrawn", "declined", "required"))
    current_consent = (
        UNKNOWN
        if person.consent_version is None
        else (PASS if person.consent_version == policy.consent_version else FAIL)
    )
    profile_identity = _text(person.profile_id)
    if person.profile_id == person.account_id.value:
        profile_identity = UNKNOWN
    complete = _all(
        profile_identity,
        _text(person.display_name),
        _text(person.summary),
        _media(person, policy),
        _state(person.chart_state, "resolved", ("unavailable", "unresolved", "pending")),
    )
    return EligibilitySnapshot(
        person.account_id,
        revision,
        UNKNOWN if age is None else PASS if age >= policy.minimum_age else FAIL,
        _all(consent, current_consent),
        UNKNOWN if person.verified is None else PASS if person.verified else FAIL,
        _all(
            _state(
                person.account_state,
                "active",
                (
                    "inactive",
                    "suspended",
                    "deletion_pending",
                    "deleted",
                    "unverified",
                ),
            ),
            _state(person.session_state, "valid", ("none", "expired", "revoked", "restricted")),
        ),
        complete,
        _state(person.visibility, "visible", ("paused", "hidden", "incomplete")),
        _state(person.moderation, "approved", ("restricted", "rejected", "suspended")),
    )


def preference_outcome(
    person: ParticipantFacts,
    target: ParticipantFacts,
    policy: DevelopmentEligibilityPolicy,
) -> PredicateOutcome:
    options = ("demo_a", "demo_b")
    if (
        person.preference_dimension != "demo_connection"
        or person.preference_version != policy.preference_version
        or target.attribute not in options
        or person.accepted_options is None
        or any(option not in options for option in person.accepted_options)
        or len(set(person.accepted_options)) != len(person.accepted_options)
    ):
        return UNKNOWN
    return PASS if target.attribute in person.accepted_options else FAIL


def _token(*values: str | int | None) -> str:
    return json.dumps(values, separators=(",", ":"))


class FixtureEligibilityRepository:
    """Synchronous memory-only acquisition; no request DTO may select this port.

    Every replacement advances counters even when values are restored unchanged.
    Missing directional observation is UNKNOWN; explicitly observed absence is
    CLEAR with its own outgoing revision. Source IDs and generations are bound
    into snapshots but never reused as object/account/asset identities.
    """

    def __init__(
        self,
        clock: Callable[[], date | datetime | None],
        policy: DevelopmentEligibilityPolicy | None = DEVELOPMENT_POLICY,
        *,
        environment: str,
    ) -> None:
        if environment not in {"development", "test"}:
            raise ValueError("Fixture evidence is restricted to development and test.")
        if not callable(clock):
            raise TypeError("An injected clock is required.")
        self._clock = clock
        self._participants: dict[AccountId, ParticipantFacts] = {}
        self._snapshot_revisions: dict[AccountId, int] = {}
        self._preference_revisions: dict[AccountId, int] = {}
        self._blocks: dict[tuple[AccountId, AccountId], BlockState] = {}
        self._block_revisions: dict[AccountId, int] = {}
        self._publication_revisions: dict[AccountId, FixtureRevision] = {}
        self._policy_time_revision = FixtureRevision()
        self._policy_revision = 0
        self._policy: DevelopmentEligibilityPolicy | None = None
        self._time_epoch = 0
        self._last_day: str | None = None
        self.set_policy(policy)

    def _publication_revision(self, account_id: AccountId) -> FixtureRevision:
        if account_id not in self._publication_revisions:
            self._publication_revisions[account_id] = FixtureRevision()
        return self._publication_revisions[account_id]

    def publication_guard(self, *accounts: AccountId) -> FixtureReadGuard:
        return capture_revisions(
            self._policy_time_revision,
            *(self._publication_revision(account_id) for account_id in accounts),
        )

    def put_participant(self, facts: ParticipantFacts) -> None:
        if not isinstance(facts, ParticipantFacts):
            raise TypeError("Fixture source writes require immutable ParticipantFacts.")
        self._participants[facts.account_id] = facts
        self._snapshot_revisions[facts.account_id] = (
            self._snapshot_revisions.get(facts.account_id, 0) + 1
        )
        self._preference_revisions[facts.account_id] = (
            self._preference_revisions.get(facts.account_id, 0) + 1
        )
        self._publication_revision(facts.account_id).advance()

    def remove_participant(self, account_id: AccountId) -> None:
        if not isinstance(account_id, AccountId):
            raise TypeError("An application AccountId is required.")
        self._participants.pop(account_id, None)
        self._snapshot_revisions[account_id] = self._snapshot_revisions.get(account_id, 0) + 1
        self._preference_revisions[account_id] = self._preference_revisions.get(account_id, 0) + 1
        self._publication_revision(account_id).advance()

    def observe_block(self, actor_id: AccountId, target_id: AccountId, state: BlockState) -> None:
        if not isinstance(actor_id, AccountId) or not isinstance(target_id, AccountId):
            raise TypeError("Block observations require application AccountIds.")
        if not isinstance(state, BlockState):
            raise TypeError("Block observations require explicit BlockState evidence.")
        self._blocks[(actor_id, target_id)] = state
        self._block_revisions[actor_id] = self._block_revisions.get(actor_id, 0) + 1
        self._snapshot_revisions[actor_id] = self._snapshot_revisions.get(actor_id, 0) + 1
        self._publication_revision(actor_id).advance()

    def set_policy(self, policy: DevelopmentEligibilityPolicy | None) -> None:
        if policy is not None and not isinstance(policy, DevelopmentEligibilityPolicy):
            raise TypeError("Policy must be a development policy record or explicitly unavailable.")
        self._policy = policy
        self._policy_revision += 1
        self._policy_time_revision.advance()

    def acquire(
        self, viewer_id: AccountId, candidate_id: AccountId
    ) -> PairEligibilityEvidence | None:
        if not isinstance(viewer_id, AccountId) or not isinstance(candidate_id, AccountId):
            raise TypeError("Acquisition requires application AccountIds.")
        # The injected dependency may synchronously update fixture state. Invoke
        # it before capturing facts and counters so it cannot stamp old facts
        # with revisions from a reentrant write.
        now = self._clock()
        if isinstance(now, datetime):
            today = None if now.tzinfo is None else now.astimezone(UTC).date()
        elif isinstance(now, date) or now is None:
            today = now
        else:
            raise TypeError("Clock must return a civil date, aware datetime, or missing time.")
        day = today.isoformat() if today else "unavailable"
        if day != self._last_day:
            self._time_epoch += 1
            self._last_day = day
            self._policy_time_revision.advance()
        viewer = self._participants.get(viewer_id)
        candidate = self._participants.get(candidate_id)
        if viewer is None or candidate is None:
            return None
        if viewer_id != candidate_id:

            def identities(person: ParticipantFacts) -> set[str]:
                return {
                    person.account_id.value,
                    *(asset.asset_id for asset in person.approved_media or ()),
                } | ({person.profile_id} if person.profile_id is not None else set())

            if viewer.source_id == candidate.source_id or identities(viewer) & identities(
                candidate
            ):
                return None
        policy = self._policy or DEVELOPMENT_POLICY
        policy_version = _token(self._policy_revision, policy.version, self._time_epoch)

        def snapshot(person: ParticipantFacts) -> EligibilitySnapshot:
            revision = _token(
                self._snapshot_revisions[person.account_id],
                person.generation,
                person.source_id,
                self._time_epoch,
            )
            return participant_snapshot(person, policy, today, revision)

        viewer_snapshot = snapshot(viewer)
        candidate_snapshot = snapshot(candidate)
        version = PairEvidenceVersion(
            viewer_id,
            candidate_id,
            viewer_snapshot.snapshot_version,
            candidate_snapshot.snapshot_version,
            policy_version,
            _token(self._preference_revisions[viewer_id]),
            _token(self._preference_revisions[candidate_id]),
            _token(self._block_revisions.get(viewer_id, 0)),
            _token(self._block_revisions.get(candidate_id, 0)),
        )
        inputs = PairPolicyInputs(
            policy_version,
            preference_outcome(viewer, candidate, policy),
            preference_outcome(candidate, viewer, policy),
            self._blocks.get((viewer_id, candidate_id), BlockState.UNKNOWN),
            self._blocks.get((candidate_id, viewer_id), BlockState.UNKNOWN),
        )
        return PairEligibilityEvidence(
            viewer_snapshot,
            candidate_snapshot,
            BoundPairPolicy(
                version,
                inputs,
                PolicyReadiness.RESOLVED
                if policy_ready(self._policy, today)
                else PolicyReadiness.PENDING,
            ),
            version,
        )

# P05.1 reciprocal eligibility fixtures

This is the implementation record for **AP1-P05.1-001**. It defines a deterministic
application fixture policy and current fact acquisition for ordered pairs. It is
not launch policy, production authentication, PostgreSQL consistency, a discovery
queue or a Human Design calculation. The existing closed candidate contract is
unchanged; no production endpoint or database adapter is introduced.

## Source and trust boundary

Python `services/api/glow_domain/eligibility_facts.py` supplies immutable
`ParticipantFacts`, `MediaFact`, `DevelopmentEligibilityPolicy` and the
`FixtureEligibilityRepository`. Construction requires an injected clock and
explicit development/test environment. The repository implements the existing
`EligibilityEvidenceRepository` acquisition port; `TrustedEligibilityService`
continues to validate `PairEligibilityEvidence`, `BoundPairPolicy` and the ordered
`PairEvidenceVersion` before the existing `glow_domain/eligibility.py` evaluator
can permit work.

TypeScript `apps/mobile/src/eligibility/facts.ts` supplies the corresponding raw
facts, `FIXTURE_PAIR_POLICY`, predicate functions and `FixturePairRepository` for
the development presentation. It is selected by development composition, not an
HTTP request. The mobile repository deep-copies/freezes inserted facts; Python
facts and nested media/options are immutable dataclasses/tuples. Both capture the
clock before current source records, preventing a clock callback that changes
fixture state from stamping older facts with newer revisions.

Only composition chooses a repository. These internal types are not additional
client DTOs; a frozen object, fixture label or asserted current version cannot
establish server authority. Production must derive the actor/session and current
facts from reviewed authenticated persistence. Expected versions are rejection
conditions, never capabilities. A client cannot supply predicates, a repository,
policy approval or fictional viewer facts to a production handler.

Invalid programming types/identities raise validation errors rather than becoming
successful policy results. Expected missing records/time/policy fail closed.
Python's declared `EvidenceUnavailable()` is a fixed-message expected acquisition
failure mapped by the trusted service to rejected/missing evidence; it carries no
raw upstream reason. Other dependency/programming errors propagate for correction.
Detailed consent, block, moderation and preference reasons remain internal.

## Explicit provisional policy and clock

| Policy input | Development value |
|---|---|
| Eligibility policy | `development-eligibility-1` |
| Current consent | `development-consent-1` |
| Preference catalog | `development-preferences-1` |
| Media policy | `development-media-1` |
| Adult threshold | 18 |
| Leap birthday | March 1 in a non-leap year |
| Effective interval | `2026-01-01` inclusive; no end by default. A supplied end is exclusive and must be later than the start. |
| Canonical corpus reference day | `2026-09-23` |
| Mobile scenario clock | Existing injected `FIXTURE_CLOCK`, `2026-09-23T12:00:00Z` |
| Fictional preference dimension/options | `demo_connection`; `demo_a`, `demo_b` |

The effective interval is a new fixture input for time-validity cases, not an
approved policy publication date. Unknown versions, pending readiness, invalid or
future effective starts, expired ends and missing time leave the policy pending
and the pair rejected. Birth dates require exact valid civil `YYYY-MM-DD`; missing,
malformed or future dates yield unknown adult status. The exact eighteenth
birthday passes. February 29 birthdays reach the next age on March 1 in a
non-leap year. TypeScript reuses onboarding's civil-date/adult rule; the shared
corpus checks Python agrees. No locale parser, timezone lookup or birthday estimate
is used.

The Python clock accepts a civil date, aware datetime converted to UTC civil day,
or missing time. A naive datetime is unavailable time. Mobile uses its injected
Date clock and UTC civil day; an invalid Date is unavailable. Every acquisition
rechecks current time. An observed day change advances effective clock identity,
even when a later clock observation returns to an earlier day. Stored record
versions alone cannot preserve an expired predicate. This fixture epoch is not a
production clock/distributed invalidation design.

These policies make no launch/legal claim. A05 still owns launch geography,
gender/orientation taxonomy, distance or age-range product requirements, operator
policy and resurfacing/rematch/history rules. No wildcard is defined. Missing
required policy denies the dependent workflow.

## Fact-to-predicate mapping for each person

All seven participant predicates must pass for **both** viewer and candidate.
`FAIL` dominates `UNKNOWN` in a conjunction; neither grants permission.

| Predicate | Source and exact rule | Fail-closed cases |
|---|---|---|
| Adult | Private `birth_date` and injected current civil day; computed age at least 18 | Underage fails; missing/invalid/future date or unavailable clock is unknown. |
| Consent | `consent_state == accepted` and exact current `consent_version` | Withdrawn/declined/required or stale version fails; missing/unknown state/version is unknown. |
| Verified | Current account verification fact | False fails; absent fact is unknown. |
| Active | `account_state == active` and `session_state == valid` | Inactive/suspended/unverified/deletion-pending/deleted or none/expired/revoked/restricted session fails; unsupported/missing state is unknown. |
| Complete | Distinct nonblank profile identity, display name, nonblank summary, current approved media and `chart_state == resolved` | Empty/missing text/media, unresolved chart and inconsistent source identity cannot pass. Preferences/reciprocity are not part of this predicate. |
| Visible | `visibility == visible` | Paused/hidden/incomplete fails; absent/unsupported state is unknown. |
| Moderation | `moderation == approved` | Restricted/rejected/suspended fails; missing or pending/unknown review is unknown. |

Completeness requires at least one approved asset with current media policy and
nonblank delivery reference, owned by that account and bound to its profile and
generation. Asset IDs must be unique and distinct from account/profile identities.
Inconsistent ownership/generation/identity makes media unknown even if another
asset appears approved. Missing media facts are unknown; an observed empty set
fails. A removed/restricted/rejected or otherwise nonapproved asset cannot satisfy
completeness. The combined mobile runtime obtains this set from current
`MediaStore.approvedCollection()`, including local revocation; it does not infer
approval from a filename, earlier upload acknowledgment or stale lifecycle row.

Account, profile and asset identities cannot substitute for each other. The pair
repository additionally rejects conflicting identities across the two records and
shared per-person source identity. `source_id` identifies one person's source
incarnation; it is not a collection-wide repository label or another account ID.
Source generation and revision changes invalidate prior evidence even if visible
values return to their old contents.

A resolved chart here is explicitly supplied fictional state for readiness. It
creates no engine identity, chart calculation or ready compatibility result.
Ordinary onboarding still lacks independent chart/review/policy evidence; saving
text, preferences or approving a photo does not invent those prerequisites.

## Reciprocal preferences and directional blocks

Each participant independently supplies an `attribute` and `accepted_options`.
The viewer accepts the candidate only when the candidate's supported attribute is
in the viewer's current accepted set. The candidate accepts the viewer only when
the viewer's supported attribute is in the candidate's current accepted set.

| A accepts B | B accepts A | Pair preference result |
|---|---|---|
| Pass | Pass | Both preference requirements pass |
| Pass | Fail | Excluded |
| Fail | Pass | Excluded |
| Fail | Fail | Excluded |
| Either unknown | Any | Excluded |

Equal chosen options or intersecting desired sets are not the algorithm. The
corpus's ready control deliberately uses opposite person attributes and opposite
accepted sets. Empty accepted sets fail; absent sets, unknown options/attributes,
duplicate options, wrong/missing dimension or unsupported preference version are
unknown. None of these states means “accept anyone.”

Each block direction requires an explicit observation. A missing observation is
unknown, not clear. An observed absence is `clear` with its own revision. First
block insertion, later clearing and repeated clear observations advance revision
identity; an old no-block token cannot revive after unblock. Either blocked or
unknown direction excludes. Self-pairs never become ready.

## Ordered revision and source binding

The shared vector fields are `viewer_id`, `candidate_id`,
`viewer_snapshot_version`, `candidate_snapshot_version`, `policy_version`,
`viewer_preference_version`, `candidate_preference_version`,
`viewer_block_version` and `candidate_block_version`. They preserve pair order and
are equality tokens, not timestamps or sortable capabilities. Python and mobile
need equivalent invalidation semantics; they do not promise identical serialized
counter tokens across independent repositories.

| Source change | Implemented fixture invalidation |
|---|---|
| Account/access/consent/profile/media/moderation/visibility change or same-value participant replacement | Advance participant aggregate revision; bind source incarnation and generation. Fixture writes conservatively advance that person's preference revision too. |
| Preference change or restoration | Advance preference and aggregate evidence, then compute both directions again. |
| Explicit block/clear/unknown observation | Advance the outgoing directional observation revision and the relevant aggregate snapshot token; absent observations retain explicit unknown state. |
| Policy set/withdrawal/restoration, even same value | Advance policy identity; unknown/unready policy rejects. |
| Observed clock day/availability change, including return to an older day | Advance effective clock identity in both snapshot and policy tokens and re-evaluate current validity. |
| Source/account generation replacement | Bind the new generation/source and revision; never reuse an earlier token merely because facts match. |

Python uses participant counters, outgoing account block counters and a policy/time
epoch. Mobile uses monotonically increasing fixture serials bound into participant,
directional-block, policy and clock components. The profile integration additionally
covers accepted profile/preference versions, discovery revision, owner authority
and current media collection version before replacing the candidate facts. Every
same-value accepted source write therefore remains distinguishable.

`READY` permits only the specific next workflow. Known exclusion returns
`EXCLUDED` even if a supplied precondition is stale. Otherwise stale preconditions
or inconsistent source vectors require `RELOAD_REQUIRED`; wrong pair, missing or
pending evidence returns `REJECTED`. Internal reasons stay private. Reacquisition
is a new decision; it does not automatically replay an obsolete privileged intent.
Neither resume nor unblock creates or restores a match/contact/history grant.
Safety/privacy operations retain their own separate authorization paths.

## Narrow mobile integration and retained data

`ProfileStore.currentPair()` composes one fictional viewer → current owner pair.
The owner record comes from accepted profile/preferences, current media and
OnboardingStore account/birth/consent authority. A separately seeded fictional
viewer supplies its own raw account/profile/media/consent/preferences/attribute
facts and directional block observations. The old reciprocal marker and
`bothBlocksClear` boolean no longer authorize this pair path.

Owner readiness no longer requires a compatible fictional candidate. It still
requires current account/adult/consent, saved profile, configured preferences,
media/chart/review and the existing development policy. Thus an independently
incompatible, paused or blocked viewer can remove candidate disclosure while
owner editing and the otherwise ready profile remain available. Explicit owner
pause and media cleanup behavior are preserved.

`candidateContext()` binds exact pair evidence, candidate profile ID, generation
and discovery revision. `candidatePreview()` copies the expected context before
dependencies, reacquires evidence and validates that context. Candidate age comes
from the same captured evaluation clock and immutable private birth facts; media
references come from the evaluated immutable approved/current-policy facts. No
separate unbound age/media read supplies the projection. It validates the closed
allowlist, reacquires final context/evidence, then checks local source identity
after the final clock callback before returning. The Alex scenario's date
`1990-06-15` yields age **36**
on the reference day; another date/day is calculated rather than assigned 36.
The projection contains only profile ID, display name, age, summary, approved
synthetic references and unavailable compatibility. It excludes email, raw birth
input, location, preferences, engine IDs, grants/private originals and reasons.
Owner preview remains a separate management view.

`useRecommendations` includes the captured pair version in its access key, checks
it again after delayed loading and masks obsolete retained content during render
before navigation or asynchronous effect cleanup. Its preexisting `gapp-dev-v1`
Alex/Jordan/Riley records remain **static smoke/layout samples**. They are gated as
a retained presentation by the viewer → owner pair; they are **not independently
fact-derived eligible candidate pairs**. The actual P05.1 pair projection is
`candidatePreview()`. P05.2 must implement real bounded discovery composition;
this hook change is not that queue/pagination/ranking feature.

Existing labeled development controls exercise each block direction, viewer
preference changes/restoration, viewer pause/resume and candidate attribute
changes. They are in-process test controls, not server evidence endpoints or
safety/contact operations. Current revision changes invalidate retained contexts;
fresh permission does not revive old pending work or historical relationships.

## Shared truth table and provider ordering

The canonical data corpus is
`packages/contracts/fixtures/reciprocal-eligibility-v1.json`, version
`reciprocal-eligibility-v1`. It supplies independently specified base raw facts,
per-case source patches and expected pair/per-person/directional outcomes.
Unspecified expected predicates are explicitly pass and directions pass/clear as
stated in the corpus description; they are not generated from evaluator output.
Python `tests/test_eligibility_facts.py` and mobile `src/eligibility/facts.test.ts`
consume the same cases, including positive controls and fail/unknown predicates
on each side, preference combinations, block directions, identities/media,
adult/leap boundaries, stale consent/policy and clock changes. Additional unit
cases exercise immutable capture and every revision component/restoration; provider
and retained-screen tests exercise delayed invalidation. Existence of a case is
not proof it passed; actual results belong in the [checkpoint](../testing/p05-1-checkpoint.md).

`FixtureCompatibilityBatchService` retains the bounded conformance seam.
Acquisition precedes any chart mapping/provider call; each retry reacquires.
`CompatibilityRequest` and `FixtureCacheKey` include the explicit captured
`eligibility_policy_version` in addition to ordered identities, input/mapping and
provider provenance. Mapping reads are dependencies too: eligibility is rechecked
after them before dispatch and during post-call/final-return validation. Every
retained outcome, including missing/pending-mapping outcomes, is rechecked before
return. A final eligibility-only sweep follows all mapping callbacks so a later
candidate cannot revoke an already revalidated earlier result unnoticed.

Pairs excluded or unresolved at initial eligibility acquisition make zero
chart/provider calls. Revocation discovered after mapping work prevents provider
dispatch; later revocation discards the affected result. No network or
ready HD output is fabricated; synthetic ready compatibility still projects
pending. Sequential rechecks narrow stale windows but are not an atomic
multi-candidate transaction. [Provider conformance](provider-conformance.md) owns
the complete provider/version/error contract.

## Remaining integration proof

See [P11 carryforward](../testing/p11-deferred-acceptance.md): DB09 authenticates
actors/revocation; DB10 proves consistent transactions, time validity, all writers'
revision increments, policy and absent-block races; DB11 proves queries/cursors;
DB05/DB06 prove interaction/contact races; DB07/DB08 prove durable events/replay.
A01/A07 govern supported HDE rights/contracts/throughput; A02 schema/roles; A04
provider/native access; A05 launch/operator policies; A08 chat enforcement. A06
stays disabled. Fixtures complete none of those proofs. Same logical DB/app-schema
direction and every protected HDE/shared-resource boundary remain unchanged.

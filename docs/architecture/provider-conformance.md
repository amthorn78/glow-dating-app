# Provisional provider contracts and conformance

P02.3 app-side baseline, prepared against application main
`35603603326a8bfbb79b6491b2fef8cc65bc9d6d`. Governing authority is GAPP-PF01
revision 1.2, sections 5–7, P02 and D08, plus the AP1-P02-001 continuation
assignment. No HDE source, endpoint, database, wire schema or live output was
inspected or changed for this implementation. A01/A07 remain unresolved.

The app interfaces in `services/api/glow_domain/provider_contracts.py` are
provisional internal Python contracts. Their only concrete adapters are in
`provider_fixtures.py`, with explicit `development`/`test` guards at construction
and invocation. They are not registered as HTTP routes. Existing HTTP/UI data
stays pending/fixture, and readiness stays 503. A supported live adapter requires
a separate reviewed mapping, actual rights and P11 evidence.

P05.1 extends this same internal seam with raw-fact eligibility acquisition,
explicit eligibility-policy binding and additional delayed-revocation checks.
AP1-P05.1-002 adds a bounded callback-free publication check after those reads.
The [reciprocal fixture mapping](reciprocal-eligibility-fixtures.md) owns its
provisional policy and shared truth table. Served development responses, closed
production DTOs and the absence of active production routes are unchanged.

| Contract | Responsibility and implemented substitute | Trust and unresolved boundary |
|---|---|---|
| `BirthInput` | Immutable private civil birth date/time, known/approximate/unknown precision, entered place, optional timezone with provenance, input/consent versions and app account identity. Private facts are excluded from its repr. | Authenticated ownership, current consent and input version must be acquired by the application; a client cannot assert their truth. No timezone calculation or accepted live HDE birth schema is claimed. |
| `ChartResolver` | Returns identity/version-bound pending, ambiguous, resolved, unavailable, unsupported, stale or consent-required state. The fixture resolves only an explicitly supplied matching `ChartMapping`. | Resolution requires supported engine operations, source authority, idempotency and data rights. No engine ID is generated from an app ID. A supplied timezone string is preserved input/provenance, not validation of that zone or proof of historical civil-time resolution. |
| `CompatibilityProvider` | One ordered mapped pair returns `BoundCompatibilityResult`, including full `FixtureCacheKey` and explicit fixture provenance; typed expected failures remain separate. | Caller first acquires trusted eligibility. Single-pair iteration models a bounded app batch; it does not declare that HDE supports a batch endpoint, a rate, a score or a ready projection. |
| `CompatibilityProjection` | Closed minimal internal status/source projection. Synthetic ready maps to pending. It cannot carry a score, band, birth input, chart identity, source body or explanation. | A01 must settle allowed live fields, wording, caching/persistence rights and freshness. No ready public HD result is enabled. |
| `EngineLifecycle` | Plans app-reference invalidation and an explicitly incomplete engine obligation. Replays are idempotent; conflicting payloads under one key reject. | No engine deletion or recalculation is executed. Unknown ownership, shared charts, zero known shared references and missing current mappings all retain an unresolved obligation. |
| `BirthInputRepository` | Narrow current private input read by app account. | Persistence/authenticated ownership implementation deferred. |
| `MappingUnitOfWork` | Defines expected-version mapping change plus a deduplicated outbox event in one transaction. A narrow in-memory substitute checks consistency/replay/rejection. | No SQL, locks, rollback durability, outbox dispatch or concurrency proof. P11 must establish the real adapter contract. |

## Birth and mapping invariants

Birth dates are `date`, never datetime instants. Local times have no timezone
offset. Unknown time has no invented value; known/approximate time requires an
entered civil value. Approximate/unknown time or absent timezone remains ambiguous
in the fixture regardless of a configured synthetic resolved scenario. The
fixture makes no silent conversion, geographic lookup or noon/midnight fallback.
Empty input fields, invalid Unicode scalar text, incorrect types and timezone
without corresponding provenance reject. User facts are preserved without
normalization. Public-contract decoding remains a separate boundary.

Resolution results carry app identity, input version and simulated
input/mapping/engine/adapter/contract provenance. A resolved mapping must belong
to that exact account/input version and use a distinct opaque engine reference.
Changed current input or revoked consent defeats replay. Changed payload under
the same idempotency key rejects. Resolution-state fixture ledgers are in-memory
and cannot prove a provider's durable replay behavior.

The private wire DTO and data models have their own identifiers and field names;
the app mapping supplies `account_id`, `input_version` and trusted consent facts
from authenticated repositories. Civil wire strings parse into `date`/`time`
without UTC conversion; `time_precision` maps to `TimePrecision`. Both the static
model and wire DTO use `timezone_name` and `timezone_provenance`, corresponding to
the internal fields. Wire-supplied timezone provenance cannot confer resolution authority.
No such production route or adapter is implemented by these internal types.

On an input correction, old result/mapping versions no longer qualify as current.
Do not relabel the old mapping as resolved for the new input. Retain the new input
as unresolved until a separately supported resolution returns matching identity
and provenance; only then can a new compatibility key be formed. Cache retention
and engine recalculation remain rights-dependent.

## Eligibility, batches, errors and freshness

`FixtureCompatibilityBatchService` composes `TrustedEligibilityService`, current
chart mappings and the provisional compatibility port. It accepts account IDs
and per-pair idempotency keys, never eligibility booleans. The composition root
owns the server evidence repository. A type or provenance marker is not
authentication and cannot turn untrusted JSON into authorization.

1. Validate a tuple of at most twenty distinct candidate identities and distinct
   idempotency keys. Twenty is an internal fixture bound, not a launch market,
   engine throughput assertion or provider-approved quota.
2. Acquire pair/version-bound eligibility. Excluded, unknown, wrong-pair,
   policy-pending and stale evidence ends that candidate before chart/provider
   access. Empty/all-excluded input yields `empty` without provider work.
3. After initial ready eligibility, capture its participating fixture guard and
   the account–chart-link guard before the first mapping read. Missing or
   unavailable participation fails closed before provider work. Read both mappings;
   reject absent/wrong identities and return pending for an
   unresolved chart. Preserve direction. Compare full versions across retries.
   Recheck eligibility after mapping callbacks and before provider dispatch;
   a mapping read may itself cross a source or clock change.
4. Invoke one pair. On declared timeout/outage, retry at most the explicitly
   configured one to three total attempts, preserving the idempotency key and
   re-acquiring eligibility/mappings before every attempt. Other expected
   failures stop immediately. No sleeps or production retry scheduler is built.
5. Match returned identity, input/mapping/eligibility-policy versions and simulated
   contract/engine provenance. Unsupported version, wrong pair and stale mapping remain distinct
   failures. Re-acquire both people's current eligibility and mappings after
   each final call; discard output on changes, including block, consent,
   suspension, pause or deletion. Recheck eligibility again after mapping reads;
   the evidence service owns those predicates.
6. After all provider calls, reacquire eligibility for every retained outcome,
   including missing/pending-mapping outcomes. A denied earlier attempt is never
   promoted by later restoration. Retained provider outputs also recheck both
   mappings and eligibility after those callbacks. The eligibility-only sweep
   preserves current exclusion diagnostics but is not the publication boundary:
   its own last read can invalidate an earlier pair. Finish with one callback-free
   check of the originally captured fact/policy/time and mapping revision cells.
   Changed fact evidence returns `reload_required`; changed mapping evidence
   returns `stale`. Both remove compatibility. No dependency read follows this
   acceptance check.
7. Preserve an outcome for every submitted candidate. Per-account changes discard
   affected retained outputs while preserving unaffected results; shared-viewer or
   policy/time changes invalidate every dependent result. `partial`
   describes mixed completion; `evaluated` describes completed fixture calls,
   not real compatibility readiness or an entitlement.

### Synchronous fixture publication boundary

`fixture_coherence.py` defines concrete `FixtureRevision` cells and immutable
`FixtureReadGuard` captures. The fact repository retains per-account cells for
participant replacement/removal and outgoing block observations, plus a shared
policy/time cell for policy writes and observed day/availability changes. The
`FixtureChartMappingRepository` retains per-account cells and advances them on
every `put(account_id, mapping_or_none)`, including deletion and same-value
restoration. A plain get-only dictionary cannot establish monotonic invalidation
and is not silently copied into a trusted adapter.

Guards remain bound to the original attempt across retries and provider calls.
Guard acquisition itself is callback-capable and occurs before the normal source
rechecks. The final `guard_is_current` function accepts exact concrete cell/guard
types, reads stored integers directly and invokes no virtual getter, custom
equality/hash, clock or repository operation. Affecting writers must use the
repository write operations and their retained cells. This internal composition
contract does not protect against a malicious adapter fabricating trusted facts
or bypassing its own writer discipline.

The candidate cap remains twenty and the configured retry cap one to three total
provider attempts per candidate. The correction adds no retry, provider call or
callback-capable sweep. Continuously changing or unavailable evidence cannot be
chased into permission. This covers synchronous fixture callbacks, including
later-candidate writes to an earlier candidate or the shared viewer. It is not
database isolation, locking, durable invalidation or a cross-thread guarantee.

`ExpectedProviderFailure` carries only a declared code. It never preserves raw
upstream text or private input. Expected timeout/outage, unsupported output,
malformed provider payload, wrong identity, stale version and idempotency conflict
are distinct. Undeclared return types and unexpected exceptions are programming
defects and propagate for correction. Broad exception-to-unavailable conversion
is intentionally absent.

The lower-level `evaluate_with_retry` is a nonpersistent conformance helper that
requires prechecked input; it is not an authorizing application service. The
batch service uses it for one attempt at a time and performs the fresh checks
around it. Neither helper is an authenticated route.

All cache/result identities remain ordered. They include both app IDs, both
engine references, both birth-input and mapping versions, explicit captured
`eligibility_policy_version`, fixture-set version,
adapter version, simulated engine and engine-contract versions and internal port
version. Existing explicit synthetic symmetry tests establish no real engine
symmetry. No cache store, TTL, permitted reuse or actual invalidation delivery is
implemented. `CompatibilityRequest` requires that policy revision explicitly;
the trusted batch takes it from `PairEvidenceVersion`, and finalized fixture
idempotency keys cannot replay prior-policy output. A client-supplied current
policy assertion grants no eligibility. The pure publication guard closes the
demonstrated in-process callback window; the future P11 transaction/recheck
boundary must establish race behavior for privileged
actions. Compatibility still cannot authorize a like, match or message.

## Transaction and lifecycle responsibilities

`MappingWrite` binds account, expected account/input/mapping versions and the
new mapping. `MappingOutboxEvent` contains only the corresponding account,
mapping version, event kind and globally unique deduplication key. The UOW must
atomically compare all expected versions, check current consent/deletion, write
the mapping and enqueue the event. Stale state returns false without either
write. Invalid correspondence or conflicting replay must roll back both.

Resolution involves two app transactions. First, persist the input/pending
request and its outbox event; only after that commit may a worker invoke an
authorized resolver. When its response arrives, the result-acceptance UOW
described here rechecks the account/input/mapping revisions and current consent,
then commits the mapping plus invalidation event. The prerequisite response
therefore precedes this second transaction; no provider call runs inside either
transaction. Any further work follows the committed event. The independent
outbox infrastructure must precede domain changes that rely on it. These
transactions and worker dispatch are designed, not implemented by the fake.
Pair-action transactions are separately defined in
`trusted_eligibility.py`; they also protect both preference/block directions and
absence-to-presence block changes.

The fixture substitutes only one account's mapping/outbox behavior. It has no
database, framework or fake locking engine. Its mutable dictionaries do not
certify atomicity, locking or crash recovery. Exact replay returns the prior
logical commit once; changed content under that key conflicts. Deletion or
withdrawn consent overrides replay success.

An account deletion transaction immediately revokes app visibility/access and
records durable tombstone/provider work. `EngineLifecycle.plan_detachment` only
models the next obligation: invalidate the app reference and resolve ownership,
preserve a shared chart, obtain supported deletion rights, or reconcile prior
references when the current mapping is absent. **Every fixture obligation remains
incomplete.** A zero app reference count does not authorize deletion of engine
data. A missing mapping does not prove no historical chart exists. Restore must
replay deletion tombstones before visibility/provider work can resume. HDE writes
remain outside D08 and require separate explicit authority.

## Dependencies and real proofs still required

| Dependency / phase | Required evidence before dependent integration |
|---|---|
| A01, P11B | Supported release/contract, authorized operation scope, accepted uncertain-birth semantics and timezone source; chart identity/update/idempotency; allowed output fields, directionality, cache rights and invalidation; deletion/shared-chart ownership and completion evidence. |
| A07, P11B | Supported request granularity, actual throughput/rate limits, timeout/retry budgets and measured bounded workload behavior. Fixture cap/retries prove none of these. |
| A02, before P11 target mutation | Exact app/HDE/legacy logical database, migration/runtime role and storage ownership. P02 opens no database connection. |
| P11A | Real repository/UOW conformance on disposable PostgreSQL, CAS under concurrent consent/input/block/deletion changes, mapping/event rollback, deduplication, durable outbox crash recovery and migration/restore proofs. |
| P11B | Authorized sandbox conformance for malformed/version/stale output, outages, partial responses, retry deadlines, replay semantics, auth/rate-limit enforcement, real cache invalidation and provider lifecycle evidence. |
| P11C | Verified isolated production app target/roles and bounded authorized live smoke after staging evidence. No HDE mutation inferred from app deployment authority. |

These block their dependent live integration actions, not independent app
contract/model/fixture work. [Provider conformance evidence](../testing/provider-conformance.md)
records actual local checks and test-to-proof boundaries.

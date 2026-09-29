# Static application data model

P02.2 defines 32 app-owned Django models and two migration files in
`services/api/glow_persistence/`. These are **unapplied design artifacts**. The
fixture API does not install this app. No ORM repository, database driver,
database connection, real authentication or durable queue is implemented by them.
The P11 [migration plan](../operations/migration-plan.md) owns activation order.

## Identity, time and field semantics

Every app model derives from `Record`: an opaque UUID primary key, aware
`created_at`/`updated_at` instants and an integer revision at least one. The wire
contract serializes UUIDs as lowercase strings and instants as UTC seconds.
Repositories must reject revision overflow above the wire safe-integer bound
rather than round a database bigint. Revisions are compare-and-swap inputs; Django
`save()` does not implement that contract automatically. Creation uses the wire
absence precondition zero, then creates revision one.

All declared fields are required unless their model field has `null=True` or
`blank=True`. A nullable fact is unknown/not yet available; it must not be filled
by guessing. Empty profile bio/location labels mean incomplete or withheld text,
not eligibility. `BirthInput.birth_date` and `local_time` preserve civil values;
an unknown time is null. A timezone and its provenance are either both present
or both null. No UTC birth instant is fabricated. Schema text/Unicode validation
runs before storage; model metadata and PostgreSQL do not replace the shared
wire decoder. `Profile.bio` maps to wire `summary` (maximum 500 code points).

Model source is the exact field/length/constraint definition. Named constraints
in the migration state are executable DDL definitions awaiting P11 proof. Django
field choices also have explicit state checks; validations such as JSON shape,
per-owner relationships and state-transition legality remain repository/domain
responsibilities. Models must never be serialized wholesale.

## Maintained authentication mapping

`AppAccount.auth_user` is a unique protected FK to `settings.AUTH_USER_MODEL`.
The static registry uses maintained `django.contrib.auth.User` to express this
dependency. App UUIDs differ from that library identity. Passwords, challenges,
normalized email identities, credential linking and bearer/refresh tokens are
owned by the configured Django/allauth components, not new Glow credential code.

The default Django `User.email` field is **not unique**. P02 does not claim it
implements normalized email uniqueness or verified login. P04/P11 must pin and
configure django-allauth headless, its supported native token strategy and email
normalization/verification/linking behavior. Required configuration intent is
unique email identities (`ACCOUNT_UNIQUE_EMAIL`), verified email onboarding and
email login through allauth; exact fields/migrations depend on the pinned release.
Do not repurpose a client-provided email or app UUID as a verified auth subject.
If the selected integration requires a different user model, resolve its initial
migration dependency before P11 creates any schema; do not switch live auth tables
casually. No allauth package/migration is fabricated or marked installed here.

`AccountSession.auth_session_ref` is an adapter-provided **non-secret** library
session identifier, not a session cookie/token/hash invented by Glow. The future
adapter must demonstrate how it obtains that identifier and revokes the actual
maintained session. If the provider has no such supported identifier, amend this
mapping before integration. `epoch` binds a session to `AppAccount.session_epoch`;
revocation must also affect maintained auth persistence. Session metadata alone
does not revoke a credential.

Official references inspected for this design on 23 September 2026:
[Django migrations](https://docs.djangoproject.com/en/5.2/topics/migrations/),
[allauth headless](https://docs.allauth.org/en/latest/headless/index.html), and
[allauth account configuration](https://docs.allauth.org/en/latest/account/configuration.html).
P11 rechecks the actual selected release and configuration.

## Data groups and ownership

All rows below are application-owned. The storage direction is the app's own
logical database on HDE's PostgreSQL service, with restricted owner, migration and
runtime roles (OD-18, [ADR 0004](../adr/0004-app-database-placement.md)). It
supersedes the audited app schema in HDE's logical database, `railway`. The audit
maps all 32 provisional models to new app-owned relations if retained; none reuses
a legacy or HDE physical table.
The final P11 design may consolidate provisional models. Engine references are
opaque external identifiers, never foreign keys into engine tables. A FK targets
only an app model or the app's maintained auth table. Index names shown are
definitions, not proven query plans or capacity claims. No schema, grant or
migration is activated by this fixture work.

| Models | Relationships, constraints and indexes | Privacy and lifecycle |
|---|---|---|
| `OutboxEvent`, `WebhookInbox` | Migration 0001 precedes app state. Unique event `dedup_key`; unique provider/event identity. Versioned aggregate reference; queue/lease/delivery timestamps. Verified/applied inbox and leased/delivered outbox states require corresponding timestamps. Indexes on state plus scheduling time. | Operational-minimized. Reference payload only; no birth/chat/token body. Payload digest binds replayed provider identity to original content. Worker retention/retry policy must be explicit. |
| `AppAccount`, `AccountSession` | One app UUID per maintained auth user; account lifecycle checks, positive eligibility/preference/block/session revisions; unique non-secret session reference, expiry and revocation timestamp. Session owner/state index. | Account-private. Session and visibility revocation are immediate transaction requirements; secrets remain with auth. |
| `PolicyRevision`, `ConsentDecision` | Unique named policy pointer; no rows seeded. Append-only consent decisions unique by account/purpose/revision with policy version and event time. Account/purpose/time index. | Account-private consent. Missing policy/decision grants nothing. Policy pointer is transactionally locked alongside actions. |
| `Profile`, `Preferences` | One each per account; explicit visibility; bounded display text. Policy-versioned JSON selections, validated against closed schema and selected policy before storage. Profile state/UUID cursor index. | Account-private source; candidate projection allowlist only. Missing preferences policy prevents eligibility. No automatic geography, range or resurfacing policy. |
| `BirthInput`, `EngineIdentity` | Private input revisions unique by account/version; input time/provenance checks. One current mapping per account with protected birth-input FK. Resolved mapping requires engine ID plus engine/contract provenance; pending mapping has none. Engine IDs intentionally not unique across accounts. | Account-private input/mapping; engine-owned chart semantics. Shared references do not grant chart deletion rights. Cross-row input ownership is checked in UOW, not by a simple FK. |
| `MediaAsset` | Owner FK; unique provider/storage reference when present; unique current position per owner. Approved state requires variant and review references. | Provider-managed bytes; private originals. App owns review/order. Reorder must use a collision-safe temporary position strategy inside one UOW; prove SQL behavior P11. |
| `DirectionalInteraction`, `Block` | Unique ordered actor/target; self-pairs forbidden; current like/pass or active/removed block row. FK indexes support both directions. | Account-private unilateral actions. Removing a block increments outgoing block revision and cannot restore contact automatically. Historical resurfacing/rematch policy A05 remains unset. |
| `Match` | UUID pair sorted by underlying UUID value (`account_low < account_high`), unique pair and positive contact version. | Participant-only projection. One pair record; history/rematch requires policy, never a second match row for the same pair. Reciprocal likes and eligibility are cross-row transaction invariants. |
| `CompatibilitySnapshot` | Ordered viewer/candidate, both engine references, birth/mapping revisions, full eligibility vector, engine/contract/adapter provenance and expiry. Unique directional revision tuple; viewer/expiry index. | Account-private metadata only; no HDE result body/score/band column. `ready` means internal metadata state, not permission to expose an HDE result. Cache/output rights remain A01. |
| `RecommendationBatch`, `RecommendationEntry` | Owner, policy and own three eligibility revisions in batch; each candidate's three revisions in entry. Limit 1–100; positions 0–99; unique candidate and position per batch. Nullable snapshot FK can clear when removed. Owner/time/ID cursor index. | Bounded account-private candidate queue. API page maximum 50 is smaller than batch maximum. Repositories enforce count ≤ batch limit, entry position < limit, no self-candidate and correct snapshot pair. |
| `ChatBinding`, `MessageSubmission` | One binding per match; provider/channel unique when known; active binding requires reference. Actor/idempotency key unique; accepted message requires provider receipt, pending message requires private text. | Provider owns retained conversation history. App temporarily owns bounded delivery spool (4000 code points), clears per approved retention/receipt policy. Only reference/version enters outbox. No provider membership alone grants send permission. |
| `DeviceRegistration`, `NotificationSettings` | Unique installation ID and private token-store reference; account FK; iOS/Android and active/revoked checks. One notification preference row per owner, defaults off. | Provider-managed secret reference, not plaintext token. Installation transfer/rotation requires old owner revocation in UOW. Wire provider token goes into the supported secure store before this reference is saved. |
| `SafetyReport`, `ModerationCase`, `Appeal`, `StaffAudit` | Reporter/subject nullable `SET_NULL`; preserved subject marker. Protected report/case relationships. Resolved case/appeal requires outcome. Unique audit request ID; object/time audit and moderation queue indexes. | Safety-restricted description/evidence and immutable audit. Evidence-ref JSON shape/ownership validated before save. Staff subject is external authenticated operator identity, distinct from dating accounts. No support-to-moderation privilege inheritance. |
| `SupportRequest` | Optional account or secure contact reference, bounded subject/description, explicit lifecycle and retention metadata. | Account-private/support-restricted. Public requests get generic acknowledgment; contact verification precedes account action. Category is server-classified, not an undeclared mandatory client field. |
| `ExportJob`, `DeletionJob`, `ProviderLifecycleStep` | Own-account export with ready artifact/expiry requirements. Unique deletion subject and nullable account FK survive purge. Each step belongs to exactly one export or deletion; unique idempotency key and verified evidence requirement. Retry queue index. | App orchestration; processor owns actual export/purge. Required processor manifest and scope completeness are UOW/domain checks. Completed deletion cannot be inferred from row state alone. |
| `DeletionTombstone`, `IdempotencyRecord` | Tombstone UUID subject survives without account FK; protected deletion job. Intent dedup unique by actor/operation/key, with target and complete canonical intent bound by the digest; immutable outcome code, result reference and committed version. | Restore-replay and operational-minimized. No email/birth/chat payloads or cached grants in tombstones/receipts. Tombstone must exist at revocation, before eventual hard purge. |
| `Entitlement` | Unique account/product reference; only permitted state `disabled`. | Conditional boundary only. No paid entitlement can be activated with these definitions; A06 and maintained provider integration require later schema change. |

## Trusted eligibility and unit-of-work boundaries

The source of truth is server-owned current policy and rows, never client boolean
flags. See [trusted eligibility](trusted-eligibility.md). Stored snapshot evidence
includes viewer/candidate identities, both `eligibility_version` values, both
`preferences_version` values, both `blocks_version` values and policy version.
Batch owner fields plus candidate entry fields reconstruct the same vector.
Changing a mapping reference, input, policy or safety state invalidates reuse.

The future PostgreSQL UOW acquires policy/account/pair rows in stable order and
rechecks the complete vector inside the committing transaction. Missing,
wrong-pair or mismatched evidence returns stale/reload/denied; a passing earlier
read is insufficient. Preference/block absence is protected by persistent
account counters, so insert/remove races cannot evade version checks. Every
relevant account/consent/profile/moderation/visibility/deletion change bumps
`eligibility_version`; preference/block mutations additionally bump their own
outgoing collection counter. Policy publishers lock the same `PolicyRevision`
row that privileged actions lock. These are requirements, not working locks.

| UOW | Must commit together | Work only after commit |
|---|---|---|
| Consent, profile, preference, pause or birth correction | Expected revision check, affected data, aggregate and directional counters, mapping/snapshot invalidation, idempotency receipt, outbox events | Resolution/invalidation/notification task dispatch; worker rechecks current version |
| Like and reciprocal match | Ordered account/pair locks, full eligibility recheck, directional action, one canonical pair match if reciprocal, one logical match event and receipt | Channel provisioning/notification through bounded deduplicated worker |
| Block/unmatch/suspend/delete access | Relevant account/pair locks and counters, contact revocation, session epoch/revocation as applicable, durable provider steps, outbox; deletion job+tombstone when deleting | Provider revocation/purge. Worker must not reactivate a revoked binding from a late completion |
| Send | Same revocation lock boundary, current two-party eligibility/contact version, dedup digest, bounded submission spool and outbox | Recheck contact version before provider dispatch; prove no direct SDK bypass and in-flight policy in P06/P11 |
| Staff action | Validated external actor/scope and object ownership, reasoned transition, immutable staff audit and outbox | Narrow provider action/reconciliation with no elevated WordPress database access |
| Inbox or worker completion | Verify signature outside data mutation; then unique event receipt/digest, current identity/version check, derived state and new outbox event if needed | Acknowledgment; stale/duplicate events cannot overwrite current state |

Idempotency keys are scoped to authenticated actor and operation; changed target
or other canonical request content under the same key is a conflict, not a second
action. Completed records keep an immutable outcome code, object UUID and its
committed revision. P05.3 adds `liked`, `passed`, `unmatched`, `blocked` and
`unblocked` to the existing `committed` code in the static definition and matching
unapplied migration. These identify the original logical result independently of
the object's later state. They do not cache a private response or grant. Replay first rechecks
current authorization, preserves that logical receipt, then builds only a current
safe projection (or generic unavailable/denied if revoked/deleted). The object
may since have changed; never mislabel its current version as the original result.
Only successful committed actions get this receipt; a precondition/authorization
failure does not become an indefinitely cached grant or denial. Digests summarize
validated canonical requests and are not credential cryptography. Crash before
commit leaves neither state nor event. Crash after commit requires redelivery;
logical event uniqueness does not establish exactly-once external transport.
Outbox payload references must target an existing owning record retained through
delivery/reconciliation (for example, a message submission or provider step).
No event relies on rereading a body already erased by deletion. Leases/retries have
configured finite limits and dead-letter reconciliation; no retry duration is
selected by schema defaults.

## Erasure, retention and restore

Retention categories and unresolved A05 decisions are governed by
[initial privacy and safety rules](privacy-and-safety-rules.md). No null deadline
means retain forever, and no missing policy authorizes a completed-purge claim.
Operational launch remains blocked on an approved category schedule and owners;
P02 static design can proceed without choosing durations.

Hard purge is deliberate after immediate revocation. Record tombstone, required
provider obligations and preserved restricted evidence first. Delete/detach
`EngineIdentity` before its `BirthInput` target because that FK uses `PROTECT`.
Delete app-private dependent rows in their reviewed order; remove `AppAccount`
before its protected auth user. Delete auth/allauth state through maintained
library lifecycle behavior, not raw guessed table names. Safety references use
`SET_NULL`; their preserved marker, descriptions and evidence remain restricted
under the actual retention decision. Provider deletion steps/tombstones protect
the deletion job so ordinary cascading purge cannot erase obligations.

Restore runs in isolation: deny user traffic, replay tombstones and revoked access,
reconcile processor steps, then verify no deleted account/session/device/channel
can regain access before opening the restored target. Backup configuration alone
does not establish this behavior. Cross-row subject equality, required provider
step completion and actual retention exceptions must be checked before marking
deletion complete.

## What static checks establish

`python -m glow_persistence.static_check` checks Django model metadata and exact
committed migration/model state equality using `MigrationLoader(connection=None)`.
Tests check outbox-before-domain ordering, identity delegation, tombstone FK
behavior as declared, pair/version constraints, wire field bounds and isolation
from the fixture API registry. They block connection/cursor/schema calls.

These results establish no SQL syntax acceptance, enforced database constraint,
atomic repository, actual allauth behavior, index performance, provider purge,
encryption configuration or restore outcome. The exact remaining cases are
[DB01–DB13, PV01–PV08 and PR01](../testing/p11-deferred-acceptance.md).

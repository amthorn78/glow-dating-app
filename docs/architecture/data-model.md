# Static application data model

P02.2 defines 32 app-owned Django models and two migration files in
`services/api/glow_persistence/`. P06.2 Stage A adds two models, `ChatIdentity` and
`ChatReadCursor`, in a third migration, `0003_chat_identity_read_cursor`, which only
creates them; `0001` and `0002` are byte-identical to P02's. These are **unapplied
design artifacts**: the fixture API does not install this app, and no migration is
applied anywhere but a disposable proof database. P06.2 Stage A adds the first ORM
code over them, the chat contact adapter and its outbox delivery (`services/api/glow_chat`,
below), which run only under the disposable-PostgreSQL proof's settings; the API's
runtime imports none of it and keeps its dummy backend. No real authentication or
deployed queue exists. The P11 [migration plan](../operations/migration-plan.md) owns
activation order.

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
| `ChatIdentity`, `ChatReadCursor` (P06.2, migration 0003) | One provider user ID per account and provider; provider/user reference unique; active or deactivated; the cut-off of the latest per-user token revocation the provider confirmed. Account FK is PROTECT. One read cursor per match and member, pointing at the last read `MessageSubmission` (PROTECT). | The user reference is `secrets.token_hex(16)`, never derived from an account ID, name or email, never shown or logged; no name, image or custom field exists to send. The mapping outlives the account row until the provider deletion step that needs it has run (P07/P08); purge removes cursors before the submissions they name. Unread is counted from Glow's own accepted submissions after the cursor; the provider's read state is not used. |
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

## Chat contact and the outbox (P06.2 Stage A)

The [P06.2 brief](../planning/p06-2-chat-integration.md), revision 2, items 1 to 4.
The domain port is `glow_domain/chat.py` (`ContactPersistence`); the persistence
adapter that implements it is `glow_chat/contact.py` (`OrmContactPersistence`); the
outbox delivery is `glow_chat/delivery.py`; the chat provider port and its fixture
adapter are `glow_domain/chat_provider.py` and `chat_provider_fixtures.py`; the token
rules are `glow_domain/chat_tokens.py`. The adapter is a new package rather than code in
`glow_persistence`, so that the model registry stays definitions only (its static check
still forbids every connection) and the runtime's seal names one package it must never
import. The disposable-PostgreSQL proof (`proofs/postgres-ordering`) runs P06.DB's race
suite against this adapter as its second subject; that run, not this page, is the
evidence ([evidence record](../testing/evidence/2026-10-05-p06-2-chat-integration.md)).

**The transaction design** is P06.DB's reference design (its brief, D5), carried as
written: `READ COMMITTED`; row locks by primary key with `SELECT ... FOR UPDATE` in one
canonical order (the lower account, the higher account, the match, the sending session);
every check in code under the locks, with the time read after them; authorize, then
deduplicate; a locked read that finds no row refuses; deletion is the lifecycle
transition. The send writes its `MessageSubmission` and its `OutboxEvent` in one
transaction. The adapter has no test switch; a caller may observe a writer's hold points
(`TransactionProbe`), which only signal and wait.

**The send's checks beyond P06.DB's** (D5): both profiles must be `visible`, and both
accounts' latest onboarding consent decision must be `accepted`. The consent is F02's
`ConsentIntent`, held as `ConsentDecision` rows with **`purpose` `onboarding`**
(`glow_domain.chat.ONBOARDING_CONSENT_PURPOSE`); decisions are append-only, and the
latest is the highest version. The pause, the restriction and the consent withdrawal
each lock the account row first and bump the version of the row the send reads (the
profile's, or a new decision's), so the send, holding both account locks, reads them
current. A resume restores a paused profile; nothing in Stage A lifts a restriction
(P07). Until P07 sets Nathan's policy, an unknown or paused state denies contact (F06).

**Provider identifiers** are random and committed before any provider call: a match's
activation creates the match, each member's `ChatIdentity` if it has none, and the
`ChatBinding` with a random `channel_ref` (state `pending`), with the channel's outbox
event, in one transaction under both account locks. **Limits (Codex's review of PR29, CX4 and CX5):** this
activation checks only the accounts' state, an active block and an existing pair, not
reciprocal likes, a paused or restricted profile or the onboarding consent, so it is the
proof's way to make a match, not F09's activation, which P11 wires with those checks
under the same locks; and the provider port has no user provisioning step (the fixture
creates users inside `create_channel`). Both are carried to Stage B. A send stores its provider message
ID in `MessageSubmission.provider_message_ref` when it is authorized; acceptance by the
provider moves the submission to `accepted`. A send is accepted into a `pending` or
`active` binding: its event queues behind the channel's creation.

**Outbox events** (schema version `glow-chat-1`). Each carries only its aggregate, its
version and a payload reference. Five are delivered, each as exactly one provider call:

| Event (aggregate) | Written by | Provider call on delivery | Receipt recorded |
|---|---|---|---|
| `match_activated` (match; payload the binding) | match activation | create the channel with exactly the two members | `ChatBinding.state` `active` |
| `message_submitted` (submission) | an authorized send | send the message on the member's behalf, with its committed ID | `MessageSubmission.state` `accepted` |
| `contact_revoked` (match, new contact version) | a block of an active match, an unmatch | remove both members; history stays at the provider (D6) | `ChatBinding.state` `revoked` |
| `access_revoked` (account, new epoch) | suspension, deletion | deactivate the provider user | `ChatIdentity.state` `deactivated` |
| `session_epoch_bumped` (account, new epoch) | every session-epoch bump (today suspension and deletion) | revoke the user's tokens issued before the event's time (DM-13 5.1) | `ChatIdentity.tokens_revoked_before` |

`block_changed`, `session_revoked`, `session_expired`, `profile_paused`,
`profile_resumed`, `profile_restricted`, `consent_accepted` and `consent_withdrawn` are
logical events for later consumers and make no provider call. An unmatch or a block
does not revoke tokens per user: removal suffices, and a per-user revocation would cut
the user's other matches. A single-device sign-out bumps no epoch; that device's token
lives until it expires (one hour), a residual recorded beside DB09.

**Delivery** is first in, first out over the chat events, by `(available_at,
created_at, id)`: the due events are read in that order and each, in turn, is leased by
its key in one transaction that reads what the call needs; one provider call follows
outside any transaction; a second transaction records the receipt and marks the event
`delivered`. Per channel and per user the order is the
commit order, because every writer whose events concern the same provider object locks
a common account row. A failed event that may be retried returns to the head with its
`available_at` unchanged, so nothing overtakes it, and is repeated with the same
committed identifiers, so the provider never gets a second channel, message or member.
After five attempts, or on a final code, the event is dead-lettered and the binding or
submission it concerns is marked `failed`. A message is never delivered into a binding
that is `revoked` or `failed`. Every provider error is kept only as a Glow code
(`provider_unavailable`, `provider_rejected`, `channel_unavailable`,
`member_unavailable`); no provider text is stored, logged or shown, and no column holds
the last error code in Stage A. A message authorized before a revocation committed is
delivered into the channel's history first and the members are removed after it: it stays
`accepted` in Glow's record, no member can read the channel, and nothing re-sends it.
Stage A runs delivery in-process under the proof; there is no deployed worker before P11,
and one deliverer at a time is assumed.

**Token rules** (D6): `grant_chat_token` grants one hour only for a `valid`, unexpired
session at its account's current epoch, of an `active` account with an active chat
identity; it refuses after suspension or deletion. It signs nothing; P11 serves the
endpoint and Stage B's adapter signs.
**Gap (Stage A's exact-head review, F1):** the per-user revocation's cut-off is the
epoch bump's time read before its commit, so an endpoint that reads the account without
its row lock could grant an old-epoch token after the cut-off, valid for up to an hour.
The endpoint must close it, by granting under the account row lock or by a cut-off at or
after the bump's commit; the choice is carried to Stage B and P11.

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
encryption configuration or restore outcome. (P06.DB's and P06.2's disposable-database
runs apply the migrations to PostgreSQL and exercise the chat adapter's transactions
there; they are proofs on a throwaway database, not P11's acceptance.) The exact remaining cases are
[DB01–DB13, PV01–PV08 and PR01](../testing/p11-deferred-acceptance.md).

# P05.3 interaction fixtures

**AP1-P05.3-001 revision 1.0.** This development-only composition extends
[bounded discovery](discovery-fixtures.md) with like/pass, reciprocal matching,
immutable command receipts, a simulated atomic outbox and participant unmatch.
It is nonpersistent. The [checkpoint](../testing/p05-3-checkpoint.md) owns actual
validation evidence; this architecture document does not attest checks or merge.
The dummy database, readiness 503, rejected HTTP writes, empty production paths
and guarded staging/production startup remain in place.

## Authority and identity

The actor comes from the current trusted fixture session/composition. A client
intent can name a target and expected state; it cannot supply actor authority,
reciprocity, eligibility, a profile-to-account mapping or a contact grant.
Python owns domain behavior. Mobile supplies the explicit in-memory presentation
substitute and consumes the same closed contracts and shared conformance cases.
Neither is maintained authentication, a production server or secure persistence.

| Source | Responsibility |
|---|---|
| `services/api/glow_domain/interactions.py` | `FixtureInteractionService`, bounded identity registry/repository, immutable receipts, guarded commands and a non-delivering worker observer. |
| `services/api/glow_domain/interaction_fixtures.py` | Shared-state fictional sessions; the opposite participant submits through the same service. |
| `services/api/glow_domain/discovery.py` | Current queue/batch authorization and consumption revision participation. |
| `apps/mobile/src/interactions/` | Development command substitute, request coordination and match presentation. |
| `packages/contracts/fixtures/interactions-v1.json` | Shared fictional mappings, provisional policy, bounds and command traces. |

[`interactions-v1.json`](../../packages/contracts/fixtures/interactions-v1.json)
owns the fictional identity bridge, policy and shared command traces. It maps
the discovery viewer and fourteen candidates to distinct lowercase account and
profile UUIDs. Development names such as `profile-jules` are never silently
accepted by the production UUID decoder. The composition owns the mapping from
the current development queue to its UUID batch and binds viewer/session, mode,
queue membership, source revision and expiry. A copied ID or mapping assertion
confers no authority. Canonical pairs use ordered app account UUIDs, not profile,
session, queue or engine chart identifiers.

A new like/pass requires current authorized batch membership and independently
reacquired eligibility for both people. Both preference/block directions,
policy, consent, visibility, media, safety and source/time revisions remain
relevant. Expected versions are rejection preconditions. Neither a displayed
card nor a prior compatibility response is sufficient. Interaction commands do
not calculate compatibility or request chart/provider work; Human Design scores
and synthetic provider output have no role in match formation.

## Directional state, pair state and consumption

| State or intent | Fixture rule |
|---|---|
| No directional record → like/pass | Create the submitting actor's unique ordered record at revision one after current authorization. A like alone reveals no other person's action and creates no match. |
| Repeated same directional action | Distinguish replay from a new versioned command; never duplicate the directional record or pair event. |
| Pass → like, undo or resurfacing | Unavailable under `development-interactions-1`; no refresh/mode change supplies missing A05 permission. |
| Second accepted reciprocal like | The system may create one active canonical pair only under current two-person eligibility and legal pair state. The client cannot create a match directly. |
| Existing active/restricted/unmatched pair | Preserve one pair identity. Old likes, unblock, resume and same-value restoration never create a second pair or implicitly rematch. |
| Participant unmatch | Revoke an active/restricted pair with the current match version. Repeated unmatch is safe. It does not require discovery eligibility, available compatibility or a selected history policy. |
| Block/unblock | Own directional block revision applies. Either block denies new interaction/contact; unblock removes only that block and never restores the historical grant. |

An existing match retains its creation-time canonical key across fixture registry
incarnation changes. Lookup uses its retained participant account identities;
unmatch, block and replay never rekey or duplicate that aggregate. A source change
revokes current grants and supplies no rematch permission.

Consumption belongs to authoritative interaction state. Once an actor commits
like/pass, that direction cannot reappear as untouched merely by switching mode,
refreshing or accepting a delayed page. A historical match also cannot return
as a new opportunity while rematch policy is unresolved. Queue invalidation is
conservative: a committed action may require an explicit fresh bounded read;
it never starts an unbounded refill. Reads, pagination and refresh themselves
record no action. Another person's unilateral action remains private, including
through normal candidate selection, labels and errors.

The fixture policy selects no launch retention, resurfacing, rematch or history
rights. A05 remains the owner of those choices. Explicit developer scenarios are
fictional setup; a reciprocal like must run through the command service rather
than set a client `reciprocal` or `matched` flag.

## Version, digest and replay boundary

`expected_version` refers to the directional interaction for like/pass, match
for unmatch and directional block for block/unblock. Zero means create-only
against absence. Positive versions must equal the current object revision;
malformed or overflowing versions fail without mutation.

Deduplication identity is **actor, operation, key**, matching static
`IdempotencyRecord.intent_dedup`. Canonical intent includes the target, action,
expected version and applicable batch/evidence binding. A changed target or
other intent field under the same identity conflicts. Request correlation IDs
are independent and never become deduplication keys.

Python stores SHA-256 of its canonical serialized intent. The mobile substitute
uses a private canonical serialized-intent comparator; it does not claim an
identical cryptographic digest representation. Neither comparator is returned
in the public receipt or normal UI inspection. Both bind the exact validated
intent for replay/conflict semantics. The static persistence record retains
its digest field; P11 owns the durable encoding and adapter mapping.

Current actor/object access is checked before disclosing a replay. An existing
identity is compared to its canonical intent before new-command version/batch
checks. An identical committed command recovers the original receipt even if
its commit consumed the old batch; it does not execute again. A pending command
cannot execute twice. A new command still needs current batch authority and
the correct version. Authorization/precondition failures leave no committed
receipt or half-applied action.

The immutable `CommandReceipt` contains only outcome code, object UUID and the
version committed by that command. `InteractionCommandResult` separates it from
`current_projection`, which is rebuilt under present access and may be null.
A directional projection also requires its original stored source guards, binding
identities and matchability; fresh eligibility cannot revive revoked original
authority. A receipt describing a past `liked` action does not promise a current active
match; later unmatch/restriction never rewrites the receipt into a new outcome
or returns a cached grant. Revoked/deleted access receives generic unavailable
behavior. Neither receipt nor event caches private profile/birth/chart data.
These internal types do not activate an HTTP response or production route; see
[closed contract rules](production-contracts.md).

The shared command limits are **200 receipts** and **200 discretionary events**
per fixture repository. Python's registry accepts at most **20 identities**;
an additional reserved allowance of at most **190 source-driven revocations**
corresponds to the possible unordered pairs. Each active pair can be restricted
this way once; rematch is unavailable. This preserves revocation after ordinary
command capacity is consumed. Capacity refuses safely; it cannot silently evict
deduplication evidence and make an old command executable again. The Python
service retains at most one current action-batch binding per discovery mode.
Mobile retains at most 200 composition-owned command-batch bindings; reaching
that bound refuses further preparation, including reciprocal fixture setup.
These bounds and any explicit fresh fixture reset are development behavior,
not production retention, durable exactly-once processing or measured capacity.

## Synchronous commit and outbox

Stage directional changes, any canonical match/contact revision, the minimal
receipt and required logical events together. Complete callback-capable reads
first. The final guard compares participating concrete monotonic source and
owned-state revisions, then adopts the staged state synchronously without an
await or new revocable dependency read between comparison and state replacement.
A concurrent/reentrant action or source replacement makes an obsolete stage
fail; no partial directional row, match, receipt or event may remain. Removal,
same-value restoration and first block insertion remain new source incarnations.

`DevelopmentInteractionEvent` carries only its UUID, kind, aggregate UUID and
version, and `gapp-interactions-fixture-v1` marker. The supported logical kinds
are `match_created`, `contact_revoked` and `block_changed`. Match creation has one
canonical identity/event; revocation and block changes are version-bound. A
controlled `FixtureInteractionWorker` records `observed_no_delivery`,
`duplicate` or `stale` for accepted observations; it refuses unknown events and
capacity overflow. It delivers no Stream channel, token, notification, message
or external work. Late completion cannot reactivate a revoked contact version.

This boundary models participating synchronous fixture writers. It proves no
PostgreSQL isolation, thread/process locks, restart durability or external
delivery. P11 must supply persistent uniqueness, stable lock ordering, all-writer
revision updates including absent-block protection, transactionally retained
receipts/outbox and crash/replay proof. Logical event uniqueness does not imply
exactly-once provider delivery.

## Revocation, projections and mobile behavior

Current match reads are participant-scoped. Another person's unreciprocated
action, private birth input, engine reference, preferences, exact location,
moderation/block reason, provider payload and secret remain excluded. An
otherwise current active projection may reuse only the allowlisted candidate
fields and approved synthetic media. A revoked connection uses generic
unavailable copy; prior profile details are not a cached permission.

Unmatch, either-direction block and applicable account/consent/visibility/source
changes invalidate new contact decisions and retained projections. Participant
unmatch remains reachable while paused/ineligible. Unblock/resume, a repeated
like or an old completion cannot resurrect the match. No assertion is made that
past messages, safety evidence or provider bytes were erased.

Python materializes source-driven restriction during a current match read,
contact decision or interaction projection. The retained source guards already
deny the obsolete grant; this is not a background invalidation worker. The
fixture contact decision uses the current match revision as `contact_version`,
always returns `send_allowed: false` and records `provider_state: not_configured`.
The production model's separate positive `contact_version` still requires a P11
transactional mapping. It must never be substituted with an old receipt version.

Discovery has accessible Like/Pass controls; matches use participant list/detail
routes and an Unmatch action. Pending submission is separate from committed
success, and a unilateral like is separate from a mutual match. UI intent retains
target, expected version, batch/mode, request generation and idempotency key.
Retrying the same intent reuses its key. Account/session/mode/navigation changes
and newer requests prevent obsolete response adoption. Failed or lost responses
reconcile current state instead of blindly restoring a removed card. Fixture
offline/lost-response/delayed delivery controls are labeled developer scenarios.
Browser keyboard/layout and JavaScript exports do not establish signed native
builds, device accessibility or secure cross-session persistence.

Mobile `interactionsFor` retains one store/adapter per `OnboardingStore` instance
through a `WeakMap`. Navigation therefore does not create a new repository or
erase deduplication evidence. Owner/session changes discard pending adoption,
retry presentation and selected match state; retained records remain subject
to current ownership. A new preview runtime/store starts fresh nonpersistent
fixtures. This is no durable restoration or retention guarantee.

## P06 and P11 handoff

An active match plus current pair eligibility is only the input to a later
contact decision. It is not a provider channel/send/history capability. P06.1
must prove actual permissions, direct-SDK/stale-token/reconnect/outage behavior
and economics under A04/A08. Stream remains preferred; this task establishes no
account, Maker entitlement, credit or paid activation.

[Deferred acceptance](../testing/p11-deferred-acceptance.md) retains real
multi-connection reciprocal/dedup/absent-block races, send-versus-revocation,
pre/post-commit worker crashes, redelivery and restore cases. The audited P11
storage direction remains a dedicated app schema and restricted roles in HDE's
same logical database `railway`. HDE/legacy objects and shared effects stay
protected. P05.3 opens no database, runs no SQL/applied migration and activates
no HDE/provider, infrastructure or deployment.

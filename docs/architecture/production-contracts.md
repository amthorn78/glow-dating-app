# P02 production contract baseline

**Contract:** `gapp-api-v1`, first app-owned design baseline. **Implemented:** schemas, generated TypeScript, generated runtime validators, executable transition/authorization contract oracle and shared fixtures. **Not implemented:** production routes, allauth wiring, durable state transitions, provider enforcement or database integration. Existing development GET routes keep `gapp-dev-v1` and fixture-only provenance. A schema-valid response is not a permission, persisted fact or working API.

`packages/contracts/production/gapp-api-v1.schema.json` owns wire shapes. `production/openapi.json` is an OpenAPI 3.1 component catalog with an intentionally empty paths map and no server: it references the same schemas without claiming production endpoints. `packages/contracts/production/flows-v1.json` owns the F01–F20 domain/data owners, named request/response definitions, private/public/staff projections, actor roles, legal transitions and acceptance cases. Every unlisted transition is forbidden. `packages/contracts/transition_contract.py` is a database-free **contract oracle** for tests; it is not installed into the API, an auth adapter, or a second domain backend. Production services must enforce these rules using trusted acquisition and a real unit of work.

## Wire and error rules

- Requests are closed intent DTOs, never client-set eligibility, consent-truth, staff roles or actor identity. The adapter derives the actor from maintained authentication. Production transport/route implementation is later work; these logical request contracts deliberately do not invent active URLs. Reads use authenticated self context or `OwnedObjectRequest`, with server-side ownership/membership/scope checks before projection.
- Success envelope: `contract_version`, opaque `request_id`, and closed `data` discriminated by `kind`. Errors use the separate closed `Error` definition. Unknown fields/versions fail validation. All additions to a closed payload need a new negotiated contract version; existing `gapp-api-v1` consumers must not silently accept them. No version inference from URLs or SDK versions.
- New app identifiers are lower-case UUID text; values are opaque. Account IDs and engine IDs are never interchangeable. Resource versions are integers 1 through JavaScript's safe-integer maximum. `expected_version=0` means create-only against absence; positive values require an existing matching version. Birth/mapping/policy versions use their explicit domain mapping; no numeric coercion from untrusted strings.
- Required nullable fields express known absence/unresolved state. An omitted required field is invalid. Commands use complete replacement of their specified editable fields; no implicit JSON merge patch. `null` never means “leave unchanged.” App timestamps are valid Gregorian UTC instants, years 0001–9999, whole seconds, exact `YYYY-MM-DDTHH:mm:ssZ`. Birth date/local time are civil facts; timezone name/provenance remain separate nullable fields. Unknown birth time requires null time; approximate time retains the entered value. No silent UTC conversion or guessed precision.
- Text lengths count Unicode scalar values, not UTF-16 units or grapheme clusters. Unpaired surrogates are invalid. No trim, case folding or Unicode normalization happens in decoding. Nonblank text uses the explicit Unicode White_Space code-point set plus BOM, identically in both validators; zero-width space is not part of that set. Content moderation may impose stricter policy later. ASCII identifiers/version labels prohibit all trailing newlines, including the JavaScript/Python end-anchor corner case.
- Public support/deletion contact uses a bounded ASCII mailbox locator pattern, **not** a complete email grammar or verification result. Quoted/internationalized addresses require an explicit future contract extension after maintained auth support is pinned. Authentication email formats remain owned by allauth. Delivery/ownership is never inferred from syntactic validity.
- Numeric/text/collection limits in the schema are transport ceilings, not selected launch geography, allowed preference categories, media business limits, retention or pricing. The API must apply a current narrower configured policy; missing relevant policy returns `policy_unresolved`. A recommendation page has at most 50 entries; a model batch may hold a larger bounded set across pages. Candidate/profile IDs and preference dimension keys must be unique; `runtime.py` and mobile `validation.ts` implement this small standard-schema supplemental rule. Whole-object `uniqueItems` is insufficient for key uniqueness.

| Error code | Planned HTTP mapping | Required behavior |
|---|---|---|
| `invalid_request` | 400 | Reject malformed/unknown fields without echoing submitted secrets/text |
| `unauthenticated` | 401 | Restart maintained authentication; no cached authorization fallback |
| `forbidden` / `not_found` | 403 / 404 | Generic unavailable object; do not reveal another person's block, report, suspension or private facts |
| `state_conflict` / `stale_version` | 409 | Discard optimistic result, reload current authorized projection and explicitly re-evaluate the user's intent |
| `idempotency_conflict` | 409 | Same key with different canonical intent must not execute |
| `policy_unresolved` | 409 | No permissive default; operation remains unavailable |
| `unsupported_contract` | 409 | Require supported client/server contract mapping, no guessed downgrade |
| `provider_unavailable` | 503 | Typed temporary failure; retry only where documented and still authorized |
| `rate_limited` | 429 | Bounded retry; actual time budget provided through transport metadata |

Messages shown to users come from controlled client copy keyed by code; the error DTO carries no stack trace, request body, provider details or raw validation errors. `retryable` does not authorize an automatic mutation retry without the same idempotency identity and fresh access check. Public unauthenticated support/deletion acknowledgments always use `PublicRequestReceipt`, never account existence or job IDs. Public deletion is only a request to verify identity, not a deletion command. This does not implement or certify enumeration resistance.

## Pagination, idempotency and stale state

P05.2 implements a separate, closed development adapter page and bounded queue
under [discovery fixtures](discovery-fixtures.md). It does not activate these
production contracts, add production paths or turn the anonymous development GET
into authenticated discovery. Its synthetic limits/order and opaque in-memory
handles are test choices, not production policy or cursor cryptography.

`PageRequest` requests a bounded recommendations/discovery collection. `CandidatePage` identifies the batch/version/expiry and an opaque nullable next cursor. The future repository cursor binds authenticated viewer, collection, batch/version, policy and both-sided eligibility revisions, and stable position. It contains no private payload; reject a forged, wrong-viewer, wrong-collection, stale or expired cursor with a generic stale response. A cursor grants no permission. Ordering is stable within a batch; refresh produces a new version. `empty` is valid and never triggers HDE work merely to fill a list. Non-ready pages expose no items or continuation cursor. Final ranking/granularity remains A01/A07.

Every mutating intent contains an idempotency key and expected version. The future unit of work scopes deduplication to authenticated actor, operation, target and key and stores a canonical-payload digest plus result atomically with the domain change/outbox. Same key/same payload returns the prior logical command outcome **only after current authorization and safe projection checks**. Retain a minimal immutable receipt (outcome code, object reference and committed version) with the idempotency record; an object reference to a mutable row alone cannot reconstruct the original result. Replay never promises identical response bytes or renews media/export grants. Fetch any current private projection separately under present access rules; return generic unavailable when access has been withdrawn. Different payload conflicts; pending operation cannot run twice. Request IDs are diagnostics, not idempotency keys. Scope-specific retention/expiry for deduplication remains A05; no duration is invented. Expired deduplication records require authoritative state inspection and must not imply safe blind replay. At P11, prove simultaneous reciprocal likes yield one canonical match and one logical outbox event.

Before new discovery, like or contact authorization, follow [trusted eligibility](trusted-eligibility.md): authenticated server identity, exact ordered account pair, both snapshot revisions, policy revision, both preference directions and both block directions. Wrong-pair evidence is rejected; stale versions reload/re-evaluate; missing policy denies. Consent withdrawal, suspension, block, pause and deletion invalidate dependent projections. Both participants are checked before chart/provider work. PairEvidenceVersion is an optimistic precondition, never a client authorization claim. Generic public errors hide the internal exclusion reasons. Profile/birth/media edits must validate their own current owner and object version as well.

The production transaction must lock or otherwise serialize current account/relationship versions and recheck immediately before committing an interaction/send entitlement, with outbox work after commit. Match activity is independently required for channel/send permission; pair eligibility alone is insufficient. Block/unmatch commit is the boundary after which no newly authorized send may begin. The selected provider must prevent direct SDK bypass; A08 remains a required capability proof. Provider acknowledgement of a previously authorized in-flight send is distinguished from granting a new send. This P02 oracle proves none of the actual races or provider behavior.

## Maintained authentication reference and app mapping

F01 uses [django-allauth headless API specification](https://docs.allauth.org/en/latest/headless/openapi-specification/), not a custom Glow credential API. The specification is referenced, not vendored or claimed installed. Current official [session-token documentation](https://docs.allauth.org/en/latest/headless/token-strategies/session-tokens.html) and [JWT strategy documentation](https://docs.allauth.org/en/latest/headless/token-strategies/jwt-tokens.html) were inspected on 23 September 2026. The latter describes `X-Session-Token` during incomplete authentication, access/refresh pairs in `meta` on completion, Bearer access, `JWTTokenAuthentication`, refresh rotation, and optional stateful session validation. No credentials or tokens were requested.

The **planned app mapping** uses the maintained JWT strategy with stateful validation enabled and refresh rotation enabled to satisfy the governing revocation requirement. Configure short-lived access with the selected installed release; no custom signing or token store. Pin the actual allauth release and generated configured specification during auth implementation before activating an adapter. Session/auth success maps to app account identity through its explicit one-to-one auth-user binding. Provider user IDs, email, session tokens and JWT claims never become candidate profile IDs or chat entitlements. A verified email alone does not establish adult, consent, profile, moderation or pair eligibility. App account suspension/deletion additionally revokes access regardless of remaining token lifetime. Auth recovery/revocation and safe linking remain delegated to the maintained interface and must be validated with actual persistence at P11. Staff identity is separately scoped; WordPress login alone never grants dating API authority.

The oracle's `auth`, `provider` and `system` roles are controlled fixture labels for trusted adapters, never client request values. User/staff roles also require a valid server session, correct owner/participant mapping, and case-specific grants for staff reads/actions. `presentation` can change only native presentation states. None of these fixture contexts is proof of real authentication.

## Flow contract and acceptance matrix

The following index is generated from the committed flow registry. Detailed projection allowlists and every legal event/source/target/role/policy tuple are in that registry. Named `test_f01` through `test_f20` tests exercise allowed/forbidden behavior and privacy/role separation; provider, SQL and native deferred proofs remain explicit in [P11 cases](../testing/p11-deferred-acceptance.md).

| Flow | Domain / data owner | Request → response definitions | Acceptance |
|---|---|---|---|
| F01 | identity / App account metadata; maintained allauth credentials/session | allauth-headless → AccountAccess | Expired/replayed credential rejected by maintained auth; fixture contract rejects ordinary user verification and revoked-session access |
| F02 | identity/consent / App | ConsentIntent → OnboardingEligibility | Unverified/underage/withdrawn/suspended cannot use discovery; old consent version rejected |
| F03 | birth/engine mapping / App private input/mapping; HDE charts | BirthInputIntent → OwnBirthInput | Unknown time remains unknown; changed input invalidates old mapping; engine identifiers never invented |
| F04 | profiles/preferences / App | ProfileIntent, PreferencesIntent, OwnedObjectRequest → OwnProfile, OwnPreferences | Wrong owner edit/read rejected; unknown dimension/option policy rejected; public birth leakage rejected |
| F05 | profiles/media / App status; provider bytes | MediaIntent, OwnedObjectRequest → MediaLifecycle, MediaUploadGrant, MediaCollection | Upload cannot skip quarantine/review; wrong owner reorder/remove fails; provider purge completion separate |
| F06 | profiles/eligibility / App | VisibilityIntent → OwnProfile | Pause invalidates queues; resume rechecks current visibility eligibility; unknown pause/contact policy denies contact |
| F07 | eligibility/discovery / App bounded queue; HDE permitted output | PageRequest → CandidatePage | Wrong-viewer/stale cursor rejected; no eligible candidates returns empty and no provider call |
| F08 | interactions / App | InteractionIntent → InteractionOutcome | Repeated key identical intent yields same result; changed payload conflicts; stale/ineligible target denied |
| F09 | matches / App | InteractionIntent, OwnedObjectRequest → MatchProjection | Reciprocal likes only; one unordered pair and logical event; unilateral client match creation denied |
| F10 | matches/communication / App entitlement; provider revocation | UnmatchIntent → MatchProjection | Participant unmatch revokes contact without owner-policy prerequisite; unmatch never grants rematch |
| F11 | communication / App entitlement/submission; provider message bodies | ChannelIntent, MessageIntent, OwnedObjectRequest → ChannelEntitlement, MessageSubmission | No send after block/unmatch commit; SDK token alone insufficient; pending submission is not delivery |
| F12 | communication / App settings/devices; push provider | NotificationIntent, DeviceIntent → NotificationSettings | Token rotation owner/session bound; logout revokes registration; no duplicate push; denied platform permission is normal |
| F13 | safety / App block; provider revocation | BlockIntent → BlockOutcome | Block works after unmatch and while paused; unblock cannot restore match/send entitlement |
| F14 | safety / App report/case; restricted provider evidence | ReportSubmission, OwnedObjectRequest → ReportReceipt | After-unmatch reporting allowed; other account receipt/evidence denied; malicious description never rendered as HTML |
| F15 | safety/moderation / App case/action/appeal/audit; WordPress staff identity | StaffCaseAction, AppealSubmission, OwnedObjectRequest → StaffCaseProjection, AppealProjection | Support role cannot suspend; actor/scope and current policy required; unrelated user cannot appeal |
| F16 | support/CMS / App support; WordPress public policy | SupportRequest, PublicSupportRequest, OwnedObjectRequest → SupportProjection, PublicRequestReceipt | Support staff cannot read birth/message evidence or invoke case action; wrong-owner status hidden |
| F17 | privacy / App export; provider-owned data under contract | ExportRequest, OwnedObjectRequest → ExportProjection | Wrong owner/expired grant denied; partial provider failure is failed/preparing, never ready |
| F18 | privacy/all domains / App jobs/tombstones; providers own purge; HDE unresolved | DeletionRequest, PublicDeletionRequest, OwnedObjectRequest → DeletionProjection, PublicRequestReceipt | Request immediately denies access/visibility; unresolved provider obligations prevent completed; restore replays tombstone |
| F19 | mobile presentation / API remains authorization owner | AppIntent → AppResponse, Error | Offline/stale response cannot authorize writes; accessible buttons submit same intents; native proofs deferred |
| F20 | entitlements / Verified provider lifecycle; app derived state |  → EntitlementProjection | Every attempted enable/purchase/restore is denied until new owner-selected versioned provider contract |

## Policy boundaries and deliberately unavailable operations

A05 owns launch geography/language, adult clock, preference dimensions/options, resurfacing, rematch, existing-history behavior, media operating rules, named moderation/support owners and retention. Schema labels are opaque policy references; they do not choose these values. `consent_current`, `media_policy`, `reciprocal_likes`, `export_complete` and `purge_verified` in the oracle are explicit trusted test prerequisites, not additional owner decisions. A resolved policy must match the current resource/policy revision; the oracle only models its presence, and trusted domain acquisition provides the production binding.

Rematch is absent from legal transitions until its policy is selected. Unblock removes the block only; it cannot restore a match, channel or history grant. Pause denies new discovery/contact until policy resolves; reporting, blocking and authorized privacy/support requests remain available independently of discovery eligibility. All public profile projections exclude private birth values, chart IDs, account/session identifiers, private preferences, exact location and nonreciprocal likes. Birth/chart corrections invalidate prior mapping/result revisions. No ready live compatibility projection is serializable in this baseline: A01/A07 must establish display/cache rights and supported fields before a versioned extension.

MediaUploadGrant contains an opaque app grant reference and expiry; the later media adapter maps it to the selected provider's supported upload mechanism with owner/type/size/count restrictions and approved origin. It is neither a provider endpoint nor proof of an uploaded asset. Original/quarantined/rejected/removed media cannot expose an approved-delivery reference. Upload grants and export-download grants are secrets outside routine logs, and must be rechecked on use. Export ready requires a delivery grant and expiry; other states cannot expose one. Completed deletion has no unresolved obligation labels. Engine deletion rights and shared-chart obligations remain A01; provider evidence and retention decisions are required before completion, never inferred from a schema-valid payload.

F20 serializes disabled only; no purchase intent, price, provider activation or owner-selected paid scope exists. F19 consumes the other contracts and has no authorization role. Actual screen readers, denied permissions, devices, deep links, signed builds and store acceptance remain later work. Generated JavaScript export is not native acceptance.

### P04.3 media collection and binding clarification

The existing per-asset `MediaLifecycle.version` could not supply the aggregate
precondition needed for a complete approved-photo reorder. P04.3 adds the closed
owner response `MediaCollection`: `kind: media_collection`, positive `version`,
and at most 20 `MediaLifecycle` items with unique `asset_id` values. The empty
collection has version 1. The 20-item bound is a transport ceiling; the separately
versioned development policy may impose a lower active-photo limit. Existing
`MediaIntent`, `MediaLifecycle` and `MediaUploadGrant` payloads do not gain fields.
This new response discriminator extends the unpublished design catalog and is
consumed by the generated fixture client in this same repository. No HTTP route
or deployed-client negotiation is activated. Older validators reject the new
discriminator; a deployed transport must negotiate support before returning it.
The rule requiring a negotiated version for changed existing closed payloads
continues to apply.

`request_upload` and `reorder` use `CommandMeta.expected_version` against the
current owner's collection revision; `remove` uses the target asset revision.
`request_upload` keeps null `asset_id` and an empty order list. `remove` requires
its owned asset and an empty order list. `reorder` keeps null `asset_id` and sends
the complete nonempty permutation of currently approved owned assets. It cannot
omit or inject an asset, approve media, or restore an asset concurrently removed
or restricted. Collection revisions advance on accepted membership, lifecycle
and ordering changes, so stale commands fail even when a particular asset's
revision was unchanged. The response carries no owner assertion; authenticated
owner/session context governs lookup and the validated result adoption boundary.

Immutable selected bytes, detected content properties and the policy revision
bind to the captured owner/session/generation, asset, grant and upload attempt
inside the media adapter. They are not undeclared intent fields or public
projection fields. A grant is a capability reference to that immutable binding,
not a filename or permission to substitute bytes. Idempotency compares the same
captured intent and private selection binding: same key/same payload may replay
only after current authorization; changed selection or payload conflicts. Grant
replacement creates a fresh identity and cannot be consumed by a delayed earlier
attempt. Fixture acknowledgment validates the staged result before mutation;
that boundary does not prove PostgreSQL/provider atomicity.

The existing 32 models and two unapplied migration definitions remain unchanged.
`MediaAsset` already defines owner, per-asset version, state, position, storage and
approved-variant references. Durable aggregate revisions, private byte/grant
binding, replay receipts and provider-event transactions still require the P11
persistence design and integration cases; static agreement does not provide
those guarantees.

### Compound actions and model projections

An incomplete/paused/restricted/removed own profile may retain an empty bio; a visible candidate may not. ProfileIntent can clear the bio, but the service must then remove visibility if completeness fails. `Profile.bio` maps to DTO `summary`; `location_label` is intentionally not exposed by the present public allowlist. Unset preferences map to null policy version and empty selections; policy-less JSON never authorizes discovery. Birth corrections from ambiguous, pending, unavailable or unsupported states return to pending under a new input version, without granting HDE resolve permission. A valid new maintained session can re-register the same revoked device installation with a new provider token; a revoked session cannot.

A scoped `StaffCaseAction.restrict_media` names the exact asset, verifies its relation to the current case and both object grants, and uses the current A05 moderation policy. Its immediate safety effect retracts approved delivery and returns the asset to review_pending while the case remains investigating; it does not preselect rejection, removal or an appeal outcome. The case audit, asset change, projection/version invalidation and outbox are one future UOW. Account suspension uses F01's scoped moderator transition, also audited against the case. Deletion request similarly combines F18 requested/access_revoked, F01 deletion_pending and F04 removed plus session/contact revocation in the same future commit; purge completion is separate and policy/provider dependent. Contract tests exercise these component transitions, not atomic multi-object persistence.

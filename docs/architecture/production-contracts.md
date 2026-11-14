# P02 production contract baseline

**Contract:** `gapp-api-v1`, first app-owned design baseline. **Implemented:** schemas, generated TypeScript, generated runtime validators, executable transition/authorization contract oracle and shared fixtures. **Not implemented:** production routes, allauth wiring into the runtime (SV1 configures allauth and proves it only under the disposable-PostgreSQL proof's settings; "Maintained authentication reference and app mapping", below), durable state transitions, provider enforcement or database integration. Existing development GET routes keep `gapp-dev-v1` and fixture-only provenance. A schema-valid response is not a permission, persisted fact or working API.

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

Every mutating intent contains an idempotency key and expected version, with one exception: `ReadCursorIntent` carries neither, since it only moves the member's own read cursor forward and a repeat changes nothing ("F11 under OD-45", below; C1's exact-head review, finding 2). Deduplication is unique by **authenticated actor, operation and key**, matching `IdempotencyRecord.intent_dedup`. The target and every intent-defining field belong in the canonical-payload digest; target is not an additional uniqueness dimension. Reusing a key for another target therefore conflicts instead of executing a second action. The future unit of work stores the digest and result atomically with domain changes/outbox. Same key/same payload returns the prior logical command outcome **only after current authorization and safe projection checks**. Retain a minimal immutable receipt (outcome code, object reference and committed version) with the idempotency record; an object reference to a mutable row alone cannot reconstruct the original result. Replay never promises identical response bytes or renews media/export grants. Fetch any current private projection separately under present access rules; return generic unavailable when access has been withdrawn. Different payload conflicts; pending operation cannot run twice. Request IDs are diagnostics, not idempotency keys. Scope-specific retention/expiry for deduplication remains A05; no duration is invented. Expired deduplication records require authoritative state inspection and must not imply safe blind replay. At P11, prove simultaneous reciprocal likes yield one canonical match and one logical outbox event.

Before new discovery, like or contact authorization, follow [trusted eligibility](trusted-eligibility.md): authenticated server identity, exact ordered account pair, both snapshot revisions, policy revision, both preference directions and both block directions. Wrong-pair evidence is rejected; stale versions reload/re-evaluate; missing policy denies. Consent withdrawal, suspension, block, pause and deletion invalidate dependent projections. Both participants are checked before chart/provider work. PairEvidenceVersion is an optimistic precondition, never a client authorization claim. Generic public errors hide the internal exclusion reasons. Profile/birth/media edits must validate their own current owner and object version as well.

The production transaction must lock or otherwise serialize current account/relationship versions and recheck immediately before committing an interaction/send entitlement, with outbox work after commit. Match activity is independently required for channel/send permission; pair eligibility alone is insufficient. Block/unmatch commit is the boundary after which no newly authorized send may begin. The selected provider must prevent direct SDK bypass; A08 remains a required capability proof. *(That sentence is P02's baseline, superseded by OD-45: the app holds no provider SDK or credential, so the client has no direct provider path; see "F11 under OD-45", below. C1's exact-head review, finding 2.)* Provider acknowledgement of a previously authorized in-flight send is distinguished from granting a new send. This P02 oracle proves none of the actual races or provider behavior.

## Maintained authentication reference and app mapping

F01 uses the [django-allauth headless API](https://docs.allauth.org/en/latest/headless/openapi-specification/), not a custom Glow credential API. **SV1 built the mapping** (the [SV1 brief](../planning/sv1-identity.md), revision 5; the [SV1 evidence record](../testing/evidence/2026-11-09-sv1-identity.md)) on the pinned release, **django-allauth 65.21.1** (`django-allauth[headless]`, hash-pinned in `services/api`'s development scope and the disposable-database proof's lock), in `services/api/glow_identity`. It is **sealed until P11**: it runs only under the proof's identity settings, on a disposable PostgreSQL, and the served runtime imports none of it. No credentials or tokens were requested; every key the proof uses is generated for one run.

**The configured specification is pinned, not vendored.** Generated once on 9 November 2026 in a scratch environment with the release's `headless-spec` extra, from 65.21.1 and SV1's settings (the `app` client only): OpenAPI 3.0.3, with SHA-256 `56d639eb5b1d997a99f24ca22ccce0b72bad124da0ea383763468085ddce6c35` for the YAML allauth serves (`yaml.dump` of `get_schema()`, 95,752 bytes) and `212d6758d6d64eaed54870e2c1cf3870286ad31becf1e349c576a369c0d655ef` for its JSON (78,289 bytes). Its 17 paths, all under `/_allauth/app/v1/`: `account/email`, `account/password/change`, `account/phone`, `auth/code/confirm`, `auth/email/verify`, `auth/email/verify/resend`, `auth/login`, `auth/password/request`, `auth/password/reset`, `auth/phone/verify`, `auth/phone/verify/resend`, `auth/reauthenticate`, `auth/session`, `auth/sessions`, `auth/signup`, `config` and `tokens/refresh`. The installed release mounts the phone routes and `auth/code/confirm` whatever the configuration (login by code's request routes only when it is enabled); SV1 configures neither phone numbers nor login by code, Glow's adapter refuses a signed-in phone request (403) where allauth's default would raise, and the evidence records each route's refusals. `HEADLESS_SERVE_SPECIFICATION` stays off; the scratch generation turned it on only so that allauth's builder could reverse its own route.

**The app mapping as built.** The maintained JWT strategy (RS256), through Glow's subclass, with stateful validation enabled (each access token is checked against its session, its user and that user's password hash) and refresh rotation enabled; access tokens live 300 seconds and refresh tokens 30 days, and the `AccountSession` 30 days from sign-in, with the Django session's expiry set to the same instant. A refused refresh token that passes allauth's own checks, its signature first, but carries an identifier its session no longer holds ends that session at both layers. No custom signing, token store or cryptography: allauth's functions decide every check, and the signing key and `SECRET_KEY` are secret references P11 supplies. Sign-up is email and password; verification and password reset are by code, never by link; enumeration prevention is allauth's (`ACCOUNT_PREVENT_ENUMERATION = True`), and allauth's unknown-account mail is off (`ACCOUNT_EMAIL_UNKNOWN_ACCOUNTS = False`), so a reset for an address with no account sends nothing. Session/auth success maps to app account identity through its explicit one-to-one auth-user binding, and each sign-in opens an `AccountSession` whose reference is allauth's `UserSession` primary key, a non-secret library identifier; the session key itself is a credential (`meta.session_token`, accepted by allauth's endpoints as `X-Session-Token` for the session's whole life), which the app keeps only in the platform's secure storage, or not at all once the token pair arrives (carried to P11's client wiring). The app sends one refresh at a time: a second refresh with the same token, or a retry after a lost response, is a replay that ends the session.

**The actor, and `AccountAccess`.** One DRF authentication class (`glow_identity.authentication.GlowActorAuthentication`) is the only way a later slice gets an actor: allauth's `JWTTokenAuthentication`, then the session from the validated token's own `sid` (never a header), then the account `active` and the session `valid`, unexpired and at the account's current epoch, or `unauthenticated` (401). SV1 serves one Glow route, the member's own `AccountAccess`, in the `AppResponse` envelope (`contract_version`, `request_id`, `data`), at the sealed path `api/v1/account/access`; refusals are the `Error` shape (`unauthenticated` with a 401, `invalid_request` for another method). The production catalog's paths map stays empty until P11 serves the routes. An unverified member is still in allauth's verification flow, and a suspended or deletion-pending member is refused at sign-in, so the other `AccountAccess` states are not served in SV1.

Provider user IDs, email, session tokens and JWT claims never become candidate profile IDs or chat entitlements. A verified email alone does not establish adult, consent, profile, moderation or pair eligibility. App account suspension and deletion revoke access regardless of remaining token lifetime: `glow_chat`'s `suspend` or `delete` bumps the epoch (refused by the actor), every allauth session of the user ends, and the auth user is made inactive (refused by allauth). Logout, a password change or reset, and ending a session from allauth's session list revoke at both layers. Recovery and revocation stay delegated to the maintained interface, proven on a disposable database by SV1 and to be validated with the real target's persistence at P11. Staff identity is separately scoped; WordPress login alone never grants dating API authority.

The oracle's `auth`, `provider` and `system` roles are controlled fixture labels for trusted adapters, never client request values. User/staff roles also require a valid server session, correct owner/participant mapping, and case-specific grants for staff reads/actions. `presentation` can change only native presentation states. None of these fixture contexts is proof of real authentication.

## Flow contract and acceptance matrix

The following index is generated from the committed flow registry. Detailed projection allowlists and every legal event/source/target/role/policy tuple are in that registry. Named `test_f01` through `test_f20` tests exercise allowed/forbidden behavior and privacy/role separation; provider, SQL and native deferred proofs remain explicit in [P11 cases](../testing/p11-deferred-acceptance.md).

| Flow | Domain / data owner | Request → response definitions | Acceptance |
|---|---|---|---|
| F01 | identity / App account metadata; maintained allauth credentials/session | allauth-headless → AccountAccess | Expired/replayed credential rejected by maintained auth; fixture contract rejects ordinary user verification and revoked-session access |
| F02 | identity/consent / App | ConsentIntent, SensitiveConsentIntent, AdultCheckIntent → OnboardingEligibility, OwnSensitiveConsent, OwnAgeState | Unverified/underage/withdrawn/suspended cannot use discovery; old consent version rejected; a newer version accepted from `accepted` (`accept`, `accept_sensitive`; SV2 C2) |
| F03 | birth/engine mapping / App private input/mapping; HDE charts | BirthInputIntent → OwnBirthInput | Unknown time remains unknown; changed input invalidates old mapping; engine identifiers never invented |
| F04 | profiles/preferences / App | ProfileIntent, PreferencesIntent, OwnedObjectRequest, ProfileFieldIntent, FiltersIntent, AreaIntent, AreaQuery → OwnProfile, OwnPreferences, OwnProfileFields, OwnFilters, OwnArea, NearestArea, ProfileCatalog, OwnCompletion | Wrong owner edit/read rejected; unknown dimension/option policy rejected; public birth leakage rejected |
| F05 | profiles/media / App status; provider bytes | MediaIntent, OwnedObjectRequest → MediaLifecycle, MediaUploadGrant, MediaCollection | Upload cannot skip quarantine/review; wrong owner reorder/remove fails; provider purge completion separate; `approve` and `reject` are the automated check's (`system`; SV2 Stage B, OD-61), and `restrict_media` stays the moderator's |
| F06 | profiles/eligibility / App | VisibilityIntent → OwnProfile | Pause invalidates queues; resume rechecks current visibility eligibility; unknown pause/contact policy denies contact |
| F07 | eligibility/discovery / App bounded queue; HDE permitted output | PageRequest → CandidatePage, CandidateCardPage | Wrong-viewer/stale cursor rejected; no eligible candidates returns empty and no provider call |
| F08 | interactions / App | InteractionIntent → InteractionOutcome | Repeated key identical intent yields same result; changed payload conflicts; stale/ineligible target denied |
| F09 | matches / App | InteractionIntent, OwnedObjectRequest → MatchProjection | Reciprocal likes only; one unordered pair and logical event; unilateral client match creation denied |
| F10 | matches/communication / App entitlement; provider revocation | UnmatchIntent → MatchProjection | Participant unmatch revokes contact without owner-policy prerequisite; unmatch never grants rematch |
| F11 | communication / App entitlement/submission; provider message bodies | ChannelIntent, MessageIntent, OwnedObjectRequest, MessagePageRequest, ReadCursorIntent → ChannelEntitlement, MessageSubmission, ConversationList, ConversationSummary, MessagePage | No send or history read after block/unmatch commit; no provider token is issued (OD-45); pending submission is not delivery; only text Glow sent is shown |
| F12 | communication / App settings/devices; push provider | NotificationIntent, DeviceIntent → NotificationSettings | Token rotation owner/session bound; logout revokes registration; no duplicate push; denied platform permission is normal |
| F13 | safety / App block; provider revocation | BlockIntent → BlockOutcome | Block works after unmatch and while paused; unblock cannot restore match/send entitlement |
| F14 | safety / App report/case; restricted provider evidence | ReportSubmission, OwnedObjectRequest → ReportReceipt | After-unmatch reporting allowed; other account receipt/evidence denied; malicious description never rendered as HTML |
| F15 | safety/moderation / App case/action/appeal/audit; WordPress staff identity | StaffCaseAction, AppealSubmission, OwnedObjectRequest → StaffCaseProjection, AppealProjection | Support role cannot suspend; actor/scope and current policy required; unrelated user cannot appeal |
| F16 | support/CMS / App support; WordPress public policy | SupportRequest, PublicSupportRequest, OwnedObjectRequest → SupportProjection, PublicRequestReceipt | Support staff cannot read birth/message evidence or invoke case action; wrong-owner status hidden |
| F17 | privacy / App export; provider-owned data under contract | ExportRequest, OwnedObjectRequest → ExportProjection | Wrong owner/expired grant denied; partial provider failure is failed/preparing, never ready |
| F18 | privacy/all domains / App jobs/tombstones; providers own purge; HDE unresolved | DeletionRequest, PublicDeletionRequest, OwnedObjectRequest → DeletionProjection, PublicRequestReceipt | Request immediately denies access/visibility; unresolved provider obligations prevent completed; restore replays tombstone |
| F19 | mobile presentation / API remains authorization owner | AppIntent → AppResponse, Error | Offline/stale response cannot authorize writes; accessible buttons submit same intents; native proofs deferred |
| F20 | entitlements / Verified provider lifecycle; app derived state |  → EntitlementProjection | Every attempted enable/purchase/restore is denied until new owner-selected versioned provider contract |

### F11 under OD-45: the conversation reads (P06.2 Stage C1)

Nathan decided D8 as option (b) on 24 October 2026 (OD-45): **no provider token is
issued** and the app holds no Stream credential, SDK or connection. Glow's API serves a
conversation's history and its new messages; Stream stays the provider behind Glow's
server. The [P06.2 brief](../planning/p06-2-chat-integration.md), "Stage C under OD-45",
holds the design; the [data model](data-model.md), "Chat contact and the outbox", holds
the reads behind these contracts. P11 serves the endpoints; nothing here is a route.

- **`ConversationList`** (`kind: conversation_list`): at most 200 `ConversationSummary`
  entries, read from Glow's rows with no provider call. A conversation the member may no
  longer see is not listed.
- **`ConversationSummary`** (`kind: conversation`): `match_id`, Glow's `state`, the
  `unread_count` and `latest`, a `LatestMessageMarker` or null. `state` is `open` for
  every listed conversation; `closed` carries no count and no marker, for a later push
  or the app's own state, and neither value says why a conversation ended (F10, F13).
  Nothing in C1 emits `closed`; its intended producer is a later push of the same summary
  (the brief's point d: a socket would push the same objects the list returns). The
  contract is unchanged (C1's exact-head review, finding 6).
  The unread count is the other member's accepted messages after the member's own read
  cursor, in the order they became visible (DM-22 6.3); the other member's cursor is
  never returned, and read receipts are not built (DM-22 item 5).
- **`LatestMessageMarker`**: Glow's `submission_id` and Glow's time `at` only, never text,
  computed over the accepted messages and the member's own pending or failed submissions,
  never the other member's (DM-22 6.1).
- **`MessagePage`** (`kind: message_page`): `match_id`, at most 100 `messages` (at most 50
  accepted ones, then, on the newest page only, the member's own pending and failed
  submissions, at most 50), and `older_cursor` and `newer_cursor`. A cursor is opaque,
  carries Glow's identifiers only, and is bound to the match it was issued for: a cursor
  from another match, or naming a message that is not an accepted message of that match,
  is refused with the generic `stale_version` (DM-22 6.4).
- **`ConversationMessage`**: Glow's `submission_id`, `author` (`own` or `other`), Glow's
  time `at`, `content` (`text`, or `unavailable`) with `text` (the text Glow sent, or
  null), and `delivery` (`pending`, `accepted` or `failed`) for the member's own messages,
  null for the other member's, which are always accepted. "Unavailable" is one state with
  no reason field, the same for retention, a failed digest check or reconciliation (DM-22
  6.2). A pending own message carries its spool text to its sender only; the other
  member's pending and failed submissions never appear (F11: a pending submission is not
  delivery).
  **`at` has two meanings** (C1's exact-head review, finding 7): for an accepted message it
  is the acceptance time (its `message_submitted` event's `delivered_at`); for the member's
  own pending and failed submissions it is that event's `available_at`. That is the
  submission time under today's deliverer, which leaves `available_at` unchanged on a
  retry (`services/api/glow_chat/delivery.py:470`); a deliverer whose retries move
  `available_at` would change it, and the P11 plan carries that dependency (C1-C1's
  re-review, R5). A message's `at` therefore changes when it is accepted, and a client
  keys a message on `submission_id`, never on `at`.
- **`MessagePageRequest`**: `match_id`, `cursor` (null for the newest page) and `limit` (1
  to 50). The actor is the authenticated session's account, never a field.
- **`ReadCursorIntent`** (`operation: read_cursor`): `match_id` and `submission_id`. It
  moves the member's own read cursor forward, in acceptance order, to an accepted message
  of the match, after the send's checks; its response is that conversation's
  `ConversationSummary`. It is the one mutating intent without `CommandMeta`: the command
  is a monotone maximum, so a repeat, a replay or a cursor behind the current one changes
  nothing, and an idempotency key or expected version would add nothing. F11's registry
  entry gains its transition, `read` from `behind` to `current`, for a participant with an
  active match and current eligibility.
- **`ChannelEntitlement` loses `channel_ref`** (DM-21 2.3), with its conditional: it was
  the provider's channel ID, and the provider's channel ID no longer reaches the client.
- **No DTO carries anything from the provider:** no user, channel or message ID, no
  timestamp, no user or member object, no custom data, no event type and no error text.
  The shared corpus rejects each such field in each new DTO, in a nested message or
  conversation, in `ChannelEntitlement`, `MessageSubmission` and `Error`, and in an
  `AppResponse`, through Python and the generated validators.
- **The new responses join `AppResponse`** and `ReadCursorIntent` joins `AppIntent`, as
  P04.3's `MediaCollection` did: an unpublished design catalog consumed by the generated
  client in this repository. No route or deployed-client negotiation is activated; older
  validators reject the new discriminators, and a deployed transport negotiates support
  before returning them.
- **Errors.** A refused read maps to Glow's generic codes: the member's own session to
  `unauthenticated`; anything about the conversation or the other member (an unmatch, a
  block, a suspension or deletion, a pause or restriction, a withdrawn consent, a message
  that is not this match's) to `not_found`; a provider failure to `provider_unavailable`,
  retryable only for an outage, never a page in which every message is unavailable (DM-22
  2.4); a cursor to `stale_version`.
- **The interim rule (F06; DM-22 3.1).** Whatever refuses a send refuses these reads, so a
  conversation also leaves the other member's list while one member is paused,
  restricted, suspended or has withdrawn consent. Before P11 serves the reads, the A05
  history question goes to Nathan in OD-32's form.
- **Uniqueness.** Conversations carry distinct match IDs and messages distinct submission
  IDs by construction of the server's projections; the shared key-uniqueness rule
  (`runtime.py`, mobile `validation.ts`) covers `items` and `selections` only, so the
  generated validators do not enforce it here.

### F02 to F06 on the server (SV2 Stages A and B, sealed until P11)

SV2 Stage A built the server side of F02, F03, F04 and F06 in `services/api/glow_profiles` (the [SV2 brief](../planning/sv2-profiles-media.md), revision 5, with DM-52's to DM-55's conditions; the [SV2 evidence record](../testing/evidence/2026-11-10-sv2-profiles-media.md)). It is **sealed until P11**: the routes run only under the disposable-PostgreSQL proof's profile settings, the served runtime imports none of it, and the production catalog's paths map stays empty until P11 serves them. Its new DTOs are additive, an unpublished design catalog (DM-52): older validators reject their discriminators, and a deployed transport negotiates support before returning them. Every route takes its actor from SV1's `GlowActorAuthentication` only (`unauthenticated`, 401), reads and writes the actor's own objects only (another member's object is `not_found`), refuses a body that is not its DTO and any query string (`invalid_request`, 400), a body the parser cannot hold (an integer too large for its number check, nesting deeper than the parser allows) and a text holding U+0000 included (correction C2), names a code and never a value in a refusal or a log line, and is served `Cache-Control: no-store`. Commands carry `meta` (an idempotency key and the expected version: `stale_version` otherwise); a replay returns the current projection, and another intent under the same key is `idempotency_conflict`. No route reaches a staff operation; P07's staff API will expose them.

- **F02.** `ConsentIntent` at `api/v1/consent` (GET `OnboardingEligibility`): `glow_chat`'s `accept_consent` and `withdraw_consent`, nested, after SV2's own check that an acceptance names the current version (`stale_version` otherwise). `SensitiveConsentIntent` at `api/v1/consent/sensitive` (GET `OwnSensitiveConsent`): SV2's own writer, purpose `sensitive_profile`; each sensitive save (a value, orientation's own words, a narrowed set) needs it accepted at its current version (`forbidden`, `sensitive_consent_required`, otherwise; correction C2, DM-55); its withdrawal sets the member's orientation and relationship status rows to "not stated" in place (no own words, the display flag off), each with `profile_field_changed` unless it already held that, resets both "show me" sets to all, and deletes the idempotency records that carried them. Both consent writers accept a newer version from `accepted` (F02 `accept` and `accept_sensitive` from `accepted` to `accepted`, `consent_current`; correction C2). `AdultCheckIntent` at `api/v1/eligibility/adult` (GET `OwnAgeState`): the adult check, 18 or over on the server's date. The date's outcome comes first, after the idempotency check and before the stale version check: a future date is `invalid_request` and changes nothing; a date under 18 is `forbidden` and is not stored. From a self-declared adult it also commits the failing rerun (`adult_check_failed`: the age state `unknown` with no date, the current birth input `missing`, a `visible` profile `incomplete`) and keeps no idempotency record; the operation returns the refusal so the reset commits, and a retry is refused (correction C2; DM-55). The onboarding consent's accept and withdraw, the adult check and staff's approval without ID verification and its revocation each end with D9's recompute (correction C1; DM-54), so an acceptance, a passing check or an approval that meets the last requirement makes the profile `visible` (F04 `requirements_met`, `system`). Identity verification has no member route: the automated check's verdict arrives through a port that SV2 builds without a provider, and staff approval without ID is a staff operation behind the `identity.staff_approval` setting.
- **F03.** `BirthInputIntent` at `api/v1/birth-input` (GET `OwnBirthInput`, also by `input_id`): a new private revision, `pending`, after the adult pass and the current onboarding consent. **The server requires a birth time** (D8; Nathan: "birth time is required at signup"): `time_precision: unknown` is refused (`invalid_request`), although the contract's `BirthInput` still allows it, and an approximate time keeps its entered value. A new revision returns any mapping to `pending`, pointing at the new revision; a new eligibility date makes the current revision `missing` (`date_changed`). **The date's outcome comes right after the adult-check gate,** before the onboarding consent, the stale version and the birth time (correction C2; DM-55). A future date is refused (`invalid_request`) and changes nothing. **A birth input whose date fails the adult rule** (under 18) is refused (`forbidden`) and nothing of it is stored, while its transaction commits the failing rerun: the age state `unknown` with no date (`adult_check_failed`), the current revision `missing` with its mapping back to `pending` (`date_changed`), and a `visible` profile `incomplete` (`requirement_removed`). It stores no idempotency record, so a retry is refused at the adult-check gate and changes nothing more (correction C1; DM-54). Earlier revisions keep their contents, readable only by their owner and never current again; whether the reset erases them is G-01's, in P07 (DM-55). SV2 creates no mapping and resolves nothing.
- **F04.** `ProfileIntent` at `api/v1/profile` (GET `OwnProfile`, also by `profile_id`): the edit, whose transition is completion when every requirement is met; `ProfileFieldIntent` at `api/v1/profile/fields` (`OwnProfileFields`); `PreferencesIntent` at `api/v1/profile/preferences` (`OwnPreferences`); `FiltersIntent` at `api/v1/profile/filters` (`OwnFilters`); `AreaIntent` at `api/v1/profile/area` (`OwnArea`); `AreaQuery` at `api/v1/profile/area/nearest`, a POST whose body alone carries the coordinates, which returns `NearestArea` and changes nothing; `ProfileCatalog` at `api/v1/profile/catalog`; and `OwnCompletion` at `api/v1/profile/completion`. **What moves a profile to `visible`** (D9; correction C1, DM-54): every writer of a completion requirement (the profile edit, the four fields, the area, the onboarding consent's accept and withdraw, the adult check, the birth input, and staff's approval without ID verification and its revocation) ends, in its own transaction and after the account row lock, with one shared recompute: an `incomplete` profile with nothing missing becomes `visible`, a `visible` profile with anything missing becomes `incomplete`, and `paused`, `restricted` and `removed` stay as they are. A completion in an F04 owner command (the profile edit, the fields, the area) is `complete` (`owner`); one that follows a write in another flow is `requirements_met` (`system`). `requirement_removed` (`system`) is the demotion that follows another write, or a field or area write that finds a requirement lapsed: a consent withdrawal, a failing adult rerun, a new birth input revision, a revoked staff approval, or a new onboarding consent version found at the member's next requirement write, the profile edit's included. Only the profile edit that clears the summary itself is the owner's `edit` (`owner`), whatever else is missing, riding on the edit's own version bump; any other demotion is `requirement_removed`, a transition of its own that bumps the profile's version and the account's `eligibility_version` (correction C2; DM-55). Each completion emits `profile_completed`, and each `requirement_removed` emits `profile_demoted`.
- **F05** (SV2 Stage B; the [SV2 brief](../planning/sv2-profiles-media.md), revision 8, D9, D10 and D19, with DM-57's and DM-58's conditions; OD-61; OD-62). Photos are objects in private R2 storage, behind a storage port and a processing port with **fixture adapters only** (no R2 call, credential, SDK or decoder; P11 builds the adapter and PV04's proof). F05's existing DTOs are used unchanged; no DTO is added. `MediaIntent` at `api/v1/media` (GET `MediaCollection`, the owner's assets but `removed`, in their order: a removed asset leaves the collection and its 20 entries, where P04.3's fixture kept removed tombstones, and stays readable by its ID (DM-58); `api/v1/media/<asset_id>`, GET `MediaLifecycle`): `request_upload` answers `MediaUploadGrant` unchanged (`grant_ref` is the grant's opaque reference, whose pattern cannot hold an address; the store's upload credential goes to no member, DM-57 U3), within the `media.policy` setting's limits (four live photos and the 20 collection entries: `state_conflict` beyond them; `stale_version` for another collection version); `remove` (the asset's version) withholds delivery at once and moves to `removal_pending`, never refused for the owner's own asset, and a repeat is `no_change`; `reorder` (the collection's version) takes exactly the current approved set, in a new order (`state_conflict` otherwise). Another member's asset is `not_found` at every route. **No member route delivers a provider or system event.** The store's events reach the domain only through the storage port, which authenticates each first: the completion (`uploaded`, `provider`) is adopted only if it is the first that matches its grant's key, within the grant's time and the byte limit of the media policy version the grant records; the deletion acknowledgment of every object of an asset, after a purge request that asks the hold port first, is `purged` (`provider`). **The account's state** (DM-58 item 9; SV2 Stage B's correction C1): the purge request and the deletion acknowledgment run in any account state, under the account row's lock, so a photo removed before its owner is suspended or asks for deletion is still purged; every other photo step (the member's commands and reads, the completion, the review step, the check, staff's restriction and the delivery read) refuses an account that is not active (`account_not_active`). The system review step (`review`, `system`) is Glow's own processing on the adopted original only, then G-02's seam (configured with none: `no_detector`) for every adopted upload, given the variant or, when processing made none, the original; an upload with no variant is then rejected (`reject`, `system`, `no_variant`). The automated check's `approve` and `reject` (`system`) are written to `StaffAudit` with the subject `system:photo-check`; an approval asks the hold port first, and the check never acts on an asset under a staff restriction. Staff's `restrict_media` (`moderator`, on a report; no route) returns an approved photo to `review_pending` with its own revocation record. `MediaLifecycle.approved_delivery_ref` is an approved variant's delivery reference only; `OwnProfile.media_ids` lists the approved photos, in their order. **D9:** completion requires an approved photo; the check's approval ends with the recompute (F04 `requirements_met`), and the removal or restriction of the last approved photo demotes a `visible` profile (F04 `requirement_removed`). **D19:** every SV2 transaction locks settings pointers in name order, and a photo writer that recomputes takes `consent.onboarding` with `media.policy` in its first `read_shared` call.
- **F06.** `VisibilityIntent` at `api/v1/profile/visibility` (`OwnProfile`): `glow_chat`'s `pause_profile` and `resume_profile`, nested; a resume rechecks completion first and refuses an incomplete profile (`forbidden`). Restriction is a staff operation through `glow_chat`'s `restrict_profile`, with no route: F04's `restrict` from `visible` and from `paused` to `restricted` (`moderator`; correction C1, DM-54).

### F07 on the server (SV3 Stage A, sealed until P11)

SV3 Stage A built the server side of F07 in `services/api/glow_discovery` (the [SV3 brief](../planning/sv3-eligibility-discovery-interactions.md), revision 2, with DM-60's conditions; the [SV3 evidence record](../testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md), "Stage A"). It is **sealed until P11**: the route runs only under the disposable-PostgreSQL proof's discovery settings, the served runtime imports none of it and selects no compatibility provider, and the production catalog's paths map stays empty until P11 serves it. Its new DTOs are additive, an unpublished design catalog, as SV2's are (`packages/contracts/README.md`, "SV3 Stage A").

- **The route.** `PageRequest` at `api/v1/discovery/page` (POST, the body only) answers `CandidateCardPage` in the `AppResponse` envelope, for the actor's own batches only. It takes its actor from SV1's `GlowActorAuthentication` only (`unauthenticated`, 401); refuses a body that is not the DTO, any query string, another content type (`invalid_request`, 400) and another method (`invalid_request`, 405, as SV2's routes answer); refuses a viewer who fails a predicate (`forbidden`, 403), computing nothing for them; names a code and never a value in a refusal or a log line; and is served `Cache-Control: no-store`. Stage A serves no action route: like, pass, the match, unmatch and block are Stage B's.
- **A page with no cursor** creates the viewer's batch for the collection, in one transaction: the viewer's account row `FOR NO KEY UPDATE` (since C1, DM-61: it does not block the `FOR KEY SHARE` that another viewer's entries' foreign-key checks take, so two pages, or a page and a pair writer, cannot deadlock through it), then the settings the selection reads under their pointers' `FOR SHARE` locks in one `read_shared` call, in name order (`consent.onboarding`, `discovery.resurfacing`, `profile.age_range`, `profile.location`, `profile.narrowing`; D19), then **one statement** that selects up to 100 candidates with every predicate (D3 to D5) and consumption (D7), ordered by a random tie-break each candidate draws inside the statement (`gen_random_uuid()`; DM-61 K2, replacing DM-60 Q2's keyed hash), stored nowhere, since the entries' positions keep the order it gives; no key exists, so none travels in a statement or reaches a log. ADULT includes the age ceiling (the age the date gives at most `AGE_CEILING`, 150, `CandidateProfile.age`'s maximum; DM-62), for the viewer and for each candidate, so no card carries an age above the contract's maximum. Recommendations then ask the compatibility port for each selected pair (none when the selection is empty: `empty`, F07's acceptance); a ready pair is ranked by its band, then the tie-break; an `unsupported` pair is left out; any `pending` or `unavailable` result makes the batch so, with no items; no port selected (the runtime's case) is `unavailable`. Broader discovery leaves out the viewer's current recommendations batch's candidates. The viewer's earlier batch of the collection is deleted with its entries (one batch per viewer and collection, `batch_one_per_collection`; Q5's bound). The batch records the viewer's `eligibility_version`, `preferences_version` and `blocks_version`, a policy version made of the five settings' version numbers (Q3), a limit of 100 and a 30-minute expiry; each entry records its candidate's three versions.
- **A page with a cursor** holds the viewer's account row and the same pointers `FOR SHARE`, and refuses with the generic stale response (`stale_version`, 409, the same body whatever the cause; D8) a cursor not issued to this viewer for this collection (a MAC over the viewer's account, the collection, the batch and the offset, keyed with its own salt), a missing (deleted) batch, another viewer's or collection's batch, a batch that is not `ready`, an expired batch, and a batch whose viewer versions or policy version no longer match (Q4). It then **rechecks every entry from the cursor's offset in one statement** (DM-60 Q1): every predicate and consumption again, both block directions for every entry, so a candidate made ineligible, blocked, matched, liked or passed since the batch was built is dropped, and a page whose entries all drop is `empty`. It writes nothing.
- **The card** holds `CandidateProfile` unchanged (`compatibility` is `pending` for every card: no ready compatibility projection is serializable, and a synthetic ready result still projects `pending`) and `CandidateDetails` (D13 (a)). `media_delivery_refs` are the candidate's approved photos, in their order, each through SV2's `delivery_reference` (approved variants only, asking the hold port first), read after the page's transaction.
- **The registry:** F07 gains `CandidateCardPage` (`owner`); no transition is added, since a page with no cursor makes `request` and then `eligible_results`, `no_results` or `outage` in one transaction. Stage B's consumption of a batch is F07's `invalidate`.

## Policy boundaries and deliberately unavailable operations

A05 owns launch geography/language, adult clock, preference dimensions/options, resurfacing, rematch, existing-history behavior, media operating rules, named moderation/support owners and retention. Schema labels are opaque policy references; they do not choose these values. `consent_current`, `media_policy`, `reciprocal_likes`, `export_complete`, `purge_verified` and `staff_approval` (SV2: the `identity.staff_approval` setting being on) in the oracle are explicit trusted test prerequisites, not additional owner decisions. A resolved policy must match the current resource/policy revision; the oracle only models its presence, and trusted domain acquisition provides the production binding.

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

## P05.3 internal interaction result and identity bridge

Existing closed `InteractionIntent`, `UnmatchIntent` and `BlockIntent` remain
the command shapes. The additive internal `CommandReceipt` records only
`outcome_code` (`liked`, `passed`, `unmatched`, `blocked` or `unblocked`),
`object_ref` and the original positive `committed_version`.
`InteractionCommandResult` has `kind: interaction_command_result`, that receipt,
`replayed`, and `current_projection`: an existing `InteractionOutcome`,
`MatchProjection`, `BlockOutcome`, or null. The current projection is separately
authorized; it never changes the receipt or turns a past active match into a
present permission. Neither type is added to the served `AppResponse` union or
an HTTP route. They belong to the unpublished internal catalog and its generated
validators; existing production wire responses are unchanged.

`DevelopmentInteractionEvent` is a closed internal fixture record with event UUID,
kind (`match_created`, `contact_revoked` or `block_changed`), aggregate UUID and
version, and `contract_version: gapp-interactions-fixture-v1`. It carries no
profile, private action, chat content, token or provider body. A logical event is
not a provider delivery receipt.

The shared `interactions-v1.json` catalog maps development account/profile names
to distinct account/profile UUIDs. Composition also binds UUID batch identity to
the current development queue, viewer/session, mode, membership and versions.
An arbitrary client-supplied mapping cannot establish this binding. Existing
development `profile-jules`-style IDs and process-local queue handles remain
development identifiers; production UUID validation is not weakened. See
[interaction fixtures](interactions-fixtures.md) for execution, receipt recovery,
consumption and revocation semantics.

`CommandMeta.expected_version` addresses the directional interaction for
like/pass, the match for unmatch, and the directional block for block/unblock.
Zero requires absence; a positive value requires that object's current revision.
An already committed identical command is checked as a replay before applying
the new-command batch/precondition rules. This recovers a lost response even
after the command consumed its old batch; it does not authorize a new action
using that batch or preserve a withdrawn access grant.

### Compound actions and model projections

An incomplete/paused/restricted/removed own profile may retain an empty bio; a visible candidate may not. ProfileIntent can clear the bio, but the service must then remove visibility if completeness fails. `Profile.bio` maps to DTO `summary`. SV2 replaced `location_label` with the member's home area, whose name is its display text (the [SV2 brief](../planning/sv2-profiles-media.md), D5); since SV3 Stage A a candidate's card shows that name in `CandidateDetails.area_name`, and nothing else of the area (the [SV3 brief](../planning/sv3-eligibility-discovery-interactions.md), D13 (a); DM-60 Q12): never its ID, internal point or a distance, the second A05 message's location (a), which "reveals only the area the member chose". Unset preferences map to null policy version and empty selections; policy-less JSON never authorizes discovery. Birth corrections from ambiguous, pending, unavailable or unsupported states return to pending under a new input version, without granting HDE resolve permission. A valid new maintained session can re-register the same revoked device installation with a new provider token; a revoked session cannot.

A scoped `StaffCaseAction.restrict_media` names the exact asset, verifies its relation to the current case and both object grants, and uses the current A05 moderation policy. Its immediate safety effect retracts approved delivery and returns the asset to review_pending while the case remains investigating; it does not preselect rejection, removal or an appeal outcome. The case audit, asset change, projection/version invalidation and outbox are one future UOW. Account suspension uses F01's scoped moderator transition, also audited against the case. Deletion request similarly combines F18 requested/access_revoked, F01 deletion_pending and F04 removed plus session/contact revocation in the same future commit; purge completion is separate and policy/provider dependent. Contract tests exercise these component transitions, not atomic multi-object persistence.

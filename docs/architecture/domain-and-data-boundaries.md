# Domain and data boundaries

**Status:** P02 definition baseline. This document preserves the F01–F20 scope and ownership map. Exact versioned wire contracts and executable checks live in [application contracts](../../packages/contracts/README.md) and [production contract rules](production-contracts.md); [static data definitions](data-model.md) and the [migration plan](../operations/migration-plan.md) explain `services/api/glow_persistence`. These definitions do not implement production routes, authentication or persistence. The only served surface remains the isolated development GET contract. GAPP-PF01 remains governing direction; Notion owns work status.

A bounded internal implementation exists in `services/api/glow_domain`: explicit eligibility predicates, distinct account/chart identities, synthetic compatibility states, versioned directional cache keys and narrow repository/provider interfaces. [Trusted eligibility](trusted-eligibility.md) defines server-owned pair/version acquisition and the future action transaction boundary. [Initial privacy and safety rules](privacy-and-safety-rules.md) constrain projections and lifecycle work. The original [domain verification](../testing/domain-seams.md) is historical PR 2 evidence; later checks do not retroactively change that checkpoint.

## Responsibility and trust

The native mobile client renders application projections and submits intents. The application API must authenticate, authorize, recheck current state and own dating-domain transitions. A WordPress operator plugin will submit narrowly scoped staff requests to that same API; it will not become a second dating backend. HDE remains the protected owner of chart calculation and compatibility intelligence. App-owned birth-input and opaque chart-reference mapping must not become an HDE implementation.

Nathan's 24 September 2026 clarification, carried by AP1-P05.1-002 revision 1.1,
keeps the application in one repository, `amthorn78/glow-dating-app`:

| Repository location | Responsibility and present boundary |
|---|---|
| `apps/mobile/` | Mobile frontend; renders projections and submits intents. |
| `services/api/` | Dating backend; owns dating authorization, state transitions and audit history. |
| `packages/contracts/` | Shared application contracts and generated definitions. |
| `wordpress/glow-admin/` | Planned P07 operator plugin; not implemented by this correction. It will call scoped dating admin APIs and retain only WordPress CMS/staff concerns. |

Separate frontend/backend repositories are unnecessary. Sharing a repository does
not combine their runtimes, deployment boundaries or trust levels. WordPress has
no privileged direct access to app/HDE tables. The existing HDE repository/service
stays separate and protected. The app can progress with provisional fixtures before
HDE is ready; later, one app-owned adapter must implement the verified supported
engine contract, with live integration and acceptance before launch.

Here, `ChartMapping` is an **account–chart link**: an app account ID, an opaque
engine reference, pending/resolved state, birth-input version and mapping version.
It calculates no chart. The app retains necessary linkage/provenance and permitted
projections; HDE remains authoritative for calculation, mechanics, interpretation,
engine-owned chart data and supported compatibility output. If HDE supplies an
equivalent linkage/version facility, the app will reuse it and retain only its
necessary ownership references. Provisional interfaces must adapt to HDE, not
require HDE to reproduce the scaffold.

Application PostgreSQL is the planned dating-domain system of record. Current development has no domain persistence. Changes that must agree atomically belong in one future application transaction, with provider side effects dispatched after commit through an outbox. There is no proposed cross-provider two-phase transaction. HDE production access, application database connection and database-dependent proof remain P11 work.

P05.3's [interaction fixture composition](interactions-fixtures.md) joins trusted
discovery membership to directional actions, one canonical match, immutable
receipts, a simulated atomic outbox and participant revocation. The mobile
implementation is a nonpersistent presentation substitute checked against shared
contracts/cases; Python remains the domain implementation. Neither installs a
production mutation route or supplies provider contact. P06 consumes the current
match/contact revision and must prove actual provider enforcement independently.

The audited P11 direction is clean application-owned schema/roles in HDE's same
logical database `railway`. Isolation means bounded app ownership and privileges,
not a new logical database requirement. Existing HDE/legacy relations, grants
and shared-resource effects remain protected; this fixture task connects no
database and applies no migration.

| Boundary | Authoritative decision/data owner | Client or adapter projection | Required enforcement, not yet implemented |
|---|---|---|---|
| Native client → app API | App domain services | Minimum user-facing state and allowed actions | Object ownership, identity, eligibility, stale-state checks, input bounds and rate limits |
| Staff WordPress → app API | App safety/support domains; separate staff identity | Scoped case summaries and justified evidence access | Staff scopes, actor audit, support/moderation separation; no direct app/HDE SQL |
| App → HDE | HDE owns calculation/output; app owns mapping and display permission | Approved mapped explanation/band plus provenance/freshness only | Supported contract, authorized credentials, bounded requests, versioning and data rights |
| App → media provider | App owns eligibility/status; provider holds bytes | Approved delivery variant only | Private originals, short-lived grants, metadata stripping, ownership and publication checks |
| App → chat/push | App owns contact entitlement; selected provider may hold message bodies | Match-bound channel state and privacy-safe notification | Provider-level send authorization, revocation and deduplication |
| App → billing provider, if selected | Verified provider events; app owns derived entitlement | Entitlement state, never client-asserted payment truth | Signature/replay checks, reconciliation and product scope decision |

## Proposed state ownership

The vocabulary below is the original conceptual design inventory. Exact wire and storage states are defined by the versioned schemas and static models, with mappings in the P02 contract/data documentation. The inventory does not settle unresolved product policies listed later. Compound authorization must evaluate the current account, consent, profile, safety and relationship states together; a single `active` field cannot authorize all actions.

| Domain owner | Proposed state vocabulary | Governing transition or invariant |
|---|---|---|
| Identity/consent | Account: `unverified`, `active`, `suspended`, `deletion_pending`, `deleted`; session: `valid`, `revoked`, `expired`; consent: `required`, `accepted`, `withdrawn` | Verification/recovery delegated to maintained auth machinery; deletion/suspension/revocation deny the relevant access. Consent version and decision facts stay private. |
| Profiles/preferences | Profile: `incomplete`, `visible`, `paused`, `restricted`, `removed` | Visibility additionally requires adult eligibility, consent, completion, reciprocal preferences and safety checks. Resume must re-evaluate all current conditions. |
| Profiles/media | `upload_pending` → `quarantined` → `review_pending` → `approved` or `rejected`; removal: `removal_pending` → `removed` | Upload success does not approve publication. Only owned, approved variants may be served; removal includes downstream purge reconciliation. |
| Birth input/engine identity | Input resolution: `missing`, `ambiguous`, `pending`, `resolved`, `unavailable`, `unsupported`; chart mapping separately versioned | Preserve actual entered date/local time/place/uncertainty. No guessed time or silent timezone substitution. Mapping state does not establish discoverability. |
| Discovery/compatibility | Batch: `pending`, `ready`, `empty`, `stale`, `unavailable`; provider result: `ready`, `pending`, `unavailable`, `unsupported` | Eligibility precedes compatibility. Candidate budget and cursor rules still need contracts. A ready batch is not a match. |
| Interactions/matches | Directional action: `liked` or `passed`; match: `active`, `unmatched`, `restricted`; block: `active`, `removed` | Like idempotency and one canonical unordered match pair. Block overrides contact/discovery. Resurfacing and rematch semantics remain undecided. |
| Communication | Channel binding: `pending`, `active`, `revoked`, `failed`; submission: `pending`, `accepted`, `failed`; device registration: `active`, `revoked` | Recheck match/block before every new send authorization. Membership and client token possession alone are insufficient. |
| Safety/moderation | Report/case: `submitted`, `triaged`, `investigating`, `resolved`; appeal: `submitted`, `reviewing`, `resolved` | Evidence permissions and reasoned action audit. Outcomes, severity response times and accountable operators need product/operations decisions. |
| Support | `open`, `in_progress`, `resolved` | Support access must not imply moderation powers or access to all private data. |
| Privacy | Export: `requested`, `preparing`, `ready`, `expired`, `failed`; deletion: `requested`, `access_revoked`, `purging`, `blocked`, `completed` | Immediate visibility/access removal precedes eventual purge. Completion requires verified provider steps and documented retention, not just hidden UI. |
| Entitlements, conditional | `disabled` until paid scope is chosen; future active/grace/revoked vocabulary follows actual provider contract | No invented pricing, subscription period, paid ranking or live purchase UI. |

## Launch-flow contract and acceptance map

The logical names below preserve the original flow inventory. They are not published URL claims. Versioned schemas and executable state/authorization examples implement the P02 contract baseline; they do not establish the deferred real acceptance described in this table. The private owner column identifies the system responsible for persistence once integrated.

| Flow / logical contract | Domain owner and public/private projection | Data owner | Required acceptance case and deferred proof |
|---|---|---|---|
| Signup, verification, recovery, logout and session revocation / `AccountAccess` | Identity; client receives minimal challenge/session outcome; credentials, email and recovery facts private | App account metadata + maintained auth library | F01: expired/replayed links, enumeration, wrong-account linking, lost-device recovery and revocation; actual allauth/SQL persistence P11 |
| Adults-only onboarding and consent / `OnboardingEligibility` | Identity/consent + eligibility; client receives eligibility requirements/result; birth date and consent facts private | App | F02: incomplete, unverified, underage, withdrawn-consent and suspended accounts denied discovery; exact age calculation/timezone and geography policy unresolved; database enforcement P11 |
| Birth entry, uncertainty correction and chart resolution / `BirthInput` + `ChartResolver` | Birth/engine identity; user can review own entered facts and ambiguity; other users see no raw birth facts or exact birth location | App owns submitted facts/mapping; HDE owns chart/output | F03: ambiguous/missing time, retry, changed input and stale chart reference; exact accepted HDE contract and live behavior P11 |
| Profile editing and preferences / `OwnProfile` + `OwnPreferences` | Profiles/preferences; explicit own-profile fields vs candidate display allowlist | App | F04: object authorization, invalid/incomplete edit, reciprocal preferences and private-field non-disclosure; final preference policy P05; persistence P11 |
| Upload, review, reorder and remove photos / `MediaLifecycle` | Profiles/media; own upload/review state vs approved delivery reference | App status/ownership; chosen provider bytes | F05: failed/retried upload, malicious content, ordering, abandoned upload and purge; exact limits/policy P04; provider delivery and purge P11 |
| Profile pause/resume / `VisibilityControl` | Profiles + eligibility; own pause state; paused users excluded from new discovery | App | F06: stale queue invalidation and re-evaluation on resume; existing-match/history behavior needs policy; SQL/provider consistency P11 |
| Recommended people then broader discovery / `RecommendationPage` + `DiscoveryPage` | Eligibility/discovery; bounded public candidate projection; internal filter reasons and provenance private | App queue/eligibility; HDE result source | F07: reciprocal constraints, empty market, blocked/deleted/paused candidates, stable pagination and refresh; actual HDE granularity/throughput P11 |
| Accessible like/pass / `InteractionIntent` | Interactions; own action outcome, never another person's unreciprocated private action unless later policy permits | App | F08: repeat idempotent request, stale candidate and same action from two devices; resurfacing policy P05; real concurrency P11 |
| Reciprocal like → mutual match / `MatchProjection` | Interactions/matches; two-party match state separate from recommendation state | App | F09: simultaneous reciprocal likes yield one pair/one logical event; transaction/uniqueness/outbox proof P11 |
| Unmatch / `UnmatchIntent` | Matches + communication; contact entitlement revoked; history projection follows separate policy | App; chat provider for applicable downstream change | F10: idempotent unmatch, stale tokens and in-flight send boundary; rematch/history policy P05/P06; provider/SQL race P11 |
| One-to-one text chat after match / `ChannelEntitlement` + `MessageSubmission` | Communication; participant view only; evidence/history access separately controlled | App entitlement/channel binding; provider message bodies subject to final terms | F11: wrong channel, direct SDK bypass, outage, reconnect, retries, block/unmatch race; provider capability proof P06 and actual persisted enforcement P11 |
| Notification preferences and delivery / `NotificationSettings` | Communication; own settings/device state; privacy-safe notification projection | App settings/token references; push provider delivery | F12: denied permission, token rotation, logout/revocation, duplicate delivery and no sensitive default push body; native/device and live delivery P09/P11 |
| Block from profile/chat or after unmatch / `BlockIntent` | Safety + matches/discovery/communication; user's block outcome private; contact restrictions authoritative | App; providers for revocation | F13: block removes discovery/contact ability across surfaces and devices; unblock must not silently resurrect prior authorization; exact resurfacing policy unresolved; race proof P11 |
| Report from profile/chat or after unmatch / `ReportSubmission` | Safety; reporter receipt, restricted evidence/case record | App; provider evidence references under retention terms | F14: report-after-unmatch, malicious evidence and cross-account access; provider evidence retention and durable case capture P11 |
| Moderation, restricted staff tools and appeal / `StaffCaseAction` + `AppealSubmission` | Safety; user decision/appeal projection, staff-scoped evidence/audit | App; WordPress owns staff/CMS account data only | F15: reasoned action, role separation, wrong scope, audit and appeal; named operators/policy P07; real auth and durability P11 |
| Support/public policy routes / `SupportRequest` + public CMS content | Support/CMS; user request status vs private support record | App support state; WordPress public content | F16: support cannot invoke moderation privilege or disclose another user's data; final policy/ownership P07/P08; connected staff API P11 |
| Data export / `ExportRequest` | Privacy; authenticated own-data bundle, short-lived delivery | App orchestration; provider-owned data gathered under contract | F17: wrong-account request, expiry, repeated request and partial provider failure; retention/export scope P08; real export completeness P11 |
| Account deletion including public request route / `DeletionRequest` | Privacy + all domains; progress/restriction explanation, private step ledger/tombstones | App orchestrates; each provider owns its purge; HDE obligations unresolved | F18: immediate invisibility/revocation, retry/partial failure, duplicate request and backup restoration without resurrection; retention decision P08, real purge/restore P11 |
| Native iOS/Android navigation, accessible swipe alternatives and failure recovery / consumer of preceding contracts | Mobile presentation; no independent authorization or HD calculation | App API remains authoritative; platform secure storage only for permitted native secrets | F19: large text/screen reader, interrupted onboarding, offline/stale action reconciliation, denied permissions and deep-link handling; signed builds/devices P09/P11 |
| Conditional paid entitlement / `EntitlementProjection` | Entitlements; UI disabled until paid product decision; verified provider state only | Provider financial lifecycle; app derived entitlement | F20, only if selected: restore/refund/revocation/grace/duplicate or reordered webhook cases; scope/budget P08, real provider/persistence P11 |

## Proposed data design and migration preparation

These are the original design targets, now represented by static model and migration definitions in `services/api/glow_persistence`. No schema has been applied, and no exact retention duration is implied. Model declarations, named constraints and the static migration plan are the exact implementation references.

| Data group | Identifier/constraint/index intent | Private projection and lifecycle owner |
|---|---|---|
| Account/session/consent | App-generated opaque account ID; auth-library identity key unique after supported normalization; consent version/decision recorded; session identity belongs to auth library | App private metadata; credentials delegated; retention decision P08 |
| Profile/preferences | One own profile per account; explicit visibility/completion; preferences bound to owner; indexes justified by eventual eligible-candidate query | Candidate allowlist excludes account credentials, contact detail, raw birth data and private location; exact display field choices P04/P05 |
| Birth input/engine mapping | Separate app input ID and opaque engine ID; mapping retains input version + engine/contract provenance; no reused account UUID assumption | Private source facts and uncertainty; date/local time remain civil values, not silently converted UTC timestamps |
| Media asset | Opaque asset ID; owner FK, provider reference, lifecycle/review state and ordering; unique ownership/reference relationships to be reviewed | Original/quarantine private; approved variant projection only; deletion steps tracked |
| Like/pass/block/match | Directional actor/target uniqueness; no self-action; canonical unordered match pair unique; block checked both directions for entitlement | Interaction record private; mutual match projection scoped to participants; deleted/paused policy unresolved |
| Recommendation batch/snapshot | Bounded entries with batch/candidate IDs, eligibility/input/engine/contract versions and freshness; eventual cursor index; directional cache unless symmetry proven | App owns projection/cache; HDE owns result semantics and permitted reuse |
| Chat binding/device notification | Unique match/provider-channel mapping; owner-scoped device registration; send-intent idempotency and outbox deduplication | Token values and message bodies excluded from routine logs; history retention separately decided |
| Report/case/appeal/audit/support | Opaque IDs; actor/subject references; restricted evidence; immutable action-event history; case/queue indexes from actual workflow | App-controlled least privilege; safety retention neither unbounded by default nor silently purged |
| Export/deletion/provider step/tombstone | Job and per-provider step identities; idempotency, retries and verification; restore-replay identity retained under explicit policy | App orchestrates progress; retention exceptions must be documented before completion claim |
| Webhook inbox/outbox/entitlement | Unique provider event/idempotency key; separate received/verified/applied outcomes; retry indexes; no client authority | Disabled paid seam until decision; event data minimized and provider lifecycle reconciled |

App event timestamps are timezone-aware instants under the wire contract's explicit format. Birth date/local time remain civil input facts and require separately resolved place/timezone provenance. Optional fields distinguish absent, unknown and intentionally withheld where domain meaning differs; exact nullability and identifier formats belong to the versioned schemas and auth/provider mapping, not this conceptual table.

The static migration sequence creates event infrastructure first, then application domain models in dependency order. This corrects the preparation table's earlier outbox-last ordering: outbox infrastructure must exist before any domain change relies on durable event publication. Authored migration files are not an applied migration ledger. Forward/backfill/expand-contract behavior and PostgreSQL uniqueness, isolation, indexing, ORM and rollback require actual P11 proof.

## Decisions and validation still owed

| Existing dependency | Must resolve before | Affected design |
|---|---|---|
| A01/A07: supported HDE contract/output/throughput | Live HDE acceptance P11 | Input identity, granularity, cache/version semantics, bounded candidate requests and deletion |
| A02: exact protected/app database and role ownership | Any P11 target mutation | Target isolation, migration privileges and legacy data disposition |
| A04/A08: actual provider access/budget and chat permission proof | Provider activation/P06 capability acceptance | Fail-closed send path, storage/processor terms, secure credentials and native signing |
| A05: launch geography/language/preferences; moderation/support owners; retention | Owning P05/P07/P08 work before final policy/launch | Age clock, display/location precision, resurfacing/rematch/history, media limits, escalation and deletion exceptions |
| A06: paid launch choice | Purchase implementation/activation | Otherwise keep billing disabled and omit paid acceptance from mandatory launch scope |

The P02 baseline turns this map into versioned schemas, generated clients/runtime validators, narrow interfaces, fixture conformance and static models/migrations. Completion evidence is in the current handoff and test records. Coverage in this table does not establish any real F01–F20 journey passed. [Deferred acceptance](../testing/p11-deferred-acceptance.md) keeps database, authentication, concurrency, live provider, restore and native proofs individually identified.

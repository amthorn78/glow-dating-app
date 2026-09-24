# Glow Dating App — A-to-Z Implementation Plan

**Document identity:** GAPP-PF01 · **Revision:** 1.4 · **Date:** 24 September 2026
**Purpose:** governing implementation sequence, acceptance criteria and continuity baseline for the application.
**Current direction:** P01–P05 completed at recorded preparation/fixture scope; new features paused for repository documentation migration and Claude Code setup. Current evidence is in the repository handoff and Notion coordination records.
**Execution model:** the receiving Claude Code session manages separate bounded implementation sessions. App Planner 1 prepares the transition. Use repository Markdown, code and Notion as primary context, without importing prompt libraries or automatic phase-approval machinery (D09).

## Repository authority note — P01.2

Published into private `amthorn78/glow-dating-app`, default branch `main`, on 23 September 2026. The revision 1.1 planning baseline and historical publication-state statements below are preserved. Current execution state belongs to Notion and the repository continuity handoff. See [authority-transfer evidence](../continuity/authority-transfer.md) for the exact commit and verified pointer updates. After that transfer, this repository file is the current governing plan; the original Drive plan remains historical. No product scope, phase acceptance, D08 authority or HDE boundary is changed by this transfer.

## 1. Direction and scope

Build a new Glow mobile dating application by assembling maintained frameworks, libraries and services around Glow-owned product logic. “From scratch” means a new application foundation, not writing authentication, chat transport, native build tooling or billing infrastructure ourselves. Existing owned repositories and Railway resources are potential assets; they are not mandatory foundations. Assess them once, retain what has demonstrable value, and avoid carrying forward obsolete coupling merely because it exists.

The current **Glow HD engine and its database are the protected integration target**. The engine owns Human Design calculation, interpretation and its data. The app owns dating accounts, consent, profiles, eligibility, preferences, recommendations presentation, likes, mutual matches, safety and operations. A new application does not imply replacing the engine or rebuilding its database.

Develop architecture, schemas, contracts, migrations, UI, domain logic, adapters, configuration, operational procedures and independent tests first. **Production database connection and database-dependent integration form the final major implementation stage, P11.** P12 is verification and handoff for subsequent release work, not a further feature-building phase. The app can reach a useful pre-integration milestone while HDE remains unfinished; that milestone must never be described as production-ready.

This plan supersedes the earlier research report's suggestion that all application implementation should wait for a completed HDE contract. Most application work proceeds behind a provisional, isolated integration boundary. Live HDE compatibility and real persistence remain later evidence requirements.

### Product baseline

- iOS and Android applications; no consumer web dating application.
- Verified account onboarding; adults-only eligibility; consent, private birth inputs, profiles and photos.
- Recommended people first, then broader discovery. A recommendation is not a mutual match or permission to message.
- Reciprocal preferences and visibility rules; accessible swipe alternatives; likes, passes, mutual matches and unmatch.
- One-to-one text chat after mutual match; notifications with privacy-safe content and user controls.
- Block, report, moderation, appeals, support, profile pause, data export and account deletion.
- WordPress as the operator interface and public policy/support site, with the dating API enforcing permissions and domain rules.
- PostgreSQL as application domain persistence; Railway for application services; Cloudflare private media where suitable.
- HDE integration through the supported engine boundary. Paid features are conditional on a real product decision and provider approval.

Voice/video, public feeds, consumer web parity, custom chat infrastructure, speculative machine learning, all-pairs compatibility computation, and a large multi-agent orchestration system are outside the initial release scope. Existing-user migration is included only if P01 discovers relevant users/data and the owner authorizes a defined migration.

## 2. Control surfaces and source authority

| Surface | Established location | What it owns |
|---|---|---|
| Operational control | [Glow Dating App — Implementation Control](https://app.notion.com/p/3e44590a05eb8118bf02f0dc0c3ea57c) | Current state, active work, blockers, next action and exact authoritative links |
| Work register | [Glow Dating App — Work Register](https://app.notion.com/p/71b769915b5b4e00830663770bc95f7e) | Task/decision/dependency/risk status and evidence pointers; never a second technical specification |
| Persistent planning | `docs/planning/` | Durable plans, briefs, source snapshots, decisions and database audit evidence |
| Separate application canon | `docs/pf-canon/` | Current GAPP-PF00 and GAPP-PF01, in Markdown |
| Working material | `docs/ephemeral/` | Prunable single-use Markdown prompts and temporary handoffs after promotion of unique evidence |
| Application repository | Private `amthorn78/glow-dating-app`, default branch `main` | All durable implementation documentation and code; no operational Drive dependency |

**Three documentation layers remain distinct.** Repository implementation documents describe the actual code, contracts, configuration, testing and operation. The **GAPP-PF** canon owns application-level governing rules and durable architectural constraints. Ephemeral files are noncanonical. These are logical layers: the application canon may live in a clearly separated `docs/pf-canon/` directory inside the application repository. It never joins or renumbers the HDE PF canon.

### Historical authority transfer in P01 — completed

The following steps describe the completed transfer, not a requirement to access Drive again. D09 and `docs/README.md` now govern ongoing documentation.

1. Establish or select the application repository after the bounded reuse assessment. Record its exact owner, name, visibility, default branch and baseline commit in Notion.
2. Commit GAPP-PF00 and this plan under `docs/pf-canon/`. Preserve the initial plan revision and source links. Add a small `AGENTS.md` that routes sessions to the index and current handoff; it does not duplicate the canon.
3. Record the authority-transfer commit and date in the index, Notion and the Drive index. Thereafter the repository owns the current plan. Mark the Drive plan as a historical planning snapshot and link to the repository authority; do not maintain two editable copies.
4. Create focused implementation documents only when their owning work is undertaken. Notion holds a link and completion state, not a pasted copy. A generated file becomes canonical only through an explicit promotion with an owner and replacement/retirement of any superseded home.

Repository locations (the WordPress plugin remains planned; other component/documentation homes exist):

| Location | Content |
|---|---|
| `apps/mobile/` | Expo/React Native app, platform configuration and client tests |
| `services/api/` | Django/DRF application, domain services, provider adapters, persistence mappings and workers |
| `wordpress/glow-admin/` | Narrow WordPress operator plugin and its tests; no second dating backend |
| `packages/contracts/` | Versioned OpenAPI/JSON schemas and generated client types; authoritative wire definitions |
| `docs/pf-canon/` | GAPP-PF00 index, GAPP-PF01 plan, then focused product/safety and HDE-boundary rules when required |
| `docs/architecture/`, `docs/adr/` | System/data diagrams, state machines, threat model and durable implementation decisions |
| `docs/operations/`, `docs/testing/` | Setup, environments, runbooks, acceptance matrix and evidence index |
| `docs/continuity/` | Current handoff and concise append-only implementation log |
| `docs/planning/`, `docs/ephemeral/` | Persistent plans versus prunable prompts; all Markdown; see documentation guide |
| `.work/` | Ignored local scratch, generated intermediates and experimental material; secrets never committed |

Use stable document titles and IDs in durable references; record source revision/commit in evidence metadata. HDE reference material remains external. This project adopts its discipline of intent → change → proof, single authority, clear boundaries and honest claim states. It does not import the HDE Epic/CRD approval or multi-session machinery.

## 3. Existing estate: preserve, assess, replace or retire

### Verified planning inventory

Read-only connector inspection on 23 September 2026 found:

| Asset | Observed identity and evidence | Planning disposition |
|---|---|---|
| HDE source | [amthorn78/glow-hdengine-v2](https://github.com/amthorn78/glow-hdengine-v2); observed/deployed commit `a63bf801665fbc19839fc013fcdb05386a1b0d09` | Preserve; external protected integration target |
| HDE Railway project | `ample-illumination`, project `ce01529f-679f-4f52-a979-23113299a59b`; production environment `a06b149a-2876-40bf-84a0-7880feaf8b67` | Preserve shared project and its existing operations |
| HDE service | `glow-hdengine-v2`, service `62e7b993-6d30-48b4-9059-c1884b16e90b`; source HDE repository `main`; latest observed deployment `7522ba86-37a8-41f2-84c5-e14caf697bb9` reported SUCCESS | Deployment metadata is not an engine-completion, contract or health certification |
| PostgreSQL beside HDE | Service `c4d54416-d1ab-4818-898b-9b9be03bc69a`; persistent volume `aad776ab-27cc-4994-87f0-589af0de7aa1`; configured PostgreSQL 17 image | Protect. Exact HDE/legacy database and role mapping remains to be verified; do not infer ownership solely from colocation |
| Legacy application service | `glow-backend-v4`, service `bfedf816-d6d4-4155-b495-cd6416e91e49`, source [amthorn78/glow-backend-v4](https://github.com/amthorn78/glow-backend-v4) `main` | Reuse-assessment candidate; do not redeploy or delete during planning |
| Redis in shared project | Service `87b4810c-3e23-4d27-b7fc-0bca7131ed37` | Ownership and current consumers unresolved; do not flush, repurpose or retire |
| Other owned Glow repositories | Sixteen `glow` repositories surfaced in owner search, including several backend/frontend/template generations | Inventory relevant candidates, not sixteen mandatory audits; bound examination to likely reusable assets |
| Other Railway projects | `tranquil-courtesy` contains `cmv-website` and Postgres; `valiant-clarity` contains `englishbiztraining`; `acs-wagtail-baseline-validation` also exists | Outside this application's change scope |
| Older Drive web folder | Web Front End / PF Canon contains an old build-log document that returned empty content | Preserve as legacy context; new mobile application has its own named control surfaces |

Variable **names**, not secret values, were inspected for the three relevant service configurations. HDE and the legacy backend both have a `DATABASE_URL` variable. This does not establish whether they point to the same logical database or use separate roles. No production database connection, SQL query, secret rotation, code mutation, service deployment or infrastructure retirement was performed to prepare this plan.

### P01 bounded reuse assessment

Start with `glow-backend-v4`, the newest relevant frontend, and their immediate schema/tests/configuration sources. For each candidate record source commit, license/ownership, actual deployment consumers, data dependencies, tested behavior, adaptation cost and disposition: **retain**, **configure**, **modify**, **replace**, or **retire later**. Read existing repository instructions before making any change. Inspect supplied schema/migration files now; the separately scoped AP1-DBA-001 read-only catalog audit is the sole recorded early-inspection exception. App persistence connection and database-dependent acceptance remain P11.

Use one bounded assessment work item, normally no more than one focused implementation checkpoint before choosing the baseline. Do not reopen a broad marketplace search. New application foundation remains the default. Salvage small, understood assets with provenance and tests. Retaining a substantial backend instead of the selected Django baseline requires a short ADR showing lower total implementation and maintenance cost, not merely existing code volume. It is a material architecture choice to present to the owner if it changes the selected direction.

The prior research sampled legacy SQL-parameter logging, development-secret/session fallbacks, broad CORS and older HD/scoring coupling. Those are inspection findings, not a full security audit or proof of live exposure. Do not copy those patterns into the new app.

**Retirement is separate work.** “Not reused” does not authorize deleting repositories, volumes, services, Redis keys or user data. Record an archive/retirement candidate with consumers, backup/export, rollback, DNS and data-retention consequences. Carry it to a later explicit disposition. Shared HDE resources are excluded from routine cleanup.

## 4. Selected architecture and reuse policy

| Area | Baseline | What is reused / configured / built |
|---|---|---|
| Mobile | Stable Expo + React Native + TypeScript, Expo Router | Reuse official scaffold and native modules; configure builds/deep links; build Glow screens and interaction states |
| API | Django supported LTS + DRF modular monolith | Reuse framework validation/auth ecosystem/migrations; build small domain modules and API policies |
| Authentication | django-allauth headless with supported native token strategy | Configure verification/recovery/provider linking and revocation; do not create custom password or token cryptography |
| Persistence | PostgreSQL application data behind repository/unit-of-work interfaces | Design SQL constraints and migration files early; connect and prove real behavior in P11 |
| Jobs | Celery/Redis with transactional outbox and bounded retries | Reuse queue mechanics; build durable domain events, deduplication and dead-letter/reconciliation procedures |
| HDE | App-owned port and one HDE adapter | Build mapping, timeout/error handling and provenance; reuse engine intelligence and protected engine data |
| Media | Cloudflare Images/private R2 as appropriate | Reuse upload/storage/delivery; build authorization, quarantine, moderation and lifecycle state |
| Chat | Stream Chat is preferred, subject to permission and cost proof | Reuse transport/history/native UI where safe; build app-controlled mutual-match and block enforcement |
| Billing | RevenueCat/store SDKs if monetization is selected | Reuse purchase/receipt lifecycle; build entitlement rules, reconciliation and support surfaces |
| Operations | WordPress plugin calling scoped application admin APIs | Reuse WordPress staff UI/CMS; app API owns dating authorization, moderation state and audit history |
| Quality/operations | CI, standard test runners, error/metric tooling | Configure reproducible checks, redaction, alerts and release evidence; no custom orchestration platform |

Pin exact framework, runtime, native SDK and package versions together in P01 after checking current official support and compatibility. The research snapshot recommended a stable Expo release and Django LTS; repository `main`, preview SDKs and unconstrained “latest” are not release pins. The implementation lockfiles, container image digests, native build settings and SBOM become the reproducible authority. Paid services remain choices subject to their specific access/budget gates, not purchases made by this document.

### Module and trust boundaries

The mobile client is untrusted. The API authenticates requests, validates inputs and enforces authorization and state transitions. Domain services depend on narrow ports for persistence, identity, media, messaging, notifications and HDE. Use these seams where substitution is needed; do not build a generic enterprise framework or duplicate Django's ORM.

Suggested domain modules: identity/consent, profiles/media, preferences/eligibility, discovery/compatibility, interactions/matches, communication, safety/moderation, privacy/deletion, support and entitlements. All state changes that must agree atomically share one application transaction. Provider work is emitted through an outbox after commit; workers use idempotency and reconciliation. There is no distributed two-phase transaction with chat or HDE.

PostgreSQL is the system of record for dating-domain state. Managed chat may own message bodies under an explicit data-processing/retention contract; the application owns match/channel entitlement and moderation-case references. Cloudflare owns media bytes; PostgreSQL owns media status and ownership. WordPress has its own CMS/staff storage and is not a second dating database.

On 23 September 2026, during AP1-P03-001 execution, Nathan directed: “the app should be in the same project as the HD Engine”. The application therefore belongs in existing Railway project `ample-illumination` (`ce01529f-679f-4f52-a979-23113299a59b`). This supersedes the earlier separate-project default and P01 disposition. Use separate app-owned services and service/environment-scoped configuration and secrets. Project placement does not grant permission to alter HDE or shared settings. Services in the same environment share private networking; service ownership is not network isolation. Exact app environments, domains and resource IDs must be verified when provisioned. P03 may finish preparation without idle services. See [same-project decision](../adr/0002-same-project-application-services.md) and [resource ownership](../operations/resource-ownership.md).

The newer owner direction recorded in [Implementation Control](https://app.notion.com/p/3e44590a05eb8118bf02f0dc0c3ea57c) prefers the **same logical PostgreSQL database as HDE**, with app-owned schema/tables and restricted app runtime/migration roles, unless assessment establishes a strong concrete reason against it. No legacy user information needs migration. Appropriate existing app structures may be reused or repurposed after object-level ownership/dependency review; the 32 provisional P02 models are not a decision to create 32 new tables. Map HDE-owned, reusable app-owned, obsolete app-owned and new-required objects before committing a physical layout, with exactly one migration owner per table and explicit allowed reads/writes. HDE schema/data/behavior, credentials, grants and actual dependencies remain protected; shared capacity and deployment effects must be assessed. Neither a shared database nor `public` is an app-only cleanup boundary.

The [completed 23 September database audit](../planning/database-audit-2026-09-23.md) and [catalog/model map](../planning/database-catalog-2026-09-23.md) resolve the dated logical-database/ownership inspection: HDE and legacy backend use database `railway` with privileged `postgres`; protect `hde` and `public.hde_body_graphs_current`. None of the 32 provisional app models maps to an approved reusable physical legacy relation. The audit recommends a clean app-owned schema and restricted roles; no role/DDL/runtime change has occurred. These dated observations require reverification before P11 mutation. A02 remains open for implemented isolation, capacity, effects and acceptance. The audit’s early read-only exception does not authorize new database connections during this migration.

## 5. HDE integration contract: fixed responsibilities, provisional wire details

### Established facts versus assumptions

The inspected HDE HTTP adapter and supplied CLI/API reference describe `POST /api/reader?v=1` with `a_id` and `b_id` UUID inputs and a closed, numeric-free public Reader response. Eligible public results include a harmony band. The development sampler is not a production recommendation API. This is a source snapshot of an unfinished system, not a commitment that the final application-facing integration contract is complete.

The app must not obtain ranking data by reading undocumented HDE tables, scraping CLI diagnostics, opening development routes, or reimplementing compatibility math. It must not add numeric scores to the public Reader v1 shape. If only permitted bands are available, ranking operates at that granularity with documented application-owned secondary criteria; it must not invent fine-grained scores. A richer internal interface requires an authorized engine contract, with HDE changes handled in the engine's own system.

### App-owned ports to establish in P02

Names in this table are proposed internal interfaces, **not claimed HDE endpoints or schemas**.

| Port / contract | App-side responsibility | Unresolved engine-side agreement |
|---|---|---|
| BirthInput / ChartResolver | Preserve entered date, local time, place, uncertainty and consent; surface ambiguity; map account to opaque engine chart reference | Accepted input fields, place/timezone resolution, missing/uncertain time behavior, chart creation/update identity and idempotency |
| CompatibilityProvider | Request a bounded eligible candidate set/pair; accept typed ready/pending/unavailable/unsupported responses | Supported single/batch operations, output granularity, directionality, engine versions, authentication and throughput |
| CompatibilityProjection | Expose only approved user-facing explanation/band and freshness state | Allowed fields, wording, eligibility meaning, persistence/cache rights and invalidation signals |
| EngineLifecycle | Remove/invalidate app references and orchestrate deletion/recalculation requests | Engine ownership, deletion/retention obligations, completion evidence and shared-chart handling |

Keep app identity and engine chart identity distinct. Store an explicit mapping with state/version provenance; do not assume the same UUID represents both. Birth details remain private. No guessed birth time, silent UTC conversion or public exact location. Changing birth inputs invalidates affected results only after the corresponding engine identity/version is resolved. Compatibility caching keys must include the relevant input/engine/contract versions; normalize pair direction only if the engine guarantees symmetry.

Fixtures cover pending charts, ambiguous birth data, unsupported output, no eligible results, engine timeout, partial batch response, retry, version mismatch and deletion. Synthetic compatibility labels are marked as fixtures in development/test contexts and cannot be exposed as real HD results to users. Production boot rejects fake HDE providers.

Before live integration, obtain the completed/explicitly supported HDE release contract, exact environment and credentials, data-owner mapping, permitted reads/writes, idempotency model, rate limits, retry policy, error semantics, output/cache rights and deletion obligations. Record the contract version and HDE commit/deployment. An engine deployment status alone does not discharge this dependency.

If HDE is still unfinished at P11, complete application-persistence/provider checks that do not require it, mark live compatibility acceptance blocked, and retain a runnable fixture-backed development build. Do not silently substitute old vendor scoring or announce release readiness.

## 6. Data architecture now; database connection last

### Data groups and invariants to design in P02

| Data group | Essential design and invariant |
|---|---|
| Account, credential/session metadata, consent | Unique normalized identity, safe linking, revocation and versioned consent; credentials delegated to the auth library |
| Profile, preferences, visibility | Separate private/public projections; reciprocal eligibility, completion and pause states; age and location disclosure boundaries |
| BirthInput and EngineIdentity | Private input record and explicit opaque HDE mapping; provenance/uncertainty retained; no duplicate engine calculations |
| MediaAsset | Owner, storage reference, state, order and moderation decision; only approved variants eligible for public delivery |
| Like, pass, Match and block | Directional actions; canonical unordered match pair; uniqueness and transactional state transitions; block overrides discovery and messaging |
| RecommendationBatch/entry and CompatibilitySnapshot | Bounded candidates, eligibility version, freshness, engine/contract provenance; no unbounded all-pairs cache |
| ChatBinding/device notifications | Unique match-to-channel mapping; send entitlement, device tokens and preferences; message-body ownership explicit |
| Report, Case, Appeal, StaffAudit | Least-privilege evidence access, reasoned actions and restricted audit trail; support access separated from moderation powers |
| Deletion/export jobs and retention tombstones | Durable progress, retryable provider steps, deadlines, verification and restore-time deletion replay |
| Entitlement/webhook inbox/outbox | Verified provider events, idempotency keys, replay protection and reconciliation; payment state never trusted from client flags |

Define identifiers, nullability, timezone semantics, unique/check/foreign-key constraints, indexes, retention categories and migration order before UI/API contracts stabilize. Model and migration files may be authored and reviewed without applying them. SQL execution, Django migration behavior, locking, ORM performance and database-backed authentication remain unproven until the real database test stage.

### Four operating states

| State | Available storage/integration | Honest claim |
|---|---|---|
| Planning — P00 | Documents and metadata reads only | Plan and control surfaces exist |
| Isolated development — P01–P10 | In-memory/fixture repositories, deterministic adapters and explicitly temporary local storage | UI/domain/contract behavior demonstrated under the named substitutes |
| Final integration — P11A/B | Disposable PostgreSQL first, then staging app database and sandbox/approved providers; HDE contract environment when ready | Real persistence, authentication, migrations, concurrency and provider behavior tested within named environments |
| Production connection — P11C | Verified final app database and approved HDE production service, with protected engine database ownership preserved | Controlled production integration smoke evidence; not a public release |

Database-dependent Django/allauth behavior cannot responsibly be certified with an in-memory domain repository. That is why P11 begins with disposable PostgreSQL before staging and production. Fakes must implement the same narrow repository contract and be run against the same conformance cases as the real adapter later; they are not an alternate production backend. Do not build a shadow SQL engine or spend weeks simulating PostgreSQL.

WordPress itself needs a database to boot. If native plugin validation is required before P11, a disposable local CMS database is permitted as temporary development storage; it does not connect the application or HDE production database. Record that limited use. Other requests to bring real database integration forward require a concrete technical reason and an explicit plan amendment; development convenience alone is insufficient.

### Migration and connection safety

- Design forward/expand-contract migrations and separate data backfills; keep compatible application rollback possible. Do not describe database rollback as simply reverting a Git commit.
- At P11, inspect the actual app objects and migration ledger before applying anything. A blank shared database is not presumed. Nathan requires no legacy-user migration; clean app data does not authorize deleting legacy or HDE dependencies.
- Application migrations may affect only verified app-owned objects. In the preferred shared logical database, distinguish exact app schema, object ownership, runtime/migration roles and dependencies from HDE; reject ambiguous scope. Never alter HDE objects/data/grants or restore/reset the shared database or volume under an app-only migration action.
- Use separate runtime and migration privileges, environment-specific credentials, TLS/private networking as supported, bounded connection pools, transaction/statement timeouts and secret references. Keep credentials out of repo, Notion, Drive, logs and chat.
- Establish and test backup/restore, recovery objectives and deletion-tombstone replay. Backup configuration or a “successful backup” status is not a restore proof. Do not assume PITR or high availability is enabled because a platform offers it.
- Before production connection, stage evidence, credentials, approved budget, target identity, migration set, backup/recovery proof, owner-resolved production authorization and a bounded smoke/rollback procedure must all exist.

## 7. Product behavior and security requirements

**Identity and onboarding.** Start with verified email and supported recovery. Add social login only with safe linking and platform-policy review. Use platform secure storage for native secrets, short-lived access credentials and server-side revocation of refresh/session state. Logout, password change, lost-device recovery, account suspension and deletion revoke the appropriate sessions. Test enumeration resistance, token replay, expired links, wrong-account linking and deep-link interception. Fixture sign-in is development-only and is never production authentication evidence.

**Discovery and matching.** Apply age/consent/completeness/visibility/moderation/block/reciprocal-preference eligibility before HDE ranking. Recommendations and broader discovery share these rules. Use bounded, stable queues, cursor pagination and explicit refresh/invalidation; do not score the entire population against itself. A like is idempotent. Simultaneous reciprocal likes produce one match and one logical match-created event. Recheck current state for every privileged action. Define resurfacing, unmatch/rematch and deleted/paused-account behavior explicitly.

**Media.** Issue short-lived upload grants; enforce ownership, size/count/type limits and safe decoding. Strip metadata, quarantine originals, moderate before publication and expose only approved variants through authorized delivery. Handle abandoned uploads, reordering, retries, removal and downstream purge. Neither an uploaded filename nor a successful vendor upload proves that an image is safe or publicly eligible.

**Chat and notifications.** A mutual match is required to obtain a channel entitlement and send. Use server-controlled channel membership and app-authorized sending; prove provider permissions prevent clients bypassing that route. Stream's documented before-message-send hook can allow messages through when the hook fails, so that hook alone is insufficient as Glow's match/block gate. Prove fail-closed behavior using the chosen provider configuration; otherwise change the provider/design before launch. Serialize or otherwise define the linearization of send versus block/unmatch: no newly authorized send after the block/unmatch commit. Test in-flight messages, stale tokens, existing channels, retries, reconnect and cross-device behavior. Decide the policy for existing conversation history separately from future contact. Push copy must not expose birth details, sensitive compatibility data or message bodies by default.

**Safety, privacy and operations.** Block/report are available from profile and chat, including after unmatch. Moderation actions, evidence retention, appeal and urgent escalation have named operational owners. WordPress staff authentication is distinct from dating-user authentication; privileged API calls enforce scope and audit the staff actor. Draft real public community/child-safety/support policies, then have the owner confirm the actual operating responsibilities. Configure least privilege and redaction; no raw birth data, chat bodies, tokens or SQL parameters in routine logs.

**Export and deletion.** Deletion immediately removes visibility and access, then durably purges or restricts data across app persistence, HDE responsibilities, chat, media, push, analytics and support systems according to the documented retention policy. Explain unavoidable retained safety/legal records precisely. Test retries, partial failures and backup restore without resurrecting a deleted account. Provide in-app and public request routes where required; deletion is not merely hiding the profile.

**Billing.** Until the owner chooses paid launch, keep entitlements behind a port and leave purchase UI disabled. If paid: verify store/RevenueCat webhook signatures and replay handling; handle restore, refund, revocation, grace and cross-device state. Do not treat a WordPress payment or client receipt assertion as an entitlement. Obtain actual product and budget decisions when needed.

**Mobile/store readiness.** Maintain a dated requirements matrix for Apple and Google covering distinctive dating-product value, UGC moderation/report/block/contact, adults-only eligibility, child-safety duties, privacy disclosures, account deletion, sign-in, subscriptions, permissions and review access. Recheck official policies and build requirements when producing release artifacts. Validate supported iOS/Android SDKs, native-library compatibility, privacy manifests/Data Safety disclosures, deep links, denied permissions, accessibility, large text, keyboard behavior, offline recovery and real-device performance. A successful Expo preview or JavaScript test is not a signed native-build or store-approval proof.

## 8. Work sequence and dependency model

The following phases are checkpoints, not separate required sessions or automatic owner approvals. One session may complete several in sequence. Tasks may be split when an independently reviewable outcome becomes clearer; preserve the parent ID and dependency links. Aim for one coherent reviewable change per task, typically a short work block up to one or two focused working days, without making AI-time promises.

| Phase | Main outcome | Depends on | Work allowed before HDE/final DB readiness |
|---|---|---|---|
| P00 | Governing plan and tracking recorded | Brief/research | Entire phase |
| P01 | Reuse disposition, repository and reproducible development base | P00 | Entire phase; no production DB access |
| P02 | Contracts, domain/data design and HDE seam | P01 | Entire phase with declared HDE assumptions |
| P03 | Config, CI, operational and secret-management preparation | P01/P02 | Preparation and isolated checks; spending/access gates apply only to affected actions |
| P04 | Native shell, onboarding, profiles and media flows | P02; P03 build/config basics | Fixture/sandbox-backed behavior |
| P05 | Eligibility, recommendation/discovery and mutual-match logic | P02/P04 contracts | Domain behavior and client flows; PG concurrency proof later |
| P06 | Messaging and notification integration seams | P02/P05 match contract | Provider capability proof and fixture/sandbox flows |
| P07 | Safety, WordPress operations and support | P02; P04–P06 relevant contracts | Almost all workflow/UI/policy preparation |
| P08 | Privacy lifecycle and conditional entitlements | P02/P04/P06/P07 contracts | Orchestration logic and provider fixtures |
| P09 | Security, native quality, observability and release preparation | Feature slices available | Independent quality checks and access-enabled native builds |
| P10 | Pre-integration readiness evidence | P01–P09 | Entire phase; explicitly records deferred real-integration evidence |
| P11 | Disposable/staging persistence, live integration, final production connection | P10 plus actual external gates | Substages proceed independently where prerequisites permit |
| P12 | Verified release-candidate handoff | P11 mandatory acceptance | Verification and readiness record; public release remains separate |

Logical parallel work is possible: P03 operations preparation can overlap P04 UI; P05 domain rules and P06 provider capability work can progress independently once contracts agree; public policy/support drafting can overlap P07; P09 checks run incrementally throughout. This is scheduling flexibility for one session, not authorization or a requirement to spawn agents. Keep one active work item in the register unless a concrete asynchronous operation is being tracked.

### P00 — Establish the governing record

- **Objective:** make the project resumable before code changes.
- **Inputs:** owner's brief and scratch-build direction, reuse clarification, prior research, relevant HDE references and live metadata.
- **Operations:** verify parents; establish the Drive project/folders, separate canon index, Notion control page and work register. Preserve original source copies.
- **Development:** none; record architecture decisions, proposed paths and genuine unknowns.
- **Documentation:** this plan; GAPP-PF00; source links; task, decision, dependency and risk entries; current handoff.
- **Dependencies/HDE:** no engine completion needed. Record protected identities and unverified DB ownership mapping.
- **Validation:** read back saved records; check links, phase coverage, task IDs, dependencies and truthful status. Confirm no implementation/deployment occurred.
- **Completion:** governing plan and register are accessible and cross-linked. No claim that later gates are approved.
- **Handoff:** P01.1 is the next ready task; no implementation commit exists.

### P01 — Assess reuse and establish the application repository

- **Objective:** a clean, reproducible development base with an explicit old-estate disposition.
- **Inputs:** P00 records, read access to likely legacy repositories/configuration, source ownership and repository instructions.
- **Operations:** identify deployment consumers and data dependencies from metadata/source; choose reuse or fresh locations; preserve unrelated work; create/select a private app repository when access permits. Configure branch protection/required checks appropriate to the account without inventing mandatory human review. Do not change HDE auto-deploy settings.
- **Development:** scaffold pinned Expo/TypeScript and Django/DRF skeletons, package locks, lint/type tooling, container/dev commands, deterministic fixture runner and one vertical nonpersistent smoke flow. Initialize scoped configuration and ignored working areas.
- **Documentation:** reuse ADR/disposition inventory, README/setup, GAPP-PF00/GAPP-PF01 authority transfer, dependency/license inventory and first continuity checkpoint.
- **Dependencies/HDE:** engine repository is read-only; no schema or math copied as application logic. GitHub credentials/permissions may block publication but not local preparation.
- **Validation:** clean checkout install/build/checks; no committed secrets; lock reproducibility; baseline licensing; fake providers explicitly development-scoped. Record exact commands/exit codes and limits.
- **Completion:** selected repository baseline and reproducible local development documented; each examined legacy asset has a disposition; no infrastructure discarded.
- **Handoff:** repository URL/branch/commit, setup instructions, current worktree state and next contract task.

### P02 — Define architecture, contracts and data model

- **Objective:** stable app-owned responsibilities and a replaceable HDE/persistence boundary.
- **Inputs:** P01 baseline, product scope, inspected HDE source contract, provisional assumptions.
- **Operations:** map environment/data owners, threat boundaries and required provider accounts; identify user decisions by last responsible phase.
- **Development:** define domain state machines, public/private projections, OpenAPI/JSON schemas, typed clients, repository/unit-of-work ports, provider interfaces and fixture adapters. Write model/migration definitions and constraints without applying them. Establish contract-version and error conventions.
- **Documentation:** architecture/data model, API schema, ADRs, HDE assumption register, initial privacy/retention and safety rules. Add focused GAPP-PF rules only for concepts needing durable governance; route implementations to their owning documents.
- **Dependencies/HDE:** final engine fields remain behind adapter mapping; no app DTO masquerades as the engine's final wire schema.
- **Validation:** schema validation, generated-client consistency, domain invariant tests, malformed/unauthorized input cases and fixture-provider conformance. Review migration design statically.
- **Completion:** every launch flow maps to a domain owner, contract, data owner and acceptance case; provisional seams are explicit; DB/HDE-dependent proofs remain marked deferred.
- **Handoff:** versioned contract baseline, migration plan and fixture catalog for UI/domain implementation.

### P03 — Prepare operations, environments and configuration

- **Objective:** reliable execution and deployment preparation without final database dependency.
- **Inputs:** P01 tooling, P02 architecture, Railway reuse disposition and available account access.
- **Operations:** define local/test/staging/production separation, domains, service identities, secret ownership and spending limits. Prepare Railway API/worker/Redis topology and deploy configuration; provision only approved isolated resources when needed. Prepare Cloudflare, mail, chat, notification and monitoring accounts/config without exposing credentials. No production database attachment.
- **Development:** CI jobs, build artifacts, health/liveness/readiness distinctions, typed configuration validation, structured logs/correlation IDs, retry/backoff primitives, metrics and feature controls. Prepare secure webhook verification and provider adapter shells.
- **Documentation:** environment/config variable catalog with names and purpose only, service ownership map, secret rotation/incident runbooks, CI and backup/restore plan.
- **Dependencies/HDE:** an HDE endpoint/config slot remains unset or fake in development; no shared secret copying. Billing/account-owner access can block provisioning while config work proceeds.
- **Validation:** missing/invalid production configuration fails closed; no fake adapter in production; redaction checks; CI repeatability; worker retry behavior using substitutes.
- **Completion:** build/deploy and operational configuration are reviewable; gated external actions are precisely recorded, not marked completed.
- **Handoff:** reproducible artifacts, configuration matrix and resource/access checklist for feature work and later P11 activation.

### P04 — Build onboarding, profiles and media

- **Objective:** a coherent native user journey from account entry to a discoverable profile.
- **Inputs:** design primitives, P02 contracts and fixtures, P03 environment/config basics.
- **Operations:** establish product copy and consent versions, email/deep-link sandbox settings, media limits and review policy. Track Apple/Google identity and signing access when native builds require it.
- **Development:** accessible navigation; account/verification/recovery screens; adult eligibility; resumable onboarding; private birth-input uncertainty handling; profile/preferences editing; pause visibility; upload/retry/reorder/delete flows. Use real auth/media SDK configuration where possible, with clearly separated fixture modes for database-dependent behavior.
- **Documentation:** onboarding/profile/media state machines, public-field projection, UX acceptance cases and provider integration notes.
- **Dependencies/HDE:** birth-input validation collects honest source facts; chart resolution remains an adapter result, not client-side HD calculation.
- **Validation:** incomplete/underage/suspended profiles cannot enter discovery in domain cases; invalid media and interrupted uploads; denied permissions; large text/screen reader; loss/recovery of app state. Auth-backed persistence and real media-policy enforcement remain P11 cases.
- **Completion:** end-to-end fixture journey works on the available development runtime; unsupported native/device checks are named, not inferred from browser rendering.
- **Handoff:** stable identity/profile/media contracts and test data for discovery and safety.

### P05 — Implement recommendations, discovery and mutual matching

- **Objective:** consistent eligible-person selection and correct interaction state.
- **Inputs:** P02 eligibility/interaction contracts, P04 profile/preference state, HDE fixture provider.
- **Operations:** resolve launch market, ranking presentation and resurfacing defaults when needed; define candidate/performance budgets as test targets, not measured capacity.
- **Development:** reciprocal filtering, recommended queue, broader discovery, pagination, accessible like/pass actions, optimistic UI with authoritative reconciliation, idempotency keys, canonical match pairs and unmatch/block invalidation. Prepare transaction/outbox mapping for later real persistence.
- **Documentation:** eligibility truth table, ranking/provenance ADR, interaction state machine and concurrency acceptance cases.
- **Dependencies/HDE:** eligibility precedes compatibility. No numeric ranking invented beyond the permitted engine output; pending/error/empty states are normal outcomes.
- **Validation:** directional preferences, stale queues, repeated requests, paused/deleted/blocked candidates, empty markets and deterministic fixture ordering. Simulated races exercise logic, but PG atomicity awaits P11.
- **Completion:** recommendation-to-discovery behavior and interaction semantics satisfy contract tests; one logical match/event invariants are specified for real transactions.
- **Handoff:** channel entitlement input, queue invalidation rules and real-concurrency test specification for P06/P11.

### P06 — Implement chat and notifications

- **Objective:** useful communication with enforceable dating safety boundaries.
- **Inputs:** match/block contracts, chat-provider access and explicit capability proof requirements.
- **Operations:** evaluate provider permission model, data terms, quota and actual cost; obtain spending approval before paid activation. Configure sandbox channels, push identities and delivery ownership to prevent duplicate notification paths.
- **Development:** chat adapter and UI, server-mediated send authorization, controlled membership, unread/pagination/reconnect states, idempotent message submission, token lifecycle, notification preferences and retry/deduplication. Keep app entitlements authoritative.
- **Documentation:** provider permission proof, send-versus-block ordering, history policy, notification data flow and failure runbook.
- **Dependencies/HDE:** no HD data in chat authorization; only approved compatibility presentation may appear in the UI. Provider inability to enforce safety is a design blocker, not a future polish item.
- **Validation:** client bypass attempts, wrong-channel membership, direct SDK send restrictions, stale tokens, block/unmatch during send, provider outage, duplicate deliveries and privacy-safe push. Record which results require live persistence and must be rerun in P11.
- **Completion:** selected design has a credible tested provider-level safety path; transport/UI and synthetic workflows work. Any unproven capability remains explicitly blocked.
- **Handoff:** messaging/notification integration settings, evidence and deferred real-state cases.

### P07 — Build safety, WordPress operations and support

- **Objective:** users and operators can respond to abuse and support needs coherently.
- **Inputs:** account/profile/media/match/chat contracts and draft safety/retention rules.
- **Operations:** owner identifies actual moderation, child-safety and support responsibilities; draft severity/escalation/appeal policies and public support/community pages. Configure a disposable WordPress environment if available.
- **Development:** reporting and blocking from relevant surfaces, case queue, evidence references, reasoned account/photo actions, appeals, staff-scoped admin API and WordPress plugin views. Add audit and support case workflows without privileged database access from WordPress.
- **Documentation:** moderation/support runbooks, staff permission matrix, audit semantics, public policy drafts and temporary CMS-storage exception if used.
- **Dependencies/HDE:** engine outputs are not abuse determinations; operators cannot alter HDE tables or calculation rules through app moderation tools.
- **Validation:** role separation, object-level authorization, malicious evidence content, escalation paths, report-after-unmatch, block across discovery/chat and safe failure of operator APIs.
- **Completion:** workflows and staff UI are demonstrable; operating ownership and final public policy approval remain named launch dependencies where unresolved.
- **Handoff:** safety state and operator controls ready for privacy lifecycle and real-provider integration.

### P08 — Implement privacy lifecycle and conditional monetization

- **Objective:** account data and paid entitlement states have complete, recoverable lifecycles.
- **Inputs:** data inventory, P07 retention/safety responsibilities and provider lifecycle contracts.
- **Operations:** owner resolves retention/business decisions, launch countries and whether paid launch is required. Prepare public deletion/export/support routes and processor inventory. Legal/contract decisions use appropriate current guidance and accountable owner review.
- **Development:** export, immediate visibility/session revocation, durable deletion workflow, provider purge/retry/reconciliation and restore tombstone handling. If paid launch is chosen, implement store/RevenueCat entitlement adapter, purchase/restore/manage screens and verified webhook inbox. Otherwise retain a documented disabled seam and defer paid features.
- **Documentation:** data lifecycle map, retention schedule, deletion/export acceptance, entitlements ADR and truthful disclosure drafts.
- **Dependencies/HDE:** final engine deletion/retention contract is required for full purge acceptance; do not promise removal of data whose ownership is unresolved.
- **Validation:** partial/duplicate/out-of-order provider events, repeated deletion, export authorization, suspended/deleted accounts, refund/grace/restore if applicable. Database durability and downstream live purges are rerun in P11.
- **Completion:** lifecycle logic and UI pass substitute/sandbox cases; optional billing scope and unproven provider steps are explicit.
- **Handoff:** final integration lifecycle matrix and exact outstanding owner/provider obligations.

### P09 — Harden security, quality and release preparation

- **Objective:** remove independent defects and assemble native/operational evidence before persistence integration.
- **Inputs:** implemented feature slices, threat model, build artifacts and current platform documentation.
- **Operations:** configure monitoring/alerts, incident escalation, backup/restore procedure, dependency update policy and cost monitoring; prepare store listings, public URLs, reviewer instructions and account ownership. Recheck current Apple/Google requirements.
- **Development:** resolve actual security/accessibility/performance issues; add bounded abuse/rate-limit controls, safe errors, timeout/retry limits, observability and configuration hardening. Produce native development/release-track builds when signing access permits.
- **Documentation:** test/evidence index, security findings/disposition, native-device matrix, store compliance matrix and operational runbooks.
- **Dependencies/HDE:** no benchmark extrapolated from mocks to real engine throughput. No endpoint/secret embedded in client builds.
- **Validation:** lint/types/unit/contract checks; object authorization and malicious-input cases; native crash/permission/offline/accessibility tests; package/license/secret scans. Load tests before P11 measure only the substituted setup and are labeled accordingly.
- **Completion:** independent checks pass or have justified scoped deferrals; no unresolved critical security defect is hidden behind a phase label.
- **Handoff:** exact artifact commits/build IDs, remaining DB/provider/native-access gaps and remediation list for P10.

### P10 — Prove pre-integration readiness

- **Objective:** reach a substantially built, reviewable application before final data connections.
- **Inputs:** P01–P09 work and evidence, contract versions, migration files, provider designs and gate register.
- **Operations:** reconcile Notion against commits and actual resources; verify budgets/access/owner decisions needed for P11; prepare target manifests and rollback boundaries without applying migrations.
- **Development:** repair integration-independent defects; finalize adapter wiring, conformance suites, migration ordering and production fake-provider rejection. Avoid starting new scope.
- **Documentation:** pre-integration acceptance record with passed/failed/deferred cases, exact target assumptions, migration manifest and next executable P11 steps.
- **Dependencies/HDE:** pin the currently supported HDE contract when available; otherwise record precisely which cases wait and proceed with independent P11A work later.
- **Validation:** run the complete fixture user journey plus safety/deletion cases; review all production-only assumptions; ensure every deferred claim has a real integration test and owner.
- **Completion:** coherent app behavior under substitutes, no unexplained blockers, and a ready final-integration packet. This is expressly not production readiness.
- **Handoff:** candidate commit, test evidence, unresolved gates, proposed target identifiers and P11A entry state.

### P11 — Final database and live integration stage

- **Objective:** establish real persistence and supported HDE/provider behavior, then connect the final production targets safely.
- **Inputs:** P10 packet; exact app target/role; HDE contract/release/environment and authorized credentials; provider accounts; approved spending; migration/restore plan and production-action authority.
- **Dependencies/HDE:** P10 readiness is required before this stage; the supported engine contract and permitted test/production access are required before live HDE checks. Independent disposable/app-persistence work may proceed while that external dependency remains unresolved.
- **Operations:** verify all identities against current state, including HDE/legacy/app database ownership. Configure isolated app database roles, connections, backups and monitoring. Preserve the existing HDE database. Record actual settings without secret values.
- **Development — P11A:** use disposable PostgreSQL, apply migrations from zero and supported upgrade state, exercise ORM/auth/repository conformance, real constraints/locking, outbox durability and query plans. Repair defects here before staging.
- **Development — P11B:** connect staging app persistence and approved provider sandboxes; run real user journeys, HDE adapter conformance, media lifecycle, chat safety, notifications, moderation, deletion, billing if in scope, queue recovery and restore drills. Never use real users as test fixtures. If no HDE test environment exists, obtain a narrowly authorized read/test-data protocol for the protected engine before any live call.
- **Development — P11C:** only after stage evidence and real gates pass, verify production target identity, apply reviewed app migrations with the restricted app migration role, connect the app service using its runtime role, connect the supported HDE service and perform bounded private smoke checks. In the preferred shared logical database, app migrations may affect only verified app-owned objects; they must not alter HDE objects, grants, data or behavior. Shared effects require their concrete review before action. A production connection is not permission to open public traffic.
- **Documentation:** exact database/role/service identities, applied migration ledger, contract versions, HDE deployment, provider evidence, backup/restore proof, measured performance, incident/rollback record and final limitations.
- **Validation:** true concurrent reciprocal likes; transactional outbox crash recovery; auth revocation; block-versus-send race; deletion across providers; connection exhaustion/timeout; queue retry/dedup; HDE version/failure responses; restore including deletion replay; real index/query latency under stated load.
- **Completion:** all mandatory real-integration cases pass in their specified environments. If HDE or production authorization is missing, stop only that substage, retain verified earlier work, and mark the release candidate blocked. Never collapse staging success into production proof.
- **Handoff:** exact connected candidate state, migration and recovery evidence, open issues and P12 readiness checklist.

### P12 — Verify and hand off for subsequent release

- **Objective:** an evidence-backed release candidate and an executable next release procedure.
- **Inputs:** P11 results, native builds, public-policy readiness and final operational responsibilities.
- **Operations:** check support/moderation coverage, alerts, account ownership, renewal/cost exposure, store access and incident response; prepare staged rollout/rollback and review submission packet. Record unresolved external approvals explicitly.
- **Development:** only fixes needed to meet acceptance; each meaningful fix reruns affected checks and updates exact build/commit evidence. No silent new features.
- **Documentation:** release-candidate manifest, acceptance result, known limitations, final handoff, production operation/runbook links and separate legacy-retirement candidates.
- **Dependencies/HDE:** supported engine release and tested contract remain attached to the candidate; future incompatible changes require adapter/contract review.
- **Validation:** reconcile complete user journey, safety/privacy/security, real integration, native device matrix, store-policy evidence and rollback readiness. Verify that no fixture adapter or test account privileges can reach real users.
- **Completion:** either “ready for subsequent release work” with all required evidence, or a precise list of blockers. Store review, external distribution and public rollout remain separate actions under actual authorization.
- **Handoff:** next action, responsible owner, exact candidate/artifacts, permitted release scope and rollback boundaries. No automatic legacy deletion follows release.

## 9. Work register and completion discipline

The Notion register uses stable IDs (`P01.1`, `D01`, `A01`, `R01`), kind, phase, state, action class, dependencies, next action and evidence/plan links. It owns live state. This plan owns phase acceptance and sequencing. Seed tasks are reviewable work packages; expand them only when a real implementation boundary requires it.

**States:** Planned → Ready → In progress → Verified → Done. Use Blocked for a concrete unmet dependency, Deferred for an explicit scope/time decision, and Recorded for a governing decision/known assumption. A task is Ready only when its inputs and authority exist. Verified means evidence has been checked; Done adds the documentation/handoff update. A generated artifact or passing unrelated test is not completion evidence.

Each significant completed item records: intended outcome; source and target commit/resource identities; changed files/systems; decision/assumption IDs; actual commands/test environment/results; limitations; rollback implications; next step. Do not include secret values or personal production records. Keep durable evidence small: commit/CI/build links and reproducible commands, with larger necessary artifacts attached once at their owning home.

At session start read Notion's current state, GAPP-PF00, the current plan/contract and repository handoff. Verify the current branch/head/worktree and relevant resource identity before writing. At session end or before a costly/external action, checkpoint the actual state. If interrupted, inspect the artifact/resource before retrying; never duplicate an uncertain external write merely because the tool timed out.

Use scoped branches and coherent commits. Ordinary local edits, tests, documentation and authorized private app PR work can proceed without phase-by-phase approval. Preserve unrelated user changes. Merge only under the established repository policy and task authority; a merge that triggers deployment inherits that deployment's authority requirements. No force-push, destructive reset, legacy retirement or HDE mutation follows from routine cleanup.

## 10. Decisions, assumptions and true gates

### Current owner authorization and session roles — D08

On 23 September 2026, Nathan authorized a new implementation session, **App Builder 1**, with full permission to create or modify application-owned objects and repositories across **GitHub, Railway, Google Drive and Notion**, except where those changes affect the Glow HD Engine. **App Planner 1** is the coordinator and build manager; App Builder 1 reports its progress to App Planner 1.

This authorizes application repository creation, code/configuration/documentation changes, branches/PRs/merges, application-only service configuration and deployment, Railway provisioning, Drive files/folders and Notion pages/databases needed for the agreed build. Do not request permission again merely because an authorized action writes to one of those surfaces, creates ordinary application infrastructure or advances a phase. Routine Railway resource provisioning within this application build is covered; record configuration and visible cost implications as operational facts. Actual missing credentials or platform permission controls remain capability boundaries. Purchases or contractual commitments outside these surfaces, public store release and unrelated projects are not granted by this authorization.

The exception is based on **effect**, not folder or repository name. Do not modify HDE source, canon, engine-owned database objects/schema/data/roles/volumes, HDE services, deployment wiring, secrets, DNS or networking. Do not change shared resources, project-level settings, environment variables, Redis, automation, repository workflows or access controls if that could affect HDE. Where ownership or downstream effects are uncertain, keep that mutation pending and use an isolated application scope when possible. Read-only source/configuration inspection is permitted. AP1-DBA-001 has a separate narrow early read-only catalog-connection exception recorded above; it permits no DDL, deletion, role/grant change or runtime wiring. Otherwise live database connection and database-dependent acceptance remain P11. Engine-mutating API calls are outside this grant.

The existing HDE repository, Railway identities and colocated PostgreSQL/Redis in section 3 are the starting protected-resource list, not an exhaustive guarantee of isolation. App Builder 1 must verify current consumers and references before changing a legacy or shared surface. App Planner 1 may coordinate a proposed HDE change but cannot expand the owner's authorization or approve it on the owner's behalf.

The owner has authorized implementation in the new session; the earlier planning-only instruction has been satisfied and no longer blocks App Builder 1. Database-last sequencing and all evidence requirements remain. Application-owned production database creation, migration and connection are authorized at P11 once its prerequisites pass and the action cannot affect HDE. Any HDE-affecting integration step remains excluded until specifically authorized. Deletion/retirement of legacy assets or data is still a distinct disposition, not an implied consequence of choosing a new foundation.

App Builder 1 owns implementation, tests, repository documentation and accurate task updates. App Planner 1 owns coordination, progress assessment, cross-work dependencies and build-direction reconciliation. Reports are evidence-bearing checkpoints, not automatic approval requests. Continue independent authorized work after reporting unless a real decision or protected-resource boundary blocks it. Use the shared Notion report record and an addressed progress message for handoff; never claim another ChatGPT session received or read a report without verified delivery/acknowledgment. No background session transport or monitoring is implied by these role names.

### Claude Code transition — D09

On 24 September 2026 Nathan directed migration from ChatGPT web to Claude Code and paused new feature implementation. All documentation needed to plan, implement, review and hand off work must be repository Markdown. Notion remains coordination/status; Drive is historical provenance only. Persistent plans live in `docs/planning/`, disposable prompts in `docs/ephemeral/`, and the existing PF canon stays here. The receiving Claude session is the manager and commissions bounded one-off implementation sessions. Its first work is code/instruction/docs/CI/environment audit followed by a bounded setup and workflow optimization, not P06 feature work. No external prompt library is imported as governing workflow. Follow the [manager workflow](../planning/manager-workflow.md), [initiation](../planning/claude-code-initiation.md) and [migration record](../planning/claude-code-migration.md). D08’s protected boundary, ordinary app authorization and P11 sequencing remain unchanged. The earlier named-session grant is applied to this explicitly directed replacement environment, not an expansion to HDE.

### Initial decisions

| ID | Decision | State / governing basis |
|---|---|---|
| D01 | Fresh application foundation with maintained component reuse; existing assets assessed, not automatically inherited | Owner chose the scratch-build direction and clarified optional reuse |
| D02 | Preserve current HDE and its database; no app-side engine reimplementation | Owner's explicit integration priority |
| D03 | Production DB connection/database-dependent integration in P11; data design early | Owner's implementation brief |
| D04 | Notion coordination; repository Markdown owns all operational documentation; historical Drive planning superseded by D09 | Owner brief and 24 September transition direction |
| D05 | Separate GAPP-PF canon; one capable session; no automatic approval at each phase | Owner's implementation brief |
| D06 | Expo/RN + modular Django/DRF baseline, managed capabilities behind adapters | Selected planning design from research; exact pins and bounded reuse ADR in P01 |
| D07 | Stream preferred only if permissions and economics pass; paid services/billing conditional | Architecture safeguard, not purchase approval |
| D08 | App Builder 1 has full create/modify authority for the application across GitHub/Railway/Drive/Notion, excluding all HDE-affecting changes; App Planner 1 coordinates and receives progress | Owner's explicit session authorization, 23 September 2026; current controlling permission record |

| D09 | Repository Markdown operational authority; Claude manager with bounded implementation sessions; feature pause and setup optimization first | Owner direction, 24 September 2026 |

### Provisional assumptions and dependencies

| ID | Unresolved item | Needed by | Action / fallback |
|---|---|---|---|
| A01 | Final HDE chart, compatibility, version/cache and deletion contract | P11B | Build fixtures/adapter now; live HDE acceptance stays blocked until supported contract exists |
| A02 | HDE/legacy/app logical DB and role ownership, existing production users/data | Before any P11 target mutation or retirement | Inspect source/config metadata early; verify protected target at P11; no automatic import, overwrite or deletion |
| A03 | Reusable old app code and preferred repo/resource placement | P01 | Bounded evidence-based assessment; fresh private app base is default |
| A04 | Provider accounts, budget, signing credentials, domain ownership and admin access | P03/P06/P09/P11 as used | Prepare code/config first; request only the exact missing access or spend when action is ready |
| A05 | Launch geography/language, preference policy, moderation/support ownership and retention | P05/P07/P08 before final policy/launch | Use explicitly recorded provisional fixtures; owner resolves product/operating commitments |
| A06 | Paid launch and entitlement product scope | P08 | Default no active paid feature; do not buy a plan or invent pricing |
| A07 | HDE throughput and supported recommendation granularity | P11B before release acceptance | Bounded candidate strategy; measure actual contract; band ordering if that is all permitted |
| A08 | Chat provider can enforce app-owned match/block send authorization | P06 capability proof; rerun P11 | Prove SDK/permission behavior; change design/provider if bypass cannot be closed |

### Autonomy and real gates

| Action | Authority in implementation | When owner intervention is genuinely required |
|---|---|---|
| Read relevant sources/metadata, plan, create requested Drive/Notion records | Autonomous under this request | Only unresolved access or target ambiguity |
| Local app code, tests, docs, fixtures, reversible architecture details and bounded research | Autonomous after planning checkpoint | Material change to product scope or selected architecture, not each phase |
| App repository creation, branches/PRs/merges and documentation transfer | Authorized for App Builder 1 by D08; preserve the HDE boundary and required checks | Actual missing access or unresolved HDE impact; no repeated application-write approval |
| Configuration templates and isolated no-spend tests | Autonomous | Actual credentials or account-owner action if unavailable |
| Application-only Railway resource creation/configuration/deployment | Authorized by D08, including routine provisioning needed for the build | Actual access barriers or possible HDE effects; do not invent a separate provisioning-approval gate |
| New third-party paid subscriptions or contractual commitments outside the authorized surfaces | Prepare concrete configuration and cost first | Specific authorization if not already granted; independent app work continues |
| HDE API access within an existing supported contract | Prepare adapter autonomously | Missing credentials or permission for live/test data; never infer write rights from read access |
| Modify HDE code, PF canon, DB schema/data, shared secrets or protected service configuration | Outside ordinary app scope | Explicit HDE-specific authority and its governing process |
| Apply application-owned production migrations/connect final app targets | Authorized by D08 at P11 after its prerequisites pass; preserve engine-owned data and resources | Unclear ownership, possible HDE effects or actual missing access; not a repeat request for app-only authority |
| Publish to stores, invite external testers, enable public traffic, send messages to people | Prepare reviewable artifacts first | Actual release/recipient authorization and necessary account-owner action |
| Delete/archive legacy repositories or retire services/data/volumes | Record a separate disposition | Explicit destructive/retirement decision after consumers and recovery are known |

A request for credentials is not a request to paste secrets into conversation. Use the platform's secure credential mechanism. A blocked external action does not block unrelated local work. Nothing in this table creates a standing requirement for the owner to approve every phase, commit or routine test.

## 11. Validation, risks and release truth

| Evidence level | Can establish | Cannot establish |
|---|---|---|
| Static review / schema validation | Contract shape, documented ownership, source/config consistency | Runtime correctness or production reachability |
| Domain/unit/fixture tests | Deterministic state logic and client behavior under declared substitutes | PG transactions, real auth persistence or provider enforcement |
| Provider sandbox / native development build | Observed SDK/platform behavior in the stated sandbox/build | Production credentials/roles, store acceptance or real-market capacity |
| Disposable/staging PostgreSQL integration | Actual migration, ORM, auth, constraints, concurrency and restore behavior in that target | Production target identity/configuration without separate verification |
| Bounded production integration | Named service/credential/contract smoke behavior at a recorded time | General availability, unlimited scale or public launch approval |

Required final acceptance covers the complete account-to-profile-to-recommendations-to-mutual-match-to-chat journey; cross-surface block/report/unmatch; media authorization; staff permissions; privacy/export/deletion; recovery and revocation; optional purchase lifecycle; real HDE provenance/failures; actual persistence/concurrency; backup restore; observability; and signed native/device quality. Record load profiles, population sizes, p95 latency/error/queue budgets and measured results in P09/P11. Do not invent user-capacity or service-level guarantees before measurement and business targets exist.

| Risk | Early mitigation | Escalation condition |
|---|---|---|
| R01 — Late persistence defects due to DB-last | Narrow ports, real schema/migration design, shared conformance suite, P11A disposable PG before production | Structural issue cannot be isolated; amend plan and record evidence rather than conceal delay |
| R02 — HDE contract changes or remains unfinished | Versioned adapter, honest fixture states, bounded application-owned presentation | Final supported contract unavailable or requires app product change |
| R03 — Shared legacy/HDE infrastructure is accidentally changed | Exact identity map, protected service/volume list, no shared credentials or blanket cleanup | Ownership/consumer mapping ambiguous before a mutation |
| R04 — Managed chat safety bypass or unacceptable cost | Early permission proof and quote; app-owned entitlement; vendor-independent port | Direct client path can bypass block/match checks or price exceeds approved budget |
| R05 — Store/safety/operations gap | Build policy/UGC/deletion/support matrix early; native builds and named operators | Missing accountable safety operation or unresolved release-policy requirement |
| R06 — Duplicate docs and misleading progress | Single authority transfer, linked evidence, Notion live status, explicit claim levels | Plan, repository and deployed behavior disagree; stop affected work and reconcile |

No calendar delivery promise is made from the earlier research's team-based estimates. The first implementation checkpoints provide actual task throughput, access constraints and defect rates. Reforecast from completed evidence, preserve scope priorities, and distinguish hands-on effort from external waiting time.

## 12. Historical initial publication checkpoint — superseded

Current continuation is `docs/continuity/current-handoff.md`; D09 pauses feature work. The following initial P00/P01 checkpoint is preserved as history, not a current assignment.

**Completed by this planning task:** brief/source review; bounded existing-estate metadata inspection; current HDE/service and colocated Postgres identification; new Drive planning/research/canon/working structure; separate application Notion control/register; governing plan and canon index; seeded work/decision/dependency/risk records and continuity state.

**Not completed:** app repository selection/creation, reuse audit of executable behavior, development, actual infrastructure configuration, database connections, HDE live acceptance, production tests or release. Metadata shows the engine deployment reported SUCCESS, not that the engine is finished.

**Next ready action: P01.1 — bounded reuse and ownership assessment, assigned to App Builder 1.** Inspect the most relevant owned app code/configuration and record retain/configure/modify/replace/retire-later dispositions. Preserve `glow-hdengine-v2`, its current database and shared resources. Then establish the application repo, move implementation authority through the recorded handoff, and continue into contracts and fixture-backed development. App Builder 1 proceeds under D08 without a new blanket plan-approval request and reports evidence and progress to App Planner 1. The original planning-only checkpoint is complete; this document update prepares the authorized new implementation session and does not claim that it has already run.

### Source and evidence ledger

- [Owner implementation brief](../planning/sources/2026-09-23-original-brief.md): primary sequencing, documentation, autonomy and planning-only instructions. Owner's 23 September clarification adds optional reuse of GitHub/Railway structures and priority preservation of HDE/database.
- [Glow mobile dating implementation research](../planning/sources/2026-09-23-original-research.md): dated comparison, product requirements and linked official/source-code evidence. Its whole-build HDE-completion dependency is superseded by this plan; historical cost/version observations are rechecked when used.
- Supplied **Reference — Glow Development Philosophy** and **Reference — Technical Writing Best Practices**: documentation/engineering discipline, not imported HDE process authority.
- Supplied **Canon — HDE CLI/API/Vendor Reference**, architecture/infrastructure sources, and [HDE HTTP reader source at inspected commit](https://github.com/amthorn78/glow-hdengine-v2/blob/a63bf801665fbc19839fc013fcdb05386a1b0d09/adapter/http_reader.py): bounded engine integration evidence. This plan is not an audit of every attached HDE PF document.
- GitHub owner repository search and Railway projects/services/config/deployment reads on 23 September 2026: identities in section 3. Config-variable values and live SQL were not read.
- [Expo project setup](https://docs.expo.dev/get-started/create-a-project/), [django-allauth headless](https://docs.allauth.org/en/latest/headless/index.html), [Stream before-message-send behavior](https://getstream.io/chat/docs/node/before-message-send-webhook/): official component references checked during planning. Revalidate the exact selected release behavior in implementation.
- [Apple App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/), [Google Play policy center](https://play.google.com/about/developer-content-policy/), [Railway documentation](https://docs.railway.com/), [Cloudflare Images](https://developers.cloudflare.com/images/), [RevenueCat documentation](https://www.revenuecat.com/docs/): authoritative recheck destinations; current policy/build/plan applicability is established in the owning implementation phase, not assumed from this static plan.

**Revision history:** 1.0 — initial governing plan; records the database-last requirement, unfinished HDE boundary, optional legacy reuse, protected engine/database, separate canon and lightweight operational model. Subsequent changes record reason, affected tasks, source/contract impact and authority in the current canonical home.

1.1 — records owner authorization D08, App Planner 1/App Builder 1 roles, effect-based HDE protection and progress-reporting responsibility; removes redundant application-only write/provisioning/production-connection permission gates while retaining phase prerequisites and the protected-engine exception.


1.2 — P01.2 publishes the plan into the established private application repository. The initial 1.1 baseline is preserved; the repository authority note distinguishes historical planning statements from current execution state.

1.3 — records Nathan’s same-Railway-project correction and newer same-logical-database/clean-app-data direction from Implementation Control; replaces separate-project/database defaults with app schema/role ownership pending A02 audit. Records the separately scoped AP1-DBA-001 read-only exception. D08 protected-resource effects and P11 runtime/migration sequencing remain unchanged.

1.4 — records D09, repository-only Markdown authority and Claude manager transition; incorporates completed dated database audit without authorizing integration.

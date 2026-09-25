# Glow dating app — full Claude Code manager handoff

Prepared by App Planner 1 for Nathan Amthor, 24 September 2026. Repository: private [`amthorn78/glow-dating-app`](https://github.com/amthorn78/glow-dating-app), default branch `main`. The [publication receipt](migration-publication.md) supplies the verified migration merge, tree and check identities without making this document embed its own future commit hash. Verify current remote state before using the packet. This brief, the initiation prompt and all required documentation are repository Markdown.

**Status, 25 September 2026:** the first assignment this packet describes, the review and the bounded Claude setup optimization, is complete as M02 (merged through PR18). Feature work is still paused. The next step is a manager proposal on whether to resume P06.1. Current routing is in the [current handoff](current-handoff.md). The facts below about Stream and the owner inputs still apply.

## Objective, current phase and limits

Build an iOS/Android dating app around Glow-owned accounts, profiles, reciprocal eligibility, recommendations, discovery, likes, mutual matches, safety and one-to-one chat. Consume supported Glow HD Engine results when ready; HDE owns chart calculation, interpretation and engine data. The app must not become a second HDE. WordPress is a later operator/policy/support surface with a narrow plugin calling the dating API, not another dating backend. One monorepo can hold mobile, API, contracts, documentation and that future plugin; deployments remain separate components.

Nathan paused new features to move implementation from ChatGPT web to Claude Code. **The receiving session is the manager. Its first assignment is repository review and bounded Claude setup/workflow optimization.** P06 chat work is not the first assignment. No external prompt libraries or HDE workflow machinery are imported as governing instructions. Use code, repository Markdown and Notion, with visible decisions and evidence.

| Phase | Verified status and delivered scope | Remaining limit |
|---|---|---|
| P00/P01 | Planning/control, reuse assessment, private repo, PF transfer, pinned mobile/API foundations and CI | Original Drive setup is historical; no ongoing dependency |
| P02 | Production-shape contracts/state machines, generated validators, domain/provider seams, 32 provisional app models and two unapplied migrations | Static definitions and fixtures; not a database schema deployed to production |
| P03 | Guarded container/runtime, offline configuration validation, retries, redacted telemetry, disabled webhook verifier and runbooks | Staging/production refused; readiness 503; no app deployment |
| P04 | Account/onboarding, adult/consent/private birth, profiles/preferences/visibility, media lifecycles | Synthetic in-memory adapters; no real auth, durable media or device proof |
| P05 | Reciprocal eligibility, recommendations/discovery, likes/matches/unmatch/block, replay/freshness guards | Fixture concurrency and logical events only; contact sending always denied |
| P06 | Planned: provider permission/economics proof, chat and notifications | No Stream SDK/account/token route/live connection established |
| P07/P08 | Planned: safety, WordPress operations, support, privacy lifecycle, conditional billing | Product/operating policies and staff auth unresolved; billing disabled |
| P09/P10 | Planned: hardening, native/release preparation and pre-integration proof | Known dependency advisories and device/accessibility/release checks remain |
| P11/P12 | Planned: final database/live integration, acceptance and handoff | DB01–DB13, PV01–PV08, PR01, N01, R01 not proven by fixtures |

The last feature baseline is PR14, merged `ea394543533e99f611158b9026a2bd01de8d09b3`; tree `b1676a034b416bf459daf41405e3b12b5d782f6e`, equal to reviewed candidate `ea73034b63a13cc6df6d07801d397f926136c737`. [AB1-R012](history/AB1-R012.md) preserves closure and failed-run history. [Main CI 35993588859](https://github.com/amthorn78/glow-dating-app/actions/runs/35993588859) passed four jobs with 250 API tests, 38 Python contract methods, 516 mobile tests, 373 JavaScript contract cases and 83 rendered browser cases, plus exports/smoke/container checks. Counts overlap. One initial PR browser failure had an unknown root cause; an unchanged-head rerun and separate main run passed. Do not relabel it as a proven infrastructure failure. The migration changes documentation/instructions/CI only; its own evidence is in the publication receipt.

No real users or legacy-user information are needed. No database, HDE/provider call, Railway deployment or account purchase is implied by the build. The API has no real login/session/token endpoint. Browser render tests are development harnesses, not a consumer web product; JS exports are not signed native builds. A large fixture suite proves only its tested substitutions and invariants.

## Codebase overview and flows

Paths below are repository-relative. Read the actual code before selecting an implementation change.

| Path | Responsibility / important entry points |
|---|---|
| `apps/mobile/package.json`, `app.config.ts`, `scripts/development.mjs` | Expo 57 / React Native 0.86 / React 19.2 pins, Router entry, guarded development configuration and commands |
| `apps/mobile/src/app/_layout.tsx`, route files under `src/app/` | Fixture-only shell and guarded navigation: account/verify/recovery/birth, profile/preferences/media, recommended/explore, matches/match/restricted |
| `apps/mobile/src/onboarding/`, `profiles/`, `media/` | Feature contexts/stores, policy and in-memory fixture adapters; safe draft/session/private-projection handling |
| `apps/mobile/src/eligibility/facts.ts`, `src/discovery/`, `src/interactions/` | Shared raw facts, discovery queue/continuation freshness, directional actions, canonical matches, immutable receipts and current projection guards |
| `apps/mobile/src/config/development.ts`, `src/hooks/use-recommendations.ts`, `src/data/` | Fixture selection and optional development HTTP presentation client; the full P04/P05 journey otherwise uses local adapters |
| `apps/mobile/rendered/`, `playwright.config.ts` | Chromium rendering of native screens through React Native Web; fixture journeys/layout coverage |
| `services/api/glow_api/settings.py`, `configuration.py`, `configuration_profiles.py` | Fail-closed fixture settings and a separate offline future-profile validator; Django dummy database |
| `services/api/glow_api/urls.py`, `views.py` | Only `GET /health/live`, `/health/ready`, `/api/v1/development/recommendations`; synthetic unauthenticated GET data, no production mutations |
| `services/api/glow_api/devserver.py`, `runtime.py`, `wsgi.py`, root `Dockerfile` | Loopback development WSGI and guarded Gunicorn artifact; no startup migrations or database calls |
| `services/api/glow_domain/eligibility_facts.py`, `eligibility.py`, `trusted_eligibility.py`, `pair_evaluation.py` | Trusted ordered-pair eligibility before provider work; versions/freshness and retained batch rechecks |
| `services/api/glow_domain/identity.py`, `ports.py`, `compatibility.py`, `provider_contracts.py`, `provider_fixtures.py` | Separate app/chart IDs and opaque account-to-chart mapping, provisional compatibility ports and synthetic providers |
| `services/api/glow_domain/discovery.py`, `discovery_fixtures.py`, `interactions.py`, `interaction_fixtures.py` | Internal fixture services for queues, reciprocal likes, idempotent receipts, matches/unmatch/block and bounded logical events. No HTTP mutation routes |
| `services/api/glow_domain/webhooks.py`, `worker_execution.py` | Pure disabled-by-default Stream signature verification and bounded worker execution interfaces; durable admission always refuses; no running Celery/broker |
| `services/api/glow_persistence/models.py`, `migrations/`, `static_check.py`, `static_settings.py` | 32 app model definitions, two unapplied migrations and database-independent consistency checks. Auth/contenttype definitions load only for static work |
| `packages/contracts/production/`, `development/`, `fixtures/`, `runtime.py`, `scripts/` | Closed JSON schemas/state machines, distinct production/development contracts, shared conformance cases and generated mobile validators/types. Production contract declarations do not create HTTP routes |
| `services/api/tests/`, `scripts/smoke.mjs`, `scripts/container_smoke.py` | Domain/API/static checks, actual API-to-mobile HTTP smoke and isolated built-container checks |
| `.github/workflows/foundation.yml`, `scripts/change_scope.py` | Change classification, conditional application jobs and an always-reported gate |

The ordinary mobile fixture flow is route → store → fixture adapter → shared policy/contracts → authorized presentation. The optional HTTP smoke is mobile client → synthetic GET API → fixture response validation. Internal Python discovery is trusted facts → reciprocal eligibility → opaque chart mappings → synthetic compatibility provider → final freshness recheck → authorized batch. Interactions consume a current batch and derive the actor from a trusted fixture session, stage receipt/state/events, then publish current projections after authority checks. They never grant chat sending.

“Chart mapping” means linking an app account to a separately identified HDE chart and checking that association's current version. `ChartMappingRepository`, `EngineIdentity` and compatibility snapshots are boundary bookkeeping, not chart generation, ephemeris, HD math or a competing scoring engine. Final HDE interface/rights/throughput remain A01/A07. Keep it opaque and adapt to the supported engine contract rather than copying internals.

### Database/infrastructure disposition

Future app services belong to Railway project `ample-illumination`, `ce01529f-679f-4f52-a979-23113299a59b`. The [23 September audit](../planning/database-audit-2026-09-23.md) and [catalog/model map](../planning/database-catalog-2026-09-23.md) observed HDE and the legacy backend using the same logical database `railway` and privileged `postgres` role. The direction is a clean app-owned schema with separate restricted runtime/migration roles in that logical database. Do not reuse the privileged runtime credential. None of the 32 provisional models had an approved reusable physical legacy relation; retain useful concepts/structure only where the audit justifies it. The 32-model count is not a mandate to create 32 tables unchanged.

Protect all HDE objects including `hde` and `public.hde_body_graphs_current`; `public` is not wholly disposable. Legacy retirement is separate work with consumer/backup/ownership review. App schema creation still affects shared capacity, locks and recovery and is not harmless merely because HDE tables are unchanged. A02 remains open for implemented isolation and acceptance. P11 owns connections/migrations; the old audit exception does not authorize a new connection in this transition. Shared HDE/legacy/Postgres/Redis identities and restrictions are in [resource ownership](../operations/resource-ownership.md).

## Documentation and development workflow

[The documentation guide](../README.md) defines naming and pruning. `docs/planning/` retains plans/briefs/source snapshots; `docs/ephemeral/` holds disposable single-use prompts only after enduring context is persisted; `docs/pf-canon/` retains the separate application PF00/PF01. ADRs, architecture, operations, testing and continuity retain their existing homes. All documentation is `.md`; JSON schemas/fixtures, locks, workflows and environment templates are machine artifacts, not alternative prose authorities.

Notion [Implementation Control](https://app.notion.com/p/3e44590a05eb8118bf02f0dc0c3ea57c) and [Work Register](https://app.notion.com/p/71b769915b5b4e00830663770bc95f7e) coordinate task state/blockers/evidence links. Repository Markdown contains everything needed to understand and complete an assignment. Capture a unique Notion/chat decision here before an implementer depends on it. No Drive access or update is required. Historical source copies are marked as superseded where relevant.

Follow the [manager workflow](../planning/manager-workflow.md). It is a **manual relay** (Nathan, 24 September 2026):

- The manager gives Nathan prompts for implementers. Nathan runs each implementation or review session himself and relays its findings. The manager follows up as needed, and Nathan reinitiates managers manually.
- The manager never starts implementation or review work itself (no subagents or remote-session tools for that work). Those sessions may use any tools, subagents or wake-ups they need.
- The sequence: inspect baseline → persist bounded assignment → write the prompt → Nathan runs the session and relays the report → verify against the pushed branch → appropriate checks/review → checked merge → actual-main verification → repository continuity and Notion sync.

Give fresh sessions complete prompts. Preserve unrelated work, and give concurrent writers separate session branches. The manager owns coordination and decisions rather than delegating an unbounded whole project.

[Local setup](../operations/local-development.md) provides pinned install/run/check commands. Claude sessions run in the dedicated `Glow app` cloud environment. Its Setup script, `scripts/bootstrap-toolchain.sh`, installs Node 24.19.0, npm 11.9.0 and CPython 3.12.14 from hash-verified downloads and links them into `$HOME/.local/bin`; see [Claude Code cloud sessions](../operations/local-development.md#claude-code-cloud-sessions). Root and mobile `CLAUDE.md` import applicable `AGENTS.md`; the first manager should review and optimize these minimal entry points, not create a second instruction hierarchy. Official [Claude memory documentation](https://code.claude.com/docs/en/memory) describes imports; confirm the installed Claude version's behavior locally.

`AGENTS.md` governs AI review selection. Since Nathan's 24 September direction, any change made only of Markdown files skips application jobs and review work. That includes READMEs, runbooks, instructions, planning, canon, handoffs and prompts. Paths under a `.claude/` directory are the exception and stay full scope. If an external Codex trigger starts a reviewer, it must classify and exit. Scripts, code, mixed changes, workflow/configuration and `.env.example` changes receive full checks and reviews. `Foundation` retains API checks, Mobile checks, API mobile smoke and API artifact checks as stable job names; a lightweight scope job and Foundation gate run for all changes. Missing comparisons fail closed. Classification runs trusted policy in isolated Python before candidate code: PR base for pull requests, preceding main for main pushes, fetched main for feature pushes. First adoption without a trusted policy runs full checks. Candidate scope tests run in the separate full-scope API job. See [CI/review policy](../operations/ci-and-branch-policy.md) for exact behavior and the external-trigger limitation. The workflow YAML itself remains candidate-controlled, so this routing is not immutable enforcement: the manager must independently classify and inspect workflow and classification-policy changes plus actual job steps/results before accepting full checks. Preserve the documented private-account branch-enforcement limitation; procedural checking is not platform protection.

## Environment-variable inventory

**Scope verified from source:** `configuration_profiles.py`/`configuration.py`, `runtime.py`, `settings.py`, `manage.py`/`wsgi.py`/`devserver.py`, mobile `app.config.ts`/development wrapper/config/context, Playwright, smoke scripts, Dockerfile and Foundation workflow. This inventories project-consumed/guarded names and explicit tooling variables, not every variable exposed by an OS or GitHub runner. No remote secret values were read. “Deployment” below describes blocked future requirements, not a deployable configuration.

Safe templates: [`services/api/.env.example`](../../services/api/.env.example) and [`apps/mobile/.env.example`](../../apps/mobile/.env.example). Only harmless fixture values are populated. Python does not auto-load dotenv; Expo uses its tooling and development wrapper. Never copy a broad shell/production environment into both processes: mobile-only `GLOW_*` names are unknown to the API and rejected. Secrets, even empty reserved slots, must be absent from the fixture API process. No deployment template with guessed keys is supplied.

### Current process/profile names

All names in this table are **nonsecret**. The “where set” column identifies source defaults, safe local templates, scripts or proposed future service-local configuration; it does not claim remote provisioning.

| Exact name | Purpose / current behavior | Where set | Local / CI / deployment requirement |
|---|---|---|---|
| `GLOW_ENV` | Environment enum, no default | API example or shell; CI API test env; smoke child | Required API local/CI `development` or `test`; staging/production refused |
| `GLOW_SERVICE_ROLE` | API/worker selector | Profile default `api` | Optional local/CI; worker runtime unavailable |
| `GLOW_DEBUG` | Strict boolean; true rejects | Profile default false | Optional local/CI; never enable debug |
| `GLOW_SECURE_TRANSPORT` | Transport definition, no proxy implementation | Profile default false locally, true in future definition | Optional local/CI; future secure transport required |
| `GLOW_ALLOWED_HOSTS` | Exact comma-separated host allowlist | Loopback defaults; adds `testserver` in test | Optional local/CI; future service domain list required; cannot change bind address |
| `GLOW_ALLOWED_ORIGINS` | Exact origins definition, no CORS middleware | Profile default empty | Optional local/CI; future origins depend on staff/browser integration |
| `GLOW_PROVIDER_TIMEOUT_SECONDS` | Integer 1–30, watchdog/planning timeout | Profile default 10 | Optional local/CI; future adapter timeout not wired |
| `GLOW_RETRY_ATTEMPTS` | Integer 1–3 total attempts | Profile default 3 | Optional local/CI; no queue activated |
| `GLOW_RETRY_BUDGET_SECONDS` | Integer 1–120, at least timeout × attempts | Profile default 45 | Optional local/CI; offline definition only |
| `GLOW_PERSISTENCE_ADAPTER` | `disabled`; future `postgresql` definition | Profile defaults | Disabled local/CI; P11 runtime not implemented |
| `GLOW_BROKER_ADAPTER` | `disabled`; future `redis` definition | Profile default disabled | Disabled local/CI; future worker needs isolated broker |
| `GLOW_COMPATIBILITY_PROVIDER` | Fixture selector / future `hde` definition | API example; default fixture locally | Optional fixture local/CI; live HDE unavailable |
| `GLOW_FEATURE_COMPATIBILITY` | Enable compatibility fixture | Profile default true locally | Must remain true for served fixture API; future adapter unresolved |
| `GLOW_FEATURE_MEDIA` | Media capability flag | Profile default false | Optional disabled local/CI; enabled future definition only |
| `GLOW_FEATURE_MAIL` | Mail capability flag | Profile default false | Optional disabled local/CI; enabled future definition only |
| `GLOW_FEATURE_CHAT` | Chat capability flag | Profile default false | Optional disabled local/CI; enabling served chat refuses |
| `GLOW_FEATURE_PUSH` | Push capability flag | Profile default false | Optional disabled local/CI; enabled future definition only |
| `GLOW_FEATURE_MONITORING` | External monitoring capability | Profile default false | Optional disabled; external adapter unavailable |
| `GLOW_FEATURE_BILLING` | Billing capability | Profile default false | Enabling rejected in all profiles pending A06 |
| `GLOW_MEDIA_ADAPTER` | Media definition label | Default disabled | Local/CI disabled; future `cloudflare` not installed |
| `GLOW_MAIL_ADAPTER` | Mail definition label | Default disabled | Local/CI disabled; future `smtp` transport unimplemented |
| `GLOW_CHAT_ADAPTER` | Chat definition label | Default disabled | Local/CI disabled; future `stream` not installed |
| `GLOW_PUSH_ADAPTER` | Push definition label | Default disabled | Local/CI disabled; future `expo` unimplemented |
| `GLOW_MONITORING_ADAPTER` | Monitoring definition label | Default disabled | External provider not selected |
| `GLOW_BILLING_ADAPTER` | Billing definition label | Default disabled | `revenuecat` planned only; billing forbidden |
| `GLOW_RAILWAY_PROJECT_ID` | Future canonical project UUID | Offline definitions/tests only | Forbidden local runtime; future owned manifest required |
| `GLOW_RAILWAY_ENVIRONMENT_ID` | Future app environment UUID | Offline definitions/tests only | Forbidden local runtime; app target unprovisioned |
| `GLOW_RAILWAY_SERVICE_ID` | Future app API/worker UUID | Offline definitions/tests only | Forbidden local runtime; protected service IDs rejected |
| `PORT` | Gunicorn artifact loopback TCP port | Default 8000; container smoke sets 8123 | Optional local/artifact CI; 1024–65535 only; no public bind |
| `DJANGO_SETTINGS_MODULE` | Django module selection | Entry points `glow_api.settings`; static checker selects `glow_persistence.static_settings` | Script-managed local/CI; artifact rejects alternate settings |
| `GLOW_APP_ENV` | Mobile build guard | Mobile example; wrapper defaults development | Required by app config, supplied by wrapper local/CI; release refused |
| `EXPO_PUBLIC_GLOW_MODE` | Public fixture selector | Mobile example; wrapper defaults fixture | Required mobile config/runtime local/CI; client-safe, never secret |
| `EXPO_PUBLIC_GLOW_API_BASE_URL` | Optional development HTTP origin | Commented mobile example / local Expo env | Optional local; unset for bundled fixtures; no live deployment meaning |
| `EAS_BUILD_PROFILE` | Mobile build guard | EAS tooling if present | Unset/development only; preview/production rejected |
| `GLOW_RENDERED_TESTS` | Enable internal web rendering target | Playwright child sets `1` | Browser tests only; absent in ordinary mobile/API runtime |
| `EXPO_PUBLIC_PROJECT_ROOT` | Expo-injected config directory | Expo SDK during rendered tests | Accepted only with rendered flag and exact directory match; not a user credential |

### Reserved secret slots — not current environment loaders

Every name below is **secret** in its intended future role. None is required for local fixture work or CI. **Do not set any of these environment variables now**, including empty strings: the current API rejects their presence. The offline validator takes a `secret_names` set containing names only; it never reads secret values. Future provisioning belongs in an approved secret store or service-local secure environment, separate by environment and role. These slots do not yet define a concrete credential format or provider wire contract.

| Exact name | Purpose | Future provisioning / requirement |
|---|---|---|
| `GLOW_DJANGO_SECRET_KEY` | Framework signing material | API secret store; future staging/production auth |
| `GLOW_DATABASE_RUNTIME_SECRET` | Restricted app runtime credential/reference | API/worker store; P11 schema/role verification required |
| `GLOW_DATABASE_MIGRATION_SECRET` | Separate migration credential/reference | P11 migration job only; not consumed by current validator/runtime |
| `GLOW_BROKER_SECRET` | Isolated app broker access | API/worker store when future redis definition used |
| `GLOW_HDE_API_TOKEN` | Supported app-to-HDE credential | Server store after A01/A07; never copy protected HDE service secrets |
| `GLOW_MEDIA_API_TOKEN` | Scoped media service credential | API/worker store after media provider/permissions proof |
| `GLOW_MAIL_CREDENTIAL` | Mail transport credential | Server store after provider/domain selection |
| `GLOW_CHAT_API_SECRET` | Stream server signing/verification slot | API/worker store after P06 permission/account proof; never mobile |
| `GLOW_PUSH_ACCESS_TOKEN` | Expo push access slot | Worker store after push account/security choice and native delivery proof |
| `GLOW_MONITORING_TOKEN` | External monitoring credential | Not required while disabled; provider unresolved |
| `GLOW_BILLING_WEBHOOK_SECRET` | Billing event-verification slot | Forbidden until A06 and provider verification decisions |

### Recognized forbidden connection names

These names are **denylist entries**, not supported connections. They must be absent locally and in current CI. There is no valid current deployment value. Where found in tests, only synthetic sentinels are used. URLs and credentials are potentially secret; host/port/database/user identifiers are connection metadata that can still be sensitive.

| Exact names | Intended meaning / secrecy | Current setting and requirement |
|---|---|---|
| `DATABASE_URL`, `GLOW_DATABASE_URL`, `DATABASE_PRIVATE_URL` | Credential-bearing database URLs; secret | Never set; connection refused by presence |
| `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER` | PostgreSQL connection metadata; not authenticators | Never set in fixture process |
| `PGPASSWORD` | PostgreSQL password; secret | Never set |
| `REDIS_URL`, `REDIS_PRIVATE_URL`, `BROKER_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`, `GLOW_BROKER_URL` | Broker/result endpoints potentially containing credentials; secret | Never set; no broker/Celery implementation |
| `HDE_API_URL`, `HD_API_BASE_URL`, `GLOW_HDE_API_URL` | Legacy/current HDE endpoint metadata; no secret value assumed | Never set; no live adapter |
| `HDE_API_TOKEN`, `HD_API_KEY`, `GEO_API_KEY`, `GLOW_HDE_API_TOKEN` | HDE/geodata credentials; secret | Never set; last name also reserved above |

Every `GUNICORN_*` name is rejected by the artifact entrypoint, unknown `GLOW_*` names by the API, and unapproved `EXPO_PUBLIC_*` names by mobile config/API. `EXPO_PUBLIC_STREAM_SECRET`, `EXPO_PUBLIC_HDE_API_TOKEN` and `EXPO_PUBLIC_UNKNOWN` occur only as negative-test examples; they are never supported configuration. No code reads a Stream API key, app ID, region, channel type, token URL or webhook URL. Since 24 September the `Glow app` cloud environment provides `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` for Nathan's development Stream application; see [environment inventory](../operations/environment-inventory.md#stream-development-application-getstreamio). Wiring them into a loader is P06.1 work.

### Tooling variables explicitly used by the repository

All are nonsecret except that the GitHub token is an ephemeral platform credential. None is a provider credential.

| Exact name | Purpose / where set | Local / CI / deployment requirement |
|---|---|---|
| `GLOW_SMOKE_PYTHON` | Smoke harness interpreter path; defaults to `services/api/.venv/bin/python`; removed before API spawn | Optional locally; CI sets `python`; not an API/deployment variable |
| `PYTHONPATH` | Contract test import path | Test shell/CI uses `.` from API directory; not deployment config |
| `EXPO_OFFLINE` | Installed-SDK/offline Expo checks | CI/mobile checks and Playwright set `1`; optional other local work |
| `CI` | Noninteractive Expo test mode; GitHub runner and Playwright child `1` | Local browser harness/CI only |
| `BROWSER` | Suppress browser auto-open; Playwright child `none` | Browser harness only |
| `PYTHONDONTWRITEBYTECODE` | Disable Python bytecode writes; Dockerfile `1` | Artifact only |
| `PYTHONUNBUFFERED` | Unbuffered process logs; Dockerfile `1` | Artifact only |
| `PIP_DISABLE_PIP_VERSION_CHECK` | Suppress pip version check; Dockerfile `1` | Image build/runtime tooling |
| `TZ` | UTC process timezone; Dockerfile `UTC` | Artifact only |
| `COMPARE_BASE`, `COMPARE_HEAD`, `IS_PULL_REQUEST` | Immutable comparison IDs and diff mode; Foundation scope-step environment from GitHub event | CI only; classifier CLI uses equivalent arguments locally |
| `GITHUB_OUTPUT` | Runner-owned step-output file; GitHub runner, used by classifier | CI only; never a secret/value dump target |
| `RESULTS` | Serialized job conclusions for Foundation gate; Workflow `toJSON(needs)` | CI only; no application input |
| `RUNNER_TEMP` | Runner-owned temporary directory; stores the extracted trusted classifier | GitHub CI only; never candidate-controlled storage |
| `GITHUB_REF` | Runner event ref; selects main-push versus feature-push policy source | GitHub CI only; comparisons still use immutable SHAs |

The workflow's platform `github.token` is handled by checkout with `persist-credentials: false`, read-only contents permission and no exposure to application code. No project API secret is configured or needed in these jobs. OS/tool-inherited variables are not an approved deployment secret mechanism.

### Claude cloud environments

- **HDE-shared environment.** App Manager 1 ran in the Claude cloud environment shared with HDE work. It injects `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` and `PORT` (names observed on 24 September 2026; values never read). The fixture API correctly refuses to start there with `inherited_connection`.
- **Dedicated environment rule.** Every Glow app manager, implementation and review session runs in the dedicated `Glow app` environment. It has no HDE variables, provides only the Stream development variables, and uses `scripts/bootstrap-toolchain.sh` as its Setup script. Its settings are in the [environment inventory](../operations/environment-inventory.md#claude-cloud-environment-glow-app-nathans-settings-24-september-2026). Never copy HDE variables into it. A session that finds HDE names present tells Nathan, never reads the values, and runs app commands only in a clean process environment ([local setup](../operations/local-development.md#claude-code-cloud-sessions)).
- **Residual risk.** Any command in a session can read every variable of that session's environment. An environment separates projects; it is not a boundary between commands. The dedicated environment limits app sessions' exposure to the Stream development values, which are recorded by name only where secret.
- **Bootstrap script inputs.** The script itself references only `HOME` and `PATH` and prints no variable values. The tools it runs read their own standard settings, such as curl's proxy and CA-bundle variables, `TMPDIR`, compiler variables and `npm_config_*`. It reads no application, provider or database configuration.

## Stream Chat setup — current facts and future proof

### What exists now

- `services/api/glow_api/configuration_profiles.py` has `GLOW_FEATURE_CHAT`, `GLOW_CHAT_ADAPTER` and the future `GLOW_CHAT_API_SECRET` slot. Served chat is disabled. No Stream dependency is present in the committed mobile/API locks.
- `services/api/glow_domain/webhooks.py` accepts **function arguments**, not environment lookups: `StreamWebhookCredentials(api_key, secret)` and `verify_stream_signature(raw_body, signature, api_key, credentials, enabled=False, content_encoding="identity")`. It checks bounded identity-encoded bytes, API-key equality and HMAC-SHA256. It rejects unsupported compression. It does not establish freshness or replay safety.
- There is no registered callback. `require_durable_webhook_admission()` refuses even a valid signature because durable inbox admission is unavailable. No token issuance, chat account sync, channel creation, SDK connection, push registration or message send is implemented. `contact_decision()` denies send.
- Fixture tests and an installed Stream skill establish neither a valid account, Maker entitlement, pricing, SDK permission behavior nor a working live connection. The earlier proposed Pusher/Ably redesign was canceled; it is not the selected implementation.

### Inputs the live adapter will need

| Input | Classification | Current repo name / status |
|---|---|---|
| Stream application API key | Client-safe identifier; not sufficient to authenticate a user | Development app: `STREAM_API_KEY=qdstwyevnyea` in the `Glow app` environment; not yet read by code; pure webhook argument is `api_key` |
| Stream API secret | Server-only signing/administration secret | Development app: `STREAM_API_SECRET` in the `Glow app` environment (value never recorded); maps to the future slot `GLOW_CHAT_API_SECRET`; pure webhook argument `secret`; no live loader |
| Per-user Stream token | Sensitive bearer credential delivered to that authenticated user's client | No endpoint/storage/refresh path exists; never a bundled environment value |
| Stream app identity, region, environment and account plan | Nonsecret operational configuration | Development app `STREAM_APP_ID=1729640` (Nathan, 24 September 2026); region and plan not yet verified |
| Channel type and role/grant configuration | Security policy | A08 proof outstanding; don't copy permissive demo defaults |
| Public HTTPS callback URL and event selection, if used | Endpoint/configuration; signature secret stays server-side | No callback route or URL variable exists; P11 durable inbox required for effects |

Current Stream [backend documentation](https://getstream.io/chat/docs/node/) places token signing on the server with the API secret. The intended app token endpoint must authenticate the app session, derive the Stream user ID from the server-owned app identity, check current account eligibility, apply expiry/refresh/revocation policy and return only the necessary token/client-safe configuration. This is an implementation plan, not existing behavior. Never accept arbitrary client user IDs for token issuance or use developer tokens in the intended permission proof.

App-owned mutual match/block/account state remains authorization authority. [Stream permissions](https://getstream.io/chat/docs/node/chat-permission-policies/) apply to client calls; server calls with valid key/secret are privileged. The proposed proof must demonstrate that direct SDK mutations cannot bypass app permission checks, including stale tokens, channel creation/membership, sends, edits, replies, reactions and attachments. Start text-only and keep unused actions disabled. App-mediated sends and server-controlled channels are candidates that must be verified, not assumed to close all bypasses.

Do not use the before-message-send webhook as the sole match/block gate. Stream's [documented behavior](https://getstream.io/chat/docs/node/before-message-send-webhook/) is to fail open when that hook is unavailable, errors or times out. This is a documented provider limitation, not a behavior tested against a Glow account. If event webhooks are used, verify current signing/header/compression details and implement raw-body validation, app binding, durable deduplication/replay/order controls and bounded retries before enabling effects. The current pure verifier is only part of that boundary.

Use distinct test/staging/production Stream application credentials and identities, with app-owned test users/channels and minimal data. Keep the server secret in the secure server environment, the API key in deliberately reviewed client-safe configuration, and user tokens in appropriate client credential storage. Do not put a server secret under `EXPO_PUBLIC_*`. The current allowlist must be deliberately updated and tested when the chosen public names are implemented; merely adding an `.env` line will fail or do nothing.

### Bounded live-verification sequence — after setup and owner inputs

1. Reconcile P06.1 prerequisites P05.3/P02.1/A04/A08. Confirm the actual Stream account/plan, Maker eligibility if desired, environment ownership/region, limits and budget with Nathan; no free entitlement or price is presumed.
2. Commission a separate sandbox proof using only synthetic users and an explicitly selected Stream test app. Establish secure credential injection and documented exact variable names in that implementation; preserve the main fixture runtime's guard until its replacement has acceptance evidence.
3. Select and pin compatible maintained Python/server and Expo/React Native SDKs based on their official current docs. Implement a bounded server token/permission proof and two authenticated test clients. Show connect, authorized read/text send, disconnect/reconnect and cleanup with redacted evidence.
4. Test unauthorized pair/user/channel access and direct client mutation attempts; then block, unmatch, suspend/delete, expired/revoked/stale token, reconnect, concurrent send/revoke and provider outage. Verify history/read policy as well as sending. A screen disappearing is not provider-side revocation proof.
5. If testing callbacks, use a narrowly scoped HTTPS test endpoint and exercise invalid signature/body/key/compression, duplicates, ordering and timeout. Do not connect the production database to make the sandbox proof work. Separate what can be measured before P11 from durable transaction/race/inbox/outbox guarantees requiring P11.
6. Record actual plan limits, MAU/concurrent connections/message/storage/bandwidth assumptions and observed requests/cost indicators. Verify push ownership/deduplication separately; don't activate both Stream and Expo send paths for the same event by accident. Reconcile native signing/device proof later.
7. Retire sandbox users/channels/endpoints as explicitly scoped, preserve redacted evidence in Markdown and report unresolved failures. No live success is claimed until these checks have actually run.

## Prioritized inputs Nathan must supply

| Priority | Input / decision | Needed before |
|---|---|---|
| 1 | **Provided:** Claude Code access with private-repository Git access. **Owner setting:** the dedicated `Glow app` cloud environment (no HDE variables, network allowlist, `scripts/bootstrap-toolchain.sh` as Setup script, re-pasted whenever that file changes); see the [environment inventory](../operations/environment-inventory.md) | Every app session. No provider key is needed for fixture setup |
| 2 | Stream account/app administration access, chosen test application/region, verified plan or Maker acceptance, budget/limits | P06.1 live sandbox proof. Supply API key/secret through secure local/server configuration after exact loader names are implemented, not through chat/Notion/PR |
| 3 | Product policy for chat/history after block/unmatch, retention/deletion/moderation owners and approved account/session authorization approach | Permission design and account/lifecycle acceptance (A05/A08) |
| 4 | Supported HDE contract/release, allowed operations/data rights, opaque identity mapping and throughput evidence; separately scoped app credential from the authorized issuer | A01/A07 and eventual live HDE integration; no internal-engine rewrite |
| 5 | App service/environment identities, clean app schema/role ownership, restricted runtime/migration secret provisioning, backup/capacity/restore decisions | A02/P11; protect shared database and HDE effects |
| 6 | Expo/EAS, Apple/Google signing and push account access; privacy-safe notification ownership | Native development builds and push/device proof |
| 7 | Cloudflare media account/access, mail provider/domain, WordPress/admin access, launch geography/preferences, support/moderation/retention owners | P07–P11 as those components are commissioned |
| 8 | Billing/product decision if monetization is desired; release/account enforcement arrangements | A06 and store release; billing remains disabled |

Complete all independent setup work first. Request only the concrete missing input for the next bounded action, explain why it is needed, and never ask Nathan to paste secret values into repository documentation, Notion or conversation.

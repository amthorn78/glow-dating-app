# Environment inventory

This page is the one living home of the environment inventory (DM-03 E2, 25 September 2026). The variable inventory below moved verbatim from the frozen [Claude handoff](../continuity/claude-code-handoff.md) that day. App Planner 1 verified it from source on 24 September 2026, and it has not been re-verified since; its scope line says what was read. It gives exact code names, purpose, local/CI/deployment requirements, provisioning location and secret classification.

Safe local templates: [`services/api/.env.example`](../../services/api/.env.example) and [`apps/mobile/.env.example`](../../apps/mobile/.env.example). See [local setup](local-development.md) for their different loading behavior. The [configuration catalog](configuration.md) retains the detailed validator contract. Future provider slots are not active environment loaders; do not populate them until separately reviewed integration work introduces that behavior.

## Claude cloud environment `Glow app` (Nathan's settings, 24 September 2026)

This is the dedicated environment for every Glow app manager, implementation and review session. A session's environment is fixed when it starts; switching environments requires a new session, and variable changes reach only sessions started afterwards. Any command in any session in this environment can read its variables, so values that are secret are recorded here by name only.

| Setting | Value |
|---|---|
| Network access | Custom, with "Also include default list of common package managers" checked. Allowed domains: `www.python.org`, `docs.expo.dev`, `*.stream-io-api.com`, `getstream.io` |
| Setup script | `scripts/bootstrap-toolchain.sh`, pasted unchanged. Installs Node 24.19.0, npm 11.9.0 and CPython 3.12.14, linked in `$HOME/.local/bin`. Paste again whenever the file changes, not only its pins. See [local setup](local-development.md#claude-code-cloud-sessions). **Current:** Nathan pasted the M02 version (blob `450b3cf`, merged in PR18) on 25 September 2026. App Manager 3 verified it in a new session the same day: the ownership check in the [current handoff](../continuity/current-handoff.md) printed 0 |
| HDE variables | None. `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` and `PORT` belong only to the HDE environment |
| API credentials | TypeSafe, a **Bearer** credential for `api.typesafe.ai`, added by Nathan on 24 September 2026. Anthropic's proxy attaches it to requests for that host, so it is not an environment variable and commands cannot read its value. Any process in any session in this environment can still send authenticated requests to `api.typesafe.ai`, including candidate tests and install scripts. By policy only the manager's advisory reasoning-level scorer uses it; nothing enforces that |

### Stream development application (getstream.io)

| Variable | Value | Classification |
|---|---|---|
| `STREAM_APP_ID` | `1729640` | Nonsecret application identity |
| `STREAM_API_KEY` | `qdstwyevnyea` | Client-safe identifier; not sufficient to authenticate a user |
| `STREAM_API_SECRET` | Held only in the environment settings; never recorded | **Secret.** Server-side signing/administration credential. Never print, copy or log it, and never expose it to mobile code or `EXPO_PUBLIC_*` |

- This is Nathan's **development** Stream application. It is for sandbox testing with synthetic users only. Production needs its own Stream application and secret, stored separately.
- **No application code reads these names.** P06.1's sandbox harness (`proofs/stream-chat/`) reads them on the server side only. The app's loader adopts them in P06.2, as the environment names for the future `GLOW_CHAT_API_SECRET` slot and the Stream API key and app ID.
- The fixture API does not reject `STREAM_*` names, so existing checks are unaffected.
- **When the variables are present** (Nathan, 25 September 2026; OD-28). For each session that calls Stream, Nathan adds the three variables to the `Glow app` environment, starts that one session, then deletes them. A session keeps the environment it started with; sessions started later get none. The prompt tells him when a session needs them. They are present now, for the I1 review. The secret is replaced in Stream's dashboard at P06.1's close.
- Nathan's dashboard lookup of 25 September 2026 recorded the application's region (US East), mode (Development) and plan (Free Chat, $0, not a trial); see the [P06.1 brief](../planning/p06-1-chat-provider-proof.md).
- P06.1-I1 recorded the permission behavior and, with Nathan's permission, changed the application's configuration on 25 September 2026. It disabled guest creation, emptied the client roles' application grants and every role's grants in the default channel types, and added the `glow-match` channel type. The [P06.1 evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md) holds the before and after states and the restore command. Pricing at scale stays unverified until P06.1-I2.

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

Every `GUNICORN_*` name is rejected by the artifact entrypoint, unknown `GLOW_*` names by the API, and unapproved `EXPO_PUBLIC_*` names by mobile config/API. `EXPO_PUBLIC_STREAM_SECRET`, `EXPO_PUBLIC_HDE_API_TOKEN` and `EXPO_PUBLIC_UNKNOWN` occur only as negative-test examples; they are never supported configuration. No code reads a Stream API key, app ID, region, channel type, token URL or webhook URL. Since 24 September the `Glow app` cloud environment provides `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` for Nathan's development Stream application; see [environment inventory](environment-inventory.md#stream-development-application-getstreamio). P06.1's sandbox harness in `proofs/stream-chat/` reads them on the server side only; wiring them into the app's loader belongs to P06.2, after the proof.

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
- **Dedicated environment rule.** Every Glow app manager, implementation and review session runs in the dedicated `Glow app` environment. It has no HDE variables, provides only the Stream development variables, and uses `scripts/bootstrap-toolchain.sh` as its Setup script. Its settings are in the [environment inventory](environment-inventory.md#claude-cloud-environment-glow-app-nathans-settings-24-september-2026). Never copy HDE variables into it. A session that finds HDE names present tells Nathan, never reads the values, and runs app commands only in a clean process environment ([local setup](local-development.md#claude-code-cloud-sessions)).
- **Residual risk.** Any command in a session can read every variable of that session's environment. An environment separates projects; it is not a boundary between commands. The dedicated environment limits app sessions' exposure to the Stream development values, which are recorded by name only where secret.
- **Bootstrap script inputs.** The script itself references only `HOME` and `PATH` and prints no variable values. The tools it runs read their own standard settings, such as curl's proxy and CA-bundle variables, `TMPDIR`, compiler variables and `npm_config_*`. It reads no application, provider or database configuration.

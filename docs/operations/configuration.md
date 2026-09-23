# Configuration definitions and credential catalog

P03 adds a pure offline definition validator in
`services/api/glow_api/configuration_profiles.py`. The served loader remains
`glow_api.configuration.load_configuration`. Only development/test fixture API
startup is implemented. Staging and production always raise the categorized
`runtime_activation_unavailable` error before an adapter or database can load.
`GLOW_ENV` is explicit; there is no environment fallback.

A consistent future definition is **not an available runtime, verified target,
working credential, supported HDE contract, ready service or deployment**. Every
returned profile has `runtime_available=False`. The validator uses no network,
filesystem, ORM, provider SDK or secret loader. Its `secret_names` argument is a
set of known secure-provisioning slot names, not values. Presence checks do not
establish credential validity, entropy, scope, expiry or secure storage. Such
checks and real adapter conformance belong to later activation work.

## Validator and diagnostic contract

`validate_profile(environ, owned_targets=frozenset(), secret_names=frozenset())`
returns immutable `ProfileValidation`: `profile`, `errors`, and
`disabled_capabilities`. `is_valid` means the offline definition is internally
consistent. Invalid definitions return no usable profile. Categories distinguish
missing required inputs, malformed syntax/bounds, contradictory security or
ownership selections, unsupported values, and intentionally disabled capability.
Optional disabled features do not invalidate a development profile. Future
mandatory compatibility/media/mail/chat/push definitions and secret slots cannot
be waived. Billing enablement remains a disabled error under A06. External
monitoring provider selection is still unavailable; local structured telemetry is
independent of that optional feature.

Errors contain only fixed codes and known variable names. Supplied values never
appear in errors. Unknown `GLOW_*` and unapproved `EXPO_PUBLIC_*` names are rejected
without echoing their names. Profiles suppress hosts/origins/target details in
`repr`; secret values are never stored. The runtime loader accepts only the
compatibility fixture capability and API role, even when an offline development
profile describes additional fixture substitutes.

Configuration hosts contain 1–20 unique exact lowercase hostnames/IPs without
wildcards, ports, schemes or suffix matching. Runtime fixture hosts can only be
localhost, IPv4/IPv6 loopback, the Android emulator host alias, and testserver.
Explicit lists are never widened. Defaults retain the original loopback aliases,
with testserver added only to the default test list. Future profiles reject those
fixture aliases. Origins contain at most 20 unique exact HTTPS origins; local
HTTP is allowed only for those loopback/emulator hosts. Paths (including a
trailing slash), credentials, query/fragment, whitespace and invalid ports reject.
An empty origin list grants no browser origins. Origins are preparation data;
no CORS middleware or staff/browser route is enabled in this baseline.

Timeout/retry fields bound planning values and reject a total budget smaller than
`timeout × attempts`. That check is a minimum budget consistency check, not a
hard cancellation or backoff execution proof. The worker execution interface owns
its actual monotonic deadline, delay and cancellation behavior. Configuring these
fields does not load a provider or schedule a task. The fixture WSGI entrypoint
uses the configured timeout as its Gunicorn watchdog; it is not an HTTP-client
request timeout implementation.

## Same-project target ownership

The latest owner direction selects Railway project `ample-illumination`,
`ce01529f-679f-4f52-a979-23113299a59b`, for the app and HDE. Configuration remains
separate by application service and environment. New app environment/service IDs
remain unassigned until verified provisioning. UUIDs in tests are synthetic.

A future `TargetIdentity` includes exact project/environment/service IDs, API or
worker role and staging or production mode. It must match an independently
verified application ownership manifest supplied as `owned_targets`. The validator
does not query Railway and cannot establish provenance of that argument. P11 or
an actual provisioning/preflight operator must acquire and check current platform
metadata; copying untrusted request values into the allowlist defeats that duty.
Known HDE, legacy backend, Postgres and Redis service IDs reject even if incorrectly
included in the allowlist. An unlisted ID still requires positive ownership.
The shared project ID is required; it does not grant access to shared settings,
secret values, databases, volumes or HDE networking. See
[resource ownership](resource-ownership.md) for current metadata and boundaries.
Local served fixture configuration rejects future target identity variables.

## Non-secret variable matrix

`D/T` means development/test; `S/P definition` means offline staging/production
planning only. Owner `App Builder 1` means implementation/configuration preparation,
not an invented production on-call appointment. Account/resource owner remains
Nathan; operating assignments and provider access are resolved under A04/A05.
No current template contains a deployment credential or real application target.

| Names | Purpose and type | Required modes / default | Scope | Owner | Secret | Activation dependency |
|---|---|---|---|---|---|---|
| `GLOW_ENV` | Exact environment enum | All; no default | Process/profile | App Builder 1 | No | S/P runtime always unavailable in P03 |
| `GLOW_SERVICE_ROLE` | `api` or `worker` | Default API; worker only offline | Service/profile | App Builder 1 | No | Real worker, broker and P11 durability |
| `GLOW_DEBUG` | Exact `true`/`false`; true rejected | Default false | Service/profile | App Builder 1 | No | No debug activation path |
| `GLOW_SECURE_TRANSPORT` | Exact boolean | Future true required; D/T false | Profile | App Builder 1 | No | Future transport/proxy verification |
| `GLOW_ALLOWED_HOSTS` | Comma-separated exact host allowlist | D/T loopback default; S/P required | Service/environment | App Builder 1 | No | Future verified domain/network; does not change bind address |
| `GLOW_ALLOWED_ORIGINS` | Comma-separated exact origin allowlist | Optional; empty | Profile | App Builder 1 | No | Future browser/staff integration and CORS implementation |
| `GLOW_PROVIDER_TIMEOUT_SECONDS` | Integer 1–30 | Default 10 | Service/profile | App Builder 1 | No | Adapter transport integration; WSGI watchdog implemented |
| `GLOW_RETRY_ATTEMPTS` | Integer 1–3 total attempts | Default 3 | Profile | App Builder 1 | No | Provider/idempotency contract before runtime wiring |
| `GLOW_RETRY_BUDGET_SECONDS` | Integer 1–120; at least timeout × attempts | Default 45 | Profile | App Builder 1 | No | Worker deadline/backoff and provider evidence |
| `GLOW_PERSISTENCE_ADAPTER` | `disabled` or planned `postgresql` | D/T disabled; S/P postgresql | Profile | App Builder 1 | No | P11; no connection variable allowed now |
| `GLOW_BROKER_ADAPTER` | `disabled` or planned `redis` | D/T disabled; future worker requires redis | Profile | App Builder 1 | No | Isolated app broker and durable outbox; no shared Redis |
| `GLOW_RAILWAY_PROJECT_ID`, `GLOW_RAILWAY_ENVIRONMENT_ID`, `GLOW_RAILWAY_SERVICE_ID` | Exact canonical UUID identity | S/P required; forbidden D/T runtime | Service/environment/profile | App Builder 1 | No | Actual app provisioning and verified ownership manifest |
| `PORT` | Integer 1024–65535, entrypoint validated | Fixture entrypoint default 8000 | Process | App Builder 1 | No | Loopback-only serving; no public route |
| `DJANGO_SETTINGS_MODULE` | Exact supported settings module | Entry points choose `glow_api.settings` | Process | App Builder 1 | No | Alternate settings refused by deployment entrypoint |
| `GLOW_APP_ENV` | Mobile development-only build selection | Mobile development | Mobile build only | App Builder 1 | No | Future native release work; not an API variable |
| `EAS_BUILD_PROFILE` | Mobile build profile | Unset or development only | Mobile build only | App Builder 1 | No | Verified EAS account, signing and release authorization |
| `EXPO_PUBLIC_GLOW_MODE` | Public fixture mode | Mobile fixture only | Public client bundle | App Builder 1 | Public | No production preview activation |
| `EXPO_PUBLIC_GLOW_API_BASE_URL` | Public validated development origin | Mobile optional | Public client bundle | App Builder 1 | Public | Explicit local development reachability only |

The actual mobile `app.config.ts` rejects every other `EXPO_PUBLIC_*` variable.
The API validator uses the same closed public-name allowlist. Provider keys,
privileged credentials and misleadingly renamed secrets cannot be added as public
variables. Known permitted fields are public by definition and must never contain
secrets. The mobile origin parser separately rejects URL credentials/query/path.
Server-only variables are not mobile configuration.

## Feature and adapter matrix

Each feature flag is exactly `true` or `false`. An enabled feature requires a
non-disabled adapter; a disabled feature requires `disabled`. Only development/test
offline definitions may select fixtures. Staging/production reject every fixture
adapter, independent of enablement. Planned choices are definition labels, not
installed SDKs, supported live schemas, purchased accounts or active transports.

| Names | Type / purpose | Required modes | Scope / owner | Secret | Activation dependency |
|---|---|---|---|---|---|
| `GLOW_FEATURE_COMPATIBILITY`, `GLOW_COMPATIBILITY_PROVIDER` | Boolean + disabled/fixture/hde | D/T fixture default; S/P enabled definition | App service; App Builder 1 | No | A01/A07 supported HDE contract, authorized separate credential, P11 |
| `GLOW_FEATURE_MEDIA`, `GLOW_MEDIA_ADAPTER` | Boolean + disabled/fixture/cloudflare | D/T disabled; S/P enabled definition | App API/worker; App Builder 1 | No | Cloudflare account/private delivery/lifecycle proof |
| `GLOW_FEATURE_MAIL`, `GLOW_MAIL_ADAPTER` | Boolean + disabled/fixture/smtp | D/T disabled; S/P enabled definition | App API/worker; App Builder 1 | No | Mail account/domain and maintained transport; smtp is protocol preparation, no provider chosen |
| `GLOW_FEATURE_CHAT`, `GLOW_CHAT_ADAPTER` | Boolean + disabled/fixture/stream | D/T disabled; S/P enabled definition | App API/worker; App Builder 1 | No | A04/A08 permission/cost proof, P06/P11 |
| `GLOW_FEATURE_PUSH`, `GLOW_PUSH_ADAPTER` | Boolean + disabled/fixture/expo | D/T disabled; S/P enabled definition | App worker; App Builder 1 | No | Native identities/token lifecycle, account and receipts proof |
| `GLOW_FEATURE_MONITORING`, `GLOW_MONITORING_ADAPTER` | Boolean + disabled/fixture; external adapter unavailable | Disabled default; optional | App service; App Builder 1 | No | Monitoring account/tool decision; local telemetry already separate |
| `GLOW_FEATURE_BILLING`, `GLOW_BILLING_ADAPTER` | Boolean + disabled/fixture/revenuecat; enabling always rejects | Disabled | App API/worker; App Builder 1 | No | A06 owner product decision; provider/store contract and P11 events |

## Secret slot matrix

These are **new future slot names**, not populated environment variables. The
offline validator accepts only their presence through `secret_names`. Supplying
any slot as an environment variable in P03 is rejected by presence, even with an
empty value. This avoids reading inherited credentials while validating future
requirements. Values/references will be provisioned only through secure per-service,
per-environment facilities when the owning adapter and stage exist. No shared
Railway variable or protected HDE secret may be copied.

| Name | Purpose / type | Required modes | Scope | Owner | Secret | Activation dependency |
|---|---|---|---|---|---|---|
| `GLOW_DJANGO_SECRET_KEY` | Maintained framework signing material; opaque secret | S/P slot presence | API/environment | Nathan account; App Builder preparation | Yes | Real auth/security settings and managed rotation |
| `GLOW_DATABASE_RUNTIME_SECRET` | Least-privilege app runtime credential reference | S/P slot presence | API/worker environment | Nathan account; app DB operator unresolved | Yes | P11 verified app target/runtime role |
| `GLOW_DATABASE_MIGRATION_SECRET` | Separate app migration credential reference | Not consumed by P03 validator/runtime | P11 migration job only | Nathan account; app DB operator unresolved | Yes | P11 reviewed ledger/target and migration privileges |
| `GLOW_BROKER_SECRET` | App-only broker credential reference | Future redis definition | App API/worker/environment | Nathan account; App Builder preparation | Yes | Isolated broker, no shared Redis reuse |
| `GLOW_HDE_API_TOKEN` | App-issued supported HDE access credential | Future compatibility definition | App API/worker/environment | Nathan account; HDE issuer | Yes | A01 explicit supported contract and operation rights |
| `GLOW_MEDIA_API_TOKEN` | Scoped media service credential | Future media definition | App API/worker/environment | Nathan account; App Builder preparation | Yes | Cloudflare scope/access and lifecycle proof |
| `GLOW_MAIL_CREDENTIAL` | Opaque mail transport credential | Future mail definition | App API/worker/environment | Nathan account; App Builder preparation | Yes | Mail account/domain/transport decision |
| `GLOW_CHAT_API_SECRET` | Server-side chat signing/verification credential | Future chat definition | App API/worker/environment | Nathan account; App Builder preparation | Yes | A08 provider permission proof; never mobile |
| `GLOW_PUSH_ACCESS_TOKEN` | Server-side Expo push credential slot | Future push definition | App worker/environment | Nathan account; App Builder preparation | Yes | Expo account/security/native delivery proof |
| `GLOW_MONITORING_TOKEN` | Reserved external monitoring credential | Not required while disabled | App service/environment | Nathan account; App Builder preparation | Yes | Monitoring provider decision; no exporter implemented |
| `GLOW_BILLING_WEBHOOK_SECRET` | Reserved provider event-verification secret | Billing remains forbidden | App API/environment | Nathan account; App Builder preparation | Yes | A06 decision + provider verification/replay and P11 |

`FORBIDDEN_CONNECTION_NAMES` is the executable inherited-variable denylist. It
covers database URLs/PostgreSQL connection fields, Redis/broker/Celery values and
legacy/current HDE URL/key/token names. Any presence rejects before value access.
It is defense in depth, not a universal detector of credentials disguised as
arbitrary platform names. Secure deployment must supply an explicit minimal
service environment and verified ownership instead of inheriting shared settings.

## Reproduce and later activation

From `services/api/` with the repository's pinned environment installed:

```bash
python -m unittest tests.test_configuration tests.test_configuration_profiles -v
```

Tests exercise valid offline future definitions, unconditional runtime refusal,
mandatory versus optional capabilities, source-value non-access, typed diagnostics,
protected/missing/incorrect target manifests, secret presence, hosts/origins and
retry bounds. Synthetic fixtures establish neither real resource ownership nor
credential validity. No copyable staging/production environment or fake credentials
are shipped. Before activation, wire maintained real adapters, verify all service
and data ownership, provision scoped secrets securely, prove security/health,
and complete the named P11 deferred cases. Never remove the runtime refusal merely
because offline validation succeeds.

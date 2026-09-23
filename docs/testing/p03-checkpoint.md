# P03 operations and artifact checkpoint

Observed 23 September 2026. Assignment AP1-P03-001 revision 1.0 under GAPP-PF01
P03/D08, with Nathan's same-project correction and the newer database direction
recorded in Implementation Control. P03.1–P03.3 are complete at preparation
scope, subject to the final publication checks recorded by AB1-R004. Later
application capability, activation and P04–P12 acceptance remain unfinished.

## Publication and evidence identity

Starting main **d950ff5a2f74bee6e3a8afd0ddf4aff693d69849**, tree
**03ad1b31cb1b0de3409037ad4ec401be76ea2bc7**. All 122 acquired baseline blobs
matched Git hashes. No open PR at startup; main was rechecked unchanged before
publication. The synthetic local Git baseline is not remote history.

[PR 4](https://github.com/amthorn78/glow-dating-app/pull/4), branch
**app-builder-1/p03-operations-foundation**. Implementation commit
**f36189b611b716fdb1db2998ccd58344537da62c**, tree
**55d711088dacdf8114cf26678a53b52b9eaa7e91**. All 41 initial publication blobs
and the complete tree matched the reviewed local source.

Implementation [PR run 35884841565](https://github.com/amthorn78/glow-dating-app/actions/runs/35884841565)
passed **API checks**, **Mobile checks**, **API mobile smoke** and **API artifact
checks**. Inspected logs confirm the counts below, skipped unused database setup,
development exports and actual image validation. The artifact job built and
validated runner-local image
`sha256:eacf50d024645910168855687ee14534b9f7aa4a3e6396ee593584957298a23a`.
This is an observed image ID, not a registry publication or Railway deployment.

This checkpoint, fresh-session handoff and reconciliation of the newer owner
database direction are a documentation-only follow-up. The containing final
candidate requires its own four passing jobs before merge. Consult PR 4 and
[AB1-R004 in shared reports](https://app.notion.com/p/3e44590a05eb81d58971ee4cd870774f)
for exact final head/run/merge and matching tree, which cannot be embedded
self-referentially in their own commit. Branch protection is disabled; checks,
current base/head and merge-tree equality are verified procedurally.

## Completion criteria and actual boundaries

| Work | Completed preparation | Still unavailable |
|---|---|---|
| P03.1 | Current resource identities, local/test/future environment and service map, same-project ADR, private-network limits, scope/side-effect and cost observations | App Railway environment/service/domain/volume, selected physical schema and roles; no idle resources created |
| P03.2 | Pinned non-root API image, guarded Gunicorn entrypoint, hosted artifact smoke, four-job CI, typed offline configuration with categorized safe refusal, host/public-variable guards, retry executor | Staging/production runtime, true readiness, deployable service, durable worker/broker and native signed artifact |
| P03.3 | Full variable/secret/access catalog, bounded safe telemetry/correlation, disabled Stream signature boundary, current provider requirements, rotation/incident/rollback/restore preparation | Real secrets/accounts/provider enforcement, durable replay/order/domain effects, monitoring service, configured backup or restore proof |

Only development/test fixtures are served. Loopback binds, production/staging
refusal, dummy backend, readiness 503, pending fixture compatibility and writes
405 remain intentional. Configuration-profile acceptance is offline definition
validation with `runtime_available=False`; it never proves provisioned ownership
or enables an adapter. The current protected-service deny list still refuses the
existing Postgres service. It must not be falsely listed as wholly app-owned to
accommodate the preferred shared logical database: schema/role-specific audit
evidence and a reviewed future preflight are required.

## Checks actually executed

Local Linux: Python **3.12.14**, Node **24.19.0**, npm **11.9.0**. Fresh locked
pip/npm installation, then final API hash-lock reinstall and `pip check`, passed.
Gunicorn **26.2.0** is the only added runtime dependency; locks and inventory
record hashes/license metadata. Its published/available-patch discrepancy and
required preactivation recheck are documented in the build guide. Hosted checks
use clean locked installs on Ubuntu 24.04 and an actual Linux amd64 image build.

Use canonical API setup (`services/api/.venv`) from the READMEs. This session's
temporary root `.venv` ran the equivalent commands; its location is not required
for recovery. Commands below use canonical paths.

| Directory | Command | Result |
|---|---|---|
| services/api | `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock` and `.venv/bin/python -m pip check` | Install and consistency pass |
| services/api | `GLOW_ENV=test .venv/bin/python manage.py check` | No issues |
| services/api | `GLOW_ENV=test .venv/bin/python manage.py test tests --verbosity 1` | **147 pass**, unused database skipped |
| services/api | `GLOW_ENV=test .venv/bin/python -m glow_persistence.static_check` | **32 model / two unapplied migration** definitions agree, no SQL |
| services/api | `.venv/bin/ruff check .` and `.venv/bin/ruff format --check .` and `.venv/bin/mypy` | Pass; **47 files**, **23 modules** |
| repo root | `PYTHONPATH=services/api services/api/.venv/bin/python -m unittest discover -s packages/contracts/tests -v` | **36 methods pass**, shared corpus as subtests |
| packages/contracts | `npm ci --ignore-scripts` then `npm run check` | Deterministic generation and **199 JS cases pass** |
| apps/mobile | `npm ci --ignore-scripts` then `EXPO_OFFLINE=1 npm run check` | TypeScript/ESLint and **12 tests pass** |
| apps/mobile | `EXPO_OFFLINE=1 npm run check:expo` and `EXPO_OFFLINE=1 npm run export:development` | Offline pin check and iOS/Android development JS export pass |
| repo root | `GLOW_SMOKE_PYTHON="$PWD/services/api/.venv/bin/python" node scripts/smoke.mjs` | Actual loopback API/mobile client: live 200, ready 503, pending fixtures, writes 405 |
| repo root | `GLOW_SMOKE_PYTHON="$PWD/services/api/.venv/bin/python" node --test scripts/smoke.test.mjs` | Occupied-port/startup-failure regression passes |
| repo root, hosted Docker | `docker build --platform linux/amd64 --tag glow-api:ci --iidfile .work/api-image-id .` after `mkdir -p .work`, then `python3 scripts/container_smoke.py glow-api:ci` | Actual image/user/workdir/entrypoint, unsafe-mode refusal, network-none loopback health and SIGTERM shutdown pass |
| repo root | `git diff --cached --check` | Clean |

Counts overlap where corpus cases run in both languages; do not sum them into a
unique-case claim. Expo offline dependency checking is limited. JS exports do
not establish signed builds, device behavior or store/release acceptance.

## Independent review and corrected findings

Independent review reran **61** configuration/profile/webhook/runtime/worker/
telemetry tests, real loopback smoke and narrowed-host HTTP enforcement. Findings
fixed before implementation publication: advancing retry clock could yield
negative sleep; settings ignored narrowed validated hosts; the smoke-only Python
selector was passed into strict runtime configuration; huge numeric telemetry
could trigger raw formatter diagnostics; and networking/environment reproduction
wording was imprecise. Final implementation review reported no unresolved blocker.
The final follow-up also reconciles the shared-database preference and separately
issued audit without enabling protected targets or claiming audit completion.

## Railway, database and provider limits

Selected project is **ample-illumination**,
`ce01529f-679f-4f52-a979-23113299a59b`, alongside HDE as Nathan requested.
Read-only metadata still shows the protected production environment and four
existing services; this run creates no app service, environment, domain or volume,
copies no shared secrets, and makes no Railway configuration/deployment changes.
Current runtime lacks an appropriate serving mode, so creating an always-on
service has no bounded P03 purpose. Future service-specific settings are concrete
in [build/deploy preparation](../operations/build-and-deploy.md).

The owner now prefers clean app storage in HDE's logical database using app-owned
schema/roles and appropriate structural reuse. No legacy users need migration.
Existing app structures and 32 provisional models require an object-level map;
`public` is not an app-only deletion boundary. The separately issued
[AP1-DBA-001](https://drive.google.com/file/d/1-AW7Jj_nDnMQiDrLgP0293ZfUuMJScP6/view)
authorizes its bounded catalog audit now, not app runtime wiring, DDL or deletion.
Its live findings were unavailable in this execution. P11 remains the runtime/
migration stage; A02 and shared-effect/role validation remain open.

Published unit rates and observed workspace type are recorded in the resource
inventory; account subscription, spend limits and actual consumption are unknown.
No new always-on Railway cost or third-party subscription was incurred by these
actions. Hosted CI ran; account-specific CI billing was not inspected.

No database connection, migration application, live HDE/provider request, secret
read, public distribution or protected mutation occurred. CI publishes no image
and has no deploy job. This is an account of observed actions and inspected app
source, not a comprehensive audit of hidden hooks or unrelated production history.

DB01–DB13, PV01–PV08, PR01, N01 and R01 remain unexecuted in the
[deferred acceptance matrix](p11-deferred-acceptance.md). Worker substitutes do
not prove crash/durable delivery; signature checks do not prove replay safety;
runbooks do not prove backup/restore. A01/A07 HDE rights/contracts, A04 access/
signing, A05 policy/operations owners, A08 chat enforcement and A06 disabled paid
scope remain visible. None prevents this preparation checkpoint.

The [current handoff](../continuity/current-handoff.md) supplies exact sources,
protected identities, recovery and next P04.1 work. AB1-R004 records final
publication, Notion closure and saved-for-relay delivery state.

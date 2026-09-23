# App Builder 1 current handoff

Recorded 23 September 2026 for the next **fresh execution session**. Nathan Amthor
owns product/resource decisions. **App Planner 1** coordinates and manages the
build; **App Builder 1** implements and reports to App Planner 1. Assignment
**AP1-P03-001** covers P03.1–P03.3 operations/configuration preparation. The complete
dating app and P04–P12 remain unfinished. Assume no earlier conversation, local
checkout, credential, virtual environment, process or uncommitted work survives.

## Repository and publication state

Private [amthorn78/glow-dating-app](https://github.com/amthorn78/glow-dating-app),
repository ID **1383293037**, default branch **main**. Accepted starting P02 main
was **d950ff5a2f74bee6e3a8afd0ddf4aff693d69849**, tree
**03ad1b31cb1b0de3409037ad4ec401be76ea2bc7**, through
[PR 3](https://github.com/amthorn78/glow-dating-app/pull/3). The accepted P02
candidate was **75df91bfcd7d9d14f424130999e0c08a41248e3d**;
[its CI](https://github.com/amthorn78/glow-dating-app/actions/runs/35871715638) and
[merged-main CI](https://github.com/amthorn78/glow-dating-app/actions/runs/35871998924)
passed. That checkpoint is history, not a branch to reset to.

P03 publication: [PR 4](https://github.com/amthorn78/glow-dating-app/pull/4), branch
**app-builder-1/p03-operations-foundation**, implementation candidate
**f36189b611b716fdb1db2998ccd58344537da62c**, tree
**55d711088dacdf8114cf26678a53b52b9eaa7e91**. The 41 changed implementation blobs
and published tree were checked against the reviewed local snapshot. Local
integrated checks passed at the scope described below. Implementation
[PR run 35884841565](https://github.com/amthorn78/glow-dating-app/actions/runs/35884841565)
passed all four jobs, including actual built-image smoke. Its runner-local image
ID is `sha256:eacf50d024645910168855687ee14534b9f7aa4a3e6396ee593584957298a23a`.
Hosted evidence is recorded in the [P03 checkpoint](../testing/p03-checkpoint.md).

This handoff and the P03 checkpoint are subsequent documentation changes on
PR 4. The containing final candidate must pass all four Foundation jobs before
merge: **API checks**, **Mobile checks**, **API mobile smoke**, and **API artifact
checks**. Consult PR 4, its actual candidate runs, and **AB1-R004** in the shared
progress record for the final accepted head, merge and CI. Those values cannot
be embedded self-referentially in their own containing commit. Do not infer a
merge or passing final run from this handoff alone. At resume, verify current
main, PR 4 terminal state and all newer open PRs before editing. Continue from
current remote head; preserve intervening work. Branch protection remains
unenforced under the observed private-repository arrangement; exact-candidate
review/checks are procedural and must not be represented as enforced protection.

Publication uses hash-verified snapshots and GitHub blob/tree/commit operations.
A local synthetic baseline is not remote Git history. Acquire a fresh authenticated
checkout or verify a fresh snapshot against actual remote blob/tree hashes; never
push fabricated lineage, force-push, or reset away intervening changes.

## Authority and source records

Read these current sources before new implementation; repository documentation
owns technical behavior and GAPP canon, while Notion owns live state.

- [AGENTS.md](../../AGENTS.md), applicable nested instructions,
  [GAPP-PF00](../pf-canon/GAPP-PF00-Canon-Index-and-Authority.md), and complete
  [GAPP-PF01](../pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md), especially
  D08, P04, P11 and the current same-project decision.
- [Implementation Control](https://app.notion.com/p/3e44590a05eb8118bf02f0dc0c3ea57c),
  [Work Register](https://app.notion.com/p/71b769915b5b4e00830663770bc95f7e), data
  source `collection://5ea4c24d-ec63-4afb-a434-8969c26b8fbe`; fetch its schema before
  property writes. [D08 authority](https://app.notion.com/p/3e44590a05eb8106b26aea3147dc84bf).
- [Shared progress record / AB1-R004](https://app.notion.com/p/3e44590a05eb81d58971ee4cd870774f).
  Inspect all subsequent builder reports and planner acknowledgments. AB1-R004 is
  this checkpoint's closure destination; saving is not direct planner delivery.
- [P03.1](https://app.notion.com/p/3e44590a05eb81ebac0ff50bd1ea6655),
  [P03.2](https://app.notion.com/p/3e44590a05eb812f97cbf42aa7796203),
  [P03.3](https://app.notion.com/p/3e44590a05eb81bdb02ac7555edc5e9e), and next
  [P04.1 — Build native shell and account/onboarding flows](https://app.notion.com/3e44590a05eb812db856f1a7221aa464).
- [AP1-P03-001 assignment](https://drive.google.com/file/d/17OuTGVLGb-SPLwRbEK3VUu3I2G38lH3r/view),
  [Drive supporting project](https://drive.google.com/drive/folders/1MXxJc_6tk-1Kf4QQhoEJPe-3uphKmrC1),
  [research/sources](https://drive.google.com/drive/folders/1cZvOmqyN-NeU2BXNUSbHVk9F_LCeSPWS),
  [original brief](https://drive.google.com/file/d/1P52syYgKzsIUWscTMXPUcylBru4S1bO6/view).
  Repository authority transfer **ac38e58651e5578ee8503b6423e4884203b42278** remains
  effective; Drive planning copies are historical. Do not repeat the transfer or
  edit parallel governing plans.

D08 already authorizes required application-owned GitHub, Railway, Drive and
Notion creation/modification, scoped PRs and checked merges. No routine phase or
application-write reapproval is required. The exception is **any direct or
indirect HDE effect**, including shared resources. New third-party purchases or
contracts outside the grant, destructive legacy retirement, public distribution
and messages to external people remain separate actions. A missing credential or
actual platform restriction is a capability boundary; never request secrets in
chat. App Planner 1 cannot expand Nathan's HDE authorization.

## Same Railway project and protected identities

Nathan explicitly instructed: **“the app should be in the same project as the HD
Engine”**. Use **ample-illumination**, not a new application project.
[ADR 0002](../adr/0002-same-project-application-services.md),
[resource ownership](../operations/resource-ownership.md), and
[environments](../operations/environments.md) record the superseding disposition.
App service IDs, environment configuration, credentials, schema/role permissions
and ownership must remain distinct. The app's future environment/service IDs and domains are
not provisioned. `app-staging` is only a proposed empty environment name.
The existing HDE production environment is not an automatically selected app
production target. Never duplicate HDE production or inherit shared secrets.

| Resource | Verified identity to protect/revalidate |
|---|---|
| Workspace | amthorn78's Projects — `ae7d1e62-8a2d-4055-b637-ec56536a7239` |
| Selected shared project | ample-illumination — `ce01529f-679f-4f52-a979-23113299a59b` |
| Existing production environment | `a06b149a-2876-40bf-84a0-7880feaf8b67` |
| HDE repository | `amthorn78/glow-hdengine-v2` |
| HDE service | `62e7b993-6d30-48b4-9059-c1884b16e90b` |
| Legacy backend service | `bfedf816-d6d4-4155-b495-cd6416e91e49` |
| Protected PostgreSQL service / volume | `c4d54416-d1ab-4818-898b-9b9be03bc69a` / `aad776ab-27cc-4994-87f0-589af0de7aa1` |
| Protected Redis service / volume | `87b4810c-3e23-4d27-b7fc-0bca7131ed37` / `9ec5ad1f-eab1-4722-ae02-28684aa3b89f` |

This is a protection baseline, not an exhaustive safe-target allowlist. Recheck
current consumers/references and exact app ownership before each external action.
Same-project placement does not confer database, secret or HDE API rights.
Railway private networks are environment-scoped; a separate app environment does
not implicitly reach HDE's existing private network. HDE networking changes,
shared/project/environment variable writes, legacy Redis reuse and protected
source/deployment changes remain excluded by D08.

This P03 execution made no Railway mutation, live secret read, database connection,
migration application, broker/provider/HDE call, public exposure or account purchase.
Application service creation was deliberately deferred: current fixture runtime
cannot serve an honest Railway deployment. Future app-only provisioning remains
authorized when a concrete valid runtime need and verified target exist.
Do not create always-on services merely to populate the resource map. Read-only
metadata and published prices do not establish actual account budget, app monthly
cost, spend cap, provider access or production readiness.

## Latest database direction and separate audit boundary

The current Implementation Control includes newer owner direction: **prefer the
same logical PostgreSQL database as HDE**, using app-owned schemas/tables and
restricted application runtime/migration roles, with maximum appropriate
structural reuse after an actual ownership, dependency and capacity audit.
**No legacy user data needs migration.** This supersedes assumptions that app
persistence necessarily requires a separate logical database. It does not
establish existing schema ownership, authorize an HDE table change, or certify
capacity and safe reuse. The 32 P02 models are provisional design definitions;
compare them against the verified existing map instead of assuming 32 new tables.

The dedicated **AP1-DBA-001** terminal audit prompt is
[issued here](https://drive.google.com/file/d/1-AW7Jj_nDnMQiDrLgP0293ZfUuMJScP6/view)
and **not executed** at this checkpoint. Its exception permits only the bounded
catalog connection in that separate audit scope. It does not authorize P03 to
connect, query application records, apply migrations or broaden the audit.
P11 remains the runtime/migration integration stage. Fetch and follow the exact
current audit assignment and record its results before designing a shared logical
database/schema/role preflight.

Do not classify the entire `public` schema as application-owned:
`public.hde_body_graphs_current` is an identified engine-owned example in the
source record. No wholesale drop/reset, privileged HDE credential reuse or
unverified legacy-table reuse is authorized. Preserve HDE objects and grants.
The current P03 API/worker target validator deliberately refuses the protected
Postgres **service ID** and cannot validate shared logical database/schema roles.
Do not evade that guard by declaring the protected database container app-owned.
Future shared-target acceptance needs the verified audit manifest and an explicit
schema/role-aware implementation before P11 activation.

## Completed preparation and retained limitations

P01.1–P01.3 and P02.1–P02.3 are the accepted earlier preparation checkpoints.
[PR 3](https://github.com/amthorn78/glow-dating-app/pull/3) provides the P02
contract/data/provider foundation: F01–F20 logical production flows, generated
wire/runtime validation, trusted pair/version eligibility, **32 provisional model
definitions and two unapplied migrations**, and provisional app-owned provider
ports. The newer database audit must determine appropriate reuse and mapping
before these definitions become an actual database change.
OpenAPI remains a component catalog with no production routes. No allauth,
real account/session lifecycle, SQL/transaction or HDE calculation is implemented
by those definitions. See [P02 checkpoint](../testing/p02-checkpoint.md),
[production contracts](../architecture/production-contracts.md),
[data model](../architecture/data-model.md),
[trusted eligibility](../architecture/trusted-eligibility.md),
[provider contracts](../architecture/provider-conformance.md),
[HDE boundary](../architecture/provisional-hde-seam.md), and
[privacy/safety rules](../architecture/privacy-and-safety-rules.md).

P03 implementation preparation is locally validated and published on PR 4;
final hosted/publication closure must be verified as described above:

- **P03.1:** current same-project environment/service/ownership map, protected IDs,
  concrete app-only future configuration and exact deferred external activation.
  No app resource or domain has been provisioned.
- **P03.2:** hash-locked Gunicorn runtime, digest-pinned Python Docker build,
  restricted build context, nonroot image, loopback-only entrypoint, explicit
  port/shutdown/bounded restart design, and fourth hosted artifact-check job.
  Strict typed configuration separates offline future profiles from unavailable
  staging/production runtime. Target checks require positive independently
  verified app ownership and reject protected services. Secret values are not
  loaded. Runtime host allowlists consume validated configuration without widening.
- **P03.3:** bounded retry/worker interfaces using deterministic substitutes;
  safe structured logging, canonical bounded correlation metadata and finite
  metric/error vocabulary; actual mobile public-variable allowlist; synthetic
  Stream raw-body signature verification; provider/access catalog and operational
  secret/incident/deployment/rollback/backup preparation.

The API's served surface is still development/test fixture GETs only. Liveness
returns 200; readiness deliberately returns 503; recommendations are synthetic and
compatibility pending; writes return 405. The API uses Django's dummy backend.
Staging/production startup refuses even if offline profile validation succeeds.
Inherited database/broker/HDE/secret configuration refuses by presence. Optional
disabled providers do not block fixture development; mandatory absent future
capabilities cannot be silently waived. No configured provider failure may become
synthetic success.

The image/runtime remains loopback-only. No registry publication or Railway
rollout is configured. Local Gunicorn tests are executable process evidence;
only a passing hosted artifact job establishes its actual built-image checks.
The current image excludes persistence/migrations and performs no hidden database
or migration action. [Build/deploy](../operations/build-and-deploy.md) records the
Gunicorn 26.2.0 package-availability distinction and the patch-version review
required before any non-loopback activation.

Retry substitutes do not establish a durable queue, after-commit dispatch,
restart recovery or provider exactly-once semantics. The signature verifier
performs authentication preparation only: no webhook route, durable replay store,
event ordering or business effect is activated. Account/domain/provider access,
secret provisioning and monitoring exporters remain unverified/unconfigured.
Backup and recovery procedures are plans, not configured backups or restore proof.
Billing and purchase UI remain disabled under A06.

Implementation/runbook homes:
[configuration and secrets](../operations/configuration.md),
[build/deploy](../operations/build-and-deploy.md),
[CI/branch policy](../operations/ci-and-branch-policy.md),
[observability/workers](../operations/observability-and-workers.md),
[providers/webhooks](../operations/providers-and-webhooks.md),
[operational runbooks](../operations/operational-runbooks.md), and
[migration/P11 plan](../operations/migration-plan.md).

## Validation and fresh-checkout reproduction

Validated local baseline: Linux, **Python 3.12.14**, **Node 24.19.0**,
**npm 11.9.0**. Integrated results: **147 API/domain/static tests**, **36 Python
contract methods**, **199 JavaScript corpus cases**, **12 mobile tests**,
deterministic generation, Ruff/format over **47 Python files**, mypy over
**23 modules**, pip consistency, TypeScript/ESLint, static **32-model/two-migration**
agreement, real loopback HTTP smoke/startup regression and iOS/Android development
JavaScript exports. Shared corpus/subtests and scoped reruns overlap these counts;
do not add them into a unique-case total. Exact candidate commands/results and
hosted artifact identity, when available, belong to the
[P03 checkpoint](../testing/p03-checkpoint.md).

Use the committed Python and npm locks without upgrading dependencies. The
following uses the canonical `services/api/.venv` location; the authoring session's
repository-root `.venv` was temporary, not a required surviving artifact.

From `services/api/`:

```bash
python --version
python -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock
.venv/bin/python -m pip check
GLOW_ENV=test .venv/bin/python manage.py check
GLOW_ENV=test .venv/bin/python manage.py test tests --verbosity 2
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
PYTHONPATH=. .venv/bin/python -m unittest discover -s ../../packages/contracts/tests -v
GLOW_ENV=test .venv/bin/python -m glow_persistence.static_check
GLOW_ENV=test .venv/bin/python smoke.py
```

From `packages/contracts/`, then independently from `apps/mobile/`:

```bash
npm ci --ignore-scripts
npm run check
```

Additional commands from `apps/mobile/`:

```bash
EXPO_OFFLINE=1 npm run check:expo
EXPO_OFFLINE=1 npm run export:development
```

From the repository root after those installs:

```bash
GLOW_SMOKE_PYTHON="$PWD/services/api/.venv/bin/python" node scripts/smoke.mjs
GLOW_SMOKE_PYTHON="$PWD/services/api/.venv/bin/python" node --test scripts/smoke.test.mjs
```

The smoke harness removes its own `GLOW_SMOKE_PYTHON` helper variable from the
API child environment. The API's strict `GLOW_*` allowlist must remain intact.
If Docker is available, from the repository root:

```bash
mkdir -p .work
docker build --platform linux/amd64 --tag glow-api:ci --iidfile .work/api-image-id .
python3 scripts/container_smoke.py glow-api:ci
```

This image check uses no network for the running container, publishes no port,
checks runtime refusal/loopback health and bounded termination, then removes its
container. The authoring environment lacked a Docker/Podman daemon; the hosted
**API artifact checks** job is the actual image-validation route. Do not claim
local Docker execution. Expo offline SDK checks and development JS exports do not
prove signed builds, emulators/devices, release transport, accessibility or stores.
No test applies migrations or uses SQLite/PostgreSQL as an early substitute.

## Dependencies and next concrete action

P11 remains the final database/live integration stage: **disposable PostgreSQL →
staging app schema/role targets → verified app production schema/role target**.
The owner prefers that production target in HDE's same logical database after
audit; isolated application privileges and protected HDE ownership remain required.
P04–P10 must preserve that sequencing, with only the separately assigned bounded
AP1-DBA-001 catalog audit exception described above. [Deferred acceptance](../testing/p11-deferred-acceptance.md)
keeps **DB01–DB13, PV01–PV08 and PR01** individually open until actual execution.
P03 simulations do not pass them. HDE live compatibility can remain blocked while
independent app feature work proceeds.

| Dependency | Required later resolution |
|---|---|
| A01/A07 | Supported HDE release/wire/output/version/cache/deletion rights and throughput; no guessed endpoint, score or engine call |
| A02 | AP1-DBA-001 catalog audit and verified ownership/dependency/capacity map; prefer same logical database with restricted app schema/roles and appropriate structural reuse; no legacy user-data migration, shared credential reuse or wholesale reset |
| A04 | Actual provider/domain/account budget, signing and required access at the affected phase |
| A05 | Geography/language, policy/retention/history, moderation/support/on-call ownership; no invented operating commitments |
| A06 | Real paid product decision; billing stays disabled |
| A08 | Provider-level fail-closed mutual-match/block chat authorization; hook existence is not capability proof |

After verifying PR 4's accepted final candidate/merge, AB1-R004 and current Notion
state, start existing **P04.1 — Build native shell and account/onboarding flows**,
[task](https://app.notion.com/3e44590a05eb812db856f1a7221aa464). Its inspected state
at this handoff is **Planned**, with dependencies **P02.1, P02.3, P03.2**. Inspect
its complete current task before changing state. Read GAPP-PF01 P04, mobile/API
instructions, current contracts and auth/privacy boundaries; implement the native
shell and account/onboarding journey at the permitted fixture/sandbox scope.
Coordinate the separately issued AP1-DBA-001 audit through the existing control
record; it is not work implicitly granted to P04.1. Use its eventual evidence to
reconcile provisional model/contract mappings. Maintained real authentication
integration and persistence-dependent evidence must remain truthful and follow P11. Do not interpret P04.1 as permission to
activate production, add paid services, invent product policies or publicize fixtures.

Keep one active work item in Notion unless a concrete asynchronous operation
requires otherwise. Record coherent commits/PRs, actual tests, limitations,
resource effects and next action; use current repository plan links. No unresolved
local implementation defect is being carried forward by this preparation handoff;
if final candidate checks reveal one, repair it and record the changed head before
claiming closure. Unfinished live/provider/native acceptance above is deliberate,
not a claim that those systems work.

No direct App Planner 1 session URL or transport is verified. Save the substantive
report in the shared record, address the final report to App Planner 1, and state
actual delivery status. Nathan may relay it; saving does not establish receipt,
review or acknowledgment. Each later prompt must carry this full role/authority,
current-head/source, scope, protected-resource, validation/dependency and next-step
context. Do not rely on “continue from above” or promise background execution.

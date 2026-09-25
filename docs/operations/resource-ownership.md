# Railway resource ownership and protected boundary

## Current P03 disposition — 23 September 2026

Nathan's instruction during this execution is: **“the app should be in the same project as the HD Engine”**. This supersedes P01's separate-project disposition below and that part of [ADR 0001](../adr/0001-isolated-application-foundation.md). [ADR 0002](../adr/0002-same-project-application-services.md) records the replacement decision. Use the existing `ample-illumination` project, ID `ce01529f-679f-4f52-a979-23113299a59b`, for future app-owned resources. Do not create a second Railway project for this application.

The owner's later database direction also prefers the **same logical PostgreSQL database as HDE**, with separately owned app schema/tables and maximum appropriate reuse unless assessment establishes a strong concrete counterargument. This supersedes the separate-app-database default; it does not select existing privileged credentials, HDE table ownership, shared grants/settings or the legacy backend runtime for reuse. App identities, scoped configuration and persistence privileges remain explicit. D08's effect-based HDE protection and P11's integration sequence still apply. No Railway resource was created, configured or deployed during this P03 implementation, and this session opened no database connection. Current app environment/service/domain/volume identities and app schema/role mapping remain unestablished.

The [environment and service map](environments.md) distinguishes local/test behavior from future staging/production roles. Complete P03 preparation without provisioning: current runtime deliberately refuses staging/production, development fixtures bind loopback, and readiness remains 503. Empty services are technically possible, but no operational P03 need warrants creating them merely to populate the map.

### Current persistence direction and audit dependency

The [Implementation Control record](https://app.notion.com/p/3e44590a05eb8118bf02f0dc0c3ea57c), under “Owner database direction — 23 September 2026” and “Clean app data and terminal audit assignment — 23 September 2026”, records the latest direction. No legacy backend/frontend user information is relevant to the new app, so no legacy user-data migration is required. This does not authorize deleting shared objects or data whose ownership/dependencies remain unknown.

Before committing the persistence layout, classify existing objects as **HDE-owned**, **reusable app-owned**, **obsolete app-owned** or **new-required**. Compare all 32 provisional P02 model definitions with that object map; they are not a requirement to create 32 new tables. Specify permitted reads/writes, separate restricted app runtime/migration roles, schema ownership and one owning migration system per reused table. Names, roles, grants, search-path settings, capacity, locking and shared operational effects remain A02 evidence requirements. Adding app objects consumes shared database resources even when no HDE table is altered.

The supplied **PF07-Canon-Glow-Infrastructure-v2.3.2**, section **2.2 Environment facts**, documents a shared database instance, HDE schema `hde`, and backend schema **TBD**. That inventory is documentary context, not a current logical-database, object, role or grant audit. The control record also identifies historical/source evidence for HDE object `public.hde_body_graphs_current`; `public` must not be treated as an app-only schema or dropped/reset wholesale.

[Completed database audit](../planning/database-audit-2026-09-23.md) and [catalog/model map](../planning/database-catalog-2026-09-23.md) record the separate read-only inspection on 23 September. HDE and legacy backend used logical database `railway` and privileged `postgres`; preserve HDE objects, including the view in `public`. No existing physical table was approved for reuse by the 32 provisional app models. A clean app-owned schema with restricted roles is the audited direction. No DDL, role/grant change, deletion or wiring was performed. Reverify ownership/capacity and implement isolation at P11; A02 is not closed by this dated audit.

### P03 identity recheck

Read-only `list_workspaces`, `list_projects`, `list_services` and `get_service_config` calls on 23 September 2026 revalidated:

| Resource | Verified identity | Disposition |
| --- | --- | --- |
| Workspace | `amthorn78's Projects`, `ae7d1e62-8a2d-4055-b637-ec56536a7239`; returned type `team`, four projects | Account metadata only; no subscription/role inference |
| Shared app/HDE project | `ample-illumination`, `ce01529f-679f-4f52-a979-23113299a59b` | Selected by owner; protect existing shared configuration |
| Only listed environment in this project | `production`, `a06b149a-2876-40bf-84a0-7880feaf8b67` | Contains protected resources; not an app activation selection |
| HDE service | `glow-hdengine-v2`, `62e7b993-6d30-48b4-9059-c1884b16e90b`; source `amthorn78/glow-hdengine-v2`, `main` | Protected |
| Legacy backend | `glow-backend-v4`, `bfedf816-d6d4-4155-b495-cd6416e91e49`; source `amthorn78/glow-backend-v4`, `main` | Preserve; no reuse, restart or retirement |
| PostgreSQL / volume | `c4d54416-d1ab-4818-898b-9b9be03bc69a` / `aad776ab-27cc-4994-87f0-589af0de7aa1` | Protected. The app gets its own logical database on this service (OD-18, [ADR 0004](../adr/0004-app-database-placement.md)), after the A02 capacity, operational-limits and role review before P11C |
| Redis / volume | `87b4810c-3e23-4d27-b7fc-0bca7131ed37` / `9ec5ad1f-eab1-4722-ae02-28684aa3b89f` | Protected; consumers unresolved |
| Dating-app resources | No separately identified app service returned in this project | Planned only; no app deployment or consumption observed |

All four protected service configurations returned `staged: null`. This is a point-in-time configuration observation, not a health, deployment or permission certification. No current deployment-status/commit claim is made from this recheck; historical P01 deployment evidence remains labeled below. Service metadata exposes variable names, but no variable-value tool was called and no secret values, database contents or live endpoints were read.

The other three accessible projects retain the IDs in the P01 history. P03 also listed their service names: `acs-wagtail-baseline-validation` has `Postgres` and `web`; `tranquil-courtesy` has `Postgres` and `cmv-website`; `valiant-clarity` has `englishbiztraining`. They remain outside this application's write scope.

### Scope controls for the shared project

- Create/configure only a newly identified app-owned service in an explicitly selected environment. `create_service` can omit `image` for an empty service; omitting `environmentId` instead creates across all non-fork environments. GitHub `create_deployment` creates a service and triggers deployment immediately.
- Supply both exact `serviceId` and `environmentId` to every app configuration/variable change. `update_service` without an environment affects all environments. `set_variables` without a service writes shared environment variables and may redeploy affected services; `skipDeploys` controls that side effect. Never write shared variables for this work.
- Do not copy production to establish app staging: Railway's duplicate-environment operation copies services, variables and configuration. An empty app-specific environment within this project is the proposed later staging option, with identity/access verified before creation.
- Services within one environment share its private network; separate services are not a network-isolation guarantee. Different environments have separate networks. No proposed name such as `app-staging` establishes a network or makes HDE reachable. Future HDE access still requires A01/A07's supported interface and authorized data access.
- Do not run a whole-project IaC synchronization in this shared project. It can delete resources omitted from the app's file. No import, migration, partial ownership transfer, shared policy change or destructive cleanup is part of P03.

These boundaries supplement the current [build/deploy instructions](build-and-deploy.md); they do not grant protected-resource authority. Inspect the exact target and side effects again immediately before any later external action.

### Platform configuration and cost facts

Current official Railway documentation was checked on 23 September 2026. [Config as Code](https://docs.railway.com/config-as-code/reference) is deprecated: new services cannot opt into `railway.json`/`railway.toml`, and legacy support ends 1 December 2026. [Infrastructure as Code](https://docs.railway.com/infrastructure-as-code) is CLI-evaluated, not automatically applied during a service deployment. The app prepares native service-scoped configuration rather than introducing legacy config or a project-wide apply. The [service API](https://docs.railway.com/integrations/api/manage-services) documents empty service creation and separate instance configuration/deploy operations.

The [Pricing Plans](https://docs.railway.com/pricing/plans) page still lists container RAM $10/GB-month, CPU $20/vCPU-month, egress $0.05/GB and volume storage $0.15/GB-month. Those are published unit rates. P03 did not establish the account's subscription, credits, current bill, budget/spend cap, app resource limits or monthly app consumption. Workspace type `team` is not a billing-plan determination. No app resource was provisioned and no new subscription or spending limit was configured.

Official boundary references: [private networking](https://docs.railway.com/networking/private-networking/how-it-works), [empty versus duplicate environments](https://docs.railway.com/environments#create-an-environment), [IaC ownership/context](https://docs.railway.com/infrastructure-as-code/reference). The connector exposes no dedicated environment-creation or billing/plan-read tool in this session; that is a tool-surface observation, not proof that the account lacks platform access. Verify the available supported route when the action is concrete.

## Historical P01 assessment — preserved, separate-project disposition superseded

The following is the original P01.1 record. Its deployment revisions, volume sizes, capability observations and assessment-time statements are historical, not refreshed P03 assertions. Its selected new-project disposition and any separate-app-database implication no longer govern; use the current owner directions above. Historical observations remain intact; current reuse planning must follow the object-level audit. HDE protection and P11 integration sequencing remain unchanged.

Assessment date: 2026-09-23. Scope: read-only Railway inspection for P01.1. No Railway resource, deployment, variable, network, volume, or database was changed. No variable values were retrieved and no database connection was opened.

### Selected disposition

Use a new application-owned Railway project for the Glow dating application when its deployment prerequisites are satisfied. Preserve the existing `ample-illumination` project and all its services. This is the selected infrastructure disposition; no new project or service was provisioned during this assessment.

The legacy backend, PostgreSQL and Redis have unresolved consumer/data mappings. Do not reuse, modify or retire these resources on the basis of their names or variable names. Do not change shared configuration that could affect HDE. Do not connect the final application database before P11; P11 must follow the governing disposable-PostgreSQL, staging and authorized app-production sequence.

### Verified identities

Observed through Railway `list_workspaces`, `list_projects`, `list_services`, `get_status` and `get_service_config`:

| Resource | Name | Exact ID |
| --- | --- | --- |
| Workspace | amthorn78's Projects | `ae7d1e62-8a2d-4055-b637-ec56536a7239` |
| Protected project | ample-illumination | `ce01529f-679f-4f52-a979-23113299a59b` |
| Only listed environment | production | `a06b149a-2876-40bf-84a0-7880feaf8b67` |
| HDE service | glow-hdengine-v2 | `62e7b993-6d30-48b4-9059-c1884b16e90b` |
| Legacy backend service | glow-backend-v4 | `bfedf816-d6d4-4155-b495-cd6416e91e49` |
| PostgreSQL service | Postgres | `c4d54416-d1ab-4818-898b-9b9be03bc69a` |
| PostgreSQL volume | postgres-volume | `aad776ab-27cc-4994-87f0-589af0de7aa1` |
| Redis service | Redis | `87b4810c-3e23-4d27-b7fc-0bca7131ed37` |
| Redis volume | redis-volume | `9ec5ad1f-eab1-4722-ae02-28684aa3b89f` |

All protected identities match the initialization prompt. `get_status` reported no staged/applying work at inspection. This is a point-in-time observation, not permission to mutate the project.

### Source configuration and deployed revisions

| Service | Configured source | Latest deployed commit | Deployment ID | Railway status / creation time |
| --- | --- | --- | --- | --- |
| HDE | `amthorn78/glow-hdengine-v2`, branch `main` | `a63bf801665fbc19839fc013fcdb05386a1b0d09` | `7522ba86-37a8-41f2-84c5-e14caf697bb9` | `SUCCESS` / `2026-09-23T00:53:59.911Z` |
| Legacy backend | `amthorn78/glow-backend-v4`, branch `main` | `520f99aa2e933907a10954dbcabdb29b2e738c05` | `affa8efc-59cb-4ef5-817b-07d1c9232997` | `SUCCESS` / `2025-10-24T17:28:05.360Z` |
| PostgreSQL | `ghcr.io/railwayapp-templates/postgres-ssl:17` | Not a Git source | `5cc9cec5-839a-4fb0-9bc7-ac26d716b057` | `SUCCESS` / `2026-08-29T14:12:12.970Z` |
| Redis | `redis:8.2.9` | Not a Git source | `794a68df-b7c4-4a20-becb-60802011e105` | `SUCCESS` / `2026-09-12T10:16:49.697Z` |

Deployment metadata was read through `list_deployments`; deployed commits are not assertions about the current GitHub HEAD. Railway `SUCCESS` is deployment status, not application behavior validation.

HDE deployment snapshot: `f56b7aba-0cfb-4484-abcd-9063a681d615`. Legacy backend deployment snapshot: `03abe419-d996-4d75-a010-2491dbfeeaf0`.

Both application services use Railpack, V2 runtime, one replica in `europe-west4-drams3a`, and `checkSuites:false`. HDE additionally reports build environment V3. The HDE Railway domain is `glow-hdengine-v2-production.up.railway.app`; the backend domain is `glow-backend-v4-production.up.railway.app`. Both route to port 8080. No endpoint requests were made.

The HDE start command is:

```text
python -m pip install --no-cache-dir -r requirements.txt && python -m gunicorn 'adapter.factory:create_app()' --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 30
```

The returned backend configuration contained no custom build/start/healthcheck command. This does not establish whether repository configuration supplies those values.

PostgreSQL has private endpoint `postgres`, TCP proxy configuration for 5432, and a 500 MB volume at `/var/lib/postgresql/data`. Redis has private endpoint `redis`, TCP proxy configuration for 6379, and a 500 MB volume at `/data`. Both report one replica in `europe-west4-drams3a`.

### Unresolved consumer and data mapping

`get_service_config` returns variable names without values. It showed:

- HDE and the backend both define `DATABASE_URL`.
- The backend additionally defines `REDIS_URL`, `SESSION_BACKEND` and `SESSION_REDIS_STRICT`.
- HDE and the backend both define `HD_API_BASE_URL`, `HD_API_KEY` and `GEO_API_KEY`.

These observations do not establish effective variable references, logical database names, database roles, data ownership, Redis consumers, or all service dependencies. Resolving those questions remains a prerequisite to any proposed legacy-resource mutation. The isolated application project avoids requiring that mutation for the new foundation.

### Isolation and available provisioning capabilities

The complete official [How Private Networking Works](https://docs.railway.com/networking/private-networking/how-it-works) document was inspected. Railway private networks are isolated at project and environment level. A new application project therefore cannot implicitly reach HDE over its existing private network. Later HDE integration needs an explicit approved interface; this assessment does not authorize HDE networking changes.

Available tool capabilities were inspected but not invoked for mutation:

- `create_project` supports explicit workspace ID, name, description and visibility.
- `create_deployment` creates a service and immediately triggers its first deployment from a concrete connected GitHub repository, branch and exact destination project/environment. Establish the deployable repository before calling it.
- `update_service` supports build/start/predeploy commands, root/config paths, healthcheck, restart policy, sleep and watch patterns. It does not handle source changes or scaling.
- `set_variables` supports service or shared environment scope; app changes must target the isolated application resource explicitly.
- `generate_domain`, `redeploy` and `accept_deploy` are available mutations and were not called.

### Observed pricing and cost limits

Source inspected in full: [Railway Pricing Plans](https://docs.railway.com/pricing/plans), observed 2026-09-23.

| Container resource | Published usage rate |
| --- | --- |
| RAM | $10 / GB / month |
| CPU | $20 / vCPU / month |
| Network egress | $0.05 / GB |
| Volume storage | $0.15 / GB / month |

The documentation states that service builds are free. No account billing plan, current bill, remaining included usage, or new application consumption was inspected. These published rates are not an account-specific cost estimate or spending assertion.

### Other accessible projects

The same workspace listed these other projects. Their service contents were not inspected because they were outside this bounded assessment.

| Project | ID |
| --- | --- |
| acs-wagtail-baseline-validation | `479ae247-0295-426d-a2e5-735652be4581` |
| tranquil-courtesy | `69cc0c47-f2e2-4bfd-a39c-48dada753613` |
| valiant-clarity | `b5163762-faa3-4f1d-8c5d-d53381f82bd5` |

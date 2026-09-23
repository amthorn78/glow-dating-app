# ADR 0001: Isolated application foundation

Date: 2026-09-23  
Status: Selected; repository publication pending when this decision was recorded  
Work item: P01.1 — Assess legacy reuse and resource ownership

## P03 placement supersession

The Railway placement and storage defaults of this P01 decision were superseded by Nathan during P03 on 23 September 2026. [ADR 0002](0002-same-project-application-services.md) places app services in the same project as HDE and records the preferred shared logical database with separate app schema/roles, pending ownership/dependency audit. Appropriate existing app structures may be reused after that audit; no legacy user data needs migration. This historical assessment records why no legacy code was copied into the foundation, not a permanent prohibition on reviewed reuse. HDE and actual dependencies remain protected. AP1-DBA-001 is a separate bounded catalog-audit exception; app runtime/migrations and database-dependent acceptance remain P11.

## Decision

Establish a new private repository at the selected location `amthorn78/glow-dating-app`, using the governing plan's Expo/React Native/TypeScript mobile client and modular Django/DRF API baseline. No code is copied from the assessed legacy repositories. Preserve the legacy repositories, applications, services and data.

The owner/repository location is a selected creation target, not a claim that repository creation or publication has completed. App Builder 1's coordinating worker reported the GitHub creation form under owner `amthorn78`; publication was pending at this writing. The repository creation result, visibility, branch and exact initial commit must be recorded after creation.

Use isolated application infrastructure rather than modifying the shared Railway project or its existing backend, PostgreSQL or Redis. The current Glow HD Engine and its database remain protected. Database-dependent integration remains in P11; this decision does not authorize an earlier final database connection.

## Context and scope

The App Builder 1 initialization prompt authorizes application-owned implementation under D08, excludes changes affecting the Glow HD Engine, and calls for a bounded legacy assessment before establishing the application foundation. A fresh foundation is permitted; legacy reuse is optional and must be supported by evidence. No legacy retirement or deletion is authorized by this decision.

This assessment inspected the most relevant owned deployed-application sources and extracted templates. Repository discovery used the authenticated GitHub connector's owned-repository listing. Source reads were pinned to each verified default-branch HEAD below. The older initial repositories were not exhaustively audited.

## Inspected source identities

| Repository | Default branch | Inspected HEAD | Disposition |
|---|---|---|---|
| [amthorn78/glow-backend-v4](https://github.com/amthorn78/glow-backend-v4) | `main` | `1b91efd4777f3b990c7272cdf000dd0b4c44b7b4` | Preserve; reference selected contracts and validation cases. |
| [amthorn78/glow-frontend-v2](https://github.com/amthorn78/glow-frontend-v2) | `main` | `f0f95ca28f40b39f47624863db1f24373cc3ace9` | Preserve, including its business/legal landing page; reference UX and error handling. |
| [amthorn78/glow-template-backend](https://github.com/amthorn78/glow-template-backend) | `master` | `078b5f465cb66cf22cac7f2eddb7b393cd9c53b8` | Do not adopt as the new baseline. |
| [amthorn78/glow-template-frontend](https://github.com/amthorn78/glow-template-frontend) | `master` | `37dc3b3ad74104e304643f8270173e7efed38300` | Do not adopt as the new baseline. |

Full recursive tree responses reported `truncated: false`. No `AGENTS.md`, `CONTRIBUTING.md` or `CLAUDE.md` appeared in these four trees. README files were read. Their statements of readiness are documentation claims, not substitutes for executed validation.

## Evidence supporting the decision

### Legacy backend can mutate its configured database during import

At the inspected backend HEAD:

- [app.py](https://github.com/amthorn78/glow-backend-v4/blob/1b91efd4777f3b990c7272cdf000dd0b4c44b7b4/app.py), lines 3900–3907, executes `ensure_database()` and `run_startup_migration()` at module import. The former calls `db.create_all()`.
- [migrate_on_startup.py](https://github.com/amthorn78/glow-backend-v4/blob/1b91efd4777f3b990c7272cdf000dd0b4c44b7b4/migrate_on_startup.py) creates tables, adds `birth_data` columns/indexes and commits.
- [Procfile](https://github.com/amthorn78/glow-backend-v4/blob/1b91efd4777f3b990c7272cdf000dd0b4c44b7b4/Procfile) invokes [scripts/boot.sh](https://github.com/amthorn78/glow-backend-v4/blob/1b91efd4777f3b990c7272cdf000dd0b4c44b7b4/scripts/boot.sh), which imports the app during preflight and then starts Gunicorn with preload. [nixpacks.toml](https://github.com/amthorn78/glow-backend-v4/blob/1b91efd4777f3b990c7272cdf000dd0b4c44b7b4/nixpacks.toml) also names `app:app` as its Gunicorn target. Which start setting controls the current Railway deployment was not established by this source assessment.
- Root `app.py` reads `DATABASE_URL` and `REDIS_URL`. This proves source-level configuration dependencies, not the current logical database, role, volume or Redis consumer mapping.

Importing, running or redeploying this backend against its current environment cannot be treated as a read-only operation. The unresolved resource mapping supports using isolated application resources. No existing backend start, restart, import or migration was performed.

### Legacy architecture differs from the selected application baseline

[requirements.txt](https://github.com/amthorn78/glow-backend-v4/blob/1b91efd4777f3b990c7272cdf000dd0b4c44b7b4/requirements.txt) pins Flask 2.3.3 and Flask-SQLAlchemy 3.0.5. Root `app.py` contains 4,376 lines combining models, authentication/session handling, routes, compatibility calculations and database initialization.

`calculate_compatibility_score()` and `calculate_mutual_compatibility()` in that file implement a Magic 10 calculation and an HD enhancement fallback. They are not accepted HDE integration contracts for this build. Copying those calculations would conflict with the new application's explicit boundary that HDE owns Human Design intelligence.

[artifacts/db/schema.sql](https://github.com/amthorn78/glow-backend-v4/blob/1b91efd4777f3b990c7272cdf000dd0b4c44b7b4/artifacts/db/schema.sql) and [schema_overview.md](https://github.com/amthorn78/glow-backend-v4/blob/1b91efd4777f3b990c7272cdf000dd0b4c44b7b4/artifacts/db/schema_overview.md) provide historical app-schema evidence. They are not verification of today's production schema, data or shared-resource ownership.

Frontend [package.json](https://github.com/amthorn78/glow-frontend-v2/blob/f0f95ca28f40b39f47624863db1f24373cc3ace9/package.json) describes a Vite/React DOM application with browser routing and Radix UI components. It is not an Expo/React Native foundation.

### Existing frontend has consumers and a separate purpose to preserve

Frontend [vercel.json](https://github.com/amthorn78/glow-frontend-v2/blob/f0f95ca28f40b39f47624863db1f24373cc3ace9/vercel.json) routes `/api/(.*)` to `https://glow-backend-v4-production.up.railway.app/api/$1`. This is source evidence of a frontend-to-backend dependency; live Vercel configuration and current traffic were not inspected.

At current HEAD, [src/pages/LandingPage.tsx](https://github.com/amthorn78/glow-frontend-v2/blob/f0f95ca28f40b39f47624863db1f24373cc3ace9/src/pages/LandingPage.tsx) presents Glow services, support and business policies. Replacing this repository would risk disturbing that separate purpose. No change to its content or deployment is part of this decision.

### Extracted templates do not supply a verified working foundation

Template backend [src/main.py](https://github.com/amthorn78/glow-template-backend/blob/078b5f465cb66cf22cac7f2eddb7b393cd9c53b8/src/main.py) references `session` without importing it. Its direct development `app.run()` call precedes the later security hook definitions. These are source findings, not executed runtime test results.

Template frontend [src/components/BirthDataFormCanonical.jsx](https://github.com/amthorn78/glow-template-frontend/blob/37dc3b3ad74104e304643f8270173e7efed38300/src/components/BirthDataFormCanonical.jsx) prevents default form submission and contains a placeholder `// Handle form submission` comment. It does not supply implemented birth-data persistence.

## What may inform new implementation

The legacy sources may inform requirements and new tests where consistent with the current GAPP plan:

- Typed birth-data validation errors and date/time edge cases, from [birth_data_validator.py](https://github.com/amthorn78/glow-backend-v4/blob/1b91efd4777f3b990c7272cdf000dd0b4c44b7b4/birth_data_validator.py) and frontend [src/utils/time.ts](https://github.com/amthorn78/glow-frontend-v2/blob/f0f95ca28f40b39f47624863db1f24373cc3ace9/src/utils/time.ts).
- Secret-presence diagnostics that expose only set/unset status, from [backend/hd_config.py](https://github.com/amthorn78/glow-backend-v4/blob/1b91efd4777f3b990c7272cdf000dd0b4c44b7b4/backend/hd_config.py) and its unit test.
- Writer response contracts, idempotent logout cases and profile update behavior as historical test ideas.

These are reference candidates, not accepted reusable modules. The birth timezone validator checks only nonempty text, and the frontend 12-hour time converter applies modulo 12 before validating the original hour. New implementation must enforce its own current contracts and validate those edge cases.

No compatibility math, authentication/session implementation, migration scripts, environment files, committed databases, dependencies or compiled bundles are copied from legacy sources.

## Ownership and license observations

The connector listed all four repositories under owner `amthorn78` and returned administrative and push permissions. The backend-v4 and frontend-v2 repositories were listed as public; both inspected template repositories were listed as private. Account ownership and connector permissions do not establish the copyright provenance of every included component.

No project-level `LICENSE`, `LICENCE`, `COPYING` or `NOTICE` path was found in the inspected trees after excluding vendored `node_modules`, `venv` and `.venv` contents. This is a filename-inventory observation, not a completed licensing audit. Third-party package license contents, attribution requirements, component provenance and any external licenses were not inspected. No license grant is inferred. Choosing no legacy code copying avoids making reuse depend on unverified provenance; new dependencies still require their own license/attribution review under the implementation plan.

## Validation performed and limitations

Performed: repository discovery, default-branch HEAD reads, complete tree inventory, pinned reads of the relevant source/configuration/schema/test files, and GitHub Actions run queries for the two deployed application HEADs.

No builds, tests, application imports, API calls, database connections, migrations or deployments were executed. No Railway settings, environment values or database contents were read by this bounded GitHub assessment. No external resource was changed.

[tests/conftest.py](https://github.com/amthorn78/glow-backend-v4/blob/1b91efd4777f3b990c7272cdf000dd0b4c44b7b4/tests/conftest.py) imports `app` before its skip fixture and changes the database configuration later. Consequently, the skip-by-default claim in the test README does not prevent import-time initialization against an inherited environment. The test collection was not run.

The HEAD-scoped GitHub Actions queries returned zero runs for backend-v4 and frontend-v2. This provides no current passing CI evidence; it does not establish that the source has never been tested. Historical README or test-script success statements were not treated as results from this assessment.

Live database/role/Redis mappings, current deployment source settings, current consumers beyond observed source references, and third-party licensing remain unverified. This assessment does not grant permission to alter or retire the legacy resources.

## Consequences and next action

The new application can proceed independently of the legacy deployment and unfinished live HDE integration. It must supply its own reproducible setup, maintained authentication machinery, explicit interfaces, current dependency pins, tests and documentation rather than relying on inherited readiness claims.

Complete P01.2 by creating and verifying the selected private application repository, recording its exact identity and initial commit, and transferring documentation authority according to GAPP-PF00/GAPP-PF01. Then establish the reproducible mobile/API base under P01.3. Preserve an isolated, versioned HDE adapter and visibly synthetic development fixtures; neither fixture tests nor temporary storage establish live HDE or PostgreSQL correctness.

## Publication evidence

Private `amthorn78/glow-dating-app` was created and verified through GitHub UI and connector. ID `1383293037`, default branch `main`, initial commit `8131cc7c68c0cfa790d9081e29e45d897f040230`. This assessment and the application canon were published at `ac38e58651e5578ee8503b6423e4884203b42278`. Earlier pending language records assessment-time state.

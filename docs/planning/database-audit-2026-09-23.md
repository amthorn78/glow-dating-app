# 🔎 AB1-DBA-001 — PostgreSQL Audit and Shared-Database Recommendation

Dated audit evidence migrated from [Notion](https://app.notion.com/p/3e44590a05eb81908661fc44eca0ce20?pvs=204) on 2026-09-24. The observations below are from 2026-09-23, not a fresh database inspection. No connection, DDL or role change was performed for the migration. Physical integration remains P11. Future changes must reverify ownership and protect HDE.

> **Outcome:** The existing Railway PostgreSQL target can safely host the new app in the same logical database **only after role/schema isolation is designed and reviewed**. Preserve the complete `hde` schema and `public.hde_body_graphs_current`. Do not reuse the legacy `public` tables as the new app's live store. No database, deployment, repository, or HDE mutation was performed.
## Audit identity
- Audit ID: `AB1-DBA-001`
- Executed: 23 September 2026
- Live database observation: `2026-09-23 16:14:44.342222 UTC`
- Method: browser-hosted Codespaces terminal; Railway CLI plus TLS `psql`; explicit `BEGIN READ ONLY`; `statement_timeout=5s`; `lock_timeout=1s`; `ROLLBACK` before disconnect
- Repository inspected: `amthorn78/glow-hdengine-v2`, local `main` at `db36a8c86070416f7df1e085d594f4ecf3c71cfa`
- Deployed HDE source pin: `aeb256e4245d2d9fc499b03feace91f785f5e4a2`
- Deployed legacy source pin: `520f99aa2e933907a10954dbcabdb29b2e738c05`
- Governing records: [Glow Dating App — Implementation Control](https://app.notion.com/p/3e44590a05eb8118bf02f0dc0c3ea57c) · [Source record](https://app.notion.com/p/3e44590a05eb81ebac0ff50bd1ea6655) · [Source record](https://app.notion.com/p/3e44590a05eb8106b26aea3147dc84bf)
## Verified Railway target
- Workspace: `amthorn78's Projects` — `ae7d1e62-8a2d-4055-b637-ec56536a7239`
- Project: `ample-illumination` — `ce01529f-679f-4f52-a979-23113299a59b`
- Environment: `production` — `a06b149a-2876-40bf-84a0-7880feaf8b67`
- HDE service: `glow-hdengine-v2` — `62e7b993-6d30-48b4-9059-c1884b16e90b`
- Legacy service: `glow-backend-v4` — `bfedf816-d6d4-4155-b495-cd6416e91e49`
- Postgres: `c4d54416-d1ab-4818-898b-9b9be03bc69a`
- Redis: `87b4810c-3e23-4d27-b7fc-0bca7131ed37`
- Both HDE and legacy service probes resolved to the same injected database binding: host `postgres.railway.internal`, port `5432`, database `railway`, role `postgres`.
- Retired bridge variables were absent from both probes.
- Latest HDE deployment: `e181c1c7-15a4-4351-9c75-5123a0c04ee3`, SUCCESS at `2026-09-23T15:04:00.274Z`.
- Latest legacy deployment: `affa8efc-59cb-4ef5-817b-07d1c9232997`, SUCCESS at `2025-10-24T17:28:05.360Z`.
## Live database identity and security posture
- PostgreSQL `17.11 (Debian 17.11-1.pgdg13+2)`
- Database `railway`; session/current user `postgres`
- Search path `hde, public`
- Read-only transaction confirmed `on`
- Schemas: `hde` owner `postgres`; `public` owner `pg_database_owner`
- Current runtime identity is a PostgreSQL superuser with create-database/create-role capability. This is the principal same-database risk.
- Non-login roles exist: `hde_owner`, `hde_rw`, `hde_reader`, `hde_ops03_reader`; the last is a member of `hde_reader`.
- `hde_reader` has SELECT across HDE objects and the legacy public relations. `hde_rw` has SELECT on `hde.meta` and INSERT/SELECT on `hde.chart_snapshot`, `hde.pair_evaluation`, and `hde.public_results`.
- No row-level-security policies were found. No user-defined functions or non-internal triggers were found in `hde` or `public`.
- Only extension: `plpgsql`.
## Inventory result
The live database contains 28 user relations: ten in `hde` and eighteen in `public`.
**Protected HDE objects:** `hde.body_graphs`, `hde.body_graphs_current`, `hde.chart_snapshot`, `hde.meta`, partitioned `hde.pair_evaluation` plus `hde.pair_evaluation_pcur`, partitioned `hde.public_results` plus `hde.public_results_pcur`, `hde.schema_migrations`, and unresolved `hde.test_bridge`.
**Protected public compatibility object:** `public.hde_body_graphs_current`, which depends on `hde.body_graphs_current`, which depends on `hde.body_graphs`.
**Legacy public tables:** `admin_action_log`, `birth_data`, `compatibility_matrix`, `email_notifications`, `human_design_data`, `user_preferences`, `user_priorities`, `user_profiles`, `user_resonance_prefs`, `user_resonance_signals_private`, `user_sessions`, and `users`.
**Legacy sequences:** `admin_action_log_id_seq`, `email_notifications_id_seq`, `user_profiles_id_seq`, `user_sessions_id_seq`, and `users_id_seq`.
There are 13 validated foreign keys, all inside the legacy public model and all targeting `public.users`; none cross schema. There are 13 check constraints, 19 primary keys, five unique constraints, and 43 valid indexes. No invalid indexes were found.
The only migration ledger is `hde.schema_migrations`, containing `011_body_graphs_durability.sql` applied at `2025-11-15 03:52:00.668498+00`. No Alembic, Django, or legacy migration ledger was found.
## Dependency and writer findings
- HDE source migration `005_identity` defines the identity-result tables and partitions. Migration `011_body_graphs_durability` defines `hde.body_graphs`, `hde.body_graphs_current`, and `public.hde_body_graphs_current`.
- Current HDE repository inspection found HDE relation references and the public compatibility view, but no qualified references to the twelve legacy public tables. This is bounded negative evidence: unqualified or dynamically constructed SQL was not exhaustively disproved.
- The deployed legacy service remains a live schema writer/recreator. Its pinned root `app.py` defines the twelve legacy tables, calls `ensure_database`, uses `db.create_all`, and invokes `run_startup_migration`. `migrate_on_startup.py` also calls `db.create_all`, issues `ALTER TABLE` / `CREATE INDEX`, and commits.
- Therefore cleanup cannot begin while `glow-backend-v4` can start or restart.
## Object disposition
### Preserve
- Entire `hde` schema, all partitions, indexes, constraints, data, grants, and `hde.schema_migrations`.
- `public.hde_body_graphs_current`.
- Railway Postgres and Redis services.
- `hde.test_bridge` pending explicit source/ownership evidence; it is not approved for deletion.
### Reuse by contract, not as app-owned storage
- HDE chart/result capabilities through supported HDE interfaces and narrowly granted reads where an approved contract requires them.
- Existing domain concepts such as birth inputs, preferences, compatibility, notifications, and audit history may inform the new app design, but the legacy physical tables must not become the new app's source of truth.
- App account identity and HDE chart identity must remain distinct and be linked explicitly.
### Retirement candidates after prerequisites
The twelve legacy public tables and their five owned sequences are cleanup candidates only after the legacy writer is retired, backup/restore evidence exists, final dependency probes pass, and a separate destructive change is authorized. This audit did not authorize or perform cleanup.
## App model reconciliation
GitHub connector access closed the earlier terminal-credential gap. Private repository `amthorn78/glow-dating-app` was read at current `main` commit [bd701ebfede1630ba162862e053a0a55daea9c9b](https://github.com/amthorn78/glow-dating-app/commit/bd701ebfede1630ba162862e053a0a55daea9c9b). The exact sources are [models.py](https://github.com/amthorn78/glow-dating-app/blob/bd701ebfede1630ba162862e053a0a55daea9c9b/services/api/glow_persistence/models.py), [migration 0001](https://github.com/amthorn78/glow-dating-app/blob/bd701ebfede1630ba162862e053a0a55daea9c9b/services/api/glow_persistence/migrations/0001_event_infrastructure.py), [migration 0002](https://github.com/amthorn78/glow-dating-app/blob/bd701ebfede1630ba162862e053a0a55daea9c9b/services/api/glow_persistence/migrations/0002_app_domain.py), and the [data-model design](https://github.com/amthorn78/glow-dating-app/blob/bd701ebfede1630ba162862e053a0a55daea9c9b/docs/architecture/data-model.md).
The sources contain exactly **32 concrete app models**. Both migrations are unapplied design artifacts. None of their proposed relations exists in the live database. The migration state sets no custom `db_table`, so the names below are Django's default table names; under the recommended app-first migration search path their intended location is schema `app`.
**Exact disposition: all 32 are new app-owned relations if retained in the final P11 design. No model maps to physical reuse of a legacy public table or an HDE-owned table.** Two models form explicit HDE seams but remain app-owned: `EngineIdentity` stores opaque mapping/provenance, and `CompatibilitySnapshot` stores app metadata/revision evidence without an HDE result body, score, or band.
- Event infrastructure: `OutboxEvent`, `WebhookInbox`.
- Account/auth adapter: `AppAccount`, `AccountSession`. Maintained Django/allauth tables are separate dependencies; `public.users` and `public.user_sessions` are rejected.
- Policy/consent: `PolicyRevision`, `ConsentDecision`.
- Profile/preferences: `Profile`, `Preferences`. Legacy profile/preference/resonance tables are rejected.
- Birth/HDE seam: `BirthInput`, `EngineIdentity`, `CompatibilitySnapshot`. Reject `public.birth_data`, `public.human_design_data`, and `public.compatibility_matrix`; consume HDE only through opaque references and an approved contract.
- Media/discovery/matching: `MediaAsset`, `DirectionalInteraction`, `Block`, `Match`, `RecommendationBatch`, `RecommendationEntry`.
- Messaging/notification: `ChatBinding`, `MessageSubmission`, `DeviceRegistration`, `NotificationSettings`.
- Safety/support/audit: `SafetyReport`, `ModerationCase`, `Appeal`, `StaffAudit`, `SupportRequest`. `public.admin_action_log` is not reused.
- Privacy lifecycle/operations: `ExportJob`, `DeletionJob`, `ProviderLifecycleStep`, `DeletionTombstone`, `IdempotencyRecord`, `Entitlement`.
This confirms clean-start storage. Conceptual reuse is limited to domain lessons and supported HDE interfaces; migration ownership remains entirely separate. P11 may still consolidate or remove provisional models through reviewed design changes, but it must not silently redirect them to legacy or HDE physical relations.
## Recommended shared-database architecture
Use a dedicated schema such as `app` in database `railway`.
- `app_owner`: NOLOGIN schema/table owner; migration-only ownership.
- `app_migrator`: controlled deployment role with only the privileges required to create/alter app-owned objects.
- `app_rw`: application runtime LOGIN role with USAGE on `app` and bounded DML on app tables; no CREATE and no ownership.
- Optional `app_reader`: operational read-only role.
- Keep ORM search path app-only where possible and schema-qualify every HDE/public reference. Do not rely on `hde, public` name resolution.
- Grant the app only the exact HDE read/execute capabilities required by an approved interface.
- Remove the shared `postgres` superuser credential from both application runtimes through a separately reviewed production change.
This resolves the main objection to colocation. No current evidence requires a separate logical database; the same logical database is supportable with strict schema/role/migration ownership.
## Cleanup proposal — not executed
1. Verify Railway backup configuration and perform a restore rehearsal to a disposable target.
2. Freeze and retire `glow-backend-v4`; remove its startup DDL path and prove it cannot reconnect or recreate tables.
3. Re-run live dependency, FK, view, trigger, function, grant, lock, and connection checks.
4. Confirm the exact app 32-model mapping and approve the new `app` schema design.
5. Preserve `public.hde_body_graphs_current`; never use `DROP ... CASCADE`.
6. Drop legacy dependent tables in reverse dependency order under a separately authorized change; let owned sequences follow or drop them last.
7. Re-run the HDE catalog, view-resolution, and service health checks.
8. Record the destructive action, backup/restore evidence, row-count disposition, and rollback window.
## Operational observations and limits
- Catalog estimates showed zero live/dead tuples in `pg_stat_user_tables`, while planner estimates suggested small legacy populations (for example users/profiles around five and sessions around thirty). These estimates are stale/unreliable and are not row counts.
- No application or legacy user row was selected, sampled, or counted.
- At observation time the audit session was the only active connection reported; 73 granted AccessShare locks and zero denied locks were observed. Query text was not inspected.
- Backup configuration and restore viability were not verified.
- Railway private DNS was unavailable directly from Codespaces; the supported `railway connect Postgres` path provided the TLS session.
- Railway container SSH was unavailable because no SSH key was configured; no key was created.
- The Codespaces Git credential could not read the private app repository, but the authorized GitHub connector subsequently provided read-only access and closed the 32-model enumeration gap.
## Effects and nonclaims
- Database writes: **0**
- Application/legacy payload row reads: **0**
- DDL, migrations, role/grant changes: **0**
- Deployments, restarts, service configuration, or secret changes: **0**
- Repository file changes, commits, branches, or PRs: **0**
- HDE mutations: **0**
- Environment-only setup: activated the existing virtual environment; installed PostgreSQL client and Railway CLI in the Codespace; completed Railway web login as `nathanamthor@gmail.com`.
- Repository remained clean after the work.
## Decision and next action
**Decision:** Continue with the owner-preferred same-project, same-logical-database architecture, using an app-owned schema and least-privilege roles. All 32 current app models map to new app-owned relations if retained; none should reuse a legacy or HDE physical table. Treat all twelve legacy public tables as retirement candidates. Preserve HDE and its public compatibility view.
**Next action:** carry this verified mapping into the P11 disposable-PostgreSQL design review. Before production DDL, finalize the `app` schema/search-path mechanism, maintained auth/allauth migration dependency, app owner/migrator/runtime roles, backup/restore proof, and legacy-writer retirement plan.

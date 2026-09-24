# Historical source snapshot

Captured for repository continuity on 2026-09-24. Original source: [App-Builder-1-Database-Audit-Plan-and-Prompt.md](https://drive.google.com/file/d/1-AW7Jj_nDnMQiDrLgP0293ZfUuMJScP6/view).

This is historical evidence, not an active assignment or governing prompt library. Current owner direction, repository PF canon and current handoff supersede obsolete Drive, role, next-action and phase-state instructions below. No Drive access is needed to use this snapshot. Recheck dated versions, pricing and provider claims before acting on them.

---

# Glow Database Audit — Plan and Fresh-Session Execution Prompt

**Prompt ID:** AP1-DBA-001
**Revision:** 1.1 — browser terminal route and verified P03 checkpoint
**Issued:** 23 September 2026
**Owner:** Nathan Amthor
**Coordinator:** App Planner 1
**Recipient:** App Builder 1 — dedicated database audit session using browser-based terminal access
**Assignment:** Read-only inventory and dependency audit of the existing Glow PostgreSQL database; produce a concrete shared-database and clean-app-storage recommendation.

## 1. Execute this assignment

You are App Builder 1 in a fresh, dedicated database audit session. App Planner 1 coordinates the Glow Dating App build. Assume no previous conversation, checkout, credentials, processes or local evidence. This document contains your complete assignment and current owner decisions.

Carry out the audit through the **browser-based terminal supplied by Nathan**. This is the primary command-execution route, not a fallback and not a requirement for a native terminal on the agent's own machine. Inspect the actual terminal host; it may be a GitHub Codespaces workspace or a provider console, and these are different environments. Do not assume either until observed. Use available GitHub/Railway capabilities for supported read-only records and Drive/Notion for evidence capture. If Nathan further directs that all inspection use the browser terminal, obey that narrower route while retaining the authorized document-publication destinations.

Do not stop after proposing another audit plan. Complete all supported inspection, preserve evidence and deliver the audit report. A working remote terminal can satisfy command execution even when the agent's local runtime has no CLI, filesystem route or database network access. If access is blocked, finish the source-based analysis and provide the precise missing capability and a resumable checkpoint; never present source definitions as verified live database state.

This is a supporting audit alongside the application workstream. P03 is now complete at preparation scope; P04.1 is the next app task. Do not take over the builder's branch, alter its code, change unrelated task states or restart completed work. Capture sanitized outputs directly to Drive/Notion. Do not create or modify repository files or create a PR. Use inline/stdin query batches without creating files on the terminal host; preserve their exact text in the audit record. Any stricter execution-session no-file-change instruction takes precedence over earlier scratch-file suggestions. Report as **AB1-DBA-001**, checking for an existing report or active audit before publication. Resume already completed inspection rather than launching a duplicate audit.

## 2. Owner decisions and exact authority

Nathan's current direction is:

1. The new application belongs in the same Railway project as HDE.
2. Prefer the **same logical PostgreSQL database** as HDE, with separately owned app schema/tables, unless evidence establishes a strong reason against it.
3. Reuse sound existing structures where useful. Legacy backend/frontend architecture can be discarded or repurposed; preserving their design is not a requirement.
4. The application should start with clean app data. **No user information from the legacy backend/frontend needs migration into the new application.**
5. Preserve the Glow HD Engine, its data, behavior and dependencies. Legacy-data irrelevance does not authorize deleting HDE records or treating HDE data as disposable because an identifier resembles a legacy user.
6. Nathan explicitly requested the schema research now and this handoff to a session with terminal access.

**Authorized now:** verify infrastructure identity and deployed source; use the supplied browser terminal and existing authorized credentials/routes for bounded read-only PostgreSQL catalog inspection; inspect relevant source without executing it; prepare finite inline/stdin queries and private evidence; publish the resulting app audit documents and update the existing Drive/Notion project records. No terminal-host file creation is required by this assignment.

This is a narrow exception to the earlier P03 prohibition on database connections **for this catalog audit only**. P11 remains the phase for application runtime persistence wiring, migration execution and database-dependent application acceptance. Do not defer this explicitly requested audit merely because those later activities remain P11.

**Outside this assignment:** database or application-row writes; deletion, truncation, schema/role/grant changes; migrations; seeding; sequence changes; maintenance; installing extensions; restore tests; production data dumps; changing services, secrets, network exposure, deployment settings or volumes; restarts/deployments; new access keys; HDE/vendor API calls; HDE code/canon changes; Git commits/PRs/merges; retiring legacy services. Do not use the broader app build grant to expand this audit.

“Clean database” means a clean application starting point within the preserved shared database. It does **not** mean resetting the PostgreSQL instance, dropping the database or clearing every object in public. Produce a separate reviewable cleanup proposal. Do not execute it.

Routine authorized inspection and document capture require no further permission. If authentication is genuinely missing, prepare the supported secure sign-in and ask only for the necessary access step. Never ask Nathan to paste passwords, tokens or database URLs into chat.

## 3. Current project context

The new private application repository is [amthorn78/glow-dating-app](https://github.com/amthorn78/glow-dating-app). It contains an Expo/React Native mobile foundation and Django/DRF API.

P01, P02 and P03 are complete at their defined preparation scope. Planner-verified merged app main is now **bd701ebfede1630ba162862e053a0a55daea9c9b**, from [PR 4](https://github.com/amthorn78/glow-dating-app/pull/4), merged 23 September 2026 at 16:03:27 UTC. Accepted candidate **36bb7bd86eede987ef91fc1972f875f6613726d8** and merge share tree **bb9fb2d113a222f418a1ea65e290f6c119df99fd**. All eight candidate checks and all four merged-main jobs passed. See AB1-R004 and AP1-ACK004 in the shared progress record. Recheck for newer work before inspecting the app models.

P02 defined **32 concrete app models and two unapplied migrations**. These are provisional definitions, not evidence of 32 live tables or a commitment to add 32 new tables. Compare them with the existing database before recommending reuse or new storage. Real persistence/authentication/concurrency/live-provider acceptance remains unproven. P03 adds configuration, container/CI and operations preparation; it created no Railway resources or database connections according to the builder's report. Production startup remains refused and readiness remains 503.

P03.1–P03.3 are Done in the verified live control records. P04.1 is the next app task. Repository documents now record the same-project and preferred same-logical-database direction. Earlier separate-project/separate-database defaults in the original P03 prompt must not override these later owner instructions. No completed live database audit has been supplied to App Planner 1 as of this revision; inspect existing audit progress before starting or resuming.

The current P03 target validator refuses the protected Postgres service ID. This is an intentional temporary guard, not a final decision against sharing the database. The audit must supply the object/schema/role evidence for a future reviewed guard that recognizes app-owned scope within the shared service. Do not remove the guard or label the entire Postgres service app-owned during this audit.

HDE owns engine calculations, chart data and compatibility semantics. App accounts and HDE chart identities are distinct concepts; do not assume that a shared user_id name or integer value makes them interchangeable.

## 4. Sources and target identity

Read current repository instructions, relevant project records and supported database procedures before database access. Pin every repository read to a recorded commit; distinguish deployed source from current main. Applicable AGENTS.md files and actual security/access controls remain binding. Use the **glow-hde-devops** skill as supporting guidance for DATABASE_READ, secure Railway access and secret handling when available. It does not turn this app-support audit into an HDE development or change-flow assignment.

| Source | Location |
|---|---|
| App control and latest owner directions | https://app.notion.com/p/3e44590a05eb8118bf02f0dc0c3ea57c |
| P03.1 resource and ownership work | https://app.notion.com/p/3e44590a05eb81ebac0ff50bd1ea6655 |
| Shared progress reports | https://app.notion.com/p/3e44590a05eb81d58971ee4cd870774f |
| App authority D08 | https://app.notion.com/p/3e44590a05eb8106b26aea3147dc84bf |
| Work register | https://app.notion.com/p/71b769915b5b4e00830663770bc95f7e |
| App plan | https://github.com/amthorn78/glow-dating-app/blob/main/docs/pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md |
| Current app handoff | https://github.com/amthorn78/glow-dating-app/blob/main/docs/continuity/current-handoff.md |
| App storage definitions | services/api/glow_persistence/models.py and its migrations in the app repository |
| App architecture and migration documents | docs/architecture/data-model.md; docs/operations/migration-plan.md; docs/operations/resource-ownership.md; docs/adr/0001-isolated-application-foundation.md |
| Protected HDE repository | https://github.com/amthorn78/glow-hdengine-v2 |
| Legacy backend repository | https://github.com/amthorn78/glow-backend-v4 |
| Legacy frontend repository | https://github.com/amthorn78/glow-frontend-v2 |
| Drive project | https://drive.google.com/drive/folders/1MXxJc_6tk-1Kf4QQhoEJPe-3uphKmrC1 |
| Drive audit/research destination | https://drive.google.com/drive/folders/1cZvOmqyN-NeU2BXNUSbHVk9F_LCeSPWS |

The following metadata was read from Railway on 23 September 2026. Resolve names and verify these identities again; do not rely on a terminal's previously linked project.

| Target | Recorded identity |
|---|---|
| Workspace | amthorn78's Projects; ae7d1e62-8a2d-4055-b637-ec56536a7239 |
| Project | ample-illumination; ce01529f-679f-4f52-a979-23113299a59b |
| Environment | production; a06b149a-2876-40bf-84a0-7880feaf8b67 |
| PostgreSQL service | Postgres; c4d54416-d1ab-4818-898b-9b9be03bc69a |
| PostgreSQL volume | aad776ab-27cc-4994-87f0-589af0de7aa1, mounted at /var/lib/postgresql/data |
| Configured PostgreSQL image | ghcr.io/railwayapp-templates/postgres-ssl:17; actual server version still requires live verification |
| Protected HDE service | glow-hdengine-v2; 62e7b993-6d30-48b4-9059-c1884b16e90b |
| Legacy backend service | glow-backend-v4; bfedf816-d6d4-4155-b495-cd6416e91e49 |
| Shared Redis service | Redis; 87b4810c-3e23-4d27-b7fc-0bca7131ed37; preserve |
| Latest observed successful legacy deployment | affa8efc-59cb-4ef5-817b-07d1c9232997, created 24 October 2025; commit 520f99aa2e933907a10954dbcabdb29b2e738c05 |
| Latest observed successful HDE deployment | e181c1c7-15a4-4351-9c75-5123a0c04ee3, created 23 September 2026; commit aeb256e4245d2d9fc499b03feace91f785f5e4a2 |

Both backend and HDE service metadata include a DATABASE_URL variable name. That alone does **not** prove that they use the same logical database, role or search path. The configured Postgres private endpoint is postgres. The actual logical database and connection role remain unverified.

Railway's connector verified metadata but exposed no direct SQL capability. Its agent stated that it could not query pg_catalog/information_schema. A subsequent read-only container-source request timed out with HTTP 504; **no container-file result was verified**. Do not mistake this limitation for a failed PostgreSQL connection or infer that the live schema was audited.

## 5. Existing evidence and traps

These findings are preparation inputs, not live catalog results:

- The supplied Glow Infrastructure reference, PF07 section 2.2, documents one shared PostgreSQL instance and HDE schema hde, with the legacy backend schema unresolved. Its environment inventory is not instruction to point tests at production.
- At the Railway-recorded legacy deployed commit **520f99aa2e933907a10954dbcabdb29b2e738c05**, root app.py defines the 12 tables listed below. Its model names are unqualified; current namespace resolution depends on the actual connection and search path.
- The same deployed source's app.py initialization invokes ensure_database() and run_startup_migration(). migrate_on_startup.py invokes db.create_all(), can ALTER birth_data, create indexes and commit. **Do not import app.py, start Gunicorn/Flask, invoke its initialization or execute migration scripts to inspect schema.**
- src/app.py also exists and differs from root app.py. Do not mix the two model inventories. Verify the actual entrypoint/deployed source.
- HDE's repository contains a historical schema-only snapshot at artifacts/db_discovery/20251113/postgres_schema_only.sql. At pinned HDE commit **aeb256e4245d2d9fc499b03feace91f785f5e4a2**, that snapshot defines these same 12 legacy tables in public, together with HDE objects. It supports a **historical public-schema finding**, not current-schema verification.
- That historical snapshot shows legacy foreign keys to public.users and grants to hde_rw. Ownership fields are omitted. Neither current privileges nor HDE independence is established.
- HDE migration migrations/011_body_graphs_durability.sql defines hde.body_graphs, hde.body_graphs_current, and **public.hde_body_graphs_current**. Treat that public view as an HDE dependency candidate until inspected live. **Never classify every public object as obsolete app data.**
- The historical snapshot lacks the complete later HDE object set. A missing object in that old file proves nothing about today's database.

### Provisional legacy inventory

| Table name | Source-indicated purpose |
|---|---|
| users | Legacy accounts, password hashes, status and admin flag |
| user_profiles | Names, avatar, biography, age and profile completion |
| user_sessions | Legacy session tokens and expiry |
| birth_data | Birth inputs, consent flags and location details |
| human_design_data | Legacy chart/vendor payload storage and expanded HD fields |
| compatibility_matrix | Pair scores and legacy compatibility output |
| user_priorities | Relationship-dimension weights |
| user_preferences | Preference JSON |
| user_resonance_prefs | Versioned weights and facets |
| user_resonance_signals_private | Private derived resonance signals |
| admin_action_log | Administrative actions and user references |
| email_notifications | Notification metadata |

These names are inspection candidates. They are not a deletion allowlist. The owner requires no migration of their user information, but live dependency checks must determine which objects can safely be retired.

## 6. Audit plan

### A. Establish bounded access and evidence

1. Read the latest owner directions/control and applicable repository instructions. Record the session's UTC start, source pins and actual target.
2. Read the browser-control skill available in the execution session and use its supported browser interface to select Nathan's terminal. Verify the visible host/workspace or provider service, connected state, shell prompt, working directory, repository origin/HEAD and clean/dirty status through non-mutating commands. Do not assume the planner's local workspace is the remote host. Use the existing virtual environment where relevant and verified; do not import application startup code. Verify Railway CLI installation/authentication on that remote host if the chosen connection route requires it, and verify a compatible PostgreSQL client. A provider console with an already authorized connection does not require a redundant local Railway login. Existing terminal access is not proof of production connectivity.
3. Prefer existing repository-owned read-only diagnostics after inspecting their source for side effects, provided they do not create files or invoke application initialization. If they do not cover this inventory, prepare finite inline/stdin catalog query batches and record their exact text in Drive/Notion. Do not build an arbitrary SQL executor or run app initialization. Send one complete bounded command at a time; verify that the shell or SQL prompt is ready before typing. An echoed command is not execution evidence. Observe completion, exit status and complete output; paginate/resend only the missing bounded read when terminal scrollback is insufficient. On disconnect or timeout, inspect session state before resubmitting. Do not attach to or terminate an unrelated process.
4. Use an existing authorized connection and the narrowest available privilege. Do not create a role, grant permissions, expose a port, register an SSH key or change settings to obtain access.
5. Keep DATABASE_URL as the sole active database transport input. Use secure child-process injection or the repository-supported connection route on the observed remote host. Do not echo the URL, put its value in argv/transcripts, save .env files or dump environment variables. Browser terminal output, screenshots, clipboard and shell history must not contain secrets. Do not use set -x or display full variable lists. Never query pg_authid/password hashes. When sign-in is necessary, use the advertised secure browser authentication mechanism or Nathan's direct sign-in; credentials stay out of chat and commands. Preserve any already granted installation/sign-in authorization from the execution session instead of requesting it again.
6. Resolve whether backend and HDE point to the same server/logical database by comparing only non-secret connection identity in memory and verifying the resulting database sessions. Do not connect to an unexpected external database if a binding differs; record the mismatch.
7. Use existing approved public/private transport as available. Do not reuse retired bridge variables or bypass network restrictions. Keep HDE runtime rails closed; this catalog task is not permission to enable vendor traffic.
8. Perform only tool setup Nathan has authorized for the observed terminal host. Do not install anything in production containers or create new infrastructure/access keys. Missing tools on the agent's own machine are irrelevant when the browser terminal has them. If the remote host genuinely lacks a required client or login and no existing authorization covers setup, report the exact missing capability and smallest access/setup step. Do not require a complete workstation bootstrap for this bounded read. If secure access still fails, record the sanitized error and resume requirement.

### B. Inspect the live PostgreSQL catalog

For each relevant logical database actually used by the two services on the named Postgres instance, open a short **READ ONLY** transaction. Verify transaction_read_only is on before running the inventory.

Use client startup files disabled where supported; finite connection timeout; transaction-local statement timeout (initially 5 seconds) and lock timeout (initially 1 second); bounded results with pagination if needed. Record actual values. End each transaction promptly. Do not leave an idle transaction open while researching or writing reports. Do not run simultaneous unbounded catalog scans.

Capture:

| Inventory area | Required metadata |
|---|---|
| Connection identity | UTC capture time, server version, logical database, current/session role, search path, transaction read-only state; redact credentials and infrastructure values not needed for identity |
| Database/schema ownership | Relevant database names, schema names/owners, database connection privileges, schema USAGE/CREATE privileges |
| Relations | Every non-system table, partition, view, materialized view, foreign table and sequence; qualified name, object kind, owner, namespace, parent/partition relationship, extension ownership |
| Columns | Names, types, nullability, identity/generated flags, defaults where safe; mark any redacted definition explicitly |
| Constraints/indexes | Primary/unique/check/exclusion/foreign-key constraints, validated state, FK delete/update actions, indexes and their validity |
| Dependencies | Cross-schema FK edges; view/materialized-view dependencies; triggers and referenced functions; function signatures/languages/security-definer and dependency metadata; sequence ownership; extension dependencies |
| Access controls | Relevant role attributes/membership, object/default privileges, row-level security flags/policies and grants; no passwords, user rows or credential material |
| Migration state | Names/structures/ownership of migration tracking objects; only known migration identifiers/versions if a recognized ledger can be read without application data; never run migrations |
| Operational metadata | Catalog/statistics-based size and approximate row/dead-row estimates when available, clearly labeled; aggregate connection/lock information without SQL query text or personal data; backup/restore configuration evidence from existing records if available |

Prefer pg_catalog/information_schema and recognized built-in metadata functions. Do not call application functions, use EXPLAIN ANALYZE, scan app payloads, SELECT *, COUNT(*) on user tables, read session tokens, sample records or extract personal birth/profile data. Read-only SQL is not a license to invoke functions with side effects.

Do not retrieve foreign-server connection options, subscriptions or user-mapping secrets. Catalog comments, defaults, policies and function/view definitions may contain literals: inspect only what is needed and redact secret/personal literals before publication. Record omitted definitions and the resulting limitation. All queries must be saved or identified so results are reproducible.

If a query times out or lacks privileges, record which inventory area is incomplete. Do not silently raise limits, grant access, or call the audit complete. Investigate with a smaller supported read when safe. Capture counts and continuation coverage so capped output cannot be mistaken for a full inventory.

### C. Map consumers, identity and HDE dependencies

1. Compare the live catalog with the **deployed** backend/HDE source and relevant migrations. Record differences from current repository main and historical snapshots.
2. Inspect connection/schema selection, SQL references, ORM mappings, views, functions, startup hooks, scheduled jobs and deployment definitions. Do this statically; do not run either application.
3. Trace dependencies in both directions between HDE and app candidates, including objects in public. Identify roles or default privileges shared between services.
4. Search for source references that PostgreSQL cannot prove, including dynamic SQL, JSON-stored IDs, unqualified table names and IDs passed through API contracts. State where a negative finding has limited coverage.
5. Determine whether legacy integer account IDs and HDE chart/user identifiers refer to the same identity domain. Do not read actual user values to make that determination. Preserve the new app's separate account/chart mapping.
6. Identify any still-running legacy writer or startup hook that could recreate retired tables or write obsolete records after cleanup. Propose how that writer would be retired before later cleanup, without stopping it now.
7. Inspect frontend configuration/source only as needed to locate obsolete backend consumers; do not turn this into a frontend rebuild or exhaustive frontend audit.

Catalog foreign keys alone cannot establish that HDE has no dependency on legacy data. Combine catalog, deployed source and configuration evidence, and retain unknowns.

### D. Produce the reuse and cleanup decision

Classify every relevant object:

- **Preserve — HDE/shared dependency**
- **Reuse structure — new app starts empty**
- **Retire candidate — obsolete app object**
- **New required — no suitable existing structure**
- **Unresolved — further evidence needed**

For each classification record qualified object name, owner, consumers, dependencies, evidence references, confidence/limits and proposed handling. No object may be called safe to delete solely because of its schema, table name, age or the owner's lack of need for legacy user information.

Recommend an app schema/role/migration ownership design within the existing logical database. Name proposed objects as proposed; never imply they exist. Preserve HDE schema, search path, roles and migration ownership. Reusing infrastructure or concepts does not require retaining poor legacy table design. Explain any concrete reason that sharing the logical database would be unsuitable.

Compare the 32 provisional app model definitions against the inventory: map each to reuse/adapt/new/defer, with reasons. Do not force reuse where identity, constraints, security, lifecycle or domain semantics differ.

Prepare a **non-executed cleanup proposal** with exact candidate objects and dependency order, how legacy writers would be retired first, a suitable backup/recovery requirement, expected HDE impact, pre/post checks and remaining owner decisions. Avoid DROP SCHEMA public CASCADE, database resets and broad cascading operations. An unverified backup configuration is not a tested restore.

Separate:
- The decision to bring no legacy user data into the new app, already made.
- The method and timing for removing old objects/data, still requiring a concrete reviewed operation.
- HDE data preservation, unchanged.

### E. Publish and hand back

Capture a private audit package in Drive/Notion with:

1. **Audit report:** conclusions, exact target/source/capture identity, shared logical database finding, scope coverage, live/source/historical distinctions, HDE dependencies, preferred architecture, cleanup proposal and blockers.
2. **Machine-readable inventory:** schema objects, columns, constraints/indexes, dependency edges and ownership/privileges; sanitized JSON/CSV as appropriate.
3. **Reproducible query/command record:** exact inline/stdin catalog query text, sanitized command templates, observed remote-host identity, timestamps, exit codes, row/result counts and terminal truncation/pagination status. No credentials. Terminal screenshots alone do not substitute for complete machine-readable results.
4. **Disposition and 32-model mapping:** may be sections of the report or separate tables.
5. **Continuity checkpoint:** actual completed work, missing access/evidence, next bounded action and artifact links. No executable destructive script is required.

Capture sanitized terminal output through the supported browser interface and preserve it directly in the existing Drive research folder and Notion records listed above. For larger output, use deterministic bounded batches with counts and continuation keys so all records are accounted for. Do not require a file on the Codespaces/provider host, a download route or an agent-local CLI to finish the audit. Document publication may create the requested Drive/Notion artifacts; the terminal-host no-file-change boundary concerns the audit execution environment, not those deliverables. Store user-facing downloadable artifacts persistently where supported, without changing sharing permissions. Hash exact captured bytes when possible; do not claim byte-perfect export from a visual transcription.

Update the existing Notion control/P03.1 and shared report record with a concise result and links, preserving unrelated work and current builder status. Fetch before edits and verify structural edits. If a connector is unavailable, save everything locally/persistently and report that publication as pending. Do not claim another session received or acknowledged the report merely because it was saved.

No app or HDE repository change is needed during this audit. Hand the app builder the exact documents/models that should be reconciled with the findings.

## 7. Completion, limits and final response

The audit is complete only if the relevant live logical database(s), schemas, object/dependency/role inventory and source comparison are actually inspected with coverage recorded. A connection test, old schema file, container listing or successful deployment is insufficient.

Use DATABASE_READ as the effect class. If using the HDE DevOps status convention, distinguish PASS, FAIL_TOOLING, TOOLING_BLOCKED or PARKED for individual checks; include plain-language scope so a partial PASS cannot imply complete database acceptance. Do not claim A02 fully resolved unless identity, ownership and protected-dependency questions are actually answered.

Final response to Nathan and App Planner 1 must state:

- What is verified live and when; whether backend and HDE really share the same logical database.
- What belongs to HDE, what is reusable, and what is only a retirement candidate.
- Whether the preferred shared-database/clean-app design is supported, with specific objections if any.
- Whether any current HDE or shared dependency could be affected by the proposed cleanup.
- Database writes, deployments and legacy user-record reads performed: expected **zero**; report any unexpected deviation candidly.
- Artifact links, unresolved limitations and the exact next step.

Stop after publishing the audit and cleanup proposal. Do not execute cleanup or begin application database integration under this prompt.

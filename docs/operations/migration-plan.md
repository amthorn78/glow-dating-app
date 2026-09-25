# Application migration design and P11 execution plan

This plan covers only separately owned application objects. **No database connection,
SQL execution or migration application has occurred.** The app's development
settings keep the dummy backend and do not install `glow_persistence`.
`glow_persistence.static_settings` exists solely for model metadata inspection.
It is not a staging or production settings module.

## P03 owner direction and audit dependency

> **Superseded in part (25 September 2026; OD-18).** The app gets its own logical database on HDE's PostgreSQL service, with its own roles; see [ADR 0004](../adr/0004-app-database-placement.md). The paragraph below records the earlier same-logical-database preference.

The current [Implementation Control](https://app.notion.com/p/3e44590a05eb8118bf02f0dc0c3ea57c)
records Nathan's preference for clean app storage in the **same logical database
as HDE**, with a separate app schema and restricted app runtime/migration roles,
unless a concrete assessment establishes a strong reason against it. No legacy
user information needs migration. This supersedes a separate-app-database default.
The 32 P02 models and two migrations below are provisional domain definitions,
not authorization to create 32 new production tables or apply the ledger unchanged.

Before selecting physical objects, map existing tables/views to HDE-owned,
reusable app-owned, obsolete app-owned or new-required, compare every provisional
model and record permitted reads/writes, dependencies and one owning migration
system per existing table. Reuse of structure does not require importing old
users. Discarding app architecture is not permission to delete shared objects.
The planner reports documentary HDE schema `hde` and the source-defined
`public.hde_body_graphs_current` object; neither is a verified live catalog, and
`public` is not an app-only deletion boundary.

[Completed database audit](../planning/database-audit-2026-09-23.md) and [catalog/model map](../planning/database-catalog-2026-09-23.md) record the separate read-only inspection on 23 September. HDE and legacy backend used logical database `railway` and privileged `postgres`; preserve HDE objects, including the view in `public`. No existing physical table was approved for reuse by the 32 provisional app models. A clean app-owned schema with restricted roles is the audited direction. No DDL, role/grant change, deletion or wiring was performed. Reverify ownership/capacity and implement isolation at P11; A02 is not closed by this dated audit.

## Committed schema order

| File | Schema responsibility | Dependencies and limits |
|---|---|---|
| `0001_event_infrastructure.py` | `OutboxEvent` and `WebhookInbox`, deduplication, state/time checks and delivery indexes | No app-state table dependency. Durable event infrastructure is defined before any domain state table. No seed data or provider activation. |
| `0002_app_domain.py` | Remaining 30 app models, app FKs, lifecycle/check/unique constraints and declared lookup indexes | Depends on 0001 and the swappable maintained auth model migration. Account/session/consent, policy, profile/birth/media, interaction/match, bounded discovery, chat/devices, safety/support, privacy/tombstones and disabled entitlements. |

These are initial **unapplied** migrations. They were generated from in-memory
`ProjectState` objects by the pinned Django autodetector and reviewed as source;
the first target state contained only outbox/inbox, the second contained all app
definitions. They contain no `RunSQL`, `RunPython`, data import or hidden provider
call. Maintained Django auth/contenttypes migration files are dependencies, not
copied into this application. allauth is not installed or added to this ledger.
See [data model](../architecture/data-model.md) for the exact auth mapping and its
unimplemented normalized-email/linking requirements.

All domain access must remain disabled until the full reviewed ledger is applied
and actual readiness checks succeed at P11. Creating outbox tables first alone
does not enable any feature. Schema ordering is not an outbox durability proof.

## Safe static review now

From `services/api/`, after the hash-locked install:

```bash
GLOW_ENV=test .venv/bin/python -m glow_persistence.static_check
.venv/bin/python -m unittest tests.test_model_definitions -v
.venv/bin/ruff check glow_persistence tests/test_model_definitions.py
.venv/bin/ruff format --check glow_persistence tests/test_model_definitions.py
```

The checker inspects field/model metadata with `databases=[]`, loads migration
files using `MigrationLoader(connection=None)`, creates model states and compares
them using `MigrationAutodetector`. Pinned Django source was inspected: the loader
skips `MigrationRecorder` when its connection is `None`. Django model creation
consults dummy-backend metadata (such as identifier length); that is not a
database connection. Guards reject connection, cursor and schema-editor calls.

Do not use `migrate`, `sqlmigrate`, a migration executor, a database test case,
SQLite or PostgreSQL to make this P02 review easier. Ordinary `makemigrations`
may inspect migration history through a backend; use the reviewed in-memory
mechanism for P02 changes. The checker does not prove an arbitrary management
command safe. Generation never runs SQL and cannot attest a target's real ledger.
No migration command or live-target preflight executor is added in P02.

## P11 target and role isolation

P11 begins only after P10 prerequisites. P11A uses a newly verified disposable
PostgreSQL target, and proves the app's database can move to its own service by
dump and restore; P11B uses staging; P11C uses the app's own logical database and
roles on HDE's PostgreSQL service (ADR 0004) after effect review. Do not turn shared
storage into a fixture. A02's open parts are the capacity and operational-limits
inspection before P11C, the roles' implementation and the legacy disposition.

Before any P11 connection/action, prepare and review a non-secret target manifest:
application repository/candidate and migration files; actual Railway project,
environment, service and volume identities; logical database/schema owner;
runtime and migration role identities; credential references (not values);
connection transport/TLS; migration ledger; backup/restore evidence; retention
and processor obligations; staged rollback bounds. Verify it against current
platform metadata. A familiar hostname or `DATABASE_URL` variable name is not
ownership evidence. Missing/ambiguous identity fails the affected action closed.

The selected shared `ample-illumination` project
`ce01529f-679f-4f52-a979-23113299a59b` will also contain separate app-owned services per the owner’s P03 instruction. Its existing HDE service, colocated PostgreSQL
`c4d54416-d1ab-4818-898b-9b9be03bc69a` and volume
`aad776ab-27cc-4994-87f0-589af0de7aa1` are protected. Revalidate all identities in
[resource ownership](resource-ownership.md) before related work. This is not an
exhaustive allow/deny list: an unlisted resource still needs positive app ownership.
No role credentials, network references, schema permissions or migrations may
affect HDE. D08 does not authorize a protected mutation through a shared resource.

Design separate app migration and runtime roles. Migration role owns only the
isolated app schema and reviewed maintenance privileges; runtime role has only
required app DML and no schema/role/database creation privileges. The HDE role is
never supplied to either. Verify those grants with actual P11 evidence before
applying schema, along with bounded connection pools and statement/transaction
timeouts. WordPress and provider workers do not receive migration credentials.
These are role design requirements; no role or fail-closed target preflight has
been provisioned/implemented by this document.

## Forward changes, backfills and rollback

1. Inspect the real ledger and existing objects. A blank target is not presumed;
   reject unexplained drift and prohibit fake-initial shortcuts or legacy imports.
   No legacy-user migration is required by Nathan's clean-app-data direction.
2. Expand with compatible nullable/additive fields and indexes as appropriate.
   Review PostgreSQL lock behavior at P11. Deploy readers/writers able to tolerate
   the overlap; do not couple feature startup to an uncompleted backfill.
3. Backfill in a separate reviewed migration/job using historical models, bounded
   resumable batches and idempotent checkpoints. Verify counts, invariants and
   quarantined exceptions; backfill secrets/private facts must not enter logs.
4. Validate/enforce new constraints only after compatible writes and backfill
   prove their preconditions. Contract/remove old storage in a later migration
   after the old code's rollback window and data lifecycle requirements expire.
5. Reverting code is not database rollback. Record forward-fix versus restore
   options for each destructive step. Do not unapply 0001/0002 against data-bearing
   storage as a casual rollback: it drops app tables and loses outbox, audit,
   privacy and tombstone evidence. A restore includes deletion replay and processor
   reconciliation; it is not permission to resurrect previously erased accounts.

Maintained auth migration/configuration must be integrated into the same reviewed
P11 ledger after pinning allauth. Verify normalization/case variants, simultaneous
identity creation, verified-email uniqueness, wrong-account linking, token
replay/expiry and real session revocation. `auth.User` metadata by itself proves
none of those requirements. Expected integrity failures map to stable safe API
errors; unexpected programming/schema failures remain visible and unmasked.

## Required later evidence

The central [deferred acceptance matrix](../testing/p11-deferred-acceptance.md)
defines DB01–DB13, PV01–PV08 and PR01. In particular: apply-from-zero and supported
upgrade, direct malformed writes for every check/unique/FK, current policy/pair
locks, simultaneous reciprocal likes, outbox crash/lease recovery and inbox replay,
send-versus-block ordering, actual authentication lifecycle, bounded query plans,
wrong-target/role refusal, deletion provider completeness and backup restore with
tombstone replay. No case is marked passed by a static migration diff.

P11 evidence records exact candidate, target/role identities, actual migration
ledger, commands/results, provider contracts, observed rollback/recovery outcome
and remaining limits. P11C production smoke follows verified staging evidence
and current isolated target checks. Production connection is not public release.

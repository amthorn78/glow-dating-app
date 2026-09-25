# ADR 0004: The app's own logical database on HDE's PostgreSQL service

Date: 2026-09-25
Status: Accepted by Nathan (OD-18). It supersedes the shared-logical-database preference in [ADR 0002](0002-same-project-application-services.md) and OD-03. The rest of ADR 0002, same-project placement, stands.
Work items: A02 and P11. The disposable proof P06.DB (OD-17) uses a CI database, not this one.

## Context

- **The earlier preference (OD-03):** the same logical PostgreSQL database as HDE, with app-owned schema and tables and restricted app roles.
- **The dated audit** of 23 September 2026 found HDE and the legacy backend on logical database `railway`, with the privileged `postgres` role ([database audit](../planning/database-audit-2026-09-23.md)).
- **The Dev Manager's advice:**
  - DM-02 B4 recommended a separate logical database.
  - DM-03 D1 refined it: a separate logical database still shares the platform's restores with HDE, and only a separate PostgreSQL service separates them.
- **Nathan's decision,** 25 September 2026: *"Yes, I support a separate logical database for the app on the same PostgreSQL service as HDE, provided this arrangement has a credible path to scale. Give the app its own credentials and permissions, keep its data separate from HDE's tables, and verify the service's capacity and operational limits. If usage later requires independent resources, the app database should be movable to its own service without redesigning the application."*

## Decision

The app gets its own logical database on HDE's PostgreSQL service, in the same Railway project (ADR 0002). Nathan's conditions are acceptance criteria for P11, and for the P06.DB proof where they apply.

1. **Its own credentials and permissions.**
   - The app has an owner role, a migration role and a runtime role.
   - None of them is `postgres`, and none has any grant on HDE's database. HDE's roles get no grant on the app's database.
2. **Its data kept apart from HDE's.**
   - The app never reads or writes HDE's tables. HDE data reaches the app only through HDE's supported interface (PF01 §5).
   - PostgreSQL does not allow queries across databases, which enforces this structurally.
3. **The service's capacity and operational limits verified before P11C:**
   - connection limits, with a pool budget for each service;
   - storage;
   - backup scope and frequency;
   - maintenance and upgrade coupling.

   This is a bounded read-only inspection under its own assignment (PF01 D08). It has not started.
4. **Movable to its own service without redesign.** Nothing needs to change today:
   - the API opens no database connection, and its fixture guards refuse every database connection name, including `GLOW_DATABASE_URL` and `DATABASE_URL`;
   - the provisional models set no schema, `search_path` or `db_table` prefix (checked on 25 September 2026).

   To keep it movable:
   - P11 gives the app its own connection setting, never an HDE variable;
   - the app depends on no HDE-owned role, extension or object;
   - its migrations are self-contained;
   - P11A proves a move by dumping the app's database and restoring it into a separate disposable instance, with a configuration change as the only application change.

## Accepted residual risk

- A platform restore of the shared service restores HDE and the app together (DM-03 D1). With the move-out path above, that is accepted.
- DB13's restore proof uses a logical restore of the app's database.
- A recovery runbook must not use a platform restore for an app-only incident without a review of its effect on HDE (PF01 D08).

## What stays from ADR 0002

- The app's services and configuration are separate, in the same project.
- HDE is protected by effect.
- No app-only action restores or resets the shared service or its volume.
- The audit's dated facts stay as evidence and are reverified before P11.

## Consequences

- PF01 §4, §6, P11C and A02 describe this placement.
- The migration plan, the resource-ownership record, the domain boundaries and the P11 deferred acceptance cases follow it. The deferred cases gain the move-out case.
- P06.DB proves send-versus-block ordering and sign-in on a disposable CI database, not on this service.

## Revisit when

- the capacity inspection shows the shared service cannot carry the app;
- usage needs independent resources, and the app moves to its own service;
- restores independent of HDE become a requirement.

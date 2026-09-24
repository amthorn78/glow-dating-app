# ADR 0002: App-owned services in the existing HDE Railway project

Date: 2026-09-23
Status: Selected by direct owner instruction; infrastructure activation pending
Work item: P03.1 — Prepare environments and Railway resource disposition

## Decision and authority

During the P03 implementation session Nathan directed: **“the app should be in the same project as the HD Engine”**.

Use the verified existing Railway project `ample-illumination`, ID `ce01529f-679f-4f52-a979-23113299a59b`, in workspace `amthorn78's Projects`, ID `ae7d1e62-8a2d-4055-b637-ec56536a7239`. App services and credentials remain separately owned. The owner's subsequent direction prefers app-owned schema/tables in the **same logical PostgreSQL database as HDE**, with maximum appropriate reuse unless a strong concrete counterargument is established. Do not create a separate Railway project for the dating app.

These directions supersede the separate-project and separate-app-database infrastructure defaults in [ADR 0001](0001-isolated-application-foundation.md), the original P01 [resource assessment](../operations/resource-ownership.md#historical-p01-assessment--preserved-separate-project-disposition-superseded), and the P03 continuation prompt. The fresh application repository/stack, HDE protection, D08 authority, and P11 database-last sequence are preserved. The no-copy foundation was the historical P01 result, not a prohibition on later reviewed reuse under the current owner direction. Historical assessments remain labeled so their observations are not rewritten as current facts.

The owner directions select project placement and a preferred shared logical database. They do not authorize unreviewed production DDL, changes to HDE source/services/settings/secrets/data/roles/volumes/DNS/networking, or shared-consumer effects. PostgreSQL object reuse is now subject to the A02 ownership/dependency audit; protected Redis and the legacy backend runtime are not activated or repurposed by this decision. App Planner 1 coordinates; App Builder 1 implements within D08's effect-based exception.

## Current facts and preparation scope

P03 read-only Railway inventory revalidated the selected project, its sole listed `production` environment and all four existing protected services/volumes. No separate dating-app service was returned. No app resource, environment, domain, volume, deployment or credential was created. Exact protected IDs and source references are in [resource ownership](../operations/resource-ownership.md).

Current API runtime serves development/test fixtures only; staging/production startup is refused and readiness is 503. Mobile production/signing is unavailable. Creating empty cloud services would not make those capabilities ready. P03 therefore prepares build/deploy artifacts and service-specific configuration with activation explicitly pending.

The [environment map](../operations/environments.md) proposes an empty app-specific staging environment in this same project when a real staging runtime exists. Its label is a proposal, not a provisioned identity. App production's environment remains unselected. No HDE production environment is duplicated to initialize app services.

## Shared logical database and object reuse

The latest [Implementation Control](https://app.notion.com/p/3e44590a05eb8118bf02f0dc0c3ea57c) records Nathan's preference for the same logical PostgreSQL database as HDE, separate app-owned schema/tables and maximum appropriate reuse. It also records that legacy backend/frontend user information is irrelevant to this app and requires no migration. Removing the need for a legacy user-data migration does not authorize deletion of shared objects or HDE data.

Before committing a persistence layout, classify existing objects as HDE-owned, reusable app-owned, obsolete app-owned or new-required. Compare the 32 provisional P02 model definitions against the map; do not presume 32 new tables. Define restricted app runtime/migration roles, permitted reads/writes and one owning migration system per reused table. A02 remains open for exact logical database, schemas, roles, dependencies, capacity and shared operational effects.

PF07 v2.3.2 section 2.2 documents a shared instance, HDE schema `hde`, and backend schema TBD. It does not establish the current live logical-database/object map. The control record's historical/source finding of HDE object `public.hde_body_graphs_current` prevents treating `public` as an app-only deletion boundary: no wholesale drop/reset.

[Completed database audit](../planning/database-audit-2026-09-23.md) and [catalog/model map](../planning/database-catalog-2026-09-23.md) record the separate read-only inspection on 23 September. HDE and legacy backend used logical database `railway` and privileged `postgres`; preserve HDE objects, including the view in `public`. No existing physical table was approved for reuse by the 32 provisional app models. A clean app-owned schema with restricted roles is the audited direction. No DDL, role/grant change, deletion or wiring was performed. Reverify ownership/capacity and implement isolation at P11; A02 is not closed by this dated audit.

## Consequences and controls

Railway [private networks](https://docs.railway.com/networking/private-networking/how-it-works) are scoped per project/environment. Separate services in one environment share its private network; different environments remain isolated. Same-project placement does not itself establish a permitted HDE API connection. Supported contract, authentication, data rights and P11 evidence still control that integration.

All eventual app writes specify exact app service and environment IDs. No shared variable, inherited credential, protected volume or project-wide policy is changed. Preferred database reuse must preserve HDE ownership/behavior and be evaluated for shared capacity, lock and recovery effects before executable mutation. Service creation from a repository can trigger deployment immediately, so build/configuration/runtime prerequisites must exist before source attachment. Missing IDs are not replaced with protected IDs or guessed names.

[Current Railway documentation](https://docs.railway.com/infrastructure-as-code) deprecates legacy `railway.json`/`railway.toml` and describes whole-project IaC application that may delete omitted resources. P03 prepares reviewed native service-scoped configuration. It does not run project-wide synchronization, adopt/transfer HDE resource ownership or install an app-only configuration as the desired state of the shared project.

No account-specific budget, subscription tier, app consumption or new resource cost was established. Those facts are recorded for actual provisioning, distinct from published unit prices. No new approval cycle is introduced: app-only provisioning is already authorized when its purpose, prerequisites, exact scope and HDE effects are established.

## Validation and future action

This decision is supported by the direct owner instruction, current read-only inventory, advertised connector scope/side-effect contracts and the linked official platform documentation. It is not deployment, network or production-readiness evidence.

Continue P03 configuration/build preparation and independent application work. Before activation, revalidate live project/environment/service ownership, select the app environment, satisfy runtime prerequisites and apply only the bounded app configuration. The separate catalog audit may run only under its own bounded assignment. App database wiring/migrations and integration follow disposable PostgreSQL, staging and app production at P11. Any action with a possible protected HDE effect remains pending for specific authority.

# ADR 0002: App-owned services in the existing HDE Railway project

Date: 2026-09-23
Status: Selected by direct owner instruction; infrastructure activation pending
Work item: P03.1 — Prepare environments and Railway resource disposition

## Decision and authority

During the P03 implementation session Nathan directed: **“the app should be in the same project as the HD Engine”**.

Use the verified existing Railway project `ample-illumination`, ID `ce01529f-679f-4f52-a979-23113299a59b`, in workspace `amthorn78's Projects`, ID `ae7d1e62-8a2d-4055-b637-ec56536a7239`. New app-owned services, credentials and future persistence remain distinct from protected HDE/legacy resources inside that project. Do not create a separate Railway project for the dating app.

This supersedes only the separate-project infrastructure disposition in [ADR 0001](0001-isolated-application-foundation.md), the original P01 [resource assessment](../operations/resource-ownership.md#historical-p01-assessment--preserved-separate-project-disposition-superseded), and the P03 continuation prompt. The fresh application repository/stack, no legacy code copying, HDE protection, D08 authority, and P11 database-last sequence are preserved. Historical assessments remain labeled so their observations are not rewritten as current facts.

The owner instruction selects project placement; it does not authorize changing HDE source, services, settings, secrets, data, roles, volumes, DNS, networking or shared consumers. Existing Postgres, Redis and `glow-backend-v4` are not app reuse targets. App Planner 1 coordinates; App Builder 1 implements within D08's effect-based exception.

## Current facts and preparation scope

P03 read-only Railway inventory revalidated the selected project, its sole listed `production` environment and all four existing protected services/volumes. No separate dating-app service was returned. No app resource, environment, domain, volume, deployment or credential was created. Exact protected IDs and source references are in [resource ownership](../operations/resource-ownership.md).

Current API runtime serves development/test fixtures only; staging/production startup is refused and readiness is 503. Mobile production/signing is unavailable. Creating empty cloud services would not make those capabilities ready. P03 therefore prepares build/deploy artifacts and service-specific configuration with activation explicitly pending.

The [environment map](../operations/environments.md) proposes an empty app-specific staging environment in this same project when a real staging runtime exists. Its label is a proposal, not a provisioned identity. App production's environment remains unselected. No HDE production environment is duplicated to initialize app services.

## Consequences and controls

Railway [private networks](https://docs.railway.com/networking/private-networking/how-it-works) are scoped per project/environment. Separate services in one environment share its private network; different environments remain isolated. Same-project placement does not itself establish a permitted HDE API connection. Supported contract, authentication, data rights and P11 evidence still control that integration.

All eventual app writes specify exact app service and environment IDs. No shared variable, inherited credential, protected volume or project-wide policy is changed. Service creation from a repository can trigger deployment immediately, so build/configuration/runtime prerequisites must exist before source attachment. Missing IDs are not replaced with protected IDs or guessed names.

[Current Railway documentation](https://docs.railway.com/infrastructure-as-code) deprecates legacy `railway.json`/`railway.toml` and describes whole-project IaC application that may delete omitted resources. P03 prepares reviewed native service-scoped configuration. It does not run project-wide synchronization, adopt/transfer HDE resource ownership or install an app-only configuration as the desired state of the shared project.

No account-specific budget, subscription tier, app consumption or new resource cost was established. Those facts are recorded for actual provisioning, distinct from published unit prices. No new approval cycle is introduced: app-only provisioning is already authorized when its purpose, prerequisites, exact scope and HDE effects are established.

## Validation and future action

This decision is supported by the direct owner instruction, current read-only inventory, advertised connector scope/side-effect contracts and the linked official platform documentation. It is not deployment, network or production-readiness evidence.

Continue P03 configuration/build preparation and independent application work. Before activation, revalidate live project/environment/service ownership, select the app environment, satisfy runtime prerequisites and apply only the bounded app configuration. Actual database connections/migrations follow disposable PostgreSQL, staging and app production at P11. Any action with a possible protected HDE effect remains pending for specific authority.

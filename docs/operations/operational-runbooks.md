# Application operations, secrets and recovery preparation

P03 preparation under GAPP-PF01 D08. These procedures apply to separately owned
Glow dating-app services in `ample-illumination`, project
`ce01529f-679f-4f52-a979-23113299a59b`. No app service, credential, monitoring
account, backup or recovery operation is claimed configured by this document.
Existing HDE, legacy backend, PostgreSQL, Redis and shared/project settings remain
protected. See [resource ownership](resource-ownership.md),
[environments](environments.md), [configuration catalog](configuration.md),
[build/deploy preparation](build-and-deploy.md) and
[provider preparation](providers-and-webhooks.md).

## Ownership and prerequisites

App Builder 1 owns code/configuration preparation and evidence; App Planner 1
coordinates dependencies; Nathan owns unresolved product and operating decisions.
An on-call, security-response, moderation or recovery operator has not been named.
A05 must establish actual operating owners, retention and recovery objectives
before activation. Do not turn those role descriptions into assumed staffing.

Before any future app operation, read the current handoff and verify the exact
repository candidate, project, environment and service against the ownership
record. A non-protected ID is not enough: require positive app ownership. Inspect
pending Railway changes before applying a deployment. If the change set includes
another service or ownership is unclear, stop that operation and preserve the
app-only work. Do not accept all shared-project staged changes as a shortcut.

## Provision credentials without exposing them

1. Establish the provider account, actual permission scope and app-specific
   environment from the provider/access catalog. Resolve A04 only for the needed
   operation. Do not purchase a subscription or infer access from an SDK.
2. Create the least-privilege app credential through that provider's secure
   account interface. Supply it through the service's secret mechanism, scoped
   to the exact app environment/service. Never paste values into chat, PRs,
   Notion, Drive, shell command arguments or committed `.env` files.
3. Never import variables from HDE/legacy services. Never use environment-shared
   variables for app secrets in this shared project. Runtime and migration
   credentials must be distinct; the worker and WordPress receive no migration
   privilege. P03 config definitions are not permission to connect persistence.
4. Record name, purpose, scope, owner, provision/expiry dates when actually known,
   rotation mechanism and non-secret credential reference. Do not record a value,
   token prefix, digest or screenshot that exposes it. Client `EXPO_PUBLIC_*`
   values are public, and the mobile config allows only its reviewed public names.
5. Validate safe presence/type/configuration without printing the environment.
   A placeholder or syntactically accepted profile is not credential validation.
   Test actual rights only in the later authorized provider/P11 scope.

## Rotate an app credential

Determine which app services and environments use the credential from the
recorded inventory. Inspect the provider's current overlap/revocation behavior;
do not assume two keys can coexist or that a key change preserves webhooks.
Prepare a replacement in the secure account interface, update only the verified
app service scope, and validate the named sandbox operation when that integration
is authorized. Revoke the prior credential and verify old access fails. Record
the credential reference, affected service/deployment, time and observed outcome.

If the provider allows no overlap, plan a bounded unavailable interval and
reconciliation rather than silent fallback. Stop dependent workers or leave the
feature unavailable during the interval. Queue/inbox records remain the source
of unfinished work after P11; never claim P03 substitutes preserve queued work.
Do not roll back to a compromised key. Stream's current pure verifier consumes
one configured key/secret pair; swapping that pair invalidates the old signature
in tests, but provider-side rotation remains unproven. Billing stays disabled.

## Suspected credential compromise or private telemetry disclosure

Contain the affected app capability using its verified app-only scope. Stop
dependent app processing if a safe feature control is not implemented; do not
change shared project settings or HDE credentials. Revoke the affected app key
in the provider's secure interface and provision a replacement. If the possibly
affected key/resource is HDE-owned or shared, preserve evidence and give Nathan
the exact proposed protected action rather than performing it under D08.

Preserve minimal restricted incident evidence: time window, safe correlation
IDs, app resource/candidate identity and controlled error codes. Do not copy the
leaked payload into a ticket. Identify exposure through appropriately scoped
provider/account audit capabilities when available; absence of a log is not
proof of no access. Repair the emitting path, rerun sentinel redaction and
authorization cases, inspect a bounded safe sample, and reconcile affected work.
Actual notification duties and retention decisions belong to the accountable
owner; this runbook makes no legal determination or sends messages.

## Deployment and application rollback

Use the selected image/entrypoint and explicit service fields documented in
[build/deploy preparation](build-and-deploy.md). The current container remains a
loopback-only fixture artifact, so it is not a Railway service to make public.
Do not change readiness or enable fixture staging to make deployment succeed.
The health endpoint mapping must stay explicit: liveness proves process response;
readiness remains unavailable until actual required capabilities exist. A
deployment-start probe is not continuous monitoring.

For a later deployable service, verify candidate checks, exact source/artifact
identity, app environment/config compatibility and rollback candidate first.
Apply only the reviewed app service configuration, inspect the resulting build
and deployment, and run the bounded private smoke for the authorized mode.
Do not generate a public domain or invite external users under preparation scope.
Record actual deployment IDs only after the platform returns them.

On failure, first distinguish build failure, startup configuration refusal,
readiness failure, provider outage and application defect. Inspect safe logs and
the exact configuration names/expected modes. Do not dump secrets or disable a
guard. Restore the prior verified app artifact/configuration only when compatible
and record the resulting deployment. No HDE redeploy, shared-variable rollback,
database restore or destructive migration follows from application rollback.
Once P11 persistence exists, schema compatibility and forward-fix/restore options
come from the [migration plan](migration-plan.md), not a Git revert.

## Retry exhaustion and provider reconciliation

The P03 worker interface bounds attempts and time and preserves an operation's
idempotency identity. It is a deterministic synchronous substitute, with no
broker, durable queue, lease, replay store or restart recovery. Its adapter must
honor the per-attempt deadline; it does not forcibly interrupt arbitrary code.
Do not run an always-on worker service merely to demonstrate these primitives.

At P11, an exhausted event remains visible as unfinished in the durable queue or
inbox and requires current authorization/version checks before retry. Determine
whether an external effect may already have occurred; reconcile through the
provider's supported lookup/idempotency contract before resubmitting. Keep the
same logical operation identity. A new correlation ID is allowed and is never
an idempotency or authentication credential. Permanent failures and unrecognized
programming errors require correction, not unbounded retry or synthetic success.

## Backup and restore preparation

No app schema/role or separate app database/volume has been provisioned by this
execution. The app gets its own logical database on HDE's PostgreSQL service
(OD-18, [ADR 0004](../adr/0004-app-database-placement.md)). A platform restore of
that service also restores HDE, so DB13 uses a logical restore of the app's
database, and no runbook uses a platform restore for an app-only incident without
a review of its effect on HDE. No backup schedule, encryption
key, retention duration, PITR, recovery-time objective or recovery-point objective
is configured or asserted. A05 supplies retention and accountable owners; actual
platform capability and cost must be checked on the selected app target at P11.

Prepare P11 DB13 alongside DB01–DB03 and the migration plan:

1. Verify database/volume identity, exact app schema/objects, restricted runtime
   and migration roles, and candidate. With shared storage, a whole-volume
   restore would affect HDE and is outside ordinary app rollback. Define a
   supported app-scoped recovery method and its dependencies before activation;
   never label the shared volume application-owned or reset `public` wholesale.
2. Select and configure the supported app-only backup method with explicit
   retention, encryption/access and recovery objectives. Record an actual backup
   identifier and time only when observed. A platform success label is not a
   restore proof.
3. Restore into a separately verified disposable or staging app target with
   user traffic and provider dispatch disabled. Never restore over HDE or assume
   the newest backup is safe for an application rollback.
4. Verify migration ledger, integrity, ownership/roles and application checks.
   Replay deletion tombstones and revocations before exposing restored state;
   reconcile provider jobs so deleted accounts, devices and channels cannot
   regain access. Test the retained deletion evidence itself survives recovery.
5. Measure the actual recovery duration/data window against the selected
   objectives. Record candidate, backup/restore IDs, tests, discrepancies and
   approved disposition. Only then consider the governed P11C target operation.

DB07/DB08/DB12/DB13, PV01–PV08, PR01, N01 and R01 remain **unexecuted** in the
[deferred acceptance matrix](../testing/p11-deferred-acceptance.md). No local
retry, webhook signature, source build or runbook satisfies their live proof.

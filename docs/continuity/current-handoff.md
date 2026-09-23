# App Builder 1 current handoff

Recorded 23 September 2026 for a **fresh execution session**. Nathan Amthor owns
product/resource decisions. **App Planner 1** coordinates and manages the build;
**App Builder 1** implements and reports to App Planner 1. The current assignment
is **AP1-P04.1-001**, native shell and fixture account/onboarding only. Read the
actual publication and Notion evidence below before treating it as complete.
Assume no earlier chat, local checkout, credentials, processes or dependencies
survive. Do not start P04.2 automatically from this assignment.

## Repository and evidence identity

Private [amthorn78/glow-dating-app](https://github.com/amthorn78/glow-dating-app),
repository ID **1383293037**, default branch **main**. This execution verified main
**bd701ebfede1630ba162862e053a0a55daea9c9b**, tree
**bb9fb2d113a222f418a1ea65e290f6c119df99fd**, and no open PRs before changes.
All **144 baseline blobs** matched that remote tree. P03 is the accepted
preparation checkpoint through [PR 4](https://github.com/amthorn78/glow-dating-app/pull/4),
AB1-R004 and AP1-ACK004; see [P03 evidence](../testing/p03-checkpoint.md).

P04.1 uses branch **app-builder-1/p04-1-native-onboarding**. The containing commit,
its current PR/checks, [P04.1 checkpoint](../testing/p04-1-checkpoint.md), and
**AB1-R005** in the shared progress record identify actual candidate, final merge,
content relationship and main CI. A commit cannot contain its own final hash.
Do not infer passing CI/merge from the existence of this handoff. Current remote
main, all newer commits/open PRs and Notion state must be reconciled before writing.

The accepted implementation on [PR 5](https://github.com/amthorn78/glow-dating-app/pull/5)
is **5fa82a39f595a61d0a13060d06c1ea523e698ded**, tree
**00b0eaae9251e7a7aee37c4c7e435f27d089ef51**. All four Foundation jobs passed in
[PR CI](https://github.com/amthorn78/glow-dating-app/actions/runs/35897572548) and
[branch CI](https://github.com/amthorn78/glow-dating-app/actions/runs/35897565557),
including **39 mobile tests and all seven rendered Chromium cases**. The latter
cover the full fixture journey, recovery, direct/history gates, private draft
isolation and small-screen doubled-text layout. Both native JavaScript exports
passed. The checkpoint records the sanitized artifact, historical failures/fixes
and remaining limits. This final documentation update needs its own candidate
checks; AB1-R005 owns the final hashes, checked merge and merged-main CI.

Publication uses hash-verified source snapshots and GitHub blob/tree/commit
operations. The local synthetic Git baseline is only a diff aid, never remote
lineage. Acquire an authenticated checkout or hash-verify a fresh snapshot. Never
push fabricated history, force-push or reset over unrelated work. Branch protection
was disabled at startup; exact-head/base/diff/check verification is procedural.
Any candidate change, including documentation, needs its applicable checks.

## Authority and startup sources

- Read [AGENTS](../../AGENTS.md), [mobile instructions](../../apps/mobile/AGENTS.md),
  [GAPP-PF00](../pf-canon/GAPP-PF00-Canon-Index-and-Authority.md), current
  [GAPP-PF01](../pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md), especially D08,
  the requested phase and P11.
- [Implementation Control](https://app.notion.com/p/3e44590a05eb8118bf02f0dc0c3ea57c),
  [Work Register](https://app.notion.com/p/71b769915b5b4e00830663770bc95f7e), data
  source `collection://5ea4c24d-ec63-4afb-a434-8969c26b8fbe`; fetch its current schema
  before property writes. [D08](https://app.notion.com/p/3e44590a05eb8106b26aea3147dc84bf)
  owns the grant; Notion owns live task state.
- [Shared reports](https://app.notion.com/p/3e44590a05eb81d58971ee4cd870774f): read
  AB1-R005 if present and all later reports/acknowledgments. Saved is not delivered.
- [P04.1 task](https://app.notion.com/p/3e44590a05eb812db856f1a7221aa464) and
  [AP1-P04.1-001 assignment](https://drive.google.com/file/d/1MyuuEG61ZSiX1EHIP61q5fKsrreO7F_-/view).
- [Mobile README](../../apps/mobile/README.md), [API README](../../services/api/README.md),
  manifests/locks and [Foundation workflow](../../.github/workflows/foundation.yml).
- [Production contracts](../architecture/production-contracts.md),
  [privacy/safety](../architecture/privacy-and-safety-rules.md), F01–F03 in
  `packages/contracts/production/flows-v1.json`, closed schemas/generated validators,
  [fixture architecture](../architecture/onboarding-fixtures.md), and
  [deferred acceptance](../testing/p11-deferred-acceptance.md).

D08 authorizes app-owned GitHub, Railway, Drive and Notion creation/modification,
scoped PRs and checked merges. No routine phase reapproval is needed. It excludes
**every direct or indirect HDE effect**, including shared-resource changes.
Public distribution, outside purchases/contracts, destructive legacy retirement
and person-directed messages remain separate actions. Missing actual access is a
capability boundary; never request secret values in chat.

Repository authority transferred at **ac38e58651e5578ee8503b6423e4884203b42278**.
[Drive project](https://drive.google.com/drive/folders/1MXxJc_6tk-1Kf4QQhoEJPe-3uphKmrC1)
retains historical planning and external sources, not an editable parallel canon.
The HDE canon/change system remains separate and unchanged.

## Implemented fixture scope and retained limits

The mobile shell now includes registration/sign-in, verification/resend,
neutral recovery/reset, adult/consent, private birth input, remaining profile,
restricted states and explicitly labeled development scenarios. Account/session
and onboarding state control Router access and history. Private drafts clear on
account/session changes; stale asynchronous completion cannot grant access.

F01 is a synthetic adapter boundary, not an allauth installation or Glow credential
API. Maintained **django-allauth headless JWT with stateful validation and refresh
rotation** remains the planned production mapping. Only fictional `example.invalid`
accounts and the displayed non-secret fixture password are used. No real email,
credential, token, secure-storage or provider claim is made.

F02 uses explicit fixture clock **2026-09-23T12:00:00Z**, age **18**, leap-birthday
March 1 convention and **development-consent-1**. They are development inputs,
not approved law/terms/policy. A05 still requires actual launch geography and
approved adult/terms/privacy/consent content. Unknown policy, unverified/underage,
stale/withdrawn consent, suspended/deletion state and unfinished profile block
ordinary discovery. The eligible recommendation scenario is a distinct fixture.

F03 uses the existing BirthInput/BirthInputIntent/OwnBirthInput closed contracts.
Known/approximate civil time is preserved; unknown stays null. Timezone and
provenance stay unresolved. Input edits invalidate earlier mapping assumptions.
Pending/ambiguous/unavailable/unsupported outcomes are synthetic. No resolved chart,
engine identifier, geocoding or HDE request is fabricated. Ordinary onboarding ends
at **profile incomplete**; P04.2/P04.3 remain separate.

Restoration is validated same-account/same-session/same-revision synthetic memory
only. No SQLite, browser storage, shadow database, durable process-restart or
cross-device restoration is added. UI gates supplement future server enforcement.
Production OpenAPI still has no active paths. P03 guards, disabled billing,
redacted diagnostics and no-real-provider-fallback behavior remain intact.

The API remains loopback-only development/test GET fixtures with dummy DB backend,
liveness 200 and readiness 503. Staging/production, DB/HDE variables and unsafe
release configurations refuse startup. No deploy job or registry publication is
introduced. Browser rendering and iOS/Android JS exports are distinct evidence;
neither proves signed builds, native device layout, screen readers, secure storage,
actual delivery or production authentication.

## Same-project/database direction and protected boundary

The app belongs in **ample-illumination**, project
**ce01529f-679f-4f52-a979-23113299a59b**. Nathan prefers HDE's same logical PostgreSQL
database with separately owned app schema/roles. No legacy user migration is needed.
The 32 provisional model definitions are not a decision to create 32 tables.

| Resource | Protected identity |
|---|---|
| Workspace | ae7d1e62-8a2d-4055-b637-ec56536a7239 |
| Production environment | a06b149a-2876-40bf-84a0-7880feaf8b67 |
| HDE repository/service | amthorn78/glow-hdengine-v2 / 62e7b993-6d30-48b4-9059-c1884b16e90b |
| Legacy backend | bfedf816-d6d4-4155-b495-cd6416e91e49 |
| Postgres service/volume | c4d54416-d1ab-4818-898b-9b9be03bc69a / aad776ab-27cc-4994-87f0-589af0de7aa1 |
| Redis service/volume | 87b4810c-3e23-4d27-b7fc-0bca7131ed37 / 9ec5ad1f-eab1-4722-ae02-28684aa3b89f |

Protection follows effects and actual dependencies, not this list alone. Do not
change shared/project/environment settings, secrets, networking or existing
services. Future app service/environment/domain/schema/role IDs are unprovisioned.
Same-environment services share private networking; a service ID is not isolation.

The **separate AP1-DBA-001 audit is now complete**, superseding P03's pending note.
Read its [recommendation](https://app.notion.com/p/3e44590a05eb81908661fc44eca0ce20)
and [catalog record](https://app.notion.com/p/3e44590a05eb8182afdaedeebc6796c6).
That report supports database `railway` with reviewed dedicated app schema and
least-privilege roles. Preserve all `hde` objects and `public.hde_body_graphs_current`.
Do not adopt the twelve legacy public tables as app storage. Retirement needs a
separate authorized action after retiring the legacy startup writer, backup/restore
proof and final dependency checks. Never reset the shared database or drop `public`.

The audit's later GitHub read closed its original source-access gap: all **32
provisional models map to new app-owned relations if retained**, with no physical
reuse of legacy or HDE tables. EngineIdentity and CompatibilitySnapshot remain
app-owned seams using opaque references/provenance. This is not final approval of
32 physical tables; reviewed P11 design may consolidate or remove models.

**Remaining audit follow-up:** final schema/search-path mechanism, maintained-auth
migration dependencies, role design, capacity and integration preflight before P11. This P04.1
execution consumed the report without executing SQL or inheriting its early
catalog-connection exception. The current protected-Postgres-service guard remains;
a future audited schema/role-aware guard is required, never a bypass declaring the
protected container app-owned. Do not reuse shared superuser credentials.

## Reproduce and recover

Pins: Python **3.12.14**, Node **24.19.0**, npm **11.9.0**, Expo **57.0.24**, React
Native **0.86.3**, React **19.2.3**. Read current locks and SDK-specific docs first.
Exact install/check commands and observed evidence are in the P04.1 checkpoint.
Use locked pip with hashes; `npm ci --ignore-scripts` in contracts and mobile;
Django checks/tests, Ruff/format/mypy, Python/JS contracts, static model agreement,
mobile check/Expo check/export, root HTTP smoke, rendered Chromium suite and hosted
image smoke. **Never run migrations for this phase.** The new Playwright dependency
is development-only and locked; the license inventory records it.

All four Foundation jobs must pass on the exact final candidate and merged main:
**API checks**, **Mobile checks** (including rendered journey), **API mobile smoke**,
and **API artifact checks**. Final evidence belongs in the checkpoint and AB1-R005.
If interrupted, inspect remote branch/PR first, compare current main and published
head, rerun only concrete remaining checks, then finish eligible publication and
Notion updates. Preserve dirty/unrelated work and never recreate uncertain writes.

## Next work and unresolved evidence

Next existing task after verified P04.1 closure is
[P04.2 — Build profiles, preferences and visibility](https://app.notion.com/3e44590a05eb81c0aef5fb3a705ee88a),
observed Planned, dependency P04.1. P04.3 private media remains Planned. Start the
next task only through its next assignment, with current sources and task state.

A01/A07 need supported HDE contracts/rights/throughput; A02 final reviewed
schema/role design and preflight using the completed mapping; A04 provider/domain/signing access; A05 approved policies
and operational owners; A06 paid scope (disabled); A08 provider chat authorization.
P11 remains disposable PostgreSQL → staging → verified authorized app production
integration. **DB01–DB13, PV01–PV08, PR01, N01 and R01** remain deferred. Fixture tests
do not prove SQL/concurrency, maintained auth, durable delivery, restore, native
signing/device acceptance or release readiness.

Save progress to the existing reports/control/task, address App Planner 1, and
record actual effects and limitations. No direct planner session transport is
verified. Nathan can relay the report; saving does not prove receipt, review or
acknowledgment. No background work is promised.

# App Builder 1 current handoff

Recorded 23 September 2026 for a **fresh execution session**. Nathan Amthor owns
product/resource decisions. **App Planner 1** coordinates and manages the build;
**App Builder 1** implements and reports to App Planner 1. The current bounded
assignment is **AP1-P04.2-001 revision 1.0**: profiles, preferences, public-field
projection and pause/completeness eligibility at fixture scope. Assume no earlier
chat, checkout, credentials, processes or dependencies survive. Do not start P04.3
automatically from this assignment.

## Current P04.2 publication checkpoint

Private [amthorn78/glow-dating-app](https://github.com/amthorn78/glow-dating-app),
repository ID **1383293037**, default branch **main**. This assignment starts from
verified main **4f2708d476d2096cdf7ef8e6062803905aca5915**, tree
**5c8c4baf21afa3cf43d6fda7fdc90ed6c05d32e5**. The scoped branch is
**app-builder-1/p04-2-profiles-preferences-visibility**. Reconcile current remote
main, open PRs, branch and worktree before continuing; this starting identity is
not permission to replace later work.

The current working document records P04.2 implementation scope, not successful
publication. Read [P04.2 evidence](../testing/p04-2-checkpoint.md), the actual
branch/PR checks and the latest Notion records before claiming completion. The
containing candidate, including final documentation, must pass all four Foundation
jobs. The external closure report **AB1-R007 if unused** owns final implementation,
final-candidate and merge hashes, exact tree/parent relationship and merged-main
CI. A commit cannot contain its own final hash. Notion owns the task's actual
In progress → Verified → Done transitions at fixture scope; no pending result may
be reported as Done.

[The complete current assignment](https://drive.google.com/file/d/1xx4gKWhuYAMIeg42nKx2ZG4L0o3MRMXk/view)
and [P04.2 task](https://app.notion.com/p/3e44590a05eb81c0aef5fb3a705ee88a)
are the execution inputs. Live startup reconciliation found AB1-R006 followed by
AP1-ACK006, and no AB1-R007. P04.2 was then set to In progress; P04.3 remains
separate. Recheck the report identifier and task state before saving later updates.

Prefer an authenticated checkout. If publication uses a connector snapshot,
verify blobs/modes against the actual remote tree and create commits with real
remote parentage. Local synthetic history is a diff aid only; never push it,
force-push or reset unrelated work. Branch protection was disabled at the accepted
checkpoint, so inspect current head/base, the complete diff, reviews and required
checks procedurally immediately before merge. Confirm no deployment side effect
has been introduced. Verify merged-main identity and checks after merge.

## Accepted P04.1 baseline and preserved history

P04.1 is **Done at fixture scope** after its initial PR 5 publication was reopened
and corrected by **AP1-P04.1-002**. **AB1-R006** records the correction; **AP1-ACK006**
accepts it. [PR 6](https://github.com/amthorn78/glow-dating-app/pull/6) merged on
23 September 2026 at **18:44:34 UTC**, with final candidate
**0b0a589f114354a4e540e0fc1b7bebdb19dbb750** and merged main
**4f2708d476d2096cdf7ef8e6062803905aca5915** sharing tree
**5c8c4baf21afa3cf43d6fda7fdc90ed6c05d32e5**. Its parents are starting main
**c544b654e0af3e75f31b579f72e5a02e5e577e84** and that final candidate.

All four jobs passed in [final PR CI](https://github.com/amthorn78/glow-dating-app/actions/runs/35904007513),
[candidate push CI](https://github.com/amthorn78/glow-dating-app/actions/runs/35903999794)
and [merged-main CI](https://github.com/amthorn78/glow-dating-app/actions/runs/35904569474).
The accepted historical evidence includes **58 mobile tests and 16 rendered
Chromium cases**. These are baseline results, not a P04.2 test claim.

Preserve all four corrections and recovery behavior:

- Birth drafts reconcile accepted and unsaved facts against monotonic authoritative
  revisions. Stale callbacks cannot restore an older value, including an A→B→A
  date sequence. Ordinary navigation/retry preserves deliberate edits.
- Retained eligibility date and consent reconcile independently. A no-edit Save
  cannot restore an adult date after an underage correction or reaccept withdrawn
  consent. The navigator remains mounted.
- Restricted-session expiry returns to account entry and clears private state;
  the seeded account restriction survives later sign-in/recovery until an explicit
  development scenario replacement.
- Expired challenges remain expired until resend. Wrong-context or delayed work
  cannot consume or expire a replacement. Retryable failures remain retryable.
- Rate-limit → retry preserves the entered recovery email.

The retained eligibility regression proved synchronization/no-edit Save before
Back. Its Back reached exact `about:blank`; a subsequent fresh private entry was
denied. This is not persisted-session or native-history proof. Earlier PR 5 thread
flags remain unresolved; the checkpoint and reports contain evidence-backed
source/regression dispositions rather than treating those flags as correctness.

[P04.1 evidence](../testing/p04-1-checkpoint.md), [onboarding architecture](../architecture/onboarding-fixtures.md)
and AB1-R005/AB1-R006 preserve initial PR 5, correction reproduction, harness
failures, fixes, source identities and acceptance limits. P01/P02 remain complete
at foundation/contract/static-definition scope; P03 remains complete at preparation
scope through [PR 4](https://github.com/amthorn78/glow-dating-app/pull/4), AB1-R004
and AP1-ACK004. See [P03 evidence](../testing/p03-checkpoint.md). Do not restart
completed work from historical unstarted/planning paragraphs.

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
  AB1-R006, AP1-ACK006 and all newer reports/acknowledgments. Saved is not delivered.
- [P04.1 task](https://app.notion.com/p/3e44590a05eb812db856f1a7221aa464),
  [P04.2 task](https://app.notion.com/p/3e44590a05eb81c0aef5fb3a705ee88a) and
  [AP1-P04.2-001 assignment](https://drive.google.com/file/d/1xx4gKWhuYAMIeg42nKx2ZG4L0o3MRMXk/view).
- [Mobile README](../../apps/mobile/README.md), [API README](../../services/api/README.md),
  manifests/locks and [Foundation workflow](../../.github/workflows/foundation.yml).
- [Production contracts](../architecture/production-contracts.md),
  [privacy/safety](../architecture/privacy-and-safety-rules.md), F01–F04/F06 in
  `packages/contracts/production/flows-v1.json`, closed schemas/generated validators,
  [onboarding architecture](../architecture/onboarding-fixtures.md),
  [profiles/preferences architecture](../architecture/profiles-preferences-fixtures.md), and
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
neutral recovery/reset, adult/consent, private birth input, owner profile/preferences
editing and preview, pause/resume, restricted states and explicitly labeled
development scenarios. Account/session and current eligibility control Router
access and history. Private drafts clear on account/session changes; stale
asynchronous completion cannot grant access.

P04.2 uses the existing generated ProfileIntent/OwnProfile,
PreferencesIntent/OwnPreferences and VisibilityIntent contracts. Its fixture port
stages mutations until current response validation/acknowledgment. Draft revisions,
owner/generation context, authoritative object versions and idempotency identities
prevent obsolete work from becoming accepted state. Retained source changes
reconcile fields while preserving unrelated deliberate edits. See the dedicated
[profiles/preferences architecture](../architecture/profiles-preferences-fixtures.md)
for exact policy, ownership, visibility and projection behavior.

Preference policy **development-preferences-1**, dimension **demo_connection**,
and options **demo_a/demo_b** are explicitly provisional editing examples. They do
not select launch geography, gender/orientation taxonomy or production reciprocal
policy. Changed preferences invalidate fictional reciprocal evidence. Ordinary
editing can save an empty biography as an incomplete draft; it does not approve
photos, resolve a chart or grant discovery. Only the explicit fictional eligible
scenario supplies demonstration media/chart/moderation/reciprocal and independent
viewer evidence for visibility tests. Candidate projection is an allowlist with
compatibility unavailable and no live delivery grant; owner preview is not public
visibility. Pause and permission changes invalidate retained recommendations and
pending grant work. Resume rechecks current state and grants no historical contact.

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
at **profile incomplete**. P04.2 adds owner editing without treating text/preferences
as proof of media approval or HDE resolution; P04.3 media remains separate.

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
migration dependencies, role design, capacity and integration preflight before P11. This P04.2
execution consumes the report without executing SQL or inheriting its early
catalog-connection exception. The current protected-Postgres-service guard remains;
a future audited schema/role-aware guard is required, never a bypass declaring the
protected container app-owned. Do not reuse shared superuser credentials.

## Reproduce and recover

Pins: Python **3.12.14**, Node **24.19.0**, npm **11.9.0**, Expo **57.0.24** / SDK
**57**, Expo Router **57.0.22**, React Native **0.86.3**, React **19.2.3**, and
development-only Playwright **1.62.1**. Read current locks and SDK-specific docs first.
Exact install/check commands and observed evidence are in the current P04.2
checkpoint; the P04.1 checkpoint preserves baseline evidence.
Use locked pip with hashes; `npm ci --ignore-scripts` in contracts and mobile;
Django checks/tests, Ruff/format/mypy, Python/JS contracts, static model agreement,
mobile check/Expo check/export, root HTTP smoke, rendered Chromium suite and hosted
image smoke. **Never run migrations for this phase.** The existing Playwright dependency
is development-only and locked; the license inventory records it.

The inherited audit checkpoint recorded **14 moderate findings and zero
high/critical**, across **GHSA-vcc3-ghjq-m6fr** and **GHSA-w5hq-g745-h8pq**. Those are
historical counts, not a new P04.2 audit. Assess compatibility/reachability and
remediate before release; route guards do not neutralize package advisories. Do not
perform a forced broad dependency update as incidental fixture work.

All four Foundation jobs must pass on the exact final candidate and merged main:
**API checks**, **Mobile checks** (including rendered journey), **API mobile smoke**,
and **API artifact checks**. Final P04.2 evidence belongs in its checkpoint and AB1-R007 if unused.
If interrupted, inspect remote branch/PR first, compare current main and published
head, rerun only concrete remaining checks, then finish eligible publication and
Notion updates. Preserve dirty/unrelated work and never recreate uncertain writes.

## Next work and unresolved evidence

After verified P04.2 completion, the expected next existing task is
[P04.3 — Build private media lifecycle](https://app.notion.com/p/3e44590a05eb814aaa84d69bb804768b),
observed Planned at startup with dependencies P04.2 and P03.3. Its exact scope is
upload/quarantine/retry/order/delete flows and authorization cases, with deferred
live proof named. Hand off the current assignment without automatically starting
P04.3; re-read its live register state and next assignment first.

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

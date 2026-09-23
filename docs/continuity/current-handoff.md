# App Builder 1 current handoff

Recorded 23 September 2026 for the next **fresh execution session**. App Planner 1 coordinates; App Builder 1 implements; Nathan Amthor owns decisions. Assignment AP1-P02-001 is checkpointing P02.1–P02.3 at their contract/design/fixture scope. The complete dating app and P03–P12 remain unfinished. Do not assume previous chats, credentials, checkout, virtual environments or running processes survive.

## Verified repository and publication

Private [amthorn78/glow-dating-app](https://github.com/amthorn78/glow-dating-app), ID 1383293037, default branch main. Starting main: **35603603326a8bfbb79b6491b2fef8cc65bc9d6d**, tree **028e018151cfd626d0a147c31f08e6a906699934**; no open PR at startup. All 79 baseline files matched remote Git blob hashes; main was rechecked unchanged before publication.

P02: [PR 3](https://github.com/amthorn78/glow-dating-app/pull/3), branch **app-builder-1/p02-contract-baseline**, implementation candidate **f1a1becebf532eecf3423dceb899177fc46e5cf3**, tree **7f61df38cb0eedc1b5d000291ce278ce6e4fb4a8**. All 55 implementation publication blobs and the complete tree matched the reviewed local snapshot.

Implementation candidate f1a1becebf532eecf3423dceb899177fc46e5cf3 passed [hosted run 35870726962](https://github.com/amthorn78/glow-dating-app/actions/runs/35870726962): API checks, Mobile checks and API mobile smoke all succeeded from clean checkout. Logs confirm 93 API tests (unused database skipped), 36 Python contract methods, 199 JavaScript corpus cases, 11 mobile tests, smoke regression and iOS/Android development export.

This handoff and [P02 checkpoint](../testing/p02-checkpoint.md) are a subsequent documentation commit on PR 3. Their containing final candidate must pass complete checks before merge. Consult PR 3 and the closure report AB1-R003 for the exact accepted head, final run and resulting merge, which cannot be embedded self-referentially in that same commit. Do not infer merge from this file alone. No other P02 PR is required by this checkpoint; fetch current main, PR 3 terminal state and any newer open PRs before editing. Private-repository branch protection remains disabled; use exact-candidate checks and never force-push or overwrite intervening work.

## Authoritative records

- [GAPP-PF00 authority](../pf-canon/GAPP-PF00-Canon-Index-and-Authority.md), [GAPP-PF01 governing plan/D08](../pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md), [AGENTS.md](../../AGENTS.md) and applicable nested instructions.
- [Implementation Control](https://app.notion.com/p/3e44590a05eb8118bf02f0dc0c3ea57c), [Work Register](https://app.notion.com/p/71b769915b5b4e00830663770bc95f7e), data source collection://5ea4c24d-ec63-4afb-a434-8969c26b8fbe.
- [D08 authorization](https://app.notion.com/p/3e44590a05eb8106b26aea3147dc84bf), [shared reports / AB1-R003 closure destination](https://app.notion.com/p/3e44590a05eb81d58971ee4cd870774f).
- [P02.1](https://app.notion.com/p/3e44590a05eb8133a3adc7893aaa9fc5), [P02.2](https://app.notion.com/p/3e44590a05eb8105b68fe2ac0cc0e21c), [P02.3](https://app.notion.com/p/3e44590a05eb81f0886cd333c132da64).
- [AP1-P02-001 assignment](https://drive.google.com/file/d/11i7_NKfsI0g8qqrb2Axy9dpYHnhShcVP/view), [Drive supporting project](https://drive.google.com/drive/folders/1MXxJc_6tk-1Kf4QQhoEJPe-3uphKmrC1). Repository canon is current; Drive plans are historical. Authority transfer ac38e58651e5578ee8503b6423e4884203b42278 remains valid; do not repeat it.

## Completed and unfinished

P01.1–P01.3 remain Done. PRs 1 and 2, accepted candidates, merges and hosted checks are recorded in [foundation evidence](../testing/foundation-checkpoint.md), [domain evidence](../testing/domain-seams.md), and AB1-R002/AP1-ACK002.

P02.1 defines every F01–F20 launch flow, domain/data owner, actor/object scope, projection, transition, error and acceptance case. Versioned gapp-api-v1 schemas, design-only OpenAPI components, generated TypeScript and standalone runtime validators agree under executable checks. Maintained auth interfaces are referenced, not integrated. [Trusted eligibility](../architecture/trusted-eligibility.md) requires server-selected acquisition, ordered pair identity, both participants' versions, policy revision and fresh privileged-action checks. The transition oracle is test-only. See [production contracts](../architecture/production-contracts.md) and [contract evidence](../testing/contract-baseline.md).

P02.2 defines **32 isolated Django models and two unapplied migrations**, with outbox/inbox first. Static checks cover model/migration agreement, constraints/relationships, pair evidence, text bounds and isolation from served settings. [Data model](../architecture/data-model.md) and [migration plan](../operations/migration-plan.md) define UOWs, minimal immutable idempotency receipts with current authorization, after-commit work, privacy/retention, deletion order, target isolation and rollback limits. Actual allauth configuration and email normalization/uniqueness proof remain unfinished.

P02.3 implements internal BirthInput/ChartResolver, CompatibilityProvider/projection, EngineLifecycle and narrow repository/UOW contracts with synthetic adapters. Conformance covers malformed/private/uncertain inputs, identities/versions, ineligible/pending/empty/partial results, typed failures, bounded retries/idempotency, final batch-wide freshness, changed birth mappings and shared-chart/deletion obligations. See [provider design](../architecture/provider-conformance.md), [HDE assumptions](../architecture/provisional-hde-seam.md) and [provider evidence](../testing/provider-conformance.md).

Initial [privacy and safety rules](../architecture/privacy-and-safety-rules.md) preserve unresolved policy inputs. Actual HTTP routes remain development GET fixtures: live 200, readiness deliberately 503, compatibility pending, writes 405. Production schemas have no implemented production routes. No real authentication, persistence, durable outbox/idempotency, SQL/concurrency, live provider/HDE, signed native/device/store or release proof is claimed. [Deferred P11 acceptance](../testing/p11-deferred-acceptance.md) names remaining cases individually.

## Validation and recovery

Linux, Python 3.12.14, Node 24.19.0, npm 11.9.0. Use committed locks and root/API/mobile setup instructions. Final local checks: **93 API/domain/static tests**, **36 Python contract methods** (including the shared corpus as subtests), **199 JavaScript corpus cases**, **11 mobile tests**, deterministic generation, Ruff/format, mypy (17 modules), TypeScript/ESLint, pip consistency, real loopback HTTP smoke/startup regression, and iOS/Android development JavaScript export. Independent scoped reviews reran eligibility 15, provider 29, model 8, Python contract 36 and JS 199 checks and closed findings; these overlap the totals.

Exact commands and hosted evidence: [P02 checkpoint](../testing/p02-checkpoint.md). Expo offline dependency checking is limited; JS export is not signed/device acceptance. Static inspection uses MigrationLoader(None) with connection/cursor/schema guards. Never substitute applying migrations or SQLite/database execution for P02 checks.

Publication used GitHub blob/tree/commit operations from a hash-verified local snapshot. The local synthetic baseline is not remote history. Acquire a fresh authenticated checkout or verified snapshot; never push synthetic lineage. Ignored dependencies/exports are reproducible and noncanonical. Essential source, evidence and recovery links are durable in GitHub/Notion.

## Authority, boundaries and dependencies

D08 authorizes necessary application-owned GitHub/Notion/Drive/Railway writes, scoped PRs and checked merges without routine reapproval. It excludes every direct or indirect HDE effect. Protect repository amthorn78/glow-hdengine-v2 and these Railway identities:

| Resource | ID |
|---|---|
| Shared project | ce01529f-679f-4f52-a979-23113299a59b |
| Production environment | a06b149a-2876-40bf-84a0-7880feaf8b67 |
| HDE service | 62e7b993-6d30-48b4-9059-c1884b16e90b |
| PostgreSQL / volume | c4d54416-d1ab-4818-898b-9b9be03bc69a / aad776ab-27cc-4994-87f0-589af0de7aa1 |
| Redis | 87b4810c-3e23-4d27-b7fc-0bca7131ed37 |
| Legacy backend | bfedf816-d6d4-4155-b495-cd6416e91e49 |

Revalidate ownership/effects before related mutation; absence from the table is not proof of safety. This execution made app GitHub and Notion writes only. Railway inspection was read-only. No HDE/canon/config/data/secret/shared/legacy change, database connection, migration application, real provider/engine call or Railway deployment was performed. CI has no deploy job. A repository-hook inspection was unsupported by the connector; this is an actual-action/configuration account, not a comprehensive hidden-hook or production-history audit.

- A01/A07: supported HDE wire/output/version/cache/deletion rights, recommendation granularity and throughput remain unresolved; keep live adapters disabled.
- A02: shared logical database/role and legacy-data ownership remains unresolved. Prefer isolated app targets; P11 begins with disposable PostgreSQL, then staging, then authorized app production.
- A05: geography/language, preference/rematch/history, moderation/support ownership and retention remain owner inputs. Missing policy fails closed; no final duration or business policy was selected.
- A04/A08: establish actual provider/signing access and chat send/revoke enforcement at their relevant phases. A06: paid scope stays disabled. No new subscription/contract/public release was undertaken.

No new decision blocks this P02 definition checkpoint. Continue independent app work while dependent live actions remain pending.

## Next concrete action

After verifying PR 3 and AB1-R003, start existing [P03.1 — Prepare environments and Railway resource disposition](https://app.notion.com/p/3e44590a05eb81ebac0ff50bd1ea6655). Read GAPP-PF01 P03 and the [resource inventory](../operations/resource-ownership.md), revalidate live identities, then define isolated local/test/staging/production API/worker/Redis disposition, domains, secret ownership and actual access/cost boundaries. Observed P03.1 state is Planned; its historical Drive Plan Reference should be corrected to repository authority when starting. P03.2/P03.3 cover CI/config and secrets/provider observability; foundational CI does not make those tasks Done. Do not attach final persistence or change shared HDE resources.

Each future execution prompt must include full roles, authority, scope, accepted baseline, sources, state, dependencies, acceptance and reporting instructions. No direct App Planner 1 session URL or transport is verified. Consult the shared record for AB1-R003 and its actual saved/delivery state at closure; it is intended for Nathan to relay, and saving does not establish delivery/review. AP1-ACK002 acknowledges only AB1-R002. No background execution is promised.

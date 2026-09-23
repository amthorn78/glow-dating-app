# P02 integrated checkpoint

Observed 23 September 2026. Assignment AP1-P02-001; GAPP-PF01 P02/D08. Scope: P02.1 production design contracts, P02.2 static app data definitions and P02.3 provisional provider conformance. Full app delivery and later-phase acceptance remain unfinished.

## Publication

Starting main **35603603326a8bfbb79b6491b2fef8cc65bc9d6d**, tree **028e018151cfd626d0a147c31f08e6a906699934**. All 79 baseline file hashes matched. No open PR at startup; main remained unchanged before publication.

[PR 3](https://github.com/amthorn78/glow-dating-app/pull/3), branch **app-builder-1/p02-contract-baseline**, implementation candidate **f1a1becebf532eecf3423dceb899177fc46e5cf3**, tree **7f61df38cb0eedc1b5d000291ce278ce6e4fb4a8**. All 55 changed/new publication blobs and the complete tree matched the reviewed snapshot. Most added lines are generated validators, schemas and migration output.

Implementation candidate f1a1becebf532eecf3423dceb899177fc46e5cf3 passed [hosted run 35870726962](https://github.com/amthorn78/glow-dating-app/actions/runs/35870726962): API checks, Mobile checks and API mobile smoke all succeeded from clean checkout. Logs confirm 93 API tests (unused database skipped), 36 Python contract methods, 199 JavaScript corpus cases, 11 mobile tests, smoke regression and iOS/Android development export.

This checkpoint/handoff is a documentation-only follow-up. Its containing final candidate must pass complete hosted checks before merge. Consult PR 3 and closure report AB1-R003 in the [shared progress record](https://app.notion.com/p/3e44590a05eb81d58971ee4cd870774f) for the exact final head/run/merge and tree equality. A file cannot contain its own final commit SHA. Branch protection is disabled; procedural exact-head/base/check/tree verification remains required.

## Local checks actually run

Linux, CPython **3.12.14**, Node **24.19.0**, npm **11.9.0**. Fresh API environment installed requirements-dev.lock with pip --require-hashes; mobile baseline used npm ci --ignore-scripts, then exact-pinned dependency/lock updates. Hosted CI installs both final mobile/contracts locks cleanly. Direct contract tooling pins: json-schema-to-typescript 16.0.0, Ajv 8.20.0, ajv-formats 3.0.1. Inventories record license metadata, not vulnerability/legal clearance.

| Directory | Command | Result |
|---|---|---|
| services/api | GLOW_ENV=test .venv/bin/python manage.py check | No issues |
| services/api | GLOW_ENV=test .venv/bin/python manage.py test tests --verbosity 1 | **93 pass**: original 41, eligibility 15, provider 29, static model 8 |
| services/api | GLOW_ENV=test .venv/bin/python -m glow_persistence.static_check | **32 app models / two migrations agree** without database |
| services/api | .venv/bin/ruff check .; .venv/bin/ruff format --check .; .venv/bin/mypy | Lint/format pass (36 files), 17 modules type-check |
| services/api | .venv/bin/python -m pip check | No broken requirements |
| repo root | PYTHONPATH=services/api services/api/.venv/bin/python -m unittest discover -s packages/contracts/tests -v | **36 methods pass**, including shared 199-case corpus as subtests |
| packages/contracts | npm run check | Deterministic bytes and **199 JS cases pass** |
| apps/mobile | npm run check | TypeScript/ESLint and **11 tests pass** |
| apps/mobile | EXPO_OFFLINE=1 npm run check:expo | Installed pins reported current; offline validation limited |
| apps/mobile | EXPO_OFFLINE=1 npm run export:development | iOS and Android development JS exported |
| repo root | node scripts/smoke.mjs | Spawned API to actual mobile TS client: live 200, ready 503, pending fixtures, writes 405 |
| repo root | node --test scripts/smoke.test.mjs | One occupied-port/startup-failure regression passes |
| repo root | git diff --cached --check | Clean after deterministic generated trailing-newline normalization |

No migrations were applied, including SQLite. Static tests use isolated registries with connection/cursor/schema guards. Auth models appear only in that registry; served settings exclude persistence and keep the dummy database. Expo/Node module-type and environment proxy warnings did not fail checks; no unrelated upgrade was made to suppress them.

## Independent review

Focused and cross-artifact reviews reran eligibility 15, provider 29, model 8, Python contract 36, JavaScript 199 and deterministic generation checks. Counts overlap the combined suites. Corrected findings included staff case/object scope, active-match checks, session revocation, restricted projections, Unicode/date/email consistency, draft profile/birth corrections, device re-registration, targeted media restriction, persisted eligibility revisions, minimal immutable idempotency receipts, after-commit resolver ordering, final batch-wide freshness and schema/storage union bounds. Final scoped review reported no outstanding findings. Fixture checks do not prove production enforcement.

## Limits

- Production OpenAPI has no served paths/servers. Schemas and state oracle define design contracts; only development GET routes exist.
- Static agreement does not prove PostgreSQL constraints/collation/indexes, actual auth/email uniqueness, locks/races, durable outbox/inbox/idempotency, migration rollback or restore. DB01–DB13 remain in [deferred P11 acceptance](p11-deferred-acceptance.md).
- Synthetic provider conformance does not establish HDE wire/output/cache/deletion permission, genuine results, throughput or live enforcement. PV01–PV08 and A01/A07/A02 remain explicit.
- Privacy/provider revocation, signed native/device and release proofs remain PR01, N01 and R01. JS export is development-only.
- No HDE/shared/legacy mutation, database connection, real provider/engine call, Railway creation/deployment, secret read or public release occurred. Only app GitHub/Notion writes publish this work. CI has no deployment job; read-only inspection is not a comprehensive production audit.

The [current handoff](../continuity/current-handoff.md) contains authoritative sources, protected identities, dependencies and the next P03.1 action. Existing Notion tasks own current status; AB1-R003 records final publication and delivery state.

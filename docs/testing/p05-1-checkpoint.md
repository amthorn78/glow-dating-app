# P05.1 reciprocal eligibility checkpoint

**Assignment:** AP1-P05.1-001 revision 1.0. **Scope:** fixture-only app execution.
**State of this checkpoint:** implementation prepared; publication/checks pending;
this record does not claim final-candidate checks, merge, merged-main success or
P05.1 acceptance. Notion owns task state.

## Reconciled source and publication identity

Private repository `amthorn78/glow-dating-app`, ID `1383293037`, default branch
`main`. Starting main `8f9dfbc30e3d0b4568d71482ca7334bf172afafa`, starting tree
`ef115f846ad325f8c1c3a60ecf44d87cadff7ced`; scoped remote branch
`app-builder-1/p05-1-reciprocal-eligibility`. The current remote head and open PRs
must be checked before publication. No synthetic local ancestry may be pushed;
connector publication uses real remote parents and verifies file blobs/modes.

Read-only Notion reconciliation confirmed D08 authority; P05.1 Planned/Autonomous,
with P02.1/P04.2 Done; AP1-ACK008 accepts combined P04 only at fixture scope.
Execution set P05.1 In progress and read it back. P05.2/P05.3 remain Planned.
The supplied prompt equals its published AP1-ACK008 digest: 25,006 bytes, SHA-256
`41a92706e7fe263a9cfee0e428e8da483ee6df15fbd7bd369a10d7d769961727`.
AB1-R009 was unused at startup; recheck before appending to the
[shared report](https://app.notion.com/p/3e44590a05eb81d58971ee4cd870774f).

The containing commit cannot certify its own hash or future checks. The external
closure report owns implementation/final-candidate/merge/tree/ordered-parent
identities, PR and run URLs, review disposition and final state transitions.

## Implementation and conformance surfaces

The [reciprocal fixture architecture](../architecture/reciprocal-eligibility-fixtures.md)
records current source-to-predicate and revision mappings, provisional policy,
clock behavior, corpus and presentation integration. The existing evaluator,
trusted acquisition service, closed contracts and bounded compatibility batch
remain the integration seams. No database adapter, production route, queue,
ranking UI, like, match or contact grant is created by this assignment.

The [current handoff](../continuity/current-handoff.md) is self-contained for P05.1.
The preceding handoff is archived under
[history](../continuity/history/p04-3-handoff.md), with relative links adjusted for
its new directory. The complete historical wording, including embedded P04.2
history, remains; its old imperative next steps are no longer current.

## Observed local setup and independent baseline checks

Observed runtime: **Python 3.12.14, Node 24.19.0, npm 11.9.0**. Committed mobile
pins remain Expo 57.0.24, Router 57.0.22, React Native 0.86.3, React 19.2.3,
Playwright 1.62.1, picker 57.0.19 and loader 57.0.1. These checks were observed
during this session; they do not establish that later eligibility edits pass.

| Directory/scope | Command | Observed result |
|---|---|---|
| Repository, API lock | `.venv/bin/python -m pip install --require-hashes -r services/api/requirements-dev.lock`; `.venv/bin/python -m pip check` | Hash-locked installation and dependency consistency passed. The active virtual environment is at repository root. |
| `packages/contracts` | `npm ci --ignore-scripts`; `npm run check` | Locked install and deterministic generation/checks passed; 212 JavaScript contract cases. |
| `apps/mobile` | `npm ci --ignore-scripts` | Locked install passed. |
| Repository | `PYTHONPATH=services/api .venv/bin/python -m unittest discover -s packages/contracts/tests -v` | 37 Python contract methods passed. |
| `services/api`, root environment | `GLOW_ENV=test ../../.venv/bin/python -m glow_persistence.static_check` | 32 static models/two unapplied migrations agree; database-free check. |
| Repository | `GLOW_SMOKE_PYTHON="$PWD/.venv/bin/python" node scripts/smoke.mjs`; `GLOW_SMOKE_PYTHON="$PWD/.venv/bin/python" node --test scripts/smoke.test.mjs` | HTTP smoke and one startup-ownership regression passed. |
| `apps/mobile` | `npm audit --json` | 14 moderate, zero high/critical findings. GHSA-vcc3-ghjq-m6fr and GHSA-w5hq-g745-h8pq remain release remediation items; guards do not remediate them. |

Counts overlap and must not be added together. Session-local logs preserve the
commands and output under the working evidence directory; they are intermediate
captures, not a replacement for durable CI/report links.

The first root HTTP smoke invocation used its default `services/api/.venv`
location, which was absent. It failed to start before HTTP behavior was exercised.
The existing `GLOW_SMOKE_PYTHON` selector was then set to the actual root virtual
environment and the smoke passed. No runner source change or assertion weakening
was needed. Keep the failed invocation as a tooling/setup event.

Local Chromium installation failed with an invalid archive before any rendered
case ran. Local Docker is unavailable. Hosted Foundation checks must supply
rendered Chromium and container build/config-refusal/smoke/shutdown evidence.
Do not report either local result as a product behavior failure or a local pass.

## Subsequent local implementation checks and review

The full API check after provider additions passed **178 tests** with unused
database setup skipped, plus Django system check, Ruff, format checks for 49
files and mypy for 24 source files. The local mobile check passed **347 tests**,
after immutable-context/projection corrections: 181 inherited tests, 141 shared
raw-fact rows and separate repository/pair integration regressions. These totals
overlap other conformance runs. Final hosted logs still own candidate acceptance.

The local offline Expo compatibility check completed with “Dependencies are up
to date” and its explicit warning that dependency validation is unreliable
offline. `EXPO_OFFLINE=1 npm run export:development` passed on the final local
source and emitted both iOS and Android development JS exports, with exit zero
recorded in `mobile-final-exports.log`. The containing candidate still needs current hosted
checks, including exports. No native build/device
acceptance follows from either command. The existing 47 rendered cases are
preserved; four new cases target retained pair revocation. Their 51-case suite
has not been executed locally because Chromium installation failed.

Independent source review reproduced and corrected four defects before
publication: a later final mapping read could leave an earlier revoked result;
two participants could share profile/asset/source identity; malformed TypeScript
verification facts could be treated as truthy; and a final clock callback could
revoke consent after a candidate's last local source check. Regressions now cover
the final eligibility-only sweep, disjoint identities/runtime fact validation and
post-callback projection guards. Further author/reviewer inspection bound age
and media to the evaluated immutable facts and captured clock, and snapshots
expected context before dependency callbacks. These reviews prove their inspected
source/regression scope, not final hosted review or production transaction safety.

## Required acceptance commands and publication checks

Use the current committed workflow/READMEs and locks. These are **remaining
verification requirements unless an observed result is recorded above or added
below**, not a pass receipt.

| Directory | Required command or check |
|---|---|
| `services/api` | `GLOW_ENV=test ../../.venv/bin/python manage.py check`; `GLOW_ENV=test ../../.venv/bin/python manage.py test tests --verbosity 2` |
| `services/api` | `../../.venv/bin/ruff check .`; `../../.venv/bin/ruff format --check .`; `../../.venv/bin/mypy` |
| Repository | `PYTHONPATH=services/api .venv/bin/python -m unittest discover -s packages/contracts/tests -v` |
| `packages/contracts` | `npm run check`, including deterministic generation `--check` and corpus validation |
| `apps/mobile` | `npm run check`; `EXPO_OFFLINE=1 npm run check:expo`; `EXPO_OFFLINE=1 npm run export:development` |
| `apps/mobile` | `npm run test:rendered`, with Chromium installed in the executing environment |
| Repository | Root HTTP/startup smoke with the actual Python runner |
| Hosted artifact job | `docker build --platform linux/amd64 --tag glow-api:ci --iidfile .work/api-image-id .`; `python3 scripts/container_smoke.py glow-api:ci` |

All four required Foundation jobs, **API checks, Mobile checks, API mobile smoke,
API artifact checks**, must pass for the actual final candidate including docs.
Every later commit needs its own current checks. Review the complete changed
source/contracts/tests/config/docs and actual final-candidate feedback. Wait for
already-running review; record unavailable review coverage and service errors
without relabeling an earlier-head receipt. Immediately before merge reconcile
main/head/base, complete diff, mergeability and reviews/checks; confirm no
production/deployment side effects. After merge verify ordered parents,
candidate/main tree relationship and all merged-main jobs before fixture closure.

## Preserved prior failures, invariants and limits

The [P04.3 checkpoint](p04-3-checkpoint.md), AB1-R008 and AP1-ACK008 preserve PR8's
initial green candidate but failed first main run, late P1 owner-removal
resurrection finding, and PR9's intermediate retained birth failure and final
synchronous draft correction. Not every earlier browser timing cause is uniquely
established. Final PR9 code review completed before merge; automatic security
last completed on the earlier removal repair, with final-head request errors.
That is not a final-head security pass.

P05.1 must preserve all 47 inherited rendered cases and P04.1 source-revision,
recovery and terminal-challenge guards, P04.2 pause/draft/malformed-adoption cases,
PR9 owner-removal versus moderation exclusions and immutable birth edits. Do not
weaken assertions, timeouts or retries to hide races.

## Effects and next boundary

This assignment changes app-owned repository/documentation and existing Notion
execution records only. No database connection, SQL, applied migration, HDE or
live-provider request, Railway/Cloudflare mutation, deployment, production
activation, public release, purchase, legacy retirement or person-directed
message is permitted by its bounded scope. HDE/shared-resource guards remain.

P05.1 is not all of P05. P05.2 discovery queues/pagination/ranking presentation and
P05.3 likes/matches/unmatch remain separate Planned tasks. Eligibility is not
contact/history permission. DB01–DB13, PV01–PV08, PR01, N01 and R01 remain open;
see the [P05.1 carryforward](p11-deferred-acceptance.md). Same logical DB/app-schema
and restricted-role design remain P11 preparation. No fixture completes real
authentication, transaction/concurrency, provider enforcement, durable events,
restore, native signing/device/accessibility or release acceptance.

Next: consult AB1-R009 and current Notion P05.1/Control. If they record fixture
acceptance and checked merge/main evidence, propose P05.2 while P05.2/P05.3 remain
Planned until separately assigned. Otherwise continue the actual branch/PR's
final-candidate review/checks, checked merge and merged-main verification. Save
AB1-R009 if still unused with those final identities/results and recovery/next
instructions for Nathan to relay; saving is not automatic planner delivery or
acknowledgment. Future CI/merge evidence belongs in that external closure report,
not a required self-certifying follow-up commit to this containing checkpoint.

# P05.1 reciprocal eligibility checkpoint

**Current assignment:** AP1-P05.1-002 revision 1.1. **Scope:** fixture-only app correction.
**Current state:** AP1-ACK009 reopened P05.1 for the two final-batch freshness
findings; correction execution set it In progress. Notion owns task state. Final
candidate/merge identities and later check results belong in AB1-R010, if unused,
and the existing task/control records, not a self-certifying containing commit.

The AP1-P05.1-001 sections below preserve the earlier session's observed evidence,
failures and publication state. Their pending/next-action wording is historical
and superseded by the **AP1-P05.1-002 correction checkpoint** at the end. PR10's
eventual successful merge does not close the subsequently reproduced findings.

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

Independent source review in AP1-P05.1-001 reported corrections for four defects before
publication: a later final mapping read could leave an earlier revoked result;
two participants could share profile/asset/source identity; malformed TypeScript
verification facts could be treated as truthy; and a final clock callback could
revoke consent after a candidate's last local source check. Regressions now cover
the final eligibility-only sweep, disjoint identities/runtime fact validation and
post-callback projection guards. Further author/reviewer inspection bound age
and media to the evaluated immutable facts and captured clock, and snapshots
expected context before dependency callbacks. These reviews prove their inspected
source/regression scope, not final hosted review or production transaction safety.
AP1-R009-F01/F02 subsequently established that the final eligibility-only sweep
still left two synchronous callback windows; the current correction below
supersedes any completeness implication of that earlier review statement.

## Initial publication and expected-version correction

[PR 10](https://github.com/amthorn78/glow-dating-app/pull/10) published the first
P05.1 candidate, `f809063cdf2aba236a50db74b349eb36990089bb`, tree
`0e670d5e4de9d2365d71c50696501ec30ab2016d`. Initial
[PR run 35938826828](https://github.com/amthorn78/glow-dating-app/actions/runs/35938826828)
and [push run 35938796359](https://github.com/amthorn78/glow-dating-app/actions/runs/35938796359)
were pending complete hosted evidence, with review also running. No final result
or merge acceptance is inferred from publication.

Independent final source review reproduced an additional TypeScript precondition
defect after that publication. Supplying `false`, `0`, an empty string or `null`
as the expected pair version could be treated like an omitted precondition by
truthiness checks and return `ready`. TypeScript's declared parameter type does
not validate those runtime values. The correction validates every supplied
expected version before invoking the injected clock/dependencies; only omitted
`undefined` means no precondition. A valid precondition has exactly nine own
enumerable data fields, each a nonblank string. Extra/missing/symbol/accessor
fields and malformed values raise the neutral `TypeError` before acquisition;
canonical immutable capture invokes no getter or `toJSON` callback.

The table-driven regression checks every vector field, explicit zero clock/
acquisition calls on malformed inputs, and valid omitted/current/reordered
positive controls. After this correction, `npm run check` in `apps/mobile`
passed TypeScript, ESLint and **348 mobile tests**. This supersedes the initial
347-test local checkpoint for the changed source. Hosted checks/review for the
corrective candidate remain required; the earlier green suite did not establish
this uncovered runtime-input boundary. No candidate2 identity or result is
claimed in this containing update.

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

## AP1-P05.1-002 correction checkpoint

**24 September 2026 UTC · revision 1.1 · fixture-only scope.** AP1-ACK009 preserves
AB1-R009/PR10 completion history and reopens P05.1 for AP1-R009-F01/F02. The current
[Drive correction assignment](https://drive.google.com/file/d/1doBr_chh_fjodNCLbu6yyiCU_TDcUfYB/view)
was retrieved completely and matched the attachment: 31,496 UTF-8 bytes, SHA-256
`431b7a4e048fcb094a7345c9e8ed84ed82da330d5cc3edcd39a6b74202c3da83`.
The existing task was set In progress and read back. P05.2/P05.3 remain Planned.
AB1-R010 was unused at startup; recheck its existing shared report home before
publication. No parallel task/canon is created.

### Reconciled baseline and preserved PR10 proof

Remote main remains `01e834d7f059feb2fcd41bf4c218178206290d04`, tree
`8bf5e31b76620ce284800aca6b1e907c32490738`, at correction startup; no open PR was
present. Direct git authentication was unavailable. All 211 connector-retrieved
file blobs/modes and the complete tree were verified before changes. Local
snapshot history is not remote ancestry; publish only with actual remote parents
and recheck newer legitimate work before any update.

PR10 final candidate `25d8b2bb16a5200f2b952f4dd26e0da6d00c5300` shares that tree.
The merge's ordered parents are `8f9dfbc30e3d0b4568d71482ca7334bf172afafa`, then
the final candidate. Candidate runs
[35939127773](https://github.com/amthorn78/glow-dating-app/actions/runs/35939127773),
[35939123430](https://github.com/amthorn78/glow-dating-app/actions/runs/35939123430)
and [merged-main 35939614030](https://github.com/amthorn78/glow-dating-app/actions/runs/35939614030)
passed all four Foundation jobs. Historical totals were 178 API, 348 mobile,
51 rendered, 212 JS contract cases and 37 Python contract methods, plus both
development JS exports. Counts overlap. The preserved 141-row raw-fact corpus
runs in multiple suites. These results preceded the new findings.

PR10 final-head code review completed before merge. Automatic security completed
only on initial head `f809063cdf2aba236a50db74b349eb36990089bb`; final requests
produced no final-head receipt. No service error or final-head security pass is
asserted for PR10. The current repair must inspect its own final-head reviews.

### Unchanged-baseline reproductions

The supplied appendix ran on the verified unchanged source with Python 3.12.14,
socket creation blocked and no database. The observed JSON was retained as
`python-baseline-reproduction.json` in session evidence for the external report.
It deliberately asserts the old defective output; maintained regressions require
safe behavior instead.

| Run | Observed before method return | Fresh/current comparison |
|---|---|---|
| Unchanged positive control | 14 eligibility/clock reads, 12 mapping reads, two provider calls; both entries evaluated with compatibility | Earlier pair ready; retained/current mapping both `mapping-1`. |
| AP1-R009-F01 | Last later-candidate eligibility acquisition withdrew the earlier candidate's consent; both entries still evaluated with compatibility | Fresh earlier-pair evaluation excluded it. |
| AP1-R009-F02 | Last later-candidate mapping read replaced the earlier link; both entries still evaluated with compatibility | Retained key carried `mapping-1`; current repository held `mapping-2`; fresh eligibility remained ready. |

Both defect runs had the same 14 eligibility reads, 12 mapping reads and two
provider calls as the control. Read counts identify the baseline sequence, not
the future implementation contract. No thread, live provider or SQL was involved.

The corrected reproduction, retained as `python-corrected-reproduction.json`,
uses the participating mapping writer and the same last-read mutation ordering:

| Run | Corrected observed outcome | Preserved control/bound |
|---|---|---|
| Unchanged control | Both entries `evaluated`, both retain compatibility; batch `evaluated` | Fresh first pair ready; retained/current link both `synthetic-mapping-v1`. |
| AP1-R009-F01 | Earlier entry `reload_required`, no compatibility; unaffected later entry `evaluated`; batch `partial` | Mutation fired; fresh first pair excluded. |
| AP1-R009-F02 | Earlier entry `stale`, no compatibility; unaffected later entry `evaluated`; batch `partial` | Mutation fired; current link `mapping-2`; fresh first pair ready. |

Every corrected run retained **14 eligibility/clock reads, 12 mapping reads and
two provider calls**. No extra sweep, acquisition, provider replay or retry was
used to close the demonstrated final-return window.

### Correction and bounded publication design

`fixture_coherence.py` provides concrete revision cells and immutable captures.
The fact repository's per-account cells advance on participant put/removal and
outgoing block observations; its shared policy/time cell advances on policy
writes and observed day/availability changes. The new fixture account–chart-link
repository advances retained per-account cells on every `put`, including removal,
same-value replacement and restoration. Guards remain bound to the original
attempt across retries and provider calls.

The batch retains real callback-capable reads and current exclusion diagnostics.
After the last read, one pure concrete-cell/integer comparison suppresses retained
compatibility when a participating source changed: fact/policy/time changes
become `reload_required`; mapping changes become `stale`. Unaffected outcomes
remain available; a shared-viewer or policy/time change invalidates every dependent
pair. No denied attempt is promoted after restoration. Missing/malformed/
unavailable guard participation fails closed before provider dispatch. No clock,
repository, provider, custom getter/equality/hash or new retry follows acceptance.
The existing cap remains twenty candidates and one to three total provider
attempts. This is synchronous fixture coherence, not PostgreSQL atomicity.

Maintained tests use named final-acquisition/final-mapping phases and actual source
writes in both batch orders. They cover earlier-candidate and shared-viewer
consent/block/media/policy changes; input/mapping/identity replacement; same-value
restoration; unavailable/malformed guards; guard-acquisition callbacks; continuous
change; positive controls and unchanged denied-provider ordering. Existing retry,
idempotency/provenance and truth-table coverage remains required.

Corresponding mobile inspection reproduced final-clock profile-adapter policy,
media, preference and profile writes retaining an obsolete preview; a `toJSON`
context substitution bypass; and a supplied Date method mutating facts after
capture. Private factory-adapter revisions, media-binding revisions, strict
descriptor-only context capture and one numeric timestamp capture before source
facts address these paths. The last preview acceptance check uses only local
revision/identity comparisons and returns `null` on invalidation. Real MediaStore
writer participation and restoration have focused regressions. There is no
presentation change requiring new rendered cases; all 51 existing cases remain.

Independent review then reproduced a same-value `MediaStore.seedEligible()`
reset that suppressed its evidence notification. The reset now invalidates that
notification signature so the existing profile synchronization path observes the
new source incarnation. A dedicated final-clock regression covers the real
writer. The intermediate 361-test mobile pass preceded this correction and is
not the final local mobile result.

### Observed current-session setup and independent gates

These results were observed during correction setup; they do not certify a later
candidate containing source or documentation changes.

| Check | Observed result |
|---|---|
| Runtime pins and hash-locked Python install | Python 3.12.14, Node 24.19.0, npm 11.9.0; root `.venv` hash-locked install and `pip check` passed. |
| Workspace installs | `npm ci --ignore-scripts` passed in mobile and contracts; no package upgrades. |
| JS contracts and generation | `npm run check` passed 212 cases and deterministic generation `--check`. |
| Python contract checks | 37 methods passed. |
| Static model agreement | 32 models/two unapplied migrations agree; no database. |
| Root HTTP/startup smoke | Passed using `GLOW_SMOKE_PYTHON` set to the root `.venv`; startup regression passed one test. |
| Expo compatibility | Offline check reported dependencies up to date, with its explicit unreliable-offline-validation caveat. |
| Dependency audit | 14 moderate, zero high/critical; GHSA-vcc3-ghjq-m6fr and GHSA-w5hq-g745-h8pq remain pre-release remediation items. |
| Local rendered/container capability | Chromium install failed with an invalid ZIP before tests; Docker executable unavailable. Hosted jobs must supply these results. |

After the source corrections, these local commands also completed successfully:

| Directory / command | Observed corrected-source result |
|---|---|
| `services/api`: `GLOW_ENV=test ../../.venv/bin/python manage.py check`; `GLOW_ENV=test ../../.venv/bin/python manage.py test tests --verbosity 2` | No Django issues; **189 API tests passed**, unused database setup skipped. |
| `services/api`: `../../.venv/bin/ruff check .`; `../../.venv/bin/ruff format --check .`; `../../.venv/bin/mypy` | Passed; **51 files** satisfy format checks and **25 source files** pass mypy. |
| `apps/mobile`: `npm run check` | TypeScript, ESLint and **362 mobile tests passed**, including the final MediaStore reset regression. |
| `apps/mobile`: `EXPO_OFFLINE=1 npm run export:development` | Both iOS and Android development JS exports completed with exit zero. This is not native build/device acceptance. |

The new Python suite adds eleven methods, including **120** final-read mutation
combinations (64 eligibility and 56 mapping). The prior provider/fact/trusted
checks and all 141 corpus rows remain. Counts overlap and are not an aggregate
coverage total. Source review and focused regressions supplement these results;
the external report records the exact reviewed candidate and any unavailable
automatic review coverage.

All four required Foundation jobs still must pass on the actual final candidate
including docs and on merged main. Hosted rendered/container results and those
future identities are not asserted here. Candidate evidence alone does not close
the correction.

### Current publication, effects and next action

Use scoped branch `app-builder-1/p05-1-batch-freshness-correction`; verify actual
remote branch/head/PR before uncertain writes. Review the complete delta and
actual final-head feedback, wait for an already-running review, and state missing
coverage precisely. Immediately before merge verify current head/base/main,
mergeability, review disposition, all four Foundation jobs and absence of
deployment/production effects. After merge verify exact SHA, ordered parents,
candidate/main tree relationship and all merged-main jobs. These future identities
belong in the external report, not a containing-commit attestation.

Changes are app fixture source/tests/docs and existing Notion records. No database
connection, SQL, applied migration, live HDE/provider call, Railway/Cloudflare
mutation, deployment, production activation, public release, purchase, destructive
retirement or person-directed message is part of this correction. Read-only
Railway metadata showed HDE/legacy/PostgreSQL/Redis services and no app service
in the shared project; it grants no right to mutate protected resources.

Finish AP1-P05.1-002 and its observed gates, then update/read back existing P05.1
In progress → Verified → Done **at fixture scope**, Control and addressed report
**To App Planner 1 · AB1-R010 if unused**. AB1-R009's earlier closure is insufficient.
P05.2 remains the next proposed task only after this repair, for stable bounded
queues, accessible browsing, freshness/empty/error states, permitted output
granularity and independently authorized actual candidates. P05.2/P05.3 remain
Planned and unstarted. P07 WordPress and P11 database/live/native proofs remain
separate. Saving a report is not delivery to another ChatGPT session; Nathan can
relay it. Before interruption publish recoverable source and record actual remote
head/PR, unpublished files, completed checks, blocker and one next action.

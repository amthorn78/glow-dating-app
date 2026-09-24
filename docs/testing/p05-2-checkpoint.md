# P05.2 recommendations and broader discovery checkpoint

**Assignment:** AP1-P05.2-001 · **Revision:** 1.0 · **Date:** 24 September 2026 UTC.
This record covers fixture implementation and observed validation. It cannot
certify its containing commit's future review, merge or final-main checks.
[Shared reports](https://app.notion.com/p/3e44590a05eb81d58971ee4cd870774f),
[Implementation Control](https://app.notion.com/p/3e44590a05eb8118bf02f0dc0c3ea57c)
and the [P05.2 task](https://app.notion.com/p/3e44590a05eb813cb49ac1612e0f8710)
own exact external publication identities and current execution state.

## Verified baseline and execution start

Starting main is `c229d3df9a8fe05157b125b189667bbf872a0d7c`, tree
`f3857142151a3f1776b134fc7316d7a9730e6915`, in private
[amthorn78/glow-dating-app](https://github.com/amthorn78/glow-dating-app),
ID 1383293037. No open PR existed at startup. The scoped remote branch
**app-builder-1/p05-2-discovery** was created at that baseline before source
publication. Terminal Git authentication was unavailable; all **213** pinned
baseline blobs, modes and the complete tree were verified after GitHub-tool
retrieval. The local reconstructed snapshot is not remote ancestry and must not
be pushed. Remote publication uses the actual remote parent and verified tree.

The task was set In progress on actual execution start at
`2026-09-24T03:20:46.166Z`; readback verified the task at `03:21:02.392Z` and Control
at `03:21:27.147Z`. P05.1 and P02.3 are dependencies; P05.1's fixture acceptance is
recorded by AB1-R010/AP1-ACK010. P05.3 remains Planned and is outside this assignment.
The [historical handoff](../continuity/history/p05-1-handoff.md) preserves the prior
correction assignment; its old next steps are superseded by
[the current handoff](../continuity/current-handoff.md).

Accepted P05.1 baseline evidence is **189 API tests, 37 Python contract methods,
362 mobile tests, 212 JavaScript contract cases and 52/52 rendered Chromium
cases**, plus both development JavaScript exports and HTTP/container/startup
checks. These counts overlap and are not P05.2 results. PR12's final candidate
`24a0101068b9957e18671b83eeb1aacffa4f3e8a` and accepted main have identical trees;
main's ordered parents are PR11 merge `5390b9a75cf6f1ec1bbdaf2a2fa36fd3841c556e`,
then the PR12 candidate. Accepted final-main
[run 35946924910](https://github.com/amthorn78/glow-dating-app/actions/runs/35946924910)
passed all four Foundation jobs. PR12 final-head code/security completion was
verified in its [receipt](https://github.com/amthorn78/glow-dating-app/pull/12#issuecomment-5806265962).
No earlier review certifies P05.2 changes.

Preserve failed first PR11 main
[run 35944199382](https://github.com/amthorn78/glow-dating-app/actions/runs/35944199382),
mixed diagnostic runs and the unmerged diagnostic branch at
`6ad567c4b4048aeaea31b62f5df5061cc26cd30c`. The focus negative control failed on
unchanged behavior and passed after the web correction; the original failed run
had no original trace, so its precise chronology remains unproven. Historical
PR10 security review limits remain recorded in the P05.1 evidence.

## Implementation and acceptance map

The [discovery architecture](../architecture/discovery-fixtures.md) owns the
implemented data path and policy rationale. Python composes existing trusted
eligibility/provider seams; TypeScript is an explicit in-memory presentation
substitute checked against the same source corpus and closed contracts. The
anonymous GET remains layout/smoke data and no production discovery route is
activated. Finite recommended and broader queues replace modulo cycling.

The synthetic policy is two cards per page, at most twenty selected/retained
candidates, two mode queues, a five-minute lifetime and the existing maximum
three total provider attempts. Recommended sorts fixture priority then profile ID;
broader sorts profile ID. Both apply identical eligibility/disclosure rules to
the same population. A mode switch preserves each mode's own progress; refresh
replaces only that mode's queue. These choices record neither HD ranking nor
launch capacity, pass/like intent or resurfacing approval.

| Boundary | Required evidence and review focus |
|---|---|
| Per-candidate authority | Shared raw-fact positive/excluded controls, both preference/block directions, missing facts/policy, malformed/wrong pair; explicit zero mapping/provider calls for initial rejection |
| Finite queues | Multiple pages, synthetic tie order, no duplicates per queue, exhaustion, independent mode progress, refresh invalidating former handles |
| Continuations/adoption | Malformed/expired/stale/cross-viewer/cross-session/wrong-mode handles; idempotent repeated reads and delayed refresh/mode/account response rejection |
| Bounds | Bounded scan/retention/provider/retry work under mostly excluded input and provider failure; no refill loop |
| Final publication | Later-candidate callback mutates earlier eligibility/link/projection; callback-free final guard removes stale output, with shared-viewer invalidation and unchanged controls |
| Source incarnation | Replacement/removal/restoration, media loss, policy/time, existing strict version/getter/clock guards; no old queue revival |
| Disclosure | Only current allowlisted fields/approved-media projection; no birth, email, location, preferences, block reasons, engine identities or raw provider body in page/cursor/UI |
| Product/regression | Both modes, loading/partial/pending/empty/exhausted/error/reload/manual refresh, small-screen controls and ordinary onboarding blocked; all inherited 52 browser cases retained |

Tests with explicit outputs/call counts and independent review are required.
This table is an acceptance map, not an assertion that listed tests passed.
The containing source's exact test files and observed outcomes are recorded
below when executed; final candidate/main runs belong in the external report.

## Observed environment setup and capability limits

| Check | Observed result |
|---|---|
| Python and locked install | Python **3.12.14**; a fresh `services/api/.venv` installed `requirements-dev.lock` with `--require-hashes`; `pip check` passed. |
| JavaScript pins/install | Node **24.19.0**, npm **11.9.0**; `npm ci --ignore-scripts` passed for mobile and contracts. No dependency upgrades. |
| Fresh dependency audit | **14 moderate, zero high/critical advisories**. Audit exited 1 for findings, not a scan error. GHSA-vcc3-ghjq-m6fr and GHSA-w5hq-g745-h8pq remain pre-release remediation items. |
| Local Chromium | Installation failed with invalid ZIP central directory, exit 1; no local browser executable and **no rendered case ran locally**. Hosted Mobile checks must supply rendered evidence. |
| Local container capability | No Docker executable. Hosted API artifact checks must supply container build/startup/smoke evidence. |

The audit is current session evidence; runtime guards do not neutralize these
advisories. Dependency remediation remains a pre-release obligation and is not
silently expanded into P05.2. JavaScript export is not signed native acceptance.

## Observed implementation checks

The contract work's focused checks completed before the final combined candidate.
`packages/contracts`: `npm run check` passed deterministic generated-byte checking
and **302 JavaScript shared contract cases** (212 inherited plus 90 discovery
cases). The **37 Python contract methods** passed, including the same shared
corpus. A separate direct trusted-Python check matched the independently specified
expected state for every one of the **14 discovery candidates**. Counts overlap;
these focused results do not certify later source edits or final-main behavior.

The rendered suite adds **17 discovery cases**, for **69 collected cases across
five files**. The inherited 52 cases remain unchanged. ESLint for
`rendered/discovery.spec.ts`, `npm run typecheck` and
`npm exec playwright test -- --list` passed locally. Test collection is not browser
execution: none of these 69 cases ran locally because Chromium installation failed.
Hosted execution remains required on the final candidate and actual merged main.

The shared provider-state/attempt oracle additionally passed **21 mobile
conformance cases**, with mobile type checking and focused lint. The 13 Python
discovery methods were rerun against the same page-state/attempt expectations.
Synthetic ready/pending are ready pages; typed unavailable is one attempt/partial;
the declared transient outage is at most three attempts/partial. These counts
overlap the combined suites.

Before initial candidate publication, corrected source passed the following
combined local gates. Python used the fresh `services/api/.venv` runner:

| Check | Observed result |
|---|---|
| Django system check and `manage.py test tests --verbosity 2` | No system issues; **203 API tests passed**, including 14 discovery methods with parametrized cases. The unused default database was explicitly skipped. |
| Python contracts | **37 methods passed**, including shared DTO cases. |
| Ruff lint and format | Passed; **54 files** satisfy format checking. |
| Mypy | Passed on **27 source files**. |
| Static model/migration check | **32 models / two unapplied migrations** agree; no database access or applied migration. |
| Actual API HTTP smoke | Liveness **200**, readiness **503**, development recommendations **200** under guarded fixture startup. |
| Deterministic generation and JS contract suite | Passed; **302 shared contract cases**. |
| Mobile `npm run check` | TypeScript, ESLint and **407 tests passed**: 362 inherited plus 45 discovery cases. |
| Expo dependency compatibility | `EXPO_OFFLINE=1 npm run check:expo` reported dependencies up to date, with its explicit warning that offline validation is less reliable. The online attempt failed with a proxy timeout; it is not a passed online check. |
| Actual API-to-mobile HTTP smoke and smoke ownership negative control | Passed using the explicit Python runner; configured transport response validation and guarded startup remained intact. |
| Both final development JavaScript exports | iOS and Android completed with **exit 0** after the Metro correction and last source edits. These are development bundles/assets, not signed native builds. |

Counts overlap and must not be added into a coverage total. These results cover
the inspected local source; subsequent changes require affected checks again.
Subsequent hosted execution exposed the focus defect recorded below. These local
results do not certify its later correction or final-main behavior.

## Preserved intermediate findings

The first local development JavaScript export failed before producing both
platform outputs: Metro could not resolve the canonical shared discovery JSON
outside `apps/mobile`. That is a bundler/source-resolution failure, not a native
device failure or a failed HDE/provider call. The correction extends the matching Expo Metro defaults with one watch folder
for `packages/contracts/fixtures`, retaining a single authoritative source. Both
platform exports then passed, including the final rerun after the last source
edits. The failed first run remains part of this session's evidence. Successful
TypeScript/Node checks alone did not establish bundle resolution.

Further backend review tightened closed-contract text checks, including BOM-only
values, and distinguished unavailable provider output from wrong-pair/provenance
and other rejected provider evidence. The later focused discovery suite passed
**14 methods**, including real bound-result identity/provenance controls and
every declared provider failure code. The earlier intermediate combined run contained 202 API tests; the final
203-test run above supersedes that count.

## Independent implementation review and corrections

Independent review examined the complete discovery service/composition/tests,
mobile adapter/store/context/screen, eligibility/provider coherence, profile
capture changes and additive closed schema. It reviewed uncommitted working
source and recorded core SHA-256 fingerprints for attribution. It is not a
remote-head automated review receipt or production security acceptance.

| Independently reproduced negative control | Before correction | Corrected behavior and evidence |
|---|---|---|
| R1: final profile-clock callback advances lifetime past five minutes after its earlier observation | Returned a partial page with two cards at time 300001, although immediate currentness check was false | Registered concrete lifetime cells and a final primitive comparison return `reload_required`, zero cards and no cursor. Same-day final-callback regression and independent rerun pass. |
| R2: retained display ignores a null fresh authority capture without a source write | Fresh capture was null while `isCurrent(page)` returned true | Fresh non-null actor/session acquisition is required before the retained-cell comparison. Independent rerun returns false; maintained regression covers the missing-source path. |
| R3: Python projection accepts a BOM-only display name despite the closed text contract | Ready page with two cards failed schema validation | Projection/capture reuse the existing explicit Unicode whitespace rule. Corrected result is a schema-valid partial page with zero cards; BOM-only name/summary cases pass. |

Other source findings corrected during implementation include bounded selection
before materialization, post-await authority checks before provider work, shared
viewer revocation before a later candidate, concurrent same-page reuse, removal
of private viewer facts from retained queue metadata, focus-aware retained route
activation, exact pending-cursor recovery, retained queue-creation clock guards,
bounded provider replay/diagnostic storage and aligned provider outcome/retry
semantics. The review also tightened malformed request/mapping identity handling
and distinguishes typed provider unavailability from rejected pair/provenance.
These source findings are distinct from the three executed negative controls.

Pre-publication independent focused verification passed **45/45 mobile discovery cases**
(24 source/race and 21 shared conformance), **14/14 Python discovery methods**
and `git diff --check`. The final narrow delta included bounded mapping/input/
reference fields, exact provider version binding, null-authority and expiry-timer
regressions. That initial working-source disposition had **no remaining concrete findings**;
subsequent hosted execution and automatic review found the issues below. A first reviewer command with an incorrect interpreter path
exited 127 without running tests; the corrected explicit command passed.

The remote candidate still needs its own automated review/check disposition.
Preserve the local negative controls and intermediate bundler/check tooling
failures in the external report; no earlier-head review is promoted to final-head
coverage. Any later source delta requires corresponding review.

## Initial publication and hosted focus finding

[PR 13](https://github.com/amthorn78/glow-dating-app/pull/13) published initial
candidate `3986df82a0acf0d64e3f04522c1f1718863cdd32`, tree
`353cc0c0a093726ff89b866f3c7c08cbc93c015f`, with actual parent
`c229d3df9a8fe05157b125b189667bbf872a0d7c`. All 37 changed blobs/modes and the
complete tree were verified. This is published source, not an accepted merge.

The initial [PR run 35952863749](https://github.com/amthorn78/glow-dating-app/actions/runs/35952863749)
and [branch run 35952862408](https://github.com/amthorn78/glow-dating-app/actions/runs/35952862408)
failed in **Mobile checks only**. The PR's API, API mobile smoke and API artifact
jobs passed: actual logs confirmed 203 API tests, 37 Python contract methods,
Ruff/mypy results, loopback responses, rejected writes, the port-ownership
negative control and built-container validation. Those passes do not override
the failing required Mobile gate.

[PR Mobile job 107484926075](https://github.com/amthorn78/glow-dating-app/actions/runs/35952863749/job/107484926075)
executed **68/69 browser cases successfully**: all 52 inherited cases and sixteen
of the seventeen new cases passed. The new 320px enlarged-text keyboard case in
`rendered/discovery.spec.ts` failed its retained-focus assertion at line 289.
Pressing Enter on Next page loaded page two, but disabling the focused control
during loading lost its keyboard focus. The application behavior requires a
correction; the existing assertion, test count, timeouts and retry policy remain.
Local browser installation remains unavailable, so corrected rendered behavior
must be established on the revised hosted candidate.

Both automatic reviews completed on the **initial candidate**: security at
`2026-09-24T03:50:37.126889Z` and code at `2026-09-24T03:53:14.477455Z`, as
recorded in the [review receipt](https://github.com/amthorn78/glow-dating-app/pull/13#issuecomment-5807202791).
Security had no posted findings. Code review raised
[P2: terminal-page publication revision](https://github.com/amthorn78/glow-dating-app/pull/13#discussion_r4089715629):
`isCurrent` did not compare queue revision when a page had no next cursor, so a
later change to an earlier/excluded candidate could retain obsolete terminal
membership/completion metadata. Initial-head review completion closes neither
that finding nor the browser failure and does not cover the correction head.

### Prepared correction and observed delta verification

The focused web `NextPageButton` uses a native HTML button with `aria-disabled`
and an activation handler that refuses work when disabled. It remains focusable
during loading and exhaustion, without programmatic refocusing or focus theft
from another screen. The native implementation delegates to the existing shared
Button; unrelated/native controls and the PR12 scroll fix are unchanged. The
original 69-case browser suite, including its failed focus assertion, remains
unchanged. This is a reviewed source correction; hosted rendering on the revised
candidate is still required to prove it fixes the observed behavior.

The terminal-page correction captures the current source revision when each page
is published and requires that revision for **every** retained page, including
terminal pages. A partial page constructed during a candidate mutation binds the
new publication revision while retaining only unchanged candidate guards; the
next source write invalidates it. Independent R4 reproduction followed the three
recommended pages and performed a same-value replacement of the excluded paused
candidate. Before correction, the terminal Lena/Noor page remained current
(`before: true, after: true`). The corrected probe returns `after: false`. Three
new regressions cover terminal changes and the safe partial-page distinction.

After this five-source-file correction, `npm run check` passed lint/types and
**410 mobile tests** (362 inherited plus 48 discovery cases). Independent narrow
review passed **48/48 discovery cases** (27 source/race plus 21 conformance),
repeated the terminal-page probe, checked the scoped focus mechanism and reported
no remaining concrete correction findings. Both corrected iOS/Android development
JavaScript exports completed with **exit 0**. The Python/contract source was
unchanged by this correction. No local browser test ran.

The correction needs verified publication on the existing PR, renewed final-head
code/security review disposition and all four Foundation jobs. Do not attribute
the earlier review receipts or 68/69 result to the correction candidate. The
external report records its exact head, complete tree and future hosted outcomes
without asking this containing commit to certify itself.

## Required validation and checked publication

Use actual committed scripts and locked dependencies. This session's explicit
Python runner is `services/api/.venv/bin/python` from repository root, or
`.venv/bin/python` inside `services/api`.

| Location | Command or required check |
|---|---|
| `services/api` | `GLOW_ENV=test .venv/bin/python manage.py check`; `GLOW_ENV=test .venv/bin/python manage.py test tests --verbosity 2` |
| `services/api` | `.venv/bin/ruff check .`; `.venv/bin/ruff format --check .`; `.venv/bin/mypy`; `GLOW_ENV=test .venv/bin/python -m glow_persistence.static_check` |
| Repository | `PYTHONPATH=services/api services/api/.venv/bin/python -m unittest discover -s packages/contracts/tests -v` |
| `packages/contracts` | `npm run check`, including deterministic generated-byte verification and both shared validation corpora |
| `apps/mobile` | `npm run check`; `EXPO_OFFLINE=1 npm run check:expo`; `EXPO_OFFLINE=1 npm run export:development` |
| Repository | `GLOW_SMOKE_PYTHON=services/api/.venv/bin/python node scripts/smoke.mjs`; `node --test scripts/smoke.test.mjs` |
| Hosted mobile | `npm run test:rendered` with installed Chromium, including all 52 inherited cases and the added discovery suite |
| Hosted artifact | Existing pinned Docker build and `python3 scripts/container_smoke.py glow-api:ci` |

All four required Foundation jobs must pass on the **actual final candidate,
including documentation**, then again on actual merged main: API checks,
Mobile checks, API mobile smoke, API artifact checks. Verify final head/base/main,
complete diff, mergeability, review dispositions and checks before the authorized
merge. Wait for running review; state errors or unavailable coverage exactly.
After merge verify ordered parents, complete candidate/main tree relationship and
final-main job outcomes. A candidate pass never certifies merged main.

Exact final candidate, PR, reviews, merge/main, run/job links and final test counts
belong in AB1-R011 (or the next unused report ID) on the existing shared report
page. Its external placement avoids a self-certifying documentation/CI loop.
Nothing in this checkpoint declares an unobserved future review/check/merge passed.

## Effects and remaining work

The bounded assignment changes app fixture source/tests/docs and existing project
records. It opens no database connection, runs no SQL/applied migration or live
HDE/provider call, and makes no Railway/Cloudflare mutation, deployment, production
activation, public release, paid activation, real-user import or legacy retirement.
HDE/shared resources and the completed audit's findings remain protected.

A01/A05/A07 and the [P11 matrix](p11-deferred-acceptance.md) remain open for their
actual integration/operating evidence. In-process counters do not prove persisted
authentication, database transactions, multi-process invalidation, provider rights,
throughput, durable delivery, restore or native/device/release acceptance.

After all P05.2 closure gates, update/read back its existing task **Verified →
Done at fixture scope**, update Control and save the addressed report **To App
Planner 1**. Saving is not automatic delivery or planner acknowledgment. The next
proposed separate task is **P05.3 — Implement likes, matches and unmatch**; it
remains Planned until assigned. P05, P06, P07 and P11 are not completed here.

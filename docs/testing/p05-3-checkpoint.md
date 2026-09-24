# P05.3 interaction fixture checkpoint

**Assignment AP1-P05.3-001 revision 1.0 · 24 September 2026 UTC.**
This checkpoint records observed source and validation. It does not certify its
own future remote checks, review, merge or final-main results. Exact final
identities belong in AB1-R012 on the [shared reports](https://app.notion.com/p/3e44590a05eb81d58971ee4cd870774f).

## Starting evidence and environment

Verified current main `833408ab3e04ad4f649e71ca0483e606806dddbb`, full tree
`5ec516752b591e6b9f558d7fa50241a08b31576f`, no open PR or prior P05.3 branch.
All 231 blobs and file modes match the pinned remote tree. Terminal Git clone
failed for unavailable credentials; GitHub tools remain available. Local snapshot
history is synthetic and must never be pushed. Scoped remote branch
`app-builder-1/p05-3-interactions` was created from the real starting main.

Live records confirmed accepted P05.1/P05.2 and P02.2 at their stated scopes,
P05.3 Ready, P06.1 Planned and A05 policy unresolved. P05.3 was set In progress
and read back; Control now records actual execution. The Library and Drive
assignment texts agree, with only an extra trailing newline in the Drive text
fetch. Accepted baseline counts overlap: 203 API tests, 37 Python contract
methods, 410 mobile tests, 302 JavaScript contract cases and 69 browser cases.
They are not results of P05.3 validation.

An explicit fresh Python **3.12.14** venv was created at `services/api/.venv`.
Hash-locked requirements installation and `pip check` passed. Node **24.19.0** and
npm **11.9.0** match pins; `npm ci --ignore-scripts` passed for mobile/contracts.
A fresh `npm audit --json` completed: **14 moderate, zero high/critical**
advisories. This is current dependency evidence; pre-release remediation remains
required and no dependency migration is included in P05.3.
The actual local Chromium install failed before test execution because the
returned browser archive was invalid/truncated. Docker is absent. Hosted browser
and container jobs are required; collection/export is never reported as execution.

## Initial validation observations

`EXPO_OFFLINE=1 npm run check:expo` exited 0 with dependencies up to date; the
command warns that offline dependency validation is less reliable. No lock or
package version changed. Actual root loopback API/mobile smoke passed with the
absolute venv interpreter, confirming liveness 200, readiness 503, deterministic
pending fixtures and mutation 405; the port-ownership negative control passed.
An initial invocation used a relative interpreter path, which the child resolved
from `services/api` and could not start. The corrected absolute runner passed;
this was a runner-path error and required no source change.

The contract/static slice passed deterministic generation, **373 JavaScript
shared cases**, **38 Python contract methods**, **9 static-model tests**, scoped
Ruff and database-free model/migration equality. These are intermediate results
for that slice, not final combined-source or hosted evidence.

## Complete local validation and review

The complete combined source passes the existing commands:

- API: `GLOW_ENV=test .venv/bin/python manage.py check` and
  `GLOW_ENV=test .venv/bin/python manage.py test tests --verbosity 2`:
  **231 tests passed**, no database setup. `ruff check .`, `ruff format --check .`
  and `mypy`: all **57 Python files** formatted and **29 checked source files** clean.
- `GLOW_ENV=test .venv/bin/python -m glow_persistence.static_check`:
  **32 models / two unapplied migrations agree**, with no connection/SQL execution.
- `PYTHONPATH=. .venv/bin/python -m unittest discover -s ../../packages/contracts/tests -v`:
  **38 methods passed**. Contracts `npm run check`: deterministic generation and
  **373 JavaScript cases passed**.
- Mobile `npm run check`: TypeScript, ESLint and **449 tests passed**.
  This includes **38 interaction tests**, including the **11 shared traces**.
  Counts overlap and must not be added as independent coverage totals.
- Rendered collection: **81 cases**, preserving all **69 inherited cases** and
  adding **12 interaction cases**. Actual execution is required in hosted CI.

Independent Python review ended with **41 focused tests passing** and no remaining
concrete finding. Executed before/after controls preserved in this session showed:
a primed source-adapter replacement returning an old active match now restricts it;
206 simultaneously retained distinct reservations now cap at 200 and drain;
a repository replacement inside revocation no longer receives an old match/event;
and replacement of the registry between batch issuance and use now rejects the
stale batch without writes. Both registry object identity and generation are bound.
A late registry callback issue was corrected before its first executable probe;
it is not claimed as an observed pre-fix failure. Retained source/policy generations,
version-exhaustion denial and participant cleanup have explicit regressions.

Independent mobile review ended with **89 focused tests passing** and no remaining
concrete finding. Reproduced corrections cover pending-media disclosure through match
projections, stale-time replay returning a match grant, deleted/expired reverse
sessions, source changes during final projection callbacks, and cross-mode retries
stuck pending. Canceled delayed work uses a released single slot. Separate probes
confirmed immutable receipt retention, lost-response retry and canceled account
changes. Browser fixture-name assertions were corrected before hosted execution.
The source-reviewed adapters retain fresh authority through publication, and replay
returns an immutable receipt plus only a currently authorized projection.

The contract/static/config/documentation review found no remaining concrete blocker.
Existing production definitions and AppResponse alternatives are unchanged; the
receipt/result types are additive internal catalog definitions. Production OpenAPI
paths remain empty. No dependency, lock, workflow, deployment or DB wiring changed.
The integrated export identified one Metro configuration gap: the new canonical
production flow import was outside the existing fixture-only watch folder. The
narrow correction watches its canonical source directory without copying flow logic.
`EXPO_OFFLINE=1 npm run export:development` then passed both iOS and Android
development JavaScript exports; this is not a signed/native-device test.

## Initial hosted publication and correction

[PR14](https://github.com/amthorn78/glow-dating-app/pull/14) opened with candidate
`c4209d4ab90320dded692f0b4da584bba31f8207`, tree
`5abeba974d8b82fb6e9b4afae612469d78cd556a`, actual parent
`833408ab3e04ad4f649e71ca0483e606806dddbb`. All **251 published blobs/modes** and
complete tree were verified. No synthetic local history was pushed.

Initial [PR run 35980054193](https://github.com/amthorn78/glow-dating-app/actions/runs/35980054193)
and [push run 35980010914](https://github.com/amthorn78/glow-dating-app/actions/runs/35980010914)
passed API, smoke and container jobs but failed Mobile checks: **80/81 browser
cases passed**, including all **69 inherited cases**. The new delayed-action/account
switch case expected an enabled Jules card immediately after replacing the session.
The retained discovery queue correctly required an explicit refresh; it must not
adopt a new session automatically. The correction asserts reload-required/zero stale
cards and performs the existing Refresh action before keeping the original enabled
card and zero-match assertions. Timeouts/retries and inherited assertions are unchanged.
Actual corrected browser execution remains a hosted gate, not a local claim.

[Automatic code review](https://github.com/amthorn78/glow-dating-app/pull/14#discussion_r4091934598)
on that initial head identified a **P2**: the mobile adapter's global safety revision
suppressed otherwise valid reciprocal matching after an unrelated block/unblock or
unmatch. Independent controls reproduced the original unrelated-pair failures.
The correction tombstones only the affected pair's stored actions, matching Python.
Independent review then reproduced a submitting-old-like resurrection in the first
correction: checking only the opposite row was insufficient. Match formation now
requires **both** stored directions to be matchable and source-current. Same-pair
block/unblock, repeated old likes, source restoration and unmatch cannot revive
contact; unrelated safety actions preserve a valid reciprocal match. The analogous
source-current case was inferred and tested after correction, not claimed as an
executed pre-fix failure. Seven focused regressions cover this correction.

Initial remote code review completed at `2026-09-24T09:18:28.739512Z` and security
at `2026-09-24T09:19:02.540497Z`, per the
[receipt](https://github.com/amthorn78/glow-dating-app/pull/14#issuecomment-5811314395).
Those receipts cover **c4209d4a only**, with the P2 recorded above. They do not
certify the later correction. The narrow correction independent review passed **45/45 interaction tests** with
no remaining concrete finding. Complete corrected `npm run check` passes **456
mobile tests**, TypeScript and ESLint. The earlier 449 count above describes the
initial candidate. The actual-store browser reproduction observed reload-required,
no page and zero actions before Refresh; after Refresh and late release the Like
control is available with zero actions/matches. Final hosted results are recorded
externally.

## Second code-review correction

The first corrected candidate `2b69e0805fe569745729f8028ab83b7e705df2bf`, tree
`9d775a72e885eec0eed97862fc6f656d7feb9408`, is the verified five-file child of
c4209d4a. All 251 blobs/modes match. Both
[PR run 35980997214](https://github.com/amthorn78/glow-dating-app/actions/runs/35980997214)
and [push run 35980992240](https://github.com/amthorn78/glow-dating-app/actions/runs/35980992240)
passed all four jobs, including **81/81 rendered cases**, 456 mobile tests, both
exports and actual container validation. These passes do not certify a later head.
Security review completed without findings at `2026-09-24T09:28:43.390118Z`;
code review completed at `2026-09-24T09:30:17.326842Z` and raised three additional
P2 findings. No merge was performed on that head.

- [Reverse block invalidation](https://github.com/amthorn78/glow-dating-app/pull/14#discussion_r4092040712):
  a fictional candidate blocking the owner before any match left its retained card
  current. Reverse safety commands must invalidate discovery while reverse likes
  remain private.
- [Deleted targets](https://github.com/amthorn78/glow-dating-app/pull/14#discussion_r4092040731):
  a mapped deleted target still accepted mobile block/unblock and target projection.
  Current target resolution must deny deleted access, including replay disclosure.
- [Repeated unblock](https://github.com/amthorn78/glow-dating-app/pull/14#discussion_r4092040718):
  Python accepted a new key for removed-to-removed despite F13 forbidding it. New
  unblock requires an active block; exact-key replay retains the original receipt.
  The regression verifies no receipt/event/state change on refusal and valid reblock.

These concrete failures were reproduced before correction. The mobile correction
notifies reverse safety commands, refuses deleted targets before new commands and
replays, and retains a target-record revision through the final callback-free
commit guard. This record guard requires current identity, not discovery eligibility;
participant unmatch remains independent of current target discovery eligibility.
The regression set includes target deletion during precommit, replay refusal and
reverse-like privacy. Narrow review also reproduced target deletion during the
final block-replay projection read after the earlier current-target check; the
corrected projection retains and compares that original target revision through
its final return, preserving the receipt and suppressing a stale projection. Python's full **232-test** API suite, Ruff, formatting and
mypy pass after its independently reviewed F13 correction. Mobile's scoped **52
interaction tests plus 27 discovery tests** pass with lint and types. The complete
corrected `npm run check` passes **463 mobile tests**, TypeScript and ESLint. Exact
correction review/head and subsequent hosted results belong in the external report.

The next narrow publication preserves all prior checks/review history and requires
fresh hosted checks and final-head review before merge. No production contract or
policy is relaxed.

## Final deleted-target projection correction

The next candidate `4db111f0cf574bd998d451ae1fb75e1f15049aad`, tree
`fb7b474fef2e144fed2d7e68b1d6f2a2b8436c07`, is the verified seven-file child of
2b69e080. Both [PR run 35982485970](https://github.com/amthorn78/glow-dating-app/actions/runs/35982485970)
and [push run 35982480461](https://github.com/amthorn78/glow-dating-app/actions/runs/35982480461)
passed all four jobs, **81/81 browser cases**, 232 API tests, 463 mobile tests,
contracts, exports and container checks. The PR and push runs completed at
`2026-09-24T09:44:37Z` and `2026-09-24T09:43:55Z` respectively.

One [manual code-review request returned Unknown error](https://github.com/amthorn78/glow-dating-app/pull/14#issuecomment-5811665223)
at `2026-09-24T09:39:02Z`; it is not successful coverage. The separate new-commit
review remained running and completed at `2026-09-24T09:45:12.659178Z` with
[P2: suppress deleted-target unmatch projections](https://github.com/amthorn78/glow-dating-app/pull/14#discussion_r4092166133).
Security review completed without findings on 4db111f0 at
`2026-09-24T09:42:47.027855Z`. No merge occurred on that head.

Participant unmatch must still commit when the other participant is deleted, but
its fresh response cannot expose that deleted profile identifier. The same shared
match projection is used by list, contact, unmatch result and replay, so the
correction covers those call sites and retains current-target authority through
final callback-capable reads in every match state. Cleanup authorization stays
separate from projection authorization. Independent before-fix probes observed
restricted/unmatched deleted-target projections in list, command and replay paths.
Five new regressions cover deleted-target cleanup/replay, deletion during final
response/replay reads and later-row invalidation of restricted/unmatched list
projections. **57 interaction tests plus 27 discovery tests** pass; full mobile
`npm run check` passes **468 tests**, TypeScript and ESLint. Exact independent
review and final publication identities are recorded in the external report;
earlier passing runs do not certify this later source.

## Stored canonical match identity correction

The four-file projection correction `e3760963ed683db9b54ec6774715d79dfebe80dd`,
tree `a114a342324ebbb5eaa836136ed1d110912f1229`, is published as the verified
child of 4db111f0. Both [PR run 35983644411](https://github.com/amthorn78/glow-dating-app/actions/runs/35983644411)
and [push run 35983639541](https://github.com/amthorn78/glow-dating-app/actions/runs/35983639541)
passed all four jobs, 468 mobile tests and **81/81 browser cases**. They completed
at `2026-09-24T09:56:13Z` and `2026-09-24T09:55:58Z` respectively. Security
completed without findings at `2026-09-24T09:56:14.008843Z`; code review completed
at `2026-09-24T09:55:05.994042Z` with
[P2: update an existing match under its stored canonical pair](https://github.com/amthorn78/glow-dating-app/pull/14#discussion_r4092254016).
No merge occurred on that head.

After a registry incarnation changes a participant's UUID, recomputing an existing
match's storage key can leave the old row behind. The independent before-fix probe
observed two stored rows with the same match ID after unmatch and a stale original
projection. The same-key block lookup omitted the existing match's immediate
restriction/event. Existing matches must be resolved by their retained participants
and updated under their own stored canonical pair; only creation of a genuinely new
match computes its initial current pair. Receipt replay must find the same retained
match. The correction covers this single identity-incarnation write/read family;
two added regression methods cover either participant UUID replacement and either
unmatch caller, one retained match ID/key, exact receipt replay, one revocation
and immediate block restriction. Independent before/after probes and three focused
methods pass with no remaining finding in this bounded family. All **30 interaction
methods**, scoped Ruff/format and mypy pass. The complete API suite passes **234
tests**, with no database setup; Ruff checks all 57 formatted files and mypy checks
29 source files. Exact final publication gates are recorded externally.

## Source-scope and original-action projection correction

Candidate `8ccf35e23b5276d318fa9577d91b6e2385996d18`, tree
`07ee1dae4a1720e66983c08e60ed714feae0b1f9`, is the verified five-file child of
e3760963. Both [PR run 35984649976](https://github.com/amthorn78/glow-dating-app/actions/runs/35984649976)
and [push run 35984640320](https://github.com/amthorn78/glow-dating-app/actions/runs/35984640320)
passed all four jobs/81 browser cases, completing at `2026-09-24T10:06:07Z` and
`2026-09-24T10:05:03Z`. Security completed without findings at
`2026-09-24T10:05:48.778337Z`. Code review completed at
`2026-09-24T10:06:11.188886Z` with two further P2 findings; that head was not merged.

- [Targeted source scope](https://github.com/amthorn78/glow-dating-app/pull/14#discussion_r4092349848):
  replacing an unrelated mobile candidate advanced a global interaction source
  guard and revoked an otherwise current match. Targeted record changes must
  revoke only participating pair/action authority. Discovery queue freshness is
  separate; genuinely shared viewer/policy changes still invalidate globally.
- [Original action authority](https://github.com/amthorn78/glow-dating-app/pull/14#discussion_r4092349860):
  Python and mobile replay rebuilt a unilateral action projection from fresh pair
  eligibility while ignoring the directional row's original retained authority.
  A same-value source restoration or block removal must not turn a historical
  receipt into current action authority. The receipt stays immutable; the current
  projection also requires the stored action's original guards/bindings and
  matchable status to remain valid.

The bounded correction checks the related/unrelated/shared writer matrix and
original-versus-fresh projection authority in both languages. Python independent
before/after evidence covers 18 like/pass controls: 16 revoked originals now return
null projection and two unchanged originals still project; receipts and counts stay
unchanged. The full API suite passes **236 tests**, Ruff/format and mypy. Exact
final publication gates are recorded externally.

Mobile separates durable pair authority from command publication freshness:
target record and affected profile ownership changes retire participating grants,
while shared viewer/policy/time changes remain global. Pending commands still
retain the original page/population and queue publication revisions. Independent
review also reproduced a queue refresh during source acquisition; retaining the
queue's original published revision and checking the original batch at final commit
rejects both callback variants. Same-value unrelated writes preserve a valid match,
but duplicate profile ownership and restoration cannot revive old authority.
Action replay additionally excludes inactive matches. Seventeen added regressions
cover these related boundaries. All **74 interaction tests plus 27 discovery tests**
pass; full mobile `npm run check` passes **485 tests**, TypeScript and ESLint.

## Shared authority and private consumption correction

Candidate `554fbd81cafb966cdc1564c3f9889baf2e486dcf`, tree
`72df178bea03722a195a91e8f0e63cf74da505d2`, is the verified eight-file child of
8ccf35e2. Both [PR run 35986344755](https://github.com/amthorn78/glow-dating-app/actions/runs/35986344755)
and [push run 35986338500](https://github.com/amthorn78/glow-dating-app/actions/runs/35986338500)
passed all four jobs/81 browser cases, completing at `2026-09-24T10:23:21Z` and
`2026-09-24T10:23:25Z`. Actual mobile logs confirm 485 tests, 373 contract cases,
development export and 81/81 browser cases in each run. Security completed without
findings at `2026-09-24T10:24:01.746802Z`. Code review completed at
`2026-09-24T10:23:37.419873Z` with three further P2 findings; that head was not merged.

- [Retained policy/clock authority](https://github.com/amthorn78/glow-dating-app/pull/14#discussion_r4092504108):
  Python stored directional guards omitted interaction-policy and discovery-clock
  revisions, permitting revoked original likes to form a match after restoration.
- [Discovery presentation scope](https://github.com/amthorn78/glow-dating-app/pull/14#discussion_r4092504115):
  mobile scenario/queue invalidation advanced interaction authority, restricting
  valid matches without any participant or policy change.
- [Private consumption freshness](https://github.com/amthorn78/glow-dating-app/pull/14#discussion_r4092504129):
  Python's global consumption revision invalidated another viewer's page after
  a private reverse unilateral like, despite unchanged exclusions.

The correction retains policy/clock authority from both accepted directional
actions in a match. Discovery consumption uses viewer-scoped exclusion revisions;
the global commit guard remains separate for atomic writes. A viewer first
observed during a final callback also receives the relevant committed invalidation.
Full API validation passes **241 tests**, Ruff/format and mypy, without database
setup. Mobile presentation writers retire pages/batches without revoking durable
interaction authority; actual source/policy writers still revoke. Full mobile
`npm run check` passes **491 tests**, TypeScript and ESLint. Independent mobile
review passes **128 interaction/discovery tests and 52 additional writer cases**.
Exact final Python review and publication gates are recorded in the external report.

## Participant cleanup authority correction

Candidate `0859fc4560088619b5d48eecbdbe3a3c3bb5a96e`, tree
`ed0f2eeaa6a106d76383d5bc4c16253ed10ed538`, is the verified nine-file child of
554fbd81. Both [PR run 35987734669](https://github.com/amthorn78/glow-dating-app/actions/runs/35987734669)
and [push run 35987729831](https://github.com/amthorn78/glow-dating-app/actions/runs/35987729831)
passed all four jobs/81 browser cases, completing at `2026-09-24T10:37:31Z` and
`2026-09-24T10:36:00Z`. Actual logs confirm 241 API tests, 38 Python contract
methods, 491 mobile tests, 373 JavaScript contract cases, development export,
smoke guards and built-image validation. Security completed without findings at
`2026-09-24T10:37:09.666842Z`. Code review completed at
`2026-09-24T10:37:31.624302Z` with two further P2 findings; that head was not merged.

- [Removed target identity](https://github.com/amthorn78/glow-dating-app/pull/14#discussion_r4092619996):
  Python required the other participant's current registry row before unmatch,
  although the aggregate retained its identity and the caller remained authorized
  for cleanup. Missing disclosure authority must suppress projection, not cleanup.
- [Restricted-session cleanup](https://github.com/amthorn78/glow-dating-app/pull/14#discussion_r4092620004):
  mobile routes and adapter required an active account, denying participant
  unmatch to valid-session suspended/deletion-pending accounts. Cleanup authority
  must remain separate from profile/discovery/new-interaction authority.

Python cleanup now uses the stored match participant identity even if the target
registry row is absent. Every match-state projection retains its registry guard
through final reads. Independent before/after probes and three targeted regression
methods pass; the full API suite passes **244 tests**, Ruff/format and mypy.

Mobile separates cleanup authority from private match/profile authority. Current
valid-session active/suspended/deletion-pending participants may read only match
ID, version and state for cleanup; deleted actors, invalid sessions and outsiders
remain denied. Routes and generic list/detail views expose that path, including
when an active participant cannot obtain the other profile's projection. Two new
routed regressions preserve all prior 81 browser assertions; **83 cases are now
collected**, with hosted rendering still required for this source.

Independent review also reproduced an outer store refresh republishing old private
matches after a nested logout or target deletion during cleanup-list acquisition.
The store retains actor/publication authority, acquires cleanup references before
the final private views and compares authority without callbacks before publishing.
Logout, target-deletion and nonnotifying clock variants now pass. Full mobile
`npm run check` passes **516 tests**, TypeScript and ESLint. Independent review
passes **156 targeted interaction/discovery/route tests**, a **30-case cleanup
matrix** and **six final-publication variants**. Exact final publication gates are
recorded in the external report.

## Aggregate projection and original replay target correction

Candidate `74fd2a87e453b32fdbac07e2aac0bd081da9c9b5`, tree
`9d6549ee527256d1be167bf9d00585421840dc0a`, is the verified sixteen-file child
of 0859fc45 (56 changed files overall). Both
[PR run 35989624779](https://github.com/amthorn78/glow-dating-app/actions/runs/35989624779)
and [push run 35989619707](https://github.com/amthorn78/glow-dating-app/actions/runs/35989619707)
passed all four jobs/**83 browser cases**, completing at `2026-09-24T10:57:56Z`
and `2026-09-24T10:57:04Z`. Actual logs confirm 244 API tests, 38 Python contract
methods, 516 mobile tests, 373 JavaScript cases, exports, smoke and container
validation. Security completed without findings at `2026-09-24T10:56:19.860005Z`.
Code review completed at `2026-09-24T11:00:01.808955Z` with two Python P2 findings;
that head was not merged.

- [Aggregate read authority](https://github.com/amthorn78/glow-dating-app/pull/14#discussion_r4092812344):
  a later match projection's source callback could revoke an earlier projection
  after its individual validation but before the final list returned.
- [Original receipt target](https://github.com/amthorn78/glow-dating-app/pull/14#discussion_r4092812351):
  after a profile UUID was reassigned, replay could combine the original receipt
  with a current projection resolved for a different target account.

The aggregate read retains per-row source guards and stored match identity plus
shared session/registry/clock/policy authority through all later callbacks, then
compares them without another callback. It does not use the repository's global
commit revision to invalidate reads for unrelated private actions. Replay now
requires the projection target, current profile binding and object reference to
match the original receipt, with registry authority retained through return.
Five initial regression methods reproduced seven pre-fix failures; that source
passed 249 API tests. Independent review then reproduced a later reverse block
leaving an earlier restricted/unmatched match object unchanged. Each projected row
now also retains both directional block identities through the final comparison,
including absence and block/unblock within one callback. The sixth new method
reproduced eight failures in a twelve-subcase matrix before this correction.
All **46 interaction methods** and the full **250-test API suite** pass with
Ruff/format and mypy. Independent review passes seven targeted methods plus
multi-state deletion/block, unrelated-private-action and five-operation registry
removal/restoration/result-time-rebinding probes, preserving receipts and cleanup.
The mobile analogue review passed seven existing list/store callback tests and
an ownership-swap/restoration probe; its source remains unchanged at **516 tests**.
Exact independent Python review and final publication gates are recorded externally.

## Publication boundary

The aggregate-projection/original-target correction is prepared for publication as a
child of actual PR14 head `74fd2a87e453b32fdbac07e2aac0bd081da9c9b5`. The branch and PR are
published; this next narrow correction remains local at this checkpoint. Exact corrected head, reviewed
heads, run/job links, merge and actual-main identity belong in **AB1-R012** on the
existing shared report page, avoiding a self-referential commit/check loop.

Required gates: all four Foundation jobs on the actual final candidate, including
documentation; final-head review dispositions; checked merge after current
base/main reconciliation; then all four jobs and actual rendered/container logs
on merged main. Preserve failed-run and negative-control history. P05.2's 69
inherited browser cases retain meaningful assertions. No broader independent
security audit, database/provider or native-device acceptance is claimed.

## Scope limits

No database connection, SQL/applied migration, live HDE/provider call, Railway or
Cloudflare mutation, deployment, paid activation, real-user/photo import, legacy
retirement or person-directed message is authorized by this assignment. The
[P11 matrix](p11-deferred-acceptance.md) owns real integration proof. Fixture
receipts/revision guards demonstrate in-process semantics, not crash durability,
PostgreSQL isolation or external exactly-once delivery.

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

## Publication boundary

The final projection correction source/checkpoint is prepared for publication as
a child of actual PR14 head `4db111f0cf574bd998d451ae1fb75e1f15049aad`. The branch and PR are
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

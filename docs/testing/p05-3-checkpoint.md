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

## Publication boundary

The corrected source/checkpoint is prepared for publication as a child of the
actual initial PR14 candidate. The branch and initial PR are published; these
correction files remain local at this checkpoint. Exact corrected head, reviewed
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

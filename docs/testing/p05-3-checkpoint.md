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

## Publication boundary

This source checkpoint precedes its containing remote candidate. All changed source
and documentation are prepared locally for one scoped publication; no candidate PR
or merge is claimed by this file. The remote branch exists at the verified baseline.
The exact published head, PR, reviewed heads, run/job links and merge/main identity
belong in **AB1-R012** on the existing shared report page, avoiding a self-referential
commit/check loop. The local synthetic history is never pushed.

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

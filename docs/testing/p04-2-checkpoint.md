# P04.2 profiles, preferences and visibility checkpoint

Assignment **AP1-P04.2-001**, revision **1.0**, issued 23 September 2026.
Scope: fixture profile/preferences editing, owner and candidate projections,
completion and visibility. This checkpoint does not establish P04.3 media,
production authorization, persistence, native-device acceptance or release.

## Starting identity and authority

Remote main was **4f2708d476d2096cdf7ef8e6062803905aca5915**, tree
**5c8c4baf21afa3cf43d6fda7fdc90ed6c05d32e5**, with no open PRs. All **172
source blobs and file modes** were verified against the complete remote tree.
Direct shell Git authentication was unavailable. A local Git baseline is only a
diff aid; publication uses the real remote parent through the GitHub connector.
Never push the synthetic local history.

Branch: `app-builder-1/p04-2-profiles-preferences-visibility`.
The live P04.2 task and Implementation Control authorize this assignment under
GAPP-PF01 D08. P04.1 is Done at fixture scope under AB1-R006/AP1-ACK006;
its four state corrections and recovery behavior remain regression requirements.
P04.3 is separate and remains unstarted by this assignment.

See [behavior and provenance](../architecture/profiles-preferences-fixtures.md),
[current handoff](../continuity/current-handoff.md), and
[deferred acceptance](p11-deferred-acceptance.md). Final candidate, PR/merge/main
identities and their checked content relationship belong to **AB1-R007**, if
still unused at publication, in the
[shared reports](https://app.notion.com/p/3e44590a05eb81d58971ee4cd870774f).
A containing commit cannot record its own final hash. This file alone does not
prove checked publication or merge.

## Unchanged baseline checks actually executed

Linux container, Python **3.12.14**, Node **24.19.0**, npm **11.9.0**.
The API was installed in `services/api/.venv` using the committed hash lock;
mobile and contracts used their committed npm locks with scripts disabled.
No dependency upgrade was applied.

| Directory | Commands | Observed result |
|---|---|---|
| services/api | `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`; `.venv/bin/python -m pip check` | Exit 0; no broken requirements |
| services/api | `GLOW_ENV=test .venv/bin/python manage.py check`; `GLOW_ENV=test .venv/bin/python manage.py test tests --verbosity 2` | Exit 0; **147 tests pass**, unused DB setup skipped |
| services/api | `.venv/bin/ruff check .`; `.venv/bin/ruff format --check .`; `.venv/bin/mypy` | Exit 0; **47** formatted files and **23** mypy source files |
| services/api | `GLOW_ENV=test .venv/bin/python -m glow_persistence.static_check` | **32 models** and **two unapplied migrations** agree without SQL |
| services/api | `GLOW_ENV=test .venv/bin/python smoke.py` | Loopback HTTP live **200**, ready **503**, recommendations **200** |
| repo root | `PYTHONPATH=services/api services/api/.venv/bin/python -m unittest discover -s packages/contracts/tests -v` | **36 Python contract methods pass** |
| packages/contracts | `npm ci --ignore-scripts`; `npm run check` | Deterministic generation matches committed bytes; **199 JavaScript cases pass** |
| apps/mobile | `npm ci --ignore-scripts`; `EXPO_OFFLINE=1 npm run check:expo` | Exit 0; offline SDK dependency check passes, with the tool's offline reliability warning retained |
| repo root | `GLOW_SMOKE_PYTHON="$PWD/services/api/.venv/bin/python" node scripts/smoke.mjs`; `node --test scripts/smoke.test.mjs` | Actual loopback mobile/API smoke, denied mutations **405**, and one bounded-startup regression pass |

Counts overlap and are not summed. API/contract/root code remains unchanged in
this slice. Hosted Foundation checks are required again on the final candidate.

## Implemented behavior and local checks

`npm run check` passes TypeScript, ESLint and **116 mobile tests**: the original
58 remain unchanged, with 56 profile policy/adapter/store cases and two new route
cases. The complete local result includes the final explicit UI-snapshot allowlist
regression and the later malformed-read/removal regressions. Both iOS and Android
development JavaScript bundles were produced locally for the initial implementation by
`EXPO_OFFLINE=1 npm run export:development`; their metadata and nonempty files
were inspected. Hosted checks must validate the published candidate independently.

The new rendered file contains **14 cases**, alongside all **16 unchanged prior
cases**. All **30 pass in hosted Chromium** on the reviewed test correction below;
no local browser pass is claimed. The
rendered cases exercise ordinary incomplete editing, blank biography, cancel,
navigation/resume, retries and conflict refresh, malformed-response rollback,
retained profile/preferences sources, pause/resume and current evidence denial,
private-field removal on account changes, owner/candidate separation, protected
links and the 320 px doubled-text empty form.

| Risk | Executable evidence |
|---|---|
| Unicode, closed edits and preference policy | `profiles/policy.test.ts`: scalar limits, combining marks, lone surrogates, empty versus whitespace-only biography, duplicate dimensions/options, unknown vocabulary and transport ceilings |
| Owner/object/version/idempotency and delayed work | `profiles/fixture-adapter.test.ts`: creation versus update, stale/foreign context, changed-payload conflict, repeated receipts, concurrent staging, malformed response rollback, immutable request/context binding, suspension denial and one-time system removal |
| Drafts, revocation and safe adoption | `profiles/store.test.ts`: independent saved/draft values, retained source revisions, cancel/retry, immediate pause, delayed resume, exact consent revision, account-switch observers, checkpoints and candidate allowlists |
| Navigation and actual screens | `onboarding/profile-routes.test.ts` and `rendered/profile-preferences.spec.ts`; the original P04.1 test files retain their behavior assertions |

## Distinct review and corrective evidence

An independent peer-agent reviewed the complete implementation diff and performed
targeted Node reproductions. This is independent source/fixture review, not a
native-device or production security certification. The following findings were
corrected before initial publication and covered by regressions:

| Finding | Disposition |
|---|---|
| Valid intent for the wrong operation could reach the visibility method | Each adapter entry requires its exact operation arm before processing; wrong-arm cases reject |
| Caller could mutate an intent during an asynchronous delay | Validate and copy intent/context before waiting; mutation and read-context regressions prove binding |
| Pending pause retained candidate disclosure until completion | Revoke discovery immediately, advance its revision and cancel prior permission-granting work; delayed pause/resume tests pass |
| Owner boundary published a transient old private draft | Publish cleared owner fields atomically; subscriber-level tests inspect every emitted snapshot |
| Source synchronization could invent a profile restriction transition or repeat removal | Account restrictions deny access independently; system removal applies only listed F04 source states and preserves terminal removed versions |
| Spreading adapter state could expose internal evidence/catalog fields | Explicit presentation-field projection; exact snapshot-key regression rejects internal fixture fields |

The review also corrected Node strip-only constructor syntax and synchronized new
rendered tests with actual save/label behavior. These were implementation/harness
corrections, not inherited P04.1 product defects. No original regression assertion
was weakened. Final publication, any hosted findings, final delta review and merged
main evidence are recorded separately when they occur.

## Published review and rendered corrections

[PR 7](https://github.com/amthorn78/glow-dating-app/pull/7) initially published
implementation **0c908cb5abb286e69e8f5acbacb522dd68b373ff**, tree
**001ff68fbf02b68b44376ba3659fec367af91396**, directly on starting main.
The first [PR run](https://github.com/amthorn78/glow-dating-app/actions/runs/35919615903)
passed the three API jobs but failed Mobile checks with **24/30** rendered cases
passing. The first [push run](https://github.com/amthorn78/glow-dating-app/actions/runs/35919615536)
passed the three API jobs and **25/30** rendered cases. These failures remain
historical evidence; they are not accepted final-candidate checks.

Corrective commit **25e274f4384b88508baeadb9e00d8667a8a7b538**, tree
**ae6fa4f4251abfe9ba3af09a11754f7c752680c5**, addresses:

- Four new rendered cases assumed a fixed Back destination after protected
  discovery history was pruned. They now assert changed data in the original
  hidden form/preview before explicit in-app return. Fresh same-session history
  entries then prove Back reaches the current owner profile with disclosure blocked
  without reviving discovery. No full reload or absent-page assertion substitutes
  for retained-state proof.
- The second pause in the media-loss case was not awaited before a development
  authority change cancelled pending work. The test waits for accepted pause,
  removes media evidence, and requires a failed-resume alert with paused state.
- The inherited unsaved-birth case failed only in the first PR run. Entry routing
  now uses one coordinated onboarding subscription instead of independently
  subscribing to profile emissions during onboarding synchronization. This
  removes a mixed-snapshot redirect risk; the exact isolated browser failure was
  not independently reproduced or uniquely attributed to it. All original
  rendered assertions remain unchanged.
- Automated PR review [comment 4087307825](https://github.com/amthorn78/glow-dating-app/pull/7#discussion_r4087307825)
  identified that malformed reloads could succeed before profile creation.
  Invalid-response injection now fails validation with empty, preferences-only,
  profile-only and both-record states. Two regressions failed before correction,
  then passed: accepted state and both deliberate drafts survive, and valid retry
  succeeds.

The corrective [PR run](https://github.com/amthorn78/glow-dating-app/actions/runs/35920747363)
and [push run](https://github.com/amthorn78/glow-dating-app/actions/runs/35920741509)
each passed the three API jobs and **26/30** rendered cases, including all **16
original cases**. Four new assertions still failed. Three incorrectly expected
`incomplete` after an authority-only policy/media/reciprocal change; the current
state machine retains saved visibility while effective disclosure is `blocked`.
The pause wait matched the word "paused" inside the edited biography, so did not
actually wait for accepted pause. Subsequent assertions use exact
`Visibility: paused` / `Visibility: blocked` labels and preserve the hidden-state,
failed-resume and Back checks. No product behavior is relaxed for these cases.
This test-only correction is **0da919e6a704ab14190def24da9cfe3a05d40356**, tree
**d219a2dd27609f8169c42b2dbc2245906bf16dea**, parented on the first corrective
commit. The dedicated visibility control prevents biography text from satisfying
state assertions; an independent review checked it against the current adapter
and presentation rules. Lint and discovery still pass with **14 new cases**.
Automated review of the first corrective commit also reported the blocked-label
mismatch in [comment 4087393220](https://github.com/amthorn78/glow-dating-app/pull/7#discussion_r4087393220).
The same test-only correction disposes that finding; it does not change F04/F06.

An independent peer-agent reviewed the repair delta, reran the two malformed-read
regressions and found no material issue. The added terminal-removal regression
was also reviewed. Full local mobile checks pass **116 tests**, TypeScript and
ESLint.

On **0da919e6a704ab14190def24da9cfe3a05d40356**, all four Foundation jobs pass in
[PR run 35921543566](https://github.com/amthorn78/glow-dating-app/actions/runs/35921543566)
and [push run 35921536996](https://github.com/amthorn78/glow-dating-app/actions/runs/35921536996).
The Mobile logs confirm **116 unit tests**, both iOS/Android development JS exports
and **30/30 rendered cases**, including all prior corrections and all new retained
projection/pause cases. Container evidence is supplied by each successful hosted
API artifact job. Both material inline review findings are resolved after the
source/regression correction; the outdated flags alone are not their disposition.

The final documentation delta is reviewed separately. Its containing candidate
must pass the same four jobs before merge, followed by merged-main verification.
The external closure report owns those final candidate/main hashes and run links;
the successful runs above cover the code/test correction, not this later document.

## Rendering and artifact environment

Local Chromium was absent. The standard `npx playwright install chromium`
attempt failed because downloaded content was not a valid browser ZIP. This is a
tooling failure, not a rendered product result. Actual browser proof uses the
existing hosted Foundation **Mobile checks** job. Docker is unavailable locally;
the hosted **API artifact checks** job owns container proof.

The workflow only builds/tests; it contains no deployment, registry push,
Railway, migration or production connection step. The evidence-upload allowlist
adds only the empty profile form to the existing empty account form. Automatic
failure screenshots and traces stay disabled; populated private input is not
captured. Any visual-inspection claim requires the actual artifact to be opened.

Both allowlisted images from first PR artifact **10776712899** were downloaded
and opened. Their sampled **320 × 568** scroll viewports show legible doubled text,
wrapped labels and controls without horizontal clipping. They are partial
scrollports, not images of the complete forms; rendered geometry/reachability
assertions cover the other controls. Only empty fictional forms were captured.

## Remaining proof boundary

Same-session fixture memory is the supported restoration scope. Full-page reload
starts a fresh instance. Browser/direct-link evidence must not be called persisted
history, cross-device recovery or native acceptance. iOS/Android development
JavaScript exports are not compiled/signed native builds.

The inherited moderate dependency findings are historical, not a new audit or
proof of remediation. Compatibility/reachability work remains before release.
DB01–DB13, PV01–PV08, PR01, N01 and R01 remain governed by the deferred matrix.
No database connection, SQL/migration execution, HDE/provider request, Railway
resource/configuration change or public release belongs to this assignment.

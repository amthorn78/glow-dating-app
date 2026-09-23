# P04.1 native shell and onboarding checkpoint

Assignment **AP1-P04.1-001**, revision 1.0, issued 23 September 2026. Scope is
**P04.1 — Build native shell and account/onboarding flows** under GAPP-PF01
P04/D08. This checkpoint separates unchanged-baseline verification, new fixture
behavior, and candidate/publication evidence. P04.2/P04.3 and P11 are not completed
by this work. See [fixture architecture](../architecture/onboarding-fixtures.md)
and [deferred acceptance](p11-deferred-acceptance.md).

## Correction and revalidation — AP1-P04.1-002

Starting main **c544b654e0af3e75f31b579f72e5a02e5e577e84**, tree
**4636d88599474309cf9b2533e1fd48415c427df0**. All 168 source blobs/modes matched
that pinned remote tree; no open PR or later main commit existed at startup.
[PR 6](https://github.com/amthorn78/glow-dating-app/pull/6), branch
`app-builder-1/p04-1-state-corrections`, carries the focused repair. Its real
remote ancestry starts at that main, never at the synthetic local diff baseline.

### Reproduction and review dispositions

The tests-only commit **06ceef6f04e517ce2d5c2e8cb49c8b8c0704a29c** preserves all
starting implementation bytes. Hosted [PR run 35902177478](https://github.com/amthorn78/glow-dating-app/actions/runs/35902177478)
[mobile job 107320869687](https://github.com/amthorn78/glow-dating-app/actions/runs/35902177478/job/107320869687)
executed 15 rendered cases: eight passed, seven failed. All seven original cases
passed, as did ordinary underage return. The new failures are distinguished below.

| Finding / PR 5 thread | Actual starting evidence | Correction / regression |
|---|---|---|
| A — 4085129530, stale birth draft | Both accepted and unsaved rendered drafts still showed the discarded 1990 date after eligibility changed to 1992 | Monotonic birth-draft revision resets obsolete facts and rejects captured edit/submit callbacks. Tests cover both paths, ABA date changes, accepted replacements and deliberately retained unsaved edits |
| B — 4085471560, retained eligibility | Ordinary return passed. The retained variant proved one hidden eligibility field existed before submitting an underage date; return showed the old adult date | Each form field reconciles its own authoritative source before children render. Live revision checks guard callbacks. Ordinary/retained/no-edit Save, consent and independent local edits remain rendered cases |
| C — 4085210603, expired restriction | Both suspended and deletion-pending rendered cases failed to reach account entry; unit regressions also failed | Session validity takes precedence. Private state/checkpoints clear; seeded account restriction survives sign-in/recovery without scenario reselection. Explicit scenario replacement is separate |
| D — 4085535817, simulated challenge expiry | Baseline unit test changed Expired → Success and incorrectly reached eligibility; elapsed-clock tests are separate | The matching challenge is terminally expired, and resend creates another. Wrong contexts, retryable errors and delayed replacement-challenge races have focused tests |
| Recovery — 4085383812 | Original rendered rate-limit → Success case passed without re-entering email | Already corrected before this repair. Original test/provider navigation structure preserved |

All five PR 5 threads were read despite their outdated/unresolved flags. The first
consent test assumed browser Back selected eligibility; that assertion did not
establish a consent defect. It now exercises all retained controls and the explicit
current-step return. The first new D rendered test opened the account outcome
panel before verification navigation completed; that timeout was a harness issue.
It now waits for the verification screen. The unit D reproduction is valid; no
rendered D baseline defect is inferred from that timeout. The original assertions
in `rendered/onboarding.spec.ts` and `onboarding.test.ts` remain unchanged.

C's full-page direct URLs prove fresh signed-out route denial because reload
clears this intentionally in-memory runtime. Expired-snapshot route denial is
separately exercised by store tests; rendered expiry, subsequent sign-in and Back
are checked before any optional reload. No persisted-state claim is made.

### Candidate checks and remaining publication gate

Linux x86_64/glibc 2.39, Python 3.12.14, Node 24.19.0, npm 11.9.0; package pins and
locks unchanged. Required local checks: locked mobile/API/contracts installs,
mobile TypeScript/ESLint and **58 tests** (39 baseline + 19 new), offline Expo
check, iOS/Android development JS exports; **147 API tests**, Ruff/format/mypy,
**36 Python contract methods**, deterministic generation and **199 JS cases**;
static **32-model/two-migration agreement** without SQL; actual loopback HTTP
200/503/200, rejected writes 405 and the bounded-startup regression. Counts overlap.
The unchanged API/contracts/static/HTTP batch passed at 18:27:22–18:27:32 UTC.

C/D's first local baseline run had 4/13 passing; nine failures demonstrated the
state/challenge defects. Two additional delayed replacement-challenge tests failed
on the intermediate correction before exact challenge identity was captured.
The final C/D suite passes 15/15; birth-draft callback regressions pass 4/4.
Independent A/C/D review ran 46/46 onboarding-subset tests and inspected B's
per-field/stale-callback reconciliation. No broader production audit is claimed.

Local Chromium is absent and standard download returned HTML instead of a browser
archive. Actual rendering uses the existing hosted Foundation Mobile job; JS
exports do not substitute. Docker is unavailable locally; existing hosted API
artifact checks own container proof. Only the original empty-account-form image
is uploaded, with no populated private inputs, traces or credential screenshots.
The final candidate, corrected rendered outcomes, complete diff/review disposition,
checked merge, matching tree and merged-main CI are recorded in **AB1-R006** in the
[shared reports](https://app.notion.com/p/3e44590a05eb81d58971ee4cd870774f). Every
candidate, including documentation, must pass the four existing Foundation jobs.

No API, contracts, dependency/lock, workflow, DB/migration, HDE/provider or Railway
change is included. Both inherited moderate advisory chains remain release
follow-up. Real authentication/persistence, native/device/signing, live providers,
P11 and public release remain unproved. P04.2/P04.3 remain unstarted.

## Prior publication and evidence identity

The assignment's starting checkpoint is main
`bd701ebfede1630ba162862e053a0a55daea9c9b`, tree
`bb9fb2d113a222f418a1ea65e290f6c119df99fd`, after
[PR 4](https://github.com/amthorn78/glow-dating-app/pull/4). The remote head and absence of open PRs were rechecked before edits, and all
144 source blobs matched the remote tree. The acquired snapshot's local Git history
is not remote Git lineage.

Branch: `app-builder-1/p04-1-native-onboarding`. The historical implementation review corrected the findings then exercised.
AP1-ACK005 subsequently reopened four paths; their current dispositions are below. [PR 5](https://github.com/amthorn78/glow-dating-app/pull/5)
has an accepted implementation at **`5fa82a39f595a61d0a13060d06c1ea523e698ded`**,
tree **`00b0eaae9251e7a7aee37c4c7e435f27d089ef51`**. All four Foundation jobs passed
on its [PR run](https://github.com/amthorn78/glow-dating-app/actions/runs/35897572548)
and [branch run](https://github.com/amthorn78/glow-dating-app/actions/runs/35897565557),
including **all seven rendered Chromium cases**. This evidence update changes only
documentation. Its containing candidate still requires exact-head CI before merge;
the final candidate, merge/main relationship and main CI belong to **AB1-R005** in
the [shared report record](https://app.notion.com/p/3e44590a05eb81d58971ee4cd870774f).
A commit cannot include its own hash. Do not infer merge from this checkpoint alone.

### Corrected publication history

The first implementation `d66e7c40ca48eeec4aac87a17b6c992ea78b2241`, tree
`2944134e82655e82a0e7acf4ed4f6ad13a37ea31`. Its first
[PR run](https://github.com/amthorn78/glow-dating-app/actions/runs/35892757779)
passed API, HTTP smoke and container jobs but failed mobile TypeScript: ignored
generated Expo web declarations had masked two unsupported Text `tabIndex` props
locally. The correction sets DOM focusability only after a web HTMLElement check;
native focus keeps the React Native API. TypeScript also passed with generated
Expo declarations excluded. Every later candidate, including documentation changes,
requires applicable Foundation jobs before merge. The failures below are historical;
their corrections passed together in the accepted implementation identified above.

Corrected candidate `65d245a78f11832e2ae63bd1e8afd55b82f580bd`
[passed static/native checks but timed out before browser tests](https://github.com/amthorn78/glow-dating-app/actions/runs/35893465492).
The harness had probed IPv4 while Expo bound IPv6 localhost, and native-only
platform configuration served a manifest rather than browser HTML. The correction
uses matching localhost `/status` readiness, explicit test-only web enablement and
visible server diagnostics. Expo's injected project-root variable is permitted
only in that harness and only at the exact app-config directory. Same-process
probes verified status 200, HTML 200 and the actual entry JavaScript bundle 200;
those probes do not substitute for the required Chromium interaction tests.

Candidate `9c0832d6e793a1a59a536fb05a6132ca30770cb5`
[ran all seven browser cases](https://github.com/amthorn78/glow-dating-app/actions/runs/35894916464):
registration/expired verification/focus and enlarged-text layout passed. Four
failures came from selectors matching hidden screens retained by the native stack;
tests now target the visible screen while keeping logout private-data absence
assertions across the entire DOM. The remaining case found competing redirects
for an unknown path. A generic link-unavailable screen now owns unmatched routes,
with one explicit safe return; known-route query/hash cleanup has one replacement
in flight. This correction is covered by the accepted hosted regression above.

Candidate `27a29c7944c2b724459870090584e6b4ad071470`
[passed three rendered cases](https://github.com/amthorn78/glow-dating-app/actions/runs/35895724641),
including interrupted drafts and all-DOM account-switch isolation. The subsequent
correction keeps navigation mounted while resetting only owner-bound private draft
state, preserving recovery input across a failed request. Stale draft callbacks
check live ownership. Logout/back tests now await the completed logout screen,
and an explicit local sitemap route replaces the SDK index with the same safe
unavailable-link screen. These corrections passed the full hosted regression above.

Candidate `ef8829a2a52088bf87b089e4cb7951d7c4c530a6`
[passed four rendered cases](https://github.com/amthorn78/glow-dating-app/actions/runs/35896752733),
including all direct/malformed link cases. Invalid reset correctly returns to
recovery for a new challenge; successful reset now returns an accepted-result flag
so the UI can safely navigate to sign-in. Explicit checked ARIA state supplements
native accessibility state for browser rendering. The back regression verifies
logout/private-field removal before Back and handles only the browser's initial
blank tab by re-entering a formerly protected URL, which must still deny access.
No other unexpected navigation result is accepted. The full hosted regression above
passed with these corrections.

## Unchanged API and contract baseline actually executed

Observed **23 September 2026, 16:44–16:45 UTC**, before new mobile implementation
acceptance. Environment: Linux x86_64 with glibc 2.39, Python **3.12.14**, Node
**24.19.0**, npm **11.9.0**. API dependencies were installed with the committed
hash lock into `services/api/.venv`; the contracts package used its committed npm
lock with scripts disabled. No dependency upgrade was used for these checks.

| Directory | Command | Observed result |
|---|---|---|
| services/api | `.venv/bin/python -m pip check` | Exit 0; no broken requirements |
| services/api | `GLOW_ENV=test .venv/bin/python manage.py check` | Exit 0; no issues |
| services/api | `GLOW_ENV=test .venv/bin/python manage.py test tests --verbosity 2` | Exit 0; **147 tests pass**; unused database setup explicitly skipped |
| services/api | `.venv/bin/ruff check .` | Exit 0 |
| services/api | `.venv/bin/ruff format --check .` | Exit 0; **47 files** already formatted |
| services/api | `.venv/bin/mypy` | Exit 0; **23 source files** |
| services/api | `PYTHONPATH=. .venv/bin/python -m unittest discover -s ../../packages/contracts/tests -v` | Exit 0; **36 test methods pass** |
| services/api | `GLOW_ENV=test .venv/bin/python -m glow_persistence.static_check` | Exit 0; **32 models**, migrations `0001_event_infrastructure` and `0002_app_domain` agree without SQL or applying migrations |
| services/api | `GLOW_ENV=test .venv/bin/python smoke.py` | Exit 0; actual loopback HTTP liveness **200**, readiness **503**, development recommendations **200** |
| packages/contracts | `npm run check` | Exit 0; deterministic generated-artifact comparison and **199 JavaScript corpus cases pass** |

The ignored local evidence directory is `.work/p04-api-baseline/`, containing
individual command logs, `results.json`, `js-contracts-result.json`, and
`environment.json`. It is a reproducible session log location, not a promised
durable attachment. Python methods and JavaScript corpus cases overlap; they must
not be summed into a unique-test count.

## P04.1 implementation and rendered evidence

The completed local checks pass: TypeScript, ESLint and **39 mobile tests**, including
27 new onboarding tests. They cover actual fixture challenges and expiry/replay,
neutral recovery, stale asynchronous completion, policy/date/consent boundaries,
known/approximate/unknown birth facts, corrections, idempotency, same-session
restoration and route denial. The exact post-adapter/pre-store cancellation race
was reproduced independently, corrected with fixture acknowledgment/rollback, and
verified recoverable. Review also corrected fixture address/time-format mismatch,
hidden invalid-date errors and final-newline civil-date acceptance.

The Playwright suite exercises rendered Expo Router screens, registration/sign-in,
verification errors/resend, neutral recovery/reset, private birth edits and failures,
interrupted drafts, account switching, blocked scenarios, direct routes and history.
Its layout case uses a 320×568 viewport with computed text sizes doubled; ordinary
journey cases use 390×844. Only the empty account form is captured, with traces and
automatic screenshots disabled. **All seven cases passed in 29.8 seconds** in
[mobile job 107305216499](https://github.com/amthorn78/glow-dating-app/actions/runs/35897572548/job/107305216499).
They demonstrate registration/verification/focus, neutral recovery/reset/retry,
direct/query/hash/unknown/sitemap denial, all birth-time modes and unavailable retry,
interrupted draft/account-switch isolation across hidden and visible DOM fields,
restricted/eligible scenarios and logout/back denial, and doubled-text layout.

The [empty-form artifact](https://github.com/amthorn78/glow-dating-app/actions/runs/35897572548/artifacts/10767681328)
is `p04-empty-form-layout`, 27,481 bytes, ZIP SHA-256
`d6467fd0cfef0b8d407ebbcdb4739116dbcbbbf3f0bf5235a832692db4c5759c`,
expiring **7 October 2026, 17:45:54 UTC**. Automated layout/focus/interaction
assertions passed; no human visual inspection of the artifact is claimed.
The committed suite and README walkthrough provide reproducible evidence after
artifact expiry. Local browser downloads were unusable; no local rendered pass is
claimed. Native JavaScript exports succeeded for both iOS and Android. Hosted
browser evidence does not prove device behavior.

The intended end of ordinary account/birth onboarding remains **profile
incomplete**, with discovery blocked. Explicit eligible development scenarios are
separate fixture controls. A completed form cannot establish real verification,
an HDE mapping, profile readiness or production authorization.

## Final local validation and hosted checks

The workflow and READMEs own the executable commands. Results below identify the
accepted implementation; AB1-R005 records the containing documentation candidate
and merged-main gates after they actually complete.

| Directory | Required command or check | Observed evidence |
|---|---|---|
| apps/mobile | `npm ci --ignore-scripts` and `npm run check` | Pass: locked install, TypeScript/ESLint and 39 mobile tests |
| apps/mobile | `EXPO_OFFLINE=1 npm run check:expo` | Pass; offline dependency check only |
| apps/mobile | `EXPO_OFFLINE=1 npm run export:development` | Pass: both development JavaScript exports |
| apps/mobile | `npm run test:rendered` | Pass: all seven hosted Chromium interaction/layout cases |
| repo root | `GLOW_SMOKE_PYTHON="$PWD/services/api/.venv/bin/python" node scripts/smoke.mjs` | Pass: actual loopback API → mobile client; 200/503 and rejected writes |
| repo root | `GLOW_SMOKE_PYTHON="$PWD/services/api/.venv/bin/python" node --test scripts/smoke.test.mjs` | Pass: one bounded startup regression |
| repo root | Complete diff review and `git diff --check` | Pass: separate review corrections and clean diff |
| GitHub implementation | **API checks**, **Mobile checks**, **API mobile smoke**, **API artifact checks** | All four pass on both exact implementation runs linked above |
| GitHub final documentation candidate / main | Exact-head CI, merged content relationship and Foundation results | Final closure ledger is AB1-R005; verify current PR and main before resuming |

Do not claim local image execution unless a Docker build and container check
actually run. The hosted artifact job is the existing image-validation route;
its runner-local image is not a published registry image or a Railway deployment.

Read-only npm audit reported **14 moderate package findings (0 high/critical)**,
representing two advisories in unchanged baseline dependency chains:
[Router URL decoding](https://github.com/advisories/GHSA-vcc3-ghjq-m6fr) and
[Expo build-chain UUID](https://github.com/advisories/GHSA-w5hq-g745-h8pq).
P04.1 adds Playwright packages and optional fsevents; none is flagged. These findings
need scoped compatibility/reachability remediation before release; route guards
are not claimed to neutralize the Router parsing issue. No forced audit fix,
downgrade or unrelated dependency upgrade was applied.

## Separate database audit consumed as source

The separately executed
[AB1-DBA-001 — PostgreSQL Audit and Shared-Database Recommendation](https://app.notion.com/p/3e44590a05eb81908661fc44eca0ce20)
was fetched for this work. It records a read-only audit executed on 23 September
2026 and recommends the owner-preferred same logical database only after reviewed
app schema/role isolation. It preserves the complete `hde` schema and
`public.hde_body_graphs_current`, and rejects the legacy public tables as the new
app's live store. A fresh read also consumed the audit's subsequent 32-model
reconciliation: all 32 map to new app-owned relations if retained, with no physical
reuse of legacy or HDE tables. Final schema/search-path design, maintained-auth
migration dependencies, roles, backup/restore and legacy-writer retirement still
need their reviewed P11 work. No early DDL is authorized by that mapping.

Consuming that saved report does not repeat its database connection or inherit
its audit exception. P04.1 adds no database connection, migration, role/grant
change, cleanup, HDE/provider request, Railway deployment or service configuration.
The same-project/same-logical-database preference remains intact; this fixture
work does not select or activate a physical schema.

## Retained limitations and next work

DB01–DB13, PV01–PV08 and PR01 remain their existing P11 cases. In particular,
DB09 must prove real allauth persistence, verification/recovery/revocation and
cross-device behavior. Fixture challenge expiry/replay tests do not prove it.
PV01/PV02 must establish authorized HDE behavior and mapping/deletion rights.
N01 and R01 retain signed device, accessibility, secure storage, delivery and
release acceptance. Browser rendering and iOS/Android JavaScript exports are
distinct evidence and establish none of those native or live-provider results.

A01/A07 supported HDE contracts/rights, A02 final schema/role design and preflight,
A04 provider/signing access, A05 launch policy and operating decisions, A06 disabled
paid scope, and A08 chat authorization proof remain scoped dependencies. Profile
and media implementation retain P04.2/P04.3. Do not start the next item until this
assignment's verified handoff is complete; the current task and exact next action
belong to Notion and [the current handoff](../continuity/current-handoff.md).

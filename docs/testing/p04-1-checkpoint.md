# P04.1 native shell and onboarding checkpoint

Assignment **AP1-P04.1-001**, revision 1.0, issued 23 September 2026. Scope is
**P04.1 — Build native shell and account/onboarding flows** under GAPP-PF01
P04/D08. This checkpoint separates unchanged-baseline verification, new fixture
behavior, and candidate/publication evidence. P04.2/P04.3 and P11 are not completed
by this work. See [fixture architecture](../architecture/onboarding-fixtures.md)
and [deferred acceptance](p11-deferred-acceptance.md).

## Publication and evidence identity

The assignment's starting checkpoint is main
`bd701ebfede1630ba162862e053a0a55daea9c9b`, tree
`bb9fb2d113a222f418a1ea65e290f6c119df99fd`, after
[PR 4](https://github.com/amthorn78/glow-dating-app/pull/4). The remote head and absence of open PRs were rechecked before edits, and all
144 source blobs matched the remote tree. The acquired snapshot's local Git history
is not remote Git lineage.

Branch: `app-builder-1/p04-1-native-onboarding`. The separate source review is
complete and material findings are corrected. [PR 5](https://github.com/amthorn78/glow-dating-app/pull/5)
published implementation `d66e7c40ca48eeec4aac87a17b6c992ea78b2241`, tree
`2944134e82655e82a0e7acf4ed4f6ad13a37ea31`. Its first
[PR run](https://github.com/amthorn78/glow-dating-app/actions/runs/35892757779)
passed API, HTTP smoke and container jobs but failed mobile TypeScript: ignored
generated Expo web declarations had masked two unsupported Text `tabIndex` props
locally. The correction sets DOM focusability only after a web HTMLElement check;
native focus keeps the React Native API. TypeScript also passed with generated
Expo declarations excluded. **Pending publication evidence:**
corrected candidate, hosted rendered checks, exact-candidate CI, merge/main
relationship, merged-main CI and AB1-R005/task closure. Every later candidate,
including documentation changes, requires applicable Foundation jobs before merge.

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
automatic screenshots disabled. **Hosted execution is still pending at this
implementation publication.** Local browser installation returned unusable download
archives; no local rendered pass is claimed. Native JavaScript exports succeeded
for both iOS and Android. Hosted browser evidence does not prove device behavior.

The intended end of ordinary account/birth onboarding remains **profile
incomplete**, with discovery blocked. Explicit eligible development scenarios are
separate fixture controls. A completed form cannot establish real verification,
an HDE mapping, profile readiness or production authorization.

## Final local validation and hosted checks

The workflow and READMEs own the executable commands. Record actual final results
for the completed candidate here, including any reruns after review corrections.

| Directory | Required command or check | Current evidence in this draft |
|---|---|---|
| apps/mobile | `npm ci --ignore-scripts` and `npm run check` | Pass: locked install, TypeScript/ESLint and 39 mobile tests |
| apps/mobile | `EXPO_OFFLINE=1 npm run check:expo` | Pass; offline dependency check only |
| apps/mobile | `EXPO_OFFLINE=1 npm run export:development` | Pass: both development JavaScript exports |
| apps/mobile | `npm run test:rendered` | Pending actual rendered interaction/layout evidence |
| repo root | `GLOW_SMOKE_PYTHON="$PWD/services/api/.venv/bin/python" node scripts/smoke.mjs` | Pass: actual loopback API → mobile client; 200/503 and rejected writes |
| repo root | `GLOW_SMOKE_PYTHON="$PWD/services/api/.venv/bin/python" node --test scripts/smoke.test.mjs` | Pass: one bounded startup regression |
| repo root | Complete diff review and `git diff --check` | Pass: separate review corrections and clean diff |
| GitHub candidate | **API checks**, **Mobile checks**, **API mobile smoke**, **API artifact checks** | Pending exact-candidate hosted results |
| GitHub main | Merged content relationship and Foundation results | Pending merge and verification |

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

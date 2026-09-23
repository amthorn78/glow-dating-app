# P04.3 private media lifecycle checkpoint

Assignment **AP1-P04.3-001 revision 1.0**, issued 23 September 2026.
Scope: private media fixture lifecycle and integration preparation. This is not
production media, persistence, native-device acceptance or release readiness.

## Starting identity and source reconciliation

Verified remote main **1c991948f819a5888256757babff31f1223622e7**, tree
**49a13dae12d27bc46ad429298da43588cdaedda4**, no open PRs. The local snapshot's
187 source blobs and modes matched the complete recursive remote tree. Local
Git history is a diff aid only; publication uses the real remote parent through
the connector. Never push that synthetic baseline.

Branch: `app-builder-1/p04-3-private-media-lifecycle`. P04.2 and P03.3 were Done;
P04.3 was Planned and then set In progress in the existing Notion register.
AB1-R007/AP1-ACK007 accept P04.2 at fixture scope. AB1-R008 was unused at startup.
D08's historical Drive Plan Reference was corrected to the existing repository
PF01 URL without changing its authorization content or State.

See [media semantics](../architecture/private-media-fixtures.md),
[provider mapping](../architecture/media-provider-mapping.md),
[current handoff](../continuity/current-handoff.md),
[walkthrough](../../apps/mobile/README.md) and
[deferred acceptance](p11-deferred-acceptance.md).
External **AB1-R008 if unused** in the
[shared report record](https://app.notion.com/p/3e44590a05eb81d58971ee4cd870774f)
owns final implementation/candidate/merge/tree identities and CI links. A
containing commit cannot certify its own final hash or future checks.

## Implementation and actual versus simulated guarantees

The owner screen supports selection, upload grants, transport progress and
interruption/cancellation/retry, exact F05 status feedback, accessible approved
ordering, removal and pending/failed/retried purge. Provider/system/moderator
controls are visibly separate synthetic actors. Owner commands cannot approve
or confirm provider deletion. Candidate delivery derives from current owned
approved assets; last-photo loss, pending removal, restriction and authority
changes revoke dependent previews/discovery and pending resume. Explicit pause
is preserved. Photo approval supplies no chart/consent/adult/profile-review/
reciprocal/launch-policy evidence.

`MediaCollection` is the smallest closed-contract extension for the missing
aggregate reorder version. Existing MediaIntent/MediaUploadGrant/MediaLifecycle
fields are unchanged. Source schema, F05, OpenAPI components, both semantic
validators, generated files and shared corpus agree. OpenAPI paths remain empty;
no API endpoint, model or migration was activated or changed.

Actual local PNG checks cover encoded bounds, signature, chunk framing/CRC,
IHDR fields and declared dimension limits, independently of filename/MIME.
There is **no pixel decoding or metadata removal**. A regression deliberately
uses invalid compressed pixels inside a valid container to preserve that limit.
Review/processing and approved variants are simulated and non-delivering.
Private originals use placeholders. Removing an app reference is not provider
purge, and simulated provider purge is not real byte/backup/cache deletion.

Native selection uses SDK-compatible Expo ImagePicker. No bounded native URI
reader has been verified; native selected files are refused for upload. The
browser fixture seam bounds File.size before arrayBuffer and performs no image
decode/object-URL creation. Simulated permission outcomes are not device proof.
The app remains explicit fixture memory, with no browser storage, DB connection,
SQL/migration, HDE/provider call, Railway change or production activation.

## Checks actually executed locally

Linux, Python **3.12.14**, Node **24.19.0**, npm **11.9.0**. Counts below describe
recorded local executions and overlap; they must not be summed.

| Directory | Command | Observed result |
|---|---|---|
| services/api | `python -m venv .venv`; `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`; `.venv/bin/python -m pip check` | Exit 0; no broken requirements |
| services/api | `GLOW_ENV=test .venv/bin/python manage.py check`; `GLOW_ENV=test .venv/bin/python manage.py test tests --verbosity 2` | Exit 0; **147 API tests**, unused DB setup skipped |
| services/api | `.venv/bin/ruff check .`; `.venv/bin/ruff format --check .`; `.venv/bin/mypy` | Exit 0; **47** format files, **23** mypy source files |
| services/api | `GLOW_ENV=test .venv/bin/python -m glow_persistence.static_check` | **32 models/two unapplied migrations** agree without SQL |
| services/api | `GLOW_ENV=test .venv/bin/python smoke.py` | Loopback live **200**, ready **503**, recommendations **200** |
| repo root | `PYTHONPATH=services/api services/api/.venv/bin/python -m unittest discover -s packages/contracts/tests -v` | **37 Python contract methods pass** |
| packages/contracts | `npm ci --ignore-scripts`; `npm run generate`; `npm run check` | Deterministic generated bytes; **212 JavaScript cases pass** |
| apps/mobile | `npm ci --ignore-scripts`; Expo install of `expo-image-picker@57.0.19`; `EXPO_OFFLINE=1 npm run check:expo` | Locked base install and SDK compatibility pass; final lock includes only two added packages |
| apps/mobile | `npm run check` | TypeScript, ESLint and **171 mobile tests pass** after all three independent review corrections; final candidate is checked separately |
| apps/mobile | `EXPO_OFFLINE=1 npm run export:development` | Both iOS/Android development JS bundles emitted; nonempty bundle metadata inspected |
| repo root | `GLOW_SMOKE_PYTHON=/absolute/path/to/services/api/.venv/bin/python node scripts/smoke.mjs`; `node --test scripts/smoke.test.mjs` | Actual mobile/API loopback smoke and startup-ownership regression pass; denied writes **405** |

The smoke Python path above is a reproduction placeholder, not a claimed universal
workspace location. Use the actual checkout's hash-locked venv. An optional
root-scope Ruff invocation encountered unrelated default rules; the project-config
invocation passed without broad source restyling.

The complete rendered suite remains a required hosted check. Local Chromium was
absent; both ordinary and headless-shell Playwright downloads returned unusable
archives before any test body ran. These are tooling failures, not media behavior
failures, and no local browser or visual pass is claimed. Docker/container evidence
comes from the hosted **API artifact checks** job. Hosted results and any fixes
are recorded below or in the external final report after observation.

## Independent review and corrective evidence

A distinct peer agent independently reviewed media implementation, integration,
dependency/configuration changes and tests. That reviewer authored the contract
extension, so its contract/generated review was self-review. The primary agent
separately inspected the complete schema/F05/OpenAPI/semantic-validator delta;
deterministic generation and shared cross-language cases validate derived outputs.
The peer independently reproduced the following issues; fixes have regressions.

| Finding | Correction and evidence |
|---|---|
| Cancelling a selected photo while Prepare awaited could still create an asset | Selection cancellation invalidates operation and adapter epoch before clearing the draft. Held-grant regression asserts no asset, no busy state and no hidden reload adoption. |
| Old approval callback could clear a newer account's delivery revocation when a scenario reused an asset ID; failed approval could also clear it | Revocation changes now occur only inside the current owner/operation-guarded validated acknowledgment. Old-generation and failed-approval regressions preserve revocation. |
| Receipt quota could prevent owner removal and provider purge after many valid reorders | Separate 128 discretionary, 20 removal and 20 purge receipt budgets preserve bounded cleanup without evicting replay receipts. The exhaustion regression passes and the reviewer independently verified it. |

All three corrections were independently reread; **55 media policy/adapter/store/
picker cases** passed in that review. The subsequent browser-seam, UI/auth harness and complete documentation
deltas were separately reviewed before publication. One README picker description
was corrected to distinguish native Expo from the browser File selector.
Review is source/fixture evidence, not production security or native acceptance.

## Dependencies and runtime effects

Only `expo-image-picker` **57.0.19** and transitive `expo-image-loader` **57.0.1**,
both MIT, were added. Existing versions remain unchanged. Inventory and lock both
contain **680** entries. The current npm audit reports **14 moderate**, zero
high/critical, involving **GHSA-vcc3-ghjq-m6fr** and **GHSA-w5hq-g745-h8pq**.
No picker/loader advisory was reported. Router's getStateFromPath imports the
affected query-string path; screen guards are not remediation. The inspected
xcode caller uses uuid.v4 rather than the advisory's v3/v5/v6 path, but that is not
a complete unreachability proof. Suggested incompatible Expo/Router downgrades
were not applied. Remaining remediation belongs before release.

No real credentials/private photos are used. No app Railway service, Cloudflare
resource or production callback is created. No database, HDE source/canon/schema/
data/roles/grants, shared Redis/Postgres, secrets, deployment or networking changes
occur. Runtime/startup guards and disabled billing remain intact.

## Publication gate and carryforward

### Initial publication and late review correction

Implementation `867cee7a1014adc5805ccb9c5be56b7b68c8a830`, tree
`41c02b166fe01e9e1edb98cbffa5ee8b37c3af08`, was published in
[PR 8](https://github.com/amthorn78/glow-dating-app/pull/8). Both candidate
[PR run 35930877276](https://github.com/amthorn78/glow-dating-app/actions/runs/35930877276)
and [push run 35930873903](https://github.com/amthorn78/glow-dating-app/actions/runs/35930873903)
passed all four jobs. The PR Mobile log confirms 171 mobile tests and 44 rendered
cases (14 media plus all 30 inherited cases), without retries or skips. Local
Chromium remained unavailable. Hosted DevTools emitted a nonfatal sandbox startup
error; Metro and the test browser completed. No visual/native-device pass is claimed.

PR 8 merged at **2026-09-23T23:00:42Z** as
`b7fb0f87a79827ebb00f9a409b59e61019652f35`, with ordered parents starting main
and implementation above and identical candidate/main trees. All 44 changed blobs
matched reviewed local content; the Foundation workflow was unchanged. Automatic
security review completed before merge at 22:59:42 UTC. Automatic code review was
still running at merge and completed at 23:01:52 UTC with
[a P1 finding](https://github.com/amthorn78/glow-dating-app/pull/8#discussion_r4088156684).
No Verified/Done transition occurred on that initial merge.

The initial merged-main [run 35931388280](https://github.com/amthorn78/glow-dating-app/actions/runs/35931388280)
passed API checks, API mobile smoke and API artifact checks, but Mobile failed two
inherited rendered cases with **42 passed**: unsaved birth-draft correction waited
for `screen-remaining` after submit; ordinary underage correction waited for
`screen-eligibility` after submit. All 14 media cases and all 171 mobile unit tests
passed. These failures are separate from the review's removal defect. Both prior
candidate runs used the same content tree and passed all 44 rendered cases; that
does not erase the main failures or establish their cause.
The failure hook recorded that both cases remained on `screen-birth`; the
workflow did not retain their error-context files. Two source reviewers could
not uniquely reproduce or attribute the failures. The original assertions,
timeouts and zero-retry configuration remain unchanged. Failure-only diagnostics
now record control presence, empty/nonempty booleans, disabled state and alert
presence, never input values, to distinguish causes if this recurs.

The finding was reproduced: failed/malformed owner removal immediately revoked
app delivery, but subsequent moderation restriction and approval could clear that
revocation while the accepted asset remained approved. Independent follow-up
review also reproduced revocation loss across inactive then active authority for
the same owner/generation, because that boundary retained the adapter asset.
The correction separates owner-removal exclusions from temporary moderation
restrictions. Reapproval cannot clear an owner's removal request; authority loss
cannot clear it while the same owner/generation still owns the retained asset.
Accepted F05 lifecycle remains distinct from the conservative delivery exclusion;
valid removal retry and provider purge are still required and supported.

The bounded follow-up branch is
`app-builder-1/p04-3-removal-revocation-fix`, based on actual main
`b7fb0f87a79827ebb00f9a409b59e61019652f35`. Its source, regressions, rendered case
and documentation require distinct review and all four final-candidate/main gates.
AB1-R008 records observed final repair checks, publication identities and review
dispositions; neither the prior green suite nor a resolved-thread flag closes the
finding without that source/regression evidence.

After the removal correction, local `npm run check` passes TypeScript, ESLint and
**175 mobile tests**. Independent review of the complete repair/test/docs delta
and all **59 media cases** passes. Two new rendered cases cover error and malformed
removal followed by restrict/reapprove/reload, retained preview revocation and
successful cleanup. The resulting **46** rendered cases require hosted execution;
discovery and source review alone are not a browser pass.

### Follow-up browser evidence and birth-draft correction

The removal repair was published as `f58475ee02462eb87435200859a6ce2939fac7dd`
in [PR 9](https://github.com/amthorn78/glow-dating-app/pull/9). Its
[push run 35932119804](https://github.com/amthorn78/glow-dating-app/actions/runs/35932119804)
passed all four jobs. Its
[PR run 35932123481](https://github.com/amthorn78/glow-dating-app/actions/runs/35932123481)
passed three jobs but Mobile failed one inherited retained underage birth case:
**45/46 rendered passed**, all 16 media cases passed, and 175 mobile/212 contract
cases passed. The prior two main failures passed in this run. Automatic code and
security reviews on this repair completed without further findings at 23:12:43
and 23:14:03 UTC respectively; PR 9 remained unmerged.

Failure-only diagnostics showed `screen-birth`, one enabled Submit, an empty
birth-date field, a nonempty place and a visible alert after both inputs had been
filled. This establishes lost input presentation, not unique attribution of all
earlier failures. Source inspection identified render-captured whole-draft merge
and submit callbacks. The correction moves the draft into a narrow synchronous
store: partial edits merge the latest snapshot and submit captures the latest
copy, while the existing account/generation/source-revision guard rejects old
callbacks. Authority replacement reconciles the draft without remounting the
navigator; unrelated publications preserve deliberate edits.

The new regression dispatches real controlled-input events for date and place in
one browser task, verifies both values and submits through the ordinary retained
underage flow. No sleep, store injection, timeout/retry change or weakened
assertion is used. Its pre-fix browser behavior was not observed locally because
Chromium remains unavailable. The new **47-case** rendered suite and final source/
unit evidence must be checked on the eventual candidate and merged main; final
identities/results remain in AB1-R008.

The final birth-draft delta passes local TypeScript/ESLint, **181 mobile tests**
(including ten birth-draft cases, six new) and both development JS exports.
The new cases cover consecutive edits/immediate submission, stable drafts and
subscription disposal, stale source/account callbacks, copied in-flight input
and precision changes. Independent review also exercises source/account changes
during an in-flight save. Browser proof still belongs to the hosted 47-case run;
local source/unit passes alone do not close it.

All four Foundation jobs must pass on the exact final candidate including docs:
**API checks**, **Mobile checks**, **API mobile smoke**, **API artifact checks**.
Recheck head/base/main, full diff and review dispositions immediately before the
already-authorized app-only merge. Reconcile any changed main. Verify ordered
merge parents, identical candidate/main content where applicable and merged-main
checks before task Done. Save actual evidence to AB1-R008 if unused and read back
Control/task/report updates. Saved reporting is not verified receipt by App Planner 1.

P04.1/P04.2/P04.3 together may close **P04 at fixture scope** only after this
integration passes. No P04 parent row exists; keep the phase statement in Control/
report without duplicating tasks. The next existing task is **P05.1 — Implement
reciprocal eligibility rules**, still Planned and unstarted by this assignment.
PV04, PV07, DB07/DB08, N01 and all other P11/release cases remain open; fixture
passes do not prove safe production processing, actual deletion, durable events,
provider enforcement or native/device quality.

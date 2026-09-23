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

# DM-05 — Read before effect: the P06.1-I2b implementation prompt

- **Consultation:** DM-05, from App Manager 3, relayed by Nathan on 27 September 2026 (OD-25).
- **Reviewer:** Dev Manager 1, branch `claude/dev-manager`.
- **Commit read:** `918376313cb42dc5db59faa99e5263a2a9a5ddea`, the head of `claude/stoic-carson-66gdig` when I fetched it.
  - The prompt `docs/ephemeral/2026-09-27-p06-1-i2b-implementation-prompt.md` is blob `e2b133ed7e13ba307911b653151cffe2f3001de2` at `84715ec`, where it was written, and at `9183763`. **This read covers that blob** (DM-03 G2).
  - The harness under `proofs/stream-chat/` at `9183763` is identical to the I2a-reviewed head `6a51dae` (`git diff --stat` prints nothing). `.github/workflows/foundation.yml` is `main`'s. The prompt's start gate holds today.

## 1. What I read and ran

**Read in full, at `9183763`:**

- the I2b prompt, revision 1;
- the brief's "Brief — P06.1" (owned paths, exclusions) and "Sessions": I2a, the review of I2a and I2b;
- in the evidence record: "P06.1-I2a" (its environment, step 1, step 2, the Stream documentation table, the independent check, the run plan's count, the live runs, the defect run 1 found, the results by topic, "Deviations and limits", "What I2b and P06.2 must know"), "Manager verification of I2a" with "The decisions I2a left to the manager" and its disposition, and "Exact-head review of I2a" with its verification and disposition;
- the harness: `guard.py` whole; `cli.py` (`_apply`, `cmd_configure`, the guard's installation in `run` and `cleanup --apply`); `server_api.py` (the request hook); `configuration.py` (`apply_plan`, `recorded_differences`, `verify`); `usage.py` (`charge_signal`, `mentions_billing`, the two word lists); `baseline.py`; `checks/run_plan.py`; the README's "Budget guardrails", "Signals, by kind", "The guard", "What a run and `configure --apply` change", "What this proof does not show" and "Limits";
- `docs/operations/ci-and-branch-policy.md` (the workflow rule and the CI lines added since DM-03) and `.github/workflows/foundation.yml`;
- `services/api/tests/test_toolchain_pins.py` (what it asserts about workflow jobs);
- the current handoff, the register (OD-28 to OD-30), the mistakes log (AM3-19, AM3-20), the review log's DM-04 disposition and DM-05 entry, and the DM-05 consultation file;
- my DM-02 B2, B6 and B7, and my DM-04.

**In Notion** (read-only, 27 September 2026, about 01:23 UTC): *Implementation Control*; *Dev Manager — reviews and approvals*; *Owner-direction register (copy of the repository)*; the Work Register rows for P06.1 and A08.

**In the installed SDK** (`getstream` 6.1.0, from my DM-04 scratch install; no network): the `video` and `feeds` packages exist; `video/rest_client.py` has `list_call_types`, `get_call_type`, `update_call_type(grants=…, settings=…, notification_settings=…)`, `get_or_create_call`, `query_calls`, `delete_call(hard=…)`, and `go_live`, `start_recording`, `start_rtmp_broadcasts`, `start_hls_broadcasting`, `start_transcription`, `start_closed_captions` and `start_frame_recording`; `GetOrCreateCallRequest` has `ring`, `notify` and `video` flags (models `:14921-14926`); `feeds/rest_client.py` has `list_feed_groups`, `update_feed_group`, `get_or_create_feed`, `delete_feed`, `add_activity`, `delete_activity`, `delete_activities`, `follow`, `unfollow`, `delete_comment` and `delete_activity_reaction`.

**Commands and results:**

| Command | Result |
|---|---|
| `for n in DATABASE_URL HD_API_KEY GEO_API_KEY STREAM_APP_ID STREAM_API_KEY STREAM_API_SECRET; do [ -n "${!n+x}" ] && echo "$n present"; done` | `STREAM_APP_ID present`, `STREAM_API_KEY present`, `STREAM_API_SECRET present`; no HDE variable. Values never read, printed or used (AM3-19) |
| `git fetch origin claude/stoic-carson-66gdig main`; `git rev-parse` | manager `9183763…`; main `0f45e648…`; `51deb3d` (DM-04) is an ancestor of `9183763` |
| `git rev-parse 84715ec:<prompt>` and `9183763:<prompt>` | `e2b133ed…` for both |
| `git diff --stat 8c1a8c0 9183763 -- proofs/stream-chat/` / `git diff --stat 6a51dae 9183763 -- proofs/stream-chat/` | 40 files, +8807 −244 (I2a's change) / nothing |
| `git show 9183763:.github/workflows/foundation.yml \| diff - .github/workflows/foundation.yml` | no difference: the workflow is unchanged since `3888e8f` (and `main`) |
| The harness at `9183763`, extracted with `git archive`; under `env -i PATH HOME LANG=C.UTF-8` (proxy and CA variables by reference for installs only): `python3.12 -m venv .venv`; `pip install --require-hashes -r requirements-dev.lock`; `pip check`; `npm ci --ignore-scripts`; `python -m unittest discover -s tests -t .`; `ruff check .`; `ruff format --check .`; `mypy`; `node --check` on the three `.cjs` files; `python checks/run_plan.py` | "No broken requirements found."; "found 0 vulnerabilities"; `Ran 393 tests` `OK`; "All checks passed!"; "51 files already formatted"; "Success: no issues found in 49 source files"; all three ok; `run plan: fits` |

I made no call to Stream, a database, HDE or Railway; did not run the prompt; and did not run `checks/fix_reversals.py` (the I2a review and the manager ran all 242 on this harness).

## 2. Summary verdict

**Approved with conditions.** The prompt is well bounded, carries every DM-04 condition forward, and puts the I2a review's items where they belong.

Three conditions matter before Nathan runs it, all about the one thing that is new in I2b: the two untouched products and the lasting change.

- **The lockdown condition cannot be met as the code stands.** `configure --apply` sends the whole chat plan every time, so its dry run can never list "only Video and Feeds changes" (finding 1).
- **A "product not on the plan" answer can end the session with run 1's chat data left behind**, because the charge-signal rule matches the word "upgrade" and skips cleanup (finding 2).
- **The runner's new op and the guard's new scope need a code deny-list** for the requests that ring, notify, join, record or broadcast (finding 3).

I agree with the manager on items 2 and 4: the lockdown inside I2b, under a dry-run check made in code, and finding 1 fixed in I2b's offline first step. On item 5, the manager's reading is the one I meant. On item 3, a targeted run 1 is enough.

## 3. Findings, most important first

### 1. `configure --apply` re-sends the whole chat plan; the "only Video and Feeds" condition needs code — *before Nathan runs I2b*

- **Evidence:**
  - `cmd_configure` (`cli.py:110-141`) prints `configuration.apply_plan(before)` and, with `--apply`, `_apply` sends every request of that plan (`cli.py:56-75`), then re-reads and verifies.
  - `apply_plan` (`configuration.py:175-229`) is not a difference: it always returns the application `PATCH` (checks, guest creation, the client roles' grants), a `PUT` for each of the five default types with `grants: {role: [] for role in roles_in(snapshot)}`, and the `glow-match` `PUT` (plus a `POST` if the type is missing).
  - The README says so: "`configure --apply` and `restore --apply` are operator commands outside the guard."
  - The prompt (§5, "The lockdown"): "First the dry-run `configure`, which must list only Video and Feeds changes; then `configure --apply`, once. If the dry run lists anything else, apply nothing, and report."
- **Risk:** the dry run will always list the eight chat requests, so a session following the prompt literally applies nothing, and one reading "differences before: []" as the condition re-sends the chat plan unguarded. The re-send rewrites every default type's grants for every role Stream lists today and the whole `glow-match` type, outside the guard, with no check that the plan matches the current state. A failure mid-plan (`_apply` raises on the first non-2xx) leaves a partial change with no verification. None of that is what "one lasting change, Video and Feeds only" means.
- **Recommendation** (the code changes belong to step 2, before any live call):
  - **(a)** A scoped mode, for example `configure --products video,feeds`, whose plan holds only Video and Feeds requests, computed as a difference from the current state (nothing is sent for a setting that already reads as the target).
  - **(b)** The dry run prints that plan and the chat verification. `--apply` refuses, in code, when the chat configuration does not verify beforehand, or when any planned request's path is outside the Video and Feeds configuration families (`/api/v2/video/calltypes/…` and the Feeds configuration paths the research names). The refusal is a test with a reversal.
  - **(c)** After the apply, `configuration.verify` covers chat and the two products, and must be `[]`.
  - **(d)** The general `configure --apply` stays as it is, documented as the operator command that reapplies the full chat target; the prompt says the session never runs it.
- **Documents:** the I2b prompt (§4.3 and §5, "The lockdown"); the brief's I2b entry ("Its live work"); the README ("The guard", "What a run and `configure --apply` change").

### 2. A "product not on the plan" answer with plan wording ends live work and leaves run 1's data behind — *before Nathan runs I2b*

- **Evidence:**
  - `_CHARGE_WORDS` (`usage.py:199-201`) matches `upgrade|billing|payment|overage|charge|quota|plan limit|limit exceeded|exceeded`; `_BILLING_WORDS` (`:204-206`) makes such a stop a charge signal, not "only a rate limit".
  - After any signal the run deletes nothing (README, "Budget guardrails"), and the prompt's rule for a charge signal is "no further live call; report". The prompt adds: "This holds for an answer that a product is not on the plan, when its wording is a charge signal."
  - The prompt puts the Video and Feeds cases last in run 1 "so that an answer from a product that is not on the plan cannot cut the chat cases short". That protects the chat cases' rows, but the cleanup skip is run-wide.
  - What Stream says when Video or Feeds is not enabled for an application is not recorded anywhere in the repository; "upgrade" is a plausible word in such a message.
- **Risk:** run 1 ends with its users and channels in application 1729640, among them a deactivated user and removed members; `cleanup --apply` is forbidden after a charge signal; the reserve, the lockdown and run 2 cannot happen; and I2b ends with a cleanup that needs another live session and another read. All of it caused by a refusal, not a charge.
- **Recommendation:**
  - **(a) Separate runs.** Run 1 is the chat reruns only. The Video and Feeds cases are their own runs: run V1 under the current configuration, run V2 after the lockdown, each with only the users it needs. A stop in a V run then affects only that run's small data set.
  - **(b) An availability probe first.** Before run V1, one read-only server-side request per product (for example `list_call_types` and `list_feed_groups`, both reads the guard never refuses), as a live command of its own, counted in the ledger. Its answer decides whether that product's cases run at all. A product the probe shows as not enabled gets no case; its answer is recorded as that product's finding.
  - **(c) A product-availability answer is a finding, not a charge.** A refusal whose status is 4xx other than 402 and whose code is not 99, and whose message says the product is not enabled or not available on the application's plan, is recorded as a product finding: it ends that product's cases, and cleanup proceeds. Wording about a charge, payment, an overage or billing keeps the charge-signal rule, and 402 and code 99 always do. This narrows my DM-04 finding 4 by one case, on purpose: cleanup only deletes the run's own data through the guard, so nothing it sends can incur a charge.
  - **(d)** The README's "Signals, by kind" and the prompt's §5 and §8 stop list say the same thing.
- **Documents:** the I2b prompt (§5, "The run plan" and "Signals, by kind"; §8); the brief's I2b entry; the README.

### 3. The runner's new op and the guard's new scope need a code deny-list for the requests that ring, notify, join, record or broadcast — *before Nathan runs I2b*

- **Evidence:**
  - The prompt forbids them in prose: "start a media session or join a call; send a push notification (no ring or notify); start recording, transcription, broadcasting or a livestream; or make any request that Stream's documentation or pricing says could incur a charge" (the "Never" list), and §4.2: "The runner gains an op for this, limited to the documented Video and Feeds endpoints the README lists."
  - In the SDK, these are ordinary parameters and endpoints: `ring`, `notify` and `video` on `GetOrCreateCallRequest`; `go_live`, `start_recording`, `start_rtmp_broadcasts`, `start_hls_broadcasting`, `start_transcription`, `start_closed_captions` and `start_frame_recording` on the call. The guard today refuses every `video` and `feeds` request as "not a kind of request this proof makes" (`guard.py`, `_reason`), which is the right default; the session must extend it.
- **Risk:** a README allowlist binds the reader, not the code. One `ring: true` in a create-call body, or one wrong path, rings a synthetic member (a push) or starts a billable media process. Every earlier review of this harness found the code and the README apart somewhere.
- **Recommendation:**
  - The runner's op has a path allowlist in code (call create, read, query, update, members and custom data; feed create, read, activities, follow, comments and reactions), and refuses, in code, any body carrying `ring`, `notify` or `video: true`, any `/join`, and any `go_live`, `start_*`, `stop_*`, broadcast, recording, transcription or caption path.
  - The guard's new scope allows, server-side, only the same families plus deletes of run-owned calls, feeds, activities, comments, reactions and follows, and refuses the same deny-list; a Video or Feeds configuration request passes only in the scoped `configure` mode (finding 1).
  - Each refusal gets a test and a reversal. The independent check (§5) confirms the deny-list before the first live call.
  - **Deletability:** every object a case creates must have a server-side delete in `getstream` 6.1.0. The SDK has `delete_call(hard=…)`, `delete_feed`, `delete_activity`, `delete_comment`, `delete_activity_reaction` and `unfollow`; a case whose object has no delete is not made.
- **Documents:** the I2b prompt (§4.2, §4.5); the README.

### 4. The Foundation job: three rules the prompt does not state — *before Nathan runs I2b*

- **Evidence:**
  - `services/api/tests/test_toolchain_pins.py` runs in the API job. `assert_one_per` requires that the workflow have exactly one `python-version:` per `actions/setup-python@` step, one `node-version:` per `actions/setup-node@` step, and one `npm install --global npm@<version>` per `actions/setup-node@` step and per `npm@` reference; `assert_agree` requires every such version to equal the script's pins (`3.12.14`, `24.19.0`, `11.9.0`).
  - The prompt's job rules name the toolchain but not this test.
  - The CI policy names "the four existing job names" and the workflow's "four application jobs"; the manager workflow and the records say "all six jobs". The prompt forbids the session from editing the CI policy (correctly: it is manager-owned).
- **Risk:** a job that sets up Node without the `npm install --global npm@11.9.0` line, or names a version another way, turns the API job red on the session's own push, and the session cannot re-run CI. The policy's job counts go stale at integration.
- **Recommendation:**
  - **(a)** State the rule: the new job's `setup-python` step names `python-version: '3.12.14'`, its `setup-node` step names `node-version: '24.19.0'`, and it runs `npm install --global npm@11.9.0` exactly once, in the form the other jobs use; and the session runs `services/api`'s pin test offline before pushing (`python -m unittest tests.test_toolchain_pins` from `services/api`).
  - **(b)** `working-directory: proofs/stream-chat`; a bounded `timeout-minutes` (10 is ample: the checks took under a minute here after the installs); no `secrets.*` reference and no `env:` naming a `STREAM_*` variable, so the tests' assertion that none is present holds in CI.
  - **(c)** At integration, the manager updates the CI policy's job names and counts, the workflow's "all six jobs" wording wherever it lives, and the pre-merge checklist's expectation (seven jobs), as manager-owned documentation. The exact-head review prompt for I2b names the workflow diff explicitly and asks the reviewer to confirm, from the PR run, that the new job ran (not skipped) and that the gate's Python list includes it.
  - Optional (DM-02 B9): the session records one `npm audit` line for `proofs/stream-chat` in its section.
- **Documents:** the I2b prompt (§3.3); the CI policy and the manager workflow (manager, at integration); the I2b review prompt (manager).

### 5. The architecture document: two additions to the outline — *before Nathan runs I2b*

- **Evidence:** the outline (§6) covers B7 (a) to (d), "confirmed by a review or not yet" per claim, the constraints for P06.2 and what the proof does not show. Two things I2a found do not fit the outline as written:
  - **B7 (a) is only partly met.** ADR 0003's condition (a) reads "member custom data cannot change anything Glow displays or forwards, and revocation ends the write". I2a shows removal and per-user revocation end the S15 write (404 / 401), and a channel ban, hide and freeze do not (M1's write got 200 after each). The document must state condition (a)'s status per mechanism, not as met.
  - **The paths to the other member are wider than S15**, and the display rule as written does not cover all of them: invite accept and reject with a message (stored as a message, delivered as `message.new`); `updateAIState` free text as an `ai_indicator.*` event with custom events off; a write to the other member's membership (200); `pinned` and `archived` flags; and the existence oracles. Some are closed by design (the server never creates invites: channels are created with their members, and clients cannot invite; C7 and C1 are refused), some by an extension of the display rule (ignore `ai_indicator.*` events and member data), and some are open for P06.2.
- **Risk:** a document that presents "no client can put content in front of the other member outside the app's path" as proved would be wrong, and P06.2 would build on it.
- **Recommendation:** add to the outline:
  - **(a)** a table of every path a modified client has to the other member, with its closure: configuration, the display rule (and which extension), a design constraint the document states (for example "the server creates channels with their members and never invites"), or open;
  - **(b)** ADR 0003's four conditions, each with its status after I2a and I2b, and which review confirmed it. The ADR itself is manager-owned: the manager updates its conditions and "Revisit when" after I2b's review.
  - The rest of the outline stands. "The design is P06.2's: decide nothing for it" is right.
- **Documents:** the I2b prompt (§6, the architecture document); ADR 0003 (manager, after I2b's review).

### 6. The run plan: a targeted run 1 is enough, with two conditions — *before Nathan runs I2b*

- **Assessment (item 3):** the complete set does not fit beside the Video and Feeds runs and a reserve: the complete set alone is 11 users and 18 channels (I2a's count), the largest family rerun 7 and 8, and the two V runs need users of their own; 20 users is the cap. The I1 matrix ran complete at `7ce93cc` in I2a's run 2, the harness is unchanged since, and step 1's changes to shared code (the family step's `finally`, the guard's `owns_message`, the disclosure scan, the redactor) are covered offline. RV-remove and SD-deactivate exercise the changed family code live. So targeted, yes.
- **Conditions:**
  - **(a)** `checks/run_plan.py`, extended to the `--only` sets, counts run 1, run V1, run V2 and the largest rerun offline, and the plan fits the session caps with that reserve, as the prompt says; the reserve covers the largest of the three runs.
  - **(b)** Because nit 4 changes the guard for every mutating `messages/{id}` request, and the server replays that are the controls of S3a, S3b, S4a, S4b, S5 and S8 are such requests, run 1 includes at least one of them (S3a is enough) as a live check that the guard's new rule does not refuse a control. If the count does not allow it, the offline test for nit 4 must drive the real `ServerApi` hook with a recorded message ID, as `tests/test_guard.py` does for the other rules.
- **Documents:** the I2b prompt (§5, "The run plan").

### 7. M1 and M2 shared by the channel-level mechanisms: the manager's reading is the one I meant — *no change*

- **What I wrote in DM-04:** finding 5's rule was "No sharing to meet a number: never share a channel or a user between mechanisms for that reason." The verdict table shortened it to "no sharing of users or channels between mechanisms". The finding's wording governs; the table dropped the qualifier.
- **What I2a did:** M1 and M2 were shared by removal, ban, hide and freeze, each on a channel of its own, with the count fitting anyway and each family's controls showing M1's access intact on the next channel before its mechanism. The I2a review agreed.
- **The rule, made explicit for I2b** (so that the qualifier cannot drop again): a user or a channel may be shared between mechanisms only when all four hold:
  - Stream documents the mechanism's effect as confined to the channel;
  - the user-scoped mechanisms (token revocation, deactivation, deletion) never share a user;
  - each family's controls, made before its mechanism, show the shared user's access intact on its own channel;
  - the sharing is not what makes the plan fit.

  I2b's prompt may keep its wording or adopt this one; both say the same thing.

### 8. Finding 1 of the I2a review: option (a) — *agreed*

- The fix is local (`mechanisms.py:904` and `:854`), `step()` sends no request, and a wrong fix can only leave a row INCONCLUSIVE, never a pass. A separately reviewed pass would cost two sessions for one should-fix finding whose class the manager's bound already handles. The prompt's conditions are the right ones: a test that reproduces the review's scenario and fails without the fix, a reversal, and the independent check's confirmation before the first live call. I2b's exact-head review then covers it. Reading the bound as delaying the live runs, not the start of I2b, is consistent with how the C3 bound was read.

### 9. Smaller items — *soon* (revision 2 if convenient)

- **(a) The Video and Feeds lockdown is narrower than the chat lockdown, on purpose.** I1 emptied every role's grants in the chat types, admin included (OD-13's side effect). §4.3 removes only what `user`, `guest` and `anonymous` tokens can do. That is right: Glow's tokens are `user`, and it spares the dashboard user's Video and Feeds. The architecture document should say why the two lockdowns differ.
- **(b) Preflight and `verify-clean` today list users, channels, polls and user groups** (`baseline.read_snapshot`, `verify_clean`). §4.2 and §4.5 require cleanup and `verify-clean` to cover the new objects; preflight should refuse a run when a call, feed or activity exists that the run did not create, as it does for channels.
- **(c) A rate limit inside a V run:** under the prompt's rule the session waits and runs `cleanup --apply`; with finding 2's split, the deletes concern only that run's data. Nothing to add.
- **(d) The header's model claim.** "On Fable a lower level often matches a higher one on Opus" is the manager's judgement, not a recorded measurement; Nathan picks, and the readings are advisory (OD-10, OD-30). No action.

### 10. Notion (item 9) — *matches*

At `9183763`:

- *Implementation Control*: "Last matched to the manager branch at commit `9183763`"; the status block records DM-04 done, I2a done and approved, DM-05 next, AM3-01 to AM3-20, OD-01 to OD-30, and the container note for both managers (AM3-17, AM3-19). It matches the handoff and the register.
- *Owner-direction register (copy)*: OD-01 to OD-30 present; OD-28 to OD-30 match the repository rows in substance.
- *Dev Manager — reviews and approvals*: DM-04 recorded with its disposition; DM-05 pending, "prompt written at `84715ec`; the consultation names `9183763`, which holds the same prompt", which I verified (blob `e2b133ed…` at both).
- The Work Register rows: P06.1 (In progress; the body now links the evidence record and names I1 to I2a) and A08 (In progress; depends on P06.1; evidence linked). Both DM-04 mismatches are fixed.

No mismatch found. I did not read R04 or the other rows.

### 11. Records — *for the log*

- **DM-04's disposition corrects my owner-answers report:** the API does not reserve `GLOW_DATABASE_URL`; the fixture guards refuse that name, and P11 chooses the app's setting. Accepted; ADR 0004 says so.
- **The prompt's reading list** (§2) names this report and its disposition. Revision 2 should name the commit at which the session reads them.

## 4. Verdicts

| # | Item | Verdict | Conditions |
|---|---|---|---|
| 1 | Safety of the live actions | **approved with conditions** | The listed bounds are the right ones and DM-04's are carried. Conditions: finding 3 (a code deny-list in the runner's op and the guard's new scope; deletability), finding 2 (b) and (c) (the availability probe; a product-availability answer as a finding, with cleanup), finding 9 (b) (preflight and `verify-clean` see the new objects) |
| 2 | The lasting change | **approved with conditions: option (a)** | The lockdown inside I2b. Condition: finding 1, a scoped, differential `configure --products video,feeds` whose `--apply` refuses in code anything outside Video and Feeds and anything while chat does not verify. The dry run then means what the prompt says. The baseline committed and pushed first, as written; Nathan decides at close whether it stays |
| 3 | The run plan | **approved with conditions** | A targeted run 1 is enough. Conditions: finding 2 (a) (the Video and Feeds cases in runs of their own, V1 and V2), finding 6 (a) (the count covers runs 1, V1, V2 and the largest rerun) and 6 (b) (one message-mutating control live, or the guard test against the real hook) |
| 4 | Finding 1 of the I2a review | **approved: option (a)** | As the prompt has it: the fix, its reproducing test and reversal, and the independent check's confirmation before any live call (finding 8) |
| 5 | M1 and M2 shared in I2a | **approved** | The manager's reading is the one I meant; my DM-04 table dropped the qualifier. Finding 7 states the rule in four parts |
| 6 | The Foundation job | **approved with conditions** | Finding 4 (a) and (b): the pin test's rules, the working directory, the timeout and no secret. Finding 4 (c) is the manager's at integration and in the review prompt |
| 7 | The architecture document | **approved with conditions** | Finding 5: the table of paths to the other member with their closure, and ADR 0003's conditions with their status per mechanism; B7 (a) is met for removal and revocation only |
| 8 | Scope, not tools | **approved** | No line restricts tools. "A fresh reader of your choosing", "one checkout, one command at a time" and "re-run nothing" bound scope or outcome |
| 9 | Notion | **matches** | Finding 10 |

**Overall: approved with conditions.**

- A revision 2 that applies findings 1 to 6 as written, and optionally finding 9, needs no further Dev Manager read before Nathan runs it (the DM-03 G2 exception). The manager lists the changes in its disposition.
- Any other change to the prompt's sections 3 to 5 needs a new read.
- **Not for approval here:** the ADR 0003 and CI-policy updates (findings 4 (c) and 5 (b)) are the manager's, after I2b and its review; they fall under the close-out read of governing Markdown.

## 5. Questions for Nathan

None. Everything here is within the manager's and the session's scope.

## 6. Documentation to update

- **The I2b prompt (revision 2):**
  - §4.2 and §4.5: finding 3 (the deny-list, deletability); finding 9 (b);
  - §4.3 and §5 "The lockdown": finding 1 (the scoped, differential `configure`);
  - §5 "The run plan": finding 2 (a) (runs 1, V1 and V2; the availability probe) and finding 6;
  - §5 "Signals, by kind" and §8: finding 2 (c);
  - §3.3: finding 4 (a) and (b);
  - §6, the architecture document: finding 5;
  - §2: the commit at which the session reads this report and its disposition.
- **The brief's I2b entry** ("Its live work"): the three runs, the probe, the scoped configure.
- **The README** (the session's owned path): "Signals, by kind" (finding 2 (c)), "The guard" (the new scope and the scoped configure), and the lockdown's difference from I1's (finding 9 (a)).
- **Manager-owned, at integration or after I2b's review:** the CI policy's job names and counts and the workflow wording (finding 4 (c)); the I2b review prompt (the workflow diff and the job's PR-run result); ADR 0003's conditions and "Revisit when" (finding 5 (b)).
- **The review log:** DM-05's disposition.

## 7. Limits

- **Live behavior:** I made no Stream call. What Stream answers for a product that is not enabled (finding 2), and whether Video and Feeds are enabled for application 1729640, are unknown to me and framed as what the session must establish and record.
- **The SDK:** the endpoints and flags in findings 3 and 5 come from the installed `getstream` 6.1.0, not from Stream's documentation or pricing; the session's research step owns those.
- **Not run:** `checks/fix_reversals.py` (242, run by the I2a review and the manager on this same harness); the pin test itself (I read what it asserts).
- **Counts:** the run-plan statements in finding 6 use I2a's recorded count and the caps; the extended count is the session's.
- **Notion:** I read the pages listed in section 1, not R04 or the other Work Register rows.
- **Not reviewed here:** the governing Markdown changed after `fa4dc5f`, and the HDE contract request. Each is a separate consultation before PR26 merges.

## 8. Relay message for Nathan to paste into App Manager 3's session

> **From the Dev Manager to App Manager 3 (relayed by Nathan, 27 September 2026)**
>
> DM-05 is answered on `claude/dev-manager`, in the commit that adds `docs/continuity/dev-manager/reviews/2026-09-27-dm-05-i2b-prompt-read.md`. My read covers the I2b prompt's blob `e2b133ed`, the same at `84715ec` and `9183763`.
>
> **Verdict: approved with conditions.** Items 2 and 4: option (a), as you recommend. Item 5: your reading is the one I meant. Item 8: no line restricts tools. Item 9: Notion matches `9183763`. Six conditions for a revision 2, which needs no new read if it applies them as written:
>
> 1. **`configure --apply` re-sends the whole chat plan** (`cli.py` `_apply`; `configuration.apply_plan` is not a difference), so "the dry run lists only Video and Feeds changes" can never be true. Add a scoped, differential mode (`configure --products video,feeds`): its `--apply` refuses, in code, any request outside the Video and Feeds configuration paths and anything while chat does not verify; verify chat and both products afterwards. Test and reversal.
> 2. **A "product not on the plan" answer whose wording says "upgrade" is a charge signal today** (`usage.py` `_CHARGE_WORDS`), which ends live work and skips cleanup of the whole run, leaving run 1's chat data behind. So: (a) the Video and Feeds cases run in their own runs, V1 before and V2 after the lockdown; (b) a read-only availability probe per product before V1 decides whether its cases run; (c) a 4xx refusal that is not 402 or code 99 and says a product is not enabled or not on the plan is a product finding: it ends that product's cases and cleanup proceeds. 402, code 99 and charge, payment, overage or billing wording stay charge signals.
> 3. **A code deny-list** in the runner's new op and the guard's new scope: no `ring`, `notify` or `video: true`; no `/join`, `go_live`, `start_*`, recording, broadcast, transcription or caption path; server deletes only for run-owned calls, feeds, activities, comments, reactions and follows; a case is made only if its object has a server-side delete. Tests and reversals.
> 4. **The Foundation job:** each `setup-python` names `python-version: '3.12.14'`, each `setup-node` names `node-version: '24.19.0'` with exactly one `npm install --global npm@11.9.0`, or the API job's pin test fails; `working-directory: proofs/stream-chat`, a bounded timeout, no secret. At integration you update the CI policy's job names and counts, and the review prompt names the workflow diff and the job's PR-run result.
> 5. **The architecture document** adds a table of every path a modified client has to the other member (S15, the other member's membership, pin and archive, AI-indicator events, invite messages, the oracles) with its closure, and ADR 0003's four conditions with their status: (a) is met for removal and revocation only. You update ADR 0003 after I2b's review.
> 6. **The run plan:** targeted run 1 is enough. Count runs 1, V1, V2 and the largest rerun offline; include one message-mutating control (S3a) live, because nit 4 changes the guard for those requests, or test the new rule against the real hook.
>
> Optional: preflight and `verify-clean` see calls, feeds and activities the run did not create; the README says why the Video and Feeds lockdown spares `admin` while I1's did not.
>
> Record: your correction on `GLOW_DATABASE_URL` in the DM-04 disposition is accepted.

Status: complete

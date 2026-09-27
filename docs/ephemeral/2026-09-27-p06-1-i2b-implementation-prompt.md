# P06.1-I2b implementation prompt — other products, the architecture document and CI, live

- **Owner:** App Manager 4 (revision 1 was App Manager 3's). Nathan starts this session manually and relays its report.
- **Revision 2, 27 September 2026.** Revision 1 (blob `e2b133ed`, at `84715ec` and `9183763`) was read by the Dev Manager, DM-05, and approved with conditions. Revision 2 applies its findings 1 to 6 as written, its optional finding 9 (a) and (b), and the four-part sharing rule of its finding 7, which the report offers as an equivalent wording. Under DM-03 G2 it needs no further read before Nathan runs it; the manager lists the changes in the [review log](../continuity/dev-manager/README.md), "DM-05".
- **Durable brief:** [P06.1 brief](../planning/p06-1-chat-provider-proof.md): "Brief — P06.1" (owned paths, credential rules, budget guardrails, the matrix quality rule), "S15: decided" and "Sessions" (P06.1-I2b).
  - The Dev Manager's specification of I2b: [DM-02](../continuity/dev-manager/reviews/2026-09-25-dm-02-build-review.md), B2 (I2b), B6 (the harness in CI) and B7 (the reapplicable configuration plan); and its read of this prompt, [DM-05](../continuity/dev-manager/reviews/2026-09-27-dm-05-i2b-prompt-read.md).
  - The offline first step's work list: the [evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md), "Exact-head review of I2a", its findings and the manager's disposition; and the manager's verification of I2a, "The decisions I2a left to the manager".
- **Where the result goes:**
  - the session adds a section "P06.1-I2b" at the end of the evidence record, writes the architecture document and brings the harness README into line;
  - the manager adds its verification there and records the outcome in the brief's "Sessions".
- **Model and reasoning level** (OD-10, OD-30). Neither reading gates anything, and Nathan picks.
  - **Manager: Fable 5.1, extra high,** decided at 01:58 UTC, before TypeSafe's readings of this revision. This is P06.1's last live session. It fixes the I2a review's findings, one of them before any live call; implements two new verdict rules; adds a CI job; researches two Stream products the proof has never touched, builds a guarded client op and a scoped, differential configuration command for them, and locks them down by a lasting configuration change; reruns destructive cases live; and writes the architecture document P06.2 builds on. A miss could cost a charge, an unintended configuration change or a false claim a design rests on, so the most capable model is most likely to change the outcome. Extra high rather than max, in the manager's judgement: on Fable a lower level often matches a higher one on Opus. I2a ran at max on Opus 5.5. The manager does not recommend ultracode: it is one session, and the session can split its work across subagents itself.
  - **TypeSafe v4** (this revision's description, sent 01:58:50 UTC): extra high (score 3.04, P(extra high) 0.96, P(max) 0.04). It raises its ultracode flag: the shape is `broad_verification` at 0.52, and P(single session) is 0.44. Revision 1's reading was extra high with no flag (P(single session) 0.56).
  - **TypeSafe m1** (sent 01:58:51 UTC): Fable 5.1 (P(most capable) 0.99, confidence 0.98). Revision 1's reading was Fable 5.1 (0.94).
- **Dev Manager read: done** (DM-01 P1). DM-05 read revision 1 and approved it with conditions; this revision applies them as written.
- **Stream variables** (OD-28): Nathan makes sure `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` for application 1729640 are set in the `Glow app` environment, starts this one session, then deletes them.
- **It runs alone** (OD-29, the linear process). Its exact-head review follows it, then the economics discovery and the delta review of the final head.
- **Deletion condition:** prune after P06.1 closes and the evidence record and brief hold the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision, the DM-05 report and its disposition.

---

You are the **implementation session for P06.1-I2b**, other products, the architecture document and CI, in the chat-provider permissions proof of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 2, from commit `<START_SHA>`.

P06.1 tests Stream's permission model against Nathan's development Stream application 1729640, with synthetic users only, using the sandbox harness in `proofs/stream-chat/`. P06.1-I1 locked the application's chat down and ran the bypass matrix. Three offline correction passes followed, and P06.1-I2a added the revocation and safety cases and ran them live. I2a's exact-head review, of the merge commit `6a51dae`, approved the harness as a sound base for your live runs, and left two should-fix findings and four nits. The manager decided two verdict rules I2a left open, and the review refined them. The Dev Manager read revision 1 of this prompt (DM-05) and set conditions; this revision carries them, and section 2 tells you where to read its report.

Your work, in this order:

1. **Offline first step:** the I2a review's items, the two rules, I2a's other harness items and the Foundation job (section 3). No Stream call until its checks pass.
2. **Video and Feeds, offline:** what the two products let a user token do, the cases that show it, the runner op and guard scope with their deny-list, the scoped configuration command, and a lockdown by configuration (section 4).
3. **An independent check of steps 1 and 2, then the live work,** within the run plan: run 1 (chat), the availability probe, run V1, the baseline, the lockdown and run V2 (section 5).
4. **Records:** the architecture document, the README and your section of the evidence record (section 6).

- Nathan started you manually and will relay your report to the manager (App Manager 4). You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs. Live commands follow section 5: one checkout, one command at a time.
- Your boundary is scope:
  - write only your owned paths (section 6);
  - push only your own session branch. On GitHub do nothing else: no pull request, no PR comments, no re-runs, no workflow dispatches. Change nothing in Notion.
- **Never:**
  - dump the environment, or print, copy, log or write `STREAM_API_SECRET` or a full token;
  - connect to a database, HDE, Railway or any provider other than Stream. On Stream, act only on application 1729640, and only as sections 4 and 5 allow;
  - run `playwright install`, `eas` or `migrate`;
  - run `restore --apply`, or the general `configure --apply`, which re-sends the whole chat plan. The one lasting change is `configure --products video,feeds --apply`, once, under section 5's rules;
  - start a media session or join a call; send a push notification (no ring or notify); start recording, transcription, broadcasting or a livestream; or make any request that Stream's documentation or pricing says could incur a charge. Section 4 puts these refusals in code;
  - change what the brief excludes: nothing in the Stream organization outside application 1729640; no plan, billing, Maker or team change; no product enabled or disabled; no key rotation or region change; no webhook or hook; no push configuration; no real people or personal data.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` must be set and non-empty, for application 1729640: `for n in STREAM_APP_ID STREAM_API_KEY STREAM_API_SECRET; do [ -n "${!n}" ] && echo "$n set" || echo "$n MISSING"; done`. If any is missing, do sections 3 and 4, make no live call, and report.
3. Record `command -v node npm npx python3.12` and their versions. Expected: v24.19.0, 11.9.0 and Python 3.12.14, from `$HOME/.local/bin`.
4. Run the harness's commands in a clean process environment, as its README's "Install", "Checks (offline)" and "Live commands" sections show.
   - The offline checks run without any `STREAM_*` variable.
   - Installs get the proxy and CA variables by reference, never printed.
   - A live command's server process gets the three `STREAM_*` variables through its environment only: never in a command-line argument, a file or any output.

## 2. Start gate

```bash
git fetch origin claude/stoic-carson-66gdig main
git merge --ff-only <START_SHA>          # on your own session branch
git rev-parse HEAD                       # must print <START_SHA>
git diff --stat 6a51dae3e0f2b7a69097151fb5e5dcfe4414b61d HEAD -- proofs/stream-chat/   # must print nothing
git diff --stat origin/main HEAD -- .github/                                           # must print nothing
```

The fourth command shows that the harness is unchanged since the reviewed head, so the review's line numbers still apply; the fifth, that the workflow is `main`'s. If any check fails, stop and report.

Then read, completely, at `<START_SHA>`:

- root `AGENTS.md` and `CLAUDE.md`;
- the P06.1 brief, `docs/planning/p06-1-chat-provider-proof.md`: "Brief — P06.1", "S15: decided", "I1's open questions: manager dispositions" and "Sessions" (P06.1-I2a, the review of I2a and P06.1-I2b);
- `docs/adr/0003-chat-display-rule.md`, with its "Conditions (DM-02 B7)";
- the evidence record, `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md`, whole. In particular:
  - "P06.1-I2a", I2a's own record, with "What I2b and P06.2 must know";
  - the manager's verification of I2a, with "The decisions I2a left to the manager";
  - "Exact-head review of I2a", your offline work list, and its disposition;
- DM-02's B2, B6 and B7, in `docs/continuity/dev-manager/reviews/2026-09-25-dm-02-build-review.md`;
- the Dev Manager's read of revision 1 of this prompt, `docs/continuity/dev-manager/reviews/2026-09-27-dm-05-i2b-prompt-read.md`, whole, and the manager's disposition of it in `docs/continuity/dev-manager/README.md`, "DM-05". Both are at `<START_SHA>`. Where this prompt and the report differ in detail, this prompt governs, and you report the difference;
- `docs/operations/ci-and-branch-policy.md`, `.github/workflows/foundation.yml` and `services/api/tests/test_toolchain_pins.py` (what it asserts about the workflow);
- `proofs/stream-chat/README.md` and the whole harness.

## 3. Step 1, offline: the I2a review's items, the two rules and the Foundation job

The work list is the evidence record's "Exact-head review of I2a": its findings 1 to 6, with the manager's disposition. The rules come from the manager's verification of I2a, as the review left them.

1. **Required, before any live call:**
   - **Finding 1** (`mechanisms.py:904`, and `apply` at `:854`): an interruption inside a family step must not lose that step's observations. Judge and keep the row after each member's observations, or in a `finally` around each step; `step()` sends no request. A test reproduces the review's scenario (RV-ban; M1's read after the ban succeeds; a 402 on M2's read) and fails without the fix: the row keeps M1's observation, and a DOES NOT MEET it shows stays.
   - **Finding 2** (`i2a.py:889`): the existence oracle compares two successes by shape, keys and list lengths, without `duration`, never by size. Each pair keeps both normalized messages in its row, so a FAIL on text can be read.
   - **Nit 3's listener and retention tests:** a family test in which every session misses the probe (`mechanisms.py:1145`), and one with the channel present and the history message gone (`:1210`). Each fails with the review's mutation.
   - **Nit 4:** the guard checks `owns_message` for every mutating `messages/{id}` path (`POST` and `PUT`, `/action`, `/reaction` and `/undelete`), not only for a delete (`guard.py:306`). The README's limit on message IDs changes with it. Because this changes the guard for every mutating message request, and the server replays that are the controls of S3a, S3b, S4a, S4b, S5 and S8 are such requests, section 5 puts one of those controls (S3a) in run 1 as a live check that the new rule refuses no control. If the count does not allow it, your offline test for this nit must drive the real `ServerApi` request hook with a recorded message ID, as `tests/test_guard.py` does for the other rules (DM-05 finding 6 (b)).
   - **Nit 5:** one offline test that sends the real runner each op the Python side uses, and checks the reply's shape. Today the real runner is driven offline for `selfcheck`, `ping`, `set_rest_user`, a channel `call`, `get`'s budget refusal and `exit`, but not for `connect`, `guest`, `anonymous`, `disconnect` or `events`, nor for a `call` with `channel_data`. The new Video and Feeds op (section 4) joins this test.
   - **Nit 6, the record:** the two sentences on H's re-creation, in "P06.1-I2a", corrected in place and marked "(corrected in P06.1-I2b)". The re-creation is inferred from the connects' success; no read of the user shows it.
   - **The disclosure rule** (F9-thread and F9-sync): the disclosure scan leaves out every term that appears, as a substring, anywhere in the serialized request (path, query and body), because the sender already had it. F9-sync carries `{XD}` inside the cid. The row keeps the key names of the response where a term was found.
   - **404 code 16 as "ended":** a dimension counts as ended on a 404 code 16 only when all three hold, and otherwise stays "not shown":
     - the same request by the same member succeeded before the mechanism;
     - the other member's identical request, already collected, still succeeds after it;
     - Stream's message, kept in the row, names the missing membership or user.

     It applies only where the mechanism removes what the request needs: the membership after a removal (RV-remove), the user after a deactivation (SD-deactivate). The README states the rule.
   - **A `sync` pair in the existence oracle:** whether `sync` answers differently for an existing and a missing channel.
   - **The API key in free text:** the redactor removes the application's API key from free text in every output, as it does the secret. Stream's code-43 message quotes it.
   - **The poll listing:** read Stream's API reference for Query Polls. Then either list polls as each of the run's own users before that user is deleted, or confirm each recorded poll gone by ID. Until one of those shows the polls absent, the listing stays "not verified" and is reported; on its own, it stops nothing (section 5).
2. **Fixed, or left with a one-line reason:** nit 3's other six tests (`mechanisms.py:1104`; `i2a.py:1061`, `:560`, `:896` and `:345`; `configuration.py:266`).
3. **The Foundation job** (DM-02 B6; the brief's owned paths; DM-05 finding 4). One new job in `.github/workflows/foundation.yml` runs the harness's offline checks, as the README's "Install" and "Checks (offline)" sections give them:
   - the hash-locked install and `pip check`, and `npm ci --ignore-scripts`;
   - the unit tests under `env -i`, Ruff check and format, mypy, `node --check` on every `.cjs` file, and `checks/run_plan.py`.

   Its rules:
   - it runs under the same condition as the other application jobs (the change-scope output), with the same action pins and `persist-credentials: false`, and `working-directory: proofs/stream-chat` as its run default;
   - **the pin test's rules** (`services/api/tests/test_toolchain_pins.py`, which runs in the API job and reads the workflow): its `actions/setup-python@` step names `python-version: '3.12.14'`; its `actions/setup-node@` step names `node-version: '24.19.0'`; and it runs `npm install --global npm@11.9.0` exactly once, in the form the other jobs use (`- run: npm install --global npm@11.9.0` with `working-directory: ${{ github.workspace }}`, right after the setup-node step). The test requires exactly one such version per setup step and one `npm@` reference per install, all equal to the pins; a job that names a version another way, or sets up Node without that install line, turns the API job red on your own push. Before you push, run the pin test offline from `services/api`: `python3.12 -m unittest tests.test_toolchain_pins` (it reads files only; the manager ran it at `<START_SHA>`: 3 tests, OK);
   - a bounded `timeout-minutes` (10 is ample: the checks take under a minute after the installs);
   - it needs no secret, and none is given to it: no `secrets.*` reference, and no `env:` naming a `STREAM_*` variable, so the tests' assertion that none is present holds in CI;
   - the gate requires it: add it to the gate's `needs` and to the gate's Python list of jobs. Change nothing else in the workflow: not its triggers, permissions or concurrency, the scope job, the other jobs or the gate's logic;
   - the fix reversals stay out of CI (they take about 15 minutes); sessions and reviews run them;
   - after you push, read your push run's result for the new job if you can, and report it. Re-run nothing;
   - optional (DM-02 B9): record one `npm audit` result line for `proofs/stream-chat` in your section.
4. **Rules for every fix,** as for C1 to I2a:
   - each code fix gets an offline test that fails without it and passes with it, and a reversal in `checks/fix_reversals.py`;
   - the credential rules, the matrix quality rule and the README's stop rules stand. Never weaken a verdict rule to make a test pass;
   - no dependency change.
5. **Before any live call,** the offline checks pass (section 7, checks 3 to 6), and `checks/fix_reversals.py` shows every reversal demonstrated, each failing for its stated reason. Commit this step on its own, before step 2's changes.

## 4. Step 2, offline: Video and Feeds

The brief: "Video and Feeds: what a user token can do, and a lockdown by configuration only. No media session, no push, nothing that could incur a charge." The README's "What this proof does not show" lists both products as untested. Glow uses neither.

1. **Research first.** From Stream's current official documentation and the installed SDK sources (`getstream` 6.1.0 covers Video and Feeds on the server side), establish and record, with the pages you rely on:
   - whether each product is available to application 1729640 on its plan, and how to tell without enabling anything. Section 5's availability probe is the live check; name here the read-only server request it makes for each product (for example `list_call_types` for Video and `list_feed_groups` for Feeds), and what Stream is documented to answer when a product is not enabled;
   - what a user token can do in each by default. For Video: creating, updating, reading and querying calls, adding members, and custom data on a call. For Feeds: creating and reading feeds and activities, following, comments and reactions, and custom data;
   - which of those could reach the other member, as S15 did: text or data the other member can read, or events it receives;
   - how each product's permissions are configured (for Video, call types and their grants; for Feeds, what the documentation gives), and whether I1's empty `.app` grants already govern them. Name the configuration paths for each product (Video's `/api/v2/video/calltypes/…`, and the Feeds configuration paths the documentation gives): the scoped `configure` of item 3 allows exactly those;
   - what each request could cost on the application's plan, from Stream's pricing and fair-use pages. A request whose cost is unclear is not made;
   - **deletability** (DM-05 finding 3): for every object a case would create, the server-side delete in `getstream` 6.1.0 that removes it. The SDK has `delete_call(hard=…)`, `delete_feed`, `delete_activity`, `delete_comment`, `delete_activity_reaction` and `unfollow`. A case whose object has no server-side delete is not made.
2. **The cases.** One case for each capability a user token may have, under the matrix quality rule:
   - the request is made with a user's own token, from a client process that never holds the secret. **The runner gains an op for this, with a path allowlist in code** (DM-05 finding 3): call create, read, query, update, members and custom data; feed create, read, activities, follow, comments and reactions. The op refuses, in code, any body carrying `ring`, `notify` or `video: true`; any `/join` path; and any `go_live`, `start_*`, `stop_*`, broadcast, recording, transcription or caption path. The README lists the allowed endpoints, and the code, not the README, enforces them;
   - **the guard's new scope, server-side:** the guard allows only the same families, plus deletes of run-owned calls, feeds, activities, comments, reactions and follows, and refuses the same deny-list. A Video or Feeds configuration request passes only in the scoped `configure` mode of item 3; during `run` it is refused;
   - each refusal of the op and of the guard gets a test and a reversal. The independent check (section 5) confirms the deny-list before the first live call;
   - its positive control is the same request succeeding: by the same user before the lockdown, or, where no user may make it, by the server, to show the request is well formed;
   - a refusal counts only as Stream's authentication or permission error, recorded by status and code. An answer that a product is not enabled or not available to the application is recorded as that product's finding, under section 5's rule for it.

   Every object a case creates (a call, a feed, an activity, a follow) has an ID the guard can attribute to the run. The server changes or deletes it only through the guard, and cleanup removes it; `verify-clean` confirms that none remains. **Preflight and `verify-clean` see the new objects** (DM-05 finding 9 (b)): today they list users, channels, polls and user groups (`baseline.read_snapshot`, `verify_clean`); they now list calls, feeds and activities too, and preflight refuses a run when a call, feed or activity exists that the run did not create, as it does for channels.
3. **The lockdown, by configuration only.** Every capability a `user`, `guest` or `anonymous` token has in Video or Feeds is removed, and nothing else changes.
   - `baseline` gains a read-only snapshot of the two products' configuration (settings and grants only; no users or data), committed as a new file in `baseline/`. The committed chat baseline does not change.
   - **A scoped, differential `configure`** (DM-05 finding 1): `configure --products video,feeds`. Its plan holds only Video and Feeds requests, computed as a difference from the current state: nothing is sent for a setting that already reads as the target. Its dry run prints that plan and the chat verification (`configuration.verify` of the current state). `configure --products video,feeds --apply` refuses, in code, when the chat configuration does not verify beforehand, or when any planned request's path is outside the Video and Feeds configuration families (Video's `/api/v2/video/calltypes/…`, and the Feeds configuration paths your research names). Each refusal is a test with a reversal. After the apply, it re-reads and verifies chat and both products, and `configuration.verify` must be `[]`.
   - The general `configure --apply` stays as it is, documented in the README as the operator command that reapplies the full chat target (`apply_plan` is not a difference: it re-sends the application `PATCH`, the five default types and `glow-match` every time). You never run it.
   - `configuration.verify` compares the Video and Feeds target too, so preflight, the end of every run and the dry-run `configure` see any drift. `restore` can return the new baseline, and is not run.
   - **Why this lockdown is narrower than I1's** (DM-05 finding 9 (a)): I1 emptied every role's grants in the chat types, admin included (OD-13's side effect); this one removes only what `user`, `guest` and `anonymous` tokens can do, and spares the dashboard user's Video and Feeds. The README and the architecture document say so.
   - A capability that configuration cannot remove, or that only disabling a product or changing the plan could remove, is recorded plainly as a finding, as S15 was, and left for Nathan's decision.
4. **Offline tests,** against the fakes, cover each new case, the runner's new op, its cap and its deny-list, the guard's new scope and its deny-list, the scoped `configure` (its difference, its dry run, its refusals and its verification), the configuration target and its verification, preflight's and `verify-clean`'s new listings, the cleanup of every new object, the availability probe and the product-finding rule (section 5), and every new request's stop rules.
5. **Rules for every new case,** as in I2a:
   - **only the run's own data:** every change the server makes goes through the guard. Never revoke tokens application-wide, and never change or delete the dashboard user;
   - **temporary settings** go through the run's journal and are restored and verified. The Video and Feeds lockdown is the one lasting change;
   - **cleanup** removes everything the new cases create, and `verify-clean` confirms it. Test that against the fakes.

## 5. Step 3: an independent check, then the live work

- **An independent check before the first live call,** by a fresh reader of your choosing, as I2a used. It focuses on:
  - finding 1's fix, which it confirms before any live call;
  - the two rules and the oracle's changes;
  - the guard, including its new Video and Feeds scope, and the deny-list in the guard and in the runner's op (DM-05 finding 3);
  - the stop path of every new request, the cost of every Video and Feeds request, and the product-finding rule below;
  - the scoped `configure`: its plan is a difference, holds only Video and Feeds requests, and its `--apply` refuses anything else and anything while chat does not verify;
  - the cleanup of every new object, and preflight's and `verify-clean`'s new listings.

  Fix what it finds, and record its findings and fixes in your section.
- **Before any run:** `verify-clean` and the dry-run `configure`.
  - Expected: no proof users, channels, user groups, calls, feeds or activities; one other user, the dashboard user; "differences before: []".
  - The poll listing may be "not verified". If that is the only reason `verify-clean` exits non-zero, go on and report it.
  - If the application holds anything else (a `deleted-user-1729640-…` user, a leftover proof user or any channel), or the configuration differs, make no live run, and report.
- **Each live command that changes anything starts from a committed and pushed head** (DM-04 finding 8), at which the offline checks and the fix reversals pass, and its record names that commit. Later commits are listed as not exercised live.
- **The run plan** (one run in reserve; DM-05 findings 2 and 6). The harness's per-session guardrails stand: 20 synthetic users, 30 channels, 10 concurrent connections and 5,000 API calls, counted across every run of one checkout.
  - **Count first:** before any live call, `checks/run_plan.py`, extended to the `--only` sets, counts the users, channels and peak connections of run 1, run V1, run V2 and the largest rerun, offline, and adds what this checkout's ledger already holds. The plan fits only if the four together fit the session caps, with the reserve covering the largest of the three runs. Record the count.
  - **Run 1, the chat reruns only,** as one `run --accept-dashboard-user --only <case ids>`, in this order:
    - RV-remove and SD-deactivate, under the rule for 404 code 16, with Stream's messages kept;
    - F9-thread and F9-sync, under the disclosure rule;
    - the existence oracle's cases, with the `sync` pair and both normalized messages kept;
    - S3a, as a live check that nit 4's guard rule refuses no message-mutating control (section 3). If the count does not allow it, leave it out and say so; the offline test against the real hook then stands in.

    Run 1 is targeted, not I2a's complete set: the families share the code that finding 1 changes, and RV-remove and SD-deactivate exercise it live.
  - **The availability probe,** after run 1 and before run V1: for each product, one read-only server-side request, as your research named it (for example `list_call_types` and `list_feed_groups`; the guard never refuses a read), as a live command of its own, counted in the ledger. Its answer decides whether that product's cases run at all. A product the probe shows as not enabled gets no case, and the probe's answer is recorded as that product's finding.
  - **Run V1,** the Video and Feeds cases under the current configuration, as its own `run --only <case ids>`, with only the users it needs. A stop in it then affects only its own small data set.
  - **The Video and Feeds baseline,** read-only, then committed and pushed, before any configuration change.
  - **The lockdown,** only if run V1 showed a capability to remove. First the dry run, `configure --products video,feeds`, which must list only Video and Feeds changes and show chat verifying; then `configure --products video,feeds --apply`, once. If the dry run lists anything else, or chat does not verify, apply nothing, and report.
  - **Run V2,** only after the lockdown: the Video and Feeds cases again, as its own run.
  - **Sharing users or channels between mechanisms** (DM-05 finding 7): allowed only when all four hold: Stream documents the mechanism's effect as confined to the channel; the user-scoped mechanisms (token revocation, deactivation, deletion) never share a user; each family's controls, made before its mechanism, show the shared user's access intact on its own channel; and the sharing is not what makes the plan fit.
  - **If it does not fit** (runs 1, V1 and V2 and the largest rerun over the session caps): no live run, and report.
  - **Reserve:** at most one rerun, `run --accept-dashboard-user --only <case ids>`, for cases runs 1, V1 and V2 could not complete. It must fit what the session has left.
  - **Nothing else live,** beyond the commands this section names and `cleanup --apply`. Fix harness errors offline, against the fakes, never by trying a live run. If the reserve is spent, report the cases not run.
- **One place, one at a time.** Every live command runs in sequence from one checkout, so one ledger counts every call and no cleanup overlaps another run.
- **Cleanup.** Use `cleanup --apply` only for your own runs' leftovers. If a `deleted-user-1729640-…` user remains after `cleanup --apply`, report it and leave it.
- **After the last live command:** `verify-clean` and the dry-run `configure` (both the general dry run and the scoped one) again. Report the outputs. If either reports a difference, do not fix it: report it, and the manager decides.
- **Signals, by kind** (the README's "Budget guardrails"; DM-05 finding 2 (c)):
  - **a charge signal:** HTTP 402, Stream code 99, or wording about billing, payment, an upgrade, an overage, a charge, a quota or a plan limit. No further live call; report. 402 and code 99 are always charge signals, and so is any answer whose wording is about a charge, a payment, an overage or billing;
  - **a product-availability answer is a finding, not a charge:** a refusal whose status is 4xx other than 402, whose code is not 99, and whose message says the product is not enabled or not available on the application's plan, is recorded as that product's finding. It ends that product's cases, and cleanup proceeds, because cleanup deletes only the run's own data through the guard, so nothing it sends can incur a charge. The harness's signal rule and the README's "Signals, by kind" say the same, with a test and a reversal; a `_CHARGE_WORDS` match on "upgrade" alone, in such an answer, does not make it a charge signal, and charge, payment, overage or billing wording still does;
  - **only a rate limit** (HTTP 429 or Stream code 9): wait at least the rate-limit window, then run `cleanup --apply` once, `verify-clean` and the dry-run `configure`. The reserve stays available if those pass. A second rate limit ends live work.
- **Preflight stops:** make no further live call, and report. Never bypass a stop, and report anything the harness marks "not verified".

## 6. Owned paths, push and records

- **You may change:**
  - `proofs/stream-chat/**`, except the committed baseline, `baseline/application-1729640-2026-09-25.json`, and the dependency files: `requirements.in`, `requirements-dev.in`, both `.lock` files, `package.json`, `package-lock.json`, `.npmrc` and the dependencies in `pyproject.toml`. If a dependency change seems needed, leave that part and report why;
  - `.github/workflows/foundation.yml`: the one new job and the gate's two references to it (section 3), and nothing else;
  - `docs/architecture/chat-provider-permissions.md`, a new file (below);
  - `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md`: your section at its end, and in-place corrections of earlier claims that were false when written, each marked "(corrected in P06.1-I2b)". Keep every recorded result: a correction changes a claim about a result, never the result.
- **Never change these sections** of the evidence record, each with everything under it:
  - "Manager verification (App Manager 3, 25 September 2026)" and "Exact-head review of I1 (25 September 2026)";
  - "Manager verification (App Manager 3, 26 September 2026)" and "Exact-head review of C1 (26 September 2026)";
  - "Manager verification of C2 (App Manager 3, 26 September 2026)" and "Exact-head review of C2 (26 September 2026)";
  - "Manager verification of C3 (App Manager 3, 26 September 2026)" and "Exact-head review of C3 (26 September 2026)";
  - "Manager verification of I2a (App Manager 3, 26 September 2026)" and "Exact-head review of I2a (27 September 2026)".
- **Nothing else,** including the brief, the ADRs, the CI policy, `apps/`, `services/`, the rest of `.github/` and every other document. Report any other change you think is needed. The CI policy's job names and counts, and ADR 0003's conditions, are the manager's to update after your session (DM-05 findings 4 (c) and 5 (b)).
- **Commit and push** your session branch, with step 1 in its own commit. Don't open a pull request.
- **The architecture document,** `docs/architecture/chat-provider-permissions.md` (DM-02 B7; DM-05 finding 5):
  - the design under proof, and what the proof shows. Each claim links to its evidence and says whether a review has confirmed it or not yet (DM-01 P4);
  - **a table of every path a modified client has to the other member,** with its closure: S15 (member custom data), the other member's membership, `pinned` and `archived`, AI-indicator events, invite accept and reject with a message, and the existence oracles, each closed by configuration, by the display rule (and which extension of it: for example ignoring `ai_indicator.*` events and member data), by a design constraint the document states (for example "the server creates channels with their members and never invites"), or open for P06.2;
  - **ADR 0003's four conditions, (a) to (d), each with its status** after I2a and I2b and the review that confirmed it. Condition (a), "member custom data cannot change anything Glow displays or forwards, and revocation ends the write", is met for removal and per-user revocation only (I2a: 404 and 401 after them; a channel ban, hide and freeze left M1's write at 200); state its status per mechanism, not as met. The ADR itself is manager-owned;
  - the exact configuration, chat and now Video and Feeds, as a reviewed, reapplicable plan for a future production application: the harness's `configure` with a fixed target application, and why the Video and Feeds lockdown spares `admin` while I1's did not. The development application's lockdown is not a production control (B7 (c));
  - the display rule (ADR 0003) and S15; member custom data in deletion and export at Stream (B7 (b)); per-person channels as the recorded fallback (B7 (d));
  - what the revocation findings, the free-text paths and the existence oracles mean for P06.2, as constraints and open questions. The design is P06.2's: decide nothing for it;
  - what the proof does not show.
- **Your section, "P06.1-I2b",** at the end of the evidence record:
  - the start SHA, your head and your branch;
  - step 1: each item, fixed (`file:line` and its test) or left (the reason); the Foundation job, the pin test's result and the job's first result;
  - Video and Feeds: the pages relied on, each capability, its cost and its delete, the cases and their verdict rules, the runner op's and the guard's deny-lists, and the scoped `configure`;
  - the independent check's findings and fixes;
  - the run plan's count, for run 1, V1, V2 and the largest rerun;
  - each live command: the commit it started from, its prefix, UTC start and end, command, exit code, results table, usage and cleanup, and the checks before and after; the probe's answers by product;
  - the Video and Feeds baseline, the scoped dry run's plan and chat verification, the apply and its verification;
  - the commits after the last live command, listed as not exercised live;
  - the results: RV-remove and SD-deactivate under the rule for 404 code 16; F9-thread and F9-sync under the disclosure rule; the existence oracle, with its messages and the `sync` pair; S3a's control; the poll listing; each product's availability; and Video and Feeds before and after the lockdown;
  - every check, with its exact results;
  - deviations and limits;
  - what P06.2 and the delta review must know.

## 7. Checks

Report the exact commands and results.

1. `git diff --check <START_SHA> HEAD`, and `git diff --name-only <START_SHA> HEAD`: only owned paths changed.
2. Classification with the trusted policy from `main`, run outside the tree, as root `AGENTS.md` requires. Expected: full scope.

   ```bash
   base=$(git rev-parse origin/main); policy_dir=$(mktemp -d)
   git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
   python3 -I "$policy_dir/change_scope.py" --base <START_SHA> --head "$(git rev-parse HEAD)" --merge-base
   ```

3. The installs from the locks, with the README's commands, in clean processes.
4. The offline checks, with the README's commands: the unit tests (393 at the start; the counts at step 1's commit and at your head), Ruff check and format, mypy, `node --check` on every `.cjs` file, and `checks/run_plan.py` with its count of run 1, V1, V2 and the largest rerun.
5. `checks/fix_reversals.py` (242 at the start; the counts at step 1's commit and at your head), with none "not demonstrated", and each failure reason read.
6. The pin test, from `services/api`: `python3.12 -m unittest tests.test_toolchain_pins`, OK at every commit that touches the workflow.
7. `git diff <START_SHA> HEAD -- .github/`: exactly the new job and the gate's two references to it.
8. A secret scan over your whole diff and over every live output you keep or quote: no secret, token, JWT-shaped string, API key or email address.
9. The live commands, and `verify-clean` and the dry-run `configure` before and after them.

## 8. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 2, from commit `<START_SHA>`), and any difference you found between this prompt and DM-05's report;
- your branch, head SHA and tree, step 1's commit, and the changed paths;
- the environment check (names only);
- step 1: each item, fixed (`file:line` and the test) or left (the reason); the Foundation job's diff, the pin test's result, and the job's first result if you could read it;
- Video and Feeds: each product's availability, what a user token could do, what the lockdown changed, and anything configuration could not remove;
- the independent check's findings and fixes, and the run plan's count;
- each live command: the commit it started from, prefix, UTC start and end, command, exit code, results, usage and cleanup, and the checks before and after; and the commits after the last live command, not exercised live;
- the results, as in your section;
- every check, with its exact results;
- deviations, limits, open questions, and what P06.2 and the delta review must know.

**Stop and report** if:

- an HDE variable is present;
- application 1729640 holds data your runs did not create, other than the dashboard user;
- a charge signal (HTTP 402, Stream code 99, or wording about a charge, a payment, an overage, billing, a quota or a plan limit), any other signal that is not only a rate limit, or a second rate limit (section 5, "Signals, by kind"). A product-availability answer under section 5's rule is a finding, not a stop: it ends that product's cases, and the rest of the plan goes on;
- the secret or a full token appears in any output, log or file. Remove it, and say where it was;
- the work needs a path outside your owned paths, a dependency change, a configuration change other than the scoped Video and Feeds lockdown, or a product enabled, disabled or changed in plan.

Skipped or unavailable checks are not passes.

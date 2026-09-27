# P06.1-I2b implementation prompt — other products, the architecture document and CI, live

- **Owner:** App Manager 3. Nathan starts this session manually and relays its report.
- **Revision 1, 27 September 2026.** The Dev Manager reads it before Nathan runs it (DM-05).
- **Durable brief:** [P06.1 brief](../planning/p06-1-chat-provider-proof.md): "Brief — P06.1" (owned paths, credential rules, budget guardrails, the matrix quality rule), "S15: decided" and "Sessions" (P06.1-I2b).
  - The Dev Manager's specification of I2b: [DM-02](../continuity/dev-manager/reviews/2026-09-25-dm-02-build-review.md), B2 (I2b), B6 (the harness in CI) and B7 (the reapplicable configuration plan).
  - The offline first step's work list: the [evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md), "Exact-head review of I2a", its findings and the manager's disposition; and the manager's verification of I2a, "The decisions I2a left to the manager".
- **Where the result goes:**
  - the session adds a section "P06.1-I2b" at the end of the evidence record, writes the architecture document and brings the harness README into line;
  - the manager adds its verification there and records the outcome in the brief's "Sessions".
- **Model and reasoning level** (OD-10, OD-30). Neither reading gates anything, and Nathan picks.
  - **Manager: Fable 5.1, extra high,** decided before TypeSafe's readings. This is P06.1's last live session. It fixes the I2a review's findings, one of them before any live call; implements two new verdict rules; adds a CI job; researches two Stream products the proof has never touched and locks them down by a lasting configuration change; reruns destructive cases live; and writes the architecture document P06.2 builds on. A miss could cost a charge, an unintended configuration change or a false claim a design rests on, so the most capable model is most likely to change the outcome. Extra high rather than max: on Fable a lower level often matches a higher one on Opus. I2a ran at max on Opus 5.5.
  - **TypeSafe v4:** extra high (score 3.02, P(extra high) 0.96, P(max) 0.03, P(high) 0.01), with no ultracode flag (P(single session) 0.56).
  - **TypeSafe m1:** Fable 5.1 (P(most capable) 0.94, confidence 0.87).
- **Dev Manager read: required** (DM-01 P1), because the prompt authorizes credential use, live provider actions and a lasting configuration change. DM-05 reads revision 1.
- **Stream variables** (OD-28): Nathan adds `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` for application 1729640 to the `Glow app` environment, starts this one session, then deletes them.
- **It runs alone** (OD-29, the linear process). Its exact-head review follows it, then the economics discovery and the delta review of the final head.
- **Deletion condition:** prune after P06.1 closes and the evidence record and brief hold the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds the revision given.

---

You are the **implementation session for P06.1-I2b**, other products, the architecture document and CI, in the chat-provider permissions proof of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<START_SHA>`.

P06.1 tests Stream's permission model against Nathan's development Stream application 1729640, with synthetic users only, using the sandbox harness in `proofs/stream-chat/`. P06.1-I1 locked the application's chat down and ran the bypass matrix. Three offline correction passes followed, and P06.1-I2a added the revocation and safety cases and ran them live. I2a's exact-head review, of the merge commit `6a51dae`, approved the harness as a sound base for your live runs, and left two should-fix findings and four nits. The manager decided two verdict rules I2a left open, and the review refined them.

Your work, in this order:

1. **Offline first step:** the I2a review's items, the two rules, I2a's other harness items and the Foundation job (section 3). No Stream call until its checks pass.
2. **Video and Feeds, offline:** what the two products let a user token do, the cases that show it, and a lockdown by configuration (section 4).
3. **An independent check of steps 1 and 2, then the live work,** within the run plan (section 5).
4. **Records:** the architecture document, the README and your section of the evidence record (section 6).

- Nathan started you manually and will relay your report to the manager (App Manager 3). You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs. Live commands follow section 5: one checkout, one command at a time.
- Your boundary is scope:
  - write only your owned paths (section 6);
  - push only your own session branch. On GitHub do nothing else: no pull request, no PR comments, no re-runs, no workflow dispatches. Change nothing in Notion.
- **Never:**
  - dump the environment, or print, copy, log or write `STREAM_API_SECRET` or a full token;
  - connect to a database, HDE, Railway or any provider other than Stream. On Stream, act only on application 1729640, and only as sections 4 and 5 allow;
  - run `playwright install`, `eas` or `migrate`;
  - run `restore --apply`, or `configure --apply` other than once, for the Video and Feeds lockdown (section 5);
  - start a media session or join a call; send a push notification (no ring or notify); start recording, transcription, broadcasting or a livestream; or make any request that Stream's documentation or pricing says could incur a charge;
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

Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`;
- the P06.1 brief, `docs/planning/p06-1-chat-provider-proof.md`: "Brief — P06.1", "S15: decided", "I1's open questions: manager dispositions" and "Sessions" (P06.1-I2a, the review of I2a and P06.1-I2b);
- `docs/adr/0003-chat-display-rule.md`;
- the evidence record, `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md`, whole. In particular:
  - "P06.1-I2a", I2a's own record, with "What I2b and P06.2 must know";
  - the manager's verification of I2a, with "The decisions I2a left to the manager";
  - "Exact-head review of I2a", your offline work list, and its disposition;
- DM-02's B2, B6 and B7, in `docs/continuity/dev-manager/reviews/2026-09-25-dm-02-build-review.md`;
- the Dev Manager's read of this prompt, `docs/continuity/dev-manager/reviews/2026-09-27-dm-05-i2b-prompt-read.md`, and the manager's disposition of it in `docs/continuity/dev-manager/README.md`, "DM-05";
- `docs/operations/ci-and-branch-policy.md` and `.github/workflows/foundation.yml`;
- `proofs/stream-chat/README.md` and the whole harness.

## 3. Step 1, offline: the I2a review's items, the two rules and the Foundation job

The work list is the evidence record's "Exact-head review of I2a": its findings 1 to 6, with the manager's disposition. The rules come from the manager's verification of I2a, as the review left them.

1. **Required, before any live call:**
   - **Finding 1** (`mechanisms.py:904`, and `apply` at `:854`): an interruption inside a family step must not lose that step's observations. Judge and keep the row after each member's observations, or in a `finally` around each step; `step()` sends no request. A test reproduces the review's scenario (RV-ban; M1's read after the ban succeeds; a 402 on M2's read) and fails without the fix: the row keeps M1's observation, and a DOES NOT MEET it shows stays.
   - **Finding 2** (`i2a.py:889`): the existence oracle compares two successes by shape, keys and list lengths, without `duration`, never by size. Each pair keeps both normalized messages in its row, so a FAIL on text can be read.
   - **Nit 3's listener and retention tests:** a family test in which every session misses the probe (`mechanisms.py:1145`), and one with the channel present and the history message gone (`:1210`). Each fails with the review's mutation.
   - **Nit 4:** the guard checks `owns_message` for every mutating `messages/{id}` path (`POST` and `PUT`, `/action`, `/reaction` and `/undelete`), not only for a delete (`guard.py:306`). The README's limit on message IDs changes with it.
   - **Nit 5:** one offline test that sends the real runner each op the Python side uses, and checks the reply's shape. Today the real runner is driven offline for `selfcheck`, `ping`, `set_rest_user`, a channel `call`, `get`'s budget refusal and `exit`, but not for `connect`, `guest`, `anonymous`, `disconnect` or `events`, nor for a `call` with `channel_data`.
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
3. **The Foundation job** (DM-02 B6; the brief's owned paths). One new job in `.github/workflows/foundation.yml` runs the harness's offline checks, as the README's "Install" and "Checks (offline)" sections give them:
   - the hash-locked install and `pip check`, and `npm ci --ignore-scripts`;
   - the unit tests under `env -i`, Ruff check and format, mypy, `node --check` on every `.cjs` file, and `checks/run_plan.py`.

   Its rules:
   - it runs under the same condition as the other application jobs (the change-scope output), with the same action pins, `persist-credentials: false`, the toolchain the other jobs use (Python 3.12.14, Node 24.19.0 and npm 11.9.0) and a bounded timeout. It needs no secret, and none is given to it;
   - the gate requires it: add it to the gate's `needs` and to the gate's list of jobs. Change nothing else in the workflow: not its triggers, permissions or concurrency, the scope job, the other jobs or the gate's logic;
   - the fix reversals stay out of CI (they take about 15 minutes); sessions and reviews run them;
   - after you push, read your push run's result for the new job if you can, and report it. Re-run nothing.
4. **Rules for every fix,** as for C1 to I2a:
   - each code fix gets an offline test that fails without it and passes with it, and a reversal in `checks/fix_reversals.py`;
   - the credential rules, the matrix quality rule and the README's stop rules stand. Never weaken a verdict rule to make a test pass;
   - no dependency change.
5. **Before any live call,** the offline checks pass (section 7, checks 3 to 5), and `checks/fix_reversals.py` shows every reversal demonstrated, each failing for its stated reason. Commit this step on its own, before step 2's changes.

## 4. Step 2, offline: Video and Feeds

The brief: "Video and Feeds: what a user token can do, and a lockdown by configuration only. No media session, no push, nothing that could incur a charge." The README's "What this proof does not show" lists both products as untested. Glow uses neither.

1. **Research first.** From Stream's current official documentation and the installed SDK sources (`getstream` 6.1.0 covers Video and Feeds on the server side), establish and record, with the pages you rely on:
   - whether each product is available to application 1729640 on its plan, and how to tell without enabling anything;
   - what a user token can do in each by default. For Video: creating, updating, reading and querying calls, adding members, and custom data on a call. For Feeds: creating and reading feeds and activities, following, comments and reactions, and custom data;
   - which of those could reach the other member, as S15 did: text or data the other member can read, or events it receives;
   - how each product's permissions are configured (for Video, call types and their grants; for Feeds, what the documentation gives), and whether I1's empty `.app` grants already govern them;
   - what each request could cost on the application's plan, from Stream's pricing and fair-use pages. A request whose cost is unclear is not made.
2. **The cases.** One case for each capability a user token may have, under the matrix quality rule:
   - the request is made with a user's own token, from a client process that never holds the secret. The runner gains an op for this, limited to the documented Video and Feeds endpoints the README lists;
   - its positive control is the same request succeeding: by the same user before the lockdown, or, where no user may make it, by the server, to show the request is well formed;
   - a refusal counts only as Stream's authentication or permission error, recorded by status and code. An answer that a product is not available to the application is recorded as that product's finding.

   Every object a case creates (a call, a feed, an activity, a follow) has an ID the guard can attribute to the run. The server changes or deletes it only through the guard, and cleanup removes it; `verify-clean` confirms that none remains.
3. **The lockdown, by configuration only.** Every capability a `user`, `guest` or `anonymous` token has in Video or Feeds is removed, and nothing else changes.
   - `baseline` gains a read-only snapshot of the two products' configuration (settings and grants only; no users or data), committed as a new file in `baseline/`. The committed chat baseline does not change.
   - `configure` gains the Video and Feeds target. Its dry run lists each change; `configure --apply` applies, re-reads and verifies it; `restore` can return the new baseline, and is not run.
   - `configuration.verify` compares the Video and Feeds target too, so preflight and the end of every run see any drift.
   - A capability that configuration cannot remove, or that only disabling a product or changing the plan could remove, is recorded plainly as a finding, as S15 was, and left for Nathan's decision.
4. **Offline tests,** against the fakes, cover each new case, the runner's new op and its cap, the guard's new scope, the configuration target and its verification, the cleanup of every new object, and every new request's stop rules.
5. **Rules for every new case,** as in I2a:
   - **only the run's own data:** every change the server makes goes through the guard. Never revoke tokens application-wide, and never change or delete the dashboard user;
   - **temporary settings** go through the run's journal and are restored and verified. The Video and Feeds lockdown is the one lasting change;
   - **cleanup** removes everything the new cases create, and `verify-clean` confirms it. Test that against the fakes.

## 5. Step 3: an independent check, then the live work

- **An independent check before the first live call,** by a fresh reader of your choosing, as I2a used. It focuses on:
  - finding 1's fix, which it confirms before any live call;
  - the two rules and the oracle's changes;
  - the guard, including its new Video and Feeds scope;
  - the stop path of every new request, and the cost of every Video and Feeds request;
  - the lockdown's target: `configure --apply` changes only Video and Feeds, and nothing chat needs;
  - the cleanup of every new object.

  Fix what it finds, and record its findings and fixes in your section.
- **Before any run:** `verify-clean` and the dry-run `configure`.
  - Expected: no proof users, channels or user groups; one other user, the dashboard user; "differences before: []".
  - The poll listing may be "not verified". If that is the only reason `verify-clean` exits non-zero, go on and report it.
  - If the application holds anything else (a `deleted-user-1729640-…` user, a leftover proof user or any channel), or the configuration differs, make no live run, and report.
- **Each live command that changes anything starts from a committed and pushed head** (DM-04 finding 8), at which the offline checks and the fix reversals pass, and its record names that commit. Later commits are listed as not exercised live.
- **The run plan** (one run in reserve). The harness's per-session guardrails stand: 20 synthetic users, 30 channels, 10 concurrent connections and 5,000 API calls, counted across every run of one checkout.
  - **Count first:** before any live call, `checks/run_plan.py`, extended, counts the users, channels and peak connections of runs 1 and 2 and of the largest rerun, offline. Record the count.
  - **Run 1,** as one `run --accept-dashboard-user --only <case ids>`, in this order:
    - RV-remove and SD-deactivate, under the rule for 404 code 16, with Stream's messages kept;
    - F9-thread and F9-sync, under the disclosure rule;
    - the existence oracle's cases, with the `sync` pair and both normalized messages kept;
    - last, the Video and Feeds cases under the current configuration. An answer from a product that is not on the plan then cannot cut the chat cases short.
  - **The Video and Feeds baseline,** read-only, then committed and pushed, before any configuration change.
  - **The lockdown,** only if run 1 showed a capability to remove. First the dry-run `configure`, which must list only Video and Feeds changes; then `configure --apply`, once. If the dry run lists anything else, apply nothing, and report.
  - **Run 2,** only after the lockdown: the Video and Feeds cases again.
  - **No sharing to meet a number:** never share a channel or a user between mechanisms for that reason.
  - **If it does not fit** (runs 1 and 2 and the largest rerun over the session caps): no live run, and report.
  - **Reserve:** at most one rerun, `run --accept-dashboard-user --only <case ids>`, for cases runs 1 and 2 could not complete. It must fit what the session has left.
  - **Nothing else live,** beyond the commands this section names and `cleanup --apply`. Fix harness errors offline, against the fakes, never by trying a live run. If the reserve is spent, report the cases not run.
- **One place, one at a time.** Every live command runs in sequence from one checkout, so one ledger counts every call and no cleanup overlaps another run.
- **Cleanup.** Use `cleanup --apply` only for your own runs' leftovers. If a `deleted-user-1729640-…` user remains after `cleanup --apply`, report it and leave it.
- **After the last live command:** `verify-clean` and the dry-run `configure` again. Report both outputs. If `configure` reports any difference, do not fix it: report it, and the manager decides.
- **Signals, by kind** (the README's "Budget guardrails"):
  - **a charge signal** (HTTP 402, Stream code 99, or wording about billing, payment, an upgrade, an overage, a charge, a quota or a plan limit): no further live call; report. This holds for an answer that a product is not on the plan, when its wording is a charge signal;
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
- **Nothing else,** including the brief, the ADRs, the CI policy, `apps/`, `services/`, the rest of `.github/` and every other document. Report any other change you think is needed.
- **Commit and push** your session branch, with step 1 in its own commit. Don't open a pull request.
- **The architecture document,** `docs/architecture/chat-provider-permissions.md` (DM-02 B7):
  - the design under proof, and what the proof shows. Each claim links to its evidence and says whether a review has confirmed it or not yet (DM-01 P4);
  - the exact configuration, chat and now Video and Feeds, as a reviewed, reapplicable plan for a future production application: the harness's `configure` with a fixed target application. The development application's lockdown is not a production control (B7 (c));
  - the display rule (ADR 0003) and S15; member custom data in deletion and export at Stream (B7 (b)); per-person channels as the recorded fallback (B7 (d));
  - what the revocation findings, the free-text paths and the existence oracles mean for P06.2, as constraints and open questions. The design is P06.2's: decide nothing for it;
  - what the proof does not show.
- **Your section, "P06.1-I2b",** at the end of the evidence record:
  - the start SHA, your head and your branch;
  - step 1: each item, fixed (`file:line` and its test) or left (the reason); the Foundation job and its first result;
  - Video and Feeds: the pages relied on, each capability and its cost, and the cases and their verdict rules;
  - the independent check's findings and fixes;
  - the run plan's count;
  - each live run: the commit it started from, its prefix, UTC start and end, command, exit code, results table, usage and cleanup, and the checks before and after;
  - the Video and Feeds baseline, the dry run's plan, the apply and its verification;
  - the commits after the last live command, listed as not exercised live;
  - the results: RV-remove and SD-deactivate under the rule for 404 code 16; F9-thread and F9-sync under the disclosure rule; the existence oracle, with its messages and the `sync` pair; the poll listing; and Video and Feeds before and after the lockdown;
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
4. The offline checks, with the README's commands: the unit tests (393 at the start; the counts at step 1's commit and at your head), Ruff check and format, mypy, `node --check` on every `.cjs` file, and `checks/run_plan.py`.
5. `checks/fix_reversals.py` (242 at the start; the counts at step 1's commit and at your head), with none "not demonstrated", and each failure reason read.
6. `git diff <START_SHA> HEAD -- .github/`: exactly the new job and the gate's two references to it.
7. A secret scan over your whole diff and over every live output you keep or quote: no secret, token, JWT-shaped string, API key or email address.
8. The live commands, and `verify-clean` and the dry-run `configure` before and after them.

## 8. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<START_SHA>`);
- your branch, head SHA and tree, step 1's commit, and the changed paths;
- the environment check (names only);
- step 1: each item, fixed (`file:line` and the test) or left (the reason); the Foundation job's diff, and its first result if you could read it;
- Video and Feeds: what a user token could do, what the lockdown changed, and anything configuration could not remove;
- the independent check's findings and fixes, and the run plan's count;
- each live run: the commit it started from, prefix, UTC start and end, command, exit code, results, usage and cleanup, and the checks before and after; and the commits after the last live command, not exercised live;
- the results, as in your section;
- every check, with its exact results;
- deviations, limits, open questions, and what P06.2 and the delta review must know.

**Stop and report** if:

- an HDE variable is present;
- application 1729640 holds data your runs did not create, other than the dashboard user;
- a charge signal, any other signal that is not only a rate limit, or a second rate limit (section 5, "Signals, by kind");
- the secret or a full token appears in any output, log or file. Remove it, and say where it was;
- the work needs a path outside your owned paths, a dependency change, a configuration change other than the Video and Feeds lockdown, or a product enabled, disabled or changed in plan.

Skipped or unavailable checks are not passes.

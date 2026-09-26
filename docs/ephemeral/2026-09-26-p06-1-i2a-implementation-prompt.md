# P06.1-I2a implementation prompt — revocation and safety, live

- **Owner:** App Manager 3. Nathan starts this session manually and relays its report.
- **Revision 2, 26 September 2026.** It applies the Dev Manager's DM-04 conditions, findings 1 to 8, and its optional finding 9, as written, and nothing else. Revision 1 was read by the Dev Manager and never given to Nathan to run.
- **Durable brief:** [P06.1 brief](../planning/p06-1-chat-provider-proof.md): "Brief — P06.1" (owned paths, credential rules, budget guardrails, the matrix quality rule), "S15: decided" and "Sessions" (P06.1-I2a).
  - The Dev Manager's specification of I2a and its claim limits: [DM-02](../continuity/dev-manager/reviews/2026-09-25-dm-02-build-review.md), B2.
  - The Dev Manager's read of revision 1: [DM-04](../continuity/dev-manager/reviews/2026-09-26-dm-04-i2a-prompt-read.md).
  - The offline first step's work list: the [evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md), "Exact-head review of C3", its findings and the manager's disposition.
- **Where the result goes:**
  - the session adds a section "P06.1-I2a" at the end of the evidence record, and brings the harness README into line;
  - the manager adds its verification there and records the outcome in the brief's "Sessions".
- **Reasoning level.** Neither reading gates anything, and Nathan picks.
  - Manager: max. The session writes new code for about ten case families and runs it live for the first time, with the secret, including destructive actions on its own data (bans, suspension, hard deletes, token revocation), with one run in reserve. Every earlier review of this harness found defects in its stop handling.
  - TypeSafe v4, read for revision 1: extra high (score 2.98, P(extra high) 0.99), with no ultracode flag (P(single session) 0.56).
  - **Used: max, on Opus 5.5.** Nathan started this session on 26 September. This line was added after the prompt was given; the body Nathan pasted is unchanged.
- **Result:** live work complete, verified by the manager and integrated at `6a51dae`. Run 1 stopped before any case on a reply-matching defect, fixed offline; the reserve rerun ran all 114 cases. No Stream mechanism meets the history policy on its own. See the evidence record, "P06.1-I2a", and the manager's verification under it.
- **Dev Manager read: done** (DM-01 P1), because the prompt authorizes credential use and live provider actions. The Dev Manager read revision 1 at `d50b572` (DM-04) and approved it with conditions. Revision 2 applies them as written, so it needs no further read (DM-03 G2); the close-out read confirms the changes.
- **Stream variables** (OD-28): Nathan adds `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` for application 1729640 to the `Glow app` environment, starts this one session, then deletes them.
- **It runs alone** (OD-29, the linear process). Its exact-head review follows it, and I2b comes after that review.
- **Deletion condition:** prune after P06.1 closes and the evidence record and brief hold the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **implementation session for P06.1-I2a**, revocation and safety, in the chat-provider permissions proof of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 2, from commit `<START_SHA>`.

P06.1-I1 built a sandbox harness in `proofs/stream-chat/` and ran its bypass matrix against Nathan's development Stream application 1729640, with synthetic users only. Three offline correction passes, C1 to C3, and their exact-head reviews followed. C3's review, of the merge commit `8c1a8c0`, approved the harness as a sound base for your live runs, and left six nits and one gap. The Dev Manager's read of this prompt (DM-04) added a guard, closing checks and a check before the first live call.

Your work, in this order:

1. **Offline first step:** the C3 review's items, the guard and the closing checks (section 3). No Stream call until its checks pass.
2. **The I2a cases:** extend the harness with the brief's I2a topics, with offline tests (section 4).
3. **An independent check of steps 1 and 2, then the live runs,** within the run plan (section 5).
4. **Records:** the README and your section of the evidence record (section 6).

- Nathan started you manually and will relay your report to the manager (App Manager 3). You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs. Live commands follow section 5: one checkout, one command at a time.
- Your boundary is scope:
  - write only your owned paths (section 6);
  - push only your own session branch. On GitHub do nothing else: no pull request, no PR comments, no re-runs, no workflow dispatches. Change nothing in Notion.
- **Never:**
  - dump the environment, or print, copy, log or write `STREAM_API_SECRET` or a full token;
  - connect to a database, HDE, Railway or any provider other than Stream. On Stream, act only on application 1729640, and only as sections 4 and 5 allow;
  - run `playwright install`, `eas` or `migrate`;
  - run `configure --apply` or `restore --apply`;
  - change what the brief excludes: nothing in the Stream organization outside application 1729640; no plan, billing, Maker or team change; no key rotation or region change; no webhook or hook; no push; no real people or personal data.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` must be set and non-empty, for application 1729640: `for n in STREAM_APP_ID STREAM_API_KEY STREAM_API_SECRET; do [ -n "${!n}" ] && echo "$n set" || echo "$n MISSING"; done`. If any is missing, do sections 3 and 4, make no live run, and report.
3. Record `command -v node npm npx python3.12` and their versions. Expected: v24.19.0, 11.9.0 and Python 3.12.14, from `$HOME/.local/bin`.
4. Run the harness's commands in a clean process environment, as its README's "Install", "Checks (offline)" and "Live commands" sections show.
   - The offline checks run without any `STREAM_*` variable.
   - Installs get the proxy and CA variables by reference, never printed.
   - A live command's server process gets the three `STREAM_*` variables through its environment only: never in a command-line argument, a file or any output. The I1 review started it through a small launcher that copied an allowlisted environment.

## 2. Start gate

```bash
git fetch origin claude/stoic-carson-66gdig
git merge --ff-only <START_SHA>          # on your own session branch
git rev-parse HEAD                       # must print <START_SHA>
git diff --stat 8c1a8c08d77052a86cfc70fc38cb830eb641438a HEAD -- proofs/stream-chat/   # must print nothing
```

The last command shows that the harness is unchanged since the reviewed head, so the review's line numbers still apply. If any check fails, stop and report.

Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`;
- the P06.1 brief, `docs/planning/p06-1-chat-provider-proof.md`: "Brief — P06.1", "S15: decided", "I1's open questions: manager dispositions" and "Sessions" (P06.1-I2a);
- `docs/adr/0003-chat-display-rule.md`;
- the evidence record, `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md`, whole. In particular:
  - the I1 review's findings 4, 6 and 9;
  - the three "What P06.1-I2a must know" lists, in C1's, C2's and C3's sections;
  - "Exact-head review of C3", your offline work list;
- DM-02's B2, in `docs/continuity/dev-manager/reviews/2026-09-25-dm-02-build-review.md`;
- the Dev Manager's DM-04 report, `docs/continuity/dev-manager/reviews/2026-09-26-dm-04-i2a-prompt-read.md`, whose conditions revision 2 applies, and the manager's disposition of it in `docs/continuity/dev-manager/README.md`;
- in `docs/architecture/production-contracts.md`: flows F10, F11 and F13, and the paragraph under "Pagination, idempotency and stale state" that makes a block or unmatch commit the boundary for new sends; and DB06 in `docs/testing/p11-deferred-acceptance.md`;
- `proofs/stream-chat/README.md` and the whole harness.

## 3. Step 1, offline: the C3 review's items, the guard and the closing checks

The work list is the evidence record's "Exact-head review of C3": its findings 1 to 6, and the gap in its "Limits". The manager's disposition there sets what is required. DM-04 adds the guard and the closing checks.

1. **Required, before any live call:**
   - **Nit 1:** RT3 searches the control window for the marker too, and leaves out only B's own read events: type `message.read` or `notification.mark_read` whose `user.id` is B. Bring README line 160 into line.
   - **The gap:** every request a client session sends, including any the SDK sends between commands, and every asynchronous SDK error, are checked for a charge or limit signal like any other client request. A signal found is recorded in the ledger and stops the run at once, as the README's "Budget guardrails" describe. Today the runner starts each command with `records = []` (`client/runner.cjs:304`), and `_send` only notes asynchronous errors (`proof_run.py:403-407`).
   - **Nit 2(a):** a test that a 402 or code-99 signal met during the cleanup ends it.
   - **The guard** (DM-04 finding 1): every server call that bans, deactivates, deletes, revokes tokens, hides, freezes, removes a member, or updates a user or member goes through one guard. Before sending, it refuses two kinds of call:
     - any target user ID or channel ID the run did not create (its recorded IDs, or IDs containing its prefix);
     - any `PATCH /api/v2/app` other than a journalled temporary setting.

     Each refusal gets an offline test and a reversal in `checks/fix_reversals.py`. Step 2's new calls go through it too.
   - **The closing checks** (DM-04 finding 2): `configuration.verify` compares every application setting the baseline records against the recorded value, except the ones the lockdown sets on purpose (guest creation). At the least, it covers `revoke_tokens_issued_before` and the four hook fields. Preflight, the end of the run and the dry-run `configure` all rely on it; today none of them can see an application-wide token revocation or a hook change. It gets a test and a reversal.
2. **Fixed, or left with a one-line reason:** nits 2(b) and 2(c), 3, 4, 5 and 6, as the review suggests; and DM-04's finding 9(c): `_delete_users` lists users for its prefix scan without `include_deactivated_users` (`proof_run.py:2883-2886`), which `baseline.read_snapshot` passes.
3. **Rules for every fix,** as for C1 to C3:
   - each code fix gets an offline test that fails without it and passes with it, and a reversal in `checks/fix_reversals.py`;
   - the credential rules, the matrix quality rule and the README's stop rules stand. Never weaken a verdict rule to make a test pass;
   - no dependency change.
4. **Before any live call,** the offline checks pass (section 7, checks 3 to 5), and `checks/fix_reversals.py` shows every reversal demonstrated, each failing for its stated reason. Commit this step on its own, before step 2's changes.

## 4. Step 2: the I2a cases

The brief's "P06.1-I2a" entry and DM-02's B2 define the topics. Take every Stream behavior from Stream's current official documentation, the installed SDK sources and what the live application does, and record the pages you rely on.

1. **Revocation, under Nathan's history policy** (OD-12): after an unmatch or block, neither person can send or see the conversation, and the history is kept out of sight only for safety reports.
   - The mechanisms: member removal, a channel-level ban, the per-user `revoke_tokens_issued_before`, hiding the channel and freezing it.
   - For each, record which of these it ends, for the member it is applied to and for the other member:
     - REST reads of the channel;
     - an **already-open WebSocket subscription**: whether it still receives the channel's events;
     - token reuse: whether the member's existing token still works;
     - the S15 write, `updateMemberPartial` on its own membership.
   - For each, record whether the affected member's own client can undo it, under the same control rule: show a hidden channel, rejoin after removal, lift its own ban, unfreeze the channel. A mechanism a client can reverse does not meet the history policy (DM-04 finding 6).
   - For each, and for each member: the event types it receives, excluding the SDK's local events; any system message the provider adds to the channel; and whether they name who acted (DM-04 finding 6).
   - After each, a server-side read shows whether the channel's messages are retained.
   - Record which mechanism, or combination, meets the policy.
2. **Suspension and deletion:**
   - Stream's mechanism for suspending a user, from its documentation (record which), and a hard user delete, with its options recorded.
   - Record what each does to the user's messages and to its member custom data, which safety reports need. A hard delete conflicts with the history policy unless the design says otherwise, so record the result plainly.
3. **Tokens and devices:** token expiry, reconnection, and use across two devices, with two client sessions for one user, including what a revocation on one device does to the other. Record each token's `iat` against the revocation time: the SDK back-dates `iat` by 5 s, so a token issued within about 5 s after a per-user `revoke_tokens_issued_before` is refused by design (DM-04 finding 9(b)).
4. **Send versus revocation, on the provider side only.** After each mechanism, the app send path refuses without calling Stream. Server-side calls bypass Stream's permission checks, so Stream's answer to a server-side send on the revoked member's behalf is recorded as an observation, not a verdict, and the README states that rule before the run (DM-04 finding 9(a)). The database-level ordering is P11's DB06: claim nothing more.
5. **Outage, as fault injection only, inside the process** (DM-04 finding 3). Give the server's Stream client a transport that raises a connection error (`httpx.ConnectError`), through `ServerApi`'s `transport` parameter, so that the SDK's error path runs and no request leaves the process. The app send path must refuse, with no partial state.
   - If an address is used anyway, show that a connection to it is refused immediately before the case, and record that. In this environment the egress proxy listens on a loopback address.
   - No real outage is claimed.
6. **The S15 mapping** (the brief's "S15: decided"; the I1 review's finding 4):
   - which member fields a member can set;
   - what the other member receives, and in which event types, with the SDK's local events excluded;
   - whether the server can clear or overwrite member custom data;
   - whether member removal deletes it.

   The configuration check keeps the three `member_custom_on_*` settings off; confirm that it reads them live.
7. **G2 and S10, with new setups** (the I1 review's finding 6):
   - G2's guest is created on the server side (`ServerApi.create_guest`) and connects by its ID only;
   - S10 needs a new setup, because its type-level toggle did not reach the channel in time.
8. **The endpoints the I1 matrix never tried** (the I1 review's finding 9):
   - content or effects in front of the other member: `updateAIState`, `partialUpdateMember` on the other member, `pin` and `archive`, invites with an `acceptInvite` or `rejectInvite` message, leaving with a message, and a ban or shadow ban of the other member;
   - reads outside the match: `sync`, replies, reactions and messages by ID, `queryReactions`, `getThread` and `queryMessageHistory`.
9. **The existence oracle:** whether a refusal for an existing ID differs from one for an ID that does not exist, for users, channels and messages.
10. **The I1 matrix again,** as the first live use of C1's, C2's and C3's fixes, and of step 1's.

**Rules for every new case:**

- **The matrix quality rule** (the brief):
  - a refusal counts only as Stream's authentication or permission error, recorded by status and code;
  - every negative case pairs with a positive control of the same request. For revocation, the control is the same request by the same member, succeeding before the mechanism;
  - a result that does not hold is a finding, reported as observed. The README states each new verdict rule.
- **Only the run's own data.** Mechanisms act only on the run's synthetic users and channels, and every destructive call goes through step 1's guard. Never revoke tokens application-wide. Never change or delete the dashboard user, and read nothing of it beyond what preflight compares.
- **Temporary settings** go through the run's journal and are restored and verified, as the README describes. A lasting configuration change is out of scope: if a case seems to need one, leave the case and report why.
- **Cleanup** removes everything the new cases create, whatever state a mechanism left it in (banned, suspended, deleted, hidden or frozen), and `verify-clean` confirms it. Test that against the fakes.
- **Offline tests** cover each new case's logic, against the fakes, and every new request's guardrails and stop rules.

## 5. Step 3: an independent check, then the live runs

- **An independent check before the first live call** (DM-04 finding 7). With a fresh reader of your choosing, as C2 and C3 used, make an independent review pass over steps 1 and 2. It focuses on:
  - the guard;
  - the stop path of every new request;
  - cleanup of every new state (banned, deactivated, hidden, frozen, deleted);
  - the new verdict rules.

  Fix what it finds, and record its findings and fixes in your section.
- **Before any run:** `verify-clean` and the dry-run `configure`.
  - Expected: no proof users, channels, polls or user groups; one other user, the dashboard user; "differences before: []".
  - If the application holds anything else (a `deleted-user-1729640-…` user, a leftover proof user or any channel), or the configuration differs, make no live run, and report.
- **Each live run starts from a committed and pushed head** (DM-04 finding 8), at which the offline checks and the fix reversals pass, and its record names that commit. Later commits are listed as not exercised live.
- **The run plan** (the brief: one run in reserve for a rerun). The harness's per-session guardrails stand: 20 synthetic users, 30 channels, 10 concurrent connections and 5,000 API calls, counted across every run of one checkout (DM-04 finding 5).
  - **Count first:** before any live call, count the complete set's users, channels and peak connections offline, and record the count. The simulation against the fakes reserves them through the same ledger.
  - **Run 1:** the complete set, the I1 matrix and every I2a case, as one `run --accept-dashboard-user`. It may use that count, provided that what is left still covers one rerun: the base setup plus the largest single case family.
  - **No sharing to meet a number:** never share a channel or a user between mechanisms for that reason.
  - **If it does not fit** (the complete set plus that reserve over the session caps): no live run, and report.
  - **Reserve:** at most one rerun, `run --accept-dashboard-user --only <case ids>`, for cases run 1 could not complete. It must fit what the session has left.
  - **Nothing else live,** beyond the checks this section names and `cleanup --apply`. Fix harness errors offline, against the fakes, never by trying a live run. If the reserve is spent, report the cases not run.
- **One place, one at a time.** Every live command runs in sequence from one checkout, so one ledger counts every call and no cleanup overlaps another run.
- **Cleanup.** Use `cleanup --apply` only for your own runs' leftovers. If a `deleted-user-1729640-…` user remains after `cleanup --apply`, report it and leave it.
- **After the last run:** `verify-clean` and the dry-run `configure` again. Report both outputs. If `configure` reports any difference, do not fix it: report it, and the manager decides.
- **Signals, by kind** (DM-04 finding 4). Bring the README's "Budget guardrails" into line with this rule.
  - **A charge signal** (HTTP 402, Stream code 99, or billing or upgrade wording): no further live call; report.
  - **Only a rate limit** (HTTP 429, Stream code 9): wait at least the rate-limit window (60 s, or the reset the answer gives); then run `cleanup --apply` once, `verify-clean` and the dry-run `configure`. The reserve rerun stays available if those pass. A second rate limit ends live work.
- **Preflight stops:** make no further live call, and report. Never bypass a stop, and report anything the harness marks "not verified".
- **First live use.** For each item on the three "What P06.1-I2a must know" lists, report what happened. Record the answer shapes of the new server calls, key names only.

## 6. Owned paths, push and records

- **You may change:**
  - `proofs/stream-chat/**`, except the committed baseline, `baseline/application-1729640-2026-09-25.json`, and the dependency files: `requirements.in`, `requirements-dev.in`, both `.lock` files, `package.json`, `package-lock.json`, `.npmrc` and the dependencies in `pyproject.toml`. If a dependency change seems needed, leave that part and report why;
  - `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md`: your section at its end, and in-place corrections of earlier claims that were false when written, each marked "(corrected in P06.1-I2a)". Keep every recorded result: a correction changes a claim about a result, never the result.
- **Never change these sections** of the evidence record, each with everything under it:
  - "Manager verification (App Manager 3, 25 September 2026)" and "Exact-head review of I1 (25 September 2026)";
  - "Manager verification (App Manager 3, 26 September 2026)" and "Exact-head review of C1 (26 September 2026)";
  - "Manager verification of C2 (App Manager 3, 26 September 2026)" and "Exact-head review of C2 (26 September 2026)";
  - "Manager verification of C3 (App Manager 3, 26 September 2026)" and "Exact-head review of C3 (26 September 2026)".
- **Nothing else,** including the brief, the ADRs, `apps/`, `services/`, `.github/` and every other document. Report any other change you think is needed.
- **Commit and push** your session branch, with step 1 in its own commit. Don't open a pull request.
- **Your section, "P06.1-I2a",** at the end of the evidence record:
  - the start SHA, your head and your branch;
  - step 1: each item, fixed (`file:line` and its test) or left (the reason);
  - the new cases and their verdict rules;
  - the independent check's findings and fixes;
  - the run plan's count;
  - each live run: the commit it started from, its prefix, UTC start and end, command, exit code, results table, usage and cleanup, and the checks before and after;
  - the commits after the last live run, listed as not exercised live;
  - the results by topic: the revocation table (mechanism, effect, which member, verdict), what each member's client can undo and what each member is shown, suspension and deletion, tokens and devices, send versus revocation, the outage injection, the S15 mapping, G2 and S10, the new endpoints and the existence oracle;
  - the first live use of each earlier fix;
  - every check, with its exact results;
  - deviations and limits;
  - what I2b and P06.2 must know.

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
4. The offline checks, with the README's commands: the unit tests (252 at the start; the counts at step 1's commit and at your head), Ruff check and format, mypy, and `node --check` on both `.cjs` files.
5. `checks/fix_reversals.py` (147 at the start; the counts at step 1's commit and at your head), with none "not demonstrated", and each failure reason read.
6. A secret scan over your whole diff and over every live output you keep or quote: no secret, token, JWT-shaped string, API key or email address.
7. The live runs, and `verify-clean` and the dry-run `configure` before and after them.

## 8. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 2, from commit `<START_SHA>`);
- your branch, head SHA and tree, step 1's commit, and the changed paths;
- the environment check (names only);
- step 1: each item, fixed (`file:line` and the test) or left (the reason);
- the independent check's findings and fixes, and the run plan's count;
- the I2a results by topic, as in your section;
- each live run: the commit it started from, prefix, UTC start and end, command, exit code, results, usage and cleanup, and the checks before and after; and the commits after the last live run, not exercised live;
- the first live use of the earlier fixes;
- every check, with its exact results;
- deviations, limits, open questions, and what I2b and P06.2 must know.

**Stop and report** if:

- an HDE variable is present;
- application 1729640 holds data your runs did not create, other than the dashboard user;
- a charge signal, any other signal that is not only a rate limit, or a second rate limit (section 5, "Signals, by kind");
- the secret or a full token appears in any output, log or file. Remove it, and say where it was;
- the work needs a path outside your owned paths, a dependency change or a lasting configuration change.

Skipped or unavailable checks are not passes.

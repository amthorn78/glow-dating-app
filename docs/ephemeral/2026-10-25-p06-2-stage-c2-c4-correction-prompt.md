# P06.2 Stage C2-C4 prompt — correction pass: replacing the window invalidates outstanding older-page requests (Codex's CX12)

- **Owner:** App Manager 8. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 25 October 2026.**
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 19: "Codex's CX12, and C2-C4", with "The re-review's F1, and C2-C3" and the owned paths for C2-C4.
  - Inputs:
    - the [DM-28 report](../continuity/dev-manager/reviews/2026-10-25-dm-28-p06-2-cx12.md) (`2d9f1e9`), whose conditions 1.1 to 1.5 are quoted below as written, and whose section 3 holds its own audit of the window-bound state;
    - the evidence record's "Stage C2-C3", "Manager verification of Stage C2-C3" (with CX12) and "Exact-head review of Stages C2-C1 and C2-C2";
    - C2's prompt, items 5 and 7.
- **Where the result goes:**
  - the session's code and tests, and its section "Stage C2-C4" in the evidence record `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`;
  - the run of record: the Foundation run on its last code commit.

  The manager adds its verification and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 1.83 (confidence 0.86); rung probabilities low 0.00, medium 0.19, high 0.79, extra high 0.02, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.97, Sonnet 5.5 0.03, Haiku 5.5 0.00 (confidence 0.96). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.184, Opus 5.5 at high 0.766, Opus 5.5 at extra high 0.019, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.006, Sonnet 5.5 at high 0.024, Sonnet 5.5 at extra high 0.001, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-10-25T13:29:01Z. Nathan picks the cell.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** none, on DM-28 3.1's terms: this prompt quotes 1.1 to 1.5 as written; `apps/mobile` only, no dependency or contract change; the cursor rule (DM-23 2.1 to 2.3, DM-25 3.1 to 3.3, DM-27 1.1) and the revocation rule (DM-24 1.1 to 1.3) unchanged; it starts in `Glow App - No Stream`, checks that no `STREAM_*` name is present, and authorizes no credential and no provider call. A departure found while it runs goes back to the Dev Manager first.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and the session calls no provider.
- **It runs alone** (OD-29). Codex's review of its code head follows, with any finding handled; then one exact-head re-review of the head holding C2-C3 and C2-C4 (DM-28 2.2 to 2.4).
- **Deletion condition:** prune after Stage C2's PR merges and the evidence record holds the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **correction session P06.2 Stage C2-C4**, a correction pass on Stage C2 of P06.2, the chat integration of the Glow dating app, in the private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<START_SHA>`.

**What exists.** Stage C1 merged on 24 October (PR32, `a8e9528`). **Stage C2,** the mobile chat interface on fixtures, is PR33, from the manager branch `claude/magical-wozniak-yfmmx2` into `main`.

- **Stage C2** (code `cb3a6a6`) added `apps/mobile/src/chat/` (a `ChatTransport` interface, an in-process fixture adapter, a validating client, a polling store, the screens and their tests). Its correction passes: **C2-C1** (code `311b07e`; the read cursor moves only over messages in view), **C2-C2** (code `27999c7`; a revocation invalidates every outstanding request, and an unknown cursor position is not treated as known) and **C2-C3** (code `85b9844`, unchanged since; the commits after it are Markdown records; the position is known only while `lastRead` is among the loaded messages). C2-C3's run of record 40160547922 passed all eight jobs.
- **Codex then posted CX12** (P2, `store.ts:282`), which the manager verified at `85b9844`, quoted:

  > If an older-page request remains in flight while a newer-cursor request returns `stale` and triggers a cursorless reload, its response still passes the epoch check even though its pagination boundary belongs to the discarded window. For example, starting with messages 6–25, hold the request for 1–5, then reload the newest window as 31–50 after more messages arrive. Releasing the older response produces 1–5 followed by 31–50 and overwrites `olderCursor` with null, leaving messages 6–30 inaccessible through "Show earlier messages." Invalidate outstanding older-page requests when replacing the window, or verify that their captured boundary still matches the current window before merging and replacing its cursor.

  `loadOlder` (`:271-291`) tests only `conversationEpoch` when its page returns. When a head read is answered `stale`, `readHead`'s branch at `:244` clears `newerCursor` and its `finally` sends the queued read with no cursor (`:249`); that page goes through `mergeHead`'s newest branch (`:255-256`), which replaces `accepted`, `unsent`, `olderCursor` and `newerCursor` without advancing any epoch. A held older page then passes `:278`, is put in front of the new window (`:281`), sets `olderCursor` from its own page (`:282`) and can fire DM-25 3.2's older-page trigger (`:285`). The messages stay in order with a silent gap, and the gap cannot be reached while the conversation stays selected. The path is C2's; C2-C3 did not touch it.
- **Why it is corrected now:** on its path it misses C2's item 5 ("It shows them in the order the page gives … and for older ones with `older_cursor`") and item 7 ("with unread, older pages, …"); a unit test shows it offline; the fix is local. The Dev Manager chose a correction pass before PR33 merges (DM-28).
- **Its reach is narrow:** C1's server answers `stale_version` to a newer cursor only when the cursor cannot be read or its boundary cannot be placed (`services/api/glow_chat/reads.py:389-411`); the fixture never answers `stale`, so the tests use C2-C3's `staleOnce` test transport and the CX9 gate.

**How you work:**
- Nathan started you manually and will relay your report to the manager (App Manager 8). You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs, including reading Expo's and React Native's versioned documentation as `apps/mobile/AGENTS.md` asks.
- Your boundary is scope:
  - write only your owned paths (section 5);
  - push only your own session branch. The Foundation workflow runs on a push only for `main`, `app-builder-1/**`, `app-planner-1/**` and `claude/**`. If your branch is under that filter, each push runs it, and you read those runs if your tools can; if it is not, say so in your report, and the manager takes the run of record from the PR run on the head that integrates your code (the manager workflow, step 5). On GitHub do nothing else: no pull request, no PR comments, no re-runs, no workflow dispatches. Change nothing in Notion.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, token or password, in any form;
  - call Stream or any other provider, or run any harness command in `proofs/stream-chat/` that sends a request;
  - connect to any database, HDE, Railway or any other provider;
  - run `playwright install`, `eas` or `migrate`;
  - add or change a dependency, a version or a lock file, in any component.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If any is present, stop and report to Nathan: this session must start in `Glow App - No Stream`.
3. **No `.env` file:** `ls -a . apps/mobile packages/contracts | grep -x '\.env'` must print nothing. If one exists, report it without reading it, and stop.
4. **The toolchain:** the pinned toolchain is in `$HOME/.local/bin`: Node 24.19.0 and npm 11.9.0 (and Python 3.12.14). Put `$HOME/.local/bin` first on PATH in every process you run, then record `node --version` and `npm --version`.
5. **A clean process environment.** Run the mobile app's and the contracts' commands in one, as `docs/operations/local-development.md` and each README show: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`EXPO_OFFLINE=1` where the mobile README uses it). Installs get the proxy and CA variables by reference, never printed.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git merge --ff-only <START_SHA>          # on your own session branch
git rev-parse HEAD                       # must print <START_SHA>
git merge-base --is-ancestor a8e952895ebd3ffc9ef0e4d195c8a7111c69b3ae HEAD && echo "C1 present"   # must print "C1 present"
git diff --quiet 85b98444320326742e642e8f2d01f720cfb77f27 HEAD -- proofs .github services scripts apps packages && echo "C2-C3's code"   # must print "C2-C3's code"
git diff --stat <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- apps/ packages/ services/ proofs/ .github/   # must print nothing
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md | grep -c '^## Stage C2-C4'   # must print 0
```

- The last two commands check the live manager branch. If code or this stage's section has already landed there, this prompt is stale: stop and report (the manager workflow, step 3, AM5-15).
- If any check fails, stop and report.

Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md` and `apps/mobile/README.md`;
- the P06.2 brief, `docs/planning/p06-2-chat-integration.md`, revision 19: "Codex's CX12, and C2-C4", "The re-review's F1, and C2-C3", and the owned paths for C2-C4;
- the DM-28 report, `docs/continuity/dev-manager/reviews/2026-10-25-dm-28-p06-2-cx12.md`, whole (its section 3 holds the Dev Manager's own audit, which 1.4 asks you to check, not copy); the DM-24 report's 1.1 to 1.3 and the DM-27 report's 1.1;
- C2's prompt, `docs/ephemeral/2026-10-24-p06-2-stage-c2-implementation-prompt.md`, items 5 and 7;
- the evidence record's "Stage C2-C3" and "Manager verification of Stage C2-C3", with its CX12 lines;
- `apps/mobile/src/chat/` whole, chiefly `store.ts` (`select`, `closeConversation`, `readHead`, `mergeHead`, `loadOlder`, `moveReadCursor`, `revoke`, `resetConversation`) and `store.test.ts` (the CX9 gate and `revokeThrough`, C2-C3's `staleOnce` and its tests at `:613` to `:690`).

## 3. The work

DM-28's conditions are quoted at their items, with their numbers. Meet each as written.

**DM-28's conditions 1.1 to 1.5, as written:**

> - **1.1 Replacing the window invalidates every older-page request outstanding at that moment** (replaces e.1).
>   - **Where:** at the replacement itself, `mergeHead`'s newest branch, not at the `stale` answer.
>     - A request made after the `stale` answer and before the reload's page is merged was asked from the window being discarded.
>     - So it is invalidated too.
>     - **Where it bites:** otherwise the newest branch runs only on the first read after a reset or a revocation, and while the conversation holds no accepted message (C1 then gives no newer cursor). In both cases `olderCursor` is null, so no older page can be outstanding. 1.1 changes behaviour only on the `stale` path.
>   - **An invalidated response, success or failure, changes nothing.**
>     - It does not change `accepted`, `unsent`, `olderCursor`, `newerCursor` or `hasOlder`.
>     - It shows no older-page error.
>     - It starts nothing: no cursor command (DM-25 3.2's older-page trigger does not fire), and no read.
>   - **The exception: a refusal that ends access** (`unavailable` or `signed_out`), unless the conversation's epoch has moved on first (a revocation, another conversation or another account; DM-24 1.1). It revokes the conversation, as a refusal of an older page does today (`store.ts:289`).
>     - **Why:** after a revocation, a late refusal adds nothing, so DM-24 1.1 drops it. Here the conversation is still open, and the refusal may be Glow's first word that access has ended. Dropping it would leave the history on screen until the next poll is refused.
>     - e.1 as written would have dropped it. That contradicts e.4's "the revocation rule … unchanged".
>   - **The session chooses the mechanism,** and records why. For example:
>     - an older-page epoch advanced by the replacement;
>     - or a comparison of the request's captured cursor with `olderCursor` before merging. A cursor is opaque, so that comparison tests identity; it computes no position.
>   - **A comparison may merge a page whose cursor is identical to the current `olderCursor`.** The page then continues the new window exactly, so that is not a departure.
> - **1.2 "Show earlier messages" stays usable** (replaces e.2).
>   - **No invalidated request leaves the older-page state `loading`.**
>     - The state is `idle` once the replacement is merged, or at the latest once the invalidated request completes.
>     - Which of the two depends on the mechanism. The record says which.
>     - As e.1 and e.2 were written, the cursor comparison would have left it `loading` for good: the state comes from the old request, and e.1 forbade its response to change it.
>   - **A request made after the replacement** asks with the reload's `older_cursor` and keeps today's behaviour:
>     - at most one for the current window at a time;
>     - its page merges;
>     - its failure shows the error;
>     - a refusal that ends access revokes.
> - **1.3 Tests** (replaces e.3). Each has its reversal in a scratch copy outside the checkout, showing that the test fails without its part of the fix.
>   - **The tools:** C2-C3's `staleOnce` and the CX9 gate compose.
>     - A helper the gate lacks goes in `store.test.ts`, or in `testing.ts` (1.5).
>     - Examples: a held page answered with a refusal, or held requests released one at a time.
>   - **(a) CX12's sequence,** in Codex's numbers or any others that leave a gap between the held page and the reload's page.
>     - **The steps:**
>       - 25 messages, with the window holding 6–25;
>       - the older page, 1–5, held;
>       - 25 more messages arrive;
>       - one head read is answered `stale`, and the reload shows 31–50;
>       - the held page is released.
>     - **Expected:**
>       - the window is the reload's page alone, with the reload's `olderCursor`;
>       - the release starts no request;
>       - "Show earlier messages" then reaches 11–30 and 1–10, in order, each message once.
>     - **Reversal:** today's code.
>   - **(b) The same, with the held page failing** without ending access.
>     - **Expected:**
>       - the window and its cursor are unchanged;
>       - no older-page error is shown;
>       - the state is `idle`, at the latest after the failure;
>       - "Show earlier messages" reaches the gap.
>     - **Reversal:** today's code, which shows the error.
>   - **(c) The same, with the held page refused because access has ended.**
>     - **Expected:** the conversation is revoked, as `assertRevoked` checks.
>     - **Reversal:** 1.1's exception removed.
>   - **(d) An older page requested after the `stale` answer and before the reload's page is merged.** The reload is held, and the older page is released after it.
>     - **Expected:** as (a).
>     - **Reversal:** a mechanism that invalidates only the requests made before the `stale` answer.
>   - **The existing tests:** every one passes unchanged, including the CX9 and CX10 tests and C2-C3's (a) to (c). Any change is named in the record, with the rule that makes it.
> - **1.4 The audit** (new).
>   - **The record lists each piece of window-bound state across a replacement,** with the code that handles it, as section 3 does:
>     - `accepted`, `unsent`, both cursors and `hasOlder`;
>     - an outstanding older page, and the older-page state;
>     - `lastRead`, `seen` and `visible`;
>     - `cursorRetry`, and a cursor command, a send and a list read in flight.
>   - **A defect found beyond CX12** is recorded as a finding outside the work, with its path. It is not fixed in C2-C4. The manager brings it to me (DM-25 1.2).
> - **1.5 Scope** (replaces e.4).
>   - **The paths:**
>     - `apps/mobile/src/chat/store.ts`, its class comment included, and `store.test.ts`;
>     - `src/chat/testing.ts`, only for a test helper;
>     - the evidence record's new section "Stage C2-C4".
>   - **The README is unchanged.** Its step 3, "**Show earlier messages** follows the page's `older_cursor`", stays true.
>   - **Unchanged:**
>     - DM-23 2.5's list, and the fixture adapter;
>     - the cursor rule, as DM-23 2.1 to 2.3, DM-25 3.1 to 3.3 and DM-27 1.1 set it;
>     - the revocation rule (DM-24 1.1 to 1.3), under which every refusal that ends access still revokes;
>     - DM-25 3.2's triggers, for a page that is merged.

1. **The invalidation** (1.1): replacing the window invalidates every older-page request outstanding at that moment, including one made after the `stale` answer and before the reload's page is merged; an invalidated response changes nothing and starts nothing; a refusal that ends access still revokes unless the epoch has moved on. You choose the mechanism and record it and why.
2. **The older-page state** (1.2): no invalidated request leaves it `loading`; record when it becomes `idle` under your mechanism. A request made after the replacement keeps today's behaviour.
3. **The tests** (1.3): (a) to (d), each with its reversal in a scratch copy outside the checkout. Every existing test passes unchanged; name any change and the rule that makes it.
4. **The audit** (1.4): each piece of window-bound state across a replacement, with the code that handles it. A defect beyond CX12 is recorded as a finding outside the work, with its path, and not fixed.
5. **The record:** a new section "Stage C2-C4" in the evidence record, with what the re-review of DM-28 2.2 must know.

**Not in C2-C4:**
- any change to the cursor rule (DM-23 2.1 to 2.3, DM-25 3.1 to 3.3, DM-27 1.1), to the revocation rule (DM-24 1.1 to 1.3) or to DM-25 3.2's triggers for a merged page (1.5);
- any change to the fixture adapter or to the README (1.5);
- a fix for any defect the audit finds beyond CX12 (1.4): record it;
- the cursor position in a contract (C2C1-X1 stays for P11), or any other contract or dependency change (stop and report);
- a network client, an API URL, a socket or any realtime service;
- any change to `packages/`, `services/`, `proofs/` or `.github/`.

**Rules for every change:**
- **A test for each change.** Each code item gets a test that fails without the change and passes with it. Say which test covers which condition.
- **Reversals in a scratch copy, never the checkout.** Make each fix reversal in a copy outside the repository, with absolute paths. Confirm afterwards that `git status` is clean.
- **No weakened check.** Never loosen a validator, a guard, a lint rule or a test to make a run pass. A flaky test is a finding (OD-21), not a retry.
- **The release block and the fixture-only guards stay unchanged:** `app.config.ts` and `scripts/development.mjs`.
- **No dependency change:** `apps/mobile/package.json`, `package-lock.json`, `.npmrc` and `dependency-inventory.json` stay unchanged, and so does every dependency file in `packages/contracts/`.

**Findings outside this work:** report each with its class. Fix one here only if it could do one of the following, and then with a test:
- let a provider field, provider ID or provider text reach a render, a stored client state or a log;
- let a revoked member see a conversation's history or send in it;
- let the app make a network call, load a provider package, or run outside the development fixture mode.

**A departure** from any condition above that you find necessary: stop before making it, record it and the reason, and report it. It goes back to the Dev Manager (DM-28 item 3).

## 4. Checks

Report the exact commands and results.

1. **The diff:** `git diff --check <START_SHA> HEAD`, and `git diff --name-only <START_SHA> HEAD`. Only owned paths changed.
2. **Classification** with the trusted policy from `main`, run outside the tree, as root `AGENTS.md` requires. Expected: full scope. Pass full SHAs, not `HEAD`.

   ```bash
   base=$(git rev-parse origin/main); policy_dir=$(mktemp -d)
   git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
   python3 -I "$policy_dir/change_scope.py" --base <START_SHA> --head "$(git rev-parse HEAD)" --merge-base
   ```

3. **The installs** from the locks, in a clean process: `npm ci --ignore-scripts` for `packages/contracts` and `apps/mobile`. Install the mobile app first: the contracts' corpus test loads its generated validators.
4. **The offline checks,** with counts at the start and at your head:
   - **the contracts:** `npm run generate`, with no diff after it, and `npm run check`;
   - **the mobile app:** `npm run check`, `EXPO_OFFLINE=1 npm run check:expo` and `EXPO_OFFLINE=1 npm run export:development`;
   - `npm run test:rendered` only if it can run without `playwright install`, marked "informational, not the pinned browser".
5. **What stays unchanged:** an empty `git diff <START_SHA> HEAD` over:
   - `apps/mobile/README.md`;
   - `apps/mobile/package.json`, `package-lock.json`, `.npmrc` and `dependency-inventory.json`;
   - `apps/mobile/src/contracts/generated/`;
   - `apps/mobile/src/chat/fixture-adapter.ts`;
   - `apps/mobile/app.config.ts` and `apps/mobile/scripts/development.mjs`;
   - `packages/`, `services/`, `proofs/` and `.github/`.
6. **The reversals** of DM-28 1.3, each with the test's output.
7. **The Foundation run on your last code commit:** its run ID, each job's conclusion (eight jobs), and the gate's log line, which must be `Application checks passed`.
   - **Wait before pushing again.** After pushing your last code commit, push nothing more to your branch until that commit's Foundation run has finished. Runs of the same branch cancel each other (the CI policy), so an early records push can cancel the code run (AM5-14).
   - A push that changes only Markdown skips the application jobs. If your last commit changes only the record, the run of record is the push run of your last code commit, and your record says so.
   - **From the Mobile job's log:** `npm run check`'s test counts; the rendered tests' count, with the long-conversation test named and passing; the job's time and the rendered step's time, against the 15-minute timeout.
   - **The API mobile smoke** job's conclusion.
   - If your tools cannot read the run, or your branch is outside the push filter, say so; re-run or dispatch nothing.
8. **A secret scan over your whole diff:** no secret, token, API key, password or email address.

## 5. Owned paths, push and records

- **You may change:**
  - `apps/mobile/src/chat/store.ts`, its class comment included, and `apps/mobile/src/chat/store.test.ts`;
  - `apps/mobile/src/chat/testing.ts`, only for a test helper;
  - the evidence record `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`: a new section "Stage C2-C4" only, after the existing sections, which stay byte-identical.
- **Nothing else.** That includes the README, the fixture adapter, the screens, `packages/`, `services/`, `proofs/`, `.github/`, `scripts/`, any `.claude/` path, the briefs, the P11 plan and every other document. Report any other change you think is needed.
- **Commit and push** your session branch. Don't open a pull request.
- **Your section "Stage C2-C4"** in the evidence record:
  - the prompt's revision and start SHA, your head, your branch and the run of record;
  - for items 1 to 5 of section 3: done (`file:line` and its test) or left (the reason), and which test covers each of DM-28 1.1 to 1.3;
  - the mechanism you chose, why, and when the older-page state becomes `idle` under it;
  - the audit (1.4), and any finding beyond CX12 with its path;
  - any change to an existing test and the rule that makes it;
  - every check, with its exact results;
  - deviations and limits;
  - what the exact-head re-review must know (DM-28 2.2): every request that can be outstanding when the window is replaced, and how each is handled.

## 6. Report

Your final message is the report Nathan relays:

- the prompt revision you received, and the commit it came from;
- the environment check;
- your branch, head SHA and tree, and the changed paths;
- for items 1 to 5 of section 3: done or left, with the recorded choices;
- every check, with its exact results, and the run of record's details from section 4 item 7;
- deviations, departures you stopped at, findings outside the work with their class, open questions and limits.

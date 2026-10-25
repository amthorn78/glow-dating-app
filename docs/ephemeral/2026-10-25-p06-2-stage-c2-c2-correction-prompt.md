# P06.2 Stage C2-C2 prompt — correction pass: revocation invalidates outstanding requests (CX9), and an unknown cursor position is not treated as known (CX10)

- **Owner:** App Manager 8. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 25 October 2026.**
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 17: "Codex's CX9 and CX10, and C2-C2", with "Stage C under OD-45" (points e and g), "Codex's CX8, and C2-C1" and the owned paths for C2-C2.
  - Inputs:
    - the [DM-24 report](../continuity/dev-manager/reviews/2026-10-25-dm-24-p06-2-cx9.md) (`1a4fc1b`), whose conditions 1.1 to 1.6 are quoted below as written;
    - the [DM-25 report](../continuity/dev-manager/reviews/2026-10-25-dm-25-p06-2-re-review-order.md) (`1809fde`), whose conditions 3.1 to 3.6 are quoted below as written;
    - the [DM-23 report](../continuity/dev-manager/reviews/2026-10-24-dm-23-p06-2-cx8.md), 2.1 to 2.6, the cursor rule C2-C1 implemented;
    - the evidence record's "Stage C2-C1", "Manager verification of Stage C2-C1", "Codex's code review of C2-C1's head" and "Codex's CX10 on C2-C1's cursor code";
    - C2's prompt, items 3 and 8 and "Findings outside this work".
- **Where the result goes:**
  - the session's code and tests, and its section "Stage C2-C2" in the evidence record `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`;
  - the run of record: the Foundation run on its last code commit.

  The manager adds its verification and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 1.89 (confidence 0.89); rung probabilities low 0.00, medium 0.14, high 0.84, extra high 0.02, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.98, Sonnet 5.5 0.02, Haiku 5.5 0.00 (confidence 0.97). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.137, Opus 5.5 at high 0.823, Opus 5.5 at extra high 0.020, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.003, Sonnet 5.5 at high 0.017, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-10-25T01:34:55Z. Nathan picks the cell.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** none, on DM-24 item 3's terms (DM-22 9.1's), confirmed by DM-25 (section 3 and item 3): this prompt quotes DM-24 1.1 to 1.6 and DM-25 3.1 to 3.6 as written; it changes no dependency and no contract; it starts in `Glow App - No Stream`, checks that no `STREAM_*` name is present, and authorizes no credential and no provider call. A departure found while it runs goes back to the Dev Manager first.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and the session calls no provider.
- **It runs alone** (OD-29). Codex's review of its code head follows, with any finding handled; then one exact-head re-review of the head that holds C2-C1 and C2-C2 (DM-25 1.1 to 1.3).
- **Deletion condition:** prune after Stage C2's PR merges and the evidence record holds the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **correction session P06.2 Stage C2-C2**, a correction pass on Stage C2 of P06.2, the chat integration of the Glow dating app, in the private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<START_SHA>`.

**What exists.** Stage C1 merged on 24 October (PR32, `a8e9528`). **Stage C2,** the mobile chat interface on fixtures, is PR33, from the manager branch `claude/magical-wozniak-yfmmx2` into `main`.

- **Stage C2** (code `cb3a6a6`) added, under `apps/mobile/`: `src/chat/` (a `ChatTransport` interface, an in-process fixture adapter, a validating client, a polling store, the screens and their tests), the routes `/conversations` and `/conversation`, and `rendered/chat.spec.ts`. Its exact-head review approved it.
- **Stage C2-C1** (code `311b07e`, unchanged since; the commits after it are Markdown records) corrected Codex's CX8: the read cursor moves only to the newest accepted message that has been in view while the conversation is shown and the app is in the foreground (DM-23 2.1 to 2.3; `src/chat/visibility.ts`, the store's `viewed`, `noteSeen` and `moveReadCursor`). Its run of record 40145402786 passed all eight jobs. No exact-head review of it has run; one follows this pass and covers both.
- **Codex then found two P2 defects, which the manager verified at `311b07e`:**
  - **CX9** (C2's code, `store.ts:300-309`), quoted:

    > When a message-page request overlaps a send or read-cursor request that refuses access, `revoke()` clears the conversation without changing `conversationEpoch`. A successful page response arriving afterward therefore passes `readHead()`'s epoch check, restores the private messages, and sets the conversation back to `ready`, making the history and composer visible again despite the refusal. An outstanding older-page response can likewise repopulate the cleared history. Invalidate outstanding requests on revocation so responses issued before access ended cannot restore that state.

    It also reaches a send in flight (`run()` still publishes `sent` and starts a head read), a cursor command (`lastRead` and the list), and the list read (`readList()` tests only the owner's epoch, so a list built before the revocation can put the revoked conversation's row back), as DM-24 found.
  - **CX10** (C2-C1's cursor code, `store.ts:283-284`), quoted:

    > If the newest 20 accepted messages are all the member's own, but an older incoming message remains unread, this check suppresses every cursor command because the loaded page contains no `other` message. Viewing the newest message therefore leaves the conversation unread. Loading the older page and viewing that incoming message does not recover either: `seen` already points to the newer own message, so `noteSeen()` returns without retrying the move. Account for unread incoming messages outside the loaded window and reconsider a deferred cursor move when older history supplies the missing evidence.

    `lastRead` starts `null` at each opening (`resetConversation`, `:177`), and no contract carries the cursor's position (C2C1-X1). The count stays above zero until the member views a later incoming message.
- **Why they are corrected now:** CX9 misses C2's item 3 and its prompt's revocation class ("let a revoked member see a conversation's history or send in it"); CX10 misses C2's item 8 ("when the member has seen newer messages"). The Dev Manager chose a correction pass before PR33 merges for both, with conditions (DM-24, DM-25).

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
git diff --quiet 311b07e11b7131147becd0f045665f30d29856fa HEAD -- apps packages services proofs .github scripts && echo "C2-C1's code"   # must print "C2-C1's code"
git diff --stat <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- apps/ packages/ services/ proofs/ .github/   # must print nothing
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md | grep -c '^## Stage C2-C2'   # must print 0
```

- The last two commands check the live manager branch. If code or this stage's section has already landed there, this prompt is stale: stop and report (the manager workflow, step 3, AM5-15).
- If any check fails, stop and report.

Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md` and `apps/mobile/README.md`;
- the P06.2 brief, `docs/planning/p06-2-chat-integration.md`, revision 17: "Codex's CX9 and CX10, and C2-C2", "Codex's CX8, and C2-C1", points e and g of "Stage C under OD-45", and the owned paths for C2-C2;
- the DM-24 report, `docs/continuity/dev-manager/reviews/2026-10-25-dm-24-p06-2-cx9.md`, and the DM-25 report, `docs/continuity/dev-manager/reviews/2026-10-25-dm-25-p06-2-re-review-order.md`; the DM-23 report's 2.1 to 2.6;
- C2's prompt, `docs/ephemeral/2026-10-24-p06-2-stage-c2-implementation-prompt.md`, items 3 and 8 and "Findings outside this work";
- the evidence record's "Stage C2-C1", "Manager verification of Stage C2-C1", "Codex's code review of C2-C1's head" and "Codex's CX10 on C2-C1's cursor code";
- `apps/mobile/src/chat/` whole; `apps/mobile/src/interactions/screen.tsx` (the match's "Open conversation", `:75`); and, for the server's forward-only rule DM-25 3.1 relies on, `services/api/glow_chat/reads.py`, `_move` (read only).

## 3. The work

The Dev Manager's conditions are quoted at their items, with their numbers. Meet each as written. DM-25 3.5 amends DM-24 1.5's last sentence for this pass: read 1.5 with 3.5.

**DM-24's conditions 1.1 to 1.6, as written:**

> - **1.1 A revocation invalidates every request outstanding when it happens.**
>   - The conversation's requests: a head read, a queued head read, an older page, a cursor command and a send.
>   - The conversation list's read.
>   - **A response to any of them, success or failure, changes nothing:** not the messages, the status, the older-page state, the cursors, `lastRead`, the draft, the send state or the list. It starts nothing either: no follow-up head read and no cursor command.
>   - **A list response requested before the revocation does not put the revoked conversation's row back.**
>   - The session chooses the mechanism (for example, advancing the conversation's epoch in `revoke()` and marking list reads issued before it) and records why.
> - **1.2 No send is left pending.** After the revocation, the send state shows no pending send and offers no retry, whether a send was in flight or not. The revoked notice is the only state shown.
> - **1.3 Requests issued after the revocation keep today's behaviour,** such as the read on a return to the foreground or after an authority change. The server decides them: a resumed match can legitimately become readable again (DM-22 3.1's interim rule).
> - **1.4 Tests,** each with its reversal in a scratch copy outside the checkout, showing the test fails without the fix. Each holds a request through `chatSetup`'s transport wrapper, then revokes through a send's refusal and, separately, through a cursor command's.
>   - **A held head read that then succeeds:** the conversation stays `revoked`, with no messages, no draft, no pending send, no new read and no cursor command.
>   - **A held older page that then succeeds:** the store's messages stay empty.
>   - **A held head read that then fails without ending access:** the status stays `revoked`, not `error`.
>   - **A held send that then succeeds:** no `sent` state and no head read.
>   - **A held cursor command that then succeeds:** no change to `lastRead` or the list.
>   - **A held list read that returns the conversation:** the row stays absent.
>   - **A read issued after the revocation, on a return to the foreground:** today's behaviour (1.3).
> - **1.5 Scope:** `apps/mobile` only.
>   - **The paths:**
>     - `src/chat/store.ts` and `src/chat/store.test.ts`;
>     - `src/chat/testing.ts`, only if a test needs a helper;
>     - the README's revocation sentence, only if the change alters what it says;
>     - the evidence record's new section "Stage C2-C2".
>   - No dependency or contract change; DM-23 2.5's unchanged list holds.
>   - C2-C1's cursor behaviour and its tests stay unchanged, apart from the revocation path's effect on them.
> - **1.6 The re-review of C2-C2's diff:**
>   - it names CX9, C2's item 3 and the prompt's revocation class;
>   - it checks each caller of `revoke()`, and a late response of each request type in 1.1, the list included;
>   - it searches the store's other asynchronous paths for any that can move a conversation out of `revoked` with a response requested before the revocation.
>
>   Codex's review of the new final head follows.

**DM-25's conditions 3.1 to 3.6, as written:**

> - **3.1 An unknown position is not treated as known** (replaces c.1).
>   - **Why:** until a cursor command has succeeded in this opening, the store does not know where the server's cursor is (C2C1-X1). So the loaded window alone cannot show that a move to `seen` passes no unread message from the other member.
>   - **Until a command has succeeded,** a move to `seen` is sent when any of these holds:
>     - the loaded messages up to `seen` include one from the other member (DM-23 2.3, as today);
>     - the conversation's summary that the store holds shows an `unread_count` above zero. The summary is the conversation's entry in the store's list, as the last list read or cursor command returned it;
>     - the store holds no summary for the conversation, as when it was opened from the match's "Open conversation" with the list never read.
>   - **Once a command has succeeded,** DM-23 2.3 holds as written.
>   - **The target is always `seen`** (DM-23 2.1).
>   - **Why this is safe:** the server moves the cursor only forward (C1's `_move`), so a move to a message at or behind its cursor changes nothing.
>   - **A summary at 0 never suppresses a move** that the window's own evidence calls for.
> - **3.2 A move the store held back is reconsidered when its evidence changes** (replaces c.2).
>   - **The two triggers:**
>     - an older page that adds messages before `seen`;
>     - a list read, or a cursor command's response, that changes the conversation's summary.
>   - Each reconsideration applies 3.1 and DM-23 2.3, and sends nothing when they do not hold.
>   - **What does not trigger one:**
>     - a viewing report (DM-23 2.3);
>     - a failed command, which is still tried again only after the next successful read (`store.test.ts:210`'s rule);
>     - a response that DM-24 1.1 makes ineffective, because it was requested before a revocation.
> - **3.3 The existing rules hold** (c.3).
>   - Never backward, and never to an unsent message.
>   - At most one command in flight.
>   - The target is `seen`, the newest accepted message that has been in view while the conversation was shown and the app was in the foreground (DM-23 2.1).
>   - No command on each viewing report.
> - **3.4 Tests** (replaces c.4). Each has its reversal in a scratch copy outside the checkout, showing that the test fails without the fix.
>   - **(a) The incoming message outside the window, with the list read first.** One incoming message, then 20 of the member's own; the incoming one is unread and outside the newest page, and the list's count is 1. Viewing the newest sends one command, to it, and the list's count clears.
>   - **(b) The same, with no list read.** The conversation is opened with no summary held: one command, and a list read afterwards shows 0.
>   - **(c) A summary that is out of date.** The summary held shows 0, from a list read before the incoming message and the 20 own arrived.
>     - Viewing the newest sends nothing.
>     - Loading the older page then sends one command, to `seen`, and the count clears.
>     - In a separate case, a list read that shows the count above zero does the same.
>   - **(d) Nothing unread.** The summary held shows 0, and the window holds no incoming message: no command, however often the messages are reported.
>   - **(e) The existing rules, unchanged:**
>     - once a command has succeeded, the member's own messages in view send nothing (`store.test.ts:193`);
>     - a failed command is still tried again only after the next read (`:210`).
>   - **The reversals:**
>     - 3.1 reverted to the window-only test fails (a) and (b);
>     - 3.2's older-page trigger removed fails (c)'s first case, and its summary trigger removed fails the second;
>     - a reconsideration on every report fails (d) or `:210`.
> - **3.5 Scope** (replaces c.5).
>   - **The paths and the unchanged list:** DM-24 1.5's, with no change to the fixture adapter. A test can send the member's own messages through the transport.
>   - **DM-24 1.5's sentence on C2-C1's cursor behaviour** reads, for C2-C2: "C2-C1's cursor behaviour and its tests stay unchanged, apart from the revocation path's effect on them and DM-25 3.1 to 3.3".
>   - **C2-C1's cursor tests** change only where 3.1 to 3.3 change the rule. The record names each change.
>   - **The README's cursor sentence** states 3.1.
>   - **No contract change:** the cursor position stays out of the contracts (C2C1-X1, for P11).
> - **3.6 The re-review** (replaces c.6). The re-review of item 1 also:
>   - names CX10 and C2's item 8 for this change;
>   - reads 3.1's three grounds and 3.2's triggers;
>   - checks that no path sends a command on a viewing report or to any target but `seen`;
>   - checks that a response DM-24 1.1 makes ineffective triggers no reconsideration;
>   - weighs one effect: a move reconsidered by a list read can be sent after the screen is left. C2-C1 already allows that for a `seen` set while shown and in the foreground ("a move to a message that was in view may now complete after the screen is left", the evidence record's "Stage C2-C1").

1. **CX9, revocation** (DM-24 1.1 to 1.3): a revocation invalidates every request outstanding when it happens, the list read included; their responses change nothing and start nothing; no send is left pending; requests issued afterwards keep today's behaviour. You choose the mechanism and record it and why.
2. **CX9's tests** (DM-24 1.4): each case of 1.4, with its reversal in a scratch copy outside the checkout.
3. **CX10, the cursor while its position is unknown** (DM-25 3.1 to 3.3): until a cursor command has succeeded in this opening, a move to `seen` is sent on any of 3.1's three grounds; a held-back move is reconsidered only on 3.2's two triggers; 3.3's rules hold. Record how the store tracks "a command has succeeded in this opening" and which events count as 3.2's triggers.
4. **CX10's tests** (DM-25 3.4): cases (a) to (e), with the reversals 3.4 names. Name each change to C2-C1's cursor tests and the rule that makes it (3.5).
5. **The README** (DM-24 1.5, DM-25 3.5): its cursor sentence states 3.1; its revocation sentence changes only if the change alters what it says.
6. **The record:** a new section "Stage C2-C2" in the evidence record.

**Not in C2-C2:**
- finding 3 of C2's review (it stays in the P11 plan);
- finding 1's broader test, finding 4 and finding 5 of C2's review (follow-ups due at the first change to `apps/mobile` after PR33 merges, DM-23 3.1);
- any change to the fixture adapter (DM-25 3.5): a test sends the member's own messages through the transport;
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

**A departure** from any condition above that you find necessary: stop before making it, record it and the reason, and report it. It goes back to the Dev Manager (DM-24 item 3; DM-25 item 3; DM-22 9.1).

## 4. Checks

Report the exact commands and results.

1. **The diff:** `git diff --check <START_SHA> HEAD`, and `git diff --name-only <START_SHA> HEAD`. Only owned paths changed.
2. **Classification** with the trusted policy from `main`, run outside the tree, as root `AGENTS.md` requires. Expected: full scope.

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
   - `apps/mobile/package.json`, `package-lock.json`, `.npmrc` and `dependency-inventory.json`;
   - `apps/mobile/src/contracts/generated/`;
   - `apps/mobile/src/chat/fixture-adapter.ts`;
   - `apps/mobile/app.config.ts` and `apps/mobile/scripts/development.mjs`;
   - `packages/`, `services/`, `proofs/` and `.github/`.
6. **The reversals** of DM-24 1.4 and DM-25 3.4, each with the test's output.
7. **The Foundation run on your last code commit:** its run ID, each job's conclusion (eight jobs), and the gate's log line, which must be `Application checks passed`.
   - **Wait before pushing again.** After pushing your last code commit, push nothing more to your branch until that commit's Foundation run has finished. Runs of the same branch cancel each other (the CI policy), so an early records push can cancel the code run (AM5-14).
   - A push that changes only Markdown skips the application jobs. If your last commit changes only the record, the run of record is the push run of your last code commit, and your record says so.
   - **From the Mobile job's log:**
     - `npm run check`'s test counts;
     - the rendered tests' count, with the long-conversation test named and passing;
     - the job's time and the rendered step's time, against the 15-minute timeout.
   - **The API mobile smoke** job's conclusion.
   - If your tools cannot read the run, or your branch is outside the push filter, say so; re-run or dispatch nothing.
8. **A secret scan over your whole diff:** no secret, token, API key, password or email address.

## 5. Owned paths, push and records

- **You may change:**
  - `apps/mobile/src/chat/store.ts` and `apps/mobile/src/chat/store.test.ts`;
  - `apps/mobile/src/chat/testing.ts`, only if a test needs a helper;
  - `apps/mobile/README.md`: its cursor sentence (DM-25 3.5), and its revocation sentence only if the change alters what it says;
  - the evidence record `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`: a new section "Stage C2-C2" only, after the existing sections, which stay byte-identical.
- **Nothing else.** That includes the fixture adapter, the screens, `packages/`, `services/`, `proofs/`, `.github/`, `scripts/`, any `.claude/` path, the briefs, the P11 plan and every other document. Report any other change you think is needed.
- **Commit and push** your session branch. Don't open a pull request.
- **Your section "Stage C2-C2"** in the evidence record:
  - the prompt's revision and start SHA, your head, your branch and the run of record;
  - for items 1 to 6 of section 3: done (`file:line` and its test) or left (the reason), and which test covers each of DM-24 1.1 to 1.4 and DM-25 3.1 to 3.4;
  - the mechanisms you chose (items 1 and 3), and why;
  - each change to C2-C1's cursor tests and the rule that makes it;
  - every check, with its exact results;
  - deviations and limits;
  - what the exact-head re-review must know (DM-24 1.6, DM-25 3.6).

## 6. Report

Your final message is the report Nathan relays:

- the prompt revision you received, and the commit it came from;
- the environment check;
- your branch, head SHA and tree, and the changed paths;
- for items 1 to 6 of section 3: done or left, with the recorded choices;
- every check, with its exact results, and the run of record's details from section 4 item 7;
- deviations, departures you stopped at, findings outside the work with their class, open questions and limits.

# P06.2 Stage C2 re-review prompt — the exact-head re-review of C2-C1 and C2-C2 (CX8, CX9, CX10)

- **Owner:** App Manager 8. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 25 October 2026.**
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 17: "Codex's CX9 and CX10, and C2-C2", with "Codex's CX8, and C2-C1" (revision 16).
- **Where the result goes:**
  - The reviewer reports to Nathan.
  - The manager records the review and its disposition in the [P06.2 evidence record](../testing/evidence/2026-10-05-p06-2-chat-integration.md), "Exact-head review of Stages C2-C1 and C2-C2", and in the brief's "Sessions".
  - A further correction pass, C2-C3, follows if the review asks for one (DM-25 2.1 to 2.3).
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.47 (confidence 0.66); rung probabilities low 0.00, medium 0.02, high 0.50, extra high 0.47, max 0.01, ultracode 0.00. Model probabilities Fable 5.1 0.02, Opus 5.5 0.98, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.97). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.010, Fable 5.1 at extra high 0.009, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.020, Opus 5.5 at high 0.490, Opus 5.5 at extra high 0.461, Opus 5.5 at max 0.010, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Flags: boundary between extra high and high. Sent 2026-10-25T02:43:34Z. Nathan picks the cell.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** none, on DM-26 item 3's terms (3.1 to 3.4): this prompt quotes DM-25 1.1 and 3.6, DM-23 2.6 and DM-24 1.6 as written, names DM-25 1.1's security focus, its head and run of record, its correction classes and DM-26's verdicts. It authorizes no credential use and no live provider action. This session is the only security reading of C2-C1 and C2-C2 (OD-41).
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Codex's code review of C2-C2's head (`9fd22c0`, holding `27999c7`) found nothing (DM-25 1.2).
- **Deletion condition:** prune after Stage C2's PR merges and the evidence record holds the review.

**Manager:** before giving this prompt to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **review session for P06.2 Stages C2-C1 and C2-C2**, the two correction passes on Stage C2, the mobile chat interface, in P06.2, the chat integration of the Glow dating app, private repository `amthorn78/glow-dating-app`. You review one exact code head. This prompt is revision 1, from commit `<RECORDS_COMMIT>`.

**What came before.**
- **Stage C2,** the mobile chat interface on fixtures (code `cb3a6a6`), is PR33, from the manager branch `claude/magical-wozniak-yfmmx2` into `main` (base `a8e9528`, Stage C1's merge). Its exact-head review approved it with six nits.
- **Codex found three P2 defects after it, each verified by the manager and corrected before the merge by the Dev Manager's choice:**
  - **CX8** (C2's code): the read cursor moved to the newest fetched message whenever the conversation was shown, so a long conversation's unread count cleared before its newest messages were seen. It missed C2's item 8 ("the app moves the member's own cursor forward with `ReadCursorIntent` when the member has seen newer messages, and never backward"). **C2-C1** (code `311b07e`; run of record 40145402786) corrected it under DM-23 2.1 to 2.6: the cursor moves only to the newest accepted message that has been in the conversation's visible area, by rendered layout. Its own re-review was withdrawn before it ran (AM7-13); this review covers it.
  - **CX9** (C2's code): `revoke()` left outstanding requests valid, so a late page, send, cursor command or list read could restore a revoked conversation, its composer or its row. It missed C2's item 3 and its prompt's revocation class ("let a revoked member see a conversation's history or send in it").
  - **CX10** (C2-C1's cursor code): with no known cursor position at opening (C2C1-X1), the store looked for an incoming message only in the loaded window, so an incoming message outside it stayed unread until a later one was viewed. It missed C2's item 8.
  - **C2-C2** (code `27999c7`, records `3ff47a7`) corrected CX9 under DM-24 1.1 to 1.6 and CX10 under DM-25 3.1 to 3.6: `revoke()` advances the conversation's and the list's epochs and drops a pending send; `cursorKnown` and the held summary decide a move while the position is unknown, with two reconsideration triggers.
- **The run of record** is C2-C2's push run 40152538074 on `27999c7`. All eight jobs passed; mobile unit tests 610 of 610, rendered `97 passed (4.9m)`, Mobile checks 6 min 31 s of 15.

- **The code head under review is `27999c7`.** You work at `<RECORDS_COMMIT>`, whose non-Markdown paths are byte-identical to `27999c7` (the start gate checks this), so the records you read are current.
- **Your scope:**
  - **C2-C1's code change:** `git diff cb3a6a6 311b07e` over every non-Markdown path, read whole.
  - **C2-C2's code change:** `git diff 311b07e 27999c7` over every non-Markdown path, read whole.
  - **The store as it stands at `27999c7`,** because C2-C2 changes code C2-C1 wrote: its cursor path and its revocation path, whole.
  - **Read against PR33's whole code change** (`git diff origin/main...HEAD`) wherever these touch C2's code.
  - **The Markdown records,** for their claims.
- **The review is offline:** the code, the offline tests and the run's logs. You call no provider and need no database.

**The Dev Manager's conditions for this review, as written.**

DM-25 1.1:

> - **1.1 What the re-review reads.**
>   - **Its head:** the code commit that holds C2-C2's code, named as workflow step 6 says.
>   - **C2-C1's diff** against DM-23 2.1 to 2.6.
>   - **C2-C2's diff** against DM-24 1.1 to 1.6 and 3.1 to 3.6 here.
>   - **The store's cursor path and revocation path as they stand at that head,** because C2-C2 changes code C2-C1 wrote. DM-23 2.6's reading list (the cursor path, the replaced unit test, the long-conversation rendered test) is read at that head.
>   - **The run of record of C2-C2's code commit:** all eight jobs, and the rendered tests.
>   - **Its security focus areas, named in its prompt.** It is the only security reading of both passes (OD-41; workflow step 7):
>     - no history or composer after a revocation (OD-12; CX9);
>     - the display rule at the client boundary unchanged;
>     - no provider package, socket or network client added.

DM-25 3.6:

> - **3.6 The re-review** (replaces c.6). The re-review of item 1 also:
>   - names CX10 and C2's item 8 for this change;
>   - reads 3.1's three grounds and 3.2's triggers;
>   - checks that no path sends a command on a viewing report or to any target but `seen`;
>   - checks that a response DM-24 1.1 makes ineffective triggers no reconsideration;
>   - weighs one effect: a move reconsidered by a list read can be sent after the screen is left. C2-C1 already allows that for a `seen` set while shown and in the foreground ("a move to a message that was in view may now complete after the screen is left", the evidence record's "Stage C2-C1").

DM-23 2.6:

> - **2.6 The re-review.** Its prompt names item 8 and CX8, and has the reviewer read the store's cursor path, the replaced unit test and the long-conversation rendered test. Codex's review of the new final head follows.
>   - C2's exact-head review confirmed DM-22 6.1 to 7.2 but not item 8's "seen".
>   - My DM-22 conditions for C2 named no test for "seen" either. The re-review closes that gap; nothing else changes.

DM-24 1.6:

> - **1.6 The re-review of C2-C2's diff:**
>   - it names CX9, C2's item 3 and the prompt's revocation class;
>   - it checks each caller of `revoke()`, and a late response of each request type in 1.1, the list included;
>   - it searches the store's other asynchronous paths for any that can move a conversation out of `revoked` with a response requested before the revocation.
>
>   Codex's review of the new final head follows.

**The security focus of this review** (DM-25 1.1, as above): no history or composer after a revocation (OD-12; CX9); the display rule at the client boundary unchanged; no provider package, socket or network client added.

**The Dev Manager's verdicts for you to weigh, and contest if you disagree** (DM-26 3.4):
- **The two substituted test pairings are accepted** (DM-26 item 1). DM-24 1.4 asks each test to revoke "through a send's refusal and, separately, through a cursor command's"; a held send cannot be revoked by a second send, nor a held command by a second command, under the one-at-a-time rules. `store.test.ts:532` and `:544` use a head read's refusal instead. Check that each revokes while its request is held, and that the other five cases run both named refusals.
- **C2C2-X1 is carried as a P11 requirement** (DM-26 2.1): a read made after a revocation sets `loading`, so the screen shows the composer, with no history, until Glow answers; a send in that window is refused. Say if you find it a fix-here class, or a defect against an item of C2's prompt.
- **C2C2-X2 is a limit** (DM-26 2.3): after a revocation and a later read, a new cursor command can overlap one made before; the old answer changes nothing, and the server moves cursors forward only.
- **Two behaviour changes the session recorded are yours to judge:** the idle send state after a send's own refusal (DM-24 1.2), and reads that overlap across a revocation (1.3).

**What comes after this review: the correction classes** (DM-25 2.1; DM-26 3.3). Report every finding with its severity. A correction pass, C2-C3, takes every blocking finding, and any should-fix finding that could do any of these:
- move the read cursor, or clear unread, for a message that was not inside the visible area while the conversation was shown and the app was in the foreground (C2's item 8; DM-23 2.1, 2.2);
- move the cursor on a fetch alone, backward, to an unsent message or to any target but `seen`, on a viewing report, or in more than one command at a time within an epoch (DM-23 2.1, 2.3; DM-25 3.3);
- fail to mark read, by the rules of DM-23 2.1 to 2.3 and DM-25 3.1 to 3.2, a message that has been in view (CX10);
- let a response requested before a revocation change any state or start anything, or move a conversation out of `revoked` (CX9; DM-24 1.1, 1.2);
- let a revoked member see a conversation's history or send in it;
- let a provider field, provider ID or provider text reach a render, a stored client state or a log;
- let the app make a network call, load a provider package, poll in the background or after its screen is left, or run outside the development fixture mode;
- change `Page`'s behaviour on another screen, the fixture adapter, or any dependency or contract (DM-23 2.5; DM-24 1.5; DM-25 3.5);
- let a test pass where it should fail;
- make a record claim more than the code, the tests or the runs show;
- leave a condition of DM-23 (2.1 to 2.5, 3.1), DM-24 (1.1 to 1.5) or DM-25 (3.1 to 3.5) unmet.

A defect that misses an item of C2's prompt is also fixed before the merge (DM-23's rule). Everything else goes into the records. For each finding, say whether it falls in one of these classes.

**How you work:**
- Nathan started you manually and will relay your report to the manager (App Manager 8). You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - **Reversals and scratch work go in a copy outside the repository, never the checkout** (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
- **Never:**
  - dump the environment, or print a credential, token or password;
  - call Stream or any other provider, or run any harness command that reaches it;
  - connect to any database, HDE, Railway or any other provider;
  - run `playwright install`, `eas` or `migrate`.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If one is present, stop and report: this session must start in `Glow App - No Stream`.
3. **The toolchain.** The pinned toolchain is in `$HOME/.local/bin`: Node 24.19.0 and npm 11.9.0 (and Python 3.12.14). Put `$HOME/.local/bin` first on PATH in every process you run.
4. **A clean process environment.** Run each component's commands in one, as `docs/operations/local-development.md` and the READMEs show: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables. Installs get the proxy and CA variables by reference, never printed.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <RECORDS_COMMIT>
git rev-parse HEAD                      # must print <RECORDS_COMMIT>
git merge-base --all origin/main HEAD   # expected: one line, a8e952895ebd3ffc9ef0e4d195c8a7111c69b3ae
git merge-base --is-ancestor <RECORDS_COMMIT> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 27999c7bd9b79fd1a1c68136b3de62b14bd32a34 HEAD -- proofs .github services scripts apps packages && echo "the code head under review"
git diff --quiet 27999c7bd9b79fd1a1c68136b3de62b14bd32a34 origin/claude/magical-wozniak-yfmmx2 -- proofs .github services scripts apps packages && echo "no code on the live branch after 27999c7"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md | grep -c -E '^#+ Exact-head review of Stages C2-C1 and C2-C2'   # must print 0
git diff --shortstat cb3a6a6dae0f3ad629a1cbd92ea299fcd5cab03a 311b07e11b7131147becd0f045665f30d29856fa -- proofs .github services scripts apps packages   # expected: 7 files changed, 402 insertions(+), 40 deletions(-)
git diff --shortstat 311b07e11b7131147becd0f045665f30d29856fa 27999c7bd9b79fd1a1c68136b3de62b14bd32a34 -- proofs .github services scripts apps packages   # expected: 3 files changed, 313 insertions(+), 16 deletions(-)
git diff --shortstat origin/main...HEAD -- proofs .github services scripts apps packages   # expected: 26 files changed, 2925 insertions(+), 7 deletions(-)
```

If any check fails, stop and report. The checks on `origin/claude/magical-wozniak-yfmmx2` read the live manager branch. The prompt is stale if this prompt's commit is not on that branch, if a non-Markdown path changed there after `27999c7`, or if this review is already recorded (AM5-15).

**Classify the change** as root `AGENTS.md` requires, with the trusted base policy outside the candidate tree and full SHAs. Run it from the repository root: the script reads git from its working directory.

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
git diff --name-only origin/main...HEAD | grep -v '\.md$' | grep -v -E '^apps/mobile/(src/|rendered/)'
```

- **Expected:** `"full": true`.
- **The last command must print nothing.** Every non-Markdown change must be under `apps/mobile/src/` or `apps/mobile/rendered/`. Anything else is code this review would not cover: stop and report it.

**Then read, completely, at `HEAD`:**

- root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md` and `apps/mobile/README.md`;
- the P06.2 brief: "Codex's CX8, and C2-C1" (revision 16), "Codex's CX9 and CX10, and C2-C2" (revision 17), and points c, e and g of "Stage C under OD-45";
- the Dev Manager's reports in `docs/continuity/dev-manager/reviews/`: DM-23 (`2026-10-24-dm-23-p06-2-cx8.md`), DM-24 (`2026-10-25-dm-24-p06-2-cx9.md`), DM-25 (`2026-10-25-dm-25-p06-2-re-review-order.md`) and DM-26 (`2026-10-25-dm-26-p06-2-c2-c2-deviation.md`);
- C2's prompt, items 3 and 8 and "Findings outside this work" (`docs/ephemeral/2026-10-24-p06-2-stage-c2-implementation-prompt.md`), and the prompts of C2-C1 and C2-C2 (`docs/ephemeral/2026-10-24-p06-2-stage-c2-c1-correction-prompt.md`, `docs/ephemeral/2026-10-25-p06-2-stage-c2-c2-correction-prompt.md`);
- the evidence record: "Codex's code review of PR33's final head", "Stage C2-C1" and its verification, "Codex's code review of C2-C1's head", "Codex's CX10 on C2-C1's cursor code", "Stage C2-C2" and its verification;
- the P11 plan's mobile-client entry (`docs/testing/p11-deferred-acceptance.md`), with C2C1-X1, C2C2-X1 and C2C2-X2;
- **the code, whole at `HEAD`:**
  - `src/chat/store.ts`: `viewed`, `noteSeen`, `indexOf`, `summary`, `moveReadCursor`, `readList`, `readHead`, `loadOlder`, `run`, `send`, `retrySend`, `revoke`, `resetConversation`, and the foreground and authority hooks;
  - `src/chat/visibility.ts` and `src/chat/screen.tsx` (the conversation's scroll container, the measurement, and `ConversationScreen`'s branches);
  - `src/chat/store.test.ts` whole, with the CX9 tests (`:490` to `:574`), the CX10 tests (`:281` to `:326`), C2-C1's cursor tests and its replaced test; `src/chat/visibility.test.ts`; `src/chat/testing.ts`;
  - `src/chat/authority.ts` (`contactVersion`), `src/chat/client.ts` and `src/chat/fixture-adapter.ts`, for the boundary and the fixture's reads;
  - `rendered/chat.spec.ts`, chiefly `:87`, `:108` and `:121`;
  - `src/components/ui.tsx` (`Page`), to confirm it is unchanged;
  - for the forward-only rule C2-C2 relies on, `services/api/glow_chat/reads.py`, `_move` (read only).

**The run's logs:** run 40152538074 on `27999c7`. Read its Mobile job (`npm run check`'s counts, the rendered tests with the long-conversation tests) and its gate. Read enough to confirm the claims above, and say what you read.

## 3. What to review

1. **CX8 and C2's item 8** (DM-23 2.1 to 2.4, 2.6): does the cursor move only to the newest accepted message that has been inside the visible area while the conversation was shown and the app was in the foreground? Trace every caller of `moveReadCursor()` and every write of `seen`; confirm that no fetch, page merge, poll or send moves the cursor by itself. Judge the visibility evidence (`measureLayout`, `onLayout`, `onScroll`), stale positions after an older page loads above, content size changes, the keyboard and a hidden screen. Say whether CX8 is closed.
2. **CX10** (DM-25 3.1 to 3.6): read 3.1's three grounds at `moveReadCursor` and 3.2's triggers (`loadOlder`, `readList`'s `sameSummary`, the follow-up after a successful command). Check that no path sends a command on a viewing report or to any target but `seen`; that `cursorKnown` is set only on an accepted response and cleared with `lastRead`; that a summary at 0 never suppresses a move the window calls for; that a response DM-24 1.1 makes ineffective triggers no reconsideration; and that a failed command is retried only after the next successful read. Weigh 3.6's effect (a move reconsidered by a list read can be sent after the screen is left). Say whether CX10 is closed.
3. **CX9 and C2's item 3** (DM-24 1.1 to 1.3, 1.6): check each caller of `revoke()`, and a late response, success or failure, of each request type in 1.1 (a head read and a queued one, an older page, a cursor command, a send and the list read). Search the store's other asynchronous paths (the foreground and authority hooks, the poll timer, `openConversation`, retries) for any that can move a conversation out of `revoked` with a response requested before the revocation. Check 1.2 (no pending send, no retry, the revoked notice the only state shown) and 1.3 (later requests decided by Glow). Say whether CX9 is closed.
4. **The tests:** does each new or changed test fail without its fix? Reproduce at least these reversals in a scratch copy: the conversation epoch's advance in `revoke()`; 3.1 reverted to the window-only test; one of 3.2's triggers removed; and C2-C1's cursor target (the replaced test and the rendered long-conversation test). Check the two substituted pairings (DM-26 item 1) and that no inherited test was loosened.
5. **Scope:** `apps/mobile` only; no dependency, contract, generated, fixture-adapter or `Page` change; every other screen's rendered tests unchanged and passing.
6. **The security focus** (above): after a revocation, no history and no successful send, through any late response; the display rule and the validation boundary unchanged; no provider package, socket, network client or background polling added. Judge C2C2-X1 against it.
7. **The records:** the README's cursor sentences (C2-C1's and C2-C2's), the evidence record's "Stage C2-C1" and "Stage C2-C2", and the P11 plan's C2C1-X1, C2C2-X1 and C2C2-X2. Does any statement claim more than the code, the tests or the runs show?
8. **The offline checks,** run at `HEAD` in a clean environment:
   - **the mobile app first:** `npm ci --ignore-scripts`, `npm run check` (610 at the run of record), `EXPO_OFFLINE=1 npm run check:expo` and `EXPO_OFFLINE=1 npm run export:development`;
   - **then the contracts:** `npm ci --ignore-scripts`, `npm run generate` with no diff, and `npm run check` (586 corpus cases). The corpus test loads the app's generated validators, so install the app first;
   - `npm run test:rendered` only if it can run without `playwright install`, marked "informational, not the pinned browser".

## 4. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<RECORDS_COMMIT>`), and the start gate's and the classification's results;
- the environment check;
- a verdict: **approve**, or **changes required**, with the findings that require them, and whether CX8, CX9, CX10 and C2's items 3 and 8 are met;
- every finding, numbered, with:
  - its severity (blocking, should fix, nit);
  - its file and line;
  - what is wrong, why it matters, and a suggested fix;
  - whether it falls in one of the correction classes above, or misses an item of C2's prompt;
- your view on each of DM-26's verdicts above;
- for each focus area, what you checked and what you found;
- the offline checks you ran, with their exact results;
- limits of the review, and open questions.

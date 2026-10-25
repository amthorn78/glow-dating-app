# P06.2 Stage C2-C1 review prompt — the exact-head re-review of C2-C1 (C2's item 8 and CX8)

- **Owner:** App Manager 7. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 25 October 2026.**
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 16: "Codex's CX8, and C2-C1", with DM-23's conditions 2.1 to 2.6 and 3.1 as written.
- **Where the result goes:**
  - The reviewer reports to Nathan.
  - The manager records the review and its disposition in the [P06.2 evidence record](../testing/evidence/2026-10-05-p06-2-chat-integration.md), "Exact-head review of Stage C2-C1", and in the brief's "Sessions".
  - A further correction pass follows if the review asks for one.
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 2.86 (confidence 0.89); rung probabilities low 0.00, medium 0.00, high 0.15, extra high 0.84, max 0.01, ultracode 0.00. Model probabilities Fable 5.1 0.02, Opus 5.5 0.98, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.97). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.003, Fable 5.1 at extra high 0.017, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.000, Opus 5.5 at high 0.147, Opus 5.5 at extra high 0.823, Opus 5.5 at max 0.010, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-10-25T00:24:34Z. Nathan picks the cell.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** none needed. DM-23 2.6 sets this re-review's content, and the prompt authorizes no credential use and no live provider action. This session is the only security reading of C2-C1 (OD-41).
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29).
- **Deletion condition:** prune after Stage C2's PR merges and the evidence record holds the review.

**Manager:** before giving this prompt to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **review session for P06.2 Stage C2-C1**, the correction pass on Stage C2's read cursor, in P06.2, the chat integration of the Glow dating app, private repository `amthorn78/glow-dating-app`. You review C2-C1 at one exact head. This prompt is revision 1, from commit `<RECORDS_COMMIT>`.

**What came before.**
- **Stage C2,** the mobile chat interface on fixtures (code `cb3a6a6`), is PR33, from the manager branch `claude/magical-wozniak-yfmmx2` into `main` (base `a8e9528`, Stage C1's merge). Its exact-head review approved it with six nits.
- **C2's prompt, item 8,** asked for this: "the app moves the member's own cursor forward with `ReadCursorIntent` when the member has seen newer messages, and never backward".
- **Codex's code review of PR33's final head found CX8:** the read cursor moved to the newest fetched message whenever the conversation was shown in the foreground. The screen neither scrolled to the newest message nor tracked what was visible, so a long conversation's unread count cleared before its newest messages were seen. `store.test.ts:141` asserted that behaviour.
- **The Dev Manager's DM-23** chose to correct it before PR33 merges, in C2-C1, with conditions 2.1 to 2.6. 2.6 sets this re-review: it names item 8 and CX8, and you read the store's cursor path, the replaced unit test and the long-conversation rendered test. C2's exact-head review confirmed DM-22 6.1 to 7.2, but not item 8's "seen"; this re-review closes that gap.
- **C2-C1** (code `311b07e`, records `73ef97e`) did this:
  - the conversation got its own scroll container (`ConversationPage`), and `Page` is unchanged;
  - each message row is measured against the scroll content with `measureLayout`, and the visible area comes from `onLayout` and `onScroll` (`src/chat/visibility.ts`, `screen.tsx`);
  - the store's `viewed()` records what is in view, and the cursor moves only to the newest accepted message that has been in view;
  - `store.test.ts:141` is replaced, with four more store tests, four visibility tests and three rendered tests (`chat.spec.ts:87`, `:108`, `:121`);
  - two README sentences are corrected (3.1).

**The run of record** is the session's push run 40145402786 on `311b07e`. All eight jobs passed. The Mobile job took 6 min 48 s of its 15-minute timeout, and its rendered step printed `97 passed (4.9m)`. The head's code is byte-identical to `311b07e`'s.

- **You review one exact head:** `<RECORDS_COMMIT>`.
- **Your scope:**
  - **C2-C1's code change:** `git diff cb3a6a6 HEAD` over every non-Markdown path, read whole. That is six files, about 380 lines added.
  - **Read against PR33's whole code change** (`git diff origin/main...HEAD`) wherever C2-C1's code touches C2's.
  - **The Markdown records,** for their claims.
- **The review is offline:** the code, the offline tests and the run's logs. You call no provider and need no database.
- **What comes after this review.** Report every finding with its severity. A correction pass takes every blocking finding. It also takes any should-fix finding that could do any of these:
  - move the read cursor, or clear unread, for a message that was not inside the visible area while the conversation was shown and the app was in the foreground (C2's item 8; DM-23 2.1, 2.2);
  - move the cursor on a fetch alone, backward, to an unsent message, for an older page, or in more than one command at a time (2.1, 2.3);
  - fail to mark a message read once it has been in view (2.1, 2.2);
  - let a provider field, provider ID or provider text reach a render, a stored client state or a log;
  - let a revoked member see a conversation's history or send in it;
  - let the app poll in the background or after its screen is left;
  - change `Page`'s behaviour on another screen, or any dependency or contract (2.5);
  - let a test pass where it should fail, including the changed inherited test `store.test.ts:94`;
  - make a record claim more than the code, the tests or the runs show;
  - leave a DM-23 condition (2.1 to 2.5, 3.1) unmet.

  Everything else goes into the records. For each finding, say whether it falls in one of those classes.

**How you work:**
- Nathan started you manually and will relay your report to the manager (App Manager 7). You are neither the manager nor an implementer.
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
git diff --quiet <RECORDS_COMMIT> origin/claude/magical-wozniak-yfmmx2 -- proofs .github services scripts apps packages && echo "no code after this prompt's commit"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md | grep -c -E '^#+ Exact-head review of Stage C2-C1'   # must print 0
git diff --quiet 311b07e11b7131147becd0f045665f30d29856fa HEAD -- proofs .github services scripts apps packages && echo "the code of the run of record"
git diff --shortstat cb3a6a6dae0f3ad629a1cbd92ea299fcd5cab03a HEAD -- proofs .github services scripts apps packages   # expected: 7 files changed, 402 insertions(+), 40 deletions(-) (six code files and the mobile README)
git diff --shortstat origin/main...HEAD -- proofs .github services scripts apps packages   # expected: 26 files changed, 2628 insertions(+), 7 deletions(-)
```

If any check fails, stop and report. The checks on `origin/claude/magical-wozniak-yfmmx2` read the live manager branch. The prompt is stale if:
- this prompt's commit is not on that branch;
- code landed after it;
- or this review is already recorded.

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
- the P06.2 brief: "Codex's CX8, and C2-C1" (revision 16), and point e of "Stage C under OD-45";
- the DM-23 report, `docs/continuity/dev-manager/reviews/2026-10-24-dm-23-p06-2-cx8.md`;
- C2's prompt, item 8 (`docs/ephemeral/2026-10-24-p06-2-stage-c2-implementation-prompt.md`), and C2-C1's prompt (`docs/ephemeral/2026-10-24-p06-2-stage-c2-c1-correction-prompt.md`);
- the evidence record's "Codex's code review of PR33's final head", "Stage C2-C1" and "Manager verification of Stage C2-C1";
- **the code, whole at `HEAD`:**
  - the store's cursor path: `src/chat/store.ts`, chiefly `viewed()`, `noteSeen()`, `moveReadCursor()`, the foreground handling and the head read;
  - `src/chat/visibility.ts` and `src/chat/screen.tsx` (the conversation's scroll container and the measurement);
  - `src/chat/store.test.ts`, with the replaced test (formerly `:141`) and the changed inherited test `:94`, and `src/chat/visibility.test.ts`;
  - `rendered/chat.spec.ts`, chiefly `:87`, `:108` and `:121`;
  - `src/components/ui.tsx` (`Page`), to confirm it is unchanged.

**The run's logs:** run 40145402786 on `311b07e`. Read its Mobile job (`npm run check`'s counts, the rendered tests with the long-conversation tests) and its gate. Read enough to confirm the claims below, and say what you read.

## 3. What to review

1. **C2's item 8 and CX8** (DM-23 2.1). Does the cursor now move only to the newest accepted message that has been inside the visible area while the conversation was shown and the app was in the foreground?
   - Trace every caller of `moveReadCursor()` and every write of `seen`.
   - Confirm that no fetch, page merge, poll or send moves the cursor by itself.
   - Say whether CX8 is closed.
2. **The visibility evidence** (2.1, 2.2):
   - Is it the rendered layout, through `measureLayout`, `onLayout` and `onScroll`, never a fetch?
   - Can a row be counted as in view when it is not: stale positions after an older page loads above it, content size changes, the keyboard, a hidden screen?
   - Can a row in view fail to be counted?
   - Judge the "wholly inside, or filling the area" rule and the 1 px tolerance.
3. **Opening and new messages** (2.2). The screen opens at the top. A message arriving while the member is scrolled up does not move the screen and is not marked read until scrolled into view.
4. **The command** (2.3):
   - one in flight, then a follow-up;
   - sent only when the position passes a message from the other member;
   - never backward, never to an unsent message, never for older pages, never in the background;
   - the retry after a failed command.

   **Judge the behaviour change** the session recorded: a move to a message that was in view can now complete after the member leaves the screen.
5. **The tests** (2.4). Does each store test, visibility test and rendered test fail without the fix? Reproduce at least the reversal of the store's cursor target and of the rendered long-conversation test, in a scratch copy.
   - **The replaced test** (formerly `store.test.ts:141`): does it now assert item 8?
   - **The changed inherited test `store.test.ts:94`** (DM-22 2.2): are its 2.2 assertions intact?
   - The rendered tests press controls with a DOM `click()`, so that Playwright does not scroll the conversation. Does that make any rendered assertion pass where a real tap would fail?
6. **Scope** (2.5):
   - `apps/mobile` only;
   - no dependency, contract or generated change;
   - `Page` unchanged, and every other screen's rendered tests unchanged and passing.
7. **The rest of C2 still holds.** C2's display rule, validation boundary, revocation handling, polling and keys are unchanged by C2-C1, or still meet DM-22 6.1 to 7.2 where C2-C1 touches them (`screen.tsx`, `store.ts`). This is the security focus of this review.
8. **The records:**
   - the README's two sentences (3.1): the cursor rule, and the forms the no-provider test catches;
   - the evidence record's "Stage C2-C1".

   Does any statement claim more than the code, the tests or the runs show? Judge **C2C1-X1** (no contract carries the cursor position), which the manager noted in the P11 plan.
9. **The offline checks,** run at `HEAD` in a clean environment:
   - **the mobile app first:** `npm ci --ignore-scripts`, `npm run check` (591 at the run of record), `EXPO_OFFLINE=1 npm run check:expo` and `EXPO_OFFLINE=1 npm run export:development`;
   - **then the contracts:** `npm ci --ignore-scripts`, `npm run generate` with no diff, and `npm run check` (586 corpus cases). The corpus test loads the app's generated validators, so install the app first;
   - `npm run test:rendered` only if it can run without `playwright install`, marked "informational, not the pinned browser".

## 4. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<RECORDS_COMMIT>`), and the start gate's and the classification's results;
- the environment check;
- a verdict: **approve**, or **changes required**, with the findings that require them, and whether CX8 and C2's item 8 are met;
- every finding, numbered, with:
  - its severity (blocking, should fix, nit);
  - its file and line;
  - what is wrong, why it matters, and a suggested fix;
  - whether it falls in one of the correction classes above;
- for each focus area, what you checked and what you found;
- the offline checks you ran, with their exact results;
- limits of the review, and open questions.

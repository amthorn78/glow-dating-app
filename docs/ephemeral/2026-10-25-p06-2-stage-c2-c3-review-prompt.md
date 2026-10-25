# P06.2 Stage C2-C3 review prompt — the exact-head re-review of C2-C3 (F1, CX10, CX11, C2's item 8)

> **Held on 25 October 2026.** Codex posted CX12 on `9422d9e` at 04:38 UTC, after this prompt went to Nathan; a fix would change the code under review (AM7-13). Whether it runs as it stands or is replaced follows DM-28.

- **Owner:** App Manager 8. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 25 October 2026.**
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 18: "The re-review's F1, and C2-C3".
- **Where the result goes:**
  - The reviewer reports to Nathan.
  - The manager records the review and its disposition in the [P06.2 evidence record](../testing/evidence/2026-10-05-p06-2-chat-integration.md), "Exact-head review of Stage C2-C3", and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.15 (confidence 0.83); rung probabilities low 0.00, medium 0.06, high 0.74, extra high 0.20, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.99, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.99). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.059, Opus 5.5 at high 0.733, Opus 5.5 at extra high 0.198, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.001, Sonnet 5.5 at high 0.007, Sonnet 5.5 at extra high 0.002, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-10-25T04:35:27Z. Nathan picks the cell.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** none needed. DM-27 1.4 sets this re-review's content, quoted below as written; the prompt authorizes no credential use and no live provider action. This session is the only security reading of C2-C3 (OD-41).
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Codex's code review of C2-C3's head (`9776c6f`, holding `85b9844`) completed at 04:35 UTC with no finding (DM-27 1.4, DM-25 1.2).
- **Deletion condition:** prune after Stage C2's PR merges and the evidence record holds the review.

**Manager:** before giving this prompt to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **review session for P06.2 Stage C2-C3**, the third correction pass on Stage C2, the mobile chat interface, in P06.2, the chat integration of the Glow dating app, private repository `amthorn78/glow-dating-app`. You review one exact code head. This prompt is revision 1, from commit `<RECORDS_COMMIT>`.

**What came before.**
- **Stage C2** (code `cb3a6a6`), with its correction passes **C2-C1** (code `311b07e`; CX8, the read cursor moves only over messages in view) and **C2-C2** (code `27999c7`; CX9, a revocation invalidates every outstanding request; CX10, an unknown cursor position is not treated as known), is PR33, from the manager branch `claude/magical-wozniak-yfmmx2` into `main` (base `a8e9528`).
- **The exact-head re-review of C2-C1 and C2-C2** (code head `27999c7`) closed CX8 and CX9, and CX10 for the case raised, and asked for changes for **F1**: once a cursor command had succeeded, `cursorKnown` stayed true even when `lastRead` was no longer among the loaded messages. A head read answered `stale` reloads only the newest page, so `lastRead` could fall before the window and `cursorKnown` held back a move DM-25 3.1's grounds called for: an incoming message stayed unread. Codex later posted the same defect as **CX11** ([thread](https://github.com/amthorn78/glow-dating-app/pull/33#discussion_r4369549700)).
- **The Dev Manager's DM-27** chose a correction pass, C2-C3, with conditions 1.1 to 1.4, and amended DM-25 3.1's "Once a command has succeeded, DM-23 2.3 holds as written" to "While `lastRead` is among the loaded accepted messages, DM-23 2.3 holds as written".
- **C2-C3** (code `85b9844`, records `ccf8392`) removed `cursorKnown` and holds a move back by the known position only while `from >= 0` (`lastRead` in the window), with three tests (`store.test.ts:649`, `:660`, `:673`) through a `stale`-answering test transport, and the README's cursor sentence.
- **The run of record** is C2-C3's push run 40160547922 on `85b9844`. All eight jobs passed; mobile unit tests 613 of 613, rendered `97 passed (4.8m)`, Mobile checks 6 min 36 s of 15.

- **The code head under review is `85b9844`.** You work at `<RECORDS_COMMIT>`, whose non-Markdown paths are byte-identical to `85b9844` (the start gate checks this).
- **Your scope:**
  - **C2-C3's code change:** `git diff 27999c7 85b9844` over every non-Markdown path, read whole (three files).
  - **The store's cursor path at `85b9844`,** whole, and every assignment to `accepted` and `lastRead`.
  - **The Markdown records,** for their claims: the evidence record's "Stage C2-C3" and "Manager verification of Stage C2-C3", and the README's cursor sentence.
- **The review is offline:** the code, the offline tests and the run's logs. You call no provider and need no database.

**The Dev Manager's conditions for this review, as written.**

DM-27 1.1 (the rule under review):

> - **1.1 The position is known only while `lastRead` is among the loaded accepted messages** (replaces d.1).
>   - **Why one test suffices:** `lastRead` is set only by a successful command and cleared wherever the store forgets the position. So this one test covers both "a command has succeeded in this opening" and "the window still holds it".
>   - **While it holds,** DM-23 2.3 holds as written. **Otherwise,** DM-25 3.1's three grounds apply.
>   - **`cursorKnown` is removed,** since it would add nothing. The record says so, and why.
>   - **The amendment:** DM-25 3.1's "Once a command has succeeded, DM-23 2.3 holds as written" reads "While `lastRead` is among the loaded accepted messages, DM-23 2.3 holds as written".

DM-27 1.4:

> - **1.4 What follows** (replaces d.4).
>   - **First,** Codex's review of C2-C3's code head, with each finding handled, as DM-25 1.2 sets it.
>   - **Then C2-C3's exact-head re-review,** of its delta from `27999c7` (DM-25 2.2). It:
>     - names F1, CX10 and C2's item 8;
>     - reads 1.1 at the head;
>     - searches every assignment to `accepted` and `lastRead` (`mergeHead`'s newest branch, `loadOlder`, `revoke`, `resetConversation`, the command's success) for any path that leaves the position treated as known while `lastRead` is outside the window.
>   - **Its prompt names:**
>     - its correction classes (DM-25 2.1);
>     - its security focus: the revocation path and the client boundary unchanged, and no provider package, socket or network client added.
>   - **Then,** Codex on the final head, the final run, the CX8, CX9 and CX10 threads resolved, the pre-merge checklist and the merge.

**The security focus of this review** (DM-27 1.4): the revocation path and the client boundary unchanged; no provider package, socket or network client added.

**What comes after this review: the correction classes** (DM-25 2.1). Report every finding with its severity. A further correction pass takes every blocking finding, and any should-fix finding that could do any of these:
- move the read cursor, or clear unread, for a message that was not inside the visible area while the conversation was shown and the app was in the foreground (C2's item 8; DM-23 2.1, 2.2);
- move the cursor on a fetch alone, backward, to an unsent message or to any target but `seen`, on a viewing report, or in more than one command at a time within an epoch (DM-23 2.1, 2.3; DM-25 3.3);
- fail to mark read, by the rules of DM-23 2.1 to 2.3, DM-25 3.1 to 3.2 and DM-27 1.1, a message that has been in view (CX10, F1, CX11);
- let a response requested before a revocation change any state or start anything, or move a conversation out of `revoked` (CX9; DM-24 1.1, 1.2);
- let a revoked member see a conversation's history or send in it;
- let a provider field, provider ID or provider text reach a render, a stored client state or a log;
- let the app make a network call, load a provider package, poll in the background or after its screen is left, or run outside the development fixture mode;
- change `Page`, the fixture adapter, or any dependency or contract (DM-23 2.5; DM-27 1.3);
- let a test pass where it should fail;
- make a record claim more than the code, the tests or the runs show;
- leave a condition of DM-27 (1.1 to 1.3) unmet.

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
git diff --quiet 85b98444320326742e642e8f2d01f720cfb77f27 HEAD -- proofs .github services scripts apps packages && echo "the code head under review"
git diff --quiet 85b98444320326742e642e8f2d01f720cfb77f27 origin/claude/magical-wozniak-yfmmx2 -- proofs .github services scripts apps packages && echo "no code on the live branch after 85b9844"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md | grep -c -E '^#+ Exact-head review of Stage C2-C3'   # must print 0
git diff --shortstat 27999c7bd9b79fd1a1c68136b3de62b14bd32a34 85b98444320326742e642e8f2d01f720cfb77f27 -- proofs .github services scripts apps packages   # expected: 3 files changed, 92 insertions(+), 23 deletions(-)
git diff --shortstat origin/main...HEAD -- proofs .github services scripts apps packages   # expected: 26 files changed, 2994 insertions(+), 7 deletions(-)
```

If any check fails, stop and report. The prompt is stale if this prompt's commit is not on the live branch, if a non-Markdown path changed there after `85b9844`, or if this review is already recorded (AM5-15).

**Classify the change** as root `AGENTS.md` requires, with the trusted base policy outside the candidate tree and full SHAs, from the repository root:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
git diff --name-only origin/main...HEAD | grep -v '\.md$' | grep -v -E '^apps/mobile/(src/|rendered/)'
```

- **Expected:** `"full": true`, and the last command prints nothing. Anything else: stop and report it.

**Then read, completely, at `HEAD`:**

- root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md` and `apps/mobile/README.md`;
- the P06.2 brief: "The re-review's F1, and C2-C3" (revision 18) and "Codex's CX9 and CX10, and C2-C2" (revision 17);
- the DM-27 report (`docs/continuity/dev-manager/reviews/2026-10-25-dm-27-p06-2-re-review-f1.md`), and the DM-25 report's 3.1 to 3.4 and the DM-23 report's 2.1 to 2.3;
- C2's prompt, item 8 (`docs/ephemeral/2026-10-24-p06-2-stage-c2-implementation-prompt.md`), and C2-C3's prompt (`docs/ephemeral/2026-10-25-p06-2-stage-c2-c3-correction-prompt.md`);
- the evidence record: "Exact-head review of Stages C2-C1 and C2-C2", "Stage C2-C3" and "Manager verification of Stage C2-C3";
- **the code, whole at `HEAD`:** `src/chat/store.ts` (`moveReadCursor`, `readHead`, `mergeHead`, `loadOlder`, `readList`, `revoke`, `resetConversation`, the command's success and follow-up); `src/chat/store.test.ts` (`:613` to `:690`, with `:193`, `:210` and the CX9 and CX10 tests); `src/chat/testing.ts`; for the server's forward-only rule, `services/api/glow_chat/reads.py`, `_move` and the newer-cursor refusal (read only).

**The run's logs:** run 40160547922 on `85b9844`. Read its Mobile job (`npm run check`'s counts, the rendered tests) and its gate, enough to confirm the claims above, and say what you read.

## 3. What to review

1. **F1 and CX11, under DM-27 1.1:** does a move get held back by the known position only while `lastRead` is among the loaded accepted messages? Read `from >= 0` at `moveReadCursor`, and say whether F1 and CX11 are closed.
2. **Every assignment to `accepted` and `lastRead`** (DM-27 1.4): `mergeHead`'s newest and incremental branches, `loadOlder`, `revoke`, `resetConversation`, the command's success and its follow-up. Is there any path that leaves the position treated as known while `lastRead` is outside the window, or treated as unknown while it is inside?
3. **The rest of the cursor rule holds:** DM-23 2.1 to 2.3 (target `seen`, forward only, one command per epoch, no command on a viewing report), DM-25 3.1's three grounds and 3.2's triggers (unchanged), and CX10's tests and `:193`, `:210` passing unchanged.
4. **The tests:** do (a), (b) and (c) each fail without the fix? Reproduce at least the session's S1 (the start commit's `store.ts`) and S2 (`from >= 0 ||` removed) in a scratch copy. Is the `stale` test transport a faithful stand-in for C1's newer-cursor refusal?
5. **Scope and security:** only `store.ts`, `store.test.ts` and the README changed in code paths; the revocation path changed only by dropping the flag's clear; the client boundary, validators and display rule untouched; no new import, provider package, `fetch`, socket, `EventSource`, `console`, timer or background poll.
6. **The records:** the README's cursor sentence, the evidence record's "Stage C2-C3" and "Manager verification of Stage C2-C3", and the P11 plan's C2C1-X1 entry. Does any statement claim more than the code, the tests or the runs show?
7. **The offline checks,** run at `HEAD` in a clean environment:
   - **the mobile app first:** `npm ci --ignore-scripts`, `npm run check` (613 at the run of record), `EXPO_OFFLINE=1 npm run check:expo` and `EXPO_OFFLINE=1 npm run export:development`;
   - **then the contracts:** `npm ci --ignore-scripts`, `npm run generate` with no diff, and `npm run check` (586 corpus cases);
   - `npm run test:rendered` only if it can run without `playwright install`, marked "informational, not the pinned browser".

## 4. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<RECORDS_COMMIT>`), and the start gate's and the classification's results;
- the environment check;
- a verdict: **approve**, or **changes required**, with the findings that require them, and whether F1, CX11, CX10 and C2's item 8 are met;
- every finding, numbered, with its severity (blocking, should fix, nit), its file and line, what is wrong, why it matters, a suggested fix, and whether it falls in one of the correction classes above;
- for each focus area, what you checked and what you found;
- the offline checks you ran, with their exact results;
- limits of the review, and open questions.

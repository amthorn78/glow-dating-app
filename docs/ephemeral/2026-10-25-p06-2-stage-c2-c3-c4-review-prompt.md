# P06.2 Stages C2-C3 and C2-C4 review prompt — the exact-head re-review of C2-C3 and C2-C4 (F1, CX11, CX12, the `stale` path)

- **Owner:** App Manager 8. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 25 October 2026.**
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 20: "C2-C4's audit observation, and the combined re-review", with "Codex's CX12, and C2-C4" (revision 19) and "The re-review's F1, and C2-C3" (revision 18).
- **Where the result goes:**
  - The reviewer reports to Nathan.
  - The manager records the review and its disposition in the [P06.2 evidence record](../testing/evidence/2026-10-05-p06-2-chat-integration.md), "Exact-head review of Stages C2-C3 and C2-C4", and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.36 (confidence 0.73); rung probabilities low 0.00, medium 0.02, high 0.60, extra high 0.37, max 0.01, ultracode 0.00. Model probabilities Fable 5.1 0.03, Opus 5.5 0.97, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.96). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.001, Fable 5.1 at high 0.018, Fable 5.1 at extra high 0.011, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.019, Opus 5.5 at high 0.582, Opus 5.5 at extra high 0.359, Opus 5.5 at max 0.010, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-10-25T17:04:07Z. Nathan picks the cell.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** none needed. DM-28 2.2 to 2.4 and DM-29 2.1 to 2.3 set this re-review's content, and the conditions it reads are quoted below as written (DM-29 2.1). The prompt authorizes no credential use and no live provider action. This session is the only security reading of C2-C3 and C2-C4 (OD-41).
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29).
  - Codex's code review of `33bae36`, which holds C2-C4's code `d3d7300`, completed at 15:53 UTC with no finding (DM-29 2.3).
  - Codex's pass on the commit holding this prompt completed with no new finding before it went to Nathan (DM-28 2.4).
- **Deletion condition:** prune after Stage C2's PR merges and the evidence record holds the review.

**Manager:** before giving this prompt to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **review session for P06.2 Stages C2-C3 and C2-C4**, the third and fourth correction passes on Stage C2, the mobile chat interface, in P06.2, the chat integration of the Glow dating app, private repository `amthorn78/glow-dating-app`. You review one exact code head. This prompt is revision 1, from commit `<RECORDS_COMMIT>`.

**What came before.**
- **Stage C2** (code `cb3a6a6`), with its correction passes **C2-C1** (code `311b07e`; CX8, the read cursor moves only over messages in view) and **C2-C2** (code `27999c7`; CX9, a revocation invalidates every outstanding request; CX10, an unknown cursor position is not treated as known), is PR33, from the manager branch `claude/magical-wozniak-yfmmx2` into `main` (base `a8e9528`).
- **The exact-head re-review of C2-C1 and C2-C2** (code head `27999c7`) closed CX8 and CX9, and CX10 for the case raised. It asked for changes for **F1**: after a head read answered `stale` reloads only the newest page, `lastRead` can fall before the window while the old flag `cursorKnown` still holds a move back, so an incoming message stays unread. Codex later posted the same defect as **CX11** ([thread](https://github.com/amthorn78/glow-dating-app/pull/33#discussion_r4369549700)).
- **C2-C3** (DM-27; code `85b9844`) removed `cursorKnown`: a move is held back by the known position only while `lastRead` is among the loaded accepted messages. It added three tests (`store.test.ts:649`, `:660`, `:673`) through a `stale`-answering test transport, `staleOnce`. Its run of record is 40160547922. Its own re-review was withdrawn without running (DM-28 2.1): this review replaces it.
- **Codex then posted CX12** ([thread](https://github.com/amthorn78/glow-dating-app/pull/33#discussion_r4369664712)): an older-page request still in flight when a `stale` answer's reload replaced the window was merged into the reload's window and set `olderCursor` from the discarded one, so the history between the two windows was shown with a silent gap and could not be reached.
- **C2-C4** (DM-28; code `a328bc7`, then `d3d7300`, test-only; records `b60409b`):
  - adds `windowEpoch` (`store.ts:86`), advanced at the replacement itself (`:266`);
  - drops an invalidated older page, success or failure, in `loadOlder` (`:291`, `:303`); a refusal that ends access still revokes (`:300-303`);
  - keys the one-at-a-time slot by the window (`:285-286`, `:304`);
  - turns a `loading` older-page state into `idle` when the reload merges (`:244-246`);
  - adds tests (a) to (f) (`store.test.ts:759` to the end) on a new `pages()` transport composed under `staleOnce`, with no existing test changed.
- **The run of record** is C2-C4's push run 40206318661 on `d3d7300`: all eight jobs passed; mobile unit tests 621 of 621, rendered `97 passed (4.8m)`, Mobile checks 6 min 41 s of 15.
- **C2-C4's audit** found no defect beyond CX12 and one observation: an older-page error shown before a replacement survives it, because `:245` turns only `loading` into `idle`. **DM-29** recorded it as a follow-up (1.1 to 1.4) and named it, with an edge and the class comment's sentence at `:65`, for you to confirm or challenge (2.2).

- **The code head under review is `d3d7300`.** You work at `<RECORDS_COMMIT>`, whose non-Markdown paths are byte-identical to `d3d7300` (the start gate checks this).
- **Your scope** (DM-28 2.2):
  - **C2-C3's delta:** `git diff 27999c7 85b9844` over every non-Markdown path, read whole (three files), against DM-27 1.1, with DM-27 1.4's search of every assignment to `accepted` and `lastRead`.
  - **C2-C4's delta:** `git diff 85b9844 d3d7300` over every non-Markdown path, read whole (two files), against DM-28 1.1 to 1.5.
  - **The `stale` path as a whole at `d3d7300`:** every request that can be outstanding when the window is replaced, and each piece of window-bound state, checked against C2-C4's audit, not taken from it.
  - **DM-29 2.2's three items:** the observation's path, the edge with the Dev Manager's trace of C1, and the class comment's sentence at `:65`.
  - **The Markdown records,** for their claims: the evidence record's "Stage C2-C3", "Manager verification of Stage C2-C3", "Stage C2-C4" and "Manager verification of Stage C2-C4"; the README's cursor sentence; the P11 plan's C2C1-X1 entry.
  - **The run of record** of C2-C4's code commit: all eight jobs, and the rendered tests.
- **The review is offline:** the code, the offline tests and the run's logs. You call no provider and need no database.

**The Dev Manager's conditions for this review, as written.**

DM-27 1.1 (C2-C3's rule):

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

DM-28 1.1 to 1.5 (C2-C4's conditions):

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

DM-28 2.2 and 2.3 (this review):

> - **2.2 One exact-head re-review** of the code head that holds C2-C3 and C2-C4. It is the only security reading of both passes (OD-41). It reads:
>   - **C2-C3's delta from `27999c7`** against DM-27 1.1, with DM-27 1.4's search of every assignment to `accepted` and `lastRead`;
>   - **C2-C4's delta from `85b9844`** against 1.1 to 1.5 here;
>   - **the `stale` path as a whole, at that head:**
>     - every request that can be outstanding when the window is replaced: a head read and one queued behind it, an older page, a cursor command, a send and a list read;
>     - each piece of window-bound state, checked against the session's audit (1.4), not taken from it;
>   - **the run of record** of C2-C4's code commit: all eight jobs, and the rendered tests.
> - **2.3 Its prompt names:**
>   - **the correction classes,** as C2-C3's re-review prompt lists them, plus two:
>     - an older page requested before the window was replaced that changes the window, starts anything, or leaves history unreachable or shown with a gap (CX12; 1.1, 1.2);
>     - a refusal that ends access, from any request of the open conversation, that does not revoke (1.1);
>   - **its security focus:**
>     - the revocation path unchanged, with every refusal that ends access revoking;
>     - the client boundary and the display rule unchanged;
>     - no provider package, socket or network client added;
>   - **the conditions it reads, quoted as written:** DM-27 1.1 and 1.4, and 1.1 to 1.5 here.

DM-29 1.1 to 1.4 (the observation, recorded as a follow-up):

> - **1.1 The follow-up.** It goes beside DM-23 3.1's list (the C2 review's findings 1, 4 and 5), due at the first change to `apps/mobile` after PR33 merges.
>   - **The change:** a replacement leaves the older-page state `idle` whatever it was, `error` included (`store.ts:245`).
>     - Any older-page state from before a replacement concerns the window it discarded.
>   - **A test, with its reversal:**
>     - an older page fails offline while its window is current;
>     - then a head read is answered `stale`;
>     - **expected:** after the reload, no older-page error is shown, and "Show earlier messages" asks with the reload's `older_cursor`;
>     - **reversal:** today's `:245`, which resets only `loading`.
>   - **With it,** the class comment's sentence (`:65`) is true as written.
> - **1.2 If a further correction pass runs before PR33 merges** for any other reason, it takes 1.1 with it. It is in the same files, and its scope is DM-28 1.5's.
> - **1.3 The records say what the code does now.** This is a records change only.
>   - **The evidence record's two lines** (`:3794`, `:3803`) get the manager's annotation: a `loading` state becomes `idle`, and an `error` from before the replacement is kept until 1.1 lands (DM-29 1.3).
>   - ***Implementation Control*'s phrase** gets the same correction.
>   - **The class comment** stays until 1.1 makes it true. The re-review's prompt names it (2.2).
> - **1.4 The manager's edge goes with the follow-up as a second reason for it,** and not to the P11 plan.
>   - 1.1 removes the edge.
>   - **The guard:** if 1.1 has not landed when a later phase lets a readable conversation lose accepted messages (a deletion or a moderation feature), that phase takes 1.1 first.

DM-29 2.2 (what this review names):

> - **2.2 It names these, for the reviewer to confirm or challenge at the head:**
>   - the observation's path;
>   - the manager's edge, with my trace of C1 (section 3);
>   - the class comment's sentence at `:65`.
>   - **How they are classed:**
>     - A finding on them that adds nothing to what this report states is the follow-up (1.1), not a further pass.
>     - A finding that adds an effect or a path is a finding in its own right, classed as usual.

**The security focus of this review** (DM-28 2.3):
- the revocation path unchanged, with every refusal that ends access revoking;
- the client boundary and the display rule unchanged;
- no provider package, socket or network client added.

**What comes after this review: the correction classes** (DM-25 2.1, with DM-28 2.3's two added). Report every finding with its severity. A further correction pass takes every blocking finding, and any should-fix finding that could do any of these:
- move the read cursor, or clear unread, for a message that was not inside the visible area while the conversation was shown and the app was in the foreground (C2's item 8; DM-23 2.1, 2.2);
- move the cursor on a fetch alone, backward, to an unsent message or to any target but `seen`, on a viewing report, or in more than one command at a time within an epoch (DM-23 2.1, 2.3; DM-25 3.3);
- fail to mark read, by the rules of DM-23 2.1 to 2.3, DM-25 3.1 to 3.2 and DM-27 1.1, a message that has been in view (CX10, F1, CX11);
- let a response requested before a revocation change any state or start anything, or move a conversation out of `revoked` (CX9; DM-24 1.1, 1.2);
- let an older page requested before the window was replaced change the window, start anything, or leave history unreachable or shown with a gap (CX12; DM-28 1.1, 1.2);
- let a refusal that ends access, from any request of the open conversation, fail to revoke (DM-28 1.1);
- let a revoked member see a conversation's history or send in it;
- let a provider field, provider ID or provider text reach a render, a stored client state or a log;
- let the app make a network call, load a provider package, poll in the background or after its screen is left, or run outside the development fixture mode;
- change `Page`, the fixture adapter, the README's older-page step, or any dependency or contract (DM-23 2.5; DM-27 1.3; DM-28 1.5);
- let a test pass where it should fail;
- make a record claim more than the code, the tests or the runs show;
- leave a condition of DM-27 (1.1 to 1.3) or DM-28 (1.1 to 1.5) unmet.

A defect that misses an item of C2's prompt is also fixed before the merge (DM-23's rule). A finding on DM-29 2.2's three items that adds nothing to what DM-29 states is the follow-up (DM-29 1.1), not a further pass; one that adds an effect or a path is a finding in its own right, classed as usual. Everything else goes into the records. For each finding, say whether it falls in one of these classes.

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
git diff --quiet d3d73002c454416f41ef7d787a139e8970759d89 HEAD -- proofs .github services scripts apps packages && echo "the code head under review"
git diff --quiet d3d73002c454416f41ef7d787a139e8970759d89 origin/claude/magical-wozniak-yfmmx2 -- proofs .github services scripts apps packages && echo "no code on the live branch after d3d7300"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md | grep -c -E '^#+ Exact-head review of Stages C2-C3 and C2-C4'   # must print 0
git diff --shortstat 27999c7bd9b79fd1a1c68136b3de62b14bd32a34 85b98444320326742e642e8f2d01f720cfb77f27 -- proofs .github services scripts apps packages   # expected: 3 files changed, 92 insertions(+), 23 deletions(-)
git diff --shortstat 85b98444320326742e642e8f2d01f720cfb77f27 d3d73002c454416f41ef7d787a139e8970759d89 -- proofs .github services scripts apps packages   # expected: 2 files changed, 204 insertions(+), 7 deletions(-)
git diff --shortstat origin/main...HEAD -- proofs .github services scripts apps packages   # expected: 26 files changed, 3191 insertions(+), 7 deletions(-)
```

If any check fails, stop and report. The prompt is stale if this prompt's commit is not on the live branch, if a non-Markdown path changed there after `d3d7300`, or if this review is already recorded (AM5-15).

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
- the P06.2 brief: "C2-C4's audit observation, and the combined re-review" (revision 20), "Codex's CX12, and C2-C4" (revision 19), "The re-review's F1, and C2-C3" (revision 18) and "Codex's CX9 and CX10, and C2-C2" (revision 17);
- the Dev Manager's reports, under `docs/continuity/dev-manager/reviews/`: DM-29 (`2026-10-25-dm-29-p06-2-c2-c4-observation.md`) and DM-28 (`2026-10-25-dm-28-p06-2-cx12.md`), whole, with their own audits (DM-28 section 3, DM-29 section 3); DM-27 (`2026-10-25-dm-27-p06-2-re-review-f1.md`); DM-24's 1.1 to 1.3, DM-25's 3.1 to 3.4 and DM-23's 2.1 to 2.3;
- C2's prompt, items 5, 7 and 8 (`docs/ephemeral/2026-10-24-p06-2-stage-c2-implementation-prompt.md`); C2-C3's and C2-C4's prompts (`docs/ephemeral/2026-10-25-p06-2-stage-c2-c3-correction-prompt.md`, `docs/ephemeral/2026-10-25-p06-2-stage-c2-c4-correction-prompt.md`);
- the evidence record: "Exact-head review of Stages C2-C1 and C2-C2", "Stage C2-C3", "Manager verification of Stage C2-C3", "Stage C2-C4" and "Manager verification of Stage C2-C4";
- **the code, whole at `HEAD`:**
  - `src/chat/store.ts`: the class comment, `select`, `closeConversation`, `noteSeen`, `readHead`, `mergeHead`, `loadOlder`, `readList`, `moveReadCursor`, the command's success and follow-up, `send`, `revoke` and `resetConversation`;
  - `src/chat/store.test.ts`: `:613` to the end, with `:193`, `:210`, the CX9 gate and its tests, and the CX10 tests;
  - `src/chat/testing.ts`; `src/chat/screen.tsx:152-172`;
  - read only, for the server: `services/api/glow_chat/reads.py`, `_select` (`:383-449`), `_move` and the newer-cursor refusal; and, for DM-29's trace, `services/api/glow_chat/delivery.py` where a submission and its event change state.

**The run's logs:** run 40206318661 on `d3d7300`. Read its Mobile job (`npm run check`'s counts, the rendered tests, the long-conversation test) and its gate, enough to confirm the claims above, and say what you read.

## 3. What to review

1. **F1 and CX11, under DM-27 1.1:** does a move get held back by the known position only while `lastRead` is among the loaded accepted messages? Read `from >= 0` at `moveReadCursor`, and say whether F1 and CX11 are closed.
2. **Every assignment to `accepted` and `lastRead`** (DM-27 1.4), at `d3d7300`: `mergeHead`'s newest and incremental branches, `loadOlder`, `revoke`, `resetConversation`, the command's success and its follow-up. Is there any path that leaves the position treated as known while `lastRead` is outside the window, or treated as unknown while it is inside?
3. **CX12, under DM-28 1.1 and 1.2:**
   - Does the replacement itself invalidate every older-page request outstanding then, including one asked after the `stale` answer and before the reload's page is merged?
   - Does an invalidated response, success or failure, change nothing and start nothing, with no older-page error and no DM-25 3.2 trigger?
   - Does a refusal that ends access still revoke, unless the conversation's epoch has moved on?
   - Does the per-window slot hold one request for the current window at a time, with no collision across windows or conversations, and is no invalidated request left holding `loading`?
   - Say whether CX12 is closed, and C2's items 5 and 7 met on its path.
4. **The `stale` path as a whole** (DM-28 2.2): for each request that can be outstanding when the window is replaced (a head read and one queued behind it, an older page, a cursor command, a send and a list read), and for each piece of window-bound state (`accepted`, `unsent`, both cursors, `hasOlder`, the older-page state, `lastRead`, `seen`, `visible`, `cursorRetry`), say how the code handles it at `d3d7300`. Check C2-C4's audit against your own trace; do not take it from the audit.
5. **DM-29 2.2's three items:**
   - the observation's path (an older-page error from before a replacement stays over the reload's window; `:245`, `screen.tsx:165-166`);
   - the manager's edge (a reload with no older cursor hides the button while the text stays), with the Dev Manager's trace that C1 has no path to it;
   - the class comment's sentence at `:65` ("the older-page state is `idle` once the replacement is merged").
   - Confirm or challenge each, and class any finding by DM-29 2.2.
6. **The rest of the rules hold:** DM-23 2.1 to 2.3 (target `seen`, forward only, one command per epoch, no command on a viewing report); DM-25 3.1's three grounds as DM-27 1.1 amends them, and 3.2's triggers for a merged page; the revocation rule (DM-24 1.1 to 1.3); CX10's tests and `:193`, `:210` passing unchanged.
7. **The tests:** do C2-C3's (a) to (c) and C2-C4's (a) to (f) each fail without their part of the fix? Reproduce, in a scratch copy:
   - C2-C3's S1 (`store.ts` at `27999c7`) and S2 (`from >= 0 ||` removed);
   - C2-C4's R1 (`store.ts` at `85b9844`), R2 (1.1's exception removed), R3 (the window advanced at the `stale` answer instead of at `:266`) and R7 (the window test removed from `:291` only).
   - Are `staleOnce` and `pages()` faithful stand-ins for C1's newer-cursor refusal and for a request held in flight?
8. **Scope and security:** only `store.ts`, `store.test.ts` and C2-C3's README sentence changed in code paths across both passes; `testing.ts`, the fixture adapter, the screens and every dependency file unchanged; the revocation path unchanged in effect; the client boundary, validators and display rule untouched; no new import, provider package, `fetch`, socket, `EventSource`, `console`, timer or background poll.
9. **The records:** the README's cursor sentence and its older-page step; the evidence record's four sections named above, with DM-29 1.3's annotations at "Stage C2-C4"'s two `idle` lines; the P11 plan's C2C1-X1 entry. Does any statement claim more than the code, the tests or the runs show?
10. **The offline checks,** run at `HEAD` in a clean environment:
    - **the mobile app first:** `npm ci --ignore-scripts`, `npm run check` (621 at the run of record), `EXPO_OFFLINE=1 npm run check:expo` and `EXPO_OFFLINE=1 npm run export:development`;
    - **then the contracts:** `npm ci --ignore-scripts`, `npm run generate` with no diff, and `npm run check` (586 corpus cases);
    - `npm run test:rendered` only if it can run without `playwright install`, marked "informational, not the pinned browser".

## 4. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<RECORDS_COMMIT>`), and the start gate's and the classification's results;
- the environment check;
- a verdict: **approve**, or **changes required**, with the findings that require them, and whether F1, CX10, CX11, CX12 and C2's items 5, 7 and 8 are met;
- every finding, numbered, with its severity (blocking, should fix, nit), its file and line, what is wrong, why it matters, a suggested fix, and whether it falls in one of the correction classes above;
- for each focus area, what you checked and what you found, with your verdict on each of DM-29 2.2's three items;
- the offline checks and reversals you ran, with their exact results;
- limits of the review, and open questions.

# DM-25 — the re-review order after DM-24, and Codex's CX10 on C2-C1's cursor rule

- **Consultation:** DM-25, revision 2, from App Manager 8, relayed by Nathan (OD-25). It was written for Dev Manager 2; Dev Manager 3 answers it (OD-47).
- **Reviewer:** Dev Manager 3, `session_01KVuPEpFRh9B22beZKTKb27`, branch `claude/dev-manager`.
- **Commit read:** `6fe07b10b987a1752a63065c65f8ae7f052eae1b`, as the consultation names it. **This read covers `6fe07b1` for items 1 to 3** (DM-03 G2).
  - The manager branch was at `6fe07b1` when I fetched it at 01:17 UTC. By 01:20 it was at `2ef4b1b74024b6c898c11021995bc782403a66be`, two commits later: `e0cc5cf` merges my start note, and `2ef4b1b` records Dev Manager 3 (OD-47), the generic Dev Manager start prompt and AM8-02.
  - Between `6fe07b1` and `2ef4b1b`, no non-Markdown file changed. Nor did anything DM-25 asks me to read: the brief, the evidence record, `docs/ephemeral/`, the P11 plan, the DM-24 report and the code (checked with `git diff --name-only` and `git diff --quiet`).
  - Item 4 below (not asked) and the Notion check read `2ef4b1b`.
- **Environment (names only):** none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, `STREAM_APP_ID`, `STREAM_API_KEY` or `STREAM_API_SECRET` is present. The consultation's line saying my container holds the three `STREAM_*` variables is true of Dev Manager 2's container, not this one.
- **What I did not do:**
  - I called no provider, database, HDE or Railway.
  - I ran no repository code. The findings rest on reading the code, not on a run.

## 1. What I read

**At `6fe07b1`:**

- **DM-24's report** (`1a4fc1b`): section 4, and its items 1 and 3 as accepted.
- **DM-24 revision 2:** item 2, with the whole diff from `568f446`.
- **The review log's DM-24 disposition,** and the mistakes log's AM7-13 and AM8-01.
- **The evidence record:** "Codex's CX10 on C2-C1's cursor code", "Codex's code review of C2-C1's head", "Stage C2-C1" and "Manager verification of Stage C2-C1".
- **DM-23's report,** 2.1 to 2.6.
- **C2's prompt, item 8:** "the app moves the member's own cursor forward with `ReadCursorIntent` when the member has seen newer messages, and never backward."
- **The code, `apps/mobile/src/chat/`** (identical to `311b07e`, by `git diff --quiet`):
  - **`store.ts`, whole:**
    - `viewed`, `indexOf`, `noteSeen` (`:138`), `resetConversation` (`:175`, where `lastRead` starts `null`), `loadOlder` (`:258`), `moveReadCursor` (`:280`, with the list update at `:292-293`) and `revoke` (`:300`);
    - the reads, the sends, and the foreground and authority hooks.
  - **`screen.tsx`:** `useViewedMessages` and `ConversationScreen`.
  - **`fixture-adapter.ts`:** `summary` (`:195`, unread at `:199`), `page`, `moveCursor` (`:298`, forward only at `:308`), and the development helpers.
  - **`testing.ts`.**
  - **`store.test.ts`:** the cursor tests `:161`, `:173`, `:193`, `:210` and `:226`.
  - **`apps/mobile/src/interactions/screen.tsx`:** the match's "Open conversation" (`:75`), which selects the conversation and opens it with no list read.
- **The server's read-cursor command:** C1's `services/api/glow_chat/reads.py`, `_move` (`:632`). It moves the cursor only forward (`:662`), so a move to a message at or behind the cursor changes nothing.
- **PR33's review threads,** read-only through the GitHub API. CX8, CX9 and CX10 are open, and CX10 has no reply yet. At 01:20 UTC, Codex's review of `2ef4b1b` was running.

**At `2ef4b1b` (item 4):**

- the register's OD-46 and OD-47 rows and its header;
- the next-manager start procedure's owner line;
- the Dev Manager start prompt, whole;
- the handoff's and the review log's diffs from `6fe07b1`;
- AM8-02.

**Notion, read-only, 01:19 UTC:**

- *Implementation Control*;
- *Dev Manager — reviews and approvals*;
- *Owner-direction register (copy of the repository)*;
- the Work Register row P06.2.

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1 The order | **Approved with conditions 1.1 to 1.3:** one exact-head re-review after C2-C2, reading each pass against its own conditions and the store as it stands at that head, with its security focus named |
| 2 DM-24 2.1's terms for that re-review | **Approved with conditions 2.1 to 2.3:** the terms carried over, with the cursor rule as item 3 sets it, and C2-C3's own re-review and Codex before the merge |
| 3 CX10: fix or carry | **(b): fix it in C2-C2,** as a separate item beside CX9, with conditions 3.1 to 3.7, which replace the manager's c.1 to c.6. The manager's c.1 does not fix CX10 when the store holds no summary of the conversation, and its c.2 makes a viewing report a trigger, which would resend a failed command on each report |
| 4 PR33's governing Markdown at `2ef4b1b` (not asked) | **OD-46's row approved with 4.1** (it says Nathan carried DM-24's revision 2; he carried revision 1). **OD-47's row approved with 4.2.** **The start procedures approved with 4.3** |
| 5 Notion | **No mismatch.** My start note's two items are fixed |

- **What needs no further read:**
  - the brief's revision 17 and C2-C2's prompt, if they quote DM-24 1.1 to 1.6 and 3.1 to 3.6 here as written (DM-24 item 3; DM-22 9.1's terms);
  - the records that apply 4.1 to 4.3 as written.
- **What goes to Nathan:** no item.

## 3. Item 1 — the order: approved, with conditions

**One exact-head re-review after C2-C2 is right.**

- It follows AM7-13's lesson: a review of a head that is about to change certifies nothing.
- It now matters more than when the manager proposed it. Item 3's fix changes C2-C1's own cursor code, so a review of C2-C1 alone would have read code that C2-C2 rewrites.
- The order is linear (OD-29): revision 17, C2-C2's prompt, its run, Codex on its head, then the one re-review.

**Conditions:**

- **1.1 What the re-review reads.**
  - **Its head:** the code commit that holds C2-C2's code, named as workflow step 6 says.
  - **C2-C1's diff** against DM-23 2.1 to 2.6.
  - **C2-C2's diff** against DM-24 1.1 to 1.6 and 3.1 to 3.6 here.
  - **The store's cursor path and revocation path as they stand at that head,** because C2-C2 changes code C2-C1 wrote. DM-23 2.6's reading list (the cursor path, the replaced unit test, the long-conversation rendered test) is read at that head.
  - **The run of record of C2-C2's code commit:** all eight jobs, and the rendered tests.
  - **Its security focus areas, named in its prompt.** It is the only security reading of both passes (OD-41; workflow step 7):
    - no history or composer after a revocation (OD-12; CX9);
    - the display rule at the client boundary unchanged;
    - no provider package, socket or network client added.
- **1.2 What "handled" means before the re-review prompt goes to Nathan.**
  - Codex has reported on a head that holds C2-C2's code, and each finding is verified and dispositioned.
  - A finding fixed before the re-review goes into a further pass under item 2's terms, so that the one re-review still reads one final head.
  - A fix-or-carry choice that no correction class decides comes to me first (OD-32; AM7-12).
- **1.3 The close, completed.** Besides what the manager lists (Codex on the final head, the final run, the pre-merge checklist and the merge):
  - the **CX10** thread is answered now and resolved with CX8's and CX9's once the fix is reviewed;
  - **PR33's governing Markdown** has the Dev Manager's dispositions in the review log (item 4);
  - **PR33's description** is brought up to date, as the handoff already says.

**C2-C2's prompt** goes to Nathan without a further read on DM-24 item 3's terms (DM-22 9.1). It must also quote 3.1 to 3.6 here as written.

## 4. Item 2 — DM-24 2.1's terms for the one re-review: approved, with conditions

- **2.1 The terms.**
  - **Which findings they cover:** a finding of the re-review in a correction class its prompt names, or a defect that misses an item of C2's prompt (DM-23's rule).
  - **The conditions:** such a finding becomes a further pass, C2-C3, without a read of mine only if:
    - it stays within `apps/mobile`, with no dependency or contract change (DM-23 2.5's unchanged list);
    - it departs from nothing DM-22, DM-23, DM-24 or this report approved;
    - it leaves two rules unchanged:
      - the cursor rule, as DM-23 2.1 to 2.3 and 3.1 to 3.3 here set it;
      - the revocation rule, as DM-24 1.1 to 1.3 set it.
  - **Anything else** comes to me before the prompt goes to Nathan.
- **2.2 C2-C3's own checks.**
  - **Before the merge:** C2-C3 gets its own exact-head re-review, of its delta and naming the finding it fixes, and then Codex's review of its head. Every new head needs its own review.
  - **Nits:** a nit that misses no item of the prompts and is in no correction class is a recorded follow-up, not C2-C3.
- **2.3 The same terms cover a Codex finding on C2-C2's head** that is fixed before the re-review (1.2).

## 5. Item 3 — CX10: fix it in C2-C2, with conditions 3.1 to 3.7

**The defect is real; the manager's verification holds in the code.**

- At open, `resetConversation` sets `lastRead` to `null` (`store.ts:177`), and no contract carries the cursor's position (C2C1-X1).
- `moveReadCursor` then tests only `accepted.slice(from + 1, to + 1)`, with `from = -1`, for a message from the other member (`:283-284`).
- With one incoming message followed by 20 of the member's own, the newest page holds no incoming message. So viewing the newest sends nothing, and the fixture's count (`:199`) stays at 1.
- After an older page is prepended, viewing the incoming message gives an index below `seen`'s. `noteSeen` returns at `:142`, and nothing reconsiders the move.

**Two corrections to the manager's framing.** Neither changes the verdict.

- **"Never clears" overstates the effect.** The count stays above zero until the member views a later message from the other member. That move passes an incoming message in the window, and the server's cursor then moves past the old one too.
- **"Any member who sends 20 messages in a row after an unread one" overstates the reach** through this app.
  - The composer sits below the messages in the same scroll area, so sending usually brings the incoming message into view, and C2-C1 then moves the cursor.
  - It takes a missed view: a row that passes the visible area between two scroll reports, or a cursor command that failed and was not retried before the store reset. Later, another client could also cause it.
  - A unit test still shows the defect offline.

**Why (b), by DM-23's rule** (a defect in a stage's own code that misses an item of that stage's prompt is fixed before the stage merges):

- **It misses C2's item 8 in its own words.** The cursor moves forward "when the member has seen newer messages". Here the member has seen messages newer than the server's cursor, and the cursor does not move.
- **It is C2-C1's code, and a unit test shows it offline.** It needs nothing from P11's environment, so the CX4 to CX7 precedent does not apply.
- **It is not a safety or privacy defect.** It is a wrong count in the member's own list, and no other member sees anything (no read receipts). Like CX8, it is a correctness defect in the stage's own interface.
- **The cost is small.** C2-C2 already changes the same store, and the same re-review reads it.
- **(a)'s argument for carrying is true, and is not a reason to wait.** The store cannot know the cursor today (C2C1-X1), but it can stop acting as if it knew, which 3.1 does. Carrying would wait on a contract change that may never be made.

**Where the manager's conditions fall short:**

- **c.1 depends on a summary the store may not hold.**
  - The match's "Open conversation" (`interactions/screen.tsx:75`) selects the conversation and opens it with no list read. If the list was never read in that session, `state.list.conversations` is empty, and c.1 has nothing to test. CX10 then stays on that path.
  - A summary the store does hold may be out of date, since the list is not read while the conversation is shown.
  - c.1's restriction to viewing the newest message is not needed. DM-23 2.1 already makes the newest viewed message the target.
- **c.2's "`noteSeen()` no longer drops it silently" makes a viewing report a trigger.**
  - After a failed command, every report would then send it again. That breaks the retry rule that `store.test.ts:210` holds: a failed command is tried again after the next read, not on each report.
  - It also cuts across DM-23 2.3 ("never on each scroll event").
  - The trigger should be a change in the evidence, not a report.
- **c.4's last test** ("no unread incoming message sends no command") cannot hold when no summary is held. The store cannot know there is nothing unread.
- **c.5** leaves DM-24 1.5's "C2-C1's cursor behaviour and its tests stay unchanged" in force. That sentence contradicts this fix if C2-C2's prompt quotes 1.5 as written.

**The Dev Manager's share.** DM-23 2.3 is the condition this defect applies. Dev Manager 2 wrote it without considering that the store does not know the server's cursor when a conversation opens. The C2-C1 session saw the harmless side of that gap (C2C1-X1: a first command may be a no-op). No one saw the side that suppresses a move: not DM-23, not the session, not the manager's verification. Codex did.

**The conditions, which replace c.1 to c.6.** C2-C2's prompt quotes them as written.

- **3.1 An unknown position is not treated as known** (replaces c.1).
  - **Why:** until a cursor command has succeeded in this opening, the store does not know where the server's cursor is (C2C1-X1). So the loaded window alone cannot show that a move to `seen` passes no unread message from the other member.
  - **Until a command has succeeded,** a move to `seen` is sent when any of these holds:
    - the loaded messages up to `seen` include one from the other member (DM-23 2.3, as today);
    - the conversation's summary that the store holds shows an `unread_count` above zero. The summary is the conversation's entry in the store's list, as the last list read or cursor command returned it;
    - the store holds no summary for the conversation, as when it was opened from the match's "Open conversation" with the list never read.
  - **Once a command has succeeded,** DM-23 2.3 holds as written.
  - **The target is always `seen`** (DM-23 2.1).
  - **Why this is safe:** the server moves the cursor only forward (C1's `_move`), so a move to a message at or behind its cursor changes nothing.
  - **A summary at 0 never suppresses a move** that the window's own evidence calls for.
- **3.2 A move the store held back is reconsidered when its evidence changes** (replaces c.2).
  - **The two triggers:**
    - an older page that adds messages before `seen`;
    - a list read, or a cursor command's response, that changes the conversation's summary.
  - Each reconsideration applies 3.1 and DM-23 2.3, and sends nothing when they do not hold.
  - **What does not trigger one:**
    - a viewing report (DM-23 2.3);
    - a failed command, which is still tried again only after the next successful read (`store.test.ts:210`'s rule);
    - a response that DM-24 1.1 makes ineffective, because it was requested before a revocation.
- **3.3 The existing rules hold** (c.3).
  - Never backward, and never to an unsent message.
  - At most one command in flight.
  - The target is `seen`, the newest accepted message that has been in view while the conversation was shown and the app was in the foreground (DM-23 2.1).
  - No command on each viewing report.
- **3.4 Tests** (replaces c.4). Each has its reversal in a scratch copy outside the checkout, showing that the test fails without the fix.
  - **(a) The incoming message outside the window, with the list read first.** One incoming message, then 20 of the member's own; the incoming one is unread and outside the newest page, and the list's count is 1. Viewing the newest sends one command, to it, and the list's count clears.
  - **(b) The same, with no list read.** The conversation is opened with no summary held: one command, and a list read afterwards shows 0.
  - **(c) A summary that is out of date.** The summary held shows 0, from a list read before the incoming message and the 20 own arrived.
    - Viewing the newest sends nothing.
    - Loading the older page then sends one command, to `seen`, and the count clears.
    - In a separate case, a list read that shows the count above zero does the same.
  - **(d) Nothing unread.** The summary held shows 0, and the window holds no incoming message: no command, however often the messages are reported.
  - **(e) The existing rules, unchanged:**
    - once a command has succeeded, the member's own messages in view send nothing (`store.test.ts:193`);
    - a failed command is still tried again only after the next read (`:210`).
  - **The reversals:**
    - 3.1 reverted to the window-only test fails (a) and (b);
    - 3.2's older-page trigger removed fails (c)'s first case, and its summary trigger removed fails the second;
    - a reconsideration on every report fails (d) or `:210`.
- **3.5 Scope** (replaces c.5).
  - **The paths and the unchanged list:** DM-24 1.5's, with no change to the fixture adapter. A test can send the member's own messages through the transport.
  - **DM-24 1.5's sentence on C2-C1's cursor behaviour** reads, for C2-C2: "C2-C1's cursor behaviour and its tests stay unchanged, apart from the revocation path's effect on them and DM-25 3.1 to 3.3".
  - **C2-C1's cursor tests** change only where 3.1 to 3.3 change the rule. The record names each change.
  - **The README's cursor sentence** states 3.1.
  - **No contract change:** the cursor position stays out of the contracts (C2C1-X1, for P11).
- **3.6 The re-review** (replaces c.6). The re-review of item 1 also:
  - names CX10 and C2's item 8 for this change;
  - reads 3.1's three grounds and 3.2's triggers;
  - checks that no path sends a command on a viewing report or to any target but `seen`;
  - checks that a response DM-24 1.1 makes ineffective triggers no reconsideration;
  - weighs one effect: a move reconsidered by a list read can be sent after the screen is left. C2-C1 already allows that for a `seen` set while shown and in the foreground ("a move to a message that was in view may now complete after the screen is left", the evidence record's "Stage C2-C1").
- **3.7 The records** (new; the manager's).
  - **The P11 plan's C2C1-X1 entry** adds:
    - the client now sends one move while it does not know the position, and relies on the server's forward-only rule (C1's read-cursor command);
    - P11 keeps that rule as a requirement, or adds the position to the conversation's contract, and the store then uses the position in place of 3.1's fallback.
  - **The evidence record's CX10 section and the Work Register row** state the outcome exactly: the count stays above zero until the member views a later message from the other member. They also state the narrower reach above.

## 6. Item 4 — PR33's governing Markdown at `2ef4b1b` (not asked)

**Why I read it now.**

- The handoff plans to send OD-46's and OD-47's rows with the pre-merge consultation (its "Before PR33 merges", after my start note).
- I read them now because one finding (4.1) is better fixed in the next records batch.
- With 4.1 to 4.3 applied as written, the pre-merge consultation only confirms them, plus anything governing that lands after `2ef4b1b`.

**What PR33 carries on governing paths since `main` (`a8e9528`):**

- the register's OD-46 row (`ba5812d`, corrected at `dda3110`);
- the register's OD-47 row (`2ef4b1b`);
- the next-manager start procedure's owner line;
- the Dev Manager start prompt, made generic.

**OD-46's row: approved with 4.1.**

- **The quote:** both quotes are as the handoff and AM7-13/AM7-14 carry them. Nathan's words were given in App Manager 7's session, so I can check them only against the records.
- **The State** is right on the withdrawal, and on App Manager 7 creating App Manager 8 with the manager branch as its outcome branch.
- **It is wrong on one fact.** It says "Nathan carries DM-24 to Dev Manager 2 (revision 2, which states the withdrawal)". Nathan carried revision 1, before revision 2 was written. DM-24's report reads revision 1 at `568f446`, and the review log's DM-24 row carries App Manager 8's note saying so.
- **4.1** That parenthesis is replaced with: "Nathan carried DM-24 to Dev Manager 2: revision 1, written before the withdrawal was recorded; revision 2 states it, and DM-25 replaces revision 2 for the one item the withdrawal changed". The rest of the cell stays. The Notion copy follows.

**OD-47's row: approved with 4.2.**

- Its quote is the handover's, word for word. Its State is accurate: the OD-35 pattern, this session's ID and environment, and Dev Manager 2 pushing nothing after `35e484e`.
- **4.2** The register's header bullet "Answers given in the Dev Manager's session … (OD-16 to OD-27, OD-35 and OD-36)" adds OD-47. Its quote comes from Dev Manager 2's record in `reviews/`, as OD-35's came from Dev Manager 1's.

**The start procedures: approved with 4.3.**

- **The next-manager owner line** is accurate (OD-46).
- **The generic Dev Manager start prompt** applies DM-03 E3, and its text matches what this session received. It is not governing Markdown under the charter. I read it because it starts this role's sessions.
- **4.3** Its start gate uses `<HANDOVER_SHA>`, which the replacement list does not define. The list defines `<HANDOVER>` as the file and its full SHA. Either the list names `<HANDOVER_SHA>`, or the gate takes `<HANDOVER>`'s SHA.

## 7. Notion: no mismatch

- ***Implementation Control*** (fetched 01:19 UTC):
  - "Current status — 25 October 2026 (App Manager 8; …; DM-25 revision 2, on the re-review order and CX10, with Nathan to carry to Dev Manager 3)", last matched to `2ef4b1b`;
  - it agrees with the repository on OD-47, the generic start prompt and AM8-02;
  - "Standing directions" now says OD-01 to OD-47, the first of my start note's two items.
- ***Dev Manager — reviews and approvals*:**
  - it has Dev Manager 3's row;
  - DM-24's row names the merge `f87f3b5` (AM8-02), the second item;
  - DM-25's row reads "Pending", "written for Dev Manager 2, answered by Dev Manager 3", as the review log does.
- **The register copy:** matched at `2ef4b1b`, OD-01 to OD-47. Its OD-46 row is the repository's, so 4.1 applies to both. Its header carries the same list as 4.2's.
- **The Work Register's P06.2 row:** "In progress". It agrees with the handoff: DM-25 revision 2 at `6fe07b1`, then revision 17, C2-C2, one combined re-review after Codex, Codex on the final head and the merge.
  - Its "never clears" is the repository's own wording (the review log's DM-25 row), so it is not a mismatch. 3.7 corrects both.

## 8. Where each condition goes

- **The brief, revision 17:**
  - C2-C2's definition: DM-24 1.1 to 1.6, with 1.5's sentence as 3.5 reads it;
  - CX10 as a separate item, with 3.1 to 3.6;
  - DM-23 2.3 recorded as amended by 3.1 when the position is unknown;
  - the order (1.1 to 1.3) and the terms for a further pass (2.1 to 2.3).
- **C2-C2's prompt:** DM-24 1.1 to 1.6 and 3.1 to 3.6, quoted as written. It goes to Nathan without a further read.
- **The re-review prompt:** 1.1 and 3.6, with DM-23 2.6 and DM-24 1.6.
- **The evidence record's "Codex's CX10 on C2-C1's cursor code":** the disposition, (b) in C2-C2, and 3.7's wording.
- **Codex's CX10 thread:** answered now, "fixed before PR33 merges, in C2-C2"; resolved once the fix is reviewed (1.3).
- **The P11 plan's C2C1-X1 entry:** 3.7.
- **The register:** 4.1 and 4.2, then the Notion copy.
- **The Dev Manager start prompt:** 4.3.
- **The handoff's "Before PR33 merges":** the read of OD-46 and OD-47 is this item 4. What remains is confirming 4.1 to 4.3 as applied, plus anything governing after `2ef4b1b`.
- **The review log and Notion's DM-25 row:** 3.7's correction of "never clears".

Status: complete

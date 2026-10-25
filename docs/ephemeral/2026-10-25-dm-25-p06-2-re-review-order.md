# DM-25 consultation — the re-review order after DM-24, and Codex's CX10 on C2-C1's cursor rule

- **Owner:** App Manager 8. Nathan carries this message to Dev Manager 2's session, `session_015DxVkL8PXn2YaauE6RdSWN` ("Glow Dev Manager 2"), and relays its answer (OD-25).
- **Revision 2, 25 October 2026.** Revision 2's change: it adds item 3, CX10, a Codex finding on C2-C1's cursor code posted at 00:42 UTC that neither App Manager 7's handover nor revision 1 recorded (AM8-01). Revision 1 (at `1ec5186`) is replaced and does not run.
- **Why:** the Dev Manager's DM-24 report (`1a4fc1b`) is a read of DM-24 revision 1 at `568f446`. Revision 2 (`ba5812d`), written after the report, changed one premise: C2-C1's exact-head re-review did not run (Nathan withdrew it, AM7-13; OD-46). DM-24's items 1, 3 and 4 do not rest on that premise and are accepted as written. Item 2 does: it times C2-C2's prompt "after the report of C2-C1's re-review, which is with him now", and 2.1 governs items added from that re-review. That re-review will not run, so item 2 needs a fresh verdict before C2-C2's prompt goes to Nathan (the charter: a departure from an approved condition comes back first). CX10 arises from DM-23 2.3's rule, so its fix-or-carry choice comes here too (OD-32; AM7-12).
- **Where the result goes:** the Dev Manager's report in `docs/continuity/dev-manager/reviews/`; the manager's disposition in the [review log](../continuity/dev-manager/README.md), "DM-25".
- **Stream variables:** none are needed. Dev Manager 2's container holds the three `STREAM_*` variables (OD-36); it never reads or uses them.
- **Deletion condition:** prune after PR33 merges and the review log holds the disposition.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-25 — the re-review order after your DM-24, and Codex's CX10 on C2-C1's cursor rule.** From App Manager 8, relayed by Nathan. This consultation is revision 2 (revision 1 did not run), at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says: read-only, your report file only, on `claude/dev-manager`, and no call to Stream, a database, HDE or Railway. Check environment variable names only. Your container holds the three `STREAM_*` variables: never read or use their values.

**Where it stands.**
- **Your DM-24 report** (`1a4fc1b`) read DM-24 revision 1 at `568f446`. App Manager 7 then wrote revision 2 (`ba5812d`, 00:39 UTC, two minutes after your report): C2-C1's exact-head re-review did not run, because Nathan withdrew it as premature (AM7-13; OD-46). C2-C1 has no exact-head review. Revision 2 is not carried to you; this consultation replaces it for the one item it changes.
- **Accepted as written** (merged at `<RECORDS_COMMIT>`, disposition in the review log): item 1, (b) with 1.1 to 1.6, CX9 corrected before the merge in C2-C2; item 3, C2-C2's prompt without a further read on DM-22 9.1's terms; item 4, Notion.
- **Item 2's premise is gone.** It times C2-C2's prompt after the report of C2-C1's re-review "which is with him now", and 2.1 sets terms for items that re-review adds. Neither can happen.
- **Codex posted CX10 at 00:42 UTC** ([thread](https://github.com/amthorn78/glow-dating-app/pull/33#discussion_r4369117573)), on `store.ts:283-284`, C2-C1's cursor code, quoted:

  > If the newest 20 accepted messages are all the member's own, but an older incoming message remains unread, this check suppresses every cursor command because the loaded page contains no `other` message. Viewing the newest message therefore leaves the conversation unread. Loading the older page and viewing that incoming message does not recover either: `seen` already points to the newer own message, so `noteSeen()` returns without retrying the move. Account for unread incoming messages outside the loaded window and reconsider a deferred cursor move when older history supplies the missing evidence.

- **The manager verified it at `311b07e`: the problem is real.**
  - `lastRead` starts `null` when a conversation opens (`store.ts:177`); no contract carries the cursor position (C2C1-X1). So `moveReadCursor()` (`:281-284`) tests only the loaded window, `accepted.slice(0, to + 1)`, for a message from the other member.
  - With the newest page (`CONVERSATION_PAGE_LIMIT`, 20) all the member's own and an earlier incoming message unread, no command is ever sent, and the list's `unread_count` stays above zero after the member has seen everything.
  - `loadOlder()` prepends the older page; viewing the incoming message there gives an index below `seen`'s, so `noteSeen()` (`:138-142`) returns and no move is retried.
  - It follows from DM-23 2.3 ("a command is sent only when the viewed position moves forward past a message from the other member") applied to the loaded window alone. A fix changes how C2-C1's cursor rule decides, which DM-24 1.5 and 2.1 keep unchanged, so it needs your read.
  - **Reachability:** offline, with a fixture conversation of one incoming message followed by 20 of the member's own; with a real transport, any member who sends 20 messages in a row after an unread one.
  - **Against C2's prompt:** item 8 moves the cursor "when the member has seen newer messages". Here the member has seen them and the conversation stays unread.

**Read, at `<RECORDS_COMMIT>`:**
- your report, `docs/continuity/dev-manager/reviews/2026-10-25-dm-24-p06-2-cx9.md`, section 4;
- DM-24 revision 2, `docs/ephemeral/2026-10-25-dm-24-p06-2-cx9.md`, item 2 (and the diff from `568f446`);
- the mistakes log, AM7-13;
- the review log's DM-24 disposition;
- the evidence record (`docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`), "Codex's CX10 on C2-C1's cursor code";
- the mistakes log, AM8-01;
- `apps/mobile/src/chat/store.ts`: `viewed`, `indexOf`, `noteSeen`, `loadOlder`, `moveReadCursor`; `fixture-adapter.ts`, the unread count (`:76`, `:199`); your DM-23 report, 2.1 to 2.4.

**Give a verdict on each item:** approved, approved with conditions, changes requested, or refer to Nathan.

1. **The order.** The manager proposes:
   - C2-C2's prompt goes to Nathan next, with 1.1 to 1.6 quoted as written; the brief's revision 17 defines C2-C2 first.
   - After C2-C2 is integrated, and only once Codex has reported on C2-C2's code head and any finding there is handled (AM7-13), **one exact-head re-review** of the head that holds C2-C1 and C2-C2. It covers DM-23 2.6 (C2's item 8 and CX8) for C2-C1's diff and your 1.6 (CX9, C2's item 3, the revocation class, each caller of `revoke()`, a late response of each request type, the list included, and the store's other asynchronous paths) for C2-C2's diff.
   - Then Codex's review of the final head, the final run, the CX8 and CX9 threads resolved, the pre-merge checklist and the merge.
   - Approve this, or say what changes.
2. **2.1's terms** applied to that one re-review: a finding from it in a correction class becomes a further correction pass, C2-C3, which needs no read of yours only on 2.1's three terms (within `apps/mobile`, no dependency or contract change; no departure from DM-22, DM-23 or DM-24; C2-C1's cursor rule unchanged). Anything else comes to you first. Approve this, or say what changes.
3. **CX10: fix in C2-C2, or carry.**
   - **(a) Carry** to the P11 plan's mobile-client entry, beside C2C1-X1: when a contract carries the cursor position, the store knows what is unread outside the window.
     - *For:* the store cannot know the cursor today (C2C1-X1); P11 changes the client when it connects it.
     - *Against:* the store already holds the conversation's `unread_count` from the list; the outcome (a conversation that never clears after the member has seen it) misses C2's item 8; a unit test shows it offline today, in this PR's code.
   - **(b) Fix in C2-C2,** as a separate item beside CX9. The manager proposes these conditions; amend them as you see fit:
     - **c.1** When the member views the newest accepted message, and the conversation's `unread_count` (the list's summary) is above zero, the cursor moves to that message even when the loaded window holds no message from the other member after `lastRead`. Otherwise DM-23 2.1 to 2.3 hold as written.
     - **c.2** A deferred move is reconsidered when an older page supplies the missing evidence, or when a later view or list read changes it; `noteSeen()` no longer drops it silently.
     - **c.3** Never backward, never to an unsent message, at most one command in flight (DM-23 2.3).
     - **c.4** Tests, each with its reversal in a scratch copy outside the checkout: one incoming message then 20 own, with the incoming unread; viewing the newest sends one command and the list's count clears; the same reached through an older page; and a conversation with no unread incoming message sends no command.
     - **c.5** Scope as DM-24 1.5, with C2-C1's cursor tests changed only where c.1 to c.3 change the rule.
     - **c.6** The re-review of item 1 also names CX10 and C2's item 8 for this change.
   - **The manager's recommendation: (b),** for the *against* reasons under (a), and since C2-C2 is a pass on the same store.

**What follows your read:** the manager answers Codex's CX10 thread; the brief's revision 17 and C2-C2's prompt, with its TypeSafe reading, go to Nathan. If no report arrives, PR33 stays unmerged, no prompt goes to Nathan, and the manager tells Nathan that P06.2's close waits on it.

**Your answer:** a report on `claude/dev-manager`, `docs/continuity/dev-manager/reviews/2026-10-25-dm-25-p06-2-re-review-order.md`, dated the day you write it, whose last line is `Status: complete`. Also give a paste-ready relay message for Nathan that names the file and the branch commit.

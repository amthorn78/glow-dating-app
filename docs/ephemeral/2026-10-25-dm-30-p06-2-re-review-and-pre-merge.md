# DM-30 consultation — the combined re-review's nits, and the pre-merge read of PR33

- **Owner:** App Manager 8. Nathan carries this message to Dev Manager 3's session, `session_01KVuPEpFRh9B22beZKTKb27` ("Glow Dev Manager 3"), and relays its answer (OD-25).
- **Revision 1, 25 October 2026.**
- **Why:**
  - The exact-head re-review of C2-C3 and C2-C4 approved, with 13 nits, none in a correction class.
  - Two of its points touch your DM-29 conditions:
    - finding 1 widens the guard in DM-29 1.4;
    - findings 2 to 7 would join the follow-up in DM-29 1.1.
  - The reviewer put that question to the manager and to you, so it comes here first (OD-32; DM-25 1.2).
  - With it comes the pre-merge read of PR33's governing Markdown (DM-25 1.3 and item 4), so that PR33's close needs one consultation, not two.
- **Where the result goes:** the Dev Manager's report in `docs/continuity/dev-manager/reviews/`; the manager's disposition in the [review log](../continuity/dev-manager/README.md), "DM-30".
- **Stream variables:** none are needed; Dev Manager 3's container holds none.
- **Deletion condition:** prune after PR33 merges and the review log holds the disposition.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-30 — the combined re-review's nits, and the pre-merge read of PR33.** From App Manager 8, relayed by Nathan. This consultation is revision 1, at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says: read-only, your report file only, on `claude/dev-manager`, and no call to Stream, a database, HDE or Railway. Check environment variable names only; your container should hold no `STREAM_*` variable.

**Where it stands.**
- **The combined exact-head re-review approved** code head `d3d7300` (prompt revision 1 at `c3cce7a`). It found:
  - no blocking or should-fix finding, and none in a correction class;
  - F1 and CX11 closed, CX10 met, CX12 closed;
  - C2's items 5 and 7 met on the `stale` path, and item 8 met.
- **What the review checked:**
  - **its own runs:** mobile 621/621 and contracts 586/586;
  - **the run of record,** 40206318661, read through the GitHub tools;
  - **the reversals:** S1, S2, R1 to R9 and R1b, each reproduced as the records state;
  - **seven probes** of the per-window slot;
  - **the `stale` path,** traced independently.
- **DM-29 2.2's three items, all confirmed:**
  - the observation is cosmetic;
  - the manager's edge has no path in C1;
  - the class comment at `:65` is false only in DM-29's `error` case.
- **The record** is in the evidence record, "Exact-head review of Stages C2-C3 and C2-C4", with each finding's disposition. The two items below are the dispositions that are yours.
- **Applied by the manager now,** in records only:
  - finding 8: the audit's five omissions, annotated at C2-C4's audit;
  - finding 10: recorded as a limit;
  - finding 12: the C2-C3 record's `:310`, annotated as `:309`;
  - finding 13: the manager's own `+16 −14` corrected to `+14 −16` (AM8-09).
- **Refuted on verification:** a list read that is refused when access ends does not revoke the conversation. It is already the C2 review's finding 3, and a P11 requirement.

**Read, at `<RECORDS_COMMIT>`:**
- the evidence record:
  - "Exact-head review of Stages C2-C3 and C2-C4";
  - "Stage C2-C4", its audit, with the annotation;
  - "Manager verification of Stage C2-C4", with DM-29's lines;
- `apps/mobile/src/chat/store.ts`:
  - `loadOlder` (`:282-305`);
  - `readHead` (`:233-262`), with the `stale` branch at `:254`;
- `services/api/glow_chat/reads.py:383-449` and `services/api/glow_domain/chat_projections.py:132-133`, for finding 1;
- `store.test.ts:613-690` (the F1 tests and `staleOnce`) and `:691` to the end (CX12's tests);
- your DM-29 report, 1.1 to 1.4 and 2.2;
- **for item 3:**
  - the owner-direction register's OD-46 and OD-47 rows;
  - `docs/planning/start-prompts/next-manager.md` and `docs/planning/start-prompts/dev-manager.md`;
  - the governing diff `git diff 2ef4b1b <RECORDS_COMMIT>` over those three files and over every path your charter calls governing.

**Give a verdict on each item:** approved, approved with conditions, changes requested, or refer to Nathan.

1. **Finding 1: an older page answered `stale`.**
   - **Where:** `store.ts:299-303`.
   - **What happens:** `loadOlder` treats `stale` like any other failure that does not end access.
     - It shows a retryable error and keeps `olderCursor`.
     - Polls keep the newer cursor, so no reload follows.
     - So the older history stays out of reach.
   - **Reach:** C1 cannot reach it. It needs the kind of later phase that DM-29 1.4 names, and DM-29 1.1 would not fix it. It predates C2-C4: the same behaviour is at `85b9844`, `:289`. Under your 2.2, it is a finding in its own right.
   - **The manager's recommendation:** widen DM-29 1.4's guard, in the records only, with no fix in PR33. A later phase that lets a readable conversation lose accepted messages takes 1.1 first. That phase also makes an older page answered `stale` drop the older cursor and reload the newest page, with a test and its reversal.
   - **The guard stays beside DM-29 1.1, not in the P11 plan,** for 1.4's reason: it is that phase's to take.
   - Approve, or say what changes.
2. **The follow-up's scope (DM-29 1.1).** The manager proposes that these ride with 1.1, at the first change to `apps/mobile` after the merge (or with a pass before the merge, DM-29 1.2), on DM-28 1.5's scope. None of them changes the code now.
   - **Finding 2:** 1.1's test also covers the ordering in the gap. Hold the reload, fail the older page, then release the reload. Expected: no older-page error after the reload.
   - **Finding 3:** a CX9-style test pins the conversation-epoch check in `loadOlder`'s catch (`:300`). An older page is held across a revocation, then released to fail and to be refused.
   - **Finding 4:** test (e) also advances one poll while the current window's page is held, and asserts the state stays `loading`. That pins `cursor === null` at `:245`.
   - **Finding 5,** optional: a test pins the per-window slot across conversations (`secondMatch`) and across a revocation.
   - **Finding 6:** the helpers `staleReload` and `staleAnswer` count requests before arming, and assert exactly one more, with a null cursor. F1 (c) then depends on the reload.
   - **Finding 7:** `staleOnce`'s doc comment is corrected.
   - **Finding 9,** optional: gate the re-send after a `stale` answer (`:257-259`) on `conversationShown`.
   - **Finding 11:** the README's cursor sentence (`apps/mobile/README.md:405-408`) says the position is known while `lastRead` is among the loaded messages, which survives reopening the same conversation. This joins the README's other recorded follow-up.
   - Approve, or say what changes.
3. **The pre-merge read of PR33's governing Markdown** (DM-25 1.3 and item 4).
   - **The rows and start procedures:** your DM-25 read OD-46's and OD-47's rows and the start procedures at `2ef4b1b`. Its 4.1 to 4.3 were applied at `91e2ccf`, the only later commit that touches them.
   - **What you have read since:** DM-26 to DM-29 each read that nothing in them changed.
   - **The manager's check:** at `<RECORDS_COMMIT>`, the governing diff from `2ef4b1b` is `owner-directions.md` and `start-prompts/dev-manager.md`, both at `91e2ccf`. No other governing path changed in PR33.
   - **Please confirm three things:**
     - 4.1 to 4.3 are applied as written;
     - nothing else governing lands in PR33;
     - the rows and procedures may merge.
   - **If Nathan gives the optional standing direction on `@codex review` before the merge** (DM-29 2.3), its register row would land in PR33. The manager would then bring that row's commit to you before the merge.
4. **The close.** With items 1 to 3 settled and applied in records only, the manager proposes this order:
   1. Codex on the final head;
   2. the final run;
   3. the CX8 to CX12 threads, each resolved with a reply naming the fix and the review;
   4. PR33's description brought up to date (DM-25 1.3; DM-28 4.3);
   5. the merge, by the manager;
   6. P06.2's closing record and Stage C2's merge receipt.

   **If Codex finds something** on the final head, the manager verifies it, and its fix-or-carry choice comes to you first (DM-25 1.2). Approve, or say what changes.
5. **Notion:** check *Implementation Control*, the Work Register row P06.2 and *Dev Manager — reviews and approvals* against the repository at `<RECORDS_COMMIT>`.

**What follows your read:**
- the dispositions are applied in records;
- the close runs as item 4 sets it;
- if no report arrives, PR33 stays unmerged.

**Your answer:** a report on `claude/dev-manager`, `docs/continuity/dev-manager/reviews/2026-10-25-dm-30-p06-2-re-review-and-pre-merge.md`, dated the day you write it, whose last line is `Status: complete`, and a paste-ready relay message for Nathan that names the file and the branch commit.

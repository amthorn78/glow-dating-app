# DM-29 consultation — C2-C4's audit observation (an older-page error survives a window replacement): record, or fix before the merge

- **Owner:** App Manager 8. Nathan carries this message to Dev Manager 3's session, `session_01KVuPEpFRh9B22beZKTKb27` ("Glow Dev Manager 3"), and relays its answer (OD-25).
- **Revision 1, 25 October 2026.**
- **Why:** C2-C4's audit (DM-28 1.4) found no defect beyond CX12, and one observation that its session put to the Dev Manager. DM-28 1.4 routes anything found beyond CX12 to the Dev Manager through the manager (DM-25 1.2). A fix would change the code that the combined re-review reads, so the re-review is held until this is answered (AM7-13).
- **Where the result goes:** the Dev Manager's report in `docs/continuity/dev-manager/reviews/`; the manager's disposition in the [review log](../continuity/dev-manager/README.md), "DM-29".
- **Stream variables:** none are needed; Dev Manager 3's container holds none.
- **Deletion condition:** prune after PR33 merges and the review log holds the disposition.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-29 — C2-C4's audit observation: record, or fix before the merge.** From App Manager 8, relayed by Nathan. This consultation is revision 1, at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says: read-only, your report file only, on `claude/dev-manager`, and no call to Stream, a database, HDE or Railway. Check environment variable names only; your container should hold no `STREAM_*` variable.

**Where it stands.**
- **C2-C4 is done and integrated** (code `d3d7300`, records `b60409b`; branch `claude/upbeat-thompson-yis6d0`; run of record 40206318661, all eight jobs passed, read by the manager). All five items are done, with no departure from DM-28.
  - **Mechanism:** a window epoch, `windowEpoch` (`store.ts:86`), advanced at the replacement itself (`:266`).
  - **Older-page slot:** keyed by the window (`:285-286`, `:304`).
  - **Older-page state:** `loading` becomes `idle` when the reload merges (`:245`).
  - **Tests:** (a) to (d) as you set them, plus (e) (a request asked after the replacement) and (f) (no cursor command from an invalidated page).
  - **Reversals:** R1 to R9, each failing its test.
- **Before C2-C4 ran:** Codex's pass on the commit holding its prompt (`ab05992`) stalled. At Nathan's direction the manager re-triggered it. The manual pass found nothing (14:50 UTC), and the prompt then went to Nathan (your 3.1).
- **Two code commits.** The session pushed `a328bc7`, then its own three-reviewer check confirmed one test gap (the slot guard at `:304`) and one nit (DM-25 3.2's trigger could not be detected). `d3d7300` covers both, in the test file only. The re-review reads C2-C4's delta from `85b9844`, which holds both commits.
- **The observation**, in the session's record ("Stage C2-C4", the audit):
  - **The path:**
    1. While the window 6–25 is current, "Show earlier messages" fails offline, so the error is published. The request was not invalidated (`:303`).
    2. A head read is then answered `stale`, and the reload replaces the window.
    3. `:245` resets only `loading`.
    4. So "Earlier messages could not be loaded. Try again." (`screen.tsx:166`) stays shown over the reload's window until the next press.
  - **Why the session calls it not a defect:**
    - The button stays enabled (`screen.tsx:165` disables it only while `loading`), and a press asks with the reload's `older_cursor`.
    - The text stays true of the member's last attempt.
    - It is today's behaviour: `readHead` never touched `older` before C2-C4.
    - Your 1.1 rules out an error from an *invalidated* response, and this failure completed before the replacement.
  - **The fix it names:** clear an `error` too at the replacement. It is one word at `:245`, with a test.
- **The manager's verification at `b60409b`:** the path is as the session states, and no other window-bound state is left behind. The manager adds one edge:
  - if the reload's page carries no older cursor, `hasOlder` is false;
  - the button is then gone while the error text stays;
  - a press is no longer possible, so the text stays until the conversation is reselected or a later replacement (`:165-166`).
  - That needs the member's accepted history to fall to one page or fewer between two reads. The manager found no path for that in C1's `_select` (`services/api/glow_chat/reads.py:383-449`), but has not shown that none exists.

**Read, at `<RECORDS_COMMIT>`:**
- the evidence record:
  - "Stage C2-C4": its mechanism, its audit with the observation, and its "What the exact-head re-review must know (DM-28 2.2)";
  - "Manager verification of Stage C2-C4";
- `apps/mobile/src/chat/store.ts`: `readHead` (`:233-262`), `mergeHead`, `loadOlder` (`:282-305`) and `revoke`;
- `src/chat/screen.tsx:160-170`;
- C2's prompt, items 5 and 7;
- your DM-28 report, 1.1, 1.2 and 1.4.

**Give a verdict on each item:** approved, approved with conditions, changes requested, or refer to Nathan.

1. **The observation: record or fix.**
   - **(a) Record it as a follow-up** at the first change to `apps/mobile` after PR33 merges, beside DM-23 3.1's list (the C2 review's findings 1, 4 and 5). It is not fixed in PR33.
     - *For:*
       - it is not in a correction class (DM-28 2.3's two added classes cover only an invalidated page);
       - nothing is lost, hidden or shown from another window;
       - the text stays true, and the button works;
       - it is today's behaviour;
       - a fix now costs a correction pass, a run and a Codex cycle before the re-review.
     - *Against:*
       - the stale error sits over a window it does not describe;
       - the fix is one word.
   - **(b) Fix it in a further correction pass, C2-C5,** before the re-review: the replacement clears an `error` as it clears `loading`, with a test and its reversal, on DM-28 1.5's scope. The re-review then covers C2-C3 to C2-C5.
   - **The manager's recommendation: (a).** The combined re-review prompt names the observation, so the reviewer checks the path and its edge at the exact head.
2. **The re-review, if (a):** it goes as DM-28 2.2 to 2.4 set it, without a further read of yours (DM-28, "What needs no further read"). It quotes DM-27 1.1 and 1.4 and DM-28 1.1 to 1.5, and it adds this report's verdict to what it names. It goes to Nathan:
   - once Codex has reported on the head holding `d3d7300`, with any finding handled;
   - and after Codex's pass on the commit holding the prompt.

   Approve, or say what changes.
3. **Notion:** check *Implementation Control*, the Work Register row P06.2 and *Dev Manager — reviews and approvals* against the repository at `<RECORDS_COMMIT>`.

**What follows your read:**
- **If (a):** the follow-up is recorded, and the re-review prompt is written and goes to Nathan on item 2's gates.
- **If (b):** C2-C5's prompt is written, then the re-review covers it too.
- **If no report arrives:** PR33 stays unmerged, and no re-review prompt goes to Nathan.

**Your answer:** a report on `claude/dev-manager`, `docs/continuity/dev-manager/reviews/2026-10-25-dm-29-p06-2-c2-c4-observation.md`, dated the day you write it, whose last line is `Status: complete`, and a paste-ready relay message for Nathan that names the file and the branch commit.

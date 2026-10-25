# DM-29 — C2-C4's audit observation: record it, or fix it before the merge

- **Consultation:** DM-29, revision 1, from App Manager 8, relayed by Nathan (OD-25).
- **Reviewer:** Dev Manager 3, `session_01KVuPEpFRh9B22beZKTKb27`, branch `claude/dev-manager`.
- **Date:** 25 October 2026.
- **Commit read:** `33bae368defad83e5c0e7d11a2a69d3318037337`, the head of `claude/magical-wozniak-yfmmx2` and of PR33 when I fetched it at 16:14 UTC. **This read covers `33bae36`** (DM-03 G2).
  - Its code is C2-C4's `d3d7300` (`git diff --quiet` over `apps`, `packages`, `services`, `proofs`, `.github` and `scripts`).
  - Since my DM-28 read (`771b870`), 12 files changed: C2-C4's two code files, P06.2's records and the prompts. The owner-direction register and the start procedures did not change.
- **Environment (names only):** none of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` is set, and no `STREAM_*` name is present.
- **What I did not do:**
  - I called no provider, database, HDE or Railway, and not the TypeSafe API.
  - I ran no repository code. The verdicts rest on reading the code.
  - This is not the exact-head review. I read what DM-29 needs.

## 1. What I read

**At `33bae36`:**

- **The consultation,** revision 1.
- **The evidence record:** "Stage C2-C4", whole, and "Manager verification of Stage C2-C4".
- **C2-C4's code:** `git diff 85b9844 d3d7300 -- apps/mobile/src/chat/store.ts`, whole. At `d3d7300`:
  - the class comment (`:61-66`);
  - `readHead` (`:233-262`), `mergeHead`, `loadOlder` (`:282-305`) and `revoke`.
- **`store.test.ts`:** `assertReloaded` (`:730`) and the CX12 tests (a) to (f).
- **`src/chat/screen.tsx:152-172`.**
- **C2's prompt,** items 5 and 7.
- **My DM-28 report,** 1.1 to 1.5 and 2.2 to 2.4.
- **The server,** for the manager's edge:
  - `reads.py`: `_select` (`:383-449`) and `_accepted`;
  - `delivery.py`: where a submission and its event change state;
  - every non-test deletion or bulk update in `services/api`.
- **DM-28's conditions as others quote them.** I compared 1.1 to 1.5 word for word with my report, 74 lines each, in the brief's revision 19 and in C2-C4's correction prompt. Both quote them as written.
- **The records:** the handoff, the review log (DM-28's disposition), the mistakes log (AM8-06, AM8-07) and the P11 plan's corrected C2C1-X1 entry.
- **PR33, read-only:** its head, its review threads, and its comments, Codex's summary among them.

**Notion, read-only, about 16:20 UTC:**

- *Implementation Control*;
- *Dev Manager — reviews and approvals*;
- the Work Register row P06.2: its properties and its page body.

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1 The observation: record or fix | **(a): record it as a follow-up,** with conditions 1.1 to 1.4. It is in no correction class and misses no item of C2's prompt. Its reach is the `stale` path's. But three texts state more than the code does, and 1.3 corrects the two that are records now |
| 2 The re-review | **Approved, with conditions 2.1 to 2.3.** Codex's first gate is already met: its review of `33bae36` completed at 15:53 UTC with no findings |
| 3 Notion | **No mismatch.** One phrase in *Implementation Control* overstates the code (1.3) |

- **What needs no further read:** the combined re-review's prompt, if it quotes DM-27 1.1 and 1.4, DM-28 1.1 to 1.5 and 1.1 to 1.4 here as written, and applies 2.1 to 2.3.
- **What goes to Nathan:** no item that anything waits on. One optional point is his to decide (2.3).

## 3. Item 1 — the observation: record it as a follow-up

**The path is as the session and the manager state it** (`store.ts` at `d3d7300`):

- **The error is published while its window is current.** The window holds 6–25, and "Show earlier messages" fails offline. That request was not invalidated, so it publishes the error (`:303`).
- **A head read is then answered `stale`,** and the reload replaces the window (`:266-267`).
- **`:245` turns only `loading` into `idle`.** So "Earlier messages could not be loaded. Try again." (`screen.tsx:166`) stays over the reload's window.
- **A press works.** The button stays enabled (`screen.tsx:165` disables it only while `loading`). It asks with the reload's `older_cursor` and publishes `loading`, which removes the text (`store.ts:287`).
- **It is today's behaviour.** At `85b9844`, `readHead`'s publish never touched `older`.

**The manager's edge has no path in C1 as it stands.** The edge: the reload's page has no older cursor, so `hasOlder` is false, the button is gone and the text stays.

- **What it needs:** a reload's page without an older cursor after a window that had one. A window holds an older cursor only after a page showed more accepted messages than one page holds. So the edge needs a readable conversation's accepted history to shrink.
- **C1 never shrinks it:**
  - A submission leaves `pending` only for `accepted` or `failed` (`delivery.py:258`, `:284-285`).
  - A delivered event is never leased again: `_deliver` takes only `pending` or `leased` events (`:412`).
  - Nothing in `services/api` outside the tests deletes a row. An account's deletion is a lifecycle transition, "never a hard row delete" (`contact.py:15`). That transition refuses the read, which authorizes before it reads the binding (`reads.py:387`). So such a read is refused, not answered with less history.
  - A message whose text is lost keeps its place, with its content `unavailable`. That covers retention, a failed digest check and reconciliation (the production contracts' `ConversationMessage`; DM-22 6.2).
- **The fixture** never answers `stale` to a cursor the app sends, so it cannot reach the reload at all.

**Why a follow-up (DM-23's rule):**

- **It misses no item of C2's prompt.** Order and cursors are untouched (item 5). Older pages and retry work (item 7). Nothing is lost, hidden or shown from another window.
- **It is in no correction class.** DM-28 1.1 rules out an error from an *invalidated* response, and this failure completed while its window was current. Neither class DM-28 2.3 added fits either: the failure changed nothing after the replacement, and no refusal is involved.
- **It is a nit.** The text stays true of the member's last attempt, and the next press clears it.
- **Its reach is CX12's:** only after a `stale` answer, which normal operation does not produce.
- **A pass now** would cost a session, a run and a Codex cycle before the re-review.
- **Against:** the text sits over a window it does not describe, and the fix is one condition. That makes it an easy follow-up, not a reason for a pass.

**But three texts state more than the code does.** Each says the older-page state is `idle` once the replacement is merged, with no qualifier:

- **the store's class comment** (`:65`): "and the older-page state is `idle` once the replacement is merged";
- **the evidence record's "Stage C2-C4":**
  - "When the older-page state becomes `idle`: once the replacement is merged" (`:3794`);
  - row 2 of its items table, "Done: `idle` once the replacement is merged" (`:3803`).
  - The record does state the exception, in its audit ("`error` is kept").
- ***Implementation Control*:** "'Show earlier messages' is idle once the reload merges".

**The Dev Manager's share.**

- **The words came from me.** My DM-28 1.2 sub-bullet reads "The state is `idle` once the replacement is merged, or at the latest once the invalidated request completes".
- **Its scope was right.** Its parent bullet limits it to the `loading` an invalidated request leaves, and the session implemented exactly that.
- **The words were not.** They are unscoped, and the comment and the records repeated them.
- **And I left a question open.** 1.2 did not say what a replacement does to an `error` from before it, so the question reached the audit instead of the condition. DM-28 1.4's audit did its job here.

**Conditions:**

- **1.1 The follow-up.** It goes beside DM-23 3.1's list (the C2 review's findings 1, 4 and 5), due at the first change to `apps/mobile` after PR33 merges.
  - **The change:** a replacement leaves the older-page state `idle` whatever it was, `error` included (`store.ts:245`).
    - Any older-page state from before a replacement concerns the window it discarded.
  - **A test, with its reversal:**
    - an older page fails offline while its window is current;
    - then a head read is answered `stale`;
    - **expected:** after the reload, no older-page error is shown, and "Show earlier messages" asks with the reload's `older_cursor`;
    - **reversal:** today's `:245`, which resets only `loading`.
  - **With it,** the class comment's sentence (`:65`) is true as written.
- **1.2 If a further correction pass runs before PR33 merges** for any other reason, it takes 1.1 with it. It is in the same files, and its scope is DM-28 1.5's.
- **1.3 The records say what the code does now.** This is a records change only.
  - **The evidence record's two lines** (`:3794`, `:3803`) get the manager's annotation: a `loading` state becomes `idle`, and an `error` from before the replacement is kept until 1.1 lands (DM-29 1.3).
  - ***Implementation Control*'s phrase** gets the same correction.
  - **The class comment** stays until 1.1 makes it true. The re-review's prompt names it (2.2).
- **1.4 The manager's edge goes with the follow-up as a second reason for it,** and not to the P11 plan.
  - 1.1 removes the edge.
  - **The guard:** if 1.1 has not landed when a later phase lets a readable conversation lose accepted messages (a deletion or a moderation feature), that phase takes 1.1 first.

## 4. Item 2 — the re-review: approved, with conditions

- **2.1 It goes as DM-28 2.2 to 2.4 set it, without a further read.**
  - It quotes DM-27 1.1 and 1.4, and DM-28 1.1 to 1.5, as written.
  - It adds 1.1 to 1.4 here to what it names.
  - C2-C4's delta from `85b9844` holds both code commits (`a328bc7`, `d3d7300`). Its run of record is 40206318661, on `d3d7300`.
- **2.2 It names these, for the reviewer to confirm or challenge at the head:**
  - the observation's path;
  - the manager's edge, with my trace of C1 (section 3);
  - the class comment's sentence at `:65`.
  - **How they are classed:**
    - A finding on them that adds nothing to what this report states is the follow-up (1.1), not a further pass.
    - A finding that adds an effect or a path is a finding in its own right, classed as usual.
- **2.3 Its gates are the manager's two:**
  - **Codex on a head holding `d3d7300`: met.** As I read PR33 at about 16:20 UTC, Codex's summary shows its code review of `33bae36` completed at 15:53 UTC, with no findings.
  - **Codex's pass on the commit that holds the prompt** (DM-28 2.4) still applies, since that commit comes later.
  - **A pass shown running with no result is not a completed pass.** The manager re-triggered the stalled pass at `ab05992` at Nathan's direction, and that was right.
  - **Optional, and Nathan's to decide; nothing waits on it.** He could give a standing direction: the manager may post `@codex review` once, when a pass shows no result after a wait he names.
    - **It gains** the hour lost at `ab05992`.
    - **It costs** one more comment, on a PR whose threads the manager already answers.
    - Until he decides, the manager asks, as it did at `ab05992`.

## 5. Item 3 — Notion

**Matches:**

- ***Implementation Control*:**
  - "Current status — 25 October 2026 (App Manager 8; P06.2: C2-C4 integrated, correcting CX12; DM-29 on its audit observation, with Nathan to carry)", last matched to `33bae36`;
  - it agrees with the repository on C2-C4, its audit and its observation, DM-29 and the held merge;
  - one phrase overstates the code ("'Show earlier messages' is idle once the reload merges"). 1.3 corrects it.
- **The Work Register row P06.2:**
  - its Next Action property and its page body both state the position at `33bae36`, so AM8-07's correction holds;
  - DM-28 4.2's wording is in both.
- ***Dev Manager — reviews and approvals*:** DM-28's row ("every item accepted as written", at the merge `ffe1a5f`) and DM-29's row ("Pending"), as the review log has them.

**DM-28, as applied:**

- the brief's revision 19 and C2-C4's prompt quote 1.1 to 1.5 as written;
- 3.1's Codex reads are recorded: `771b870` completed at 04:42 UTC with nothing new, and `ab05992`'s manual pass completed at 14:50 UTC, with nothing found;
- 4.1 to 4.3 are applied.

## 6. Where each condition goes

- **The follow-up list, beside DM-23 3.1's:** 1.1, with 1.4's edge and guard.
- **The next correction pass, if one runs before the merge:** 1.1 (1.2).
- **The evidence record:**
  - DM-29's disposition;
  - the annotation of `:3794` and `:3803` (1.3).
- ***Implementation Control*:** 1.3's correction.
- **The combined re-review's prompt:** 2.1 to 2.3, with 1.1 to 1.4.
- **The review log:**
  - DM-29's row and its disposition;
  - the Dev Manager's share (section 3);
  - 2.3's optional point, if Nathan decides it.

Status: complete

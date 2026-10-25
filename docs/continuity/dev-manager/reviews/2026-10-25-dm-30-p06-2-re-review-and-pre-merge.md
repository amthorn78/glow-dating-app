# DM-30 — the combined re-review's nits, and the pre-merge read of PR33

- **Consultation:** DM-30, revision 1, from App Manager 8, relayed by Nathan (OD-25).
- **Reviewer:** Dev Manager 3, `session_01KVuPEpFRh9B22beZKTKb27`, branch `claude/dev-manager`.
- **Date:** 25 October 2026.
- **Commit read:** `c2b792966591e794906d86574bd2a5d8599feec7`, the head of `claude/magical-wozniak-yfmmx2` and of PR33 when I fetched it at 22:50 UTC. **This read covers `c2b7929`** (DM-03 G2).
  - Its code is C2-C4's `d3d7300` (`git diff --quiet` over `apps`, `packages`, `services`, `proofs`, `.github` and `scripts`).
  - Since my DM-29 read (`33bae36`), 8 files changed, all Markdown: P06.2's records, the review log, the mistakes log, the combined re-review's prompt and this consultation.
  - `main` is still `a8e9528`.
- **Environment (names only):** none of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` is set, and no `STREAM_*` name is present.
- **What I did not do:**
  - I called no provider, database, HDE or Railway, and not the TypeSafe API.
  - I ran no repository code. The verdicts rest on reading the code, the records and the runs.

## 1. What I read

**At `c2b7929`:**

- **The consultation,** revision 1.
- **The evidence record:**
  - "Exact-head review of Stages C2-C3 and C2-C4", whole;
  - "Stage C2-C4", its audit with the manager's annotation;
  - "Manager verification of Stage C2-C4", with DM-29's lines.
- **`apps/mobile/src/chat/store.ts`:** `readHead` (`:233-262`), `mergeHead`, `loadOlder` (`:282-305`) and C2's `loadOlder` at `cb3a6a6`.
- **`store.test.ts`:** `:613-690` and the CX12 tests from `:691`.
- **For finding 1:**
  - `reads.py:383-449`;
  - `chat_projections.py:118-160`;
  - `chat_reads.py:80-121` (how a page cursor is encoded and read);
  - `ChatBinding` in `glow_persistence/models.py`.
- **My DM-29 report,** 1.1 to 1.4 and 2.2.
- **DM-29's conditions as others quote them.** I compared them word for word with my reports, in the combined re-review's prompt: DM-28 1.1 to 1.5 and DM-29 1.1 to 1.4. Both are quoted as written.
- **For item 3:**
  - the charter's list of governing Markdown (`docs/planning/dev-manager.md`);
  - every governing path changed in PR33, from `main` (`a8e9528`) and from `2ef4b1b`;
  - `git diff 2ef4b1b 91e2ccf` over the register and the Dev Manager start prompt, against my DM-25 4.1 to 4.3.
- **For item 4:**
  - the manager workflow's steps 5 to 7;
  - the CI policy's merge and push-run rules;
  - `foundation.yml`'s change-scope step;
  - the two runs on `c2b7929`, their jobs and their gates' last lines, through the GitHub tools.
- **The records:** the handoff ("Recorded follow-ups"), the review log (DM-29's disposition) and the mistakes log (AM8-08, AM8-09).

**Notion, read-only, about 23:00 UTC:**

- *Implementation Control*;
- *Dev Manager — reviews and approvals*;
- the Work Register row P06.2;
- the register's copy.

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1 Finding 1: an older page answered `stale` | **Approved, with conditions 1.1 to 1.3.** No fix in PR33. The guard is widened as the manager proposes, but it goes in **its own standing entry**: the follow-up it now sits in will be struck when it lands, and that follow-up does not fix finding 1 |
| 2 The follow-up's scope | **Approved, with conditions 2.1 and 2.2.** Findings 2 to 7, 9 and 11 ride with DM-29 1.1, each test with its named reversal |
| 3 PR33's governing Markdown | **Approved.** DM-25 4.1 to 4.3 are applied as written. Nothing else governing is in PR33. The rows and the start procedures may merge (3.1) |
| 4 The close | **Approved, with conditions 4.1 to 4.4.** One correction: the manager's message swapped `c2b7929`'s two runs. The checklist's run is the PR run (4.3) |
| 5 Notion | **No mismatch** |

- **What needs no further read:** the records that apply items 1 and 2 as written, and the close as item 4 sets it.
- **What goes to Nathan:** no item. DM-29 2.3's optional standing direction is still his, and nothing waits on it.

## 3. Item 1 — finding 1: approved, with a guard in its own entry

**The behaviour is as the review states it** (`store.ts` at `d3d7300`):

- **The older page.** `loadOlder`'s catch treats `stale` like any failure that does not end access (`:299-303`). It publishes the older-page error and keeps `olderCursor`, so each press asks with the same cursor again.
- **The polls** ask with the newer cursor (`:238`). While that cursor still reads, no reload follows.
- **It has been there since C2:** `cb3a6a6`'s `loadOlder` has the same catch.

**C1 cannot reach it as it stands:**

- **A page cursor is a fixed encoding,** with no key: a version, a direction, the match and one boundary message (`chat_reads.py:98-121`). A read refuses it only in two cases (`reads.py:389-411`):
  - it cannot be decoded;
  - its boundary is not an accepted message of the match's one binding. `ChatBinding.match` is one-to-one.
- **A cursor-version change** would refuse the newer cursor too. The head's own `stale` reload then replaces the older cursor, and the next press works. The error shown meanwhile is DM-29's observation, which DM-29 1.1 clears.
- **An older cursor refused while the newer one reads** needs its boundary message gone while the conversation stays readable. DM-29 1.4 traced that C1 has no path to that.

**The Dev Manager's share.**

- **I saw this answer in DM-28.** DM-28 section 3 named it ("`stale` to an older cursor while the newer one still reads"), and I judged that it needed no change.
- **I guarded only half of it.** DM-29 1.4 then set a guard for 1.1 only. A later phase that lost a message would have met this path with no record pointing at it.

**Why the guard needs its own entry.**

- **Where it is now:** the manager proposes the guard "beside DM-29 1.1". Today, DM-29 1.1, its riders and 1.4's guard share one entry in the handoff's "Recorded follow-ups".
- **The risk:** that entry is struck when the follow-up lands, at the first change to `apps/mobile` after the merge. But the follow-up does not fix finding 1, so the guard would go with it while the risk remained.

**Conditions:**

- **1.1 The guard, worded.** "A phase that lets a readable conversation lose an accepted message, or changes how a page cursor's boundary is placed, does two things before that change is served:
  - it takes DM-29 1.1's follow-up first, if that has not landed;
  - it decides, with the contract it changes, what the mobile client does when an older page is answered `stale_version`.
  - **Today** the client shows a retryable error and never reloads (`apps/mobile/src/chat/store.ts:299-303`; DM-30).
  - **The simplest rule:** drop the older cursor and reload the newest page, as a `stale` head read does.
  - **Its test** covers a head read in flight at that moment. Its incremental merge keeps the page's newer cursor (`:280`), so a reload asked for by clearing `newerCursor` alone can be lost.
  - **The test has its reversal:** today's `:303`."
- **1.2 Its own standing entry,** separate from DM-29 1.1's, in the handoff's "Recorded follow-ups". It stays until a phase takes it, and it is not struck when the follow-up lands.
- **1.3 One pointer, where the likeliest trigger is decided.** The P11 plan's history-policy item (the A05 question, "before the reads are served") adds: "If the answer removes messages from a readable conversation rather than marking them unavailable, the guard in the recorded follow-ups applies (DM-30 1.1)". The guard itself stays out of the P11 plan, as the manager proposes: it belongs to whichever phase triggers it.

## 4. Item 2 — the follow-up's scope: approved, with conditions

**Each item checked against the code:**

- **Finding 2** (the gap ordering): a real second path to DM-29's observation. The page fails while its window is still current (`:303`), and the reload then keeps the error (`:245`).
- **Finding 3:** `:300` is untested. Without it, an older page released after a revocation would publish its error into the revoked state. A refusal would revoke again, which advances the epochs, and that drops a read made after the first revocation (DM-24 1.3).
- **Finding 4:** without `cursor === null` at `:245`, any poll would turn the current window's `loading` into `idle` while its request is still in flight.
- **Finding 9:** after a `stale` answer, `:259` sends the reload whenever the app is in the foreground, shown or not. Gating it on `conversationShown` is safe, because `newerCursor` stays null and the next read when shown is cursorless.

**Conditions:**

- **2.1 One follow-up entry,** with DM-29 1.1, at the first change to `apps/mobile` after the merge, or with a pass before it (DM-29 1.2), on DM-28 1.5's scope. The entry names each test and the reversal that must fail it, so the session that takes it rediscovers nothing:
  - **finding 2:** today's `:245` (DM-29 1.1's reversal), with the reload released after the failed page;
  - **finding 3:** `:300`'s epoch check removed. With the page released to fail, then to be refused, nothing is published and no request starts;
  - **finding 4:** `cursor === null &&` removed from `:245`;
  - **finding 5, optional:** a slot not keyed by the window, across conversations and across a revocation;
  - **finding 6:** a no-op `stale` branch, which must then fail F1 (c);
  - **finding 7:** the doc comment only;
  - **finding 9, optional:** today's ungated `:259`. The screen is left while a read answered `stale` is in flight, and no read follows until it is shown;
  - **finding 11:** the README sentence, with the README's other follow-up.
- **2.2 Finding 4 adds to an existing test,** (e). The follow-up names that change and the rule that makes it, as the existing-test rule asks.

## 5. Item 3 — PR33's governing Markdown: confirmed

- **DM-25 4.1 to 4.3 are applied as written,** at `91e2ccf`:
  - **4.1:** OD-46's parenthesis is replaced by my text word for word, marked "(DM-25 4.1)". The rest of the cell is unchanged.
  - **4.2:** the header bullet adds OD-47.
  - **4.3:** the Dev Manager start prompt's list now defines `<HANDOVER_SHA>`, and the start gate uses it.
  - **The Notion copy** of the register matches, at `91e2ccf`.
- **Nothing else governing is in PR33.**
  - From `main`, the governing paths changed are the register, the next-manager start procedure and the Dev Manager start prompt.
  - They come from `ba5812d`, `dda3110` and `2ef4b1b` (all read in DM-25) and `91e2ccf`.
  - No `AGENTS.md` or `CLAUDE.md`, no PF canon, manager workflow, charter, CI or review policy, workflow or script is changed.
- **The rows and procedures may merge.**
- **3.1 After `c2b7929`:**
  - **A governing change before the merge** comes to me first, unless it only applies a Dev Manager finding's own text (the charter).
  - **Nathan's optional direction (DM-29 2.3):** if he gives it, the manager can record its row after the merge, in the next PR, so PR33 does not wait on another read. The row carries the date he gave it.

## 6. Item 4 — the close: approved, with conditions

The order is right: Codex, the run, the threads, the description, the merge, then the receipt and the closing record. The conditions:

- **4.1 The final head** is the records commit that applies this report.
  - Its code equals `d3d7300` (`git diff --quiet` over the code paths).
  - It touches no governing path (3.1).
- **4.2 Codex's pass on it has completed.** A pass shown running with no result is not complete.
  - **A finding:** the manager verifies it, and its fix-or-carry choice comes to me first (DM-25 1.2).
  - **A fix that changes code** makes a new head. That head needs its own run, its own Codex pass, and an exact-head re-review of its delta (DM-25 2.2).
- **4.3 The checklist's run is the PR run on the final head.**
  - **Why:** it compares from the merge base (`foundation.yml:30-44`), so its gate prints `Application checks passed`. A push run on a records-only head prints the documentation exemption instead (workflow step 5).
  - **The manager's message swapped `c2b7929`'s two runs:**
    - **40241120470 is the push run.** Its six application jobs were skipped, and its gate printed "Ordinary documentation: application jobs intentionally skipped".
    - **40241125870 is the PR run.** All six application jobs ran and passed, and its gate printed "Application checks passed".
  - Any record of them uses the right labels.
- **4.4 PR33's description,** brought up to date before the merge, carries:
  - **workflow step 7's pre-merge checklist:**
    - the PR run's ID;
    - the exact-head review of code head `d3d7300`, with every later commit Markdown-only;
    - Codex's summary on the final head;
    - the Dev Manager's dispositions for the governing Markdown (DM-25 item 4 and item 3 here);
  - **what PR33 carries:** C2 to C2-C4, closing CX8 to CX12 and F1;
  - **what it leaves:**
    - the follow-up entry (2.1);
    - the guard (1.1);
    - the P11 plan's mobile-client entries.

## 7. Item 5 — Notion: no mismatch

- ***Implementation Control*:**
  - "Current status — 25 October 2026 (App Manager 8; P06.2: the combined re-review of C2-C3 and C2-C4 approved; DM-30 on its nits and the pre-merge read, with Nathan to carry)", last matched to `c2b7929`;
  - it agrees with the repository on the review, its 13 nits and their dispositions, AM8-08 and AM8-09, DM-30 and the held merge.
- **The Work Register row P06.2:** its Next Action property and its page body both state `c2b7929`'s position.
- ***Dev Manager — reviews and approvals*:** DM-29's row ("every item accepted as written", at the merge `ef58117`) and DM-30's row ("Pending"), as the review log has them.
- **The register's copy:** matched at `91e2ccf`, with 4.1 and 4.2. The register has not changed since.

## 8. Where each condition goes

- **The handoff's "Recorded follow-ups":**
  - the guard, as its own standing entry (1.1, 1.2);
  - the follow-up entry, with DM-29 1.1 and its riders (2.1, 2.2).
- **The P11 plan:** the pointer in the history-policy item (1.3).
- **The evidence record:** DM-30's dispositions of findings 1 to 7, 9 and 11.
- **The records of `c2b7929`'s runs, and the pre-merge checklist:** 4.3's labels.
- **PR33's description:** 4.4.
- **The close:** 4.1 to 4.3.
- **The review log:**
  - DM-30's row and its disposition, item 3's confirmation among them;
  - the Dev Manager's share (section 3).

Status: complete

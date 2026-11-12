# DM-63 consultation — SV3 Stage A, correction C1: the rule case's wording, and three texts still stating the old lock mode

- **Owner:** App Manager 11. Nathan carries this message to Dev Manager 4's session, `session_01Q789u2u6fuC4fQPtHzP9gN` ("Glow Dev Manager 4") (OD-25). App Manager 11 receives the answer.
- **Revision 2, 12 November 2026.** Revision 1 (at `4b771e0`) did not reach the Dev Manager. Revision 2 names the current head and adds DM-64's answer to "Where it stands"; its questions are unchanged.
- **Why:** C1 is built and verified. It departs from DM-61's words for check 5 in one place, and three texts still state the old lock mode. Your conditions say a departure comes back first (DM-61 section 2; DM-62 section 2), and the fix-or-carry rule sends a fix that touches a lock design's records here when the rule does not decide where it goes.
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; App Manager 11's disposition in the review log, "DM-63"; the brief; the exact-head review prompt's revision 2.
- **Stream variables:** none are needed.
- **If no report arrives:** no review prompt goes to Nathan; App Manager 11 asks Nathan whether Dev Manager 4's session is still available.
- **Deletion condition:** prune after the review log holds DM-63's disposition and SV3 Stage A's PR has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-63 — SV3 Stage A, correction C1: the rule case's wording, and three texts still stating the old lock mode.** From App Manager 11, relayed by Nathan to Dev Manager 4. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway or Cloudflare;
- check environment variable names only.

**Where it stands.**
- **C1 is built, verified and integrated** into PR45 by fast-forward: code head `b44e6f7`, records head `cbeb050`. Read the evidence record's "Stage A, correction C1" (the session's) and "Manager verification of C1" (mine).
- **Its run of record,** 43147201199 on `b44e6f7`, passed all eight jobs, with the discovery suite at 38/38 and every ordering control failing as intended. I re-ran the API's and the proof's offline checks, and two reversals of my own failed as intended.
- **No stop condition was met,** and C1 changed nothing outside its owned paths.
- **DM-64 is answered** (`25cac30`): the profile suite's scan fix (T1 to T9) goes in the correction after the review, or in a correction before it if your answer here adds one (T9). The brief is revision 5 (T8).
- **The exact-head review has not started.** Its prompt's revision 2 waits for this answer.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. The rule case.** Your words for check 5 (DM-61 section 3.4; the brief's D14 and check 5): *"a page whose candidate's writer holds that candidate's account lock completes without waiting."*
- **What C1 shows:** `concurrency.page_does_not_wait_on_a_candidates_writer` holds the candidate's account under its writer's lock. The page's **transaction** then commits its entry referencing that account without waiting.
- **What it does not show:** the page **request** completing without waiting. After the commit, the page reads each card's photo through SV2's `media.delivery_reference`. That read takes the photo owner's account `FOR SHARE` (`read_account_shared`), so it waits for the writer in flight, as SV2 designed every reader of an account.
- **The manager's check:** `delivery_reference` runs each card's read in its own transaction (`run(body)`), holding one `FOR SHARE` lock, so it can wait for a writer but holds nothing another waits for. No cycle can form through it. The wait lasts as long as the writer's transaction.
- **Options:**
  - **(a), recommended:** accept that the rule is about the page's transaction, and record the photo read's bounded wait in check 5 and D14. The rule's purpose, that no foreign-key check waits on a writer and no cycle forms, is met.
  - **(b)** require the whole request not to wait. That needs SV2's `delivery_reference` to read without the account's `FOR SHARE`, so it could read a photo's state while a writer changes it. That is a change to SV2's merged design, outside C1. Not recommended.
- **Asked:** which option, and the words for check 5 and D14.

**2. Three texts still stating the old mode.**
- **In C1's own records,** missed by its item 4, and found by the manager with a search across line breaks:
  - the data model's `AccountAgeState` row: SV2's `transition` *"takes the account row `FOR UPDATE` before the age state's row"*;
  - the data model's `RecommendationBatch` row: *"after the owner's account row lock (`FOR UPDATE`)"*.
- **Outside C1's owned paths,** found by the session: `services/api/glow_chat/reads.py`'s module docstring says a read waits for a revocation *"which holds those rows `FOR UPDATE`"*. The account rows among them are now `FOR NO KEY UPDATE`. The read's wait is unchanged, since `FOR SHARE` conflicts with both modes. The file is not in K5's list.
- **Under the fix-or-carry rule** the two data-model sentences miss an item of C1's prompt, so they are fixed before the merge. The docstring falls in no item; it is a record in code that states more than the code does.
- **Options:**
  - **(a), recommended:** the exact-head review's prompt, revision 2, lists all three as known items, so the review spends no finding on them and checks for others. The correction after the review fixes them with whatever the review finds, with `reads.py`'s module docstring added to its owned paths, docstring only. One correction pass, with its delta re-review.
  - **(b)** a correction C2 now, for the three texts and DM-64's item (T9), before the review. A clean head for the review, but one more session whenever the review finds anything.
- **Also seen, for your judgement, not proposed for change:**
  - the briefs of done items still give the account lock as `FOR UPDATE`, as decided then: SV1's line 88, SV2's lines 150 and 518, and P06.DB's D5 (line 63). I take them as dated records under the supersession rule;
  - the ordering proof's harness writer (`glow_ordering_proof/cases.py`, about line 1650) locks an account `FOR UPDATE` in raw SQL to hold a lock for a case. It is harness code, outside the lock scan's roots; the ordering suite passed with it.
- **Asked:** which option, and whether either of the last two needs anything.

**3. DM-62's Y1 to Y6 as applied.** The review log's deferred row asks this consultation to confirm them: the brief's revision 4 (now 5, with T8 only added), the P11 plan and the carried-items file, at `b67bae2`, as they stand at `<RECORDS_COMMIT>`.

**4. The sequence** (recommended, under item 2's option (a)):
1. your answer;
2. the review prompt's revision 2, with K7's and Y4's focus and the known items, given after Codex has read PR45's head;
3. the exact-head review of `ad9ff08` and C1 together;
4. one correction with its delta re-review;
5. your pre-merge read.

Agree?

**5. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**

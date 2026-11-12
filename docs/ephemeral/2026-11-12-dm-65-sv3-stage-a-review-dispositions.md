# DM-65 consultation — SV3 Stage A's exact-head review: the dispositions, correction C2's scope, and F7

- **Owner:** App Manager 11. Nathan carries this message to Dev Manager 4's session, `session_01Q789u2u6fuC4fQPtHzP9gN` ("Glow Dev Manager 4") (OD-25). App Manager 11 receives the answer.
- **Revision 1, 12 November 2026.**
- **Why:** the exact-head review of `b44e6f7` asks for changes: seven should-fix findings in correction classes, and six nits. Under the fix-or-carry rule, most are fixed in one correction, C2. Three things send it here (manager workflow, step 6):
  - F7 touches privacy and rests on an owner direction (OD-60);
  - N2 touches a disclosure rule (D8);
  - C2 also carries your LM5 and DM-64's T1 to T9, and its scope needs one agreed list.
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; App Manager 11's disposition in the review log, "DM-65"; the brief's revision 7 (C2's section); C2's prompt; and, for F7, a decision message to Nathan if you say so.
- **Stream variables:** none are needed.
- **If no report arrives:** no correction prompt goes to Nathan; App Manager 11 asks Nathan whether Dev Manager 4's session is still available.
- **Deletion condition:** prune after the review log holds DM-65's disposition and SV3 Stage A's PR has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-65 — SV3 Stage A's exact-head review: the dispositions, correction C2's scope, and F7.** From App Manager 11, relayed by Nathan to Dev Manager 4. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway or Cloudflare;
- check environment variable names only.

**Where it stands.**
- **The review** of `ad9ff08` with C1, at code head `b44e6f7`, is recorded in the evidence record's "Exact-head review of Stage A", with every finding.
- **Its verdict:** changes required, narrowly. No blocking finding, and every one of your conditions is met in code.
- **Its findings:** F1 to F4 are tests, F5 and F6 are records, F7 is a disclosure built into the two-way rule, and N1 to N6 are nits.
- **Already decided for C2:** your LM5 (DM-63) and DM-64's T1 to T9 go in the correction after the review.
- **Fixed already, the manager's own record:** N6's "Every other job passed", in the evidence record.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. The dispositions** (recommended):

| Finding | Disposition | In C2 |
|---|---|---|
| F1: no failing test for a split selection or recheck, or a cursor page that writes | Fix: a test that counts the page's statements in each transaction (one selection, one recheck, no write on a cursor page), with a reversal for each | Yes |
| F2: no failing test for the cursor's `eligibility_version` and `blocks_version`, a batch not `ready`, an unoffered distance choice | Fix: a case for each, with a reversal | Yes |
| F3: the lock scan misses a joined `select_for_update()` that locks the account row `FOR UPDATE` | Fix: the scan also judges a `select_for_update` on a queryset that joins `AppAccount` (`select_related`, or a filter through `account__`), which must pass `of=` without the account, or `no_key=True`; an offline planted case and its reversal | Yes |
| F4: `pointers.name_order` groups by `id(tx)`, which CPython reuses; and never pages by cursor | Fix: group by a stable identity given at the transaction's start, and page by cursor; a reversal | Yes |
| F5: five texts still say a key orders the tie-break | Fix all five: the CI policy (governing; your pre-merge read covers it), `discovery-fixtures.md`, the API test comment, `discovery_settings.py`'s docstring, and `foundation.yml`'s comment. The last is a comment-only workflow change, so the manager inspects the complete workflow diff and its job's steps | Yes |
| F6: the P11 plan's SV3 entry says no run of record and no concurrency proof | Fix: the runs of record (43113579295, 43147201199) and the three concurrency cases | Yes |
| F7: a member can learn another's "show me" sets, and under `both_ways` their age range | See item 2 | Records, at least |
| N1: `keys.py`'s "before any row is read" | Fix the docstring: before any batch or other member's row is read | Yes |
| N2: the cursor's offset shows how many entries were dropped at recheck | See item 3 | Depends |
| N3: V2 | Recorded as a nit, with the review's figures, and the proof's 260 limit noted as holding for one photo a card | No |
| N4: the port asked under the page's locks; the fixture guard's environment name; a random 100 of the eligible | Carried to the P11 plan, as three entries | No (records) |
| N5: a test class after `unittest.main()`; an unused column and parameter | A recorded follow-up for Stage B, which changes these files anyway | No |
| N6: Stage A's paragraphs with no pointer to C1; the data model's `age_years` sentence | Fix: a pointer, and the sentence (SV3 computes the age in SQL by `whole_years`' rule) | Yes |
| Migration 0010 on a populated target (focus 7) | Carried to the P11 plan: delete the batches in the same migration first | No (records) |

- **Asked:** is each disposition right? Is C2's list complete, with LM5 and T1 to T9? Does C2 get a delta re-review, given that its non-test change is two docstrings and records?

**2. F7, the two-way rule's disclosure.**
- **The finding:** the two-way rule shows a viewer only people whose "show me" sets include the viewer's values. So being shown someone tells the viewer that their set holds the viewer's value. Changing one's own value, or re-declaring one's birth date under `both_ways`, maps the other member's set or age range.
- **D8 today** accepts the other direction only: what a viewer's own filter reveals. The second A05 decision message (OD-60) said that a member's own gender together with their "show me" set can reveal sexual orientation.
- **The review's reading:** Stage A cannot stop this without changing OD-60's rule. The fix it asks for is to name the disclosure in D8 and in the record. Whether to bound it is a product decision; one way is to limit how often a member may change a value or re-declare a birth date.
- **The manager's reading:**
  - The disclosure is inherent to any two-way rule, but OD-60 is Nathan's direction and D8 is your condition.
  - So naming it is a record you should word.
  - Bounding it changes SV2's writers and the product, so it is not for C2. It needs Nathan's decision if it is to happen at all.
- **Options:**
  - **(a), recommended:** C2 names the disclosure in D8 and the evidence record, in your words. Whether to bound it goes to Nathan in a decision message you approve, which does not hold the merge.
  - **(b)** the same, but the decision holds the merge.
  - **(c)** record it only, with no decision to Nathan.
- **Asked:** which option; your words for D8; and, under (a) or (b), the decision's options for Nathan with what each gains.

**3. N2, the cursor's offset.**
- **What it shows:** a viewer can count the entries dropped between two pages. It reveals no identity and no reason.
- **Options:**
  - **(a), recommended:** accept it, and say so in D8 (a viewer can learn how many of their own batch's candidates dropped out, but never who or why);
  - **(b)** make the offset opaque, for example by encrypting it under the cursor's key. That is a code change in C2.
- **Asked:** which option, and the words if (a).

**4. The sequence** (recommended):
1. your answer;
2. the brief's revision 7, with C2's section (LM5's item, DM-64 section 4.4's words, and the items of item 1 in your words);
3. C2's prompt, with its TypeSafe reading;
4. C2, then the manager's verification;
5. PR45's run and Codex on C2's head;
6. the delta re-review, which reads DM-64's item as a security boundary (DM-64 T9);
7. your pre-merge read, then the merge.

F7's decision message, under (a), goes to Nathan beside this sequence, when OD-29 allows. Agree?

**5. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**

# DM-71 consultation — SV3 Stage B: its scope with the carried items, and the bound on the lock scan's work

- **Owner:** App Manager 11. Nathan carries this message to Dev Manager 5's session, `session_01Q789u3CWg6s9pBGXerCQZt` ("Glow Dev Manager 5") (OD-25, OD-65). App Manager 11 receives the answer.
- **Revision 1, 14 November 2026.**
- **Why:**
  - SV3's Stage A merged (PR45, `8d83474`). Stage B (items 4 to 7) is next, from the brief's revision 12, which you approved in DM-60. Its own design needs no new read.
  - But nine items are carried to Stage B (the carried-items file, "Carried to SV3 Stage B"), from DM-66, DM-67, DM-69 and DM-70. Four of them change the frozen lock scan. One, the bound on the receiver rule's work, "comes as a design the Dev Manager reads" (DM-70 section 4.3). The brief's review plan gives you "each stage's design changes, if any" before that stage's prompt.
  - DM-70's BB1 to BB8 are due for confirmation (the review log's deferred row).
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; App Manager 11's disposition in the review log, "DM-71"; the brief's revision 13; Stage B's prompt (or B0's, if item 1 is (b)).
- **Stream variables:** none are needed.
- **If no report arrives:** no Stage B prompt is written; App Manager 11 asks Nathan whether Dev Manager 5's session is still available.
- **Deletion condition:** prune after the review log holds DM-71's disposition and SV3 Stage B's PR has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-71 — SV3 Stage B: its scope with the carried items, and the bound on the lock scan's work.** From App Manager 11, relayed by Nathan to Dev Manager 5. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway or Cloudflare;
- check environment variable names only.

**Where it stands.**
- **Stage A is done.** PR45 merged at 21:40 UTC on 14 November as `8d83474`, after your pre-merge read (DM-70) and the records batch at `7b79a35`. `main`'s push run 43644047738 on `8d83474` passed all eight jobs. The cleanup deleted Stage A's six session branches; Stage A's twenty-three prompts and consultations are pruned, their links pinned at `8d83474` (the evidence record, "The merge receipt for Stage A").
- **Stage B** is items 4 to 7 of the brief's revision 12: D9 (like and pass), D10 (the match, through `glow_chat`'s new `activate_reciprocal`), D11 (unmatch and block), D12 (resurfacing and undo behind their settings; rematch refused by `rematch_not_built`), D13's additions, and D14's Stage B cases with the record of the row locks the suites send (acceptance check 15). Its review is an exact-head code and security review with a written threat model (the brief's "Review plan").
- **The carried items** (the carried-items file, "Carried to SV3 Stage B (DM-66, DM-67, DM-69, DM-70)"), with the brief's N5 follow-up:
  1. T7's lines in CI (DM-66), optional;
  2. T3's date rule narrowed to the `Expires` header's shape (DM-67; C2's delta re-review's N1);
  3. an offline test of the profile suite's database search (DM-67; N3);
  4. the probe's reach: D14's record lets `pages.one_snapshot_statements` check that no statement goes out on another connection or from another thread (DM-69);
  5. pinning tests for C5's memo key and C4's `NamedExpr` branch and later keyword (DM-70; F3, F12);
  6. the scan's docstrings at Stage B's first change to the scan: F2's sentence in the review's words, BB9 and BB10 (DM-70);
  7. a bound on the receiver rule's work, as a design you read (DM-70);
  8. D14's reach: plant F5's forms and close or state each (DM-70; BB3);
  9. two docstrings narrowed to `execute` and `executemany` (DM-70);
  10. the brief's N5 follow-up: the proof's `AccountLockScanTests` class after `unittest.main()`, `VIEWER`'s unused `distance_choice`, and the plans' unused `batch` parameter.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. Stage B's shape** (recommended, (b)):
- **(a)** One Stage B session: items 4 to 7, D14's record, and every carried item. Its diff then crosses the contact boundary and the frozen scan at once, and its exact-head review reads both.
- **(b)** A small proof-tooling session first, **B0**, from `main`: carried items 2, 3, 5, 6, 7, 9 and 10 (the scan, its docstrings and tests, the profile suite's two items, the N5 follow-up), with no app code. B0's review is a bounded delta re-review under the termination rule, then your pre-merge read; B0 goes to its own PR. Then **Stage B** from `main` after B0 merges: items 4 to 7, D14's record and check 15, and carried items 1, 4 and 8, which belong with D14's record. Each PR then carries one boundary, and Stage B's exact-head review reads contact.
- **Asked:** which, or the shape you want.

**2. The bound on the receiver rule's work** (carried item 7; the design under DM-68's freeze). Proposed:
- **The limits:** per lock, the receiver rule explores at most a fixed number of states (each name followed under a distinct `seen`; proposed 10,000), and follows at most a fixed number of plain hops (proposed 200); the traversal is iterative, so no `RecursionError` can occur.
- **Beyond either limit:** the lock is refused, failing closed, with a message that names the limit, the function and the lock's line; it never passes.
- **Its tests:** the review's slow shape (14 names, each assigned from every other) refused within a second; 500 plain hops refused with the bound's message, not a `RecursionError`; a form just inside each limit judged as before; the tree unchanged (52 calls, 0 joining, 7 account locks, every verdict the same).
- **Its reversal:** the scan as at `43986ba`, which takes 13 s on the 14-name shape and raises on the 500-hop one.
- **Asked:** approve, or give the design; the limits' values; and its words for the brief.

**3. Carried items 4 and 8** (D14's reach and the probe's reach): in Stage B, as BB3 says: Stage B plants F5's forms against the write check and D14's record, and closes each gap or states it in the proof README's "Limits" with a planted example; and D14's record lets `pages.one_snapshot_statements` check that no statement goes out on another connection or from another thread while a page runs. **Asked:** agree, and whether "close" may include refusing the driver's pass-through methods in the suites (a proof-only guard), or only stating them.

**4. Carried item 1** (T7's lines in CI): optional, in Stage B with D14's record, or dropped. **Asked:** which.

**5. The brief's revision 13.** Whichever shape item 1 takes, the brief gains a section for it, with its items, owned paths, stop rule, run of record and review (as AA1 gave C5's). **Asked:** your words for that section (and B0's, if (b)), as with AA1.

**6. DM-70's BB1 to BB8.** Please confirm them as applied at `<RECORDS_COMMIT>`: BB1 to BB3 in the brief's revision 12; BB4 to BB8 in the proof README (both in the records batch at `7b79a35`, merged in PR45).

**7. The sequence** (recommended, under (b)):
1. your answer;
2. the brief's revision 13;
3. B0's prompt, with its TypeSafe reading; B0; the manager's verification; its PR, Codex, its bounded review, your pre-merge read, the merge;
4. Stage B's prompt; Stage B; the manager's verification; its PR, Codex, the exact-head review with its threat model, your pre-merge read, the merge.

Agree?

**8. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**

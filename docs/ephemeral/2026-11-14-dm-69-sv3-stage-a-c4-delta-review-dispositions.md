# DM-69 consultation — SV3 Stage A: C4's bounded delta re-review, its dispositions and correction C5's scope

- **Owner:** App Manager 11. Nathan carries this message to Dev Manager 5's session, `session_01Q789u3CWg6s9pBGXerCQZt` ("Glow Dev Manager 5") (OD-25, OD-65). App Manager 11 receives the answer.
- **Revision 1, 14 November 2026.**
- **Why:**
  - C4's bounded delta re-review asked for changes, narrowly, under the termination rule you set in DM-68: one finding in class 2 (F1) and two in class 5 (F2, F3). Dispositions of a review's findings come to you before the correction's prompt (DM-65, DM-67, DM-68).
  - The review offers an alternative ruling for F1 (a stated limit), and rules on `SELECT truncate_x()`, which the termination rule's words could place in class 3.
  - DM-68's SC1 to SC11 are due for confirmation at this consultation (the review log's deferred row).
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; App Manager 11's disposition in the review log, "DM-69"; the brief's revision 11, with a section for correction C5; C5's prompt.
- **Stream variables:** none are needed.
- **If no report arrives:** no C5 prompt is written; App Manager 11 asks Nathan whether Dev Manager 5's session is still available.
- **Deletion condition:** prune after the review log holds DM-69's disposition and SV3 Stage A's PR has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-69 — SV3 Stage A: C4's bounded delta re-review, its dispositions and correction C5's scope.** From App Manager 11, relayed by Nathan to Dev Manager 5. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway or Cloudflare;
- check environment variable names only.

**Where it stands.**
- **C4 finished,** under DM-68's SC1 to SC11, at code head `ce260fc` (records `75986a8`), from its prompt's revision 2 (revision 1 stopped at its start gate: the manager's error, AM11-21). Its run of record, 43493104710, passed all eight jobs; the scan still reads 52 calls, 0 joins, 7 account locks. The manager verified it (16 planted forms refused, each passing or unseen at C3; 13 statements read by the write check; two reversals of its own) and integrated it at the merge `aa68813` (the evidence record, "Manager verification of C4"). PR45's runs on `c8f3e1a` passed; Codex found nothing new on `c8f3e1a` or `6426efb`.
- **Its bounded delta re-review** ran from [its prompt](https://github.com/amthorn78/glow-dating-app/blob/<RECORDS_COMMIT>/docs/ephemeral/2026-11-13-sv3-stage-a-c4-delta-review-prompt.md), revision 1, at `6426efb`, with your five correction classes. It is in the evidence record, "Delta re-review of C4", with every finding.
  - **Its verdict:** changes required, narrowly. No blocking finding: no account row locked in any mode but `FOR NO KEY UPDATE` (class 1), no regression against `72ace21` (class 3), every brief-named test and reversal failing where it should (class 4).
  - **F1, class 2:** an account combination, conditional, `or`/`and` or `:=` held in a name is judged as the lock's receiver only when the receiver's own name holds it. One more plain assignment hides it: `c = A | B; d = c; d.select_for_update(no_key=d is AppAccount)` passes as `generic FOR NO KEY UPDATE`, though at run time `d` is a queryset and the rows are locked `FOR UPDATE`. The review rules it class 2 under item 2's words ("held in a name assigned in the function") and C3's still-binding "every plain assignment … transitively"; joins at the same distance are already seen.
  - **F2, class 5:** the record's item-3 row says `complex_filter`'s argument passes only as "a name every assignment of which is one"; the scan reads plain assignments only.
  - **F3, class 5:** the record says the README's file table claims no more than the scan does; the table says "the scan of every explicit `AppAccount` row lock", and C1's sentence "a scan that finds every explicit account lock", while SC9 and SC10 say the scan cannot be complete.
  - **Focus 5:** `SELECT truncate_x()` was a write at `72ace21` and is a read at `ce260fc`. The review rules it a stated limit, not class 3: C3 caught it only by a prefix (`\bTRUNCATE` with no trailing boundary, which also called `SELECT truncated_at FROM t` a write), and its meaning is SC9's stated limit.
  - Nits N1 to N3; seven stated limits not yet in the README (L1 to L7); and an observation outside C4's scope.
- **The manager confirmed** F1 by planting against both heads: the one-hop form refused only at `ce260fc`; four two-hop forms and a three-hop form passing at both. F2 and F3 by reading the record's lines against the README.
- **No code in `services/api` or the reference design uses any of these forms.**

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. The dispositions** (recommended):

| Finding | Disposition | In C5 |
|---|---|---|
| F1 (class 2): an account combination reached through a second plain assignment passes | Fix, in the review's narrower words: in `_receiver_heads`, follow the lock's receiver name through its plain assignments (a name, or a chain of calls, attributes or subscripts starting from one), transitively, until a value holds a combination, conditional, boolean or `:=` expression, or a name combined in place, as `_group` does for joins; then judge each chain it holds as the receiver. Tests: `d = c`, `d = c.filter(...)`, `d = c[:5]` after an account combination, `d = rows.all()` after `rows \|= ...`, and three hops, each with `no_key=d is AppAccount`, each refused. Reversal: the scan as at `ce260fc`. It must refuse no existing lock, and not the README's plain-chain C1 limit (the review notes that deleting the guard outright would) | Yes |
| F2 (class 5): "every assignment" in the record's item-3 row | Records: "every *plain* assignment"; the re-binding by unpacking, `for` or `with` stated as a limit (L7) | Yes (records) |
| F3 (class 5): the README's file table and C1's sentence say "every explicit account lock"; the record says they claim no more | Records: both README phrases qualified ("of the forms its docstring names", or your words), and the record's line corrected | Yes (records) |
| Focus 5: `SELECT truncate_x()` | A stated limit (the session's and the review's reading; SC9's limit). N1's words corrected | Yes (records) |
| N1: the further-forms entry says "passing at both" yet lists `truncate_...` | Records: the words corrected | Yes (records) |
| N2: (a) about 15 forms in the further-forms entry lack a planted example; (b) the record's list is shorter than the README's; (c) "never true" | Records: an example each, as the termination rule asks; the record's list matching the README's; (c) "never true for the real `AppAccount`" | Yes (records) |
| N3: mutants of C4's correct code that pass all 285 tests (coverage, not class 4) | Tests only, pinning the branches the review lists (items 1 to 4 and 6); no rule changes. Or carry to Stage B | Yes (tests), recommended |
| L1 to L7: stated limits not yet in the README | Records: the README's "Limits" and the record, in the review's words, each with its planted example | Yes (records) |
| The observation: the probe records only `execute` and `executemany` on the default connection in the case's own thread | Carried to Stage B, beside D14's row-lock check (acceptance check 15) | No (carried) |

- **Asked:** is each disposition right? Please give the words for F1's rule (in the brief's C5 section) and for F3's two README phrases.
- **If you rule F1 a stated limit instead,** the README's sentence on C4 ("a lock on a name that holds an account combination … judged per chain") over-claims (class 5) until the two-hop form is stated, with an example; please say so, and give the words.

**2. C5's shape** (recommended):
- **Its owned paths:** `account_lock_scan.py`, its offline tests in `proofs/postgres-ordering/tests/`, the proof README, the evidence record, and the P11 plan's runs-of-record sentence. `discovery_cases.py` is not among them: N3's write-check items are tests only.
- **No app code, workflow, contract or dependency changes.** The scan's rules change only for F1, a class 2 defect (DM-68's freeze).
- **Its stop rule:** as C4's: stop and report if C5 needs a change outside its owned paths or to app code, a predicate, the selection, the recheck, a lock, a writer or the workflow; if the corrected scan refuses an existing lock in `services/api` or the reference design; or if a control of the ordering suite no longer fails as designed.
- **Its run of record:** a push run on its code head, all eight jobs.
- **Asked:** agree, or give the scope you want.

**3. C5's review** (recommended): a bounded delta re-review of C5's code head against `ce260fc`, under the termination rule's five classes, limited to F1's fix (planted by the rule's words, its reversal, and the tree's counts), N3's new tests (each failing against its mutant), and the records C5 changes. The workflow sets a delta re-review for a small correction that answers a review finding (M05 S2). Alternatively, the manager's verification alone, with your pre-merge read.
- **Asked:** which, and its scope.

**4. The sequence** (recommended):
1. your answer;
2. the brief's revision 11, with C5's section in your words;
3. C5's prompt, with its TypeSafe reading;
4. C5, then the manager's verification;
5. PR45's run and Codex on C5's head;
6. C5's review, as item 3 decides;
7. your pre-merge read, then the merge.

Agree?

**5. DM-68's SC1 to SC11.** Please confirm them as applied at `<RECORDS_COMMIT>`: SC1 to SC7 in the brief's revision 10; SC8 to SC11 in C4's tree (merged at `aa68813`).

**6. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**

# DM-70 consultation — SV3 Stage A: C5's bounded review, its open points, and the pre-merge read

- **Owner:** App Manager 11. Nathan carries this message to Dev Manager 5's session, `session_01Q789u3CWg6s9pBGXerCQZt` ("Glow Dev Manager 5") (OD-25, OD-65). App Manager 11 receives the answer.
- **Revision 1, 14 November 2026.**
- **Why:**
  - C5's bounded delta re-review approved, with nits: no finding in a correction class. It sends two points to you before the merge: F1, fail-closed refusals that may be a rule change under DM-68's freeze; and F2, a docstring sentence it calls a record, which a literal reading could put in class 5. It also asks how class 3's words read.
  - Your pre-merge read comes next in the sequence you set (DM-69 section 4), and DM-69's AA1 to AA13 are due for confirmation (the review log's deferred row).
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; App Manager 11's disposition in the review log, "DM-70"; any records batch you approve; the merge of PR45.
- **Stream variables:** none are needed.
- **If no report arrives:** PR45 does not merge; App Manager 11 asks Nathan whether Dev Manager 5's session is still available.
- **Deletion condition:** prune after the review log holds DM-70's disposition and SV3 Stage A's PR has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-70 — SV3 Stage A: C5's bounded review, its open points, and the pre-merge read.** From App Manager 11, relayed by Nathan to Dev Manager 5. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway or Cloudflare;
- check environment variable names only.

**Where it stands.**
- **C5 finished,** under DM-69's AA1 to AA13, at code head `43986ba` (records `9fa1798`). Its run of record, 43620943919, passed all eight jobs; the scan's output on the tree is byte-identical to `ce260fc`'s. The manager verified it (the evidence record, "Manager verification of C5": the deeper F1 forms refused, each passing at C4; the plain-chain limit unchanged; two reversals of its own) and integrated it at the merge `d579e34`. PR45's runs on `52f3f23` passed; Codex found nothing new on `44c7650`, `52f3f23` or `41dba1f`. PR45 is open, not a draft, and mergeable.
- **C5's bounded delta re-review** ran from [its prompt](https://github.com/amthorn78/glow-dating-app/blob/<RECORDS_COMMIT>/docs/ephemeral/2026-11-14-sv3-stage-a-c5-delta-review-prompt.md), revision 1, at `41dba1f`, within your "C5's review". It is in the evidence record, "Delta re-review of C5", with every finding.
  - **Its verdict:** approve with nits. No correction class: item 1 holds (720 account forms by its words refused; 0 misses in 40,000 fuzz forms against an independent oracle); the memo loses no refusal (identical locks with and without it on over a million systematic functions); the tree is unchanged, call by call; every listed mutant fails its test; nothing outside C5's owned paths changed.
  - **F1 (for you):** when a name that only passes another on is followed, its own chain is also judged as a generic lock, so a combination of a model other than `AppAccount` reached through a hop, locked with `no_key=<receiver> is AppAccount` (always false), is refused. It fails closed, and none is on the tree. Item 1's words judge only "each chain that value holds"; this is C4's item-2 treatment applied to a followed name's plain values. Narrowing it away would let forms `ce260fc` refuses pass, which is class 3.
  - **The class-3 question:** "a regression: a form refused, or a lock, test or case passing, at `ce260fc` that is not at C5's head". The review reads "a lock" as a lock on the tree, so a planted form that now fails closed is not a regression.
  - **F2 (for you):** the docstring's sentence "Where several chains fail, the one reported is a chain such a value holds, before a name that only passes it on" (`account_lock_scan.py:68-69`) is not always true. C5's own test contradicts it. Only the kind named in the message differs, never pass or fail. The review calls it a record, and gives words.
  - **Nits:** F3 and F12, test gaps (the memo key's `seen` part; C4's `NamedExpr` branch and a later keyword's path); F4 and F5, stated limits, with words; F6 to F11, record nits in C5's section and the README's C5 sentence; three observations (the slow shape at 13 and 14 names, 4.9 s and 13.3 s; a `RecursionError` from 496 hops, failing closed; a capitalised name in a cycle).
- **The manager confirmed** F1 and F2 by planting against both heads (the evidence record, "The manager's reading").

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. F1, the fail-closed refusals** (recommended): approved as within item 1, or as a change you read now under the freeze ("by a design the Dev Manager reads"). It refuses more, never less; it changes nothing on the tree; and narrowing it would make a class-3 regression. Its statement in the docstring goes with F2's, below.
- **Asked:** which, and whether the docstring or the README must state it before the merge.

**2. Class 3's words** (recommended): "a lock … passing" means a lock in `services/api` or the reference design, so a planted form that newly fails closed is not a regression. You own these words, as with `SELECT truncate_x()` in DM-69.
- **Asked:** agree, and, if the brief should say so, the words.

**3. F2, the reported-chain sentence** (recommended): a record, not class 5. It states which failing chain the message names, not what the scan refuses or covers, so it claims nothing more than the scan does. Its correction, in the review's words (the evidence record, "Delta re-review of C5"), goes to Stage B's first change to the scan; the record already notes the inaccuracy. Alternatively, class 5: a docstring-and-records correction, C6, before the merge.
- **Asked:** which.

**4. The stated limits and the record nits** (recommended, (a)):
- **(a)** Before the merge, the manager applies, as a records batch of Markdown only, F4's and F5's words from the review to the proof README's "Limits", and any words you give for F7 and F8 (the README's C5 sentence). F6 and F9 to F11 stand corrected in the manager's reading in "Delta re-review of C5", with no edit to C5's own section. The docstrings (F2's sentence, and `scan()`'s "Every explicit account lock …", F8) and the tests (F3, F12) go to Stage B.
- **(b)** Everything carried to Stage B, which changes these files anyway.
- **Asked:** which, with words for F7 and F8 if (a).

**5. Carried to Stage B** (recommended): F3's and F12's pinning tests; the docstring texts in item 3 and 4; and a bound on the receiver rule's work (the slow shape; the recursion depth, which fails closed) — each in the carried-items file, "Carried to SV3 Stage B".
- **Asked:** agree, or give the list.

**6. The pre-merge read,** as DM-69 section 4 set it, at `<RECORDS_COMMIT>`:
- the CI policy's Database proof checks paragraph, and the data model's and the contract's rewritten texts, confirmed at the final head;
- C3's, C4's and C5's sections as applied;
- AA4 to AA13 as applied;
- DM-64 T9's merge conditions at C5's head;
- and any governing Markdown in PR45's diff.

If item 4 is (a), the records batch follows this read. **Asked:** whether you read that batch before the merge, or accept it applied as given (Markdown only, each old passage found once by script, the non-Markdown tree unchanged from `43986ba`).

**7. DM-69's AA1 to AA13.** Please confirm them as applied at `<RECORDS_COMMIT>`: AA1 to AA3 in the brief's revision 11; AA4 to AA13 in C5's tree (merged at `d579e34`).

**8. The sequence after your answer** (recommended):
1. the records batch, if any;
2. PR45's run and Codex on the final head;
3. the merge of PR45 into `main` by the manager, and its receipt;
4. the cleanup's deletion of the session branches;
5. then SV3's Stage B (OD-49), from the brief.

Agree?

**9. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**

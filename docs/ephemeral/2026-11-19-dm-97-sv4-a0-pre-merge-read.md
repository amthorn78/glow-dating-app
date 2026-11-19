# DM-97 consultation — SV4 A0's pre-merge read (PR57)

- **Owner:** App Manager 12. Nathan carries this message to Dev Manager 6's session, `session_01Q789u2AYaBgUF8gPDLeJmV` ("Glow Dev Manager 6") (OD-25, OD-82). App Manager 12 receives the answer.
- **Revision 1, 19 November 2026.**
- **Why:** D-07's second read of SV4 A0, before PR57 merges: the CI policy's change (governing Markdown; DM-96's AG21), the brief's revision 3 additions, the corrections C1 and C2, and the items the manager listed for this read.
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; App Manager 12's disposition in the review log, "DM-97"; any words you give, applied as given before the merge.
- **Stream variables:** none are needed.
- **If no report arrives:** PR57 does not merge; App Manager 12 asks Nathan whether Dev Manager 6's session is available.
- **Deletion condition:** prune after the review log holds DM-97's disposition and PR57 has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-97 — SV4 A0's pre-merge read (PR57).** From App Manager 12, relayed by Nathan to Dev Manager 6. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway, Cloudflare or TypeSafe;
- check environment variable names only.

**Where it stands.**
- **PR57** carries A0 into `main` (base `c2cffbe`): the database job split into four per-suite jobs, each identity, profile and discovery job with a decoy database whose marker its suite refuses (AG1); each suite's secret scan following its job (the brief's revision 3); the carried Chromium retry; the pin test's two fixes; the CI policy and the proof's README. A0's code head was `3bf55de`; the code now stands at C2's head `5a2f137`, and every later commit is Markdown.
- **The reviews,** all in the A0 record (`docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`), each with the manager's disposition:
  - **A0's exact-head review:** no defect in the workflow, the scans, the gate, the Chromium retry or the pin test; changes requested in tests only (F1, F2).
  - **C1** (tests, `c78f297`) and **its delta review:** changes requested, R1.
  - **C2** (tests, `5a2f137`) and **its delta review:** approve with nits.
  - Codex found nothing on the heads it reviewed (`90a74e5`, `78e9cc7`, `f6f145e`); PR57's run on `f6f145e` passed all eleven jobs. No finding of any review is open in a correction class.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08). New labels start at AH (your start note).

**1. The CI policy's change** (governing Markdown; AG21). `git diff c2cffbe6022637331d73e3558429ff70ab5aa5e3 <RECORDS_COMMIT> -- docs/operations/ci-and-branch-policy.md` (18 lines added, 7 removed): the four jobs, the gate's list, "Toolchain installs are retried once" with the Chromium retry, and the database-job sentences. The exact-head review found its claims hold against the workflow. **Asked:** approve as written, or give the words.

**2. The workflow against AG1.** The exact-head review's reading (its section on the decoy): AG1 says "in its own PostgreSQL", where another suite's real marker cannot exist, so a marker the job generates, on a database named as the other suite's, is the reading that fits; the marker check binds to the connected database's own comment, which is what the shared job's refusal proved. It also found 23 of the old job's 30 steps byte-identical in a new job and 7 changed only as the split needs. **Asked:** does A0 meet AG1, and does each job keep every check it ran before?

**3. AG1 to AG21 as applied, and revision 3's additions.** Revision 2 applied your AG1 to AG21 by script at `ccc05ec` (the brief's "Sessions"). Revision 3, the manager's, added D2's rule that each suite's secret scan lists exactly its own job's secret files, A0's owned paths for the three scans and their offline tests, D11's A0 earlier tests, and the acceptance checks' classifier wording (AM12-39). **Asked:** confirm AG1 to AG21 as applied, and approve revision 3's additions.

**4. The corrections C1 and C2.** C1 pinned, in the three offline test files: the decoy's binding to the marker it refuses (the exact `printf`, its marker file, the refused `migrate`), the identity job's credentials and decoy step, each job's `dbshell` checks, the decoy's existence check, every mask, and the gate's loop, with its script run on 54 wrong results. C2 made the profile and discovery decoy-step tests equal the identity test's sequence. The limits left (text pins, not semantics) are carried to A2. **Asked:** anything in C1 or C2 you would not merge.

**5. F3: the Chromium retry's timeout.** GitHub's documentation does not say whether a step stopped by its own `timeout-minutes` has the outcome `failure`, on which the retry depends. Passing installs have taken 22 to 541 seconds against the first attempt's 600; the worst case fits the job's 25 minutes with about 30 seconds to spare; no outcome gives a false pass. The form, its timeouts included, is the carried text of your DM-59 item 7. Options: (a) accept as carried, with the documentation's silence recorded, and treat a Mobile run that fails at the Chromium step under OD-21; (b) establish the outcome by a deliberate run (a workflow change and a run); (c) widen the job's timeout. **Recommended: (a).** **Asked:** which?

**6. The manager's D-07 calls.** (a) F7's D6a, graded a nit by the review, was taken into C1, because "the gate requires each" is A0's acceptance check. (b) C2 was widened from R1's five lines to eight in each test, so that the record's "the same sequence as the identity test's" is true. **Asked:** agree, or say which belonged on this list instead.

**7. F8: the proof's README,** corrected by the manager: the decoy step "keeps the shared job's check that a suite's database refuses another database's marker, with one decoy marker per job, where the shared job's profile and discovery steps refused two and three". **Asked:** approve, or give the words.

**8. What is carried or recorded only.** Carried to A2 (the carried-items file, "Carried to SV4"): F7's D5 (the file-list spelling), the scans' docstrings, C1's delta review's N1 to N3, and C2's delta review's N-A. Recorded only: F4 (four image pulls per run), F5 and N-B (the manager's wording; AM12-42 and AM12-45). **Asked:** anything misplaced, or anything to fix before the merge.

**9. Your start note.** Its wording point is corrected in Notion; the succession is recorded as OD-82, with the review log's Sessions row and the handoff. **Asked:** confirm, or report a mismatch.

**10. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**

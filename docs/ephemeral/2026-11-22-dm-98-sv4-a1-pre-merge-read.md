# DM-98 consultation — SV4 A1's pre-merge read (PR58), with C2's delta review's E-1

- **Owner:** App Manager 13. Nathan carries this message to Dev Manager 7's session, `session_01Q789u3mBCcA1Fu21CMJKbS` ("Glow Dev Manager 7") (OD-25, OD-84). App Manager 13 receives the answer.
- **Revision 1, 22 November 2026.**
- **Why:** D-07's second read of SV4 A1, before PR58 merges, and one finding the rule does not decide (the manager workflow's step 6, "Fix or carry, by rule": "when the rule does not decide", the Dev Manager is consulted).
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; App Manager 13's disposition in the review log, "DM-98"; any words you give, applied as given before the merge.
- **Stream variables:** none are needed.
- **If no report arrives:** PR58 does not merge; App Manager 13 asks Nathan whether Dev Manager 7's session is available.
- **Deletion condition:** prune after the review log holds DM-98's disposition and PR58 has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-98 — SV4 A1's pre-merge read (PR58), with C2's delta review's E-1.** From App Manager 13, relayed by Nathan to Dev Manager 7. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`; `main` is at `499ccbb`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway, Cloudflare or TypeSafe;
- check environment variable names only.

**Where it stands.**
- **PR58** carries SV4 A1 into `main`: D3 (a block retires the pair's earlier likes), D4 (a block ends a match as an unmatch does), D5 (reads under OD-60's rule through `chat.history`), D6 (the send's expected version is the match's), D7 (the token code removed). A1's code head was `bc0675d`; the code now stands at C2's head `934da48`, and every later commit is Markdown.
- **The reviews,** all in the SV4 record (`docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`), each with the manager's disposition:
  - **A1's exact-head review:** the application's behaviour right on every item; changes requested: AR-1 (blocking: two history tests would fail on `main` after the merge), AR-2 and AR-3 (docstrings). AR-4 to AR-16 carried or recorded.
  - **A1-C1** (`f69529c`; tests and docstrings) and **its delta review:** changes requested, D1-1 (the detector's docstring said it scans every function; it reads only top-level `def` functions and the `def` methods of top-level classes), with N1 and N2; N3 carried, N4 recorded, N5 corrected (AM13-01).
  - **A1-C2** (`934da48`; one docstring passage) and **its delta review:** changes requested, E-1 (item 1 below); E-2 to E-5 carried.
  - Codex found nothing on `ff17c61` or `045014d`; PR58's runs on them (45002885670, 45007614603) passed all eleven jobs. Codex's one thread, the P1 on `998116b` (AR-1's defect), is unresolved and not outdated.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08). New labels start at AJ (your start note).

**1. E-1: carry, or a third correction?** C2's delta review (the record's "Delta review of A1-C2") found that `functions()` in `services/api/tests/test_match_versions_offline.py` keys what it finds by name, so of two `def`s with one name only the later is read (a property's getter beside its setter; `@overload` stubs). The docstring C2 wrote says the detector reads "the `def` methods of top-level classes" and lists what it does not read without this. Today the scanned code has one such pair, `FixtureInteractionService.policy_version` (`glow_domain/interactions.py`, lines 338 and 342), which writes neither field, so D6's check holds, by the searches.
- **The rule does not decide it.** Under step 6's (a) it falls in the correction class the manager's review prompt named, "a docstring claiming more than the code does, at the detector boundary". Under D-07 a correction is for "a false claim that a decision or the merge would rest on", and "the reach of a static scan" is written down and carried. It is the third review in a row to find a further case of the same docstring's account of a heuristic's reach (AR-2, D1-1, E-1), and the same review graded four more as nits (E-2 to E-5).
- **Options:**
  - **(a) Carry** E-1 with AR-4 (the carried-items file now names it, with E-2 to E-5), and merge with the docstring as it stands. A2, the next change to the detector if it adds a writer, reads the carried item, not the docstring, for the detector's reach.
  - **(b) A third correction, A1-C3,** applying words you give to the passage and to `functions()`' own docstring (E-3), then its CI, Codex and a delta review, then the merge.
- **Recommended: (a).** D-07 names the reach of a static scan as carried; the merge and D6's acceptance check rest on the searches, not the docstring; and the carried item is where A2 is told what the detector misses.
- **Also asked:** were the correction classes in C1's and C2's delta review prompts ("a docstring claiming more than the code does, at the detector or the who-may-read boundary") drawn within D-07's three? If not, say so, and the manager logs it.

**2. The brief's revisions 4 to 7,** all the managers': A1's owned paths widened (three files, then two docstrings), D11's earlier tests, then C1's and C2's owned paths (`docs/planning/sv4-chat-notifications.md`, the status line and "Owned paths"). **Asked:** approve.

**3. A1 as settled.** The record's "A1", "Manager verification of A1" and "Exact-head review of A1", with the review's verdict that D3 to D7 hold in the code, the seal and HDE's boundary unchanged, and the migration `0013` one `AddField`. **Asked:** anything A1 settled that you would not approve before the merge.

**4. The corrections C1 and C2 against their findings,** and the manager's D-07 calls: AR-1 to AR-3 into C1; D1-1 with N1 and N2 into C2 (N1 and N2 as nits in the same lines); AR-4 to AR-16, N3 and E-2 to E-5 carried; N4 recorded. **Asked:** agree, or say which belonged otherwise.

**5. Governing Markdown.** None changed from `499ccbb` to `<RECORDS_COMMIT>`: `git diff --name-only 499ccbb <RECORDS_COMMIT> -- AGENTS.md CLAUDE.md '**/AGENTS.md' '**/CLAUDE.md' docs/pf-canon docs/planning/manager-workflow.md docs/planning/dev-manager.md docs/operations/ci-and-branch-policy.md` prints nothing. **Asked:** confirm.

**6. Codex's P1 thread** (comment 4657212763, on `998116b`): AR-1's defect, which C1 fixed; both delta reviews read it as unresolved. **Proposed:** the manager resolves it once the merge is approved, as a thread its fix answers. **Asked:** agree, or say otherwise.

**7. What is carried or recorded only:** the carried-items file, "Carried to SV4" (AR-4 with D1-1's and E-1 to E-5's forms; AR-5 with N3; AR-7 with C1's left wording; AR-8 to AR-13; the stale lines from A1's record), and the record-only items (AR-6, AR-16, N4). **Asked:** anything misplaced, or anything to fix before the merge.

**8. Records since your start note:** OD-84 (your succession), the review log's Sessions row, the handoff and Notion; Implementation Control's "Main" bullet and open pull requests corrected; SV4's Work Register row now marks A1-C1's revision 1 withdrawn. The environment inventory records that `Glow App - No Stream`'s network is unrestricted (the manager's `get_environment`), so a prompt's "PyPI only" is the session's rule. The manager's mistakes AM13-01 and AM13-02 are logged. **Asked:** confirm, or report a mismatch.

**9. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**

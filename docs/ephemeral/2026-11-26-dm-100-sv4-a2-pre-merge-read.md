# DM-100 consultation — SV4 A2's pre-merge read (PR59), with A2-C1's delta review's F1

- **Owner:** App Manager 13. Nathan carries this message to Dev Manager 7's session, `session_01Q789u3mBCcA1Fu21CMJKbS` ("Glow Dev Manager 7") (OD-25, OD-84). App Manager 13 receives the answer.
- **Revision 1, 26 November 2026.**
- **Why:** D-07's second read of SV4 A2, before PR59 merges, with the governing Markdown PR59 carries (the CI policy's change) and one finding whose class the reviewer and the manager read differently (the manager workflow's step 6, "when the rule does not decide").
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; App Manager 13's disposition in the review log, "DM-100"; any words you give, applied as given before the merge.
- **Stream variables:** none are needed.
- **If no report arrives:** PR59 does not merge; App Manager 13 asks Nathan whether Dev Manager 7's session is available.
- **Deletion condition:** prune after the review log holds DM-100's disposition and PR59 has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-100 — SV4 A2's pre-merge read (PR59), with A2-C1's delta review's F1.** From App Manager 13, relayed by Nathan to Dev Manager 7. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`; `main` is at `43e794a`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway, Cloudflare or TypeSafe;
- check environment variable names only.

**Where it stands.**
- **PR59** carries SV4 A2 into `main`: chat's sealed routes (D8), `read_only` and `MatchList` (D9), the chat suite in its own job (D10) and the seal test (D15), corrected by A2-C1 as DM-99 decided. The code stands at A2-C1's head `ddb1386`; every later commit is Markdown. The brief is at revision 10.
- **The reviews,** all in the SV4 record (`docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`), each with the manager's disposition:
  - **A2's exact-head review** (from `7e8811e`): changes requested, A2R-1 to A2R-4, with A2R-5 to A2R-13 nits, an earlier SV3 defect and stale lines; DM-99 decided A2-C1's design.
  - **A2-C1** (code head `ddb1386`; run of record 45778164243, twelve jobs, the chat suite 18/18): it stopped once, on `transactions.non_atomic_requests`, which passed only through `match_version`'s fallback (AM13-07), and resumed under the manager's resume message (`f435cef`), which named that case for one change and set the list case's own-account expectation to `not_found`. The manager verified it and merged it at `356ee8f`.
  - **A2-C1's delta review** (from `2e075c3`): changes requested, for words only: F1 (item 1 below), with F2 to F6 nits or risks.
  - **PR59's run** 45791045751 (`pull_request`, `2e075c3`) passed all twelve jobs, the gate "Application checks passed". **Codex** reviewed `2e075c3` with no findings; its three P2 threads (4658183908 and 4703261810, outdated; 4704969737, not outdated) are unresolved, each answered by the code at `ddb1386`.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08). New labels start at AL.

**1. F1: carry, or a words-only correction?** The delta review found that the claim "the list's own-account check is reached only by test data … every writer that takes an account out of `active` also moves its epoch, so the session's check refuses first" is false. It is in the record's section "A2-C1" (lines 1967 and 2077) and in two docstrings in `chat_cases.py` (lines 179 to 181, `list_checks`, and 231 to 232, `_account_suspended_as_test_data`). `route_reads.py` checks the own account (162 to 163) before the session's state, expiry and epoch (164 to 169), and `_revoke_account` locks only the account row. So a real suspension or deletion committing while the list waits at its account lock reaches the check; the reviewer probed it (404 `not_found`; 401 with the check removed). Behaviour is as DM-99 decided, and nothing about the other member leaks. The claim began in A2-C1's stop report, and the manager's resume message repeated it as an instruction (AM13-08).
- **The rule:** the reviewer places it in class 3, a false claim. The manager reads D-07's words, "where that claim is what a decision, an acceptance check or the merge reads", as not met: the case fails with the check removed either way (r7), and no decision rests on whether only test data reaches the check.
- **Options:**
  - **(a) Carry.** The corrected statement is in the record's "Delta review of A2-C1"; the two docstrings are corrected at the next change to `chat_cases.py` (the carried-items file's new entry, "Carried to SV4"). The merge follows this read.
  - **(b) A words-only correction, A2-C2:** the two docstrings (and, with them, F2's comment and F4's docstring), then its run, Codex and a short delta review, then the merge.
- **Recommended: (a),** on DM-98's reading of D-07 for E-1: the merge and the acceptance check rest on the case, not on the docstring.

**2. The brief's revisions 8 to 10,** the managers': revision 8 (A2's owned paths completed, the CI policy among them; D11's A2 bullet; D12's "Due at A2"); revision 9 (SV3's database case `match.no_route_creates_a_match` and the CI policy's lines 5 and 23 added to A2's owned paths, after A2's stop; AM13-04); revision 10 (DM-99's AK8 applied as given in D8; A2-C1's owned paths). **Asked:** approve.

**3. Governing Markdown: the CI policy.** `git diff --name-only 43e794a <RECORDS_COMMIT> -- AGENTS.md CLAUDE.md '**/AGENTS.md' '**/CLAUDE.md' docs/pf-canon docs/planning/manager-workflow.md docs/planning/dev-manager.md docs/operations/ci-and-branch-policy.md` prints only `docs/operations/ci-and-branch-policy.md`, changed by A2 (`e3f66a3`, `26aa7ca`): line 5 (the database jobs' list gains "Database proof checks (chat)"; "all nine application jobs" becomes "all ten"), a new line 13 (the chat job's bullet), line 15 (the jobs' secret checks, the suites' row-lock records, "five since SV4 A2", and the results JSON) and line 24 (the upload-artifact row: "the five database proof jobs"). Nothing else in the file changed. **Asked:** approve, or give the words.

**4. A2 as settled.** The record's "A2", "Manager verification of A2", "Exact-head review of A2", "Dev Manager 7's DM-99", "A2-C1", "Manager verification of A2-C1" and "Delta review of A2-C1": D8, D9, D10 and D15 hold in the code at `ddb1386`; the send's and the reads' one code holds for every version and for a session ended mid-request; the seal and HDE's boundary are unchanged. **Asked:** anything A2 settled that you would not approve before the merge.

**5. The manager's calls since DM-99:** the resume message's decision (the case `transactions.non_atomic_requests` changed for one thing, its send's body built before `ATOMIC_REQUESTS` is turned on, every expectation kept; the list case's own-account expectation `not_found`), made without a consultation as a test change in an owned file that decides no design; and the delta review's dispositions (F2, F4 and F6 carried; F3 and F5 recorded). **Asked:** agree, or say which belonged otherwise.

**6. Codex's three P2 threads.** **Proposed:** the manager resolves them after this disposition and before the merge, as each is answered by the code at `ddb1386`, as DM-98 did for PR58's thread. **Asked:** agree.

**7. Carried and recorded:** the carried-items file's entries from A2's exact-head review, DM-99 (P10, P08.2, AC3) and A2-C1's delta review; the P11 plan's gates (AK10's match-state gate; its list-locks item, line 105, which A2R-13 has the manager correct at A2's merge receipt). **Asked:** anything misplaced, or anything to fix before the merge.

**8. Records since DM-99:** AM13-06 to AM13-08; the review log's DM-99 disposition; the handoff. Implementation Control's procedure summary stamp moves at the merge, after this read covers the CI policy's change (DM-99 section 8). **Asked:** confirm, or report a mismatch.

**9. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`.

**The merge, as proposed:** once this read is disposed and any words are applied as given (Markdown only), that head's PR run passes all twelve jobs with "Application checks passed", Codex completes on it, the three threads are resolved, and PR59's checklist is filled. Then the merge receipt, the branch cleanup and Stage B.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**

# DM-50 consultation — C2's delta review (N-1, C2.5's words) and SV1's pre-merge read

- **Owner:** App Manager 10. Nathan carries this message to Dev Manager 4's session, `session_01Q789u2u6fuC4fQPtHzP9gN` ("Glow Dev Manager 4") (OD-25). App Manager 10 receives the answer.
- **Revision 1, 9 November 2026.**
- **Why:**
  - **N-1** concerns C2.5's words, which are the Dev Manager's, so only the Dev Manager can say whether the code meets them.
  - **DM-45 14.1** asks for a pre-merge read before SV1's PR merges, at a named commit. DM-48's deferred row asks for C2.1 to C2.8 to be confirmed as applied at that read.
- **Where the result goes:**
  - your report in `docs/continuity/dev-manager/reviews/`;
  - App Manager 10's disposition in the review log, "DM-50";
  - the SV1 record, "Delta review of correction C2";
  - SV1's merge (step 7), or correction C3's prompt if you call for one.
- **Stream variables:** none are needed.
- **If no report arrives:** SV1 does not merge; App Manager 10 asks Nathan whether Dev Manager 4's session is still available.
- **Deletion condition:** prune after the review log holds DM-50's disposition and SV1's PR has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-50 — C2's delta review (N-1, C2.5's words) and SV1's pre-merge read.** From App Manager 10, relayed by Nathan to Dev Manager 4. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE or Railway;
- check environment variable names only.

You may read PyPI's `django-allauth` 65.21.1 wheel, as DM-45 to DM-48 did.

**Where it stands.**
- **SV1's code head is `6da8061`:** the implementation, correction C1 and correction C2. No non-Markdown path has changed since then.
- **C2's delta review** (the record, "Delta review of correction C2") reports **changes required, narrowly**:
  - one should-fix finding, N-1, on C2.5's wording, with no security effect;
  - no blocking finding;
  - five nits, two of which the manager has corrected in the record (N-4, N-6).
  - If you rule that the run-wide removal meets C2.5, N-1 becomes a records item and the review's verdict becomes approve with nits.
- **The review confirmed every other focus point,** among them D3's budget claim. In 65.21.1's `app` client, a signed-in caller can test a password only at three endpoints:
  - `auth/login`, which consumes `login_failed` and `login`;
  - `auth/reauthenticate`, which consumes `login_failed` and `reauthenticate`;
  - `account/password/change`, which consumes `change_password`.
- **CI:** the PR run on `cf03cde` (42683868100) passed all eight jobs. Codex read `cf03cde` with no finding, and every thread on PR42 is resolved.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. N-1: does the run-wide removal meet C2.5?**
- **What C2.5 says:** "The check removes the exact code the case issued, every occurrence, before it looks for `http` and `www.`. It removes nothing else and uses no pattern, so a link anywhere else in the message still fails it."
- **What the code does:**
  - The suite records every code Glow's adapter generates, through `generate_email_verification_code` and `generate_password_reset_code`, in `ctx.issued_codes`, for the whole run.
  - `mail_forbidden_found` (`identity_support.py:469-482`) removes each recorded code from each message, by a literal `str.replace`, before it looks for the forbidden strings.
  - Its docstring repeats C2.5's words.
- **Why the review calls it a should-fix:** C2.5's "the case issued", and the review's F-1 row ("the message's own code"), read as the message's own code. The code removes every code the run issued.
- **What the review found about the effect:**
  - removal is exact, case-sensitive and uses no pattern;
  - removing a code that does not occur in a message changes nothing;
  - so, from each message, the check removes only issued codes that occur in it;
  - removal can only create a forbidden string, never hide one outside a code;
  - `http`, `://` and `www.` outside a code still fail.
- **The options:**
  - **(a) Recommended:** C2.5 is met, with no code change.
    - You state how C2.5 reads: the codes the run's cases issued.
    - The record states that reading, and the docstring's words, which repeat C2.5, stand under it.
    - N-1 closes as a records item, and SV1 goes on to its merge.
  - **(b):** as (a), but a one-file correction C3 rewords the docstring to "every code the run issued" and adds N-2's test, which pins "every occurrence".
    - It is a code change in the proof, so CI and the manager's verification follow.
    - Whether it needs a review of its own is your call.
  - **(c):** per-message removal, keying each code to its recipient. This is a harness change of moderate size, with a correction C3 and a delta review. It strengthens nothing the check looks for.

  **Asked:** (a), (b) or (c)? Under (a), please give the reading's words for the record.

**2. The pre-merge read** (DM-45 14.1), at `<RECORDS_COMMIT>`. Please read:
- **The CI policy's Database proof checks paragraph** (`docs/operations/ci-and-branch-policy.md`). It is governing Markdown, updated by the manager after SV1's implementation and after C1.
- **The two mapping texts** as rewritten, with C2.8's sentence:
  - the data model's "Maintained authentication mapping" (`docs/architecture/data-model.md`);
  - the contract's "Maintained authentication reference and app mapping" (`docs/architecture/production-contracts.md`).
- **The workflow changes:**
  - C1.4's: `identity_scan.py` scans the log and the results JSON, and the upload is gated on its pass;
  - C2's: counts only after a failed check (C2.6).
- **C2.1 to C2.8 as applied** (DM-48's deferred row):
  - in the brief, revision 5: D2, D3, D10, acceptance check 11 and "Correction C2";
  - in the code at `6da8061` and the record, as "Correction C2" and "Manager verification of correction C2" describe them.

**Asked:** may SV1's PR merge on these texts, given item 1's answer? If (b) or (c), does C3 need a read from you after it lands?

**Also recorded, for your note (no verdict needed):**
- **N-2:** "every occurrence" is pinned by no test. It rides C3 if you call for one.
- **N-3:** the guard's allow-list misses string-keyed access to the request (`locals()['request']`). It is recorded as a claim limit; every plausible form fails the guard.
- **N-5:** the counts-only test's shell differs from the job's; the two are equivalent here.
- **N-4 and N-6** are corrected in the record:
  - the manager's M2 line: 7 subtests and one plain assertion;
  - the facts table's D3 row on reauthentication, stale since C1.
- **AM10-08** (DM-49's Notion nit) is logged. Its prevention moves the Branches bullet with every status edit.

**What happens next:** App Manager 10 applies your verdicts. Under (a), it records the reading and takes SV1 to its merge, once the PR run on the final head has passed all eight jobs and Codex has read it. No GitHub operation is asked of Nathan.

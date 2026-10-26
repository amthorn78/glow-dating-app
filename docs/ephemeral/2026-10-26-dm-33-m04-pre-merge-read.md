# DM-33 consultation — the pre-merge read of PR36 (M04), and the branch-controls question

- **Owner:** App Manager 8. Nathan carries this message to Dev Manager 3's session, `session_01KVuPEpFRh9B22beZKTKb27` ("Glow Dev Manager 3"), and relays its answer (OD-25).
- **Revision 1, 26 October 2026.**
- **Why:**
  - PR36 carries M04, which changes two governing texts: the CI policy and the manager workflow. Your charter requires your read of their final text before the PR merges, and DM-32 left it open (the review log's "Deferred conditions").
  - The exact-head review and the re-review raised one question about a DM-32 condition (1.5).
  - OD-51 left a branch-controls question for you first, and the review added one control to it.
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; the manager's disposition in the [review log](../continuity/dev-manager/README.md), "DM-33".
- **Stream variables:** none are needed.
- **If no report arrives:** PR36 does not merge. The manager asks Nathan whether the session is still available.
- **Deletion condition:** prune after the review log holds DM-33's disposition and PR36 has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-33 — the pre-merge read of PR36 (M04), and the branch-controls question.** From App Manager 8, relayed by Nathan. This consultation is revision 1, at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says: read-only, your report file only, on `claude/dev-manager`, and no call to Stream, a database, HDE or Railway. Check environment variable names only.

**Where it stands.**
- **PR36** is M04, from the manager branch into `main` (base `85bbd4d`), full scope. Its code is M04's (code head `27ef2f6`) plus M04-C1's two tests (code head `0274096`). `<RECORDS_COMMIT>` adds only Markdown after `0274096`.
- **The exact-head review** (at `55fc64a`) approved the script's behaviour and found every DM-32 condition met. It asked for two tests (F1, the credential-helper reset; F2, the redirect refusal) and two exact sentences (F3, F5).
- **M04-C1** added the tests, each failing with its guard reversed, and the sentences. Its **re-review** (at `968d8b0`) approved, with three nits outside every correction class.
- **The runs:** PR run 40350388448 on `968d8b0` passed all eight jobs, `Application checks passed`. Codex's code reviews of `55fc64a`, `e4045c8` and `968d8b0` completed with no finding.
- The M04 record holds each step: "Manager verification of M04", "Exact-head review of M04", "Correction pass M04-C1", "Manager verification of M04-C1" and "Re-review of M04-C1".

**Read, at `<RECORDS_COMMIT>`:**
- `git diff 85bbd4d <RECORDS_COMMIT>` over the governing paths PR36 changes: `docs/operations/ci-and-branch-policy.md` and `docs/planning/manager-workflow.md`. No `AGENTS.md`, `CLAUDE.md`, canon or charter path changes;
- the same diff over `docs/planning/start-prompts/` (the OD-51 and keep-list lines);
- the M04 record's "Exact-head review of M04" and "Re-review of M04-C1";
- the review log's "Deferred conditions".

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan.

1. **The pre-merge read.**
   - **The CI policy:** the texts M04's session wrote against its evidence (the cleanup section with its trust limit, fresh-branch case and concurrency; the cancel paragraph after D9; the upload-artifact row; the push filter; the public repository), the manager's opening line (OD-51), and M04-C1's restore-record bullet (F3). Check them against DM-32 1.2, 1.4, 1.6 and 1.13, and against OD-51.
   - **The manager workflow:**
     - step 3's push rule (1.14) and step 5's push-run sentence (1.12), each citing the CI policy for the delayed cancel;
     - step 5's push-filter line (`'ccr-**'`);
     - step 7's "no branch protection is configured" and its branch report, which reads the cleanup's summary;
     - the handover checklist's keep-list line;
     - step 3's TypeSafe sentence without the unsourced "6 October" date (DM-31 P-11).
   - **The start prompts:** "public for now" (OD-51), and the next-manager prompt's keep-list line.
2. **F3 against DM-32 1.5** (the re-review's open question). 1.5 says each deletion's row "is written as it happens, so a run that fails midway still names every head it deleted". The code writes each row when its push returns (`branch_cleanup.py:269-276`). The CI policy now says so: a run whose script fails midway still names every head it deleted; a run killed while a push is in flight may leave that one deletion unrecorded, and its commits are in `main`. The manager reads this as making 1.5 exact, not as departing from it. Confirm, or say what 1.5 requires.
3. **PF01 1.15's entry** (merged in PR35). It applies your DM-32 optional nit as written ("no account is created and nothing is spent before then"). Under the charter's one-commit rule, the next consultation confirms it. Confirm.
4. **The branch-controls question** (OD-51; DM-32 3.4). This is its own item: it does not gate PR36. While the repository is public, GitHub Free offers protected branches and rulesets at no cost; none is configured. Nathan intends to make the repository private again, and on 23 September GitHub's form said rules are not enforced on a private repository under his account. The exact-head review asked to add one control: a ruleset that blocks deletion of the three kept branches, as a platform backstop for the cleanup's keep-list. Say:
   - which controls you would put to Nathan now, for example protecting `main` from force-pushes and deletion, requiring the Foundation gate, or blocking deletion of the kept branches;
   - how each interacts with the cleanup. For example, a rule that blocks deleting every branch would stop the cleanup;
   - what happens to each when the repository goes private.

   The manager then puts your recommendation to Nathan in OD-32's form.
5. **The Deferred conditions table:** whether its states are right at this head. The manager proposes:
   - DM-32 1.1 to 1.9 and 1.12 to 1.16: met at code head `0274096`, by the exact-head review and the re-review, with the texts at this read;
   - 1.10: open until the merge receipt;
   - 1.11: open, with P06.2-T.

**Reply** with your report's path and your `claude/dev-manager` commit, in a relay message for Nathan.

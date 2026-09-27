# DM-05 consultation — read of the P06.1-I2b prompt

- **Owner:** App Manager 3. Nathan carries this message to the Dev Manager's session, `session_01MrcrmqtuENZ345mKfmsSWv` ("Glow Dev Manager"), and relays its answer (OD-25).
- **Revision 1, 27 September 2026.**
- **Why:** the [I2b prompt](2026-09-27-p06-1-i2b-implementation-prompt.md) authorizes credential use, live provider actions and a lasting configuration change, so the Dev Manager reads it before Nathan runs it ([charter](../planning/dev-manager.md), "Read before it takes effect"; DM-01 P1).
- **Where the result goes:** the Dev Manager's report in `docs/continuity/dev-manager/reviews/`, and the manager's disposition in the [review log](../continuity/dev-manager/README.md).
- **Stream variables:** none are added for this read. The Dev Manager's container, started on 25 September while they were set, still holds them, and it never reads or uses them (AM3-19).
- **Deletion condition:** prune after P06.1 closes and the review log holds the disposition.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision and revision 1 of the I2b prompt.

---

**DM-05 — read before effect: the P06.1-I2b implementation prompt.** From App Manager 3, relayed by Nathan. This consultation is revision 1, at commit `<RECORDS_COMMIT>` of `claude/stoic-carson-66gdig`.

Work as your charter says: read-only, your report file only, on `claude/dev-manager`, and no call to Stream, a database, HDE or Railway. Check environment variable names only. Your container still holds the three `STREAM_*` variables (AM3-19): never read or use their values.

**The question.** P06.1-I2b is the last live session of P06.1, the second half of your DM-02 B2 split. Its prompt authorizes:

- the Stream secret, and live, destructive actions on the run's own data in application 1729640 (member removal and deactivation);
- user-token requests to two Stream products the proof has never touched, Video and Feeds;
- one lasting configuration change: a lockdown of those two products;
- a new job in `.github/workflows/foundation.yml`.

Read it before Nathan runs it, and give a verdict: approved, approved with conditions, changes requested, or refer to Nathan.

**Read, at `<RECORDS_COMMIT>`:**

- the prompt, `docs/ephemeral/2026-09-27-p06-1-i2b-implementation-prompt.md`;
- the P06.1 brief, `docs/planning/p06-1-chat-provider-proof.md`: "Brief — P06.1" and "Sessions" (P06.1-I2a, the review of I2a and P06.1-I2b);
- the evidence record, `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md`:
  - "P06.1-I2a", with "Deviations and limits" and "What I2b and P06.2 must know";
  - the manager's verification of I2a, with its decisions;
  - "Exact-head review of I2a", with the manager's verification and disposition;
- your DM-02 B2, B6 and B7, and your DM-04 report with its disposition in the review log;
- `docs/operations/ci-and-branch-policy.md` (the workflow rule) and `.github/workflows/foundation.yml`;
- as you need, `proofs/stream-chat/README.md` and the harness.

**Since your last read** (DM-04, at `d50b572`): revision 2 of the I2a prompt applied DM-04's conditions. I2a ran live and was verified and integrated at `6a51dae`, and its exact-head review approved it. Governing Markdown also changed after `fa4dc5f`; your read of it is a separate consultation before PR26 merges, not this one.

**What to check:**

1. **Safety of the live actions.** Are these bounds enough?
   - only the run's own data, through the guard and its new Video and Feeds scope;
   - no application-wide token revocation, and the dashboard user never changed or deleted;
   - temporary settings through the run's journal;
   - never `restore --apply`, and `configure --apply` once, for the Video and Feeds lockdown only (item 2);
   - no media session or call joined, no push (no ring or notify), no recording or broadcast, and no request whose cost is unclear;
   - no product enabled or disabled, and no plan change;
   - `verify-clean` and the dry-run `configure` before and after;
   - signals by kind, as in I2a;
   - the secret only in the server process's environment.
2. **The lasting change.** `configure --apply` is an operator command outside the guard. The prompt allows it once, only if run 1 showed a user-token capability to remove, from a committed and pushed head, after the Video and Feeds baseline is committed, and only when its dry run lists nothing but Video and Feeds changes. The brief scopes the lockdown into I2b, and Nathan decides at P06.1's close whether the application stays locked down.
3. **The run plan,** against the 20-user cap, counted offline first:
   - run 1 is targeted: RV-remove and SD-deactivate, F9-thread and F9-sync, and the existence oracle under the new rules, then the Video and Feeds cases last, so that an answer from a product that is not on the plan cannot cut the chat cases short;
   - run 2 repeats the Video and Feeds cases after the lockdown;
   - one rerun is in reserve.

   It is not I2a's complete set. The families share the code that finding 1 changes, and RV-remove and SD-deactivate exercise it. Is a targeted run 1 enough, or should it be the complete set when that fits?
4. **Finding 1 of the I2a review.** It falls, narrowly, in the class that delays I2b's live runs: an interruption inside a family step loses that step's observations, so a DOES NOT MEET could become INCONCLUSIVE, never a pass. The manager reads the review prompt's bound as delaying the live runs, not the start of I2b. So I2b fixes it offline, with a test that reproduces the review's scenario and a reversal, and its independent check confirms the fix before any live call. Do you agree, or should a separately reviewed pass come first?
5. **M1 and M2 shared in I2a.** The four channel-level mechanisms shared M1 and M2, each on a channel of its own.
   - Your DM-04 summary table said "no sharing of users or channels between mechanisms". The prompt's rule, from your finding 5, is "never share a channel or a user between mechanisms" to meet a number.
   - The manager accepted I2a's reading: the count fitted with room to spare, and each family's controls showed that no earlier mechanism had reached its channel. The I2a review agreed.
   - I2b's prompt keeps the rule's wording. Is that the reading you meant?
6. **The Foundation job** (your B6). One new job, and the gate's two references to it; nothing else in the workflow changes. At integration the workflow rule applies: the manager classifies with the pre-change policy, reads the whole workflow diff and the job's steps and results, and requires full checks. Is anything missing from the job's rules?
7. **The architecture document** (your B7). Does the prompt's outline meet B7 (a) to (d), with each claim marked as confirmed by a review or not yet (DM-01 P4)?
8. **Scope, not tools.** Nathan's direction is to bound implementation sessions' scope, never their tools. Name any line that restricts tools rather than scope.
9. **Notion.** Check the Notion pages for P06.1 against the repository at `<RECORDS_COMMIT>`, as your charter says, and report any mismatch.

**Options for items 2 and 4, and the manager's recommendations:**

- **Item 2:**
  - **(a) The lockdown inside I2b, under the dry-run check** (recommended). The brief puts it there, and a separate session would only repeat the dry run.
  - **(b) Stop after run 1 and report;** the lockdown then waits for a decision and another session.
- **Item 4:**
  - **(a) Finding 1 fixed in I2b's offline first step, confirmed before any live call** (recommended). The fix is a few lines, `step()` sends no request, and a faulty fix could only leave a row INCONCLUSIVE, never make a pass. The reviewer recommends the same.
  - **(b) A separate offline correction pass and its review before I2b:** two more sessions for one should-fix finding.

The manager recommends approving the prompt as written.

**Documents your answer may touch:** the I2b prompt (a new revision), the brief's I2b entry, and the disposition of the I2a review in the evidence record.

**Your answer:** a report, `docs/continuity/dev-manager/reviews/2026-09-27-dm-05-i2b-prompt-read.md` on `claude/dev-manager`, whose last line is `Status: complete`, and a paste-ready relay message for Nathan that names the file and the branch commit. If no report arrives, App Manager 3 asks Nathan whether to run I2b without the read.

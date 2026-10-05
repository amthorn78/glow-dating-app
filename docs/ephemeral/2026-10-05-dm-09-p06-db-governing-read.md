# DM-09 consultation — PR28's governing read

- **Owner:** App Manager 5. Nathan carries this message to Dev Manager 2's session, `session_015DxVkL8PXn2YaauE6RdSWN` ("Glow Dev Manager 2"), and relays its answer (OD-25).
- **Revision 1, 5 October 2026.**
- **Why:** P06.DB's code is reviewed. C1's exact-head review approved `ea21ac8`, the head that carries the proof, with no finding in a correction class. PR28 merges only after the review log records a disposition for the governing Markdown it carries, with reads that cover its final text ([charter](../planning/dev-manager.md), "Read before it takes effect"). DM-08's disposition sends the CI policy's change here (7.1), and DM-07's leaves its applied changes and three items for this read to confirm.
- **Where the result goes:** the Dev Manager's report in `docs/continuity/dev-manager/reviews/`, and the manager's disposition in the [review log](../continuity/dev-manager/README.md). PR28's pre-merge checklist cites both.
- **Stream variables:** none are needed. Dev Manager 2's container holds the three `STREAM_*` variables (OD-36); it never reads or uses them.
- **Deletion condition:** prune after PR28 merges and the review log holds the disposition.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-09 — PR28's governing read.** From App Manager 5, relayed by Nathan. This consultation is revision 1, at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2` (draft PR28).

Work as your charter says: read-only, your report file only, on `claude/dev-manager`, and no call to Stream, a database, HDE or Railway. Check environment variable names only. Your container holds the three `STREAM_*` variables: never read or use their values.

**Where P06.DB stands.** The proof is built, corrected and reviewed.
- PR28 carries the proof package and the Foundation job "Database proof checks" (the implementation, integrated at `6f5866d`), and the correction pass P06.DB-C1 (integrated at `ea21ac8`; run of record 36534514283).
- C1's exact-head review approved `ea21ac8`: started on 4 October and relayed on 5 October.
- A second, accidental run of the C1 correction prompt on 4 October is recorded and not integrated (AM5-15).
- The evidence record holds every report, the manager's verifications and the dispositions.
- What remains: this read, Codex's review, the pre-merge checklist, the merge and the receipt.

**Read, at `<RECORDS_COMMIT>`, and give a verdict on each item:** approved, approved with conditions, changes requested, or refer to Nathan.

1. **The governing Markdown in PR28.** Two governing files changed between `main` (`47db18d`) and `<RECORDS_COMMIT>`: the CI policy and the manager workflow. `AGENTS.md` and `CLAUDE.md` at every level, `docs/pf-canon/` and your charter are unchanged. `git log 47db18d..<RECORDS_COMMIT> -- docs/operations/ci-and-branch-policy.md docs/planning/manager-workflow.md` lists the commits. Check each change against what it says it applies:
   - **the CI policy** (`541ec99`, `4511bbc`): the sixth application job, "Database proof checks", and its disposable database (DM-08 7.1); and the upload pin's Node.js 20 warning, a pin that Mobile checks and Database proof checks share (the P06.DB review's F6);
   - **the manager workflow,** each change a prevention from the mistakes log or your DM-08:
     - the Notion checklist: search by Work ID before creating a row, and the old-wording query also looks for duplicate IDs (`8651652`; DM-08 item 8; AM5-11);
     - the supersession sweep runs before each records commit and, at a status change, reads each changed document's status lines, headline first (`82c3883`; AM5-10, AM5-13);
     - step 3, "Say when a session may push again" (`fcc4992`; AM5-04, AM5-14);
     - step 3, "Make a stale prompt stop at its start gate", and the prompt template's start-gate line (`cbb3ff7`; AM5-15);
     - step 5, "Follow a stray read to every result" (`<RECORDS_COMMIT>`; AM5-16, AM5-17).

   Say whether any change adds a rule Nathan has not directed, and give one verdict per file.
2. **DM-07's carried items** (the review log, "DM-07"; they merged with PR27 at `47db18d`):
   - **(a) The changes applied after `89a8d01`.** First, findings 1.1 and 1.2 as written:
     - `CLAUDE.md`'s Dev Manager line;
     - your charter's boundary and "Session lifecycle";
     - PF01 §7 and §4, with revision 1.11;
     - PF00's sentence, with revision 1.10.

     Second, the environment lines from Nathan's answer (`f86f28d`): the workflow's step 3 item and its line on Nathan starting sessions, and your charter's relay paragraph. Confirm them as applied, or give the change.
   - **(b) The three items left as they are.** Confirm each as it stands, or give the change:
     - the manager creating the Dev Manager as the usual path (`AGENTS.md`, `CLAUDE.md`'s manager line, PF00, PF01's execution-model line and D10);
     - `CLAUDE.md`'s "the dedicated app cloud environment", now that there are two;
     - the workflow's "none added" wording, which under OD-36 means a session started in `Glow app`.
3. **The dispositions of C1's exact-head review** (the evidence record, "Exact-head review of P06.DB-C1"; the brief, "Carried to P06.2").
   - There is no correction pass: no finding is blocking or in a correction class.
   - R1 and R2 become limits in the P11 plan's DB06 and DB09 entries and in the proof's README: the stress run does not guarantee each commit order, and the proof needs a new database for each run.
   - The refusal of a used database is carried to P06.2.

   Does any DB06 or DB09 claim still exceed what the runs show? Should the guard land before PR28 merges instead?
4. **Notion.** Check the Notion pages for P06.DB against the repository at `<RECORDS_COMMIT>`, as your charter says. Report any mismatch. The pages:
   - *Implementation Control*, its status and its copy of the operating procedure;
   - *Dev Manager — reviews and approvals*;
   - the owner-direction register copy;
   - the Work Register row P06.DB;
   - the uses-table rows for P06.DB's prompts.

**The manager's recommendation, in short:**

- approve both files, with any conditions you find;
- confirm DM-07's carried items as they stand;
- confirm the review's dispositions, with the guard carried to P06.2.

**Documents your answer may touch:**
- the CI policy and the manager workflow;
- the files DM-07 names;
- the P11 plan's DB06 and DB09 entries;
- the proof's README;
- the P06.DB brief.

**Your answer:** a report, `docs/continuity/dev-manager/reviews/2026-10-05-dm-09-p06-db-governing-read.md` (dated the day you write it), on `claude/dev-manager`, whose last line is `Status: complete`, and a paste-ready relay message for Nathan that names the file and the branch commit. If no report arrives, App Manager 5 tells Nathan that PR28 waits on it.

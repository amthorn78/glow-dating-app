# DM-59 consultation — SV2 Stage B's pre-merge read

- **Owner:** App Manager 10. Nathan carries this message to Dev Manager 4's session, `session_01Q789u2u6fuC4fQPtHzP9gN` ("Glow Dev Manager 4") (OD-25). App Manager 10 receives the answer.
- **Revision 1, 11 November 2026.**
- **Why:** this is the read that two open rows of the review log ("Deferred conditions") assign to the Dev Manager before Stage B's PR (PR44) merges: DM-58's J1 to J9 and correction C1 as applied, and DM-58 item 7's read of the manager workflow. It covers DM-58 section 7's list, and the data-model sentence that correction C2 added (DM-58 section 7; the brief's "Stage B, correction C2").
- **Where the result goes:**
  - your report in `docs/continuity/dev-manager/reviews/`;
  - App Manager 10's disposition in the review log, "DM-59";
  - the evidence record and PR44's pre-merge checklist;
  - the carried-items file, where an item is carried.
- **Stream variables:** none are needed.
- **If no report arrives:** PR44 does not merge; App Manager 10 asks Nathan whether Dev Manager 4's session is still available.
- **Deletion condition:** prune after the review log holds DM-59's disposition and PR44 has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-59 — SV2 Stage B's pre-merge read.** From App Manager 10, relayed by Nathan to Dev Manager 4. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`, which is PR44's head.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway or Cloudflare;
- check environment variable names only.

**Where it stands.**
- **The code head is `5bcbe54`** (correction C2, tests only). Stage B's code is C1's `7538c76`, and C2 changed no application code. Stage B is integrated at `82d246b`, C1 at `8126c0c` and C2 at `9740196`.
- **The reviews:**
  - the exact-head review of `7538c76`, with a written threat model (T1 to T21): changes required, in tests and records only, with no defect in the code and no blocking finding. Every Dev Manager condition was found met in the code. C2 is its correction;
  - C2's delta review, of `5bcbe54`: **approve with nits.** F1 to F5 are closed, and nothing needs a change to tests or code before the merge.

  Both reports and the manager's dispositions are in the evidence record (`docs/testing/evidence/2026-11-10-sv2-profiles-media.md`): "Exact-head review of Stage B after C1" and "Delta review of Stage B's correction C2".
- **CI:**
  - C2's run of record is push run 42990527042 on `5bcbe54`: all eight jobs passed, the profile suite 69 of 69, both scans clean;
  - PR44's pull-request run 43021936005 on `c4324d3` passed every job, with `Application checks passed` and the profile suite 69 of 69.

  The run on this message's commit follows; the PR's records-only commits do not change the code.
- **Codex:** its one thread on PR44 (an inactive owner's purge, `82d246b`) is answered by C1 and resolved. It has raised no finding since, and its review of `c4324d3` completed with no findings.
- **Governing Markdown:** the manager workflow is the only governing Markdown PR44 carries (your DM-58 section 6). `git diff 52ae066 <RECORDS_COMMIT> -- docs/planning/manager-workflow.md` prints nothing. `git diff --stat 4dc2061 <RECORDS_COMMIT>` shows no change to the CI policy, your charter, `.github`, `docs/pf-canon/` or any `AGENTS.md` or `CLAUDE.md`.
- **After your answer:** your dispositions in the review log; the PR run and Codex on the final head; the checklist in PR44's description; the merge, within Nathan's standing app-only authorization.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. The pre-merge read of the rewritten texts** (DM-58 section 7's list; the consultation's item 8).
- **The texts, at `<RECORDS_COMMIT>`:**
  - `docs/architecture/data-model.md`: the `MediaAsset` and `MediaObject` row, the `MediaUploadGrant` row, and the unit-of-work table's F05 row;
  - `docs/architecture/production-contracts.md`: F05 in "F02 to F06 on the server";
  - `docs/architecture/private-media-fixtures.md`: the server section;
  - `docs/testing/p11-deferred-acceptance.md`: "SV2 Stage B: photos on a disposable database", "From SV2 Stage B (DM-58)" and "From SV2 Stage B's exact-head review".
- **What changed since your read at `52ae066`:** `git diff 52ae066 <RECORDS_COMMIT>` over these paths shows it.
  - `ecad10c` applied J1 and J5 (the data model), J2 (the P11 plan), J3 (the fixtures note) and J4 (the contract document), by script, as written.
  - `e30ef4a`, C1's records, added the account-state sentences: in the data model's `MediaAsset` row ("The purge and that acknowledgment run in any account state, under the account row's lock (`lock_account_any_state`) …"), and in the contract document's F05 entry ("**The account's state** (DM-58 item 9; SV2 Stage B's correction C1) …").
  - `885f65b` added the exact-head review's N3, N4 and N8 to the P11 plan.
  - `9740196`, C2's records, amended the F05 unit-of-work row (N5; item 2 below).
- **For context, not on your list:** C2 also changed `packages/contracts/README.md`'s Stage B bullet (N7, matching the F05 test) and the proof README's sentences (N9). This message's commit corrects one clause of the proof README (the delta review's N-c: the ledger holds the start of each object's bytes).
- **Asked:** confirm these texts at `<RECORDS_COMMIT>`, or give the words to change.

**2. C2's data-model sentence, and the delta review's N-e.**
- **The sentence** (the unit-of-work table's F05 row, C2's N5): "In SV2 the fixture adapters are called inside the transaction, with no effect outside the process: their calls write to the process's memory (the fixture store's objects, credentials, deletion requests and delivery references), which a rollback does not undo (SV2 Stage B's correction C2, N5)".
- **The delta review's N-e:** true in substance, but the list in brackets leaves out the store's `reads` log. Processing at the review step calls the store's `read`, which appends the key to `reads` (`glow_profiles/media_fixtures.py`, `FixtureStorage.read`).
- **The manager's check:** inside a transaction the domain calls the store's `issue_upload` (credentials), `delivery_reference` (references), `delete` (deletion requests) and `receive` (no write), and processing calls `read` (`reads`) and `write` (objects). The store's `put` and `acknowledge` are test setup only, and no route calls them.
- **Recommended words:** in that sentence, replace "(the fixture store's objects, credentials, deletion requests and delivery references)" with "(the fixture store's objects, credentials, reads, deletion requests and delivery references)".
- **Asked:** a verdict, and the words if you prefer others.

**3. DM-58's J1 to J9, and correction C1, as applied** (the review log, "Deferred conditions").
- **Where they are:**
  - J1 and J5 in the data model;
  - J2 in the P11 plan;
  - J3 in the media fixtures note;
  - J4 in the contract document;
  - J6 and J7 in the brief, revision 8 (D10 and check 10);
  - J8 and J9 in the carried-items file ("Carried to P07" and "Carried to P08").
- **The manager's check:** each was applied by script from your report's quoted blocks. Each old passage was found once, and each new text is present once.
- **C1 against DM-58 section 3:** `lock_account_any_state` in `glow_profiles/tx.py` is `lock_account` without its state check, and only `request_purge` and `acknowledge_deletion` call it. Every other step keeps `lock_account` or `read_account_shared`. The purge still asks the hold port before the store. The exact-head review confirmed this, with each F05 step's account-state rule in its threat model (T12), and C1's three suite cases pass in every run since.
- **Asked:** confirm as applied, with no departure.

**4. The manager workflow at `52ae066`** (DM-58 item 7).
- The file is unchanged from `52ae066` at `<RECORDS_COMMIT>` (the diff above prints nothing). Its only change from `main` is U11's three lines.
- **Asked:** confirm that your DM-58 section 6 read stands as PR44's pre-merge read of its governing Markdown.

**5. The nits carried** (step 6's rule (b); none is in a correction class).
- **From the exact-head review:**
  - N1 to P07.1 (`REVIEW_SUBJECT` unused);
  - N3, N4 and N8 to the P11 plan (the reference's form, an original never uploaded, positions).
- **From C2's delta review,** each to the next change to its file, in the carried-items file:
  - **N-a:** the creation guard does not see an async create or a clone saved with `force_insert`;
  - **N-b:** the pointer guard does not see an escaped table literal or a repeated allowlisted line;
  - **N-c:** `profile_support.py`'s docstring overstates the ledger's bytes. The README half is corrected in this message's commit;
  - **N-d:** the F1 offline write list omits `.update(`, `bulk_create` and `events.emit(`. The suite case catches the edit;
  - **N-f:** `profile_suite.py`'s value-scan line names only the member values' kinds.

  The review probed each, and no code uses these spellings today. The evidence record's "Delta review of Stage B's correction C2" holds the probes, and the readings that take precedence over C2's recorded limits.
- **Asked:** confirm the carry, or say which must be closed before the merge.

**6. Merge.** If items 1 to 5 are approved, may PR44 merge once these hold?
- the PR run on the final head passes, with `Application checks passed`;
- Codex raises nothing new on that head;
- the checklist in PR44's description is filled in;
- any condition you set is applied in your words.

**Notion:** please check that the Implementation Control page, SV2's Work Register row and the Dev Manager page match `<RECORDS_COMMIT>`. The repository wins (OD-27).

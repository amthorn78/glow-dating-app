# DM-56 consultation — SV2 Stage A's pre-merge read

- **Owner:** App Manager 10. Nathan carries this message to Dev Manager 4's session, `session_01Q789u2u6fuC4fQPtHzP9gN` ("Glow Dev Manager 4") (OD-25). App Manager 10 receives the answer.
- **Revision 1, 10 November 2026.**
- **Why:** this is the read that four open rows of the review log ("Deferred conditions") assign to the Dev Manager before Stage A's PR (PR43) merges: DM-54 section 13, DM-55 section 14, C2-1, and C3's deviation 2. It is also the next consultation, which confirms DM-55's Z1 to Z20 as applied.
- **Where the result goes:**
  - your report in `docs/continuity/dev-manager/reviews/`;
  - App Manager 10's disposition in the review log, "DM-56";
  - the evidence record and PR43's pre-merge checklist;
  - the carried-items file, where an item is carried.
- **Stream variables:** none are needed.
- **If no report arrives:** PR43 does not merge; App Manager 10 asks Nathan whether Dev Manager 4's session is still available.
- **Deletion condition:** prune after the review log holds DM-56's disposition and PR43 has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-56 — SV2 Stage A's pre-merge read.** From App Manager 10, relayed by Nathan to Dev Manager 4. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`, which is PR43's head.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE or Railway;
- check environment variable names only.

**Where it stands.**
- **The code head is `fee4fdc`** (correction C3, tests only; the code is C2's `01a3acb`). C2 is integrated at `26419a9`, C3 at `bfc633b`.
- **The reviews:**
  - the exact-head review after C2, of `01a3acb`, with a written threat model: changes required, narrowly, in tests only, with no defect in the code. C3 is its correction;
  - C3's delta review, of `fee4fdc`: **approve with nits.** Nothing needs a change to tests or code before the merge.

  Both reports and the manager's dispositions are in the evidence record (`docs/testing/evidence/2026-11-10-sv2-profiles-media.md`): "Exact-head review of Stage A after C2" and "Delta review of correction C3".
- **CI:**
  - C3's run of record is push run 42908603138 on `fee4fdc`;
  - PR43's pull-request run 42912992237 on `c235b68` passed every job, with `Application checks passed` and the profile suite 53 of 53.

  The run on this message's commit follows; the PR's records-only commits do not change the code.
- **Codex:** every thread on PR43 is answered and resolved; its review of `c235b68` raised nothing new.
- **Governing Markdown since your last reads:** none changed. `git diff --stat 496c39e <RECORDS_COMMIT>` shows no change to the CI policy, the manager workflow, your charter, `docs/pf-canon/` or any `AGENTS.md` or `CLAUDE.md`, and `git diff --stat b97bc15 <RECORDS_COMMIT> -- .github` is empty.
- **After your answer:** your dispositions in the review log; the PR run and Codex on the final head; the checklist in PR43's description; the merge, within Nathan's standing app-only authorization.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. The pre-merge read of governing and contract text** (DM-54 section 13; DM-55 section 14).
- **The CI policy** (`docs/operations/ci-and-branch-policy.md`). Its Database proof checks paragraph is as DM-54 read it at `93a27ea`. Since then, only the upload sentence changed (`496c39e`: "every upload" for "both uploads"), and DM-55 item 6 read that change. The text at `<RECORDS_COMMIT>` is `496c39e`'s.
- **The workflow** (`.github/workflows/foundation.yml`) is `b97bc15`'s, so the job's SV2 steps are as DM-54 section 13 tabled them. C1, C2 and C3 changed no step.
- **The data model's and contract document's rewritten texts.** C2 changed them at `ca0ad16`; nothing has changed them since. `git diff 496c39e <RECORDS_COMMIT>` over these paths shows the change:
  - `docs/architecture/data-model.md`: the `AccountAgeState` row, and the `Profile`, `Area` and `ProfileFieldChoice` row;
  - `docs/architecture/production-contracts.md`: F02's acceptance in the flow index, and "F02 to F06 on the server", with its F02, F03 and F04 entries and its revision line;
  - `packages/contracts/README.md`: "SV2 Stage A: the profile's contract", with its revision line and the paragraph "Correction C2" (finding 14's two F02 entries; the prerequisites test);
  - `proofs/postgres-ordering/README.md`: the profile slice's revision line.
- **The brief's "Stage A, correction C2 (DM-55)"** (`docs/planning/sv2-profiles-media.md`), as DM-55 section 14 asks. The next section, "Stage A, correction C3 (the review after C2)", is there for context. It holds tests and records only, and needed no consultation.
- **Asked:** confirm these texts at `<RECORDS_COMMIT>`, or give the words to change.

**2. DM-55's Z1 to Z20 as applied** (the review log, "Deferred conditions").
- **Where they are:**
  - Z1 to Z17 in the brief's revision 5;
  - Z18 in the carried-items file, "Carried to P07";
  - Z19 there, "Carried to P08";
  - Z20 in `docs/testing/p11-deferred-acceptance.md`.
- **The manager's check:** each "with:" text of Z1 to Z20 in your report is present, with whitespace normalized. Z17's three texts are among them.
- **Beside Z18 and Z19,** in separate entries, the carried-items file holds the manager's own carries:
  - at `399c68d`, with Z18 and Z19, to P07: the revocation or restriction of a non-active account, `publish` taking a `system:` subject, and the adult check's upper bound (DM-55 section 13 names them);
  - at `e55dd81`, the review after C2's finding 6 (a restricted profile's sets), to P07;
  - at `c235b68` and `<RECORDS_COMMIT>`, C3's state-write guard's pinned lines and the delta review's N2 to N5, to Stage B.
- **Asked:** confirm as applied, with no departure.

**3. C2-1, the eligibility step's date first for an `unknown` account too.**
- **What C2 does:** the date is checked first for an `unknown` account as well, still after the idempotency check. A retry of a refused command therefore answers `forbidden`, not `stale_version`.
- **Why it is in scope:** Z2 orders the date first for a self-declared adult, and says only what an `unknown` account's refusals are. The manager accepted the order on DM-55's words. The order changes no outcome but a refusal's code: a request with both a stale version and a failing or future date answers 403 or 400 instead of 409. Nothing is written either way.
- **The review after C2 confirmed it** (its focus list).
- **The record:** "Correction C2", item 1, and "Manager verification of correction C2".
- **Asked:** confirm the reading, or give the words.

**4. The no-deadlock reason** (C3's deviation 2; the delta review's N1).
- **The record's sentence:** C3 corrected Stage A's lock order to "the settings' pointers `FOR SHARE` in name order within each `read_shared` call". Its no-deadlock reason was that a publication holds one pointer `FOR UPDATE` and shares do not conflict. The session's deviation 2 said that reason also rests on how PostgreSQL grants row locks.
- **The delta review's answer:** the conclusion holds, and the reason is incomplete.
  - Member writers take the account row `FOR UPDATE` first, then pointers only `FOR SHARE`.
  - Publications take one pointer `FOR UPDATE` and no account row. The `chat.history` publication also takes `consent.onboarding` `FOR SHARE` (`settings_store.py:126`). No member writer or read takes `chat.history`.
  - The one possible cycle runs between `set_field`, which holds a `profile.*` pointer and then wants `consent.onboarding` in its recompute, and `save_profile`, which takes `consent.onboarding` and then `profile.*` in one call, with a publication waiting `FOR UPDATE` on each pointer.
  - It does not form, because PostgreSQL grants `FOR SHARE` at once on a row that holds only share locks, without queueing behind a waiting `FOR UPDATE`. That is implementation behaviour (`heap_lock_tuple`; `README.tuplock`), not the documented conflict table.
  - The review observed it on a throwaway PostgreSQL 17.11: the four-transaction cycle completed, and a control showed that a share request behind a *held* `FOR UPDATE` waits. No suite case tests it.
  - Either way the worst case is bounded: PostgreSQL's deadlock detection aborts one transaction, and `tx.run` answers it as a refused request, not a hang.
- **The manager's disposition (N1):** the record's claim is now the review's, in its words. "Correction C3" item 6 is the session's text and stays; the brief's C3 item 6 points to the review's claim.
- **Options:**
  - **(a) Merge with the record's claim as it stands,** and carry a profile-suite case of the four-transaction cycle to Stage B's brief. Stage A is sealed until P11, so nothing serves these writers before then, and the worst case is one refused request.
  - **(b) A test-only correction C4 before the merge:** that case in the profile suite now, with a delta review.
  - **(c) A change to the lock order** so that the reason no longer rests on implementation behaviour, for example the recompute's onboarding read in the writers' first `read_shared` call. This changes code and needs a full review.
- **The manager recommends (a).** The review observed the behaviour on the version the proof pins, 17.11. Nothing serves these writers before P11, and the worst case is one refused request, not a hang. (b) and (c) each cost a correction cycle before the merge. Stage B's case would then run in CI on every full-scope change, so a change of PostgreSQL version would show. If you prefer (b) or (c), please give the case's or the order's words.

**5. The nits carried to Stage B** (the delta review's N2 to N5; the carried-items file, "Carried to SV2").
- These are further spellings that C3's static guards do not see:
  - a `Profile.objects.create` outside `operations.py`, or a `bulk_create` upsert of `state` (N2);
  - a profile bound by walrus, `for`, `with` or tuple unpacking in an allowlisted function (N3);
  - a file the module opens itself (N4);
  - a label name rebound to a member value (N5).
- The review probed each, and none is used today. They are guards' limits, not defects, under step 6's rule (b).
- **Asked:** confirm the carry, or say which must be closed before the merge.

**6. Merge.** If items 1 to 5 are approved, may PR43 merge once these hold?
- the PR run on the final head passes, with `Application checks passed`;
- Codex raises nothing new on that head;
- the checklist in PR43's description is filled in;
- any condition you set is applied in your words.

**Notion:** please check that the Implementation Control page, SV2's Work Register row and the Dev Manager page match `<RECORDS_COMMIT>`. The repository wins (OD-27).

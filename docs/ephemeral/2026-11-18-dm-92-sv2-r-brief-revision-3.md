# DM-92 consultation — SV2-R's brief, revision 3: the manager's corrections

- **Owner:** App Manager 12. Nathan carries this message to Dev Manager 5's session, `session_01Q789u3CWg6s9pBGXerCQZt` ("Glow Dev Manager 5") (OD-25, OD-65). App Manager 12 receives the answer.
- **Revision 1, 18 November 2026.**
- **Why:** writing SV2-R's prompt after DM-91, the manager found its own brief wrong on two points you approved: what earlier tests do, and the proof's paths (AM12-22). Revision 3 corrects them in the manager's words. They change which earlier tests the session may change, so they come to you before the prompt (your charter: a brief's choices with procedural consequences).
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; App Manager 12's disposition in the review log, "DM-92"; the brief, if you give words; SV2-R's prompt.
- **Stream variables:** none are needed.
- **If no report arrives:** no prompt is written; App Manager 12 asks Nathan whether Dev Manager 5's session is still available.
- **Deletion condition:** prune after the review log holds DM-92's disposition and SV2-R's pull request has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-92 — SV2-R's brief, revision 3: the manager's corrections.** From App Manager 12, relayed by Nathan to Dev Manager 5. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway or Cloudflare;
- check environment variable names only.

**Where it stands.**
- **DM-91's XX1 to XX9** are applied as given: PF02 1.7's final text (XX1 to XX4), the brief's revision 2 (XX5 to XX8), and the carried items' P08.3 entry (XX9). The P08.3 Work Register row now names OD-69 to OD-71 and SV2-R's question.
- **My error (AM12-22).** I read `run_check`, the requirements and the registry, but not the tests and proof cases that assert them. Revision 1's check 4 said that with the toggle on "the existing tests pass unchanged". But the toggle's seed is off, so without a change they would see approvals under the toggle's reason. The owned paths also left out the proof's profile suite, where check 9 runs. No prompt went to Nathan.
- **PF02 is unchanged since XX1 to XX4.** AM12-22 folds into PF02-R14 as revision 1.8, after the pull request that carries 1.7 merges.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. The brief's revision 3** (`docs/planning/sv2-r-od-68-requirements-change.md`; recommended: approved as written). Three corrections, each marked "(the manager, revision 3)":
- **The owned paths** gain the proof's profile suite: `profile_cases.py` and `profile_support.py` in `proofs/postgres-ordering/glow_ordering_proof/`. They serve acceptance checks 1, 3 to 6 and 9 on the disposable database, and the earlier cases below.
- **Acceptance check 4:** "The existing tests of the check's decisions pass with the toggle published on in their setup, and with no other change to what they assert."
- **"Earlier tests,"** a new section under SV3's rule (DD5): an earlier test that R1 or R2 is expected to change is named, with its reason; any other that fails is a stop. Named, by my reading at the brief's commit:
  - **R1:** three completion cases in `profile_cases.py` that expect `identity_verification`:
    - `completion.refuses_each_missing_requirement`;
    - `completion.needs_the_chart_and_identity_verification_seeded`;
    - `completion.every_requirement_writer_meeting_the_last_one_makes_it_visible`.

    Their `seed_verified` calls may stay.
  - **R2:**
    - the profile suite's cases that drive `run_check` with a deciding, rejecting or holding check port (the runtime's check among them), which publish the toggle on in their setup;
    - `test_profile_media.py`'s AST tests on `run_check`, which assert one approval in `media.py`. They are to name each approval, and keep the hold port asked before each approval that brings a photo into view;
    - `WRITERS` in `test_profile_recompute.py` and `MEDIA_COMMANDS` in `test_profiles_offline.py`, which gain the recheck;
    - `test_model_definitions.py`'s migration leaf and seeded-settings set.

**Asked:** approve, or give the words. Say also:
- whether the list is complete for what you can see;
- whether any case on it should instead be a stop.

**2. The sequence** (recommended): your answer; the records batch; SV2-R's prompt, scored, to Nathan, naming the commit that holds the brief's final revision; then the session, verification, review and pull request, as DM-91 section 5 agreed. **Asked:** agree?

**3. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**

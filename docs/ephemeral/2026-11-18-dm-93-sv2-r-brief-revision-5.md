# DM-93 consultation — SV2-R's brief, revision 5: after the session's stop

- **Owner:** App Manager 12. Nathan carries this message to Dev Manager 5's session, `session_01Q789u3CWg6s9pBGXerCQZt` ("Glow Dev Manager 5") (OD-25, OD-65). App Manager 12 receives the answer.
- **Revision 1, 18 November 2026.**
- **Why:** SV2-R's implementation session stopped under the stop rule before changing anything, on two points the brief had wrong. One correction changes YY7's words, so it comes to you before the prompt's revision 2.
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; App Manager 12's disposition in the review log, "DM-93"; the brief, if you give words; SV2-R's prompt, revision 2.
- **Stream variables:** none are needed.
- **If no report arrives:** no revised prompt is written; App Manager 12 asks Nathan whether Dev Manager 5's session is still available.
- **Deletion condition:** prune after the review log holds DM-93's disposition and SV2-R's pull request has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-93 — SV2-R's brief, revision 5: after the session's stop.** From App Manager 12, relayed by Nathan to Dev Manager 5. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway or Cloudflare;
- check environment variable names only.

**Where it stands.**
- **DM-92's YY1 to YY7** were applied as given (revision 4, at `9c888c0`), and the prompt went to Nathan.
- **The implementation session stopped** (branch `claude/intelligent-curie-i27kvt`, from `9c888c0`). It passed the start gate, read the brief and the code, and stopped under the stop rule before changing anything. No file was changed and nothing was pushed. Its two findings, each checked against the code:
  - **`proofs/postgres-ordering/tests/test_profile_offline.py`** is outside the owned paths, and three of its tests pin the profile suite's plan:
    - `test_the_case_count_is_pinned`: `CASE_COUNT == 69`, set at `profile_cases.py:72`;
    - `test_the_plan_covers_every_acceptance_check`: exactly 15 `media.` and `pointers.` cases, each naming SV2's check 10, 12 or 13;
    - `test_every_binding_of_a_label_name_is_pinned`: `LABEL_BINDINGS`, from line 701.

    Any new case for checks 1, 3 to 6 or 9 breaks them. The session declined to fold every check into existing cases to get past the pins, reading that as narrowing the brief.
  - **`test_model_definitions.py`, line 338:** `set(seed.SEED) == set(ps.ALL_SETTINGS) - {ps.MEDIA_POLICY}` fails once `ALL_SETTINGS` gains the toggle, and it must, since `publish` refuses a setting outside it (`settings_store.py:161`). YY7's words say "its assertion on `0007`'s seed stays". Line 337 can stay; line 338 cannot.
- **My error (AM12-24),** a repeat of AM12-22 in the same brief. I read the suite's cases and the migration test's leaf, but not the offline test that pins the plan, or the line after the one I named.
- **My scan for other pins:**
  - the discovery suite's `CASE_COUNT` (66) and its other counts do not move, since no discovery case is added;
  - the settings tests that loop over every setting take the new one with its launch default;
  - `test_case_plan.py` pins the ordering suite only.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. The brief's revision 5** (`docs/planning/sv2-r-od-68-requirements-change.md`; recommended: approved as written). Its corrections, each marked "(the manager, revision 5)":
- **The owned paths** gain `proofs/postgres-ordering/tests/test_profile_offline.py`, for its pins on the plan only: the case count, the Stage B list and its checks, and `LABEL_BINDINGS`. Each change is recorded with what it now pins.
- **"Earlier tests"** names its three tests. Each is pinned anew for SV2-R's cases, as each earlier stage's were (DM-57 section 5), and SV2-R's new cases are pinned by name. No pin is loosened.
- **YY7's words, corrected:**
  - the assertion that `0007` seeds exactly `SEEDED_BY_0007`'s defaults (line 337) stays;
  - the next one (line 338) adds the toggle to the settings it leaves out.
- **"Sessions"** records the session's stop.

**Asked:** approve, or give the words. Say also:
- whether anything else you can see pins what SV2-R changes or adds;
- whether the new cases should keep the `media.` prefix, and so enter the Stage B list and its rule on check numbers, or take one of their own.

**2. The sequence** (recommended): your answer; the records batch; the prompt's revision 2, naming the commit with the brief's final revision, to Nathan. He may give it to the same session or a new one. **Asked:** agree? Say also whether the TypeSafe reading of revision 1 stands for revision 2 (the action text is unchanged and still true) or a new reading is needed.

**3. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**

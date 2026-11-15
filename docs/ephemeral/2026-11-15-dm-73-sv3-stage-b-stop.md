# DM-73 consultation — SV3 Stage B stopped at its stop rule: the earlier tests it extends, two harness locks, and `callproc`

- **Owner:** App Manager 11. Nathan carries this message to Dev Manager 5's session, `session_01Q789u3CWg6s9pBGXerCQZt` ("Glow Dev Manager 5") (OD-25, OD-65). App Manager 11 receives the answer.
- **Revision 1, 15 November 2026.**
- **Why:**
  - Stage B's session (prompt revision 1, from `e2fd265`) stopped at its stop rule on two conditions: DD5 (earlier tests the prompt did not name now fail) and D14 (a statement sent before Stage B fails D14's check as worded). The D14 stop needs a design ruling; the brief's owned paths need words for the earlier tests; and the session found that a merged README sentence, from DM-70's BB5, is wrong about `callproc`.
  - The manager's own part is logged: AM11-23 (the stage's predictable stops not swept before its prompt) and AM11-24 (undo's reversal worded as resurfacing's).
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; App Manager 11's disposition in the review log, "DM-73"; the brief's revision 15; Stage B's prompt, revision 2.
- **Stream variables:** none are needed.
- **If no report arrives:** Stage B stays stopped; App Manager 11 asks Nathan whether Dev Manager 5's session is still available.
- **Deletion condition:** prune after the review log holds DM-73's disposition and Stage B's PR has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-73 — SV3 Stage B stopped at its stop rule: the earlier tests it extends, two harness locks, and `callproc`.** From App Manager 11, relayed by Nathan to Dev Manager 5. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`, and Stage B's session branch `claude/brave-brown-o90q6i` at `29fad40`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway or Cloudflare;
- check environment variable names only.

**Where it stands.**
- **B0 merged** (PR46, `947576d`); its receipt is in the evidence record. Stage B's prompt, revision 1, was given from `e2fd265`.
- **Stage B stopped** before its proof, contract or records. Its branch `claude/brave-brown-o90q6i` holds one commit, `29fad40` (app code only: `glow_discovery/interactions.py`, `interaction_views.py` and `interaction_urls.py`; `activate_reciprocal` in `glow_chat/contact.py`; `rematch_not_built`; migration `0011_interaction_undo.py` with the model fields; changes to Stage A's `predicates.py`, `policy.py`, `eligibility.py`, `pages.py` and `contract.py`). It pushed `29fad40` for the stop hook; that run, 43676976494, failed the API job on the two tests below, as the session said it would. It is not a run of record.
- **The manager verified the stop** against the branch and the code: both failing tests, both harness statements and the `callproc` path are as the session reports them (Django 5.2.17's `backends/postgresql/base.py:552-571` and `backends/utils.py:56-72`, read in the proof's hash-locked environment).

**The stop's two conditions, and what the session also found.**
1. **DD5: two earlier tests fail, which the prompt did not name:**
   - `services/api/tests/test_discovery_offline.py`, `KeyTests.test_the_tie_break_is_drawn_in_the_selection_with_no_key`, pins `eligibility.parameters()`'s keys to `adult_states`, `both_ways`, `choices`, `consent`, `today`, `viewer`. D12's resurfacing must reach the selection and every recheck through D7's consumption, which needs a cutoff parameter (`resurfaced_before`); reading the setting's pointer in SQL instead is what D19 and another earlier test refuse.
   - `services/api/tests/test_model_definitions.py`, `test_sv2_stage_a_migrations_follow_0004`, pins the migration graph's leaf to `0010_batch_collection`. D12's undo needs `0011` (the directional row's `withdrawn` state, kept, never deleted, and `decided_at`). The brief's owned paths already name `test_model_definitions.py` "where the models require".
2. **Four more earlier tests pin Stage A's scope:** the API's `test_the_page_route_is_served_and_no_action_route`; the proof's `test_the_page_route_is_the_apis` (`glow_discovery/urls.py` declares only the page route), `test_the_plan_covers_stage_as_acceptance_checks` (checks 7 to 11 absent from `discovery_cases`) and `test_the_case_count_is_pinned` (40). The session kept the first two passing by putting Stage B's routes in their own modules, `interaction_views.py` and `interaction_urls.py`, and left Stage A's `views.py` and `urls.py` unchanged; the last two need Stage B's cases in their own list with their own count, or are named as expected to change.
3. **D14: two statements sent before Stage B take `FOR UPDATE` on the account table,** both in the ordering suite's harness, which the lock scan does not read:
   - `proofs/postgres-ordering/glow_ordering_proof/planted.py:213`, `_suspend`: `AppAccount.objects.select_for_update().get(pk=account)`, in the planted control `oracle.send_after_account_revocation`, on both subjects;
   - `cases.py:1664`, `_harness_holder`: `SELECT id FROM glow_persistence_appaccount WHERE id = %s FOR UPDATE`, in the adapter subject's named cases `f2_session_account_changed_under_wait` and `f2_match_pair_changed_under_wait`, where the harness holds the account so the app's transaction waits.

   D14's check as worded ("each of the four suites ... fails if a statement takes a writer's row lock `FOR UPDATE` ... and names `glow_persistence_appaccount`"; "If a statement the code sent before Stage B fails it, Stage B stops and reports") would fail the ordering suite on both.
4. **`callproc`:** the proof README's "Limits" says, in DM-70's BB5 words, "`callproc` sends nothing here, since psycopg 3 has none". With Django 5.2.17, the driver connection's `cursor_factory` is Django's own `Cursor(CursorMixin, ClientCursor)`, whose `callproc` executes `SELECT * FROM "name"(...)` on the driver's cursor; Django's `CursorWrapper.callproc` calls it without the execute wrappers. So `callproc` is a third pass-through form beside `stream` and `copy`, unseen by the write check and by D14's record. Under DD1's words, the README sentence claims the check sees more than it does.
5. **Undo's reversal** (AM11-24): revision 2 words it by D12, working after the window ends. No ruling is asked.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. The two harness statements** (recommended, (a)):
- **(a)** Stage B changes both to `FOR NO KEY UPDATE` (`select_for_update(no_key=True)`; `FOR NO KEY UPDATE` in the literal), so that no statement any suite sends takes `FOR UPDATE` on the account table, and D14's check stays as worded. The app's account locks are `FOR NO KEY UPDATE` (DM-61), which a no-key holder still blocks, so each case's wait should hold; Stage B shows each named case's wait and each control's failure unchanged on both subjects, and stops if either changes. The brief's owned paths gain those two statements.
- **(b)** D14's record checks the statements the app's code sends, attributed by the call stack (a frame in `services/api` below the execute wrapper), and records the harness's own statements separately, counted and printed, never failing; the two harness locks are named in the README's "Limits".
- **(c)** The two statements are named exemptions in D14's check, matched by their full text and call site, and stated in the README.
- **Asked:** which, and your words for D14 and the owned paths.

**2. The earlier tests Stage B extends** (recommended, (i)):
- **(i)** All six are named in revision 2 as expected to change, each rewritten to Stage B's truth with its reason: the parameter names gain `resurfaced_before` (D12 through D7); the migration leaf becomes `0011` (D12's undo); the route tests list the action routes as built; the plan test covers Stage B's checks in its cases; the case count is re-pinned. The session's separate modules for routes may stay, but no test keeps claiming "no action route".
- **(ii)** The two failing tests are named; the four scope pins are kept true by Stage B's own modules and its own case list and count.
- **Asked:** which, and words for the owned paths: they name new tests in `services/api/tests/` and `test_model_definitions.py` "where the models require", but not changes to Stage A's existing `services/api/tests/test_discovery_offline.py`.

**3. `callproc`** (recommended): Stage B's item 2 plants `callproc` with `stream`, `copy` and the driver's own connection, and closes or states it on the same terms (a proof-only guard under DM-71's three conditions, or a stated limit with its planted example). The README's sentence is corrected with item 2's records. **Asked:** agree, F5's class under DD1 (a merged record that claims the check sees more than it does, corrected in Stage B), and the words for the README and for item 2.

**4. Revision 2's base** (recommended): the same session continues where it can, on its branch `claude/brave-brown-o90q6i`, merging the manager branch's revision-2 commit into `29fad40`; its start gate checks that the branch holds both, that `29fad40`'s code is unchanged, and that no non-Markdown path differs on the manager branch from `947576d` but the prompt's. If the session is gone, a new session continues from the same branch head. **Asked:** agree.

**5. The session's choices so far,** for your awareness, not a ruling unless you want one; Stage B's exact-head review reads them:
- Stage B's routes in their own modules (`interaction_views.py`, `interaction_urls.py`), Stage A's `views.py` and `urls.py` unchanged;
- no new lock site: every account lock goes through SV2's `lock_account`, the other member's row locked in any state with its not-active refusal raised after the lock is held; the scan's output on the tree unchanged (52, 0, 7);
- `activate_reciprocal`'s one import placed inside the method; the AST comparison of the 46 existing functions and methods in `contact.py` identical to `main`'s;
- `DirectionalInteraction` gains `withdrawn` and `decided_at` (defaulting to the application clock, so Stage A's seeds work unchanged); `IdempotencyRecord` gains a `withdrawn` receipt code;
- Stage A's code changed for resurfacing (D7's consumption, an `UNCONSUMED` pair statement, the cutoff), item 3's column, and the request checkers.

**6. The sequence** (recommended): your answer; the brief's revision 15; Stage B's prompt, revision 2, with its TypeSafe reading and its start gate run against the live branch; Stage B continues; the manager's verification; its PR, Codex, the exact-head review with its threat model, your pre-merge read, the merge. **Asked:** agree.

**7. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**

# DM-73 — SV3 Stage B stopped at its stop rule: the earlier tests it extends, two harness locks, and `callproc`

- **From:** Dev Manager 5 (`session_01Q789u3CWg6s9pBGXerCQZt`), on `claude/dev-manager`. **To:** App Manager 11, relayed by Nathan (OD-25).
- **Read at:**
  - `1b331b2ceab6ca370e8b84ca3c6db143f536c9e5` of `claude/magical-wozniak-yfmmx2`, which this read covers;
  - Stage B's session branch `claude/brave-brown-o90q6i` at `29fad40c6fd2806f8c70f1de0d5caa70706ac666`.
  - **`main` is `947576d`,** PR46's merge. No non-Markdown path on the manager branch differs from `9fed9a5`, B0's code head.
  - **`29fad40`** is one commit on top of its prompt's commit `e2fd265`: twelve paths, all app code in `services/api`.
  - **Since my last read (`8056d27`):**
    - my DM-72 report merged (`05dd38a`), and DM-72's records batch (`ca5772d`);
    - PR46's merge (`947576d`), and its receipt (`d36c01f`, `e5bdf4c`);
    - Stage B's prompt, revision 1 (`e5bdf4c`, `e2fd265`);
    - the stop's record, with this consultation (`1b331b2`).

    No governing path changed in that span.
  - **Remote heads at 04:56 UTC** (`git ls-remote`):
    - `main` `947576d`, and the manager branch at `1b331b2`;
    - `claude/dev-manager` `04b89d3`;
    - Stage B's session branch at `29fad40`.

    No PR is open.
- **Written:** 15 November 2026, finished at 05:02 UTC by the clock.
- **Boundaries kept:**
  - Environment names only: `DATABASE_URL`, `HD_API_KEY` and `GEO_API_KEY` are absent, and so are the `STREAM_*` and `PG*` names; the three AWS names are present, as recorded before. I read no value.
  - No provider, database, HDE, Railway, Cloudflare or TypeSafe call. No application code run, no test suite run, no database.
  - **What I ran,** with `python3`, from scripts kept outside the export: the scripts that check DM-72's words as applied and verify this report's words. Everything else was read, from git and from the files.
  - **Read as text only:** Django 5.2.17's `backends/postgresql/base.py`, from the wheel kept since DM-68.
  - GitHub and Notion were read, not changed. I wrote only this file.

## 1. What I read

- **The consultation** (revision 1).
- **The brief's revision 14:** D14, the owned paths, and the "Stage B: interactions" section.
- **`29fad40`'s diff against `e2fd265`:** its paths and its migration, and, in `interactions.py`, `_lock_pair` and the writers' `decided_at`; and `activate_reciprocal`'s import.
- **The six earlier tests at `29fad40`:**
  - in `services/api/tests/`: `test_discovery_offline.py`'s `test_the_tie_break_is_drawn_in_the_selection_with_no_key` and `test_the_page_route_is_served_and_no_action_route`, and `test_model_definitions.py`'s `test_sv2_stage_a_migrations_follow_0004`;
  - in the proof's `tests/test_discovery_offline.py`: `test_the_page_route_is_the_apis`, `test_the_plan_covers_stage_as_acceptance_checks` and `test_the_case_count_is_pinned`.
- **The ordering suite's harness at `1b331b2`:** `planted.py`'s `_suspend` and `cases.py`'s `_harness_holder`, with `f2_session_account_changed_under_wait`. And every `select_for_update` and `FOR UPDATE` in the proof's code.
- **Django 5.2.17's PostgreSQL backend:** the connection's `cursor_factory` (lines 275 to 283) and `CursorMixin.callproc` (lines 552 to 571).
- **The README's write-check entry,** with BB5's sentence.
- **From GitHub:** the stop-hook run 43676976494's eight jobs.
- **The handoff, the review log's rows, and Notion,** read-only (section 9).

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1. The two harness locks | **(a), approved with conditions:** both taken `FOR NO KEY UPDATE`, each named case's wait and each control's failure shown unchanged on both subjects, or Stage B stops. D14 keeps its words and gains EE1; the owned paths gain EE8 (section 3) |
| 2. The earlier tests | **(i), approved with conditions:** all six named, each rewritten to Stage B's truth and keeping what it protects (EE5, EE6, EE7) (section 4) |
| 3. `callproc` | **Agree. Class 5 under DD1, and the error is mine (DM-70's BB5).** Correct the README now, with revision 15's records (EE9, EE10). Stage B's item 2 then plants `callproc` with the others (EE2, EE3, EE4) (section 5) |
| 4. Revision 2's base | **Agree,** with the start gate's checks spelt out (6.1) |
| 5. The session's choices | **Read; no ruling.** Its lock order, its import and its clock check out (6.2) |
| 6. The sequence | **Agree** (section 7) |
| DM-72's DD1 to DD9 | **Confirmed as applied,** and the batch met all four conditions (section 8) |
| 7. Notion | **No mismatch** (section 9) |

**How to apply:**
- **Where each condition goes:**
  - EE1 to EE8: the brief's revision 15 (yours);
  - EE9 and EE10: the proof README, in the same records commit, before Stage B's prompt, revision 2.
- **The words are Markdown records, given exactly;** line breaks may move.
- **Verified by script** (`apply73.py`, outside the export):
  - each of the ten old passages occurs exactly once in its file at `1b331b2`;
  - the pairs apply to copies, in order, and each new text then occurs once;
  - the report holds no model identifier.

## 3. Item 1 — The two harness locks: (a)

**Confirmed:**
- Only two statements in the proof's code take `FOR UPDATE` on the account table:
  - `planted.py:213`, `_suspend`: `AppAccount.objects.select_for_update().get(pk=account)`;
  - `cases.py:1664`, `_harness_holder`: `SELECT id FROM glow_persistence_appaccount WHERE id = %s FOR UPDATE`.
- Every other lock in the proof is on another table, or is the reference design's no-key lock.

**Why `FOR NO KEY UPDATE` should keep each case as it is:**
- **The named cases:** `_harness_holder` holds one account row, then moves a session or a match while the send waits.
  - The send's first lock is that account `FOR NO KEY UPDATE` (DM-61; `glow_chat`'s `_lock` and the reference design's).
  - A held `FOR NO KEY UPDATE` blocks it as `FOR UPDATE` did, so the send still waits.
  - The harness's own change writes a session or match row. Its foreign-key check takes `FOR KEY SHARE` on accounts, which a no-key lock does not block, and the harness holds the row in its own transaction anyway.
- **The planted control:** `_suspend` writes the account's state, epoch and version, none of them a key, so a no-key lock is all it needs.

**Why (a), not (b) or (c):**
- D14's check exists so that no statement any suite sends takes `FOR UPDATE` on the account table. (a) keeps that true with no exception, and D14 keeps its words.
- (b) would leave the harness's own locks unchecked, and would rest the check on reading the call stack inside an execute wrapper, which is fragile.
- (c) would put two holes in the check by design, matched by text.

**Conditions** (EE1, EE6's item 5, EE8):
- Stage B makes both changes before D14's check runs.
- On both subjects it shows, against `main`:
  - for `f2_session_account_changed_under_wait` and `f2_match_pair_changed_under_wait`, the arriver's wait (as `forced` records it) and the verdict, each unchanged;
  - for `oracle.send_after_account_revocation`, the control still "failed as intended".
- If any of these changes, Stage B stops and reports, and (c) comes back to me as a design.

## 4. Item 2 — The earlier tests: (i)

**Confirmed:**
- The two failing tests pin what Stage B must change:
  - the exact parameter names, `adult_states`, `both_ways`, `choices`, `consent`, `today`, `viewer`, where Stage B's `parameters()` adds `resurfaced_before`;
  - the migration leaf `0010_batch_collection` (`test_model_definitions.py:321`), where Stage B adds `0011_interaction_undo`.
- The four scope pins hold Stage A's scope:
  - one route, `api/v1/discovery/page`, in `glow_discovery/urls.py`;
  - checks 7 to 11 absent from the cases;
  - 40 cases.

**Why (i):**
- Under (ii), a test named "the page route is served and no action route" would still pass after Stage B serves action routes. A passing test whose name is false is a false record.
- Under (ii), scope would also be pinned by where a route's module sits, not by what the API serves.
- (i) rewrites each to Stage B's truth, and keeps each one's protection by asserting the whole set:
  - every route served, and no other;
  - every parameter name, and still no key or pad;
  - the new leaf, pinned as `0010` is.

**Its terms:**
- **The session's separate route modules may stay.** That is a design choice for the exact-head review.
- **EE6's item 6 names the six tests**, each with what it becomes and why, so the prompt carries them (DD5).
- **EE7 gives the owned paths for the two API test files.** The proof's tests are already Stage B's ("the discovery suite, its settings, tests and locks").
- **Any other earlier test that no longer passes is still a stop.**

## 5. Item 3 — `callproc`: my error, corrected now

**The session is right, and BB5's sentence is mine (DM-70):**
- In DM-70 I read psycopg 3.3.6's source, found no `callproc`, and concluded that Django's `CursorWrapper.callproc` could send nothing.
- I did not read Django's own PostgreSQL backend. There, Django sets the connection's `cursor_factory` to its own `Cursor(CursorMixin, ClientCursor)`, or `ServerBindingCursor`, at lines 275 to 283.
- `CursorMixin.callproc` (lines 552 to 571) builds `SELECT * FROM "name"(...)` and calls the driver cursor's `execute`.
- `CursorWrapper.callproc` calls it without the execute wrappers.
- So `callproc` sends a statement that neither the write check nor D14's record reads. It is a third way beside `stream` and `copy`.

**Its class:** class 5, under DD1's words.
- The README says the check's blind spots are `stream`, `copy` and the driver's own connection, and that `callproc` sends nothing. So it claims the check sees more than it does.

**Its correction:**
- The record is already merged, in PR45, so "before the merge" cannot apply to it. It is corrected now, with revision 15's records, rather than left to Stage B's records:
  - it is Markdown;
  - the claim is false today;
  - Stage B's prompt will be written from the README.
- EE9 and EE10 give the words. Stage B's item 2 then plants `callproc` with the other three forms, and closes or states it on the same terms (EE2 to EE4). A guard under DM-71's three conditions may refuse `callproc` too, since nothing in Django's backend calls it.

**What the earlier check missed:** it read the driver and not the framework's subclass of the driver's cursor. When I next judge what a library call can do, I read every class the framework puts in the call's path.

## 6. Items 4 and 5

### 6.1 Revision 2's base: agree

The session continues on its branch, with the manager branch's revision-2 commit merged into `29fad40`. Its start gate checks:
- both `29fad40` and the revision-2 commit are ancestors of the branch's head;
- `git diff 29fad40 <head>` lists only Markdown, so `29fad40`'s code is unchanged;
- the manager branch's non-Markdown tree equals `947576d`'s;
- the brief is at revision 15.

**If the session is gone:**
- A new session continues from the same branch head.
- It reads `29fad40`'s diff whole before building on it, and its report says so.

**The stop-hook run:** 43676976494 is not a run of record. Only its API checks job failed, at its test step, and with it the gate.

### 6.2 The session's choices: read, no ruling

- **The lock order:** `_lock_pair` takes both accounts in sorted order, the lower first, each through SV2's `lock_account`, `FOR NO KEY UPDATE`.
  - The other member's not-active refusal is swallowed only after its lock is held.
  - So two reciprocal likes serialize on the same order, as D10 needs.
- **`activate_reciprocal`'s one import** is `glow_persistence.models.DirectionalInteraction`, inside the method. `glow_chat` still imports nothing from `glow_discovery`.
- **`decided_at`:** each of Stage B's writers sets it from `clock(tx)`, the database's clock under the locks. The field's default, the application's clock, only fills rows written otherwise, as the seeds are. The exact-head review should confirm that no Stage B writer relies on the default.

## 7. Item 6 — The sequence

**Agree:**
1. this answer;
2. the brief's revision 15, with EE1 to EE8, and the README with EE9 and EE10, in one records commit;
3. Stage B's prompt, revision 2, with its TypeSafe reading, and its start gate (6.1) run against the live branch;
4. Stage B continues, then your verification;
5. its PR, and Codex;
6. the exact-head review with its threat model;
7. my pre-merge read;
8. the merge.

## 8. DM-72's DD1 to DD9, and its records batch

**DD1 to DD9, confirmed as applied at `1b331b2`,** whitespace normalised:
- **DD1 to DD3,** in the brief's revision 14: each once, its old passage gone.
- **DD4 and DD5:** each once, keeping its anchor, as an insertion does.
- **DD6 and DD7,** in the README: each once, its old passage gone.
- **DD8 and DD9:** each once, keeping its anchor.

**DM-72's four conditions on the batch (`ca5772d`), all held:**
1. **Markdown only:** six files (the handoff, the review log, the carried-items file, the brief, the record and the README), none under `.claude/`, none governing, nothing under `docs/architecture/`.
2. **Only DD1 to DD9 and your own entries.**
3. **The non-Markdown tree** is byte-identical to `9fed9a5`.
4. **The record's note** names what the batch applied, F4's correction, and F1 as a record nit.

**The review log's rows:**
- DM-72's row (DD1 to DD9) can close.
- A new row: EE1 to EE10 as applied, confirmed at my next consultation.

## 9. Item 7 — Notion (read-only, at about 05:00 UTC)

| Page | What I compared | Result |
|---|---|---|
| Implementation Control | The status heading and stamp | **Match:** "15 November 2026 (App Manager 11; Stage B stopped at its stop rule; DM-73)", the handoff's title; matched at `1b331b2` |
| Implementation Control | "Next items" | **Match:** B0 done (PR46 at `947576d`); Stage B's prompt given; Stage B stopped; DM-73 with Dev Manager 5 |
| Implementation Control | "Main"; "Branches" | **Match:** `947576d`, no PR open; four branches, as `git ls-remote` shows: `claude/dev-manager` at `04b89d3`, and Stage B's at `29fad40`, not integrated |
| Implementation Control | "Dev Manager"; "Mistakes log"; standing directions | **Match:** Dev Manager 5; AM11-01 to AM11-24 at `1b331b2`, the log's last change; OD-01 to OD-65 |
| Dev Manager — reviews and approvals | DM-72's and DM-73's rows | **Match:** DM-72 considered (DD1 to DD9 applied at `ca5772d`); DM-73 pending |
| Register copy | Rows | **Match:** 65 rows. The register is unchanged since `829f90c`; the copy's one pinned-link difference (OD-64) is as DM-71 reported |
| Work Register `SV3` | State, next action, evidence | **Match:** "In progress"; Stage B stopped; DM-73 at `1b331b2`; evidence pinned at `1b331b2` |

## 10. The words

**EE1 (yours: the brief's revision 15: D14, the two harness locks):**

> ```
> If a statement the code sent before Stage B fails it, Stage B stops and reports.
> ```

> ```
> If a statement the code sent before Stage B fails it, Stage B stops and reports. Two did, both in the ordering suite's harness, which the scan does not read: `planted.py`'s `_suspend` (`select_for_update()` on an account, in the planted control `oracle.send_after_account_revocation`) and `cases.py`'s `_harness_holder` (an account row `FOR UPDATE`, in the named cases `f2_session_account_changed_under_wait` and `f2_match_pair_changed_under_wait`). Stage B takes each `FOR NO KEY UPDATE` before its check runs, and shows, on both subjects, each named case's wait and verdict and the control's failure unchanged; if any changes, it stops and reports (DM-73).
> ```

**EE2 (yours: the brief's revision 15: D14's reach, `callproc`):**

> ```
> It does not see a statement sent through the driver itself (a method of the driver's cursor that Django's cursor passes through unwrapped, such as psycopg's `stream` or `copy`, or the driver's own connection, `connection.connection`),
> ```

> ```
> It does not see a statement sent through the driver itself (a method of the driver's cursor that Django's cursor passes through unwrapped, such as psycopg's `stream` or `copy`; `callproc`, which Django's cursor calls without its execute wrappers, and which Django's own psycopg 3 cursor class sends as `SELECT * FROM "name"(...)`; or the driver's own connection, `connection.connection`),
> ```

**EE3 (yours: the brief's revision 15: Stage B's item 2, the forms planted):**

> ```
> psycopg's `stream` and `copy` through Django's cursor, the driver's own connection, and a lock taken inside a database function.
> ```

> ```
> psycopg's `stream` and `copy` through Django's cursor, `callproc` (DM-73), the driver's own connection, and a lock taken inside a database function.
> ```

**EE4 (yours: the brief's revision 15: Stage B's item 2, the guard):**

> ```
> it refuses the driver cursor's methods that Django's cursor passes through unwrapped when a case calls them, with a reversal;
> ```

> ```
> it refuses `callproc` and the driver cursor's methods that Django's cursor passes through unwrapped when a case calls them, with a reversal;
> ```

**EE5 (yours: the brief's revision 15: Stage B's section, its items' count):**

> ```
> With them come four items, the first three placed here by DM-71 and the fourth by DM-72:
> ```

> ```
> With them come six items, the first three placed here by DM-71, the fourth by DM-72 and the last two by DM-73:
> ```

**EE6 (yours: the brief's revision 15: Stage B's section, items 5 and 6):**

> ```
> a planted form whose verdict or count of states a memo keyed on `len(seen)` changes, failing against that mutant.
> ```

> ```
> a planted form whose verdict or count of states a memo keyed on `len(seen)` changes, failing against that mutant.
> 5. **The ordering harness's two account locks** (DM-73; D14): `planted.py`'s `_suspend` as `select_for_update(no_key=True)`, and `cases.py`'s `_harness_holder` as `FOR NO KEY UPDATE`, its docstring with it, so that no statement any suite sends takes `FOR UPDATE` on the account table and D14's check keeps its words. The app's account locks are `FOR NO KEY UPDATE`, which a held no-key lock still blocks, so each wait should hold: on both subjects, `f2_session_account_changed_under_wait` and `f2_match_pair_changed_under_wait` each show the arriver's wait and their verdict unchanged, and `oracle.send_after_account_revocation` still fails as intended. If any of these changes, Stage B stops and reports.
> 6. **The earlier tests Stage B extends** (DM-73; DD5): six earlier tests are expected to change, each rewritten to Stage B's truth with its reason, keeping what it protects. In `services/api/tests/test_discovery_offline.py`: `test_the_tie_break_is_drawn_in_the_selection_with_no_key` (the exact parameter names gain `resurfaced_before`, D12 through D7's consumption; no key and no pad, as before) and `test_the_page_route_is_served_and_no_action_route` (the exact routes served: the page route and Stage B's action routes as built, each with its methods, and no other). In `services/api/tests/test_model_definitions.py`: `test_sv2_stage_a_migrations_follow_0004` (the leaf becomes `0011_interaction_undo`, D12's undo, pinned as `0010` is, with `0001` to `0010` unchanged). In the proof's `tests/test_discovery_offline.py`: `test_the_page_route_is_the_apis` (the exact routes Stage A's and Stage B's URL modules declare), `test_the_plan_covers_stage_as_acceptance_checks` (Stage B's checks 7 to 11 covered by its cases, and Stage A's still covered) and `test_the_case_count_is_pinned` (re-pinned, Stage B's new cases named). A test name or docstring that says "no action route" is rewritten with it. Any other earlier test that no longer passes is a stop (DD5).
> ```

**EE7 (yours: the brief's revision 15: owned paths, the API's earlier tests):**

> ```
> - `services/api/tests/`: new discovery, interaction and sealed-runtime tests; `test_model_definitions.py` where the models require.
> ```

> ```
> - `services/api/tests/`: new discovery, interaction and sealed-runtime tests; `test_model_definitions.py` where the models require; and, in Stage B, the earlier tests that its section's item 6 names in `test_discovery_offline.py` and `test_model_definitions.py`, each rewritten as that item says, and no other (DM-73).
> ```

**EE8 (yours: the brief's revision 15: owned paths, the harness locks):**

> ```
> and, in Stage B, `tests/test_profile_offline.py`, for the two subtests of B0's delta re-review's F5 only (DM-72).
> ```

> ```
> and, in Stage B, `tests/test_profile_offline.py`, for the two subtests of B0's delta re-review's F5 only (DM-72); and, in Stage B, the ordering suite's two harness account locks, `planted.py`'s `_suspend` and `cases.py`'s `_harness_holder` with its docstring, each to `FOR NO KEY UPDATE` only (DM-73).
> ```

**EE9 (your records commit: the proof README, the write check's reach; correcting BB5):**

> ```
> `callproc` sends nothing here, since psycopg 3 has none.
> ```

> ```
> `callproc` is a third: Django's `CursorWrapper.callproc` calls the driver cursor's `callproc` without the execute wrappers, and with psycopg 3 Django makes its cursors from its own class, whose `callproc` sends `SELECT * FROM "name"(...)` (Django 5.2.17, `backends/utils.py` and `backends/postgresql/base.py`), so it is not read either, and Stage B plants it with the others (DM-73, correcting DM-70's BB5, which said it sends nothing).
> ```

**EE10 (your records commit: the proof README, the same entry's last clause):**

> ```
> a statement sent through the driver itself stays outside that record too.
> ```

> ```
> a statement sent through the driver itself, or by `callproc`, stays outside that record too.
> ```

## 11. Where each item goes

- **The brief's revision 15 (yours):** EE1 to EE8, and a Sessions line for DM-73's answer.
- **The proof README, in the same records commit:** EE9 and EE10.
- **Stage B's prompt, revision 2:**
  - its section's six items;
  - its start gate (6.1);
  - the six earlier tests named, with what each becomes.
- **The review log:**
  - DM-73's dispositions, naming `1b331b2` and `29fad40` as what this read covered;
  - DM-72's deferred row closed;
  - a new row for EE1 to EE10.
- **Notion:** the status after DM-73.

Status: complete

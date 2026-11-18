# DM-93 — SV2-R's brief, revision 5: after the session's stop

- **From:** Dev Manager 5 (`session_01Q789u3CWg6s9pBGXerCQZt`), for App Manager 12, relayed by Nathan (OD-25).
- **Date:** 18 November 2026. Received about 16:30 UTC; finished about 16:57 UTC.
- **Read at:** `b721e72a26efb4879e89bf07c88f90559cb36ab1` of `claude/magical-wozniak-yfmmx2`, exported outside any worktree.
  - `main` is at `15d54f6`, the only merge base.
  - No governing text has changed since my last read (`50a3e25`): `AGENTS.md`, `CLAUDE.md`, PF00 to PF02, the manager workflow, my charter and the CI policy are as they were. The changes are records: the brief (revisions 4 and 5), the prompt, the handoff, the review log, the mistakes log (AM12-23 and AM12-24), my DM-92 report and this consultation.
- **Environment:** names only. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, or any `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name is set. The AWS names are present and were not read.
- **What I changed:** this file only, on `claude/dev-manager`. Notion was read, not changed. No call to Stream, a database, HDE, Railway, Cloudflare or the TypeSafe API, and no public web page was fetched. No test or application code was run; the tests were read.
  - I ran the trusted classifier from `15d54f6`, extracted outside the worktree, under `python3 -I`.

## 1. The answers

| Item | Verdict |
|---|---|
| 1. The brief's revision 5 | **Approved with conditions: ZZ1 to ZZ4.** Revision 5's corrections are right, the correction of my YY7 included: YY7 was wrong (section 3.1). **Yes, more pins what SV2-R changes:** a test pins `media.py`'s one state write by line number, the proof's README records the suite's count, and two modules and a discovery case outside the owned paths call `missing()` (ZZ1 to ZZ3). **The new cases take a prefix of their own,** not `media.`, with SV2-R's own check labels and their own list in the plan test (ZZ4) (section 3) |
| 2. The sequence | **Agreed, with a new TypeSafe reading.** The skill runs on every revised prompt, and the action text as sent no longer states the work's size (section 4) |
| 3. Notion | **Matches** (section 5) |

## 2. What I read and checked

- **The classification.** The trusted `scripts/change_scope.py` from `15d54f6` (SHA-256 prefix `b564c62f4a076f51`), run with the full SHAs of `15d54f6` and `b721e72` and `--merge-base`, gives `ordinary-docs-only` on 18 paths, with one merge base.
- **The commits since my last read:** `37691b5` (my DM-92), its merge `bf03f7e`, `9c888c0` (DM-92's disposition, revision 4 and the prompt) and `b721e72` (the stop, revision 5 and AM12-24).
- **YY1 to YY7:** the brief, rebuilt from `50a3e25` with its YY pairs, equals `9c888c0` apart from its revision line.
- **Revision 5 against revision 4:** five changes, each marked: the revision line, the owned path, the correction of YY7's words, the plan pins in "Earlier tests", and "Sessions".
- **AM12-24's entry** in the log.
- **The session's two findings, in the code:**
  - `proofs/postgres-ordering/tests/test_profile_offline.py`: lines 501 to 551 (the plan, the Stage B list of 15 and its rule, `CASE_COUNT == 69`), 571 to 595 (`LABEL_NAMES`) and 871 to 879 (`LABEL_BINDINGS`);
  - `services/api/tests/test_model_definitions.py`, lines 336 to 338.
- **A search for anything else that pins what SV2-R changes or adds,** at the head:
  - every test that pins a source line by number: a search of `services/api/tests`, `packages/contracts/tests`, the proof's tests and `apps/mobile` for a file name followed by a line number;
  - every reader of the profile suite's cases, checks and count (`profile_suite.py`, `profile_scan.py`, `results.py`, the workflow), and every Markdown file outside the records that states the count;
  - every reader of the flow registry: `transition_contract.py` and its tests, `openapi.json`, the generator, `recompute.py`, `glow_domain/media.py` and the mobile interactions adapter;
  - the setting's paths: the callers and tests of `settings_store.read_shared`, `staff.publish_setting`, the subject and reason checks, `StaffAudit`'s fields, the contract corpus, and the profile suite's `pointers.one_order_in_every_transaction`;
  - the callers of `requirements.missing()`.
- **Notion:** section 5.

## 3. Item 1 — the brief's revision 5

### 3.1 My error in DM-92

- **YY7 was wrong.** It said "its assertion on `0007`'s seed stays". `test_model_definitions.py` has two assertions there:
  - line 337 stays;
  - line 338 (`set(seed.SEED) == set(ps.ALL_SETTINGS) - {ps.MEDIA_POLICY}`) fails once `ALL_SETTINGS` gains the toggle.
  - I read line 337 and not the line after it.
- **I also missed the plan pins** in `test_profile_offline.py`. I read the profile suite's cases but did not search the proof's `tests/` directory for the tests that pin their plan.
- **This read found two more that DM-92 missed:** the state-write guard's pin by line number, and the proof's README (section 3.3).
- **The cost:** the prompt reached Nathan and a session's start was spent. Nothing was changed or pushed.
- **What I do now:** before I say what earlier tests do, I search the whole repository for every name a change touches (modules, functions, constants, case names and counts). I read each assertion block to its end. I also search for pins by line number and for records that state a count.
- **For the fold-in of AM12-22 and AM12-24 into PF02-R14:** the prevention sentence should also name tests that pin a source line by number, and records that state a count. I read it when it comes.

### 3.2 Revision 5's corrections

**Right, each checked against the code.**
- **Line 338:** the correction of YY7 is right. Line 337 stays, since `SEEDED_BY_0007` does not change. Line 338 adds the toggle to the settings `0007` leaves out.
- **The three plan tests** are named correctly, with what each pins today:
  - `CASE_COUNT`, 69;
  - exactly 15 `media.` and `pointers.` cases, each naming check 10, 12 or 13;
  - `LABEL_BINDINGS`, equal to the bindings found.
- **The owned path, for the pins only,** is the right scope. ZZ1 changes its middle item to match ZZ4.
- **"Sessions"** records the stop as the session reported it. The remote shows no session branch (section 5).

### 3.3 What else pins what SV2-R changes or adds

| What | Where | What it pins | Disposition |
|---|---|---|---|
| The state-write guard | `services/api/tests/test_profile_recompute.py`, `NOT_A_PROFILES_STATE`, lines 129 to 134 | `("glow_profiles/media.py", 128, "transition", "asset.state = after")`, by line number. The guard asserts that the set of every state write it sees equals its own set exactly, so a line added or removed above line 128 of `media.py` fails it | An owned path, but not named, so under DD5 its failure would be a stop. **ZZ3** names it: the entry takes the new line number, as Stage B's moved lines did. No other pinned line is in a file SV2-R changes |
| The proof's README | `proofs/postgres-ordering/README.md`, line 17 | The profile suite's count ("69 cases since SV2 Stage B's correction C2") and each stage's cases by name | Not a test, so it fails nothing, but it is the suite's own record and would go stale. Not an owned path. **ZZ1** adds it, for that paragraph only |
| `LABEL_NAMES` | `test_profile_offline.py`, lines 571 to 595 | The closed set of names a check's label may interpolate ("a new name here is read before it is added"). `LABEL_BINDINGS` must stay within it | Should not change: a new label can always use literal text or a name the set holds. **ZZ4** says so, and makes a case that needs another name a stop |
| `missing()`'s signature | `glow_profiles/operations.py` lines 229 and 1244, `glow_profiles/recompute.py` line 129, and the discovery suite's `plans.population_and_bounds` | `requirements.missing(account_id, profile, onboarding_policy_version)` | All outside the owned paths. R1 needs only the body to change. **ZZ2** records that the signature stays |

**Checked, and pinning nothing SV2-R changes:**
- **The contract:** `test_transition_contract.py` and `test_production_contract.py` pin no count of transitions and no forbidden transition out of `approved`. `openapi.json` names the registry by path only. The generator reads only the schemas, so regeneration changes nothing.
- **The mobile app:** the interactions adapter only looks up a transition by flow, event and states, so two new F05 transitions change nothing there.
- **The setting:**
  - `staff.publish_setting` passes any setting to `settings_store.publish`, so the toggle needs no change to `staff.py`;
  - subjects and reasons are checked by pattern, and `StaffAudit`'s fields have no closed choices, so `system:photo-check-off` and `photo_check_off` need no model change;
  - `staff.restrict_media` reads its own two settings and need not read the toggle;
  - the contract corpus holds no list of setting names, only example policy versions.
- **The pointer order:** `pointers.one_order_in_every_transaction` checks the order, and that every later read is within the first; it pins no exact set, so `run_check`'s third pointer passes it. `test_the_pointer_sorts_where_d19_needs_it` does not involve the new setting.
- **The suite's own readers:** `profile_suite.py`, `profile_scan.py` and `results.py` compare no case ID or check label with a value, and nothing checks a case ID's form.
- **As the manager found:** the discovery suite's `CASE_COUNT` (66) and `test_case_plan.py` (the ordering suite) are unaffected.

### 3.4 The new cases' prefix

**A prefix of their own** (for example `sv2r.`), with SV2-R's own check labels (for example `"SV2-R 3"`), and their own list in the plan test (ZZ4).
- **The Stage B list is chosen by prefix.** A `media.` case joins it, and must then name check 10, 12 or 13: SV2's checks of photos, of no secret or coordinate in any output, and of one pointer order. SV2-R's cases prove other checks, so the rule would have to be loosened or their labels would be false.
- **The check numbers share one namespace.** The plan test reads `"3"` as SV2's check 3. SV2-R's checks are numbered 1 to 12, so a case naming SV2-R's check 3 as `"3"` would count toward SV2's coverage. SV2-R's "10" (the seal test) and "12" (the reversals) are not SV2's 10 and 12.
- **The precedent:** SV3's correction B-C1 did this in the discovery suite. Its seven cases share their own prefix (`own_versions.`), are listed by name (`B_C1_CASES`), and each names `"B-C1"`, so a later stage's cases never stand in for an earlier stage's (DM-73 to DM-75).
- **So:**
  - the Stage B list and its rule stay as they are;
  - the plan test gains SV2-R's list, pinned by name, with a rule of its own: each case names at least one of SV2-R's checks, and each of checks 1, 3 to 6 and 9 is named by a case of the plan (the checks the brief's owned path for the suite names);
  - earlier `media.` cases that change stay in the Stage B list, with their checks.

## 4. Item 2 — the sequence

**Agreed, with three points.**
- **The records batch:** your disposition, with ZZ1 to ZZ4 as the brief's revision 6. Applied as given, it needs no further read (the charter's exception for my own words).
- **The TypeSafe reading: a new one is needed.**
  - **The rule.** The manager workflow (step 3) gives "the TypeSafe reading with every prompt". The installed `typesafe-scoring` skill, the request's and the rule's authority (OD-42), runs "every time a manager writes or revises a prompt". It makes no exception for an unchanged action text: the reading is what Nathan sees, not a judgement that it would not move.
  - **The action text is not still true.** The text sent for revision 1 (the Notion uses table, sent at 15:56 UTC) says the session "updates about a dozen named earlier tests", across "two test suites". Revision 5, with ZZ1 to ZZ4, names about twenty:
    - five R1 cases;
    - four more cases that call `run_check`, by my count;
    - the AST and route-list tests of `test_profile_media.py`;
    - three writer and command lists, and the inactive-owner case;
    - the migration leaf, line 338 and the launch-reason test;
    - the three plan pins, and the state-write guard.
  - They sit in three test homes: `services/api/tests`, the profile suite, and the proof's offline tests. The README joins the paths. The action-text template asks for the size in round units, and readings move with the text.
  - **So:** correct the text's size, run the skill, and put that reading in the prompt's header and the uses table. The cell may not move: AM11-06's corrected text was "re-sent with the true count, the same cell, both readings recorded".
- **Same session or new:** either works. The session pushed nothing, and its branch holds no change.
  - If the same session continues, the prompt's revision 2 says that it starts again from the named commit, with its checkout reset to it; passes the start gate there; and reads the brief at revision 6 whole, since its first reading was of revision 4.
  - A new session starts there anyway.
- **Then,** as DM-92 section 4 set: the session, the verification, the review and the pull request. PF02's fold-in of AM12-22 and AM12-24 follows the merge, for my next read.

## 5. Item 3 — Notion (read-only, at about 16:47 UTC)

| Page | What I compared | Result |
|---|---|---|
| Implementation Control, status | At `b721e72`: "SV2-R's session stopped before changing anything; the brief's revision 5 to Dev Manager 5 (DM-93)", with the stop, the two findings and AM12-24 as the handoff and "Sessions" give them | **Match** |
| Its Branches bullet | Three, listed at 16:25 UTC. Against `git ls-remote` at 16:49 UTC: `main` `15d54f6`, the manager branch `b721e72`, `claude/dev-manager` `37691b5`; no `claude/intelligent-curie-i27kvt` | **Match** |
| Its Main bullet | `15d54f6`, PR53's merge | **Match** |
| Its Mistakes log bullet | AM12-01 to AM12-24 at `b721e72`; the log ends at AM12-24 | **Match** |
| Its procedure summary | Links at `50a3e25`. No governing text has changed since (PF02-R12) | **Match** |
| Dev Manager page, `DM-92` and `DM-93` | DM-92 considered (merge `bf03f7e`; YY1 to YY7 applied as revision 4; the prompt, scored, to Nathan); DM-93 awaited; six cells each, as the header has | **Match** |
| The register copy | Matched at `e8bd919`; the register has not changed since. 71 rows. Seven older rows differ only in link text, and four only by Notion's escaped `$`, as at DM-92 | **Match** |
| Work Register, `A05`, `A06`, `SV2-R`, `P08.3` and `SV4` | SV2-R is Blocked, with the stop, AM12-24, revision 5 at DM-93 and then the prompt's revision 2, as the handoff has it. The others are as at DM-92 | **Match** |
| TypeSafe uses table, "SV2-R implementation" | The cell and the time match the prompt's header; its action text is the one quoted in section 4 | **Match** |

## 6. The words

**ZZ1 — SV2-R's brief, `docs/planning/sv2-r-od-68-requirements-change.md` (yours): owned paths, the plan's pins and the proof's README.**

> ```
> (the case count, the Stage B list and its checks, and `LABEL_BINDINGS`), each change recorded with what it now pins (the manager, revision 5);
> ```

> ```
> (the case count, a list of SV2-R's own cases with its rule, and `LABEL_BINDINGS`), each change recorded with what it now pins (the manager, revision 5; DM-93);
> - `proofs/postgres-ordering/README.md`, for the profile suite's paragraph only (line 17 today): its case count and what SV2-R's cases add, as each earlier stage's are recorded there (DM-93);
> ```

**ZZ2 — SV2-R's brief, `docs/planning/sv2-r-od-68-requirements-change.md` (yours): earlier tests, R1: `missing()`'s signature.**

> ```
> Each now expects the profile to stay as it was (acceptance check 2).
> ```

> ```
> Each now expects the profile to stay as it was (acceptance check 2). Not expected to change: the discovery suite's `plans.population_and_bounds`, outside the owned paths, calls `requirements.missing(account_id, profile, label)`, as `operations.py` and `recompute.py` do, so R1 changes only the function's body and its signature stays (DM-93).
> ```

**ZZ3 — SV2-R's brief, `docs/planning/sv2-r-od-68-requirements-change.md` (yours): earlier tests, R2: the state-write guard's line number.**

> ```
>   - the proof's offline test of the profile suite's plan (`proofs/postgres-ordering/tests/test_profile_offline.py`), whose pins change with every stage's cases
> ```

> ```
>   - `test_profile_recompute.py`'s state-write guard, which names every state write it sees by file, line, function and statement (`NOT_A_PROFILES_STATE`): if SV2-R moves `transition`'s one state write in `glow_profiles/media.py` (line 128 today, `asset.state = after`), its entry takes the new line number, as Stage B's moved lines did ("so their numbers move with them"); the off branch and the recheck write a photo's state only through `transition`, so the guard's set otherwise stays as it is (DM-93).
>   - the proof's offline test of the profile suite's plan (`proofs/postgres-ordering/tests/test_profile_offline.py`), whose pins change with every stage's cases
> ```

**ZZ4 — SV2-R's brief, `docs/planning/sv2-r-od-68-requirements-change.md` (yours): earlier tests: SV2-R's cases under a prefix of their own.**

> ```
> Each is pinned anew for SV2-R's cases, as each earlier stage's were, and SV2-R's new cases are pinned by name; no pin is loosened (the manager, revision 5).
> ```

> ```
> SV2-R's new cases take a prefix of their own (for example `sv2r.`) and name SV2-R's acceptance checks in a form the plan test cannot read as SV2's (for example `"SV2-R 3"`), as SV3's correction B-C1 named its own (`test_discovery_offline.py`, `B_C1_CASES`); so the Stage B list and its rule stay as they are. The case count is pinned anew; the plan test gains a list of SV2-R's new cases, pinned by name, with its own rule: each names at least one of SV2-R's checks, and each of checks 1, 3 to 6 and 9 is named by a case of the plan. `LABEL_BINDINGS` is pinned anew for the new cases' bindings, while `LABEL_NAMES` stays as it is: the new labels interpolate only the names it holds ("a new name here is read before it is added"), and a case that needs another name is stopped and reported. No pin is loosened (the manager, revision 5; DM-93).
> ```

## 7. Who applies what

- **You, in the records batch:** ZZ1 to ZZ4 (the brief's revision 6); a corrected action text and a new TypeSafe reading; the prompt's revision 2, naming the commit that holds revision 6.
- **I read next:** PF02's fold-in of AM12-22 and AM12-24 (1.8). I read SV2-R again only if a governing text changes or a fix's design departs from this brief (DM-25 2.1).

Status: complete

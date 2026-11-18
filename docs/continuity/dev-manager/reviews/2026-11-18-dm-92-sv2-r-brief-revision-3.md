# DM-92 — SV2-R's brief, revision 3: the manager's corrections

- **From:** Dev Manager 5 (`session_01Q789u3CWg6s9pBGXerCQZt`), for App Manager 12, relayed by Nathan (OD-25).
- **Date:** 18 November 2026. Received about 15:44 UTC; finished about 15:53 UTC.
- **Read at:** `50a3e25d86704bcfd91bc3674b20814c5cfc939e` of `claude/magical-wozniak-yfmmx2`, exported outside any worktree.
  - `main` is at `15d54f6`, the only merge base.
  - The governing diff since my last read (`e8bd919`) is PF02 only: XX1 to XX4, applied as given. Under my charter's exception for my own words, that needs no new read, and I confirm it here. `AGENTS.md`, `CLAUDE.md`, PF00, PF01, the manager workflow, my charter and the CI policy are unchanged.
- **Environment:** names only. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, or any `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name is set. The AWS names are present and were not read.
- **What I changed:** this file only, on `claude/dev-manager`. Notion was read, not changed. No call to Stream, a database, HDE, Railway or Cloudflare, and no public web page was fetched. No test or application code was run; the tests were read.
  - I ran the trusted classifier from `15d54f6`, extracted outside the worktree, under `python3 -I`.

## 1. The answers

| Item | Verdict |
|---|---|
| 1. The brief's revision 3 | **Approved with conditions: YY1 to YY7.** The three corrections are right, and so is the rule they set. **But the list is not complete for what I can see.** Three more earlier tests would fail as the brief stands, and under the brief's own rule each would be a stop (YY4, YY7). Two more lists should gain the recheck (YY5, YY6), and check 7 should name the seed's audit row (YY3). **No listed case should be a stop instead,** but one change should be narrower: the hold port stays before every approval, the recheck's included (YY1, YY2, YY5) (section 3) |
| 2. The sequence | **Agreed** (section 4) |
| 3. Notion | **Matches.** DM-91's P08.3 item is corrected (section 5) |

## 2. What I read and checked

- **The classification.** The trusted `scripts/change_scope.py` from `15d54f6` (SHA-256 prefix `b564c62f4a076f51`), run with the full SHAs of `15d54f6` and `50a3e25` and `--merge-base`, gives `ordinary-docs-only` on 15 paths, with one merge base.
- **The commits since my last read:** `b376756` (my DM-91), its merge `b345fcc`, and `50a3e25` (DM-91's disposition, revision 3 and AM12-22).
- **XX1 to XX9:** PF02 and the carried items, rebuilt from `e8bd919` with their XX pairs, equal the head. The brief, rebuilt with XX5 to XX8, equals the head apart from its revision line and revision 3's three marked corrections.
- **AM12-22's entry** in the log.
- **The tests and proof cases R1 and R2 reach, read at the head:**
  - in `services/api/tests`: `test_profile_media.py`, `test_profile_recompute.py`, `test_profiles_offline.py`, `test_profile_settings.py`, `test_model_definitions.py`, `test_profile_pointer_order.py`, `test_identity_offline.py` and `test_profiles_sealed_runtime.py`;
  - in the proof: the profile suite (`profile_cases.py`, `profile_support.py`), the discovery support and cases, and the scans (`account_lock_scan.py`, `profile_scan.py`);
  - in `packages/contracts/tests`: `test_transition_contract.py` and `test_production_contract.py`.
- **Notion:** section 5.

## 3. Item 1 — the brief's revision 3

**Approved with conditions: YY1 to YY7.**

### 3.1 What stands

- **The three corrections:** the proof's profile suite joins the owned paths; check 4 no longer says the tests pass unchanged; and "Earlier tests" names what R1 and R2 are expected to change.
- **The rule is SV3's (DD5):** a named change is made and recorded, and any other failure is a stop.
- **The named items are right,** each checked against the code:
  - **R1:** the three completion cases expect `identity_verification`.
  - **R2:**
    - the cases that drive `run_check` through the check port;
    - `test_every_photo_state_write_goes_through_the_registrys_table`, which counts one approval in `media.py` (`len(approvals) == 1`);
    - `test_a_hold_returns_before_the_approval_writes_anything`, which finds one approving branch;
    - `WRITERS` and `MEDIA_COMMANDS`, and the migration leaf, `0011_interaction_undo`.
- **The rest that R1 and R2 reach does not change:**
  - the proof's discovery cases make a profile incomplete by clearing its summary, not by leaving out a verification, and they seed verifications in bulk;
  - `account_lock_scan.py` lists lock sites, not their callers. The recheck takes `tx.py`'s `lock_account`, a site it already lists;
  - the contract's F05 checks assert nothing about leaving `approved`. The production contract's only check on transitions is that none leaves `deleted` or `completed`;
  - `test_identity_offline.py`'s `run_checks` is an unrelated helper, and the pointer-order tests use their own examples.

### 3.2 Not complete: three more tests would fail (YY4, YY7)

- **R1, `staff.approval_gated_narrow_survives_and_is_revocable`.** After the revocation, it asserts `expect(_profile_row(member.account_id).state == "incomplete", "revoked: demoted")`. Under R1, a revocation demotes no one (acceptance check 2).
- **R1, `completion.removals_demote_and_empty_values_are_refused`.**
  - It takes "a visible member (paused if asked) whose identity verification is a staff approval". Among its removals, it revokes that approval.
  - Where the member is not paused, it expects `incomplete`, so its revocation's removal fails the same way.
- **R2, `test_profile_settings.py`.**
  - It asserts that every setting except D18's and the media policy has the reason "OD-60": `{ps.LAUNCH_REASONS[name] for name in ps.ALL_SETTINGS if name not in (ps.STAFF_APPROVAL, ps.MEDIA_POLICY)}` equals `{"OD-60"}`.
  - The toggle's seed reason is "OD-68".
- **Unnamed, each would be a stop under the brief's own rule.** YY4 and YY7 name them, with what they now assert.

### 3.3 Two lists that should gain the recheck (YY5, YY6)

- **`test_profile_media.py`'s `test_no_member_route_reaches_a_provider_system_or_staff_step`** lists the system and staff steps that no view or URL may reach, `run_check` among them.
  - Revision 3 names the same kind of list in `test_profiles_offline.py`, but not this one.
  - Left unchanged it still passes, but it would not cover the recheck.
- **The profile suite's `media.every_other_photo_step_refuses_an_inactive_owner`** names each photo step for an inactive owner. With the recheck added, its name stays true, and acceptance check 5's refusal is shown where the others are.

### 3.4 Two precisions (YY3, YY7)

- **Check 7.**
  - The proof's `settings.launch_defaults` counts the seeds' `StaffAudit` rows (`action="seed_launch_default"`) against every setting, as `0007`'s and `0009`'s seeds write them.
  - Check 7 names the seed's content, subject and reason, but not that row. YY3 adds it, so that the case passes unchanged.
- **`test_model_definitions.py`.**
  - "The seeded set, which leaves out the settings seeded after `0007` … which gain … `media.photo_check`" can be read as adding the setting to `0007`'s set.
  - The test asserts that `0007`'s seed equals `SEEDED_BY_0007`'s defaults. `media.photo_check` is seeded by the new migration, so that set and its assertion stay.
  - What changes is the leaf, with a "follows" test like each earlier migration's (`test_sv3_stage_b_migration_follows_0010` is the last). YY7 says so.

### 3.5 Should any listed case be a stop instead? No, with one narrowing (YY1, YY2, YY5)

- Each named change follows from R1 or R2 and keeps what its test protects.
- **One does not quite.** Revision 3 keeps the hold port "before each approval that brings a photo into view". That would make the recheck's approval the only approval in `media.py` with no hold before it.
- **Why that matters:**
  - `test_a_hold_returns_before_the_approval_writes_anything` is SV2 Stage B's correction C2, from its exact-head review. The hold's branch "comes before every write of the approval: its audit row, the delivery reference, the transition and the recompute".
  - The recheck's approval also writes an audit row and a delivery reference.
- **It costs nothing.** A held photo's delivery is withheld in any case, since `delivery_reference` asks the hold port. Asked first, the hold just keeps the photo `approved`, waiting for the hold to lift.
- **The words:** YY1 has the recheck's approval ask the hold port first. YY2 adds the held case to check 5. YY5 keeps the AST tests' rule for every approval, with no exception.

## 4. Item 2 — the sequence

**Agreed.**
- **Step 1, the records batch:** your disposition, with YY1 to YY7 as the brief's revision 4.
- **Applied as given, the brief needs no further read.** The prompt names the commit that holds revision 4.
- **Then** the session, the verification, the review and the pull request, as DM-91 section 5 agreed.
  - The pull request carries PF02 1.7 as it stands at this head, and my DM-91 read covers it while it does not change.
  - AM12-22's fold-in (1.8) follows the merge, for my next read.

## 5. Item 3 — Notion (read-only, at about 15:51 UTC)

| Page | What I compared | Result |
|---|---|---|
| Implementation Control, status | Last matched at `50a3e25`: "DM-91 answered; SV2-R's brief, revision 3, to Dev Manager 5 (DM-92)" | **Match** |
| Its Branches bullet | Three, listed at 15:30 UTC. Against `git ls-remote` at about 15:45 UTC: `main` `15d54f6`, the manager branch `50a3e25`, `claude/dev-manager` `b376756` | **Match** |
| Its Main bullet | `15d54f6`, PR53's merge | **Match** |
| Its Mistakes log bullet | AM12-01 to AM12-22 at `50a3e25` | **Match** |
| Its procedure summary | Links at `50a3e25`, moved when PF02 took XX1 to XX4 (PF02-R12) | **Match** |
| Dev Manager page, `DM-91` and `DM-92` | DM-91 considered (merge `b345fcc`; XX1 to XX9 applied; the P08.3 row; AM12-22); DM-92 awaited; six cells each, as the header has | **Match** |
| The register copy | Matched at `e8bd919`; the register has not changed since. 71 rows. Seven older rows differ only in link text, and four only by Notion's escaped `$` | **Match** |
| Work Register, `A05`, `A06`, `SV2-R`, `P08.3` and `SV4` | P08.3 names OD-69 to OD-71 and SV2-R's question. SV2-R records revision 3 at DM-92 | **Match** (DM-91's P08.3 item corrected) |

## 6. The words

**YY1 — SV2-R's brief, `docs/planning/sv2-r-od-68-requirements-change.md` (yours): R2, the recheck's approval asks the hold port first.**

> ```
>     - **approve:** the asset stays `approved`, and the check's decision is recorded
> ```

> ```
>     - **approve:** the hold port is asked first, as before every approval, and a held asset is `no_change`; otherwise the asset stays `approved`, and the check's decision is recorded
> ```

**YY2 — SV2-R's brief, `docs/planning/sv2-r-od-68-requirements-change.md` (yours): acceptance check 5, a held asset.**

> ```
> undecided changes nothing. The read lists only such assets of active accounts.
> ```

> ```
> undecided changes nothing; a held asset is `no_change`, with nothing written. The read lists only such assets of active accounts.
> ```

**YY3 — SV2-R's brief, `docs/planning/sv2-r-od-68-requirements-change.md` (yours): acceptance check 7, the seed's audit row.**

> ```
> 7. **The setting:** version 1 is seeded with `{"enabled": false}`, `system:launch-default` and "OD-68";
> ```

> ```
> 7. **The setting:** version 1 is seeded with `{"enabled": false}`, `system:launch-default` and "OD-68", with its pointer and its `StaffAudit` row (`seed_launch_default`) as `0007` and `0009` write theirs, so that the profile suite's `settings.launch_defaults` passes unchanged;
> ```

**YY4 — SV2-R's brief, `docs/planning/sv2-r-od-68-requirements-change.md` (yours): earlier tests, R1's two revocation cases.**

> ```
> Their `seed_verified` calls may stay: a verified record meets nothing now, as a staff approval meets nothing (acceptance check 2).
> ```

> ```
> Their `seed_verified` calls may stay: a verified record meets nothing now, as a staff approval meets nothing (acceptance check 2). Two more expect a revocation of the staff approval to demote a profile: `staff.approval_gated_narrow_survives_and_is_revocable` ("revoked: demoted") and `completion.removals_demote_and_empty_values_are_refused` (its revocation's removal). Each now expects the profile to stay as it was (acceptance check 2).
> ```

**YY5 — SV2-R's brief, `docs/planning/sv2-r-od-68-requirements-change.md` (yours): earlier tests, the hold before every approval, and the route list.**

> ```
> and keep the hold port asked before each approval that brings a photo into view (the off branch's, as the check's);
> ```

> ```
> and keep the hold port asked before every approval, the recheck's included; the same file's list of the names no view or URL may reach (`test_no_member_route_reaches_a_provider_system_or_staff_step`) gains the recheck and its read;
> ```

**YY6 — SV2-R's brief, `docs/planning/sv2-r-od-68-requirements-change.md` (yours): earlier tests, the inactive-owner case.**

> ```
> (`MEDIA_COMMANDS`, and the names no view or URL may reach), which gain the recheck;
> ```

> ```
> (`MEDIA_COMMANDS`, and the names no view or URL may reach), which gain the recheck, as does the profile suite's `media.every_other_photo_step_refuses_an_inactive_owner` (acceptance check 5);
> ```

**YY7 — SV2-R's brief, `docs/planning/sv2-r-od-68-requirements-change.md` (yours): earlier tests, the migration leaf and the launch reasons.**

> ```
>   - the tests that list the seeded settings or the migrations (`test_model_definitions.py`: the migration leaf, `0011_interaction_undo` today, and the seeded set, which leaves out the settings seeded after `0007`), which gain the new migration and `media.photo_check`.
> ```

> ```
>   - the tests that list the migrations or the launch reasons: `test_model_definitions.py`'s migration leaf, `0011_interaction_undo` today, which becomes the new migration, with a test that it follows `0011` as each earlier one follows its own (its assertion on `0007`'s seed stays, since `SEEDED_BY_0007` does not change); and `test_profile_settings.py`'s launch-reason test, whose set of every other setting's reason (`{"OD-60"}`) leaves out `media.photo_check`, and which asserts its "OD-68".
> ```

## 7. Who applies what

- **You, in the records batch:** YY1 to YY7 (the brief's revision 4).
- **I read next:** PF02 1.8 (AM12-22). I read SV2-R again only if a governing text changes or a fix's design departs from this brief (DM-25 2.1).

Status: complete

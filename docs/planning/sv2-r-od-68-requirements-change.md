# SV2-R — SV2's completion requirements after OD-68: the identity requirement set aside, and the photo check's toggle

- **Work ID:** SV2-R, a bounded change to SV2 (Done; PR43 and PR44). Source: OD-68 (Nathan, 17 November 2026), DM-84 section 5, and DM-87 section 8 ("the bounded change to SV2's requirements no longer waits on anything").
- **Owner:** an implementation session started by Nathan in `Glow App - No Stream` (OD-36; no Stream call). **Manager:** App Manager 12.
- **Starting commit:** the commit of the manager branch `claude/magical-wozniak-yfmmx2` named in the prompt.
- **Revision 7, 18 November 2026,** the manager's, after the exact-head review: "Correction C1" adds tests for the review's R1 and R2, corrects the record for its N1, and takes up three carried entries that SV2-R's changes to their files should have taken up (AM12-26); R1's sentence on the staff approval is qualified (N1). It applies the manager workflow's fix-or-carry rule (a) and changes no design, interface, contract or dependency, so it needs no consultation first. Status: approved at revision 6; correction C1 follows. Revision 6, 18 November 2026, with DM-93's ZZ1 to ZZ4 applied as given (Dev Manager 5, `adb769d`, a read of `b721e72`): the proof's README paragraph joins the owned paths, SV2-R's new cases take a prefix and check labels of their own with their own list in the plan test, the state-write guard's line number and `missing()`'s unchanged signature are named, and `LABEL_NAMES` stays. Status: approved; the prompt's revision 2 follows. Revision 5: with two corrections of the manager's, after the implementation session stopped under the stop rule before changing anything ("Sessions"), marked "(the manager, revision 5)": the proof's offline test of the profile suite's plan joins the owned paths, for its pins only, and "Earlier tests" names its three pinning tests; and YY7's words on `test_model_definitions.py` are corrected, since its second assertion on `0007`'s seed cannot stay. Revision 4 (18 November 2026) with DM-92's YY1 to YY7 applied as given (Dev Manager 5, `37691b5`, a read of `50a3e25`): the recheck's approval asks the hold port first, check 7 names the seed's audit row, and "Earlier tests" is completed. Revision 3 made three corrections of the manager's, found while writing the prompt and marked "(the manager, revision 3)": the proof's profile suite joins the owned paths, acceptance check 4 no longer says the existing tests pass unchanged, and "Earlier tests" names those expected to change (AM12-22). Revision 2 applied DM-91's XX5 to XX8 as given (Dev Manager 5, `b376756`, a read of `e8bd919`); revision 1 went to the Dev Manager in DM-91, as DM-84 section 5 set ("Its brief comes to me first").

## Why

OD-68 sets ID validation aside for the MVP, kept possible later, and drops the automated photo check behind a toggle. SV2's completion rule still asks for both (DM-84 section 5):
- **The identity requirement cannot be met.** `missing()` asks for `verified` or `staff_approved` (`services/api/glow_profiles/requirements.py`, lines 122 to 124). No check runs, since the seam's fixture adapter passes no one, and the staff approval is off at launch. So no profile can become `visible`.
- **A photo reaches `approved` only by the automated check** (`media.run_check`). With no check in use, no photo is approved, so the photo requirement cannot be met either.

Nothing is live, so this costs nothing yet. It must land before P10, whose evidence runs onboarding to a visible profile (DM-84 section 5).

## Outcome

A profile can become `visible` in the MVP with every requirement but identity verification met, and a photo is approved while the photo check's toggle is off. The identity record, its port and the staff approval stay, ready for ID validation later. The toggle is a setting in D2's store, off at launch, on OD-60's pattern.

## Design

- **R1 — The identity requirement is set aside** (OD-68: "ID validation set aside for now but kept possible later").
  - **Recommended (a):** `missing()` no longer checks identity verification while ID validation is set aside, and the completion read never reports `identity_verification`. The module's docstring says the requirement is set aside (OD-68).
    - **Kept unchanged:** the `IdentityVerification` record and its port; the staff approval without ID verification, its revocation and their setting (`identity.staff_approval`, off at launch); and their tests. With no identity requirement an approval meets nothing: its recompute changes no profile whose state is current (D9's recompute still catches up a profile left stale, as `completion.every_requirement_writer…` shows; the exact-head review's N1, the manager, revision 7), and it still bumps `eligibility_version`, writes `StaffAudit` and emits its event. That is DM-84's "it waits": D18's code and setting stay, and nothing changes now.
    - **The contract's closed list keeps `identity_verification`** (`gapp-api-v1.schema.json`, the completion read's `missing`), so ID validation can return without a contract change. Its description already defines the value and is left unchanged.
    - **When ID validation is added,** its own brief re-adds the requirement and decides what happens to profiles already `visible`. That is outside this change.
  - **(b), not recommended:** a setting in D2's store ("identity verification required"), off at launch. A setting nobody can usefully turn on until a verification company and its adapter exist adds a mass-demotion path to build and prove now. Nathan asked for a toggle for the photo check only (OD-68).
  - **No member is live,** so no data migration of existing profiles is needed.

- **R2 — The photo check's toggle** (OD-68: "We can drop it but I want toggle for this"). These are DM-84 section 5's defaults, Dev Manager 5's and not Nathan's words; he can change any of them (OD-68's row).
  - **The setting:** `media.photo_check`, with the content `{"enabled": false}` under a closed schema, in D2's store. It is versioned, audited and published like every other setting, and emits `policy_published`. Version 1 is seeded by a new data migration, with the staff subject `system:launch-default` and the reason "OD-68". P07's console exposes it later.
  - **It covers the automated check only** (`PhotoCheckPort`). Glow's processing, which strips a photo's metadata, and G-02's seam are not the photo check. Every photo still passes F05's `review` as now.
  - **`run_check` reads it** in its one `read_shared` call, with `consent.onboarding` and `media.policy`. The new setting takes its place in D19's single pointer order.
  - **While it is off:** `run_check` approves a photo from `review_pending` by F05's existing `approve` (role `system`) without calling the check port. The approval is recorded under the toggle's own subject and reason (recommended: `system:photo-check-off` and `photo_check_off`), never under `system:photo-check` with `automated_check`, so no record says the check approved it. As today:
    - an asset under a staff restriction is not approved;
    - the hold port is asked first;
    - an asset with no variant is refused;
    - the approval ends with D9's recompute.
  - **While it is on:** `run_check` is unchanged; the check port decides.
  - **Turning it on:** new photos wait for the check. A photo approved while it was off stays shown and goes through the check. A new system step, `recheck`, takes one `approved` asset whose approval carries the toggle's reason and asks the check port:
    - **approve:** the hold port is asked first, as before every approval, and a held asset is `no_change`; otherwise the asset stays `approved`, and the check's decision is recorded (`StaffAudit` with `system:photo-check` and `automated_check`, and the asset's review reference moved to it), so the step no longer finds it;
    - **reject:** the asset leaves view (`rejected`, delivery withheld), and D9's recompute follows, which demotes a `visible` profile when it was the last approved photo (`requirement_removed`);
    - **undecided:** nothing changes.

    A read lists the assets awaiting it, for P11's worker; SV2 has no worker, and tests drive the step. The step takes the account row lock first and refuses an account that is not `active`, as every other system step does (DM-58 item 9). It reads the toggle in its one `read_shared` call, with `consent.onboarding` and `media.policy` as `run_check` does, and while the toggle is off it changes nothing and does not call the check port.
  - **F05's registry gains two `system` transitions out of `approved`:** `approve` (`approved` to `approved`) and `reject` (`approved` to `rejected`), each with the policy `A05`, in `packages/contracts/production/flows-v1.json` and `glow_domain.media.TRANSITIONS` alike. F05 has none today, since `restrict_media` is the moderator's (DM-84 section 5 named one; the check's approval of a shown photo needs the second, so that it is a recorded transition and not an unrecorded change of reference). Every other unlisted transition stays forbidden.
  - **Turning it off again:** photos waiting in `review_pending` are approved by `run_check`'s off branch under the toggle's reason. Photos the check approved stay as they are.
  - **Throughout:** staff act on reports (OD-61's no-staff-review part stands); `restrict_media` works in both states; neither the toggle nor the check clears a staff restriction.

- **R3 — The photo requirement stands:** at least one approved photo (`requirements.py`, line 118). Only how a photo reaches `approved` changes, and the module's docstring says so for each state of the toggle.

- **R4 — The fixed limits and the seal:** unchanged. No new dependency, no provider call, and the runtime stays sealed (SV2's D13 and D14). Every test comes with its reversal, recorded with its failing output (D15).

## Owned paths (the session)

- `services/api/glow_profiles/requirements.py`, `media.py`, `media_fixtures.py` and `settings_store.py`;
- `services/api/glow_domain/media.py` and `profile_settings.py`;
- a new migration under `services/api/glow_persistence/migrations/` (the setting's seed);
- `packages/contracts/production/flows-v1.json`, and the package's README, which records each change to the registry (as SV2's Stage B did); regeneration is run to show that no generated output changes;
- tests under `services/api/tests/` and `packages/contracts/tests/`;
- the proof's profile suite, `proofs/postgres-ordering/glow_ordering_proof/profile_cases.py` and `profile_support.py`, for acceptance checks 1, 3 to 6 and 9 on the disposable database and for the earlier cases "Earlier tests" names (the manager, revision 3);
- the proof's offline test of the profile suite's plan, `proofs/postgres-ordering/tests/test_profile_offline.py`, for its pins on the plan only (the case count, a list of SV2-R's own cases with its rule, and `LABEL_BINDINGS`), each change recorded with what it now pins (the manager, revision 5; DM-93);
- `proofs/postgres-ordering/README.md`, for the profile suite's paragraph only (line 17 today): its case count and what SV2-R's cases add, as each earlier stage's are recorded there (DM-93);
- the record, `docs/testing/evidence/<the session's date>-sv2-r-requirements-change.md`.

A change any other path needs, `apps/mobile` included (its interactions fixture imports the flow registry), is stopped and reported before it is made.

## Manager-owned

This brief and the prompt; the SV2 brief's D2, D9, D10 and D18 notes at integration; the carried-items file (P07, P10); the P11 plan's SV2 entry (`docs/testing/p11-deferred-acceptance.md`); the handoff; the owner-direction register; the review log; PF01.

## Exclusions

- **The card check and the free trial** (OD-68, OD-69, OD-70): the card is not a profile requirement (OD-70, C1; DM-87 section 8: "The offer adds a kind of entitlement, not a profile requirement"). **Whether an entitlement (a trial, a payment or a grant) gates visibility** is the billing item's (P08.3) to decide, not this change's.
- The staff approval's future, OD-64's birth-date lock, G-02's detection choice and the staff grant: each waits where DM-84 section 5 and the carried items place it.
- Any change to the contract's schema, the mobile app, Stream, a database outside the test job, HDE or Railway; any real provider.

## Dependencies and inputs

The SV2 brief (D2, D9, D10, D13 to D15, D18 and D19); OD-68 in the register; DM-84 section 5; the SV2 evidence record; P06.DB's disposable-PostgreSQL job.

## Acceptance checks

1. **Completion without identity verification:** a profile with every other requirement met and no `verified` or `staff_approved` record becomes `visible` at the recompute, and the completion read never lists `identity_verification`. With the old check restored, the test fails (its reversal).
2. **The staff approval is unchanged:** gated by its setting, audited, bumping `eligibility_version`; its approval and revocation change no profile's visibility.
3. **Toggle off:** `run_check` approves a `review_pending` asset with a variant under the toggle's subject and reason, and a spy check port shows no call. A restricted asset is not approved, a held asset is `no_change`, an asset with no variant is refused, and the recompute makes a complete profile `visible`.
4. **Toggle on:** `run_check` behaves as before. The existing tests of the check's decisions pass with the toggle published on in their setup, and with no other change to what they assert (the manager, revision 3: the seed is off, so without it they would see approvals under the toggle's reason).
5. **The recheck:** for an asset approved under the toggle's reason, approve records the check's decision and the read no longer lists it; reject withholds delivery and demotes a `visible` profile whose last approved photo it was; undecided changes nothing; a held asset is `no_change`, with nothing written. The read lists only such assets of active accounts. An asset of an account that is not `active` is refused. With the toggle off, the step calls no check port and changes nothing.
6. **Toggle off again:** a `review_pending` asset is approved under the toggle's reason.
7. **The setting:** version 1 is seeded with `{"enabled": false}`, `system:launch-default` and "OD-68", with its pointer and its `StaffAudit` row (`seed_launch_default`) as `0007` and `0009` write theirs, so that the profile suite's `settings.launch_defaults` passes unchanged; a publication outside its closed schema is refused before anything is written; a publication writes `StaffAudit` and emits `policy_published`.
8. **The registry:** `flows-v1.json` and `TRANSITIONS` agree, the contract's transition tests pass, and every unlisted transition is still forbidden.
9. **Locks:** a publication of the toggle, `run_check` and the recheck serialize on the setting's pointer lock, in D19's order, on the disposable database.
10. **The seal test and the full suite pass;** no new dependency.
11. **The PR run on the head:** all eight Foundation jobs, with the Database proof checks on P06.DB's disposable PostgreSQL.
12. **Each new or changed test's reversal** is recorded with its failing output.

## Earlier tests (the manager, revision 3)

The rule is SV3's (DD5): an earlier test that R1 or R2 is expected to change is named here, with the reason, and any other earlier test that no longer passes is a stop, reported and not changed. By the manager's reading of the brief's start commit, these are expected to change, and each change is named in the record:
- **R1, identity no longer reported:** the profile suite's completion cases that expect `identity_verification` in the completion read (`profile_cases.py`: `completion.refuses_each_missing_requirement`, whose profile stays for identity verification; `completion.needs_the_chart_and_identity_verification_seeded`; and `completion.every_requirement_writer_meeting_the_last_one_makes_it_visible`, where only verification is missing). Their `seed_verified` calls may stay: a verified record meets nothing now, as a staff approval meets nothing (acceptance check 2). Two more expect a revocation of the staff approval to demote a profile: `staff.approval_gated_narrow_survives_and_is_revocable` ("revoked: demoted") and `completion.removals_demote_and_empty_values_are_refused` (its revocation's removal). Each now expects the profile to stay as it was (acceptance check 2). Not expected to change: the discovery suite's `plans.population_and_bounds`, outside the owned paths, calls `requirements.missing(account_id, profile, label)`, as `operations.py` and `recompute.py` do, so R1 changes only the function's body and its signature stays (DM-93).
- **R2, the toggle seeded off:**
  - the profile suite's cases that drive `run_check` with a deciding, rejecting or holding check port, the runtime's check among them, which publish the toggle on in their setup (acceptance check 4);
  - `services/api/tests/test_profile_media.py`'s AST tests on `run_check`, which assert one approval in `media.py` and the hold port before it: they name each approval, the off branch's and the recheck's included, and keep the hold port asked before every approval, the recheck's included; the same file's list of the names no view or URL may reach (`test_no_member_route_reaches_a_provider_system_or_staff_step`) gains the recheck and its read;
  - the writer and command lists of `test_profile_recompute.py` (`WRITERS`) and `test_profiles_offline.py` (`MEDIA_COMMANDS`, and the names no view or URL may reach), which gain the recheck, as does the profile suite's `media.every_other_photo_step_refuses_an_inactive_owner` (acceptance check 5);
  - the tests that list the migrations or the launch reasons: `test_model_definitions.py`'s migration leaf, `0011_interaction_undo` today, which becomes the new migration, with a test that it follows `0011` as each earlier one follows its own (its assertion that `0007` seeds exactly `SEEDED_BY_0007`'s defaults stays, since `SEEDED_BY_0007` does not change; the next one, that `0007` seeds every setting but those seeded after it, line 338's `set(ps.ALL_SETTINGS) - {ps.MEDIA_POLICY}`, adds the toggle to the settings it leaves out (the manager, revision 5, correcting YY7's words, which kept both)); and `test_profile_settings.py`'s launch-reason test, whose set of every other setting's reason (`{"OD-60"}`) leaves out `media.photo_check`, and which asserts its "OD-68".
  - `test_profile_recompute.py`'s state-write guard, which names every state write it sees by file, line, function and statement (`NOT_A_PROFILES_STATE`): if SV2-R moves `transition`'s one state write in `glow_profiles/media.py` (line 128 today, `asset.state = after`), its entry takes the new line number, as Stage B's moved lines did ("so their numbers move with them"); the off branch and the recheck write a photo's state only through `transition`, so the guard's set otherwise stays as it is (DM-93).
  - the proof's offline test of the profile suite's plan (`proofs/postgres-ordering/tests/test_profile_offline.py`), whose pins change with every stage's cases (DM-57 section 5): `test_the_case_count_is_pinned` (`CASE_COUNT`, 69 today, set in `profile_cases.py`), `test_the_plan_covers_every_acceptance_check` (exactly 15 `media.` and `pointers.` cases, each naming check 10, 12 or 13 of SV2's brief), and `test_every_binding_of_a_label_name_is_pinned` (`LABEL_BINDINGS`). SV2-R's new cases take a prefix of their own (for example `sv2r.`) and name SV2-R's acceptance checks in a form the plan test cannot read as SV2's (for example `"SV2-R 3"`), as SV3's correction B-C1 named its own (`test_discovery_offline.py`, `B_C1_CASES`); so the Stage B list and its rule stay as they are. The case count is pinned anew; the plan test gains a list of SV2-R's new cases, pinned by name, with its own rule: each names at least one of SV2-R's checks, and each of checks 1, 3 to 6 and 9 is named by a case of the plan. `LABEL_BINDINGS` is pinned anew for the new cases' bindings, while `LABEL_NAMES` stays as it is: the new labels interpolate only the names it holds ("a new name here is read before it is added"), and a case that needs another name is stopped and reported. No pin is loosened (the manager, revision 5; DM-93).

## Classification expectation

Full scope: code, a migration and the flow registry.

## Evidence home

The session's record; the manager's verification is added to it as a section.

## Report format

Branch, start and head SHAs, changed paths, what was built against R1 to R4, every acceptance check with its exact result and each reversal's failing output, the PR run's ID and jobs, deviations and open questions.

## Review plan

Full scope: Codex on every head; an exact-head code review in a review session, prompted after the implementation report is verified; corrections and re-reviews as findings need; the Dev Manager's pre-merge read of any governing change. The PR merges after its run and Codex's summary on the final head and its checklist.

## Correction C1 (after the exact-head review; the manager, revision 7)

The exact-head review of `f4703a1` ([the record](../testing/evidence/2026-11-18-sv2-r-requirements-change.md), "Exact-head review") found the code right and two guards untested. Both fall in its prompt's correction class "let a test pass where it should fail", so they are fixed before the merge (the manager workflow, step 6, rule (a)). C1 adds tests only: **no code changes.** A new test that fails against the code at `f4703a1` is a stop, reported with its output.

- **C1.1, the recheck's state condition (the review's R1).** No test calls `recheck` on a photo that is no longer `approved`. Removing `asset.state != md.APPROVED` from its refusal (`glow_profiles/media.py`, lines 758 to 762 at `f4703a1`) passed every suite (the review's reversal B). Under that change, a photo approved while the toggle was off and then restricted by staff (`review_pending`, its review reference kept) would be rejected by the check through F05's `reject` from `review_pending`. The tests:
  - offline, in `services/api/tests/test_sv2r_requirements.py`: a structural test that the recheck's refusal `not_awaiting_recheck` holds unless the photo's state is `md.APPROVED`, and comes before any port call or write;
  - on the disposable database, inside `sv2r.the_recheck`: with the toggle on, a photo approved while it was off and then restricted by staff, and another removed by its owner, each rechecked with a rejecting check and with an approving one. Each gives `no_change` with `not_awaiting_recheck`; the check port is not called; nothing is written (the photo's state, version and review reference, its audit rows and its events unchanged); and `awaiting_recheck` lists neither.
- **C1.2, `run_check` on an approved photo (the review's R2).** SV2-R's two transitions out of `approved` mean the registry no longer refuses `approve` or `reject` from `approved`, so `run_check`'s `not_in_review` refusal (lines 638 and 639) is all that stops it acting on an approved photo, and no test calls it there (the review's reversal A). The tests:
  - offline, in `test_sv2r_requirements.py`: a structural test that `run_check`'s refusal on state admits only `md.REVIEW_PENDING`, before the restriction check and the toggle's branch;
  - on the disposable database, inside existing `sv2r.` cases (for example `sv2r.toggle_on_the_check_decides_as_before` and `sv2r.toggle_off_approves_without_the_check`): `run_check` on an approved photo, with the toggle on and with it off, gives `no_change` with `not_in_review`, with the check port not called and nothing written.
- **C1.3, the reversals.** Each is recorded with its failing output, offline and, where Docker allows, on a local disposable database under P06.DB's D4 (the run of record is CI's):
  - the review's reversal A, `run_check`'s state refusal admitting `approved`: C1.2's tests fail;
  - the review's reversal B, the recheck's refusal without its state condition: C1.1's tests fail.
- **C1.4, the carried entries due at SV2-R** (the carried-items file, "Carried to the next change to SV2's profile guards and suite"). SV2-R changed `test_profile_recompute.py`, `test_profile_media.py` and `profile_support.py`, and each carries an entry for the next change to its file, which this brief did not take up (AM12-26). C1 takes each up as its entry says, each widened guard with a reversal for a spelling it now sees:
  - **N-a,** `services/api/tests/test_profile_recompute.py`: the creation guard also sees an async create (`acreate`, `aget_or_create`, `aupdate_or_create`) and a clone saved with `force_insert=True` after `pk = None`;
  - **N-d,** `services/api/tests/test_profile_media.py`: the held branch's offline write list also names `.update(`, `bulk_create` and `events.emit(`;
  - **N-c,** `proofs/postgres-ordering/glow_ordering_proof/profile_support.py`: the module docstring says the ledger holds the start of each object's bytes, the first 24, as their hex and their `repr`.
- **C1.5, the record.** Acceptance check 2's row says the approval's recompute moves no profile whose state is current, and that D9's recompute still catches up a profile a test left stale (the review's N1). A new section, "Correction C1", records each test, each reversal and its failing output, each carried entry taken up, the local checks and the run of record.
- **Owned paths (C1):**
  - `services/api/tests/test_sv2r_requirements.py`, new tests;
  - `services/api/tests/test_profile_recompute.py` and `test_profile_media.py`, N-a's and N-d's guards only;
  - `proofs/postgres-ordering/glow_ordering_proof/profile_cases.py`, the `sv2r.` cases only, extended: no new case, so `CASE_COUNT` (77), `SV2R_CASES`, `LABEL_BINDINGS` and the proof README's count stay;
  - `profile_support.py`, N-c's docstring and, if one is needed, a helper only the `sv2r.` cases use;
  - the record.

  Any other path, any other earlier test changed, a new case, or a code change is a stop.
- **Its review:** C1 changes no code, so a delta review follows (the manager workflow, step 6: a correction of 60 or fewer non-test lines), after Codex's pass on the commit that holds its prompt; then the merge.

## Sessions

- **The implementation session** (`claude/intelligent-curie-i27kvt`, from `9c888c0`, the prompt's revision 1; 18 November 2026) passed the start gate and the environment check, read the brief and the code, and stopped under the stop rule before changing anything: the work needed `proofs/postgres-ordering/tests/test_profile_offline.py`, outside the owned paths, whose three pins any new profile case breaks, and YY7's words kept line 338 of `test_model_definitions.py`, which fails once `ALL_SETTINGS` gains the toggle. No file was changed and nothing was pushed. Both findings were checked against the code by the manager and are corrected in revision 5 (AM12-24).
- **The implementation session, on the prompt's revision 2** (`claude/intelligent-curie-i27kvt`, from `80bed4a`; 18 November 2026): R1 to R4 built, the earlier tests changed as "Earlier tests" names them, eight `sv2r.` profile cases added (`CASE_COUNT` 77) and the proof README's paragraph updated; code head `f4703a1`, records head `587f4a2`. Its run of record, 44362141024 on `f4703a1`, passed all eight Foundation jobs; the profile suite passed 77 of 77. Verified by the manager ([the record](../testing/evidence/2026-11-18-sv2-r-requirements-change.md), "Manager verification") and merged into the manager branch; its pull request and exact-head code review follow.
- **The exact-head review** (a review session on the review prompt, revision 1, at `e2bacf7`, of code head `f4703a1`; 18 November 2026): changes requested, for tests only. It found no defect in the code; two should-fix findings in the class "let a test pass where it should fail" (R1, the recheck's state condition untested; R2, `run_check` on an approved photo untested), each shown by a reversal that passed every suite, the PostgreSQL profile suite included; and four nits (N1 to N4). The four required reversals failed their tests; the API's 642 tests, the contracts' 53 and the proof's 377 passed, and the profile suite passed 77 of 77 locally. Disposed of in [the record](../testing/evidence/2026-11-18-sv2-r-requirements-change.md), "Exact-head review": R1, R2 and N1 to correction C1 (above), with the carried entries due at SV2-R (AM12-26); N2 and N3 to the carried-items file; N4 to the P11 plan, with DM-91 section 4.3's note (AM12-25).

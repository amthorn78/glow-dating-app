# SV2-R: SV2's completion requirements after OD-68 (evidence)

- **Work item:** SV2-R ([brief](../../planning/sv2-r-od-68-requirements-change.md), revision 6, with DM-84 section 5 and DM-91 to DM-93's conditions; OD-68). The identity requirement is set aside (R1), the automated photo check goes behind a toggle, `media.photo_check`, off at launch (R2), the photo requirement stands (R3), and the fixed limits, the seal and D15's reversals are unchanged (R4).
- **Sealed:** nothing here is served. The new code runs only under the disposable-PostgreSQL proof's profile settings, and the served runtime imports no new module (D13; `tests/test_profiles_sealed_runtime.py` passes unchanged). Local database runs are iteration, not evidence. The evidence of record is the CI run on the code head, below.

## The session

- **The prompt:** SV2-R's implementation prompt, revision 2, from `80bed4a4b5fdd25e8ffaad506d4355cd8e794efb` of `claude/magical-wozniak-yfmmx2`, started by Nathan. The same session had run revision 1 (from `9c888c0`) and stopped under its stop rule before changing anything. The brief's "Sessions" records that stop.
- **The branch:** `claude/intelligent-curie-i27kvt`. Revision 2 reset it to `80bed4a`. Its name matches `claude/**`, so the Foundation workflow runs on its pushes.
- **The code commit:** `f4703a1` (**the code head**), one commit holding every code, test, contract and proof change below.
- **The records commit** (this file) follows the run of record (run 44362141024, on `f4703a1`), as the push rule requires.

## Start gate and environment

- **The environment check, names only.**
  - None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` was set, and no `STREAM_*` or `PG*` name.
  - Present: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_CA_BUNDLE`, and the GitHub token names `GH_TOKEN` and `GITHUB_TOKEN`. None of their values was read, printed or passed to a command.
  - Every repository command ran in a clean process environment (`env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus `GLOW_ENV=test` for the API). The proxy and CA variables were passed by reference only to `pip` and `npm ci`.
- **The toolchain:** CPython 3.12.14 (`python3.12`), Node v24.19.0, npm 11.9.0, Docker 29.10.0 (build `fdd4b8e`).
- **The start gate**, each line as the prompt has it:
  - fetched both branches;
  - `git rev-parse HEAD` printed `80bed4a4b5fdd25e8ffaad506d4355cd8e794efb`;
  - `PR53's merge present`;
  - `main's code`: no non-Markdown path differs from `15d54f6`;
  - no owned path or the brief differs from the live manager branch, whose head was `80bed4a`;
  - `0` SV2-R records;
  - the migrations were `0001` to `0011` only.

## What was built

| Item | Files | What |
|---|---|---|
| **R1** | `glow_profiles/requirements.py` | `missing()` no longer checks identity verification, so the completion read never reports `identity_verification`. Its signature `(account_id, profile, onboarding_policy_version)` is unchanged (DM-93 ZZ2), and the module no longer imports `IdentityVerification`. The closed list `ALL` keeps the value, so the contract's `OwnCompletion` is unchanged. The record, its port, the staff approval, its revocation and their setting are unchanged. The module's docstring says the requirement is set aside (OD-68). |
| **R2: the setting** | `glow_domain/profile_settings.py`; `glow_persistence/migrations/0012_photo_check_seed.py` | `PHOTO_CHECK = "media.photo_check"`, in `ALL_SETTINGS` (not in `SEEDED_BY_0007`). Its launch default is `{"enabled": False}` and its launch reason `OD-68`. Its closed schema is the one key `enabled`, a boolean: anything else is `schema`, refused before any write. Migration 0012 follows `0011` (see "The setting"). |
| **R2: `run_check`** | `glow_profiles/media.py`, `glow_domain/media.py` | One `read_shared` call for `[consent.onboarding, media.photo_check, media.policy]`, in name order (D19). While the toggle is off, the check port is not called, and the asset is approved by the same `approve`, under `system:photo-check-off` and `photo_check_off` (`PHOTO_CHECK_OFF_SUBJECT`, `PHOTO_CHECK_OFF`). A restriction, a missing variant and the hold port stop it as they stop the check's approval, and it ends with D9's recompute. While the toggle is on, `run_check` is unchanged. |
| **R2: `recheck` and its read** | `glow_profiles/media.py` | `recheck(asset_id)` is a system step (see "`run_check`'s off branch and the recheck"). `awaiting_recheck()` lists, oldest first, the IDs of every `approved` photo of an `active` account whose review reference is an approval `StaffAudit` row with the toggle's subject and reason. It is for P11's worker. No route or view reaches either one. |
| **R2: the registry** | `packages/contracts/production/flows-v1.json`, `glow_domain/media.py` (`TRANSITIONS`), `packages/contracts/README.md` | F05 gains `approve` (`approved` to `approved`) and `reject` (`approved` to `rejected`), each `system` with `A05`, after the existing thirteen. No existing entry or DTO changes. |
| **R3** | `glow_profiles/requirements.py` | The photo requirement is unchanged (at least one approved photo). The docstring says how a photo reaches `approved` with the toggle off and with it on, and what the recheck does. |
| **R4** | (none) | No new dependency, no pin changed, no provider call. `glow_api/` is unchanged, and the seal test passes unchanged. `media_fixtures.py` and `settings_store.py` are owned paths that needed no change. |

## The setting

- **The schema:** `{"enabled": <bool>}`, closed (`_photo_check_refusals`). `{}`, `{"enabled": 1}`, `{"enabled": 0}`, `{"enabled": "true"}`, `{"enabled": None}`, an extra key, another key, a list, `True` and `None` are each `('schema',)`. Either boolean publishes, over either current value.
- **The seed:** `0012_photo_check_seed.py`, SHA-256 `4e40028b63947646da1c03443f86304189069a5caf596f8752ef9e65761f39d2`, depends on `0011_interaction_undo`. It holds one reversible `RunPython`, with no `RunSQL`, no outbox event and no network module. It writes, as `0007` and `0009` write theirs:
  - **the version:** `SettingVersion` `media.photo_check` number 1, `{"enabled": false}`, `system:launch-default`, `OD-68`, at the database clock;
  - **the pointer:** `PolicyRevision` `media.photo_check`, `policy_version` `media.photo_check.v1`, naming that row;
  - **the audit row:** `StaffAudit` with `system:launch-default`, scope `settings`, action `seed_launch_default`, the version's ID, reason `OD-68`, a new request ID, `before_version` none and `after_version` 1.

  The reverse removes all three. `test_sv2r_migration_follows_0011` pins the file and asserts each of these. The profile suite's `settings.launch_defaults` passes unchanged: "16 settings read their launch defaults", and the `seed_launch_default` rows number `len(ALL_SETTINGS)`.
- **Publication:** `staff.publish_setting` passes the toggle to `settings_store.publish` unchanged, which writes `StaffAudit` (`publish`) and emits `policy_published` (`sv2r.the_toggle_is_a_setting`).

## `run_check`'s off branch and the recheck

- **`run_check`:**
  1. `lock_account` (refuses an account that is not `active`);
  2. one `read_shared` of the three pointers; `checking = found[ps.PHOTO_CHECK].content['enabled'] is True`;
  3. the asset `FOR UPDATE`;
  4. not in review: `no_change`;
  5. restricted: `no_change` (before the branch, so the toggle never clears a restriction);
  6. the variant;
  7. `if checking:` the check port decides, under `CHECK_SUBJECT` and `APPROVED_BY_CHECK`. `else:` `decided = md.CheckDecision('approve')`, with no port call, under the toggle's subject and reason;
  8. undecided: `no_change`;
  9. on approve: no variant is refused; the hold port is asked (`held`: `no_change`); then the audit row with the branch's subject and reason, the `approve` transition with a delivery reference and the review reference, and D9's recompute. On reject (with the toggle on only): as before.
- **`recheck`:**
  1. `lock_account`;
  2. one `read_shared` of the same three pointers;
  3. the asset `FOR UPDATE`;
  4. toggle off: `no_change` (`photo_check_off`), before any port, write or recompute;
  5. not `approved`, or its review reference not the toggle's approval: `no_change` (`not_awaiting_recheck`);
  6. the variant; the check port decides;
  7. undecided: `no_change`;
  8. on approve: no variant is refused; the hold port is asked first (`held`: `no_change`, nothing written); then `StaffAudit` with `system:photo-check` and `automated_check`, and F05's `approve` from `approved`, with a new delivery reference and the review reference moved to that row. There is no recompute, since the photo stays approved;
  9. on reject: `StaffAudit` with the check's subject and reason, F05's `reject` from `approved` (delivery withheld), then D9's recompute (`requirement_removed` when it was the last approved photo).
- **The AST tests that pin them** (`services/api/tests/test_profile_media.py`):
  - `PhotoCheckToggleTests` holds:
    - the toggle read in each step's one `read_shared` call, in name order;
    - the off branch with no `adapters.check`, no `CHECK_SUBJECT` and no `APPROVED_BY_CHECK`;
    - the one check-port call in `run_check`;
    - the restriction before the branch;
    - the recheck's off guard first, its one statement `return Result('no_change', reason='photo_check_off')`, with nothing before it calling a port or writing;
    - the recheck's approve, reject and undecided branches;
    - the read's filters, with no lock, transaction or port.
  - `RouteTests` holds:
    - each approval in `media.py` named by its step (`["recheck", "run_check"]`), the hold port asked before each;
    - `held_before_every_write`, correction C2's rule applied to both steps;
    - the route-reach list.
  - `AccountStateTests` (unchanged) holds the recheck's first statement to `lock_account`.

## The registry's two entries

- **The entries:** `{"event": "approve", "from": "approved", "to": "approved", "role": "system", "eligible": false, "policies": ["A05"], "active_match": false}` and `{"event": "reject", "from": "approved", "to": "rejected", ...}`, the same otherwise. `TRANSITIONS` gains `("approve", APPROVED): (APPROVED, "system")` and `("reject", APPROVED): (REJECTED, "system")`. `test_the_writers_table_is_f05s_registry` holds the two tables equal.
- **The examples:** `test_sv2r_f05_system_transitions_out_of_approved` checks:
  - **allowed:** the system with `A05`, for both;
  - **`forbidden`:** the owner, a moderator and a participant;
  - **`policy_unresolved`:** the system without `A05`;
  - **`state_conflict`:** `approve` to `rejected` or to `review_pending`, `reject` to `approved` or to `review_pending`, and `review`, `uploaded` and `purged` from `approved`;
  - **the pin:** F05's five transitions out of `approved`.
- **Regeneration:** `npm run generate --prefix packages/contracts`, run twice. Each exited 0, and `git status` showed no change to any generated output either time.

## The earlier tests changed (the brief's "Earlier tests")

| Test or case | Reason | Before | After |
|---|---|---|---|
| `test_model_definitions.py`, `test_sv2_stage_a_migrations_follow_0004` | migration leaf; `0007`'s left-out settings | leaf `0011_interaction_undo`; `set(seed.SEED) == set(ps.ALL_SETTINGS) - {ps.MEDIA_POLICY}`. Failed at the change: `AssertionError: [('glow_persistence', '0012_photo_check_seed')]` | leaf `0012_photo_check_seed`; `... - {ps.MEDIA_POLICY, ps.PHOTO_CHECK}`. Line 337 (`SEEDED_BY_0007`'s defaults) unchanged. New `test_sv2r_migration_follows_0011` |
| `test_profile_settings.py`, `test_the_launch_values_are_od60s_and_od61s` | launch reasons | `{"OD-60"}` for every setting but D18's and the media policy | leaves out `PHOTO_CHECK` too, and asserts its `OD-68` and `{"enabled": False}` |
| `test_profile_media.py`, `test_every_photo_state_write_goes_through_the_registrys_table` | one approval in `media.py` | `len(approvals) == 1` (failed at the change: `2 != 1`) | approvals named by step, `["recheck", "run_check"]`, the hold port before the recheck's audit row and transition |
| `test_profile_media.py`, `test_a_hold_returns_before_the_approval_writes_anything` | the hold port before every approval (DM-92 YY1, YY5) | `run_check` only | `run_check` and `recheck`, each with one hold guard before every write; the recheck writes no recompute |
| `test_profile_media.py`, `test_no_member_route_reaches_a_provider_system_or_staff_step` | the names no view or URL may reach | eight names | adds `recheck` and `awaiting_recheck` |
| `test_profile_media.py`, `test_the_writers_table_is_f05s_registry` | the two transitions | the table equal to the registry | also both new entries `system`, exactly five transitions out of `approved`, and no `uploaded`, `review`, `purged` or `upload_grant` from it |
| `test_profile_recompute.py`, `WRITERS` | the recheck's rejection recomputes | eleven writers | adds `("media.py", "recheck"): "OTHER_FLOW"` |
| `test_profile_recompute.py`, `NOT_A_PROFILES_STATE` | `transition`'s state write moved (DM-93 ZZ3) | `("glow_profiles/media.py", 128, "transition", "asset.state = after")` (failed at the change: seen at 132) | the same at line 132; the set otherwise unchanged |
| `test_profiles_offline.py`, `MEDIA_COMMANDS` | the recheck is a system step | eight commands (failed at the change: `recheck` found, not listed) | adds `recheck` |
| `completion.refuses_each_missing_requirement` | R1 | `stays(member, ["identity_verification"], ...)` | with the chart seeded and no verification, the edit makes it `visible` and the read lists nothing |
| `completion.needs_the_chart_and_identity_verification_seeded` | R1 | missing `["chart", "identity_verification"]`; incomplete after the chart seed | missing `["chart"]`; `visible` after the chart seed; the rest unchanged |
| `staff.approval_gated_narrow_survives_and_is_revocable` | R1 (check 2) | "revoked: demoted" (`incomplete`) | "revoked: stays visible" |
| `completion.removals_demote_and_empty_values_are_refused` | R1 (check 2) | the revocation demoted, or stayed paused | the revocation leaves the profile as it was (visible, or paused); 8 removals demote |
| `completion.every_requirement_writer_meeting_the_last_one_makes_it_visible` | R1 | `missing == ["identity_verification"]` before the staff approval | `missing == []`: the seed met the last requirement without a write, and the approval's recompute makes it visible |
| `media.an_upload_moves_only_through_quarantine_the_seam_and_review`, `media.the_checks_decisions_are_the_systems_and_never_clear_a_restriction`, `media.a_hold_stops_the_checks_approval`, `media.the_photo_requirement_completes_and_its_removal_demotes` | R2 (check 4) | no toggle | `ctx.photo_check(True)` in their setup; nothing they assert changes |
| `profile_support.approved_photo` | R2 (check 4); see "Deviations" | `run_check` with the test's `DecidingCheck` | the same, with `photo_check(True)` in its setup |
| `media.every_other_photo_step_refuses_an_inactive_owner` | R2 (check 5) | five steps per owner; the photo through `approved_photo` | the photo approved while the toggle is off (listed by the read while the owner is active); the recheck refused for an inactive owner with no check-port call; the read leaves it out; six steps per owner |
| `test_profile_offline.py`, `test_the_case_count_is_pinned` | SV2-R's eight cases | `CASE_COUNT == 69` | `77`, and `plan()[69:] == SV2R_CASES` |
| `test_profile_offline.py`, new `test_sv2rs_own_cases_name_its_checks` and `SV2R_CASES`, `SV2R_CHECKS` | DM-93 ZZ4 | none | each SV2-R case under `sv2r.`, naming at least one `SV2-R <n>` and no SV2 check number; each of checks 1, 3 to 6 and 9 named; only those cases take the prefix |
| `test_profile_offline.py`, `test_the_plan_covers_every_acceptance_check` and `LABEL_BINDINGS` | DM-93 ZZ4 | 15 Stage B cases; the bindings | unchanged: no new case takes a Stage B prefix, and no new or changed line binds a name in `LABEL_NAMES`, so the pins found equal the old pins. `LABEL_NAMES` unchanged |
| `proofs/postgres-ordering/README.md`, line 17 | DM-93 ZZ1 | 69 cases | 77 cases, and what SV2-R's add |

No other earlier test or case changed or failed, in the API suite, the contract tests, the proof's offline tests or the four suites of the run of record.

## The acceptance checks

Local results are this session's runs. The run of record is below.

| Check | Tests | Result | Reversal and its failing output |
|---|---|---|---|
| **1** completion without identity verification | `test_sv2r_requirements.py` (AST, signature, behaviour under a dummy backend, the closed list, D18 kept, the docstring); `sv2r.a_profile_completes_without_identity_verification`; the R1 changes above | pass | **The identity check restored in `missing()`.** Offline: `FAIL: test_missing_reads_no_identity_verification ... AssertionError: 'IdentityVerification' unexpectedly found in 'def missing(...`, and `FAIL: test_with_every_other_requirement_met_nothing_is_missing`. On a local database: `[profile] cases: 68/77 passed`, with `FAIL sv2r.a_profile_completes_without_identity_verification ...: FAILED: nothing is missing without identity verification` and the five R1 cases each failing at their new assertion (for example `completion.refuses_each_missing_requirement ...: FAILED: identity verification: set aside`) |
| **2** the staff approval unchanged: gated by its setting, audited and bumping `eligibility_version`; its approval and revocation move no profile whose state is current, and D9's recompute still catches up a profile a test left stale (`completion.every_requirement_writer…`, where the seed met the last requirement without a write and the approval's recompute makes the profile visible; the exact-head review's N1, corrected in correction C1) | `sv2r.the_staff_approval_meets_nothing`; `staff.approval_gated_...`; `completion.removals_...`; `test_sv2r_requirements.test_d18_stays` | pass | Covered by check 1's reversal on the database: `FAIL sv2r.the_staff_approval_meets_nothing ...: FAILED: visible without any verification` |
| **3** toggle off | `PhotoCheckToggleTests` (off branch); `held_before_every_write`; `sv2r.toggle_off_approves_without_the_check` | pass | **Off branch calls the check port:** offline `AssertionError: 'adapters.check' unexpectedly found in 'decided = adapters.check.decide(...'`; on a local database `72/77`, `FAIL sv2r.toggle_off_approves_without_the_check ...: FAILED: the check port was not called`. **It records `system:photo-check` with `automated_check`:** offline `AssertionError: 'md.CHECK_SUBJECT' unexpectedly found ...`; on a local database `72/77`, `FAILED: under the toggle's own subject`. **It approves a restricted photo** (the guard removed): offline `ERROR: test_the_off_branch_calls_no_check_port...` (the restriction no longer precedes the branch). **It approves a held photo** (the port asked after the audit row, its answer ignored): offline `FAIL: test_a_hold_returns_before_the_approval_writes_anything ... AssertionError: 0 != 1` |
| **4** toggle on | the four named media cases with the toggle on; `sv2r.toggle_on_the_check_decides_as_before` | pass, with nothing they assert changed | The off branch reversal above also fails `media.every_other_photo_step...`. With the toggle on, these cases are Stage B's own, with Stage B's reversals |
| **5** the recheck | `PhotoCheckToggleTests` (recheck); `held_before_every_write`; `WRITERS`; `MEDIA_COMMANDS`; `sv2r.the_recheck`; `media.every_other_photo_step_refuses_an_inactive_owner` | pass | **Acts while off** (guard removed): offline `ERROR: test_the_recheck_changes_nothing_while_the_toggle_is_off`; local database `76/77`, `FAIL sv2r.the_recheck ...: FAILED: off: no_change`. **Approves a held photo** (hold guard removed): offline `FAIL: test_a_hold_returns_... AssertionError: 0 != 1`; local database `76/77`, `FAILED: held: no_change`. **Leaves the rejected photo's profile visible** (recompute removed): offline `FAIL: test_every_requirement_writer_ends_with_the_recompute (writer='recheck') ... recheck does not recompute`; local database `76/77`, `FAILED: the recompute demotes the profile`. **Skips the active-account gate** (`lock_account_any_state`): offline `AssertionError: 'lock_account_any_state(tx, account_id)' != 'lock_account(tx, account_id)'` (LockOrderTests, AccountStateTests) |
| **6** toggle off again | `sv2r.toggle_off_again_approves_under_its_reason` | pass | Check 3's reversals on a local database: `FAILED: turned off again, the waiting photo is approved`, and `FAILED: under the toggle's reason` |
| **7** the setting | `test_the_photo_checks_toggle_has_a_closed_schema`, `test_closed_schemas_refuse_unknown_keys_and_types`, `test_the_launch_values_...`, `test_sv2r_migration_follows_0011`; `settings.launch_defaults` (unchanged); `sv2r.the_toggle_is_a_setting` | pass | **A publication outside the schema accepted** (`_photo_check_refusals` returning nothing): `FAIL: test_the_photo_checks_toggle_has_a_closed_schema (content={}) ... AssertionError: Tuples differ: () != ('schema',)`, and the generic closed-schema test (`setting='media.photo_check'`). **The seed's reason `OD-60`:** `FAIL: test_sv2r_migration_follows_0011 ... '363a969b...' != '4e40028b...'`. **Seeded on:** the same test, `'81126291...' != '4e40028b...'`. **The launch reason `OD-60`:** `AssertionError: 'OD-60' != 'OD-68'` |
| **8** the registry | `test_the_writers_table_is_f05s_registry`; `test_sv2r_f05_system_transitions_out_of_approved` | pass | **A third transition out of `approved`** (`review`, in both tables): API `FAIL: test_the_writers_table_is_f05s_registry ... Items in the first set but not the second`; contract `FAIL: ... (event='review', after='review_pending') AssertionError: 'allowed' != 'state_conflict'`. **`reject` missing from the registry:** API `FAIL: test_the_writers_table_is_f05s_registry`; contract `AssertionError: 'state_conflict' != 'allowed'`. **`approve` missing from `TRANSITIONS`:** `FAIL: test_the_writers_table_is_f05s_registry` |
| **9** locks | `sv2r.locks_serialize_on_the_toggles_pointer` (three lock waits, each observed in `pg_stat_activity`: a publication of the toggle held at its commit and `run_check` waiting, then reading the new version; a publication held and the recheck waiting, then reading it on; the recheck's shared lock held and a publication waiting; then D19's order recorded through `settings_store._hold`: `run_check` and the recheck lock `consent.onboarding`, `media.photo_check`, `media.policy`, and a publication of the toggle its own pointer only); `test_each_step_reads_the_toggle_in_its_one_read_shared_call_in_name_order` | pass | **The toggle's pointer out of D19's order** (`run_check` reads `[consent.onboarding, media.policy]`, then `[media.photo_check]`): offline `AssertionError: 'settings_store.read_shared(tx, [ps.ONBOARDING_CONSENT, ps.PHOTO_CHECK, ps.MEDIA_POLICY])' not found ...`; on a local database `run_check` raises `PointerOrderError` in every approval: `[profile] cases: 21/77 passed`, with `FAIL sv2r.locks_serialize_on_the_toggles_pointer ...: FAILED: run_check waited on the publication's pointer lock` |
| **10** seal and full suite | `test_profiles_sealed_runtime.py` (unchanged); the full API suite; `test_dependency_pins.py` (unchanged) | pass: 642 tests, `OK (skipped=1)` in CI | (none needed: no runtime path changed) |
| **11** the run | run 44362141024, below | all eight jobs `success`; the gate's `Application checks passed` | (none) |
| **12** reversals | this table, plus: a state write outside `transition` in the recheck (`FAIL: test_only_the_recompute_writes_a_profiles_state`); an SV2-R case labelled `"3"` (`FAIL: test_sv2rs_own_cases_name_its_checks ... names at least one of SV2-R's checks`); check 9 left unnamed (`'SV2-R 9' not found`); a label name rebound to a value (`FAIL: test_every_binding_of_a_label_name_is_pinned`) | every reversal failed, and every edit was undone (each file restored from its copy; `git status` clean of them; the full suites green again) | (none) |

## The local checks

- **API** (`services/api`):
  - `python3.12 -m venv .venv`, then the hash-locked install, exit 0;
  - `manage.py check`: no issues;
  - `manage.py test tests --verbosity 2`: `Ran 642 tests`, `OK`;
  - `ruff check .`: all passed;
  - `ruff format --check .`: 165 files formatted;
  - `mypy`: no issues in 95 files;
  - `glow_persistence.static_check`: agrees, migrations `0001` to `0012`;
  - `smoke.py`: PASS.
- **The contract tests:** `PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests`: `Ran 53 tests`, `OK`.
- **The contracts** (`packages/contracts`): `npm ci --ignore-scripts` exit 0; `npm run check` exit 0; two `npm run generate` runs with no generated change.
- **The mobile app** (`apps/mobile`): `npm ci --ignore-scripts` exit 0; `npm run check` exit 0, 691 tests passed. No change under `apps/`.
- **The proof** (`proofs/postgres-ordering`):
  - the hash-locked install, and `pip check`: no broken requirements;
  - the offline tests under `env -i`: `Ran 377 tests`, `OK`;
  - Ruff: all passed; `ruff format --check`: 71 files formatted; mypy: no issues in 71 files.
- **A local database run** (iteration, not evidence), under D4:
  - the CI job's pinned image `postgres@sha256:d74eeac9...`, on `127.0.0.1:5433`, with `track_commit_timestamp=on`;
  - a generated superuser and role password, and a new marker for each database, in a mode-700 directory, nothing printed;
  - none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present;
  - the container and every secret file removed afterwards.

  Docker's daemon was not running at first, and the session started it. Docker Hub answered `429 Too Many Requests` three times; a fourth pull, after the code was pushed, succeeded. The profile suite then passed: `[profile] cases: 77/77 passed in 140.6 s`, both of the suite's scans clean, `PROFILE VERDICT: PASS`. The job's `profile_scan` on the log: 0 of the job's secrets found; the suite's own scans clean. The database reversals above ran on new databases in the same container.

## The run of record

- **Run:** [44362141024](https://github.com/amthorn78/glow-dating-app/actions/runs/44362141024), Foundation #1336, on the push of `f4703a1faf79e1a66f615a17b531f874be73b1ed`.
- **Jobs**, each `success`:
  - Change scope;
  - API checks: `Ran 642 tests`, `OK (skipped=1)`; Ruff, format (165 files) and mypy (95 files) pass; the contract tests `Ran 53 tests`, `OK`, with `test_sv2r_f05_system_transitions_out_of_approved ... ok`;
  - API mobile smoke;
  - API artifact checks;
  - Stream proof checks;
  - Mobile checks: the contracts' `npm run check` (`node scripts/generate.mjs --check && node --test tests/*.test.mjs`), 902 tests passed and 0 failed; the app's check, 691 tests passed and 0 failed; `check:expo`; `export:development`; the rendered fixture journeys, `104 passed (5.3m)`;
  - Database proof checks;
  - Foundation gate: `Application checks passed`.
- **Database proof checks:** started 17:45:34 and finished 17:59:16, **13 min 42 s** against its 30-minute timeout.
  - **Ordering suite:** `[reference] cases: 56/56 passed`, `[adapter] cases: 115/115 passed`, `[read] cases: 62/62 passed`, `== VERDICT: PASS ==`. A wrong marker, `dbshell` and a second run were each refused, with the second run's row counts unchanged.
  - **Identity suite:** `[identity] cases: 49/49 passed in 41.5 s`, phase 42 s. Its secret scan clean: 754 held, 0 found. The job's check found 0 of its secrets in the output and in the JSON. A second run was refused with its counts unchanged.
  - **Profile suite:** the profile database refused the other two markers, and the migrations applied from zero with `makemigrations --check`.
    - `[profile] cases: 77/77 passed in 104.7 s`, phase **105 s**, `PROFILE VERDICT: PASS`.
    - `profile secret scan: clean (1590 secrets held; 0 found in 972 log records, 190 writes and the results JSON)`.
    - `profile value scan: clean (909 member values held: ...; 0 found in the same output)`.
    - The job's check: 0 secrets in the output and 0 in the JSON, and the suite's own scans clean.
    - A second run was refused ("a setting was published beyond its launch default"), with its counts `142 142 107 70 1732 1082` unchanged. The artifact `sv2-profile-results` was saved.
    - The new cases, each `PASS`:
      - `sv2r.a_profile_completes_without_identity_verification`;
      - `sv2r.the_staff_approval_meets_nothing`;
      - `sv2r.toggle_off_approves_without_the_check`;
      - `sv2r.toggle_on_the_check_decides_as_before`;
      - `sv2r.the_recheck`;
      - `sv2r.toggle_off_again_approves_under_its_reason`;
      - `sv2r.the_toggle_is_a_setting`;
      - `sv2r.locks_serialize_on_the_toggles_pointer` (three lock waits, each observed).
    - The changed cases, each `PASS`:
      - `completion.refuses_each_missing_requirement` ("8 checks, identity verification set aside");
      - `completion.needs_the_chart_and_identity_verification_seeded`;
      - `staff.approval_gated_narrow_survives_and_is_revocable` ("revoked, the profile stays");
      - `completion.removals_demote_and_empty_values_are_refused` ("8 removals ...; a revoked approval leaves the profile as it was");
      - `completion.every_requirement_writer_meeting_the_last_one_makes_it_visible` (7 writers);
      - `media.an_upload_moves_only_through_quarantine_the_seam_and_review`;
      - `media.the_checks_decisions_are_the_systems_and_never_clear_a_restriction`;
      - `media.a_hold_stops_the_checks_approval`;
      - `media.every_other_photo_step_refuses_an_inactive_owner` ("12 steps refused");
      - `media.the_photo_requirement_completes_and_its_removal_demotes`;
      - `settings.launch_defaults` ("16 settings").
  - **Discovery suite:** `[discovery] cases: 66/66 passed in 184.9 s`, phase 187 s, `DISCOVERY VERDICT: PASS`. Its secret scan clean (2495 held, 0 found) and its value scan clean (1336 held, 0 found). The job's check found 0. A second run was refused with its counts unchanged.
- **Toolchain retry:** none fired. Every job's "Wait 60 s before the one retry" and "Retry the Python install once" steps were `skipped`.
- **No value in the logs.** The Database proof checks and Mobile checks logs were searched for the suites' fixed coordinates (`40.7123457`, `-74.0067891`, `40.735425`, `40.712`), the held birth time `04:13:27` and `BEGIN PRIVATE KEY`: 0 hits each. The job's masked values show as `***` (3 lines). The suites' own value and secret scans report 0 found.

## Deviations, limits and open questions

- **`approved_photo` publishes the toggle on in its setup.** It is the suite's shared helper, and it drives `run_check` with the test's own deciding check port. The brief says such cases "publish the toggle on in their setup" (check 4).
  - **Why:** `media.the_checks_decisions_...` asserts that every approval and rejection row in the database has the subject `system:photo-check`. With the toggle off, the earlier cases' photos would carry `system:photo-check-off`, and that assertion would have to change, which check 4 forbids ("no other change to what they assert").
  - **The effect:** every earlier case's photo is approved by the check, as before. The off branch is exercised by SV2-R's own cases, appended last in the plan.
  - **The order matters, and it holds:** `media.every_other_photo_step_refuses_an_inactive_owner`, which makes one off-branch approval, runs after `media.the_checks_decisions_...`.
  - **The discovery suite** calls `approved_photo` in one case; it publishes the toggle there too. `glow_discovery` reads no `policy_published`, and the discovery suite passed 66/66.
  - **Open question for the manager:** keep this, or change that one global assertion instead.
- **The order in the off branch** is today's: restriction, variant, hold port, then the writes. The brief lists "the hold port is asked first" before "an asset with no variant is refused", under "As today", so I kept today's order. A missing variant is refused, which writes nothing in either order.
- **The recheck's approval** takes a new delivery reference from the storage port for the variant (DM-92: it "writes ... a delivery reference"). It emits `media_approved` a second time for the same photo. DM-91 4.3 notes that a later consumer must not take that as a first approval (for P11).
- **`awaiting_recheck`** takes no lock and opens no transaction. It is a list for a worker, and `recheck` checks every condition again under the locks.
- **A guard caught my own code before the push:** `test_profile_pointer_order.test_nothing_but_the_store_and_the_model_mentions_a_pointer` failed when a new case named `PolicyRevision`. The case now reads the pointer through `settings_store.read_unlocked`. That guard is unchanged.
- **The local database run came after the push.** Docker Hub's rate limit blocked the image until after `f4703a1` was pushed, so the first push had no local database iteration. The run of record passed. The local run and the database reversals followed it, on the same pinned image.
- **Not reversed on the database:** the restricted-photo and held-photo reversals of check 3. They are reversed offline (above). `sv2r.toggle_off_approves_without_the_check` asserts both on PostgreSQL.
- **No record changed outside the owned paths.** The brief's manager-owned records (the SV2 brief's notes, the carried items, the P11 plan's SV2 entry, the handoff) are not touched.

## Manager verification (App Manager 12, 18 November 2026, 18:49 UTC)

- **The paths.** `git diff --name-status 80bed4a 587f4a2` lists 19 paths, each an owned path of the brief's revision 6, with no mode change or symlink. Nothing under `apps/`, no generated output, and no existing migration changed. `proofs/postgres-ordering/README.md` changed in line 17 only, and `tests/test_profile_offline.py` only in its plan pins (`CASE_COUNT` 77, `SV2R_CASES` and its rule); `LABEL_NAMES` and `LABEL_BINDINGS` are unchanged.
- **The run of record,** read with the GitHub tools: run 44362141024, event `push`, on `f4703a1`, conclusion `success`, with all eight jobs `success` and no toolchain retry step run. The gate printed "Application checks passed". In the Database proof checks job, the profile suite printed "cases: 77/77 passed in 104.7 s", each of the eight `sv2r.` cases `PASS` under its "SV2-R n" label, its secret scan clean and "PROFILE VERDICT: PASS"; the discovery suite printed "DISCOVERY VERDICT: PASS" with its scans clean; each second run was refused.
- **The code, read at `587f4a2`:**
  - **R1:** `requirements.missing` drops only the identity check and the model's import; its signature stays (DM-93 ZZ2), `ALL` keeps `identity_verification`, and the docstring says the requirement is set aside;
  - **the registry:** `flows-v1.json` and `glow_domain.media.TRANSITIONS` each gain exactly `approve` (`approved` to `approved`) and `reject` (`approved` to `rejected`), `system`, with `A05`;
  - **the seed:** `0012_photo_check_seed.py` depends on `0011` and writes version 1 (`{"enabled": false}`), its pointer and a `StaffAudit` row (`seed_launch_default`), with `system:launch-default` and "OD-68", on `0009`'s pattern;
  - **`run_check`:** one `read_shared` call for `consent.onboarding`, `media.photo_check` and `media.policy`, in name order; then not in review and a restriction, as before; with the toggle off, no call to the check port, and the approval under `system:photo-check-off` and `photo_check_off`, after the missing-variant refusal and the hold port, ending with the recompute;
  - **`recheck`:** `lock_account` first, then one `read_shared` call; `no_change` with no port call while the toggle is off; the hold port before its approval; its rejection through `transition`, then the recompute. `awaiting_recheck` lists only `approved` photos of `active` accounts whose review reference carries the toggle's reason.
- **The session's open question,** `approved_photo` publishing the toggle on in its setup: accepted as the manager's reading of the brief's words. The helper drives `run_check` with the test's own deciding check port, which is the case "Earlier tests" says publishes the toggle on in its setup, so each earlier case's assertions stay unchanged (acceptance check 4). The exact-head review is asked to check it.
- **Not done by the manager:** no test, suite or reversal was run here; the reversals and the local database run are the session's, recorded above.

## Exact-head review (the review session's report, recorded by App Manager 12, 18 November 2026)

- **The review.** A review session on the review prompt's revision 1 (at `e2bacf7`) reviewed code head `f4703a1` in full, with a written threat model of 18 threats, each given its stopping code and its test. Nathan relayed its report. **Verdict: changes requested, for tests only.** It found no defect in the code, two should-fix findings in the correction class "let a test pass where it should fail", and four nits.
- **Its start.** The start gate passed in every line: one merge base, `15d54f6`; no path outside Markdown differing from `f4703a1`, at `e2bacf7` or on the live branch; no review recorded. The trusted classifier, extracted from `15d54f6` and run with `python3 -I`, full SHAs and `--merge-base`, gave `"full": true`, `behavior-or-empty`, 38 paths. The environment check found none of the forbidden names; the AWS and GitHub token names it found were not read.
- **Its checks,** in a scratch copy of `f4703a1`:
  - the API: `manage.py check` clean; `manage.py test tests` 642 tests OK (one skipped); Ruff clean; `ruff format --check` 165 files; mypy no issues in 95 files; `glow_persistence.static_check` agrees for `0001` to `0012`; `smoke.py` PASS three times;
  - the contracts: 53 tests OK; `generate.mjs --check` matched;
  - the proof: its offline tests 377 OK; Ruff, `ruff format --check` (71 files) and mypy clean;
  - the four required reversals each failed their tests: the identity check restored in `missing()` (six failures in `test_sv2r_requirements.py`), the off branch calling the check port, a third `system` transition out of `approved` in both tables, and the toggle read out of D19's order;
  - locally under P06.DB's D4: the profile suite 77 of 77 in 145.9 s, both scans clean, and three database reversals failing `sv2r.the_recheck` or `sv2r.locks_serialize_on_the_toggles_pointer` (the recheck acting while off, approving a held photo, reading the toggle unlocked).
- **The runs, read by the review:** 44362141024 (`push`, `f4703a1`) and 44378253123 (PR54's `pull_request` run on `e2bacf7`): all eight jobs `success`, no retry step run, and the gate's "Application checks passed"; the profile suite 77 of 77 in each (104.7 s and 93.2 s), with its scans and the job's own check clean. The record's counts and lines matched.
- **The findings and their dispositions** (the manager workflow, step 6, "Fix or carry, by rule"):

| Finding | Severity and class | Disposition |
|---|---|---|
| **R1:** no test of the recheck's state condition (`glow_profiles/media.py`, lines 758 to 762); removing it (reversal B) passed every suite, 77 of 77 on PostgreSQL included. Under that change, a photo approved while the toggle was off and then restricted by staff would be rejected by the check | Should fix; "let a test pass where it should fail" | Fixed before the merge (rule (a)): the brief's correction C1.1 |
| **R2:** no test of `run_check` on an approved photo (lines 638 and 639), which since SV2-R's two transitions out of `approved` is the only stop; widening it (reversal A) passed every suite | Should fix; the same class | Fixed before the merge: C1.2 |
| **N1:** acceptance check 2's "changes no profile" claims more than `completion.every_requirement_writer…` shows, where D9's recompute catches up a profile a test left stale | Nit | Corrected in C1 (C1.5); the brief's R1 sentence qualified in its revision 7 |
| **N2:** `staff.py`'s module docstring (lines 8 to 15) and `glow_domain/identity_verification.py` (line 46) still describe the identity requirement | Nit; pre-existing code R1 made stale | Carried to the next change to each file (the carried-items file) |
| **N3:** `media.the_checks_decisions…` holds only while no off-branch approval runs before it in the plan | Nit | Carried to the first change to the profile suite after SV2-R (the carried-items file) |
| **N4:** `awaiting_recheck()` is unbounded and takes no lock; neither the P11 plan nor the carried items had the recheck's worker or DM-91 section 4.3's note | Observation, outside the review's scope | The P11 plan, "SV2-R carryforward", with DM-91 section 4.3's note (AM12-25) |

- **The manager's check of R1 and R2** (App Manager 12, 20:42 UTC). Read at `f4703a1`: `run_check` refuses with `not_in_review` for any state but `review_pending`, and the recheck's `not_awaiting_recheck` joins `asset.state != md.APPROVED` to the review reference's filter; `transition` sets the review reference only on `approve`, so a restriction keeps it. The profile suite asserts `not_in_review` only for `upload_pending`, `quarantined` and `removal_pending` photos, and `not_awaiting_recheck` only for a photo the check re-approved; no API test asserts either for these states. The manager ran neither reversal; they are the review's. The manager read run 44378253123 (PR54's `pull_request` run on `e2bacf7`) with the GitHub tools: all eight jobs `success`, no retry step run, and the gate's "Application checks passed"; PR54 had no review thread.
- **Found by the manager while disposing of the review:** the carried entries N-a, N-c and N-d were due at SV2-R's changes to `test_profile_recompute.py`, `profile_support.py` and `test_profile_media.py`, and its brief did not take them up (AM12-26). Correction C1.4 takes them up.
- **The review's limits:** it ran the identity, ordering, discovery and mobile suites only through their CI results; it did not read Codex's summary or `profile_cases.py` whole; a subagent extracted the CI log lines, which the review checked against this record.
- **Next:** correction C1 (tests only), then a delta review and the merge.

## Correction C1 (the correction session's record, 18 November 2026)

- **The prompt:** SV2-R's correction C1 prompt, revision 1, from `1708b53c4f89b10c9d71325b7a2bdd32aff2fca9` of `claude/magical-wozniak-yfmmx2`, started by Nathan; the brief's revision 7, "Correction C1", is the specification. Tests only: **no code changed.**
- **The branch:** `claude/modest-cerf-3acfed`, from `1708b53`. Its name matches `claude/**`, so the Foundation workflow runs on its pushes.
- **The code commit:** `f4c93ea8ed17d26f29a01c5c7e75e910ab925b11` (**C1's code head**), one commit holding the five test and proof paths below. The records commit (this section) follows the run of record, as the push rule requires.

### Start gate and environment

- **The environment check, names only.**
  - None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` was set, and no `STREAM_*` or `PG*` name.
  - Present: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_CA_BUNDLE`, and the GitHub token names `GH_TOKEN` and `GITHUB_TOKEN`. None of their values was read, printed or passed to a command.
  - Every repository command ran in a clean process environment (`env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus `GLOW_ENV=test` for the API). The proxy and CA variables were passed by reference to `pip` only.
- **The toolchain:** CPython 3.12.14 (`python3.12`), Node v24.19.0, npm 11.9.0, Docker 29.10.0 (build `fdd4b8e`).
- **The start gate**, each line as the prompt has it:
  - fetched both branches; the live manager branch's head was `1708b53`, and `1708b53` is on it;
  - `git rev-parse HEAD` printed `1708b53c4f89b10c9d71325b7a2bdd32aff2fca9`;
  - `the reviewed code`: no non-Markdown path differs from `f4703a1`;
  - no code, test, proof, contract, app or workflow path, nor the brief or this record, differs between `1708b53` and the live manager branch;
  - `0` "Correction C1" sections; `77` `@case(` lines.

### The items

| Item | Files | Tests | Reversal and its failing output |
|---|---|---|---|
| **C1.1** the recheck's state condition (the review's R1) | `services/api/tests/test_sv2r_requirements.py`; `profile_cases.py`, `sv2r.the_recheck` | **Offline:** `StateRefusalTests.test_the_recheck_refuses_a_photo_that_is_not_approved`: the one `if` whose one statement returns `no_change` with `not_awaiting_recheck` tests `asset.state != md.APPROVED or not _approvals_while_off().filter(pk=asset.review_ref).exists()`, exactly those two disjuncts; nothing before it calls a port or writes (`adapters.`, `_decision_audit(`, `transition(`, `recompute.`, `.save(`, `.create(`, `.update(`, `bulk_create`, `events.emit(`, `delivery_reference(`); the check port comes after it; it is the step's only comparison on `asset.state`. **On PostgreSQL**, in `sv2r.the_recheck`, with the toggle on: a member's photo approved while the toggle was off and then restricted by staff (`review_pending`, its review reference still the toggle's approval row, asserted), and another approved while off and then removed by its owner through the member's route (`removal_pending`, its review reference still the toggle's, asserted); each rechecked once with a rejecting check and once with an approving one: `no_change` with `not_awaiting_recheck`, the spy check port and a recording hold port never asked, and `_photo_snapshot` unchanged (state, version, delivery reference, review reference, rejection reason, the profile's state and version, the photo's `StaffAudit` rows and the photo's and profile's outbox events); `awaiting_recheck()` lists neither | **Reversal B** (`asset.state != md.APPROVED or` removed, leaving `if not _approvals_while_off().filter(pk=asset.review_ref).exists():`). Offline, the full API suite: `Ran 645 tests`, `FAILED (failures=1)`: `FAIL: test_the_recheck_refuses_a_photo_that_is_not_approved ... AssertionError: <ast.UnaryOp object at 0x7f9c951755d0> is not an instance of <class 'ast.BoolOp'>`. On a local database: `[profile] cases: 76/77 passed`, `FAIL sv2r.the_recheck (SV2-R 5, D9, D10, OD-68) 2.9 s: FAILED: restricted: not the recheck's`, `PROFILE VERDICT: FAIL`. Restored: `cmp` with `f4703a1`'s `glow_profiles/media.py` identical |
| **C1.2** `run_check` on an approved photo (R2) | `test_sv2r_requirements.py`; `profile_cases.py`, `sv2r.toggle_off_approves_without_the_check` and `sv2r.toggle_on_the_check_decides_as_before` | **Offline:** `StateRefusalTests.test_run_check_refuses_a_photo_that_is_not_in_review`: the one `if` returning `no_change` with `not_in_review` tests exactly `asset.state != md.REVIEW_PENDING`; nothing before it calls a port or writes; it comes before the `restricted` refusal and the `if checking:` branch; it is the step's only comparison on `asset.state`, and `md.APPROVED` is named nowhere in the step's body. **On PostgreSQL:** with the toggle off, right after the off branch approves the case's photo, `run_check` on it with a rejecting spy check and a recording hold: `no_change`, `not_in_review`, neither port asked, the snapshot unchanged. With the toggle on, after the check approves the case's photo, `run_check` on it with a rejecting check and with an approving one: the same each time | **Reversal A** (`if asset.state not in (md.REVIEW_PENDING, md.APPROVED):`). Offline, the full API suite: `Ran 645 tests`, `FAILED (failures=1)`: `FAIL: test_run_check_refuses_a_photo_that_is_not_in_review ... AssertionError: 'asset.state not in (md.REVIEW_PENDING, md.APPROVED)' != 'asset.state != md.REVIEW_PENDING'`. On a local database: `[profile] cases: 75/77 passed`, `FAIL sv2r.toggle_off_approves_without_the_check (SV2-R 3, D9, D10, OD-68) 1.2 s: FAILED: off: an approved photo is not in review` and `FAIL sv2r.toggle_on_the_check_decides_as_before (SV2-R 4, D10, OD-68) 0.7 s: FAILED: on, a rejecting check: not in review`, `PROFILE VERDICT: FAIL`. Restored: `cmp` identical |
| **C1.3** the reversals | (none changed) | A and B above, each run offline (the full API suite) and on a local disposable database under D4 | Each edit made by a script that copied `media.py` aside, wrote the edit, ran the tests and copied the file back; after each, `cmp services/api/glow_profiles/media.py` against `git show f4703a1:services/api/glow_profiles/media.py` printed nothing (identical) |
| **C1.4** the carried entries N-a, N-d and N-c | `test_profile_recompute.py` (the creation guard), `test_profile_media.py` (the held branch's write list), `profile_support.py` (the module docstring) | See "The carried entries" below | See below |
| **C1.5** the record | this file | acceptance check 2's row now says that the approval's recompute moves no profile whose state is current, and that D9's recompute still catches up a profile a test left stale (`completion.every_requirement_writer…`); this section | (none: Markdown) |

**No new case.** `CASE_COUNT` stays 77; `SV2R_CASES`, `LABEL_NAMES`, `LABEL_BINDINGS` and the proof README's count are unchanged, and `tests/test_profile_offline.py` passes unchanged (its label-binding pin included: no new line binds a name in `LABEL_NAMES`, and every new label is literal text or a choice between two literals). The new database checks sit inside the three existing cases named above, and each case's return line is unchanged but `sv2r.the_recheck`'s, which adds "restricted or removed: not the recheck's, no call and no change".

### The carried entries

- **N-a** (`services/api/tests/test_profile_recompute.py`, the creation guard only):
  - `CREATING` gains `acreate`, `aget_or_create`, `aupdate_or_create` and `abulk_create` (with `bulk_create` as `BULK`, which `_creations_with_state` leaves out as before), and `_profile_creations` now uses `CREATING` (it had its own copy of the four synchronous names);
  - a new `_clones`: an assignment of `None` to `pk` or `id` on any object, after which a save inserts a copy of the row, its state included, and any call given `force_insert`; `test_a_photo_is_created_only_upload_pending` asserts there are none in `glow_profiles` or the age port;
  - `test_the_creation_guard_sees_each_spelling` also asserts that its tree has no clone, and a new `test_the_creation_guard_sees_each_async_and_clone_spelling` shows each new spelling seen by `_asset_creations`, `_profile_creations`, `_creations_with_state` and `_clones`.
  - `abulk_create` is beyond the entry's words, as `bulk_create` already was in the set; a clone by `id = None`, or saved without `force_insert`, is seen by its assignment.
  - **Reversals,** each a temporary function appended to `glow_profiles/media.py`, run against `tests.test_profile_recompute` with C1's file and with `1708b53`'s:

    | Spelling | With C1 | Before C1 |
    |---|---|---|
    | `await MediaAsset.objects.acreate(account_id=account_id, state=md.APPROVED)` | `Ran 8 tests`, `FAILED (failures=1)`: `FAIL: test_a_photo_is_created_only_upload_pending ... AssertionError: Lists differ: [('gl[185 chars]NG)'), ('glow_profiles/media.py', '_c1_probe',[68 chars]D)')] != [('gl[185 chars]NG)')]` | `Ran 7 tests`, `OK` |
    | `await MediaAsset.objects.aget_or_create(pk=asset_id, state=md.APPROVED)` | the same test, `Lists differ: ... '_c1_probe',[65 chars]D)')]` | `OK` |
    | `await MediaAsset.objects.aupdate_or_create(pk=asset_id, state=md.APPROVED)` | the same test, `Lists differ: ... '_c1_probe',[68 chars]D)')]` | `OK` |
    | `await MediaAsset.objects.abulk_create([asset])` | the same test, `Lists differ: ... '_c1_probe',[40 chars]])')]` | `OK` |
    | `asset = MediaAsset.objects.get(pk=asset_id)`, `asset.pk = None`, `asset.save(force_insert=True)` | the same test, `AssertionError: Lists differ: [('glow_profiles/media.py', '_c1_probe', '[87 chars]e)')] != []` | `OK` |

- **N-d** (`services/api/tests/test_profile_media.py`, `held_before_every_write`'s write list only): the list of writes nothing before the hold guard may hold also names `.update(`, `bulk_create` and `events.emit(`, for `run_check` and `recheck` alike. **Reversals,** each a statement inserted in `run_check`'s approval branch just before `if adapters.hold.held(asset.id):`, run against `tests.test_profile_media` with C1's file and with `1708b53`'s:

  | Statement | With C1 | Before C1 |
  |---|---|---|
  | `MediaAsset.objects.filter(pk=asset.id).update(review_ref=None)` (the delta review's A3) | `Ran 28 tests`, `FAILED (failures=1)`: `FAIL: test_a_hold_returns_before_the_approval_writes_anything (...) (step='run_check', write='.update(')`, `AssertionError: '.update(' unexpectedly found in "lock_account(tx, account_id)\nfound = ...` | `Ran 28 tests`, `OK` |
  | `MediaObject.objects.bulk_create([])` | the same test, `(step='run_check', write='bulk_create')` | `OK` |
  | `events.emit(tx, events.MEDIA_APPROVED, aggregate_id=asset.id, aggregate_version=int(asset.version), payload_ref=asset.id, now=now)` | the same test, `(step='run_check', write='events.emit(')` | `OK` |

- **N-c** (`proofs/postgres-ordering/glow_ordering_proof/profile_support.py`, the module docstring only): the ledger now reads as holding "the start of each object's bytes, their first 24, as their hex and their `repr`, which any whole print of either contains", as `add_bytes` does and the proof README already says. A docstring: no reversal.
- After every reversal, `media.py` was restored and `cmp` with `f4703a1`'s file printed nothing; each swapped test file was copied back, and `git status` showed only C1's five paths.

### The local checks

- **API** (`services/api`):
  - `python3.12 -m venv .venv`, then the hash-locked install, exit 0;
  - `manage.py check`: no issues;
  - `manage.py test tests --verbosity 2`: `Ran 645 tests`, `OK` (642 before C1, and three new: the two `StateRefusalTests` and `test_the_creation_guard_sees_each_async_and_clone_spelling`);
  - `ruff check .`: all passed; `ruff format --check .`: 165 files formatted; `mypy`: no issues in 95 files.
- **The contract tests:** `PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests`: `Ran 53 tests`, `OK`.
- **The proof** (`proofs/postgres-ordering`): the hash-locked install and `pip check` ("No broken requirements found"); the offline tests under `env -i`: `Ran 377 tests`, `OK`; Ruff all passed; `ruff format --check`: 71 files formatted; mypy: no issues in 71 files.
- **A local database run** (iteration, not evidence), under D4:
  - the CI job's pinned image `postgres@sha256:d74eeac9...`, on `127.0.0.1:5433`, with `track_commit_timestamp=on`; the session started `dockerd`, and Docker Hub served the pull at the first attempt;
  - a generated superuser and role password, a non-superuser role, and for each run a new database with its own new marker as its comment and its own key files, in a mode-700 directory, nothing printed; a check of each run's log for its own secrets found 0;
  - none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present;
  - the container, its volume, the secrets directory and the results files removed afterwards.

  The first run of the new tests gave `75/77`, with `sv2r.toggle_on_the_check_decides_as_before` and `sv2r.the_recheck` each `ERROR: DoesNotExist`: my own setup, not the code. `_photo_snapshot` reads the member's profile row, and the two members those checks used (`ctx.member()`) had none yet. Each check now makes the member's profile first, through the member's route (`ctx.profile`), before its first snapshot. The run on the final tests: `[profile] cases: 77/77 passed in 150.7 s`, both scans clean (`1601 secrets held; 0 found`; `919 member values held ...; 0 found`), `PROFILE VERDICT: PASS`. Reversals A and B then ran on new databases in the same container (above).
- **One offline test of mine failed while I wrote it,** before any commit: `_state_tests` began as a count of the text `asset.state` in each step's body, which also counts the `detail={'state': asset.state}` of each applied result (`AssertionError: 3 != 1` in both new tests). It now counts only comparisons on `asset.state`. The code was not the cause.

### The run of record

- **Run:** [44402994154](https://github.com/amthorn78/glow-dating-app/actions/runs/44402994154), Foundation #1344, event `push`, on `f4c93ea8ed17d26f29a01c5c7e75e910ab925b11`, attempt 1, read with the GitHub tools after it finished.
- **Jobs**, each `success`:
  - Change scope;
  - API checks: `Ran 645 tests`, `OK (skipped=1)`; Ruff "All checks passed!", "165 files already formatted", mypy "no issues found in 95 source files"; the contract tests `Ran 53 tests`, `OK`;
  - API mobile smoke;
  - API artifact checks;
  - Stream proof checks;
  - Mobile checks;
  - Database proof checks;
  - Foundation gate: `Application checks passed`.
- **Database proof checks:** started 21:35:24 and finished 21:46:53 UTC, **11 min 29 s** against its 30-minute timeout.
  - The proof's offline tests: `Ran 377 tests`.
  - **Ordering suite:** `[reference] cases: 56/56 passed`, `[adapter] cases: 115/115 passed`, `[read] cases: 62/62 passed in 14.3 s`, `== VERDICT: PASS ==`; a wrong marker and `dbshell` refused, and a second run refused on the used database.
  - **Identity suite:** `[identity] cases: 49/49 passed in 34.7 s`, phase 35 s; `identity secret scan: clean (754 secrets held; 0 found ...)`; the job's secrets found in its output and JSON: 0 and 0; a second run refused.
  - **Profile suite:** the profile database refused the other two markers, and the migrations applied from zero.
    - `[profile] cases: 77/77 passed in 83.7 s`, phase **84 s**, `PROFILE VERDICT: PASS`.
    - `profile secret scan: clean (1601 secrets held; 0 found in 978 log records, 190 writes and the results JSON)`.
    - `profile value scan: clean (919 member values held: coordinates, birth dates, times and places, own words, sensitive values; 0 found in the same output)`.
    - The job's check: "the job's secrets found in the profile suite's output: 0" and "... in the profile results JSON: 0".
    - A second run refused ("a setting was published beyond its launch default"), exit status 1, with its counts `143 143 109 72 1746 1087` before and after. The artifact `sv2-profile-results` was saved.
    - **The extended cases,** each `PASS`:
      - `sv2r.toggle_off_approves_without_the_check (SV2-R 3, D9, D10, OD-68) 1.4 s`;
      - `sv2r.toggle_on_the_check_decides_as_before (SV2-R 4, D10, OD-68) 0.4 s`;
      - `sv2r.the_recheck (SV2-R 5, D9, D10, OD-68) 2.1 s: ... restricted or removed: not the recheck's, no call and no change; ...`.
    - The other five `sv2r.` cases each `PASS`, unchanged.
  - **Discovery suite:** `[discovery] cases: 66/66 passed in 157.9 s`, phase 159 s, `DISCOVERY VERDICT: PASS`; its secret scan (2495 held, 0 found) and value scan (1336 held, 0 found) clean; the job's check found 0 and 0; a second run refused.
- **Toolchain retry:** none fired. In each job that has them, "Wait 60 s before the one retry of the Python install (DM-41)" and "Retry the Python install once (DM-41)" were `skipped`.
- **No value in the log.** The Database proof checks job's log (2,677 lines, saved to my scratch directory and searched there, then deleted) holds none of the suites' fixed coordinates (`40.7123457`, `-74.0067891`, `40.735425`, `40.712`), the held birth time `04:13:27`, `BEGIN PRIVATE KEY` or `fixture-variant`: 0 hits each. Masked values show as `***` (3 lines). The suites' own scans report 0 found. The other jobs' logs were not searched for these values.

### Deviations, limits and open questions

- **No code changed,** and no new test failed against the code at `f4703a1`: neither stop applied. The two failures recorded under "The local checks" were my own test code before the commit, each corrected in the test, never in the code.
- **N-a goes slightly beyond the entry's words:** `abulk_create` joins `CREATING` beside `bulk_create`; `_profile_creations` now reads `CREATING` rather than its own copy; and `_clones` also sees `id = None`, and a `force_insert` call with or without a cleared key. Each is a widening of the same guard, in the owned part of the file.
- **The C1.1 and C1.2 database checks also pass a recording hold port** and assert it was not asked, beyond the brief's "check port not called". The case's own member in `sv2r.toggle_on_the_check_decides_as_before`, and the new member in `sv2r.the_recheck`, each get a profile through the member's route before the first snapshot, so that the snapshot can read it (see "The local checks").
- **`test_sv2r_requirements.py`'s module docstring** gains a paragraph naming C1's tests. That is the new tests' own file.
- **Not reversed on the database:** the N-a and N-d reversals, which are offline guards; the entry says the profile suite's `media.a_hold_stops_the_checks_approval` catches N-d's edit there.
- **Limits:** the structural tests read `media.py`'s source as written: an equivalent refusal written another way (a helper, or the conditions split across statements) fails them, as the review's reversals A and B do; that is their purpose, and the database checks are the behavioural ones.
- **Open questions:** none.

## Correction C1, manager verification (App Manager 12, 18 November 2026, 22:01 UTC)

- **The paths.** `git diff --numstat 1708b53 038282e` lists six paths, each an owned path of the brief's "Correction C1", with no mode change or symlink: `test_sv2r_requirements.py` (117 added, 2 removed, both docstring lines), `test_profile_recompute.py` (104, 9), `test_profile_media.py` (5, 0), `profile_cases.py` (87, 3), `profile_support.py` (5, 4) and this record (120, 1, the one removed line being check 2's row). No module outside the tests and the proof's test support changed; the merge (`5d8fab8`) equals `f4c93ea` outside Markdown.
- **Within each file's part.** `profile_cases.py` changes only inside `sv2r_toggle_off`, `sv2r_toggle_on` and `sv2r_recheck`: steps added, one import widened to `media, staff`, and the recheck's result line extended; no assertion removed and no case added (77 `@case(` lines). `test_profile_media.py` adds `.update(`, `bulk_create` and `events.emit(` to the held branch's write list only. `test_profile_recompute.py` widens `CREATING` with the async forms, keeps the bulk forms out of `_creations_with_state` as before (`CREATING - BULK`), adds `_clones`, and asserts it finds nothing in the scanned code; the three earlier guards only see more. `profile_support.py` changes its module docstring only.
- **The new steps** use the existing `_photo_snapshot` (the photo's state, version, delivery and review references, rejection reason, the profile's state and version, and the audit and event counts) and `RecordingHold`, and assert that neither port is asked.
- **The run of record,** read with the GitHub tools: run 44402994154, event `push`, on `f4c93ea`, conclusion `success`, with all eight jobs `success`, no retry step run, and the gate's "Application checks passed". In the Database proof checks job (11 min 29 s): "[profile] cases: 77/77 passed in 83.7 s", "PROFILE VERDICT: PASS", both scans clean, the job's own check finding 0 secrets, and `sv2r.toggle_off_approves_without_the_check`, `sv2r.toggle_on_the_check_decides_as_before` and `sv2r.the_recheck` each `PASS` (the last with "restricted or removed: not the recheck's, no call and no change"); the second run refused; the identity, ordering and discovery verdicts `PASS`; no line holding `BEGIN PRIVATE KEY`. The log lines were extracted by a subagent through the GitHub tools and are quoted, not summarized.
- **Not done by the manager:** no test, suite or reversal was run here; the reversals' failing outputs are the session's, above, for the delta review to re-run.
- **Next:** a delta review of C1 (the manager workflow, step 6: no code changed), then the merge.

## Delta review of correction C1 (the review session's report, recorded by App Manager 12, 18 November 2026)

- **The review.** A review session on the delta review prompt's revision 1 (at `e9cc9ab`) reviewed C1's head `f4c93ea`, each touched path read whole, with the exact-head review's security focus. Nathan relayed its report. **Verdict: approve with nits.** It found no blocking or should-fix finding and nothing in a correction class; five nits.
- **Its start.** The start gate passed in every line (one merge base, `15d54f6`; no path outside Markdown differing from `f4c93ea`; no delta review recorded). The trusted classifier, extracted from `15d54f6` and run with `python3 -I`, full SHAs and `--merge-base` from inside the repository, gave `"full": true`, `behavior-or-empty`, 42 paths (a first attempt from outside the repository gave `comparison-unavailable`, also full). The environment check found none of the forbidden names.
- **Its checks,** in a scratch copy of `f4c93ea`: the API's 645 tests OK (one skipped), `manage.py check`, Ruff, `ruff format --check` (165 files) and mypy (95 files) clean, the contracts' 53 tests OK; the proof's 377 offline tests OK, with Ruff, format (71 files) and mypy clean.
- **Its reversals:** reversal A and reversal B each fail C1's tests offline (the messages C1's record gives) and on a local disposable database under P06.DB's D4 (75 of 77 and 76 of 77, failing the cases C1 extended); so do the refusal moved after the restriction check, a port call or an audit row before either refusal, and the recheck's condition widened to `review_pending`. Each of N-a's and N-d's new spellings fails C1's tests and passes `1708b53`'s. Locally at `f4c93ea` the profile suite passed 77 of 77, its scans clean.
- **The runs, read by the review:** 44402994154 (C1's run of record) and 44408183628 (PR54's `pull_request` run on `e9cc9ab`): all eight jobs `success`, no retry step run, the gate's "Application checks passed"; the profile suite 77 of 77 in each (83.7 s and 85.9 s), its scans and the job's own check clean; the record's counts and lines matched.
- **The findings and their dispositions** (the manager workflow, step 6, rule (b): a nit that misses no item and is in no class is a recorded follow-up):

| Finding | Disposition |
|---|---|
| **1:** `test_sv2r_requirements.py`'s `PORT_OR_WRITE` list (lines 159 to 170) does not see `.delete(`, `.get_or_create(`, `.update_or_create(`, `bulk_update(`, `.execute(` or the async forms, and sees a port only through the name `adapters.`; a `get_or_create` or a `.delete()` inserted before the recheck's refusal passed it. No code uses these spellings | Carried to the next change to that file (the carried-items file) |
| **2:** `_photo_snapshot` (`profile_cases.py`, lines 4221 to 4237, before C1) does not read the restriction reference, the removal time, the detection, the position, the media-object rows or the account's `eligibility_version`, and counts audit rows and events rather than comparing them. Every write these refusals could let through goes through `transition` or the audit, which it sees | Carried to the next change to the profile suite |
| **3:** N-c's docstring (`profile_support.py`, lines 8 to 15) omits that `add_bytes` also holds the whole text of printable ASCII bytes; the proof README's sentence has the same omission. The entry asked for the first-24-bytes correction only | Carried to the next change to `profile_support.py` and the README's sentence |
| **4:** `_clones` (`test_profile_recompute.py`, lines 528 to 552) misses a key cleared by tuple unpacking, `_state.adding = True`, and `force_insert` passed through `**kwargs` | Carried to the next change to that file |
| **5:** under reversal B, `sv2r.the_recheck` stops at the restricted photo's first assertion, so its removed-photo branch is not reached; it runs and passes at the head, and the offline test covers any widening | Recorded; no follow-up |
| **Observation (pre-existing):** `recheck` has no restriction check of its own and relies on the state refusal, since F05 allows `approve` from `review_pending`; C1's tests now pin that refusal | Recorded; no follow-up |

- **The manager's check** (App Manager 12, 22:34 UTC): run 44408183628 read with the GitHub tools, event `pull_request`, on `e9cc9ab`, conclusion `success`. The merge waits for the run and Codex's pass on PR54's final head, read with the same tools.
- **The review's limits:** it read `profile_cases.py` only in the changed cases and their helpers, and did not read Codex's summary, the other jobs' logs, or the API job's test-count line in run 44402994154 (only the end of that log); its offline reversals ran against the affected test modules; it did not run `smoke.py`, `glow_persistence.static_check`, `generate.mjs --check` or the other suites locally, taking them from CI.
- **Next:** the merge of PR54, after its run and Codex's pass on its final head; then the merge receipt.

## Merge receipt (App Manager 12, 18 November 2026)

- **PR54 merged into `main` at `6edae78`** (a merge commit, made with `expectedHeadSha` `115bc5a`; read back at 22:57 UTC: its parents are `15d54f6` and `115bc5a`, and its tree equals `115bc5a`'s).
- **On the final head `115bc5a`,** read with the GitHub tools before the merge: run 44413105426 (`pull_request`), all eight jobs `success`, no retry step run, the gate's "Application checks passed"; Codex's summary complete on `115bc5a` with no findings; no review thread. PF02's revision 1.7 there equals `50a3e25`'s, so DM-91's read covered it (the review log's "Deferred conditions").
- **The reviews:** the exact-head review of `f4703a1` (changes requested, for tests only), correction C1 (`f4c93ea`) and its delta review (approve with nits), each above.
- **Pruned in this receipt** (each deletion condition met by the merge and this receipt), with every link to them pinned at `6edae78`: the DM-91, DM-92 and DM-93 consultations, and SV2-R's implementation, review, correction C1 and delta review prompts.
- **SV2-R is done.**

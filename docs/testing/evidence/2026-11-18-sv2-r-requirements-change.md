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
| **2** the staff approval unchanged | `sv2r.the_staff_approval_meets_nothing`; `staff.approval_gated_...`; `completion.removals_...`; `test_sv2r_requirements.test_d18_stays` | pass | Covered by check 1's reversal on the database: `FAIL sv2r.the_staff_approval_meets_nothing ...: FAILED: visible without any verification` |
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

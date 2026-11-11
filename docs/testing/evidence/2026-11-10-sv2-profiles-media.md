# SV2 profiles and media: evidence

- **Work item:** SV2 ([brief](../../planning/sv2-profiles-media.md), revision 3, with [DM-52](../../continuity/dev-manager/reviews/2026-11-10-dm-52-sv2-brief.md)'s and [DM-53](../../continuity/dev-manager/reviews/2026-11-10-dm-53-sv2-stage-a-paths.md)'s conditions; OD-60, OD-61).
- **This record holds Stage A.** Stage B (photos, D10, acceptance check 10) has its own session and section.
- **Sealed:** nothing here is served. The routes run only under the disposable-PostgreSQL proof's profile settings; the served runtime imports none of the new code (D13). Local database runs are iteration, not evidence: the evidence of record is the CI run on the code head.

## Stage A

### The session

- **The prompt:** [Stage A's implementation prompt](https://github.com/amthorn78/glow-dating-app/blob/4dc2061a33c6f63e2887b11aeb2fd32d6224e23e/docs/ephemeral/2026-11-10-sv2-stage-a-implementation-prompt.md), revision 1, from `a6624de1568ed248dc975d9ae3a9e8863969f9b6` of `claude/magical-wozniak-yfmmx2`.
- **The branch:** `claude/sv2-stage-a-impl-0qqzvj`, started at `a6624de`.
- **The code commits:**
  - `4e94215`: D5, the committed area table and its derivation step;
  - `70e9b56`: the server's profile (D2 to D9, D11, D17, D18), its migrations and the API's tests;
  - `bb19493`: D11, the contract's DTOs, registry entries, corpus cases, README section and regenerated outputs;
  - `475a28d`: D12, the profile suite, its settings, tests and README section, and the Database proof checks job's steps;
  - `24c22ca`: the tests strengthened where four reversals had gone unseen (below), and the new DB04 case;
  - `b97bc15` (**the code head**): the DB04 case extended to every constraint migration 0005 declares, after a review of the P11 plan's entry against the migration found it covered 16 of the 22 (pushed after the run on `24c22ca` had finished).
- **The records commit** follows the run of record (run 42759801460, on `b97bc15`), as the push rule requires.

### Start gate and environment

- **The environment check, names only.** None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` was set, and no `STREAM_*` or `PG*` name. The GitHub token names `GH_TOKEN` and `GITHUB_TOKEN` were present; they were never read, and every repository command ran in a clean process environment (`env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus `GLOW_ENV=test` for the API). The proxy and CA variables were passed to `npm ci` by reference, never printed.
- **The toolchain:** CPython 3.12.14 as `python3.12` (`services/api/.python-version`: 3.12.14), Node v24.19.0, npm 11.9.0, Docker 29.9.2 (build `a82e528`). `$HOME/.local/bin` is second on `PATH`, after `/nix/var/nix/profiles/default/bin`, which holds only Nix's own tools; `python3.12`, `node` and `npm` resolve to `$HOME/.local/bin`.
- **The start gate** (each line as the prompt has it):
  - `git fetch origin claude/magical-wozniak-yfmmx2 main`: fetched;
  - the session branch at `a6624de`, and `git rev-parse HEAD` printed `a6624de1568ed248dc975d9ae3a9e8863969f9b6`;
  - `PR42 present` (`df8a04c` is an ancestor);
  - no non-Markdown path differs from `main`'s `c864edd`;
  - no owned path differs from the live manager branch. Its head was then `bf62e40` (AM10-13), whose only change since `a6624de` is `docs/continuity/manager-mistakes.md`, and `a6624de` is on it;
  - `services/api/glow_profiles` did not exist;
  - the migrations were `0001` to `0004` only;
  - the brief's "Sessions" recorded no Stage A implementation session.

### The area file (D5)

- **The source:** the Census Bureau's 2024 Gazetteer file for core-based statistical areas, a work of the US government in the public domain: `https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/2024_Gaz_cbsa_national.zip`.
- **The download, once.** A first request, to a mistyped path without the `2024_Gazetteer/` segment, answered 404 with an HTML page; nothing was kept, and its empty directory was removed. The brief's URL was then fetched once, into a new empty directory in the session's scratchpad, outside the checkout: HTTP 200, 46,177 bytes, `application/zip`, last modified Fri, 30 Aug 2024 18:40:40 GMT.
- **The three hashes:**
  - the zip: `0ec21c5d83982467903f1500fbbae87311edc81f09bed8ec1bbded80bce7eec3`, D5's;
  - its one member, `2024_Gaz_cbsa_national.txt` (188,130 bytes, 936 lines: a header and 935 areas, UTF-8, LF), extracted with `python3.12 -I` into another new empty directory: `31b285827a72b9f7917b312d458d01e2efe2909e4c5cb7b4b760b6bb0725f787`, D5's;
  - the derived table, `services/api/glow_profiles/data/cbsa_areas_2024.tsv` (50,458 bytes, 926 lines: a header and **925 areas**): `2bf5e4da9e9904931cae26e900b75617e4b4a529f14f96a262883f6381e31138`.
- **The derivation step:** `services/api/glow_profiles/areas_source.py`, standard library only, run with `python3 -I` and the paths as arguments (`derive <source.txt> <out>`; `verify <table>`). It checks the source's hash, its header and ten columns, 935 areas, unique five-digit GEOIDs, each name ending in its states and type, and each internal point a published decimal in range. It drops the 10 areas whose only state is PR (no area spans PR and a state) and keeps 925, in GEOID order, as area ID, name, latitude and longitude, tab-separated. 59 multi-state areas are kept.
- **Pinned:** `areas_source.DERIVED_SHA256` and migration 0006's `AREA_FILE_SHA256` hold the table's hash; 0006 refuses a changed table before loading it, and nothing is fetched at migration, test or run time (`tests/test_profile_areas.py`; the proof's `area.file_hash_and_925_areas`).

### Outcome items and acceptance checks

Each test is in `services/api/tests/` (the API's, no database) or in `proofs/postgres-ordering/glow_ordering_proof/profile_cases.py` (the proof's cases, on the third disposable database, through the HTTP endpoints). Each reversal is named in "The reversals", below.

| Item or check | Files | Tests | Reversals |
|---|---|---|---|
| **Outcome 1, the settings store (D2); check 1** | `glow_domain/profile_settings.py`; `glow_profiles/settings_store.py`, `staff.py`; `glow_persistence/models.py` (`SettingVersion`); migrations 0005, 0007 | API: `test_profile_settings` (the schemas, the fixed limits, the launch defaults, the seed equal to the code). Proof: `settings.launch_defaults`, `settings.publication_writes_version_audit_event`, `settings.fixed_limits_refused_before_any_write`, `settings.pointer_read_under_lock`, `settings.retired_value_stays_matchable` | `D2.limit-crossed-written`, `D2.no-staff-audit`, `D2.no-policy-published`, `D2.pointer-unlocked`, `D2.retired-refused-for-holder` |
| **Outcome 2, the fields (D3); checks 2 and 3** | `glow_domain/profile_fields.py`; `glow_profiles/operations.py` (`set_field`, `set_preferences`), `catalog.py`, `contract.py`; models `ProfileFieldChoice`, `PreferenceSetEntry` | API: `test_profile_fields` (pick limits, reserved and retired values, the two-way rule, own words, display, the whitespace set). Proof: `fields.values_within_pick_limits`, `fields.sensitive_needs_consent`, `fields.own_words_bounded_and_displayed_only_when_shown`, `sets.start_at_all_and_stay_the_owners`, `sets.all_marker_not_stated_and_decliners` | `D3.all-stored-as-list`, `D3.not-stated-narrowed`, `D3.sensitive-field-without-consent`, `D3.own-words-without-consent`, `D3.narrowed-sensitive-set-without-consent`, `D3.over-pick-limit` |
| **Outcome 3, age range and location (D4, D5); checks 4 and 5** | `glow_profiles/operations.py` (`set_filters`, `set_area`, `nearest_area`), `areas.py`, `areas_source.py`; models `Area`, `Preferences`, `Profile`; migrations 0005, 0006 | API: `test_profile_areas` (the file, its hashes, the nearest internal point), `test_profile_contract` (no radius or coordinate in the catalog; refusals name the path, never the value). Proof: `filters.age_range_floor_and_order`, `area.chosen_by_id`, `area.nearest_query_changes_nothing`, `area.coordinates_never_kept_or_echoed`, `area.no_route_returns_a_distance`, `area.file_hash_and_925_areas` | `D4.floor-at-the-contract`, `D4.floor-at-the-operation`, `D5.*` (12) |
| **Outcome 4, consent and the adult check (D6, D7); checks 6 and 7** | `glow_profiles/operations.py` (`decide_onboarding_consent`, `decide_sensitive_consent`, `adult_check`), `requirements.py`; `glow_domain/identity.py` (the age section); `glow_identity/age.py` (`transition`, `age_years`); models `ConsentDecision`, `AccountAgeState` | API: `test_profile_age` (whole years, the leap-day boundary, the transition's shape, its refusal outside a transaction). Proof: `consent.onboarding_reaches_the_send_check`, `consent.old_version_refused`, `consent.purposes_never_satisfy_or_revoke_each_other`, `consent.sensitive_withdrawal_scope`, `consent.withdrawal_on_a_paused_profile_stays_paused`, `adult.eighteen_today_and_the_leap_days_pass`, `adult.failing_dates_are_refused_and_not_stored`, `adult.a_corrected_date_reruns_and_demotes`, `adult.a_birth_input_with_another_date_changes_it`, `adult.transition_bumps_and_waits_on_the_account_lock`, `adult.a_new_date_makes_the_birth_input_missing` | `D6.*` (7), `D7.*` (6) |
| **Outcome 5, the private birth input (D8); check 8** | `glow_profiles/operations.py` (`save_birth_input`, `_mapping_to_pending`, `_invalidate_birth_input`) | Proof: `birth.submit_correct_change_write_private_revisions`, `birth.a_time_is_required_and_approximate_is_kept`, `birth.needs_the_adult_pass_and_current_consent`, `birth.a_seeded_mapping_returns_to_pending`, `completion.needs_the_chart_and_identity_verification_seeded` | `D8.*` (4) |
| **Outcome 6, visibility and completion (D9, D18); check 9** | `glow_profiles/operations.py` (`save_profile`, `set_visibility`, `_demote_if_visible`), `requirements.py`, `identity_verification.py`, `staff.py`; `glow_domain/identity_verification.py`; model `IdentityVerification` | API: `test_profiles_offline` (the port refuses a passed check; no SV2 code writes `verified` or a resolved mapping; the account row first). Proof: `completion.refuses_each_missing_requirement`, `completion.needs_the_chart_and_identity_verification_seeded`, `visibility.pause_and_resume_through_glow_chat`, `visibility.resume_rechecks_completion`, `staff.approval_gated_narrow_survives_and_is_revocable`, `staff.no_member_route_reaches_a_staff_operation`, `completion.each_change_emits_its_event`, `completion.takes_the_account_lock_first_and_sees_a_withdrawal`, `completion.removals_demote_and_empty_values_are_refused` | `D9.*` (4), `D18.*` (4) |
| **Outcome 8, the member's routes (D11); check 11** | `glow_profiles/views.py`, `urls.py`, `contract.py`, `idempotency.py`, `tx.py` | API: `test_profile_contract` (the server's request checks against the contract's validator on every corpus case and every case one change away; each projection as its DTO), `test_profiles_offline` (the routes, no staff route, no request atomicity, codes only in refusals and logs). Proof: `ownership.every_route_refuses_strangers_and_stale_versions`, `ownership.a_replay_and_a_conflicting_key`, and every served body checked against its DTO (`check_body`) in every case | `D17.extra-field`, `D17.another-members-object`, `D18.member-route-to-staff` |
| **Outcome 9, the proof (D12)** | `proofs/postgres-ordering/glow_ordering_proof/profile_*.py`, `schema_check.py`, `__main__.py`; `.github/workflows/foundation.yml` (the Database proof checks job's steps) | Proof offline: `tests/test_profile_offline.py` (the settings' refusals, the job's secret check, the upload gate and the SV2 steps as the job runs them, the plan, the schema check on every production corpus case, the value ledger, the commands' refusals). The run of record, below | (the job's own checks: the other markers refused, the second run refused, counts only after a failed check) |
| **Outcome 10, sealed (D13)** | none in `glow_api/` | API: `test_profiles_sealed_runtime` | `D13.runtime-imports-glow-profiles` |
| **DB04's part (the schema's own refusals)** | migration 0005's constraints | Proof: `constraints.malformed_direct_writes_are_refused` (25 direct writes: all 22 constraints migration 0005 declares, each write breaking one only, and two foreign keys; the case checks, from the migration itself, that every declared constraint has its write) | `DB04.constraint-dropped`, `DB04.version-check-dropped` |
| **Check 12, no secret or member value in any output; the keyed digests (D17)** | `glow_profiles/idempotency.py`; `profile_suite.py`, `profile_support.py` (`ValueLedger`), `profile_scan.py` | API: `test_profiles_offline` (`KeyedDigestTests`; `NoValueInLogsTests`). Proof: `digests.keyed_and_not_reproducible_without_the_key`, the suite's two scans after every case, and the job's own check (`profile_scan`) | `D17.unkeyed-digest`, `LOG.own-words`, `LOG.sensitive-value`, `LOG.birth-date-and-time`, `D5.coordinates-logged` |

Outcome 7 (photos) and acceptance check 10 are Stage B's. Outcome 11 is this record and the records commit: the data model's profile, preferences, consent, age state and identity verification rows; the contract document's F02 to F06 index rows, their server mapping and `staff_approval` in the oracle's list; the note in `profiles-preferences-fixtures.md`; and the P11 plan's partial evidence.

### The reversals (D15)

Each reversal is a temporary edit that must make its test fail. A harness in the session's scratchpad applied each edit exactly once per anchor, ran the test, recorded the failing lines, and restored the files byte for byte, checking each file's SHA-256 against its value before the edit. Each proof reversal ran on a new database in the throwaway PostgreSQL (D4; iteration, not evidence), migrated from zero. `git status` was clean after the batch.

**59 reversals; every one made its test fail.** On the first pass (57), 53 failed as required. One was a harness error: the first reversal's database name had been used by a trial run, so its database was not created and the result proved nothing; it was rerun on a new database and failed as required. **Three were not caught, and each exposed a weak test,** strengthened in `24c22ca`, then rerun and caught:
- `D5.coordinates-read-from-headers`: the case's headers-only request had an empty body, which Django's test client sends with no content type, so the route refused it for that and no header was ever read. The case now also sends the coordinate headers beside a JSON body without them, which must be refused.
- `D7.transition-without-the-account-lock`: without the account row lock, the transition still waited on the account row at its eligibility bump's `UPDATE`, after locking the age state's row, so "a wait was observed" held although the order was inverted. The case now locks the age state's row with `NOWAIT` from a third connection while the transition waits: it must succeed.
- `LOG.own-words`: the proof's value scan caught it, but the API's static check, which looked at `logger` calls only, missed a logger reached through `__import__("logging")`. The check now refuses any import of `logging`, `getLogger` or import by name outside the views.

The 58th and 59th, `DB04.constraint-dropped` and `DB04.version-check-dropped`, are the new constraints case's own: each drops one constraint from the throwaway database before the case runs, and both ran again on the extended case (`b97bc15`). Before the batch, three cases were strengthened so that their reversals could be seen at all: the filters case calls the operation directly with a minimum of 17 (the contract refuses it first at the route); the coordinates case gives its member a profile, a row the coordinates must not reach; and the completion case points a resolved mapping at an older revision.

| Reversal | The temporary edit | File | Test that failed | Failing output |
|---|---|---|---|---|
| `D2.limit-crossed-written` (first pass: harness error, rerun) | a publication that crosses a fixed limit is written anyway | `glow_profiles/settings_store.py` | proof: `settings.fixed_limits_refused_before_any_write` | `list_reserved_value: the publication is refused` |
| `D2.no-staff-audit` | StaffAudit is not written | `glow_profiles/settings_store.py` | proof: `settings.publication_writes_version_audit_event` | `a StaffAudit row names the staff` |
| `D2.no-policy-published` | policy_published is not written | `glow_profiles/settings_store.py` | proof: `settings.publication_writes_version_audit_event` | `policy_published is emitted` |
| `D2.pointer-unlocked` | the pointer is read without its lock | `glow_profiles/settings_store.py` | proof: `settings.pointer_read_under_lock` | `the member's write waited on the publication's pointer lock` |
| `D2.retired-refused-for-holder` | a retired value is refused for its holder (a retirement strips it from the holders) | `glow_profiles/settings_store.py` | proof: `settings.retired_value_stays_matchable` | `the holder still holds it` |
| `D3.all-stored-as-list` | "all" stored as the current list: a value the console adds is then missing | `glow_profiles/operations.py` | proof: `sets.all_marker_not_stated_and_decliners` | `added value seen` |
| `D3.not-stated-narrowed` | "not stated" accepted in a narrowed set | `glow_domain/profile_fields.py` | proof: `sets.all_marker_not_stated_and_decliners`; API: `test_profile_fields.ShowMeTests` | `not-stated: answers 400`; `test_all_or_a_narrowed_list_of_live_values: AssertionError: 'not_narrowable' != 'reserved_value'` |
| `D3.sensitive-field-without-consent` | a sensitive field saved without the sensitive-fields consent | `glow_profiles/operations.py` | proof: `fields.sensitive_needs_consent` | `orientation refused: answers 403` |
| `D3.own-words-without-consent` | orientation's own words saved without the sensitive-fields consent | `glow_domain/profile_fields.py` | proof: `fields.sensitive_needs_consent`; API: `test_profile_fields.OwnValueTests.test_what_carries_sensitive_data` | `orientation refused: answers 403`; `test_what_carries_sensitive_data: AssertionError: False is not true` |
| `D3.narrowed-sensitive-set-without-consent` | a narrowed sensitive set saved without the sensitive-fields consent | `glow_profiles/operations.py` | proof: `fields.sensitive_needs_consent` | `a narrowed sensitive set refused: answers 403` |
| `D3.over-pick-limit` | an own value outside its pick limit accepted | `glow_domain/profile_fields.py` | proof: `fields.values_within_pick_limits`; API: `test_profile_fields.OwnValueTests.test_values_within_the_pick_limit` | `gender refused: answers 400`; `test_values_within_the_pick_limit: AssertionError: None != 'over_pick_limit'` |
| `D4.floor-at-the-contract` | a minimum below 18 accepted by the request check | `glow_profiles/contract.py` | API: `test_profile_contract.RequestParityTests` | `test_the_server_decides_every_case_one_change_away_as_the_contract_does: AssertionError: Lists differ: [('valid-FiltersIntent', '{"operation": "f[2245 chars]"}')] != []` |
| `D4.floor-at-the-operation` | a minimum below 18 accepted by the operation | `glow_profiles/operations.py` | proof: `filters.age_range_floor_and_order` | `the operation's floor` |
| `D5.coordinates-stored` | the coordinates stored (on the member's profile row) | `glow_profiles/operations.py` | proof: `area.coordinates_never_kept_or_echoed` | `no table holds the coordinates (outbox and idempotency records included)` |
| `D5.coordinates-logged` | the coordinates logged | `glow_profiles/operations.py` | proof: `area.coordinates_never_kept_or_echoed` | `values found in output: 4; secrets found: 0` |
| `D5.coordinates-returned` | the coordinates returned | `glow_profiles/operations.py` | proof: `area.coordinates_never_kept_or_echoed` | `a query: the body is its DTO` |
| `D5.coordinates-in-the-outbox` | the coordinates put in the outbox | `glow_profiles/operations.py` | proof: `area.nearest_query_changes_nothing`, `area.coordinates_never_kept_or_echoed` | `no row, no event and no idempotency record is written` |
| `D5.coordinate-in-a-validation-message` | a coordinate in a validation message (the refusal's path) | `glow_profiles/contract.py` | proof: `area.coordinates_never_kept_or_echoed`; API: `test_profile_contract.RequestParityTests.test_a_refusal_names_the_field_never_its_value` | `the exception's text`; `test_a_refusal_names_the_field_never_its_value: AssertionError: '91.7123457' unexpectedly found in "AreaQuery.latitude=91.7123457Invalid('AreaQuery.latitude=9` |
| `D5.coordinate-in-an-exception` | a coordinate in an exception's text (a mistyped coordinate) | `glow_profiles/contract.py` | API: `test_profile_contract.RequestParityTests.test_a_refusal_names_the_field_never_its_value` | `test_a_refusal_names_the_field_never_its_value: AssertionError: '40.7123457' unexpectedly found in "AreaQuery.latitude is not a number: 40.7123457Invalid('Are` |
| `D5.coordinate-in-an-error` | a coordinate in an error response (the refused body echoed) | `glow_profiles/views.py` | proof: `area.coordinates_never_kept_or_echoed` | `coordinates in a query string: the body is the contract's Error` |
| `D5.coordinates-in-a-query-string` | the coordinates taken from a URL's query string | `glow_profiles/views.py` | proof: `area.coordinates_never_kept_or_echoed` | `coordinates in a query string: answers 400` |
| `D5.coordinates-in-a-response-header` | the coordinates in a response header | `glow_profiles/views.py` | proof: `area.coordinates_never_kept_or_echoed` | `no response header holds them` |
| `D5.coordinates-read-from-headers` (first pass: not caught; the test was strengthened, then rerun) | the coordinates read from request headers (they override a body without them) | `glow_profiles/views.py` | proof: `area.coordinates_never_kept_or_echoed` | `coordinates in headers beside a JSON body without them: answers 400` |
| `D5.query-sets-the-area` | the phone-location query setting the area | `glow_profiles/operations.py` | proof: `area.nearest_query_changes_nothing` | `the area is not set` |
| `D5.distance-returned` | a distance returned | `glow_profiles/operations.py` | proof: `area.no_route_returns_a_distance` | `no served body names distance_miles` |
| `D6.old-version-accepted` | the version check removed: an old consent version accepted | `glow_profiles/operations.py` | proof: `consent.old_version_refused` | `an old onboarding version: answers 409` |
| `D6.purpose-filter-removed` | the purpose filter removed: a sensitive_profile decision satisfies or revokes onboarding consent | `glow_profiles/requirements.py` | proof: `consent.purposes_never_satisfy_or_revoke_each_other` | `onboarding: required` |
| `D6.withdrawal-leaves-the-fields` | the withdrawal leaving the two fields | `glow_profiles/operations.py` | proof: `consent.sensitive_withdrawal_scope` | `removed` |
| `D6.withdrawal-leaves-own-words` | the withdrawal leaving orientation's own words (values reset, words kept) | `glow_profiles/operations.py` | proof: `consent.sensitive_withdrawal_scope` | `removed` |
| `D6.withdrawal-leaves-the-sets` | the withdrawal leaving the narrowed sets | `glow_profiles/operations.py` | proof: `consent.sensitive_withdrawal_scope` | `both sets reset` |
| `D6.withdrawal-leaves-the-records` | the withdrawal leaving the commands' idempotency records | `glow_profiles/operations.py` | proof: `consent.sensitive_withdrawal_scope` | `their idempotency records deleted` |
| `D6.accept-before-the-lock` | accept_consent called before the account lock | `glow_profiles/operations.py` | API: `test_profiles_offline.LockOrderTests` | `test_every_operation_takes_the_account_row_first: AssertionError: "if intent['decision'] == 'accepted':\n  [87 chars]']))" != 'lock_account(tx, account_id)'` |
| `D7.transition-without-the-account-lock` (first pass: not caught; the test was strengthened, then rerun) | the transition without the account row lock | `glow_identity/age.py` | proof: `adult.transition_bumps_and_waits_on_the_account_lock` | `while it waits, it holds no lock on the age state's row: account first` |
| `D7.transition-without-the-bump` | the transition without the eligibility bump | `glow_identity/age.py` | proof: `adult.transition_bumps_and_waits_on_the_account_lock` | `the transition bumps eligibility_version` |
| `D7.failing-date-stored` | a failing date stored (the check passes an under-18 date) | `glow_profiles/operations.py` | proof: `adult.failing_dates_are_refused_and_not_stored` | `a failing date: answers 403` |
| `D7.failing-rerun-leaves-date-and-state` | a failing rerun leaving the date and the state | `glow_profiles/operations.py` | proof: `adult.a_corrected_date_reruns_and_demotes` | `the corrected date: answers 200` |
| `D7.failing-rerun-leaves-visible` | a failing rerun leaving a visible profile | `glow_profiles/operations.py` | proof: `adult.a_corrected_date_reruns_and_demotes` | `the visible profile demoted` |
| `D7.new-date-leaves-birth-input-current` | a new eligibility date leaving the current birth input current | `glow_profiles/operations.py` | proof: `adult.a_new_date_makes_the_birth_input_missing` | `the current revision is missing` |
| `D8.unknown-time-accepted` | a birth input with time_precision unknown accepted | `glow_profiles/operations.py` | proof: `birth.a_time_is_required_and_approximate_is_kept` | `an unknown time: answers 400` |
| `D8.mapping-left-resolved` | a new revision leaving the mapping resolved | `glow_profiles/operations.py` | proof: `birth.a_seeded_mapping_returns_to_pending` | `pending` |
| `D8.mapping-at-the-old-revision` | a new revision leaving the mapping pointing at the old revision | `glow_profiles/operations.py` | proof: `birth.a_seeded_mapping_returns_to_pending` | `pointing at the new revision` |
| `D8.completion-accepts-an-old-mapping` | completion accepting a resolved mapping that points at an old revision | `glow_profiles/requirements.py` | proof: `completion.needs_the_chart_and_identity_verification_seeded` | `a mapping at an older revision is no chart` |
| `D9.resume-without-completion` | resume without the completion check | `glow_profiles/operations.py` | proof: `visibility.resume_rechecks_completion` | `resume of an incomplete profile: answers 403` |
| `D9.completion-read-before-the-lock` | completion read before the account lock: a withdrawal while a completion waits is not seen | `glow_profiles/operations.py` | proof: `completion.takes_the_account_lock_first_and_sees_a_withdrawal` | `and saw the withdrawal` |
| `D9.removal-refused` | a removal the member is entitled to make refused instead of demoting (a withdrawal on a visible profile) | `glow_profiles/operations.py` | proof: `completion.removals_demote_and_empty_values_are_refused` | `withdrawn: answers 200` |
| `D9.required-value-cleared` | a required value cleared instead of refused (an empty gender saved) | `glow_domain/profile_fields.py`, `glow_profiles/contract.py` | proof: `completion.removals_demote_and_empty_values_are_refused` | `an empty gender: answers 400` |
| `D17.unkeyed-digest` | an unkeyed digest, reproducible from its command | `glow_profiles/idempotency.py` | proof: `digests.keyed_and_not_reproducible_without_the_key`; API: `test_profiles_offline.KeyedDigestTests` | `not unkeyed`; `test_a_stored_digest_cannot_be_reproduced_without_the_key: AssertionError: False is not true` |
| `D17.extra-field` | an extra field in a response (the account ID in the own profile) | `glow_profiles/contract.py` | proof: `ownership.every_route_refuses_strangers_and_stale_versions`; API: `test_profile_contract.ProjectionTests` | `the profile: the body is its DTO`; `test_each_projection_validates_as_its_dto: AttributeError: 'types.SimpleNamespace' object has no attribute 'account_id'` |
| `D17.another-members-object` | another member's object returned (a birth input by ID) | `glow_profiles/operations.py` | proof: `ownership.every_route_refuses_strangers_and_stale_versions` | `their input: answers 404` |
| `D18.approval-while-off` | a staff approval accepted while the setting is off | `glow_profiles/staff.py` | proof: `staff.approval_gated_narrow_survives_and_is_revocable` | `refused while off` |
| `D18.approval-stands-in-for-consent-and-age` | a staff approval standing in for consent and the adult check | `glow_profiles/requirements.py` | proof: `staff.approval_gated_narrow_survives_and_is_revocable` | `only that` |
| `D18.member-route-to-staff` | a member route reaching a staff operation | `glow_profiles/urls.py`, `glow_profiles/views.py` | proof: `staff.no_member_route_reaches_a_staff_operation`; API: `test_profiles_offline.ProfileRoutesTests` | `SV1's routes and SV2's only`; `test_the_member_routes_are_served_and_no_staff_route: AssertionError: Items in the first set but not the second:` |
| `D18.switch-off-removes-approvals` | switching the setting off removing past approvals | `glow_profiles/settings_store.py` | proof: `staff.approval_gated_narrow_survives_and_is_revocable` | `a past approval survives the switch-off` |
| `D13.runtime-imports-glow-profiles` | the runtime importing glow_profiles (through glow_domain.identity, which it imports) | `glow_domain/identity.py` | API: `test_profiles_sealed_runtime` | `test_the_age_section_imports_nothing_new: AssertionError: Lists differ: ['fro[102 chars] typing import Protocol', 'import glow_profiles  # noqa: F401'] ` |
| `LOG.own-words` (first pass: not caught; the test was strengthened, then rerun) | an own-words value logged (the field write) | `glow_profiles/operations.py` | proof: `fields.own_words_bounded_and_displayed_only_when_shown`; API: `test_profiles_offline.NoValueInLogsTests` | `values found in output: 2; secrets found: 0`; `test_nothing_but_the_views_reaches_logging_or_imports_by_name: AssertionError: Lists differ: ['operations.py:418 gets a logger', 'operations.py:418 imports by name'] != [` |
| `LOG.sensitive-value` | a sensitive field's value logged (the field write) | `glow_profiles/operations.py` | proof: `fields.values_within_pick_limits` | `values found in output: 3; secrets found: 0` |
| `LOG.birth-date-and-time` | a birth date and time logged (the birth input write) | `glow_profiles/operations.py` | proof: `birth.a_time_is_required_and_approximate_is_kept` | `values found in output: 2; secrets found: 0` |
| `DB04.constraint-dropped` (rerun on the extended case) | a declared constraint missing from the database (age_state_birth_date dropped) | the throwaway database (SQL, before the case) | proof: `constraints.malformed_direct_writes_are_refused` | `PostgreSQL refuses the write by age_state_birth_date` |
| `DB04.version-check-dropped` | a new model's version check missing from the database (glow_persistence_profilefieldchoice_version dropped) | the throwaway database (SQL, before the case) | proof: `constraints.malformed_direct_writes_are_refused` | `PostgreSQL refuses the write by glow_persistence_profilefieldchoice_version` |

### The contract (D11)

- **New definitions (20),** all additive: `OwnWords`, `AreaId`, `ProfileFieldIntent`, `OwnFieldValue`, `OwnProfileFields`, `FiltersIntent`, `OwnFilters`, `AreaIntent`, `OwnArea`, `AreaQuery`, `NearestArea`, `CatalogValue`, `CatalogField`, `ConsentPolicy`, `ProfileCatalog`, `OwnCompletion`, `SensitiveConsentIntent`, `OwnSensitiveConsent`, `AdultCheckIntent`, `OwnAgeState`. `AppIntent` gains `ProfileFieldIntent`, `FiltersIntent`, `AreaIntent`, `SensitiveConsentIntent` and `AdultCheckIntent`; `AppResponse` gains `OwnProfileFields`, `OwnFilters`, `OwnArea`, `NearestArea`, `ProfileCatalog`, `OwnCompletion`, `OwnSensitiveConsent` and `OwnAgeState`. No other existing definition changes. `openapi.json` gains the 20 components; its paths map stays empty.
- **`AdultCheckIntent` and `OwnAgeState`** are additions D11's list did not name: D7's step needs an intent and a read of its own, and neither fits an existing closed payload.
- **The registry (`flows-v1.json`),** with an allowed and a forbidden example of each new entry in `packages/contracts/tests/test_transition_contract.py` (`SV2StageATransitionTests`); no existing entry changes, and F05 is untouched:
  - **F02:** `accept_sensitive` from `not_given` and `withdrawn` to `accepted` (`owner`; `consent_current`); `withdraw_sensitive` from `accepted` to `withdrawn` (`owner`); `adult_check` from `unknown`, and from `self_declared_adult` to itself, to `self_declared_adult` (`owner`; `A05`); `adult_check_failed` from `self_declared_adult` to `unknown` (`owner`); `id_check_passed` from `unverified` and `staff_approved` to `verified` (`provider`); `approve_without_id` from `unverified` to `staff_approved` (`moderator`; `A05`, `staff_approval`); `revoke_approval` from `staff_approved` to `unverified` (`moderator`; `A05`). Tests: `test_f02_sensitive_consent_has_events_of_its_own`, `test_f02_adult_check`, `test_f02_identity_verification_and_staff_approval` (the setting off is `policy_unresolved`; neither event reads as F01's email verification);
  - **F03:** `date_changed` from `pending`, `ambiguous`, `resolved`, `unavailable` and `unsupported` to `missing` (`owner`). Test: `test_f03_a_new_eligibility_date_makes_the_birth_input_missing`;
  - **F04:** `requirement_removed` from `visible` to `incomplete` (`system`). Test: `test_f04_requirement_removed_is_the_systems_demotion` (`paused` is a `state_conflict`; the owner's `edit` keeps its own entry);
  - **the DTOs** in F02's and F04's `request_contracts`, `response_contracts` and `projection_roles` (`owner`). Test: `test_sv2_projections_are_the_owners_only` (another owner, a revoked session, staff, the system, the provider and the public read `not_found`).
- **The corpus:** 123 new cases (709 in all: 579 production, 130 development), each DTO's valid and invalid cases.
- **The server's request checks** (`glow_profiles/contract.py`) decide every corpus case of their 11 definitions as `packages/contracts/runtime.py` does (each definition has cases both ways), and every case one change away from a valid one: each value replaced by each of 48 probes, a field removed or added, a list emptied or an entry repeated, 6,830 cases, through both `valid` and `parse`. That comparison found one difference, fixed before the code head: JSON Schema's integer is any number with no fractional part, so the contract accepts `1.0` as a version, and the server now does too, handing the operations an `int` so that a digest does not depend on how a number was written.
- **The README:** "SV2 Stage A: the profile's contract", in `packages/contracts/README.md`.
- **Generated outputs:** `npm run generate --prefix packages/contracts`, run twice, the second changing nothing (the outputs' SHA-256 equal after each run). Changed: `apps/mobile/src/contracts/generated/gapp-api-v1.ts`, `validators.js` and `validators.d.ts`. Unchanged: `gapp-dev-v1.ts`. No mobile source, test or fixture changed.

### The threat model's inputs

**Every route** (`services/api/glow_profiles/urls.py`; sealed: only the proof's `profile_urls.py` serves them). Who may call: an actor from SV1's `GlowActorAuthentication` only, an `active` account with a `valid`, unexpired session at the account's current epoch. Every route refuses an unauthenticated call (401 `unauthenticated`), another method (405 `invalid_request`), any query string (400 `invalid_request`), a body that is not its DTO or not `application/json` (400 `invalid_request`), and another member's object (404 `not_found`); every command refuses a stale version (409 `stale_version`) and another intent under a used key (409 `idempotency_conflict`). No refusal or log line carries a submitted value; every response is `Cache-Control: no-store`. Tests: `ownership.every_route_refuses_strangers_and_stale_versions`, `ownership.a_replay_and_a_conflicting_key`, `test_profiles_offline`.

| Route | Methods | Request → response | Refusals of its own (beyond the above) |
|---|---|---|---|
| `api/v1/profile` | GET, POST | `ProfileIntent` → `OwnProfile` | 409 `state_conflict` (a profile that is not editable) |
| `api/v1/profile/<profile_id>` | GET | → `OwnProfile` | 404 for another member's profile |
| `api/v1/profile/completion` | GET | → `OwnCompletion` | |
| `api/v1/profile/visibility` | POST | `VisibilityIntent` → `OwnProfile` | 403 `forbidden` (a resume while incomplete); 409 `state_conflict` (a resume when not paused; `glow_chat`'s refusals) |
| `api/v1/profile/fields` | GET, POST | `ProfileFieldIntent` → `OwnProfileFields` | 400 (pick limit, unknown, retired, reserved, duplicate or empty values; bad own words; `looking_for` hidden); 403 (a sensitive value without the sensitive-fields consent); 409 `stale_version` (an old catalog version) |
| `api/v1/profile/preferences` | GET, POST | `PreferencesIntent` → `OwnPreferences` | 400 (a missing or unknown dimension; `all` with values; `not-stated`; an unknown or retired value; a field not narrowable); 403 (a narrowed sensitive set without the consent) |
| `api/v1/profile/filters` | GET, POST | `FiltersIntent` → `OwnFilters` | 400 (a minimum below 18, a maximum below the minimum, an unknown distance choice) |
| `api/v1/profile/area` | GET, POST | `AreaIntent` → `OwnArea` | 400 (an unknown area); 403 (no way of locating offered) |
| `api/v1/profile/area/nearest` | POST | `AreaQuery` → `NearestArea` | 400 (out of range, mistyped or extra fields; coordinates anywhere but the body); 403 (the approximate location not offered). Writes nothing |
| `api/v1/profile/catalog` | GET | → `ProfileCatalog` | |
| `api/v1/consent` | GET, POST | `ConsentIntent` → `OnboardingEligibility` | 409 `stale_version` (an old version); 409 `state_conflict` (a withdrawal with no decision) |
| `api/v1/consent/sensitive` | GET, POST | `SensitiveConsentIntent` → `OwnSensitiveConsent` | the same two |
| `api/v1/eligibility/adult` | GET, POST | `AdultCheckIntent` → `OwnAgeState` | 403 (under 18 on the server's date); 400 (a future or invalid date); neither is stored |
| `api/v1/birth-input` | GET, POST | `BirthInputIntent` → `OwnBirthInput` | 403 (no adult pass; no current onboarding consent); 400 (an unknown time; a future date) |
| `api/v1/birth-input/<input_id>` | GET | → `OwnBirthInput` | 404 for another member's revision |

**Every staff operation** (`glow_profiles/staff.py` and `settings_store.publish`). No route reaches one: a staff subject reaches each only as a Python call with a staff subject (`staff:` and up to 200 characters of `[A-Za-z0-9._@-]`), a reason (a code of up to 100 characters) and a request ID, which P07's staff API will supply after its own authentication. Each writes a `StaffAudit` row in its transaction. A member's subject is refused.
- `publish_setting(name, content, …)`: the next version of a setting, refused with nothing written if the content fails its closed schema or crosses a fixed limit, or if the request ID was used. Tests: `settings.*`.
- `approve_without_id(account, …)`: only while `identity.staff_approval` is on, read under its pointer's lock; `unverified` to `staff_approved`. Test: `staff.approval_gated_narrow_survives_and_is_revocable`.
- `revoke_approval(account, …)`: at any time; `staff_approved` to `unverified`, and a `visible` profile is demoted. Same test, and `completion.removals_demote_and_empty_values_are_refused`.
- `restrict_profile(account, …)`: `glow_chat`'s `restrict_profile`, nested (it emits `profile_restricted` itself). The registry has no entry for profile restriction; it was absent before SV2.

**Every stored value that is private, sensitive or derived from the phone's location** (all account-private; each model's account foreign key cascades with the account, whose deletion is P08's):

| Value | Where | What removes or changes it | Tests |
|---|---|---|---|
| Display name, summary | `Profile` | the owner's edit | `completion.*` |
| The home area (derived from the phone's location when the member sets the area the query returned) | `Profile.area`, a reference to `Area` | the owner sets another area; never cleared by an edit | `area.*` |
| The phone's coordinates | **nowhere**: in the request's memory only, never stored, logged, returned, echoed, put in the outbox or an idempotency record | | `area.coordinates_never_kept_or_echoed` (every table searched, every response body and header, the exception's text) |
| Gender, looking for, their own words, the display flags | `ProfileFieldChoice` | the owner's next choice | `fields.*` |
| **Sensitive:** orientation and relationship status values, orientation's own words | `ProfileFieldChoice` | the sensitive-fields consent's withdrawal deletes them, in its transaction | `consent.sensitive_withdrawal_scope` |
| The "show me" sets | `PreferenceSetEntry` | the owner's next sets; the withdrawal resets the two sensitive sets to all | `sets.*`, `consent.sensitive_withdrawal_scope` |
| The age range, the distance choice | `Preferences` | the owner's next filters | `filters.age_range_floor_and_order` |
| Consent decisions | `ConsentDecision` (append-only) | none; a new decision supersedes | `consent.*` |
| **The birth date** | `AccountAgeState.birth_date` | a failing rerun clears it; a new date replaces it | `adult.*` |
| **The birth facts** (date, time, precision, place, time zone) | `BirthInput` revisions (append-only) | none in SV2; a new date makes the current revision `missing` | `birth.*` |
| The mapping's state | `EngineIdentity` (none created by SV2) | a new revision returns it to `pending` | `birth.a_seeded_mapping_returns_to_pending` |
| Identity verification: the state, the company's reference, or the staff subject and reason | `IdentityVerification` | a revocation returns it to `unverified`; no ID image, number or selfie is kept anywhere | `staff.*`, `completion.needs_the_chart_and_identity_verification_seeded` |
| Command digests | `IdempotencyRecord.request_digest`: `salted_hmac(<salt naming the operation>, <the canonical intent>, sha256)` under the settings' `SECRET_KEY`, 64 characters | expiry after 24 hours (deleted when the key is reused); the sensitive-fields withdrawal deletes the records of the commands that carried the two fields or their sets | `digests.keyed_and_not_reproducible_without_the_key`, `KeyedDigestTests` |
| Staff subjects and reasons | `StaffAudit`, `SettingVersion`, `IdentityVerification` | none (audit) | `settings.publication_writes_version_audit_event` |

**Every setting, its launch default (version 1, `system:launch-default`, reason OD-60, or OD-61 for D18's) and the fixed limits** (`glow_domain/profile_settings.py`; the seed in migration 0007 equals `LAUNCH_DEFAULTS`):
- `profile.gender`: woman, man, non-binary; pick 1. `profile.orientation`: no values (OD-60 names none); pick 1. `profile.looking_for`: long-term, short-term, casual, new friends, figuring it out; any number. `profile.relationship_status`: single, separated or divorcing, partnered (open or non-monogamous); pick 1;
- `profile.narrowing`: every field narrowable; "show me" never shown; not stated seen by those who keep all;
- `profile.age_range`: 18 to no maximum, both ways;
- `profile.location`: both ways of locating offered; one distance choice, `anywhere`; no coordinates stored and no distance shown;
- `discovery.resurfacing`, `discovery.undo`: off, no waiting period; `discovery.rematch`: off, never after a block or a report;
- `chat.history`: read-only for each cause, hidden after an unmatch or a block, a deletion as an unmatch, under `consent.onboarding.v1`;
- `identity.staff_approval`: off, standing in for identity verification only;
- `consent.onboarding`, `consent.sensitive_profile`: development text (P08 writes the wording).
- **The fixed limits** (a publication crossing one is refused, naming the limit): matching uses list values; the age floor is 18; never exact coordinates or an exact distance; rematch never after a block or a report; unmatch and block stay hidden; a deletion works as an unmatch; "show me" is never shown; a member who states none in an optional field appears only to viewers who keep all; a change to H that makes more readable reaches a member only after they accept the consent wording that describes it; no list holds more than 50 live values; a staff approval stands in for identity verification only; a list value is never `all` or `not-stated`; a published list value is retired, never removed. Bounds in code: labels 80 characters, consent text 4,000, at most 200 values per list, 20 distance choices, 5,000 miles, 3,650 waiting days, an age ceiling of 150. Tests: `test_profile_settings`; `settings.fixed_limits_refused_before_any_write` (each limit crossed, nothing written).

**Each writer's locks, in order** (READ COMMITTED; DM-13 4.1: the account row first; the settings' pointers `FOR SHARE` in name order; every member command then takes its idempotency record `FOR UPDATE`, after its rows and before any write, so it authorizes, then deduplicates; every SV2 operation is the whole of its transaction, `ATOMIC_REQUESTS` off, and `glow_chat`'s writers nest as savepoints):
- `save_profile`: the account `FOR UPDATE`; the catalog's seven pointers and the onboarding consent's; the profile.
- `set_field`: the account; the catalog's pointers; the profile; the field's row; the idempotency record.
- `set_preferences`, `set_filters`: the account; the catalog's pointers; the preferences row.
- `set_area`: the account; the location pointer; the profile.
- `nearest_area` and every read: the account `FOR SHARE`; the pointers they read. They write nothing.
- `decide_onboarding_consent`: the account; the onboarding consent's pointer; the profile; then `glow_chat`'s `accept_consent` or `withdraw_consent`.
- `decide_sensitive_consent`: the account; the sensitive consent's pointer; the preferences row.
- `adult_check`: the account; the age state; the profile; then the age port's `transition` (the account `FOR UPDATE`, already held, then the age state); the current birth input; the mapping.
- `save_birth_input`: the account; the onboarding consent's pointer; the age state; the current birth input; the profile; the mapping; the age port's `transition` when the date changes.
- `set_visibility`: the account; the onboarding consent's pointer; the profile; then `glow_chat`'s `pause_profile` or `resume_profile`.
- `publish`: the setting's pointer `FOR UPDATE` (and, for `chat.history`, the onboarding consent's `FOR SHARE`).
- `approve_without_id`: the account; the staff approval setting's pointer `FOR SHARE`; the identity verification row. `revoke_approval`: the account; the profile; the identity verification row. `restrict_profile`: the account; then `glow_chat`'s writer.
- Tests: `test_profiles_offline.LockOrderTests` (the first statement of every operation's transaction); `settings.pointer_read_under_lock`, `adult.transition_bumps_and_waits_on_the_account_lock`, `completion.takes_the_account_lock_first_and_sees_a_withdrawal` (each wait observed in `pg_locks`).

**Each event** (`glow_profiles/events.py`, schema `glow-profiles-1`; each carries only the aggregate's ID and version and a payload reference, no value; `glow_chat`'s delivery reads only its own `glow-chat-1` types): `policy_published`, `profile_edited`, `profile_completed`, `profile_demoted`, `profile_field_changed`, `preferences_changed`, `area_changed`, `sensitive_consent_accepted`, `sensitive_consent_withdrawn`, `age_state_changed`, `birth_input_submitted`, `birth_input_invalidated`, `identity_verification_changed`. The nested writers emit `glow_chat`'s own (`consent_accepted`, `consent_withdrawn`, `profile_paused`, `profile_resumed`, `profile_restricted`). Tests: `completion.each_change_emits_its_event`, `settings.publication_writes_version_audit_event`, `area.nearest_query_changes_nothing` (none for the query).

### Commands and results

**API** (`services/api`; `python3.12 -m venv .venv`, then `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`; every command with `GLOW_ENV=test` in a clean environment), on the final tree:
- `python manage.py check`: `System check identified no issues (0 silenced).`
- `python manage.py test tests --verbosity 2`: `Ran 516 tests in 29.576s`, `OK`.
- `python smoke.py`: `PASS /health/live: HTTP 200`, `PASS /health/ready: HTTP 503`, `PASS /api/v1/development/recommendations: HTTP 200`.
- `ruff check .`: `All checks passed!`; `ruff format --check .`: `131 files already formatted`.
- `mypy`: `Success: no issues found in 60 source files`. The configured files (`pyproject.toml`, not owned) leave out `glow_profiles`, so `mypy glow_profiles tests/test_profile_*.py tests/test_profiles_*.py` was also run: `Success: no issues found in 24 source files`.
- `python -m glow_persistence.static_check`: `Static definitions agree: 40 app models; migrations=0001_event_infrastructure,…,0007_settings_launch_defaults`.

**The contracts** (`packages/contracts`): `npm ci --ignore-scripts` (`found 0 vulnerabilities`); `npm run generate` twice (no further change); `npm run check`: `tests 709`, `pass 709`, `fail 0`. From `services/api`, `PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests -v`: `Ran 45 tests`, `OK`.

**The mobile app** (`apps/mobile`): `npm ci --ignore-scripts` (it reports 17 moderate-severity advisories in the existing lock, which SV2 does not change); `npm run check`: `tsc --noEmit` and `eslint .` clean, `tests 691`, `pass 691`, `fail 0`, with only the three generated files changed. Its export and rendered checks are CI's.

**The proof** (`proofs/postgres-ordering`, its venv and hash-locked install): `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8 .venv/bin/python -m unittest discover -s tests -t . -v`: `Ran 218 tests`, `OK`; `ruff check .`: `All checks passed!`; `ruff format --check .`: `59 files already formatted`; `mypy`: `Success: no issues found in 59 source files`.

**Local database runs: iteration, not evidence** (D4). Docker's daemon was started in the sandbox; the CI job's image pinned by digest (`postgres@sha256:d74eeac9…`, PostgreSQL 17.11) was pulled once from Docker Hub and published on `127.0.0.1:5433` only; the passwords, markers and keys were generated into a directory only the session's user could read; a new database with its own marker took each run; none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or a `PG*` name was present; the containers and files were removed afterwards.
- the profile suite during development: 43 of 43, both scans clean;
- **the Database proof checks job's own shell steps, run in order** from the credentials step to the cleanup, as the workflow has them (its `uses:` upload steps skipped, `::add-mask::` lines withheld from the output): every step passed. The ordering suite took 572 s, the identity suite 42 s and the profile suite 58 s (43 of 43; 820 secrets and 107 member values held, none found; the job's own check found none of its secrets); the profile database refused both other markers; the second profile run was refused with every count unchanged;
- the 59 reversals, each on its own new database;
- **the profile suite on `24c22ca`:** 44 of 44 in 63.3 s; secret scan clean (842 held; none in 530 log records, 106 writes and the results JSON); value scan clean (108 held);
- **the profile suite on `b97bc15`, the code head:** 44 of 44 in 66.0 s, the constraints case with its 25 writes; both scans clean (842 secrets and 108 member values held, none found).

### The run of record

**Foundation push run [42759801460](https://github.com/amthorn78/glow-dating-app/actions/runs/42759801460)** on `b97bc15cd7a5200eac6c7eb3e033131bebbe8e90`, **the code head** (attempt 1, 05:04:32 to 05:14:38 UTC on 10 November 2026). Every job passed, and the gate printed **`Application checks passed`**:

- **Change scope, API checks, API artifact checks, API mobile smoke, Stream proof checks:** success. API checks: **`Ran 516 tests`**, `OK`; Ruff, the format check and mypy clean; the Python contract tests `Ran 45 tests`, `OK`.
- **Mobile checks:** success. The contracts' check (`Generated types and runtime validators match schemas.`; 709 tests passed); `npm run check` (691 tests passed, with `tsc --noEmit` and `eslint .`); `check:expo`; `export:development`; the rendered checks: **104 passed, in 4.8 minutes**.
- **Database proof checks:** success, in 9 minutes 42 seconds of its 30-minute timeout. The offline tests (`Ran 218 tests`, `OK`), Ruff, the format check and mypy; the wrong marker and `dbshell` refused; the ordering suite `== VERDICT: PASS ==` (both subjects pass; 234 case rows passed, none failed; 0 oracle violations) and its second run refused; the identity suite 49 of 49 in 44.8 s (the identity phase 45 s), its second run refused; **the profile suite:** both other markers refused, the migrations from zero and `No changes detected`; **44 of 44 cases in 49.4 s; the profile phase 50 s**, the constraints case reading `25 malformed direct writes refused by PostgreSQL, each by its constraint: all 22 that migration 0005 declares, and two foreign keys`; `profile secret scan: clean (842 secrets held; 0 found in 530 log records, 106 writes and the results JSON)`; `profile value scan: clean (108 member values held …; 0 found in the same output)`; the job's own check found none of its secrets in the suite's output or in the results JSON, and the suite's scans clean; `PROFILE VERDICT: PASS`; a second profile run refused, every count unchanged (`74 74 60 30 606 516 before and after`); `sv2-profile-results` uploaded only after the check passed; the container and its files removed.
- **No toolchain retry fired:** every retry step was skipped.
- **No secret and no coordinate in the logs:** the Database proof checks job's whole log (2,094 lines), the API checks job's (2,143) and the Mobile checks job's (2,562) were each searched in full: no coordinate the suite sends appears; the only masked values are the checkout action's own token lines.

**The earlier run, on `24c22ca`:** Foundation push run [42758271326](https://github.com/amthorn78/glow-dating-app/actions/runs/42758271326) on `24c22caee1655e66719b0c0830ec057e25d1c319` (attempt 1, 04:49:32 to 04:56:32 UTC), the head before the DB04 extension. Every job passed, and the gate printed `Application checks passed`:

- **Change scope:** success; full scope.
- **API checks:** success. The scope and branch-cleanup policies' tests (14 and 18, `OK`); `manage.py check` (`System check identified no issues (0 silenced).`); `manage.py test tests --verbosity 2`: **`Ran 516 tests`**, `OK`; Ruff (`All checks passed!`), the format check (`131 files already formatted`), mypy (`Success: no issues found in 60 source files`); the Python contract tests (`Ran 45 tests`, `OK`).
- **Mobile checks:** success. The contracts' check (`Generated types and runtime validators match schemas.`; 709 tests, 709 passed); the app's `npm run check` (`tsc --noEmit`, `eslint .`, 691 tests, 691 passed); `check:expo` (`Dependencies are up to date`); `export:development` (`Exported: .work/native-export`); the rendered checks, **104 passed** (4.4 minutes); the empty-form layout evidence saved.
- **API mobile smoke, API artifact checks, Stream proof checks:** success.
- **Database proof checks:** success, in 6 minutes 43 seconds of its 30-minute timeout.
  - The offline tests (`Ran 218 tests`, `OK`), Ruff, the format check and mypy.
  - Three databases created for the non-superuser role, each with its own marker; a wrong marker refused, the proof's database unchanged and holding no table; `dbshell` refused.
  - **The ordering suite:** `VERDICT: PASS (reference)` and `VERDICT: PASS (adapter)`, the delivery and read phases, and `== VERDICT: PASS ==` (234 case rows passed, none failed; the oracle found 0 violations in either subject's rows); a second run refused, every count unchanged.
  - **The identity suite:** 49 of 49 in 32.2 s (the identity phase 33 s); its scan clean (754 secrets held, none found) and the job's own check clean; a second run refused, every count unchanged; `sv1-identity-results` uploaded.
  - **The profile suite:** the profile database refused the ordering and identity databases' markers (exit status 1 each, with the marker's refusal), took the migrations from zero (0005, 0006 and 0007 among them), and `makemigrations --check --dry-run` printed `No changes detected`. **44 of 44 cases in 31.7 s; the profile phase 32 s.** `profile secret scan: clean (842 secrets held; 0 found in 530 log records, 106 writes and the results JSON)`; `profile value scan: clean (108 member values held …; 0 found in the same output)`; the job's own check found none of its secrets in the suite's output or in the results JSON, and the suite's scans clean; `PROFILE VERDICT: PASS`. A second profile run was refused (`refusing a used database`), every count unchanged (auth users, app accounts, profiles, setting versions, outbox events and idempotency records, `74 74 60 30 606 516` before and after). `sv2-profile-results` (4,326 bytes) was uploaded only after the check passed.
  - The container, its credential files and the marker files removed; no proof container remains.
- **No toolchain retry fired:** every "Wait 60 s before the one retry of the Python install (DM-41)" step, and every retry, was skipped.
- **No secret and no coordinate in the logs.** The Database proof checks job's whole log (2,094 lines), the API checks job's (2,143) and the Mobile checks job's (2,544) were each searched in full: none holds any coordinate the suite sends (`40.7123457`, `-74.0067891`, `34.0522342`, `-118.2436849`, nor their fractional digits). The only masked values are the checkout action's own token lines (three in each job), GitHub's token for the checkout, not one of the job's generated secrets. Those, the passwords, markers and keys the job generates, are what the suites' scans and the job's own check look for, and they found none.

### What could not run, and the limits

- **The mobile app's export and rendered checks** are CI's; `playwright install` was not run here.
- **The server's clock cannot be set:** the adult check runs at the database's UTC date; the leap-day boundaries (28 February and 1 March, P04's rule) are checked on the rule's own function, in the API's tests and the proof's case.
- **No verification company and no chart engine** exist: a case that needs `verified` or a resolved mapping seeds it in the disposable database as test data; no SV2 code writes either.
- **Not claimed:** the real target and its persistence; the deployed wiring; P07's staff API and P08's consent wording; SV3's candidate projection and two-way matching across members (only the rule's function and one-member reads are shown); a distance filter (one distance choice exists at launch).

### Decisions and deviations for the manager

1. **`orientation` launches with no values,** since OD-60 names none; until staff publish values, a member can only leave it not stated. The suite publishes its own test values.
2. **One distance choice, `anywhere`,** at launch; a radius needs a publication within the 5,000-mile limit.
3. **`AdultCheckIntent` and `OwnAgeState`** were added (the contract, above).
4. **Completion is the profile edit's transition** (P04's reviewed table: "Remains incomplete unless all current requirements permit completion"), so it happens on the owner's next profile edit once every requirement is met; resume rechecks it.
5. **The idempotency records' lifetime is 24 hours, provisional:** the contract leaves retention to A05 and the model requires a value.
6. **Completion requires the onboarding consent accepted at its current version.** Publishing a new version demotes no one by itself, but a `visible` member's next profile edit then finds consent missing and moves the profile to `incomplete` until they accept the new version; resume and the birth input need it too. The sensitive-fields consent's acceptance also names its current version.
7. **A birth input whose date fails the adult check is saved,** and the rerun then sets the age state to `unknown` and demotes the profile, as P04's `/birth` step does.
8. **`Profile.location_label` was removed** (D5). One sentence outside the owned rows still mentions location labels (`data-model.md`, "Identity, time and field semantics").
9. **`glow_domain/identity.py`'s import line** (`from datetime import date, datetime`) is outside its age section, which needs `date`.
10. **An integral JSON number is accepted as an integer,** as the contract's validators decide (the contract, above).
11. **The Database proof checks job:** the role-and-databases step's name now says three databases; the passfile has three lines; one Python block generates both JWT keys, each its own. The CI policy's Database proof checks paragraph (manager-owned) does not yet describe the SV2 steps.
12. **D16 does not apply:** `identity_support.py` is unchanged, so DM-50 1.2's docstring and pin stay carried.
13. **Profile restriction has no registry entry,** before and after SV2.

### Manager verification (App Manager 10, 10 November 2026)

**The diff.** `git diff a6624de f2635fa` was read for its scope, and in part for its content: 63 paths, each owned by the brief, revision 3: 58 to the code head `b97bc15`, and five Markdown files in the records commit `f2635fa`. About 12,200 lines are hand-written, excluding the generated contract outputs, the corpus, the area table and Markdown.
- `glow_api`, `glow_chat`, `scripts`, the runtime's `requirements.in` and `requirements.lock`, and every dependency lock are unchanged. No `apps/` path other than the three generated contract outputs changed.
- **The workflow:** every hunk is in the Database proof checks job. Its credentials step adds the third marker and `SECRET_KEY`, masked before anything prints, and a second RSA key from the same Python block; the new steps reuse the pinned `upload-artifact`.
- **The contract:** the schema and `openapi.json` gain definitions only, with no line removed. The registry's four removed lines are existing last elements gaining a trailing comma. `node scripts/generate.mjs --check` at `f2635fa`, after `npm ci --ignore-scripts`, printed `Generated types and runtime validators match schemas.`
- **D7:** `record` is unchanged. `transition` refuses outside a transaction and locks the account row, then the age state's row. The import line of `glow_domain/identity.py` gains `date` (the session's item 9).
- **The area table:** SHA-256 `2bf5e4da9e99…1138`, the value migration 0006 pins; 925 data rows and none in Puerto Rico.
- **Read against the brief:**
  - every route authenticates through SV1's actor class, refuses a query string and any body that is not its DTO, logs a reason code only, and sends `Cache-Control: no-store`;
  - the staff operations are module functions that no route imports;
  - completion runs only in the owner's name-and-summary edit (`operations.py`, the profile edit). No other writer attempts it (the session's item 4; DM-54).

**Classification.** The trusted classifier from `main` (`c864edd`), run with `python3 -I` and `--base c864edd… --head e0c0ffe… --merge-base` after the integration merge, returned:
- full scope, `behavior-or-empty`;
- the PR's whole diff, the manager's records since PR42 included;
- one merge base, `df8a04c`.

**Re-runs.** These ran in a scratch copy of the code head's whole tree (`git archive b97bc15`), in the clean environment, with hash-locked installs:
- **API:** `Ran 516 tests` … `OK`; Ruff clean; `131 files already formatted`; mypy `no issues found in 60 source files`.
- **mypy by hand** on `glow_profiles` and the seven new test modules: `no issues found in 24 source files`. The configured run's `files` is `glow_api`, `glow_domain`, `glow_chat`, `glow_identity`, so CI does not type-check `glow_profiles` (the session's item 10; DM-54).
- **The proof's offline tests:** `Ran 218 tests` … `OK`; Ruff clean; mypy `no issues found in 59 source files`.

The manager runs no database test locally.

**Reversals, re-run offline.** Each failed as it should:
- **R1:** `glow_api/urls.py` imports `glow_profiles.urls`. The sealed-runtime test module cannot load: `RuntimeError: Model class django.contrib.contenttypes.models.ContentType doesn't declare an explicit app_label and isn't in an application in INSTALLED_APPS.`
- **R1b:** `glow_api/urls.py` imports the pure `glow_domain.profile_fields`. `test_no_runtime_module_names_the_profile_slice` and `test_the_runtime_imports_none_of_the_profile_slice` fail (`FAILED (failures=2)`).
- **R2:** `operations.py` gets a logger and logs. `test_profiles_offline` fails (`FAILED (failures=1)`).
- **R3:** the stored digest becomes an unkeyed SHA-256. `test_profiles_offline` fails (`FAILED (failures=1)`).

Each file was restored and its hash checked against `b97bc15`, and the two test modules then pass (`Ran 14 tests` … `OK`).

**The run of record**, read with the GitHub tools: push run 42759801460 on `b97bc15`.
- All eight jobs `success`, and the gate printed `Application checks passed`. Every DM-41 retry step was `skipped`.
- The profile suite: `cases: 44/44 passed in 49.4 s`; `profile secret scan: clean (842 secrets held …)`; `profile value scan: clean (108 member values held …)`; `profile phase: 50 s`.
- The second profile run was refused, with the counts `74 74 60 30 606 516` unchanged.
- The artifact `sv2-profile-results` is 4,379 bytes, and the cleanup removed the container.

The records push run 42761123580 on `f2635fa` passed.

**What goes to the Dev Manager** (DM-54): the session's items 1 to 7, 10 and 13, and the stale sentence of item 8. Items 9, 11 and 12 are settled here: the import line is needed by the age section; the CI policy's paragraph is the manager's, updated in this batch; D16 did not apply, so DM-50 1.2 stays carried.

## Correction C1

Correction C1 of Stage A, to [DM-54](../../continuity/dev-manager/reviews/2026-11-10-dm-54-sv2-stage-a-decisions.md)'s words as the brief's revision 4 applies them ("Stage A, correction C1"; D7, D8, D9, D11's registry entries, checks 7 and 9). Local database runs here are iteration, not evidence; the evidence of record is the CI run on the code head, below.

### The session

- **The prompt:** [C1's correction prompt](https://github.com/amthorn78/glow-dating-app/blob/4dc2061a33c6f63e2887b11aeb2fd32d6224e23e/docs/ephemeral/2026-11-10-sv2-stage-a-c1-correction-prompt.md), revision 1, from `033e8d4cf2ef85bc2b05bfd6b5489852bd2e9fd3` of `claude/magical-wozniak-yfmmx2`.
- **The branch:** `claude/funny-lamport-5f2s1u`, started at `033e8d4`. Its name matches `claude/**`, so the Foundation workflow runs on its pushes.
- **The code commit, the code head:** `86a2156` (`86a215675e0ad826425e16c14fb6b826664b9c34`).
- **The records commit** (this section, and the data model's and the contract document's text) follows the run of record, as the push rule requires.

### Start gate and environment

- **The environment check, names only.** None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` was set, and no `STREAM_*` or `PG*` name (`compgen -e | grep -E '^(STREAM_|PG)'` printed nothing). The GitHub token names `GH_TOKEN` and `GITHUB_TOKEN` were present; they were never read. Every repository command ran in a clean process environment (`env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus `GLOW_ENV=test` for the API), with the proxy and CA variables passed by reference for the installs, never printed.
- **The toolchain:** `Python 3.12.14` (`python3.12`), Node `v24.19.0`, npm `11.9.0`, `Docker version 29.9.2, build a82e528`; `python3.12`, `node` and `npm` resolve to `$HOME/.local/bin`, second on `PATH` after `/nix/var/nix/profiles/default/bin`, as in Stage A.
- **The start gate,** each line as the prompt has it:
  - `git fetch origin claude/magical-wozniak-yfmmx2 main`: fetched;
  - `git switch -C claude/funny-lamport-5f2s1u 033e8d4…` and `git rev-parse HEAD`: `033e8d4cf2ef85bc2b05bfd6b5489852bd2e9fd3`;
  - no non-Markdown path under `.github`, `scripts`, `services`, `apps`, `packages` or `proofs` differs from `b97bc15`: printed nothing;
  - no owned path differs from the live manager branch: printed nothing. Its head was then `0612754`, whose only change after `033e8d4` is `docs/planning/sv2-profiles-media.md` (Codex's review of `033e8d4` recorded: two P1 findings, both this correction's items 1 and 3), and `033e8d4` is on it;
  - `grep -c -E '^#+ Correction C1'` on this record: `0`;
  - `grep -c 'requirements_met'` on `flows-v1.json`: `0`.

### Item 1 — D9's one recompute (Y3, Y5)

- **The change.** `services/api/glow_profiles/recompute.py` (new) holds the one shared function, `recompute(tx, account_id, now, *, writer)`, and its pure rule, `next_state`: an `incomplete` profile with nothing missing becomes `visible`, a `visible` profile with anything missing becomes `incomplete`, and `paused`, `restricted` and `removed` stay as they are. It reads the onboarding consent policy's pointer `FOR SHARE` and the profile `FOR UPDATE`, then every requirement (`requirements.missing`) on the current rows, all after the writer's account row lock. A change bumps the profile's version and the account's `eligibility_version` (the profile edit's own write already bumps both, and its change rides on it) and emits its event. The profile edit's own completion and demotion logic is now this call, and `_demote_if_visible` is gone: **nothing but the recompute writes a profile's state in SV2** (`glow_chat`'s pause, resume and restriction aside, and a new profile created `incomplete`).
- **Each writer that now ends with it, with the registry entry each change uses** (`flows-v1.json`, F04):

  | Writer | File | A completion | A demotion |
  |---|---|---|---|
  | the profile edit (`save_profile`) | `operations.py` | `complete` (`owner`), `profile_completed` | `edit` from `visible` to `incomplete` (`owner`), carried by the edit's own `profile_edited` |
  | the four fields (`set_field`) | `operations.py` | `complete` (`owner`), `profile_completed` | `requirement_removed` (`system`), `profile_demoted` |
  | the area (`set_area`) | `operations.py` | `complete` (`owner`), `profile_completed` | `requirement_removed` (`system`), `profile_demoted` |
  | the onboarding consent's accept and withdraw (`decide_onboarding_consent`) | `operations.py` | `requirements_met` (`system`), `profile_completed` | `requirement_removed`, `profile_demoted` |
  | the adult check (`adult_check`: the applied path and the unchanged-date path) | `operations.py` | `requirements_met`, `profile_completed` | `requirement_removed`, `profile_demoted` |
  | the birth input (`save_birth_input`, and its refused failing date, item 3) | `operations.py` | none in Stage A (a new revision is `pending`, so the chart is missing) | `requirement_removed`, `profile_demoted` |
  | staff's approval without ID verification (`approve_without_id`) | `staff.py` | `requirements_met`, `profile_completed` | `requirement_removed`, `profile_demoted` |
  | its revocation (`revoke_approval`) | `staff.py` | none (it removes a requirement) | `requirement_removed`, `profile_demoted` |

  The recompute runs on every path of these writers that is not a replay or a refusal, `no_change` included, so a requirement that lapsed without a write is found there too. It does not run in the operations that write no requirement: the "show me" sets, the filters, the phone-location query, the sensitive-fields consent, pause and resume (resume rechecks completion first, as before), restriction, publication and the reads.
- **A decision for the manager (C1-1): the demotion's entry in the fields and the area.** The brief names `complete` (`owner`) for a completion in an F04 owner command, and gives no entry for a demotion there. A field or area write can never itself remove a requirement (an emptying edit is refused, D9), so a demotion there is always a requirement found lapsed, such as a new consent version; it is recorded as `requirement_removed` (`system`) with `profile_demoted`. The profile edit's demotion keeps the owner's `edit`, as before C1, whether the summary was cleared or a requirement had lapsed.
- **Tests.**
  - API (`services/api/tests/test_profile_recompute.py`, new, no database): `RuleTests.test_the_rule_and_the_registry_entries` (the rule for every state with and without a missing requirement; the entry for each writer and change); `RuleTests.test_every_entry_the_recompute_names_is_in_the_registry` (`complete`, `requirements_met`, `edit` and `requirement_removed` each in F04 with its role, and `eligible` exactly on completion); `CallSiteTests.test_every_requirement_writer_ends_with_the_recompute` (each of the eight writers calls it, with its own kind of writer, directly or through its module helper; none of the other eight operations does); `CallSiteTests.test_only_the_recompute_writes_a_profiles_state`.
  - The profile suite (on the disposable database, through the routes):
    - `completion.every_requirement_writer_meeting_the_last_one_makes_it_visible`: the profile edit, a field (`looking_for`), a field that is no requirement (orientation, after the seeds met the last ones without a write), the area, the onboarding consent's accept, the adult check (after a failing rerun and the chart seeded again) and staff's approval each make an `incomplete` profile with only that requirement missing `visible`, each with one more `profile_completed`; the owner's completion read then lists nothing missing. The birth input is shown never completing (its new revision's chart is missing).
    - `completion.a_write_that_finds_a_requirement_missing_demotes`: a new onboarding consent version is published, and it alone moves no one; then an area change, a gender write and the adult check with its unchanged date each demote a `visible` profile with `profile_demoted`, and the profile edit demotes with its owner `edit` and no `profile_demoted`; accepting the new version completes a profile (`requirements_met`); a paused profile's area change leaves it `paused`; a restricted profile (through `glow_chat`'s writer) and a removed one (a harness write, since SV2 has no writer to `removed`) stay so through a consent withdrawal and acceptance.
    - **The existing lock case** `completion.takes_the_account_lock_first_and_sees_a_withdrawal` still shows a completion waiting on the withdrawal's account row lock and then seeing the withdrawal, and the other order.
- **Reversals** (each on its own new database; failing output from the harness):

  | Reversal | The temporary edit | Failing output |
  |---|---|---|
  | `C1.1-recompute-left-out-of-set_area` | `set_area`'s recompute call removed | proof: `FAIL completion.every_requirement_writer_meeting_the_last_one_makes_it_visible … FAILED: the area: the profile is visible`; `FAIL completion.a_write_that_finds_a_requirement_missing_demotes … FAILED: the area: the visible profile is demoted`; `cases: 45/47 passed`; `PROFILE VERDICT: FAIL`. API: `test_every_requirement_writer_ends_with_the_recompute (writer='set_area')`, `AssertionError: [] is not true : set_area does not recompute`, `FAILED (failures=1)` |
  | `C1.1-recompute-left-out-of-adult_check` | the adult check's applied-path recompute call removed | `FAIL adult.a_corrected_date_reruns_and_demotes … FAILED: the visible profile demoted`; `FAIL completion.removals_demote_and_empty_values_are_refused … FAILED: adult_rerun: demoted`; `FAIL completion.every_requirement_writer_meeting_the_last_one_makes_it_visible … FAILED: the adult check: incomplete first`; `cases: 44/47 passed` |
  | `C1.1-visible-with-the-chart-missing` | the recompute ignores a missing chart, so it makes a profile `visible` with one requirement missing | `FAIL completion.refuses_each_missing_requirement … FAILED: the chart: completion is refused`; `FAIL completion.needs_the_chart_and_identity_verification_seeded … FAILED: a new revision demotes`; `FAIL completion.removals_demote_and_empty_values_are_refused … FAILED: birth_input: demoted`; `FAIL completion.every_requirement_writer_meeting_the_last_one_makes_it_visible … FAILED: a birth input never completes`; `cases: 43/47 passed` |
  | `C1.1-recompute-changes-a-paused-profile` | the rule moves a `paused` profile with anything missing to `incomplete` | proof: `FAIL consent.withdrawal_on_a_paused_profile_stays_paused`, `FAIL visibility.resume_rechecks_completion`, `FAIL completion.removals_demote_and_empty_values_are_refused`, `FAIL completion.a_write_that_finds_a_requirement_missing_demotes … FAILED: a paused member's area change: answers 200`, `FAIL birth.a_failing_date_is_refused_and_nothing_of_it_is_stored`; `cases: 42/47 passed`. API: `RuleTests.test_the_rule_and_the_registry_entries`, `AssertionError: … 'incomplete' … != … 'paused' …`, `FAILED (failures=1)`. (Under the reversal, those routes answered other than 200; why was not investigated, since the reversal is seen either way.) |

### Item 2 — the registry entries (Y4)

- **The change** (`packages/contracts/production/flows-v1.json`, F04, appended after `requirement_removed`; no existing line removed or changed): `requirements_met` from `incomplete` to `visible` (`system`; `eligible: true`; `A05`); `restrict` from `visible` to `restricted` and from `paused` to `restricted` (`moderator`; `A05`). Both roles are ones `transition_contract.authorized` authorizes. No DTO changes, so no generated output changes (`npm run check`: `Generated types and runtime validators match schemas.`).
- **Tests** (`packages/contracts/tests/test_transition_contract.py`, `SV2StageATransitionTests`): `test_f04_requirements_met_is_the_systems_completion` (allowed for the system with eligibility and `A05`; forbidden for an owner, for a context with the owner role, and without eligibility; `policy_unresolved` without `A05`; `state_conflict` from `paused`; the owner's `complete` still allowed) and `test_f04_restrict_is_the_moderators` (allowed for a scoped moderator from `visible` and `paused`; forbidden for the owner and for another object; `policy_unresolved` without `A05`; `state_conflict` from `incomplete`, `restricted` and `removed`).
- **Reversal** `C1.2-requirements_met-role-unauthorized`: `requirements_met`'s role changed to `staff`, which the oracle never authorizes. `test_f04_requirements_met_is_the_systems_completion`: `AssertionError: 'forbidden' != 'allowed'`, `FAILED (failures=1)`.

### Item 3 — a birth input whose date fails the adult rule (Y6 to Y8)

- **The change** (`operations.py`: `save_birth_input` and the new `_refuse_failing_birth_input`; `_invalidate_birth_input` gains `whatever_its_date`). After the existing gates (the adult pass, the current onboarding consent, the expected version, a known time, no future date), a date that fails the adult rule (`adult_outcome` is not `PASS`; a future date keeps its earlier `invalid_request` refusal) takes this path:
  - **refused, with nothing of it stored:** no `BirthInput` revision is created, so its date, time and place are written nowhere; the mapping is not pointed at it; the age port is given `unknown` with no date; and no idempotency record is stored;
  - **its transaction commits the failing rerun:** the age state becomes `unknown` with no date, through the age port's `transition`, which bumps `eligibility_version` (`age_state_changed`); a current birth input, whatever its date, becomes `missing` with its mapping back to `pending` (`birth_input_invalidated`); and D9's recompute makes a `visible` profile `incomplete` (`profile_demoted`), while a `paused` one stays paused;
  - **the operation returns** `Result("refused", "forbidden", "birth_date_fails_adult_rule")` without raising, so `tx.run` commits; the route answers 403 with the contract's `Error`, naming the code only;
  - **a retry,** of the same command or a new one, finds no idempotency record and is refused at the adult-check gate (`adult_check_required`, 403 `forbidden`, raised, so rolled back), changing nothing more.
- **Tests.**
  - The profile suite: `birth.a_failing_date_is_refused_and_nothing_of_it_is_stored`, for a `visible` member and a `paused` one. After the refusal: no new revision; no `BirthInput` row holds the failing date, time or place; no table in the database holds its place or date (every row of every table read as JSON text); the actor's idempotency records unchanged; the age state `unknown` with no date and one more `age_state_changed`; the held revision `missing` with one more `birth_input_invalidated`; the mapping `pending`, its engine reference cleared, still pointing at that revision; the profile `incomplete` with one more `profile_demoted` (or `paused`, with none); `eligibility_version` bumped; the owner's reads show the held revision with `resolution: missing` and no date. A retry of the same command, and a new command, each answer 403 `forbidden`, and a snapshot of every row the case watches (revisions, the age state, the account's versions, the profile, the mapping, the outbox's count and the actor's idempotency records) is unchanged after each. The suite's value scan holds the failing input's date, time and place (`ValueLedger`) and finds none of them in any log record, write or the results JSON.
  - API: `CallSiteTests.test_the_failing_birth_input_returns_its_refusal` (the helper raises nothing, creates no revision, stores no record, recomputes, and returns the refusal).
- **Reversals:**

  | Reversal | The temporary edit | Failing output |
  |---|---|---|
  | `C1.3-revision-stored` | a revision is created before the refusal | `FAIL birth.a_failing_date_is_refused_and_nothing_of_it_is_stored … FAILED: no revision is written`; `cases: 46/47 passed`; `PROFILE VERDICT: FAIL` |
  | `C1.3-refusal-raised` | the refusal raised, so the rerun's effects roll back | `FAIL birth.a_failing_date_is_refused_and_nothing_of_it_is_stored … FAILED: the age state is unknown`; `cases: 46/47 passed` |
  | `C1.3-idempotency-record-stored` | an idempotency record stored with the refusal | `FAIL birth.a_failing_date_is_refused_and_nothing_of_it_is_stored … FAILED: no idempotency record is stored`; `cases: 46/47 passed` |

### Item 4 — CI's mypy (Y9)

- **The change:** `services/api/pyproject.toml`, `[tool.mypy]`'s `files` only: `["glow_api", "glow_domain", "glow_chat", "glow_identity", "glow_profiles"]`. The configured `mypy`: `Success: no issues found in 78 source files` (60 before; `glow_profiles` adds 18, `recompute.py` among them).
- **Reversal** `C1.4-type-error-in-glow_profiles`: `_REVERSAL: int = "not an int"` added to `glow_profiles/recompute.py`; the configured `mypy` (no argument): `glow_profiles/recompute.py:62: error: Incompatible types in assignment (expression has type "str", variable has type "int")  [assignment]`, `Found 1 error in 1 file (checked 78 source files)`, exit status 1.

### Item 5 — the data model's sentence (Y11)

`docs/architecture/data-model.md`, "Identity, time and field semantics": the sentence replaced with DM-54's words exactly ("An empty profile bio means incomplete or withheld text, not eligibility. `BirthInput.birth_date` and `local_time` preserve civil values; an unknown time is null, though SV2's server refuses a birth input without a time (OD-61)."); the paragraph's line breaks moved.

### Item 6 — the records

- `docs/architecture/data-model.md`, SV2's rows: `AccountAgeState` (a failing birth input refused, the rerun committed), `IdentityVerification` (both staff operations end with the recompute), `Profile` (the one recompute, its writers and its rule).
- `docs/architecture/production-contracts.md`, F02 to F06's server mapping: F02 (the writers that end with the recompute, `requirements_met`), F03 (the failing birth input), F04 ("What moves a profile to `visible`": the recompute, each change's entry and event), F06 (restriction's `restrict` entries).
- `packages/contracts/README.md`, SV2's section: the two entries. `proofs/postgres-ordering/README.md`, SV2's section: 47 cases, with C1's.
- This section.

### The threat model's inputs (C1)

- **The recompute's call sites and locks** (READ COMMITTED; DM-13 4.1). Each writer takes the account row `FOR UPDATE` first, as before, then its own rows; the recompute is its last state change, before its idempotency record, and reads the onboarding consent's pointer `FOR SHARE` (already held by the writers that read it earlier) and the profile `FOR UPDATE`, then the requirements' rows:
  - `save_profile`: the account; the catalog's and onboarding consent's pointers; the profile; the edit; then the recompute;
  - `set_field`: the account; the catalog's pointers; the profile; the field's row; the idempotency record; the write; then the recompute;
  - `set_area`: the account; the location pointer; the profile; the write; then the recompute;
  - `decide_onboarding_consent`: the account; the onboarding pointer; the profile; `glow_chat`'s nested writer; then the recompute;
  - `adult_check`: the account; the age state; the profile; the age port's transition; the current birth input and its mapping; then the recompute (on the unchanged-date path, the recompute alone);
  - `save_birth_input`: the account; the onboarding pointer; the age state; the current birth input; the profile; the new revision, the mapping, the age port's transition; then the recompute; on a failing date, the age port's transition, the current birth input and its mapping, then the recompute;
  - `approve_without_id`: the account; the staff approval setting's pointer `FOR SHARE`; the identity verification row; then the recompute (the onboarding pointer `FOR SHARE`, then the profile);
  - `revoke_approval`: the account; the profile; the identity verification row; then the recompute.

  Every SV2 writer of an account serializes on its account row, so the recompute's reads cannot interleave with another requirement writer of the same account. The pointers it reads are only `FOR SHARE`, which a publication's `FOR UPDATE` of one pointer waits on, and a publication takes no account row, so no cycle is added. Tests: `LockOrderTests` (each operation's first statement), `completion.takes_the_account_lock_first_and_sees_a_withdrawal` (both orders, each wait observed in `pg_locks`).
- **No path makes a profile `visible` with a requirement missing:** the recompute is the only SV2 code that writes a profile's state (`test_only_the_recompute_writes_a_profiles_state`), and it does so only with nothing missing (`next_state`); resume is `glow_chat`'s, after SV2's own recheck, unchanged. **None leaves one `visible` after a write that finds one missing:** every requirement writer ends with it (`test_every_requirement_writer_ends_with_the_recompute`; the suite's cases and the reversals above). A requirement that lapses without a write (a new consent version) stays unseen until the member's next requirement write (DM-54; K1 to K3 carried).
- **The failing birth input's path:** refused (403 `forbidden`, `birth_date_fails_adult_rule`); committed (the age state `unknown` with no date, the current revision `missing`, its mapping `pending`, a `visible` profile `incomplete`, and their three events, each carrying references only); stored: none of the input's values, no revision, no idempotency record, nothing in a log (the views log the reason code only). A retry is refused at the adult-check gate and changes nothing.

### Commands and results

**API** (`services/api`; `python3.12 -m venv .venv`, then `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`; each with `GLOW_ENV=test` in the clean environment), on the code head's tree:
- `python manage.py check`: `System check identified no issues (0 silenced).`
- `python manage.py test tests --verbosity 2`: `Ran 521 tests`, `OK` (516 before; `test_profile_recompute`'s 5 added).
- `ruff check .`: `All checks passed!`; `ruff format --check .`: `133 files already formatted`.
- `mypy`: `Success: no issues found in 78 source files`.
- `python smoke.py`: `PASS /health/live: HTTP 200`, `PASS /health/ready: HTTP 503`, `PASS /api/v1/development/recommendations: HTTP 200`.
- `python -m glow_persistence.static_check`: `Static definitions agree: 40 app models; migrations=0001_event_infrastructure,…,0007_settings_launch_defaults` (no migration added).

**The contracts:** from `services/api`, `PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests -v`: `Ran 47 tests`, `OK` (45 before). In `packages/contracts`, after `npm ci --ignore-scripts` (`found 0 vulnerabilities`) and `npm ci --ignore-scripts` in `apps/mobile`: `npm run check`: `Generated types and runtime validators match schemas.`, `tests 709`, `pass 709`, `fail 0`. No generated file changed (`git status` lists no `apps/` path).

**The mobile app** (`apps/mobile`): `npm run check`: `tsc --noEmit` and `eslint .` clean, `tests 691`, `pass 691`, `fail 0`; no change under `apps/`.

**The proof** (`proofs/postgres-ordering`; the same venv and hash-locked install, `pip check`: `No broken requirements found.`): `env -i … .venv/bin/python -m unittest discover -s tests -t . -v`: `Ran 218 tests`, `OK`; `ruff check .`: `All checks passed!`; `ruff format --check .`: `59 files already formatted`; `mypy`: `Success: no issues found in 59 source files`.

**Local database runs: iteration, not evidence** (P06.DB's D4). Docker's daemon was started in the sandbox; the CI job's image pinned by digest (`postgres@sha256:d74eeac9…`, PostgreSQL 17.11) was pulled once from Docker Hub and published on `127.0.0.1:5433` only; the passwords, markers and keys were generated into a directory only the session's user could read, and never printed; a non-superuser role owned each database, and each run had a new database with its own marker as its comment; none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or a `PG*` name was present; the container, its volume and the key files were removed afterwards.
- the profile suite on the code head's tree: `cases: 47/47 passed in 80.3 s`; `profile secret scan: clean (1040 secrets held; 0 found in 650 log records, 112 writes and the results JSON)`; `profile value scan: clean (133 member values held …; 0 found in the same output)`; `PROFILE VERDICT: PASS`;
- the seven database reversals, each on its own new database, above. A harness in the scratchpad applied each edit exactly once, ran the test, kept the failing lines, and restored the file byte for byte, its SHA-256 checked; `git status` showed only the correction's own changes afterwards.

### The run of record

**Foundation push run [42769301337](https://github.com/amthorn78/glow-dating-app/actions/runs/42769301337)** on `86a215675e0ad826425e16c14fb6b826664b9c34`, **the code head** (attempt 1, 06:33:26 to 06:43:24 UTC on 10 November 2026), read with the GitHub tools and the run's own log archive. Every job's conclusion was `success`, and the gate printed **`Application checks passed`**:

- **Change scope:** success; `{"full": true, "reason": "missing-or-invalid-comparison", "paths": []}`. A branch's first push has no earlier commit to compare with, so the trusted policy takes full scope; the change is full scope in any case.
- **API checks:** success. The scope and branch-cleanup policies' tests (`Ran 14 tests`, `Ran 18 tests`, `OK`); `System check identified no issues (0 silenced).`; `manage.py test tests --verbosity 2`: **`Ran 521 tests`**, `OK`; Ruff `All checks passed!`, `133 files already formatted`; **mypy: `Success: no issues found in 78 source files`**, `glow_profiles` now among them; the Python contract tests `Ran 47 tests`, `OK`, `test_f04_requirements_met_is_the_systems_completion` and `test_f04_restrict_is_the_moderators` among them.
- **Mobile checks:** success. The contracts' check (`Generated types and runtime validators match schemas.`; `tests 709`, `pass 709`); `npm run check` (`tests 691`, `pass 691`, with `tsc --noEmit` and `eslint .`); `check:expo`; `export:development`; the rendered checks, **`104 passed (5.3m)`**.
- **API mobile smoke, API artifact checks, Stream proof checks:** success.
- **Database proof checks:** success, in 9 minutes 40 seconds (06:33:36 to 06:43:16) of its 30-minute timeout.
  - The offline tests (`Ran 218 tests`, `OK`), Ruff, the format check and mypy (`Success: no issues found in 59 source files`).
  - A wrong marker refused (`wrong-marker migrate exit status: 1`) and `dbshell` refused (`dbshell exit status: 1`).
  - **The ordering suite:** `[reference] cases: 56/56 passed`, `[adapter] cases: 115/115 passed`, `[read] cases: 62/62 passed`, 0 oracle violations in either subject's rows, `== VERDICT: PASS ==`; a second run refused, every count unchanged.
  - **The identity suite:** the ordering database's marker refused; `[identity] cases: 49/49 passed in 44.5 s`; `identity secret scan: clean (754 secrets held; 0 found in 240 log records, 102 writes and the results JSON)`; `identity phase: 45 s`; a second identity run refused, every count unchanged (`53 53 63 32 50`).
  - **The profile suite:** the profile database refused both other markers (`exit status 1` each, with the marker's refusal); the migrations from zero and `No changes detected`; **`[profile] cases: 47/47 passed in 65.2 s`**, C1's three new cases among them; **`profile secret scan: clean (1040 secrets held; 0 found in 650 log records, 112 writes and the results JSON)`**; **`profile value scan: clean (133 member values held: coordinates, birth dates, times and places, own words, sensitive values; 0 found in the same output)`**; the job's own check: `the job's secrets found in the profile suite's output: 0`, `… in the profile results JSON: 0`, `the suite's own scans (secrets, member values) reported clean: True`; `PROFILE VERDICT: PASS`; **`profile phase: 65 s`**.
  - **The second profile run** was refused (`second profile run exit status: 1`; `refusing a used database: auth users exist; app accounts exist; outbox events exist; a setting was published beyond its launch default. The profile suite runs once per new database.`), with the counts of auth users, app accounts, profiles, setting versions, outbox events and idempotency records **`92 92 78 33 800 675` before and after**.
  - `sv2-profile-results` (4,676 bytes) uploaded only after the check passed; the container, its credential files and the marker files removed (`no proof container remains`).
- **No toolchain retry fired:** every "Wait 60 s before the one retry of the Python install (DM-41)" step, and every retry, was `skipped`.
- **No secret, coordinate or failing birth input value in the logs.** All eight jobs' logs (8,311 lines) were searched: none holds the coordinates the suite sends (`40.7123457`, `-74.0067891`), the failing input's place prefix (`Synthetic Failing Place`) or its time (`02:47:19`). The only masked values are the checkout action's own token lines.

### What could not run, and the limits

- **The mobile app's export and rendered checks** are CI's; `playwright install` was not run here.
- **The Database proof checks job's shell steps** were not rerun locally as a whole: C1 changes neither the workflow nor the steps, and the run of record ran them.
- **The server's clock cannot be set** (as in Stage A); the failing birth date is 17 years and about four months before the database's UTC date.
- **The birth input cannot meet the last requirement in Stage A:** its new revision is `pending`, and only P11's chart adapter resolves one, so its recompute is shown demoting, never completing. P11's chart and verification adapters and Stage B's photo approval will end with the same recompute (DM-54, K4); none exists yet.
- **A requirement that lapses without a write** (a new onboarding consent version) is seen only at the member's next requirement write, as DM-54 accepts for Stage A (K1 to K3 carried).
- **Not claimed:** the real target and its persistence; the deployed wiring; P07's staff API; SV3's discovery and SV4's messaging reads of a lapsed version.

### Decisions and deviations for the manager

1. **C1-1, the demotion's entry in the fields and the area** (above): `requirement_removed` (`system`), with `profile_demoted`, since those writes cannot themselves remove a requirement. The profile edit's demotion keeps the owner's `edit`, without `profile_demoted`, as before.
2. **C1-2, the recompute on `no_change` paths:** it also runs where a writer changes nothing (the adult check's unchanged date, an onboarding decision that repeats the last, an approval of an approved member), so a lapsed requirement is found at any requirement write, as Y3 says ("A requirement that lapses without a write … demotes at the member's next requirement write"). Replays and refusals do not run it.
3. **C1-3, a future birth date** keeps its earlier refusal (400 `invalid_request`, raised, so nothing changes, and the age state stays `self_declared_adult`); only a date under 18 takes the refused-and-rerun path. Y6 to Y8 speak of a date that fails "the adult rule"; the adult check's own step treats a future date as failing too, and its rerun on a `self_declared_adult` state sets `unknown`. Whether a future birth input date should also rerun is left to the manager; Stage A's threat model lists it among the birth input's 400 refusals.
4. **C1-4, the refusal's code:** the failing birth input answers 403 `forbidden` with the reason `birth_date_fails_adult_rule`, as the adult check's under-age refusal is `forbidden`. No contract code is added.
5. **C1-5, the staff approval's result** carries the profile's state after the recompute in its `detail` (`"profile"`), for P07's console and the suite; no DTO is involved.
6. **No stop rule was met:** no model, migration, DTO, generated output, `glow_chat`, `glow_identity`, `glow_api`, workflow, lock or dependency changed; no existing registry entry changed; both new roles are ones the oracle authorizes; and the Database proof checks job took 9 minutes 40 seconds.

### Manager verification of correction C1 (App Manager 10, 10 November 2026)

**The diff.** `git diff 033e8d4 f54545c` was read for scope, and in part for content: 14 paths, each one C1's brief section owns.
- 11 are code, to the code head `86a2156`. The other three are Markdown, in the records commits `baf8067` and `f54545c`.
- `glow_chat`, `glow_identity`, `glow_api`, the workflow, the models, the migrations, the schema, the generated contract outputs and every lock are unchanged.
- `pyproject.toml`'s one change adds `glow_profiles` to `[tool.mypy]`'s `files`.
- The registry gains three F04 entries and no line elsewhere: `requirements_met` (`system`) and two `restrict` (`moderator`).
- **Read against the brief:**
  - `glow_profiles/recompute.py` applies D9's rule;
  - `save_birth_input` returns `_refuse_failing_birth_input`'s refusal, not raising it, for an under-18 date: the age transition, the current revision to `missing` and the recompute commit, and no revision or idempotency record is written.

**Integration.** Merged at `6e5d0d1`; its non-Markdown paths are byte-identical to `86a2156`. The trusted classifier from `main` (`c864edd`) returned full scope (`behavior-or-empty`), with one merge base, `df8a04c`.

**Re-runs,** in a scratch copy of `86a2156` (`git archive`), in the clean environment, with hash-locked installs:
- **API:** `Ran 521 tests` … `OK`; Ruff clean; `133 files already formatted`; the configured mypy `no issues found in 78 source files`, now with `glow_profiles`.
- **Contract tests:** `Ran 47 tests` … `OK`.
- **The proof's offline tests:** `Ran 218 tests` … `OK`; Ruff clean; mypy `no issues found in 59 source files`.

The manager runs no database test locally.

**Two reversals, re-run offline.** Each failed as it should:
- **C1-R1:** `set_area`'s recompute call removed. `test_every_requirement_writer_ends_with_the_recompute` fails (`writer='set_area'`).
- **C1-R2:** a type error in `glow_profiles/recompute.py`. The configured mypy reports `Found 1 error in 1 file (checked 78 source files)`.

Each file was restored and its hash checked against `86a2156`.

**The run of record**, read with the GitHub tools: push run 42769301337 on `86a2156`.
- All eight jobs `success`, and the gate printed `Application checks passed`. Every DM-41 retry step was `skipped`.
- The second profile run was refused, with the counts `92 92 78 33 800 675` unchanged.
- The artifact `sv2-profile-results` is 4,676 bytes, and the cleanup removed the container.

**Codex.** Its review of `033e8d4` raised two P1 findings against the code before C1: the recompute missing from every writer but the profile edit, and a failing birth input stored. They are C1's items 1 and 3, and `86a2156` addresses both.
- **Codex on `40db2c2`** (the commit that holds the integration and the review prompt's revision 1): its code review completed at 13:11:55 UTC. It did not raise the two P1 findings again, and their threads are answered and resolved.
- **One new P2 finding** (`operations.py:1019`, "Commit the protective reset for future birth dates too"): a future birth date takes the 400 refusal before the committed reset, so an adult's state, a resolved birth input and a visible profile stay as they were. That is C1-3's point (below).
  - **Disposition:** under step 6 it joins the exact-head review's pass. The review prompt's revision 2 puts both readings in focus item 3; the manager does not decide between them.
  - Whether it is fixed follows the review's answer. If the words do not decide, it goes to the Dev Manager with the correction's scope. Its thread stays open until then.

**The session's decisions** (its "Decisions and deviations for the manager"):
- **C1-1:** a demotion found by a field or area write is `requirement_removed` (`system`), with `profile_demoted`. **Accepted, the manager on DM-54's words.** Y4 makes `requirement_removed` "the demotion that follows another write". A field or area write cannot empty a required value, since D9 refuses that, so any demotion there comes from a lapse.
  - **A note for the review and the Dev Manager:** a demotion inside the profile edit is always recorded as the owner's `edit`, even when the cause is a lapsed requirement rather than a cleared summary. Y4's words keep `edit` for "the owner's own edit that clears the summary".
- **C1-2:** the recompute also runs on writes that change nothing. **Accepted:** D9 says every writer ends with it.
- **C1-3:** a future birth date keeps its 400 refusal, with no rerun and no state change; only a date under 18 takes the refused-and-rerun path. **Accepted for the review, the manager's reading of DM-54's words, put to the Dev Manager at the pre-merge read.** Codex's P2 on `40db2c2` contests it (above): `adult_outcome` fails a future date, and the brief's acceptance item 7 counts one among the dates that fail. Both readings go to the review.
  - A future date fails D7's validity ("valid, not in the future"), not its age test: it is not a declaration of age (P04's `birthInputValid` refuses it: "Future dates are unavailable").
  - It is refused and stores nothing, which keeps "a failing date is refused and not stored".
- **C1-4:** 403 `forbidden`, with the reason `birth_date_fails_adult_rule`. **Accepted:** DM-54 section 8 gives `forbidden` as the public code.
- **C1-5:** the staff approval's result reports the profile's state after the recompute. **Accepted:** it is not a DTO.

**Codex on `9c5f6ee`** (the commit that holds the review prompt's revision 2): its code review completed at 13:23:29 UTC with no new finding. Its summary's "unresolved" state is the P2 thread at `operations.py:1019`, open until the review's answer on C1-3 is disposed.

## Exact-head review of Stage A (code head `86a2156`)

- **The session:** started by Nathan from the exact-head review prompt, revision 2, at `9c5f6eeadc1364c1484539ba23ddcbd42d19adde` (`docs/ephemeral/2026-11-10-sv2-stage-a-review-prompt.md`). It reported on 10 November 2026, and its report was relayed to App Manager 10.
- **The gates:**
  - the environment check passed: none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, `STREAM_*` or `PG*` was present, and the GitHub token names were never read;
  - the start gate passed, with one merge base, `df8a04c`, and no code after `86a2156`;
  - the trusted classification is `"full": true`, `behavior-or-empty`.
- **How it worked:** it read the core code itself, and six parallel reviewers covered the workflow and runs, the contract, the records, the Dev Manager's conditions and the tests. It confirmed every finding first-hand unless the finding is marked "(reviewer)".
- **What it ran:**
  - the API's checks: `manage.py check`; 521 tests `OK`; Ruff clean; mypy clean on 78 files;
  - the contract tests (47) and `generate.mjs --check`;
  - the proof's offline tests (218), Ruff and mypy;
  - the five required offline reversals, each failing its case. Its evidence reviewer re-ran 19 of the record's offline reversals at this head, and each failed as recorded;
  - the Census zip (46,177 bytes): both source hashes and the derived file's match;
  - informational, on a throwaway PostgreSQL under P06.DB's D4: the suite 47/47 in 75 s, and the twelve edits in the table below.
- **What it read:** runs 42759801460 (44/44), 42769301337 (47/47) and PR43's pull-request run 42823651738 on `9c5f6ee` (47/47). In each, all eight jobs passed, the gate printed `Application checks passed`, and no retry fired. Apart from finding 5's prose date, no secret or member value is in the logs.
- **The verdict: changes required, narrowly.** No finding is blocking. Eight findings fall in the correction classes (1 to 8), and four go to the Dev Manager with C1-3 (9, 10, 13 and 14).
- **Its statements:**
  - no path leaks a value, lets a member reach another member's object, acts unauthenticated, or makes a profile `visible` with a requirement missing;
  - no existing test was weakened. One expectation was widened by D7 (`AccountAgeState` now has `birth_date`);
  - none of the Dev Manager's conditions is plainly unmet. For a future date Y6 to Y8 are disputed; B8's history limit holds only for a direct change; Y4 is arguable;
  - all 68 existing contract definitions are unchanged. The 20 new ones are each closed and bounded. The 19 registry entries each use an authorized role, with an allowed and a forbidden example;
  - the workflow's diff, compared as parsed YAML, is confined to the Database proof checks job, and the CI policy's paragraph matches its steps;
  - every lock and manifest is unchanged;
  - every count in the records reproduces; the mismatches are finding 8.

**The database edits** (informational only):

| Edit | Suite result |
|---|---|
| A coordinate logged at `DEBUG` by the views' logger | Value scan `FOUND`, `PROFILE VERDICT: FAIL` |
| The failing birth input's refusal raised | `birth.a_failing_date…` fails, 46/47 |
| The recompute removed from revocation | 2 cases fail |
| The recompute removed from the birth input's accepted path | 2 cases fail |
| The unchanged-date recompute removed | 1 case fails |
| A queryset update forcing `visible` in `set_area` | 3 cases fail |
| Coordinates stored at four decimals | **Passes 47/47** |
| No account row lock | **Passes 47/47** |
| A withdrawn sensitive consent honoured | **Passes 47/47** |
| The future-date refusal removed | **Passes 47/47** |
| A birth date logged by `age.py` | **Passes 47/47** |
| An unkeyed digest for the birth input | **Passes 47/47** |

**The review's threat model**, as its report gives it (assets, actors and entry points are the prompt's):

| # | Threat | What stops it | What proves it | Gap |
|---|---|---|---|---|
| 1 | An anonymous prober, or a stolen token, on the 15 routes | `views._Route`: SV1's actor only (`views.py:41-56`); `tx.lock_account` rereads the account's state under its lock (`tx.py:157-166`) | `ownership.every_route_refuses_strangers_and_stale_versions` | The 401 is shown on 13 of 15 patterns; the session is read at authentication, not under the lock (SV1's design) |
| 2 | A member on another member's object | every operation takes the account from the actor; reads filter by it (`operations.py:185-264`) | the same case; `sets.start_at_all_and_stay_the_owners` | none found |
| 3 | A stale or replayed command | the expected version and keyed record in each operation; `idempotency.decide` | a stale version on all 10 command routes; `ownership.a_replay_and_a_conflicting_key` | none found |
| 4 | A publication crossing a fixed limit, or unaudited | `publication_refusals` before any write; `settings_store.publish` writes the version, pointer, `StaffAudit` and `policy_published` together | `FixedLimitTests`; `settings.fixed_limits_refused_before_any_write`; `settings.publication_writes_version_audit_event` | finding 1 |
| 5 | A sensitive field without its consent, or outliving withdrawal | `carries_sensitive` and `_sensitive_accepted` under the account lock; `_withdraw_sensitive_data` | `fields.sensitive_needs_consent`; `consent.sensitive_withdrawal_scope` | findings 4, 9 |
| 6 | One consent standing for the other; an old version accepted | `requirements.latest_decision(account, purpose)`; the version check under the pointer's lock | `consent.purposes_never_satisfy_or_revoke_each_other`; `consent.old_version_refused` | none found |
| 7 | Coordinates kept or echoed | `nearest_area` returns the area only and writes nothing; query strings refused | `area.nearest_query_changes_nothing`; `area.coordinates_never_kept_or_echoed`; `area.no_route_returns_a_distance`; the run's value scan | finding 5 |
| 8 | A birth input read by another, or an engine result invented | owner-only reads; no `EngineIdentity` created; no `resolved` written | `birth.submit_correct_change_write_private_revisions`; `birth.a_seeded_mapping_returns_to_pending`; `WritesTests` | none found |
| 9 | A member who declares a date under 18 | `adult_check`; `_refuse_failing_birth_input`; the `age_state_birth_date` check | `adult.failing_dates_are_refused_and_not_stored`; `adult.a_corrected_date_reruns_and_demotes`; `birth.a_failing_date_is_refused_and_nothing_of_it_is_stored` | findings 2, 13 |
| 10 | `visible` with a requirement missing, or left `visible` | `recompute.recompute` ends all eight writers; resume rechecks first | seven `completion.*` cases; `CallSiteTests` | a lapse without a write (DM-54 accepts it); findings 3, 7 |
| 11 | A member route reaching a staff operation | `views` and `urls` import no staff code; `_check_staff` | `test_no_view_reaches_a_staff_operation`; `staff.no_member_route_reaches_a_staff_operation` | name-based (nit) |
| 12 | Staff approval with the setting off, or standing in for more | the setting read `FOR SHARE` after the account lock; `requirements.missing` checks each requirement | `staff.approval_gated_narrow_survives_and_is_revocable` | none found |
| 13 | Seeded rows reaching the runtime | seeds in the proof package with `fixture:` values; the port refuses `record_check_passed` | `WritesTests`; `completion.needs_the_chart_and_identity_verification_seeded` | none found |
| 14 | Values in outbox events | `events.emit` takes IDs and a version only | `completion.each_change_emits_its_event`; the table search | finding 12 |
| 15 | Stored digests reversed | `idempotency.digest`: `salted_hmac`, SHA-256, a salt naming the operation | `KeyedDigestTests`; `digests.keyed_and_not_reproducible_without_the_key` | finding 6 |
| 16 | Values in logs or errors | only the views log, and a code only; `tx.run` reports exceptions by type | `NoValueInLogsTests`; `test_errors_validate_and_name_no_value`; the value scan | findings 5, 7, 11 |
| 17 | The served runtime importing SV2 | nothing in `glow_api` names it; the new domain modules are pure | `ProfilesSealedRuntimeTests` | contrived edits only |
| 18 | The area file changed or fetched | the pinned SHA-256 checked before load (migration `0006`) | `AreaTableTests`; `area.file_hash_and_925_areas` | none; re-derived byte for byte |
| 19 | Secrets or member values in public CI logs and artifacts | generated in the job, masked, mode 0600; `profile_scan` before output or upload | `ProfileScanTests`; `ProfileWorkflowTests`; three runs' logs | finding 5 |

**The review's findings and the manager's dispositions.** Under the manager workflow's step 6, "Fix or carry, by rule": rule (a) fixes a defect in a correction class before the merge, and the Dev Manager is consulted where a fix's design changes, where it touches a security boundary, a contract or an interface, or where the rule does not decide. The consultation is DM-55.

| # | Severity (class) | Finding | Disposition |
|---|---|---|---|
| 1 | should fix (a publication crosses a fixed limit) | The history setting's limit ("more readable needs new consent wording") is crossed in two publications with no new wording. The first changes only the setting's own label; the second makes a cause readable, naming the onboarding version members already accepted (`profile_settings.py:405-415`). Only the direct change is tested | **Fix in correction C2, after DM-55** (item 2): the fix's design is on a privacy boundary |
| 2 | should fix, after the Dev Manager rules (an account left an adult's; a condition unmet by the letter) | C1-3. The two writers disagree. From `self_declared_adult`, a future date at the eligibility step answers 200 and resets the account (P1), while at the birth input it answers 400 and changes nothing (P2). An under-18 date at the eligibility step answers 200 with a keyed record kept 24 hours (P5), while the birth input refuses it with no record. An under-18 birth input refused by an earlier gate (an unknown time, a stale version, a lapsed consent) skips the reset. No test pins a future-date behaviour. On the words: the letter leans to Codex, and DM-54's reasons (section 8: "a date under 18") and P04's rule lean to the session, so the words do not decide. Neither reading keeps anything of the refused input | **To the Dev Manager** (DM-55 item 1); fixed in C2 as ruled |
| 3 | should fix (a test passes where it should fail) | Nothing proves the account row lock: without `select_for_update` in `lock_account`, the 521 API tests and the 47 cases pass | **Fix in C2** (test-only), with its reversal |
| 4 | should fix (a sensitive field outliving withdrawal, through a test gap) | No case saves a sensitive field after a withdrawal: `_sensitive_accepted` reading "any accepted decision" passes everything | **Fix in C2** (test-only), with its reversal |
| 5 | should fix (a test passes where it should fail) | The scans and the table search match exact text only, and the static logging guard covers `glow_profiles` alone. Coordinates stored at four decimals pass, as does a birth date logged by `glow_identity/age.py`. The fixture's prose date "29 February 2008" is in the public log and artifact while the scan reports 0 (a fixture constant, not a member's value) | **Fix in C2** (test and scan only): the scans match each fixture value in every form the code could print, the guard covers `age.py`, and no case prints a fixture date in prose |
| 6 | should fix (a digest reproducible without the key, through a test gap) | The stored digest is checked for one command only; the birth input storing an unkeyed SHA-256 passes everything | **Fix in C2** (test-only): every command's stored digest |
| 7 | should fix, low (a static guard defeated by a plausible edit) | A profile state written by `.update(state=…)`, a recompute dropped from one branch, and a refusal reason built with `Result(…)` all leave the 521 API tests green. The suite catches the first two; the third is unguarded (reviewer) | **Fix in C2** (test-only): the static guards cover the first and the third |
| 8 | should fix (a record claims more than the code or runs show) | Eight claims: the contract document's F02 refusal sentence and F04 lapse sentence; the P11 plan's SV2 entry (still `b97bc15`, 44 of 44); the evidence record's "accepting the new version completes a profile" (an assertion that cannot fail), "Each writes a `StaffAudit` row" (only an `applied` outcome does), the scans' timing (once, after the last case), Stage A's 59 reversals (shown on `b97bc15` only), and three smaller ones (`glow_domain.identity`'s age section, 233 case rows, four records citing the brief's revision 3) | **Fix in C2.** The two contract sentences follow DM-55's rulings on items 1 and 4. Stage A's sections stand as written, and C2's record corrects them in its own section |
| 9 | should fix or carry (arguably an old consent version accepted) | The sensitive consent is not checked against its current version: accepted at `v2` with `v3` current, a field and a narrowed set both save (P7). No condition asks for it; K1 to K3 carry only the onboarding case | **To the Dev Manager** (DM-55 item 3) |
| 10 | should fix, for the Dev Manager (Y4, arguably) | C1-1. A lapse found by the profile edit is recorded as the owner's `edit`, with no `profile_demoted`, outside Y4's literal words ("the owner's own edit that clears the summary"). No event is removed, but SV3 must reread the state on `profile_edited`, and no record says so | **To the Dev Manager** (DM-55 item 4) |
| 11 | should fix (arguably a record claim: "every refusal is the contract's `Error`") | Three bodies do not answer 400: a 321-digit integer coordinate and 10,000 nested arrays answer 500 `text/html`, and U+0000 in a stored text answers 503 with `retryable: true`. No value is echoed | **Fix in C2**, in the manager's words (DM-55 item 6, for confirmation) |
| 12 | should fix or record | The sensitive withdrawal deletes field rows that earlier `profile_field_changed` events still name, and emits no field event, against the data model's rule that a payload reference "must target an existing owning record" | **To the Dev Manager** (DM-55 item 5) |
| 13 | for the Dev Manager ("keep any birth data of a self-declared minor", by the letter) | After a date under 18, earlier birth input revisions keep their date, time and place as `missing`, and the owner's read returns them. The code follows Y6's operative words; Y6's closing clause ("no birth data of a self-declared minor is kept") says more | **To the Dev Manager** (DM-55 item 1, with C1-3) |
| 14 | nit to should fix (W5's general sentence) | Re-acceptance at a new version from `accepted` is a transition both consent writers make and F02 lacks | **Fix in C2 under W5**, as two F02 entries (DM-55 item 6, for confirmation) |
| 15 | nits | Ten nits, two of them pre-existing | **In C2** (test-only): the sealed-runtime test asserts its `refused`, the scan's verdict reads its own line rather than the word "clean" anywhere, the suite's case count is pinned, the four registry prerequisites are pinned, and `age_years` (no caller) is removed. **Carried, after DM-55:** a revocation or restriction of a non-active account, and `publish` accepting a `system:` subject (P07); the adult check's missing upper bound (G-01, P07); a wrong method answering `invalid_request` with status 405 (the contract document's error table, in C2's record). **Pre-existing:** the CI policy's "both uploads" (there are four), corrected by the manager in this batch; `IdempotencyRecord` with no account foreign key (P11) |

**The review on the manager's readings:**
- **C1-1:** `requirement_removed` in a field or area write is within W5 and Y4, since those writes cannot remove a requirement themselves. The profile edit's lapse demotion recorded as `edit` is outside Y4's literal words (finding 10).
- **C1-3:** the words do not decide, so it goes to the Dev Manager. The firm finding is that the two writers disagree (finding 2). An impossible date is refused at parse on both routes, before any transaction.

**What the review could not run or read:**
- `npm run check` exactly as CI runs it: a contracts-only install lacks the mobile app's `ajv`. With the module path set, it passes 709 of 709;
- the mobile app's checks;
- most of Stage A's 46 database reversals;
- the ordering and identity suites locally;
- run 42758271326.

Nothing in the repository changed; `git status` was clean at `9c5f6ee`.

**DM-55's rulings** (answered at `f165861`, a read of `496c39e`; the review log, "DM-55"):
- **Finding 2 (C1-3):** option (b). A future date is invalid input at both writers, refused `invalid_request` with no change. A date under 18 from a self-declared adult is checked first at both writers, before their other refusals, and refused `forbidden` with no idempotency record while the reset commits. The manager's recommendation of (a) is withdrawn.
- **Finding 13:** erasing the earlier revisions is declined as worded and carried to P07 for G-01 (Z18). Until then they keep their contents, readable only by their owner and never current again. Y6's closing clause becomes a sentence that claims only what the code does (Z2).
- **Findings 1, 9, 10 and 12:** each approved as the manager recommended, 9 and 12 with conditions (Z6 to Z15).
- **Findings 11 and 14:** confirmed in the manager's words.
- **Finding 15:** confirmed, except that `age_years` stays and gets a test (Z16, Z17), and the 405 also goes to P11 (Z20).
- **C2's review:** a full exact-head review with a written threat model.

The brief's revision 5 holds the words, and its "Stage A, correction C2" section lists C2's items.

## Correction C2

Correction C2 of Stage A, to [DM-55](../../continuity/dev-manager/reviews/2026-11-10-dm-55-sv2-stage-a-review.md)'s words as the brief's revision 5 applies them ("Stage A, correction C2"; D2, D4, D6, D7, D8, D9, D11's registry entries, checks 1, 2, 6, 7 and 9), and to the exact-head review's findings as disposed above. Local database runs here are iteration, not evidence; the evidence of record is the CI run on the code head, below. Stage A's and C1's sections stand as written; this section corrects their claims where the review found them wrong (below, "The eight corrected claims").

### The session

- **The prompt:** [C2's correction prompt](https://github.com/amthorn78/glow-dating-app/blob/4dc2061a33c6f63e2887b11aeb2fd32d6224e23e/docs/ephemeral/2026-11-10-sv2-stage-a-c2-correction-prompt.md), revision 1, from `399c68d21d36cb477581587b62337c827196993f` of `claude/magical-wozniak-yfmmx2`.
- **The branch:** `claude/awesome-maxwell-wo9jxa`, started at `399c68d`. Its name matches `claude/**`, so the Foundation workflow runs on its pushes.
- **The code commit, the code head:** `01a3acb` (`01a3acb3d725e05d6e2d6a2d78f5e102db9e9f5a`).
- **The records commit** (this section; the data model's rows; the contract document's F02 to F04 sentences, index row and SV2 paragraph; the package README's and the proof README's SV2 sections; the P11 plan's "SV2 Stage A" entry) follows the run of record, as the push rule requires.

### Start gate and environment

- **The environment check, names only.** None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` was set, and no `STREAM_*` or `PG*` name (`compgen -e | grep -E '^(STREAM_|PG)'` printed nothing). `GH_TOKEN` and `GITHUB_TOKEN` were present and never read. Every repository command ran in a clean process environment (`env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus `GLOW_ENV=test` for the API); the installs passed the proxy and CA variables by reference, never printed.
- **The toolchain:** `Python 3.12.14` (`python3.12`), Node `v24.19.0`, npm `11.9.0`, all in `$HOME/.local/bin`, first on `PATH`; `Docker version 29.9.2, build a82e528`.
- **The start gate,** each line as the prompt has it:
  - `git fetch origin claude/magical-wozniak-yfmmx2 main`: fetched (`main` at `c864edd`; the manager branch at `399c68d` itself);
  - `git switch -C claude/awesome-maxwell-wo9jxa 399c68d…` and `git rev-parse HEAD`: `399c68d21d36cb477581587b62337c827196993f`;
  - no non-Markdown path under `.github`, `scripts`, `services`, `apps`, `packages` or `proofs` differs from `86a2156`: printed nothing;
  - no owned path differs from the live manager branch: printed nothing; `399c68d` is on it (it is its head);
  - `grep -c -E '^#+ Correction C2'` on this record: `0`;
  - `grep -c 'Stage A, correction C2 (DM-55)'` on the brief: `1`.

### Item 1 — a future date and a date under 18, at both writers (Z1 to Z4)

- **The change** (`services/api/glow_profiles/operations.py`).
  - **The eligibility step** (`adult_check`): after the account row lock, the age state's and the profile's locks, the clock, `age_state_missing` and the idempotency check (a replay or a key conflict), the date's outcome comes first, on both states and before the stale version check. A future date raises `invalid_request` (`adult_check:future`) and changes nothing. A date under 18 from an `unknown` account raises `forbidden` (`adult_check:under_age`) and changes nothing; from a self-declared adult it calls `_reset_failing_date` and **returns** `Result("refused", FORBIDDEN, ADULT_CHECK_UNDER_AGE)`, so `tx.run` commits the reset, and no idempotency record is stored. Only then the stale version, and a passing date's transition.
  - **The birth input** (`save_birth_input`): after the idempotency check and the adult-check gate (`adult_check_required` for an account that is not a self-declared adult), the date's outcome comes before the onboarding consent, the stale version and the birth time. A future date raises `invalid_request` (`birth_date_in_future`) and changes nothing; a date under 18 calls `_reset_failing_date` and returns `Result("refused", FORBIDDEN, BIRTH_DATE_FAILS_ADULT_RULE)`.
  - **One reset for both** (`_reset_failing_date`, replacing C1's `_refuse_failing_birth_input`): the age port's transition to `unknown` with no date (the date is never handed to the port; `age_state_changed`), the current birth input `missing` whatever its date with its mapping back to `pending` (`birth_input_invalidated`), and D9's recompute (`requirement_removed`, `profile_demoted`; a `paused` profile stays paused). It creates no revision and stores no record, and returns nothing; each writer returns its own refusal. `_age_transition` now takes passing dates only (anything else is `state_conflict`, `age:not_a_passing_date`, a branch no path reaches).
- **Tests.**
  - The profile suite, new: `adult.a_self_declared_adults_date_comes_first_at_both_writers`. A future date at the eligibility step and at the birth input, each from a visible self-declared adult: 400 `invalid_request`, and a snapshot of every row the case watches (the account's revisions, the age state, the account's versions, the profile, the mapping, the outbox's count and the actor's idempotency records) unchanged. A date under 18, each from a new visible member: at the eligibility step; there behind a stale version; at the birth input; there behind a stale version; behind a birth time not given; behind a lapsed onboarding consent (a new onboarding version published first). Each answers 403 `forbidden`; the age state becomes `unknown` with no date, the current birth input `missing` with its mapping `pending`, the profile `incomplete`, each with one more `age_state_changed`, `birth_input_invalidated` and `profile_demoted`; no revision is written; no idempotency record is stored; `eligibility_version` is bumped. A retry of the same command and a new command each answer 403 and change nothing. An `unknown` account: a future date (400) and a date under 18 (403) at the eligibility step change neither its state nor the outbox, and the birth input with either date is refused at its gate (403).
  - Changed to the new rule: `adult.a_corrected_date_reruns_and_demotes` (the corrected date under 18 now answers 403, not 200, with the reset read back through the owner's GET), and the failing reruns in `completion.refuses_each_missing_requirement`, `completion.removals_demote_and_empty_values_are_refused` and `completion.every_requirement_writer_meeting_the_last_one_makes_it_visible` (each now `ctx.refused(…, 403, "forbidden", …)`). `birth.a_failing_date_is_refused_and_nothing_of_it_is_stored` and `adult.failing_dates_are_refused_and_not_stored` are unchanged and pass.
  - API: `CallSiteTests.test_a_failing_date_returns_its_refusal_at_both_writers` (`test_profile_recompute.py`, replacing C1's `test_the_failing_birth_input_returns_its_refusal`): `_reset_failing_date` raises only the age port's own refusal, creates no revision, stores no record, recomputes and returns nothing; in each writer its call is followed at once by `return Result('refused', FORBIDDEN, <the writer's constant>)`.
- **Reversals** (each on its own new database, through the scratchpad's harness; failing output):

  | Reversal | The temporary edit | Failing output |
  |---|---|---|
  | `C2.1-date-after-stale-at-adult_check` | **at the eligibility step** (`adult_check`), the date's checks placed after the stale version check | `FAIL adult.a_self_declared_adults_date_comes_first_at_both_writers: FAILED: the eligibility step: the retry: answers 403` (the retry, which carries a stale version, answers 409) |
  | `C2.1-birth-date-after-the-consent` | at the birth input, the under-18 check placed after the onboarding consent's | `FAILED: the birth input behind a lapsed onboarding consent: the age state is unknown` |
  | `C2.1-future-resets-at-adult_check` | a future date from a self-declared adult resets the account at the eligibility step | `FAILED: the eligibility step: a future date changes nothing` |
  | `C2.1-record-stored-with-the-refusal` | an idempotency record stored with the eligibility step's refusal | `FAILED: the eligibility step: no idempotency record is stored` |
  | `C2.1-refusal-raised` | the eligibility step's refusal raised, so the reset rolls back | `FAIL adult.a_corrected_date_reruns_and_demotes: FAILED: unknown, the date cleared`; `FAIL adult.a_self_declared_adults_date_comes_first_at_both_writers: FAILED: the eligibility step: the age state is unknown` |

### Item 2 — the history setting's limit (Z6, Z7)

- **The change** (`services/api/glow_domain/profile_settings.py`, `_history_refusals`): a history publication that makes nothing more readable and names a consent version other than the one the current setting names is refused with **`MORE_READABLE_NEEDS_CONSENT`** (`more_readable_needs_consent_wording`), the existing code; no new code. The direct rule (a more readable change must name the onboarding consent's current version, which must differ from the version the current setting names) is unchanged. A refusal comes before anything is written (`settings_store.publish`).
- **Tests.** API: `FixedLimitTests.test_h_cannot_cross_its_limit_in_two_publications` (the label alone moved: refused; the second step, had the first applied: refused; a less readable change with the label kept, and no change: allowed). The profile suite, new: `settings.history_limit_not_crossed_in_two_publications`: with a cause hidden and a new onboarding version published, the first step (the label alone moves to it) is refused naming the limit and writes nothing (`_counts()` unchanged: versions, audit rows, events, pointers, records); the direct change (more readable under the version already named) is refused and writes nothing; a more readable change naming the new version applies.
- **Reversal** `C2.2-history-refusal-removed` (the new refusal disabled): API `FAIL: test_h_cannot_cross_its_limit_in_two_publications … AssertionError: Tuples differ: () != ('more_readable_needs_consent_wording',)`; suite `FAIL settings.history_limit_not_crossed_in_two_publications: FAILED: the label alone cannot move` (`settings.fixed_limits_refused_before_any_write` still passes: it tests the direct change only, as the review found).

### Item 3 — the sensitive-fields consent's current version (Z9, Z10)

- **The change** (`operations.py`): `set_field` and `set_preferences` read the catalog's settings and `consent.sensitive_profile` in **one** `settings_store.read_shared` call (`_catalog_and_sensitive_consent`), after the account row lock, every pointer `FOR SHARE` in name order (`consent.sensitive_profile` sorts before every `profile.*`). `_sensitive_accepted(account, current_version)` now requires the latest `sensitive_profile` decision to be `accepted` **at that version**. The refusal is unchanged: `forbidden`, `sensitive_consent_required`. The saves it gates are unchanged: a sensitive field's value, orientation's own words and a narrowed orientation or relationship status set. DM-55's section 5 consequence holds as the rule: `PreferencesIntent` carries all four sets, so a set narrowed under an older version blocks every preferences save until the member accepts the current version or puts it back to all.
- **Tests.** The profile suite, new: `fields.sensitive_needs_the_current_consent_version`. A sensitive value, orientation's own words and a narrowed relationship status set are each refused 403 `forbidden` before acceptance, after a withdrawal, and while the version accepted is an old one (a new sensitive consent version published); a gender value, a narrowed gender set and orientation left `not-stated` each succeed at the old version; after accepting the current version (F02's new `accept_sensitive` from `accepted`), each of the three succeeds. `fields.sensitive_needs_consent` (before acceptance) still passes.
- **Reversals:** `C2.3-version-ignored` (the version comparison removed): `FAIL fields.sensitive_needs_the_current_consent_version: FAILED: a sensitive value at an old version: answers 403`. `C2.3-any-accepted-decision` (any accepted decision at the current version, not the latest): `FAILED: a sensitive value after its withdrawal: answers 403`.

### Item 4 — a lapse the profile edit finds (Y4; Z12)

- **The change** (`services/api/glow_profiles/recompute.py`; `operations.save_profile`). `entry(writer, before, after, *, clears_summary=False)`: a demotion is the owner's `edit` only when the profile edit itself clears the summary (`clears_summary`: the profile's summary was not empty and the edit's is), whatever else is missing; every other demotion, the profile edit's included, is `requirement_removed`. `rides_on_the_edit` names the only changes that ride on the edit's own write (its `complete` and its owner `edit`); every other change bumps the profile's version and the account's `eligibility_version` and emits its event (`profile_demoted` for `requirement_removed`), as in every other writer. The display name cannot be cleared (D9: refused). `clears_summary` from another writer is a `ValueError`.
- **Tests.** API: `RuleTests.test_the_rule_and_the_registry_entries` (the profile edit's demotion without `clears_summary` is `requirement_removed`; with it, `edit`; `rides_on_the_edit` holds for the profile edit's `complete` and `edit` only; `clears_summary` from F04's owner writers or another flow is refused). The profile suite, new: `completion.the_profile_edit_is_the_owners_edit_only_when_it_clears_the_summary`: an edit that clears the summary demotes as `edit` (the profile's version and `eligibility_version` each +1, no `profile_demoted`, one `profile_edited`); after a new onboarding version, an edit that keeps the summary demotes as `requirement_removed` (each version +2, one `profile_demoted`); an edit that clears the summary while the consent has lapsed is `edit` (+1, no `profile_demoted`). Changed: `completion.a_write_that_finds_a_requirement_missing_demotes` now expects the profile edit's lapse demotion with `profile_demoted`.
- **Reversal** `C2.4-every-edit-demotion-is-edit` (every profile-edit demotion back to `edit`): API `FAIL: test_the_rule_and_the_registry_entries … AssertionError: {'pro[74 chars]e': 'edit', …} != {'pro[74 chars]e': 'requirement_removed', …}`; suite `FAIL completion.a_write_that_finds_a_requirement_missing_demotes: FAILED: the profile edit finding a lapse (requirement_removed): profile_demoted (requirement_removed)` and `FAIL completion.the_profile_edit_is_the_owners_edit_only_when_it_clears_the_summary: FAILED: a lapse the edit found: the profile's version bumped 2`.

### Item 5 — the withdrawal's field rows (Z13, Z14)

- **The change** (`operations._withdraw_sensitive_data`): the member's orientation and relationship status rows are locked `FOR UPDATE` in field order and each set to "not stated" in place: `value_ids` `["not-stated"]`, `own_words` null, `shown` false, `setting_version` unchanged, `version` +1, with `profile_field_changed` for it. A row that already holds `["not-stated"]` with no own words and its flag off is left as it is, with no event. The sets' reset to all and the deletion of the records of the commands that carried the two fields or their sets are unchanged.
- **Tests.** The profile suite, `consent.sensitive_withdrawal_scope`, extended: after the withdrawal both rows still exist, each `not-stated` with no own words and its flag off, its setting version kept, its version +1 and one more `profile_field_changed`; for a second member, a row set explicitly to `not-stated` with its flag off is unchanged (values, own words, flag, version and `updated_at`) with no event, while the other row is reset with its event; every `profile_field_changed` event of the run names an existing row.
- **Reversals:** `C2.5-rows-deleted`: `FAILED: orientation: the row still exists`. `C2.5-flag-kept`: `FAILED: orientation: no own words, flag off`. `C2.5-event-for-an-unchanged-row`: emitting `profile_field_changed` for the unchanged row at its own version is refused by the outbox's `dedup_key`, so the withdrawal fails (`FAILED: withdrawn: answers 200`); emitted at another version (`C2.5-event-for-an-unchanged-row-new-version`), the case's own check fails: `FAILED: with no event`.

### Item 6 — bodies that must answer 400

- **The change.** `glow_profiles/contract.py`: `number` compares an integer exactly and checks finiteness for floats only, so a 321-digit integer is out of range, not an `OverflowError`; `parse` maps `RecursionError` (nesting deeper than the parser allows) to `Invalid`, beside `UnicodeDecodeError` and `ValueError` (which already covers an integer longer than Python's digit limit). `glow_domain/profile_fields.py`: `text_ok` refuses a text holding U+0000, so every stored text (display name, summary, own words, place label, time zone and its provenance) refuses it at parse. Each is `invalid_request` (400) with the contract's `Error`, through the views' `_BadRequest`; nothing is echoed. The contract's validators accept U+0000; the server's stricter rule is recorded in `contract.py`'s docstring, and the corpus parity tests still pass.
- **Tests** (API, offline): `BodiesTheParserCannotHoldTests.test_each_answers_400_with_the_contracts_error_and_no_value`, through each route's own view with the actor forced and every body within the 16 KiB request limit (so the parser, not the limit, decides): a coordinate given as a 321-digit integer; 10,000 nested arrays as the parser meets them (10,000 opening brackets); 5,000 closed nested arrays; U+0000 in a display name. Each answers 400, `application/json`, exactly the `Error`'s four fields with `code: invalid_request` and `retryable: false`, and no part of the body.
- **Reversals:** `C2.6-integer-guard-removed`: the view raises `OverflowError: int too large to convert to float` (uncaught, a 500 in a server), `FAILED (failures=1)`. `C2.6-nesting-guard-removed`: `RecursionError: maximum recursion depth exceeded while decoding a JSON array from a unicode string`, `FAILED (failures=1)`. `C2.6-u0000-guard-removed`: `(case='u0000_in_a_stored_text') AssertionError: 503 != 400`. **A deviation on the way:** the first form of the nesting case, 10,000 closed arrays (20 KB), passed with the guard removed, because the 16 KiB request limit refused it before the parser; the case was changed to bodies under the limit, and the reversal then failed as above.

### Item 7 — two F02 entries under W5

- **The change** (`packages/contracts/production/flows-v1.json`, F02, each inserted after its event's `withdrawn` entry; no existing line changed: `git diff` shows 22 lines added and none removed): `accept` from `accepted` to `accepted` and `accept_sensitive` from `accepted` to `accepted`, each `owner`, `eligible: false`, policies `["consent_current"]`, `active_match: false`. `owner` is a role `transition_contract.authorized` authorizes. No DTO changes, so no generated output changes.
- **Tests** (`packages/contracts/tests/test_transition_contract.py`, `SV2StageATransitionTests.test_f02_reacceptance_at_a_newer_version`): for each event, allowed with `consent_current` (the current version, newer than the one accepted); an old version (no `consent_current`) is `policy_unresolved`; another owner and the system are `forbidden`. The oracle answers an old version `policy_unresolved`, not `forbidden`: the refused example is that outcome.
- **Reversal** `C2.7-role-unauthorized` (`accept_sensitive`'s new entry's role changed to `staff`, which the oracle never authorizes): `FAIL: test_f02_reacceptance_at_a_newer_version (… event='accept_sensitive') AssertionError: 'forbidden' != 'allowed'`, `FAILED (failures=1)`.

### Item 8 — the test gaps (findings 3, 5, 6 and 7)

- **The account row lock** (finding 3). The profile suite, new: `completion.a_second_writer_waits_for_the_account_row_lock`. Two SV2 writers of one account whose own rows are disjoint: `set_filters` (the preferences) holds its transaction before its commit; `set_area` (the profile) arrives with a probe on `after_first_lock`. The case observes the second waiting on the first's lock (`pg_stat_activity`, `pg_blocking_pids`), checks that while it waits it has not passed its first lock (the probe has not fired) and holds no lock on its own profile row (a third connection takes it `FOR UPDATE NOWAIT`), then that both apply in order. **Reversal** `C2.8-no-account-row-lock` (`lock_account` without `select_for_update`): `FAIL completion.a_second_writer_waits_for_the_account_row_lock: FAILED: it waited at the account row, before passing its first lock` (the writer passes its first lock and later waits on the account row's update); `completion.takes_the_account_lock_first_and_sees_a_withdrawal` still passes, as the review found.
- **The scans and the table search** (finding 5).
  - `profile_support.forms(value)`: every form the code could print a value in: as sent and as JSON escapes it; a date also as `date(Y, M, D)` (Python's `repr`), compact (`20080229`), numeric (`29/02/2008`, `02/29/2008`, `29.2.2008`) and in prose (`29 February 2008`, `29 February 2008` with a leading zero, `February 29, 2008`); a time as `time(H, M, S)`; a coordinate also without its sign, and rounded and truncated to every lower precision down to three decimals (about 110 metres, finer than the state laws' 1,750 and 1,850 feet). `ValueLedger` holds each value with its forms and counts a value found when any form is found; `_found_in_database` searches every row of every table for every form. The area table's internal points hold none of the suite's coordinates' forms at three decimals or more (checked against the committed table).
  - **The fixture date in prose:** `adult.eighteen_today_and_the_leap_days_pass`'s detail line printed "29 February 2008" into the suite's output, which is the job's public log and the results artifact; it now says "the leap-day date". No case's detail prints a date.
  - **The static logging guard** covers `glow_identity/age.py`: `NoValueInLogsTests.test_the_age_port_logs_and_prints_nothing` (no logging or warnings import, no `logger`, `logging`, `log` or `print` name, no `getLogger`, `warning` or `debug` attribute, no import by name).
  - **Reversals:** `C2.8-coordinates-at-four-decimals` (the phone-location query writes the coordinates at four decimals into the profile's summary): `FAIL area.coordinates_never_kept_or_echoed: FAILED: no table holds the coordinates (outbox and idempotency records included)`. `C2.8-age-py-logs-a-birth-date` (a temporary edit of `age.py`: `transition` logs `change.birth_date` with `%r` at DEBUG): API `FAIL: test_the_age_port_logs_and_prints_nothing … ['85 reaches debug', '85 reaches getLogger', '85 imports by name'] != []`; the full suite `profile value scan: FOUND (163 member values held: …; 11 found in the same output)`, `PROFILE VERDICT: FAIL` (53 of 53 cases passed: only the scan sees it). `age.py` was restored byte for byte (SHA-256 checked) and is unchanged at the code head (`git diff 399c68d 01a3acb -- services/api/glow_identity` is empty).
  - Offline: `ValueLedgerTests.test_every_form_the_code_could_print_is_found` (each form found; two decimals, another date and another time not).
- **Every command's stored digest** (finding 6). `ProfileContext.remember` keeps, by actor and key, the first intent of every command that committed (each 200 through a route, and the cases' direct calls); the digests case now checks **every** `IdempotencyRecord` the run left against its own command: 64 characters, not the unkeyed SHA-256 of its canonical intent, and equal to `salted_hmac(SALT_PREFIX + <its operation>, <its canonical intent>, secret=SECRET_KEY, algorithm="sha256")`; and the records cover all ten kinds of command (`profile`, `profile_field`, `preferences`, `filters`, `area`, `consent`, `sensitive_consent`, `adult_check`, `birth_input`, `visibility`). Locally: 802 records checked. **Reversal** `C2.8-birth-input-unkeyed-sha256` (the birth input storing an unkeyed SHA-256): the full suite `FAIL digests.keyed_and_not_reproducible_without_the_key … FAILED: birth_input: not the unkeyed SHA-256`, `cases: 52/53`.
- **The static guards** (finding 7). `CallSiteTests.test_only_the_recompute_writes_a_profiles_state` also forbids any `.update(...)` call on a queryset naming `Profile` with a `state` keyword (or `**`) in `glow_profiles`. `NoValueInLogsTests.test_every_refusal_reason_is_a_code` now checks `Result(…)` as well as `Refused(…)`: a reason is a whole code (`[a-z_]+(:[a-z_]+)?`, or `DeadlockDetected`, matched in full, where it was searched before), a module constant holding one, or a closed interpolation; a `Result` whose outcome is not a literal carries no reason (90 sites checked; at least 60 required). **Reversals:** `C2.8-queryset-update-of-a-profiles-state` (`Profile.objects.filter(…).update(state="visible")` in `set_area`): `FAIL: test_only_the_recompute_writes_a_profiles_state … [('operations.py', 643)] != []`. `C2.8-result-reason-from-a-value` (`return Result("refused", INVALID_REQUEST, str(intent["value_ids"]))` in `set_field`): `FAIL: test_every_refusal_reason_is_a_code (module='operations.py', line=423) AssertionError: "str(intent['value_ids'])" not found in {…}`.

### Item 9 — finding 15's test items

- **The sealed runtime** (`test_profiles_sealed_runtime.py`): the runtime script now prints the `refused` it computes, and the test asserts `ImproperlyConfigured` (the dummy backend refuses a connection). **Reversal** `C2.9-sealed-refused-not-computed` (the script's `except` branch sets `refused = None`): `AssertionError: None != 'ImproperlyConfigured'`.
- **The scan's verdict** (`profile_scan.py`): `suite_reported_clean` reads the suite's own result line for each scan: exactly one line starting `profile secret scan: ` and one starting `profile value scan: `, each matched in full as clean with `0 found`; the word "clean" elsewhere counts for nothing. Offline: `ProfileScanTests.test_the_verdict_reads_the_suites_own_result_lines` (a FOUND line beside "clean" words in a case's detail; a value FOUND line; a clean line that found some; a clean line twice; a clean line not at a line's start: each refused, the JSON removed). The module may import `re` (standard library). **Reversal** `C2.9-scan-reads-clean-anywhere` (the old substring check): four of the five logs pass where they must be refused, `AssertionError: 0 != 3`, `FAILED (failures=4)`.
- **The case count** is pinned: `profile_cases.CASE_COUNT = 53` (47 after C1, and C2's six new cases); `profile_suite.run` refuses before any case when the suite holds another number; `ProfilePlanTests.test_the_case_count_is_pinned`. **Reversal** `C2.9-a-case-dropped` (one case's `@case` removed): `AssertionError: 52 != 53`.
- **The registry prerequisites.** SV2 added **one** name to the contract document's list of trusted test prerequisites, `staff_approval`; SV2's entries require **four** prerequisites in all: `consent_current`, `A05`, `staff_approval` and eligibility (`requirements_met`'s `eligible`). `test_sv2_registry_prerequisites_are_pinned` pins each of SV2's 21 entries' policies and eligibility exactly, the set of trusted prerequisites the registry uses (the policies not named `A…`), and that set against the backticked names in the contract document's sentence. **Reversals:** `C2.9-prerequisite-dropped` (`staff_approval` removed from `approve_without_id`): `FAIL: test_f02_identity_verification_and_staff_approval … 'allowed' != 'policy_unresolved'` and `FAIL: test_sv2_registry_prerequisites_are_pinned`; `C2.9-prerequisite-unlisted` (`staff_approval` unbackticked in the document): `FAIL: test_sv2_registry_prerequisites_are_pinned … Items in the second set but not the first`.
- **`age_years`** (Z16, Z17): the profile suite, new: `adult.age_years_is_whole_years_never_the_date`, on the age port (`OrmAgeAssurance().age_years`) after the route's adult checks: `None` while `unknown`; 29, 30 and 18 for dates 30 years less a day, 30 years and 18 years ago; each an `int` and never a `date`. **Reversal** `C2.8-age_years-returns-the-date` (a temporary edit of `age.py`: `return born`): `FAIL adult.age_years_is_whole_years_never_the_date: FAILED: an integer, never the date`; `age.py` restored byte for byte and unchanged at the code head.

### Item 10 — the records, and the eight corrected claims (finding 8)

**The eight claims,** each with the true statement:
1. **The contract document's F02 refusal sentence** ("under 18 is `forbidden` and a future date `invalid_request`, and neither is stored") left out the reset and the order. True: the date's outcome comes first; a future date is `invalid_request` and changes nothing; a date under 18 is `forbidden`, not stored, and from a self-declared adult also commits the failing rerun with no idempotency record. The sentence is rewritten so.
2. **The contract document's F04 lapse sentence** ("the owner's own profile edit that removes one keeps `edit`") described a lapse found by the profile edit as `edit`. True since C2: only the edit that clears the summary itself is `edit`; any other demotion is `requirement_removed`, with its own bumps and `profile_demoted`. Rewritten.
3. **The P11 plan's "SV2 Stage A" entry** named Stage A's run (`b97bc15`, 44 of 44) only. True: C1's run of record is 42769301337 on `86a2156` (47 of 47), and C2's is below. The entry now names C2's run of record.
4. **"Accepting the new version completes a profile"** (C1's section, `completion.a_write_that_finds_a_requirement_missing_demotes`) was an assertion that could not fail: the member was never demoted, so it was `visible` before the acceptance. True at C1's head: it showed only that the acceptance left a visible profile visible. Since C2 the case demotes that member first (an area change while the consent has lapsed) and then shows the acceptance completing it, with one more `profile_completed`.
5. **"Each writes a `StaffAudit` row in its transaction"** (Stage A's threat model, "Every staff operation"): only an `applied` outcome writes one. A `no_change` or a refusal writes none (`staff.py`'s `_audited` runs only on `applied`).
6. **The scans' timing:** the suite's secret and value scans run **once, after the last case** (`profile_suite.run`), over everything captured during the run, not after each case. The section comment in `profile_cases.py` ("the scans run after every case") still says otherwise; it is a code comment, left for the next code change (see the deviations).
7. **Stage A's 59 reversals** were each shown on `b97bc15` or before; none was re-run at C1's head, and C1 recorded its own. They are not evidence for a later head. C2's reversals above are shown on C2's tree.
8. **Three smaller ones:**
   - Stage A's Outcome table gives `glow_domain/identity.py` as "(the age section)": SV2 also changed the module's `datetime` import line (`date`), outside that section, as Stage A's decision 9 says;
   - Stage A's run of record gives "234 case rows" for the ordering suite: there are 233 (`56` + `115` + `62`);
   - four owned records cited the brief's revision 3 for SV2 (the contract document's SV2 paragraph, the package README's SV2 section, the proof README's SV2 paragraph and the P11 plan's entry): each now cites revision 5.

**The 405** (carried to P11 by DM-55's Z20): a wrong method on an SV2 route answers `invalid_request` with status **405** (`views.handle_exception`, `MethodNotAllowed`), while the contract document's error table gives `invalid_request` 400 only. Unchanged in C2; P11 either adds 405 to the table or answers 400.

**The other records:**
- `docs/architecture/data-model.md`: the `AccountAgeState` row (items 1 and the earlier revisions kept); the `Profile`/`ProfileFieldChoice` row (the sensitive saves' current version, item 3; the withdrawal in place, item 5; each change its own entry, only the summary-clearing edit `edit`, item 4).
- `docs/architecture/production-contracts.md`: the F02 index row (the re-acceptance entries); the SV2 paragraph (revision 5; the 400 bodies); F02's, F03's and F04's server mapping (items 1, 3, 4, 5 and 7).
- `packages/contracts/README.md`, SV2's section: revision 5; C2's two entries and the prerequisites' pin. `proofs/postgres-ordering/README.md`, SV2's paragraph: revision 5; 53 cases, the count pinned; C2's forms, cases and the scan's own lines.
- `docs/testing/p11-deferred-acceptance.md`, the "SV2 Stage A" entry only: revision 5, and C1's and C2's runs of record.

### The threat model's inputs (C2)

- **The order of each age writer's checks** (READ COMMITTED; DM-13 4.1):
  - **the eligibility step** (`adult_check`): the account row `FOR UPDATE`; the age state `FOR UPDATE`; the profile `FOR UPDATE`; the clock; `age_state_missing`; the idempotency check (replay, `idempotency_conflict`); **the date**: future → `invalid_request` (raised: nothing changes), under 18 → from `unknown` `forbidden` (raised), from `self_declared_adult` the reset and a returned `forbidden`; then the stale version; then the passing date's transition, the birth input's invalidation for another date, and the recompute; the record;
  - **the birth input** (`save_birth_input`): the account row; the onboarding consent pointer `FOR SHARE`; the age state; the current revision; the profile; the clock; the idempotency check; **the adult-check gate** (`adult_check_required`, raised); **the date**: future → `invalid_request` (raised), under 18 → the reset and a returned `forbidden`; then the onboarding consent (`onboarding_consent_required`), the stale version, the birth time (`birth_time_required`); then the revision, the mapping, the age date if another, the recompute; the record.
- **What each refusal commits and stores:** every raised refusal rolls the whole transaction back and stores nothing. The two returned `forbidden` refusals commit only the reset: the age state `unknown` with no date (`age_state_changed`), the current revision `missing` and its mapping `pending` (`birth_input_invalidated`), and the recompute's demotion (`requirement_removed`, `profile_demoted`, the two versions bumped); no revision, no date, time or place, no idempotency record, and nothing in a log (the views log the reason code only). Each event carries references only.
- **The sensitive saves' consent read and its lock order:** `set_field` and `set_preferences`: the account row `FOR UPDATE`; then one `read_shared` over `consent.sensitive_profile` and the seven catalog settings, each pointer `FOR SHARE` in name order (`consent.sensitive_profile`, then `profile.age_range`, `profile.gender`, `profile.location`, `profile.looking_for`, `profile.narrowing`, `profile.orientation`, `profile.relationship_status`); then the profile and the field row, or the preferences, `FOR UPDATE`. A publication takes one pointer `FOR UPDATE` and no account row, so no cycle is added; the save reads the consent's version before or after a publication, never a mix. The decision itself is read after the lock (`requirements.latest_decision`, purpose `sensitive_profile` only).
- **The withdrawal's rows and events:** in the withdrawal's transaction, after the account row and the preferences: the decision (`sensitive_consent_withdrawn`); each of the two field rows `FOR UPDATE`, set to "not stated" in place with `profile_field_changed`, or left alone with no event; the two sets back to all with `preferences_changed`; the records of `profile_field.orientation`, `profile_field.relationship_status` and `preferences` deleted. Every `profile_field_changed` event of the run names an existing row.
- **The parse refusals:** a body that is not UTF-8, not JSON, a non-finite constant, deeper than the parser allows (`RecursionError`), an integer longer than Python's digit limit (`ValueError`), an integer coordinate out of range however long (compared exactly), or a stored text holding U+0000, is `invalid_request` (400) with the contract's `Error`, before any transaction; the refusal names the definition or the field's path, never a value. A body over 16 KiB is refused first by the request limit (`RequestDataTooBig`, 400).

### Commands and results

**API** (`services/api`; `python3.12 -m venv .venv`, then `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`; each with `GLOW_ENV=test` in the clean environment), on the code head's tree:
- `python manage.py check`: `System check identified no issues (0 silenced).`
- `python manage.py test tests --verbosity 2`: `Ran 524 tests`, `OK` (521 before: three added, the age port's logging guard, the 400 bodies and the history limit's two steps; C1's failing-birth-input test replaced by the two-writer one).
- `ruff check .`: `All checks passed!`; `ruff format --check .`: `133 files already formatted`.
- `mypy`: `Success: no issues found in 78 source files`.
- `python smoke.py`: `PASS /health/live: HTTP 200`, `PASS /health/ready: HTTP 503`, `PASS /api/v1/development/recommendations: HTTP 200`.
- `python -m glow_persistence.static_check`: `Static definitions agree: 40 app models; migrations=0001_event_infrastructure,…,0007_settings_launch_defaults` (no migration added).

**The contracts:** from `services/api`, `PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests -v`: `Ran 49 tests`, `OK` (47 before). In `packages/contracts`, after `npm ci --ignore-scripts` there and in `apps/mobile` (`found 0 vulnerabilities`): `npm run check`: `Generated types and runtime validators match schemas.`, `tests 709`, `pass 709`, `fail 0`. No generated file changed (`git status` lists no `apps/` path).

**The mobile app** (`apps/mobile`): `npm run check`: exit 0, `tests 691`, `pass 691`, `fail 0`.

**The proof** (`proofs/postgres-ordering`; the same venv and hash-locked install, `pip check`: `No broken requirements found.`): `python -m unittest discover -s tests -t . -v`: `Ran 221 tests`, `OK` (218 before); `ruff check .`: `All checks passed!`; `ruff format --check .`: `59 files already formatted`; `mypy`: `Success: no issues found in 59 source files`.

**Local database runs: iteration, not evidence** (P06.DB's D4). Docker's daemon was started in the sandbox; the CI job's image pinned by digest (`postgres@sha256:d74eeac9…`, PostgreSQL 17.11) was pulled once from Docker Hub and published on `127.0.0.1:5433` only; the superuser's and the role's passwords, each database's marker, the `SECRET_KEY` and the JWT key were generated into a directory only the session's user could read, and never printed; a non-superuser role owned each database, each with its own marker as its comment; none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or a `PG*` name was present; the container, its volume and the key directory were removed afterwards (`docker ps -a` lists none).
- the profile suite on the code head's tree, twice (before and after the last offline-test change): `[profile] cases: 53/53 passed in 108.8 s`; `profile secret scan: clean (1216 secrets held; 0 found in 810 log records, 130 writes and the results JSON)`; `profile value scan: clean (163 member values held: …; 0 found in the same output)`; `PROFILE VERDICT: PASS`; `suite_reported_clean` on that log: `True`; a second run on the same database refused (`refusing a used database: …`);
- the reversals above: 32 temporary edits, each applied exactly once by a harness in the scratchpad that ran the check, kept the failing lines and restored the file byte for byte (its SHA-256 checked). The database reversals ran on their own new database each: the suite's chosen cases through the suite's own context and `run_case` (without the scans), or the full suite where a scan or the digests case decides (`C2.8-age-py-logs-a-birth-date`, `C2.8-birth-input-unkeyed-sha256`). `git status` showed only the correction's own changes afterwards.

### The run of record

**Foundation push run [42864458572](https://github.com/amthorn78/glow-dating-app/actions/runs/42864458572)** on `01a3acb3d725e05d6e2d6a2d78f5e102db9e9f5a`, **the code head** (attempt 1, 17:23:28 to 17:33:28 UTC on 10 November 2026), read with the GitHub tools and the jobs' own log files. Every job's conclusion was `success`, and the gate printed **`Application checks passed`**:

- **Change scope:** success (a branch's first push: the trusted policy takes full scope; the change is full scope in any case).
- **API checks:** success. `System check identified no issues (0 silenced).`; `manage.py test tests --verbosity 2`: **`Ran 524 tests`**, `OK`; Ruff `All checks passed!`, `133 files already formatted`; **mypy: `Success: no issues found in 78 source files`**; the Python contract tests `Ran 49 tests`, `OK`, `test_f02_reacceptance_at_a_newer_version` and `test_sv2_registry_prerequisites_are_pinned` among them.
- **Mobile checks:** success. `Generated types and runtime validators match schemas.`; the contracts' `tests 709`, `pass 709`; `npm run check` `tests 691`, `pass 691`; `check:expo`; `export:development`; the rendered checks, **`104 passed (4.4m)`**.
- **API mobile smoke, API artifact checks, Stream proof checks:** success.
- **Database proof checks:** success, in 9 minutes 37 seconds (17:23:39 to 17:33:16) of its 30-minute timeout.
  - The offline tests **`Ran 221 tests`**, `OK`; Ruff, the format check and mypy (`Success: no issues found in 59 source files`).
  - A wrong marker refused (`wrong-marker migrate exit status: 1`) and `dbshell` refused (`dbshell exit status: 1`).
  - **The ordering suite:** `[reference] cases: 56/56 passed`, `[adapter] cases: 115/115 passed`, `[read] cases: 62/62 passed`, `== VERDICT: PASS ==`; a second run refused (`second run exit status: 1`), every count unchanged.
  - **The identity suite:** the ordering database's marker refused; `[identity] cases: 49/49 passed in 41.7 s`; `identity secret scan: clean (754 secrets held; 0 found in 240 log records, 102 writes and the results JSON)`; `identity phase: 42 s`; a second identity run refused, every count unchanged (`53 53 63 32 50`).
  - **The profile suite:** the profile database refused both other markers (`exit status 1` each); the migrations from zero and `No changes detected`; **`[profile] cases: 53/53 passed in 75.7 s`**, C2's six new cases among them; **`profile secret scan: clean (1216 secrets held; 0 found in 810 log records, 130 writes and the results JSON)`**; **`profile value scan: clean (163 member values held: coordinates, birth dates, times and places, own words, sensitive values; 0 found in the same output)`**; the job's own check: `the job's secrets found in the profile suite's output: 0`, `… in the profile results JSON: 0`, `the suite's own scans (secrets, member values) reported clean: True` (now read from the suite's own result lines); `PROFILE VERDICT: PASS`; **`profile phase: 76 s`**. The digests case checked **802** stored digests of all ten kinds of command.
  - **The second profile run** was refused (`second profile run exit status: 1`; `refusing a used database: auth users exist; app accounts exist; outbox events exist; a setting was published beyond its launch default. The profile suite runs once per new database.`), with the counts of auth users, app accounts, profiles, setting versions, outbox events and idempotency records **`108 108 92 38 978 802` before and after**.
  - `sv2-profile-results` (5,212 bytes) uploaded only after the check passed; the container, its credential files and the marker files removed (`no proof container remains`).
- **No toolchain retry fired:** every "Wait 60 s before the one retry of the Python install (DM-41)" step, and every retry, was `skipped`.
- **No secret, coordinate or member value in the Database job's log** (2,108 lines, searched as downloaded): none of the suite's coordinates at four decimals or more (`40.7123`, `74.0067`, `74.0068`, `34.0522`, `118.243`), the failing input's place prefix or time, the leap-day fixture date (ISO or "February 2008"), or the own words' prefixes. The only masked values are the checkout action's own token lines.

### What could not run, and the limits

- **The mobile app's export and rendered checks** are CI's; `playwright install` was not run here.
- **The Database proof checks job's shell steps** were not rerun locally as a whole: C2 changes neither the workflow nor the steps; the run of record ran them.
- **The server's clock cannot be set** (as before): the under-18 dates are 17 years and about four months, or 17 years and 45 days, before the database's UTC date, and the future date a year after it.
- **The database reversals ran chosen cases, not the whole suite,** except the two above; each case makes its own members, and the history case publishes its own cause first.
- **Not claimed:** the real target and its persistence; the deployed wiring; P07's staff API; SV3's discovery and SV4's messaging reads; what a new sensitive consent version asks of values saved under an earlier one (P08, Z19); the erasure of earlier birth input revisions after a failing date (G-01, P07, Z18).

### Decisions and deviations for the manager

1. **C2-1, the eligibility step's date first on both states.** The brief orders the date first for a self-declared adult. C2 puts it first for an `unknown` account too (still after the idempotency check), so a retry of the refused command, whose expected version is now stale, is refused `forbidden` as the brief's "a retry is refused, since the account is no longer an adult's" says, not `stale_version`. For an `unknown` account the refusals are the same as before; only a request that is both stale and carries a failing date now answers the date's code. Its reason codes are unchanged (`adult_check:future`, `adult_check:under_age`).
2. **C2-2, item 2's refusal code:** the existing `MORE_READABLE_NEEDS_CONSENT` (`more_readable_needs_consent_wording`); no new code.
3. **C2-3, item 7's refused example:** the oracle answers an old version `policy_unresolved` (no `consent_current`), not `forbidden`; the test also shows another owner `forbidden`.
4. **C2-4, the prerequisites' count:** one name added to the document's list (`staff_approval`), four prerequisites across SV2's entries (`consent_current`, `A05`, `staff_approval`, eligibility); both are pinned.
5. **C2-5, the nesting case's bodies:** within the 16 KiB request limit (10,000 opening brackets; 5,000 closed pairs), since a 20 KB body is refused by the limit before the parser (item 6's deviation).
6. **C2-6, a stale code comment:** `profile_cases.py`'s section comment "the scans run after every case" is wrong (they run once, after the last case; claim 6). It was found after the code commit, and the push rule allows no code change after the run of record; it is left for the next code change.
7. **No stop rule was met:** no model, migration, DTO, generated output, `glow_chat`, `glow_identity` (`age.py` included: unchanged at the head), `glow_api`, workflow, lock or dependency changed; no existing registry entry changed; the new entries' role is `owner`; the Database proof checks job took 9 minutes 37 seconds of its 30.

### Manager verification of correction C2 (App Manager 10, 10 November 2026)

**Integrated** at the merge `26419a9` (C2's code head `01a3acb`, records head `ca0ad16`). Nothing changed on the manager branch after `399c68d` before the merge.

**The scope:** `git diff --name-only 399c68d ca0ad16` lists 22 paths, each within "Stage A, correction C2"'s owned paths.
- The records commit `ca0ad16` holds Markdown only.
- No model, migration, schema, generated output, lock, workflow, `glow_chat`, `glow_identity` or `glow_api` path changed, and `age.py` is unchanged.
- `flows-v1.json` gains only the two F02 entries (`accept` and `accept_sensitive` from `accepted` to `accepted`, `owner`, `consent_current`), and no existing entry changed.
- The P11 plan changed only in its "SV2 Stage A" entry.
- The trusted classification, `main`'s policy run with `python3 -I` outside the tree: `"full": true`, `behavior-or-empty`, with one merge base, `df8a04c`.
- The whole of Stage A's code diff is still 59 non-Markdown paths from `df8a04c`.

**Re-runs,** in a scratch copy of `01a3acb` (`git archive`), in the clean environment, with the hash-locked installs:
- **API:** `manage.py check`, no issues; `Found 524 test(s)` … `OK`; Ruff clean; `133 files already formatted`; mypy `no issues found in 78 source files`.
- **Contract tests:** `Ran 49 tests` … `OK`.
- **The proof's offline tests:** `Ran 221 tests` … `OK`; Ruff clean; `59 files already formatted`; mypy `no issues found in 59 source files`.
- **The contract outputs:** `node scripts/generate.mjs --check`: `Generated types and runtime validators match schemas.`

The manager runs no database test locally.

**Four reversals, re-run offline.** Each failed as it should:
- **C2-R1:** the U+0000 check removed from `text_ok`. `test_each_answers_400_with_the_contracts_error_and_no_value (case='u0000_in_a_stored_text')` fails.
- **C2-R2:** `RecursionError` removed from `parse`'s refusals. The same test fails.
- **C2-R3:** the new `accept_sensitive` entry's role set to `staff`. `test_f02_reacceptance_at_a_newer_version (event='accept_sensitive')` fails.
- **C2-R4:** a profile `.update(state="visible")` added to `operations.py`. `test_only_the_recompute_writes_a_profiles_state` fails.

Each file was restored and its hash checked against `01a3acb`.

**The run of record**, read with the GitHub tools: push run 42864458572 on `01a3acb`.
- All eight jobs `success`, and the gate printed `Application checks passed`. Every DM-41 retry step was `skipped`.
- The profile suite: `[profile] cases: 53/53 passed in 75.7 s`.
  - `profile secret scan: clean (1216 secrets held; 0 found in 810 log records, 130 writes and the results JSON)`;
  - `profile value scan: clean (163 member values held …; 0 found in the same output)`;
  - `PROFILE VERDICT: PASS`, and `profile phase: 76 s`.
- The second profile run was refused, with the counts `108 108 92 38 978 802` unchanged.
- `sv2-profile-results` is 5,212 bytes, and the cleanup removed the container.

**Codex.** Its review of `496c39e` raised one P2, and its review of `399c68d` two P1s. Each is an item of C2:
- **The history label moved first** (P2, `profile_settings.py:414`): finding 1, item 2.
- **A date under 18 behind a later refusal** (P1, `operations.py:1011`): item 1.
- **The sensitive consent's version at a save** (P1, `operations.py:130`): finding 9, item 3.

The P2 on `40db2c2` (`operations.py:1019`) asked that a future date commit the reset. DM-55 ruled it invalid input that changes nothing, and C2 builds that. Its thread is answered with the ruling. The four threads are answered and resolved once this batch is pushed.

**The session's decisions** (its "Decisions and deviations for the manager"):
- **C2-1:** the eligibility step checks the date first for an `unknown` account too, still after the idempotency check. A retry of the refused command then answers `forbidden`, not `stale_version`. **Accepted, the manager on DM-55's words.** Z2 orders the date first for a self-declared adult, and says only what an `unknown` account's refusals are. The order changes no outcome but the refusal's code, and nothing is written either way. It goes to the exact-head review and to the Dev Manager's pre-merge read.
- **C2-2:** item 2 reuses `MORE_READABLE_NEEDS_CONSENT`. **Accepted:** the prompt allowed it.
- **C2-3:** item 7's refused example is the oracle's `policy_unresolved` for an old version, with another owner `forbidden`. **Accepted:** it is the oracle's own answer.
- **C2-4:** one name added to the document's list (`staff_approval`), and four prerequisites across SV2's entries, all pinned. **Accepted:** the review's "four" counted the second.
- **C2-5:** the nesting case's bodies stay within the 16 KiB request limit. **Accepted:** the first body never reached the parser, and the session found it by its reversal.
- **C2-6:** `profile_cases.py`'s comment "the scans run after every case" is stale (corrected claim 6). **A recorded follow-up:** it is fixed with the next code change to the profile suite, a correction after the review if one is needed, or Stage B.

## Exact-head review of Stage A after C2 (code head `01a3acb`)

- **The session:** started by Nathan from the exact-head review prompt after C2, revision 1, at `44455a59cba40f620bad0cdf81d4dfda62ee553b` (`docs/ephemeral/2026-11-10-sv2-stage-a-c2-review-prompt.md`). It reported on 10 November 2026, and its report was relayed to App Manager 10.
- **The gates:**
  - the environment check passed: none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, `STREAM_*` or `PG*` was present, and the GitHub token names were never read;
  - the start gate passed, with one merge base, `df8a04c` (`main`'s `c864edd` has the same tree), and no code differing from `01a3acb`;
  - the trusted classification is `"full": true`, `behavior-or-empty`.
- **What it ran,** in a scratch copy of `01a3acb`:
  - the API's checks: `manage.py check`; 524 tests `OK`; Ruff; mypy clean on 78 files;
  - the contract tests (49), `generate.mjs --check`, and `npm run check` (709 of 709);
  - the proof's offline tests (221), Ruff and mypy (59 files);
  - the five required offline reversals, each failing its case (R1 to R5);
  - the Census zip (46,177 bytes): both pinned hashes matched, and `areas_source.py derive` reproduced the committed table byte for byte;
  - informational, on a throwaway PostgreSQL under P06.DB's D4: the suite 53/53 with both scans clean and a second run refused, and four database reversals (DB1 to DB4), each failing a case.
- **What it read:** runs 42759801460 (44/44), 42769301337 (47/47) and 42864458572 (53/53), and PR43's pull-request run 42869473767 on `44455a5` (53/53 in 77.7 s; profile phase 79 s; counts `108 108 92 38 978 802` unchanged). In each, all eight jobs passed, the gate printed `Application checks passed`, and no DM-41 retry fired. The SV2 steps' logs hold no unmasked secret, PEM line, coordinate or date.
- **The verdict: changes required, narrowly, in tests only.** It found no defect in the code. Finding 1 is should fix in a correction class; findings 2 to 6 are nits.
- **Its statements:**
  - none of the Dev Manager's conditions is unmet in the code, read through the brief's revision 5;
  - each of the first review's 15 findings is fixed as disposed, or carried as DM-55 ruled;
  - each of C2's ten items is built as the brief words it;
  - no test was weakened: C2's rewrites keep every later assertion, and the one removed assertion (the deleted rows) is the one DM-55's in-place rule replaced;
  - of the 68 existing contract definitions, only `AppIntent` and `AppResponse` changed, by gaining members; the 20 new ones are closed; the outputs regenerate byte for byte; all 21 new registry entries use authorized roles, with an allowed and a forbidden example;
  - the workflow's diff from `df8a04c` is confined to the Database proof checks job, and C2 did not change it;
  - no lock or dependency manifest changed;
  - the records' claims hold against the code and the runs.
- **On the manager's readings:**
  - **C2-1: confirmed.** Putting the date first for an `unknown` account too is within Z2's words. It changes no outcome but a refusal's code: a request carrying both a stale version and a failing or future date answers 403 or 400 instead of 409. Nothing is written either way, and the idempotency check still comes first.
  - **C2-4: right.** One name added to the document's list (`staff_approval`), four prerequisites across SV2's 21 entries, each pinned exactly.

**The review's threat model**, as its report gives it, condensed (assets, actors and entry points are the prompt's):

| # | Threat | What stops it | What proves it |
|---|---|---|---|
| 1 | An anonymous prober on the 15 routes | SV1's actor only, with `IsAuthenticated`; `handle_exception` answers 401 with the contract's `Error` | `ownership.every_route_refuses_strangers_and_stale_versions` |
| 2 | A stolen token | SV1's actor; `lock_account` and `read_account_shared` refuse an account that is not active | the same case; SV1's suite, 49/49 |
| 3 | A member on another member's object | the account from the actor only; reads filter by it; another member's object ID is `not_found` | the ownership case; `sets.start_at_all_and_stay_the_owners` |
| 4 | A stale or replayed command | each writer's expected version; `idempotency.decide` after the locks | `ownership.a_replay_and_a_conflicting_key` |
| 5 | A publication crossing a fixed limit, in one step or two, or unaudited | `publication_refusals` before any write; `publish` writes the version, pointer, `StaffAudit` and `policy_published` together | `FixedLimitTests`; `settings.fixed_limits_refused_before_any_write`; `settings.history_limit_not_crossed_in_two_publications`; `settings.publication_writes_version_audit_event` |
| 6 | A sensitive save without the current consent version, or a value outliving withdrawal | one `read_shared` call for the catalog and the consent; `_sensitive_accepted` checks the version; the rows set to "not stated" in place | `fields.sensitive_needs_consent`; `fields.sensitive_needs_the_current_consent_version`; `consent.sensitive_withdrawal_scope`; DB2, DB3 |
| 7 | One consent satisfying the other; an old version accepted | `latest_decision` filters by purpose; the version checked under the pointer's lock; the `consent_purpose` constraint | `consent.purposes_never_satisfy_or_revoke_each_other`; `consent.old_version_refused` |
| 8 | Coordinates kept or echoed | `nearest_area` writes nothing; a query string refused; every error a code only | `area.nearest_query_changes_nothing`; `area.coordinates_never_kept_or_echoed`; the value scan; `BodiesTheParserCannotHoldTests` |
| 9 | A birth input read by another, or an engine result invented | owner-only reads; no `EngineIdentity` created; nothing writes `resolved` or `verified` | `birth.submit_correct_change_write_private_revisions`; `birth.a_seeded_mapping_returns_to_pending`; `WritesTests` |
| 10 | A member who declares a date under 18 | the date first at both writers; `_reset_failing_date`; the `age_state_birth_date` constraint | `adult.a_self_declared_adults_date_comes_first_at_both_writers`; `birth.a_failing_date_is_refused_and_nothing_of_it_is_stored`; `CallSiteTests`; DB1, DB4 |
| 11 | `visible` with a requirement missing, or left `visible` | `recompute` ends all eight writers on every non-raising path; resume rechecks | the `completion.*` cases; `CallSiteTests`; `completion.a_second_writer_waits_for_the_account_row_lock` |
| 12 | A member route reaching a staff operation | `views` and `urls` import no staff code; the subject from the caller only; `_check_staff` | `test_no_view_reaches_a_staff_operation`; `staff.no_member_route_reaches_a_staff_operation`; gap: finding 1(d) |
| 13 | Staff approval with the setting off, or standing in for more | the setting read `FOR SHARE` after the account lock; `requirements.missing` checks each | `staff.approval_gated_narrow_survives_and_is_revocable` |
| 14 | Seeded rows reaching the runtime | seeds only in the proof's `profile_support`, with `fixture:` values; the port refuses `record_check_passed` | `WritesTests`; `completion.needs_the_chart_and_identity_verification_seeded` |
| 15 | Values in the outbox, or an event naming a deleted record | `events.emit` takes references only; no SV2 path deletes a referenced row | `completion.each_change_emits_its_event`; the withdrawal case |
| 16 | A stored digest reversed by trying values | `salted_hmac`, SHA-256, a salt naming the operation | `KeyedDigestTests`; `digests.*` (802 records, 10 kinds); R3 |
| 17 | Values in logs or errors | the views log a code only; `tx.run` reports an exception by type; the parser echoes nothing | `NoValueInLogsTests`; the value scan; gaps: finding 1 |
| 18 | The served runtime importing SV2 | `glow_api` names none of it | `ProfilesSealedRuntimeTests`; R1 |
| 19 | The area file changed or fetched | migration 0006 checks the file's SHA-256; nothing fetched | `area.file_hash_and_925_areas`; the review's re-derivation |
| 20 | Secrets or member values in CI logs or artifacts | generated in the job, masked, mode 0600; `profile_scan` before any output or upload | `ProfileScanTests`; the four runs' logs |

**The review's findings and the manager's dispositions** (step 6, "Fix or carry, by rule"):

| # | Severity (class) | Finding | Disposition |
|---|---|---|---|
| 1 | should fix, low (a test passes where it should fail: the first review's finding 7's class). The code at `01a3acb` is right | The static guards are name-based, and plausible edits pass all 524 API tests and 221 proof tests: **(a)** an `AgeTransitionRefused` message in `age.py` becomes the refusal reason `f"age:{refused}"`, which `views.py` logs at INFO, and the age-port guard covers logging only; **(b)** a second logger in `views.py`, a borrowed logger under another name, or `sys.stderr.write`; **(c)** a profile state written as `before.state = …`, through `bulk_update`, `setattr`, a queryset variable's `.update(**…)`, or from `age.py`; **(d)** a member view reaching staff code through a helper in `operations.py`; **(e)** a new operation whose inner function is not named `body`, or a recompute inside a condition | **Fix before the merge, in correction C3** (test-only), for (a) to (c), with the review's bounded fix: the refusal-reason check covers `AgeTransitionRefused(…)` in `age.py` and `PortOutcome(…)` in `glow_profiles/identity_verification.py`; `views.py` holds exactly one `getLogger` call, and every logging call is checked whatever its receiver is named; every `.state =`, `setattr(…, "state", …)` and `bulk_update` in `glow_profiles` is on an allowlist of non-profile writes or in `recompute.py`. **(d), (e) and lazy imports in `glow_domain`:** recorded as the guards' limits, as the review advises |
| 2 | nit | `BodiesTheParserCannotHoldTests` is defined after `unittest.main()` in `test_profiles_offline.py`, so running the file as a script skips it (`manage.py test` runs it) | **In C3:** the class before `unittest.main()` |
| 3 | nit | `profile_cases.py:2227`: `ctx.refused(…, born)` uses the fixture date as a check's label, so a failing run would print it in the case's detail (the scan withholds a failing log) | **In C3:** a label without the date |
| 4 | nit (records) | The recompute's `consent.onboarding` read comes after the `profile.*` or `identity.staff_approval` pointers, so "the pointers `FOR SHARE` in name order" holds per `read_shared` call, not across a transaction. No deadlock is possible: a publication holds one pointer `FOR UPDATE` | **In C3's record:** Stage A's lock-order sentence corrected to "in name order within each `read_shared` call", with the reason no deadlock can follow. No code change |
| 5 | nit (policy) | With `chosen_area` off and only the phone's location offered, `set_area` accepts any area ID, not only the query's answer | **Recorded, no change:** D5's "that area, or another" allows it, and both ways are on at launch |
| 6 | nit | `set_preferences` and `set_filters` do not check the profile's state, so a restricted profile can still change its sets and filters. Nothing leaks | **Carried to P07** (what a restriction stops), in the carried-items file |
| Known | recorded follow-up | C2-6, `profile_cases.py`'s stale comment on the scans' timing | **In C3**, as C2-6's disposition says (the next code change to the profile suite) |

**A note on the database reversals:** DB4 (an idempotency record stored with the under-18 refusal) fails the date-first case and the digests case, though not `adult.failing_dates_are_refused_and_not_stored`. No gap follows: two cases catch it.

**What the review read in part only, or could not run:**
- DM-52 to DM-55's reports were read in part (DM-55's verdicts and items, DM-54's verdict table and Y10 and Y11); OD-60 and OD-61, and `glow_chat`'s functions, were not read. The conditions were checked through the brief's revision 5, which applies them word for word. The Dev Manager's pre-merge read covers the conditions as applied.
- `profile_cases.py` was read in the cases the focus names; migration 0005, the corpus and the other profile test files were surveyed or run.
- The mobile app's export and rendered checks, the ordering and identity suites, and the workflow's shell steps as a whole were not run locally; push run 42869454425 was not read.

Nothing in the repository, on GitHub or in Notion changed.

**C3's review:** C3 changes tests only (no non-test line), so a delta review follows it, reading every path C3 touches as it stands at C3's head (M05 S2). Codex reads the PR's final head as usual.

## Correction C3

Correction C3 of Stage A, to the exact-head review after C2 (above, "Exact-head review of Stage A after C2") as the brief's "Stage A, correction C3" words it: findings 1 to 4 and C2-6. **C3 changes tests and this record only;** the code is `01a3acb`'s. Local database runs here are iteration, not evidence; the evidence of record is the CI run on the code head, below. Stage A's, C1's and C2's sections stand as written; this section corrects one sentence of Stage A's (below, item 6).

### The session

- **The prompt:** C3's correction prompt, revision 1, from `e55dd81a43d215584ecdb731916713e104409295` of `claude/magical-wozniak-yfmmx2`, started by Nathan.
- **The branch:** `claude/stoic-faraday-gist9o`, started at `e55dd81`. Its name matches `claude/**`, so the Foundation workflow runs on its pushes.
- **The code commit, the code head:** `fee4fdc` (`fee4fdc5c71c54b95faa9bbb1256edee74546de3`): the four test files below, nothing else.
- **The records commit** (this section only) follows the run of record, as the push rule requires.

### Start gate and environment

- **The environment check, names only.** None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` was set (the prompt's loop printed nothing), and no `STREAM_*` or `PG*` name (`compgen -e | grep -E '^(STREAM_|PG)'` printed nothing). `GH_TOKEN` and `GITHUB_TOKEN` were present and never read. Every repository command ran in a clean process environment (`env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus `GLOW_ENV=test` for the API); the installs and the Docker daemon took the proxy and CA variables by reference, never printed.
- **The toolchain:** `Python 3.12.14` (`python3.12`); Node `v24.19.0` and npm `11.9.0`, both `$HOME/.local/bin` (`/root/.local/bin`), first on `PATH`; `Docker version 29.9.2, build a82e528`.
- **The start gate,** each line as the prompt has it:
  - `git fetch origin claude/magical-wozniak-yfmmx2 main`: fetched (`main` at `c864edd`; the manager branch at `e55dd81` itself);
  - `git switch -C claude/stoic-faraday-gist9o e55dd81…` and `git rev-parse HEAD`: `e55dd81a43d215584ecdb731916713e104409295`;
  - no non-Markdown path under `.github`, `scripts`, `services`, `apps`, `packages` or `proofs` differs from `01a3acb`: printed nothing;
  - no owned path (`services/api`, `proofs/postgres-ordering`, the SV2 evidence) differs from the live manager branch: printed nothing; `e55dd81` is on it (`merge-base --is-ancestor`: yes);
  - `grep -c -E '^#+ Correction C3'` on this record: `0`;
  - `grep -c 'Stage A, correction C3 (the review after C2)'` on the brief: `1`.

### Item 1 — the static guards (finding 1, (a) to (c))

**The files:** `services/api/tests/test_profiles_offline.py` (`NoValueInLogsTests`: four new tests; a new `scanned_modules()`, `glow_profiles` and `glow_identity/age.py` by path) and `services/api/tests/test_profile_recompute.py` (`CallSiteTests.test_only_the_recompute_writes_a_profiles_state`, extended; its earlier assertions kept). Each new check passes on `01a3acb`'s code as it stands (`Ran 529 tests`, `OK`; 524 before, five added).

- **Refusal reasons** (finding 1 (a)).
  - `test_the_age_ports_refusals_are_codes`: every exception class `age.py` defines (`AgeStateRecorded`, `AgeTransitionRefused`) is built from exactly one argument, a literal string matching the whole-code pattern (`[a-z_]+(:[a-z_]+)?`), with no keywords; at least four `AgeTransitionRefused` and one `AgeStateRecorded` (today four and one). `_reset_failing_date` raises `f"age:{refused}"` from it, and the views log that reason, so the message is now checked at its source.
  - `test_the_identity_ports_outcomes_are_codes`: every `PortOutcome(…)` in `glow_profiles` is in `identity_verification.py` and built from literals only: an outcome in `applied`, `no_change`, `refused`, and a reason (positional or keyword) matching the whole-code pattern; at least six (today six). `staff.py` raises `Refused(STATE_CONFLICT, outcome.reason)` from it.
- **Logging** (finding 1 (b)).
  - `test_the_views_hold_one_logger_and_name_it_only_to_log`: `views.py` holds exactly **one** call ending `getLogger`; its one module-level binding is `logger = logging.getLogger('glow_profiles.views')`; its one logging import is `import logging` (no alias, no `from logging`); `logging` is named only in that call; `logger` is named only where it is bound and as the receiver of the two `logger.info` calls, so it is never passed, copied or borrowed under another name.
  - `test_every_logging_call_is_checked_whatever_its_receiver`: every attribute in `glow_profiles` or `age.py` named `debug`, `info`, `warning`, `warn`, `error`, `exception`, `critical`, `fatal` or `log`, called or not, on any receiver, is one of the views' `logger.info` calls (whose format and arguments `test_only_the_views_log_and_only_a_code` checks) or the contract's `error` builder, reached as `contract.error` where the module imports `from glow_profiles import contract` and never rebinds the name, and `contract.py` defines `error`. A `getattr` with a literal logging method name is refused too.
  - `test_nothing_writes_to_the_standard_streams`: no attribute `stdout`, `stderr`, `__stdout__` or `__stderr__` (however `sys` is named); no import of those names or of `write`; no import of `warnings`, `traceback`, `faulthandler` or `pprint`; no `print(…)` with a `file` keyword or `**`; no `os.write` or `os.writev`; in `glow_profiles` and `age.py`.
- **Profile state** (finding 1 (c)). `_state_writes` finds, in `glow_profiles` and `age.py`, every assignment (plain, augmented or annotated, tuple targets included) to any `.state`; every `setattr`, `vars`, `__setattr__` and `__dict__`; every `bulk_update`; and every `update`, `update_or_create` or `get_or_create` whose keywords name `state`, `defaults` or `create_defaults`, or unpack `**`, **whatever the receiver is named**. The set found must equal the recompute's write plus the allowlist below, each by file, line, enclosing function and statement; and `_binds` checks that every value the enclosing function binds to the written variable is the named model's (an expression naming it, or a call of a same-module helper whose every return names it), and that the recompute's `profile` is a `Profile`. The earlier checks stay: the one `profile.state = after` in `recompute.py`, no queryset `.update(state=…)` on a receiver naming `Profile`, and `Profile.objects.create(state='incomplete')` the only create.

**The guards' allowlist** (`NOT_A_PROFILES_STATE` in `test_profile_recompute.py`; writes that are not a profile's state):

| File | Line | Function | Statement | Model |
|---|---|---|---|---|
| `glow_profiles/recompute.py` | 138 | `recompute` | `profile.state = after` | `Profile` (the recompute's own write, `RECOMPUTE_WRITE`) |
| `glow_profiles/identity_verification.py` | 82 | `approve_without_id` | `row.state = VerificationState.STAFF_APPROVED.value` | `IdentityVerification` |
| `glow_profiles/identity_verification.py` | 96 | `revoke_approval` | `row.state = VerificationState.UNVERIFIED.value` | `IdentityVerification` |
| `glow_profiles/operations.py` | 902 | `_invalidate_birth_input` | `current.state = 'missing'` | `BirthInput` |
| `glow_profiles/operations.py` | 922 | `_mapping_to_pending` | `mapping.state = 'pending'` | `EngineIdentity` |
| `glow_identity/age.py` | 98 | `transition` | `row.state = change.state.value` | `AccountAgeState` |

The entries name their lines, as the brief asks, so an edit that moves one of these lines also fails the check until the allowlist is updated with it; that is the price of naming the line.

**The reversals,** each a temporary edit of `01a3acb`'s code, applied once by a harness in the scratchpad. For each, the harness ran **`01a3acb`'s whole API suite** in a scratch copy of `01a3acb` holding the same edit, which passed (`Ran 524 tests`, `OK`: the edit is one the earlier guards let through), then the new check in the branch, which failed, then restored the file in both trees and checked its SHA-256 against `01a3acb`'s.

| Reversal | The temporary edit | `01a3acb`'s 524 | The new check's failing output |
|---|---|---|---|
| `C3.1a-age-refusal-from-a-value` | `age.py`: `raise AgeTransitionRefused(f"no_transition:{change.birth_date}")` | `OK` | `FAIL: test_the_age_ports_refusals_are_codes … (line=95)`; `AssertionError: <ast.JoinedStr …> is not an instance of <class 'ast.Constant'> : f'no_transition:{change.birth_date}'` |
| `C3.1a-port-outcome-from-a-value` | `identity_verification.py`: `return PortOutcome("refused", f"not_unverified:{reason}")` (the staff's own reason) | `OK` | `FAIL: test_the_identity_ports_outcomes_are_codes (module='identity_verification.py', line=77)`; `AssertionError: False is not true : PortOutcome('refused', f'not_unverified:{reason}')` |
| `C3.1b-a-second-getlogger-in-views` | `views.py`: `audit = logging.getLogger("glow_profiles.audit")`, and `audit.info("profile route refused: %s", result.data)` in `_answer` | `OK` | `FAIL: test_the_views_hold_one_logger_and_name_it_only_to_log`: `AssertionError: 2 != 1`; `FAIL: test_every_logging_call_is_checked_whatever_its_receiver`: `['glow_profiles/views.py:85 audit.info'] != []` |
| `C3.1b-a-borrowed-logger` | `views.py`: `trace = logger`, and `trace.info("profile route refused: %s", result.data)` in `_answer` | `OK` | `FAIL: test_the_views_hold_one_logger_and_name_it_only_to_log`: `['Assign:33', 'bound', 'logger.info', 'logger.info'] != ['bound', 'logger.info', 'logger.info']`; `FAIL: test_every_logging_call_is_checked_whatever_its_receiver`: `['glow_profiles/views.py:85 trace.info'] != []` |
| `C3.1b-sys-stderr-write` | `operations.py`: `import sys`, and `sys.stderr.write(f"{intent['value_ids']}\n")` before `set_field`'s field refusal | `OK` | `FAIL: test_nothing_writes_to_the_standard_streams`: `['glow_profiles/operations.py:424 sys.stderr'] != []` |
| `C3.1c-before-state-in-staff` | `staff.py`, `restrict_profile`: `before.state = "visible"` and `before.save(update_fields=["state", "updated_at"])` | `OK` | `FAIL: test_only_the_recompute_writes_a_profiles_state`: `Items in the first set but not the second: ('glow_profiles/staff.py', 226, 'body', "before.state = 'visible'")` |
| `C3.1c-bulk-update` | `operations.py`, `adult_check` (below every allowlisted line): `Profile.objects.bulk_update([Profile(pk=p.pk, state="visible") for p in Profile.objects.filter(account_id=account_id)], ["state"])` | `OK` | `FAIL: test_only_the_recompute_writes_a_profiles_state`: `Items in the first set but not the second: ('glow_profiles/operations.py', 1003, 'body', "Profile.objects.bulk_update([Profile(pk=p.pk, state='visible') for p in …], ['state'])")` |
| `C3.1c-setattr` | the same place: `held = Profile.objects.filter(account_id=account_id).first()`; `setattr(held, "state", "visible")`; `held.save(…)` | `OK` | `FAIL: …`: `Items in the first set but not the second: ('glow_profiles/operations.py', 1004, 'body', "setattr(held, 'state', 'visible')")` |
| `C3.1c-queryset-variable-update` | the same place: `profiles = Profile.objects.filter(account_id=account_id)`; `profiles.update(**{"state": "visible"})` | `OK` | `FAIL: …`: `Items in the first set but not the second: ('glow_profiles/operations.py', 1004, 'body', "profiles.update(**{'state': 'visible'})")` |
| `C3.1c-state-write-in-age-py` | `age.py`: `Profile` imported, and in `transition` before `return "applied"`: the profile `FOR UPDATE`, `profile.state = "incomplete"` when `visible`, and its save | `OK` | `FAIL: …`: `Items in the first set but not the second: ('glow_identity/age.py', 122, 'transition', "profile.state = 'incomplete'")` |

The three `operations.py` state reversals were first placed in `set_area`, above the allowlisted lines 902 and 922; they failed there too, but also through those lines' move. They were rerun below line 922, as above, so that the failure is the new write alone. Every file was restored: `age.py` `303818000681…`, `identity_verification.py` `3be51bb3cef8…`, `views.py` `0f18425ed1e8…`, `operations.py` `4e31cc73028…`, `staff.py` `9823c4d9a676…`, each equal to `01a3acb`'s; `git diff 01a3acb -- services/api/glow_profiles services/api/glow_identity services/api/glow_domain services/api/glow_chat services/api/glow_api services/api/glow_persistence` is empty at the code head.

### Item 2 — the guards' limits (finding 1, (d) and (e))

What the static guards cannot see, and what covers each behaviour:

- **A member view reaching staff code through a helper in `operations.py`.** `ProfileRoutesTests.test_no_view_reaches_a_staff_operation` reads the imports and names of `views.py` and `urls.py` only; `operations.py` could import `glow_profiles.staff` lazily inside a function (a module-level import would be circular, since `staff.py` imports `operations`) and call it from a member command. **The profile suite's cover:** `staff.no_member_route_reaches_a_staff_operation` (the served routes are exactly SV1's and SV2's, none names a staff word, and the staff-shaped paths answer 404) shows no route *is* a staff operation, and `staff.approval_gated_narrow_survives_and_is_revocable` shows the approval's effects only through the staff calls. Neither drives every member command looking for a staff write, so a helper that a member command calls on some inputs would be seen only by the case that exercises those inputs; `completion.each_change_emits_its_event` would show an unexpected `identity_verification_changed` only where it counts that event.
- **A new operation whose inner function is not named `body`.** `LockOrderTests` finds operations by their inner `body` function and pins the set (`COMMANDS | READS | STAFF`), so a renamed `body` in an existing operation fails it, but a *new* operation with another inner name is not seen. **The profile suite's cover:** a new member command needs a route, and the route set is pinned twice (`ProfileRoutesTests` and `staff.no_member_route_reaches_a_staff_operation`); the lock order itself is observed for the existing operations in `pg_locks` by `completion.takes_the_account_lock_first_and_sees_a_withdrawal`, `completion.a_second_writer_waits_for_the_account_row_lock`, `adult.transition_bumps_and_waits_on_the_account_lock` and `settings.pointer_read_under_lock`. A new operation would need its own case: none exists before it does.
- **A recompute inside a condition.** `CallSiteTests.test_every_requirement_writer_ends_with_the_recompute` finds the `recompute.recompute(…)` call anywhere under the writer (or a module helper it calls), so a call under an `if` that a path skips passes it. **The profile suite's cover:** each writer is driven through its route to its recompute's effect: `completion.every_requirement_writer_meeting_the_last_one_makes_it_visible` (the profile edit, a field, orientation, the area, the onboarding consent's accept, the adult check, the staff approval), `completion.a_write_that_finds_a_requirement_missing_demotes` (the area, a field, the adult check's unchanged date, the profile edit finding a lapse, the area before the acceptance; `paused`, `restricted` and `removed` stay), `completion.removals_demote_and_empty_values_are_refused` (the consent's withdrawal, the summary cleared, a birth input, the adult rerun and the approval's revocation, each on a visible and a paused profile), `adult.a_corrected_date_reruns_and_demotes` and `birth.a_failing_date_is_refused_and_nothing_of_it_is_stored` (the failing date at both writers), and `birth.a_seeded_mapping_returns_to_pending` (a new birth input revision). A condition that skips the recompute only on a path no case takes would not be seen.
- **A lazy import in `glow_domain`.** `ProfilesSealedRuntimeTests.test_the_age_section_imports_nothing_new` reads `glow_domain/identity.py`'s lines that *start* with `import` or `from`, so an import indented inside a function is not seen, and `test_the_runtime_imports_none_of_the_profile_slice` reads `sys.modules` after the runtime's import, before any function runs. **No profile-suite case covers this:** the profile suite runs under the proof's profile settings, where `glow_profiles` is meant to load. What bounds it is `test_the_profile_slice_cannot_load_under_the_runtime_settings` (each of `operations`, `staff`, `views`, `urls` and `settings_store` refuses to load under the runtime's settings: its apps are not installed) and the dummy backend's refusal of any connection (`refused: ImproperlyConfigured`), so a lazy import reached at run time in the served runtime would fail closed, not reach a database. This is a deviation from the brief's "the profile suite's cases cover each behaviour", recorded for the manager below.

**Further limits of C3's own guards,** found while building them:
- a `getattr` whose method name is computed (`getattr(log, name)`) is not seen; only a literal logging method name is;
- a state written through raw SQL (`cursor.execute("UPDATE …")`), or a `Profile(…, state=…)` built and saved, or `Profile.objects.create` with `**`, is not seen by the state guard; the creates check names `Profile.objects.create` only;
- `_binds` reads the bindings of the written variable in its enclosing function only; a model reached through an attribute or another module's helper is not followed (none of the allowlisted writes needs it);
- the stream guard does not follow a file object passed in from elsewhere (`areas_source.py`'s `handle.write` writes the derived table to the file its command opened).

### Item 3 — `BodiesTheParserCannotHoldTests` (finding 2)

**The file:** `services/api/tests/test_profiles_offline.py`: `if __name__ == "__main__": unittest.main()` moved from before the class to the file's end. **The check,** the file run as a script from `services/api` (`.venv/bin/python tests/test_profiles_offline.py -v`): in a scratch copy of `01a3acb`, `Ran 11 tests`, `OK`, with no `BodiesTheParserCannotHoldTests` line; at the code head, `test_each_answers_400_with_the_contracts_error_and_no_value (__main__.BodiesTheParserCannotHoldTests…) ... ok`, `Ran 17 tests`, `OK` (the eleven, C3's five and the class's one). `manage.py test` ran it before and after.

### Item 4 — no check's label holds a member value (finding 3)

- **The file:** `proofs/postgres-ordering/glow_ordering_proof/profile_cases.py`. In `adult.a_self_declared_adults_date_comes_first_at_both_writers`, the unknown account's loop now carries a label with each date, `"an unknown account's future date"` and `"an unknown account's date under 18"`, and `ctx.refused(…, what)` takes it, where it took the fixture date (`born`) at line 2227. In `adult.age_years_is_whole_years_never_the_date`, the label `f"whole years ({years})"` printed the fixture member's age; it is now `"whole years, as the date gives them"`. Both checks are otherwise unchanged; the case count stays 53.
- **How it was checked:** an AST pass over `profile_cases.py` listed the label of every checking call (`expect`'s second argument, `ctx.refused`'s fourth, `ctx.data`'s third: 487 calls at the code head) and every interpolation in one. Each interpolated name was read where it is bound: setting, field and event names, routes, codes, profile states, the missing requirements' names, loop labels (`what`, `when`, `writer`, `removal`) bound to literal text, and the stored records' operation names. Only `born` and `years` held a member's value. The same pass over the cases' detail lines (their `return` values) and `CaseFailed` messages found counts, codes and labels only. **A new offline test pins it:** `tests/test_profile_offline.py`, `ProfileLabelTests.test_no_checks_label_holds_a_member_value`: every label is literal text, a choice between two literals, or an f-string whose interpolations are in `LABEL_NAMES` (17 names, each read as above); more than 450 calls checked. `test_a_label_built_from_a_value_is_found` shows both old labels found.
- **The reversals,** each a temporary edit of the branch's `profile_cases.py`, restored after (SHA-256 `244197ba64d6…`, the code head's): `C3.4-the-date-as-a-label` (`… status, code, born)`): `FAIL: test_no_checks_label_holds_a_member_value`, `AssertionError: Lists differ: ['2231: refused labelled by born'] != []`; `C3.4-the-age-in-a-label` (`f"whole years ({years})"`): `AssertionError: Lists differ: ['2447: expect labelled by years'] != []`.

### Item 5 — the scans' timing (C2-6)

`profile_cases.py`'s section comment now reads "the scans run once, after the last case", as `profile_suite.run` does (the secret and value scans run in its `finally`, after the loop over the cases, then on the results JSON). A comment only; no check changes.

### Item 6 — the records: Stage A's lock-order sentence (finding 4)

Stage A's "Each writer's locks, in order" says "the settings' pointers `FOR SHARE` in name order". **Corrected:** the account row first; then the settings' pointers, `FOR SHARE`, **in name order within each `read_shared` call**, not across a transaction. The recompute's onboarding read (`consent.onboarding`, its own `read_shared` call) comes after the writer's other pointers, so it can follow a writer's `profile.*` or `identity.staff_approval` pointers. **No deadlock follows,** since a publication holds one pointer `FOR UPDATE` (and takes no account row): every other lock on a pointer is `FOR SHARE`, and shares do not conflict with each other. Stage A's sections stand as written; this is the sentence as it should read.

### The threat model's inputs (C3)

C3 changes no code path, so no threat changes. It narrows two gaps the review named: threat 17 (values in logs or errors), whose static cover now checks the age port's and the identity port's reasons at their source, every logging attribute whatever its receiver, and the standard streams; and threat 11 (`visible` with a requirement missing), whose static cover now sees every state write in `glow_profiles` and the age port whatever its variable is named. Threat 12's gap (finding 1 (d)) and the guards' other limits are item 2's.

### Commands and results

**API** (`services/api`; `python3.12 -m venv .venv`, then `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`, the first attempt stalled with no output and was stopped, the second with `--timeout 60 --progress-bar off` exited 0; each command with `GLOW_ENV=test` in the clean environment), at the code head:
- `python manage.py check`: `System check identified no issues (0 silenced).`
- `python manage.py test tests --verbosity 2`: `Ran 529 tests`, `OK` (524 at `01a3acb`, run the same way in a scratch copy: `Ran 524 tests`, `OK`).
- `ruff check .`: `All checks passed!`; `ruff format --check .`: `133 files already formatted` (after `ruff format` of the two changed files, which it had first listed).
- `mypy`: `Success: no issues found in 78 source files`.

**The contract tests:** from `services/api`, `PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests -v`: `Ran 49 tests`, `OK`.

**The proof** (`proofs/postgres-ordering`; the same venv and hash-locked install, exit 0): `python -m unittest discover -s tests -t . -v`: `Ran 223 tests`, `OK` (221 before: `ProfileLabelTests`' two added); `ruff check .`: `All checks passed!`; `ruff format --check .`: `59 files already formatted`; `mypy`: `Success: no issues found in 59 source files`.

**The reversals:** the twelve above, by the harness in the scratchpad (`reverse.py` with `reversals.json`; the two label reversals by a shell loop), each restoring its file and checking its SHA-256.

**Local database run: iteration, not evidence** (P06.DB's D4). Docker's daemon was started in the sandbox; the CI job's image pinned by digest (`postgres@sha256:d74eeac9…`, `postgres (PostgreSQL) 17.11 (Debian 17.11-1.pgdg13+2)`) was pulled from Docker Hub (two pulls answered `429 Too Many Requests`; the third succeeded) and published on `127.0.0.1:5433` only; the superuser's and the role's passwords, the markers, both `SECRET_KEY`s and both JWT keys were generated into a directory only the session's user could read, and never printed; a non-superuser role owned the one database, `glow_profile_proof`, with its own marker as its comment; none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or a `PG*` name was present. On the code head's tree:
- `migrate`: exit 0; `makemigrations --check --dry-run`: `No changes detected`;
- `[profile] cases: 53/53 passed in 97.5 s`; `profile secret scan: clean (1216 secrets held; 0 found in 810 log records, 130 writes and the results JSON)`; `profile value scan: clean (163 member values held: coordinates, birth dates, times and places, own words, sensitive values; 0 found in the same output)`; `PROFILE VERDICT: PASS`; the job's check (`profile_scan`): `… found in the profile suite's output: 0`, `… in the profile results JSON: 0`, `the suite's own scans (secrets, member values) reported clean: True`; the phase 98 s;
- a second run on the same database: exit 1, `refusing a used database`; the counts `108 108 92 38 978 802` before and after;
- the container, its volume, the key directory and the results JSON were removed (`docker ps -a` lists none), and the daemon stopped.

### The run of record

**Foundation push run [42908603138](https://github.com/amthorn78/glow-dating-app/actions/runs/42908603138)** on `fee4fdc5c71c54b95faa9bbb1256edee74546de3`, **the code head** (attempt 1, 21:48:33 to 21:58:42 UTC on 10 November 2026), read with the GitHub tools and the Database job's own log file. The run's conclusion was `success`; all eight jobs' conclusions were `success`, and the gate (`Foundation gate`) printed **`Application checks passed`**:

- **Change scope:** success (a branch's first push; the change is full scope: test files).
- **API checks:** success. `System check identified no issues (0 silenced).`; `manage.py test tests --verbosity 2`: **`Ran 529 tests`**, `OK`; Ruff `All checks passed!`, `133 files already formatted`; mypy `Success: no issues found in 78 source files`; the Python contract tests `Ran 49 tests`, `OK`.
- **Mobile checks, API mobile smoke, API artifact checks, Stream proof checks:** success (C3 changes no file they read; their counts were not read).
- **Database proof checks:** success, in 9 minutes 50 seconds (21:48:46 to 21:58:36) of its 30-minute timeout.
  - The offline tests **`Ran 223 tests`**, `OK`, `ProfileLabelTests`' two among them; Ruff `All checks passed!`, `59 files already formatted`; mypy `Success: no issues found in 59 source files`.
  - A wrong marker refused (`wrong-marker migrate exit status: 1`) and `dbshell` refused (`dbshell exit status: 1`).
  - **The ordering suite:** `[reference] cases: 56/56 passed`, `[adapter] cases: 115/115 passed`, `[read] cases: 62/62 passed in 17.9 s`, `== VERDICT: PASS ==`; a second run refused (`second run exit status: 1`), every count unchanged.
  - **The identity suite:** `[identity] cases: 49/49 passed in 44.4 s`; `identity secret scan: clean (754 secrets held; 0 found in 240 log records, 102 writes and the results JSON)`; `identity phase: 44 s`; a second identity run refused, the counts `53 53 63 32 50` before and after.
  - **The profile suite:** the profile database refused both other markers (`exit status 1` each); the migrations from zero and `No changes detected`; **`[profile] cases: 53/53 passed in 79.4 s`**; **`profile secret scan: clean (1216 secrets held; 0 found in 810 log records, 130 writes and the results JSON)`**; **`profile value scan: clean (163 member values held: coordinates, birth dates, times and places, own words, sensitive values; 0 found in the same output)`**; the job's own check: `the job's secrets found in the profile suite's output: 0`, `… in the profile results JSON: 0`, `the suite's own scans (secrets, member values) reported clean: True`; `PROFILE VERDICT: PASS`; **`profile phase: 80 s`**. The digests case checked `802` stored digests of `10` kinds of command.
  - **The second profile run** was refused (`second profile run exit status: 1`; `refusing a used database: auth users exist; app accounts exist; outbox events exist; a setting was published beyond its launch default. The profile suite runs once per new database.`), with the counts of auth users, app accounts, profiles, setting versions, outbox events and idempotency records **`108 108 92 38 978 802` before and after**.
  - `sv2-profile-results` (5,221 bytes) uploaded after the check passed; the container, its credential files and the marker files removed (`no proof container remains`).
- **No toolchain retry fired:** every "Wait 60 s before the one retry of the Python install (DM-41)" step and every "Retry the Python install once (DM-41)" step (API checks, API mobile smoke, Stream proof checks, Database proof checks) was `skipped`.
- **The Database job's log** (2,110 lines, searched as downloaded): no line holds the suite's coordinates at four decimals (`40.7123`, `74.0067`, `74.0068`, `34.0522`, `118.243`), the leap-day fixture date (`2008-02-29` or "February 2008"), or a private key's header. The downloaded log was deleted afterwards.

### What could not run, and the limits

- **The mobile app's checks** (`npm run check`, the export and the rendered checks) were not run locally: C3 changes no file they read; the run of record ran them. `playwright install` was not run.
- **The Database proof checks job's shell steps** were not rerun locally as a whole; the local run above follows its profile steps on one database. C3 changes neither the workflow nor the steps.
- **The ordering and identity suites** were not run locally: C3 changes no file they read.
- **The guards' limits** are item 2's.
- **Not claimed:** anything about the code beyond `01a3acb`'s, which C3 does not change; the no-deadlock reason's reliance on PostgreSQL's row locking (below, 2).

### Decisions and deviations for the manager

1. **Item 2, the lazy import in `glow_domain`:** no profile-suite case covers it, and none can, since the suite runs where `glow_profiles` is meant to load. The brief says the suite's cases cover each limit's behaviour; for this one the cover is the sealed runtime's load refusal and its dummy backend (item 2). For the new operation whose inner function is not `body`, the cover is the pinned route set and the lock cases of the existing operations; a new operation would need its own case.
2. **Item 6, the no-deadlock reason.** The sentence is recorded as the brief words it. Its reason also rests on how PostgreSQL grants row locks: a cycle could form if a writer's `FOR SHARE` request on a pointer queued behind a publication's waiting `FOR UPDATE` on it (writer A holds `profile.x` shared and asks for `consent.onboarding`; publication P1 waits for `consent.onboarding` behind writer B's share; B waits for `profile.x` behind publication P2, which waits on A). As I understand PostgreSQL's row locking, a `FOR SHARE` request on a row that holds only share locks is granted at once, without queueing behind a waiting `FOR UPDATE`, so A does not wait and no cycle forms. C3 did not test this with a case (it changes no case's behaviour); if the manager wants it shown, a profile-suite case with two publications and two writers would show it.
3. **Item 4, a second label:** `f"whole years ({years})"` printed the fixture member's age (29, 30 or 18), a value derived from the member's date, so it is changed with the fixture date's label under item 4's "no check's label holds a member value".
4. **Item 1, beyond the brief's list:** the state guard also sees `__setattr__`, `__dict__`, `vars`, and `update_or_create` or `get_or_create` with `state`, `defaults` or `**`; the stream guard also refuses `print(file=…)`, `os.write`, and imports of `warnings`, `traceback`, `faulthandler` and `pprint`; and `_binds` checks each allowlisted write's model. Each passes on `01a3acb`.
5. **The allowlist names lines** (the brief's words): an edit that moves an allowlisted line fails the state guard until the allowlist moves with it.
6. **No stop rule was met:** no file outside the owned paths changed (`glow_profiles`, `glow_domain`, `glow_identity`, `glow_chat`, `glow_api`, models, migrations, DTOs, registry entries, the workflow, locks and dependencies are all unchanged); no new check failed on `01a3acb`'s code without a temporary edit; every reversal was undone.

### Manager verification of correction C3 (App Manager 10, 10 November 2026)

**Integrated** at the merge `bfc633b` (C3's code head `fee4fdc`, records head `414d4a7`). Nothing changed on the manager branch after `e55dd81` before the merge.

**The scope:** `git diff --name-only e55dd81 414d4a7` lists five paths, each within "Stage A, correction C3"'s owned paths: the two API test files, `profile_cases.py`, the proof's `tests/test_profile_offline.py`, and the record.
- The records commit `414d4a7` holds Markdown only.
- No path outside tests changed: from `01a3acb` to `fee4fdc`, the four non-Markdown paths are tests or the profile suite.
- `profile_cases.py`'s change is two check labels and one comment. No assertion changed.
- The trusted classification, `main`'s policy run with `python3 -I` outside the tree: `"full": true`, `behavior-or-empty`, with one merge base, `df8a04c`.

**Re-runs,** in a scratch copy of `fee4fdc`, in the clean environment, with the hash-locked installs:
- **API:** `manage.py check`, no issues; `Ran 529 tests` … `OK`; Ruff clean; `133 files already formatted`; mypy `no issues found in 78 source files`.
- **Contract tests:** `Ran 49 tests` … `OK`.
- **The proof's offline tests:** `Ran 223 tests` … `OK`; Ruff clean; `59 files already formatted`; mypy `no issues found in 59 source files`.

**Three reversals of the manager's own, re-run offline.** Each was appended at the file's end, so no allowlisted line moved, and each failed its new check:
- **C3-R1:** `setattr(profile, "state", "visible")` in a new function in `staff.py`. `test_only_the_recompute_writes_a_profiles_state` fails.
- **C3-R2:** a second `logging.getLogger(…)` in `views.py`. `test_the_views_hold_one_logger_and_name_it_only_to_log` fails.
- **C3-R3:** an `AgeTransitionRefused(f"bad date {value}")` in `age.py`. `test_the_age_ports_refusals_are_codes` fails.

Each file was restored and its hash checked; the 22 guard tests then passed.

**The run of record**, read with the GitHub tools: push run 42908603138 on `fee4fdc`.
- All eight jobs `success`, and the gate printed `Application checks passed`. Every DM-41 retry step was `skipped`.
- The profile suite: `[profile] cases: 53/53 passed in 79.4 s`; both scans clean (1216 secrets and 163 member values held, 0 found); `PROFILE VERDICT: PASS`; `profile phase: 80 s`.
- The second profile run was refused, with the counts `108 108 92 38 978 802` unchanged.
- `sv2-profile-results` is 5,221 bytes, and the cleanup removed the container.

**The session's deviations:**
1. **The lazy-import limit has no profile-suite case:** the suite runs where `glow_profiles` is meant to load. The sealed-runtime test and the dummy database backend bound it instead. **Accepted.**
2. **The no-deadlock reason rests on PostgreSQL's row locking.** It assumes a `FOR SHARE` lock is granted at once while only share locks are held, even with a `FOR UPDATE` request waiting, and no case tests it. **To C3's delta review, then the Dev Manager's pre-merge read.** The review confirms the reason or refutes it; if it cannot be shown, the record should claim only what is shown. Either way, PostgreSQL detects a deadlock and aborts one transaction, so the worst case is one refused request, not a hang.
3. **Additions beyond the brief's list:** the age label, more patterns, and a model check on each allowlisted write. Each passes at `01a3acb`. **Accepted:** they are within items 1 and 4.
4. **The allowlist pins line numbers,** as the brief asked, so an edit that moves one of those lines fails the guard until the allowlist moves with it. **Accepted, as a deliberate tripwire.** It is carried to Stage B, whose sessions update the allowlist with any edit that moves an allowlisted line (the carried-items file, "Carried to SV2").
5. **Not run locally:** the mobile checks, the ordering and identity suites, and the job's shell steps as a whole. **Accepted:** C3 changes no file they read, and the run of record ran them.

## Delta review of correction C3 (code head `fee4fdc`)

- **The session:** started by Nathan from C3's delta review prompt, revision 1, at `c235b68e1081ef8c71efebd224b9d0bcbdc83272` (`docs/ephemeral/2026-11-10-sv2-stage-a-c3-delta-review-prompt.md`). It reported on 10 November 2026, and its report was relayed to App Manager 10.
- **The gates:**
  - the environment check passed, and the GitHub token names were never read;
  - the start gate passed, with one merge base, `df8a04c`, and no code differing from `fee4fdc`;
  - the trusted classification is `"full": true`, `behavior-or-empty`;
  - `git diff --name-only 01a3acb fee4fdc -- . ':!*.md'` lists exactly four paths, all tests.
- **What it ran,** in scratch copies of `fee4fdc` and `01a3acb`:
  - the API's checks (529 tests `OK`, Ruff, mypy on 78 files) and the contract tests (49);
  - the proof's offline tests (223), Ruff and mypy;
  - five reversals of its own (D1 to D4 and a label), each passing `01a3acb`'s 524 tests and failing its new check at `fee4fdc`;
  - a tripwire reversal (T1), a comment line above an allowlisted write, which fails the guard;
  - six gap probes (G1 to G6) and a label-rebinding probe;
  - informational, on a throwaway PostgreSQL 17.11 under D4: the suite 53/53 in 89.4 s, both scans clean, a second run refused, and a lock probe.
- **What it read:** push run 42908603138 on `fee4fdc` and PR43's pull-request run 42912992237 on `c235b68`. Each has all eight jobs `success` and the gate's `Application checks passed`. The PR run's profile suite passed 53/53 in 69.9 s with both scans clean, and its rerun was refused with the counts `108 108 92 38 978 802` unchanged.
- **The verdict: approve with nits.** C3 closes the full review's finding 1, (a) to (c), for every spelling the review and the brief named. Every new check fails for the edit it names, none was relaxed, and no code changed. No finding is should-fix, and none falls in a correction class.

**Its answer on the lock order** (focus 6, C3's deviation 2): **the conclusion holds, and the recorded reason is incomplete.**
- Member writers take the account row `FOR UPDATE` first, then pointers only `FOR SHARE`, in name order within each `read_shared` call.
- Publications take one pointer `FOR UPDATE` and no account row. Only the `chat.history` publication also takes `consent.onboarding` `FOR SHARE`, and no member writer or read takes `chat.history`.
- The one possible cycle is the one the session named. `set_field` holds `profile.*` and then wants `consent.onboarding` in its recompute; `save_profile` takes `consent.onboarding` and then `profile.*` in one call. A publication waits `FOR UPDATE` on each pointer.
- It does not deadlock, because PostgreSQL grants `FOR SHARE` at once on a row that holds only share locks, without queueing behind a waiting `FOR UPDATE` (`heap_lock_tuple`; `README.tuplock`). That is implementation behaviour, not the documented conflict table. The review observed it on 17.11: the exact four-transaction cycle completed with no deadlock, and a control showed that a share request behind a *held* `FOR UPDATE` does wait.
- **What the record may claim,** in the review's words: no deadlock, because publications take no account row, no member transaction reads `chat.history`, and PostgreSQL grants a share request on a share-only-locked row without queueing behind a waiting `FOR UPDATE`. That last point is implementation behaviour, observed on 17.11 by this review and not tested by a suite case. Either way the worst case is bounded: PostgreSQL's deadlock detection aborts one transaction, and `tx.run` answers it as a refused request, not a hang.
- **The Dev Manager's pre-merge read (DM-56)** found more pairs of transactions that take two pointers in opposite orders: `set_area` (`profile.location`, then `consent.onboarding` in its recompute) against `save_profile` (`consent.onboarding`, then every `profile.*`), and the owner's catalog read (`profile.*`, then `consent.onboarding` and `consent.sensitive_profile`) against `save_profile` and `set_field`. The same PostgreSQL behaviour rules out each, so the claim above stands. Were a cycle to form, PostgreSQL would abort one transaction, and `tx.run` would answer it `provider_unavailable` (503, retryable), with that transaction rolled back.

**The findings and the manager's dispositions** (step 6, rule (b): a nit is a recorded follow-up):

| # | Severity | Finding | Disposition |
|---|---|---|---|
| N1 | nit (records) | "Correction C3"'s no-deadlock reason is incomplete: "shares do not conflict" does not rule out a cycle alone, and "a publication holds one pointer `FOR UPDATE`" leaves out `chat.history`'s `FOR SHARE` on `consent.onboarding` (`settings_store.py:126`). The conclusion is right | **Recorded:** the reason above, in the review's words, is the record's claim. "Correction C3" item 6 is the session's text and is not edited; where it differs, this reason governs. To the Dev Manager's pre-merge read, with C3's deviation 2 |
| N2 | nit | The creates check reads `operations.py` only, and no check sees `bulk_create`: `Profile.objects.create(…, state=…)` in `staff.py` (G3) and a `bulk_create` upsert of `state` (G4) pass all 529 tests | **Carried to Stage B,** as a guard to widen when its sessions touch these tests (the carried-items file, "Carried to SV2") |
| N3 | nit | `_binds` reads only plain `name = …` bindings, so a profile bound by walrus, `for`, `with` or tuple unpacking in an allowlisted function satisfies the entry (G5) | **Carried to Stage B**, with N2 |
| N4 | nit | The standard-streams check does not see a file the module opens itself (`open(…).write(…)`, `Path.write_text`; G1, G2) | **Carried to Stage B**, with N2 |
| N5 | nit | The label guard trusts a name in `LABEL_NAMES` wherever it is bound, so a rebinding to a member value passes. Every current binding is safe: the review read all 17 | **Carried to Stage B**, with N2 |

**What it did not run or read:** the mobile checks, the ordering and identity suites locally, and the workflow's shell steps as a whole (both CI runs passed them). It read `profile_cases.py` and the application modules as far as the guards and the lock order need.

Nothing in the repository, on GitHub or in Notion changed.

**What follows:** the Dev Manager's pre-merge read (DM-56), then the pre-merge checklist in PR43's description, the PR run and Codex on the final head, and the merge.

## The Dev Manager's pre-merge read (DM-56)

- **The read:** Dev Manager 4's [DM-56 report](../../continuity/dev-manager/reviews/2026-11-10-dm-56-sv2-stage-a-pre-merge.md), answered at `d342f05`, a read of `e86b635` with the code head `fee4fdc`. It is integrated at `607ce47`.
- **Its run:** PR43's pull-request run 42918781989 on `e86b635` passed every job, and its gate printed `Application checks passed`. The profile suite passed 53 of 53 in 59.9 s, both scans were clean, and the second run was refused with the counts `108 108 92 38 978 802` unchanged.
- **Its verdicts:**
  - the CI policy and the workflow are as DM-54 read them;
  - the contract document and both READMEs match the code;
  - two data-model sentences claimed more than the code does, and V1 and V2 correct them;
  - Z1 to Z20 are confirmed as applied;
  - C2-1 is approved, and V3 states the order in D7;
  - the no-deadlock reason's option (a). V4, above in "Delta review of correction C3", records three more pairs of transactions that take two pointers in opposite orders. V5 carries the pointer order to Stage B's brief, with one order per transaction recommended;
  - N2 to N5's carry to Stage B is confirmed.
- **The merge:** PR43 may merge once V1 to V5 are applied as written, the pull-request run on that final head passes with `Application checks passed`, Codex raises nothing new there, and the checklist is filled in. V1 to V5 are applied as written; the review log's "DM-56" holds the dispositions.

## The merge receipt for Stage A (10 November 2026, App Manager 10)

- **PR43 merged** at 23:41:17 UTC as the merge commit `4dc2061a33c6f63e2887b11aeb2fd32d6224e23e`.
  - Its parents are `c864edd` (`main`) and `a644771` (PR43's head).
  - It merged by the expected-head guard (`expectedHeadSha` `a644771477641f89bb9075e7684e3491397f76cf`), after the pre-merge checklist in PR43's description was filled.
  - `main`'s tree equals `a644771`'s. The final head's non-Markdown paths are byte-identical to C3's code head `fee4fdc`.
- **Its checks:**
  - the trusted policy at `c864edd` read full scope (`behavior-or-empty`, 109 paths), with one merge base, `df8a04c`;
  - PR run 42923450949 on `a644771` passed all eight jobs. The gate printed `Application checks passed`. The profile suite passed 53 of 53 in 75.4 s, its secret and value scans were clean, and its phase took 77 s. A second profile run was refused with the counts `108 108 92 38 978 802` unchanged, and `sv2-profile-results` (5,206 bytes) was uploaded. Every DM-41 retry step was skipped;
  - push run 42923441007 on the same head passed, as a Markdown-only change against its parent;
  - Codex's code review of `a644771` completed at 23:29:23 UTC with no findings. All six threads on PR43 are resolved: four P1 findings and one P2 were fixed, and the P2 on a future date was answered with DM-55's ruling;
  - the reviews, corrections C1 to C3, C3's delta review and DM-52 to DM-56 are recorded above and in the review log;
  - PR43's governing Markdown, the CI policy's Database proof checks paragraph, had the Dev Manager's read before the merge: DM-54 at `93a27ea`, DM-55 for its upload sentence at `496c39e`, and DM-56 at `e86b635`, with DM-56's V1 to V5 applied as written at `a644771`.
- **The cleanup run** 42925412863 passed and deleted Stage A's four session branches, each "merged into main":
  - `claude/sv2-stage-a-impl-0qqzvj` (`f2635fa`, the implementation);
  - `claude/funny-lamport-5f2s1u` (`f54545c`, C1);
  - `claude/awesome-maxwell-wo9jxa` (`ca0ad16`, C2);
  - `claude/stoic-faraday-gist9o` (`414d4a7`, C3).

  It kept `main`, the manager branch and `claude/dev-manager` by the keep-list. The review sessions pushed no branch.
- **`git ls-remote`** after it (23:41 UTC): `main` at `4dc2061`, the manager branch at `a644771`, `claude/dev-manager` at `d342f05`, and nothing else. PR43's activity subscription is ended.
- **`main`'s push run** 42925412949 on `4dc2061`: all eight jobs passed, and the gate's log prints `Application checks passed` (completed at 23:51:40 UTC). The profile suite passed 53 of 53 in 78.8 s, with both scans clean, its phase took 80 s, and a second run was refused with the counts `108 108 92 38 978 802` unchanged. The DM-41 retry steps were skipped in the four Python jobs. It was still running when this receipt was first committed at `65a7221`.
- **The manager branch holds `main`** (11 November 2026): `main`'s merge commit `4dc2061` is merged into it at `780fb20`, so the next PR's merge base is `4dc2061`, not PR43's head (the session's git rule; DM-57 item 5). Its content is unchanged.
- **Pruned:** Stage A's eleven prompts and consultations in `docs/ephemeral/`:
  - DM-53 to DM-56's consultations;
  - the implementation prompt, C1's, C2's and C3's prompts, both exact-head review prompts and C3's delta review prompt.

  Their unique content lives in the brief, this record, the review log and the Dev Manager's reports. The nineteen links to them (twelve in the brief, four in the review log and three in this record) are pinned at `4dc2061`, where each file exists. Text that names a prompt's path, as this record's session headers do, stays true as history. DM-52's consultation stays until SV2's Stage B merges, since it consulted on the whole brief.
- **Stage A is done; SV2 continues with Stage B** (photos). Carried forward, in the carried-items file:
  - to Stage B: the pointer order (DM-56 V5), C3's allowlist pins, and the delta review's N2 to N5;
  - to P07: Z18 (a self-declared minor's earlier birth input revisions, for G-01), the adult check's upper bound, a revocation or restriction of a non-active account, `publish` taking a `system:` subject, and a restricted profile's sets;
  - to P08: Z19 (a new sensitive consent version's effect on saved values);
  - to P11 (the P11 plan): Z20 (the 405) and `IdempotencyRecord`'s account key.

  To the Dev Manager's next consultation: the confirmation that DM-56's V1 to V5 are applied.

## Stage B

SV2's Stage B, as the brief's "Stage B (revision 6)" lists it (the brief, revision 7, with DM-57's U1 to U5 and U8 to U10 as written): photos in private R2 object storage behind fixture ports (OD-62; D10), the photo requirement (D9), F05's `approve` and `reject` as the system's (D11), one pointer order in every transaction (D19), Stage A's carried guards, and the profile suite's new cases. Local database runs here are iteration, not evidence; the evidence of record is the CI run on the code head, below. Stage A's sections stand as written.

### The session

- **The prompt:** Stage B's implementation prompt, revision 1, from `854c2143d6cd8b60a546bc3d520d5f41d5316636` of `claude/magical-wozniak-yfmmx2`, started by Nathan.
- **The branch:** `claude/sweet-ramanujan-wkn311`, started at `854c214`. Its name matches `claude/**`, so the Foundation workflow runs on its pushes.
- **The code commits:**
  - `762ac74`: D19, the media policy and its seed, the models and migrations 0008 and 0009, the ports, fixture adapters and photo writers, the routes, the photo requirement, F05's registry change and its test, the API's tests, C3's allowlist and the guards for N2 to N4;
  - `42343b4`: the profile suite's eleven cases, Stage A's cases given an approved photo, `CASE_COUNT`, the plan and schema tests, and N5;
  - `d8f1bad` (**the code head**): the fixture store records each delivery reference's key, so that a reference made for the original is seen (a gap found while writing the reversals, before any push).
- **The records commit** (this section and the brief's owned records) follows the run of record, as the push rule requires.

### Start gate and environment

- **The environment check, names only.** None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` was set (the prompt's loop printed nothing), and no `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*` or `CF_*` name (`compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_)'` printed nothing). **Three AWS names were present, as DM-57 section 8 expected:** `AWS_ACCESS_KEY_ID`, `AWS_CA_BUNDLE` and `AWS_SECRET_ACCESS_KEY`, and no other `AWS_*` name. Their values were never read, printed or used, and no command passed them: every repository command ran in a clean process environment (`env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus `GLOW_ENV=test` for the API, and the proof's `PROOF_*` names for a local database run); the installs took the proxy and CA variables by reference, never printed. `GH_TOKEN` and `GITHUB_TOKEN` were present and never read.
- **The toolchain:** `Python 3.12.14` (`python3.12`; `services/api/.python-version`: 3.12.14); Node `v24.19.0` and npm `11.9.0`, both `/root/.local/bin`, first on `PATH`; `Docker version 29.9.2, build a82e528`.
- **The start gate,** each line as the prompt has it:
  - `git fetch origin claude/magical-wozniak-yfmmx2 main`: fetched (`main` at `4dc2061`; the manager branch at `854c214` itself);
  - `git switch -C claude/sweet-ramanujan-wkn311 854c214…` and `git rev-parse HEAD`: `854c2143d6cd8b60a546bc3d520d5f41d5316636`;
  - `Stage A present` (`4dc2061` is an ancestor);
  - no non-Markdown path differs from `main`'s `4dc2061`: printed nothing;
  - no owned path differs from the live manager branch: printed nothing; `854c214` is on it;
  - `grep -rn -F '"media.policy"' services/api`: printed nothing;
  - the migrations were `0001` to `0007` only;
  - `grep -c '^## Stage B'` on this record: `0`;
  - the brief's "Sessions" recorded no Stage B implementation session.
- **What was read:** the instructions, the brief (revision 7) whole, DM-57 whole, the evidence record's Stage A sections, C3 and its delta review, the media design's sources, the contract's F05 and its DTOs, the transition oracle and its tests, the data model's rows, `models.py`, Stage A's code, tests and proof, and the Database proof checks job. **DM-52 to DM-56** (about 2,700 lines) were read for this stage by a subagent of this session, which reported every passage on media, the pointer order, the guards and Stage B's carries with its line numbers; DM-56 section 6 and DM-57 were read directly. The subagent found no "Tried" list in DM-52 to DM-56; the N2 to N5 probes are in the carried-items file and in "Delta review of correction C3". OD-60, OD-61 and OD-62 were read in the register (`docs/continuity/owner-directions.md`).

### Items and acceptance checks

Each test is in `services/api/tests/` (the API's, no database), `packages/contracts/tests/`, or `proofs/postgres-ordering` (its offline tests, or the profile suite's cases on the third disposable database, through the HTTP endpoints). Each reversal is named in "The reversals", below.

| Item or check | Files | Tests | Reversals |
|---|---|---|---|
| **1. Photos (Outcome item 7; D10, OD-62)**: the media policy, the grant and its model, the ports and fixture adapters, the quarantine path with G-02's seam and the hold port, the check's approval and rejection, staff's restriction, reorder, removal and its acknowledgment, the delivery reference, F05's member routes | `glow_domain/media.py` (F05's table, the five ports, keys); `glow_domain/profile_settings.py` (`media.policy`, its schema and ceilings); `glow_profiles/media.py` (the writers and reads), `media_fixtures.py` (the adapters), `staff.py` (`restrict_media`), `contract.py`, `events.py`, `operations.py` (the reads), `views.py`, `urls.py`; `glow_persistence/models.py` (`MediaAsset`'s records, `MediaObject`, `MediaUploadGrant`); migrations 0008 and 0009 | API: `test_profile_media` (19: the table is F05's, the policy, keys and references, the fixtures, the projections, no member route to a provider, system or staff step, every state write through the table), `test_model_definitions` (0008 and 0009 pinned; the models hold only what D10 needs). Proof: `media.policy_is_development_media_1_within_ceilings`, `media.grant_within_the_policys_limits`, `media.an_upload_moves_only_through_quarantine_the_seam_and_review`, `media.an_upload_with_no_variant_passes_the_seam_and_is_rejected`, `media.completions_are_matched_to_their_grant`, `media.the_checks_decisions_are_the_systems_and_never_clear_a_restriction`, `media.removal_withholds_delivery_and_completes_on_every_objects_purge`, `media.reorder_and_every_route_refuses_another_members_photo`, `media.no_key_original_or_bytes_in_any_response` | `MEDIA.*` (2), `GRANT.*` (3), `COMPLETION.*` (4), `SEAM.*` (5), `CHECK.*` (5), `REMOVAL.*` (5), `D17.*`, `LOG.*` |
| **2. The photo requirement (D9)** | `glow_profiles/requirements.py` (`photo`), `media.py` (`run_check`, `remove_photo` end with the recompute), `staff.py` (`restrict_media` too); `contract.own_profile` (`media_ids`) | API: `test_profile_recompute` (`run_check`, `remove_photo` and `restrict_media` are `OTHER_FLOW` writers; seven photo steps are not). Proof: `media.the_photo_requirement_completes_and_its_removal_demotes`; `completion.refuses_each_missing_requirement` (a photo); every Stage A case that makes a profile `visible`, with its photo approved through Stage B's own path | `D9.*` (2) |
| **3. The registry (D11)** | `packages/contracts/production/flows-v1.json` (F05's `approve` and `reject`: `system`) | Contracts: `test_f05_quarantine_cannot_be_published_by_uploader`. API: `RegistryTests.test_the_writers_table_is_f05s_registry` | `CHECK.approve-by-a-moderator-in-the-registry` |
| **4. One pointer order (D19); check 13** | `glow_profiles/tx.py` (`Tx.pointers`), `settings_store.py` (`_hold`, `PointerOrderError`, `publish` recording its own pointer), `operations.py` (`set_field`, `set_area`, the catalog read), `staff.py` (approval without ID) | API: `test_profile_pointer_order` (the error answered `provider_unavailable`, not a refusal, and refused before its lock; a later call in order passes; a publication's own pointer held before its lock and its read; nothing outside `settings_store` locks a pointer, in the API and the proof). Proof: `pointers.one_order_in_every_transaction` (27 transactions observed: every one locked its pointers in name order, and every member and staff writer read every pointer in its first call; a lock out of order rolled the transaction back whole); every case runs under the check | `D19.*` (6) |
| **5. Carried from Stage A** | `tests/test_profile_recompute.py` (the allowlist; N2, N3), `tests/test_profiles_offline.py` (N4), `proofs/postgres-ordering/tests/test_profile_offline.py` (N5) | The allowlist: `operations.py`'s two lines moved (902 to 927, 922 to 947) and `media.py:128` (`transition`, `asset.state = after`, `MediaAsset`) added. **N2:** every `create`, `get_or_create`, `update_or_create` or `bulk_create` on a receiver naming `Profile`, and every `Profile(...)` built, anywhere in the scanned modules, is the profile edit's one create; a `bulk_create` that upserts (`update_conflicts`, `update_fields`, `unique_fields`, `**`) or builds an object with `state` is a state write. **N3:** `_binds` fails on any other binding of the written variable (unpacking, an annotated or augmented assignment, walrus, `for` or comprehension, `with`, `except`, a parameter, an import, `global`). **N4:** no `open` in any form, `write_text`, `write_bytes` or other file-making call, nor a `write` on a file the module opened, but the area table's derivation step. **N5:** every binding of a label name in the cases is pinned (`LABEL_BINDINGS`, 61), and every call of a case's helper passes its label parameters literal text or another label name (49 calls). **D16 does not apply:** `identity_support.py` is unchanged | `N2.*` (2), `N3.*` (2), `N4.*` (2), `N5.*` (2) |
| **6. The proof** | `profile_cases.py` (eleven cases; `CASE_COUNT` 53 to 64; `completion.refuses_each_missing_requirement` and `completion.every_requirement_writer_meeting_the_last_one_makes_it_visible` give their hand-built members an approved photo; `EXPECTED_PROFILE_ROUTES` gains the two media routes; `COMMAND_OPERATIONS` gains `media`); `profile_support.py` (the photo helpers, the test's own adapters, synthetic PNGs; `ready_member` approves a photo unless told not to); `tests/test_profile_offline.py` | `ProfilePlanTests` (checks 1 to 13 and D10, D19 covered; the count pinned at 64; eleven Stage B cases), `SchemaCheckCorpusTests` (the three media DTOs decided). The job's SV2 steps are unchanged | (the job's own checks) |
| **Check 11 for the new routes** | `views.py`, `urls.py` | Proof: `media.reorder_and_every_route_refuses_another_members_photo` (another member's photo `not_found` on read, removal and reorder; unauthenticated GET and POST 401; a stale collection and a stale asset version 409; a query string and an extra field 400), `media.grant_within_the_policys_limits` (a replay, another intent under the key, a stale version) | `REMOVAL.removal-by-another-owner`, `REMOVAL.reorder-with-another-owners-photo`, `D17.another-members-photo-returned` |
| **Check 12 for the new routes** | `profile_support.py` (object keys, grant references, delivery references and the start of each photo's bytes join the value ledger) | Proof: the suite's value scan (511 member values held) and the job's own check; `media.no_key_original_or_bytes_in_any_response`; `digests.keyed_and_not_reproducible_without_the_key` now checks the `media` commands' digests | `LOG.an-object-key-logged` |

**Stage A's tests changed to follow the brief,** none weakened: `test_model_definitions` (42 models, not 40; the leaf is 0009; 0007 holds every setting but the media policy), `test_profile_settings` (0007's seed and reasons are `SEEDED_BY_0007`'s; the media policy's reason is `development-media-1`), `test_profile_contract` (`MediaIntent` joins the server's request checks), `test_profiles_offline` (the two media routes; `restrict_media` and the photo operations in the lock-order test), `test_profile_recompute` (the allowlist lines; the photo writers), `test_profiles_sealed_runtime` (`glow_domain.media` sealed), the contracts' F05 test (U9), and the proof's plan and count tests (DM-57 section 5).

### The reversals (D15)

Each reversal is a temporary edit of the code head `d8f1bad`, applied once by a harness in the session's scratchpad (`reverse.py`, with `reversals.json` generated by `make_reversals.py`, which checks each anchor occurs exactly once) in a **throwaway copy** of the code head (`git archive`), never the working tree: the named tests then ran in that copy, the profile suite on a new throwaway database each (D4; iteration, not evidence), migrated from zero. Every copy was removed afterwards, and `git status` held only this records commit's files. **42 reversals; every one made its tests fail, each for the reason it names.** Notes:
- `REMOVAL.delivery-not-withheld-at-once` is stopped by the new constraint `media_delivery_only_approved`: the removal answers 409, so no reference survives it, and the cases fail at the removal.
- `LOG.an-object-key-logged` passes every case, but the suite's value scan finds the keys in its log capture (`profile value scan: FOUND`, 113 of 511 values), so the suite fails; the API's two logging guards fail too.
- `SEAM.a-variant-from-another-object` fails 45 cases: every photo is then rejected with `no_variant`, so each case that needs an approved photo fails at `the test's check approved the photo`. `SEAM.an-object-key-holds-the-account-id` fails 9, among them `media.grant_within_the_policys_limits` (`the key holds no ID`) and `media.an_upload_moves_only_through_quarantine_the_seam_and_review` (`no account ID in a key`); others fail as a member's second grant collides on the unique key.
- `CHECK.an-approval-without-the-hold-port`'s API test errors (its anchor, the hold check, is gone) rather than failing an assertion; the suite's case fails at `the approval asked the hold port first`.

| Reversal | The temporary edit | File | Failing output |
|---|---|---|---|
| `D19.set-field-pointer-dropped` | `set_field` without its added `consent.onboarding` (its first call as in Stage A) | operations.py | suite `24/64 passed`; first: `settings.pointer_read_under_lock`: `gender: answers 200` |
| `D19.set-area-pointer-dropped` | `set_area` reads `profile.location` alone first | operations.py | suite `22/64 passed`; first: `settings.pointer_read_under_lock`: `the area: answers 200` |
| `D19.staff-approval-pointer-dropped` | staff's approval without ID reads `identity.staff_approval` alone first | staff.py | suite `60/64 passed`; first: `staff.approval_gated_narrow_survives_and_is_revocable`: `approved while on` |
| `D19.catalog-read-in-two-calls` | the owner's catalog read in two calls again (`profile.*`, then both consents) | operations.py | suite `18/64 passed`; first: `settings.launch_defaults`: `the catalog: answers 200` |
| `D19.publish-own-pointer-unrecorded` | `publish` does not record its own pointer as held | settings_store.py | api: `FAIL test_a_publication_records_its_own_pointer_before_its_lock_and_its_read`: `AssertionError: Lists differ: [[]] != [['chat.history']]` |
| `D19.check-disabled` | the check never raises | settings_store.py | api: `FAIL test_a_lock_out_of_order_is_an_internal_error_answered_provider_unavailable`: `AssertionError: Lists differ: ['applied', '', '', True] != ['error', 'provider_unavailable', 'PointerOrderErro` / suite `63/64 passed`; first: `pointers.one_order_in_every_transaction`: `an error` |
| `MEDIA.ceiling-crossed-written` | `publish` writes a media publication whatever its refusals | settings_store.py | suite `62/64 passed`; first: `media.policy_is_development_media_1_within_ceilings`: `a publication above a ceiling is refused` |
| `MEDIA.bytes-ceiling-dropped-in-the-domain` | the byte ceiling dropped from the media policy's limits | profile_settings.py | api: `FAIL test_a_publication_above_each_ceiling_is_refused_naming_it`: `AssertionError: Tuples differ: () != ('media_bytes_within_ceiling',)` / suite `62/64 passed`; first: `media.policy_is_development_media_1_within_ceilings`: `a publication above a ceiling is refused` |
| `GRANT.beyond-the-policys-limits` | a grant beyond the policy's live photos issued | media.py | suite `63/64 passed`; first: `media.grant_within_the_policys_limits`: `a grant beyond the policy's limits: answers 409` |
| `GRANT.second-use-accepted` | a used grant accepts a second completion (re-adoption, no transition) | media.py | suite `63/64 passed`; first: `media.completions_are_matched_to_their_grant`: `a second completion changes nothing` |
| `GRANT.checked-against-the-current-version` | the completion checked against the current policy version, not the grant's | media.py | suite `63/64 passed`; first: `media.completions_are_matched_to_their_grant`: `adopted under the version its grant records` |
| `COMPLETION.another-keys-completion-adopted` | a completion for a key no grant names adopted by the latest pending grant | media.py | suite `63/64 passed`; first: `media.completions_are_matched_to_their_grant`: `a completion for no grant's key changes nothing` |
| `COMPLETION.oversize-adopted` | the byte-limit check removed | media.py | suite `63/64 passed`; first: `media.completions_are_matched_to_their_grant`: `an oversize completion changes nothing` |
| `COMPLETION.second-completion-changes-the-asset` | a second completion for an adopted key rewrites the original's size and entity tag | media.py | suite `63/64 passed`; first: `media.completions_are_matched_to_their_grant`: `the adopted original is unchanged` |
| `COMPLETION.a-member-route-delivers-a-provider-event` | a member route `api/v1/media/events` that calls `record_upload` | urls.py, views.py | api: `FAIL test_no_member_route_reaches_a_provider_system_or_staff_step`; `FAIL test_the_member_routes_are_served_and_no_staff_route`: `AssertionError: Items in the first set but not the second:` / suite `63/64 passed`; first: `staff.no_member_route_reaches_a_staff_operation`: `SV1's routes and SV2's only` |
| `SEAM.a-variant-from-another-object` | processing given another object's key than the adopted original's | media.py | suite `19/64 passed`; first: `settings.pointer_read_under_lock`: `the test's check approved the photo` |
| `SEAM.an-upload-with-no-variant-skips-the-seam` | the seam called only when a variant was made | media.py | suite `63/64 passed`; first: `media.an_upload_with_no_variant_passes_the_seam_and_is_rejected`: `the seam was given the original` |
| `SEAM.an-unavailable-store-rejects-the-asset` | an unavailable store treated as no variant (rejection) | media.py | suite `63/64 passed`; first: `media.an_upload_with_no_variant_passes_the_seam_and_is_rejected`: `unavailable` |
| `SEAM.the-original-referenced-for-delivery` | the delivery reference made for the original's key | media.py | suite `63/64 passed`; first: `media.an_upload_moves_only_through_quarantine_the_seam_and_review`: `the reference is the variant's only` |
| `SEAM.an-object-key-holds-the-account-id` | the original's key is the account ID's hex | media.py | suite `55/64 passed`; first: `area.coordinates_never_kept_or_echoed`: `no table holds the coordinates (outbox and idempotency records included)` |
| `CHECK.approve-by-a-moderator-in-the-registry` | F05's `approve` back to `moderator` in `flows-v1.json` | flows-v1.json | api: `FAIL test_the_writers_table_is_f05s_registry`: `AssertionError: {('up[209 chars]d', 'system'), ('reject', 'review_pending'): ([471 chars]or')} != {('up[209 ch` / contract: `FAIL test_f05_quarantine_cannot_be_published_by_uploader`: `AssertionError: 'allowed' != 'forbidden'` |
| `CHECK.decision-written-with-a-staff-subject` | the check's decisions written with a `staff:` subject | media.py | suite `61/64 passed`; first: `media.an_upload_moves_only_through_quarantine_the_seam_and_review`: `written with a system: subject` |
| `CHECK.an-approval-clears-a-staff-restriction` | the check clears the restriction record, then approves | media.py | suite `63/64 passed`; first: `media.the_checks_decisions_are_the_systems_and_never_clear_a_restriction`: `the check never clears a staff restriction` |
| `CHECK.an-approval-undoes-an-owners-removal` | the check moves a `removal_pending` asset back to review, then approves | media.py | suite `63/64 passed`; first: `media.the_checks_decisions_are_the_systems_and_never_clear_a_restriction`: `the check cannot approve a removed photo` |
| `CHECK.an-approval-without-the-hold-port` | the approval's hold check removed | media.py | api: `ERROR test_every_photo_state_write_goes_through_the_registrys_table` / suite `63/64 passed`; first: `media.an_upload_moves_only_through_quarantine_the_seam_and_review`: `the approval asked the hold port first` |
| `REMOVAL.delivery-not-withheld-at-once` | `removal_pending` keeps the delivery reference | media.py | suite `61/64 passed`; first: `media.removal_withholds_delivery_and_completes_on_every_objects_purge`: `removed: answers 200` |
| `REMOVAL.removed-before-every-objects-acknowledgment` | `purged` after the first object's acknowledgment | media.py | suite `63/64 passed`; first: `media.removal_withholds_delivery_and_completes_on_every_objects_purge`: `not removed until every object` |
| `REMOVAL.the-purge-without-the-hold-port` | the purge's hold check removed | media.py | suite `63/64 passed`; first: `media.removal_withholds_delivery_and_completes_on_every_objects_purge`: `the hold port was asked` |
| `REMOVAL.removal-by-another-owner` | `locked_asset` without the owner filter (every photo writer) | media.py | suite `63/64 passed`; first: `media.reorder_and_every_route_refuses_another_members_photo`: `removal of another owner's photo: answers 404` |
| `REMOVAL.reorder-with-another-owners-photo` | reorder's ownership check removed | media.py | suite `63/64 passed`; first: `media.reorder_and_every_route_refuses_another_members_photo`: `reorder with another owner's photo: answers 404` |
| `D9.the-checks-approval-leaves-incomplete` | the check's approval without the recompute | media.py | api: `FAIL test_every_requirement_writer_ends_with_the_recompute`: `AssertionError: [] is not true : run_check does not recompute` / suite `63/64 passed`; first: `media.the_photo_requirement_completes_and_its_removal_demotes`: `the check's approval completes it` |
| `D9.the-last-photos-removal-leaves-visible` | the removal without the recompute | media.py | suite `63/64 passed`; first: `media.the_photo_requirement_completes_and_its_removal_demotes`: `the last removal demotes` |
| `D17.another-members-photo-returned` | the asset read without the owner filter | media.py | suite `63/64 passed`; first: `media.reorder_and_every_route_refuses_another_members_photo`: `their photo: answers 404` |
| `LOG.an-object-key-logged` | the completion's key logged at `warning` | media.py | api: `FAIL test_every_logging_call_is_checked_whatever_its_receiver`; `FAIL test_nothing_but_the_views_reaches_logging_or_imports_by_name`: `AssertionError: Lists differ: ["glow_profiles/media.py:418 logging.getLogger('glow_profiles.media').warning"] ` / suite `64/64 passed`; `profile value scan: FOUND` |
| `N2.a-profile-created-outside-operations` | `Profile.objects.create(..., state='visible')` in `staff.py` | staff.py | api: `FAIL test_only_the_recompute_writes_a_profiles_state`: `AssertionError: Lists differ: [('gl[159 chars]e')"), ('glow_profiles/staff.py', '_probe', "P[86 chars]')")] !=` |
| `N2.a-bulk-create-upsert-of-state` | a `Profile` `bulk_create` upsert of `state` in `operations.py` | operations.py | api: `FAIL test_only_the_recompute_writes_a_profiles_state`: `AssertionError: Items in the first set but not the second:` |
| `N3.a-profile-bound-by-walrus` | `_invalidate_birth_input`'s `current` also bound to a `Profile` by walrus, same line | operations.py | api: `FAIL test_only_the_recompute_writes_a_profiles_state`: `AssertionError: False is not true : ('current', 'BirthInput')` |
| `N3.a-profile-bound-by-tuple-unpacking` | `_mapping_to_pending`'s `mapping` also bound to a `Profile` by tuple unpacking, same line | operations.py | api: `FAIL test_only_the_recompute_writes_a_profiles_state`: `AssertionError: False is not true : ('mapping', 'EngineIdentity')` |
| `N4.a-file-the-module-opens-itself` | `open(...).write(...)` in `operations.py` | operations.py | api: `FAIL test_no_module_writes_a_file_it_opens_itself`: `AssertionError: Items in the first set but not the second:` |
| `N4.a-path-write-text` | `Path(...).write_text(...)` in `media.py` | media.py | api: `FAIL test_no_module_writes_a_file_it_opens_itself`: `AssertionError: Items in the first set but not the second:` |
| `N5.a-label-name-rebound-to-a-member-value` | `what` bound to a fixture birth date in a case | profile_cases.py | prooftests: `FAIL test_every_binding_of_a_label_name_is_pinned`: `AssertionError: {'what': frozenset({'parameter of completed[3091 chars]8"})} != {'bumps': frozenset({'paramete` |
| `N5.a-label-parameter-passed-a-member-value` | `stays(..., what)` passed a fixture birth date | profile_cases.py | prooftests: `FAIL test_every_label_parameter_is_passed_a_label`: `AssertionError: Lists differ: ['1334: stays(what=...)'] != []` |

### The contract (D11)

- **The registry entries changed:** F05's `approve` and `reject` from `review_pending` (to `approved`, to `rejected`): `role` `moderator` to `system`, their policies (`A05`) unchanged. These are the only existing entries that change (DM-57 U9). `restrict_media` stays `moderator`.
- **Added:** none. Every transition Stage B's writers make is in F05 already: `upload_grant`, `uploaded`, `review`, `approve`, `reject`, `reorder`, `remove` from each of its five states, `purged`, `restrict_media`; an upload with no variant takes `review`, then `reject`. F04's `requirements_met` and `requirement_removed` (Stage A's) are the recompute's. The writers' table in `glow_domain/media.py` equals the registry's F05 entries, roles included (`RegistryTests`).
- **The F05 test's change** (`test_f05_quarantine_cannot_be_published_by_uploader`): its line letting `STAFF` approve is replaced. The examples now: the uploader (`forbidden`) and staff (`forbidden`) cannot approve from `review_pending`; the system with `A05` can (`allowed`), and without it is `policy_unresolved`; the system's rejection with `A05` is `allowed`, staff's and the owner's `forbidden`; an approval from `quarantined` or `removal_pending` is a `state_conflict`; the two removals and the owner's refused purge are kept.
- **No DTO changes, and none is added.** F05's member routes use `MediaIntent`, `MediaLifecycle`, `MediaUploadGrant` and `MediaCollection` as they are; `MediaUploadGrant` carries no credential (DM-57 U3). The server's `MediaIntent` check decides every corpus case of the definition, and every case one change away, as the contract's validators do (`RequestParityTests`).
- **Generated outputs:** `npm run generate --prefix packages/contracts`, run twice: the SHA-256 of each file in `apps/mobile/src/contracts/generated/` was the same before, after the first run and after the second. **No generated file changed**, since no DTO changed and the registry is not a generator input. No `apps/` path changed.
- **The README:** a Stage B bullet in "SV2 Stage A: the profile's contract". **The contract document:** F05's index row and its server mapping ("F02 to F06 on the server (SV2 Stages A and B, sealed until P11)").

### The threat model's inputs

**Every new route** (`glow_profiles/urls.py`; sealed: only the proof's `profile_urls.py` serves them). Who may call: an actor from SV1's `GlowActorAuthentication` only, as Stage A's routes. Each refuses an unauthenticated call (401 `unauthenticated`), another method (405), any query string and a body that is not its DTO (400 `invalid_request`), and another member's asset (404 `not_found`); each command refuses a stale version (409 `stale_version`) and another intent under a used key (409 `idempotency_conflict`). No refusal or log line carries a value; `Cache-Control: no-store`. Tests: `media.reorder_and_every_route_refuses_another_members_photo`, `media.grant_within_the_policys_limits`, `ProfileRoutesTests`, `RouteTests`.

| Route | Methods | Request → response | Refusals of its own |
|---|---|---|---|
| `api/v1/media` | GET, POST | `MediaIntent` → `MediaUploadGrant` (`request_upload`), `MediaLifecycle` (`remove`), `MediaCollection` (`reorder`); GET `MediaCollection` | 409 `state_conflict` (a grant beyond the live photos or the 20 entries; a reorder that is not exactly the approved set; positions exhausted); 409 `stale_version` (the collection's version for a grant or a reorder, the asset's for a removal); 404 (another member's asset in a removal or reorder); 400 (an action no member has: `approve`, `reject`, `uploaded`, `purged`) |
| `api/v1/media/<asset_id>` | GET | → `MediaLifecycle` | 404 for another member's asset |

**Every provider and system event, how it reaches the domain, and what it may change** (`glow_profiles/media.py`; no route reaches any of them; the proof calls them in process, as P11's workers will):
- `record_upload(raw)` (F05 `uploaded`, `provider`): only an event the storage adapter authenticates (`StoragePort.receive`; the fixture returns only an event it issued, unchanged; any other value is `refused`, `event_not_authenticated`). It may move its grant's asset `upload_pending` → `quarantined` and adopt the original's size and entity tag, only if no completion was adopted for the grant, the asset is `upload_pending`, the upload's time is within the grant's, and its size is within the byte limit of the policy version the grant records; anything else is `no_change` with a code (`no_grant_for_key`, `not_awaiting_upload`, `grant_expired`, `over_byte_limit`). Test: `media.completions_are_matched_to_their_grant`.
- `acknowledge_deletion(raw)` (the store's deletion of one object, `provider`): authenticated the same way. It may record one object deleted, only for an asset in `removal_pending` whose purge was requested and an object not yet recorded; the last object's acknowledgment moves the asset to `removed` (F05 `purged`). A duplicate or out-of-order one is `no_change`. Test: `media.removal_withholds_delivery_and_completes_on_every_objects_purge`.
- `review(asset_id)` (F05 `review`, `system`): only from `quarantined`. It processes the adopted original only, checked against its completion's size and entity tag and the bounds of its grant's version, writes a variant under a new key, passes G-02's seam with the variant (or the original when there is none), and moves to `review_pending`; with no variant it then rejects (`system`, `no_variant`). An unavailable store is refused `provider_unavailable` and changes nothing. A seam outcome other than review is refused (`detection_route_not_built`). Tests: `media.an_upload_moves_only_through_quarantine_the_seam_and_review`, `media.an_upload_with_no_variant_passes_the_seam_and_is_rejected`.
- `run_check(asset_id)` (F05 `approve` or `reject`, `system`): only from `review_pending` and only with no staff restriction. Approval asks the hold port first, takes the storage port's delivery reference for the variant, writes `StaffAudit` (`system:photo-check`) and ends with D9's recompute; rejection writes `StaffAudit` and the reason code. The runtime's check is `undecided`, always. Test: `media.the_checks_decisions_are_the_systems_and_never_clear_a_restriction`.
- `request_purge(asset_id)` (system): only from `removal_pending`; asks the hold port first, then asks the store to delete every object not yet acknowledged. Changes no state.
- `delivery_reference(asset_id)` (a system read for P11's delivery): an approved variant's reference only, asking the hold port first; `None` in any other state, under a restriction or a removal, or with a hold.

**Every staff operation, and how its subject reaches it:** `staff.restrict_media(asset_id, staff_subject, reason, request_id)` (F05 `restrict_media`, `moderator`): a Python call only, its subject (`staff:` and up to 200 characters of `[A-Za-z0-9._@-]`) and reason from its caller in code until P07's staff authentication, as Stage A's staff operations; a member's subject is refused. Only from `approved`: back to `review_pending`, delivery withheld, the restriction's `StaffAudit` row kept as the asset's restriction record, and D9's recompute. A used request ID is `idempotency_conflict`. No operation clears a restriction in SV2: the staff decision that closes a report is P07's. Tests: `media.the_checks_decisions_are_the_systems_and_never_clear_a_restriction`, `media.the_photo_requirement_completes_and_its_removal_demotes`.

**Every stored reference and key, what it may hold, and what removes it** (all account-private; each row cascades with the account, whose deletion is P08's; no row is deleted otherwise):

| Value | Where | What it may hold | What removes or changes it | Tests |
|---|---|---|---|---|
| Object keys (the original's, each variant's) | `MediaObject.key`, `MediaAsset.storage_ref`, `MediaUploadGrant.object_key` | 32 random hexadecimal characters (database constraints on both key columns): no account, profile or asset ID, filename or member value | never; the store's object is deleted on purge and its row records the acknowledgment | `media.grant_within_the_policys_limits`, `media.an_upload_moves…`, `KeyTests` |
| The grant's reference | `MediaUploadGrant.grant_ref` | `grant-` and 32 random hexadecimal characters; fits `PolicyVersion`, so no address | never | `KeyTests`, `media.grant…` |
| The delivery reference | `MediaAsset.approved_variant_ref` | the storage port's opaque reference for the variant (the fixture's: `delivery-` and 32 random hexadecimal characters); never a key or an address | cleared by every transition out of `approved` (restriction, removal); a constraint holds it null outside `approved` | `media.an_upload_moves…`, `media.removal…` |
| The original's size and entity tag | `MediaObject.byte_size`, `entity_tag` | the adopted completion's | never | `media.completions…` |
| The policy version | `MediaUploadGrant.policy_version` | a `media.policy` label | never | `media.completions…` |
| The revocation records | `MediaAsset.removal_requested_at`, `restriction_ref` | a time; a `StaffAudit` ID | never (P07 closes a report) | `media.the_checks_decisions…` |
| The decision evidence | `MediaAsset.review_ref`, `rejection_reason`, `detection`; `StaffAudit` | an audit ID; a code; `no_detector` | never | `media.*` |
| The store's upload credential | the fixture's memory only | a random token, scoped to one key, expiring with the grant | the process | `media.grant…`, `media.no_key_original_or_bytes_in_any_response` |
| Photo bytes | the fixture store's memory only | synthetic PNGs made by the test; synthetic variant bytes | the store's deletion | the value scan |

**The media policy's settings and ceilings** (`media.policy`; version 1 seeded by 0009, `system:launch-default`, reason `development-media-1`): types `image/png`; 1,048,576 bytes; 2,048 × 2,048; 4,194,304 declared pixels; four live photos; a 60-second grant; three transfer attempts (a client's, not counted by the server). **Ceilings in code** (a publication above one is refused, naming it, with nothing written): no type beyond PNG (`media_types_within_ceiling`), at most 1 MiB (`media_bytes_within_ceiling`), at most 4,194,304 declared pixels (`media_pixels_within_ceiling`), at most 20 live photos, the contract's collection entries (`media_live_photos_within_collection`). Schema bounds: dimensions 1 to 65,535, a grant of 1 to 3,600 seconds, 1 to 10 attempts. Tests: `MediaPolicyTests`; `media.policy_is_development_media_1_within_ceilings`.

**Each transaction's pointer locks, in order, and D19's check** (READ COMMITTED; the account row first in every writer; then the pointers `FOR SHARE`, all in the first `read_shared` call, in name order; a pointer read again later is already held):
- `save_profile`: `consent.onboarding`, the seven `profile.*`. `set_field` (changed): `consent.onboarding`, `consent.sensitive_profile`, the seven `profile.*`. `set_preferences`: `consent.sensitive_profile`, the seven `profile.*`. `set_filters` and the fields read: the seven `profile.*`. `set_area` (changed): `consent.onboarding`, `profile.location`. The catalog read (changed): `consent.onboarding`, `consent.sensitive_profile`, the seven `profile.*`. The onboarding consent, the birth input, visibility, the completion and consent reads: `consent.onboarding`. The adult check and staff's revocation: `consent.onboarding` in the recompute only. The sensitive consent: `consent.sensitive_profile`. The phone-location query: `profile.location`. Staff's approval without ID (changed): `consent.onboarding`, `identity.staff_approval`. Staff's profile restriction: none.
- **Stage B's:** `request_upload`: `media.policy`. `remove_photo`, `run_check` and `restrict_media`: `consent.onboarding`, `media.policy`. `reorder_photos`, `record_upload`, `acknowledge_deletion`, `review`, `request_purge` and the reads: none (a completion and the review read their grant's recorded version by label, `version_content`, with no lock: versions are append-only).
- **A publication:** its own pointer, recorded as held, then `FOR UPDATE`; `chat.history`'s then `consent.onboarding` `FOR SHARE`, which sorts after it.
- **The check:** `settings_store` records each transaction's pointers on its `Tx`; a lock on a pointer that sorts before a held one, and is not itself held, raises `PointerOrderError` before the lock is taken, and `tx.run` rolls the transaction back and answers `provider_unavailable` (retryable, `PointerOrderError`). Members take the account row and then pointers in this order; publications take pointers only, in this order, and no account row; so no wait cycle forms whatever PostgreSQL's queueing does (D19). Tests: `test_profile_pointer_order`; `pointers.one_order_in_every_transaction`; every case.

**Each event and what it carries** (schema `glow-profiles-1`; the asset's ID, its version and itself as the payload reference; never a value, key, reference or byte): `media_upload_granted`, `media_uploaded`, `media_in_review`, `media_approved`, `media_rejected`, `media_reordered` (one per moved photo), `media_removal_requested`, `media_purged`, `media_restricted`; and D9's `profile_completed` and `profile_demoted` from the recompute. No row an event names is deleted. Tests: the media cases count them (`media_in_review`, `media_purged`, `profile_completed`, `profile_demoted`); Stage A's `completion.each_change_emits_its_event` checks every `glow-profiles-1` event carries a reference only.

### Commands and results

**The installs** (each in the clean environment, the proxy and CA variables by reference): `services/api`: `python3.12 -m venv .venv`, `.venv/bin/python -m pip install --timeout 60 --progress-bar off --require-hashes -r requirements-dev.lock`: exit 0. `proofs/postgres-ordering`: the same with its `requirements-dev.lock`: exit 0. `npm ci --ignore-scripts` in `packages/contracts` and in `apps/mobile`: exit 0 each.

**API** (`services/api`, `GLOW_ENV=test`, at the code head `d8f1bad`):
- `python manage.py check`: `System check identified no issues (0 silenced).`
- `python manage.py test tests --verbosity 2`: `Ran 554 tests`, `OK` (529 at `854c214`; Stage B adds 25: `test_profile_media`'s 19, `test_profile_pointer_order`'s 3, two model-definition tests and the stream guard's file test).
- `python smoke.py`: `PASS /health/live: HTTP 200`, `PASS /health/ready: HTTP 503`, `PASS /api/v1/development/recommendations: HTTP 200`.
- `ruff check .`: `All checks passed!`; `ruff format --check .`: `140 files already formatted`.
- `mypy`: `Success: no issues found in 81 source files`.
- `python -m glow_persistence.static_check`: `Static definitions agree: 42 app models; migrations=0001_event_infrastructure,…,0007_settings_launch_defaults,0008_media_lifecycle,0009_media_policy_seed`.
- **Migration 0008** was generated by `makemigrations glow_persistence --name media_lifecycle` under the static registry (`glow_persistence.static_settings`, the dummy backend, inside `static_check.no_database_access()`), then formatted by Ruff; 0009 is hand-written, as 0007 is.

**The contracts:** `npm run generate --prefix packages/contracts` twice (no generated file changed: the SHA-256 of each was the same before and after both runs); `npm run check --prefix packages/contracts`: `Generated types and runtime validators match schemas.`, `tests 709`, `pass 709`, `fail 0`. From `services/api`, `PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests`: `Ran 49 tests`, `OK`.

**The mobile app:** `npm run check --prefix apps/mobile`: exit 0, `tests 691`, `pass 691`, `fail 0`, with no `apps/` path changed. Its export and rendered checks are CI's.

**The proof** (`proofs/postgres-ordering`): `python -m unittest discover -s tests -t .`: `Ran 226 tests`, `OK` (223 before: `LabelBindingTests`' three added); `ruff check .`: `All checks passed!`; `ruff format --check .`: `59 files already formatted`; `mypy`: `Success: no issues found in 59 source files`.

**Local database runs: iteration, not evidence** (P06.DB's D4). Docker's daemon was started in the sandbox; the CI job's image pinned by digest (`postgres@sha256:d74eeac9…`) was pulled from Docker Hub once (the first attempt succeeded) and published on `127.0.0.1:5433` only; the superuser's and the role's passwords, each database's marker, the `SECRET_KEY` and the JWT key were generated into a directory only the session's user could read, and never printed; a non-superuser role owned each database, each with its own marker as its comment; none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or a `PG*` name was present, and no `AWS_*` name was passed.
- the suite with Stage A's cases and the photo seeding only (53 cases): 52 of 53, the one failure the pinned route set (fixed: the two media routes);
- **the suite at `42343b4`:** `[profile] cases: 64/64 passed in 84.5 s`; `profile secret scan: clean (1381 secrets held; 0 found in 902 log records, 152 writes and the results JSON)`; `profile value scan: clean (511 member values held …; 0 found in the same output)`; `PROFILE VERDICT: PASS`; the migrations from zero and `makemigrations --check --dry-run` (`No changes detected`) before it;
- the 32 reversals with a suite run, each on its own new database (above); the unreversed cases passed in each, as their summary lines show;
- the container, its volume, the key directory and every log were removed (`docker ps -a` lists none).

**The reversals:** the 42 above, by the harness in the scratchpad, in throwaway copies of `d8f1bad`.


### The run of record

**Foundation push run [42947095725](https://github.com/amthorn78/glow-dating-app/actions/runs/42947095725)** on `d8f1bade8198c4c3f504ce9ca0a9279ef78b94bd`, **the code head** (attempt 1, 02:35:45 to 02:45:08 UTC on 11 November 2026), read with the GitHub tools: the run, its jobs and steps, and each job's log through `get_job_logs` (the Database job's last lines directly; all seven logs in full by a subagent of this session, which reported the lines below and counts of the patterns searched, never a match). The run's conclusion was `success`; all eight jobs' conclusions were `success`, and the gate (`Foundation gate`) printed **`Application checks passed`**:

- **Change scope:** success; `"full": true` (the branch's first push, so `missing-or-invalid-comparison`: full checks ran).
- **API checks:** success. The scope and branch-cleanup policies' tests (`Ran 14 tests`, `Ran 18 tests`, `OK`); `System check identified no issues (0 silenced).`; `manage.py test tests --verbosity 2`: **`Ran 554 tests`**, `OK`; `All checks passed!`, `140 files already formatted`, `Success: no issues found in 81 source files`; the Python contract tests `Ran 49 tests`, `OK`.
- **Mobile checks:** success. `Generated types and runtime validators match schemas.`; the contracts' tests `tests 709`, `pass 709`, `fail 0`; the app's `npm run check` and `check:expo`: `tests 691`, `pass 691`, `fail 0`; `export:development`; the rendered checks **`104 passed (4.6m)`**.
- **API mobile smoke, API artifact checks, Stream proof checks:** success (the Stream offline tests `Ran 648 tests`, `OK`, and `run plan: fits`; the built image's loopback smoke passed).
- **Database proof checks:** success, in **9 minutes 11 seconds** (02:35:53 to 02:45:04) of its 30-minute timeout.
  - The offline tests **`Ran 226 tests`**, `OK`; `All checks passed!`, `59 files already formatted`, `Success: no issues found in 59 source files`.
  - A wrong marker refused (`wrong-marker migrate exit status: 1`, the database unchanged, 0 relations before and after) and `dbshell` refused (`dbshell exit status: 1`).
  - **The ordering suite:** `[reference] cases: 56/56 passed`, `[adapter] cases: 115/115 passed`, `[read] cases: 62/62 passed in 14.2 s`, `== VERDICT: PASS ==`; a second run refused (`second run exit status: 1`), every count unchanged, with migrations 0008 and 0009 applied to its database.
  - **The identity suite:** `[identity] cases: 49/49 passed in 37.4 s`; `identity secret scan: clean (754 secrets held; 0 found in 240 log records, 102 writes and the results JSON)`; `IDENTITY VERDICT: PASS`; `identity phase: 38 s`; a second identity run refused, the counts `53 53 63 32 50` before and after.
  - **The profile suite:** the profile database refused both other markers (`exit status 1` each); the migrations from zero (0008 and 0009 among them) and `No changes detected`; **`[profile] cases: 64/64 passed in 81.7 s`** (64 `PASS` lines, no `FAIL`); **`profile secret scan: clean (1381 secrets held; 0 found in 902 log records, 152 writes and the results JSON)`**; **`profile value scan: clean (511 member values held: coordinates, birth dates, times and places, own words, sensitive values; 0 found in the same output)`**; the job's own check: `the job's secrets found in the profile suite's output: 0`, `… in the profile results JSON: 0`, `the suite's own scans (secrets, member values) reported clean: True`; `PROFILE VERDICT: PASS`; **`profile phase: 83 s`**. The digests case checked `986` stored digests of `11` kinds of command (`media` among them); the pointer-order case observed 27 transactions; the disclosure case found none of 223 object keys and 117 credentials in any response.
  - **The second profile run** was refused (`second profile run exit status: 1`; `refusing a used database: auth users exist; app accounts exist; outbox events exist; a setting was published beyond its launch default. The profile suite runs once per new database.`), with the counts of auth users, app accounts, profiles, setting versions, outbox events and idempotency records **`123 123 99 44 1510 986` before and after**.
  - `sv2-profile-results` (6,079 bytes) uploaded after the check passed; the container, its credential files and the marker files removed (`no proof container remains`).
- **No toolchain retry fired:** every "Wait 60 s before the one retry of the Python install (DM-41)" and "Retry the Python install once (DM-41)" step (API checks, API mobile smoke, Stream proof checks, Database proof checks) was `skipped`.
- **No secret, coordinate, key, reference or photo byte in the logs.** In all seven jobs' logs (2,135, 2,185, 2,545, 677, 319, 254 and 191 lines): no line holds any of the suite's coordinates at full or four-decimal precision, a private key's header, a `delivery-` or `grant-` reference, `fixture-variant` or a PNG signature. The only masked lines (`***`, two to four per job) are the checkout, setup-python and setup-node actions' own token inputs. The only 32-hex tokens are two Expo export bundle file names (their build content hashes) in the Mobile job's `export:development` step. No log has a `##[error]` line.

### What could not run, and the limits

- **The mobile app's export and rendered checks** were not run locally; the run of record ran them. `playwright install` was not run.
- **The Database proof checks job's shell steps** were not rerun locally as a whole; the local runs follow its profile steps on one database. Stage B changes neither the workflow nor its steps. **The ordering and identity suites** were not run locally; the run of record ran them, with migrations 0008 and 0009 applied to their databases.
- **No R2, no processor, no detector, no check vendor and no hold record exist.** The storage, processing, detection, check and hold ports have fixture adapters only; the processing fixture checks PNG framing and the policy's bounds and decodes nothing; its variant is synthetic. The test drives the check with its own adapter, and its holding and recording adapters are the test's own. PV04 owns the real path.
- **Not claimed:** the real target and its persistence; the deployed wiring; R2's events, Queues, signed upload addresses, deletion and caches (PV04, DB08); crash and restart (DB07); SV3's candidate delivery of approved photos; P07's report closure and its clearing of a restriction; G-02's detection service and G-05's hold record; a DB04-style suite case for migration 0008's new constraints (they are exercised where the cases reach them, as `REMOVAL.delivery-not-withheld-at-once` shows, but no case writes each one malformed).

### Decisions and deviations for the manager

1. **`MediaCollection.version` is derived, not stored:** 1 plus the sum of the account's asset versions. Every asset's creation and every transition bumps an asset's version, and no asset row is deleted, so it starts at 1 and advances with every adopted transition and order change (P04.3's semantics) with no new column.
2. **A grant's time is judged by the store's upload time:** a completion is adopted only if its reported upload time is not after the grant's expiry, and `used_at` records that time (a constraint holds it within the grant). A completion processed later, for an upload made in time, is still adopted. The completion event is the adapter's, authenticated.
3. **"Live photos" are `upload_pending`, `quarantined`, `review_pending` and `approved`;** a rejected or removed photo frees a place. The collection's 20 entries (every state but `removed`) are a second limit at the grant.
4. **No operation clears a staff restriction in SV2.** The brief's words leave it to "the staff decision that closes the report", which is P07's; a restricted photo stays in `review_pending`, and the check passes it by (`restricted`).
5. **The hold port is asked at the purge's request,** before the store is asked to delete, not again at each object's acknowledgment: by then the object is deleted, and the record says so.
6. **The store's upload credential is issued inside the grant's transaction** (the fixture's in memory), and the purge's deletion request inside the purge's. P11 decides where a real adapter's calls go relative to the commit (the data model's "work only after commit").
7. **The check's rejection reason** from its port is stored only when it is a code (`[a-z_]{1,64}`); otherwise `rejected`.
8. **A variant's object row holds its size and no entity tag;** only an original's adoption records an entity tag (`media_object_adoption_evidence`).
9. **The fixture authenticates events by identity:** it returns only an event it issued itself, unchanged. No key is generated for it.
10. **`delivery_reference`** is a system read with no route, for P11's delivery; the owner's own `MediaLifecycle` shows an approved photo's reference whatever a hold says, since the DTO requires one while `approved` and a hold is not a state.
11. **New database constraints** on `MediaAsset` (`media_delivery_only_approved`, `media_approved_unrevoked`, `media_removal_record`, `media_seam_passed`), `MediaObject` and `MediaUploadGrant` back the writers' rules. A filename or other non-hexadecimal key cannot be stored, so the key reversal uses the account ID's hex.
12. **`FIXED_LIMITS` gains the four media ceilings,** and `ALL_SETTINGS` the media policy, with `SEEDED_BY_0007` naming 0007's fourteen; Stage A's seed tests now compare 0007 with those fourteen.
13. **The fixture store records each delivery reference's key** (`d8f1bad`), added after the reversal harness showed a reference made for the original would otherwise go unseen.
14. **N5's pin** holds a long binding by its first 48 characters and its whole text's SHA-256, to keep lines readable.
15. **DM-52 to DM-56 were read through a subagent** of this session for their Stage B content (above); DM-57 and DM-56 section 6 directly.
16. **No stop rule was met:** no path outside the owned paths changed (`glow_api`, `glow_chat`, `glow_identity`, `apps/`, `scripts/`, the workflow, the `Dockerfile`, environment templates, requirement files and the CI policy are unchanged); no dependency or pin changed; no provider, R2, Cloudflare or other service was called and no credential used; no DTO changed and no registry entry but F05's `approve` and `reject`; every role is one the oracle authorizes; the served runtime imports none of the new code (`test_profiles_sealed_runtime`); `glow_chat`'s writers are called unchanged.

### Manager verification of Stage B (App Manager 10, 11 November 2026)

**The diff.** `git diff 854c214 e7d6616` (the prompt's start to the records head) was read for its scope, and in part for its content. It has 35 paths, each owned by the brief, revision 7. Of these, 29 are non-Markdown files (+4,219 lines, −65) at the code head `d8f1bad`, and 19 of those are outside the tests (+2,935). The other six are the Markdown files in the records commit `e7d6616`.
- **Unchanged:** `glow_api`, `glow_chat`, `glow_identity`, `apps/`, `scripts/`, `.github/`, the `Dockerfile`, every environment template, requirement file and dependency lock. No generated contract output and no DTO changed.
- **The registry:** the only lines changed in `flows-v1.json` are F05's `approve` and `reject` roles, `moderator` to `system` (OD-61).
- **D19:**
  - `settings_store._hold` records each pointer on the transaction's `Tx`, and raises `PointerOrderError` when a held name sorts after the new one.
  - `read_shared` (`FOR SHARE`) and `publish` (`select_for_update`) are the only pointer lock sites. No module outside `settings_store` locks a `PolicyRevision` row.
  - `tx.run` refuses nesting, so each transaction has one `Tx`.
- **Read against D10:**
  - object keys are opaque hex;
  - a completion is adopted once, within its grant's expiry and the byte limit of the grant's own policy version;
  - processing happens at `review`, and an upload with no variant passes the seam with its original and is rejected (`no_variant`);
  - the hold port is asked before approval, delivery and purge;
  - `removed` follows the acknowledgment of every object;
  - delivery is only of an approved, unrestricted, unremoved, unheld variant.

**Classification.** The trusted classifier from `main` (`4dc2061`; byte-identical to `main`'s `scripts/change_scope.py`) ran with `python3 -I` and `--base 4dc2061… --head e7d6616… --merge-base`, after the fast-forward. It returned:
- full scope, `behavior-or-empty`;
- the PR's whole diff (58 paths), the manager's records since PR43 included;
- one merge base, `4dc2061`.

**Re-runs.** These ran in a scratch copy of the code head's whole tree (`git archive d8f1bad`), in the clean environment, with hash-locked installs:
- **API:** `Found 554 test(s)` … `OK`; `System check identified no issues (0 silenced).`; Ruff `All checks passed!`; `140 files already formatted`; mypy `no issues found in 81 source files`; the static check agreed.
- **The proof's offline tests:** `Ran 226 tests` … `OK`; mypy `no issues found in 59 source files`.

The manager runs no database test locally.

**Reversals, re-run offline.** Each was applied in the scratch copy, and the file was restored afterwards. Each ran against `tests.test_profile_pointer_order` and `tests.test_profile_media` (22 tests):
- **M1:** `_hold`'s raise removed. `test_a_lock_out_of_order_is_an_internal_error_answered_provider_unavailable` fails (`FAILED (failures=1)`).
- **M2:** the review calls the seam only when processing made a variant. The two modules pass (`Ran 22 tests`, `OK`), so no offline test sees it.
  - The session's `SEAM.an-upload-with-no-variant-skips-the-seam` shows the profile suite's case `media.an_upload_with_no_variant_passes_the_seam_and_is_rejected` failing at `the seam was given the original` (`profile_cases.py:3119`).
  - That result comes from a local database run, which is iteration, not evidence.
- **M3:** the approval's hold check removed. Only `test_every_photo_state_write_goes_through_the_registrys_table` errors, because its anchor is gone, as the session recorded for `CHECK.an-approval-without-the-hold-port`. No offline assertion is on the hold. The suite's case fails at `the approval asked the hold port first` (`profile_cases.py:3074`).

After the restore, both files' SHA-256 matched `d8f1bad`'s, and the 22 tests pass. For the seam's no-variant path and the approval's hold, the profile suite on PostgreSQL is the only check that asserts the behaviour. The run of record ran both cases and passed. This goes to the exact-head review as a coverage note, not as a defect.

**The run of record,** read with the GitHub tools: push run 42947095725 on `d8f1bad`.
- All eight jobs were `success`, and every DM-41 retry step was `skipped`.
- The Database proof checks job:
  - the profile database refused both other markers;
  - migrations 0008 and 0009 applied from zero, and `No changes detected`;
  - `[profile] cases: 64/64 passed in 81.7 s`, with `profile secret scan: clean (1381 secrets held; 0 found in 902 log records, 152 writes and the results JSON)` and `profile value scan: clean (511 member values held …)`;
  - `PROFILE VERDICT: PASS`, and `profile phase: 83 s`.
- The second profile run was refused (`exit status: 1`), with the counts `123 123 99 44 1510 986` unchanged.
- `sv2-profile-results` is 6,079 bytes, and `no proof container remains`.

The records push run 42949445496 on `e7d6616` passed. Change scope and the gate were `success`, and the six application jobs were `skipped`: the change since the code head is ordinary documentation.

**The session's sixteen decisions:**
- **To the Dev Manager (DM-58):**
  - 1: the collection's version is derived;
  - 2: a grant's expiry is judged by the store's upload time;
  - 3: `removed` photos are outside the collection's 20 entries and its read, where P04.3 kept removed tombstones within that bound (`private-media-fixtures.md`, "Provisional development policy and byte checks");
  - 6: the store's calls are made inside the transaction, where the data model's unit-of-work table puts provider work after commit;
  - 10: the owner's `MediaLifecycle` shows an approved photo's reference whatever a hold says.
- **Settled here:**
  - 4 follows D10's words and the carried item for P07 (`carried-to-later-items.md`: a photo's restriction is cleared only by the staff decision that closes the report);
  - 5 follows the brief's check list ("approval, delivery and a removed asset's purge each ask the hold port first");
  - 7, 8, 9 and 11 to 16 are within the brief, and each is recorded above.

**Codex on `82d246b`** (PR44's first head, opened at that commit): its code review completed at 03:19:45 UTC with one P2 finding, "Allow media purge to finish for inactive accounts" (`media.py`, `request_purge`). Confirmed: `request_purge` and `acknowledge_deletion` lock the owner's account row with `lock_account`, which refuses an account that is not `active`, so a photo removed before its owner is suspended or asks for deletion stays `removal_pending`, with its objects kept; delivery stays withheld. No test covers it. The fix changes the account-state gate on F05's system steps, so it goes to the Dev Manager as DM-58's item 9 ([addendum](https://github.com/amthorn78/glow-dating-app/blob/3240ef0acca7983e5b60b9a111be371ed5a16b74/docs/ephemeral/2026-11-11-dm-58-addendum-inactive-owner-purge.md)); its thread stays open until the disposition.

## Stage B, correction C1

SV2 Stage B's correction C1, as the brief's "Stage B, correction C1 (DM-58 item 9)" lists it (the brief, revision 8; DM-58 section 3): Codex's P2 on PR44 (`82d246b`), an inactive owner's purge refused by the account-state gate. Stage B's sections stand as written. Local database runs here are iteration, not evidence; the evidence of record is the CI run on the code head, below.

### The session

- **The prompt:** Stage B correction C1's prompt, revision 1, from `ecad10c797b56d724c6039cc771717f6ccfad6e9` of `claude/magical-wozniak-yfmmx2`, started by Nathan.
- **The branch:** `claude/gracious-davinci-lpqt02`, started at `ecad10c`. Its name matches `claude/**`, so the Foundation workflow runs on its pushes.
- **The code commit, the code head:** `7538c7642f38ac374f2a0f7ca22c8887a3a31922` (`7538c76`): items 1 and 2.
- **The records commit** (this section, the data model's `MediaAsset` row, the contract document's F05 server mapping and the proof README) follows the run of record, as the push rule requires.

### Start gate and environment

- **The environment check, names only.**
  - None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` was set (the prompt's loop printed nothing).
  - No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*` or `CF_*` name (`compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_)'` printed nothing).
  - **Three AWS names were present, as DM-57 and DM-58 expected:** `AWS_ACCESS_KEY_ID`, `AWS_CA_BUNDLE` and `AWS_SECRET_ACCESS_KEY`, and no other `AWS_*` name. Their values were never read, printed or used, and no command passed them.
  - `GH_TOKEN` and `GITHUB_TOKEN` were present and never read.
  - Every repository command ran in a clean process environment (`env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus `GLOW_ENV=test` for the API, and the proof's `PROOF_*` names and `DJANGO_SETTINGS_MODULE` for a local database run); the installs, Docker's daemon and its one pull took the proxy and CA variables by reference, never printed.
- **The toolchain:** `Python 3.12.14` (`python3.12`); Node `v24.19.0` and npm `11.9.0`, both `/root/.local/bin` (`which node` and `which npm` resolve there; the first `PATH` entry is the Nix profile, which holds neither); `Docker version 29.9.2, build a82e528`.
- **The start gate,** each line as the prompt has it:
  - `git fetch origin claude/magical-wozniak-yfmmx2 main`: fetched (`main` at `4dc2061`; the manager branch at `ecad10c` itself);
  - `git switch -C claude/gracious-davinci-lpqt02 ecad10c…` and `git rev-parse HEAD`: `ecad10c797b56d724c6039cc771717f6ccfad6e9`; `e7d6616` is an ancestor;
  - no non-Markdown path differs from `d8f1bad`: printed nothing;
  - no owned path differs from the live manager branch: printed nothing; `ecad10c` is on it;
  - `grep -rn 'lock_account_any_state' services/api proofs`: printed nothing;
  - `grep -c '^## Stage B, correction C1'` on this record: `0`; on the brief, `'^## Stage B, correction C1 (DM-58 item 9)'`: `1`.
- **What was read:** the root `AGENTS.md` and `CLAUDE.md`, `services/api/README.md` and `proofs/postgres-ordering/README.md`; the brief, revision 8: D10's bullet on reorder and removal, acceptance check 10 and "Stage B, correction C1 (DM-58 item 9)"; DM-58 sections 3 and 7; this record's "Stage B" and "Manager verification of Stage B", with Codex's finding; `glow_profiles/tx.py` and `glow_profiles/media.py` whole; `glow_chat/contact.py`'s `suspend`, `delete` and `_revoke_account`; the tests changed, below.

### Items

| Item | Files | Checks | Reversals |
|---|---|---|---|
| **1. The two writers** | `glow_profiles/tx.py`: `lock_account_any_state`, beside `lock_account`, which is unchanged: the account row `FOR UPDATE`, an absent row refused `not_found` / `account_missing`, `after_first_lock` signalled, no state check; the module docstring states the rule. `glow_profiles/media.py`: `request_purge` and `acknowledge_deletion` call it first, in place of `lock_account`; the purge still asks the hold port before the store; both docstrings and the module docstring state the rule. No other lock changed | API: `LockOrderTests` (three tests), `AccountStateTests` (three). Proof: the three cases below | `C1.the-purge-gated`, `C1.the-acknowledgment-gated`, `C1.the-any-state-lock-checks-the-state`, `C1.the-purge-without-the-hold-port` |
| **2. The tests** | `tests/test_profiles_offline.py`; `tests/test_profile_media.py`; `profile_cases.py` (three cases, `CASE_COUNT` 64 to 67); `tests/test_profile_offline.py` (the count pinned at 67; Stage B's cases counted 14) | Below | `C1.review-ungated`, and those of item 1 |
| **3. The records** | `docs/architecture/data-model.md` (the `MediaAsset` row); `docs/architecture/production-contracts.md` (F05's server mapping, "The account's state"); `proofs/postgres-ordering/README.md` (the profile suite's paragraph: 67 cases, Stage A's 53, Stage B's eleven by name and C1's three); this section | Read against the code at `7538c76` | (records) |

**The tests, item 2:**
- **`LockOrderTests`** (`tests/test_profiles_offline.py`):
  - `test_every_operation_takes_the_account_row_first`: its expectation changes as the brief says. `ANY_STATE` (`request_purge`, `acknowledge_deletion`) must begin with `lock_account_any_state(tx, account_id)`; every other command, staff operation, system step and read keeps `lock_account(tx, account_id)` or `read_account_shared(tx, account_id)`, as before. Nothing else in it changes.
  - New: `test_only_the_two_writers_take_the_account_row_in_any_state`: in every module of `services/api` but its tests and `.venv`, the name is used only in `media.py`'s `request_purge` and `acknowledge_deletion`, once each, and imported only by `media.py`.
  - New: `test_the_any_state_lock_is_lock_account_without_its_state_check`: its statements are `lock_account`'s first three and `return account`; `lock_account`'s are those three, the `account_not_active` refusal and `return account`.
- **`AccountStateTests`** (`tests/test_profile_media.py`, new): the purge begins with the any-state lock and asks `adapters.hold.held` once, before `adapters.storage.delete` and before `purge_requested_at` is set; the acknowledgment begins with it and records a deletion only for a `removal_pending` asset whose purge was requested; every other photo step's first statement is `lock_account` or `read_account_shared`. The purge's hold check had no offline assertion before (it was the suite's only); it has one now.
- **The suite's three cases** (`profile_cases.py`; checks 10 and D10; the owner is made inactive with `glow_chat`'s `OrmContactPersistence(provider="fixture").suspend` or `.delete`, called unchanged):
  - `media.a_photo_removed_before_its_owner_is_suspended_is_still_purged`: an approved photo (two objects) removed, delivery withheld at once; the owner suspended; a hold still stops the purge, with nothing deleted; the purge is asked, the hold port asked first, every object's deletion asked; one acknowledgment leaves it `removal_pending`, the last makes it `removed` (`media_purged` once, every object acknowledged); the account stays `suspended`. **Delivery is checked withheld at each step** (`_withheld`: the row holds no delivery reference, and `delivery_reference` returns none: it refuses an owner who is not active).
  - `media.a_purge_asked_before_its_owner_asks_for_deletion_completes`: an approved photo removed; the purge asked while the owner is active; then the owner asks for deletion (`deletion_pending`, with its `DeletionJob`); the first acknowledgment leaves it `removal_pending`, a duplicate changes nothing (`already_deleted`), the last makes it `removed`; delivery withheld throughout; the account stays `deletion_pending`.
  - `media.every_other_photo_step_refuses_an_inactive_owner`: for a suspended owner and for one who asked for deletion, each with an upload pending, one quarantined, one in review and one approved: `record_upload`, `review`, `run_check` (the test's approving check never asked), staff's `restrict_media` and `delivery_reference` each answer `refused` / `forbidden` / `account_not_active`; the grant stays unused, and the counts, the objects and each asset's state and version are unchanged. Staff's restriction and the delivery read are beyond the three the brief names; they check the same rule (deviation 4).
- **`CASE_COUNT`** becomes 67 (`profile_cases.py`), with `test_the_case_count_is_pinned` (64 to 67) and `test_the_plan_covers_every_acceptance_check`'s count of Stage B's `media` and `pointers` cases (11 to 14). These are the two expectations the brief changes; no test was weakened or removed.
- **C3's state-write guard** (the allowlist in `tests/test_profile_recompute.py`, `NOT_A_PROFILES_STATE`) pins `media.py:128` (`transition`, `asset.state = after`). C1 does not move it (deviation 1), so the allowlist is unchanged.

### The reversals (D15)

Each reversal is a temporary edit of the working tree at the code commit `7538c76`, applied by a harness in the session's scratchpad (`reverse.py`; each anchor checked to occur exactly once). For each: the API's `LockOrderTests`, `AccountStateTests` and `test_profile_recompute` (11 tests), then the profile suite on a new throwaway database (D4; iteration, not evidence), migrated from zero; then the file restored with `git checkout HEAD --`, and **every file's SHA-256 checked equal to the commit's** (`media.py` `491c734b…afc8ce3d`, `tx.py` `14c6141e…f707f70`, after every reversal). Each made its tests fail, for the reason it names.

| Reversal | The temporary edit | File | Failing output |
|---|---|---|---|
| `BASE.the-code-at-d8f1bad` (the stop rule's check) | `tx.py` and `media.py` as at `d8f1bad` | both | api `FAILED (failures=5, errors=1)`: `LockOrderTests` (`request_purge`, `acknowledge_deletion`: `'lock_account(tx, account_id)' != 'lock_account_any_state(tx, account_id)'`; the any-state lock used nowhere; its definition absent: `KeyError`, an error), `AccountStateTests` (both writers). Suite `65/67 passed`: `media.a_photo_removed_before_its_owner_is_suspended_is_still_purged`: `a hold stops the purge`; `media.a_purge_asked_before_its_owner_asks_for_deletion_completes`: `one object acknowledged after the deletion request`. `media.every_other_photo_step_refuses_an_inactive_owner` **passes**, as it should on the gated code. Every failure is item 1's |
| `C1.the-purge-gated` | `request_purge` begins with `lock_account` again | media.py | api `FAILED (failures=3)`: `LockOrderTests` (`request_purge`; the any-state lock's users), `AccountStateTests` (the purge). Suite `66/67 passed`: `media.a_photo_removed_before_its_owner_is_suspended_is_still_purged`: `a hold stops the purge` (the suspended owner's purge refused before the hold port is asked) |
| `C1.the-acknowledgment-gated` | `acknowledge_deletion` begins with `lock_account` again | media.py | api `FAILED (failures=3)`: `LockOrderTests` (`acknowledge_deletion`; the users), `AccountStateTests` (the acknowledgment). Suite `65/67 passed`: the suspension case at `one object acknowledged for a suspended owner`; the deletion case at `one object acknowledged after the deletion request` |
| `C1.review-ungated` | `review` begins with `lock_account_any_state` | media.py | api `FAILED (failures=3)`: `LockOrderTests` (`review`: `'lock_account_any_state(tx, account_id)' != 'lock_account(tx, account_id)'`; the users), `AccountStateTests.test_every_other_photo_step_keeps_its_gate` (`review`). Suite `66/67 passed`: `media.every_other_photo_step_refuses_an_inactive_owner`: `review refuses an inactive owner` |
| `C1.the-any-state-lock-checks-the-state` | `lock_account_any_state` refuses an account that is not active | tx.py | api `FAILED (failures=1)`: `test_the_any_state_lock_is_lock_account_without_its_state_check`. Suite `65/67 passed`: both purge cases, as for the code at `d8f1bad` |
| `C1.the-purge-without-the-hold-port` | `request_purge`'s hold check removed | media.py | api `FAILED (failures=1)`: `AccountStateTests` (the purge: `0 != 1`). Suite `64/67 passed`: Stage B's `media.removal_withholds_delivery_and_completes_on_every_objects_purge` (`the hold port was asked`) and both purge cases (`a hold stops the purge`; `the purge asked the hold port first`) |

The brief's reversals are all here: the gate restored in each writer fails its case and `LockOrderTests`; `lock_account_any_state` in `review` fails the third case.

### Each F05 step's account-state rule after C1 (for the exact-head review's threat model)

Every step is one `tx.run` transaction that takes the photo owner's `AppAccount` row first (DM-13 4.1). An absent row is `not_found` / `account_missing` everywhere.

- **In any account state** (`lock_account_any_state`, the row `FOR UPDATE`; `active`, `suspended`, `deletion_pending` or any other):
  - `request_purge(asset_id)` (system): only from `removal_pending`; asks the hold port first (a hold stops it, `held`), then asks the store to delete every object not yet acknowledged, and sets `purge_requested_at`;
  - `acknowledge_deletion(raw)` (F05 `purged`, `provider`, authenticated by the storage adapter): records one object deleted only for a `removal_pending` asset whose purge was requested; the last object's acknowledgment moves it to `removed`.
  - `glow_chat`'s `suspend` and `delete` take the same row `FOR UPDATE`, so either serializes with these two. Neither changes the account.
- **Refuse an account that is not `active`** (`forbidden` / `account_not_active`):
  - the member's commands, through `MediaIntent` at `api/v1/media` (the actor class refuses an inactive account first, and each also takes `lock_account`): `request_upload`, `remove_photo`, `reorder_photos`;
  - the member's reads (`api/v1/media`, `api/v1/media/<asset_id>`): `operations.read`, `read_account_shared` (the row `FOR SHARE`);
  - the provider's completion: `record_upload` (`lock_account`);
  - the system's steps: `review` and `run_check` (`lock_account`);
  - staff's `restrict_media` (`lock_account`);
  - the system read `delivery_reference` (`read_account_shared`).
- Tests: `LockOrderTests`, `AccountStateTests`; the three cases above; Stage B's media cases for the active owner.

### Commands and results

**The installs** (each in the clean environment, the proxy and CA variables by reference): `services/api`: `python3.12 -m venv .venv`, `.venv/bin/python -m pip install --timeout 60 --progress-bar off --require-hashes -r requirements-dev.lock`: exit 0. `proofs/postgres-ordering`: the same with its `requirements-dev.lock`: exit 0. No npm install was needed: no contract, generated output or `apps/` path changed.

**API** (`services/api`, `GLOW_ENV=test`, at `7538c76`):
- `python manage.py check`: `System check identified no issues (0 silenced).`
- `python manage.py test tests --verbosity 2`: `Ran 559 tests`, `OK` (554 at `d8f1bad`; C1 adds 5: `LockOrderTests`' two and `AccountStateTests`' three).
- `ruff check .`: `All checks passed!`; `ruff format --check .`: `140 files already formatted`.
- `mypy`: `Success: no issues found in 81 source files`.
- `python -m glow_persistence.static_check`: `Static definitions agree: 42 app models` (no model or migration changed).

**The contracts** (from `services/api`): `PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests -v`: `Ran 49 tests`, `OK`.

**The proof** (`proofs/postgres-ordering`): `python -m unittest discover -s tests -t . -v`: `Ran 226 tests`, `OK` (the same count; two expectations changed); `ruff check .`: `All checks passed!`; `ruff format --check .`: `59 files already formatted`; `mypy`: `Success: no issues found in 59 source files`.

**Local database runs: iteration, not evidence** (P06.DB's D4):
- Docker's daemon was started in the sandbox; the CI job's image pinned by digest (`postgres@sha256:d74eeac9…`) was pulled from Docker Hub once and published on `127.0.0.1:5433` only.
- The superuser's and the role's passwords, each database's marker, the `SECRET_KEY`s and the JWT keys were generated into directories only the session's user could read (mode 700, files 600), and never printed. A non-superuser role owned each database, each new database had its own marker as its comment, and each was dropped after its run.
- None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or a `PG*` name was present, and no `AWS_*` name was passed.
- **The suite at `7538c76`:** migrations from zero (exit 0), `No changes detected`; `[profile] cases: 67/67 passed in 86.3 s`; `profile secret scan: clean (1425 secrets held; 0 found in 910 log records, 158 writes and the results JSON)`; `profile value scan: clean (535 member values held: coordinates, birth dates, times and places, own words, sensitive values; 0 found in the same output)`; `PROFILE VERDICT: PASS`; the job's check (`profile_scan`): `0`, `0`, `True`.
- The six reversal runs above, each on its own new database.
- The container, its volume, the key directories and every log were removed (`docker ps -a` lists none).

### The run of record

**Foundation push run [42957799823](https://github.com/amthorn78/glow-dating-app/actions/runs/42957799823)** on `7538c7642f38ac374f2a0f7ca22c8887a3a31922`, **the code head**.
- **When:** attempt 1, 04:13:22 to 04:21:38 UTC on 11 November 2026.
- **How it was read:** with the GitHub tools: the run, its jobs and steps, the Database job's last lines directly, and all eight logs in full through `get_job_logs` (content, never a download address) by a subagent of this session. The subagent reported the lines below and counts of the patterns searched, never a match.
- **The result:** the run's conclusion was `success`, all eight jobs' conclusions were `success`, and the gate (`Foundation gate`, 04:21:36 to 04:21:38) printed **`Application checks passed`**. The jobs:

- **Change scope:** success; `{"full": true, "reason": "missing-or-invalid-comparison", "paths": []}` (the branch's first push): full checks ran.
- **API checks:** success (04:13:33 to 04:14:30). The scope and branch-cleanup policies' tests (`Ran 14 tests`, `Ran 18 tests`, `OK`); `System check identified no issues (0 silenced).`; `manage.py test tests --verbosity 2`: **`Ran 559 tests`**, `OK`; `All checks passed!`, `140 files already formatted`, `Success: no issues found in 81 source files`; the Python contract tests `Ran 49 tests`, `OK`.
- **Mobile checks:** success (04:13:33 to 04:21:34). `Generated types and runtime validators match schemas.`; the contracts' tests `tests 709`, `pass 709`, `fail 0`; the app's `npm run check` and `check:expo`: `tests 691`, `pass 691`, `fail 0`; the rendered checks **`104 passed (5.3m)`**.
- **API mobile smoke, API artifact checks, Stream proof checks:** success. The smoke's `PASS: spawned loopback API -> mobile TypeScript client; …`; `built-image loopback smoke passed`; the Stream offline tests `Ran 648 tests`, `OK`, and `run plan: fits`.
- **Database proof checks:** success, in **6 minutes 18 seconds** (04:13:33 to 04:19:51) of its 30-minute timeout.
  - The offline tests **`Ran 226 tests`**, `OK`; `All checks passed!`, `59 files already formatted`, `Success: no issues found in 59 source files`.
  - A wrong marker refused (`wrong-marker migrate exit status: 1`, 0 relations before and after) and `dbshell` refused (`dbshell exit status: 1`).
  - **The ordering suite:** `[reference] cases: 56/56 passed`, `[adapter] cases: 115/115 passed`, `[read] cases: 62/62 passed in 10.7 s`, `== VERDICT: PASS ==`. A second run was refused (`second run exit status: 1`), every count unchanged.
  - **The identity suite:** `[identity] cases: 49/49 passed in 30.0 s`; `identity secret scan: clean (754 secrets held; 0 found in 240 log records, 102 writes and the results JSON)`; `IDENTITY VERDICT: PASS`; `identity phase: 31 s`. A second identity run was refused, with the counts `53 53 63 32 50` before and after.
  - **The profile suite:**
    - the profile database refused both other markers (`exit status 1` each); the migrations from zero and `No changes detected`;
    - **`[profile] cases: 67/67 passed in 55.6 s`**, C1's three among them (`media.a_photo_removed_before_its_owner_is_suspended_is_still_purged`, `media.a_purge_asked_before_its_owner_asks_for_deletion_completes`, `media.every_other_photo_step_refuses_an_inactive_owner`: `10 steps refused for a suspended and a deleting owner (account_not_active)`);
    - **`profile secret scan: clean (1425 secrets held; 0 found in 910 log records, 158 writes and the results JSON)`** and **`profile value scan: clean (535 member values held: coordinates, birth dates, times and places, own words, sensitive values; 0 found in the same output)`**;
    - the job's own check: `the job's secrets found in the profile suite's output: 0`, `… in the profile results JSON: 0`, `the suite's own scans (secrets, member values) reported clean: True`;
    - `PROFILE VERDICT: PASS`; **`profile phase: 56 s`**;
    - the digests case checked `998` stored digests of `11` kinds of command; the pointer-order case observed 27 transactions; the disclosure case found none of 239 object keys and 127 credentials in any response.
  - **The second profile run** was refused (`second profile run exit status: 1`; `refusing a used database: auth users exist; app accounts exist; outbox events exist; a setting was published beyond its launch default. The profile suite runs once per new database.`), with the counts of auth users, app accounts, profiles, setting versions, outbox events and idempotency records **`127 127 99 44 1550 998` before and after**.
  - `sv2-profile-results` (6,259 bytes) was uploaded after the check passed; the container, its credential files and the marker files were removed (`no proof container remains`).
- **No toolchain retry fired:** every "Wait 60 s before the one retry of the Python install (DM-41)" and "Retry the Python install once (DM-41)" step was `skipped`, in API checks, API mobile smoke, Stream proof checks and Database proof checks.
- **No secret, key, reference or photo byte in the logs.** The eight jobs' logs hold 192, 2,137, 2,545, 677, 319, 2,190, 256 and 79 lines. None holds a private key's header, a `delivery-` or `grant-` reference, `fixture-variant` or a PNG signature. No log has a `##[error]` or `##[warning]` line.

### What could not run, and the limits

- **The mobile app's checks** were not run locally: no contract, generated output or `apps/` path changed. The run of record ran them.
- **The Database proof checks job's shell steps** were not rerun locally as a whole, and **the ordering and identity suites** were not run locally; the local runs follow the job's profile steps on one database each. C1 changes neither the workflow nor its steps.
- **No R2, processor, detector, check vendor or hold record exists,** as in Stage B; the ports have fixture adapters only, and the hold port is the test's own.
- **Not claimed:** P08's account deletion and its system step that removes the photos a member did not remove (DM-58 J9, carried); whether G-02's seam should inspect an inactive account's adopted upload before its purge (J8, carried to P07.1); a purge concurrent with a suspension observed waiting on the account row (the two take the same row `FOR UPDATE`, as `_revoke_account` and `lock_account_any_state` read; no suite case holds one and observes the other); a suspended member's own routes (the actor class refuses them before any operation; no C1 case calls them).

### Decisions and deviations for the manager

1. **The state-write guard's allowlist is not in an owned path, so C1 keeps the pinned line where it is.** The prompt names the allowlist in `tests/test_profiles_offline.py`; it is `NOT_A_PROFILES_STATE` in `tests/test_profile_recompute.py`, which C1 does not own, and it pins `media.py:128` (`asset.state = after`). The new import line would have moved that line to 129. Rather than write outside the owned paths, or stop, `media.py`'s module docstring was rewritten one line shorter: the system's steps paragraph now states the account-state rule and runs into the D9 paragraph, whose text is unchanged. The line stays at 128 and `test_profile_recompute` passes unchanged. The brief's sentence ("A line C1 moves … updates the allowlist in the same change") therefore did not apply.
2. **`lock_account` is unchanged,** and `lock_account_any_state` repeats its first three statements, rather than `lock_account` calling the new function. The gated function's text, the one every other step relies on, stays as `d8f1bad` had it; `test_the_any_state_lock_is_lock_account_without_its_state_check` pins the two as equal but for the state check.
3. **The hold port is asked at the purge's request only,** not at each acknowledgment, as Stage B's decision 5 settled; C1 keeps it.
4. **The third case checks five steps, not three:** `record_upload`, `review` and `run_check`, as the brief names, and also staff's `restrict_media` and the system read `delivery_reference`. Both are gated steps under the same rule, and the case needed an approved photo anyway. It runs for both inactive states, `suspended` and `deletion_pending`.
5. **The first case also shows a hold stopping the purge of a suspended owner,** with nothing deleted, before the purge proceeds: "the purge still asks the hold port first" in any state.
6. **"Delivery stays withheld throughout"** is checked on the row (no delivery reference) and through `delivery_reference`, which refuses an inactive owner and returns none for an asset that is not approved. The owner's own routes are not called after the suspension or the deletion request.
7. **`AccountStateTests` adds an offline assertion on the purge's hold check** (before the store's deletion and before `purge_requested_at`). Stage B's `REMOVAL.the-purge-without-the-hold-port` was caught only by the suite; `C1.the-purge-without-the-hold-port` is now caught offline too. The approval's hold check (M3) and the seam's no-variant path (M2) are unchanged: no offline assertion was added for them.
8. **The code commit was pushed before the local reversals finished.** The reversals edit only the local working tree, are never committed, and each was restored and checked by SHA-256 (above); nothing more was pushed until the run of record finished.
9. **The contract document's F05 index row** (its "Flows" table) is unchanged; C1 changes only the server mapping, as the owned paths say. Its mapping still names the brief's revision 7 as Stage B's, which it was.
10. **No stop rule was met:**
    - no path outside C1's owned paths changed: `glow_chat`, `glow_identity`, `glow_domain`, `glow_api`, `tests/test_profile_recompute.py`, the workflow, every lock file and dependency are unchanged;
    - no model, migration, DTO or registry entry changed;
    - no other step's account-state gate changed (`LockOrderTests`, `AccountStateTests`);
    - no provider, R2, Cloudflare or other service was called, and no credential used;
    - every new check that fails on the code at `d8f1bad` fails for item 1's reason (`BASE.the-code-at-d8f1bad`).

### Manager verification of Stage B's correction C1 (App Manager 10, 11 November 2026)

**The diff.** `git diff ecad10c e30ef4a` was read for its scope and its code: 10 paths, each among C1's owned paths, with the code head `7538c76` and the records commit `e30ef4a` (Markdown only).
- **The code:** `tx.py` gains `lock_account_any_state`, `lock_account`'s first three statements without its state check, and `lock_account` is unchanged. `request_purge` and `acknowledge_deletion` call it in place of `lock_account`; the purge still asks the hold port before the store. No other lock site changed, and no model, migration, DTO, registry entry, workflow, lock file or dependency changed.
- **Deviation 1** is the manager's mistake (AM10-19): the brief and the prompt placed the state-write guard's allowlist in `tests/test_profiles_offline.py`; it is `NOT_A_PROFILES_STATE` in `tests/test_profile_recompute.py`, which pins `media.py:128` and is not C1's. The session kept line 128 in place by shortening the module docstring, so the guard passes unchanged (`media.py:128` is still `asset.state = after`). Deviations 2 to 9 are within the brief.

**Classification.** The trusted classifier from `main` (`4dc2061`; byte-identical to `main`'s `scripts/change_scope.py`), with `python3 -I` and `--base 4dc2061… --head e30ef4a… --merge-base`, after the fast-forward: full scope, `behavior-or-empty`; the PR's whole diff (63 paths); one merge base, `4dc2061`. The manager workflow is unchanged since `52ae066` (DM-58 section 6).

**Re-runs.** In a scratch copy of the code head's tree (`git archive 7538c76`), in the clean environment, with hash-locked installs:
- **API:** `System check identified no issues (0 silenced).`; `Ran 559 tests` … `OK`; Ruff `All checks passed!`; `140 files already formatted`; mypy `no issues found in 81 source files`; the contract tests `Ran 49 tests` … `OK`.
- **The proof's offline tests:** `Ran 226 tests` … `OK`; Ruff clean; mypy `no issues found in 59 source files`.

The manager runs no database test locally.

**Reversals, re-run offline** (`tests.test_profiles_offline`, `tests.test_profile_media` and `tests.test_profile_recompute`, 47 tests), each restored afterwards and checked against `7538c76` by SHA-256:
- **M4:** `lock_account` back in `request_purge`: three failures (`LockOrderTests`' two and `AccountStateTests`' hold-port test).
- **M5:** the any-state lock given the state check: `test_the_any_state_lock_is_lock_account_without_its_state_check` fails.
- **M6:** `review` takes the any-state lock: three failures (`LockOrderTests`' two and `test_every_other_photo_step_keeps_its_gate` for `review`).

After the restore, the 47 tests pass.

**The run of record,** read with the GitHub tools: push run 42957799823 on `7538c76`. All eight jobs `success`; every DM-41 retry step `skipped`. The Database proof checks job: `[profile] cases: 67/67 passed in 55.6 s`, with the three new cases passing (`a_photo_removed_before_its_owner_is_suspended_is_still_purged`, `a_purge_asked_before_its_owner_asks_for_deletion_completes`, `every_other_photo_step_refuses_an_inactive_owner`: 10 steps refused for a suspended and a deleting owner); `profile secret scan: clean (1425 secrets held; …)`, `profile value scan: clean (535 member values held …)`, `PROFILE VERDICT: PASS`, `profile phase: 56 s`; the second profile run refused (exit status 1), the counts `127 127 99 44 1550 998` unchanged; `sv2-profile-results` 6,259 bytes; `no proof container remains`. The records push run 42959433903 on `e30ef4a` passed.

**Integration:** the manager branch was fast-forwarded from `ecad10c` to `e30ef4a`. Codex's P2 on `request_purge` is answered by C1 on PR44's head that holds it.

**What follows:** Codex on PR44's head that holds C1 and the exact-head review's prompt, then the full exact-head review of `7538c76` with its written threat model (DM-58 sections 3 and 7), then the Dev Manager's pre-merge read.

## Exact-head review of Stage B after C1 (code head `7538c76`)

- **The session:** started by Nathan from Stage B's exact-head review prompt, revision 1, at `8126c0c6df80f494c18070151b3831e1d6551f86` (`docs/ephemeral/2026-11-11-sv2-stage-b-review-prompt.md`). It reported on 11 November 2026, and its report was relayed to App Manager 10.
- **The gates:**
  - the environment check passed: none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*` or `CF_*` was present; the three expected AWS names were present, their values never read or passed;
  - the start gate passed, with one merge base, `4dc2061`, and no code differing from `7538c76`;
  - the trusted classification is `"full": true`, `behavior-or-empty`, over 64 paths.
- **What it ran,** in a scratch copy of `7538c76`:
  - the API's checks: `manage.py check`; 559 tests `OK`; Ruff; mypy clean on 81 files;
  - the contract tests (49) and `generate.mjs --check` (`Generated types and runtime validators match schemas.`);
  - the proof's offline tests (226), Ruff and mypy (59 files);
  - the four required offline reversals, each failing its case (R1 to R4), and six more of its own (R5 to R10, R12);
  - informational, on a throwaway PostgreSQL under P06.DB's D4: the suite 67/67 with both scans clean, and five database reversals (R5 to R8, R11).
- **What it read:** runs 42947095725 (64/64) and 42957799823 (67/67), and PR44's pull-request run 42963058038 on `8126c0c` (67/67 in 97.9 s). In each, all eight jobs passed, the gate printed `Application checks passed`, and no DM-41 retry fired. In the PR run's eight logs, no line holds a private-key header, a `delivery-` or `grant-` reference, `fixture-variant`, a PNG signature, `##[error]` or `##[warning]`.
- **The verdict: changes required, in tests and records only.** It found no blocking finding and no defect in the code: the code behaves as the brief, DM-57, DM-58 and C1 require. Findings F1 to F4 are should fix in correction classes; F5 is should fix outside them; N1 to N9 are nits.
- **Its statements:**
  - every Dev Manager condition is met in the code: U1 to U5, U8 to U10, J6, J7 and DM-58 section 3's correction;
  - item 1's premise holds: every write to a projected field goes through `transition`, which bumps the version, and no asset row is deleted anywhere;
  - J2 to J5 hold as built; the ports' fixture calls have effects in process memory only (N5), with no external call;
  - C1: `lock_account_any_state` equals `lock_account` without its state check; only the two writers use it; `glow_chat`'s `_revoke_account` takes the same row `FOR UPDATE`, so a purge serializes with a suspension or a deletion request; deviation 1 holds (`media.py:128` is still `asset.state = after`);
  - no test was weakened: Stage A's cases gain an approved photo, the F05 test asserts more, and the seed tests narrow to `SEEDED_BY_0007` with 0009 pinned on its own;
  - no DTO changed; the registry diff is exactly F05's `approve` and `reject`, `moderator` to `system`;
  - `.github`, the `Dockerfile`, every lock, requirement and package file and `apps/` are unchanged from `4dc2061`;
  - the records hold against the code and the runs, except F4 and nits N2, N5, N6 and N7.
- **The coverage notes** (DM-58 section 5):
  - **M2:** the suite's case suffices: the reversal passes offline and fails the suite at exactly `the seam was given the original`;
  - **M3:** the suite catches the hold check's removal (`:3074`), but not its answer ignored: F1;
  - **migration 0008's constraints:** F5.

**The review's threat model,** condensed (assets, actors and entry points are the prompt's):

| # | Threat | What stops it | What proves it |
|---|---|---|---|
| T1 | An anonymous prober on F05's routes | SV1's actor on every route (401); UUIDv4 asset IDs | `media.reorder_and_every_route…` |
| T2 | A member on another member's photo | `locked_asset` and `read_asset` filter by account; reorder checks its set | the same case; the session's `REMOVAL.*` and `D17.*` reversals |
| T3 | A stolen token | SV1's actor and the account-state gates; a delivery reference is not a credential (J2, P11) | SV1's suite; `media.every_other_photo_step_refuses_an_inactive_owner` |
| T4 | A grant replayed, uploads raced, limits or expiry crossed | the account row lock; `used_at` and the state check; the store's time against the expiry; the grant's own version's byte limit; the live and 20-entry limits; `media_grant_used_in_time` | `media.completions_are_matched_to_their_grant`, `media.grant_within_the_policys_limits`; R11 |
| T5 | A forged, duplicated, late or out-of-order store event | `receive` returns only events the adapter issued; `not_awaiting_upload`, `purge_not_requested`, `already_deleted` | `FixtureTests`; the completions and removal cases |
| T6 | A member route reaching a provider, system or staff step | the views call only `media.command`, which dispatches the owner's three actions | `RouteTests`; `staff.no_member_route_reaches_a_staff_operation` |
| T7 | An upload skipping quarantine, review or the seam | one writer, `transition`, bound to F05's table; the seam called unconditionally; `media_seam_passed` | `RegistryTests`, the two upload cases; R6. Gap: F3 |
| T8 | An original delivered, or a key or credential exposed | only the variant gets a reference; the projection shows one only while `approved`; 32-hex random keys; the credential stays in the adapter | `media.an_upload_moves…`, `media.no_key_original_or_bytes_in_any_response`, `KeyTests` |
| T9 | The check approving a held photo | the hold check at `media.py:636-637` | **F1:** only "the hold port was asked" is tested |
| T10 | The check clearing a restriction or undoing a removal | nothing clears `restriction_ref`; only `purged` leaves `removal_pending`; `media_approved_unrevoked` | `media.the_checks_decisions…` |
| T11 | A held, removed or restricted photo delivered | `delivery_reference`'s four conditions; `transition` clears the reference; `media_delivery_only_approved` | `media.an_upload_moves…`, `media.removal…`; R8 |
| T12 | A removal never completing, completing early, or lost to an inactive owner | the remaining-objects check; `lock_account_any_state` in the two writers only (C1) | `media.removal…`, C1's three cases, `LockOrderTests`, `AccountStateTests`; R2, R3 |
| T13 | `visible` without an approved photo, or left `visible` | `requirements.missing`; the recompute in `run_check`, `remove_photo` and `restrict_media` | `media.the_photo_requirement…`, `completion.refuses_each_missing_requirement` |
| T14 | Pointers locked out of name order | `_hold`; the publication records its own pointer | `PointerOrderCheckTests`, `pointers.one_order…`; R1. Gap: F2 |
| T15 | A media policy publication crossing a ceiling | absolute ceilings in code, checked before any write, so no two-step publication crosses one; `StaffAudit` on each | `MediaPolicyTests`, `media.policy_is…` |
| T16 | A value in a log, event or error | no logging in `media.py`; events carry references; refusal reasons are codes | `NoValueInLogsTests`, the session's `LOG.*` reversal, the value scan (narrower than recorded: F4) |
| T17 | An outbox event naming a deleted record | no asset, object or grant row is deleted | J1's rule in the data model |
| T18 | The served runtime importing Stage B | `SEALED_MODULES` holds `glow_domain.media` | `test_profiles_sealed_runtime`; R4 |
| T19 | Secrets in the public CI logs and artifacts | the job masks its secrets; the scan runs before any upload | the PR run's eight logs |
| T20 | A staff caller in code | `_check_staff` needs a `staff:` subject; a request ID used once; `lock_account` | `media.the_checks_decisions…`; the inactive-owner case |
| T21 | Migrations 0008 and 0009 | 0008 generated; both pinned by SHA-256; `makemigrations --check`; 0009's seed equals the code's default | `test_model_definitions`. Gap: F5 |

**The review's findings and the manager's dispositions** (step 6, "Fix or carry, by rule"). F1 to F4 are in correction classes and are fixed before the merge. F5 is fixed in the same pass, as the review recommends, since it extends the same kind of case. None changes a design, a contract or the code, so the correction needs no consultation first. C2 changes tests and records only:

| # | Severity (class) | Finding | Disposition |
|---|---|---|---|
| F1 | should fix (a test passes where it should fail; the check could approve a held photo) | Nothing shows a hold **stopping** an approval. The suite's case asserts only that the hold port was asked, with a hold that holds nothing, and the offline test checks the order of the text. R5 (the hold's answer ignored) passes the targeted API tests and the suite 67/67 on PostgreSQL | **In C2:** a suite case with the photo held, asserting the check's outcome `held`, the photo still `review_pending`, no approval `StaffAudit` row, no reference and no change to the profile; and an offline assertion that the approval's held branch returns before the transition |
| F2 | should fix (a test passes where it should fail; pointers locked out of order unchecked) | The lock-site guard misses `select_for_update()` on a queryset held in a variable, and raw SQL whose table name comes from `PolicyRevision._meta.db_table` (R9, R10 pass); a lock outside `settings_store` also bypasses `_hold` | **In C2:** the guard fails on any mention of `PolicyRevision` or its table in a scanned source outside `settings_store.py` and `models.py`, with the proof's read-only mentions named, each by file and function; each new spelling with its reversal |
| F3 | should fix (a test passes where it should fail; a photo reaching `approved` other than by its one path) | The state-write guard does not cover `MediaAsset.objects.create(state=…)` or `MediaAsset(state=…)` outside `transition`. The code has none today; R12 (an `approved` asset created in `staff.py`) passes every offline test | **In C2:** the guard (`tests/test_profile_recompute.py`) flags a `create`, `get_or_create`, `update_or_create` or constructor of `MediaAsset` with `state` anywhere but `request_upload`'s `upload_pending`, with its reversal |
| F4 | should fix (a record claims more than the code shows) | The records say the scans cover "object keys … and photo bytes". The ledger (`profile_support.py:519, 527`) holds only the originals' keys, photo bytes only as the hex of their first 24 bytes, and no fixture credential token | **In C2:** the ledger widened to the variants' keys, the bytes' `repr` and the fixture's credential tokens, with a reversal; any record that still claims more is corrected in C2's section |
| F5 | should fix (outside the classes) | Migration 0008's 11 constraints have no malformed-write case, where Stage A's 0005 has one for each (the P11 plan's DB04, partial) | **In C2:** a suite case writing each of 0008's constraints malformed and refused by PostgreSQL by name, as `constraints.malformed_direct_writes_are_refused` does for 0005 |
| N1 | nit | `glow_domain/media.py:85`'s `REVIEW_SUBJECT` is unused; the review's `no_variant` rejection is audited as `system:photo-check` | **Carried to P07.1** (G-02), the next change to `glow_domain/media.py`: whether the review step's rejection carries its own subject, or the constant goes |
| N2 | nit (records) | Decision 2's "a constraint holds it within the grant": `media_grant_used_in_time` sets only an upper bound, as DM-58 says | **In C2's record:** the sentence corrected; Stage B's section stands as written |
| N3 | nit (P11) | The server stores and returns whatever reference the port gives; "cannot be an address" rests on the contract's pattern, which only the suite checks | **Carried to P11** (PV04), in the P11 plan |
| N4 | nit (P11) | An original never uploaded (removed while `upload_pending`) still has a `MediaObject` row that needs an acknowledgment; R2 may send no delete event for a missing key | **Carried to P11** (PV04, DB08), in the P11 plan |
| N5 | nit (records) | The data model's F05 unit-of-work row: "no external effect" holds outside the process only; fixture calls write to process memory, which a rollback does not undo | **In C2:** the row says so |
| N6 | nit (records) | The fixture credential's key scope and expiry are recorded but not enforced: `put` takes no credential | **In C2's record** |
| N7 | nit (records) | `packages/contracts/README.md`: "a rejection likewise" implies a reject-without-A05 example the F05 test does not have | **In C2:** the sentence corrected |
| N8 | nit | Positions only grow while a photo holds the top one; after about 30,000 uploads, `positions_exhausted` blocks uploads for good | **Carried to P11**, in the P11 plan |
| N9 | nit (records) | The proof README's Stage A sentence "(DB04, for SV2's tables)" now reads as covering 0008's tables | **In C2:** the sentence names 0005's and, with F5, 0008's |

**What the review could not run:** the mobile checks (no `apps/` path changed; CI ran them), the ordering and identity suites, and the Database job's shell steps as a whole. A subagent read the full CI logs and reported counts only. Nothing in the repository, on GitHub or in Notion changed.

**C2's review:** C2 changes tests and records only (no non-test line), so a delta review follows it, reading every path C2 touches as it stands at C2's head, with this review's security focus (M05 S2). Codex reads the PR's final head as usual, then the Dev Manager's pre-merge read (DM-58 section 7).

## Stage B, correction C2

The brief's "Stage B, correction C2 (the exact-head review)", six items, tests and records only, against the exact-head review's F1 to F5 and nits N2, N5, N6, N7 and N9. Local database runs here are iteration, not evidence; the evidence of record is the CI run on the code head.

### The session

- **Started by Nathan** from correction C2's prompt, revision 1, at `885f65b2ef9472f59620cf61c727264af96aaa08` of the manager branch (`docs/ephemeral/2026-11-11-sv2-stage-b-c2-correction-prompt.md`), on 11 November 2026.
- **Branch:** `claude/eloquent-dijkstra-dmah71`, from `885f65b`. It matches `claude/**`, so the Foundation workflow ran on the push.
- **Code head:** `5bcbe549b7370264785c158ac95931730f7bf331` (tests only). **Records head:** the commit that adds this section and the three record corrections (item 6), pushed after the run of record finished.

### Start gate and environment

- **The start gate passed:** `git rev-parse HEAD` printed `885f65b2ef9472f59620cf61c727264af96aaa08`; no non-Markdown path differs from `7538c76`; no owned path differs between `885f65b` and the live manager branch, whose head was `885f65b` itself; `CASE_COUNT = 67` once; no "Stage B, correction C2" section in this record; the brief's C2 section present once.
- **The environment check (names only):** none of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY`; no `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*` or `CF_*` name; the three expected AWS names, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_CA_BUNDLE`, and no other `AWS_*` name, their values never read, printed or passed; `GH_TOKEN` and `GITHUB_TOKEN` present, never read.
- **The toolchain:** `Python 3.12.14`; `node v24.19.0` and `npm 11.9.0`, both from `$HOME/.local/bin` (second on `PATH`, after the Nix profile's `bin`, which holds neither); `Docker version 29.9.2`. No Docker daemon was running; the session started `dockerd` in its sandbox (decision 6).
- **Every repository command** ran under `env -i PATH HOME LANG=C.UTF-8`, the proxy and CA variables by reference, and only the command's own variables (`GLOW_ENV=test` for the API; the proof's `PROOF_*` and `DJANGO_SETTINGS_MODULE` for the local suite). No `AWS_*` name passed.

### Item 1 — a hold stops an approval (F1)

- **Files:** `proofs/postgres-ordering/glow_ordering_proof/profile_cases.py` (`media.a_hold_stops_the_checks_approval`); `services/api/tests/test_profile_media.py` (`RouteTests.test_a_hold_returns_before_the_approval_writes_anything`).
- **The suite case:** a member with every requirement but the photo (the two seeds and the completing edit; `missing == ["photo"]`) uploads a photo, which the review step moves to `review_pending`. The test's check decides to approve it and the test's hold port (`RecordingHold({asset_id})`) holds it. Twice, the check's result is `no_change` with reason `held`; the check and the hold port were each asked once; and a snapshot is unchanged: the asset's state (`review_pending`), version, delivery reference and review reference, the profile's state (`incomplete`) and version, the asset's `StaffAudit` rows, the outbox events of the asset and the profile, and the delivery references the fixture store has issued (none new). No approval `StaffAudit` row exists; the owner's lifecycle shows `review_pending` with no reference; the profile still misses its photo and lists none. Released (`RecordingHold()`), the same check approves it and the profile becomes `visible`, with one approval row: the hold alone stopped it.
- **The offline assertion:** in `run_check`'s body, the one `if decided.decision == 'approve':` branch holds exactly one `if adapters.hold.held(asset.id):` whose only statement is `return Result('no_change', reason='held')`, with no `else`; nothing before it, in the body or the branch, contains `_decision_audit(`, `transition(`, `delivery_reference(`, `recompute.recompute(`, `.save(` or `.create(`; each of the approval's four writes comes after it; and the port is asked once in the body.
- **Reversal R1** (`glow_profiles/media.py`: the two lines of the held branch replaced by a bare `adapters.hold.held(asset.id)`, the port asked and its answer ignored):
  - offline: `FAIL: test_a_hold_returns_before_the_approval_writes_anything` (`AssertionError: 0 != 1`), the only failure of `RouteTests` (3 tests): the existing order check passes the reversal, as the review found;
  - on a throwaway PostgreSQL 17.11 (D4): `[profile] FAIL media.a_hold_stops_the_checks_approval (10, D9, D10) 1.0 s: FAILED: the outcome is held`, `[profile] cases: 68/69 passed`, every other case passing.
  - Undone with `git checkout`; `media.py`'s SHA-256 `491c734b25de6013…` matches `HEAD` and `7538c76` after both.

### Item 2 — the lock-site guard (F2)

- **File:** `services/api/tests/test_profile_pointer_order.py`: `NothingElseLocksAPointerTests.test_nothing_but_the_store_and_the_model_mentions_a_pointer` and `test_the_search_word_matches_the_models_table`. The existing lock-spelling check is unchanged.
- **The check:** every line of every scanned source (the API's packages and the proof, not their tests, migrations or virtual environments, as before) outside `glow_persistence/models.py` and `glow_profiles/settings_store.py` whose lower-cased text holds `policyrevision` is a mention: code, a string, an f-string's literal parts, a comment or a docstring. Each mention is named by file, innermost function and stripped line; the set must equal the allowlist exactly, so a new mention, a lock or not, fails until it is read and named. The second test checks that `models.py` sets no `db_table`, so the table is Django's default, `glow_persistence_policyrevision`, which the search word matches.
- **The allowlist (`POINTER_READS`), the proof's four read-only mentions, none a lock:** in `profile_cases.py`, `_counts` (`PolicyRevision,` in its import, and `"pointers": sum(PolicyRevision.objects.values_list("version", flat=True)),`) and `settings_publication` (its import line, and `pointer = PolicyRevision.objects.get(name=ps.GENDER_LIST)`).
- **Reversal R2a** (`glow_profiles/staff.py`: a function binding `rows = PolicyRevision.objects.filter(name=name)` and returning `rows.select_for_update()`): `FAIL: test_nothing_but_the_store_and_the_model_mentions_a_pointer` (`Lists differ: ['services/api/glow_profiles/staff.py:307 …'] != []`), the only failure of the class's three tests: the existing check passes it.
- **Reversal R2b** (`glow_profiles/operations.py`: `table = PolicyRevision._meta.db_table` then `cursor.execute(f"SELECT id FROM {table} WHERE name = %s FOR SHARE", [name])`): the same failure (`['services/api/glow_profiles/operations.py…'] != []`), again the only one.
- Each undone; `staff.py` `b642194b07e83033…` and `operations.py` `47f7235bb7a81eca…` match `HEAD` and `7538c76`.
- **What it still cannot see:** a name built at run time (`"Policy" + "Revision"`, a table name split across lines or strings, `getattr` on the models module, `apps.get_models()` or the introspection's table list iterated); a source outside the scanned roots (tests, migrations, non-Python files). The model and the store themselves are read only by the lock-spelling check.

### Item 3 — the state-write guard (F3)

- **File:** `services/api/tests/test_profile_recompute.py`: `CallSiteTests.test_a_photo_is_created_only_upload_pending` and `test_the_creation_guard_sees_each_spelling`, with `ASSET_CREATE`, `CREATIONS_WITH_STATE`, `_enclosing`, `_asset_creations` and `_creations_with_state`. `NOT_A_PROFILES_STATE` and the existing checks are unchanged.
- **The checks,** over `scanned_modules()` (`glow_profiles` and the age port):
  - every `create`, `get_or_create`, `update_or_create` or `bulk_create` on a receiver naming `MediaAsset`, and every call of a name ending `MediaAsset`, is exactly one: `request_upload.body`'s `MediaAsset.objects.create(…, state=md.UPLOAD_PENDING)`;
  - every `create`, `get_or_create` or `update_or_create`, and every call of a capitalized name (a class built), whose keywords set `state` or unpack `**`, whatever the receiver is named, equals the allowlist, each by file, enclosing definitions, call and the state it sets.
- **The allowlist (`CREATIONS_WITH_STATE`), seven, each its own model's initial state:** `glow_identity/age.py` `OrmAgeAssurance.record` (`AccountAgeState`, `assurance.state.value`); `events.py` `emit` (`OutboxEvent`, `'pending'`); `idempotency.py` `store` (`IdempotencyRecord`, `'completed'`); `media.py` `request_upload.body` (`MediaAsset`, `md.UPLOAD_PENDING`); `operations.py` `save_birth_input.body` (`BirthInput`, `'pending'`), `save_profile.body` (`Profile`, `'incomplete'`) and `decide_sensitive_consent.body` (`ConsentDecision`, `'accepted' if accepting else 'withdrawn'`).
- **The spellings test** shows each form F3 names seen: `create`, `models.MediaAsset(...)`, `get_or_create` and `update_or_create` by the named check (four), and those, an alias's `model.objects.create(state=...)` and a `**` constructor by the receiver-independent one (six).
- **Reversal R3** (`glow_profiles/staff.py`: `_approve_directly` returning `MediaAsset.objects.create(account_id=…, provider="fixture", position=1, state="approved")`): `FAIL: test_a_photo_is_created_only_upload_pending` (`Lists differ: [… ('glow_profiles/staff.py', '_approve_di…')] != […]`), the only failure of `CallSiteTests` (5 tests): the existing state-write check passes it. Undone; `staff.py` matches `HEAD` and `7538c76`.
- **What it still cannot see:** a class held under a lower-case name and called (`cls(state=…)`); a state passed through a positional argument or a dict built elsewhere and handed to a lower-case factory; raw SQL; any module outside `glow_profiles` and the age port.

### Item 4 — the scans' ledger (F4)

- **Files:** `proofs/postgres-ordering/glow_ordering_proof/profile_support.py` (`ValueLedger.add_bytes`, `ObservedObjects`, `ProfileContext.watch_store` and `hold_media`), `profile_cases.py` (`run_case`), `tests/test_profile_offline.py` (`ValueLedgerTests`, two new tests).
- **What the value ledger now holds,** besides Stage A's member values:
  - every object key, the original's and each variant's, from every `MediaObject` and `MediaUploadGrant` row after each case, and from the fixture store as each object is written;
  - every grant reference (from the rows) and every delivery reference the store issued, with the key it was issued for;
  - every upload credential the store issued: its key and its token;
  - each object's bytes, as the store writes them (`ObservedObjects`, which the store's `objects` becomes before the first case, so an object written and purged within one case is still held) and as they remain after each case: the hex of their first 24 bytes, which any print of their hex starts with; their `repr` up to the end of their first 24 bytes, without the closing quote, which any print of their `repr` starts with; and the text of printable ASCII bytes (the fixture's synthetic variant). Each form is searched as written and as JSON escapes it (`forms`).
- `run_case` calls `watch_store` before each case and `hold_media` after it; a failure of `hold_media` fails the case (`ERROR: the value ledger's photo values: …`).
- **Offline:** a photo's bytes printed as their `repr` (whole, from their first 30 bytes, inside JSON), their hex (whole, first 24 bytes) and the variant as text, `repr` and hex are each found; another photo's bytes and a photo's first 12 bytes are not; an object set and then popped stays held, key and bytes.
- **Reversals,** on a throwaway database (D4), each in `media.an_upload_moves_only_through_quarantine_the_seam_and_review`:
  - **R4a**, the variant's key written to a log record (`logging.getLogger("glow_ordering_proof.c2_reversal").warning("variant %s", variant)`): `[profile] cases: 69/69 passed`, `profile value scan: FOUND (813 member values held: …; 1 found in the same output)`, `PROFILE VERDICT: FAIL`, exit 1;
  - **R4b**, the photo's `repr` written to a log record (`….warning("photo %r", synthetic_png(3, 2))`): the same, `profile value scan: FOUND (…; 1 found …)`, `PROFILE VERDICT: FAIL`.
  - Each undone; `profile_cases.py` `eaa4ba0db962b60f…` matches `HEAD`.
- **What it still cannot see:** an object set by `dict.update` or `setdefault` (the store uses neither); bytes printed in another encoding (base64, a decoded PNG's text) or from their middle; a value in an output the suite does not capture. The suite's printed value-scan line (`profile_suite.py`, outside C2's paths) still names only the member values' kinds; its count now includes the photos' values (decision 4).

### Item 5 — migration 0008's constraints (F5)

- **File:** `profile_cases.py`: `constraints.malformed_media_writes_are_refused` (checks `10`, `D10`), with `MEDIA_CATALOG` and `SHADOWED`.
- **The case:** a member with an approved photo and a pending upload. 21 direct writes no SV2 writer makes, each breaking one constraint only, each inside its own `transaction.atomic()`, each refused by PostgreSQL with an error naming that constraint (`constraint "<name>"` in the error's text, which is never kept), and a snapshot of the rows' counts and the touched rows' values unchanged after all of them:
  - **the 13 constraints migration 0008 declares,** read from the migration module as the 0005 case reads 0005 and each required to have a write: `media_delivery_only_approved`, `media_approved_unrevoked`, `media_removal_record`, `media_seam_passed` (`MediaAsset`); `glow_persistence_mediaobject_version`, `media_object_role`, `media_object_opaque_key`, `media_object_adoption_evidence`, `media_one_original` (`MediaObject`); `glow_persistence_mediauploadgrant_version`, `media_grant_expiry`, `media_grant_used_in_time`, `media_grant_opaque_key` (`MediaUploadGrant`);
  - **the 8 other constraints PostgreSQL holds on 0008's two new tables,** each named by Django and read by name from `pg_constraint`: `MediaObject`'s unique key and its asset's foreign key, and Django's `byte_size >= 0` check; `MediaUploadGrant`'s unique `grant_ref`, `object_key` and asset (one-to-one), and its asset's and account's foreign keys. The catalog's set must equal `MEDIA_CATALOG`, so a new unique key, foreign key or check on these tables fails the case until it has a write. Django's two `version >= 0` column checks are in the catalog but shadowed by 0008's `version >= 1`, so they have no write (`SHADOWED`).
- **Local:** `[profile] PASS constraints.malformed_media_writes_are_refused (10, D10) 0.5 s: 21 malformed direct writes refused by PostgreSQL, each by its constraint: all 13 that migration 0008 declares, and 8 unique keys, foreign keys and column checks of its two tables`.
- **Reversal R5** (`glow_persistence/migrations/0008_media_lifecycle.py`: the `media_grant_used_in_time` operation deleted, on a throwaway database only): `makemigrations --check` printed `+ Create constraint media_grant_used_in_time on model mediauploadgrant`; `[profile] FAIL constraints.malformed_media_writes_are_refused (10, D10) 0.5 s: FAILED: PostgreSQL refuses the write by media_grant_used_in_time`, `68/69`. Undone; the migration's SHA-256 `6d91f4fb1763f801…` matches `HEAD` and `7538c76`.
- **Not covered:** NOT NULL columns and primary keys; `MediaAsset`'s constraints from before 0008.
- **The review counted 0008's constraints as 11;** the migration declares 13 `AddConstraint` operations, the two `_version` checks among them, and the case covers all 13 (decision 1).

### Item 6 — the records (N2, N5, N6, N7, N9), and what the ledger holds

- **N2, decision 2 of "Stage B" corrected** (that section stands as written): "A grant's time is judged by the store's upload time: a completion is adopted only if its reported upload time is not after the grant's expiry, and `used_at` records that time. `media_grant_used_in_time` sets an upper bound only (`used_at` at or before `expires_at`); no constraint holds `used_at` at or after `issued_at`."
- **N6, recorded:** the fixture credential (`FixtureCredential`) records a key, a byte limit and an expiry, and none of them is enforced: `put` takes no credential, so the fixture store accepts an upload at any key, of any size, at any time. What refuses an upload outside its grant is the domain's own check at the completion (the grant's key, `used_at` and the asset's state, the expiry against the store's upload time, the byte limit of the grant's policy version). A real adapter's credential is P11's (PV04).
- **N5:** `docs/architecture/data-model.md`, the F05 unit-of-work row: "with no effect outside the process: their calls write to the process's memory (the fixture store's objects, credentials, deletion requests and delivery references), which a rollback does not undo".
- **N7:** `packages/contracts/README.md`, the Stage B bullet now says what `test_f05_quarantine_cannot_be_published_by_uploader` asserts: the uploader and staff `forbidden` for both decisions; the system with `A05` `allowed` for both; without `A05`, `policy_unresolved` for an approval only (the test has no rejection without `A05`); and an approval from `quarantined` (uploader, or system with `A05`) or `removal_pending` (system with `A05`) a `state_conflict`.
- **N9:** `proofs/postgres-ordering/README.md`: Stage A's DB04 sentence now names 0005's tables; a new sentence describes C2's two cases (0008's 13 and 8), the ledger's new values, and the count, 69, with Stage A's 53, Stage B's eleven, C1's three and C2's two.
- **F4's records:** Stage B's "Check 12 for the new routes" row ("object keys, grant references, delivery references and the start of each photo's bytes join the value ledger") held, at `7538c76`, the originals' keys from `request_upload`, the grant references, the delivery references of photos approved through `approved_photo` and the disclosure case, and the hex of the first 24 bytes of photos put through `put_photo`: no variant key, no credential token, no bytes `repr`, and no bytes put by a case directly. Since C2 it holds what item 4 lists.

### Commands and results

| Command (clean environment) | Result |
|---|---|
| `python3.12 -m venv .venv && .venv/bin/python -m pip install --require-hashes -r requirements-dev.lock` (`services/api`, then `proofs/postgres-ordering`) | exit 0, each |
| `manage.py check` (`GLOW_ENV=test`) | `System check identified no issues (0 silenced).` |
| `manage.py test tests --verbosity 2` | `Ran 564 tests` `OK` (559 at `7538c76`; five new) |
| `ruff check .`; `ruff format --check .`; `mypy` (API) | `All checks passed!`; `140 files already formatted`; `Success: no issues found in 81 source files` |
| `PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests -v` | `Ran 49 tests` `OK` |
| `python -m unittest discover -s tests -t . -v` (proof) | `Ran 228 tests` `OK` (226 at `7538c76`; two new) |
| `ruff check .`; `ruff format --check .`; `mypy` (proof) | `All checks passed!`; `59 files already formatted`; `Success: no issues found in 59 source files` |
| The profile suite on a throwaway PostgreSQL 17.11 (D4), final code (iteration) | migrate exit 0; `No changes detected`; `[profile] cases: 69/69 passed in 120.6 s`; `profile secret scan: clean (1447 secrets held; 0 found in 918 log records, 162 writes and the results JSON)`; `profile value scan: clean (813 member values held: …; 0 found in the same output)`; `PROFILE VERDICT: PASS` |
| An earlier local run (iteration) | `68/69`: the new 0008 case's catalog check omitted the `MediaAsset` table, which holds four of 0008's constraints; corrected before the commit |
| Reversals R1 to R5 | as each item records; every file restored and its SHA-256 matched to `HEAD` |

**Local database runs (D4):** six, each a new container from the CI job's pinned image (`postgres@sha256:d74eeac9…`, server `17.11 (Debian 17.11-1.pgdg13+2)`), published on `127.0.0.1` only, with a generated superuser and role password, one database with the run's marker as its comment, the proof's settings in a clean environment with none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or a `PG*` name, and the container and its credential files removed afterwards (`docker ps -a` empty at the end). Iteration, not evidence.

### The run of record

- **Foundation run 42990527042** on `5bcbe549b7370264785c158ac95931730f7bf331` (push), attempt 1: **conclusion success**. Read with the GitHub tools; a subagent of this session read the full logs and reported results and counts only.
- **Jobs (8), each success:** Change scope; API mobile smoke; Mobile checks; API artifact checks; API checks; Stream proof checks; Database proof checks; Foundation gate, which printed `Application checks passed` (scope full, every input job success).
- **Counts:** API `Ran 564 tests` `OK`; contracts `Ran 49 tests` `OK`; API Ruff, `140 files already formatted`, mypy 81 files clean; the proof's offline `Ran 228 tests` `OK`.
- **The profile suite:** both other markers refused on the profile database (`exit status 1` each, with the refusal printed); `No changes detected`; **`[profile] cases: 69/69 passed in 99.8 s`** (69 `PASS` lines, no `FAIL`), among them `media.a_hold_stops_the_checks_approval … 0.8 s: the check's approval held twice with nothing written; released, it approves` and `constraints.malformed_media_writes_are_refused … 0.5 s: 21 malformed direct writes refused by PostgreSQL, each by its constraint: all 13 that migration 0008 declares, and 8 unique keys, foreign keys and column checks of its two tables`; **`profile secret scan: clean (1447 secrets held; 0 found in 918 log records, 162 writes and the results JSON)`**; **`profile value scan: clean (813 member values held: coordinates, birth dates, times and places, own words, sensitive values; 0 found in the same output)`**; `PROFILE VERDICT: PASS`; the job's own check: `the job's secrets found in the profile suite's output: 0`, `… in the profile results JSON: 0`, `the suite's own scans (secrets, member values) reported clean: True`; **`profile phase: 100 s`**. The digests case checked `1009` stored digests of `11` kinds of command; the pointer-order case observed 27 transactions; the disclosure case found none of 244 object keys and 130 credentials in any response.
- **The second profile run:** `second profile run exit status: 1`, refused as a used database (auth users, app accounts and outbox events exist; a setting was published beyond its launch default); rows before and after `129 129 100 44 1568 1009`, unchanged.
- **No DM-41 retry fired:** both retry steps skipped in all four jobs that have them. No `##[error]` or `##[warning]` line.
- The value ledger's count rose from Stage B's run of record (511) to 813 with item 4's values.

### What could not run, and the limits

- The mobile checks, the API smoke and the artifact checks were not run locally (no `apps/` or image path changed); CI ran them. The ordering, identity and Stream suites were not run locally. `generate.mjs --check` was not run (no contract or generated path changed).
- The reversals' database halves ran only locally (iteration); CI ran the final code, not the reversals.
- Each guard's limits are under its item.

### Decisions and deviations for the manager

1. **0008 has 13 declared constraints, not 11:** the case covers every `AddConstraint` the migration holds, the two `_version` checks among them, and adds the 8 unique keys, foreign keys and column checks PostgreSQL holds on its two new tables, named from the catalog, beyond the brief's words; Django's two `version >= 0` checks are recorded as shadowed.
2. **The state-write guard (F3) goes beyond `MediaAsset` by name:** it also pins every creation that sets a state, whatever its receiver (seven), so an aliased model is seen.
3. **The ledger (F4) holds more than the brief lists:** grant references from the rows and every delivery reference the store issued, besides the variants' keys, the bytes' `repr` and the credential tokens. A `repr` is held as its start, up to the end of the first 24 bytes, which every print of the whole `repr` contains, as the hex was already held; the variant's text is held too.
4. **`profile_suite.py` is unchanged** (outside C2's paths): its value-scan line still reads "member values held: coordinates, birth dates, times and places, own words, sensitive values", though its count now includes the photos' values. A later change in that file can name them.
5. **The ledger's photo values are gathered in `run_case`,** before and after each case, so `profile_suite.py` needs no change; a failure to gather them fails the case.
6. **Docker:** the sandbox had `dockerd` installed but not running; the session started it locally to run D4's recipe with the pinned image.
7. **The three record corrections (item 6) are in the records commit,** with this section, after the run of record; the code commit holds tests only.
8. **No stop rule was met:** no path under `glow_profiles`, `glow_domain`, `glow_persistence`, `glow_chat`, `glow_identity` or `glow_api` changed, nor a DTO, registry entry, workflow, lock file or dependency; every new check passed on the code at `7538c76` as it stands, with no temporary edit; every reversal's temporary edit of code was undone and checked by SHA-256. `CASE_COUNT` changed 67 to 69 for the brief's two cases, with the offline pin, and `ProfilePlanTests`' Stage B count 14 to 15 for the hold case. No test was weakened or deleted.

### Manager verification of Stage B's correction C2 (App Manager 10, 11 November 2026)

**The diff.** `git diff 885f65b 9740196` was read for its scope and its code: 10 paths, each among C2's owned paths.
- **The code head `5bcbe54`** changes six paths, each a test or the proof's suite: `profile_cases.py`, `profile_support.py` and `tests/test_profile_offline.py` in the proof; `test_profile_media.py`, `test_profile_pointer_order.py` and `test_profile_recompute.py` in `services/api/tests`. No path under `glow_profiles`, `glow_domain`, `glow_persistence`, `glow_chat`, `glow_identity` or `glow_api` changed, and no model, migration, DTO, registry entry, workflow, lock file or dependency.
- **The records commit `9740196`** changes four Markdown paths: `data-model.md` (N5), this record, `packages/contracts/README.md` (N7) and `proofs/postgres-ordering/README.md` (N9).
- **The deviations:**
  - 1 to 3 widen the brief's checks (all 13 of 0008's declared constraints and 8 catalog constraints; creations that set a state whatever their receiver; grant and delivery references and a `repr`'s start in the ledger). Each is accepted.
  - 4 goes to the delta review as a nit: `profile_suite.py`'s value-scan line names only the member values' kinds, while its count (813) now includes the photos' values.
  - 5, 7 and 8 are within the brief.
  - 6 is recorded: the session started `dockerd` in its sandbox for D4's local runs, which are iteration, not evidence.

**Classification.** The trusted classifier from `main` (`4dc2061`; byte-identical to `main`'s `scripts/change_scope.py`), with `python3 -I` and `--base 4dc2061… --head 9740196… --merge-base`, after the fast-forward: full scope, `behavior-or-empty`; the PR's whole diff (65 paths); one merge base, `4dc2061`. The manager workflow is unchanged since `52ae066` (DM-58 section 7).

**Re-runs.** In a scratch copy of the code head's tree (`git archive 5bcbe54`), in the clean environment, with hash-locked installs:
- **API:** `System check identified no issues (0 silenced).`; `Ran 564 tests` … `OK`; Ruff `All checks passed!`; `140 files already formatted`; mypy `no issues found in 81 source files`; the contract tests `Ran 49 tests` … `OK`.
- **The proof's offline tests:** `Ran 228 tests` … `OK`; Ruff clean; mypy `no issues found in 59 source files`.

The manager runs no database test locally.

**Reversals, re-run offline** (`tests.test_profile_media`, `tests.test_profile_pointer_order`, `tests.test_profile_recompute` and `tests.test_profiles_offline`, 55 tests). Each was restored afterwards and checked against `5bcbe54` by SHA-256. Each fails exactly C2's new test, which the checks before C2 passed:
- **M7:** `run_check` asks the hold port and ignores its answer (`glow_profiles/media.py`): one failure, `RouteTests.test_a_hold_returns_before_the_approval_writes_anything`.
- **M8:** an approved `MediaAsset` created in `glow_profiles/staff.py`: one failure, `CallSiteTests.test_a_photo_is_created_only_upload_pending`.
- **M9:** a `PolicyRevision` queryset bound to a variable and locked in `glow_profiles/operations.py`: one failure, `NothingElseLocksAPointerTests.test_nothing_but_the_store_and_the_model_mentions_a_pointer`.

After the restore, the 55 tests pass, and `media.py` (`491c734b25de6013…`), `staff.py` (`b642194b07e83033…`) and `operations.py` (`47f7235bb7a81eca…`) match `5bcbe54`.

**The run of record,** read with the GitHub tools: push run 42990527042 on `5bcbe54`. All eight jobs `success`; every DM-41 retry step `skipped`. The Database proof checks job:
- `[profile] cases: 69/69 passed in 99.8 s`, with both new cases passing (`media.a_hold_stops_the_checks_approval`, and `constraints.malformed_media_writes_are_refused` with its 21 writes);
- `profile secret scan: clean (1447 secrets held; …)` and `profile value scan: clean (813 member values held …)`;
- `PROFILE VERDICT: PASS`, `profile phase: 100 s`;
- the second profile run refused (exit status 1), the counts `129 129 100 44 1568 1009` unchanged;
- `sv2-profile-results` 6,396 bytes; `no proof container remains`.

The records push run 42992446669 on `9740196` passed.

**Integration:** the manager branch was fast-forwarded from `885f65b` to `9740196`.

**What follows:** the delta review of C2 (M05 S2: C2 changes no non-test line), which reads every path C2 touches at `5bcbe54`, with the exact-head review's security focus. Then Codex on the final head, the Dev Manager's pre-merge read (DM-58 section 7, with C2's data-model sentence), the PR run, and the merge.

## Delta review of Stage B's correction C2 (code head `5bcbe54`)

- **The session:** started by Nathan from C2's delta review prompt, revision 1, at `c4324d39cd6f0b6166f8d5d7a12b5cad2001eb29` (`docs/ephemeral/2026-11-11-sv2-stage-b-c2-delta-review-prompt.md`). It reported on 11 November 2026, and its report was relayed to App Manager 10.
- **The gates:**
  - the environment check passed: none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*` or `CF_*`; the three expected AWS names and no other `AWS_*` name, their values never read or passed; the session started `dockerd` in its sandbox;
  - the start gate passed, with one merge base, `4dc2061`, and no non-Markdown path differing from `5bcbe54`;
  - the trusted classification is `"full": true`, `behavior-or-empty`, over 65 paths.
- **What it ran,** in a scratch copy of `5bcbe54`:
  - the API's checks: `manage.py check`; 564 tests `OK`; Ruff; 140 files formatted; mypy clean on 81 files;
  - the contract tests (49) and the proof's offline tests (228), Ruff and mypy (59 files);
  - eleven offline reversals of its own (A1 to A4, B1 to B3 with B2b, C1 to C3);
  - informational, on a throwaway PostgreSQL 17.11 under P06.DB's D4: one suite run with A3 and a credential token logged in the 0008 case, `68/69` with `media.a_hold_stops_the_checks_approval` failing at its unchanged snapshot, `profile value scan: FOUND (…; 1 found)` with the secret scan clean, `PROFILE VERDICT: FAIL`; the container, its credential files and `dockerd` removed or stopped afterwards.
- **What it read:** runs 42990527042 (69/69 in 99.8 s), 42992446669 (records only: Change scope and the gate passed, the six application jobs skipped) and PR44's pull-request run 43021936005 on `c4324d3` (all eight jobs passed, `Application checks passed`, 69/69 in 75.0 s, both scans clean, the second run refused). In both Database job logs, no line holds `fixture-variant`, a `delivery-` or `grant-` reference, a PNG signature, a private-key header or PostgreSQL `DETAIL` text; the other six jobs' logs were not scanned for these. No workflow prints `docker logs`.
- **The verdict: approve with nits.** No blocking or should-fix finding, and none in a correction class. F1 to F5 are closed, each new check fails for the edit it names, and the runs match the records. Nothing in the repository, on GitHub or in Notion changed.
- **Its statements:**
  - **F1:** A1 (an audit row in the held branch), A2 (the hold asked after `transition`) and A4 (the answer kept, the branch falling through) each fail the offline check; A3 passes offline and fails the suite case (N-d). No plausible edit passes both.
  - **F2:** the four `POINTER_READS` entries are reads; no model has a foreign key to `PolicyRevision`, so no lock comes through a join; B3 (`getattr(m, "PolicyRevision")`) fails the new test, though C2's item 2 lists `getattr` among the limits.
  - **F3:** every `MediaAsset` creation but `request_upload`'s is flagged, and C3 (`md.UPLOAD_PENDING` to `md.APPROVED`) fails. Two of the seven entries set the state their writer decides rather than a fixed initial state (`AccountAgeState`, `assurance.state.value`; `ConsentDecision`, accepted or withdrawn), so C2's "each its own model's initial state" is loose for them.
  - **F4:** one store instance (`default_storage()`); credentials and references are never removed; `watch_store` and `hold_media` run around every case and a failure to gather fails it; nothing C2 added prints a value; the 24-byte PNG prefix includes the IHDR chunk and the dimensions, and values under five characters are skipped, so benign matches are unlikely.
  - **F5:** 0008 declares 13 constraints (deviation 1 confirmed); read against the model and the migration, each of the 21 writes breaks exactly one; `SHADOWED` is right; a refusal's text is matched and discarded.
  - **The records:** N2, N6, N7 and N9 hold against the code and the test, but for N-c; N5's sentence is true in substance (N-e); C2's section and the manager's verification match the code, the counts and the runs.
  - **No test weakened;** `CASE_COUNT` 67 to 69 and the Stage B plan count 14 to 15 match the two cases; the scope is exactly the six test and suite paths.

**The review's findings and the manager's dispositions** (step 6, "Fix or carry, by rule"). Every finding is a nit, outside the correction classes, so under rule (b) each is a recorded follow-up; nothing changes in tests or code before the merge:

| # | Finding | Disposition |
|---|---|---|
| N-a | F3's recorded limits are incomplete: an async `acreate(..., state="approved")` and a clone (`pk = None`, `save(force_insert=True)`) pass every offline check, as they pass the older state-write guard (C1, C2). No code in `glow_profiles` or the age port uses either | **Recorded here,** as C2's item 3's further limits; **carried** to the next change to `test_profile_recompute.py` (the carried-items file) |
| N-b | F2's recorded limits are incomplete: an escaped literal (`"glow_persistence_policy\x72evision"`) and an allowlisted line's text repeated in the same function, with the lock in a helper, pass (B1, B2b); `POINTER_READS` is compared as a set. `getattr` on the models module is caught (B3), so it is not a limit | **Recorded here,** as C2's item 2's further limits and its one correction; **carried** to the next change to `test_profile_pointer_order.py` |
| N-c | The proof README's C2 sentence and `profile_support.py`'s module docstring say the ledger holds each object's bytes "as their hex and their `repr`"; it holds the start of each, the first 24 bytes, which any whole print contains | **The README corrected** in this batch ("the start of each object's bytes … their first 24 bytes, which any whole print of either contains"); the docstring, a code path, **carried** to the next change to `profile_support.py` |
| N-d | F1's offline write list omits `.update(`, `bulk_create` and `events.emit(`, so an `.update(review_ref=…)` before the hold's return passes offline (A3); the suite case catches it | **Carried** to the next change to `test_profile_media.py` |
| N-e | The data model's F05 unit-of-work row lists the fixture store's memory writes without its `reads` log, which `read` appends inside the transaction (`media_fixtures.py:99-104`) | **To the Dev Manager's pre-merge read** (DM-59), with words recommended, since the row is on its list |
| N-f | `profile_suite.py`'s value-scan line names only the member values' kinds while its count (813) includes the photos' values (C2's deviation 4) | **Carried** to the next change to `profile_suite.py`; already recorded in C2's section and the proof README |

**C2's records, as the review corrects them.** C2's section stands as written; these readings take precedence over it:
- item 2's limits also include an escaped table literal and a repeated allowlisted line with the lock in a helper; `getattr` on the models module is caught;
- item 3's limits also include an async create and a clone saved with `force_insert`; two of `CREATIONS_WITH_STATE`'s entries set a state their writer decides;
- the ledger holds the start of each object's bytes, as item 4 says.

**What follows:** the Dev Manager's pre-merge read (DM-59: DM-58 section 7's list, C2's data-model sentence with N-e, J1 to J9 and C1 as applied, the manager workflow at `52ae066`, the carried nits and the merge); then the PR run and Codex on the final head, the checklist in PR44's description, and the merge.

### PR44's pull-request run on `9464dd8`: Mobile checks failed outside the PR

- **Run 43044190450** on `9464dd8` (DM-59's commit, Markdown only): six jobs passed, the Database proof checks with the profile suite among them. **Mobile checks** failed at "Install Chromium for rendered fixture checks" (`npx playwright install --with-deps chromium`, 15:03:12 to 15:13:17 UTC): apt could not fetch nine font packages, each attempt reporting `Temporary failure resolving 'azure.archive.ubuntu.com'`, then `Failed to install browsers`. The Foundation gate failed only for that job.
- **The diagnosis:** outside the PR. `git diff --name-only c4324d3 9464dd8 -- . ':!*.md'` prints nothing, and the same code passed all eight jobs at `c4324d3` (run 43021936005). The failure is the runner's package-mirror name resolution. The step has no retry (DM-41's covers `actions/setup-python` only).
- **Done:** one comment on PR44 (the PR-activity rules for a PR the manager opened); no re-run, which the manager cannot perform (OD-58), and no empty commit. The explanation goes to the Dev Manager as DM-59's item 7 ([addendum](https://github.com/amthorn78/glow-dating-app/blob/3240ef0acca7983e5b60b9a111be371ed5a16b74/docs/ephemeral/2026-11-11-dm-59-addendum-chromium-install.md); recommended: (b), the explanation accepted and a one-time retry of the step carried to the next workflow change). PR44 merges only on a passing PR run of its final head (OD-21).
- **Run 43046997028** on `4b2c03a` (the addendum's commit, Markdown only) failed the same way: Mobile checks' Chromium install from 15:20:05 to 15:30:16 UTC, on another runner, with the same nine packages and the same error; the other six jobs passed by 15:25, and the gate failed only for that job. The name-resolution failure lasted at least from 15:03 to 15:30 UTC. Codex's review of `4b2c03a` completed with no findings. The Dev Manager was told in DM-59's relay, which carried DM-59 and its item 7 together, read at `4b2c03a`.

### DM-59, the Dev Manager's pre-merge read

- **The report** (`docs/continuity/dev-manager/reviews/2026-11-11-dm-59-sv2-stage-b-pre-merge.md`, at `d2b46ad`, a read of `4b2c03a`; integrated at the merge `75cf4fc`): the rewritten texts approved with conditions; N-e approved in the manager's words; J1 to J9 and C1 confirmed as applied; the manager workflow's read at `52ae066` standing as PR44's pre-merge read if the file is unchanged at the final head; the carried nits confirmed; item 7's (b) approved. The review log's "DM-59" lists each disposition.
- **L1 to L7,** applied by script from the report's quoted blocks in this batch: each old passage found once, each new text present once. L1 is the data model's F05 unit-of-work row ("reads" added); L2 to L4 the P11 plan's Stage B entry (C2's run of record, the earlier runs, C1's and C2's PV04 evidence and 0008's DB04 case); L5 and L6 revision 8 in the contract document and the media fixtures note; L7 "Carried to the next change to the Foundation workflow".
- **The merge** waits on the PR run of this batch's head, the final head, passing with `Application checks passed`, and on Codex raising nothing new there. If that run's Mobile checks fail at the same step with the same name-resolution error while every other job passes, the manager records the run, makes no commit only to start a run, and makes its next records commit no sooner than an hour after the failure; any other failure goes back to the Dev Manager (DM-59 section 7).
- **Run 43050934985** on `17e441e`, the final head, failed the same way: Mobile checks' Chromium install from 15:43:47 to 15:53:53 UTC, on another runner, with the same nine packages and the same `Temporary failure resolving 'azure.archive.ubuntu.com'`; the other six jobs passed, the Database proof checks among them, and the gate failed only for that job. Codex's review of `17e441e` completed at 15:44 UTC with no findings. Under DM-59 section 7, the run is recorded, no commit is made only to start a run, and the next records commit, this one, came no sooner than an hour after the failure; its pull-request run is the next attempt.

## The merge receipt for Stage B (11 November 2026, App Manager 10)

- **PR44 merged** at 17:08:51 UTC as the merge commit `3240ef0acca7983e5b60b9a111be371ed5a16b74`.
  - Its parents are `4dc2061` (`main`) and `a9a4e05` (PR44's head).
  - It merged by the expected-head guard (`expectedHeadSha` `a9a4e0587129a726132e24682fb6b542b841ed68`), after the pre-merge checklist in PR44's description was filled.
  - `main`'s tree equals `a9a4e05`'s. The final head's non-Markdown paths are byte-identical to C2's code head `5bcbe54`; Stage B's application code is C1's `7538c76`.
- **Its checks:**
  - the trusted policy at `4dc2061` read full scope (`behavior-or-empty`, 69 paths), with one merge base, `4dc2061`;
  - PR run 43063498285 on `a9a4e05` passed all eight jobs. The gate printed `Application checks passed`. The profile suite passed 69 of 69 in 57.6 s, its secret and value scans were clean (1,447 secrets and 813 values held), and its phase took 58 s. A second profile run was refused with the counts `129 129 100 44 1568 1009` unchanged, `sv2-profile-results` (6,365 bytes) was uploaded, and no proof container remained;
  - push run 43063486723 on the same head passed, as a Markdown-only change against its parent;
  - the pull-request runs on `9464dd8` (43044190450), `4b2c03a` (43046997028) and `17e441e` (43050934985), each a Markdown-only head, failed only at Mobile checks' Chromium install on the runners' package-mirror name resolution, from at least 15:03 to 15:53 UTC; their records are above, under DM-59 item 7 and section 7;
  - Codex's code review of `a9a4e05` completed at 17:00:59 UTC with no findings. Its one thread on PR44 (`82d246b`, an inactive owner's purge) was answered by C1 and is resolved;
  - Stage B, corrections C1 and C2, the exact-head review of `7538c76`, C2's delta review and DM-57 to DM-59 are recorded above and in the review log;
  - PR44's governing Markdown, the manager workflow (DM-57 U11), had the Dev Manager's read at `52ae066` (DM-58 section 6); it is unchanged at `a9a4e05`, and DM-59 item 4 confirmed the read stands. DM-59's L1 to L7 were applied as written at `17e441e`.
- **The cleanup run** 43065281784 passed and deleted Stage B's three session branches, each "merged into main":
  - `claude/sweet-ramanujan-wkn311` (`e7d6616`, the implementation);
  - `claude/gracious-davinci-lpqt02` (`e30ef4a`, C1);
  - `claude/eloquent-dijkstra-dmah71` (`9740196`, C2).

  It kept `main`, the manager branch and `claude/dev-manager` by the keep-list. The review sessions pushed no branch.
- **`git ls-remote`** after it (17:09 UTC): `main` at `3240ef0`, the manager branch at `a9a4e05`, `claude/dev-manager` at `d2b46ad`, and nothing else. No PR is open. PR44's activity subscription is ended.
- **`main`'s push run** 43065281916 on `3240ef0` was still running when this receipt was first committed; by then six of its jobs had passed, Mobile checks' Chromium install among them (24 s, the mirror reachable again).
- **The manager branch holds `main`:** fast-forwarded to `3240ef0`, since no commit followed PR44's head, so the next PR's merge base is `3240ef0` (DM-57 item 5).
- **Pruned:** Stage B's eleven prompts and consultations in `docs/ephemeral/`:
  - DM-52's (it consulted on the whole brief), DM-57's, DM-58's with its addendum, and DM-59's with its addendum;
  - the implementation prompt, C1's and C2's prompts, the exact-head review prompt and C2's delta review prompt.

  Their unique content lives in the brief, this record, the review log and the Dev Manager's reports. The eighteen links to them (ten in the brief, six in the review log and two in this record) are pinned at `3240ef0`, where each file exists. Text that names a prompt's path, as this record's session headers do, stays true as history.
- **SV2 is done.** Carried forward:
  - in the carried-items file: to P07 and P07.1, J8 and the exact-head review's N1; to P08, J9; "Carried to the next change to SV2's profile guards and suite" (the delta review's N-a to N-d and N-f); "Carried to the next change to the Foundation workflow" (DM-59's L7, the Chromium install's retry);
  - in the P11 plan: J2, the exact-head review's N3, N4 and N8, and Stage B's entry (L2 to L4).

  To the Dev Manager's next consultation: the confirmation that DM-59's L1 to L7 are applied.


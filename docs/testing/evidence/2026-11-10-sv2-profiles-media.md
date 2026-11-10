# SV2 profiles and media: evidence

- **Work item:** SV2 ([brief](../../planning/sv2-profiles-media.md), revision 3, with [DM-52](../../continuity/dev-manager/reviews/2026-11-10-dm-52-sv2-brief.md)'s and [DM-53](../../continuity/dev-manager/reviews/2026-11-10-dm-53-sv2-stage-a-paths.md)'s conditions; OD-60, OD-61).
- **This record holds Stage A.** Stage B (photos, D10, acceptance check 10) has its own session and section.
- **Sealed:** nothing here is served. The routes run only under the disposable-PostgreSQL proof's profile settings; the served runtime imports none of the new code (D13). Local database runs are iteration, not evidence: the evidence of record is the CI run on the code head.

## Stage A

### The session

- **The prompt:** [Stage A's implementation prompt](../../ephemeral/2026-11-10-sv2-stage-a-implementation-prompt.md), revision 1, from `a6624de1568ed248dc975d9ae3a9e8863969f9b6` of `claude/magical-wozniak-yfmmx2`.
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

- **The prompt:** [C1's correction prompt](../../ephemeral/2026-11-10-sv2-stage-a-c1-correction-prompt.md), revision 1, from `033e8d4cf2ef85bc2b05bfd6b5489852bd2e9fd3` of `claude/magical-wozniak-yfmmx2`.
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

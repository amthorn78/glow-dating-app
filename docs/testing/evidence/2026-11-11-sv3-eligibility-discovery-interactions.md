# SV3: eligibility, discovery and interactions, proven on disposable PostgreSQL

- **Brief:** [SV3](../../planning/sv3-eligibility-discovery-interactions.md), revision 2, with [DM-60](../../continuity/dev-manager/reviews/2026-11-11-dm-60-sv3-brief.md)'s Q1 to Q15 applied.
- **This record** is written by the stage sessions. Each stage has its own section.

## Stage A

- **Session:** SV3 Stage A's implementation session, started by Nathan from [the Stage A prompt](../../ephemeral/2026-11-11-sv3-stage-a-implementation-prompt.md), revision 1, from `aa9ed701c36dce8772fbbf82b1283b6f845421e9` of the manager branch `claude/magical-wozniak-yfmmx2`.
- **Branch:** `claude/loving-maxwell-cqu7eq` (pushes to `claude/**` run the Foundation workflow).
- **Code head:** `ad9ff081e26535ab89eb1187c7b69ca96fac2ef4`. **Records heads:** `1128bf7`, which adds this record, pushed before the code head's run had started, at Nathan's direction, and the records commit that corrects "The run of record", below.
- **What Stage A built:** Outcome items 1 to 3 with the page route (D1 to D8, D13 for Stage A's parts, D14's Stage A cases, D15 to D19), in `services/api/glow_discovery`, with migration 0010, the contract's additive DTOs and the discovery suite on a fourth disposable database. No action route, no `glow_chat` change, no change to `glow_domain/profile_settings.py`, no provider, deployed URL, real member, HDE call or stored credential.

### The start gate and the environment check

- **Environment (names only; no value was read or printed):** none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`; no `STREAM_*` and no `PG*` name; the GitHub token names `GH_TOKEN` and `GITHUB_TOKEN` present, never read. Every repository command ran under `env -i` with `PATH`, `HOME`, `LANG=C.UTF-8` and its own variables (the proxy and CA variables passed by reference for the package installs only).
- **Toolchain:** `python3.12 --version` → `Python 3.12.14`; `node --version` → `v24.19.0`; `npm --version` → `11.9.0`; `docker --version` → `Docker version 29.9.2, build a82e528`.
- **Start gate:** `git switch -C claude/loving-maxwell-cqu7eq aa9ed70…`; `git rev-parse HEAD` → `aa9ed701c36dce8772fbbf82b1283b6f845421e9`; `PR44 present`; the non-Markdown diff against `3240ef0` printed nothing; the owned paths' diff between `aa9ed70` and the live manager branch printed nothing (the live branch was at `aa9ed70`); `glow_discovery` did not exist; migrations `0001` to `0009` only. The brief's "Sessions" recorded no Stage A implementation session.

### What was built, by Outcome item and acceptance check

The cases run in the discovery suite (`proofs/postgres-ordering/glow_ordering_proof/discovery_cases.py`, 32 cases); "Reversals" below gives each reversal's edit and failing line.

| Item or check | Files | Tests | Reversals (all failed as intended unless noted) |
|---|---|---|---|
| **Outcome 1: pair eligibility over the ORM** (D2, D3) | `glow_discovery/eligibility.py` (`OrmEligibilityEvidence`, `OrmPairActionTransaction`), `predicates.py` (`PAIR`) | `adapter.both_ways_agree`; every `_sees` check compares the page with `TrustedEligibilityService` over the adapter | `D3.self`; the candidate-side predicate reversals fail on the page/adapter agreement |
| **Outcome 2: the two-way rule, age and distance** (D4, D5) | `predicates.py` (`sees`, `fields`, `in_range`, `AGE`, `miles`, `distance`) | `two_way.*` (five), `age.range_both_ways`, `age.leap_days_and_age_state`, `distance.zero_boundary_viewer_only` | `D4.*` (7), `D5.same_area_not_zero`, `D5.boundary_off_by_one` |
| **Outcome 3: recommendations and broader** (D6 to D8) | `pages.py`, `policy.py`, `keys.py`, migration `0010_batch_collection.py`, `glow_persistence/models.py` | `pages.*` (nine), `disclosure.*` (two), `plans.population_and_bounds` | `D6.*` (3), `D7.*` (17), `D8.*` (3) |
| **Outcome 8: the page route** (D13) | `views.py`, `urls.py`, `contract.py` | `route.refusals`, `card.fields_area_and_photos`, every page checked against the schema | `D13.*` (7) |
| **Outcome 9: the proof** (D14) | `proofs/postgres-ordering/**` (the discovery suite, settings, scan, offline tests), `.github/workflows/foundation.yml` (the Database proof checks job's steps) | the suite; `tests/test_discovery_offline.py` | `DB04.*` (two); the scan's offline tests |
| **Outcome 10: sealed** (D15) | `services/api/tests/test_discovery_sealed_runtime.py` | four tests | `D15.runtime_imports_discovery`, `D15.runtime_selects_fixture` |
| **Outcome 11: the records** | this record; the data model, the contract document, the three fixture notes, the P11 plan, the contracts README | — | — |
| **Check 1: each predicate** | as Outcome 1 | `predicates.adult_state`, `.consent`, `.profile_states`, `.account_states`, `.blocks`, `.missing_rows` | `D3.*` (17, `D3.adult_not_read` among them); `D3.candidate_adult` did not fail (findings) |
| **Check 2: the two-way rule** | as Outcome 2 | `two_way.each_field_both_directions`, `.keep_all`, `.narrowed_never_not_stated`, `.retired_value`, `.not_narrowable` | `D4.one_direction_of_one_field`, `.all_is_the_current_list`, `.narrowed_matches_not_stated`, `.not_narrowable_ignored` |
| **Check 3: age** | `predicates.py` | `age.range_both_ways`, `age.leap_days_and_age_state` (54 leap-day pairs; no page field names a birth) | `D4.age_from_birth_input`, `.sql_rule_differs_at_leap_day`, `.age_range_one_way` |
| **Check 4: distance** | `predicates.py`; `discovery_support.check_page` | `distance.zero_boundary_viewer_only`, `logs.no_private_value`, the page checks and the scans | `D5.*` (8) |
| **Check 5: pages** | `pages.py`, `keys.py` | `pages.recommended_then_broader`, `.keyed_stable_order`, `.stale_cursors`, `.dropped_between_pages`, `.recheck_is_one_snapshot`, `.empty_and_no_provider_call`, `.port_states`, `.consumption`, `.one_batch_per_collection`, `plans.population_and_bounds` | `D2.recheck_two_statements`, `D6.*`, `D7.*` |
| **Check 6: disclosure** | `contract.py`, `pages.py` | `disclosure.population_of_one`, `disclosure.no_count_reason_or_private_value` | `D8.*`, `D13.show_me_on_card`, `.filter_on_card`, `.hidden_field_shown` |
| **Check 12: ownership** | `views.py` | `route.refusals` (19 refusals), `pages.stale_cursors` (another viewer's cursor), `predicates.account_states` (no actor) | `D7.other_viewer_accepted` |
| **Check 13: no secret or private value** | `discovery_suite.py`, `discovery_scan.py`, the workflow step | the suite's two scans; the job's check; `logs.no_private_value` | `log.own_words`, `log.birth_date`, `D5.coordinate_in_log` |
| **Check 14: one pointer order** (D19) | `pages.py` (`_selection`) | `pointers.name_order`; the settings store's own check at run time | `D19.pointer_out_of_order` |
| **DB04 (partial)** | — | `constraints.batch_writes_are_refused` (15 writes: all 11 constraints 0002 and 0010 declare on the two tables, and three foreign keys) | `DB04.constraint_without_write`, `DB04.unique_constraint_dropped` |

### The contract (D13 (a); DM-60 Q12)

- **New DTOs** (production schema, `$defs`; OpenAPI components, no paths):
  - `CandidateDetails`: `looking_for` (1 to 50 option IDs, always), `gender` and `orientation` (`value_ids` and `own_words`, or null while the flag is off; at least one value unless own words are given), `relationship_status` (`value_ids`, or null), `area_name` (`Text80` or null).
  - `CandidateCard`: `profile_id`, `profile` (`CandidateProfile`, unchanged) and `details`. `profile_id` repeats the profile's own at the card's top level so that the contract's unchanged unique-key rule over `items` (`runtime.py`, `validation.ts`) covers cards; without it `runtime.py` would raise on a card and `validation.ts` would refuse two cards.
  - `CandidateCardPage`: `kind: candidate_card_page`, `collection`, and `CandidatePage`'s other fields and state rules, with `CandidateCard` items. It joins `AppResponse`.
- **No existing DTO changes**, `CandidatePage` and `CandidateProfile` included.
- **The registry:** F07's `response_contracts` and `projection_roles` gain `CandidateCardPage` (`owner`). Examples in `tests/test_transition_contract.py`, `test_sv3_card_page_is_the_viewers_own`: allowed, the viewer with a valid session; forbidden (`not_found`), another member, a revoked session, staff, the system, a provider and the public. The test also pins F07's request, its first response, its six transitions and `CandidatePage`'s projection as they were. No transition is added and no existing entry changes.
- **The corpus:** 54 cases added (709 → 763), all decided alike by Python, the generated validators and the proof's schema check.
- **Generated files** (`npm run generate --prefix packages/contracts`): `apps/mobile/src/contracts/generated/gapp-api-v1.ts`, `validators.js` and `validators.d.ts` changed; `gapp-dev-v1.ts` did not. A further run changed nothing (each file's SHA-256 equal before and after).
- **The contract document:** the F07 index row (`PageRequest → CandidatePage, CandidateCardPage`), a new "F07 on the server" section, and the `location_label` sentence rewritten to say the card shows the area's name and nothing else of the area.

### The query plans (D14; DB11; Q13)

- **The population:** 1,000 members seeded directly in `plans.population_and_bounds`'s setup, each with every row SV2's completion reads (onboarding consent at the current version, the adult age state with its date, a profile with a summary and an area across four areas, gender and "looking for", an approved photo, a resolved chart and an identity verification), every "show me" set at all and the launch filters; `glow_profiles.requirements.missing` was empty for all 1,000. The viewer is built through the routes.
- **The phase:** the plans run in the discovery suite's last case, `EXPLAIN (ANALYZE, BUFFERS)` with a throwaway tie-break key, so no secret is in a plan's text.
- **Labelled:** the disposable setup's measurement (PF01 P09: no extrapolation): PostgreSQL 17.11 in the CI job's container, one run, at 1,000 members; not a capacity claim.
- **Times:** no run of record exists ("The run of record", below), so there are no CI figures. In the local iteration on the fresh database only (iteration, not evidence; `EXPLAIN ANALYZE`'s execution time, one run): the selection 42.1 ms (recommendations) and 41.4 ms (broader), the recheck 4.0 ms, the pair read 0.27 ms, the viewer's read 0.08 ms.
- **Shapes (the same in the local iteration):**
  - **The selection** (recommendations; broader likewise, with an anti-join on the recommendations batch's entries): a bitmap index scan on `profile_visibility_cursor` (state, ID) over the visible profiles; for each, index lookups for the account, age state, consent, preferences, the four fields' set rows (`preference_set_value`) and value rows, blocks, interactions and matches (nested loops and anti-joins); a top-N heapsort on the keyed hash; `LIMIT 100`. Its cost grows with the visible population, which every eligible candidate is evaluated against once per batch (about 53,000 shared buffer hits locally at 1,000). At this size no area-pair table is needed (D5); the measured distance choice is `anywhere`.
  - **The recheck** (a page of 50): an index scan on `batch_position` from the cursor's offset, the same per-candidate lookups for at most 51 entries, `LIMIT 51`.
  - **The pair read** and **the viewer's read:** primary-key and unique-key index scans, one row.
- **Statements per page request** (D7's bound, counted through the connection's execute wrapper, which logs nothing): locally 223 for a recommendations page that creates its batch, 222 for its next page by cursor and 224 for a broader page (no run of record exists to give CI's). Of these, a fixed number belong to the actor and the page's transaction, and four to each card's photo through SV2's `delivery_reference` (its owner's read, then its own transaction): with one photo per seeded member, 50 cards account for 200. The bound is the page's 50 cards times the media policy's live photos (four at launch, at most 20 by its fixed limit).

### The threat model's inputs

**The route and its refusals.** One route, `POST api/v1/discovery/page`, for a signed-in member (SV1's actor: an `active` account, a `valid` unexpired session at the current epoch), on their own batches only.

| Refusal | When | Test |
|---|---|---|
| `unauthenticated`, 401 | no token, a bad token, a suspended or deleted account (the actor) | `route.refusals`, `predicates.account_states` |
| `invalid_request`, 405 | any method but POST | `route.refusals` |
| `invalid_request`, 400 | a query string, another content type, a body that is not `PageRequest` (an extra or missing field, a limit of 0, 51, 1.5 or "5", an unknown collection, a cursor of 101 characters, with a newline or empty, a viewer ID, a body the parser cannot hold) | `route.refusals`, `pages.one_batch_per_collection` |
| `forbidden`, 403 | the viewer fails a predicate (age state, consent, profile state); no batch is created | `predicates.adult_state`, `.consent`, `.profile_states` |
| `stale_version`, 409 (one body for every cause) | a forged cursor, another viewer's, the other collection's, a deleted, expired or not-`ready` batch, the viewer's own versions changed, a setting the selection reads published | `pages.stale_cursors` (ten causes, one response shape), `predicates.consent` |
| `provider_unavailable`, 503 (retryable); `state_conflict`, 409, for an integrity error | a database error or a programming error (a pointer out of order), by type only, as SV2's `tx.run` answers | `D19.pointer_out_of_order`'s and `D7.earlier_batch_kept`'s reversals |

**Each predicate, its source row and its direction** (`predicates.py`; for the viewer and for the candidate unless stated):

| Predicate | Source rows | Direction | Tests |
|---|---|---|---|
| SELF | the two account IDs | the pair | `adapter.both_ways_agree` |
| ACTIVE | `AppAccount.state` | each | `predicates.account_states` |
| ADULT | `AccountAgeState.state` in `{self_declared_adult}`, with its date | each | `predicates.adult_state` |
| CONSENT | the latest `ConsentDecision` with purpose `onboarding`, `accepted` at `consent.onboarding`'s current label | each | `predicates.consent` |
| VISIBLE (and VERIFIED, COMPLETE, MODERATION) | `Profile.state = visible` | each | `predicates.profile_states` |
| PREFERENCE, the four fields | each member's `PreferenceSetEntry` rows against the other's `ProfileFieldChoice.value_ids`, with `profile.narrowing` | both | `two_way.*` |
| PREFERENCE, age | `Preferences.minimum_age`/`maximum_age` against the other's age from `AccountAgeState.birth_date`, with `profile.age_range`'s direction | the viewer's always; the candidate's under `both_ways` | `age.*` |
| PREFERENCE, distance | the viewer's `Preferences.distance_choice` against `profile.location`'s choices, between the two `Area` internal points | the viewer's only | `distance.zero_boundary_viewer_only` |
| BLOCK | `Block` rows, `active`, from each to the other | both | `predicates.blocks` |
| Consumption (D7) | `DirectionalInteraction` from the viewer (`liked`, `passed`); `Match` on the pair in any state | the viewer's | `pages.consumption` |

**What a viewer can see of another member, and what they cannot.**
- **Can:** the profile ID, display name, age in whole years, summary, approved and deliverable photos' delivery references, compatibility `pending`; "looking for"; gender, orientation and relationship status while each flag is on, with the own words for gender and orientation; the area's name. Tested by `card.fields_area_and_photos` and `disclosure.no_count_reason_or_private_value`, which compare every card with the candidate's own rows.
- **Cannot:** a birth date or birth input; a "show me" set; a filter (age range, distance choice); an area ID, an internal point or a distance; a field whose flag is off; an unapproved, removed or held photo; a count; an exclusion reason; who blocked whom; an unreciprocated like; the batch's versions or policy version. Tested by the schema check of every page, `check_page` (no case member's area ID, internal point or distance in any page), the card equality checks, and the reversals `D5.*`, `D8.*` and `D13.*`.

**D8's population-of-one measurement** (`disclosure.population_of_one`): with one candidate, the viewer's gender filter on the candidate's gender showed one card; on another gender, an empty page. The empty page equals an empty market's page in every field but the batch ID and expiry. The card did not show the candidate's gender, because its flag was off. **What the two responses reveal:** the viewer learns that the one member's gender is in the narrowed set, though the card does not show it. OD-60 accepted this ("a viewer who narrows a field learns it for everyone shown"); SV3 does not prevent it. The suite's results JSON holds the measurement's record (`disclosure`).

**The tie-break's key, and why a client cannot compute the order.** Within a band, a batch is ordered by `salted_hmac("glow_discovery.tie_break", "<batch>:<profile>", algorithm="sha256")` under the settings' `SECRET_KEY`. The selection computes it in SQL as HMAC-SHA-256 over PostgreSQL's core `sha256`, with the inner and outer pads derived from `salted_hmac`'s own key (`keys.sql_pads`). `pages.keyed_stable_order` pins the SQL's value to `salted_hmac`'s and the served order to the keyed one. A client knows the batch ID and the profile IDs but not the key, so it cannot compute the order or read band boundaries from it. A new batch has a new ID, so orders say nothing between batches. The pads travel only as statement parameters: the suite's secret ledger holds the derived keys and the pads, and its scan found none in any output. Under the fixture adapter every ready pair is in one band. The cursor's MAC uses the same construction with its own salt, over the viewer's account, the collection, the batch and the offset.

**Each read's statements and their snapshot.**
- **A page with no cursor:** the viewer's account row `FOR UPDATE`; the five pointers `FOR SHARE` in one `read_shared` call (D19); the clock; the viewer's read (`VIEWER`); for broader, the viewer's recommendations batch row; then **the selection, one statement**, the only read of other members' rows, so one snapshot (D2). The batch's writes follow.
- **A page with a cursor:** the viewer's account row `FOR SHARE`; the same pointers; the clock; the batch row and the account's versions; the viewer's read; then **the recheck, one statement**, the only read of other members' rows (DM-60 Q1). Every viewer-side fact is stable for the transaction, because each writer of one takes the viewer's account row first. `pages.recheck_is_one_snapshot` commits two writes from another connection between the locks and the recheck (the candidate states a match again, then pauses) and shows the paused candidate dropped; with the recheck split into two statements, the paused candidate was shown (`D2.recheck_two_statements`).
- **The trusted adapter:** one statement (`PAIR`).
- **Photos:** after the page's transaction, each in its own `delivery_reference` transaction. They are not eligibility facts, and a photo no longer deliverable gives no reference.

### Reversals (D18)

Each reversal is a temporary edit of the committed code, run against its test on the local throwaway database (or the API's tests) and then undone with `git checkout`. The tree was clean after every one. 70 reversals; 69 failed as intended; one did not (the findings).

| Reversal | The temporary edit | Files | Run | Result: the failing line |
|---|---|---|---|---|
| `D2.recheck_two_statements` | the page's recheck split into two statements (the profile states, then the rest) outside one REPEATABLE READ transaction, the probe point between them | `pages.py` | `pages.recheck_is_one_snapshot` | failed as intended: `pages.recheck_is_one_snapshot`: FAILED: never visible-and-matching at one moment: dropped |
| `D3.candidate_adult` | ADULT removed for the candidate | `predicates.py` | `predicates.adult_state` | **did not fail** (see the findings) |
| `D3.candidate_consent` | CONSENT removed for the candidate | `predicates.py` | `predicates.consent` | failed as intended: `predicates.consent`: FAILED: the page and the trusted adapter agree |
| `D3.candidate_visible` | VISIBLE removed for the candidate (the predicate and the selection's scan filter) | `predicates.py` | `predicates.profile_states` | failed as intended: `predicates.profile_states`: FAILED: the page and the trusted adapter agree |
| `D3.candidate_active` | ACTIVE removed for the candidate (the predicate and the selection's scan filter) | `predicates.py` | `predicates.account_states` | failed as intended: `predicates.account_states`: FAILED: the page and the trusted adapter agree |
| `D3.self` | SELF removed | `predicates.py` | `adapter.both_ways_agree` | failed as intended: `adapter.both_ways_agree`: FAILED: a member is never their own candidate |
| `D3.viewer_preference` | PREFERENCE removed in the viewer's direction | `predicates.py` | `two_way.each_field_both_directions` | failed as intended: `two_way.each_field_both_directions`: FAILED: the page and the trusted adapter agree |
| `D3.candidate_preference` | PREFERENCE removed in the candidate's direction | `predicates.py` | `two_way.each_field_both_directions` | failed as intended: `two_way.each_field_both_directions`: FAILED: the page and the trusted adapter agree |
| `D3.block_candidate_to_viewer` | a block read in one direction only (the viewer's): the candidate's block of the viewer ignored | `predicates.py` | `predicates.blocks` | failed as intended: `predicates.blocks`: FAILED: the page and the trusted adapter agree |
| `D3.block_viewer_to_candidate` | a block read in one direction only (the candidate's): the viewer's block of the candidate ignored | `predicates.py` | `predicates.blocks` | failed as intended: `predicates.blocks`: FAILED: the page and the trusted adapter agree |
| `D3.viewer_adult` | ADULT removed for the viewer | `predicates.py` | `predicates.adult_state` | failed as intended: `predicates.adult_state`: FAILED: a viewer outside the accepted states: answers 403 |
| `D3.viewer_consent` | CONSENT removed for the viewer | `predicates.py` | `predicates.consent` | failed as intended: `predicates.consent`: FAILED: a viewer at an old consent version: answers 403 |
| `D3.viewer_visible` | VISIBLE removed for the viewer | `predicates.py` | `predicates.profile_states` | failed as intended: `predicates.profile_states`: FAILED: a paused viewer: answers 403 |
| `D3.viewer_active` | ACTIVE removed for the viewer (the predicate; SV1's actor and the account row lock still refuse at the route) | `predicates.py` | `predicates.account_states` | failed as intended: `predicates.account_states`: FAILED: the viewer's own predicate fails a suspended account |
| `D3.consent_no_current_version` | CONSENT read without the current-version check | `predicates.py` | `predicates.consent` | failed as intended: `predicates.consent`: FAILED: a viewer at an old consent version: answers 403 |
| `D3.consent_no_purpose` | CONSENT read without the purpose filter | `predicates.py` | `predicates.consent` | failed as intended: `predicates.consent`: FAILED: sensitive decisions numbered above it change nothing |
| `D3.missing_row_passes` | a missing row treated as a pass (no preferences row: no range, so any age passes) | `predicates.py` | `predicates.missing_rows` | failed as intended: `predicates.missing_rows`: FAILED: no preferences row fails closed |
| `D4.one_direction_of_one_field` | one direction of one field removed (the candidate's gender set) | `predicates.py` | `two_way.each_field_both_directions` | failed as intended: `two_way.each_field_both_directions`: FAILED: gender: a miss in one direction excludes |
| `D4.all_is_the_current_list` | "all" matching only the lists' values when the set was written, so a value the console adds later is missed | `predicates.py` | `two_way.keep_all` | failed as intended: `two_way.keep_all`: FAILED: keep-all sees a member with no orientation row |
| `D4.narrowed_matches_not_stated` | a narrowed set matching "not stated" (a member with no stated value) | `predicates.py` | `two_way.narrowed_never_not_stated` | failed as intended: `two_way.narrowed_never_not_stated`: FAILED: a missing orientation row is not stated, excluded |
| `D4.age_from_birth_input` | the candidate's age taken from the birth input | `predicates.py` | `age.leap_days_and_age_state` | failed as intended: `age.leap_days_and_age_state`: FAILED: the age state's age decides the range, not the birth input's |
| `D4.sql_rule_differs_at_leap_day` | the SQL rule differing from age_years (days / 365) | `predicates.py` | `age.leap_days_and_age_state` | failed as intended: `age.leap_days_and_age_state`: FAILED: the SQL rule is age_years' at a leap-day case |
| `D4.age_range_one_way` | the age range applied one way under both_ways | `predicates.py` | `age.range_both_ways` | failed as intended: `age.range_both_ways`: FAILED: both ways: the viewer outside theirs |
| `D4.not_narrowable_ignored` | the narrowing setting ignored (a field not narrowable still narrowed) | `predicates.py` | `two_way.not_narrowable` | failed as intended: `two_way.not_narrowable`: FAILED: a field not narrowable reads as keeping all |
| `D5.same_area_not_zero` | two members in one area not at distance zero | `predicates.py` | `distance.zero_boundary_viewer_only` | failed as intended: `distance.zero_boundary_viewer_only`: FAILED: one area is distance zero |
| `D5.boundary_off_by_one` | a boundary off by one mile | `predicates.py` | `distance.zero_boundary_viewer_only` | failed as intended: `distance.zero_boundary_viewer_only`: FAILED: within the boundary, included |
| `D5.area_id_in_response` | an area ID in a response (the card's area name followed by the candidate's area ID) | `contract.py`, `predicates.py` | `distance.zero_boundary_viewer_only` | failed as intended: `distance.zero_boundary_viewer_only`: FAILED: a page carries no member's area ID |
| `D5.coordinate_in_response` | a coordinate in a response (the card's area name followed by the area's internal point) | `contract.py`, `predicates.py` | `distance.zero_boundary_viewer_only` | failed as intended: `distance.zero_boundary_viewer_only`: FAILED: a page carries no internal point or distance |
| `D5.distance_in_response` | a distance in a response (a distance field on the card's profile) | `contract.py` | `distance.zero_boundary_viewer_only` | failed as intended: `distance.zero_boundary_viewer_only`: FAILED: the recommendations page: the body is its DTO |
| `D5.area_id_in_error` | an area ID in an error (the refusal body carries the viewer's area ID) | `views.py` | `pages.stale_cursors` | failed as intended: `pages.stale_cursors`: FAILED: a forged cursor: the body is the contract's Error |
| `D5.coordinate_in_log` | a coordinate in a log line (the viewer's internal point at DEBUG) | `pages.py` | `logs.no_private_value` | failed as intended: `logs.no_private_value`: FAILED: no member value in the DEBUG capture |
| `D5.event_written` | an event written by a page (an outbox event naming the batch) | `pages.py` | `distance.zero_boundary_viewer_only` | failed as intended: `distance.zero_boundary_viewer_only`: FAILED: the pages wrote no outbox event |
| `D6.unkeyed_tie_break` | an unkeyed tie-break, reproducible from the batch's and the profiles' IDs | `predicates.py` | `pages.keyed_stable_order` | failed as intended: `pages.keyed_stable_order`: FAILED: one band: the order is the keyed tie-break's |
| `D6.broader_includes_recommended` | broader including the batch's recommended candidates | `pages.py` | `pages.recommended_then_broader` | failed as intended: `pages.recommended_then_broader`: FAILED: broader leaves the recommended out |
| `D6.unavailable_stops_broader` | the port's unavailable stopping broader | `pages.py` | `pages.port_states` | failed as intended: `pages.port_states`: FAILED: broader still serves them |
| `D7.forged_accepted` | a forged cursor accepted (no MAC check) | `keys.py` | `pages.stale_cursors` | failed as intended: `pages.stale_cursors`: FAILED: a forged cursor: answers 409 |
| `D7.other_viewer_accepted` | another viewer's cursor accepted (the cursor and the batch not bound to the viewer) | `keys.py`, `pages.py` | `pages.stale_cursors` | failed as intended: `pages.stale_cursors`: FAILED: another viewer's cursor: answers 409 |
| `D7.other_collection_accepted` | the other collection's cursor accepted | `keys.py`, `pages.py` | `pages.stale_cursors` | failed as intended: `pages.stale_cursors`: FAILED: the other collection's cursor: answers 409 |
| `D7.expired_accepted` | an expired batch accepted | `pages.py` | `pages.stale_cursors` | failed as intended: `pages.stale_cursors`: FAILED: an expired batch: answers 409 |
| `D7.viewer_versions_ignored` | a batch whose viewer versions changed accepted | `pages.py` | `pages.stale_cursors` | failed as intended: `pages.stale_cursors`: FAILED: the viewer's own change: answers 409 |
| `D7.policy_version_ignored` | a batch whose policy version changed accepted | `pages.py` | `pages.stale_cursors` | failed as intended: `pages.stale_cursors`: FAILED: a discovery setting published: answers 409 |
| `D7.earlier_batch_kept` | a deleted batch's cursor / an earlier batch of the same collection left in place (no deletion; the unique constraint then refuses the second batch) | `pages.py` | `pages.one_batch_per_collection` | failed as intended: `pages.one_batch_per_collection`: FAILED: the recommendations page: answers 200 |
| `D7.policy_version_without_consent.onboarding` | a publication of consent.onboarding leaving the batch's policy version unchanged | `policy.py` | `predicates.consent` | failed as intended: `predicates.consent`: FAILED: a cursor after a new consent: answers 409 |
| `D7.policy_version_without_discovery.resurfacing` | a publication of discovery.resurfacing leaving the batch's policy version unchanged | `policy.py` | `pages.stale_cursors` | failed as intended: `pages.stale_cursors`: FAILED: a discovery setting published: answers 409 |
| `D7.policy_version_without_profile.location` | a publication of profile.location leaving the batch's policy version unchanged | `policy.py` | `pages.stale_cursors` | failed as intended: `pages.stale_cursors`: FAILED: a profile setting published: answers 409 |
| `D7.like_not_consumed` | a seeded like not excluding | `predicates.py` | `pages.consumption` | failed as intended: `pages.consumption`: FAILED: recommendations: consumed pairs excluded |
| `D7.pass_not_consumed` | a seeded pass not excluding | `predicates.py` | `pages.consumption` | failed as intended: `pages.consumption`: FAILED: recommendations: consumed pairs excluded |
| `D7.match_active_not_consumed` | a seeded active match not excluding | `predicates.py` | `pages.consumption` | failed as intended: `pages.consumption`: FAILED: recommendations: consumed pairs excluded |
| `D7.match_restricted_not_consumed` | a seeded restricted match not excluding | `predicates.py` | `pages.consumption` | failed as intended: `pages.consumption`: FAILED: recommendations: consumed pairs excluded |
| `D7.match_unmatched_not_consumed` | a seeded unmatched match not excluding | `predicates.py` | `pages.consumption` | failed as intended: `pages.consumption`: FAILED: recommendations: consumed pairs excluded |
| `D7.page_over_50` | a page over 50 items | `contract.py` | `pages.one_batch_per_collection` | failed as intended: `pages.one_batch_per_collection`: FAILED: a page of 51: answers 400 |
| `D7.batch_over_100` | a batch over 100 (101 selected; the entry's position constraint then refuses it) | `pages.py` | `plans.population_and_bounds` | failed as intended: `plans.population_and_bounds`: FAILED: the recommendations page: answers 200 |
| `D8.count_in_response` | a count in a response | `contract.py` | `disclosure.no_count_reason_or_private_value` | failed as intended: `disclosure.no_count_reason_or_private_value`: FAILED: the recommendations page: the body is its DTO |
| `D8.reason_in_response` | a reason in a response (an empty page saying why) | `contract.py` | `pages.empty_and_no_provider_call` | failed as intended: `pages.empty_and_no_provider_call`: FAILED: the recommendations page: the body is its DTO |
| `D8.private_value_in_response` | another member's private value in a response (the candidate's minimum age in the display name) | `contract.py`, `predicates.py` | `disclosure.no_count_reason_or_private_value` | failed as intended: `disclosure.no_count_reason_or_private_value`: FAILED: exactly the profile's own |
| `D13.show_me_on_card` | a "show me" set on the card (the candidate's looking-for set merged into the shown values) | `contract.py`, `predicates.py` | `disclosure.no_count_reason_or_private_value` | failed as intended: `disclosure.no_count_reason_or_private_value`: FAILED: exactly the displayed fields |
| `D13.filter_on_card` | a filter on the card (the candidate's distance choice among the shown values) | `contract.py`, `predicates.py` | `disclosure.no_count_reason_or_private_value` | failed as intended: `disclosure.no_count_reason_or_private_value`: FAILED: exactly the displayed fields |
| `D13.area_id_on_card` | an area ID on the card | `contract.py`, `predicates.py` | `card.fields_area_and_photos` | failed as intended: `card.fields_area_and_photos`: FAILED: a page carries no member's area ID |
| `D13.point_on_card` | an internal point on the card | `contract.py`, `predicates.py` | `card.fields_area_and_photos` | failed as intended: `card.fields_area_and_photos`: FAILED: a page carries no internal point or distance |
| `D13.distance_on_card` | a distance on the card | `contract.py` | `card.fields_area_and_photos` | failed as intended: `card.fields_area_and_photos`: FAILED: the recommendations page: the body is its DTO |
| `D13.hidden_field_shown` | a field whose shown flag is off shown on the card | `contract.py` | `disclosure.no_count_reason_or_private_value, card.fields_area_and_photos` | failed as intended: `disclosure.no_count_reason_or_private_value`: FAILED: no set, hidden field or filter value on the card |
| `D13.unapproved_photo_on_card` | an unapproved photo's reference on the card (every asset listed, the original's key standing in for a missing reference) | `pages.py`, `predicates.py` | `card.fields_area_and_photos` | failed as intended: `card.fields_area_and_photos`: FAILED: approved, deliverable photos only |
| `D15.runtime_imports_discovery` | the runtime importing glow_discovery | `urls.py` | `tests.test_discovery_sealed_runtime` | failed as intended: FAIL: test_no_runtime_module_names_the_discovery_slice (tests.test_discovery_sealed_runtime.DiscoverySealedRuntimeTests.test_no_runtime_module_names_the_discovery_slice) (module='urls.py') |
| `D15.runtime_selects_fixture` | the runtime selecting the fixture compatibility provider | `settings.py` | `tests.test_discovery_sealed_runtime` | failed as intended: FAIL: test_no_runtime_module_names_the_discovery_slice (tests.test_discovery_sealed_runtime.DiscoverySealedRuntimeTests.test_no_runtime_module_names_the_discovery_slice) (module='settings.py') |
| `log.own_words` | own words logged (each card's field rows at DEBUG) | `pages.py` | `logs.no_private_value` | failed as intended: `logs.no_private_value`: FAILED: no member value in the DEBUG capture |
| `log.birth_date` | a birth date logged (the viewer's age state's date at DEBUG) | `pages.py` | `logs.no_private_value` | failed as intended: `logs.no_private_value`: FAILED: no member value in the DEBUG capture |
| `D19.pointer_out_of_order` | a pointer taken out of name order (profile.location before the selection's call) | `pages.py` | `pointers.name_order` | failed as intended: `pointers.name_order`: FAILED: the recommendations page: answers 200 |
| `D3.adult_not_read` | ADULT removed where the age state's state is read (the member's adult column true for the viewer and the candidate, in the pages and the adapter) | `predicates.py` | `predicates.adult_state` | failed as intended: `predicates.adult_state`: FAILED: by the adult rule |
| `DB04.constraint_without_write` | one declared constraint left without its write (batch_one_per_collection's) | `discovery_cases.py` | `constraints.batch_writes_are_refused` | failed as intended: `constraints.batch_writes_are_refused`: FAILED: a write for every constraint the two tables declare |
| `DB04.unique_constraint_dropped` | the `batch_one_per_collection` write changed to one the schema allows (the viewer's other collection), so the constraint is not shown refusing | `discovery_cases.py` | `constraints.batch_writes_are_refused` | failed as intended: `constraints.batch_writes_are_refused`: FAILED: PostgreSQL refuses the write by batch_one_per_collection |

### Commands and results

**API** (`services/api`; `python3.12 -m venv .venv`, `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`; then with `GLOW_ENV=test`):
- `manage.py check` → `System check identified no issues (0 silenced).`
- `manage.py test tests --verbosity 2` → `Ran 583 tests`, `OK`.
- `smoke.py` → `PASS /health/ready: HTTP 503`, `PASS /api/v1/development/recommendations: HTTP 200`.
- `ruff check .` → `All checks passed!`; `ruff format --check .` → `156 files already formatted`; `mypy` → `Success: no issues found in 92 source files`.
- `python -m glow_persistence.static_check` → `Static definitions agree: 42 app models; migrations=0001_event_infrastructure,…,0010_batch_collection`.
- `python -m django makemigrations --check --dry-run glow_persistence` under `glow_persistence.static_settings` → `No changes detected in app 'glow_persistence'`.

**The contracts** (`packages/contracts`; `npm ci --ignore-scripts`):
- `npm run generate` (twice) → `Generated types and runtime validators.`; the second changed nothing.
- `npm run check` → `Generated types and runtime validators match schemas.`; `tests 763`, `pass 763`, `fail 0`.
- `PYTHONPATH=. .venv/bin/python -m unittest discover -s ../../packages/contracts/tests` (from `services/api`) → `Ran 50 tests`, `OK`.

**The mobile app** (`apps/mobile`; `npm ci --ignore-scripts`): `npm run check` → `tests 691`, `pass 691`, `fail 0`, with `tsc --noEmit` and `eslint .`; no mobile source changed.

**The proof** (`proofs/postgres-ordering`; its venv, `pip install --require-hashes -r requirements-dev.lock`, `pip check` → `No broken requirements found.`):
- `env -i … python -m unittest discover -s tests -t .` → `Ran 248 tests`, `OK` (rerun on the code head `ad9ff08`, as were the API's tests: `Ran 583 tests`, `OK`).
- `ruff check .` → `All checks passed!`; `ruff format --check .` → formatted; `mypy` → `Success: no issues found in 66 source files`.
- The workflow file parsed (js-yaml from the mobile app's locked modules): the Database proof checks job has 30 steps, its timeout still 30 minutes, and every hunk of the workflow's diff lies inside that job.

### Local database runs (iteration, not evidence)

P06.DB's D4 conditions: a throwaway PostgreSQL from the CI job's pinned image (`postgres@sha256:d74eeac9…ec46f`, pulled from Docker Hub), on `127.0.0.1:5433` only, started with a local `dockerd`. A generated password, a generated marker as the database's comment (`glow_discovery_proof`), and generated keys sat in a 0700 directory under the session's scratchpad. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name was present. At 21:13 UTC the local Docker daemon, the container and their data were already gone (no `dockerd` process, no Docker data directory, nothing listening on port 5433); this session did not remove them, and does not know what did. The credential files were then removed with the session's teardown script.
- **First database:** `migrate` from zero; `makemigrations --check --dry-run` → `No changes detected`. The suite → `29/31` (two test bugs, fixed: a suspended candidate's own profile read, now cached; a cursor the case itself invalidated by paging the target first). Every reversal ran on this database.
- **Second, fresh database:** `migrate` from zero; `No changes detected`; `[discovery] cases: 32/32 passed in 127.0 s`; `discovery secret scan: clean (1099 secrets held; 0 found in 647 log records, 66 writes and the results JSON)`; `discovery value scan: clean (603 member values held …; 0 found in the same output)`; `DISCOVERY VERDICT: PASS`; a second run → `refusing a used database: …`, exit 1.

### The run of record

- **The code head's run did not start.** Foundation run [43096394432](https://github.com/amthorn78/glow-dating-app/actions/runs/43096394432), on the push of `ad9ff08` at 20:29:52 UTC, stayed `queued` with no job created (still none at 20:56, 21:07, 21:12 and 22:19 UTC). Read at 20:44 UTC, GitHub's status page showed Actions operational and a Webhooks incident from 20:22 to 20:26 UTC, resolved before the push; a critical Actions incident was declared four minutes later (the diagnostic, below). The prompt forbids this session to re-run or dispatch a run, and the push rule forbids any push before the run has finished.
- **Nathan's direction**, asked in this session. The first question overstated the wait as about 55 minutes; by the clock it had been about 25. Of four options (he re-runs it; keep waiting; push the records now; stop and report), he chose "Push records now". Asked again at 20:56 UTC with the corrected 26 minutes, he chose **"Yes, push records now"**. The records commit `1128bf7`, Markdown only, was pushed at 21:07:40 UTC. This departs from the push rule. The question rested on two statements of this session's, both wrong:
  - **That the records commit's run would be the run of record. It is not.** Foundation run [43100390225](https://github.com/amthorn78/glow-dating-app/actions/runs/43100390225), on `1128bf7`, concluded `success` in about a minute, but its Change scope job classified the push's own diff (`ad9ff08`..`1128bf7`, eight Markdown files) as `ordinary-docs-only`, and every application job (API checks, Mobile checks, API mobile smoke, API artifact checks, Stream proof checks, Database proof checks) was skipped; only Change scope and the Foundation gate ran. A push is classified by its own diff (`github.event.before` to the head), which this session did not check before saying so. That run checked none of Stage A's code.
  - **That the workflow's concurrency group would cancel the queued run.** It did not: at 21:12 UTC run 43096394432 was still `queued`, with no job.
- **No run of record exists** for Stage A's code. This session then offered Nathan a re-run of 43096394432. That was a process error: the manager workflow ("Actions re-runs") and OD-58 say no one asks Nathan to perform a GitHub operation, a re-run included. He declined (*"I am not running jobs manually, if there is something causing hangs I suspect there is a CI defect"*) and asked for a diagnostic and the session report to the manager. The diagnostic follows. Pushing these records commits is a further departure from the push rule, since the code head's run will not finish; it is left to Nathan's word. A push cannot cancel that run (the push of `1128bf7` did not).

#### Diagnostic: why the code head's run never started

Read with the GitHub tools (read only) and GitHub's public status feed, 21:12 to 22:19 UTC.

- **The run:** 43096394432 (run number 1043), `push`, attempt 1, created 20:29:52 UTC for the push that created the branch (`ce873a9` to `ad9ff08`, five commits). `status: queued`; `updated_at` equals `created_at` (never touched again); zero jobs; no billable usage (`billable: {}`). Still so at 22:19 UTC.
- **Not the workflow file.** The next push's run, 43100390225 (run number 1044, 21:07:41 UTC), used the identical workflow (`git diff ad9ff08 1128bf7 -- .github` is empty). GitHub created all eight of its jobs, two ran and six were skipped by their conditions, and it finished in 62 s. A YAML or expression error ends a run at start-up (`startup_failure`) rather than leaving it queued. The first job, Change scope, is unchanged by Stage A.
- **Not a branch-creating push.** SV2 Stage B C2's run 42990527042 (08:52:48 UTC, `5bcbe54`), the first run on its branch, started every job and finished in 10.5 minutes.
- **Not the concurrency group.** A run waiting on `foundation-refs/heads/claude/loving-maxwell-cqu7eq` would have been cancelled by run 1044 (`cancel-in-progress: true`), and run 1044 would not have run first. Run 1043 was not cancelled, so it never entered the group.
- **Not runner capacity.** A run waiting for a runner has jobs in `queued`; this run has none.
- **Nothing else in the repository was stuck.** Of its 30 most recent runs (04:13 to 21:08 UTC), run 1043 is the only one not `completed`.
- **GitHub's incidents** (status feed, read at 22:04 UTC): "Incident with Webhooks", minor, 20:22:20 to 20:26:23 UTC, about four minutes before the push; then a critical incident, *"Impact across multiple GitHub products including Actions, Pages, and Copilot products"* (components Actions, Pages, Webhooks and Copilot), declared at 20:48:12 UTC, 18 minutes after the push. It reported Actions *"experiencing degraded availability"* at 20:48:25 and the degradation mitigated at 21:07:24, and at 21:21:32 *"The backlog of Actions jobs has been fully processed"*. It was resolved at 21:21:39. Run 1043 was not in that recovery: it still had no job an hour after it.
- **Conclusion.** No defect in the repository's CI is shown: the same workflow, on the same branch, ran normally one push later. Run 1043 was created on GitHub's side and never dispatched, inside a period of two GitHub incidents touching Webhooks and Actions. That GitHub's degradation caused it is an inference from the timing, not proven; GitHub does not expose why a run was not dispatched. Whether GitHub will ever end the run is not known.
- **Two gaps in the procedure, not defects of the workflow.** Both are as designed, and changing either is a CI-policy decision for the manager and the Dev Manager, outside this session's owned paths:
  - The Foundation workflow has no `workflow_dispatch` trigger. Under OD-58 no one asks Nathan to re-run, and the manager workflow forbids an empty commit. So when a push's run is never dispatched, the only routes to a full run on that head are a new code push or the pull request's run.
  - A push is classified by its own diff, so a Markdown-only push after such a code push certifies nothing about the code. The pull request's run classifies the whole pull request and is full scope ("A documentation-only last commit does not exempt a code PR", the CI policy).

### Findings, deviations and limits

- **`D3.candidate_adult` did not fail, and why.** Removing ADULT from the candidate's side of the page's predicate leaves the candidate excluded anyway. A state outside the accepted set has no date (the `age_state_birth_date` constraint), so the candidate has no age and fails the age range too. ADULT is therefore enforced twice for a candidate and cannot be removed alone observably. The variant `D3.adult_not_read`, which removes the age state's state wherever it is read (the pages and the adapter), fails on the adapter's reason (`by the adult rule`). The viewer's side (`D3.viewer_adult`) fails on its 403.
- **The viewer's ACTIVE** is enforced three times: SV1's actor (401), the page transaction's account lock (`account_not_active`), and the predicate. `predicates.account_states` therefore also runs the viewer's own statement for a suspended account, which `D3.viewer_active` makes fail.
- **The band:** the fixture adapter's result carries no band, so every ready pair is in one band (`policy.FIXTURE_BAND`) and the keyed tie-break orders recommendations. The case `pages.keyed_stable_order` proves the order in the database. Ordering by band first is proven in the API's offline test (`RankingTests`, two bands); `compatibility.py` is not an owned path. HDE's band is P11's.
- **The port's states:** any `unavailable` result makes the recommendations batch `unavailable`, any `pending` makes it `pending` (each with no items), and `unsupported` leaves a pair out. The fixture's case applies to every pair, so mixed states are not exercised.
- **No `CompatibilitySnapshot` is written.** The entry's snapshot field stays null (D6 allows a fixture snapshot; none is needed).
- **`discovery.resurfacing`** is one of the five settings the batch's policy version is made of (Q3 names "each `discovery.*` setting it uses"). Stage A applies no resurfacing: a pass excludes for good, as with the setting off at launch. Stage B applies its content.
- **A viewer who fails a predicate** gets `forbidden` (403) and no batch, rather than an empty page (D3: "gets no page"). Their own state is theirs to know.
- **The stale response** is the contract's `Error` with `stale_version` (409), one body for every cause. A `CandidateCardPage` with state `stale` is never served: Stage B's consumption marks the batch `stale`, and the cursor is then refused like any other.
- **The card's `profile_id` at the card's top level** is a design detail forced by the unchanged unique-key rule (above); the two IDs are always equal, which every page check asserts.
- **Photos are read after the page's transaction**, through SV2's `delivery_reference`, which refuses to run inside one; four statements per photo; a photo no longer deliverable gives no reference.
- **Case isolation** in the suite pauses every `visible` profile left by earlier cases with a direct write to the disposable database (test data, never an application writer), since discovery reads the whole population.
- **Seeds in setup** (test data, as SV2's suite seeds): the chart and identity rows, directional interactions and matches (consumption is read, not written, in Stage A), a lagging age state or consent row, profile states no member route reaches (`removed`, back to `visible`), an account back to `active` after suspension or deletion, a batch's expiry in the past, and the plans' population.
- **The commit message of `ad9ff08`** says the suite has 31 cases; it has 32 (the constraints case was added, and the commit amended, before the push). The record and the pinned count are 32.
- **Not run here:** the mobile app's export and rendered checks, and `playwright install` (CI's, and CI has run none of its checks on Stage A's code: "The run of record"); any provider, HDE, Stream or Railway call; `proofs/stream-chat`. Stage B's checks 7 to 11 and the concurrency cases DB05 and DB10's action half are Stage B's.

## Manager verification of Stage A

- **Who and when:** App Manager 11, 11 November 2026, from 22:29 UTC (the clock at its first command) to 22:38 UTC, on the session's branch `claude/loving-maxwell-cqu7eq` at `4dee875` (code head `ad9ff08`; records `1128bf7`, `3b8185f`, `4dee875`), integrated into the manager branch by fast-forward (`aa9ed70` to `4dee875`).
- **Scope:** `git diff --stat aa9ed70 4dee875`: 45 files, 18,356 insertions and 5,127 deletions, most of both in the regenerated `validators.js`. Every path is in Stage A's owned set. `glow_api`, `glow_chat`, `glow_identity`, `glow_profiles` and `glow_domain` are unchanged; so are `glow_domain/profile_settings.py` and `glow_chat/contact.py`, which are Stage B's. `services/api/pyproject.toml` changes only mypy's `files` (adding `glow_discovery`), and `proofs/postgres-ordering/pyproject.toml` only gains a mypy override for `glow_discovery`. The model change is `RecommendationBatch.collection`, with its check and the one-batch-per-collection unique constraint, in migration `0010_batch_collection`. The registry change is F07's added `CandidateCardPage` response with its `owner` projection; no existing entry or DTO changes.
- **Classification:** full scope (code, a migration, a contract change, a workflow change and the proof).
- **The workflow diff, read whole:** only the Database proof checks job's steps change.
  - The credentials step adds the fourth marker and `SECRET_KEY`, both masked, the distinctness check over all four markers, the database and its passfile line, and the discovery JWT key, written by Python straight to a 0600 file.
  - The role step's name and echo count four databases.
  - Three new steps follow the profile suite: the other three markers refused on the new database, then the migrations from zero and `makemigrations --check --dry-run`; the suite, timed, with its own scan before any output is shown; and a second run's refusal with six row counts unchanged.
  - The upload of `sv3-discovery-results` runs only when the scan passed.
  - The job's timeout is unchanged (30 minutes). No other job, trigger or permission changes.
- **Re-run here,** in a clean worktree of `4dee875`, in clean process environments:

| Check | Result |
|---|---|
| API (`GLOW_ENV=test`): `manage.py check`; `manage.py test tests` | no issues; 583 tests, OK |
| API: ruff, format, mypy, static check, smoke | clean; 156 files formatted; mypy no issues in 92 files; the static check's limits line; smoke `PASS` |
| Contracts: `npm run check` | "Generated types and runtime validators match schemas"; 763/763 |
| Contracts: Python tests | 50, OK |
| Mobile: `npm run check` | 691/691 |
| Proof: `pip check`; offline tests; ruff; format; mypy | no broken requirements; 248, OK; clean; 66 files formatted; no issues in 66 files |
| The worktree after every check | clean (`git status` empty) |

  The contracts' corpus test first failed here with `Cannot find module 'ajv/dist/runtime/ucs2length'`: it loads the mobile app's generated validators, which need `apps/mobile`'s packages. After `npm ci --ignore-scripts` in `apps/mobile` it passed. That was this verification's setup, not the code.
- **Reversals re-run here** (offline, each restored and the tree clean afterwards):
  - the cursor's MAC without the collection: `KeyTests.test_a_cursor_is_bound_to_its_viewer_collection_batch_and_offset` fails;
  - the card ignoring a field's `shown` flag: `ContractTests.test_the_card_shows_only_what_display_allows` fails.

  The database reversals were not re-run: this container's Docker daemon is not running. CI's run on the PR is their check.
- **The code, read against the brief:**
  - `predicates.py` is one source for the selection, each page's recheck and the adapter's pair read. Each predicate holds for both members, fails closed (`IS TRUE`), and checks blocks in both directions. Distance applies in the viewer's direction only, a choice the setting does not offer fails, and nothing selects a birth date, a coordinate, an area ID or a distance.
  - The selection and the recheck are each one statement (D2, Q1). A page with a cursor writes nothing.
  - The batch's policy version is made of the five settings the selection reads, in name order (Q3).
  - The cursor's MAC covers the viewer, the collection, the batch and the offset, and every stale cause gives one `stale_version` response (Q4). Creating a batch deletes the viewer's earlier batch of that collection (Q5's bound).
  - The card goes through `profile_fields.displayed` and never carries a set, a filter, an area ID or a distance (Q12).
- **The session's findings, dispositioned:**
  - `D3.candidate_adult` not failing: accepted. ADULT is enforced twice for a candidate, because a state outside the accepted set has no date and so no age. When P09.2 adds an accepted state with a date, the candidate-side reversal becomes observable and is run again (carried with Q18).
  - The other design details in its "Findings" (one band from the fixture, no snapshot written, resurfacing not applied in Stage A, a 403 for an ineligible viewer, one stale body, the card's repeated `profile_id`) are within the brief.
  - The commit message's "31 cases" for 32: a nit; the record and the pinned count say 32.
- **For the exact-head review, and the Dev Manager's pre-merge read:**
  - **V1, the tie-break's key in SQL parameters.** The selection computes the keyed tie-break in SQL (`predicates.TIE_BREAK`), with the HMAC key's inner and outer pads passed as statement parameters (`keys.sql_pads`). The pads are the derived tie-break key itself, XORed with constants. A server that logs statement parameters would record them, for example PostgreSQL's `log_min_duration_statement` or Django's query log under `DEBUG`. Anyone holding them could compute the order, the band leak Q2 closes. The derived key is `sha256(salt + SECRET_KEY)`, which does not reveal `SECRET_KEY`. The review checks whether any logging path records them, and the Dev Manager rules on whether this is acceptable or needs a different key (for example a per-batch random salt kept in the batch row and never returned).
  - **V2, statements per page.** 222 to 224 statements per page request, mostly SV2's `delivery_reference`, run once per photo after the page's transaction (four statements a photo; at most 50 cards and the media policy's live photos). The count is bounded, as D7 requires, and DB11 measures it in P11. A nit, for the review to weigh.
- **The run of record:** none yet. Run 43096394432 on `ad9ff08` is still `queued` with no jobs (read between 22:29 and 22:38 UTC), and run 43100390225 on `1128bf7` checked no code (above). Under the manager workflow's step 5 ("Push runs as evidence"), the run of record is the pull-request run on the manager branch's head. That head's non-Markdown paths are byte-identical to `ad9ff08`'s. No re-run is asked of anyone (OD-58).
- **The session's process notes:** it pushed `1128bf7` before the code run finished, at Nathan's word, on two wrong statements of its own, and offered Nathan a re-run. All are recorded above by the session. The two procedure gaps it names go to the Dev Manager with the pre-merge read: Foundation has no `workflow_dispatch` trigger, and a Markdown-only push certifies no code.

### The run of record for Stage A (PR45)

- **Pull-request run [43113579295](https://github.com/amthorn78/glow-dating-app/actions/runs/43113579295)** on `88f9299` (PR45's head; its non-Markdown paths byte-identical to `ad9ff08`), 22:39:24 to 22:47:38 UTC.
  - **Jobs:** all eight passed: Change scope, API checks, Mobile checks, API mobile smoke, API artifact checks, Stream proof checks, Database proof checks and the Foundation gate.
  - **The gate:** it printed `Application checks passed`.
  - **Retries:** none fired; the setup-python retry steps were skipped, and the Chromium install passed at the first attempt.
- **The discovery phase** (read in the job's log by App Manager 11):
  - the three other markers were refused on `glow_discovery_proof`, and the migrations applied from zero;
  - `[discovery] cases: 32/32 passed in 52.4 s`;
  - both scans clean: "1099 secrets held; 0 found in 647 log records, 66 writes and the results JSON", and "603 member values held … 0 found";
  - statements per page request: 224, 223 and 222;
  - the five plans at 1,000 members: pair 0.131 ms; recheck of a page of 50, 1.845 ms; broader selection 25.274 ms; recommendations selection 27.884 ms; viewer 0.045 ms (the disposable setup's measurement);
  - `discovery phase: 53 s (the job's timeout is 30 minutes)`;
  - the second run refused ("refusing a used database"), with its six row counts unchanged (1097 1097 1094 47 274 1368);
  - `sv3-discovery-results` uploaded after the scan passed (artifact 13897074594).
- **The other suites** in the same job passed: the ordering suite, the identity suite and the profile suite.
- **Codex** reviewed `88f9299` at 22:42:36 UTC with no findings and nothing unresolved.

### Codex on `7e4d826`: CX1, a lock cycle in page creation

- **Codex's review of `7e4d826`** (the commit that holds the review prompt; its code is identical to `88f9299`'s) completed at about 23:43 UTC with one P2 ([thread](https://github.com/amthorn78/glow-dating-app/pull/45#discussion_r4544471290), `services/api/glow_discovery/pages.py:207`). In Codex's words: *"When two mutually eligible members create discovery batches concurrently, each transaction takes `FOR UPDATE` on its own account here and then inserts a `RecommendationEntry` referencing the other account. PostgreSQL's foreign-key checks require `FOR KEY SHARE` on those referenced accounts, which conflicts with the other transaction's `FOR UPDATE`, creating a deadlock. `glow_profiles.tx.run` converts the aborted transaction into `provider_unavailable` without retrying, so otherwise valid page requests intermittently return 503."*
- **The manager's verification:** confirmed in the code.
  - `pages.create` takes `lock_account` (`FOR UPDATE`) on the viewer, then `bulk_create`s entries referencing the candidates' `AppAccount` rows.
  - The foreign-key check's `FOR KEY SHARE` conflicts with `FOR UPDATE`.
  - The manager also found a second cycle. A `glow_chat` pair writer (`block`, `unblock`, `unmatch`, `activate_match`) holding a candidate below the viewer `FOR UPDATE` waits for the viewer, while the page waits for the candidate. The proof has no concurrent page-creation case, so neither shows in a run.
- **Disposition:** its fix changes the lock design, and the cleanest one reaches `glow_chat` and `glow_profiles`, outside Stage A's owned paths. It goes to the Dev Manager as [DM-61](../../ephemeral/2026-11-11-dm-61-sv3-stage-a-lock-cycle.md), with V1, before any correction (step 6). The exact-head review's prompt is held, to be revised for the corrected head (23:46 UTC).

### Codex on `1ffff7d`: CX2, the tie-break key in a statement's text

- **Codex's review of `1ffff7d`** (the commit that holds C1's prompt, revision 1; its code is identical to `88f9299`'s) completed at about 00:37 UTC on 12 November with one P2 ([thread](https://github.com/amthorn78/glow-dating-app/pull/45#discussion_r4544820991), `services/api/glow_discovery/eligibility.py:67`). In Codex's words: *"If a selection errors or is cancelled, these HMAC pads can reach PostgreSQL's server log: the proof's Django/psycopg configuration uses default client-side binding, which embeds the parameters in the SQL text, and PostgreSQL logs failing statements by default. Either pad reveals the derived tie-break key, allowing a log reader to compute every batch's secondary ordering and infer compatibility-band boundaries when multiple bands are served. The application's output scans do not inspect the database server log."* It asks for the database-generated random order "as the correction plan specifies".
- **The manager's verification:** confirmed.
  - `eligibility.parameters` (lines 55 to 71) puts `keys.sql_pads()`'s two pads into every selection's parameters.
  - Both lock files pin Django 5.2.17 and psycopg 3.3.6, and no database setting sets `server_side_binding`, so Django's psycopg 3 backend binds on the client and the pads are in the statement's text.
  - PostgreSQL's default `log_min_error_statement` is `error`, so a failing or cancelled statement's text is logged.
  - This is V1 as DM-61 widened it (its item 2), and needs no logging setting.
- **Disposition:** K2 already removes the key from SQL and C1 carries it, so there is no new decision and no consultation. Revision 1 of C1's prompt named the tie-break's files without `eligibility.py` (AM11-09). Revision 2 names it and its parameters, adds CX2 to the prompt's background, and has the tie-break check cover the statement's text as sent. The thread stays open until Codex reads C1's head (00:41 UTC).

### Codex on `a919dea`: CX3, a card's age above the contract's maximum

- **Codex's review of `a919dea`** (the commit that holds C1's prompt, revision 2; code unchanged since `ad9ff08`) completed at about 00:45 UTC with one P2 ([thread](https://github.com/amthorn78/glow-dating-app/pull/45#discussion_r4544877615), `services/api/glow_discovery/contract.py:119`). In Codex's words: *"If a visible member has an accepted birth date more than 150 years ago, this emits a card that violates `CandidateProfile.age`'s maximum of 150. This state is not excluded upstream: `adult_outcome()` only checks the lower age bound, the default preference range has no maximum, and discovery's predicates impose no upper bound. For example, `1800-01-01` passes the adult check but projects age 226 on the review date. One such candidate makes the entire page invalid for schema-validating consumers."*
- **The manager's verification:** confirmed.
  - The production schema's `BirthInput` and `AdultCheckIntent` accept any `YYYY-MM-DD` date except year `0000`, and `glow_domain.identity.adult_outcome` refuses only a future date and an age under 18.
  - The launch default `profile.age_range` has `default_maximum: None` (migration 0007), and `predicates.in_range` treats a null `maximum_age` as no upper limit.
  - `predicates.AGE` computes whole years, and `RECHECK` recomputes it on every page; `contract.card` emits `int(row["age"])` against `CandidateProfile.age`'s `minimum 18, maximum 150`.
  - No middleware or view validates the response, so the page goes out and fails as a whole in the app's validator.
  - The bound exists as `glow_domain.profile_settings.AGE_CEILING = 150`.
- **Disposition:** a defect in Stage A's own code, fixed before the merge (fix or carry, (a)). The fix touches a contract and the eligibility design, so it goes to the Dev Manager as [DM-62](../../ephemeral/2026-11-12-dm-62-sv3-stage-a-age-bound.md), with a recommended discovery predicate at `AGE_CEILING` in C1. C1's prompt, revision 2, is held, and revision 3 follows DM-62's answer (00:49 UTC).

## Stage A, correction C1

- **Session:** SV3 Stage A's correction C1, started by Nathan from [C1's prompt](../../ephemeral/2026-11-12-sv3-stage-a-c1-correction-prompt.md), revision 3, from `823be0ba1bad4fadd004a94911b9b7a81f0b586e` of the manager branch `claude/magical-wozniak-yfmmx2`.
- **Specification:** the [brief](../../planning/sv3-eligibility-discovery-interactions.md), revision 4, "Stage A, correction C1 (DM-61)", with D2, D3, D6, D14, checks 3 and 5, the owned paths and the exclusions as DM-61's K1 to K7 and DM-62's Y1 to Y4 wrote them.
- **Branch:** `claude/glow-correction-c1-1jzjgr` (pushes to `claude/**` run the Foundation workflow).
- **Code head:** `b44e6f7e42abfa6d1f24ca9a429f07e15684fe74`, three commits on `823be0b`: `6c49fae` (the account locks), `e100cd3` (the random tie-break and ADULT's ceiling), `b44e6f7` (the proof). **Records head:** the commit that adds this section, pushed after the run of record finished.

### The start gate and the environment check

- **Environment (names only; no value was read or printed):** none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`; no `STREAM_*` and no `PG*` name. The three AWS names were present: `AWS_ACCESS_KEY_ID`, `AWS_CA_BUNDLE`, `AWS_SECRET_ACCESS_KEY`; never read, and passed to no command. `GH_TOKEN` and `GITHUB_TOKEN` present, never read. Every repository command ran under `env -i` with `PATH`, `HOME`, `LANG=C.UTF-8` and its own variables (the proxy and CA variables by reference, for the package installs only).
- **Toolchain:** `python3.12 --version` → `Python 3.12.14`; `node --version` → `v24.19.0`; `npm --version` → `11.9.0` (both in `$HOME/.local/bin`, first on `PATH`); `docker --version` → `Docker version 29.9.2, build a82e528`.
- **Start gate:** `git switch -C claude/glow-correction-c1-1jzjgr 823be0b…`; `git rev-parse HEAD` → `823be0ba1bad4fadd004a94911b9b7a81f0b586e`; `Stage A's code head` printed (no non-Markdown path differs from `ad9ff08`); the owned paths' diff between `823be0b` and the live manager branch printed nothing (the live branch was at `823be0b`); the record's count of "Stage A, correction C1" headings on the live branch → `0`; `823be0b` is an ancestor of the live branch.
- **Read:** root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`; the proof's README; the brief's revision 4 (D2, D3, D6, D14, checks 3 and 5, owned paths, exclusions, review plan, C1's section); DM-61 and DM-62 whole; this record's "Stage A", "Manager verification of Stage A" and the three Codex sections; P06.DB's D5 through the data model's transaction design and the reference design itself; the data model's unit-of-work table (it states no lock mode); every changed file; `glow_domain/identity.py` (`whole_years`, `adult_outcome`), `glow_domain/profile_settings.py` (`AGE_CEILING`) and `CandidateProfile` in the production schema (`age`: integer, minimum 18, maximum 150), read only. **PostgreSQL 17's manual**, "Explicit Locking", read at `postgresql.org/docs/17/explicit-locking.html`: `FOR NO KEY UPDATE` *"will not block `SELECT FOR KEY SHARE` commands that attempt to acquire a lock on the same rows"*, and `FOR KEY SHARE` blocks `SELECT FOR UPDATE` *"but not `SELECT FOR NO KEY UPDATE`"*; Table 13.3 as DM-61 gives it.

### Item 1: the account locks `FOR NO KEY UPDATE` (K1, K5)

**Every explicit lock of an `AppAccount` row**, found by a scan of `services/api` (its tests, migrations and virtual environment left out) and the reference design (`account_lock_scan`, below), not by K5's list alone. The scan found these seven and no other; all are in K5's list.

| File and function | Before (`823be0b`) | After (`b44e6f7`) |
|---|---|---|
| `services/api/glow_profiles/tx.py`, `lock_account` | line 165, `AppAccount.objects.select_for_update()` (`FOR UPDATE`) | line 169, `select_for_update(no_key=True)` (`FOR NO KEY UPDATE`) |
| `services/api/glow_profiles/tx.py`, `lock_account_any_state` | line 181, `FOR UPDATE` | line 185, `FOR NO KEY UPDATE` |
| `services/api/glow_profiles/identity_verification.py`, `_locked` | line 55, `FOR UPDATE` | line 55, `FOR NO KEY UPDATE` |
| `services/api/glow_identity/revocation.py`, `mark_verified` | line 95, `FOR UPDATE` | line 95, `FOR NO KEY UPDATE` |
| `services/api/glow_identity/age.py`, `transition` | line 87, `FOR UPDATE` | line 87, `FOR NO KEY UPDATE` |
| `services/api/glow_chat/contact.py`, `_lock` (every writer's account locks, and their `Match` and `AccountSession` locks) | line 165, `model.objects.select_for_update()` (`FOR UPDATE` for every model) | line 167, `select_for_update(no_key=model is AppAccount)`: `FOR NO KEY UPDATE` for an account row, `FOR UPDATE` for every other row, unchanged |
| `proofs/postgres-ordering/glow_ordering_proof/reference.py`, `_lock` | line 119, `FOR UPDATE` for every model | line 122, `no_key=model is AppAccount`, as `glow_chat`'s |

- **Nothing else in those files changed** but the docstrings and comments that state the mode: `tx.py`'s module docstring, `lock_account`'s, `lock_account_any_state`'s and `read_account_shared`'s ("every writer takes it `FOR NO KEY UPDATE` first"); `identity_verification._locked`'s comment (kept to one line, since `test_profile_recompute` pins that file's line numbers); `mark_verified`'s and `age.py`'s docstrings; `contact.py`'s module docstring, `_lock`'s and `_lock_shared`'s; the module docstrings of `operations.py` and `media.py`; `reference.py`'s module docstring and `_lock`'s. No writer's body changed; every other row's lock is as it was.
- **Nothing deletes an account row or changes its keys:** no `delete()` of an `AppAccount` and no write of its `id` or `auth_user` in `services/api` (DM-61 3.2 found the same); so no account lock needed to stay `FOR UPDATE`.
- **The pin of the two lock functions' bodies** (`test_profiles_offline.py`, `test_the_any_state_lock_is_lock_account_without_its_state_check`) now expects `select_for_update(no_key=True)` in both.
- **`pages.py`'s docstring** states the mode of the viewer's lock (`lock_account`) and why it does not block the entries' foreign-key checks.

### Item 2: the random tie-break (K2)

- **The selection** (`predicates.SELECTION`) draws `gen_random_uuid()` for each candidate (`predicates.TIE_BREAK`), selects it `AS tie_break` and orders by it (then the profile ID, a tie that cannot occur) within its `LIMIT`. Recommendations sort the selected rows by band, then by that returned value (`pages._recommend`); the entries' positions record the order, so each page reads `position` and nothing stores the value or computes it again.
- **Removed:** `keys.tie_break`, `keys.sql_pads`, `keys.TIE_BREAK_SALT`, `keys.BLOCK` and `keys`' `hashlib` and `settings` imports; the keyed `predicates.TIE_BREAK` (HMAC over `sha256` with the pads); the `ipad` and `opad` parameters set in `eligibility.parameters`, and its import of `keys`; the selection's `batch` parameter, which only the keyed hash read; the plans' throwaway key (`discovery_support.explain`); and the suite's ledger entries computed from `keys.sql_pads`.
- **Kept:** the cursor's MAC (`keys._mac`, `cursor`, `read_cursor`, `CURSOR_SALT`, `CURSOR`), byte-identical, computed in Python and never sent to the database.
- **The API's offline test** `KeyTests.test_the_tie_break_is_drawn_in_the_selection_with_no_key` replaces the `salted_hmac` pin: `TIE_BREAK` is `gen_random_uuid()`, the selection draws and orders by it, the parameters are exactly `adult_states`, `both_ways`, `choices`, `consent`, `today` and `viewer` (none bytes), `keys` holds none of the removed names, and no statement names a pad, `sha256` or an HMAC. `RankingTests` now gives the ranking UUID tie-breaks.

### Item 5: ADULT's age ceiling (Y1 to Y3)

- **Where:** in `predicates.MEMBER`'s one `adult` column: `(s.state = ANY(%(adult_states)s) AND s.birth_date IS NOT NULL AND <AGE of s.birth_date> <= 150) AS adult`, with `AGE`'s whole-years rule on the server's UTC date (`%(today)s`) and `150` from `glow_domain.profile_settings.AGE_CEILING`, imported (`int(ps.AGE_CEILING)` in the statement's text), not written again. `MEMBER` is read for the viewer and the candidate by the selection, every page's recheck, the viewer's read (`VIEWER`) and the trusted adapter's pair read (`PAIR`), and `member_states` requires `adult IS TRUE`, so a member whose date gives 151 or more fails ADULT everywhere, as a state outside the set does. A NULL age fails closed.
- **No DTO, contract, registry entry or SV2 code changed;** SV2's adult check is as it was (its ceiling at entry is carried to P09.2, DM-62 Y6).
- **The tests** (check 3, Y2):
  - `age.ceiling_150_shown_151_excluded` (discovery suite), at the server's date: a candidate whose date gives exactly 150 is shown, one who turns 151 tomorrow (150 today) is shown, and one at 151 is excluded, each agreeing with the pair read (`_sees`), which names ADULT for 151 (`("candidate", "adult")`) and not for 150; the cards carry 150; every page is checked against the production schema. **A page's recheck:** with a batch made, a candidate on a later page moved to 151 is dropped at the next page. **The viewer:** at 151, `forbidden` (403) and no batch, and the pair read names `("viewer", "adult")`; at 150 they page again.
  - `age.ceiling_at_leap_days`: `age.leap_days_and_age_state`'s six birth dates moved 132 years back (1876 and 1868 are leap years, as 2008 and 2000 are) against its nine days, 54 pairs: `MEMBER`'s `adult` equals `whole_years ≤ 150`, the age equals `whole_years`, the viewer's own read (`VIEWER`) and the pair read's candidate column (`PAIR`) agree, and both 150 and 151 fall on the leap-day cases (1876-02-29 is 150 on 2026-03-01 and 2027-02-28, and 151 on 2027-03-01).
  - **The pin** (Y3): `AgeCeilingTests.test_the_ceiling_is_candidate_profile_ages_maximum_in_the_production_schema` reads `packages/contracts/production/gapp-api-v1.schema.json` and requires `CandidateProfile.age`'s `maximum` to equal `AGE_CEILING` (150); `test_adult_bounds_the_age_its_date_gives_for_every_reader` checks the ceiling sits in `MEMBER`'s `adult`, which all four statements read.

### Item 3: the proof (K3, K4; DM-61 sections 3.4 and 4.2)

The discovery suite has 38 cases (32 before; `CASE_COUNT` and its offline pin changed with it). Six are C1's; `pages.keyed_stable_order` became `pages.random_stable_order`. The concurrency cases run each transaction on its own thread and its own connection (`_Worker`), held at its lock by a probe (`_Held`: `after_first_lock`, `before_commit`; it only signals and waits).

| Case | What it shows |
|---|---|
| `concurrency.two_viewers_create_at_once` (Codex's CX1) | Two mutually eligible viewers' `pages.create`, each held at `after_first_lock` (its own account locked) until both hold; then one is released and must reach `before_commit` (its entries written, each foreign-key check taking `FOR KEY SHARE` on the other's locked account) before the other is released. In both orders both pages are `applied`, and each batch holds an entry referencing the other's account |
| `concurrency.block_races_page_creation` (the second cycle) | `glow_chat`'s `block` by a candidate whose account is below the viewer's (it locks the candidate, then the viewer) against the viewer's page (it locks the viewer, then writes an entry referencing the candidate). Page first: the page commits its entry while the block holds the candidate, then the block completes. Block first: the block is observed waiting on the viewer's lock (`pg_blocking_pids` names the page's backend), the page then commits its entry, and the block completes. Both `applied` in both interleavings; the block is undone between them |
| `concurrency.page_does_not_wait_on_a_candidates_writer` (the rule) | SV2's profile edit of the candidate held at `after_first_lock` (the candidate's account locked); the viewer's page transaction commits its batch, with the entry referencing that account, while the writer still holds it. Then the page's photo read, SV2's `delivery_reference` in its own transaction after the page's commit, takes the candidate's account `FOR SHARE` and is observed waiting for the writer, as SV2 designed every read to; once released, both are `applied` (see "Findings and deviations") |
| `locks.account_locks_no_key_update` (the scan) | `account_lock_scan.scan()` finds the seven locks above, all `FOR NO KEY UPDATE`, at exactly the expected sites |
| `pages.random_stable_order` (K2, K4; Codex's CX2) | 12 candidates in one band, two batches paged three at a time: each batch serves every candidate once, in the entries' position order; the same cursor gives the same page; neither order is the profile IDs' or `sha256("<batch>:<profile>")`'s; the two orders differ (equal by chance with probability 1 in 12!); no entry field holds a tie-break. Every statement the page requests ran (`record_statements`: 312, 258 with parameters, locally and in the run of record, each read as sent through psycopg's `ClientCursor.mogrify`, the client-side binding cursor Django 5.2 uses by default) holds no value derived from `SECRET_KEY`: the key itself, the cursors' derived key and every MAC issued, and the removed tie-break's derived key and both pads (`derived_from_secret_key`) |
| `age.ceiling_150_shown_151_excluded`, `age.ceiling_at_leap_days` | Item 5, above |

- **The scan** (`proofs/postgres-ordering/glow_ordering_proof/account_lock_scan.py`) reads the source and imports none of it. It judges three kinds of lock: an ORM `select_for_update` whose receiver names `AppAccount` (it must pass `no_key=True`); a generic one on a model held in a variable, as `glow_chat`'s and the reference's `_lock` are (it must pass a `no_key` that names `AppAccount`, or `True`); and SQL text outside a docstring that takes `FOR UPDATE` and names the account table or an unknown `{table}`. A lock of another model, and a `FOR SHARE` or `FOR KEY SHARE` read, are not judged. Its offline tests (`AccountLockScanTests`, five) plant each kind of `FOR UPDATE` lock and see it refused, see the no-key forms, another model's lock, a shared read and a docstring pass, and see the command exit 1.
- **The suite's ledger** no longer imports `keys.sql_pads`: it holds the run's keys, the cursors' derived key and the removed tie-break's derived key and pads (`derived_from_secret_key`), so the job's secret scan still looks for them in every output.
- **The plans** run with the statements' own parameters (no key exists to replace).
- **The README** gains the discovery suite's paragraph with C1's additions, the reference design's account lock mode and the layout rows for the discovery modules and the scan.

### Reversals

Each is a temporary edit of the committed code, run against its cases on the local throwaway database with a scratch runner kept outside the repository (or offline), then undone with `git checkout`; the tree was clean after each.

| Reversal | The temporary edit | Run | Result: the failing line |
|---|---|---|---|
| `C1.account_locks_for_update` | the seven account locks back to `select_for_update()` (`sed` over the six files) | the three concurrency cases and the scan | failed as intended: `concurrency.two_viewers_create_at_once`: FAILED: both pages succeed (applied, error:provider_unavailable:DeadlockDetected) · `concurrency.block_races_page_creation`: FAILED: page first: both succeed (page error:provider_unavailable:DeadlockDetected, block applied) · `concurrency.page_does_not_wait_on_a_candidates_writer`: FAILED: the page's transaction committed its entry while the writer held the candidate's account (pid 212 wait_event_type=Lock wait_event=transactionid pg_locks not granted: transactionid/ShareLock pg_blocking_pids=[211] (holder pid 211) after 1 polls, 2 ms) · `locks.account_locks_no_key_update`: FAILED: every account lock is FOR NO KEY UPDATE: … reference.py:122 (_lock, generic) FOR UPDATE; … contact.py:167 (_lock, generic) FOR UPDATE; … age.py:87 (transition, orm) FOR UPDATE; … revocation.py:95 (mark_verified, orm) FOR UPDATE; … identity_verification.py:55 (_locked, orm) FOR UPDATE; … tx.py:169 (lock_account, orm) FOR UPDATE; … tx.py:185 (lock_account_any_state, orm) FOR UPDATE |
| `C1.account_locks_for_update`, the other orders | the same, with each concurrency case's loop limited to its second order | the first two cases | failed as intended: `concurrency.two_viewers_create_at_once`: FAILED: both pages succeed (error:provider_unavailable:DeadlockDetected, applied) · `concurrency.block_races_page_creation`: FAILED: block first: both succeed (page applied, block deadlock:DeadlockDetected); the block is `glow_chat`'s writer, which reports a deadlock as its own `deadlock` outcome |
| `C1.planted_for_update` | a module with `AppAccount.objects.select_for_update().filter(pk=account_id).first()`, scanned alone, and then placed in `services/api/glow_profiles/` | `python -m glow_ordering_proof.account_lock_scan` | failed as intended: `BAD <scratchpad>/planted/planted.py:5 (lock, orm): FOR UPDATE`, `account locks found: 1; not FOR NO KEY UPDATE: 1`, exit 1; in the tree: `BAD services/api/glow_profiles/zz_planted.py:5 (lock, orm): FOR UPDATE`, `account locks found: 8; not FOR NO KEY UPDATE: 1`, exit 1. The offline tests plant the four kinds |
| `C1.tie_break_profile_id` | `TIE_BREAK = "c.profile_id"` | `pages.random_stable_order` | failed as intended: FAILED: not the profile IDs' order |
| `C1.tie_break_unkeyed_hash` | `TIE_BREAK = sha256(convert_to(batch || ':' || profile_id))`, with the `batch` parameter restored in `pages.create` | `pages.random_stable_order` | failed as intended: FAILED: not an order computable from the batch's and profiles' IDs |
| `C1.tie_break_keyed` (beyond the brief's list) | `ad9ff08`'s `predicates.py`, `keys.py`, `eligibility.py` and `pages.py` (the keyed tie-break, its pads as parameters) | `pages.random_stable_order` | failed as intended: FAILED: no statement or parameter carries a value derived from the key |
| `C1.no_age_ceiling` | the ceiling removed from `MEMBER`'s `adult` | the two ceiling cases, and a scratch probe | failed as intended: `age.ceiling_150_shown_151_excluded`: FAILED: the recommendations page: the body is its DTO (the production schema's check of the page) · `age.ceiling_at_leap_days`: FAILED: ADULT's ceiling is whole_years at most 150 · the probe: a viewer's page answered HTTP 200 with `card ages [151]`, and the schema check's error was at `$.data.items[0].profile.age`, on its `maximum` |

### The threat model's inputs, updated

**Each writer's locks and their modes** (an account row `FOR NO KEY UPDATE`; every other explicitly locked row `FOR UPDATE`, unchanged; readers `FOR SHARE`, unchanged):

| Writer | Locks, in order |
|---|---|
| SV2's operations (`tx.run` with `lock_account`; photos' purge and acknowledgment with `lock_account_any_state`) | the actor's account `FOR NO KEY UPDATE`; settings pointers `FOR SHARE` in name order (D19); its own rows `FOR UPDATE`; `glow_chat`'s writers nested inside, their account locks then no stronger than the operation's |
| SV2's staff identity verification (`identity_verification._locked`) and SV2's age transition (`age.transition`) | the account `FOR NO KEY UPDATE` (already held by the operation), then the verification or age-state row `FOR UPDATE` |
| SV1's `mark_verified` | the account `FOR NO KEY UPDATE`, alone |
| `glow_chat`'s pair writers (`block`, `unblock`, `unmatch`, `activate_match`, the send) | the lower account, then the higher, `FOR NO KEY UPDATE`; the match and the session `FOR UPDATE` |
| `glow_chat`'s account writers (suspend, delete, pause, consent) | the account `FOR NO KEY UPDATE`; their own rows `FOR UPDATE` |
| SV3's page with no cursor (`pages.create`) | the viewer's account `FOR NO KEY UPDATE`; the five pointers `FOR SHARE`; then its writes: the earlier batch's delete, the batch (its foreign key `FOR KEY SHARE` on the viewer's own account) and the entries (each entry's foreign key `FOR KEY SHARE` on its candidate's account) |
| SV3's page with a cursor | the viewer's account `FOR SHARE`; the pointers `FOR SHARE`; writes nothing |
| A card's photo read (SV2's `delivery_reference`, after the page's commit) | the photo owner's account `FOR SHARE`, in its own transaction |
| Readers (`read_account_shared`, `glow_chat`'s token grant and conversation reads) | `FOR SHARE`, unchanged |

**The cycles that can no longer form, and why.** A foreign-key check takes `FOR KEY SHARE` on the referenced account, and `FOR KEY SHARE` conflicts only with `FOR UPDATE`. No code takes an account row `FOR UPDATE` now, explicitly or by a delete or key change (none exists; PostgreSQL would take `FOR UPDATE` for one by itself). So:
- **Codex's CX1:** two viewers' pages each hold their own account and write entries referencing the other's; the entries' checks no longer wait, so neither waits on the other (`concurrency.two_viewers_create_at_once`).
- **The second cycle:** a pair writer holding the lower candidate and waiting for the viewer, against the page holding the viewer and writing an entry referencing the candidate; the page's check no longer waits on the candidate's lock, so the page commits and the writer then takes the viewer (`concurrency.block_races_page_creation`). The same holds for `send`, `unmatch`, `activate_match` and Stage B's like, match and block writes, each of which references another member's account.
- **What still waits, by design:** a writer on a writer of the same account (`FOR NO KEY UPDATE` conflicts with itself), and a `FOR SHARE` reader on a writer in flight, including a page's photo read after its commit. None of these holds a lock while it waits that another member's write needs, so no cycle runs through them; the ordering suite's `inverted_lock_order` control still deadlocks as designed (two writers locking the same two accounts in opposite orders).

**Where the tie-break's randomness comes from:** PostgreSQL's `gen_random_uuid()`, core since PostgreSQL 13, which fills its bytes from `pg_strong_random`, drawn once per candidate row inside the selection, on the database server. **No key exists:** no secret, pad or value derived from `SECRET_KEY` is in any statement, parameter or log line for the tie-break, so CX2's route (client-side binding writing parameters into a failing statement's logged text) carries nothing for it; the order is recorded only in the entries' positions; a client knowing the batch's and every profile's ID cannot compute it, and a new batch draws new values. The cursor's MAC is the only key in `glow_discovery`, and it never enters a statement. (DM-62's Y5, the other secrets in the database server's log, is P11's.)

**ADULT's rule, with its ceiling, for both members:** the age state is in the accepted set (`self_declared_adult` only), with its date, and the age that date gives in whole years on the server's UTC date is at most `AGE_CEILING` (150, `CandidateProfile.age`'s maximum). Read directly, not through `visible`, for the viewer and for the candidate, in the selection, every page's recheck, the viewer's read and the trusted adapter's pair read; a missing row, a missing date or a NULL age fails. A member at 151 or more is treated as a state outside the set: a viewer gets `forbidden` and no batch; a candidate is in no batch, is dropped at the next page if they pass 150 during one, and fails the pair read, so no card carries an age above the contract's maximum.

### Commands and results

**API** (`services/api`; `python3.12 -m venv .venv`, `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`; then with `GLOW_ENV=test`), on the code head:
- `manage.py check` → `System check identified no issues (0 silenced).`
- `manage.py test tests --verbosity 2` → `Ran 585 tests`, `OK` (583 before; the two new `AgeCeilingTests`, and the tie-break test replaced). The first full run failed one test, `test_profile_recompute.CallSiteTests.test_only_the_recompute_writes_a_profiles_state`, which pins line numbers in `identity_verification.py`: a two-line comment had moved two lines down by one. The comment was kept to one line and the test passed unchanged.
- `smoke.py` → `PASS /health/live: HTTP 200`, `PASS /health/ready: HTTP 503`, `PASS /api/v1/development/recommendations: HTTP 200`.
- `ruff check .` → `All checks passed!`; `ruff format --check .` → `156 files already formatted`; `mypy` → `Success: no issues found in 92 source files`.
- `python -m glow_persistence.static_check` → `Static definitions agree: 42 app models; migrations=0001_event_infrastructure,…,0010_batch_collection`.

**The contracts and the mobile app** (`npm ci --ignore-scripts` in `apps/mobile` and `packages/contracts`, from their locks): `npm run check` in `packages/contracts` → `Generated types and runtime validators match schemas.`, `tests 763`, `pass 763`, `fail 0`; the contracts' Python tests (`PYTHONPATH=. .venv/bin/python -m unittest discover -s ../../packages/contracts/tests`, from `services/api`) → `Ran 50 tests`, `OK`; `npm run check` in `apps/mobile` → `tests 691`, `pass 691`, `fail 0`. Nothing under `packages/` or `apps/` changed.

**The proof** (`proofs/postgres-ordering`; its venv, `pip install --require-hashes -r requirements-dev.lock`, `pip check` → `No broken requirements found.`): `env -i … python -m unittest discover -s tests -t .` → `Ran 253 tests`, `OK` (248 before: the five scan tests); `ruff check .` → `All checks passed!`; `ruff format --check .` → `67 files already formatted`; `mypy` → `Success: no issues found in 67 source files`.

### Local database runs (iteration, not evidence)

P06.DB's D4 conditions: a throwaway PostgreSQL from the CI job's pinned image (`postgres@sha256:d74eeac9…ec46f`, pulled from Docker Hub), started with a local `dockerd`, published on `127.0.0.1:5433` only, with `track_commit_timestamp=on`. A generated superuser and role password, a generated marker as each of the four databases' comment, and generated keys sat in a 0700 directory under the session's scratchpad, written by a scratch script that printed no value. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name was present. The container and the credential files were removed at the end.
- **Discovery, first database:** `migrate` from zero; `makemigrations --check --dry-run` → `No changes detected`. The suite → `36/38`: two test bugs, fixed. `pages.random_stable_order` read the first batch's positions after the second batch had replaced it (one batch per collection); and `concurrency.page_does_not_wait_on_a_candidates_writer` required the whole page request to finish while the writer held the lock, but its photo read after the commit waits by SV2's design (the findings).
- **Discovery, a fresh database:** `[discovery] cases: 38/38 passed in 98.6 s`; `discovery secret scan: clean (1275 secrets held; 0 found in 745 log records, 98 writes and the results JSON)`; `discovery value scan: clean (699 member values held …; 0 found in the same output)`; `DISCOVERY VERDICT: PASS`. Statements per page request 223, 222 and 224; the plans at 1,000 members: selection 35.7 ms (recommendations) and 31.8 ms (broader), recheck 2.6 ms, pair 0.21 ms, viewer 0.06 ms.
- **The ordering suite**, both subjects, on the corrected code: `[reference] cases: 56/56 passed`, `[adapter] cases: 115/115 passed`, `[read] cases: 62/62 passed`; every negative and planted control `failed as intended` (the reference's ten design controls, `inverted_lock_order`'s deadlock among them, and nine planted oracle controls; the adapter's 13 planted controls; the read phase's three); `== VERDICT: PASS ==`.
- **The identity suite:** `[identity] cases: 49/49 passed`, scan clean, `IDENTITY VERDICT: PASS`. **The profile suite:** `[profile] cases: 69/69 passed`, both scans clean, `PROFILE VERDICT: PASS`.
- **Every reversal above** ran on the discovery database after the fresh run.

### The run of record

- **Foundation run [43147201199](https://github.com/amthorn78/glow-dating-app/actions/runs/43147201199)** (run number 1069, `push`, attempt 1) on the code head `b44e6f7`, 03:17:29 to 03:25:50 UTC, concluded `success`. It started at once; nothing was pushed to the branch until it had finished. Read with the GitHub tools and the run's log archive.
  - **Change scope:** full scope (`{"full": true, "reason": "missing-or-invalid-comparison"}`: the push created the branch, so there was no earlier head to compare; C1 is full scope in any case).
  - **Jobs:** all eight `success`: Change scope, API checks, Mobile checks, API mobile smoke, API artifact checks, Stream proof checks, Database proof checks and the Foundation gate.
  - **The gate:** `Application checks passed`.
  - **Retries:** none fired: every "Wait 60 s before the one retry of the Python install (DM-41)" and "Retry the Python install once" step was skipped, and the Chromium install passed at its first attempt.
  - **API checks:** `Ran 585 tests`, `OK`; the contracts' Python tests `Ran 50 tests`, `OK`. **Mobile checks:** the contracts' `tests 763`, `pass 763`, and the app's `tests 691`, `pass 691`, `fail 0`, with the export and the rendered onboarding checks. **The proof's offline tests:** `Ran 253 tests`.
- **The four suites, in the Database proof checks job:**
  - **The ordering suite:** `[reference] cases: 56/56 passed`, `[adapter] cases: 115/115 passed`, `[read] cases: 62/62 passed`; every control `failed as intended` (35 rows marked yes: the reference's ten design controls, `inverted_lock_order`'s `deadlock` among them, and nine planted ones; the adapter's 13 planted ones; the read phase's three); `== VERDICT: PASS ==`; the second run refused.
  - **The identity suite:** `[identity] cases: 49/49 passed in 30.0 s`; its scan clean, 0 of the job's secrets in its output or JSON; `IDENTITY VERDICT: PASS`; `identity phase: 31 s`; the second run refused.
  - **The profile suite:** `[profile] cases: 69/69 passed in 57.5 s`; both scans clean, 0 of the job's secrets; `PROFILE VERDICT: PASS`; `profile phase: 58 s`; the second run refused.
  - **The discovery suite:** the three other markers refused and the migrations applied from zero; `[discovery] cases: 38/38 passed in 60.5 s`, C1's six among them as in the table above; `discovery secret scan: clean (1275 secrets held; 0 found in 745 log records, 98 writes and the results JSON)`; `discovery value scan: clean (699 member values held …; 0 found in the same output)`; the job's check: `the job's secrets found in the discovery suite's output: 0`, `… in the discovery results JSON: 0`, `the suite's own scans (secrets, member values) reported clean: True`; `DISCOVERY VERDICT: PASS`; **`discovery phase: 61 s (the job's timeout is 30 minutes)`**; the second run refused (`refusing a used database: …`) with its six row counts unchanged (`1113 1113 1110 52 284 1581`); `sv3-discovery-results` uploaded after the check (artifact 13911744449).
  - Statements per page request: 224, 223 and 222. The plans at 1,000 members (the disposable setup's measurement): pair 0.135 ms, recheck of a page of 50 1.778 ms, broader selection 17.447 ms, recommendations selection 19.926 ms, viewer 0.045 ms.
- **No secret in the log:** the job generates and masks every secret before anything prints, and its checks found none of the job's secrets in any suite's output or results JSON. This session read the log for these lines only; it holds none of the job's values to search for.

### Item 4: the records

Only the sentences that state the account lock's mode, the keyed tie-break or ADULT's rule were rewritten:
- **The data model:** `mark_verified`'s lock; ADULT in "The eligibility read as built" (the ceiling); a page's lock on the viewer's account; "The transaction design" (every account lock `FOR NO KEY UPDATE`, why, and that nothing deletes an account row or changes its keys); the grant's wait on an epoch bump; the conversation reads' wait on a revocation. It stated no keyed tie-break.
- **The contract document, F07's server section:** a page with no cursor's account lock, the random tie-break in place of the keyed one, and ADULT's ceiling.
- **The P11 plan:** the revocation lock-wait line (the waiting writer's lock is `FOR NO KEY UPDATE` on an account row; the behaviour is the same) and DB11's "stable keyed order".
- **This section** carries the threat model's inputs, above.

### Findings and deviations

- **The rule's case, worded against the brief.** The brief's D14 and DM-61 3.4 say *"a page whose candidate's writer holds that candidate's account lock completes without waiting"*. The page's **transaction** does: it holds the viewer's account and commits its entries referencing the held account while the writer still holds it. But the page **request** then reads each card's photo through SV2's `delivery_reference`, in its own transaction after the commit, which takes the photo owner's account `FOR SHARE` (`read_account_shared`) and so waits for the writer in flight, as SV2 designed every read to (and as it did under `FOR UPDATE`). It holds none of the page's locks, so no cycle runs through it. The case therefore checks the page's transaction, and records the photo read's wait as observed. The first local run, which required the whole request to finish while the writer held its lock, failed on this wait. Under the reversal, the page's transaction itself waited at its entries' insert. This is for the manager and the review to weigh; changing the photo read is SV2's code and outside C1.
- **A docstring outside K5's list still says `FOR UPDATE`:** `services/api/glow_chat/reads.py`'s module docstring says a read waits for a revocation *"which holds those rows `FOR UPDATE`"*. The account rows among them are now held `FOR NO KEY UPDATE` (the read's wait is unchanged, since `FOR SHARE` conflicts with both). `reads.py` is not in K5's list, so it is left for the manager to route.
- **The ledger's values derived from `SECRET_KEY`** are the ones discovery could carry: the key, the cursors' derived key and every issued MAC, and the removed tie-break's derived key and pads. The check reads only page requests' statements (the case's members are built through SV2's commands before it starts, and those store SV2's keyed idempotency digests by design). Django's session hash and SV2's digests are not in its list.
- **`glow_chat`'s block reports a deadlock as its own `deadlock` outcome**, not `provider_unavailable`: in the reversal's block-first order, PostgreSQL aborted the block, and `glow_chat`'s `_run` returns `ContactResult("deadlock", "DeadlockDetected")`. The page's side reports `provider_unavailable` through SV2's `tx.run`. Both are "one side refused, the other applied" (K3).
- **A reversal beyond the brief's list,** `C1.tie_break_keyed`, shows that the key check would catch the keyed design's pads.
- **The selection still orders by the profile ID after the tie-break,** a tie that two random UUIDs cannot produce in practice; it makes the order total. A reviewer may judge it unneeded.
- **No stop condition was met:** no model, migration, DTO, registry entry, workflow, lock file or dependency changed; nothing in `glow_chat`, `glow_identity` or `glow_profiles` changed beyond K5's list; no account lock had to stay `FOR UPDATE`; every ordering control failed as designed; and the ordering, identity and profile suites passed on the corrected code (locally, and in the run of record above).

### What could not be run here

- The mobile app's export and rendered checks and `playwright install` (CI's: they passed in the run of record above).
- Any provider, HDE, Stream, Railway or other external call; `proofs/stream-chat` (its CI job ran unchanged).

## Manager verification of C1

App Manager 11, 12 November 2026 (finished at 03:46 UTC). Not a code review: the exact-head review follows.

- **The branch:** `claude/glow-correction-c1-1jzjgr`, code head `b44e6f7`, records head `cbeb050`, starting at `823be0b` (the live manager head, so integrated by fast-forward). Its 26 paths are all in C1's owned paths. Outside `glow_discovery`, every changed line is a lock's mode or a docstring that states it (K5); `media.py` changes only its module docstring.
- **The code:** `keys.tie_break`, `sql_pads` and the pads' parameters are gone, and `predicates.TIE_BREAK` is `gen_random_uuid()`; the cursor's MAC is unchanged. ADULT's ceiling is in `MEMBER`'s one `adult` column, with `AGE_CEILING` imported; a null date still fails closed.
- **The run of record,** 43147201199 on `b44e6f7` (push), read from GitHub: all eight jobs `success`, every retry step skipped, and the gate printed `Application checks passed`. The database job's log: ordering 56/56, 115/115 and 62/62, with every control failing as intended (`inverted_lock_order` still deadlocks); identity 49/49 (31 s); profile 69/69 (58 s); discovery 38/38 in 60.5 s (phase 61 s), its seven new cases among them; every suite's secret scan clean; each second run refused with its row counts unchanged.
- **Re-run here,** at `cbeb050`, in fresh venvs from the hash-locked requirements: the API's `manage.py check`, 585 tests OK, smoke PASS, Ruff, format and mypy clean, the static check; the proof's 253 offline tests OK, Ruff and mypy clean. The contracts and the mobile app have no change in C1; CI's jobs passed.
- **Two reversals of my own,** each restored: `contact._lock` back to `select_for_update()` makes the lock scan report `not FOR NO KEY UPDATE: 1` and exit 1 (a first attempt's `sed` matched nothing, so it was redone with a checked replacement); ADULT's ceiling removed from `MEMBER` fails `AgeCeilingTests.test_adult_bounds_the_age_its_date_gives_for_every_reader`.
- **The photo read's wait** (the session's first deviation): `media.delivery_reference` runs each card's read in its own transaction (`run(body)`), holding one `FOR SHARE` lock, so it can wait for a writer but holds nothing another waits for: no cycle. The session's statement holds.
- **Two sentences C1's item 4 missed,** found by a search across line breaks: the data model's `AccountAgeState` row ("takes the account row `FOR UPDATE` before the age state's row") and its `RecommendationBatch` row ("after the owner's account row lock (`FOR UPDATE`)"). With `glow_chat/reads.py`'s module docstring (the session's second deviation), three texts still state the old mode.
- **Disposition:** the first deviation departs from DM-61's words for check 5, and the three texts need a home, so both go to the Dev Manager as [DM-63](../../ephemeral/2026-11-12-dm-63-sv3-stage-a-c1-verification.md) before the review prompt's revision 2.
- **DM-63's answer** (`715ef27`, a read of `8828112`): the rule is the page's transaction's, and C1 shows it; DM-61's "completes without waiting" was too broad (LM1 to LM3, in the brief's revision 6). The three texts are known items for the review (LM6) and are fixed in the correction after it, in DM-63's words (LM5). Nothing in C1 changes.

### PR45's run on `4b771e0`: SV2's profile suite, one case

- **The run:** PR45's run 43150501532 on `4b771e0` (code identical to `b44e6f7`) failed in Database proof checks, at SV2's profile suite, 68 of 69: `area.coordinates_never_kept_or_echoed` reported *"FAILED: no table holds the coordinates (outbox and idempotency records included)"*. Every other application job passed, and the gate failed on that job. The suite's secret and value scans were clean. It is not a run of record.
- **The manager's diagnosis:** `_found_in_database` searches every row's `row_to_json` text for `forms("40.7123457")`, which include `40.712` to `40.712345`. Called offline, those forms match a timestamp written at second 40 and millisecond 712 (`…T03:51:40.712345+00:00`). The suite writes thousands of timestamped rows, many per second, so such a row exists in some runs (an estimate; nothing measures the rate, DM-64 section 3.3). No profile-suite file has changed since `5bcbe54` (SV2 Stage B's C2), and C1 changed none. The same forms feed `ValueLedger`'s value scans. Which row matched is not known, because the case names no table.
- **Disposition:** not C1's defect, and not resolved by a re-run (OD-21). It goes to the Dev Manager as [DM-64](../../ephemeral/2026-11-12-dm-64-sv2-profile-suite-coordinate-scan.md), recommending a fix in the correction after the exact-head review. The review reads `b44e6f7`, whose run of record is green (04:00 UTC).
- **DM-64's answer** (`25cac30`, a read of `16c2052`): the diagnosis agreed. The same mechanism reaches the value scans' texts: the results JSON's migration times and raw durations, and the discovery plans' timings. A second exposure of the same kind: Django's `Expires` header prints the current second, which can equal a held birth time (nine in the profile suite, one in discovery), so a value scan can fail at those seconds of the day. The fix (T1 to T9) goes in the correction after the exact-head review, or in a correction before it if DM-63's answer adds one. **Until then,** a run that fails with either signature (T9: (i) `area.coordinates_never_kept_or_echoed` failing alone with both scans clean; (ii) a value scan "FOUND" with every case passing, at a held birth time) is recorded here and not re-run (OD-21, OD-58); any other failure is investigated as new (14:22 UTC).

## Exact-head review of Stage A (`ad9ff08` with C1, code head `b44e6f7`)

- **The session:** the exact-head code and security review, from the review prompt's revision 2 at `3b36969` (TypeSafe v8.2: Fable 5.1 at max; Nathan's pick not recorded). Relayed by Nathan on 12 November. It changed nothing in the repository, on GitHub or in Notion.
- **Gates:** environment (names only), start gate and classification (`"full": true`; 47 non-Markdown paths, C1's 21) passed. Toolchain CPython 3.12.14, Node 24.19.0, npm 11.9.0, Docker 29.9.2.
- **Verdict: changes required, narrowly.** No blocking finding. It found no way for a member to see, or be shown to, someone a predicate excludes, to read a private value from a response, to use another member's cursor, to compute a batch's order, or to deadlock two writers. Seven should-fix findings in correction classes; six nits. All the Dev Manager's conditions are met in code (Q1, Q3 to Q6, Q12, Q13; K1 to K5; Y1 to Y3; LM1, LM2); by AST, C1 changed only the seven lock functions' code outside `glow_discovery`. `D3.candidate_adult` now fails at `b44e6f7`, through the ceiling case.

| # | Severity | Class | What | Where |
|---|---|---|---|---|
| F1 | Should fix | A test passes where it should fail | No test fails when the one-snapshot read is broken: a recheck or selection split into two statements after the probe, and a cursor page that writes, each pass 38/38 | `discovery_cases.py:1034-1093`; `pages.py:226-238`, `:334` |
| F2 | Should fix | Same | No failing test for the viewer's `eligibility_version` and `blocks_version` in a cursor's freshness, a batch that is not `ready`, or a distance choice the setting does not offer | `pages.py:174-194`; `discovery_cases.py:958-1006`; `predicates.py:141-142` |
| F3 | Should fix | Same (K3's scan) | The lock scan misses a `select_for_update()` on another model's queryset that joins the account table (Django locks the joined row `FOR UPDATE`, with no `OF`); none exists at `b44e6f7` | `account_lock_scan.py:161-179` |
| F4 | Should fix | A test fails where the code is right | `pointers.name_order` groups calls by `id(tx)`, which CPython reuses; it failed once in 16 local runs; the case never pages by cursor | `discovery_cases.py:1746-1769` |
| F5 | Should fix | A record says more than the code | Five texts still say a key orders the tie-break: the CI policy (governing), `discovery-fixtures.md`, `foundation.yml`'s comment, `discovery_settings.py`'s docstring, an API test comment | the review's list |
| F6 | Should fix | A record against the runs | The P11 plan's SV3 entry: "Run of record: none yet", and concurrency "not claimed" | `p11-deferred-acceptance.md:80`, `:84` |
| F7 | Should fix | A private value learned, by OD-60's own rule | Through the two-way rule a member can read another member's "show me" sets, and under `both_ways` their age range, by changing their own value or re-declared birth date; D8 accepts only the other direction | Brief D8; this record's "cannot"; `predicates.py:146-153` |
| N1 | Nit | — | `keys.py`'s docstring: "before any row is read"; the page first reads the viewer's account and the pointers | `keys.py:5-7` |
| N2 | Nit | Arguably a count | The cursor's offset shows how many entries were dropped at recheck between two pages | `keys.py:22-35` |
| N3 | Nit | — | V2: the bound is sound (about 824 statements a page at launch, 4,024 at the fixed photo limit); the proof's 260 holds for one photo a card | — |
| N4 | Nit | For P11 | The compatibility port asked inside the page's transaction; the fixture guard trusting a settings-set environment name; recommendations ranking a random 100 of the eligible | `pages.py:247`; `policy.py:111-131`; `predicates.py:253-254` |
| N5 | Nit | — | A test class after `unittest.main()`; `VIEWER` selects an unused column; the plans pass an unused parameter | the review's list |
| N6 | Nit | Records | This record's "Every other job passed" (corrected above at this batch); no pointer from Stage A's paragraphs to C1's update; the data model's `age_years` sentence | the review's list |

- **Also from the review:** migration 0010 is safe for an empty target; a populated target would need its batches deleted first in the same migration (focus 7). The photo reads hold nothing another transaction waits for (DM-63). No other current text gives an account lock as `FOR UPDATE` beyond the three known items. The five recorded reversals it re-ran failed as recorded; four offline reversals failed as intended; database reversals (informational, 16 local runs): block in one direction 35/38, "not stated" 37/38, `unmatched` 37/38, locks `FOR UPDATE` 34/38, ceiling removed 36/38, candidate-side ADULT 37/38; its own (F1, F2) passed 38/38.
- **The manager's reading:** the findings are specific and evidenced, and F5's CI policy sentence and N6's line are the manager's (AM11-14, AM11-16). Dispositions go to the Dev Manager as [DM-65](../../ephemeral/2026-11-12-dm-65-sv3-stage-a-review-dispositions.md) before correction C2's prompt: F7 touches privacy and an owner direction (OD-60), and N2 a disclosure rule (17:35 UTC).

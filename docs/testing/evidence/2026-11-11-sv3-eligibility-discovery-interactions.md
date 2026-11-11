# SV3: eligibility, discovery and interactions, proven on disposable PostgreSQL

- **Brief:** [SV3](../../planning/sv3-eligibility-discovery-interactions.md), revision 2, with [DM-60](../../continuity/dev-manager/reviews/2026-11-11-dm-60-sv3-brief.md)'s Q1 to Q15 applied.
- **This record** is written by the stage sessions. Each stage has its own section.

## Stage A

- **Session:** SV3 Stage A's implementation session, started by Nathan from [the Stage A prompt](../../ephemeral/2026-11-11-sv3-stage-a-implementation-prompt.md), revision 1, from `aa9ed701c36dce8772fbbf82b1283b6f845421e9` of the manager branch `claude/magical-wozniak-yfmmx2`.
- **Branch:** `claude/loving-maxwell-cqu7eq` (pushes to `claude/**` run the Foundation workflow).
- **Code head:** `ad9ff081e26535ab89eb1187c7b69ca96fac2ef4`. **Records head:** the commit that adds this record, pushed before the code head's run had started, at Nathan's direction (the run of record, below), and a second records commit with that run's figures.
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
- **Run of record's figures:** in "The run of record", below.
- **Shapes (the same in the local iteration):**
  - **The selection** (recommendations; broader likewise, with an anti-join on the recommendations batch's entries): a bitmap index scan on `profile_visibility_cursor` (state, ID) over the visible profiles; for each, index lookups for the account, age state, consent, preferences, the four fields' set rows (`preference_set_value`) and value rows, blocks, interactions and matches (nested loops and anti-joins); a top-N heapsort on the keyed hash; `LIMIT 100`. Its cost grows with the visible population, which every eligible candidate is evaluated against once per batch (about 53,000 shared buffer hits locally at 1,000). At this size no area-pair table is needed (D5); the measured distance choice is `anywhere`.
  - **The recheck** (a page of 50): an index scan on `batch_position` from the cursor's offset, the same per-candidate lookups for at most 51 entries, `LIMIT 51`.
  - **The pair read** and **the viewer's read:** primary-key and unique-key index scans, one row.
- **Statements per page request** (D7's bound, counted through the connection's execute wrapper, which logs nothing): locally 223 for a recommendations page that creates its batch, 222 for its next page by cursor and 224 for a broader page; the run of record's figures are below. Of these, a fixed number belong to the actor and the page's transaction, and four to each card's photo through SV2's `delivery_reference` (its owner's read, then its own transaction): with one photo per seeded member, 50 cards account for 200. The bound is the page's 50 cards times the media policy's live photos (four at launch, at most 20 by its fixed limit).

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

P06.DB's D4 conditions: a throwaway PostgreSQL from the CI job's pinned image (`postgres@sha256:d74eeac9…ec46f`, pulled from Docker Hub), on `127.0.0.1:5433` only, started with a local `dockerd`. A generated password, a generated marker as the database's comment (`glow_discovery_proof`), and generated keys sat in a 0700 directory under the session's scratchpad. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name was present. The container and the files were removed afterwards.
- **First database:** `migrate` from zero; `makemigrations --check --dry-run` → `No changes detected`. The suite → `29/31` (two test bugs, fixed: a suspended candidate's own profile read, now cached; a cursor the case itself invalidated by paging the target first). Every reversal ran on this database.
- **Second, fresh database:** `migrate` from zero; `No changes detected`; `[discovery] cases: 32/32 passed in 127.0 s`; `discovery secret scan: clean (1099 secrets held; 0 found in 647 log records, 66 writes and the results JSON)`; `discovery value scan: clean (603 member values held …; 0 found in the same output)`; `DISCOVERY VERDICT: PASS`; a second run → `refusing a used database: …`, exit 1.

### The run of record

- **The code head's run did not start.** Foundation run [43096394432](https://github.com/amthorn78/glow-dating-app/actions/runs/43096394432), on the push of `ad9ff08` at 20:29:52 UTC, stayed `queued` with no job created (still none at 20:56 and at 21:07 UTC). GitHub's status page showed Actions operational, and a Webhooks incident from 20:22 to 20:26 UTC, resolved before the push. Whether that incident caused it is not known. The prompt forbids this session to re-run or dispatch a run, and the push rule forbids any push before the run has finished.
- **Nathan's direction**, asked in this session. The first question overstated the wait as about 55 minutes; by the clock it had been about 25. Of four options (he re-runs it; keep waiting; push the records now; stop and report), he chose "Push records now". Asked again at 20:56 UTC with the corrected 26 minutes, he chose **"Yes, push records now"**. So this records commit, Markdown only, is pushed now, and its run, on the records head (the same code as `ad9ff08`, plus Markdown), is the run of record. This departs from the push rule and from "the run of record is the one on your last code commit"; the code it runs is the code head's. The workflow's concurrency group (`cancel-in-progress: true`) cancels the queued run when this commit is pushed.
- **Its figures** follow in the next records commit, pushed after it has finished.

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
- **Not run here:** the mobile app's export and rendered checks, and `playwright install` (CI's); any provider, HDE, Stream or Railway call; `proofs/stream-chat`. Stage B's checks 7 to 11 and the concurrency cases DB05 and DB10's action half are Stage B's.

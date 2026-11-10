# DM-55 — SV2 Stage A's exact-head review: C1-3, the rulings it asks for, and correction C2's scope

- **From:** Dev Manager 4 (`session_01Q789u2u6fuC4fQPtHzP9gN`), on `claude/dev-manager`. **To:** App Manager 10, relayed by Nathan (OD-25).
- **Read at:** `496c39e202794e06b2b9d61be8a9a7bbffd1d7ce` of `claude/magical-wozniak-yfmmx2`. Also read: C1's code head `86a2156` (no code path changes between it and `496c39e`), Stage A's branch `claude/sv2-stage-a-impl-0qqzvj` at `f2635fa`, C1's branch `claude/funny-lamport-5f2s1u` at `f54545c`, and `main` at `c864edd`. All five were still there at 15:04 UTC (`git ls-remote`).
- **Written:** 10 November 2026, finished at 15:04 UTC by the clock.
- **Boundaries kept:**
  - I checked environment variable names only; none of the six names is present.
  - I called no provider, database, HDE, Railway or TypeSafe service, ran no application code, and wrote only this file.
  - Notion was read, not edited.

## 1. What I read

- **The consultation,** and the evidence record's "Exact-head review of Stage A": the gates, what the review ran, its threat model, the 15 findings and the manager's dispositions.
- **The code at `86a2156`:**
  - `glow_profiles/operations.py`: the adult check (`adult_check`, lines 896 to 967), the birth input (`save_birth_input`, 973 to 1074) and its refusal (`_refuse_failing_birth_input`, 1082 to 1109), `_invalidate_birth_input`, `_sensitive_accepted` (128 to 130), `set_field`, `set_preferences`, both consent writers, `_withdraw_sensitive_data` (798 to 824) and the owner's reads;
  - `recompute.py`, `idempotency.py`, `settings_store.py` (`read_shared`'s name order), `catalog.py`, `contract.py` (`number`, `parse`, `own_birth_input`) and `views.py`;
  - `glow_domain/identity.py` (`adult_outcome`, `age_years`), `glow_domain/profile_fields.py`, `glow_domain/profile_settings.py` (`_history_refusals`, lines 391 to 416, and the history launch default);
  - `glow_identity/age.py` (`age_years`);
  - `glow_persistence/models.py`: `BirthInput` (its two checks) and `OutboxEvent` (`dedup_key`);
  - the schema's `OwnBirthInput`, `BirthInput`, `AdultCheckIntent` and `OwnAgeState`;
  - `flows-v1.json`'s F02;
  - P04's client rule: `apps/mobile/src/onboarding/policy.ts` (`adultOutcome`) and `store.ts` (`setAdultDate`, `saveBirth`).
- **At `496c39e`:** the brief, revision 4; `data-model.md`'s rows, its outbox rule and its erasure section; `production-contracts.md`'s error table and SV2 server mapping; the carried-items file; the P11 plan; the CI policy's `upload-artifact` row; the Foundation workflow's four upload steps; the review log.
- **Notion,** read-only (section 12).

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1. A date that fails, at both writers | **Changes requested: option (b), not (a).** A future date is invalid input at both writers and changes nothing; only a date under 18 resets a self-declared adult. **1.2 and 1.3 approved** for that date. **1.4 declined as worded:** an erased revision cannot be read through the existing `OwnBirthInput`, and the rest of the design is G-01's. The decision is carried to P07. Z1 to Z5 and Z18 give the words |
| 2. The history setting's limit | **Approved: (a).** Z6 to Z8 give the words, the manager's tightened |
| 3. The sensitive consent's version | **Approved with conditions: (a).** The pointer is read in the settings store's name order. What a new version asks of existing values is P08's, beside DM-54's K3, not K1. Z9 to Z11 and Z19 |
| 4. C1-1 | **Approved: (a).** No new design words; one review focus item (Z12) and two notes for C2's prompt |
| 5. The withdrawal's field rows | **Approved with conditions: (a).** The display flag also goes off, and a row with nothing to remove stays unchanged. Z13 to Z15 |
| 6. The manager's settled items | **Confirmed, with two changes:** `age_years` stays, with a test, and its place is named in the owned paths (Z16, Z17); the 405 also goes to P11's plan (Z20) |
| 7. DM-53's and DM-54's conditions | **Confirmed as applied,** with no departure (section 9) |
| 8. C2's scope and its review | **Agreed:** a full exact-head review with a written threat model. Under these rulings C2 needs no model change and no migration (section 10) |
| Notion | **Matches** `496c39e`, with one nit (section 12) |

**How to apply:**
- **Z1 to Z17** change the brief, **Z18 and Z19** the carried-items file and **Z20** the P11 plan, all in given words; line breaks may move.
- **Verified by script:** every condition was applied in order to copies of the three files at `496c39e`, and each passage was found exactly once, before and at its turn.
- **No further read is needed before C2's prompt** if they are applied as written; a departure comes back first. My next consultation confirms them as applied (step 6).

## 3. Item 1 — A future date, and a date that fails the adult rule

**(b).** A future date is invalid input at both writers, refused with no change. A date under 18 is the one that fails the adult rule, at both writers, with the reset.

**Why (b), not (a):**
- **A future date declares no age.** The reset exists because a date under 18 is the member saying they are a minor (G-01). A future date says nothing about age. Like an impossible date, it is a date no one is born on.
- **P04's rule groups it with the impossible date, not with the date under 18.** D7 takes its order and its one date from P04's rule.
  - `adultOutcome` returns `unknown` for both, not `fail` (`policy.ts`, lines 24 to 29).
  - `setAdultDate` refuses both with one message, "Enter a real civil date that is not in the future", and changes nothing (`store.ts`, lines 220 to 223), even for an adult.
- **The server already codes it as invalid input:**
  - `invalid_request` at the eligibility step for an `unknown` account (`operations.py`, line 926);
  - `birth_date_in_future` at the birth input (line 1019);
  - the contract document's F02 sentence: "under 18 is `forbidden` and a future date `invalid_request`".
- **(a) splits two kinds of invalid input.** An impossible date is refused at parse and changes nothing, while a future date would reset the account, though neither is a birth date.
- **(a) costs a real adult their state over a typo.** A mistyped year in the future would demote a visible profile and make the member re-enter their birth input. Under (b) they see an error.
- **Safety is the same under both** (the review): nothing of the input is kept either way, and a minor gains nothing from a future date.
- **The words do not favour (a) when read whole:**
  - Check 7's list ("under 18, a future date and an invalid date each fail") is the first check's, where an impossible date also "fails", and no one proposes a reset for that.
  - Check 7's rerun sentence names only "under 18".
  - D7's "Every date change reruns the check" assumes a date the check can take.
- **(b) needs about as much rewriting as (a).** The manager's words for (a) replace three places (D7's bullet, D8's sentence, check 7). (b) replaces the same three, plus D7's check sentence (Z1).
- **P04's client refusing a future date** makes either option cheap. The server must not rely on it, and under (b) it refuses the date too.

**1.2 approved:** for a self-declared adult, the date is checked first, after the idempotency check and before the request's other refusals. That covers a stale version (both writers), and a birth time not given or a lapsed onboarding consent (the birth input).
- A date under 18 is the member's statement that they are a minor. A defect elsewhere in the same request must not hide it.
- A key conflict still refuses first. That is a client fault, and a minor gains nothing from it: the account stays as it was, and the next request with a new key is read.

**1.3 approved:** the eligibility step's failing rerun is refused (`forbidden`), not `applied`, keeps no idempotency record, and commits the reset. Today it answers 200 `applied` and keeps the keyed record for 24 hours (the review's P5).

**1.4 declined as worded; the decision is carried to P07 (G-01).** Erasing every revision is the right aim, but the words leave four parts undesigned:
- **The owner's read cannot return an erased revision.**
  - `OwnBirthInput` requires `input`. `BirthInput` requires `birth_date`, `time_precision` and `place_label` as strings (the schema at `86a2156`), and `contract.own_birth_input` calls `row.birth_date.isoformat()` (`contract.py`, line 506).
  - So both reads, the latest and by `input_id`, would fail on an erased revision.
  - The fix is a new read rule (an erased revision refused as `not_found`), or a changed DTO. D11 forbids the second: an existing closed payload needs a negotiated contract version.
- **The next save needs a rule for its expected version.** A client that reads `not_found` sends 0, while the save compares it with the erased row's version (line 1010) and refuses it as stale.
- **An existing check needs changing.** `birth_time_uncertainty` (`models.py`, lines 498 to 502), one of the checks P11's proof waits for, ties `local_time` to `time_precision`. An erased revision needs it amended, or relies on SQL passing a check that evaluates to NULL.
- **Erasure is G-01's to design.**
  - What Glow does with a suspected minor's data beyond refusing the input is G-01's (D7).
  - Erasing a member's data is a path a G-05 hold may need to stop. D10 makes every purge SV2 builds ask the hold port first, and SV2 has no hold port outside media.

Until P07 decides:
- **The earlier revisions stay as built:** readable only by their owner, and never current again, since only a new submit writes a current revision.
- **Nothing real is at risk:** the runtime is sealed until P11, and no member's data exists.

Z18 carries the decision, with these facts. **Y6's closing clause was my error** (section 11). Z2 replaces it with a sentence that claims only what the code does.

**What C2 builds:**
- **The eligibility step:**
  - For a self-declared adult, the date's outcome comes before the stale version check.
  - A future date is refused `invalid_request` and changes nothing.
  - A date under 18 returns the refusal without raising, commits the reset, and stores no record.
- **The birth input:** the date's outcome comes right after the adult-check gate, before the onboarding consent, the stale version and the time.
- **The tests:** check 7's cases at both writers, each with its reversal. That includes a date under 18 behind each of the three later refusals, and a future date at each writer.
- **The records:** the data model's `AccountAgeState` row and the contract document's F02 and F03 sentences follow Z2.

**Z1:** in D7, "The check", replace:

> ```
> A failing date is refused and not stored, and the state stays `unknown`;
> ```

with:

> ```
> An impossible date, a future date and a date under 18 are each refused and not stored, and the state stays `unknown`;
> ```

**Z2:** in D7, replace the bullet:

> ```
>   - **A birth input whose date fails the rule is not stored (DM-54).** It is refused, and nothing of it is kept, but its transaction still commits the failing rerun: the age state becomes `unknown` with no date, a current birth input stops being current (`missing`, its mapping back to `pending`), and a `visible` profile becomes `incomplete`. The operation returns the refusal without raising, so the transaction commits, and it stores no idempotency record, so a retry is refused at the adult-check gate and changes nothing more. "A failing date is refused and not stored" then holds on both paths, and no birth data of a self-declared minor is kept (G-01). P04's `saveBirth` saved the input; the server does not.
> ```

with:

> ```
>   - **A future date, and a date that fails the adult rule (DM-54; DM-55).** A date fails the adult rule when it is under 18 at the server's clock. A date in the future does not fail it: like an impossible date, it is invalid input, declares no age and never reruns the check (P04's rule: `setAdultDate` refuses both and changes nothing).
>     - **For an account whose state is `self_declared_adult`,** both writers, the eligibility step and the birth input, check the date first, after the idempotency check (a replay or a key conflict) and before any other refusal (a stale version, a birth time not given, a lapsed onboarding consent). A future date is refused `invalid_request` and changes nothing. A failing date is refused `forbidden`, nothing of it is stored and no idempotency record is kept, but the transaction still commits the failing rerun: the age state becomes `unknown` with no date, the current birth input stops being current (`missing`, its mapping back to `pending`), and a `visible` profile becomes `incomplete`. The operation returns the refusal without raising, so the transaction commits. A retry is refused, since the account is no longer an adult's, and changes nothing more.
>     - **For an account whose state is `unknown`,** the eligibility step refuses a future date (`invalid_request`) or a failing one (`forbidden`) and changes nothing, and the birth input is refused at its adult-check gate.
>     - Nothing of a refused date is stored on either path. Earlier birth input revisions keep their contents, readable only by their owner and never current again; whether a failing rerun erases them is G-01's, in P07 (DM-55). P04's `saveBirth` saved the input; the server does not.
> ```

**Z3:** in D8, replace:

> ```
> A revision whose date fails the adult rule is refused and not stored (D7; DM-54).
> ```

with:

> ```
> A revision whose date is in the future is refused as invalid input and changes nothing; one whose date fails the adult rule is refused and not stored, while the failing rerun commits (D7; DM-54; DM-55).
> ```

**Z4:** in acceptance check 7, replace:

> ```
> under 18, a future date and an invalid date each fail, the date is not stored, and the age state stays `unknown`. A corrected date reruns the check: under 18, the state becomes `unknown`, the date is cleared, and a visible profile becomes `incomplete`, so a send is refused. A birth input with another date changes the age state's date. A birth input whose date fails the rule is refused and stores nothing, while the age state becomes `unknown`, a current birth input `missing` and a visible profile `incomplete`; a retry is refused and changes nothing.
> ```

with:

> ```
> a date under 18 fails, a future date and an impossible one are invalid input, none is stored, and the age state stays `unknown`. For a self-declared adult, a future date, at the eligibility step or in a birth input, is refused (`invalid_request`) and changes nothing. A corrected date under 18, at either, is refused (`forbidden`) before the request's other refusals (a stale version, a birth time not given, a lapsed onboarding consent) and stores nothing, with no idempotency record, while the failing rerun commits: the age state becomes `unknown` with no date, the current birth input `missing` with its mapping back to `pending`, and a visible profile `incomplete`, so a send is refused. A retry is refused and changes nothing. A birth input with another passing date changes the age state's date.
> ```

**Z5:** in the review plan's focus, replace:

> ```
>   - a birth input whose date fails the adult rule: nothing of it is kept, the rerun's effects commit, and a retry changes nothing more;
> ```

with:

> ```
>   - a date that fails the adult rule, at either writer: nothing of it is kept and no idempotency record is kept, the rerun's effects commit before the request's other refusals, and a retry changes nothing more; a future date changes nothing at either (DM-55);
> ```

## 4. Item 2 — The history setting's limit

**(a).** One comparison, and it keeps the setting's version label meaningful.
- **The gap is real:**
  - `_history_refusals` checks the label only when a cause becomes more readable (`profile_settings.py`, lines 405 to 415).
  - A first publication can move the label alone. A second then names the version members already accepted.
- **Under (a), the label changes only with a more readable change,** and then to the onboarding consent's current version.
  - Onboarding labels only grow (`policy_version` numbers them by publication).
  - So each more readable change needs an onboarding version published since the one the setting names.
  - The launch default names `consent.onboarding.v1` with every cause already read-only, so the first more readable change, after a cause is hidden, needs a version 2.
- **(b) works too,** but it reads the setting's history at each publication, and it leaves the label free to move when nothing becomes more readable.

**Z6:** in D2's fixed limits, replace:

> ```
>     - a change to H that makes more readable reaches a member only after they accept the consent wording that describes it (OD-60's table, H);
> ```

with:

> ```
>     - a change to H that makes more readable reaches a member only after they accept the consent wording that describes it (OD-60's table, H). The history setting names the onboarding consent version whose wording describes it: a publication that makes a cause more readable names the onboarding consent's current version, which must differ from the version the current setting names, and a publication that makes nothing more readable keeps the version the current setting names. Each more readable change therefore needs an onboarding version published since the one the setting names (DM-55);
> ```

**Z7:** in acceptance check 1, replace:

> ```
>    - a publication crossing each fixed limit is refused, and nothing is written;
> ```

with:

> ```
>    - a publication crossing each fixed limit is refused, and nothing is written, including a history publication that changes the consent version it names while making nothing more readable (DM-55);
> ```

**Z8:** in the review plan's focus, replace:

> ```
>   - the settings' fixed limits and audit;
> ```

with:

> ```
>   - the settings' fixed limits and audit, including a limit crossed in two publications (DM-55);
> ```

## 5. Item 3 — The sensitive-fields consent's version

**(a), with two changes to the words.**
- **Why (a):** it is F02's rule ("old consent version rejected") at the one place SV2 collects new sensitive data. The acceptance already checks the current version under the pointer's lock. Today the saves check only that the latest decision is `accepted` (`operations.py`, lines 128 to 130).
- **The lock order:**
  - `set_field` and `set_preferences` read the catalog's settings `FOR SHARE` in one `read_shared` call, after the account row lock.
  - The settings store's rule is name order across those reads (`settings_store.py`, its docstring and `read_shared`).
  - `consent.sensitive_profile` sorts before every `profile.*` setting. So the save reads it in the same call as the catalog's settings, not in a second read afterwards. Z9 says so.
- **The carry:** what a new version asks of existing values is the analogue of DM-54's K3 (P08: what a new onboarding version requires of existing members). DM-54's K1 is SV3's reading of the onboarding version in discovery. Z9 names P08, and Z19 carries it.
- **A consequence, accepted:**
  - `PreferencesIntent` carries all four sets, so a member who narrowed a sensitive set under an older version cannot save any set until they accept the current version or put that set back to all.
  - The same holds for re-saving a stated orientation.
  - That is the rule ("each of those saves"), so C2 and its review should not treat it as a defect. P10's client prompts for the new version.

**Z9:** in D6, "The sensitive-fields consent", replace:

> ```
> before either field's "show me" set is narrowed.
> ```

with:

> ```
> before either field's "show me" set is narrowed. Each of those saves needs the consent accepted at its current version, read under its policy pointer's lock with the save's other settings, after the account row lock and in name order (the settings store's rule; F02: "old consent version rejected"). A value, own words or a narrowed set saved under an earlier version stays until the member's next such save or a withdrawal; what a new version asks of them is P08's (DM-55).
> ```

**Z10:** in acceptance check 2, replace:

> ```
>    - orientation and relationship status, orientation's own words, and narrowing either field's set are refused without the sensitive-fields consent;
> ```

with:

> ```
>    - orientation and relationship status, orientation's own words, and narrowing either field's set are refused without the sensitive-fields consent: before it is accepted, after its withdrawal, and while the version accepted is not the current one (DM-55);
> ```

**Z11:** in the review plan's focus, replace:

> ```
>   - consent's purpose filtering and the current-version check;
> ```

with:

> ```
>   - consent's purpose filtering and the current-version check, at each acceptance and at each sensitive save (DM-55);
> ```

Z10 also covers the review's finding 4 (a sensitive save after a withdrawal) and item 3's own case. Each needs its reversal.

## 6. Item 4 — C1-1, a lapse the profile edit finds

**(a).** Y4's words already say it: "The owner's own edit that clears the summary keeps the existing owner `edit`". Any other demotion that follows another write is `requirement_removed`.
- **As built:** `recompute.entry` gives every demotion in the profile edit `edit` (`recompute.py`, lines 83 and 84), and only `requirement_removed` emits `profile_demoted` (lines 130 to 136). The contract document's F04 sentence then misdescribes the code.
- **The display name cannot be cleared** (D9: "refused, since each is replaced, never cleared"), so the test is the summary alone.

**Two notes for C2's prompt:**
- **An edit that clears the summary is `edit`, whatever else is missing.** It is the owner's own removal, and Y4 names it.
- **A `requirement_removed` demotion in the profile edit is a transition of its own.**
  - It bumps the profile's version and the account's `eligibility_version` and emits `profile_demoted`, as in every other writer. Only the owner's `edit` rides on the edit's own write.
  - The two events then carry different versions. Their `dedup_key`s would not collide anyway, since the key includes the event type.

**Z12:** in the review plan's focus, replace:

> ```
>   - D9's recompute at the end of every requirement writer: no path makes a profile `visible` with a requirement missing, and none leaves one `visible` after a write that finds one missing;
> ```

with:

> ```
>   - D9's recompute at the end of every requirement writer: no path makes a profile `visible` with a requirement missing, and none leaves one `visible` after a write that finds one missing; each change has its own registry entry and event, and only the profile edit that clears the summary is the owner's `edit` (DM-55);
> ```

## 7. Item 5 — The withdrawal's field rows

**(a), with two additions.**
- **Why (a):** it keeps the data model's rule ("Outbox payload references must target an existing owning record") and D6's outcome. Today `_withdraw_sensitive_data` deletes rows (`operations.py`, line 800) that earlier `profile_field_changed` events name (lines 414 to 421).
- **The display flag goes off.** Deleting the row removes the flag today. An in-place reset that kept `shown` would keep the member's earlier choice to show a sensitive field. Every later save sets the flag from its own intent, so nothing is lost.
- **A row with nothing to remove is left as it is,** with no version bump and no event. The words are then deterministic, and no event says a change happened when none did.
- **The setting version stays as it was.** `not-stated` is valid under every list version, and reading the lists' pointers would add locks for nothing.

**Z13:** in D6, "The sensitive-fields consent", replace:

> ```
> Withdrawal, in one transaction, removes the member's own orientation and relationship status values and orientation's own words, resets those two "show me" sets to all, and deletes the member's idempotency records of the commands that carried any of them (D17).
> ```

with:

> ```
> Withdrawal, in one transaction, sets each of the member's orientation and relationship status rows to "not stated" in place, with no own words, its display flag off and its setting version unchanged, bumping the row's version and emitting `profile_field_changed` for it, so that earlier events still name an existing record; a row that already holds "not stated" with no own words and its flag off is left as it is, with no event (DM-55). It also resets those two "show me" sets to all, and deletes the member's idempotency records of the commands that carried any of them (D17).
> ```

**Z14:** in acceptance check 6, replace:

> ```
>    - the sensitive-fields consent's withdrawal removes the two values and resets their sets;
> ```

with:

> ```
>    - the sensitive-fields consent's withdrawal removes the two values, leaving each row "not stated" in place with its event, and resets their sets (DM-55);
> ```

**Z15:** in the review plan's focus, replace:

> ```
>   - the outbox: events carry references, never values;
> ```

with:

> ```
>   - the outbox: events carry references, never values, and each reference names a record that still exists (DM-55);
> ```

**The records:** the data model's `ProfileFieldChoice` row ("its withdrawal deletes them") and the contract document's F02 sentence ("removes the member's orientation and relationship status values") follow Z13 in C2.

## 8. Item 6 — The manager's settled items

- **Finding 11: confirmed in the manager's words.** I traced each cause:
  - `contract.number` calls `math.isfinite` on a 321-digit integer, which raises `OverflowError`, not `Invalid`;
  - deep nesting raises `RecursionError` in `json.loads`;
  - U+0000 passes `text_ok` and fails at the database, which `tx.run` reports as `provider_unavailable`.
  Each of the three escapes `_BadRequest` today.
- **Finding 14: confirmed.** F02 has `accept` from `required` and `withdrawn`, and `accept_sensitive` from `not_given` and `withdrawn`, but neither from `accepted`. Both writers make that move at a newer version. The two new entries add no change to an existing entry.
- **Findings 3 to 7: confirmed,** each with its reversal. Finding 4's case is also Z10's.
- **Finding 15: confirmed, except `age_years`.** Keep it, and add a test:
  - **Why keep it:** D4 makes SV3 read a member's age "through a function that returns whole years, never the date". `age_years` is that function, on the age port, and both the data model's `AccountAgeState` row and `identity.py`'s age section name it. Removing it would leave both stale and send SV3 towards reading `AccountAgeState.birth_date` itself.
  - **What it lacks is a test:** nothing calls it, and the API tests cannot reach the database. C2 adds a profile-suite case with its reversal: whole years for a self-declared adult, `None` while `unknown`, and an integer, never the date.
  - **Its place was outside the owned paths' letter,** which give `age.py` to "D7's transition only". I approve it there as D4's read. Z16 and Z17 name it, so a later session's scope check finds it allowed.
- **Finding 8: confirmed,** with the data model's `AccountAgeState` and `ProfileFieldChoice` rows and the contract document's F02 to F04 sentences following items 1, 4 and 5.
- **Carried: confirmed,** with one addition:
  - the error table (`production-contracts.md`, line 19) gives `invalid_request` 400 only;
  - recording the 405 in C2's record leaves no one to resolve it;
  - so it also goes to P11's plan, where the routes are served (Z20).
- **The CI policy's `upload-artifact` row: confirmed** as applied at `496c39e`. There are four uploads, one in Mobile checks (line 124) and three in Database proof checks (lines 607, 721 and 730), each with `if-no-files-found: ignore`. My pre-merge read re-checks it at the final head.

**Z16:** in D4, replace:

> ```
> through a function that returns whole years, never the date.
> ```

with:

> ```
> through the age port's `age_years`, which returns whole years, never the date (DM-55).
> ```

**Z17:** in "Owned paths" and "Exclusions", three replacements:

> ```
> and in `identity.py`, the age section only, for D7's date and transition.
> ```

with:

> ```
> and in `identity.py`, the age section only, for D7's date and transition and D4's `age_years` (DM-55).
> ```

and:

> ```
> - `services/api/glow_identity/age.py`: D7's transition only; `record` is unchanged.
> ```

with:

> ```
> - `services/api/glow_identity/age.py`: D7's transition and D4's `age_years` only; `record` is unchanged (DM-55).
> ```

and:

> ```
> - `services/api/glow_identity/**`, except D7's transition in `age.py`: SV2 uses its actor class unchanged.
> ```

with:

> ```
> - `services/api/glow_identity/**`, except D7's transition and D4's `age_years` in `age.py` (DM-55): SV2 uses its actor class unchanged.
> ```

## 9. Item 7 — DM-53's and DM-54's conditions as applied

**Confirmed as applied at `496c39e`, with no departure.** Checked by script, with whitespace normalized:
- **W1 to W10,** in the brief's revision 3, are in revision 4. W5's block is there as Y4 amended it: Y4 inserts two F04 entries inside it, and W5 with Y4 applied is present.
- **Y1 to Y10 and Y12** are in revision 4, and **Y11** is in `data-model.md`. No replaced passage remains.
- **K1 to K5** are each in their section:
  - K1 in "Carried to SV3";
  - K2 in "Carried to SV4";
  - K3 in "Carried to P08";
  - K5 in "Carried to P07";
  - K4 in the P11 plan.
- **The manager's marked choices:** the three choices marked "the manager, on DM-52's words" are D1's stage for D18, D7's one date and D9's removals, which DM-53 approved. None is marked on DM-53's or DM-54's words.
- **Supersession sweep:** the brief's other sentences on the adult check, the birth input, the withdrawal and the age function agree with Z1 to Z17 once applied:
  - D7's "Every date change reruns the check";
  - D8's resolution states;
  - D9's list of removals;
  - F02's and F04's entries;
  - check 6's other bullets;
  - D17's withdrawal sentence;
  - D3's own-words sentence.
  "Stage A, correction C1" describes C1 as it was and stays.

## 10. Item 8 — Correction C2's scope and its review

**Agreed.** C2 changes designs on two security boundaries, the adult rule and the sensitive data's consent, and it is well over 60 non-test lines. So a full exact-head review with a written threat model reads C2's head, not a delta review (M05 S2). Codex reads the PR's head as usual.

**C2's scope under these rulings:**
- item 1's order and refusals at both writers, with no migration (1.4 carried);
- items 2 to 5's code, tests and records;
- item 6's fixes, with `age_years`' test in place of its removal;
- the record corrections.

**A stop rule like C1's still fits.** The changes need:
- no model, migration or DTO change;
- no change to `glow_chat`, `glow_identity`, `glow_api`, the workflow, a lock or a dependency;
- no change to an existing registry entry: finding 14's two entries are new.

**The review's focus** is the brief's list with Z5, Z8, Z11, Z12 and Z15.

## 11. My errors

- **Y6's closing clause overclaimed.** "No birth data of a self-declared minor is kept (G-01)" said more than its operative words, which make only the current revision stop being current. Finding 13 is right. Z2 replaces the clause with what the code does, and Z18 carries the rest.
- **DM-54's words left C1-3 open.** My section 8 reasoned only about a date under 18, and its words ("a date that fails the rule") left a future date unsettled. Codex's P2 and the review's finding 2 follow from that. Z1 to Z4 settle it.
- **I missed `age_years`' place.** In DM-54 I checked the changed paths, but not that `age_years` sat in `age.py` beyond "D7's transition only". The review did not flag it either. Z17 records it.

## 12. Notion (read-only, at about 14:50 UTC)

- **Implementation Control** (page content as of 14:27 UTC) is matched to `496c39e`. Its status names the review's verdict and statements, DM-55's questions and the next steps.
- **The Work Register:**
  - SV2's row is "In progress", with evidence at `496c39e` and DM-55's next steps;
  - A05's row is "In progress" and records OD-60 and OD-61;
  - G-01's row is "Planned". It is an umbrella with no session of its own, so Z18's carry goes to P07's section, which names G-01.
- **Nit:** the Dev Manager page (content as of 05:54 UTC) has no DM-55 row. The review log has it as pending since `496c39e`. Add it with DM-55's disposition. The repository wins (OD-27).

## 13. Carried items

**Z18:** in the carried-items file, "Carried to P07", after DM-54's K5 entry, replace:

> ```
> Also the idempotency records' retention (24 hours, provisional).
> ```

with:

> ```
> Also the idempotency records' retention (24 hours, provisional).
> - **From SV2 Stage A's exact-head review (DM-55), for G-01:** what Glow does with a self-declared minor's earlier birth input revisions. A date under 18 from a self-declared adult is refused and nothing of it is stored, the age state becomes `unknown`, and the current revision becomes `missing`, but every revision keeps its date, time, place and time zone, readable only by its owner and never current again. P07 decides, before P11 wires the runtime, whether that reset erases them. Erasing them in place keeps the rows, since events name them, and needs: a read rule, since `OwnBirthInput` requires a full `BirthInput` (an erased revision refused as `not_found`, or a negotiated contract version); a save rule for the next revision's expected version; nullable `birth_date`, `time_precision` and `place_label`, with `birth_time_uncertainty` amended; and a place for G-05's hold, which may need to stop an erasure.
> ```

**Z19:** in the carried-items file, "Carried to P08", after DM-54's K3 entry, replace:

> ```
> Until P08 decides, a `visible` member's next requirement write demotes them (D9's recompute).
> ```

with:

> ```
> Until P08 decides, a `visible` member's next requirement write demotes them (D9's recompute).
> - **From SV2 Stage A's exact-head review (DM-55):** what a new sensitive-fields consent version asks of the orientation and relationship status values, orientation's own words and the narrowed sets saved under an earlier version: re-acceptance, a grace period or removal. Until P08 decides, they stay until the member's next such save or a withdrawal, and that save needs the current version (D6).
> ```

**Z20:** in the P11 plan, after DM-54's K4 entry, replace:

> ```
> P11 plans the sweep with the retention the third A05 message sets.
> ```

with:

> ```
> P11 plans the sweep with the retention the third A05 message sets.
> - **From SV2 Stage A's exact-head review (DM-55):** a wrong method on an SV2 route answers `invalid_request` with status 405, while the contract document's error table gives `invalid_request` 400 only. When P11 serves the routes, it either adds 405 to the table or answers 400.
> ```

The manager's own carries from the review stand beside these:
- the revocation or restriction of a non-active account, and `publish` taking a `system:` subject, to P07;
- the adult check's upper bound, to G-01 with P07;
- `IdempotencyRecord`'s missing account key, to P11.

## 14. Where each item goes

- **The brief's revision 5:** Z1 to Z17, and C2's section with finding 11's words, the manager's.
- **The carried-items file:** Z18 and Z19. **The P11 plan:** Z20.
- **C2's prompt:**
  - section 3's "What C2 builds";
  - section 6's two notes;
  - section 8's `age_years` test;
  - findings 3 to 8, 14 and 15 as confirmed;
  - the stop rule in section 10.
- **The review log:** DM-55's disposition. **Notion:** the Dev Manager page's DM-55 row.
- **My pre-merge read, after C2's review:**
  - the CI policy's text;
  - the data model's and contract document's rewritten texts;
  - C2's section of the brief;
  - the deferred row for DM-54 section 13.

Status: complete

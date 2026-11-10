# DM-54 — SV2 Stage A as built: the session's decisions, what moves a profile to visible, and a correction's scope

- **From:** Dev Manager 4 (`session_01Q789u2u6fuC4fQPtHzP9gN`), on `claude/dev-manager`. **To:** App Manager 10, relayed by Nathan (OD-25).
- **Read at:** `93a27ea4faa67bf258135236fc92f5f97a3d5635` of `claude/magical-wozniak-yfmmx2`, with Stage A's code head `b97bc15` and records `f2635fa` on `claude/sv2-stage-a-impl-0qqzvj`, and `main` at `c864edd`. All four were still there at 05:34 UTC (`git ls-remote`).
- **Written:** 10 November 2026, finished at 05:45 UTC by the clock.
- **Boundaries kept:**
  - I checked environment variable names only; none of the six names is present.
  - I called no provider, database, HDE, Railway or TypeSafe service, ran no code, and wrote only this file.
  - I read the run of record through the GitHub tools.
  - Notion was read, not edited.

## 1. What I read

- **The consultation,** and the evidence record's Stage A sections: the run of record, the limits, the session's 13 decisions, and the manager's verification.
- **The code at `b97bc15`:**
  - `glow_profiles`: `operations.py` (the profile edit, the demotion, the adult check, the birth input, visibility), `requirements.py`, `identity_verification.py`, `staff.py`, `idempotency.py`, `settings_store.py`, `contract.py` (`parse`, `_integral`);
  - `glow_domain/profile_settings.py`;
  - migration `0007` (the launch defaults);
  - `services/api/pyproject.toml`'s `[tool.mypy]`;
  - the schema's `AdultCheckIntent` and `OwnAgeState`;
  - `flows-v1.json`'s F02 to F04;
  - the Foundation workflow's four SV2 steps.
- **The changed paths,** `c864edd..b97bc15`: `identity_support.py` is unchanged.
- **Every place that makes a profile `visible`:** only the profile edit (`operations.py`, line 343), and resume through `glow_chat`.
- **At `93a27ea`:** the brief, revision 3; `data-model.md`'s "Identity, time and field semantics"; the CI policy's two changed paragraphs; the carried-items file and the P11 plan.
- **Push run 42759801460's eight jobs:** each `success` on `b97bc15`, every DM-41 retry step `skipped`, and the four SV2 steps `success`.
- **Notion,** read-only (section 16).

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1. Two launch values | **Approved.** Both seeds are right: the session invented no value OD-60 does not give. Both values go to Nathan in the third A05 message, each with a recommendation; nothing needs them sooner. Y1 records them in D2 |
| 2. `AdultCheckIntent` and `OwnAgeState` | **Approved as additive.** D7's step comes before any birth input, so it needs its own intent and read, which D11's list (and my DM-52 conditions) left out. Y2 names them in D11 |
| 3. What moves a profile to `visible` | **(a), as one recompute at the end of every requirement writer.** It makes a profile `visible` as soon as its last requirement is met, whoever meets it, and makes demotion uniform. Y3 to Y5 give D9's words, the registry entry `requirements_met` (`system`) and the check |
| 4. The idempotency records' lifetime | **Approved,** 24 hours, provisional. Expired records are removed only when their key is reused, and nothing sweeps the rest. The sweep and the retention are carried (K4, K5) |
| 5. A new onboarding consent version | **Acceptable for Stage A,** with item 3's recompute, under which a lapsed version demotes at the member's next requirement write of any kind. What a publication does to existing members is P08's rule. Discovery's and messaging's reads of the version are SV3's and SV4's (K1 to K3) |
| 6. A birth input whose date fails | **(b).** The input is refused and nothing of it is stored, while its transaction still commits the failing rerun. Y6 to Y8 give the words |
| 7. CI's mypy | **Approved,** with Y9. `glow_persistence`'s exclusion is deliberate, not a gap: the config skips it as "untyped Django declarations" |
| 8. Restriction's registry entries | **Right, under W5:** `restrict` from `visible` and `paused` to `restricted` (`moderator`; `A05`), in Y4 |
| 9. The stale sentence | **Approved,** with the next sentence too, which OD-61 qualifies (Y10, Y11) |
| 10. The manager's four settled items | **Confirmed** (section 12) |
| The CI policy's paragraph | **Read now, and it matches** the workflow's four SV2 steps. The pre-merge read needs only to confirm that it, and those steps, are unchanged at the PR's final head, or to read what C1 changes (section 13) |
| The correction | **C1 carries Y3 to Y11's changes,** with Codex's findings if any. No review has read Stage A yet, so C1 needs no delta review: the exact-head review, with its written threat model, reads the corrected head in full (section 14). Y12 adds two focus items |
| Notion | **Matches** `93a27ea`. DM-53's two nits are fixed |

**How to apply:**
- **Y1 to Y10 and Y12** change the brief, and **Y11** changes `data-model.md`, all in given words; line breaks may move.
- **Verified by script:** every condition applied in order to a copy of revision 3 (Y11 to `data-model.md`), and each passage was found exactly once.
- **K1 to K5** are carried-item entries (section 15).
- **No further read is needed before C1's prompt** if they are applied as written; a departure comes back first. My next consultation confirms them as applied (step 6).

## 3. Item 1 — Two launch values OD-60 does not give

- **The facts:**
  - OD-60's approved tables give starting lists only for gender, "looking for" and relationship status.
  - Orientation's row has an editable list, but no proposed values.
  - The location row has "console-set distance choices", but no values.
  - So the session was right to invent neither. Migration `0007` seeds `profile.orientation` with `"values": []`, and the distance choices with `anywhere` (no radius, `show_distance` false).
- **Both seeds are safe:**
  - an empty list collects no orientation;
  - `anywhere` shows no distance and allows no triangulation.
- **One consequence the third message must say.** Until orientation has values, every member is "not stated" in it, so orientation matches nothing. That is although Nathan said orientation "DOES need to be used for matching" (OD-60's follow-up). The list is what makes that true.
- **Not sooner than the third message:**
  - nothing in SV2 to SV4 needs the values, since the suites publish their own;
  - P07's console is what publishes them, and the third message comes before P07's brief.
- **The distance recommendation should carry DM-52's fact:** a distance counts areas whose internal points are within it, and two members in one area are at distance zero.
- **Y1** records both in D2.

**Y1:** in D2, replace:

> ```
> and the reason "OD-60", or, for D18's setting, the register row that records Nathan's answers of 10 November 2026.
> ```

with:

> ```
> and the reason "OD-60", or, for D18's setting, the register row that records Nathan's answers of 10 November 2026. Orientation's list launches with no values, and the distance choices with `anywhere` only, since OD-60 gives neither; both launch values go to Nathan in the third A05 message (DM-54).
> ```

## 4. Item 2 — `AdultCheckIntent` and `OwnAgeState`

- **Additive, and needed.** D7's eligibility step takes a date before any birth input exists (P04's order), so it needs its own intent and read. D11's list did not have them, and nor did my DM-52 conditions.
- **Their shape:**
  - `AdultCheckIntent` carries `operation`, `meta` and `birth_date`.
  - `OwnAgeState` carries `kind`, `version`, `state` and the owner's own `birth_date`, null when `unknown`.
  - Both are registered in F02, with the projection role `owner` and W5's `adult_check` entries.
- **Disclosure:** the date goes only to its owner (D17).
- **Y2** names them in D11.

**Y2:** in D11, replace:

> ```
>   - the age range and the area, with their reads, and the phone-location query, whose coordinates are bounded and never echoed, and whose response is the nearest area (D5);
> ```

with:

> ```
>   - the age range and the area, with their reads, and the phone-location query, whose coordinates are bounded and never echoed, and whose response is the nearest area (D5);
>   - the adult check's intent (`AdultCheckIntent`) and the owner's age state read (`OwnAgeState`, with the owner's own date), for D7's eligibility step, which comes before any birth input (DM-54);
> ```

## 5. Item 3 — What moves a profile to `visible`

**(a), framed as one recompute at the end of every requirement writer.**

- **OD-61 rules out (b) and (c).** "Approval must be automated based on ID verification", and "the chart is calculated immediately … there is no lag". Under (b) or (c), a requirement the system meets (the chart, the company's verdict, Stage B's photo approval) shows nothing until the member acts again.
- **P04.2's own rule is (a)'s.** Completion is not a member action there: "Remains incomplete unless all current requirements permit completion". (a) applies that rule at every writer, not at one edit.
- **One recompute, not separate "attempts",** also fixes the demotion side:
  - Today only the name-and-summary edit demotes a `visible` profile with any requirement missing (`operations.py`, `save_profile`). So a lapsed consent version demotes on a name edit but not on an area change.
  - One shared function at the end of each writer removes the difference: `incomplete` with nothing missing becomes `visible`, and `visible` with anything missing becomes `incomplete`.
  - `paused`, `restricted` and `removed` stay as they are.
- **The member keeps control.** Pausing is always available (F06), and a paused profile stays paused.
- **The registry:**
  - A completion that follows a write in another flow is `requirements_met` (`system`), mirroring W5's `requirement_removed`. The cause keeps its own entry and actor: F02's `id_check_passed` is `provider`, and F03's `resolve` is `system`.
  - A completion in an F04 owner command keeps `complete` (`owner`).
  - No F04 entry is `provider`.
- **After Stage A:**
  - P11's chart adapter and verification adapter end their writes with the same recompute (K4);
  - Stage B's photo approval does too, in Y3's words, since D10 is the brief's.

**Y3:** in D9, replace:

> ```
>   - **Each change emits** the outbox event SV3's invalidation reads.
> ```

with:

> ```
>   - **What moves a profile to `visible` (DM-54).** Every writer of a completion requirement ends, in its own transaction and on rows read after the account row lock, with one shared recompute: an `incomplete` profile with nothing missing becomes `visible`, and a `visible` profile with anything missing becomes `incomplete`; `paused`, `restricted` and `removed` stay as they are. The writers are:
>     - the owner's: the profile edit, the four fields, the area, the onboarding consent's accept and withdraw, the adult check and the birth input;
>     - staff's: approval without ID verification and its revocation;
>     - after Stage A: P11's chart adapter when it resolves a mapping, P11's verification adapter when it records `verified`, and Stage B's automated photo check when it approves.
>
>     So a profile shows as soon as its last requirement is met, whoever meets it (OD-61: "the human design chart is calculated immediately when someone signs up, there is no lag"; "Approval must be automated based on ID verification"). A requirement that lapses without a write, such as a new onboarding consent version, demotes at the member's next requirement write. The member can pause at any time (F06).
>   - **Each change emits** the outbox event SV3's invalidation reads.
> ```

**Y4:** in D11's registry entries for F04 (items 3 and 8), replace:

> ```
> The owner's own edit that clears the summary keeps the existing owner `edit` from `visible` to `incomplete`.
> ```

with:

> ```
> The owner's own edit that clears the summary keeps the existing owner `edit` from `visible` to `incomplete`.
>     - `requirements_met` from `incomplete` to `visible` (`system`; `eligible`; `A05`): the completion that follows a write in another flow (D9's recompute; DM-54), as `requirement_removed` is the demotion that follows one. A completion in an F04 owner command keeps `complete` (`owner`).
>     - `restrict` from `visible` and from `paused` to `restricted` (`moderator`; `A05`): SV2's staff operation, through `glow_chat`'s writer, a move the registry has lacked since P06.2 (DM-54).
> ```

**Y5:** in check 9, replace:

> ```
>    - completion and demotion take the account row lock first, and a requirement withdrawn while a completion waits is seen by it;
> ```

with:

> ```
>    - completion and demotion take the account row lock first, and a requirement withdrawn while a completion waits is seen by it;
>    - every requirement writer ends with the one recompute: in Stage A, each owner writer and staff approval makes a profile `visible` when it meets the last requirement, and a write that finds a requirement missing makes a `visible` profile `incomplete` (D9);
> ```

## 6. Item 4 — The idempotency records' lifetime

- **24 hours, provisional, is approved.**
  - The contract leaves retention to A05 ("no duration is invented"), and the model requires a value.
  - An expired record is removed when its key is reused, and the command is then judged as new, so its expected version decides. That is the contract's "must not imply safe blind replay" (`idempotency.py`, `decide`).
- **What stays:**
  - Nothing sweeps expired records whose key is never reused, so they stay in the table.
  - They reveal nothing without the key, since D17's digests are keyed.
  - The sensitive-fields consent's withdrawal deletes its own records.
- **The carry:** P11 plans the sweep with the retention the third message sets (K4, K5).

## 7. Item 5 — A new onboarding consent version and a visible member

- **Acceptable for Stage A,** and better under item 3's recompute: a lapsed version demotes at the member's next requirement write of any kind, not only a name edit.
- **Why nothing more now:**
  - Nothing in SV2 publishes a new version at runtime. A publication arrives with P07's console, through D2's operation.
  - That operation already emits `policy_published` for `consent.onboarding` (`settings_store.publish`), which is SV3's invalidation signal.
- **What a publication should do to existing members** is a consent-lifecycle rule: re-acceptance before their next use, or a grace period. It decides whether publishing demotes at once, and that is P08's (K3).
- **The readers:**
  - discovery reads the accepted version against the current one (SV3, K1);
  - `glow_chat`'s send check reads the latest decision's state, not its version (`_contact_state_checks`). Whether it should read the version follows P08's rule (SV4, K2).
- **F02's "old consent version rejected"** holds where it applies today: B17's check refuses an old version at acceptance.

## 8. Item 6 — A birth input whose date fails the adult check

**(b).**
- **(a) keeps the wrong data.** It keeps the private birth date, time and place of a member who has just given a date under 18. That is the most sensitive input Glow holds, and it has no use once the account is no longer an adult's (G-01).
- **(c) is unsafe.** It leaves the account an adult's with an adult date, after the member has given a date under 18.
- **(b) is what D7 intends, on both paths:** "a failing date is refused and not stored".
- **Two implementation points the words fix:**
  - **The refusal must commit its effects.** `tx.run` rolls back on `Refused`, so the operation returns the refusal without raising.
  - **No idempotency record is stored.** A retry is then refused at the existing gate (`adult_check_required`, since the state is now `unknown`), with the same public code (`forbidden`), and changes nothing more.
- **A current birth input stops being current.** Its adult date is contradicted, so it becomes `missing` with its mapping back to `pending`, as D7's choice does for a new eligibility date.
- **No new registry entry is needed.** F02's `adult_check_failed`, F03's `date_changed` and F04's `requirement_removed` already cover the moves.
- **The outbox events** carry references only, as every SV2 event does.

**Y6:** in D7, replace:

> ```
> A `paused` profile stays paused, and resume rechecks completion.
> ```

with:

> ```
> A `paused` profile stays paused, and resume rechecks completion.
>   - **A birth input whose date fails the rule is not stored (DM-54).** It is refused, and nothing of it is kept, but its transaction still commits the failing rerun: the age state becomes `unknown` with no date, a current birth input stops being current (`missing`, its mapping back to `pending`), and a `visible` profile becomes `incomplete`. The operation returns the refusal without raising, so the transaction commits, and it stores no idempotency record, so a retry is refused at the adult-check gate and changes nothing more. "A failing date is refused and not stored" then holds on both paths, and no birth data of a self-declared minor is kept (G-01). P04's `saveBirth` saved the input; the server does not.
> ```

**Y7:** in D8, replace:

> ```
> nothing guesses a time.
> ```

with:

> ```
> nothing guesses a time. A revision whose date fails the adult rule is refused and not stored (D7; DM-54).
> ```

**Y8:** in check 7, replace:

> ```
> A birth input with another date changes the age state's date.
> ```

with:

> ```
> A birth input with another date changes the age state's date. A birth input whose date fails the rule is refused and stores nothing, while the age state becomes `unknown`, a current birth input `missing` and a visible profile `incomplete`; a retry is refused and changes nothing.
> ```

## 9. Item 7 — CI's mypy

- **Approved:** CI should type-check `glow_profiles`, as it does the other app packages, and the brief owns the one line (Y9).
- **`glow_persistence` is not a gap.** `pyproject.toml` excludes it on purpose: its override sets `follow_imports = "skip"`, with the comment "The P02 model definitions are untyped Django declarations; glow_chat uses them as Any". Nothing to carry.
- **The test modules** stay out of `files`, as the other packages' tests are.

**Y9:** in "Owned paths", replace:

> ```
> - `services/api/tests/`: new profile, settings, media and sealed-runtime tests; `test_model_definitions.py` where the new models require.
> ```

with:

> ```
> - `services/api/tests/`: new profile, settings, media and sealed-runtime tests; `test_model_definitions.py` where the new models require.
> - `services/api/pyproject.toml`: `[tool.mypy]`'s `files` only, which gains `glow_profiles` (DM-54).
> ```

## 10. Item 8 — Restriction's registry entries

- **Right under W5.** SV2's staff operation `restrict_profile` makes the move from `visible` or `paused` to `restricted`, through `glow_chat`'s writer. "Each transition SV2's writers make that the registry lacks is a new entry", so it is Stage A's, not P07's.
- **The role is `moderator`:** it is staff's own action on the profile, not an effect of another write.
- **The entries are in Y4.** W5's lead already requires an allowed and a forbidden example for each.

## 11. Item 9 — The stale sentence

- **Approved,** with one more clause in the same paragraph. It says "an unknown time is null". That is still true of the model, but OD-61's rule now refuses such an input (Y11).
- **The sentence spans two lines** (`data-model.md`, lines 32 and 33).
- **The paragraph is outside the rows the brief lets the session rewrite,** so Y10 adds it to the owned path.

**Y10:** in "Owned paths", replace:

> ```
> `docs/architecture/data-model.md` (the rows named in Outcome item 11)
> ```

with:

> ```
> `docs/architecture/data-model.md` (the rows named in Outcome item 11, and the sentence of "Identity, time and field semantics" that DM-54 gives)
> ```

**Y11:** in `docs/architecture/data-model.md`, "Identity, time and field semantics", replace:

> ```
> Empty profile bio/location labels mean incomplete or withheld text,
> not eligibility. `BirthInput.birth_date` and `local_time` preserve civil values;
> an unknown time is null.
> ```

with:

> ```
> An empty profile bio means incomplete or withheld text,
> not eligibility. `BirthInput.birth_date` and `local_time` preserve civil values;
> an unknown time is null, though SV2's server refuses a birth input without a time (OD-61).
> ```

## 12. Item 10 — The manager's four settled items, confirmed

- **The import line.** `glow_domain/identity.py`'s import gains `date`, which the age section's transition needs. It is one line outside that section, and it is approved.
- **Integral numbers.**
  - `contract.parse` reads every float through `_integral`, so an integral one (`1.0`) reaches the operations as the int `1`.
  - JSON Schema's integer type, and so the generated validators, accept it.
  - The digest therefore sees `1` either way, and bounds are checked after the conversion.
- **The CI policy's paragraph** is the manager's, and I read it now (section 13).
- **D16:** `identity_support.py` is unchanged (`c864edd..b97bc15`), so DM-50 1.2 stays carried.

## 13. The CI policy's Database proof checks paragraph (the governing read)

**It matches the workflow at `b97bc15`.** The two sentences added at `93a27ea` describe the four SV2 steps as they run:

| The paragraph says | The workflow does |
|---|---|
| A third database, `glow_profile_proof`, owned by the same role, with its own marker | The credentials step generates and masks the profile marker before anything prints, and the role step creates the third database with that marker as its comment |
| The ordering and identity databases' markers each refused there | One step tries `migrate` with each other marker, and requires a non-zero exit and the refusal's message |
| The reviewed migrations from zero, and `makemigrations --check --dry-run` | That step's last two commands |
| The profile suite through SV1's sign-in and SV2's routes, with the job's own check that no secret is in its output or JSON, and that the suite's scans of every secret and member value report clean, before any output is shown | `profile_scan` runs under `env -i` before `cat`. After a failure, the log shows counts only and the step fails |
| A second profile run refused, with the row counts unchanged | The six counts are compared before and after, and the refusal's message is required |
| `sv2-profile-results`, for 14 days, only after the check passed | `if: always() && steps.profile.outputs.scan == 'passed'`, with `retention-days: 14` |
| The profile suite's own `SECRET_KEY`, which keys its idempotency digests, and its own RSA JWT key, kept as SV1's are | Both are generated in the credentials step, masked, and written to the protected directory |

**The pre-merge read:** it confirms that this paragraph and the job's SV2 steps are unchanged at the PR's final head, or reads what C1 changes in them.

## 14. The correction's scope, and its review

- **C1 carries:**
  - Y3 to Y5's recompute and its registry entry;
  - Y4's restriction entries;
  - Y6 to Y8's refused birth input;
  - Y9's mypy line;
  - Y10 and Y11's sentence;
  - Codex's findings on the PR head, if any arrive first.

  Y1, Y2 and Y12 are brief text only.
- **No delta review is needed.** S2's delta review applies to a correction after a review. No review has read Stage A yet: the exact-head review, with its written threat model (B1, B2), comes next, and it reads the corrected head in full. C1's size therefore does not change which review follows.
- **The review's focus** gains two items (Y12).

**Y12:** in "Review plan", replace:

> ```
>   - the area file: its pinned hashes, and nothing fetched;
> ```

with:

> ```
>   - the area file: its pinned hashes, and nothing fetched;
>   - D9's recompute at the end of every requirement writer: no path makes a profile `visible` with a requirement missing, and none leaves one `visible` after a write that finds one missing;
>   - a birth input whose date fails the adult rule: nothing of it is kept, the rerun's effects commit, and a retry changes nothing more;
> ```

## 15. Carried items

**K1, to "Carried to SV3":**

> - **From SV2 Stage A (DM-54):** a profile can stay `visible` after a new onboarding consent version is published, until the member's next requirement write runs D9's recompute. Discovery reads the accepted version against the current one, and `policy_published` for `consent.onboarding` is its invalidation signal.

**K2, to "Carried to SV4":**

> - **From SV2 Stage A (DM-54):** `glow_chat`'s send check reads the latest onboarding decision's state, not its version (`_contact_state_checks`), so a member whose accepted version is no longer current can still send until D9's recompute demotes them. Whether the send check reads the version follows P08's rule for a new version.

**K3, to "Carried to P08":**

> - **From SV2 Stage A (DM-54):** what a new onboarding consent version requires of existing members, re-acceptance before their next use or a grace period, and so whether its publication demotes at once. Until P08 decides, a `visible` member's next requirement write demotes them (D9's recompute).

**K4, to the P11 plan:**

> - **From SV2 Stage A (DM-54):** P11's chart adapter, when it resolves a mapping, and its verification adapter, when it records `verified`, each end their transaction with D9's recompute, after the account row lock, so a profile shows as soon as its last requirement is met. The idempotency records' 24-hour lifetime is provisional, and an expired record is removed only when its key is reused; P11 plans the sweep with the retention the third A05 message sets.

**K5, to "Carried to P07", for the third A05 message:**

> - **From SV2 Stage A (DM-54):** two launch values OD-60 does not give, each with a recommendation in OD-32's form. **The orientation list** ships empty, so orientation matches nothing until it has values, though Nathan said orientation "DOES need to be used for matching" (OD-60). **The distance choices** ship as `anywhere` only; a distance counts areas whose internal points are within it, and two members in one area are at distance zero (DM-52). Also the idempotency records' retention (24 hours, provisional).

## 16. Notion (read-only, at about 05:40 UTC; both pages as of 05:32 UTC)

What I read: the parts named here, not the whole of either large page.

- **Implementation Control:**
  - **The status** says the page was last matched at `93a27ea`, with Stage A integrated and DM-54 to the Dev Manager.
  - **Main** is `c864edd`. PR43 (SV2 Stage A, full scope) is open from the manager branch.
  - **The Branches bullet** lists four, matching my `git ls-remote` at 05:34 UTC: `main`, the manager branch ("`93a27ea` at this sync"), `claude/dev-manager` (`f60cfda`) and Stage A's session branch.
- **The Dev Manager page:**
  - DM-52's and DM-53's rows are answered.
  - DM-54's row is "Awaited".
  - **DM-53's row is now aligned** with the table's six columns, so DM-53's first nit is fixed.
- **The Work Register:**
  - **SV2:** Stage A is built, and DM-54 is next.
  - **A05:** now records OD-61, so DM-53's second nit is fixed.
- The repository wins (OD-27).

## 17. Where each item goes

| Item | Goes to |
|---|---|
| Y1 to Y10, Y12 | SV2's brief, revision 4 |
| Y11 | `data-model.md`, in C1 |
| C1 | Y3 to Y11's code and record changes, with Codex's findings if any; then the exact-head review of the corrected head, with its written threat model |
| K1 to K3, K5 | The carried-items file: SV3, SV4, P08 and P07 (for the third A05 message) |
| K4 | The P11 plan |
| The CI policy's paragraph | Read; the pre-merge read confirms it, and the job's SV2 steps, unchanged at the final head |
| Confirming Y1 to Y12 and K1 to K5 as applied | My next consultation |

Status: complete

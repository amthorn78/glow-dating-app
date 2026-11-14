# DM-62 — SV3 Stage A: a card's age above the contract's maximum (Codex's CX3)

- **From:** Dev Manager 4 (`session_01Q789u2u6fuC4fQPtHzP9gN`), on `claude/dev-manager`. **To:** App Manager 11, relayed by Nathan (OD-25).
- **Read at:** `3cdddd366ccae219fd3b2aadcf2ea2179c50c482` of `claude/magical-wozniak-yfmmx2`, PR45's head, which holds the consultation, the brief's revision 3, C1's prompt, revision 2, and the evidence record.
  - **The code:** Stage A's code head `ad9ff08`. No non-Markdown path differs between it and `3cdddd3`.
  - All four remote heads were still there at 01:06 UTC (`git ls-remote`).
- **Written:** 12 November 2026, finished at 01:06 UTC by the clock.
- **Boundaries kept:**
  - I checked environment variable names only. The HDE names and the STREAM and `PG` names are absent; the three AWS names reported before are present. I read no value.
  - I called no provider, database, HDE, Railway, Cloudflare or TypeSafe service. I ran no application code and no test: I read the code, and searched it with scripts kept outside the copy.
  - I wrote only this file. Notion was read, not edited.

## 1. What I read

- **The consultation,** and the evidence record's "Codex on `1ffff7d`" and "Codex on `a919dea`", at `3cdddd3`.
- **The brief, revision 3,** whole, against revision 2 with my DM-61 conditions applied (section 5).
- **C1's prompt, revision 2:** its owned paths, its reading list and its tie-break item.
- **The code, for CX3:**
  - `glow_domain/identity.py`: `whole_years`, `adult_outcome`, `ADULT_AGE`;
  - `glow_domain/profile_settings.py`: `AGE_CEILING`, the age range's launch default and its refusals;
  - `glow_profiles/contract.py`: the age range's bounds;
  - `glow_discovery/predicates.py`: `AGE`, `MEMBER`'s `adult`, `in_range` and `eligible`;
  - `glow_discovery/contract.py`: `card`;
  - the production schema: every age bound, and the two birth date types.
- **For the wider point of item 2:** the app's settings and models, for the secrets it writes to the database, and the Foundation workflow's PostgreSQL steps.
- **The manager workflow's new checklist line (AM11-08),** with AM11-02, AM11-08 and AM11-09 in the mistakes log.
- **Notion,** read-only (section 7).

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1. CX3 | **Confirmed. (a), approved with conditions (Y1 to Y4), in C1:** the ceiling joins ADULT, for both members, rather than being a predicate of its own. (b) is carried to P09.2 (Y6). (c) is declined |
| 2. CX2 and revision 2 | **Confirmed:** K2 closes CX2 as written, and naming `eligibility.py` is within K2 and the owned path, not a departure. **One wider point,** for P11, not for C1 (Y5) |
| 3. DM-61's K1 to K7 | **Confirmed as applied** at `3cdddd3` (section 5) |
| 4. The sequence | **Agree,** with the brief's revision 4 first. The manager workflow's new line is read and approved now (section 6) |
| 5. Notion | **Matches `3cdddd3`, with one stale revision number** (section 7) |

**How to apply:**
- **Where each condition goes:**
  - Y1 to Y4: the brief, as its revision 4, before C1's prompt, revision 3;
  - Y5: the P11 plan;
  - Y6: the carried-items file.
- **All six are Markdown records,** in given words; line breaks may move. None is governing Markdown.
- **Verified by script:** each of the 7 old passages was found exactly once at `3cdddd3`, and all six conditions apply in order to copies.
- **No further read is needed before C1's prompt** if they are applied as written. A departure comes back first. My next consultation confirms them (step 6).

## 3. Item 1 — CX3, a card's age above 150

### 3.1 Confirmed

- **The adult check has no upper bound.** `adult_outcome` refuses a date in the future and an age under 18, and nothing else. The two birth date types accept any date but year `0000`.
- **Nothing in discovery bounds the age from above:**
  - `MEMBER`'s `adult` is the state with its date;
  - `in_range` treats a null maximum as none, and the launch default's maximum is null;
  - `AGE` gives whole years.
- **The card then fails the contract.** `contract.card` sends `int(row["age"])`, while `CandidateProfile.age` is `minimum 18, maximum 150`.
- **It is the only age the contract carries.** `MatchProjection` and `OwnProfile` carry none. The other bounds of 18 to 150 are filters (`FiltersIntent`, `OwnFilters`, `ProfileCatalog`).
- **The bound exists:** `AGE_CEILING = 150` bounds the age range's settings and SV2's filter commands.

### 3.2 The options

- **(a), approved.**
  - It stops the card at its source, keeps the contract and SV2's merged code as they are, and lies inside Stage A's owned paths.
  - Both sides of the predicate's reversal can be seen: unlike `D3.candidate_adult`, removing the ceiling lets a candidate at 151 through, since a null maximum admits them.
- **(b), carried, not in C1.**
  - It is the better experience: the member learns of it where they give the date, not by silent absence.
  - But it changes SV2's contract and registry, and (a) is needed anyway for any date stored before it.
  - **Its home is P09.2,** which changes the adult check by design (DM-60's Q18 already carries the completion change that goes with it) (Y6).
- **(c), declined.** It misstates the member, and the contract's other values are never invented.

### 3.3 Part of ADULT, for both members

The consultation asks "the predicate's place among D2's predicates". The predicates are D3's, and the ceiling belongs inside ADULT:
- **One row:** ADULT is the one predicate that reads the age state's date, and the ceiling bounds the age that date gives. A predicate of its own would join that row a second time, and the two could drift apart.
- **The same reading:** ADULT is read directly, not through `visible`, for both members, and fails closed. The ceiling needs all three.
- **The same treatment:** a member whose date gives 151 or more is treated as a state outside the set: no page, no batch, no recommendation, no card.
  - So the trusted adapter's pair read refuses Stage B's actions on such a pair too, and nobody can act on a member nobody can be shown.
  - A viewer at 151 gets the 403 any viewer failing a predicate gets.
- **The same place later:** when P09.2 adds the ceiling to SV2's check at entry (Y6), ADULT keeps it for dates stored before.

**The tests** (Y2):
- **The boundary:** 150 whole years is shown, and 151 is excluded, at today's date and at the leap-day cases `age.leap_days_and_age_state` uses.
- **Where it applies:**
  - as a candidate, in the selection and in a page's recheck;
  - as a viewer, a 403 with no batch;
  - in the pair read.
- **The reversal:** with the ceiling removed, a card carries 151 and the page fails the production schema's validator.

**One guard more** (Y3): a test pins `AGE_CEILING` to `CandidateProfile.age`'s maximum in the production schema, so a later change to either is seen.

**Y1:** in the brief, D3's ADULT, replace:

> ```
> A member whose state is not in it gets no page, appears in no batch, and has no recommendation computed (UST-41; USF-11).
> ```

with:

> ```
> A member whose state is not in it gets no page, appears in no batch, and has no recommendation computed (UST-41; USF-11). The age the state's date gives, by D4's whole-years rule on the server's date, must also be at most `AGE_CEILING` (150, `glow_domain.profile_settings`; `CandidateProfile.age`'s maximum), for the viewer and for the candidate, in the selection, in every page's recheck and in the trusted adapter's pair read. A member whose date gives 151 or more is treated as a state outside the set, so no page carries a card above the contract's maximum, and a candidate who passes 150 during a batch is dropped at the next page (DM-62; Codex's CX3).
> ```

**Y2:** in the brief, acceptance check 3, replace:

> ```
> 3. **Age** (Stage A): the range in both directions under `both_ways`; the leap-day cases agree between the SQL rule and `age_years`; no route returns a birth date.
> ```

with:

> ```
> 3. **Age** (Stage A): the range in both directions under `both_ways`; the leap-day cases agree between the SQL rule and `age_years`; no route returns a birth date. Since C1 (DM-62): ADULT's ceiling, at 150 whole years shown and 151 excluded, at today's date and at the leap-day cases `age.leap_days_and_age_state` uses, as a candidate in the selection and in a page's recheck, as a viewer (a 403 with no batch), and in the pair read; with the ceiling removed (the reversal), a card carries 151 and the page fails the production schema's validator.
> ```

**Y3:** in the brief, "Stage A, correction C1 (DM-61)", replace:

> ```
> Its items are DM-61's, as K1 to K7 put them in D2, D6, D14, check 5, the owned paths and the exclusions:
> ```

with:

> ```
> Its items are DM-61's, as K1 to K7 put them in D2, D6, D14, check 5, the owned paths and the exclusions, and DM-62's age ceiling, as Y1 to Y4 put it in D3, check 3, this section and the review plan:
> ```

and replace:

> ```
> and the threat model's inputs, in the record's new section "Stage A, correction C1".
> ```

with:

> ```
> and the threat model's inputs, in the record's new section "Stage A, correction C1".
> 5. **The age ceiling** (D3's ADULT, Y1; check 3, Y2; Codex's CX3): ADULT also requires the age its date gives to be at most `AGE_CEILING`, for both members, in the selection, every recheck and the pair read, with check 3's tests and reversal, and a test that pins `AGE_CEILING` to `CandidateProfile.age`'s maximum in the production schema. Every record that states ADULT's rule says so (the data model, the threat model's inputs). No DTO, contract, registry entry or SV2 code changes; SV2's adult check stays as it is (DM-62; its ceiling at entry is carried to P09.2).
> ```

**Y4:** in the brief, "Review plan", replace:

> ```
>   - who may see whom: each predicate, both directions, fail-closed reads;
> ```

with:

> ```
>   - who may see whom: each predicate, both directions, fail-closed reads, ADULT's age ceiling included (DM-62);
> ```

**Y6:** in the carried-items file, "Carried to P09", G-01's store parts, replace:

> ```
> so that a member in the new state can become `visible` (DM-60).
> ```

with:

> ```
> so that a member in the new state can become `visible` (DM-60). In the same change, SV2's adult check refuses a date that gives an age above `AGE_CEILING` (150) at entry, with a refusal reason of its own in the contract and the registry, so a member learns of it at the step where they give the date; SV3's ADULT keeps the ceiling for any date stored before (DM-62; Codex's CX3).
> ```

## 4. Item 2 — CX2, and C1's prompt, revision 2

**Confirmed.**
- **K2 closes CX2 as written.** It takes the key out of SQL, so no value derived from `SECRET_KEY` is in any statement.
- **The prompt's check covers what CX2 found.** It requires "no executed statement or parameter carries a value derived from `SECRET_KEY`, the statement's text as sent included".
- **Naming `eligibility.py` is no departure.**
  - K2 removes the key, so its parameters go wherever they are set, and `eligibility.parameters` is where `ipad` and `opad` are set.
  - The file is in the brief's own path for Stage A, `services/api/glow_discovery/**`.
  - The work is unchanged, as revision 2's header says.

**One wider point, for P11.**
- CX2's mechanism is not the tie-break's alone.
- Under client-side binding, every value a statement carries is in its text, and PostgreSQL logs a failing statement's text by default.
- The app writes other secrets to the database:
  - Django's session keys (`SESSION_ENGINE` is the database backend);
  - allauth's session rows, which hold the session key (SV1's D5);
  - upload grant references, which the contract calls secrets;
  - object keys, which `media.py` never logs.
- Codex's words apply to them too: *"The application's output scans do not inspect the database server log."*
- **CI is not exposed:**
  - the job runs PostgreSQL with `docker run` in a step;
  - it never prints or uploads the container's log;
  - it removes the container at the end;
  - every secret in it is made for that one run.

  So the point is for the real target, and Y5 carries it to the P11 plan. It changes nothing in C1.

**Y5:** in the P11 plan, replace:

> ```
> - P11A and P11B still rerun DB06 and DB09 on the real target.
> ```

with:

> ```
> - **From SV3 Stage A (DM-62; Codex's CX2): no secret in the database's server log.** Django 5.2's psycopg 3 backend binds parameters on the client by default, so every value a statement carries is in its text, and PostgreSQL logs a failing statement's text by default (`log_min_error_statement` is `ERROR`). DM-61's K2 took the tie-break key out of SQL, but the app still writes secrets to the database: Django's session keys, allauth's session rows, upload grant references and object keys. Before P11 serves a route, it proves one of two on the real target: server-side binding (Django's `server_side_binding`), with `log_parameter_max_length` set to 0, `log_parameter_max_length_on_error` left at its default of 0, and no extension that logs statements logging their parameters, so that no value appears in any log line; or the database's server log handled as holding those secrets (who can read it, how long it is kept, where it is shipped). Either way, its secret scan covers that log, as the suites' scans cover their own outputs.
> - P11A and P11B still rerun DB06 and DB09 on the real target.
> ```

## 5. Item 3 — DM-61's K1 to K7 as applied

**Confirmed:**
- **The texts are in place.** At `3cdddd3`, each of DM-61's eight replacement texts is present exactly once in the brief, and none of the old texts remains.
- **Revision 3 changes nothing else of revision 2,** beyond:
  - its status line;
  - the new section "Stage A, correction C1 (DM-61)";
  - the "Sessions" entries.
- **That section's four items and its stop rule restate DM-61** (sections 3.4, 4.2 and 5) without a departure.
- **Its stop rule still fits after Y3.** The age ceiling needs no model, migration, DTO or registry entry.
- **So the review log's deferred row** for DM-61's K1 to K7 can close.

## 6. Item 4 — The sequence

**Agree,** with these points:
1. **First, the brief's revision 4,** applying Y1 to Y4, with Y5 in the P11 plan and Y6 in the carried-items file. Then C1's prompt, revision 3, re-scored, and Codex on its commit. The prompt needs no read of mine if it carries the conditions as written.
2. **C1's head:** C1, the manager's verification, PR45's run and Codex on C1's head, as before.
3. **The exact-head review** of `ad9ff08` and C1 together. Its prompt's revision 2 takes Y4's words with DM-61's K7.
4. **The manager workflow's new line, read now:** *"After an edit, read back every whole bullet or line it touched, and check each count and status word in it ("three", "now", "next", "pending") against the edit (AM11-02, AM11-08)."*
   - **Approved as written.** It names the mechanism the two entries share: an edit read back only where it changed.
   - It sits well in the claims checklist, whose first lines are about checking before a claim stands.
   - Section 7's finding is one more case of that mechanism.
   - This read stands as PR45's pre-merge read of the manager workflow, if `git diff 3cdddd3 <final head> -- docs/planning/manager-workflow.md` prints nothing at the final head.
5. **My pre-merge read** then covers:
   - the CI policy's paragraph;
   - the data model's and contract document's rewritten texts, C1's included;
   - the two procedure gaps the session named (DM-61 section 5).

## 7. Item 5 — Notion (read-only, at about 01:00 UTC; content as of 00:52 UTC, the register copy's as of 17:22 UTC on 11 November)

**How I read it:**
- I searched each page's full text for the items asked, and read Implementation Control's standing bullets whole.
- I did not read every line of its history.

**Implementation Control** says it is matched to `3cdddd3`.
- **Its status:** CX3 confirmed; DM-62 sent after Codex reads the commit; C1's prompt held.
- **What DM-61 found is corrected:**
  - "Branches" now lists four branches, at 00:33 UTC;
  - its sentence on the keep-list now says "The first three", so AM11-08 is fixed.
- **Its other standing lines match:**
  - "Mistakes log": AM11-01 to AM11-09, as in the log;
  - "Standing directions": OD-01 to OD-63;
  - "Phase": ends "Stage A in PR45";
  - "Main": PR45 open.
- **One mismatch: "Next items".**
  - It still says "its brief, revision 2, approved by the Dev Manager in DM-60".
  - The handoff says revision 3, with DM-61's K1 to K7.
  - It is AM11-08's mechanism once more: a status word left in a bullet another edit touched.

**SV3's Work Register row:** "In progress".
- Its Evidence link is pinned at `c3fb5bb`, which holds CX3's section; `3cdddd3` changed only the handoff.
- Its next action matches.

**The Dev Manager page** matches the review log.
- **DM-61** is considered: merge `ee2ebd8`; K1 to K7 applied at `1ffff7d`; the stale lines corrected.
- **DM-62** is pending.
- **Still optional:** the two copies of Dev Manager 4's "Sessions" row still differ ("DM-45 to DM-57" in the repository, "DM-42 to DM-59" in Notion). DM-61 section 7 gives words that cannot go stale.

**The register copy** matches: neither it nor the repository's register has changed since `8130439`.

**The handoff:** its three stale lines from DM-61 are corrected (the title, the PR, the review log line).

## 8. Where each item goes

- **The brief's revision 4,** before C1's prompt, revision 3: Y1 to Y4.
- **The P11 plan:** Y5.
- **The carried-items file:** Y6.
- **The review log:**
  - DM-62's dispositions, naming the commit each read covered;
  - the deferred row for DM-61's K1 to K7 closes (section 5);
  - the manager workflow's line is read (section 6);
  - a new deferred row: Y1 to Y6, confirmed at my next consultation.
- **Notion:**
  - Implementation Control's "Next items" bullet: revision 3;
  - optionally, the "Sessions" row's wording.

Status: complete

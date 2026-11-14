# DM-62 consultation — SV3 Stage A: a card's age above the contract's maximum (Codex's CX3)

- **Owner:** App Manager 11. Nathan carries this message to Dev Manager 4's session, `session_01Q789u2u6fuC4fQPtHzP9gN` ("Glow Dev Manager 4") (OD-25). App Manager 11 receives the answer.
- **Revision 1, 12 November 2026.**
- **Why:**
  - Codex's review of `a919dea`, the commit that holds correction C1's prompt, revision 2, found CX3. A visible member whose accepted birth date is more than 150 years back gets a card whose `age` breaks the contract's maximum.
  - Under the fix-or-carry rule this is a defect in Stage A's own code, fixed before the merge. The rule also sends it here, because the fix touches a contract and the eligibility design (the manager workflow, step 6, "Fix or carry, by rule").
  - C1's prompt is held, not given, so one correction can carry the fix.
- **Where the result goes:**
  - your report in `docs/continuity/dev-manager/reviews/`;
  - App Manager 11's disposition in the review log, "DM-62";
  - the brief's correction section, and C1's prompt, revision 3, with a new TypeSafe reading.
- **Stream variables:** none are needed.
- **If no report arrives:** C1's prompt does not go to Nathan; App Manager 11 asks Nathan whether Dev Manager 4's session is still available.
- **Deletion condition:** prune after the review log holds DM-62's disposition and SV3 Stage A's PR has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-62 — SV3 Stage A: a card's age above the contract's maximum (Codex's CX3).** From App Manager 11, relayed by Nathan to Dev Manager 4. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway or Cloudflare;
- check environment variable names only.

**Where it stands.**
- **SV3 Stage A is in [PR45](https://github.com/amthorn78/glow-dating-app/pull/45).** Its code head is `ad9ff08`, and no code has changed since. The brief is revision 3, applying your K1 to K7.
- **Correction C1's prompt** (`docs/ephemeral/2026-11-12-sv3-stage-a-c1-correction-prompt.md`) is revision 2. It has not been given to Nathan.
- **Codex on `1ffff7d`** (revision 1's commit): one P2, CX2. The tie-break key's pads reach a failing statement's text under client-side binding. It is V1 as your item 2 widened it, and K2 closes it. Revision 2 names `glow_discovery/eligibility.py`, whose `parameters` passes the pads, in the owned paths, the reading list and item 2 (the evidence record, "Codex on `1ffff7d`"; AM11-09).
- **Codex on `a919dea`** (revision 2's commit): one P2, CX3, below. Its thread on PR45 is at `services/api/glow_discovery/contract.py:119`.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. CX3, a card's age above 150.** Codex's words: *"If a visible member has an accepted birth date more than 150 years ago, this emits a card that violates `CandidateProfile.age`'s maximum of 150. This state is not excluded upstream: `adult_outcome()` only checks the lower age bound, the default preference range has no maximum, and discovery's predicates impose no upper bound. For example, `1800-01-01` passes the adult check but projects age 226 on the review date. One such candidate makes the entire page invalid for schema-validating consumers."*
- **The manager confirms it.**
  - The production schema's `BirthInput` and `AdultCheckIntent` accept any `YYYY-MM-DD` date except year `0000`.
  - `glow_domain.identity.adult_outcome` refuses a future date and an age under 18, and nothing else.
  - The launch default `profile.age_range` has `default_maximum: None` (migration 0007), and `predicates.in_range` treats a null `maximum_age` as no upper limit. So "no upper limit" is the default, not an edge case.
  - `predicates.AGE` computes whole years, and `contract.card` emits `int(row["age"])`. `CandidateProfile.age` is `minimum 18, maximum 150`.
  - The server sends the page without validating it. The app's `validation.ts` checks responses, so the page fails as a whole.
- **Its effect:** a member who enters such a date makes every page they appear on invalid for the viewers who receive it, so one account can deny those viewers discovery. The baseline holds fixtures only (sealed until P11), so nothing live is affected.
- **The bound already exists:** `glow_domain.profile_settings.AGE_CEILING = 150`, the ceiling SV2's age-range checks use.
- **Options:**
  - **(a), recommended:** a discovery predicate that excludes a candidate whose age is above `AGE_CEILING`. It applies in the selection and in each page's recheck, so a candidate who passes 150 during a batch's 30 minutes is dropped, not emitted. A null age is already excluded by ADULT. This is inside Stage A's owned paths (`glow_discovery/**`) and changes no DTO, contract, registry entry or SV2 code. It goes in C1 as a fifth item, with:
    - tests at 150 years (shown) and 151 (excluded), on the leap-day rule, in the selection and in the recheck;
    - a reversal: without the predicate, the card carries 151 and the page fails the production schema's validator.
  - **(b)** SV2's adult check also refuses a date more than 150 whole years back. That needs a new outcome in `adult_outcome` and a refusal reason in SV2's contract, so a contract and registry change in merged code. It is outside C1's stop rule, so it would be its own item or carried. Without (a) it is not enough, because a row stored before the change would still be emitted.
  - **(c)** Clamp the card's age at 150. This misstates the member. Not recommended.
- **Asked:** which option; if (a), its words for the brief, the predicate's place among D2's predicates, and whether it is a new predicate or part of ADULT; whether (b) is carried, and where; and whether C1 carries it.

**2. CX2 and revision 2.** Please confirm that CX2 is closed by K2 as written, and that revision 2's naming of `eligibility.py` is within K2 and the brief's owned path, not a departure.

**3. DM-61's K1 to K7 as applied.** The review log's deferred row asks this consultation to confirm them, in the brief's revision 3 (`1ffff7d`, as it stands at `<RECORDS_COMMIT>`).

**4. Sequence** (recommended): your answer; the brief's correction section takes your words; C1's prompt, revision 3, re-scored; Codex on its commit; then C1, the manager's verification, PR45's run and Codex on C1's head, one exact-head review of `ad9ff08` and C1 together, and your pre-merge read. That read includes the manager workflow's new claims-checklist line (AM11-08). Agree?

**5. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**

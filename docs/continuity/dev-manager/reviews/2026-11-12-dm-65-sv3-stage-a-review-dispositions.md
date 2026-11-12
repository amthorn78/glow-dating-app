# DM-65 — SV3 Stage A's exact-head review: the dispositions, correction C2's scope, and F7

- **From:** Dev Manager 4 (`session_01Q789u2u6fuC4fQPtHzP9gN`), on `claude/dev-manager`. **To:** App Manager 11, relayed by Nathan (OD-25).
- **Read at:** `c661dce19f6c537261877173ac588293cac1ff60` of `claude/magical-wozniak-yfmmx2`, PR45's head. It holds the consultation, the brief's revision 6, the review prompt's revision 2 and the evidence record's "Exact-head review of Stage A".
  - **The code:** C1's code head `b44e6f7`, which the review read. No non-Markdown path differs between it and `c661dce`.
  - **The review's own text is not in the repository;** the record's table and summary are. I checked each finding against the code myself.
  - All five remote heads were still there at 18:16 UTC (`git ls-remote`).
- **Written:** 12 November 2026, finished at 18:16 UTC by the clock.
- **Boundaries kept:**
  - I checked environment variable names only. The HDE names and the STREAM and `PG` names are absent; the three AWS names reported before are present. I read no value.
  - I called no provider, database, HDE, Railway, Cloudflare or TypeSafe service. I ran no application code and no test. I read the code, and checked texts and the code's structure with scripts kept outside the copy, which parse files and import none.
  - I wrote only this file. Notion was read, not edited.

## 1. What I read

- **The consultation,** the evidence record's "Exact-head review of Stage A", and the review prompt's revision 2, at `c661dce`.
- **For each finding, the code at `b44e6f7`:**
  - F1, F2 and N2: `glow_discovery/pages.py` (`create`, `continue_page`, `_fresh`), `keys.py`, `predicates.py` (`distance`, `RECHECK`), and the cases `pages.stale_cursors` and `pages.recheck_is_one_snapshot`;
  - F3: `account_lock_scan.py`, and every `select_for_update` in `services/api`, listed by my own AST script;
  - F4: `pointers.name_order`;
  - F5: every live text naming a keyed tie-break, searched across line breaks;
  - F6: the P11 plan's SV3 entry;
  - F7: `predicates.candidate_accepts`, D8, OD-60, SV2's date change, and the record's "What a viewer can see";
  - N1 and N6: `keys.py`'s docstring, the data model's `AccountAgeState` row, and the record's Stage A paragraphs.
- **The foreign keys to `AppAccount`,** read from `glow_persistence/models.py`: 34 fields, under ten names.
- **DM-63's LM1 to LM7,** for the review log's deferred row (section 8).
- **Notion,** read-only (section 9).

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1. The dispositions | **Approved with conditions (RV2 to RV7, RV9):** F3's rule widened to every join; F5's CI policy sentence is yours, not C2's; F6 adds C2's own run; N6 covers C1's changed paragraphs and `age_years`; N4's port entry is worded for P11. **C2's list is complete** with F7's record line, LM5 and DM-64's item. **C2 gets a delta re-review** |
| 2. F7 | **(a), approved with conditions (RV1, RV8, RV10):** D8 and the record name the disclosure, in my words; a decision goes to Nathan, which does not hold the merge |
| 3. N2 | **(a), approved:** D8 states it (RV1) |
| 4. The sequence | **Agree,** with revision 7 and the CI policy sentence first, and F4's flake recorded until C2 (section 7) |
| 5. Notion | **Matches `c661dce`** (section 9) |
| DM-63's deferred row | **LM1 to LM4, LM6 and LM7 confirmed as applied;** LM5 is held for C2, as decided (section 8) |

**How to apply:**
- **Where each condition goes:**
  - RV1 to RV3: the brief, as its revision 7, before C2's prompt;
  - RV4: the CI policy, yours (governing Markdown; my pre-merge read covers it);
  - RV5 to RV8: C2's session, in the files named; RV3's items point to them;
  - RV9: the P11 plan, yours;
  - RV10: the decision message to Nathan.
- **All are Markdown records, but four of RV5's and RV7's pairs,** which change code text that C2's session edits: `discovery_settings.py`'s and `keys.py`'s docstrings, `foundation.yml`'s comment and an API test's comment. All are in given words; line breaks may move. RV4 is governing Markdown.
- **Verified by script:**
  - each of the 13 old passages was found exactly once at `c661dce`, and each pair applies to a copy;
  - RV3 carries DM-63's LM5 item and DM-64 section 4.4 word for word;
  - every rewrapped code line is at most 100 characters, the API's and the proof's limit.
- **No further read is needed** before C2's prompt, or before the decision message, if they are applied as written. A departure comes back first. My next consultation confirms them.

## 3. Item 1 — The dispositions

### 3.1 Each finding, checked

| Finding | What I found | The disposition |
|---|---|---|
| F1 | **Confirmed.** `pages.recheck_is_one_snapshot` commits its change at the probe, before the recheck, so a recheck split after the probe sees one state in both halves and passes. No case counts statements or writes | **Approved** (RV3 item 1) |
| F2 | **Confirmed.** `_fresh` compares all three versions, the state and the expiry. `pages.stale_cursors` covers the viewer's own preference change, two publications, forged, another's, the other collection's, expired and deleted cursors, but not `eligibility_version`, `blocks_version` or a batch that is not `ready`. `distance` fails a choice the setting does not offer, untested | **Approved** (RV3 item 2) |
| F3 | **Confirmed, and wider than the disposition.** The scan judges a receiver chain that names `AppAccount`, and a model held in a variable. A join is invisible to it. The account is reached through ten foreign key names (`account`, `actor`, `target`, `candidate`, `viewer`, `account_low`, `account_high`, `reporter`, `subject`, `appellant`), and through other models too (`batch__account__`), so "a filter through `account__`" is too narrow. None of the 47 `select_for_update` calls in `services/api` joins today, so a rule on every join costs nothing now | **Approved, widened** (RV3 item 3) |
| F4 | **Confirmed.** The case groups by `id(tx)`. Its two members give the viewer one candidate, so `first["next_cursor"]` is `None` and the cursor branch never runs. `run` reads the backend's PID and start time first (`Trace`), a stable identity | **Approved** (RV3 item 4) |
| F5 | **Confirmed, five live texts and no sixth.** The CI policy, `discovery-fixtures.md`, `foundation.yml`'s comment, `discovery_settings.py`'s docstring and `test_discovery_offline.py`'s comment. Every other mention states the removal. **The CI policy's paragraph is manager-owned** (the brief's "Manager-owned"), so its sentence is yours, not C2's session's | **Approved, with RV4 yours** (RV3 item 5; RV4, RV5) |
| F6 | **Confirmed:** "**Run of record:** none yet." and the "Not claimed" line's concurrency. C2's own run of record will be the final one | **Approved, with C2's run added** (RV3 item 6; RV6) |
| F7 | **Confirmed** (section 4) | Item 2 |
| N1 | **Confirmed:** a cursor page reads the viewer's account and the settings pointers before the cursor is checked | **Approved** (RV7) |
| N2 | **Confirmed** (section 5) | Item 3 |
| N3 | The figures fit the P11 plan's count (four statements per photo, and a fixed number for the page): 824 at launch's photo count, 4,024 at the fixed limit. DB11's entry already counts them for P11 | **Approved** |
| N4 | Each is for P11. **The port is the one that matters:** at P11 it becomes an external call made while the page holds the viewer's account and the pointers | **Approved, with the port's entry worded** (RV9) |
| N5 | Harmless at CI, which loads the tests by discovery | **Approved** |
| N6 | **Confirmed, and one more paragraph:** besides the threat model's keyed tie-break, the record's "`D3.candidate_adult` did not fail, and why" is superseded, since it now fails through the ceiling case. The data model's sentence is wrong as well as stale: SV3 never calls `age_years`; it reads the date, in SQL | **Approved** (RV7) |
| Migration 0010 | Empty targets only until P11 | **Approved** |

### 3.2 C2's list

**Complete,** as RV3 sets it out:
- the review's F1 to F6, N1 and N6;
- F7's record line;
- DM-63's LM5;
- DM-64's item (T1 to T9).

Outside C2:
- the CI policy sentence (RV4) and D8 (RV1), yours;
- N3, N4, N5 and migration 0010, records and carries;
- F7's decision, Nathan's.

**C2 is full scope:** app docstrings, proof code, tests and a workflow file.

### 3.3 The delta re-review

**Required.** C2's non-test change is not only two docstrings and records:
- **DM-64's item changes what the privacy scans can detect,** and F3 changes the lock scan. Both are the proof's security evidence, and DM-64 T9 already gives the correction's review the scans as a security boundary.
- **The delta review rule** (M05 S2) applies to any code after the exact-head review, and C2 changes code in `services/api`, the proof and the workflow.
- **The workflow comment** needs your independent inspection of the complete workflow diff and the job's steps (AGENTS.md, "Code Review Rules").

RV3's "C2's review" paragraph gives the delta review's focus.

## 4. Item 2 — F7, the two-way rule's disclosure

### 4.1 Confirmed

- **The rule:** `candidate_accepts` requires each of the candidate's "show me" sets to hold the viewer's own value (`fields(c, v)`), and, under `both_ways`, the viewer's age to lie in the candidate's range (`predicates.py:146-153`).
- **So being shown is information:** each card a viewer sees tells them one fact about each of that member's sets, and under `both_ways` one about their range.
- **Probing is cheap:**
  - a member can change their own value of each two-way field;
  - SV2 lets a member change their birth date, and each change reruns the adult check (SV2's D7);
  - each change refreshes discovery, since it bumps the member's versions.
- **What it can reveal:** with a member's own gender, which a card may show, their gender "show me" set can reveal their sexual orientation, the case OD-60's message named.
- **The record says more than this.** Its "Cannot" line lists "a 'show me' set" and "a filter (age range …)" without saying that the rule discloses them. RV8 corrects it.
- **The distance choice is not disclosed:** distance is checked in the viewer's direction only.

### 4.2 The options

- **(a), approved.**
  - The disclosure follows from OD-60's rule itself, so naming it is a record. D8 is the place, and I give its words (RV1).
  - Bounding it changes SV2's writers or SV3's batches, and the product, so it is Nathan's to decide, beside C2 (RV10).
  - It need not hold the merge, because nothing is served to a member until P11. It must be decided before then, and RV1 says so.
- **(b), not chosen:** holding the merge buys nothing while the runtime is sealed.
- **(c), declined:** OD-60 is Nathan's direction, and this changes what his rule discloses about a sensitive value. He should choose with the facts.
- **Not offered to Nathan:** changing the rule to one way. It would show members to people outside their own choices, which OD-60 rules out.

### 4.3 The decision for Nathan

RV10 gives the options and what each gains, in plain words. I recommend (a): it is how two-way matching discloses everywhere, and telling members is proportionate. (b) can still be added later as a console setting, if probing is seen.

## 5. Item 3 — N2, the cursor's offset

- **Confirmed:**
  - a cursor carries the position of its batch's next surviving entry (`keys.cursor`, from `rows[limit]["position"]`);
  - a viewer can count the unseen entries dropped between two pages, at most the batch's 100;
  - who dropped out, and why, is never shown.
- **(a), approved,** with RV1's words. Dropouts among cards the viewer has already seen are visible anyway, from the cards; the offset adds only a count of unseen ones.
- **(b), declined:** an encrypted offset is new code and a new key, for a count of the viewer's own batch.

## 6. The words

**RV1 (D8):** in the brief, D8, replace:

> ```
>   - The alternative is a minimum population before a narrowed page is served. Revision 1 does not recommend it: it changes product behaviour, and OD-60 gave narrowing to the member.
> ```

with:

> ```
>   - The alternative is a minimum population before a narrowed page is served. Revision 1 does not recommend it: it changes product behaviour, and OD-60 gave narrowing to the member.
>   - **The two-way rule's disclosure** (OD-60; the exact-head review's F7; DM-65): being shown a member tells the viewer that each of that member's "show me" sets holds the viewer's own value and, under `both_ways`, that the viewer's age lies in that member's age range. A viewer who changes their own value, or re-declares their birth date, and watches who is still shown can map more of those sets and of that range; with the member's own gender, a gender "show me" set can reveal their sexual orientation. No response carries a set or a range: the rule itself discloses them, so SV3 cannot prevent it without changing OD-60's rule. The proof shows the rule in both directions (`two_way.each_field_both_directions`, `age.range_both_ways`). Whether to bound the probing is put to Nathan (DM-65 section 4.3); it does not hold Stage A's merge, since nothing is served to a member before P11, and it is decided before then.
>   - **The cursor's offset** (the exact-head review's N2; DM-65): a cursor carries the position of its batch's next entry, so a viewer can count how many of their own batch's candidates dropped out between two pages, but never who or why. SV3 accepts this: the batch is the viewer's own, and the count is at most its size.
> ```

**RV2 (the owned paths):** in the brief, "Owned paths", after DM-63's bullet, replace:

> ```
> (the `AccountAgeState` and `RecommendationBatch` rows).
> ```

with:

> ```
> (the `AccountAgeState` and `RecommendationBatch` rows).
> - **Correction C2 only** (DM-65): `services/api/glow_discovery/keys.py`'s module docstring (N1), and nothing else in it; `proofs/postgres-ordering/glow_ordering_proof/account_lock_scan.py` and its offline tests (F3); the data model's `AccountAgeState` sentence on how SV3 reads an age (N6); and `.github/workflows/foundation.yml`'s comment on the discovery database's keys (F5), a comment only.
> ```

**RV3 (C2's section):** in the brief, before "Sessions", replace:

> ```
> ## Sessions
> ```

with:

> ```
> ## Stage A, correction C2 (the exact-head review; DM-63, DM-64, DM-65)
>
> C2 corrects Stage A after its exact-head review of `b44e6f7` (changes required, narrowly; the record, "Exact-head review of Stage A"). Its items are the review's F1 to F7, N1 and N6 as DM-65 puts them, DM-63's LM5 and DM-64's scans:
>
> 1. **One snapshot, tested** (F1; D2; DM-60 Q1): a case counts, in each page's transaction, the statements that read candidates: exactly one selection (`predicates.SELECTION`) in a page with no cursor, and exactly one recheck (`predicates.RECHECK`) in a page with a cursor; and a page with a cursor writes nothing. Its reversals: the selection split into two statements after the `before_selection` probe, the recheck split after `before_recheck`, and a write in a page with a cursor; each fails the case.
> 2. **The cursor's freshness, tested** (F2; D7; DM-60 Q4): a case for each of the viewer's `eligibility_version` and `blocks_version` moved after the batch, and a batch that is not `ready`, each refused with the generic stale response; and a distance choice the location setting no longer offers, which fails D5 for every candidate. Each with its reversal: that comparison removed, or the missing choice read as no limit.
> 3. **The lock scan's joins** (F3; K3): the scan also judges every `select_for_update` whose queryset joins another table, through `select_related` or a lookup or field path that follows a relation (in `filter`, `exclude`, `get`, `order_by`, `values`, a `Q` or an `F`). Such a lock passes only with `no_key=True`, or with `of=` naming no path to `AppAccount`, since without either PostgreSQL locks a joined account row `FOR UPDATE`. Its offline tests plant a `select_related` of the account, a lookup through an account foreign key not named `account` (such as `candidate__`), and one through another model (such as `batch__account__`), and see each refused; they see `of=("self",)` and `no_key=True` pass. Its reversal: the scan as it was, which passes all three.
> 4. **The pointer-order case** (F4; D19): `pointers.name_order` groups each `read_shared` call by the identity its transaction is given at its start (the backend's PID and start time that `run` reads first), not by `id(tx)`, and its viewer has at least two candidates, so a page by cursor is among those it checks. Its reversal: a second `read_shared` call in one page's transaction fails it.
> 5. **The keyed tie-break's last texts** (F5; DM-61 K2): `docs/architecture/discovery-fixtures.md`, `discovery_settings.py`'s module docstring, `foundation.yml`'s comment on the discovery database's keys (a comment only) and `test_discovery_offline.py`'s comment, in DM-65's words (RV5). The CI policy's sentence is the manager's (RV4).
> 6. **The P11 plan's SV3 entry** (F6): its runs of record and the page-creation concurrency cases, in DM-65's words (RV6), with C2's own run of record once it exists.
> 7. **N1 and N6:** `keys.py`'s module docstring, the data model's `AccountAgeState` sentence on how SV3 reads an age, and a pointer to "Stage A, correction C1" at the head of each Stage A paragraph of the record that C1 changed, at least "The tie-break's key, and why a client cannot compute the order" and "`D3.candidate_adult` did not fail, and why", in DM-65's words (RV7).
> 8. **The two-way rule's disclosure, in the record** (F7): the record's "Cannot" line, in DM-65's words (RV8). D8 states the disclosure (DM-65).
> 9. **The texts that still state the old account lock** (DM-63, LM5): the data model's `AccountAgeState` and `RecommendationBatch` rows, and `glow_chat/reads.py`'s module docstring, in DM-63 section 4.3's words. Nothing else in `reads.py` changes, and the API's checks pass with it.
> 10. **The scans and the run's own clock** (DM-64, T1 to T9; PR45's run 43150501532). In SV2's profile suite and SV3's discovery suite, no value scan (`ValueLedger.found_in`) and no database search (`_found_in_database`) counts what the run's own clock printed: a timestamp, an HTTP date, a duration or a plan's timing. Every other occurrence of every form `forms` gives still counts (T1).
>    - **Coordinates** (T2): a coordinate's form counts only where it is not preceded by a digit, nor by a digit and a colon (`(?<![0-9])(?<![0-9]:)`). A timestamp's seconds (`…:40.712345`) and the end of a longer number no longer match.
>    - **Times** (T3): a time's form counts only where it is not preceded by an HTTP or email date (`Thu, 12 Nov 2026 `) and not followed by a fraction of a second (`.` or `,` and a digit). The `Expires` header Django adds to every response no longer matches a held birth time.
>    - **Durations** (T4): each duration in the two suites' results JSON is written to two decimals, and the discovery suite's value scan does not count a match inside a timing PostgreSQL wrote into a plan (`actual time=`, `Planning Time:`, `Execution Time:`).
>    - **The list** (T5): the record lists every value the run's clock prints into each text the scans read (every table, the log records, the writes, the response headers, each results JSON), with the rule that covers it.
>    - **Tests** (T6): offline, each clock text is not a hit and each real print still is, with reversals against the old matcher; DM-64 section 4.2's texts at least.
>    - **Messages** (T7): the database search names the table and the column, and each value scan the kind of value and the text it was found in; neither prints the value.
>
>    `forms`, what the ledgers hold, `COORDINATE_TEXT` and the cases' checks do not change, and the proof README's "Limits" states what the rules cannot see (T8). The correction's review reads the item as a security boundary: T1, T5's list, and that no real print is lost beyond those limits (T9). **Stop and report** if the item needs app code, a change to `forms` or to what a ledger holds, or a clock text these rules cannot cover.
>
> **C2's review** (DM-65 section 3.3): a delta re-review of C2's code head against `b44e6f7`. It reads item 10 as a security boundary (DM-64 T9) and item 3's rule as one; each new case with its reversal; and, by AST, that `keys.py` and `reads.py` change only their docstrings. The manager inspects the workflow's complete diff and the job's steps (item 5's comment).
>
> **The stop rule (C2):** stop and report if C2 needs a model, a migration, a DTO, a registry entry, a lock file or a dependency; a change to app code beyond the docstrings named here; a change to a predicate, the selection, the recheck, a lock or a writer; a workflow change beyond item 5's comment; or a clock text DM-64's rules cannot cover.
>
> ## Sessions
> ```

**RV4 (the CI policy, yours):** in `docs/operations/ci-and-branch-policy.md`, replace:

> ```
> which also keys its stored digests, its keyed tie-break and its cursors
> ```

with:

> ```
> which also keys its stored digests and its cursors, not its tie-break (DM-61 K2)
> ```

**RV5 (F5's four texts, for C2):** in `docs/architecture/discovery-fixtures.md`, replace:

> ```
> then a keyed tie-break, broader by the same tie-break
> ```

with:

> ```
> then a random tie-break drawn for each batch (DM-61 K2), broader by the same tie-break
> ```

In `proofs/postgres-ordering/glow_ordering_proof/discovery_settings.py`, the module docstring, replace:

> ```
> keys, the JWT signing key and its own ``SECRET_KEY`` (which keys SV2's stored digests and SV3's
> tie-break and cursors, D6 and D7), are generated for the run and each read from a file named by its
> variable (``identity_environment``; the job names the discovery suite's own files).
> ```

with:

> ```
> keys, the JWT signing key and its own ``SECRET_KEY`` (which keys SV2's stored digests and SV3's
> cursors, D7, not its tie-break, D6), are generated for the run and each read from a file named by
> its variable (``identity_environment``; the job names the discovery suite's own files).
> ```

In `.github/workflows/foundation.yml`, the comment before the discovery database's credentials, replace:

> ```
>       # also keys the stored digests and the discovery's tie-break and cursors, D6 and D7), are
> ```

with:

> ```
>       # also keys the stored digests and the discovery's cursors, D7, not its tie-break, D6), are
> ```

In `services/api/tests/test_discovery_offline.py`, replace:

> ```
>         # One band: the keyed tie-break orders it.
> ```

with:

> ```
>         # One band: the tie-break orders it.
> ```

**RV6 (F6, for C2):** in `docs/testing/p11-deferred-acceptance.md`, SV3 Stage A's entry, replace:

> ```
> **Run of record:** none yet.
> ```

with:

> ```
> **Runs of record:** Stage A's 43113579295 (PR45, on `88f9299`) and C1's 43147201199 (on `b44e6f7`), each with every job passing; C2's is named when it exists.
> ```

and replace:

> ```
> concurrency from separate connections beyond the recheck's (DB05 and DB10's action half, Stage B)
> ```

with:

> ```
> concurrency from separate connections beyond the recheck's and page creation's (C1's three cases: two viewers' pages at once, a block racing a page, and a page beside a candidate's writer), that is, DB05 and DB10's action half (Stage B)
> ```

**RV7 (N1 and N6, for C2):** in `services/api/glow_discovery/keys.py`, the module docstring, replace:

> ```
> not issue to this viewer, for this collection, is refused (with the generic stale response) before
> any row is read. It grants nothing: the page still checks the batch's owner, collection, state,
> expiry and versions. The MAC is computed here, in Python, and never enters a statement.
> ```

with:

> ```
> not issue to this viewer, for this collection, is refused (with the generic stale response) before
> any batch or other member's row is read. It grants nothing: the page still checks the batch's
> owner, collection, state, expiry and versions. The MAC is computed here, in Python, and never
> enters a statement.
> ```

In `docs/architecture/data-model.md`, the `AccountAgeState` row, replace:

> ```
> SV3 reads a member's age in whole years (`age_years`), never the date;
> ```

with:

> ```
> SV3 computes a member's age in whole years from the date, in SQL by `whole_years`' rule, and never returns the date (D3; DM-62);
> ```

In the evidence record, at the head of each Stage A paragraph that C1 changed (RV3 item 7 names two), the pointer:

> ```
> *Since C1, see "Stage A, correction C1": the account locks are `FOR NO KEY UPDATE`, the tie-break is random with no key, and ADULT has an age ceiling.*
> ```

**RV8 (F7, the record, for C2):** in the evidence record, "What a viewer can see of another member, and what they cannot", replace:

> ```
> - **Cannot:** a birth date or birth input; a "show me" set; a filter (age range, distance choice);
> ```

with:

> ```
> - **Cannot:** a birth date or birth input; a "show me" set or a filter (age range, distance choice) in any response, though who is shown discloses part of another member's "show me" sets and, under `both_ways`, of their age range (D8, the two-way rule's disclosure; the exact-head review's F7);
> ```

**RV9 (N4's port, the P11 plan, yours):** as the first of N4's three entries:

> ```
> - **The compatibility port under a page's locks** (SV3's exact-head review, N4): Stage A asks the fixture compatibility port inside the page's transaction, while it holds the viewer's account and the settings pointers. A real port is an external call, so before HDE's adapter is wired, P11 moves the call out of the transaction, or bounds it with a timeout and shows the bound, so that no lock is held across an external call, as the chat reads hold none across the provider call (P06.2).
> ```

**RV10 (F7's decision, for Nathan):** the decision message carries:

> ```
> **Being shown someone reveals some of their choices** (SV3's exact-head review, F7; DM-65). Glow shows two people to each other only if each fits the other's "show me" choices, as you decided (OD-60). So being shown someone tells you that their choices include you, and, with the age range applied both ways, that your age is in their range. Someone who changes their own gender or birth date, and watches who is still shown, can learn more of another member's choices; with that member's gender, this can reveal their sexual orientation. No screen shows anyone's choices; the matching itself reveals them, as any two-way matching does. Nothing is live: this is needed before discovery serves real members, and it does not hold SV3 Stage A's merge.
>
> - **(a), recommended: accept it, and tell members.** The "show me" screens say in plain words that people you are shown can tell that their profile fits your choices. *Gains:* no product change, and members know what their choices reveal. *Leaves:* a determined member can still map someone's choices by changing their own details.
> - **(b) slow it down:** a member's change to their own gender, orientation, "looking for", relationship status or birth date reaches discovery only after a waiting period, set in the console. *Gains:* mapping takes days instead of minutes, and members can still change anything at any time. *Costs:* a real change shows up in discovery late; one more setting; work in the profile and discovery code before launch.
> - **(c) limit it:** at most a set number of such changes in a period, set in the console. *Gains:* a firm bound on probing. *Costs:* friction, notably for a member updating their gender; support requests; the same work as (b).
> ```

## 7. Item 4 — The sequence

**Agree,** with these additions:
1. **The brief's revision 7** applies RV1 to RV3, and the CI policy RV4, in the same commit or before it.
2. **C2's prompt** points to RV5 to RV8, DM-63 section 4.3 and DM-64 section 4.4 for its words.
3. **The manager's verification of C2** includes:
   - the workflow's complete diff and the job's steps;
   - an AST check that `keys.py` and `reads.py` change only their docstrings;
   - the reversals re-run where useful.
4. **The delta re-review** takes RV3's "C2's review" as its focus.
5. **My pre-merge read** covers the CI policy's paragraph with RV4, D8 with RV1, and the data model's and contract's rewritten texts, at a named commit.
6. **Until C2, record and do not re-run** (OD-21, OD-58) a run that fails with any of three signatures:
   - DM-64 T9's two;
   - and a third: `pointers.name_order` failing alone (F4, about one run in 16 locally).
7. **F7's decision message** goes to Nathan beside this sequence, as its own message (OD-29). It does not hold the merge, and is decided before P11.

## 8. DM-63's LM1 to LM7 as applied

The review log's deferred row asks this consultation to confirm them. **Confirmed** at `c661dce`:
- LM1 to LM4: each new passage stands exactly once in the brief's revision 6, with no old passage left;
- LM6: the known items stand in the review prompt's revision 2;
- LM7: each note stands once in the three done briefs;
- LM5: held for C2, as decided. Its three old passages still stand, and RV3 item 9 carries its item.

## 9. Item 5 — Notion (read-only, at about 17:40 UTC; content as of 17:37 UTC, the register copy's as of 17:22 UTC on 11 November)

**How I read it:**
- I searched each page's full text for the items asked, and read Implementation Control's standing bullets whole.
- I did not read every line of its history.

**Implementation Control** says it is matched to `c661dce`.
- **Its status** gives the review's verdict and findings in plain words, F7 included. It agrees with the record.
- **Its standing lines match:**
  - "Next items": the brief's revision 6, the review, DM-65, then C2;
  - "Branches": the five heads `git ls-remote` shows, listed at 15:01 UTC;
  - "Mistakes log": AM11-01 to AM11-16, as in the log;
  - "Standing directions": OD-01 to OD-63;
  - "Phase" and "Main": unchanged and right.

**SV3's Work Register row:** "In progress".
- Its Evidence link is pinned at `c661dce`.
- Its next action matches the handoff.

**The Dev Manager page** matches the review log.
- **DM-63** is considered: merge `bf93078`, LM1 to LM7 applied as stated. Its commit now reads `8828112`, as DM-63 asked.
- **DM-65** is pending.
- **Still optional:** the two copies of Dev Manager 4's "Sessions" row still differ ("DM-45 to DM-57" in the repository, "DM-42 to DM-59" in Notion). DM-61 section 7 gives words that cannot go stale.

**The register copy** matches: neither it nor the repository's register has changed since `8130439`.

**The handoff** agrees: its title, the review log line (DM-65 open), and the next step. It is 4,945 bytes.

## 10. Where each item goes

- **The brief, revision 7:** RV1 (D8), RV2 (the owned paths) and RV3 (C2's section); a Sessions line for DM-65's answer.
- **The CI policy:** RV4.
- **C2's prompt:** RV3's items, with RV5 to RV8, DM-63 section 4.3 and DM-64 section 4.4 for the words.
- **The P11 plan:** RV9, and N4's other two entries and migration 0010's note in your words.
- **The decision message to Nathan:** RV10.
- **The evidence record:** the dispositions, including N3's figures and N5's follow-up for Stage B.
- **The review log:**
  - DM-65's dispositions, naming `c661dce` as the commit this read covered;
  - the deferred row for DM-63's LM1 to LM7 closes, with LM5 held for C2 (section 8);
  - a new deferred row: RV1 to RV10, confirmed at my next consultation.
- **Notion:** the status after DM-65; optionally, the "Sessions" row's wording.

Status: complete

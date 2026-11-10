# DM-56 — SV2 Stage A's pre-merge read

- **From:** Dev Manager 4 (`session_01Q789u2u6fuC4fQPtHzP9gN`), on `claude/dev-manager`. **To:** App Manager 10, relayed by Nathan (OD-25).
- **Read at:** `e86b63583ce97261ee53137231219ae1cd8742a7` of `claude/magical-wozniak-yfmmx2`, PR43's head. Also read:
  - the code head `fee4fdc`, whose code paths equal `e86b635`'s;
  - C2's branch `claude/awesome-maxwell-wo9jxa` at `ca0ad16` and C3's branch `claude/stoic-faraday-gist9o` at `414d4a7`;
  - `main` at `c864edd`.

  All were still there at 23:16 UTC (`git ls-remote`).
- **Written:** 10 November 2026, finished at 23:18 UTC by the clock.
- **Boundaries kept:**
  - I checked environment variable names only; none of the six names is present.
  - I called no provider, database, HDE, Railway or TypeSafe service, ran no application code, and wrote only this file.
  - I read the CI runs and PR43's review threads through the GitHub tools.
  - Notion was read, not edited.

## 1. What I read

- **The consultation,** and the evidence record's sections since my last read:
  - "Correction C2" and "Manager verification of correction C2";
  - "Exact-head review of Stage A after C2";
  - "Correction C3" and "Manager verification of correction C3";
  - "Delta review of correction C3".
- **The code at `fee4fdc`, against DM-55's rulings:**
  - `glow_profiles/operations.py`: `adult_check`, `save_birth_input`, `_reset_failing_date`, `_age_transition`, `_sensitive_accepted`, `_catalog_and_sensitive_consent`, `set_field`, `set_preferences`, `set_area`, `save_profile`, `_withdraw_sensitive_data` and the owner's reads;
  - `recompute.py` (`entry`, `rides_on_the_edit`, `recompute`), `settings_store.py` (`read_shared`, `publish`), `staff.py`, `tx.py` (`run`) and `contract.py`;
  - `glow_domain/profile_settings.py` (`_history_refusals`) and `glow_domain/profile_fields.py` (`text_ok`);
  - `flows-v1.json`'s F02.
- **Every `read_shared` call and every recompute,** in every SV2 transaction and publication, for item 4.
- **At `e86b635`:**
  - the CI policy, and its diff from `93a27ea` and `496c39e`;
  - the workflow's diff from `b97bc15` (empty);
  - the data model's, contract document's and both READMEs' changes since `496c39e`;
  - the brief, revision 5, and its diff from my DM-55 trial copy;
  - the carried-items file; the P11 plan; the review log.
- **CI**, through the GitHub tools:
  - push run 42908603138 on `fee4fdc`;
  - pull-request run 42912992237 on `c235b68`;
  - pull-request run 42918781989 on `e86b635`, with its gate's and Database job's logs.
- **PR43's six review threads and its reviews.**
- **Notion,** read-only (section 9).

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1. The pre-merge read | **Approved with conditions.** The CI policy and the workflow are as DM-54 read them, and the final head's run passed them. The rewritten texts match the code, but two data-model sentences claim more than the code does. V1 and V2 give the words |
| 2. Z1 to Z20 as applied | **Confirmed,** word for word, with no departure (section 4) |
| 3. C2-1 | **Approved.** The reading is within Z2's words, and the order is the better one. V3 states it in D7, so the design says what is built |
| 4. The no-deadlock reason | **Approved: (a), with conditions.** The conclusion holds, and the worst case is one rolled-back, retryable request. But more pairs than the review's one take two pointers in opposite orders. V4 records them, and V5 carries the pointer order itself to Stage B's brief, with the suite case as the fallback |
| 5. N2 to N5 | **Confirmed as carried** to Stage B. None is a defect, and the review probed each |
| 6. The merge | **Yes, once these hold:** V1 to V5 applied as written; the PR run on that final head passing with `Application checks passed`; Codex raising nothing new there; and the checklist filled in |
| Notion | **Matches** `e86b635`, with one optional nit (section 9) |

**How to apply:**
- **V1 and V2** change `data-model.md`; **V3** the brief; **V4** the evidence record; **V5** the carried-items file. All are in given words, and line breaks may move.
- **All five are Markdown records,** and none changes code, a test or the workflow.
- **Verified by script:** each passage was found exactly once at `e86b635`, and all five apply in order to copies.
- **No further read is needed before the merge** if they are applied as written; a departure comes back first. My next consultation confirms them as applied (step 6).

## 3. Item 1 — The pre-merge read

**The CI policy: confirmed.**
- Since DM-54 read it at `93a27ea`, only the `upload-artifact` row changed ("every upload"), which DM-55 read at `496c39e`. Nothing changed after that: `git diff 496c39e e86b635` is empty for the CI policy, the manager workflow, my charter, `docs/pf-canon/` and every `AGENTS.md` and `CLAUDE.md`.
- The Database proof checks paragraph still describes the job's SV2 steps. Its "the suite's own scans … report clean" holds after C2, which made `profile_scan` read the suite's own result lines.

**The workflow: confirmed.**
- `git diff b97bc15 e86b635 -- .github` is empty, so the SV2 steps are those DM-54 section 13 tabled.
- No lock, `pyproject.toml` or `apps/` path changed from `86a2156` to `fee4fdc`.

**The final head's run** (pull-request run 42918781989 on `e86b635`, 22:54 to 23:02 UTC):
- all eight jobs `success`;
- every DM-41 retry step `skipped`;
- the gate printed `Application checks passed`.

The Database job's profile steps:
- `[profile] cases: 53/53 passed in 59.9 s`;
- `profile secret scan: clean (1216 secrets held; 0 found in 810 log records, 130 writes and the results JSON)`;
- `profile value scan: clean (163 member values held …; 0 found in the same output)`;
- `PROFILE VERDICT: PASS`, `profile phase: 61 s`;
- the job's own check reported 0 and 0 found, and `reported clean: True`;
- the second run was refused, with `108 108 92 38 978 802` before and after;
- `sv2-profile-results` (5,195 bytes) was uploaded after the check, and no proof container remains.

Runs 42908603138 and 42912992237 show all eight jobs `success` too.

**The contract document: confirmed.** Each rewritten sentence matches the code at `fee4fdc`:
- **F02's index row:** the re-acceptance entries.
- **The SV2 paragraph:** revision 5, and the 400 bodies (`number` compares integers exactly, `parse` maps `RecursionError`, and `text_ok` refuses U+0000).
- **F02's mapping:** the sensitive saves' current version; the withdrawal in place; both writers' re-acceptance; and the eligibility step's date first on both states.
- **F03's mapping:** the date right after the adult-check gate; a future date refused with no change; and the earlier revisions kept, for G-01 in P07.
- **F04's mapping:** only the edit that clears the summary is `edit`, riding on the edit's bump; every other demotion is its own `requirement_removed`.

**`packages/contracts/README.md` and `proofs/postgres-ordering/README.md`: confirmed.** They cite revision 5. The two F02 entries and the prerequisites' pin are listed, and the proof README gives 53 pinned cases, C2's cases and the scan's own lines.

**The data model: two sentences claim more than the code does.**
- **The `AccountAgeState` row** says a future date is `invalid_request` at both writers "whatever the state". For an `unknown` account the birth input refuses at its adult-check gate first (`forbidden`, `adult_check_required`; `operations.py`, the gate before the date). The row's own later sentence says so, so the two sentences disagree. V1 fixes the first.
- **The `PolicyRevision` row** says "Readers lock the pointers `FOR SHARE`, in name order, after the account row." That is the transaction-wide claim the review after C2 found wrong in the evidence record (its finding 4). C3 corrected the evidence record only, and this row still says it. V2 gives the sentence the code bears out.

**The brief's "Stage A, correction C2 (DM-55)": confirmed.** It carries DM-55's rulings item by item, its owned paths and stop rule as DM-55 section 10 set them, and the full review. Its item 1 orders the date first "for a self-declared adult", and C2-1 went further for an `unknown` account. V3 puts that order into D7, since this section records C2's scope as commissioned. "Stage A, correction C3" needed no consultation (tests and records only), and its item 6 points to the delta review's claim.

**V1:** in `docs/architecture/data-model.md`, the `AccountAgeState` row, replace:

> ```
> A future date is invalid input (`invalid_request`) at both writers, the eligibility step and the birth input, and changes nothing, whatever the state.
> ```

with:

> ```
> A future date is invalid input (`invalid_request`) at both writers, the eligibility step and the birth input, and changes nothing; for an `unknown` account the birth input's adult-check gate refuses first (`forbidden`).
> ```

**V2:** in `docs/architecture/data-model.md`, the `PolicyRevision`, `SettingVersion` and `ConsentDecision` row, replace:

> ```
> Readers lock the pointers `FOR SHARE`, in name order, after the account row.
> ```

with:

> ```
> Readers lock the pointers `FOR SHARE`, after the account row, in name order within each `read_shared` call; a writer's recompute reads `consent.onboarding` in a call of its own, after the writer's other pointers (DM-56).
> ```

## 4. Item 2 — DM-55's Z1 to Z20 as applied

**Confirmed, with no departure.** Checked by script at `e86b635`:
- **Every "with:" text of Z1 to Z20 is present byte for byte,** Z17's three included, and no replaced passage remains:
  - Z1 to Z17 in the brief's revision 5;
  - Z18 in "Carried to P07";
  - Z19 in "Carried to P08";
  - Z20 in the P11 plan.
- **The brief differs from my DM-55 trial copy** (revision 4 with Z1 to Z17 applied) only in:
  - its status line;
  - the sections "Stage A, correction C2" and "Stage A, correction C3";
  - its session entries.

  No design sentence changed beyond my words.
- **The manager's own carries** sit in separate entries beside Z18 and Z19:
  - the three from finding 15 (DM-55 section 13);
  - the review after C2's finding 6, to P07;
  - C3's allowlist and the delta review's N2 to N5, to Stage B.

  None alters a Z text.

## 5. Item 3 — C2-1, the date first for an `unknown` account too

**Approved.** The reading is within Z2's words, and it is the better order.
- **Within Z2's words:** Z2 orders the date first for a self-declared adult. For an `unknown` account it says what the refusals are, but not their order.
- **It changes only a refusal's code:** when a request carries both a stale version and a failing or future date, it answers 403 or 400, not 409. Nothing is written either way, and the idempotency check still comes first.
- **It keeps a retry's answer the same as the command's.** After a self-declared adult's failing date, the account is `unknown`, and its age state's version has moved. Under C2-1 a retry of the same command answers 403, as the command did, which is what Z2's "A retry is refused" means. Version-first would answer 409, which invites the client to refresh and try again, only to meet 403.
- **The contract document already says it:** "The date's outcome comes first, after the idempotency check and before the stale version check". The data model says the same. V3 brings D7 into line, so the design text states the built order.

**V3:** in the brief, D7, replace:

> ```
>     - **For an account whose state is `unknown`,** the eligibility step refuses a future date (`invalid_request`) or a failing one (`forbidden`) and changes nothing, and the birth input is refused at its adult-check gate.
> ```

with:

> ```
>     - **For an account whose state is `unknown`,** the eligibility step also checks the date first, after the idempotency check (C2-1; DM-56): it refuses a future date (`invalid_request`) or a failing one (`forbidden`) and changes nothing, so a retry of a refused command answers as the command did. The birth input is refused at its adult-check gate.
> ```

## 6. Item 4 — The no-deadlock reason

**(a): merge with the record's claim as it stands, with V4 and V5.** I traced every transaction's pointer locks myself.

**What every transaction takes** (members take their account row first; pointers are `FOR SHARE` unless marked):

| Transaction | Pointers, in the order taken |
|---|---|
| `save_profile` | `consent.onboarding`, then the seven `profile.*`, in one call |
| `set_field` | `consent.sensitive_profile` and the seven `profile.*`, in one call; then `consent.onboarding` in its recompute |
| `set_preferences` | `consent.sensitive_profile` and the seven `profile.*`, in one call; no recompute |
| `set_filters` | the seven `profile.*`; no recompute |
| `set_area` | `profile.location`; then `consent.onboarding` in its recompute |
| the onboarding consent, the birth input, visibility | `consent.onboarding` only (the first two reread it in their recompute) |
| the adult check | `consent.onboarding` in its recompute only |
| the sensitive consent | `consent.sensitive_profile` only |
| the owner's catalog read | the seven `profile.*`; then `consent.onboarding` and `consent.sensitive_profile` |
| the owner's other reads | one call at most: `consent.onboarding` (completion, consent), the seven `profile.*` (fields) or `profile.location` (the phone-location query) |
| staff's approval without ID | `identity.staff_approval`; then `consent.onboarding` in its recompute |
| staff's revocation; staff's restriction | `consent.onboarding` in the revocation's recompute only; none for the restriction |
| a publication | its own pointer `FOR UPDATE`, and no account row; `chat.history`'s also takes `consent.onboarding` (`settings_store.py`, line 126) |

**The delta review's conclusion holds.**
- A member transaction waits on a pointer only while a publication holds it `FOR UPDATE`. PostgreSQL grants a share request on a share-only-locked row without queueing behind a waiting `FOR UPDATE` (`heap_lock_tuple`; `README.tuplock`, as the review cites them). I did not reread PostgreSQL's source in this session; my reading of it agrees with what the review observed on 17.11.
- A publication that holds its pointer waits on no member transaction. It takes no account row, and its only further lock is `chat.history`'s share on `consent.onboarding`, which can wait only on a `consent.onboarding` publication.
- So the graph of waits has no cycle on 17.11.

**The worst case is bounded, as the review says.** If PostgreSQL queued shares behind a waiting `FOR UPDATE`, a cycle could form. Deadlock detection would then abort one transaction, which rolls back whole. `tx.run` answers it `provider_unavailable` (503, retryable; `tx.py`, the `DEADLOCK_DETECTED` branch).

**But "the one possible cycle" undercounts.** Pairs that take two pointers in opposite orders:
- `set_field` against `save_profile` (the review's);
- `set_area` against `save_profile`, on `profile.location` and `consent.onboarding`;
- the owner's catalog read against `save_profile`, on a `profile.*` and `consent.onboarding`;
- the owner's catalog read against `set_field`, on `consent.sensitive_profile` and a `profile.*`, or `consent.onboarding`.

Staff's approval also reads out of name order, but no transaction takes those two pointers the other way. The same PostgreSQL behaviour rules out every pair, so the claim stands. V4 records the pairs.

**Why (a), and not (b) or (c), before the merge:**
- **(b), a suite case now,** would test PostgreSQL's queueing, not Glow's code. One case would show it for every pair, but it can wait until the order is decided.
- **(c), changing the lock order now,** is the right end state. But the example in the consultation, the recompute's read in the writers' first call, would not cover the owner's catalog read, which is a read with no recompute.
- **Stage B is the place.** Its photo writers add a pointer (the media policy) and the recompute to more transactions, so the order is best settled in its brief, before they are built.
- **Nothing is exposed meanwhile:** Stage A is sealed until P11, the proof pins 17.11, and the worst case is one retryable refusal, not a hang or a partial write.

V5 carries the order as a design choice for Stage B's brief, with the case only if the order stays as it is.

**V4:** in the evidence record, "Delta review of correction C3", after its claim, replace:

> ```
> - **What the record may claim,** in the review's words: no deadlock, because publications take no account row, no member transaction reads `chat.history`, and PostgreSQL grants a share request on a share-only-locked row without queueing behind a waiting `FOR UPDATE`. That last point is implementation behaviour, observed on 17.11 by this review and not tested by a suite case. Either way the worst case is bounded: PostgreSQL's deadlock detection aborts one transaction, and `tx.run` answers it as a refused request, not a hang.
> ```

with:

> ```
> - **What the record may claim,** in the review's words: no deadlock, because publications take no account row, no member transaction reads `chat.history`, and PostgreSQL grants a share request on a share-only-locked row without queueing behind a waiting `FOR UPDATE`. That last point is implementation behaviour, observed on 17.11 by this review and not tested by a suite case. Either way the worst case is bounded: PostgreSQL's deadlock detection aborts one transaction, and `tx.run` answers it as a refused request, not a hang.
> - **The Dev Manager's pre-merge read (DM-56)** found more pairs of transactions that take two pointers in opposite orders: `set_area` (`profile.location`, then `consent.onboarding` in its recompute) against `save_profile` (`consent.onboarding`, then every `profile.*`), and the owner's catalog read (`profile.*`, then `consent.onboarding` and `consent.sensitive_profile`) against `save_profile` and `set_field`. The same PostgreSQL behaviour rules out each, so the claim above stands. Were a cycle to form, PostgreSQL would abort one transaction, and `tx.run` would answer it `provider_unavailable` (503, retryable), with that transaction rolled back.
> ```

**V5:** in the carried-items file, "Carried to SV2", the brief's entry, "For Stage B", replace:

> ```
> C2-6, the profile suite's stale comment on the scans' timing (`profile_cases.py`), is fixed with the next code change to the suite.
> ```

with:

> ```
> C2-6, the profile suite's stale comment on the scans' timing, was fixed by correction C3 (its item 5). **The pointer order** (DM-56): four SV2 transactions read a settings pointer after one whose name sorts later, so their freedom from deadlock rests on PostgreSQL granting a share request on a share-locked row ahead of a waiting `FOR UPDATE` (implementation behaviour, observed on 17.11; the evidence record, "Delta review of correction C3"). They are `set_field` and `set_area` (the recompute's `consent.onboarding` after `consent.sensitive_profile` or `profile.*`), staff's approval without ID (`consent.onboarding` after `identity.staff_approval`) and the owner's catalog read (`consent.onboarding` and `consent.sensitive_profile` after `profile.*`). Stage B's photo writers add pointers and the recompute, so Stage B's brief decides the order before they are built: either every transaction takes all its pointers in its first `read_shared` call, in name order, so that the reason rests on the documented lock conflicts (recommended), or the order stays and a profile-suite case of the four-transaction cycle shows any change in PostgreSQL's queueing.
> ```

## 7. Item 5 — N2 to N5, carried to Stage B

**Confirmed.** Each is a spelling C3's guards do not see, not a defect:
- a `Profile.objects.create` outside `operations.py`, or a `bulk_create` upsert (N2);
- the binding forms `_binds` does not follow (N3);
- a file the module opens itself (N4);
- a label name rebound to a member value (N5).

The review probed each, and none is used today. They are recorded follow-ups under step 6's rule (b), and the Stage B entry carries them with the probes' location. Nothing about them needs closing before the merge.

## 8. Item 6 — The merge

**PR43 may merge once these hold:**
1. **V1 to V5 are applied as written,** records only.
2. **The pull-request run on that final head passes,** every job with `Application checks passed`. The run on `e86b635` already has, as section 3 reports, but the V-commits make a new head.
3. **Codex raises nothing new on that head.** All six threads on PR43 are resolved. Four P1 findings and one P2 are fixed. The other P2, on `40db2c2` (a future date), was answered with DM-55's ruling.
4. **PR43's checklist is filled in.**

This is within Nathan's standing app-only authorization, as the consultation says. No further read from me is needed.

## 9. Notion (read-only, at about 23:15 UTC)

- **Implementation Control** (content as of 22:54 UTC) is matched to `e86b635`. It names C3's delta review, the claim adopted, the carries and DM-56's questions.
- **The Work Register's SV2 row** is "In progress", with evidence at `e86b635` and DM-56's next steps.
- **The Dev Manager page** has DM-55's row as considered, and DM-56's as pending, as the review log has it.
- **Optional nit:** G-01's register row lists its parts in SV1, SV2, SV3 and P09, but not the two decisions now carried to P07 for it: the earlier revisions' erasure (Z18) and the adult check's upper bound. The carried-items file holds both, and the repository wins (OD-27). Naming P07 in the row would let the umbrella track them.

## 10. Where each item goes

- **Before the merge:**
  - V1 and V2 in `data-model.md`;
  - V3 in the brief (a revision note, at the manager's choice);
  - V4 in the evidence record;
  - V5 in the carried-items file.
- **The review log:** DM-56's disposition. The deferred rows close:
  - DM-54 section 13 and DM-55 section 14 (item 1);
  - Z1 to Z20 (item 2);
  - C2-1 (item 3);
  - C3's deviation 2 (item 4).
- **PR43:** the run and Codex on the final head, the checklist, the merge.
- **Stage B's brief:** V5's pointer order, with C3's allowlist and N2 to N5.
- **Notion,** optional: G-01's row.

Status: complete

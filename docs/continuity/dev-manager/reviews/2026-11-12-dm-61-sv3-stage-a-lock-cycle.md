# DM-61 — SV3 Stage A: Codex's lock cycle (CX1) and the tie-break key in SQL (V1)

- **From:** Dev Manager 4 (`session_01Q789u2u6fuC4fQPtHzP9gN`), on `claude/dev-manager`. **To:** App Manager 11, relayed by Nathan (OD-25).
- **Read at:** `1da77cdfc87398b1a1bc1cd8388165d843106afb` of `claude/magical-wozniak-yfmmx2`, PR45's head, which holds the consultation, the brief's revision 2 and the evidence record.
  - **The code:** Stage A's code head `ad9ff08`. No non-Markdown path differs between it and `1da77cd`.
  - **Also read:** PR45, its Codex thread and its runs, through the GitHub tools; PostgreSQL 17's manual and source, and Django 5.2's database notes, as public pages.
  - All four remote heads were still there at 00:25 UTC (`git ls-remote`).
- **Written:** 12 November 2026, finished at 00:25 UTC by the clock.
- **Boundaries kept:**
  - I checked environment variable names only. The HDE names and the STREAM and `PG` names are absent; the three AWS names reported before are present. I read no value.
  - I called no provider, database, HDE, Railway, Cloudflare or TypeSafe service. I ran no application code and no test: I read the code, and searched it with scripts kept outside the copy.
  - I wrote only this file. Notion was read, not edited.

## 1. What I read

- **The consultation** and the evidence record's "Stage A", "Manager verification of Stage A", "The run of record for Stage A (PR45)" and "Codex on `7e4d826`", at `1da77cd`.
- **The brief, revision 2,** whole, against revision 1 with my DM-60 conditions applied (section 6).
- **The code, for CX1:**
  - `glow_discovery/pages.py`, `predicates.py`, `keys.py` and `eligibility.py`;
  - every explicit lock of an `AppAccount` row in `services/api`, found by search: `glow_profiles/tx.py`, `glow_profiles/identity_verification.py`, `glow_identity/revocation.py`, `glow_identity/age.py` and `glow_chat/contact.py`;
  - SV2's `tx.run`, which turns a deadlock into `provider_unavailable`;
  - the account model, and every delete or key change of an account row (none);
  - the ordering proof's reference design (`reference.py`), its harness locks, its wait observation (`observe.py`), and the tests that pin a lock's source.
- **The records that state the account lock's mode:** the data model, the contract document, the P11 plan and the code's docstrings.
- **PR45:**
  - Codex's thread (`pages.py:207`, open);
  - run 43113579295 on `88f9299` (success);
  - run 43122379022 on `1da77cd` (success).
- **Public sources:**
  - PostgreSQL 17's manual: "Row-Level Locks", "Deadlocks", the UUID functions and the logging settings;
  - its source: `uuid.c` and `ri_triggers.c`;
  - Django 5.2's notes on psycopg 3's parameter binding.
- **Notion,** read-only (section 7).

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1. CX1 and the second cycle | **Both cycles confirmed. (b), approved with conditions (K1, K3 to K7),** in this correction. (a) and (c) declined. (b)'s list of locks is short by three, and the reference design must change with the app |
| 2. V1 | **The exposure is confirmed, and is wider than stated.** Neither (a) nor (c). **(b)'s aim is approved, by a simpler means (K2):** a random value drawn inside the statement, with no key at all |
| 3. The sequence | **Agree,** with the brief's revision 3 first and the review's focus widened (section 5) |
| 4. Notion | **Matches `1da77cd`, with two small mismatches;** the handoff itself has three stale lines (section 7) |
| DM-60's Q1 to Q20 | **Confirmed as applied** at `1da77cd` (section 6) |

**How to apply:**
- **K1 to K7 go in the brief,** as its revision 3, before C1's prompt.
- **They are Markdown records,** in given words; line breaks may move. None is governing Markdown.
- **Verified by script:** each of the 8 old passages was found exactly once at `1da77cd`, and all seven conditions apply in order to a copy.
- **No further read is needed before C1's prompt** if they are applied as written. A departure comes back first. My next consultation confirms them (step 6).

## 3. Item 1 — CX1 and the second cycle

### 3.1 Both cycles are real

**The lock rules,** from PostgreSQL 17's manual ("Row-Level Locks", Table 13.3):

| A lock in this mode... | ...conflicts with |
|---|---|
| `FOR KEY SHARE` | `FOR UPDATE` only |
| `FOR SHARE` | `FOR NO KEY UPDATE`, `FOR UPDATE` |
| `FOR NO KEY UPDATE` | `FOR SHARE`, `FOR NO KEY UPDATE`, `FOR UPDATE` |
| `FOR UPDATE` | all four |

**The foreign-key check takes `FOR KEY SHARE`.** In PostgreSQL's source (`ri_triggers.c`, `RI_FKey_check`, on insert into the referencing table), the check is `SELECT 1 FROM [ONLY] <pktable> x WHERE pkatt1 = $1 [AND ...] FOR KEY SHARE OF x`.

**Page creation, as built** (`pages.create`):
- it locks the viewer's account `FOR UPDATE` (`lock_account`);
- then it inserts up to 100 entries, each referencing a candidate's account, so each entry's check takes `FOR KEY SHARE` on that account.

**Codex's cycle:**
- Two mutually eligible members, A and B, each create a page.
- Each holds its own account `FOR UPDATE`.
- Each then waits for `FOR KEY SHARE` on the other's account.

**The manager's second cycle is right.**
- A two-account writer locks the lower account first.
- With a candidate C below the viewer V, the writer holds C and waits for V, while the page holds V and waits for C's key-share lock.
- **One addition:** every two-account writer of `glow_chat` can take part, `send` and `unmatch` included.
  - Those two need a match between C and V. Consumption keeps a matched C out of V's selection.
  - But a match committed after the selection's snapshot and before the entries' insert puts such a C in the batch.
  - Stage B's like, under both locks, will take part the same way.
- **Which transaction is aborted cannot be chosen.** The manual: *"PostgreSQL automatically detects deadlock situations and resolves them by aborting one of the transactions involved, allowing the other(s) to complete. (Exactly which transaction will be aborted is difficult to predict and should not be relied upon.)"* So a block can be the one refused.

**Where each cycle is reachable today:**
- the first, through Stage A's own page route;
- the second, only in the proof, until Stage B adds the block and like routes.

### 3.2 The options

**(a), declined.**
- It closes Codex's cycle: `FOR NO KEY UPDATE` does not conflict with `FOR KEY SHARE`.
- It leaves the second: the writer's `FOR UPDATE` on C still blocks the page's key-share lock.

**(c), declined.**
- A retry cures a deadlock only after it happens. PostgreSQL detects it only after `deadlock_timeout` (one second by default).
- The victim may be the block, so the pair writers would need retries too, against SV2's and `glow_chat`'s rule that nothing is retried.

**(b), approved.**
- **Why it is safe:**
  - `FOR NO KEY UPDATE` still excludes every other writer, and every `FOR SHARE` reader (SV2's `read_account_shared`, `glow_chat`'s token grant).
  - The only conflict it drops is with `FOR KEY SHARE`, which only foreign-key checks take here.
  - No code waits on a foreign-key check to learn an account's state: a check that waits learns nothing but that the row still exists. So no guarantee rests on the conflict dropped.
- **Nothing deletes an account row or changes its keys:**
  - `auth_user` is `PROTECT`ed, and set only when the account is made;
  - deletion is the lifecycle transition (`glow_chat`'s 5.6).

  If one ever did, PostgreSQL would take `FOR UPDATE` for it by itself. The manual: *"The `FOR UPDATE` lock mode is also acquired by any `DELETE` on a row, and also by an `UPDATE` that modifies the values of certain columns"*, those with a unique index usable in a foreign key. So (b) never weakens referential integrity.
- **It closes both cycles, and any later write that references another account:**
  - Stage B's like, whose interaction row references its target;
  - the match;
  - the block.
- **The writers' own updates** already take `FOR NO KEY UPDATE`: *"This lock mode is also acquired by any `UPDATE` that does not acquire a `FOR UPDATE` lock."* So under (b) the app never holds an account row `FOR UPDATE`.

**Three locks are missing from (b)'s list.** Besides `lock_account`, `lock_account_any_state` and `glow_chat`'s `_lock`, three more lock an account row `FOR UPDATE`:
- `glow_profiles/identity_verification.py` (`_locked`);
- `glow_identity/revocation.py` (`mark_verified`);
- `glow_identity/age.py` (`transition`).

They lock one account each, so they cannot close a cycle. But left alone:
- a page's foreign-key check would wait behind them;
- the two that run inside an SV2 operation would raise its `FOR NO KEY UPDATE` back to `FOR UPDATE` for the rest of the transaction.

So (b) covers every explicit lock of an account row, and a scan keeps it so (K3).

**The reference design changes with the app.**
- The data model says the app's transaction design is *"P06.DB's reference design (its brief, D5), carried as written"*.
- The ordering suite runs its cases and controls against both the reference (`reference.py`) and the app's adapter. Its wait observations do not depend on the lock's mode.
- Changing the reference's account locks too keeps one design, proven in both subjects. The suite's controls must still fail as designed.

**What stays as it is:**
- the proof's harness locks (`cases.py`'s holder, `planted.py`'s plants), which are not the design under proof. A harness's `FOR UPDATE` still makes every writer wait;
- every lock of a row other than an account (matches, sessions, pointers, an account's own rows).

### 3.3 This correction, not an item of its own

- **The cause is Stage A's.** Its page creation is the first write that references other members' accounts while holding one, and the first cycle is reachable through its own route.
- **`main` should not take a known cycle** for Stage B to clear first.
- **One item at a time** (Nathan, 24 September): a separate item before Stage B would still be SV3's.
- **The change is small and mechanical,** and Stage A's exact-head review reviews it once, with the code that needs it.

### 3.4 What the proof must show (K3, K4)

- **Codex's cycle:** two mutually eligible viewers create batches at once, from separate connections.
  - Each holds its own account lock before either writes its entries.
  - Both orders; both pages succeed.
- **The second cycle:** `glow_chat`'s `block` between a candidate and the viewer, the candidate's account below the viewer's, races the viewer's page creation.
  - Both interleavings; both succeed.
- **The rule itself:** a page whose candidate's writer holds that candidate's account lock completes without waiting.
- **A scan:** no explicit lock of an `AppAccount` row in `services/api` or in the reference design is anything but `FOR NO KEY UPDATE`.
- **The reversals:**
  - with the account locks `FOR UPDATE` again, the first two cases deadlock (`40P01`, one side `provider_unavailable`), and the third waits;
  - a planted `FOR UPDATE` fails the scan.
- **Unchanged:** the ordering suite on both subjects, with every control failing as designed, and the identity and profile suites, all passing; the discovery phase within the job's 30 minutes.

**K1:** in the brief, D2, replace:

> ```
> so the recheck sees each writer's committed state or waits for it.
> ```

with:

> ```
> so the recheck sees each writer's committed state or waits for it.
>   - **Account locks** (DM-61): every explicit lock of an `AppAccount` row, in the app and in the reference design, is `FOR NO KEY UPDATE`. It excludes every other writer and every `FOR SHARE` reader, as `FOR UPDATE` did, but not the `FOR KEY SHARE` that PostgreSQL's foreign-key check takes. So a write that references another member's account, such as a batch's entries, never waits on that member's writers, and no lock cycle forms through one (Codex's CX1 on PR45). Nothing deletes an account row or changes its keys; a delete or a key change would take `FOR UPDATE` by itself.
> ```

**K3:** in the brief, D14, replace:

> ```
>   - **Concurrency from separate connections** (DB05, Stage B): simultaneous reciprocal likes, in both arrival orders, give one match and one `match_activated` event. Repeated likes with fresh keys give one row.
> ```

with:

> ```
>   - **Concurrency from separate connections** (DB05, Stage B): simultaneous reciprocal likes, in both arrival orders, give one match and one `match_activated` event. Repeated likes with fresh keys give one row.
>   - **Page creation under concurrency** (Stage A, correction C1; DM-61), from separate connections, each interleaving held at its locks by the probes: two mutually eligible viewers create batches at once, each holding its own account lock before either writes its entries, in both orders, and both pages succeed; `glow_chat`'s `block` between a candidate and the viewer, the candidate's account below the viewer's, races the viewer's page creation in both interleavings, and both succeed; and a page whose candidate's writer holds that candidate's account lock completes without waiting. A scan of `services/api` and the reference design finds no explicit lock of an `AppAccount` row other than `FOR NO KEY UPDATE`. The reversals: with the account locks `FOR UPDATE` again, the first two cases deadlock (`40P01`, one side `provider_unavailable`) and the third waits; a planted `FOR UPDATE` lock fails the scan.
> ```

**K4:** in the brief, acceptance check 5, replace:

> ```
> the query count per page; the recorded plans.
> ```

with:

> ```
> the query count per page; the recorded plans. Since C1 (DM-61): page creation under concurrency (D14) succeeds; the tie-break draws a new random order for each batch, which the entries' positions keep, and no statement or parameter carries a key; with an order computable from the batch's and the profiles' IDs (the reversal), the check fails.
> ```

**K5:** in the brief, "Owned paths", replace:

> ```
> - `services/api/glow_domain/profile_settings.py`: the fixed limit `rematch_not_built` only (D12; DM-60).
> ```

with:

> ```
> - `services/api/glow_domain/profile_settings.py`: the fixed limit `rematch_not_built` only (D12; DM-60).
> - **Correction C1 only** (DM-61; D2's account locks): every explicit lock of an `AppAccount` row taken `FOR NO KEY UPDATE`, with the docstrings that state the mode, and nothing else in these files: `services/api/glow_profiles/tx.py` (`lock_account`, `lock_account_any_state`), `services/api/glow_profiles/identity_verification.py`, `services/api/glow_identity/revocation.py`, `services/api/glow_identity/age.py`, `services/api/glow_chat/contact.py` (`_lock` for `AppAccount` rows only; every other row's lock, and every writer's body, unchanged), the module docstrings of `services/api/glow_profiles/operations.py` and `media.py`, and the reference design's account locks in `proofs/postgres-ordering/glow_ordering_proof/reference.py`. With them: the test that pins the two lock functions' bodies (`services/api/tests/test_profiles_offline.py`), and the records that state the account lock's mode (the data model, the contract document's F07 server section and the P11 plan's revocation lock-wait line).
> ```

**K6:** in the brief, "Exclusions", replace:

> ```
> - `services/api/glow_chat/**`, except D10 (a)'s writer: SV3 calls the existing writers unchanged.
> ```

with:

> ```
> - `services/api/glow_chat/**`, except D10 (a)'s writer and C1's account lock mode (DM-61): SV3 calls the existing writers unchanged.
> ```

and replace:

> ```
> - `services/api/glow_identity/**` and `services/api/glow_profiles/**`: SV3 uses SV1's actor and SV2's reads and writers unchanged. A change one of them needs stops the session.
> ```

with:

> ```
> - `services/api/glow_identity/**` and `services/api/glow_profiles/**`: SV3 uses SV1's actor and SV2's reads and writers unchanged, except C1's account lock mode (DM-61). Any other change one of them needs stops the session.
> ```

**K7:** in the brief, "Review plan", replace:

> ```
>   - the consistent view (D2): the single-statement selection, and the action's recheck under locks;
> ```

with:

> ```
>   - the consistent view (D2): the single-statement selection, and the action's recheck under locks;
>   - the account locks (D2; DM-61): every explicit lock of an `AppAccount` row, in the app and in the reference design, `FOR NO KEY UPDATE`; nothing that deletes an account row or changes its keys; the page-creation concurrency cases and their reversals (D14);
>   - the tie-break (D6; DM-61): a random value drawn inside the selection, with no key in any statement, parameter or log line;
> ```

## 4. Item 2 — V1, the tie-break key

### 4.1 The exposure is real, and wider than stated

**The key travels in the statement's text.**
- Django 5.2 with psycopg 3 *"defaults to the client-side binding cursors"* (its database notes).
- So the pads are written into the statement's text before it reaches PostgreSQL. They are not separate bind parameters.

**So the default configuration already logs them on any error.**
- PostgreSQL's `log_min_error_statement` defaults to `ERROR`: *"statements causing errors … will be logged"*, with their text.
- So a selection that fails, by a statement timeout, a cancellation or an out-of-memory sort, writes the key's pads into the server log.
- No logging setting needs to be switched on for that.
- The suite's ledger and scans cover the app's own outputs, not the database server's log.

**The pads are the key.**
- The pads are the derived key XORed with constants, so holding them is holding the key.
- The key is one long-lived value for every batch, until `SECRET_KEY` changes.
- So one leaked line lets its reader compute the order of every batch, and read band boundaries from it. That is the leak DM-60's Q2 meant to close.

**My mistake.**
- DM-60's Q2 named `salted_hmac`, a long-lived key, for a value the selection computes in SQL.
- I did not foresee that the key would then have to travel in every selection statement.
- K2 replaces Q2's words.

### 4.2 The options

- **(a), declined.** It rests on a P11 logging rule for parameters, but the default error log records the statement's text, and with client-side binding the pads are in that text.
- **(c), declined,** for the manager's reason: it breaks D2's one-statement selection and its bound.
- **(b)'s aim, approved, by a simpler means.**
  - A per-batch secret limits a leak to one batch. But it still travels in a statement, unless the database makes it, and it needs a field in migration 0010.
  - The order does not need a key at all. The entries' positions already record it, so nothing ever computes it again:
    - each page reads `position`;
    - the recheck keeps it;
    - recommendations sort the selected rows in Python by band, then by the value the statement returned.
  - **So the tie-break can be a random value that PostgreSQL draws for each candidate inside the selection,** `gen_random_uuid()`.
    - It is in core: *"PostgreSQL includes one function to generate a UUID: gen_random_uuid"* (since PostgreSQL 13).
    - It fills its bytes from `pg_strong_random` (`uuid.c`).
    - It needs no extension, no parameter, no field and no migration.
    - A client still cannot compute the order from the IDs, and a new batch draws new values.
- **What goes with it:**
  - `keys.sql_pads` and the ledger's derived keys and pads;
  - the plans' throwaway key;
  - `pages.keyed_stable_order`'s pin to `salted_hmac`.
- **The cursor's MAC is unchanged.** Python computes it, and it never enters a statement.

**K2:** in the brief, D6, replace:

> ```
> Ties are broken by an app-owned secondary key, a keyed hash of the batch and the candidate (`salted_hmac` with a salt of its own and SHA-256, as `glow_profiles/idempotency.py` keys SV2's stored digests, so that a client who knows the batch's and the profiles' IDs cannot compute the order and read band boundaries from it; DM-60), so the order is stable within a batch and reveals nothing between batches.
> ```

with:

> ```
> Ties are broken by an app-owned secondary key: a random value PostgreSQL draws for each candidate inside the selection (`gen_random_uuid()`, core since PostgreSQL 13, from its `pg_strong_random`), stored nowhere, since the entries' positions record the order it gives. No key exists, so none can travel in a statement or reach a log, and a client who knows the batch's and the profiles' IDs still cannot compute the order or read band boundaries from it (DM-61, replacing DM-60 Q2's keyed hash, whose key the selection had to carry as a statement parameter). The positions keep the order stable within a batch, and a new batch draws new values, so the order reveals nothing between batches.
> ```

**What the proof must show** (K4 holds it for check 5):
- **No key travels.** No executed statement or parameter carries a value derived from `SECRET_KEY`.
- **The order is stable** within a batch, across its pages.
- **Two batches differ.** Over the same candidates in one band, two batches order them differently.
  - With at least 10 candidates, equal orders have a chance below 1 in 3.6 million.
- **The reversal:** an order computable from the batch's and the profiles' IDs (an unkeyed hash, or the profile ID) fails the check.

## 5. Item 3 — The sequence

**Agree:** one correction, C1, carrying CX1's (b) and V1's random tie-break, each with its tests and reversals, then the manager's verification, the exact-head review and my pre-merge read. In detail:
1. **The brief's revision 3,** applying K1 to K7, before C1's prompt. C1's prompt needs no read of mine if it carries them as written.
2. **C1:** the code, the tests and reversals of section 3.4 and K2's proof, and the records that state the account lock's mode and the keyed tie-break:
   - the data model;
   - the contract document;
   - the P11 plan's DB11 line ("stable keyed order");
   - the threat model's inputs.
3. **The manager's verification of C1.**
4. **On C1's head:** PR45's run, which is full scope, and Codex's review. CX1's thread is answered with C1's commit.
5. **The exact-head review of Stage A's final head,** reading `ad9ff08` and C1 together, with its threat model.
   - Its prompt's revision 2 takes K7's two new focus lines, and V2 as the nit the manager named.
   - Reading both together needs no delta review: nothing has been reviewed yet.
6. **My pre-merge read,** at a named commit:
   - the CI policy's paragraph, and the data model's and contract document's rewritten texts, C1's lock texts included;
   - the two procedure gaps the session named: Foundation has no `workflow_dispatch`, and a Markdown-only push certifies no code.

## 6. DM-60's Q1 to Q20 as applied

**Confirmed:**
- **The texts are in place.** At `1da77cd`, each of DM-60's 26 replacement texts is present exactly once, and none of the old texts remains:
  - Q1 to Q15 in the brief;
  - Q16 in the P11 plan;
  - Q17 to Q20 in the carried-items file.
- **Nothing else changed in the brief.** Revision 2 is revision 1 with my conditions applied, plus its status line and its "Sessions" entries.
- **The carried-items file** has no other change.
- **The P11 plan's other changes** are Stage A's partial evidence entries, which are Stage A's records (section 5, step 6).
- **So the review log's deferred row** "DM-60: Q1 to Q20 … are confirmed as applied" can close.

## 7. Item 4 — Notion (read-only, at about 00:12 UTC; content as of 23:47 UTC on 11 November, the register copy's as of 17:22 UTC)

**How I read it:**
- I searched each page's full text for the items asked, and read Implementation Control's standing bullets whole.
- I did not read every line of its history.

**Implementation Control** says it is matched to `1da77cd`.
- **Its status:**
  - CX1 found and confirmed;
  - DM-61 sent;
  - the review prompt held;
  - PR45's run of record.
- **Its standing lines:**
  - "Next items" now says "P06.2-F (**done**, PR40)", so DM-60's fix is in;
  - "Mistakes log" holds AM11-01 to AM11-07, as the log does at `1da77cd`;
  - "Standing directions" says OD-01 to OD-63;
  - "Main" names PR45 as open.
- **One mismatch: the "Branches" bullet.**
  - It says "three", listed at 18:14 UTC, and names Stage A's session branch only inside the manager branch's description.
  - The handoff lists four remote branches at 22:39 UTC: `main`, the manager branch, `claude/dev-manager`, and `claude/loving-maxwell-cqu7eq` (`4dee875`).
  - `git ls-remote` shows those four now.
  - It should say four, with that listing's time.

**SV3's Work Register row:**
- "In progress";
- its next action matches: DM-61 at `1da77cd`, the prompt held, C1 next.
- **One mismatch:** its Evidence link is pinned at `7e4d826`, before `1da77cd` added the record's "Codex on `7e4d826`" section. It should pin `1da77cd`.

**The Dev Manager page** matches the review log.
- **DM-60** is considered: merge `72791a7`; Q1 to Q20 applied at `fe1b6ba`; the phrase corrected (AM11-02).
- **DM-61** is pending.
- **Optional:** the two copies of Dev Manager 4's "Sessions" row now differ, and both are stale.
  - The repository's says "DM-45 to DM-57"; Notion's says "DM-42 to DM-59"; DM-60 is answered.
  - The fix is "DM-45 onward: each answer and its integration are in its row below" in both, which cannot go stale.

**The register copy** matches.
- Its 63 rows are unchanged since `8130439`, and so is the repository's register: `git diff 8130439 1da77cd` on it prints nothing.
- **So my DM-60 comparison stands:** the same seven rows, where Notion writes a file path as a name, differ once formatting is set aside.

**In the repository: three stale lines in the handoff** (`current-handoff.md` at `1da77cd`). Implementation Control is right where the handoff is not.
- **Its title** still says "SV3's brief with the Dev Manager". Stage A is in PR45, with DM-61 out.
- **Its "Manager" bullet** still says *"No PR is open: App Manager 11 opens SV3 Stage A's PR from this branch once Stage A has a code head."* PR45 has been open since 22:39 UTC.
  - Its "Branches and PRs" section, dated 22:39 UTC, also says the PR is "opened … after this commit". It should name PR45.
- **Its "Review log" bullet** still says "DM-01 to DM-59" and *"the next consultation confirms DM-59's L1 to L7 as applied"*.
  - DM-60 confirmed them and was answered.
  - The handoff's own "Next actions" already says the next consultation confirms DM-60's Q1 to Q20.

## 8. Where each item goes

- **The brief's revision 3,** before C1's prompt: K1 to K7.
- **C1:** its code, tests, reversals and records (sections 3.4, 4.2 and 5).
- **The review log:**
  - DM-61's dispositions, naming the commit each read covered;
  - the deferred row for DM-60's Q1 to Q20 closes (section 6);
  - a new deferred row: K1 to K7, confirmed at my next consultation.
- **The handoff:** its three stale lines (section 7).
- **Notion:**
  - Implementation Control's "Branches" bullet;
  - SV3's Evidence link;
  - optionally, the "Sessions" row's wording, with the repository's.

Status: complete

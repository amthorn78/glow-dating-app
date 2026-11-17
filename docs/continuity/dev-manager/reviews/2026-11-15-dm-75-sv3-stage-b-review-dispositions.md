# DM-75 — SV3 Stage B: the exact-head review's findings, before correction B-C2

- **From:** Dev Manager 5 (`session_01Q789u3CWg6s9pBGXerCQZt`), for App Manager 11, relayed by Nathan (OD-25).
- **Date:** 15 November 2026. Received about 17:26 UTC; finished about 17:55 UTC.
- **Read at:** `c9bca52c79c5813e5f13a58d5502acd3b95c06fd` of `claude/magical-wozniak-yfmmx2`, exported outside any worktree, with the governing diff since my last read (`6fa1b2c`, DM-74).
  - No governing path changed since `6fa1b2c`: no `AGENTS.md` or `CLAUDE.md`, nothing in `docs/pf-canon/`, the manager workflow, the charter or the CI policy.
  - The non-Markdown tree at `c9bca52` is `470d97a`'s, the code the review read.
- **Environment:** names only. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, or any `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name is set. The AWS names are present and were not read.
- **What I changed:** this file only, on `claude/dev-manager`. Notion was read, not changed. No call to Stream, a database, HDE, Railway or Cloudflare.

## 1. The answers

| Item | Verdict |
|---|---|
| 1. #1, a block's direction | **Approved with conditions: (c).** Carried to SV4 and sealed until P11. No decision for Nathan now; the rule stands. The texts are corrected, including three the review did not list. P11 gains a precondition (section 3; GG1 to GG11) |
| 2. #2, undo chained | **Approved with conditions: (a), one step,** read as "the pass must be the actor's latest decision of any kind". That is a reading of OD-60, not a referral (section 4; GG12 to GG15) |
| 3. #3, the coverage test | **Approved,** as recommended (section 5) |
| 4. #4 to #6 and #13, D14's rule | **Approved with conditions.** #4 and #5 are corrected and fail closed, with four conditions; #6 and #13 are stated (section 6; GG16 to GG21) |
| 5. #7, the `GET` routes | **Approved: records only,** with words for the two contract texts (section 7; GG22, GG23) |
| 6. The nits and records | **Approved,** in B-C2, with #9 the manager's. #16 becomes a case, not a narrowed credit. Words for DB05 and migration 0011's note (section 8; GG24, GG25) |
| 7. FF1 to FF6 | **Confirmed as applied;** the deferred row closes (section 9) |
| 8. The sequence | **Agreed,** with B-C2's section and owned paths in given words. The bounded delta re-review matches C4's and C5's precedent. A full review applies instead if B-C2 crosses S2's line (section 10; GG26, GG27) |
| 9. Notion | **No mismatch** at `c9bca52` (section 11) |

## 2. What I read and checked

- **The review**, from the record's "Exact-head review of Stage B" (lines 1846 to 1884), with the manager's check, and the consultation.
- **The code each finding rests on, at `470d97a`:**
  - `glow_chat/contact.py`: `block` (lines 645-714), `unblock` (716-751) and `unmatch` (753-794);
  - `glow_discovery/interactions.py` (all 608 lines);
  - `interaction_views.py` (all 178 lines);
  - `contract.py`'s `match_projection`;
  - `row_locks.py` (lines 1-420);
  - the plan-coverage test and its pins;
  - the undo, resurfacing and block cases;
  - `continue_page`;
  - `decided_at`'s field.
- **The writers of `restricted`.** On the server, `contact.py:692` is the only one. `glow_domain/interactions.py` (P05.3's in-memory fixture commands) also restricts a match on a block, and in `_refresh_match` when the pair's eligibility no longer holds. That is a second cause, as in P05's mobile fixture adapter.
- **#4 and #5 reproduced** with `row_locks.refusal`, loaded alone under `python3 -I`, using my own forms of the kinds the review lists.
  - Each of these passes at `470d97a` though PostgreSQL takes `FOR UPDATE` on account rows:
    - a `'--'` literal;
    - a `'/*'` literal closed by a later comment;
    - `$$--$$`;
    - `E'\'--'`;
    - a `"--"` alias;
    - a `U&"…"` identifier spelling the account table with escapes;
    - a comma item whose alias an `EXISTS` sub-query binds again;
    - a sub-query alias bound twice.
  - A plain `DO $$ … FOR UPDATE; END $$` block is refused at `470d97a`. A lexer that masks every dollar-quoted body would turn it into a pass, which is why condition 6.2(c) exists.
- **Origins.** OD-60's text and the second A05 message (its R option (c), line 67). OD-12. The carried-items file's "Carried to SV4". The P11 plan's precondition and migration entries.
- **Precedent for the review's size:** the record's C4 and C5 verifications, and DM-65 3.3 and DM-69 section 4.

## 3. Item 1 — #1, a block's direction

### 3.1 Confirmed

- **The finding holds.**
  - `block` sets `restricted` only on an `active` match (`contact.py:691-695`).
  - Stage B serves `str(match.state)` to either participant, through `read_match` (`interactions.py:565-576`) and the unmatch answer (`:495-500`).
  - A member who did not block, and sees `restricted`, learns that the other member did.
- **The manager's point holds: a projection change alone is not enough.**
  - `unmatch` answers `no_change` (`already_unmatched`) for an `unmatched` match (`contact.py:776-777`).
  - It takes a `restricted` match to `unmatched` with `version` and `contact_version` advanced (`:778-781`).
  - So showing the member who did not block `unmatched` would still differ from a real unmatch twice over: in their own unmatch's answer, and in the version after the blocker's later unmatch.
- **Three more texts make the same claim.** The review listed four. These three also say the direction stays hidden:
  - `interactions.py`'s module docstring (lines 59-60: "Nothing here logs or returns … a block's direction");
  - the data model's `Block` row (line 169: "its direction is never shown to the blocked member");
  - the block case's message, "both participants read the same restricted match, with no direction" (`interaction_cases.py:1090`).
  - The brief's acceptance check 10 also says "the blocked member cannot learn the direction".

### 3.2 The ruling: (c), carried to SV4 and sealed until P11

- **Nothing is served before P11.** The routes are sealed: the review's reversal R1 shows the served runtime includes none of them.
- **The right shape is SV4's to design.**
  - A fix must make the state, the version and the answers to the non-blocker's own commands alike.
  - Its shape depends on what each member reads when messaging stops. That is SV4's under OD-60 H ("one neutral line the same for every cause") and OD-12 ("after an unmatch or block neither person can send or see the conversation").
  - There are two candidate shapes:
    - the block reads as an unmatch to the member who did not block;
    - `restricted` gets more than one cause on the server, as P05.3's fixture commands and P05's mobile adapter already give it.
  - Either changes a `glow_chat` writer (D11) or what `MatchProjection`'s states mean. Building one inside Stage B would pre-empt that design.
- **(b) and (d) are worse.**
  - (b) changes a reviewed writer and D11 inside a correction.
  - (d) would drop a privacy rule that protects the member who blocks, when the leak is not inherent. The F7 contrast:
    - F7's disclosure came from OD-60's rule itself (DM-65), so only Nathan could change it.
    - Here the rule is fine and the implementation leaks, so the answer is a fix.
- **DM-65 precedent.** DM-65 carried Stage A's F7 the same way: recorded, not holding the merge, and in place before P11.

### 3.3 Who decides, and when

- **Not Nathan, not now.** D8 and F13's private projection stay as they are. Nothing changes for members, and nothing is served.
- **At SV4, only if needed.** If SV4's design would change D8's rule, F13's private projection, or what either member can do or read, SV4's brief puts it to Nathan first, in plain words (OD-32). GG3 says so.

### 3.4 The conditions, with words

1. **D8 names the gap, and acceptance check 10 follows** (GG1, GG2; the manager, with revision 17).
2. **SV4 carries the fix's rule; P11 carries the seal** (GG3, GG4; the manager, with revision 17).
3. **B-C2 corrects every text that says the direction stays hidden** (GG5 to GG11). B-C2 changes no behaviour for #1.
4. **The block case keeps its assertions.** It pins today's state. SV4's fix will change it, and SV4's prompt names it then (DD5).
5. **GG11 also carries the review's #12** (an unblock keeps the row), since the two changes are in the same sentence of the data model.

**GG1 — the brief, `docs/planning/sv3-eligibility-discovery-interactions.md` (yours, with revision 17): D8's gap.**

> ```
>   - A block's direction is never shown to the blocked member (F13).
> ```

> ```
>   - A block's direction is never shown to the blocked member (F13). **The gap** (the exact-head review of Stage B, #1; DM-75): today the member who did not block can infer it. On the server only `glow_chat`'s block makes a match `restricted`, and Stage B serves the match's state to both participants (the match read and the unmatch answer), so a member who sees `restricted` and did not block learns that the other member did. Hiding it is not a change to the projection alone: `glow_chat`'s unmatch takes a `restricted` match to `unmatched`, advancing its version, and answers `no_change` for an `unmatched` one, so the version and the answers to each member's own commands would differ too. The rule stands. SV4 designs the fix, and P11 serves a match's state to no member until it is in place (the carried-items file, "Carried to SV4"; the P11 plan); nothing is served before P11.
> ```

**GG2 — the brief, `docs/planning/sv3-eligibility-discovery-interactions.md` (yours, with revision 17): acceptance check 10.**

> ```
> unblock restores no match and no send; the blocked member cannot learn the direction.
> ```

> ```
> unblock restores no match and no send; the blocked member cannot learn the direction from the block's answers or `blocks_version`, and D8's gap (a match only a block restricts, read by both participants) is stated and carried to SV4, before P11 (DM-75).
> ```

**GG3 — the carried-items file, `docs/planning/carried-to-later-items.md` (yours, with revision 17): a new last entry in "Carried to SV4".**

> ```
> P07's console offers `discovery.rematch` only after it.
> ```

> ```
> P07's console offers `discovery.rematch` only after it.
> - **From SV3 Stage B's exact-head review (#1; DM-75): a block's direction, before P11.** D8 and F13's private projection say a block's direction is never shown to the blocked member. Today it can be inferred: on the server only `glow_chat`'s block makes a match `restricted` (`contact.py`'s `block`), and SV3's match read and unmatch answer serve the match's state to both participants (`glow_discovery.interactions`, `_match_projection`), so the member who did not block, seeing `restricted`, learns that the other did. SV4's design makes what a participant who has not blocked is served about the match (its state, its version, and the answers to their own commands and reads) the same whether the other member blocked or unmatched them, including after the blocker's later unblock or unmatch; OD-12 already treats the two alike (neither member can send or see the conversation). Its inputs: OD-60 H's one neutral line the same for every cause, and SV2's `incomplete` cause (above); `glow_chat`'s unmatch takes a `restricted` match to `unmatched`, advancing its version, and answers `no_change` for an `unmatched` one; a block changes a match only while it is `active`; P05.3's fixture commands (`glow_domain.interactions`) and P05's mobile fixture adapter (`fixture-adapter.ts`) also restrict a match when the pair loses its eligibility, so there `restricted` has more than one cause; and `MatchProjection`'s states are `main`'s contract. P11 serves no route that returns a match's state to a member (SV3's match read and unmatch, or SV4's own) until the design is reviewed and in place; nothing is served before P11. If the design would change D8's rule, F13's private projection or what either member can do, SV4's brief puts it to Nathan first.
> ```

**GG4 — the P11 plan, `docs/testing/p11-deferred-acceptance.md` (yours, with revision 17): a precondition after OD-64's.**

> ```
> Not yet built: its own brief, read by the Dev Manager first.
> ```

> ```
> Not yet built: its own brief, read by the Dev Manager first.
> - **Before a match's state is served to a member: a block's direction** (SV3 Stage B's exact-head review, #1; DM-75; the [carried-items file](../planning/carried-to-later-items.md), "Carried to SV4"). On the server only a block makes a match `restricted`, so the member who did not block can infer the block's direction from the match's state, which D8 and F13's private projection forbid. P11 serves no route that returns a match's state to a member (SV3's match read and unmatch, or SV4's) until SV4's fix is reviewed and in place.
> ```

**GG5 — the record, `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md` (B-C2): Stage B's "Cannot" line.**

> ```
> a block's direction (a restricted match reads the same to both participants, the blocked member's own block answers as any first block does, and a block bumps only its actor's `blocks_version`; `block.works_after_unmatch_and_while_paused`);
> ```

> ```
> a block's direction from the block's own answers (the blocked member's own block answers as any first block does, and a block bumps only its actor's `blocks_version`; `block.works_after_unmatch_and_while_paused`), though a match only a block restricts, read by both participants, lets the member who did not block infer it (corrected in B-C2: the exact-head review's #1, D8's gap, carried to SV4 before P11; DM-75);
> ```

**GG6 — the contract document, `docs/architecture/production-contracts.md` (B-C2): the F10 and F13 bullet.**

> ```
> an unblock restores no match and no send; a restricted match reads the same to both participants, so the blocked member cannot learn the direction.
> ```

> ```
> an unblock restores no match and no send. A match reads `restricted` only after a block, and both participants read its state, so the member who did not block can infer the direction: D8's gap (the exact-head review of Stage B, #1; DM-75), which SV4 closes before P11 serves any match state (the carried-items file, "Carried to SV4").
> ```

**GG7 — the block case, `proofs/postgres-ordering/glow_ordering_proof/interaction_cases.py` (B-C2): its docstring.**

> ```
>     is paused; it refuses a send; an unblock restores no match and no send. The blocked member
>     cannot learn the direction: a restricted match reads the same to both participants, and the
>     blocked member's own block answers as any first block does."""
> ```

> ```
>     is paused; it refuses a send; an unblock restores no match and no send. The blocked member's
>     own block answers as any first block does. A restricted match reads the same to both
>     participants, but only a block restricts a match, so the member who did not block can infer
>     the direction (D8's gap, carried to SV4 before P11; DM-75)."""
> ```

**GG8 — the block case, `proofs/postgres-ordering/glow_ordering_proof/interaction_cases.py` (B-C2): its message only.**

> ```
>         "both participants read the same restricted match, with no direction",
> ```

> ```
>         "both participants read the same restricted match (D8's gap; DM-75)",
> ```

**GG9 — `services/api/glow_discovery/contract.py` (B-C2): `match_projection`'s docstring.**

> ```
>     """``MatchProjection``, for a participant only: the other member's profile ID and the state,
>     never who restricted it or why."""
> ```

> ```
>     """``MatchProjection``, for a participant only: the other member's profile ID and the state.
>     It names no actor and no reason, but only a block makes a match ``restricted``, so the member
>     who did not block can infer its direction (D8's gap, carried to SV4 before P11; DM-75)."""
> ```

**GG10 — `services/api/glow_discovery/interactions.py` (B-C2): the module docstring's last paragraph.**

> ```
> Nothing here logs or returns another member's private value, a count, a reason or a block's
> direction (D8, D17); a refusal names a code and an internal reason, never a value.
> ```

> ```
> Nothing here logs or returns another member's private value, a count or a reason (D8, D17); a
> refusal names a code and an internal reason, never a value. No answer names a block's direction,
> but a match's state (``restricted`` only after a block) lets the member who did not block infer
> it: D8's gap, carried to SV4 before P11 (DM-75).
> ```

**GG11 — the data model, `docs/architecture/data-model.md` (B-C2): the `Block` row (with #12).**

> ```
> an unblock removes the row, bumps the actor's `blocks_version` and restores no match and no send. A block works after an unmatch and while either member is paused; its direction is never shown to the blocked member.
> ```

> ```
> an unblock keeps the row, marks it `removed` and advances its version, bumps the actor's `blocks_version`, and restores no match and no send. A block works after an unmatch and while either member is paused. No answer names its direction, but a match only a block restricts, read by both participants, lets the member who did not block infer it (D8's gap, carried to SV4 before P11; DM-75).
> ```

## 4. Item 2 — #2, undo chained

### 4.1 Confirmed

- **The chain is real.** `latest` is chosen among the actor's `passed` rows only (`interactions.py:416-423`). After undo B, B is `withdrawn`, so A is the latest `passed` row and passes the check.
- **The existing case never tests the chain.** It tests the older pass only while the newer one stands (`interaction_cases.py:1160-1162`).
- **`decided_at` cannot be null.** It is `DateTimeField(default=timezone.now)` (`models.py:710`). So ordering all of an actor's rows by it puts no `NULL` first.

### 4.2 The ruling: (a), one step, read as the alternative reading

- **The rule.** The pass undo withdraws must be the actor's latest decision of any kind. Of all the actor's directional rows, in any state, the one with the latest `decided_at` (ties broken by ID, as now) must be that pass.
- **It is a reading of OD-60, not a change.**
  - OD-60's words: "an undo of the last pass".
  - They answer the second A05 message, which offered it as "(c) an undo of the last pass only, straight after it" (line 67). OD-60 then made it a setting with a waiting period.
  - "Straight after it" means before any other decision of the actor's.
  - So no referral to Nathan is needed.
- **Why not the `passed`-and-`withdrawn` set.** That reading needs an edge rule. Pass Z, pass A, undo A, then like A takes A out of the set, and Z becomes undoable again. That reopens a chain: each step costs a like, but it is a chain. With "latest decision of any kind" there is no edge to state.
- **The code change is one filter.** `state="passed"` comes out of the `latest` query. The row's own `passed` check (line 414) stays. The refusal stays `state_conflict`; its internal reason may be renamed.
- **The contract package stays.** Its generated description ("the actor's own most recent pass of the named target") is still true, so B-C2 needs no contract change.
- **The case** (B-C2's item 2, GG26):
  - after undo B, undo A is refused;
  - after a like of B over its withdrawn row, undo A is still refused;
  - the window check keeps its backdated pass the actor's latest decision, so it is refused for its window only (`undo_window_ended`).
  - The window check needs that change. Today it backdates the third target's pass after liking the second target, so under the new rule that pass would be refused for not being the latest decision before its window is ever checked.
  - Reversal: `470d97a`'s selection fails the case.

**GG12 — the brief, `docs/planning/sv3-eligibility-discovery-interactions.md` (yours, with revision 17): D12's undo.**

> ```
>     - **undo:** the actor's most recent pass can be withdrawn within `waiting_days` of it. Off, it cannot.
> ```

> ```
>     - **undo:** the actor's most recent pass can be withdrawn within `waiting_days` of it, and only while it is the actor's latest decision: of all the actor's directional rows, whatever their state, the one with the latest `decided_at` (ties broken by ID) must be that pass. An undo sets `decided_at`, so the withdrawal is then the latest decision; after any later like, pass or undo of the actor's, an earlier pass can no longer be withdrawn. One step, never a chain (OD-60's "an undo of the last pass", from the second A05 message's "an undo of the last pass only, straight after it"; the exact-head review of Stage B, #2; DM-75). Off, it cannot.
> ```

**GG13 — the contract document, `docs/architecture/production-contracts.md` (B-C2): F08's undo.**

> ```
> on, only the actor's most recent pass within `waiting_days` of it becomes `withdrawn`
> ```

> ```
> on, only the actor's most recent pass within `waiting_days` of it, while it is still the actor's latest decision (no like, pass or undo of theirs after it; D12, DM-75), becomes `withdrawn`
> ```

**GG14 — the data model, `docs/architecture/data-model.md` (B-C2): the undo row.**

> ```
> the setting on and the waiting period; the actor's most recent pass;
> ```

> ```
> the setting on and the waiting period; the actor's most recent pass, which must be their latest decision (D12; DM-75);
> ```

**GG15 — `services/api/glow_discovery/interactions.py` (B-C2): the module docstring's undo paragraph.**

> ```
> **Undo** (D12; D13's ``InteractionUndoIntent``) withdraws the actor's most recent pass within
> ``discovery.undo``'s ``waiting_days`` of it, while the setting is on (``forbidden`` while off); the
> row is kept and its version advanced (``withdrawn``), never deleted and created again.
> ```

> ```
> **Undo** (D12; D13's ``InteractionUndoIntent``) withdraws the actor's most recent pass within
> ``discovery.undo``'s ``waiting_days`` of it, while the setting is on (``forbidden`` while off), and
> only while that pass is the actor's latest decision (the latest ``decided_at`` of all their rows,
> in any state; DM-75): one step, never a chain. The row is kept and its version advanced
> (``withdrawn``), never deleted and created again.
> ```

## 5. Item 3 — #3, the coverage test

- **Agreed, as recommended.**
  - Stage A's checks and decisions are computed over Stage A's own cases: those in neither `STAGE_B_CASES` nor `B_C1_CASES` (`test_discovery_offline.py:372-404`).
  - Stage B's and B-C1's labels are checked over their own cases.
  - The review's mutation must fail the test, as it does at `947576d`.
  - The record's claim is corrected.
- **No words are needed beyond B-C2's item 3** (GG26).

## 6. Item 4 — #4 to #6 and #13, D14's rule and its limits

### 6.1 The ruling

- **Approved as recommended:** #4 and #5 corrected and failing closed; #6 and #13 stated.
- **Why correct them, not just state them.**
  - The rule exists to catch a writer's lock on account rows, the class of DM-61's lock cycle.
  - Its comment stripping is a known misreading. It hides a lock in ordinary raw SQL, not only in contrived text. A literal holding `--` or `/*` is enough, and the app already sends raw statements (`predicates`).
  - A fail-closed reading can only add refusals, and a refusal fails the suite where it shows.
  - This answers class 5 by making the claims true, not by narrowing them.

### 6.2 The conditions

These are the brief's words in GG16 and GG17, and B-C2's items 4 to 6 in GG26.

- **(a) A quoted identifier stays a name.** Django quotes every table (`"glow_persistence_appaccount"`), so masking quoted identifiers would hide the account table from every statement. Comment markers inside a quoted identifier are not comments.
- **(b) Every string constant and every comment is masked before judging.** That covers `'…'` with `''`, `E'…'` with backslash escapes, `U&'…'` and dollar-quoted strings, and comments `--` and `/* … */` (nested).
- **(c) Some statements fail by rule:** a `DO` statement, since its dollar-quoted body runs as code and masking it would hide a lock that `470d97a` refuses today; a statement holding a `U&` quoted identifier, since its escapes can spell the account table; and a statement with an unterminated span or block comment.
- **(d) An `OF` name counts only where the statement binds it once, in any scope.** The binding must be a plain `FROM` or `JOIN` item's table or its alias. The account table may appear only as such an item's table or as a column's qualifier. Any other form fails: a name bound twice, a comma item, a schema-qualified name, `ONLY`, `*`, a sub-query's or a function's alias, or the account table inside a sub-query.
- **The tests.**
  - Each of the review's eight texts fails at B-C2's head and passes at `470d97a`.
  - Each passes with `FOR NO KEY UPDATE` in its place. The `DO` statement is the exception: it fails either way, by rule.
  - The review's scope example and one planted example of each of (d)'s forms fail.
  - The existing row-lock offline tests are unchanged. Their statements keep their verdicts under (a) to (d).
  - The run of record shows no refusal in any suite. A refusal is a stop.
- **#6 and #13** are stated in the README (GG18 to GG21). `row_locks.py`'s docstring says the same, in the README's words:
  - its "whatever wrapper a case adds inside it" goes;
  - `psycopg.connect` leaves its "unseen" list, since the driver's patched cursor methods record it;
  - the connection count is explained.

**GG16 — the brief, `docs/planning/sv3-eligibility-discovery-interactions.md` (yours, with revision 17): D14's rule.**

> ```
> unless its lock clause is `FOR UPDATE OF` a list of names none of which is that table or an alias the statement gives it; a lock clause it cannot read that way fails too.
> ```

> ```
> unless its lock clause is `FOR UPDATE OF` a list of names none of which is that table or an alias the statement gives it; a lock clause it cannot read that way fails too. It reads a statement as PostgreSQL does: every comment (nested block comments included) and every string constant (dollar-quoted ones included) is masked before it judges, a quoted identifier stays a name, and a statement with an unterminated span, a `DO` statement (its body runs as code) and a statement holding a `U&` quoted identifier fail. An `OF` name counts only where the statement binds it once, in any scope, as a table named in a plain `FROM` or `JOIN` item or that item's alias, and the account table appears only as such an item's table or a column's qualifier; any other form fails: a name bound twice, a comma item, a schema-qualified name, `ONLY`, `*`, a sub-query's or a function's alias, or the account table inside a sub-query (the exact-head review of Stage B, #4 and #5; DM-75).
> ```

**GG17 — the brief, `docs/planning/sv3-eligibility-discovery-interactions.md` (yours, with revision 17): D14's reach.**

> ```
> It is exact for the statements the suites send through Django's `execute` and `executemany`, and sees no code they do not run
> ```

> ```
> It is exact for the statements the suites send through Django's `execute` and `executemany`, as Django's `execute` receives them (a case's own wrapper inside it is judged on the text before any rewrite, and a statement that wrapper sends through the driver is not recorded; none does today; DM-75), and sees no code they do not run
> ```

**GG18 — the proof README, `proofs/postgres-ordering/README.md` (B-C2): D14's entry, what it records and how it reads.**

> ```
> it is exact for every statement the suites send through Django's `execute` and `executemany`, on every connection the process opens and from every thread, and for every statement sent through psycopg's own cursor methods outside them (`stream`, `copy`, `callproc`, the driver's own connection), each judged by the rule:
> ```

> ```
> it records every statement the suites send through Django's `execute` and `executemany`, as Django's `execute` receives them, on every connection the process opens and from every thread, and every statement sent through psycopg's own cursor methods outside them (`stream`, `copy`, `callproc`, the driver's own connection, a connection opened with `psycopg.connect`), but for the two forms below, and judges each as PostgreSQL reads it (every comment, nested block comments included, and every string constant, dollar-quoted ones included, masked; a quoted identifier kept as a name; a statement with an unterminated span, a `DO` statement and a statement holding a `U&` quoted identifier failing) by the rule:
> ```

**GG19 — the proof README, `proofs/postgres-ordering/README.md` (B-C2): D14's entry, the `OF` resolution.**

> ```
> (no `OF`, a sub-query's alias, a `WITH` query's name, a schema-qualified name, a view, text after the clause) fails too.
> ```

> ```
> (no `OF`, a sub-query's alias, a `WITH` query's name, a schema-qualified name, a view, text after the clause) fails too, and an `OF` name counts only where the statement binds it once, in any scope, and the account table appears only as a plain `FROM` or `JOIN` item's table or a column's qualifier (a name bound twice, a comma item, a schema-qualified name, `ONLY`, `*`, or the account table inside a sub-query fails; the exact-head review of Stage B's #4 and #5, each form planted; DM-75).
> ```

**GG20 — the proof README, `proofs/postgres-ordering/README.md` (B-C2): D14's entry, two unseen forms (#6).**

> ```
> It does not see: a statement sent below psycopg's cursors
> ```

> ```
> It does not see: a statement a case's own execute wrapper sends through the driver while Django's `execute` runs on that thread (the driver's record skips that thread until `execute` returns), and it judges a statement such a wrapper rewrites on the text before the rewrite (no case's wrapper sends or rewrites one today); a statement sent below psycopg's cursors
> ```

**GG21 — the proof README, `proofs/postgres-ordering/README.md` (B-C2): D14's entry, the counts (#13).**

> ```
> Its counts of connections and threads are of distinct identities, which a closed connection's or an ended thread's successor may reuse.
> ```

> ```
> Its counts of connections and threads are of distinct identities, which a closed connection's or an ended thread's successor may reuse, and it counts a connection's Django wrapper and its psycopg connection as two, so its connections are about twice its threads.
> ```

## 7. Item 5 — #7, the `GET` routes

- **Agreed: records only.**
  - What the routes do, confirmed:
    - every route refuses a query string (`_actor`, `interaction_views.py:73-74`) and another method (405);
    - only `post` reads the content type (`:93-95`);
    - `OwnVersionsView.get` refuses a body (`:172-177`);
    - `MatchView.get` reads neither (`:159-161`).
  - A `GET` body is never parsed, so nothing is lost.
  - Refusing a content type on a `GET` could refuse ordinary clients.
- **The record's Stage B section and the routes case's docstring say the same as GG22 and GG23**, and the case says what it checks on each route (B-C2's item 7).

**GG22 — `services/api/glow_discovery/interaction_views.py` (B-C2): the module docstring.**

> ```
> A body that is not its DTO, any query string, another content type or another method is
> ``invalid_request`` (400; 405 for the method, as SV2's and Stage A's routes answer). Another
> ```

> ```
> On each ``POST`` route, a body that is not its DTO, any query string or another content type is
> ``invalid_request`` (400), and on every route another method is ``invalid_request`` (405), as
> SV2's and Stage A's routes answer. The two ``GET`` routes refuse a query string (400) and read no
> content type; ``GET api/v1/interactions/<profile_id>`` refuses a body (400), and
> ``GET api/v1/matches/<match_id>`` reads none. Another
> ```

**GG23 — the contract document, `docs/architecture/production-contracts.md` (B-C2): the routes bullet.**

> ```
> refuses a body that is not its DTO, any query string and another content type (`invalid_request`, 400) and another method (405),
> ```

> ```
> refuses any query string (`invalid_request`, 400) and another method (405), and, on each `POST` route, a body that is not its DTO and another content type (400) (the two `GET` routes read no content type, and of them only `GET api/v1/interactions/<profile_id>` refuses a body),
> ```

## 8. Item 6 — the nits and records

- **Agreed, in B-C2,** as the consultation lists them: #8, #10, #11, #12 (in GG11), #14, #15, the revision 15 citations, migration 0011's note, and the block's 404 in F13's server mapping.
- **#9 is the manager's.** I read it at the pre-merge read.
- **#16 becomes a case, not a narrowed credit.**
  - The cursor's recheck is a real path that no case reaches: a `NULL` cutoff in `continue_page` alone passes every test.
  - `continue_page` takes the page's `limit`, so `settings.resurfacing_off_and_on` can fetch a second page by cursor with two resurfaced candidates and expect the one it has not shown.
  - B-C2 extends that case rather than adding one. Item 2 does the same with the undo case. So the count stays 66, and #9's "66 cases in all" holds. If B-C2 adds a case, the counts follow it.
- **Migration 0011's note** uses words that reflect the one-step rule (GG25). With one backfill instant, every pass would no longer be undoable. Instead, undo's choice falls to the ID tie-break.

**GG24 — the P11 plan, `docs/testing/p11-deferred-acceptance.md` (B-C2): DB05 (#10).**

> ```
> repeated likes with fresh keys at once: one row, the other refused as stale;
> ```

> ```
> repeated likes with fresh keys at once: one like applied and one row (the case asserts nothing of how the other ends);
> ```

**GG25 — the P11 plan, `docs/testing/p11-deferred-acceptance.md` (B-C2): migration 0011 on a populated target.**

> ```
> deletes them in the same migration, before the field and the constraint are added.
> ```

> ```
> deletes them in the same migration, before the field and the constraint are added.
> - **Migration 0011 on a populated target** (SV3 Stage B's exact-head review, focus 7; DM-75): it is safe on an empty table (`ADD COLUMN` is metadata-only, and the new CHECK constraints are supersets of the old). A target that already holds directional rows backfills `decided_at` from each row's `updated_at`, its last write, not one instant for every row, which would restart every resurfacing waiting period and tie every member's rows, leaving undo's latest decision (D12) to the ID tie-break; and it adds the new CHECK constraints `NOT VALID`, then validates them (`VALIDATE CONSTRAINT`).
> ```

## 9. Item 7 — FF1 to FF6

- **Confirmed as applied at `c9bca52`, checked by script.**
  - FF1 to FF3's new texts are in the brief once each.
  - FF4 to FF6's new texts are in once each, and their old passages are gone.
- **The review found FF1 to FF3 and FF6 met in code.** FF4 and FF5 are the brief's wording of the F2 cases.
- **The deferred row closes.**

## 10. Item 8 — the sequence

- **Agreed:**
  1. this answer;
  2. revision 17 (GG1, GG2, GG12, GG16, GG17, GG26, GG27), with the carried-items entry (GG3), the P11 precondition (GG4) and the CI policy's sentence (#9);
  3. B-C2's prompt with its TypeSafe reading;
  4. B-C2;
  5. the manager's verification;
  6. PR47's run and Codex on its head;
  7. a bounded delta re-review of B-C2 against `470d97a`;
  8. my pre-merge read;
  9. the merge.
- **The review's size.**
  - B-C2's non-test lines in `services/api` are a few:
    - one filter;
    - three docstrings;
    - no behaviour change but undo's selection.
  - Its proof tooling goes to the bounded delta re-review with its findings, as C4's (`account_lock_scan.py` +412 −165) and C5's (+111 −14) did.
  - Undo's rule is a reading of OD-60, so B-C2 changes no design (M05 S2).
  - If B-C2's non-test lines in `services/api` exceed 60, or it changes a design, a full exact-head review applies instead (GG26).
- **At the pre-merge read I read:**
  - the CI policy's sentence;
  - the data model;
  - the contract document;
  - the proof README's D14 entry;
  - the carried-items entry;
  - the P11 plan's two entries;
  - any governing Markdown.

**GG26 — the brief, `docs/planning/sv3-eligibility-discovery-interactions.md` (yours, with revision 17): "Stage B, correction B-C2", before "Sessions".**

> ```
> the Dev Manager's pre-merge read after it.
>
> ## Sessions
> ```

> ```
> the Dev Manager's pre-merge read after it.
>
> ## Stage B, correction B-C2 (Stage B's exact-head review; DM-75)
>
> B-C2 answers the exact-head review of `470d97a` (Stage B with B-C1; the record, "Exact-head review of Stage B"): changes required, no blocking finding. It changes no model, migration, lock, version check, existing DTO, stale body, `glow_chat` writer, lock-scan rule or bound, contract package, workflow or dependency. The block's direction (#1) is not fixed here: it is D8's gap, carried to SV4 before P11 (DM-75), and B-C2 corrects only its texts.
>
> 1. **The block's direction (#1): the texts.** Each text that said the direction stays hidden states D8's gap, in DM-75's words: the record's Stage B "Cannot" line, the contract document's F10 and F13 bullet, the block case's docstring and one message (its assertions unchanged), `contract.py`'s `match_projection` docstring, `interactions.py`'s module docstring and the data model's `Block` row (DM-75's GG5 to GG11).
> 2. **Undo, one step (#2; D12).** The pass undo withdraws must be the actor's latest decision: of all the actor's directional rows, in any state, the one with the latest `decided_at` (ties broken by ID); otherwise `state_conflict`, with nothing written. `settings.undo_off_and_on` gains: after undo B, undo A is refused; after a like of B over its withdrawn row, undo A is still refused; and its window check keeps the backdated pass the actor's latest decision (each later row of the actor's backdated before it), so it is refused for its window only (`undo_window_ended`). Its reversal: `470d97a`'s selection, over `passed` rows only, fails the case. The texts: DM-75's GG13 to GG15.
> 3. **The plan-coverage test (#3; DD5).** Stage A's checks and decisions are computed over Stage A's own cases (those in neither `STAGE_B_CASES` nor `B_C1_CASES`), and Stage B's and B-C1's over their own; the review's mutation (14, D19 and DB04 stripped from Stage A's only carriers) fails it, as it fails at `947576d`; the record's claim that the rewritten test kept what it protects is corrected.
> 4. **D14 reads a statement as PostgreSQL does (#4).** Before it judges, `row_locks.refusal` masks every comment (`--` to the line's end; `/* … */`, nested) and every string constant (`'…'` with `''`, `E'…'` with backslash escapes, `U&'…'`, and dollar-quoted strings, the tag empty or an identifier); a quoted identifier (`"…"` with `""`) stays a name, so Django's `"glow_persistence_appaccount"` is still the account table; a statement with an unterminated span or block comment fails, as do a `DO` statement, whose dollar-quoted body runs as code, and a statement holding a `U&` quoted identifier. Each of the review's eight texts fails at B-C2's head and passes at `470d97a`; each passes with `FOR NO KEY UPDATE` in place of `FOR UPDATE` (the `DO` statement fails either way, by rule); and "Comments are read as spaces" gives way to these words.
> 5. **D14 resolves `FOR UPDATE OF` without ambiguity (#5).** An `OF` name counts only where the statement binds it once, in any scope, as a table named in a plain `FROM` or `JOIN` item or that item's alias, and the account table appears only as such an item's table or a column's qualifier; any other form fails: a name bound twice, a comma item, a schema-qualified name, `ONLY`, `*`, a sub-query's or a function's alias, or the account table inside a sub-query. The review's scope example and one planted example of each form fail at B-C2's head; each that passes at `470d97a` is shown passing there.
> 6. **D14's limits and counts, stated (#6, #13).** The proof README's D14 entry (DM-75's GG18 to GG21) and `row_locks.py`'s docstring, in the README's words, state that a statement a case's own execute wrapper sends through the driver while Django's `execute` runs on that thread is not recorded, and that a statement such a wrapper rewrites is judged on the text before the rewrite; the docstring's "whatever wrapper a case adds inside it" goes; `psycopg.connect` is no longer listed as unseen; and the connection count is said to count a connection's Django wrapper and its psycopg connection as two.
> 7. **The `GET` routes' texts (#7).** `interaction_views.py`'s module docstring and the contract document's routes bullet say what each route refuses (DM-75's GG22 and GG23); the record's Stage B section and the routes case's docstring say the same, and the case says what it checks on each route. No route's behaviour changes.
> 8. **The records:** the proof README's SV3 paragraph counts Stage B's 19 cases (59), then B-C1's 66 (#8); it and the contract document's F08 to F13 paragraph name the brief's revision 17 where they named 15; the P11 plan's DB05 says what the case asserts (#10; DM-75's GG24) and gains migration 0011's note (DM-75's GG25); the contract document's flow index gains `OwnInteractionVersions` in F08's and F13's rows, as the registry has (#11); the data model says an unblock keeps the row (#12; in DM-75's GG11); and the contract document's F13 server mapping records the block's `not_found` for a profile ID that never existed, as the review judged it: a signal of existence only, on random version 4 IDs, that reveals no state (DM-74 3.4).
> 9. **The tests (#14, #15, #16),** each with a reversal: the structural test of `activate_reciprocal` compares its nested `body`'s decorators (a bypassing decorator fails it); the routes case's "another member's batch" check names an entry of another member's batch (removing the batch-owner check fails it); and `settings.resurfacing_off_and_on` reaches a resurfaced candidate on a page fetched by cursor (a `NULL` cutoff in `continue_page` fails it).
> 10. **The earlier tests it changes** (DD5; AM11-23's sweep), each named in its prompt with its reason: `settings.undo_off_and_on` (item 2), `settings.resurfacing_off_and_on` and the routes case (item 9), the block case's docstring and one message (item 1), `test_the_plan_covers_stage_as_and_stage_bs_acceptance_checks` (item 3) and the API's structural test of `activate_reciprocal` (item 9). The row-lock offline tests are only added to. Any other earlier test that no longer passes is a stop.
>
> **The stop rule (B-C2):** stop and report if B-C2 needs a change outside its owned paths, or to a model, a migration, a lock, a version check, an existing DTO, D8's single stale body, a `glow_chat` writer, the lock scan's rules or B0's bound, the contract package, the workflow or a dependency; if a statement any suite sends fails D14's corrected rule; if a form items 4 and 5 name cannot be made to fail without refusing a statement the suites send; or if a case other than those item 10 names changes its verdict.
>
> **B-C2's run of record:** a push run on its code head, with all eight jobs passing, the discovery suite 66/66, each suite's D14 record `PASS` with none refused, and the discovery phase's duration within the job's 30 minutes, read from GitHub.
>
> **The review:** a bounded delta re-review of B-C2 against `470d97a` (M05 S2; DM-75), after the manager's verification, PR47's run and Codex on its head. It reads every path B-C2 touches as it stands at its head, applies C4's five classes, plants the review's eight texts and item 5's forms against D14's rule, and runs item 2's reversal. If B-C2's non-test lines in `services/api` exceed 60, or it changes a design, a full exact-head review applies instead. The Dev Manager's pre-merge read follows.
>
> ## Sessions
> ```

**GG27 — the brief, `docs/planning/sv3-eligibility-discovery-interactions.md` (yours, with revision 17): B-C2's owned paths.**

> ```
> its runs of record only. Nothing else changes in B-C1.
> ```

> ```
> its runs of record only. Nothing else changes in B-C1.
> - **Correction B-C2 only** (DM-75): in `services/api/glow_discovery/`, undo's latest-decision rule and the module docstring in `interactions.py`, `match_projection`'s docstring in `contract.py` and the module docstring in `interaction_views.py`, and nothing else in them; in `services/api/tests/`, the structural test of `activate_reciprocal` and any test item 2 adds; in the proof, `row_locks.py` (its reading, its resolution and its docstring) and its offline tests, `interaction_cases.py` (the cases and texts its section's items 1, 2, 7 and 9 name) and `tests/test_discovery_offline.py`'s plan-coverage test; the proof README's D14 entry and SV3 paragraph; the contract document's F08 to F13 server mapping and its flow index's F08 and F13 rows; the data model's `Block` row and undo row; the P11 plan's DB05 line, migration 0011's note and its runs of record; and the evidence record. Nothing else changes in B-C2.
> ```

## 11. Item 9 — Notion (read-only, at about 17:40 UTC)

| Page | What I compared | Result |
|---|---|---|
| Implementation Control | The status heading and stamp | **Match:** "15 November 2026 (App Manager 11; DM-75 with Dev Manager 5)", last matched at `c9bca52`, with the review's findings and DM-75's recommendations as recorded |
| Implementation Control | "Next items" | **Match:** brief revision 16; DM-61's to DM-74's conditions; the exact-head review asked for changes; DM-75 with Dev Manager 5, before correction B-C2 |
| Implementation Control | "Main"; "Branches" | **Match:** `947576d`, PR47 open. Five branches, as `git ls-remote` shows: `main` `947576d`; the manager branch `c9bca52`; `claude/dev-manager` `5a74183`; Stage B's `291edef`; B-C1's `53d3988` |
| Implementation Control | "Dev Manager"; "Mistakes log"; standing directions | **Match:** Dev Manager 5; AM11-01 to AM11-27 at `c9bca52`, as the log holds; OD-01 to OD-65 |
| Dev Manager — reviews and approvals | DM-74's and DM-75's rows | **Match:** DM-74 considered, its answer and disposition columns as the review log's; DM-75 pending |
| Register copy | Rows | **Match:** 65 rows. The register is unchanged since `829f90c` |
| Work Register `SV3` | State, next action, evidence | **Match:** "In progress"; DM-75 with Dev Manager 5 from `c9bca52`, then revision 17 and B-C2; evidence pinned at `c9bca52` |

## 12. Who applies what

| Words | Where | Who |
|---|---|---|
| GG1, GG2, GG12, GG16, GG17, GG26, GG27 | The brief, as revision 17 | The manager |
| GG3 | The carried-items file | The manager, with revision 17 |
| GG4 | The P11 plan | The manager, with revision 17 |
| GG5 to GG11, GG13 to GG15, GG18 to GG25 | The record, the contract document, the data model, the proof README, the P11 plan and the three app files and one case file | B-C2 |
| #9 | The CI policy | The manager, with revision 17 (its words, read at the pre-merge read) |

Status: complete

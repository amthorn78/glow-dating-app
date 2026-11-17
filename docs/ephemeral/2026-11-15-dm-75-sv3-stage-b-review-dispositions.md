# DM-75 consultation — SV3 Stage B: the exact-head review's findings (changes required), before correction B-C2

- **Owner:** App Manager 11. Nathan carries this message to Dev Manager 5's session, `session_01Q789u3CWg6s9pBGXerCQZt` ("Glow Dev Manager 5") (OD-25, OD-65). App Manager 11 receives the answer.
- **Revision 1, 15 November 2026.**
- **Why:** the exact-head review of Stage B's `470d97a` (Stage B's `5d58993` with correction B-C1) returned changes required. Two findings need a ruling: #1 meets F13's private projection and D8's rule, and #2 is a reading of OD-60. A third choice (#4 to #6) is between correcting D14's rule and stating its limits. As with Stage A's review (DM-65), the dispositions go to the Dev Manager before the correction's prompt.
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; App Manager 11's disposition in the review log, "DM-75"; the brief's revision 17, with a section "Stage B, correction B-C2" if you give words; then correction B-C2's prompt.
- **Stream variables:** none are needed.
- **If no report arrives:** B-C2's prompt is not written; App Manager 11 asks Nathan whether Dev Manager 5's session is still available.
- **Deletion condition:** prune after the review log holds DM-75's disposition and Stage B's PR has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-75 — SV3 Stage B: the exact-head review's findings (changes required), before correction B-C2.** From App Manager 11, relayed by Nathan to Dev Manager 5. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway or Cloudflare;
- check environment variable names only.

**Where it stands.**
- **Stage B with B-C1** is built, verified and integrated (code head `470d97a`). PR47's head is `e75649d` (Markdown only after `6d71ce0`): its pull-request run 43733276848 passed all eight jobs, and Codex's code review of `e75649d` found nothing (the evidence record, "PR47 at `e75649d`").
- **The exact-head review** (prompt revision 1 at `e75649d`; Opus 5.5 at extra high) is in the evidence record, "Exact-head review of Stage B", with every finding, the rejected candidates, the reversals and the manager's check. Verdict: **changes required**. No blocking finding, seven should-fix findings in correction classes, nine nits.
- **What it found sound:** no path reveals a like (once the like's recheck passes under both locks, every refusal of `activate_reciprocal` is unreachable, so no 409 shows the target's like). Idempotency, the recheck at commit, ownership, the canonical lock order and B-C1's read hold, and the AST comparison holds for all 32 existing definitions in `contact.py`. Your conditions are met in code but for three gaps (#1, #3, #6). Every deviation and reading of the two sessions was accepted. Its reversals (R1 to R5 offline; m1 to m7, m8b and m9b on a local database) each behaved as expected.
- **The manager's check:** #1 to #7 confirmed in the code at `470d97a` (#4 and #5 reproduced with `row_locks.refusal`). #9 is the manager's own sentence in the CI policy (AM11-26).

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. #1: a `restricted` match shows the blocked member the block's direction** (recommended, (c)):
- **The finding:**
  - only `glow_chat`'s block makes a match `restricted` (`contact.py:691-692`); unmatch makes it `unmatched`, and suspension and staff restriction leave it alone;
  - Stage B serves `str(match.state)` to both participants, through the match read and the unmatch answer (`interactions.py:231-238`);
  - the blocked member knows they did not block, so `restricted` tells them the other member did.
- **What it breaks:**
  - F13's private projection in the registry (P05: "Actor receipt; block direction hidden from other user");
  - D8 ("A block's direction is never shown to the blocked member");
  - four texts that say the direction stays hidden: this record's "Cannot" line, `production-contracts.md:201`, `interaction_cases.py:1049-1050` and `contract.py:256`.
- **Why the fix is not in the projection alone** (the manager's check):
  - `glow_chat`'s `unmatch` takes a `restricted` match to `unmatched`, advancing its version, and refuses an `unmatched` one (`contact.py:776`);
  - a block changes the match only while it is `active`.
  - So suppose the member who did not block were shown `unmatched` (say). Their own unmatch would succeed where a real unmatch is refused, and the blocker's later unmatch would advance the version of a match that reads `unmatched`.
  - The state, the version and each command's answer would all have to be made alike.
- **What constrains a fix:**
  - D11 keeps `glow_chat`'s writers unchanged, and D13 allows additions only (`MatchProjection` and its enum are `main`'s).
  - The match read is sealed until P11.
  - What a member reads when messaging stops is SV4's to design (the carried-items file, "Carried to SV4": OD-60 H's "one neutral line the same for every cause", and SV2's `incomplete` cause).
  - In P05's mobile fixture adapter, a match also becomes `restricted` when the pair loses its current eligibility (`fixture-adapter.ts:120-131`), so there `restricted` has more than one cause. On the server only the block writes it.
- **Options:**
  - **(a) Fixed in B-C2,** within Stage B's code: what a participant who has not blocked is served must not depend on the block's direction, in the state, the version, and the answers to their own unmatch and block, including after the blocker's later unblock or unmatch. Your words would set the rule.
  - **(b) Fixed by changing `glow_chat`'s block** (for example, a block on an active match makes it `unmatched`, as an unmatch does). This changes D11 and an existing `glow_chat` writer, which the review prompt's classes treat as a correction class of its own, and it changes what the blocker reads.
  - **(c) Carried to SV4, sealed until P11.** B-C2 corrects the four texts and this record to say that today the blocked member can infer the direction from `restricted`, and D8 names the gap. The fix and its design go to SV4, which designs what each member reads when messaging stops and owns the contact protocol, before P11 serves the match read. This does not hold the merge, since nothing is served before P11; DM-65 did the same for Stage A's F7. The review prompt's classes put #1 in the correction pass, so a carry needs your approval.
  - **(d) Accepted as a disclosure.** This changes F13's private projection and D8's rule, a privacy rule, so it would be referred to Nathan.
- **Asked:** which; whether Nathan should decide it now or at SV4; and your words for D8, the carried-items entry, and the four texts.

**2. #2: undo can be chained** (recommended, (a)):
- **The finding:** "the most recent pass" is the latest row still `passed` (`interactions.py:416-423`).
  - After an undo, the next-older pass becomes undoable, through every pass within `waiting_days`.
  - Undo then works as on-demand resurfacing while resurfacing is off.
  - OD-60's words are "an undo of the last pass"; D12 says "the actor's most recent pass".
  - Nothing states chaining, and nothing pins it: `settings.undo_off_and_on` tests an older pass only while a newer one stands.
- **Options:**
  - **(a) One step:** the undoable row is the one with the latest `decided_at` among the actor's `passed` and `withdrawn` rows (ties by ID), and only while it is `passed`. An undo sets `decided_at`, so a withdrawn pass then blocks the next until a new pass.
    - One edge for your words: a like over a withdrawn row takes it out of that set, so the next-older pass becomes the latest again.
    - The alternative reading: undo applies only when the actor's latest decision of any kind is a pass.
  - **(b) Chaining kept:** stated in D12, the contract document and this record, and pinned by a case.
- **Asked:** which, as a reading of OD-60 or referred to Nathan; under (a), your words for D12 and the case (pass A, pass B, undo B, then undo A refused; and the like edge as you rule it).

**3. #3: the plan-coverage test pooled** (recommended: fixed in B-C2):
- **The test:** Stage A's coverage test is computed over Stage A's own cases again, and Stage B's and B-C1's labels get a check of their own.
- **Its reversal:** the review's mutation (14, D19 and DB04 stripped from Stage A's only carriers) must fail it, as it fails at `947576d`.
- **The record:** this record's claim that the rewritten test keeps what it protects is corrected.
- **Asked:** agree.

**4. #4 to #6 and #13: D14's rule and its limits** (recommended: #4 and #5 corrected and failing closed; #6 and #13 stated):
- **#4:** before judging, quoted spans are masked with a small lexer: `'…'` with `''`, `E'…'` with backslash escapes, `U&'…'`, `"…"`, `U&"…"`, dollar quotes, and nested block comments. A statement with an unterminated span is refused. The review's eight texts become tests, and "Comments are read as spaces" becomes exact.
- **#5:** a statement naming the account table with `FOR UPDATE OF` is refused when its `OF` list cannot be resolved without ambiguity: an alias bound more than once in the statement, or the account table in a form the resolver does not read (a comma item, a schema-qualified name, `ONLY`, `*`, or a sub-query). Django's statements bind each alias once in plain `FROM` and `JOIN` items, so today's suites are unaffected; the run shows it.
- **#6 and #13:** the README's "Limits" and the docstring state (a) that driver statements are skipped while a Django `execute` runs on that thread, and (b) that a rewriting wrapper is judged on the text before the rewrite. The docstring's "whatever wrapper a case adds inside it" goes, `psycopg.connect` is no longer listed as unseen, and the connection count is said to count a connection's Django wrapper and its psycopg connection separately. No current wrapper sends or rewrites SQL.
- **The alternative for all of them:** Limits only, with "exact" taken out of the README and docstring.
- **Asked:** which, and words for any condition.

**5. #7: the GET routes' refusals** (recommended: records):
- **The texts:** the module docstring, the contract document's routes bullet, this record's Stage B section and the routes case's docstring say the two GET routes take no body: they read neither a body nor a content type, and refuse a query string and another method.
- **The case:** the routes case says what it checks on each route.
- **The alternative:** code. Both GET routes refuse a non-empty body and a content type. The review found no security effect, and refusing a content type on a GET could refuse ordinary clients.
- **Asked:** agree.

**6. The nits and records** (recommended: in B-C2, except #9):
- **Records:**
  - #8: the proof README's count, 19 cases (59), then B-C1's 66;
  - #10: the P11 plan's DB05, to what the case asserts;
  - #11: the contract document's F08 and F13 index rows gain `OwnInteractionVersions`, as the registry has;
  - #12: the data model's unblock keeps the row, `removed`, with its version advanced.
- **Tests:**
  - #14: the structural test compares `body`'s decorators;
  - #15: the "another member's batch" check names an entry of another member's batch;
  - #16: a database case reaches resurfacing on a page fetched by cursor (or this record's credit is narrowed).
- **The revision 15 citations:** the proof README's SV3 paragraph and `production-contracts.md` line 194 still cite the brief's revision 15; both name the revision in force.
- **The populated target:** migration 0011's note (a `decided_at` backfill; `NOT VALID` then `VALIDATE` for the CHECK constraints) is added to the P11 plan, beside migration 0010's.
- **The block's 404:** the block's 404 for a profile ID that never existed (DM-74 3.4) is recorded in F13's server mapping in the contract document, as the review judged it: an existence-only signal on random IDs, revealing no state.
- **#9, the manager's:** the CI policy's "DB04, DB05 and DB10; 59 cases in all" becomes "DB04, DB05 and DB10, with correction B-C1's own-versions read; 66 cases in all". The manager applies it with the brief's revision 17, and you read it at the pre-merge read.
- **Asked:** agree, or words.

**7. FF1 to FF6** (a record): the review found FF1 to FF3 and FF6 met in code. FF4 and FF5 are the brief's wording of the F2 cases. **Asked:** confirm as applied, closing the deferred row.

**8. The sequence** (recommended):
1. your answer;
2. the brief's revision 17, with "Stage B, correction B-C2": its items, owned paths, the earlier tests it is expected to change with their reasons (DD5; AM11-23's sweep), and its stop rule;
3. B-C2's prompt with its TypeSafe reading;
4. B-C2;
5. the manager's verification;
6. PR47's run and Codex on its head;
7. a bounded delta re-review of B-C2 against `470d97a`;
8. your pre-merge read (the CI policy paragraph, the data model, the contract texts, and any governing Markdown);
9. the merge.

Under (b) for #1, the re-review would read the `glow_chat` change in full. **Asked:** agree.

**9. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**

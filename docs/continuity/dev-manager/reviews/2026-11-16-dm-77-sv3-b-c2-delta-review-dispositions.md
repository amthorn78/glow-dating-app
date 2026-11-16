# DM-77 — SV3 Stage B: B-C2's delta re-review, before correction B-C3

- **From:** Dev Manager 5 (`session_01Q789u3CWg6s9pBGXerCQZt`), for App Manager 11, relayed by Nathan (OD-25).
- **Date:** 16 November 2026. Received about 04:11 UTC; finished about 04:25 UTC.
- **Read at:** `892bd59067cebb1a20f16b458e39637b52c45e99` of `claude/magical-wozniak-yfmmx2`, exported outside any worktree.
  - Its code equals `4860b56`'s: `git diff 4860b56 892bd59` is empty outside Markdown.
  - The governing diff since my last read (`e19f731`) is empty. The commits since are DM-76's merge and disposition, AM11-31, and the review's record.
- **Environment:** names only. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, or any `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name is set. The AWS names are present and were not read.
- **What I changed:** this file only, on `claude/dev-manager`. Notion was read, not changed. No call to Stream, a database, HDE, Railway or Cloudflare.
  - I downloaded the pinned psycopg 3.3.6 source distribution into my scratchpad, to read how it quotes values. Nothing from it was run.

## 1. The answers

| Item | Verdict |
|---|---|
| 1. F1, the `U&` sentence | **(a): the words follow the code.** My DM-75 words disagreed with their own test condition; B-C2 followed the test, which is the right rule (section 4; II1, II12, II13) |
| 2. F2, the `OF` list | **Agreed, the review's words.** DM-75 6.2 (d) is read with that exception (section 5; II2, II12, II14) |
| 3. F3 and S1 | **(a): correct both.** A statement that creates a function or a procedure fails whatever its lock, as `DO` does, and the own-objects check counts temporary schemas. A `dblink` query is stated (section 6; II3, II4, II9 to II11) |
| 4. F4, "as PostgreSQL reads it" | **Agreed,** in words that also cover the driver's statements (section 7; II1, II6, II7, II12) |
| 5. F5 | **Agreed, the fix,** with one condition: a join's `USING (…)` column list binds nothing (section 8) |
| 6. S2 | **(a): fail closed, with a wider test than the review's.** The rule reads a placeholder's neighbours on both sides, so it also catches a placeholder inside a dollar-quote tag (`$q%sx$`) (section 9) |
| 7. F6 | **Agreed, the fix,** with its negative tests and their reversal (section 10) |
| 8. Limits and nits | **Agreed,** with a `dblink` limit added. Words for N2 and N3 (section 11; II5, II8) |
| 9. The session's departures | **Accepted** (section 12) |
| 10. B-C3 and the next review | **Agreed.** B-C3's section and owned paths are II15 and II16. A bounded delta re-review follows (section 13) |
| 11. The sequence | **Agreed** (section 14) |
| 12. Notion | **Two stale lines.** The Branches bullet and the Mistakes log bullet were not moved with the status line at `892bd59` (section 15) |

## 2. What I read and checked

- **The record's sections:**
  - "Delta re-review of B-C2" (lines 2248 to 2278);
  - "Manager verification of B-C2";
  - "PR47 at `b0386f8`, and Codex's fifth finding";
  - the own-objects row (line 1552).
- **The code at `4860b56`:**
  - `row_locks.py`: its docstring, `OWN_OBJECTS` (lines 280-296), `judge` (453-485) and `_resolve`'s item reader and scan loop (540-700);
  - `interaction_cases.py`: `_Ledger` and `_as_a_client` (lines 1986-2090);
  - `UndoSelectionTests`;
  - migration 0011's `AddField` and `AddConstraint`;
  - the CI workflow's role statement (`NOSUPERUSER NOCREATEDB NOCREATEROLE`).
- **Reproduced with `row_locks.refusal`, loaded alone under `python3 -I`:**
  - a `U&` identifier spelling the account table is refused with `FOR UPDATE` and passes with `FOR NO KEY UPDATE` (F1);
  - `FOR SHARE OF "glow_persistence_appaccount"` beside a `FOR UPDATE OF` naming the match passes (F2);
  - a `CREATE FUNCTION` body (dollar-quoted) and a `CREATE PROCEDURE` body (`'…'`) taking `FOR UPDATE` on the account table each pass (S1);
  - S2's text passes, and so does its form with a named placeholder;
  - the plain control for F5 (an `OF` name bound twice, both plain) is refused. With the account table inside a parenthesised join, the appearance check refuses it, as the review says.
- **Forms of my own, for item 6:**
  - an `E` written before a placeholder passes D14, and so does a hyphen before one (with the rest of the text in a quoted span);
  - a quote before a placeholder is refused;
  - section 9 says why the first two cannot change a token in practice.
- **psycopg 3.3.6's quoting** (`psycopg/types/numeric.py`, `psycopg/adapt.py`):
  - a negative number is written with a space before it;
  - a string is written through libpq's `escape_literal`, which puts `E` and a space before a string that holds a backslash.
- **Notion:** Implementation Control's standing lines, the Dev Manager page's DM-76 and DM-77 rows, the register copy and the Work Register's SV3 and M08 rows (section 15).

## 3. My own errors in this round

Five of the review's findings are in my own DM-75 words.

- **F1:** my 6.2 (c) failed a `U&` statement whatever its lock, while my test condition passed each text with `FOR NO KEY UPDATE`, `DO` alone excepted. The two disagreed.
- **F2:** GG19 left out the `OF` list, which an existing test needs.
- **F4:** GG18 and GG16 said "as PostgreSQL reads it" without saying which text is read or the setting it assumes.
- **N2:** GG21's "about twice its threads" is false in the run of record.
- **N3:** GG25's migration note described the safe way without saying that 0011, as written, does the other.

Two more errors are my own:

- **S1:** my 6.2 (c) gave the `DO` rule's reason, a body that runs as code. That reason applies word for word to a function's or a procedure's body. I relied on the own-objects check without reading its schema filter, which excludes temporary schemas.
- **DM-76's list of governing changes after `854c214`** named the CI policy's and the register's but missed the manager workflow's two (`b67bae2`, `a919dea`), though my own `git log` showed both. The manager's AM11-31 found them.

The lesson I take is the one AM9-08 states: words for a check are tried against the code and the check's own test conditions before they are given.

## 4. Item 1 — F1, the `U&` sentence

- **(a): the words follow the code.**
  - The rule exists to catch `FOR UPDATE` on account rows. A `U&` identifier's escapes can spell the account table, so a statement holding one fails when it takes `FOR UPDATE`, which is what the code does.
  - Under `FOR NO KEY UPDATE` or a reader's lock there is nothing to catch, so failing it whatever its lock would add a refusal with no purpose.
  - (b) would also contradict DM-75's own test condition, which B-C2 followed.
- **The words:**
  - II1 for the README, B-C3's;
  - II12 for D14 in the brief, the manager's;
  - II13 for B-C2's item 4, a note that keeps what was asked and says what holds now.
  - The docstring already says it.

## 5. Item 2 — F2, the `OF` list

- **Agreed, the review's words.**
  - A name in a lock clause's `OF` list refers to a binding; it binds nothing.
  - A `FOR UPDATE OF` name is still resolved by its binding and refused if that binding is the account table.
  - A `FOR SHARE OF` the account table takes only a reader's lock on its rows.
- **DM-75 6.2 (d) is read with that exception,** and the record lists the reading among B-C2's, as B-C3's item 2 says.
- **The words:** II2 (README, B-C3's), II12 (brief) and II14 (B-C2's item 5, a note).

## 6. Item 3 — F3 and S1, function bodies and temporary schemas

- **(a): correct both.**
- **S1 is a regression, and my words caused it.**
  - `470d97a` refused a function body that takes `FOR UPDATE`; my item 4 masked it and excepted only `DO`.
  - The `DO` rule's reason (its body runs as code) is exactly a function's or a procedure's.
  - So a statement that creates a function or a procedure (`CREATE [OR REPLACE] FUNCTION` or `PROCEDURE`, the words read as PostgreSQL reads them) fails whatever its lock.
- **F3 is a check that claims more than it counts.**
  - Widening `OWN_OBJECTS`'s schema filter to exclude only `pg_catalog`, `information_schema`, the TOAST schemas and extensions makes temporary objects count.
  - Codex's P2 on `892bd59` asks the same, with a negative control.
- **Cost.**
  - No suite sends either form today (the manager's grep), so nothing that runs now is refused.
  - Both are a few lines of proof tooling.
  - Stating them as limits instead would leave a known path to an account row's `FOR UPDATE` with every statement passing.
- **What stays outside.**
  - A function, procedure, view or rule created through a path the record does not see, and gone before the check runs. That path is already among the stated limits.
  - A `dblink` query, a string the `dblink` extension runs as SQL on its own connection. Installing that extension needs a superuser, and the proof's role is created `NOSUPERUSER` (the workflow) and refused if it is a superuser (`run`). I state it (II4).
- **The tests:**
  - S1's planted bodies (dollar-quoted, `'…'` and `E'…'`) each fail, with `FOR NO KEY UPDATE` too;
  - an offline test pins `OWN_OBJECTS`'s schema filter;
  - a planted database reversal (a temporary function, view and rule in a case's session) shows the counts 1, 1, 1, run under D4's conditions and recorded as informational, as the other database reversals are.
- **The words:**
  - II3 and II4 for the README;
  - II9 for the record's row (line 1552);
  - II10 for the manager's sentence in "Manager verification of B-C2", a correction note;
  - II11 for `row_locks.py`'s docstring.

## 7. Item 4 — F4, "as PostgreSQL reads it"

- **Agreed,** with one change to the review's words. The record judges statements from two sources: Django's `execute`, and the driver's own methods (`stream`, `copy`, `callproc`, a `psycopg.connect` connection). So the words say "the text the record receives", not "the text Django's `execute` receives".
- **The words:**
  - II1 (README line 240), II6 (README line 19) and II7 (the P11 plan line 85) are B-C3's;
  - II12 is the brief's;
  - the docstring (lines 27-28 and 454) says the same, in the README's words.

## 8. Item 5 — F5, bindings the resolver does not read

- **Agreed, the fix.** These are read as bindings, none of them plain:
  - an item inside a parenthesised join;
  - an item of a `DELETE` or `MERGE` statement's `USING` list.

  So an `OF` name bound there fails, as bound twice or as not plain.
- **One condition:** a join's `USING (…)` is a column list and binds nothing. A test shows a `JOIN … USING (id)` statement is judged as before.
- **The tests:** each of the review's planted texts is a case, failing at B-C3's head and passing at `4860b56`.

## 9. Item 6 — S2, a placeholder glued to a name or a dollar sign

- **(a): fail closed, with a wider test than the review's.**
- **Why the review's test is too narrow.** Django's psycopg backend writes each value into the text before sending it (client-side binding). A value can complete a dollar-quote tag:
  - a number, `true`, `false` or `NULL` written into `$q%s$` makes `$q1$`;
  - the placeholder can sit anywhere in the tag, as in `$q%sx$`, where no `$` is beside it.

  So "a placeholder directly next to a `$`" misses forms, and "a statement that takes `FOR UPDATE`" cannot be judged on D14's reading, since that reading is what the bound text changes: S2's own lock is inside what D14 reads as a dollar quote.
- **The rule.** A statement fails, whatever D14 reads in it, when both hold:
  - its text holds the word `UPDATE` anywhere, spans and comments included;
  - it has a placeholder (`%s`, `%b`, `%t`, or a named one such as `%(name)s`) whose neighbour on either side is a name character (a letter, digit, underscore, dollar sign or non-ASCII character).
- **Why the other neighbours are safe:**
  - psycopg 3.3.6 writes a negative number with a space before it, so a hyphen cannot become `--`;
  - it writes a string through libpq's `escape_literal`, which puts `E` and a space before a string that holds a backslash, so a letter before a placeholder cannot change where a string ends;
  - a placeholder after a space, an opening parenthesis or a comma, or before `::`, passes, so Django's statements and the app's raw ones are unaffected.
- **Bound-statement judging is not required.** Judging the bound statement too, as Codex suggests, would be more precise. But it needs the driver's binding reproduced in the record (and psycopg's server-side form turns `%s` into `$1`), which is more than a correction needs.
- **The tests:**
  - S2's text and `$q%sx$` each fail at B-C3's head and pass at `4860b56`;
  - a no-key account lock with `= %s`, and a raw statement with `%(name)s::timestamptz`, pass.
- **The words:** II1 (README) and II12 (brief); the docstring says the same.

## 10. Item 7 — F6, B-C1's ledger

- **Agreed, the fix.**
  - In both of `_as_a_client`'s wrappers, `_Ledger.check` runs before `_Ledger.served_from` (today `served_from` comes first: lines 2069 and 2073, and 2080 and 2081).
  - `check` runs against the versions served before the command was sent, which also closes S5's concurrent direct answer.
- **The tests,** at the wrapper's level:
  - a route command and a direct command, each answering with an unserved version it sent, fail the ledger;
  - a read followed by a command passes;
  - the old order fails the first two.
- **S5's remainder is stated:** a `stale_version` refusal caused by the batch or pair, and a `not_found` after the version check, each accept an unserved version.

## 11. Item 8 — the other limits and the nits

- **Agreed:**
  - S3, S4, S5's remainder, N9 and N10 stated in the README's "Limits" and the record, and a `dblink` query with them (II4);
  - N1, N4, N5 and N6 in B-C3's records;
  - N7 and N8 as tests.
- **N2 and N3 in my words:**
  - II5 removes GG21's false ratio;
  - II8 says what migration 0011 does as written before saying what it must do on a populated target.

## 12. Item 9 — the session's departures

**Accepted.**

- The read-only `gh api` GET calls wrote nothing and printed no token.
- The `__pycache__` written into the scratch trees was removed and re-verified against `git archive`.
- The classification was repeated from the repository's root.

## 13. Item 10 — B-C3 and the next review

- **Agreed.**
- **B-C3's scope:** items 1 to 8 as ruled here, in the proof's tooling, cases, tests, README and records, and the P11 plan. Its only change in `services/api` is N8's test, so it adds no non-test line there.
- **The review:** a bounded delta re-review under C4's five classes and the exact-head review's classes. This is consistent with C4's, C5's and B-C2's: the proof's tooling is the harness the classes judge, and the changes answer review findings without a design change.
- **The earlier tests it changes:**
  - the fast-path agreement test (N7);
  - `UndoSelectionTests` (N8);
  - any test the manager's sweep finds pinning `OWN_OBJECTS`'s text, the ledger's order, or a statement the new rules refuse (AM11-23).
- **B-C3's section and owned paths:** II15 and II16.

## 14. Item 11 — the sequence

**Agreed:**

1. this answer;
2. the brief's revision 18, with II12 to II16;
3. B-C3's prompt after Codex's pass on the commit that holds it (PF02-R40, applied by the manager's practice);
4. B-C3 built, verified and integrated, with its run of record;
5. its bounded delta re-review;
6. my pre-merge read of PR47, confirming DM-75's and DM-77's texts as applied;
7. the merge, then M08's integration (DM-76).

Codex's two P2s on `892bd59` are S2 and F3. B-C3's items 6 and 3 answer them, and their threads are resolved after the review confirms.

## 15. Item 12 — Notion (read-only, at about 04:18 UTC)

| Page | What I compared | Result |
|---|---|---|
| Implementation Control | The status heading and stamp | **Match:** "16 November 2026 (App Manager 11; DM-77, then correction B-C3; M08 approved, waiting for PR47)", last matched at `892bd59`, the review's verdict as recorded |
| Implementation Control | The operating procedure's stamp | **Match:** `b192164`, moved from `854c214` with each move listed, the workflow's two included (AM11-31). No governing path changed after it |
| Implementation Control | "Next items"; "Main"; standing directions | **Match:** brief revision 17, DM-61's to DM-75's conditions; `947576d`, PR47 open; OD-01 to OD-66 |
| Implementation Control | "Branches" | **Mismatch:** still "listed … 02:29 UTC". It gives `claude/dev-manager` at `ab1520b` and the manager branch's heads only to `e19f731`. `git ls-remote` gives `claude/dev-manager` at `ccf1e5a` (DM-76's report, merged at `b192164`) and the manager branch at `892bd59`, after `b192164`, `973d8f7` and `3f2f72b` |
| Implementation Control | "Mistakes log" | **Mismatch:** "AM11-01 to AM11-30, at `e19f731`". At `892bd59` the log holds AM11-31 (added at `973d8f7`, completed at `3f2f72b`) |
| Dev Manager — reviews and approvals | DM-76's and DM-77's rows | **Match:** DM-76 considered, its answer and disposition columns as the review log's; DM-77 pending |
| Register copy | Rows | **Match:** 66 rows, OD-01 to OD-66 |
| Work Register `SV3`; `M08` | State, next action, evidence | **Match:** SV3 at DM-77 with evidence pinned at `892bd59`; M08 approved by DM-76, integration after PR47 |

The two mismatches are the status line moved without the bullets beside it: PF02-R11's rule, from AM10-08 and AM11-02.

## 16. The words

**II1 — the proof README, `proofs/postgres-ordering/README.md` (B-C3): D14's reading (F1, F4, S1, S2).**

> ```
> and judges each as PostgreSQL reads it (every comment, nested block comments included, and every string constant, dollar-quoted ones included, masked; a quoted identifier kept as a name; a statement with an unterminated span, a `DO` statement and a statement holding a `U&` quoted identifier failing) by the rule:
> ```

> ```
> and judges each as PostgreSQL reads the text the record receives, before psycopg writes its parameters into it, with `standard_conforming_strings` on (every comment, nested block comments included, and every string constant, dollar-quoted ones included, masked; a quoted identifier kept as a name; an unterminated span, a `DO` statement and a statement that creates a function or a procedure (the last two run a string as code) failing whatever its lock; a statement that holds a `U&` quoted identifier failing if it takes `FOR UPDATE`; and a statement whose text holds the word `UPDATE` anywhere and a placeholder glued to a name character or a dollar sign failing, since the value psycopg writes there can complete a dollar-quote tag) by the rule:
> ```

**II2 — the proof README, `proofs/postgres-ordering/README.md` (B-C3): D14's resolution (F2, F5).**

> ```
> and the account table appears only as a plain `FROM` or `JOIN` item's table or a column's qualifier (a name bound twice, a comma item, a schema-qualified name, `ONLY`, `*`, or the account table inside a sub-query fails; the exact-head review of Stage B's #4 and #5, each form planted; DM-75).
> ```

> ```
> and the account table appears only as a plain `FROM` or `JOIN` item's table, a column's qualifier, or a name in a lock clause's `OF` list, read as a reference (a `FOR UPDATE OF` name is still resolved by its binding) (a name bound twice, a binding inside a parenthesised join or in a `DELETE` or `MERGE` statement's `USING` list, a comma item, a schema-qualified name, `ONLY`, `*`, or the account table inside a sub-query fails; the exact-head review of Stage B's #4 and #5 and B-C2's delta re-review's F5, each form planted; DM-75, DM-77).
> ```

**II3 — the proof README, `proofs/postgres-ordering/README.md` (B-C3): the planted function (S1, F3).**

> ```
> a `CREATE FUNCTION` in that case fails it as a function of the database's own.
> ```

> ```
> a `CREATE FUNCTION` in that case fails it, as a statement that creates a function and as a function of the database's own; a temporary function, view and rule planted in a case's session each count (DM-77).
> ```

**II4 — the proof README, `proofs/postgres-ordering/README.md` (B-C3): the own-objects limit, and `dblink`.**

> ```
> a lock taken inside a database function a statement calls (none exists: the check counts the database's own functions, views and rules, each zero);
> ```

> ```
> a lock taken inside a database function, procedure, view or rule that a path the record does not see created, and that no longer exists when the check runs (a statement that creates a function or a procedure fails whatever its lock, and the check counts the functions, procedures, views and rules that exist when it runs, outside `pg_catalog`, `information_schema`, the TOAST schemas and extensions, temporary schemas included, each zero; DM-77); a `dblink` query, a string that extension runs as SQL on its own connection (installing it needs a superuser, and the proof's role is not one);
> ```

**II5 — the proof README, `proofs/postgres-ordering/README.md` (B-C3): the counts (N2).**

> ```
> Its counts of connections and threads are of distinct identities, which a closed connection's or an ended thread's successor may reuse, and it counts a connection's Django wrapper and its psycopg connection as two, so its connections are about twice its threads.
> ```

> ```
> Its counts of connections and threads are of distinct identities, which a closed connection's or an ended thread's successor may reuse, and it counts a connection's Django wrapper and its psycopg connection as two. Neither count bounds the other: a thread that opens connections in turn adds an identity for each (DM-77).
> ```

**II6 — the proof README, `proofs/postgres-ordering/README.md` (B-C3): the SV3 paragraph (F4).**

> ```
> and D14's rule reads a statement as PostgreSQL does and resolves `FOR UPDATE OF` by scope (the D14 entry below).
> ```

> ```
> and D14's rule reads the text the record receives as PostgreSQL would, before psycopg writes its parameters into it and with `standard_conforming_strings` on, and resolves `FOR UPDATE OF` by scope (the D14 entry below).
> ```

**II7 — the P11 plan, `docs/testing/p11-deferred-acceptance.md` (B-C3): B-C2's run line (F4).**

> ```
> undo one step, D14 read as PostgreSQL reads it; DM-75)
> ```

> ```
> undo one step, D14 reading the text the record receives as PostgreSQL would, before psycopg writes its parameters into it and with `standard_conforming_strings` on; DM-75, DM-77)
> ```

**II8 — the P11 plan, `docs/testing/p11-deferred-acceptance.md` (B-C3): migration 0011's note (N3).**

> ```
> A target that already holds directional rows backfills `decided_at` from each row's `updated_at`, its last write, not one instant for every row, which would restart every resurfacing waiting period and tie every member's rows, leaving undo's latest decision (D12) to the ID tie-break; and it adds the new CHECK constraints `NOT VALID`, then validates them (`VALIDATE CONSTRAINT`).
> ```

> ```
> As written, it backfills `decided_at` with one instant for every existing row (the field's default, read once when it runs) and validates its new CHECK constraints at once. One instant would restart every resurfacing waiting period and tie every member's rows, leaving undo's latest decision (D12) to the ID tie-break. So before it runs on a target that already holds directional rows, it is changed to backfill `decided_at` from each row's `updated_at`, its last write, and to add the new CHECK constraints `NOT VALID`, then validate them (`VALIDATE CONSTRAINT`) (DM-77).
> ```

**II9 — the record, `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md` (B-C3): the own-objects row (F3, S1).**

> ```
> closed by a check: the migrated database defines no function, procedure, view or rule of its own (`row_locks.OWN_OBJECTS`), each zero, or the suite fails
> ```

> ```
> closed by a rule and a check: a statement that creates a function or a procedure fails whatever its lock (B-C3; DM-77), and no function, procedure, view or rule exists when the check runs, outside `pg_catalog`, `information_schema`, the TOAST schemas and extensions, temporary schemas included since B-C3 (`row_locks.OWN_OBJECTS`), each zero, or the suite fails
> ```

**II10 — the record, `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md` (the manager's): its B-C2 verification.**

> ```
> No suite creates a function, and the own-objects check fails any that exists when it runs.
> ```

> ```
> No suite creates a function, and the own-objects check fails any that exists when it runs outside the `pg_` schemas; until B-C3 it did not count a temporary schema's objects (the delta re-review's F3; DM-77).
> ```

**II11 — `proofs/postgres-ordering/glow_ordering_proof/row_locks.py` (B-C3): its docstring's own-objects paragraph.**

> ```
> **The database's own objects:** a lock taken inside a database function, a view or a rule is not in
> any statement's text, so the check also counts the functions, procedures, views and rules the
> migrated database defines outside the system schemas and extensions; the suite fails unless each is
> zero (no migration defines one).
> ```

> ```
> **The database's own objects:** a lock taken inside a database function, a view or a rule is not in
> any statement's text, so a statement that creates a function or a procedure fails whatever its
> lock (its body, a string constant, runs as code; DM-77), and the check counts the functions,
> procedures, views and rules that exist when it runs outside ``pg_catalog``,
> ``information_schema``, the TOAST schemas and extensions, temporary schemas included; the suite
> fails unless each is zero (no migration defines one).
> ```

**II12 — the brief, `docs/planning/sv3-eligibility-discovery-interactions.md` (yours, revision 18): D14's rule.**

> ```
> It reads a statement as PostgreSQL does: every comment (nested block comments included) and every string constant (dollar-quoted ones included) is masked before it judges, a quoted identifier stays a name, and a statement with an unterminated span, a `DO` statement (its body runs as code) and a statement holding a `U&` quoted identifier fail. An `OF` name counts only where the statement binds it once, in any scope, as a table named in a plain `FROM` or `JOIN` item or that item's alias, and the account table appears only as such an item's table or a column's qualifier; any other form fails: a name bound twice, a comma item, a schema-qualified name, `ONLY`, `*`, a sub-query's or a function's alias, or the account table inside a sub-query (the exact-head review of Stage B, #4 and #5; DM-75).
> ```

> ```
> It reads a statement as PostgreSQL reads the text the record receives, before psycopg writes its parameters into it, with `standard_conforming_strings` on: every comment (nested block comments included) and every string constant (dollar-quoted ones included) is masked before it judges, and a quoted identifier stays a name. An unterminated span, a `DO` statement and a statement that creates a function or a procedure (the last two run a string as code) fail whatever their lock; a statement holding a `U&` quoted identifier fails if it takes `FOR UPDATE`; and a statement whose text holds the word `UPDATE` anywhere and a placeholder glued to a name character or a dollar sign fails, since the value psycopg writes there can complete a dollar-quote tag. An `OF` name counts only where the statement binds it once, in any scope, as a table named in a plain `FROM` or `JOIN` item or that item's alias, and the account table appears only as such an item's table, a column's qualifier, or a name in a lock clause's `OF` list, read as a reference (a `FOR UPDATE OF` name is still resolved by its binding); any other form fails: a name bound twice, a binding inside a parenthesised join or in a `DELETE` or `MERGE` statement's `USING` list, a comma item, a schema-qualified name, `ONLY`, `*`, a sub-query's or a function's alias, or the account table inside a sub-query (the exact-head review of Stage B, #4 and #5; DM-75; B-C2's delta re-review, F1, F2, F4, F5, S1 and S2; DM-77).
> ```

**II13 — the brief, `docs/planning/sv3-eligibility-discovery-interactions.md` (yours, revision 18): a note on B-C2's item 4.**

> ```
> and "Comments are read as spaces" gives way to these words.
> ```

> ```
> and "Comments are read as spaces" gives way to these words. (DM-77: this item's "a statement holding a `U&` quoted identifier" and its test condition disagreed; B-C2 followed the test, so such a statement fails if it takes `FOR UPDATE`, as D14's words now say.)
> ```

**II14 — the brief, `docs/planning/sv3-eligibility-discovery-interactions.md` (yours, revision 18): a note on B-C2's item 5.**

> ```
> The review's scope example and one planted example of each form fail at B-C2's head; each that passes at `470d97a` is shown passing there.
> ```

> ```
> The review's scope example and one planted example of each form fail at B-C2's head; each that passes at `470d97a` is shown passing there. (DM-77: a name in a lock clause's `OF` list is read as a reference, as a qualifier is; B-C3 also reads a binding inside a parenthesised join or a `DELETE` or `MERGE` statement's `USING` list.)
> ```

**II15 — the brief, `docs/planning/sv3-eligibility-discovery-interactions.md` (yours, revision 18): "Stage B, correction B-C3", before "Sessions".**

> ```
> The Dev Manager's pre-merge read follows.
>
> ## Sessions
> ```

> ```
> The Dev Manager's pre-merge read follows.
>
> ## Stage B, correction B-C3 (B-C2's delta re-review; DM-77)
>
> B-C3 answers B-C2's bounded delta re-review of `4860b56` (the record, "Delta re-review of B-C2"): changes required, narrowly, no blocking finding. It changes no model, migration, lock, version check, existing DTO, stale body, `glow_chat` writer, lock-scan rule or bound, contract package, workflow or dependency, and no non-test line in `services/api`.
>
> 1. **The `U&` sentence (F1).** The words follow the code: a statement holding a `U&` quoted identifier fails if it takes `FOR UPDATE`. The proof README's D14 entry says so (DM-77's II1).
> 2. **The `OF` list as a reference (F2).** The account table may also appear as a name in a lock clause's `OF` list, read as a reference; a `FOR UPDATE OF` name is still resolved by its binding. The README says so (DM-77's II2), and the record lists the reading among B-C2's.
> 3. **Function bodies and temporary schemas (S1, F3).** A statement that creates a function or a procedure (`CREATE [OR REPLACE] FUNCTION` or `PROCEDURE`, the words read as PostgreSQL reads them) fails whatever its lock, as a `DO` statement does: its body, a string constant, runs as code. `OWN_OBJECTS` excludes only `pg_catalog`, `information_schema`, the TOAST schemas and extensions, so a temporary schema's objects count. Tests: S1's planted bodies (dollar-quoted, `'…'` and `E'…'`) each fail, with `FOR NO KEY UPDATE` too; an offline test pins the query's schema filter; a planted database reversal (a temporary function, view and rule in a case's session) shows the counts 1, 1, 1 under D4's conditions, informational. The README, `row_locks.py`'s docstring and the record say what the check counts (DM-77's II3, II4, II9 and II11).
> 4. **The reading's qualification (F4).** The README's D14 entry and SV3 paragraph, `row_locks.py`'s docstring and the P11 plan's B-C2 line say D14 reads the text the record receives as PostgreSQL would, before psycopg writes its parameters into it, with `standard_conforming_strings` on (DM-77's II1, II6 and II7).
> 5. **Bindings the resolver did not read (F5).** An item inside a parenthesised join, and an item of a `DELETE` or `MERGE` statement's `USING` list, are read as bindings, none of them plain, so an `OF` name bound there fails; a join's `USING (…)` column list binds nothing, and a `JOIN … USING (id)` statement is judged as before. The review's planted texts are each a case, failing at B-C3's head and passing at `4860b56`.
> 6. **A placeholder glued to a name or a dollar sign (S2).** A statement whose text holds the word `UPDATE` anywhere (spans and comments included) and a placeholder (`%s`, `%b`, `%t`, or a named one such as `%(name)s`) whose neighbour on either side is a name character (a letter, digit, underscore, dollar sign or non-ASCII character) fails, whatever D14 reads in it: psycopg writes the value there, and a number, `true`, `false` or `NULL` can complete a dollar-quote tag. S2's text and `$q%sx$` each fail at B-C3's head and pass at `4860b56`; a no-key account lock with `= %s`, and a statement with `%(name)s::timestamptz`, pass.
> 7. **B-C1's ledger (F6).** In both of `_as_a_client`'s wrappers, `_Ledger.check` runs before `_Ledger.served_from`, against the versions served before the command was sent. A test at the wrapper's level shows that a route command and a direct command, each answering with an unserved version it sent, fail the ledger, while a read followed by a command passes; the old order fails the first two.
> 8. **The stated limits and the records.** In the README's "Limits" and the record: S3 (`standard_conforming_strings = off`), S4 (a placeholder against its lock clause; SQL inside a parameter's value), S5's remainder (a `stale_version` refusal caused by the batch or pair, or a `not_found` after the version check), N9, N10, and a `dblink` query (DM-77's II4). Records: N1, N4, N5 and N6; N2 and N3 in DM-77's words (II5, II8); the manager's own-objects sentence (II10).
> 9. **Tests (N7, N8):** a `--` statement in the fast-path agreement test; `UndoSelectionTests` pins undo's `raise` as well as its `if`.
> 10. **The earlier tests it changes** (DD5; AM11-23's sweep), each named in its prompt with its reason: the fast-path agreement test (item 9), `UndoSelectionTests` (item 9), and any test the sweep finds pinning `OWN_OBJECTS`'s text, the ledger's order, or a statement items 3, 5 and 6 refuse. Any other earlier test that no longer passes is a stop.
>
> **The stop rule (B-C3):** stop and report if B-C3 needs a change outside its owned paths, or to a model, a migration, a lock, a version check, an existing DTO, D8's single stale body, a `glow_chat` writer, the lock scan's rules or B0's bound, the contract package, the workflow, a dependency or a non-test line in `services/api`; if a statement any suite sends fails D14's corrected rule; or if a case other than those item 10 names changes its verdict.
>
> **B-C3's run of record:** a push run on its code head, with all eight jobs passing, the discovery suite 66/66, and each suite's D14 record `PASS` with none refused and its own-objects counts 0, 0, 0, read from GitHub.
>
> **The review:** a bounded delta re-review of B-C3 against `4860b56` (M05 S2; DM-77), after the manager's verification, PR47's run and Codex on its head, under C4's five classes and the exact-head review's classes. It reads every path B-C3 touches as it stands at its head, plants S1's bodies, S2's forms and F5's texts against D14's rule, runs F6's tests and their reversal, and checks the temporary-schema count. The Dev Manager's pre-merge read of PR47 follows.
>
> ## Sessions
> ```

**II16 — the brief, `docs/planning/sv3-eligibility-discovery-interactions.md` (yours, revision 18): B-C3's owned paths.**

> ```
> Nothing else changes in B-C2.
> ```

> ```
> Nothing else changes in B-C2.
> - **Correction B-C3 only** (DM-77): in the proof, `row_locks.py` (the creation rule, the placeholder rule, the bindings F5 names, `OWN_OBJECTS`'s schema filter and its docstring) and its offline tests, `interaction_cases.py` (the ledger's two wrappers and N5's detail line), and the proof's offline tests, new files included, for the ledger's test; in `services/api/tests/`, `UndoSelectionTests` only (N8); the proof README's D14 entry, SV3 paragraph and "Limits"; the P11 plan's B-C2 line, migration 0011's note and its runs of record; and the evidence record. Nothing else changes in B-C3.
> ```

## 17. Who applies what

| Words | Where | Who |
|---|---|---|
| II12 to II16 | The brief, as revision 18 | The manager |
| II10 | The record's "Manager verification of B-C2" | The manager, with revision 18 |
| II1 to II6, II9, II11 | The proof README, the record, `row_locks.py` | B-C3 |
| II7, II8 | The P11 plan | B-C3 |
| The Branches and Mistakes log bullets | Notion | The manager's next sync |

Status: complete

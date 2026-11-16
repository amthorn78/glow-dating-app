# DM-78 — SV3 Stage B: B-C3's delta re-review, before correction B-C4

- **From:** Dev Manager 5 (`session_01Q789u3CWg6s9pBGXerCQZt`), for App Manager 11, relayed by Nathan (OD-25).
- **Date:** 16 November 2026. DM-78's own message did not reach this session. Only its addition did (Codex on `4c2f918`), at about 15:20 UTC. I answered DM-78 from its file at `4c2f918`, the commit the addition names. Finished about 16:00 UTC.
- **Read at:** `4c2f9188b63fff181a7f3555f9f3c56b45f76ad3` of `claude/magical-wozniak-yfmmx2`, exported outside any worktree.
  - Its code equals `edc883e`'s: `git diff edc883e 4c2f918` is empty outside Markdown.
  - The governing diff since my last read (`892bd59`) is empty. The commits since are DM-77's merge and disposition, B-C3 and its verification, and the review's record with DM-78.
- **Environment:** names only. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, or any `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name is set. The AWS names are present and were not read.
- **What I changed:** this file only, on `claude/dev-manager`. Notion was read, not changed. No call to Stream, a database, HDE, Railway or Cloudflare.
  - A prototype of the rules below lives in my scratchpad and is not committed. It loads `row_locks.py` from the export under `python3 -I`.
  - psycopg 3.3.6's source distribution, already in my scratchpad, was read again and not run.

## 1. The answers

| Item | Verdict |
|---|---|
| 1. F1, a name holding `(` | **Agreed, the fix:** placeholders are read as psycopg 3.3.6 reads them (section 4; JJ3, JJ11, JJ12) |
| 2. F5, a placeholder beside a quote | **(a), wider than the neighbour set:** a placeholder any part of which lies inside a string constant, a quoted identifier or a comment fails, whatever the statement holds. S4 is rewritten (section 5; JJ3, JJ7, JJ8, JJ12) |
| 3. F4, with Codex's (c) | **(a) for views, and (c) as well. Neither is enough alone.** A statement that creates a view fails whatever its lock. With the models' tables given, a statement that takes `FOR UPDATE` without naming the account table fails unless every relation name it reads is one of them. `PREPARE` needs no rule of its own. The negative control covers creation, use and removal (section 6; JJ1, JJ3 to JJ6, JJ10, JJ12 to JJ14) |
| 4. F2 and F3 | **(a), the fix.** `excluded` is stated (section 7; JJ4, JJ9, JJ13) |
| 5. N1 to N3 | **Agreed** (section 8; JJ10) |
| 6. The Docker daemon | **Accepted,** and the line for later prompts agreed (section 9) |
| 7. The freeze | **(a), frozen from B-C4's head.** B-C4's review is the last under all five classes, and its own class 2 findings become stated limits (section 10; JJ13, JJ14) |
| 8. B-C4 and its review | **Agreed.** Its section and owned paths are JJ14 and JJ15 (section 11) |
| 9. The sequence | **Agreed** (section 12) |
| 10. Notion | **Matches** at `4c2f918` (section 13) |

## 2. What I read and checked

- **The consultation's file** at `4c2f918`, and the addition.
- **The record:**
  - "Delta re-review of B-C3" (lines 2389 to 2419);
  - B-C3's account of its placeholder rule (line 2207).
- **The code at `edc883e`** (`row_locks.py`):
  - its docstring;
  - the lexer and the placeholder pattern (lines 125 to 171);
  - `_glued_placeholder`, `_creates_routine` and `judge` (492 to 570);
  - `_resolve` (592 to 860);
  - `RowLockRecord.note`, `_model_tables` and `model_tables()`.
- **psycopg 3.3.6's `_re_placeholder` and `_split_query`** (`psycopg/_queries.py`).
- **Reproduced with `row_locks.refusal`,** loaded alone under `python3 -I`, with a set of model tables given. Each of these returns `None`:
  - F1's two texts (the `%(n)s` control is refused);
  - F4's `CREATE TEMP VIEW`, its `SELECT id FROM v FOR UPDATE`, its `DROP VIEW` and `PREPARE p AS SELECT id FROM v FOR UPDATE`;
  - F5's text;
  - my own forms: `"%s"`, `'a %s b'`, `-- %s`, `/* %s */`, `$$ %s $$` and `E'%s'`;
  - a temporary view named like a model table, and a `FOR UPDATE` through that name.
- **The prototype of DM-78's rules** refuses:
  - F1's texts;
  - F5 and each span form, including a placeholder name that holds a quote or `--`;
  - F4's creation and its lock, the `public` view with `FOR UPDATE OF v2`, and the `PREPARE`;
  - a `TABLE` command, and a schema-qualified relation.

  It passes:
  - a `%%` inside a string constant, and a placeholder glued to a closing quote outside it;
  - Django's statement shapes;
  - a `FOR UPDATE` with no `OF` list on models' tables;
  - F4's `DROP VIEW` and `EXECUTE`.

  I could evaluate 199 complete statement texts in the offline test module statically (five f-strings I could not). Judged with and without model tables, the prototype changes none of their verdicts.
- **A sweep of non-test code** (`services/api` and the proof):
  - none of its 925 SQL-like plain string constants holds a placeholder inside a span or creates a view; the only two hits are module docstrings. An f-string or a joined text was not swept;
  - every `select_for_update()` call is on a model;
  - no raw SQL text takes `FOR UPDATE`. The reversals that do are planted locally, not committed.
- **Notion:** section 13.

## 3. My own errors in this round

Two of the review's findings rest on my own DM-77 reasoning.

- **F5:** DM-77's section 9 ("Why the other neighbours are safe") considered a placeholder's neighbours outside a span only. A placeholder inside a span lets the quotes and text psycopg writes end that span. So value-borne SQL passes whether or not the text holds `UPDATE`. Each of my span forms above passes at `edc883e`. The S4 sentence that followed from my rule implied otherwise.
- **F4:** DM-77's section 6 ("What stays outside") named only objects created through a path the record does not see. I reasoned about a lock taken inside an object, not a lock taken through one. A lock-free view created through a path the record does see, then used with `FOR UPDATE`, escaped too. II4 carried that premise.

The lesson: AM9-08's check of words against the code is not enough for a rule I call safe. I also plant the forms the words call safe. This round, each ruling below was tried on the prototype first.

## 4. Item 1 — F1, a named placeholder whose name holds `(`

- **Agreed, the fix.**
- **What psycopg 3.3.6 reads as a placeholder.** `_re_placeholder` reads `%`, then either a name in parentheses followed by one character, or any one character. The name is one or more characters other than `)`.
  - `_split_query` accepts only `s`, `b` and `t` as that character, and reads `%%` as a literal percent sign.
  - So D14's pattern becomes, for example, `%%|%\([^)]+\)[sbt]|%[sbt]`, matched over the whole text in order, as psycopg scans it.
- **Both placeholder tests use this reading:** item 6's glued test, and item 2's span test.
- **On the prototype,** the pattern refuses F1's two texts and still refuses the control.
- **The record's line 2207** describes B-C3's rule as reading every named placeholder. JJ11 adds the note.
- **The words:** JJ3 and JJ11 are B-C4's; JJ12 is yours.

## 5. Item 2 — F5, a placeholder beside a quote

- **(a), but the rule tests the span, not the neighbour.** Adding the quotes to the neighbour set catches `'%s'` and `"%s"` only. A placeholder anywhere inside a span does the same harm, and each of my span forms passes at `edc883e`.
- **Why each span form is harmful.** psycopg writes a string value with its own quotes, and doubles any quote inside it.
  - Inside a string constant, those quotes end the constant, so the value's text after them is SQL: F5's `''FOR UPDATE --''`.
  - Inside a quoted identifier, a value holding `"` ends it.
  - Inside a line comment, a value holding a line end ends it.
  - Inside a block comment, a value holding `*/` ends it.
  - Inside a dollar-quoted string, a value holding its tag ends it.
- **The rule.** A statement with a placeholder any part of which lies inside a span fails, whatever its lock or text.
  - The value brings its own text, so the `UPDATE` condition that keeps the glued test narrow cannot apply here.
  - The test runs before the fast path, as the glued test does: a statement whose only spans are quoted identifiers takes the fast path.
- **"Any part" also covers a name that holds a quote or a comment mark** (`%(a'b)s`).
  - psycopg removes the whole placeholder, name included. A span that D14 reads as opening inside a name does not exist after binding.
  - So any overlap with a span fails.
- **Cost.** Django never writes a placeholder inside a span, and my sweep of non-test code found none. A `%%` inside a constant is a literal percent sign, and passes.
- **Outside every span, a value is a constant.**
  - psycopg writes a number as a numeric constant, with a space before a minus sign.
  - It writes `true`, `false` and `NULL` as they are.
  - It writes anything else as one quoted string constant, perhaps with a cast, and puts `E` and a space before it when the string holds a backslash.
  - So where a placeholder is outside every span and glued to no name character or dollar sign, no SQL in its value reaches PostgreSQL as SQL, with S3's setting.
  - A placeholder glued to a closing quote outside the constant (`'a'%s`) only joins two constants into one, and passes.
- **S4's new words say this** (JJ8).
- **The words:** JJ3 and JJ8 are B-C4's; JJ12 is yours. JJ7 cites F5 in the "Limits" bullet's heading.

## 6. Item 3 — F4, with Codex's (c)

- **(a) for views, and (c) as well.** Neither is enough alone.
- **(c) alone misses a temporary view named like a model table.**
  - PostgreSQL looks for a relation in the session's temporary schema first.
  - So after `CREATE TEMP VIEW glow_persistence_match AS SELECT id FROM glow_persistence_appaccount`, a `SELECT id FROM glow_persistence_match FOR UPDATE` reaches the account row through one of the models' table names.
  - (c) passes that lock; (a) refuses the view's creation.
  - This is reasoned from PostgreSQL's documented search order, not run.
- **(a) alone misses a relation outside the models that reached the statement another way:**
  - a view that a path the record does not see created, used with `FOR UPDATE`, then dropped before the check;
  - the account table renamed by an `ALTER TABLE … RENAME`, which D14 judges on that statement's own text.

  (c) refuses the lock in each case.
- **What (c) reads.** Unlike D14's other rules, (c) does not fail closed by construction: a relation in a position the resolution does not read would escape it. So its words name what it reads:
  - every `FROM`, `JOIN`, `USING`-list, `INTO`, `UPDATE` and `DELETE FROM` item, in any scope, including a `WITH` query's name read as one;
  - each name must be written without a schema;
  - a `TABLE` command fails, since the resolution does not read one as an item;
  - parentheses it cannot read fail;
  - a function's and a sub-query's own relations are read in turn. A function cannot be locked, and its body is covered by the creation rule and the count.
- **Cost.**
  - Every `FOR UPDATE` a suite sends is Django's `select_for_update()` on a model's table.
  - Such a statement with no `OF` list passes (c), on the prototype.
  - Among the offline tests' texts, (c) changes no verdict.
  - The run of record shows the rest. A refusal there is B-C4's stop.
- **`PREPARE` needs no rule of its own.**
  - Its body is in the text D14 reads (the review's focus points), so `PREPARE p AS SELECT id FROM v FOR UPDATE` is judged as any statement is, and (c) refuses it.
  - The review's `PREPARE` path is a lock-free view's, which (a) refuses at the view's creation.
  - `EXECUTE` carries no lock clause of its own.
- **What remains is stated (JJ6):**
  - a lock through a model table's name that refers to another relation when the lock runs:
    - a view of that name that a path the record does not see created;
    - the account table renamed to that name;
    - a table of that name of which the account table was made a child (`ALTER TABLE … INHERIT`, `ATTACH PARTITION`);
  - a statement sent before Django's registry is ready, which is judged without the models' tables.

  Each of these needs a schema change before the lock, and D14 judges each statement on its own text.
- **The negative control (Codex's request):**
  - offline: a record given the models' tables is fed `CREATE TEMP VIEW v AS SELECT id FROM glow_persistence_appaccount`, `SELECT id FROM v FOR UPDATE` and `DROP VIEW v`, in that order. It refuses the first two and passes the third;
  - the `public` view with `FOR UPDATE OF v2` and the `PREPARE` are refused;
  - a planted database reversal (the three statements in a case's session) shows the record failing at the view's creation and at the lock, with the own-objects counts 0, 0, 0 after the drop. It runs under D4's conditions and is informational.
- **The words:** JJ1, JJ3 to JJ6 and JJ10 are B-C4's; JJ12 to JJ14 are yours.

## 7. Item 4 — F2 and F3, two bindings, and `excluded`

- **(a), the fix.** B-C4's review is the last under all five classes, so this is the place to make "a name bound twice" true for both forms.
  - Neither form takes an account lock (17.11). The only question is the cost of reading them, and it is small:
    - a `MERGE INTO` target reads an alias as a `FROM` item's does (`USING`, a reserved word, ends it);
    - a join's `USING (…)` followed by `AS name` binds that name, to no table.
- **`excluded` is stated (JJ9).**
  - `INSERT … ON CONFLICT … DO UPDATE` gives the proposed row that name, but no token in the text binds it.
  - A lock clause names only its own query's `FROM` items, so none can name the proposed row.
  - An `OF` name spelled `excluded` is resolved by its other bindings, as PostgreSQL resolves it.
- **The words:** JJ4 and JJ9 are B-C4's; JJ13 is yours.

## 8. Item 5 — the nits

- **Agreed:**
  - N1: a test text whose placeholder's only glued neighbour is `$`. It fails with `$` removed from the name characters.
  - N2: a test that pins a `JOIN` item inside a `USING` list as not plain. It fails with the final pass removed.
  - N3: the docstring's "What it does not see" loses "a placeholder against its lock clause". JJ10 gives the paragraph's end, with the new limits.

## 9. Item 6 — the reviewer's Docker daemon

- **Accepted.** The daemon was stopped before any pull or run, and no value was read.
- **The line is agreed as written,** for every later prompt that allows a local database run: "start the Docker daemon under `env -i`, with only `PATH`, `HOME` and the proxy's names".
- **B-C4's prompt needs it,** since item 3's planted reversal runs on a local database.

## 10. Item 7 — D14's rules after B-C4

- **(a): frozen from B-C4's head.**
- **Why:**
  - Three reviews in a row each found the next form, and each correction widened the rules.
  - B-C3's real `FOR UPDATE` findings (F1, F4, F5) are all forms no suite sends, found by planting.
  - The record exists for the statements the suites send, and class 1 keeps those whole.
- **The one open point in 7 (a): may B-C4's own review still change a rule for class 2? I rule no.**
  - B-C4's review reports under all five classes, the last review to do so.
  - Its class 2 findings are recorded as stated limits, and the rule's words are narrowed to match.
  - Class 1 defects and regressions are corrected.
  - A test that passes where it should fail (class 4) and a record that claims more than D14 does (class 5) are corrected as before.
  - Otherwise one more correction round reopens the cycle the freeze closes.
  - A small fix can still come "by a design the Dev Manager reads".
- **The words follow DM-68's for the lock scan,** with D14's class 1:
  - in "B-C4's review, and how D14's line ends" (JJ14);
  - with a pointer in D14's rule (JJ13).

## 11. Item 8 — B-C4 and its review

- **Agreed.** B-C4's section and owned paths are JJ14 and JJ15.
- **Beyond the consultation's scope, B-C4 also has:**
  - the fast path's creation test, which must read `VIEW`, since a view's creation with no span passes it today;
  - the negative control (item 3);
  - the run's duration in its run of record, since the span test lexes more statements.
- **Nothing changes in `services/api` or the ledger.**
- **The review is a bounded delta re-review against `edc883e`.**

## 12. Item 9 — the sequence

- **Agreed.** Two notes:
  - Codex's thread on `4c2f918` (r4587204267) is answered at B-C4's head; S2's thread (r4581883081) is answered with F1. Both are resolved after B-C4's review confirms them.
  - The Docker line goes into B-C4's prompt and its review's prompt.

## 13. Item 10 — Notion (read-only, at about 15:29 UTC)

| Page | What I compared | Result |
|---|---|---|
| Implementation Control, status | Last matched at `4c2f918`, with B-C3's review and DM-78 | **Match** |
| Its Branches bullet | Eight branches and their heads, against `git ls-remote` now | **Match** |
| Its Mistakes log bullet | AM11-01 to AM11-31, at `b67d9e3`; the log has not changed since | **Match** |
| Its procedure summary | The stamp at `b192164`; no governing change since | **Match** |
| Dev Manager page, `DM-77` and `DM-78` | DM-77 answered and considered; DM-78 pending, at `4c2f918` | **Match** |
| The register copy | Matched at `e19f731`, OD-66 last; the register has not changed since | **Match** |
| Work Register, `SV3` and `M08` | SV3 at DM-78, evidence pinned at `4c2f918`; M08 approved, integrated after PR47 | **Match** |

Codex's finding (14:46 UTC) came after the sync at `4c2f918`. The manager records it at its next push, as the addition says.

## 14. The words

**JJ1 — the proof README, `proofs/postgres-ordering/README.md` (B-C4): the SV3 paragraph's every-suite sentence (F4, Codex).**

> ```
> the suite fails if a statement takes `FOR UPDATE` and names the account table, unless every such clause is `FOR UPDATE OF` other tables only, or if a function, procedure, view or rule exists outside the system schemas when it runs (temporary schemas counted since B-C3);
> ```

> ```
> the suite fails if a statement takes `FOR UPDATE` and names the account table, unless every such clause is `FOR UPDATE OF` other tables only, if a statement takes `FOR UPDATE` through a name that is not one of the models' tables (since B-C4), or if a function, procedure, view or rule exists outside the system schemas when it runs (temporary schemas counted since B-C3);
> ```

**JJ2 — the proof README, `proofs/postgres-ordering/README.md` (B-C4): the SV3 paragraph's B-C4 sentence.**

> ```
> and `_Ledger` checks each command's version against the versions served before it was sent, before it records the command's answer (the D14 entry and "Limits" below).
> ```

> ```
> and `_Ledger` checks each command's version against the versions served before it was sent, before it records the command's answer (the D14 entry and "Limits" below). **Correction B-C4** (B-C3's delta re-review; DM-78) adds no case, 66 in all: D14 reads a placeholder as psycopg reads it, a name holding `(` included, and fails a statement with a placeholder inside a string constant, a quoted identifier or a comment, whatever it holds; it fails a statement that creates a view, whatever its lock, and a statement that takes `FOR UPDATE` through a name that is not one of the models' tables, whatever else it names; and it reads a `MERGE INTO` target's alias written without `AS`, and a join's `USING (…) AS` alias, as bindings, none of them plain (the D14 entry and "Limits" below).
> ```

**JJ3 — the proof README, `proofs/postgres-ordering/README.md` (B-C4): D14's reading (F1, F4, F5).**

> ```
> an unterminated span, a `DO` statement and a statement that creates a function or a procedure (the last two run a string as code) failing whatever its lock; a statement that holds a `U&` quoted identifier failing if it takes `FOR UPDATE`; and a statement whose text holds the word `UPDATE` anywhere and a placeholder glued to a name character or a dollar sign failing, since the value psycopg writes there can complete a dollar-quote tag)
> ```

> ```
> an unterminated span, a `DO` statement, a statement that creates a function or a procedure (the last two run a string as code) and a statement that creates a view (`CREATE [OR REPLACE] [TEMP | TEMPORARY] [RECURSIVE] VIEW` or `CREATE MATERIALIZED VIEW`, since a lock through a view reaches a table it does not name) failing whatever its lock; a statement that holds a `U&` quoted identifier failing if it takes `FOR UPDATE`; and, each placeholder read as psycopg 3.3.6 reads one (`%s`, `%b` or `%t`, or `%(name)s`, `%(name)b` or `%(name)t` with a name of one or more characters other than `)`, `%%` being a literal percent sign), a statement with a placeholder any part of which lies inside a string constant (dollar-quoted ones included), a quoted identifier or a comment failing whatever its lock or text, since the quotes and text psycopg writes there can end that span, and a statement whose text holds the word `UPDATE` anywhere and a placeholder glued to a name character or a dollar sign failing, since the value psycopg writes there can complete a dollar-quote tag; B-C3's delta re-review's F1, F4 and F5, DM-78)
> ```

**JJ4 — the proof README, `proofs/postgres-ordering/README.md` (B-C4): D14's resolution, and the relations check (F2, F3, F4, Codex).**

> ```
> (a name bound twice, a binding inside a parenthesised join or in a `DELETE` or `MERGE` statement's `USING` list, a comma item, a schema-qualified name, `ONLY`, `*`, or the account table inside a sub-query fails; the exact-head review of Stage B's #4 and #5 and B-C2's delta re-review's F5, each form planted; DM-75, DM-77).
> ```

> ```
> (a name bound twice, a binding inside a parenthesised join, in a `DELETE` or `MERGE` statement's `USING` list, as a `MERGE INTO` target's alias (with or without `AS`) or as a join's `USING (…) AS` alias, a comma item, a schema-qualified name, `ONLY`, `*`, or the account table inside a sub-query fails; the exact-head review of Stage B's #4 and #5, B-C2's delta re-review's F5 and B-C3's delta re-review's F2 and F3, each form planted; DM-75, DM-77, DM-78). With the models' tables given (as Django's registry lists them, once it is ready), a statement that takes `FOR UPDATE` and does not name the account table fails too unless every relation name it reads, in any scope (each `FROM`, `JOIN`, `USING`-list, `INTO`, `UPDATE` and `DELETE FROM` item, a `WITH` query's name read as one included), is one of those tables, written without a schema; a `TABLE` command, or parentheses it cannot read, fail it as well. So a `FOR UPDATE` through a name that is not one of the models' tables fails, whatever else the statement names (Codex on `4c2f918`; DM-78); a model table's name that refers to another relation is under what it does not see, below.
> ```

**JJ5 — the proof README, `proofs/postgres-ordering/README.md` (B-C4): the negative control (F4, Codex).**

> ```
> a temporary function, view and rule planted in a case's session each count (DM-77).
> ```

> ```
> a temporary function, view and rule planted in a case's session each count (DM-77); and a temporary view over the account table planted in a case's session, a `SELECT … FOR UPDATE` from it and its `DROP VIEW` fail the check twice, at the view's creation and at the lock, though the own-objects counts read 0, 0, 0 after the drop (Codex on `4c2f918`; DM-78).
> ```

**JJ6 — the proof README, `proofs/postgres-ordering/README.md` (B-C4): what it does not see (F4).**

> ```
> a lock taken inside a database function, procedure, view or rule that a path the record does not see created, and that no longer exists when the check runs (a statement that creates a function or a procedure fails whatever its lock, and the check counts the functions, procedures, views and rules that exist when it runs, outside `pg_catalog`, `information_schema`, the TOAST schemas and extensions, temporary schemas included, each zero; DM-77);
> ```

> ```
> a lock taken inside a database function, procedure, view or rule that a path the record does not see created, and that no longer exists when the check runs (a statement that creates a function, a procedure or a view fails whatever its lock, and the check counts the functions, procedures, views and rules that exist when it runs, outside `pg_catalog`, `information_schema`, the TOAST schemas and extensions, temporary schemas included, each zero; DM-77, DM-78); a lock through a model table's name that refers to another relation when the lock runs: a view of that name that such a path created (PostgreSQL looks in the session's temporary schema first, so a temporary one hides the table), the account table renamed to that name, or a table of that name of which the account table was made a child (`ALTER TABLE … INHERIT`, `ATTACH PARTITION`), since D14 judges each statement on its own text and follows no change to the schema (B-C3's delta re-review, F4; DM-78); a statement sent before Django's registry is ready, which is judged without the models' tables;
> ```

**JJ7 — the proof README, `proofs/postgres-ordering/README.md` (B-C4): the further limits' heading.**

> ```
> (SV3 Stage B, correction B-C3; B-C2's delta re-review's S3, S4, S5, N9 and N10; DM-77; each with its planted example, the evidence record's "Delta re-review of B-C2" and "Stage B, correction B-C3"):
> ```

> ```
> (SV3 Stage B, corrections B-C3 and B-C4; B-C2's delta re-review's S3, S4, S5, N9 and N10, and B-C3's delta re-review's F5 and `excluded`; DM-77, DM-78; each with its planted example, the evidence record's "Delta re-review of B-C2", "Stage B, correction B-C3", "Delta re-review of B-C3" and "Stage B, correction B-C4"):
> ```

**JJ8 — the proof README, `proofs/postgres-ordering/README.md` (B-C4): S4 (F5).**

> ```
> S4, a statement's parameters are not read: SQL inside a parameter's value that psycopg writes where a placeholder stands inside a string constant (`SELECT id FROM glow_persistence_appaccount WHERE state <> '%s'` with the value `FOR UPDATE --`, which psycopg writes as `''FOR UPDATE --''`, a lock clause to PostgreSQL) passes, as it did at `470d97a`, when the text itself holds no word `UPDATE`; the review's other S4 form, a placeholder against its lock clause (`= %sFOR UPDATE`), is refused since B-C3 by the placeholder rule; no non-test code places a placeholder inside a constant or against a word.
> ```

> ```
> S4, a statement's parameters are not read: D14 judges the text before psycopg writes the values into it. psycopg writes each value as a constant: a numeric constant for a number (with a space before a minus sign), `true`, `false` or `NULL`, or else one quoted string constant, perhaps with a cast (with `E` and a space before it when the string holds a backslash). So where a placeholder stands outside every span and is glued to no name character or dollar sign, no SQL in its value reaches PostgreSQL as SQL, with S3's setting. Since B-C4, a placeholder any part of which lies inside a span fails, whatever the statement holds (`SELECT id FROM glow_persistence_appaccount WHERE state <> '%s'`, with or without a lock clause: with the value `FOR UPDATE --`, psycopg writes `''FOR UPDATE --''`, a lock clause to PostgreSQL; B-C3's delta re-review, F5); since B-C3, one glued to a name character or a dollar sign fails when the text holds the word `UPDATE` (`= %sFOR UPDATE`); no non-test code places a placeholder inside a span or against a word.
> ```

**JJ9 — the proof README, `proofs/postgres-ordering/README.md` (B-C4): `excluded`.**

> ```
> N10, the fast path assumes PostgreSQL 15 or later, where a number glued to a word is trailing junk (`1FOR UPDATE` is an error in 17, a lock in 14); the proof pins 17.
> ```

> ```
> N10, the fast path assumes PostgreSQL 15 or later, where a number glued to a word is trailing junk (`1FOR UPDATE` is an error in 17, a lock in 14); the proof pins 17. `excluded`, the name `INSERT … ON CONFLICT … DO UPDATE` gives the proposed row with no token binding it, is not read as a binding, so an `OF` name spelled `excluded` is resolved by its other bindings alone; a lock clause names only its own query's `FROM` items, so none can name the proposed row (B-C3's delta re-review; planted, passing; not run on PostgreSQL).
> ```

**JJ10 — `proofs/postgres-ordering/glow_ordering_proof/row_locks.py` (B-C4): the docstring's "What it does not see" (N3, F4, F5).**

> ```
> through an asynchronous cursor; a statement read with ``standard_conforming_strings`` off (S3);
> a placeholder against its lock clause, or SQL inside a parameter's value (S4); and a statement a
> case never runs.
> ```

> ```
> through an asynchronous cursor; a statement read with ``standard_conforming_strings`` off (S3);
> a parameter's value where its placeholder stands outside every span and is glued to no name
> character or dollar sign, which psycopg writes as a constant (S4); a lock through a model
> table's name that refers to another relation when the lock runs (a view of that name a path the
> record does not see created, the account table renamed to that name, or a table of that name of
> which the account table was made a child), since it judges each statement on its own text and
> follows no change to the schema; a statement sent before Django's registry is ready, judged
> without the models' tables; the name ``excluded`` as a binding; and a statement a case never
> runs.
> ```

**JJ11 — the record, `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md` (B-C4): B-C3's placeholder rule (F1).**

> ```
> a placeholder (`%s`, `%b`, `%t`, or `%(name)s`, `%(name)b`, `%(name)t`) with a name character
> ```

> ```
> a placeholder (`%s`, `%b`, `%t`, or `%(name)s`, `%(name)b`, `%(name)t`, a name read as any characters but parentheses, so a name holding `(` was not read: B-C3's delta re-review, F1, corrected in B-C4) with a name character
> ```

**JJ12 — the brief, `docs/planning/sv3-eligibility-discovery-interactions.md` (yours, revision 19): D14's reading (F1, F4, F5).**

> ```
> An unterminated span, a `DO` statement and a statement that creates a function or a procedure (the last two run a string as code) fail whatever their lock; a statement holding a `U&` quoted identifier fails if it takes `FOR UPDATE`; and a statement whose text holds the word `UPDATE` anywhere and a placeholder glued to a name character or a dollar sign fails, since the value psycopg writes there can complete a dollar-quote tag.
> ```

> ```
> An unterminated span, a `DO` statement, a statement that creates a function or a procedure (the last two run a string as code) and a statement that creates a view (`CREATE [OR REPLACE] [TEMP | TEMPORARY] [RECURSIVE] VIEW` or `CREATE MATERIALIZED VIEW`, the words read as PostgreSQL reads them) fail whatever their lock; a statement holding a `U&` quoted identifier fails if it takes `FOR UPDATE`. A placeholder is read as psycopg 3.3.6 reads one (`%s`, `%b` or `%t`, or `%(name)s`, `%(name)b` or `%(name)t` with a name of one or more characters other than `)`; `%%` is a literal percent sign): a statement with a placeholder any part of which lies inside a string constant (dollar-quoted ones included), a quoted identifier or a comment fails whatever its lock or text, since the quotes and text psycopg writes there can end that span; and a statement whose text holds the word `UPDATE` anywhere and a placeholder glued to a name character or a dollar sign fails, since the value psycopg writes there can complete a dollar-quote tag (B-C3's delta re-review, F1, F4 and F5; DM-78).
> ```

**JJ13 — the brief, `docs/planning/sv3-eligibility-discovery-interactions.md` (yours, revision 19): D14's resolution, the relations check and the freeze's pointer (F2, F3, F4, Codex).**

> ```
> any other form fails: a name bound twice, a binding inside a parenthesised join or in a `DELETE` or `MERGE` statement's `USING` list, a comma item, a schema-qualified name, `ONLY`, `*`, a sub-query's or a function's alias, or the account table inside a sub-query (the exact-head review of Stage B, #4 and #5; DM-75; B-C2's delta re-review, F1, F2, F4, F5, S1 and S2; DM-77).
> ```

> ```
> any other form fails: a name bound twice, a binding inside a parenthesised join, in a `DELETE` or `MERGE` statement's `USING` list, as a `MERGE INTO` target's alias (with or without `AS`) or as a join's `USING (…) AS` alias, a comma item, a schema-qualified name, `ONLY`, `*`, a sub-query's or a function's alias, or the account table inside a sub-query (the exact-head review of Stage B, #4 and #5; DM-75; B-C2's delta re-review, F1, F2, F4, F5, S1 and S2; DM-77; B-C3's delta re-review, F2 and F3; DM-78). With the models' tables given (Django's registry, once it is ready), a statement that takes `FOR UPDATE` and does not name the account table fails too unless every relation name it reads, in any scope (each `FROM`, `JOIN`, `USING`-list, `INTO`, `UPDATE` and `DELETE FROM` item, a `WITH` query's name read as one included), is one of those tables, written without a schema; a `TABLE` command, or parentheses it cannot read, fail it as well (Codex on `4c2f918`; DM-78). After B-C4, these rules are frozen ("Stage B, correction B-C4").
> ```

**JJ14 — the brief, `docs/planning/sv3-eligibility-discovery-interactions.md` (yours, revision 19): "Stage B, correction B-C4", before "Sessions".**

> ```
> The Dev Manager's pre-merge read of PR47 follows.
>
> ## Sessions
> ```

> ```
> Correction B-C4 follows (DM-78).
>
> ## Stage B, correction B-C4 (B-C3's delta re-review; DM-78)
>
> B-C4 answers B-C3's bounded delta re-review of `edc883e` (the record, "Delta re-review of B-C3"): changes required, no blocking finding. It changes no model, migration, lock, version check, existing DTO, stale body, `glow_chat` writer, ledger, lock-scan rule or bound, contract package, workflow or dependency, and no line in `services/api`.
>
> 1. **Placeholders read as psycopg reads them (F1).** D14 reads a placeholder as psycopg 3.3.6 does: `%s`, `%b` or `%t`, or `%(name)s`, `%(name)b` or `%(name)t` with a name of one or more characters other than `)`; `%%` is a literal percent sign. Both placeholder tests use this reading. F1's two texts (`%((n)s` with `{"(n": 1}`, and `%(a(b)s`) are cases, failing at B-C4's head and passing at `edc883e`. The record's account of B-C3's rule gains DM-78's note (JJ11).
> 2. **A placeholder inside a span (F5).** A statement with a placeholder any part of which lies inside a string constant (`'…'`, `E'…'`, `U&'…'` or dollar-quoted), a quoted identifier (`"…"` or `U&"…"`) or a comment (`--` or `/* … */`) fails whatever its lock or text: psycopg writes the value with its own quotes, which can end that span. The test runs before the fast path, as the glued-placeholder test does. Cases, each failing at B-C4's head and passing at `edc883e`: F5's text, the same without its lock clause, `"%s"`, a placeholder inside each other kind of span, and a name holding a quote (`%(a'b)s`). A `%%` inside a string constant, and a placeholder glued to a closing quote outside the constant (`'a'%s`), pass. The README's S4 follows (JJ8).
> 3. **A view's creation, and a lock through a name outside the models (F4; Codex on `4c2f918`).** A statement that creates a view (`CREATE [OR REPLACE] [TEMP | TEMPORARY] [RECURSIVE] VIEW` or `CREATE MATERIALIZED VIEW`, the words read as PostgreSQL reads them) fails whatever its lock, and the fast path's creation test reads `VIEW` as it reads `FUNCTION` and `PROCEDURE`. With the models' tables given, a statement that takes `FOR UPDATE` and does not name the account table fails unless every relation name it reads, in any scope, is one of those tables, written without a schema; a `TABLE` command, or parentheses it cannot read, fail it too. `PREPARE` needs no rule of its own: its body is judged as any statement is. Tests, offline:
>    - a record given the models' tables and fed `CREATE TEMP VIEW v AS SELECT id FROM glow_persistence_appaccount`, `SELECT id FROM v FOR UPDATE` and `DROP VIEW v`, in that order, refuses the first two and passes the third;
>    - F4's `public` view with `FOR UPDATE OF v2`, and `PREPARE p AS SELECT id FROM v FOR UPDATE`, are refused;
>    - a `FOR UPDATE` with no `OF` list on models' tables, as Django's `select_for_update()` sends it, passes.
>
>    A planted database reversal (F4's three statements in a case's session) shows the record failing at the view's creation and at the lock, with the own-objects counts 0, 0, 0 after the drop, under D4's conditions, informational. The stated limits' examples (a lock through a model table's name after a temporary view of that name, whose creation fails; a renamed table) are planted in the record.
> 4. **Two bindings (F2, F3).** A `MERGE INTO` target's alias written without `AS`, and a join's `USING (…) AS` alias, are read as bindings, none of them plain. The review's texts are cases, failing at B-C4's head and passing at `edc883e`. `excluded` is stated, not read (JJ9).
> 5. **The nits.** N1: a test text whose placeholder's only glued neighbour is `$`, failing with `$` removed from the name characters. N2: a test that pins a `JOIN` item inside a `USING` list as not plain, failing with the final pass removed. N3: the docstring's "What it does not see" in DM-78's words (JJ10).
> 6. **The records.** The README's D14 entry, SV3 paragraph and "Limits" in DM-78's words (JJ1 to JJ9). `row_locks.py`'s docstring says what the README says, in its reading, rule and resolution paragraphs and its fast-path sentence, and its "What it does not see" in DM-78's words (JJ10). The record gains B-C4's section and the note on B-C3's rule (JJ11).
> 7. **The earlier tests it changes** (DD5; AM11-23's sweep), each named in its prompt with its reason: any test that pins `_PLACEHOLDER`'s text or the fast path's creation test, or holds a statement items 1 to 4 refuse. Any other earlier test that no longer passes is a stop.
>
> **The stop rule (B-C4):** stop and report if B-C4 needs a change outside its owned paths, or to a model, a migration, a lock, a version check, an existing DTO, D8's single stale body, a `glow_chat` writer, the ledger, the lock scan's rules or B0's bound, the contract package, the workflow, a dependency or any line in `services/api`; if a statement any suite sends fails D14's corrected rule; or if a case other than those item 7 names changes its verdict.
>
> **B-C4's run of record:** a push run on its code head, with all eight jobs passing, the discovery suite 66/66, each suite's D14 record `PASS` with none refused and its own-objects counts 0, 0, 0, the account-table lock counts equal to B-C3's run of record (43809849211) in every suite, and the discovery phase's duration within the job's 30 minutes, read from GitHub.
>
> **B-C4's review, and how D14's line ends** (DM-78): a bounded delta re-review of B-C4 against `edc883e` (M05 S2), after the manager's verification, PR47's run and Codex on its head, under C4's five classes and the exact-head review's classes. It reads every path B-C4 touches as it stands at its head; plants each form items 1 to 4 name, by each rule's words and not its examples alone; and runs the negative control and each new test's reversal. It is the last review of D14 under all five classes. From B-C4's head, D14's rules are frozen, as the lock scan's were after C4 (DM-68): they change only to correct a class 1 defect (a lock of an `AppAccount` row that is not `FOR NO KEY UPDATE`, at the reviewed head in `services/api` or the reference design, or in a statement a suite sends that D14 passes) or a regression (class 3), or by a design the Dev Manager reads. Any other form a rule does not see, a form its words name (class 2) included, is recorded with its planted example as a stated limit in the README's "Limits" and the record, and the rule's words are narrowed to match; this applies to the findings of B-C4's own review. A test or reversal that passes where it should fail (class 4), and a record that claims more than D14 does (class 5), are corrected as before. This holds in every later review, SV4's included. The Dev Manager's pre-merge read of PR47 follows.
>
> ## Sessions
> ```

**JJ15 — the brief, `docs/planning/sv3-eligibility-discovery-interactions.md` (yours, revision 19): B-C4's owned paths.**

> ```
> Nothing else changes in B-C3.
> ```

> ```
> Nothing else changes in B-C3.
> - **Correction B-C4 only** (DM-78): in the proof, `row_locks.py` (its placeholder reading, the span and view-creation rules, the fast path's creation test, the relations check, the bindings F2 and F3 name, and its docstring) and its offline tests, new files included; the proof README's D14 entry, SV3 paragraph and "Limits"; the P11 plan's SV3 entry, its runs of record only; and the evidence record. Nothing else changes in B-C4.
> ```

## 15. Who applies what

- **B-C4:** JJ1 to JJ11, the README, the docstring and the record's note, as written. The docstring's reading, rule and resolution paragraphs and its fast-path sentence follow the README in B-C4's own words.
- **You, in the brief's revision 19:** JJ12 to JJ15, as written. The status line and "Sessions" are yours.
- **You, in B-C4's prompt and its review's prompt:** the Docker line (section 9), and the threads to answer (section 12).
- **My pre-merge read of PR47** confirms DM-75's, DM-77's and DM-78's texts as applied.

Status: complete

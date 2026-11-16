# DM-79 — SV3 Stage B: B-C4's delta re-review, before PR47's pre-merge read

- **From:** Dev Manager 5 (`session_01Q789u3CWg6s9pBGXerCQZt`), for App Manager 11, relayed by Nathan (OD-25).
- **Date:** 16 November 2026. Received about 20:45 UTC; finished about 20:58 UTC.
- **Read at:** `f3f1c6454e382fb97f4dc5a5c17c00ae1735654a` of `claude/magical-wozniak-yfmmx2`, exported outside any worktree.
  - Its code equals `07d8de3`'s: `git diff 07d8de3 f3f1c64` is empty outside Markdown.
  - The governing diff since my last read (`4c2f918`) is empty. The commits since are DM-78's merge and disposition, B-C4 and its verification, and the review's record with DM-79.
- **Environment:** names only. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, or any `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name is set. The AWS names are present and were not read.
- **What I changed:** this file only, on `claude/dev-manager`. Notion was read, not changed. No call to Stream, a database, HDE, Railway or Cloudflare.
  - My probes live in my scratchpad and are not committed. They load `row_locks.py` from the exports of `f3f1c64` and `4c2f918` under `python3 -I`.

## 1. The answers

| Item | Verdict |
|---|---|
| 1. F1, an alias that ends the `FROM` list | **Approved as a stated limit, with words.** The limit is KK5. The rule's words are narrowed in KK1 to KK3, KK6, KK8 to KK10 and KK12 to KK14 (section 4) |
| 2. F2, a placeholder followed by a string constant | **(a), a stated limit.** The limit is in KK5; S4 and the docstring's S4 clause are narrowed in KK4 and KK7 (section 5) |
| 3. F3, the record's sentence on `%()s` | **Corrected:** KK11 (section 6) |
| 4. N1, three forms that pass now | **Confirmed.** Each follows from DM-78's words, and none takes an account lock (section 7) |
| 5. How the words land | **(a): a records correction, B-C5, with a short bounded review.** (b) conflicts with my charter, and (c) would carry a class 5 docstring past the merge (section 8). B-C5's section and owned paths are KK15 and KK16 |
| 6. The sequence | **Agreed** (section 9) |
| 7. Notion | **Matches** at `f3f1c64` (section 10) |

## 2. What I read and checked

- **The consultation's file** at `f3f1c64`.
- **The record:**
  - "Stage B, correction B-C4" (lines 2420 to 2638);
  - "Manager verification of B-C4";
  - "Delta re-review of B-C4" (lines 2671 to 2693).
- **The code at `07d8de3`** (`row_locks.py`):
  - its docstring;
  - the placeholder pattern and the two placeholder tests;
  - `judge` and `_relations`;
  - `_bindings`: `_ENDS_FROM` (lines 242 to 261), the item reader, and the scan's branch that ends a `FROM` list (lines 981 and 982).
- **Reproduced with `row_locks.refusal`** at `07d8de3`'s code and at `edc883e`'s, with a set of model tables given:
  - F1's two texts pass at `07d8de3`. So does the same form with the alias `values`, and with a renamed table `x` after `set` instead of `v`;
  - F1's control with the alias `s` is refused. So is the same text with the `ON` condition in parentheses, and with a bare `set` alias used nowhere else;
  - F1's shape in a statement that names the account table is refused by the account rule;
  - F2's text passes at both heads: glued, across a line end, and across a `--` comment and a line end;
  - F3's text passes at `07d8de3` and was refused at `edc883e` as a glued placeholder;
  - N1's three forms pass at `07d8de3`, and each was refused at `edc883e`. The `MERGE INTO … x` form shows this only in a statement that names the account table.
- **DM-78's fifteen texts** are each found once at `f3f1c64`, with their old passages gone.
- **Item 5 rests on:**
  - my charter (`docs/planning/dev-manager.md`, lines 36 and 94);
  - the CI policy's paragraph on full-scope review (line 101);
  - the manager workflow's S2 (line 83).
- **Notion:** section 10.

## 3. My own errors in this round

Both of the review's limits rest on my own DM-78 words.

- **F2:** DM-78's section 5 and its S4 words (JJ8) said that outside every span a value is a constant. They also said a quote glued to a placeholder "only joins two constants into one". That holds for a constant before a placeholder. For a constant after it, psycopg writes a string value holding a backslash as ` E'…'`, so the joined constant becomes an escape string. That constant's backslashes become escapes, and its end moves.
  - My prototype judged texts only and never bound a value, so it could not find a form that depends on how a value is quoted.
  - The review calls this DM-77 section 9's gap from the other side, and it is.
- **F1:** DM-78's words for the relations check named every `FROM` and `JOIN` item as read. I did not read `_ENDS_FROM` against words that are also valid aliases, and I planted no such alias.

The lesson:
- a rule about placeholders is tried with the driver's own binding of planted values, as the review did;
- a rule that lists positions is tried against every word its reader treats as the end of a list.

## 4. Item 1 — F1, an alias that ends the `FROM` list

- **Approved as a stated limit.** Under the freeze, a class 2 form becomes a stated limit, and the rule's words are narrowed to match (DM-78's "B-C4's review, and how D14's line ends").
- **What happens.**
  - `set` and `values` are among the words that end a `FROM` list (`_ENDS_FROM`), and either can also be an alias.
  - As an item's alias the reader takes it, and the list goes on.
  - Anywhere else at the list's own depth, the list ends there: for example, as a column's qualifier in an `ON` condition written without parentheses (`ON set.id = m.id`).
  - A later `JOIN` or comma item is then not read, and the relations check never sees it.
- **Its reach.**
  - Only a statement that takes `FOR UPDATE` and does not name the account table is affected.
  - A statement that names the account table is judged by the account rule, which needs an `OF` list and binds each name in it. My probes of F1's shape with the account table are refused.
  - Django writes every `ON` condition in parentheses.
  - Through statements D14 sees, F1 reaches an account row only with a relation outside the models: a view made through a path D14 does not see, or a table renamed by a statement D14 judges on its own text (my probe with `x` passes).
- **The words:**
  - the limit, in a new "Limits" bullet for the limits recorded under the freeze (KK5);
  - the narrowing, in the README's SV3 paragraph (KK1, KK2) and D14 entry (KK3);
  - in `row_locks.py`'s module docstring (KK6), `judge`'s docstring (KK8) and `_relations`'s docstring (KK9);
  - in the record's account of the relations check (KK10);
  - in the manager's own note for the review (KK12);
  - in the P11 plan's B-C4 clause (KK13);
  - in the brief's D14 rule (KK14).
- **Two docstrings the review did not name** carry the same claim, so they are narrowed too:
  - `_relations`'s docstring repeats the module docstring's list;
  - `judge`'s docstring says a `FOR UPDATE` statement "must read only" the models' tables.

## 5. Item 2 — F2, a placeholder followed by a string constant

- **(a), a stated limit.**
- **Why not (b), a design:**
  - F2 is outside every rule, and class 1 is not engaged: no non-test code places a placeholder before a quote, and the form also needs a value holding a backslash.
  - A new rule would turn B-C5 from a records correction into a rule change. Its review would again be a review of a rule, which reopens the cycle the freeze closed.
  - (b) as worded also misses one of F2's forms. PostgreSQL continues a string constant across whitespace that holds a line end with `--` comments inside it. So "the next non-space character is a quote" fails to see `%s -- note` followed by a line end and a quote. A design would need more care than a records correction allows.
- **The words:**
  - the limit, in the same new bullet (KK5);
  - S4's sentence (KK4);
  - the docstring's S4 clause (KK7).

## 6. Item 3 — F3, the record's sentence on `%()s`

- **Corrected:** the head is right and the sentence is wrong.
  - Where a name holds `%(`, `edc883e`'s pattern read the inner placeholder (`%(b)s` in `%(a%(b)s`).
  - B-C4's pattern reads one placeholder named `a%(b`, as psycopg does.
  - The corrected sentence does not claim to list every such text (KK11).

## 7. Item 4 — N1, three forms that pass now

- **Confirmed.** Each follows from DM-78's words, and none takes an account lock:
  - `version%()s`: psycopg reads `%(` with an empty name as no placeholder and raises before it sends the text with parameters. B-C4 reads it as psycopg does;
  - `%(a%(b)s`: one placeholder named `a%(b`, glued to no name character. KK11 records it;
  - the `MERGE INTO … x` alias: an alias hides its table's name, as PostgreSQL binds it, so an `OF` name spelled as the table binds once, to a model table's plain item. My probe passes at `07d8de3` and was refused at `edc883e` as bound twice.

## 8. Item 5 — how the words land

- **(a): B-C5, a records correction, with a short bounded review.**
- **(b) is declined.** My charter says: "The Dev Manager does not replace the exact-head code and security reviews that Nathan runs for full-scope changes", and "A Dev Manager `approved` is neither an owner decision nor an exact-head review."
  - A change to a `.py` file is full scope (AGENTS.md), a docstring included.
  - The CI policy wants a bounded review prompt for the exact head, run by Nathan in a separate session: "Classification and test checks do not substitute for review."
- **(c) is declined.** It would leave two docstring passages that claim more than D14 does, which is class 5. The freeze keeps class 5 corrected as before.
  - DM-70's and DM-72's carry-over covers record nits only: a record wrong about something other than what D14 refuses or sees.
- **B-C5's review is short:**
  - it confirms by AST, with docstrings set aside, that `row_locks.py`'s code is `07d8de3`'s;
  - it reads each changed docstring and every Markdown path B-C5 touches, as each stands at the head (M05 S2);
  - it finds each of my texts once, as given;
  - it judges each narrowed sentence against the code, under class 5 and class 1.
- **The words:** B-C5's section (KK15) and owned paths (KK16).

## 9. Item 6 — the sequence

- **Agreed.** Three notes:
  - the brief's revision 20 holds KK14 to KK16;
  - KK12 is your own record note, applied with the records, before B-C5;
  - my pre-merge read of PR47 confirms DM-75's, DM-77's, DM-78's and DM-79's texts as applied.

## 10. Item 7 — Notion (read-only, at about 20:47 UTC)

| Page | What I compared | Result |
|---|---|---|
| Implementation Control, status | Last matched at `f3f1c64`, with B-C4's review and DM-79 | **Match** |
| Its Branches bullet | Nine branches and their heads, against `git ls-remote` now | **Match** |
| Its Mistakes log bullet | AM11-01 to AM11-31, at `b67d9e3`; the log has not changed since | **Match** |
| Its procedure summary | The stamp at `b192164`; no governing change since | **Match** |
| Dev Manager page, `DM-78` and `DM-79` | DM-78 answered and considered; DM-79 pending, at `f3f1c64` | **Match** |
| The register copy | Matched at `e19f731`, OD-66 last; the register has not changed since | **Match** |
| Work Register, `SV3` and `M08` | SV3 at DM-79, evidence pinned at `f3f1c64`, the brief at revision 19; M08 unchanged | **Match** |

## 11. The words

**KK1 — the proof README, `proofs/postgres-ordering/README.md` (B-C5): the SV3 paragraph's every-suite sentence (F1).**

> ```
> if a statement takes `FOR UPDATE` through a name that is not one of the models' tables (since B-C4),
> ```

> ```
> if a statement takes `FOR UPDATE` through a name that is not one of the models' tables, in the positions its reading binds (since B-C4; "Limits" below),
> ```

**KK2 — the proof README, `proofs/postgres-ordering/README.md` (B-C5): the SV3 paragraph's B-C4 sentence (F1), and B-C5's.**

> ```
> and a statement that takes `FOR UPDATE` through a name that is not one of the models' tables, whatever else it names; and it reads a `MERGE INTO` target's alias written without `AS`, and a join's `USING (…) AS` alias, as bindings, none of them plain (the D14 entry and "Limits" below).
> ```

> ```
> and a statement that takes `FOR UPDATE` through a name that is not one of the models' tables, in the positions its reading binds, whatever else it names; and it reads a `MERGE INTO` target's alias written without `AS`, and a join's `USING (…) AS` alias, as bindings, none of them plain (the D14 entry and "Limits" below). **Correction B-C5** (B-C4's delta re-review; DM-79) changes no rule and adds no case, 66 in all: it records two forms D14 does not see as limits under its freeze (an item after a `set` or `values` that the reading takes as the end of the `FROM` list, and a placeholder followed by a string constant), narrows the relations check's words to the positions its reading binds, and corrects the record (the D14 entry and "Limits" below).
> ```

**KK3 — the proof README, `proofs/postgres-ordering/README.md` (B-C5): D14's relations check (F1).**

> ```
> fails too unless every relation name it reads, in any scope (each `FROM`, `JOIN`, `USING`-list, `INTO`, `UPDATE` and `DELETE FROM` item, a `WITH` query's name read as one included), is one of those tables, written without a schema; a `TABLE` command, or parentheses it cannot read, fail it as well. So a `FOR UPDATE` through a name that is not one of the models' tables fails, whatever else the statement names (Codex on `4c2f918`; DM-78);
> ```

> ```
> fails too unless every relation name its reading binds, in any scope (each `FROM`, `JOIN`, `USING`-list, `INTO`, `UPDATE` and `DELETE FROM` item, a `WITH` query's name read as one included, but not an item after a `set` or `values` that the reading takes as the end of the `FROM` list: F1 in the limits under the freeze, below), is one of those tables, written without a schema; a `TABLE` command, or parentheses it cannot read, fail it as well. So a `FOR UPDATE` through a name that is not one of the models' tables, in a position its reading binds, fails, whatever else the statement names (Codex on `4c2f918`; DM-78; B-C4's delta re-review, F1; DM-79);
> ```

**KK4 — the proof README, `proofs/postgres-ordering/README.md` (B-C5): S4 (F2).**

> ```
> So where a placeholder stands outside every span and is glued to no name character or dollar sign, no SQL in its value reaches PostgreSQL as SQL, with S3's setting.
> ```

> ```
> So where a placeholder stands outside every span and is glued to no name character or dollar sign, no SQL in its value reaches PostgreSQL as SQL, with S3's setting; but a string constant that follows such a placeholder can read differently once the value is written (F2 in the limits under the freeze, below).
> ```

**KK5 — the proof README, `proofs/postgres-ordering/README.md` (B-C5): the limits under the freeze (F1, F2).**

> ```
> (B-C3's delta re-review; planted, passing; not run on PostgreSQL).
> ```

> ```
> (B-C3's delta re-review; planted, passing; not run on PostgreSQL).
> - **The row-lock record's limits under the freeze** (SV3 Stage B, after B-C4; D14's rules frozen from `07d8de3`, DM-78; B-C4's delta re-review, the last of D14 under all five classes, F1 and F2; DM-79; each with its planted example, the evidence record's "Delta re-review of B-C4"): F1, the relations check reads a `FROM` list until a word that ends one, and `set` and `values`, which can also be an alias, are among those words: where either stands at the list's own depth other than as an item's alias (as a column's qualifier in an `ON` condition written without parentheses, `JOIN glow_persistence_block set ON set.id = m.id`), the list ends there, so a later `JOIN` or comma item is not read, and a relation outside the models there passes (`SELECT m.id FROM glow_persistence_match m JOIN glow_persistence_block set ON set.id = m.id JOIN v ON true FOR UPDATE`, and `…, v FOR UPDATE`; with `v` a view over the account table, PostgreSQL 17.11 held the account row `FOR UPDATE`; with the alias `s`, or the condition in parentheses, each is refused). Django writes every `ON` condition in parentheses, and a statement that names the account table is judged as before: its rule needs an `OF` list, binds each name in it, and fails a name it cannot bind. F2, a placeholder that stands outside every span and is followed by a string constant, glued to it or across whitespace that holds a line end (`--` comments included), passes: psycopg writes a string value that holds a backslash as ` E'…'`, which runs into the constant after it, so that constant's backslashes become escapes and its end moves (`SELECT id FROM glow_persistence_appaccount WHERE state <> %s'\'' FOR UPDATE --'`, whose lock D14 reads inside a constant; with the value `a\b`, psycopg sent `… E'a\\b''\'' FOR UPDATE --'`, and PostgreSQL 17.11 held the account row `FOR UPDATE`; a value without a backslash did not). No non-test code places a placeholder before a quote. Neither form is refused, under the freeze.
> ```

**KK6 — `proofs/postgres-ordering/glow_ordering_proof/row_locks.py` (B-C5): the module docstring's rule paragraph (F1).**

> ```
> account table fails too unless every relation name it reads (``_relations``), in any scope (each
> ``FROM``, ``JOIN``, ``USING``-list, ``INTO``, ``UPDATE`` and ``DELETE FROM`` item, a ``WITH``
> query's name read as one included), is one of those tables, written without a schema; a ``TABLE``
> command, or parentheses it cannot read, fail it as well. So a ``FOR UPDATE`` through a name that
> is not one of the models' tables fails, whatever else the statement names (Codex on ``4c2f918``;
> DM-78). A sub-query's and a function's own relations are read in turn; a function is not a
> relation.
> ```

> ```
> account table fails too unless every relation name its reading binds (``_relations``), in any
> scope (each ``FROM``, ``JOIN``, ``USING``-list, ``INTO``, ``UPDATE`` and ``DELETE FROM`` item, a
> ``WITH`` query's name read as one included, but not an item after a ``set`` or ``values`` that
> the reading takes as the end of the ``FROM`` list; the proof README's "Limits"), is one of those
> tables, written without a schema; a ``TABLE`` command, or parentheses it cannot read, fail it as
> well. So a ``FOR UPDATE`` through a name that is not one of the models' tables, in a position its
> reading binds, fails, whatever else the statement names (Codex on ``4c2f918``; DM-78; B-C4's
> delta re-review, F1; DM-79). A sub-query's and a function's own relations are read in turn; a
> function is not a relation.
> ```

**KK7 — `proofs/postgres-ordering/glow_ordering_proof/row_locks.py` (B-C5): the module docstring's S4 clause (F2).**

> ```
> character or dollar sign, which psycopg writes as a constant (S4); a lock through a model
> table's name that refers to another relation when the lock runs (a view of that name a path the
> record does not see created, the account table renamed to that name, or a table of that name of
> which the account table was made a child), since it judges each statement on its own text and
> follows no change to the schema; a statement sent before Django's registry is ready, judged
> without the models' tables; the name ``excluded`` as a binding; and a statement a case never
> runs.
> ```

> ```
> character or dollar sign, which psycopg writes as a constant, and a string constant after such a
> placeholder, which a value holding a backslash can change (S4; the proof README's "Limits"); a
> lock through a model table's name that refers to another relation when the lock runs (a view of
> that name a path the record does not see created, the account table renamed to that name, or a
> table of that name of which the account table was made a child), since it judges each statement
> on its own text and follows no change to the schema; a statement sent before Django's registry
> is ready, judged without the models' tables; the name ``excluded`` as a binding; and a statement
> a case never runs.
> ```

**KK8 — `proofs/postgres-ordering/glow_ordering_proof/row_locks.py` (B-C5): `judge`'s docstring (F1).**

> ```
>     that takes ``FOR UPDATE`` without naming the account table must read only them."""
> ```

> ```
>     that takes ``FOR UPDATE`` without naming the account table must read only them, in the
>     positions its reading binds (the module docstring's rule)."""
> ```

**KK9 — `proofs/postgres-ordering/glow_ordering_proof/row_locks.py` (B-C5): `_relations`'s docstring (F1).**

> ```
>     relation name it reads, in any scope (each ``FROM``, ``JOIN``, ``USING``-list, ``INTO``,
>     ``UPDATE`` and ``DELETE FROM`` item, a ``WITH`` query's name read as one), is one of
>     ``tables``, written without a schema; a ``TABLE`` command, or parentheses it cannot read, fail
>     it. A sub-query's and a function's own relations are read in turn; a function is not a
>     relation."""
> ```

> ```
>     relation name its reading binds, in any scope (each ``FROM``, ``JOIN``, ``USING``-list,
>     ``INTO``, ``UPDATE`` and ``DELETE FROM`` item, a ``WITH`` query's name read as one; not an
>     item after a ``set`` or ``values`` read as the end of the ``FROM`` list, a stated limit:
>     B-C4's delta re-review, F1; DM-79), is one of ``tables``, written without a schema; a
>     ``TABLE`` command, or parentheses it cannot read, fail it. A sub-query's and a function's
>     own relations are read in turn; a function is not a relation."""
> ```

**KK10 — the record, `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md` (B-C5): the relations check's account (F1).**

> ```
> must be one of the tables, written without a schema (`OUTSIDE_THE_MODELS`).
> ```

> ```
> must be one of the tables, written without a schema (`OUTSIDE_THE_MODELS`); an item after a `set` or `values` that the reading takes as the end of the `FROM` list is not read, a stated limit under the freeze (B-C4's delta re-review, F1; DM-79).
> ```

**KK11 — the record, `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md` (B-C5): the sentence on `%()s` (F3).**

> ```
> It is the only text `edc883e`'s placeholder pattern read as a placeholder that B-C4's does not.
> ```

> ```
> It is not the only change in that direction: where a name holds `%(`, `edc883e`'s pattern read the inner placeholder (`%(b)s` in `%(a%(b)s`), where B-C4's reads one placeholder named `a%(b`, as psycopg does, so `UPDATE glow_persistence_match SET version = %(a%(b)s WHERE id = 1`, refused at `edc883e` as a glued placeholder, passes at B-C4's head (B-C4's delta re-review, F3 and N1; DM-79).
> ```

**KK12 — the record, `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md` (yours): the verification's note for the review (F1).**

> ```
>   - the relations check reads the positions JJ4 names; a relation in a position it does not read would escape it (DM-78 section 6);
> ```

> ```
>   - the relations check reads the positions JJ4 names; a relation in a position it does not read would escape it (DM-78 section 6). B-C4's delta re-review found one: an item after a `set` or `values` that the reading takes as the end of the `FROM` list (F1), a stated limit under the freeze (DM-79);
> ```

**KK13 — the P11 plan, `docs/testing/p11-deferred-acceptance.md` (B-C5): B-C4's clause (F1).**

> ```
> and a `FOR UPDATE` through a name that is not one of the models' tables;
> ```

> ```
> and a `FOR UPDATE` through a name that is not one of the models' tables, in the positions its reading binds (the proof README's "Limits");
> ```

**KK14 — the brief, `docs/planning/sv3-eligibility-discovery-interactions.md` (yours, revision 20): D14's rule (F1, F2).**

> ```
> fails too unless every relation name it reads, in any scope (each `FROM`, `JOIN`, `USING`-list, `INTO`, `UPDATE` and `DELETE FROM` item, a `WITH` query's name read as one included), is one of those tables, written without a schema; a `TABLE` command, or parentheses it cannot read, fail it as well (Codex on `4c2f918`; DM-78). After B-C4, these rules are frozen ("Stage B, correction B-C4").
> ```

> ```
> fails too unless every relation name its reading binds, in any scope (each `FROM`, `JOIN`, `USING`-list, `INTO`, `UPDATE` and `DELETE FROM` item, a `WITH` query's name read as one included), is one of those tables, written without a schema; a `TABLE` command, or parentheses it cannot read, fail it as well (Codex on `4c2f918`; DM-78). After B-C4, these rules are frozen ("Stage B, correction B-C4"). The forms they do not see are stated limits in the proof README's "Limits", among them an item after a `set` or `values` that the reading takes as the end of the `FROM` list, and a placeholder followed by a string constant (B-C4's delta re-review, F1 and F2; DM-79).
> ```

**KK15 — the brief, `docs/planning/sv3-eligibility-discovery-interactions.md` (yours, revision 20): "Stage B, correction B-C5", before "Sessions".**

> ```
> The Dev Manager's pre-merge read of PR47 follows.
>
> ## Sessions
> ```

> ```
> Correction B-C5 follows (DM-79).
>
> ## Stage B, correction B-C5 (B-C4's delta re-review; DM-79)
>
> B-C5 corrects the records after B-C4's bounded delta re-review of `07d8de3` (the record, "Delta re-review of B-C4"): changes required by one class 5 finding that is record-only (F3), with two stated limits under D14's freeze (F1, F2). It changes no rule, since D14's rules are frozen from `07d8de3` (DM-78). It changes no code, test, model, migration, lock, version check, DTO, `glow_chat` writer, ledger, lock-scan rule or bound, contract package, workflow or dependency, and no line in `services/api`. In `row_locks.py` it changes three docstrings only (the module's, `judge`'s and `_relations`'s), the file otherwise identical to `07d8de3`'s by AST with docstrings set aside.
>
> 1. **F1, a stated limit.** The README's "Limits" gains it with its planted example (DM-79's KK5). The relations check's words narrow to the positions its reading binds: in the README's SV3 paragraph and D14 entry (KK1 to KK3), the three docstrings (KK6, KK8, KK9), the record's account of the check (KK10) and the P11 plan's B-C4 clause (KK13).
> 2. **F2, a stated limit.** The README's "Limits" gains it with its planted example (KK5). S4's sentence and the docstring's S4 clause narrow to match (KK4, KK7).
> 3. **F3, the record.** The record's sentence on `%()s` is corrected (KK11).
> 4. **B-C5's own records.** The README's SV3 paragraph gains B-C5's sentence (KK2). The record gains B-C5's section: the AST identity, each of DM-79's texts found once, and the run of record. The P11 plan's SV3 entry gains B-C5's run of record.
>
> **The stop rule (B-C5):** stop and report if B-C5 needs a change outside its owned paths, a change to `row_locks.py` other than its three docstrings, or a text other than as DM-79 gives it.
>
> **B-C5's run of record:** a push run on its head, with all eight jobs passing, the discovery suite 66/66, each suite's D14 record `PASS` with none refused and its own-objects counts 0, 0, 0, and the account-table lock counts equal to B-C4's run of record (43919688476) in every suite, read from GitHub.
>
> **B-C5's review** (DM-79): a bounded delta re-review of B-C5 against `07d8de3` (M05 S2), after the manager's verification, PR47's run and Codex on its head, under class 5 and class 1. D14's rules are frozen, and with the code unchanged no other class can arise. It confirms by AST, with docstrings set aside, that `row_locks.py`'s code is `07d8de3`'s; reads the three docstrings, and every Markdown path B-C5 touches, as each stands at its head; finds each of DM-79's texts once, as given; and checks each narrowed or new sentence against the code at `07d8de3`. A form D14 does not see is recorded as a stated limit, under the freeze. The Dev Manager's pre-merge read of PR47 follows.
>
> ## Sessions
> ```

**KK16 — the brief, `docs/planning/sv3-eligibility-discovery-interactions.md` (yours, revision 20): B-C5's owned paths.**

> ```
> Nothing else changes in B-C4.
> ```

> ```
> Nothing else changes in B-C4.
> - **Correction B-C5 only** (DM-79): in the proof, `row_locks.py`'s module docstring, `judge`'s docstring and `_relations`'s docstring, and nothing else in it; the proof README's D14 entry, SV3 paragraph and "Limits"; the P11 plan's SV3 entry, B-C4's clause and its runs of record only; and the evidence record. Nothing else changes in B-C5.
> ```

## 12. Who applies what

- **B-C5:** KK1 to KK11 and KK13, as written.
- **You, with the records before B-C5:** KK12 in your verification section, and KK14 to KK16 as the brief's revision 20. The status line and "Sessions" are yours.
- **You, in B-C5's prompt and its review's prompt:** the Docker line, if a local database run is allowed. B-C5's code does not change, so none is needed.
- **My pre-merge read of PR47** confirms DM-75's, DM-77's, DM-78's and DM-79's texts as applied.

Status: complete

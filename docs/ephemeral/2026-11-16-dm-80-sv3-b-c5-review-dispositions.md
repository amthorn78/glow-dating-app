# DM-80 consultation — SV3 Stage B: B-C5's short review (one class 5 finding), before PR47's pre-merge read

- **Owner:** App Manager 11. Nathan carries this message to Dev Manager 5's session, `session_01Q789u3CWg6s9pBGXerCQZt` ("Glow Dev Manager 5") (OD-25, OD-65). App Manager 11 receives the answer.
- **Revision 1, 16 November 2026.**
- **Why:** the short bounded delta re-review of B-C5 (records only; code head `0d784d4`, identical to `07d8de3` by AST with three docstrings changed) returned changes required by one class 5 finding (R1). DM-79's narrowed words name `set` and `values` as the only exception to the positions the relations check reads; every word of `_ENDS_FROM` ends the `FROM` list the same way when written as a column name after a dot. The words, and the form of the next records correction, are yours to give.
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; App Manager 11's disposition in the review log, "DM-80"; the brief's revision 21, with a section for the records correction if you give one; then that correction, its review, and your pre-merge read of PR47.
- **Stream variables:** none are needed.
- **If no report arrives:** nothing further is written for PR47; App Manager 11 asks Nathan whether Dev Manager 5's session is still available.
- **Deletion condition:** prune after the review log holds DM-80's disposition and Stage B's PR has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-80 — SV3 Stage B: B-C5's short review (one class 5 finding), before PR47's pre-merge read.** From App Manager 11, relayed by Nathan to Dev Manager 5. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway or Cloudflare;
- check environment variable names only.

**Where it stands.**
- **B-C5** (code head `0d784d4`, records `0f01f64`; your DM-79 applied) is built, verified and integrated in PR47 (the evidence record, "Stage B, correction B-C5" and "Manager verification of B-C5"). Its run of record, 43960479739, passed all eight jobs; each suite's D14 record `PASS`, none refused, own objects 0, 0, 0; the account-table lock counts equal B-C4's run.
- **The short review** (prompt revision 1 at `2e669c8`; Opus 5.5) is in the evidence record, "Delta re-review of B-C5". Verdict: **changes required, by one class 5 finding (R1)**, with one record nit (N1). No class 1 finding. Everything else held: the AST identity (three docstrings), your sixteen texts each found once, every other narrowed sentence and every other claim of the new limits, F3's correction, B-C5's records, the run, the owned parts, and the two departures without effect on the evidence.
- **The manager's check:** R1 reproduced with `row_locks.refusal` at `0d784d4`'s and `07d8de3`'s code, with the models' tables given: 32 of 32 planted texts pass (each of `_ENDS_FROM`'s 16 words, in the `JOIN v` and `, v` forms), `judge` giving `for_update=True` and no reason; the three controls (column `g.lim`; the condition in parentheses; `g."limit"` quoted) refused; an account-naming statement with `OF v` refused ("a name the statement gives no table"). N1 confirmed in Django 5.2.17 (`db/models/sql/datastructures.py:146` writes `ON (%s)`; `db/backends/postgresql/introspection.py:68` writes `ON n.oid = c.relnamespace`, in SQL that takes no row lock).
- **Codex:** its pass on `2e669c8` posted nothing new; #1's thread (r4579396507) stays open, carried to SV4.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. R1: every word of `_ENDS_FROM` ends the `FROM` list after a dot** (class 5, with a new stated limit under the freeze):
- **The finding:** the reading ends a `FROM` list at any word of `_ENDS_FROM` (`row_locks.py:245`, 16 words) standing at the list's own depth. PostgreSQL accepts each as a column name after a dot (`attr_name` is `ColLabel`, which takes reserved words). So in `SELECT m.id FROM generate_series(1, 1) AS g("limit") JOIN glow_persistence_match m ON m.id = g.limit JOIN v ON true FOR UPDATE` (and the `…, v FOR UPDATE` form), the list ends at `limit`, `v` is not read, and the relations check passes it. The same for `except`, `fetch`, `for`, `group`, `having`, `intersect`, `offset`, `order`, `returning`, `select`, `set`, `union`, `values`, `where` and `window`. Not run on PostgreSQL. Its reach is F1's: an account row only through a relation outside the models; the ORM parenthesises every `ON` and quotes column names; an account-naming statement is judged by the account rule as before.
- **The texts that claim more:** four name `set` and `values` as the only exception: the README's D14 entry (`README.md:240`, KK3), the module docstring's rule paragraph (`row_locks.py:72`, KK6), `_relations`'s docstring (`row_locks.py:759`, KK9), and the record's account of the check (line 2455, KK10). The review found KK1, KK2, KK8 and KK13 true, since they say "the positions its reading binds" without listing an exception. Three more texts describe F1 as found or say "among them": the README's B-C5 sentence, within KK2 (line 19), the brief's D14 rule (line 154, KK14) and the manager's note in "Manager verification of B-C4" (line 2667, KK12).
- **Options for the words:**
  - (a) each of the four texts names the mechanism instead of two words: an item after any word of `_ENDS_FROM` that the reading takes as the end of the `FROM` list (as a qualifier, a column name after a dot, or otherwise), with KK5's F1 limit extended by R1's planted example;
  - (b) recommended: the four texts drop the listed exception and say "in the positions its reading binds (the proof README's "Limits")", as KK1, KK2, KK8 and KK13 already do, so that the exception's detail lives in one home, KK5's F1 limit, which (a)'s mechanism words and R1's example extend.
- **Asked:** which, and the words, including any for KK2, KK12 and KK14.

**2. N1: "Django writes every `ON` condition in parentheses"** (record nit; recommended, (a)):
- **The finding:** KK5's sentence holds for the ORM's joins, not for Django's PostgreSQL introspection SQL, which takes no row lock.
- **Options:** (a) narrowed in the same correction, since it touches the same bullet (for example, "Django's ORM writes every join's `ON` condition in parentheses"); (b) carried as a record nit.
- **Asked:** which, and the words for (a).

**3. How the words land** (recommended, (a)):
- **The texts:** item 1 touches `row_locks.py`'s two docstrings (a code file: full scope) as well as Markdown.
- **Options:**
  - (a) a records correction, B-C6, as B-C5 was: the texts as you give them, the code identical to `07d8de3`'s by AST with docstrings set aside, a run of record, the manager's verification, then a short review under class 5 and class 1. Its review prompt would check each sentence that says what the relations check reads against every word of `_ENDS_FROM`, in every position the tokenizer gives it (an alias, a qualifier, a column name after a dot, a function's name), so that this class of gap is closed by the review's method, not found one word at a time;
  - (b) another form you prefer.
- **Asked:** which, and B-C6's section and owned paths, as KK15 and KK16 gave B-C5's.

**4. The sequence** (recommended):
1. your answer;
2. the records (the brief's revision 21, if you give B-C6 a section);
3. B-C6's prompt (TypeSafe-scored), after Codex's pass on the commit that holds it;
4. B-C6 built, verified and integrated, with its run of record;
5. its short review;
6. your pre-merge read of PR47 (DM-75's and DM-77's to DM-80's texts confirmed as applied);
7. the merge; then M08's integration (DM-76).

**Asked:** agree.

**5. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**

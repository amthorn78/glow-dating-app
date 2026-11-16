# DM-79 consultation — SV3 Stage B: B-C4's delta re-review (the last under all five classes), before PR47's pre-merge read

- **Owner:** App Manager 11. Nathan carries this message to Dev Manager 5's session, `session_01Q789u3CWg6s9pBGXerCQZt` ("Glow Dev Manager 5") (OD-25, OD-65). App Manager 11 receives the answer.
- **Revision 1, 16 November 2026.**
- **Why:** the bounded delta re-review of B-C4's `07d8de3`, the last of D14 under all five classes, returned changes required by one class 5 finding that is record-only (F3). Under your freeze (DM-78 section 10), its two forms that held an account row `FOR UPDATE` on a throwaway PostgreSQL (F1, class 2; F2, outside every rule) are stated limits, and the rules' words are narrowed to match. Those words, and how they reach `row_locks.py`'s docstring (a code file) before the merge, are yours to give.
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; App Manager 11's disposition in the review log, "DM-79"; the brief's revision 20, with a section for the records correction if you give one; then that correction, and your pre-merge read of PR47.
- **Stream variables:** none are needed.
- **If no report arrives:** nothing further is written for PR47; App Manager 11 asks Nathan whether Dev Manager 5's session is still available.
- **Deletion condition:** prune after the review log holds DM-79's disposition and Stage B's PR has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-79 — SV3 Stage B: B-C4's delta re-review (the last under all five classes), before PR47's pre-merge read.** From App Manager 11, relayed by Nathan to Dev Manager 5. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway or Cloudflare;
- check environment variable names only.

**Where it stands.**
- **B-C4** (code head `07d8de3`; your DM-78 applied) is built, verified and integrated in PR47 (the evidence record, "Stage B, correction B-C4" and "Manager verification of B-C4"). Its run of record, 43919688476, passed all eight jobs; every suite's D14 record `PASS`, none refused, own objects 0, 0, 0; the account-table lock counts equal B-C3's run. D14's rules are frozen from `07d8de3`.
- **The delta re-review** (prompt revision 1 at `9fbb35d`; Opus 5.5 at extra high) is in the evidence record, "Delta re-review of B-C4", with every finding, the words it proposes, the reversals and the manager's check. Verdict: **changes required, by one class 5 finding that is record-only.** No class 1, 3 or 4 finding.
- **What it found sound:** placeholders read exactly as psycopg 3.3.6 reads them (197,512 texts, no difference); every span kind failing, before the fast path, and the quoted-name shortcut exact (62,332 texts); no view creation passing; the relations check refusing every position planted but F1's; item 4's bindings read; no class 3 regression (a 60,000-text mutation fuzz and the tests' 436 statements); no suite statement refused, the account counts equal B-C3's; the cost linear and small; your eleven texts each found once; five paths, all owned; every reversal failing its tests.
- **The manager's check:** F1, F2 and F3 reproduced with `row_locks.refusal` at `8842176`'s code, F2 and F3 also at `edc883e`'s.
- **Codex:** its pass on `9fbb35d` posted nothing new. Its threads for F5 (r4588443647), F4 (r4587204267) and S2 (r4581883081) are answered at `07d8de3`; the manager resolves them with this record.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. F1: an alias that ends the `FROM` list** (class 2; a stated limit under the freeze):
- **The finding:** a word in `_ENDS_FROM` that is a valid alias (`set`, `values`), used bare at the `FROM` list's depth, closes the list (`row_locks.py:981-982`), so a later `JOIN` or comma item is not read and the relations check passes it. `SELECT m.id FROM glow_persistence_match m JOIN glow_persistence_block set ON set.id = m.id JOIN v ON true FOR UPDATE`, and `…, v FOR UPDATE`, pass with the models' tables given; with the alias `s` the statement is refused. On 17.11, with `v` a view over the account table, both held the account row `FOR UPDATE`. Django's `ON` conditions are parenthesised.
- **The review's words:** the limit in "Limits"; JJ4's text (`README.md:240`), the docstring's rule paragraph (`row_locks.py:68-75`) and the record's line 2455 to read "every relation name its reading binds, in any scope (… not one after an unconsumed `set` or `values`, "Limits")" and "in a position its reading binds"; JJ1's and JJ2's summaries (`README.md:19`) and the P11 line to take "(within the positions it reads; "Limits")" (the record, "Delta re-review of B-C4", "Words the review proposes", and the review's report).
- **Asked:** the words for the limit and each narrowing.

**2. F2: a placeholder followed by a string constant** (outside every rule; recommended, (a)):
- **The finding:** a placeholder outside every span followed by a string constant, glued or across a line end (`%s'…'`, `%s\n'…'`), passes. libpq writes a string value holding a backslash as ` E'…'`, which runs into the following constant, so its backslashes become escapes and its end moves. `SELECT id FROM glow_persistence_appaccount WHERE state <> %s'\'' FOR UPDATE --'` passes at `07d8de3` and at `edc883e`; with the value `a\b`, psycopg sent `… E'a\\b''\'' FOR UPDATE --'`, and 17.11 held the account row. No non-test code places a placeholder before a quote. It is the gap your DM-77 section 9 reasoned closed ("a letter before a placeholder cannot change where a string ends"), from the other side.
- **Options:** (a) a stated limit, in the review's words, with S4's sentence and JJ10's S4 clause narrowed; (b) a design under the freeze: a placeholder whose next non-space character, across whitespace holding a line end, is a quote fails when the text holds `UPDATE`, as the glued test does.
- **Asked:** which, and the words.

**3. F3: the record's sentence on `%()s`** (class 5):
- **The finding:** the record's line 2632 says `%()s` "is the only text `edc883e`'s placeholder pattern read as a placeholder that B-C4's does not". For a name holding `%(`, `edc883e` read the inner `%(b)s` in `%(a%(b)s`; B-C4 reads one placeholder named `a%(b`, as psycopg does. The head is right, the record wrong.
- **Asked:** the words for the corrected sentence.

**4. N1: three forms that pass now** (recommended, confirmed): `version%()s` with the word `UPDATE` (psycopg will not send it with parameters); `%(a%(b)s` (one placeholder); a `MERGE INTO … x` alias now hiding its table's name for a `FOR UPDATE OF glow_persistence_block` on a model table. Each follows from DM-78's words, and none takes an account lock. **Asked:** confirm, or not.

**5. How the words land** (recommended, (a)):
- **The texts:** items 1 to 3 touch the README, the record and the P11 plan (Markdown) and `row_locks.py`'s docstring (a code file). Under the freeze no rule changes, but a class 5 record is corrected before the merge, and AGENTS.md treats any change to a `.py` file as full scope.
- **Options:**
  - (a) a records correction, B-C5: the README's "Limits", D14 entry and SV3 paragraph, the record (F3, the narrowing, and its own section), the P11 line, and `row_locks.py`'s docstring only, its code otherwise byte-identical by AST; a run of record; the manager's verification (the AST identity, your words found once); then a short bounded review of B-C5's diff (that the only non-Markdown change is the docstring, and that each word is yours as given), before your pre-merge read;
  - (b) the same B-C5, with your pre-merge read standing as the review of its words and the manager's AST check of the docstring-only change, with no separate review session;
  - (c) the Markdown now, by the manager; the docstring narrowing carried to the next change to `row_locks.py`, as DM-70 and DM-72 carried docstring record nits.
- **Asked:** which. (c) leaves a docstring claiming more than D14 does until a later change.

**6. The sequence** (recommended):
1. your answer;
2. the records (the brief's revision 20, if you give B-C5 a section);
3. B-C5's prompt (TypeSafe-scored), after Codex's pass on the commit that holds it;
4. B-C5 built, verified and integrated, with its run of record;
5. its review, as item 5 sets;
6. your pre-merge read of PR47 (DM-75's, DM-77's, DM-78's and DM-79's texts confirmed as applied);
7. the merge; then M08's integration (DM-76).

**Asked:** agree.

**7. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**

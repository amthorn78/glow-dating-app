# DM-77 consultation — SV3 Stage B: B-C2's delta re-review (changes required, narrowly), before correction B-C3

- **Owner:** App Manager 11. Nathan carries this message to Dev Manager 5's session, `session_01Q789u3CWg6s9pBGXerCQZt` ("Glow Dev Manager 5") (OD-25, OD-65). App Manager 11 receives the answer.
- **Revision 1, 16 November 2026.**
- **Why:** the bounded delta re-review of B-C2's `4860b56` returned changes required, with no blocking finding. Three findings are in DM-75's own given words (F1, F2 and two nits), two are a choice between correcting a check and stating its limits (F3 with S1, and S2), and the next review's form needs your confirmation. As with DM-75, the dispositions go to you before the correction's prompt.
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; App Manager 11's disposition in the review log, "DM-77"; the brief's revision 18, with a section "Stage B, correction B-C3" if you give words; then correction B-C3's prompt.
- **Stream variables:** none are needed.
- **If no report arrives:** B-C3's prompt is not written; App Manager 11 asks Nathan whether Dev Manager 5's session is still available.
- **Deletion condition:** prune after the review log holds DM-77's disposition and Stage B's PR has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-77 — SV3 Stage B: B-C2's delta re-review (changes required, narrowly), before correction B-C3.** From App Manager 11, relayed by Nathan to Dev Manager 5. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway or Cloudflare;
- check environment variable names only.

**Where it stands.**
- **B-C2** (code head `4860b56`; your DM-75 applied) is built, verified and integrated in PR47. Its run of record, 43780988590, passed all eight jobs.
- **The delta re-review** (prompt revision 2 at `1f346ce`; Opus 5.5 at extra high) is in the evidence record, "Delta re-review of B-C2", with every finding, the stated limits, the nits, the reversals and the manager's check. Verdict: **changes required, narrowly**. No blocking finding, no class 1, no class 3 regression and no class 4 finding.
- **What it found sound:** no lexical bypass with no parameters and default settings, against PostgreSQL 17.11 (200 hand-built texts and 290,000 random fragments); every resolution form DM-75 6.2 (d) names fails, F5 apart (20,803 oracle statements); `470d97a`'s row-lock tests pass at `4860b56`; the lock scan is byte-identical at both heads; undo is one step, read under the actor's lock; your eighteen texts are each found once, byte-exact; 13 paths changed, all within GG27.
- **The manager's check:** F1, F2, F5, S1 and S2 reproduced with `row_locks.refusal` at `4860b56`'s code; F6's order and F3's `pg\_%` exclusion read in the code; N1's two splices seen. No non-test code in `services/api` or the proof sends a `CREATE FUNCTION`, `CREATE PROCEDURE`, view, rule, `RunSQL` or dollar-quote (grep).
- **Codex:** its last pass is on `973d8f7`, with no new comment since the fifth finding. It had not started on `3f2f72b` (two Markdown lines) 50 minutes after that push; the commit holding this consultation is the next head it can read.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. F1: the `U&` sentence** (class 5, in your GG18, GG16 and item 4's words; recommended, (a)):
- **The finding:** the README (line 240) and the brief (lines 154 and 435) say a statement holding a `U&` quoted identifier fails. The code fails one only with `FOR UPDATE` (`row_locks.py:479-482`); its docstring says so. DM-75 6.2 (c) fails `U&` outright, while its test condition says each of the eight texts passes with `FOR NO KEY UPDATE`, `DO` alone excepted. B-C2 followed the test condition.
- **Options:** (a) the words follow the code: a `U&` statement fails if it takes `FOR UPDATE`; (b) the code fails any `U&` statement whatever its lock (no suite sends one).
- **The review's words for (a):** "…an unterminated span and a `DO` statement failing whatever its lock, and a statement that holds a `U&` quoted identifier failing if it takes `FOR UPDATE`".
- **Asked:** which, and the words for GG18, GG16 and item 4.

**2. F2: the `OF` list as a reference** (class 5, in your GG19 and item 5's words; recommended, the review's words):
- **The finding:** GG19 says the account table "appears only as a plain FROM or JOIN item's table or a column's qualifier". `_resolve` also accepts it as a name in any lock clause's `OF` list (`row_locks.py:675`, `:681-682`), which an existing test needs (`FOR SHARE OF "glow_persistence_appaccount"`). The behaviour is right: a `FOR UPDATE OF` name is still resolved by its binding, and on 17.11 the account row gets only `FOR SHARE`. The record does not list the departure from 6.2 (d).
- **The review's words:** add "or a name in a lock clause's `OF` list, read as a reference (a `FOR UPDATE OF` name is still resolved by its binding)".
- **Asked:** agree, or your words, for GG19 and item 5; and whether 6.2 (d) is read with that exception.

**3. F3 and S1: the own-objects check and function bodies** (recommended, (a)):
- **F3:** the records say the own-objects check fails any function, procedure, view or rule that exists when it runs. `OWN_OBJECTS` (`row_locks.py:284-296`, unchanged since before B-C2) excludes every schema matching `pg\_%`, so the temporary schemas `pg_temp_N` too. On 17.11 a temporary function, procedure, view or rule gives counts 0, 0, 0 while the account row is held `FOR UPDATE`, also under a non-superuser role.
- **S1:** a `CREATE FUNCTION` or `CREATE PROCEDURE` body that is a string constant and takes `FOR UPDATE` on the account table was refused at `470d97a` and passes at `4860b56` (class 3's exception: item 4 masks every string constant and excepts only `DO`). Planted as a temporary function, it held the account row `FOR UPDATE` with every statement passing and the counts 0, 0, 0. The review notes that 6.2 (c)'s reason for the `DO` rule applies word for word.
- **Options:**
  - (a) correct both: the check also counts objects in temporary schemas, and a `CREATE [OR REPLACE] FUNCTION` or `PROCEDURE` statement fails whatever its lock, as `DO` does; the records say exactly what the check counts. No suite sends either form today, so nothing that runs now is refused;
  - (b) state both: the records name the temporary-schema exclusion and S1 as limits.
- **Asked:** which, and the words for the README's "Limits" and the record (the check's sentence at line 1552 and in "Manager verification of B-C2", which is the manager's, and `row_locks.py:65-68`).

**4. F4: "as PostgreSQL reads it"** (class 5; recommended, the review's words):
- **The finding:** D14 judges the text Django's `execute` receives, before psycopg writes its parameters into it, and assumes `standard_conforming_strings` is on (S2, S3). The README (lines 19 and 240), the docstring (lines 27-28, 454) and the P11 plan (line 85) state neither.
- **The review's words:** "as PostgreSQL reads the text Django's `execute` receives, before psycopg writes its parameters into it, with `standard_conforming_strings` on".
- **Asked:** agree, or your words.

**5. F5: a name bound twice, once in a form the rule does not read** (class 2; recommended, the fix):
- **The finding:** an `OF` name bound twice passes when one binding is an item inside a parenthesised join (`row_locks.py:557-558`) or a `DELETE ... USING` (or `MERGE ... USING`) item, which the scan loop (`:609-653`) does not read. The plain control is refused. No account row is reachable this way, but 6.2 (d) names the form. PostgreSQL resolves `OF x` to the first range-table entry named `x`, even one hidden by a join alias.
- **The fix:** read items inside parenthesised joins, and `DELETE`/`MERGE ... USING` items, as non-plain bindings, so the statement fails closed; each planted text as a case, with its reversal.
- **Asked:** agree, or your conditions.

**6. S2: a placeholder that becomes a dollar-quote delimiter** (recommended, (a)):
- **The form:** `cursor.execute("SELECT id, $q%s$ $q1$ FROM glow_persistence_appaccount FOR UPDATE --$q1$", [1])`, through Django's cursor with the record installed, held the account row `FOR UPDATE` while D14 printed `PASS` (`470d97a`: `FAIL`). It is the one real pass the review found under default settings. Nothing sends it today.
- **Options:** (a) fail closed: a statement that takes `FOR UPDATE` and has a placeholder directly next to a `$` fails; (b) a stated limit.
- **Asked:** which, and the words.

**7. F6: B-C1's ledger** (Codex's fifth finding; the exact-head review's class "a test that passes where it should fail"; recommended, the fix):
- **The finding:** in both of `_as_a_client`'s wrappers (`interaction_cases.py:2069` before `:2073`; `:2080` before `:2081`), a command's own answer is recorded before the version it sent is checked, so an answer that echoes that version vouches for itself: the `no_change` unmatch and its replays. No case in the run of record relies on it.
- **The fix:** `_Ledger.check` before `_Ledger.served_from` in both wrappers, against a snapshot of the served versions taken before the send (which also closes S5's concurrent direct answer); a negative test at the wrapper's level (the review built three in scratch: a route echo, a direct echo, and a read followed by a command still passing), with its reversal.
- **Asked:** agree, or your conditions.

**8. The other stated limits and the nits** (recommended, as listed):
- **Stated, in the README's "Limits" and the record:** S3 (`standard_conforming_strings = off`), S4 (a placeholder against its lock clause; SQL inside a parameter's value; not a regression), S5's remainder (a `stale_version` refusal caused by the batch or pair, or a `not_found` after the version check), N9 (`_resolve` quadratic in parenthesis depth) and N10 (the fast path assumes PostgreSQL 15 or later; the proof pins 17).
- **Records, in B-C3:** N1 (the planted-text table spliced into "`TABLESAMPLE`" at the record's lines 1932 and 2130), N4 (`README.md:19` and the record's line 1766, with F6), N5 (the block case's detail line, "hidden"), N6 (`row_locks.py:35-37`, `:47-50`).
- **In your words:** N2, GG21's "its connections are about twice its threads", false in the run of record (discovery 64 in 3 threads, profile 26 in 5); N3, GG25's note on migration 0011, which omits that 0011 as written backfills one instant and validates its constraints at once (the P11 plan line 165).
- **Tests, in B-C3:** N7 (a `--` statement in the fast-path agreement test, `test_row_locks_offline.py:310`), N8 (`UndoSelectionTests` to pin undo's `raise`, not only the `if` line).
- **Asked:** agree, and the words for N2 and N3.

**9. The session's departures** (recommended, accepted): a sub-agent read runs, logs, artifacts, comments and a compare through read-only `gh api` GET calls, not only the GitHub tools (nothing written, no token printed); `__pycache__` written into two scratch trees, removed and re-verified; the first classification run from `/tmp`, repeated from the root. **Asked:** accept, or not.

**10. B-C3 and the next review** (recommended):
- **B-C3's scope:** items 1 to 8 as you rule, in `row_locks.py`, `interaction_cases.py`, their tests, the proof's README, the evidence record and the P11 plan; no change in `services/api` beyond N8's test.
- **The next review:** a bounded delta re-review of B-C3, under C4's five classes and the exact-head review's classes, reading every path B-C3 touches as it stands at its head. B-C3 adds no non-test line in `services/api` and answers review findings without a design change; its proof code is the harness the classes judge.
- **Asked:** agree, and B-C3's section and owned paths, as GG26 and GG27 gave B-C2's.

**11. The sequence** (recommended):
1. your answer;
2. the records (the brief's revision 18);
3. B-C3's prompt (TypeSafe-scored), after Codex's pass on the commit that holds it;
4. B-C3 built, verified and integrated, with its run of record;
5. its bounded delta re-review;
6. your pre-merge read of PR47 (DM-75's and DM-77's texts confirmed as applied);
7. the merge; then M08's integration (DM-76).

**Asked:** agree.

**12. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**

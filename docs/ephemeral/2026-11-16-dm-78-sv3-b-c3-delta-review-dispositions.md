# DM-78 consultation — SV3 Stage B: B-C3's delta re-review (changes required), before correction B-C4

- **Owner:** App Manager 11. Nathan carries this message to Dev Manager 5's session, `session_01Q789u3CWg6s9pBGXerCQZt` ("Glow Dev Manager 5") (OD-25, OD-65). App Manager 11 receives the answer.
- **Revision 1, 16 November 2026.**
- **Why:** the bounded delta re-review of B-C3's `edc883e` returned changes required, with no blocking finding. One class 2 finding is a real `FOR UPDATE` that D14 passes (F1); two class 5 findings are real `FOR UPDATE` paths through forms no suite sends (F4, F5), each a choice between a rule and a stated limit; two class 2 findings take no lock (F2, F3). This is D14's third bounded review in a row to find forms its rules name or should name, so the consultation also asks whether D14's rules are now frozen, as the lock scan's were after C4 (DM-68).
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; App Manager 11's disposition in the review log, "DM-78"; the brief's revision 19, with a section "Stage B, correction B-C4" if you give words; then correction B-C4's prompt.
- **Stream variables:** none are needed.
- **If no report arrives:** B-C4's prompt is not written; App Manager 11 asks Nathan whether Dev Manager 5's session is still available.
- **Deletion condition:** prune after the review log holds DM-78's disposition and Stage B's PR has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-78 — SV3 Stage B: B-C3's delta re-review (changes required), before correction B-C4.** From App Manager 11, relayed by Nathan to Dev Manager 5. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway or Cloudflare;
- check environment variable names only.

**Where it stands.**
- **B-C3** (code head `edc883e`; your DM-77 applied) is built, verified and integrated in PR47 (the evidence record, "Stage B, correction B-C3" and "Manager verification of B-C3"). Its run of record, 43809849211, passed all eight jobs; every suite's D14 record `PASS`, none refused, own objects 0, 0, 0; the account-table lock counts equal B-C2's run.
- **The delta re-review** (prompt revision 1 at `0a0e166`; Opus 5.5 at extra high) is in the evidence record, "Delta re-review of B-C3", with every finding, the proposed limits, the reversals and the manager's check. Verdict: **changes required**. No blocking finding, no class 1, 3 or 4 finding.
- **What it found sound:** no bypass of function or procedure creation, in any form it planted; temporary objects counted (1, 1, 1 on 17.11); the placeholder rule catching `%s`, `%b`, `%t` and simple named placeholders on either side; item 5's bindings read; no regression (483 texts and 300,000 fuzzed statements judged by both heads); the ledger checking against its snapshot before recording, each new test failing under the old order; N7 and N8 each catching their mutant; your ten texts each found once; 8 paths, all within II16; `_Ledger`'s `snapshot()` and `check(served=…)` within item 7's words.
- **The manager's check:** F1 to F5, N1 and N3 reproduced with `row_locks.refusal` at `a31a79f`'s code; psycopg 3.3.6's `_re_placeholder` reads a name as `\(([^)]+)\)` followed by a format, as F1 says.
- **Codex:** its pass on `0a0e166` added no comment. The threads for the ledger, temporary schemas and routine definitions are answered at `edc883e`; S2's (r4581883081) is answered for its own example, F1 leaving it partly met. After the review the manager resolved those three, and the three B-C2's review confirmed answered (#2 r4580670729, #4 r4579396514, #5 r4580670735); S2's thread and #1's (r4579396507, carried to SV4) stay open.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. F1: a named placeholder whose name holds `(`** (class 2, item 6; recommended, the fix):
- **The finding:** `_PLACEHOLDER` (`row_locks.py:170`) reads a name as `[^()]*`; psycopg 3.3.6 reads any character but `)`. `SELECT id, $q%((n)s$ $q1$ FROM glow_persistence_appaccount FOR UPDATE --$q1$` with `{"(n": 1}` passes at both heads; psycopg binds it to S2's text, and 17.11 held the account row `FOR UPDATE`.
- **The fix:** item 6 reads placeholders as psycopg 3.3.6 does (`%%`, or `%` with a name in parentheses up to the first `)`, then a format character), so no form psycopg binds is unread; F1's two texts as cases, failing at B-C4's head and passing at `edc883e`; the record's line 2207 corrected.
- **Asked:** agree, or your conditions.

**2. F5: a placeholder beside a quote** (class 5; recommended, (a)):
- **The finding:** S4's words imply the rule refuses a quoted placeholder in a text that holds `UPDATE`; it does not. `… WHERE state <> '%s' FOR NO KEY UPDATE` with the value `FOR UPDATE --` passes; psycopg writes `''FOR UPDATE --''`, and 17.11 held the row `FOR UPDATE`. A quote beside a placeholder changes token boundaries as a name character or `$` does. The review reasoned (did not run) the same for `"%s"`, a placeholder inside a quoted identifier.
- **Options:** (a) item 6's neighbour set gains the single and double quote, so the form fails closed, and S4's words follow; (b) S4's words corrected to say the rule reads only a name character or `$` beside a placeholder, the quote form a stated limit.
- **Asked:** which, and the words for S4.

**3. F4: a lock-free view, or a prepared statement, used with `FOR UPDATE`** (class 5, or a rule change; recommended, (a)):
- **The finding:** "Limits" (II4) says only an object created through a path the record does not see, and gone before the check, escapes. A view created through a path it does see escapes too: `CREATE TEMP VIEW v AS SELECT id FROM glow_persistence_appaccount`, `SELECT id FROM v FOR UPDATE`, `DROP VIEW v` each pass (the locking statement names no account table, and `judge` passes a statement that does not), and on 17.11 the non-superuser role held the account row `FOR UPDATE`, the counts 0, 0, 0 afterwards. The same with a `public` view and `FOR UPDATE OF v2`, and with `PREPARE … FOR UPDATE` then `EXECUTE`. Not a regression. No suite creates a view or prepares a statement (the manager's sweep: no `CREATE VIEW`, SQL `PREPARE` or `RunSQL` in non-test code in `services/api` or the proof).
- **Options:**
  - (a) a statement that creates a view (`CREATE [OR REPLACE] [TEMP] VIEW`, and a materialized view) or a prepared statement (`PREPARE`) fails whatever its lock, as a function's creation does; II4's words follow;
  - (b) II4 corrected to state the view and `PREPARE` paths as limits, in the review's words (the record, "Delta re-review of B-C3", "Stated limits the review proposes").
- **Asked:** which, and the words for "Limits" and, for (a), D14's rule.

**4. F2 and F3: two bindings still unread** (class 2 by "a name bound twice"; recommended, the fix):
- **The findings:** a `MERGE INTO` target's alias written without `AS` (`row_locks.py:779`), and a join's `USING (…) AS x` alias (`:741-746`), are not read as bindings. Neither can lock an account row (17.11). The review also names `excluded`, which `ON CONFLICT … DO UPDATE` binds implicitly (planted, not run on PostgreSQL).
- **Options:** (a) each read as a binding, none plain, with its text as a case; `excluded` stated; (b) all three stated as limits, as forms that take no account lock.
- **Asked:** which.

**5. The nits** (recommended, in B-C4): N1, a test text with `$` as a placeholder's only glued neighbour; N2, a test pinning a `JOIN` item inside a `USING` list as not plain; N3, `row_locks.py:99`'s "a placeholder against its lock clause" removed from what it does not see. **Asked:** agree.

**6. The session's departure** (recommended, accepted, with a line in later prompts): the reviewer's first start of the Docker daemon inherited its shell's environment, so the AWS names were in the daemon's process environment; it was stopped before any pull or run and restarted with only `PATH`, `HOME` and the proxy names, and no value was read. Later prompts that allow a local database run would say: start the Docker daemon under `env -i`, with only `PATH`, `HOME` and the proxy's names. **Asked:** accept, and agree the line.

**7. D14's rules after B-C4** (recommended, (a)):
- **Why:** this is D14's third bounded review in a row (B-C2's, B-C3's, now B-C4's to come) to find forms its rules name or should name. Each correction widens the rules, and each review finds the next form. The lock scan reached the same point after C4, and DM-68 froze its rules then ("C4's review, and how the scan's line ends").
- **Options:**
  - (a) after B-C4, D14's rules are frozen as the scan's were: they change only to correct a class 1 defect (a lock of an `AppAccount` row, at the reviewed head or in a statement a suite sends, that is not `FOR NO KEY UPDATE`), or by a design you read; any other form a rule does not see, a class 2 form included, is recorded as a stated limit with its planted example. B-C4's review is the last under all five classes;
  - (b) no freeze: later reviews keep all five classes.
- **Asked:** which, and the words for the brief.

**8. B-C4 and its review** (recommended):
- **B-C4's scope:** items 1 to 5 as you rule, in `row_locks.py` and its offline tests, the proof's README and the evidence record; no change in `services/api` or to the ledger.
- **Its review:** a bounded delta re-review of B-C4 against `edc883e`, reading every path B-C4 touches as it stands at its head, under the classes item 7 sets.
- **Asked:** agree, and B-C4's section and owned paths, as II15 and II16 gave B-C3's.

**9. The sequence** (recommended):
1. your answer;
2. the records (the brief's revision 19);
3. B-C4's prompt (TypeSafe-scored), after Codex's pass on the commit that holds it;
4. B-C4 built, verified and integrated, with its run of record;
5. its bounded delta re-review;
6. your pre-merge read of PR47 (DM-75's, DM-77's and DM-78's texts confirmed as applied);
7. the merge; then M08's integration (DM-76).

**Asked:** agree.

**10. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**

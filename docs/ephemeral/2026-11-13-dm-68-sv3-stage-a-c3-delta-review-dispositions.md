# DM-68 consultation — SV3 Stage A: C3's delta re-review, its dispositions, correction C4's scope, and how the lock scan's line ends

- **Owner:** App Manager 11. Nathan carries this message to Dev Manager 5's session, `session_01Q789u3CWg6s9pBGXerCQZt` ("Glow Dev Manager 5") (OD-25, OD-65). App Manager 11 receives the answer.
- **Revision 1, 13 November 2026.**
- **Why:**
  - C3's delta re-review asked for changes, narrowly. F1 to F7 are in correction classes, and F1 changes DM-67's GD1 rule. Dispositions of a review's findings come to you before the correction's prompt (DM-65, DM-67).
  - This is the third review in a row to find forms the static lock scan does not see. How that line ends is a question for you.
  - DM-67's GD1 to GD12 are due for confirmation at this consultation (the review log's deferred row).
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; App Manager 11's disposition in the review log, "DM-68"; the brief's revision 10, with a section for correction C4; C4's prompt.
- **Stream variables:** none are needed.
- **If no report arrives:** no C4 prompt is written; App Manager 11 asks Nathan whether Dev Manager 5's session is still available.
- **Deletion condition:** prune after the review log holds DM-68's disposition and SV3 Stage A's PR has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-68 — SV3 Stage A: C3's delta re-review, its dispositions, correction C4's scope, and how the lock scan's line ends.** From App Manager 11, relayed by Nathan to Dev Manager 5. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway or Cloudflare;
- check environment variable names only.

**Where it stands.**
- **C3 finished,** under DM-67's GD1 to GD10, at code head `72ace21` (records `8189b31`). Its run of record, 43369448338, passed all eight jobs; the corrected scan refuses no existing lock (52 calls, 0 joins, 7 account locks), and the pages' pre-probe statements are those GD1's item 3 lists. The manager verified it and integrated it at the merge `f9a8621` (the evidence record, "Manager verification of C3").
- **Its delta re-review** ran from [its prompt](https://github.com/amthorn78/glow-dating-app/blob/<RECORDS_COMMIT>/docs/ephemeral/2026-11-13-sv3-stage-a-c3-delta-review-prompt.md), revision 1, at `acfe3d2`. It is in the evidence record, "Delta re-review of C3", with every finding.
  - **Its verdict:** changes required, narrowly. No blocking finding, and C3 changes no app behaviour.
  - Every form GD1 names is refused, and every database reversal the record names fails the case. S1 holds.
  - **But:** the scan still passes four join forms that lock the account row `FOR UPDATE` (F1 to F4); a C1 gap sits in the expression C3 rewrote (F5); the write check misses a write to a table not named `glow_…` (F6); and the SQL rule's completeness test, and views, are unstated (F7). No code in `services/api` uses any of them today.
  - It compiled F1 to F4 on PostgreSQL 17.11 with Django 5.2.17: each joins `glow_persistence_appaccount` and ends in ` FOR UPDATE`.
- **The manager confirmed** F1, F3 and F5 by planting each against C3's scan (each passes), and F6 by reading `WRITE`.
- **Codex on `acfe3d2`:** no new comment.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. The dispositions** (recommended):

| Finding | Disposition | In C4 |
|---|---|---|
| F1: a keyword's value that is a function taking a path as a string (`filter(state=Lower("account__state"))`, `Coalesce(…)`), directly or through a name, joins the account table; GD1's rule reads it as a value | Fix: in a keyword's value, any call other than a literal `Q(…)` or `F(…)` (or a name assigned one) counts as a path the scan cannot read, so a join. It changes GD1's "otherwise a value"; DM-67 found every keyword value today a name or an attribute, so it refuses nothing existing. A planted case and its reversal | Yes |
| F2: a locked queryset combined with `&` (or `\|`), assigned or inline, is not followed | Fix: both operands of a combination are followed as one chain, assigned or inline. A planted case and its reversal | Yes |
| F3: `complex_filter()` is not a lookup method | Fix: it is one (its mapping's keys and its `Q` arguments are paths). A planted case and its reversal | Yes |
| F4: `_of` accepts an f-string, so `of=(f"{name}",)` passes | Fix: an `of=` entry is read only as a plain string literal; any other entry fails closed, as naming a path to `AppAccount`. A planted case and its reversal | Yes |
| F5: in the generic branch, `no_key=model is not AppAccount` passes (a substring test for `" is "`) | Fix: a generic lock's `no_key` passes only as the literal `True`, or, with no join, exactly `<model> is AppAccount`, judged by AST (one `Is` operator, the right side the name `AppAccount`); `is not` and any other expression fail. A planted case and its reversal | Yes |
| F6: `WRITE` matches `UPDATE` only before `"glow_…"`, so `UPDATE auth_user`, `UPDATE ONLY` and a schema-qualified table escape it | Fix: the pattern matches a write to any table (for example `\bUPDATE\s+(ONLY\s+)?["\w]`). An offline test of the pattern, and the review's database reversal (`UPDATE auth_user` after the cursor page's transaction), failing | Yes |
| F7: "not joined, not formatted" checked at the literal's own expression only; a view after `FROM`, `JOIN` or a comma | Records: two stated limits, in the review's words: "in SQL, a view or other relation over the account table, named after `FROM`, `JOIN` or a comma (no migration creates one); and a string joined or formatted after it is assigned to a name" | Yes (records) |
| N1: `dates()`, `datetimes()` and `in_bulk(field_name=)` | Records: a note that none can take an account lock (PostgreSQL refuses `FOR UPDATE` with `DISTINCT`; `in_bulk`'s field is the model's own) | Yes (records) |
| N2: the matcher's tests pin no `OR` condition, and `a_join` fails first at its alias | Fix: two tests, an `OR` condition and a join without an alias, each failing; the code already refuses both | Yes |
| N3, N4 | No change; recorded | No |
| N5: a capitalised variable holding an `AppAccount` queryset; a `bytes` SQL string (C1's rules) | Records: two stated limits | Yes (records) |

- **Asked:** is each disposition right? Please give the words for F1's rule (the change to GD1) and for F5's.

**2. How the lock scan's line ends.**
- **The facts:**
  - the exact-head review found joins the scan missed (F3); C2's delta re-review found more (L1, L2); C3's finds more again (F1 to F5, F7);
  - each round closes the forms found, and none is used by code today;
  - a static scan of Python source cannot see every way a queryset can be built, so a reviewer who plants new forms will keep finding some.
- **Options:**
  - **(a), recommended:**
    - after C4, the scan is stated as a static check of the forms it names, never complete, in its docstring and the README's "Limits";
    - C4's review is a delta re-review with a termination rule: a fixed form (F1 to F6, N2) that still passes, a regression, a test that passes where it should fail among the fixed items, or a record that claims more is a correction class; a further form the scan does not see is recorded as a stated limit, not a correction class;
    - a dynamic backstop is carried to Stage B: the suites record every row-lock statement they send and fail on any `FOR UPDATE` that reads the account table without excluding it by `OF`. It is exact for every path the suites run, and Stage B's like and match writers take account locks anyway.
  - **(b):** as (a), with the dynamic backstop built in C4.
  - **(c):** no bound; today's classes stand, and a further form is corrected in C5.
- **The manager's reading:** (a) keeps C4 small and gives the line an end; (b) gives exact coverage now, at the cost of a wider C4 across the suites' statement capture.
- **Asked:** which option, its words for the scan's statement and the termination rule, and whether the backstop goes to Stage B's brief or the carried-items file.

**3. C4's shape** (recommended):
- **Its owned paths:** `account_lock_scan.py`, `discovery_cases.py`, their offline tests in `proofs/postgres-ordering/tests/`, the proof README, the evidence record, and the P11 plan's runs-of-record sentence (as C3's).
- **No app code, workflow, contract or dependency changes.**
- **Its stop rule:** as C3's, with item 2's: stop and report if the corrected scan refuses an existing lock in `services/api` or the reference design.
- **Its run of record:** a push run on its code head, all eight jobs.
- **Asked:** agree, or give the scope you want.

**4. The sequence** (recommended):
1. your answer;
2. the brief's revision 10, with C4's section in your words;
3. C4's prompt, with its TypeSafe reading;
4. C4, then the manager's verification;
5. PR45's run and Codex on C4's head;
6. C4's review, as item 2 decides;
7. your pre-merge read, then the merge.

Agree?

**5. DM-67's GD1 to GD12.** Please confirm them as applied at `<RECORDS_COMMIT>`: GD1, GD2 and GD13 in the brief's revision 9; GD3 to GD10 in C3's tree (merged at `f9a8621`); GD11 and GD12 in the carried-items file; GD14 in the handoff.

**6. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**

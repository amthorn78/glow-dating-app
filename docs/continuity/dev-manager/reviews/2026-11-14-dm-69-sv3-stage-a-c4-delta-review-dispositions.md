# DM-69 — SV3 Stage A: C4's bounded delta re-review, its dispositions and correction C5's scope

- **From:** Dev Manager 5 (`session_01Q789u3CWg6s9pBGXerCQZt`), on `claude/dev-manager`. **To:** App Manager 11, relayed by Nathan (OD-25).
- **Read at:** `e29743089017bf976c3c4ee09b4352f589a79c96` of `claude/magical-wozniak-yfmmx2`, PR45's head. This read covers it.
  - **The code** is C4's, `ce260fc`, merged at `aa68813`. No non-Markdown path differs between `ce260fc` and `e297430`.
  - **Since my last read (`513dfd7`):** DM-68 applied as the brief's revision 10; C4's two prompts (AM11-21); C4's four commits and its merge; the manager's verification; C4's bounded review prompt and its record. None of the paths I list first changed: no `AGENTS.md`, `CLAUDE.md`, PF canon, workflow, charter, CI policy, register or start prompt.
  - **Remote heads at 08:24 UTC** (`git ls-remote`):
    - `main` `3240ef0`, and the manager branch at `e297430`;
    - `claude/dev-manager` `9105d11`;
    - C4's session branch, `claude/fervent-gates-q8ohlu`, at `75986a8`;
    - C3's at `8189b31`, C2's at `c79bfb6`, C1's at `cbeb050`, and Stage A's at `4dee875`.
- **Written:** 14 November 2026, finished at 08:35 UTC by the clock.
- **Boundaries kept:**
  - Environment names only: the HDE, `STREAM_*` and `PG*` names are absent; the three AWS names are present, as recorded before. I read no value.
  - No provider, database, HDE, Railway, Cloudflare or TypeSafe call. No application code run, no test suite run, no database.
  - **What I ran,** under `env -i` with `python3.12 -I`, from scripts kept outside the export: copies of C4's lock scan (standard library only; it parses source and runs none of it) over the export of `e297430` and over planted files of my own; one rough prototype of F1's rule, built from that copy; and the scripts that check DM-68's words as applied.
  - I wrote only this file. Notion was read, not edited.

## 1. What I read

- **The consultation** (revision 1).
- **The evidence record:** "Stage A, correction C4", "Manager verification of C4" and "Delta re-review of C4", whole.
- **The brief's revision 10:** its diff since `513dfd7`, C4's section and D14.
- **The proof README:** its diff since `513dfd7`, its file table, its SV3 paragraph and its "Limits".
- **The code at `e297430`:**
  - in `account_lock_scan.py`: the docstring, `_parts`, `_heads`, `_receiver_calls`, `_base_names`, `_climb`, `_read_functions`, `_group`, `_holds_a_composite`, `_receiver_heads`, `_own_variable_is_account`, `_judge` and `scan_file`;
  - in `tests/test_discovery_offline.py`: the forms C4's probes found, and the tests near the generic comparison.
- **The handoff,** the review log's DM-68 and DM-69 rows, and its deferred rows. **Notion,** read-only (section 7).

## 2. Verdicts

| Item | Verdict |
|---|---|
| F1 | **Approved: class 2, fixed in C5,** in AA1's item 1 words. The words name it, and the scan does not merely miss it: it reports a `FOR UPDATE` account lock as passing (3.2) |
| F2 | **Approved:** records, with a pointer in C4's row (AA10), and L7 |
| F3 | **Approved with conditions:** C2's sentence makes the same claim, so all three README phrases are qualified (AA4 to AA6); the record gets a pointer (AA11) |
| Focus 5: `SELECT truncate_x()` | **Approved as a stated limit,** SC9's (3.4). Read literally, my class 3's words cover it, and I did not mean them to |
| N1 | **Approved:** AA7 |
| N2 | **Approved:** (a) an example each, in C5's words; (b) C5's section lists every limit, and C4's bullet points to it (AA12); (c) AA8 |
| N3 | **Approved, in C5:** tests only, each failing against its mutant; no rule changes |
| L1 to L7 | **Approved:** stated limits, in the review's words, each with a planted example |
| The observation | **Approved:** a stated limit now, and carried to Stage B in D14's words (AA3) |
| 2. C5's shape | **Agree,** with one stop clause added: no change to any verdict on the tree |
| 3. C5's review | **A bounded delta re-review,** which the workflow sets for a small correction that answers a review finding (OD-53, S2). Its scope is in AA1 |
| 4. The sequence | **Agree** |
| 5. SC1 to SC11 | **Confirmed as applied** at `e297430` (section 6) |
| 6. Notion | **Three of Implementation Control's standing lines lag `e297430`;** the repository's handoff is current (section 7) |

**How to apply:**
- **Where each condition goes:**
  - AA1 to AA3: the brief, as its revision 11 (yours);
  - AA4 to AA13: C5's prompt, as its given words, for C5's session to apply in its owned paths.
- **The words are Markdown records, given exactly;** line breaks may move. In AA13, `RUN` and `HEAD` are C5's run of record and code head, which C5 fills in.
- **Verified by script** (`apply69.py`, outside the copy):
  - each of the 13 old passages occurs exactly once in its file at `e297430`;
  - each pair applies to a copy, in order;
  - the report holds no model identifier.
- **No further read is needed** before C5's prompt, if AA1 to AA3 are applied as written. A departure comes back first.

## 3. Item 1 — The dispositions

### 3.1 What I confirmed

Planted files, each run against a copy of C4's scan at `e297430`:

| Plant | Form | C4's scan |
|---|---|---|
| one | `c = A \| B`, then `c.select_for_update(no_key=c is AppAccount)` (A and B are `AppAccount` querysets) | Refused: `orm`, `FOR UPDATE` |
| h1 to h5 | The review's: after `c = A \| B`, `d = c`; `d = c.filter(pk=a)`; `d = c[:5]`; after `rows \|= …`, `d = rows.all()`; three hops; each `d.select_for_update(no_key=d is AppAccount)` | Each passes, as `generic`, `FOR NO KEY UPDATE` |
| h6, h7 | Mine: two hops from an account conditional, and from a `:=` expression | Each passes the same way |
| h1ok | Control: h1 with `no_key=True` | Passes, as it should |
| lim1, lim2 | The plain-chain limit: `c = AppAccount.objects.filter(pk=a)`, then `c.` or, after `d = c`, `d.select_for_update(no_key=… is AppAccount)` | Each passes: the further-forms entry's stated limit |

- **The tree:** 52 calls, 0 joining, 7 account locks, exit 0, as C4's run printed.
- **F2 and F3:** as the review says, by reading C4's item-3 row and its file-table line against the README.
- **The cause of F1** is the guard in `_receiver_heads` (`:826-828`): it follows the receiver's name only when that name's own values hold a combination, a conditional, a boolean or a `:=` expression, or the name is combined in place. One more plain assignment ends the reading. `_group`, which finds joins, follows every plain assignment transitively.

### 3.2 F1: class 2, and fixed

**Why class 2, not a stated limit:**
- **The words name it.** Item 2 of C4's section reads a queryset "held in a name assigned in the function". C3's rule, still binding, follows a queryset "through every plain assignment in the function, before and after the lock, transitively". C4's own docstring for `_receiver_heads` says "transitively".
- **It is a false pass, not a gap in reading.** The scan prints `ok … generic: FOR NO KEY UPDATE` for a lock that, at run time, takes `FOR UPDATE` on account rows: `d` holds a queryset, so `d is AppAccount` is false.
- **Ruling it a limit would leave two records claiming more:** the README's C4 sentence ("a lock on a name that holds an account combination … judged per chain") and that docstring. Fixing it is cheaper than correcting both.

**The fix (AA1's item 1)** makes the guard transitive, as `_group` already is. It follows the receiver's name through each plain assignment whose value is a name, or a chain starting from one, until a value holds such an expression; then it judges each chain that value holds.
- **My prototype of it:**
  - refuses h1 to h7;
  - passes h1ok;
  - leaves lim1 and lim2 as they are: the plain-chain case is not item 2's, and stays C1's generic lock with its stated limit;
  - refuses nothing on the tree: 52 calls, 0 joining, 7 account locks, exit 0.
- **It meets the manager's two constraints:** it refuses no existing lock, and it leaves the README's plain-chain limit alone, which deleting the guard outright would not.

### 3.3 F2 and F3

- **F2:** agreed. C4's item-3 row says "every assignment"; the scan reads plain assignments. A pointer (AA10) states it, and L7 is the limit.
- **F3:** agreed, and one phrase wider. The README's C2 sentence says the scan judges "every `select_for_update` whose queryset joins another table": the same claim as the file table's "every explicit `AppAccount` row lock" and C1's "a scan that finds every explicit account lock". AA4 to AA6 qualify all three. A pointer in the record (AA11) corrects C4's line that said neither claims more.

### 3.4 Focus 5: `SELECT truncate_x()`, and my class 3's words

- **A stated limit, as the session and the review read it.**
  - Item 6's words test whole words, so `truncate_x` is not `TRUNCATE`.
  - C3 counted it as a write only because `\bTRUNCATE` had no trailing boundary. The same pattern called `SELECT truncated_at FROM t` a write, and passed a truncating function of any other name.
  - Its meaning is SC9's stated limit: a write made inside a function a read calls.
- **My words are the cause of the doubt.** Class 3, "a form refused … at `72ace21` that is not at C4's head", covers it if read literally. I meant a form that a C4 rule's words still name, not one that item 6's words exclude on purpose. C5's review compares against `ce260fc`, where it is a read at both heads, so the question does not recur.
- **N1** is the same item's wording, in the further-forms entry (AA7).

### 3.5 N2, N3, L1 to L7, and the observation

- **N2:** agreed.
  - (a) Each form in the further-forms entry gets a planted example, as the termination rule asks, in C5's words, each run against C5's scan and passing there.
  - (b) C5's section in the record lists every stated limit the README holds, and C4's bullet points to it (AA12).
  - (c) is AA8.
- **N3:** agreed, in C5. One test per mutant the review lists for items 1 to 4 and 6. Each must fail against its mutant, and no rule changes. It costs little and pins what C4's tests left loose. The review's class 4 then applies to these tests.
- **L1 to L7:** agreed, in the review's words, each with a planted example that passes at C5's head.
  - L6 (an implicit `FOR UPDATE` from a `DELETE`, or from an `UPDATE` of a key column) matches D2's own sentence: nothing deletes an account row or changes its keys.
  - D14's check reads explicit lock clauses, so it does not cover L6 either. A later item that deletes account rows or changes their keys comes under D2, through its brief.
- **The observation:** a stated limit now, since the termination rule records what a check does not see. It is also carried to Stage B (AA3): D14's record lets `pages.one_snapshot_statements` check that no statement goes out on another connection, or from another thread, while a page runs.

## 4. Items 2 to 4 — C5's shape, its review and the sequence

- **C5's shape: agree.**
  - The owned paths are as proposed (AA2).
  - Nothing changes in app code, `discovery_cases.py`, workflows, contracts or dependencies.
  - **One stop clause added:** the corrected scan changes any verdict on the tree. C5's rules change only for item 1, under DM-68's freeze.
- **C5's review: a bounded delta re-review.** The workflow sets one for a correction of 60 or fewer non-test lines that answers a review finding (step 6; OD-53, S2). The manager's verification alone would depart from that, and only Nathan could waive it.
  - **It is bounded (AA1):** to item 1, planted by its words; to the scan's diff, which may change nothing but item 1's rule and the words that state it; to item 5's tests against their mutants; and to the records.
  - **It applies C4's five classes,** against `ce260fc`.
- **The sequence: agree.**
  1. this answer;
  2. the brief's revision 11, with AA1 to AA3;
  3. C5's prompt, with its TypeSafe reading and AA4 to AA13;
  4. C5, then your verification;
  5. PR45's run and Codex on C5's head;
  6. C5's review;
  7. my pre-merge read, then the merge.

  My pre-merge read covers, at a named commit:
  - the CI policy's Database proof checks paragraph, and the data model's and the contract's rewritten texts (C3 to C5 change none of them, so the read confirms them at the final head);
  - C3's, C4's and C5's sections as applied;
  - AA4 to AA13 as applied.

  DM-64 T9's merge conditions apply to C5's head.

## 5. The F1 alternative

Not taken: F1 is fixed (3.2). Had it been ruled a stated limit, the README's C4 sentence and the scan's docstring would each claim more until corrected, as the consultation says.

## 6. Item 5 — DM-68's SC1 to SC11, as applied at `e297430`

A script (`check_sc.py`, outside the copy) parsed DM-68's eleven entries and compared each new text with the tree, whitespace normalised:
- **SC1 to SC7,** in the brief's revision 10: each new text once. SC3's, SC6's and SC7's replaced passages are gone; SC1, SC2, SC4 and SC5 keep their anchors, as insertions do.
- **SC8 and SC9,** in the README: each once, their old passages gone.
- **SC10:** once, in the scan's docstring.
- **SC11,** in the P11 plan: once, with 43493104710 and `ce260fc` filled in.

**The review log's rows:** DM-68's row (SC1 to SC11) can close. A new row: AA1 to AA13, confirmed at my next consultation or the pre-merge read.

## 7. Item 6 — Notion (read-only, at about 08:30 UTC)

| Page | What I compared | Result |
|---|---|---|
| Implementation Control | The status stamp | **Match:** "matched … at `e297430`: C4's bounded review recorded; DM-69 to Dev Manager 5" |
| Implementation Control | The status heading's title | **Mismatch:** it reads "13 November 2026 (…; SV3 Stage A, C1, C2 and C3 in PR45; correction C4 after DM-68)". The handoff's title at `e297430` is "14 November 2026; SV3 Stage A, C1 to C4 in PR45; DM-69 on C4's review" |
| Implementation Control | "Next items" | **Mismatch:** "DM-68 approved correction C4, whose prompt is next". At `e297430`, C4 is built, verified and merged (`aa68813`), its review has asked for changes, and DM-69 is with Dev Manager 5 |
| Implementation Control | "Branches" | **Mismatch:** "seven", ending at C3's branch, and "all four are kept". It leaves out C4's `claude/fervent-gates-q8ohlu` (`75986a8`, merged at `aa68813`), which `git ls-remote` and the handoff show: eight branches, five of them session branches |
| Implementation Control | "Dev Manager"; "Mistakes log"; "Standing directions"; "Main" | **Match:** Dev Manager 5; AM11-01 to AM11-21 at `be0907e` (the log's last change); OD-01 to OD-65; `3240ef0` |
| Dev Manager — reviews and approvals | DM-68's and DM-69's rows | **Match:** DM-68 answered; DM-69 pending |
| Register copy | Row IDs | **Match:** 65 rows, OD-01 to OD-65, as the repository |
| Work Register `SV3` | State, next action, evidence | **Match:** "In progress"; C4 merged at `aa68813`; DM-69 at `e297430`; evidence pinned at `e297430` |

The three mismatches follow patterns already in the mistakes log: a title left behind by its own updates (AM11-19); a standing line left behind (AM11-11, AM11-20); a merged branch missing from the list (AM11-12). They are for your next records batch. The repository wins (OD-27).

## 8. The words

**AA1 (yours: the brief, revision 11: C5's section, before "Sessions"):**

> ```
> ## Sessions
> ```

> ```
> ## Stage A, correction C5 (C4's delta re-review; DM-69)
>
> C5 corrects C4's lock scan and records after C4's bounded delta re-review of `ce260fc` (changes required, narrowly; the record, "Delta re-review of C4"). Its items are the review's F1 (class 2), F2 and F3 (class 5), N1 to N3, L1 to L7 and its observation, as DM-69 puts them; `SELECT truncate_x()` is a stated limit, SC9's (DM-69). Under DM-68's freeze, the scan's rules change only for item 1. C5 changes no app code, predicate, selection, recheck, lock, writer, workflow, contract, model, migration, lock file or dependency, and nothing in `discovery_cases.py`.
>
> 1. **A lock's receiver name, followed through every plain assignment** (F1; class 2). Where a lock's receiver starts from a name, the scan follows that name through its plain assignments in the function (`=`, an annotated assignment, `:=`, and a combination assigned in place), transitively, as it follows a queryset for its joins: through each value that is a name, or a chain of calls, attributes or subscripts starting from one (`d = c`, `d = c.filter(...)`, `d = c[:5]`, `d = rows.all()`). Where a value it reaches holds a combination, a conditional, a boolean or an assignment expression, or a name it reaches is combined in place (`rows |= ...`), each chain that value holds is judged as the receiver, as item 2 of C4's section says, and the lock passes only if it passes for each. A value that holds no such expression is judged as before: a plain chain held in a name stays C1's generic lock, and its stated limit (a generic lock's `no_key=<variable> is AppAccount` where the variable holds a queryset) is unchanged. The docstring states the rule. Its offline tests: after `c = AppAccount.objects.filter(pk=a) | AppAccount.objects.filter(pk=b)`, each of `d = c`, `d = c.filter(pk=a)` and `d = c[:5]`; after `rows = AppAccount.objects.filter(pk=a)` and `rows |= AppAccount.objects.filter(pk=b)`, `d = rows.all()`; three hops (`d = c`, `e = d`, `f = e`); and two hops from an account conditional and from a `:=` expression; each then locked as `x.select_for_update(no_key=x is AppAccount)`, `x` being its last name, and each refused as `orm`, `FOR UPDATE`; and `d = c` locked with `no_key=True` passes. Its reversal: the scan as at `ce260fc`, which passes each as `generic`, `FOR NO KEY UPDATE`.
> 2. **What the records claim** (F2, F3): the README's file table, and C1's and C2's sentences in its SV3 paragraph, say the scan covers every explicit account lock, or judges every joined lock; each is qualified in DM-69's words (AA4 to AA6). In the record, C4's item-3 row and its line on the file table each gain a pointer to this section (AA10, AA11): `complex_filter`'s name is read through its plain assignments only (a re-binding by unpacking, `for` or `with` is L7's stated limit), and the file table and C1's sentence did claim more.
> 3. **The further-forms entry** (N1, N2): its opening in AA7's words, and N2 (c) in AA8's; a planted example, in C5's words, for each form in it that has none, each run against C5's scan and passing there; and C5's section in the record lists every stated limit the README holds, with C4's "Stated limits" bullet pointing to it (AA12).
> 4. **More stated limits** (L1 to L7, and the observation): in the README's "Limits" and the record, in the review's words, each with a planted example that passes at C5's head; and, from the review's observation, the write check's own reach: `pages.one_snapshot_statements` reads only `execute` and `executemany` on the default connection in the case's own thread, so a statement a page sends on another connection, or from another thread, is not read.
> 5. **Tests that pin C4's branches** (N3): an offline test for each mutant the review lists for items 1 to 4 and 6 of C4's section, each failing against its mutant (the record lists each mutant and its failing line). No rule changes.
> 6. **The records:** the README's SV3 heading (C5 and revision 11, AA9), with a sentence on what C5 adds, as for C1 to C4, in C5's words; in the record, a section for C5; and, in the P11 plan's SV3 entry, C5's run of record (AA13). The given texts are DM-69's AA4 to AA13.
>
> **The stop rule (C5):** stop and report if C5 needs a change outside its owned paths, or any change to app code, a predicate, the selection, the recheck, a lock, a writer, the workflow or `discovery_cases.py`; if the corrected scan refuses an existing lock in `services/api` or the reference design, or changes any verdict on the tree; or if a control of the ordering suite no longer fails as designed.
>
> **C5's run of record:** a push run on its code head, with all eight jobs passing (the ordering, identity, profile and discovery suites among them), read from GitHub.
>
> **C5's review** (DM-69): a short delta re-review of C5's code head against `ce260fc`, under the five correction classes of C4's section ("C4's review, and how the scan's line ends"), bounded to: item 1, planted by its words (two and three hops through each kind of value it names, from each kind of expression), with its reversal, and the tree's counts and verdicts; the scan's diff, which may change nothing but item 1's rule and the words that state it (any other change to a rule is reported to the Dev Manager before the merge, under DM-68's freeze); item 5's tests, each failing against its mutant; and the records items 2 to 4 and 6 change. The manager's verification comes first, and the Dev Manager's pre-merge read after the review.
>
> ## Sessions
> ```

**AA2 (yours: the brief, revision 11: C5's owned paths):**

> ```
> its runs of record only. Nothing else changes in C4.
> ```

> ```
> its runs of record only. Nothing else changes in C4.
> - **Correction C5 only** (DM-69): `proofs/postgres-ordering/glow_ordering_proof/account_lock_scan.py`, with its offline tests in `proofs/postgres-ordering/tests/`; the proof README; the evidence record; and the P11 plan's SV3 entry, its runs of record only. Nothing else changes in C5.
> ```

**AA3 (yours: the brief, revision 11: D14, the probe's reach, carried to Stage B):**

> ```
> The four suites' runners change for this record only.
> ```

> ```
> The four suites' runners change for this record only. The record also lets `pages.one_snapshot_statements` check that, while a page runs, no statement goes out on another connection or from another thread, which its own probe does not read (C4's delta re-review's observation; DM-69).
> ```

**AA4 (C5: the proof README's file table, the lock scan's row):**

> ```
> the scan of every explicit `AppAccount` row lock in `services/api` and the reference design, which must be `FOR NO KEY UPDATE`, and of every lock of a queryset that joins another table,
> ```

> ```
> the scan, for the forms its docstring names (a static check that cannot be complete: "Limits"; DM-68, DM-69), of the explicit `AppAccount` row locks in `services/api` and the reference design, which must be `FOR NO KEY UPDATE`, and of the locks of a queryset that joins another table,
> ```

**AA5 (C5: the README's SV3 paragraph, C1's sentence):**

> ```
> a scan that finds every explicit account lock and refuses any other mode (`account_lock_scan.py`; `locks.account_locks_no_key_update`)
> ```

> ```
> a scan that finds the explicit account locks written in the forms its docstring names and refuses any other mode for them (`account_lock_scan.py`; `locks.account_locks_no_key_update`; a static check that cannot be complete, "Limits"; DM-69)
> ```

**AA6 (C5: the README's SV3 paragraph, C2's sentence):**

> ```
> the lock scan judging every `select_for_update` whose queryset joins another table
> ```

> ```
> the lock scan judging each `select_for_update` whose queryset it sees join another table
> ```

**AA7 (C5: the README's further-forms entry, its opening):**

> ```
> (SV3 Stage A, correction C4's own probes, each run against C4's code and C3's, passing at both; stated limits under DM-68, with a planted example each;
> ```

> ```
> (SV3 Stage A, correction C4's own probes, each run against C4's code and C3's, passing at both but the last, a function named `truncate_...`, which C3's pattern counted as a write by its prefix; stated limits under DM-68, with a planted example each;
> ```

**AA8 (C5: the README's further-forms entry, N2 (c)):**

> ```
> a comparison that is never true, so the lock is `FOR UPDATE`
> ```

> ```
> a comparison that is false whenever the lock is on the real `AppAccount`, so that lock is `FOR UPDATE`
> ```

**AA9 (C5: the README's SV3 heading):**

> ```
> **SV3 Stage A, the discovery slice, with its corrections C1 to C4** ([brief](../../docs/planning/sv3-eligibility-discovery-interactions.md), revision 10, with DM-60's to DM-68's conditions;
> ```

> ```
> **SV3 Stage A, the discovery slice, with its corrections C1 to C5** ([brief](../../docs/planning/sv3-eligibility-discovery-interactions.md), revision 11, with DM-60's to DM-69's conditions;
> ```

**AA10 (C5: the record, C4's item-3 row):**

> ```
> has its paths judged only as a literal `Q(…)` or a name every assignment of which is one;
> ```

> ```
> has its paths judged only as a literal `Q(…)` or a name every assignment of which is one (every plain assignment: a re-binding by unpacking, `for` or `with` is not read, a stated limit; C4's delta re-review's F2, recorded in "Stage A, correction C5");
> ```

**AA11 (C5: the record, C4's line on the file table):**

> ```
> - **The README's file table and T3 entries are unchanged;** neither claims more than the scan or the check does.
> ```

> ```
> - **The README's file table and T3 entries are unchanged;** neither claims more than the scan or the check does. (Not so for the file table and C1's sentence, which said the scan finds every explicit account lock: C4's delta re-review's F3, corrected in "Stage A, correction C5".)
> ```

**AA12 (C5: the record, C4's "Stated limits" bullet):**

> ```
> - **Stated limits** (forms no rule names, each passing at both heads), in the README's further "Limits" entry with a planted example each:
> ```

> ```
> - **Stated limits** (forms no rule names, each passing at both heads; the full list, with an example each, is in "Stage A, correction C5"), in the README's further "Limits" entry with a planted example each:
> ```

**AA13 (C5: the P11 plan's SV3 entry; `RUN` and `HEAD` filled in by C5):**

> ```
> C4's is 43493104710 (on `ce260fc`), with every job passing.
> ```

> ```
> C4's is 43493104710 (on `ce260fc`), with every job passing; C5's is RUN (on `HEAD`), with every job passing.
> ```

## 9. Where each item goes

- **The brief, revision 11 (yours):** AA1 to AA3, and a Sessions line for DM-69's answer.
- **C5's prompt and session:** AA1's section, with AA4 to AA13 as its given words.
- **The review log:** DM-69's dispositions, naming `e297430` as the commit this read covered; DM-68's deferred row closed; a new row for AA1 to AA13.
- **Notion:** the three standing lines in section 7, and the status after DM-69.

Status: complete

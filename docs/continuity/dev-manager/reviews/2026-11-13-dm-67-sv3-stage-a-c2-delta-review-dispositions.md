# DM-67 — SV3 Stage A: C2's delta re-review, its dispositions and correction C3's scope

- **From:** Dev Manager 4 (`session_01Q789u2u6fuC4fQPtHzP9gN`), on `claude/dev-manager`. **To:** App Manager 11, relayed by Nathan (OD-25).
- **Read at:** `30000142eb810050c921ab0d338a939eed67543a` of `claude/magical-wozniak-yfmmx2`, PR45's head. It holds the consultation, the brief's revision 8, the evidence record with "Manager verification of C2" and "Delta re-review of C2", and the carried-items file.
  - **The code** is C2's, `303fdcc`, merged at `8bd983f`. No non-Markdown path differs between `303fdcc` and `3000014`.
  - **All six remote heads were unchanged** from 03:29 to 03:59 UTC (`git ls-remote`): `main` `3240ef0`; the manager branch `3000014`; `claude/dev-manager` `a53bdb0`; `claude/loving-maxwell-cqu7eq` `4dee875`; `claude/glow-correction-c1-1jzjgr` `cbeb050`; `claude/practical-cray-h7t08x` `c79bfb6`.
- **Written:** 13 November 2026, finished at 03:59 UTC by the clock.
- **Boundaries kept:**
  - I checked environment variable names only. The HDE names and the STREAM and `PG` names are absent; the three AWS names reported before are present. I read no value.
  - I called no provider, database, HDE, Railway, Cloudflare or TypeSafe service. I ran no application code and no test. I read the code, and checked it with scripts kept outside the copy, which parse files by AST and import nothing from them.
  - I wrote only this file. Notion was read, not edited.

## 1. What I read

- **The consultation,** and the evidence record's "Stage A, correction C2" (T5's table), "Manager verification of C2" and "Delta re-review of C2", with every finding.
- **The brief's revision 8:** the owned paths, D8, "Stage A, correction C2", its stop rule and "Sessions".
- **The code at `303fdcc`:**
  - `account_lock_scan.py`: its docstring, `read_models`, `_follows`, `_expression_paths`, `scan_file`'s chain, hop and judgement (`:351-430`), and the SQL rule;
  - `discovery_cases.py`: `_Statements`, `_member_tables`, `WRITE`, `pages.one_snapshot_statements` and `logs.no_private_value`'s capture;
  - `discovery_support.py`: `check_page` and `hold_area`;
  - `profile_support.py`: `forms`, the T2 to T4 patterns and `Matcher`;
  - for S1's list, the statements the pages make: `glow_discovery/pages.py` (`create`, `continue_page`, `_with_photos`), `glow_profiles/tx.py` (`run`, `lock_account`, `read_account_shared`), `glow_profiles/media.py` (`delivery_reference`, `_owner`), `glow_discovery/predicates.py` (`VIEWER`'s parameters, the tables) and `glow_persistence/models.py` (`AppAccount`'s fields, every `Meta`).
- **The records C3 changes:** the proof README (its SV3 paragraph, the file table, "Limits"), the P11 plan's SV3 entry, the carried-items file's SV3 Stage B and OD-64 sections, and the handoff.
- **My DM-63 to DM-66,** for the deferred rows (section 6).
- **Notion,** read-only (section 7).

## 2. Verdicts

| Item | Verdict |
|---|---|
| L1 | **Approved,** as proposed: fix in C3 (GD1, item 1) |
| L2 | **Approved with conditions:** fix in C3, with the rules made exact (GD1, item 2). Read literally, rule (i) counts every keyword's value as an unread argument, and the corrected scan would then refuse 47 of the 52 existing calls. The SQL gap is wider than `JOIN {}`, and is fixed rather than stated. The limits are as GD7 states |
| S1 | **Approved with conditions:** the list must name all three reads of the viewer's own account row. With only the account lock, a page by cursor fails the case, since its `FOR SHARE` read and its versions read are not that lock. `VIEWER` is bound to the viewer, and the phase before the transaction is covered too (GD1, item 3) |
| S2 | **Approved,** as proposed (GD1, item 4) |
| R1 | **Approved:** records in C3, in GD5's and GD6's words. The README's understated limit is **my DM-64 T8's wording**, which C2 used as given |
| N1 | **Approved: carried to Stage B,** in GD12's words. **My DM-66 called the one-digit day "harmless extra coverage". That was wrong:** a wider look-behind exempts more text, so it counts less |
| N2 | **Approved:** two rows in T5's table, in GD8's words |
| N3 | **Approved: carried to Stage B,** in GD12's words |
| 2. C3's shape | **Agree, with three additions:** the P11 plan's runs-of-record sentence (GD10); C2's item 3 row in the record points to C3 (GD9); and the stop rule names the reference design's locks and a pre-probe statement that item 3's list does not name. **The delta re-review, as recommended** |
| 3. The sequence | **Agree** |
| 4. Notion | **Matches `3000014`** (section 7) |
| The deferred rows | **DM-63's LM5, DM-64's T1 to T9, DM-65's RV1 to RV10 and DM-66's CK1 to CK7 are confirmed as applied** (section 6) |

**How to apply:**
- **Where each condition goes:**
  - GD1 and GD2: the brief, as its revision 9;
  - GD3 to GD10: C3's session, in its owned paths, as C3's section says;
  - GD11 and GD12: the carried-items file, yours;
  - GD13 and GD14 (optional): the brief's D8 and the handoff's title, yours.
- **All are Markdown records,** in given words; line breaks may move. In GD10, `RUN` and `HEAD` are C3's run of record and code head, which C3 fills in.
- **Verified by script** (`apply67.py`, outside the copy): each of the 14 old passages occurs exactly once at `3000014`; each pair applies to a copy in order; and the report holds no model identifier.
- **No further read is needed** before C3's prompt, if GD1 and GD2 are applied as written. A departure comes back first.

## 3. Item 1 — The dispositions

### 3.1 What I confirmed

Every finding stands as the review states it. Each was checked by reading `303fdcc`:
- **L1:** the generic branch (`account_lock_scan.py:406-411`) gives a generic lock with joins and an `of=` the mode `FOR UPDATE OF …`, which the pass test `Lock.no_key` (`:102-104`) accepts. The docstring (`:24-25`) requires `no_key=True`.
- **L2:**
  - `_expression_paths` reads only a literal `Q(…)` or `F(…)` call;
  - `PATH_METHODS` holds neither `latest`, `earliest` nor `extra`;
  - `scan_file` follows one `held` assignment and one `used` variable;
  - `_follows` returns false for a path of one segment, and `read_models` reads forward relation fields only. So `User.objects.filter(appaccount=…)`, a join, is not seen.
- **S1:** the pre-probe check (`discovery_cases.py:1287-1290`) reads the `transaction` phase only. It passes any statement whose tables are the account table alone and whose parameters include the viewer's ID.
- **S2:** the write check (`:1313`) reads `probe.in_transaction()`, the `transaction` and `candidates` phases only.
- **R1:** `TIME_AFTER = r"(?![.,][0-9])"` (`profile_support.py:139`) drops a held time followed by `.` or `,` and a digit, a field separator included. The README says "printed with a fraction of a second".
- **N1:** `TIME_BEFORE` (`:135-138`) exempts a time after any capital and two letters, a comma, a day in two digits or one, a capital and two letters, four digits and a space, in every text the scans read. Django writes `Expires` with a two-digit day.
- **N2:**
  - `check_page` (`discovery_support.py:242-253`) scans a page's JSON against `private`, which `hold_area` fills with the areas' internal points only;
  - `contract.instant` (`glow_profiles/contract.py:555`) writes `expires_at` in whole seconds;
  - the DEBUG capture's handler sets no formatter, so each record is its message alone.
- **N3:** no file in `proofs/postgres-ordering/tests/` names `_found_in_database`.

**What the corrected rules would judge today.** Three scripts of my own read the 52 `select_for_update` calls (47 in `services/api`, 5 in the reference design) and every SQL lock string, by AST.
- **No call has any of the new forms:**
  - no positional argument to a lookup method;
  - no expression method, no `extra`, no `latest` or `earliest`;
  - no `select_related`;
  - no path argument that is not a string literal;
  - no `*` or `**`.
- **Every keyword value is a name or an attribute.**
- **A name that holds a lock is used afterwards** only for `save`, `delete` or `refresh_from_db` on a row, or, in the reference design's `_lock`, for `query.filter(pk=…)`.
- **None locks auth's `User`.** `AppAccount`'s only relation field is `auth_user`, and no model has `Meta.ordering`.
- **The scanned files hold three SQL lock strings outside docstrings,** all `FOR SHARE`.
- **So GD1's items 1 and 2 refuse no existing lock,** and the counts stay as C2's run printed them: 52 calls read, 0 locking a queryset that joins.

### 3.2 L1

Approved as proposed. A generic lock's model can be `AppAccount` at run time. With joins:
- `no_key=model is AppAccount` locks every joined row `FOR UPDATE` when the model is another;
- `of=` locks the model's own row `FOR UPDATE` when the model is `AppAccount`.

Only `no_key=True` is safe in both cases. The planted helper and its reversal are in GD1.

### 3.3 L2: the rules, made exact

- **Rule (i) needs one distinction.** A keyword's name is a path; its value is normally a value (`pk=account_id`). Read literally, "any argument … that is not a literal the scan reads counts as a join" covers that value too.
  - Under L1's fix, every lock but the five on `AppAccount` itself would then be refused: 47 of the 52 calls. That is C3's stop condition.
  - GD1 counts a positional argument, an expression method's argument, a path method's non-literal argument, and `*` or `**`.
  - A keyword's value is judged only when it is, or names, a `Q` or `F`.
  - What stays unseen is a stated limit: an expression given as a keyword's value from outside the function.
- **Rules (ii) to (iv)** are as proposed, with (iv)'s names read exactly: a relation field's `related_query_name`, else its `related_name`, else the model's lower-cased name. Today that is `appaccount` on auth's `User`.
- **SQL, fixed rather than stated.** The SQL rule (`:423`) counts an unknown table only where `FROM` is followed by `{}`, an f-string's field or a bare format field. It misses:
  - `JOIN {}`, the manager's case;
  - a named or numbered format field (`{table}`, `{0}`), which `_text` keeps as written, while the rule looks for `{}`;
  - `%` formatting;
  - a statement joined from strings;
  - a field elsewhere in the string that adds a `JOIN`.

  The docstring's "(a `{table}` placeholder)" claims more than the code does. GD1's rule refuses a `FOR UPDATE` string unless it is complete literal text that names its tables itself. It refuses nothing today, since no string outside a docstring takes `FOR UPDATE`, and it closes the class in a few lines.
- **The limits** (GD7):
  - a queryset or expression that reaches the lock from another function;
  - an expression given as a keyword's value from outside;
  - `Meta.ordering` (none today);
  - a model imported under another name (C1's rule);
  - a lock clause built at run time (`FOR {mode}`).

### 3.4 S1: the list

The consultation's list names `VIEWER` and "the viewer's account-row lock". Before the probe point, the pages make these member-table reads, the tables being those `_member_tables()` holds:
- **in a page with no cursor:** `lock_account`'s `FOR NO KEY UPDATE`, and `VIEWER`;
- **in a page by cursor:** `read_account_shared`'s `SELECT state FROM glow_persistence_appaccount WHERE id = %s FOR SHARE`, the viewer's versions (`AppAccount.objects.filter(pk=…).values_list(…).first()`), and `VIEWER`.

With the lock alone on the list, the corrected case fails a page by cursor. So GD1 gives one shape that covers all three account reads: one `SELECT` with no subquery, the account table alone, the primary key equal to the viewer's ID as its only condition and parameter. It also tightens the list in two places:
- **`VIEWER`** passes only with the viewer's ID as its `viewer` parameter. Today it passes with any member's.
- **The check also reads the phase before the transaction begins.** Today that phase holds `run`'s `SELECT pg_backend_pid(), now()` and nothing that reads a member table.

The pointers' read, the clock and the batch reads touch no member table and are not judged. The stop rule makes any other pre-probe statement a stop, not a widening.

### 3.5 S2

Approved as proposed. In a page by cursor, the `committed` phase holds the photo reads, made after the page's transaction: `_owner`'s plain read, then `delivery_reference`'s own transaction with `read_account_shared`'s `FOR SHARE` and the asset's read. They write nothing and take no writer's lock, so the corrected check passes the real page.

### 3.6 R1, and my error in DM-64 T8

The README's limit, "a held time printed with a fraction of a second, or inside an HTTP or email date", is my DM-64 T8's wording, which C2 used as given. T3's own rule, also mine, drops any held time followed by `.` or `,` and a digit, and any after a date of that shape in any text. So my T8 understated what T3 cannot see. GD5 states the rule's shape and GD6 its limit, with the review's example.

### 3.7 N1, and my error in DM-66

DM-66 accepted C2's one-digit day as "harmless extra coverage". It is the opposite. `TIME_BEFORE` is an exemption, so each shape it adds is one more place a held time goes uncounted, in every text. The exemption exists only for the `Expires` header, which Django writes with a two-digit day. The disposition is right: carried to Stage B with CK7's follow-up, in GD12's words.

The review's example, `Fri, 15 Jun 1990 04:13:27`, also leaves its date uncounted, since `forms` gives no three-letter month. That is `forms`'s limit, not T3's, and GD12 routes it to Stage B's brief.

### 3.8 N2

Approved. Neither text can carry a matching clock print.
- **A page's body** is scanned against the internal points only. Its one clock value, `expires_at`, has no decimal point.
- **The DEBUG capture** has no time in its format.

GD8 adds both rows to T5's table, marked as C3's additions.

### 3.9 N3

Approved as carried. The profile suite's database cases run the rules on every table in CI, so the gap is only an offline test's. GD12 gives the item for Stage B.

### 3.10 The words

**GD1 (the brief, revision 9: C3's section, before "Sessions"):**

> ```
> ## Sessions
> ```

> ```
> ## Stage A, correction C3 (C2's delta re-review; DM-67)
>
> C3 corrects C2's proof tooling and records after C2's delta re-review of `303fdcc` (changes required, narrowly; the record, "Delta re-review of C2"). Its items are the review's L1, L2, S1, S2, R1 and N2, as DM-67 puts them; N1 and N3 are carried to Stage B (the carried-items file). C3 changes no app code, predicate, selection, recheck, lock, writer, workflow, contract, model, migration, lock file or dependency.
>
> 1. **A generic lock with a join** (L1): a generic lock (a `select_for_update` on a model held in a variable) whose queryset joins another table passes only with `no_key=True`, as the scan's docstring says; an `of=` does not make it pass, since the model can be `AppAccount`. Its offline test plants the review's helper, `model.objects.select_related("account").select_for_update(of=("self",))`, sees it refused, and sees the same helper with `no_key=True` pass. Its reversal: the scan as at `303fdcc`, which passes the helper.
> 2. **The joins the scan does not see** (L2). In the function that holds the lock:
>    - **Arguments:** a positional argument of a lookup method (`filter`, `exclude`, `get`, `get_or_create`, `update_or_create`) and any argument of an expression method (`annotate`, `alias`, `aggregate`) counts as a join, unless it is a literal `Q(…)` or `F(…)`, or a name assigned one in the function, whose paths the scan then judges. So do a path method's argument that is not a string literal, and `*` or `**` anywhere in the chain. A keyword's name is a path, as now; its value is judged as a `Q` or an `F` when it is one or a name assigned one, and is otherwise a value, not a path.
>    - **Methods:** `latest` and `earliest` are path methods; `extra()`, with any argument, counts as a join.
>    - **Variables:** the chain is followed through every plain assignment in the function, before and after the lock, transitively (`a = M.objects.filter(…)`, `b = a.select_for_update()`, `b.order_by(…)`), and so is every assignment of a name an argument uses.
>    - **Reverse relations:** a path whose first segment is the reverse name of one of `AppAccount`'s own relation fields follows a relation, alone or with more segments. The names are read from `glow_persistence/models.py`: the field's `related_query_name`, else its `related_name`, else `appaccount`. Today there is one, `auth_user`'s, so `appaccount` on auth's `User`.
>    - **SQL:** a string that takes `FOR UPDATE` passes only if it is complete literal text (no f-string field and no `{…}` format field anywhere in it, not formatted with `%` or `.format()`, not joined to other strings) that names the table after `FROM` and after every `JOIN` itself, none of them the account table. Any other such string counts as a lock of the account table and is refused. Today no string outside a docstring in the scanned files takes `FOR UPDATE`; the three SQL locks there are `FOR SHARE`.
>
>    Each form has an offline test that plants it and sees it refused, with its reversal, the scan as at `303fdcc`, which passes it: a `Q` and an `F` held in variables; a `Q` from a helper; `latest("account__created_at")`; `extra(tables=[…])`; a join added two variables after the lock; `User.objects.filter(appaccount=…)` locked `FOR UPDATE`; and `FOR UPDATE` in SQL with `JOIN {}`, with `FROM {table}` in a `.format` string, and as a clause in a string of its own. Every lock in `services/api` and the reference design still reads as before: 52 `select_for_update` calls read, none locking a queryset that joins, and the seven explicit account locks unchanged. The docstring, the README's "Limits" and the record state what the scan still cannot see, in DM-67's words.
> 3. **Before the probe point, an explicit list** (S1). In `pages.one_snapshot_statements`, in every phase the probe records before the probe point (before the page's transaction begins, and in it), a statement that reads a member table passes only if it is one of these:
>    - `predicates.VIEWER`, exactly, with the viewer's ID as its `viewer` parameter;
>    - a read of the viewer's own account row: one `SELECT` with no subquery, whose only table is `glow_persistence_appaccount`, whose only condition is its primary key equal to one parameter, and whose only parameter is the viewer's ID; it may order by the key, take `LIMIT 1`, and end in `FOR NO KEY UPDATE` or `FOR SHARE`.
>
>    These are the statements the pages make there today: in a page with no cursor, the account lock `FOR NO KEY UPDATE` and `VIEWER`; in a page by cursor, the account's `FOR SHARE` read, the viewer's versions read and `VIEWER`. Any other statement that reads a member table before the probe point fails the case. The list's matcher has offline tests: the three account reads pass, and a read naming another ID, an `IN` list, a join, a subquery and `VIEWER` for another member each fail. Its database reversals, each failing the case: D, a pre-probe read of other members' accounts (the review's), and `VIEWER` run for another member before the probe point.
> 4. **A page by cursor writes nothing, in any phase** (S2): the write check reads every phase the probe records for a page by cursor (`outside`, `transaction`, `candidates` and `committed`, the photo reads after the commit included) and fails on any write. Its database reversal E, a write after the cursor page's transaction (the review's), fails the case.
> 5. **The records** (R1, N2; L2's limits): in the proof README, the SV3 paragraph's heading (C3 and revision 9), the file table's lock-scan row, T3's rule and its limit in "Limits", and a "Limits" entry for the lock scan; in the record, two rows in T5's table (a page's body and the DEBUG capture) and a pointer from C2's item 3 row to this section; and, in the P11 plan's SV3 entry, C3's run of record. The given texts are DM-67's GD3 to GD10. The README's SV3 paragraph also gains a sentence on what C3 adds, as for C1 and C2, and the record a section for C3, both in C3's words.
>
> **The stop rule (C3):** stop and report if C3 needs a change outside its owned paths, any change to app code, a predicate, the selection, the recheck, a lock, a writer or the workflow; if the corrected scan refuses an existing lock in `services/api` or the reference design; or if a page makes a statement before the probe point that item 3's list does not name (report it; do not widen the list).
>
> **C3's run of record:** a push run on its code head, with all eight jobs passing (the ordering, identity, profile and discovery suites among them), read from GitHub.
>
> **C3's review** (DM-67): a short delta re-review of C3's code head against `303fdcc`, reading items 1 to 4 as security boundaries. It plants L1's helper and each of item 2's forms and sees each refused; runs item 3's and item 4's database reversals and sees each fail; checks item 3's list against the statements the pages make before the probe point; reads the scan's counts on the tree; and confirms from the diff that nothing outside C3's owned paths changed. The manager's verification comes first, and the Dev Manager's pre-merge read after the review.
>
> ## Sessions
> ```

**GD2 (the brief, revision 9: C3's owned paths):**

> ```
> and `.github/workflows/foundation.yml`'s comment on the discovery database's keys (F5), a comment only.
> ```

> ```
> and `.github/workflows/foundation.yml`'s comment on the discovery database's keys (F5), a comment only.
> - **Correction C3 only** (DM-67): `proofs/postgres-ordering/glow_ordering_proof/account_lock_scan.py` and `discovery_cases.py`, with their offline tests in `proofs/postgres-ordering/tests/`; the proof README; the evidence record; and the P11 plan's SV3 entry, its runs of record only. Nothing else changes in C3.
> ```

**GD3 (C3: the proof README's SV3 heading):**

> ```
> **SV3 Stage A, the discovery slice, with its corrections C1 and C2** ([brief](../../docs/planning/sv3-eligibility-discovery-interactions.md), revision 8, with DM-60's to DM-66's conditions;
> ```

> ```
> **SV3 Stage A, the discovery slice, with its corrections C1, C2 and C3** ([brief](../../docs/planning/sv3-eligibility-discovery-interactions.md), revision 9, with DM-60's to DM-67's conditions;
> ```

**GD4 (C3: the README's file table, the lock scan's row):**

> ```
> and of every lock of a queryset that joins another table, which must take `no_key=True` or an `of=` naming no account;
> ```

> ```
> and of every lock of a queryset that joins another table, which must take `no_key=True` or, on a named model, an `of=` naming no account (a generic lock with a join must take `no_key=True`; C3);
> ```

**GD5 (C3: the README's "Limits", T3's rule):**

> ```
> and a held time's form only where it is not preceded by an HTTP or email date (`Thu, 12 Nov 2026 `) and not followed by a fraction of a second;
> ```

> ```
> and a held time's form only where it is not preceded by a date in the HTTP or email shape (`Thu, 12 Nov 2026 `, the day in two digits or one) and not followed by `.` or `,` and a digit;
> ```

**GD6 (C3: the README's "Limits", T3's limit):**

> ```
> a held time printed with a fraction of a second, or inside an HTTP or email date;
> ```

> ```
> a held time followed by `.` or `,` and a digit (a fraction of a second, a logging time's milliseconds, or a field separator before a digit, as in `1990-06-15,04:13:27,40`), or preceded by a date in the HTTP or email shape (any three-letter day and month, any year, the day in two digits or one, as in `Fri, 15 Jun 1990 04:13:27`), in any text the scans read;
> ```

**GD7 (C3: the README's "Limits", the lock scan):**

> ```
> - **The scans' messages** (DM-64 T7):
> ```

> ```
> - **The lock scan** (SV3 Stage A, corrections C1 to C3; DM-61, DM-65, DM-67): it reads the source, never imports it, and follows a queryset within one function. So it cannot see: the joins of a queryset, or of a `Q`, an `F` or another expression, that reaches the lock from another function (a lock on such a queryset is judged as a generic lock); an expression given as a keyword's value from outside the function; a model's `Meta.ordering` (none exists today); a model imported under another name (C1's rule, unchanged); and a lock clause built at run time (such as `FOR {mode}`).
> - **The scans' messages** (DM-64 T7):
> ```

**GD8 (C3: the record's T5 table, two rows):**

> ```
> so T3 is not needed there; a timestamp's date is the run's, and no searched date is (each is 17 or more years back) |
> ```

> ```
> so T3 is not needed there; a timestamp's date is the run's, and no searched date is (each is 17 or more years back) |
> | **A page's body** (the discovery suite's `check_page`, against its private ledger; added in C3, the delta re-review's N2) | the batch's `expires_at`, in whole seconds (`2026-11-13T03:54:40Z`, `contract.instant`) | the private ledger holds only the areas' internal points (`hold_area`), so only coordinate forms are searched there; a form has at least three decimals, and the time has no decimal point |
> | **The DEBUG capture** (the discovery suite's `logs.no_private_value`, against the member values and the secrets; added in C3, N2) | nothing: its handler sets no formatter, so each record is its message alone (`%(message)s`), and the loggers seen print no time (as in the log records' row) | — |
> ```

**GD9 (C3: the record, C2's item 3 row):**

> ```
> a path the scan cannot read counts as a join; a generic lock with a join needs `no_key=True`.
> ```

> ```
> a path the scan cannot read counts as a join; a generic lock with a join needs `no_key=True` (neither held at `303fdcc`: the delta re-review's L1 and L2, corrected in "Stage A, correction C3").
> ```

**GD10 (C3: the P11 plan's SV3 entry; `RUN` and `HEAD` filled in by C3):**

> ```
> C2's is 43337467715 (on `303fdcc`), with every job passing.
> ```

> ```
> C2's is 43337467715 (on `303fdcc`), with every job passing; C3's is RUN (on `HEAD`), with every job passing.
> ```

**GD11 (yours: the carried-items file, the section's heading):**

> ```
> ## Carried to SV3 Stage B (DM-66)
> ```

> ```
> ## Carried to SV3 Stage B (DM-66, DM-67)
> ```

**GD12 (yours: the carried-items file, N1 and N3):**

> ```
> the rest of the output stays withheld (acceptance check 12).
> ```

> ```
> the rest of the output stays withheld (acceptance check 12).
> - **T3's date rule, narrowed** (DM-67; C2's delta re-review, N1): T3 leaves a held time uncounted after any date in the HTTP or email shape (any year, the day in two digits or one) in every text the scans read, though the only clock text it exists for is the `Expires` header. Stage B, which changes the discovery suite, narrows it to that header's own shape (its name, an HTTP date with a two-digit day, and ` GMT` after the time) in the response headers' text alone, with T6's tests (the header not a hit; a held time after another date, or in another text, still one) and a reversal against the wider rule. DM-66 called the one-digit day "harmless extra coverage"; it widens the exemption instead (DM-67). The same text's date is not counted either, since `forms` gives no three-letter month: Stage B's brief decides whether `forms` gains it or the README's "Limits" states it.
> - **An offline test of the database search** (DM-67; C2's delta re-review, N3): no offline test exercises `profile_cases._found_in_database`'s rules; the profile suite's database cases cover them. Stage B adds one, with a fake cursor as the proof's other offline tests use: a timestamp column's text not a hit; a held coordinate, place and date still hits; and each label naming `table.column` without the value; with a reversal against the old matcher.
> ```

## 4. Item 2 — C3's shape

- **Agree:** a correction of the proof's tooling and records only, with no app code, workflow, contract or dependency change. GD2 states the owned paths. It adds one sentence of the P11 plan (GD10), as C2's item 6 did for C2's run.
- **The stop rule:** as proposed, with two additions in GD1's words:
  - the reference design's locks join `services/api`'s in the scan clause;
  - a statement the pages make before the probe point that item 3's list does not name is a stop, not a widening.
- **The run of record:** as proposed.
- **The review: the delta re-review, as recommended.**
  - Both checks are security boundaries.
  - The manager's own verification of C2 re-ran a `select_related` join and found nothing. The forms that were missed needed someone to plant each one.
  - A short re-review that plants every form and runs the database reversals is worth its cost. GD1 says what it reads.

## 5. Item 3 — The sequence

**Agree:**
1. this answer;
2. the brief's revision 9, with GD1 and GD2;
3. C3's prompt, with its TypeSafe reading;
4. C3, then your verification;
5. PR45's run and Codex on C3's head;
6. C3's delta re-review;
7. my pre-merge read, then the merge.

- **My pre-merge read covers,** at a named commit:
  - the CI policy's Database proof checks paragraph, and the data model's and contract's rewritten texts. C3 changes none of them, so the read confirms them at the final head;
  - C3's section as applied;
  - GD3 to GD12 as applied.
- **DM-64 T9's merge conditions now apply to C3's head:**
  - a green run of record on the final head;
  - Codex on that head;
  - the correction's review.

## 6. The deferred rows, as applied at `3000014`

The review log has four rows due at this consultation. My scripts check each condition's new words in the tree.
- **DM-63's LM5:** confirmed in the data model's `AccountAgeState` and `RecommendationBatch` rows and in `glow_chat/reads.py`'s module docstring, each once. The row can close.
- **DM-64's T1 to T9:** confirmed as applied:
  - T1 to T4 and T7 in C2's code, as the delta re-review also found;
  - T5's table in the record;
  - T6's tests in `RunClockTests`;
  - T8's owned-path line, with CK1's migration times, and the README's "Limits";
  - T9 by C2's placement and its delta re-review.

  Two departures, both mine to own:
  - T8's limit words understated T3's shape (R1), and GD6 replaces them in C3;
  - T3's one-digit day goes beyond T3's words, and I accepted it in DM-66 (N1), now carried.

  The row closes when GD6 lands.
- **DM-65's RV1 to RV10:**
  - RV5, RV7 and RV8 confirmed at C2's integration, each once, with RV7's pointers placed;
  - RV6 confirmed: the P11 plan names C2's run 43337467715;
  - RV2, RV4, RV9 and RV10 unchanged;
  - RV1's words all stand, with Nathan's OD-64 answer recorded between its sub-bullets;
  - RV3 matches exactly once CK2's change is applied to it.

  The row can close.
- **DM-66's CK1 to CK7:** confirmed as applied:
  - CK1 and CK2 in the brief's revision 8;
  - CK3 and CK4 in the README;
  - CK5 in the record;
  - CK6 in your relay message to C2;
  - CK7 in the carried-items file.

  The row can close.

## 7. Item 4 — Notion (read-only, at about 03:34 UTC)

**Implementation Control** says it is matched to `3000014`.
- **Its status** gives C2's delta re-review and DM-67 in plain words.
- **Its standing lines match:**
  - "Next items": DM-67 with the Dev Manager;
  - "Branches": six, listed at 00:06 UTC, with C2's at `c79bfb6` after its merge. These are the six heads `git ls-remote` shows;
  - "Mistakes log": to AM11-18 at `8d8e706`. The repository's log is unchanged since, and its newest entry is AM11-18;
  - "Standing directions": the register copy holds OD-01 to OD-64;
  - "Main": `3240ef0`.

**SV3's Work Register row:** "In progress", with its evidence pinned at `3000014`. Its next action gives the same sequence as item 3.

**The Dev Manager page** matches the review log.
- **DM-66** is considered: merge `7fa7a26`.
- **DM-67** is pending.
- **Still optional:** the "Sessions" row's two copies differ, as before.

**The register copy:** 64 rows, OD-64 included, as in the repository. The nine presentational differences are as before.

**Two stale lines in the repository,** both optional. Neither misleads a reader of the current state.
- **The brief's D8** still says the decision "is put to Nathan", just above Nathan's answer (GD13).
- **The handoff's title** still says "C2 continues after DM-66", though its body is current (GD14).

**GD13 (optional, yours: the brief's D8):**

> ```
> Whether to bound the probing is put to Nathan (DM-65 section 4.3); it does not hold Stage A's merge, since nothing is served to a member before P11, and it is decided before then.
> ```

> ```
> Whether to bound the probing was put to Nathan (DM-65 section 4.3); it did not hold Stage A's merge, since nothing is served to a member before P11.
> ```

**GD14 (optional, yours: the handoff's title):**

> ```
> # Current handoff — App Manager 11 (13 November 2026; SV3 Stage A and C1 in PR45; C2 continues after DM-66)
> ```

> ```
> # Current handoff — App Manager 11 (13 November 2026; SV3 Stage A, C1 and C2 in PR45; correction C3 after DM-67)
> ```

## 8. Where each item goes

- **The brief, revision 9:**
  - GD1 and GD2;
  - a Sessions line for DM-67's answer;
  - GD13 if you take it.
- **C3's prompt and session:** GD1's section, with GD3 to GD10 as its given words.
- **The carried-items file:** GD11 and GD12.
- **The handoff:** GD14 if you take it, and the next step.
- **The review log:**
  - DM-67's dispositions, naming `3000014` as the commit this read covered;
  - the four deferred rows, closed as section 6 says (DM-64's when GD6 lands);
  - a new deferred row: GD1 to GD12, confirmed at my next consultation or the pre-merge read.
- **Notion:** the status after DM-67.

Status: complete

# DM-68 — SV3 Stage A: C3's delta re-review, its dispositions, correction C4's scope, and how the lock scan's line ends

- **From:** Dev Manager 5 (`session_01Q789u3CWg6s9pBGXerCQZt`), on `claude/dev-manager`. **To:** App Manager 11, relayed by Nathan (OD-25).
- **Read at:** `513dfd750028a2c055d72627371b8df283d8529c` of `claude/magical-wozniak-yfmmx2`, PR45's head. This read covers it.
  - **The code** is C3's, `72ace21`, merged at `f9a8621`. No non-Markdown path differs between `72ace21` and `513dfd7`.
  - **Since my last listing (`2e3ef0f`):** C3's five commits and its merge; the manager's verification; C3's delta re-review prompt and its record; OD-65 (my succession); AM11-20. Of the paths I list first, only the register changed (OD-65 added). No `AGENTS.md`, `CLAUDE.md`, PF canon, workflow, charter, CI policy or start prompt changed.
  - **Remote heads at 09:03 UTC** (`git ls-remote`): `main` `3240ef0`; the manager branch and `refs/pull/45/head` `513dfd7`; `claude/dev-manager` `7fc47e6`; C3's `claude/glow-discovery-c3-ir9mnd` `8189b31`; C2's `c79bfb6`; C1's `cbeb050`; Stage A's `4dee875`.
- **Written:** 13 November 2026, finished at 09:25 UTC by the clock.
- **Boundaries kept:**
  - Environment names only: the HDE, `STREAM_*` and `PG*` names are absent; the three AWS names are present, as recorded before. I read no value.
  - No provider, database, HDE, Railway, Cloudflare or TypeSafe call. No application code run, no test suite run, no database.
  - **What I ran** (the charter's read-only checks), under `env -i` with `python3.12 -I`, from scripts kept outside the export:
    - copies of C3's lock scan, standard library only, which parse source and run none of it, over the export of `513dfd7` and over planted files of my own;
    - three rough prototypes of the rules below, built from that copy, to see what each would refuse;
    - two AST census scripts.
  - **Django's source:** I downloaded Django 5.2.17's wheel from PyPI (its SHA-256 matches the proof's lock) and read three of its source files. I ran none of it.
  - I wrote only this file. Notion was read, not edited.

## 1. What I read

- **The consultation** (revision 1). **The evidence record:** "Stage A, correction C3", "Manager verification of C3" and "Delta re-review of C3", whole.
- **The brief's revision 9:**
  - its diff since `2e3ef0f`;
  - its C3 section, D14, the owned paths, the acceptance checks and the review plan.
- **The other records:** the register's OD-65 row; the handoff; the review log's DM-60 to DM-68 rows and its deferred rows.
- **The code at `513dfd7`:**
  - `account_lock_scan.py`, whole;
  - in `discovery_cases.py`: `WRITE`, `_Statements`, `_member_tables`, `listed`, `OWN_ACCOUNT_READ` and `pages.one_snapshot_statements`;
  - the two generic helpers (`glow_chat/contact.py:167`; the reference design's `:122`), and `glow_profiles/tx.py`'s `run`;
  - the heads of `VIEWER`, `SELECTION` and `RECHECK` in `glow_discovery/predicates.py`;
  - every SQL string in `predicates.py`, `pages.py`, `eligibility.py`, `tx.py` and `media.py`.
- **Django 5.2.17:** `QuerySet.__and__`, `__or__`, `__xor__` and `complex_filter` (`django/db/models/query.py`), and `Query.combine` (`django/db/models/sql/query.py`).
- **DM-67's report,** for GD1 to GD14. **Notion,** read-only (section 8).

## 2. Verdicts

| Item | Verdict |
|---|---|
| F1 | **Approved with conditions.** As worded, the rule either refuses six existing locks or misses F1's own second form, depending on how it is read (3.2). SC1's item 1 gives a rule that refuses both of F1's forms and no existing lock |
| F2 | **Approved with conditions, wider.** `^` combines querysets too. The same gap also hides an explicit account lock taken on a combination, a conditional, an `or` or a `:=` expression (3.3). SC1's item 2 |
| F3 | **Approved,** in SC1's item 3's words |
| F4 | **Approved,** in SC1's item 4's words |
| F5 | **Approved with conditions:** the left side must be the lock's own variable. `other is AppAccount`, `not (model is AppAccount)` and `model is AppAccount and flag` also pass today (3.5). SC1's item 5 |
| F6 | **Approved with conditions:** a positive list of reads, not a longer list of writes (3.6). SC1's item 6, with a stop clause |
| F7, N1, N5 | **Approved:** records, in SC9's words |
| N2 | **Approved:** SC1's item 7 |
| N3, N4 | **Approved:** no change |
| 2. How the line ends | **Option (a), with conditions** (section 4; SC1, SC4 to SC7). The termination rule keeps a real account lock blocking, binds every later review of SV3, Stage B's included, and freezes the scan's rules. The backstop goes into the brief (D14 and a check 15), built in Stage B with its reversal, not into the carried-items file |
| 3. C4's shape | **Agree,** with item 6's stop clause added |
| 4. The sequence | **Agree** |
| 5. GD1 to GD12 | **Confirmed as applied** at `513dfd7`, and GD13 too. GD14 was applied at `2e3ef0f`; the handoff's later titles have since replaced it (section 7) |
| 6. Notion | **Matches `513dfd7`** in every part read (section 8) |

**How to apply:**
- **Where each condition goes:**
  - SC1 to SC7: the brief, as its revision 10 (yours);
  - SC8 to SC11: C4's prompt, as its given words, for C4's session to apply in its owned paths.
- **The words are Markdown records, given exactly,** except SC10, which C4 places in the scan's docstring. Line breaks may move. In SC11, `RUN` and `HEAD` are C4's run of record and code head, which C4 fills in.
- **Verified by script** (`apply68.py`, outside the copy):
  - each of the ten old passages occurs exactly once at `513dfd7`;
  - each pair applies to a copy, in order;
  - the report holds no model identifier.
- **No further read is needed** before C4's prompt, if SC1 to SC7 are applied as written. A departure comes back first.

## 3. Item 1 — The dispositions

### 3.1 What I confirmed

Each finding stands as the review states it. I checked each from the code at `513dfd7` (the same as `72ace21`), and with planted files run against a copy of C3's scan:

| Plant | Form | C3's scan |
|---|---|---|
| f1a, f1b, f1c | F1: `filter(display_name=Lower("account__state"))`; the same `Lower(…)` assigned to a name first; `Coalesce("account__state", Value(""))` | Each passes: no lock found, 0 joins |
| f2a, f2b | F2: `locked & Profile.objects.filter(account__state=…)`, assigned and inline | Each passes |
| f2d | Mine: the same with `^` | Passes |
| f2c | Mine: `(AppAccount.objects.filter(pk=a) \| AppAccount.objects.filter(pk=b)).select_for_update()` | Passes: `account locks found: 0` |
| r1, r2, r3 | Mine: an account lock whose receiver is a conditional, an `or` or a `:=` expression | Each passes: no lock found |
| r4 | Mine: a join in one branch of a conditional receiver | Passes |
| f3 | F3: `complex_filter({"account__state": …})` | Passes |
| f4a | F4: `of=(f"{name}",)`, with a join | Passes, as `FOR UPDATE OF {}` |
| f4b | Control: `of=(name,)` | Refused, as it should be |
| f5a | F5: `no_key=model is not AppAccount` | Passes, as `generic: FOR NO KEY UPDATE` |
| f5b, f5c, f5d | Mine: `not (model is AppAccount)`; `other is AppAccount`; `model is AppAccount and flag` | Each passes the same way |

- **F6:** `WRITE` (`discovery_cases.py:1171-1175`) is `INSERT INTO`, `DELETE FROM`, `UPDATE` only before `"glow_`, `MERGE INTO`, `TRUNCATE`, `COPY`, or a writer's row lock. `UPDATE auth_user` matches none of them.
- **F7, N1 and N3 to N5:** as the review says, by reading `_complete`, `names_its_tables`, `OWN_ACCOUNT_READ` and the generic branch (`:658`).
- **The tree:** C3's scan reads 52 calls, 0 joining, and 7 account locks, and exits 0, as C3's run printed.
- **Django 5.2.17, as read:**
  - `&`, `|` and `^` each chain the left operand's query and merge the right one's filters and joins into it (`Query.combine`). That leaves `select_for_update` as the left operand had it, so a lock on the left, or on the combination, takes the joins of both.
  - `complex_filter` takes a `Q` or a dict of lookups.

### 3.2 F1, and DM-67's own gap

**The gap is in DM-67's words.** GD1 judged a keyword's value only as a `Q` or an `F`, "and otherwise a value", so as not to refuse 47 of the 52 calls. Its limits (GD7) name an expression given "from outside the function". A `Lower("account__state")` written inside the function is in neither. DM-67 should have counted it or stated it; I own that for the office.

**The proposed rule depends on how it is read.** My census (an AST script over the 52 locks, using C3's own `_group`):
- **The keyword values:** counted lock by lock, the locks' calls hold 111, and **none is a call**, as DM-67 found.
- **What their names hold:** counted the same way, 25 calls are reached through the names those values use, in seven of the locks. Among them:
  - `UUID(change.account_id.value)` (`glow_identity/age.py`);
  - `self._authorize(…)` (`glow_chat/reads.py`);
  - a locked queryset held in a name (`glow_chat/delivery.py:437`; `glow_profiles/media.py:428` and `:546`);
  - `transition(tx, asset.id, "reject", …)` (`media.py:546`).

The two readings:
- **"Any call, in the value or through a name it uses."** This is how the scan already reads a value, and the plain reading of "directly or through a name". My prototype of it refuses six existing locks: `delivery.py:437`, `reads.py:649` and `:659`, `age.py:89`, and `media.py:428` and `:546`. It prints `locking a queryset that joins: 7`, `account locks found: 13; not FOR NO KEY UPDATE: 6`. C4 would stop.
- **"A call written in the value itself."** This refuses no existing lock. But F1's second form still passes: `expression = Lower("account__state")`, then `filter(display_name=expression)`.

**SC1's item 1:** a call to a capitalised name other than `Q` and `F` (a class, as Django's expressions and functions are) that takes a string literal or an f-string as an argument counts as a join, written in the value or reached through a name it uses. Any other call is a value.
- **Tested in a prototype:** it refuses f1a to f1c, and f1d, `Cast(expression="account__created_at", …)`, a path given by keyword. It passes my control ok1: `filter(account_id=account.pk, updated_at__lt=timezone.now())`, with `account` assigned from a lower-case call. On the tree it refuses nothing: 52 calls, 0 joining, 7 account locks, exit 0.
- **What it leaves, stated in SC9:** a path given to an expression through a name (`Lower(path)`), and an expression class called by a lower-case name.

### 3.3 F2: the mechanism, not the example

The scan reads a lock's receiver, and every queryset it follows, only as a plain chain of attributes, calls and subscripts down to a name (`_receiver_names`, `_receiver_calls`, `_base_name`). It reads a conditional or boolean expression only at the top of an assigned value. Anything else ends the reading:
- **A combination** (`&`, `|`, and `^`, which Django 5.2.17 supports) is F2: its joins go unseen.
- **The receiver itself fares worse.** An explicit account lock taken on a combination (f2c), a conditional (r1), an `or` (r2) or a `:=` expression (r3) is not seen as a lock at all. Each takes `FOR UPDATE` on account rows: the CX1 hazard itself.
- **SC1's item 2** reads each such expression through to its chains. It judges each chain as the receiver, and passes the lock only if it passes for each chain.
- **It refuses no existing lock.** In the functions that hold the 52 locks, every `|` is in a type annotation (`int | None` and the like), which is not a queryset, and there is no `&` or `^`. My prototype refuses all eight plants (f2a to f2d, r1 to r4) and nothing on the tree.

These are F2's mechanism, not new findings to chase. C4 is for closing the mechanism, not the review's one example.

### 3.4 F3 and F4

- **F3:** agreed. A dict counts as a join: it fails closed, and is simpler than reading the dict's keys. A literal `Q` is judged. No file in `services/api` outside its tests calls `complex_filter`, `dates`, `datetimes` or `in_bulk`.
- **F4:** agreed. `_of` should read its entries with `_literal`, not `_text`. A name or a starred entry already fails closed (f4b); only the f-string gets through.

### 3.5 F5

The manager's syntax rule (one `is`, its right side `AppAccount`):
- **It refuses:** `is not` (f5a), `not (…)` (f5b) and the `and` form (f5d).
- **It passes:** `other is AppAccount` (f5c). With `model` holding `AppAccount` and `other` holding another model, that lock takes `FOR UPDATE` on the account row.

SC1's item 5 also requires the left side to be the variable the lock's receiver starts from.
- **Today's helpers:** the two that take a comparison are both exactly `model.objects.select_for_update(no_key=model is AppAccount)`, so both pass.
- **The prototype:** it refuses f5a to f5d.

### 3.6 F6: a positive list of reads

Widening `UPDATE` closes the review's example but not the class. A write is any statement that is not a read, and a list of writes misses what it does not name: `SELECT … INTO`, `CALL`, a `WITH` that holds one, a schema change. S1 ended its line with a positive list (DM-67); F6 should too.
- **SC1's item 6:** a statement is a read only if it begins with `SELECT` or `WITH` and holds none of `INSERT`, `UPDATE`, `DELETE`, `MERGE`, `INTO`, `TRUNCATE` or `COPY`. Anything else is a write. A writer's row lock stays a write, as `WRITE` counts it now.
- **Why the real page should pass it:**
  - no SQL string in `predicates.py`, `pages.py`, `eligibility.py`, `tx.py` or `media.py` holds any of those words;
  - `VIEWER`, `SELECTION` and `RECHECK` begin with `WITH`;
  - `tx.run` opens one durable `atomic` block (so no savepoint), and sends `SELECT pg_backend_pid(), now()` and `SELECT clock_timestamp()`;
  - C3's record lists only reads among a page by cursor's statements before its probe point.
- **The stop clause:** I could not run the page, so the stop rule covers a statement the corrected check counts as a write.
- **The limit it leaves:** a write made inside a function a read calls (`nextval`, or a function the database defines). SC9 states it.

### 3.7 F7, N1 and N5

Agreed, as records. SC9 places them in the README's lock-scan entry, with the limits that items 1 and 6 leave:
- the review's words for F7;
- N1's reason;
- N5's two limits.

The docstring states what the scan is (SC10).

### 3.8 N2 to N4

Agreed. N2's two tests are SC1's item 7.

## 4. Item 2 — How the line ends

**Option (a), with conditions.**

**Why not (b).** Four independent readings show today's code clean:
- the scan's counts in every run of record;
- DM-67's AST census;
- each review's planted forms;
- my census above: none of the 52 locks is written in any of F1 to F5's forms, and the seven account locks are `FOR NO KEY UPDATE`.

Exact coverage now would add nothing for this code. The backstop's value is for code not yet written, and the next account locks arrive in Stage B, with the like and the match. Building it in C4 would widen C4 across four suites' runners and need its own design read: the opposite of ending the line.

**Why not (c).** It does not converge. Three rounds each closed what they found and found more. The render-rule check did the same until DM-39 stated a positive list and froze it. A static reading of Python cannot see every way a queryset is built.

**The conditions:**
1. **A real lock stays blocking.** The termination rule must not turn a defect in the app into a stated limit. A lock of an account row at the reviewed head that is not `FOR NO KEY UPDATE`, however it is written, is the review's first class. The review lists every lock by AST to look for one.
2. **It binds every later review of SV3,** Stage B's included. After C4 the scan's rules are frozen: they change only to correct a defect in one of the classes, or by a design I read. Otherwise the next review reopens the line.
3. **The backstop goes into the brief:** D14, a new check 15, and its runners in Stage B's owned paths, as a Stage B requirement with its reversal.
   - The workflow sends a follow-up to its owning brief when there is one (step 5), and SV3 has one.
   - The check also changes Stage B's acceptance.
   - The carried-items file holds items whose owner has no brief yet.
4. **Its words are exact (SC4):**
   - what is recorded: every statement each suite sends through Django, on every connection it opens;
   - what fails: a `FOR UPDATE` that names the account table without an `OF` that excludes it, or a lock clause the check cannot read;
   - what it prints: counts and each failing statement's text, never a parameter;
   - its reversal, and its limits: statements sent outside Django, and code the suites do not run;
   - a stop if a statement the code sent before Stage B fails it.

The scan's statement and the termination rule are SC1's last paragraph, SC9 and SC10.

## 5. Item 3 — C4's shape

**Agree:**
- C3's owned paths (SC2);
- no change to app code, workflows, contracts or dependencies;
- the run of record as proposed.

**One addition to the stop rule,** for item 6: the real page by cursor sends a statement the corrected check counts as a write. C4 reports it, and does not narrow the words to pass it. The scan's stop is as proposed, with the same "do not narrow" clause.

## 6. Item 4 — The sequence

**Agree:**
1. this answer;
2. the brief's revision 10, with SC1 to SC7;
3. C4's prompt, with its TypeSafe reading and SC8 to SC11;
4. C4, then your verification;
5. PR45's run and Codex on C4's head;
6. C4's review, as SC1's last paragraph sets it;
7. my pre-merge read, then the merge.

- **My pre-merge read covers,** at a named commit:
  - the CI policy's Database proof checks paragraph, and the data model's and the contract's rewritten texts (C3 and C4 change none of them, so the read confirms them at the final head);
  - C3's and C4's sections as applied;
  - SC8 to SC11 as applied.
- **DM-64 T9's merge conditions now apply to C4's head:** a green run of record on the final head, Codex on that head, and the correction's review.

## 7. Item 5 — DM-67's GD1 to GD12, as applied at `513dfd7`

A script (`check_gd.py`, outside the copy) parsed DM-67's 14 pairs and compared each new text with the tree, whitespace normalised:
- **GD1, GD2 and GD13,** in the brief's revision 9: each new text once; GD13's old sentence gone.
- **GD3 to GD7,** in the proof README: each once. GD3 to GD6's old passages are gone, and GD7's entry stands before the line it precedes.
- **GD8 and GD9** in the record, and **GD10** in the P11 plan, with C3's run 43369448338 and `72ace21` filled in: each once. GD9's and GD10's replaced passages are gone; GD8 adds its two rows after its anchor.
- **GD11 and GD12,** in the carried-items file: each once. GD11's old heading is gone; GD12 adds its items after its anchor.
- **GD14:** applied at `2e3ef0f` (the handoff's title read exactly as given), and since replaced by the handoff's own later titles. Nothing to do.

**The review log's rows:**
- DM-67's row (GD1 to GD12) can close.
- DM-64's T1 to T9 row closes too, since GD6 has landed (DM-67 section 6).
- A new row: SC1 to SC11, confirmed at my next consultation or the pre-merge read.

## 8. Item 6 — Notion (read-only, 09:13 to 09:16 UTC)

| Page | What I compared | Result |
|---|---|---|
| Implementation Control | The status heading and its stamp | **Match:** "matched … at `513dfd7`", with C3's delta re-review and DM-68 in plain words |
| Implementation Control | "Next items" | **Match:** the brief at revision 9; C3 built, verified and integrated; DM-68 with Dev Manager 5 |
| Implementation Control | "Branches" | **Match:** seven branches, with `claude/dev-manager` at `7fc47e6` and C3's branch at `8189b31`, as `git ls-remote` shows |
| Implementation Control | "Dev Manager" | **Match:** Dev Manager 5, OD-65, start note `7fc47e6` merged at `6cf247c` |
| Implementation Control | "Mistakes log" | **Match:** AM11-01 to AM11-20, at `dacd0ea`; the repository's log is unchanged since |
| Implementation Control | "Standing directions"; "Main" | **Match:** OD-01 to OD-65; `3240ef0` |
| Dev Manager — reviews and approvals | DM-68's row; the Sessions row | **Match:** DM-68 pending; Dev Manager 5 recorded as the review log has it |
| Register copy | Row IDs; OD-65 | **Match:** 65 rows, OD-01 to OD-65; OD-65's cell read against the repository's row |
| Work Register `SV3` | State, next action, evidence | **Match:** "In progress"; C3 merged at `f9a8621`; DM-68 at `513dfd7`; evidence pinned at `513dfd7` |

**The two stale lines in my start note are corrected** (AM11-20). No mismatch.

## 9. The words

**SC1 (yours: the brief, revision 10: C4's section, before "Sessions"):**

> ```
> ## Sessions
> ```

> ```
> ## Stage A, correction C4 (C3's delta re-review; DM-68)
>
> C4 corrects C3's proof tooling and records after C3's delta re-review of `72ace21` (changes required, narrowly; the record, "Delta re-review of C3"). Its items are the review's F1 to F6 and N2, as DM-68 puts them, with the forms DM-68 adds to F2 and F5; F7, N1 and N5 are records; N3 and N4 need no change. C4 changes no app code, predicate, selection, recheck, lock, writer, workflow, contract, model, migration, lock file or dependency.
>
> 1. **A function given a path, in a keyword's value** (F1). In a keyword's value, a call to a capitalised name other than `Q` and `F` (a class, as Django's expressions and functions are: `Lower`, `Coalesce`, `Cast`, `Concat`, `OuterRef`, `RawSQL`, `Value`, ...) that takes a string literal or an f-string as an argument counts as a path the scan cannot read, so a join: written in the value itself, or in a value assigned in the function to a name the value uses, through that name's assignments, as a `Q` or an `F` there already is. Any other call in a keyword's value is a value: one to a lower-case function or method returns what another function made. This replaces C3's "and is otherwise a value, not a path". Its offline tests plant `filter(display_name=Lower("account__state"))`, the same `Lower(...)` assigned to a name first, and `Coalesce("account__state", Value(""))`, and see each refused; and see `filter(pk=account.pk)`, with `account` assigned from a lower-case call, and `filter(expires_at__gt=timezone.now())` pass. Its reversal: the scan as at `72ace21`, which passes all three.
> 2. **A queryset that is not a plain chain** (F2, with the forms DM-68 adds). A queryset written as a combination (`&`, `|` or `^`), a conditional expression (`... if ... else ...`), a boolean expression (`and`, `or`) or an assignment expression (`:=`) is read through to every chain it holds, inline or held in a name assigned in the function, before and after the lock, whichever part holds the lock and whether the lock is taken on a part or on the whole; the joins of every part count. Where the lock's receiver is such an expression, each chain it holds is judged as the receiver, with the joins of them all, and the lock passes only if it passes for each: `(AppAccount.objects.filter(pk=a) | AppAccount.objects.filter(pk=b)).select_for_update()` is an account lock, and needs `no_key=True`. Its offline tests plant the review's `locked & Profile.objects.filter(account__state=...)`, assigned and inline, the same with `^`, that account lock, and an account lock whose receiver is a conditional, an `or` and a `:=` expression, and see each refused. Its reversal: the scan as at `72ace21`, which passes each (the account locks as no lock at all).
> 3. **`complex_filter()`** (F3): `complex_filter` is a lookup method. A literal `Q(...)` given to it, or a name assigned one, has its paths judged; a dict, or any other argument, counts as a join. Its offline test plants `complex_filter({"account__state": ...})` and sees it refused, and sees `complex_filter(Q(pk=...))` pass. Its reversal: the scan as at `72ace21`, which passes the dict.
> 4. **`of=`, read only as literals** (F4): an `of=` passes only as a tuple or list written in the call whose every entry is a plain string literal naming no path to `AppAccount`; an f-string, a name, a call, a starred entry or any other value fails closed, as naming a path to `AppAccount`. Its offline test plants `of=(f"{name}",)` and sees it refused. Its reversal: the scan as at `72ace21`, which passes it as `FOR UPDATE OF {}`.
> 5. **A generic lock's `no_key`, read by its syntax** (F5): a generic lock passes only with `no_key` given as the literal `True`, or, where its queryset joins no other table, as exactly `<variable> is AppAccount`: one comparison with the one operator `is`, its left side the variable the lock's receiver starts from (`model` in `model.objects.select_for_update(...)`) and its right side the name `AppAccount`. Anything else fails: `is not`, `not (... is AppAccount)`, a comparison inside `and` or `or`, another variable, a reversed comparison, or a name assigned the comparison. The two helpers that take one today, `glow_chat`'s `_lock` and the reference design's, pass as they are. Its offline tests plant `no_key=model is not AppAccount`, `no_key=not (model is AppAccount)`, `no_key=other is AppAccount` and `no_key=model is AppAccount and flag`, and see each refused. Its reversal: the scan as at `72ace21`, which passes all four as `FOR NO KEY UPDATE`.
> 6. **A write is anything but a read** (F6): in `pages.one_snapshot_statements`, a statement counts as a write unless, with its leading whitespace removed and its case ignored, it begins with the word `SELECT` or `WITH` and holds none of the words `INSERT`, `UPDATE`, `DELETE`, `MERGE`, `INTO`, `TRUNCATE` or `COPY`. So a writer's row lock (`FOR UPDATE`, `FOR NO KEY UPDATE`) is a write, and `FOR SHARE` is not. The page with no cursor's control (its batch's writes are seen) uses the same test. Its offline tests: the statements a page by cursor sends are reads (`run`'s backend read, the clock, the account's `FOR SHARE` read, the versions read, `VIEWER`, the recheck and the photo reads); and `UPDATE auth_user ...`, `UPDATE ONLY "glow_..." ...`, a schema-qualified `UPDATE`, `INSERT INTO`, `DELETE FROM`, a `WITH` holding an `UPDATE`, `SELECT ... INTO`, `SELECT ... FOR NO KEY UPDATE`, `CALL ...` and `TRUNCATE` are writes. Its database reversal, the review's: `UPDATE auth_user SET is_active = is_active WHERE id = -1` after the cursor page's transaction fails the case; E and C2's write still fail it.
> 7. **The matcher's tests** (N2): two more of `listed`'s offline cases, each failing: a read of the viewer's own row with an `OR` condition, and a join without an alias. The code already refuses both.
> 8. **The records:** the scan's docstring and the README's "Limits" state what the scan is and what it cannot see (F7, N1, N5 and the limits items 1 and 6 leave), in DM-68's words; the README's SV3 heading (C4 and revision 10), with a sentence on what C4 adds, as for C1 to C3, in C4's words; in the record, a section for C4; and, in the P11 plan's SV3 entry, C4's run of record. The given texts are DM-68's SC8 to SC11.
>
> **The stop rule (C4):** stop and report if C4 needs a change outside its owned paths, or any change to app code, a predicate, the selection, the recheck, a lock, a writer or the workflow; if the corrected scan refuses an existing lock in `services/api` or the reference design; or if the corrected write check counts a statement the real page by cursor sends as a write. Report it; do not narrow the words of items 1 to 6 to pass it.
>
> **C4's run of record:** a push run on its code head, with all eight jobs passing (the ordering, identity, profile and discovery suites among them), read from GitHub.
>
> **C4's review, and how the scan's line ends** (DM-68): a short delta re-review of C4's code head against `72ace21`, reading items 1 to 7 as security boundaries. It plants each form items 1 to 6 name, by each rule's words and not its examples alone, and sees each refused; runs item 6's database reversals and sees each fail; lists every `select_for_update` call and every SQL string that takes `FOR UPDATE` in `services/api` and the reference design, by AST, and reads each one's lock mode; reads the scan's counts on the tree; and confirms from the diff that nothing outside C4's owned paths changed. Its correction classes are these, and only these:
> - a lock of an `AppAccount` row at the reviewed head, in `services/api` or the reference design, that is not `FOR NO KEY UPDATE`, however it is written (a defect in the app's locks, not the scan's, and blocking);
> - a form one of items 1 to 6's rules names that the scan or the write check still passes;
> - a regression: a form refused, or a lock, test or case passing, at `72ace21` that is not at C4's head;
> - a test or reversal of items 1 to 7 that passes where it should fail;
> - a record (the scan's docstring, the README, the evidence record, the P11 plan) that claims more than the scan or the check does.
>
> Any other form the scan or the write check does not see is recorded, with its planted example, as a stated limit in the README's "Limits" and the record, and is not a correction class. This holds in every later review of SV3, Stage B's included. After C4, the scan's rules are frozen: they change only to correct a defect in one of these classes, or by a design the Dev Manager reads. D14's check of the row locks the suites send (Stage B) covers what they run, whatever its form. The manager's verification comes first, and the Dev Manager's pre-merge read after the review.
>
> ## Sessions
> ```

**SC2 (yours: the brief, revision 10: C4's owned paths):**

> ```
> its runs of record only. Nothing else changes in C3.
> ```

> ```
> its runs of record only. Nothing else changes in C3.
> - **Correction C4 only** (DM-68): `proofs/postgres-ordering/glow_ordering_proof/account_lock_scan.py` and `discovery_cases.py`, with their offline tests in `proofs/postgres-ordering/tests/`; the proof README; the evidence record; and the P11 plan's SV3 entry, its runs of record only. Nothing else changes in C4.
> ```

**SC3 (yours: the brief, revision 10: a pointer in C3's section):**

> ```
> and is otherwise a value, not a path.
> ```

> ```
> and is otherwise a value, not a path (C4's item 1 counts more as a join here: "Stage A, correction C4"; DM-68).
> ```

**SC4 (yours: the brief, revision 10: D14, the row-lock check):**

> ```
>   - **The run's secrets** are generated and handled as SV1's and SV2's are.
> ```

> ```
>   - **Every account row lock the suites send, checked** (Stage B; DM-68). The lock scan reads the source and cannot be complete (the proof README's "Limits"), so Stage B adds a check of what the suites send. Each of the four suites records the text of every statement it sends through Django while its cases run (an execute wrapper on every connection it opens, those its concurrency cases open in other threads included), and fails if a statement takes a writer's row lock `FOR UPDATE`, not `FOR NO KEY UPDATE`, and names `glow_persistence_appaccount`, unless its lock clause is `FOR UPDATE OF` a list of names none of which is that table or an alias the statement gives it; a lock clause it cannot read that way fails too. It runs before the suite's verdict, and prints counts and each failing statement's text, never a parameter. Its reversal: one account lock in `services/api` taken without `no_key=True` fails every suite that runs it. It is exact for the statements the suites send through Django, and sees no code they do not run, which the scan reads for the forms it names. If a statement the code sent before Stage B fails it, Stage B stops and reports. The four suites' runners change for this record only.
>   - **The run's secrets** are generated and handled as SV1's and SV2's are.
> ```

**SC5 (yours: the brief, revision 10: acceptance check 15):**

> ```
> 14. **One pointer order** (D19): every SV3 transaction's pointer locks follow name order.
> ```

> ```
> 14. **One pointer order** (D19): every SV3 transaction's pointer locks follow name order.
> 15. **No account row locked `FOR UPDATE`** (Stage B; DM-68): in each of the four suites, no statement sent takes `FOR UPDATE` on the account table without an `OF` that excludes it (D14's check), with its reversal.
> ```

**SC6 (yours: the brief, revision 10: Stage B's owned path for the suites' runners):**

> ```
> with their offline tests and the README's "Limits".
> ```

> ```
> with their offline tests and the README's "Limits"; and, in Stage B, the four suites' runners, for D14's record of the row locks they send only (DM-68).
> ```

**SC7 (yours: the brief, revision 10: the review plan):**

> ```
>   - the proof's secret handling.
> ```

> ```
>   - the proof's secret handling, and, in Stage B, D14's record of the row locks the suites send, with its reversal (DM-68).
> ```

**SC8 (C4: the proof README's SV3 heading):**

> ```
> **SV3 Stage A, the discovery slice, with its corrections C1, C2 and C3** ([brief](../../docs/planning/sv3-eligibility-discovery-interactions.md), revision 9, with DM-60's to DM-67's conditions;
> ```

> ```
> **SV3 Stage A, the discovery slice, with its corrections C1 to C4** ([brief](../../docs/planning/sv3-eligibility-discovery-interactions.md), revision 10, with DM-60's to DM-68's conditions;
> ```

**SC9 (C4: the README's "Limits", the lock scan's entry, and the write check's after it):**

> ```
> - **The lock scan** (SV3 Stage A, corrections C1 to C3; DM-61, DM-65, DM-67): it reads the source, never imports it, and follows a queryset within one function. So it cannot see: the joins of a queryset, or of a `Q`, an `F` or another expression, that reaches the lock from another function (a lock on such a queryset is judged as a generic lock); an expression given as a keyword's value from outside the function; a model's `Meta.ordering` (none exists today); a model imported under another name (C1's rule, unchanged); and a lock clause built at run time (such as `FOR {mode}`).
> ```

> ```
> - **The lock scan** (SV3 Stage A, corrections C1 to C4; DM-61, DM-65, DM-67, DM-68): a static check of the forms its docstring names. It reads the source, never imports it, and follows a queryset within one function, so it cannot be complete: a queryset can be built, and a lock taken, in ways a reading of the source does not see. It refuses the forms it names; any other form is a stated limit, here and in the evidence record, not a defect of the scan, unless code uses it to lock an account row (DM-68). From Stage B, the suites also check every row lock they send, whatever its form (the brief's D14). So the scan cannot see: the joins of a queryset, or of a `Q`, an `F` or another expression, that reaches the lock from another function (a lock on such a queryset is judged as a generic lock); an expression given as a keyword's value from outside the function; a field path given to an expression through a name (`Lower(path)`), or to an expression class called by a lower-case name; a model's `Meta.ordering` (none exists today); a model imported under another name (C1's rule, unchanged), or a queryset of `AppAccount` held in a capitalised variable; a lock clause built at run time (such as `FOR {mode}`); and, in SQL, a view or other relation over the account table, named after `FROM`, `JOIN` or a comma (no migration creates one), a string joined or formatted after it is assigned to a name, and a `bytes` string. It does not read `dates()`, `datetimes()` or `in_bulk(field_name=...)`, which need no rule: PostgreSQL refuses a row lock with the `DISTINCT` the first two add, and `in_bulk`'s field is the model's own.
> - **A page by cursor's write check** (SV3 Stage A, corrections C2 to C4; DM-68): in `pages.one_snapshot_statements`, a statement is a read only if it begins with `SELECT` or `WITH` and holds none of the words `INSERT`, `UPDATE`, `DELETE`, `MERGE`, `INTO`, `TRUNCATE` or `COPY`; any other statement is a write. So it cannot see a write made inside a function a read calls (such as `nextval`, or a function the database defines).
> ```

**SC10 (C4: the scan's docstring, words to place after its first paragraph):**

> ```
> What the scan is (DM-68): a static check of the forms this docstring names. It reads the source and never runs it, so it cannot be complete: a queryset can be built, and a lock taken, in ways a reading of the source does not see. It refuses the forms named here; any other form is a stated limit (the proof README's "Limits"), not a defect of the scan, unless code uses it to lock an account row. From SV3's Stage B, the suites also check every row lock they send, whatever its form (the brief's D14).
> ```

**SC11 (C4: the P11 plan's SV3 entry; `RUN` and `HEAD` filled in by C4):**

> ```
> C3's is 43369448338 (on `72ace21`), with every job passing.
> ```

> ```
> C3's is 43369448338 (on `72ace21`), with every job passing; C4's is RUN (on `HEAD`), with every job passing.
> ```

## 10. Where each item goes

- **The brief, revision 10 (yours):** SC1 to SC7, and a Sessions line for DM-68's answer.
- **C4's prompt and session:** SC1's section, with SC8 to SC11 as its given words.
- **The review log:**
  - DM-68's dispositions, naming `513dfd7` as the commit this read covered;
  - DM-67's and DM-64's deferred rows closed (section 7);
  - a new row: SC1 to SC11, confirmed at my next consultation or the pre-merge read.
- **Notion:** the status after DM-68.

Status: complete

# DM-70 — SV3 Stage A: C5's bounded review, its open points, and the pre-merge read

- **From:** Dev Manager 5 (`session_01Q789u3CWg6s9pBGXerCQZt`), on `claude/dev-manager`. **To:** App Manager 11, relayed by Nathan (OD-25).
- **Read at:** `1b31cf7ef6966a96c6e004d327443bcd8ce9d53e` of `claude/magical-wozniak-yfmmx2`, PR45's head. This read covers it.
  - **The code** is C5's, `43986ba`, merged at `d579e34`. No non-Markdown path differs between `43986ba` and `1b31cf7`.
  - **Since my last read (`e297430`):**
    - DM-69 applied as the brief's revision 11, with C5's prompt (`44c7650`), and my DM-69 report merged (`66979b0`);
    - C5's three commits, which change only its five owned paths, and their merge (`d579e34`);
    - your verification (`52f3f23`), C5's review prompt (`41dba1f`), and the review's record with this consultation (`1b31cf7`).

    No governing path changed in that span.
  - **Remote heads at 21:20 UTC** (`git ls-remote`):
    - `main` `3240ef0`, and the manager branch at `1b31cf7`;
    - `claude/dev-manager` `ccd7336`;
    - C5's session branch, `claude/keen-cannon-p0ic1b`, at `9fa1798`;
    - C4's at `75986a8`, C3's at `8189b31`, C2's at `c79bfb6`, C1's at `cbeb050`, and Stage A's at `4dee875`.

    PR45 is the only open PR.
- **Written:** 14 November 2026, finished at 21:24 UTC by the clock.
- **Boundaries kept:**
  - Environment names only: `DATABASE_URL`, `HD_API_KEY` and `GEO_API_KEY` are absent, and so are the `STREAM_*` and `PG*` names; the three AWS names are present, as recorded before. I read no value.
  - No provider, database, HDE, Railway, Cloudflare or TypeSafe call. No application code run, no test suite run, no database.
  - **What I ran,** with `python3.12 -I`, from scripts kept outside the export:
    - copies of C4's and C5's lock scans (standard library only; they parse source and run none of it), over the export of `1b31cf7` and over planted files of my own;
    - the scripts that check DM-67's, DM-68's and DM-69's words as applied, and that verify this report's words.
  - **Read as text only:** psycopg 3.3.6's source distribution, downloaded from PyPI into its own directory, from which nothing was run.
  - GitHub and Notion were read, not changed. I wrote only this file.

## 1. What I read

- **The consultation** (revision 1).
- **The evidence record:** "Stage A, correction C5", "Manager verification of C5" and "Delta re-review of C5", whole; and C1's item 1, the seven account locks.
- **The brief's revision 11:** C4's and C5's sections, the termination rule, and D14.
- **The proof README:** its SV3 paragraph (C5's sentence) and its "Limits".
- **The code at `1b31cf7`:**
  - in `account_lock_scan.py`: the docstring, `_receiver_heads`, `_name_heads`, `_judge` and `scan()`;
  - in `discovery_cases.py`: `one_snapshot_statements`' docstring;
  - every `select_for_update` call in `services/api`;
  - the code the data model and the contract describe: `glow_discovery`'s `pages`, `policy`, `predicates`, `keys` and `views`; `glow_profiles.tx` and `settings_store.read_shared`; `glow_identity`'s `revocation` and `age`; and migration 0010.
- **Driver and framework source, as text:**
  - Django 5.2.17's `CursorWrapper` (`django/db/backends/utils.py`), the pinned version;
  - psycopg 3.3.6's cursor and connection, the proof's pinned driver.
- **For the pre-merge read:**
  - PR45's changes to governing paths (the manager workflow and the CI policy), and `.github/workflows/foundation.yml`'s SV3 steps;
  - the data model's and the contract's SV3 texts;
  - from GitHub: run 43620943919's eight jobs, and PR45's runs on `1b31cf7`.
- **The handoff, the review log's rows, and Notion,** read-only (section 8).

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1. F1 | **Approved, within item 1.** Nothing needs to state it before the merge; the docstring states it at Stage B's first change to the scan, in BB9's words (3.1) |
| 2. Class 3's words | **Agree.** The brief should say so; BB1 does, and also settles `SELECT truncate_x()` (3.2) |
| 3. F2 | **A record, not class 5.** It is corrected at Stage B's first change to the scan, in the review's words. No C6 (3.3) |
| 4. Limits and nits | **(a), approved with conditions** (4.1):<br>- F4 in the review's words (BB6);<br>- F5 in corrected words (BB5): the pinned driver has no `callproc`, and Django passes its `stream` and `copy` through unwrapped;<br>- D14's stated reach narrowed to match (BB2 to BB4);<br>- F7 and F8 in BB7 and BB8 |
| 5. Carried to Stage B | **Agree, with three additions** (4.3) |
| 6. The pre-merge read | **Done at `1b31cf7`. Nothing blocks the merge.** I accept the records batch as applied, on four conditions (5.6) |
| 7. AA1 to AA13 | **Confirmed as applied** at `1b31cf7` (section 6) |
| 8. The sequence | **Agree,** with the final head's checks spelt out (section 7) |
| 9. Notion | **No mismatch.** DM-69's three stale lines are fixed (section 8) |

**How to apply:**
- **Where each condition goes:**
  - BB1 to BB3: the brief's next revision (yours);
  - BB4 to BB8: the proof README, in your records batch;
  - BB9 and BB10: the carried-items file, "Carried to SV3 Stage B", for Stage B's first change to the scan.
- **The words are Markdown records, given exactly;** line breaks may move.
- **Verified by script** (`apply70.py`, outside the export):
  - each of the eight old passages occurs exactly once in its file at `1b31cf7`;
  - each pair applies to a copy, in order, and each new text then occurs once;
  - the report holds no model identifier.

## 3. Items 1 to 3 — F1, class 3 and F2

### 3.1 F1: within item 1

**Confirmed by planting,** with my own files against copies of both scans:
- `c = Match… | Match…; d = c; d.select_for_update(no_key=d is AppAccount)`:
  - refused at `43986ba` (`generic`, `FOR UPDATE`), passing at `ce260fc`;
  - the same with `d = c.filter(pk=a)`;
  - with `no_key=True`, it passes at both heads;
  - with `no_key=c is AppAccount`, it is refused at both (the receiver's own chain fails).
- A plain chain through the same hop (`c = Match.objects.filter(pk=a)`) passes at both: item 1 leaves plain chains as they were.

**Why it is item 1's own rule, not a new one:**
- Item 1 judges each chain a reached value holds "as item 2 of C4's section says".
- C4, as built and reviewed, also judges a name that holds such an expression by its own chain: a generic lock whose variable is that name. So `c = Match… | Match…; c.select_for_update(no_key=other is AppAccount)` is refused at `ce260fc`.
- C5 applies that same treatment at each hop. A name it passes through is judged as C4 judges the name it locks.

**What it changes:**
- It refuses more, never less.
- The tree's output is byte-identical.
- None of the forms it newly refuses locks an account row.

**Under the freeze it stays as built:**
- The freeze allows a rule change only to correct a defect in one of the five classes, or by a design I read.
- A false refusal of a planted form of another model is in no class. Section 3.2 makes that explicit for class 3.
- So nothing narrows it, and no design is needed.

**No statement before the merge:**
- Class 5 is a record that claims more than the scan does. No record says such a form passes.
  - The docstring's rules are conditions a lock must meet ("passes only if").
  - Its sentence on locks of another model covers a receiver that names the model, not a name that holds it.
- The record already describes the behaviour: the review's F1 and your reading.
- The docstring states it at Stage B's first change to the scan (BB9).

### 3.2 Class 3: agree, and the brief should say so

- **"A lock … passing" meant a lock in `services/api` or the reference design.** A planted form that newly fails closed is not a regression.
- **Two more gaps in the bullet as I wrote it:**
  - it names `72ace21`, C4's baseline, though later reviews read it against their own;
  - DM-69 ruled `SELECT truncate_x()` a stated limit, although the bullet, read literally, covered it.
- **BB1 rewrites the bullet to say all of it:**
  - the baseline is the head the review compares against;
  - "a lock" is a lock on the tree;
  - a planted form that newly fails closed is not a regression;
  - a form the baseline caught only through a pattern that a later item's words replace and exclude is a stated limit.

### 3.3 F2: a record, not class 5

- **Confirmed:** after an account combination and `d = c`:
  - `no_key=other is AppAccount` is refused at both heads, reported as `generic`;
  - `no_key=d is AppAccount` is reported as `orm`.
- **Why not class 5:**
  - Class 5 is a record that claims more than the scan or the check does: a refusal or a reach it does not have.
  - F2's sentence misstates only which failing chain's kind the message names.
  - It says no form is refused that passes, and the verdict is the same either way.
- **The review's words are right.** I read `_receiver_heads` and `_name_heads`:
  - the receiver's own chain comes first;
  - then each followed name's values, in the order they are assigned;
  - a value that only passes a name on puts the chains that name reaches before its own.
- **Where the correction goes:**
  - The docstring is code, so its text waits for Stage B's first change to the scan. There is no C6.
  - The record's C5 section carries the same claim, in "The chain reported". Your records-batch note names that sentence as corrected by F2's words, with no edit to C5's own section (5.6, condition 4).

## 4. Items 4 and 5 — the limits, the nits and Stage B

### 4.1 (a), with conditions

**F4: the review's words,** as a new "Limits" entry for C5's review (BB6). I planted all six of its forms against both scans: each passes at both heads as `generic`, `FOR NO KEY UPDATE`.

**F5: the review's words need one correction.**
- **`callproc` sends nothing here:**
  - the proof pins psycopg 3.3.6 (`requirements.lock`), and psycopg 3's source has no `callproc`;
  - Django's `CursorWrapper.callproc` calls the driver's `callproc`, so with this driver it raises before anything is sent.
- **What does bypass the probe:**
  - Django's `CursorWrapper.__getattr__` passes every attribute it does not define straight to the driver's cursor, so psycopg's `stream` and `copy` send statements with no execute wrapper;
  - so does the driver's own connection, `connection.connection`.
- **None of this is on the tree:**
  - no code in `services/api` or the proof uses `stream`, `copy`, `callproc` or `connection.connection`;
  - no migration defines a database function.
- **Read from source, not planted:** planting needs a database. Stage B plants them with D14's record (4.3, item 4).
- BB5 gives the corrected words.

**D14's reach, stated to match** (BB2 to BB4).
- **Three texts promise more than an execute wrapper can see.** Each says D14's check will cover what the suites send, whatever its form:
  - the README's lock-scan entry;
  - my termination rule, in the brief;
  - D14 itself: "exact for the statements the suites send through Django".
- **What an execute wrapper misses:** it sees only `execute` and `executemany`. It misses:
  - what the driver is handed directly;
  - a lock taken inside a database function that a statement calls.
- **Why now:** none of these is on the tree. But the termination rule leans on D14 as the backstop for the frozen scan, so D14's reach should be stated before Stage B is built against it.
- **Where:**
  - BB2 and BB3 narrow the brief;
  - BB4 narrows the README;
  - the scan's own docstring says the same, and follows at Stage B (4.3, item 5).

**F7 and F8:** BB7 and BB8.
- F8's words claim only what C5 changed: AA4 to AA6 qualified the README.
- The record's C1 section lists "every explicit lock of an `AppAccount` row". That is a fact about the tree, which later reviews confirmed by listing all 52 `select_for_update` calls by AST. It needs no note.

**F6, F9, F10 and F11** stand corrected in your reading, as you propose.

### 4.2 Why not (b)

- Stage B's brief and prompt will be written from the README's "Limits" and from D14. Carrying the wrong reach into them is the risk.
- The batch is Markdown only. It needs no session and no further review (5.6).

### 4.3 Carried to SV3 Stage B: agree, with three additions

The carried-items file, "Carried to SV3 Stage B", holds:
1. **F3's and F12's pinning tests,** as the review describes them.
2. **The docstring texts,** at Stage B's first change to the scan:
   - F2's sentence, in the review's words;
   - F1's statement, in BB9's;
   - `scan()`'s one-line docstring, in BB10's.
3. **A bound on the receiver rule's work:**
   - the slow shape: 4.9 s at 13 names, 13.3 s at 14;
   - the recursion at 496 hops, which fails closed.

   Under the freeze, the bound comes as a design I read. It must refuse beyond its bound, never pass.
4. **Added: D14's reach** (BB3). Stage B plants F5's forms against the write check and D14's record. For each of the following, it either closes the gap or states it with a planted example:
   - the driver's pass-through methods;
   - the driver's own connection;
   - a lock inside a database function.
5. **Added: two docstrings narrowed** as BB4 narrows the README, to what passes through `execute` and `executemany`:
   - the scan's opening sentence on Stage B;
   - `one_snapshot_statements`' "every statement it sends is a read", narrowed further to the default connection in the case's own thread.
6. **Added, needing nothing:** the review's observation of a capitalised name in a cycle. It is the capitalised-variable limit, already stated.

## 5. Item 6 — The pre-merge read, at `1b31cf7`

### 5.1 The CI policy's Database proof checks paragraph

**Approved.**
- It is unchanged since DM-67's read at `3000014`. RV4, its tie-break sentence, was confirmed in DM-66.
- I read it against `foundation.yml`'s SV3 steps, and they match:
  - a fourth database, `glow_discovery_proof`, with its own masked marker, where the other three markers are refused;
  - the reviewed migrations from zero, then `makemigrations --check --dry-run`;
  - the suite and `glow_ordering_proof.discovery_scan`, with counts only after a failed check, and the phase timed;
  - a second run refused, with the row counts unchanged;
  - `sv3-discovery-results` uploaded for 14 days, only after the check has passed;
  - the suite's own `SECRET_KEY` and RSA JWT key, generated and masked, the key written at mode 0600 with `O_EXCL`.

### 5.2 The data model's and the contract's rewritten texts

**Confirmed at the final head:**
- Neither file has changed since `39c0bf0` (C2), which DM-67's read covered.
- The code they describe is unchanged since then: C3 to C5 changed only the scan, the write check and the offline tests.
- I checked their claims against the code at `1b31cf7`:
  - the seven explicit account locks, each `no_key=True` or the `no_key=model is AppAccount` helper, among them `mark_verified`'s and the age transition's;
  - `read_account_shared`'s `FOR SHARE`, which a continued page takes;
  - the five settings, read in name order by one `read_shared` call;
  - `BATCH_LIMIT` 100, `PAGE_MAX` 50, a 30-minute lifetime, and a policy version built from the five version numbers;
  - `batch_collection` and `batch_one_per_collection`, in migration 0010, and the batch states;
  - `gen_random_uuid()` as the tie-break;
  - `AGE_CEILING` 150, with the age computed in SQL by `whole_years`' rule;
  - the cursor's `salted_hmac`, with its own salt;
  - `Cache-Control: no-store`.

### 5.3 C3's, C4's and C5's sections as applied

**Confirmed by script at `1b31cf7`:**
- **C5's section:** DM-69's AA1 to AA3, each once.
- **C4's section:** DM-68's SC1 to SC7.
  - SC2, SC3, SC5, SC6 and SC7 are found as given.
  - SC1 and SC4 are each found once with DM-69's AA1 and AA3 applied over them, as those pairs intended.
- **C3's section:** DM-67's GD1, found once with SC1, SC3 and AA1 applied over it.
- **The README's and the P11 plan's older texts** (SC8, SC9, SC11, and GD3 to GD10) read as the later pairs left them.

### 5.4 AA4 to AA13 as applied

**Confirmed:** section 6.

### 5.5 DM-64 T9 at C5's head

**Met for the code:**
- **The run of record:** 43620943919, on `43986ba`.
  - I read its eight jobs from GitHub: each a success, the discovery suite's steps among the Database proof checks', and every DM-41 retry step skipped.
  - T9's fix, C2's item, is in that code.
- **The review:** the correction's review approved at C2 (DM-67), and every later correction's review is recorded.
- **Codex:** nothing new on `44c7650`, `52f3f23` or `41dba1f`.
- **PR45's runs on `1b31cf7`:**
  - the pull-request run, 43639899348, passed (20:53 to 21:06 UTC);
  - the push run, 43639734709, ran no application job, since its push held only Markdown.
- **What remains:** after the records batch, the pull-request run and Codex on the final head.

### 5.6 Governing Markdown in PR45, and the records batch

**Two governing paths are in PR45's diff.** No `AGENTS.md`, `CLAUDE.md`, PF canon or charter changed.
- **The manager workflow:**
  - the checklist line (AM11-02, AM11-08) was approved in DM-62, a read of `3cdddd3`;
  - the only change since then (`b67bae2`): the supersession sweep also searches Notion's standing lines and a brief's previous revision number (AM5-22, AM11-11). I read that change now: **approved.** Every AM reference in it resolves.
- **The CI policy:** approved (5.1).

**The records batch: I accept it as applied, without a further read,** if:
1. it is Markdown only, outside any `.claude/` directory, and changes no governing path and nothing under `docs/architecture/`;
2. it applies BB1 to BB8 exactly, each old passage found once by script before and each new text once after. Beside them it holds only your own entries: the review log, the brief's status and Sessions lines, the carried-items file, the record's note and the handoff;
3. the non-Markdown tree is byte-identical to `43986ba`;
4. the record's note names what the batch applied, including the two new limits, and names the C5 section's "The chain reported" sentence as corrected by F2's words.

If any condition fails, I read the batch before the merge. I confirm the applied words at my next consultation.

## 6. Item 7 — DM-69's AA1 to AA13, as applied at `1b31cf7`

A script (`check_aa.py`, outside the export) parsed DM-69's thirteen entries and compared each new text with the tree, whitespace normalised:
- **AA1 to AA3,** in the brief's revision 11: each once, keeping their anchors, as insertions do.
- **AA4 to AA9,** in the README: each once, their old passages gone.
- **AA10 to AA12,** in the record: each once; AA11 keeps its anchor.
- **AA13,** in the P11 plan: once, with 43620943919 and `43986ba` filled in.

**The review log's rows:**
- DM-69's row (AA1 to AA13) can close.
- A new row: BB1 to BB8 as applied, confirmed at my next consultation.

## 7. Item 8 — The sequence

**Agree:**
1. the records batch, with BB1 to BB8;
2. on the final head:
   - the non-Markdown tree byte-identical to `43986ba`;
   - PR45's pull-request run, with all eight jobs and `Application checks passed` (DM-32 1.12);
   - Codex;
3. the merge by you, and its receipt;
4. the cleanup's deletion of the six session branches, keeping `main`, the manager branch and `claude/dev-manager`;
5. SV3's Stage B, from the brief, with the carried items in 4.3.

## 8. Item 9 — Notion (read-only, at about 21:10 UTC)

| Page | What I compared | Result |
|---|---|---|
| Implementation Control | The status heading and stamp | **Match:** "14 November 2026 (App Manager 11; SV3 Stage A, C1 to C5 in PR45; DM-70, the pre-merge read)", the handoff's title; matched at `1b31cf7` |
| Implementation Control | "Next items" | **Match:** the brief's revision 11; C5 built, verified and integrated; its review approved with nits; DM-70 next |
| Implementation Control | "Branches" | **Match:** nine, as `git ls-remote` shows, C5's `claude/keen-cannon-p0ic1b` (`9fa1798`) included; the six session branches kept until PR45 merges |
| Implementation Control | "Dev Manager"; "Mistakes log"; "Main"; standing directions | **Match:** Dev Manager 5; AM11-01 to AM11-21 at `be0907e`, the log's last change; `3240ef0`, with PR45 open; OD-01 to OD-65 |
| Dev Manager — reviews and approvals | DM-69's and DM-70's rows | **Match:** DM-69 answered (`ccd7336`); DM-70 pending |
| Register copy | Row IDs | **Match:** 65 rows, OD-01 to OD-65; the register is unchanged since `dacd0ea`, where the copy was matched |
| Work Register `SV3` | State, next action, evidence | **Match:** "In progress"; C5 merged at `d579e34`; DM-70 at `1b31cf7`; evidence pinned at `1b31cf7` |

DM-69's three stale lines are fixed: the status title, "Next items" and "Branches".

## 9. The words

**BB1 (yours: the brief's next revision: class 3's bullet, in C4's review section):**

> ```
> - a regression: a form refused, or a lock, test or case passing, at `72ace21` that is not at C4's head;
> ```

> ```
> - a regression: a form the scan or the write check refused at the head the review compares against (`72ace21` for C4's review) that the reviewed head passes, or a lock in `services/api` or the reference design, a test or a case that passes there and not at the reviewed head. A planted form that the reviewed head newly refuses (it fails closed) is not one; nor is a form the earlier head refused only through a pattern that a later item's words replace and exclude, which is a stated limit (`SELECT truncate_x()`; DM-69, DM-70);
> ```

**BB2 (yours: the brief's next revision: the termination rule's D14 sentence):**

> ```
> D14's check of the row locks the suites send (Stage B) covers what they run, whatever its form.
> ```

> ```
> D14's check of the row locks the suites send (Stage B) covers what they send through Django's `execute` and `executemany`, whatever its form, within the reach D14 states (DM-70).
> ```

**BB3 (yours: the brief's next revision: D14, the record's reach):**

> ```
> It is exact for the statements the suites send through Django, and sees no code they do not run, which the scan reads for the forms it names.
> ```

> ```
> It is exact for the statements the suites send through Django's `execute` and `executemany`, and sees no code they do not run, which the scan reads for the forms it names. It does not see a statement sent through the driver itself (a method of the driver's cursor that Django's cursor passes through unwrapped, such as psycopg's `stream` or `copy`, or the driver's own connection, `connection.connection`), nor a lock taken inside a database function a statement calls (no migration defines one today); Stage B closes each, or states it in the proof README's "Limits" with a planted example (DM-70).
> ```

**BB4 (your records batch: the proof README's "Limits", the lock scan's entry):**

> ```
> From Stage B, the suites also check every row lock they send, whatever its form (the brief's D14).
> ```

> ```
> From Stage B, the suites also check every row lock they send through Django's `execute` and `executemany`, whatever its form, within the reach the brief's D14 states.
> ```

**BB5 (your records batch: the README's "Limits", the write check's own reach; F5):**

> ```
> so a statement a page sends on another connection, or from another thread, is not read (planted: an `UPDATE auth_user SET is_active = is_active WHERE id = -1` sent from a thread on its own connection inside the page by cursor's transaction, on a local database); from Stage B, the suites' record of every statement they send lets the case check that none goes out there (the brief's D14).
> ```

> ```
> so a statement a page sends on another connection, or from another thread, is not read (planted: an `UPDATE auth_user SET is_active = is_active WHERE id = -1` sent from a thread on its own connection inside the page by cursor's transaction, on a local database), nor one sent through the driver itself: a method of the driver's cursor that Django's cursor passes through unwrapped (psycopg 3.3.6's `stream` and `copy`), or the driver's own connection (`connection.connection`). Those two are read from Django 5.2.17's and psycopg 3.3.6's source (C5's delta re-review's F5; DM-70), and Stage B plants them; `callproc` sends nothing here, since psycopg 3 has none. From Stage B, the suites' record of every statement sent through Django's `execute` and `executemany`, on any connection and from any thread, lets the case check that none goes out on another connection or from another thread (the brief's D14); a statement sent through the driver itself stays outside that record too.
> ```

**BB6 (your records batch: the README's "Limits", a new entry for C5's review; F4):**

> ```
> - **The scans' messages** (DM-64 T7):
> ```

> ```
> - **Further forms C5's delta re-review found** (SV3 Stage A, the records batch before PR45's merge; the review's F4, in its words; a stated limit under DM-68 and DM-70, each example planted by the review and by the Dev Manager, passing at C5's head and at C4's; the evidence record, "Delta re-review of C5"): a queryset passed on by a binding that is not a plain assignment, or by a call that wraps it (`match c:` then `case d:`; `d = copy.copy(c)`, `d = list(c)`, `d = await c`), and a combination written by a function, not an operator (`operator.or_(A, B)`, `reduce(operator.or_, [A, B])`): a lock on the name is judged as a generic lock, and its `no_key=<name> is AppAccount` passes though the name holds a queryset.
> - **The scans' messages** (DM-64 T7):
> ```

**BB7 (your records batch: the README's SV3 paragraph, C5's sentence; F7):**

> ```
> Offline tests pin C4's branches, each failing against a mutant of C4's code that C4's tests let pass;
> ```

> ```
> Offline tests pin C4's branches, each failing against a mutant of C4's code (C4's own tests fail four of those mutants too: `UPDATE`, `INTO`, `_climb`'s in-place entry and the read's start);
> ```

**BB8 (your records batch: the README's SV3 paragraph, C5's sentence; F8):**

> ```
> the records no longer say the scan finds every account lock;
> ```

> ```
> the README no longer says the scan finds every account lock (`scan()`'s one-line docstring still does, until Stage B's first change to the scan);
> ```

**BB9 (Stage B: the scan's docstring, F1's statement, after F2's corrected sentence):**

> ```
> Where it follows a name to such an expression, each value on the way that only passes a name on (`d = c`, `d = c.filter(...)`) is judged too, by its own chain, as a generic lock whose variable is that name, as C4 judges a name that holds one: after `c = Match.objects.filter(pk=a) | Match.objects.filter(pk=b)` and `d = c`, `d.select_for_update(no_key=d is AppAccount)` is refused (`generic`, `FOR UPDATE`), though it locks no account row. It fails closed; `no_key=True` passes.
> ```

**BB10 (Stage B: `scan()`'s one-line docstring; F8):**

> ```
> The explicit account locks, and generic locks that can take one, of the forms this module's docstring names, in the scanned files.
> ```

## 10. Where each item goes

- **The brief's next revision (yours):** BB1 to BB3, and a Sessions line for DM-70's answer.
- **Your records batch:**
  - BB4 to BB8, in the README;
  - the record's note (5.6, condition 4);
  - the carried-items file (4.3, with BB9 and BB10).
- **The review log:**
  - DM-70's dispositions, naming `1b31cf7` as the commit this read covered;
  - DM-69's deferred row closed;
  - a new row for BB1 to BB8.
- **Notion:** the status after DM-70.

Status: complete

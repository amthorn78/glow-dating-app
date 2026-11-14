# DM-71 — SV3 Stage B: its scope with the carried items, and the bound on the lock scan's work

- **From:** Dev Manager 5 (`session_01Q789u3CWg6s9pBGXerCQZt`), on `claude/dev-manager`. **To:** App Manager 11, relayed by Nathan (OD-25).
- **Read at:** `b120380b186e0a920fd5bc2709a0594391e49897` of `claude/magical-wozniak-yfmmx2`. This read covers it.
  - **`main` is `8d83474`,** PR45's merge. Its tree equals the records batch's (`7b79a35`), and its code is C5's: no non-Markdown path differs from `43986ba`.
  - **Since my last read (`1b31cf7`):**
    - my DM-70 report merged (`366e457`), and the records batch (`7b79a35`);
    - PR45's merge (`8d83474`), and its receipt (`829f90c`, `30e43b5`), which pruned Stage A's 23 prompts and consultations and re-pinned OD-64's link;
    - this consultation (`b120380`).

    No governing path changed in that span.
  - **Remote heads at 23:37 UTC** (`git ls-remote`): `main` `8d83474`, the manager branch at `b120380`, and `claude/dev-manager` `a03e8c8`. No PR is open.
- **Written:** 14 November 2026, finished at 23:42 UTC by the clock.
- **Boundaries kept:**
  - Environment names only: `DATABASE_URL`, `HD_API_KEY` and `GEO_API_KEY` are absent, and so are the `STREAM_*` and `PG*` names; the three AWS names are present, as recorded before. I read no value.
  - No provider, database, HDE, Railway, Cloudflare or TypeSafe call. No application code run, no test suite run, no database.
  - **What I ran,** with `python3.12 -I`, from scripts kept outside the export:
    - a copy of the lock scan at `b120380` (unchanged since `43986ba`; standard library only, it parses source and runs none of it), and a scratch prototype of the bound built from that copy, never pushed;
    - both over the export of `b120380` and over planted files of my own: the slow shape at 6 to 14 names, plain hop chains of 10 to 500, and combinations of 300 and 1,000 parts;
    - a script that counts the receiver rule's states and hops per lock, and the scripts that check DM-70's words as applied and verify this report's words.
  - **Read as text only:** Django 5.2.17's PostgreSQL backend, from the wheel kept since DM-68.
  - GitHub and Notion were read, not changed. I wrote only this file.

## 1. What I read

- **The consultation** (revision 1).
- **The brief's revision 12:** D1, D9 to D14, the owned paths, the exclusions, the acceptance checks, the review plan, and C5's section.
- **The carried-items file,** "Carried to SV3 Stage B (DM-66, DM-67, DM-69, DM-70)", whole.
- **The evidence record:** the records batch's note (`7b79a35`), and the exact-head review's N5.
- **The code at `b120380`:**
  - in `account_lock_scan.py`: `_holds_a_composite`, `_chain_base`, `_reaches_a_composite`, `_distinct`, `_receiver_heads`, `_name_heads`, `_passes`, the `Lock` record, `scan_file` and `main`;
  - in `profile_support.py`: `forms`, T3's `TIME_BEFORE`, `found_in` and `where`, and the value scans' callers in the suites;
  - in `glow_discovery/predicates.py`: `VIEWER`;
  - in `discovery_cases.py`: the query plans' parameters, and `one_snapshot_statements`' docstring.
- **Django 5.2.17's `django/db/backends/postgresql/base.py`:** `create_cursor`, `is_usable` and `init_connection_state`.
- **The handoff, the review log's rows, and Notion,** read-only (section 8).

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1. Stage B's shape | **(b), approved with conditions** (3.1):<br>- `VIEWER`'s unused column is app code, so it moves to Stage B;<br>- B0 also states one more limit I found;<br>- T7's lines are not built (item 4) |
| 2. The bound | **Approved with conditions** (3.2):<br>- the limits are 1,000 states and 100 names followed, not 10,000 and 200;<br>- the recursion may stay;<br>- no test asserts a time;<br>- the words are CC3's B0 item 1 |
| 3. Carried items 4 and 8 | **Agree, in Stage B.** "Close" may include a proof-only guard, on three conditions (3.3) |
| 4. T7's lines in CI | **Dropped** (3.4) |
| 5. The brief's revision 13 | **CC1 to CC4** (section 9): B0's section and Stage B's, B0's owned paths, and D1's order |
| 6. BB1 to BB8 | **Confirmed as applied** at `b120380`. All four of DM-70's conditions on the records batch held (section 5) |
| 7. The sequence | **Agree,** with two additions (section 6) |
| 8. Notion | **No mismatch of substance.** Two links are pinned one commit behind (section 8) |

**How to apply:**
- **Where each condition goes:** CC1 to CC4, the brief's revision 13 (yours). B0's prompt then takes CC3's B0 section as its given words, and Stage B's prompt takes CC3's Stage B section.
- **The words are Markdown records, given exactly;** line breaks may move.
- **Verified by script** (`apply71.py`, outside the export):
  - each of the four old passages occurs exactly once in the brief at `b120380`;
  - the pairs apply to a copy, in order, and each new text then occurs once;
  - the report holds no model identifier.
- **No further read is needed** before B0's prompt if CC1 to CC4 are applied as written. A departure comes back first.

## 3. Items 1 to 4

### 3.1 Stage B's shape: (b), with three corrections

**(b) is right.** It keeps one boundary per PR:
- B0 changes only the proof's tooling, under the lock scan's freeze;
- Stage B changes who may contact whom.

Each review then reads one thing: B0's under the five correction classes, and Stage B's with its threat model. One session, (a), would put the frozen scan's design change inside the contact review, so one review would have to read both.

**Three corrections to the split:**
- **`VIEWER`'s unused `distance_choice` is app code** (`services/api/glow_discovery/predicates.py`), so it cannot go in a B0 with no app code. It goes to Stage B, which owns `glow_discovery`. The proof follows it on its own, since its list of statements matches `predicates.VIEWER` itself.
- **One more stated limit, in B0:**
  - a combination of 1,000 parts raises `RecursionError` in the scan's reading of combinations, C4's `_parts`, at both `43986ba` and with the bound; one of 300 parts does not;
  - the scan then exits 1, so it fails closed, and no class applies;
  - but no record should let the bound's words be read as "no `RecursionError` can occur".
- **T7's lines in CI are dropped** (3.4), so Stage B takes carried items 4 and 8 only.

**B0's PR and review stand as you propose.**
- B0's review is a bounded delta re-review: the five classes for the scan and the write check, and DM-64 T9's reading for the value scans, whose rule B0 narrows.
- My pre-merge read follows it.

### 3.2 The bound: approved, with lower limits

**What the scan does now:**
- the receiver rule recurses two frames per name it follows (`_receiver_heads`, then `_name_heads`);
- it memoises each name under the set `seen` of names already on its path, so the states it can visit grow with the subsets of a function's names.

**Measured on this container:**

| Form | Memo states | Time per lock | At `b120380` |
|---|---|---|---|
| The tree, worst lock | 1 | under 0.1 ms | judged; 1 name followed |
| 8 names, each assigned from every other | 513 | 0.04 s | judged |
| 10 names | 2,561 | 0.29 s | judged |
| 12 names | 12,289 | 2.0 s | judged |
| 13 names | 26,625 | 5.8 s | judged |
| 14 names | 57,345 | 13.5 s | judged |
| 500 plain hops | — | — | `RecursionError` |

**Why lower limits than proposed:**
- With the proposed 10,000 states and 200 names, counting states as the words define them, my prototype refused the 14-name shape after 8.6 s for the whole run. That breaks the consultation's own test ("refused within a second").
- With 1,000 states and 100 names, it refused the 14-name shape in 0.8 s and the 500 hops in 0.3 s.
- In both, the tree's output stayed byte-identical: 52 calls, 0 joining, 7 account locks, every verdict the same.
- The tree's worst lock needs 1 state and 1 name, and C5's tests plant at most three hops. 1,000 and 100 leave room for any real code.

**What a hop and a state are:**
- **A hop** is a name the rule follows: it reaches such an expression, and its values are read. A model's name, which has no assignment in the function, is not followed and counts toward neither limit. My first prototype counted `AppAccount` as a hop and refused a 99-hop chain that should pass. The words say so.
- **A state** is a name followed under a distinct `seen`.

**The recursion may stay:**
- At 100 names its depth is about 200 frames, a fifth of Python's default limit, so no `RecursionError` can come from the receiver rule.
- An iterative rewrite is a larger change to frozen, reviewed code, and could change the order in which chains are judged, which F2's words describe. If B0 makes it iterative anyway, that order and every verdict stay the same.

**No test asserts a time.** A wall-clock assertion would be flaky on a shared runner. The tests assert each refusal's message; the record states the times.

**The words** are CC3's B0 item 1. The reversal is the scan at `8d83474`.

### 3.3 Carried items 4 and 8: in Stage B, and what "close" may mean

**Agree:** both belong with D14's record.

**"Close" may include a proof-only guard, if:**
1. it acts only in the suites' processes, and nothing in `services/api` changes for it;
2. it refuses only what the record cannot see: psycopg's `stream` and `copy`, which Django's `CursorWrapper.__getattr__` passes through unwrapped, when a case calls them;
3. it never refuses Django's own use of the driver's connection.

**Why condition 3 matters:** Django's PostgreSQL backend uses the driver's connection directly, and a broad guard would break it:
- `create_cursor` opens every cursor there;
- `is_usable`, the health check, runs `SELECT 1` "bypassing Django's utilities";
- `init_connection_state` configures each new connection.

**What follows from that:**
- The driver's own connection, used by code, is closed only by what Stage B can check without breaking Django, or it is stated.
- A lock inside a database function may be closed by a check that the migrated database defines no function of its own, with its reversal. No migration defines one today: there is no `RunSQL` in any migration.
- Each close has a planted reversal.

### 3.4 T7's lines in CI: dropped

- **The job withholds a failed scan's output on purpose:** acceptance check 13, "no secret and no private value in any output".
- **What letting the lines through would mean:** a filter that lets T7's lines through, however closed its vocabulary, is a new path from a member value to a public log.
- **What it would buy:** reading those lines from a local run, which the README already describes. That is not worth the path.
- **Where it goes:** the carried-items file records it as not built (DM-71). It comes back only as its own item, with its own review, if a failed scan in CI ever cannot be diagnosed locally.

## 4. Item 5 — The brief's revision 13

CC1 to CC4, in section 9:
- **CC1:** D1's order (Stage A, B0, Stage B);
- **CC2:** B0's owned paths;
- **CC3:** B0's section and Stage B's section, before "Sessions";
- **CC4:** Stage B's runners, which may carry the guards.

Stage B's other owned paths, stops and review are the brief's existing ones. Its section names only what DM-71 adds.

## 5. Item 6 — DM-70's BB1 to BB8, and the records batch

**BB1 to BB8, confirmed as applied at `b120380`** (`check_bb.py`, whitespace normalised):
- **BB1 to BB3,** in the brief's revision 12: each once, its old passage gone.
- **BB4, BB5, BB7 and BB8,** in the README: each once, its old passage gone.
- **BB6:** once, keeping its anchor, as an insertion does.

**DM-70's four conditions on the batch, all held:**
1. **Markdown only:** six files (the handoff, the review log, the carried-items file, the brief, the record and the README), none under `.claude/`, none governing, nothing under `docs/architecture/`.
2. **Only BB1 to BB8 and your own entries.**
3. **The non-Markdown tree** is byte-identical to `43986ba`. PR45's merge has the batch's tree.
4. **The record's note** names what the batch applied, the two new limits, and the C5 section's "The chain reported" sentence as corrected by F2's words.

**The review log's rows:**
- DM-70's row (BB1 to BB8) can close.
- A new row: CC1 to CC4 as applied, confirmed at my next consultation.

## 6. Item 7 — The sequence

**Agree, with two additions:**
1. this answer;
2. the brief's revision 13, with CC1 to CC4;
3. **B0:**
   - its prompt, with its TypeSafe reading;
   - B0 itself, then your verification;
   - its PR, and Codex;
   - its bounded review, then my pre-merge read, of the bound as built and B0's records, at a named commit;
   - the merge, its receipt, and the cleanup of B0's session branch;
4. **Stage B,** from `main` after that:
   - its prompt;
   - Stage B itself, then your verification;
   - its PR, and Codex;
   - the exact-head review with its threat model;
   - my pre-merge read: the CI policy's paragraph, the data model's and the contract's rewritten texts, and any governing Markdown;
   - the merge.

**The additions:**
- B0 merges before Stage B's prompt is written, so Stage B starts from the bounded scan.
- Stage B's prompt names B0's merge commit as its start.

## 7. What B0's and Stage B's sessions must not lose

- **The freeze holds through both:**
  - B0 changes the scan's rules for the bound alone;
  - Stage B changes none. D14's record is a separate check, not a scan rule.
- **The termination rule binds both reviews** (BB1's class 3 included).

## 8. Item 8 — Notion (read-only, at about 23:30 UTC)

| Page | What I compared | Result |
|---|---|---|
| Implementation Control | The status heading and stamp | **Match:** "14 November 2026 (App Manager 11; SV3 Stage A merged at 8d83474; DM-71 on Stage B's scope)", the handoff's title; matched at `b120380` |
| Implementation Control | "Next items" | **Match:** the brief's revision 12; Stage A done and merged at `8d83474`; Stage B next, with DM-71 |
| Implementation Control | "Main"; "Branches" | **Match:** `8d83474`, no PR open; three branches, as `git ls-remote` shows, `claude/dev-manager` at `a03e8c8` |
| Implementation Control | "Dev Manager"; "Mistakes log"; standing directions | **Match:** Dev Manager 5; AM11-01 to AM11-21 at `be0907e`, the log's last change; OD-01 to OD-65 |
| Dev Manager — reviews and approvals | DM-70's and DM-71's rows | **Match:** DM-70 considered (BB1 to BB8 applied at `7b79a35`); DM-71 pending |
| Register copy | Rows and text | **Match in substance:** 65 rows. The register's one change since the copy's match (`dacd0ea`) is OD-64's decision-message link, re-pinned at `8d83474` when its prompt was pruned (`829f90c`). The copy's link, pinned at `058829c`, still resolves |
| Work Register `SV3` | State, next action, evidence | **Match:** "In progress"; Stage A merged; DM-71 at `b120380`. Its evidence link is pinned at `829f90c`, one commit before the record's last change (`30e43b5`, `main`'s push run) |

Neither pinned link misleads. Both can follow at your next sync.

## 9. The words

**CC1 (yours: the brief's revision 13: D1, the order of the stages):**

> ```
> Stage B starts from `main` after Stage A merges.
> ```

> ```
> Stage B starts from `main` once Stage A and then B0, a proof-tooling session with no app code, have merged (DM-71).
> ```

**CC2 (yours: the brief's revision 13: B0's owned paths):**

> ```
> its runs of record only. Nothing else changes in C5.
> ```

> ```
> its runs of record only. Nothing else changes in C5.
> - **B0 only** (DM-71): `proofs/postgres-ordering/glow_ordering_proof/account_lock_scan.py`; in `discovery_cases.py`, `one_snapshot_statements`' docstring and the query plans' unused `batch` parameter only; in `profile_support.py`, T3's rule and `forms` only, with the suites' calls of the value scans only to name the response headers' text for T3; the offline tests in `proofs/postgres-ordering/tests/`; the proof README; the evidence record; and the P11 plan's SV3 entry, its runs of record only. Nothing else changes in B0.
> ```

**CC3 (yours: the brief's revision 13: B0's section and Stage B's, before "Sessions"):**

> ```
> ## Sessions
> ```

> ```
> ## Stage B, B0: the proof's tooling (DM-71)
>
> B0 applies, before Stage B and in its own PR, from `main` (`8d83474`), the items carried to Stage B that change only the proof's tooling: items 2, 3, 5, 6, 7 and 9 of the carried-items file's "Carried to SV3 Stage B", and the proof's two N5 items. Under DM-68's freeze, the lock scan's rules change only for item 1, a design the Dev Manager read (DM-71). B0 changes no app code, predicate, selection, recheck, lock, writer, workflow, contract, model, migration, lock file or dependency.
>
> 1. **A bound on the receiver rule's work** (DM-70; the design DM-71 read). For each lock, the receiver rule follows at most 100 names along one chain, and visits at most 1,000 states in all, a state being a name it follows under a distinct `seen`. A name is followed when it reaches such an expression and its values are read; a name with no assignment in the function (a model's name) is not followed and counts toward neither limit. Beyond either limit, the lock is refused and never passes: it is recorded as a lock that is not `FOR NO KEY UPDATE`, and its line names the limit, the function and the lock's line (for example `BAD <path>:<line> (<function>, bound: more than 1000 states): FOR UPDATE`). The limits are module constants, and the docstring states them and the refusal. The traversal may stay recursive: at 100 names its depth is about 200 frames, a fifth of Python's default limit. If it is made iterative, the order in which chains are judged, which F2's words describe, and every verdict stay the same. Its offline tests: 14 names, each assigned from every other, refused with the states limit's message; a chain of 500 plain hops, refused with the names limit's message and not a `RecursionError`; with `no_key=True`, 8 such names and a chain of 99 hops (100 names followed), each passing as before; and the tree unchanged (52 calls, 0 joining, 7 account locks, the output byte-identical). No test asserts a time; the record states each. Its reversal: the scan as at `8d83474`, which takes about 13 s on the 14 names and raises `RecursionError` on the 500 hops.
> 2. **The scan's docstrings** (DM-70; carried item 6, and item 9's first): F2's reported-chain sentence, in the review's words (the evidence record, "Delta re-review of C5", "Words the review proposes"), in place of the docstring's sentence on which chain is reported; BB9's statement after it; `scan()`'s one-line docstring, in BB10's words; and the opening paragraph's sentence on Stage B as: "From SV3's Stage B, the suites also check every row lock they send through Django's ``execute`` and ``executemany``, whatever its form, within the reach the brief's D14 states."
> 3. **`one_snapshot_statements`' docstring** (DM-70; carried item 9's second): "every statement it sends is a read" becomes "every statement its probe records (``execute`` and ``executemany`` on the default connection, in the case's own thread) is a read".
> 4. **Pinning tests** (DM-70; carried item 5): as the carried item says, each failing against its mutant.
> 5. **T3's date rule, narrowed** (DM-67; carried item 2): as the carried item says, to the `Expires` header's own shape in the response headers' text alone. The date beside a held time is then counted too: `forms` gains a date's HTTP and email shape, its day in two digits and in one, with a three-letter month (`15 Jun 1990`, `5 Jun 1990`), and the README's "Limits" drops that gap. Its offline tests, T6's: the `Expires` header's time not a hit; a held time after another date, or in another text, a hit; a held date in the new shape a hit; and reversals against the wider rule and against `forms` without the new shape.
> 6. **An offline test of the database search** (DM-67; carried item 3): as the carried item says.
> 7. **The proof's N5 items** (the brief's N5 follow-up): the offline test classes that stand after `unittest.main()` in `tests/test_discovery_offline.py`, moved before it; and the query plans' unused `batch` parameter, removed. `VIEWER`'s unused column is app code, and is Stage B's.
> 8. **A stated limit** (DM-71): a combination of 1,000 parts exceeds Python's recursion limit in the scan's reading of combinations (C4's `_parts`), so the scan exits 1: it fails closed. One of 300 parts does not. In the README's "Limits", with that planted example.
> 9. **The records:** the README's SV3 heading (B0), with a sentence on what B0 adds, in B0's words; its "Limits" for items 1, 5 and 8; in the record, a section "Stage B, B0"; and, in the P11 plan's SV3 entry, B0's run of record.
>
> **The stop rule (B0):** stop and report if B0 needs a change outside its owned paths, or any change to app code, a predicate, the selection, the recheck, a lock, a writer, the workflow, or a rule of the lock scan beyond item 1; if the bounded scan changes any verdict or line of its output on the tree; if a test of C1's to C5's sections no longer passes; if the narrowed rule or the new date forms make the profile or discovery suite find a value in a clock text; or if a case can hold a date the run's clock prints, which the new forms would then match.
>
> **B0's run of record:** a push run on its code head, with all eight jobs passing (the ordering, identity, profile and discovery suites among them), read from GitHub.
>
> **B0's review** (DM-71): a bounded delta re-review of B0's code head against `8d83474`, under the five correction classes of C4's section for the lock scan and the write check, and DM-64 T9's reading for the value scans (no real print lost; a clock text left uncounted only where its rule says), bounded to: item 1, planted by its words (each limit just inside and just beyond, the 14 names and the 500 hops), with its reversal, and the tree's counts and verdicts; the scan's diff, which may change nothing but item 1's rule and the docstrings (any other change to a rule is reported to the Dev Manager before the merge, under DM-68's freeze); items 4 to 6, each test failing against its mutant or its reversal; items 7 and 8; and the records. The manager's verification comes first, and the Dev Manager's pre-merge read after the review. B0 merges before Stage B's prompt.
>
> ## Stage B: interactions (DM-71)
>
> Stage B builds Outcome items 4 to 7 and their routes (D9 to D12, with D13's additions for them), and D14's Stage B cases with the record of the row locks the suites send (acceptance checks 7 to 12 and 15, with 13 and 14 for its own code), from `main` after B0 merges. With them come three items DM-71 placed here:
>
> 1. **The probe's reach** (DM-69; carried item 4): with D14's record, `pages.one_snapshot_statements` checks that, while a page runs, no statement goes out on another connection or from another thread. Its reversal: C4's delta re-review's planted statement, an `UPDATE` sent from a thread on its own connection inside the page by cursor's transaction, fails the case. The README's limit for it is rewritten to what remains.
> 2. **D14's reach** (DM-70; carried item 8; D14, BB3): Stage B plants F5's forms against the write check and D14's record: psycopg's `stream` and `copy` through Django's cursor, the driver's own connection, and a lock taken inside a database function. For each, it closes the gap or states it in the README's "Limits" with its planted example. A close may be a proof-only guard (DM-71): it acts only in the suites' processes, and nothing in `services/api` changes for it; it refuses the driver cursor's methods that Django's cursor passes through unwrapped when a case calls them, with a reversal; and it never refuses Django's own use of the driver's connection (creating cursors, the health check's `SELECT 1`, configuring a new connection). A lock inside a database function may be closed by a check, with its reversal, that the migrated database defines no function of its own (no migration defines one today).
> 3. **`VIEWER`'s unused `distance_choice`** (the brief's N5 follow-up): removed from `predicates.VIEWER`. The proof's list of statements follows it, since it matches `predicates.VIEWER` itself.
>
> T7's lines in CI (DM-66) are not built (DM-71).
>
> **The stop rule (Stage B):** the brief's own stops (D14: a statement the code sent before Stage B fails D14's check; D16: a new dependency; the owned paths: a mobile source, test or fixture; D10 (a): any change to an existing writer in `glow_chat`); and stop and report if Stage B needs a change to the lock scan's rules or to B0's bound (DM-68's freeze), or a guard that would refuse Django's own use of the driver's connection.
>
> **Stage B's run of record:** a push run on its code head, with all eight jobs passing, D14's check passing in each of the four suites with its counts, and the discovery phase's duration within the job's 30 minutes, read from GitHub.
>
> **Stage B's review:** as the "Review plan" says: an exact-head code and security review of Stage B's final code head, with a written threat model, after Codex. It takes the items for contact, whatever Stage B changes in Stage A's code, D14's record with its stated reach and each guard, and C4's five correction classes for the lock scan and the write check. The manager's verification comes first, and the Dev Manager's pre-merge read after the review: the CI policy's paragraph and the data model's and the contract's rewritten texts, at a named commit.
>
> ## Sessions
> ```

**CC4 (yours: the brief's revision 13: Stage B's runners, for the guards):**

> ```
> and, in Stage B, the four suites' runners, for D14's record of the row locks they send only (DM-68).
> ```

> ```
> and, in Stage B, the four suites' runners, for D14's record of the row locks they send and for the guards DM-71 allows only (DM-68, DM-71).
> ```

## 10. Where each item goes

- **The brief's revision 13 (yours):** CC1 to CC4, and a Sessions line for DM-71's answer.
- **The carried-items file:**
  - B0's items and Stage B's marked as placed;
  - T7's lines recorded as not built (DM-71);
  - N5's `VIEWER` item moved to Stage B.
- **The review log:**
  - DM-71's dispositions, naming `b120380` as the commit this read covered;
  - DM-70's deferred row closed;
  - a new row for CC1 to CC4.
- **Notion:** the status after DM-71, and the two pinned links in section 8 at your next sync.

Status: complete

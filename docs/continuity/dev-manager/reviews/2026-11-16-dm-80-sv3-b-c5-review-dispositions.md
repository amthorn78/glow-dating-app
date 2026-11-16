# DM-80 — SV3 Stage B: B-C5's short review, before PR47's pre-merge read

- **From:** Dev Manager 5 (`session_01Q789u3CWg6s9pBGXerCQZt`), for App Manager 11, relayed by Nathan (OD-25).
- **Date:** 16 November 2026. Received about 23:14 UTC; finished about 23:20 UTC.
- **Read at:** `3962900468ea3abef107f7f4cbeeae3551bc549e` of `claude/magical-wozniak-yfmmx2`, exported outside any worktree.
  - Its code equals `0d784d4`'s: `git diff 0d784d4 3962900` is empty outside Markdown.
  - The governing diff since my last read (`f3f1c64`) is empty. The commits since are DM-79's merge and disposition, B-C5 and its verification, and the review's record with DM-80.
- **Environment:** names only. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, or any `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name is set. The AWS names are present and were not read.
- **What I changed:** this file only, on `claude/dev-manager`. Notion was read, not changed. No call to Stream, a database, HDE, Railway or Cloudflare.
  - My probes live in my scratchpad and are not committed. They load `row_locks.py` from the export of `3962900` under `python3 -I`.

## 1. The answers

| Item | Verdict |
|---|---|
| 1. R1, every word of `_ENDS_FROM` after a dot | **(b): one home.** The README's F1 limit states the mechanism and R1's example (LL3, LL4). The four texts drop their listed exception and point to it (LL2, LL5 to LL7). LL1, LL8 and LL9 are the words for KK2's paragraph, KK12 and KK14 (section 4) |
| 2. N1, Django's `ON` conditions | **(a): narrowed in the same correction,** to the ORM's joins (in LL4; section 5) |
| 3. How the words land | **(a): B-C6, a records correction like B-C5, with a short review.** Its method checks every sentence about the relations check's reading against every way the reading ends a list. Its section and owned paths are LL10 and LL11 (section 6) |
| 4. The sequence | **Agreed** (section 7) |
| 5. Notion | **One stale count.** Implementation Control's Branches bullet says "nine", while ten branches exist; B-C5's session branch is named in the bullet but not counted (section 8) |

## 2. What I read and checked

- **The consultation's file** at `3962900`.
- **The record:**
  - "Stage B, correction B-C5" (from line 2696);
  - "Manager verification of B-C5";
  - "Delta re-review of B-C5" (from line 2793).
- **The code at `0d784d4`:**
  - `_ENDS_FROM`;
  - the scan in `_bindings`: an alias the item reader takes is stepped over, and any other word of `_ENDS_FROM` at the list's own depth ends the list;
  - the three docstrings B-C5 changed.
- **Reproduced with `judge`,** with a set of model tables given:
  - R1's form passes with each of the sixteen words, in both the `JOIN v` and the `, v` form: 32 of 32, each with `for_update` true and no reason;
  - the controls are refused: the column `g.lim`, the condition in parentheses, and `g."limit"` quoted;
  - an account-naming statement with `OF v` is refused ("FOR UPDATE OF a name the statement gives no table").
- **DM-79's sixteen texts** are each found once at `3962900`, with their old passages gone.
- **Every text that names `set` or `values`:**
  - the four R1 names (README line 240; `row_locks.py` lines 72 and 759; the record's line 2455);
  - KK5's limit itself (README line 242);
  - the README's B-C5 sentence (line 19);
  - the brief's D14 rule (line 154);
  - your note in "Manager verification of B-C4" (record line 2667);
  - a code comment on `_KEYWORDS` (`row_locks.py` line 266), which is about bare aliases and is true;
  - history in the reviews' own sections and the brief's "Sessions", left as it is.
- **Notion:** section 8.

## 3. My own errors in this round

R1 and N1 both rest on my DM-79 words.

- **R1:** I listed `set` and `values` as the only exception in five places (KK3, KK5, KK6, KK9 and KK10), after reading F1 as an alias problem.
  - I asked which words of `_ENDS_FROM` can be an alias.
  - The right question was where a word of that list can stand at the list's depth without ending the `FROM` list in SQL. A column's name after a dot takes any of them, reserved words included.
  - DM-79's own lesson was to try a list of positions against every word its reader treats as an end. I applied it to one position only.
- **N1:** "Django writes every `ON` condition in parentheses" was wider than what I had checked, which was the ORM's joins.

The lesson I take: a limit's detail is stated once, as the mechanism the code follows, and every other text points to it. Copies of a list of exceptions are what carried my error into four files. The words below follow that.

## 4. Item 1 — R1, every word of `_ENDS_FROM` after a dot

- **(b), as you recommend.** One home, KK5's F1 limit, states the mechanism. The four texts R1 names drop their listed exception and point to it.
- **Why (b) over (a).**
  - (a) would put the mechanism's words in four places, and each copy would have to stay exact.
  - KK1, KK2, KK8 and KK13 already say "the positions its reading binds" and point to "Limits"; the review found them true. The four texts now say the same.
  - This follows "One home per fact" (`docs/README.md`).
- **The mechanism, as the code follows it** (LL4).
  - The reading ends a `FROM` list at any of the sixteen words of `_ENDS_FROM` that it meets at the list's own depth.
  - The only exception is a word it takes as an item's name or alias, which the item reader steps over.
  - So the list ends at such a word written as a column's name after a dot (`g.limit`), as a column's qualifier (`set.id`), or in any other way.
  - The limit lists the sixteen words, so a reader can check the text against `_ENDS_FROM` without the code.
- **Its reach is F1's.**
  - Only a statement that takes `FOR UPDATE` and does not name the account table is affected.
  - An account-naming statement is judged by the account rule; my probe with `OF v` is refused.
  - Django's ORM writes each join's `ON` condition in parentheses and quotes every column's name. The quoted control is refused.
- **The three texts that describe F1 as found:**
  - **KK2's B-C5 sentence** (README line 19) records what B-C5 did, and is true as history. LL1 adds B-C6's sentence after it, which says the limit was widened, rather than rewriting B-C5's sentence;
  - **KK12, your note** (record line 2667), is true as history. LL8 adds R1 to it;
  - **KK14, the brief's D14 rule** (line 154), says "among them", so it claims no complete list, but it should describe the limit as it now stands. LL9 does.
- **The words:**
  - LL1 to LL7 are B-C6's: the README, the two docstrings and the record's account of the check;
  - LL8 to LL11 are yours: your note, and the brief's revision 21.

## 5. Item 2 — N1, Django's `ON` conditions

- **(a): narrowed in the same correction,** since it is in the bullet LL4 replaces.
- **The new words:** "Django's ORM writes every join's `ON` condition in parentheses and quotes every column's name". The second half is R1's reach as the review states it, and the quoted control shows why it matters.

## 6. Item 3 — how the words land

- **(a): B-C6, a records correction like B-C5.**
  - It changes two docstrings in `row_locks.py` (the module's and `_relations`'s), so the change is full scope.
  - It needs a run of record, your verification, and a short review run by Nathan (DM-79 section 8; my charter; the CI policy).
- **The review's method closes the class of gap, not one word.** It finds every sentence outside the reviews' own sections that says what the relations check reads or where its reading stops. It checks each one against the scan in `_bindings`:
  - every word of `_ENDS_FROM` in every position the tokenizer can give it: an item's name or alias, a column's qualifier, a column's name after a dot, a function's name, a bare word;
  - the closing parenthesis, which ends a list opened inside it.
- **After B-C6, only one sentence states where the reading stops:** the README's F1 limit. The others point to it. So that check is short.
- **The words:** B-C6's section (LL10) and owned paths (LL11).

## 7. Item 4 — the sequence

- **Agreed.** Three notes:
  - the brief's revision 21 holds LL9 to LL11;
  - LL8 is your own record note, applied with the records, before B-C6;
  - my pre-merge read of PR47 confirms DM-75's and DM-77's to DM-80's texts as applied.

## 8. Item 5 — Notion (read-only, at about 23:17 UTC)

| Page | What I compared | Result |
|---|---|---|
| Implementation Control, status | Last matched at `3962900`, with B-C5's review and DM-80 | **Match** |
| Its Branches bullet | Its count and listing time, against `git ls-remote` now | **Mismatch:** it says "nine" and "listed … 18:07 UTC". Ten branches exist now: `claude/brave-gates-1ty8o2`, B-C5's session branch, which the bullet names, was created after that listing and not counted |
| Its Mistakes log bullet | AM11-01 to AM11-32, at `2e669c8`; the log has not changed since | **Match** |
| Its procedure summary | The stamp at `b192164`; no governing change since | **Match** |
| Dev Manager page, `DM-79` and `DM-80` | DM-79 answered and considered; DM-80 pending, at `3962900` | **Match** |
| The register copy | Matched at `e19f731`, OD-66 last; the register has not changed since | **Match** |
| Work Register, `SV3` and `M08` | SV3 at DM-80, evidence pinned at `3962900`, the brief at revision 20; M08 unchanged | **Match** |

The mismatch is AM11-08's pattern: a bullet gained an item and kept its count. The repository wins (OD-27). The fix is the count and the listing time.

## 9. The words

**LL1 — the proof README, `proofs/postgres-ordering/README.md` (B-C6): the SV3 paragraph's B-C6 sentence (R1).**

> ```
> and corrects the record (the D14 entry and "Limits" below).
> ```

> ```
> and corrects the record (the D14 entry and "Limits" below). **Correction B-C6** (B-C5's short review; DM-80) changes no rule and adds no case, 66 in all: F1's limit now states its mechanism, an item after any word that the reading takes as the end of the `FROM` list, a column's name after a dot included (R1), and the texts that say what the relations check reads point to that limit alone (the D14 entry and "Limits" below).
> ```

**LL2 — the proof README, `proofs/postgres-ordering/README.md` (B-C6): D14's relations check (R1).**

> ```
> a `WITH` query's name read as one included, but not an item after a `set` or `values` that the reading takes as the end of the `FROM` list: F1 in the limits under the freeze, below), is one of those tables,
> ```

> ```
> a `WITH` query's name read as one included; where the reading stops is F1 in the limits under the freeze, below), is one of those tables,
> ```

**LL3 — the proof README, `proofs/postgres-ordering/README.md` (B-C6): the limits' heading (R1, N1).**

> ```
> (SV3 Stage B, after B-C4; D14's rules frozen from `07d8de3`, DM-78; B-C4's delta re-review, the last of D14 under all five classes, F1 and F2; DM-79; each with its planted example, the evidence record's "Delta re-review of B-C4"):
> ```

> ```
> (SV3 Stage B, after B-C4; D14's rules frozen from `07d8de3`, DM-78; B-C4's delta re-review, the last of D14 under all five classes, F1 and F2; DM-79; B-C5's short review, R1 and N1; DM-80; each with its planted example, the evidence record's "Delta re-review of B-C4" and "Delta re-review of B-C5"):
> ```

**LL4 — the proof README, `proofs/postgres-ordering/README.md` (B-C6): F1's limit, its mechanism and R1's example (R1, N1).**

> ```
> F1, the relations check reads a `FROM` list until a word that ends one, and `set` and `values`, which can also be an alias, are among those words: where either stands at the list's own depth other than as an item's alias (as a column's qualifier in an `ON` condition written without parentheses, `JOIN glow_persistence_block set ON set.id = m.id`), the list ends there, so a later `JOIN` or comma item is not read, and a relation outside the models there passes (`SELECT m.id FROM glow_persistence_match m JOIN glow_persistence_block set ON set.id = m.id JOIN v ON true FOR UPDATE`, and `…, v FOR UPDATE`; with `v` a view over the account table, PostgreSQL 17.11 held the account row `FOR UPDATE`; with the alias `s`, or the condition in parentheses, each is refused). Django writes every `ON` condition in parentheses, and a statement that names the account table is judged as before:
> ```

> ```
> F1, the relations check reads a `FROM` list until a word that ends one (`except`, `fetch`, `for`, `group`, `having`, `intersect`, `limit`, `offset`, `order`, `returning`, `select`, `set`, `union`, `values`, `where` or `window`): where one of those words stands at the list's own depth and the reading does not take it as an item's name or alias, as a column's name after a dot (`g.limit`), a column's qualifier (`set.id`) or otherwise, the list ends there, so a later `JOIN` or comma item is not read, and a relation outside the models there passes. The planted examples are `SELECT m.id FROM glow_persistence_match m JOIN glow_persistence_block set ON set.id = m.id JOIN v ON true FOR UPDATE` (B-C4's delta re-review, F1) and `SELECT m.id FROM generate_series(1, 1) AS g("limit") JOIN glow_persistence_match m ON m.id = g.limit JOIN v ON true FOR UPDATE` (B-C5's short review, R1, which passes with each of the sixteen words), each also as `…, v FOR UPDATE`; with `v` a view over the account table, PostgreSQL 17.11 held the account row `FOR UPDATE` in F1's form, and R1's was not run on PostgreSQL; with the alias `s`, the condition in parentheses, or the column's name quoted (`g."limit"`), each is refused. Django's ORM writes every join's `ON` condition in parentheses and quotes every column's name, and a statement that names the account table is judged as before:
> ```

**LL5 — `proofs/postgres-ordering/glow_ordering_proof/row_locks.py` (B-C6): the module docstring's rule paragraph (R1).**

> ```
> ``WITH`` query's name read as one included, but not an item after a ``set`` or ``values`` that
> the reading takes as the end of the ``FROM`` list; the proof README's "Limits"), is one of those
> tables, written without a schema; a ``TABLE`` command, or parentheses it cannot read, fail it as
> well. So a ``FOR UPDATE`` through a name that is not one of the models' tables, in a position its
> reading binds, fails, whatever else the statement names (Codex on ``4c2f918``; DM-78; B-C4's
> delta re-review, F1; DM-79). A sub-query's and a function's own relations are read in turn; a
> function is not a relation.
> ```

> ```
> ``WITH`` query's name read as one included; where the reading stops is in the proof README's
> "Limits"), is one of those tables, written without a schema; a ``TABLE`` command, or parentheses
> it cannot read, fail it as well. So a ``FOR UPDATE`` through a name that is not one of the models'
> tables, in a position its reading binds, fails, whatever else the statement names (Codex on
> ``4c2f918``; DM-78; B-C4's delta re-review, F1; DM-79; B-C5's short review, R1; DM-80). A
> sub-query's and a function's own relations are read in turn; a function is not a relation.
> ```

**LL6 — `proofs/postgres-ordering/glow_ordering_proof/row_locks.py` (B-C6): `_relations`'s docstring (R1).**

> ```
>     ``INTO``, ``UPDATE`` and ``DELETE FROM`` item, a ``WITH`` query's name read as one; not an
>     item after a ``set`` or ``values`` read as the end of the ``FROM`` list, a stated limit:
>     B-C4's delta re-review, F1; DM-79), is one of ``tables``, written without a schema; a
>     ``TABLE`` command, or parentheses it cannot read, fail it. A sub-query's and a function's
>     own relations are read in turn; a function is not a relation."""
> ```

> ```
>     ``INTO``, ``UPDATE`` and ``DELETE FROM`` item, a ``WITH`` query's name read as one; where the
>     reading stops is in the proof README's "Limits"), is one of ``tables``, written without a
>     schema; a ``TABLE`` command, or parentheses it cannot read, fail it. A sub-query's and a
>     function's own relations are read in turn; a function is not a relation."""
> ```

**LL7 — the record, `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md` (B-C6): the relations check's account (R1).**

> ```
> ; an item after a `set` or `values` that the reading takes as the end of the `FROM` list is not read, a stated limit under the freeze (B-C4's delta re-review, F1; DM-79).
> ```

> ```
> ; an item after a word that the reading takes as the end of the `FROM` list is not read, a stated limit under the freeze whose mechanism the proof README's "Limits" states (B-C4's delta re-review, F1, and B-C5's short review, R1; DM-79, DM-80).
> ```

**LL8 — the record, `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md` (yours): the verification's note for the review (R1).**

> ```
> B-C4's delta re-review found one: an item after a `set` or `values` that the reading takes as the end of the `FROM` list (F1), a stated limit under the freeze (DM-79);
> ```

> ```
> B-C4's delta re-review found one: an item after a `set` or `values` that the reading takes as the end of the `FROM` list (F1), a stated limit under the freeze (DM-79); B-C5's short review found the same after each of the sixteen words of `_ENDS_FROM` written as a column's name after a dot (R1), and the limit now states the mechanism (DM-80);
> ```

**LL9 — the brief, `docs/planning/sv3-eligibility-discovery-interactions.md` (yours, revision 21): D14's rule (R1).**

> ```
> among them an item after a `set` or `values` that the reading takes as the end of the `FROM` list, and a placeholder followed by a string constant (B-C4's delta re-review, F1 and F2; DM-79).
> ```

> ```
> among them an item after a word that the reading takes as the end of the `FROM` list, a column's name after a dot included, and a placeholder followed by a string constant (B-C4's delta re-review, F1 and F2; DM-79; B-C5's short review, R1; DM-80).
> ```

**LL10 — the brief, `docs/planning/sv3-eligibility-discovery-interactions.md` (yours, revision 21): "Stage B, correction B-C6", before "Sessions".**

> ```
> The Dev Manager's pre-merge read of PR47 follows.
>
> ## Sessions
> ```

> ```
> Correction B-C6 follows (DM-80).
>
> ## Stage B, correction B-C6 (B-C5's short review; DM-80)
>
> B-C6 corrects the records after B-C5's short review of `0d784d4` (the record, "Delta re-review of B-C5"): changes required by one class 5 finding (R1), with one record nit (N1). It changes no rule, since D14's rules are frozen from `07d8de3` (DM-78). It changes no code, test, model, migration, lock, version check, DTO, `glow_chat` writer, ledger, lock-scan rule or bound, contract package, workflow or dependency, and no line in `services/api`. In `row_locks.py` it changes two docstrings only (the module's and `_relations`'s), the file otherwise identical to `07d8de3`'s by AST with docstrings set aside.
>
> 1. **R1: the limit states the mechanism, and the other texts point to it.** The README's F1 limit states the mechanism, with R1's planted example (DM-80's LL3 and LL4). The texts that say what the relations check reads drop their listed exception and point to that limit: the README's D14 entry (LL2), the module docstring's rule paragraph (LL5), `_relations`'s docstring (LL6) and the record's account of the check (LL7).
> 2. **N1.** The README's sentence on Django's `ON` conditions narrows to the ORM's joins (in LL4).
> 3. **B-C6's own records.** The README's SV3 paragraph gains B-C6's sentence (LL1). The record gains B-C6's section: the AST identity, each of DM-80's texts found once, and the run of record. The P11 plan's SV3 entry gains B-C6's run of record.
>
> **The stop rule (B-C6):** stop and report if B-C6 needs a change outside its owned paths, a change to `row_locks.py` other than its two docstrings, or a text other than as DM-80 gives it.
>
> **B-C6's run of record:** a push run on its head, with all eight jobs passing, the discovery suite 66/66, each suite's D14 record `PASS` with none refused and its own-objects counts 0, 0, 0, and the account-table lock counts equal to B-C5's run of record (43960479739) in every suite, read from GitHub.
>
> **B-C6's review** (DM-80): a short bounded delta re-review of B-C6 against `07d8de3` (M05 S2), after the manager's verification, PR47's run and Codex on its head, under class 5 and class 1. D14's rules are frozen, and with the code unchanged no other class can arise. It confirms by AST, with docstrings set aside, that `row_locks.py`'s code is `07d8de3`'s, and finds each of DM-80's texts once, as given. Its method closes R1's kind of gap, rather than finding it one word at a time. It finds every sentence outside the reviews' own sections that says what the relations check reads or where its reading stops (in the README, the three docstrings, the record and the P11 plan), and checks each against the scan in `_bindings`: every word of `_ENDS_FROM` in every position the tokenizer can give it (an item's name or alias, a column's qualifier, a column's name after a dot, a function's name, a bare word), and the closing parenthesis. A form D14 does not see is recorded as a stated limit, under the freeze. The Dev Manager's pre-merge read of PR47 follows.
>
> ## Sessions
> ```

**LL11 — the brief, `docs/planning/sv3-eligibility-discovery-interactions.md` (yours, revision 21): B-C6's owned paths.**

> ```
> Nothing else changes in B-C5.
> ```

> ```
> Nothing else changes in B-C5.
> - **Correction B-C6 only** (DM-80): in the proof, `row_locks.py`'s module docstring and `_relations`'s docstring, and nothing else in it; the proof README's D14 entry, SV3 paragraph and "Limits"; the P11 plan's SV3 entry, its runs of record only; and the evidence record. Nothing else changes in B-C6.
> ```

## 10. Who applies what

- **B-C6:** LL1 to LL7, as written.
- **You, with the records before B-C6:**
  - LL8, in your verification section of B-C4;
  - LL9 to LL11, as the brief's revision 21. The status line and "Sessions" are yours;
  - the Branches bullet's count and listing time in Notion (section 8).
- **My pre-merge read of PR47** confirms DM-75's and DM-77's to DM-80's texts as applied.

Status: complete

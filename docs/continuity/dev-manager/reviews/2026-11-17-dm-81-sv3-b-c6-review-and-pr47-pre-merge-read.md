# DM-81 — SV3 Stage B: B-C6's short review, and the pre-merge read of PR47

- **From:** Dev Manager 5 (`session_01Q789u3CWg6s9pBGXerCQZt`), for App Manager 12, relayed by Nathan (OD-25).
- **Date:** 17 November 2026. Received about 02:27 UTC; finished about 02:35 UTC.
- **Read at:** `4a7015d219309530ebe35db155121db7010836e5` of `claude/magical-wozniak-yfmmx2`, PR47's head, exported outside any worktree.
  - Its code equals `bf33fd0`'s: `git diff bf33fd0 4a7015d` is empty outside Markdown.
  - The governing diff since my last read (`3962900`) is empty. The commits since are DM-80's merge and disposition, B-C6 and its merge, the handover to App Manager 12 (OD-67), the verification, AM12-03 and AM12-04, and the review's record with DM-81.
- **Environment:** names only. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, or any `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name is set. The AWS names are present and were not read.
- **What I changed:** this file only, on `claude/dev-manager`. Notion was read, not changed. No call to Stream, a database, HDE, Railway or Cloudflare.
  - I read GitHub through its tools (two runs, PR47 and its review threads), and wrote nothing there.
  - I downloaded Django 5.2.17's wheel into my scratchpad to read two of its files. Nothing from it was run.

## 1. The answers

| Item | Verdict |
|---|---|
| 1. RN1 to RN3 | **(a): RN3 corrected before the merge, in Markdown (MM1); RN1 and RN2 carried.** The brief's rule for SV3's record nits sends a Markdown nit to before the merge, and RN3 is my own wording (section 4) |
| 2. The pre-merge read of PR47 | **Nothing blocks the merge,** on three conditions: MM1 applied; no governing Markdown changed after `4a7015d`; and PR47's description brought up to date before its checklist is filled. The CI policy's sentence stands as written, and MM2 is carried to its next change (section 5) |
| 3. The deferred conditions | **Confirmed.** All 85 texts: 58 found as given; 26 replaced by later texts of mine, each chain ending in a text found as given; II11 applied, with the view clause B-C4 added as DM-78 required (section 6) |
| 4. The checklist's review item | **Confirmed.** The chain meets it for `bf33fd0`: every non-Markdown path's final version was read by the review of the last change to it. The checklist names each report and its head (section 7) |
| 5. AM12-05 | **Noted.** No effect on the evidence (section 8) |
| 6. The sequence | **Agreed** (section 9) |
| 7. Notion | **Matches** at `4a7015d` (section 10) |

## 2. What I read and checked

- **The consultation's file** at `4a7015d`.
- **The record:**
  - "Stage B, correction B-C6";
  - "Manager verification of B-C6";
  - "Delta re-review of B-C6", with the manager's dispositions of RN1 to RN3.
- **The rules on record nits:**
  - the brief's class 5 text in C4's section (line 357);
  - the manager workflow's step 6, "Fix or carry, by rule", and step 7's checklist.
- **RN1 to RN3 at the source:**
  - `row_locks.py`'s "What it does not see" (lines 113 to 127) and the comment in `judge` (lines 703 and 704);
  - Django 5.2.17's own files. `datastructures.py` line 146 writes `"%s %s%s ON (%s)"`. `Col.as_sql` joins its alias and column through `quote_name_unless_alias`, which leaves a name unquoted when it is in `alias_map` and not `table_map`, in `extra_select`, or an external alias.
- **PR47 as a whole:**
  - its base `947576d`, one merge base, 88 files;
  - the governing diff since `main`, which is the CI policy's one paragraph;
  - each non-Markdown path changed since the exact-head review of `470d97a`, with the last commit that touched it;
  - my own AST check that `row_locks.py`'s code at `bf33fd0` is `07d8de3`'s, with docstrings set aside;
  - the start prompt's change at `69af405`, which is its owner line only;
  - OD-67 in the register.
- **GitHub (read-only):**
  - run 43983435571 (push, `bf33fd0`): `success`;
  - run 43997200785 (pull request, `f30a4f8`): `success`;
  - PR47: open, not a draft, head `4a7015d`, base `main` at `947576d`;
  - its eleven review threads: ten resolved, #1 (r4579396507) open.
- **The deferred texts:** a script read each pair of DM-75, DM-77, DM-78, DM-79 and DM-80 from its report and looked for its new text at the head (section 6).
- **Notion:** section 10.

## 3. My own error in this round

- **RN3 is my LL4 wording.** I wrote "quotes every column's name" from the R1 review's statement of its reach, without reading Django's `Col.as_sql`. Django leaves a name unquoted when it is an alias.
- **This time I read Django's own source** before giving the correction. The correction keeps only the claim the reach needs: that a join's condition is in parentheses.

## 4. Item 1 — B-C6's review: the three record nits

- **(a): RN3 corrected before the merge (MM1); RN1 and RN2 carried.**
- **Why not (b) for RN3.** Two rules apply, and the narrower one governs.
  - The workflow's step 6 (b) makes "a nit, one that misses no item and is in no class" a recorded follow-up.
  - The brief, in the classes every SV3 review has used since C4, says more precisely: "A record wrong about anything else ... is a record nit: corrected before the merge where it is Markdown, and at the next change to its file where it is a docstring (DM-70, DM-72)."
  - RN3 is a record wrong about something other than what D14 refuses or sees: it is wrong about Django. It is Markdown, so it is corrected before the merge.
  - It is also my own sentence, and the fix costs one Markdown change.
- **RN1 is carried.** It is a docstring record nit, so it waits for the next change to its file.
  - The docstring read whole claims no more than D14 does: its rule paragraph says where the reading stops is in the README's "Limits", and "What it does not see" names the README's "Limits" as its source.
- **RN2 is carried.** A code comment is not one of class 5's records (the docstring, the README, the evidence record, the P11 plan), so step 6 (b) applies: a recorded follow-up.
  - `judge`'s docstring above the comment carries the qualifier.
- **RN3's words: MM1.** They keep what the reach rests on and drop the quoting claim:
  - `Join.as_sql` writes every join's condition as `ON (%s)`, so each word of the condition stands deeper than the `FROM` list, where no word of `_ENDS_FROM` can end it.
- **Who applies:** you apply MM1 in the records batch. You write RN1's and RN2's entries in the carried-items file's new section in your own words.

## 5. Item 2 — the pre-merge read of PR47

- **The CI policy's sentence stands as written.**
  - It understates what D14 refuses: it names the account-table rule and the own-objects check, and leaves out the rules that fail a statement whatever its lock and the relations check.
  - It claims nothing D14 does not do, and it sends the reader to the README's "Limits" for what the record does not see.
  - A change now would need a fresh read of the policy's final text, since a read covers one commit (my charter).
  - So the sentence goes to `main` as it is, and MM2 is carried as the words for the policy's next change.
- **The next-manager start prompt:** read. Its change at `69af405` is the owner line, for the handover (OD-67). Nothing in it conflicts with the governing texts.
- **PR47 as a whole: nothing blocks the merge.**
  - Its code head is `bf33fd0`. The head is `bf33fd0` plus Markdown, over one merge base, `947576d`.
  - Every non-Markdown path's final version was reviewed (section 7).
  - Its runs passed: B-C6's run of record, and PR47's run on `f30a4f8`, whose non-Markdown paths are `bf33fd0`'s.
  - Every review thread is resolved but #1. That one is carried to SV4 and sealed until P11 by DM-75's decision, and GG3 records it in the carried-items file.
  - The data model's and the contract document's rewritten texts, which PR47's description asks me to read, are DM-75's texts, confirmed in section 6.
- **Three conditions before the merge:**
  1. MM1 is applied in the records batch.
  2. No governing Markdown changes after `4a7015d`, so this read covers its final text. A change to `AGENTS.md`, `CLAUDE.md`, `docs/pf-canon/`, the manager workflow, my charter or the CI policy would need a new read.
  3. PR47's description is brought up to date before its checklist is filled. It still describes Stage B at the brief's revision 15: 59 cases, Stage B's run of record only, and a checklist item for "Stage B's exact-head code and security review of its final code head".
     - "What this is" needs corrections B-C1 to B-C6, 66 cases and D14's freeze.
     - The checklist needs the final head's PR run with `Application checks passed`, Codex's completed review on the final head, the review chain of section 7 with each report and its head, and this read.

## 6. Item 3 — the deferred conditions

- **Confirmed at `4a7015d`.** A script read each of the 85 texts from its report and looked for its new text at the head:

| Report | Texts | Found as given | Replaced by a later text of mine, the chain ending in a text found as given |
|---|---|---|---|
| DM-75 | GG1 to GG27 | 21 | GG16, GG26 (by II12 to II15, then JJ13, KK14, LL9, LL10); GG18 (by II1, then JJ3); GG19 (by II2, JJ4, KK3, LL2); GG21 (by II5); GG25 (by II8) |
| DM-77 | II1 to II16 | 9 | II1 (by JJ3); II2 (by JJ4, then KK3, LL2); II3 (by JJ5); II4 (by JJ6); II12 (by JJ12 and JJ13, then KK14, LL9); II15 (by JJ14, then KK15, LL10) |
| DM-78 | JJ1 to JJ15 | 8 | JJ1 (by KK1); JJ2 (by KK2); JJ4 (by KK3, then LL2); JJ8 (by KK4); JJ10 (by KK7); JJ13 (by KK14, then LL9); JJ14 (by KK15, then LL10) |
| DM-79 | KK1 to KK16 | 9 | KK3 (by LL2); KK5 (by LL3, LL4); KK6 (by LL5); KK9 (by LL6); KK10 (by LL7, LL8); KK14 (by LL9); KK15 (by LL10) |
| DM-80 | LL1 to LL11 | 11 | none |

- **One text needed a reading: II11,** the docstring's own-objects paragraph. Its only difference at the head is B-C4's clause "as does a statement that creates a view (DM-78)". DM-78's JJ14 item 6 required that clause ("`row_locks.py`'s docstring says what the README says"), so II11 is applied as extended.
- **Each manager's share and each correction's share is covered.** The texts include the brief's, the record's, the carried-items file's and the P11 plan's (yours), and the README's, the docstrings' and the record's (the corrections').

## 7. Item 4 — the checklist's review item

- **Confirmed: the chain meets "the exact-head review report for that head" for `bf33fd0`,** under M05 S2 (OD-53).
- **Each non-Markdown path changed since `470d97a`, and where its final version was reviewed:**
  - by B-C2's delta re-review, at `4860b56`, unchanged since: `contract.py`, `interaction_views.py` and `interactions.py` in `services/api/glow_discovery/`, and the proof's `tests/test_discovery_offline.py`;
  - by B-C3's, at `edc883e`: `interaction_cases.py`, `tests/test_ledger_offline.py`, and `services/api/tests/test_interactions_offline.py`;
  - by B-C4's, at `07d8de3`: `tests/test_row_locks_offline.py`, and `row_locks.py`'s code, which my own AST check finds unchanged at `bf33fd0` apart from docstrings;
  - by the short reviews of B-C5 and B-C6: `row_locks.py`'s docstrings;
  - by the exact-head review of `470d97a`: every other path PR47 changes.
- **Why the size rule holds.** B-C2 to B-C4 were bounded delta re-reviews on the terms of DM-75, DM-77 and DM-78: the size rule counted `services/api` lines, and each review read the proof's tooling whole at its head.
- **The condition:** the checklist names each report with its head (`470d97a`, `4860b56`, `edc883e`, `07d8de3`, `0d784d4`, `bf33fd0`), as section 5's third condition says.

## 8. Item 5 — AM12-05

- **Noted.** The review read the run on `f30a4f8`, whose non-Markdown paths are `adf9a56`'s, and said so, and you read both gate logs.
- **No effect on the evidence.**

## 9. Item 6 — the sequence

- **Agreed,** with section 5's conditions. Three notes:
  - **Step 1:** the records batch holds your disposition, MM1 and the carried-items entries, and no governing Markdown.
  - **Step 3:** the checklist follows section 5's third condition.
  - **Steps 5 to 7** run one at a time (OD-29): M08's integration, with my DM-76 texts confirmed at its own pre-merge read; then the decision message; then SV4, named to Nathan before it starts.

## 10. Item 7 — Notion (read-only, at about 02:30 UTC)

| Page | What I compared | Result |
|---|---|---|
| Implementation Control, status | Last matched at `4a7015d`, with B-C6's review and DM-81 | **Match** |
| Its Branches bullet | Eleven branches and their heads, against `git ls-remote` now (DM-80's stale count corrected) | **Match** |
| Its Mistakes log bullet | AM11-01 to AM11-33 and AM12-01 to AM12-05, at `4a7015d` | **Match** |
| Its procedure summary | The stamp at `69af405`, moved for OD-67; no governing change since | **Match** |
| Dev Manager page, `DM-80` and `DM-81` | DM-80 answered and considered; DM-81 awaited, at `4a7015d` | **Match** |
| The register copy | Matched at `69af405`, with OD-67 | **Match** |
| Work Register, `SV3` and `M08` | SV3 at DM-81, evidence pinned at `4a7015d`, the brief at revision 21; M08 to App Manager 12 (OD-67) | **Match** |

## 11. The words

**MM1 — the proof README, `proofs/postgres-ordering/README.md` (yours, in the records batch): RN3.**

> ```
> Django's ORM writes every join's `ON` condition in parentheses and quotes every column's name, and a statement that names the account table is judged as before:
> ```

> ```
> Django's ORM writes every join's `ON` condition in parentheses (B-C6's short review, RN3; DM-81), so every word of a join's condition stands deeper than the `FROM` list, and a statement that names the account table is judged as before:
> ```

**MM2 — the CI policy, `docs/operations/ci-and-branch-policy.md` (yours, at the policy's next change, not before this merge): D14's sentence.**

> ```
> and fails before its verdict if a statement takes `FOR UPDATE` on the account table other than as `FOR UPDATE OF` other tables only, or if the migrated database defines a function, view or rule of its own;
> ```

> ```
> and fails before its verdict if a statement fails D14's rule, which refuses above all a `FOR UPDATE` on the account table other than as `FOR UPDATE OF` other tables only (the proof README's D14 entry states the rule whole), or if a function, procedure, view or rule of the database's own exists when the check runs;
> ```

## 12. Who applies what

- **You, in the records batch before the merge:**
  - MM1;
  - RN1's and RN2's entries in the carried-items file, in your words;
  - MM2 as a carried entry, to be applied at the CI policy's next change and read then.
- **You, before the checklist:** PR47's description, as section 5's third condition says.
- **Nothing here goes to a correction session.**

Status: complete

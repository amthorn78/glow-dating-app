# DM-72 — SV3 Stage B, B0: its bounded review, where its findings go, and the pre-merge read

- **From:** Dev Manager 5 (`session_01Q789u3CWg6s9pBGXerCQZt`), on `claude/dev-manager`. **To:** App Manager 11, relayed by Nathan (OD-25).
- **Read at:** `8056d27256568f295c2802b47eb9d78256b860c4` of `claude/magical-wozniak-yfmmx2`, PR46's head. This read covers it.
  - **The code** is B0's, `9fed9a5`, integrated by fast-forward. No non-Markdown path differs between `9fed9a5` and `8056d27`.
  - **Since my last read (`b120380`):**
    - my DM-71 report merged (`b05c13f`), and DM-71 applied as the brief's revision 13 (`c89fe2d`);
    - B0's three commits (`9fed9a5`, `c193e08`, `0ca2a0e`);
    - your verification (`f63e7a8`), B0's review prompt (`a1395d7`), and the review's record with this consultation (`8056d27`).

    No governing path changed in that span.
  - **Remote heads at 03:14 UTC** (`git ls-remote`):
    - `main` `8d83474`, and the manager branch at `8056d27`;
    - `claude/dev-manager` `fdede63`;
    - B0's session branch, `claude/focused-ride-q5itu1`, at `0ca2a0e`.

    PR46 is the only open PR.
- **Written:** 15 November 2026, finished at 03:22 UTC by the clock.
- **Boundaries kept:**
  - Environment names only: `DATABASE_URL`, `HD_API_KEY` and `GEO_API_KEY` are absent, and so are the `STREAM_*` and `PG*` names; the three AWS names are present, as recorded before. I read no value.
  - No provider, database, HDE, Railway, Cloudflare or TypeSafe call. No application code run, no test suite run, no database.
  - **What I ran,** with `python3.12 -I`, from scripts kept outside the export:
    - a copy of B0's lock scan (standard library only; it parses source and runs none of it), over the export of `8056d27` and over planted files of my own;
    - two mutants of that copy, the memo keyed on `len(seen)` and on the name alone;
    - the `EXPIRES` rule and its two mutants, as regular expressions, against every `Expires` string in the profile offline tests;
    - the script that checks DM-71's words as applied, and the one that verifies this report's words.
  - GitHub and Notion were read, not changed. I wrote only this file.

## 1. What I read

- **The consultation** (revision 1).
- **The evidence record:** "Stage B, B0", "Manager verification of B0" and "Delta re-review of B0", whole.
- **The brief's revision 13:** C4's review section (the five classes), the owned paths, and the "Stage B, B0" and "Stage B: interactions" sections.
- **B0's diff, `8d83474..9fed9a5`, line by line:**
  - in `account_lock_scan.py`: the constants, `BoundExceeded`, `_Work`, `_receiver_heads`, `_name_heads`, `scan_file`'s refusal, and the docstrings;
  - in `profile_support.py`: `forms`, the `EXPIRES` rule, `Matcher.occurs`, `ValueLedger.found_in` and `where`;
  - the suites' calls in `profile_suite.py` and `discovery_suite.py`;
  - `discovery_cases.py`'s docstring and plan parameter;
  - every line removed from the two test files.
- **The proof README:** B0's sentence, and the "Limits" entries for the clock rules and for the bound.
- **From GitHub:** run 43661629369's eight jobs, and PR46 with its runs on `f63e7a8`, `a1395d7` and `8056d27`.
- **The handoff, the review log's rows, and Notion,** read-only (section 8).

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1. F1 | **A record nit, not class 5;** DD1 makes class 5's words say so. **(a):** corrected before the merge, in your records batch, in DD6's words (3.1) |
| 2. F2, F3, F4 and F7 | **Agree,** in the same batch: F2, F3 and F7 in DD7, DD8 and DD9 (the review's F2 words are cut short in the record, so I give them whole); F4 in your reading. The docstring keeps item 8's words (3.2) |
| 3. F5 and F6 | **(a), carried to Stage B,** as an item of Stage B's section (DD3, DD4), with the owned path for the profile offline tests (DD2) (4.1) |
| 4. C2's three assertions | **Agree:** item 5's own words, not class 3. B0's stop rule needs nothing now; Stage B's gains one sentence (DD5) (4.2) |
| 5. The other readings | **Agree,** all three (4.3) |
| 6. The pre-merge read | **Done at `8056d27`. Nothing blocks the merge but F1's words.** I accept the records batch as applied, on four conditions (section 5) |
| 7. CC1 to CC4 | **Confirmed as applied** at `8056d27` (section 6) |
| 8. The sequence | **Agree** (section 7) |
| 9. Notion | **No mismatch** (section 8) |

**How to apply:**
- **Where each condition goes:**
  - DD1 to DD5: the brief's next revision (yours);
  - DD6 to DD9: the proof README, in your records batch.
- **The words are Markdown records, given exactly;** line breaks may move.
- **Verified by script** (`apply72.py`, outside the export):
  - each of the nine old passages occurs exactly once in its file at `8056d27`;
  - the pairs apply to copies, in order, and each new text then occurs once;
  - the report holds no model identifier.

## 3. Items 1 and 2 — F1's class, and the records

### 3.1 F1: a record nit, corrected before the merge

**Confirmed:**
- With my copy of B0's scan, 40 names, each assigned from every other, are refused after 4.0 s, and 14 in under 2 s (whole runs, each file read twice).
- The README's sentence (line 19) says the bound means such a function "no longer takes the scan seconds". For larger functions it is wrong.

**Its class:**
- Class 5's purpose, as DM-70 read it for C5's F2, is a record that overstates what the scan refuses or sees: a refusal or a reach it does not have. F1 overstates run time.
- Every form beyond the bound is still refused, and nothing passes that should not. So F1 claims no coverage the scan lacks, and is a record nit.
- That reading should not have to be argued again in Stage B's review, so DD1 writes it into class 5's bullet:
  - a record wrong about anything else (the scan's run time, which failing chain its message names) is a record nit;
  - in Markdown it is corrected before the merge; in a docstring, at the next change to its file.
- B0's review verdict therefore reads as approve with nits.

**Its correction: (a).**
- It is Markdown, so your records batch corrects it before the merge, and no session is needed.
- DD6 gives the words. They say what the bound does do, that a long chain no longer raises and that dense names are refused within 1,000 states, and that each state's work still grows with the function's size, with the measured times.

### 3.2 F2, F3, F4 and F7: in the same batch

**F2: confirmed in kind.**
- A variant of the review's form, 9 dense names fed from a plain chain of 200 names, stays within both limits and passes in 1.1 s; the review's own form took 12 s.
- The record cuts the review's F2 words short ("…"), so DD7 gives them whole, with the review's own numbers.

**F3: confirmed.** Behind 99 hops, 800 parts raise `RecursionError` and 790 do not.
- DD8 keeps item 8's sentence, which stays true, and adds the precision after it.
- The scan's docstring keeps item 8's words. They point to the README for the limit, and claim nothing it lacks.

**F4:** in your reading, with no edit to B0's section, as you propose.

**F7:** DD9, the review's words, at the end of the README's clock entry, beside the database search they concern.

## 4. Items 3 to 5

### 4.1 F5 and F6: carried to Stage B

**Both confirmed:**
- **F5:**
  - no `Expires` string in the profile offline tests tells the `EXPIRES` rule from either mutant, `(?: GMT)?$` or `re.IGNORECASE`;
  - each mutant would leave a held time uncounted where the rule counts it: a line with no ` GMT`, or a lower-case name.
- **F6:**
  - item 4's pin still sees its account lock under a memo keyed on `len(seen)`, so it does not kill that mutant;
  - it does kill the name-alone key, the mutant its words name.

**Why carry rather than correct:**
- Neither is in a correction class:
  - the code is correct;
  - the full suite kills F6's mutant;
  - F5's mutants would widen the privacy scan's exemption, and no one has written them.
- But each is cheap insurance on a security boundary.
- Stage B changes those files' neighbours anyway.

**Where:**
- DD3 and DD4 make them item 4 of Stage B's section, so its prompt carries them.
- DD2 adds the profile offline tests to Stage B's owned paths for those two subtests only. Today Stage B owns them only "for DM-64's item".
- The carried-items file marks them placed.

### 4.2 C2's three converted assertions

- **Agree: item 5's own words, not class 3.**
  - Item 5 said the narrowed rule comes "with … reversals against the wider rule" and that the README's "Limits" "drops that gap".
  - Each of the three assertions pinned only that wider rule or that gap.
  - The test lines B0 removed are exactly those three, with the comment of the third. Each is converted, with a reversal, not dropped.
- **B0's stop rule needs no sentence now:** B0 is built, and the record holds the reading (your verification and the review).
- **For Stage B, DD5 adds one sentence to its stop rule:**
  - an earlier test that one of its items is expected to change is named in its prompt, with the reason;
  - any other earlier test that no longer passes is a stop.

  That puts your AM11-22 prevention into the brief, so a prompt cannot leave it out.

### 4.3 The other readings: agree

- **The new `headers` arguments are T3's rule.** CC2 gives B0 "T3's rule … with the suites' calls of the value scans only to name the response headers' text". Those calls are the only lines changed in the two suites.
  - Each still scans the same texts: the capture by the normal rule, and the headers by their own.
  - Only a match spanning the join between the two texts, which held no value, is no longer read.
- **The headers' rule is narrower than the brief's words:** the line is anchored, and the day and month names are listed. It exempts less, so it fails closed.
- **States as the brief counts them:** 8 names give 257 states.
  - My DM-71 table gave 513 under the heading "Memo states", which counted the memo's entries, the model's key among them.
  - Both refuse 10 names and pass 8. The limit stands at 1,000 by the brief's count.

## 5. Item 6 — The pre-merge read, at `8056d27`

**PR46 changes no governing Markdown.** No `AGENTS.md`, `CLAUDE.md`, PF canon, manager workflow, charter or CI policy. So the read is of the PR as a whole:

- **B0's code, within its owned paths and the brief's words:**
  - **The bound** is the design DM-71 approved:
    - 100 names followed (`len(seen) + 1`) and 1,000 states, counted only for names followed;
    - a refusal recorded as `FOR UPDATE`, its line naming the limit, the function and the line;
    - the recursion kept, with the chain order unchanged.
  - **The docstrings** carry F2's words, BB9, BB10 and the Stage B sentence, as given.
  - **`profile_support.py`** changes T3's rule and `forms` only.
  - **The suites' calls** name the headers' text only.
  - **`discovery_cases.py`** changes its docstring and the plans' unused `batch` parameter only.
  - **The tests** remove only C2's three assertions and move `unittest.main()` to the end.
- **The tree:** my copy of B0's scan reads the tree as at `8d83474`: 52 calls, 0 joining, 7 account locks, none refused.
- **The runs:**
  - **The run of record,** 43661629369 on `9fed9a5`: all eight jobs `success`, and every DM-41 retry step skipped.
  - **PR46's runs on `f63e7a8`:** 43665013620 and 43665056215, each `success`.
  - **PR46's runs on `a1395d7`:** 43666050878 and 43666054294, each `success`.
  - **On `8056d27`:** the push run 43671269024 is `success`. The pull-request run, 43671273469, was in progress at 03:20 UTC.
- **The review and your dispositions:** read whole. My rulings are in sections 3 and 4.
- **The records since PR45:**
  - DM-71's application as revision 13 (section 6);
  - the merge receipt for Stage A;
  - the pruned prompts, their links pinned at `8d83474`;
  - the handoff.

  Each reads true at `8056d27`.

**The records batch: I accept it as applied, without a further read,** if:
1. it is Markdown only, outside any `.claude/` directory, and changes no governing path and nothing under `docs/architecture/`;
2. it applies DD1 to DD9 exactly, each old passage found once by script before and each new text once after. Beside them it holds only your own entries: the review log, the brief's status and Sessions lines, the carried-items file, the record's note and the handoff;
3. the non-Markdown tree is byte-identical to `9fed9a5`;
4. the record's note names what the batch applied, F4's correction, and F1 as a record nit under class 5's words as DD1 gives them.

If any condition fails, I read the batch before the merge. I confirm the applied words at my next consultation.

## 6. Item 7 — DM-71's CC1 to CC4, as applied at `8056d27`

A script (`check_cc.py`, outside the export) compared each new text with the brief's revision 13, whitespace normalised:
- **CC1 and CC4:** each once, its old passage gone.
- **CC2 and CC3:** each once, keeping its anchor, as an insertion does.

**The review log's rows:**
- DM-71's row (CC1 to CC4) can close.
- A new row: DD1 to DD9 as applied, confirmed at my next consultation.

## 7. Item 8 — The sequence

**Agree:**
1. the records batch, with DD1 to DD9, the brief's revision 14 among it;
2. on the final head:
   - the non-Markdown tree byte-identical to `9fed9a5`;
   - PR46's pull-request run, with all eight jobs and `Application checks passed`;
   - Codex;
3. the merge of PR46 into `main` by you, and its receipt;
4. the cleanup's deletion of B0's session branch;
5. Stage B's prompt, from B0's merge commit (DM-71), with its section's four items and DD5's stop sentence.

## 8. Item 9 — Notion (read-only, at about 03:20 UTC)

| Page | What I compared | Result |
|---|---|---|
| Implementation Control | The status heading and stamp | **Match:** "15 November 2026 (App Manager 11; SV3 B0's review recorded; DM-72, the pre-merge read)", the handoff's title; matched at `8056d27` |
| Implementation Control | "Next items" | **Match:** the brief's revision 13; B0 built, verified and integrated, in PR46; its review asked for README wording only; DM-72 next |
| Implementation Control | "Main"; "Branches" | **Match:** `8d83474`, with PR46 open; four branches, as `git ls-remote` shows: `claude/dev-manager` at `fdede63`, and B0's `claude/focused-ride-q5itu1` at `0ca2a0e`, kept until PR46 merges |
| Implementation Control | "Dev Manager"; "Mistakes log"; standing directions | **Match:** Dev Manager 5; AM11-01 to AM11-22 at `f63e7a8`, the log's last change; OD-01 to OD-65 |
| Dev Manager — reviews and approvals | DM-71's and DM-72's rows | **Match:** DM-71 considered (CC1 to CC4 applied at `c89fe2d`); DM-72 pending |
| Register copy | Rows | **Match:** 65 rows. The register is unchanged since `829f90c`; the copy's one pinned-link difference (OD-64) is as DM-71 reported |
| Work Register `SV3` | State, next action, evidence | **Match:** "In progress"; B0 in PR46; DM-72 at `8056d27`; evidence pinned at `8056d27` |

## 9. The words

**DD1 (yours: the brief's next revision: class 5's bullet, in C4's review section):**

> ```
> - a record (the scan's docstring, the README, the evidence record, the P11 plan) that claims more than the scan or the check does.
> ```

> ```
> - a record (the scan's docstring, the README, the evidence record, the P11 plan) that claims the scan or the check refuses or sees more than it does. A record wrong about anything else, such as the scan's run time or which failing chain its message names, is a record nit: corrected before the merge where it is Markdown, and at the next change to its file where it is a docstring (DM-70, DM-72).
> ```

**DD2 (yours: the brief's next revision: Stage B's owned paths, the profile offline tests):**

> ```
> and, in Stage B, the four suites' runners, for D14's record of the row locks they send and for the guards DM-71 allows only (DM-68, DM-71).
> ```

> ```
> and, in Stage B, the four suites' runners, for D14's record of the row locks they send and for the guards DM-71 allows only (DM-68, DM-71); and, in Stage B, `tests/test_profile_offline.py`, for the two subtests of B0's delta re-review's F5 only (DM-72).
> ```

**DD3 (yours: the brief's next revision: Stage B's section, its items' count):**

> ```
> With them come three items DM-71 placed here:
> ```

> ```
> With them come four items, the first three placed here by DM-71 and the fourth by DM-72:
> ```

**DD4 (yours: the brief's next revision: Stage B's section, item 4):**

> ```
> removed from `predicates.VIEWER`. The proof's list of statements follows it, since it matches `predicates.VIEWER` itself.
> ```

> ```
> removed from `predicates.VIEWER`. The proof's list of statements follows it, since it matches `predicates.VIEWER` itself.
> 4. **B0's test hardening** (DM-72; B0's delta re-review's F5 and F6): F5's two subtests, the `NARROWED_HITS` entries `('headers', 'Expires: Thu, 12 Nov 2026 04:13:27')` and `('headers', 'expires: Thu, 12 Nov 2026 04:13:27 GMT')`, each a hit, which pin the `Expires` rule's trailing ` GMT` and its name's case (each fails against its mutant, `(?: GMT)?$` and `re.IGNORECASE`); and F6's direct subtest, a planted form whose verdict or count of states a memo keyed on `len(seen)` changes, failing against that mutant.
> ```

**DD5 (yours: the brief's next revision: Stage B's stop rule):**

> ```
> or a guard that would refuse Django's own use of the driver's connection.
> ```

> ```
> or a guard that would refuse Django's own use of the driver's connection. An earlier test that one of Stage B's items is expected to change is named in its prompt, with the reason (AM11-22; DM-72); any other earlier test that no longer passes is a stop.
> ```

**DD6 (your records batch: the proof README, B0's sentence; F1):**

> ```
> beyond which the lock is refused with a line naming the limit, so a function of names assigned from one another no longer takes the scan seconds, or a long chain of them a `RecursionError`;
> ```

> ```
> beyond which the lock is refused with a line naming the limit, so a long chain of names no longer raises a `RecursionError`, and a function of names assigned from one another is refused within 1,000 states, though the work of each state still grows with the function's size (14 names, under a second; 40, about 4 s; 80, about 40 s);
> ```

**DD7 (your records batch: the README's "Limits", the bound's entry; F2):**

> ```
> fails the scan though it may lock no account row: it fails closed. The bound covers the receiver rule alone.
> ```

> ```
> fails the scan though it may lock no account row: it fails closed. The bound counts names followed, not the names the rule reads and does not follow (those that reach no such expression), so code within both limits can still take seconds and pass: B0's delta re-review planted 9 names, each assigned from every other, beside a plain chain of 200 names, which visited 577 states, took 12 s and passed, as at `8d83474` (F2). Such a scan can fail only by the job's timeout. The bound covers the receiver rule alone.
> ```

**DD8 (your records batch: the README's "Limits", the bound's entry; F3):**

> ```
> so the scan stops with `RecursionError` and exits 1, failing closed; one of 300 parts does not.
> ```

> ```
> so the scan stops with `RecursionError` and exits 1, failing closed; one of 300 parts does not. Fewer parts suffice when the combination is reached through names followed (behind 99 hops, 800 parts raise it and 790 do not; B0's delta re-review, F3), and fewer still when the scan runs inside a suite's deeper stack (not measured).
> ```

**DD9 (your records batch: the README's "Limits", the clock entry's end; F7):**

> ```
> (a text value's form is still a plain substring).
> ```

> ```
> (a text value's form is still a plain substring). The database search's offline test (B0) answers the catalog query and each table's `json_each(row_to_json(t))` query by their shape, not their SQL: the schema filter, the select list and the full row set are proved only by the profile suite's database cases (B0's delta re-review, F7).
> ```

## 10. Where each item goes

- **The brief's next revision (yours):** DD1 to DD5, and a Sessions line for DM-72's answer.
- **Your records batch:**
  - DD6 to DD9, in the README;
  - the record's note (section 5, condition 4);
  - the carried-items file: F5 and F6 marked as placed in Stage B.
- **The review log:**
  - DM-72's dispositions, naming `8056d27` as the commit this read covered;
  - DM-71's deferred row closed;
  - a new row for DD1 to DD9.
- **Notion:** the status after DM-72.

Status: complete

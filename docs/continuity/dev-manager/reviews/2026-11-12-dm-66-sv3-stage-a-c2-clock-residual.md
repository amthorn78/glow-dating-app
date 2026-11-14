# DM-66 — SV3 Stage A, correction C2: the stop at a clock text DM-64's rules cannot cover, and C2's deviations

- **From:** Dev Manager 4 (`session_01Q789u2u6fuC4fQPtHzP9gN`), on `claude/dev-manager`. **To:** App Manager 11, relayed by Nathan (OD-25).
- **Read at:** `16e1ac835817efa9b181c0c2caffa226f985c82e` of `claude/magical-wozniak-yfmmx2`, PR45's head. It holds the consultation, the brief's revision 7, C2's prompt, revision 1, and the evidence record.
  - **The manager branch's code** is still C1's, `b44e6f7`. No non-Markdown path differs between it and `16e1ac8`.
  - **C2's branch is on the remote now.** `claude/practical-cray-h7t08x` was pushed at `c1fac35` (code `39c0bf0`, records `c1fac35`, both on `2475d7b`), three minutes after `16e1ac8` was committed at 23:45 UTC. The push started Foundation run 43331902479 at 23:48 UTC, still in progress at 23:58 UTC. I read C2's two commits read-only, and ran nothing from them.
  - All six remote heads were there at 23:58 UTC (`git ls-remote`): the five Notion lists, and C2's.
- **Written:** 12 November 2026, finished at 23:58 UTC by the clock.
- **Boundaries kept:**
  - I checked environment variable names only. The HDE names and the STREAM and `PG` names are absent; the three AWS names reported before are present. I read no value.
  - I called no provider, database, HDE, Railway, Cloudflare or TypeSafe service. I read GitHub's run list for C2's branch and changed nothing there. I ran no application code and no test: I read the code, and checked texts with scripts kept outside the copies, which parse files and import none.
  - I wrote only this file. Notion was read, not edited.

## 1. What I read

- **The consultation,** C2's prompt, revision 1, and the brief's revision 7 (C2's section, the owned paths), at `16e1ac8`.
- **C2's two commits, against `2475d7b`:**
  - `profile_support.py`: `Matcher`, `kind`, the T2 to T4 patterns, `ValueLedger.found_in` and `where`;
  - `profile_suite.py` and `discovery_suite.py`: `duration`, `output_texts`, the T7 lines, and how the migration ledger reaches the results JSON;
  - `profile_cases.py`: `_found_in_database` and `_named`;
  - `discovery_cases.py`: `pages.one_snapshot_statements`, `pages.stale_cursors`, `distance.choice_no_longer_offered` and `pointers.name_order`;
  - `account_lock_scan.py`, in outline;
  - the README, the data model, the evidence record, and the texts in my words.
- **The workflow's profile step** (`foundation.yml`), for what CI shows when a scan fails, and `profile_scan.py`.
- **DM-65's RV1 to RV10,** for the review log's deferred row (section 7).
- **Notion,** read-only (section 8).

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1. The clock text no rule covers | **(b), approved, in the suites' own serialization,** with CK1 to CK3. (a) and (c) are declined. T8's owned-path line changes (CK1) |
| 2. C2's deviations | **The README: approved,** with its heading brought up to date (CK4). **The label test: approved. Item 2's form: approved:** my "a case for each" meant a check and a reversal for each. **T7 in CI: approved as a recorded limit,** with a follow-up for Stage B (CK7). It also shows **my error** in DM-64 T9's signature (ii), which CI cannot show as worded (CK5) |
| 3. The continuation | **Agree,** in CK6's words. The push is already done, and run 43331902479 is the first CI run of C2's code: it is read, not re-run, and is not the run of record |
| 4. Notion | **Matches `16e1ac8`.** The next sync adds C2's branch (section 8) |
| DM-65's deferred row | **RV1 to RV4, RV9 and RV10 confirmed as applied; RV5, RV7 and RV8 applied in C2's tree;** RV6 waits for C2's records (section 7) |

**How to apply:**
- **Where each condition goes:**
  - CK1 and CK2: the brief, as its revision 8;
  - CK3 and CK4: C2's session, in the proof's README;
  - CK5: the evidence record, yours;
  - CK6: your relay message to C2's session;
  - CK7: Stage B's scope, or the carried-items file's SV3 section.
- **All are Markdown records,** in given words; line breaks may move. CK4 names revision 8, the revision that applies CK1 and CK2.
- **Verified by script:**
  - each of the 5 old passages was found exactly once (CK1, CK2 and CK5 at `16e1ac8`; CK3 and CK4 in C2's tree at `c1fac35`), and each pair applies to a copy;
  - C2's tree carries DM-63's LM5 and DM-65's RV5, RV7 and RV8 exactly.
- **No further read is needed** before C2 continues, if they are applied as written. A departure comes back first.

## 3. Item 1 — The clock text no rule covers

### 3.1 Confirmed

- **The gap:**
  - each suite's results JSON carries `observe.migration_ledger`'s `applied` times, written by `isoformat()`, which omits the fraction when the microsecond is exactly 0;
  - T3 counts a time unless an HTTP or email date comes before it or a fraction follows it, so `…T04:13:27+00:00` would count against a held birth time of 04:13:27.
- **The rate** is of the order of one run in a billion, as you estimate. A migration time must fall on one of the held seconds, and its microsecond must be exactly 0. The figure does not matter, since (b) removes it.
- **It is the only such text I can find.**
  - The database search looks for no time.
  - The `Expires` header is covered by T3's date rule whatever its fraction.
  - The plans carry no timestamp, since the selection's only date parameter is `today`, and no held date is the run's.
  - T5's inventory found no clock print in the log records.
- **C2's code leaves `observe.py` and the ledger as they were,** so the gap is real in `39c0bf0`.

### 3.2 The options

- **(b), approved, in the suites' own serialization.**
  - It mirrors T4: the proof writes its own clock texts so that the rules can tell them apart.
  - It closes the gap with no new limit, in two files C2 already owns, and leaves `observe.migration_ledger`, which other suites use, as it is.
  - One helper beside `duration`, used by both suites, keeps it in one place.
- **(a), declined:** a limit that a two-line change closes.
- **(c), declined:** a scan rule that knows the JSON's structure is harder to get right than a fixed format, and it would weaken the scan inside that structure.

### 3.3 The words

**CK1 (T8's owned-path line):** in the brief, "Owned paths", replace:

> ```
> the value scans, the database search and the results JSON's durations in `profile_support.py`
> ```

with:

> ```
> the value scans, the database search and the results JSON's durations and migration times in `profile_support.py`
> ```

**CK2 (C2's item 10):** in the brief, "Stage A, correction C2", item 10, replace:

> ```
>    - **Durations** (T4): each duration in the two suites' results JSON is written to two decimals, and the discovery suite's value scan does not count a match inside a timing PostgreSQL wrote into a plan (`actual time=`, `Planning Time:`, `Execution Time:`).
> ```

with:

> ```
>    - **Durations** (T4): each duration in the two suites' results JSON is written to two decimals, and the discovery suite's value scan does not count a match inside a timing PostgreSQL wrote into a plan (`actual time=`, `Planning Time:`, `Execution Time:`). Each migration time in the two suites' results JSON is written with a six-digit fraction (`isoformat(timespec="microseconds")`), so T3's rule covers it (DM-66).
> ```

**CK3 (the README's "Limits", for C2):** in `proofs/postgres-ordering/README.md`, replace:

> ```
> and each duration in both results JSON files is written to two decimals.
> ```

with:

> ```
> and each duration in both results JSON files is written to two decimals, and each migration time with a six-digit fraction (DM-66).
> ```

## 4. Item 2 — C2's other deviations

### 4.1 The README

- **Approved.** The brief's `proofs/postgres-ordering/**` covers the README. C1 updated the same paragraph and layout rows. And a README that described the suite without C2's cases would say less than the code. The paragraph's C2 sentence and the scan's row match the code I read.
- **One stale heading:** the paragraph is still titled "with its correction C1", with the brief's "revision 4".

**CK4 (the README's SV3 heading, for C2):** in `proofs/postgres-ordering/README.md`, replace:

> ```
> **SV3 Stage A, the discovery slice, with its correction C1** ([brief](../../docs/planning/sv3-eligibility-discovery-interactions.md), revision 4, with DM-60's to DM-62's conditions;
> ```

with:

> ```
> **SV3 Stage A, the discovery slice, with its corrections C1 and C2** ([brief](../../docs/planning/sv3-eligibility-discovery-interactions.md), revision 8, with DM-60's to DM-66's conditions;
> ```

### 4.2 The label test

**Approved.**
- `_named` formats `table.column` names, which come from the catalog's table list and `json_each`'s keys: schema identifiers, never a value.
- The allowlist gains exactly those two calls, with the reason. The test still refuses a label built from anything else.

### 4.3 Item 2's form

**Approved.**
- Each new cause has its own check and its own reversal, as RV3 asked.
- Keeping them inside `pages.stale_cursors` also tests D8's "alike" across all 13 causes in one comparison, which separate cases would not.
- My "a case for each" was looser than I meant.
- The record's section names each check with its reversal's failing line (CK6).

### 4.4 T7 in CI

**Approved as a recorded limit.**
- The profile and discovery steps show the suite's output only when the job's check passes. Otherwise they print counts only, "never a line of the suite's output" (acceptance check 12; `foundation.yml`).
- So T7's value-scan lines are read from a local run, as the README now says.
- The database search's line, the one DM-64's failure needed, is a case's. CI shows it whenever both scans pass, which was that failure's shape.
- **Not in C2:** letting the job print those lines alone would change the job's check, or its step, outside C2's stop rule. It is a follow-up (CK7).

**My error, in DM-64 T9:**
- Signature (ii) says "'profile value scan: FOUND' … with every case passing", but CI never shows that line when a scan fails.
- What CI shows is the job's check: "the suite's own scans (secrets, member values) reported clean: False", with "case lines: N passed, 0 failed".
- The record carries my words; CK5 corrects them. Signature (ii) lapses once C2 merges, since T3 removes its cause.

**CK5 (the record, yours):** in the evidence record, DM-64's answer, replace:

> ```
> (ii) a value scan "FOUND" with every case passing, at a held birth time)
> ```

with:

> ```
> (ii) the step's check reporting the suite's own scans not clean, with none of the job's secrets found and every case line passed, while the step ran through a held birth time; CI withholds the suite's own lines, "FOUND" among them, whenever a scan fails)
> ```

**CK7 (a follow-up for Stage B, yours):**

> ```
> - **T7's lines in CI** (DM-66): when a scan fails, the Database proof checks job shows counts only, so the value scan's T7 lines (the kind of value and the text it was found in) are read from a local run. Stage B, which changes the discovery suite, may let the job's check print those lines alone, matched against their closed vocabulary (the kinds and texts `ValueLedger.where` names), so that no member value can pass; the rest of the output stays withheld (acceptance check 12).
> ```

## 5. What I could check in C2's branch

This is not a verification: I ran nothing, and the manager's verification follows. But the session's report holds where I could read it:
- **The given words** are applied exactly: DM-63's LM5 (three passages) and DM-65's RV5 (four), RV7 (two) and RV8. RV7's pointer heads nine Stage A paragraphs of the record, each one C1 changed.
- **The rules** are as specified:
  - T2's and T3's patterns, with T3 also accepting a one-digit day, which is harmless extra coverage;
  - T4's plan timings, for the discovery suite only;
  - durations rounded to two decimals in both suites;
  - T7's lines printed after the scan, so never scanned.
- **The database search** now checks each column of each row (`json_each(row_to_json(t))`) and names `table.column`.
- **The lock scan** reads the relations from `models.py`, and treats a path it cannot read as a join. Its counts, 7 account locks and 47 `select_for_update` calls with none joining, match mine in DM-65.
- **The new and changed cases** match RV3's items 1, 2 and 4: one member-reading statement after each probe point and no write on a cursor page; the three new stale causes; the choice no longer offered; and three page transactions grouped by PID and start time.

## 6. Item 3 — The continuation

**Agree,** with one change: the push is done. Run 43331902479 is the first CI run of C2's code. It is not C2's run of record, it is read and not re-run (OD-58), and nothing more is pushed until it finishes (the push rule).

**CK6 (your relay message to C2's session):**

> ```
> **C2: continue after DM-66.** Your stop is answered (DM-66). Your prompt, revision 1, stands, with these changes.
> 1. **Your pushed branch.** `c1fac35` is on the remote, and its Foundation run 43331902479 is not C2's run of record. Push nothing more until it has finished (the push rule). Then read it: if a job failed, report the job and its lines before you go on, and do not re-run it (OD-58).
> 2. **The migration times** (DM-66 item 1, option (b)). In `profile_suite.py`, beside `duration`, write each migration's `applied` time into the results JSON with a six-digit fraction (`isoformat(timespec="microseconds")`), and use the same helper in `discovery_suite.py`. `observe.migration_ledger` stays as it is. T6's tests gain a migration time at a held birth time whose microsecond is 0: not a hit as the suites now write it, and a hit with plain `isoformat()` (the reversal). In the README's "Limits", use DM-66's words (CK3).
> 3. **The README's SV3 heading,** in DM-66's words (CK4).
> 4. **Then finish C2:**
>    - item 6, in RV6's words;
>    - the record's section "Stage A, correction C2", with T5's list, this ruling and every deviation: the README's wider changes, the two allowlisted labels, item 2's checks inside `pages.stale_cursors` with each reversal's failing line, and T7's lines withheld in CI when a scan fails;
>    - the API, contract and mobile checks;
>    - the ordering, identity, profile and discovery suites, with the repeats your prompt asks;
>    - the run of record, under the push rule.
> 5. **The stop rule** stands as written. With option (b), the migration times are within it.
> ```

**If the session is lost:** agree. A new C2 session starts from C2's pushed branch, now on the remote at `c1fac35`, rather than from the session's notes alone, and its prompt names that start.

## 7. DM-65's RV1 to RV10 as applied

The review log's deferred row asks this consultation to confirm them.
- **Confirmed at `16e1ac8`:**
  - RV1 to RV3 in the brief's revision 7;
  - RV4 in the CI policy;
  - RV9 in the P11 plan;
  - RV10 in F7's decision message.
- **Applied in C2's tree at `c1fac35`:** RV5, RV7 and RV8. They are confirmed again when C2 is integrated.
- **Not yet:** RV6, item 6, which waits for C2's run of record.

## 8. Item 4 — Notion (read-only, at about 23:50 UTC; content as of 23:45 UTC, the register copy's as of 17:22 UTC on 11 November)

**How I read it:**
- I searched each page's full text for the items asked, and read Implementation Control's standing bullets whole.
- I did not read every line of its history.

**Implementation Control** says it is matched to `16e1ac8`.
- **Its status** gives C2's stop in plain words, and says C2's work is "not yet pushed". That was true when written; the push followed at 23:48.
- **Its standing lines match:**
  - "Next items": the brief's revision 7, C2 stopped, DM-66;
  - "Branches": five, listed at 18:43 UTC, as there were until 23:48;
  - "Mistakes log": AM11-01 to AM11-17, as in the log;
  - "Standing directions": OD-01 to OD-63;
  - "Main": unchanged and right.
- **The next sync:** six branches, with C2's `claude/practical-cray-h7t08x` (`c1fac35`), and C2's work pushed. The handoff's branch line needs the same.

**SV3's Work Register row:** "In progress", pinned at `16e1ac8`. Its next action also says "not pushed", for the next sync.

**The Dev Manager page** matches the review log.
- **DM-65** is considered: merge `01d2423`, applied at `2475d7b`.
- **DM-66** is pending.
- **Still optional:** the "Sessions" row's two copies differ, as before.

**The register copy** matches: neither it nor the repository's register has changed since `8130439`.

**The handoff** agrees with `16e1ac8`: its title, the review log line and the next step. It is 4,943 bytes.

## 9. Where each item goes

- **The brief, revision 8:** CK1 and CK2; a Sessions line for DM-66's answer.
- **C2's session,** through your relay message (CK6): option (b), CK3 and CK4, and the rest of C2.
- **The evidence record:** CK5; DM-66's disposition.
- **Stage B's scope, or the carried-items file's SV3 section:** CK7.
- **The review log:**
  - DM-66's dispositions, naming `16e1ac8` and C2's `c1fac35` as the commits this read covered;
  - the deferred row for DM-65's RV1 to RV10 stays open, for RV5 to RV8 at C2's integration;
  - a new deferred row: CK1 to CK7, confirmed at my next consultation.
- **Notion:** six branches, C2's push, the status after DM-66.

Status: complete

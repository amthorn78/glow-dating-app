# DM-64 — PR45's run failed on SV2's profile suite: the coordinate scan matches a timestamp

- **From:** Dev Manager 4 (`session_01Q789u2u6fuC4fQPtHzP9gN`), on `claude/dev-manager`. **To:** App Manager 11, relayed by Nathan (OD-25).
- **Read at:** `16c2052ea17549e47d062aeeb619f19d55bda6a7` of `claude/magical-wozniak-yfmmx2`, PR45's head, which holds the consultation, the brief's revision 4 and the evidence record's "PR45's run on `4b771e0`".
  - **The code:** C1's code head `b44e6f7`. No non-Markdown path differs between it and `16c2052`, and no profile-suite file differs from `5bcbe54`.
  - All five remote heads were still there at 04:32 UTC (`git ls-remote`).
- **Written:** 12 November 2026, finished at 04:32 UTC by the clock.
- **DM-63 has not reached me.** It was sent at `4b771e0`, and the review log shows it pending. This answer does not depend on it, except for where the fix goes (T9).
- **Boundaries kept:**
  - I checked environment variable names only. The HDE names and the STREAM and `PG` names are absent; the three AWS names reported before are present. I read no value.
  - I called no provider, database, HDE, Railway, Cloudflare or TypeSafe service. I ran no application code and no test. I read the code, and tested the proposed rules on my own copy of `forms`' logic, in a script kept outside the copy.
  - I wrote only this file. Notion was read, not edited.

## 1. What I read

- **The consultation,** and the evidence record's "PR45's run on `4b771e0`", at `16c2052`.
- **The run:** run 43150501532's Database proof checks log (the profile suite's lines and the step's times) and the steps it skipped.
- **The proof's scans:**
  - `profile_support.py`: `ISO_TIME`, `DECIMAL`, `COARSEST_DECIMALS`, `forms`, `ValueLedger`, and `birth_body`, which adds each birth input's values to the ledger;
  - `profile_cases.py`: `COORDINATES`, `COORDINATE_TEXT`, `_found_in_database` and its two callers;
  - `profile_suite.py` and `discovery_suite.py`: the text each value scan reads, the results JSON and the verdict;
  - `discovery_support.py` and `discovery_cases.py`: the internal points and the distance in the ledgers, the page check, the DEBUG capture, and the plans the results JSON carries;
  - `observe.py`: `server_facts` and `migration_ledger`, which both results JSON files carry;
  - `identity_support.py`: `OutputCapture` and its log format.
- **What prints the run's clock:**
  - the views' `_no_store` (`glow_profiles/views.py:92`, `glow_discovery/views.py:39`);
  - Django 5.2.17's `add_never_cache_headers`, `patch_response_headers` and `http_date`, read from the pinned version's wheel.
- **The brief, revision 4:** the owned paths, the review plan and "Stage A, correction C1 (DM-61)".
- **OD-21 and OD-58** in the register.
- **Notion,** read-only (section 6).

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1. The diagnosis | **Agreed: the failure is the proof's, not C1's.** The same mechanism reaches further than stated, and a **second exposure of the same kind** needs the same fix: held birth times against the `Expires` header (section 3.2) |
| 2. The fix | **(a), approved with conditions (T1 to T9):** one rule for each kind of value, in every scan, not a change to the database search alone. (b) and (c) are declined |
| 3. The sequence | **Agree,** with two failure signatures to record, not re-run, until the fix (T9) |
| 4. Notion | **Matches `16c2052`.** One optional difference remains (section 6) |

**How to apply:**
- **Where each condition goes:**
  - T8's owned-path line: the brief, now;
  - section 4.4's words (T1 to T7, T8's limits and T9): the brief's section for the correction that carries the fix, when the manager writes it.
- **All are Markdown records,** in given words; line breaks may move. None is governing Markdown.
- **Verified by script:**
  - T8's old passage was found exactly once at `16c2052`, and it applies to a copy;
  - the code names in section 4.4 exist at `16c2052`;
  - the rules T2 and T3 were tested offline on 27 texts, with three reversals (section 4.2).
- **No further read is needed** before the correction's prompt if they are applied as written. A departure comes back first. My next consultation after the correction confirms them.

## 3. Item 1 — The diagnosis

### 3.1 Confirmed

- **The search:** `_found_in_database` reads every row of every public table as `row_to_json(t)::text`. It counts a table if any form of `COORDINATE_TEXT` is a substring of a row (`profile_cases.py:642`).
- **The forms:**
  - for `40.7123457`, `forms` gives `40.712`, `40.7123`, `40.71234`, `40.71235`, `40.712345`, `40.712346` and `40.7123457`;
  - a timestamp at second 40 whose fraction starts `712` contains `40.712`, and `…:40.712345` contains four of the forms;
  - `row_to_json` writes a `timestamptz` as `"2026-11-12T03:54:40.712345+00:00"`.
- **The run fits:**
  - the failing case was the suite's 14th, about 11 seconds into a step that started at 03:54:35, so rows written in second 03:54:40 were in the database when it searched;
  - every other case passed, and both scans were clean;
  - the same code, `b44e6f7`, passed 69 of 69 in run 43147201199.
- **Not C1's:**
  - no profile-suite file has changed since `5bcbe54`, and C1 changed none;
  - the mechanism needs only rows that carry timestamps, which every writer has made since SV2.
- **The one other cause I can see:** the bare fractions in `COORDINATE_TEXT` (`7123457`, `0067891`) occurring by chance inside a UUID, a digest or a long number.
  - By my count that is of the order of one run in a thousand or rarer, far below the timestamp.
  - The failure names no table, so neither cause can be proven from this run. T7 makes the next one diagnosable.
- **The same forms reach the value scans,** as the consultation says, and their texts carry the run's clock too:
  - each results JSON carries the migration ledger's `applied` times in full (`observe.migration_ledger`, `isoformat()`);
  - each also carries the durations as raw floats;
  - the discovery results JSON carries each candidate query's `EXPLAIN (ANALYZE, BUFFERS)` text, whose timings have three decimals (`actual time=0.015..1.234`, `Execution Time: 2.345 ms`).

  So the profile suite's coordinates (`40.7123457`, `34.0522342`) and the discovery suite's internal points (whole parts 34 to 41, such as New York's `40.735425`) can match there as well.

### 3.2 A second exposure: held birth times against the `Expires` header

- **What prints the clock:**
  - the profile and discovery views send each answer through `_no_store`, which calls Django's `add_never_cache_headers`;
  - in Django 5.2.17 that sets `Expires` to `http_date(time.time())`, the current second (`django/utils/cache.py:284–285`): for example, `Expires: Thu, 12 Nov 2026 04:13:27 GMT`.
- **What reads it:** both suites' value scans read every response header the routes sent (`profile_suite.py:144–148`, `discovery_suite.py:146–151`).
- **What it matches:**
  - the ledgers hold each birth time a case sends, as entered (`birth_body`, `profile_support.py:396–397`), and a time's form is the time itself;
  - the profile suite holds nine: 02:47:19, 04:13:27 (the default), 06:45:12, 07:31:45, 09:08:07, 10:20:30, 11:22:33, 12:34:56 and 21:56:08;
  - the discovery suite holds 04:13:27.
- **So:**
  - a run whose profile suite answers a request during one of those seconds (UTC) fails its value scan ("profile value scan: FOUND"), and the suite's verdict fails;
  - with an 81-second suite, that is up to about 0.8 percent of runs at random times of day (9 × 81 ÷ 86,400), and the discovery suite (about 60 seconds in the run of record) adds under 0.1 percent;
  - it depends on the time of day, not on the code.
- **Not seen yet** in any run I know of; I found it by reading the code. It is the same kind of failure (a scan matching the run's own clock), in the same files, so it belongs in the same fix (T3).
- **Dates are safe:** every held date is at least 17 years back (`years_ago`), so none can be the run's own date.

### 3.3 The rate

The record's "a few percent" and Notion's "a few runs in a hundred" are estimates; nothing measures the rate. The verdict does not depend on it: a gate that is intermittently red is not dependable at any of these rates (OD-21).

## 4. Item 2 — The fix

### 4.1 The options

- **(a), approved, widened:**
  - **Skipping date and time columns** (the consultation's first bullet) is not enough by itself. Timestamps also sit inside JSON payloads (the outbox), text columns and every results JSON. One rule for each kind of value, in every scan, covers them all, and with it the skip is not needed.
  - **The check of every text** (its second bullet) must cover every value the run's clock prints, not only fractional-second timestamps: HTTP dates, durations and plan timings too, checked against times and distances as well as coordinates (T5).
- **(b), declined:**
  - it changes the nearest-area cases;
  - it cannot move the discovery suite's internal points, which come from the committed area table;
  - it leaves the end of a longer number (`…61.712`), the durations, the plan timings and the birth times as they are.
- **(c), declined** (OD-21): the gate would stay intermittently red, on this case and, at some times of day, on the value scans.

### 4.2 The rules, tested offline

I tested T2 and T3 on my own copy of `forms`' logic.
- **Not hits under the new rules, and hits under the old matcher** (11 texts):
  - a `timestamptz` in `row_to_json`;
  - a timestamp with a space;
  - Django's JSON encoder's milliseconds;
  - an interval's text;
  - a migration's `applied` time;
  - an epoch number ending `40.712`;
  - the longer number `140.7123`;
  - the `Expires` header and an email date at a held time;
  - a timestamp with a fraction at a held time;
  - a logging time (`04:13:27,512`).
- **Still hits** (16 texts):
  - a coordinate in a numeric column (compact JSON), in a JSON payload with a space after the colon, in a text column at three decimals, at the start of a text, in an array, and in a query string;
  - a coordinate followed by further digits (`40.71234512329102`, a 32-bit float's print);
  - the longitude signed, unsigned after a minus, and truncated;
  - a birth time as entered (`"local_time": "04:13:27"`), in compact JSON, alone, with its date (`1990-06-15T04:13:27+00:00`), with today's date (a bug the scan must still catch), and as Python's `repr` (`time(4, 13, 27)`).
- **Reversals:** the old matcher hits the timestamp, the epoch number and the `Expires` header.
- **Durations:** `40.71283` is a hit; written to two decimals (`40.71`), it is not.
- **Plan timings:** T2 alone still counts `actual time=0.015..40.735` and `Execution Time: 40.735 ms` against New York's stored point, `40.735425`, so T4 needs its own rule for them. Costs (`cost=0.29..40.74`) have two decimals and cannot match.

### 4.3 The conditions

**T1 (the property):** in SV2's profile suite and SV3's discovery suite, no value scan (`ValueLedger.found_in`) and no database search (`_found_in_database`) counts what the run's own clock printed. Every other occurrence of every form that `forms` gives still counts.

**T2 (coordinates):** a coordinate's form counts only where it is not preceded by a digit, nor by a digit and a colon (`(?<![0-9])(?<![0-9]:)`).

**T3 (times):** a time's form counts only where it is not preceded by an HTTP or email date (`Thu, 12 Nov 2026 `) and not followed by a fraction of a second (`.` or `,` and a digit).

**T4 (durations):**
- each duration in the two suites' results JSON is written to two decimals;
- the discovery suite's value scan does not count a match inside a timing PostgreSQL wrote into a plan (`actual time=`, `Planning Time:`, `Execution Time:`).

**T5 (the list):** the record lists every value the run's clock prints into each text the scans read (every table, the log records, the writes, the response headers, each results JSON), with the rule that covers it.

**T6 (tests):** offline tests show that each clock text is not a hit and each real print still is, with reversals against the old matcher. They include section 4.2's texts at least.

**T7 (messages):**
- the database search names the table and the column;
- each value scan names the kind of value and the text it was found in;
- neither prints the value.

**T8 (scope and limits):**
- `forms`, what the ledgers hold, `COORDINATE_TEXT` and the cases' checks do not change. No app code changes.
- The proof README's "Limits" states what the rules cannot see:
  - a coordinate printed straight after a digit, or after a digit and a colon (as in `%2040.712`);
  - a held time printed with a fraction of a second, or inside an HTTP or email date;
  - and, unchanged, the small chance that `COORDINATE_TEXT`'s bare fractions occur inside other digits or hex.
- The brief's owned paths gain the files:

> ```
> - `proofs/postgres-ordering/**`: the discovery suite, its settings, tests and locks.
> ```

> ```
> - `proofs/postgres-ordering/**`: the discovery suite, its settings, tests and locks; and, for DM-64's item only, the value scans, the database search and the results JSON's durations in `profile_support.py`, `profile_cases.py`, `profile_suite.py` and `discovery_suite.py`, with their offline tests and the README's "Limits".
> ```

**T9 (placement and sequence):**
- **Placement:**
  - the item goes in the correction after the exact-head review, which PR45 needs anyway;
  - if DM-63's answer puts a correction before the review, the item goes there instead, and the review reads it whole;
  - either way, that correction's section carries section 4.4's words.
- **The review prompt is not held:** the review reads `b44e6f7`, whose run of record is green.
- **The correction's review** reads the item as a security boundary (the privacy scans): T1, T5's list, and that no real print is lost beyond T8's limits.
- **The merge needs:**
  - a green run of record on the final head, with the item in it;
  - Codex on that head;
  - the correction's review.
- **Until the fix, record and do not re-run** (OD-21, OD-58) a run that fails with either signature:
  - (i) `area.coordinates_never_kept_or_echoed` failing alone, with both scans clean;
  - (ii) "profile value scan: FOUND" or "discovery value scan: FOUND" with every case passing, where the job log's line times show the suite running at a held birth time (section 3.2).

  Any other failure is investigated as new.

### 4.4 The words for the correction's section

Place these as an item of the section for the correction that carries the fix, numbered in its order:

> ```
> **The scans and the run's own clock** (DM-64, T1 to T9; PR45's run 43150501532). In SV2's profile suite and SV3's discovery suite, no value scan (`ValueLedger.found_in`) and no database search (`_found_in_database`) counts what the run's own clock printed: a timestamp, an HTTP date, a duration or a plan's timing. Every other occurrence of every form `forms` gives still counts (T1).
> - **Coordinates** (T2): a coordinate's form counts only where it is not preceded by a digit, nor by a digit and a colon (`(?<![0-9])(?<![0-9]:)`). A timestamp's seconds (`…:40.712345`) and the end of a longer number no longer match.
> - **Times** (T3): a time's form counts only where it is not preceded by an HTTP or email date (`Thu, 12 Nov 2026 `) and not followed by a fraction of a second (`.` or `,` and a digit). The `Expires` header Django adds to every response no longer matches a held birth time.
> - **Durations** (T4): each duration in the two suites' results JSON is written to two decimals, and the discovery suite's value scan does not count a match inside a timing PostgreSQL wrote into a plan (`actual time=`, `Planning Time:`, `Execution Time:`).
> - **The list** (T5): the record lists every value the run's clock prints into each text the scans read (every table, the log records, the writes, the response headers, each results JSON), with the rule that covers it.
> - **Tests** (T6): offline, each clock text is not a hit and each real print still is, with reversals against the old matcher; DM-64 section 4.2's texts at least.
> - **Messages** (T7): the database search names the table and the column, and each value scan the kind of value and the text it was found in; neither prints the value.
>
> `forms`, what the ledgers hold, `COORDINATE_TEXT` and the cases' checks do not change, and the proof README's "Limits" states what the rules cannot see (T8). The correction's review reads the item as a security boundary: T1, T5's list, and that no real print is lost beyond those limits (T9). **Stop and report** if the item needs app code, a change to `forms` or to what a ledger holds, or a clock text these rules cannot cover.
> ```

## 5. Item 3 — The sequence

- **Agree.**
  - The exact-head review reads `b44e6f7`, whose run of record (43147201199) is green, so DM-64 does not hold its prompt.
  - The merge then needs a green run of record on the final head, with the fix in it, plus Codex on that head and the correction's review (T9).
- **Before the fix,** a repeat is likely enough to plan for. T9 gives its two signatures. A run with either is recorded, and no one is asked to re-run it (OD-58). Any other failure is investigated as new (OD-21).
- **If DM-63's answer adds a correction before the review,** and the item joins it (T9), the review reads that correction's head instead. That head then needs its own green run of record before the review prompt goes.

## 6. Item 4 — Notion (read-only, at about 04:15 UTC; content as of 04:00 to 04:01 UTC, the register copy's as of 17:22 UTC on 11 November)

**How I read it:**
- I searched each page's full text for the items asked, and read Implementation Control's standing bullets whole.
- I did not read every line of its history.

**Implementation Control** says it is matched to `16c2052`.
- **Its status:** the run's failure diagnosed, DM-64 sent, DM-63 pending. It agrees with the record.
- **What DM-62 found is corrected:** "Next items" now says revision 4 (AM11-11).
- **Its other standing lines match:**
  - "Branches": the five heads `git ls-remote` shows, listed at 03:46 UTC;
  - "Mistakes log": AM11-01 to AM11-12, as in the log;
  - "Standing directions": OD-01 to OD-63;
  - "Phase": ends "Stage A in PR45";
  - "Main": `3240ef0`, with PR45 open.
- **Once DM-64 is considered,** its "a few runs in a hundred" should read as an estimate, and its status should name the birth-time exposure (section 3.2). This is not a mismatch at `16c2052`.

**SV3's Work Register row:** "In progress".
- Its Evidence link is pinned at `16c2052`.
- Its next action names DM-63 and DM-64, then the review, and matches the handoff.

**The Dev Manager page** matches the review log.
- **DM-62** is considered: merge `f5c69fa`, applied as the brief's revision 4. Notion also names the applying commit, `b67bae2`.
- **DM-63 and DM-64** are pending.
- **Still optional:** the two copies of Dev Manager 4's "Sessions" row still differ ("DM-45 to DM-57" in the repository, "DM-42 to DM-59" in Notion). DM-61 section 7 gives words that cannot go stale.

**The register copy** matches: neither it nor the repository's register has changed since `8130439`.

**The handoff** agrees: its title, the review log line (DM-63 and DM-64 open) and the next step.

## 7. Where each item goes

- **The brief:**
  - now: T8's owned-path line;
  - when the manager writes the section for the correction that carries the fix: section 4.4's words.
- **The evidence record:** the manager's disposition; "a few percent" marked as an estimate; the birth-time exposure (section 3.2).
- **The review log:**
  - DM-64's dispositions, naming the commit this read covered;
  - a new deferred row: T1 to T9, confirmed at my next consultation after the correction.
- **The exact-head review prompt, revision 2:** no change is needed for DM-64. Optionally, it can name DM-64's item as known, so that the reviewer does not report it as new.
- **Notion:** Implementation Control's status, as in section 6; optionally, the "Sessions" row's wording.

Status: complete

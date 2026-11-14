# DM-66 consultation — SV3 Stage A, correction C2: the stop at a clock text DM-64's rules cannot cover, and C2's deviations

- **Owner:** App Manager 11. Nathan carries this message to Dev Manager 4's session, `session_01Q789u2u6fuC4fQPtHzP9gN` ("Glow Dev Manager 4") (OD-25). App Manager 11 receives the answer.
- **Revision 1, 12 November 2026.**
- **Why:**
  - C2 stopped at its stop rule (the brief's "The stop rule (C2)"; DM-64 T9): "a clock text DM-64's rules cannot cover". Your conditions say a departure comes back first (DM-65 section 2).
  - C2 also reports four deviations from its prompt and the brief.
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; App Manager 11's disposition in the review log, "DM-66"; the brief's C2 section; the relay message that lets C2's session continue.
- **Stream variables:** none are needed.
- **If no report arrives:** C2 does not continue; App Manager 11 asks Nathan whether Dev Manager 4's session is still available.
- **Deletion condition:** prune after the review log holds DM-66's disposition and SV3 Stage A's PR has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-66 — SV3 Stage A, correction C2: the stop at a clock text DM-64's rules cannot cover, and C2's deviations.** From App Manager 11, relayed by Nathan to Dev Manager 4. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway or Cloudflare;
- check environment variable names only.

**Where it stands.**
- **C2 ran from its prompt, revision 1, at `2475d7b`,** on branch `claude/practical-cray-h7t08x`, and stopped at its stop rule.
- **Its work is committed in its own container only, not pushed:** `39c0bf0` holds the code and its texts (items 1 to 5, item 7's `keys.py` docstring, items 9 and 10), and `c1fac35` holds the evidence record's pointers and its "Cannot" line (items 7 and 8). So you cannot read the code. This message reports what the session said, and the manager has not verified it.
- **The session's report** (relayed by Nathan):
  - **Items 1 to 4:**
    - `pages.one_snapshot_statements` is new, and `pages.stale_cursors` gains three checks;
    - `distance.choice_no_longer_offered` is new;
    - the lock scan now judges joins, through `select_related`, relation paths in calls, `Q`, `F` and paths held in variables, with `of=` checked against the account foreign keys it reads from `models.py`, which are your ten;
    - `pointers.name_order` groups by the backend's PID and start time.
    
    Every reversal failed as intended. The widened scan finds 7 account locks, all `FOR NO KEY UPDATE`, and 47 `select_for_update` calls in `services/api`, none of them joining. `pointers.name_order` passed 30 of 30 local repeats.
  - **Items 5, 7, 8 and 9:** in the given words, each passage found once. By AST, `keys.py`, `reads.py` and `discovery_settings.py` change only their docstrings. The workflow changes in one comment line.
  - **Item 10:**
    - T2, T3, T4 and T7 are applied; `forms`, what the ledgers hold and `COORDINATE_TEXT` are unchanged; the README's "Limits" is updated;
    - T6's tests carry your 11 clock texts and 16 real prints, and with the old matcher 16 fail;
    - T5's inventory, from saved run texts: the `Expires` headers, the results JSON's migration times and plan timings, 125 timestamp columns, and no clock print in the log records.
  - **Local runs** (iteration, not evidence), once each with C2's code: discovery 40/40 and profile 69/69, both scans clean. The proof's offline tests are 266 OK.
  - **Not done, because of the stop:** item 6, the record's C2 section, the API, contract and mobile checks, the ordering and identity suites, the repeated suite runs, and the run of record.
- **Codex** found two more P2s since the review, both already C2's work: on `c661dce`, `pointers.name_order`'s `id(tx)` (item 4); and on `2475d7b`, the discovery scan matching the run's clock (item 10).

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. The clock text no rule covers.**
- **The session's words:**
  - each results JSON writes the migration ledger's `applied` times with `isoformat()`, which drops the fraction when the microsecond is exactly 0, as in `2026-11-12T04:13:27+00:00`;
  - T3 excludes a time only when an HTTP date comes before it or a fraction follows it, so this print would count if it fell on a held birth-time second;
  - "roughly 1 run in 10^10".
- **The manager's check of the arithmetic:** a time needs both a microsecond of exactly 0 (one in a million for each migration time) and a second that equals one of the nine held birth times (about one in 10,000). With the ledger's migrations, that is of the order of one run in a billion or rarer.
- **Options:**
  - **(a)** a documented limit in the README's "Limits", with no code;
  - **(b), the session's choice:** the two suites write those times with a fixed six-digit fraction (`isoformat(timespec="microseconds")`), as T4 writes durations to two decimals. That goes beyond T8's owned "results JSON's durations". Done in the suites' own serialization (`profile_suite.py`, `discovery_suite.py`) it stays in owned files; done where the ledger is built (`observe.migration_ledger`) it does not;
  - **(c)** the value scan does not count a match inside the results JSON's migration ledger's `applied` values, as T4 does not count one inside a plan's timing.
- **The manager's recommendation:** (b), in the suites' own serialization, so that the rule set covers every clock text with no limit beyond T8's; otherwise (a).
- **Asked:** which option, its words, and whether T8's owned-path line needs a change.

**2. C2's other deviations.**
- **The README:** it updated the proof README's discovery paragraph and the scan's layout row. Both are under the brief's `proofs/postgres-ordering/**`, but wider than the prompt's "Limits" alone.
- **The label test:** two failure labels now name the table and column through `_named(...)`. It added exactly those two calls to the label test's allowlist, with the reason. The test checks that no check label is built from a value.
- **Item 2's form:** RV3 says "a case for each" of the cursor's `eligibility_version`, `blocks_version` and a batch not `ready`. The session added them as checks inside `pages.stale_cursors`, which now refuses 13 causes alike, each with its own reversal. The distance choice is a new case.
- **T7 in CI:** the value scan's T7 lines go to the suite's own output, which CI withholds whenever a scan fails. So in CI a failing scan names its kind and text only in a local run.
- **Asked:** a verdict on each.

**3. The continuation** (recommended):
1. your answer;
2. the manager's relay message to C2's session, in your words: push its branch first, since that run is not C2's run of record; then apply item 1's ruling and finish items 6 and 10's list, the record's section, the local checks and the run of record;
3. the manager's verification;
4. PR45's run and Codex on C2's head;
5. the delta re-review;
6. your pre-merge read.

If the session is lost, a new C2 session works from the brief and the session's notes, if they survive. Agree?

**4. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**

# DM-64 consultation — PR45's run failed on SV2's profile suite: the coordinate scan matches a timestamp

- **Owner:** App Manager 11. Nathan carries this message to Dev Manager 4's session, `session_01Q789u2u6fuC4fQPtHzP9gN` ("Glow Dev Manager 4") (OD-25), after or beside DM-63. App Manager 11 receives the answer.
- **Revision 1, 12 November 2026.**
- **Why:** a CI failure that a re-run might seem to clear goes to the Dev Manager first, with options that need nothing from Nathan (OD-32). A passing re-run would not resolve an intermittent failure (OD-21). The fix changes what the proof's privacy scans match, and that touches a security boundary.
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; App Manager 11's disposition in the review log, "DM-64"; the brief; the exact-head review prompt's revision 2 and the correction after the review.
- **Stream variables:** none are needed.
- **If no report arrives:** PR45 does not merge; App Manager 11 asks Nathan whether Dev Manager 4's session is still available.
- **Deletion condition:** prune after the review log holds DM-64's disposition and SV3 Stage A's PR has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-64 — PR45's run failed on SV2's profile suite: the coordinate scan matches a timestamp.** From App Manager 11, relayed by Nathan to Dev Manager 4. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway or Cloudflare;
- check environment variable names only.

**What happened.**
- **The run:** PR45's run 43150501532 on `4b771e0` (records after C1; code identical to C1's head `b44e6f7`) failed in Database proof checks. Every other job passed, and the gate failed on that job.
- **The failing case:** SV2's profile suite, 68 of 69, with `area.coordinates_never_kept_or_echoed` failing: *"FAILED: no table holds the coordinates (outbox and idempotency records included)"*. The suite's secret and value scans were clean.
- **The same case passed elsewhere:** in C1's run of record 43147201199 on `b44e6f7` (69 of 69), and in every completed earlier run of PR45: 43113579295, 43122379022, 43130424814 and 43141093842; the rest were cancelled by later pushes. PR44's three failed runs on 11 November failed only at Mobile checks' Chromium install (the handoff's CI note). No profile-suite file has changed since SV2 Stage B's C2 (`5bcbe54`), and C1 changed none.

**The manager's diagnosis** (the mechanism is shown; which row matched is not known, because the case names no table):
- `profile_cases._found_in_database` reads every row of every table as `row_to_json(t)::text` and looks for each of `profile_support.forms(text)` in it.
- For the latitude `40.7123457`, `forms` gives `40.712`, `40.7123`, `40.71234`, `40.712345` and longer forms (C2's finding 5: rounded and truncated down to three decimals).
- A timestamp written at second 40 and millisecond 712, such as `"created_at":"2026-11-12T03:51:40.712345+00:00"`, contains four of them. I checked this by calling `forms` offline.
- The suite writes thousands of timestamped rows (about 1,500 outbox events and 1,000 idempotency records), many per second. So a run has a chance of a few percent that one row written in second 40 has milliseconds 712 before the case runs. That fits a rare, intermittent failure.
- **The same forms feed `ValueLedger`,** which runs the profile and discovery suites' value scans. Any text those scans read that carries fractional-second timestamps has the same exposure, for every coordinate whose whole part is under 60 (the discovery fixtures' internal points among them). Those scans have not failed so far.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. The diagnosis.** Do you agree with it, and that the failure is the proof's, not C1's?

**2. The fix.**
- **(a), recommended:** fix it in the correction after the exact-head review, which PR45 needs anyway. Every use of `forms` for a coordinate should be unable to match a timestamp:
  - the database search reads no timestamp or date column, since a coordinate is never stored in one;
  - the session checks every text the value scans read for fractional-second timestamps, and makes the scans unable to match one;
  - an offline test shows a timestamp at `:40.712` is not a hit, while a coordinate stored in a numeric or JSON column still is;
  - a reversal: with the old search, the timestamp is a hit.
  
  The owned paths add `profile_cases.py` and `profile_support.py`, in `proofs/postgres-ordering/**`. No app code changes.
- **(b)** choose fixture coordinates whose whole part is 60 or more, so that no form can be a timestamp's seconds. This is simpler, but it changes the nearest-area lookups and any discovery case built on the fixture areas' points.
- **(c)** carry it. This is not recommended: the gate would stay intermittently red (OD-21).
- **Asked:** which option, and its words for the correction's section.

**3. PR45's sequence.** The exact-head review reads `b44e6f7`, whose run of record is green. So this does not hold the review prompt. The merge then needs a green run on the final head, with this fix in it. Agree?

**4. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**

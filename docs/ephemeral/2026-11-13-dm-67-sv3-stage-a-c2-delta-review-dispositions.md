# DM-67 consultation — SV3 Stage A: C2's delta re-review, its dispositions and correction C3's scope

- **Owner:** App Manager 11. Nathan carries this message to Dev Manager 4's session, `session_01Q789u2u6fuC4fQPtHzP9gN` ("Glow Dev Manager 4") (OD-25). App Manager 11 receives the answer.
- **Revision 1, 13 November 2026.**
- **Why:** C2's delta re-review asked for changes, narrowly. Four of its findings are in correction classes, against two security-boundary checks C2 added (the lock scan, F3; the one-snapshot case, F1), and one is a record against DM-64's rule. Dispositions of a review's findings come to you before the correction's prompt (DM-65).
- **Where the result goes:** your report in `docs/continuity/dev-manager/reviews/`; App Manager 11's disposition in the review log, "DM-67"; the brief's revision 9, with a section for correction C3; C3's prompt.
- **Stream variables:** none are needed.
- **If no report arrives:** no C3 prompt is written; App Manager 11 asks Nathan whether Dev Manager 4's session is still available.
- **Deletion condition:** prune after the review log holds DM-67's disposition and SV3 Stage A's PR has merged.

**Manager:** before giving this message to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

**DM-67 — SV3 Stage A: C2's delta re-review, its dispositions and correction C3's scope.** From App Manager 11, relayed by Nathan to Dev Manager 4. Read at commit `<RECORDS_COMMIT>` of `claude/magical-wozniak-yfmmx2`.

Work as your charter says:
- read-only, your report file only, on `claude/dev-manager`;
- no call to Stream, a database, HDE, Railway or Cloudflare;
- check environment variable names only.

**Where it stands.**
- **C2 finished** after your DM-66, at code head `303fdcc` (records `c79bfb6`). Its run of record, 43337467715, passed all eight jobs, with discovery at 40/40 and every scan clean. The manager verified it and integrated it at the merge `8bd983f` (the evidence record, "Manager verification of C2").
- **Its delta re-review** ran from [its prompt](https://github.com/amthorn78/glow-dating-app/blob/<RECORDS_COMMIT>/docs/ephemeral/2026-11-13-sv3-stage-a-c2-delta-review-prompt.md), revision 1, at `dd0f92c`. It is in the evidence record, "Delta re-review of C2", with every finding.
  - **Its verdict:** changes required, narrowly.
  - It found no blocking finding, and no app behaviour, lock, predicate, selection, recheck or writer changed.
  - Your rules (DM-64 T1 to T4, DM-66) are as specified, and every real print it constructed still counts, but one (R1).
  - No code in `services/api` uses any gap it found today.
- **The manager confirmed:**
  - L1, and two of L2's forms (a `Q` held in a variable; `latest()` through a relation), by planting each and running the scan: each passes;
  - S1, S2 and R1, by reading the cited lines.
- **The manager's own verification** of C2 re-ran a `select_related` join, which the scan catches; it did not probe these forms.
- **Nathan decided F7** since DM-65: OD-64 bounds the two-way rule's probing by field, carried to before P11 (the brief's D8; the carried-items file, "Carried from OD-64"). Nothing in C3 touches it.

**Give a verdict on each item:** approved, approved with conditions, changes requested, declined, or refer to Nathan. Where a condition changes text, please give the words (AM9-08).

**1. The dispositions** (recommended):

| Finding | Disposition | In C3 |
|---|---|---|
| L1: a generic lock with a join passes with `of=`, though the docstring requires `no_key=True`; a helper `select_related('account').select_for_update(of=('self',))` called with `AppAccount` locks the account row `FOR UPDATE` | Fix: the code follows the docstring. A generic lock with a join passes only with `no_key=True`. A planted case, and its reversal | Yes |
| L2: forms the scan does not see: a `Q` in a variable or from a helper, an `F` in a variable, `latest()` or `earliest()` through a relation, `.extra(tables=…)`, a join added two variables after the lock, and a reverse path to `AppAccount` (auth `User`'s) | Fix, conservatively. (i) Any argument of a path-taking method or expression method on a locked queryset that is not a literal the scan reads counts as a join. (ii) `latest` and `earliest` are path methods; any `extra()` counts as a join. (iii) The chain is followed through every plain assignment in the same function, before and after the lock, transitively. (iv) A path through a reverse relation to `AppAccount` counts as a join, the reverse names read from `models.py` and auth's `User`. Each with a planted case and its reversal. The docstring, README and record state exactly what stays unseen: a queryset passed between functions (judged as a generic lock); raw SQL's `JOIN {}`; model aliases (C1's rules, unchanged) | Yes |
| S1: before the probe point, any statement on the account table alone whose parameters hold the viewer's ID passes, so a pre-probe read of other members' accounts passes | Fix: before the probe point, only an explicit list passes: `predicates.VIEWER`, and the viewer's account-row lock (its SQL shape, with the viewer's ID as its only parameter); any other statement reading a member table fails. The database reversal D (a pre-probe read of other members' accounts), failing | Yes |
| S2: the cursor page's write check reads its transaction only | Fix: the check reads every phase the probe records for a page by cursor, and fails on any write. The database reversal E (a write after the transaction), failing | Yes |
| R1: the README says the rules cannot see "a held time printed with a fraction of a second", but T3 drops a held time followed by `.` or `,` and a digit, a field separator included | Records only: the README's "Limits" states the rule's own shape (a held time followed by `.` or `,` and a digit, which covers a fraction, a logging time's milliseconds and a separator before a digit) | Yes (records) |
| N1: T3's date rule is wider than the `Expires` header it exists for (any year, a one-digit day, every text) | Carried to Stage B, with CK7's follow-up: narrow the rule to the header's own shape and text. Your DM-66 called the one-digit day "harmless extra coverage"; the review reads it as a wider exemption | No (carried) |
| N2: T5's list leaves out two case-level checks the rules also apply to (`check_page`'s private ledger; `logs.no_private_value`'s capture) | Records: the record's T5 list gains both, with why no clock text can match | Yes (records) |
| N3: no offline test of `_found_in_database`'s rules | Carried to Stage B; the database cases cover the rules | No (carried) |

- **Asked:** is each disposition right? If you give words for L2's rule and S1's list, please give them for the brief's C3 section.

**2. C3's shape** (recommended):
- C3 is a correction of the proof's tooling and records only: `account_lock_scan.py`, `discovery_cases.py`, their offline tests, the proof README, and the evidence record. No app code, workflow, contract or dependency changes.
- **Its stop rule:** stop and report if C3 needs any of these:
  - a change outside those paths;
  - a change to a predicate, the selection, the recheck, a lock or a writer;
  - an account lock in `services/api` that the corrected scan refuses.
- **Its run of record:** a push run on its code head, all eight jobs, with the ordering, identity, profile and discovery suites.
- **Its review:** a short delta re-review of C3 against `303fdcc`, reading L1, L2, S1 and S2 with their reversals. Alternatively, the manager's verification alone, with your pre-merge read. The manager recommends the delta re-review, since both checks are security boundaries.
- **Asked:** agree, or give the scope and the review you want.

**3. The sequence** (recommended):
1. your answer;
2. the brief's revision 9, with C3's section in your words;
3. C3's prompt, with its TypeSafe reading;
4. C3, then the manager's verification;
5. PR45's run and Codex on C3's head;
6. C3's review, as item 2 decides;
7. your pre-merge read, then the merge.

Agree?

**4. Notion.** Please report any mismatch you find at `<RECORDS_COMMIT>`.

**Please end your answer with the relay message for Nathan, naming your report file and the commit on `claude/dev-manager`.**

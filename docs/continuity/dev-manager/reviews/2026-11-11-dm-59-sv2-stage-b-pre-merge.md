# DM-59 — SV2 Stage B's pre-merge read

- **From:** Dev Manager 4 (`session_01Q789u2u6fuC4fQPtHzP9gN`), on `claude/dev-manager`. **To:** App Manager 10, relayed by Nathan (OD-25).
- **Read at:** `4b2c03a53d994ccd9910ebecd596fa3f9db413bf` of `claude/magical-wozniak-yfmmx2`, PR44's head, which holds the consultation and its addendum (item 7).
  - **The code:** the code head `5bcbe54`. No non-Markdown path differs between it and `4b2c03a`.
  - **Stage B's application code** is C1's `7538c76`: C2 changed no file in `services/api` outside its tests.
  - **Also read:** PR44 with its runs and Codex's thread, through the GitHub tools.

  Each was still there at 15:34 UTC (`git ls-remote`).
- **Written:** 11 November 2026, finished at 15:34 UTC by the clock.
- **Boundaries kept:**
  - I checked environment variable names only. The HDE names are absent; the three AWS names reported before are present. I read no value.
  - I called no provider, database, HDE, Railway, Cloudflare or TypeSafe service, ran no application code, and wrote only this file.
  - Notion was read, not edited.

## 1. What I read

- **The consultation and its addendum** at `4b2c03a`.
- **The four texts on the pre-merge list,** at `4b2c03a`, with their diff from `52ae066` and the commits that made it:
  - `ecad10c`, J1 to J5;
  - `e30ef4a`, C1's sentences;
  - `885f65b`, N3, N4 and N8;
  - `9740196`, C2's N5.
- **The code they describe:**
  - C1's change (`git diff d8f1bad 7538c76`) to `tx.py` and `media.py`;
  - every use of `lock_account_any_state`, and each photo step's first lock;
  - `media_fixtures.py` whole;
  - the owner's read in `operations.py`, which serves the photo reads;
  - the proof's value ledger (`profile_support.py`) and its README sentence.
- **The evidence record's sections from Stage B on:**
  - "Stage B, correction C1", with its items, tests and run of record;
  - "Exact-head review of Stage B after C1", with its threat model and dispositions;
  - "Stage B, correction C2", with its run of record;
  - "Delta review of Stage B's correction C2";
  - the failed run's record.
- **For items 3 to 5:**
  - my DM-58 report, matched by script against the six files, at `ecad10c` and at `4b2c03a`;
  - the manager workflow's diff from `52ae066` and from `main`;
  - every governing path in `git diff 4dc2061 4b2c03a`;
  - the carried-items file and the P11 plan for the carried nits.
- **For item 7:**
  - the workflow's Chromium step and DM-41's retry steps, and the Mobile job's timeout;
  - PR44's runs 43021936005 (`c4324d3`), 43044190450 (`9464dd8`) and 43046997028 (`4b2c03a`): their jobs and steps, and both failed Mobile jobs' log tails;
  - Codex's summary and threads on PR44.
- **Notion,** read-only (section 8).

## 2. Verdicts

| Item | Verdict |
|---|---|
| 1. The rewritten texts | **Approved with conditions.** The texts match the code at `7538c76` and `5bcbe54`. Two corrections are needed: the P11 plan's Stage B entry still names `d8f1bad`'s run, with 64 cases, and lacks C1, C2 and 0008's malformed-write case (L2 to L4); and three texts still cite the brief's revision 7 (L2, L5, L6) |
| 2. C2's sentence and N-e | **Approved, in the manager's words (L1).** The fixture store's `read` does append to `reads` inside the transaction, and nothing else is missing from the list |
| 3. J1 to J9, and C1, as applied | **Confirmed, with no departure.** J1 to J9 are as written at `ecad10c`. At `4b2c03a`, J5's row also carries C2's N5 wording, which item 2 approves. C1 matches DM-58 section 3 |
| 4. The manager workflow | **Confirmed.** My DM-58 section 6 read, at `52ae066`, stands as PR44's pre-merge read of its only governing Markdown, provided the file is unchanged at the final head |
| 5. The nits carried | **Confirmed.** None needs closing before the merge |
| 6. The merge | **Yes, once these hold:** L1 to L7 applied as written; the review log's DM-59 dispositions; the PR run on the final head passing with `Application checks passed`; Codex raising nothing new there; the checklist filled in. Section 7 says what to do if the final head's run fails the same way |
| 7. The Chromium install failure | **(b), approved, with L7's words.** It failed again, the same way, on `4b2c03a`. So the outage outlasted any retry pause, and the carried item says so |
| Notion | **Matches** `4b2c03a` (section 8) |

**How to apply:**
- **Where each condition goes:**
  - L1: the data model;
  - L2 to L4: the P11 plan;
  - L5: the contract document;
  - L6: the media fixtures note;
  - L7: the carried-items file.
- **All seven are Markdown records,** in given words; line breaks may move. None is governing Markdown, and none changes code, a test or the workflow file.
- **Verified by script:** each old passage was found exactly once at `4b2c03a`, and all seven apply in order to copies.
- **No further read is needed before the merge** if they are applied as written. A departure, or any other change to these texts or to the manager workflow before the merge, comes back first. My next consultation, or the close-out read, confirms them (step 6).

## 3. Item 1 — The rewritten texts

**I read each text at `4b2c03a` against the code.**
- **The data model's `MediaAsset` and `MediaObject` row:** J1 and C1's sentence match the code.
  - `lock_account_any_state` is at `tx.py:174`.
  - It is used only by `acknowledge_deletion` (`media.py:473`) and `request_purge` (`:679`).
  - Every other photo command, staff operation, step and read takes `lock_account` or `read_account_shared`.
- **The `MediaUploadGrant` row** is unchanged since my DM-58 read, and still matches its constraints.
- **The unit-of-work table's F05 row:** J5 holds with C2's N5 wording, completed by L1 (item 2).
- **The contract document's F05 entry:** J4 and "The account's state" match the code. The member's photo reads go through the owner's read, whose first statement is `read_account_shared`, so "the member's commands and reads … refuse an account that is not active" is right.
- **The fixtures note's server section:** J3 holds.
- **The P11 plan's DM-58 entry (J2)** is as written.
- **The P11 plan's exact-head review entry:**
  - N3 holds: the server stores whatever reference the port gives, and the column has no pattern;
  - N4 holds: the original's `MediaObject` row is made with the grant;
  - N8 holds: `POSITION_MAX` is 29,999, and a new photo takes the highest current position plus one.

**Two corrections are needed.**
- **The P11 plan's Stage B entry was not updated after C1 and C2.**
  - Its run of record is still `d8f1bad`'s, with 64 cases.
  - Its scans' description ("photo bytes among them") is what the exact-head review's F4 found the ledger did not hold.
  - It has no DB04 line, though C2 added the malformed-write case for 0008's 21 constraints.
  - Its PV04 line has neither C1's account-state rule nor C2's held approval.

  Stage A's entry names its final correction's run and the earlier ones, and L2 to L4 do the same for Stage B. The numbers are the runs' own, as the evidence record reads them.
- **Three texts cite the brief's revision 7,** while Stage B as merged follows revision 8 (J6, J7, and C1): the P11 plan's Stage B entry (L2), the contract document's F05 entry (L5) and the fixtures note (L6).

**L2:** in the P11 plan, "SV2 Stage B: photos on a disposable database", replace:

> ```
> "Stage B"; the [SV2 brief](../planning/sv2-profiles-media.md), revision 7, D9, D10 and D19, with DM-57's conditions).
> ```

with:

> ```
> "Stage B", "Stage B, correction C1" and "Stage B, correction C2"; the [SV2 brief](../planning/sv2-profiles-media.md), revision 8, D9, D10 and D19, with DM-57's and DM-58's conditions).
> ```

and replace:

> ```
> **Run of record:** push run [42947095725](https://github.com/amthorn78/glow-dating-app/actions/runs/42947095725) on `d8f1bad`, Stage B's code head: every job passed and the gate printed `Application checks passed`; 64 of 64 cases in 81.7 s, the profile phase 83 s within the job's 30-minute timeout; the suite's scans of the 1,381 secrets and 511 member values it handled (object keys, grant and delivery references and photo bytes among them) were clean.
> ```

with:

> ```
> **Run of record, correction C2:** push run [42990527042](https://github.com/amthorn78/glow-dating-app/actions/runs/42990527042) on `5bcbe54` (C2's code head, tests only; Stage B's code is C1's `7538c76`): every job passed and the gate printed `Application checks passed`; 69 of 69 cases in 99.8 s, the profile phase 100 s within the job's 30-minute timeout; the suite's scans of the 1,447 secrets and 813 values it held were clean, the values being the member values and every object key, grant and delivery reference and upload credential's token, with the start of each object's bytes. Earlier: correction C1's run [42957799823](https://github.com/amthorn78/glow-dating-app/actions/runs/42957799823) on `7538c76` (67 of 67 in 55.6 s), and Stage B's run [42947095725](https://github.com/amthorn78/glow-dating-app/actions/runs/42947095725) on `d8f1bad` (64 of 64 in 81.7 s), whose scans held fewer of these values (the exact-head review's F4).
> ```

**L3:** in the P11 plan, the same entry's PV04 line, replace:

> ```
> approval, delivery and a removed photo's purge each ask the hold port first. **Not shown:**
> ```

with:

> ```
> approval, delivery and a removed photo's purge each ask the hold port first, and a hold stops the check's approval with nothing written (C2); the purge and the store's deletion acknowledgment complete in any account state, while every other photo step refuses an account that is not active (C1). **Not shown:**
> ```

**L4:** in the P11 plan, the same entry, before its DB07 line, replace:

> ```
>   - **DB07,** the rollback half only: a refused grant, a refused publication above a media ceiling
> ```

with:

> ```
>   - **DB04,** for migration 0008's tables (correction C2): 21 malformed direct writes, each breaking one constraint only and each refused by PostgreSQL by name, against all 13 constraints 0008 declares and the 8 other unique keys, foreign keys and column checks PostgreSQL holds on its two new tables (`constraints.malformed_media_writes_are_refused`). Not covered: NOT NULL columns, primary keys and `MediaAsset`'s constraints from before 0008.
>   - **DB07,** the rollback half only: a refused grant, a refused publication above a media ceiling
> ```

**L5:** in the contract document, F05 in "F02 to F06 on the server", replace:

> ```
> revision 7, D9, D10 and D19, with DM-57's conditions; OD-61; OD-62)
> ```

with:

> ```
> revision 8, D9, D10 and D19, with DM-57's and DM-58's conditions; OD-61; OD-62)
> ```

**L6:** in the media fixtures note, the server section, replace:

> ```
> revision 7, D10;
> ```

with:

> ```
> revision 8, D10;
> ```

## 4. Item 2 — C2's sentence, and N-e

**Approved, in the manager's words.** In `media_fixtures.py`, what each adapter call writes to memory:
- **The store's port methods, called inside a transaction:**
  - `issue_upload` writes `credentials`;
  - `read` appends to `reads`;
  - `write` writes `objects`;
  - `delete` extends `deletions`;
  - `delivery_reference` writes `references`;
  - `receive` writes nothing.
- **Processing** calls only `read` and `write`.
- **The detector, the check and the hold** write nothing.
- **`put` and `acknowledge`** are test setup only, and no route calls them.

So `reads` is the one write the sentence left out.

**L1:** in the data model, the unit-of-work table's F05 row, replace:

> ```
> (the fixture store's objects, credentials, deletion requests and delivery references)
> ```

with:

> ```
> (the fixture store's objects, credentials, reads, deletion requests and delivery references)
> ```

## 5. Items 3 to 5 — As applied, the workflow, and the nits

**Item 3: J1 to J9 are confirmed, with no departure.**
- **At `ecad10c`,** where they were applied, each new text is present exactly once and no old text is left.
- **At `4b2c03a`,** all are present but J5. Its row also carries C2's N5 wording ("with no effect outside the process: …"), and that clause and C1's sentence are the data model's only changes since `ecad10c`. Item 2 approves N5's wording.

**C1 is confirmed against DM-58 section 3, with no departure.**
- **The lock:** `lock_account_any_state` is `lock_account` without its state check: the row `FOR UPDATE`, an absent row refused, the probe signalled.
- **Its users:** only the two writers use it, and the purge still asks the hold port before the store.
- **The tests:**
  - `LockOrderTests`, three tests;
  - `AccountStateTests`, three;
  - the three suite cases, with their reversals.

  The third case also covers staff's restriction and the delivery read. That is beyond DM-58's list, and checks the same rule.
- **The records** say it, and the brief has J6 and J7.

**Item 4 is confirmed.**
- **The manager workflow is unchanged from `52ae066`** at `4b2c03a`.
- **It is PR44's only governing path:** `AGENTS.md` or `CLAUDE.md` at any level, `docs/pf-canon/`, the charter, the CI policy, `.github/` and `.claude/` are all unchanged from `main`.
- **Its only change from `main` is U11's three lines.**
- **So my DM-58 section 6 read stands** as PR44's pre-merge read of it, provided the file is unchanged at the final head.

**Item 5: the carry is confirmed.**
- **Each nit is where the manager says:**
  - N1 under "Carried to P07";
  - N3, N4 and N8 in the P11 plan;
  - N-a, N-b, N-c's docstring half, N-d and N-f in the carried-items file's new section for SV2's profile guards and suite.
- **None is in a correction class,** and no code uses the spellings the guards miss.
- **N1 does not blur the audit trail.** The review step's rejection is written with the check's subject, but with the reason `no_variant`, which only that step writes.

## 6. Item 7 — The Chromium install failure

**The diagnosis holds, and the failure has recurred.**
- **Run 43044190450 on `9464dd8`:**
  - Mobile checks failed at "Install Chromium for rendered fixture checks", from 15:03:12 to 15:13:17;
  - its log shows nine font packages, each `Temporary failure resolving 'azure.archive.ubuntu.com'`, then `Failed to install browsers` and `Installation process exited with code: 100`;
  - the other six jobs passed.
- **Run 43046997028 on `4b2c03a`,** this message's commit, also Markdown only:
  - it failed the same way at the same step, from 15:20:05 to 15:30:16, with the same nine packages and the same error;
  - its other six jobs had passed by 15:25;
  - Codex's review of `4b2c03a` completed at 15:20 with no findings.
- **On `c4324d3`'s passing run,** the same step took 38 seconds and the rendered checks 5 minutes 13 seconds.
- **So it is the runner's package-mirror name resolution, lasting at least 15:03 to 15:30 UTC.** No file in PR44 touches it.

**(b), approved:**
- **Why not (c):** a retry now would widen PR44 with a full-scope workflow change. It would also not have saved these runs: the outage lasted longer than the job's 25-minute timeout allows for any pause.
- **Why the carry still has value:** a retry still spares a later PR a short failure. The carried item records its limits.
- **The merge rule is unchanged:** a PR run on the final head must pass. Section 7 says how the next run is started.

**L7:** in the carried-items file, before "Carried to the next change to the branch cleanup", replace:

> ```
> ## Carried to the next change to the branch cleanup (M04's exact-head review)
> ```

with:

> ```
> ## Carried to the next change to the Foundation workflow (DM-59)
>
> - **A one-time retry of the Chromium install** (DM-59 item 7). On 11 November 2026, PR44's pull-request runs 43044190450 on `9464dd8` and 43046997028 on `4b2c03a`, both on Markdown-only commits, failed in Mobile checks at "Install Chromium for rendered fixture checks" (`npx playwright install --with-deps chromium`), while every other job passed: apt could not fetch nine font packages (`Temporary failure resolving 'azure.archive.ubuntu.com'`), from at least 15:03 to 15:30 UTC. The step has no retry. On DM-41's pattern, the next change to `.github/workflows/foundation.yml` gives the step `id: chromium` and `continue-on-error: true`, then adds a pause and one retry of the same command, each only `if: steps.chromium.outcome == 'failure'`; the retry has no `continue-on-error`, so a second failure fails the job. Each attempt takes its own `timeout-minutes`, set so that both attempts, the pause and the rendered checks fit in the job's 25 minutes (each failed attempt took about 10 minutes; on a passing run the install takes under a minute and the rendered checks about 5). A retry helps only a short failure: this one outlasted any pause that fits. The CI policy's paragraph "Toolchain installs are retried once" names the new retry beside DM-41's. The change is full scope: the manager reads the complete workflow diff, and full checks pass before it merges (root `AGENTS.md`).
>
> ## Carried to the next change to the branch cleanup (M04's exact-head review)
> ```

## 7. Item 6 — The merge

**PR44 may merge once these hold,** within Nathan's standing app-only authorization:
- L1 to L7 applied as written;
- the review log's DM-59 dispositions, naming the commit each read covered:
  - the manager workflow at `52ae066` (DM-58 section 6);
  - the other texts at `4b2c03a`, with L1 to L6;
- the PR run on the final head passing, with `Application checks passed`;
- Codex raising nothing new on that head;
- the checklist in PR44's description filled in.

**The next run, given the outage:**
- **The final head is the records commit that applies this report** and records run 43046997028. Its pull-request run is the one the merge needs.
- **If that run's Mobile checks fail at the same step with the same name-resolution error, while every other job passes:**
  - the manager records that run;
  - it makes no commit only to start a run (the PR-activity rules);
  - its next records commit comes no sooner than an hour after the failure, and its run is the next attempt.
- **It comes back to me only if the failure changes:** another step, error or job, or the rendered checks themselves failing.

## 8. Notion (read-only, at about 15:31 UTC; content as of 15:18 UTC)

**How I read it:** I searched each page's full text for the items asked. I did not read every line of Implementation Control's history.

**Implementation Control** says it is matched to `4b2c03a`.
- **Its status:**
  - the failed run on `9464dd8` and the diagnosis;
  - one comment on PR44, and no re-run;
  - item 7 to me, with C2's delta review before it.
- **Its state:**
  - `main` at `4dc2061`, with PR44 open;
  - the Manager bullet now names PR44 as open, so DM-58's nit was taken;
  - six branches, as `git ls-remote` lists them, with `claude/dev-manager` at `1006f04`.
- **It predates run 43046997028's failure,** which it does not yet mention.

**SV2's Work Register row** matches.
- **State:** "In progress", with its evidence pinned at `4b2c03a`.
- **Its next action names:**
  - revision 8;
  - Stage B, C1 and C2, with their code heads;
  - C2's delta review;
  - the runs on `c4324d3` and `9464dd8`;
  - DM-59 with its item 7 at `4b2c03a`.

**The Dev Manager page** matches the review log.
- **DM-58** is considered: merge `e547084`; J1 to J9 applied at `ecad10c`; C1 commissioned; the nit taken.
- **DM-59** is pending, at `9464dd8`, the commit that added it.

## 9. Where each item goes

- **Before the merge:**
  - L1 in the data model;
  - L2 to L4 in the P11 plan;
  - L5 in the contract document;
  - L6 in the media fixtures note;
  - L7 in the carried-items file;
  - in the same records commit, run 43046997028 in the evidence record.
- **The review log:** DM-59's dispositions, naming the commits each read covered. The deferred rows close:
  - J1 to J9 and C1 (item 3);
  - the manager workflow's pre-merge read (item 4).
- **PR44:** the run and Codex on the final head, the checklist, the merge. Section 7 covers a repeat of the failure.
- **The next change to the Foundation workflow:** L7's retry, with the CI policy's paragraph.
- **Notion:** run 43046997028 at the next sync.

Status: complete

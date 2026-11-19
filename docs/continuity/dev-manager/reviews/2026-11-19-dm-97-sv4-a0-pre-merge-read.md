# DM-97 — SV4 A0's pre-merge read (PR57)

- **Read at:** `fc9decdb87fcb8b6fd97f71a7ac6c88ceffb1d9a` of `claude/magical-wozniak-yfmmx2`: PR57's head, and the live branch's head when I fetched it at 22:36 UTC. `main` at `c2cffbe`, PR57's base.
- **Requested by:** App Manager 12, relayed by Nathan ([the consultation](../../ephemeral/2026-11-19-dm-97-sv4-a0-pre-merge-read.md)).
- **Written by:** Dev Manager 6, on 19 November 2026, from about 22:36 UTC.
- **What this is:** D-07's second read of SV4 A0 (OD-75). It is the governing read of the CI policy's change that DM-96's AG21 asked for (the review log's deferred row "DM-96: the Dev Manager reads A0's change to the CI policy before A0 merges"), with the items the manager listed for it.

## 1. The answers

| Item | Verdict |
|---|---|
| 1. The CI policy's change | **Approved as written,** at `fc9decd`. Every claim I checked holds against the workflow |
| 2. The workflow against AG1 | **A0 meets AG1, and each job keeps every check it ran before.** The exact-head review's reading of "another suite's marker" is the right one |
| 3. AG1 to AG21, and revision 3 | **AG1 to AG21 are applied exactly** (checked by script). **Revision 3's additions are approved** |
| 4. C1 and C2 | **Approved.** There is nothing in either that I would not merge |
| 5. F3, the Chromium retry's timeout | **(a), approved with conditions AH1 and AH2.** The open question has an answer: the runner marks a step stopped by its own timeout as failed, so the retry runs. But the 10 and 6 minutes are A0's, not DM-59's, and the slowest passing installs come close to the first attempt's limit |
| 6. The manager's D-07 calls | **Agreed,** both |
| 7. F8, the README's sentence | **Approved as written** |
| 8. What is carried or recorded only | **Each is in the right place.** Two additions to the carried entry (AH3, AH4), and two living records still name the one shared job (AH5, AH6) |
| 9. The start note's points | **Confirmed.** No mismatch |
| 10. Notion | **Matches** the repository at `fc9decd` in everything I read |

- **The merge:** PR57 may merge once AH1 and AH2 are applied as given, in the batch that records this disposition, and that batch's head has its passing PR run and Codex's completed review (section 13).
- **AH3 to AH6** block nothing. They may go in the same batch or the next.
- **For Nathan:** nothing to decide.

## 2. What I read and checked

- **The governing diff:** `git diff c2cffbe fc9decd` lists 33 files. The only governing Markdown among them is the CI policy (`docs/operations/ci-and-branch-policy.md`). No `AGENTS.md` or `CLAUDE.md`, nothing under `docs/pf-canon/`, and neither the manager workflow nor the charter changed. The register (`owner-directions.md`) gained OD-82.
- **The classification:** the trusted classifier, `main`'s `scripts/change_scope.py` (sha256 `b564c62f…`), was extracted outside the tree and run with `python3 -I --base c2cffbe… --head fc9decd… --merge-base`. It printed `"full": true`, reason `behavior-or-empty`, with one merge base. The non-Markdown paths at `fc9decd` equal C2's code head `5a2f137` (`git diff --name-only 5a2f137 fc9decd -- . ':!*.md'` is empty).
- **The workflow,** `c2cffbe`'s against `fc9decd`'s:
  - parsed with PyYAML in my scratch directory and compared job by job and step by step, by script;
  - every changed or new step read whole: the four credentials steps, the four role steps, the three `dbshell` steps, the three decoy steps, the two suite steps whose comments changed, the start and removal steps, the Mobile job's three Chromium steps and the gate.
- **The proof's code, read without importing it:**
  - the three scans' diffs;
  - `glow_ordering_proof/marker.py`, unchanged by A0, whole;
  - the suites' use of `server_facts()`.
- **The tests:**
  - C1's diffs in all three offline test files, whole (`3bf55de..c78f297`), and C2's in two (`c78f297..5a2f137`);
  - the decoy-step and `dbshell` test sequences of the three files, compared by my own `ast` script, never importing or running them;
  - the pin test's diff (`services/api/tests/test_toolchain_pins.py`).
- **The records:**
  - the A0 record (`docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`), sections "A0" to "Delta review of A0-C2", whole;
  - the brief, revision 3: D2, D11's A0 bullet, A0's owned paths, the acceptance checks, the review plan and the revision history;
  - DM-96's report, sections 3, 11, 12 and 14;
  - DM-59's report, section 6, and its carried entry;
  - the carried-items file's "Carried to SV4" and "Carried to the next change to the Foundation workflow (DM-59)";
  - the register's OD-82 and its preface; the review log's Sessions table and its DM-97 row; the handoff, whole.
- **GitHub, read only, through the GitHub tools:**
  - PR57 (head `fc9decd`, base `c2cffbe`, open, mergeable);
  - its runs, and PR run 44610075506 on `fc9decd`: its eleven jobs and their steps, the gate's whole log and the identity job's log from its decoy step to its end;
  - Codex's summary comment, and the PR's reviews (none).
- **The runner's source:** `actions/runner`'s `src/Runner.Worker/StepsRunner.cs` and `src/Runner.Worker/ExecutionContext.cs`, at release v2.338.2 and at `main` `7e211dc`. These are public files, fetched read only (section 7).
- **Notion,** read only: section 12.
- **Not run by me:** the offline tests. CI ran all 383 in each database job on the final head, and the manager and both delta reviews ran them too.

## 3. Item 1 — the CI policy's change

**Approved as written.** Each claim below was checked against the workflow at `fc9decd`, and against PR run 44610075506 on the same head.

- **The jobs and their count:**
  - the four names, "Database proof checks (ordering)", "(identity)", "(profile)" and "(discovery)";
  - "all nine application jobs";
  - the gate's `needs` and its `jobs` tuple name the same nine.
- **Every database job:**
  - runs the install, `pip check`, the offline tests under `env -i`, and Ruff and mypy (the old job's steps, byte for byte);
  - starts its own PostgreSQL 17.11 from the pinned digest, on loopback on its own runner;
  - generates its own credentials and masks them before anything prints.
- **The four bullets,** each against its job's steps:
  - **Ordering:** the wrong-marker and `dbshell` refusals, the migrations, `facts`, the suite, the second-run refusal and the `p06-db-proof-results` upload. All are byte for byte the old steps.
  - **Identity, profile and discovery:** `dbshell`'s refusal under the suite's own settings; the decoy's marker refused, with the relation counts unchanged and no table; the scan; the second run; and the upload, gated on the scan.
- **The scans' paragraph:** each scan reads "every secret file its own job writes … and no other". I checked each scan's `VALUE_FILES`, `PASSFILE` and `KEY_FILES` against the files its job's credentials step writes:

  | Job | Files its credentials step writes |
  |---|---|
  | identity | `superuser-password`, `passfile`, `identity-marker`, `marker` (the decoy's), `identity-secret-key`, `identity-jwt-key.pem` |
  | profile | the same, with `profile-…` for the suite and `identity-marker` for the decoy |
  | discovery | the same, with `discovery-…` and `profile-marker` |

  `create-role.sql` is removed by the role step, and its values are in the files above.
- **The upload-artifact row:** "the four database proof jobs".
- **"Toolchain installs are retried once":**
  - the first attempt has `id: chromium`, `continue-on-error: true` and `timeout-minutes: 10`;
  - the pause (`sleep 60`) and the retry each run only `if: steps.chromium.outcome == 'failure'`;
  - the retry has `timeout-minutes: 6` and no `continue-on-error`;
  - the arithmetic holds: 2.2 + 10 + 1 + 6 + 5.3 = 24.5 minutes of the job's 25.
- **The database-server paragraph:**
  - the decoy's names per job: `glow_proof`, `glow_identity_proof` and `glow_profile_proof`;
  - the masks;
  - the `if: always()` removal step, with its check that no proof container remains;
  - the 30-minute timeouts, and the 24-minute finding rule.
- **The documentation policy's counts** ("nine") and the gate's history ("six before SV4 A0 split Database proof checks into one job per suite").
- **The live run:** PR run 44610075506 (event `pull_request`, head `fc9decd`): all eleven jobs succeeded, and the gate's log ends "Application checks passed" (20:43:54 UTC).

No stale job name or count is left in the policy. Two other living records still describe the one job; they are outside the policy (AH5, AH6).

## 4. Item 2 — the workflow against AG1

**A0 meets AG1, and each job keeps every check it ran before.**

- **Outside the database jobs, nothing changed:**
  - the triggers, the permissions, the concurrency group, and the jobs `scope`, `api`, `smoke`, `artifact` and `proof` are identical;
  - Mobile checks differs only by the Chromium retry's two added steps and its first step's three keys;
  - the gate differs only in its `needs` and its `jobs` tuple. Its rule and its `if: always()` are unchanged.
- **Every database job keeps today's condition, `needs: scope`, `runs-on` and `timeout-minutes: 30`.**
- **The old job's 30 steps:**
  - 23 are byte for byte in a new job (by hash);
  - 7 changed only as the split needs: the credentials step, the role step, the three "refuses the other marker(s)" steps (now the decoy steps), and the profile and discovery suite steps, whose inner comment alone changed;
  - none was made conditional, reordered or dropped;
  - the new steps add checks: `dbshell`'s refusal under each suite's settings, and the decoy step's relation counts.
- **The server's facts:** the ordering job records them in its `facts` step. The identity, profile and discovery suites record their own server's facts in their reports (`server_facts()`: `identity_suite.py` line 113, `profile_suite.py` line 137, `discovery_suite.py` line 133). So every new server's facts are recorded.
- **AG1's words.** "carrying another suite's marker" was Dev Manager 5's text, written "in its own PostgreSQL". I confirm the exact-head review's reading:
  - another suite's real marker exists only in another job, on another runner, and passing it across would share a secret between jobs for no gain;
  - the marker check compares the connected database's own comment (`marker.py`, `QUERY`: `WHERE d.datname = pg_catalog.current_database()`), so the case to refuse is a well-formed marker that another database in the same server carries;
  - a marker the job generates, on a database named as the other suite's, is exactly that case.
- **The decoy step is stronger than the shared job's step:**
  - it also requires the suite's database unchanged, by relation counts per schema;
  - it requires no relation outside the catalog schemas, and no `django_migrations`.
  The shared job's profile and discovery steps refused two and three markers. One marker per job proves the same property, since each refusal is the same equality test against that database's comment.
- **The live evidence** (the identity job of run 44610075506, on `fc9decd`):
  - "decoy database glow_proof with a marker as its comment: 1; its comment differs from the identity database's: t";
  - relation counts before and after identical (`information_schema 69`, `pg_catalog 266`, `pg_toast 80`, `public 0`), "0 before, 0 after" outside them, and "to_regclass('public.django_migrations') IS NULL after: t";
  - exit status 1, with the refusal "…the database's comment is different…";
  - then the migrations from zero, and "No changes detected".

  I read the other three jobs' steps by their conclusions only, all success.
- **No step prints a value.** The decoy step prints counts and `t`, the `dbshell` step prints a status and the refusal, and every value is masked before the first line that can print (C1 pins this).
- **The durations on `fc9decd`:** ordering 535 s, identity 127 s, profile 163 s, discovery 300 s. The shared job took 16 min 32 s on `main`'s run 44416436012.

## 5. Item 3 — AG1 to AG21, and revision 3's additions

- **AG1 to AG21: confirmed as applied.**
  - My script parsed DM-96's 21 pairs from its section 14 and checked them against the brief at `fc9decd`. Each new passage occurs exactly once.
  - Each old passage is gone, except AG9's and AG13's, which lie inside their new passages.
  - The five carried additions (AG16, AG17) are in place:
    - in the carried-items file: Stage B's sameness for notifications, P08's per-member consent limit, AC3's `read_only` and P07's staff path;
    - in the P11 plan: the epoch revocation's revisit.
- **Revision 3's additions: approved.**
  - **D2's rule for the scans** is right, and the split needed it. Without it, the profile and discovery scans would fail on files their jobs no longer write. With it, each scan also covers its job's decoy marker. It drops no secret a job holds: each file a scan no longer reads now exists only in another job, on another runner (section 3's table).
  - **A0's owned paths** for the three scans and their offline tests were the minimum the split needed (AM12-39).
  - **D11's A0 earlier tests:** A0's own search at `eac8443` found no other reader (the record, "The search for earlier tests").
  - **The acceptance checks' wording** names what the classifier really prints: `"full": true`, reason `behavior-or-empty`, as my own run printed for `fc9decd`.

## 6. Item 4 — the corrections C1 and C2

**Approved.** There is nothing in either that I would not merge.

- **Tests only.**
  - C1 changes the three offline test files, and its only removed lines are their three module docstrings.
  - C2 changes two of them and removes nothing.
  - No workflow, scan, setting or application file changes in either.
- **C1 closes F1, F2 and F7's D6a:**
  - the exact `printf` binds each decoy's comment to its own marker variable, and each marker file has one writer;
  - the refused `migrate` names the decoy's marker file;
  - every mask comes before the first line that can print;
  - the `dbshell` and decoy-step sequences are pinned as whole lines, in order, with one `set +e` and one `set -e`;
  - the gate's script runs on 54 wrong results (nine jobs, three wrong results each, in both modes).
- **C2's claim holds.** My `ast` comparison, with suite names mapped, finds:
  - at `5a2f137`, the profile and discovery decoy-step sequences (26 lines each) and `dbshell` sequences (16 each) equal the identity test's;
  - at `c78f297`, the decoy-step sequences had 18 lines, R1's gap.
- **The gate test's subprocess is safe.** It runs the gate's own Python with `sys.executable -I`, only `PATH` and `RESULTS` in its environment, and a 30-second timeout. It runs inside the offline tests, where no credential exists.
- **The limit stands as recorded.** The tests pin text; CI's runs show the behaviour. An edit that leaves every pinned line in place and defeats a check elsewhere can still pass (X4, X5, X9, X14, X15). That is carried to A2 (item 8), which extends these tests.

## 7. Item 5 — F3, the Chromium retry's timeout

**(a), approved with conditions AH1 and AH2.**

**What DM-59 item 7 carried.** Its words: *"Each attempt takes its own `timeout-minutes`, set so that both attempts, the pause and the rendered checks fit in the job's 25 minutes (each failed attempt took about 10 minutes; on a passing run the install takes under a minute and the rendered checks about 5)."*

- So DM-59 set the rule, not the numbers. The consultation says the form is the carried text "its timeouts included". That goes further than the text: 10 and 6 minutes are A0's choice under the rule, and no Dev Manager read them before this read.
- DM-59's premise, "under a minute", was also out of date. A0's own data shows passing installs of 22, 28, 38, 302, 510 and 541 seconds (the record, item 3).

**The open question has an answer.** GitHub's documentation is silent, but the runner's source settles it:

- `StepsRunner.cs`, `RunStepAsync`: when a step's own time limit cancels it, and the job is not cancelled, the step logs "The action '<name>' has timed out after N minutes." and its result is `Failed`;
- `ExecutionContext.cs`, `ApplyContinueOnError`: a `Failed` result with `continue-on-error` true becomes `Outcome = Failed` and `Result = Succeeded`;
- so after a timeout, `steps.chromium.outcome` is `failure`, and the pause and the retry run.

I read this at release v2.338.2, the version the final head's run reports ("Current runner version: '2.338.2'", in the gate's log), and the same code at `main` `7e211dc`. It is the runner's code, not a documented contract. If a later runner changed it, the first attempt would end `cancelled` and the job would fail: never a false pass.

**The options:**

- **(a), accept: yes.** The form meets DM-59's rule, the outcome is now established for the runner in use, and no outcome passes falsely.
- **(b), a deliberate run: no longer needed.** It would take a workflow change made only to force a timeout.
- **(c), widen the timeout now: no.** Under D-07 that is not a correction: no defect in application behaviour, no security boundary, and, after AH1, no false claim the merge rests on.

**The margin is real, though.**

- Before A0 a slow passing install had the whole 25 minutes. Since A0, an install slower than 600 seconds goes to the retry, and the job fails if the retry needs more than 360 seconds.
- 541 seconds has been seen.
- So a slow mirror can now turn a run red that would have passed. Under OD-21 that red run would be diagnosed.
- AH2 carries the check to the next change to the workflow, with a rule, so the data decides. It also asks that change to consider clearing an interrupted `dpkg` before the retry: a first attempt stopped during apt's `dpkg` stage can leave it interrupted (the A0 record's limits).
- **AH1** corrects the record's F3 row, which credits the timeouts to DM-59 and calls the outcome open.

## 8. Item 6 — the manager's D-07 calls

**Agreed, both.** Neither belonged on the consultation list instead.

- **(a) F7's D6a into C1.**
  - A0's acceptance check reads "… and the gate requires each" (the brief, "Acceptance checks", A0).
  - D-07 makes a missing test a correction "when … an acceptance check of the item's brief rests on it".
  - The review graded it a nit, but the rule decides it.
- **(b) C2 widened from five lines to eight.**
  - R1 was a false claim in the record ("the same sequence of whole lines as the identity test's") and a test gap.
  - Making the claim true needed all eight lines, three of which had been pinned only as substrings.
  - It was the same pass, tests only, with no change of design. D-07 lists such a fix for the pre-merge read, and the manager listed it.

## 9. Item 7 — F8, the proof's README

**Approved as written.**

- The sentence: "This keeps the shared job's check that a suite's database refuses another database's marker, with one decoy marker per job, where the shared job's profile and discovery steps refused two and three". It is accurate (section 4).
- F8's other half, "only while F1's binding holds", is now a tested fact (C1's exact `printf` pins), so the sentence need not carry it.

## 10. Item 8 — what is carried or recorded only

**Each is in the right place.**

- **Carried to A2:** F7's D5, the scans' docstrings, C1's N1 to N3 and C2's N-A. A2 adds a fifth job and scan the same way and extends these tests, so it is the right home.
- **Recorded only:**
  - F4 is rightly recorded only: each runner pulls once, and a `429` fails the job loudly (OD-21);
  - F5 and N-B were the manager's wording, now corrected (AM12-42, AM12-45).

**Additions:**

- **AH3, more stale docstrings:** eight more module docstrings, which F6 did not list, still describe the shared job.
- **AH4, X5's description:** the carried entry says "beside X4, X5 and X9", but describes only X4 and X9. C1's N2 named all three.
- **AH5 and AH6, two living records:** `docs/operations/environment-inventory.md` (line 116) and `docs/operations/migration-plan.md` (lines 5 and 6) still name the one job. Fixing them is the supersession sweep (the manager workflow, step 5). The briefs of done items (P06.DB, SV1, SV2, SV3) keep their history and need nothing.
- **At the merge:** A0 completes "Carried to the next change to the Foundation workflow (DM-59)". That entry closes with the merge receipt, and AH2's new section takes its place as the open item.

## 11. Item 9 — the start note's points

**Confirmed. No mismatch.**

- **OD-82** quotes Nathan's words as Dev Manager 5's handover records them, with this session's ID, its creation time from `get_session`, and the start note `a87a6c8`.
- **The register's preface** lists OD-82 among the answers given in the Dev Manager's session.
- **The review log's Sessions row** gives the basis `7383e22`, the read of `55ab2a4`, the environment and the wording point.
- **The handoff** names Dev Manager 6.
- **The wording point:** I checked both corrections in Notion (section 12). The handoff's title, which my note also named, has since been replaced.

## 12. Item 10 — Notion (read only, between 22:43 and 22:57 UTC)

| Page | What I compared | Result |
|---|---|---|
| Implementation Control (last edited 20:35:22 UTC) | The status stamp | "Last matched … at `fc9decd`: C2's delta review recorded; DM-97, A0's pre-merge read, with Nathan". **Match** |
| Implementation Control | "Dev Manager", "Main", "Mistakes log" | Dev Manager 6; `main` at `c2cffbe`; AM12-01 to AM12-45 at `fc9decd`, as the repository holds. **Match** |
| Implementation Control | "Branches" | Six, listed at 20:34 UTC: `claude/dev-manager` at `a87a6c8` and the three session branches. **Match**, also with my `git ls-remote` at 22:36 UTC |
| Dev Manager — reviews and approvals (20:35:12 UTC) | DM-97's row; the Sessions row | DM-97 pending, sent at `fc9decd`; Dev Manager 6's row as the review log has it. **Match** |
| Register copy (05:39:22 UTC) | Its stamp, its preface and its rows | Matched at `90a74e5`. The register file is unchanged from `90a74e5` to `fc9decd`. The preface lists OD-82. There are 82 rows, equal to the repository's once links and file names are normalized: seven rows differ only by the Notion checklist's rewrites of file names. **Match** |
| Work Register `SV4` (SQL) | State, Owner Role, Next Action, Evidence | "In progress"; App Manager 12; DM-97 next, with the brief's revisions described rightly; evidence pinned at `fc9decd`. **Match** |

The repository wins on any difference (OD-27). I found none.

## 13. The merge

**PR57 may merge when all four of these hold:**

1. AH1 and AH2 are applied as given, in the batch that records this disposition. They apply my words, so they need no further read (D-07).
2. The PR run on that batch's head passes all eleven jobs and its gate prints "Application checks passed". The non-Markdown paths must still equal `5a2f137`.
3. Codex's review completes on that head.
4. The pre-merge checklist is filled.

**Already true at `fc9decd`:**

- PR run 44610075506 passed all eleven jobs;
- Codex's code review completed on `fc9decd` with no findings (its summary, 20:36:23 UTC);
- the PR has no review thread.

**What this read covers.** It covers the CI policy's text at `fc9decd`. A further change to the policy before the merge, other than in words I give, needs another read. This read answers the review log's deferred row for AG21.

## 14. The words

Each old passage below occurs exactly once in its file at `fc9decd`. The pairs are applied in order, and each new passage then occurs exactly once (checked by script).

**AH1 — the A0 record, `docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`: F3's disposition row.**

> ```
> | F3 | **For Dev Manager 6's pre-merge read** | The Chromium form, its timeouts included, is the carried text of DM-59 item 7, the Dev Manager's; no outcome gives a false pass. The manager recommends accepting it as carried, with the documentation's silence recorded here, and treating a Mobile run that fails at the Chromium step under OD-21 |
> ```

> ```
> | F3 | **Accepted as carried** (DM-97, option (a)); the first attempt's margin is **carried** to the next change to the Foundation workflow (the carried-items file, DM-97) | The form is DM-59 item 7's: `id: chromium`, `continue-on-error: true`, a pause and one retry, each only `if: steps.chromium.outcome == 'failure'`, each attempt with its own `timeout-minutes`, all inside the job's 25 minutes. The 10 and 6 minutes are A0's, chosen under that rule; DM-59's "on a passing run the install takes under a minute" was out of date (A0 measured 22 to 541 s). GitHub's documentation does not say what outcome a step stopped by its own `timeout-minutes` has, but the runner's source does: it marks the step failed ("has timed out after N minutes"), and with `continue-on-error` its outcome is then `failure`, so the retry runs (`actions/runner`: `RunStepAsync` in `src/Runner.Worker/StepsRunner.cs` and `ApplyContinueOnError` in `src/Runner.Worker/ExecutionContext.cs`, read by Dev Manager 6 at release v2.338.2, the version PR57's run 44610075506 reports, and at `main` `7e211dc`; source code, not a documented contract). No outcome gives a false pass. A Mobile run that fails at the Chromium step is diagnosed under OD-21 |
> ```

**AH2 — the carried-items file, `docs/planning/carried-to-later-items.md`: the Chromium install's margin, for the next change to the Foundation workflow.**

> ```
> ## Carried to the next change to the branch cleanup (M04's exact-head review)
> ```

> ```
> ## Carried to the next change to the Foundation workflow (DM-97)
>
> - **The Chromium install's first attempt** (DM-97, F3; the A0 record, "Exact-head review of A0"). Since SV4 A0 the first attempt of `npx playwright install --with-deps chromium` stops at 10 minutes and the one retry at 6; before A0 the step had no time limit of its own, only the Mobile job's 25 minutes. Passing installs have taken 22 to 541 seconds (the A0 record, item 3), so a passing install slower than 600 seconds now goes to the retry, and the job fails if the retry needs more than 360 seconds, where before A0 it passed. The next change to `.github/workflows/foundation.yml` reads the first attempt's duration in every run of record since A0 (each record states it): if any passing first attempt took more than 480 seconds, or any first attempt was stopped by its time limit, that change raises the Mobile job's `timeout-minutes` and the first attempt's so that both attempts, the pause and the rendered checks still fit, and states the margin; otherwise it records the durations and changes nothing. It also considers running `sudo dpkg --configure -a` before the retry, since an attempt stopped during apt's `dpkg` stage can leave dpkg interrupted. A first attempt stopped by its own time limit has the outcome `failure`, so the retry does run (the runner's source at release v2.338.2; DM-97). Free while the repository is public (OD-51).
>
> ## Carried to the next change to the branch cleanup (M04's exact-head review)
> ```

**AH3 — the carried-items file, `docs/planning/carried-to-later-items.md`: "Carried to SV4", eight more docstrings that describe the shared job.**

> ```
> A2 takes both up if it changes these files; otherwise they move to the next change to the scans.
> ```

> ```
> A2 takes both up if it changes these files; otherwise they move to the next change to the scans. Eight more module docstrings still describe the shared job (DM-97), each taken up by A2 if it changes that file, or else by the next change to it: `proofs/postgres-ordering/tests/test_row_locks_offline.py` (lines 7 and 8, "the Database proof checks job"); `glow_ordering_proof/identity_settings.py`, `profile_settings.py` and `discovery_settings.py` (a "second", "third" or "fourth database in the same disposable PostgreSQL"); `identity_suite.py`, `profile_suite.py` and `discovery_suite.py` (line 3, "On the second", "third" or "fourth disposable database"); and `__main__.py` (lines 20, 24 and 28, the same).
> ```

**AH4 — the carried-items file, `docs/planning/carried-to-later-items.md`: "Carried to SV4", C1's X5.**

> ```
> are not pinned (X9, older than A0); and the gate test runs the gate's script but not the step around it (N3).
> ```

> ```
> are not pinned (X9, older than A0); `fail=0` set again just before `test "$fail" = 0` defeats the decoy step's failure with every test passing (X5); and the gate test runs the gate's script but not the step around it (N3).
> ```

**AH5 — the environment inventory, `docs/operations/environment-inventory.md`: the proof's names.**

> ```
> set only by Database proof checks for its disposable database
> ```

> ```
> set only by the database proof jobs, each for its own disposable database (one job per suite since SV4 A0)
> ```

**AH6 — the migration plan, `docs/operations/migration-plan.md`: where the reviewed migrations run.**

> ```
> The reviewed migrations run only in the Foundation job's
> disposable PostgreSQL and in sessions' throwaway clusters (P06.DB, P06.2).
> ```

> ```
> The reviewed migrations run only in the disposable PostgreSQL of each Foundation
> database proof job (one per suite since SV4 A0) and in sessions' throwaway clusters (P06.DB, P06.2).
> ```

## 15. Checks

- **The environment, by names only:**
  - none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or the three `STREAM_*` names is set;
  - no `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name is set;
  - the three `AWS_*` names are present (OD-76), never read or used.
- **No calls** to Stream, a database, HDE, Railway, Cloudflare or TypeSafe.
- **What I did read:**
  - GitHub, read only, through the GitHub tools;
  - Notion, read only;
  - `actions/runner`'s public source, fetched read only over HTTPS.
- **The code** was read from exports with PyYAML and `ast`, never imported or run.
- **This file** is the only file committed, on `claude/dev-manager`.

Status: complete

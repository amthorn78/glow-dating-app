# P06.DB-C1 prompt — correction pass: the exact-head review's findings

- **Owner:** App Manager 5. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 29 September 2026.**
- **Durable brief:** [P06.DB brief](../planning/p06-db-disposable-postgres-proof.md), revision 2, and its "Sessions" (P06.DB-C1).
  - Work list: the [P06.DB evidence record](../testing/evidence/2026-09-29-p06-db-disposable-postgres-proof.md), "Exact-head review of P06.DB (29 September 2026)": the review's report, verbatim, the manager's verification and the "Disposition".
- **Where the result goes:**
  - the session fixes the proof package, brings its README into line, corrects the named statements of the evidence record in place, and adds a section at the end of the record, "P06.DB-C1 corrections";
  - the Foundation run on the session's last code commit becomes the run of record for the stress numbers;
  - the manager adds its verification there, records the outcome in the brief's "Sessions", and settles the P11 plan's DB06 limit.
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v6: Opus 5.5, high.** Effort score 2.22 (confidence 0.82); rung probabilities low 0.00, medium 0.02, high 0.74, extra high 0.24, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.01, Opus 5.5 0.99 (confidence 0.98). Sent 2026-09-29T06:39:25Z. Nathan picks the cell.
  - **Nathan's pick: Opus 5.5 at high**, started 29 September. This line was added after the prompt was given; the body Nathan pasted is unchanged.
- **Result:** done on 29 September. F1 to F4 are fixed, each with a test, and Foundation run 36534514283 on `4280770` is the run of record; the evidence record explains its run-level `cancelled` label (AM5-14). The manager verified the report and integrated the branch at `ea21ac8`; see the evidence record, "Manager verification of P06.DB-C1". C1's exact-head review follows.
- **A second run, 4 October:** Nathan started this prompt again, on Opus 5.5 at extra high, in place of C1's review. Its start gate checks only its start commit, so it could not tell that the work was done (AM5-15), and the session made the pass again on `claude/magical-goldberg-ie0j16`. The manager recorded it and did not integrate it; see the evidence record, "A second run of the C1 correction prompt". **This prompt is done: do not run it again.**
- **No Dev Manager read is needed:** the job's generated password is not credential use in the charter's sense (DM-08 7.2), the session takes no live provider action, and nothing here departs from the brief's D3, D4 or D5.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and the session calls no provider.
- **It runs alone** (OD-29, the linear process). Its exact-head review follows.
- **Deletion condition:** prune after P06.DB's PR merges and the evidence record holds the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **implementation session for P06.DB-C1**, the correction pass on P06.DB, the early disposable-PostgreSQL proof of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<START_SHA>`.

P06.DB built `proofs/postgres-ordering/`, a proof package that orders message-send authorizations against every revocation of contact on a real PostgreSQL 17 database, and the Foundation job "Database proof checks", which starts that database inside the job and runs the proof. Its run of record is Foundation run 36520940933. The exact-head review of the package, at `6f5866d`, asked for changes, narrowly. The design, the job and its credential handling are sound, and nothing in the run is a false pass of the ordering guarantees. But:

- **F1, should fix, in a correction class** ("make DB06's mark claim more than the run shows"): the stress run's per-race overlap count reads every race's log rows at the same iteration number, so only the first race's count is established, and the duplicates race never measured its own;
- **F2, should fix:** the commit-order oracle's rule O2 misses a send stored at the version a revocation set;
- **F3 and F4, nits:** a negative control counts as "failed as intended" on any failure, not only its own signal; and the lock-wait observation does not record which backend blocks the waiting connection;
- **F5 and F6** are the manager's, and are done.

**You fix F1 to F4, offline, and rerun the job by pushing your branch.**

- Nathan started you manually and will relay your report to the manager (App Manager 5). You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- Your boundary is scope:
  - write only your owned paths (section 5);
  - push only your own session branch. Each push runs the Foundation workflow on your branch; read those runs if your tools can. On GitHub do nothing else: no pull request, no PR comments, no re-runs, no workflow dispatches. Change nothing in Notion.
- **Never:**
  - dump the environment, or print, echo or log the proof database's password, in any form;
  - connect to any database other than a disposable one that you or the job start for this proof (brief, D4). Never connect to Stream, HDE, Railway or any other provider;
  - run `playwright install` or `eas`;
  - run Django's `migrate` anywhere but against a disposable proof database, from the proof's own settings;
  - change anything under `services/`.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. No `PG*`, `PROOF_DB_*` or `STREAM_*` name should be set: `compgen -e | grep -E '^(PG|PROOF_DB_|STREAM_)'` prints names only. If any is present, report its name first in your report, never read or use its value, and run every proof command in a clean process environment that lacks it.
3. The pinned toolchain is in `$HOME/.local/bin`, including Python 3.12.14. Put `$HOME/.local/bin` first on PATH, then record `command -v python3.12` and its version.
4. Run the proof's commands in a clean process environment, as its README's "Install" and "Checks (offline)" sections show: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8` plus only the proof's own variables. Installs get the proxy and CA variables by reference, never printed.
5. **What a local database can use (brief, D4):** record whether `docker info` succeeds (its exit status only), and `command -v initdb pg_ctl postgres pg_isready psql`.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2
git merge --ff-only <START_SHA>          # on your own session branch
git rev-parse HEAD                       # must print <START_SHA>
git diff --stat 6f5866d505c5fd94ad9224ab9b23ba4e3bafaef5 HEAD -- proofs/ .github/   # must print nothing
```

The last command shows that the package and the workflow are unchanged since the reviewed head, so the review's line numbers still apply. If any check fails, stop and report.

Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`;
- the P06.DB brief, `docs/planning/p06-db-disposable-postgres-proof.md` (revision 2): "What P06.DB proves", D1 to D6 with item 6, the brief's rules and "Sessions";
- the evidence record, `docs/testing/evidence/2026-09-29-p06-db-disposable-postgres-proof.md`:
  - "Exact-head review of P06.DB (29 September 2026)" is your work list: the report, verbatim, the manager's verification and the "Disposition";
  - "P06.DB implementation" is the session's record, with the statements you correct in place;
  - "Manager verification of P06.DB", which records the checks your change must keep;
- `proofs/postgres-ordering/README.md` and the whole package under `proofs/postgres-ordering/`;
- `.github/workflows/foundation.yml`, the `database` job, which you do not change.

## 3. The work

The review's findings are numbered F1 to F6 in the evidence record, each with its `file:line`, a scenario and a suggested fix. Use the suggested fix unless you find a better one, and say why if you do. The requirements below are the manager's disposition, and they stand either way.

1. **F1: each race measures its own overlaps.** Do this first.
   - Every per-iteration read of the stress run selects only the race's own rows: `_intervals` (`glow_ordering_proof/stress.py:111`) by the race's `case_id` as well as the run tag and the iteration, and any other per-iteration read, such as the per-iteration oracle check, the same way.
   - An iteration overlaps when two of its own writers' database intervals intersect:
     - in a two-writer race, the send's and the revocation's;
     - in `race.racing_duplicates`, the two sends';
     - in `race.opposing_writers`, the send's and any revocation's.
   - **The floors stay:** 50 iterations and 10 measured overlaps per race. If a race cannot reach 10 real overlaps within its budget, do not weaken the floor or the measure. You may change the construction's head start, or the budget's 200 iterations and 30 seconds within the job's timeout, with the reason recorded. If a race still cannot reach its floor, keep it failing and report it.
   - **Tests,** offline and without a database. Each fails without the fix:
     - `_overlapped` for each race kind, including the duplicates race with intersecting and with disjoint intervals;
     - the per-race selection: rows of two races at the same iteration count only for their own race.
   - **The rerun.** Push your branch; the job's run on your last code commit is the new run of record for the stress numbers. Report each race's iterations, measured overlaps and seconds, and each race's outcomes.
   - **The records.** Correct these statements in place, each marked "(corrected in P06.DB-C1; the exact-head review's F1)". Each must say what the first run established (the first race's 200 of 200), what it did not (the other eleven races' counts, and the duplicates race's own overlap, never measured), and where the corrected counts are (your section):
     - in the evidence record's "P06.DB implementation" section: the DB06 bullet of "Summary" ("200 measured overlaps"); "How an overlap is measured (6.3)"; the stress table's overlaps column; the two "200 overlaps each" in the local-runs table; and the limits bullet under "Deviations, open questions and limits";
     - in the package's `README.md`: the stress run's bullet under "How a pass is judged", and the overlap line under "Limits".
2. **F2: O2 catches any send after a contact revocation.** In `glow_ordering_proof/oracle.py` (`:187` to `:196`), O2 flags every applied contact revocation of the send's match, meaning a block or unmatch whose log row carries a contact version, that committed before or with the send, whatever its version. O6 stays.
   - In P06.DB a block or unmatch is never undone for its match (an unblock leaves the match `restricted`, and there is no rematch), so the stronger rule must hold for every row the design writes. Say so in the rule's docstring and the README.
   - **Tests,** on constructed rows (replace the oracle's fetches; no database):
     - a submission at v2 that committed after a block at v2 is an O2 violation;
     - one that committed before the block is not;
     - the existing rules still flag what they flagged.
   - In the rerun, the design's rows still show zero violations, and each control the oracle caught before still shows its oracle violations.
3. **F3: a control fails as intended only by its own signal** (`glow_ordering_proof/controls.py:163`, `:186`).
   - Each control declares the signal its broken switch must produce. The evidence record's controls table shows each control's signal in the run of record: an unobserved wait with a stale commit and an oracle violation, an oracle violation at the first failing iteration, the expected refusal missing, or a deadlock.
   - A control counts as failed as intended only when its declared signal is present. A harness error, or any other failure, counts as a control that did not fail as intended, which fails the job.
   - **Tests:**
     - a control whose case fails for another reason is not counted;
     - each control's declared signal is one its broken switch can produce.
4. **F4: a forced case records which backend blocks the waiting connection** (`glow_ordering_proof/observe.py:168` to `:223`, `cases.py` `forced`).
   - Capture the holder's backend PID, as the arriver's is captured (`on_begin`).
   - When the wait is observed, read `pg_blocking_pids(<the arriver's pid>)` and record it.
   - Require the holder's PID to be among the blockers: a wait on any other backend does not count as observed.
   - **Test:** the decision without a database. A wait whose blockers do not include the holder is not observed.

**Not in this pass:** anything else. F5 and F6 are done. The manager's observation 3, that the oracle cannot see a stale client version, stays a recorded limit. If you find more, report it with its class. Fix it here only if it could do one of these, and then with a test:

- let a send authorization commit after a revocation that invalidates it without the suite failing;
- let a password or connection value reach a log, an artifact or a file outside the job's temporary directory;
- let the job or the proof connect to anything but its own disposable database;
- make DB06's or DB09's mark claim more than the run shows.

**Local runs** [D4]. You may iterate against a disposable database in your own sandbox, as the implementation session did:

- `docker run` with the job's recipe if Docker works;
- otherwise a throwaway cluster from local binaries (`initdb` in a temporary directory, listening only on a Unix socket or loopback), recording its version;
- otherwise iterate through CI.

The same rules hold: a generated password, loopback or a socket only, removed afterwards, and no forbidden or `PG*` name present. Local runs are iteration, not evidence: the record rests on the CI job's run. Your report says which you used.

**If the design itself fails.** If a corrected measure or rule shows that the brief's design is wrong, not your code, do not redesign past D5. Keep the failing case, report it with the observations and your proposed change, and stop there. The manager takes a design change to the Dev Manager.

**Rules for every fix:**

- **A test for each fix.** Each item you fix in code gets an offline test that fails without the fix and passes with it. Say which test covers which item.
- **Evidence comes from the database.** Every guarantee is judged by what PostgreSQL recorded (rows, commit times, lock waits), never by what the test code believes it did.
- **No weakened check.** Never loosen a case, the oracle, a control's signal or a floor to make a run pass. A flaky case is a finding (OD-21), not a retry.
- **No password anywhere:** not in the diff, a log line, the evidence record or your report.
- **The API is untouched.** Nothing under `services/` changes, and the proof imports `glow_persistence` without monkey-patching its models or migrations.
- **No dependency change.** `requirements.in`, `requirements-dev.in`, both `.lock` files and the dependency lists in `pyproject.toml` stay as they are.
- **The workflow is unchanged.** If a fix seems to need a workflow change (for example, its timeout), leave that item and report why.

## 4. Checks

Report the exact commands and results.

1. `git diff --check <START_SHA> HEAD`, and `git diff --name-only <START_SHA> HEAD`: only owned paths changed.
2. Classification with the trusted policy from `main`, run outside the tree, as root `AGENTS.md` requires. Expected: full scope.

   ```bash
   base=$(git rev-parse origin/main); policy_dir=$(mktemp -d)
   git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
   python3 -I "$policy_dir/change_scope.py" --base <START_SHA> --head "$(git rev-parse HEAD)" --merge-base
   ```

3. The installs from the locks, with `pip install --require-hashes`, and `pip check`, in a clean process.
4. The offline checks, with the README's commands:
   - the unit tests, with the counts at the start (the implementation left 40) and at your head;
   - Ruff check and format;
   - mypy, with its file count;
   - the Django pin test;
   - `services/api`'s toolchain pin test (`cd services/api && python3.12 -m unittest tests.test_toolchain_pins`).
5. Your local runs, if any: which database, its version, and the results, marked "iteration, not evidence".
6. **The Foundation run on your last code commit:** its run ID, each job's conclusion (eight jobs, "Database proof checks" included), and the gate's log line, which must be `Application checks passed`.
   - A push that changes only Markdown skips the application jobs by the CI policy's design. If your last commit changes only the record, the evidence of record is the push run of your last code commit, and your record says so, as the implementation's did.
   - From the database job's log:
     - the image digest and `SELECT version()`, and `makemigrations --check`;
     - each case with its observed waits and blocking backends;
     - the oracle's result over every row;
     - each race's seed, iterations and measured overlaps;
     - each control's declared signal and whether it was met (for stress controls, the first failing iteration);
     - the container's removal.
   - Confirm that the log shows no password, and no `***` mask where a password would be. If your tools cannot read the run, say so; re-run or dispatch nothing.
7. A secret scan over your whole diff: no secret, token, API key, password or email address.

## 5. Owned paths, push and records

- **You may change:**
  - `proofs/postgres-ordering/**`, except the dependency files named above;
  - `docs/testing/evidence/2026-09-29-p06-db-disposable-postgres-proof.md`: your new section at its end, and the in-place corrections that section 3 item 1 names. Every other part stays byte-identical, in particular "Manager verification of P06.DB (App Manager 5, 29 September 2026)" and "Exact-head review of P06.DB (29 September 2026)", each with everything under it.
- **Nothing else,** including the workflow, the brief, the CI policy, the P11 acceptance plan, `services/`, `scripts/`, `apps/`, `packages/`, the root `.gitignore` and every other document. Report any other change you think is needed.
- **Commit and push** your session branch. Don't open a pull request.
- **Your section of the evidence record,** "P06.DB-C1 corrections", at its end:
  - the start SHA, your head, your branch and the new run of record;
  - for F1 to F4: fixed (`file:line` and its test) or left (the reason);
  - the records you corrected;
  - the new run's numbers: each race's iterations, measured overlaps and seconds; the oracle; each control's signal; the observed waits with their blocking backends;
  - local runs, marked "iteration, not evidence";
  - every check, with its exact results;
  - deviations and limits;
  - what the exact-head review must know: the rules that changed.

## 6. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<START_SHA>`);
- the environment check, and what a local database could use;
- your branch, head SHA and tree, and the changed paths;
- for F1 to F4: fixed (`file:line` and the test) or left (the reason);
- the records corrections;
- every check, with its exact results, and the run of record's details from section 4 item 6;
- which local database you used, if any;
- deviations, limits, and what the exact-head review must know.

Skipped or unavailable checks are not passes.

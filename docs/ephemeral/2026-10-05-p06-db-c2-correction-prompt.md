# P06.DB-C2 prompt — correction pass: the run's marker (Codex's CX3)

- **Owner:** App Manager 5. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 2, 5 October 2026.** Revision 1 (`d50f334`) never ran: DM-11 approved its one departure from DM-10 with conditions, and revision 2 replaces the departure with DM-11's words (section 3, item 3) and quotes DM-11's note on 2.4 (section 3, item 4).
- **Durable brief:** [P06.DB brief](../planning/p06-db-disposable-postgres-proof.md), revision 5: D1's "The run's marker" and "DM-10's conditions" with DM-11's notes, D3's item 5, D4's condition 2, and "Sessions" (P06.DB-C2).
  - Work list: the [P06.DB evidence record](../testing/evidence/2026-09-29-p06-db-disposable-postgres-proof.md), "Codex's second code review, of `9bcec21`": the finding, the manager's verification and the disposition; the [DM-10 report](../continuity/dev-manager/reviews/2026-10-05-dm-10-p06-db-cx3-design-read.md), item 2; and the [DM-11 report](../continuity/dev-manager/reviews/2026-10-05-dm-11-p06-db-c2-prompt-read.md), items 1 and 2.
- **Where the result goes:**
  - the session changes the proof package, its README and the Foundation workflow's `database` job, and adds a section at the end of the evidence record, "P06.DB-C2 corrections";
  - the Foundation run on the session's last code commit becomes the run of record;
  - the manager adds its verification there, records the outcome in the brief's "Sessions", and applies the CI policy's sentence that DM-10 item 4 gives.
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v6: Opus 5.5, high.** Effort score 2.03 (confidence 0.81); rung probabilities low 0.00, medium 0.13, high 0.72, extra high 0.14, max 0.01, ultracode 0.00. Model probabilities Fable 5.1 0.02, Opus 5.5 0.98 (confidence 0.97). Sent 2026-10-05T03:28:30Z. Nathan picks the cell.
  - Revision 1's reading, sent 2026-10-05T01:58:22Z, was the same cell (score 1.92). Revision 1 was never given to Nathan to run.
  - **Nathan's pick:** not recorded: the relay of the session's report did not name it.
- **The Dev Manager's read:** DM-10 approved the design with conditions 2.1 to 2.5, and this prompt quotes 2.1 to 2.4 as written. Its one departure, from 2.3's query (section 3, item 3), is in DM-11's words, and section 3, item 4 quotes DM-11's note on 2.4. DM-11 approved them: applied as written, this prompt needs no further read (DM-03 G2).
- **Result:** done on 5 October, from revision 2. Branch `claude/ecstatic-feynman-749ccu`, code head `43d8ca4`, final head `1178dfa`; Foundation run 37262466651 on the code head is the run of record. The manager verified it and integrated it at `369d03c`: the evidence record, "P06.DB-C2 corrections" and "Manager verification of P06.DB-C2".
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and the session calls no provider.
- **It runs alone** (OD-29, the linear process). Its exact-head review follows.
- **Deletion condition:** prune after P06.DB's PR merges and the evidence record holds the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **implementation session for P06.DB-C2**, the second correction pass on P06.DB, the early disposable-PostgreSQL proof of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 2, from commit `<START_SHA>`.

P06.DB built `proofs/postgres-ordering/`, a proof package that orders message-send authorizations against every revocation of contact on a real PostgreSQL 17 database, and the Foundation job "Database proof checks", which starts that database inside the job and runs the proof. Two exact-head reviews approved it, the second at `ea21ac8` (C1). Then Codex's code review of the pull request found a P1, **CX3**, which the manager confirmed:

- the proof's only database guard is its host check, which accepts `127.0.0.1`, `localhost`, `::1` or any Unix-socket directory (`glow_ordering_proof/environment.py:108` to `112`);
- the settings build Django's database from those options at import (`settings.py:28` to `42`), and the documented first command, `migrate`, changes whatever database is there before `run`'s server checks;
- a loopback host names a route, not a database, so an SSH-forwarded or other local server passes. The CI job is safe by construction; a misdirected local run is not.

The fix is the brief's "run's marker": whoever creates the disposable database sets a marker generated for the run as the database's comment, and the proof refuses any database that does not carry it. The Dev Manager approved it with conditions (DM-10), and the brief quotes them.

**You add the run's marker, offline, and rerun the job by pushing your branch.**

- Nathan started you manually and will relay your report to the manager (App Manager 5). You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- Your boundary is scope:
  - write only your owned paths (section 5);
  - push only your own session branch. Each push runs the Foundation workflow on your branch; read those runs if your tools can. On GitHub do nothing else: no pull request, no PR comments, no re-runs, no workflow dispatches. Change nothing in Notion.
- **Never:**
  - dump the environment, or print, echo or log the proof database's passwords or the run's marker, in any form;
  - connect to any database other than a disposable one that you or the job start for this proof (brief, D4), or set a comment on any other database. Never connect to Stream, HDE, Railway or any other provider;
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
git diff --stat ea21ac8577b83158be1f941b93dbef411bece41f HEAD -- proofs/postgres-ordering/glow_ordering_proof proofs/postgres-ordering/tests .github/   # must print nothing
git diff --stat <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- proofs/ .github/   # must print nothing
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-09-29-p06-db-disposable-postgres-proof.md | grep -c '^## P06.DB-C2 corrections'   # must print 0
```

- The third command shows that the package's code, its tests and the workflow are unchanged since C1's reviewed head, so the cited line numbers apply.
- The last two check the live manager branch. If either fails, this pass has already landed: this prompt is stale, so stop and report (the manager workflow, step 3, AM5-15).
- If any check fails, stop and report.

Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`;
- the P06.DB brief, `docs/planning/p06-db-disposable-postgres-proof.md` (revision 5): D1 with "The run's marker" and "DM-10's conditions", D3 with its item 5, D4, D5, item 6, the brief's rules and "Sessions";
- the evidence record, `docs/testing/evidence/2026-09-29-p06-db-disposable-postgres-proof.md`: "Codex's review of PR28's final head" with its subsection "Codex's second code review, of `9bcec21`", and "P06.DB-C1 corrections", whose run of record your run must match;
- the DM-10 report, `docs/continuity/dev-manager/reviews/2026-10-05-dm-10-p06-db-cx3-design-read.md`, and the DM-11 report, `docs/continuity/dev-manager/reviews/2026-10-05-dm-11-p06-db-c2-prompt-read.md`;
- `proofs/postgres-ordering/README.md` and the whole package under `proofs/postgres-ordering/`;
- `.github/workflows/foundation.yml`, the `database` job.

## 3. The work

The Dev Manager's conditions 2.1 to 2.4, quoted from the brief's D1, are requirements. Where this section adds detail, the condition's words still stand.

1. **The marker's form** (DM-10, 2.1): *"`PROOF_DB_MARKER` must be exactly 32 lowercase hexadecimal characters (`secrets.token_hex(16)`). Otherwise the settings refuse at import, like the other `PROOF_DB_*` names. Empty, short, padded or prefixed values are refused, and the comparison is of the whole comment string. Offline tests show each refusal. Without this, an empty marker and the bare comment `glow-ordering-proof:` would match."*
   - `PROOF_DB_MARKER` joins the proof's own names in `environment.py`, and its refusal names the variable, never the value.
   - The expected comment is exactly `glow-ordering-proof:` followed by the marker.
2. **The check** (DM-10, 2.2): *"It is registered in a module that every management command loads: the proof's settings or the installed app's `ready`, not `__main__`. It reads `shobj_description(oid, 'pg_database')` for `current_database()`. On a mismatch, or a missing or null comment, it closes the connection through Django (`connection.close()`), so the wrapper does not keep it, then raises an exception that ends the command with a non-zero status. An offline test with a fake cursor shows the handler connected and refusing. The refusal names `PROOF_DB_MARKER` and never a value."*
   - It runs on every new connection, and before it the connection runs nothing but its own session settings: no other statement, no transaction that writes, no lock.
   - It applies to every command that uses the proof's settings: `migrate`, `makemigrations --check --dry-run`, `facts` and `run`.
   - **Tests,** offline, with a fake connection and cursor:
     - a matching comment passes;
     - a different comment, a comment with anything before or after the expected string, a null comment and no row each refuse, close the connection and end with a non-zero status;
     - no refusal message contains a value.
3. **The CI step** (DM-10, 2.3): *"Before the migrations, the step runs `migrate` with a different well-formed marker; it requires a non-zero exit and the refusal message; and, as the superuser inside the container, it checks that the proof's database has no relation in its schemas: zero rows in `pg_class` joined to `pg_namespace`, excluding `pg_catalog` and `information_schema`; in particular, no `django_migrations`. A step that only checks the exit code would pass if `migrate` failed for another reason after creating a table."*
   - **The one departure, which DM-11 approved with these words.** Every PostgreSQL database keeps the toast tables of its own catalogs in the schema `pg_toast`, so the query as quoted counts PostgreSQL's relations even in a new database. The step therefore runs, as the superuser inside the container and with `psql -d` naming the proof's database (never `postgres`), a count of `pg_class` rows joined to `pg_namespace` per schema, before and after the wrong-marker `migrate`. It requires:
     - every schema's count after equals its count before, `pg_toast` included;
     - the count over every schema except `information_schema` and those for which `starts_with(nspname, 'pg_')` is true is zero, before and after;
     - `to_regclass('public.django_migrations')` is null after.

     The step prints both per-schema tables once. It prints no name of a role, password or marker.
4. **The marker in the job** (DM-10, 2.4): *"It is generated in the credentials step and masked with `::add-mask::` as that step's first output (cheap, and it keeps logs uniform). It reaches the proof only through `PROOF_DB_MARKER` on the steps that need it. The README's local recipe sets it with `COMMENT ON DATABASE` right after creating the database, with a new marker for each new database. It says the marker does not replace the reused-database guard carried to P06.2."*
   - The step that creates the role and its database also sets the database's comment, as the superuser inside the container, from the file it already reads, so that nothing prints the statement.
   - **DM-11's note on 2.4,** in its words, which C2's exact-head review checks in the workflow diff. 2.4 says the marker reaches the proof "only through `PROOF_DB_MARKER` on the steps that need it". In GitHub Actions, that means:
     - each step that needs the marker reads it from the job's protected temporary directory into the variable for its own commands;
     - never through `$GITHUB_ENV`, which would hand it to every later step, the upload step included;
     - never through a step output (`$GITHUB_OUTPUT`), which the runner withholds once the value is masked.
   - Only the `database` job changes. Every other job, and the gate, stay byte-identical.
   - The removal step also removes any file that holds the marker.
5. **The README:** the local recipe (2.4), the settings' variables, the CI job's description and a line in "Limits" saying that the marker ties the proof to the database created for the run. The marker does not replace the reused-database guard carried to P06.2.

**The evidence stays the same** (DM-10, 2.5, which the exact-head review checks): the new run of record shows the same plan as `ea21ac8`: 55 cases, 10 controls, the same races and floors; 55 of 55 passed, every control met, 0 design violations; every forced wait observed with its holder. Do not change any race, case, control, floor or the reference design. If the marker seems to need such a change, stop and report: that is a departure, and it goes back to the Dev Manager.

**Not in this pass:** anything else. CX1 and CX2 stay carried to P06.2, and so do the reused-database guard (R2), per-order counts (R1) and the tests for R3 and R4. If you find more, report it with its class. Fix it here only if it could do one of these, and then with a test:

- let a send authorization commit after a revocation that invalidates it without the suite failing;
- let a password, the marker or a connection value reach a log, an artifact or a file outside the job's temporary directory;
- let the job or the proof connect to anything but its own disposable database;
- make DB06's or DB09's mark claim more than the run shows.

**Local runs** (brief, D4). You may iterate against a disposable database in your own sandbox:

- `docker run` with the job's recipe if Docker works;
- otherwise a throwaway cluster from local binaries (`initdb` in a temporary directory, listening only on a Unix socket or loopback), recording its version;
- otherwise iterate through CI.

The same rules hold: a generated password and a new marker, loopback or a socket only, removed afterwards, and no forbidden or `PG*` name present. Local runs are iteration, not evidence: the record rests on the CI job's run. Your report says which you used.

**Rules for every change:**

- **A test for each change.** Each item you change in code gets an offline test that fails without the change and passes with it. Say which test covers which item.
- **Evidence comes from the database.** Every guarantee is judged by what PostgreSQL recorded, never by what the test code believes it did.
- **No weakened check.** Never loosen a case, the oracle, a control's signal or a floor to make a run pass. A flaky case is a finding (OD-21), not a retry.
- **No password or marker anywhere:** not in the diff, a log line, the evidence record or your report.
- **The API is untouched.** Nothing under `services/` changes, and the proof imports `glow_persistence` without monkey-patching its models or migrations.
- **No dependency change.** `requirements.in`, `requirements-dev.in`, both `.lock` files and the dependency lists in `pyproject.toml` stay as they are.

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
   - the unit tests, with the counts at the start (C1 left 82) and at your head;
   - Ruff check and format;
   - mypy, with its file count;
   - the Django pin test;
   - `services/api`'s toolchain pin test (`cd services/api && python3.12 -m unittest tests.test_toolchain_pins`).
5. Your local runs, if any: which database, its version, and the results, marked "iteration, not evidence".
6. **The Foundation run on your last code commit:** its run ID, each job's conclusion (eight jobs, "Database proof checks" included), and the gate's log line, which must be `Application checks passed`.
   - **Wait before pushing again.** After pushing your last code commit, push nothing more to your branch until that commit's Foundation run has finished. Runs of the same branch cancel each other (the CI policy), so an early records push can cancel the code run or leave it marked `cancelled` (the manager workflow, step 3; AM5-14).
   - A push that changes only Markdown skips the application jobs by the CI policy's design. If your last commit changes only the record, the evidence of record is the push run of your last code commit, and your record says so.
   - From the database job's log:
     - the wrong-marker step: its exit status, the refusal line and the relation counts per schema, before and after;
     - the image digest and `SELECT version()`, and `makemigrations --check`;
     - each case with its observed waits and blocking backends;
     - the oracle's result over every row;
     - each race's seed, iterations and measured overlaps;
     - each control's declared signal and whether it was met;
     - the container's removal.
   - Confirm that the log shows no password and no marker, and no `***` mask where either would be. If your tools cannot read the run, say so; re-run or dispatch nothing.
7. A secret scan over your whole diff: no secret, token, API key, password, marker value or email address.

## 5. Owned paths, push and records

- **You may change:**
  - `proofs/postgres-ordering/**`, except the dependency files named above;
  - `.github/workflows/foundation.yml`: the `database` job only;
  - `docs/testing/evidence/2026-09-29-p06-db-disposable-postgres-proof.md`: your new section at its end. Every other part stays byte-identical.
- **Nothing else,** including the brief, the CI policy, the P11 acceptance plan, `services/`, `scripts/`, `apps/`, `packages/`, the root `.gitignore` and every other document. Report any other change you think is needed.
- **Commit and push** your session branch. Don't open a pull request.
- **Your section of the evidence record,** "P06.DB-C2 corrections", at its end:
  - the start SHA, your head, your branch and the new run of record;
  - for items 1 to 5 of section 3: done (`file:line` and its test) or left (the reason);
  - the wrong-marker step's result, with the relation counts per schema, before and after;
  - the new run's numbers against C1's run of record: cases, controls, each race's iterations, measured overlaps and seconds, the oracle, and the observed waits with their blocking backends;
  - local runs, marked "iteration, not evidence";
  - every check, with its exact results;
  - deviations and limits;
  - what the exact-head review must know, with DM-10's 2.5 and DM-11's note on 2.4.

## 6. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 2, from commit `<START_SHA>`);
- the environment check, and what a local database could use;
- your branch, head SHA and tree, and the changed paths;
- for items 1 to 5 of section 3: done (`file:line` and the test) or left (the reason);
- every check, with its exact results, and the run of record's details from section 4 item 6;
- which local database you used, if any;
- deviations, limits, and what the exact-head review must know.

Skipped or unavailable checks are not passes.

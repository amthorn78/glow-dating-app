# P06.DB prompt — the early disposable-PostgreSQL proof

- **Owner:** App Manager 5. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 29 September 2026.**
- **Durable brief:** [P06.DB brief](../planning/p06-db-disposable-postgres-proof.md), revision 2, which applies the Dev Manager's read of revision 1 as written ([DM-08 report](../continuity/dev-manager/reviews/2026-09-29-dm-08-p06-db-brief.md); its disposition in the [review log](../continuity/dev-manager/README.md), "DM-08").
- **Where the result goes:**
  - the session writes the proof package, the Foundation job and a new evidence record;
  - the manager verifies the report, integrates the branch into PR28, adds its verification to the evidence record, updates the CI policy (DM-08 7.1) and the P11 plan's DB06 and DB09 marks (brief, D6), and records the outcome.
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v6: Fable 5.1, max.** Effort score 3.63 (confidence 0.74); rung probabilities low 0.00, medium 0.00, high 0.03, extra high 0.30, max 0.66, ultracode 0.01. Model probabilities Fable 5.1 0.86, Opus 5.5 0.14 (confidence 0.72). Sent 2026-09-29T03:07:43Z. Nathan picks the cell.
  - **Nathan's pick: Fable 5.1 at ultracode**, in his words *"Fable Max Ultracode"*, started 29 September. This line was added after the prompt was given; the body Nathan pasted is unchanged.
- **No Dev Manager read is needed** (DM-08 7.2): the password the job generates is not credential use in the charter's sense (no external system, no stored secret), and the session takes no live provider action. A prompt that departs from the brief and DM-08 on D3, D4 or D5 would go back to the Dev Manager; this one does not.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and the session calls no provider.
- **It runs alone** (OD-29, the linear process). Its exact-head code and security review follows.
- **Deletion condition:** prune after P06.DB's PR merges and the evidence record holds the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **implementation session for P06.DB**, the early disposable-PostgreSQL proof of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<START_SHA>`.

Nathan approved P06.DB on 25 September 2026 (OD-17): *"Use a disposable PostgreSQL instance in CI to prove send-versus-block ordering and sign-in against real database behavior before P06.2. It must have no connection to a shared or production database. Record what the proof tested and its result, then dispose of the database."*

The app's persistence schema, `services/api/glow_persistence`, has reviewed migrations that have never been applied to a real database; the API itself runs on Django's dummy backend and refuses every connection name. P06.2 will build the server-side send path, and it rests on the ordering you prove. **You build the proof:** an isolated package, `proofs/postgres-ordering/`, and one new Foundation job, "Database proof checks", that starts a disposable PostgreSQL 17 database inside the job, applies the migrations, and proves that one transaction boundary orders send authorizations against every revocation of contact, plus a minimal sign-in.

The brief, revision 2, is your specification. Its design choices D1 to D6 and item 6 were read by the Dev Manager (DM-08) and are settled: build them as written. Where this prompt and the brief differ, the brief wins; report the difference.

- Nathan started you manually and will relay your report to the manager (App Manager 5). You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- Your boundary is scope:
  - write only your owned paths (section 5);
  - push only your own session branch. Each push runs the Foundation workflow on your branch; read those runs if your tools can. On GitHub do nothing else: no pull request, no PR comments, no re-runs, no workflow dispatches. Change nothing in Notion.
- **Never:**
  - dump the environment, or print, echo or log the proof database's password, in any form;
  - connect to any database other than a disposable one that you or the job start for this proof (brief, D4). Never connect to Stream, HDE, Railway or any other provider;
  - run `playwright install` or `eas`;
  - run Django's `migrate` anywhere but against a disposable proof database, from the proof's own settings. That is P06.DB's setup (PF01 §6: *"Applying migrations is setup there, not DB01 acceptance"*); never against any other database, and never with the API's settings;
  - change anything under `services/`: no model, migration, setting, guard or test. A reviewed migration that fails on PostgreSQL is a finding: stop and report it.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. No `PG*` name may be set: `env | cut -d= -f1 | grep '^PG' || echo "no PG names"`. If any is present, report its name, never read its value, and run every proof command in a clean process environment that lacks it (item 5).
3. `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` should be absent: `for n in STREAM_APP_ID STREAM_API_KEY STREAM_API_SECRET; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, report its name first in your report, never read or use its value, and continue.
4. The pinned toolchain is in `$HOME/.local/bin` (Python 3.12.14; `scripts/bootstrap-toolchain.sh`). Put `$HOME/.local/bin` first on PATH, then record `command -v python3.12` and its version.
5. Run the proof's commands in a clean process environment, as the Stream proof's README does: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8` plus only the proof's own variables. Installs get the proxy and CA variables by reference, never printed.
6. **What a local database can use (brief, D4):** record whether `docker info` succeeds (its exit status only), and `command -v initdb pg_ctl postgres pg_isready psql`.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2
git merge --ff-only <START_SHA>          # on your own session branch
git rev-parse HEAD                       # must print <START_SHA>
test ! -e proofs/postgres-ordering && echo "no proof package yet"
```

If a check fails, stop and report.

Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`;
- the P06.DB brief, `docs/planning/p06-db-disposable-postgres-proof.md` (revision 2), and the DM-08 report, `docs/continuity/dev-manager/reviews/2026-09-29-dm-08-p06-db-brief.md`;
- PF01 §6, "Early disposable-PostgreSQL proof" (`docs/pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md`), and OD-17 in `docs/continuity/owner-directions.md`;
- `docs/testing/p11-deferred-acceptance.md`: DB06 and DB09 and the rows that name them (lines 85, 90, 112 and 138 to 140);
- `docs/architecture/data-model.md`: the auth mapping and `auth_session_ref`, the lock-order paragraph, and the unit-of-work table;
- `services/api/glow_persistence/`: `models.py` (`AppAccount`, `AccountSession`, `Block`, `Match`, `ChatBinding`, `MessageSubmission`, `OutboxEvent`, `DeletionJob`, `DeletionTombstone`), both migrations, `apps.py` and `static_settings.py`;
- `services/api/glow_domain/interactions.py`: how the P05.3 rules unmatch, block and unblock (a block turns an active match `restricted`; an unblock leaves the match as it is);
- `services/api/glow_api/configuration_profiles.py`: `FORBIDDEN_CONNECTION_NAMES`;
- `.github/workflows/foundation.yml`, `services/api/tests/test_toolchain_pins.py` and `docs/operations/ci-and-branch-policy.md`;
- `proofs/stream-chat/`: its README ("Install", "Checks (offline)"), `pyproject.toml`, `requirements*.in` and `requirements*.lock`, as the pattern for a proof package.

## 3. The work

Build what the brief specifies, in this order. The brief's section names are in brackets.

1. **The package** [D1, D2]. `proofs/postgres-ordering/`, with its own README (what it proves and does not, how to run it offline and against a disposable database, and its limits), `pyproject.toml` (Ruff and mypy set as `proofs/stream-chat/` sets them), `requirements.in`, `requirements-dev.in` and hash-pinned `.lock` files. Pin Django 5.2.17, as `services/api` does, and `psycopg` 3; no allauth. Ruff 0.16.8 and mypy 2.3.1, as pinned in `services/api/requirements-dev.lock`; add typing stubs only if mypy needs them.
2. **The settings** [D1, D3 condition 1]. Its own Django settings module: never import the API's settings or `static_settings`. `INSTALLED_APPS` holds `django.contrib.contenttypes`, `django.contrib.auth` and `glow_persistence.apps.PersistenceDesignConfig`, imported from `services/api` unchanged.
   - Refuse to start if `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, any other name in `FORBIDDEN_CONNECTION_NAMES` or any `PG*` name is present.
   - Explicit connection options: a loopback host (or a Unix-socket directory for a local cluster), port, database name, user and `passfile`, with no service name, so that libpq takes nothing from its environment or default files. Refuse any other host.
   - The proof's own variable names, never a `PG*`, `DATABASE_URL` or `GLOW_*` name.
   - Offline tests show each refusal.
3. **The reference design** [D5; brief items 2 and 3]. The send and every revocation, as D5 specifies: `READ COMMITTED`; `SELECT ... FOR UPDATE` by primary key in the canonical order (the lower account, the higher account, the match, then the sending session's `AccountSession` row); state checked in code after the locks; time read after the locks (5.2); authorize, then deduplicate (5.4); an empty locked read is a refusal (5.5); the check list and the exclusions of 5.6; deletion as the lifecycle transition, never a hard delete. The send inserts its `MessageSubmission` and its `OutboxEvent` in one transaction. Create the match's `ChatBinding` locally (`active`, with a stand-in channel reference); call no provider. The sign-in creates a user through `django.contrib.auth`, its `AppAccount`, and an `AccountSession` with a random, non-secret stand-in `auth_session_ref` (D2).
4. **One interface, and the suite** [D1; item 6; brief item 2]. The race suite drives send, block, unblock, unmatch, suspend, delete, sign-in and sign-out through one small interface, so that P06.2 can run the same suite against the app's adapter. It covers every guarantee in the brief's items 2 and 3:
   - **forced interleavings** on two real connections for each revocation: the send commits first; the revocation commits first; each arrives while the other holds its locks. Before releasing the first transaction, confirm from `pg_stat_activity` (`wait_event_type = 'Lock'` for the second connection's backend) or `pg_locks` that the second is waiting, and record it (6.2);
   - the **named cases**: a stale contact version; the four retry rules of 5.4, the racing duplicates forced; unblock does not resurrect; a session that expires while the send waits (5.2); sign-out and administrative expiry against a send, both ways (5.1); opposing writers with no deadlock (5.3); a first block against a send (D5); the minimal sign-in's revocations (item 3);
   - the **commit-order oracle** (6.1): with `track_commit_timestamp=on`, no `MessageSubmission` commits after a revocation that invalidates it, judged by `pg_xact_commit_timestamp(xmin)` over every row, with each revocation's own commit time read from a row it writes in its transaction (its `OutboxEvent`, or a proof log row);
   - the **stress run** (6.3): a seeded, randomized repeat of each race. Fix its budget in code: up to 200 iterations or 30 seconds per race, whichever comes first, with the whole database step well under the job's timeout. Record the seed, the iterations and a measured overlap count, and say how you measure an overlap. A race that ends with fewer than 50 iterations or fewer than 10 observed overlaps fails the job instead of passing. You may change the 200 and the 30 from measured CI times, with the reason recorded; keep the floors;
   - a **negative control for each guarantee** (6.3): a deliberately broken variant, for example no row lock, no version check, no session lock, `now()` in place of a time read after the locks, deduplication before authorization, or the lock order inverted for one writer. Each runs in the same job and must be seen failing there: a forced case's control deterministically, a stress control at least once within its budget, with its first failing iteration recorded. A control that never fails fails the job.
   - `SERIALIZABLE` is optional (D5): if you run it, only as a recorded comparison with its own negative control. `READ COMMITTED` with row locks is the design.
5. **The job** [D3, conditions 1 to 4; D1]. In `.github/workflows/foundation.yml`, add a job with the key `database`, named "Database proof checks":
   - the other application jobs' `needs: scope` and `if:` condition, `runs-on: ubuntu-24.04`, a `timeout-minutes` of at most 20, the same pinned `actions/checkout` (with `persist-credentials: false`) and `actions/setup-python` with `python-version: '3.12.14'`, `working-directory: proofs/postgres-ordering`, no `env:` of secrets, and the workflow's read-only permissions;
   - the hash-locked install and `pip check`; the offline tests under `env -i`; Ruff and mypy;
   - **the database**, per D3:
     - the password generated under `set +x`, with `::add-mask::` as its first output, written to a file only the job's user can read;
     - the official `postgres` image at 17.11, pinned by digest (find the digest from `docker pull`'s own output; the workflow runs no `docker inspect` at all);
     - started with `docker run` under a unique name, bound with `-p 127.0.0.1:<port>:5432`, with `-c track_commit_timestamp=on`, the password reaching it by a route that prints nothing (for example `POSTGRES_PASSWORD_FILE` with the file mounted read-only);
     - readiness awaited with `pg_isready` and a fixed limit;
     - a role created in the job that owns the proof's database and is not a superuser, which the proof connects as;
   - **the proof:** `migrate` from zero with the proof's settings, and the applied ledger recorded; `makemigrations --check --dry-run`, which must find no change (if it does, stop and report, as for a failing migration); `SELECT version()` recorded beside the image digest; the suite, the oracle, the stress run and the controls; a results table printed in the log, with no password and no connection string in it;
   - an `if: always()` step that removes the container and the password file;
   - **the gate:** add `database` to its `needs` and to its tuple of required jobs. Change nothing else in the workflow: no other job, the gate's messages, the triggers, the concurrency or the classifier's step.
6. **Offline tests** [acceptance check 4]: the settings' refusals, the case plan and the result recording, the budget's floors, and a pin test that fails if the proof's Django differs from `services/api/requirements.lock`'s. They run without a database.
7. **The evidence record** (section 5).

**Local runs** [D4]. You may iterate against a disposable database in your own sandbox: `docker run` with the same recipe if Docker works; otherwise a throwaway cluster from local binaries (`initdb` in a temporary directory, listening only on a Unix socket or loopback), recording its version; otherwise iterate through CI. The same rules hold: a generated password, loopback or a socket only, removed afterwards, and no forbidden or `PG*` name present. Local runs are iteration, not evidence: the record rests on the CI job's run on your final head. Your report says which you used.

**If the design itself fails.** If a case fails because the brief's design is wrong, not your code, do not redesign past D5: keep the failing case, report it with the observations and your proposed change, and stop there. The manager takes a design change to the Dev Manager.

**Rules for the work:**

- **Evidence comes from the database.** Every guarantee is judged by what PostgreSQL recorded (rows, commit times, lock waits), never by what the test code believes it did.
- **No weakened check.** Never loosen a case, the oracle or a floor to make a run pass. A flaky case is a finding (OD-21), not a retry.
- **No password anywhere:** not in the diff, a log line, the evidence record or your report.
- **The API is untouched.** Nothing under `services/` changes, and the proof imports `glow_persistence` without monkey-patching its models or migrations.

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
4. The offline checks: the unit tests with their count; Ruff check and format; mypy with its file count; the Django pin test; and `services/api`'s toolchain pin test with the new job in the workflow (`cd services/api && python3.12 -m unittest tests.test_toolchain_pins`).
5. Your local runs, if any: which database, its version, and the results, marked "iteration, not evidence".
6. **The Foundation run on your final head:** its run ID, each job's conclusion (eight jobs, "Database proof checks" included), and the gate's log line, which must be `Application checks passed`. From the database job's log: the image digest and `SELECT version()`, the applied ledger, `makemigrations --check`, each case with its observed waits, the oracle's result over every row, the stress run's seed, iterations and overlap count per race, each control's failure (and, for stress controls, the first failing iteration), and the container's removal. Confirm that the log shows no password and no `***` mask where a password would be. If your tools cannot read the run, say so; re-run or dispatch nothing.
7. A secret scan over your whole diff: no secret, token, API key, password or email address.

## 5. Owned paths, push and records

- **You may change:**
  - `proofs/postgres-ordering/**` (new);
  - `.github/workflows/foundation.yml`: the new `database` job, and the gate's `needs` and tuple. Nothing else in it;
  - a new evidence record, `docs/testing/evidence/<YYYY-MM-DD>-p06-db-disposable-postgres-proof.md`, dated the day you create it.
- **Nothing else,** including the brief, the CI policy (the manager updates it at integration, DM-08 7.1), the P11 acceptance plan (the manager marks DB06 and DB09), `services/`, `scripts/`, `apps/`, `packages/`, the root `.gitignore`, the ADRs and every other document. Report any other change you think is needed.
- **Commit and push** your session branch. Don't open a pull request.
- **The evidence record,** in the house style of `docs/testing/evidence/`, one section, "P06.DB implementation":
  - the start SHA, your head, your branch and the final-head CI run;
  - what the proof tested, and its result, in D6's words: what "partially evidenced" claims and what it does not;
  - the PostgreSQL version and image digest, the applied ledger, `makemigrations --check`, each case with its observed waits, the oracle, the stress numbers and each control's failure, from the final-head run;
  - local runs, marked "iteration, not evidence";
  - how the password was generated, masked, passed and discarded, without its value;
  - the database's disposal;
  - deviations, open questions and limits;
  - what the exact-head review must know.

## 6. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<START_SHA>`);
- the environment check, and what a local database could use;
- your branch, head SHA and tree, and the changed paths;
- for each design item (D1 to D6 and item 6) and each case: built as specified, or where and why it differs;
- every check, with its exact results, and the final-head run's details from section 4 item 6;
- which local database you used, if any;
- deviations, open questions, limits, and what the exact-head review must know.

Skipped or unavailable checks are not passes.

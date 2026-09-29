# P06.DB review prompt — exact-head code and security review of the disposable-PostgreSQL proof

- **Owner:** App Manager 5. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 29 September 2026.**
- **Durable brief:** [P06.DB brief](../planning/p06-db-disposable-postgres-proof.md), revision 2: its review plan (DM-08 7.2) and "Sessions".
  - Evidence: the [P06.DB evidence record](../testing/evidence/2026-09-29-p06-db-disposable-postgres-proof.md): "P06.DB implementation" (the session's own record) and the manager's verification under it.
- **Where the result goes:** the manager records the verified review in the evidence record, under a new heading "Exact-head review of P06.DB". The outcome goes into the brief's "Sessions" and decides whether the P11 plan's DB06 and DB09 marks stand as worded.
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v6: Fable 5.1, max.** Effort score 3.93 (confidence 0.94); rung probabilities low 0.00, medium 0.00, high 0.01, extra high 0.05, max 0.93, ultracode 0.01. Model probabilities Fable 5.1 0.94, Opus 5.5 0.06 (confidence 0.88). Sent 2026-09-29T04:57:55Z. Nathan picks the cell.
  - **Nathan's pick: Fable 5.1 at max**, started 29 September. This line was added after the prompt was given; the body Nathan pasted is unchanged.
- **Result:** changes required, narrowly, on 29 September. One should-fix finding is in a correction class (F1, the stress run's overlap count); there is one other should-fix finding (F2) and four nits. The manager verified the report and recorded it with its disposition in the evidence record, "Exact-head review of P06.DB". The correction pass P06.DB-C1 follows.
- **No Dev Manager read is needed:** the prompt authorizes no credential use and no live provider action, and the session starts no database.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and the session calls no provider.
- **It runs alone** (OD-29, the linear process). After it: corrections, if any, each with its own review; then the Dev Manager's read of PR28's governing changes, Codex's review and the merge.
- **Deletion condition:** prune after P06.DB's PR merges and the evidence record holds the result.

**Manager:** before giving this prompt to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **review session for P06.DB**, the early disposable-PostgreSQL proof of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<RECORDS_COMMIT>`.

Nathan approved P06.DB on 25 September 2026 (OD-17): *"Use a disposable PostgreSQL instance in CI to prove send-versus-block ordering and sign-in against real database behavior before P06.2. It must have no connection to a shared or production database. Record what the proof tested and its result, then dispose of the database."* The app's persistence schema, `services/api/glow_persistence`, had never been applied to a real database, and P06.2 will design the server-side send path on the ordering this proof shows. The implementation session built, from the manager branch at `8651652`:

- **the proof package** `proofs/postgres-ordering/` (29 files):
  - Django settings that refuse the API's forbidden connection names and every `PG*` name, and connect only to a loopback database through a passfile;
  - the reference design of the send and of each revocation (`reference.py`), with switches in `design.py` that only the negative controls turn off;
  - a race suite of 55 cases behind one interface (`interface.py`, `cases.py`), with each forced wait observed in the database (`observe.py`);
  - a commit-order oracle over every row (`oracle.py`, rules O1 to O8), a seeded stress run of 12 races (`stress.py`, `budget.py`), ten negative controls (`controls.py`) and the results table and verdict (`results.py`, `__main__.py`);
- **one Foundation job, "Database proof checks":** it runs the package's offline checks, then starts PostgreSQL 17.11 from the official image, pinned by digest, inside the job on loopback, with passwords the job generates and masks. It then applies the reviewed migrations from zero, runs the suite, the stress run, the controls and the oracle, uploads the results JSON and removes the database. The gate requires the job;
- **the evidence record.**

The run of record is Foundation run 36520940933 on the code head `dff83d4`, in which every job passed. The manager verified the branch and integrated it with a merge commit.

- **You review one exact head:** `6f5866d505c5fd94ad9224ab9b23ba4e3bafaef5`, that merge commit.
  - Its first parent, `9768fcc`, is the manager branch before the merge. Its second parent, `074eea1`, is the session's head, a commit that adds only the evidence record.
  - The code head is `dff83d4cc1e2c9cbe91507d2fd2a8f2992ae6938`, and the merge's proof package and workflow are byte-identical to it.
  - The merge brought 31 files: the 29 under `proofs/postgres-ordering/`, `.github/workflows/foundation.yml` and the evidence record.
- **Your scope is P06.DB's change:** the whole of `git diff HEAD^1 HEAD`. Include what the proof depends on in `services/api/glow_persistence` (its models and migrations, which P06.DB must not change) and in `docs/architecture/data-model.md`. Later commits are Markdown-only manager records, which you read at `<RECORDS_COMMIT>`.
- **The database run is not repeated here.** You start no database. The review is offline and reads the job's log (the brief's review plan; DM-08 7.2). You check that the code could not have produced a false pass: a case, race, oracle or control result that the run shows but the design has not earned.
- **What comes after this review.** Report every finding with its severity, as usual. Some findings get a correction pass before PR28 merges: any blocking finding, and any should-fix finding that could:
  - let a send authorization commit after a revocation that invalidates it without the suite failing;
  - let a password or connection value reach a log, an artifact or a file outside the job's temporary directory;
  - let the job or the proof connect to anything but its own disposable database;
  - make DB06's or DB09's mark claim more than the run shows.

  Everything else goes into the records. For each finding, say whether it falls in one of those classes.
- Nathan started you manually and will relay your report to the manager (App Manager 5). You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - Keep scratch work outside the repository, or in its ignored paths (`.venv/`, `.work/`).
- **Never:**
  - dump the environment;
  - start or connect to any database, whether a local cluster, a container, or the proof's settings pointed at anything. Never connect to Stream, HDE, Railway or any other provider;
  - run `playwright install`, `eas` or `migrate`, or the proof's `facts` and `run` commands.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. No `PG*`, `PROOF_DB_*` or `STREAM_*` name should be set: `compgen -e | grep -E '^(PG|PROOF_DB_|STREAM_)'` prints names only. If any is present, report its name first in your report, never read or use its value, and continue.
3. The pinned toolchain is in `$HOME/.local/bin`, including Python 3.12.14. Put `$HOME/.local/bin` first on PATH in every process you run the proof in, then record `command -v python3.12` and its version.
4. Run the proof's commands in a clean process environment, as its README's "Install" and "Checks (offline)" sections show. Installs get the proxy and CA variables by reference, never printed.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach 6f5866d505c5fd94ad9224ab9b23ba4e3bafaef5
git rev-parse HEAD                      # must print 6f5866d505c5fd94ad9224ab9b23ba4e3bafaef5
git rev-parse HEAD^2                    # must print 074eea18a04cf60d8e5235f52442879262eb5fa2
git merge-base --all origin/main HEAD   # expected: one line, 47db18dfec3f62626f4e09f65f52c7a2e10c9e3e
git merge-base --is-ancestor HEAD <RECORDS_COMMIT> && echo "records build on the head"
git diff --stat HEAD^1 HEAD             # expected: 31 files, 5072 insertions, 2 deletions
git diff --quiet dff83d4cc1e2c9cbe91507d2fd2a8f2992ae6938 HEAD -- proofs .github services scripts apps packages && echo "the code of run 36520940933"
```

If any check fails, stop and report.

Classify three times, as root `AGENTS.md` requires. The trusted base policy runs outside the candidate tree, every run uses the same policy file, and every SHA is a full one (a short SHA fails closed):

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
python3 -I "$policy_dir/change_scope.py" --base "$base" --head 9768fcc42909551786784c561a869d3cc7fa20f6 --merge-base
python3 -I "$policy_dir/change_scope.py" --base "$head" --head <RECORDS_COMMIT> --merge-base
git diff --name-only "$base" "$head" | grep -v '\.md$' | grep -v '^proofs/postgres-ordering/' | grep -v '^\.github/workflows/foundation\.yml$'
```

- **The first run** is the head against `main`. Expected: `"full": true`. The last command must print nothing: every non-Markdown change in PR28 is under `proofs/postgres-ordering/` or is the workflow. Anything else is code this review would not cover: stop and report it.
- **The second run** is PR28 before the merge. Expected: `ordinary-docs-only`, so PR28 held no code before P06.DB.
- **The third run** is everything after the head. Expected: `ordinary-docs-only`. Anything else means a non-Markdown change landed after the head: stop and report it.

Then read, completely.

**At `HEAD`:**

- root `AGENTS.md` and `CLAUDE.md`;
- the P06.DB prompt, `docs/ephemeral/2026-09-29-p06-db-implementation-prompt.md` (revision 1): what the session was asked to do, including its owned paths, its rules and its report format;
- the P06.DB brief, `docs/planning/p06-db-disposable-postgres-proof.md` (revision 2): "What P06.DB proves", the design D1 to D6 with item 6, and "Brief" (acceptance checks and review plan);
- the Dev Manager's read of the brief, `docs/continuity/dev-manager/reviews/2026-09-29-dm-08-p06-db-brief.md`, and the manager's disposition in `docs/continuity/dev-manager/README.md`, "DM-08";
- in `docs/architecture/data-model.md`, the unit-of-work rules for sending, blocking, unmatching, suspension, deletion and sessions, which D5 follows;
- the evidence record, `docs/testing/evidence/2026-09-29-p06-db-disposable-postgres-proof.md`: the session's section, "P06.DB implementation";
- `.github/workflows/foundation.yml` and `services/api/tests/test_toolchain_pins.py`;
- `proofs/postgres-ordering/README.md` and the whole of `git diff HEAD^1 HEAD`;
- in `services/api/glow_persistence`, the models and migrations the proof uses (`AppAccount`, `AccountSession`, `Match`, `Block`, `ChatBinding`, `MessageSubmission`, `OutboxEvent`, `DeletionJob`, `DeletionTombstone`), and in `services/api` the forbidden connection list that the proof's `environment.py` copies.

**At `<RECORDS_COMMIT>`,** with `git show <RECORDS_COMMIT>:<path>`:

- the evidence record's "Manager verification of P06.DB": its identity checks, its two corrections to the session's record, its five observations for this review and its dispositions;
- the brief's "Sessions";
- `docs/testing/p11-deferred-acceptance.md`: the DB06 and DB09 rows and "Early partial evidence", with the marks;
- `docs/operations/ci-and-branch-policy.md`, the lines that name the new job. That policy is governing Markdown, which the Dev Manager reads; you check only that it describes the job as built.

## 3. What to review

The focus areas are in order of risk.

1. **No send authorization can commit after a revocation that invalidates it** (the brief's item 2 and D5; `reference.py`).
   - **The send.** Check each step:
     - its reads before the locks: only the match's pair and the session's account, which the code calls immutable. Confirm that against the models and against every writer in the package;
     - the lock order: lower account, higher account, match, then the session, each by primary key with `FOR UPDATE`;
     - `clock_timestamp()` read after the locks;
     - the checks on the rows as locked, in their order;
     - authorization before deduplication, then the binding check;
     - the `MessageSubmission`, its `OutboxEvent` and the log row, all in one transaction.
   - **Each revocation:**
     - block and unmatch: which rows they lock, and in which order. A block turns an active match `restricted` and bumps its contact version; an unblock leaves the match as it is;
     - suspension and deletion: the account row and its `session_epoch`. Deletion must be the lifecycle transition, with its `DeletionJob` and `DeletionTombstone`, never a hard delete;
     - sign-out and expiry: the session row;
     - sign-in.
   - Under `READ COMMITTED`, could any interleaving let a send pass its checks on a row version that a committed revocation has already replaced?
   - Could a writer take its locks in a different order and deadlock with the send (D5's canonical order), or skip a lock that the send's check relies on? Is there any revocation of contact in the package that does not take that lock?
   - **The retry rules.** Check each:
     - the identical replay;
     - the same key with a different request (`idempotency_conflict`);
     - a retry after a revocation, which must be refused and never get the old receipt;
     - racing duplicates: one row, and no unique-constraint error reaches the caller.
2. **The suite could not pass falsely.**
   - **Forced cases** (`cases.py` `forced`, `observe.py`):
     - is the arriving connection really waiting on the holder's lock when it is observed (`pg_stat_activity` with `wait_event_type = 'Lock'` for its backend, then `pg_locks` not granted)? Could it be waiting on something else, or be observed before it reaches the contended row?
     - does every held case require the wait?
     - is each case's expected outcome the one the design must produce?
   - **The oracle** (`oracle.py`, O1 to O8):
     - are the rules right and complete for the guarantees, and applied to every row? Ties count as violations.
     - is `pg_xact_commit_timestamp(xmin)` the commit time the oracle needs for each row it reads, including a row updated after it was written (an update changes `xmin`)?
     - could the join or the partition by run tag hide a violation?
     - the manager's observation 3: the submission stores the locked match's contact version, so O6 cannot see a stale client version.
   - **The stress run** (`stress.py`, `budget.py`):
     - overlaps are measured from database-clock intervals, and every race reports 200 overlaps in 200 iterations. Is that measure meaningful, or does it count every iteration by construction? Could a race pass while its writers never contend?
     - both orders occurred in every two-writer race: the send was authorized in 6 to 54 of 200 iterations per race;
     - the seed, and the fixed budget (OD-21).
   - **The controls** (`controls.py`, `design.py`):
     - does each break exactly what it says, and fail in the same run?
     - the manager's observation 2: several guarantees have no control of their own. For each, say whether the suite as it stands would catch a broken variant, and whether the gap matters for DB06's mark.
   - **The verdict** (`results.py`, `__main__.py`, `tests/test_results.py`): does the job fail on any failed case, an unclean race, a control that never failed, a violation in the design's rows, or a missing oracle?
3. **No password or connection value escapes, and nothing but the disposable database is reached** (D3; the workflow; `environment.py`, `settings.py`).
   - **The credential step:** `set +x`, `umask 077`, the masks before anything prints, and the files.
     - Could a password appear in a log line, a process listing, Docker's output, the container's log, psql's output, an error message, the results JSON or the uploaded artifact?
     - The role statement carries the role's password. Confirm it never reaches the log: psql's output file, the statement's deletion, and PostgreSQL's own logging of a statement that fails.
   - **The container:**
     - it is published only on `127.0.0.1:5433`;
     - the password arrives through `POSTGRES_PASSWORD_FILE` on a read-only mount;
     - the image is pinned by digest, with `track_commit_timestamp=on`;
     - the proof role is `NOSUPERUSER NOCREATEDB NOCREATEROLE`, and the run shows `superuser` false.
   - **The settings:**
     - they refuse `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, every name on the API's forbidden list and every `PG*` name;
     - they accept a loopback host or an absolute socket path only;
     - they give an explicit passfile, with SSL and GSS encryption disabled and no service name.
     - Does the copy of the API's list follow the API's list, as its test claims? Could any libpq default still apply (`~/.pgpass`, a service file, an environment default)?
   - **The API boundary:** the proof imports `glow_persistence` by adding `services/api` to `sys.path`. Does it import anything else from the API? Could the API's settings, guards or fixture mode be affected?
   - **Removal:** the `if: always()` step removes the container with its volume and the credential directory, then checks that no container remains. Does that hold when an earlier step fails or times out?
   - **The results artifact** (the manager's observation 4): read it if your tools can download it (run 36520940933, artifact 11013181409). Otherwise check what `results.py` writes. Say which you did.
4. **The workflow and the gate** (the CI policy's rule for workflow changes).
   - `git diff HEAD^1 HEAD -- .github/` is exactly the new job and the gate's `needs` and job tuple.
   - The job's condition equals the other application jobs'. Check its pins, `persist-credentials: false`, its timeout, and that it has no secret and no `env:` of secrets. The gate's documentation-only output is unchanged.
   - `services/api`'s pin test passes at the head.
   - **Hosted CI:**
     - run 36520940933: all eight jobs succeeded, and the gate printed `Application checks passed`;
     - the latest pull-request run of PR28 whose head contains `6f5866d`: confirm from its jobs that "Database proof checks" ran, not skipped, and passed.
5. **DM-08 7.2, from the database job's log** (job 109253447793), read whole:
   - no password appears. The three `***` are `actions/checkout`'s masking of its own token; look for any string shaped like the generated passwords (48 hexadecimal characters);
   - each forced wait was observed, in every held case;
   - the ten controls failed in the same run, and the two stress controls at their recorded first failing iteration.
6. **DB06 and DB09 claim no more than the run shows** (D6). Take the manager's observation 1 into account: the epoch check is never the deciding refusal. Are the marks accurate as worded, with their limit? Give your wording if they are not.
7. **Records.** This is a full-scope review: never skip a finding because its file ends in `.md`.
   - The session's section of the evidence record agrees with the code and the run, apart from the two corrections the manager recorded. Check its numbers against the log.
   - The README's description matches the code.
   - The manager's verification at `<RECORDS_COMMIT>`: assess each of its corrections, observations and dispositions, and say where you disagree and why.
8. **Scope and dependencies.**
   - Only the 31 paths named changed. Nothing under `services/`, `scripts/`, `apps/`, `packages/` or `.gitignore` changed. Every file has mode 100644, and there are no symlinks.
   - The proof's locks install with `--require-hashes`. Django 5.2.17 and its hashes equal `services/api`'s. `psycopg[binary]` 3.3.6 is the one new runtime dependency (D2).

**Out of scope:**

- running any database;
- `services/api`, beyond what the proof imports or copies;
- governing Markdown (the CI policy and the manager workflow's checklist line), which the Dev Manager reads;
- P06.2, and anything in HDE.

## 4. Checks to run

Report the exact commands and results.

1. `git diff --check HEAD^1 HEAD`.
2. The three classifications above.
3. The install from the proof's locks, with the README's commands, in a clean process: `pip install --require-hashes -r requirements-dev.lock` and `pip check`.
4. The offline checks, with the README's commands:
   - the unit tests under `env -i` (the session reported 40);
   - Ruff check and format, and mypy;
   - `services/api`'s `python3.12 -m unittest tests.test_toolchain_pins`.
5. A secret scan over the whole of `git diff HEAD^1 HEAD`: no secret, token, password, connection string or email address. The long hexadecimal strings should be the action pins and the image digest, and the lock lines should be hashes; confirm each.
6. Hosted CI, as focus areas 4 and 5 say.
7. Anything else you judge necessary, offline only. You may write throwaway tests or scripts outside the repository that exercise the package without a database: the settings' refusals, the case and control plans, or the oracle's rules against constructed rows (by replacing its fetches). Nothing may open a connection.

## 5. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<RECORDS_COMMIT>`);
- the environment check's result (names only);
- the head you reviewed (`git rev-parse HEAD`) and the three classification outputs;
- **verdict:** "approve" (P06.DB's proof, job and records are sound, and PR28 can go on to the Dev Manager's read and the merge) or "changes required";
- **findings,** most severe first. For each: severity (**blocking**, **should fix** or **nit**), `file:line`, the concrete failure scenario, a suggested fix, and whether it falls in one of the classes that need a correction before PR28 merges;
- DM-08 7.2's three checks from the log, each confirmed or not;
- for each of the manager's corrections, observations and dispositions: agree, or disagree with the reason;
- the DB06 and DB09 marks: accurate as worded, or your wording;
- the workflow: confirmed as exactly the one job and the gate's change, and the job's result in run 36520940933 and in PR28's latest run;
- the areas you reviewed with no findings;
- every check you ran, with its exact result;
- limits: anything you could not check, and why.

Skipped or unavailable checks are not passes. Change nothing in the repository, on GitHub or in Notion.

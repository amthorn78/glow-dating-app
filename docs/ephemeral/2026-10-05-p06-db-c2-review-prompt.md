# P06.DB-C2 review prompt — exact-head review of the correction pass (the run's marker)

- **Owner:** App Manager 5. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 5 October 2026.**
- **Durable brief:** [P06.DB brief](../planning/p06-db-disposable-postgres-proof.md), revision 5, and its "Sessions".
  - Evidence: the [P06.DB evidence record](../testing/evidence/2026-09-29-p06-db-disposable-postgres-proof.md): "P06.DB-C2 corrections" (the session's own record) and "Manager verification of P06.DB-C2".
- **Where the result goes:** the manager records the verified review in the evidence record, under a new heading "Exact-head review of P06.DB-C2". The outcome goes into the brief's "Sessions" and decides whether PR28 goes on to Codex's review of its final head and the merge.
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v6: Opus 5.5, extra high.** Effort score 2.83 (confidence 0.79); rung probabilities low 0.00, medium 0.01, high 0.23, extra high 0.68, max 0.08, ultracode 0.00. Model probabilities Fable 5.1 0.04, Opus 5.5 0.96 (confidence 0.93). Sent 2026-10-05T04:38:01Z. Nathan picks the cell.
  - **Nathan's pick:** Opus 5.5 at extra high, the reading's cell (reported on 5 October).
- **No Dev Manager read is needed:** the prompt authorizes no credential use and no live provider action, and the session starts no database.
- **Result:** done on 5 October, from revision 1 (records commit `dd67696`): **approve**, of `369d03c`. No finding is blocking, and the review puts none in a correction class. F1, should fix: Django's `dbshell` starts `psql` outside Django, so the marker is never checked for it; the README now says so, and the Dev Manager approved F1's disposition the same day (DM-12): no correction pass before the merge, and a guard that refuses `dbshell` required before P06.2's first run of the suite. F2 and F3 are nits in the records, applied (AM5-21). The manager verified the report and recorded it in the evidence record, "Exact-head review of P06.DB-C2".
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and the session calls no provider.
- **It runs alone** (OD-29, the linear process). After it: a correction, if any, with its own review; then Codex's review of the final head, the pre-merge checklist and the merge.
- **Deletion condition:** prune after P06.DB's PR merges and the evidence record holds the result.

**Manager:** before giving this prompt to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **review session for P06.DB-C2**, the second correction pass on P06.DB, the early disposable-PostgreSQL proof of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<RECORDS_COMMIT>`.

P06.DB built two things:

- `proofs/postgres-ordering/`, a proof package that orders message-send authorizations against every revocation of contact on a real PostgreSQL 17 database;
- the Foundation job "Database proof checks". It starts that database inside the job, on loopback, with passwords the job generates and masks, runs the proof and removes the database.

Two exact-head reviews approved it, the second at `ea21ac8` (C1). Then Codex's code review of the pull request found a P1, **CX3**. The proof's only database guard was its host check, which accepts any loopback host or Unix-socket directory. So an SSH-forwarded or other local server passed it, and the documented first command, `migrate`, would change that database. The Dev Manager approved the fix's design with conditions 2.1 to 2.5 (DM-10), and the CI step's check in its own words (DM-11). The correction session started from `ad3323d` and added **the run's marker**:

- the proof's settings require `PROOF_DB_MARKER`, exactly 32 lowercase hexadecimal characters, and register a receiver on Django's `connection_created` signal (`glow_ordering_proof/marker.py`);
- on every new connection, the receiver reads the comment of the connection's database. Unless the comment is exactly `glow-ordering-proof:` followed by the marker, it closes the connection through Django and raises `RefusedDatabase`, which ends the command with a non-zero status;
- the job generates and masks the marker and a second well-formed one, and sets the database's comment to the run's marker. Before the migrations, it shows a `migrate` with the other marker refused, with each schema's relation count unchanged;
- 16 new offline tests (98 in all), the README, and a new section of the evidence record.

Foundation run 37262466651 on the code head `43d8ca4` is the run of record: every job passed. The manager verified the branch, undid each part of the fix in turn (each undoing was caught) and integrated it with a merge commit.

- **You review one exact head:** `369d03c5cd1ed3537e044335bfb6ecc4cbc25f9a`, that merge commit.
  - Its first parent, `ad3323d`, is the manager branch before the merge. Its second parent, `1178dfa`, is the session's head.
  - The code head is `43d8ca428ea25aef485af0e7d5f3a1840a2ae0c6`, and the merge's proof package and workflow are byte-identical to it. The session's later commit changed only the evidence record.
  - The merge brought 10 files: the workflow, the README, three files under `glow_ordering_proof/`, four under `tests/`, and the evidence record.
- **Your scope is C2's change:** the whole of `git diff HEAD^1 HEAD`. Read it against the package and the workflow as they stand at `HEAD`, because a change can break code it did not touch.
  - The earlier reviews covered the rest of the package at `6f5866d` and `ea21ac8`. Re-read that code where the marker depends on it: how each command reaches the database, where the workers open their connections, and how the settings load.
  - Later commits are Markdown-only manager records, which you read at `<RECORDS_COMMIT>`.
- **The database run is not repeated here.** You start no database. The review is offline and reads the job's log. You check three things:
  - that the marker ties every command to the database created for the run;
  - that the job shows it;
  - that the evidence stays the same (DM-10's 2.5).
- **What comes after this review.** Report every finding with its severity, as usual. Some findings get another correction pass before PR28 merges: any blocking finding, and any should-fix finding that could:
  - let a send authorization commit after a revocation that invalidates it without the suite failing;
  - let a password, the marker or a connection value reach a log, an artifact or a file outside the job's temporary directory;
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
  - start or connect to any database, whether a local cluster, a container, or the proof's settings pointed at anything, and never set a database's comment. Never connect to Stream, HDE, Railway or any other provider;
  - run `playwright install` or `eas`;
  - run `migrate` or the proof's `facts` and `run` commands yourself. The offline tests run them only through `tests/command_harness.py`, whose fake server opens no connection; running the tests is allowed.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. No `PG*`, `PROOF_DB_*` or `STREAM_*` name should be set: `compgen -e | grep -E '^(PG|PROOF_DB_|STREAM_)'` prints names only. If any is present, report its name first in your report, never read or use its value, and continue.
3. The pinned toolchain is in `$HOME/.local/bin`, including Python 3.12.14. Put `$HOME/.local/bin` first on PATH in every process you run the proof in, then record `command -v python3.12` and its version.
4. Run the proof's commands in a clean process environment, as its README's "Install" and "Checks (offline)" sections show. Installs get the proxy and CA variables by reference, never printed.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach 369d03c5cd1ed3537e044335bfb6ecc4cbc25f9a
git rev-parse HEAD                      # must print 369d03c5cd1ed3537e044335bfb6ecc4cbc25f9a
git rev-parse HEAD^2                    # must print 1178dfa450cce88daf354de8b7b2f0434800fc05
git merge-base --all origin/main HEAD   # expected: one line, 47db18dfec3f62626f4e09f65f52c7a2e10c9e3e
git merge-base --is-ancestor HEAD <RECORDS_COMMIT> && echo "records build on the head"
git merge-base --is-ancestor <RECORDS_COMMIT> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet <RECORDS_COMMIT> origin/claude/magical-wozniak-yfmmx2 -- proofs .github services scripts apps packages && echo "no code after this prompt's commit"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-09-29-p06-db-disposable-postgres-proof.md | grep -c -E '^#+ Exact-head review of P06\.DB-C2'   # must print 0: this review is not yet recorded
git diff --stat HEAD^1 HEAD             # expected: 10 files, 840 insertions, 18 deletions
git diff --quiet 43d8ca428ea25aef485af0e7d5f3a1840a2ae0c6 HEAD -- proofs .github services scripts apps packages && echo "the code of run 37262466651"
```

If any check fails, stop and report. The three checks on `origin/claude/magical-wozniak-yfmmx2` read the live manager branch. If this prompt's commit is not on it, if code landed after that commit, or if this review is already recorded, the prompt is stale.

Classify three times, as root `AGENTS.md` requires. The trusted base policy runs outside the candidate tree, every run uses the same policy file, and every SHA is a full one (a short SHA fails closed):

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
python3 -I "$policy_dir/change_scope.py" --base ea21ac8577b83158be1f941b93dbef411bece41f --head "$(git rev-parse HEAD^1)" --merge-base
python3 -I "$policy_dir/change_scope.py" --base "$head" --head <RECORDS_COMMIT> --merge-base
git diff --name-only "$base" "$head" | grep -v '\.md$' | grep -v '^proofs/postgres-ordering/' | grep -v '^\.github/workflows/foundation\.yml$'
```

- **The first run** is the head against `main`. Expected: `"full": true`. The last command must print nothing: every non-Markdown change in PR28 is under `proofs/postgres-ordering/` or is the workflow. Anything else is code this review would not cover: stop and report it.
- **The second run** covers everything from C1's reviewed head to the manager branch just before this merge. Expected: `ordinary-docs-only`, so the only code since C1's review is C2's.
- **The third run** is everything after the head. Expected: `ordinary-docs-only`. Anything else means a non-Markdown change landed after the head: stop and report it.

Then read, completely.

**At `HEAD`:**

- root `AGENTS.md` and `CLAUDE.md`;
- the C2 prompt, `docs/ephemeral/2026-10-05-p06-db-c2-correction-prompt.md` (revision 2). It holds what the session was asked to do, DM-10's conditions 2.1 to 2.5 as quoted, DM-11's words and its note on 2.4, the owned paths, the rules and the report format;
- the DM-10 report, `docs/continuity/dev-manager/reviews/2026-10-05-dm-10-p06-db-cx3-design-read.md`, and the DM-11 report, `docs/continuity/dev-manager/reviews/2026-10-05-dm-11-p06-db-c2-prompt-read.md`;
- the P06.DB brief, `docs/planning/p06-db-disposable-postgres-proof.md` (revision 5): D1 with "The run's marker" and "DM-10's conditions", D3 with its item 5, D4, D6 and "Sessions";
- the evidence record, `docs/testing/evidence/2026-09-29-p06-db-disposable-postgres-proof.md`:
  - "Codex's second code review, of `9bcec21`": CX3 as posted, the manager's verification and the disposition;
  - "P06.DB-C2 corrections", the session's section;
- `proofs/postgres-ordering/README.md` and the whole of `git diff HEAD^1 HEAD`;
- whole, the package files the marker depends on: `environment.py`, `settings.py`, `marker.py`, `__main__.py` and `concurrency.py` (where the workers open their connections), and the tests the diff adds or changes;
- the `database` job of `.github/workflows/foundation.yml`, whole.

**At `<RECORDS_COMMIT>`,** with `git show <RECORDS_COMMIT>:<path>`:

- the evidence record's "Manager verification of P06.DB-C2": its identity checks, its reversal table, its five observations and its dispositions;
- the brief's "Sessions";
- `docs/testing/p11-deferred-acceptance.md`: "Early partial evidence", with the DB06 and DB09 entries.

## 3. What to review

The focus areas are in order of risk.

1. **No command can skip the check** (DM-10 2.2; `marker.py`, `settings.py`).
   - The receiver is registered when the settings are imported, on `connection_created`, for every backend. Can any command or code path that uses the proof's settings open a connection before the receiver is registered, or without the signal? Check `__main__.py`, `facts`, `run`, the worker threads in `concurrency.py`, and Django's management commands.
   - Before the check, the connection may run only its own session settings. Confirm what Django 5.2.17's `connect()` and the PostgreSQL backend's `init_connection_state` run before the signal, and that nothing writes or locks.
   - On a refusal, the receiver calls `connection.close()` through Django, then raises `RefusedDatabase`, which is deliberately not a `DatabaseError`.
     - Does each command end with a non-zero status? Can Django or the proof catch the exception anywhere and carry on?
     - Is the connection really not kept: is the wrapper's `connection` `None`?
     - What happens in a worker thread?
   - A failing query closes the connection and re-raises the driver's error. The manager's observation 4: `makemigrations` alone turns a Django `OperationalError` from its consistency check into a warning. Agree or not, and say whether it matters.
   - The comparison is of the whole comment string against the prefix and the marker. Check a null comment, no row and an empty comment.
2. **The marker's form** (DM-10 2.1; `environment.py`). Exactly 32 lowercase hexadecimal characters, checked with `fullmatch`. Each refusal names the variable and never a value, and the settings refuse at import.
3. **The CI step proves the refusal changed nothing** (DM-10 2.3, in DM-11's words; the wrong-marker step).
   - DM-11's precisions:
     - `starts_with(n.nspname, 'pg_')`, not `LIKE`;
     - `psql -d glow_proof`, never `postgres`;
     - the per-schema counts before and after compared whole, `pg_toast` included;
     - `to_regclass('public.django_migrations')` null after.
   - Can the step pass for the wrong reason? Consider `migrate` failing for another cause after creating a relation, the refusal line matched in output that is not the refusal, a count taken in another database, the `set +e` and `set -e` around the wrong-marker run, and the `cmp` of the two tables.
   - The step prints both tables, the counts, the exit status and the refusal line, and no name of a role, password or marker.
4. **The marker in the job** (DM-10 2.4, with DM-11's note).
   - The marker is generated in the credentials step and masked before any output. Agree or not with the manager's observation 2, on the masks' order.
   - DM-11's note: each step that needs the marker reads it from the job's protected temporary directory into `PROOF_DB_MARKER` for its own commands, never through `$GITHUB_ENV` or a step output. Check the whole job.
   - The role step sets the comment from `create-role.sql` with its output withheld, then removes the file. The removal step removes the marker files. The upload step sees only `.work/results.json`.
   - Only the `database` job changed. The gate and the other jobs are byte-identical to `ad3323d`'s.
5. **The evidence stays the same** (DM-10 2.5; the log of run 37262466651's database job, job 111612413204, read whole).
   - The plan is `ea21ac8`'s: 55 cases, 10 controls, and the same races, seed, budget and floors. No race, case, control, floor or reference-design file changed.
   - 55 of 55 passed, every control met its declared signal, there were 0 violations in the design's rows, and every forced wait was observed with its holder.
   - The marker query runs only at connection creation (the code), and the log shows that no worker reconnected inside a race. The verification lines are the record; agree or not with the manager's observation 3 on that line.
   - **Timing** (the manager's observation 1). The races ran slower than in C1's run, with more overlaps. Read PR28's latest pull-request run on a head that contains `369d03c`, which runs C2's code again, and its database job's per-race seconds and overlaps. Say whether the marker could cause the difference.
   - **DM-08 7.2's checks, again:**
     - no password or marker in the log: look for strings of 32 or 48 hexadecimal characters; the three `***` are the checkout and setup-python tokens;
     - each forced wait observed, with its blocking backend;
     - the ten controls met their declared signals.
6. **The tests are real** (`tests/test_marker.py`, `tests/test_marker_commands.py`, `tests/command_harness.py`).
   - The command harness replaces the backend's driver-facing methods in a subprocess. Does it still exercise Django's real `connect()`, the signal and the commands? Or could it pass while the real path skips the check?
   - The manager undid each part of the fix in turn, and each undoing was caught. Is any part of the fix untested?
7. **CX3 is closed** (the evidence record, "Codex's second code review, of `9bcec21`").
   - With the marker, can the proof or its documented commands change, or read from, a database that was not created for the run? Consider a reused database, a reused marker, a server on loopback or a socket, and the README's local recipe.
   - The reused-database guard stays carried to P06.2 (R2). Does the README's "Limits" describe what the marker covers and what it does not?
8. **DB06 and DB09 claim no more than the runs show** (D6). The P11 plan's entries now cite run 37262466651. Are they accurate as worded? Give your wording if not.
9. **Records.** This is a full-scope review: never skip a finding because its file ends in `.md`.
   - The session's section agrees with the log: the wrong-marker step's table, the races, the controls, the oracle and the log checks.
   - The README describes the code and the job.
   - The manager's verification of C2 at `<RECORDS_COMMIT>`: assess its observations and dispositions, and say where you disagree and why.
10. **Scope and dependencies.**
    - Only the 10 paths named changed. No dependency file, `services/`, `scripts/`, `apps/`, `packages/` or `.gitignore` path changed.
    - Every file has mode 100644, there are no symlinks, and the locks are unchanged.

**Out of scope:**

- running any database;
- `services/api`;
- governing Markdown (the CI policy and the manager workflow), which the Dev Manager reads;
- P06.2, and anything in HDE;
- CX1, CX2 and R1 to R4, which stay carried to P06.2, except where focus area 7 asks;
- the package's ordering code, which C2 did not change, except where the marker depends on it.

## 4. Checks to run

Report the exact commands and results.

1. `git diff --check HEAD^1 HEAD`.
2. The three classifications above.
3. The install from the proof's locks, with the README's commands, in a clean process: `pip install --require-hashes -r requirements-dev.lock` and `pip check`.
4. The offline checks, with the README's commands:
   - the unit tests under `env -i` (the session reported 98);
   - `ruff check .`, `ruff format --check .` and mypy;
   - `services/api`'s `python3.12 -m unittest tests.test_toolchain_pins`.
5. A secret scan over the whole of `git diff HEAD^1 HEAD`: no secret, token, password, marker value, connection string or email address. Confirm that each long hexadecimal string is a commit SHA or a digest.
6. Hosted CI: run 37262466651, as focus area 5 says, and PR28's latest pull-request run on a head that contains `369d03c`. In that run, "Database proof checks" must have run, not been skipped, and passed; give its per-race seconds and overlaps.
7. Anything else you judge necessary, offline only. You may write throwaway tests or scripts outside the repository that exercise the package without a database, such as undoing part of the fix to see its test fail. Nothing may open a connection.

## 5. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<RECORDS_COMMIT>`);
- the environment check's result (names only);
- the head you reviewed (`git rev-parse HEAD`) and the three classification outputs;
- **verdict:** "approve" or "changes required". "Approve" means C2's correction, its run of record and the records are sound, and PR28 can go on to Codex's review of its final head and the merge;
- **findings,** most severe first. For each:
  - its severity: **blocking**, **should fix** or **nit**;
  - `file:line`;
  - the concrete failure scenario;
  - a suggested fix;
  - whether it falls in one of the classes that need a correction before PR28 merges;
- DM-10's conditions 2.1 to 2.5, and DM-11's precisions and its note on 2.4: each confirmed or not;
- DM-08 7.2's checks from the log, each confirmed or not;
- each of the manager's five observations and its dispositions: agree, or disagree with the reason;
- the DB06 and DB09 entries: accurate as worded, or your wording;
- PR28's latest pull-request run: the result of "Database proof checks", and its per-race seconds and overlaps;
- the areas you reviewed with no findings;
- every check you ran, with its exact result;
- limits: anything you could not check, and why.

Skipped or unavailable checks are not passes. Change nothing in the repository, on GitHub or in Notion.

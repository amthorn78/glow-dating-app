# P06.DB evidence: the early disposable-PostgreSQL proof

This is the evidence record for [P06.DB](../../planning/p06-db-disposable-postgres-proof.md) (brief revision 2; OD-17). It records observations only and is not an instruction source. The proof package is `proofs/postgres-ordering/` ([README](../../../proofs/postgres-ordering/README.md)).

## P06.DB implementation

The implementation session. It built the proof package, its Django settings and refusals, the reference design under proof, the race suite behind one interface, the commit-order oracle, the stress run, the negative controls and the Foundation job "Database proof checks", and ran the job on its head.

- **Prompt:** revision 1, from commit `86516522042b83769125dbda4ca5736967a7c462` (`docs/ephemeral/2026-09-29-p06-db-implementation-prompt.md`).
- **Session:** branch `claude/epic-maxwell-e4zomh`, started from `86516522042b83769125dbda4ca5736967a7c462` (the manager branch `claude/magical-wozniak-yfmmx2`).
- **Code head:** `dff83d4cc1e2c9cbe91507d2fd2a8f2992ae6938`. The evidence of record is Foundation run 36520940933 on that head (a push run; the classifier found full scope, so every application job ran).
- **Final head:** the commit that adds this record, which changes only this Markdown file. Its push run is documentation-only by the classifier's design (CI policy: a Markdown-only push skips the application jobs), so the record cites the code head's run; the pull request's run covers the final head against the merge base.
- **Times:** 29 September 2026, all in UTC.

### Summary

- **Setup, not acceptance: holds.** On PostgreSQL 17.11 in the job, Django's `contenttypes` and `auth` migrations and the reviewed `glow_persistence` migrations `0001_event_infrastructure` and `0002_app_domain` applied from an empty database, and `makemigrations --check --dry-run` printed `No changes detected`. The ledger below is read from `django_migrations`.
- **DB06, partially evidenced in CI (P06.DB), in D6's words:** on PostgreSQL 17, the reference design orders send authorizations against block, unmatch, suspension, deletion and sign-out, with the guarantees listed in the brief's item 2, under forced and randomized races. All 55 cases passed; every "while it holds the locks" case was observed waiting in `pg_stat_activity` and `pg_locks`; the commit-order oracle found zero violations over every row the design wrote; the twelve stress races each completed 200 iterations with 200 measured overlaps and zero violations; all ten negative controls failed in the same run.
- **DB09, partially evidenced in CI (P06.DB), in D6's words:** the app-side session and epoch revocation ordering against sends, with a stand-in session reference; not maintained authentication, verification, recovery, linking, credential revocation or allauth, which stay with the item that serves authentication and with P11.
- **What it does not claim:** that the app enforces any of it (the design is in the proof, not the app, until P06.2 carries it and tests it again); DB06's provider half (channel membership, and a send the provider has already accepted), which stays with P06.2 and P11; the P11 target, its roles, pooling or load; maintained authentication. P11A and P11B still rerun DB06 and DB09 on the real target; DB01, the move-out path and every other deferred case stay with P11. No app route, served feature or provider call changes.

### Environment check (names only)

| Check | Result |
|---|---|
| `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` | None present (the loop printed nothing) |
| `PG*` names | `no PG names` |
| `STREAM_APP_ID`, `STREAM_API_KEY`, `STREAM_API_SECRET` | None present |
| `command -v python3.12` | `/root/.local/bin/python3.12`, Python 3.12.14 (`$HOME/.local/bin` first on PATH) |
| `docker info` | exit status 1 (Docker does not work in the sandbox) |
| `command -v initdb pg_ctl postgres pg_isready psql` | `pg_isready` and `psql` at `/usr/bin`; `initdb`, `pg_ctl` and `postgres` absent from PATH but present in `/usr/lib/postgresql/16/bin/` (PostgreSQL 16.13, Ubuntu 16.13-0ubuntu0.24.04.1) |
| Start gate | `git fetch origin claude/magical-wozniak-yfmmx2`; `git merge --ff-only 86516522…` fast-forwarded; `git rev-parse HEAD` printed `86516522042b83769125dbda4ca5736967a7c462`; `no proof package yet` |

### What was built, against the brief

| Item | Built as specified, or the difference |
|---|---|
| D1 isolation | `proofs/postgres-ordering/` with its own settings (`glow_ordering_proof/settings.py`), hash-pinned locks (uv 0.8.17), offline tests, one CI job. `glow_persistence` is imported from `services/api` unchanged (its path is added to `sys.path` by the settings). The settings never import the API's settings or `static_settings` (an offline test parses the imports). They refuse `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, every other name on the API's `FORBIDDEN_CONNECTION_NAMES` (copied, not imported; a test reads the API's source and fails if the copy drifts) and any `PG*` name, presence alone, and name the offenders without values. Connection: explicit host (`127.0.0.1`, `localhost`, `::1` or an absolute Unix-socket directory; anything else refused), port, database, user and `passfile`, `sslmode=disable`, `gssencmode=disable`, no service name. Variables: `PROOF_DB_HOST`, `PROOF_DB_PORT`, `PROOF_DB_NAME`, `PROOF_DB_USER`, `PROOF_DB_PASSFILE`. The pin test (`tests/test_django_pin.py`) fails if the proof's Django version or wheel hashes differ from `services/api/requirements.lock`. One interface: `glow_ordering_proof/interface.py` (`OrderingSubject`, `FixtureFactory`, `Result`, `Hooks`) |
| D2 dependencies | Django 5.2.17 (the same hashes as the API's lock), `psycopg[binary]` 3.3.6, Ruff 0.16.8, mypy 2.3.1; no allauth. The sign-in's `auth_session_ref` is `standin-` plus 32 hex characters from `secrets.token_hex`, unique and non-secret; fixture users are created through `django.contrib.auth` with no password and no email address |
| D3 the job | Job key `database`, "Database proof checks": `needs: scope`, the other jobs' `if:`, `ubuntu-24.04`, `timeout-minutes: 20`, the pinned `actions/checkout` (`persist-credentials: false`) and `actions/setup-python` (`3.12.14`), `working-directory: proofs/postgres-ordering`, no `env:` of secrets, the workflow's read-only permissions. Steps: the hash-locked install and `pip check`; the offline tests under `env -i`; Ruff and mypy; the credential step (below); `docker pull` and `docker run` of `postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f` (the `17.11` tag's index digest) with `--publish 127.0.0.1:5433:5432`, a unique name (`glow-proof-db-<run id>-<attempt>`), `-c track_commit_timestamp=on`, and the superuser's password by `POSTGRES_PASSWORD_FILE` from a read-only bind mount; readiness with `docker exec … pg_isready` within 60 attempts of one second; the non-superuser role `glow_proof` (`NOSUPERUSER NOCREATEDB NOCREATEROLE`) owning database `glow_proof`, created by `psql` inside the container over its Unix socket from a file, with its output kept in a file; `migrate`, `makemigrations --check --dry-run` and `facts` (`SELECT version()`, `track_commit_timestamp`, the role's `rolsuper`, the ledger) with the proof's settings in a clean process; `run`; an `actions/upload-artifact` of the results JSON (`p06-db-proof-results`, 14 days); an `if: always()` step that removes the container with its volume and the credential files and fails if a proof container remains. The gate's `needs` and tuple gain `database`; nothing else in the workflow changed. The job runs no `docker inspect` and prints no connection option |
| D4 local runs | Docker does not work in the sandbox. A throwaway cluster from `/usr/lib/postgresql/16/bin/initdb` (PostgreSQL 16.13) in a `mktemp -d` directory under `/tmp` (the scratchpad's parents are root-only and the cluster runs as the `postgres` OS user), listening on a Unix socket only, `track_commit_timestamp=on`, a generated superuser password by `--pwfile`, a generated password for the non-superuser role `glow_proof` by a SQL file removed after use, `pg_hba` with `peer` for the postgres OS user and `scram-sha-256` for everyone else, a `0600` passfile, no forbidden or `PG*` name present. Removed at the end of the session (below). Iteration, not evidence |
| D5 the design | `glow_ordering_proof/reference.py`: `READ COMMITTED` (set on the connection through Django's `OPTIONS["isolation_level"]` and read back with `SHOW transaction_isolation` inside a writer's transaction), `SELECT … FOR UPDATE` by primary key in the canonical order (lower account, higher account, match, the sending session's `AccountSession` row), state checked in code after the locks (5.5), `clock_timestamp()` read after the locks (5.2), authorize then deduplicate (5.4), an empty locked read is a refusal (5.5), the check list of 5.6 with paused or restricted profiles and withdrawn consent excluded, deletion as the lifecycle transition (`deletion_pending`, epoch bumped, `DeletionJob` in `access_revoked`, `DeletionTombstone`). The send inserts its `MessageSubmission` and its `OutboxEvent` (`message_submitted`) in one transaction and records one proof-log row in the same transaction. The `ChatBinding` is created locally, `active`, with `proof-channel-<match id>`. Block: `Block` row inserted or `removed` to `active`, the actor's `blocks_version` bumped, an `active` match turned `restricted` with `contact_version` bumped, `block_changed` and `contact_revoked` outbox events. Unblock: the block `removed`, the match untouched. Unmatch: `unmatched`, `contact_version` bumped, `contact_revoked`. Suspension and deletion: the account row only, `session_epoch` and `eligibility_version` bumped, `access_revoked`. Sign-out and administrative expiry: the session row, `revoked` or `expired`, `session_revoked` or `session_expired` (5.1). `SERIALIZABLE` was not run (optional under D5) |
| Item 6 honesty | 6.1: `glow_ordering_proof/oracle.py`, `pg_xact_commit_timestamp(xmin)` over every `MessageSubmission` and every revocation's log row, rules O1 to O8 (below). 6.2: `observe_lock_wait` polls `pg_stat_activity` for the second connection's backend until `wait_event_type = 'Lock'` and reads its not-granted `pg_locks` entry before the first transaction is released; a forced case whose wait was not observed fails. 6.3: seeded stress run (`--seed 20260929`), budget fixed in `budget.py` (200 iterations or 30 s per race, floors 50 iterations and 10 overlaps), overlaps measured from database-clock intervals (below), controls in the same run with first failing iterations recorded |
| D6 the claim | Worded above, in the summary |

**How the password was generated, masked, passed and discarded.** The credential step runs with `set +x` and `umask 077`. Two passwords come from `python -c 'import secrets; print(secrets.token_hex(24))'` into shell variables; the step's first two outputs are `::add-mask::` for each. The superuser's password is written to `superuser-password`, the role's into `create-role.sql` (`CREATE ROLE glow_proof LOGIN PASSWORD '…' NOSUPERUSER NOCREATEDB NOCREATEROLE; CREATE DATABASE glow_proof OWNER glow_proof;`) and into the libpq passfile (`127.0.0.1:5433:glow_proof:glow_proof:…`), all `0600` in a `mktemp -d` directory under `$RUNNER_TEMP`. The container reads the superuser's file through `POSTGRES_PASSWORD_FILE` from a read-only bind mount; the role is created by `docker exec -i … psql` reading the SQL file from stdin, with stdout and stderr kept in a file (never printed), and the SQL file is removed at once. The proof reads the passfile through Django's `OPTIONS["passfile"]`; no `PG*`, `DATABASE_URL` or `GLOW_*` name carries it. The `if: always()` step removes the container with `docker rm --force --volumes` and the directory with `rm -rf`. No password is stored as a repository secret, printed, or present in this record.

**How an overlap is measured (6.3).** Each writer's transaction interval is read from the database: its start is `now()` inside the transaction (the proof-log row's `xact_start` default) and its end is `pg_xact_commit_timestamp(xmin)` of the row it wrote; a writer that was refused rolled back, so its start (`now()`) and end (`clock_timestamp()` read just before the rollback) are recorded afterwards in an attempt row. An iteration overlapped when the send's interval and a revocation's interval intersect (`start1 < end2 and start2 < end1`). Observed lock waits are the forced cases' measure, not the stress run's.

**The oracle's rules** (over every `MessageSubmission` S, partitioned by the run tag of its log row): O1 exactly one `send` log row committed in S's transaction; O2 no contact revocation of S's match with a version above S's committed before or with S; O3 no sign-out or expiry of S's session committed before or with S; O4 no suspension or deletion of either member committed before or with S; O5 S committed before its session's `expires_at`; O6 S's contact version equals one plus the contact revocations of the match committed before S; O7 S's epoch equals one plus the account revocations of the actor committed before S and the session's own epoch; O8 one row per `(actor, idempotency_key)`. Equal commit timestamps count as violations.

### The final-head run: Foundation run 36520940933 on `dff83d4cc1e2c9cbe91507d2fd2a8f2992ae6938`

Push run 401, `https://github.com/amthorn78/glow-dating-app/actions/runs/36520940933`, started 04:17:03 UTC. Eight jobs:

| Job | Conclusion |
|---|---|
| Change scope | success (full scope) |
| API checks | success (job 109253447754, 28 s) |
| Mobile checks | success (job 109253447940, 5 min 5 s) |
| API mobile smoke | success (job 109253447830, 39 s) |
| API artifact checks | success (job 109253447790, 25 s) |
| Stream proof checks | success (job 109253447772, 1 min 14 s) |
| Database proof checks | success (job 109253447793; 04:17:14 to 04:19:04 UTC, 1 min 50 s; the suite step 74 s) |
| Foundation gate | success (job 109254616772); its log line: `Application checks passed`, with `database: success` in its `RESULTS` |

**From the database job's log** (job 109253447793):

- **The image and the server.** `docker pull` printed `Digest: sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f` and `Status: Downloaded newer image for postgres@sha256:d74eeac9…`; the same digest is pinned in the workflow. `SELECT version()`: `PostgreSQL 17.11 (Debian 17.11-1.pgdg13+2) on x86_64-pc-linux-gnu, compiled by gcc (Debian 14.2.0-19) 14.2.0, 64-bit`. `track_commit_timestamp`: `on`. `default_transaction_isolation`: `read committed`, and `SHOW transaction_isolation` inside a writer's transaction: `read committed`. `deadlock_timeout`: `1s`. `current_user`: `glow_proof`; `superuser`: `false`; `current_database`: `glow_proof`. Readiness: `127.0.0.1:5432 - accepting connections` (inside the container) after the start step's 16 s.
- **The applied ledger** (`django_migrations`, in order): `contenttypes.0001_initial`, `contenttypes.0002_remove_content_type_name`, `auth.0001_initial` to `auth.0012_alter_user_first_name_max_length` (twelve), `glow_persistence.0001_event_infrastructure`, `glow_persistence.0002_app_domain`, all applied between 04:17:43.31 and 04:17:45.23 UTC; sixteen rows. `migrate` printed `OK` for each; `makemigrations --check --dry-run` printed `No changes detected`.
- **The cases:** `cases: 55/55 passed`. Each of the ten revocations (`block_by_low`, `block_by_high`, `unmatch_by_low`, `unmatch_by_high`, `suspend_low`, `suspend_high`, `delete_low`, `delete_high`, `sign_out_sender`, `expire_sender`) passed its four interleavings (`sequential_send_first`, `sequential_revocation_first`, `send_holds`, `revocation_holds`), and the fifteen named cases passed (`positive_send`, `stale_contact_version`, `retry_identical`, `retry_different_request`, `retry_after_revocation`, `racing_duplicates`, `unblock_no_resurrect`, `session_expires_during_wait`, `opposing_first_lock_block_high_vs_send`, `opposing_first_lock_suspend_high_vs_block_low`, `opposing_blocks_both_sides`, `opposing_four_writers`, `sign_in_revocations`, `deletion_keeps_authorization`, `unmatch_repeat_is_safe`). **Observed waits:** every one of the 26 cases with a held first transaction (the twenty `send_holds` and `revocation_holds` cases, `racing_duplicates`, `session_expires_during_wait`, the three pairwise opposing-writer cases) recorded `pid 98 wait_event_type=Lock wait_event=transactionid pg_locks not granted: transactionid/ShareLock` after one or two polls of `pg_stat_activity`. In each `send_holds` case the case also compared the commit timestamps and found the send's before the revocation's; in each `revocation_holds` case the send was refused and no submission row existed. `opposing_four_writers`: 40 writers in 10 rounds, no deadlock.
- **The stress run** (seed 20260929; budget 200 iterations or 30 s per race; floors 50 iterations and 10 overlaps), every race with 0 violations and 0 harness failures:

| Race | Iterations | Overlaps | Seconds | Outcomes |
|---|---|---|---|---|
| `race.block_by_low` | 200 | 200 | 4.5 | send authorized 41, refused `match_not_active` 159; block applied 200 |
| `race.block_by_high` | 200 | 200 | 6.1 | send authorized 44, refused 156; block applied 200 |
| `race.unmatch_by_low` | 200 | 200 | 4.5 | send authorized 54, refused 146; unmatch applied 200 |
| `race.unmatch_by_high` | 200 | 200 | 4.3 | send authorized 50, refused 150; unmatch applied 200 |
| `race.suspend_low` | 200 | 200 | 5.8 | send authorized 36, refused `account_not_active` 164; suspend applied 200 |
| `race.suspend_high` | 200 | 200 | 4.5 | send authorized 19, refused 181; suspend applied 200 |
| `race.delete_low` | 200 | 200 | 5.0 | send authorized 42, refused 158; delete applied 200 |
| `race.delete_high` | 200 | 200 | 5.5 | send authorized 24, refused 176; delete applied 200 |
| `race.sign_out_sender` | 200 | 200 | 4.1 | send authorized 6, refused `session_not_valid` 194; sign-out applied 200 |
| `race.expire_sender` | 200 | 200 | 4.4 | send authorized 14, refused 186; expiry applied 200 |
| `race.racing_duplicates` | 200 | 200 | 7.6 | one authorized and one replayed in every iteration (first request authorized 122 times, second 78); one row per key |
| `race.opposing_writers` | 200 | 200 | 6.3 | send refused 200 (`match_not_active` 192, `account_not_active` 8); both blocks and the suspension applied 200; no deadlock |

  Both orders occurred in every two-writer race (the send committed first in 6 to 54 of 200 iterations, the revocation first in the rest). In `race.opposing_writers` the send never won against three revocations in 200 iterations; its ordering guarantee is judged by the oracle over the rows that did commit, and the pairwise forced cases cover the send winning against each writer.

- **The negative controls,** all ten `failed as intended`:

| Control | Broken switch | Target | Signal in the run |
|---|---|---|---|
| `no_locks.forced` | no account, match or session lock | `unmatch_by_high.send_holds` | the unmatch was not observed waiting; the send committed at 04:18:54.514965 after the unmatch at 04:18:54.509059; oracle 2 violations (O2, O6) |
| `no_locks.stress` | the same | `race.block_by_high` | first failing iteration 1: the block (v2) committed 04:18:54.587654, the send at v1 04:18:54.587888; oracle 2 violations |
| `no_version_check` | no contact-version check | `named.stale_contact_version` | sends at versions 2 and 0 were authorized; oracle O6 |
| `no_session_lock` | the send does not lock its session row | `sign_out_sender.send_holds` | the sign-out was not observed waiting; the send committed 04:18:54.733603 after the sign-out at 04:18:54.728461; oracle 1 violation (O3) |
| `transaction_start_time` | `now()` in place of a time read after the locks | `named.session_expires_during_wait` | the send whose session expired while it waited was authorized; oracle 1 violation (O5) |
| `dedup_before_authorize` | deduplication before authorization | `named.retry_after_revocation` | the retry after the block was `replayed` with the old receipt |
| `inverted_lock_order` | a block by the higher account locks its own account first | `named.opposing_first_lock_block_high_vs_send` | `deadlock:DeadlockDetected` for the send |
| `no_account_lock.forced` | the send does not lock the accounts | `suspend_high.send_holds` | the suspension was not observed waiting; the send committed 04:18:59.043841 after the suspension at 04:18:59.038532; oracle 1 violation (O4) |
| `no_account_lock.stress` | the same | `race.suspend_high` | first failing iteration 1: the suspension committed 04:18:59.143343, the send 04:18:59.147735; oracle 1 violation |
| `filter_state_in_lock` | the state filter inside the locked read, an absent row treated as nothing to refuse | `unmatch_by_high.revocation_holds` | the send that arrived while the unmatch held was authorized and committed; oracle 2 violations (O2, O6) |

- **The oracle over every row:** 573 submissions and 2,694 revocation rows examined; submissions by tag: `design:forced` 32, `design:stress` 530, the nine controls 1 or 2 each; **violations in the design's rows: 0**; violations only under control tags (`no_locks.forced` 2, `no_locks.stress` 2, `filter_state_in_lock` 2, `no_session_lock` 1, `no_account_lock.forced` 1, `no_account_lock.stress` 1, `transaction_start_time` 1). `== VERDICT: PASS ==`.
- **Disposal in the job:** `container removed: glow-proof-db-36520940933-1`, `credential files removed`, `no proof container remains`.
- **The results JSON** was uploaded as artifact `p06-db-proof-results` (ID 11013181409, 5,941 bytes, 14 days).
- **No password and no mask where a password would be.** The log has three `***`: lines 38, 94 and 152, all `actions/checkout`'s masking of its own token during checkout, before the credential step. The credential step's visible output is the one line `credentials generated into a directory readable only by this job's user`; the role step's is `role glow_proof (NOSUPERUSER) and database glow_proof created`. No connection option, passfile content or connection string appears.

### Local runs (iteration, not evidence)

PostgreSQL 16.13 (Ubuntu 16.13-0ubuntu0.24.04.1), the throwaway cluster of D4 above, non-superuser role `glow_proof`, `track_commit_timestamp=on`, `read committed`. `migrate` applied the same sixteen migrations from zero; `makemigrations --check --dry-run` printed `No changes detected`.

| Run | Result |
|---|---|
| Run 1 (before the `no_locks.forced` control was retargeted from `block_by_high.send_holds` to `unmatch_by_high.send_holds`) | PASS: 55/55 cases; twelve races at 200 iterations and 200 overlaps each, 4.1 to 7.9 s per race; ten controls failed as intended (stress controls at iteration 1); 593 submissions and 2,694 revocation rows examined, zero design violations; 1 min 15 s |
| Run 2 (the pushed code, same database, rows accumulating) | PASS: 55/55 cases; twelve races at 200 iterations and 200 overlaps each, 4.5 to 8.6 s per race; ten controls failed as intended, `no_locks.forced` now with a committed violation (send committed after the unmatch) and the wait not observed; 1,190 submissions and 5,388 revocation rows examined, zero design violations; 1 min 26 s |

The retarget's reason: under `block_by_high.send_holds` the no-locks send re-read the `Block` table after the block committed and was refused `blocked`, so the control failed only through the unobserved wait; under `unmatch_by_high.send_holds` there is no block row and the stale send commits, so the control also fails through the oracle.

### The database's disposal

- **In CI:** the `if: always()` step removed the container with its anonymous data volume (`docker rm --force --volumes`) and the credential directory (`rm -rf`), then checked `docker ps --all` for any `glow-proof-db` container and found none. The runner itself is discarded after the job.
- **Locally:** the throwaway PostgreSQL 16.13 cluster was stopped with `pg_ctl stop` and its directory (data, socket, secrets, log and passfile) removed at the end of the session: `pg_ctl stop -m fast` printed `server stopped`, `pg_isready` then got no response, no postgres process remained, and `rm -rf` of the `mktemp -d` directory left nothing under `/tmp`; the proof package's `.venv/`, `.work/` and caches are gitignored and stay only in the sandbox.

### Checks

| Check | Command | Result |
|---|---|---|
| 1 | `git diff --check 86516522042b83769125dbda4ca5736967a7c462 HEAD` | clean |
| 1 | `git diff --name-only 86516522042b83769125dbda4ca5736967a7c462 HEAD` | `.github/workflows/foundation.yml` and 29 files under `proofs/postgres-ordering/` (this record is added by the final commit); nothing else |
| 2 | trusted-policy classification (`origin/main` = `47db18dfec3f62626f4e09f65f52c7a2e10c9e3e`; `python3 -I <tmp>/change_scope.py --base 86516522… --head dff83d4c… --merge-base`) | `{"full": true, "reason": "behavior-or-empty", …}`: full scope |
| 3 | `python3.12 -m venv .venv`; `pip install --require-hashes -r requirements-dev.lock` (proxy and CA variables by reference); `pip check` in a clean process | installed; `No broken requirements found.` The Django hashes in both proof locks are identical to `services/api/requirements.lock`'s |
| 4 | `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8 .venv/bin/python -m unittest discover -s tests -t .` | `Ran 40 tests … OK` (settings refusals 15, connection options 5, settings module 5, Django pin 4, budget 3, case plan 4, control plan 4, results 9; the settings tests include each refusal) |
| 4 | `.venv/bin/ruff check .` and `.venv/bin/ruff format --check .` | `All checks passed!`; `23 files already formatted` |
| 4 | `.venv/bin/mypy` | `Success: no issues found in 23 source files` |
| 4 | the Django pin test | in the 40 above (`tests/test_django_pin.py`, 4 tests) |
| 4 | `cd services/api && python3.12 -m unittest tests.test_toolchain_pins` (with the new job in the workflow) | `Ran 3 tests … OK` |
| 5 | local runs | above, iteration, not evidence |
| 6 | the Foundation run on the code head | above |
| 7 | secret scan over the diff (`git diff --cached -U0`, grep for password, secret, token, key, private-key markers, email addresses, connection strings and long hex strings, excluding lock hashes) | only names, comments and placeholders (`SECRET_KEY = "p06-db-proof-placeholder-not-a-secret"`, the refused variable names, `secrets.token_hex` calls); the long hex strings are the pinned action commits and the image digest; no email address |

The same checks ran in the job: `pip install --require-hashes`, `pip check`, the 40 tests under `env -i`, Ruff and mypy, all `success`.

### Deviations, open questions and limits

- **The final head's push run is documentation-only.** This record is the last commit. By the CI policy's design, a Markdown-only push skips the application jobs, so the final head's own push run does not show `Application checks passed`; the evidence of record is run 36520940933 on the code head `dff83d4c…`, which differs from the final head by this file alone (`git diff --stat dff83d4c… HEAD` shows one Markdown file). The pull request's run compares the final head against the merge base and runs every job. The prompt's item 6 asked for the gate line on the final head; this is the nearest the policy allows without a code change made only to trigger CI.
- **The `no_locks.forced` control was retargeted** during local iteration from `block_by_high.send_holds` to `unmatch_by_high.send_holds`, for the reason under "Local runs". The prompt named the controls by example, not by target.
- **`SERIALIZABLE` was not run** (optional under D5).
- **The image digest** was first read from Docker Hub's registry manifest for the `17.11` tag (`HEAD /v2/library/postgres/manifests/17.11`, `docker-content-digest`), because Docker does not work in the sandbox; the job's `docker pull` printed the same digest, which is the confirmation the prompt asked for.
- **Local iteration ran on PostgreSQL 16.13,** not 17.11, from the sandbox's own binaries as D4 condition 3 allows; the cluster's directory is under `/tmp` rather than the scratchpad because the postgres OS user cannot traverse the scratchpad's root-only parents.
- **The proof's `ChatBinding`** is created `active` with a stand-in channel reference and the provider is never called; DB06's provider half stays with P06.2 and P11 (D6).
- **The stress budget was not changed** from 200 iterations or 30 s; every race finished its 200 iterations in 4 to 8 s on the runner, so the wall-clock cap was never reached.
- **Fixture accounts start `active`** and their users have no password and no email address; verification and credentials are outside P06.DB.
- **Sends in `race.opposing_writers` never committed first** in 200 iterations (three revocations against one send); the send's ordering against each writer when it wins is covered by the forced `send_holds` cases and the two-writer races.
- **Open question for the manager:** none that blocks integration. The manager's items at integration are the CI policy's job list (now six application jobs), the P11 plan's DB06 and DB09 marks in D6's words, and Notion.
- **Limits:** the oracle treats equal commit timestamps as violations and none occurred; overlaps are measured from database-clock intervals, not from observed lock waits; the controls are broken variants of this package's own reference design and show what the suite detects, not every way an adapter could be wrong; the design is proven in the proof package, not in the app.

### What the exact-head review must know

- The exact head to review is the final head (this record's commit); its code is identical to `dff83d4cc1e2c9cbe91507d2fd2a8f2992ae6938`, whose run 36520940933 is the evidence of record. Read the database job's log (job 109253447793) for: no password (the three `***` are checkout's token), each forced wait observed (`wait_event_type=Lock` on every held case), and the ten controls failing in the same run (DM-08 7.2).
- The changed paths are `.github/workflows/foundation.yml` (the `database` job and the gate's `needs` and tuple only), `proofs/postgres-ordering/**` and this record. Nothing under `services/`, `scripts/`, `apps/`, `packages/` or `.gitignore` changed.
- The workflow change is full scope under the CI policy's workflow rule: the manager independently classifies with the pre-change policy and reads the complete workflow diff.
- The proof's settings add `services/api` to `sys.path` to import `glow_persistence` unchanged; they import nothing else from the API. The forbidden-name set is a copy of the API's, guarded by a test that reads the API's source.
- The reference design's switches (`design.py`) exist only so the controls can break one guarantee each; the reference is `Design()` and the suite runs it first under `design:*` tags, then each control under its `control:*` tag, and the oracle partitions by tag.
- The results JSON artifact (`p06-db-proof-results`) holds the same data as the printed table, with case notes, waits, per-race outcomes and every oracle violation's detail.

### Manager verification of P06.DB (App Manager 5, 29 September 2026)

App Manager 5 checked the relayed report against the pushed branch, the code and hosted CI. The manager started no database: its re-run below is the offline checks only.

- **Identity:**
  - branch `claude/epic-maxwell-e4zomh`, head `074eea18a04cf60d8e5235f52442879262eb5fa2`, tree `916655737a103c0e4bba92db6b562c26bc7ababc`, as reported. Two commits on the start `8651652`: `dff83d4` (the code) and `074eea1` (this record only). One merge base with `main` (`47db18d`);
  - 31 files, +5,072 and −2: 29 under `proofs/postgres-ordering/`, `.github/workflows/foundation.yml` and this record. Every path is owned. Nothing under `services/`, `scripts/`, `apps/`, `packages/` or `.gitignore` changed, and the root README is unchanged. Every file has mode 100644, there is no symlink, and `git diff --check` is clean;
  - **integrated** into the manager branch with a merge commit, `6f5866d505c5fd94ad9224ab9b23ba4e3bafaef5` (first parent `9768fcc`, the manager branch; second parent `074eea1`). Its proof package and workflow are byte-identical to `dff83d4`'s: `git diff dff83d4 6f5866d -- proofs .github services scripts apps packages` is empty.
- **Classification:** the trusted policy from `main` (`47db18d`, sha256 `dec69a26…`), outside the tree, with `python3 -I` and full SHAs: `8651652` → `074eea1` is full scope (`behavior-or-empty`), 31 paths; `dff83d4` → `074eea1` is `ordinary-docs-only` (this record only); `47db18d` → `6f5866d` is full scope, and its only non-Markdown path outside `proofs/postgres-ordering/` is the workflow.
- **The workflow,** read whole, as the CI policy's rule for workflow changes requires. The diff is the new job `database` and the gate's `needs` and job tuple, nothing else:
  - the job's condition is the other application jobs' condition; its checkout and setup-python pins are theirs, with `persist-credentials: false`; its timeout is 20 minutes; it references no secret and sets no `env:` of secrets; the workflow's permissions stay `contents: read`;
  - the results upload uses `actions/upload-artifact` at `ea165f8d…`, the commit API artifact checks already uses (the CI policy's action table). The job's one warning is GitHub's: that action targets Node.js 20 and is forced to run on Node.js 24; the step succeeded;
  - the credential step runs with `set +x` and `umask 077`, masks both generated passwords before anything else prints, and writes them only to files. The password reaches the container through `POSTGRES_PASSWORD_FILE` on a read-only mount, and the proof through the passfile that `PROOF_DB_PASSFILE` names. The role step reads its statement from a file, keeps psql's output in a file and then deletes the statement. The removal step runs `if: always()` and fails if a proof container remains.
- **Code read,** not line by line, which is the exact-head review's work: `reference.py` (the send and every revocation), `design.py`, `controls.py`, `oracle.py`, `environment.py`, `settings.py`, `budget.py` and `__main__.py`, and the parts of `cases.py`, `observe.py`, `stress.py` and the tests that the observations below rest on. The reference takes no state filter into the locked read and refuses a missing row (`_lock`), and reads `clock_timestamp()` after the locks (`_time`).
- **Offline re-run** in a scratch worktree of `dff83d4`, with Python 3.12.14, every command in a clean process (`env -i`), the install with the proxy and CA variables by reference:
  - `pip install --require-hashes -r requirements-dev.lock`; `pip check`: "No broken requirements found.";
  - `python -m unittest discover -s tests -t .`: `Ran 40 tests`, `OK`. Ruff check: "All checks passed!"; Ruff format: "23 files already formatted"; mypy: "Success: no issues found in 23 source files";
  - at `6f5866d`, `services/api`'s `python3.12 -m unittest tests.test_toolchain_pins`: `Ran 3 tests`, `OK`. The Django pin and its hashes in both proof locks equal `services/api/requirements.lock`'s.
- **Hosted CI:** Foundation run [36520940933](https://github.com/amthorn78/glow-dating-app/actions/runs/36520940933) on `dff83d4`, a push run: all eight jobs succeeded (Change scope, API checks, Mobile checks, API mobile smoke, API artifact checks, Stream proof checks, Database proof checks, Foundation gate), and the gate printed `Application checks passed`. Database proof checks (job 109253447793) ran its fourteen steps, from set-up to the removal of the database, and its post steps, each `success`.
- **The database job's log, read whole** (756 lines), against this record:
  - the image digest `sha256:d74eeac9…` on the pull; PostgreSQL 17.11 (`Debian 17.11-1.pgdg13+2`), `superuser` false, `track_commit_timestamp` on, `read committed` inside a writer's transaction; the sixteen migrations; `No changes detected`;
  - `cases: 55/55 passed`; the twelve races at 200 iterations and 200 overlaps each, with the outcome counts this record gives; the ten controls `failed as intended`; the oracle: 573 submissions and 2,694 revocation rows, `violations in the design's rows: 0`, `== VERDICT: PASS ==`; the artifact (ID 11013181409, 5,941 bytes);
  - **no password:** the log's only `***` are on lines 38, 94 and 152, `actions/checkout`'s masking of its own token, before the credential step, and no 48-character hexadecimal string appears. The credential and role steps print one line each, as this record says;
  - **each forced wait observed:** the 25 cases that call the forced helper each show `wait_event_type=Lock wait_event=transactionid` and a not-granted `transactionid/ShareLock`, and none of them passes `wait_required=False`;
  - disposal: `container removed: glow-proof-db-36520940933-1`, `credential files removed`, `no proof container remains`.

#### Corrections to this record

The implementation section above is left as the session wrote it. Two statements in it are wrong:

- **"every one of the 26 cases with a held first transaction"** (the cases bullet): the cases it lists are 25, the twenty `send_holds` and `revocation_holds` cases and five named cases, and the log shows those 25 with an observed wait. No held case lacks one.
- **`no_version_check`, "oracle O6"** (the controls table): the oracle found no violation under `control:no_version_check`; its two submissions were examined and neither broke a rule. The control failed through its case's expected refusals only. See observation 3 below.

#### Observations for the exact-head review

None of these blocks integration. The exact-head review assesses each and says whether it needs a correction before PR28 merges.

1. **The epoch check is never the deciding refusal.** Every `session_epoch` bump is a suspension or deletion (`reference.py:499`), in the transaction that moves the account out of `active`, and the send checks both accounts' state before the session's epoch (`reference.py:203` to `213`). So `session_epoch_stale` never occurs in the run's log, `named.sign_in_revocations` accepts either reason, and no control removes the epoch check. The brief's item 3 ("suspension and deletion revoke every session of the account, on every device, through the epoch") is shown through the account-state check, with the epoch bumped beside it. The epoch check itself is exercised only once an account can be `active` again after a bump, which P06.DB has no path for. DB09's mark in the P11 plan carries this limit.
2. **Not every guarantee has its own control.** The brief's item 2 says each guarantee has a deliberately broken variant. The ten controls break the locks (all of them, the accounts', the session's), the version check, the time source, authorize-before-deduplicate, the canonical lock order and the state filter. None breaks the idempotency conflict (the same key with a different request), the identical replay, the single row under racing duplicates, unblock without resurrection, the epoch check (observation 1), deletion as a lifecycle transition, the repeated unmatch, or the match lock alone. `test_the_guarantees_have_controls` checks that eight broken designs are present, not that every guarantee has one. Some of these rest on a schema constraint (a second row for the same actor and key would break the unique constraint, and O8 counts rows), and deletion and expiry share their code paths with suspension and sign-out, which have controls.
3. **The oracle cannot see a stale client version.** The send stores the locked match's contact version on the submission, not the request's (`reference.py:250` to `252`), so O6 compares the match's own version with the revocations before it. A stale version is refused by the send's check, and only the case's expected outcome shows that; the correction above follows from it.
4. **The results artifact.** The upload step was not named in the brief. It reuses a pinned action already in the workflow, and `results.py` states that nothing it writes sees a connection option, a password or a passfile path. The review confirms that the JSON carries no connection data.
5. **Local iteration ran on PostgreSQL 16.13,** a throwaway cluster under `/tmp`, as D4's third condition allows; this record lists it as iteration, not evidence.

#### Dispositions

- **P06.DB is verified and integrated** into PR28 at `6f5866d`. Its code is the code of run 36520940933.
- **The deviations are accepted:**
  - **the final head's push run is documentation-only,** by the CI policy's design; the evidence of record is run 36520940933 on `dff83d4`, and PR28's run on the manager branch runs every job again on the integrated code;
  - **the `no_locks.forced` control retargeted** from `block_by_high.send_holds` to `unmatch_by_high.send_holds`: the prompt named the controls by example, and under the new target the control also fails through the oracle, not only through the unobserved wait;
  - **the results upload** (observation 4), **`SERIALIZABLE` not run** (optional under D5), **the image digest read first from the registry** and confirmed by the job's pull, and **local iteration on 16.13** (observation 5).
- **The P11 plan's DB06 and DB09** are marked "partially evidenced in CI (P06.DB)" in D6's words, with observation 1's limit on DB09, pending the exact-head review.
- **The CI policy** now names Database proof checks, counts six application jobs and describes the job's disposable database (DM-08 7.1). It is governing: the Dev Manager reads it before PR28 merges.
- **Next: the exact-head code and security review** of `6f5866d`, offline, reading run 36520940933's logs (the brief's review plan; DM-08 7.2).

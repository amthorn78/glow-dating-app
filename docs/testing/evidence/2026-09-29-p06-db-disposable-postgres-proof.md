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
- **DB06, partially evidenced in CI (P06.DB), in D6's words:** on PostgreSQL 17, the reference design orders send authorizations against block, unmatch, suspension, deletion and sign-out, with the guarantees listed in the brief's item 2, under forced and randomized races. All 55 cases passed; every "while it holds the locks" case was observed waiting in `pg_stat_activity` and `pg_locks`; the commit-order oracle found zero violations over every row the design wrote; the twelve stress races each completed 200 iterations with zero violations, and the log printed 200 measured overlaps for each (corrected in P06.DB-C1; the exact-head review's F1): the run established the first race's count only, `race.block_by_low`'s 200 of 200, because the measure read every race's rows at the same iteration number; it did not establish the other eleven races' counts, and `race.racing_duplicates`'s own overlap was never measured. The corrected per-race counts are in "P06.DB-C1 corrections" at the end of this record; all ten negative controls failed in the same run.
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

**How an overlap is measured (6.3).** Each writer's transaction interval is read from the database: its start is `now()` inside the transaction (the proof-log row's `xact_start` default) and its end is `pg_xact_commit_timestamp(xmin)` of the row it wrote; a writer that was refused rolled back, so its start (`now()`) and end (`clock_timestamp()` read just before the rollback) are recorded afterwards in an attempt row. An iteration overlapped when the send's interval and a revocation's interval intersect (`start1 < end2 and start2 < end1`). Observed lock waits are the forced cases' measure, not the stress run's. (corrected in P06.DB-C1; the exact-head review's F1) The rows were read by run tag and iteration only, not by race, and every design race shares the tag `design:stress` and numbers its iterations from 1. From the second race on, an iteration therefore counted if any earlier race's rows at the same iteration number overlapped, and `race.racing_duplicates`, whose two writers are both sends, could never count its own rows. The run established the first race's count only, `race.block_by_low`'s 200 of 200; the other eleven races' counts were not established, and the duplicates race's own overlap was never measured. P06.DB-C1 reads each race's own rows (by `case_id` too) and counts, in the duplicates race, the two sends' intervals; its corrected counts are in "P06.DB-C1 corrections" at the end of this record.

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

| Race | Iterations | Overlaps (as printed; see the correction below) | Seconds | Outcomes |
|---|---|---|---|---|
| `race.block_by_low` | 200 | 200 (established) | 4.5 | send authorized 41, refused `match_not_active` 159; block applied 200 |
| `race.block_by_high` | 200 | 200 (not established) | 6.1 | send authorized 44, refused 156; block applied 200 |
| `race.unmatch_by_low` | 200 | 200 (not established) | 4.5 | send authorized 54, refused 146; unmatch applied 200 |
| `race.unmatch_by_high` | 200 | 200 (not established) | 4.3 | send authorized 50, refused 150; unmatch applied 200 |
| `race.suspend_low` | 200 | 200 (not established) | 5.8 | send authorized 36, refused `account_not_active` 164; suspend applied 200 |
| `race.suspend_high` | 200 | 200 (not established) | 4.5 | send authorized 19, refused 181; suspend applied 200 |
| `race.delete_low` | 200 | 200 (not established) | 5.0 | send authorized 42, refused 158; delete applied 200 |
| `race.delete_high` | 200 | 200 (not established) | 5.5 | send authorized 24, refused 176; delete applied 200 |
| `race.sign_out_sender` | 200 | 200 (not established) | 4.1 | send authorized 6, refused `session_not_valid` 194; sign-out applied 200 |
| `race.expire_sender` | 200 | 200 (not established) | 4.4 | send authorized 14, refused 186; expiry applied 200 |
| `race.racing_duplicates` | 200 | 200 (not established; its own overlap never measured) | 7.6 | one authorized and one replayed in every iteration (first request authorized 122 times, second 78); one row per key |
| `race.opposing_writers` | 200 | 200 (not established) | 6.3 | send refused 200 (`match_not_active` 192, `account_not_active` 8); both blocks and the suspension applied 200; no deadlock |

  The overlaps column (corrected in P06.DB-C1; the exact-head review's F1): only `race.block_by_low`'s 200 of 200 is established by this run; the other eleven counts are the log's figures and are not established, and `race.racing_duplicates`'s own overlap was never measured. The corrected per-race counts are in "P06.DB-C1 corrections" at the end of this record. The iterations, seconds, outcomes and violations of every race are unaffected.

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
| Run 1 (before the `no_locks.forced` control was retargeted from `block_by_high.send_holds` to `unmatch_by_high.send_holds`) | PASS: 55/55 cases; twelve races at 200 iterations and 200 overlaps each as printed (corrected in P06.DB-C1; the exact-head review's F1): only the first race's 200 is established, the other eleven counts are not, and the duplicates race's own overlap was never measured; the corrected counts are in "P06.DB-C1 corrections"; 4.1 to 7.9 s per race; ten controls failed as intended (stress controls at iteration 1); 593 submissions and 2,694 revocation rows examined, zero design violations; 1 min 15 s |
| Run 2 (the pushed code, same database, rows accumulating) | PASS: 55/55 cases; twelve races at 200 iterations and 200 overlaps each as printed (corrected in P06.DB-C1; the exact-head review's F1): only the first race's 200 is established, the other eleven counts are not, and the duplicates race's own overlap was never measured; the corrected counts are in "P06.DB-C1 corrections"; 4.5 to 8.6 s per race; ten controls failed as intended, `no_locks.forced` now with a committed violation (send committed after the unmatch) and the wait not observed; 1,190 submissions and 5,388 revocation rows examined, zero design violations; 1 min 26 s |

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
- **Limits:** the oracle treats equal commit timestamps as violations and none occurred; overlaps are measured from database-clock intervals, not from observed lock waits (corrected in P06.DB-C1; the exact-head review's F1): the run's per-race overlap counts rest on a measure that read every race's rows at the same iteration number, so only the first race's 200 of 200 is established, the other eleven races' counts are not, and `race.racing_duplicates`'s own overlap was never measured; the corrected counts are in "P06.DB-C1 corrections" at the end of this record; the controls are broken variants of this package's own reference design and show what the suite detects, not every way an adapter could be wrong; the design is proven in the proof package, not in the app.

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
  - the results upload uses `actions/upload-artifact` at `ea165f8d…`, the commit Mobile checks already uses (the CI policy's action table). (Corrected after the exact-head review, F6: this said API artifact checks; AM5-12.) The job's one warning is GitHub's: that action targets Node.js 20 and is forced to run on Node.js 24; the step succeeded;
  - the credential step runs with `set +x` and `umask 077`, masks both generated passwords before anything else prints, and writes them only to files. The password reaches the container through `POSTGRES_PASSWORD_FILE` on a read-only mount, and the proof through the passfile that `PROOF_DB_PASSFILE` names. The role step reads its statement from a file, keeps psql's output in a file and then deletes the statement. The removal step runs `if: always()` and fails if a proof container remains.
- **Code read,** not line by line, which is the exact-head review's work: `reference.py` (the send and every revocation), `design.py`, `controls.py`, `oracle.py`, `environment.py`, `settings.py`, `budget.py` and `__main__.py`, and the parts of `cases.py`, `observe.py`, `stress.py` and the tests that the observations below rest on. The reference takes no state filter into the locked read and refuses a missing row (`_lock`), and reads `clock_timestamp()` after the locks (`_time`).
- **Offline re-run** in a scratch worktree of `dff83d4`, with Python 3.12.14, every command in a clean process (`env -i`), the install with the proxy and CA variables by reference:
  - `pip install --require-hashes -r requirements-dev.lock`; `pip check`: "No broken requirements found.";
  - `python -m unittest discover -s tests -t .`: `Ran 40 tests`, `OK`. Ruff check: "All checks passed!"; Ruff format: "23 files already formatted"; mypy: "Success: no issues found in 23 source files";
  - at `6f5866d`, `services/api`'s `python3.12 -m unittest tests.test_toolchain_pins`: `Ran 3 tests`, `OK`. The Django pin and its hashes in both proof locks equal `services/api/requirements.lock`'s.
- **Hosted CI:** Foundation run [36520940933](https://github.com/amthorn78/glow-dating-app/actions/runs/36520940933) on `dff83d4`, a push run: all eight jobs succeeded (Change scope, API checks, Mobile checks, API mobile smoke, API artifact checks, Stream proof checks, Database proof checks, Foundation gate), and the gate printed `Application checks passed`. Database proof checks (job 109253447793) ran its fourteen steps, from set-up to the removal of the database, and its post steps, each `success`.
- **The database job's log, read whole** (756 lines), against this record:
  - the image digest `sha256:d74eeac9…` on the pull; PostgreSQL 17.11 (`Debian 17.11-1.pgdg13+2`), `superuser` false, `track_commit_timestamp` on, `read committed` inside a writer's transaction; the sixteen migrations; `No changes detected`;
  - `cases: 55/55 passed`; the twelve races at 200 iterations and 200 overlaps each, with the outcome counts this record gives (the log's figures: the exact-head review's F1 found the overlap counts of races 2 to 12 not established by the run); the ten controls `failed as intended`; the oracle: 573 submissions and 2,694 revocation rows, `violations in the design's rows: 0`, `== VERDICT: PASS ==`; the artifact (ID 11013181409, 5,941 bytes);
  - **no password:** the log's only `***` are on lines 38, 94 and 152, the masking of the token that `actions/checkout` (lines 38 and 94) and `actions/setup-python` (line 152) each receive, before the credential step (corrected after the exact-head review: this said all three were checkout's; AM5-12), and no 48-character hexadecimal string appears. The credential and role steps print one line each, as this record says;
  - **each forced wait observed:** the 25 cases that call the forced helper each show `wait_event_type=Lock wait_event=transactionid` and a not-granted `transactionid/ShareLock`, and none of them passes `wait_required=False`;
  - disposal: `container removed: glow-proof-db-36520940933-1`, `credential files removed`, `no proof container remains`.

#### Corrections to this record

The implementation section above is left as the session wrote it. Three statements in it are wrong (the third added after the exact-head review):

- **"every one of the 26 cases with a held first transaction"** (the cases bullet): the cases it lists are 25, the twenty `send_holds` and `revocation_holds` cases and five named cases, and the log shows those 25 with an observed wait. No held case lacks one.
- **`no_version_check`, "oracle O6"** (the controls table): the oracle found no violation under `control:no_version_check`; its two submissions were examined and neither broke a rule. The control failed through its case's expected refusals only. See observation 3 below.
- **"all `actions/checkout`'s masking of its own token"** (the log bullet): line 152 is `actions/setup-python`'s `token` input; lines 38 and 94 are checkout's. None is a password (added after the exact-head review; AM5-12).

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

### Exact-head review of P06.DB (29 September 2026)

Nathan ran the review session from revision 1 of the [review prompt](../../ephemeral/2026-09-29-p06-db-review-prompt.md) (records commit `dda1ed4`), in `Glow App - No Stream`, on Fable 5.1 at max, the cell TypeSafe v6 read. He relayed its report to App Manager 5 the same day. It reviewed the exact head `6f5866d505c5fd94ad9224ab9b23ba4e3bafaef5`.

- **Verdict: changes required, narrowly.** The design, the job and its credential handling are sound, and nothing in the run is a false pass of the ordering guarantees.
- **One should-fix finding is in a correction class** (F1, "make DB06's mark claim more than the run shows"): the stress run's per-race overlap count reads every race's log rows at the same iteration number, so only the first race's count is established.
- **One should-fix finding outside the classes** (F2): the oracle's O2 misses a send stored at the version a revocation set. **Four nits** (F3 to F6).
- **Everything else is confirmed:** DM-08 7.2's three log checks, the workflow, the artifact's contents, the scope, and all of the manager's corrections, observations and dispositions.

#### The report, as relayed

The session's notes before its report, as relayed, verbatim:

> I'll start with the environment check (names only), then the start gate and the three classifications, before reading the change and running the offline checks.
>
> Environment check passed — none of the sensitive env vars (DATABASE_URL, HD_API_KEY, GEO_API_KEY, PG*, PROOF_DB_*, STREAM_*) are set, and Python 3.12.14 is available. Moving on to the start gate now.
>
> All start-gate checks pass. Now the three classifications with the trusted base policy.
>
> All three classifications matched expectations. Moving on to the reading phase, starting with the file list, modes, and governing documents.
>
> I'm reading the DM-08 report and the manager's disposition, then the evidence record, the data-model rules and the code. Continuing with the rest of DM-08 and the DM README section.
>
> I've wrapped up the governing documents and session evidence. Now I'll pull the workflow diff/full workflow, proof package sources/tests, persistence models/migrations, API forbidden list/pin test, and the later commit's records all together.
>
> I'll read through the proof package's sources, including the saved reference design, other modules, tests, persistence models, and related records in parallel.
>
> I'll pull in the remaining independent modules—cases, observation, oracle, stress, control, result, tests, persistence models, and later records—together now.

The report, verbatim, with its headings moved down to fit this record:

**Review report: P06.DB exact-head review of `6f5866d505c5fd94ad9224ab9b23ba4e3bafaef5`**

Prompt received: revision 1, from commit `dda1ed4135acb914791b0eb6ce7ae8a5203c1d67`.

Environment check, names only: none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` is set. No `PG*`, `PROOF_DB_*` or `STREAM_*` name is set. `command -v python3.12` printed `/root/.local/bin/python3.12`, Python 3.12.14, with `$HOME/.local/bin` first on PATH in every proof process.

Head reviewed: `git rev-parse HEAD` printed `6f5866d505c5fd94ad9224ab9b23ba4e3bafaef5`. `HEAD^2` is `074eea18a04cf60d8e5235f52442879262eb5fa2`, `HEAD^1` is `9768fcc42909551786784c561a869d3cc7fa20f6`, the one merge base with `origin/main` is `47db18dfec3f62626f4e09f65f52c7a2e10c9e3e`, `dda1ed4` descends from the head, the diff is 31 files, 5,072 insertions, 2 deletions, and the diff of `proofs .github services scripts apps packages` against `dff83d4` is empty. The trusted policy from `main`, sha256 `dec69a26…`, run with `python3 -I` outside the tree:

1. `47db18d` → `6f5866d`: `{"full": true, "reason": "behavior-or-empty", …}`, 42 paths. The only non-Markdown paths are `proofs/postgres-ordering/**` and `.github/workflows/foundation.yml`; the exclusion command printed nothing.
2. `47db18d` → `9768fcc`: `{"full": false, "reason": "ordinary-docs-only", …}`, 11 Markdown paths.
3. `6f5866d` → `dda1ed4`: `{"full": false, "reason": "ordinary-docs-only", …}`, 10 Markdown paths.

PR28's head has since moved to `49525a6` (one records-only commit after `dda1ed4`). I fetched it and classified `6f5866d` → `49525a6`: `ordinary-docs-only`, the same 10 Markdown paths, no non-Markdown change. This review still covers the exact head `6f5866d`.

##### Verdict and findings

**Verdict: changes required, narrowly.** The proof's design, the job and its credential handling are sound, and nothing in the run is a false pass of the ordering guarantees. One should-fix finding falls in a correction class: the stress run's per-race overlap count is contaminated across races, so the evidence record's stress numbers claim a measurement the run did not make. Correct that code and the record, then PR28 can go to the Dev Manager's read and the merge. No finding is blocking.

**F1. Should fix, in class "make DB06's mark claim more than the run shows".** `proofs/postgres-ordering/glow_ordering_proof/stress.py:111` to `131`. `_intervals` selects the log rows by `run_tag` and `iteration` only, never by the race (`case_id`), and `_overlapped` needs one `send*` interval and one non-send interval. Every design race runs under the one tag `design:stress` with iterations 1 to 200, so race k at iteration N also sees the rows of races 1 to k−1 at iteration N. An iteration counts as overlapped if any earlier race's iteration N overlapped. The 10-overlap floor of the brief's item 6.3 is therefore enforced for the first race only. `race.racing_duplicates` cannot measure its own overlap at all, because both of its rows are `send` and `send_attempt`, yet it reports 200 of 200; those are inherited. I confirmed this offline against the installed package: a duplicates iteration with plainly concurrent intervals returns `False`, and a disjoint iteration plus an earlier race's overlapping rows returns `True`; the SQL's `WHERE` clause is `run_tag = %s AND iteration = %s AND kind <> 'sign_in'`. Fix: add `AND case_id = %s` with the race id, and for the duplicates race count an overlap when any two writers' intervals intersect. Record: the DB06 summary bullet ("each completed 200 iterations with 200 measured overlaps"), the stress table's overlaps column and the "How an overlap is measured" paragraph must say that the per-race counts for races 2 to 12 are not established by the run, that the first race's 200 of 200 is clean, and that the duplicates race's overlap was never measured; the README's "How a pass is judged" bullet on the stress run and its limits line need the same. Whether to rerun the two-minute job with the fix before the mark stands is the manager's call; I recommend it, since the corrected code yields real per-race numbers. The interleaving of the construction itself is independently shown: both stress controls, using the same barrier start and seeded head start, produced a stale commit at iteration 1.

**F2. Should fix, not in a correction class.** `oracle.py:187` to `196`. O2 flags a contact revocation of S's match only when its version exceeds S's. The send stores the locked match's version, so a send that committed after a block or unmatch at that match's new version passes O2 and O6. I showed this offline with constructed rows: a submission at v2 committed after a block at v2 yields no violation. Under the reference design this cannot occur, and the named and forced cases catch a design that ignores match state (`sequential_send_first` sends at the new version and expects `match_not_active`; `unblock_no_resurrect`), so the suite fails. But the oracle "over every row" does not encode the brief's invariant that no send commits after any revocation that invalidates it, and when P06.2 runs this suite's stress races against the adapter, an adapter that checks versions but not match state would pass the oracle. Fix: in O2, flag any contact revocation with a version of S's match that committed before or with S, regardless of the version comparison; keep O6. Not in a class because the suite as it stands would still fail.

**F3. Nit.** `controls.py:163` and `186`. A forced control counts as "failed as intended" on any case failure, a harness error included, and a stress control on any harness failure, not only its intended signal. In this run every control's recorded signal is the intended one: unobserved waits with commit order and oracle violations, expected-refusal mismatches, the deadlock, and O2/O6, O3, O4, O5 violations. Fix: require the expected signal, such as an oracle violation or the named expectation. Not in a class.

**F4. Nit.** `observe.py:168` to `223`. The wait observation confirms `wait_event_type = 'Lock'` and a not-granted `pg_locks` entry for the arriver, but not which backend blocks it. Only two writer connections exist in a forced case, so the wait can only be on the holder; `pg_blocking_pids(pid)` would record that explicitly. Not in a class.

**F5. Nit, records.** The brief's D5 says the account locks "and each account's `blocks_version`" order a first block against a send. The send never reads `blocks_version`; the account locks alone do the ordering in P06.DB, which is sufficient, and the counter is bumped for discovery's snapshot use. Not in a class.

**F6. Nit, records.** The results upload's pin `actions/upload-artifact@ea165f8d…` targets Node.js 20 and GitHub warns it is forced onto Node.js 24. It is the pin Mobile checks already uses, and the step succeeded. Track it in the CI policy's action table. Not in a class.

##### Checks and confirmations

**DM-08 7.2 from the database job's log,** job 109253447793, read whole, 756 lines:

- **No password: confirmed.** The three `***` are on lines 38, 94 and 152, `actions/checkout`'s and `setup-python`'s token masking, before the credential step at line 289. No 48-character hexadecimal string appears; the only long hex runs are 40 characters (action SHAs) and 64 (the image digest, the container id, the artifact zip digest). The credential step prints one line, the role step one line, and no connection option, passfile content or connection string appears.
- **Each forced wait observed: confirmed.** 25 cases hold a first transaction: the twenty `send_holds` and `revocation_holds` cases, `racing_duplicates`, `session_expires_during_wait` and the three pairwise opposing-writer cases. Each shows `pid 98 wait_event_type=Lock wait_event=transactionid pg_locks not granted: transactionid/ShareLock` after 1 or 2 polls. The artifact lists 25 cases with waits and none unobserved, and `wait_required` is never passed as `False`.
- **Ten controls failed in the same run: confirmed,** with `no_locks.stress` and `no_account_lock.stress` at first failing iteration 1 and 1, and the oracle's violations by tag exactly as the record's oracle summary says.

**The workflow: confirmed** as exactly the new `database` job plus the gate's `needs` and job tuple. The six application jobs share one `if:` string; the job has the other jobs' checkout and setup-python pins, `persist-credentials: false`, `python-version '3.12.14'`, `timeout-minutes: 20`, no job-level `env:`, and no `secrets.` reference; permissions stay `contents: read`; the gate's documentation-only message is unchanged. Run 36520940933 on `dff83d4`: all eight jobs `success`, and the gate printed `Application checks passed` with `database: success` in `RESULTS`. PR28's latest pull-request run is 36529602797, event `pull_request`, head `49525a6`, which contains `6f5866d`: all eight jobs `success`, and Database proof checks, job 109280113746, ran its fourteen steps through the database removal, not skipped.

**The results artifact:** I downloaded artifact 11013181409 through the API, 5,941 bytes, zip sha256 `e0efe199…` matching the log. `results.json` holds no password, passfile path, `PROOF_DB_` name, host, port, runner path or connection string, and no hex run of 32 or more characters. Its verdict is PASS with no reasons, and its cases, races, controls and oracle counts match the log and the record.

**Checks run, exact results:**

| Check | Result |
|---|---|
| `git diff --check HEAD^1 HEAD` | clean, exit 0 |
| The three classifications, plus `6f5866d` → `49525a6` | as listed above |
| `python3.12 -m venv .venv`; `pip install --require-hashes -r requirements-dev.lock` in `env -i` with proxy and CA variables by reference; `pip check` | installed 12 packages; `No broken requirements found.` |
| `env -i PATH HOME LANG .venv/bin/python -m unittest discover -s tests -t .` | `Ran 40 tests`, `OK` |
| `.venv/bin/ruff check .`; `.venv/bin/ruff format --check .`; `.venv/bin/mypy` | `All checks passed!`; `23 files already formatted`; `Success: no issues found in 23 source files` |
| `cd services/api && python3.12 -m unittest tests.test_toolchain_pins` | `Ran 3 tests`, `OK` |
| Secret scan over `git diff HEAD^1 HEAD` | no value of any kind; the 49 lines matching secret words are variable names, comments, the credential step's own text, test fixtures with `x`, and the placeholder `SECRET_KEY`; no email address; long hex outside the locks is the three action pins, the image digest and commit SHAs in the record; every lock line is a pin, a `--hash=sha256:` line, a comment or blank, 420 hash lines |
| Locks | Django 5.2.17 with hashes byte-identical to `services/api/requirements.lock` in both proof locks; Ruff 0.16.8 and mypy 2.3.1 as the API's dev lock; `psycopg[binary]` 3.3.6 is the one new runtime dependency, no allauth |
| Throwaway offline tests, no connection opened | `_overlapped` behaviour as F1 states; the oracle on constructed rows flags O1 to O8 as documented and shows F2's gap |
| Scope | 31 paths, all mode 100644, no symlink; nothing under `services/`, `scripts/`, `apps/`, `packages/` or `.gitignore` changed; the package imports nothing from the API but `glow_persistence` |

##### Records, marks, dispositions and limits

**Areas reviewed with no findings.** The send's pre-lock reads are the match pair and the session's account only, immutable in the models and untouched by every writer. The lock order is lower account, higher account, match, session, each by primary key with `FOR UPDATE`, time is `clock_timestamp()` after the locks, checks run on the rows as locked in the stated order, authorization precedes deduplication, and the submission, its outbox event and the log row commit in one transaction. Every revocation takes locks the send takes in a consistent global order, so no interleaving under `READ COMMITTED` lets a send pass on a replaced row version, no writer can deadlock the design, and no contact revocation skips a lock. The block check reads unlocked rows only under the account locks every block writer takes. Deletion is the lifecycle transition with its job and tombstone. The four retry rules behave as D5 says, and the racing duplicates yield one row with no constraint error. The settings refuse every forbidden and `PG*` name at import, accept loopback or an absolute socket path only, and give an explicit passfile with SSL and GSS disabled and no service name, so no libpq default file applies. The credential step, the container's loopback publish, the read-only password mount, the digest pin, `track_commit_timestamp=on`, the `NOSUPERUSER` role with `superuser false`, and the `if: always()` removal that fails if a proof container remains are as the brief requires. Bindings are never revoked in the package, which is the provider half left to P06.2.

**The manager's two corrections:** agree with both. 25 held cases, not 26, as the log and artifact show. `no_version_check` produced no oracle violation; its `oracle_violations` is 0 in the artifact and its signal carries no oracle suffix.

**The manager's five observations:** agree with all five. On observation 1, `session_epoch_stale` occurs nowhere in the log or the artifact. On observation 2, I checked each guarantee without its own control: the idempotency conflict, the identical replay, the single row under racing duplicates, unblock without resurrection, deletion as a lifecycle transition and the repeated unmatch would each be caught deterministically by their named case, not by the oracle; the epoch check alone would not be caught by anything, which the DB09 limit already states; and a control that drops only the match lock would not fail, because the account locks alone order every writer here, so that gap is expected. Nothing there changes DB06's mark. On observation 3, agree, and recording the request's version in the log row would let O6 see it. On observation 4, the artifact carries no connection data, confirmed by download. **Dispositions:** agree with all, subject to F1's correction.

**The marks.** DB06 is accurate as worded, but the evidence record behind it must carry F1's correction; if the manager prefers a limit line: "the stress run's per-race overlap counts are not established for eleven of the twelve races; the randomized construction's interleaving is shown by the stress controls failing at their first iteration". DB09 is accurate as worded with its limit; an optional addition: "O7 checks the stored epoch's consistency, but no case or control exercises the epoch check as the deciding refusal".

**The records.** The session's section agrees with the code and the run apart from the two corrected statements and F1's overlap numbers, which the run does not establish. The README matches the code, with F1's stress bullet needing the same correction. The CI policy at `dda1ed4` describes the job as built.

**Limits.** No database was started, and the run was not repeated; the log, the artifact and the runs were read through the GitHub API. PostgreSQL's ordering of commit timestamps behind lock release, which makes ties impossible in the design's rows, rests on documented behaviour and was not tested here. The local iteration runs on PostgreSQL 16.13 cannot be verified and count for nothing. Notion was not read. I changed nothing in the repository, on GitHub or in Notion; only the ignored `.venv/` and my scratchpad hold scratch work.

#### Manager verification of the review (App Manager 5, 29 September 2026)

- **F1: confirmed in the code.**
  - `stress.py:111` to `125`: `_intervals` selects `WHERE run_tag = %s AND iteration = %s AND kind <> 'sign_in'`, although `run_race` sets `case_id = race.id` for every log row it writes (`:234`) and restarts `iteration` at 1 for each race (`:233`).
  - Every design race runs under one tag. From the second race on, an iteration's intervals therefore include the earlier races' rows at the same iteration number, and `_overlapped` (`:128` to `:131`) counts the iteration if any pair among them overlapped.
  - `race.block_by_low` runs first, so its 200 of 200 is clean. The other eleven races' counts are not established.
  - `race.racing_duplicates`'s two writers are both sends (`:180` to `:183`), so its own rows can never count.
  - Not affected: the per-race oracle attribution (`attach_oracle`, `:287` to `:293`, which filters by `case_id`), and each race's outcome counts, which come from its own results.
- **F2: confirmed.** `oracle.py:190` flags O2 only when the revocation's version exceeds the send's, and the send stores the locked match's version (`reference.py:250` to `252`).
- **F3 and F4:** as the review describes; both are nits.
- **F5: confirmed.** The brief's D5 says the account locks "and each account's `blocks_version`" order a first block against a send. The send reads no `blocks_version`. The block writers bump it (`reference.py:350`, `:414`), the cases check the bump (`cases.py:274`, `:617`), and the account locks do the ordering.
- **F6: confirmed, and it corrects the manager's verification.** The upload pin was already used by Mobile checks, in its step "Save empty-form layout evidence" (`foundation.yml:112`), not by API artifact checks as the verification said.
- **The log's three `***`:** lines 38 and 94 are `actions/checkout`'s; line 152 is `actions/setup-python`'s `token` input. The session's record said all three were checkout's, and the manager's verification repeated that without deriving it. None is a password, so no conclusion changes. This slip and F6's are AM5-12.
- **The review's other statements** agree with the manager's own reading: the start gate, the classifications, DM-08 7.2's three checks, the workflow, CI on `49525a6` and the scope. The review downloaded the artifact; the manager did not.

#### Disposition

- **F1 is in a correction class.** P06.DB-C1, an offline correction pass, fixes the measurement with a test. It reruns the job on its head for real per-race overlap counts, and corrects in place the record's statements that rest on the old counts: the DB06 summary bullet, the stress table's overlaps and the overlap paragraph, and the README's stress bullet and limits line. Until C1's run, the randomized part of DB06's evidence rests on the first race and on the two stress controls failing at their first iteration. The P11 plan's DB06 mark carries that limit.
- **F2 goes into C1.** O2 is to flag any applied contact revocation of the send's match that committed before or with the send, whatever its version; O6 stays. In P06.DB a block or unmatch is never undone for its match (an unblock leaves the match `restricted`, and there is no rematch), so the stronger rule holds for every row the design writes.
- **F3 and F4 go into C1,** each with a test. A control counts as failed as intended only by its own expected signal. A forced case records the blocking backend with `pg_blocking_pids` and requires it to be the holder's.
- **F5:** the manager corrected D5's sentence in the brief. The account locks order a first block against a send; each block also bumps the blocking account's `blocks_version`, the persistent account revision, which the send does not need to read because it holds both account locks. The design is unchanged.
- **F6:** the CI policy's action table now records the Node.js 20 warning, and that Mobile checks and Database proof checks share the pin. A newer pin is a later change, not P06.DB's. The manager's verification is corrected in place (AM5-12).
- **Observation 3** (the oracle cannot see a stale client version) stays a recorded limit. The named case and the `no_version_check` control catch a missing version check deterministically, as the review confirms.
- **The marks:** DB06 stands as worded, pending C1, with F1's interim limit. DB09 stands, and its limit takes the review's more precise wording.
- **Next:** the P06.DB-C1 correction prompt, then C1's exact-head review. After that come the Dev Manager's read of PR28's governing changes, Codex's review and the merge.

## P06.DB-C1 corrections

The correction pass on P06.DB: the exact-head review's F1 to F4, each with an offline test, and a rerun of the job for real per-race overlap counts.

- **Prompt:** revision 1, from commit `4511bbc65382617dc58461394351763d114a832b` (`docs/ephemeral/2026-09-29-p06-db-c1-correction-prompt.md`).
- **Session:** branch `claude/confident-knuth-b9d0c2`, started from `4511bbc65382617dc58461394351763d114a832b` (fast-forwarded from the manager branch `claude/magical-wozniak-yfmmx2`); `git diff --stat 6f5866d… HEAD -- proofs/ .github/` printed nothing at the start.
- **Code head:** `42807705d374a4d532b1c4fb203d3f4be1cef438`. **New run of record:** Foundation run 36534514283 on that head (push run 411). Its jobs and the run-level conclusion are below.
- **Records commits:** `60b6b70` (the in-place corrections above) and the commit that adds this section. Both change only this Markdown file, so their push runs are documentation-only by the CI policy's design.
- **Times:** 29 September 2026, UTC.

### Environment check (names only)

| Check | Result |
|---|---|
| `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` | none present (the loop printed nothing) |
| `PG*`, `PROOF_DB_*`, `STREAM_*` names | none (`compgen -e \| grep -E …` printed nothing) |
| `command -v python3.12` | `/root/.local/bin/python3.12`, Python 3.12.14 (`$HOME/.local/bin` first on PATH) |
| `docker info` | exit status 1 |
| `command -v initdb pg_ctl postgres pg_isready psql` | `pg_isready` and `psql` at `/usr/bin`; `initdb`, `pg_ctl`, `postgres` not on PATH, present in `/usr/lib/postgresql/16/bin/` (PostgreSQL 16.13) |

### F1 to F4

| Finding | Fixed where | Test (offline, no database) |
|---|---|---|
| **F1** each race measures its own overlaps | `stress.py:118` `_intervals(run_tag, case_id, iteration)` selects `WHERE run_tag = %s AND case_id = %s AND iteration = %s` (`:128`); `stress.py:140` `_overlapped(race_kind, intervals)`: a two-writer or opposing race counts the send's interval against any revocation's, `race.racing_duplicates` any two sends'; `run_race` passes the race (`:294`), and the stop-at-first-violation oracle check passes `case_id=race.id` (`:297`), which `oracle.evaluate` applies as `l.case_id = %s` (`oracle.py:141`). The floors (50 iterations, 10 overlaps) and the budget (200 iterations or 30 s) are unchanged | `tests/test_stress_overlap.py`: `_overlapped` for each race kind, the duplicates race intersecting and disjoint, revocations that overlap only each other; the per-race selection through a cursor stand-in that applies the query's own `column = %s` conditions (rows of two races at iteration 1 count only for their own race); the per-iteration oracle query names the race |
| **F2** O2 catches any send after a contact revocation | `oracle.py:220`: O2 flags every applied contact revocation of the send's match (a block or unmatch whose log row carries a contact version) that committed before or with the send, whatever its version; O6 stays. The rules are split from the fetches (`oracle.py:187`, `judge`). The docstring (`oracle.py:12`) and the README say why the stronger rule must hold for every row the design writes: a block or unmatch is never undone for its match in P06.DB | `tests/test_oracle_rules.py`, with the oracle's fetches replaced by constructed rows: a submission at v2 committed after a block at v2 is an O2 violation; committed before the block, it is not; an unmatch at any version; equal timestamps; a block without a contact version is not a contact revocation; and O1 to O8 still flag what they flagged |
| **F3** a control fails as intended only by its own signal | `cases.py:111` onwards: the case judge records a signal with each failure (`wait_not_observed`, `commit_after_revocation`, `refusal_missing`, `deadlock`, `database_error`, `harness_error`, `other`; `outcome_signal` at `:209`). `controls.py:46` `Signal`: each control declares the case signals it must show and the oracle rules one of whose violations must appear under its tag; `judge_forced` (`:224`) and `judge_stress` (`:242`) count a control only when its declared signal is present, and never with a harness error, a database error or a stress harness failure (`DISQUALIFYING`, `:42`). The table and the JSON print each control's declared signal | `tests/test_control_signals.py`: each control's declared signal is one its broken switch can produce (a table in the test, derived from the reference design; `no_version_check` declares no oracle rule, observation 3); forced controls declare a case signal and stress controls an oracle rule; a case failing by a harness error, a database error, any other failure or the wrong signal is not counted; every part of a signal is required; a stress harness failure or a violation of another rule is not counted |
| **F4** a forced case records which backend blocks the waiter | `cases.py:271` captures the holder's pid through `on_begin`, as the arriver's is captured; `observe.py:189` `observe_lock_wait(pid, holder_pid=…)` reads `pg_blocking_pids(pid)` with the wait state (`:210`), records the blockers, and counts the wait as observed only when `waits_on_holder` (`observe.py:180`) finds the holder among them (`:218`); a wait on another backend keeps polling until the arriver finishes or the timeout | `tests/test_lock_wait.py`: the decision (a wait whose blockers do not include the holder is not observed; no lock wait is not observed), and the polling loop against a scripted cursor: blocked by another backend, not observed; blocked by the holder, observed, with the blockers recorded |

**Without the fix,** run against the package at `4511bbc` with the new tests: the four F2 tests that name the gap fail by assertion (`'O2' not found in []` and `['O6']`); the F1, F3 and F4 tests fail because the corrected functions and parameters do not exist there (`TypeError: _overlapped() takes 1 positional argument`, `_intervals() takes 2 positional arguments`, `evaluate() got an unexpected keyword argument 'case_id'`, `ImportError: cannot import name 'CASE_SIGNALS'`, `AttributeError: … 'waits_on_holder'`). All pass at the code head.

### The records corrected

Each marked "(corrected in P06.DB-C1; the exact-head review's F1)", each saying that run 36520940933 established the first race's count only (`race.block_by_low`, 200 of 200), that it did not establish the other eleven races' counts, that `race.racing_duplicates`'s own overlap was never measured, and pointing to this section:

- this record's "P06.DB implementation" section: the DB06 bullet of "Summary"; "How an overlap is measured (6.3)"; the stress table's overlaps column (with a note under the table); both local-runs rows' "200 overlaps each"; and the limits bullet under "Deviations, open questions and limits";
- the package README: the stress run's bullet under "How a pass is judged" and the overlap line under "Limits". The README also describes F2's rule, F3's declared signals and F4's blocking-backend check, and records observation 3 (the oracle cannot see a stale client version) as a limit.

"Manager verification of P06.DB" and "Exact-head review of P06.DB", with everything under them, are byte-identical to `4511bbc`.

### The new run of record: Foundation run 36534514283 on `42807705d374a4d532b1c4fb203d3f4be1cef438`

Push run 411, `https://github.com/amthorn78/glow-dating-app/actions/runs/36534514283`, started 07:04:34 UTC.

| Job | Conclusion |
|---|---|
| Change scope | success (job 109295401195; full scope) |
| API checks | success (job 109295438911) |
| Mobile checks | success (job 109295439059) |
| API mobile smoke | success (job 109295439067) |
| API artifact checks | success (job 109295439026) |
| Stream proof checks | success (job 109295439180) |
| Database proof checks | success (job 109295439073; 07:04:44 to 07:06:06 UTC; the suite step 48 s) |
| Foundation gate | success (job 109296705850, finished 07:09:03); its log line: `Application checks passed`, with every job, `database` included, `success` in its `RESULTS` |

**The run-level conclusion reads `cancelled`.** The workflow's `concurrency` group (`foundation-${{ github.ref }}`, `cancel-in-progress: true`) did this after the records push `60b6b70` at 07:05:20 queued run 36534597575 on the same branch. That run's jobs were created at 07:09:04, after run 36534514283's gate had finished at 07:09:03, and the earlier run was marked `cancelled` at 07:09:05. Every job of run 36534514283 had already completed with `success`, and no step was interrupted. Run 36534597575 (the records commit) succeeded as documentation-only: Change scope success, the six application jobs skipped, the gate success. I re-ran and dispatched nothing (the prompt forbids it). Whether a run whose jobs all succeeded but whose run-level status reads `cancelled` is acceptable as the run of record is the manager's call; see "Deviations and limits".

**From the database job's log** (797 lines, read whole):

- **The image and the server.** `Digest: sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`, the pinned digest. `SELECT version()`: `PostgreSQL 17.11 (Debian 17.11-1.pgdg13+2) on x86_64-pc-linux-gnu, compiled by gcc (Debian 14.2.0-19) 14.2.0, 64-bit`. `track_commit_timestamp` `on`; `default_transaction_isolation` `read committed`, and `read committed` inside a writer's transaction; `superuser` `false`. The sixteen migrations applied from zero, 07:05:12.14 to 07:05:13.57; `makemigrations --check --dry-run`: `No changes detected`. The offline tests in the job: `Ran 82 tests`, OK.
- **The cases:** `cases: 55/55 passed`. **Observed waits with their blocking backends:** each of the 25 held cases (the twenty `send_holds` and `revocation_holds` cases, `racing_duplicates`, `session_expires_during_wait` and the three pairwise opposing-writer cases) shows `pid 98 wait_event_type=Lock wait_event=transactionid pg_locks not granted: transactionid/ShareLock pg_blocking_pids=[97] (holder pid 97)` after 1 or 2 polls: the waiting backend was blocked by the holder's backend and by no other. In each `send_holds` case the commit timestamps put the send before the revocation.
- **The stress run** (seed 20260929; budget 200 iterations or 30 s per race; floors 50 iterations and 10 overlaps), each race counting only its own rows, every race with 0 violations and 0 harness failures and its floors met:

| Race | Iterations | Measured overlaps | Seconds | Outcomes |
|---|---|---|---|---|
| `race.block_by_low` | 200 | 200 | 3.3 | send authorized 44, refused `match_not_active` 156; block applied 200 |
| `race.block_by_high` | 200 | 200 | 3.3 | send authorized 46, refused `match_not_active` 154; block applied 200 |
| `race.unmatch_by_low` | 200 | 199 | 3.1 | send authorized 56, refused `match_not_active` 144; unmatch applied 200 |
| `race.unmatch_by_high` | 200 | 199 | 3.1 | send authorized 52, refused `match_not_active` 148; unmatch applied 200 |
| `race.suspend_low` | 200 | 178 | 2.7 | send authorized 38, refused `account_not_active` 162; suspend applied 200 |
| `race.suspend_high` | 200 | 183 | 2.7 | send authorized 24, refused `account_not_active` 176; suspend applied 200 |
| `race.delete_low` | 200 | 191 | 3.0 | send authorized 48, refused `account_not_active` 152; delete applied 200 |
| `race.delete_high` | 200 | 192 | 3.0 | send authorized 28, refused `account_not_active` 172; delete applied 200 |
| `race.sign_out_sender` | 200 | 174 | 2.7 | send authorized 16, refused `session_not_valid` 184; sign-out applied 200 |
| `race.expire_sender` | 200 | 177 | 2.9 | send authorized 21, refused `session_not_valid` 179; expiry applied 200 |
| `race.racing_duplicates` | 200 | 200 | 4.0 | one authorized and one replayed in every iteration (`send_a` authorized 120, `send_b` 80); one row per key |
| `race.opposing_writers` | 200 | 200 | 4.6 | send authorized 1, refused `match_not_active` 192, `account_not_active` 7; both blocks and the suspension applied 200; no deadlock |

  The counts now differ between races (174 to 200), as a per-race measure would; the lowest, `race.sign_out_sender`'s 174, is well above the floor of 10. `race.racing_duplicates`'s 200 is now its own two sends' intersecting intervals. The head start and the budget were not changed.

- **The negative controls,** each with its declared signal, all ten `failed as intended` (the signal met):

| Control | Declared signal | Signal in the run |
|---|---|---|
| `no_locks.forced` (`unmatch_by_high.send_holds`) | `wait_not_observed` + `commit_after_revocation` + oracle O2/O6 | the unmatch not observed waiting on the holder; the send committed 07:05:57.025615 after the unmatch at 07:05:57.021920; oracle 2 violations (O2, O6) |
| `no_locks.stress` (`race.block_by_high`) | oracle O2/O6 | first failing iteration 1: the block (v2) committed 07:05:57.080272, the send at v1 07:05:57.080445; oracle O2, O6 |
| `no_version_check` (`named.stale_contact_version`) | `refusal_missing` | sends at versions ahead and behind authorized; oracle 0 violations (observation 3) |
| `no_session_lock` (`sign_out_sender.send_holds`) | `wait_not_observed` + `commit_after_revocation` + oracle O3 | the sign-out not observed waiting; the send committed 07:05:57.196364 after the sign-out at 07:05:57.191552; oracle 1 violation (O3) |
| `transaction_start_time` (`named.session_expires_during_wait`) | `refusal_missing` + oracle O5 | the send whose session expired while it waited was authorized; oracle 1 violation (O5) |
| `dedup_before_authorize` (`named.retry_after_revocation`) | `refusal_missing` | the retry after the block was `replayed` with the old receipt |
| `inverted_lock_order` (`named.opposing_first_lock_block_high_vs_send`) | `deadlock` | `deadlock:DeadlockDetected` for the send |
| `no_account_lock.forced` (`suspend_high.send_holds`) | `wait_not_observed` + `commit_after_revocation` + oracle O4 | the suspension not observed waiting; the send committed 07:06:01.427917 after the suspension at 07:06:01.423348; oracle 1 violation (O4) |
| `no_account_lock.stress` (`race.suspend_high`) | oracle O4 | first failing iteration 1: the suspension committed 07:06:01.496925, the send 07:06:01.500259; oracle O4 |
| `filter_state_in_lock` (`unmatch_by_high.revocation_holds`) | `refusal_missing` + oracle O2/O6 | the send that arrived while the unmatch held was authorized and committed; oracle 2 violations (O2, O6) |

- **The oracle over every row,** with the stronger O2: 617 submissions and 2,694 revocation rows examined; `design:forced` 32, `design:stress` 574, the controls 1 or 2 each; **violations in the design's rows: 0**. Violations only under control tags: `no_locks.forced` 2, `no_locks.stress` 2, `filter_state_in_lock` 2, `no_session_lock` 1, `no_account_lock.forced` 1, `no_account_lock.stress` 1, `transaction_start_time` 1, as in run 36520940933. Every control that the oracle caught before still shows its oracle violations. `== VERDICT: PASS ==`.
- **Disposal:** `container removed: glow-proof-db-36534514283-1`, `credential files removed`, `no proof container remains`.
- **The results JSON:** artifact `p06-db-proof-results`, ID 11017908859, 6,179 bytes, digest `sha256:2be4f793…`, expires 13 October 2026. I did not download it.
- **No password, and no mask where a password would be.** The log's only `***` are on lines 38 and 152 (the `token` inputs of `actions/checkout` and `actions/setup-python`) and line 94 (checkout's git `AUTHORIZATION: basic ***` header), all before the credential step. The credential step prints one line (`credentials generated into a directory readable only by this job's user`) and the role step one line. The only long hexadecimal runs are 40 characters (action commits, 15) and 64 (digests and IDs, 7), with no standalone 48-character run. The words "password" and "passfile" appear only in the workflow's own script text and in the names of the offline tests. No connection option, passfile content or connection string appears.

### Local runs (iteration, not evidence)

Docker does not work in the sandbox, so I started a throwaway cluster from `/usr/lib/postgresql/16/bin/initdb`: PostgreSQL 16.13 (Ubuntu 16.13-0ubuntu0.24.04.1), run as the `postgres` OS user, in a `mktemp -d` directory under `/tmp`. It listened only on a Unix socket (`listen_addresses = ''`), with `track_commit_timestamp = on`, port 5433. The superuser's password was generated and passed through `--pwfile`, and that file was removed after initdb. The non-superuser role `glow_proof` got a generated password through a SQL file that I removed after use, and the passfile was `0600`. `pg_hba` allowed `peer` for postgres and `scram-sha-256` for everyone else, and no forbidden or `PG*` name was present. `migrate` applied the sixteen migrations and `makemigrations --check --dry-run` printed `No changes detected`.

| Run | Result |
|---|---|
| Local run 1 (before the forced controls' signal text put the oracle first) | PASS: 55/55 cases; each wait blocked by the holder (`pg_blocking_pids=[…] (holder pid …)`, 25 cases); races at 200 iterations with 200, 200, 200, 200, 200, 199, 200, 200, 198, 200, 200 and 200 overlaps; ten controls failed as intended by their declared signals; 544 submissions and 2,694 revocation rows, zero design violations; 1 min 43 s |
| Local run 2 (the pushed code, same database, rows accumulating) | PASS: 55/55; every race 200 of 200 overlaps; ten controls failed as intended; 1,084 submissions and 5,388 revocation rows, zero design violations; 115 s |

At the end I stopped the cluster (`pg_ctl stop -m fast` printed `server stopped`, and `pg_isready` then got `no response`) and removed its directory; no cluster directory and no postgres process remained. The package's `.venv/` and `.work/` are gitignored and stay only in the sandbox.

### Checks

| Check | Command | Result |
|---|---|---|
| 1 | `git diff --check 4511bbc… HEAD` | clean |
| 1 | `git diff --name-only 4511bbc… HEAD` | `proofs/postgres-ordering/README.md`, seven files under `glow_ordering_proof/` (`__main__.py`, `cases.py`, `controls.py`, `observe.py`, `oracle.py`, `results.py`, `stress.py`), six under `tests/` (`fakes.py`, `test_control_signals.py`, `test_lock_wait.py`, `test_oracle_rules.py`, `test_results.py`, `test_stress_overlap.py`), and this record; nothing else. No dependency file, workflow or `services/` path changed |
| 2 | trusted policy from `main` (`47db18d`, sha256 `dec69a26…`) extracted to a temporary directory, `python3 -I <tmp>/change_scope.py --base 4511bbc… --head 4280770… --merge-base`, run from the repository root | `{"full": true, "reason": "behavior-or-empty", …}`, 14 paths: full scope. (A first attempt run with the temporary directory as the working directory printed `comparison-unavailable`, because no repository was there; the rerun from the root is the result) |
| 3 | `python3.12 -m venv .venv`; `pip install --require-hashes -r requirements-dev.lock` in `env -i` with the proxy and CA variables by reference; `pip check` | installed; `No broken requirements found.` |
| 4 | `env -i PATH HOME LANG .venv/bin/python -m unittest discover -s tests -t .` | 40 tests at the start; at the head `Ran 82 tests`, `OK` (new: overlap 8, oracle rules 15, control signals 14, lock wait 5) |
| 4 | `.venv/bin/ruff check .`; `.venv/bin/ruff format --check .` | `All checks passed!`; `28 files left unchanged` |
| 4 | `.venv/bin/mypy` | `Success: no issues found in 28 source files` |
| 4 | the Django pin test | in the 82 (`tests/test_django_pin.py`, 4 tests) |
| 4 | `cd services/api && python3.12 -m unittest tests.test_toolchain_pins` | `Ran 3 tests`, `OK` |
| 5 | local runs | above, iteration, not evidence |
| 6 | the Foundation run on the code head | run 36534514283 above |
| 7 | secret scan over `git diff 4511bbc… HEAD` (added lines; password, secret, token, API key, private-key markers, connection strings, email addresses, hex runs of 32 or more) | no match in the code commit's added lines; this record's added lines carry only digests, commit SHAs and the words of this section |

### Deviations and limits

- **The run of record's run-level conclusion is `cancelled`,** although every one of its eight jobs, the gate included, concluded `success` and the gate printed `Application checks passed`. My records push `60b6b70`, 50 seconds after the code push, queued a run in the same `cancel-in-progress` concurrency group. The fix for future pushes is to wait for the code run to finish before pushing records; I did not re-run or push a code change only to trigger CI. If the manager needs a run whose run-level conclusion is `success`, a re-run of 36534514283 (or PR28's pull-request run after integration) gives one.
- **Control signals are declared from what each switch can produce,** and the run met every declaration. I changed the text of the `no_version_check` expectation, which named O6, to say that the case's expected refusal is its signal and that the oracle cannot see a stale client version (the manager's correction and observation 3).
- **The wait is now observed only when the holder blocks the arriver.** A wait on another backend keeps the observer polling until the arriver finishes or the 15 s timeout passes, and then the wait counts as not observed. In the run, every held case was blocked by the holder alone.
- **Local iteration ran on PostgreSQL 16.13,** not 17.11, from the sandbox's binaries (D4 condition 3), under `/tmp` because the postgres OS user cannot traverse the scratchpad's parents.
- **Observation 3 stays a limit**: the oracle cannot see a stale client version. **Observation 1 stays**: the epoch check is never the deciding refusal.
- **Not found:** anything more in the four correction classes.

### What the exact-head review must know

- The code to review is `42807705d374a4d532b1c4fb203d3f4be1cef438`; its run is 36534514283 (read job 109295439073's log). The later commits change only this record.
- **The rules that changed:**
  - the overlap measure is per race: rows by run tag, `case_id` and iteration, and the duplicates race counts its two sends;
  - O2 no longer compares versions: any applied contact revocation of the match before or with the send is a violation;
  - a control counts as failed as intended only by its declared signal, never by a harness error, a database error or a stress harness failure;
  - a forced wait counts as observed only when `pg_blocking_pids` of the waiting backend names the holder's backend.
- `oracle._Submission` and `oracle._Revocation` are renamed `SubmissionRow` and `RevocationRow`, and the rules moved into `oracle.judge`; `evaluate` reads the rows as before and calls it.
- The offline tests replace Django's connection with stand-ins in `tests/fakes.py`; no test opens a database.

### Manager verification of P06.DB-C1 (App Manager 5, 29 September 2026)

App Manager 5 checked the relayed report against the pushed branch, the code and hosted CI. The manager started no database: its re-run below is the offline checks only.

- **Identity:**
  - branch `claude/confident-knuth-b9d0c2`, final head `24e716b643b0ad0bd3f969d5c0351862a4a66321`, tree `c3c9bac548b2ad0d2ba29d1a1f1d6988c65dab5f`, as reported. Three commits on the start `4511bbc`: `4280770` (the code), then `60b6b70` and `24e716b` (this record only). The start gate holds: `git diff --stat 6f5866d 4511bbc -- proofs/ .github/` is empty;
  - 15 paths, +1,250 and −122: `proofs/postgres-ordering/README.md`, seven files under `glow_ordering_proof/`, six under `tests/` and this record. The code commit changes 433 lines of source and adds 739 lines of tests. No dependency file, workflow, `services/`, `scripts/`, `apps/` or `packages/` path changed, and `git diff --check` is clean;
  - **integrated** with a merge commit, `ea21ac8577b83158be1f941b93dbef411bece41f` (first parent `82c3883`, the manager branch; second parent `24e716b`). At the merge, its proof package and this record are byte-identical to `24e716b`'s.
- **Classification:** the trusted policy from `main` (sha256 `dec69a26…`), outside the tree, with `python3 -I` and full SHAs: `4511bbc` → `4280770` is full scope (`behavior-or-empty`), 14 paths; `4511bbc` → `24e716b` is full scope, 15 paths.
- **The diff, read whole** (`git diff 4511bbc 4280770`). Each fix is the one the prompt asked for:
  - **F1:** `_intervals` selects by run tag, `case_id` and iteration. `_overlapped` takes the race's kind and, for `race.racing_duplicates`, intersects the two sends' intervals. The per-iteration oracle check passes `case_id`, and `oracle.evaluate` applies it. The floors, the head start and the budget are unchanged;
  - **F2:** O2 flags every block or unmatch of the send's match whose log row carries a contact version and that committed before or with the send. The version comparison is gone, and O6 is unchanged. The rules moved into `oracle.judge`, which `evaluate` calls with the rows it read;
  - **F3:** each case failure carries a signal. Each control declares a `Signal`: case signals, all required, and oracle rules, one of which must appear. `judge_forced` and `judge_stress` count a control only when its signal is met, and never beside a harness error, a database error or a stress harness failure. A control that declares nothing can never count;
  - **F4:** the holder's backend pid is captured through `on_begin`. The observer reads `pg_blocking_pids` with the wait state and counts a wait only when the holder is among the blockers. A wait on another backend keeps it polling until the arriver finishes or the timeout passes.
- **Offline re-run** in a scratch worktree of `4280770`, with Python 3.12.14, every command in a clean process (`env -i`), the install with the proxy and CA variables by reference:
  - `pip install --require-hashes -r requirements-dev.lock`; `pip check`: "No broken requirements found.";
  - `python -m unittest discover -s tests -t .`: `Ran 82 tests`, `OK`. Ruff check: "All checks passed!"; Ruff format check: "28 files already formatted"; mypy: "Success: no issues found in 28 source files";
  - `services/api`'s `python3.12 -m unittest tests.test_toolchain_pins`: `Ran 3 tests`, `OK`.
- **Fix reversals,** in the manager's own run: each fix undone alone, in a fresh copy of the package at `4280770`, then its test module run.

  | Reversal | Result |
  |---|---|
  | F1: `_intervals` without its `case_id` condition | 2 of the 8 overlap tests fail |
  | F1: the duplicates race treated as a two-writer race | 2 of 8 fail |
  | F1: the per-iteration oracle check without `case_id` (`stress.py:297`) | **all 8 pass** (observation 1 below) |
  | F2: O2 compares versions again | 3 of the 15 oracle-rule tests fail |
  | F3: a forced control counts on any failure | 3 of the 14 control-signal tests fail (6 failures, counting subtests) |
  | F3: a stress control counts on any violation or harness failure | 2 of 14 fail |
  | F4: any lock wait counts | 2 of the 5 lock-wait tests fail |

- **Secret scan** over the added lines of `git diff 4511bbc 24e716b`: no password, token, key, connection string or email address. The only long hexadecimal strings are commit SHAs (40 characters) and the image digest (64).
- **Hosted CI:** Foundation run [36534514283](https://github.com/amthorn78/glow-dating-app/actions/runs/36534514283) on `4280770`, a push run. All eight jobs succeeded, and the gate (job 109296705850) printed `Application checks passed`, with every job's result `success`, `database` included.
- **The database job's log, read whole** (job 109295439073; 798 lines in the manager's download), against the section above:
  - the image digest `sha256:d74eeac9…`; PostgreSQL 17.11, `superuser` false, `track_commit_timestamp` on, `read committed`; the sixteen migrations; `No changes detected`; `Ran 82 tests`, `OK`;
  - `cases: 55/55 passed`, and each of the 25 held cases shows `pg_blocking_pids=[97] (holder pid 97)`;
  - the twelve races' iterations, measured overlaps (174 to 200), seconds and outcomes, exactly as the section's table gives them, each race with 0 violations, 0 harness failures and its floors met;
  - the ten controls, each `failed as intended` with the declared signal the section's controls table gives, the two stress controls at iteration 1;
  - the oracle: 617 submissions and 2,694 revocation rows, `violations in the design's rows: 0`, the control tags' violations as given, and `== VERDICT: PASS ==`; the artifact `p06-db-proof-results`, ID 11017908859;
  - **no password:** the only `***` are on lines 38 and 94 (`actions/checkout`) and 152 (`actions/setup-python`), all before the credential step (line 328), and no 48-character hexadecimal string appears;
  - disposal: `container removed: glow-proof-db-36534514283-1`, `credential files removed`, `no proof container remains`.
- **The records:** "Manager verification of P06.DB" and "Exact-head review of P06.DB" are byte-identical to `4511bbc`'s, each section compared whole. The in-place corrections carry the required mark and say what run 36520940933 established, what it did not, and where the corrected counts are. The README's corrections match the code.

#### The run-level conclusion `cancelled`

- **What happened,** from the runs' and jobs' timestamps: run 36534514283 started at 07:04:34. The session's records push `60b6b70` started run 36534597575 at 07:05:24 on the same branch, so in the same concurrency group (`foundation-${{ github.ref }}`, `cancel-in-progress: true`). That run created its first job at 07:09:04. Run 36534514283's gate had finished at 07:09:03, and the run was marked `cancelled` at 07:09:05. None of its jobs was cancelled: all eight, and every step in them, completed with `success`.
- **The cause is the prompt's,** not the session's environment or the proof's: it told the session to push its records after its code, but not to wait for the code run to finish first (AM5-14). The proof needs no database in the session: its database runs inside the GitHub Actions job.
- **Decision (App Manager 5):** run 36534514283's job results are C1's run of record for the stress numbers. The manager workflow's test for a push run as evidence is its gate log, and the gate printed `Application checks passed` on the exact code head after the other seven jobs had completed. The label is recorded here as a limit. PR28's pull-request run on the integrated head, which carries `4280770`'s proof package unchanged, runs every job again. Its result is in PR28's description and is recorded with the next records batch.

#### Observations for the exact-head review

1. **One part of F1 has no test that fails without it.** Removing `case_id` from the per-iteration oracle check at its call site (`stress.py:297`) leaves every test passing: `test_the_per_iteration_oracle_check_names_the_race` tests the query of `oracle.evaluate`, not the call. Today the change is behavior-neutral, because only the two stress controls use that check (`stop_at_first_violation`), each under its own run tag with one race.
2. **Two statements in the section above differ from the manager's reading, with no effect.** Its checks table quotes the Ruff format check as "28 files left unchanged", the wording of `ruff format` without `--check`; the job's log and the manager's run of `ruff format --check .` both say "28 files already formatted". And it gives the database job's log as 797 lines, where the manager's download counts 798.
3. **The "without the fix" paragraph** ran the new tests against the package at `4511bbc`, where the F1, F3 and F4 tests fail on missing names rather than on behavior. The reversals above show each fix's behavior caught, except the one in observation 1.

#### Dispositions

- **F1 to F4 are fixed.** The manager found nothing in the four correction classes.
- **DB06:** the F1 limit is settled. In run 36534514283 each race measured its own overlaps, 174 to 200 of its 200 iterations (floor 10), with zero violations, and the oracle with the stronger O2 found none in the design's rows. The P11 plan's DB06 entry now rests on this run, and C1's exact-head review follows. DB09 is unchanged.
- **The run of record:** as decided above.
- **AM5-14** is logged; its prevention is a line in the manager workflow's step 3, which the Dev Manager reads before PR28 merges.
- **Next:** C1's exact-head review ([prompt](../../ephemeral/2026-09-29-p06-db-c1-review-prompt.md)), of `ea21ac8`, offline, reading job 109295439073's log.

### A second run of the C1 correction prompt (App Manager 5, 4 October 2026)

On 4 October Nathan started a session on Opus 5.5 at extra high, the cell TypeSafe v6 read for C1's exact-head review, and relayed its report the same day. The session had been given the C1 correction prompt (revision 1, from `4511bbc`), not the review prompt. Its start gate checks only that commit, so nothing told it that C1 was already done and integrated (AM5-15). It made the whole correction pass again, independently, on its own branch. **C1's exact-head review has not run.**

- **Checked against GitHub.** The branch is not integrated, so the manager re-ran no offline check, and it started no database.
  - Branch `claude/magical-goldberg-ie0j16`, on `4511bbc`: code head `335eff51190da8431d639e7dd869857cf1943708`, final head `767b852a3494e0296b28924cf90726b0b39cff2d` (that branch's copy of this record only), tree `54207a8f4b289f920a1fff4f0fb5063ac5dc8b13`, as reported. 14 paths: 13 under `proofs/postgres-ordering/`, four of them new test files with mode 100644, and this record. No workflow, dependency, `services/` or `scripts/` path changed. The session opened no pull request, and the manager branch and `main` are unchanged.
  - Foundation run [37209125365](https://github.com/amthorn78/glow-dating-app/actions/runs/37209125365) on `335eff5`: all eight jobs `success`. Its records push, run 37209596956 on `767b852`, started after the code run had finished and skipped the application jobs.
  - The database job's log (job 111456521968, 810 lines), against the report:
    - the image digest `sha256:d74eeac9…`; PostgreSQL 17.11, `superuser` false, `track_commit_timestamp` on; `No changes detected`; `Ran 93 tests`;
    - `cases: 55/55 passed`, each of the 25 held cases `blocked by [97] (holder pid 97)`;
    - the twelve races at 200 iterations, with 196 to 200 measured overlaps;
    - the ten controls failed as intended by their declared signals, the two stress controls at iteration 1;
    - the oracle: 524 submissions and 2,694 revocation rows, `violations in the design's rows: 0`, `== VERDICT: PASS ==`;
    - `container removed: glow-proof-db-37209125365-1`;
    - the only `***` are on lines 38, 94 and 152, and no 48-character hexadecimal string appears.

    The report's figures match the log.

#### What it showed about PR28's code

Two points in the second run's report hold for C1's code too. C1's exact-head review classifies them (revision 2 of its prompt, focus area 10).

**1. A race can miss one commit order.** The stress floors count iterations and measured overlaps, not which writer committed first. The sends authorized, that is, committed before the revocation, in each run:

| Run | Head | Code | `race.sign_out_sender` | `race.expire_sender` | `race.opposing_writers` |
|---|---|---|---|---|---|
| 36520940933 | `dff83d4` | the implementation | 6 | 14 | 0 |
| 36534514283 | `4280770` | C1, the run of record | 16 | 21 | 1 |
| 36599961669 (pull request) | `fcc4992` | C1 | 0 | 0 | 1 |
| 37208329912 (pull request) | `d27519b` | C1 | 5 | 13 | 1 |
| 37209125365 | `335eff5` | the second run's | 0 | 0 | 0 |

- In one of the three runs of C1's code, neither sign-out race had an iteration in which the send committed first.
- In all five runs, each of the other eight two-writer races had at least 14.
- In the sign-out races, the forced cases `send_holds` and `sequential_send_first` put the send first, and they passed in every run.
- DB06's wording, "under forced and randomized races", names no order.

**2. One run per database.** The stress run's run tag is fixed (`design:stress`, `__main__.py:75` to `77`). `_intervals` and the per-iteration oracle check select by that tag, the race and the iteration. In a database that already holds an earlier run, they also read that run's rows, and the final oracle reads every row. The job's database is new in each run, so no run of record is affected. C1's own local run 2 shows the effect (below).

#### A correction to C1's section

C1's section stays as the session wrote it. Its local-runs table gives run 2 ("the pushed code, same database, rows accumulating") every race at 200 of 200 overlaps. With the fixed tag, each of run 2's per-iteration reads also returned run 1's rows for the same race and iteration. So an iteration counted as an overlap when either run's writers overlapped, and those are not run 2's own counts. Local runs are iteration, not evidence, and no claim rests on them. The manager's verification of C1 did not notice this (AM5-16).

#### Dispositions

- **Recorded, not integrated.** PR28 keeps C1 as integrated at `ea21ac8`, verified above, with run 36534514283 as its run of record. The second run is a separate implementation of the same four fixes. It is not PR28's code, so its run is evidence for neither DB06 nor DB09. Its branch stays as pushed and unmerged, and its own section of this record exists only there; the handoff lists the branch for retirement after PR28 merges.
- **The two points above** go to C1's exact-head review, with the correction to local run 2.
- **The pick recorded on 4 October** (`d27519b`) was this session's, not the review's. The review prompt's header, the brief's "Sessions", the handoff and the uses table now say so.
- **AM5-15 and AM5-16** are logged. AM5-15's prevention is a line in the manager workflow's step 3, which the Dev Manager reads before PR28 merges.
- **Next:** C1's exact-head review, from revision 2 of its [prompt](../../ephemeral/2026-09-29-p06-db-c1-review-prompt.md).

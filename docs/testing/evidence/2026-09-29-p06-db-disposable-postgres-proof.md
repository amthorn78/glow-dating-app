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

C1's section stays as the session wrote it. Its local-runs table gives run 2 ("the pushed code, same database, rows accumulating") every race at 200 of 200 overlaps. With the fixed tag, each of run 2's per-iteration reads also returned run 1's rows for the same race and iteration. So an iteration counted as an overlap when either run's writers overlapped, and those are not run 2's own counts. Local runs are iteration, not evidence, and no claim rests on them. The manager's verification of C1 did not notice this (AM5-16). (Extended after C1's exact-head review, R5: see "Exact-head review of P06.DB-C1", "Corrections to this record".)

#### Dispositions

- **Recorded, not integrated.** PR28 keeps C1 as integrated at `ea21ac8`, verified above, with run 36534514283 as its run of record. The second run is a separate implementation of the same four fixes. It is not PR28's code, so its run is evidence for neither DB06 nor DB09. Its branch stays as pushed and unmerged, and its own section of this record exists only there; the handoff lists the branch for retirement after PR28 merges.
- **The two points above** go to C1's exact-head review, with the correction to local run 2.
- **The pick recorded on 4 October** (`d27519b`) was this session's, not the review's. The review prompt's header, the brief's "Sessions", the handoff and the uses table now say so.
- **AM5-15 and AM5-16** are logged. AM5-15's prevention is a line in the manager workflow's step 3, which the Dev Manager reads before PR28 merges.
- **Next:** C1's exact-head review, from revision 2 of its [prompt](../../ephemeral/2026-09-29-p06-db-c1-review-prompt.md).

### Exact-head review of P06.DB-C1 (4 October 2026)

Nathan ran the review session from revision 2 of the [review prompt](../../ephemeral/2026-09-29-p06-db-c1-review-prompt.md) (records commit `cbb3ff7`), in `Glow App - No Stream`, on Opus 5.5 at extra high, the cell TypeSafe v6 read. He started it on 4 October and relayed its report to App Manager 5 on 5 October. It reviewed the exact head `ea21ac8577b83158be1f941b93dbef411bece41f`.

- **Verdict: approve.** C1's four fixes do what their findings needed, none can produce a false pass in CI, and the run of record and the records are sound.
- **No finding is blocking or in a correction class.** Two should-fix findings go into the records: R1, the stress run does not reliably produce the order where the send commits first; R2, the proof assumes one run per database and does not check it. Four nits, R3 to R6.
- **Everything else is confirmed:** DM-08 7.2's three log checks on job 109295439073, the run-of-record decision, the manager's observations and dispositions, the record of the second run with its commit-order table, and PR28's latest pull-request run.

#### The report, as relayed

The session's notes before its report, as relayed, verbatim:

> I'm now checking the concurrency helpers (the holder-pid slot F4 depends on) and fixtures, then the README.
>
> README read. Now the offline checks: install from the locks in a clean process, then tests, Ruff, mypy and the toolchain pin test.
>
> Both are ignored (the first check ran on non-existent directories). Installing now.
>
> All offline checks pass. Now `git diff --check`, scope, locks, modes and the secret scan.
>
> Secret scan is clean. Now hosted CI: loading the GitHub tools to read run 36534514283 and its database job's log.
>
> The workflow confirms each job starts a fresh container (no named volume; anonymous volume removed). Now the run's metadata and jobs.
>
> All eight jobs completed `success` by 07:09:03; the run was marked `cancelled` at 07:09:05. Now the database job's whole log.
>
> The log is 798 lines (`wc -l` counts 797 newlines, which reconciles the session's 797 with the manager's 798). Reading it whole in chunks.
>
> Read the whole log (798 lines). Now the mechanical checks on it: masks, 48-hex runs, held-case count.
>
> Every `***` is a checkout or setup-python token (lines 38, 94, 152); no 48-character hex run; all 25 held cases show `pg_blocking_pids=[97] (holder pid 97)`. Now PR28 and its latest pull-request run.
>
> PR28's head is now `c846d50`, newer than the `cbb3ff7` my start gate fetched. Re-checking the live branch before going on.
>
> One records-only commit landed after the prompt's commit (Nathan's pick for this review). Classifying it with the same trusted policy.
>
> The new commit is records-only (`ordinary-docs-only`) and records this review as in flight; the gate conditions still hold, so the prompt is not stale. Now PR28's latest pull-request runs.
>
> The latest completed PR run is 37217951614 on `cbb3ff7`; a newer one (37218684874 on `c846d50`) is still in progress. Reading 37217951614's jobs.
>
> Database proof checks ran all 14 steps there and passed. Now its per-race counts, and the database job IDs for the other runs the commit-order table lists.
>
> Database jobs found (109514555200, 111454162459). Fetching those logs plus the two other runs' the commit-order table cites, to check the counts.
>
> Commit-order counts match across all five runs in the manager's table, and the newer PR run on `cbb3ff7` adds a second run of C1's code showing zero send-first iterations in both sign-out races. Next I'll look at the run that cancelled the run of record.
>
> The P11 entries are read. Now my own reversal experiments in a scratch copy (offline, no connection): each fix undone alone, then its tests run, to check the manager's table and look for gaps.
>
> My reversal results match the manager's table exactly, with six of seven cases caught and the per-iteration oracle call site uncaught; I also found that removing the empty-signal guard and the pre-existing sign_in exclusion are both uncaught and currently behavior-neutral. Next I'll verify the two earlier sections are byte-identical to 4511bbc.
>
> The hash mismatch is my extraction's artifact (at `4511bbc` the section runs to end of file). Comparing properly:
>
> Sections confirmed unchanged (the diff from `4511bbc` only appends after line 350). Quick check of the manager's identity figures for C1.
>
> Identity figures check out (433 source lines changed, 739 test lines added, tree `c3c9bac`). Next, I'll confirm no control, case expectation, or floor was loosened between the first review's head and this one.
>
> That "identical" line was a false positive (both outputs were empty: the module path was missing). Rerunning with the package on the path.
>
> This plan matches `6f5866d`: 55 cases, 10 controls, same designs, targets, races, budget, and floors. Next, I'll run an offline demonstration of focus area 10's second point using a reused database, applying the package's own functions to constructed rows.
>
> I confirmed offline that an existing database with a prior run can already satisfy both the overlap count and a stress control's signal using those earlier rows—though this doesn't apply to CI since each database there starts fresh. Next I'll check the gate logs and controls from the latest PR run.
>
> Latest completed PR run is clean. Checking whether the newest PR run (on `c846d50`) has finished.
>
> It finished `success`, so it is now PR28's latest pull-request run. Reading its database job.
>
> `held: 0` here is likely different backend pids in this run, not missing waits. Checking.
>
> All 25 held cases consistently show the holder as the only blocker, and the latest PR run on c846d50 passed cleanly across all eight jobs. I'll load the workspace's reporting skill before drafting the report for Nathan.

The report, verbatim, with its headings moved down to fit this record:

**Verdict: approve.** C1's four fixes do what their findings needed, none can produce a false pass in CI, and the run of record and the records are sound. There is no blocking finding and nothing in a correction class. Two points need record changes (R1, R2) that the manager can make without another correction pass.

- **Prompt:** revision 2, from `cbb3ff78687f1f78561649088460331b57023756`.
- **Environment (names only):** none of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` is set, and no `PG*`, `PROOF_DB_*` or `STREAM_*` name is set. `command -v python3.12` gives `/root/.local/bin/python3.12`, Python 3.12.14.
- **Head reviewed:** `ea21ac8577b83158be1f941b93dbef411bece41f`. `HEAD^2` is `24e716b`, there is one merge base (`47db18d`), and the diff is 15 files, +1,250/−122. The code is identical to `4280770`.
- **Live branch:** it moved after my start gate, from `cbb3ff7` to `c846d50`. That one commit is Markdown-only (`ordinary-docs-only`, 3 paths) and records Nathan's pick for this review. The gate conditions still hold: no code landed after the prompt's commit, and this review is not yet recorded.
- **Classifications** (trusted policy from `main`, sha256 `dec69a26…`, `python3 -I`, full SHAs):
  1. `47db18d`→`ea21ac8`: `{"full": true, "reason": "behavior-or-empty"}`, 52 paths. The exclusion command printed nothing.
  2. `6f5866d`→`82c3883`: `ordinary-docs-only`, 12 paths.
  3. `ea21ac8`→`cbb3ff7`: `ordinary-docs-only`, 9 paths.

##### Findings (most severe first; none blocking, none in a correction class)

| # | Severity | Where | Correction class? |
|---|---|---|---|
| R1 | Should fix (records only) | `stress.py:264-267`, `budget.py:183-184` | No |
| R2 | Should fix | `__main__.py:75-77`, `stress.py:118-133` and `:296-297`, `controls.py:275` | No |
| R3 | Nit | `stress.py:297` | No |
| R4 | Nit | `controls.py:61-62`, `stress.py:128` | No |
| R5 | Nit (records) | evidence record line 120; the manager's correction to C1's local run 2 | No |
| R6 | Nit | `README.md:32` | No |

**R1. The stress run does not reliably produce the order where the send commits first.**
- **Cause:** a sign-out or expiry is a short transaction that locks only the session row, and the send locks that row last. The head start is at most 3 ms, and only on half the iterations, so the revocation almost always gets there first. The floors count iterations and overlaps, not which writer committed first.
- **Counts of send-first iterations** (sign-out / expiry / opposing writers):
  - run of record 36534514283: 16 / 21 / 1
  - PR runs on C1's code:
    - `fcc4992`: 0 / 0 / 1
    - `d27519b`: 5 / 13 / 1
    - `cbb3ff7`: 0 / 0 / 0
    - `c846d50`: 3 / 12 / 1
- **Effect:** in 2 of the 5 runs of C1's code, neither sign-out race had a single send-first iteration, and the job still passed. The forced cases `sequential_send_first` and `send_holds` cover that order deterministically and passed in every run, with the wait observed on the holder.
- **Fix:** record the limit in the P11 DB06 and DB09 entries and in the README's "Limits" (wording below).
  - Do not add a floor on each commit order: the construction cannot guarantee both orders, so the job would become flaky (OD-21).
  - Optional later, with P06.2: a seeded delay for the revocation in the session races, and printed counts per order.
- **Why not in a class:** DB06's mark rests on run 36534514283, where both orders occurred in every two-writer race.

**R2. The proof assumes one run per database and does not check it.**
- **Cause:** the run tags are fixed (`design:stress`, `control:<id>`), so the per-iteration reads also return an earlier run's rows for the same race and iteration.
- **Effect,** shown offline with the package's own functions on constructed rows:
  - an iteration counts as overlapped when an earlier run's writers overlapped;
  - a stress control counts as "failed as intended" on an earlier run's violation even when this run's iteration is clean;
  - a forced control's oracle part can be met the same way;
  - the final oracle can only gain violations from old rows, so that part fails safe.
- **CI is unaffected:** each job starts a new container from the image, removes it with its anonymous volume, and applies all 16 migrations from zero in every log I read (7 runs).
- **Fix:** have `run` refuse a database whose `proof_writer_log` already holds rows (one query, with an offline test), or add a per-run nonce to the run tags, and add a README line. A recorded limit is enough for PR28. The guard should land before P06.2 runs this suite against the adapter.

**R3. The per-iteration oracle call has no test that fails without `case_id`** (the manager's observation 1). I agree it is behavior-neutral today: only the two stress controls use that check, each under its own tag with one race. A call-site test is optional. R2 also shows `case_id` gives no protection across runs.

**R4. Two guards have no test that fails without them:** the empty-signal guard in `Signal.met`, and the pre-existing `kind <> 'sign_in'` exclusion. Both are neutral today: a test asserts that every control declares a signal, and the sign-in rows commit before the writers start.

**R5. The local-run corrections miss the reused database.**
- The implementation's local run 2 reused run 1's database, so even its first race's 200 was not its own; the in-place correction at line 120 says that count is established.
- The manager's correction to C1's local run 2 is accurate about overlaps, but that run's stress controls, and the oracle parts of its forced controls, could also have read run 1's rows.
- Local runs count for nothing.

**R6.** The README's layout row for `observe.py` omits `pg_blocking_pids`.

##### Focus areas 1 to 5: the fixes and the tests

- **F1:**
  - Each race now reads only its own rows; no other per-iteration read spans races.
  - An intersection of two database intervals is real concurrency. It cannot count by construction:
    - the head start sleeps before `BEGIN`, so it only shortens overlap;
    - an attempt row's end is `clock_timestamp()` inside the writer's own transaction;
    - sign-in rows are excluded and finish before the writers start.
  - The counts fit each race:
    - the short revocations (sign-out 174, expiry 177, suspension 178–183) are lowest;
    - blocks and unmatches are at 199–200;
    - the duplicates race is at 200 because its second send waits on the first's locks.
  - The floors and the budget are unchanged.
- **F2:**
  - The refactor into `judge` is exact: the queries are the same and only the O2 condition changed. Ties still count as violations.
  - The stronger rule holds for every row the design writes:
    - a log row carries a contact version only when it moves the match out of `active` or to `unmatched`;
    - an unblock leaves the match `restricted`;
    - a repeated unmatch writes no row;
    - there is no rematch.
- **F3:**
  - Each control's declared signal is the deterministic product of its broken switch.
  - A harness or database error disqualifies a control, and every declared case signal is required.
  - A failure with the signal `other` beside the declared signal still counts. That is correct: such failures are side effects of the break.
  - For `no_version_check`, `refusal_missing` is enough, because the named case names the exact refusal reason.
- **F4:**
  - The holder's pid comes from its own transaction's first statement, through `on_begin`.
  - Requiring the holder to be among the blockers is equivalent to requiring it to be the only blocker here. No other connection holds locks during a forced case, and every log shows exactly `[holder]`.
  - The observer cannot time out falsely, because the holder is not released until the wait is observed.
- **Nothing is looser:** case ids, controls (id, design, mode, target), races, budget and floors are byte-identical to `6f5866d` in a generated plan, and case expectations only gained signal tags.
- **The tests are real:** I undid each fix in a scratch copy, and my results match the manager's seven reversals exactly; six are caught. Three more reversals I added were also caught, and two guards were not (R4).

##### DM-08 7.2: the three checks from job 109295439073 (798 lines, read whole)

- **No password: confirmed.** The only `***` are on lines 38 and 94 (`actions/checkout`) and line 152 (`actions/setup-python`), all before the credential step at line 352. There are no 48-character hexadecimal runs: the long hex runs are 15 of 40 characters and 7 of 64.
- **Each forced wait observed with its blocking backend: confirmed.** All 25 held cases show `pg_blocking_pids=[97] (holder pid 97)`.
- **The ten controls met their declared signals: confirmed.** The two stress controls failed at iteration 1.
- **C1's section matches the log:** every race's overlaps, seconds and outcomes, the controls' timestamps, and the oracle's figures (617 submissions, 2,694 revocation rows, 0 design violations).

##### The manager's records

**Run of record:** I agree with the decision.
- All eight jobs and all their steps completed `success`, and the gate printed `Application checks passed` at 07:09:00.
- The last job ended at 07:09:03, and the run was marked `cancelled` at 07:09:05 by the concurrency group of the records run 36534597575 (created 07:05:24).
- The gate's job-level evidence is what the CI policy uses. The same proof code has since passed four PR runs with run-level `success`.

| Item | View |
|---|---|
| Observation 1: the call-site test | Agree: neutral today; a test is optional (R3) |
| Observation 2: "left unchanged"; 797 vs 798 lines | Agree, no effect. The log says "28 files already formatted"; `wc -l` counts 797 newlines in a 798-line log |
| Observation 3: the "without the fix" paragraph | Agree; the reversals show the behavior is caught |
| Dispositions: F1–F4 fixed, nothing in a class, the run of record, AM5-14 | Agree |
| DB06 settled on run 36534514283 | Agree, with R1's limit added |
| Second run: recorded, not integrated, not evidence for PR28 | Agree. The commit-order table matches all five logs, including "at least 14" for the other eight races |
| Correction to C1's local run 2 | Accurate, but incomplete (R5) |
| "Manager verification of P06.DB" and "Exact-head review of P06.DB" unchanged from `4511bbc` | Confirmed: the record's diff only appends after line 350 |

**DB06 and DB09:** both entries are accurate as worded for run 36534514283. I propose adding one limit line to each:
- **DB06:** "In the stress run, the overlap is the intersection of two writers' database intervals, not an observed lock wait, and the construction does not guarantee each commit order. Against sign-out, expiry and the opposing writers the send rarely commits first (16, 21 and 1 of 200 in run 36534514283; none in either sign-out race in two of five runs of the same code), so that order rests on the forced cases. Each run needs a new database, which the job always provides."
- **DB09:** "In the sign-out and expiry stress races the send commits first rarely or never; that order rests on the forced `sequential_send_first` and `send_holds` cases."

**Focus area 10:**
1. **Commit orders:** R1, should fix in the records, not in a class. A recorded limit is enough; I don't recommend a floor on each order.
2. **One run per database:** R2, should fix, not in a class. A recorded limit is enough for PR28; the refusal should come before P06.2 reuses the suite.

##### PR28's latest pull-request run

Run 37218684874 on `c846d50`, which contains `ea21ac8`:
- all eight jobs `success`, and the gate printed `Application checks passed`;
- Database proof checks (job 111484403665) ran all 14 steps, with 55 of 55 cases, 25 waits blocked by the holder, 10 controls met, and 0 design violations over 565 submissions;
- per-race overlaps: 200, 200, 200, 200, 191, 189, 200, 200, 184, 188, 200, 200.

The previous run, 37217951614 on `cbb3ff7`, also passed: 200, 200, 200, 200, 199, 199, 200, 200, 198, 199, 200, 200.

##### Areas with no findings

- F1 to F4 as described above, and the 82 tests.
- Scope: only the 15 paths named changed. No dependency file, workflow, `services/`, `scripts/`, `apps/`, `packages/` or `.gitignore` path changed. Every file is mode 100644, there are no symlinks, and the locks and workflow are unchanged since `6f5866d`.
- The workflow's database job: a new container per run, loopback only, credential handling as before.
- The README matches the corrected code, apart from R6.
- The in-place corrections carry the required mark and say what the first run established, what it did not, and where the corrected counts are.
- The manager's identity figures for C1: tree `c3c9bac`, 433 source lines changed and 739 test lines added.

##### Checks run

| Check | Result |
|---|---|
| `git diff --check HEAD^1 HEAD` | clean, exit 0 |
| Three classifications | as listed above |
| `pip install --require-hashes -r requirements-dev.lock`, `pip check` (`env -i`, proxy and CA variables by reference) | installed; `No broken requirements found.` |
| Unit tests (`env -i`) | `Ran 82 tests`, `OK` |
| `ruff check .` / `ruff format --check .` / `mypy` | `All checks passed!` / `28 files already formatted` / `Success: no issues found in 28 source files` |
| `services/api`: `python3.12 -m unittest tests.test_toolchain_pins` | `Ran 3 tests`, `OK` |
| Secret scan over the diff's added lines | no secret, password, token, connection string or email address; the hex strings are two commit SHAs (`4280770`, `4511bbc`) and the pinned image digest |
| Fix reversals in scratch copies | 13 reversals; F1c, F3f and the `sign_in` exclusion uncaught, the rest caught |
| Plan comparison against `6f5866d` | identical |
| Offline demonstration of a reused database | overlap and stress-control false counts shown |
| Hosted CI | runs 36534514283, 36534597575, 37217951614 and 37218684874 read through the GitHub API |

##### Limits

- I started no database and opened no connection.
- I read only job 109295439073's log line by line. For the other six database logs I extracted the race tables, verdicts, migrations, waits, masks and hex runs by search.
- I did not download the results artifact 11017908859. From reading `results.py`, the JSON gains only signal labels and pids.
- GitHub's concurrency mechanics are inferred from the timestamps.
- Notion was not read.
- I changed nothing in the repository, on GitHub or in Notion. The checkout is left detached at `ea21ac8` with a clean tree, and scratch work is in the ignored `.venv/` and my scratchpad.

**NOTHING NEEDED** beyond relaying this report to App Manager 5.

#### Manager verification of the review (App Manager 5, 5 October 2026)

- **The classifications,** rerun with the trusted policy (sha256 `dec69a26…`) and full SHAs: `47db18d` → `ea21ac8` is full scope, 52 paths, and its only non-Markdown paths are under `proofs/postgres-ordering/` or the workflow; `6f5866d` → `82c3883` and `ea21ac8` → `cbb3ff7` are `ordinary-docs-only`, 12 and 9 paths; `cbb3ff7` → `c846d50`, the commit that landed during the review, is `ordinary-docs-only`, 3 paths. `budget.py`, `design.py` and `reference.py` are unchanged from `6f5866d`.
- **R1: confirmed.**
  - The send locks the lower account, the higher account, the match and then its session (`reference.py:187` to `192`); a sign-out locks only the session (`reference.py:582`). The head start delays each writer but the first by nothing or by up to 3 ms, chosen by the seed (`stress.py:264` to `267`).
  - The send-first counts match the five logs of C1's code; the manager's own download of the latest, job 111484403665 on `c846d50`, gives 3, 12 and 1. In two of the five runs (`fcc4992` and `cbb3ff7`) neither sign-out race had an iteration in which the send committed first. In run 36534514283 every two-writer race had both orders.
  - One citation slip, with no effect: the review cites `budget.py:183-184` for the floors. `budget.py` has 24 lines; the floors are at `:11` and `:12`, checked at `:24`.
- **R2: confirmed in the code.** The run tags are fixed (`__main__.py:70` and `:75` to `77`; each control's tag, `controls.py:91`), and the per-iteration reads select by tag, race and iteration (`stress.py:118` to `133` and `:296` to `297`; `controls.py:275`). The job starts a new container in every run (the manager's verification of P06.DB, and every log read since).
- **R4:** the empty-signal guard is `controls.py:61` to `62`, and the sign-in exclusion is `stress.py:128`.
- **R5: confirmed.** The implementation's local-runs table gives run 2 as "same database, rows accumulating", and its in-place correction says that only the first race's 200 is established. The manager's correction to C1's local run 2 names only its overlap counts. Both are corrected below (AM5-17).
- **R6: confirmed.** The README's layout row for `observe.py` (line 32) names `pg_stat_activity` and `pg_locks` only.
- **PR28's latest pull-request run,** 37218684874 on `c846d50`: the database job's log (job 111484403665) gives `cases: 55/55 passed`, 25 waits each `pg_blocking_pids=[103] (holder pid 103)`, overlaps 200, 200, 200, 200, 191, 189, 200, 200, 184, 188, 200 and 200, 565 submissions, `violations in the design's rows: 0` and `== VERDICT: PASS ==`. The previous run's overlaps (37217951614 on `cbb3ff7`) are as the review gives them.
- **The rest** agrees with the manager's own verification of C1: the run of record's timeline, DM-08 7.2's three checks and C1's identity figures.

#### Corrections to this record

Local runs are iteration, not evidence, so neither correction changes a claim. The sections they correct stay as written.

- **The implementation's local runs, run 2** ("the pushed code, same database, rows accumulating"): its in-place correction says only the first race's 200 is established. In the same database, under the same run tag, that run's reads also took in run 1's rows, so none of its counts, the first race's included, is its own.
- **The manager's correction to C1's local run 2** (in "A second run of the C1 correction prompt"): besides the overlap counts, that run's stress controls and the oracle parts of its forced controls could have been met by run 1's rows, so its "ten controls failed as intended" is not run 2's own result either (AM5-17).

#### Disposition

- **Approved.** C1 stands as integrated at `ea21ac8`. No finding is blocking or in a correction class, so, by the prompt's rule, there is no further correction pass and the rest goes into the records.
- **R1:** the P11 plan's DB06 and DB09 entries carry the limit in the review's wording, and the README's "Limits" carries it too. No floor on each commit order: the construction cannot guarantee both, so the job would become flaky (OD-21). The optional seeded delay and per-order counts are carried to P06.2 (the brief, "Carried to P06.2").
- **R2:** the README's "Limits" and DB06's entry carry the limit. The refusal of a database that already holds proof rows is carried to P06.2, to land before P06.2 runs the suite against the app's adapter.
- **R3 and R4:** recorded; both are behavior-neutral today, and R3 is the manager's observation 1.
- **R5:** corrected above, and AM5-17 is logged. It repeats AM5-16, so its prevention is now a checklist item in the manager workflow's step 5, which the Dev Manager reads before PR28 merges.
- **R6:** the README's layout row now names `pg_blocking_pids`.
- **The marks:** DB06 and DB09 stand as worded, each with its new limit line.
- **Next:** the Dev Manager's read of PR28's governing changes (DM-09), then Codex's review, the merge and the receipt.

### Codex's review of PR28's final head (5 October 2026)

App Manager 5 marked PR28 ready at about 00:44 UTC, at its final head `a8f09aa4b9dc6ab0fdf4f00cc68ab35a4ffac9ec`, after PR run 37248312801 passed all eight jobs on it. Codex started both reviews at 00:44 UTC. Its code review completed at 00:48 UTC with one review and two inline comments, each marked P2. Its security review completed at 00:49 UTC with no comment. Codex's summary comment shows both reviews completed on `a8f09aa`. The labels CX1 and CX2 are the manager's.

#### The findings, as posted

> **CX1. P2, `proofs/postgres-ordering/glow_ordering_proof/oracle.py:250`: "Verify that the session owns the persisted sender."** When P06.2 reuses this suite, an adapter can authorize with one account's session but persist another account as `MessageSubmission.actor`—or even persist a non-member—and still pass the oracle. The session's account is loaded here but is used only for epoch-revocation counting; it is never compared with `s.actor` or the match members, while the current cases primarily check outcomes and row counts. Add an invariant and a case proving that the session account equals the persisted actor and belongs to the match, otherwise the suite can certify misattributed or unauthorized messages.

> **CX2. P2, `proofs/postgres-ordering/glow_ordering_proof/reference.py:209-210`: "Enforce the session-expiry invariant through commit."** When a session expires after this check but before the transaction commits—for example with a short remaining TTL or a slow outbox/log insert—the submission is still authorized and committed. That contradicts O5, which treats every submission committed at or after `expires_at` as a violation, but the suite only forces expiry while waiting before this check. Either make the transaction design enforce the commit-time invariant or narrow and record the intended authorization-check-time invariant, with a forced post-check delay covering the boundary.

#### Manager verification (App Manager 5, 5 October 2026)

- **CX1: confirmed. The gap is in the suite, not in the reference design.**
  - The oracle reads each session's account (`oracle.py:250`) and uses it only to count account revocations for O7 (`:257` to `262`). No rule compares a submission's actor with its session's account or with its match's members. O7 also counts the session's account where its docstring says the actor's.
  - The reference design cannot write such a row. The send reads the session's account, refuses `not_a_member` unless it is one of the match's two accounts, and stores that account as the actor of the submission and of its log row (`reference.py:172` to `184`, `:255`, `:275` and `276`). A send request names no actor (`interface.py:66` to `71`).
  - No case exercises `not_a_member`, and no control writes a misattributed row, so the suite would not catch another subject that misattributes. That matters when P06.2 runs this suite against the app's adapter, as the brief intends ("One interface for the race suite"). It does not change what the runs show about the reference design.
- **CX2: confirmed. The design's rule and the oracle's differ.**
  - The send reads the time once, after its locks (`reference.py:195`, through `clock_timestamp()`, `:74` to `83`), and refuses an expired session against that time (`:209` and `210`). Its outbox and log rows follow, and the transaction commits after them. This is the check the brief's 5.2 asks for: "one time taken after locking".
  - O5 is stricter: the commit must be before the session's expiry (`oracle.py:251`). A send whose session expires between the check and the commit would be authorized by the design and flagged by O5. The suite would then fail, so it cannot pass falsely at that boundary.
  - No run comes near that boundary. Every session but one lives 300 seconds (`cases.py:46`), and each case and each stress iteration builds its own (`stress.py:258`). The 3-second session in `session_expires_during_wait` belongs to the send that must be refused (`cases.py:674` to `714`).
  - The `transaction_start_time` control is caught by its case's expected refusal and by O5, so a narrower O5 must keep that detection.
- **Against the correction classes of PR28's review prompts:** neither finding lets a send commit after a revocation that invalidates it without the suite failing. Neither touches a credential or a connection, or lets the job reach another database. DB06's entry depends on neither. DB09's "expiry" could be read as ordering a send's commit against time-based expiry, which the design does not do; a limit line closes that reading. Both findings are should-fix, for the suite P06.2 reuses.

#### Disposition

- **No correction pass before the merge.** Neither finding is blocking or in a correction class. This is the rule C1's exact-head review applied to R1 and R2, whose guard DM-09 approved carrying to P06.2.
- **CX1:** the README's "Limits" records it, and it is carried to P06.2 (the brief, "Carried to P06.2"). Before the suite runs against the app's adapter, the oracle checks that each submission's actor is its session's account and a member of its match, and a control that writes a misattributed row must fail.
- **CX2:** the P11 plan's DB09 entry and the README's "Limits" record it, and it is carried to P06.2. P06.2 settles the expiry rule as the brief's 5.2 states it, checked at a time read after the locks. It narrows O5 to match, keeps O5's detection of the `transaction_start_time` control, and forces the boundary with a delay between the check and the commit. A design that enforces expiry at commit instead goes to the Dev Manager with P06.2's brief.
- **The threads:** each Codex thread gets a reply with this disposition.
- **Next:** CI on the new final head, then the merge and the receipt. (Superseded the same day: the push of `9bcec21` started a second code review, whose CX3 needs a correction first; see below.)

#### Codex's second code review, of `9bcec21` (5 October 2026)

The push of `9bcec21`, the commit that records CX1 and CX2, started a second Codex code review at 00:58 UTC. It completed at 01:02 UTC with one inline comment, marked P1. The security review did not run again. PR run 37249533664 on `9bcec21` passed all eight jobs. App Manager 5 made PR28 a draft again at 01:07 UTC.

> **CX3. P1, `proofs/postgres-ordering/glow_ordering_proof/environment.py:108-111`: "Prove the target is disposable before allowing migrations."** When the documented local command is given an existing PostgreSQL instance or an SSH-forwarded database on loopback (or any local Unix socket), this check accepts it and `python -m django migrate` mutates it before `glow_ordering_proof run` performs its later server checks. Loopback identifies only the network route, not database provenance, so require a proof-specific marker or freshly generated instance identity before exposing Django settings to migration commands; otherwise a mistaken local invocation can apply the app schema to a shared or production database despite the protected-database boundary. AGENTS.md reference: [AGENTS.md:L5-L5](https://github.com/amthorn78/glow-dating-app/blob/9bcec21059b02ea5ab5811d2741fcd58c643cfce/AGENTS.md#L5-L5)

##### Manager verification (App Manager 5, 5 October 2026)

- **Confirmed.**
  - The host check accepts `127.0.0.1`, `localhost`, `::1` or any absolute Unix-socket directory, and checks nothing about the server behind it (`environment.py:108` to `112`).
  - The settings build Django's database from those options when they are imported (`settings.py:28` to `42`), so every management command connects with them, `migrate` included.
  - The documented sequence runs `migrate` first (the README, "Running against a disposable database"). `run`'s server checks come later. They test for a superuser, `track_commit_timestamp` and the isolation level (`__main__.py:55` to `60`), and none of them tells a disposable database from another.
- **What limits it today.**
  - The CI job reaches only the container it starts on `127.0.0.1:5433`, so the job is safe by construction.
  - The settings refuse `DATABASE_URL`, the HDE keys and every `PG*` name, and the password comes only from a passfile the operator writes.
  - So a non-disposable database is reached only when a person or session points the proof's variables at one, against the README, D4 and `AGENTS.md`. Nothing in the code stops that mistake.
- **Against the correction classes:** CX3 falls in "let the job or the proof connect to anything but its own disposable database". The job cannot. The proof can, when misdirected, and its first documented command changes that database. The protected boundary is protected by effect, and a guard that rests on the operator's care does not meet it.

##### Disposition

- **A correction pass before the merge: P06.DB-C2.** CX3 is in a correction class, so PR28 does not merge until it is fixed and the fix is reviewed at its exact head. P06.2's runs of the suite, local or CI, would inherit the same gap.
- **The design goes to the Dev Manager first.** The fix changes D3 and D4 (the brief: "A prompt that departs from it on D3, D4 or D5 goes back to the Dev Manager"), and it is a security-boundary decision (the charter).
  - Brief revision 3 states the design in D1, D3 and D4. Whoever creates the disposable database sets a marker generated for the run as the database's comment. The proof refuses any connection whose database does not carry that marker, before it sends any statement but the connection's own session settings.
  - DM-10 reads it, with CX3's classification and the dispositions of CX1 and CX2. The C2 prompt follows the read.
- **PR28 is a draft again** until C2, its exact-head review and Codex's review of the final head are done.
- **CX1 and CX2** stay as recorded above, unless DM-10 says otherwise.
- **The brief's guard was the manager's:** D1 and D4 took loopback as the database boundary (AM5-18).
- **Next:** DM-10. (Done the same day: Dev Manager 2 approved the classification and the marker, with conditions 2.1 to 2.5, at `9f2e79d`; brief revision 4 applies them, and the review log has the disposition, "DM-10". The C2 prompt departs from 2.3's query in one point, so DM-11 read it first: Dev Manager 2 approved the departure with conditions at `91c5c2c`, in words that replace it, and the C2 prompt runs as revision 2 in those words; brief revision 5 records them, and the review log has the disposition, "DM-11". Then the correction pass P06.DB-C2, done the same day: "P06.DB-C2 corrections" and "Manager verification of P06.DB-C2", below.)

## P06.DB-C2 corrections

The second correction pass on P06.DB: Codex's CX3, corrected with the run's marker under DM-10's conditions 2.1 to 2.4 and DM-11's words for 2.3's check, and a rerun of the job.

- **Prompt:** revision 2, from commit `ad3323da9beb56a366f307561507fe38557e7b17` (`docs/ephemeral/2026-10-05-p06-db-c2-correction-prompt.md`).
- **Session:** branch `claude/ecstatic-feynman-749ccu`, fast-forwarded to `ad3323da9beb56a366f307561507fe38557e7b17`. At the start, `git diff --stat ea21ac8… HEAD -- proofs/postgres-ordering/glow_ordering_proof proofs/postgres-ordering/tests .github/` and `git diff --stat ad3323d… origin/claude/magical-wozniak-yfmmx2 -- proofs/ .github/` printed nothing, and the live manager branch's record had no "P06.DB-C2 corrections" heading (`grep -c` printed `0`).
- **Code head:** `43d8ca428ea25aef485af0e7d5f3a1840a2ae0c6` (tree `b1d74ade790e1bd57c24254e72f8d53313746cdf`). **New run of record:** Foundation run 37262466651 on that head (push run 439).
- **Records commit:** the commit that adds this section. It changes only this Markdown file, so its push run is documentation-only by the CI policy's design; the evidence of record is the push run of the code head. I pushed it only after run 37262466651 had finished (AM5-14).
- **Times:** 5 October 2026, UTC.

### Environment check (names only)

| Check | Result |
|---|---|
| `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` | none present (the loop printed nothing) |
| `PG*`, `PROOF_DB_*`, `STREAM_*` names | none (`compgen -e \| grep -E …` printed nothing) |
| `command -v python3.12` | `/root/.local/bin/python3.12`, Python 3.12.14 (`$HOME/.local/bin` first on PATH) |
| `docker info` | exit status 1 |
| `command -v initdb pg_ctl postgres pg_isready psql` | `pg_isready` and `psql` at `/usr/bin`; `initdb`, `pg_ctl`, `postgres` not on PATH, present in `/usr/lib/postgresql/16/bin/` (PostgreSQL 16.14) |

### Items 1 to 5

| Item | Done where | Test (offline, no database) |
|---|---|---|
| **1. The marker's form** (DM-10 2.1) | `environment.py:55` `MARKER = "PROOF_DB_MARKER"`, in `PROOF_NAMES` (`:56`), so a missing marker is refused with the other missing names; `:59` `MARKER_FORM` (`[0-9a-f]{32}`, matched with `fullmatch`); `:138` `database_marker` refuses a missing or malformed value, naming the variable and no value; `:152` `expected_comment` is `glow-ordering-proof:` (`:61`) followed by the marker. The settings call it at import (`settings.py:34`) | `tests/test_marker.py`, `MarkerFormTests`: twenty `token_hex(16)` values accepted; refused, each naming `PROOF_DB_MARKER` and no value: missing, empty, 31 and 33 characters, upper case, non-hex, a leading or trailing space, a trailing newline, `0x`-prefixed, the comment prefix plus the marker, and the bare prefix. `SettingsMarkerTests.test_settings_refuse_a_missing_or_malformed_marker_at_import`: the settings module refuses at import (missing, empty, short, padded) |
| **2. The check** (DM-10 2.2) | `marker.py`: `install` (`:51`) connects `verify_new_connection` to Django's `connection_created` with a `dispatch_uid` and `weak=False` (`:55`), and the settings call it at import (`settings.py:34`), so every command that loads the settings registers it before its first connection; `__main__.py` does not mention it. `verify_new_connection` (`:67`) runs `QUERY` (`:29`): `pg_backend_pid()` and `shobj_description(d.oid, 'pg_database')` for `d.datname = current_database()`. A missing row, a null comment or any comment that is not the whole expected string closes the connection through Django (`connection.close()`, `:59`) and raises `RefusedDatabase` (`:39`), which is deliberately not a `django.db.DatabaseError`, because `makemigrations` turns an `OperationalError` into a warning and carries on. A failing query also closes the connection (`:77`). The refusal (`REFUSAL`, `:36`) names `PROOF_DB_MARKER` and no value. A pass prints one line with the backend pid and thread (`:86`), so a run's log shows when each connection was opened (2.5). Django 5.2.17's `connect()` sends the signal after `get_new_connection`, `set_autocommit` and `init_connection_state` only; for this backend the last runs `SET TIME ZONE` when the server's differs and `SET ROLE` only with `assume_role`, which the proof does not configure | `tests/test_marker.py`, `ConnectionCheckTests`, with a fake connection and cursor: a matching comment passes with exactly one statement and no close; a different marker, the bare prefix, the marker alone, anything before or after the expected string, upper case, an empty comment, a null comment and no row each refuse, close once, ran only the marker query, and carry no value; no installed marker refuses without a statement; a failing query closes and propagates; the refusal is not a `DatabaseError`. `SettingsMarkerTests`: importing the settings registers the receiver under its `dispatch_uid` with the run's comment, and the registration is in `settings.py`, not `__main__.py`. `tests/test_marker_commands.py` runs `migrate`, `makemigrations --check --dry-run`, `facts` and `run` each in a clean subprocess through `tests/command_harness.py`: Django's real `connect()`, signal, settings and commands, with only the backend's driver-facing methods replaced by a fake server. For five wrong comments each command exits non-zero with the refusal and no value, the marker query was the connection's only statement, and the connection was closed and not kept; with the matching comment each command passes the check and reaches its own first statement |
| **3. The CI step** (DM-10 2.3, in DM-11's words) | `.github/workflows/foundation.yml:283` to `333`, "Show that a wrong marker is refused and leaves the proof's database unchanged", after the role step and before the migrations. As the superuser inside the container, with `psql -d glow_proof`, it counts `pg_class` rows per schema (`pg_namespace` left-joined, so a schema with none shows `0`) before and after `migrate` run with the other well-formed marker; it requires a non-zero exit, the refusal line, every schema's count unchanged (`cmp` of the two tables, `pg_toast` included), zero relations outside `information_schema` and the schemas for which `starts_with(nspname, 'pg_')` is true, before and after, and `to_regclass('public.django_migrations') IS NULL` after. It prints both tables once and no name of a role, password or marker; on an unexpected outcome it withholds `migrate`'s diagnostics | CI only (the step is workflow shell). Its queries were tried on the local cluster (below): unchanged and zero after a refused `migrate`; after a real `migrate`, `public` 184, `pg_toast` 110, 184 outside, and `django_migrations` present, so each of the three checks would fail |
| **4. The marker in the job** (DM-10 2.4, with DM-11's note) | `foundation.yml:233` to `247`: the credentials step generates the run's marker and a different one with `secrets.token_hex(16)`, masks both with `::add-mask::` (`:239`, `:240`) right after the passwords' masks and before any other output, refuses if the two are equal, and writes them to `marker` and `wrong-marker` in the job's `mktemp -d` directory, mode `0600`. `create-role.sql` gains `COMMENT ON DATABASE glow_proof IS 'glow-ordering-proof:<marker>'` (`:244`), which the role step already pipes into `psql` as the superuser with its output kept out of the log (`:278` to `281`) and then deletes. Each step that needs a marker reads it with `PROOF_DB_MARKER="$(cat "$DIR/…")"` for its own commands (`:302`, `:341`, `:354`); nothing writes it to `$GITHUB_ENV` or `$GITHUB_OUTPUT`, and the upload step sees only `.work/results.json`. The wrong-marker step removes `wrong-marker` and its log (`:331`); the removal step removes the whole directory, `marker` included (`:377`). Only the `database` job changed: the other seven jobs, the gate and the workflow's top level parse identical to `ad3323d`'s | The run's log (below): the marker step's masks precede any output, no marker or password appears, and `credential and marker files removed` |
| **5. The README** | `README.md`: the brief line (`:5`); the layout's settings, environment and new marker rows (`:23` to `25`); the offline checks (`:80`); "The run's marker" with the local recipe, `COMMENT ON DATABASE` right after `CREATE DATABASE`, a new marker per database, and the reused-database guard (`:93` to `100`); `PROOF_DB_MARKER` in the command (`:108`); why loopback is not enough (`:117`); the CI job (`:119`); the local recipe (`:121`); a "Limits" line: the marker ties the proof to the database created for the run and does not replace the reused-database guard carried to P06.2 (`:132`) | Documentation |

**Without the change:** at `ad3323d` the new tests cannot import `environment.MARKER`. Mutating the new code shows each test group bites (the whole suite run each time): settings not calling `install`, 26 failures; a prefix comparison (`startswith`), 7; no `connection.close()` on refusal, 23; `strip()` before the form check, 4; `search` instead of `fullmatch`, 6; `RefusedDatabase` as an `OperationalError`, 6 (among them `makemigrations` in the command harness, which then carries on); a null comment passing, 5; the comment in the refusal message, 15. The unmutated copy passes.

### The wrong-marker step's result (run 37262466651)

Exit status `1`, and the refusal line:

> `refusal: glow_ordering_proof.marker.RefusedDatabase: refusing this database: its comment is not the run's marker (PROOF_DB_MARKER): the database's comment is different. The proof runs only against the disposable database created for this run, whose comment the creator set with that run's PROOF_DB_MARKER; the connection is closed`

| Schema | Relations before | Relations after |
|---|---|---|
| `information_schema` | 69 | 69 |
| `pg_catalog` | 266 | 266 |
| `pg_toast` | 80 | 80 |
| `public` | 0 | 0 |

Relations outside `information_schema` and the `pg_` schemas: 0 before, 0 after. `to_regclass('public.django_migrations') IS NULL` after: `t`. The step ended with `a wrong marker was refused, and the proof's database is unchanged and holds no table`.

### The new run of record: Foundation run 37262466651 on `43d8ca428ea25aef485af0e7d5f3a1840a2ae0c6`

Push run 439, `https://github.com/amthorn78/glow-dating-app/actions/runs/37262466651`, started 04:12:07 UTC.

| Job | Conclusion |
|---|---|
| Change scope | success (job 111612382380; full scope) |
| API checks | success (job 111612413259) |
| Mobile checks | success (job 111612413210) |
| API mobile smoke | success (job 111612413181) |
| API artifact checks | success (job 111612413261) |
| Stream proof checks | success (job 111612413193) |
| Database proof checks | success (job 111612413204; 04:12:19 to 04:14:14 UTC; the wrong-marker step 1 s, the suite step 72 s) |
| Foundation gate | success (job 111613560771, finished 04:17:45); its log line: `Application checks passed`, with every job, `database` included, `success` in its `RESULTS` |

**The run-level conclusion is `success`** (completed 04:17:46 UTC). I pushed nothing while it ran.

**From the database job's log** (904 lines, read whole):

- **The image and the server.** `Digest: sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`, the pinned digest. `SELECT version()`: `PostgreSQL 17.11 (Debian 17.11-1.pgdg13+2) on x86_64-pc-linux-gnu, compiled by gcc (Debian 14.2.0-19) 14.2.0, 64-bit`. `track_commit_timestamp` `on`; `default_transaction_isolation` `read committed`, and `read committed` inside a writer's transaction; `superuser` `false`. The sixteen migrations applied from zero, 04:12:54.39 to 04:12:56.76; `makemigrations --check --dry-run`: `No changes detected`. The offline tests in the job: `Ran 98 tests`, OK; Ruff `All checks passed!`; mypy `Success: no issues found in 32 source files`.
- **The marker on every connection.** `database marker verified on a new connection` once for `migrate` (backend pid 130), once for `makemigrations` (131), once for `facts` (132), and five times for `run`, all before `cases: 55/55 passed`: the main thread (133) and `proof-writer-0` to `proof-writer-3` (134, 135, 137, 136). No such line appears after them, so no connection was opened inside a case, a race or a control.
- **The cases:** `cases: 55/55 passed`. **Observed waits with their blocking backends:** each of the 25 held cases (the twenty `send_holds` and `revocation_holds` cases, `racing_duplicates`, `session_expires_during_wait` and the three pairwise opposing-writer cases) shows `pid 135 wait_event_type=Lock wait_event=transactionid pg_locks not granted: transactionid/ShareLock pg_blocking_pids=[134] (holder pid 134)`, after 1 poll (9 cases), 2 (14) or 3 (2): the waiting backend was blocked by the holder's backend and by no other, as in C1's run (pids 98 and 97 there).
- **The stress run** (seed 20260929; budget 200 iterations or 30 s per race; floors 50 iterations and 10 overlaps), every race with 0 violations and 0 harness failures and its floors met, against C1's run of record (Foundation run 36534514283):

| Race | Iterations (C1 → C2) | Measured overlaps (C1 → C2) | Seconds (C1 → C2) | C2 outcomes |
|---|---|---|---|---|
| `race.block_by_low` | 200 → 200 | 200 → 200 | 3.3 → 5.2 | send authorized 34, refused `match_not_active` 166; block applied 200 |
| `race.block_by_high` | 200 → 200 | 200 → 200 | 3.3 → 5.2 | send authorized 41, refused 159; block applied 200 |
| `race.unmatch_by_low` | 200 → 200 | 199 → 200 | 3.1 → 4.9 | send authorized 55, refused 145; unmatch applied 200 |
| `race.unmatch_by_high` | 200 → 200 | 199 → 200 | 3.1 → 5.0 | send authorized 45, refused 155; unmatch applied 200 |
| `race.suspend_low` | 200 → 200 | 178 → 199 | 2.7 → 4.4 | send authorized 37, refused `account_not_active` 163; suspend applied 200 |
| `race.suspend_high` | 200 → 200 | 183 → 199 | 2.7 → 4.3 | send authorized 14, refused 186; suspend applied 200 |
| `race.delete_low` | 200 → 200 | 191 → 200 | 3.0 → 4.7 | send authorized 38, refused 162; delete applied 200 |
| `race.delete_high` | 200 → 200 | 192 → 200 | 3.0 → 4.5 | send authorized 18, refused 182; delete applied 200 |
| `race.sign_out_sender` | 200 → 200 | 174 → 197 | 2.7 → 4.2 | send refused `session_not_valid` 200 (authorized 0); sign-out applied 200 |
| `race.expire_sender` | 200 → 200 | 177 → 199 | 2.9 → 4.3 | send authorized 1, refused 199; expiry applied 200 |
| `race.racing_duplicates` | 200 → 200 | 200 → 200 | 4.0 → 6.3 | one authorized and one replayed in every iteration (`send_a` authorized 115, `send_b` 85); one row per key |
| `race.opposing_writers` | 200 → 200 | 200 → 200 | 4.6 → 7.1 | send refused `match_not_active` 189, `account_not_active` 11 (authorized 0); both blocks and the suspension applied 200; no deadlock |

  The plan is unchanged: twelve races, the same seed, budget and floors. Every race ran its full 200 iterations again and measured 197 to 200 overlaps (C1: 174 to 200). The races ran slower (4.2 to 7.1 s against 2.7 to 4.6 s; the suite step 72 s against 48 s); see "Deviations and limits". In `race.sign_out_sender` the send never committed first and in `race.expire_sender` once, the commit order the recorded R1 limit says the stress run does not guarantee; the forced cases `sequential_send_first` and `send_holds` cover it, and passed.

- **The negative controls,** each with its declared signal, all ten `failed as intended` (the signal met), as in C1's run:

| Control | Declared signal | Signal in the run |
|---|---|---|
| `no_locks.forced` (`unmatch_by_high.send_holds`) | `commit_after_revocation` + `wait_not_observed` + oracle O2/O6 | not observed waiting on the holder; the send committed 04:14:03.340569 after the revocation at 04:14:03.333853; oracle 2 violations (O2, O6) |
| `no_locks.stress` (`race.block_by_high`) | oracle O2/O6 | first failing iteration 1: the block (v2) committed 04:14:03.432092, the send at v1 04:14:03.432346; oracle O2, O6 |
| `no_version_check` (`named.stale_contact_version`) | `refusal_missing` | sends at versions ahead and behind authorized; oracle 0 violations (observation 3) |
| `no_session_lock` (`sign_out_sender.send_holds`) | `commit_after_revocation` + `wait_not_observed` + oracle O3 | not observed waiting; the send committed 04:14:03.631258 after the sign-out at 04:14:03.625194; oracle 1 violation (O3) |
| `transaction_start_time` (`named.session_expires_during_wait`) | `refusal_missing` + oracle O5 | the send whose session expired while it waited was authorized; oracle 1 violation (O5) |
| `dedup_before_authorize` (`named.retry_after_revocation`) | `refusal_missing` | the retry after the revocation was `replayed` with the old receipt |
| `inverted_lock_order` (`named.opposing_first_lock_block_high_vs_send`) | `deadlock` | `deadlock:DeadlockDetected` for the send |
| `no_account_lock.forced` (`suspend_high.send_holds`) | `commit_after_revocation` + `wait_not_observed` + oracle O4 | not observed waiting; the send committed 04:14:07.997618 after the suspension at 04:14:07.991642; oracle 1 violation (O4) |
| `no_account_lock.stress` (`race.suspend_high`) | oracle O4 | first failing iteration 1: the suspension committed 04:14:08.082819, the send 04:14:08.087643; oracle O4 |
| `filter_state_in_lock` (`unmatch_by_high.revocation_holds`) | `refusal_missing` + oracle O2/O6 | the send that arrived while the unmatch held was authorized and committed; oracle 2 violations (O2, O6) |

- **The oracle over every row:** 526 submissions (C1: 617) and 2,694 revocation rows (C1: 2,694) examined; `design:forced` 32 (C1: 32), `design:stress` 483 (C1: 574, the count of authorized sends, which the races decide), the controls 1 or 2 each; **violations in the design's rows: 0**. Violations only under control tags, the same as C1's: `no_locks.forced` 2, `no_locks.stress` 2, `filter_state_in_lock` 2, `no_session_lock` 1, `no_account_lock.forced` 1, `no_account_lock.stress` 1, `transaction_start_time` 1. `== VERDICT: PASS ==`.
- **Disposal:** `container removed: glow-proof-db-37262466651-1`, `credential and marker files removed`, `no proof container remains`.
- **The results JSON:** artifact `p06-db-proof-results`, ID 11324438345, 6,188 bytes, zip digest `sha256:81b6810d…`. I did not download it.
- **No password, no marker, and no mask where either would be.** The log's only `***` are on lines 38 and 152 (the `token` inputs of `actions/checkout` and `actions/setup-python`) and line 94 (checkout's git `AUTHORIZATION: basic ***` header), all before the credential step. The credential step prints one line, the role step one line, and the wrong-marker step its two tables, its counts, its exit status, the refusal line and its verdict. The only long hexadecimal runs are 40 characters (action commits, 15) and 64 (digests and IDs, 7): no standalone 32- or 48-character run. The words "password", "passfile" and "marker" appear only in the workflow's own script text, the names of the offline tests, the steps' fixed messages and the refusal and verification lines, none with a value. The step headers show the workflow's script text and the `DIR` path, as in C1's run; no connection option, passfile content, connection string or marker value appears.

### Local runs (iteration, not evidence)

Docker does not work in the sandbox, so I started a throwaway cluster from `/usr/lib/postgresql/16/bin/initdb`: PostgreSQL 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1), not CI's 17.11, run as the `postgres` OS user in a `mktemp -d` directory under `/tmp`, listening only on a Unix socket (`listen_addresses = ''`), port 5433, `track_commit_timestamp = on`, and `log_statement = 'all'` for this iteration only. The superuser's and the role's passwords and both markers were generated with `secrets`; the superuser's password went through `--pwfile`, removed after `initdb`; the role, its database and the comment came from one SQL file, removed after use; `pg_hba` allowed `peer` for `postgres` and `scram-sha-256` for everyone else (the first attempt used initdb's default `peer` for all, and the proof's role was refused until I changed it). No forbidden or `PG*` name was present.

- **The wrong-marker step's logic:** `migrate` with the other marker exited 1 with the refusal line; the per-schema counts were unchanged (`information_schema` 69, `pg_catalog` 264, `pg_toast` 80, `public` 0), 0 outside the `pg_` schemas, and no `django_migrations`. After the real `migrate`, the same queries gave `public` 184, `pg_toast` 110, 184 outside and `django_migrations` present.
- **The proof with the run's marker:** `migrate` applied the sixteen migrations, `makemigrations --check --dry-run` printed `No changes detected`, `facts` ran, and `run` passed: 55/55 cases; twelve races at 200 iterations with 200 overlaps each; ten controls failed as intended by their declared signals; 531 submissions and 2,694 revocation rows, zero design violations; 106 s.
- **What each connection ran, from the server's statement log:** every proof connection ran `SELECT set_config('TimeZone', 'UTC', false)` (Django's session setting), then the marker query, then its own work; the refused connection ran those two and nothing else. `run` opened five connections, all before the cases.
- No marker or password appeared in the run's output, the results JSON or the refused `migrate`'s output (counted with `grep -c -F -f` against the files, never printed). The server's statement log held the role's creation statement and the comment, as `log_statement = 'all'` records them; it stayed in the cluster's directory, was never printed, and was removed with it.

At the end I stopped the cluster (`pg_ctl stop -m fast` printed `server stopped`; `pg_isready` then printed `no response`) and removed its directory. No cluster directory and no live postgres process remained; one `<defunct>` entry from the failed first start (its log file was not writable by the `postgres` user) stays in the sandbox's process table. The package's `.venv/` is gitignored and stays only in the sandbox; `.work/` was removed.

### Checks

| Check | Command | Result |
|---|---|---|
| 1 | `git diff --check ad3323d… HEAD` | clean |
| 1 | `git diff --name-only ad3323d… HEAD` (code head) | `.github/workflows/foundation.yml`; `proofs/postgres-ordering/README.md`; `glow_ordering_proof/environment.py`, `marker.py` (new), `settings.py`; `tests/command_harness.py` (new), `test_marker.py` (new), `test_marker_commands.py` (new), `test_settings_refusals.py` (its `GOOD` gains a marker made with `secrets.token_hex(16)`); and, in the records commit, this record. Nothing else: no dependency file, no `services/` path, no other job |
| 2 | trusted policy from `main` (`47db18d`, sha256 `dec69a26…`) extracted to a temporary directory, `python3 -I <tmp>/change_scope.py --base ad3323d… --head 43d8ca4… --merge-base`, from the repository root | `{"full": true, "reason": "behavior-or-empty", …}`, 9 paths: full scope |
| 3 | `python3.12 -m venv .venv`; `pip install --require-hashes -r requirements-dev.lock` in `env -i` with the proxy and CA variables by reference; `pip check` | installed; `No broken requirements found.` |
| 4 | `env -i PATH HOME LANG=C.UTF-8 .venv/bin/python -m unittest discover -s tests -t .` | 82 tests at the start (C1's count); at the head `Ran 98 tests`, `OK` (new: `test_marker` 14, `test_marker_commands` 2) |
| 4 | `.venv/bin/ruff check .`; `.venv/bin/ruff format --check .` | `All checks passed!`; `32 files already formatted` |
| 4 | `.venv/bin/mypy` | `Success: no issues found in 32 source files` |
| 4 | the Django pin test (`python -m unittest tests.test_django_pin`) | `Ran 4 tests`, `OK` |
| 4 | `cd services/api && python3.12 -m unittest tests.test_toolchain_pins` | `Ran 3 tests`, `OK` |
| 5 | local runs | above, iteration, not evidence |
| 6 | the Foundation run on the code head | run 37262466651 above |
| 7 | secret scan over `git diff ad3323d… HEAD` (added lines: password, secret, token, API key, private-key markers, connection strings, email addresses, hex runs of 32 or more) | no secret, password, marker value or email address; the matches are the words in the workflow's variable names and comments, `token_hex` and `import secrets` |

### Deviations and limits

- **The marker's masks are the credentials step's third and fourth lines of output,** after the two passwords' masks; all four masks come before any other output. DM-10 2.4 says "as that step's first output"; I read the masks together as that output.
- **The check prints one line per new connection** (`database marker verified on a new connection: backend pid …, thread …`), with no value. It is not in DM-10's conditions; I added it so the log shows, as 2.5 asks the review to confirm, that no worker reconnected inside a race.
- **The per-schema count left-joins `pg_class`,** so a schema with no relation (`public`) is printed with `0` rather than left out. The counts are still of `pg_class` rows joined to `pg_namespace`.
- **The check's `SELECT` runs in autocommit** (Django sets autocommit before the signal, and `atomic()` turns it off only after the connection exists). It assigns no transaction ID and takes no row lock; like any `SELECT` it holds `AccessShareLock` on the catalogs it reads for the statement's duration. The local statement log shows no `BEGIN` before it.
- **The races ran slower than in C1's run** (each race 4.2 to 7.1 s against 2.7 to 4.6 s; the suite step 72 s against 48 s) and measured more overlaps (197 to 200 against 174 to 200). The marker query cannot cause either: the log shows it ran on five connections, all before the cases. A different runner is the likely cause; I did not establish it. The budget's 30-second cap per race was not approached.
- **R1 is visible in this run:** in `race.sign_out_sender` the send never committed first, and in `race.expire_sender` once. This is the recorded limit (the README's "Limits", R1), and the forced cases cover that order.
- **Local iteration ran on PostgreSQL 16.14,** not 17.11 (D4 condition 3), with `log_statement = 'all'`, which the CI job does not set.
- **The marker does not replace the reused-database guard** (R2), carried to P06.2, nor CX1, CX2, R1 or the tests for R3 and R4.
- **Not found:** anything more in the prompt's four "fix here only if" classes.

### What the exact-head review must know

- The code to review is `43d8ca428ea25aef485af0e7d5f3a1840a2ae0c6`; its run is 37262466651 (the database job's log, job 111612413204). The later commit changes only this record.
- **DM-10's 2.5:** the plan is `ea21ac8`'s: 55 cases, 10 controls, the same twelve races, seed, budget and floors. The run shows 55 of 55, every control failed as intended by its declared signal, 0 violations in the design's rows, and each of the 25 held cases observed waiting on its holder. No race, case, control, floor or reference-design file changed (`git diff --name-only ea21ac8… 43d8ca4 -- proofs/postgres-ordering/glow_ordering_proof` lists only `environment.py`, `marker.py` and `settings.py`). The marker query runs only in the `connection_created` receiver, that is, at connection creation (`marker.py:55`, `:67`), and the log's eight verification lines, the last five all before `cases: 55/55 passed`, show that no worker reconnected inside a race.
- **DM-11's note on 2.4:** in the workflow diff, each step that needs a marker reads it from the job's `mktemp -d` directory with `$(cat "$DIR/…")` into `PROOF_DB_MARKER` for its own command (`foundation.yml:302`, `:341`, `:354`); the role step reads the comment from `create-role.sql` (`:244`, `:278`). Nothing writes a marker to `$GITHUB_ENV` or `$GITHUB_OUTPUT`; the step outputs are still only `dir` and `container`.
- **DM-11's three precisions** are in the step: `starts_with(n.nspname, 'pg_')`, not `LIKE`; `psql -d glow_proof`, never `postgres`; per-schema counts compared before and after with `cmp`, `pg_toast` included.
- `RefusedDatabase` is not a `DatabaseError` on purpose; the command harness's `makemigrations` case and the mutation run show why.
- The offline tests replace only the backend's driver-facing methods in a subprocess (`tests/command_harness.py`); no test opens a database.

### Manager verification of P06.DB-C2 (App Manager 5, 5 October 2026)

App Manager 5 checked the relayed report against the pushed branch, the code and hosted CI. The manager started no database: its re-run below is the offline checks only.

- **Identity:**
  - branch `claude/ecstatic-feynman-749ccu`, final head `1178dfa450cce88daf354de8b7b2f0434800fc05`, tree `d22b6f7174d8e889f876299299b55246cdde225a`, as reported. Two commits on the start `ad3323d`: `43d8ca4` (the code; tree `b1d74ade790e1bd57c24254e72f8d53313746cdf`), then `1178dfa` (this record only);
  - 10 paths. The code commit changes 9: the workflow, the README, `environment.py`, `marker.py` (new) and `settings.py` under `glow_ordering_proof/`, and `command_harness.py`, `test_marker.py`, `test_marker_commands.py` (all new) and `test_settings_refusals.py` under `tests/`; +683 and −18. The records commit appends the section above, 157 lines; every earlier line of this record is byte-identical. No dependency file, `services/`, `scripts/`, `apps/` or `packages/` path changed, and `git diff --check` is clean;
  - **integrated** with a merge commit, `369d03c5cd1ed3537e044335bfb6ecc4cbc25f9a` (first parent `ad3323d`, the manager branch; second parent `1178dfa`). Its tree is `1178dfa`'s.
- **Classification:** the trusted policy from `main`, outside the tree, with `python3 -I` and full SHAs: `ad3323d` → `43d8ca4` is full scope (`behavior-or-empty`), 9 paths; `ad3323d` → `1178dfa` is full scope, 10 paths; `43d8ca4` → `1178dfa` is `ordinary-docs-only`.
- **The workflow change,** checked as the CI policy requires for one: classified with the pre-change policy (`main`'s; PR28 does not change the classifier), the whole diff read, and the job's actual steps and results read from run 37262466651.
  - Only the `database` job changed. The diff has no hunk outside it, so the other six application jobs, the scope job and the gate are byte-identical.
  - The credentials step generates the run's marker and a second well-formed one with `secrets.token_hex(16)`, masks both right after the passwords' masks, refuses if they are equal, and writes them to `marker` and `wrong-marker` in the job's `mktemp -d` directory, mode `0600`. `create-role.sql` gains the `COMMENT ON DATABASE` statement, which the role step pipes into `psql` with its output withheld, then deletes.
  - The new step, before the migrations, runs `psql -d glow_proof` as the superuser inside the container. It counts relations per schema with a left join, counts relations outside `information_schema` and the schemas for which `starts_with(n.nspname, 'pg_')` is true, and asks `to_regclass('public.django_migrations') IS NULL`. It fails on an exit status of 0, a missing refusal line, any changed count (`cmp` of the two tables), any relation outside, or a ledger. DM-11's three precisions hold.
  - DM-11's note on 2.4 holds: each step that needs a marker takes it from the directory with `$(cat "$DIR/…")` into `PROOF_DB_MARKER` for its own command. Nothing writes a marker to `$GITHUB_ENV` or `$GITHUB_OUTPUT`; the step outputs are still `dir` and `container`. The removal step deletes the directory.
- **The code, read whole.**
  - `environment.py`: `PROOF_DB_MARKER` is in `PROOF_NAMES`; `MARKER_FORM` is `[0-9a-f]{32}`, applied with `fullmatch`; `database_marker` refuses a missing or malformed value by name; `expected_comment` is the prefix and the marker.
  - `marker.py`: `install` connects the receiver to `connection_created` with a `dispatch_uid` and `weak=False`. The receiver reads `pg_backend_pid()` and `shobj_description(d.oid, 'pg_database')` for `current_database()`, and refuses with no installed marker, no row, a null comment or any other comment, closing the connection through Django first. A failing query closes the connection and re-raises. `RefusedDatabase` is not a `DatabaseError`.
  - `settings.py` calls `marker.install` at import. No package code opens a connection outside Django: `psycopg.connect` appears nowhere, and `connection_created` only in `marker.py`.
- **Offline re-run** in a scratch worktree of `43d8ca4`, with Python 3.12.14 and every command in a clean process (`env -i`). The environment was the one installed from the locks for C1's verification; no dependency file changed since `ea21ac8` (Django 5.2.17, psycopg 3.3.6, Ruff 0.16.8, mypy 2.3.1). `python -m unittest discover -s tests -t .`: `Ran 98 tests`, `OK`. Ruff check: "All checks passed!"; Ruff format check: "32 files already formatted"; mypy: "Success: no issues found in 32 source files". The command harness replaces only the backend's driver-facing methods (its `get_new_connection` returns a plain object) and opens no socket.
- **Fix reversals,** in the manager's own run: each change undone alone in the worktree, then the whole suite.

  | Reversal | Result |
  |---|---|
  | The package's code back to `ad3323d`'s, the new tests kept | 3 errors: the new test modules cannot import the marker's names |
  | The settings do not install the check | 26 failures |
  | A refusal does not close the connection | 23 failures |
  | The comment compared by prefix (`startswith`) | 7 failures |
  | The marker's form checked with `match`, not `fullmatch` | 4 failures |
  | `RefusedDatabase` as a Django `OperationalError` | 6 failures |

  The unchanged copy passes, before and after. The manager's first pass at this table restored the worktree wrongly after the first reversal, so the later results tested a reverted tree; they were discarded and the reversals redone (AM5-20).
- **Hosted CI:**
  - Foundation run [37262466651](https://github.com/amthorn78/glow-dating-app/actions/runs/37262466651) on `43d8ca4`, a push run: all eight jobs succeeded, and the gate (job 111613560771) printed `Application checks passed`.
  - The records push run 37263032448 on `1178dfa`: the six application jobs were skipped, and its gate printed `Ordinary documentation: application jobs intentionally skipped`, as the CI policy designs. The session had not opened it.
- **The database job's log, read whole** (job 111612413204; 905 lines as the API returns them, where the session counted 904), against the section above:
  - the wrong-marker step: exit status `1`; the refusal line, which carries no value; the per-schema counts identical before and after (`information_schema` 69, `pg_catalog` 266, `pg_toast` 80, `public` 0); 0 relations outside, before and after; `django_migrations` absent (`t`);
  - the image digest `sha256:d74eeac9…`; PostgreSQL 17.11; `superuser` false; `track_commit_timestamp` on; `read committed`; the sixteen migrations; `No changes detected`; `Ran 98 tests`, `OK`;
  - eight `database marker verified on a new connection` lines: one each for `migrate` (backend pid 130), `makemigrations` (131) and `facts` (132), and five for `run` (133 to 137), the main thread's and one per writer thread. `run` opened no other connection, so none was re-created inside a case, race or control;
  - `cases: 55/55 passed`, and each of the 25 held cases shows `pg_blocking_pids=[134] (holder pid 134)`;
  - the twelve races, the ten controls and the oracle (526 submissions, 2,694 revocation rows, 0 violations in the design's rows, the control tags' violations as C1's), exactly as the section's tables give them; `== VERDICT: PASS ==`;
  - **no password and no marker:** the only `***` are on lines 38 and 94 (`actions/checkout`) and 152 (`actions/setup-python`), all before the credentials step (line 344). No 32- or 48-character hexadecimal string appears; the long ones are 40-character commit SHAs and 64-character digests and IDs. The passwords and the comment appear only in the step's script text, as `%s` templates;
  - disposal: `container removed: glow-proof-db-37262466651-1`, `credential and marker files removed`, `no proof container remains`.
- **The section's comparison with C1:** its C1 column matches "P06.DB-C1 corrections" (each race's overlaps and seconds, 617 submissions, `design:stress` 574, the controls' violations, pids 98 and 97).

#### Observations for the exact-head review

1. **The races ran slower in this run, with more overlaps:** 4.2 to 7.1 s against 2.7 to 4.6 s, and 197 to 200 overlaps against 174 to 200. The same day, PR run 37260032996 on `ad3323d`, the code before C2, gave 2.6 to 4.6 s and 174 to 200 (job 111605158228, Azure region `westus3`); C2's run ran in `westus`. The marker query ran only on `run`'s five connections. A slower runner fits both differences but is not established. PR28's pull-request run on the integrated head runs C2's code again.
2. **The masks' order** (the section's first deviation). DM-10's 2.4 says the marker is masked "as that step's first output". The step's first four outputs are the four `::add-mask::` lines, the passwords' first; its only other output is its closing line. The manager reads this as within 2.4.
3. **The verification line** (the section's second deviation): one line per new connection, with its backend pid and thread and no value. It is not in DM-10's conditions. The hook still runs one `SELECT` and nothing else, and the line gives 2.5's reconnect check a direct record. The manager reads it as within 2.2.
4. **A failing marker query.** If the query itself raises, for example on a dropped connection or a server that is not PostgreSQL, the receiver closes the connection and re-raises the driver's error as Django wraps it. That ends `migrate`, `facts` and `run`. `makemigrations` alone turns a Django `OperationalError` from its consistency check into a warning and carries on; `makemigrations --check --dry-run` changes no database, and in the job it runs after `migrate`. Not in a correction class, in the manager's reading.
5. **R1 again:** in `race.sign_out_sender` the send never committed first, in `race.expire_sender` once and in `race.opposing_writers` never. The P11 plan's R1 limit now cites this run as well.

#### Dispositions

- **CX3 is corrected:** the proof refuses any database whose comment is not the run's marker, under DM-10's conditions 2.1 to 2.4 and DM-11's words for 2.3's check. The manager found nothing in the four correction classes.
- **The run of record** for the final code is run 37262466651 (the C2 prompt). The P11 plan's DB06 and DB09 entries cite it; the marks stand as worded.
- **The CI policy** takes DM-10's sentence, as written (its item 4), in the batch that records this verification.
- **AM5-20** is logged, a summary row: the slip reached no record.
- **Next:** C2's exact-head review ([prompt](../../ephemeral/2026-10-05-p06-db-c2-review-prompt.md)), of `369d03c`, offline, reading job 111612413204's log; it checks DM-10's 2.5 and DM-11's note on 2.4.

# P06.DB disposable-PostgreSQL proof: send-versus-revocation ordering and a minimal sign-in

A proof harness that runs the app's reviewed persistence schema (`services/api/glow_persistence`, imported unchanged) against a real PostgreSQL database that exists only for the proof, and shows that one transaction boundary orders a send authorization against every revocation of contact: a block by either member, an unmatch, a suspension or deletion of either account, and a sign-out or expiry of the sending session. It also runs a minimal sign-in: a user through `django.contrib.auth`, its `AppAccount`, and an `AccountSession` bound to the account's `session_epoch`.

Brief: [P06.DB](../../docs/planning/p06-db-disposable-postgres-proof.md) (revision 2, with the Dev Manager's DM-08 conditions). Authority: OD-17. Evidence: [2026-09-29 P06.DB evidence](../../docs/testing/evidence/2026-09-29-p06-db-disposable-postgres-proof.md).

This is proof tooling, not application code. The API's settings, configuration guards, fixture mode and dummy database backend do not change, and no app code path gains a database. The reference design lives here; P06.2 carries it into the app's persistence adapter and runs the same suite against it through the one interface in `glow_ordering_proof/interface.py`.

## What it proves, and what it does not

**Proves, on the disposable database of one CI job** (the evidence of record is the Foundation job "Database proof checks" on the final head):

1. **Setup, not acceptance** (PF01 §6). From an empty database, Django's `auth` and `contenttypes` migrations and the reviewed `glow_persistence` migrations `0001` and `0002` apply, and `makemigrations --check --dry-run` finds no change. The applied ledger is read back from `django_migrations`.
2. **DB06, partially.** The reference design (D5) orders a send authorization, a `MessageSubmission` with its `OutboxEvent` in one transaction, against every revocation above, under forced interleavings on two real connections and under seeded randomized races, with a commit-order oracle over every row, observed lock waits, and negative controls that fail in the same run.
3. **DB09, partially.** The app-side session and epoch revocation ordering against sends, with a stand-in `auth_session_ref`: sign-out and administrative expiry revoke one session; suspension and deletion revoke every session of the account through the epoch; a revoked, expired or stale-epoch session cannot authorize a send, including a session that expires while the send waits on a lock.

**Does not prove** (brief, D6): that the app enforces any of it (the design is in this package until P06.2 carries it and tests it again); DB06's provider half (channel membership, a send the provider already accepted); the P11 target, its roles, pooling or load; maintained authentication, verification, recovery, linking, credential revocation or allauth, which stay with the item that serves authentication and with P11. P11A and P11B rerun DB06 and DB09 on the real target. A paused or restricted profile and a withdrawn consent are excluded from the send's checks (A05 has not set their effect on an existing conversation).

## Layout

| Path | What it is |
|---|---|
| `glow_ordering_proof/settings.py` | The proof's own Django settings. Refuses to start if `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, any other name on the API's forbidden connection list or any `PG*` name is present. Explicit loopback or Unix-socket connection with a `passfile`; no service name, so libpq takes nothing from its environment or default files. Never imports the API's settings |
| `glow_ordering_proof/environment.py` | The refusal and connection rules as pure functions, and the proof's variable names (`PROOF_DB_HOST`, `PROOF_DB_PORT`, `PROOF_DB_NAME`, `PROOF_DB_USER`, `PROOF_DB_PASSFILE`) |
| `glow_ordering_proof/interface.py` | The one small interface the suite drives: `OrderingSubject` (sign-in, sign-out, expiry, send, block, unblock, unmatch, suspend, delete), `FixtureFactory`, `Result`, `Hooks` |
| `glow_ordering_proof/design.py` | The design's switches; the reference is `Design()`, each negative control flips one |
| `glow_ordering_proof/reference.py` | The reference design under proof (D5, below) |
| `glow_ordering_proof/cases.py` | The forced interleavings and the named cases |
| `glow_ordering_proof/stress.py` | The seeded stress run and its overlap measure |
| `glow_ordering_proof/oracle.py` | The commit-order oracle over every row |
| `glow_ordering_proof/controls.py` | The negative controls |
| `glow_ordering_proof/observe.py` | The proof log table, lock-wait observation (`pg_stat_activity`, `pg_locks`), server facts, the migration ledger |
| `glow_ordering_proof/budget.py` | The stress budget and floors, fixed in code |
| `glow_ordering_proof/results.py` | The report, its JSON and the printed table |
| `tests/` | Offline tests: no database |

## The reference design (D5)

`READ COMMITTED` with row locks. Every writer runs in one `transaction.atomic()` and locks rows by primary key with `SELECT ... FOR UPDATE` in one canonical order: the lower account, the higher account, the match, then the sending session's `AccountSession` row. State is checked in code after the locks, never filtered inside the locked read (5.5). Time is read with `clock_timestamp()` after the locks (5.2). The send authorizes first and deduplicates second (5.4). The send checks: the match is `active` and its pair unchanged, both accounts `active`, the session `valid`, unexpired and at its account's `session_epoch`, no `active` block in either direction, and the contact version equals the one the client sent (5.6); then it looks up `(actor, idempotency_key)`, and inserts the `MessageSubmission` and its `OutboxEvent`.

The revocations take the same locks in the same order: a block records its `Block` row (inserted, or `removed` to `active`), bumps the actor's `blocks_version` and turns an `active` match `restricted` with its contact version bumped; an unblock removes the block and leaves the match as it is; an unmatch turns the match `unmatched` and bumps its contact version; a suspension or deletion locks the account row only, changes its state and bumps its `session_epoch` (5.3); deletion is the lifecycle transition to `deletion_pending` with the `DeletionJob` and `DeletionTombstone`, never a hard delete (5.6); a sign-out or administrative expiry locks the session row the send locks (5.1). Each writer records one row in the proof's log table inside its transaction, so the oracle can read its commit time.

The sign-in creates the `AccountSession` with a random stand-in `auth_session_ref` (D2). The stand-in generator is not carried into the app; P06.2 or the item that serves authentication supplies the real identifier. Fixture accounts are created through `django.contrib.auth` with no password (credentials are the library's, out of scope) and start `active`.

## How a pass is judged

- **Forced interleavings**, for each of the ten revocations: the send commits first sequentially; the revocation commits first sequentially; the revocation arrives while the send holds its locks; the send arrives while the revocation holds its locks. Before the first transaction is released, the second connection must be observed waiting: `pg_stat_activity.wait_event_type = 'Lock'` for its backend, with the not-granted entry from `pg_locks`. A case whose wait was not observed fails.
- **Named cases**: a stale contact version; the four retry rules of 5.4, with the racing duplicates forced; unblock does not resurrect (and a re-block); a session that expires while the send waits; sign-out and expiry against a send both ways; opposing writers with no deadlock (pairwise forced, and four writers together for ten rounds); the first block against a send; the minimal sign-in's revocations; deletion keeping the committed authorization.
- **The commit-order oracle** (`oracle.py`): with `track_commit_timestamp=on`, `pg_xact_commit_timestamp(xmin)` of each row is its commit time. Over every `MessageSubmission`: no revocation that invalidates it (a contact revocation above its version, a revocation of its session, a suspension or deletion of either member) committed before or with it; it committed before its session's expiry; its contact version and epoch are exactly what the revocations committed before it imply; one row per idempotency key. Zero violations in the design's rows.
- **The stress run** (`stress.py`): each race repeated with fresh fixtures, both writers started together with a seeded head start of up to 3 ms, within the budget in `budget.py`: up to 200 iterations or 30 seconds per race, whichever first. An overlap is measured from the database: each writer's interval is `now()` inside its transaction to its commit timestamp (or to `clock_timestamp()` read just before its rollback, recorded afterwards as an attempt row), and an iteration overlapped when the send's and a revocation's intervals intersect. A race with fewer than 50 iterations or fewer than 10 overlaps fails the job. The seed, iterations, overlaps and outcome counts are printed.
- **Negative controls** (`controls.py`): no row locks, no version check, no session lock, `now()` in place of a time read after the locks, deduplication before authorization, the lock order inverted for one writer, no account lock, and a state filter inside the locked read. Each runs in the same job under its broken `Design`. A forced control must fail its case deterministically; a stress control must produce a violation within the budget, and its first failing iteration is recorded. A control that never fails fails the job.
- **The table**: the run prints the server facts (`SELECT version()`, `track_commit_timestamp`, the role's `rolsuper`, the observed transaction isolation), the migration ledger, every case with its observed waits, every race, every control and the oracle's counts, then `VERDICT: PASS` or `FAIL` with reasons. It prints no password and no connection option. `--results` also writes the same as JSON.

`SERIALIZABLE` is not run (D5 makes it optional and `READ COMMITTED` with row locks is the design).

## Install

From this directory, with the pinned toolchain (Python 3.12.14):

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock
.venv/bin/python -m pip check
```

In a Claude Code cloud session pip needs the proxy and CA variables, passed by reference and never printed (`HTTPS_PROXY="$HTTPS_PROXY" PIP_CERT="$PIP_CERT" ...`).

The locks were generated with uv 0.8.17:

```bash
uv pip compile requirements.in --python-version 3.12 --generate-hashes --output-file requirements.lock --no-header
uv pip compile requirements-dev.in --python-version 3.12 --generate-hashes --output-file requirements-dev.lock --no-header
```

Django is pinned to 5.2.17 as `services/api` pins it, with the same wheel hashes; `tests/test_django_pin.py` fails if they differ. The driver is `psycopg[binary]` 3 (D2). No allauth.

## Checks (offline)

No database. The tests run in a clean environment and show each refusal of the settings, the case plan, the result recording, the budget's floors and the Django pin:

```bash
env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8 .venv/bin/python -m unittest discover -s tests -t . -v
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
```

## Running against a disposable database

Only against a database that exists for the proof: the CI job's container, or a throwaway cluster in a session's own sandbox (brief, D4). Never against a shared, staging or production database, and never with the API's settings. The commands run in a clean process environment that carries only the proof's variables:

```bash
env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8 \
  PROOF_DB_HOST=127.0.0.1 PROOF_DB_PORT=5433 PROOF_DB_NAME=glow_proof PROOF_DB_USER=glow_proof \
  PROOF_DB_PASSFILE=/path/readable/only/by/you/passfile \
  DJANGO_SETTINGS_MODULE=glow_ordering_proof.settings \
  .venv/bin/python -m django migrate
# then, with the same variables:
#   python -m django makemigrations --check --dry-run
#   python -m glow_ordering_proof facts
#   python -m glow_ordering_proof run --seed 20260929 --results .work/results.json
```

`PROOF_DB_HOST` is `127.0.0.1`, `localhost`, `::1` or an absolute Unix-socket directory; anything else is refused. The passfile is a libpq password file (`host:port:database:user:password`, mode `0600`); the password appears nowhere else. The proof connects as a non-superuser role that owns the database, and `run` refuses a superuser, a server without `track_commit_timestamp=on`, and any isolation level but `read committed`.

The Foundation job "Database proof checks" does all of this on every change that is not ordinary documentation: the hash-locked install and `pip check`, the offline tests under `env -i`, Ruff and mypy; then it generates two passwords under `set +x` with `::add-mask::` as its first output, writes them to files readable only by the job's user, starts the official `postgres` image at 17.11 pinned by digest with `docker run` on `127.0.0.1:5433` with `-c track_commit_timestamp=on` (the superuser's password reaches the container through `POSTGRES_PASSWORD_FILE` from a read-only mount), waits with `pg_isready` within 60 seconds, creates the non-superuser role and its database inside the container over its Unix socket, runs `migrate`, `makemigrations --check --dry-run`, `facts` and `run`, uploads the results JSON, and removes the container, its volume and the credential files in an `if: always()` step. The job has no `env:` of secrets, reads no `PG*` or `DATABASE_URL` name, and runs no `docker inspect`.

**Local runs are iteration, not evidence** (D4). A session may start a throwaway cluster with `docker run` under the same recipe, or from local binaries (`initdb` in a temporary directory listening only on a Unix socket or loopback, `-c track_commit_timestamp=on`), with a generated password, a non-superuser role, none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present, and removes it afterwards. Its PostgreSQL version may differ from CI's 17.11 and is recorded as such.

## Limits

- The evidence of record is the CI job's run on the final head. The report says which local database, if any, a session used.
- The design is proven here, not in the app. P06.2 carries it into the persistence adapter and runs this suite against it; P11A and P11B rerun DB06 and DB09 on the real target.
- The oracle judges commit order with microsecond commit timestamps; it treats equal timestamps as a violation.
- `auth_session_ref` is a stand-in; credentials, verification and the maintained session are not exercised.
- The provider is never called; the `ChatBinding` is created locally with a stand-in channel reference.
- The stress run's overlaps are measured from database-clock intervals, not from observed lock waits; the forced cases observe the waits.
- The negative controls are broken variants of this package's own reference design; they show what this suite detects, not every way an adapter could be wrong.

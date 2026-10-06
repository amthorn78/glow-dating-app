# P06.DB disposable-PostgreSQL proof: send-versus-revocation ordering and a minimal sign-in, on two subjects

A proof harness that runs the app's reviewed persistence schema (`services/api/glow_persistence`, imported unchanged) against a real PostgreSQL database that exists only for the proof, and shows that one transaction boundary orders a send authorization against every revocation of contact: a block by either member, an unmatch, a suspension or deletion of either account, and a sign-out or expiry of the sending session. It also runs a minimal sign-in: a user through `django.contrib.auth`, its `AppAccount`, and an `AccountSession` bound to the account's `session_epoch`.

Brief: [P06.DB](../../docs/planning/p06-db-disposable-postgres-proof.md) (revision 2, with the Dev Manager's DM-08 conditions; the run's marker from revision 5, with DM-10's conditions and DM-11's words for the CI step). Authority: OD-17. Evidence: [2026-09-29 P06.DB evidence](../../docs/testing/evidence/2026-09-29-p06-db-disposable-postgres-proof.md).

**P06.2 Stage A** ([brief](../../docs/planning/p06-2-chat-integration.md), revision 2; [evidence](../../docs/testing/evidence/2026-10-05-p06-2-chat-integration.md)): the suite now runs on two subjects in the same run, each reported separately (D3). The **reference design** keeps its cases, its ten negative controls and its stress run, unchanged. The **app's adapter** (`services/api/glow_chat`, imported unchanged, as `glow_persistence` is) runs every case, D5's extra revocations, the stress run and the oracle over its own rows; a guarantee is claimed for the app only from this run. Then a **delivery phase** runs the app's outbox delivery against the fixture provider. P06.DB's carried items 1 to 6 are in place: a used database and `dbshell` are refused, the oracle checks who sent (O9) and the narrowed expiry rule (O5), commit orders are counted per race, and the tests for R3 and R4 exist.

This is proof tooling, not application code. The API's settings, configuration guards, fixture mode and dummy database backend do not change, and no app runtime gains a database: the adapter runs only here, under the proof's settings.

## What it proves, and what it does not

**Proves, on the disposable database of one CI job** (the evidence of record is the Foundation job "Database proof checks" on the final head):

1. **Setup, not acceptance** (PF01 §6). From an empty database, Django's `auth` and `contenttypes` migrations and the reviewed `glow_persistence` migrations `0001` and `0002` apply, and `makemigrations --check --dry-run` finds no change. The applied ledger is read back from `django_migrations`.
2. **DB06, partially.** The reference design (D5) orders a send authorization, a `MessageSubmission` with its `OutboxEvent` in one transaction, against every revocation above, under forced interleavings on two real connections and under seeded randomized races, with a commit-order oracle over every row, observed lock waits, and negative controls that fail in the same run.
3. **DB09, partially.** The app-side session and epoch revocation ordering against sends, with a stand-in `auth_session_ref`: sign-out and administrative expiry revoke one session; suspension and deletion revoke every session of the account through the epoch; a revoked, expired or stale-epoch session cannot authorize a send, including a session that expires while the send waits on a lock.

4. **P06.2 Stage A, the app's adapter.** Items 2 and 3 above, shown again by the adapter's own run (its cases, races and oracle), with D5's additions: a paused or restricted profile and a withdrawn onboarding consent refuse a send, each writer joining the lock protocol, with its four forced interleavings and a stress race (pause, restriction, withdrawal). The outbox turns match activation, each authorized send and each revocation into one call to a fixture chat provider, idempotently.

**Does not prove** (brief, D6; P06.2's brief, D6 to D8): DB06's provider half against Stream (Stage B), or a real provider outage; a deployed delivery worker, crash recovery or concurrent deliverers (P11); the P11 target, its roles, pooling or load; maintained authentication, verification, recovery, linking, credential revocation or allauth, which stay with the item that serves authentication and with P11. P11A and P11B rerun DB06 and DB09 on the real target. The reference design still excludes D5 (P06.DB 5.6); only the adapter carries it.

## Layout

| Path | What it is |
|---|---|
| `glow_ordering_proof/settings.py` | The proof's own Django settings. Refuses to start if `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, any other name on the API's forbidden connection list or any `PG*` name is present, or if `PROOF_DB_MARKER` is missing or malformed. Explicit loopback or Unix-socket connection with a `passfile`; no service name, so libpq takes nothing from its environment or default files. Registers the marker check on every new connection. Installs the proof package as an app, for its `dbshell`. Never imports the API's settings |
| `glow_ordering_proof/apps.py`, `management/commands/dbshell.py` | P06.2 (carried item 6, DM-12): the proof's own `dbshell`, which Django loads before its own under these settings; it refuses with the marker's `RefusedDatabase`, opening no connection and starting no client |
| `glow_ordering_proof/adapter.py` | P06.2: the app's adapter as the suite's second subject (`AdapterSubject`, which only translates types and records each call's context after it) and its fixtures (accounts with a visible profile and an accepted onboarding consent, matches through the adapter's activation) |
| `glow_ordering_proof/evidence.py` | P06.2: where each subject's evidence is: the reference design's proof log; the adapter's own rows (its submissions with their `message_submitted` events, its revocations' outbox events and consent decisions) with the harness's call rows for context |
| `glow_ordering_proof/planted.py` | P06.2: the oracle-level controls (DM-13 2.1), which plant one violation per rule in either subject's row shape |
| `glow_ordering_proof/delivery_phase.py` | P06.2: the outbox drained to the fixture provider, the end state of every design world, and the targeted delivery cases |
| `glow_ordering_proof/environment.py` | The refusal and connection rules as pure functions, the marker's form, and the proof's variable names (`PROOF_DB_HOST`, `PROOF_DB_PORT`, `PROOF_DB_NAME`, `PROOF_DB_USER`, `PROOF_DB_PASSFILE`, `PROOF_DB_MARKER`) |
| `glow_ordering_proof/marker.py` | The run's marker check: on every new connection, the database's comment must be exactly `glow-ordering-proof:` followed by `PROOF_DB_MARKER`, or the connection is closed and the command fails |
| `glow_ordering_proof/interface.py` | The one small interface the suite drives: `OrderingSubject` (sign-in, sign-out, expiry, send, block, unblock, unmatch, suspend, delete), `FixtureFactory`, `Result`, `Hooks` |
| `glow_ordering_proof/design.py` | The design's switches; the reference is `Design()`, each negative control flips one |
| `glow_ordering_proof/reference.py` | The reference design under proof (D5, below) |
| `glow_ordering_proof/cases.py` | The forced interleavings and the named cases |
| `glow_ordering_proof/stress.py` | The seeded stress run and its overlap measure |
| `glow_ordering_proof/oracle.py` | The commit-order oracle over every row |
| `glow_ordering_proof/controls.py` | The negative controls |
| `glow_ordering_proof/observe.py` | The proof log table, the adapter's call table and the world table, the used-database check, lock-wait observation (`pg_stat_activity`, `pg_locks`, `pg_blocking_pids`), server facts, the migration ledger |
| `glow_ordering_proof/budget.py` | The stress budget and floors, fixed in code |
| `glow_ordering_proof/results.py` | The report, its JSON and the printed table |
| `tests/` | Offline tests: no database |

## The reference design (D5)

`READ COMMITTED` with row locks. Every writer runs in one `transaction.atomic()` and locks rows by primary key with `SELECT ... FOR UPDATE` in one canonical order: the lower account, the higher account, the match, then the sending session's `AccountSession` row. State is checked in code after the locks, never filtered inside the locked read (5.5). Time is read with `clock_timestamp()` after the locks (5.2). The send authorizes first and deduplicates second (5.4). The send checks: the match is `active` and its pair unchanged, both accounts `active`, the session `valid`, unexpired and at its account's `session_epoch`, no `active` block in either direction, and the contact version equals the one the client sent (5.6); then it looks up `(actor, idempotency_key)`, and inserts the `MessageSubmission` and its `OutboxEvent`.

The revocations take the same locks in the same order: a block records its `Block` row (inserted, or `removed` to `active`), bumps the actor's `blocks_version` and turns an `active` match `restricted` with its contact version bumped; an unblock removes the block and leaves the match as it is; an unmatch turns the match `unmatched` and bumps its contact version; a suspension or deletion locks the account row only, changes its state and bumps its `session_epoch` (5.3); deletion is the lifecycle transition to `deletion_pending` with the `DeletionJob` and `DeletionTombstone`, never a hard delete (5.6); a sign-out or administrative expiry locks the session row the send locks (5.1). Each writer records one row in the proof's log table inside its transaction, so the oracle can read its commit time.

The sign-in creates the `AccountSession` with a random stand-in `auth_session_ref` (D2). The stand-in generator is not carried into the app; P06.2 or the item that serves authentication supplies the real identifier. Fixture accounts are created through `django.contrib.auth` with no password (credentials are the library's, out of scope) and start `active`.

## How a pass is judged

- **Forced interleavings**, for each of the ten revocations: the send commits first sequentially; the revocation commits first sequentially; the revocation arrives while the send holds its locks; the send arrives while the revocation holds its locks. Before the first transaction is released, the second connection must be observed waiting on the first: `pg_stat_activity.wait_event_type = 'Lock'` for its backend, with the not-granted entry from `pg_locks`, and the holder's backend among the backends `pg_blocking_pids` names for it (the holder's pid is captured as the arriver's is, when its transaction begins). A wait on any other backend does not count as observed. A case whose wait was not observed fails. The table prints the waiting backend, its blockers and the holder's pid.
- **Named cases**: a stale contact version; the four retry rules of 5.4, with the racing duplicates forced; unblock does not resurrect (and a re-block); a session that expires while the send waits; sign-out and expiry against a send both ways; opposing writers with no deadlock (pairwise forced, and four writers together for ten rounds); the first block against a send; the minimal sign-in's revocations; deletion keeping the committed authorization.
- **The commit-order oracle** (`oracle.py`): with `track_commit_timestamp=on`, `pg_xact_commit_timestamp(xmin)` of each row is its commit time. Over every `MessageSubmission`: no revocation that invalidates it committed before or with it, whether an applied contact revocation of its match (a block or unmatch whose log row carries a contact version, whatever that version is: O2), a revocation of its session, or a suspension or deletion of either member; it committed before its session's expiry; its contact version and epoch are exactly what the revocations committed before it imply; one row per idempotency key. Zero violations in the design's rows. O2 does not compare versions: a send stored at the version a block or unmatch set is still a send after that revocation. It holds for every row the design writes because in P06.DB a block or unmatch is never undone for its match: an unblock leaves the match `restricted`, and there is no rematch (P06.DB-C1, the exact-head review's F2). O6 still checks the stored version against the revocations before the send.
- **The stress run** (`stress.py`): each race repeated with fresh fixtures, both writers started together with a seeded head start of up to 3 ms, within the budget in `budget.py`: up to 200 iterations or 30 seconds per race, whichever first. An overlap is measured from the database: each writer's interval is `now()` inside its transaction to its commit timestamp (or to `clock_timestamp()` read just before its rollback, recorded afterwards as an attempt row). Each race reads only its own rows, by run tag, race (`case_id`) and iteration, for the overlap and for a stress control's per-iteration oracle check. An iteration overlapped when two of its own writers' intervals intersect: in a two-writer race the send's and the revocation's; in `race.racing_duplicates` the two sends'; in `race.opposing_writers` the send's and any revocation's. A race with fewer than 50 iterations or fewer than 10 overlaps fails the job. The seed, iterations, overlaps and outcome counts are printed. (Corrected in P06.DB-C1; the exact-head review's F1.) Before P06.DB-C1 the measure read every race's rows at the same iteration number, since all design races share one run tag and number their iterations from 1, and it counted only a send against a non-send. So the first run of record, Foundation run 36520940933, established the first race's count only, `race.block_by_low`'s 200 of 200. It did not establish the other eleven races' counts, and `race.racing_duplicates`, whose two writers are both sends, never measured its own overlap. The corrected per-race counts are in the [evidence record](../../docs/testing/evidence/2026-09-29-p06-db-disposable-postgres-proof.md), "P06.DB-C1 corrections".
- **Negative controls** (`controls.py`): no row locks, no version check, no session lock, `now()` in place of a time read after the locks, deduplication before authorization, the lock order inverted for one writer, no account lock, and a state filter inside the locked read. Each runs in the same job under its broken `Design`, and each declares the signal its broken switch must produce: the case signals (the arriver not observed waiting on the holder, the send committing after the revocation, an expected refusal missing, a deadlock) and the oracle rules one of whose violations must appear under the control's tag. A forced control must fail its case deterministically with that signal; a stress control must produce an oracle violation of a declared rule within the budget, and its first failing iteration is recorded. A control counts as failed as intended only when its declared signal is present: a harness error, a database error, a stress harness failure or any other failure does not count (P06.DB-C1, the exact-head review's F3). A control that does not fail as intended fails the job. The table prints each control's declared signal beside what the run showed.
- **P06.2's additions.**
  - **O9 (CX1):** each submission's actor is its session's account and a member of its match.
  - **O5, narrowed (CX2; the brief's D4, confirmed by DM-13):** the design checks expiry at a time read after its locks, so a submission is a violation when it committed at or after its session's expiry *and* its checks must have run after the expiry: its transaction began at or after it, or a writer of a row it locks ended inside its transaction at or after it (it waited). That keeps the detection of the `transaction_start_time` control. The forced case `named.session_expires_after_check` holds a send between its checks and its commit until the database clock passes the session's expiry: it is authorized, commits after the expiry, and is not a violation.
  - **O10 (D5, the adapter only):** as of the submission's commit, neither member's profile is paused or restricted and each member's latest onboarding consent is accepted.
  - **O0:** every revocation PostgreSQL holds has its witness (a match's contact version, an account's epoch, a session's end, a profile's version), so a revocation applied without its witness cannot hide from O2 to O4.
  - **The adapter's evidence:** the adapter writes no proof row. Its submission's commit time is its own row's, its witness is the `message_submitted` event with the same `xmin`, and its revocations' commit times are their outbox events' and consent decisions'. The call rows the harness writes after each call carry only the run tag, the request's session and the transaction's start; none is a commit time.
  - **Commit orders (carried item 2):** each race prints its iterations per commit order (the send first, or the revocation first), judged from the same database intervals; in the sign-out and expiry races the revocation gets a seeded extra delay of up to 8 ms on about half the iterations.
  - **Planted controls (DM-13 2.1):** the adapter carries no fault switch, so for each rule a control writes one violating row in the subject's shape (CX1's misattributed row among them) and the oracle must report that rule under the control's run tag. They run on both subjects; the two for O10 on the adapter only.
  - **The delivery phase**, after both oracles (delivery updates rows the oracle reads): the outbox is drained, first in, first out; then every design world is checked against the fixture provider (an active match's channel has exactly its two members, a revoked one none, every authorized message once and none after the removal, every suspended or deleted member deactivated with one token revocation per epoch bump, nothing but identifiers and members sent); then the targeted cases (each event kind, a retry before and after the provider acted, provider text kept out, a revocation committed after an authorization and before its delivery, a dead letter).
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

No database. The tests run in a clean environment and show each refusal of the settings (the run's marker's form among them), the marker check against a fake connection and cursor, every command (`migrate`, `makemigrations --check --dry-run`, `facts`, `run`) refusing a wrong comment through Django's real connection path with a fake server (`tests/command_harness.py`), the case plan, the result recording, the budget's floors, the Django pin, and, on constructed rows with the database reads replaced, the per-race overlap measure, the oracle's rules, the controls' declared signals and the wait decision:

```bash
env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8 .venv/bin/python -m unittest discover -s tests -t . -v
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/mypy
```

## Running against a disposable database

Only against a database that exists for the proof: the CI job's container, or a throwaway cluster in a session's own sandbox (brief, D4). Never against a shared, staging or production database, and never with the API's settings.

**The run's marker** (brief D1; DM-10 2.1, 2.2 and 2.4). Whoever creates the disposable database generates a new marker for it, `python3 -c 'import secrets; print(secrets.token_hex(16))'`, keeps it in a file readable only by them, and right after creating the database sets its comment, as the database's owner or a superuser, from a file so that nothing prints the statement:

```sql
CREATE DATABASE glow_proof OWNER glow_proof;
COMMENT ON DATABASE glow_proof IS 'glow-ordering-proof:<the marker>';
```

Each new database gets a new marker; never reuse one. Every connection the proof's settings open through Django is checked: `migrate`, `makemigrations`, `facts`, `run` and any other command that queries through Django read the comment on each new connection, before any statement but the connection's own session settings. Unless the comment is exactly `glow-ordering-proof:` followed by `PROOF_DB_MARKER`, the command closes the connection and fails, naming `PROOF_DB_MARKER` and no value. **`dbshell` is refused** (P06.2, carried item 6): Django's `dbshell` would start `psql` outside Django, so under these settings the proof's own command replaces it and refuses before any connection. **`run` refuses a used database** (P06.2, carried item 1): a proof table or an app account that already holds rows means an earlier run wrote there, so each run needs a new database. `PROOF_DB_MARKER` must be exactly 32 lowercase hexadecimal characters, or the settings refuse at import. The marker is not a credential, but it is handled like one: never printed or logged. It does not replace the reused-database guard carried to P06.2 (see "Limits").

The commands run in a clean process environment that carries only the proof's variables:

```bash
env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8 \
  PROOF_DB_HOST=127.0.0.1 PROOF_DB_PORT=5433 PROOF_DB_NAME=glow_proof PROOF_DB_USER=glow_proof \
  PROOF_DB_PASSFILE=/path/readable/only/by/you/passfile \
  PROOF_DB_MARKER="$(cat /path/readable/only/by/you/marker)" \
  DJANGO_SETTINGS_MODULE=glow_ordering_proof.settings \
  .venv/bin/python -m django migrate
# then, with the same variables:
#   python -m django makemigrations --check --dry-run
#   python -m glow_ordering_proof facts
#   python -m glow_ordering_proof run --seed 20260929 --results .work/results.json
```

`PROOF_DB_HOST` is `127.0.0.1`, `localhost`, `::1` or an absolute Unix-socket directory; anything else is refused. A loopback host names a route, not a database, so the host check alone does not tie the proof to the database created for the run; the marker does. The passfile is a libpq password file (`host:port:database:user:password`, mode `0600`); the password appears nowhere else. The proof connects as a non-superuser role that owns the database, and `run` refuses a superuser, a server without `track_commit_timestamp=on`, and any isolation level but `read committed`.

The Foundation job "Database proof checks" does all of this on every change that is not ordinary documentation: the hash-locked install and `pip check`, the offline tests under `env -i`, Ruff and mypy; then it generates two passwords and two markers (the run's, and a different well-formed one) under `set +x` with their `::add-mask::` lines as its first output, writes them to files readable only by the job's user in the job's temporary directory, starts the official `postgres` image at 17.11 pinned by digest with `docker run` on `127.0.0.1:5433` with `-c track_commit_timestamp=on` (the superuser's password reaches the container through `POSTGRES_PASSWORD_FILE` from a read-only mount), waits with `pg_isready` within 60 seconds, creates the non-superuser role and its database inside the container over its Unix socket and sets the database's comment to `glow-ordering-proof:` and the run's marker, from the same file, so that nothing prints the statement. Before the migrations, one step runs `migrate` with the other marker and requires a non-zero exit and the refusal line, and, as the superuser inside the container in the proof's database, counts `pg_class` rows per schema before and after: every count unchanged, `pg_toast` included; zero outside `information_schema` and the schemas for which `starts_with(nspname, 'pg_')` is true; and no `django_migrations` (DM-10 2.3, in DM-11's words). It prints both tables and no name of a role, password or marker. P06.2 adds a step that shows `dbshell` refused before the migrations, and one after the run that shows a second `run` on the now-used database refused with every count unchanged. Then the job runs `migrate`, `makemigrations --check --dry-run`, `facts` and `run`, uploads the results JSON, and removes the container, its volume, the credential files and the marker files in an `if: always()` step. Each step that needs the marker reads it from the job's temporary directory into `PROOF_DB_MARKER` for its own commands, never through `$GITHUB_ENV` or a step output. The job has no `env:` of secrets, reads no `PG*` or `DATABASE_URL` name, and runs no `docker inspect`.

**Local runs are iteration, not evidence** (D4). A session may start a throwaway cluster with `docker run` under the same recipe, or from local binaries (`initdb` in a temporary directory listening only on a Unix socket or loopback, `-c track_commit_timestamp=on`), with a generated password, a non-superuser role, a new marker set as the database's comment (above), none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present, and removes it afterwards. Its PostgreSQL version may differ from CI's 17.11 and is recorded as such.

## Limits

- The evidence of record is the CI job's run on the final head. The report says which local database, if any, a session used.
- The reference design is proven here; the app's adapter is proven by its own run in the same job (P06.2 Stage A). P11A and P11B rerun DB06 and DB09 on the real target.
- The oracle judges commit order with microsecond commit timestamps; it treats equal timestamps as a violation.
- `auth_session_ref` is a stand-in; credentials, verification and the maintained session are not exercised.
- The provider is never called; the `ChatBinding` is created locally with a stand-in channel reference.
- The stress run's overlaps are measured from database-clock intervals, not from observed lock waits; the forced cases observe the waits. (Corrected in P06.DB-C1; the exact-head review's F1.) The first run of record (Foundation run 36520940933) established the overlap count of its first race only, `race.block_by_low`'s 200 of 200; the other eleven races' counts were not established, and `race.racing_duplicates`'s own overlap was never measured. The corrected per-race counts are in the evidence record, "P06.DB-C1 corrections".
- The stress run does not guarantee each commit order. The send locks its session row last, and a sign-out or an expiry locks only that row, so in those two races the send rarely commits first, and in some runs never; against the opposing writers it commits first at most once in 200. That order rests on the forced cases `sequential_send_first` and `send_holds`. The floors count iterations and overlaps, not orders. (Added after C1's exact-head review, R1.)
- The marker ties the proof to the database created for the run: a server reached by mistake on loopback or a socket does not carry its comment, and every connection the proof opens through Django refuses it before any statement but the connection's session settings. Each new connection logs one line, `database marker verified on a new connection`, with its backend pid and thread, so a run's log shows when each connection was opened. (Added in P06.DB-C2, after Codex's CX3.)
- `dbshell` is refused under the proof's settings, before any connection (P06.2; DM-12). Before P06.2 it was not checked (C2's exact-head review, F1).
- One run per database: the run tags are fixed, so `run` refuses a database whose proof tables or app accounts already hold rows (P06.2; C1's exact-head review, R2). The CI job starts a new database in every run, and a step shows the second run refused.
- The oracle checks who sent (O9, P06.2; Codex's CX1), with two planted controls (another member, a non-member) on both subjects.
- Expiry is checked at a time read after the locks (D5, 5.2), not at commit; O5 is narrowed to match, and the boundary is forced by `named.session_expires_after_check` (P06.2; Codex's CX2; the P06.2 brief's D4).
- The adapter's evidence is its own rows. Its commit times are PostgreSQL's, but a submission's session and its transaction's start come from the harness's call row, written after the call from what the adapter returned; O0 checks that every revocation the database holds has its witness.
- The delivery phase runs one deliverer in-process against an in-memory fixture provider; it shows idempotency, ordering and error mapping, not a provider's real behavior (Stage B) or a deployed worker (P11).
- The oracle cannot see a stale client version: the send stores the locked match's version, not the request's. The named case `stale_contact_version` and the `no_version_check` control catch a missing version check through the case's expected refusal.
- The negative controls are broken variants of this package's own reference design; they show what this suite detects, not every way an adapter could be wrong.

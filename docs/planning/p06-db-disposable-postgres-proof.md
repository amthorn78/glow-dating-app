# P06.DB — Early disposable-PostgreSQL proof

- **Status:** brief revision 1, 29 September 2026, by App Manager 5. Its design choices go to the Dev Manager first (DM-08), because P06.DB adds a dependency, a database service in CI and a transaction design that P06.2 builds on (the [charter](dev-manager.md): new components, services or significant dependencies, and integration strategy). No prompt is written until the Dev Manager answers.
- **Authority:** Nathan, 25 September 2026 (OD-17): *"Yes, I approve the plan change. Use a disposable PostgreSQL instance in CI to prove send-versus-block ordering and sign-in against real database behavior before P06.2. It must have no connection to a shared or production database. Record what the proof tested and its result, then dispose of the database."* PF01 §6 ("Early disposable-PostgreSQL proof") and §8 place it after P06.1 and before P06.2. Nathan's direction of 29 September (OD-37): *"I want to move forward with dev"*.
- **Why now:** P06.1 closed on 29 September, when PR27 merged at `47db18d`. P06.2 designs the server-side send path, and that path rests on the ordering this item proves.

## What P06.DB proves

Against a real PostgreSQL 17 database that exists only inside one CI job (17.11 is the version the 23 September [database audit](database-audit-2026-09-23.md) found on the target service):

1. **Setup, not acceptance.** From an empty database, Django's maintained `auth` and `contenttypes` migrations and the reviewed `glow_persistence` migrations `0001` and `0002` apply. The proof records the applied ledger. This is setup, not DB01's acceptance (PF01 §6).
2. **Send versus block ordering: DB06, partially.** One defined transaction boundary orders a send authorization for a match against every revocation of that contact: a block by either member, an unmatch, a suspension of either account and a deletion of either account. A send authorization is a `MessageSubmission` row for the match's `ChatBinding`; the proof creates the binding locally and calls no provider.
   - After the revocation commits, no new send authorization commits.
   - An authorization that committed first is recorded as such, and the revocation still takes effect.
   - A send carrying a stale contact version is refused.
   - An identical retry (same actor, same idempotency key) returns the first result and never creates a second authorization; the same key with a different request is refused.
   - Each interleaving is forced deterministically on two real connections: the send commits first; the revocation commits first; each arrives while the other holds its locks. A randomized stress run then repeats each race many times with zero violations.
   - **Negative controls:** each guarantee has a deliberately broken variant (for example, no row lock, or no version check) that the same test shows failing. A race test that has never been seen to fail proves nothing.
3. **Minimal sign-in: DB09, partially.** Maintained Django authentication persistence creates a user and its `AppAccount`. A sign-in records an `AccountSession` bound to the account's `session_epoch`. Sign-out revokes that session; suspension and deletion revoke every session of the account, on every device, through the epoch. A revoked or expired session cannot authorize a send.
4. **Evidence and disposal.** The job records the PostgreSQL version and image digest, the applied ledger, every case with its result, and the stress counts. The database is destroyed with the job.

What it does not prove: P11A and P11B still rerun DB06 and DB09 on the real target; DB06's provider half (channel membership, and a send the provider has already accepted) stays with P06.2 and P11; DB01, the move-out path and every other deferred case stay with P11; no app route, served feature or provider call changes.

## Proposed design (for the Dev Manager, DM-08)

- **D1. Where the proof lives.** An isolated package, `proofs/postgres-ordering/`, like `proofs/stream-chat/`: its own Django settings module, hash-pinned locks and offline tests, used by one CI job.
  - The API's runtime settings, configuration guards and fixture mode do not change. The API still refuses every connection name and keeps its dummy database backend, and no app code path gains a database.
  - The proof imports `glow_persistence`'s models and migrations without changing them. If a reviewed migration fails on real PostgreSQL, the session stops and reports it as a finding; changing migrations is outside P06.DB.
  - The proof's settings never import the API's settings. They accept only a loopback host, and refuse to start if `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY`, any other name on the API's forbidden connection list, or any `PG*` name is present (libpq reads `PG*` names as defaults).
  - The send-authorization and revocation functions under proof live in the package as the reference design. P06.2 carries the proven design into the app's persistence adapter; P11A reruns DB06 on the real target.
- **D2. Dependencies.** `psycopg` 3 (the driver Django 5.2 supports), pinned by hash in the proof's own lock. No allauth: the minimal sign-in uses `django.contrib.auth` and the app's `AccountSession`, and allauth's adoption stays with the item that serves authentication. The session's `auth_session_ref` is a random, non-secret identifier, never a cookie or token, as the [data model](../architecture/data-model.md) requires.
- **D3. The CI job.** A new Foundation job, "Database proof checks", runs on every full-scope change like the other application jobs, and the gate requires it.
  - PostgreSQL is started inside the job with `docker run`, from an image pinned by digest, bound to `127.0.0.1` only, with a password generated in the job (for example with `openssl rand`) and never stored, printed or set as a repository secret. That meets PF01's "CI-generated credentials". A `services:` container starts before any step runs, so its password would have to be written into the workflow or held as a repository secret.
  - The password reaches the proof through a file only the job's user can read, or a proof-specific variable set only on the steps that need it; never a `PG*` or `DATABASE_URL` name. The job masks it (`::add-mask::`) as soon as it is generated.
  - An `if: always()` step removes the container. The job needs no repository secret (OD-20's CI rule) and reads no inherited connection name.
- **D4. Local runs.** The implementation session may start the same disposable container in its own sandbox, with a generated password, bound to loopback and removed afterwards, if Docker works there; otherwise it iterates through CI. OD-17 names CI, so the Dev Manager says whether a local disposable instance is within it or needs Nathan. Either way the session connects to no other database, and `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` and every `PG*` name must be absent.
- **D5. The transaction design.** The recommendation, for the Dev Manager to challenge:
  - `READ COMMITTED`, with the send and every revocation taking row locks with `SELECT ... FOR UPDATE` in one fixed order: the lower account, the higher account, then the match. The fixed order prevents deadlocks.
  - The send checks, under those locks: the match is active; no active block exists in either direction; both accounts are active; the session is valid, unexpired and at its account's current epoch; and the contact version equals the one the client sent.
  - A revocation changes the relevant state and increments the contact version (and the block or session revision where it applies) in the same transaction.
  - A block that does not exist yet has no row to lock. The account locks, which every writer takes, and each account's `blocks_version` are what order a first block against a send, as the P11 plan's DB06 row asks: persistent directional or account revisions, not only locks on existing block rows.
  - The alternative is `SERIALIZABLE` with bounded retries; the proof can run both and record the difference.
- **D6. What "partially" means.** On success the P11 acceptance plan marks DB06 and DB09 "partially evidenced in CI (P06.DB)". Nothing else changes status.

## Brief

- **Work ID and title:** P06.DB, the early disposable-PostgreSQL proof (OD-17; PF01 §6 and §8).
- **Owner and manager:** Nathan Amthor; App Manager 5.
- **Starting commit and manager branch:** `main` at `47db18d` (PR27's merge); manager branch `claude/magical-wozniak-yfmmx2`, restarted from `main`. The prompt names its start SHA.
- **Environment:** `Glow App - No Stream` (OD-36). No Stream call, HDE, Railway or provider.
- **Owned paths (writable):**
  - `proofs/postgres-ordering/**` (new);
  - `.github/workflows/foundation.yml`: the one new job and the gate's list of required jobs. That is full scope, under the CI policy's workflow rule;
  - the evidence record, `docs/testing/evidence/<date>-p06-db-disposable-postgres-proof.md` (new).
- **Manager-owned paths:** this brief and the rest of `docs/planning/`, `docs/continuity/`, `docs/ephemeral/`, `docs/pf-canon/`, `docs/testing/p11-deferred-acceptance.md`, root `AGENTS.md` and `CLAUDE.md`, and Notion.
- **Exclusions:** every other path, including `services/` (no app code, settings, guards or migrations), `apps/`, `packages/`, `scripts/`, other workflow jobs, `Dockerfile`, `.dockerignore`, `.gitignore`, the `.env.example` files and any `.claude/` path. No database other than the disposable one the job, or the session under D4, starts.
- **Dependencies and inputs:** P06.1 merged; the reviewed migrations on `main`; Django 5.2.17 as pinned in `services/api`; the Dev Manager's answer to DM-08.
- **Acceptance checks** (exact commands go in the prompt after DM-08):
  1. `git diff --check <START_SHA> HEAD` is clean, and only owned paths changed.
  2. The trusted-base classification reports full scope.
  3. Dependencies install from hash-pinned locks with `pip install --require-hashes`, and `pip check` passes.
  4. The offline checks pass without a database: unit tests of the case plan and result recording, Ruff 0.16.8 and mypy 2.3.1 as pinned in `services/api/requirements-dev.lock`.
  5. The new CI job passes on the final head: the migrations apply from zero; every ordering and sign-in case passes; the stress run shows zero violations; every negative control fails as intended; the container is removed; the log prints a redacted results table.
  6. The gate requires the new job, and the other jobs are unchanged.
- **Classification expectation:** full scope.
- **Evidence home:** the new evidence record above; the P11 acceptance plan's DB06 and DB09 marks after the manager's verification.
- **Report format:** branch, SHAs, tree, changed paths, every check with its exact result, the CI run IDs, the PostgreSQL version and image digest, the applied ledger, each case, the stress counts and the negative controls, deviations, open questions and limits.
- **Review plan:** one implementation session, then an exact-head code and security review of its final head, offline, reading the job's logs. Corrections, if any, before the merge. The Dev Manager reads the prompt only if it authorizes credential use or live provider actions; D3's generated password and D4 are for DM-08 to classify.

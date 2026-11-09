# SV1 prompt — the identity slice: maintained sign-in and the mail adapter, proven on disposable PostgreSQL

- **Owner:** App Manager 10. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 9 November 2026.**
- **Durable brief:** [SV1 — The identity slice](../planning/sv1-identity.md), revision 3.
- **Where the result goes:**
  - the session's changes in `services/api`, `proofs/postgres-ordering`, the Database proof checks job and the three architecture and P11 texts the brief names, and its record, `docs/testing/evidence/<date>-sv1-identity.md`, on its own branch;
  - the run of record: the Foundation run on its last code commit, with the identity phase;
  - the manager adds its verification to the record and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at max.** Effort score 3.54 (confidence 0.67); rung probabilities low 0.00, medium 0.01, high 0.10, extra high 0.25, max 0.62, ultracode 0.02. Model probabilities Fable 5.1 0.24, Opus 5.5 0.75, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.67). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.002, Fable 5.1 at high 0.024, Fable 5.1 at extra high 0.060, Fable 5.1 at max 0.149, Fable 5.1 at ultracode 0.005, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.007, Opus 5.5 at high 0.075, Opus 5.5 at extra high 0.188, Opus 5.5 at max 0.465, Opus 5.5 at ultracode 0.015, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.001, Sonnet 5.5 at extra high 0.003, Sonnet 5.5 at max 0.006, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Flags: boundary between extra high and max. Sent 2026-11-09T05:06:14Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs.
  - The brief's revision 3 applies DM-45's and DM-46's conditions as written. DM-46 says they need no read before the prompt (DM-46 section 1), and the prompt needs none of its own (DM-45 item 14).
  - This prompt authorizes no credential use and no live provider action. The JWT signing key, the identity settings' `SECRET_KEY` and the database password are generated for one run and destroyed with it.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Then, in order:
  - the manager's verification;
  - the PR and Codex's review of its head;
  - an exact-head code and security review with a written threat model (the brief's review plan);
  - the Dev Manager's read of the CI policy's paragraph and the two mapping texts, before the merge (DM-45 14.1).
- **Deletion condition:** prune after SV1's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **implementation session for SV1**, the identity slice, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What SV1 is.** You build Glow's server-side sign-in on maintained code. It is proven on a disposable PostgreSQL in CI and kept sealed from the served runtime until P11:
- django-allauth headless, `app` client only, with the JWT strategy;
- verification and password reset by code, never by link;
- every session and account transition through `glow_chat`'s reviewed operations, plus F01's `verified` transition, which SV1 adds;
- revocation at both layers, Glow's and allauth's;
- one actor class for the later slices, and the member's own `AccountAccess`;
- a mail adapter with a fixture backend;
- the age-state seam;
- an identity suite on a second disposable database in the Database proof checks job.

There is no mail provider, deployed URL, real member or stored credential.

**The brief, `docs/planning/sv1-identity.md`, revision 3, is the specification:** its Outcome items 1 to 10, D1 to D15 and its acceptance checks.
- Much of its text is the Dev Manager's words (DM-45 and DM-46), checked against allauth 65.21.1's and Django 5.2.17's source. Follow them exactly.
- Where this prompt summarizes the brief, the brief wins.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 10. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only the brief's "Owned paths (the session)";
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule.** Stop and report, with no further change, if any of these holds:
  - **an owned path:** the work needs a path outside the owned paths. That includes:
    - `services/api/glow_api/` (the seal);
    - `services/api/glow_chat/`: you call its operations, never change them;
    - the runtime scope's `requirements.in` and `requirements.lock`;
    - `packages/` (D14);
    - `apps/`;
    - any other workflow job;
    - the `Dockerfile`;
    - an environment template;
  - **the dependency set** (D12): the new packages would be anything but `django-allauth`, `cryptography` and what `cryptography` requires on CPython 3.12 (today `cffi` and `pycparser`), or PyJWT would move from 2.15.0;
  - **the installed release differs from the brief.** allauth at its pinned release does something differently from what the brief states, D5's facts above all. Those facts are:
    - `UserSession`'s non-derived primary key;
    - `end()` deleting the Django session;
    - the session key's reach;
    - the session-list route.

    Report what the source shows, with file and line;
  - **a design change:** a `glow_chat` operation would need to behave differently, `AUTH_USER_MODEL` would change, or the contract would change;
  - **the seal:** the served runtime would import `glow_identity`, `allauth`, `jwt` or `cryptography`;
  - **the timeout:** the Database proof checks job cannot stay within its 30-minute timeout.

  If the configured specification cannot be generated (D14, 9.2), that is not a stop: record why, as the brief says.
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished. A newer push cancels the earlier run's application jobs, and the run of record is lost. Push your records commit only after the run of record has finished.
- **Network:**
  - PyPI, for `pip install --require-hashes` and for reading `django-allauth`'s release page and its dependencies' metadata;
  - `docs.allauth.org`, for the pinned release's documentation;
  - Docker Hub, only to pull the PostgreSQL image the CI job pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`) for a local run (below).

  A page you cannot reach is named as unread, never filled from memory.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions):
  - a throwaway PostgreSQL in Docker, from the CI job's pinned image, on loopback only;
  - a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present;
  - removed afterwards.

  Local passes are "iteration, not evidence"; the run of record is CI's. If Docker or the image is unavailable, iterate through CI and say so.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, password, code, token, session key or signing key, in any form. The test accounts, emails and passwords you make are synthetic; make them obviously so (`@example.invalid` addresses);
  - call any provider, send any real email, or run any command in `proofs/stream-chat/`;
  - connect to any database but a throwaway one you started under D4's conditions; run `migrate` or `makemigrations` only through the proof's own commands against such a database or under the static registry's dummy settings;
  - connect to HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script;
  - weaken or delete a test to make the suite pass.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` or `PG*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG)'` prints names only. If any is present, stop and report.
3. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
4. **The toolchain:** CPython 3.12.14 as `python3.12` (`services/api/.python-version`); Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, first on PATH. Record `python3.12 --version`, `node --version`, `npm --version` and `docker --version`.
5. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API). The proxy and CA variables pass by reference, never printed (`docs/operations/local-development.md`).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git merge-base --is-ancestor 8d2de724091f2a7127d207fbc557ea1ced57f690 HEAD && echo "PR41 present"   # PR41's head; main's merge da92f1f has the same tree. Must print "PR41 present"
git diff --name-only da92f1fb71da6c93fae8a747f62c718800a12ae9 HEAD | grep -v -E '\.md$'            # against main: must print nothing
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/api proofs/postgres-ordering .github 'docs/testing/evidence/*sv1-identity*' docs/architecture docs/testing/p11-deferred-acceptance.md   # must print nothing
test -e services/api/glow_identity && echo "glow_identity exists"                                   # must print nothing
grep -c -i 'django-allauth' services/api/requirements-dev.lock proofs/postgres-ordering/requirements-dev.lock   # must print 0 for each
ls services/api/glow_persistence/migrations | grep -E '^[0-9]{4}_'                                  # must list 0001 to 0003 only
```

If a check fails, stop and report. The prompt is stale if:
- `<START_SHA>` is not on the live manager branch;
- the live branch has changed an owned path since it;
- or the brief's "Sessions" already records an implementation session.

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`; `proofs/postgres-ordering/README.md`;
- **the brief,** revision 3, whole;
- **DM-45's and DM-46's reports,** whole: `docs/continuity/dev-manager/reviews/2026-11-09-dm-45-sv1-brief.md` and `…/2026-11-09-dm-46-sv1-brief-revision-2.md`. Their "Tried" lists are cases your tests should cover;
- **F01 and `AccountAccess`:** `packages/contracts/production/flows-v1.json` and `gapp-api-v1.schema.json`; `docs/architecture/production-contracts.md`, "Maintained authentication reference and app mapping";
- **the data model:** `docs/architecture/data-model.md`, its "Maintained authentication mapping", unit-of-work table and outbox event table;
- **the code you build beside** (read only):
  - `services/api/glow_chat/contact.py`: `_run`, `open_session`, `sign_out`, `expire_session`, `_end_session`, `suspend`, `delete`, `_revoke_account`;
  - `services/api/glow_persistence/models.py`: `AppAccount`, `AccountSession`;
  - `services/api/tests/test_chat_sealed_runtime.py`;
  - `services/api/glow_domain/identity.py`;
- **the proof:** `proofs/postgres-ordering` (its settings, `environment`, `marker`, the suites' entry points and its locks), and the Database proof checks job in `.github/workflows/foundation.yml`, whole;
- the P06.DB brief's D1 to D6, and the P11 plan's DB09 and "From SV1";
- `docs/operations/ci-and-branch-policy.md`'s Database proof checks paragraph (manager-owned: read it, do not change it).

## 3. What to do

1. **Pin and read the release.**
   - Pin `django-allauth[headless]` at the latest 65.x on PyPI when you start, with its release notes read for security entries (D12), in the development scope and in the proof's lock, hash-locked.
   - Record the exact transitive set and each package's licence from its metadata.
   - Then **read the installed source** for every fact the brief takes from 65.21.1 (D2, D3, D5, D6, D8). If you pin a later release, re-check each fact at that release. Record each with its file and line, and apply the stop rule to any difference.
2. **Outcome items 1 to 10,** in the brief's order, each with its tests. Every test comes with its reversal (D15): a temporary edit that must make the test fail, run and then undone. Record the edit and the failing output. Make at least these reversals, each named in the record:
   - **D2:**
     - stateful validation off: logout no longer ends the access token;
     - the replay subclass removed: a replayed refresh token no longer ends its session;
     - the subclass reading `sid` before allauth's checks: a forged token ends a session;
     - `set_expiry` not called: allauth's refresh outlives `expires_at`;
   - **D3:**
     - `ACCOUNT_EMAIL_UNKNOWN_ACCOUNTS` back to its default: the reset for an unknown address raises;
     - Glow's account-already-exists message removed: the taken-address sign-up raises;
   - **D4 and D6:**
     - the `AppAccount` created outside `save_user`'s transaction;
     - the `verified` transition without its lock or its refusal;
     - a `glow_chat` call inside `transaction.atomic()`, refused by the revocation service;
     - the sign-in hook not ending allauth's session when `open_session` refuses;
     - the second layer failing, with the error and the repeat;
     - `ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE` off;
     - Glow's `USERSESSIONS_ADAPTER` removed: the session list's `DELETE` leaves the `AccountSession` valid and writes no `session_revoked` (N1);
   - **D5 and D7:**
     - the actor class reading `X-Session-Token` instead of the token's own `sid`;
     - an account not `active`, or a session at an old epoch, accepted;
   - **D8:** a notice event not sent;
   - **D11:** the runtime importing `glow_identity`: the sealed-runtime test fails;
   - **the log capture:** a password, code, token or key logged in one path.
3. **The configured specification** (D14, 9.2). In a scratch environment outside the checkout, with `django-allauth[headless-spec]` at the pinned release and SV1's settings, generate the configured headless specification once. Record its SHA-256 and its list of paths. Commit nothing from that environment, and add `headless-spec` to no lock.
4. **The local checks:**
   - **API,** in `services/api`: `python3.12 -m venv .venv`, `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`; then, with `GLOW_ENV=test`: `manage.py check`, `manage.py test tests --verbosity 2`, `smoke.py`, `ruff check .`, `ruff format --check .`, `mypy` and `python -m glow_persistence.static_check`;
   - **the proof,** in `proofs/postgres-ordering`: its venv and hash-locked install, its offline tests under `env -i`, Ruff and mypy;
   - **a local database run,** if Docker allows it under D4's conditions: iteration, not evidence.
5. **The run of record.**
   - Commit and push your code. The Foundation workflow runs on your branch's pushes. Wait for the run to finish (the push rule above).
   - Read it with your GitHub tools:
     - every job's conclusion and the gate's line (`Application checks passed`);
     - the API test count;
     - the ordering suite's and the identity suite's results;
     - the identity phase's duration against the job's 30-minute timeout;
     - whether a toolchain retry fired;
     - that no secret appears in the job's log.
   - The run of record is the one on your last code commit. If it fails, stop and report the failing job and its log lines. Do not re-run it, and push no fix without saying so in the report.
6. **The records** the brief owns: rewrite the data model's "Maintained authentication mapping" and the contract's "Maintained authentication reference and app mapping" as built, with the pinned release. Add DB09's partial evidence to the P11 plan. Change no other section of those files.

## 4. The record

Write `docs/testing/evidence/<today's date>-sv1-identity.md`:
- the start gate's results, the environment check (names only) and the toolchain versions;
- the pinned release, the transitive set and the licences; each fact read from the installed source, with file and line;
- a table with one row per Outcome item and acceptance check: the files, the test, the reversal and its failing output;
- the configured specification's SHA-256 and paths, or why it could not be generated;
- **the threat model's inputs:**
  - every endpoint and its refusals;
  - every token, code and key, with where it lives and how it ends;
  - every revocation path, at both layers;
  - each with its test;
- every command you ran, with its result line; local database runs listed as iteration, not evidence;
- the run of record's ID, each job's result, the counts, the identity phase's duration, and whether a retry fired;
- what you could not run, and why.

Commit each logical step with a clear message ending in the session's attribution lines. Push your records commit only after the run of record has finished. Confirm that `git status` is clean, and that `git diff --name-only <START_SHA> HEAD` lists only your owned paths.

## 5. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch, your code head and records head;
- the start gate's and the environment check's results;
- the pinned release, its transitive set and licences, and every fact you read from its source;
- for each Outcome item: what changed, its tests, and each reversal's result;
- the configured specification's result;
- each local check's result, and whether a local database run was used;
- the run of record: its ID, every job, the gate's line, the counts, the identity phase's duration and whether a retry fired;
- anything that met the stop rule, every deviation from the brief, and what you could not run.

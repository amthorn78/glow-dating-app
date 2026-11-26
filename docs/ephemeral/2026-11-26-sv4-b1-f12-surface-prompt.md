# SV4 B1 prompt — F12's surface: the models, the ORM persistence and three sealed routes

- **Owner:** App Manager 13. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 26 November 2026.**
- **Durable brief:** [SV4 — the chat and notifications slice](../planning/sv4-chat-notifications.md), revision 12, its section "Stage B" (D16 to D20, D29's B1 cases, D30, D31; B1's owned paths, completed in this prompt).
- **Where the result goes:**
  - the session's code on its own branch, and its section "B1" in the SV4 record (`docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`);
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification to the record, and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 3.30 (confidence 0.53); rung probabilities low 0.00, medium 0.02, high 0.19, extra high 0.25, max 0.52, ultracode 0.02. Model probabilities Fable 5.1 0.26, Opus 5.5 0.73, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.64). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.005, Fable 5.1 at high 0.049, Fable 5.1 at extra high 0.065, Fable 5.1 at max 0.135, Fable 5.1 at ultracode 0.005, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.015, Opus 5.5 at high 0.139, Opus 5.5 at extra high 0.182, Opus 5.5 at max 0.380, Opus 5.5 at ultracode 0.015, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.002, Sonnet 5.5 at extra high 0.003, Sonnet 5.5 at max 0.005, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-26T19:00:26Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs: Stage B's design was read as DM-101 and its conditions are applied as given in revision 12, and this prompt authorizes no credential use and no live provider action. Dev Manager 7 reads B1 before its pull request merges (D-07), with any governing Markdown B1 changes.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and none may be present. `amthorn78/glow-docs` is attached, read-only; this work needs nothing from it (OD-74).
- **It runs alone** (OD-29). Then, in order: the manager's verification; a new pull request from the manager branch, its run and Codex's review; B1's exact-head code and security review, with its threat model; any correction under D-07; Dev Manager 7's pre-merge read; the merge. B2's prompt follows B1's merge.
- **Deletion condition:** prune after B1's pull request merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch.

---

You are the **implementation session for SV4 B1**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What B1 is.** The first of SV4 Stage B's two sessions: F12's surface (devices and notification settings), stored and served, sealed until integration. B1 covers:
- **D16's seal for B1:** the token store and the push transport keep their fixtures only, reached through factories that only the proof's chat settings name (AM1);
- **D17, the models and migration `0014`:** `DeviceRegistration` one row per account and installation, `NotificationSettings` in the contract's names, `IdempotencyRecord`'s new outcome codes, the ledger and the pending discards as tables, the custody rules as database constraints;
- **D18, the ORM persistence:** a persistence port in `glow_domain/notifications.py`, with its in-memory service as the port's fixture, and an ORM adapter in a new app, `services/api/glow_notifications/`;
- **D19, F12's three routes:** `GET api/v1/notifications`, `POST api/v1/notifications/device`, `POST api/v1/notifications/settings`, with the installation from the `Glow-Installation-Id` header;
- **D20, the contract's documentation:** no schema change; "F12 on the server" in `production-contracts.md`;
- **D29's B1 cases,** in the chat suite.

B1 writes no trigger, deliverer, sweep or G-04 read: those are B2's (D21 to D27). There is no provider call, deployed URL, real member, HDE call, real token or stored credential. The runtime stays sealed: no route is added to the runtime's URL configuration, and the production catalog's `paths` stay empty.

**The brief, revision 12, is the specification:** the section "Stage B", D16 to D20, D29 (B1), D30, D31, the owned paths, the exclusions, the acceptance checks and the review plan. Much of its text is the Dev Manager's words (DM-101, AM1 to AM16). Follow them exactly. Where this prompt summarizes the brief, the brief wins. Where it adds to the brief, it says so.

**What came before.**
- **SV4 Stage A merged:** A0 with PR57 (`499ccbb`), A1 with PR58 (`43e794a`), A2 with A2-C1 with PR59 (`988a36a`, 26 November 2026): chat's sealed routes (`glow_chat/views.py`), the match list, and the chat suite on `glow_chat_proof` in its own job, with its scan and row-lock record. `main`'s push run 45866641384 passed all twelve jobs.
- **P06.3** built F12 at fixture scope (`services/api/glow_domain/notifications.py`, `notification_fixtures.py`, `tests/test_notifications.py`): the intents, the transitions, the token's custody, the versions and the composer, in memory and guarded to development and test. Its brief's D9 lists the six field mismatches D17 settles.
- **DM-101** (Dev Manager 7, `60325b1`) approved Stage B's design with AM1 to AM16, applied in revision 12.
- **`main` is at `988a36a`.** The manager branch has changed only Markdown since.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 13. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only B1's owned paths:
    - `services/api/glow_notifications/` (new: its `__init__.py`, `apps.py` and `conf.py` on the slices' pattern, the ORM adapter, the contract mapping, the views, the URLs and the fixtures' factory hooks);
    - `services/api/glow_domain/notifications.py` and `notification_fixtures.py` (the port; the in-memory service as its fixture);
    - `services/api/glow_persistence/models.py` (`DeviceRegistration`, `NotificationSettings`, `IdempotencyRecord`'s outcome codes and constraint, the two new tables) and one new migration, `services/api/glow_persistence/migrations/0014_*.py`, generated by `makemigrations`;
    - `services/api/glow_profiles/idempotency.py`, only to let `store` take an outcome code, with `committed` as its default and every existing caller unchanged (or none, if you write B1's records in the adapter with `digest` and `decide`; record which);
    - `services/api/tests/` (B1's new tests: routes, persistence, mapping and seal; `tests/test_notifications.py`; and the earlier tests listed below);
    - the chat suite: `proofs/postgres-ordering/glow_ordering_proof/chat_cases.py`, `chat_support.py`, `chat_settings.py`, `chat_urls.py`, `chat_scan.py`, `chat_suite.py`, and `row_locks.py` only if its lists change; `proofs/postgres-ordering/tests/` (the chat suite's offline tests, the tests that pin its settings and URL modules, and the earlier tests listed below); `proofs/postgres-ordering/README.md` (the chat suite's paragraph);
    - `.github/workflows/foundation.yml`, only the chat job's credentials step and its scan's inputs, and only if the synthetic push tokens need a secret file the scan reads (below); with it, `docs/operations/ci-and-branch-policy.md`'s chat-job lines (13 and 15) only, which are governing Markdown;
    - `docs/architecture/data-model.md` (the device and notification lines, and A2R-13's stale chat lines) and `docs/architecture/production-contracts.md` ("F12 on the server");
    - each file a follow-up below names, only for that follow-up, and only if you change the file for your own work;
    - the record, section "B1" only;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: use the GitHub tools where your session has them, otherwise `gh api` REST `GET` calls, and say in the report which you used. No pull request, comment, review, thread resolution, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule.** Stop and report, with no further change, if any of these holds:
  - **an owned path:** the work needs a path outside the list above, including `services/api/glow_api/`, anything in `glow_chat/` (A2's routes and the chat writers stay as they are), `glow_discovery/`, `glow_identity/`, `packages/contracts/` (no schema change, D20), `apps/mobile/`, `scripts/`, an environment template or a `requirements` file;
  - **a served route:** the work would add a route to the runtime's URL configuration, a path to the production catalog, or a module the runtime's settings or WSGI application import (D31's seal);
  - **a design point:** D17's shape or constraints, D18's lock order (the account row, then the requesting session's row `FOR SHARE`, then the registrations), its custody rule (`put` before the transaction; an unsaved reference to the pending discards), the digest's binding (the intent, the token and the installation), D19's routes, header or codes, or the bound (D25: 10 active registrations, `state_conflict` beyond it) would have to change;
  - **a token:** a push token is found in any row, log line, answer, exception or receipt, or a reference anywhere AM4 does not allow;
  - **a dependency:** a new Python or npm package, or a changed pin (D13);
  - **the timeout:** the chat job, or any other job, no longer fits its `timeout-minutes`;
  - **an earlier test:** a test changes in any way other than gaining B1's entry in a list it pins, or as a follow-up below names, every earlier assertion kept; or a test would be weakened or deleted;
  - **a provider:** the token store or the transport would need anything but its fixture, reached through the proof's factories.
  - In each case, report it; do not narrow the brief's words to pass it. A reversal's temporary edit is allowed, and must be undone.
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished. A newer push cancels the earlier run's application jobs, and the run of record is lost. Push your records commit only after the run of record has finished. The workflow runs on pushes to `claude/**` and `ccr-**`; if your branch is named otherwise, say so in the report, since no run starts.
  - **If GitHub never starts the run** (it stays `queued` with no jobs for 30 minutes), do not re-run it, dispatch it, push an empty commit, or ask anyone to re-run it (OD-58). Record it, push your records commit, and report.
  - **If the run fails,** stop and report the failing job and its log lines. Do not re-run it, and push no fix without saying so in the report.
- **Network:** PyPI and the npm registry, for `pip install --require-hashes` and `npm ci --ignore-scripts` from the existing locks only; Docker Hub, only to pull the PostgreSQL image the workflow pins, for a local run (below); GitHub, for your pushes and reads. The environment does not enforce this; you do. A page you cannot reach is named as unread, never filled from memory.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions): a throwaway PostgreSQL in Docker, from the pinned image, on loopback only; a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present; removed afterwards. Migrations reach that database only through the proof's own commands; never run `manage.py migrate` yourself. Local passes are "iteration, not evidence"; the run of record is CI's.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, password, marker, token or key, in any form;
  - read, print or use the value of any `AWS_*` variable, or name one in a command (section 1);
  - call any provider or HDE; connect to any database but a throwaway one you started under D4's conditions; connect to Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script in your own environment;
  - weaken or delete a test to make the suite pass.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:** `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_|RAILWAY_)'` prints names only. If any is present, stop and report.
3. **AWS and GitHub token names may be present** (OD-76); record which, by name only, and never read them.
4. **The toolchain:** CPython 3.12.14 as `python3.12`; Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, first on PATH. Record `python3.12 --version`, `node --version`, `npm --version` and `docker --version`.
5. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`docs/operations/local-development.md`).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git merge-base --is-ancestor <START_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git merge-base --is-ancestor 988a36a1fe4bc7b654a07e565e15fe721dcf3520 HEAD && echo "PR59's merge present"
git diff --quiet 988a36a1fe4bc7b654a07e565e15fe721dcf3520 HEAD -- . ':!*.md' && echo "main's code"
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/api proofs packages apps .github docs/operations/ci-and-branch-policy.md docs/architecture docs/planning/sv4-chat-notifications.md   # must print nothing
grep -c '^## B1' docs/testing/evidence/2026-11-19-sv4-chat-notifications.md   # must print 0
test ! -e services/api/glow_notifications && echo "no glow_notifications yet"
ls services/api/glow_persistence/migrations | grep -c '^0014_'                # must print 0
```

If a check fails, stop and report. The prompt is stale if its commit is not on the live branch, the live branch has changed an owned path or the brief since it, or B1's record, app or migration already exists.

**Then read, completely:**
- **The instructions:** root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`; `proofs/postgres-ordering/README.md`; `docs/operations/ci-and-branch-policy.md`, the database proof jobs' paragraphs.
- **The brief,** revision 12: the section "Stage B" whole, and Stage A's D2, D8, D13 to D15 that it builds on.
- **The Dev Manager's report** DM-101 (`docs/continuity/dev-manager/reviews/2026-11-26-dm-101-sv4-stage-b-brief.md`), whole; DM-99 (`2026-11-26-dm-99-sv4-a2-c1-design.md`), its AK2 (the mapping's completeness test).
- **P06.3's brief** (`docs/planning/p06-3-notifications.md`), "Outcome" and D1 to D9, and its record's "Exact-head review of P06.3".
- **The SV4 record's** "A2", "A2-C1" and their reviews' "Limits and deviations" and dispositions.
- **The carried-items file's** "Carried to SV4".
- **The code you build on,** whole: `glow_domain/notifications.py`, `notification_fixtures.py` and `tests/test_notifications.py`; the models (`Record`, `AccountSession`, `AppAccount`, `DeviceRegistration`, `NotificationSettings`, `IdempotencyRecord`); `glow_chat/contact.py`'s `_lock`, `_run` and `_end_session` (the lock helpers and the session's end, which you call nothing in but must order against); `glow_chat/views.py` and `contract.py` (A2's route pattern: `non_atomic_requests`, `JsonOnlyNegotiation`, the error mapping, `WWW-Authenticate`, the text-reader factory `GLOW_CHAT_TEXT_READER`); `glow_domain/chat_projections.py`'s `error_for`; `glow_profiles/idempotency.py`; SV1's `GlowActorAuthentication`; the chat suite's six modules and `proofs/postgres-ordering/tests/test_chat_offline.py`; `services/api/tests/test_chat_routes_offline.py` and `test_chat_routes_sealed_runtime.py`; `services/api/tests/test_model_definitions.py`; `apps/mobile/src/notifications/transport.ts`, `client.ts` and `fixture-adapter.ts` (what the app expects; you change none of them).

## 3. What to do

Build D16 (B1's part), D17 to D20 and D29's B1 cases as the brief says, with D14's reversals. In particular:

1. **The seal and the fixtures (D16, AM1).** The ORM adapter takes the token store, and any code that would take the transport, from factories that only the proof's chat settings name, as A2's history read takes its text reader. The served runtime names none, and whatever needs one refuses without it (`provider_unavailable`). The fixtures keep their own refusal outside development and test (`require_fixture_environment`).
2. **The models and migration (D17, AM2).** As D17 says: `DeviceRegistration` one row per account and installation (the pair unique; one `active` row per installation, a partial unique constraint); `token_secret_ref` nullable, present exactly while `active`, unique where present; `session` and `ended_by` (present exactly when `revoked`); `platform` removed; `NotificationSettings` with `match_notifications` and `message_notifications`, `push_enabled` removed; `IdempotencyRecord`'s outcome codes gain `register`, `rotate`, `revoke` and `settings` in its choices and `intent_result`; the ledger (D25: a row per event and installation, unique, `pending` or `sent`) and the pending discards (a reference only) as tables, which B2 fills. Each custody rule is a database constraint. One migration, `0014`, from `makemigrations`; `makemigrations --check` clean. Record the migration's operations.
3. **The persistence (D18, AM3 to AM5).**
   - **The port:** the domain keeps its pure parts (the intents' parsing, the transitions, the custody types, the versions' rules, the wording), and its in-memory service becomes the port's fixture, still guarded; `tests/test_notifications.py` keeps every assertion against the fixture.
   - **The locks:** a device or settings command locks the account row (`FOR NO KEY UPDATE`), then the requesting session's row `FOR SHARE`, then the registrations it changes by primary key. A transfer locks both accounts, the lower first, after reading the other account's identifier without a lock, and refuses (`state_conflict`) if it changed under the locks. The settings read takes the account and session rows `FOR SHARE`. Every check is read under the locks.
   - **Idempotency:** `IdempotencyRecord`, through SV2's keyed digest, binding the canonical intent, the token and the requesting installation, so a replay with another token, or the same body under the same key from another installation, is `idempotency_conflict`. The token is never stored.
   - **Custody:** the store's `put` runs before the command's transaction, never inside it; a command that does not save the new reference (a refusal, a failure or a replay) sends it to the pending discards. An old token is discarded after the commit; a failed discard waits in its table (B2's sweep retries it). A reference is held only by an active registration's row, a pending discard's row and a push request handed to the transport.
   - **Versions** stay P06.3's: a settings change advances every registration of the account in the same transaction.
   - **The bound (D25):** an account holds at most 10 active registrations; a registration beyond it is `state_conflict`. Record the constant's home.
4. **The routes (D19, AM6, AM7),** on A2's pattern: `non_atomic_requests`, JSON-only negotiation, every refusal the contract's `Error` naming a code and never a value, nothing cached, another method 405. The installation comes from `Glow-Installation-Id` (a lower-case UUID, the contract's pattern) on all three routes; a `DeviceIntent`'s `device_id` must equal it (`forbidden`). The codes are D19's, with AM6's additions; each 401, at the door or inside the locks, carries `WWW-Authenticate: Bearer`. A test proves every refusal reason the adapter can raise maps to one code (DM-99's AK2 pattern), and reads each helper's raises, not only the adapter's own (A2-C1's delta review, F2's lesson). The installation identifier is never served, logged or shown (AM7); your threat-model notes in the record say so.
5. **The documentation (D20):** "F12 on the server" in `production-contracts.md` (the routes, the header, the codes, which installation a read describes, that settings are the account's); `data-model.md`'s device and notification lines as built.
6. **The cases (D29, B1, with AM13),** in the chat suite, each with its reversal: register, rotate, revoke and register again; a transfer between accounts; each refusal D19 lists; a replay and a conflict; the settings change advancing every registration; no token in any row, log line or answer; the bound; a register that reaches its session's row while that session's sign-out holds it (held at its commit) refused once the sign-out commits; a register refused after the store took its token leaving the reference in the pending discards and in no registration; the same key and body from another installation `idempotency_conflict`; two accounts registering one new installation at once, and a transfer whose other account changes under the locks, each ending with one `active` row and a refusal for the other.
   - **The scan holds the synthetic push tokens among its secrets** (DM-101, section 11), and a case queries the rows for each token, since the scan reads only the output and the results JSON. If the tokens need a secret file the scan reads, the chat job's credentials step writes it and the scan's inputs name it, in the existing form; record the change, and the CI policy's chat-job lines (13 and 15) follow it in their existing form (governing Markdown, read by the Dev Manager before B1 merges). If the suite can derive them from a file the job already writes, record that instead and change neither.
7. **The seal (D31):** a test in the style of `test_chat_routes_sealed_runtime.py` (or that file, extended) proves the runtime's settings, URL configuration and WSGI application import nothing of `glow_notifications`, and that the database backend is the dummy one.

**Earlier tests** (D31, with AM16). Each may change only by gaining B1's entry in a list it pins, every earlier assertion kept, unless a follow-up below names it; record each, by file and test, with the entry added:
- `services/api/tests/test_notifications.py`, and its seal test (it keeps every assertion against the fixture);
- `services/api/tests/test_model_definitions.py` (the migration and model lists and counts);
- the chat suite's plan pin and case count (`proofs/postgres-ordering/tests/test_chat_offline.py`);
- the offline tests that pin the chat suite's settings and URL modules, where B1 names the fixtures' factories or its routes there;
- `row_locks.py`'s lists and their offline test, only if B1's cases lock tables they do not list;
- **your own sweep:** before any change, at your prompt's commit, grep every suite's source and tests and the API's tests for each list B1 extends (the models and migrations, the outcome codes, the installed apps and settings modules, the routes, the case and plan counts, the scan's secret files), and record what you found. A test your sweep finds is handled the same way; any other change stops you.

**Follow-ups taken if you change the file for your own work** (D30; otherwise they stay carried). Record which you took:
- **In `chat_cases.py`:** A2-C1's delta review's F1 (the two docstrings that say the list's own-account check is reached only by test data, at `list_checks` and `_account_suspended_as_test_data`: correct them to the carried entry's statement) and F4 (`reads.session_ended_in_locks_answers_as_hidden`'s docstring branch); A2's review's A2R-6 (cases 5 and 15: make the withdrawn-consent cause one a read rule ignoring it would fail, every earlier assertion kept);
- **in `test_chat_offline.py`:** A2R-7 (the first check of `test_the_cases_that_publish_hidden_run_last` made able to fail);
- **in the proof README:** the chat suite's case list, all of its cases described;
- **in `data-model.md`:** A2R-13's stale lines (no chat routes or match list); **in `test_row_locks_offline.py`:** A2R-13's lines 6 and 1167;
- **in `glow_domain/notifications.py` and `tests/test_notifications.py`:** A1's record's stale lines (the pre-D5 read rule cited);
- **in `test_chat_routes_offline.py`:** F2 (the completeness test's reach into `settings_store.read_shared`'s helpers).
- The line numbers in the carried entries are as at `26aa7ca` or `ddb1386`; read them at your commit.

**Reversals (D14).** Every new test comes with its reversal, recorded with its failing output; at least: a route that takes its installation from the body; a refusal that names a value; a token written to a row; the session row unlocked (the sign-out case then commits a registration); `put` inside the transaction; the installation left out of the digest; a custody constraint removed; the one-`active`-row constraint removed; the bound removed; a 401 without `WWW-Authenticate`; the runtime importing `glow_notifications`.

## 4. Checks, then the report

- **The trusted classifier,** from `main` (`988a36a`), extracted outside your checkout and run from it with `python3 -I` and full SHAs: `python3 -I <trusted copy>/change_scope.py --base 988a36a1fe4bc7b654a07e565e15fe721dcf3520 --head <your code head> --merge-base` prints `"full": true` (reason `behavior-or-empty`).
- **The diff:** `git diff --name-only <START_SHA> <your head>` lists only owned paths.
- **The API's checks,** in a clean environment, after `pip install --require-hashes -r requirements-dev.lock` in `services/api`: `GLOW_ENV=test python manage.py check`, `GLOW_ENV=test python manage.py test tests`, `makemigrations --check --dry-run`, `ruff check .`, `ruff format --check .` and `mypy`. Record the counts and skips before and after.
- **The proof's offline tests,** Ruff and mypy in `proofs/postgres-ordering`, from its lock; **the contract's** `npm run check` and its Python tests, unchanged; **the mobile app's** `npm run check`, unchanged.
- **Every reversal,** with its output, each file restored (`git status` clean).
- **The run of record,** on your last code commit: every job passed, the chat job among them, within its timeout, and the gate printed "Application checks passed".

**The record,** section "B1", on A2's pattern: this prompt's revision and commit; the start gate's and the environment check's results; what you built, by D-number; the migration's operations; your sweep and each earlier test changed, with the entry added; the follow-ups taken; the new cases and tests; the reversals; the commands and results; any local database runs (iteration, not evidence); the run of record, with each job's duration; the threat model's inputs (who may register, rotate, revoke or read an installation; the token's custody; the installation identifier as a capability); "Substring pins, not semantics"; every limit and deviation.

Your final message, which Nathan relays:
- your branch and heads (code and records);
- the record's path;
- the run of record's link and result, with the chat job's duration;
- what you built, by D-number;
- each earlier test changed, and the follow-ups taken;
- every stop, limit and deviation, and which GitHub route you used.

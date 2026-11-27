# SV4 B1 exact-head review prompt — F12's surface (devices and notification settings), with a written threat model

- **Owner:** App Manager 13. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 26 November 2026.**
- **Durable brief:** [SV4 — the chat and notifications slice](../planning/sv4-chat-notifications.md), revision 12, its section "Stage B": "Review plan (Stage B)" (an exact-head code and security review of each session's final code head, with a written threat model; for B1, who may register, rotate, revoke or read an installation, and the token's custody).
- **Where the result goes:** the report Nathan relays. The manager records it in the SV4 record, "Exact-head review of B1", with a disposition for each finding (a correction before the merge, or carried), and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Fable 5.1 at max.** Effort score 3.78 (confidence 0.85); rung probabilities low 0.00, medium 0.00, high 0.05, extra high 0.12, max 0.82, ultracode 0.01. Model probabilities Fable 5.1 0.78, Opus 5.5 0.22, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.71). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.039, Fable 5.1 at extra high 0.094, Fable 5.1 at max 0.640, Fable 5.1 at ultracode 0.008, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.000, Opus 5.5 at high 0.011, Opus 5.5 at extra high 0.026, Opus 5.5 at max 0.180, Opus 5.5 at ultracode 0.002, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-26T22:12:06Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action. Dev Manager 7's pre-merge read of B1 follows this review (D-07).
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and none may be present. `amthorn78/glow-docs` is attached, read only; this review needs nothing from it (OD-74).
- **It runs alone** (OD-29), after PR60's run and Codex's review of the manager-branch head that holds this prompt (manager workflow, step 6). A full review of B1's code, not a delta review.
- **Deletion condition:** prune after B1's pull request (PR60) merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **exact-head review of SV4 B1**, F12's surface (devices and notification settings, stored and served, sealed until integration), for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one exact code head in full, with a written threat model. This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **SV4's brief,** revision 12 (`docs/planning/sv4-chat-notifications.md`), its section "Stage B": D16 to D20 and D29's B1 cases set B1; D21 to D27 are B2's (the triggers, the deliverer, `logout`, the sweeps, G-04's read), and B1 builds none of them. Much of the section is the Dev Manager's words: DM-101 (`docs/continuity/dev-manager/reviews/2026-11-26-dm-101-sv4-stage-b-brief.md`) approved the design with AM1 to AM16, applied as given in revision 12.
- **P06.3** built F12 at fixture scope (`services/api/glow_domain/notifications.py`): the intents, the transitions, the token's custody types, the versions and the composer, in memory. B1 makes that service the fixture of a persistence port, and adds an ORM adapter and three sealed routes.
- **SV4 Stage A** merged with PR59 at `988a36a` (`main`): chat's sealed routes (`glow_chat/views.py`, whose pattern B1's routes follow) and the chat suite, in which B1's cases run.
- **The implementation** (branch `claude/lucid-fermi-droq7u`; the SV4 record `docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`, section "B1"): code head `e7e7e84`, run of record 45900925199, all twelve jobs, the chat suite 30/30; records head `f106105`. No stop. The manager verified it ("Manager verification of B1") and merged it into the manager branch at `4fe1a7f`. PR60 carries it into `main`.
- **Codex** reviewed `cd920fd`, PR60's first head, and left one P2 thread, comment 4713760650, on `services/api/glow_notifications/persistence.py`, line 376 (`_park`): "Preserve token custody when parking the reference fails" (focus item 3). It is unresolved; nobody has replied to it.

**The code head under review is `e7e7e84`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `e7e7e84` (the start gate checks this).

**Your scope:**
- **The code:** `git diff 988a36a1fe4bc7b654a07e565e15fe721dcf3520 e7e7e845946da1a3aa46f5fcf56add24e99dc70b`, its 23 non-Markdown paths, read in full at `e7e7e84`, each changed module whole, beside its version at `988a36a` where it had one:
  - the API (`services/api/`): the new app `glow_notifications/` (`__init__.py`, `apps.py`, `conf.py`, `contract.py`, `persistence.py`, `providers.py`, `urls.py`, `views.py`); `glow_domain/notifications.py` (the port; the fixture); `glow_persistence/models.py` and the new migration `glow_persistence/migrations/0014_notification_devices.py`; the tests `tests/test_notifications.py`, `test_notifications_port.py`, `test_notifications_routes_offline.py`, `test_notifications_sealed_runtime.py` and `test_model_definitions.py`;
  - the ordering proof (`proofs/postgres-ordering/`): the chat suite's `glow_ordering_proof/chat_cases.py`, `chat_scan.py`, `chat_settings.py`, `chat_suite.py`, `chat_support.py`, `chat_urls.py`, and `tests/test_chat_offline.py`.
- **What B1 relies on unchanged,** read where it relies on it: SV1's `GlowActorAuthentication` and `glow_chat/contact.py`'s `_end_session` (the session's end, which B1's lock order is set against); `glow_profiles/tx.py` (`lock_account`, `read_account_shared`, `caller_transaction_open`, `clock`) and `glow_profiles/idempotency.py` (`digest`, `decide`, `RECORD_LIFETIME`); `glow_chat/views.py` (A2's route pattern) and `glow_domain/chat_projections.py` (`error_for`); `glow_domain/notification_fixtures.py`; `apps/mobile/src/notifications/transport.ts`, `client.ts` and `fixture-adapter.ts` (what the app expects).
- **The Markdown, as claims about the code:** `docs/architecture/data-model.md` and `production-contracts.md` (their changed lines), `proofs/postgres-ordering/README.md` (the chat suite's paragraph), and the record's section "B1" with "Manager verification of B1", whole.
- **The runs:** 45900925199 (the run of record), and PR60's run on `<PROMPT_SHA>` (event `pull_request`), once it has finished; Codex's reviews of `cd920fd` and of `<PROMPT_SHA>`.
- **Out of scope:** B2's work (the triggers, the deliverer, `logout`, the sweeps, G-04's read); the real token, permission prompt and transport (P09.2, P11B); the mobile app, which B1 does not change. Report only where B1's change affects them.

**The threat model.** Write it in your report:
- **Assets:**
  - a device's push token, which no row, log line, answer, exception, receipt or results file may hold; and the token store's reference, held only by an active registration's row, a pending discard's row and (from B2) a push request (AM4);
  - a member's registrations and settings: only the owner may register, rotate, revoke or read an installation of their account, or change their settings (F12: "Token rotation owner/session bound");
  - the installation identifier, a capability for a transfer: a signed-in member who presents another account's installation revokes that account's registration of it, so it is never served, logged or shown (AM7);
  - the ordering of a command against its session's end: no command commits for a session whose end committed first (AM3);
  - the custody constraints in the database (AM2) and the bound of 10 active registrations (D25);
  - the seal: no route in the runtime's URL configuration, no path in the production catalog, no `glow_notifications` module the runtime imports, no factory the runtime names (D16, D31);
  - the chat job's secrets and the suite's scanned values (the synthetic push tokens and installations among them), which no log, results file or upload may carry.
- **Actors:**
  - a member using any of the three routes, in every state SV1 refuses or admits (signed out, expired, at a stale epoch, suspended, deleted) and while their session ends mid-request;
  - another member, with or without the first member's installation identifier;
  - two accounts registering one new installation at once; a transfer whose other account changes under the locks;
  - a request that is not its route's DTO: an extra field, a field naming an actor, a session or an installation, a missing or malformed `Glow-Installation-Id`, a query string, another content type or method, a body on the read;
  - a replay, and the same key and body from another installation;
  - the token store refusing, failing, or answering something that is not a reference;
  - a caller's transaction around a view (`ATOMIC_REQUESTS`, a test case's block);
  - the CI runner, its logs and its artifacts;
  - a later writer of `DeviceRegistration` (B2's `logout` and sweeps; P09.2; P11B).
- **Entry points:** `GET api/v1/notifications`, `POST api/v1/notifications/device`, `POST api/v1/notifications/settings`; `OrmNotificationPersistence`'s `read`, `device` and `settings`; the factory hooks (`GLOW_NOTIFICATIONS_TOKEN_STORE`, `GLOW_NOTIFICATIONS_PUSH_TRANSPORT`); the migration `0014`; the chat suite's settings, URL configuration, cases, support, scan and runner.

For each threat, give the code that stops it and the test or run that proves it. The focus:
1. **Who may act on an installation (D19).** Each route takes its actor from `GlowActorAuthentication` only and the installation from `Glow-Installation-Id` only; a `DeviceIntent`'s `device_id` must equal the header (`forbidden`). Say whether any route serves or changes another account's registration or settings, whether the read tells a member whether another account holds an installation, whether a revoke can reach another account's registration except through a transfer, and whether the answers tell a caller that a transfer took place.
2. **The transfer and the capability (AM7).** A register on an installation active for another account revokes that account's registration (`ended_by` `transfer`) after locking both accounts, the lower first, having read the holder with no lock; a change under the locks is `transfer_changed`. Say whether the re-read under the locks closes every race (the holder's own rotate, revoke or a second transfer; the holder's account suspended or deleted), whether the holder's registration row can change without its account's lock, and whether the record's statement of the capability (never served, logged or shown; the suite's value scan holds the installations) holds.
3. **Custody end to end (D18, AM4, AM2).**
   - The store's `put` runs in `device()` before `_run`'s transaction; a fresh reference the command does not save is parked after the transaction (`_park`); a retired reference moves to `PendingTokenDiscard` inside the transaction and is discarded after the commit, its row removed then. Say whether any path saves a reference twice, loses one without a row (beyond the recorded stop between `put` and `_park`), leaves one on a revoked row, or discards one still in use.
   - The constraints `device_account_installation`, `device_one_active_installation`, `device_reference_while_active` and `device_ended_when_revoked` (with its NULL fix): say whether each refuses what it names on PostgreSQL, whether any custody rule is left to code alone, and whether `PendingTokenDiscard`'s uniqueness can make a retire fail.
   - **Codex's P2 on PR60** (comment 4713760650, on `cd920fd`; `persistence.py`, line 376, `_park`). **The claim:** if the store's `put` succeeds and the database then fails, `_run` answers an error and `_park`'s insert can fail too; `_park` catches that and only logs a fixed line, so the token stays in the store with neither a registration nor a pending discard, and once `device()` returns no sweep can find it. This happens during a handled database failure, with no process stop, which the record's custody limit (a stop between `put` and `_park`) does not cover. Codex suggests discarding through the store when parking fails, or keeping a recoverable handle. **Say:** whether the claim holds, shown by a test, a probe or the code's path; whether any other path loses a reference the same way (`_discard`'s removal of the pending row; a retire whose `bulk_create` fails inside the transaction); which correction class it falls in; and the smallest fix and where it belongs. Do not fix it.
   - The token in the idempotency digest (AM5): say whether the keyed digest, with the installation bound, can reveal the token or let another installation replay.
   - Say whether any log line, exception message, answer, receipt or the results JSON can carry a token, a reference or an installation identifier.
4. **The locks (AM3).** A device or settings command locks the account `FOR NO KEY UPDATE`, then the session `FOR SHARE`, then the registrations `FOR UPDATE` by key; the read takes the account and session `FOR SHARE`. Say whether a register reaching its session's row while the sign-out holds it is refused after the sign-out commits (READ COMMITTED's re-read), whether any order here can deadlock with `glow_chat`'s writers, SV2's or SV3's account writers, or another F12 command, and whether the read can pair a new version with old settings. The record says r19 (the settings command locking its session before its account) is caught only by an offline structure test: say whether that is a defect or a limit.
5. **The bound (D25).** At most 10 active registrations, counted under the account lock; a rotation adds none; a transfer into an account at the bound. Say whether two of an account's commands can pass the bound together, and whether `state_conflict` beyond it is right.
6. **Idempotency.** SV2's `decide` after the session's checks; the record with F12's receipt code and SV2's 24 hours. Say whether a replay answers the current projection without changing anything, whether a replayed register parks its fresh reference, and whether an idempotency record can outlive what it names in a way that matters.
7. **The codes and the challenge (D19, AM6).** `glow_notifications.contract.REFUSALS` and `refusal()`: every session reason `unauthenticated`, with `WWW-Authenticate: Bearer` on every 401 at the door or inside the locks; a deadlock `state_conflict` (retryable), any other database error `state_conflict`; an unknown reason `state_conflict`. Say whether the completeness test (`MappingCompletenessTests`) reaches every reason the adapter, the fixture and their helpers can raise, and whether any refusal names a value or differs in a way that tells a member something about another account.
8. **The routes' shape.** `non_atomic_requests` (and case 1's `ATOMIC_REQUESTS` check), JSON-only negotiation, `no-store`, 405, a body on the read, a query string, another content type, `RequestDataTooBig`. Say whether each view refuses a caller's transaction, and whether any route answers outside the contract's `Error`.
9. **The port and the fixture (D18).** `NotificationPersistence` and its two implementations: say whether the fixture and the adapter answer alike for every case both reach (the bound, the codes, the versions, a transfer), whether `tests/test_notifications.py` keeps every earlier assertion against the fixture, and whether the fixture's guard (`require_fixture_environment`) still holds.
10. **The models and the migration (D17).** `0014`'s operations in order, the removals of `platform` and `push_enabled`, the renames, the outcome codes in `IdempotencyRecord`'s choices and `intent_result`, the two new tables. Say whether the migration runs from zero and from `0013` without data loss that matters (no row exists outside a proof), and whether `test_model_definitions.py`'s changes gain only B1's entries.
11. **The seal (D16, AM1, D31).** `test_notifications_sealed_runtime.py`: the runtime's settings, URL configuration and WSGI application import nothing of `glow_notifications`; the backend is the dummy one; no runtime setting names either factory. Say whether the test would catch a module reached indirectly, and whether the served runtime could reach a fixture.
12. **The cases (D29, AM13).** Check each of the twelve new cases against D29's B1 list and AM13's additions: register, rotate, revoke and register again; a transfer; each refusal; a replay and a conflict; the settings advance; no token in any row, log line or answer (and the case that queries the rows for each token); the bound; the sign-out race; a refused register's parked reference; the other installation's conflict; two accounts on one new installation; a transfer that changes under the locks. Say whether any is vacuous, whether the synthetic tokens' derivation from the job's existing key file is sound and kept out of every output, and whether the follow-ups B1 took (F1, F4, A2R-6, A2R-7, the README's case list, A2R-13's `data-model.md` lines, A1's stale lines) are done as the carried entries say.
13. **The earlier tests and the reversals.** Each changed earlier test gains only B1's entry (D31): `test_model_definitions.py`, `test_notifications.py`'s seal list, `test_chat_offline.py`'s settings, URL modules and plan. Say whether any new test is vacuous, and whether each reversal the record names (53) fails its test; the record names three caught offline only (r16 at its first pass, r19, r30) and one only by the value scan (r15).
14. **The records:** check every claim in `production-contracts.md`'s "F12 on the server", `data-model.md`'s changed lines, the proof README's chat paragraph and the record's section "B1" against the code and the runs. The manager routed to B2 the CI `mypy` list (`services/api/pyproject.toml` does not name `glow_notifications`; AM13-15), the CI policy's line 13, the README's lines 76 and 216 and A2's order-dependent test: say whether any of them is a defect D-07 names before B1 merges.

**Re-run, at least,** in a scratch copy of `e7e7e84`, each package in a virtual environment installed from its own lock with `pip install --require-hashes`, under `env -i`:
- **The API:** `GLOW_ENV=test python manage.py check && GLOW_ENV=test python manage.py test tests`; `ruff check .`, `ruff format --check .` and `mypy`, and `mypy glow_notifications` by name, since CI's list does not name it; `GLOW_ENV=test python manage.py makemigrations --check --dry-run`.
- **The ordering proof:** its offline tests, `ruff` and `mypy`.
- **Reversals, offline, on copies,** each restored afterwards. For each, say which test fails, or that only a database case catches it:
  - a route that takes its installation from the body;
  - the store's `put` moved inside the transaction;
  - the installation left out of the digest;
  - a 401 from inside the locks without `WWW-Authenticate`;
  - the bound removed;
  - a refusal that names a value;
  - the runtime's URL configuration including `glow_notifications.urls`;
  - any other you doubt.
- **The database cases, informational:** the chat suite on a throwaway PostgreSQL under P06.DB's D4, if Docker allows, with any probe you need (a concurrent sign-out, a transfer, a constraint written around).

**What comes after this review: the correction classes** (D-07; the manager workflow, step 6). Report every finding with its severity. A correction pass takes every blocking finding, and any should-fix finding that is:
- **a defect in application behaviour:** a route that serves, changes or refuses against F12's transitions or D19; a version, a replay or a conflict answered wrongly; a deadlock or a crossing; a bound passed;
- **a defect at a security boundary:** an actor or an installation taken from anything but SV1's authentication and the header; another account's registration or settings read or changed except through the transfer F12 allows; a token or a reference anywhere AM4 does not allow, or a custody rule left open; an installation identifier served or logged; a command that commits for a session whose end committed first; a seal crossed; HDE's boundary crossed;
- **a false claim that a decision or the merge would rest on** (D-07): where that claim is what a decision, an acceptance check or the merge reads.

A missing test is a correction only when the behaviour is at a security boundary or an acceptance check rests on it. Any other overclaim, and the reach of a static scan or a substring pin, is recorded and carried. For each finding, say whether it falls in one of these classes.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 13. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, thread resolutions, re-runs or workflow dispatches. Read GitHub with the GitHub tools where your session has them, otherwise with `gh api` REST `GET` calls, and say which you used.
  - **Scratch work goes in a copy outside the repository,** never the checkout (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
- **Network:**
  - PyPI and the npm registry, for hash-locked installs from the existing locks in a scratch copy;
  - Docker Hub, only to pull the PostgreSQL image the workflow pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`);
  - GitHub, read only, to read the runs, PR60 and Codex's reviews.

  A page you cannot reach is named as unread, never filled from memory.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions): a throwaway PostgreSQL in Docker, from that image, on loopback only; a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present; removed afterwards. Migrations reach that database only through the proof's own commands; never run `manage.py migrate` yourself.
- **Never:**
  - dump the environment, or print a credential, password, marker, token, session key or key, the suite's synthetic push tokens included;
  - read, print or use the value of any `AWS_*` variable (section 1);
  - call any provider or HDE;
  - connect to any database but a throwaway one you started under D4's conditions, HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:** `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_|RAILWAY_)'` prints names only. If any is present, stop and report.
3. **AWS names may be present** (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_CA_BUNDLE`); the cloud container sets them (OD-76). `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below except your GitHub reads runs without them.
5. **The toolchain:** CPython 3.12.14 as `python3.12`; Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`; Docker if present. Record their versions.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables. No `AWS_*` name passes.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, 988a36a1fe4bc7b654a07e565e15fe721dcf3520
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet e7e7e845946da1a3aa46f5fcf56add24e99dc70b HEAD -- . ':!*.md' && echo "the code head under review"
git diff --quiet e7e7e845946da1a3aa46f5fcf56add24e99dc70b origin/claude/magical-wozniak-yfmmx2 -- . ':!*.md' && echo "no code on the live branch after e7e7e84"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-19-sv4-chat-notifications.md | grep -c -E '^#+ Exact-head review of B1'   # must print 0
```

If any check fails, stop and report. The prompt is stale if its commit is not on the live branch, a non-Markdown path changed there after `e7e7e84`, or this review is already recorded.

**Classify the change** as root `AGENTS.md` requires, with the trusted base policy outside the candidate tree:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
```

Run it from the checkout (the policy file outside it). Expected: `"full": true`. Anything else: stop and report.

**Then read, completely, at `HEAD`:**
- root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`; `proofs/postgres-ordering/README.md`; `docs/operations/ci-and-branch-policy.md`, the database proof jobs' section;
- the brief, revision 12: the section "Stage B" whole, and Stage A's D2, D8 and D13 to D15 it builds on;
- DM-101's report, whole;
- P06.3's brief (`docs/planning/p06-3-notifications.md`), "Outcome" and D1 to D9;
- B1's prompt (`docs/ephemeral/2026-11-26-sv4-b1-f12-surface-prompt.md`), its stop rule, "What to do" and "Earlier tests" above all;
- the record's section "B1", whole, with "Manager verification of B1";
- every file in the code diff, whole, beside its version at `988a36a`.

**The runs,** read from GitHub: 45900925199, and PR60's run on `<PROMPT_SHA>` if it has finished: every job's conclusion and duration, and the gate's line; Codex's reviews of `cd920fd` and of `<PROMPT_SHA>`, and any thread on PR60.

## 3. What to do

1. Write the threat model, then review the change against the focus, item by item.
2. In a scratch copy of `e7e7e84`: re-run the checks and the reversals above, and any you doubt; run the database cases locally under D4 if you can, informational.
3. For each finding: its severity (blocking, should fix, nit), its file and line, the evidence, and whether it falls in a correction class.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- the threat model, each threat with its stopping code and its test or run;
- the focus, item by item, with your verdict on each;
- every finding, with its severity, file and line, evidence and correction class;
- the checks and reversals you re-ran, each with its exact result, and any local run;
- the runs and Codex's reviews as you read them, and which GitHub route you used;
- your verdict: **approve**, **approve with nits** or **changes requested**;
- what you did not read or run, and why.

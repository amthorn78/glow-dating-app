# SV3 Stage A prompt — pair eligibility, the two-way rule, age and distance, and recommended then broader pages, proven on disposable PostgreSQL

- **Owner:** App Manager 11. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 11 November 2026.**
- **Durable brief:** [SV3 — The eligibility, discovery and interactions slice](../planning/sv3-eligibility-discovery-interactions.md), revision 2.
- **Where the result goes:**
  - the session's changes in Stage A's owned paths, and its record, `docs/testing/evidence/<date>-sv3-eligibility-discovery-interactions.md`, under the heading `## Stage A`, on its own branch;
  - the run of record: the Foundation run on its last code commit, with the discovery phase;
  - the manager adds its verification to the record, and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 2.68 (confidence 0.51); rung probabilities low 0.00, medium 0.03, high 0.43, extra high 0.37, max 0.17, ultracode 0.00. Model probabilities Fable 5.1 0.36, Opus 5.5 0.52, Sonnet 5.5 0.12, Haiku 5.5 0.00 (confidence 0.36). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.011, Fable 5.1 at high 0.155, Fable 5.1 at extra high 0.133, Fable 5.1 at max 0.061, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.016, Opus 5.5 at high 0.224, Opus 5.5 at extra high 0.192, Opus 5.5 at max 0.088, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.004, Sonnet 5.5 at high 0.052, Sonnet 5.5 at extra high 0.044, Sonnet 5.5 at max 0.020, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Flags: boundary between extra high and high; model near tie between Opus 5.5 and Fable 5.1. Sent 2026-11-11T19:12:15Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs.
  - The brief's revision 2 applies DM-60's Q1 to Q15 as written. DM-60 says they need no read before this prompt (DM-60, section 2).
  - This prompt authorizes no credential use and no live provider action. The suite's keys and the database password are generated for one run and destroyed with it.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Then, in order:
  - the manager's verification;
  - the PR and Codex's review of its head;
  - an exact-head code and security review with a written threat model (the brief's "Review plan", Stage A's items);
  - the Dev Manager's read, before the merge, of the CI policy's paragraph and the data model's and contract's rewritten texts.
  - Stage B's prompt follows only after Stage A merges (D1).
- **Deletion condition:** prune after Stage A's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **implementation session for SV3's Stage A**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What Stage A is.** You build the server's eligibility and discovery on SV1's actor and SV2's profile. Stage A decides who may see whom. It is proven on a disposable PostgreSQL in CI and kept sealed from the served runtime until P11. It covers:
- pair eligibility over the ORM, in one consistent view (D2, D3);
- the two-way rule over the four fields, age, and distance (D4, D5);
- recommended first, then broader, with the compatibility port's fixture adapter in the proof only (D6);
- bounded batches and cursors, with consumption's exclusions and one batch per viewer and collection (D7);
- what a viewer can learn, measured (D8);
- the page route and the card's additive DTO (D13, for Stage A's parts);
- a discovery suite on a fourth disposable database in the Database proof checks job (D14, Stage A's cases).

There is no provider, deployed URL, real member, HDE call or stored credential.

**The brief, `docs/planning/sv3-eligibility-discovery-interactions.md`, revision 2, is the specification.** Stage A builds:
- Outcome items 1 to 3, and items 8 to 11 for those parts;
- D1 to D8, D13 for Stage A's parts, D14's Stage A cases, and D15 to D19;
- acceptance checks 1 to 6, and 12 to 14 for Stage A's routes.

Much of its text is the Dev Manager's words (DM-60), checked against the code. Follow them exactly. Where this prompt summarizes the brief, the brief wins.

**What Stage A leaves to Stage B, as the brief places it:**
- **Like, pass, the match, unmatch and block** (D9 to D11), and their routes. Stage A builds no action route.
- **Resurfacing and undo** (D12), undo's DTOs (D13's undo line), and the fixed limit `rematch_not_built` in `glow_domain/profile_settings.py`.
- **D10's writer** in `glow_chat/contact.py`: Stage A changes nothing in `glow_chat/`.
- **D14's concurrency cases** (DB05, DB10) and acceptance checks 7 to 11.
- **Consumption is read, not written, in Stage A** (D7, Q5): Stage A's selection and recheck exclude a candidate the viewer has liked or passed, and the other member of any pair with a `Match` row. Its tests seed those `DirectionalInteraction` and `Match` rows in setup, as SV2's suite seeds the chart and identity rows. No Stage A code writes them.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 11. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only the brief's "Owned paths (the sessions)", for Stage A's parts. Of those, `services/api/glow_chat/contact.py` and `services/api/glow_domain/profile_settings.py` are Stage B's only;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule.** Stop and report, with no further change, if any of these holds:
  - **an owned path:** the work needs a path outside Stage A's owned paths. That includes:
    - `services/api/glow_api/` (the seal);
    - `services/api/glow_chat/`, `services/api/glow_identity/` and `services/api/glow_profiles/`: you use their reads and writers unchanged;
    - `services/api/glow_domain/profile_settings.py`;
    - any `apps/` path other than `apps/mobile/src/contracts/generated/`, and those files written other than by `npm run generate --prefix packages/contracts`. That includes a mobile source, test or fixture that would have to change for the Mobile checks job to pass;
    - `scripts/`, any other workflow job, the `Dockerfile`, an environment template, or the runtime scope's `requirements.in` and `requirements.lock`;
    - the CI policy (`docs/operations/ci-and-branch-policy.md`), which is the manager's;
  - **the dependency set** (D16): any new Python or npm package, or a changed pin;
  - **a design change:** the work needs any of these:
    - an existing DTO or registry entry to change;
    - a page read that cannot be one statement, and cannot run in one REPEATABLE READ transaction either (D2, Q1);
    - the batch's policy version to be more than the one `RecommendationBatch.policy_version` value (D7, Q3);
    - the SQL whole-years rule to differ from `age_years` at any of the onboarding fixtures' leap-day cases (D4);
    - a role the oracle does not authorize;
  - **the seal:** the served runtime would import `glow_discovery` or any new module, or select a fixture compatibility provider;
  - **the timeout:** the Database proof checks job cannot stay within its 30-minute timeout (D14, Q13).
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished. A newer push cancels the earlier run's application jobs, and the run of record is lost. Push your records commit only after the run of record has finished. The workflow runs on pushes to `claude/**` and `ccr-**`; if your branch is named otherwise, say so in the report, since no run starts.
- **Network:**
  - **PyPI and the npm registry:** for `pip install --require-hashes` and `npm ci --ignore-scripts` from the existing locks only;
  - **Docker Hub:** only to pull the PostgreSQL image the CI job pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`) for a local run (below).

  A page you cannot reach is named as unread, never filled from memory.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions):
  - a throwaway PostgreSQL in Docker, from the CI job's pinned image, on loopback only;
  - a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present;
  - removed afterwards.

  Local passes are "iteration, not evidence"; the run of record is CI's. If Docker or the image is unavailable, iterate through CI and say so.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, password, code, token, session key or signing key, in any form;
  - make test data that looks real. Accounts, emails, names, birth facts, places and coordinates are synthetic and obviously so (`@example.invalid` addresses);
  - call any provider or HDE, send any email, or run any command in `proofs/stream-chat/`;
  - connect to any database but a throwaway one you started under D4's conditions. Run `migrate` or `makemigrations` only through the proof's own commands against such a database, or under the static registry's dummy settings;
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
git merge-base --is-ancestor 3240ef0acca7983e5b60b9a111be371ed5a16b74 HEAD && echo "PR44 present"   # main's merge of SV2 Stage B. Must print "PR44 present"
git diff --name-only 3240ef0acca7983e5b60b9a111be371ed5a16b74 HEAD | grep -v -E '\.md$'           # against main: must print nothing
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/api proofs/postgres-ordering packages/contracts apps/mobile/src/contracts .github 'docs/testing/evidence/*sv3*' docs/architecture docs/testing/p11-deferred-acceptance.md   # must print nothing
test -e services/api/glow_discovery && echo "glow_discovery exists"                                # must print nothing
ls services/api/glow_persistence/migrations | grep -E '^[0-9]{4}_'                                 # must list 0001 to 0009 only
```

If a check fails, stop and report. The prompt is stale if:
- `<START_SHA>` is not on the live manager branch;
- the live branch has changed an owned path since it;
- or the brief's "Sessions" already records a Stage A implementation session.

**Then read, completely:**
- **The instructions:**
  - root `AGENTS.md` and `CLAUDE.md`;
  - `services/api/README.md`, `proofs/postgres-ordering/README.md` and `packages/contracts/README.md`;
  - `apps/mobile/AGENTS.md`: you change only its generated contracts.
- **The brief,** revision 2, whole.
- **The Dev Manager's report** DM-60, whole: `docs/continuity/dev-manager/reviews/2026-11-11-dm-60-sv3-brief.md`. Its examples (the two-statement page in section 4, the keyed tie-break in section 7, the stale cases and consumption in section 8) are cases your tests should cover.
- **Nathan's directions:** OD-12, OD-55, OD-60 and OD-61 in `docs/continuity/owner-directions.md`.
- **The matrix recheck:** `docs/testing/evidence/2026-11-11-sv3-matrix-recheck.md`.
- **The contract:**
  - `packages/contracts/production/flows-v1.json` (F07 to F10 and F13), `gapp-api-v1.schema.json` and `openapi.json`;
  - `packages/contracts/transition_contract.py` (`authorized` and the roles it knows);
  - `packages/contracts/tests/`, and `scripts/generate.mjs` (read only);
  - `docs/architecture/production-contracts.md`: the flow index, "Pagination, idempotency and stale state", "Policy boundaries and deliberately unavailable operations", "P05.3 internal interaction result and identity bridge", "Compound actions and model projections", and its list of trusted test prerequisites.
- **The data model:** `docs/architecture/data-model.md`, its rows for the account, the age state, consent, the profile, the four fields and "show me" sets, preferences, the area, interactions, blocks, matches, batches and entries, and the compatibility snapshot; its unit-of-work table and its outbox event table.
- **P05's behaviour,** which the server must match: `docs/architecture/discovery-fixtures.md`, `interactions-fixtures.md`, `reciprocal-eligibility-fixtures.md` and `trusted-eligibility.md`; and `services/api/glow_domain/eligibility.py`, `trusted_eligibility.py`, `eligibility_facts.py`, `discovery.py`, `interactions.py`, `compatibility.py`, `ports.py` and `provider_fixtures.py`.
- **The code you build beside** (read only):
  - `services/api/glow_chat/contact.py`: `_run`, `_lock`, `_contact_state_checks`, `activate_match`, `block`, `unblock`, `unmatch`;
  - `services/api/glow_profiles/`: `requirements.py`, `operations.py`, `settings_store.py` (`read_shared` and the pointer-order check, D19), `idempotency.py` (the keyed digests, for D6's tie-break), `areas.py`, `media.py` (`delivery_reference`), `views.py`, `urls.py` and `contract.py`;
  - `services/api/glow_identity/`: `authentication.py` (the actor) and `age.py` (`age_years`);
  - `services/api/glow_domain/identity.py`, `profile_fields.py` and `profile_settings.py`;
  - `services/api/glow_persistence/models.py`, whole;
  - `services/api/tests/test_profiles_sealed_runtime.py` and `test_model_definitions.py`.
- **SV2:** its brief, `docs/planning/sv2-profiles-media.md` (D2 to D5, D9, D11 to D13, D17 and D19), and its record, `docs/testing/evidence/2026-11-10-sv2-profiles-media.md`.
- **The proof:**
  - `proofs/postgres-ordering`: its settings, `environment`, `marker`, and the profile suite's files (`profile_settings.py`, `profile_suite.py`, `profile_support.py`, `profile_cases.py`, `profile_scan.py`, `profile_urls.py`);
  - the Database proof checks job in `.github/workflows/foundation.yml`, whole.
- **The plans:**
  - the P06.DB brief's D1 to D6;
  - the P11 plan's DB04, DB10 and DB11 rows, and its SV1 and SV2 entries;
  - `docs/operations/ci-and-branch-policy.md`'s Database proof checks paragraph (manager-owned: read it, do not change it).

**Facts from the code that the design relies on:**
- **A block bumps only its actor's `blocks_version`** (`glow_chat`'s `block`). So a candidate's block of the viewer leaves the viewer's batch fresh, and each page's recheck must read `Block` rows in both directions for every entry (D7).
- **SV2's settings store takes pointers in name order** (D19). Every Stage A transaction that reads a setting takes all its pointers in its first `read_shared` call.
- **`visible` is recomputed by every SV2 requirement writer** (DM-60 item 3). ADULT and CONSENT are read directly because `visible` can lag them (D3).
- **Two helpers refuse to run inside an open transaction:** `glow_chat`'s reads (`reads.py`, `_caller_transaction_open`) and SV1's `require_no_transaction` (`revocation.py`). Django's `TestCase` opens a transaction, so a test that needs either uses the proof or a `TransactionTestCase`.
- **The launch distance choice is `anywhere`** (SV2 Stage A's record), which filters nothing. D5's distance tests publish a setting version with a mile choice in the test's setup, through the settings store's domain operation.

## 3. What to do

1. **Outcome items 1 to 3, with the page route,** in the brief's order. Each comes with its tests, and every test comes with its reversal (D18): a temporary edit that must make the test fail, run and then undone. Record the edit and the failing output. Make at least these reversals, each named in the record:
   - **D2:**
     - the page's recheck split into two statements outside one REPEATABLE READ transaction, with DM-60 section 4's example (blocked, pause, unblock) showing a paused profile;
   - **D3:**
     - each predicate removed in turn, for the viewer and for the candidate: the excluded member then appears;
     - CONSENT read without the current-version check, or without the purpose filter;
     - a missing row treated as a pass;
     - a block read in one direction only;
   - **D4:**
     - one direction of one field removed;
     - "all" matching only the current list, so a value the console adds is missed;
     - a narrowed set matching "not stated";
     - the candidate's age taken from the birth input, or the SQL rule differing from `age_years` at a leap-day case;
     - the age range applied one way under `both_ways`;
   - **D5:**
     - two members in one area not at distance zero;
     - a boundary off by one mile;
     - a distance, a coordinate or an area ID in a response, an error, a log line or an event, one reversal each;
   - **D6:**
     - an unkeyed tie-break, reproducible from the batch's and the profiles' IDs (Q2);
     - broader including the batch's recommended candidates;
     - the port's `unavailable` stopping broader;
   - **D7:**
     - each of Q4's stale cases accepted in turn (forged, another viewer's, the other collection's, expired, viewer versions changed, policy version changed, a deleted batch);
     - a publication of `consent.onboarding`, or of a `profile.*` or `discovery.*` setting the selection reads, leaving the batch's policy version unchanged (Q3);
     - a seeded like, pass or `Match` row (each state) not excluding (Q5);
     - an earlier batch of the same collection left in place when a new one is created (Q5's bound);
     - a page over 50 items, or a batch over 100;
   - **D8:**
     - a count, a reason or another member's private value in a response;
   - **D13:**
     - a "show me" set, a filter, an area ID, an internal point or a distance in the card;
     - a field whose `shown` flag is off shown on the card;
     - an unapproved photo's reference on the card;
   - **D15:** the runtime importing `glow_discovery`, or selecting the fixture compatibility provider: the sealed-runtime test fails;
   - **the log capture:** a birth date, a coordinate, a distance, an own-words value or a "show me" set logged in one path.
2. **The contract** (D13, with DM-60's Q12; owned paths):
   - the card's additive DTO for the shown fields and the area's name, its wrapper and the new page response, in the production schema;
   - their `openapi.json` components (no paths);
   - their corpus cases;
   - their flow-registry entries in F07, with an allowed and a forbidden example each in `tests/test_transition_contract.py`; no existing entry changes;
   - the `location_label` sentence in `production-contracts.md`'s "Compound actions and model projections", rewritten to say what the card now shows;
   - a README section for SV3's additions.

   Then regenerate with `npm run generate --prefix packages/contracts`, never by hand. Run it a second time and confirm that `git status` shows no further change. Record which generated files changed.
3. **The proof** (D14, Stage A's cases): the discovery suite in `proofs/postgres-ordering`, on a fourth database, `glow_discovery_proof`, in the same PostgreSQL, with its own marker and settings, through SV1's sign-in and SV2's routes for the cases' own members. Then:
   - the Database proof checks job's steps for it, after the profile suite, on the pattern of the profile suite's: the earlier databases' markers each refused on the new one, the migrations from zero, `makemigrations --check --dry-run`, the suite, its own secret scan before any output is shown, and a second run's refusal with the row counts unchanged; its results JSON uploaded only after the scan passes;
   - **the plans' population** (Q13): seeded directly in the suite's setup, with every row completion requires, at 1,000 members; each candidate query's `EXPLAIN (ANALYZE, BUFFERS)` plan recorded, labelled as the disposable setup's measurement;
   - the discovery phase's duration, against the job's 30 minutes.
4. **The local checks:**
   - **API,** in `services/api`: `python3.12 -m venv .venv`, then `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`. Then, with `GLOW_ENV=test`: `manage.py check`, `manage.py test tests --verbosity 2`, `smoke.py`, `ruff check .`, `ruff format --check .`, `mypy` and `python -m glow_persistence.static_check`;
   - **the contracts,** in `packages/contracts`: `npm ci --ignore-scripts`, then `npm run check`, then the Python contract tests (`PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests -v` from `services/api`, as CI runs them);
   - **the mobile app,** in `apps/mobile`: `npm ci --ignore-scripts`, then `npm run check`, with the regenerated outputs and no other change. Its export and rendered checks are CI's; `playwright install` is never run here;
   - **the proof,** in `proofs/postgres-ordering`: its venv and hash-locked install, its offline tests under `env -i`, Ruff and mypy;
   - **a local database run,** if Docker allows it under D4's conditions: iteration, not evidence.
5. **The run of record.**
   - Commit and push your code. The Foundation workflow runs on your branch's pushes. Wait for the run to finish (the push rule above).
   - Read it with your GitHub tools:
     - every job's conclusion, and the gate's line (`Application checks passed`);
     - the API test count;
     - the ordering, identity, profile and discovery suites' results;
     - the discovery phase's duration, against the job's 30-minute timeout;
     - the Mobile checks job's contract check, typecheck, tests, export and rendered checks;
     - whether a toolchain retry fired;
     - that no secret, coordinate or distance appears in the job's log.
   - The run of record is the one on your last code commit. If it fails, stop and report the failing job and its log lines. Do not re-run it, and push no fix without saying so in the report.
6. **The records** the brief owns, for Stage A's parts:
   - the data model's batch and entry rows, and the eligibility read, rewritten as built;
   - the contract document's F07 index row, kept in step with the registry by hand, its server mapping, and the `location_label` sentence (above);
   - a note in `discovery-fixtures.md`, `reciprocal-eligibility-fixtures.md` and `trusted-eligibility.md` that the server exists, sealed;
   - the P11 plan's partial evidence for DB04, DB10 and DB11.

   Change no other section of those files.

## 4. The record

Write `docs/testing/evidence/<today's date>-sv3-eligibility-discovery-interactions.md`, under `## Stage A`:
- the start gate's results, the environment check (names only) and the toolchain versions;
- a table with one row per Outcome item and acceptance check in Stage A: the files, the test, the reversal and its failing output;
- the contract: the new DTOs, the registry entries with their examples, and the generated files that changed;
- the recorded query plans, with the population and the phase they ran in;
- **the threat model's inputs:**
  - every route and its refusals, and who may call it;
  - each predicate, its source row and its direction;
  - every value a viewer can see of another member, and every value they cannot;
  - D8's population-of-one measurement: what the two responses reveal;
  - the tie-break's key, and why a client cannot compute the order;
  - each read's statements and their snapshot;
  - each with its test;
- every command you ran, with its result line, with local database runs listed as iteration, not evidence;
- the run of record: its ID, each job's result, the counts, the discovery phase's duration, and whether a retry fired;
- what you could not run, and why.

Commit each logical step with a clear message ending in the session's attribution lines. Push your records commit only after the run of record has finished. Confirm that `git status` is clean, and that `git diff --name-only <START_SHA> HEAD` lists only your owned paths.

## 5. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch, your code head and records head;
- the start gate's and the environment check's results;
- for each Outcome item: what changed, its tests, and each reversal's result;
- the contract: the DTOs, the registry entries, and the generated files that changed;
- the query plans' summary: population, each query's time and its plan's shape;
- each local check's result, and whether a local database run was used;
- the run of record: its ID, every job, the gate's line, the counts, the discovery phase's duration and whether a retry fired;
- anything that met the stop rule, every deviation from the brief, and what you could not run.

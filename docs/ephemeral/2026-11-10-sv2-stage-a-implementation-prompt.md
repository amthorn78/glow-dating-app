# SV2 Stage A prompt — the profile, its settings, consent, the adult check, the birth input and visibility, proven on disposable PostgreSQL

- **Owner:** App Manager 10. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 10 November 2026.**
- **Durable brief:** [SV2 — The profiles and media slice](../planning/sv2-profiles-media.md), revision 3.
- **Where the result goes:**
  - the session's changes in Stage A's owned paths, and its record, `docs/testing/evidence/<date>-sv2-profiles-media.md`, under the heading `## Stage A`, on its own branch;
  - the run of record: the Foundation run on its last code commit, with the profile phase;
  - the manager adds its verification to the record and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at max.** Effort score 3.54 (confidence 0.61); rung probabilities low 0.00, medium 0.01, high 0.10, extra high 0.28, max 0.53, ultracode 0.08. Model probabilities Fable 5.1 0.35, Opus 5.5 0.64, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.52). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.003, Fable 5.1 at high 0.035, Fable 5.1 at extra high 0.098, Fable 5.1 at max 0.185, Fable 5.1 at ultracode 0.028, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.006, Opus 5.5 at high 0.064, Opus 5.5 at extra high 0.179, Opus 5.5 at max 0.339, Opus 5.5 at ultracode 0.051, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.001, Sonnet 5.5 at extra high 0.003, Sonnet 5.5 at max 0.005, Sonnet 5.5 at ultracode 0.001, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Flags: boundary between extra high and max. Sent 2026-11-10T02:42:19Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs.
  - The brief's revision 3 applies DM-52's and DM-53's conditions as written. DM-53 says they need no read before this prompt (DM-53, section 2).
  - This prompt authorizes no credential use and no live provider action. The identity keys, the profile suite's `SECRET_KEY` and the database password are generated for one run and destroyed with it.
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

You are the **implementation session for SV2's Stage A**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What Stage A is.** You build the server's profile on SV1's actor. It is proven on a disposable PostgreSQL in CI and kept sealed from the served runtime until P11:
- a versioned, audited settings store with launch defaults and fixed limits in code (D2);
- the four two-way list fields, the own words and the display choices (D3);
- the age range, and the location by area, with the phone's coordinates never kept (D4, D5);
- onboarding consent and the sensitive-fields consent (D6);
- the adult check and the age state's date (D7);
- the private birth input (D8);
- completion, demotion, pause, resume and restriction (D9);
- identity verification's seam and staff approval without it, behind a setting (D18);
- the member's routes, additive contract DTOs and their flow-registry entries (D11);
- a profile suite on a third disposable database in the Database proof checks job (D12).

There is no provider, deployed URL, real member, HDE call or stored credential. **Photos are Stage B's** (D10).

**The brief, `docs/planning/sv2-profiles-media.md`, revision 3, is the specification.** Stage A builds:
- Outcome items 1 to 6, and items 8 to 11 for those parts;
- D1 to D9 and D11 to D18 (D16 only if it applies);
- acceptance checks 1 to 9, 11 and 12.

Much of its text is the Dev Manager's words (DM-52 and DM-53), checked against the code. Follow them exactly. Where this prompt summarizes the brief, the brief wins.

**What Stage A leaves to Stage B, as the brief places it:**
- **Photos:** everything in D10 and acceptance check 10.
- **The photo requirement** in completion (D9: "Stage B adds it"). The owner's completion read's closed list keeps its photo value, as D11 lists it. Stage A's completion neither checks nor reports it.
- **The media policy setting and its ceilings** (D2, "the media policy (D10)"). The manager reads D1 and check 10, which puts the ceiling's refusal under Photos, as placing it in Stage B. Stage A's check 1 covers every other setting.
- **F05's registry changes** (D11, "F05 is Stage B's").
- **The P11 plan's PV04** and `private-media-fixtures.md`.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 10. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only the brief's "Owned paths (the sessions)", for Stage A's parts;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule.** Stop and report, with no further change, if any of these holds:
  - **an owned path:** the work needs a path outside the owned paths. That includes:
    - `services/api/glow_api/` (the seal);
    - `services/api/glow_chat/`: you call its writers, never change them;
    - `services/api/glow_identity/`, except D7's transition in `age.py`;
    - any `apps/` path other than `apps/mobile/src/contracts/generated/`, and those files written other than by `npm run generate --prefix packages/contracts`. That includes a mobile source, test or fixture that would have to change for the Mobile checks job to pass;
    - `scripts/`, any other workflow job, the `Dockerfile`, an environment template, or the runtime scope's `requirements.in` and `requirements.lock`;
    - the CI policy (`docs/operations/ci-and-branch-policy.md`), which is the manager's;
  - **the dependency set** (D14): any new Python or npm package, or a changed pin;
  - **a design change:** the work needs any of these:
    - a `glow_chat` writer to behave differently;
    - an existing DTO or registry entry to change;
    - `record`, sign-up or the actor to change;
    - a role the oracle does not authorize;
  - **the area file:** a downloaded hash differs from D5's, or the derived table does not hold 925 areas;
  - **the seal:** the served runtime would import `glow_profiles` or any new module;
  - **the timeout:** the Database proof checks job cannot stay within its 30-minute timeout.
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished. A newer push cancels the earlier run's application jobs, and the run of record is lost. Push your records commit only after the run of record has finished. The workflow runs on pushes to `claude/**` and `ccr-**`; if your branch is named otherwise, say so in the report, since no run starts.
- **Network:**
  - **PyPI and the npm registry:** for `pip install --require-hashes` and `npm ci --ignore-scripts` from the existing locks only;
  - **`www2.census.gov`:** only to download `https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/2024_Gaz_cbsa_national.zip` once (D5). The manager saw it answer `200` with 46,177 bytes, last modified 30 August 2024;
  - **Docker Hub:** only to pull the PostgreSQL image the CI job pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`) for a local run (below).

  A page you cannot reach is named as unread, never filled from memory.
- **Downloaded files are untrusted data.** Put the zip in a new, empty directory outside the checkout, and extract it there. Keep your scripts elsewhere, and read the file with `python3 -I`, passing its path as an argument.
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
git merge-base --is-ancestor c864edd11dd16b0b5479170ce35158383be2b358 HEAD && echo "SV1 present"   # main's PR42 merge; must print "SV1 present"
git diff --name-only c864edd11dd16b0b5479170ce35158383be2b358 HEAD | grep -v -E '\.md$'           # against main: must print nothing
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/api proofs/postgres-ordering packages/contracts apps/mobile/src/contracts .github 'docs/testing/evidence/*sv2*' docs/architecture docs/testing/p11-deferred-acceptance.md   # must print nothing
test -e services/api/glow_profiles && echo "glow_profiles exists"                                  # must print nothing
ls services/api/glow_persistence/migrations | grep -E '^[0-9]{4}_'                                 # must list 0001 to 0004 only
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
- **The brief,** revision 3, whole.
- **The Dev Manager's reports,** whole. Their "Tried" lists and corrections are cases your tests should cover:
  - DM-52: `docs/continuity/dev-manager/reviews/2026-11-10-dm-52-sv2-brief.md`;
  - Nathan's answers in its session: `…/2026-11-10-nathan-answers-dm-52.md`;
  - DM-53: `…/2026-11-10-dm-53-sv2-stage-a-paths.md`.
- **Nathan's directions:** OD-60 and OD-61 in `docs/continuity/owner-directions.md`.
- **The location's facts:** `docs/testing/evidence/2026-11-10-od-60-matrix-recheck.md`.
- **The contract:**
  - `packages/contracts/production/flows-v1.json`, `gapp-api-v1.schema.json` and `openapi.json`;
  - `packages/contracts/transition_contract.py` (`authorized` and the roles it knows);
  - `packages/contracts/tests/`, and `scripts/generate.mjs` (read only);
  - `docs/architecture/production-contracts.md`: the flow index, F02 to F06, "Compound actions and model projections", and its list of trusted test prerequisites.
- **The data model:** `docs/architecture/data-model.md`, its rows for the profile, preferences, consent, the age state, the birth input and the mapping, its unit-of-work table and its outbox event table.
- **The code you build beside** (read only):
  - `services/api/glow_chat/contact.py`: `_run`, `_lock`, `_bump_eligibility`, `_event`, `_contact_state_checks`, `pause_profile`, `resume_profile`, `restrict_profile`, `_set_profile`, `accept_consent`, `withdraw_consent`, `_decide_consent`;
  - `services/api/glow_chat/reads.py`, `_caller_transaction_open` and `_run`;
  - `services/api/glow_identity/`: `authentication.py` (the actor), `revocation.py` (`require_no_transaction`), `age.py`, `urls.py` and `conf.py`;
  - `services/api/glow_domain/identity.py`;
  - `services/api/glow_persistence/models.py`, whole;
  - `services/api/tests/test_identity_sealed_runtime.py` and `test_model_definitions.py`.
- **P04's fixture rules,** read only: `apps/mobile/src/onboarding/store.ts` (`setAdultDate`, `setConsent`) and `apps/mobile/src/profiles/policy.ts`.
- **SV1:** its brief, `docs/planning/sv1-identity.md` (D2 to D10), and its record, `docs/testing/evidence/2026-11-09-sv1-identity.md`.
- **The proof:**
  - `proofs/postgres-ordering`: its settings, `environment`, `marker`, `identity_settings.py`, `identity_suite.py`, `identity_support.py` and `identity_cases.py`;
  - the Database proof checks job in `.github/workflows/foundation.yml`, whole.
- **The plans:**
  - the P06.DB brief's D1 to D6;
  - the P11 plan's DB04, DB07, DB08 and DB10 rows, and "From SV1";
  - `docs/operations/ci-and-branch-policy.md`'s Database proof checks paragraph (manager-owned: read it, do not change it).

**Facts from the code that the design relies on:**
- **SV2's operations nest `glow_chat`'s writers on purpose** (D6, D9; DM-52). Each takes the account row lock first, then calls the writer, whose own transaction becomes a savepoint, and rolls everything back on any result other than `applied` or `no_change`.
- **Two helpers refuse to run inside an open transaction,** so call neither from within SV2's:
  - `glow_chat`'s reads (`reads.py`, `_caller_transaction_open`);
  - SV1's `require_no_transaction` (`revocation.py`).
  - Django's `TestCase` opens a transaction, so a test that needs either uses the proof or a `TransactionTestCase`.
- **`OrmAgeAssurance.record` refuses an existing row by design.** D7 adds one transition beside it, and `record` stays as it is.
- **`EngineIdentity.adapter_version` is required, even for a pending row.** SV2 creates no `EngineIdentity` row (D8, as DM-53 wrote it).

## 3. What to do

1. **The area table** (D5).
   - Download the zip once (Network, above), and check its SHA-256 against D5's (`0ec21c5d…`).
   - Extract it, and check `2024_Gaz_cbsa_national.txt`'s SHA-256 against D5's (`31b28582…`).
   - Derive the committed table (area ID, name, internal point) by a deterministic step that lives in the owned paths and is recorded. The step drops the 10 Puerto Rico areas and leaves 925.
   - Record the three hashes: the zip's, the text file's and the derived file's. A test checks the derived file's hash and its 925 rows.
   - Nothing is fetched at migration, test or run time. If a hash differs, stop.
2. **Outcome items 1 to 6, with their routes,** in the brief's order. Each comes with its tests, and every test comes with its reversal (D15): a temporary edit that must make the test fail, run and then undone. Record the edit and the failing output. Make at least these reversals, each named in the record:
   - **D2:**
     - a publication that crosses a fixed limit is written anyway;
     - `StaffAudit` or `policy_published` is not written;
     - the pointer is read without its lock;
     - a retired value is refused for its holder;
   - **D3:**
     - "all" stored as the current list: a value the console adds is then missing;
     - "not stated" in a narrowed set;
     - a sensitive field, its own words or a narrowed sensitive set saved without the sensitive-fields consent;
     - an own value outside its pick limit accepted;
   - **D4:** a minimum below 18 accepted;
   - **D5:**
     - the coordinates stored, logged, returned or put in the outbox, one reversal each;
     - a coordinate in an error or validation message, an exception's text, a URL, a query string or a header;
     - the phone-location query setting the area;
     - a distance returned;
   - **D6:**
     - the version check removed: an old consent version accepted;
     - the purpose filter removed: a `sensitive_profile` decision satisfies, or revokes, onboarding consent;
     - the withdrawal leaving the two fields, orientation's own words, the narrowed sets or the commands' idempotency records;
     - `accept_consent` called before the account lock;
   - **D7:**
     - the transition without the account row lock, or without the eligibility bump;
     - a failing date stored;
     - a failing rerun leaving the date, the state or a `visible` profile;
     - a new eligibility date leaving the current birth input current;
   - **D8:**
     - a birth input with `time_precision` `unknown` accepted;
     - a new revision leaving the mapping `resolved`, or pointing at the old revision;
     - completion accepting a resolved mapping that points at an old revision;
   - **D9:**
     - resume without the completion check;
     - completion read before the account lock: a withdrawal while a completion waits is not seen;
     - a removal the member or staff is entitled to make refused instead of demoting;
     - a required value cleared instead of refused;
   - **D17:**
     - an unkeyed digest, reproducible from its command;
     - an extra field in a response;
     - another member's object returned;
   - **D18:**
     - a staff approval accepted while the setting is off;
     - a staff approval standing in for consent or the adult check;
     - a member route reaching a staff operation;
     - switching the setting off removing past approvals;
   - **D13:** the runtime importing `glow_profiles`: the sealed-runtime test fails;
   - **the log capture:** a coordinate, a birth date or time, an own-words value or a sensitive field logged in one path.
3. **The contract** (D11, with DM-53's words; Owned paths):
   - the new DTOs in the production schema;
   - their `openapi.json` components;
   - their corpus cases;
   - their flow-registry entries, as D11's "The flow registry" lists them, each with an allowed and a forbidden example in `tests/test_transition_contract.py`. F05 stays as it is;
   - the `staff_approval` prerequisite in `production-contracts.md`'s list;
   - a README section for SV2's additions.

   Then regenerate with `npm run generate --prefix packages/contracts`, never by hand. Run it a second time and confirm that `git status` shows no further change. Record which generated files changed: `gapp-api-v1.ts`, `validators.js` and `validators.d.ts` are expected, and `gapp-dev-v1.ts` is not.
4. **The local checks:**
   - **API,** in `services/api`: `python3.12 -m venv .venv`, then `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`. Then, with `GLOW_ENV=test`: `manage.py check`, `manage.py test tests --verbosity 2`, `smoke.py`, `ruff check .`, `ruff format --check .`, `mypy` and `python -m glow_persistence.static_check`;
   - **the contracts,** in `packages/contracts`: `npm ci --ignore-scripts`, then `npm run check`, then the Python contract tests (`PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests -v` from `services/api`, as CI runs them);
   - **the mobile app,** in `apps/mobile`: `npm ci --ignore-scripts`, then `npm run check` (its typecheck, lint and tests), with the regenerated outputs and no other change. Its export and rendered checks are CI's; `playwright install` is never run here;
   - **the proof,** in `proofs/postgres-ordering`: its venv and hash-locked install, its offline tests under `env -i`, Ruff and mypy;
   - **a local database run,** if Docker allows it under D4's conditions: iteration, not evidence.
5. **The run of record.**
   - Commit and push your code. The Foundation workflow runs on your branch's pushes. Wait for the run to finish (the push rule above).
   - Read it with your GitHub tools:
     - every job's conclusion, and the gate's line (`Application checks passed`);
     - the API test count;
     - the ordering, identity and profile suites' results;
     - the profile phase's duration, against the job's 30-minute timeout;
     - the Mobile checks job's contract check, typecheck, tests, export and rendered checks;
     - whether a toolchain retry fired;
     - that no secret and no coordinate appears in the job's log.
   - The run of record is the one on your last code commit. If it fails, stop and report the failing job and its log lines. Do not re-run it, and push no fix without saying so in the report.
6. **The records** the brief owns, for Stage A's parts:
   - the data model's profile, preferences, consent, age state and identity verification rows, rewritten as built;
   - the contract document's F02 to F06 index rows, kept in step with the registry by hand, and their server mapping. F03's says the server requires a birth time (D8);
   - a note in `profiles-preferences-fixtures.md` that the server exists, sealed;
   - the P11 plan's partial evidence for DB04, DB07, DB08 and DB10.

   Change no other section of those files.

## 4. The record

Write `docs/testing/evidence/<today's date>-sv2-profiles-media.md`, under `## Stage A`:
- the start gate's results, the environment check (names only) and the toolchain versions;
- the area file: its source URL, the three hashes, the derivation step and the row count;
- a table with one row per Outcome item and acceptance check in Stage A: the files, the test, the reversal and its failing output;
- the contract: the new DTOs, the registry entries with their examples, and the generated files that changed;
- **the threat model's inputs:**
  - every route and its refusals, and who may call it;
  - every staff operation, and how its subject reaches it;
  - every stored value that is private, sensitive or derived from the phone's location, with where it lives and what removes it;
  - every setting and fixed limit;
  - each writer's locks, in order;
  - each event and what it carries;
  - each with its test;
- every command you ran, with its result line, with local database runs listed as iteration, not evidence;
- the run of record: its ID, each job's result, the counts, the profile phase's duration, and whether a retry fired;
- what you could not run, and why.

Commit each logical step with a clear message ending in the session's attribution lines. Push your records commit only after the run of record has finished. Confirm that `git status` is clean, and that `git diff --name-only <START_SHA> HEAD` lists only your owned paths.

## 5. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch, your code head and records head;
- the start gate's and the environment check's results;
- the area file's source, hashes and row count;
- for each Outcome item: what changed, its tests, and each reversal's result;
- the contract: the DTOs, the registry entries, and the generated files that changed;
- each local check's result, and whether a local database run was used;
- the run of record: its ID, every job, the gate's line, the counts, the profile phase's duration and whether a retry fired;
- anything that met the stop rule, every deviation from the brief, and what you could not run.

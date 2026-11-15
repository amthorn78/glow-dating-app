# SV3 Stage B prompt — like and pass, the mutual match, unmatch and block, resurfacing and undo, and the row locks the suites send, proven on disposable PostgreSQL

- **Owner:** App Manager 11. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 15 November 2026.**
- **Durable brief:** [SV3 — The eligibility, discovery and interactions slice](../planning/sv3-eligibility-discovery-interactions.md), revision 14, with its section "Stage B: interactions (DM-71)".
- **Where the result goes:**
  - the session's changes in Stage B's owned paths, and its record, a new section `## Stage B (interactions)` at the end of `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md`, on its own branch;
  - the run of record: the Foundation run on its last code commit, with the discovery phase;
  - the manager adds its verification to the record, and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 2.68 (confidence 0.65); rung probabilities low 0.00, medium 0.03, high 0.36, extra high 0.51, max 0.09, ultracode 0.01. Model probabilities Fable 5.1 0.07, Opus 5.5 0.89, Sonnet 5.5 0.04, Haiku 5.5 0.00 (confidence 0.85). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.002, Fable 5.1 at high 0.025, Fable 5.1 at extra high 0.036, Fable 5.1 at max 0.006, Fable 5.1 at ultracode 0.001, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.027, Opus 5.5 at high 0.320, Opus 5.5 at extra high 0.454, Opus 5.5 at max 0.080, Opus 5.5 at ultracode 0.009, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.001, Sonnet 5.5 at high 0.014, Sonnet 5.5 at extra high 0.020, Sonnet 5.5 at max 0.004, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Flags: boundary between high and extra high. Sent 2026-11-15T03:46:21Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs.
  - The brief's revision 14 applies DM-71's CC1 to CC4 and DM-72's DD1 to DD5 as written; DM-72 sets this prompt's place in the sequence: from B0's merge commit, with Stage B's section's four items and DD5's stop sentence (DM-72 section 7).
  - The brief's review plan: the prompts need no read of their own, since they authorize no credential and no live action. This prompt authorizes no credential use and no live provider action. The suites' keys and the database password are generated for one run and destroyed with it.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed: the chat side's rows are written through `glow_chat`'s adapter, with no provider call.
- **It runs alone** (OD-29). Then, in order:
  - the manager's verification;
  - Stage B's PR and Codex's review of its head;
  - an exact-head code and security review of Stage B's final code head, with a written threat model (the brief's "Review plan", Stage B's items, and whatever Stage B changes in Stage A's code);
  - Dev Manager 5's pre-merge read, at a named commit, of the CI policy's paragraph and the data model's and the contract's rewritten texts.
- **Deletion condition:** prune after Stage B's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch (AM11-21).

---

You are the **implementation session for SV3's Stage B**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What Stage B is.** You build who may contact whom, on Stage A's eligibility and discovery, SV1's actor, SV2's profile and `glow_chat`'s writers. Stage B is proven on a disposable PostgreSQL in CI and kept sealed from the served runtime until P11. It covers:
- like and pass: idempotent directional actions, rechecked under locks at commit (D9);
- the mutual match: reciprocal likes make one match on the one pair record, with one logical event, under both accounts' locks, through `glow_chat`'s new `activate_reciprocal` (D10, option (a));
- unmatch and block, through `glow_chat`'s existing writers, unchanged (D11);
- resurfacing and undo behind their settings, off at launch; rematch refused by the new fixed limit `rematch_not_built` (D12);
- D13's additions for these routes (undo's command DTO, and the outcome code and projection state it needs);
- D14's Stage B cases (DB05, DB10) and the record of the row locks the suites send (acceptance check 15);
- the four items of the brief's "Stage B: interactions (DM-71)": the probe's reach, D14's reach, `VIEWER`'s unused `distance_choice`, and B0's test hardening.

There is no provider, deployed URL, real member, HDE call or stored credential.

**The brief, `docs/planning/sv3-eligibility-discovery-interactions.md`, revision 14, is the specification.** Stage B builds, in its section's words:
- Outcome items 4 to 7 and their routes, with items 8 to 11 for those parts;
- D9 to D12, D13's additions for them, D14's Stage B cases with the record of the row locks the suites send, and D15 to D19 for Stage B's code;
- acceptance checks 7 to 12 and 15, with 13 and 14 for its own code;
- the section's items 1 to 4.

Much of its text is the Dev Manager's words (DM-60, DM-68, DM-70, DM-71, DM-72), checked against the code. Follow them exactly. Where this prompt summarizes the brief, the brief wins.

**What came before.**
- **Stage A** (PR45, merged at `8d83474`, with corrections C1 to C5) built eligibility and discovery in `services/api/glow_discovery`: the pair read, the two-way rule, age and distance, recommended then broader pages with batches and cursors, the page route and the card's additive DTO, and the discovery suite on the fourth disposable database. Its selection and recheck already exclude a candidate the viewer has liked or passed, and the other member of any pair with a `Match` row, from rows its tests seed; no Stage A code writes them. All of Stage A's account locks are `FOR NO KEY UPDATE` (DM-61), and its proof holds a static scan of explicit account locks, whose rules are frozen (DM-68), and `pages.one_snapshot_statements`.
- **B0** (PR46, merged at `947576d`) changed only the proof's tooling: a bound on the lock scan's receiver rule (DM-71), its docstrings and pinning tests, T3's date rule narrowed, the database search's offline test. The scan's output on the tree is unchanged.
- **Every later review of SV3 has the five correction classes** of the brief's "C4's review, and how the scan's line ends", class 3 as BB1 words it and class 5 as DD1 words it. Stage B's review is the full exact-head review with a threat model; the classes govern the lock scan and the write check.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 11. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only the brief's "Owned paths (the sessions)", for Stage B's parts. Among them:
    - `services/api/glow_discovery/**`: the interaction operations, their views and URL configuration, beside Stage A's code; any change to Stage A's code is named in the report;
    - `services/api/glow_chat/contact.py`: under D10 (a) only, the new `activate_reciprocal` and its tests; every existing function and method unchanged;
    - `services/api/glow_domain/profile_settings.py`: the fixed limit `rematch_not_built` only (D12; DM-60);
    - `services/api/glow_persistence/models.py` and new migrations after `0010`: only the indexes and fields D9 to D12 need, each named in the report;
    - the contract's files, for D13's additions only, and the generated outputs only as `npm run generate --prefix packages/contracts` writes them;
    - `proofs/postgres-ordering/**`: the discovery suite, its settings, tests and locks; the four suites' runners, for D14's record of the row locks they send and for the guards DM-71 allows only; and `tests/test_profile_offline.py`, for the two subtests of B0's delta re-review's F5 only (DD2);
    - `.github/workflows/foundation.yml`: the Database proof checks job's steps only;
    - the records the brief names (item 6 below), and the evidence record;
  - **the lock scan's rules and B0's bound are not yours** (DM-68's freeze): no change to a rule of `account_lock_scan.py`. D14's record is a separate check, not a scan rule;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule** (the brief's "The stop rule (Stage B)", with its own stops). Stop and report, with no further change, if any of these holds:
  - **D14:** a statement the code sent before Stage B fails D14's check of the row locks the suites send;
  - **D16:** any new Python or npm package, or a changed pin;
  - **an owned path:** the work needs a path outside Stage B's owned paths. That includes:
    - `services/api/glow_api/` (the seal);
    - `services/api/glow_identity/` and `services/api/glow_profiles/`, which you use unchanged;
    - in `services/api/glow_chat/`, anything but `activate_reciprocal` and its tests;
    - any `apps/` path other than `apps/mobile/src/contracts/generated/`, and those files written other than by `npm run generate`; a mobile source, test or fixture that would have to change for the Mobile checks job to pass;
    - `scripts/`, any other workflow job, the `Dockerfile`, an environment template, or the runtime scope's `requirements.in` and `requirements.lock`;
    - the CI policy (`docs/operations/ci-and-branch-policy.md`), which is the manager's;
  - **D10 (a):** any change to an existing writer in `glow_chat`, or an import of `glow_discovery` from `glow_chat`;
  - **DM-68's freeze:** a change to the lock scan's rules or to B0's bound;
  - **DM-71's guard condition:** a guard that would refuse Django's own use of the driver's connection (creating cursors, the health check's `SELECT 1`, configuring a new connection);
  - **a design change:** an existing DTO or an existing flow-registry entry would have to change (D13: additions only, each as a new entry);
  - **the seal:** the served runtime would import `glow_discovery` or any new module, or select a fixture compatibility provider;
  - **the timeout:** the Database proof checks job cannot stay within its 30-minute timeout (D14); it is not raised;
  - **an earlier test** (DD5): an earlier test that one of Stage B's items is expected to change is named here, with the reason; any other earlier test that no longer passes is a stop. **By the manager's reading at `<START_SHA>`, no earlier test is expected to change:**
    - `rematch_not_built`: SV2's tests (`services/api/tests/test_profile_settings.py`, `test_profile_media.py`) check that each refusal they name is a member of `FIXED_LIMITS`, and none publishes `discovery.rematch` with `enabled` on; the profile suite's fixed-limit case (`profile_cases.py`) names its own refusals only;
    - `VIEWER`'s column (item 3): the proof refers to `predicates.VIEWER` by the object, not its text (`discovery_cases.listed`, `tests/test_discovery_offline.py`), so the list follows it;
    - F08's like over a pass: the registry's entry requires the policy `A05` in its context, and `test_transition_contract.py`'s case without it stays `policy_unresolved`; D13 adds entries and changes none;
    - Stage A's tests that seed `DirectionalInteraction` and `Match` rows in setup stay as they are: Stage B's writers write the same rows.

    If an earlier test fails, report which and why; do not change or delete it.
  - In each case, report it; do not narrow the brief's words to pass it. A reversal's or a mutant's temporary edit of code is allowed, and must be undone.
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished. A newer push cancels the earlier run's application jobs, and the run of record is lost. Push your records commit only after the run of record has finished. The workflow runs on pushes to `claude/**` and `ccr-**`; if your branch is named otherwise, say so in the report, since no run starts.
  - **If GitHub never starts the run** (it stays `queued` with no jobs for 30 minutes), do not re-run it, dispatch it, push an empty commit, or ask anyone to re-run it (OD-58). Record it, push your records commit, and report. The manager's PR run is then the run of record (the manager workflow, step 5).
  - **If the run fails,** stop and report the failing job and its log lines. Do not re-run it, and push no fix without saying so in the report.
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
  - read, print or use the value of any `AWS_*` variable, or name one in a command (section 1);
  - make test data that looks real. Accounts, emails, names, birth facts, places and coordinates are synthetic and obviously so (`@example.invalid` addresses);
  - call any provider or HDE, send any email, or run any command in `proofs/stream-chat/`;
  - connect to any database but a throwaway one you started under D4's conditions. Run `migrate` or `makemigrations` only through the proof's own commands against such a database, or under the static registry's dummy settings;
  - connect to HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script;
  - weaken or delete a test to make the suite pass.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:** `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` or `PG*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG)'` prints names only. If any is present, stop and report.
3. **Three AWS names are expected:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_CA_BUNDLE`. `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values, and pass none to a command.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
5. **The toolchain:** CPython 3.12.14 as `python3.12` (`services/api/.python-version`); Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, first on PATH. Record `python3.12 --version`, `node --version`, `npm --version` and `docker --version`.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API). The proxy and CA variables pass by reference, never printed (`docs/operations/local-development.md`).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git merge-base --is-ancestor 947576d98b7c3103455a670c20fdba2734ff5053 HEAD && echo "B0's merge present"   # PR46's merge into main; must print the line
git diff --quiet 947576d98b7c3103455a670c20fdba2734ff5053 HEAD -- . ':!*.md' && echo "main's code"   # must print the line
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/api proofs/postgres-ordering packages/contracts apps/mobile/src/contracts .github 'docs/testing/evidence/*sv3*' docs/architecture docs/testing/p11-deferred-acceptance.md   # must print nothing
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md | grep -c -E '^## Stage B \(interactions\)'   # must print 0
ls services/api/glow_persistence/migrations | grep -E '^[0-9]{4}_'   # must list 0001 to 0010 only
```

If a check fails, stop and report. The prompt is stale if:
- `<START_SHA>` is not on the live manager branch;
- the live branch has changed an owned path since it;
- or the record already holds "Stage B (interactions)".

**Then read, completely:**
- **The instructions:**
  - root `AGENTS.md` and `CLAUDE.md`;
  - `services/api/README.md`, `proofs/postgres-ordering/README.md` and `packages/contracts/README.md`;
  - `apps/mobile/AGENTS.md`: you change only its generated contracts.
- **The brief,** revision 14, whole.
- **The Dev Manager's reports** that shaped Stage B, in `docs/continuity/dev-manager/reviews/`: DM-60 (whole; its sections on D9 to D12 and the match's serialization), DM-68 (the termination rule and D14's record), DM-70 (sections 4.3 and 9: D14's reach), DM-71 (sections 3.1, 3.3 and 9: Stage B's shape, the guards' three conditions) and DM-72 (sections 4.1 and 4.2: B0's test hardening, and DD5).
- **Nathan's directions:** OD-12, OD-55, OD-60 (its R: resurfacing, undo and rematch) and OD-61 in `docs/continuity/owner-directions.md`.
- **The contract:**
  - `packages/contracts/production/flows-v1.json` (F07 to F10 and F13), `gapp-api-v1.schema.json` and `openapi.json`;
  - `packages/contracts/transition_contract.py` (`transition`, `authorized` and the roles and policies it knows);
  - `packages/contracts/tests/`, and `scripts/generate.mjs` (read only);
  - `docs/architecture/production-contracts.md`: the flow index, "Pagination, idempotency and stale state", "Policy boundaries and deliberately unavailable operations", "P05.3 internal interaction result and identity bridge", "Compound actions and model projections", and SV3's additions.
- **The data model:** `docs/architecture/data-model.md`, its rows for interactions, blocks, matches, batches and entries, the chat binding and identity, and the settings; its unit-of-work table and its outbox event table.
- **P05's behaviour,** which the server must match: `docs/architecture/interactions-fixtures.md` and `reciprocal-eligibility-fixtures.md`; and `services/api/glow_domain/interactions.py`, `eligibility.py`, `trusted_eligibility.py` and `ports.py`.
- **The code you build beside** (read only, except where your owned paths say):
  - `services/api/glow_discovery/`, whole: Stage A's pages, predicates, policy, keys and views;
  - `services/api/glow_chat/contact.py`, whole: `_run`, `_lock`, `_contact_state_checks`, `activate_match` (its lock order and probe points, which `activate_reciprocal` takes), `block`, `unblock`, `unmatch`; and `glow_chat`'s tests;
  - `services/api/glow_profiles/`: `settings_store.py` (`read_shared`, the pointer order, D19), `idempotency.py` (the keyed digests and replay), `operations.py` (how SV2's operations nest `glow_chat`'s writers), `views.py`, `urls.py` and `contract.py`;
  - `services/api/glow_identity/authentication.py` (the actor) and `revocation.py`;
  - `services/api/glow_domain/profile_settings.py`, whole;
  - `services/api/glow_persistence/models.py`, whole;
  - `services/api/tests/test_profiles_sealed_runtime.py`, `test_model_definitions.py`, and Stage A's discovery tests.
- **The record:** `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md`: "Stage A" (its threat model's inputs), "Stage A, correction C1" (the account locks and the page-creation cases), "Delta re-review of C4" and "Delta re-review of C5" (the write check's reach and F5's forms), "Stage B, B0" and "Delta re-review of B0" (F5 and F6).
- **The proof:**
  - `proofs/postgres-ordering`: its settings, `environment`, `marker`, the discovery suite's files (`discovery_settings.py`, `discovery_suite.py`, `discovery_support.py`, `discovery_cases.py`, `discovery_scan.py`), the other three suites' runners, `account_lock_scan.py` (read only), `profile_support.py` and `tests/test_profile_offline.py`'s `RunClockTests` and `NarrowedClockRuleTests`;
  - the Database proof checks job in `.github/workflows/foundation.yml`, whole.
- **The plans:**
  - the P06.DB brief's D1 to D6;
  - the P11 plan's DB04, DB05, DB10 and DB11 rows, and its SV1, SV2 and SV3 entries;
  - `docs/operations/ci-and-branch-policy.md`'s Database proof checks paragraph (manager-owned: read it, do not change it).

**Facts from the code that the design relies on:**
- **Stage A's account locks are `FOR NO KEY UPDATE`,** and every SV3 writer's must be too (D2; DM-61); the lock scan reads them, and D14's record checks what the suites send.
- **A block bumps only its actor's `blocks_version`** (`glow_chat`'s `block`), so the other member's batch stays fresh; Stage A's page recheck reads `Block` rows in both directions for every entry, and D9's recheck at commit must too.
- **SV2's settings store takes pointers in name order** (D19): every Stage B transaction that reads a setting takes all its pointers in its first `read_shared` call.
- **Two helpers refuse to run inside an open transaction:** `glow_chat`'s reads (`reads.py`, `_caller_transaction_open`) and SV1's `require_no_transaction` (`revocation.py`). Django's `TestCase` opens a transaction, so a test that needs either uses the proof or a `TransactionTestCase`.
- **F08's like over the actor's own pass** requires the policy `A05` (OD-60's R) in the transition's context; D12's resurfacing is what returns the candidate to the actor's batch (D9).
- **`activate_match`'s docstring** names the precondition `activate_reciprocal` checks under its locks: *"reciprocal likes and current two-person eligibility are checked by the activation P11 wires (F09), under the same locks"* (D10).

## 3. What to do

1. **Outcome items 4 to 7, with their routes,** in the brief's order. Each comes with its tests, and every test comes with its reversal (D18): a temporary edit that must make the test fail, run and then undone. Record the edit and the failing output. Make at least these reversals, each named in the record:
   - **D9 (check 7):**
     - an identical repeat not replayed, and a changed payload with the same key accepted;
     - each of a stale batch, a wrong batch, a target outside the batch and an ineligible target accepted, or refused with something written;
     - the recheck at commit skipped, or read outside the locks;
     - a committed like or pass leaving its batch fresh (F07's `invalidate`), or a new command naming a consumed batch accepted;
     - the target shown an unreciprocated like, in any response or page;
     - a pass over a like accepted;
   - **D10 (check 8):**
     - the match created without the two `liked` rows, or without the account locks in `glow_chat`'s order;
     - a second `Match` row, or a second `match_activated` event, from reciprocal likes in either order;
     - a route that creates a match;
     - `activate_reciprocal` accepting what `activate_match` refuses, or a missing `liked` row in either direction;
   - **DB10 (check 9):** each change of D14's list (a block, an unblock, a pause, a consent withdrawal, a preference change, a settings publication) committed while a like waits on its locks, unseen by the like;
   - **D11 (check 10):**
     - unmatch or block not through `glow_chat`'s writer;
     - a send accepted after each;
     - block refused after unmatch or while paused;
     - unblock restoring a match or a send;
     - the blocked member able to learn the direction;
   - **D12 (check 11):**
     - resurfacing or undo working while off;
     - each on with a waiting period, working before it ends;
     - undo deleting and recreating the directional row, so an expected version from before it matches;
     - a publication of `discovery.rematch` with `enabled` on accepted, or writing something;
     - after an unmatch, either member in the other's pages, or a like making a second match or reactivating the first;
   - **ownership (check 12):** each route accepting an unauthenticated request, another member's match or batch, or a stale version;
   - **D15:** the runtime importing a new module: the sealed-runtime test fails;
   - **the log capture (check 13):** a private value of another member, a birth date, a coordinate, a distance or a "show me" set logged in one path.
2. **D10's writer, `activate_reciprocal`** (D10 (a); the review plan): `activate_match`'s body with one check added under its account locks, the two `liked` rows; the same rows and events (the identity events and the one `match_activated` event), the same lock order and probe points; called only from the like, inside its transaction, after its recheck of D3 to D5 for the pair under the same locks. `glow_chat` imports nothing from `glow_discovery`. Record, by AST, that every existing function and method in `glow_chat/contact.py` is unchanged from `main`'s, and that `glow_chat`'s existing tests are unchanged and pass.
3. **The contract** (D13; owned paths): undo's command DTO, and the outcome code and projection state it needs, each as an added DTO or value; their `openapi.json` components (no paths); their corpus cases; their flow-registry entries (F08's undo, and any transition Stage B's writers make that the registry lacks), each as a new entry with an allowed and a forbidden example in `tests/test_transition_contract.py`; no existing DTO or entry changes; and the README's SV3 section. Then regenerate with `npm run generate --prefix packages/contracts`, never by hand; run it a second time and confirm that `git status` shows no further change. Record which generated files changed.
4. **The proof** (D14's Stage B cases, and the section's items):
   - **DB05:** simultaneous reciprocal likes from separate connections, in both arrival orders, give one match and one `match_activated` event; repeated likes with fresh keys give one row;
   - **DB10:** each change of D14's list, committed while a like waits on its locks, is seen by the like;
   - **D14's record of the row locks the suites send** (check 15; DM-68): in each of the four suites, an execute wrapper on every connection it opens (those its concurrency cases open in other threads included) records each statement's text, and the suite fails if a statement takes a writer's row lock `FOR UPDATE`, not `FOR NO KEY UPDATE`, and names `glow_persistence_appaccount`, unless its lock clause is `FOR UPDATE OF` names none of which is that table or an alias the statement gives it; a lock clause it cannot read that way fails too. It runs before the suite's verdict, and prints counts and each failing statement's text, never a parameter. Its reversal: one account lock in `services/api` taken without `no_key=True` fails every suite that runs it;
   - **item 1, the probe's reach** (DM-69): with D14's record, `pages.one_snapshot_statements` checks that, while a page runs, no statement goes out on another connection or from another thread. Its reversal: C4's delta re-review's planted statement, an `UPDATE` sent from a thread on its own connection inside the page by cursor's transaction, fails the case. The README's limit for it is rewritten to what remains;
   - **item 2, D14's reach** (DM-70, BB3): plant F5's forms against the write check and D14's record: psycopg's `stream` and `copy` through Django's cursor, the driver's own connection (`connection.connection`), and a lock taken inside a database function. For each, close the gap or state it in the README's "Limits" with its planted example. A close may be a proof-only guard, on DM-71's three conditions: it acts only in the suites' processes, and nothing in `services/api` changes for it; it refuses the driver cursor's methods that Django's cursor passes through unwrapped when a case calls them, with a reversal; and it never refuses Django's own use of the driver's connection. A lock inside a database function may be closed by a check, with its reversal, that the migrated database defines no function of its own;
   - **item 3:** `VIEWER`'s unused `distance_choice` removed from `predicates.VIEWER`; the proof's list of statements follows it;
   - **item 4, B0's test hardening** (DM-72): F5's two subtests, the `NARROWED_HITS` entries `('headers', 'Expires: Thu, 12 Nov 2026 04:13:27')` and `('headers', 'expires: Thu, 12 Nov 2026 04:13:27 GMT')`, each a hit, each failing against its mutant (`(?: GMT)?$`, `re.IGNORECASE`); and F6's direct subtest, a planted form whose verdict or count of states a memo keyed on `len(seen)` changes, failing against that mutant;
   - the Database proof checks job's steps, only as D14's record and the new cases need them;
   - the discovery phase's duration, against the job's 30 minutes.
5. **The local checks:**
   - **API,** in `services/api`: `python3.12 -m venv .venv`, then `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`. Then, with `GLOW_ENV=test`: `manage.py check`, `manage.py test tests --verbosity 2`, `smoke.py`, `ruff check .`, `ruff format --check .`, `mypy` and `python -m glow_persistence.static_check`;
   - **the contracts,** in `packages/contracts`: `npm ci --ignore-scripts`, then `npm run check`, then the Python contract tests (`PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests -v` from `services/api`, as CI runs them);
   - **the mobile app,** in `apps/mobile`: `npm ci --ignore-scripts`, then `npm run check`, with the regenerated outputs and no other change;
   - **the proof,** in `proofs/postgres-ordering`: its venv and hash-locked install, its offline tests under `env -i`, Ruff, `ruff format --check` and mypy; and the lock scan, `python -m glow_ordering_proof.account_lock_scan`, with its counts and every new lock's verdict;
   - **a local database run,** if Docker allows it under D4's conditions: iteration, not evidence.
6. **The run of record.**
   - Commit and push your code. Wait for the Foundation run on your last code commit to finish (the push rule).
   - Read it with your GitHub tools:
     - every job's conclusion, and the gate's line (`Application checks passed`);
     - the API test count;
     - the ordering, identity, profile and discovery suites' results, D14's check in each with its counts, and each suite's value and secret scans;
     - the discovery phase's duration, against the job's 30-minute timeout;
     - the lock scan case's line;
     - the Mobile checks job's contract check, typecheck, tests, export and rendered checks;
     - whether a toolchain retry fired;
     - that no secret, coordinate or distance appears in the job's log.
7. **The records** the brief owns, for Stage B's parts:
   - the data model's interaction, block and match rows, rewritten as built, and the unit-of-work and outbox rows Stage B's writers add;
   - the contract document's F08 to F10 and F13 index rows, kept in step with the registry by hand, and their server mapping;
   - a note in `interactions-fixtures.md` that the server's interactions exist, sealed, as Stage A's note in `reciprocal-eligibility-fixtures.md` does for eligibility;
   - the P11 plan's partial evidence for DB04, DB05 and DB10, and Stage B's run of record in its SV3 entry;
   - the proof README: its SV3 paragraph (a sentence on what Stage B adds), and "Limits" for items 1 and 2.

   Change no other section of those files.

## 4. The record

Add a section `## Stage B (interactions)` at the end of `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md`:
- the start gate's results, the environment check (names only) and the toolchain versions;
- a table with one row per Outcome item, acceptance check and section item in Stage B: the files, the test, the reversal and its failing output;
- `activate_reciprocal`: its diff against `activate_match`, and the AST comparison of every existing function and method in `contact.py`;
- the contract: the new DTOs and values, the registry entries with their examples, and the generated files that changed;
- D14's record: its counts in each suite, its reversal, and each of item 2's forms with its close or stated limit and planted example;
- **the threat model's inputs:**
  - every route and its refusals, and who may call it;
  - each action's recheck at commit: its locks, their order, and the predicates it reads;
  - the match's uniqueness: the two likes' serialization, and the constraint behind it;
  - what each member can learn of the other's actions (an unreciprocated like, a block's direction), and what they cannot;
  - idempotency: the keys, the digests, replay before staleness;
  - each setting's gate (resurfacing, undo, rematch);
  - each with its test;
- every command you ran, with its result line, with local database runs listed as iteration, not evidence;
- the run of record: its ID, each job's result, the counts, D14's check in each suite, the discovery phase's duration, and whether a retry fired;
- every deviation from the brief, and what you could not run, and why.

Commit each logical step with a clear message ending in the session's attribution lines. Push your records commit only after the run of record has finished. Confirm that `git status` is clean, and that `git diff --name-only <START_SHA> HEAD` lists only your owned paths.

## 5. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch, your code head and records head;
- the start gate's and the environment check's results;
- for each Outcome item and section item: what changed, its tests, and each reversal's result;
- `activate_reciprocal` and the AST comparison;
- the contract: the DTOs and values, the registry entries, and the generated files that changed;
- D14's record in each suite, and item 2's forms;
- each local check's result, and whether a local database run was used;
- the run of record: its ID, every job, the gate's line, the counts, D14's check in each suite, the discovery phase's duration and whether a retry fired;
- any change to Stage A's code, named;
- anything that met the stop rule, every deviation from the brief, and what you could not run.

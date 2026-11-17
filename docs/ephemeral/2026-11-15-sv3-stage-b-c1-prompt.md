# SV3 Stage B, correction B-C1 prompt — the actor's own versions: one owner-only read, and the proof taking its versions as a client does

- **Owner:** App Manager 11. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 15 November 2026.**
- **Durable brief:** [SV3 — The eligibility, discovery and interactions slice](../planning/sv3-eligibility-discovery-interactions.md), revision 16, with its section "Stage B, correction B-C1 (Codex on PR47; DM-74)".
- **Where the result goes:**
  - the session's changes in B-C1's owned paths, and its record, a new section `## Stage B, correction B-C1` at the end of `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md`, on its own branch;
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification to the record, and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.10 (confidence 0.82); rung probabilities low 0.00, medium 0.08, high 0.74, extra high 0.17, max 0.01, ultracode 0.00. Model probabilities Fable 5.1 0.01, Opus 5.5 0.84, Sonnet 5.5 0.15, Haiku 5.5 0.00 (confidence 0.79). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.001, Fable 5.1 at high 0.007, Fable 5.1 at extra high 0.002, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.067, Opus 5.5 at high 0.622, Opus 5.5 at extra high 0.143, Opus 5.5 at max 0.008, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.012, Sonnet 5.5 at high 0.111, Sonnet 5.5 at extra high 0.026, Sonnet 5.5 at max 0.002, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-15T14:14:15Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs.
  - The brief's revision 16 applies DM-74's FF1 to FF6 as written; DM-74 sets this prompt's place in the sequence (DM-74 section 5) and needs no further read if they are applied as written.
  - The brief's review plan: the prompts need no read of their own, since they authorize no credential and no live action. This prompt authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Then, in order:
  - the manager's verification, and PR47's run and Codex's review of its head;
  - the exact-head code and security review of Stage B's code head `5d58993` and B-C1 together, with its threat model;
  - Dev Manager 5's pre-merge read.
- **Deletion condition:** prune after Stage B's PR (PR47) merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch (AM11-21).

---

You are the **implementation session for SV3 Stage B's correction B-C1**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What B-C1 is.** One correction to SV3's Stage B, before its exact-head review:
- **the finding** (Codex on PR47, P2; the evidence record, "PR47 and Codex on its head"): F08's like, pass and undo, and F13's block and unblock, compare `CommandMeta.expected_version` with the actor's own row, `0` for its absence. A client that has lost its own command answers, or a second device, has no read that returns that version, so it cannot act;
- **why now** (DM-74): a block after an unblock is reachable at launch with no setting. The removed block row carries a version above zero, and without it a member can never block that person again from a new device;
- **the fix:** one owner-only read of the actor's own directional row and own block (item 1), and the proof taking its versions as a client does (item 2).

B-C1 changes no model, migration, lock, version check, existing DTO, stale body, `glow_chat` writer, lock-scan rule or bound, workflow or dependency. There is no provider, deployed URL, real member, HDE call or stored credential.

**The brief, `docs/planning/sv3-eligibility-discovery-interactions.md`, revision 16, is the specification:** its section "Stage B, correction B-C1", with D13's "The actor's own versions" (FF1) and B-C1's owned paths (FF2). Its text is Dev Manager 5's words (DM-74), checked against the code. Follow them exactly. Where this prompt summarizes the brief, the brief wins.

**What came before.**
- **SV3's Stage A** (PR45, `8d83474`) and **B0** (PR46, `947576d`) are merged.
- **Stage B** (likes and passes, the mutual match, unmatch and block, resurfacing, undo and rematch's refusal, D14's record of the row locks the suites send) was built, verified and integrated: code head `5d58993`. Its run of record is 43686623299, all eight jobs passing, discovery 59/59, each suite's D14 record `PASS`.
- **PR47** carries it. Its runs on `622a4f4` passed all eight jobs. Codex's review of that head raised the finding above.
- **DM-74** ruled it fixed now, as B-C1, in shape (a1): one read, not a field on the card, since a blocked member is never on a card.
- **The exact-head review** comes after B-C1 and reads `5d58993` and B-C1 together.

**Facts from the code that the fix relies on** (at `5d58993`):
- **The version checks:**
  - `glow_discovery/interactions.py` line 307 (like and pass) compares `_expected(intent)` with `0 if row is None else int(row.version)` for the actor's directional row;
  - line 401 does the same for undo;
  - line 518 does it for block and unblock, with the actor's directional block.

  They stay as they are.
- **What answers carry a version today:** each command's answer: `_interaction_projection` (`InteractionOutcome`), the undo outcome, and `_block_projection` (`BlockOutcome`). Every stale cause answers one 409 `stale_version` body with no version (D8); that body stays.
- **The match read** (`read_match`, `GET api/v1/matches/<uuid:match_id>`) is the pattern for the new read: one transaction holding the actor's account row `FOR SHARE`, served `Cache-Control: no-store`, for the actor only, through SV1's `GlowActorAuthentication`.
- **The block's 404:** Stage B's block answers 404 `target_not_found` for a profile ID that does not exist, before its locks (line 506). It is for the exact-head review's threat model, not B-C1's to change (DM-74 section 3.4). The new read must not add a second such answer: it never answers 404 for a missing profile.
- **The proof's gap:** `proofs/postgres-ordering/glow_ordering_proof/interaction_cases.py`'s `_version()` reads the directional row through the ORM, so no case sends a version a client could not have.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 11. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - **write only B-C1's owned paths** (the brief's "Owned paths (the sessions)", "Correction B-C1 only", FF2):
    - in `services/api/glow_discovery/`: the own-versions read in `interactions.py`, `interaction_views.py`, `interaction_urls.py` and `contract.py`, and nothing else in them;
    - its tests in `services/api/tests/`;
    - D13's contract addition for it: the production schema, `openapi.json`'s DTOs (no paths), the corpus, `flows-v1.json`'s F08 and F13 entries, `packages/contracts/README.md` and the contract tests;
    - the generated outputs, only as `npm run generate --prefix packages/contracts` writes them;
    - in the proof: `interaction_cases.py`, and the discovery suite's case list, count and offline tests;
    - the contract document's F08 and F13 server mapping;
    - the proof README's SV3 paragraph;
    - the evidence record;
    - the P11 plan's SV3 entry, its runs of record only.

    Nothing else changes in B-C1.
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule** (the brief's "The stop rule (B-C1)"). Stop and report, with no further change, if any of these holds:
  - B-C1 needs a change outside its owned paths;
  - it needs a change to any of these: a model, a migration, a lock, a version check, an existing DTO, D8's single stale body, a `glow_chat` writer, the lock scan's rules or B0's bound, the workflow, or a dependency;
  - the read cannot give the same answer for every profile the actor has no row with, whatever that profile's state;
  - a case other than those item 3 names changes its verdict;
  - **an earlier test** (DD5; the section's item 3): an earlier test that B-C1 is expected to change is named here, with its reason. Any other earlier test that no longer passes is a stop. Expected to change, each keeping what it protects:
    - the API's `test_the_page_route_and_stage_bs_action_routes_are_served_and_no_other` (`services/api/tests/test_discovery_offline.py`): the exact route set gains the read's route, with its view and its one method, `GET`, and still no other route;
    - the proof's `test_the_routes_are_the_apis` (`tests/test_discovery_offline.py`): `interaction_urls.py`'s exact routes gain the read's;
    - the discovery case `match.no_route_creates_a_match`: the exact routes the suite serves gain the read's (42), and still none takes a match intent;
    - the proof's `test_the_case_count_is_pinned`: re-pinned, with B-C1's cases named in order after Stage B's 19;
    - **the contract tests gain the DTO.** By the manager's reading at `<START_SHA>`, that means `packages/contracts/tests/test_transition_contract.py`'s Stage B registry test (the one pinning F08's lists and F07, F09, F10 and F13 as unchanged). F08's and F13's response lists and projection roles gain the read's DTO with its owner projection, and so do their request lists if the read adds a request DTO. F08's and F13's transitions, and F07, F09 and F10, stay pinned exactly as they are.

    **Not an earlier test changing, but its coverage, which item 1 requires:** `services/api/tests/test_interactions_sealed_runtime.py`'s `STAGE_B_ROUTES` and `STAGE_B_PATHS` (and the route prefixes it checks) gain the read's route and a path for it. That test passes without the change, since the runtime serves none of Stage B's routes; the change keeps D15's seal covering the new route.

    By the manager's reading at `<START_SHA>`, **no other earlier test is expected to change**:
    - no other test pins the routes `interaction_urls.py` serves;
    - the mobile app maps no response kind exhaustively, so a new DTO in `AppResponse` widens the generated types only (Stage B's undo outcome did the same);
    - B-C1 adds no `ApiError` code. A new one would change the Mobile checks job's exhaustive map (`apps/mobile/src/chat/client.test.ts`), a mobile test, which is a stop (the owned paths).

    If any other earlier test fails, report which and why; do not change or delete it.
  - In each case, report it; do not narrow the brief's words to pass it. A reversal's temporary edit of code is allowed, and must be undone.
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished; a newer push cancels the earlier run's application jobs. Push your records commit only after the run of record has finished. The workflow runs on pushes to `claude/**` and `ccr-**`; if your branch is named otherwise, say so in the report.
  - **If GitHub never starts the run** (it stays `queued` with no jobs for 30 minutes), do not re-run it, dispatch it, push an empty commit, or ask anyone to re-run it (OD-58). Record it, push your records commit, and report.
  - **If the run fails,** stop and report the failing job and its log lines. Do not re-run it, and push no fix without saying so in the report.
- **Network:**
  - PyPI and the npm registry, for `pip install --require-hashes` and `npm ci --ignore-scripts` from the existing locks only;
  - Docker Hub, only to pull the PostgreSQL image the CI job pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`) for a local run.

  A page you cannot reach is named as unread, never filled from memory.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions):
  - a throwaway PostgreSQL in Docker, from the CI job's pinned image, on loopback only;
  - a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present;
  - removed afterwards.

  Local passes are "iteration, not evidence"; the run of record is CI's.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, password, code, token, session key or signing key, in any form;
  - read, print or use the value of any `AWS_*` variable, or name one in a command (section 1);
  - make test data that looks real: accounts, emails, names, birth facts, places and coordinates are synthetic and obviously so (`@example.invalid` addresses);
  - call any provider or HDE, send any email, or run any command in `proofs/stream-chat/`;
  - connect to any database but a throwaway one you started under D4's conditions;
  - run `migrate` or `makemigrations` other than through the proof's own commands against such a database, or under the static registry's dummy settings;
  - connect to HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script;
  - weaken or delete a test to make the suite pass.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:** `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` or `PG*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG)'` prints names only. If any is present, stop and report.
3. **Three AWS names are expected:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_CA_BUNDLE`. `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values, and pass none to a command.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
5. **The toolchain:** CPython 3.12.14 as `python3.12`; Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, first on PATH. Record `python3.12 --version`, `node --version`, `npm --version` and `docker --version`.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git merge-base --is-ancestor <START_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"   # must print the line
git diff --quiet 5d58993389e1fafcbdece1338dbf9d83736132c6 HEAD -- . ':!*.md' && echo "Stage B's code"   # must print the line: the start's non-Markdown tree equals 5d58993's
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/api proofs/postgres-ordering packages/contracts apps/mobile/src/contracts .github 'docs/testing/evidence/*sv3*' docs/architecture docs/testing/p11-deferred-acceptance.md   # must print nothing
grep -c -F 'Status: brief, revision 16,' docs/planning/sv3-eligibility-discovery-interactions.md   # must print 1
grep -c -E '^## Stage B, correction B-C1' docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md   # must print 0
```

If a check fails, stop and report. The prompt is stale if:
- `<START_SHA>` is not on the live manager branch;
- the live branch has changed an owned path since it;
- or the record already holds "Stage B, correction B-C1".

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`, `proofs/postgres-ordering/README.md` and `packages/contracts/README.md`; `apps/mobile/AGENTS.md` (you change only its generated contracts);
- the brief, revision 16: D8, D9 to D13 (with "The actor's own versions"), D15, "Stage B: interactions (DM-71)" and "Stage B, correction B-C1", whole;
- DM-74's report, whole, in `docs/continuity/dev-manager/reviews/`;
- the evidence record: "Stage B (interactions)", "Manager verification of Stage B" and "PR47 and Codex on its head";
- Codex's thread on PR47 (https://github.com/amthorn78/glow-dating-app/pull/47#discussion_r4578551630), with your GitHub tools;
- the contract:
  - `packages/contracts/production/flows-v1.json` (F08 and F13);
  - `gapp-api-v1.schema.json`: `CommandMeta`, `InteractionOutcome`, `BlockOutcome`, `OwnedObjectRequest`, `MatchProjection`, undo's four DTOs and `AppResponse`;
  - `openapi.json`, the corpus, `transition_contract.py` (`read_projection`), and `tests/test_transition_contract.py`;
- `docs/architecture/production-contracts.md`: "Pagination, idempotency and stale state", the version rule, and the F08 and F13 server mapping; and `interactions-fixtures.md`'s "Version, digest and replay boundary";
- the code, whole:
  - `services/api/glow_discovery/interactions.py` (above all `_account_of_profile`, the like and pass, undo, block, `read_match`, `_interaction_projection` and `_block_projection`), `interaction_views.py`, `interaction_urls.py` and `contract.py`;
  - `services/api/tests/test_interactions_offline.py`, `test_interactions_sealed_runtime.py` and `test_discovery_offline.py`;
  - the proof's `interaction_cases.py`, `discovery_cases.py` (the plan), `discovery_urls.py` and `tests/test_discovery_offline.py`.

## 3. What to do

1. **The own-versions read** (the section's item 1; FF1). Build it as the section says:
   - **The route:** a `GET` route for a target profile ID (proposed `api/v1/interactions/<uuid:profile_id>`), for the actor only, through SV1's `GlowActorAuthentication`, served `Cache-Control: no-store`.
   - **The transaction:** one transaction holding the actor's account row `FOR SHARE`, as the match read does. It reads the actor's own directional row toward that profile's account, and the actor's own block of it.
   - **The answer,** a new DTO:
     - the profile ID as asked;
     - the directional row's state (`none`, `liked`, `passed` or `withdrawn`) and version;
     - the block's state (`none`, `active` or `removed`) and version;
     - each `none` and `0` where the actor has no row.
   - **Its answer depends only on the actor's own rows:**
     - where the actor has none, it is the same 200 body whether the profile exists or not and whatever its state, never a 404;
     - where the actor has a row, it is that row, whatever the other member's state;
     - no row whose actor is the other member is ever read.

   Its tests, each with its reversal (D18): a temporary edit that must make the test fail, run and then undone, with the edit and the failing output recorded. At least:
   - **each state and version** after a like, a pass, an undo, a resurfaced like, a block and an unblock;
   - **the alike cases, byte-identical:** for a profile with no row, a missing profile ID, and each of not visible, paused, restricted, removed, excluded and blocking the actor. Reversal: the missing profile answered 404, or the profile's state read;
   - **the other member's rows** (their like, their pass, their block) never shown. Reversal: the read keyed on either direction;
   - **owner-only:** an unauthenticated request refused; another method refused; a body or query refused; `no-store` present; and the account held `FOR SHARE`;
   - **recovery from no state,** each with the version the read gives:
     - with resurfacing on, a like of a passed candidate who resurfaces;
     - with undo on, a like after a withdrawn pass;
     - a block after an unblock.

     Each recovery's reversal: with the read's version replaced by `0`, the command is refused `stale_version`;
   - **D15:** the read's route not served by the runtime, with `test_interactions_sealed_runtime.py`'s lists gaining it (above).
2. **The proof takes its versions as a client does** (the section's item 2):
   - `interaction_cases._version()` reads the new route, not the ORM;
   - every expected version a case sends comes from a command's own answer or from the read, which a test asserts. Its reversal: `_version()` reading the ORM again fails that test;
   - item 1's three recovery cases are discovery cases too;
   - D14's record runs over them as over every case.
3. **The contract** (D13: additive only):
   - the read's DTO, with a request DTO only if one is needed;
   - their `openapi.json` components (no paths) and corpus cases;
   - F08's and F13's entries gain the DTO with its owner projection, and no transition changes;
   - the contract test named above, and an allowed and a forbidden projection example;
   - the README's SV3 section.

   No existing DTO's properties or enums change, and no `ApiError` code is added. Regenerate with `npm run generate --prefix packages/contracts`, never by hand. Run it a second time and confirm that `git status` shows no further change, and record which generated files changed.
4. **The earlier tests** (the section's item 3): the tests named in the stop rule, each rewritten as it says, with its assertion before and after in the record. No other earlier test changes.
5. **The local checks:**
   - **API,** in `services/api`: `python3.12 -m venv .venv`, then `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`. Then, with `GLOW_ENV=test`: `manage.py check`, `manage.py test tests --verbosity 2`, `smoke.py`, `ruff check .`, `ruff format --check .`, `mypy` and `python -m glow_persistence.static_check`;
   - **the contracts,** in `packages/contracts`: `npm ci --ignore-scripts`, then `npm run check`, then the Python contract tests (`PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests -v` from `services/api`);
   - **the mobile app,** in `apps/mobile`: `npm ci --ignore-scripts`, then `npm run check`, with the regenerated outputs and no other change;
   - **the proof,** in `proofs/postgres-ordering`: its venv and hash-locked install, its offline tests under `env -i`, Ruff, `ruff format --check` and mypy; and the lock scan, `python -m glow_ordering_proof.account_lock_scan`, its output unchanged (52 calls, 0 joining, 7 account locks);
   - **a local database run,** if Docker allows it under D4's conditions: iteration, not evidence.
6. **The run of record.** Commit and push your code, and wait for the Foundation run on your last code commit to finish (the push rule). Read it with your GitHub tools:
   - every job's conclusion, and the gate's line (`Application checks passed`);
   - the API test count;
   - each suite's result and D14's line (`ROW LOCKS (D14): PASS`), and the scans;
   - the discovery suite's count and phase duration, against the job's 30-minute timeout;
   - the Mobile checks job's contract check, tests and rendered checks;
   - whether a toolchain retry fired.
7. **The records** (the section's item 4):
   - the contract document's F08 and F13 server mapping states the read and its answer;
   - the proof README's SV3 paragraph gains a sentence on B-C1;
   - the P11 plan's SV3 entry gains B-C1's run of record.

   Change no other section of those files.

## 4. The record

Add a section `## Stage B, correction B-C1` at the end of `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md`:
- the start gate's results, the environment check (names only) and the toolchain versions;
- the read: its route, its transaction and locks, its DTO, and its answer for each case, the alike cases' bodies shown byte-identical;
- a table with one row per test: the file, the test, the reversal and its failing output;
- the proof: `_version()` before and after, the assertion that every sent version comes from an answer or the read, and the recovery cases;
- the contract: the new DTO, the registry entries with their examples, and the generated files that changed;
- the earlier tests: each named test's assertion before and after, and why; the sealed-runtime lists' coverage;
- every command you ran, with its result line, with local database runs listed as iteration, not evidence;
- the run of record: its ID, each job's result, the counts, D14's line in each suite, the discovery phase's duration, and whether a retry fired;
- every deviation from the brief, and what you could not run, and why.

Commit each logical step with a clear message ending in the session's attribution lines. Push your records commit only after the run of record has finished. Confirm that `git status` is clean, and that `git diff --name-only <START_SHA> HEAD` lists only B-C1's owned paths.

## 5. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch, your code head and records head;
- the start gate's and the environment check's results;
- the read: route, transaction, DTO and its answers, and each test with its reversal's result;
- the proof's change and the recovery cases;
- the contract: the DTO, the registry entries, and the generated files that changed;
- the earlier tests, each before and after;
- each local check's result, and whether a local database run was used;
- the run of record: its ID, every job, the gate's line, the counts, D14's line in each suite, the discovery phase's duration and whether a retry fired;
- anything that met the stop rule, every deviation from the brief, and what you could not run.

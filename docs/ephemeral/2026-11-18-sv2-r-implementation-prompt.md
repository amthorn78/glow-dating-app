# SV2-R prompt — SV2's completion requirements after OD-68: the identity requirement set aside, and the photo check's toggle

- **Owner:** App Manager 12. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 18 November 2026.**
- **Durable brief:** [SV2-R — SV2's completion requirements after OD-68](../planning/sv2-r-od-68-requirements-change.md), revision 4 (DM-91's XX5 to XX8 and DM-92's YY1 to YY7 applied as given).
- **Where the result goes:**
  - the session's changes in the brief's owned paths, and its record, `docs/testing/evidence/<the session's date>-sv2-r-requirements-change.md`, on its own branch;
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification to the record, and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.25 (confidence 0.63); rung probabilities low 0.00, medium 0.15, high 0.45, extra high 0.39, max 0.01, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.56, Sonnet 5.5 0.44, Haiku 5.5 0.00 (confidence 0.41). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.084, Opus 5.5 at high 0.252, Opus 5.5 at extra high 0.218, Opus 5.5 at max 0.006, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.066, Sonnet 5.5 at high 0.198, Sonnet 5.5 at extra high 0.172, Sonnet 5.5 at max 0.004, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Flags: boundary between extra high and high; model near tie between Opus 5.5 and Sonnet 5.5. Sent 2026-11-18T15:56:15Z. Nathan picks the cell.
- **The Dev Manager's read:** done. Dev Manager 5 read the brief in DM-91 and DM-92, and its words are applied as given. This prompt authorizes no credential use and no live provider action, so it needs no read of its own (the charter, "Read before it takes effect"). The suites' keys and the database password are generated for one run and destroyed with it.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Then, in order: the manager's verification; the pull request and Codex's review of its head; an exact-head code review of the final code head (the brief's "Review plan"); corrections as findings need; the merge after its run, Codex's summary on the final head and its checklist.
- **Deletion condition:** prune after SV2-R's pull request merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch (AM11-21).

---

You are the **implementation session for SV2-R**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What SV2-R is.** A bounded change to SV2, the server's profiles and media slice, after Nathan's direction OD-68 (17 November 2026): ID validation is set aside for the MVP and kept possible later, and the automated photo check is dropped behind a toggle. Today no profile can become `visible`, since the completion rule still asks for identity verification and a photo approved by the automated check. SV2-R makes it possible, and stays proven on a disposable PostgreSQL in CI and sealed from the served runtime until P11. It covers:
- **R1:** the identity requirement set aside: off the completion check, with the identity record, its port, the staff approval and its setting, and the contract's value kept;
- **R2:** the photo check's toggle, `media.photo_check`, off at launch, in D2's settings store: `run_check`'s off branch, the `recheck` step for photos approved while it was off, and two `system` transitions out of `approved` in F05's registry;
- **R3:** the photo requirement unchanged, with its docstring;
- **R4:** the fixed limits, the seal and D15's reversals unchanged;
- **"Earlier tests":** the earlier tests and proof cases R1 and R2 are expected to change, and nothing else.

There is no provider, deployed URL, real member, HDE call or stored credential.

**The brief, `docs/planning/sv2-r-od-68-requirements-change.md`, revision 4, is the specification.** Much of its text is the Dev Manager's words (DM-84 section 5, DM-91, DM-92), checked against the code. Follow them exactly. Where this prompt summarizes the brief, the brief wins.

**What came before.**
- **SV2** built the profile and its settings (Stage A, PR43, `4dc2061`) and photos (Stage B, PR44, `3240ef0`), with corrections, proven by the profile suite on the third disposable database. Its brief, `docs/planning/sv2-profiles-media.md`, revision 8, holds D2 (the settings store), D9 (completion and the one shared recompute), D10 (photos), D13 to D15 (the seal, no new dependency, reversals), D18 (identity verification and the staff approval) and D19 (one pointer order).
- **SV3** (PR45 to PR47, `36a19f7`) built eligibility, discovery and interactions on SV2's profile; its discovery suite is the fourth database.
- **`main` is at `15d54f6`** (PR53, Markdown only). The manager branch has changed only Markdown since.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 12. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only the brief's "Owned paths (the session)":
    - `services/api/glow_profiles/requirements.py`, `media.py`, `media_fixtures.py` and `settings_store.py`;
    - `services/api/glow_domain/media.py` and `profile_settings.py`;
    - one new migration under `services/api/glow_persistence/migrations/`, after `0011` (the setting's seed);
    - `packages/contracts/production/flows-v1.json`, and `packages/contracts/README.md`'s note of the registry's change;
    - tests under `services/api/tests/` and `packages/contracts/tests/`;
    - the proof's profile suite: `proofs/postgres-ordering/glow_ordering_proof/profile_cases.py` and `profile_support.py`;
    - the record;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only, through your GitHub tools: no pull request, comment, review, re-run, workflow dispatch or setting. Use `gh` for nothing but a search. Change nothing in Notion.
- **The stop rule.** Stop and report, with no further change, if any of these holds:
  - **an owned path:** the work needs a path outside the list above. That includes:
    - `services/api/glow_profiles/staff.py`, `identity_verification.py`, `recompute.py`, `events.py`, `operations.py`, `views.py`, `urls.py` and `contract.py`;
    - `services/api/glow_domain/identity_verification.py`, `services/api/glow_persistence/models.py` and every existing migration;
    - `services/api/glow_api/` (the seal);
    - the contract's schema (`gapp-api-v1.schema.json`), `openapi.json` and any generated output;
    - any `apps/` path, `apps/mobile` included (its interactions fixture imports the flow registry): a mobile source, test or fixture that would have to change for the Mobile checks job to pass;
    - any other file of `proofs/postgres-ordering`, `scripts/`, any workflow, the `Dockerfile`, an environment template, or a `requirements` file;
  - **a dependency:** any new Python or npm package, or a changed pin (D14);
  - **a design change:** an existing DTO or an existing flow-registry entry would have to change (the registry gains exactly the brief's two `system` entries out of `approved`, and nothing else changes);
  - **the seal:** the served runtime would import a new module or select a fixture provider;
  - **the timeout:** the Database proof checks job cannot stay within its 30-minute timeout; it is not raised;
  - **an earlier test** (the brief's "Earlier tests", SV3's DD5 rule): an earlier test or proof case that no longer passes and is not named there. Report which and why; do not change or delete it.
  - In each case, report it; do not narrow the brief's words to pass it. A reversal's temporary edit of code is allowed, and must be undone.
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished. A newer push cancels the earlier run's application jobs, and the run of record is lost. Push your records commit only after the run of record has finished. The workflow runs on pushes to `claude/**` and `ccr-**`; if your branch is named otherwise, say so in the report, since no run starts.
  - **If GitHub never starts the run** (it stays `queued` with no jobs for 30 minutes), do not re-run it, dispatch it, push an empty commit, or ask anyone to re-run it (OD-58). Record it, push your records commit, and report. The manager's PR run is then the run of record.
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
  - connect to any database but a throwaway one you started under D4's conditions. Run `migrate` or `makemigrations` only through the proof's own commands against such a database, under Django's test runner, or under the static registry's dummy settings;
  - connect to HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script;
  - weaken or delete a test to make the suite pass.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:** `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` or `PG*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG)'` prints names only. If any is present, stop and report.
3. **AWS names may be present** (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_CA_BUNDLE`). `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values, and pass none to a command.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
5. **The toolchain:** CPython 3.12.14 as `python3.12` (`services/api/.python-version`); Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, first on PATH (`scripts/bootstrap-toolchain.sh`). Record `python3.12 --version`, `node --version`, `npm --version` and `docker --version`.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API). The proxy and CA variables pass by reference, never printed (`docs/operations/local-development.md`).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git merge-base --is-ancestor 15d54f647aa012edf53165f04a0a7e4931a7b67f HEAD && echo "PR53's merge present"   # must print the line
git diff --quiet 15d54f647aa012edf53165f04a0a7e4931a7b67f HEAD -- . ':!*.md' && echo "main's code"   # must print the line
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/api proofs/postgres-ordering packages/contracts apps .github docs/planning/sv2-r-od-68-requirements-change.md   # must print nothing
ls docs/testing/evidence | grep -c 'sv2-r-'         # must print 0
ls services/api/glow_persistence/migrations | grep -E '^[0-9]{4}_'   # must list 0001 to 0011 only
```

If a check fails, stop and report. The prompt is stale if:
- `<START_SHA>` is not on the live manager branch;
- the live branch has changed an owned path or the brief since it;
- or an SV2-R record already exists.

**Then read, completely:**
- **The instructions:** root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`, `proofs/postgres-ordering/README.md` and `packages/contracts/README.md`; `apps/mobile/AGENTS.md` (you change nothing there).
- **The brief,** revision 4, whole, its "Earlier tests" above all.
- **The SV2 brief's** D2, D9, D10, D13 to D15, D18 and D19 (`docs/planning/sv2-profiles-media.md`).
- **The Dev Manager's reports** that shaped SV2-R, in `docs/continuity/dev-manager/reviews/`: DM-84 (section 5, its toggle defaults), DM-91 (sections 3 and 4) and DM-92 (section 3).
- **Nathan's direction** OD-68 in `docs/continuity/owner-directions.md`.
- **The code you change or build beside:**
  - `services/api/glow_profiles/`: `requirements.py`, `media.py` (`transition`, `review`, `run_check`, `_decision_audit`, `request_purge`, `delivery_reference`), `media_fixtures.py`, `settings_store.py` (`read_shared` and its pointer order), `staff.py` (`publish_setting`, `approve_without_id`, `revoke_approval`, `restrict_media`), `recompute.py` and `tx.py` (`lock_account`);
  - `services/api/glow_domain/`: `media.py` (`TRANSITIONS`, `CHECK_SUBJECT`, `APPROVED_BY_CHECK`), `profile_settings.py` (the closed schemas, `LAUNCH_DEFAULTS`, `LAUNCH_REASONS`, `SEEDED_BY_0007`, `ALL_SETTINGS`, `FIXED_LIMITS`) and `identity_verification.py`;
  - `services/api/glow_persistence/models.py`, and migrations `0007_settings_launch_defaults.py` and `0009_media_policy_seed.py`, whose seed pattern (version, pointer and `StaffAudit` row with `seed_launch_default`) the new migration follows;
  - `packages/contracts/production/flows-v1.json` (F05) and `packages/contracts/transition_contract.py`, with `packages/contracts/tests/test_transition_contract.py`;
  - every test and proof case the brief's "Earlier tests" names, and `profile_support.py`'s `approved_photo`;
  - the Database proof checks job in `.github/workflows/foundation.yml`, its SV2 steps.
- **The record of SV2:** `docs/testing/evidence/2026-11-10-sv2-profiles-media.md`, "Stage B" and its corrections.

## 3. What to do

1. **R1, the identity requirement set aside.** `missing()` no longer checks identity verification, and the completion read never reports `identity_verification`; the module's docstring says the requirement is set aside (OD-68). Nothing else of D18 changes. Its tests (acceptance checks 1 and 2), each with its reversal: a temporary edit that must make the test fail, run and then undone. Record the edit and the failing output.
2. **R2, the photo check's toggle,** as the brief's R2 sets it, in this order:
   - **the setting** `media.photo_check`, with `{"enabled": false}` under a closed schema in `profile_settings.py`, and its seed in a new migration after `0011`, with `system:launch-default`, "OD-68", its pointer and its `StaffAudit` row (`seed_launch_default`) as `0007` and `0009` write theirs (check 7);
   - **`run_check`** reads it in its one `read_shared` call, in D19's name order. While it is off, it approves a `review_pending` photo under the toggle's own subject and reason, without calling the check port; a restriction, the hold port and a missing variant stop it as now; the approval ends with D9's recompute (checks 3, 4 and 6);
   - **`recheck`,** a new system step for an `approved` photo whose approval carries the toggle's reason, with a read listing those photos for P11's worker. It takes the account row lock first, refuses an account that is not `active`, reads the toggle in its one `read_shared` call, and changes nothing while the toggle is off. On approve, it asks the hold port first (a held photo is `no_change`) and records the check's decision; on reject, the photo leaves view and D9's recompute follows; undecided changes nothing (check 5);
   - **F05's registry** gains `approve` (`approved` to `approved`) and `reject` (`approved` to `rejected`), `system`, with `A05`, in `flows-v1.json` and `TRANSITIONS` alike, each with an allowed and a forbidden example in `test_transition_contract.py`; the contracts README records the change, as SV2 Stage B's note does; then `npm run generate --prefix packages/contracts`, twice, with `git status` showing no change to any generated output (check 8);
   - **the locks:** a publication of the toggle, `run_check` and the recheck serialize on the setting's pointer lock, in D19's order, on the disposable database (check 9), in the profile suite.

   Every new or changed test comes with its reversal, recorded with its failing output (check 12). Make at least these reversals, each named in the record:
   - the identity check restored in `missing()` (check 1);
   - the off branch calling the check port, approving a restricted or held photo, or recording `system:photo-check` with `automated_check` (check 3);
   - the recheck acting while the toggle is off, approving a held photo, or leaving a rejected photo's profile `visible` when it was its last approved photo (check 5);
   - a publication of the toggle outside its closed schema accepted (check 7);
   - a third transition out of `approved`, or one of the two missing from either table (check 8);
   - the toggle's pointer taken out of D19's order (check 9).
3. **R3:** `requirements.py`'s docstring says how a photo reaches `approved` in each state of the toggle.
4. **The earlier tests** the brief's "Earlier tests" names: change each as it says, and record each change with its reason, before and after. Any other earlier test that fails is a stop (above).
5. **The local checks:**
   - **API,** in `services/api`: `python3.12 -m venv .venv`, then `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`. Then, with `GLOW_ENV=test`: `manage.py check`, `manage.py test tests --verbosity 2`, `ruff check .`, `ruff format --check .`, `mypy`, and the contract tests (`PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests -v`), as CI runs them;
   - **the contracts,** in `packages/contracts`: `npm ci --ignore-scripts`, then `npm run check`;
   - **the mobile app,** in `apps/mobile`: `npm ci --ignore-scripts`, then `npm run check`, with no change under `apps/`;
   - **the proof,** in `proofs/postgres-ordering`: its venv and hash-locked install, its offline tests under `env -i`, Ruff, `ruff format --check` and mypy;
   - **a local database run** of the profile suite, if Docker allows it under D4's conditions: iteration, not evidence.
6. **The run of record.**
   - Commit and push your code. Wait for the Foundation run on your last code commit to finish (the push rule).
   - Read it with your GitHub tools:
     - every job's conclusion, and the gate's line (`Application checks passed`);
     - the API test count;
     - the ordering, identity, profile and discovery suites' results, each suite's value and secret scans, and the profile suite's new and changed cases by name;
     - the Database proof checks job's duration, against its 30-minute timeout;
     - the Mobile checks job's contract check and tests;
     - whether a toolchain retry fired;
     - that no secret, coordinate or member value appears in the job's log.

## 4. The record

Write `docs/testing/evidence/<the session's date>-sv2-r-requirements-change.md`:
- the start gate's results, the environment check (names only) and the toolchain versions;
- a table with one row per acceptance check (1 to 12) and per item of R1 to R4: the files, the test, the reversal and its failing output;
- the setting: its schema, its seed migration, and the seed's pointer and `StaffAudit` row;
- `run_check`'s off branch and the recheck: their order of checks, writes and the hold port, with the AST tests that pin them;
- the registry's two entries, their examples, and the regeneration's result;
- each earlier test or proof case changed, with its reason, before and after, against the brief's "Earlier tests";
- the local checks, each with its exact result;
- the run of record: its ID, head, each job's conclusion and the lines asked for above;
- deviations, limits and open questions.

## 5. The report

Branch, start and head SHAs, changed paths, what was built against R1 to R4, every acceptance check with its exact result and each reversal's failing output, each earlier test changed, the run of record's ID and jobs, deviations and open questions. Push your records commit after the run of record has finished, and end with the record's path and your branch's final head.

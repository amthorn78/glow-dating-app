# SV2 Stage A correction C1 prompt — one completion recompute in every requirement writer, a failing birth date not stored, restriction's registry entries and CI's mypy

- **Owner:** App Manager 10. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 10 November 2026.**
- **Durable brief:** [SV2 — The profiles and media slice](../planning/sv2-profiles-media.md), revision 4, "Stage A, correction C1".
- **Where the result goes:**
  - the session's changes, and the record's new section "Correction C1", under "Stage A" in `docs/testing/evidence/2026-11-10-sv2-profiles-media.md`, on the session branch;
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification, and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.13 (confidence 0.79); rung probabilities low 0.00, medium 0.10, high 0.69, extra high 0.20, max 0.01, ultracode 0.00. Model probabilities Fable 5.1 0.03, Opus 5.5 0.94, Sonnet 5.5 0.03, Haiku 5.5 0.00 (confidence 0.92). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.003, Fable 5.1 at high 0.021, Fable 5.1 at extra high 0.006, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.094, Opus 5.5 at high 0.649, Opus 5.5 at extra high 0.188, Opus 5.5 at max 0.009, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.003, Sonnet 5.5 at high 0.021, Sonnet 5.5 at extra high 0.006, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-10T05:52:54Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The brief's revision 4 applies DM-54's Y1 to Y10 and Y12 as written, and DM-54 says they need no read before this prompt (section 2). This prompt authorizes no credential use and no live provider action.
- **Which session:** Stage A's implementation session, on its branch `claude/sv2-stage-a-impl-0qqzvj`, is the natural home: it built the code, its local harness and its reversal runner. A new session can run it equally well, on its own branch.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of the commit that holds it (step 6). Then:
  - the manager's verification;
  - Codex on C1's head;
  - an exact-head code and security review of the corrected head in full, with a written threat model. No delta review is needed, since no review has run (DM-54, section 14).
- **Deletion condition:** prune after SV2 Stage A's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are **correction C1 of SV2's Stage A**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **Stage A's implementation** (code head `b97bc15`, records `f2635fa`, integrated at `e0c0ffe`, on PR43) built the server's profile in `services/api/glow_profiles`. Its profile suite runs on a third disposable database in the Database proof checks job. Its record is `docs/testing/evidence/2026-11-10-sv2-profiles-media.md`, "Stage A", with the manager's verification.
- **The session reported 13 decisions**, and the Dev Manager ruled on them in DM-54 (`docs/continuity/dev-manager/reviews/2026-11-10-dm-54-sv2-stage-a-decisions.md`), with Y1 to Y12 in given words. The brief's revision 4 applies them. Four need code:
  - **Completion runs only in the profile edit.** No other writer makes a profile `visible`, and only that edit demotes one whose requirement has lapsed. DM-54 replaces this with one shared recompute at the end of every requirement writer (D9, Y3).
  - **A birth input whose date fails the adult rule is saved.** DM-54: it is refused and nothing of it is stored, while the rerun's effects commit (D7, D8, Y6 to Y8).
  - **The registry lacks two kinds of entry:** `requirements_met` (`system`), and `restrict` (`moderator`) (Y4).
  - **CI does not type-check `glow_profiles`** (Y9).
- **Codex's review** of PR43 at `93a27ea` completed with no findings.

**The brief's "Stage A, correction C1" is your specification,** with D7, D8, D9, D11's registry entries, checks 7 and 9 and the "Review plan" as revision 4 words them. Read them whole. Where this prompt summarizes them, the brief wins.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 10. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only "Stage A, correction C1"'s owned paths:
    - `services/api/glow_profiles/**`, and SV2's own modules in `services/api/glow_domain/` (`profile_fields.py`, `profile_settings.py`, `identity_verification.py`);
    - `services/api/pyproject.toml`: `[tool.mypy]`'s `files` only;
    - `services/api/tests/`: SV2's profile tests;
    - `packages/contracts/production/flows-v1.json`: Y4's entries only; `packages/contracts/tests/test_transition_contract.py`: their examples; `packages/contracts/README.md`: SV2's section;
    - `proofs/postgres-ordering/**`: the profile suite, its tests and the README's SV2 section;
    - `docs/architecture/data-model.md`: Y11's sentence and SV2's rows; `docs/architecture/production-contracts.md`: F02 to F06's server mapping;
    - the record's new section "Correction C1";
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule.** Stop and report, with no further change, if the correction seems to need any of these:
  - a model or migration change;
  - a change to an existing DTO, or a new one. No schema change is expected, so the generated contract outputs do not change either;
  - a change to `glow_chat`, `glow_identity`, `glow_api`, the workflow, a lock or a dependency;
  - a change to an existing registry entry, or a role the oracle does not authorize;
  - more than the Database proof checks job's 30-minute timeout.
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished. Push your records commit only after the run of record has finished. The workflow runs on pushes to `claude/**` and `ccr-**`; if your branch is named otherwise, say so in the report, since no run starts.
- **Network:**
  - PyPI and the npm registry, for `pip install --require-hashes` and `npm ci --ignore-scripts` from the existing locks;
  - Docker Hub, only to pull the PostgreSQL image the CI job pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`) for a local run.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions):
  - a throwaway PostgreSQL in Docker, from the CI job's pinned image, on loopback only;
  - a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present;
  - removed afterwards.

  Local passes are "iteration, not evidence"; the run of record is CI's.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, password, code, token, session key or signing key, in any form;
  - make test data that looks real: accounts, emails, names, birth facts, places and coordinates are synthetic and obviously so (`@example.invalid`);
  - call any provider or HDE, send any email, or run any command in `proofs/stream-chat/`;
  - connect to any database but a throwaway one you started under D4's conditions. Run `migrate` or `makemigrations` only through the proof's own commands against such a database, or under the static registry's dummy settings;
  - connect to HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script;
  - weaken or delete a test to make the suite pass.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:**
   `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`.
   If any is present, stop and report.
2. **No `STREAM_*` or `PG*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG)'` prints names only. If any is present, stop and report.
3. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them.
4. **The toolchain:** CPython 3.12.14 as `python3.12`; Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, first on PATH; Docker. Record `python3.12 --version`, `node --version`, `npm --version` and `docker --version`.
5. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API). The proxy and CA variables pass by reference, never printed.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # Stage A's session: claude/sv2-stage-a-impl-0qqzvj; <START_SHA> already contains its f2635fa
git rev-parse HEAD                                  # must print <START_SHA>
git diff --name-only b97bc15cd7a5200eac6c7eb3e033131bebbe8e90 HEAD -- .github scripts services apps packages proofs | grep -v -E '\.md$'   # must print nothing: the code is b97bc15's
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/api proofs/postgres-ordering packages/contracts .github docs/architecture 'docs/testing/evidence/*sv2*'   # must print nothing
grep -c -E '^#+ Correction C1' docs/testing/evidence/2026-11-10-sv2-profiles-media.md   # must print 0
grep -c 'requirements_met' packages/contracts/production/flows-v1.json                   # must print 0
```

If a check fails, stop and report. The prompt is stale if any of these holds:
- `<START_SHA>` is not on the live manager branch;
- an owned path changed there after it;
- "Correction C1" is already recorded.

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`; `proofs/postgres-ordering/README.md`; `packages/contracts/README.md`;
- **the brief,** revision 4: D7, D8, D9, D11's "The flow registry", checks 7 and 9, "Review plan", and "Stage A, correction C1";
- **DM-54's report,** whole;
- **the record's "Stage A" sections:** "Decisions and deviations for the manager" and "Manager verification";
- **the code you change:**
  - `glow_profiles/operations.py`: the profile edit's completion step, `_demote_if_visible`, the field, area, consent, adult-check and birth-input writers;
  - `glow_profiles/staff.py`: `approve_without_id` and `revoke_approval`;
  - `glow_profiles/requirements.py`, `tx.py` (`run` and `Refused`) and `idempotency.py`;
  - `services/api/pyproject.toml`'s `[tool.mypy]`;
- **the registry:** `flows-v1.json`'s F02 to F04, and `transition_contract.py`'s `authorized`;
- **the profile suite's cases** for completion, removals, the adult check and the birth input.

## 3. What to do

1. **The items of "Stage A, correction C1", in order.** For each: the change, its tests, and its reversals. A reversal is a temporary edit that must make a test fail; run it, then undo it. Record the edit and the failing output.
   - **Item 1, D9's recompute:**
     - one shared function, called at the end of each writer D9 lists for Stage A, in that writer's own transaction, after the account row lock, on rows read after it;
     - the profile edit's own completion and demotion logic becomes that function's call.

     **Tests**, in the profile suite on the disposable database:
     - each listed writer that meets the last requirement makes the profile `visible`, with its event;
     - a write that finds a requirement missing makes a `visible` profile `incomplete`. One case must use a requirement that lapsed without a write: a new onboarding consent version, then an area change;
     - `paused`, `restricted` and `removed` profiles stay as they are;
     - the existing lock case still shows a withdrawal seen by a waiting completion.

     **Reversals:**
     - the recompute left out of one writer (name which; at least the area and the adult check, one each);
     - the recompute making a profile `visible` with one requirement missing;
     - the recompute changing a `paused` profile.
   - **Item 2, the registry entries** (Y4):
     - `requirements_met` from `incomplete` to `visible` (`system`; `eligible`; `A05`);
     - `restrict` from `visible` and from `paused` to `restricted` (`moderator`; `A05`).

     Each gets an allowed and a forbidden example in `tests/test_transition_contract.py`. No existing entry changes.

     **Reversal:** one entry's role changed to one the oracle does not authorize. Its allowed example must fail.
   - **Item 3, a birth input whose date fails the adult rule** (Y6 to Y8), in the brief's words:
     - refused, with nothing of it stored;
     - its transaction still commits the rerun: the age state `unknown` with no date, a current birth input `missing` with its mapping back to `pending`, a `visible` profile `incomplete`;
     - the operation returns the refusal without raising, and stores no idempotency record;
     - a retry is refused at the adult-check gate and changes nothing more.

     **Tests:**
     - after the refusal, no row holds the failing revision's date, time or place;
     - the age state, the current birth input, its mapping and the profile are as listed, with their events;
     - a retry of the same command, and of a new one, changes no row;
     - the value scan finds none of the failing input's values anywhere in the output.

     **Reversals:**
     - the revision stored;
     - the refusal raised, so the rerun's effects roll back;
     - an idempotency record stored.
   - **Item 4, CI's mypy** (Y9): `glow_profiles` joins `[tool.mypy]`'s `files`. The configured `mypy` must pass. **Reversal:** a deliberate type error in `glow_profiles`, which the configured `mypy` must now report.
   - **Item 5, the data model's sentence** (Y11): replace it with DM-54's words exactly.
   - **Item 6, the records:**
     - the data model's SV2 rows and the contract document's F02 to F06 server mapping, where items 1 and 3 change what they say;
     - the package README's SV2 section, where it lists the registry entries.
2. **The local checks:**
   - **API,** in `services/api`: `python3.12 -m venv .venv` and `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`; then, with `GLOW_ENV=test`, `manage.py check`, `manage.py test tests --verbosity 2`, `ruff check .`, `ruff format --check .` and `mypy` (now covering `glow_profiles`);
   - **the contracts:** the Python contract tests (`PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests -v` from `services/api`), and `npm run check` in `packages/contracts` after `npm ci --ignore-scripts` there and in `apps/mobile`. No generated file may change;
   - **the proof,** in `proofs/postgres-ordering`: the same install, then `python -m unittest discover -s tests -t . -v`, `ruff check .`, `ruff format --check .` and `mypy`;
   - **the profile suite** on a local throwaway database under D4, if Docker allows, as iteration.
3. **The run of record.** Commit and push your code, then wait for its Foundation run to finish (the push rule). Read it with your GitHub tools:
   - every job's conclusion, and the gate's line (`Application checks passed`);
   - the API and proof test counts;
   - the API job's mypy line;
   - the profile suite's count and time, the profile phase's duration and both scans' lines;
   - the second profile run's refusal and its counts;
   - whether a toolchain retry fired.

   If it fails, stop and report the failing job and its log lines. Do not re-run it.

## 4. The record

Add a section `## Correction C1` under "Stage A" in `docs/testing/evidence/2026-11-10-sv2-profiles-media.md`, after the existing Stage A sections, holding:
- the start gate's results, the environment check (names only) and the toolchain versions;
- for each item: the files, the tests, the reversals and their failing output;
- each writer that now ends with the recompute, and the registry entry each completion uses;
- **for the threat model:** the recompute's call sites and locks, and the failing birth input's path (what is refused, what commits, what is stored);
- every command you ran, with its result line;
- the run of record's ID, each job's result, the counts, the profile phase and whether a retry fired;
- what you could not run, and why.

Commit each logical step with a clear message ending in the session's attribution lines. Push the records commit only after the run of record has finished. Then confirm:
- `git status` is clean;
- `git diff --name-only <START_SHA> HEAD` lists only your owned paths.

## 5. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch, your code head and records head;
- the start gate's and the environment check's results;
- for each of items 1 to 6: what changed, its tests, and each reversal's result;
- each local check's result;
- the run of record: its ID, every job, the gate's line, the counts, the profile phase, the mypy line and whether a retry fired;
- anything that met the stop rule, every deviation, and what you could not run.

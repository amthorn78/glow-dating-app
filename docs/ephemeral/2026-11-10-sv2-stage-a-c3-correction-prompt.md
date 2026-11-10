# SV2 Stage A correction C3 prompt — the static guards, three test nits and a record correction (tests only)

- **Owner:** App Manager 10. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 10 November 2026.**
- **Durable brief:** [SV2 — The profiles and media slice](../planning/sv2-profiles-media.md), revision 5, "Stage A, correction C3".
- **Where the result goes:**
  - the session's changes, and the record's new section "Correction C3" in `docs/testing/evidence/2026-11-10-sv2-profiles-media.md`, on the session branch;
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification, and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 1.94 (confidence 0.87); rung probabilities low 0.00, medium 0.13, high 0.80, extra high 0.07, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.99, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.99). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.129, Opus 5.5 at high 0.792, Opus 5.5 at extra high 0.069, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.001, Sonnet 5.5 at high 0.008, Sonnet 5.5 at extra high 0.001, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-10T21:02:21Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. C3 changes tests and records only, under step 6's rule (a), with no design change (the brief's "Stage A, correction C3"). This prompt authorizes no credential use and no live provider action.
- **Which session:** C2's session, on its branch `claude/awesome-maxwell-wo9jxa`, is the natural home. A new session can run it equally well, on its own branch.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of the commit that holds it (step 6). Then:
  - the manager's verification;
  - Codex on C3's head;
  - a delta review of C3 (M05 S2);
  - the Dev Manager's pre-merge read.
- **Deletion condition:** prune after SV2 Stage A's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are **correction C3 of SV2's Stage A**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **Stage A** built the server's profile in `services/api/glow_profiles`, sealed, with a profile suite on a third disposable database in the Database proof checks job. Corrections C1 and C2 followed. C2's code head is `01a3acb`, integrated at `26419a9` on PR43; its run of record, 42864458572, passed every job, with the profile suite at 53/53.
- **The exact-head review after C2** found no defect in the code and no blocking finding. Its one should-fix finding is that several static guards are name-based, so plausible edits pass every test. It also found five nits. Its report and the manager's dispositions are in the record, "Exact-head review of Stage A after C2".
- **The brief's "Stage A, correction C3"** lists your six items. **It is your specification;** where this prompt summarizes it, the brief wins.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 10. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only "Stage A, correction C3"'s owned paths:
    - `services/api/tests/`: SV2's profile tests (`test_profiles_offline.py`, `test_profile_recompute.py`);
    - `proofs/postgres-ordering/**`: the profile suite (`glow_ordering_proof/profile_cases.py`) and its offline tests;
    - the record's new section "Correction C3";
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule.** Stop and report, with no further change, if the correction seems to need any change outside tests and the record:
  - `glow_profiles`, `glow_domain`, `glow_identity` (`age.py` included), `glow_chat` or `glow_api`;
  - a model, migration, DTO or registry entry, the workflow, a lock or a dependency.

  Stop too if a new check fails on the code as it stands, without a temporary edit. That would be a code defect for the manager, not a test change. A reversal's temporary edit of code is allowed, and must be undone.
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
  - connect to any database but a throwaway one you started under D4's conditions, HDE, Railway or any other external service;
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
git switch -C <your session branch> <START_SHA>   # C2's session: claude/awesome-maxwell-wo9jxa; <START_SHA> already contains its ca0ad16
git rev-parse HEAD                                  # must print <START_SHA>
git diff --name-only 01a3acb3d725e05d6e2d6a2d78f5e102db9e9f5a HEAD -- .github scripts services apps packages proofs | grep -v -E '\.md$'   # must print nothing: the code is 01a3acb's
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/api proofs/postgres-ordering 'docs/testing/evidence/*sv2*'   # must print nothing
grep -c -E '^#+ Correction C3' docs/testing/evidence/2026-11-10-sv2-profiles-media.md   # must print 0
grep -c 'Stage A, correction C3 (the review after C2)' docs/planning/sv2-profiles-media.md   # must print 1
```

If a check fails, stop and report. The prompt is stale if any of these holds:
- `<START_SHA>` is not on the live manager branch;
- an owned path changed there after it;
- "Correction C3" is already recorded.

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`; `proofs/postgres-ordering/README.md`;
- **the brief,** revision 5: "Stage A, correction C3";
- **the record:** "Exact-head review of Stage A after C2", and "Correction C2"'s items 8 and 9;
- **the tests you change:**
  - `services/api/tests/test_profiles_offline.py`: `NoValueInLogsTests`, `ProfileRoutesTests`, `LockOrderTests` and `BodiesTheParserCannotHoldTests`;
  - `services/api/tests/test_profile_recompute.py`: `CallSiteTests`;
  - `proofs/postgres-ordering/glow_ordering_proof/profile_cases.py`: the eligibility step's cases, and the comment on the scans' timing;
- **the code the guards read** (read only):
  - `glow_profiles/views.py`, `operations.py`, `staff.py`, `recompute.py` and `identity_verification.py`;
  - `glow_identity/age.py`.

## 3. What to do

1. **The items of "Stage A, correction C3", in order.** For each: the change, its tests, and its reversals. A reversal is a temporary edit that must make a test fail; run it, then undo it, and check the file's SHA-256 against `01a3acb`. Record the edit and the failing output.
   - **Item 1, the static guards** (finding 1, (a) to (c)). Each reversal below must fail its new check, and each must pass every test today:
     - **Refusal reasons:**
       - an `AgeTransitionRefused(f"…{value}…")` in `age.py`;
       - a `PortOutcome(…)` built from a value in `glow_profiles/identity_verification.py`.
     - **Logging:**
       - a second `getLogger` call in `views.py`;
       - a logger borrowed under another name;
       - a `sys.stderr.write` in `glow_profiles`.
     - **Profile state:**
       - `before.state = …` on a `Profile` in `staff.py`;
       - a profile's state written through `bulk_update`;
       - `setattr(profile, "state", …)`;
       - a queryset variable's `.update(**…)` setting `state`;
       - a state write in `age.py`.

     The allowlist of state writes that are not a profile's names each entry with its file, line and model. The guards must still pass on `01a3acb` as it stands.
   - **Item 2, the guards' limits** (finding 1, (d) and (e)). Record in "Correction C3" what the guards cannot see, and which profile-suite case covers each behaviour:
     - a member view reaching staff code through a helper in `operations.py`;
     - a new operation whose inner function is not named `body`;
     - a recompute inside a condition;
     - a lazy import in `glow_domain`.
   - **Item 3** (finding 2): `BodiesTheParserCannotHoldTests` before `unittest.main()`. Show that running the file as a script now runs it.
   - **Item 4** (finding 3): the eligibility step's check at `profile_cases.py:2227` no longer uses the fixture date as a label. No check's label holds a member value: say how you checked.
   - **Item 5** (C2-6): the comment on the scans' timing says they run once, after the last case.
   - **Item 6, the record** (finding 4): "Correction C3" corrects Stage A's lock-order sentence. The settings' pointers are taken `FOR SHARE` in name order within each `read_shared` call. The recompute's onboarding read can follow a writer's other pointers, and no deadlock follows, since a publication holds one pointer `FOR UPDATE`. Stage A's sections stand as written.
2. **The local checks:**
   - **API,** in `services/api`: `python3.12 -m venv .venv` and `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`. Then, with `GLOW_ENV=test`: `manage.py check`, `manage.py test tests --verbosity 2`, `ruff check .`, `ruff format --check .` and `mypy`;
   - **the contract tests:** `PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests -v`, from `services/api`;
   - **the proof,** in `proofs/postgres-ordering`: the same install, then `python -m unittest discover -s tests -t . -v`, `ruff check .`, `ruff format --check .` and `mypy`;
   - **the profile suite** on a local throwaway database under D4, if Docker allows, as iteration. The case count stays 53.
3. **The run of record.** Commit and push your test changes, then wait for its Foundation run to finish (the push rule). Read it with your GitHub tools:
   - every job's conclusion, and the gate's line (`Application checks passed`);
   - the API and proof test counts;
   - the profile suite's count and time, the profile phase's duration and both scans' lines;
   - the second profile run's refusal and its counts;
   - whether a toolchain retry fired.

   If it fails, stop and report the failing job and its log lines. Do not re-run it.

## 4. The record

Add a section `## Correction C3` at the end of `docs/testing/evidence/2026-11-10-sv2-profiles-media.md`, holding:
- the start gate's results, the environment check (names only) and the toolchain versions;
- for each item: the files, the checks, the reversals and their failing output;
- the guards' allowlist and their limits;
- the corrected lock-order sentence;
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
- for each of items 1 to 6: what changed, its checks, and each reversal's result;
- each local check's result;
- the run of record: its ID, every job, the gate's line, the counts, the profile phase and whether a retry fired;
- anything that met the stop rule, every deviation, and what you could not run.

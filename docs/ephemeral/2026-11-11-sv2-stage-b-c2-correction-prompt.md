# SV2 Stage B correction C2 prompt — the exact-head review's test gaps and records (tests only)

- **Owner:** App Manager 10. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 11 November 2026.**
- **Durable brief:** [SV2 — The profiles and media slice](../planning/sv2-profiles-media.md), revision 8, "Stage B, correction C2 (the exact-head review)".
- **Where the result goes:**
  - the session's changes, and the record's new section "Stage B, correction C2" in `docs/testing/evidence/2026-11-10-sv2-profiles-media.md`, on the session branch;
  - the run of record: the Foundation run on its last code commit, with the profile phase;
  - the manager adds its verification, and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.03 (confidence 0.85); rung probabilities low 0.00, medium 0.10, high 0.78, extra high 0.12, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.98, Sonnet 5.5 0.02, Haiku 5.5 0.00 (confidence 0.97). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.098, Opus 5.5 at high 0.764, Opus 5.5 at extra high 0.118, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.002, Sonnet 5.5 at high 0.016, Sonnet 5.5 at extra high 0.002, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-11T08:20:24Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. C2 changes tests and records only, under step 6's rule (a), with no design change (the brief's "Stage B, correction C2"). This prompt authorizes no credential use and no live provider action.
- **Which session:** C1's session, on its branch `claude/gracious-davinci-lpqt02`, is the natural home. A new session can run it equally well, on its own branch.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of the commit that holds it (step 6). Then:
  - the manager's verification and integration into PR44;
  - Codex on PR44's head that holds C2;
  - a delta review of C2 (M05 S2);
  - the Dev Manager's pre-merge read (DM-58 section 7).
- **Deletion condition:** prune after Stage B's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are **correction C2 of SV2's Stage B**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **Stage B** built photos in `services/api/glow_profiles` (`media.py`), sealed, behind fixture ports; **correction C1** made the purge and the store's deletion acknowledgment run in any account state. C1's code head is `7538c76`, integrated at `8126c0c` on PR44; its run of record, 42957799823, passed every job, with the profile suite at 67/67.
- **Stage B's exact-head review** of `7538c76` found no defect in the code and no blocking finding. Its should-fix findings are gaps in the tests and the static guards, and records that claim more than the scans show. Its report and the manager's dispositions are in the record, "Exact-head review of Stage B after C1".
- **The brief's "Stage B, correction C2 (the exact-head review)"** lists your six items. **It is your specification;** where this prompt summarizes it, the brief wins.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 10. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only "Stage B, correction C2"'s owned paths:
    - `services/api/tests/`: `test_profile_media.py`, `test_profile_pointer_order.py` and `test_profile_recompute.py`;
    - `proofs/postgres-ordering/**`: the profile suite (`glow_ordering_proof/profile_cases.py`, `profile_support.py`), its offline tests and the README;
    - `docs/architecture/data-model.md` (the F05 unit-of-work row) and `packages/contracts/README.md` (the Stage B bullet);
    - the record's new section "Stage B, correction C2";
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule** (the brief's "The stop rule (C2)"). Stop and report, with no further change, if the correction seems to need any change outside tests and the records above:
  - `glow_profiles`, `glow_domain`, `glow_persistence` (a model or migration), `glow_chat`, `glow_identity` or `glow_api`;
  - a DTO or registry entry, the workflow, a lock file or a dependency.

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
  - read, print or use the value of any `AWS_*` variable (section 1);
  - make test data that looks real: accounts, emails, names, birth facts, places and coordinates are synthetic and obviously so (`@example.invalid`), and photo bytes are small synthetic PNGs made in the test;
  - call any provider or HDE, send any email, or run any command in `proofs/stream-chat/`;
  - connect to any database but a throwaway one you started under D4's conditions, HDE, Railway, Cloudflare or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script;
  - weaken or delete a test to make the suite pass. Changing `CASE_COUNT` follows the brief; say what each change is.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:**
   `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`.
   If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*` or `CF_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_)'` prints names only. If any is present, stop and report.
3. **Three AWS names are expected:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_CA_BUNDLE` (DM-57 and DM-58). `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values. If any other `AWS_*` name is present, stop and report.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them.
5. **The toolchain:** CPython 3.12.14 as `python3.12`; Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, first on PATH; Docker. Record `python3.12 --version`, `node --version`, `npm --version` and `docker --version`.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API). The proxy and CA variables pass by reference, never printed. No `AWS_*` name passes.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # C1's session: claude/gracious-davinci-lpqt02; <START_SHA> already contains its e30ef4a
git rev-parse HEAD                                  # must print <START_SHA>
git diff --name-only 7538c7642f38ac374f2a0f7ca22c8887a3a31922 HEAD | grep -v -E '\.md$'   # must print nothing: the code is 7538c76's
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/api proofs/postgres-ordering packages/contracts docs/architecture/data-model.md 'docs/testing/evidence/*sv2*'   # must print nothing
grep -c '^CASE_COUNT = 67$' proofs/postgres-ordering/glow_ordering_proof/profile_cases.py      # must print 1
grep -c '^## Stage B, correction C2' docs/testing/evidence/2026-11-10-sv2-profiles-media.md     # must print 0
grep -c '^## Stage B, correction C2 (the exact-head review)' docs/planning/sv2-profiles-media.md   # must print 1
```

If a check fails, stop and report. The prompt is stale if any of these holds:
- `<START_SHA>` is not on the live manager branch;
- an owned path changed there after it;
- "Stage B, correction C2" is already recorded.

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`; `proofs/postgres-ordering/README.md`; `packages/contracts/README.md`;
- **the brief,** revision 8: "Stage B, correction C2 (the exact-head review)";
- **the record:** "Exact-head review of Stage B after C1", whole, and the "Check 12" row and decision 2 of "Stage B";
- **the code the tests read** (read only): `glow_profiles/media.py` (`run_check`, `transition`, `request_upload`), `media_fixtures.py`, `settings_store.py`, and `glow_persistence/migrations/0008_media_lifecycle.py`'s constraints;
- **the tests you change:**
  - `services/api/tests/test_profile_media.py` (the approval's hold check);
  - `services/api/tests/test_profile_pointer_order.py` (`NothingElseLocksAPointerTests`);
  - `services/api/tests/test_profile_recompute.py` (the state-write guard and its allowlist, `NOT_A_PROFILES_STATE`);
  - `proofs/postgres-ordering/glow_ordering_proof/profile_cases.py` (the media cases and `constraints.malformed_direct_writes_are_refused`), `profile_support.py` (`RecordingHold`, the value ledger and its forms) and `tests/test_profile_offline.py`.

## 3. What to do

1. **The items of "Stage B, correction C2", in order.** For each: the change, its tests, and its reversals. A reversal is a temporary edit that must make a test fail; run it, then undo it, and check the file's SHA-256 against its committed state. Record the edit and the failing output.
   - **Item 1, a hold stops an approval** (F1): the suite case and the offline assertion. Reversal: the approval asks the hold port and ignores its answer. It must now fail both the new suite case and the offline assertion.
   - **Item 2, the lock-site guard** (F2): the wider check, with the proof's read-only mentions named. Reversals: a `select_for_update()` on a `PolicyRevision` queryset held in a variable, in a `glow_profiles` module other than `settings_store.py`; raw SQL whose table comes from `PolicyRevision._meta.db_table`. Each must fail the check.
   - **Item 3, the state-write guard** (F3): the `create` and constructor spellings. Reversal: an `approved` `MediaAsset` created in `staff.py`. It must fail the check.
   - **Item 4, the scans' ledger** (F4): the variants' keys, the bytes' `repr`, the credential tokens. Reversal: a variant's key or a photo's `repr` written to a log record in a media case. It must fail the value scan.
   - **Item 5, migration 0008's constraints** (F5): each of 0008's constraints written malformed and refused by its name. Reversal: one constraint dropped in the migration, as a temporary edit on a throwaway database only. The case must fail.
   - **Item 6, the records** (N2, N5, N6, N7, N9), as the brief words them.

   Every new check must pass on the code at `7538c76` as it stands. `CASE_COUNT` becomes 69, with the offline test that pins it.
2. **The local checks:**
   - **API,** in `services/api`: `python3.12 -m venv .venv` and `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`. Then, with `GLOW_ENV=test`: `manage.py check`, `manage.py test tests --verbosity 2`, `ruff check .`, `ruff format --check .` and `mypy`;
   - **the contract tests:** `PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests -v`, from `services/api`;
   - **the proof,** in `proofs/postgres-ordering`: the same install, then `python -m unittest discover -s tests -t . -v`, `ruff check .`, `ruff format --check .` and `mypy`;
   - **the profile suite** on a local throwaway database under D4, if Docker allows, as iteration: 69 cases.
3. **The run of record.** Commit and push your test changes, then wait for its Foundation run to finish (the push rule). Read it with your GitHub tools:
   - every job's conclusion, and the gate's line (`Application checks passed`);
   - the API and proof test counts;
   - the profile suite's count and time, the profile phase's duration and both scans' lines;
   - the second profile run's refusal and its counts;
   - whether a toolchain retry fired.

   If it fails, stop and report the failing job and its log lines. Do not re-run it.

## 4. The record

Add a section `## Stage B, correction C2` at the end of `docs/testing/evidence/2026-11-10-sv2-profiles-media.md`, holding:
- the start gate's results, the environment check (names only) and the toolchain versions;
- for each item: the files, the checks, the reversals and their failing output;
- the guards' allowlists and what they still cannot see;
- the corrected record sentences (N2, N6), and what the value ledger now holds;
- every command you ran, with its result line;
- the run of record's ID, each job's result, the counts, the profile phase and whether a retry fired;
- what you could not run, and why; and any decision or deviation, numbered.

Commit each logical step with a clear message ending in the session's attribution lines. Push the records commit only after the run of record has finished. Then confirm:
- `git status` is clean;
- `git diff --name-only <START_SHA> HEAD` lists only your owned paths.

## 5. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch, your code head and records head;
- the start gate's and the environment check's results (names only);
- for each of items 1 to 6: what changed, its checks, and each reversal's result;
- each local check's result;
- the run of record: its ID, every job, the gate's line, the counts, the profile phase and whether a retry fired;
- anything that met the stop rule, every decision and deviation, and what you could not run.

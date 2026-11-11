# SV2 Stage B correction C1 prompt — an inactive owner's purge (DM-58 item 9)

- **Owner:** App Manager 10. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 11 November 2026.**
- **Durable brief:** [SV2 — The profiles and media slice](../planning/sv2-profiles-media.md), revision 8, "Stage B, correction C1 (DM-58 item 9)".
- **Where the result goes:**
  - the session's changes, and the record's new section "Stage B, correction C1" in `docs/testing/evidence/2026-11-10-sv2-profiles-media.md`, on the session branch;
  - the run of record: the Foundation run on its last code commit, with the profile phase;
  - the manager adds its verification, and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.39 (confidence 0.69); rung probabilities low 0.00, medium 0.04, high 0.56, extra high 0.38, max 0.02, ultracode 0.00. Model probabilities Fable 5.1 0.01, Opus 5.5 0.97, Sonnet 5.5 0.02, Haiku 5.5 0.00 (confidence 0.96). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.006, Fable 5.1 at extra high 0.004, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.039, Opus 5.5 at high 0.543, Opus 5.5 at extra high 0.369, Opus 5.5 at max 0.019, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.001, Sonnet 5.5 at high 0.011, Sonnet 5.5 at extra high 0.008, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Flags: boundary between extra high and high. Sent 2026-11-11T03:50:40Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. DM-58 section 3 approved C1's design, and a fix that does what it says needs no further consultation (step 6, "Fix or carry, by rule"). The Dev Manager's next consultation confirms it as applied. This prompt authorizes no credential use and no live provider action.
- **Which session:** Stage B's session, on its branch `claude/sweet-ramanujan-wkn311`, is the natural home. A new session can run it equally well, on its own branch.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of the commit that holds it (step 6). Then:
  - the manager's verification and integration into PR44;
  - Codex on PR44's head that holds C1;
  - the full exact-head code and security review of the corrected head, with a written threat model (no delta review: DM-58 section 3);
  - the Dev Manager's pre-merge read (DM-58 section 7).
- **Deletion condition:** prune after Stage B's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are **correction C1 of SV2's Stage B**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **Stage B** built photos in `services/api/glow_profiles` (`media.py`), sealed, behind fixture ports, with the profile suite's media cases. Its code head is `d8f1bad`, integrated at `82d246b` on PR44; its run of record, 42947095725, passed every job, with the profile suite at 64/64.
- **Codex's review of PR44** found that `request_purge` and `acknowledge_deletion` begin with `lock_account` (`glow_profiles/tx.py`), which refuses an account that is not `active`. A photo removed before its owner is suspended or asks for deletion (`glow_chat`'s `suspend` and `delete`) then stays `removal_pending`: its purge cannot be asked, an acknowledgment for a purge already asked is refused, and its objects stay in storage.
- **The Dev Manager approved a correction** (DM-58 section 3: `docs/continuity/dev-manager/reviews/2026-11-11-dm-58-sv2-stage-b-decisions.md`). The brief's "Stage B, correction C1 (DM-58 item 9)" lists your three items. **It is your specification;** where this prompt summarizes it, the brief wins.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 10. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only "Stage B, correction C1"'s owned paths:
    - `services/api/glow_profiles/tx.py` and `services/api/glow_profiles/media.py`;
    - `services/api/tests/`: `test_profiles_offline.py` and `test_profile_media.py`;
    - `proofs/postgres-ordering/**`: the profile suite (`glow_ordering_proof/profile_cases.py`, `profile_support.py`), its offline tests and the README;
    - `docs/architecture/data-model.md` (the `MediaAsset` row) and `docs/architecture/production-contracts.md` (the F05 server mapping);
    - the record's new section "Stage B, correction C1";
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule** (the brief's "The stop rule (C1)"). Stop and report, with no further change, if the correction needs:
  - a path outside the owned paths: `glow_chat` (you call `suspend` and `delete`, never change them), `glow_identity`, `glow_domain` and `glow_api` included;
  - a model, migration, DTO or registry entry, the workflow, a lock file or a dependency;
  - a change to any other step's account-state gate: every other photo command, staff operation, system step and read keeps `lock_account` or `read_account_shared`;
  - a provider call or a credential.

  Stop too if a new check fails on the code at `d8f1bad` in a way that item 1 does not explain. A reversal's temporary edit of code is allowed, and must be undone.
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
  - weaken or delete a test to make the suite pass. Changing `LockOrderTests`' expectation for the two writers and `CASE_COUNT` follows the brief; say what each change is.

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
git switch -C <your session branch> <START_SHA>   # Stage B's session: claude/sweet-ramanujan-wkn311; <START_SHA> already contains its e7d6616
git rev-parse HEAD                                  # must print <START_SHA>
git diff --name-only d8f1bade8198c4c3f504ce9ca0a9279ef78b94bd HEAD | grep -v -E '\.md$'   # must print nothing: the code is d8f1bad's
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/api proofs/postgres-ordering docs/architecture/data-model.md docs/architecture/production-contracts.md 'docs/testing/evidence/*sv2*'   # must print nothing
grep -rn 'lock_account_any_state' services/api proofs   # must print nothing
grep -c '^## Stage B, correction C1' docs/testing/evidence/2026-11-10-sv2-profiles-media.md   # must print 0
grep -c '^## Stage B, correction C1 (DM-58 item 9)' docs/planning/sv2-profiles-media.md        # must print 1
```

If a check fails, stop and report. The prompt is stale if any of these holds:
- `<START_SHA>` is not on the live manager branch;
- an owned path changed there after it;
- "Stage B, correction C1" is already recorded.

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`; `proofs/postgres-ordering/README.md`;
- **the brief,** revision 8: D10 (its bullet on reorder and removal), acceptance check 10, and "Stage B, correction C1 (DM-58 item 9)";
- **DM-58's report,** sections 3 and 7;
- **the record:** "Stage B" and "Manager verification of Stage B", with Codex's finding on `82d246b`;
- **the code you change:** `glow_profiles/tx.py` (`lock_account`, `read_account_shared`, `run`) and `glow_profiles/media.py`, whole;
- **the code you call** (read only): `glow_chat/contact.py`, `suspend`, `delete` and `_revoke_account`;
- **the tests you change:** `services/api/tests/test_profiles_offline.py` (`LockOrderTests`, and the state-write guard's allowlist), `services/api/tests/test_profile_media.py`, and `proofs/postgres-ordering/glow_ordering_proof/profile_cases.py`'s media cases, with `profile_support.py` and `tests/test_profile_offline.py`.

## 3. What to do

1. **The items of "Stage B, correction C1", in order.** For each: the change, its tests, and its reversals. A reversal is a temporary edit that must make a test fail; run it, then undo it, and check the file's SHA-256 against its committed state. Record the edit and the failing output.
   - **Item 1, the two writers:** `lock_account_any_state` in `tx.py`, beside `lock_account`: the account row `FOR UPDATE`, an absent row refused as `account_missing`, and `after_first_lock` signalled as `lock_account` does, with no state check. `request_purge` and `acknowledge_deletion` call it first, in place of `lock_account`. The purge still asks the hold port first. Nothing else changes its lock.
   - **Item 2, the tests:**
     - `LockOrderTests` expects `lock_account_any_state` first in the two writers, and `lock_account` or `read_account_shared` everywhere else, as today;
     - the three suite cases the brief names: removed, then suspended, then purged; purge asked, then deletion asked, then completed; and `record_upload`, `review` and `run_check` still refusing an inactive owner (`account_not_active`). In the first two, check that delivery stays withheld throughout and the asset becomes `removed` only after every object's acknowledgment;
     - `CASE_COUNT` becomes 67, with the offline test that pins it;
     - **the reversals:** `lock_account` restored in `request_purge`, and in `acknowledge_deletion`, each failing its suite case and `LockOrderTests`; `lock_account_any_state` in `review` failing the third case. Run each reversal's offline tests, and its suite run as iteration if Docker allows.

     A line C1 moves in a file C3's state-write guard pins by number updates the allowlist in the same change.
   - **Item 3, the records:** the data model's `MediaAsset` row and the contract document's F05 server mapping say the purge and the deletion acknowledgment run in any account state, under the account row's lock, and every other photo step refuses an account that is not active; the proof README's profile-suite paragraph names the suite's case count (67) and Stage B's media cases, where it now says 53.
2. **The local checks:**
   - **API,** in `services/api`: `python3.12 -m venv .venv` and `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`. Then, with `GLOW_ENV=test`: `manage.py check`, `manage.py test tests --verbosity 2`, `ruff check .`, `ruff format --check .` and `mypy`;
   - **the contract tests:** `PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests -v`, from `services/api`;
   - **the proof,** in `proofs/postgres-ordering`: the same install, then `python -m unittest discover -s tests -t . -v`, `ruff check .`, `ruff format --check .` and `mypy`;
   - **the profile suite** on a local throwaway database under D4, if Docker allows, as iteration: 67 cases.
3. **The run of record.** Commit and push your code and test changes, then wait for its Foundation run to finish (the push rule). Read it with your GitHub tools:
   - every job's conclusion, and the gate's line (`Application checks passed`);
   - the API and proof test counts;
   - the profile suite's count and time, the profile phase's duration and both scans' lines;
   - the second profile run's refusal and its counts;
   - whether a toolchain retry fired.

   If it fails, stop and report the failing job and its log lines. Do not re-run it.

## 4. The record

Add a section `## Stage B, correction C1` at the end of `docs/testing/evidence/2026-11-10-sv2-profiles-media.md`, holding:
- the start gate's results, the environment check (names only) and the toolchain versions;
- for each item: the files, the checks, the reversals and their failing output;
- each F05 step's account-state rule after C1, as a list the exact-head review's threat model can use: which steps lock in any state, and which refuse an account that is not active;
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
- for each of items 1 to 3: what changed, its checks, and each reversal's result;
- each local check's result;
- the run of record: its ID, every job, the gate's line, the counts, the profile phase and whether a retry fired;
- anything that met the stop rule, every decision and deviation, and what you could not run.

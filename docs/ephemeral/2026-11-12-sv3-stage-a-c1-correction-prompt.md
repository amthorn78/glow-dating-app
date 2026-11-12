# SV3 Stage A correction C1 prompt — account locks `FOR NO KEY UPDATE`, and a random tie-break (DM-61)

- **Owner:** App Manager 11. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 2, 12 November 2026.** Revision 1 (`1ffff7d`) named the tie-break's files without `eligibility.py`, whose `parameters` passes the key's pads to the database. Revision 2 names it and adds Codex's CX2 on `1ffff7d` to "What came before". The work is unchanged.
- **Durable brief:** [SV3 — The eligibility, discovery and interactions slice](../planning/sv3-eligibility-discovery-interactions.md), revision 3, "Stage A, correction C1 (DM-61)", with D2, D6, D14, check 5, the owned paths and the exclusions as K1 to K7 wrote them.
- **Where the result goes:**
  - the session's changes in C1's owned paths, and its record, a new section "Stage A, correction C1" in `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md`, on its own branch;
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.21 (confidence 0.79); rung probabilities low 0.00, medium 0.05, high 0.70, extra high 0.24, max 0.01, ultracode 0.00. Model probabilities Fable 5.1 0.10, Opus 5.5 0.88, Sonnet 5.5 0.02, Haiku 5.5 0.00 (confidence 0.84). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.005, Fable 5.1 at high 0.070, Fable 5.1 at extra high 0.024, Fable 5.1 at max 0.001, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.044, Opus 5.5 at high 0.616, Opus 5.5 at extra high 0.211, Opus 5.5 at max 0.009, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.001, Sonnet 5.5 at high 0.014, Sonnet 5.5 at extra high 0.005, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-12T00:39:06Z, for revision 2. Nathan picks the cell.
  - **Revision 1's reading,** from the same action text: the same cell, Opus 5.5 at high (score 2.31, confidence 0.75; high 0.64, extra high 0.32; Opus 5.5 0.90), sent 2026-11-12T00:34:16Z.
- **The Dev Manager's read:** none before it runs. The brief's revision 3 applies DM-61's K1 to K7 as written, and DM-61 says they need no read before this prompt (DM-61, section 2). This prompt authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Then, in order:
  - the manager's verification;
  - PR45's run and Codex's review on C1's head;
  - the exact-head code and security review of `ad9ff08` and C1 together, with a written threat model (DM-61 section 5);
  - the Dev Manager's pre-merge read.
- **Deletion condition:** prune after SV3 Stage A's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are **correction C1 of SV3's Stage A**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 2, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **Stage A** built eligibility and discovery in `services/api/glow_discovery`, sealed until P11, with a discovery suite on a fourth disposable database. Its code head is `ad9ff08`, integrated by fast-forward into PR45. Its run of record, PR45's run 43113579295, passed every job, with the discovery suite at 32/32. The evidence record's "Stage A" and "Manager verification of Stage A" describe it.
- **Codex's review of PR45** found CX1, a lock cycle in page creation. `pages.create` locks the viewer's account `FOR UPDATE`, then inserts entries that reference the candidates' accounts. PostgreSQL's foreign-key check takes `FOR KEY SHARE` on each referenced row, and `FOR UPDATE` blocks it. So two mutually eligible viewers creating pages at once can deadlock, and so can a page and a `glow_chat` pair writer (`block`, for one) whose lower account is the candidate.
- **The manager's verification** raised V1. The keyed tie-break computed HMAC in SQL with the key's pads as statement parameters, so a log that records statements or parameters records the key.
- **Codex's review of `1ffff7d`** (the commit that held this prompt's revision 1) found CX2, which is V1 with one more fact. Django 5.2's psycopg 3 backend binds parameters on the client by default, so the pads are written into the statement's text, and PostgreSQL logs the text of a failing or cancelled statement by default. K2 takes the key out of SQL, so it closes CX2 too.
- **The Dev Manager ruled** (DM-61: `docs/continuity/dev-manager/reviews/2026-11-12-dm-61-sv3-stage-a-lock-cycle.md`):
  - **CX1:** every explicit lock of an `AppAccount` row becomes `FOR NO KEY UPDATE`, in the app and in the ordering proof's reference design (K1, K5);
  - **V1:** the tie-break becomes a random value drawn inside the selection, with no key at all (K2, replacing DM-60's Q2).
- **The brief's revision 3 applies them,** in D2, D6, D14, check 5, the owned paths and the exclusions, and lists your four items in "Stage A, correction C1 (DM-61)". **It is your specification;** where this prompt summarizes it, the brief wins.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 11. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only C1's owned paths:
    - **the account locks,** as K5 lists them, and nothing else in these files:
      - `services/api/glow_profiles/tx.py` (`lock_account`, `lock_account_any_state`);
      - `services/api/glow_profiles/identity_verification.py`;
      - `services/api/glow_identity/revocation.py`;
      - `services/api/glow_identity/age.py`;
      - `services/api/glow_chat/contact.py` (`_lock` for `AppAccount` rows only; every other row's lock, and every writer's body, unchanged);
      - the module docstrings of `services/api/glow_profiles/operations.py` and `media.py`;
      - the reference design's account locks in `proofs/postgres-ordering/glow_ordering_proof/reference.py`;
    - **the tie-break:** `services/api/glow_discovery/**`, the brief's own path for Stage A: above all `predicates.py`, `pages.py`, `keys.py` and `eligibility.py`, whose `parameters` passes the pads;
    - **the tests:** `services/api/tests/` (the discovery tests, and the pin of the two lock functions' bodies in `test_profiles_offline.py`);
    - **the proof:** `proofs/postgres-ordering/**`, that is, the discovery suite's cases and support, the scan of account locks, the offline tests and the README;
    - **the records:**
      - `docs/architecture/data-model.md`, where it states the account lock's mode or the keyed tie-break;
      - `docs/architecture/production-contracts.md`, F07's server section;
      - `docs/testing/p11-deferred-acceptance.md`: the revocation lock-wait line, and DB11's "stable keyed order";
      - the record's new section "Stage A, correction C1";
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule** (the brief's "The stop rule (C1)"). Stop and report, with no further change, if C1 needs any of these:
  - a model, a migration, a DTO, a registry entry, the workflow, a lock file or a dependency;
  - a change in `glow_chat`, `glow_identity` or `glow_profiles` beyond K5's list;
  - an account lock that cannot be `FOR NO KEY UPDATE`, because something deletes an account row or changes its keys.

  Stop too if a control of the ordering suite no longer fails as designed, or if any of these fails on the corrected code: the ordering suite on either subject, the identity suite or the profile suite. A reversal's temporary edit of code is allowed, and must be undone.
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished. A newer push cancels the earlier run's application jobs, and the run of record is lost. Push your records commit only after the run of record has finished. The workflow runs on pushes to `claude/**` and `ccr-**`; if your branch is named otherwise, say so in the report, since no run starts.
  - **If GitHub never starts the run** (it stays `queued` with no jobs for 30 minutes, as Stage A's did), do not re-run it, dispatch it, push an empty commit, or ask anyone to re-run it (OD-58). Record it, push your records commit, and report. The manager's PR run is then the run of record (the manager workflow, step 5).
- **Network:**
  - PyPI and the npm registry, for `pip install --require-hashes` and `npm ci --ignore-scripts` from the existing locks;
  - Docker Hub, only to pull the PostgreSQL image the CI job pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`) for a local run.

  A page you cannot reach is named as unread, never filled from memory.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions):
  - a throwaway PostgreSQL in Docker, from the CI job's pinned image, on loopback only;
  - a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present;
  - removed afterwards.

  Local passes are "iteration, not evidence"; the run of record is CI's. If Docker or the image is unavailable, iterate through CI and say so.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, password, code, token, session key or signing key, in any form;
  - read, print or use the value of any `AWS_*` variable (section 1);
  - make test data that looks real;
  - call any provider or HDE, send any email, or run any command in `proofs/stream-chat/`;
  - connect to any database but a throwaway one you started under D4's conditions, HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script;
  - weaken or delete a test to make the suite pass.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:** `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` or `PG*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG)'` prints names only. If any is present, stop and report.
3. **Three AWS names are expected:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_CA_BUNDLE`. `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values, and pass none to a command.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them.
5. **The toolchain:** CPython 3.12.14 as `python3.12`; Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, first on PATH; Docker if present. Record their versions.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API). The proxy and CA variables pass by reference, never printed.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git diff --quiet ad9ff081e26535ab89eb1187c7b69ca96fac2ef4 HEAD -- .github scripts services apps packages proofs ':!*.md' && echo "Stage A's code head"   # must print the line
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/api proofs/postgres-ordering packages apps/mobile/src/contracts .github docs/architecture docs/testing/p11-deferred-acceptance.md 'docs/testing/evidence/*sv3*'   # must print nothing
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md | grep -c -E '^#+ Stage A, correction C1'   # must print 0
```

If a check fails, stop and report. The prompt is stale if:
- `<START_SHA>` is not on the live manager branch;
- the live branch has changed an owned path since it;
- or the record already holds "Stage A, correction C1".

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`; `proofs/postgres-ordering/README.md`;
- the brief, revision 3: D2, D6, D14, check 5, the owned paths, the exclusions, "Review plan" and "Stage A, correction C1 (DM-61)";
- DM-61's report, whole, above all section 3.4 and section 4.2, which give the proof's cases and reversals;
- the evidence record's "Stage A", "Manager verification of Stage A" and "Codex on `7e4d826`";
- the P06.DB brief's D5 (the reference design) and the data model's "unit of work" table;
- every file in the owned paths that you change, whole, and `glow_discovery/pages.py`, `predicates.py`, `keys.py`, `eligibility.py`, the discovery suite (`discovery_cases.py`, `discovery_support.py`, `discovery_suite.py`) and its probes;
- PostgreSQL 17's manual on row-level locks ("Explicit Locking", Table 13.3), if you can reach it; if not, say so.

## 3. What to do

1. **Account locks `FOR NO KEY UPDATE`** (item 1; K1, K5):
   - Every explicit lock of an `AppAccount` row in the places K5 lists becomes `select_for_update(no_key=True)`, with each docstring that states the mode. Change nothing else in those files.
   - Find every explicit `AppAccount` lock by a scan of `services/api` and the reference design, not by this list alone. A lock outside K5's list is a stop.
   - Update the test that pins the two lock functions' bodies.
2. **The random tie-break** (item 2; K2):
   - The selection draws `gen_random_uuid()` for each candidate and orders by it within a band. The entries' positions keep the order, and nothing stores the value.
   - Remove `keys.tie_break`, `keys.sql_pads`, `predicates.TIE_BREAK` and their parameters (`ipad` and `opad`, set in `eligibility.parameters`). Keep the cursor's MAC as it is.
3. **The proof** (item 3; K3, K4; DM-61 sections 3.4 and 4.2), with the probes holding each interleaving at its locks, from separate connections:
   - **Codex's cycle:** two mutually eligible viewers create batches at once, each holding its own account lock before either writes its entries, in both orders. Both pages succeed.
   - **The second cycle:** `glow_chat`'s `block` between a candidate and the viewer, the candidate's account below the viewer's, races the viewer's page creation in both interleavings. Both succeed.
   - **The rule:** a page whose candidate's writer holds that candidate's account lock completes without waiting.
   - **The scan:** no explicit lock of an `AppAccount` row in `services/api` or the reference design is anything but `FOR NO KEY UPDATE`.
   - **The tie-break:**
     - no executed statement or parameter carries a value derived from `SECRET_KEY`, the statement's text as sent included (client-side binding writes the parameters into it);
     - the order is stable within a batch, across its pages;
     - two batches over the same ten or more candidates in one band are ordered differently.
   - **The reversals,** each run and recorded with its failing output:
     - the account locks `FOR UPDATE` again: the first two cases deadlock (`40P01`, one side `provider_unavailable`), and the third waits;
     - a planted `FOR UPDATE` lock fails the scan;
     - an order computable from the batch's and the profiles' IDs (an unkeyed hash, or the profile ID) fails the tie-break check.
   - **Unchanged:** the ordering suite on both subjects, with every control failing as designed; the identity and profile suites passing; and the discovery phase within the job's 30 minutes.
4. **The records** (item 4): the data model, the contract document's F07 server section, and the P11 plan's two lines, where they state the account lock's mode or the keyed tie-break. Rewrite only those sentences.
5. **The local checks:**
   - **API,** in `services/api`: `python3.12 -m venv .venv`, then `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`. Then, with `GLOW_ENV=test`: `manage.py check`, `manage.py test tests --verbosity 2`, `smoke.py`, `ruff check .`, `ruff format --check .`, `mypy` and `python -m glow_persistence.static_check`;
   - **the proof,** in `proofs/postgres-ordering`: its venv and hash-locked install, its offline tests under `env -i`, Ruff and mypy;
   - **the contracts and the mobile app:** their checks, to show nothing there changed (`npm ci --ignore-scripts` in `apps/mobile` before `npm run check` in `packages/contracts`, since its corpus test loads the mobile app's generated validators);
   - **a local database run,** if Docker allows it under D4's conditions: the ordering, identity, profile and discovery suites, as iteration, not evidence.
6. **The run of record.**
   - Commit and push your code. Wait for the Foundation run on your last code commit to finish (the push rule).
   - Read it with your GitHub tools: every job's conclusion; the gate's line (`Application checks passed`); the ordering, identity, profile and discovery suites' results; the discovery phase's duration; whether a retry fired; and that no secret appears in the job's log.
   - If it fails, stop and report the failing job and its log lines. Do not re-run it, and push no fix without saying so in the report.

## 4. The record

Add a section "Stage A, correction C1" to `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md`:
- the start gate's results, the environment check (names only) and the toolchain versions;
- every explicit `AppAccount` lock found, its file and line, before and after;
- the tie-break's change, and what was removed;
- each new case and each reversal, with its failing output;
- **the threat model's inputs,** updated:
  - each writer's locks and their modes;
  - the cycles that can no longer form, and why;
  - where the tie-break's randomness comes from, and that no key exists;
- every command you ran, with its result line, with local database runs listed as iteration, not evidence;
- the run of record: its ID, each job's result, the four suites' counts, the discovery phase's duration, and whether a retry fired;
- what you could not run, and why.

Commit each logical step with a clear message ending in the session's attribution lines. Push your records commit only after the run of record has finished. Confirm that `git status` is clean, and that `git diff --name-only <START_SHA> HEAD` lists only your owned paths.

## 5. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 2, from `<START_SHA>`), your branch, your code head and records head;
- the start gate's and the environment check's results;
- for each of the four items: what changed, its tests, and each reversal's result;
- every explicit `AppAccount` lock, before and after;
- each local check's result, and whether a local database run was used;
- the run of record: its ID, every job, the gate's line, the four suites' counts, the discovery phase's duration and whether a retry fired;
- anything that met the stop rule, every deviation from the brief, and what you could not run.

# SV3 Stage A correction C2 prompt — the exact-head review's findings, DM-63's texts and DM-64's scans

- **Owner:** App Manager 11. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 12 November 2026.**
- **Durable brief:** [SV3 — The eligibility, discovery and interactions slice](../planning/sv3-eligibility-discovery-interactions.md), revision 7, "Stage A, correction C2 (the exact-head review; DM-63, DM-64, DM-65)", with D8 and the owned paths as DM-65's RV1 and RV2 wrote them.
- **Where the result goes:**
  - the session's changes in C2's owned paths, and its record, a new section "Stage A, correction C2" in `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md`, on its own branch;
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 2.61 (confidence 0.72); rung probabilities low 0.00, medium 0.01, high 0.39, extra high 0.59, max 0.01, ultracode 0.00. Model probabilities Fable 5.1 0.02, Opus 5.5 0.98, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.97). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.008, Fable 5.1 at extra high 0.012, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.010, Opus 5.5 at high 0.382, Opus 5.5 at extra high 0.578, Opus 5.5 at max 0.010, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Flags: boundary between high and extra high. Sent 2026-11-12T18:42:33Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The brief's revision 7 applies DM-65's RV1 to RV3 as written, and DM-65 says they need no read before this prompt (DM-65 section 2). This prompt authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Then, in order:
  - the manager's verification, with the workflow's complete diff and the job's steps, and an AST check that `keys.py` and `reads.py` change only their docstrings;
  - PR45's run and Codex's review on C2's head;
  - the delta re-review of C2 against `b44e6f7` (DM-65 section 3.3);
  - the Dev Manager's pre-merge read.
- **Deletion condition:** prune after SV3 Stage A's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are **correction C2 of SV3's Stage A**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **Stage A** built eligibility and discovery in `services/api/glow_discovery`, sealed until P11. **Correction C1** made every explicit lock of an `AppAccount` row `FOR NO KEY UPDATE`, made the tie-break random with no key, and gave ADULT an age ceiling. Its code head is `b44e6f7`, and its run of record, 43147201199, passed every job, with the discovery suite at 38 of 38.
- **The exact-head review of `b44e6f7`** asked for changes, narrowly. It found no blocking finding, and every Dev Manager condition met in code. Its findings (the evidence record, "Exact-head review of Stage A"):
  - **F1 to F4,** tests that would pass where they should fail, or fail where the code is right;
  - **F5 and F6,** records that claim more than the code or the runs;
  - **F7,** a disclosure built into the two-way rule;
  - **N1 to N6,** nits.
- **The Dev Manager ruled** (its reports are in `docs/continuity/dev-manager/reviews/`):
  - **DM-63:** three texts still state the old account lock (LM5);
  - **DM-64:** the profile and discovery suites' scans can match what the run's own clock prints (T1 to T9). This is the cause of PR45's red run 43150501532;
  - **DM-65:** the dispositions, and C2's ten items (RV3), with the words for each (RV5 to RV8).
- **The brief's revision 7 lists your ten items** in "Stage A, correction C2". **It is your specification;** where this prompt summarizes it, the brief wins.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 11. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only C2's owned paths, as the brief's "Owned paths" gives them:
    - **the discovery suite and its offline tests:** `proofs/postgres-ordering/**`'s discovery cases, support and suite (items 1, 2 and 4), `account_lock_scan.py` and its offline tests (item 3);
    - **the scans:** for DM-64's item only, `profile_support.py`, `profile_cases.py`, `profile_suite.py` and `discovery_suite.py`, with their offline tests and the proof README's "Limits" (item 10);
    - **the docstrings and the comment, nothing else in those files:** `services/api/glow_discovery/keys.py`'s module docstring (item 7); `services/api/glow_chat/reads.py`'s module docstring sentence on what a revocation in flight holds (item 9); `discovery_settings.py`'s module docstring and `.github/workflows/foundation.yml`'s comment on the discovery database's keys (item 5);
    - **the tests:** `services/api/tests/test_discovery_offline.py`'s comment (item 5), and any API test C2's items need;
    - **the records:** `docs/architecture/discovery-fixtures.md` (item 5); the data model's `AccountAgeState` and `RecommendationBatch` rows (items 7 and 9); the P11 plan's SV3 Stage A entry (item 6); and, in the evidence record, the pointers (item 7), the "Cannot" line (item 8) and the new section "Stage A, correction C2";
  - use the given words where the brief points to them: DM-65 section 6 (RV5 to RV8), DM-63 section 4.3 (LM5) and DM-64 section 4.4 (item 10);
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule** (the brief's "The stop rule (C2)"). Stop and report, with no further change, if C2 needs any of these:
  - a model, a migration, a DTO, a registry entry, a lock file or a dependency;
  - a change to app code beyond the docstrings named here;
  - a change to a predicate, the selection, the recheck, a lock or a writer;
  - a workflow change beyond item 5's comment;
  - a clock text DM-64's rules cannot cover, or a change to `forms` or to what a ledger holds.

  Stop too if a control of the ordering suite no longer fails as designed, or if any of these fails on the corrected code: the ordering suite on either subject, the identity suite, the profile suite or the discovery suite. A reversal's temporary edit of code is allowed, and must be undone.
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished. A newer push cancels the earlier run's application jobs, and the run of record is lost. Push your records commit only after the run of record has finished. The workflow runs on pushes to `claude/**` and `ccr-**`; if your branch is named otherwise, say so in the report, since no run starts.
  - **If GitHub never starts the run** (it stays `queued` with no jobs for 30 minutes), do not re-run it, dispatch it, push an empty commit, or ask anyone to re-run it (OD-58). Record it, push your records commit, and report. The manager's PR run is then the run of record (the manager workflow, step 5).
  - **If the run fails,** stop and report the failing job and its log lines. Do not re-run it.
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
git diff --quiet b44e6f7e42abfa6d1f24ca9a429f07e15684fe74 HEAD -- .github scripts services apps packages proofs ':!*.md' && echo "C1's code head"   # must print the line
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/api proofs/postgres-ordering packages apps/mobile/src/contracts .github docs/architecture docs/testing/p11-deferred-acceptance.md 'docs/testing/evidence/*sv3*'   # must print nothing
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md | grep -c -E '^#+ Stage A, correction C2'   # must print 0
```

If a check fails, stop and report. The prompt is stale if:
- `<START_SHA>` is not on the live manager branch;
- the live branch has changed an owned path since it;
- or the record already holds "Stage A, correction C2".

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`; `proofs/postgres-ordering/README.md`;
- the brief, revision 7: D2, D3, D5, D7, D8, D14, D19, the acceptance checks, the owned paths, the exclusions, "Review plan" and "Stage A, correction C2";
- DM-65's report, whole, above all sections 3 and 6; DM-64's, whole, above all sections 3 and 4; DM-63's section 4.3;
- the evidence record's "Stage A, correction C1", "Manager verification of C1", "PR45's run on `4b771e0`" and "Exact-head review of Stage A";
- every file in the owned paths that you change, whole, and `glow_discovery/pages.py`, `predicates.py`, `eligibility.py`, `glow_profiles/tx.py` (`run`, the trace) and `media.py`'s `delivery_reference`, read only;
- the run 43150501532's failing case, against DM-64's diagnosis.

## 3. What to do

Make the brief's ten items, each with its tests and reversals, in its words:

1. **One snapshot, tested** (F1): the statement count in each page's transaction, and no write in a page with a cursor, with three reversals.
2. **The cursor's freshness, tested** (F2): `eligibility_version`, `blocks_version`, a batch not `ready`, and a distance choice no longer offered, each with its reversal.
3. **The lock scan's joins** (F3): every `select_for_update` whose queryset joins another table, passing only with `no_key=True` or an `of=` naming no path to `AppAccount`; the three planted cases and the two passing ones; the reversal. Run the scan over `services/api` and the reference design and report what it finds.
4. **The pointer-order case** (F4): grouped by the transaction's identity from its start, with a viewer of at least two candidates so a cursor page is checked; the reversal.
5. **The keyed tie-break's last texts** (F5), in RV5's words. `foundation.yml` changes in that comment only.
6. **The P11 plan's SV3 entry** (F6), in RV6's words. In your records commit, after the run of record, name C2's run of record in it.
7. **N1 and N6,** in RV7's words: `keys.py`'s module docstring, the data model's `AccountAgeState` sentence, and the pointer at the head of each Stage A paragraph of the record that C1 changed.
8. **The record's "Cannot" line** (F7), in RV8's words.
9. **The three texts that still state the old account lock** (LM5), in DM-63 section 4.3's words. Nothing else in `reads.py` changes.
10. **The scans and the run's own clock** (DM-64, T1 to T9), as DM-64 section 4.4 and the brief's item 10 give them: the coordinate, time and duration rules, the list (T5), the offline tests with DM-64 section 4.2's texts at least, the messages (T7), and the README's "Limits" (T8).

**The local checks:**
- **API,** in `services/api`: `python3.12 -m venv .venv`, then `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`. Then, with `GLOW_ENV=test`: `manage.py check`, `manage.py test tests --verbosity 2`, `smoke.py`, `ruff check .`, `ruff format --check .`, `mypy` and `python -m glow_persistence.static_check`;
- **the proof,** in `proofs/postgres-ordering`: its venv and hash-locked install, its offline tests under `env -i`, Ruff and mypy;
- **the contracts and the mobile app:** their checks, to show nothing there changed (`npm ci --ignore-scripts` in `apps/mobile` before `npm run check` in `packages/contracts`);
- **a local database run,** if Docker allows it under D4's conditions: the ordering, identity, profile and discovery suites, as iteration, not evidence. Run the profile and discovery suites more than once, since item 10 and item 4 address intermittent failures.

**The run of record:**
- Commit and push your code. Wait for the Foundation run on your last code commit to finish (the push rule).
- Read it with your GitHub tools: every job's conclusion; the gate's line (`Application checks passed`); the ordering, identity, profile and discovery suites' results; the profile and discovery phases' durations; whether a retry fired; and that no secret appears in the job's log.

## 4. The record

Add a section "Stage A, correction C2" to `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md`:
- the start gate's results, the environment check (names only) and the toolchain versions;
- for each of the ten items: what changed, its tests, and each reversal with its failing output;
- what the widened lock scan finds over `services/api` and the reference design;
- **T5's list:** every value the run's clock prints into each text the scans read, with the rule that covers it;
- every command you ran, with its result line, with local database runs listed as iteration, not evidence;
- the run of record: its ID, each job's result, the four suites' counts, the phases' durations, and whether a retry fired;
- what you could not run, and why.

Commit each logical step with a clear message ending in the session's attribution lines. Push your records commit only after the run of record has finished. Confirm that `git status` is clean, and that `git diff --name-only <START_SHA> HEAD` lists only your owned paths.

## 5. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch, your code head and records head;
- the start gate's and the environment check's results;
- for each of the ten items: what changed, its tests, and each reversal's result;
- the widened scan's findings;
- each local check's result, and whether a local database run was used, with how many runs of the profile and discovery suites;
- the run of record: its ID, every job, the gate's line, the four suites' counts, the phases' durations and whether a retry fired;
- anything that met the stop rule, every deviation from the brief, and what you could not run.

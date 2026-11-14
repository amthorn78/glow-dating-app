# SV3 Stage A correction C3 prompt — the lock scan's joins and the one-snapshot case (C2's delta re-review; DM-67)

- **Owner:** App Manager 11. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 13 November 2026.**
- **Durable brief:** [SV3 — The eligibility, discovery and interactions slice](../planning/sv3-eligibility-discovery-interactions.md), revision 9, "Stage A, correction C3 (C2's delta re-review; DM-67)", with C3's owned paths as DM-67's GD1 and GD2 wrote them.
- **Where the result goes:**
  - the session's changes in C3's owned paths, and its record, a new section "Stage A, correction C3" in `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md`, on its own branch;
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.31 (confidence 0.76); rung probabilities low 0.00, medium 0.02, high 0.66, extra high 0.30, max 0.02, ultracode 0.00. Model probabilities Fable 5.1 0.04, Opus 5.5 0.96, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.95). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.001, Fable 5.1 at high 0.026, Fable 5.1 at extra high 0.012, Fable 5.1 at max 0.001, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.019, Opus 5.5 at high 0.634, Opus 5.5 at extra high 0.288, Opus 5.5 at max 0.019, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-13T04:30:18Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The brief's revision 9 applies DM-67's GD1 and GD2 as written, and DM-67 says they need no further read before this prompt (DM-67 section 2). This prompt authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Then, in order:
  - the manager's verification;
  - PR45's run and Codex's review on C3's head;
  - C3's delta re-review against `303fdcc` (the brief's "C3's review");
  - the Dev Manager's pre-merge read.
- **Deletion condition:** prune after SV3 Stage A's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are **correction C3 of SV3's Stage A**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **Stage A** built eligibility and discovery in `services/api/glow_discovery`, sealed until P11. Correction C1 made every explicit lock of an `AppAccount` row `FOR NO KEY UPDATE`.
- **Correction C2** fixed the exact-head review's findings, at code head `303fdcc`. Among other things, it:
  - added `pages.one_snapshot_statements`, a case that counts the statements in each page's transaction;
  - widened the lock scan (`account_lock_scan.py`) to judge every `select_for_update` whose queryset joins another table;
  - changed the privacy scans so the run's own clock no longer counts as a leaked value.

  Its run of record, 43337467715, passed every job.
- **C2's delta re-review** asked for changes, narrowly (the evidence record, "Delta re-review of C2"). It found no blocking finding and no app change, but two of C2's guards can pass while what they guard is wrong:
  - **L1:** a generic lock with a join passes with `of=`, though the scan's docstring requires `no_key=True`;
  - **L2:** the scan does not see several join forms: a `Q` or an `F` held in a variable or from a helper, `latest()` or `earliest()` through a relation, `extra()`, a join added through later variables, and a reverse path to `AppAccount`;
  - **S1:** before the probe point, the case accepts any account-table statement whose parameters include the viewer's ID;
  - **S2:** the cursor page's write check reads its transaction only.

  Also **R1:** the README states T3's rule more narrowly than it is; and **N2:** T5's list leaves out two case-level texts. Codex found L1, L2's `Q` variable, S1 and S2 too, on PR45 (`3000014`).
- **The Dev Manager ruled** (DM-67, in `docs/continuity/dev-manager/reviews/`). It approved each fix, made L2's and S1's rules exact, and gave the words: **GD1** is your section in the brief, and **GD3 to GD10** are the record texts you apply.
- **The brief's revision 9 lists your five items** in "Stage A, correction C3". **It is your specification;** where this prompt summarizes it, the brief wins.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 11. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only C3's owned paths, as the brief's "Owned paths" gives them (GD2):
    - `proofs/postgres-ordering/glow_ordering_proof/account_lock_scan.py` and `discovery_cases.py`;
    - their offline tests in `proofs/postgres-ordering/tests/`;
    - the proof README;
    - the evidence record;
    - the P11 plan's SV3 entry, its runs of record only;
  - use the given words where the brief points to them: DM-67 section 3.10's GD3 to GD10, applied in order, each old passage found once. Fill in GD10's `RUN` and `HEAD` with your run of record and code head;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule** (the brief's "The stop rule (C3)"). Stop and report, with no further change, if C3 needs any of these:
  - a change outside its owned paths;
  - any change to app code, a predicate, the selection, the recheck, a lock, a writer or the workflow.

  Stop and report too:
  - if the corrected scan refuses an existing lock in `services/api` or the reference design;
  - if a page makes a statement before the probe point that item 3's list does not name. Report the statement; do not widen the list;
  - if a control of the ordering suite no longer fails as designed;
  - if any of these fails on the corrected code: the ordering suite on either subject, or the identity, profile or discovery suite.

  A reversal's temporary edit of code is allowed, and must be undone.
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished. A newer push cancels the earlier run's application jobs, and the run of record is lost. Push your records commit only after the run of record has finished. The workflow runs on pushes to `claude/**` and `ccr-**`; if your branch is named otherwise, say so in the report, since no run starts.
  - **If GitHub never starts the run** (it stays `queued` with no jobs for 30 minutes), do not re-run it, dispatch it, push an empty commit, or ask anyone to re-run it (OD-58). Record it, push your records commit, and report. The manager's PR run is then the run of record (the manager workflow, step 5).
  - **If the run fails,** stop and report the failing job and its log lines. Do not re-run it.
- **Network:**
  - PyPI, for `pip install --require-hashes` from the existing locks;
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
5. **The toolchain:** CPython 3.12.14 as `python3.12`; Docker if present. Record their versions.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables. The proxy and CA variables pass by reference, never printed.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git diff --quiet 303fdcca30788bf88a65f65e50d532971ab435a4 HEAD -- .github scripts services apps packages proofs ':!*.md' && echo "C2's code head"   # must print the line
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- proofs/postgres-ordering docs/testing/p11-deferred-acceptance.md 'docs/testing/evidence/*sv3*'   # must print nothing
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md | grep -c -E '^#+ Stage A, correction C3'   # must print 0
```

If a check fails, stop and report. The prompt is stale if:
- `<START_SHA>` is not on the live manager branch;
- the live branch has changed an owned path since it;
- or the record already holds "Stage A, correction C3".

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`; `proofs/postgres-ordering/README.md`;
- the brief, revision 9: D2, D14, the owned paths, "Stage A, correction C2" (its item 3 and its item 1) and "Stage A, correction C3";
- DM-67's report, whole, above all sections 3.3 to 3.10;
- the evidence record's "Stage A, correction C2", "Manager verification of C2" and "Delta re-review of C2";
- `account_lock_scan.py`, `discovery_cases.py` (`_Statements`, `_member_tables`, `WRITE`, `pages.one_snapshot_statements`) and their offline tests, whole;
- for item 3's list, read only: `glow_discovery/pages.py` (`create`, `continue_page`, `_with_photos`), `glow_profiles/tx.py` (`run`, `lock_account`, `read_account_shared`), `glow_profiles/media.py` (`delivery_reference`, `_owner`), `glow_discovery/predicates.py` (`VIEWER`) and `glow_persistence/models.py` (`AppAccount`'s fields).

## 3. What to do

Make the brief's five items, each with its tests and reversals, in its words:

1. **A generic lock with a join** (L1): it passes only with `no_key=True`. Its offline test plants the review's helper and sees it refused, and the same helper with `no_key=True` pass. The reversal is the scan as at `303fdcc`.
2. **The joins the scan does not see** (L2): the arguments, methods, variables, reverse relations and SQL rules, exactly as the brief's item 2 gives them. A keyword's value is a value unless it is, or names, a `Q` or an `F`. Each form gets an offline test that plants it and sees it refused, with its reversal against the scan as at `303fdcc`:
   - a `Q` and an `F` held in variables;
   - a `Q` from a helper;
   - `latest("account__created_at")`;
   - `extra(tables=[…])`;
   - a join added two variables after the lock;
   - `User.objects.filter(appaccount=…)` locked `FOR UPDATE`;
   - `FOR UPDATE` in SQL with `JOIN {}`, with `FROM {table}` in a `.format` string, and as a clause in a string of its own.

   Run the scan over `services/api` and the reference design. Report what it finds; the counts must stay 52 calls read, none locking a queryset that joins, and the seven explicit account locks.
3. **Before the probe point, an explicit list** (S1):
   - **The list:** `predicates.VIEWER`, with the viewer's ID as its `viewer` parameter; and one shape of a read of the viewer's own account row, as the brief's item 3 gives it.
   - **Where it applies:** every phase before the probe point, the phase before the transaction begins included.
   - **The matcher's offline tests:** the three account reads pass; a read naming another ID, an `IN` list, a join, a subquery, and `VIEWER` for another member each fail.
   - **The database reversals, each failing the case:**
     - D, a pre-probe read of other members' accounts;
     - `VIEWER` run for another member before the probe point.
4. **A page by cursor writes nothing, in any phase** (S2): the write check reads every phase the probe records for a page by cursor. Its database reversal E, a write after the cursor page's transaction, fails the case.
5. **The records** (R1, N2; L2's limits), in DM-67's GD3 to GD10:
   - the README's SV3 heading (GD3), the lock scan's row in the file table (GD4), T3's rule and limit in "Limits" (GD5, GD6), and a "Limits" entry for the lock scan (GD7);
   - the record's two new rows in T5's table (GD8), and a pointer from C2's item 3 row (GD9);
   - the P11 plan's runs-of-record sentence (GD10), in your records commit, after the run of record.

   The README's SV3 paragraph also gains a sentence on what C3 adds, as for C1 and C2, in your words.

**The local checks:**
- **the proof,** in `proofs/postgres-ordering`: its venv and hash-locked install (`requirements-dev.lock`), its offline tests under `env -i`, Ruff, `ruff format --check` and mypy; and the lock scan, `python -m glow_ordering_proof.account_lock_scan`, with its counts;
- **a local database run,** if Docker allows it under D4's conditions: the discovery suite with item 3's and item 4's database reversals, and once clean; the ordering, identity and profile suites once each. All are iteration, not evidence.

**The run of record:**
- Commit and push your code. Wait for the Foundation run on your last code commit to finish (the push rule).
- Read it with your GitHub tools:
  - every job's conclusion, and the gate's line (`Application checks passed`);
  - the ordering, identity, profile and discovery suites' results, and the profile and discovery phases' durations;
  - the lock scan case's line;
  - whether a retry fired, and that no secret appears in the job's log.

## 4. The record

Add a section "Stage A, correction C3" to `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md`, at its end:
- the start gate's results, the environment check (names only) and the toolchain versions;
- for each of the five items: what changed, its tests, and each reversal with its failing output;
- what the corrected lock scan finds over `services/api` and the reference design;
- the statements each page makes before the probe point, against item 3's list;
- every command you ran, with its result line, with local database runs listed as iteration, not evidence;
- the run of record: its ID, each job's result, the four suites' counts, the phases' durations, and whether a retry fired;
- every deviation from the brief, and what you could not run, and why.

Apply GD8 and GD9 where they stand in the record, above your section. Commit each logical step with a clear message ending in the session's attribution lines. Push your records commit only after the run of record has finished. Confirm that `git status` is clean, and that `git diff --name-only <START_SHA> HEAD` lists only your owned paths.

## 5. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch, your code head and records head;
- the start gate's and the environment check's results;
- for each of the five items: what changed, its tests, and each reversal's result;
- the corrected scan's findings, and the pages' pre-probe statements;
- each local check's result, and whether a local database run was used;
- the run of record: its ID, every job, the gate's line, the four suites' counts, the phases' durations and whether a retry fired;
- anything that met the stop rule, every deviation from the brief, and what you could not run.

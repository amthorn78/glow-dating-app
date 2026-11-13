# SV3 Stage A correction C4 prompt — the lock scan's last forms and the write check (C3's delta re-review; DM-68)

- **Owner:** App Manager 11. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 2, 13 November 2026.** Revision 1, from `0fbc130`, stopped at its start gate and changed nothing: the manager had appended a line to the evidence record, one of C4's owned paths, after that commit (`3bbc06f`; AM11-21). Revision 2 changes only its start commit and these notes.
- **Durable brief:** [SV3 — The eligibility, discovery and interactions slice](../planning/sv3-eligibility-discovery-interactions.md), revision 10, "Stage A, correction C4 (C3's delta re-review; DM-68)", with C4's owned paths as DM-68's SC1 and SC2 wrote them.
- **Where the result goes:**
  - the session's changes in C4's owned paths, and its record, a new section "Stage A, correction C4" in `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md`, on its own branch;
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.22 (confidence 0.82); rung probabilities low 0.00, medium 0.02, high 0.74, extra high 0.23, max 0.01, ultracode 0.00. Model probabilities Fable 5.1 0.01, Opus 5.5 0.99, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.99). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.007, Fable 5.1 at extra high 0.002, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.020, Opus 5.5 at high 0.733, Opus 5.5 at extra high 0.228, Opus 5.5 at max 0.010, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-13T18:18:03Z. Nathan picks the cell.
  - Revision 1's reading (Opus 5.5 at high, score 2.21, sent 2026-11-13T09:46:01Z) is superseded; revision 1 stopped at its start gate.
- **The Dev Manager's read:** none before it runs. The brief's revision 10 applies DM-68's SC1 to SC7 as written, and DM-68 says they need no further read before this prompt (DM-68 section 2). This prompt authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Then, in order:
  - the manager's verification;
  - PR45's run and Codex's review on C4's head;
  - C4's review against `72ace21`, under the brief's termination rule ("C4's review, and how the scan's line ends");
  - Dev Manager 5's pre-merge read.
- **Deletion condition:** prune after SV3 Stage A's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are **correction C4 of SV3's Stage A**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 2, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **Stage A** built eligibility and discovery in `services/api/glow_discovery`, sealed until P11. Correction C1 made every explicit lock of an `AppAccount` row `FOR NO KEY UPDATE`; C2 and C3 built and tightened two proof checks: a static scan of those locks (`account_lock_scan.py`) and `pages.one_snapshot_statements`.
- **C3** (code head `72ace21`; run of record 43369448338, every job passing) fixed C2's delta re-review findings under DM-67.
- **C3's delta re-review** asked for changes, narrowly (the evidence record, "Delta re-review of C3"). No app change, and no gap used by code today, but:
  - **F1 to F4:** the scan passes four join forms that lock the account row `FOR UPDATE`: a function given a path in a keyword's value, a combined queryset, `complex_filter()`, and an f-string in `of=`;
  - **F5:** a generic lock's `no_key=model is not AppAccount` passes;
  - **F6:** the write check misses a write to a table not named `glow_…`;
  - **F7, N1, N5:** limits to state; **N2:** two tests the pre-probe matcher lacks.
- **Dev Manager 5 ruled** (DM-68, in `docs/continuity/dev-manager/reviews/`). It approved each fix and widened two: F2 to `^` and to an account lock whose receiver is a combination, a conditional, an `or` or a `:=` expression (which C3's scan does not see as a lock at all), and F5 to require the lock's own variable on the left. It chose how the scan's line ends: after C4, the scan is a static check of the forms it names, its rules freeze, and a further unseen form is a stated limit, while a real account lock stays blocking; D14's check of the row locks the suites send comes in Stage B.
- **Revision 1 of this prompt** (from `0fbc130`) stopped at its start gate, with no change: the manager had added one line to the evidence record after its commit (Codex's review of `0fbc130`, which found F1 to F6 and nothing new). This revision starts after that line.
- **The brief's revision 10 lists your eight items** in "Stage A, correction C4". **It is your specification;** where this prompt summarizes it, the brief wins. **Your given words are DM-68's SC8 to SC11** (section 9 of its report).

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 11. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only C4's owned paths, as the brief's "Owned paths" gives them (SC2):
    - `proofs/postgres-ordering/glow_ordering_proof/account_lock_scan.py` and `discovery_cases.py`;
    - their offline tests in `proofs/postgres-ordering/tests/`;
    - the proof README;
    - the evidence record;
    - the P11 plan's SV3 entry, its runs of record only;
  - use the given words where the brief points to them: DM-68's SC8, SC9 and SC11, each old passage found once and applied in order, and SC10, placed in the scan's docstring after its first paragraph. Fill in SC11's `RUN` and `HEAD` with your run of record and code head;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule** (the brief's "The stop rule (C4)"). Stop and report, with no further change, if C4 needs any of these:
  - a change outside its owned paths;
  - any change to app code, a predicate, the selection, the recheck, a lock, a writer or the workflow.

  Stop and report too:
  - if the corrected scan refuses an existing lock in `services/api` or the reference design;
  - if the corrected write check counts a statement the real page by cursor sends as a write;
  - in either case, report it; do not narrow the words of items 1 to 6 to pass it;
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
git diff --quiet 72ace2179a7dff74fecf6b7f06de30b7a1454dcb HEAD -- .github scripts services apps packages proofs ':!*.md' && echo "C3's code head"   # must print the line
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- proofs/postgres-ordering docs/testing/p11-deferred-acceptance.md 'docs/testing/evidence/*sv3*'   # must print nothing
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md | grep -c -E '^#+ Stage A, correction C4'   # must print 0
```

If a check fails, stop and report. The prompt is stale if:
- `<START_SHA>` is not on the live manager branch;
- the live branch has changed an owned path since it;
- or the record already holds "Stage A, correction C4".

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`; `proofs/postgres-ordering/README.md`;
- the brief, revision 10: D2, D14, the owned paths, "Stage A, correction C3" and "Stage A, correction C4";
- DM-68's report, whole, above all sections 3 and 9; DM-67's section 3.10, for GD1's rule as it stood;
- the evidence record's "Stage A, correction C3", "Manager verification of C3" and "Delta re-review of C3";
- `account_lock_scan.py` and `discovery_cases.py` (`WRITE`, `_Statements`, `pages.one_snapshot_statements`) and their offline tests, whole;
- read only: the two generic helpers (`glow_chat/contact.py`'s `_lock`, the reference design's `_lock`), `glow_discovery/pages.py` (`create`, `continue_page`, `_with_photos`), `glow_profiles/tx.py` (`run`, `lock_account`, `read_account_shared`), `glow_profiles/media.py` (`delivery_reference`, `_owner`) and `glow_discovery/predicates.py` (`VIEWER`, `SELECTION`, `RECHECK`).

## 3. What to do

Make the brief's eight items, each with its tests and reversals, in its words:

1. **A function given a path, in a keyword's value** (F1): a call to a capitalised name other than `Q` and `F` that takes a string literal or an f-string counts as a join, written in the value or reached through a name it uses; any other call is a value. Plant the brief's three forms and see each refused; see its two controls pass. Its reversal is the scan as at `72ace21`.
2. **A queryset that is not a plain chain** (F2, widened): combinations (`&`, `|`, `^`), conditionals, `and`/`or` and `:=`, read through to every chain, inline or held in a name, before and after the lock, and as the lock's receiver. Plant the brief's forms (the review's `&`, assigned and inline; `^`; the account lock on a combination; an account lock on a conditional, an `or` and a `:=` receiver) and see each refused. Its reversal is the scan as at `72ace21`.
3. **`complex_filter()`** (F3): a lookup method; a dict or any argument but a literal `Q` (or a name assigned one) counts as a join. Its test and reversal as the brief gives them.
4. **`of=`, read only as literals** (F4): a tuple or list written in the call, every entry a plain string literal naming no path to `AppAccount`; anything else fails closed. Its test and reversal as the brief gives them.
5. **A generic lock's `no_key`, read by its syntax** (F5): the literal `True`, or, with no join, exactly `<the lock's own variable> is AppAccount`. Plant the brief's four forms and see each refused; the two existing helpers pass as they are. Its reversal is the scan as at `72ace21`.
6. **A write is anything but a read** (F6): a statement is a read only if it begins with `SELECT` or `WITH` and holds none of `INSERT`, `UPDATE`, `DELETE`, `MERGE`, `INTO`, `TRUNCATE` or `COPY`. Its offline tests as the brief lists them; its database reversal (`UPDATE auth_user …` after the cursor page's transaction) fails the case, and E and C2's write still fail it. The page with no cursor's control uses the same test.
7. **The matcher's tests** (N2): an `OR` condition and a join without an alias, each failing.
8. **The records:** SC10 in the scan's docstring; SC8 and SC9 in the README; the README's SV3 paragraph gains a sentence on what C4 adds, in your words; SC11 in the P11 plan, in your records commit after the run of record; and the record's section.

Run the scan over `services/api` and the reference design, and report its counts: they must stay 52 calls read, none locking a queryset that joins, and the seven explicit account locks.

**The local checks:**
- **the proof,** in `proofs/postgres-ordering`: its venv and hash-locked install (`requirements-dev.lock`), its offline tests under `env -i`, Ruff, `ruff format --check` and mypy; and the lock scan, `python -m glow_ordering_proof.account_lock_scan`, with its counts;
- **a local database run,** if Docker allows it under D4's conditions: the discovery suite once clean and with item 6's database reversals; the ordering, identity and profile suites once each. All are iteration, not evidence.

**The run of record:**
- Commit and push your code. Wait for the Foundation run on your last code commit to finish (the push rule).
- Read it with your GitHub tools:
  - every job's conclusion, and the gate's line (`Application checks passed`);
  - the ordering, identity, profile and discovery suites' results, and the profile and discovery phases' durations;
  - the lock scan case's line and `pages.one_snapshot_statements`' line;
  - whether a retry fired, and that no secret appears in the job's log.

## 4. The record

Add a section "Stage A, correction C4" to `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md`, at its end:
- the start gate's results, the environment check (names only) and the toolchain versions;
- for each of the eight items: what changed, its tests, and each reversal with its failing output;
- what the corrected scan finds over `services/api` and the reference design;
- the statements a page by cursor sends, each as the corrected write check reads it;
- every command you ran, with its result line, with local database runs listed as iteration, not evidence;
- the run of record: its ID, each job's result, the four suites' counts, the phases' durations, and whether a retry fired;
- every deviation from the brief, and what you could not run, and why.

Commit each logical step with a clear message ending in the session's attribution lines. Push your records commit only after the run of record has finished. Confirm that `git status` is clean, and that `git diff --name-only <START_SHA> HEAD` lists only your owned paths.

## 5. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 2, from `<START_SHA>`), your branch, your code head and records head;
- the start gate's and the environment check's results;
- for each of the eight items: what changed, its tests, and each reversal's result;
- the corrected scan's findings, and how the write check reads a page by cursor's statements;
- each local check's result, and whether a local database run was used;
- the run of record: its ID, every job, the gate's line, the four suites' counts, the phases' durations and whether a retry fired;
- anything that met the stop rule, every deviation from the brief, and what you could not run.

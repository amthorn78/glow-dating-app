# SV3 Stage B, B0 prompt — the proof's tooling: the lock scan's bound, its docstrings and pinning tests, T3's date rule and the database search's test (DM-71)

- **Owner:** App Manager 11. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 14 November 2026.**
- **Durable brief:** [SV3 — The eligibility, discovery and interactions slice](../planning/sv3-eligibility-discovery-interactions.md), revision 13, "Stage B, B0: the proof's tooling (DM-71)", with B0's owned paths as DM-71's CC2 wrote them.
- **Where the result goes:**
  - the session's changes in B0's owned paths, and its record, a new section "Stage B, B0" in `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md`, on its own branch;
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 1.74 (confidence 0.72); rung probabilities low 0.00, medium 0.34, high 0.58, extra high 0.08, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.96, Sonnet 5.5 0.04, Haiku 5.5 0.00 (confidence 0.95). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.326, Opus 5.5 at high 0.557, Opus 5.5 at extra high 0.077, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.014, Sonnet 5.5 at high 0.023, Sonnet 5.5 at extra high 0.003, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-14T23:51:26Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The brief's revision 13 applies DM-71's CC1 to CC4 as written, and DM-71 says they need no further read before this prompt (DM-71 section 2). This prompt authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Then, in order:
  - the manager's verification;
  - B0's own PR, from the manager branch, and Codex's review of its head;
  - B0's bounded delta re-review against `8d83474` (the brief's "B0's review");
  - Dev Manager 5's pre-merge read; the merge; then Stage B's prompt, from B0's merge commit.
- **Deletion condition:** prune after B0's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch (AM11-21).

---

You are **B0, the proof-tooling session of SV3's Stage B**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **SV3's Stage A is done.** It built eligibility and discovery in `services/api/glow_discovery`, sealed until P11, with corrections C1 to C5, and merged as PR45 at `8d83474` (the evidence record, "The merge receipt for Stage A"). Its proof added a static scan of explicit account row locks (`account_lock_scan.py`) and `pages.one_snapshot_statements`.
- **DM-68 froze the lock scan's rules after C4:** it is a static check of the forms its docstring names; any other form is a stated limit; its rules change only to correct a defect in a correction class, or by a design the Dev Manager reads. Every later SV3 review has the five correction classes of the brief's "C4's review, and how the scan's line ends" (class 3 as DM-70's BB1 words it).
- **Items were carried to Stage B** during Stage A's reviews (the carried-items file, "Carried to SV3 Stage B"). **DM-71** placed those that change only the proof's tooling in you, B0, in your own PR before Stage B: a bound on the scan's receiver rule (a design the Dev Manager read: 1,000 states, 100 names followed), the scan's docstrings, pinning tests, T3's date rule narrowed, an offline test of the profile suite's database search, two docstrings narrowed, the proof's two N5 items, and one more stated limit. Stage B, which builds the contact routes, starts from your merge.
- **The brief's revision 13 lists your nine items** in "Stage B, B0: the proof's tooling (DM-71)". **It is your specification, and its words are your given words;** where this prompt summarizes it, the brief wins. The carried-items file holds what each item points to; its sources are the evidence record's "Delta re-review of C2" (N1, N3) and "Delta re-review of C5" (F2's words, F3, F12).

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 11. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only B0's owned paths, as the brief's "Owned paths" gives them (CC2):
    - `proofs/postgres-ordering/glow_ordering_proof/account_lock_scan.py`;
    - in `discovery_cases.py`, `one_snapshot_statements`' docstring and the query plans' unused `batch` parameter only;
    - in `profile_support.py`, T3's rule and `forms` only, with the suites' calls of the value scans only to name the response headers' text for T3 (the member-value scans' calls, `values.found_in`, in `profile_suite.py` and `discovery_suite.py`);
    - the offline tests in `proofs/postgres-ordering/tests/`;
    - the proof README;
    - the evidence record;
    - the P11 plan's SV3 entry, its runs of record only;
  - **no app code:** nothing in `services/`, `packages/`, `apps/`, `.github/` or `scripts/`. `VIEWER`'s unused column is Stage B's;
  - **`profile_cases.py` is not yours:** item 6 is an offline test that calls `_found_in_database` unchanged. If it is unclear whether a call is one of the suites' calls of the value scans, stop and report it;
  - change the lock scan's rules only for item 1, the bound (DM-68's freeze);
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule** (the brief's "The stop rule (B0)"). Stop and report, with no further change, if B0 needs any of these:
  - a change outside its owned paths;
  - any change to app code, a predicate, the selection, the recheck, a lock, a writer, the workflow, or a rule of the lock scan beyond item 1.

  Stop and report too:
  - if the bounded scan changes any verdict or line of its output on the tree;
  - if a test of C1's to C5's sections no longer passes;
  - if the narrowed rule or the new date forms make the profile or discovery suite find a value in a clock text;
  - if a case can hold a date the run's clock prints, which the new forms would then match;
  - and, since the run of record needs all eight jobs: if any of the ordering suite (either subject, its controls failing as designed), the identity, profile or discovery suite fails on the corrected code.

  Report each; do not narrow the brief's words to pass it. A reversal's or a mutant's temporary edit of code is allowed, and must be undone.
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
git merge-base --is-ancestor origin/main HEAD && echo "main is in this commit"   # must print the line
git diff --quiet 8d83474a354603cee11b8a09fe66b63a3602074f HEAD -- .github scripts services apps packages proofs ':!*.md' && echo "main's code"   # must print the line
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- proofs/postgres-ordering docs/testing/p11-deferred-acceptance.md 'docs/testing/evidence/*sv3*'   # must print nothing
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md | grep -c -E '^#+ Stage B, B0'   # must print 0
```

If a check fails, stop and report. The prompt is stale if:
- `<START_SHA>` is not on the live manager branch;
- the live branch has changed an owned path since it;
- or the record already holds "Stage B, B0".

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`; `proofs/postgres-ordering/README.md`;
- the brief, revision 13: D2, D14, the owned paths, "Stage A, correction C4" (with "C4's review, and how the scan's line ends"), "Stage A, correction C5", and "Stage B, B0: the proof's tooling (DM-71)";
- DM-71's report, whole, above all sections 3.1, 3.2, 7 and 9; DM-70's sections 4.3 and 9 (BB9, BB10);
- the carried-items file's "Carried to SV3 Stage B";
- the evidence record's "Delta re-review of C2" (N1, N3), "Delta re-review of C4" and "Delta re-review of C5" (F2's words, F3 and F12), and DM-64's T1 to T9 as the record and the README state them;
- whole: `account_lock_scan.py`; `profile_support.py` (the value scans, T3 and `forms`); the value scans' calls in `profile_suite.py` and `discovery_suite.py`; `discovery_cases.py`'s `one_snapshot_statements` and the query plans; and their offline tests;
- read only: `profile_cases.py`'s `_found_in_database` (item 6).

## 3. What to do

Make the brief's nine items, each with its tests and reversals, in its words:

1. **The bound on the receiver rule's work:** 100 names followed along one chain and 1,000 states per lock, a model's name counting toward neither; beyond either, the lock refused with the limit, the function and the line named; module constants; the docstring states them. Its tests and reversal (the scan as at `8d83474`) as the brief gives them. No test asserts a time; record each time.
2. **The scan's docstrings:** F2's sentence in the review's words; BB9 after it; `scan()`'s docstring in BB10's words; the opening paragraph's Stage B sentence in the brief's words.
3. **`one_snapshot_statements`' docstring,** in the brief's words.
4. **The pinning tests** (F3: the memo key's `seen`; F12: `_climb`'s `NamedExpr` branch and a field path in a later keyword argument), each failing against its mutant.
5. **T3's date rule, narrowed** to the `Expires` header's own shape in the response headers' text alone, and `forms` gaining a date's HTTP and email shape; its offline tests and reversals as the brief gives them; the README's "Limits" drops that gap. Watch the stop rule's clock clause.
6. **An offline test of `profile_cases._found_in_database`'s rules,** with a fake cursor, as the carried item says: a timestamp column's text not a hit; a held coordinate, place and date still hits; each label naming `table.column` without the value; and a reversal against the old matcher.
7. **The proof's N5 items:** the test classes after `unittest.main()` moved before it; the query plans' unused `batch` parameter removed.
8. **The stated limit:** a 1,000-part combination's `RecursionError` in `_parts` (the scan exits 1); 300 parts do not; in the README's "Limits", with that planted example.
9. **The records:** the README's SV3 heading and a sentence on what B0 adds, in your words; its "Limits" for items 1, 5 and 8; the record's section; and B0's run of record in the P11 plan's SV3 entry, in your records commit after the run of record.

Run the scan over `services/api` and the reference design: its output must be byte-identical to `8d83474`'s (52 calls read, 0 locking a queryset that joins, 7 explicit account locks, every verdict and line the same).

**The local checks:**
- **the proof,** in `proofs/postgres-ordering`: its venv and hash-locked install (`requirements-dev.lock`), its offline tests under `env -i`, Ruff, `ruff format --check` and mypy; and the lock scan, `python -m glow_ordering_proof.account_lock_scan`, compared with `8d83474`'s output;
- **a local database run,** if Docker allows it under D4's conditions: the profile and discovery suites once each (T3's change reaches both), and the ordering and identity suites once each. All are iteration, not evidence.

**The run of record:**
- Commit and push your code. Wait for the Foundation run on your last code commit to finish (the push rule).
- Read it with your GitHub tools:
  - every job's conclusion, and the gate's line (`Application checks passed`);
  - the ordering, identity, profile and discovery suites' results, the profile and discovery phases' durations, and each suite's value and secret scans;
  - the lock scan case's line;
  - whether a retry fired, and that no secret appears in the job's log.

## 4. The record

Add a section "Stage B, B0" to `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md`, at its end:
- the start gate's results, the environment check (names only) and the toolchain versions;
- for each of the nine items: what changed, its tests, and each reversal or mutant with its failing output; the bound's times, measured, not asserted;
- the scan's output on the tree, compared with `8d83474`'s;
- every command you ran, with its result line, with local database runs listed as iteration, not evidence;
- the run of record: its ID, each job's result, the four suites' counts, the phases' durations, the scans' results, and whether a retry fired;
- every deviation from the brief, and what you could not run, and why.

Commit each logical step with a clear message ending in the session's attribution lines. Push your records commit only after the run of record has finished. Confirm that `git status` is clean, and that `git diff --name-only <START_SHA> HEAD` lists only your owned paths.

## 5. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch, your code head and records head;
- the start gate's and the environment check's results;
- for each of the nine items: what changed, its tests, and each reversal's or mutant's result;
- the scan's output on the tree against `8d83474`'s;
- each local check's result, and whether a local database run was used;
- the run of record: its ID, every job, the gate's line, the four suites' counts, the phases' durations and whether a retry fired;
- anything that met the stop rule, every deviation from the brief, and what you could not run.

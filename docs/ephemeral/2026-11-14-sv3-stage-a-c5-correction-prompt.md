# SV3 Stage A correction C5 prompt — the receiver rule's depth, the records and the pinning tests (C4's delta re-review; DM-69)

- **Owner:** App Manager 11. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 14 November 2026.**
- **Durable brief:** [SV3 — The eligibility, discovery and interactions slice](../planning/sv3-eligibility-discovery-interactions.md), revision 11, "Stage A, correction C5 (C4's delta re-review; DM-69)", with C5's owned paths as DM-69's AA1 and AA2 wrote them.
- **Where the result goes:**
  - the session's changes in C5's owned paths, and its record, a new section "Stage A, correction C5" in `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md`, on its own branch;
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.05 (confidence 0.85); rung probabilities low 0.00, medium 0.09, high 0.78, extra high 0.13, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.01, Opus 5.5 0.99, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.99). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.001, Fable 5.1 at high 0.008, Fable 5.1 at extra high 0.001, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.089, Opus 5.5 at high 0.772, Opus 5.5 at extra high 0.129, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-14T08:41:10Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The brief's revision 11 applies DM-69's AA1 to AA3 as written, and DM-69 says they need no further read before this prompt (DM-69 section 2). This prompt authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Then, in order:
  - the manager's verification;
  - PR45's run and Codex's review on C5's head;
  - C5's bounded delta re-review against `ce260fc` (the brief's "C5's review");
  - Dev Manager 5's pre-merge read.
- **Deletion condition:** prune after SV3 Stage A's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch (AM11-21).

---

You are **correction C5 of SV3's Stage A**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **Stage A** built eligibility and discovery in `services/api/glow_discovery`, sealed until P11. Correction C1 made every explicit lock of an `AppAccount` row `FOR NO KEY UPDATE`. C2 to C4 built and tightened two proof checks: a static scan of those locks (`account_lock_scan.py`) and `pages.one_snapshot_statements`.
- **DM-68 ended the scan's line.** After C4, the scan is a static check of the forms it names; its rules are frozen; a further unseen form is a stated limit; a real account lock stays blocking. Every later review of SV3 has five correction classes and only those (the brief's "C4's review, and how the scan's line ends"). D14's check of the row locks the suites send comes in Stage B.
- **C4** (code head `ce260fc`; run of record 43493104710, every job passing) built DM-68's items.
- **C4's bounded delta re-review** asked for changes, narrowly (the evidence record, "Delta re-review of C4"). No blocking finding, no regression, and every test and reversal C4's brief names fails where it should. But:
  - **F1 (class 2):** an account combination, conditional, boolean or `:=` held in a name is judged as the lock's receiver only when the receiver's own name holds it. One more plain assignment hides it: `c = A | B; d = c; d.select_for_update(no_key=d is AppAccount)` passes as `generic FOR NO KEY UPDATE`, though the rows are locked `FOR UPDATE`. Codex found the same, on PR45 (`e297430`).
  - **F2, F3 (class 5):** two record sentences claim more than the scan does.
  - **N1 to N3, L1 to L7 and an observation:** record fixes, stated limits, and tests that pin C4's branches.
  - `SELECT truncate_x()` is a stated limit, SC9's.
- **Dev Manager 5 ruled** (DM-69, in `docs/continuity/dev-manager/reviews/`). It approved each disposition: F1 is class 2, fixed by making the receiver rule follow plain assignments transitively, as the join rule already does. Its prototype refused the review's five forms and two more, and changed nothing on the tree. It widened F3 to C2's README sentence.
- **The brief's revision 11 lists your six items** in "Stage A, correction C5". **It is your specification;** where this prompt summarizes it, the brief wins. **Your given words are DM-69's AA4 to AA13** (section 8 of its report).

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 11. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only C5's owned paths, as the brief's "Owned paths" gives them (AA2):
    - `proofs/postgres-ordering/glow_ordering_proof/account_lock_scan.py`;
    - its offline tests in `proofs/postgres-ordering/tests/`;
    - the proof README;
    - the evidence record;
    - the P11 plan's SV3 entry, its runs of record only;
  - **`discovery_cases.py` is not yours.** N3's write-check items are tests only;
  - change the scan's rules only for item 1 (DM-68's freeze);
  - use DM-69's AA4 to AA13 as given words where the brief points to them, each old passage found once and applied in order. Fill in AA13's `RUN` and `HEAD` with your run of record and code head;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule** (the brief's "The stop rule (C5)"). Stop and report, with no further change, if C5 needs any of these:
  - a change outside its owned paths;
  - any change to app code, a predicate, the selection, the recheck, a lock, a writer, the workflow or `discovery_cases.py`.

  Stop and report too:
  - if the corrected scan refuses an existing lock in `services/api` or the reference design, or changes any verdict on the tree;
  - in either case, report it; do not narrow item 1's words to pass it;
  - if a control of the ordering suite no longer fails as designed;
  - if any of these fails on the corrected code: the ordering suite on either subject, or the identity, profile or discovery suite.

  A reversal's or a mutant's temporary edit of code is allowed, and must be undone.
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
git diff --quiet ce260fc HEAD -- .github scripts services apps packages proofs ':!*.md' && echo "C4's code head"   # must print the line
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- proofs/postgres-ordering docs/testing/p11-deferred-acceptance.md 'docs/testing/evidence/*sv3*'   # must print nothing
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md | grep -c -E '^#+ Stage A, correction C5'   # must print 0
```

If a check fails, stop and report. The prompt is stale if:
- `<START_SHA>` is not on the live manager branch;
- the live branch has changed an owned path since it;
- or the record already holds "Stage A, correction C5".

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`; `proofs/postgres-ordering/README.md`;
- the brief, revision 11: D2, D14, the owned paths, "Stage A, correction C4" (with "C4's review, and how the scan's line ends") and "Stage A, correction C5";
- DM-69's report, whole, above all sections 3 and 8;
- the evidence record's "Stage A, correction C4", "Manager verification of C4" and "Delta re-review of C4" (its N3 row lists the mutants item 5 pins);
- `account_lock_scan.py` and `tests/test_discovery_offline.py`, whole;
- read only: the two generic helpers (`glow_chat/contact.py`'s `_lock`, the reference design's `_lock`) and `discovery_cases.py`'s `is_write`, `READ_START` and `WRITE_WORDS` (for item 5's write-check tests).

## 3. What to do

Make the brief's six items, each with its tests and reversals, in its words:

1. **A lock's receiver name, followed through every plain assignment** (F1; class 2). The brief's item 1 gives the rule, its offline tests (two hops through `d = c`, `d = c.filter(pk=a)` and `d = c[:5]` after an account combination; `d = rows.all()` after `rows |= ...`; three hops; two hops from an account conditional and from a `:=` expression; each refused as `orm`, `FOR UPDATE`; and `d = c` with `no_key=True` passing) and its reversal (the scan as at `ce260fc`, which passes each as `generic`, `FOR NO KEY UPDATE`). A plain chain held in a name stays C1's generic lock, and its stated limit is unchanged. The docstring states the rule.
2. **What the records claim** (F2, F3): AA4, AA5 and AA6 in the README; AA10 and AA11 in the record.
3. **The further-forms entry** (N1, N2): AA7 and AA8; a planted example, in your words, for each form in it that has none, each run against your scan and passing there; your section in the record lists every stated limit the README holds; AA12.
4. **More stated limits** (L1 to L7, and the observation): in the README's "Limits" and the record, in the review's words (the record, "Delta re-review of C4"), each with a planted example that passes at your head; and the write check's own reach, as the brief's item 4 words it.
5. **Tests that pin C4's branches** (N3): an offline test for each mutant the review lists for items 1 to 4 and 6 of C4's section (the record's N3 row), each failing against its mutant. Record each mutant and its failing line. No rule changes.
6. **The records:** AA9 (the README's SV3 heading); a sentence in the README's SV3 paragraph on what C5 adds, in your words; AA13 in the P11 plan, in your records commit after the run of record; and the record's section.

Run the scan over `services/api` and the reference design, and report its counts and every lock's verdict: the counts must stay 52 calls read, none locking a queryset that joins, and the seven explicit account locks, and no verdict may change from `ce260fc`'s.

**The local checks:**
- **the proof,** in `proofs/postgres-ordering`: its venv and hash-locked install (`requirements-dev.lock`), its offline tests under `env -i`, Ruff, `ruff format --check` and mypy; and the lock scan, `python -m glow_ordering_proof.account_lock_scan`, with its counts;
- **a local database run,** if Docker allows it under D4's conditions: the discovery, ordering, identity and profile suites once each. All are iteration, not evidence.

**The run of record:**
- Commit and push your code. Wait for the Foundation run on your last code commit to finish (the push rule).
- Read it with your GitHub tools:
  - every job's conclusion, and the gate's line (`Application checks passed`);
  - the ordering, identity, profile and discovery suites' results, and the profile and discovery phases' durations;
  - the lock scan case's line and `pages.one_snapshot_statements`' line;
  - whether a retry fired, and that no secret appears in the job's log.

## 4. The record

Add a section "Stage A, correction C5" to `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md`, at its end:
- the start gate's results, the environment check (names only) and the toolchain versions;
- for each of the six items: what changed, its tests, and each reversal or mutant with its failing output;
- what the corrected scan finds over `services/api` and the reference design, with each lock's verdict against `ce260fc`'s;
- every stated limit the README holds, each with its planted example and the head it passes at;
- every command you ran, with its result line, with local database runs listed as iteration, not evidence;
- the run of record: its ID, each job's result, the four suites' counts, the phases' durations, and whether a retry fired;
- every deviation from the brief, and what you could not run, and why.

Commit each logical step with a clear message ending in the session's attribution lines. Push your records commit only after the run of record has finished. Confirm that `git status` is clean, and that `git diff --name-only <START_SHA> HEAD` lists only your owned paths.

## 5. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch, your code head and records head;
- the start gate's and the environment check's results;
- for each of the six items: what changed, its tests, and each reversal's or mutant's result;
- the corrected scan's findings and verdicts on the tree;
- each local check's result, and whether a local database run was used;
- the run of record: its ID, every job, the gate's line, the four suites' counts, the phases' durations and whether a retry fired;
- anything that met the stop rule, every deviation from the brief, and what you could not run.

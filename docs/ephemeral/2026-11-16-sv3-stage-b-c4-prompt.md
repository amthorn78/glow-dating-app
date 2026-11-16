# SV3 Stage B, correction B-C4 prompt — B-C3's delta re-review: placeholders as psycopg reads them, placeholders in spans, views and unmodelled relations, two bindings, the records; then D14 frozen

- **Owner:** App Manager 11. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 16 November 2026.**
- **Durable brief:** [SV3 — The eligibility, discovery and interactions slice](../planning/sv3-eligibility-discovery-interactions.md), revision 19, with its section "Stage B, correction B-C4 (B-C3's delta re-review; DM-78)".
- **Where the result goes:**
  - the session's changes in B-C4's owned paths, and its record, a new section `## Stage B, correction B-C4` at the end of `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md`, on its own branch;
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification to the record, and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.13 (confidence 0.80); rung probabilities low 0.00, medium 0.09, high 0.70, extra high 0.21, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.01, Opus 5.5 0.98, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.97). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.001, Fable 5.1 at high 0.007, Fable 5.1 at extra high 0.002, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.088, Opus 5.5 at high 0.686, Opus 5.5 at extra high 0.206, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.001, Sonnet 5.5 at high 0.007, Sonnet 5.5 at extra high 0.002, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-16T16:25:22Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs.
  - The brief's revision 19 applies DM-78's JJ12 to JJ15 as written. DM-78 sets this prompt's place in the sequence (its section 12) and needs no further read if its words are applied as written.
  - This prompt authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Then, in order:
  - the manager's verification, and PR47's run and Codex's review of its head;
  - a bounded delta re-review of B-C4 against `edc883e`, the last of D14 under all five classes (DM-78 section 10);
  - Dev Manager 5's pre-merge read;
  - the merge.
- **Deletion condition:** prune after Stage B's PR (PR47) merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch (AM11-21).

---

You are the **implementation session for SV3 Stage B's correction B-C4**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What B-C4 is.** The correction pass for the bounded delta re-review of correction B-C3's code head `edc883e`. The review asked for changes, with no blocking finding. DM-78 ruled on each finding:
- **F1:** D14 reads a placeholder as psycopg 3.3.6 reads one, a name holding `(` included (item 1).
- **F5:** a statement with a placeholder any part of which lies inside a string constant, a quoted identifier or a comment fails, whatever it holds (item 2).
- **F4, with Codex's (c):** a statement that creates a view fails whatever its lock; with the models' tables given, a statement that takes `FOR UPDATE` and does not name the account table fails unless every relation name it reads is one of those tables (item 3).
- **F2 and F3:** a `MERGE INTO` target's alias written without `AS`, and a join's `USING (…) AS` alias, are read as bindings, none of them plain; `excluded` is stated (item 4).
- **The nits** (item 5) and **the records** (item 6).

**After B-C4, D14's rules are frozen** (DM-78 section 10; the brief's "B-C4's review, and how D14's line ends"): B-C4's review is the last under all five classes, and later changes to the rules come only for a class 1 defect, a regression, or a design the Dev Manager reads.

Codex's thread on `4c2f918` (F4 again) is answered by item 3, and S2's thread (r4581883081) by item 1.

B-C4 changes no model, migration, lock, version check, existing DTO, stale body, `glow_chat` writer, ledger, lock-scan rule or bound, contract package, workflow or dependency, and no line in `services/api`. There is no provider, deployed URL, real member, HDE call or stored credential.

**The brief, `docs/planning/sv3-eligibility-discovery-interactions.md`, revision 19, is the specification:**
- its section "Stage B, correction B-C4", items 1 to 7, its stop rule, its run of record and "B-C4's review, and how D14's line ends";
- D14's rule (JJ12, JJ13);
- B-C4's owned paths, "Correction B-C4 only" (JJ15).

Its text is Dev Manager 5's words (DM-78), checked against the code. Follow them exactly. Where this prompt summarizes the brief, the brief wins.

**DM-78's given words that B-C4 applies.** DM-78's report (`docs/continuity/dev-manager/reviews/2026-11-16-dm-78-sv3-b-c3-delta-review-dispositions.md`) gives the exact old and new texts as pairs of quoted blocks in its section 14:
- **B-C4's eleven:** JJ1 to JJ9 (the proof README), JJ10 (`row_locks.py`'s docstring, "What it does not see") and JJ11 (the record's account of B-C3's placeholder rule) (its section 15, "Who applies what").
- **Apply each as written.** Its old passage must be found exactly once before the change, and its new text exactly once after. The manager checked each old passage once at `<START_SHA>`.
- **Stop if a pair cannot be applied.** If an old passage is not found exactly once, report it; do not reword it.
- **Leave the manager's pairs alone.** JJ12 to JJ15 (the brief) are already applied.
- **The docstring's reading, rule and resolution paragraphs and its fast-path sentence** follow the README in your own words (DM-78 section 15).

**What came before.**
- **SV3's Stage A** (PR45, `8d83474`) and **B0** (PR46, `947576d`) are merged.
- **Stage B**, **B-C1**, **B-C2** and **B-C3** are built, verified and integrated in PR47: code head `edc883e`. B-C3's run of record, 43809849211, passed all eight jobs: discovery 66/66, each suite's D14 record `PASS`, none refused, own objects 0, 0, 0; account-table writer locks 44,841 (ordering), 127 (identity), 2,061 (profile) and 4,256 (discovery), all `FOR NO KEY UPDATE`.
- **B-C3's bounded delta re-review:** changes required; no blocking finding, no class 1, 3 or 4 finding (the evidence record, "Delta re-review of B-C3", with its findings, proposed limits and planted examples).
- **DM-78** ruled on each finding and froze D14's rules from B-C4's head. The brief is now at revision 19.

**Facts from the code** (at `edc883e`; the manager's reading at `<START_SHA>`, whose non-Markdown tree equals it):
- **D14's rule** (`proofs/postgres-ordering/glow_ordering_proof/row_locks.py`):
  - `_PLACEHOLDER` (line 170) is `%%|%(?:\([^()]*\))?[sbt]`; psycopg 3.3.6's `_re_placeholder` reads a name as one or more characters other than `)`, then any one character, and `_split_query` accepts only `s`, `b` and `t` there (F1);
  - `_NAME_CHARACTER` (line 171); `_glued_placeholder` (line 492); `_creates_routine` (line 509);
  - `judge` (line 523): after the `DO` and creation rules it returns with no refusal when the statement takes no `FOR UPDATE`, then fails a `U&` identifier, then returns with no refusal when the statement does not name the account table (line 569, Codex's line), before `_resolve` (line 592) is called;
  - `_resolve`'s join `USING (…)` handling (lines 741-746), its `MERGE INTO` target (line 779) and its final not-plain pass for `USING`-list items (line 794);
  - the docstring's "What it does not see" (line 99 and after; N3, JJ10);
  - `RowLockRecord._model_tables` (line 973) gives `judge` the models' tables once Django's registry is ready (`model_tables()`, line 1151: every installed model's table, many-to-many tables included); before that, an empty set.
- **What the suites send** (the manager's sweep, AM11-23, and DM-78 section 2):
  - every `FOR UPDATE` a suite sends is Django's `select_for_update()` on a model (`reference.py`, `planted.py`, `profile_cases.py` and the API's `glow_*` apps); no raw SQL text in non-test code takes `FOR UPDATE`;
  - no non-test code creates a view, sends SQL `PREPARE` or `RunSQL`, or places a placeholder inside a span; DM-78's sweep of 925 SQL-like constants found none (f-strings and joined texts not swept);
  - the run of record shows whether items 2 and 3 refuse any statement a suite sends (the stop rule).
- **The existing row-lock offline tests** (`tests/test_row_locks_offline.py`):
  - `test_the_fast_path_and_the_full_reading_agree` (line 310) and the creation tests (`FunctionBodyTests`, line 522; `ROUTINE_BODIES`, line 454) gain statements for item 3's `VIEW`;
  - `test_a_placeholder_apart_from_names_a_literal_percent_or_no_update_passes` (line 626) holds `'a%%sb'`, a `%%` inside a string constant, which item 2 passes;
  - `GLUED` (line 508) and its test (line 617) assert `GLUED_PLACEHOLDER` as the reason; none of their placeholders lies inside a span;
  - DM-78's prototype of its rules judged 199 statically evaluable texts of this module with and without the models' tables and changed none of their verdicts.
- **The case count stays 66.** Item 3's database reversal is local and informational; its other tests are offline. B-C4 adds no case.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 11. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - **write only B-C4's owned paths** (the brief's "Owned paths (the sessions)", "Correction B-C4 only", JJ15):
    - in the proof: `row_locks.py` (its placeholder reading, the span and view-creation rules, the fast path's creation test, the relations check, the bindings F2 and F3 name, and its docstring) and its offline tests, new files included;
    - the proof README's D14 entry, SV3 paragraph and "Limits";
    - the P11 plan's SV3 entry, its runs of record only;
    - the evidence record.

    Nothing else changes in B-C4.
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule** (the brief's "The stop rule (B-C4)"). Stop and report, with no further change, if any of these holds:
  - B-C4 needs a change outside its owned paths;
  - it needs a change to any of these: a model, a migration, a lock, a version check, an existing DTO, D8's single stale body, a `glow_chat` writer, the ledger, the lock scan's rules or B0's bound, the contract package, the workflow, a dependency, or any line in `services/api`;
  - a statement any suite sends fails D14's corrected rule;
  - one of DM-78's eleven pairs cannot be applied as written;
  - a case other than those item 7 names changes its verdict;
  - **an earlier test** (DD5; the section's item 7): expected to change, each keeping what it protects:
    - **`test_the_fast_path_and_the_full_reading_agree`** and the creation tests (`FunctionBodyTests`, `ROUTINE_BODIES`): only added to, for item 3's `VIEW` (the fast path's creation test reads `VIEW` as it reads `FUNCTION` and `PROCEDURE`);
    - **`test_row_locks_offline.py`:** otherwise only added to. Every existing test keeps its statements and verdicts, among them `'a%%sb'` (line 626), and `GLUED`'s reason.

    By the manager's reading at `<START_SHA>` and DM-78's prototype, no test pins `_PLACEHOLDER`'s text, and no other earlier test is expected to change. If any other earlier test fails, report which and why; do not change or delete it.
  - In each case, report it; do not narrow the brief's words to pass it. A reversal's temporary edit of code is allowed, and must be undone.
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished; a newer push cancels the earlier run's application jobs. Push your records commit only after the run of record has finished. The workflow runs on pushes to `claude/**` and `ccr-**`; if your branch is named otherwise, say so in the report.
  - **If GitHub never starts the run** (it stays `queued` with no jobs for 30 minutes), do not re-run it, dispatch it, push an empty commit, or ask anyone to re-run it (OD-58). Record it, push your records commit, and report.
  - **If the run fails,** stop and report the failing job and its log lines. Do not re-run it, and push no fix without saying so in the report.
- **Network:**
  - PyPI and the npm registry, for `pip install --require-hashes` and `npm ci --ignore-scripts` from the existing locks only;
  - Docker Hub, only to pull the PostgreSQL image the CI job pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`) for a local run.

  A page you cannot reach is named as unread, never filled from memory.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions):
  - **start the Docker daemon under `env -i`, with only `PATH`, `HOME` and the proxy's names** (DM-78 section 9);
  - a throwaway PostgreSQL in Docker, from the CI job's pinned image, on loopback only;
  - a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present;
  - removed afterwards, with its volumes, and the daemon stopped.

  Local passes are "iteration, not evidence"; the run of record is CI's.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, password, code, token, session key or signing key, in any form;
  - read, print or use the value of any `AWS_*` variable, or name one in a command (section 1);
  - make test data that looks real: accounts, emails, names, birth facts, places and coordinates are synthetic and obviously so (`@example.invalid` addresses);
  - call any provider or HDE, send any email, or run any command in `proofs/stream-chat/`;
  - connect to any database but a throwaway one you started under D4's conditions;
  - run `migrate` or `makemigrations` other than through the proof's own commands against such a database, or under the static registry's dummy settings;
  - connect to HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script;
  - weaken or delete a test to make the suite pass.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:** `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` or `PG*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG)'` prints names only. If any is present, stop and report.
3. **Three AWS names are expected:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_CA_BUNDLE`. `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values, and pass none to a command, the Docker daemon included.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
5. **The toolchain:** CPython 3.12.14 as `python3.12`; Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, first on PATH. Record `python3.12 --version`, `node --version`, `npm --version` and `docker --version`.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git merge-base --is-ancestor <START_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"   # must print the line
git diff --quiet edc883ed937c50d1a52cd82b1fa7c3d1e1482847 HEAD -- . ':!*.md' && echo "B-C3's code"   # must print the line: the start's non-Markdown tree equals edc883e's
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/api proofs/postgres-ordering 'docs/testing/evidence/*sv3*' docs/testing/p11-deferred-acceptance.md   # must print nothing
grep -c -F 'Status: brief, revision 19,' docs/planning/sv3-eligibility-discovery-interactions.md   # must print 1
grep -c -E '^## Stage B, correction B-C4' docs/planning/sv3-eligibility-discovery-interactions.md   # must print 1
grep -c -E '^## Stage B, correction B-C4' docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md   # must print 0
test -f docs/continuity/dev-manager/reviews/2026-11-16-dm-78-sv3-b-c3-delta-review-dispositions.md && echo "DM-78's report"   # must print the line
```

If a check fails, stop and report. The prompt is stale if:
- `<START_SHA>` is not on the live manager branch;
- the live branch has changed an owned path since it;
- or the record already holds "Stage B, correction B-C4".

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md` and `proofs/postgres-ordering/README.md` (above all D14's entry, the SV3 paragraph and "Limits");
- the brief, revision 19: D14, "Stage B, correction B-C3" and "Stage B, correction B-C4" with "B-C4's review, and how D14's line ends", whole;
- DM-78's report, whole: its rulings (sections 4 to 12) and its pairs (section 14);
- the evidence record: "Stage B, correction B-C3", "Manager verification of B-C3" and "Delta re-review of B-C3", whole;
- the code, whole: the proof's `row_locks.py` and `tests/test_row_locks_offline.py`; psycopg 3.3.6's `_queries.py` (`_re_placeholder`, `_split_query`) from the hash-locked install;
- the texts DM-78's pairs change: the proof README, `row_locks.py`'s docstring, the record's account of B-C3's placeholder rule, and the P11 plan's SV3 entry.

## 3. What to do

Each test below comes with its reversal (D18): a temporary edit that must make the test fail, run, then undone, with the edit and the failing output recorded. "Fails at B-C4's head and passes at `edc883e`" means you run the test, or the planted text through `row_locks.refusal`, at both.

1. **Placeholders read as psycopg reads them** (item 1; F1). D14 reads a placeholder as psycopg 3.3.6 does: `%s`, `%b` or `%t`, or `%(name)s`, `%(name)b` or `%(name)t` with a name of one or more characters other than `)`; `%%` is a literal percent sign. Both placeholder tests use this reading.
   - **Cases:** F1's two texts (`SELECT id, $q%((n)s$ $q1$ FROM glow_persistence_appaccount FOR UPDATE --$q1$`, and the same with `%(a(b)s`) fail at B-C4's head and pass at `edc883e`; the `%(n)s` control is still refused.
   - **The record:** apply JJ11 to the record's account of B-C3's rule.
   - **Its reversal:** `edc883e`'s pattern restored fails F1's cases.
2. **A placeholder inside a span** (item 2; F5).
   - **The rule:** a statement with a placeholder any part of which lies inside a string constant (`'…'`, `E'…'`, `U&'…'` or dollar-quoted), a quoted identifier (`"…"` or `U&"…"`) or a comment (`--` or `/* … */`) fails whatever its lock or text. The test runs before the fast path, as the glued-placeholder test does.
   - **Cases,** each failing at B-C4's head and passing at `edc883e`: F5's text (`SELECT id FROM glow_persistence_appaccount WHERE state <> '%s' FOR NO KEY UPDATE`), the same without its lock clause, `"%s"`, a placeholder inside each other kind of span, and a name holding a quote (`%(a'b)s`).
   - **Passing:** a `%%` inside a string constant, and a placeholder glued to a closing quote outside the constant (`'a'%s`).
   - **The texts:** S4 in JJ8's words.
   - **Its reversal:** the span rule disabled fails the failing cases.
3. **A view's creation, and a lock through a name outside the models** (item 3; F4; Codex on `4c2f918`).
   - **The creation rule:** a statement that creates a view (`CREATE [OR REPLACE] [TEMP | TEMPORARY] [RECURSIVE] VIEW` or `CREATE MATERIALIZED VIEW`, the words read as PostgreSQL reads them) fails whatever its lock, and the fast path's creation test reads `VIEW` as it reads `FUNCTION` and `PROCEDURE`.
   - **The relations check:** with the models' tables given, a statement that takes `FOR UPDATE` and does not name the account table fails unless every relation name it reads, in any scope (each `FROM`, `JOIN`, `USING`-list, `INTO`, `UPDATE` and `DELETE FROM` item, a `WITH` query's name read as one included), is one of those tables, written without a schema; a `TABLE` command, or parentheses it cannot read, fail it too. Without the models' tables (before Django's registry is ready), the check does not apply, as JJ6 states.
   - **`PREPARE`** needs no rule of its own: its body is judged as any statement is.
   - **Tests, offline:**
     - a record given the models' tables and fed `CREATE TEMP VIEW v AS SELECT id FROM glow_persistence_appaccount`, `SELECT id FROM v FOR UPDATE` and `DROP VIEW v`, in that order, refuses the first two and passes the third;
     - F4's `public` view with `FOR UPDATE OF v2`, and `PREPARE p AS SELECT id FROM v FOR UPDATE`, are refused;
     - a `FOR UPDATE` with no `OF` list on models' tables, as Django's `select_for_update()` sends it, passes;
     - each fails at B-C4's head where it should and passes at `edc883e`.
   - **A planted database reversal,** local under D4's conditions (the Docker daemon under `env -i`) and informational: F4's three statements in a case's session show the record failing at the view's creation and at the lock, with the own-objects counts 0, 0, 0 after the drop. Record its commands and output. If Docker is unavailable, say so.
   - **The stated limits' examples** (a lock through a model table's name after a temporary view of that name, whose creation fails; a renamed table) are planted in the record.
   - **The texts:** JJ1, JJ3 to JJ6 and JJ10.
   - **Its reversals:** the view-creation rule disabled; the relations check disabled; each fails its tests.
4. **Two bindings** (item 4; F2, F3). A `MERGE INTO` target's alias written without `AS`, and a join's `USING (…) AS` alias, are read as bindings, none of them plain.
   - **Cases:** the review's two texts fail at B-C4's head and pass at `edc883e`; a `JOIN … USING (id)` statement with no alias keeps its verdict.
   - **`excluded`** is stated, not read (JJ9).
   - **Its reversal:** each binding left unread fails its case.
5. **The nits** (item 5).
   - **N1:** a test text whose placeholder's only glued neighbour is `$` (`SELECT id, $%s$ $NULL$ FROM glow_persistence_appaccount FOR UPDATE --$NULL$`), failing with `$` removed from the name characters.
   - **N2:** a test that pins a `JOIN` item inside a `USING` list as not plain, failing with the final pass removed.
   - **N3:** the docstring's "What it does not see" in JJ10's words.
6. **The records** (item 6).
   - The README's D14 entry, SV3 paragraph and "Limits" in JJ1 to JJ9's words.
   - `row_locks.py`'s docstring says what the README says, in its reading, rule and resolution paragraphs and its fast-path sentence, in your words, and its "What it does not see" in JJ10's.
   - The record gains B-C4's section, and JJ11's note on B-C3's rule.
   - The P11 plan's SV3 entry gains B-C4's run of record.
7. **The local checks:**
   - **API,** in `services/api`, unchanged by B-C4: set up `python3.12 -m venv .venv` and `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`; then, with `GLOW_ENV=test`, `manage.py check`, `manage.py test tests --verbosity 2`, `ruff check .`, `ruff format --check .` and `mypy`;
   - **the proof,** in `proofs/postgres-ordering`: its venv and hash-locked install; its offline tests under `env -i`, Ruff, `ruff format --check` and mypy; the lock scan, `python -m glow_ordering_proof.account_lock_scan`, its output unchanged (52 calls, 0 joining, 7 account locks);
   - **a local database run,** if Docker allows it under D4's conditions: iteration, not evidence. Run the discovery suite at least, and item 3's database reversal.
8. **The run of record.** Commit and push your code. Wait for the Foundation run on your last code commit to finish (the push rule), then read it with your GitHub tools:
   - every job's conclusion, and the gate's line (`Application checks passed`);
   - each suite's result, D14's line (`ROW LOCKS (D14): PASS`, none refused) and its own-objects counts (0, 0, 0);
   - the account-table writer-lock counts in each suite, against B-C3's run of record (44,841; 127; 2,061; 4,256);
   - the discovery suite: 66/66, and its phase duration against the job's 30-minute timeout (the span test lexes more statements);
   - whether a toolchain retry fired.

## 4. The record

Add a section `## Stage B, correction B-C4` at the end of `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md`, with:
- the start gate's results, the environment check (names only) and the toolchain versions;
- **DM-78's eleven pairs:** each applied, with its target file, its old passage found once before and its new text once after;
- **D14:** the placeholder reading, the span rule, the view-creation rule, the relations check and the bindings, described; a table of every text items 1 to 5 plant, with its verdict at `edc883e` and at B-C4's head;
- **the tests:** a table with one row per test, giving the file, the test, the reversal and its failing output;
- **the earlier tests:** each named test's statements before and after, and why;
- **commands:** every command you ran, with its result line. List local database runs, item 3's reversal among them, as iteration, not evidence;
- **the run of record:** its ID, each job's result, D14's line, own-objects counts and account-table lock counts in each suite, the discovery phase's duration, and whether a retry fired;
- **B-C4's lines in `services/api`:** their count (expected zero);
- **the freeze:** one line that D14's rules are frozen from this head (the brief's "B-C4's review, and how D14's line ends");
- every deviation from the brief, and what you could not run, and why.

Commit each logical step with a clear message ending in the session's attribution lines. Push your records commit only after the run of record has finished. Confirm that `git status` is clean, and that `git diff --name-only <START_SHA> HEAD` lists only B-C4's owned paths.

## 5. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch, your code head and records head;
- the start gate's and the environment check's results;
- DM-78's eleven pairs, each applied or not;
- each rule's change, and each test with its reversal's result;
- the planted texts' verdicts before and after, and item 3's database reversal;
- the earlier tests, each before and after;
- each local check's result, and whether a local database run was used (and that the Docker daemon ran under `env -i`);
- the run of record: its ID, every job, the gate's line, D14's line, own-objects counts and account-table lock counts in each suite, the discovery phase's duration and whether a retry fired;
- B-C4's lines in `services/api`;
- anything that met the stop rule, every deviation from the brief, and what you could not run.

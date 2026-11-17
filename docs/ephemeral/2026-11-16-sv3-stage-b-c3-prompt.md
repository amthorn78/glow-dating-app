# SV3 Stage B, correction B-C3 prompt — B-C2's delta re-review: function bodies, glued placeholders, unread bindings, temporary schemas, the ledger's order, the limits and records

- **Owner:** App Manager 11. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 16 November 2026.**
- **Durable brief:** [SV3 — The eligibility, discovery and interactions slice](../planning/sv3-eligibility-discovery-interactions.md), revision 18, with its section "Stage B, correction B-C3 (B-C2's delta re-review; DM-77)".
- **Where the result goes:**
  - the session's changes in B-C3's owned paths, and its record, a new section `## Stage B, correction B-C3` at the end of `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md`, on its own branch;
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification to the record, and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 1.86 (confidence 0.84); rung probabilities low 0.00, medium 0.19, high 0.76, extra high 0.05, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.99, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.99). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.188, Opus 5.5 at high 0.752, Opus 5.5 at extra high 0.050, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.002, Sonnet 5.5 at high 0.008, Sonnet 5.5 at extra high 0.001, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-16T04:31:25Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs.
  - The brief's revision 18 applies DM-77's II12 to II16 as written, and the record holds II10. DM-77 sets this prompt's place in the sequence (its section 14) and needs no further read if its words are applied as written.
  - This prompt authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Then, in order:
  - the manager's verification, and PR47's run and Codex's review of its head;
  - a bounded delta re-review of B-C3 against `4860b56` (DM-77 section 13);
  - Dev Manager 5's pre-merge read;
  - the merge.
- **Deletion condition:** prune after Stage B's PR (PR47) merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch (AM11-21).

---

You are the **implementation session for SV3 Stage B's correction B-C3**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What B-C3 is.** The correction pass for the bounded delta re-review of correction B-C2's code head `4860b56`. The review asked for changes, narrowly, with no blocking finding. DM-77 ruled on each finding:
- **F1, the `U&` sentence:** the words follow the code; a `U&` statement fails only with `FOR UPDATE` (item 1).
- **F2, the `OF` list:** a name in a lock clause's `OF` list is read as a reference; the words say so (item 2).
- **S1 and F3:** a statement that creates a function or a procedure fails whatever its lock, as `DO` does; the own-objects check counts temporary schemas (item 3).
- **F4:** D14's reading is qualified: the text the record receives, before psycopg binds its parameters, with `standard_conforming_strings` on (item 4).
- **F5:** bindings inside a parenthesised join, or in a `DELETE` or `MERGE` statement's `USING` list, are read, none of them plain (item 5).
- **S2:** a statement whose text holds `UPDATE` and a placeholder glued to a name character or a dollar sign fails (item 6).
- **F6, Codex's fifth finding:** B-C1's ledger checks a command's version before recording its answer, against the versions served before the send (item 7).
- **The other limits and the nits:** stated, recorded, or tested (items 8 and 9).

Codex's two P2 findings on `892bd59` are S2 and F3 again; items 6 and 3 answer them.

B-C3 changes no model, migration, lock, version check, existing DTO, stale body, `glow_chat` writer, lock-scan rule or bound, contract package, workflow or dependency, and no non-test line in `services/api`. There is no provider, deployed URL, real member, HDE call or stored credential.

**The brief, `docs/planning/sv3-eligibility-discovery-interactions.md`, revision 18, is the specification:**
- its section "Stage B, correction B-C3", items 1 to 10, its stop rule, its run of record and its review;
- D14's rule (II12), and the notes on B-C2's items 4 and 5 (II13, II14);
- B-C3's owned paths, "Correction B-C3 only" (II16).

Its text is Dev Manager 5's words (DM-77), checked against the code. Follow them exactly. Where this prompt summarizes the brief, the brief wins.

**DM-77's given words that B-C3 applies.** DM-77's report (`docs/continuity/dev-manager/reviews/2026-11-16-dm-77-sv3-b-c2-delta-review-dispositions.md`) gives the exact old and new texts as pairs of quoted blocks in its section 16:
- **B-C3's ten:** II1 to II6, II9 and II11 (the proof README, the record's own-objects row, `row_locks.py`'s docstring), and II7 and II8 (the P11 plan) (its section 17, "Who applies what").
- **Apply each as written.** Its old passage must be found exactly once before the change, and its new text exactly once after. The manager checked each old passage once at `<START_SHA>`.
- **Stop if a pair cannot be applied.** If an old passage is not found exactly once, report it; do not reword it.
- **Leave the manager's pairs alone.** II10 (the record's "Manager verification of B-C2") and II12 to II16 (the brief) are already applied.

**What came before.**
- **SV3's Stage A** (PR45, `8d83474`) and **B0** (PR46, `947576d`) are merged.
- **Stage B** (code head `5d58993`), **B-C1** (`470d97a`) and **B-C2** (`4860b56`; undo one step, D14 read as PostgreSQL reads) are built, verified and integrated in PR47. B-C2's run of record, 43780988590, passed all eight jobs: discovery 66/66, each suite's D14 record `PASS` with none refused.
- **B-C2's bounded delta re-review:** changes required, narrowly; no blocking finding, no class 1, no class 3 regression and no class 4 finding (the evidence record, "Delta re-review of B-C2", with its findings, stated limits, nits and planted examples).
- **DM-77** ruled on each finding. The brief is now at revision 18.

**Facts from the code** (at `4860b56`; the manager's reading at `<START_SHA>`, whose non-Markdown tree equals it):
- **D14's rule** (`proofs/postgres-ordering/glow_ordering_proof/row_locks.py`):
  - `judge` (line 453) takes a fast path when no span mark is present (`_SPAN_MARKS`, line 140: a quote, `$`, `--`, `/*`, `&`) and the double quotes are even; otherwise it reads the statement whole;
  - the `DO` and unterminated-span rules fail whatever the lock; the `U&` rule fails with `FOR UPDATE` only (lines 479-482, reason `U_AND_NAME`, line 148);
  - `_resolve`'s item reader and scan loop (lines 540-700): an item inside a parenthesised join is never read as a binding (lines 557-558), and the loop (609-653) reads no `USING` item;
  - `OWN_OBJECTS` (lines 280-296): three counts (functions and procedures, views and materialized views, rules), each excluding `information_schema` and every schema matching `pg\_%`. It runs in `RowLockRecord.check` (line 989), before each suite's verdict, on the suite's connection, and in the case `row_locks.driver_forms_are_seen` (`interaction_cases.py`, line 377), which expects `(0, 0, 0)`.
- **What the suites send** (the manager's sweep, AM11-23):
  - no `CREATE FUNCTION`, `CREATE PROCEDURE`, view, rule, `RunSQL`, `DO`, `U&` or dollar-quote appears in non-test code in `services/api` or the proof;
  - no non-test code holds a placeholder glued to a name character; the only matches of the pattern are Django constraint-name templates in `glow_persistence/models.py` (`"%(app_label)s_%(class)s_state"`), which Django renders into names before any SQL is sent;
  - Django's own SQL is not in the source; the run of record shows whether item 6 refuses any of it (the stop rule).
- **psycopg is pinned at 3.3.6** (`requirements.lock`). Django's psycopg backend binds on the client: it writes each value into the text before sending it. `%%` is a literal percent sign, not a placeholder.
- **B-C1's ledger** (`interaction_cases.py`): `_Ledger` (line 1986), `served_from` (2002) and `check` (2020). In `_as_a_client`'s routes wrapper, `served_from` (line 2069) runs before `check` (2073); in its direct wrapper, line 2080 before 2081.
- **N5:** the block case's return line (`interaction_cases.py`, line 1106) ends "hidden".
- **The record's N1 splices:** at `<START_SHA>`, lines 1932 ("The resolution") and 2130 ("The other binding forms") each hold the planted-text table's header mid-sentence, where "`TABLESAMPLE`" was. The table's intended copy is the one after the script note in "D14: the reading and the resolution".
- **The proof README's SV3 paragraph** (line 19) names the brief's revision 17; II6 changes the same paragraph.
- **The case count stays 66.** S1's and F3's database reversal is local and informational (DM-77 section 6); F6's tests are offline. B-C3 adds no case.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 11. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - **write only B-C3's owned paths** (the brief's "Owned paths (the sessions)", "Correction B-C3 only", II16):
    - in the proof: `row_locks.py` (the creation rule, the placeholder rule, the bindings F5 names, `OWN_OBJECTS`'s schema filter and its docstring) and its offline tests; `interaction_cases.py` (the ledger's two wrappers and N5's detail line); and the proof's offline tests, new files included, for the ledger's test;
    - in `services/api/tests/`: `UndoSelectionTests` only (N8);
    - the proof README's D14 entry, SV3 paragraph and "Limits";
    - the P11 plan's B-C2 line, migration 0011's note and its runs of record;
    - the evidence record.

    Nothing else changes in B-C3.
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule** (the brief's "The stop rule (B-C3)"). Stop and report, with no further change, if any of these holds:
  - B-C3 needs a change outside its owned paths;
  - it needs a change to any of these: a model, a migration, a lock, a version check, an existing DTO, D8's single stale body, a `glow_chat` writer, the lock scan's rules or B0's bound, the contract package, the workflow, a dependency, or a non-test line in `services/api`;
  - a statement any suite sends fails D14's corrected rule;
  - one of DM-77's ten pairs cannot be applied as written;
  - a case other than those item 10 names changes its verdict;
  - **an earlier test** (DD5; the section's item 10): the earlier tests B-C3 is expected to change are named here, with their reasons. Any other earlier test that no longer passes is a stop. Expected to change, each keeping what it protects:
    - **`test_the_fast_path_and_the_full_reading_agree`** (`tests/test_row_locks_offline.py`, line 310; item 9, N7): it gains a `--` statement (for example `FOR -- c`, a newline, `UPDATE` on the account table). Reversal: `--` removed from `_SPAN_MARKS` fails it.
    - **`UndoSelectionTests`** (`services/api/tests/test_interactions_offline.py`, line 1298; item 9, N8): it also pins undo's `raise` after its `if`. Reversal: the `raise` removed fails it.
    - **`test_the_ledger_passes_only_a_served_version_or_a_refusal_first`** (`tests/test_discovery_offline.py`, line 605; item 7): it calls `_Ledger.served_from` and `_Ledger.check` directly. If item 7 changes `check`'s signature (to take the versions served before the send), its calls change to match, and every assertion keeps its verdict.
    - **`test_every_case_of_the_module_runs_under_the_ledger`** (line 594; item 7): it pins the wrapper's name, `_as_a_client.<locals>.wrapped`. Keep that name; if item 7 cannot, say why.
    - **`test_row_locks_offline.py`:** otherwise only added to. Every existing test keeps its statements and verdicts, among them the `LIKE 'pg\_%'` statement at line 297, which holds `UPDATE` and no placeholder.

    By the manager's reading at `<START_SHA>`, no test pins `OWN_OBJECTS`'s text, and no other earlier test is expected to change. If any other earlier test fails, report which and why; do not change or delete it.
  - In each case, report it; do not narrow the brief's words to pass it. A reversal's temporary edit of code is allowed, and must be undone.
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished; a newer push cancels the earlier run's application jobs. Push your records commit only after the run of record has finished. The workflow runs on pushes to `claude/**` and `ccr-**`; if your branch is named otherwise, say so in the report.
  - **If GitHub never starts the run** (it stays `queued` with no jobs for 30 minutes), do not re-run it, dispatch it, push an empty commit, or ask anyone to re-run it (OD-58). Record it, push your records commit, and report.
  - **If the run fails,** stop and report the failing job and its log lines. Do not re-run it, and push no fix without saying so in the report.
- **Network:**
  - PyPI and the npm registry, for `pip install --require-hashes` and `npm ci --ignore-scripts` from the existing locks only;
  - Docker Hub, only to pull the PostgreSQL image the CI job pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`) for a local run.

  A page you cannot reach is named as unread, never filled from memory.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions):
  - a throwaway PostgreSQL in Docker, from the CI job's pinned image, on loopback only;
  - a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present;
  - removed afterwards, with its volumes.

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
3. **Three AWS names are expected:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_CA_BUNDLE`. `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values, and pass none to a command.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
5. **The toolchain:** CPython 3.12.14 as `python3.12`; Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, first on PATH. Record `python3.12 --version`, `node --version`, `npm --version` and `docker --version`.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git merge-base --is-ancestor <START_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"   # must print the line
git diff --quiet 4860b56c222db719f28010845ae32d15ecbf124a HEAD -- . ':!*.md' && echo "B-C2's code"   # must print the line: the start's non-Markdown tree equals 4860b56's
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/api proofs/postgres-ordering 'docs/testing/evidence/*sv3*' docs/testing/p11-deferred-acceptance.md   # must print nothing
grep -c -F 'Status: brief, revision 18,' docs/planning/sv3-eligibility-discovery-interactions.md   # must print 1
grep -c -E '^## Stage B, correction B-C3' docs/planning/sv3-eligibility-discovery-interactions.md   # must print 1
grep -c -E '^## Stage B, correction B-C3' docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md   # must print 0
test -f docs/continuity/dev-manager/reviews/2026-11-16-dm-77-sv3-b-c2-delta-review-dispositions.md && echo "DM-77's report"   # must print the line
```

If a check fails, stop and report. The prompt is stale if:
- `<START_SHA>` is not on the live manager branch;
- the live branch has changed an owned path since it;
- or the record already holds "Stage B, correction B-C3".

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md` and `proofs/postgres-ordering/README.md` (above all D14's entry, the SV3 paragraph and "Limits");
- the brief, revision 18: D12, D14, "Stage B, correction B-C2" and "Stage B, correction B-C3", whole;
- DM-77's report, whole: its rulings (sections 4 to 13) and its pairs for B-C3 (section 16);
- the evidence record: "Stage B, correction B-C2", "Manager verification of B-C2" and "Delta re-review of B-C2", whole;
- the code, whole:
  - the proof's `row_locks.py` and `tests/test_row_locks_offline.py`;
  - `interaction_cases.py`: `_Ledger`, `_as_a_client`, the block case and `row_locks.driver_forms_are_seen`;
  - `tests/test_discovery_offline.py`'s ledger tests;
  - `services/api/glow_discovery/interactions.py`'s undo, and `services/api/tests/test_interactions_offline.py`'s `UndoSelectionTests`;
- the texts DM-77's pairs change: the proof README, the record's own-objects row (line 1552), and the P11 plan's SV3 entry and migration 0011's note.

## 3. What to do

Each test below comes with its reversal (D18): a temporary edit that must make the test fail, run, then undone, with the edit and the failing output recorded. "Fails at B-C3's head and passes at `4860b56`" means you run the test, or the planted text through `row_locks.refusal`, at both.

1. **The `U&` sentence** (item 1; F1). Apply II1 to the proof README's D14 entry. The code is unchanged for this item; the docstring already says it.
2. **The `OF` list as a reference** (item 2; F2). Apply II2. The record's "Deviations, readings and what could not be run" for B-C2 gains the reading: DM-75 6.2 (d) is read with the `OF`-list exception (DM-77 section 5).
3. **Function bodies and temporary schemas** (item 3; S1, F3; Codex's P2 on `row_locks.py:287`).
   - **The creation rule:** a statement that creates a function or a procedure (`CREATE [OR REPLACE] FUNCTION` or `PROCEDURE`, the words read as PostgreSQL reads them) fails whatever its lock, as a `DO` statement does.
   - **The filter:** `OWN_OBJECTS` excludes only `pg_catalog`, `information_schema`, the TOAST schemas and extensions, so a temporary schema's functions, procedures, views and rules count.
   - **The tests:**
     - S1's planted bodies (dollar-quoted, `'…'` and `E'…'`, each taking `FOR UPDATE` on the account table) each fail at B-C3's head, with `FOR NO KEY UPDATE` too, and pass at `4860b56`; the review's planted form is `CREATE FUNCTION pg_temp.f() RETURNS SETOF bigint LANGUAGE sql AS $$ SELECT id FROM glow_persistence_appaccount FOR UPDATE $$`;
     - an offline test pins the query's schema filter;
     - **a planted database reversal,** local under D4's conditions and informational: a temporary function, view and rule (a rule on a temporary table) created in a case's session give the counts 1, 1, 1, and the suite's own-objects line fails. Record its commands and output. If Docker is unavailable, say so.
   - **The texts:** II3 and II4 (the README), II9 (the record's row at line 1552) and II11 (`row_locks.py`'s docstring).
   - `row_locks.driver_forms_are_seen` keeps its verdict: `(0, 0, 0)` with the wider filter.
4. **The reading's qualification** (item 4; F4). Apply II6 (the README's SV3 paragraph) and II7 (the P11 plan's B-C2 line); II1 already carries the README's D14 entry. `row_locks.py`'s docstring (lines 27-28 and 454) says the same, in the README's words.
5. **Bindings the resolver did not read** (item 5; F5).
   - An item inside a parenthesised join, and an item of a `DELETE` or `MERGE` statement's `USING` list, are read as bindings, none of them plain, so an `OF` name bound there fails.
   - A join's `USING (…)` column list binds nothing: a `JOIN … USING (id)` statement is judged as before.
   - **The tests:** the review's two planted texts each fail at B-C3's head and pass at `4860b56`:
     - `SELECT 1 FROM glow_persistence_appaccount a JOIN (glow_persistence_block x JOIN glow_persistence_block y ON true) j ON true JOIN glow_persistence_match x ON true FOR UPDATE OF x`;
     - `WITH q AS (DELETE FROM glow_persistence_block z USING glow_persistence_block x WHERE z.id = x.id RETURNING z.id) SELECT 1 FROM glow_persistence_appaccount a JOIN glow_persistence_match x ON true FOR UPDATE OF x`;

     a `MERGE … USING` form fails too, and a `JOIN … USING (id)` statement keeps its verdict.
6. **A placeholder glued to a name or a dollar sign** (item 6; S2; Codex's P2 on `row_locks.py:875`).
   - **The rule:** a statement fails, whatever D14 reads in it, when both hold:
     - its text holds the word `UPDATE` anywhere, spans and comments included;
     - it has a placeholder (`%s`, `%b`, `%t`, or a named one such as `%(name)s`) whose neighbour on either side is a name character (a letter, digit, underscore, dollar sign or non-ASCII character).
   - By the manager's reading, "the word" is matched as D14 matches its other words (whole word, any case), and `%%` is a literal percent sign, not a placeholder. If you read either otherwise, say so.
   - **The tests:** S2's text (`SELECT id, $q%s$ $q1$ FROM glow_persistence_appaccount FOR UPDATE --$q1$`) and a `$q%sx$` form each fail at B-C3's head and pass at `4860b56`; a no-key account lock with `= %s`, and a statement with `%(name)s::timestamptz`, pass.
   - **Its reversal:** the rule disabled fails the failing tests.
7. **B-C1's ledger** (item 7; F6; Codex's fifth finding).
   - In both of `_as_a_client`'s wrappers, `_Ledger.check` runs before `_Ledger.served_from`, against the versions served before the command was sent.
   - **The tests,** at the wrapper's level (a new offline test file is allowed): a route command and a direct command, each answering with an unserved version it sent, fail the ledger; a read followed by a command passes.
   - **Its reversal:** the old order fails the first two.
8. **The stated limits and the records** (item 8).
   - **In the README's "Limits" and the record:** S3 (`standard_conforming_strings = off`), S4 (a placeholder against its lock clause; SQL inside a parameter's value), S5's remainder (a `stale_version` refusal caused by the batch or pair, or a `not_found` after the version check), N9 (`_resolve` quadratic in parenthesis depth), N10 (the fast path assumes PostgreSQL 15 or later; the proof pins 17), and a `dblink` query (II4). Each with its planted example from the review, as the record's "Delta re-review of B-C2" gives it.
   - **Records:**
     - N1: the record's lines 1932 and 2130 restored to their sentences ("`TABLESAMPLE`"), the planted-text table kept once, where it belongs;
     - N4: "`_Ledger` checks it for every command" (`README.md:19`; the record's line 1766) says what holds after item 7, with S5's remainder;
     - N5: the block case's return line no longer ends "hidden";
     - N6: `row_locks.py`'s loose wording at lines 35-37 and 47-50;
     - N2 and N3 in DM-77's words: II5 (the README) and II8 (the P11 plan);
     - the README's SV3 paragraph names the brief's revision 18 where it names 17;
     - the P11 plan's runs of record gain B-C3's.
9. **Tests** (item 9; N7, N8): as the stop rule's list says, each with its reversal.
10. **The local checks:**
    - **API,** in `services/api`:
      - set up: `python3.12 -m venv .venv`, then `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`;
      - then, with `GLOW_ENV=test`: `manage.py check`, `manage.py test tests --verbosity 2`, `smoke.py`, `ruff check .`, `ruff format --check .`, `mypy` and `python -m glow_persistence.static_check`;
      - the Python contract tests: `PYTHONPATH=. python -m unittest discover -s ../../packages/contracts/tests -v`, unchanged;
    - **the proof,** in `proofs/postgres-ordering`:
      - its venv and hash-locked install;
      - its offline tests under `env -i`, Ruff, `ruff format --check` and mypy;
      - the lock scan, `python -m glow_ordering_proof.account_lock_scan`, its output unchanged (52 calls, 0 joining, 7 account locks);
    - **a local database run,** if Docker allows it under D4's conditions: iteration, not evidence. Run the discovery suite at least, and item 3's database reversal.
11. **The run of record.** Commit and push your code. Wait for the Foundation run on your last code commit to finish (the push rule), then read it with your GitHub tools:
    - every job's conclusion, and the gate's line (`Application checks passed`);
    - the API test count;
    - each suite's result, D14's line (`ROW LOCKS (D14): PASS`, none refused) and its own-objects counts (0, 0, 0), and the scans;
    - the discovery suite: 66/66, and its phase duration against the job's 30-minute timeout;
    - whether a toolchain retry fired.

## 4. The record

Add a section `## Stage B, correction B-C3` at the end of `docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md`, with:
- the start gate's results, the environment check (names only) and the toolchain versions;
- **DM-77's ten pairs:** each applied, with its target file, its old passage found once before and its new text once after;
- **D14:** the creation rule, the placeholder rule, the bindings and the filter, described; a table of every text items 3, 5 and 6 plant, with its verdict at `4860b56` and at B-C3's head, and its `FOR NO KEY UPDATE` variant's where item 3 asks;
- **the ledger:** the wrappers' order before and after, and the tests;
- **the tests:** a table with one row per test, giving the file, the test, the reversal and its failing output;
- **the earlier tests:** each named test's assertion before and after, and why;
- **commands:** every command you ran, with its result line. List local database runs, item 3's reversal among them, as iteration, not evidence;
- **the run of record:** its ID, each job's result, the counts, D14's line and own-objects counts in each suite, the discovery phase's duration, and whether a retry fired;
- **B-C3's non-test lines in `services/api`:** their count (expected zero);
- every deviation from the brief, and what you could not run, and why.

Commit each logical step with a clear message ending in the session's attribution lines. Push your records commit only after the run of record has finished. Confirm that `git status` is clean, and that `git diff --name-only <START_SHA> HEAD` lists only B-C3's owned paths.

## 5. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch, your code head and records head;
- the start gate's and the environment check's results;
- DM-77's ten pairs, each applied or not;
- each rule's change, and each test with its reversal's result;
- the planted texts' verdicts before and after, and item 3's database reversal;
- the earlier tests, each before and after;
- each local check's result, and whether a local database run was used;
- the run of record: its ID, every job, the gate's line, the counts, D14's line and own-objects counts in each suite, the discovery phase's duration and whether a retry fired;
- B-C3's non-test lines in `services/api`;
- anything that met the stop rule, every deviation from the brief, and what you could not run.

# SV3 Stage B, correction B-C3: bounded delta re-review prompt

- **Owner:** App Manager 11. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 16 November 2026.**
- **Durable brief:** [SV3 — The eligibility, discovery and interactions slice](../planning/sv3-eligibility-discovery-interactions.md), revision 18, "Stage B, correction B-C3 (B-C2's delta re-review; DM-77)" and its paragraph "The review", under the five correction classes of "C4's review, and how the scan's line ends", which hold in every later review of SV3.
- **Where the result goes:** the report Nathan relays. The manager records it in the evidence record, "Delta re-review of B-C3", with a disposition for each finding (a correction, or a stated limit or record), and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 2.70 (confidence 0.64); rung probabilities low 0.00, medium 0.01, high 0.40, extra high 0.50, max 0.06, ultracode 0.03. Model probabilities Fable 5.1 0.03, Opus 5.5 0.97, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.96). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.012, Fable 5.1 at extra high 0.015, Fable 5.1 at max 0.002, Fable 5.1 at ultracode 0.001, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.010, Opus 5.5 at high 0.388, Opus 5.5 at extra high 0.485, Opus 5.5 at max 0.058, Opus 5.5 at ultracode 0.029, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Flags: boundary between high and extra high. Sent 2026-11-16T05:44:33Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action. Dev Manager 5's pre-merge read follows it.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of PR47's head, which is this prompt's commit (manager workflow, step 6).
- **Deletion condition:** prune after Stage B's PR (PR47) merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch.

---

You are the **bounded delta code and security re-review of correction B-C3, in SV3's Stage B**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one correction against the code head the previous review read, within a scope the Dev Manager fixed, under classes that fix what can lead to another correction. This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`, the head of [PR47](https://github.com/amthorn78/glow-dating-app/pull/47).

**What came before.**
- **SV3's Stage A** (PR45, `8d83474`) and **B0** (PR46, `947576d`) are merged.
- **Stage B**, **B-C1** and **B-C2** are built: code head `4860b56`. B-C2 made undo one step and made D14's rule read a statement as PostgreSQL does, failing closed (DM-75).
- **B-C2's bounded delta re-review of `4860b56`** asked for changes, narrowly, with no blocking finding (the evidence record, "Delta re-review of B-C2"): one class 2 finding (F5), four class 5 findings (F1 to F4), Codex's fifth finding confirmed (F6, B-C1's version ledger), five stated limits (S1 to S5) and ten nits.
- **DM-77** (Dev Manager 5, in `docs/continuity/dev-manager/reviews/`) ruled on each. The brief's revision 18 holds its words; its sixteen texts are II1 to II16.
- **B-C3** (branch `claude/zealous-dirac-6f5mq2`) built them: docs `a384af5`, code head `edc883e`, records `a31a79f` (the evidence record, "Stage B, correction B-C3").
- **Its run of record** is Foundation run 43809849211 on `edc883e` (push):
  - all eight jobs passed, and the gate printed `Application checks passed`;
  - API 628 tests; ordering 56/56, 115/115 and 62/62; identity 49/49; profile 69/69; discovery 66/66, its phase 159 s;
  - each suite's `ROW LOCKS (D14): PASS`, none refused, and the database's own functions, views and rules 0, 0, 0.
- **The manager verified B-C3** (the evidence record, "Manager verification of B-C3"): the diff within the owned paths; `services/api` outside its tests byte-identical to `4860b56`; DM-77's sixteen texts; the run of record; local re-runs; planted texts; two reversals of its own. It fast-forwarded the manager branch to `a31a79f`.
- **Points for this review** (the manager's verification, "For the delta re-review and the Dev Manager", and the session's departures):
  - **`_Ledger` itself changed:** it gains `snapshot()`, and `check` an optional `served` argument, beyond "the ledger's two wrappers" in II16's words. The session read item 7's "against the versions served before the command was sent" as needing them.
  - **`OWN_OBJECTS`'s filter** excludes `pg_catalog`, `information_schema`, `pg_toast` and each `pg_toast_temp_N`, and extension-owned functions as before; views and rules have no extension test, as before.
  - **The creation rule** is read on tokens, and the fast path no longer skips such text. It also refuses a body written without a string constant (`RETURN …`, `BEGIN ATOMIC … END`).
  - **Item 6's reading** (the manager's): "the word `UPDATE`" is a whole word in any case, and `%%` is a literal percent sign. S4's `= %sFOR UPDATE` form is now refused by item 6, so "Limits" keeps only SQL inside a parameter's value.
  - **Codex on PR47:** four threads that B-C3 answers, still unresolved: the fifth finding, the ledger ([r4580718359](https://github.com/amthorn78/glow-dating-app/pull/47#discussion_r4580718359)); on `892bd59`, S2 ([r4581883081](https://github.com/amthorn78/glow-dating-app/pull/47#discussion_r4581883081)) and F3 ([r4581883085](https://github.com/amthorn78/glow-dating-app/pull/47#discussion_r4581883085)); on `b67d9e3`, S1 again, a function created, called and dropped before the check ([r4582044541](https://github.com/amthorn78/glow-dating-app/pull/47#discussion_r4582044541)).

**The code head under review is `edc883e`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `edc883e` (the start gate checks this). The baseline is `4860b56`, the head B-C2's review read; `main` is at `947576d`.

**Your scope** (the brief's "Stage B, correction B-C3", paragraph "The review"; nothing outside it):
- **Every path B-C3 touches,** as it stands at `edc883e` (code) and `a31a79f` (records): `git diff b67d9e30fc4dfb5f5aebd5954d3ad9dc2d6c7a56 a31a79fb263281c787256273eb42649bf8b240c6`.
- **D14's rules** (`row_locks.py`): plant S1's bodies, Codex's three statements, S2's forms and F5's texts against the corrected rule, by each rule's words and not its examples alone. Read each verdict at `edc883e` and at `4860b56`, with its `FOR NO KEY UPDATE` variant where the rule names it.
- **The temporary-schema count** (`OWN_OBJECTS`): what it counts and excludes.
- **B-C1's ledger** (item 7): the two wrappers, `_Ledger`'s changes, the new tests and their reversal.
- **Items 1, 2, 4, 8 and 9:** the records, the stated limits and the two tests (N7, N8), each with its reversal.
- **DM-77's ten given texts for B-C3** (II1 to II9, II11), as written.
- **The runs:** 43809849211, the run of record, and PR47's pull-request run on this prompt's commit or its parent, if one has finished.
- **Out of scope:**
  - code B-C3 does not change;
  - Stage B's, B-C1's and B-C2's code outside B-C3's diff, which the earlier reviews read;
  - #1's fix, which is SV4's (the carried-items file, "Carried to SV4");
  - OD-64, and the items carried to later phases.

**The size rule** (DM-77 section 13). This review is bounded because B-C3 adds no non-test line in `services/api` (its only change there is `UndoSelectionTests`) and answers review findings without a design change; its proof code is the harness the classes judge. Check this yourself from the diff. If B-C3 changes a design (a rule or a behaviour beyond DM-77's words), say so first: a full exact-head review applies instead, and the manager takes it to the Dev Manager.

**How findings are judged.**
- **For D14's rules,** the five correction classes (the brief's "C4's review, and how the scan's line ends"), read for D14's record and against `4860b56`. These, and only these, lead to another correction:
  1. a lock of an `AppAccount` row at the reviewed head, in `services/api` or the reference design, or in a statement a suite sends, that is not `FOR NO KEY UPDATE`, however it is written (blocking);
  2. a form one of DM-75 6.2 (a) to (d)'s rules, as DM-77 reads and widens them (items 3, 5 and 6), names that the rule still passes;
  3. a regression: a form the rule refused at `4860b56` that the reviewed head passes, or a lock, a test or a case that passes there and not at the reviewed head. A planted form the reviewed head newly refuses (it fails closed) is not one; nor is a form the earlier head refused only through a pattern that a later item's words replace and exclude, which is a stated limit;
  4. a test or reversal of items 3, 5, 6, 7 and 9 that passes where it should fail;
  5. a record (`row_locks.py`'s docstring, the README, the evidence record, the P11 plan) that claims D14's rule, the own-objects check or the ledger refuses or sees more than it does. A record wrong about anything else is a record nit.

  Any other form the rule does not see is recorded, with its planted example, as a stated limit, not a correction class.
- **For the ledger, undo's test and the texts,** the exact-head review's classes that apply. Each of these is a finding:
  - a test that passes where it should fail, or fails where the code is right;
  - a Dev Manager condition unmet;
  - a record that claims more than the code, the tests or the runs show.
- **For each finding,** name its class, or say it is a stated limit, a record nit, or a rule change for the Dev Manager.

**The focus:**
1. **The creation rule (item 3), as a security boundary.** Can any statement that creates a function or a procedure pass: by case, spacing, comments or quoting between its words, `OR REPLACE`, a schema-qualified or quoted name, a body with or without a string constant, a second statement after `;`, or the fast path? Does any other statement create code that runs later and holds a lock the text does not show (a trigger, a rule, a view, an aggregate, an operator, `PREPARE`)? Say for each whether its lock is in the text D14 reads.
2. **The own-objects count (item 3).** Does `OWN_OBJECTS` count a temporary schema's functions, procedures, views and rules, and exclude only what DM-77 names? Can a function, procedure, view or rule escape it while the suite runs, other than the stated limit (one created by a path the record does not see and gone before the check)?
3. **The placeholder rule (item 6).** Can a placeholder that psycopg 3.3.6's client-side binding turns into part of a token (a dollar-quote tag, a name, a number, a keyword) pass the rule in a statement that holds `UPDATE`: by its kind (`%s`, `%b`, `%t`, named), its neighbour on either side, `%%`, case, or `UPDATE` hidden by the reading? Is any statement a suite sends refused by it? Read the run's D14 lines.
4. **The bindings (item 5).** Does an item inside a parenthesised join, or in a `DELETE` or `MERGE` statement's `USING` list, now count as a binding, none plain, so an `OF` name bound there fails? Does a join's `USING (…)` column list still bind nothing? Is any other place an item binds a name still unread (an `UPDATE … FROM` item, a `LATERAL` item, a nested `WITH`)?
5. **Regressions against `4860b56`** (class 3). List every planted form `4860b56` refused that `edc883e` passes. Is any statement a suite sends refused, or judged differently (writer, account, `FOR UPDATE`)? Compare the run's D14 lines with B-C2's run of record (43780988590).
6. **B-C1's ledger (item 7; Codex's fifth finding).** Does each wrapper check a command against the versions served before it was sent, then record its answer? Can a command's own answer, a replay's, or a concurrent answer still vouch for the version it sent? Is `_Ledger`'s change (`snapshot()`, `check`'s `served`) within item 7's words, and do the earlier ledger tests keep what they protect? Does each new test fail under the old order?
7. **The tests** (items 3, 5, 6, 7 and 9). Does each fail against its reversal? Do N7's `--` statement and N8's pinned `raise` each catch the mutant the review named?
8. **The records.**
   - DM-77's ten texts as written.
   - The proof README's D14 entry, SV3 paragraph and "Limits" (S3, S4's remainder, S5's remainder, N9, N10, `dblink`); `row_locks.py`'s docstring.
   - The P11 plan's B-C2 line, migration 0011's note and its runs of record.
   - Every claim in the record's "Stage B, correction B-C3", N1's restored sentences, N4's note and item 2's reading.
9. **Nothing else changed:** from the diff, no path outside B-C3's owned paths (II16), and no workflow, contract package, model, migration, lock file, dependency or `glow_chat` file.
10. **Codex's four threads** (above): is each answered at `edc883e`?

**Re-run, at least,** in a scratch copy of `edc883e`:
- **The checks:**
  - the API's `manage.py check`, its tests, Ruff, `ruff format --check` and mypy;
  - the proof's offline tests, Ruff, `ruff format --check` and mypy;
  - the lock scan, its output compared byte for byte with `4860b56`'s.
- **Offline reversals, at least six,** each against its test:
  - the creation rule disabled;
  - `OWN_OBJECTS`'s filter put back to `4860b56`'s, against its offline test;
  - the placeholder rule disabled;
  - one of item 5's bindings (a parenthesised join's items, or a `USING` list) left unread;
  - the ledger's wrappers put back in their old order;
  - N7's `--` removed from `_SPAN_MARKS`, or N8's `raise` removed;
  - one of your own, against a claim you doubt.
- **A database reversal** (item 3's temporary function, view and rule counting 1, 1, 1) is optional, under D4's conditions below. The session ran it locally; the record gives its result.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 11. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, thread resolutions, re-runs or workflow dispatches.
  - **Scratch work goes in a copy outside the repository,** never the checkout (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
  - **GitHub is read through your GitHub tools.** If a sub-agent reads it another way, say so in the report (B-C2's review used read-only `gh api` calls, which DM-77 accepted).
- **Network:**
  - PyPI, for hash-locked installs in a scratch copy;
  - Docker Hub, only to pull the PostgreSQL image the CI job pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`), if you choose a local run;
  - GitHub, through your tools, to read runs and PR47's threads.
- **Local database runs** are optional here and allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions): a throwaway PostgreSQL in Docker, from that image, on loopback only; a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present; removed afterwards, with its volumes. Local passes are iteration, not evidence.
- **Never:**
  - dump the environment, or print a credential, password, token, session key or key;
  - read, print or use the value of any `AWS_*` variable, or name one in a command (section 1);
  - call any provider or HDE, send any email, or run any command in `proofs/stream-chat/`;
  - connect to any database but a throwaway one you started under D4's conditions, HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:**
   `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`.
   If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*` or `CF_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_)'` prints names only. If any is present, stop and report.
3. **Three AWS names are expected:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_CA_BUNDLE` (DM-57 and DM-58). `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values. If any other `AWS_*` name is present, stop and report.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
5. **The toolchain:** CPython 3.12.14 as `python3.12`; Docker if present. Record their versions.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API). No `AWS_*` name passes.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, 947576d98b7c3103455a670c20fdba2734ff5053
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet edc883ed937c50d1a52cd82b1fa7c3d1e1482847 HEAD -- . ':!*.md' && echo "the code head under review"
git diff --quiet edc883ed937c50d1a52cd82b1fa7c3d1e1482847 origin/claude/magical-wozniak-yfmmx2 -- . ':!*.md' && echo "no code on the live branch after edc883e"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md | grep -c -E '^#+ Delta re-review of B-C3'   # must print 0
```

If any check fails, stop and report. The prompt is stale if any of these holds:
- its commit is not on the live branch;
- a non-Markdown path changed there after `edc883e`;
- this review is already recorded.

**Classify the change** as root `AGENTS.md` requires, with the trusted base policy outside the candidate tree, run from the repository's root:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
```

Expected: `"full": true`. Anything else: stop and report.

**Then read, completely, at `HEAD`:**
- root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md` and `proofs/postgres-ordering/README.md` (above all D14's entry, the SV3 paragraph and "Limits");
- the brief, revision 18: D12, D14, "C4's review, and how the scan's line ends", "Stage B, correction B-C2" and "Stage B, correction B-C3", whole;
- DM-77's report, whole, above all sections 4 to 13 and 16;
- the evidence record: "Delta re-review of B-C2", "Stage B, correction B-C3" and "Manager verification of B-C3";
- the diff `git diff 4860b56c222db719f28010845ae32d15ecbf124a edc883ed937c50d1a52cd82b1fa7c3d1e1482847`, and, whole at `HEAD`:
  - `row_locks.py`, `tests/test_row_locks_offline.py` and `tests/test_ledger_offline.py`;
  - in `interaction_cases.py`, `_Ledger`, `_as_a_client`, the block case and `row_locks.driver_forms_are_seen`;
  - `tests/test_discovery_offline.py`'s ledger tests;
  - `services/api/tests/test_interactions_offline.py`'s `UndoSelectionTests`, and `services/api/glow_discovery/interactions.py`'s `undo`.

**The run,** with your GitHub tools: 43809849211. Read every job's conclusion, the gate's line, and the Database proof checks job's suite, scan and D14 lines.

## 3. What to do

1. Review the delta against the focus, item by item, with focus 1 to 6 as security boundaries: what each rule stops, what it cannot see, and the test that proves it.
2. In a scratch copy of `edc883e`, re-run the checks and the offline reversals above, and any you doubt.
3. For each finding, give:
   - its severity (blocking, should fix, nit);
   - its file and line, and the evidence;
   - its class (1 to 5, or one of the exact-head review's classes for the ledger, undo's test and the texts), or "stated limit", "record nit", or "rule change for the Dev Manager".

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- the size rule's check, and whether a full review applies instead;
- **the verdict:** approve, approve with nits, or changes required. Changes are required only for a finding in a correction class;
- the findings, in a table: number, severity, class or "stated limit", "record nit" or "rule change for the Dev Manager", file and line, what is wrong, and the evidence;
- the answer to each focus point (1 to 10), a few lines each. Include:
  - for each stated limit, its planted example and the words for the README;
  - whether each of Codex's four threads is answered at `edc883e`;
- the reversals you re-ran, with their results;
- what you ran, and what you could not run or read.

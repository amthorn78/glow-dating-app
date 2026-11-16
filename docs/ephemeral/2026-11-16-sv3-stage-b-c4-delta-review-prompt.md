# SV3 Stage B, correction B-C4: bounded delta re-review prompt (the last of D14 under all five classes)

- **Owner:** App Manager 11. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 16 November 2026.**
- **Durable brief:** [SV3 — The eligibility, discovery and interactions slice](../planning/sv3-eligibility-discovery-interactions.md), revision 19, "Stage B, correction B-C4 (B-C3's delta re-review; DM-78)" and its paragraph "B-C4's review, and how D14's line ends", under the five correction classes of "C4's review, and how the scan's line ends".
- **Where the result goes:** the report Nathan relays. The manager records it in the evidence record, "Delta re-review of B-C4", with a disposition for each finding (a correction, or a stated limit or record), and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 2.69 (confidence 0.70); rung probabilities low 0.00, medium 0.01, high 0.36, extra high 0.57, max 0.05, ultracode 0.01. Model probabilities Fable 5.1 0.02, Opus 5.5 0.98, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.97). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.007, Fable 5.1 at extra high 0.011, Fable 5.1 at max 0.001, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.010, Opus 5.5 at high 0.353, Opus 5.5 at extra high 0.559, Opus 5.5 at max 0.049, Opus 5.5 at ultracode 0.010, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-16T18:07:06Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action. Dev Manager 5's pre-merge read follows it.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of PR47's head, which is this prompt's commit (manager workflow, step 6).
- **Deletion condition:** prune after Stage B's PR (PR47) merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch.

---

You are the **bounded delta code and security re-review of correction B-C4, in SV3's Stage B**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one correction against the code head the previous review read, within a scope the Dev Manager fixed, under classes that fix what can lead to another correction. **This is the last review of D14's rules under all five classes: from B-C4's head they are frozen** (DM-78 section 10). This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`, the head of [PR47](https://github.com/amthorn78/glow-dating-app/pull/47).

**What came before.**
- **SV3's Stage A** (PR45, `8d83474`) and **B0** (PR46, `947576d`) are merged.
- **Stage B**, **B-C1**, **B-C2** and **B-C3** are built: code head `edc883e`.
- **B-C3's bounded delta re-review of `edc883e`** asked for changes, with no blocking finding (the evidence record, "Delta re-review of B-C3"): three class 2 findings (F1, a named placeholder whose name holds `(`, a real `FOR UPDATE`; F2 and F3, two bindings unread), two class 5 findings (F4, a lock-free view or prepared statement used with `FOR UPDATE`; F5, a placeholder beside a quote), three nits.
- **DM-78** (Dev Manager 5, in `docs/continuity/dev-manager/reviews/`) ruled on each, adopted Codex's relations check as well, and froze D14's rules from B-C4's head. The brief's revision 19 holds its words; its fifteen texts are JJ1 to JJ15.
- **B-C4** (branch `claude/ecstatic-feynman-61wkt0`) built them: README `24dd91d`, code head `07d8de3`, records `8842176` (the evidence record, "Stage B, correction B-C4").
- **Its run of record** is Foundation run 43919688476 on `07d8de3` (push):
  - all eight jobs passed, and the gate printed `Application checks passed`;
  - ordering 56/56, 115/115 and 62/62; identity 49/49; profile 69/69; discovery 66/66, its phase 175 s (B-C3's: 159 s);
  - each suite's `ROW LOCKS (D14): PASS`, none refused, own objects 0, 0, 0; account-table writer locks 44,841, 127, 2,061 and 4,256, all `FOR NO KEY UPDATE`, equal to B-C3's run.
- **The manager verified B-C4** (the evidence record, "Manager verification of B-C4"): the diff within the owned paths; `services/api` unchanged; DM-78's fifteen texts; the run of record; local re-runs; planted texts; two reversals of its own. It fast-forwarded the manager branch to `8842176`.
- **Points for this review** (the manager's verification, "For the delta re-review", and the session's departures):
  - **A quoted-name shortcut** in the span test: a text whose only spans are quoted identifiers is judged by counting double quotes instead of full lexing, added after full lexing made `judge` about seven times slower; the session's fuzz of 146,871 texts agrees with the full lexer, and a test pins the two to agree.
  - **`%(a'b)s`** fails as an unterminated span, not as a placeholder inside a span: it fails closed, by another reason.
  - **`_creates`** also reads `LOCAL`, `GLOBAL` and `UNLOGGED` between `CREATE` and `VIEW`; the word `TABLE` is refused anywhere in a statement the relations check reads.
  - **The relations check reads the positions JJ4 names;** a relation in a position it does not read would escape it (DM-78 section 6).
  - **Codex on PR47:** three threads that B-C4 answers, still unresolved: F5 on `cbea3ca` ([r4588443647](https://github.com/amthorn78/glow-dating-app/pull/47#discussion_r4588443647)), F4 on `4c2f918` ([r4587204267](https://github.com/amthorn78/glow-dating-app/pull/47#discussion_r4587204267)) and S2 ([r4581883081](https://github.com/amthorn78/glow-dating-app/pull/47#discussion_r4581883081)).

**The code head under review is `07d8de3`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `07d8de3` (the start gate checks this). The baseline is `edc883e`, the head B-C3's review read; `main` is at `947576d`.

**Your scope** (the brief's "Stage B, correction B-C4", paragraph "B-C4's review, and how D14's line ends"; nothing outside it):
- **Every path B-C4 touches,** as it stands at `07d8de3` (code) and `8842176` (records): `git diff cbea3ca2c18db8168ae00ca77ff2480227f9f066 88421763f3e0a845068be22a113d6ebd5c815e9e`.
- **D14's rules** (`row_locks.py`): plant each form items 1 to 4 name, by each rule's words and not its examples alone. Read each verdict at `07d8de3` and at `edc883e`.
- **The negative controls:** item 3's offline record control (creation, use and removal), Codex's wrapper-level control for item 2, and each new test's reversal.
- **Items 5 and 6:** the nits and the records.
- **DM-78's eleven given texts for B-C4** (JJ1 to JJ11), as written.
- **The runs:** 43919688476, the run of record, and PR47's pull-request run on this prompt's commit or its parent, if one has finished.
- **Out of scope:**
  - code B-C4 does not change, among it the ledger and everything in `services/api`;
  - Stage B's, B-C1's, B-C2's and B-C3's code outside B-C4's diff, which the earlier reviews read;
  - #1's fix, which is SV4's (the carried-items file, "Carried to SV4");
  - OD-64, and the items carried to later phases.

**The size rule** (DM-78 section 11). This review is bounded because B-C4 changes no line in `services/api` and answers review findings without a design change; its proof code is the harness the classes judge. Check this yourself from the diff. If B-C4 changes a design (a rule or a behaviour beyond DM-78's words), say so first: a full exact-head review applies instead, and the manager takes it to the Dev Manager.

**How findings are judged** (the brief's "B-C4's review, and how D14's line ends"). The five classes, read for D14's record and against `edc883e`:
1. a lock of an `AppAccount` row at the reviewed head, in `services/api` or the reference design, or in a statement a suite sends that D14 passes, that is not `FOR NO KEY UPDATE`, however it is written (blocking);
2. a form one of D14's rules names (DM-75 6.2, as DM-77 and DM-78 read and widen it) that the rule still passes;
3. a regression: a form the rule refused at `edc883e` that the reviewed head passes, or a lock, a test or a case that passes there and not at the reviewed head. A planted form the reviewed head newly refuses (it fails closed) is not one;
4. a test or reversal of items 1 to 5 that passes where it should fail;
5. a record (`row_locks.py`'s docstring, the README, the evidence record, the P11 plan) that claims D14's rule refuses or sees more than it does. A record wrong about anything else is a record nit.

**Under the freeze, class 2 no longer leads to a correction.** Report each class 2 finding with its planted example and the words that would state it as a limit in the README's "Limits" and narrow the rule's words to match; it is recorded, not fixed. Classes 1, 3, 4 and 5 lead to a correction as before. Any other form a rule does not see is a stated limit, with its planted example. For each finding, name its class, or say it is a stated limit, a record nit, or a rule change for the Dev Manager.

**The focus:**
1. **Placeholders as psycopg reads them (item 1).** Does D14 read every placeholder psycopg 3.3.6's `_re_placeholder` and `_split_query` read, and no other: names of one or more characters other than `)`, the format `s`, `b` or `t`, `%%` as a literal? Compare them by planting, not by reading the pattern alone.
2. **A placeholder inside a span (item 2), as a security boundary.** Does a placeholder any part of which lies inside a string constant (every kind), a quoted identifier (every kind) or a comment (both kinds) fail, before the fast path? Is the quoted-name shortcut exact: can a text it judges have a placeholder inside a span it misses, or one outside it refuses? Does Codex's wrapper-level control show the record refusing F5's text through `note`?
3. **A view's creation (item 3).** Can a statement that creates a view pass, by case, spacing, comments or quoting between its words, `OR REPLACE`, `TEMP`, `TEMPORARY`, `RECURSIVE`, `LOCAL`, `GLOBAL`, `UNLOGGED`, `MATERIALIZED`, a second statement after `;`, or the fast path?
4. **The relations check (item 3), as a security boundary.** With the models' tables given, can a statement that takes `FOR UPDATE` and does not name the account table read a relation that is not one of them and pass: through a position the check does not read (a `LATERAL` item, a function in `FROM`, a nested `WITH`, a sub-query, `ONLY`, `*`, a quoted or mixed-case name), a schema-qualified name, a `TABLE` command, or parentheses? Does Django's `select_for_update()` on a model, with and without `OF`, still pass? Is any statement a suite sends refused? Read the run's D14 lines.
5. **The bindings (item 4).** Do a `MERGE INTO` target's alias without `AS` and a join's `USING (…) AS` alias now count as bindings, none plain? Does a join's `USING (…)` column list still bind nothing?
6. **Regressions against `edc883e`** (class 3). List every planted form `edc883e` refused that `07d8de3` passes. Is any statement a suite sends refused, or judged differently (writer, account, `FOR UPDATE`)? Compare the run's D14 lines with B-C3's run of record (43809849211).
7. **The tests** (items 1 to 5). Does each fail against its reversal? Do the negative controls fail as they should?
8. **The records.**
   - DM-78's eleven texts as written.
   - The proof README's D14 entry, SV3 paragraph and "Limits"; `row_locks.py`'s docstring, its reading, rule and resolution paragraphs and fast-path sentence against the README, and its "What it does not see" (JJ10).
   - The P11 plan's runs-of-record line.
   - Every claim in the record's "Stage B, correction B-C4", and JJ11's note.
9. **Nothing else changed:** from the diff, no path outside B-C4's owned paths (JJ15), and no workflow, contract package, model, migration, lock file, dependency, ledger or `services/api` file.
10. **Codex's three threads** (above): is each answered at `07d8de3`?
11. **The run's cost:** the discovery phase took 175 s against B-C3's 159 s, of the job's 30 minutes. Is the span test's cost bounded for the statements the suites send?

**Re-run, at least,** in a scratch copy of `07d8de3`:
- **The checks:** the proof's offline tests, Ruff, `ruff format --check` and mypy; the lock scan, its output compared byte for byte with `edc883e`'s. The API is unchanged by B-C4; run its tests if you wish.
- **Offline reversals, at least six,** each against its test:
  - `edc883e`'s placeholder pattern restored;
  - the span rule disabled;
  - the quoted-name shortcut disabled, or made to miss one span kind;
  - the view-creation rule disabled, or the fast path's creation test without `VIEW`;
  - the relations check disabled, or a schema allowed;
  - one of item 4's bindings left unread;
  - one of your own, against a claim you doubt.
- **A database reversal** (item 3's three statements in a case's session) is optional, under D4's conditions below. The session ran it locally; the record gives its result.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 11. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, thread resolutions, re-runs or workflow dispatches.
  - **Scratch work goes in a copy outside the repository,** never the checkout (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
  - **GitHub is read through your GitHub tools.** If a sub-agent reads it another way, say so in the report.
- **Network:**
  - PyPI, for hash-locked installs in a scratch copy;
  - Docker Hub, only to pull the PostgreSQL image the CI job pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`), if you choose a local run;
  - GitHub, through your tools, to read runs and PR47's threads.
- **Local database runs** are optional here and allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions):
  - **start the Docker daemon under `env -i`, with only `PATH`, `HOME` and the proxy's names** (DM-78 section 9);
  - a throwaway PostgreSQL in Docker, from that image, on loopback only;
  - a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present;
  - removed afterwards, with its volumes, and the daemon stopped.

  Local passes are iteration, not evidence.
- **Never:**
  - dump the environment, or print a credential, password, token, session key or key;
  - read, print or use the value of any `AWS_*` variable, or name one in a command (section 1), or pass one to the Docker daemon;
  - call any provider or HDE, send any email, or run any command in `proofs/stream-chat/`;
  - connect to any database but a throwaway one you started under D4's conditions, HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:**
   `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`.
   If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*` or `CF_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_)'` prints names only. If any is present, stop and report.
3. **Three AWS names are expected:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_CA_BUNDLE` (DM-57 and DM-58). `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values, and pass none to a command, the Docker daemon included. If any other `AWS_*` name is present, stop and report.
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
git diff --quiet 07d8de3dc820e51623cb8529cac124054c0b8b2b HEAD -- . ':!*.md' && echo "the code head under review"
git diff --quiet 07d8de3dc820e51623cb8529cac124054c0b8b2b origin/claude/magical-wozniak-yfmmx2 -- . ':!*.md' && echo "no code on the live branch after 07d8de3"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md | grep -c -E '^#+ Delta re-review of B-C4'   # must print 0
```

If any check fails, stop and report. The prompt is stale if any of these holds:
- its commit is not on the live branch;
- a non-Markdown path changed there after `07d8de3`;
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
- root `AGENTS.md` and `CLAUDE.md`; `proofs/postgres-ordering/README.md` (above all D14's entry, the SV3 paragraph and "Limits");
- the brief, revision 19: D14, "C4's review, and how the scan's line ends", "Stage B, correction B-C3" and "Stage B, correction B-C4" with "B-C4's review, and how D14's line ends", whole;
- DM-78's report, whole, above all sections 4 to 11 and 14;
- the evidence record: "Delta re-review of B-C3", "Stage B, correction B-C4" and "Manager verification of B-C4";
- the diff `git diff edc883ed937c50d1a52cd82b1fa7c3d1e1482847 07d8de3dc820e51623cb8529cac124054c0b8b2b`, and, whole at `HEAD`, `row_locks.py` and `tests/test_row_locks_offline.py`;
- psycopg 3.3.6's `_queries.py` (`_re_placeholder`, `_split_query`), from a hash-locked install.

**The run,** with your GitHub tools: 43919688476. Read every job's conclusion, the gate's line, and the Database proof checks job's suite, scan and D14 lines.

## 3. What to do

1. Review the delta against the focus, item by item, with focus 1 to 4 and 6 as security boundaries: what each rule stops, what it cannot see, and the test that proves it.
2. In a scratch copy of `07d8de3`, re-run the checks and the offline reversals above, and any you doubt.
3. For each finding, give:
   - its severity (blocking, should fix, nit);
   - its file and line, and the evidence;
   - its class (1 to 5), or "stated limit", "record nit", or "rule change for the Dev Manager"; for a class 2 finding, the words that state it as a limit.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- the size rule's check, and whether a full review applies instead;
- **the verdict:** approve, approve with nits, or changes required. Changes are required only for a finding in class 1, 3, 4 or 5; class 2 findings are stated limits under the freeze;
- the findings, in a table: number, severity, class or "stated limit", "record nit" or "rule change for the Dev Manager", file and line, what is wrong, and the evidence;
- the answer to each focus point (1 to 11), a few lines each. Include:
  - for each stated limit, its planted example and the words for the README;
  - whether each of Codex's three threads is answered at `07d8de3`;
- the reversals you re-ran, with their results;
- what you ran, and what you could not run or read, and whether a local database run was used (with the Docker daemon under `env -i`).

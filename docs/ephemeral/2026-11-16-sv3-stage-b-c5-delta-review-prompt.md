# SV3 Stage B, correction B-C5: short bounded delta re-review prompt (records only; class 5 and class 1)

- **Owner:** App Manager 11. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 16 November 2026.**
- **Durable brief:** [SV3 — The eligibility, discovery and interactions slice](../planning/sv3-eligibility-discovery-interactions.md), revision 20, "Stage B, correction B-C5 (B-C4's delta re-review; DM-79)", its paragraph "B-C5's review".
- **Where the result goes:** the report Nathan relays. The manager records it in the evidence record, "Delta re-review of B-C5", with a disposition for each finding, and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 1.92 (confidence 0.80); rung probabilities low 0.00, medium 0.19, high 0.70, extra high 0.11, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.99, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.99). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.188, Opus 5.5 at high 0.693, Opus 5.5 at extra high 0.109, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.002, Sonnet 5.5 at high 0.007, Sonnet 5.5 at extra high 0.001, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-16T22:31:28Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action. Dev Manager 5's pre-merge read of PR47 follows it.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of PR47's head, which is this prompt's commit (manager workflow, step 6).
- **Deletion condition:** prune after Stage B's PR (PR47) merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch.

---

You are the **short bounded delta re-review of correction B-C5, in SV3's Stage B**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). B-C5 is a records correction: it changes three docstrings and Markdown, and no code. You review it against `07d8de3`, the code head the previous review read, under class 5 and class 1 only (DM-79 section 8). This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`, the head of [PR47](https://github.com/amthorn78/glow-dating-app/pull/47).

**What came before.**
- **SV3's Stage A** (PR45, `8d83474`) and **B0** (PR46, `947576d`) are merged.
- **Stage B and B-C1 to B-C4** are built: code head `07d8de3`. D14's rules are frozen from `07d8de3` (DM-78 section 10).
- **B-C4's bounded delta re-review**, the last of D14 under all five classes, asked for changes by one class 5 finding that is record-only (F3, the record's sentence on `%()s`). It found two forms D14 does not see, stated limits under the freeze (F1, an item after a `set` or `values` that the reading takes as the end of the `FROM` list; F2, a placeholder followed by a string constant). The evidence record, "Delta re-review of B-C4", holds them with their planted examples.
- **DM-79** (Dev Manager 5, `docs/continuity/dev-manager/reviews/2026-11-16-dm-79-sv3-b-c4-delta-review-dispositions.md`) gave the limits' words, narrowed the rules' words to match, corrected F3, and ruled a records correction, B-C5, with this short review. Its sixteen texts are KK1 to KK16 (its section 11): B-C5 applies KK1 to KK11 and KK13; the manager applied KK12 and KK14 to KK16.
- **B-C5** (branch `claude/brave-gates-1ty8o2`) applied them: code head `0d784d4`, records `0f01f64` (the evidence record, "Stage B, correction B-C5").
- **Its run of record** is Foundation run 43960479739 on `0d784d4` (push):
  - all eight jobs passed, and the gate printed `Application checks passed`; no DM-41 retry fired;
  - ordering 56/56, 115/115, 13/13 and 62/62; identity 49/49; profile 69/69; discovery 66/66, its phase 135 s (B-C4's: 175 s);
  - each suite's `ROW LOCKS (D14): PASS`, 0 refused, own objects 0, 0, 0; account-table writer locks 44,841, 127, 2,061 and 4,256, all `FOR NO KEY UPDATE`, equal to B-C4's run of record (43919688476).
- **The manager verified B-C5** (the evidence record, "Manager verification of B-C5") and fast-forwarded the manager branch to `0f01f64`.
- **The session's two departures,** both recorded: its venv outside the repository, and its download of the Database job's log from the link the GitHub tools returned, outside the prompt's "PyPI only" line (AM11-32).

**The head under review.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `0d784d4` (the start gate checks this). The baseline is `07d8de3`; `main` is at `947576d`.

**Your scope** (the brief's "B-C5's review"; nothing outside it):
- **Every path B-C5 touches,** as it stands at the head: `git diff 5d1977e6d1c110b9c59be1f11030bbdbd5d3fb0f 0f01f649980b635724d8811604985c309e5bb44f`. These are the proof README, `row_locks.py` (three docstrings), the evidence record and the P11 plan.
- **The AST identity:** `row_locks.py`'s code at the head equals `07d8de3`'s with docstrings set aside.
- **DM-79's sixteen texts,** each found once at the head, as given.
- **Each narrowed or new sentence,** checked against the code at `07d8de3`.
- **The run:** 43960479739, and PR47's pull-request run on this prompt's commit or its parent, if one has finished.
- **Out of scope:**
  - D14's rules themselves, which are frozen; a form they do not see is a stated limit, not a finding to correct;
  - code B-C5 does not change, among it everything in `services/api` and the ledger;
  - the earlier stages' and corrections' code and records outside B-C5's diff, which the earlier reviews read;
  - #1's fix, which is SV4's, OD-64, and the items carried to later phases.

**The size rule** (DM-79 section 8). This review is short because B-C5 changes no code: `row_locks.py` differs from `07d8de3` in three docstrings only. Check this yourself first, by AST. If any code changed (anything but those docstrings, in any non-Markdown file), say so first: a full exact-head review applies instead, and the manager takes it to the Dev Manager.

**How findings are judged** (the brief's "B-C5's review"):
- **Class 1 (blocking):** a lock of an `AppAccount` row at the reviewed head, in `services/api` or the reference design, or in a statement a suite sends that D14 passes, that is not `FOR NO KEY UPDATE`, however it is written.
- **Class 5:** a record (`row_locks.py`'s docstrings, the README, the evidence record, the P11 plan) that claims D14's rule refuses or sees more than it does.
- **Neither:** a record wrong about anything else is a record nit; a form D14 does not see is a stated limit under the freeze, with its planted example. With the code unchanged, no other class can arise.

Class 1 and class 5 lead to a correction. Name each finding's class, or say it is a record nit or a stated limit.

**The focus:**
1. **The AST identity.** Is `row_locks.py`'s code at the head `07d8de3`'s, with docstrings set aside? Do exactly three docstrings differ: the module's, `judge`'s and `_relations`'s? Is `row_locks.py` the only non-Markdown path that differs from `07d8de3`?
2. **DM-79's texts.** Is each of KK1 to KK16 found once at the head, as given (each the content of its quoted code block in DM-79's section 11, without the `> ` markers)? KK5's, KK15's and KK16's old passages stay present once, since each new text keeps its old passage and adds to it.
3. **The narrowed sentences** (class 5), each against the code at `07d8de3`:
   - the relations check's words: "every relation name its reading binds, in any scope", the positions listed, and the exception for an item after a `set` or `values` that the reading takes as the end of the `FROM` list (README D14 entry and SV3 paragraph; the module docstring's rule paragraph; `judge`'s and `_relations`'s docstrings; the record's account; the P11 plan's B-C4 clause; the brief's D14 rule). Read `_relations`, `_bindings` and `_ENDS_FROM`. Does any narrowed sentence still claim a position the reading does not bind?
   - S4's sentence and the module docstring's S4 clause, against F2.
4. **The new limits** (README "Limits", KK5). Is each claim true at `07d8de3`? Among them:
   - F1: that `set` and `values` are among the words that end a `FROM` list; that the planted texts pass and the controls (the alias `s`; the condition in parentheses) are refused; that a statement naming the account table is judged as before, its rule needing an `OF` list and failing a name it cannot bind;
   - F2: that a placeholder followed by a string constant, glued or across whitespace holding a line end (`--` comments included), passes; the planted text passes;
   - "Django writes every `ON` condition in parentheses", and "No non-test code places a placeholder before a quote".

   Plant each example through `row_locks.refusal` at `07d8de3`'s code, with the models' tables given where the limit says so.
5. **F3's corrected sentence** (KK11): true of `edc883e`'s and `07d8de3`'s placeholder patterns?
6. **B-C5's own records:** KK2's B-C5 sentence in the README; every claim in the record's "Stage B, correction B-C5"; the P11 plan's B-C5 run-of-record sentence, against run 43960479739.
7. **Class 1.** With the code unchanged, does the run of record show any account-table lock that is not `FOR NO KEY UPDATE`, or any refused statement? Compare its D14 lines with 43919688476's.
8. **Nothing else changed:** only the four paths, and within them only B-C5's owned parts (the brief's "Correction B-C5 only", KK16): the README's D14 entry, SV3 paragraph and "Limits"; the P11 plan's SV3 entry; the evidence record; no workflow, contract package, model, migration, lock file, dependency, test or `services/api` file.
9. **The session's two departures:** does either affect the evidence?

**Re-run, at least,** in a scratch copy of the head:
- the proof's offline tests, Ruff, `ruff format --check` and mypy;
- the lock scan, its output compared byte for byte with `07d8de3`'s;
- the AST comparison, by your own script;
- the count of each of DM-79's sixteen texts, by a script that reads them from the report, never retyped;
- each planted example of focus 4 and 5 through `row_locks.refusal`, with one control of your own against a claim you doubt.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 11. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, thread resolutions, re-runs or workflow dispatches.
  - **Scratch work goes in a copy outside the repository,** never the checkout (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
  - **GitHub is read through your GitHub tools.** If a sub-agent reads it another way, say so in the report.
- **Network:**
  - PyPI, for hash-locked installs in a scratch copy;
  - GitHub, through your tools, to read runs and PR47; and GitHub's Actions results host, only through a job-log download link those tools return, to read a whole log. Record no such link.

  No Docker and no local database run: the code is unchanged.
- **Never:**
  - dump the environment, or print a credential, password, token, session key or key;
  - read, print or use the value of any `AWS_*` variable, or name one in a command (section 1);
  - call any provider or HDE, send any email, or run any command in `proofs/stream-chat/`;
  - connect to any database, HDE, Railway or any other external service, or start Docker;
  - run `migrate`, `playwright install`, `eas`, a native build or a package install script.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:**
   `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`.
   If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*` or `CF_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_)'` prints names only. If any is present, stop and report.
3. **Three AWS names are expected:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` and `AWS_CA_BUNDLE` (DM-57 and DM-58). `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values, and pass none to a command. If any other `AWS_*` name is present, stop and report.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
5. **The toolchain:** CPython 3.12.14 as `python3.12`. Record its version.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables. No `AWS_*` name passes.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, 947576d98b7c3103455a670c20fdba2734ff5053
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 0d784d494fb2046d9d6c3f00ea330a2043933df2 HEAD -- . ':!*.md' && echo "the code head under review"
git diff --quiet 0d784d494fb2046d9d6c3f00ea330a2043933df2 origin/claude/magical-wozniak-yfmmx2 -- . ':!*.md' && echo "no code on the live branch after 0d784d4"
git diff --name-only 07d8de3dc820e51623cb8529cac124054c0b8b2b HEAD -- . ':!*.md'   # expected: proofs/postgres-ordering/glow_ordering_proof/row_locks.py alone
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md | grep -c -E '^#+ Delta re-review of B-C5'   # must print 0
```

If any check fails, stop and report. The prompt is stale if any of these holds:
- its commit is not on the live branch;
- a non-Markdown path changed there after `0d784d4`;
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
- root `AGENTS.md` and `CLAUDE.md`; `proofs/postgres-ordering/README.md` (D14's entry, the SV3 paragraph, S4 and "Limits");
- the brief, revision 20: D14 and "Stage B, correction B-C5", whole;
- DM-79's report, whole;
- the evidence record: "Delta re-review of B-C4", "Manager verification of B-C4", "Stage B, correction B-C5" and "Manager verification of B-C5";
- the diff `git diff 5d1977e6d1c110b9c59be1f11030bbdbd5d3fb0f 0f01f649980b635724d8811604985c309e5bb44f`, and, at `HEAD`, `row_locks.py`'s module docstring, `judge`, `_relations`, `_bindings` and `_ENDS_FROM`;
- psycopg 3.3.6's `_queries.py` (`_re_placeholder`, `_split_query`), from a hash-locked install, for focus 4 and 5.

**The run,** with your GitHub tools: 43960479739. Read every job's conclusion, the gate's line, and the Database proof checks job's suite, scan and D14 lines.

## 3. What to do

1. Review the delta against the focus, item by item.
2. In a scratch copy of the head, re-run the checks above, and any you doubt.
3. For each finding, give:
   - its severity (blocking, should fix, nit);
   - its file and line, and the evidence;
   - its class (1 or 5), or "record nit", or "stated limit" with its planted example.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- the size rule's check, and whether a full review applies instead;
- **the verdict:** approve, approve with nits, or changes required. Changes are required only for a finding in class 1 or class 5;
- the findings, in a table: number, severity, class, "record nit" or "stated limit", file and line, what is wrong, and the evidence;
- the answer to each focus point (1 to 9), a few lines each;
- what you re-ran, with results, and what you could not run or read.

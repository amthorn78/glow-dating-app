# SV3 Stage A, correction C4: bounded delta re-review prompt

- **Owner:** App Manager 11. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 13 November 2026.**
- **Durable brief:** [SV3 — The eligibility, discovery and interactions slice](../planning/sv3-eligibility-discovery-interactions.md), revision 10, "Stage A, correction C4 (C3's delta re-review; DM-68)" and its paragraph "C4's review, and how the scan's line ends" (DM-68's termination rule).
- **Where the result goes:** the report Nathan relays. The manager records it in the evidence record, "Delta re-review of C4", with a disposition for each finding (a correction, or a stated limit or record), and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.46 (confidence 0.68); rung probabilities low 0.00, medium 0.01, high 0.54, extra high 0.43, max 0.02, ultracode 0.00. Model probabilities Fable 5.1 0.05, Opus 5.5 0.95, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.93). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.001, Fable 5.1 at high 0.027, Fable 5.1 at extra high 0.022, Fable 5.1 at max 0.001, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.009, Opus 5.5 at high 0.513, Opus 5.5 at extra high 0.408, Opus 5.5 at max 0.019, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Flags: boundary between extra high and high. Sent 2026-11-13T23:26:59Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action. Dev Manager 5's pre-merge read follows it.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of PR45's head, which is this prompt's commit (manager workflow, step 6).
- **Deletion condition:** prune after SV3 Stage A's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **bounded delta code and security re-review of correction C4 to SV3's Stage A** (eligibility and discovery) for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one correction's changes against the head the previous re-review read, with two checks read as security boundaries, under a termination rule that fixes what can lead to another correction. This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **C3's delta re-review** read code head `72ace21` (the evidence record, "Delta re-review of C3"): changes required, narrowly. No blocking finding and no app change, but:
  - **F1 to F4:** the static lock scan (`account_lock_scan.py`) passed four join forms that lock the account row `FOR UPDATE`: a function given a path in a keyword's value, a combined queryset, `complex_filter()`, and an f-string in `of=`;
  - **F5:** a generic lock's `no_key=model is not AppAccount` passed;
  - **F6:** `pages.one_snapshot_statements`' write check missed a write to a table not named `glow_…`;
  - **F7, N1, N5:** limits to state; **N2:** two tests the pre-probe matcher lacked.

  Codex found F1 to F6 too, on PR45 (`0fbc130`).
- **Dev Manager 5 disposed of them** (DM-68, SC1 to SC11, in `docs/continuity/dev-manager/reviews/`). It approved each fix and widened two: F2 to `^` and to an account lock whose receiver is a combination, a conditional, an `or` or a `:=` expression, and F5 to require the lock's own variable on the left. It also chose how the scan's line ends: after C4, the scan is a static check of the forms it names, its rules freeze, a further unseen form is a stated limit, and a real account lock stays blocking. D14's check of the row locks the suites send comes in Stage B. The brief's revision 10, "Stage A, correction C4", gives C4's eight items and this review's rule.
- **C4** (branch `claude/fervent-gates-q8ohlu`) built them: code head `ce260fc`, records `75986a8` (the evidence record, "Stage A, correction C4"). Its prompt's revision 1 stopped at its start gate with no change (the manager's error, AM11-21); revision 2 ran.
  - **Beyond the brief's forms,** its own probes found three more and C4 refuses them (`ce260fc`): `rows |= M.objects.select_for_update()…`, the lock on the right; a lock on a name that holds an account combination or conditional; a model held in a variable starting with an underscore (`_model`).
  - **It states further unseen forms as limits,** in a README entry after SC9's words, each with a planted example.
- **Its run of record** is Foundation run 43493104710 on `ce260fc` (push). All eight jobs passed, and the gate printed `Application checks passed`. Every suite passed (ordering 56/56, 115/115 and 62/62; identity 49/49; profile 69/69; discovery 40/40), and every scan was clean.
- **The manager verified C4** (the evidence record, "Manager verification of C4"): the diff within C4's owned paths; DM-68's SC8 to SC11 as given; the run of record; the offline tests; 16 planted forms refused, each passing or unseen at `72ace21`; 13 statements read by the write check; and two reversals of its own. It integrated C4 by the merge `aa68813`.
- **The session's report, for this review:**
  - `SELECT truncate_x()` (a function whose name only starts with "truncate") was a write under C3's pattern and is a read under item 6's words. The session recorded it as a stated limit; one of its verifiers called it a regression.
  - Its readings beyond the brief's examples: a `*` or `**` argument to a capitalised call counts as a join; `complex_filter(filter_obj=…)` is read like a positional argument, and an `F` there counts as a join; an in-place combination counts as a combination.

**The code head under review is `ce260fc`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `ce260fc` (the start gate checks this). The baseline is `72ace21`, which C3's delta re-review read.

**Your scope:**
- **The code:** `git diff 72ace2179a7dff74fecf6b7f06de30b7a1454dcb ce260fc`, its three non-Markdown paths, each read in full at `ce260fc`:
  - `proofs/postgres-ordering/glow_ordering_proof/account_lock_scan.py`: its docstring, the receiver and chain rules (combinations, conditionals, `and`/`or`, `:=`, in-place combinations), the keyword-value rule, `complex_filter`, `of=`, the generic branch's `no_key`, and the SQL rule;
  - `proofs/postgres-ordering/glow_ordering_proof/discovery_cases.py`: `is_write`, `READ_START`, `WRITE_WORDS` and their use in `pages.one_snapshot_statements` and the page with no cursor's control;
  - `proofs/postgres-ordering/tests/test_discovery_offline.py`: C4's tests.
- **The records, as claims about the code:**
  - the evidence record's "Stage A, correction C4" and "Manager verification of C4";
  - the scan's docstring (SC10);
  - the proof README: its SV3 heading (SC8), its sentence on C4, the lock scan's and the write check's "Limits" entries (SC9) and the further-forms entry after them;
  - the P11 plan's SV3 entry's runs-of-record sentence (SC11).
- **The runs:** 43493104710, the run of record; and PR45's pull-request run on this prompt's commit or its parent, if one has finished.
- **Out of scope:**
  - code C4 does not change. Stage A and C1 to C3 were read at `b44e6f7`, `303fdcc` and `72ace21`; report a finding there only where C4's change reaches it, or under the first correction class below;
  - Stage B (D14's row-lock check among it), OD-64's limits, and the items carried to later phases.

**The correction classes** (the brief's "C4's review, and how the scan's line ends"). These, and only these, lead to another correction:
1. a lock of an `AppAccount` row at the reviewed head, in `services/api` or the reference design, that is not `FOR NO KEY UPDATE`, however it is written (a defect in the app's locks, not the scan's, and blocking);
2. a form one of items 1 to 6's rules names that the scan or the write check still passes;
3. a regression: a form refused, or a lock, test or case passing, at `72ace21` that is not at C4's head;
4. a test or reversal of items 1 to 7 that passes where it should fail;
5. a record (the scan's docstring, the README, the evidence record, the P11 plan) that claims more than the scan or the check does.

Any other form the scan or the write check does not see is recorded, with its planted example, as a stated limit in the README's "Limits" and the record. It is not a correction class. For each finding, name its class, or say it is a stated limit or a record.

**The focus** (the brief's paragraph):
1. **Items 1 to 5, the lock scan, as a security boundary.** For each rule, plant the forms it names, by the rule's words and not its examples alone, and see each refused:
   - item 1: a call to a capitalised name other than `Q` and `F` that takes a string literal or an f-string, in a keyword's value or reached through a name it uses; its controls pass;
   - item 2: combinations (`&`, `|`, `^`), conditionals, `and`/`or` and `:=`, inline or held in a name, before and after the lock, and as the lock's receiver, an account lock among them;
   - item 3: `complex_filter()` with a dict, or any argument but a literal `Q` or a name assigned one;
   - item 4: `of=` other than a tuple or list written in the call whose every entry is a plain string literal naming no path to `AppAccount`;
   - item 5: a generic lock's `no_key` other than the literal `True` or, with no join, exactly `<the lock's own variable> is AppAccount`; the two existing helpers pass.

   Then the three further forms C4 refuses at `ce260fc`: is each refused, and does its test fail without the change?
2. **Item 6, the write check, as a security boundary.** A statement is a read only if it begins with `SELECT` or `WITH` and holds none of the words `INSERT`, `UPDATE`, `DELETE`, `MERGE`, `INTO`, `TRUNCATE` or `COPY`. Plant writes by those words and see each counted; confirm the statements the real page by cursor sends (the record lists 26) are all reads; and confirm the page with no cursor's control uses the same test.
3. **Item 7:** the matcher's two new tests (an `OR` condition, a join without an alias) each fail for the reason the rule gives.
4. **The tree** (class 1). List every `select_for_update` call and every SQL string that takes `FOR UPDATE` in `services/api` (its tests and virtual environment left out) and in the reference design, by AST and not by the scan, and read each one's lock mode. Then read the scan's counts on the tree (52 calls, none locking a queryset that joins, seven explicit account locks) and confirm it refuses no existing lock.
5. **`SELECT truncate_x()`.** At `72ace21` the write check counted it a write; at `ce260fc` it counts it a read, as item 6's words say. SC9 already states, as a limit, a write made inside a function a read calls. Judge whether this falls in class 3 or is a stated limit, and why. If it is in class 3, give the words of a fix that keeps item 6's words.
6. **The session's readings beyond the brief's examples:** a `*` or `**` argument to a capitalised call counted as a join; `complex_filter(filter_obj=…)` read as a positional argument; an in-place combination counted as a combination. Is each within its rule? Does any refuse an existing lock?
7. **The records:**
   - SC8 to SC11 as applied; the README's sentence on C4.
   - **The further-forms entry:** is each form in it truly unseen at `ce260fc` (plant its example)? Is each truly outside items 1 to 6's rules? A form a rule names is class 2, not a limit.
   - **Every claim** in the record's C4 sections holds against the code and the run.
8. **Nothing else changed:** from the diff, no path outside C4's owned paths, and no app code, workflow, contract, model, migration, lock file or dependency.

**Re-run, at least,** in a scratch copy of `ce260fc`:
- **The checks:** the proof's offline tests, `ruff`, `ruff format --check` and `mypy`; the lock scan over the tree, with its counts.
- **Offline reversals, at least six,** each against its test:
  - item 1's capitalised-call rule removed;
  - item 2's combination traversal cut to plain chains;
  - item 4's literal-only reading of `of=` undone (an f-string read by its text);
  - item 5's syntax check undone (any expression naming `AppAccount` and ` is ` passes);
  - item 6's positive rule replaced by C3's `WRITE` pattern;
  - one of your own choosing, against a claim you doubt.
- **The discovery suite, informational:** on a throwaway PostgreSQL under P06.DB's D4, if Docker allows. If you can run it, run the database reversals the record names, each failing the case: `UPDATE auth_user SET is_active = is_active WHERE id = -1` after the cursor page's transaction, E, and C2's write. Add any you doubt.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 11. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - **Scratch work goes in a copy outside the repository,** never the checkout (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
- **Network:**
  - PyPI, for hash-locked installs in a scratch copy;
  - Docker Hub, only to pull the PostgreSQL image the CI job pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`);
  - GitHub, through your tools, to read runs.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions):
  - a throwaway PostgreSQL in Docker, from that image, on loopback only;
  - a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present;
  - removed afterwards.
- **Never:**
  - dump the environment, or print a credential, password, token, session key or key;
  - read, print or use the value of any `AWS_*` variable (section 1);
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
git merge-base --all origin/main HEAD                 # expected: one line, 3240ef0acca7983e5b60b9a111be371ed5a16b74
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet ce260fc HEAD -- .github scripts services apps packages proofs ':!*.md' && echo "the code head under review"
git diff --quiet ce260fc origin/claude/magical-wozniak-yfmmx2 -- .github scripts services apps packages proofs ':!*.md' && echo "no code on the live branch after ce260fc"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md | grep -c -E '^#+ Delta re-review of C4'   # must print 0
```

If any check fails, stop and report. The prompt is stale if any of these holds:
- its commit is not on the live branch;
- a non-Markdown path changed there after `ce260fc`;
- this review is already recorded.

**Classify the change** as root `AGENTS.md` requires, with the trusted base policy outside the candidate tree:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
```

Expected: `"full": true`. Anything else: stop and report.

**Then read, completely, at `HEAD`:**
- root `AGENTS.md` and `CLAUDE.md`; `proofs/postgres-ordering/README.md`;
- the brief, revision 10: D2, D14, the owned paths, "Stage A, correction C3" and "Stage A, correction C4", with "C4's review, and how the scan's line ends";
- DM-68's report, whole, above all sections 3 and 9;
- the evidence record's "Delta re-review of C3", "Stage A, correction C4" and "Manager verification of C4";
- every file in the code diff, whole; and, read only: the two generic helpers (`glow_chat/contact.py`'s `_lock`, the reference design's `_lock`), `glow_discovery/pages.py` (`create`, `continue_page`, `_with_photos`), `glow_profiles/tx.py` (`run`, `lock_account`, `read_account_shared`), `glow_discovery/predicates.py` (`VIEWER`, `RECHECK`) and `glow_persistence/models.py`.

**The run,** with your GitHub tools: 43493104710, every job's conclusion, the gate's line, and the Database proof checks job's suite lines, including `locks.account_locks_no_key_update` and `pages.one_snapshot_statements`.

## 3. What to do

1. Review the code delta against the focus, item by item, with focus 1 and 2 as security boundaries: for each rule, what it stops, what it cannot see, and the test that proves it.
2. In a scratch copy of `ce260fc`:
   - re-run the checks and the offline reversals above, and any you doubt;
   - run the discovery suite locally under D4 if you can, informational, with the database reversals.
3. For each finding: its severity (blocking, should fix, nit), its file and line, the evidence, and its correction class (1 to 5), or "stated limit" or "record".

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- **the verdict:** approve, approve with nits, or changes required. Changes are required only for a finding in a correction class;
- the findings, in a table: number, severity, correction class or "stated limit" or "record", file and line, what is wrong, and the evidence;
- the answer to each focus point (1 to 8), a few lines each; for focus 5, the class and why; for each stated limit, its planted example and the words for the README;
- the list of every account lock in the tree with its lock mode (focus 4);
- the reversals you re-ran, with their results, the local database ones named informational;
- what you ran, and what you could not run or read.

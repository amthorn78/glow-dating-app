# SV3 Stage A, correction C5: bounded delta re-review prompt

- **Owner:** App Manager 11. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 14 November 2026.**
- **Durable brief:** [SV3 — The eligibility, discovery and interactions slice](../planning/sv3-eligibility-discovery-interactions.md), revision 11, "Stage A, correction C5 (C4's delta re-review; DM-69)" and its paragraph "C5's review", under the five correction classes of "C4's review, and how the scan's line ends" (DM-68's termination rule).
- **Where the result goes:** the report Nathan relays. The manager records it in the evidence record, "Delta re-review of C5", with a disposition for each finding (a correction, or a stated limit or record), and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.11 (confidence 0.83); rung probabilities low 0.00, medium 0.08, high 0.74, extra high 0.18, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.01, Opus 5.5 0.99, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.99). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.001, Fable 5.1 at high 0.007, Fable 5.1 at extra high 0.002, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.079, Opus 5.5 at high 0.733, Opus 5.5 at extra high 0.178, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-14T18:07:42Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action. Dev Manager 5's pre-merge read follows it.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of PR45's head, which is this prompt's commit (manager workflow, step 6).
- **Deletion condition:** prune after SV3 Stage A's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch.

---

You are the **bounded delta code and security re-review of correction C5 to SV3's Stage A** (eligibility and discovery) for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one small correction against the head the previous review read, within a scope the Dev Manager fixed, under a termination rule that fixes what can lead to another correction. This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **C4's bounded delta re-review** read code head `ce260fc` (the evidence record, "Delta re-review of C4"): changes required, narrowly. No blocking finding and no regression, but:
  - **F1 (class 2):** an account combination, conditional, boolean or `:=` held in a name was judged as the lock's receiver only when the receiver's own name held it, so `c = A | B; d = c; d.select_for_update(no_key=d is AppAccount)` passed as `generic FOR NO KEY UPDATE`, though it locks the rows `FOR UPDATE`. Codex found it too (`e297430`).
  - **F2, F3 (class 5):** record sentences that claimed more than the scan does.
  - **N1 to N3, L1 to L7, an observation:** record fixes, stated limits, and tests to pin C4's branches.
- **Dev Manager 5 disposed of them** (DM-69, AA1 to AA13, in `docs/continuity/dev-manager/reviews/`). The brief's revision 11, "Stage A, correction C5", gives C5's six items and this review's scope ("C5's review").
- **C5** (branch `claude/keen-cannon-p0ic1b`) built them: code head `43986ba`, records `9fa1798` (the evidence record, "Stage A, correction C5").
- **Its run of record** is Foundation run 43620943919 on `43986ba` (push). All eight jobs passed, and the gate printed `Application checks passed`. Every suite passed (ordering 56/56, 115/115 and 62/62; identity 49/49; profile 69/69; discovery 40/40). The lock scan's output on the tree is byte-identical to its output at `ce260fc`.
- **The manager verified C5** (the evidence record, "Manager verification of C5"): the diff within C5's owned paths; AA4 to AA13 as given; the run of record; the offline tests (296); the deeper F1 forms refused, each passing at `ce260fc`, with the plain-chain limit unchanged; and two reversals of its own. It integrated C5 by the merge `d579e34`.
- **The session's report, for this review and the Dev Manager:**
  - **A memo** of each name's chains (`_distinct`, `reached`), beyond the brief's words. The session reads it as item 1's implementation, changing no verdict (38,656 forms and 6,000 random ones).
  - **The reported kind:** for a name that only passes another on, the chains it reaches are judged before its own, so the brief's forms report as `orm`, not `generic`. No pass or refusal changes.
  - **Two new refusals of non-account locks, failing closed:** a `Match` or `Profile` combination reached through a hop, locked with `no_key=<name> is AppAccount`, which is always false. Neither shape is on the tree.
  - **A slow shape left:** names each assigned from every other in one function stay exponential (12 such names, about 2 s). Nothing like it is on the tree.

**The code head under review is `43986ba`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `43986ba` (the start gate checks this). The baseline is `ce260fc`, which C4's review read.

**Your scope** (the brief's "C5's review"; nothing outside it):
- **Item 1, planted by its words:** two and three hops through each kind of value it names (a name; a chain of calls, attributes or subscripts starting from one), from each kind of expression it names (a combination, a conditional, a boolean, an assignment expression, a name combined in place), with its reversal (the scan as at `ce260fc`); and the tree's counts and every verdict.
- **The scan's diff** (`git diff ce260fc 43986ba -- proofs/postgres-ordering/glow_ordering_proof/account_lock_scan.py`), which may change nothing but item 1's rule and the words that state it. Any other change to a rule is reported, and goes to the Dev Manager before the merge, under DM-68's freeze.
- **Item 5's tests,** each failing against its mutant (the record's N3 row in "Delta re-review of C4", and C5's section).
- **The records items 2 to 4 and 6 change:** the README (AA4 to AA9, C5's sentence, the further-forms entry's examples, the new "Limits" entry), the record (AA10 to AA12, C5's section) and the P11 plan (AA13).
- **The runs:** 43620943919, the run of record; and PR45's pull-request run on this prompt's commit or its parent, if one has finished.
- **Out of scope:** code C5 does not change; `discovery_cases.py`; Stage B (D14's row-lock check among it); OD-64; the items carried to later phases.

**The correction classes** (the brief's "C4's review, and how the scan's line ends"), against `ce260fc`. These, and only these, lead to another correction:
1. a lock of an `AppAccount` row at the reviewed head, in `services/api` or the reference design, that is not `FOR NO KEY UPDATE`, however it is written (blocking);
2. a form one of the rules names (C4's items 1 to 6, C5's item 1) that the scan or the write check still passes;
3. a regression: a form refused, or a lock, test or case passing, at `ce260fc` that is not at C5's head;
4. a test or reversal of C5's items 1 and 5 that passes where it should fail;
5. a record (the scan's docstring, the README, the evidence record, the P11 plan) that claims more than the scan or the check does.

Any other form the scan does not see is recorded, with its planted example, as a stated limit, not a correction class. For each finding, name its class, or say it is a stated limit, a record, or a rule change for the Dev Manager.

**The focus:**
1. **Item 1, as a security boundary.** Plant two and three hops through each kind of value, from each kind of expression, by the rule's words and not its examples alone; see each account form refused, and the controls (`no_key=True`; the plain-chain limit) pass as the brief says. Run the reversal.
2. **The memo, as a security boundary.** `_distinct` keeps one chain among those `_judged_alike` (whether `AppAccount` is among its names, whether any name is capitalised, whether it starts from a variable, and that variable). Can two chains it treats as alike be judged differently by `_judge` or by the join rule, so that a refusal is lost? Can `reached`, keyed by name and `seen`, return a result computed for another context? Plant forms that would separate them.
3. **The scan's diff:** does it change anything but item 1's rule and the words that state it? Judge the reported kind and the two new fail-closed refusals of non-account forms: within item 1's words, or a rule change for the Dev Manager?
4. **The tree** (class 1). The scan's counts (52, 0, 7) and every per-call verdict, compared with `ce260fc`'s; no existing lock refused.
5. **Item 5:** each test fails against its mutant; name any listed mutant that still passes.
6. **The records:** AA4 to AA13 as applied; the README's sentence on C5; the further-forms entry's new examples and the new "Limits" entry, each example passing at `43986ba` as the record says; every claim in C5's section, and the session's addendum (round 2 ended at 45 confirmed and 5 refuted).
7. **Nothing else changed:** from the diff, no path outside C5's owned paths, and no app code, `discovery_cases.py`, workflow, contract, model, migration, lock file or dependency.

**Re-run, at least,** in a scratch copy of `43986ba`:
- **The checks:** the proof's offline tests, `ruff`, `ruff format --check` and `mypy`; the lock scan over the tree, with its counts, compared with `ce260fc`'s output.
- **Offline reversals, at least four,** each against its test:
  - item 1's transitive step removed (a name's own values only);
  - the memo removed (`_distinct` returning its input), against the tests and against your planted forms, to confirm it changes no verdict;
  - two of item 5's mutants, of your choosing;
  - one of your own, against a claim you doubt.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 11. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - **Scratch work goes in a copy outside the repository,** never the checkout (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
- **Network:**
  - PyPI, for hash-locked installs in a scratch copy;
  - Docker Hub, only to pull the PostgreSQL image the CI job pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`), if you choose a local run;
  - GitHub, through your tools, to read runs.
- **Local database runs** are optional here and allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions): a throwaway PostgreSQL in Docker, from that image, on loopback only; a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present; removed afterwards.
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
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables. No `AWS_*` name passes.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, 3240ef0acca7983e5b60b9a111be371ed5a16b74
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 43986ba HEAD -- .github scripts services apps packages proofs ':!*.md' && echo "the code head under review"
git diff --quiet 43986ba origin/claude/magical-wozniak-yfmmx2 -- .github scripts services apps packages proofs ':!*.md' && echo "no code on the live branch after 43986ba"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md | grep -c -E '^#+ Delta re-review of C5'   # must print 0
```

If any check fails, stop and report. The prompt is stale if any of these holds:
- its commit is not on the live branch;
- a non-Markdown path changed there after `43986ba`;
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
- the brief, revision 11: D2, D14, the owned paths, "Stage A, correction C4" (with "C4's review, and how the scan's line ends") and "Stage A, correction C5" (with "C5's review");
- DM-69's report, whole, above all sections 3 and 8;
- the evidence record's "Delta re-review of C4", "Stage A, correction C5" and "Manager verification of C5";
- `account_lock_scan.py` and C5's tests in `tests/test_discovery_offline.py`, whole; and, read only, the two generic helpers (`glow_chat/contact.py`'s `_lock`, the reference design's `_lock`).

**The run,** with your GitHub tools: 43620943919, every job's conclusion, the gate's line, and the Database proof checks job's suite lines, including `locks.account_locks_no_key_update`.

## 3. What to do

1. Review the code delta against the focus, item by item, with focus 1 and 2 as security boundaries: what the rule stops, what it cannot see, and the test that proves it.
2. In a scratch copy of `43986ba`, re-run the checks and the offline reversals above, and any you doubt.
3. For each finding: its severity (blocking, should fix, nit), its file and line, the evidence, and its correction class (1 to 5), or "stated limit", "record", or "rule change for the Dev Manager".

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- **the verdict:** approve, approve with nits, or changes required. Changes are required only for a finding in a correction class;
- the findings, in a table: number, severity, class or "stated limit", "record" or "rule change for the Dev Manager", file and line, what is wrong, and the evidence;
- the answer to each focus point (1 to 7), a few lines each; for each stated limit, its planted example and the words for the README;
- the reversals you re-ran, with their results;
- what you ran, and what you could not run or read.

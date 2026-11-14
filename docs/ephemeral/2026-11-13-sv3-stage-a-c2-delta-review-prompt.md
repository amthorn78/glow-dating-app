# SV3 Stage A, correction C2: delta re-review prompt

- **Owner:** App Manager 11. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 13 November 2026.**
- **Durable brief:** [SV3 — The eligibility, discovery and interactions slice](../planning/sv3-eligibility-discovery-interactions.md), revision 8, "Stage A, correction C2" and its paragraph "C2's review" (DM-65 section 3.3).
- **Where the result goes:** the report Nathan relays. The manager records it in the evidence record, "Delta re-review of C2", with a disposition for each finding (fix before the merge, or carry), and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.28 (confidence 0.79); rung probabilities low 0.00, medium 0.01, high 0.70, extra high 0.28, max 0.01, ultracode 0.00. Model probabilities Fable 5.1 0.03, Opus 5.5 0.97, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.96). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.021, Fable 5.1 at extra high 0.008, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.010, Opus 5.5 at high 0.679, Opus 5.5 at extra high 0.272, Opus 5.5 at max 0.010, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-13T01:13:44Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action. The Dev Manager's pre-merge read follows it.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of PR45's head, which is this prompt's commit (manager workflow, step 6).
- **Deletion condition:** prune after SV3 Stage A's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **delta code and security re-review of correction C2 to SV3's Stage A** (eligibility and discovery) for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one correction's changes against the head the full review already read, with two of them read as security boundaries. This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **The exact-head review of Stage A** read code head `b44e6f7` (Stage A's `ad9ff08` with correction C1) in full, with a threat model. Its verdict: **changes required, narrowly**. It found no blocking finding, seven should-fix findings (F1 to F7) and six nits (N1 to N6). It is in the evidence record, "Exact-head review of Stage A".
- **The Dev Manager disposed of them** (DM-65, RV1 to RV10). C2 took F1 to F6, N1 and N6, with DM-63's LM5 (three texts still giving the account lock as `FOR UPDATE`) and DM-64's T1 to T9 (the privacy scans matching what the run's own clock prints). F7, the two-way rule's disclosure, is named in the brief's D8. Nathan has since decided to bound it (OD-64); that work is carried to before P11 and is not in this review.
- **C2** (branch `claude/practical-cray-h7t08x`) built its items, then stopped at its stop rule. A migration time printed without a fraction was a clock text DM-64's rules could not cover.
- **DM-66 ruled** option (b): each migration time in the two suites' results JSON is written with a six-digit fraction. It also approved C2's four deviations: the README's wider changes, two allowlisted labels, item 2's checks inside `pages.stale_cursors`, and T7's lines withheld in CI when a scan fails. C2 then finished.
- **C2's code head is `303fdcc`;** its records are `c79bfb6`. The evidence record's "Stage A, correction C2" holds its items, each reversal's failing line, T5's list and its runs.
- **Its run of record** is Foundation run 43337467715 on `303fdcc` (push). All eight jobs passed, and the gate printed `Application checks passed`. Every suite passed: identity 49/49, profile 69/69, discovery 40/40. Every scan was clean.
- **The first CI run of C2's code,** 43331902479 on `c1fac35`, ran before DM-66's change. It is not the run of record.
- **The manager verified C2** (the evidence record, "Manager verification of C2"), re-running two reversals, and integrated it by the merge `8bd983f`.

**The code head under review is `303fdcc`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `303fdcc` (the start gate checks this). The baseline is `b44e6f7`, which the full review read; this review reads what C2 changed and what that change touches.

**Your scope:**
- **The code:** `git diff b44e6f7e42abfa6d1f24ca9a429f07e15684fe74 303fdcca30788bf88a65f65e50d532971ab435a4`, its 13 non-Markdown paths, each read in full at `303fdcc`:
  - `proofs/postgres-ordering/glow_ordering_proof/`:
    - `profile_support.py`: `kind`, `Matcher`, `PLAN_TIMING`, and `ValueLedger.found_in` and `where`;
    - `profile_cases.py`: `_found_in_database` and `_named`;
    - `profile_suite.py`: `duration`, `migration_time`, `migration_times`, `output_texts` and the T7 lines;
    - `discovery_suite.py`;
    - `discovery_cases.py`: `pages.one_snapshot_statements`, `pages.stale_cursors`, `distance.choice_no_longer_offered` and `pointers.name_order`;
    - `account_lock_scan.py`;
    - `discovery_settings.py` (its docstring);
  - the proof's offline tests, `tests/test_profile_offline.py` and `tests/test_discovery_offline.py`;
  - `services/api/glow_discovery/keys.py` and `services/api/glow_chat/reads.py` (their module docstrings), and `services/api/tests/test_discovery_offline.py` (one comment);
  - `.github/workflows/foundation.yml` (one comment line).
- **The records, as claims about the code:**
  - the evidence record's "Stage A, correction C2" and "Manager verification of C2";
  - the P11 plan's SV3 Stage A entry: its runs of record and its concurrency line;
  - the data model's `AccountAgeState` and `RecommendationBatch` sentences that C2 rewrote;
  - `discovery-fixtures.md`'s server line;
  - the proof README's SV3 paragraph, its scan's layout row and its "Limits";
  - the CI policy's discovery sentence (`docs/operations/ci-and-branch-policy.md`, "not its tie-break"), against the workflow.
- **The runs:** 43337467715, the run of record; 43331902479; and PR45's pull-request run on this prompt's commit or its parent, if one has finished.
- **Out of scope:**
  - code C2 does not change. All of Stage A and C1 was read at `b44e6f7`; report a finding there only where C2's change reaches it;
  - Stage B (like, pass, the match, unmatch, block, resurfacing, undo and rematch);
  - OD-64's limits, which are not built;
  - the items the brief carries to later phases.

**The focus** (the brief's "C2's review"; DM-64 T9):
1. **The value scans and the run's clock, as a security boundary** (DM-64 T1 to T9, with DM-66):
   - **The rules:**
     - T1: every scan applies the rule for each kind of value;
     - T2: a coordinate's form counts unless it follows a digit, or a digit and a colon;
     - T3: a time counts unless it sits inside an HTTP or email date, or a fraction of a second follows it;
     - T4: durations are written to two decimals, and the discovery scan does not count a match inside a plan's timing;
     - DM-66: migration times carry a six-digit fraction.

     Is each rule no wider than the clock text it exists for?
   - **T5's list** (the record): does it name every clock text that reaches what the scans read, and is each covered?
   - **No real print is lost** beyond the README's "Limits". Construct the places a real leak could take and check that each still counts:
     - a held coordinate in a JSON value, after a space, a quote, a minus sign or an `=`, in a URL, and in a log line;
     - a held birth time in a response body, a log line and a write;
     - a held date in each of `forms`' shapes.

     Name any that no longer counts and is not a stated limit.
2. **The database search** (`profile_cases._found_in_database`):
   - Does reading each column through `json_each(row_to_json(t))` miss any table, column or type the search read before C2?
   - Do the failure labels name `table.column` only, never a value? Is the label test's allowlist change exactly the two `_named` calls?
3. **The lock scan, as a security boundary** (item 3, F3):
   - Does it judge every `select_for_update` whose queryset joins the account table: `select_related`, a relation path in a chained call, a `Q` or an `F`, and a path held in a variable?
   - Is `of=` judged against the foreign keys to `AppAccount` it reads from `models.py`?
   - What can it not see: a dynamic path, raw SQL, `.extra()`, `raw()`, or a queryset passed between functions? Is each counted as a join or missed, and is that stated?
   - Does any account lock in `services/api` escape it today?
4. **The new and changed cases, each with its reversal:**
   - `pages.one_snapshot_statements` (F1);
   - `pages.stale_cursors`' three new causes and `distance.choice_no_longer_offered` (F2);
   - `pointers.name_order` (F4).

   Could any pass while the behaviour it guards is wrong?
5. **App code and the workflow:**
   - By AST, `keys.py` and `reads.py` change only their docstrings; the API test changes in one comment.
   - `foundation.yml` changes in one comment line, and no step, condition or command changed.
6. **The proof's secret handling:**
   - The job's checks and its uploads are unchanged.
   - T7's messages name a kind and a text, never a value.
   - The README's statement holds that CI withholds T7's lines whenever a scan fails.
7. **The records:** every claim in the texts listed in the scope holds against the code and the runs.

**Re-run, at least,** in a scratch copy of `303fdcc`:
- **The checks:**
  - the proof's offline tests, `ruff`, `ruff format --check` and `mypy`;
  - in `services/api`, with `GLOW_ENV=test`: `manage.py check`, `manage.py test tests`, `ruff` and the configured `mypy`.
- **Offline reversals, at least five:**
  - T2's look-behinds removed, against the clock tests;
  - T3's fraction rule removed, against the clock tests;
  - the lock scan's join judgement disabled, against its planted joins;
  - `migration_time` writing plain `isoformat()`, against its test;
  - one of your own choosing: a real leak the rules must still catch.
- **The profile and discovery suites, informational:** on a throwaway PostgreSQL under P06.DB's D4, if Docker allows. If you can run them, add database reversals you doubt, such as:
  - the recheck split into two statements;
  - one of the three new stale causes not checked;
  - a page by cursor that writes.

**What comes after this review: the correction classes.** Report every finding with its severity. A correction takes every blocking finding, and any should-fix finding that could do any of these:
- let a scan miss a real member value or secret the run handled, beyond a limit the README states;
- let the lock scan miss a lock that takes an account row `FOR UPDATE`, through a join or otherwise;
- let a test pass where it should fail, or fail where the code is right;
- change app behaviour, a lock, a predicate, the selection, the recheck or a writer;
- leave a Dev Manager condition unmet (DM-63 LM5, DM-64 T1 to T9, DM-65 RV5 to RV8, DM-66 CK1 to CK4);
- make a record claim more than the code, the tests or the runs show.

Everything else goes into the records. For each finding, say whether it falls in one of these classes.

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
git diff --quiet 303fdcca30788bf88a65f65e50d532971ab435a4 HEAD -- .github scripts services apps packages proofs ':!*.md' && echo "the code head under review"
git diff --quiet 303fdcca30788bf88a65f65e50d532971ab435a4 origin/claude/magical-wozniak-yfmmx2 -- .github scripts services apps packages proofs ':!*.md' && echo "no code on the live branch after 303fdcc"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md | grep -c -E '^#+ Delta re-review of C2'   # must print 0
```

If any check fails, stop and report. The prompt is stale if any of these holds:
- its commit is not on the live branch;
- a non-Markdown path changed there after `303fdcc`;
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
- the brief, revision 8: D2, D7, D8, D14, the owned paths, "Review plan" and "Stage A, correction C2";
- the Dev Manager's DM-63 to DM-66 reports (`docs/continuity/dev-manager/reviews/`);
- the evidence record's "Exact-head review of Stage A", "Stage A, correction C2" and "Manager verification of C2";
- every file in the code diff, whole.

**The runs,** with your GitHub tools: 43337467715, every job's conclusion, the gate's line, and the Database proof checks job's suite lines; 43331902479, its jobs and discovery lines.

## 3. What to do

1. Review the code delta against the focus, item by item, with focus 1 and 3 as security boundaries: for each, what the rule stops, what it cannot see, and the test that proves it.
2. In a scratch copy of `303fdcc`:
   - re-run the checks and the offline reversals above, and any you doubt;
   - run the profile and discovery suites locally under D4 if you can, informational.
3. For each finding: its severity (blocking, should fix, nit), its file and line, the evidence, and whether it falls in a correction class.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- **the verdict:** approve, approve with nits, or changes required;
- the findings, in a table: number, severity, correction class or not, file and line, what is wrong, and the evidence;
- the answer to each focus point (1 to 7), a few lines each;
- the reversals you re-ran, with their results, the local database ones named informational;
- what you ran, and what you could not run or read.

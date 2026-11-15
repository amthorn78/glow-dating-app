# SV3 Stage B, B0: bounded delta re-review prompt

- **Owner:** App Manager 11. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 15 November 2026.**
- **Durable brief:** [SV3 — The eligibility, discovery and interactions slice](../planning/sv3-eligibility-discovery-interactions.md), revision 13, "Stage B, B0: the proof's tooling (DM-71)" and its paragraph "B0's review", under the five correction classes of "C4's review, and how the scan's line ends" (DM-68's termination rule, class 3 as DM-70's BB1 words it).
- **Where the result goes:** the report Nathan relays. The manager records it in the evidence record, "Delta re-review of B0", with a disposition for each finding (a correction, or a stated limit or record), and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.21 (confidence 0.72); rung probabilities low 0.00, medium 0.11, high 0.58, extra high 0.31, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.01, Opus 5.5 0.99, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.99). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.001, Fable 5.1 at high 0.006, Fable 5.1 at extra high 0.003, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.109, Opus 5.5 at high 0.574, Opus 5.5 at extra high 0.307, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-15T01:53:41Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action. Dev Manager 5's pre-merge read follows it.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of PR46's head, which is this prompt's commit (manager workflow, step 6).
- **Deletion condition:** prune after B0's PR (PR46) merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch.

---

You are the **bounded delta code and security re-review of B0, the proof-tooling session before SV3's Stage B**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one small change to the disposable-PostgreSQL proof against the head `main` holds, within a scope the Dev Manager fixed, under a termination rule that fixes what can lead to a correction. This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`, the head of [PR46](https://github.com/amthorn78/glow-dating-app/pull/46).

**What came before.**
- **SV3's Stage A** merged as PR45 at `8d83474`, with corrections C1 to C5. Its proof holds a static scan of explicit account row locks (`account_lock_scan.py`), whose rules DM-68 froze after C4, and the profile and discovery suites' scans for member values in their output (DM-64's T1 to T9).
- **Items were carried to Stage B** during Stage A's reviews. **DM-71** (Dev Manager 5, in `docs/continuity/dev-manager/reviews/`) placed those that change only the proof's tooling in B0, in its own PR before Stage B, and read the one design among them: a bound on the scan's receiver rule (1,000 states, 100 names followed). The brief's revision 13 gives B0's nine items, its stop rule and this review's scope ("B0's review").
- **B0** (branch `claude/focused-ride-q5itu1`) built them: code head `9fed9a5`, records `c193e08` and `0ca2a0e` (the evidence record, "Stage B, B0").
- **Its run of record** is Foundation run 43661629369 on `9fed9a5` (push). All eight jobs passed, and the gate printed `Application checks passed`. Every suite passed (ordering 56/56, 115/115 and 62/62; identity 49/49; profile 69/69; discovery 40/40), with every secret and value scan clean. The lock scan's output on the tree is byte-identical to its output at `8d83474`.
- **The manager verified B0** (the evidence record, "Manager verification of B0"): the diff within B0's owned paths; the given words; the run of record; the offline tests (314); the bound's planted forms at both heads; and two reversals of its own. It integrated B0 by fast-forward.
- **Points the session and the manager raise, for this review and the Dev Manager:**
  - **C2's three assertions** (AM11-22): narrowing T3 failed three assertions of C2's `RunClockTests` that pinned the wider rule: the email date as a clock text, the `Expires` text read in any text, and the README limit `Mon, 15 Jun 1990 04:13:27 GMT`. The session converted them under the narrowed rule, with reversals against the wider rule, and asks that its reading (item 5's own words, not a regression) be confirmed. The stop rule's clause "if a test of C1's to C5's sections no longer passes" did not foresee it.
  - **`profile_support.py`'s signatures:** `Matcher.occurs`, `ValueLedger.found_in` and `ValueLedger.where` gain the response headers' text (or its name), so that the narrowed rule reads that text alone. The manager reads this as T3's rule itself, within B0's owned paths.
  - **The headers' rule is narrower than the brief's words:** it anchors the whole line and lists the HTTP day and month names. It exempts less; anything else counts.
  - **States as the brief counts them:** 8 names give 257 states by the brief's words (a name followed under a distinct `seen`); DM-71's table gave 513 from a prototype that also counted the model's memo entries.

**The code head under review is `9fed9a5`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `9fed9a5` (the start gate checks this). The baseline is `8d83474`, `main`'s head.

**Your scope** (the brief's "B0's review"; nothing outside it):
- **Item 1, planted by its words:** each limit just inside and just beyond, the 14 names and the 500 hops, with its reversal (the scan as at `8d83474`); and the tree's counts and every verdict.
- **The scan's diff** (`git diff 8d83474 9fed9a5 -- proofs/postgres-ordering/glow_ordering_proof/account_lock_scan.py`), which may change nothing but item 1's rule and the docstrings. Any other change to a rule is reported, and goes to the Dev Manager before the merge, under DM-68's freeze.
- **Items 4 to 6,** each test failing against its mutant or its reversal: the pinning tests (F3, F12); T3 narrowed and `forms` widened, with C2's three converted assertions; the database search's offline test.
- **Items 7 and 8:** the discovery tests moved before `unittest.main()` and the query plans' `batch` parameter removed; the 1,000-part stated limit.
- **The records:** the scan's and `one_snapshot_statements`' docstrings in their given words; the README's SV3 heading, B0's sentence and its "Limits" for items 1, 5 and 8; the record's "Stage B, B0"; and the P11 plan's run of record.
- **The runs:** 43661629369, the run of record; and PR46's pull-request run on this prompt's commit or its parent, if one has finished.
- **Out of scope:** code B0 does not change; app code; Stage B (D14's row-lock record, the probe's reach, D14's reach, `VIEWER`'s column); OD-64; the items carried to later phases.

**How findings are judged.**
- **For the lock scan and the write check,** the correction classes (the brief's "C4's review, and how the scan's line ends"), against `8d83474`. These, and only these, lead to another correction:
  1. a lock of an `AppAccount` row at the reviewed head, in `services/api` or the reference design, that is not `FOR NO KEY UPDATE`, however it is written (blocking);
  2. a form one of the rules names (C4's items 1 to 6, C5's item 1, B0's item 1) that the scan or the write check still passes;
  3. a regression, in the brief's words: "a form the scan or the write check refused at the head the review compares against (`8d83474` for this review) that the reviewed head passes, or a lock in `services/api` or the reference design, a test or a case that passes there and not at the reviewed head. A planted form that the reviewed head newly refuses (it fails closed) is not one; nor is a form the earlier head refused only through a pattern that a later item's words replace and exclude, which is a stated limit";
  4. a test or reversal of B0's items 1 and 4 that passes where it should fail;
  5. a record (the scan's docstring, the README, the evidence record, the P11 plan) that claims more than the scan or the check does.

  Any other form the scan does not see is recorded, with its planted example, as a stated limit, not a correction class.
- **For the value scans** (items 5 and 6), DM-64 T9's reading: no real print lost, and a clock text left uncounted only where its rule says. A real print the narrowed rule or the new forms miss, or a clock text left uncounted beyond the rule's words, is a finding; so is a test of items 5 and 6 that passes where it should fail.
- **For each finding,** name its class, or say it is a stated limit, a record, or a rule change for the Dev Manager.

**The focus:**
1. **Item 1, as a security boundary.** Plant each limit just inside and just beyond by its words, not its examples alone: names followed along one chain, and states counted as the brief defines them (a name followed under a distinct `seen`; a name with no assignment in the function counts toward neither). Can any form go beyond a limit and pass, or be judged differently within both limits than at `8d83474`? Is every `BoundExceeded` a refusal, whatever the lock's `no_key` or model? Does the order in which chains are judged, which F2's sentence describes, stay the same? Run the reversal.
2. **The scan's diff:** does it change anything but item 1's rule and the docstrings? Is the 1,000-part limit (item 8) as the README and the docstring state it: the scan exits 1 at 1,000 parts and passes 300?
3. **The tree** (class 1): the scan's counts (52, 0, 7) and every per-call verdict, compared with `8d83474`'s output byte for byte; no existing lock refused.
4. **T3 and `forms`, by T9's reading.**
   - A held time after any other date, or in any text but the response headers', counts; a held date in the new HTTP and email shapes counts.
   - Only an `Expires` header's own time, in the headers' text, is left uncounted. Does the anchored rule match the header as the suites record it (one `Name: value` line per header)?
   - Do the suites still scan every text they scanned before (the log records, the process's writes, the response headers, the results JSON), for secrets and for member values?
   - The clock clause: can a case hold a date the run's clock prints, which the new forms would match?
   - C2's three converted assertions: does each pin only the wider rule, so that its conversion is item 5's own words? Or is any a regression (class 3, or a value scan finding)?
   - The new signatures of `occurs`, `found_in` and `where`: T3's rule, or beyond B0's owned paths?
5. **Items 4 and 6:** each pinning test fails against its mutant; the database search's test fails against the old matcher, and its labels name `table.column` without the value. Name any mutant or reversal that still passes.
6. **Items 7 and 8:** the discovery test file, run as a script, runs every test; removing the `batch` parameter changes no plan or result; the 1,000-part limit's planted example.
7. **The records:** the given words in the two docstrings; the README's B0 sentence and its "Limits" entries for items 1, 5 and 8, each planted example behaving as stated at `9fed9a5`; every claim in the record's "Stage B, B0" (the bound's times are measured, not asserted); the P11 plan's run of record.
8. **Nothing else changed:** from the diff, no path outside B0's owned paths, and no app code, workflow, contract, model, migration, lock file or dependency.

**Re-run, at least,** in a scratch copy of `9fed9a5`:
- **The checks:** the proof's offline tests, `ruff`, `ruff format --check` and `mypy`; the lock scan over the tree, compared byte for byte with `8d83474`'s output.
- **Offline reversals, at least five,** each against its test:
  - the bound removed (the scan as at `8d83474`), against item 1's tests and your planted forms;
  - one of the two limits' checks disabled alone, against its test;
  - T3's wider rule restored, and `forms` without the new shape;
  - one of item 4's mutants, of your choosing;
  - the database search's old matcher;
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
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables. No `AWS_*` name passes.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, 8d83474a354603cee11b8a09fe66b63a3602074f
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 9fed9a5 HEAD -- .github scripts services apps packages proofs ':!*.md' && echo "the code head under review"
git diff --quiet 9fed9a5 origin/claude/magical-wozniak-yfmmx2 -- .github scripts services apps packages proofs ':!*.md' && echo "no code on the live branch after 9fed9a5"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-11-sv3-eligibility-discovery-interactions.md | grep -c -E '^#+ Delta re-review of B0'   # must print 0
```

If any check fails, stop and report. The prompt is stale if any of these holds:
- its commit is not on the live branch;
- a non-Markdown path changed there after `9fed9a5`;
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
- root `AGENTS.md` and `CLAUDE.md`; `proofs/postgres-ordering/README.md`;
- the brief, revision 13: D2, D14, the owned paths, "Stage A, correction C4" (with "C4's review, and how the scan's line ends"), "Stage A, correction C5" and "Stage B, B0: the proof's tooling (DM-71)" (with "B0's review");
- DM-71's report, whole, above all sections 3.1, 3.2, 7 and 9; DM-70's sections 4.3 and 9; and DM-64's T1 to T9 as the record and the README state them;
- the evidence record's "Delta re-review of C2" (N1, N3), "Delta re-review of C5", "Stage B, B0" and "Manager verification of B0";
- whole: `account_lock_scan.py`; `profile_support.py`; the value scans' calls in `profile_suite.py` and `discovery_suite.py`; `discovery_cases.py`'s `one_snapshot_statements` and the query plans; and B0's tests in `tests/test_discovery_offline.py` and `tests/test_profile_offline.py`; read only, `profile_cases.py`'s `_found_in_database`.

**The run,** with your GitHub tools: 43661629369, every job's conclusion, the gate's line, and the Database proof checks job's suite and scan lines, including `locks.account_locks_no_key_update`.

## 3. What to do

1. Review the code delta against the focus, item by item, with focus 1 and 4 as security boundaries: what the rule stops, what it cannot see, and the test that proves it.
2. In a scratch copy of `9fed9a5`, re-run the checks and the offline reversals above, and any you doubt.
3. For each finding: its severity (blocking, should fix, nit), its file and line, the evidence, and its class (1 to 5, or a value scan finding under T9's reading), or "stated limit", "record", or "rule change for the Dev Manager".

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- **the verdict:** approve, approve with nits, or changes required. Changes are required only for a finding in a correction class, or a value scan finding under T9's reading;
- the findings, in a table: number, severity, class or "stated limit", "record" or "rule change for the Dev Manager", file and line, what is wrong, and the evidence;
- the answer to each focus point (1 to 8), a few lines each, with your reading of C2's three converted assertions; for each stated limit, its planted example and the words for the README;
- the reversals you re-ran, with their results;
- what you ran, and what you could not run or read.

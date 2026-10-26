# M04-C1 re-review prompt — the exact-head re-review of the correction pass

- **Owner:** App Manager 8. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 26 October 2026.**
- **Durable brief:** [M04 — Branch hygiene](../planning/m04-branch-hygiene.md), revision 3; its "Sessions" lines for the exact-head review and M04-C1.
- **Where the result goes:**
  - The reviewer reports to Nathan.
  - The manager records the re-review and its disposition in the [M04 evidence record](../testing/evidence/2026-10-26-m04-branch-hygiene.md), "Re-review of M04-C1", and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.33 (confidence 0.75); rung probabilities low 0.00, medium 0.03, high 0.64, extra high 0.31, max 0.02, ultracode 0.00. Model probabilities Fable 5.1 0.02, Opus 5.5 0.98, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.97). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.001, Fable 5.1 at high 0.013, Fable 5.1 at extra high 0.006, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.029, Opus 5.5 at high 0.627, Opus 5.5 at extra high 0.304, Opus 5.5 at max 0.020, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-10-26T15:32:31Z. Nathan picks the cell.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** none before it runs. The exact-head review's correction classes and dispositions set this re-review's content. The prompt authorizes no credential use and no live provider action. This session is the only security reading of M04-C1 (OD-41).
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Codex's review of the commit that holds this prompt, and with it M04-C1's code, completes before it goes to Nathan.
- **Deletion condition:** prune after M04's PR merges and the evidence record holds this re-review.

**Manager:** before giving this prompt to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **re-review session for M04-C1**, the correction pass on M04 (branch hygiene) in the Glow dating app, repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one exact code head, for code and for security. This prompt is revision 1, from commit `<RECORDS_COMMIT>`.

**What came before.**
- **M04** (code head `27ef2f6`) adds `.github/workflows/branch-cleanup.yml` and `scripts/branch_cleanup.py`, which delete remote branches fully merged into `main`, with the CI hardening. It is PR36, from the manager branch `claude/magical-wozniak-yfmmx2` into `main` (base `85bbd4d`).
- **Its exact-head review** (prompt revision 1 at `55fc64a`) approved the script's behaviour and asked for changes for two guards that no test failed without, in the correction class "a guard of D3, D6 or D7 that no test fails without":
  - **F1 (V1):** the empty `credential.helper=` reset in `NETWORK` (`branch_cleanup.py:38`);
  - **F2:** the redirect refusal, `_NoRedirect` in `_open()` (`:89-95`).

  It also found two record sentences that claimed more than the code (F3, the restore record; F5, a moved `main`), carried F4 and F6 as follow-ups and V5 as a recorded race. The evidence record's "Exact-head review of M04" holds it.
- **M04-C1** (branch `claude/blissful-volta-coypr6`, code head `0274096`, records `ab38a80`) added two tests to `scripts/test_branch_cleanup.py` and corrected the sentences. Its run of record is push run 40347076599 on `0274096`: all eight jobs passed, `Application checks passed`, the cleanup suite `Ran 18 tests`. The manager verified it ("Manager verification of M04-C1") and fast-forwarded the manager branch to `ab38a80`.

- **The code head under review is `0274096`.** You work at `<RECORDS_COMMIT>`, whose non-Markdown paths are byte-identical to `0274096` (the start gate checks this).
- **Your scope:**
  - **the code delta:** `git diff 27ef2f6 0274096`, which changes `scripts/test_branch_cleanup.py` only: three imports and two tests, `test_helpers_configured_earlier_never_see_the_token` and `test_redirected_listing_is_refused`. Read the whole test file at HEAD, with `scripts/branch_cleanup.py` for what the tests exercise;
  - **the records delta:** the CI policy's bullet "**The summary is the restore record.**" (F3); the evidence record's two corrected sentences (section 3's "**No fetch in the script.**" and section 7's moved-`main` race, F5); its sections "Correction pass M04-C1" and "Manager verification of M04-C1";
  - **the run of record** 40347076599, and the PR run on this head (event `pull_request`) once it has finished.
- **Out of scope:** the script and workflows themselves, which the exact-head review approved and which are unchanged. A finding there that this pass did not introduce is reported as such, not as a defect of the pass.
- **The review is offline:** the code, the offline tests and the runs' logs. You call no provider and need no database.

**The security focus:**
- each new test fails when its guard is removed, and cannot pass for another reason (a recorder that never runs; a refusal from a connection error, not the redirect);
- the tests stay on loopback: no request leaves `127.0.0.1`, whatever proxy variables the process has, and no server, thread or file outlives the test;
- no real credential is used; the fake `TOKEN` is the only token, and where it lands (the F1 control's log) is inside the test's temporary directory;
- F1's test exercises the real `NETWORK` and `CREDENTIAL_HELPER`, and F2's the real `_open()` and `read_open_prs()`, not copies.

**What comes after this re-review: the correction classes.** Report every finding with its severity. A further correction pass takes every blocking finding, and any should-fix finding that could do any of these:
- let a new test pass where it should fail, including with its guard removed or for a reason other than the guard;
- let a test reach a host other than `127.0.0.1`, use a real credential, or leave a server, thread or file outside the test's temporary directory;
- change `scripts/branch_cleanup.py`, either workflow, `scripts/change_scope.py` or its tests, an existing test, or any path outside the pass's three;
- make a record claim more than the code, the tests or the runs show;
- leave F1, F2, F3 or F5 unmet, or a condition of DM-32 (1.1 to 1.16) unmet at this head.

Everything else goes into the records. For each finding, say whether it falls in one of these classes.

**How you work:**
- Nathan started you manually and will relay your report to the manager (App Manager 8). You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - **Reversals and scratch work go in a copy outside the repository, never the checkout** (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
- **The cleanup script deletes branches.** Run it only through its tests. Never run it with `GITHUB_TOKEN` or `GH_TOKEN` in its environment.
- **Never:**
  - dump the environment, or print a credential, token or password;
  - call Stream or any other provider;
  - connect to any database, HDE, Railway or any other external service;
  - run `playwright install`, `eas` or `migrate`.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If one is present, stop and report: this session must start in `Glow App - No Stream`.
3. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`; the environment inventory). Never read them; every command below runs without them.
4. **The toolchain.** Python 3.12.14 in `$HOME/.local/bin`, first on PATH in every process; record `python3.12 --version`.
5. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <RECORDS_COMMIT>
git rev-parse HEAD                      # must print <RECORDS_COMMIT>
git merge-base --all origin/main HEAD   # expected: one line, 85bbd4d000f97f6a857dc0f5519a8a3501dc40d3
git merge-base --is-ancestor <RECORDS_COMMIT> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 0274096348dc54df8ad7605aa6f1eecf706954ca HEAD -- .github scripts services apps packages proofs && echo "the code head under review"
git diff --quiet 0274096348dc54df8ad7605aa6f1eecf706954ca origin/claude/magical-wozniak-yfmmx2 -- .github scripts services apps packages proofs && echo "no code on the live branch after 0274096"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-26-m04-branch-hygiene.md | grep -c -E '^#+ Re-review of M04-C1'   # must print 0
git diff --shortstat 27ef2f6fdc65f4f1d684c66ae69ff0e601f4f427 0274096348dc54df8ad7605aa6f1eecf706954ca -- .github scripts services apps packages proofs   # expected: 1 file changed, 68 insertions(+)
git diff --shortstat origin/main...HEAD -- .github scripts services apps packages proofs   # expected: 6 files changed, 864 insertions(+), 13 deletions(-)
```

If any check fails, stop and report. The prompt is stale if this prompt's commit is not on the live branch, if a non-Markdown path changed there after `0274096`, or if this re-review is already recorded (AM5-15).

**Classify the change** as root `AGENTS.md` requires, with the trusted base policy outside the candidate tree and full SHAs, from the repository root:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
```

- **Expected:** `"full": true`. Anything else: stop and report it.

**Then read, completely, at `HEAD`:**

- root `AGENTS.md` and `CLAUDE.md`;
- the evidence record, `docs/testing/evidence/2026-10-26-m04-branch-hygiene.md`: "Exact-head review of M04", "Correction pass M04-C1", "Manager verification of M04-C1", and sections 3 and 7 for F5's two sentences;
- the correction prompt, `docs/ephemeral/2026-10-26-m04-c1-correction-prompt.md`;
- the CI policy's "Branch cleanup (M04)" section;
- `scripts/test_branch_cleanup.py` and `scripts/branch_cleanup.py`, whole.

**The runs' logs,** with your GitHub tools: run 40347076599 (every job's conclusion, the gate's line, the API job's two policy suites with their counts and the two new tests' lines); and the PR run on `<RECORDS_COMMIT>`, if it has finished (every job, the gate's line). Say what you read.

## 3. What to review

1. **F1's test** (`test_helpers_configured_earlier_never_see_the_token`): does it configure a generic and a URL-scoped helper that git would really consult for `https://github.com`; run `fill` and `approve` through the real `NETWORK`; and fail if either helper is asked to `get` or `store`? Does its control, without the reset, really show both helpers asked, so the test cannot pass because the recorder never runs? Is the recorder's `shlex`-quoted path and its log safe for any temporary-directory name?
2. **F2's test** (`test_redirected_listing_is_refused`): does the 302 reach the real `_open()` through the real `read_open_prs()`; does `served == ["/repos/owner/repo/pulls"]` prove the request reached the server and the redirect was not followed; does the proxy handling keep the request on loopback for every proxy variable, in either case; and are the server, its thread and the patched environment all restored, whatever the test's outcome?
3. **F3 and F5:** does the CI policy's bullet now say what `:269-276` does, and do the evidence record's two sentences now say what `resolve_main()` (`:164-166`) does? Is anything else in either file changed?
4. **Scope:** only `scripts/test_branch_cleanup.py` changed in code, the 16 existing tests unchanged, and no other path but the CI policy's one bullet and the evidence record.
5. **The reversals:** reproduce, in scratch copies, F1's (`"-c", "credential.helper=",` dropped from `NETWORK`) and F2's (`build_opener()` in place of `build_opener(_NoRedirect)`). Each should fail its own new test and only it. Add any reversal of your own that the security focus calls for, for example a recorder that never runs, or a server that is never reached.
6. **The records:** the evidence record's "Correction pass M04-C1" and "Manager verification of M04-C1". Does any statement claim more than the code, the tests or the runs show?
7. **The offline checks,** run at `HEAD` in a clean environment: `python3.12 -I -m unittest discover -s scripts -p 'test_branch_cleanup.py' -v` (18) and the same for `test_change_scope.py` (14); `python3.12 -I -m py_compile scripts/test_branch_cleanup.py`; `git diff --check origin/main...HEAD`.

## 4. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<RECORDS_COMMIT>`), and the start gate's and the classification's results;
- the environment check;
- a verdict: **approve**, or **changes required**, with the findings that require them, and whether F1, F2, F3 and F5 are closed;
- every finding, numbered, with its severity (blocking, should fix, nit), its file and line, what is wrong, why it matters, a suggested fix, and whether it falls in one of the correction classes above;
- for each focus area, what you checked and what you found;
- the offline checks, reversals and runs you read, with their exact results;
- limits of the review, and open questions.

# M04-C1 correction prompt — two tests for untested guards, and three exact sentences

- **Owner:** App Manager 8. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 26 October 2026.**
- **Durable brief:** [M04 — Branch hygiene](../planning/m04-branch-hygiene.md), revision 3; its "Sessions" line for the exact-head review.
- **Where the result goes:**
  - the session's tests and record text, and the section "Correction pass M04-C1" in the [M04 evidence record](../testing/evidence/2026-10-26-m04-branch-hygiene.md);
  - the run of record: the Foundation run on its code commit.

  The manager adds its verification and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 1.68 (confidence 0.73); rung probabilities low 0.01, medium 0.34, high 0.61, extra high 0.04, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.99, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.99). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.010, Opus 5.5 at medium 0.337, Opus 5.5 at high 0.604, Opus 5.5 at extra high 0.040, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.003, Sonnet 5.5 at high 0.006, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-10-26T12:13:22Z. Nathan picks the cell.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** none before it runs. The pass fixes the exact-head review's F1 and F2, which fall in a correction class its prompt named, by tests alone, and makes three sentences exact (F3, F5); no design or condition changes (manager workflow, step 6). F3's wording reaches the Dev Manager's pre-merge read with the CI policy. The prompt authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Codex's review of the commit that holds this prompt completes before it goes to Nathan; an exact-head re-review of this pass's delta follows it.
- **Deletion condition:** prune after M04's PR merges and the evidence record holds this pass and its re-review.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **correction session M04-C1** for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.** M04 adds `.github/workflows/branch-cleanup.yml` and `scripts/branch_cleanup.py`, which delete remote branches fully merged into `main`, with 16 tests in `scripts/test_branch_cleanup.py`. It is integrated on the manager branch (code head `27ef2f6`) and open as PR36. Its exact-head review asked for changes, for two guards that no test fails without; it found no blocking finding, and the script's behaviour is approved as it is. The review is summarized in the evidence record's "Exact-head review of M04".

**Your four items:**

1. **F1 (V1): a test for the credential-helper reset.** `NETWORK` (`branch_cleanup.py:38`) passes `-c credential.helper=` before the script's own helper. That empty value clears every helper configured earlier, so none of them is asked to `get` or `store` the token. Dropping it passes all 16 tests today. Add a test that fails without it:
   - in the test's environment, `GIT_CONFIG_GLOBAL` names a temporary config file that sets a generic `credential.helper` and a URL-scoped `credential.https://github.com.helper`, both a recording helper that writes its arguments and its input to a temporary file;
   - run `git <NETWORK> credential fill` for `protocol=https` and `host=github.com`, with the test's fake `TOKEN` as `GITHUB_TOKEN` and `GIT_TERMINAL_PROMPT=0`; then `git <NETWORK> credential approve` with what `fill` printed;
   - **expected:** `fill` prints the token as the password, and the recording helper was never run;
   - **a built-in control:** the same two commands, with the script's helper but without the reset, do run the recording helper, so the test cannot pass because the recorder never works.
2. **F2: a test for the redirect refusal.** `_open()` (`:94-95`) opens with `_NoRedirect` (`:89-91`), so a redirected listing refuses. Dropping it passes all 16 tests today; without it, urllib follows a 302, drops the `Authorization` header, and accepts the new location's listing. Add a test that fails without it:
   - a loopback `http.server` on `127.0.0.1`, port 0, in a thread, answers the pulls path with a 302 to a second path on the same server, which would answer 200 with `[]` and no `Link` header;
   - patch `branch_cleanup.API` to the server's `http://127.0.0.1:<port>`, and call `read_open_prs("owner/repo", TOKEN, urlopen=branch_cleanup._open)`;
   - **expected:** `Refused`, and the server never served the second path;
   - keep the request local whatever proxy variables the process has: for example, within the test set `NO_PROXY` to `127.0.0.1` and clear `HTTP_PROXY`, `HTTPS_PROXY` and their lower-case forms. Shut the server down in the test's clean-up.
3. **F3: the restore record's sentence, made exact.** Each row is written when its push has returned (`:274-276`), so a run killed while a push is in flight may leave that one deletion unrecorded; its commits are in `main`. In the CI policy, `docs/operations/ci-and-branch-policy.md`, the bullet "**The summary is the restore record.**" (line 63) says a run that fails midway still names every head it deleted. Make it say: each deletion's row is written as soon as its push returns, so a run whose script fails midway still names every head it deleted; a run killed while a push is in flight may leave that one deletion unrecorded, and its commits are in `main`. Keep the rest of the bullet and the file byte-identical.
4. **F5: two sentences of the evidence record, made exact.** `resolve_main()` (`:164-166`) refuses only when `main`'s head, as `ls-remote` read it, is not a commit in the checkout. A `main` that moved after checkout to a commit the checkout already holds is decided against the new head, which is correct. Correct section 3's "**No fetch in the script.**" bullet (line 38: "if `main` moved there, the run refuses") and section 7's race bullet (line 128: "`main` moved after checkout: the run refuses") to say so. Mark each with `[Corrected in M04-C1: the exact-head review's F5]`.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 8. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only your owned paths: `scripts/test_branch_cleanup.py`; the CI policy's one bullet (item 3); the evidence record's two sentences (item 4) and a new section at its end, "Correction pass M04-C1";
  - **change nothing else:** not `scripts/branch_cleanup.py`, either workflow, `scripts/change_scope.py` or its tests, any dependency or lock file. If a test cannot be written without changing the script, stop and report why;
  - change no existing test: the 16 pass unchanged;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete any branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch, ruleset or setting. Change nothing in Notion.
- **Push once for code, then wait** (manager workflow, step 3). Push the tests as one commit and wait until that commit's Foundation run has finished before pushing anything else: a newer push of the same branch cancels the earlier run's application jobs and fails its gate. Then push the records.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, token or password, in any form. The tests use the existing fake `TOKEN`;
  - call Stream or any other provider; the F2 test's server listens on `127.0.0.1` only, and no test reaches any other host;
  - connect to any database, HDE, Railway or other external service;
  - run `playwright install`, `eas` or `migrate`;
  - run the cleanup script outside its tests.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If any is present, stop and report: this session must start in `Glow App - No Stream`.
3. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`; the environment inventory). Never read them; every repository command runs without them.
4. **The toolchain:** Python 3.12.14 in `$HOME/.local/bin`, first on PATH in every process; record `python3.12 --version`.
5. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # before any work: your branch starts at this prompt's commit
git rev-parse HEAD                       # must print <START_SHA>
git merge-base --is-ancestor <START_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 27ef2f6fdc65f4f1d684c66ae69ff0e601f4f427 HEAD -- .github scripts services apps packages proofs && echo "M04's code head"
git diff --stat <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- .github scripts services apps packages proofs   # must print nothing
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-26-m04-branch-hygiene.md | grep -c -E '^#+ Correction pass M04-C1'   # must print 0
```

If any check fails, stop and report. The prompt is stale if code changed on the live branch after this prompt's commit, or if this pass is already recorded (AM5-15).

Then read, completely: root `AGENTS.md` and `CLAUDE.md`; the evidence record, whole, with "Exact-head review of M04"; `scripts/branch_cleanup.py` and `scripts/test_branch_cleanup.py`, whole; the CI policy's "Branch cleanup (M04)" section.

## 3. Checks

Report the exact commands and results.

1. **The diff:** `git diff --check <START_SHA> HEAD`, and `git diff --name-only <START_SHA> HEAD`: only the three owned paths.
2. **Classification** with the trusted policy from `main`, outside the tree. Expected: full scope.

   ```bash
   base=$(git rev-parse origin/main); policy_dir=$(mktemp -d)
   git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
   python3 -I "$policy_dir/change_scope.py" --base <START_SHA> --head "$(git rev-parse HEAD)" --merge-base
   ```

3. **The tests,** from the repository root, at the start and at your head: `python3.12 -I -m unittest discover -s scripts -p 'test_branch_cleanup.py' -v` (16 at the start; 16 plus yours at the head) and the same for `test_change_scope.py` (14, unchanged).
4. **The reversals,** each in a scratch copy outside the checkout, with the test's output:
   - F1's: `"-c", "credential.helper=",` dropped from `NETWORK`. Your F1 test fails, and the 16 still pass;
   - F2's: `build_opener(_NoRedirect)` replaced by `build_opener()` in `_open()`. Your F2 test fails, and the 16 still pass;
   - each new test passes with the real code.
5. **The Foundation run on your code commit:** its run ID, each of the eight jobs' conclusions, the gate's line (`Application checks passed`), and the API job's `test_branch_cleanup.py` line with its count. If your branch has no run, say so; re-run or dispatch nothing.
6. **A secret scan over your whole diff:** no secret, token, API key, password or email address beyond the existing fake `TOKEN`.

## 4. The record

Add "Correction pass M04-C1" at the end of the evidence record, in the per-pass template: identity (prompt revision and commit, branch, commits, run of record, environment check, start gate), the four items with where each is, the checks of section 3 as a table, deviations and limits, and what the re-review must know.

## 5. Report

Your final message is the report Nathan relays:

- the prompt revision you received, and the commit it came from;
- the environment check and the start gate;
- your branch, head SHA, code commit and the changed paths;
- for items 1 to 4: done or left, with where;
- every check, with its exact results, the reversals and the run of record's details;
- deviations, departures you stopped at, findings outside the work, open questions and limits.

# M04 implementation prompt — branch hygiene: the cleanup workflow, with the CI hardening

- **Owner:** App Manager 8. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 26 October 2026.**
- **Durable brief:** [M04 — Branch hygiene](../planning/m04-branch-hygiene.md), revision 3, which applies the Dev Manager's DM-32 conditions 1.1 to 1.16 and Nathan's OD-51.
- **Where the result goes:**
  - the session's code, tests and CI policy text, and its evidence record `docs/testing/evidence/2026-10-26-m04-branch-hygiene.md`;
  - the run of record: the Foundation run on its last code commit.

  The manager adds its verification and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 3.19 (confidence 0.59); rung probabilities low 0.00, medium 0.01, high 0.19, extra high 0.40, max 0.39, ultracode 0.01. Model probabilities Fable 5.1 0.11, Opus 5.5 0.87, Sonnet 5.5 0.02, Haiku 5.5 0.00 (confidence 0.83). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.001, Fable 5.1 at high 0.021, Fable 5.1 at extra high 0.044, Fable 5.1 at max 0.043, Fable 5.1 at ultracode 0.001, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.009, Opus 5.5 at high 0.165, Opus 5.5 at extra high 0.348, Opus 5.5 at max 0.339, Opus 5.5 at ultracode 0.009, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.004, Sonnet 5.5 at extra high 0.008, Sonnet 5.5 at max 0.008, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Flags: boundary between max and extra high. Sent 2026-10-26T04:01:29Z. Nathan picks the cell.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** none before it runs. DM-32 read the brief and its conditions are applied as written (DM-03 G2). This prompt authorizes no credential use and no live provider action: the session's GitHub access is read-only for this work, and its only writes are its own branch. Its CI policy text reaches the Dev Manager before the PR merges.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Codex's review of its code head follows, then an exact-head code and security review with a written threat model.
- **Deletion condition:** prune after M04's PR merges and its merge receipt records the first cleanup run.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **implementation session M04** for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What M04 is.** Nathan, 5 October 2026 (OD-39): a small GitHub workflow that runs when a PR merges into `main`, and on demand. It deletes every branch whose commits are all in `main`, except `main`, the manager branch and the Dev Manager's branch, and never a branch with unmerged work. With it come four CI fixes from the whole-project review M05 (findings 10, 11, 12 and 14) that change the same files. The design is fixed in the brief's D1 to D9, which the Dev Manager approved with conditions (DM-32). Build it as written there; this prompt does not restate every condition.

**The repository is public for now** (OD-51): Nathan keeps it public for budget reasons and intends to make it private again. While it is public, anyone can read what you push, which is one more reason for the rules below.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 8. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only your owned paths (section 5);
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete any branch, yours included;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch, ruleset or setting. Change nothing in Notion.
- **The push filter.** Today the Foundation workflow runs on a push only for `main`, `app-builder-1/**`, `app-planner-1/**` and `claude/**`. Your change adds `'ccr-**'`. GitHub reads a push's workflow from the pushed commit, so once that commit is on your branch your pushes should start runs. Check whether they do, and say so. If your branch has no runs, say so; the manager then takes the run of record from the PR run on the head that integrates your code, and runs the cancel test itself (DM-32 1.15).
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, token or password, in any form;
  - call Stream or any other provider, or run any command in `proofs/stream-chat/` that sends a request;
  - connect to any database, HDE, Railway or other external service. Network use is limited to the package installs from the locks, `git ls-remote` and shallow clones of GitHub's own actions, and your GitHub tools' reads;
  - run `playwright install`, `eas` or `migrate`;
  - add or change a dependency, a version or a lock file, in any component;
  - add a `pull_request_target` trigger, or any trigger but the brief's to the cleanup workflow;
  - run the cleanup script in a mode that deletes, against any remote but a temporary one your tests create.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If any is present, stop and report: this session must start in `Glow App - No Stream`.
3. **The toolchain:** the pinned toolchain is in `$HOME/.local/bin`: Python 3.12.14, Node 24.19.0 and npm 11.9.0. Put `$HOME/.local/bin` first on PATH in every process you run, and record `python3.12 --version`.
4. **A clean process environment** for each component's commands, as `docs/operations/local-development.md` shows: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables. Installs get the proxy and CA variables by reference, never printed.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # before any work: your branch starts at this prompt's commit
git rev-parse HEAD                       # must print <START_SHA>
git merge-base --is-ancestor 4aa66e2336d1a040bfd1b0ec5ea4cdf79209a2f6 HEAD && echo "PR34 present"   # must print "PR34 present"
git diff --name-only 4aa66e2336d1a040bfd1b0ec5ea4cdf79209a2f6 origin/main | grep -v -E '\.md$'   # must print nothing
git diff --name-only 4aa66e2336d1a040bfd1b0ec5ea4cdf79209a2f6 HEAD | grep -v -E '\.md$'          # must print nothing
git diff --stat <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- .github scripts services apps packages proofs   # must print nothing
git ls-tree --name-only origin/claude/magical-wozniak-yfmmx2 -- docs/testing/evidence/2026-10-26-m04-branch-hygiene.md   # must print nothing
```

- `main` may have moved by Markdown only: the manager's records since PR34 merge as their own docs-only PR.
- If code or this record has already landed on the live manager branch, this prompt is stale: stop and report (AM5-15).
- If any check fails, stop and report.

Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`;
- M04's brief, `docs/planning/m04-branch-hygiene.md`, revision 3;
- the DM-32 report, `docs/continuity/dev-manager/reviews/2026-10-26-dm-32-m04-brief.md`, whole: its conditions 1.1 to 1.16 are the brief's;
- the M05 record, `docs/testing/evidence/2026-10-25-m05-project-review.md`: findings 10 to 14, and P-7 and P-9 in section 8;
- `.github/workflows/foundation.yml`, `scripts/change_scope.py`, `scripts/test_change_scope.py`, and `docs/operations/ci-and-branch-policy.md`;
- the manager workflow, `docs/planning/manager-workflow.md`, steps 3, 5 and 7, for context only: its texts are the manager's.

## 3. The work

1. **The cleanup workflow,** `.github/workflows/branch-cleanup.yml` (D1, D2, D3, D7, D8):
   - triggers: `push` to `main`, and `workflow_dispatch` with one `boolean` input, `dry_run`, default `true`;
   - the job runs only when `github.ref` is `refs/heads/main`;
   - `permissions: {}` at the top; the job gets `contents: write` and `pull-requests: read`, and a bounded `timeout-minutes`;
   - checkout pinned to the CI policy's commit, with `persist-credentials: false` and the full history the ancestry checks need;
   - a concurrency group with `cancel-in-progress: false`;
   - one step runs the script. Only that step's `env:` holds the token, as `${{ github.token }}` (no `secrets.` reference), with the event name and the input. No `${{ }}` expression appears inside any `run:`.
2. **The script,** `scripts/branch_cleanup.py`: standard library only, Python 3.12, no network but the GitHub API's PR listing and `git`.
   - **The mode** (D8; DM-32 1.7): a push deletes. A dispatch deletes only when the input is exactly `false`; any other value is a dry run.
   - **The selection** (D4, D5): the remote's `refs/heads/*` from `git ls-remote`; `main`'s current head; and every open PR's head and base, read from `GET /repos/{owner}/{repo}/pulls?state=open` page by page until the last page. A branch is deleted only if its head is an ancestor of `main`, it is not on the keep-list (`main`, `claude/magical-wozniak-yfmmx2` and `claude/dev-manager`, by name), and no open PR has it as head or base. A head that cannot be resolved is kept.
   - **Fail closed** (D7; DM-32 1.3): if the listing, the remote read or `main`'s resolution fails at any point, the script deletes nothing and exits non-zero.
   - **The deletion** (D6): each one is conditional on the checked head: `git push --force-with-lease=refs/heads/<b>:<sha> origin :refs/heads/<b>`, or an equivalent precondition. A refused lease keeps the branch, is reported, and is not an error that stops the others.
   - **The token** (D3; DM-32 1.1): git receives it through the environment only, for example a `credential.helper` given with `-c` that reads it from the environment. It never appears in a command's arguments, a file, git config or any output.
   - **Names are data** (D4): every branch name is passed as an argument list element, never through a shell.
   - **The summary** (D6, D8; DM-32 1.3 and 1.5): appended to `$GITHUB_STEP_SUMMARY` as the run goes. First the open PRs it read (number, head, base); then one row per branch (name, head, decision and reason), each deletion's row written as soon as that deletion happens. Names are escaped for the table.
   - **The pre-merge dry run's input:** an option that reads the open PRs from a JSON file instead of the API, accepted only in dry-run mode, so that you can run it with your GitHub tools' listing. The workflow never passes it.
3. **The selection tests,** `scripts/test_branch_cleanup.py`, on temporary repositories with a bare remote, as `test_change_scope.py` builds its histories. Cover every case in the brief's acceptance check 2, with a fake PR listing for the two-page and failure cases. For each, record a reversal: the smallest change to the script that makes the test fail, and the test's output with it.
4. **The Foundation changes,** `.github/workflows/foundation.yml` (D9):
   - `!cancelled() && (…)` in place of `always() && (…)` on the six application jobs; the gate keeps `always()`;
   - the Mobile job's `timeout-minutes`: 25, unless your measurements argue for another value, which you state;
   - `actions/upload-artifact` at its current release: resolve the tag's commit with `git ls-remote https://github.com/actions/upload-artifact`, read that commit's `action.yml` in a shallow scratch clone for the inputs both uploads use (`name`, `path`, `include-hidden-files`, `if-no-files-found`, `retention-days`), and record the release and commit;
   - the API job's candidate-policy step also runs `scripts/test_branch_cleanup.py`;
   - the push filter adds `'ccr-**'`.
5. **The classifier** (finding 12): `scripts/change_scope.py`'s `git diff` call adds `--ignore-submodules=none`. Add a test to `scripts/test_change_scope.py`: a base whose `.gitmodules` sets `ignore = all` for a submodule, and a head that moves its gitlink and edits a Markdown file, classifies full scope. Record the reversal (the flag removed) failing it.
6. **The CI policy,** `docs/operations/ci-and-branch-policy.md`: the changes in the brief's "Owned paths", "The CI policy's changes", each against your own evidence:
   - the cleanup workflow and its write permission, the one exception to read-only contents;
   - the trust limit (DM-32 1.2);
   - the fresh-branch case (DM-32 1.4) and the concurrency wording (DM-32 1.6);
   - the cancel paragraph and the upload-artifact row in final form, saying what D9 makes true (DM-32 1.13);
   - the push filter, and that `'ccr-**'` comes out, or its minutes are approved, when the repository goes private again (OD-51; DM-32 3.4);
   - the public repository (OD-51): public for now, for budget reasons, and Nathan intends to make it private again; while it is public, branch protection and rulesets are available at no cost, none is configured, and the procedural substitutes stay until Nathan decides, and after it is private again.

   Keep the rest byte-identical.
7. **The cancel test** (DM-32 1.15), on your branch if its pushes start runs: before your final code push, push two commits less than a minute apart. Record both runs: the earlier run's application jobs `cancelled` and its gate failed, the newer run as the result. Then make your final code push and wait for its run before pushing anything else (step 3's rule; AM5-14).
8. **The pre-merge dry run** (acceptance check 4), at your head: fetch every remote branch, list the open PRs with your GitHub tools into a JSON file, and run the script in dry-run mode against `origin`. Record each branch with its decision. It deletes nothing.

## 4. Checks

Report the exact commands and results.

1. **The diff:** `git diff --check <START_SHA> HEAD`, and `git diff --name-only <START_SHA> HEAD`. Only owned paths changed.
2. **Classification** with the trusted policy from `main`, run outside the tree, as root `AGENTS.md` requires. Expected: full scope. Pass full SHAs.

   ```bash
   base=$(git rev-parse origin/main); policy_dir=$(mktemp -d)
   git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
   python3 -I "$policy_dir/change_scope.py" --base <START_SHA> --head "$(git rev-parse HEAD)" --merge-base
   ```

3. **The script tests,** from the repository root: `python3.12 -I -m unittest discover -s scripts -p 'test_change_scope.py' -v` and the same for `test_branch_cleanup.py`, with counts at the start and at your head.
4. **The workflows' text:** show, with `grep` or a short Python read, each point of the brief's acceptance check 1 in `branch-cleanup.yml`, and the D9 lines in `foundation.yml`. Show that `secrets.` does not appear in `branch-cleanup.yml`, and that no `run:` block in it contains `${{`.
5. **The reversals** of section 3 items 3 and 5, each with the test's output.
6. **The Foundation run on your last code commit,** if your branch has runs:
   - its run ID, each job's conclusion (eight jobs), and the gate's log line, which must be `Application checks passed`;
   - the Mobile job's time against its timeout;
   - the run's artifacts: `p04-empty-form-layout` and `p06-db-proof-results`, with names, sizes and retention (DM-32 1.9);
   - if your tools cannot read the run, say so; re-run or dispatch nothing.
7. **A secret scan over your whole diff:** no secret, token, API key, password or email address.

## 5. Owned paths, push and records

- **You may create:** `.github/workflows/branch-cleanup.yml`, `scripts/branch_cleanup.py` and `scripts/test_branch_cleanup.py`.
- **You may change:** `.github/workflows/foundation.yml`, `scripts/change_scope.py`, `scripts/test_change_scope.py` and `docs/operations/ci-and-branch-policy.md`.
- **Your evidence record:** `docs/testing/evidence/2026-10-26-m04-branch-hygiene.md`.
- **Nothing else.** That includes `AGENTS.md`, `CLAUDE.md`, the manager workflow, the briefs, the handoff, every other document, any `.claude/` path, and every component's code and locks. Report any other change you think is needed.
- **Commit and push** your session branch. Don't open a pull request.
- **Your evidence record:**
  - the prompt's revision and start SHA, your branch and head, and the run of record;
  - for items 1 to 8 of section 3: done (`file:line` and its test) or left (the reason);
  - the choices you made where the brief leaves one (the timeout, the token's route into git, the keep-list's location, the summary's format), and why;
  - the dry run's table;
  - every check, with its exact results;
  - deviations and limits;
  - **what the exact-head review must know,** for its written threat model (DM-32 1.16): where the token can reach; what a branch's own copy of either workflow could do; every place a name or an input enters a command; how the listing's completeness is ensured; and the races between selection and deletion.

## 6. Report

Your final message is the report Nathan relays:

- the prompt revision you received, and the commit it came from;
- the environment check and the start gate;
- your branch, head SHA and the changed paths;
- for items 1 to 8 of section 3: done or left, with the recorded choices;
- every check, with its exact results, the run of record's details and the cancel test's two runs;
- the dry run's expected deletions;
- deviations, departures you stopped at, findings outside the work, open questions and limits.

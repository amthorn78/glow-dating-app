# M04 review prompt — the exact-head code and security review of branch hygiene

- **Owner:** App Manager 8. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 26 October 2026.**
- **Durable brief:** [M04 — Branch hygiene](../planning/m04-branch-hygiene.md), revision 3, with the Dev Manager's DM-32 conditions 1.1 to 1.16.
- **Where the result goes:**
  - The reviewer reports to Nathan.
  - The manager records the review and its disposition in the [M04 evidence record](../testing/evidence/2026-10-26-m04-branch-hygiene.md), "Exact-head review of M04", and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Fable 5.1 at max.** Effort score 3.66 (confidence 0.78); rung probabilities low 0.00, medium 0.00, high 0.04, extra high 0.25, max 0.71, ultracode 0.00. Model probabilities Fable 5.1 0.56, Opus 5.5 0.44, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.41). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.022, Fable 5.1 at extra high 0.140, Fable 5.1 at max 0.398, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.000, Opus 5.5 at high 0.018, Opus 5.5 at extra high 0.110, Opus 5.5 at max 0.312, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Flags: model near tie between Fable 5.1 and Opus 5.5. Sent 2026-10-26T11:26:17Z. Nathan picks the cell.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** none before it runs. DM-32 set this review's content (1.16; the brief's "Review plan", item 4). The prompt authorizes no credential use and no live provider action. This session is the only security reading of M04 (OD-41).
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Codex's code review of the commit that holds this prompt, and with it M04's code, completes before this prompt goes to Nathan, and each finding is handled first (manager workflow, step 6).
- **Deletion condition:** prune after M04's PR merges and the evidence record holds this review.

**Manager:** before giving this prompt to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **review session for M04**, branch hygiene, in the Glow dating app, repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one exact code head, for code and for security. This prompt is revision 1, from commit `<RECORDS_COMMIT>`.

**What M04 is.** Nathan, 5 October 2026 (OD-39): a workflow that deletes every remote branch whose commits are all in `main`, except `main`, the manager branch and the Dev Manager's branch, and never a branch with unmerged work. With it come four CI fixes from the whole-project review M05 (findings 10, 11, 12 and 14). The design is the brief's D1 to D9, approved with DM-32's conditions 1.1 to 1.16.

**What came before.**
- **The implementation session** (branch `claude/laughing-meitner-ywjnk1`, started at `bbd461b`) did all eight items of its prompt. Code head `27ef2f6`; records `7f9e6e7`.
- **Its run of record** is push run 40270021713 on `27ef2f6`: all eight jobs passed and the gate printed `Application checks passed`. Its cancel test is runs 40269750327 (`2d3566d`) and 40269779556 (`6199f2c`).
- **The manager** verified the report against the branch (the record, "Manager verification of M04"), and integrated it at `39b6141` after PR35 merged as `85bbd4d`. Its own reversals found **V1**: dropping the empty `credential.helper=` reset passes every test.
- **This PR** is M04's, from the manager branch `claude/magical-wozniak-yfmmx2` into `main` (base `85bbd4d`). Its head carries the manager's records too: Markdown only, in the CI policy's opening line, the manager workflow, the start prompts, the environment inventory, the review log, the mistakes log, the handoff, the brief and the two evidence records.

- **The code head under review is `27ef2f6`.** You work at `<RECORDS_COMMIT>`, whose non-Markdown paths are byte-identical to `27ef2f6` (the start gate checks this).
- **Your scope:**
  - **the code:** `git diff origin/main...HEAD` over every non-Markdown path, read whole (six files: `.github/workflows/branch-cleanup.yml`, `.github/workflows/foundation.yml`, `scripts/branch_cleanup.py`, `scripts/test_branch_cleanup.py`, `scripts/change_scope.py`, `scripts/test_change_scope.py`), against D1 to D9 and DM-32 1.1 to 1.9;
  - **the threat model** (DM-32 1.16), written by you, below;
  - **V1 and V5,** named below;
  - **the records,** for their claims: the CI policy's changes, the evidence record whole, and the manager workflow's steps 3, 5 and 7 and handover checklist where they describe the workflows;
  - **the runs:** the run of record, the cancel test, and the PR run on this head (event `pull_request`) once it has finished.
- **The review is offline:** the code, the offline tests and the runs' logs. You call no provider and need no database.

**The security focus** (the brief's "Review plan", item 4; Codex's security reviews are no longer available, OD-41):
- the selection rule (D4, D5);
- the triggers and permissions, and where the token reaches (D1 to D3, D8);
- the lease and the summary as the restore record (D6);
- injection through branch names, PR fields and the dispatch input;
- fail closed (D7);
- the classifier change (finding 12).

**What comes after this review: the correction classes.** Report every finding with its severity. A correction pass takes every blocking finding, and any should-fix finding that could do any of these:
- delete a branch that is on the keep-list, is an open PR's head or base, holds a commit not in `main`, or moved after it was checked;
- delete anything on a dry run, on a dispatch whose `dry_run` is not exactly `false`, or after a read that failed or is incomplete;
- let the token reach an argument, a file, git config, a log line, a step other than the script's, a credential helper other than the script's, or a local git command;
- let a branch name, a PR field or an input reach a shell, an option position or a workflow command, or break the summary's table;
- start a deletion before the previous deletion's row is written;
- add a trigger, a permission, a secret, an action or an unpinned action beyond the brief's;
- let a superseded run's gate pass, or a gate pass without six passing or six exempt jobs; or change the classifier's result for any change but one a submodule setting hid;
- let a test pass where it should fail, including a guard of D3, D6 or D7 that no test fails without (V1 is named for this class);
- make a record claim more than the code, the tests or the runs show;
- leave a condition of DM-32 (1.1 to 1.16) or an item of the implementation prompt unmet.

A defect that misses an item of the implementation prompt is fixed before the merge (manager workflow, step 6). Everything else goes into the records. For each finding, say whether it falls in one of these classes.

**How you work:**
- Nathan started you manually and will relay your report to the manager (App Manager 8). You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - **Reversals and scratch work go in a copy outside the repository, never the checkout** (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
- **The cleanup script deletes branches.** Run it only through its tests, or, if you choose, in one dry run as section 3 item 9 describes. Never run it with `GITHUB_TOKEN` or `GH_TOKEN` in its environment, never without `--dry-run`, and never against a remote but `origin` or one your scratch copy creates.
- **Never:**
  - dump the environment, or print a credential, token or password;
  - call Stream or any other provider;
  - connect to any database, HDE, Railway or any other external service;
  - run `playwright install`, `eas` or `migrate`.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If one is present, stop and report: this session must start in `Glow App - No Stream`.
3. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`; the environment inventory). Never read them; every command below runs without them.
4. **The toolchain.** The pinned toolchain is in `$HOME/.local/bin`: Python 3.12.14 (and Node 24.19.0, npm 11.9.0). Put `$HOME/.local/bin` first on PATH in every process you run, and record `python3.12 --version`.
5. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <RECORDS_COMMIT>
git rev-parse HEAD                      # must print <RECORDS_COMMIT>
git merge-base --all origin/main HEAD   # expected: one line, 85bbd4d000f97f6a857dc0f5519a8a3501dc40d3
git merge-base --is-ancestor <RECORDS_COMMIT> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 27ef2f6fdc65f4f1d684c66ae69ff0e601f4f427 HEAD -- .github scripts services apps packages proofs && echo "the code head under review"
git diff --quiet 27ef2f6fdc65f4f1d684c66ae69ff0e601f4f427 origin/claude/magical-wozniak-yfmmx2 -- .github scripts services apps packages proofs && echo "no code on the live branch after 27ef2f6"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-26-m04-branch-hygiene.md | grep -c -E '^#+ Exact-head review of M04'   # must print 0
git diff --shortstat bbd461bcad24a22062f5cad4bcbd695ce1826eb0 27ef2f6fdc65f4f1d684c66ae69ff0e601f4f427 -- .github scripts services apps packages proofs   # expected: 6 files changed, 796 insertions(+), 13 deletions(-)
git diff --shortstat origin/main...HEAD -- .github scripts services apps packages proofs   # expected: the same
```

If any check fails, stop and report. The prompt is stale if this prompt's commit is not on the live branch, if a non-Markdown path changed there after `27ef2f6`, or if this review is already recorded (AM5-15).

**Classify the change** as root `AGENTS.md` requires, with the trusted base policy outside the candidate tree and full SHAs, from the repository root. The base policy is the one before finding 12's change:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
git diff --name-only origin/main...HEAD | grep -v '\.md$'
```

- **Expected:** `"full": true`, and the last command prints the six code paths above and nothing else. Anything else: stop and report it.

**Then read, completely, at `HEAD`:**

- root `AGENTS.md` and `CLAUDE.md`;
- M04's brief, `docs/planning/m04-branch-hygiene.md`, revision 3;
- the DM-32 report, `docs/continuity/dev-manager/reviews/2026-10-26-dm-32-m04-brief.md`, whole;
- the implementation prompt, `docs/ephemeral/2026-10-26-m04-implementation-prompt.md`;
- the evidence record, `docs/testing/evidence/2026-10-26-m04-branch-hygiene.md`, whole, with "Manager verification of M04";
- the CI policy, `docs/operations/ci-and-branch-policy.md`, whole;
- the M05 record, `docs/testing/evidence/2026-10-25-m05-project-review.md`: findings 10 to 14;
- the manager workflow, `docs/planning/manager-workflow.md`: steps 3, 5 and 7, and the handover checklist;
- **the code, whole at `HEAD`:** the six files above. In `scripts/branch_cleanup.py`: `KEEP` (`:22`), `MAX_PAGES` (`:26`), `NETWORK` (`:38`), `git()` (`:45`), `diagnostic()` (`:54`), `deletes()` (`:62`), `pr_entries()` (`:73`), the redirect handler (`:89`), `read_open_prs()` (`:102`), `read_prs_file()` (`:136`), `read_heads()` (`:144`), `resolve_main()` (`:164`), `merged()` (`:169`), `decide()` (`:175`), `delete_branch()` (`:188`), `cell()` (`:199`), `Summary` (`:206`) and `main()` (`:221`).

**The runs' logs,** with your GitHub tools: run 40270021713 (every job's conclusion, the gate's line, the API job's two policy suites, the Mobile job's time against 25 minutes, the two artifacts and their retention); runs 40269750327 and 40269779556 (the cancel test as section 5 item 6 of the record states it); and the PR run on `<RECORDS_COMMIT>`, if it has finished (every job, the gate's line, the artifacts). Say what you read.

## 3. What to review

1. **The selection rule** (D4, D5; DM-32 1.3, 1.4): a branch is deleted only when its head, as `ls-remote` read it, is an ancestor of `main`'s head, it is not on the keep-list, and no open PR names it as head or base. Is any path to a deletion missing one of these? Is an unresolvable head always kept? Is `main` resolved before any decision, and does a moved `main` refuse? Does the fresh-branch case behave as the CI policy says?
2. **The triggers and permissions** (D1 to D3, D8; DM-32 1.1, 1.2, 1.7, 1.8): `push` to `main` and `workflow_dispatch` only; the `main`-only condition; `permissions: {}`, the job's `contents: write` and `pull-requests: read`; the timeout; checkout's pin, `persist-credentials: false` and `fetch-depth: 0`; the concurrency group; the token only in the script step's `env:`; no `secrets.`; no `${{` inside a `run:`; the mode, with any `dry_run` but an exact `false` a dry run.
3. **Where the token reaches** (D3; DM-32 1.1), and **V1**:
   - the script's environment; `ls-remote` and `push` through `NETWORK`; the API request's `Authorization` header, unredirected, with redirects refused;
   - is it kept out of every argument, file, git config, log line and local git command (`git()`), and does `diagnostic()` mask it?
   - **V1:** `NETWORK` puts `-c credential.helper=` before the script's helper, so that a helper configured earlier (system, global, repository or URL-scoped) is not asked to `store` the token. No test fails when the reset is dropped. Confirm or challenge that the reset does this, on git's documented helper-list behaviour and a scratch check of your own, and class the gap.
4. **The lease and the restore record** (D6; DM-32 1.5): `--force-with-lease=refs/heads/<name>:<sha>` with `:refs/heads/<name>`; a refused lease kept, reported, and not an error; a failed deletion failing the run (exit 1); each deletion's row written before the next deletion; `git push origin <sha>:refs/heads/<name>` restoring a branch from its row.
5. **Fail closed** (D7; DM-32 1.3): the listing reads every page until no `rel="next"`, and refuses on any HTTP error, non-200 status, redirect, network error, malformed JSON, entry without number, head or base, missing token, or more than `MAX_PAGES` pages; all reads finish before the first deletion; exit 2 for a refusal, with nothing deleted.
6. **Injection** (D4, D8): branch names from `ls-remote`, PR refs from the API or the JSON file, the event and `dry_run` from the environment. Does any reach a shell, an option position, a refspec that parses another way, or a line that starts a workflow command? Is the summary's escaping (`cell()`, the code-span fences, `|`, non-printable characters) sound for any name git allows? Is `--open-prs-json` refused outside a dry run?
7. **Foundation and the classifier** (D9; findings 10, 11, 12, 14): `!cancelled() && (…)` on the six application jobs and `always()` kept on the gate, so a superseded run's gate fails and a passing gate still needs six passing or six exempt jobs; Mobile's 25 minutes; the upload-artifact pin `cf430e030ddbb5b0abf93d22962f4752f3646cd9` (v7.0.2) with the inputs both uploads use; both policy suites in the API job; `'ccr-**'` in the push filter; `--ignore-submodules=none` and its test. Does the classifier change alter the result for any change but one a submodule setting hid?
8. **The threat model** (DM-32 1.16). Write your own, briefly, then check the record's section 7 against it; do not take it from the record. Cover:
   - **the token's reach**, as item 3;
   - **a branch's own copy of either workflow:** what a branch that edits `branch-cleanup.yml`, the script or `foundation.yml` can run, with which token and permissions, on push and on dispatch; what a fork PR can run; what a merged change does at its own merge; and what stops each (the CI policy's "Trust limit");
   - **names and inputs**, as item 6;
   - **the listing's completeness**, as item 5, and **V5**: past 100 open PRs, a PR that closes between two page reads can move another across the page boundary unread, and a PR opened after the listing is not seen; either can let a branch that just became a PR's head be deleted, which closes that PR. One PR is open today. Confirm or challenge it, weigh it against a fix (for example a re-read of the listing after the deletions are chosen), and class it;
   - **races between selection and deletion:** a branch pushed or created after `ls-remote`, a head pushed after checkout, `main` moved after checkout or after selection, two cleanup runs, a pending run replaced.
9. **The tests:** do the 16 cleanup tests and the classifier's new test each fail without their part of the code? Reproduce, in a scratch copy: R5 (`--force` in place of the lease), R7 (a listing error ends the listing), R10 (`dry_run_input != "true"`), R12b (the push through a shell string), R13 (the flag removed), R15 (local git commands keep the token), and V1's reversal (`"-c", "credential.helper=",` dropped from `NETWORK`). Add any reversal of your own that the security focus calls for. Optional, read-only: one dry run, as the record's section 4 does, with `env -i`, `--dry-run` and `--open-prs-json` from your GitHub tools' listing; record its table.
10. **The records:** the CI policy's changes (the cleanup section, the push filter, the cancel paragraph, the upload-artifact row, the public repository, and the opening line); the evidence record; the manager workflow's steps 3, 5 and 7 and the handover checklist's keep-list line. Does any statement claim more than the code, the tests or the runs show?
11. **The offline checks,** run at `HEAD` in a clean environment: `python3.12 -I -m unittest discover -s scripts -p 'test_change_scope.py' -v` (14 at the code head) and the same for `test_branch_cleanup.py` (16); `python3.12 -I -m py_compile` of the four scripts; `git diff --check origin/main...HEAD`.

## 4. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<RECORDS_COMMIT>`), and the start gate's and the classification's results;
- the environment check;
- a verdict: **approve**, or **changes required**, with the findings that require them;
- every finding, numbered, with its severity (blocking, should fix, nit), its file and line, what is wrong, why it matters, a suggested fix, and whether it falls in one of the correction classes above;
- your threat model (section 3 item 8), and your verdict on V1 and on V5;
- for each focus area, what you checked and what you found;
- the offline checks, reversals and runs you read, with their exact results;
- limits of the review, and open questions.

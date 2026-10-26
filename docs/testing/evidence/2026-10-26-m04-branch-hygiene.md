# M04 — Branch hygiene: evidence record

The cleanup workflow for fully merged branches (Nathan, 5 October 2026; OD-39) and the four CI fixes from M05 (findings 10, 11, 12 and 14), built to D1 to D9 of [M04's brief](../../planning/m04-branch-hygiene.md), revision 3, with DM-32's conditions 1.1 to 1.16 ([report](../../continuity/dev-manager/reviews/2026-10-26-dm-32-m04-brief.md)).

## 1. Identity

- **Prompt:** revision 1, at commit `bbd461bcad24a22062f5cad4bcbd695ce1826eb0` of the manager branch `claude/magical-wozniak-yfmmx2`.
- **Session branch:** `claude/laughing-meitner-ywjnk1`, set to `bbd461b` before any work. Commits:
  - `2d3566d` code: the cleanup workflow, script and tests, and Foundation's D9 changes;
  - `6199f2c` the CI policy (Markdown), pushed 20 s after `2d3566d` for the cancel test;
  - `27ef2f6` **code head**: the classifier flag and its test;
  - the commit that adds this record and the CI policy's cancel paragraph as run 40269750327 showed it (Markdown only).
- **Run of record:** push run 40270021713 on `27ef2f6`: all eight jobs `success`, gate `Application checks passed` (section 5, item 6). No PR run: this session opens no PR.
- **Date:** 26 October 2026 (UTC). Environment: `Glow App - No Stream`.
- **Environment check (names only):** none of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` is set (the loop printed nothing); `compgen -e | grep -E '^STREAM_'` printed nothing (exit 1). The names `GITHUB_TOKEN` and `GH_TOKEN` are present in this session's environment; their values were never read, and every repository command below ran under `env -i`, without them. Toolchain in `$HOME/.local/bin`: `python3.12` 3.12.14, `node` v24.19.0, `npm` 11.9.0; `/usr/bin/python3` is 3.13.17.
- **Start gate:** every check passed. `HEAD` = `bbd461b…`; PR34 (`4aa66e2`) is an ancestor; no non-Markdown path differs from `4aa66e2` on `origin/main` (= `4aa66e2`) or on `HEAD`; nothing under `.github`, `scripts`, `services`, `apps`, `packages` or `proofs` differs between `bbd461b` and the live manager branch (= `bbd461b`); this record did not exist there.

## 2. The work, item by item

| # | Item | State | Where | Test |
|---|---|---|---|---|
| 1 | Cleanup workflow (D1, D2, D3, D7, D8) | Done | `.github/workflows/branch-cleanup.yml:7-49` | Section 5, item 4 |
| 2 | The script (D4 to D8) | Done | `scripts/branch_cleanup.py` | Item 3's tests |
| 3 | Selection tests, each with a reversal | Done: 16 tests | `scripts/test_branch_cleanup.py` | Section 5, items 3 and 5 |
| 4 | Foundation (D9) | Done | `foundation.yml:6` (`'ccr-**'`), `:53`, `:82`, `:126`, `:151`, `:168`, `:200` (`!cancelled()`), `:438` (gate on `always()`), `:85` (Mobile 25), `:114` and `:413` (upload-artifact v7.0.2), `:70-71` (both policy suites) | Runs 40269750327, 40269779556 and 40270021713 |
| 5 | Classifier (finding 12) | Done | `scripts/change_scope.py:41` | `test_change_scope.py:101`, reversal R13 |
| 6 | CI policy | Done | `docs/operations/ci-and-branch-policy.md` | Against sections 4 and 5 |
| 7 | Cancel test | Done | Runs 40269750327 and 40269779556 | Section 5, item 6 |
| 8 | Pre-merge dry run | Done | Section 4 | — |

**The script, by D-point:** the mode, `deletes()` (`:62`); the listing, `read_open_prs()` (`:102`), page by page until GitHub links no next page, at most `MAX_PAGES` = 50, refusing on any error, status other than 200, redirect, malformed JSON or entry; the remote read, `read_heads()` (`:144`); `main`'s resolution, `resolve_main()` (`:164`); the rule, `decide()` (`:175`) with `KEEP` (`:22`); the leased deletion, `delete_branch()` (`:188`, the push at `:191`); the escaping, `cell()` (`:199`); the row-by-row summary, `Summary` (`:206`) and `main()` (`:276`). All reads finish before the first deletion, so a refused read deletes nothing.

## 3. Choices where the brief leaves one

- **Mobile timeout: 25 minutes.** Run 40243775584's Mobile job took 6 min 24 s (Chromium install 23 s, rendered suite 4 min 47 s). Run 40029112295's job hit its 15-minute timeout after an 11 min 27 s Chromium install, with the rendered suite cancelled after 2 min 47 s. That install plus a normal job is about 17.5 minutes, so 25 leaves about 7.5 minutes. Measured with my GitHub tools' job reads.
- **The cleanup job's timeout: 10 minutes.** The script runs one `ls-remote`, a few API pages and one push per deletion.
- **The token's route into git:** the step's `GITHUB_TOKEN`, read by a credential helper given with `-c` on the two commands that reach the remote (`ls-remote`, `push`): `-c credential.helper=` first drops every helper configured earlier, then `credential.helper=!f() { … printf "username=x-access-token\npassword=%s\n" "$GITHUB_TOKEN"; }; f` answers `get` only. The argument names the variable, never its value. Local git commands run without `GITHUB_TOKEN` in their environment (`git()`, `:45`). A scratch check with a repository-level `store` helper and a URL-scoped one showed neither was handed the credential.
- **No fetch in the script.** It relies on checkout's `fetch-depth: 0`, which in `actions/checkout` v7.0.1 fetches `+refs/heads/*:refs/remotes/origin/*` (`src/ref-helper.ts`, read in a shallow clone at `3d3c42e`). A head pushed after the checkout is not in the object store, so it is kept as unresolvable. If `main` moved after checkout, the run refuses only when `main`'s head, as `ls-remote` read it, is not a commit in the checkout, and the run its push queued follows; a `main` moved to a commit the checkout already holds is decided against the new head, which is correct. [Corrected in M04-C1: the exact-head review's F5]
- **Read order:** the remote, then `main`, then the open PRs, so the listing is as close to the deletions as it can be.
- **The keep-list's location:** a constant in the script (D5).
- **The summary's format:** a Markdown header with the mode and `main`'s head and the restore command, a PR table, then one row per branch in name order. Each name is a code span with a fence longer than any backtick run in it, `|` escaped and non-printable characters shown as `\uXXXX`. Every line also goes to the log.
- **Exit codes:** 0; 2 for a refusal (nothing deleted); 1 when a deletion failed other than by a refused lease. A refused lease is reported and is not an error.
- **Interpreter:** the runner's `python3` (3.12 on `ubuntu-24.04`), run with `-I`; standard library only, so no setup action is added.

## 4. The pre-merge dry run (acceptance check 4)

At `27ef2f6`: `git fetch --no-tags origin '+refs/heads/*:refs/remotes/origin/*'`; the open PRs from my GitHub tools (`list_pull_requests`, state open, 100 per page: one page, one PR) written to a scratch JSON file; then `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8 GITHUB_STEP_SUMMARY=<scratch> python3.12 -I scripts/branch_cleanup.py --dry-run --open-prs-json <scratch>`. Exit 0; `git ls-remote origin 'refs/heads/*'` listed the same 5 branches afterwards.

| Branch | Head | Decision | Reason |
|---|---|---|---|
| `claude/dev-manager` | `3abbc814a3220d1fb14ace222db8d55bf2b37760` | kept | keep-list |
| `claude/laughing-meitner-ywjnk1` | `27ef2f6fdc65f4f1d684c66ae69ff0e601f4f427` | kept | unmerged |
| `claude/magical-wozniak-yfmmx2` | `bbd461bcad24a22062f5cad4bcbd695ce1826eb0` | kept | keep-list |
| `claude/zen-thompson-5fdqqz` | `e27f7c7c02693bb1ed5223d9a0b06b3f67b40fd5` | would delete | merged into main |
| `main` | `4aa66e2336d1a040bfd1b0ec5ea4cdf79209a2f6` | kept | keep-list |

Open PRs read: #35, head `claude/magical-wozniak-yfmmx2`, base `main`. **Expected deletions at M04's merge:** `claude/zen-thompson-5fdqqz`, and this session's branch once its head is in `main`, plus any other branch fully merged by then.

## 5. Checks

1. **The diff.** `git diff --check bbd461b… HEAD`: clean. `git diff --name-only bbd461b… HEAD`: the eight owned paths only (`.github/workflows/branch-cleanup.yml`, `.github/workflows/foundation.yml`, `docs/operations/ci-and-branch-policy.md`, this record, `scripts/branch_cleanup.py`, `scripts/change_scope.py`, `scripts/test_branch_cleanup.py`, `scripts/test_change_scope.py`).
2. **Classification**, trusted policy from `origin/main` = `4aa66e2`, extracted to a scratch directory, `/usr/bin/python3 -I … --base bbd461b… --head 27ef2f6… --merge-base`: `{"full": true, "reason": "behavior-or-empty", "paths": [the 7 code-head paths]}`. Full scope, as expected.
3. **Script tests** (`env -i … python3.12 -I -m unittest discover -s scripts -p …`): `test_change_scope.py` 13 tests OK at `bbd461b`, 14 OK at `27ef2f6`; `test_branch_cleanup.py` did not exist at `bbd461b`, 16 OK at `27ef2f6`. Also `py_compile` of all four scripts: OK.
4. **The workflows' text** (parsed with the system PyYAML 6.0.3, not a repository dependency; and `grep -n`):
   - triggers `push` to `[main]` and `workflow_dispatch` with `dry_run` (`type: boolean`, `default: true`); no other trigger;
   - `permissions: {}` at the top; the job `if: github.ref == 'refs/heads/main'`, `timeout-minutes: 10`, `permissions: {contents: write, pull-requests: read}`;
   - `concurrency: {group: branch-cleanup, cancel-in-progress: false}`;
   - checkout `actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1` with `persist-credentials: false`, `fetch-depth: 0`; no other action;
   - one script step, whose `env:` holds `GITHUB_TOKEN: ${{ github.token }}`, `CLEANUP_EVENT: ${{ github.event_name }}` and `CLEANUP_DRY_RUN: ${{ inputs.dry_run }}`, and whose `run:` is `python3 -I scripts/branch_cleanup.py`;
   - `secrets.` in the file: no match; `${{` in any `run:`: none.
   - `foundation.yml`: the push filter adds `'ccr-**'`; the six application jobs' `if:` starts `!cancelled() &&`; the gate keeps `if: always()`; Mobile `timeout-minutes: 25`; both uploads `actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9 # v7.0.2` with their inputs unchanged; the API job's policy step runs both suites.
   - **upload-artifact:** `git ls-remote https://github.com/actions/upload-artifact` lists `v7.0.2` and `v7` at `cf430e030ddbb5b0abf93d22962f4752f3646cd9`, the newest release tag. Its `action.yml`, read in a shallow scratch clone and diffed with v4.6.2's (`ea165f8`): the five inputs both uploads use are unchanged; it adds `archive` (default `true`, zipped as v4) and moves `node20` to `node24`. The commit subjects between them name Node 24 (v5, v6), ESM and direct file uploads (v7.0.0), and a dependency bump (v7.0.2).
5. **Reversals.** Each is applied to a scratch copy of the scripts and its test run alone; all 18 fail, and the real code passes.

   | Id | Reversal (the smallest change) | Test | Result with it |
   |---|---|---|---|
   | R1 | `merge-base --is-ancestor main_sha sha` (arguments swapped) | merged branch selected | FAIL: `'merged' unexpectedly found` on the remote |
   | R2 | the `unmerged` keep removed | unmerged branch kept | FAIL: `'unmerged' not found` |
   | R3 | `claude/dev-manager` dropped from `KEEP` | keep-list names | FAIL (`claude/dev-manager`): not found |
   | R4 | the base of an open PR not protected | PR head and base | FAIL (`pr-base`): not found |
   | R5 | `--force` in place of the lease | moved after selection | FAIL: `'moved' not found` |
   | R6 | `return status != 1` (an error counts as merged) | unresolvable head | FAIL: `'foreign' not found` |
   | R7 | a listing error ends the listing (`return entries`) | failed listing | FAIL ×3: HTTP error on page 2, network error, not JSON: `0 != 2` |
   | R8 | `if True:` in place of `if not has_next(link):` | two-page listing | FAIL: `[['1']] != [['1'], ['2']]` |
   | R9 | rows collected and written after the loop | fails midway | FAIL: `'a-merged' not found in {}` |
   | R10 | `dry_run_input != "true"` | dispatch mode | FAIL ×12, from `None`, `''` and `'True'` on: `True is not false` |
   | R11 | `if True:` in place of `if deleting:` | dry run | FAIL: the remote's branches changed |
   | R12a | the pipe left unescaped in `cell()` | metacharacters | FAIL ×2: `6 != 5` cells; row text |
   | R12b | the push run through a shell string | metacharacters | FAIL: `pwned` and `pwned2` created |
   | R13 | `--ignore-submodules=none` removed | submodule test | FAIL: `False is not true` |
   | R14 | `resolve_main()` removed | fail closed (remote, main) | FAIL (`foreign_main`): `0 != 2` |
   | R15 | local git commands keep `GITHUB_TOKEN` | the token's reach | FAIL: `'test-token-…' != None` |
   | R16 | the JSON option accepted in delete mode | JSON file dry run only | FAIL: `0 != 2` |
   | R17 | a failed deletion does not fail the run | refused deletion | FAIL: `0 != 1` |

6. **CI runs** (read with my GitHub tools; nothing re-run or dispatched). The push filter: this branch is under `claude/**`, so its pushes started runs before `'ccr-**'` existed; `'ccr-**'` itself is not exercised by it.
   - **The cancel test.** `2d3566d` pushed at 04:34:13, `6199f2c` at 04:34:33. **Run 40269750327** (`2d3566d`): Change scope `success`; all six application jobs `cancelled`. API checks, API mobile smoke and API artifact checks had finished every step `success` (the last at 04:35:11) and still read `cancelled`; Stream proof checks (its unit-test step), Database proof checks (the suite step) and Mobile checks (the Chromium install) were stopped mid-step at 04:35:46, 04:35:52 and 04:35:52, 71 to 77 s after the newer run was created (04:34:35). The `always()` steps ran (both uploads, the database removal). Foundation gate `failure`: `AssertionError: Unexpected api result`. Conclusion `cancelled`; no artifact. **Run 40269779556** (`6199f2c`, Markdown only), the result: it waited until 04:36:01, then Change scope `success`, the six jobs `skipped`, the gate `success`, `Ordinary documentation: application jobs intentionally skipped`. The API job's policy step in run 40269750327 passed both suites on the runner before the stop.
   - **The run of record, 40270021713** (`27ef2f6`, push, 04:37:25 to 04:45:06): conclusion `success`. Change scope, API checks, Mobile checks, API mobile smoke, API artifact checks, Stream proof checks, Database proof checks and Foundation gate: all `success`. The gate's log line: `Application checks passed`.
     - API checks' policy step: `test_change_scope.py` `Ran 14 tests` OK and `test_branch_cleanup.py` `Ran 16 tests` OK on the runner (Python 3.12.14), then the API suite's 366 and the contracts' 39. I searched the full 1,958-line log for these result lines; I did not read it otherwise.
     - **Mobile checks:** 6 min 32 s (04:37:35 to 04:44:07) against its new 25-minute timeout; Chromium install 23 s; rendered suite 4 min 54 s.
     - Database proof checks: 7 min 24 s against 30 (its suite step 6 min 29 s, under OD-21's 24 minutes).
     - **Artifacts** (DM-32 1.9): `p04-empty-form-layout`, 64,386 bytes, expires 2026-11-09T04:44:04Z, and `p06-db-proof-results`, 20,841 bytes, expires 2026-11-09T04:44:54Z: both present under v7.0.2, with 14 days' retention.
7. **Secret scan** over `git diff bbd461b… HEAD` added lines, for GitHub, AWS, Slack and OpenAI-style keys, private-key headers, `password=` values, `token = "` and e-mail shapes. Hits, none a secret: the helper's `printf` format (names `$GITHUB_TOKEN`, carries no value); the test's fake `TOKEN = "test-token-0123456789abcdef"`; the reserved placeholder `test@example.invalid`, as `test_change_scope.py:21` already uses; test assertions on `password=`; and this record's own lines that quote the helper's format and describe the scan.

## 6. Deviations and limits

- **D9 stops superseded jobs, but not at once.** Finding 10's fix holds: the superseded run's application jobs are cancelled and its gate fails. In the test the stop took 71 to 77 s, so three jobs finished every step first and the newer run waited 86 s. The CI policy states this; step 5's and step 3's texts are the manager's.
- **No pre-merge check reaches the cleanup's GitHub path** (DM-32 1.10): the token's write permission, the API listing and the lease against GitHub are first exercised by the first run on `main`. The tests use a bare local remote and a fake listing.
- **The listing's completeness has a race only past 100 open PRs:** GitHub pages by number, so a PR closed between two page reads can move another PR across the boundary unread. A PR opened after the listing is not seen at all. Either can let a merged head that just became a PR's head be deleted, which closes that PR; its row restores the branch.
- **The CI policy's opening line still says "the new private application repository"** (line 3), outside the parts the brief lists; I left it byte-identical. It is the manager's to correct with OD-51's other texts.
- **No PR run.** The manager's PR run on the integrating head is the merge's run of record (manager workflow, step 7).

## 7. What the exact-head review must know (DM-32 1.16)

- **Where the token can reach.** It is `${{ github.token }}` with `contents: write` and `pull-requests: read`, in one step's `env:` only. In that step it reaches:
  - the script's process environment;
  - the `ls-remote` and `push` subprocesses, and through them the helper's shell, which prints it to git on `get` only;
  - the `Authorization` header of requests to `https://api.github.com/repos/<GITHUB_REPOSITORY>/pulls`, set as an unredirected header, with redirects refused.

  It is in no argument, file, git config or line the script prints; `diagnostic()` masks it in git's error line should git ever print it. Checkout gets the token through its own default input and removes it after (`persist-credentials: false`).
- **A branch's own copy of either workflow.** GitHub runs a push's or dispatch's workflow from the branch's commit, so a branch that edits `branch-cleanup.yml` or the script can drop the `main`-only condition and run with the permissions it declares, `contents: write` included; a branch's copy of `foundation.yml` can change its own routing and gate. That needs push access, which can delete branches anyway. The cleanup has no PR trigger; a fork PR whose copy adds one runs it with a fork's read-only token. A merged change to the cleanup acts at its own merge. The protection is the review of workflow changes (`AGENTS.md`), not the condition.
- **Where a name or an input enters a command.** Branch names come from `ls-remote` and PR refs from the API or the JSON file. A name goes into git only as `refs/heads/<name>`, one list element, in `--force-with-lease=refs/heads/<name>:<sha>` and `:refs/heads/<name>`; git refnames cannot contain `:`, so the lease parses one way, and the `refs/heads/` prefix keeps a name such as `-lead` from reading as an option. Ancestry and the lease take only 40-hex SHAs from `ls-remote`. `--remote` refuses a leading `-`. The event and `dry_run` reach the script as environment values and are compared as strings; nothing is passed to a shell, and no `${{ }}` is in a `run:`. In the summary and the log, names are code spans with `|` escaped; since a refname cannot hold `:` or a newline, no line can start a workflow command.
- **The listing's completeness.** It reads every page until GitHub's `Link` header has no `rel="next"`, and refuses on any HTTP error, non-200 status, redirect, network error, malformed JSON, entry without a number, head or base, or more than 50 pages. A missing token refuses. The summary lists each PR it read. Protection is by name, so a fork's same-named head also keeps the branch.
- **Races between selection and deletion.**
  - A branch pushed after `ls-remote`: the lease refuses, and the row says so. The push also carries the checked head as the ref's old value, so the server refuses an update that moved after its advertisement.
  - A branch created after `ls-remote` is not considered.
  - A head pushed after checkout is unresolvable, so it is kept.
  - `main` moved after checkout: the run refuses when `main`'s head, as `ls-remote` read it, is not a commit in the checkout; when the checkout already holds that commit, the run decides against the new head, which is correct. [Corrected in M04-C1: the exact-head review's F5]
  - `main` moved or rewound after selection: the selection used `main` as `ls-remote` read it; a rewind of `main`, which the branch policy forbids, could leave a deleted branch's commits reachable only from the summary's head.
  - A PR opened or closed during or after the listing: see section 6.
  - Two cleanup runs never overlap (one concurrency group); a pending run can be replaced by a newer one, and the run that remains reads the state afresh.

## Manager verification of M04 (26 October 2026, App Manager 8)

App Manager 8 read the relayed report against the pushed branch `claude/laughing-meitner-ywjnk1` (head `7f9e6e7`, code head `27ef2f6`) before integrating it. This section takes the record past the 150-line target (step 5): it is what the exact-head review must know of the manager's own checks.

- **Scope:** `git diff --name-only bbd461b 7f9e6e7` lists the 8 owned paths only, all mode `100644`; `git diff --check` is clean. The trusted classifier from `main` (`4aa66e2`) prints full scope.
- **The code, read whole:** `branch-cleanup.yml` (triggers, the `main`-only condition, `permissions: {}`, the job's `contents: write` and `pull-requests: read`, `timeout-minutes: 10`, `persist-credentials: false`, `fetch-depth: 0`, the token as `${{ github.token }}` in one step's `env:`, no `secrets.` and no `${{` inside `run:`); `branch_cleanup.py` (the mode, the paged listing with redirects refused and the Authorization header unredirected, fail-closed reads, the keep-list, the lease, the environment-only credential helper behind an empty-helper reset, the token stripped from local git commands, names as argument elements, the row-by-row summary); `foundation.yml`'s D9 lines; the classifier's flag and its test; the CI policy's changes.
- **The tests, run here** in a scratch worktree at `7f9e6e7`, `env -i`, `python3.12` 3.12.14: `test_change_scope.py` 14 tests OK; `test_branch_cleanup.py` 16 tests OK.
- **Seven reversals of the manager's own**, each in a scratch copy with `discover -k`, with two unmodified controls passing:
  - the lease removed: `test_branch_moved_after_selection_is_kept_by_the_lease` fails;
  - open PRs ignored: `test_open_pr_head_and_base_are_kept` fails (3 subtests);
  - a dispatch deleting unless `true`: `test_dispatch_deletes_only_on_exact_false` fails (12 subtests);
  - `claude/dev-manager` off the keep-list: `test_keep_list_names_are_kept_while_merged` fails;
  - the next page ignored: `test_two_page_listing_is_read_whole` fails;
  - the submodule flag removed: `test_submodule_ignore_setting_cannot_hide_a_gitlink_move` fails;
  - **the empty `credential.helper=` reset dropped: every test still passes.** The record says the reset was shown by a scratch check, not a test (section 3), so no claim is wrong; it is a coverage gap (V1 below).
- **The runs, read with the GitHub tools:**
  - run of record 40270021713 (push, `27ef2f6`): all eight jobs `success`; the gate log prints `Application checks passed`; Mobile 04:37:35 to 04:44:07 (6 min 32 s of 25); artifacts `p04-empty-form-layout` (64,386 bytes) and `p06-db-proof-results` (20,841 bytes), each expiring 9 November (14 days);
  - the cancel test, run 40269750327 (`2d3566d`): all six application jobs `cancelled`; API checks, smoke and artifact had finished every step; Stream proof, Database and Mobile stopped mid-step at 04:35:46 to 04:35:52; the Database job's clean-up step still ran; the gate failed. Run 40269779556 skipped the application jobs as documentation;
  - the records run 40270835083 (`7f9e6e7`): `success`.
- **The pin:** `git ls-remote https://github.com/actions/upload-artifact` names `cf430e030ddbb5b0abf93d22962f4752f3646cd9` for both `v7` and `v7.0.2`.
- **The integration:** PR35 merged first, as `85bbd4d`. The manager branch was brought to `85bbd4d` and the session branch merged into it with a merge commit, `39b6141` (parents `85bbd4d` and `7f9e6e7`). `git diff --name-only 85bbd4d 39b6141` lists the 8 paths, and they are byte-identical to `7f9e6e7`. The manager's records for V2 to V4 and V6, and this section, followed in the next commit; of these paths they change only the CI policy's opening line and this record.

**Findings, for the exact-head review:**

| # | Finding | Class | Disposition |
|---|---|---|---|
| V1 | The empty-helper reset that keeps an earlier credential helper from receiving the token has no test: a reversal that drops it passes the suite | Test coverage, security-relevant | To the exact-head review, which decides fix or carry (step 6's rule) |
| V2 | The CI policy's opening line still says "the new private application repository" (the session flagged it, outside its listed changes) | Records | Corrected in M04's PR, with the two start prompts' "private repository" (OD-51) |
| V3 | The cancel stop is delayed (71 to 77 s); the manager workflow's steps 3 and 5 must say so, citing the CI policy (DM-32 1.12 to 1.14) | Records | Steps 3 and 5 rewritten in M04's PR, with step 5's push-filter line and step 7's checklist and branch-state texts, for the Dev Manager's pre-merge read |
| V4 | The keep-list names one manager branch; a new manager branch is deleted once fully merged unless a full-scope keep-list change lands first | Process | Added to the handover checklist and the next-manager start prompt, in M04's PR, for the Dev Manager's read |
| V5 | Past 100 open PRs, a PR closing between page reads can move another across a page unread; a PR opened after the listing is unseen | Race, recorded by the session | To the exact-head review's threat model; one open PR today |
| V6 | `GITHUB_TOKEN` and `GH_TOKEN` are present, by name, in this session's and the manager's containers; never read | Environment | Noted in the [environment inventory](../../operations/environment-inventory.md), "Claude cloud environments" |

## Exact-head review of M04 (26 October 2026)

- **The review:** an exact-head code and security review that Nathan ran from [the review prompt](https://github.com/amthorn78/glow-dating-app/blob/4794d3e99012c348a0fb78d8a12a6e6d1cd20f8e/docs/ephemeral/2026-10-26-m04-review-prompt.md), revision 1, at `55fc64a`, for code head `27ef2f6`, relayed on 26 October. Nathan's pick: not yet recorded. The report is relayed only, so its findings and checks are summarized here.
- **Gate and scope:** every start-gate check passed; the trusted policy from `85bbd4d` classified the PR full scope, with exactly the six code paths. The environment check found no HDE or `STREAM_*` name; `GITHUB_TOKEN` and `GH_TOKEN` were present and never read, and every repository command ran under `env -i`.
- **Verdict: changes required,** for two should-fix findings in the correction class "a guard of D3, D6 or D7 that no test fails without". No blocking finding. The selection rule, triggers and permissions, the token's reach, the lease, fail-closed, the injection handling, the Foundation and classifier changes, and every run claim checked out; every DM-32 condition and every item of the implementation prompt is met at this head.

| # | Severity | Finding | Disposition (step 6) |
|---|---|---|---|
| F1 (V1) | Should fix | The empty `credential.helper=` reset (`branch_cleanup.py:38`) has no test; dropping it passes all 16. The reviewer's scratch check: without it, a global or URL-scoped helper is handed `get` and `store`, and `store` carries the token | (a): in a named class. Fixed before the merge by M04-C1, a test with its reversal |
| F2 | Should fix | The redirect refusal (`_NoRedirect`, `:89-95`) has no test; dropping it passes all 16. On a loopback 302 the real code refuses; without it urllib follows, drops the `Authorization` header, and accepts the new location's listing, so a redirected empty listing would remove every PR protection | (a): in a named class. Fixed before the merge by M04-C1, a test with its reversal. The manager reproduced the passing reversal |
| F3 | Nit | Each row is written after its push returns (`:274-276`), so a run killed during a push may leave that one deletion unrecorded; the CI policy (`:63`) says a run that fails midway names every head it deleted | A record claim, narrowly: the wording is made exact in M04-C1 (a script that fails midway still names every head it deleted; a run killed during a push may miss that one, whose commits are in `main`). No script change. The Dev Manager's pre-merge read checks it against DM-32 1.5 |
| F4 | Nit | The git helper answers `get` for any host | (b): a follow-up, in the carried-items file |
| F5 | Nit | Sections 3 and 7 say a `main` moved after checkout refuses; it proceeds, correctly, when the new head is already in the checkout | A record claim, narrowly: corrected in M04-C1 |
| F6 | Nit | The mask in `diagnostic()`, the strict decode and SHA check in `read_heads()` and `cell()`'s non-printable escaping have no failing reversal; none changes a deletion decision | (b): a follow-up, in the carried-items file |
| V5 | — | Confirmed: past 100 open PRs a PR closing between page reads can shift another unread, and a PR opened after the listing is unseen; one open PR today | Carried, as section 6 states it; the row restores a deleted branch |

- **The threat model** (DM-32 1.16) agrees with section 7, adding F3's in-flight push and F5's resolvable `main`. The token reaches the script's environment, the two network git commands' helper (on `get` only) and the API header; nothing else. A branch's own copy of a workflow is bounded only by push access and the review of workflow changes; no ruleset protects `main` or the kept branches, which the reviewer asks to add to OD-51's branch-controls question.
- **Checks the reviewer ran:** at `55fc64a`, 14 and 16 tests OK, `py_compile` OK, `git diff --check` clean. Reversals R5, R7, R10, R12b, R13 and R15 fail their tests; V1's and F2's (M1) pass the suite; of the reviewer's own, M2, M6, M7, M9 and M10 fail their tests, and M3, M4, M5 and M8 pass the suite (F6). Runs 40270021713, 40269750327, 40269779556 and the PR run 40315206331 on `55fc64a` (8 jobs `success`, `Application checks passed`, both artifacts with 14 days) match the record. A dry run at `55fc64a` decided as section 4, with the manager branch at `06608f2`.
- **Limits the reviewer named:** the GitHub path is untested before the first run on `main` (DM-32 1.10); the helper-list check ran on git 2.43.0, not the runner's 2.55.0; the redirect check used loopback HTTP; six of the record's 17 reversals were reproduced.

## Correction pass M04-C1 (26 October 2026)

### Identity

- **Prompt:** M04-C1, revision 1, at commit `e4045c8d5f2c7e32aa057f333e6c6bae8029d75b` of the manager branch `claude/magical-wozniak-yfmmx2`, from Nathan.
- **Session branch:** `claude/blissful-volta-coypr6`, set to `e4045c8` before any work. Commits:
  - `0274096` **code head**: the two tests (F1, F2);
  - the commit that adds this section and the CI policy's and this record's corrections (F3, F5; Markdown only), pushed after the code commit's run had finished.
- **Run of record:** push run 40347076599 on `0274096` (15:12:43 to 15:19:29 UTC): all eight jobs `success`, gate `Application checks passed`. No PR run: this session opens no PR.
- **Environment:** `Glow App - No Stream`. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` is set (the loop printed nothing); `compgen -e | grep -E '^STREAM_'` printed nothing. The names `GITHUB_TOKEN` and `GH_TOKEN` are present; their values were never read. Every repository command ran under `env -i PATH="$HOME/.local/bin:$PATH" HOME="$HOME" LANG=C.UTF-8`, without them. `python3.12 --version`: Python 3.12.14, in `$HOME/.local/bin`; `/usr/bin/python3` is 3.13.17; git 2.43.0.
- **Start gate:** every check passed. `HEAD` = `e4045c8…`, an ancestor of the live manager branch (= `e4045c8`); nothing under `.github`, `scripts`, `services`, `apps`, `packages` or `proofs` differs from M04's code head `27ef2f6`, or between `e4045c8` and the live branch; the live record had no "Correction pass M04-C1" heading (count 0).

### The four items

| # | Item | State | Where |
|---|---|---|---|
| 1 | F1 (V1): a test for the credential-helper reset | Done | `scripts/test_branch_cleanup.py:435-460`, `test_helpers_configured_earlier_never_see_the_token` |
| 2 | F2: a test for the redirect refusal | Done | `scripts/test_branch_cleanup.py:462-498`, `test_redirected_listing_is_refused` |
| 3 | F3: the restore record's sentence | Done | `docs/operations/ci-and-branch-policy.md:63` |
| 4 | F5: the two sentences on a moved `main` | Done | this record, section 3 (`:38`) and section 7 (`:128`), each marked |

- **F1's test.** `GIT_CONFIG_GLOBAL` names a scratch config with `credential.helper` and `credential.https://github.com.helper`, each a recording script (given as `!<path> generic` and `!<path> scoped`) that appends its arguments and its input to a scratch log. `git <NETWORK> credential fill` for `protocol=https`, `host=github.com`, with the fake `TOKEN` as `GITHUB_TOKEN` and `GIT_TERMINAL_PROMPT=0`, prints `username=x-access-token` and the token as the password; `git <NETWORK> credential approve` with that output exits 0; the log does not exist. **The control:** the same two commands with `-c credential.helper=<the script's helper>` alone print the same credential, and the log's `run:` lines are then exactly `generic get`, `scoped get`, `generic store` and `scoped store`, compared sorted [Corrected by the re-review's nit 3: the log also holds each helper's input]. The control builds its argument from `CREDENTIAL_HELPER`, not from `NETWORK`, so it is unchanged by the reversal.
- **F2's test.** A `ThreadingHTTPServer` on `127.0.0.1`, port 0, in a daemon thread, answers `/repos/owner/repo/pulls` with a 302 to `/elsewhere`, which would answer 200 with `[]` and no `Link` header. With `branch_cleanup.API` patched to `http://127.0.0.1:<port>`, `read_open_prs("owner/repo", TOKEN, urlopen=branch_cleanup._open)` raises `Refused`, and the server served only the pulls path. During the call every `*_proxy` variable, in either case, is removed from `os.environ` and `NO_PROXY` and `no_proxy` are `127.0.0.1` (`mock.patch.dict`, restored after). The clean-up shuts the server down, closes it and joins the thread.
- **F3.** The bullet now says each deletion's row is written as soon as its push returns, so a run whose script fails midway still names every head it deleted, and the restore command; then that a run killed while a push is in flight may leave that one deletion unrecorded, and its commits are in `main`. The rest of the bullet and of the file is byte-identical.
- **F5.** Both sentences now say the run refuses only when `main`'s head, as `ls-remote` read it, is not a commit in the checkout, and that a `main` moved to a commit the checkout already holds is decided against the new head, which is correct.

### Checks

| # | Check | Command | Result |
|---|---|---|---|
| 1 | The diff | `git diff --check e4045c8… HEAD`; `git diff --name-only e4045c8… HEAD` | clean; `docs/operations/ci-and-branch-policy.md`, this record, `scripts/test_branch_cleanup.py`: the three owned paths only, all mode `100644` |
| 2 | Classification | trusted `scripts/change_scope.py` from `origin/main` = `85bbd4d`, extracted to a scratch directory; `/usr/bin/python3 -I … --base e4045c8… --head <h> --merge-base` at `0274096`: `{"full": true, "reason": "behavior-or-empty", "paths": ["scripts/test_branch_cleanup.py"]}`; at the records head, the same with the two Markdown paths added. Full scope, as expected |
| 3 | The tests at the start (`e4045c8`) | `env -i … python3.12 -I -m unittest discover -s scripts -p 'test_branch_cleanup.py' -v`, and the same for `test_change_scope.py` | 16 OK; 14 OK |
| 3 | The tests at the head | the same `test_branch_cleanup.py` 18 OK (the 16, unchanged, and the two new); `test_change_scope.py` 14 OK, unchanged |
| 3 | The new tests with loopback proxy variables set | the same, with `HTTP_PROXY`, `http_proxy` and `HTTPS_PROXY` = `http://127.0.0.1:9`, `-k redirected -k helpers_configured` | 2 OK |
| 4 | F1's reversal | scratch copy; `"-c", "credential.helper=",` dropped from `NETWORK` | `test_helpers_configured_earlier_never_see_the_token` FAIL: `self.assertFalse(log.exists())`, `True is not false`; the other 17 pass (`FAILED (failures=1)` of 18) |
| 4 | F2's reversal | scratch copy; `build_opener(_NoRedirect)` → `build_opener()` in `_open()` | `test_redirected_listing_is_refused` FAIL: `Refused not raised`; the other 17 pass (`FAILED (failures=1)` of 18) |
| 4 | The real code | as check 3 | both new tests pass |
| 5 | Foundation on `0274096` | read with the GitHub tools; nothing re-run or dispatched | run 40347076599 (push): Change scope, API checks, Mobile checks, API mobile smoke, API artifact checks, Stream proof checks, Database proof checks and Foundation gate all `success`; the gate's log line `Application checks passed`. API checks' policy step on the runner (Python 3.12.14): `test_change_scope.py` `Ran 14 tests` OK; `test_branch_cleanup.py` `Ran 18 tests` OK, both new tests `ok`; then the API suite's 366 and the contracts' 39 OK. I searched the job's 1,960-line log for these lines and did not read it otherwise |
| 6 | Secret scan | added lines of `git diff e4045c8… HEAD`, for GitHub, AWS, Slack and OpenAI-style keys, private-key headers, `password=`, `token = "`, `api_key` and e-mail shapes | hits, none a secret: the F1 test's assertion on `password={TOKEN}`, the existing fake token; this section's environment line, which names `HD_API_KEY` and `GEO_API_KEY`; and this row, which names the patterns |

### Deviations and limits

- **PATH.** In this container `/nix/var/nix/profiles/default/bin` comes before `$HOME/.local/bin` on the inherited `PATH`. It holds no Python, so `python3.12` resolved to `$HOME/.local/bin` either way; every `env -i` command put `$HOME/.local/bin` first explicitly.
- **The push ran outside `env -i`.** Under `env -i` git cannot reach the session's GitHub proxy (`could not read Username`), so `git push -u origin claude/blissful-volta-coypr6` ran in the session's own environment. No credential was read or printed.
- **F1's control writes the fake token to a scratch log**: the recorder is handed `store` with the password, which is the harm the reset prevents. The log is in the test's temporary directory, removed at tear-down, and the token is the existing fake `TOKEN`.
- **Length:** this section takes the record from 184 to about 240 lines, past the 150-line target (step 5), because each pass keeps its own identity, checks and limits; nothing the re-review must know is cut.
- **F3's wording:** the restore command stays attached to the first sentence, and the in-flight case is its own sentence after it.
- **Limits:** F1's test ran here on git 2.43.0; on the runner it passed on git 2.55.0, which the API job's log shows [Corrected by the re-review's nit 2]. F2's test is loopback HTTP, not HTTPS against GitHub; the GitHub path stays unexercised before the first run on `main` (DM-32 1.10). F4 and F6 stay carried, as the review disposed.

### What the re-review must know

- The code head is `0274096`; `scripts/branch_cleanup.py`, both workflows, `scripts/change_scope.py` and its tests are byte-identical to `27ef2f6`, and the 16 existing tests are unchanged. The test file's diff is three imports and the two tests after the last existing one.
- Each new test fails with its guard reversed and passes with the real code; F1's has a control that fails if the recorder never runs.
- F3 and F5 change records only; no behaviour claim beyond the review's F3 and F5 is added.

## Manager verification of M04-C1 (26 October 2026, App Manager 8)

- **Scope:** `git diff --name-status e4045c8 ab38a80` lists the three owned paths, mode `100644`; `git diff --check` is clean. The code delta is `scripts/test_branch_cleanup.py` alone, 68 added lines; the script, both workflows, `change_scope.py` and its tests are byte-identical to `27ef2f6`.
- **The tests, read whole and run here** in scratch copies of `ab38a80` under `env -i`, `python3.12` 3.12.14: `test_branch_cleanup.py` 18 OK, `test_change_scope.py` OK. F1's reversal fails only F1's test; F2's fails only F2's. F1's control proves the recorder runs; F2's `served` assertion proves the request reached the server, so its `Refused` is the redirect's, not a connection failure's.
- **The runs, read with the GitHub tools:** 40347076599 on `0274096`, all eight jobs `success`, the gate `Application checks passed`, the API job `Ran 18 tests` with both new tests `ok`, then 14, 366 and 39; 40348682976 on `ab38a80`, the six application jobs `skipped` as documentation and the gate `success`.
- **Integration:** the manager branch fast-forwarded to `ab38a80`. The trusted policy from `85bbd4d` classifies PR36 full scope, 20 paths.
- **One cosmetic correction:** rows 1 and 5 of C1's checks table had the command and the result in one cell; the cells are split, words unchanged.

## Re-review of M04-C1 (26 October 2026)

- **The review:** Nathan ran [the re-review prompt](https://github.com/amthorn78/glow-dating-app/blob/4794d3e99012c348a0fb78d8a12a6e6d1cd20f8e/docs/ephemeral/2026-10-26-m04-c1-re-review-prompt.md), revision 1, at `968d8b0`, for code head `0274096`, relayed on 26 October. Nathan's pick: not yet recorded. Every start-gate check passed; the trusted policy from `85bbd4d` classified the PR full scope.
- **Verdict: approve.** F1, F2, F3 and F5 are closed; no blocking or should-fix finding; nothing in a correction class; every DM-32 condition still met, the script and workflows being unchanged.
- **What it checked:** both tests run the real code; F1's scoped helper is one git really consults for `github.com` (re-scoped to another host, the test fails); F1's recorder path is safe for a temporary directory holding quotes, `$`, `;` and backticks; F2's request stays on loopback with every proxy variable set to a dead proxy; no thread, file descriptor, temporary directory or environment change outlives either test, on the passing or the reversed path (`-X dev`).
- **Reversals:** F1's and F2's each fail only their own test. Of the reviewer's own, a recorder that writes nowhere, the reset placed after the script's helper, a server never reached, the proxy stripping removed, and a scoped helper on another host each fail.
- **Runs read:** 40347076599 on `0274096` and the PR run 40350388448 on `968d8b0`: all eight jobs `success`, `Application checks passed`, the cleanup suite `Ran 18 tests` with both new tests `ok`, on the runner's git 2.55.0; 40348682976 on `ab38a80`, documentation only.

| # | Finding | Disposition |
|---|---|---|
| 1 | Nit: F2's test asserts `Refused` without its reason; the `served` assertion already rules out a connection error | (b): a follow-up, in the carried-items file with F4 and F6 |
| 2 | Nit: C1's limits said the runner's git version was not read; the logs show 2.55.0 | Corrected in C1's section, marked |
| 3 | Nit: C1's F1 bullet said the log holds exactly four lines; it holds their input too, and the test compares the `run:` lines sorted | Corrected in C1's section, marked |

- **Limits it named:** the reversals ran on git 2.43.0, the runner shows only the passing direction; F2 is loopback HTTP, so the GitHub path waits for the first run on `main` (DM-32 1.10); `erase` is not tested separately, the same reset covering it.
- **Its open question,** for the Dev Manager's pre-merge read: F3's wording narrows DM-32 1.5's "written as it happens" to name the in-flight window. It is in DM-33.

## M04's merge receipt (26 October 2026)

- **PR36 merged** at 17:09 UTC on 26 October, by App Manager 8, under the standing app-only authorization. The merge commit is `4794d3e99012c348a0fb78d8a12a6e6d1cd20f8e`; its parents are `85bbd4d`, `main` before, and `9d1570ebbe1c2daa4b5da81a23670e02fc955456`, the final head, pinned with the merge's expected head. `main`'s tree equals the final head's (`git diff --quiet`).
- **The pre-merge checklist** (PR36's description):
  - **classification:** full scope from the trusted policy on `main` (`85bbd4d`), 23 paths, one merge base; the final head's code is byte-identical to `0274096`;
  - **the run:** PR run 40364422379 on `9d1570e` (event `pull_request`): all eight jobs `success`, the gate `Application checks passed`; both artifacts, 14 days;
  - **the reviews:** the exact-head review of `27ef2f6` and the re-review of M04-C1's `0274096` (sections above);
  - **Codex:** its code review of `9d1570e` completed with no finding;
  - **governing Markdown:** DM-33 (`8855163`, a read of `f4d7df5`) approved; no governing path changed after `f4d7df5`.
- **`main`'s push run** 40366011370: all eight jobs `success`. Mobile checks took 16 min 4 s of its 25 (the Chromium install 9 min 52 s, as in run 40029112295's 11 min 27 s), so the old 15-minute timeout would have stopped it (finding 11).
- **The first cleanup run, M04's run of record** (DM-32 1.10; acceptance check 5): run 40366011457, push on `4794d3e`, job "Delete merged branches" 17:09:48 to 17:10:02, `success`. It was the first test of the GitHub path: the token's write permission, the PR listing and the lease against GitHub. From the job's log, which carries every summary line:
  - mode **delete** (event `push`); `main` `4794d3e`; **open pull requests read: 0** (PR36 had just merged);
  - **deleted**, each "merged into main": `claude/blissful-volta-coypr6` (`ab38a80ca3692369c16882188e2376f6701c21e4`), `claude/laughing-meitner-ywjnk1` (`7f9e6e7aa224372f2a5a273c195f66230d1b4280`) and `claude/zen-thompson-5fdqqz` (`e27f7c7c02693bb1ed5223d9a0b06b3f67b40fd5`), exactly the three expected;
  - **kept**, keep-list: `claude/dev-manager` (`8855163`), `claude/magical-wozniak-yfmmx2` (`9d1570e`) and `main` (`4794d3e`);
  - the token appears in the log only as `***`; each row names the restore command's head.

  `git ls-remote --heads` afterwards lists the three kept branches only. The summary matches section 4's dry run, apart from what changed in between: M04-C1's branch, and PR35's and PR36's merges.
- **Pruned in this batch,** with their links pinned at `4794d3e`: M04's implementation, review, correction and re-review prompts, and the DM-32 and DM-33 consultations.
- **What stays open:** DM-33's branch-controls recommendation, to Nathan in OD-32's form; the follow-ups in the carried-items file (F4, F6, the re-review's nit 1, DM-33's log line and nit).

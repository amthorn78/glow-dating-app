# M04 — Branch hygiene: automatic cleanup of merged branches, with the CI hardening

- **Work ID:** M04 (cross-cutting).
- **Owner:** Nathan Amthor, by his direction of 5 October 2026 (OD-39); next in the order he resumed on 26 October (OD-49). **Manager:** App Manager 8. **Implementer:** one implementation session, started by Nathan.
- **Revision 1, 26 October 2026,** for the Dev Manager's read (DM-32).
- **Starting point:** `main` at `4aa66e2` (PR34), with the manager branch's Markdown records after it. The prompt names the exact commit.
- **Prompt:** written after DM-32, in `docs/ephemeral/`, for `Glow App - No Stream`.
- **Evidence home:** `docs/testing/evidence/<date>-m04-branch-hygiene.md`, written by the session; the prompt names the date.

## Why

Nathan, 5 October 2026 (OD-39), on the repository's 38 branches: *"I see a LOT of branches here, which is concerning."* Then: *"yes give me a prompt for option 1 to implement in App Manager 6"*. Option 1 is a small GitHub workflow that runs when a PR merges into `main`, and on demand. It deletes every branch whose commits are all in `main`, except `main`, the manager branch and the Dev Manager's branch, and never a branch with unmerged work. Until it exists, Nathan deletes merged branches by hand from the manager's list at each merge (manager workflow, step 7).

M05 and DM-31 add CI fixes that change the same workflow file, so they ride with it (DM-31 item 4):

- **Finding 10:** a newer run of the same ref does not stop an older run's jobs. The application jobs run under `always()`, so they finish, and the older run reads `cancelled` with every job passed (run 40162341984). Two governing texts describe this wrongly; DM-31 3.7 has M04 state them in final form.
- **Finding 11:** the Mobile job took 6 min 24 s of its 15 in run 40243775584, and one Chromium install took 11 min 27 s (run 40029112295).
- **Finding 14:** `actions/upload-artifact` is pinned at `ea165f8` (v4.6.2), which targets Node.js 20; v7.0.2 was the current release on 26 October.
- **Finding 12 (optional; recommended):** `scripts/change_scope.py` calls `git diff` without `--ignore-submodules=none`. A trusted base `.gitmodules` with `ignore = all` would hide a gitlink move (latent: the repository has no `.gitmodules`).

## Outcome

1. **A cleanup workflow** that deletes only fully merged branches, safely, with a summary of every branch it kept or deleted and why.
2. **The Foundation workflow hardened:** superseded runs stop; the Mobile job has margin; upload-artifact is current. With finding 12, the classifier ignores no submodule setting.
3. **The CI policy and the manager workflow** describe both workflows as they behave, including the texts DM-31 3.7 left for M04.
4. **Evidence:** selection tests, each with a reversal that fails it; the PR run on the exact head; a pre-merge dry run of the selection against the live branch list; then the first cleanup run on `main` as its run of record.

## Design

- **D1 — Its own workflow file,** `.github/workflows/branch-cleanup.yml`, so write permission never reaches the Foundation jobs.
- **D2 — Triggers:** `push` to `main`, which a merge makes, and `workflow_dispatch`. No `pull_request` or `pull_request_target` trigger, ever. The job runs only when `github.ref` is `refs/heads/main`, so a dispatch on another branch runs nothing.
- **D3 — Permissions:** `permissions: {}` at the top; the one job gets `contents: write` and `pull-requests: read`. It uses `GITHUB_TOKEN` alone and references no secret. Actions are pinned to full commit SHAs from the CI policy's table. The token reaches only the step that deletes, where that is practical. Otherwise the job runs nothing but `main`'s own reviewed script and `git`.
- **D4 — The selection rule** (a standard-library Python script, `scripts/branch_cleanup.py`, which runs no candidate code). It reads the remote's `refs/heads/*`, the current `main`, and the head and base branch of every open PR. A branch is deleted only when all of these hold:
  - its head commit is an ancestor of `main` (`git merge-base --is-ancestor`). A squash-merged branch therefore stays, as does any head the job cannot resolve;
  - it is not on the keep-list;
  - it is neither the head nor the base of an open PR. A same-named branch from a fork also keeps it;
  - its name came from the remote listing, and it is passed as an argument, never interpolated into a shell.
- **D5 — The keep-list is held on `main`,** in the script or in a non-Markdown file beside it, so a change to it is full scope: `main`, the manager branch `claude/magical-wozniak-yfmmx2` and `claude/dev-manager`, by name (DM-13 item 10; the manager and Dev Manager branches are always fully merged after integration).
- **D6 — Deletion only at the checked head.** Each deletion is conditional on the head the selection checked, using `git push --force-with-lease=refs/heads/<b>:<sha> origin :refs/heads/<b>` or an equivalent precondition. A push in between leaves the branch. Deleting a merged branch loses no commit. The summary records each deleted branch's head, so `git push origin <sha>:refs/heads/<name>` restores it.
- **D7 — Fail closed.** If listing open PRs, reading the remote or resolving `main` fails, nothing is deleted and the run fails. A concurrency group queues runs; it never cancels them.
- **D8 — Dry run and summary.** `workflow_dispatch` takes a `dry_run` input that defaults to true. The push run deletes. Every run writes a job summary with one row per branch: name, head, decision (deleted, kept, would delete), and reason (keep-list, open PR, unmerged, unresolvable).
- **D9 — The Foundation changes:**
  - `!cancelled() && (…)` replaces `always() && (…)` on the six application jobs, and the gate keeps `always()` (finding 10);
  - the Mobile job's timeout gets measured margin, 25 minutes unless the session's measurements argue otherwise, with no cache action added (finding 11);
  - upload-artifact moves to its current release, with its commit resolved by `git ls-remote`, and its release notes checked for the inputs used (finding 14);
  - the API job's candidate-policy step also runs `scripts/test_branch_cleanup.py`;
  - with finding 12, `change_scope.py`'s `git diff` adds `--ignore-submodules=none`, with a test: a trusted base `.gitmodules` set to `ignore = all`, plus a gitlink move and a docs edit, classifies full scope, and the reverted flag fails the test.
- **Considered and not chosen:**
  - GitHub's "automatically delete head branches" setting. Session branches are integrated by fast-forward, not merged as PR heads, so it would not delete them, and it would delete the manager branch at each PR merge.
  - A manual list at each merge (OD-39's option 2). Nathan did not choose it.

## Questions for the Dev Manager (DM-32)

1. **The first run.** Recommended: the push run at M04's merge deletes for real. The protections are the tests, the pre-merge dry run, the lease and recoverability. The alternative is to ship with push runs in dry-run mode, read one summary on `main`, then flip deletion on in a second small full-scope PR, at the cost of one more review cycle.
2. **The push filter** (AM7-02; the P06.2 brief's B2-C2 point vi). A harness-named session branch (`ccr-…`) starts no Foundation run, so its run of record waits for the manager's integration.
   - Recommended: add `'ccr-**'` to the push filter.
   - The cost is more runs. The Actions minutes quota for this private repository and its use were not checked from a session.
3. **Finding 12 in M04** (recommended): it makes M04 a classification-policy change too, under the rules in `AGENTS.md`. **Finding 13** (the pin test misses `proofs/stream-chat/package.json`): recommended for P06.2-T, which changes `services/api` anyway, not M04.

## Owned paths (the implementation session's)

- **New:** `.github/workflows/branch-cleanup.yml`, `scripts/branch_cleanup.py`, `scripts/test_branch_cleanup.py`.
- **Changed:**
  - `.github/workflows/foundation.yml`, for D9 and question 2's answer;
  - with finding 12, `scripts/change_scope.py` and `scripts/test_change_scope.py`;
  - `docs/operations/ci-and-branch-policy.md`;
  - its evidence record.
- **The CI policy's changes:**
  - the cleanup workflow, with its write permission named as the one exception to "read-only contents permissions";
  - the trust limit for it;
  - the cancel paragraph and the upload-artifact row in final form (DM-31 3.7; M05's P-9 as their starting text);
  - the push filter, if it changes.

## Manager-owned

This brief and the prompt; the manager workflow's step 5 push-run sentence, in final form (DM-31 3.7; M05's P-7 as its starting text), and step 7's "Report the branch state", which reads the cleanup run's summary once M04's first run of record holds; the handoff, the register, the review log and Notion.

## Exclusions

- No other branch, tag, ruleset, repository setting or secret is created or changed.
- No `pull_request_target` workflow.
- No deletion from a session: the session's dry run only reads.
- No HDE repository or resource.
- No other code change; finding 13 and E15's refusal lists stay with P06.2-T.

## Dependencies and inputs

OD-39 and OD-49; DM-13 item 10; DM-31 items 3.7 and 4; M05 findings 10 to 14; AM7-02; the current Foundation workflow, classifier and CI policy. No credential is needed. The session's GitHub tools read the open PRs for the dry run. `git ls-remote` resolves the upload-artifact commit; M05's session did so from `Glow App - No Stream`.

## Acceptance checks

1. The cleanup workflow's text shows D1 to D3 and D8: its triggers, the `main`-only condition, the permissions, no `secrets.` reference, and full-SHA pins.
2. **Selection tests,** each with a recorded reversal that fails it. They run on a temporary repository with a bare remote:
   - a merged branch is selected;
   - an unmerged branch is kept;
   - each keep-list name is kept while merged;
   - the head and the base of an open PR are kept;
   - a branch moved after selection is kept, because the lease is refused;
   - an unresolvable head is kept;
   - a failed PR listing deletes nothing;
   - a dry run deletes nothing and selects the same set;
   - a name with shell metacharacters is handled as data.
3. **Foundation:**
   - the PR run on the exact head passes every job and prints `Application checks passed`;
   - two quick pushes to the session's branch show the earlier run's application jobs `cancelled`, with the newer run's gate as the result;
   - the Mobile job's duration and timeout are recorded;
   - the new upload-artifact pin's release and commit are recorded;
   - with finding 12, the submodule test and its reversal are recorded.
4. **A pre-merge dry run** of the selection, at the session's head, against the live `git ls-remote` listing and the open PRs from its GitHub tools. It lists each branch with its decision.
5. **After the merge** (manager): the first cleanup run on `main` is M04's run of record. Its summary matches the dry run, apart from changes in between, and `git ls-remote` afterwards shows only kept branches. A wrong deletion is restored from the summary's head, and the workflow is disabled until a fix merges.
6. `git diff --check` is clean. The offline checks the session runs are recorded with their exact results, and any check not run is named with its reason.

## Classification expectation

Full scope: a workflow, scripts and tests. The manager classifies with the trusted base policy from `main`, which is pre-change for finding 12, run as `python3 -I … --base --head --merge-base`. It reads the complete diff of both workflows and the actual job steps and results. A green or skipped check alone is not acceptance (`AGENTS.md`; the CI policy, "Trust limit and manager control").

## Review plan

- **DM-32 reads this brief before the prompt** (the charter: a new component with write permission that deletes branches, and a CI and review-policy change).
- **Then:**
  1. the implementation session;
  2. the manager's verification and integration;
  3. Codex's review of the code head;
  4. an exact-head code and security review that Nathan runs. Its focus is the selection rule, the triggers and permissions, the lease, injection, and the classifier change;
  5. Codex on the final head;
  6. the Dev Manager's read of the CI policy and manager workflow changes before the merge.
- **After the merge:** the first cleanup run is recorded in the merge receipt.

## Sessions

- **Revision 1** (26 October 2026): to the Dev Manager as DM-32.

# M04 — Branch hygiene: automatic cleanup of merged branches, with the CI hardening

- **Work ID:** M04 (cross-cutting).
- **Owner:** Nathan Amthor, by his direction of 5 October 2026 (OD-39); next in the order he resumed on 26 October (OD-49). **Manager:** App Manager 8. **Implementer:** one implementation session, started by Nathan.
- **Revision 3, 26 October 2026:** revision 2 applied DM-32's conditions 1.1 to 1.16 ([report](../continuity/dev-manager/reviews/2026-10-26-dm-32-m04-brief.md)); revision 3 adds `'ccr-**'` to the push filter and corrects the records that say private, after Nathan kept the repository public for now, for budget reasons (OD-51). Revision 1 went to the Dev Manager as DM-32.
- **Starting point:** `main` at `4aa66e2` (PR34), with the manager branch's Markdown records after it. The prompt names the exact commit.
- **Prompt:** [`docs/ephemeral/2026-10-26-m04-implementation-prompt.md`](../ephemeral/2026-10-26-m04-implementation-prompt.md), revision 1, for `Glow App - No Stream`.
- **Evidence home:** `docs/testing/evidence/2026-10-26-m04-branch-hygiene.md`, written by the session.

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
- **D3 — Permissions:** `permissions: {}` at the top; the one job gets `contents: write` and `pull-requests: read`, and a bounded `timeout-minutes`. It uses `GITHUB_TOKEN` alone and references no secret. Actions are pinned to full commit SHAs from the CI policy's table. **The token's reach** (DM-32 1.1):
  - checkout keeps `persist-credentials: false`;
  - only the step that runs the script has `GITHUB_TOKEN` in its environment, for the PR listing and the deletions;
  - the script never prints the token, and never writes it to disk or to git config.
- **D4 — The selection rule** (a standard-library Python script, `scripts/branch_cleanup.py`, which runs no candidate code). It reads the remote's `refs/heads/*`, the current `main`, and the head and base branch of every open PR. A branch is deleted only when all of these hold:
  - its head commit is an ancestor of `main` (`git merge-base --is-ancestor`). A squash-merged branch therefore stays, as does any head the job cannot resolve;
  - it is not on the keep-list;
  - it is neither the head nor the base of an open PR. A same-named branch from a fork also keeps it. **The listing is complete** (DM-32 1.3): it reads every page and fails closed on any error, and the summary lists the open PRs it read (number, head and base);
  - its name came from the remote listing, and it is passed as an argument, never interpolated into a shell.
  - **The fresh-branch case** (DM-32 1.4): a branch whose head is a commit of `main` counts as merged, so a session branch pushed at its start commit, before any work, is deleted at the next merge once that commit is in `main`. Its next push re-creates it. The CI policy says so, so that sessions and managers do not read it as a fault.
- **D5 — The keep-list is held on `main`,** in the script or in a non-Markdown file beside it, so a change to it is full scope: `main`, the manager branch `claude/magical-wozniak-yfmmx2` and `claude/dev-manager`, by name (DM-13 item 10; the manager and Dev Manager branches are always fully merged after integration).
- **D6 — Deletion only at the checked head.** Each deletion is conditional on the head the selection checked, using `git push --force-with-lease=refs/heads/<b>:<sha> origin :refs/heads/<b>` or an equivalent precondition. A push in between leaves the branch. Deleting a merged branch loses no commit. **The summary is the restore record** (DM-32 1.5): each deletion's row, with its head, is written as it happens, so a run that fails midway still names every head it deleted, and `git push origin <sha>:refs/heads/<name>` restores it [M04's review, F3: a run killed while a push is in flight may leave that one deletion unrecorded; its commits are in `main`]. The summary escapes branch names, as data.
- **D7 — Fail closed.** If listing open PRs, reading the remote or resolving `main` fails, nothing is deleted and the run fails. A concurrency group with `cancel-in-progress: false` never cancels a running run, but a newer pending run replaces an older pending one, as GitHub documents; the CI policy says so (DM-32 1.6).
- **D8 — Dry run and summary.** The event sets the mode (DM-32 1.7): a push deletes. `workflow_dispatch` takes a `boolean` `dry_run` input that defaults to true, passed to the script through `env:`, never through `${{ }}` inside `run:`; on a dispatch, any value but an exact `false` means a dry run. Every run writes a job summary with one row per branch: name, head, decision (deleted, kept, would delete), and reason (keep-list, open PR, unmerged, unresolvable).
- **D9 — The Foundation changes:**
  - `!cancelled() && (…)` replaces `always() && (…)` on the six application jobs, and the gate keeps `always()` (finding 10);
  - the Mobile job's timeout gets measured margin, 25 minutes unless the session's measurements argue otherwise, with no cache action added (finding 11);
  - upload-artifact moves to its current release, with its commit resolved by `git ls-remote`, and its release notes checked for the inputs used (finding 14);
  - the API job's candidate-policy step also runs `scripts/test_branch_cleanup.py`;
  - the push filter adds `'ccr-**'`, so a harness-named session branch starts a run (AM7-02; OD-51);
  - with finding 12, `change_scope.py`'s `git diff` adds `--ignore-submodules=none`, with a test: a trusted base `.gitmodules` set to `ignore = all`, plus a gitlink move and a docs edit, classifies full scope, and the reverted flag fails the test.
- **Considered and not chosen:**
  - GitHub's "automatically delete head branches" setting. Session branches are integrated by fast-forward, not merged as PR heads, so it would not delete them, and it would delete the manager branch at each PR merge.
  - A manual list at each merge (OD-39's option 2). Nathan did not choose it.

## The Dev Manager's answers (DM-32)

1. **The first run deletes for real** (approved, with 1.10). M04's merge receipt names the expected deletions in advance, and says that the first run is the first test of the workflow's GitHub path: the token's write permission, the PR listing and the lease against GitHub. No pre-merge check reaches that path, since the job runs only on `main`.
2. **The push filter adds `'ccr-**'`.** DM-32 approved it only while the repository stays public (3.4), and Nathan keeps it public for now, for budget reasons; he intends to make it private again (OD-51). Actions minutes on standard runners are free for public repositories (GitHub's documentation, read on 26 October 2026). When it goes private, `'ccr-**'` comes out or he approves its minutes.
3. **Finding 12 is in M04** (approved). **Finding 13 goes to P06.2-T** (1.11): the test is in the carried-items file's "Carried to P06.2-T" and its row, and the bootstrap script's wording stays with the hardening item in the [M02 brief](claude-setup-optimization.md), since a Setup-script change needs Nathan to paste it.

## Owned paths (the implementation session's)

- **New:** `.github/workflows/branch-cleanup.yml`, `scripts/branch_cleanup.py`, `scripts/test_branch_cleanup.py`.
- **Changed:**
  - `.github/workflows/foundation.yml`, for D9 and question 2's answer;
  - with finding 12, `scripts/change_scope.py` and `scripts/test_change_scope.py`;
  - `docs/operations/ci-and-branch-policy.md`;
  - its evidence record.
- **The CI policy's changes:**
  - the cleanup workflow, with its write permission named as the one exception to "read-only contents permissions";
  - **the trust limit** (DM-32 1.2): the `main`-only condition stops an accidental dispatch, but not a branch's own edited copy. A branch that adds or edits a workflow can run it, on push or on dispatch, with the permissions it declares, and a merged change to the cleanup workflow or its script acts at its own merge. The protection is the review of workflow changes (`AGENTS.md`);
  - the fresh-branch case (D4) and the concurrency wording (D7);
  - the cancel paragraph and the upload-artifact row in final form (DM-31 3.7; M05's P-9 as their starting text). They say, after D9 (DM-32 1.13): a newer run of the same ref cancels an earlier run's application jobs; the earlier run's gate still runs and fails, and that run is not evidence; so a push before a code run finishes discards that run;
  - the push filter's `'ccr-**'`, and that it is removed, or its minutes approved, when the repository goes private again (OD-51; DM-32 3.4);
  - **the public repository** (OD-51): the "Branch enforcement limitation" section and the Dependabot bullet say that the repository is public for now, for budget reasons, and that Nathan intends to make it private again; that while it is public, protected branches and rulesets are available at no cost (GitHub's documentation, read on 26 October 2026) and none is configured; and that the procedural substitutes stay in force until Nathan decides which controls to use, and after it is private again. The 23 September observation stays, as history.

## Manager-owned

This brief and the prompt; in the manager workflow (all for the Dev Manager's pre-merge read):

- step 5's push-run sentence, in final form (DM-31 3.7; M05's P-7 as its starting text). It states the rule and cites the CI policy for the mechanism, without restating it (DM-32 1.12);
- step 3's "Say when a session may push again" (AM5-04, AM5-14), which describes the old mechanism; after D9 that rule is what saves a run of record (DM-32 1.14);
- step 7's "Report the branch state", which reads the cleanup run's summary once M04's first run of record holds, and its line "Branch protection is not enforceable on this repository", corrected as the CI policy is (OD-51).

Also the handoff, the register, the review log and Notion.

## Exclusions

- No other branch, tag, ruleset, repository setting or secret is created or changed.
- No `pull_request_target` workflow.
- No deletion from a session: the session's dry run only reads.
- No HDE repository or resource.
- No other code change; finding 13 and E15's refusal lists stay with P06.2-T.

## Dependencies and inputs

OD-39, OD-49 and OD-51; DM-13 item 10; DM-31 items 3.7 and 4; M05 findings 10 to 14; AM7-02; the current Foundation workflow, classifier and CI policy. No credential is needed. The session's GitHub tools read the open PRs for the dry run. `git ls-remote` resolves the upload-artifact commit; M05's session did so from `Glow App - No Stream`.

## Acceptance checks

1. The cleanup workflow's text shows D1 to D3 and D8: its triggers, the `main`-only condition, the permissions, the job's `timeout-minutes` (DM-32 1.8), `persist-credentials: false`, the token in one step's environment, the dispatch input through `env:`, no `secrets.` reference, and full-SHA pins.
2. **Selection tests,** each with a recorded reversal that fails it. They run on a temporary repository with a bare remote:
   - a merged branch is selected;
   - an unmerged branch is kept;
   - each keep-list name is kept while merged;
   - the head and the base of an open PR are kept;
   - a branch moved after selection is kept, because the lease is refused;
   - an unresolvable head is kept;
   - a failed PR listing deletes nothing, and a two-page listing is read whole (DM-32 1.3);
   - a run that fails midway has already written each deletion's row (DM-32 1.5);
   - on a dispatch, any `dry_run` value but an exact `false` is a dry run (DM-32 1.7);
   - a dry run deletes nothing and selects the same set;
   - a name with shell metacharacters is handled as data.
3. **Foundation:**
   - the PR run on the exact head passes every job and prints `Application checks passed`;
   - the PR run's artifacts list shows `p04-empty-form-layout` and `p06-db-proof-results`, with their names and retention, since both uploads use `if-no-files-found: ignore` and the pin moves from v4 (DM-32 1.9);
   - two quick pushes to a branch the push filter covers show the earlier run's application jobs `cancelled` and its gate failed, with the newer run as the result. The prompt checks the session's branch name, or the manager runs the test after integration; the session runs it before its final code push, then waits for that push's run (DM-32 1.15);
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
  4. an exact-head code and security review that Nathan runs. Its focus is the selection rule, the triggers and permissions, the lease, injection, and the classifier change. It carries a short written threat model: the token's reach, a branch's own copy of the workflow, injection through names and inputs, the listing's completeness, and races (DM-32 1.16; Codex's security reviews are no longer available, OD-41);
  5. Codex on the final head;
  6. the Dev Manager's read of the CI policy and manager workflow changes before the merge.
- **After the merge:** the first cleanup run is recorded in the merge receipt, against the expected deletions it named (DM-32 1.10).

## Sessions

- **Revision 1** (26 October 2026): to the Dev Manager as DM-32 (`515bd72`).
- **DM-32** (26 October 2026; report `3abbc81`): approved with conditions 1.1 to 1.16, all accepted and applied as **revision 2**, which needs no further read (DM-03 G2). The push filter's `'ccr-**'` waited on Nathan's answer on the repository's visibility (DM-32 3.4).
- **Revision 3** (26 October 2026): Nathan keeps the repository public for now, for budget reasons, and intends to make it private again (OD-51), so the push filter adds `'ccr-**'` and the records that say private are corrected. It applies his decision and DM-32 3.4's conditional approval, so it needs no further read.
- **The implementation prompt, revision 1** (26 October 2026; its TypeSafe reading is in its header and the uses table): given to Nathan. The records since PR34 merge first as their own docs-only PR, so that M04's PR carries M04 alone (DM-31 item 4).
- **The implementation** (26 October 2026): branch `claude/laughing-meitner-ywjnk1`, code head `27ef2f6`, records `7f9e6e7`. All eight items done. Run of record 40270021713 on `27ef2f6`: all eight jobs passed and the gate printed `Application checks passed`; Mobile 6 min 32 s of 25; both artifacts present. The cancel test (runs 40269750327 and 40269779556) showed a newer run cancelling the earlier run's application jobs 71 to 77 s late, not at once, and the CI policy says so. The dry run's one expected deletion is `claude/zen-thompson-5fdqqz`, with the session's branch once it is in `main`. Nathan's pick: not recorded. The manager verified it against the pushed branch, its own seven reversals included; one found a coverage gap, the empty credential-helper reset untested (V1). Its section "Manager verification of M04" lands with the integration, which waits until PR35, the records since PR34, has merged.
- **The integration** (26 October 2026): PR35 merged as `85bbd4d`; the session branch was merged into the manager branch as `39b6141`, byte-identical to `7f9e6e7` on the 8 paths, with "Manager verification of M04" in the record. The manager's V2 to V4 and V6 records joined it: the CI policy's opening line and the start prompts (OD-51); steps 3, 5 and 7 (DM-32 1.12 to 1.14); the handover checklist's and the next-manager start prompt's keep-list lines; the environment inventory's token names. Next: M04's PR, Codex on its head, the exact-head review with its threat model (DM-32 1.16) and V1, then the Dev Manager's pre-merge read.
- **The exact-head review** (26 October 2026; prompt revision 1 at `55fc64a`, code head `27ef2f6`): changes required, for F1 (V1, the helper reset) and F2 (the redirect refusal), two guards no test fails without; no blocking finding, and every DM-32 condition met. F3 and F5 are record wording; F4 and F6 are follow-ups in the carried-items file; V5 is carried. The correction pass **M04-C1** adds the two tests with their reversals and makes F3's and F5's wording exact; its [prompt](../ephemeral/2026-10-26-m04-c1-correction-prompt.md) follows Codex on the commit that holds it. Then a re-review of C1's delta, Codex on the final head and the Dev Manager's pre-merge read.
- **M04-C1** (26 October 2026; branch `claude/blissful-volta-coypr6`, code head `0274096`, records `ab38a80`): the two tests, each failing with its guard reversed, and F3's and F5's sentences made exact. Run of record 40347076599: all eight jobs passed, 18 cleanup tests. Nathan's pick: not recorded. Verified and fast-forwarded into the manager branch. Next: the [re-review of C1's delta](../ephemeral/2026-10-26-m04-c1-re-review-prompt.md), after Codex on the commit that holds it.

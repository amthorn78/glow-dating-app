# Current handoff — App Manager 2 (M02 in progress)

**Process: manual relay** (Nathan, 24 September 2026).

- The manager gives Nathan prompts for implementers. Nathan runs each implementation or review session himself and relays its findings back. The manager follows up as needed.
- Nathan reinitiates managers manually.
- The manager never starts implementation or review work itself (no subagents or remote-session tools for that work).
- Implementation and review sessions may use any tools, subagents or wake-ups they need.

The full procedure is in [manager workflow](../planning/manager-workflow.md). Nathan remains product and account owner. Feature work stays paused; P06.1 is not dispatched.

## Status — App Manager 2, 24 September 2026

**Where M02 stands.** M02-I1 is integrated, and the exact-head review of `ccebd1b` returned **approve for merge, with nothing blocking**. App Manager 2 is fixing every finding except a workflow change before merge, in **correction round M02-C1**, which is commissioned and waiting for Nathan's relay. After it comes a delta review of the final head against `ccebd1b`, then the merge. The details are in the evidence record's App Manager 2 sections and in the brief's disposition table.

- **Environment (names only).** No HDE variables; the three `STREAM_*` names are present; the Setup script produced the pinned toolchain. Nathan added the TypeSafe API credential on 24 September.
- **PR.** M02 is on `claude/fervent-darwin-idyko3`, [draft PR18](https://github.com/amthorn78/glow-dating-app/pull/18). It replaced [PR17](https://github.com/amthorn78/glow-dating-app/pull/17), which is closed with a link.
- **M02-I1.** Session head `3a0726d` was verified and fast-forwarded in, and it is recorded in the evidence.
- **Review of `ccebd1b`** (at the extra-high level): CI passed 6/6 on both the push and the PR run.
  - Six findings are should-fix: symlink trust bypass, ruff reading Markdown, a single merge base, push-run cancellation, stale lines, pin-test false passes.
  - One is residual risk: `.claude/**` was exempt.
  - The rest are nits.
- **Decisions and policy (Nathan, 24 September):**
  - **One work item at a time.** No new work item starts until the current item's CI and review are clear. Corrections and re-reviews belong to the current item. This is recorded in root `AGENTS.md`, the manager workflow and Notion.
  - **`.claude/**` stays full scope.** The M02-C1 classifier enforces this once M02 merges, and the documents already say so.
  - **Branch and PR discretion:** *"I will trust you to manage the branches and PRs as you see fit."*
- **Setup script.** Nathan pastes the final `scripts/bootstrap-toolchain.sh` into the `Glow app` Setup script **once, after M02 merges**. Until then, new sessions keep the old script's uid-1000 Node tree, which the new script replaces on its first run.
- **Reasoning levels.** Each prompt gets the manager's level and the TypeSafe effort scorer v4 reading; the Notion page *TypeSafe effort scorer — Glow app usage log* tracks them, and the procedure is step 3 of the [manager workflow](../planning/manager-workflow.md).
  - M02-I1: manager high, TypeSafe extra high. Nathan ran extra high; the outcome was adequate, with TypeSafe the better call.
  - Review: manager extra high, TypeSafe high. Nathan ran extra high; the outcome was adequate, with the manager the better call.
- **Queued behind M02:** the rendered-test diagnosis and the stale-documentation sweep. Three intermittent rendered failures of one kind have occurred, a form submit that does not advance. The manager's GitHub integration cannot re-run Actions jobs (403), so Nathan re-runs them when needed.

## State at handover

App Manager 1 was the first Claude manager. It ran in the environment shared with HDE, which injects `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` and `PORT` (names observed; values never read).

- **main:** `07b3b10720ddd333ada807a56595f369263714fe` (PR16). The application behavior baseline is unchanged since PR14 (`ea39454…`). P01–P05 are complete only at fixture scope. [Migration receipt](migration-publication.md).
- **M02 (Claude setup optimization):** in progress on branch `claude/ecstatic-goodall-qajdh4`, [draft PR17](https://github.com/amthorn78/glow-dating-app/pull/17). PR18 has since replaced it; see the status above.
  - **Brief:** [claude-setup-optimization](../planning/claude-setup-optimization.md). **Evidence:** [M02 evidence record](../testing/evidence/2026-09-24-m02-claude-setup.md).
  - **Done by App Manager 1 (reviewed with the PR):** repository review, the proposal, a verified baseline (all local checks pass on the pinned toolchain in a clean process environment), `scripts/bootstrap-toolchain.sh` (tested; this is the dedicated environment's Setup script), and the manual-relay procedure in `CLAUDE.md`, `AGENTS.md`, the manager workflow, PF00 1.4 and PF01 1.5 (D09).
  - **CI/review policy (Nathan, 24 September):** any change made only of Markdown files skips application CI and code/security review. Scripts and other non-Markdown files stay full scope. This applies to later PRs once M02 merges, because CI loads the classifier from `main`. M02 itself contains scripts, so it stays full scope.
  - **Remaining:** implementation item M02-I1 (brief section "Implementation brief — M02-I1"; prompt in `docs/ephemeral/2026-09-24-m02-implementation-prompt.md`). Then review, CI, merge, receipt, this handoff and Notion.
- **Dedicated app cloud environment `Glow app`:** Nathan created it with the settings recorded in the [environment inventory](../operations/environment-inventory.md#claude-cloud-environment-glow-app-nathans-settings-24-september-2026). App Manager 2 is the first session in it and verified it (see the status above). The environment also provides Nathan's **development** Stream application:
  - `STREAM_APP_ID=1729640`
  - `STREAM_API_KEY=qdstwyevnyea`
  - `STREAM_API_SECRET` (secret; name only; never print or record it)

  No code reads these yet; P06.1 will. A session's environment is fixed at start, so switching environments requires a new session.

## App Manager 2 — next actions

**Progress (24 September):** 1 to 3 are done. For 4, the review of `ccebd1b` approved with findings, and correction round M02-C1 is commissioned; a delta review follows it.

1. **Verify the environment (names only).** None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` should be present. `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` should be present. `command -v node npm python3.12` should resolve to `$HOME/.local/bin`, with `node --version` v24.19.0, `npm --version` 11.9.0 and `python3.12 --version` 3.12.14. If anything differs, tell Nathan exactly which setting to fix. Never print values.
2. **Verify the repository.** Check main, open PRs and the worktree. Run `git fetch origin claude/ecstatic-goodall-qajdh4` and review its head and PR17's CI runs. A session can push only its own working branch, so:
   - fast-forward your branch to that head (`git merge --ff-only`) and push it;
   - open a replacement draft PR (M02);
   - close PR17 with a link to the replacement.
3. **Commission M02-I1.** Put your branch's head SHA into the prompt's start gate and give Nathan the M02-I1 prompt to paste into a new implementation session in the same environment. When Nathan relays the report:
   - verify it against the pushed branch;
   - classify the change with trusted base policy;
   - integrate the branch and push;
   - check the actual CI job steps.
4. **Review.** Write a bounded code/security review prompt for the exact final head. Nathan runs it in a separate session and relays the findings. Send corrections back through prompts; every new head needs its own checks and review.
5. **Merge and close.** Merge after all six Foundation jobs pass and review is clean. Then:
   - verify main;
   - record an ordinary-documentation receipt in `docs/testing/evidence/`;
   - update this handoff;
   - sync Notion (Implementation Control, Work Register M02 row, D09 row);
   - prune closed prompts.
6. **Propose, don't dispatch.** Then propose to Nathan whether to prepare P06.1. It needs Stream access, plan and budget, a secret-injection decision, and chat-history policy.

**Open review item.** App Manager 1 read the core governance, operations, setup, CI, handoff and planning documents and the configuration code. Its helper sweep of the remaining `docs/architecture/`, `docs/testing/` and other `docs/operations/` files, looking for stale statements, was stopped before reporting and produced no findings. Include that sweep in a prompt if it is still wanted. App Manager 2 left it out of M02-I1. It recommends a separate sweep after M02 merges, when a Markdown-only change skips application CI and review.

## Accepted baseline and limits

The app has fixture onboarding/profiles/media, eligibility/discovery and interactions, an API smoke runtime, contracts and static model/migration definitions. Not established:

- real authentication or persistence;
- Stream or HDE calls;
- provider delivery;
- a signed native build;
- release readiness.

Readiness stays 503, provider sending stays unavailable, and database integration stays with P11. The [database audit](../planning/database-audit-2026-09-23.md) is dated evidence, not permission to connect. HDE and shared infrastructure remain protected by effect. Stream remains preferred; secret slots are future definitions, not loaders. Outstanding owner inputs are in the [Claude handoff](claude-code-handoff.md#prioritized-inputs-nathan-must-supply).

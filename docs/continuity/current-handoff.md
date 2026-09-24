# Current handoff — App Manager 2 (M02 in progress)

**Process: manual relay** (Nathan, 24 September 2026).

- The manager gives Nathan prompts for implementers. Nathan runs each implementation or review session himself and relays its findings back. The manager follows up as needed.
- Nathan reinitiates managers manually.
- The manager never starts implementation or review work itself (no subagents or remote-session tools for that work).
- Implementation and review sessions may use any tools, subagents or wake-ups they need.

The full procedure is in [manager workflow](../planning/manager-workflow.md). Nathan remains product and account owner. Feature work stays paused; P06.1 is not dispatched.

## Status — App Manager 2, 24 September 2026

App Manager 2 is the first session in the `Glow app` environment. Next actions 1–3 are done: M02-I1 ran, was verified and is integrated. **The exact-head code and security review (next action 4) is commissioned and waiting for Nathan's relay.** The details are in the evidence record's App Manager 2 sections ([start verification](../testing/evidence/2026-09-24-m02-claude-setup.md#app-manager-2--start-verification-24-september-2026) and [M02-I1 verification and integration](../testing/evidence/2026-09-24-m02-claude-setup.md#app-manager-2--m02-i1-verification-and-integration-24-september-2026)).

- **Environment (names only).** No HDE variables; the three `STREAM_*` names are present; the Setup script produced the pinned toolchain. Nathan added the TypeSafe API credential on 24 September, and `api.typesafe.ai` answers in running sessions.
- **M02 is on `claude/fervent-darwin-idyko3`, [draft PR18](https://github.com/amthorn78/glow-dating-app/pull/18).** It replaced [PR17](https://github.com/amthorn78/glow-dating-app/pull/17) at head `a335c4f`; PR17 is closed with a link.
- **M02-I1 is integrated.**
  - The session branch is `claude/eager-goodall-1zjgey`, head `3a0726d47248e40d9462d0dbb5ffc34f08ab4c5f`: five commits from the start SHA `9280bdc`. It was fast-forwarded into the manager branch.
  - Verification:
    - the complete diff was read;
    - the 13 files are within the owned paths, apart from one disclosed, accepted one-line `apps/mobile/README.md` edit;
    - classification is full scope (24 paths);
    - hosted push run 36030512434 passed 6/6, read job by job;
    - the manager re-ran `bash -n`, the pin test (3/3) and the classifier tests (9/9).
  - **The Setup script changed.** Nathan pastes the new `scripts/bootstrap-toolchain.sh` into the `Glow app` Setup script **after the review passes and M02 merges**, not before. Until then, new sessions still get the old script's uid-1000 Node tree. The new script replaces that tree the first time it runs.
- **Review commissioned** for the head that carries this handoff revision; the review prompt names the exact SHA. Any correction produces a new head, which needs its own CI and review.
- **Reasoning levels (Nathan, 24 September).**
  - Every prompt gets two readings: the manager's level and the TypeSafe effort scorer v4 reading. They are tracked in the Notion page *TypeSafe effort scorer — Glow app usage log*; the procedure is step 3 of the [manager workflow](../planning/manager-workflow.md).
  - M02-I1: the manager said high and TypeSafe said extra high. Nathan ran extra high, and the outcome was adequate.
- **Branch and PR discretion (Nathan, 24 September):** *"I will trust you to manage the branches and PRs as you see fit."* This is recorded in the manager workflow, with the merge gates unchanged.
- **Recurring intermittent rendered failure (outside M02 scope).**
  - There are three occurrences of one kind: a form submit that does not advance to the next screen.
    - `state-corrections.spec.ts:45` failed on PR14's first attempt and on PR17's run 36020836838.
    - `onboarding.spec.ts:103` failed on PR18's push run 36025919795, on `9280bdc`. The PR run for that same head passed 6/6.
  - The root cause is unknown, and it is not infrastructure.
  - The manager's GitHub integration cannot re-run Actions jobs (403). When a re-run is warranted, the manager says so and Nathan uses "Re-run failed jobs" on the run page.
  - A bounded diagnosis item is proposed for after M02 merges; it is not dispatched.

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

**Progress (24 September):** 1 to 3 are done; M02-I1 is verified and integrated. 4 is commissioned: the review prompt is with Nathan.

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

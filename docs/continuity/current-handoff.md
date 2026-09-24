# Current handoff — App Manager 2 (M02 in progress)

**Process: manual relay** (Nathan, 24 September 2026).

- The manager gives Nathan prompts for implementers. Nathan runs each implementation or review session himself and relays its findings back. The manager follows up as needed.
- Nathan reinitiates managers manually.
- The manager never starts implementation or review work itself (no subagents or remote-session tools for that work).
- Implementation and review sessions may use any tools, subagents or wake-ups they need.

The full procedure is in [manager workflow](../planning/manager-workflow.md). Nathan remains product and account owner. Feature work stays paused; P06.1 is not dispatched.

## State at handover

App Manager 1 was the first Claude manager. It ran in the environment shared with HDE, which injects `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` and `PORT` (names observed; values never read).

- **main:** `07b3b10720ddd333ada807a56595f369263714fe` (PR16). The application behavior baseline is unchanged since PR14 (`ea39454…`). P01–P05 are complete only at fixture scope. [Migration receipt](migration-publication.md).
- **M02 (Claude setup optimization):** in progress on branch `claude/ecstatic-goodall-qajdh4`, [draft PR17](https://github.com/amthorn78/glow-dating-app/pull/17).
  - **Brief:** [claude-setup-optimization](../planning/claude-setup-optimization.md). **Evidence:** [M02 evidence record](../testing/evidence/2026-09-24-m02-claude-setup.md).
  - **Done by App Manager 1 (reviewed with the PR):** repository review, the proposal, a verified baseline (all local checks pass on the pinned toolchain in a clean process environment), `scripts/bootstrap-toolchain.sh` (tested; this is the dedicated environment's Setup script), and the manual-relay procedure in `CLAUDE.md`, `AGENTS.md`, the manager workflow, PF00 1.4 and PF01 1.5 (D09).
  - **Remaining:** implementation item M02-I1 (brief section "Implementation brief — M02-I1"; prompt in `docs/ephemeral/2026-09-24-m02-implementation-prompt.md`). Then review, CI, merge, receipt, this handoff and Notion.
- **Dedicated app cloud environment:** Nathan is creating it with the settings in the brief's "Owner action" section. App Manager 2 is the first session in it.

## App Manager 2 — next actions

1. **Verify the environment (names only).** None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` should be present. `command -v node npm python3.12` should resolve to `$HOME/.local/bin`, with `node --version` v24.19.0, `npm --version` 11.9.0 and `python3.12 --version` 3.12.14. If anything differs, tell Nathan exactly which setting to fix. Never print values.
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

**Open review item.** App Manager 1 read the core governance, operations, setup, CI, handoff and planning documents and the configuration code. Its helper sweep of the remaining `docs/architecture/`, `docs/testing/` and other `docs/operations/` files, looking for stale statements, was stopped before reporting and produced no findings. Include that sweep in a prompt if it is still wanted.

## Accepted baseline and limits

The app has fixture onboarding/profiles/media, eligibility/discovery and interactions, an API smoke runtime, contracts and static model/migration definitions. Not established:

- real authentication or persistence;
- Stream or HDE calls;
- provider delivery;
- a signed native build;
- release readiness.

Readiness stays 503, provider sending stays unavailable, and database integration stays with P11. The [database audit](../planning/database-audit-2026-09-23.md) is dated evidence, not permission to connect. HDE and shared infrastructure remain protected by effect. Stream remains preferred; secret slots are future definitions, not loaders. Outstanding owner inputs are in the [Claude handoff](claude-code-handoff.md#prioritized-inputs-nathan-must-supply).

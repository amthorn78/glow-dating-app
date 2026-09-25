# Current handoff — after M02 (App Manager 2 to App Manager 3, 25 September 2026)

**Process: manual relay** (Nathan, 24 September 2026).

- The manager gives Nathan prompts for implementers. Nathan runs each implementation or review session himself and relays its findings back. The manager follows up as needed.
- Nathan reinitiates managers manually.
- The manager never starts implementation or review work itself (no subagents or remote-session tools for that work).
- Implementation and review sessions may use any tools, subagents or wake-ups they need.

The full procedure is in [manager workflow](../planning/manager-workflow.md). Nathan remains product and account owner. Feature work stays paused; P06.1 is not dispatched.

## Status — 25 September 2026

**At a glance:**

- **Phase:** P01–P05 are complete at fixture scope. The documentation migration (M01) and the Claude setup (M02) are complete. **Feature work stays paused** until Nathan's recorded direction resumes it.
- **Next step, per the plan:** App Manager 3 proposes whether to resume P06.1; see "Next actions".
- **Handover:** Nathan starts App Manager 3 in the `Glow app` environment with the [start prompt](../ephemeral/2026-09-25-next-manager-start-prompt.md). Both reasoning levels are extra high.
- **Setup script:** Nathan pasted the M02 version on 25 September. The first new session verifies it; see below.
- **Mistakes:** the [manager mistakes log](manager-mistakes.md) records every manager mistake (Nathan, 25 September). Read it at the start, and add your own when they are found.

**M02 is merged.** [PR18](https://github.com/amthorn78/glow-dating-app/pull/18) merged on 24 September 2026 at 23:59 UTC as merge commit `2b6c7dfdd10114407c610cce9f38a88ec35cd3ff`. That commit has the tree of the exact reviewed head `5e3fb2f`.

- **Records:** the [M02 evidence record](../testing/evidence/2026-09-24-m02-claude-setup.md) holds every session's results, both reviews, the CI evidence and the merge receipt. The [M02 brief](../planning/claude-setup-optimization.md) holds the review dispositions and, in its last sections, the recorded follow-ups.
- **Close-out, all ordinary documentation:** [PR19](https://github.com/amthorn78/glow-dating-app/pull/19) (the receipt, three documentation nits and the pruned M02 prompts), [PR20](https://github.com/amthorn78/glow-dating-app/pull/20) (Codex's post-merge finding), [PR21](https://github.com/amthorn78/glow-dating-app/pull/21) (this handoff aligned with the plan) and the PR that added the mistakes log.
- **Codex review after the merge.** Marking PR18 ready started Codex's automatic review of `5e3fb2f`, and it finished five minutes after the merge. It reported one P2 in the Setup script's linking step, which the manager verified. It does not affect the paste here. Its fix is a recorded follow-up; see the brief.

- **Setup script: pasted by Nathan on 25 September, verification pending.**
  - Nathan pasted `scripts/bootstrap-toolchain.sh` from `main` into the `Glow app` environment's Setup script. It is blob `450b3cf6504dd0ab13ae2932d8da5a5346319c81`.
  - A Setup script runs only when a new session starts. App Manager 2's session resumed on its old disk, so it still has the old toolchain: on 25 September, 3401 entries under `$HOME/.local/share/glow-app-toolchain` were not root-owned, from the old script's uid-1000 Node tree.
  - The first new session's Setup run replaces that tree in about two minutes. Its log says `replacing …/node-v24.19.0-linux-x64` and then `ready: node v24.19.0, npm 11.9.0, Python 3.12.14`. Afterwards, `find "$HOME/.local/share/glow-app-toolchain" ! -user 0 | wc -l` prints 0.
- **The documentation exemption is live.** CI loads the classifier from `main`. A change made only of Markdown files is ordinary documentation, so it runs no application jobs and needs no code or security review. Two cases stay full scope: any path with a `.claude` component, and a comparison with more than one merge base.
- **Environment (names only):**
  - No HDE variables.
  - The three `STREAM_*` names are present for Nathan's development Stream application; see below.
  - The TypeSafe API credential is attached by the proxy for `api.typesafe.ai`; see the [environment inventory](../operations/environment-inventory.md).
- **Decisions and policy (Nathan, 24 September):**
  - **One work item at a time.** No new work item starts until the current item's CI and review are clear. Corrections, re-reviews and the merge close-out belong to the current item.
  - **`.claude/**` stays full scope.**
  - **Branch and PR discretion:** *"I will trust you to manage the branches and PRs as you see fit."* Merges still need the gates in the [CI policy](../operations/ci-and-branch-policy.md).
- **Reasoning levels.** Each prompt gets the manager's level and the TypeSafe effort scorer v4 reading, tracked in the Notion page *TypeSafe effort scorer — Glow app usage log*. The procedure is step 3 of the [manager workflow](../planning/manager-workflow.md).

  | Session | Manager | TypeSafe | Nathan ran | Outcome | Better call |
  |---|---|---|---|---|---|
  | M02-I1 | high | extra high | extra high | adequate | TypeSafe |
  | Review | extra high | high | extra high | adequate | Manager |
  | M02-C1 | extra high | extra high | extra high | adequate | both |
  | Delta review | extra high | extra high, ultracode flagged | extra high, no ultracode | adequate | both |

  - The delta review had the first ultracode flag: P(`single_session`) was 0.43. The manager did not recommend ultracode; one session sufficed.
  - The pre-registered comparison comes after 10 relayed sessions; this is 4 of 10.
- **CI reliability.** Three intermittent rendered failures of one kind have occurred: a form submit that does not advance. The manager's GitHub integration cannot re-run Actions jobs (403), so Nathan re-runs them when needed.
- **Branches.** Every remote branch except one is fully merged into `main`. That includes the M02 session branches `claude/ecstatic-goodall-qajdh4`, `claude/eager-goodall-1zjgey` and `claude/vigilant-einstein-i95w78`, and the earlier `app-builder-1/*`, `app-planner-1/*` and `docs/*` branches.
  - A cloud session cannot delete another session's branch. Nathan may delete merged branches on GitHub.
  - `app-builder-1/p05-1-birth-diagnostics` is deliberately unmerged; its history is in the [P05.2 handoff](history/p05-2-handoff.md). Keep it.
- **Open PRs:** none.

## Next actions

Follow the plan: PF01's sequence and D09, and the [initiation](../planning/claude-code-initiation.md) assignment, which ends: *"Complete the optimization before proposing whether to resume P06.1."* M02 was that optimization, and it is complete.

1. **Verify the environment (names only).**
   - None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` should be present. `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` should be present.
   - `command -v node npm python3.12` should resolve to `$HOME/.local/bin`, with v24.19.0, 11.9.0 and Python 3.12.14.
   - Run the Setup-script ownership check above. It should print 0 in any session started after Nathan's paste; if it does not, tell Nathan before continuing.
   - If anything differs, tell Nathan exactly which setting to fix. Never print values.
2. **Verify the repository and the record.** Check `main`, open PRs and the worktree. Reconcile Implementation Control and the Work Register, as PF00's "Start here" requires.
3. **Propose whether to resume P06.1. Propose it; don't dispatch it.** Feature work stays paused until Nathan's recorded direction resumes it.
   - Reconcile P06.1's prerequisites in the Work Register (P02.1, P05.3, A04 and A08) with PF01's P06 section and step 1 of the [Claude handoff's live-verification sequence](claude-code-handoff.md#bounded-live-verification-sequence--after-setup-and-owner-inputs).
   - Ask only for the owner inputs the next bounded action needs, from that handoff's prioritized inputs 2 and 3: the Stream account and plan, the test application and region, budget and limits, the secret-injection approach, and the chat-history policy after a block or unmatch.
   - If Nathan resumes P06.1, write its brief in `docs/planning/` and its prompt in `docs/ephemeral/`, with both reasoning levels, and follow the [manager workflow](../planning/manager-workflow.md).
4. **Present the recorded follow-ups with that proposal; Nathan schedules them.** They are outside PF01's sequence, so none starts without his direction:
   - the intermittent rendered-test failures, three so far, where a form submit does not advance. Earlier birth-journey diagnostics are on the unmerged branch `app-builder-1/p05-1-birth-diagnostics`;
   - the Setup-script and pin-test hardening: review nits N1, N2 and N6, Codex's P2 on directory-shaped link destinations, and an optional completion stamp. A script change needs another paste;
   - App Manager 1's stale-documentation sweep of `docs/architecture/`, `docs/testing/` and the rest of `docs/operations/`.

The Notion reconciliation App Manager 1 flagged is done: Plan References point to the repository, A03 is Done and M01 has a row. Implementation Control records it.

## Environment and history

App Manager 1 was the first Claude manager. It ran in the environment shared with HDE, which injects `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` and `PORT` (names observed; values never read). Nathan then created the dedicated `Glow app` cloud environment. Its settings are in the [environment inventory](../operations/environment-inventory.md#claude-cloud-environment-glow-app-nathans-settings-24-september-2026). App Manager 2 was the first session in it; it took M02 over from PR17 and replaced it with PR18. The environment also provides Nathan's **development** Stream application:

- `STREAM_APP_ID=1729640`
- `STREAM_API_KEY=qdstwyevnyea`
- `STREAM_API_SECRET` (secret; name only; never print or record it)

No code reads these yet; P06.1 will. A session's environment is fixed at start, so switching environments requires a new session.

The application behavior baseline is unchanged since PR14 (`ea39454…`). P01–P05 are complete only at fixture scope; see the [migration receipt](migration-publication.md).

## Accepted baseline and limits

The app has fixture onboarding/profiles/media, eligibility/discovery and interactions, an API smoke runtime, contracts and static model/migration definitions. Not established:

- real authentication or persistence;
- Stream or HDE calls;
- provider delivery;
- a signed native build;
- release readiness.

Readiness stays 503, provider sending stays unavailable, and database integration stays with P11. The [database audit](../planning/database-audit-2026-09-23.md) is dated evidence, not permission to connect. HDE and shared infrastructure remain protected by effect. Stream remains preferred; secret slots are future definitions, not loaders. Outstanding owner inputs are in the [Claude handoff](claude-code-handoff.md#prioritized-inputs-nathan-must-supply).

# Current handoff — App Manager 3, P06.1 proposed (25 September 2026)

**Process: manual relay** (Nathan, 24 September 2026).

- The manager gives Nathan prompts for implementers. Nathan runs each implementation or review session himself and relays its findings back. The manager follows up as needed.
- Nathan reinitiates managers manually.
- The manager never starts implementation or review work itself (no subagents or remote-session tools for that work).
- Implementation and review sessions may use any tools, subagents or wake-ups they need.

The full procedure is in [manager workflow](../planning/manager-workflow.md). Nathan remains product and account owner. Feature work stays paused; P06.1 is not dispatched.

## Status — 25 September 2026

**At a glance:**

- **Phase:** P01–P05 are complete at fixture scope. The documentation migration (M01) and the Claude setup (M02) are complete. **Feature work stays paused** until Nathan's recorded direction resumes it.
- **Next step, per the plan:** App Manager 3 gave Nathan the [P06.1 proposal](../planning/p06-1-chat-provider-proof.md) on 25 September. It waits on his decision and five owner inputs; nothing is dispatched. See "Next actions".
- **Manager:** App Manager 3 is active on session branch `claude/stoic-carson-66gdig`. It started in the `Glow app` environment from the [start prompt](../ephemeral/2026-09-25-next-manager-start-prompt.md), which a later manager also uses.
- **Setup script:** verified. Nathan's 25 September paste has taken effect; see below.
- **Mistakes:** the [manager mistakes log](manager-mistakes.md) records every manager mistake (Nathan, 25 September). Read it at the start, and add your own when they are found.

**M02 is merged.** [PR18](https://github.com/amthorn78/glow-dating-app/pull/18) merged on 24 September 2026 at 23:59 UTC as merge commit `2b6c7dfdd10114407c610cce9f38a88ec35cd3ff`. That commit has the tree of the exact reviewed head `5e3fb2f`.

- **Records:** the [M02 evidence record](../testing/evidence/2026-09-24-m02-claude-setup.md) holds every session's results, both reviews, the CI evidence and the merge receipt. The [M02 brief](../planning/claude-setup-optimization.md) holds the review dispositions and, in its last sections, the recorded follow-ups.
- **Close-out, all ordinary documentation:** [PR19](https://github.com/amthorn78/glow-dating-app/pull/19) (the receipt, three documentation nits and the pruned M02 prompts), [PR20](https://github.com/amthorn78/glow-dating-app/pull/20) (Codex's post-merge finding), [PR21](https://github.com/amthorn78/glow-dating-app/pull/21) (this handoff aligned with the plan) and the PR that added the mistakes log.
- **Codex review after the merge.** Marking PR18 ready started Codex's automatic review of `5e3fb2f`, and it finished five minutes after the merge. It reported one P2 in the Setup script's linking step, which the manager verified. It does not affect the paste here. Its fix is a recorded follow-up; see the brief.

- **Setup script: pasted by Nathan and verified on 25 September.**
  - Nathan pasted `scripts/bootstrap-toolchain.sh` from `main` into the `Glow app` environment's Setup script. It is blob `450b3cf6504dd0ab13ae2932d8da5a5346319c81`.
  - App Manager 2's session had resumed on its old disk, where 3401 entries under `$HOME/.local/share/glow-app-toolchain` were not root-owned, from the old script's uid-1000 Node tree.
  - App Manager 3, a new session, verified the paste: `find "$HOME/.local/share/glow-app-toolchain" ! -user 0 | wc -l` printed 0 of 9837 entries, and the tree had been built fresh that day. The details are in the [M02 evidence record](../testing/evidence/2026-09-24-m02-claude-setup.md#setup-script-verification-app-manager-3-25-september-2026).
  - Every new session in the `Glow app` environment should pass the same check.
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
- **CI on main.** Main's application code last changed with PR18 (`2b6c7df`); every later merge is Markdown only and passed through the documentation exemption. On 25 September App Manager 2's branch push run [36081899675](https://github.com/amthorn78/glow-dating-app/actions/runs/36081899675) ran every application job on `b8ca009`'s tree: all six jobs passed, and the gate log says `Application checks passed`.
- **CI reliability.** Three intermittent rendered failures of one kind have occurred: a form submit that does not advance. The manager's GitHub integration cannot re-run Actions jobs (403), so Nathan re-runs them when needed.
- **Branches.** Every remote branch except one is fully merged into `main`. That includes App Manager 2's branch `claude/fervent-darwin-idyko3`, the M02 session branches `claude/ecstatic-goodall-qajdh4`, `claude/eager-goodall-1zjgey` and `claude/vigilant-einstein-i95w78`, and the earlier `app-builder-1/*`, `app-planner-1/*` and `docs/*` branches.
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
3. **P06.1 proposal: delivered on 25 September, awaiting Nathan.** Feature work stays paused until Nathan's recorded direction resumes it.
   - The [proposal](../planning/p06-1-chat-provider-proof.md) reconciles P02.1, P05.3, A04 and A08 with PF01's P06 section and step 1 of the [Claude handoff's live-verification sequence](claude-code-handoff.md#bounded-live-verification-sequence--after-setup-and-owner-inputs).
   - It asks Nathan for five owner inputs, from that handoff's prioritized inputs 2 and 3: the plan; the test application and its region; the budget; the secret handling; and the chat history after an unmatch or block.
   - When Nathan answers, record his decision and inputs in the proposal and here, and sync Notion.
   - If he resumes P06.1, add its brief to the same file, write its prompt in `docs/ephemeral/` with both reasoning levels, and follow the [manager workflow](../planning/manager-workflow.md).
4. **Recorded follow-ups: presented with the proposal on 25 September; Nathan schedules them.** They are outside PF01's sequence, so none starts without his direction:
   - the intermittent rendered-test failures, three so far, where a form submit does not advance. Earlier birth-journey diagnostics are on the unmerged branch `app-builder-1/p05-1-birth-diagnostics`;
   - the Setup-script and pin-test hardening: review nits N1, N2 and N6, Codex's P2 on directory-shaped link destinations, and an optional completion stamp. A script change needs another paste;
   - App Manager 1's stale-documentation sweep of `docs/architecture/`, `docs/testing/` and the rest of `docs/operations/`.

The Notion reconciliation App Manager 1 flagged is done: Plan References point to the repository, A03 is Done and M01 has a row. Implementation Control records it. App Manager 3's reconciliation on 25 September found Implementation Control and the Work Register in line with this handoff except the P05.3 row, whose next action still routed to App Planner 1; it corrected that row.

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

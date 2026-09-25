# Current handoff — App Manager 3, P06.1 in progress (25 September 2026)

**Process: manual relay** (Nathan, 24 September 2026).

- The manager gives Nathan prompts for implementers. Nathan runs each implementation or review session himself and relays its findings back. The manager follows up as needed.
- Nathan reinitiates managers manually.
- The manager never starts implementation or review work itself (no subagents or remote-session tools for that work).
- Implementation and review sessions may use any tools, subagents or wake-ups they need.

The full procedure is in [manager workflow](../planning/manager-workflow.md). Nathan remains product and account owner. Nathan resumed P06.1 on 25 September 2026; other feature work stays paused until his recorded direction resumes it.

## Status — 25 September 2026

**At a glance:**

- **Phase:** P01–P05 are complete at fixture scope. The documentation migration (M01) and the Claude setup (M02) are complete. **Nathan resumed P06.1 on 25 September 2026:** *"resume P06.1, yes to reconfiguring the test app"*. Other feature work stays paused until his recorded direction resumes it.
- **Current work item: P06.1**, the chat-provider permissions and economics proof. Its [brief](../planning/p06-1-chat-provider-proof.md) holds the proposal, Nathan's answers, the Stream dashboard baseline and the session plan. App Manager 3 commissioned P06.1-I1 on 25 September; Nathan runs it and relays the report. See "Next actions".
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
  | P06.1-I1 | extra high | extra high | pending | pending | pending |

  - The delta review had the first ultracode flag: P(`single_session`) was 0.43. The manager did not recommend ultracode; one session sufficed.
  - P06.1-I1's shape reading was single_session at P 0.53, just above the 0.5 rule, so no ultracode; the runner-up was new_silent_guard at 0.31.
  - The pre-registered comparison comes after 10 relayed sessions; 4 of 10 have outcomes.
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
3. **P06.1, the current work item (resumed by Nathan on 25 September).** Its [brief](../planning/p06-1-chat-provider-proof.md) holds the proposal, Nathan's answers and permission, the Stream dashboard baseline and the session plan.
   - **P06.1-I1 is commissioned** ([prompt](../ephemeral/2026-09-25-p06-1-i1-implementation-prompt.md)): the sandbox harness, enforcement of Stream's checks, channel-type lockdown, the authorized path and the bypass matrix. Nathan runs it at extra high and relays the report.
   - Then, following the [manager workflow](../planning/manager-workflow.md): verify the report against the pushed branch; integrate it into the manager branch; commission the exact-head code and security review; correct if needed.
   - Then write P06.1-I2's prompt (revocation and history under Nathan's policy, outage, economics, the architecture document). Its head gets a delta review.
   - Close: open the PR, pass every Foundation job on its head, wait for Codex's reviews, merge, verify `main`, and record the receipt, the handoff and Notion.
   - The dashboard showed Stream's authentication and permission checks in relaxed modes. I1 establishes and records the real settings through the API before any client acts.
4. **Recorded follow-ups: presented with the proposal on 25 September; Nathan schedules them.** They are outside PF01's sequence, so none starts without his direction, and only after P06.1's CI and review are clear:
   - the intermittent rendered-test failures, three so far, where a form submit does not advance. Earlier birth-journey diagnostics are on the unmerged branch `app-builder-1/p05-1-birth-diagnostics`;
   - the Setup-script and pin-test hardening: review nits N1, N2 and N6, Codex's P2 on directory-shaped link destinations, and an optional completion stamp. A script change needs another paste;
   - App Manager 1's stale-documentation sweep of `docs/architecture/`, `docs/testing/` and the rest of `docs/operations/`.

The Notion reconciliation App Manager 1 flagged is done: Plan References point to the repository, A03 is Done and M01 has a row. Implementation Control records it. App Manager 3's reconciliation on 25 September found Implementation Control and the Work Register in line with this handoff except the P05.3 row, whose next action still routed to App Planner 1; it corrected that row.

## Environment and history

App Manager 1 was the first Claude manager. It ran in the environment shared with HDE, which injects `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` and `PORT` (names observed; values never read). Nathan then created the dedicated `Glow app` cloud environment. Its settings are in the [environment inventory](../operations/environment-inventory.md#claude-cloud-environment-glow-app-nathans-settings-24-september-2026). App Manager 2 was the first session in it; it took M02 over from PR17 and replaced it with PR18. The environment also provides Nathan's **development** Stream application:

- `STREAM_APP_ID=1729640`
- `STREAM_API_KEY=qdstwyevnyea`
- `STREAM_API_SECRET` (secret; name only; never print or record it)

No application code reads these. P06.1's sandbox harness reads them on the server side only; the app's loader adopts them in P06.2. A session's environment is fixed at start, so switching environments requires a new session.

The application behavior baseline is unchanged since PR14 (`ea39454…`). P01–P05 are complete only at fixture scope; see the [migration receipt](migration-publication.md).

## Accepted baseline and limits

The app has fixture onboarding/profiles/media, eligibility/discovery and interactions, an API smoke runtime, contracts and static model/migration definitions. Not established:

- real authentication or persistence;
- Stream or HDE calls;
- provider delivery;
- a signed native build;
- release readiness.

Readiness stays 503, provider sending stays unavailable, and database integration stays with P11. The [database audit](../planning/database-audit-2026-09-23.md) is dated evidence, not permission to connect. HDE and shared infrastructure remain protected by effect. Stream remains preferred; secret slots are future definitions, not loaders. Outstanding owner inputs are in the [Claude handoff](claude-code-handoff.md#prioritized-inputs-nathan-must-supply).

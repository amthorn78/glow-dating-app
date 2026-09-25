# Current handoff — after M02 (App Manager 2, 25 September 2026)

**Process: manual relay** (Nathan, 24 September 2026).

- The manager gives Nathan prompts for implementers. Nathan runs each implementation or review session himself and relays its findings back. The manager follows up as needed.
- Nathan reinitiates managers manually.
- The manager never starts implementation or review work itself (no subagents or remote-session tools for that work).
- Implementation and review sessions may use any tools, subagents or wake-ups they need.

The full procedure is in [manager workflow](../planning/manager-workflow.md). Nathan remains product and account owner. Feature work stays paused; P06.1 is not dispatched.

## Status — 25 September 2026

**M02 is merged.** [PR18](https://github.com/amthorn78/glow-dating-app/pull/18) merged on 24 September 2026 at 23:59 UTC as merge commit `2b6c7dfdd10114407c610cce9f38a88ec35cd3ff`. That commit has the tree of the exact reviewed head `5e3fb2f`.

- **Records:** the [M02 evidence record](../testing/evidence/2026-09-24-m02-claude-setup.md) holds every session's results, both reviews, the CI evidence and the merge receipt. The [M02 brief](../planning/claude-setup-optimization.md) holds the review dispositions and, in its last sections, the queued follow-ups.
- **Close-out:** the receipt, the fixes for three documentation nits and the pruned M02 prompts landed through a documentation-only PR, the one that carries this handoff.

- **Pending owner action: paste the Setup script once.**
  - Nathan pastes `scripts/bootstrap-toolchain.sh` from `main` into the `Glow app` environment's Setup script, unchanged. It is blob `450b3cf6504dd0ab13ae2932d8da5a5346319c81`.
  - Until then, new sessions get the old script's toolchain. Its Node tree is owned by uid 1000; on 25 September, 3401 entries under `$HOME/.local/share/glow-app-toolchain` were not root-owned.
  - The first new session after the paste replaces that tree in about two minutes. Afterwards, `find "$HOME/.local/share/glow-app-toolchain" ! -user 0 | wc -l` prints 0.
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

## Next actions

1. **Verify the environment (names only).**
   - None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` should be present. `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` should be present.
   - `command -v node npm python3.12` should resolve to `$HOME/.local/bin`, with v24.19.0, 11.9.0 and Python 3.12.14.
   - If Nathan has pasted the Setup script, the ownership check above prints 0.
   - If anything differs, tell Nathan exactly which setting to fix. Never print values.
2. **Verify the repository.** Check `main`, open PRs and the worktree.
3. **Confirm the Setup-script paste** with Nathan if it is still pending.
4. **Choose the next work item with Nathan**, one at a time, from the queue in the brief's section "Delta review of `5e3fb2f`, merge and follow-ups". The manager's recommended order:
   1. the rendered-test diagnosis;
   2. the Setup-script and pin-test hardening (review nits N1, N2, N6 and an optional completion stamp);
   3. the stale-documentation sweep of `docs/architecture/`, `docs/testing/` and the rest of `docs/operations/`, which is ordinary documentation;
   4. a P06.1 proposal. P06.1 needs Stream access, plan and budget, a secret-injection decision and a chat-history policy. Propose it; don't dispatch it.

   For the chosen item, write its brief in `docs/planning/`, its prompt in `docs/ephemeral/`, and both reasoning levels, then follow the [manager workflow](../planning/manager-workflow.md).
5. **Notion follow-up.** On 24 September App Manager 1 found that 47 of 62 Work Register rows cite the historical Drive plan as Plan Reference, and that A03 still shows Ready. Reconcile them if the M02 close-out has not; the Notion Implementation Control page records what was done.

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

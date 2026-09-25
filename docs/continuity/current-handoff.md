# Current handoff — App Manager 3 (25 September 2026)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md), and is linked from here. The earlier, longer handoff is [archived](history/m02-p06-1-handoff.md) (DM-01 P3).

- **Process:** Nathan's manual relay, per the [manager workflow](../planning/manager-workflow.md), with the [Dev Manager](../planning/dev-manager.md) as the second-layer reviewer. Nathan carries messages between the two managers by hand (OD-25).
- **Standing directions:** the [owner-direction register](owner-directions.md). Notion carries a copy of it and of the operating procedure; the repository wins on any difference (OD-26, OD-27).
- **A new manager** starts from the [next-manager start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager:** App Manager 3, on the session branch `claude/stoic-carson-66gdig`, which is the head of draft [PR26](https://github.com/amthorn78/glow-dating-app/pull/26).
- **Current item: P06.1**, the chat-provider permissions and economics proof. Nathan resumed it on 25 September; all other feature work stays paused. The [brief](../planning/p06-1-chat-provider-proof.md) holds the plan, results and decisions. The [evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md) holds the runs.
  - **I1 is done** at code head `9ff600f`. Push run [36109949498](https://github.com/amthorn78/glow-dating-app/actions/runs/36109949498) passed all six jobs with `Application checks passed`.
  - **S15:** the display rule ([ADR 0003](../adr/0003-chat-display-rule.md)) is conditional on the I1 review confirming S15 live. Nathan's principle is in force, and he confirmed its exceptions (OD-16).
  - **Two sessions are ready for Nathan,** and they can run side by side:
    - I1's exact-head review, from revision 3 of its [prompt](../ephemeral/2026-09-25-p06-1-i1-review-prompt.md), with records commit `516bee2`;
    - the flake diagnosis (OD-21), from its [prompt](../ephemeral/2026-09-25-p06-1-flake-diagnosis-prompt.md).
- **Dev Manager 1:** session `session_01MrcrmqtuENZ345mKfmsSWv`, branch `claude/dev-manager`. The [review log](dev-manager/README.md) records DM-01 to DM-03, Nathan's answers and their dispositions.

## Waiting checkpoint (25 September 2026)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 3 | Nathan | The report of I1's exact-head review | I2a and I2b wait for the review and any corrections |
| App Manager 3 | Nathan | The flake diagnosis report | PR26 cannot be accepted while the failure is unexplained (OD-21) |
| App Manager 3 | Nathan | His decision on the manager's Stream-secret recommendation (OD-20) | The current setup stands. I2a waits for the decision |

## Next actions

1. Verify each report when it arrives, and record it where its prompt says. Commission corrections if needed. If the review narrows or closes S15, the choice of the display rule goes back to Nathan.
2. While the sessions run, write the HDE contract-requirements document from PF01 §5 for Nathan to take into HDE's own process (OD-23). It is manager work, and it waits on nothing.
3. Write the prompts for I2a (revocation and safety) and I2b (Video and Feeds, the architecture document and the harness in CI), and the economics discovery prompt, as the brief's "Sessions" section describes. The Dev Manager reads each one before Nathan runs it.
4. Close P06.1:
   - a Dev Manager close-out read of the governing Markdown changed after `fa4dc5f` (charter, "A read covers one commit");
   - complete the pre-merge checklist in PR26 (workflow step 7);
   - mark the PR ready and wait for Codex;
   - merge and verify `main`;
   - record the receipt, this handoff and Notion;
   - rotate the development Stream secret (DM-02 B8).
5. **Next item after P06.1:** P06.DB, the early disposable-PostgreSQL proof (OD-17, PF01 §6). Then P06.2.

**Recorded follow-ups** (Nathan schedules them after P06.1's CI and review are clear):

- the Setup-script and pin-test hardening from M02's reviews ([M02 brief](../planning/claude-setup-optimization.md), last sections);
- a sweep for stale documentation in `docs/architecture/`, `docs/testing/` and `docs/operations/`.

## Branches

- **PR26** carries the manager branch, I1's branch `claude/compassionate-lamport-531vtk` and the Dev Manager's reports. It is ahead of `main` and not behind it, so nothing conflicts. Everything after I1's code head is Markdown.
- `claude/dev-manager` holds only the Dev Manager's reports. The manager merges it in batches.
- Keep the unmerged `app-builder-1/p05-1-birth-diagnostics`. It holds the earlier diagnostics for the rendered-test failure.
- All other remote branches are fully merged into `main`.

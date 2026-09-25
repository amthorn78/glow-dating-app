# Current handoff — App Manager 3 (25 September 2026)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md), and is linked from here. The earlier, longer handoff is [archived](history/m02-p06-1-handoff.md) (DM-01 P3).

- **Process:** Nathan's manual relay, per the [manager workflow](../planning/manager-workflow.md), with the [Dev Manager](../planning/dev-manager.md) as the second-layer reviewer.
- **Standing directions:** the [owner-direction register](owner-directions.md).
- **A new manager** starts from the [next-manager start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager:** App Manager 3, on the session branch `claude/stoic-carson-66gdig`, which is the head of draft [PR26](https://github.com/amthorn78/glow-dating-app/pull/26).
- **Current item: P06.1**, the chat-provider permissions and economics proof. Nathan resumed it on 25 September; all other feature work stays paused. The [brief](../planning/p06-1-chat-provider-proof.md) holds the plan, results and decisions. The [evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md) holds the runs.
  - **I1 is done.** It is integrated at code head `9ff600f`. Push run [36109949498](https://github.com/amthorn78/glow-dating-app/actions/runs/36109949498) passed all six jobs with `Application checks passed`.
  - **S15 is decided:** the display rule ([ADR 0003](../adr/0003-chat-display-rule.md)). The display rule as S15's answer is conditional on the I1 review confirming S15 live. Nathan's principle is in force, with its carve-outs pending.
  - **I1's exact-head review has not run.** Its [prompt](../ephemeral/2026-09-25-p06-1-i1-review-prompt.md) is at revision 3. The Dev Manager read revision 2 (DM-03), and revision 3 adds its conditions. Nathan should not use revision 1, which named `c0a34f8`.
- **Dev Manager 1:** session `session_01MrcrmqtuENZ345mKfmsSWv`, branch `claude/dev-manager`. DM-01, DM-02 and DM-03 are answered, and their dispositions are recorded in the [review log](dev-manager/README.md). An idle session cannot receive cross-session messages; send a consultation as a one-time Routine into it (charter, relay step 1).

## Waiting checkpoint (25 September 2026)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 3 | Nathan | The report of I1's exact-head review. Nathan runs revision 3 of the prompt, with `<RECORDS_COMMIT>` filled in as the manager gave it | Nothing else in P06.1 starts. I2a and I2b wait for the review and any corrections |
| App Manager 3 | Nathan | Answers to the Dev Manager's ten questions (DM-01 questions 1–4, DM-02 questions 1–6), as the review log relays them | The items stay open. Nothing that depends on them starts |

## Next actions

1. Nathan runs the I1 review from revision 3 of its prompt and relays the report.
2. Verify the report, and record it in the evidence record under "Exact-head review of I1". Commission corrections if needed. If the review narrows or closes S15, the choice of the display rule goes back to Nathan.
3. Write the prompts for I2a (revocation and safety) and I2b (Video and Feeds, the architecture document and the harness in CI), and the economics discovery prompt, as the brief's "Sessions" section describes. The Dev Manager reads each one before Nathan runs it.
4. Close P06.1:
   - a Dev Manager close-out read of the governing Markdown changed after `fa4dc5f` (charter, "A read covers one commit");
   - complete the pre-merge checklist in PR26 (workflow step 7);
   - mark the PR ready and wait for Codex;
   - merge and verify `main`;
   - record the receipt, this handoff and Notion.

**Recorded follow-ups** (Nathan schedules them after P06.1's CI and review are clear, unless he answers DM-01 question 1 otherwise):

- the intermittent rendered-test failure, where a form submit does not advance;
- the Setup-script and pin-test hardening from M02's reviews ([M02 brief](../planning/claude-setup-optimization.md), last sections);
- a sweep for stale documentation in `docs/architecture/`, `docs/testing/` and `docs/operations/`.

## Branches

- PR26 merges both the manager branch and I1's branch, `claude/compassionate-lamport-531vtk`.
- `claude/dev-manager` holds only the Dev Manager's reports. The manager merges it in batches.
- Keep the unmerged `app-builder-1/p05-1-birth-diagnostics`. It holds the diagnostics for the rendered-test failure.
- All other remote branches are fully merged into `main`.

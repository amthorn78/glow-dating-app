# Current handoff — App Manager 3 (25 September 2026)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md), and is linked from here. The earlier, longer handoff is [archived](history/m02-p06-1-handoff.md) (DM-01 P3).

- **Process:** Nathan's manual relay, per the [manager workflow](../planning/manager-workflow.md), with the [Dev Manager](../planning/dev-manager.md) as the second-layer reviewer. Nathan carries messages between the managers by hand (OD-25).
- **Standing directions:** the [owner-direction register](owner-directions.md). Notion carries a copy of it and of the operating procedure; the repository wins on any difference (OD-26, OD-27).
- **A new manager** starts from the [next-manager start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager:** App Manager 3, on `claude/stoic-carson-66gdig`, the head of draft [PR26](https://github.com/amthorn78/glow-dating-app/pull/26).
- **Current item: P06.1**, the chat-provider permissions and economics proof. Resumed on 25 September; other feature work stays paused. Plan, results and decisions: the [brief](../planning/p06-1-chat-provider-proof.md). Runs: the [evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md).
  - **S15:** the I1 review confirmed it live, so the display rule ([ADR 0003](../adr/0003-chat-display-rule.md)) stands. Nathan's principle is in force, with the exceptions he confirmed (OD-16).
  - **Linear order (OD-29):** one session at a time, one prompt per message.
    - **Done:** I1 (`9ff600f`) and its review (changes required); the flake fix (`8b8b1bd`) and its review (approve, so OD-21 is met); C1 (`e85bba0`) and C2 (`63e922f`), each with its review (approve, with items for the next pass); C3, integrated at `8c1a8c0`.
    - **Next:** C3's exact-head review, offline and scoped to C3 ([prompt](../ephemeral/2026-09-26-p06-1-c3-review-prompt.md)). Nathan starts it.
    - **Then:** I2a. It is live: the Dev Manager reads its prompt first, and Nathan adds the Stream variables.
- **The [HDE contract request](../planning/hde-contract-request.md) is written** (OD-23). Nathan takes it into HDE's process and sets the date; on delivery, record the receipt (its section 6).
- **Dev Manager 1:** session `session_01MrcrmqtuENZ345mKfmsSWv`, branch `claude/dev-manager`. Its [review log](dev-manager/README.md) holds DM-01 to DM-03, Nathan's answers and the dispositions.

## Waiting checkpoint (26 September 2026)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 3 | Nathan | C3's review report | Nothing else starts (OD-29) |
| App Manager 3 | Nathan | Confirmation of the shared-restore risk ADR 0004 records as accepted | ADR 0004 stands |
| App Manager 3 | The Dev Manager, via Nathan | Reads of the governing changes after `fa4dc5f` and of the HDE contract request. The relay messages are not yet sent; each goes as its own step in the linear order | PR26 cannot merge without the reads |

## Next actions

1. Verify C3's review report and record it. Then write I2a's prompt; the Dev Manager reads it, then Nathan runs it.
2. Then I2b and the economics discovery, one at a time, as the brief's "Sessions" describes. Live prompts tell Nathan to add the three `STREAM_*` variables first (OD-28).
3. Close P06.1:
   - the Dev Manager's reads of the governing Markdown changed after `fa4dc5f` (charter, "A read covers one commit");
   - complete the pre-merge checklist in PR26 (workflow step 7);
   - mark the PR ready and wait for Codex;
   - merge and verify `main`;
   - record the receipt, this handoff and Notion;
   - rotate the development Stream secret (DM-02 B8).
4. **Next item after P06.1:** P06.DB, the early disposable-PostgreSQL proof (OD-17, PF01 §6). Then P06.2.

**Recorded follow-ups** (Nathan schedules them after P06.1's CI and review are clear):

- the Setup-script and pin-test hardening from M02's reviews ([M02 brief](../planning/claude-setup-optimization.md), last sections);
- a sweep for stale documentation in `docs/architecture/`, `docs/testing/` and `docs/operations/`;
- failure capture in CI: a trace and screenshot on a rendered failure (the flake diagnosis's proposal).

## Branches

- **PR26** is not behind `main`. Its code: I1's harness (`9ff600f`), the flake fix (`8b8b1bd`), C1 (`e85bba0`), C2 (`63e922f`) and C3 (`8c1a8c0`); the rest is Markdown.
- Merged into PR26 only: the session branches `claude/compassionate-lamport-531vtk` (I1), `claude/trusting-mayer-bw6p40` (flake), `claude/youthful-pasteur-caokpc` (C1), `claude/lucid-einstein-79bqmd` (C2) and `claude/friendly-hypatia-ug6r52` (C3), and `claude/dev-manager`, which holds only the Dev Manager's reports.
- Retire the unmerged `app-builder-1/p05-1-birth-diagnostics` after PR26 merges.
- Every other remote branch is merged into `main`.

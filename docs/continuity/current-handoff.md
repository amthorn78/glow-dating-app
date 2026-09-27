# Current handoff — App Manager 4 (27 September 2026)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); the earlier handoff is [archived](history/m02-p06-1-handoff.md).

- **Process:** Nathan's manual relay, per the [manager workflow](../planning/manager-workflow.md), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25).
- **Standing directions:** the [owner-direction register](owner-directions.md); Notion carries a copy, and the repository wins (OD-26, OD-27).
- **A new manager** starts from the [start procedure](../planning/start-prompts/next-manager.md); read the [mistakes log](manager-mistakes.md).

## Now

- **Manager:** App Manager 5, started by Nathan by hand on 27 September from the [start procedure](../planning/start-prompts/next-manager.md), succeeding App Manager 4 (`session_016nNFAZqaqTDqxX4Bq6jbRV`, Fable 5.1 at extra high), whose handover commit is the head of `claude/stoic-carson-66gdig`, draft [PR26](https://github.com/amthorn78/glow-dating-app/pull/26); App Manager 4 pushes nothing after it. App Manager 5 works on its own branch from that head, opens a replacement PR and closes PR26 with a link (workflow, "Branches and pushes"). A manager's container may hold the three `STREAM_*` variables; it never reads or uses them (AM3-17).
- **Current item: P06.1**, the chat-provider permissions and economics proof (resumed 25 September; other feature work paused): the [brief](../planning/p06-1-chat-provider-proof.md) and the [evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md).
  - **S15:** confirmed live; the display rule ([ADR 0003](../adr/0003-chat-display-rule.md)) stands (OD-14, OD-16).
  - **Linear (OD-29):** one session at a time, one prompt per message.
    - **Done:** I1 (`9ff600f`) and its review; the flake fix (`8b8b1bd`), C1 (`e85bba0`), C2 (`63e922f`), C3 (`8c1a8c0`) and I2a (`6a51dae`), each approved by its review; DM-04. No Stream mechanism meets the history policy alone (I2a).
    - **Done:** DM-05: approved with conditions, all accepted and applied in revision 2 of I2b's [prompt](../ephemeral/2026-09-27-p06-1-i2b-implementation-prompt.md); disposition in the [review log](dev-manager/README.md).
    - **Done:** I2b (`ad89753`, merged at `55b2238`): the Video and Feeds lockdown is applied to application 1729640; removal and deactivation MEET the history policy under the 404 code 16 rule; the [architecture document](../architecture/chat-provider-permissions.md) is written; "Stream proof checks" runs in CI.
    - **Done:** OD-33 and OD-34: the [reasoning-strength matrix](../planning/reasoning-level-matrix.md), six rungs on both models; request v6 (Nathan's Claude skill `typesafe-scoring`); every prompt re-read.
    - **In flight:** the I2b review at `55b2238` ([prompt](../ephemeral/2026-09-27-p06-1-i2b-review-prompt.md), revision 3), on Fable 5.1 at max; then the economics discovery.
- **The [HDE contract request](../planning/hde-contract-request.md)** (OD-23): in Nathan's own process; on delivery, record the receipt (its section 6); not a standing item for him (OD-32).
- **Dev Manager 1:** session `session_01MrcrmqtuENZ345mKfmsSWv`, branch `claude/dev-manager`; the [review log](dev-manager/README.md) holds DM-01 to DM-05.

## Waiting checkpoint (27 September 2026, handover to App Manager 5)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 5 | Nathan | The I2b review's report (running on Fable 5.1 at max, started 27 September) | Nothing else starts (OD-29); ask for the session's state |
| App Manager 5 | Nathan | The `typesafe-scoring` skill visible in its session | Report it; the request body is in the matrix file, section 6 |
| App Manager 5 | The Dev Manager, via Nathan | Reads of the governing changes after `fa4dc5f` (OD-31's and OD-32's too) and of the HDE contract request, each a later step; that read also confirms the restore risk ADR 0004 records as accepted (OD-32) | PR26 cannot merge without the reads |

## Next actions

1. Verify the I2b review's report; a correction pass only for a finding in the classes the review prompt names. Then update ADR 0003's conditions and "Revisit when" (DM-05 finding 5 (b)) and record the outcome.
2. Then the economics discovery (the brief's "Sessions").
3. Close P06.1:
   - the Dev Manager's reads of the governing Markdown changed after `fa4dc5f`;
   - complete the pre-merge checklist in PR26 (workflow step 7);
   - mark the PR ready and wait for Codex;
   - merge and verify `main`;
   - record the receipt, this handoff and Notion;
   - rotate the development Stream secret (DM-02 B8).
4. **Next item after P06.1:** P06.DB, the early disposable-PostgreSQL proof (OD-17, PF01 §6). Then P06.2.

**Recorded follow-ups** (after P06.1): Setup-script and pin-test hardening ([M02 brief](../planning/claude-setup-optimization.md)); a stale-documentation sweep of `docs/architecture/`, `docs/testing/` and `docs/operations/`.

## Branches

- **PR26** is not behind `main`. Code: I1 (`9ff600f`), the flake fix (`8b8b1bd`), C1 (`e85bba0`), C2 (`63e922f`), C3 (`8c1a8c0`), I2a (`6a51dae`) and I2b (`55b2238`); the rest is Markdown.
- Merged into PR26 only: the session branches the brief names and `claude/dev-manager`.
- Retire the unmerged `app-builder-1/p05-1-birth-diagnostics` after PR26 merges; every other remote branch is merged into `main`.

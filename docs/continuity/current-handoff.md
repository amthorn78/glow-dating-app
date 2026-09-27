# Current handoff — App Manager 5 (27 September 2026)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); the earlier handoff is [archived](history/m02-p06-1-handoff.md).

- **Process:** Nathan's manual relay, per the [manager workflow](../planning/manager-workflow.md), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25).
- **Standing directions:** the [owner-direction register](owner-directions.md); Notion carries a copy, and the repository wins (OD-26, OD-27).
- **A new manager** starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager:** App Manager 5 (`session_01Xv2QTYGpc5bSQQoVeWiN4E`), started by Nathan by hand on 27 September. Its branch `claude/magical-wozniak-yfmmx2` continues from App Manager 4's handover commit `2a86c8e`; draft [PR27](https://github.com/amthorn78/glow-dating-app/pull/27) replaces PR26, closed with a link.
- **Current item: P06.1**, the chat-provider permissions and economics proof (resumed 25 September; other feature work paused): the [brief](../planning/p06-1-chat-provider-proof.md) and the [evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md).
  - **S15:** confirmed live; the display rule ([ADR 0003](../adr/0003-chat-display-rule.md)) stands (OD-14, OD-16).
  - **Linear (OD-29):** one session at a time, one prompt per message.
    - **Done:** I1 and its review; the flake fix, C1, C2, C3 and I2a, each approved by its review (commits under "Branches"); DM-04. No Stream mechanism meets the history policy alone (I2a).
    - **Done:** DM-05, its conditions applied in revision 2 of I2b's [prompt](../ephemeral/2026-09-27-p06-1-i2b-implementation-prompt.md).
    - **Done:** I2b (`ad89753`, merged at `55b2238`): the Video and Feeds lockdown is applied to application 1729640; removal and deactivation MEET the history policy; the [architecture document](../architecture/chat-provider-permissions.md) is written; "Stream proof checks" runs in CI.
    - **Done:** OD-33, OD-34: the [reasoning-strength matrix](../planning/reasoning-level-matrix.md), six rungs, both models; request v6 (skill `typesafe-scoring`).
    - **Done:** the I2b [review](../ephemeral/2026-09-27-p06-1-i2b-review-prompt.md): approve, findings to C4; ADR 0003's conditions updated.
    - **Done:** C4 ([prompt](../ephemeral/2026-09-27-p06-1-c4-correction-prompt.md)), integrated by fast-forward at `c83bedf` (code head `b2b9a0b`).
    - **Next:** C4's exact-head [review](../ephemeral/2026-09-27-p06-1-c4-review-prompt.md), the final delta review; then the economics discovery.
- **The [HDE contract request](../planning/hde-contract-request.md)** (OD-23): in Nathan's own process; on delivery, record the receipt (its section 6); not a standing item for him (OD-32).
- **Dev Manager 1:** session `session_01MrcrmqtuENZ345mKfmsSWv`, branch `claude/dev-manager`; the [review log](dev-manager/README.md) holds DM-01 to DM-05.

## Waiting checkpoint (27 September 2026, App Manager 5)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 5 | Nathan | The C4 review's report (prompt given 27 September) | Nothing else starts (OD-29); ask for the session's state |
| App Manager 5 | The Dev Manager, via Nathan | The close-out consultation, next action 3, a later step | PR27 cannot merge without it |

## Next actions

1. Verify the C4 review's report; another correction pass only for a finding in the classes its prompt names.
2. Then the economics discovery (the brief's "Sessions").
3. Close P06.1:
   - the Dev Manager's close-out consultation: reads of the governing Markdown changed after `fa4dc5f` (ADR 0003's update too) and of the HDE contract request; the restore risk ADR 0004 records as accepted (OD-32); the activities query, `call_member` and the I2b review's finding 2 (a live read);
   - complete the pre-merge checklist in PR27 (workflow step 7);
   - mark the PR ready and wait for Codex;
   - merge and verify `main`;
   - record the receipt, this handoff and Notion;
   - rotate the development Stream secret (DM-02 B8).
4. **Next item after P06.1:** P06.DB, the early disposable-PostgreSQL proof (OD-17, PF01 §6). Then P06.2.

**Recorded follow-ups** (after P06.1): Setup-script and pin-test hardening ([M02 brief](../planning/claude-setup-optimization.md)); a stale-documentation sweep of `docs/architecture/`, `docs/testing/` and `docs/operations/`.

## Branches

- **PR27** is not behind `main`; earlier records call it PR26. Code: I1 (`9ff600f`), the flake fix (`8b8b1bd`), C1 (`e85bba0`), C2 (`63e922f`), C3 (`8c1a8c0`), I2a (`6a51dae`), I2b (`55b2238`) and C4 (`c83bedf`); the rest is Markdown.
- Merged into PR27 only: the session branches the brief names, `claude/dev-manager` and PR26's head, `claude/stoic-carson-66gdig`.
- Retire the unmerged `app-builder-1/p05-1-birth-diagnostics` after PR27 merges; every other remote branch is merged into `main`.

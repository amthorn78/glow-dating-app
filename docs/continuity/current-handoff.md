# Current handoff — App Manager 5 (29 September 2026, after PR27)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); the earlier handoff is [archived](history/m02-p06-1-handoff.md).

- **Process:** Nathan's manual relay, per the [manager workflow](../planning/manager-workflow.md), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25).
- **Standing directions:** the [owner-direction register](owner-directions.md); Notion carries a copy, and the repository wins (OD-26, OD-27).
- **A new manager** starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager:** App Manager 5 (`session_01Xv2QTYGpc5bSQQoVeWiN4E`), started by Nathan by hand on 27 September. Its branch `claude/magical-wozniak-yfmmx2` restarted from `main` at `47db18d` after PR27 merged; draft PR28 carries the next item.
- **P06.1 is done** (merged 29 September at `47db18d`): the [brief](../planning/p06-1-chat-provider-proof.md) and the [evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md), with its merge receipt. The display rule ([ADR 0003](../adr/0003-chat-display-rule.md)) stands; the development application stays locked down (OD-37). P06.2 inherits the brief's "Carried to P06.2".
- **Current item: P06.DB**, the early disposable-PostgreSQL proof (OD-17, PF01 §6): the [brief](../planning/p06-db-disposable-postgres-proof.md), revision 2, which applies the Dev Manager's read ([DM-08](dev-manager/reviews/2026-09-29-dm-08-p06-db-brief.md)) as written. The [implementation prompt](../ephemeral/2026-09-29-p06-db-implementation-prompt.md) went to Nathan on 29 September; its session starts in `Glow App - No Stream`, and no Dev Manager read of it is needed (DM-08 7.2).
  - **Linear (OD-29):** one session at a time, one prompt per message. Other feature work stays paused.
- **The [HDE contract request](../planning/hde-contract-request.md)** (OD-23): in Nathan's own process; on delivery, record the receipt (its section 6); not a standing item for him (OD-32).
- **Dev Manager 2:** session `session_015DxVkL8PXn2YaauE6RdSWN`, created by Dev Manager 1 (OD-35); branch `claude/dev-manager`; the [review log](dev-manager/README.md) holds DM-01 to DM-08, each with its disposition.
- **Environments** (OD-36): every prompt names one; `Glow app` only for a session that calls Stream.

## Waiting checkpoint (29 September 2026, App Manager 5)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 5 | The P06.DB implementation session, via Nathan | Its report: branch, head, the final-head Foundation run and the evidence record | Nothing to chase: Nathan runs the session when he chooses; the next step waits on its report |

## Next actions

1. Verify the implementation session's report against its branch and its final-head run; integrate it into PR28; add the manager's verification to its evidence record; update the CI policy's job list and counts (DM-08 7.1) and the P11 plan's DB06 and DB09 marks in D6's words.
2. Write the exact-head code and security review prompt, with the TypeSafe reading (environment `Glow App - No Stream`).
3. Before PR28 merges: the Dev Manager reads its governing changes (the CI policy, the workflow's Notion checklist line) and confirms the changes the review log's DM-07 section lists; then Codex, the merge and the receipt; then P06.2.
4. Standing: before the Stream harness is used live again, the C5 review's nits 2 and 3 and its header-allowlist advice; before the next Dev Manager session, rewrite its start prompt (DM-03 E3; DM-07 item 7).

**Recorded follow-ups:** prune the P06.1 prompts in `docs/ephemeral/` once their links are commit-pinned; Setup-script and pin-test hardening ([M02 brief](../planning/claude-setup-optimization.md)); a stale-documentation sweep of `docs/architecture/`, `docs/testing/` and `docs/operations/`.

## Branches

- **PR27** merged at `47db18d`: P06.1's code (I1, the flake fix, C1 to C5, I2a, I2b) and its records. PR28 starts from it.
- `claude/dev-manager` merges into the manager branch at each consultation's integration.
- Retire the unmerged `app-builder-1/p05-1-birth-diagnostics` once its content is confirmed recorded; every other remote branch is merged into `main`.

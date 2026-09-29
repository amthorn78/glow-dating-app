# Current handoff — App Manager 5 (29 September 2026, after PR27)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); the earlier handoff is [archived](history/m02-p06-1-handoff.md).

- **Process:** Nathan's manual relay, per the [manager workflow](../planning/manager-workflow.md), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25).
- **Standing directions:** the [owner-direction register](owner-directions.md); Notion carries a copy, and the repository wins (OD-26, OD-27).
- **A new manager** starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager:** App Manager 5 (`session_01Xv2QTYGpc5bSQQoVeWiN4E`), started by Nathan by hand on 27 September. Its branch `claude/magical-wozniak-yfmmx2` restarted from `main` at `47db18d` after PR27 merged; draft PR28 carries the next item.
- **P06.1 is done** (merged 29 September at `47db18d`): the [brief](../planning/p06-1-chat-provider-proof.md) and the [evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md), with its merge receipt. The display rule ([ADR 0003](../adr/0003-chat-display-rule.md)) stands; the development application stays locked down (OD-37). P06.2 inherits the brief's "Carried to P06.2".
- **Current item: P06.DB**, the early disposable-PostgreSQL proof (OD-17, PF01 §6): the [brief](../planning/p06-db-disposable-postgres-proof.md), revision 2, which applies the Dev Manager's read ([DM-08](dev-manager/reviews/2026-09-29-dm-08-p06-db-brief.md)) as written.
  - **The implementation is done and integrated** into PR28 at `6f5866d` (29 September). Its run of record, Foundation run 36520940933 on `dff83d4`, passed every job. The manager's verification, its corrections and five observations are in the [evidence record](../testing/evidence/2026-09-29-p06-db-disposable-postgres-proof.md). The P11 plan's DB06 and DB09 are marked partially evidenced in CI, DB06's with F1's limit until C1's run, and the CI policy names the new job.
  - **Its exact-head review** of `6f5866d` ([prompt](../ephemeral/2026-09-29-p06-db-review-prompt.md)), run by Nathan on 29 September on Fable 5.1 at max: **changes required, narrowly.** F1, in a correction class: the stress run's per-race overlap count read every race's rows at the same iteration number. F2: the oracle's O2 misses a send stored at the version a revocation set. Four nits. The manager verified and recorded it, with its disposition, in the evidence record; F5 and F6 are done, and AM5-12 is logged.
  - **In flight: P06.DB-C1, the correction pass** ([prompt](../ephemeral/2026-09-29-p06-db-c1-correction-prompt.md)): F1 to F4 with tests, the record corrected in place, and the job rerun for real per-race overlap counts, in `Glow App - No Stream`. Nathan started it on 29 September, on Opus 5.5 at high (TypeSafe v6 read the same cell). No Dev Manager read of it is needed. Then C1's exact-head review.
  - **Linear (OD-29):** one session at a time, one prompt per message. Other feature work stays paused.
- **The [HDE contract request](../planning/hde-contract-request.md)** (OD-23): in Nathan's own process; on delivery, record the receipt (its section 6); not a standing item for him (OD-32).
- **Dev Manager 2:** session `session_015DxVkL8PXn2YaauE6RdSWN`, created by Dev Manager 1 (OD-35); branch `claude/dev-manager`; the [review log](dev-manager/README.md) holds DM-01 to DM-08, each with its disposition.
- **Environments** (OD-36): every prompt names one; `Glow app` only for a session that calls Stream.

## Waiting checkpoint (29 September 2026, App Manager 5)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 5 | The P06.DB-C1 correction session, via Nathan | Its report: F1 to F4 fixed with their tests, the records corrected, and the run of record on its last code commit with each race's measured overlaps | Nothing to chase: Nathan runs the session when he chooses; the next step waits on its report |

## Next actions

1. Verify C1's report against its branch and its run; integrate it; add the manager's verification to its section of the evidence record; settle the P11 plan's DB06 limit from the new per-race counts. Then C1's exact-head review prompt, with the TypeSafe reading (environment `Glow App - No Stream`).
2. Before PR28 merges: the Dev Manager reads its governing changes (the CI policy, the workflow's Notion checklist line and its supersession-sweep line, AM5-13) and confirms the changes the review log's DM-07 section lists; then Codex, the merge and the receipt; then P06.2.
3. Standing: before the Stream harness is used live again, the C5 review's nits 2 and 3 and its header-allowlist advice; before the next Dev Manager session, rewrite its start prompt (DM-03 E3; DM-07 item 7).

**Recorded follow-ups:** prune the P06.1 prompts in `docs/ephemeral/` once their links are commit-pinned; Setup-script and pin-test hardening ([M02 brief](../planning/claude-setup-optimization.md)); a stale-documentation sweep of `docs/architecture/`, `docs/testing/` and `docs/operations/`.

## Branches

- **PR27** merged at `47db18d`: P06.1's code (I1, the flake fix, C1 to C5, I2a, I2b) and its records. PR28 starts from it.
- **PR28** (draft) carries P06.DB: its brief, prompts and records, and since the merge commit `6f5866d` the session branch `claude/epic-maxwell-e4zomh` (the proof package and the new Foundation job).
- `claude/dev-manager` merges into the manager branch at each consultation's integration.
- Retire the unmerged `app-builder-1/p05-1-birth-diagnostics` once its content is confirmed recorded; every other remote branch is merged into `main`.

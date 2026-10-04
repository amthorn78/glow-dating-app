# Current handoff — App Manager 5 (29 September 2026, after PR27)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); the earlier handoff is [archived](history/m02-p06-1-handoff.md).

- **Process:** Nathan's manual relay, per the [manager workflow](../planning/manager-workflow.md), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25).
- **Standing directions:** the [owner-direction register](owner-directions.md); Notion carries a copy, and the repository wins (OD-26, OD-27).
- **A new manager** starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager:** App Manager 5 (`session_01Xv2QTYGpc5bSQQoVeWiN4E`), started by Nathan by hand on 27 September. Its branch `claude/magical-wozniak-yfmmx2` restarted from `main` at `47db18d` after PR27 merged; draft PR28 carries the next item.
- **P06.1 is done** (merged 29 September at `47db18d`): the [brief](../planning/p06-1-chat-provider-proof.md) and the [evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md), with its merge receipt. The display rule ([ADR 0003](../adr/0003-chat-display-rule.md)) stands; the development application stays locked down (OD-37). P06.2 inherits the brief's "Carried to P06.2".
- **Current item: P06.DB**, the early disposable-PostgreSQL proof (OD-17, PF01 §6): the [brief](../planning/p06-db-disposable-postgres-proof.md), revision 2, which applies the Dev Manager's read ([DM-08](dev-manager/reviews/2026-09-29-dm-08-p06-db-brief.md)) as written.
  - **The implementation is done and integrated** into PR28 at `6f5866d` (29 September). Its run of record, Foundation run 36520940933 on `dff83d4`, passed every job. The manager's verification, its corrections and five observations are in the [evidence record](../testing/evidence/2026-09-29-p06-db-disposable-postgres-proof.md). The P11 plan's DB06 and DB09 are marked partially evidenced in CI, DB06's now resting on C1's run, and the CI policy names the new job.
  - **Its exact-head review** of `6f5866d` ([prompt](../ephemeral/2026-09-29-p06-db-review-prompt.md)), run by Nathan on 29 September on Fable 5.1 at max: **changes required, narrowly.** F1, in a correction class: the stress run's per-race overlap count read every race's rows at the same iteration number. F2: the oracle's O2 misses a send stored at the version a revocation set. Four nits. The manager verified and recorded it, with its disposition, in the evidence record; F5 and F6 are done, and AM5-12 is logged.
  - **P06.DB-C1, the correction pass, is done** ([prompt](../ephemeral/2026-09-29-p06-db-c1-correction-prompt.md)), run by Nathan on 29 September on Opus 5.5 at high, and integrated at `ea21ac8`: F1 to F4 fixed, each with a test. Foundation run 36534514283 on its code head `4280770` is the run of record: every job passed, and each race measured its own overlaps, 174 to 200 of 200. Its run-level status reads `cancelled` because the session's records push started a second run on the same branch; the manager accepted the job results and recorded the label as a limit (AM5-14). The manager's verification is in the evidence record, and the P11 plan's DB06 limit is settled.
  - **A second run of the C1 correction prompt** (4 October): the session Nathan started that day, on Opus 5.5 at extra high, had been given the C1 correction prompt, not the review's, and its start gate could not tell that C1 was done (AM5-15). It made the pass again on `claude/magical-goldberg-ie0j16`, and its run passed. The manager recorded it in the evidence record and did not integrate it. Its two points about PR28's code, the stress run's commit orders and its fixed run tag, go to C1's review; AM5-16 is the manager's miss of the second in C1's local run 2.
  - **Next: C1's exact-head review** ([prompt](../ephemeral/2026-09-29-p06-db-c1-review-prompt.md), revision 2), of `ea21ac8`, offline, in `Glow App - No Stream`. Given to Nathan on 4 October; revision 1 never ran. No Dev Manager read of it is needed. Then the Dev Manager's read of PR28's governing changes, Codex and the merge.
  - **Linear (OD-29):** one session at a time, one prompt per message. Other feature work stays paused.
- **The [HDE contract request](../planning/hde-contract-request.md)** (OD-23): in Nathan's own process; on delivery, record the receipt (its section 6); not a standing item for him (OD-32).
- **Dev Manager 2:** session `session_015DxVkL8PXn2YaauE6RdSWN`, created by Dev Manager 1 (OD-35); branch `claude/dev-manager`; the [review log](dev-manager/README.md) holds DM-01 to DM-08, each with its disposition.
- **Environments** (OD-36): every prompt names one; `Glow app` only for a session that calls Stream.

## Waiting checkpoint (4 October 2026, App Manager 5)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 5 | The P06.DB-C1 exact-head review session (revision 2), via Nathan | Its report: verdict, findings with their classes, the log checks, focus area 10's two points, and its view of the manager's run-of-record decision, observations, DB06 wording and correction to C1's local run 2 | Nothing to chase: Nathan runs the session when he chooses; the next step waits on its report |

## Next actions

1. Verify the C1 review's report against `ea21ac8` and the log, and record it with its disposition in the evidence record. Then a correction pass if it asks for one, or the Dev Manager's read of PR28's governing changes.
2. Before PR28 merges: the Dev Manager reads its governing changes (the CI policy, and the workflow's Notion checklist line, its supersession-sweep line (AM5-13), its push-timing line (AM5-14) and its stale-prompt start-gate line with the prompt template's start-gate line (AM5-15)) and confirms the changes the review log's DM-07 section lists; then Codex, the merge and the receipt; then P06.2.
3. Standing: before the Stream harness is used live again, the C5 review's nits 2 and 3 and its header-allowlist advice; before the next Dev Manager session, rewrite its start prompt (DM-03 E3; DM-07 item 7).

**Recorded follow-ups:** prune the P06.1 prompts in `docs/ephemeral/` once their links are commit-pinned; Setup-script and pin-test hardening ([M02 brief](../planning/claude-setup-optimization.md)); a stale-documentation sweep of `docs/architecture/`, `docs/testing/` and `docs/operations/`.

## Branches

- **PR27** merged at `47db18d`: P06.1's code (I1, the flake fix, C1 to C5, I2a, I2b) and its records. PR28 starts from it.
- **PR28** (draft) carries P06.DB: its brief, prompts and records, and since the merge commit `6f5866d` the session branch `claude/epic-maxwell-e4zomh` (the proof package and the new Foundation job).
- `claude/dev-manager` merges into the manager branch at each consultation's integration.
- `claude/magical-goldberg-ie0j16`: the second run of the C1 correction prompt (4 October), recorded and not integrated; retire it after PR28 merges.
- Retire the unmerged `app-builder-1/p05-1-birth-diagnostics` once its content is confirmed recorded; every other remote branch is merged into `main`.

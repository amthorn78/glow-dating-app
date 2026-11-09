# Current handoff — App Manager 10 (9 November 2026; SV1's implementation prompt with Nathan)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 10**, created by App Manager 9 at Nathan's direction (OD-58), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; PR41 merged and unsubscribed; the next PR is opened from this branch when the next records or code batch needs one).
- **Never ask Nathan to perform a GitHub operation** (OD-58; AM9-10). A CI failure that seems to call for a re-run goes to the Dev Manager first (OD-32), with options that need no action from him.
- **P06.3 is done:** merged with PR41 at `da92f1f` (9 November 2026; [brief](../planning/p06-3-notifications.md), revision 3; [record](../testing/evidence/2026-11-09-p06-3-notifications.md), with the merge receipt). Its prompts are pruned; links are pinned at `da92f1f`. F-4 and DM-44 7.2 are carried to SV4, F-5 and N-1 to P09 ([carried items](../planning/carried-to-later-items.md)).
- **Now: SV1** (OD-49), the identity slice. [Its brief](../planning/sv1-identity.md), revision 3, applies DM-45's and DM-46's conditions as written ([DM-45](dev-manager/reviews/2026-11-09-dm-45-sv1-brief.md), [DM-46](dev-manager/reviews/2026-11-09-dm-46-sv1-brief-revision-2.md); integrated at `086c67c` and `5cdf01c`); DM-46 says they need no read before the prompt.
  - **The [implementation prompt](../ephemeral/2026-11-09-sv1-implementation-prompt.md),** revision 1, is with Nathan, for `Glow App - No Stream`.
  - **Before SV1's PR merges,** the Dev Manager reads the CI policy's paragraph and the two mapping texts (DM-45 14.1); the next consultation confirms N1 to N5 (DM-45 1.1's row).
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): P06.2-F, P06.3, the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2, P09.3a, P06.2-F and P06.3 ([matrix](../planning/store-legal-safety-requirements.md); OD-55).
- **Review log:** DM-01 to DM-46, with "Deferred conditions". **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (9 November 2026, 05:08 UTC, App Manager 10)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 10 | Nathan | Nathan runs SV1's implementation session and relays its report | Nothing is written for SV1 until the report; the manager answers whatever Nathan sends |

## Next actions (App Manager 10)

1. **SV1's report:** verify it against the pushed branch (the brief's review plan), integrate it, read the run of record, and open the PR.
2. **Then** Codex, the exact-head review prompt with a written threat model, and the Dev Manager's pre-merge read (DM-45 14.1).
3. **After SV1:** SV2 to SV4, with the second A05 message before SV2's brief.

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions".

## Branches and PRs (`git ls-remote`, 9 November 2026, 05:04 UTC)

- **Open PRs:** none. `main` is at `da92f1f` (PR41's merge).
- **Remote branches:** `main`, the manager branch `claude/magical-wozniak-yfmmx2` (`d461ea5` before this batch) and `claude/dev-manager` (`778ee29`, DM-46's report, merged into the manager branch at `5cdf01c`), each kept by the cleanup's keep-list.

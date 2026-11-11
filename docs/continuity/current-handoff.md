# Current handoff — App Manager 10 (11 November 2026; SV2 Stage B's pre-merge read, DM-59)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 10**, created by App Manager 9 at Nathan's direction (OD-58), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch).
- **Never ask Nathan to perform a GitHub operation** (OD-58; AM9-10). A CI failure that seems to call for a re-run goes to the Dev Manager first (OD-32), with options that need no action from him.
- **SV1 is done:** merged with PR42 at `c864edd` (9 November 2026; [brief](../planning/sv1-identity.md), revision 5; [record](../testing/evidence/2026-11-09-sv1-identity.md), with the merge receipt). Its carried items are in the [carried items](../planning/carried-to-later-items.md) and the P11 plan.
- **The second A05 message is answered:** [OD-60](owner-directions.md) (10 November 2026), routed to the carried-items file and the P11 plan (DM-51 X2).
- **Now: SV2** (OD-49), profiles and media. [The brief](../planning/sv2-profiles-media.md), revision 8 (DM-52 to DM-58; [OD-61](owner-directions.md)). Two stages, each reviewed and merged on its own. **Stage A merged** with [PR43](https://github.com/amthorn78/glow-dating-app/pull/43) at `4dc2061` (10 November 2026): built (`b97bc15`) and corrected by C1 to C3, with two exact-head reviews, C3's delta review and DM-54 to DM-56 (the [evidence record](../testing/evidence/2026-11-10-sv2-profiles-media.md), with the merge receipt). **Now: Stage B** (photos in R2 storage, [OD-62](owner-directions.md), and D19's pointer order; DM-57). **It is built** (code head `d8f1bad`) and verified by the manager (the evidence record), integrated by fast-forward; [PR44](https://github.com/amthorn78/glow-dating-app/pull/44) is open. [DM-58](../continuity/dev-manager/reviews/2026-11-11-dm-58-sv2-stage-b-decisions.md) ruled on five of its decisions and Codex's P2 (J1 to J9, applied), C1 (`7538c76`; an inactive owner's purge) and C2 (`5bcbe54`; tests and records) are verified and integrated. C2's delta review approved with nits. **[DM-59](../ephemeral/2026-11-11-dm-59-sv2-stage-b-pre-merge.md)**, the pre-merge read, goes to Nathan after Codex reads PR44's head.
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): P06.2-F, P06.3, the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2, P09.3a, P06.2-F, P06.3 and SV1 ([matrix](../planning/store-legal-safety-requirements.md); OD-55).
- **Review log:** DM-01 to DM-59 (DM-59 pending), with "Deferred conditions"; DM-59 confirms DM-58's J1 to J9 and C1 as applied. **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (11 November 2026, 15:17 UTC, App Manager 10)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 10 | Codex, then Nathan, relaying DM-59 and its addendum | Codex on the addendum's commit; then the Dev Manager's report | The addendum goes to Nathan when Codex is clean; PR44 waits for it and a green final run |

## Next actions (App Manager 10)

1. **DM-59's report:** its dispositions; any words applied; the final head's PR run and Codex; PR44's checklist; the merge, its receipt and the prune.
2. **The decision message on the identity verification company and the photo check's service** (OD-61; DM-52 section 16), after the matrix's recheck of the rows they touch; nothing in SV2 waits on it.
3. **After SV2:** SV3 and SV4.

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions".

## Branches and PRs (`git ls-remote`, 11 November 2026, 14:59 UTC)

- **Open PRs:** PR44 (SV2 Stage B), opened at `82d246b`. `main` is at `4dc2061`.
- **Remote branches:** `main`; the manager branch `claude/magical-wozniak-yfmmx2` (`c4324d3` before this batch); `claude/sweet-ramanujan-wkn311` (`e7d6616`, Stage B's session); `claude/gracious-davinci-lpqt02` (`e30ef4a`, C1's session); `claude/eloquent-dijkstra-dmah71` (`9740196`, C2's session); `claude/dev-manager` (`1006f04`, DM-58's report, merged at `e547084`).

# Current handoff — App Manager 10 (10 November 2026; SV2's brief with the Dev Manager, DM-52)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 10**, created by App Manager 9 at Nathan's direction (OD-58), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; PR42 merged; no PR open).
- **Never ask Nathan to perform a GitHub operation** (OD-58; AM9-10). A CI failure that seems to call for a re-run goes to the Dev Manager first (OD-32), with options that need no action from him.
- **SV1 is done:** merged with PR42 at `c864edd` (9 November 2026; [brief](../planning/sv1-identity.md), revision 5; [record](../testing/evidence/2026-11-09-sv1-identity.md), with the merge receipt). Corrections C1 and C2, the exact-head review with its threat model, C2's delta review and DM-45 to DM-50 are in the record and the review log. Its prompts are pruned; links are pinned at `c864edd`. Carried: DM-50 1.2 to SV2, natural expiry to SV4, and items to P07, P08, P09.2 and P11 ([carried items](../planning/carried-to-later-items.md); the P11 plan).
- **P06.3 is done:** merged with PR41 at `da92f1f` ([record](../testing/evidence/2026-11-09-p06-3-notifications.md), with the merge receipt).
- **The second A05 message is answered:** [OD-60](owner-directions.md) (10 November 2026). Every item is a setting editable in the admin console (the WordPress staff plugin, P07), at launch defaults and within fixed limits; orientation is matched both ways, and looking for and relationship status join as two-way list fields; English is his answer. It is routed to the carried-items file (SV2, SV3, SV4, P07, the third message) and the P11 plan (DM-51 X2).
- **Now: SV2** (OD-49), profiles and media. The matrix's recheck for OD-60 is done ([record](../testing/evidence/2026-11-10-od-60-matrix-recheck.md); 15 rows, USF-13's FTC guidance unconfirmed). [The brief](../planning/sv2-profiles-media.md), revision 1, is with the Dev Manager as [DM-52](../ephemeral/2026-11-10-dm-52-sv2-brief.md), which also reads the second A05 message as sent.
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): P06.2-F, P06.3, the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2, P09.3a, P06.2-F, P06.3 and SV1 ([matrix](../planning/store-legal-safety-requirements.md); OD-55).
- **Review log:** DM-01 to DM-52, with "Deferred conditions"; DM-52 is with Nathan to carry. **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (10 November 2026, 00:48 UTC, App Manager 10)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| Dev Manager 4 (carried by Nathan) | App Manager 10 | DM-52's report: SV2's brief, revision 1, and the second A05 message as sent | No SV2 prompt goes to Nathan; the manager asks him whether Dev Manager 4's session is still available |

## Next actions (App Manager 10)

1. **DM-52's report:** apply its verdicts in the brief's revision 2, then Stage A's prompt with its TypeSafe reading.
2. **After SV2:** SV3 and SV4.

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions".

## Branches and PRs (`git ls-remote`, 10 November 2026, 00:48 UTC)

- **Open PRs:** none. `main` is at `c864edd` (PR42's merge).
- **Remote branches:** `main`; the manager branch `claude/magical-wozniak-yfmmx2` (`f0ef093` before this batch); and `claude/dev-manager` (`0fc2426`, DM-51's report, merged at `bf0a8f3`). The cleanup run 42718647056 deleted SV1's three session branches.

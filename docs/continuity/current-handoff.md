# Current handoff — App Manager 10 (9 November 2026; SV1 merged; the second A05 message next)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 10**, created by App Manager 9 at Nathan's direction (OD-58), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; PR42 merged; no PR open).
- **Never ask Nathan to perform a GitHub operation** (OD-58; AM9-10). A CI failure that seems to call for a re-run goes to the Dev Manager first (OD-32), with options that need no action from him.
- **SV1 is done:** merged with PR42 at `c864edd` (9 November 2026; [brief](../planning/sv1-identity.md), revision 5; [record](../testing/evidence/2026-11-09-sv1-identity.md), with the merge receipt). Corrections C1 and C2, the exact-head review with its threat model, C2's delta review and DM-45 to DM-50 are in the record and the review log. Its prompts are pruned; links are pinned at `c864edd`. Carried: DM-50 1.2 to SV2, natural expiry to SV4, and items to P07, P08, P09.2 and P11 ([carried items](../planning/carried-to-later-items.md); the P11 plan).
- **P06.3 is done:** merged with PR41 at `da92f1f` ([record](../testing/evidence/2026-11-09-p06-3-notifications.md), with the merge receipt).
- **Now: the second A05 message,** before SV2's brief (DM-37 4.5; OD-50: the open A05 questions go to Nathan in OD-32's form). It confirms the language in one line (the carried-items file, "Carried to the second A05 message").
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): P06.2-F, P06.3, the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2, P09.3a, P06.2-F, P06.3 and SV1 ([matrix](../planning/store-legal-safety-requirements.md); OD-55).
- **Review log:** DM-01 to DM-50, with "Deferred conditions"; DM-50's confirmation rides the next consultation. **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (9 November 2026, 23:16 UTC, App Manager 10)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| Nathan | App Manager 10 | The second A05 message | Nothing is owed; the manager writes it next |

## Next actions (App Manager 10)

1. **The second A05 message** (OD-32's form), before SV2's brief.
2. **Then** SV2's brief, with the matrix's G-02 and G-10 and DM-50 1.2 (the carried-items file, "Carried to SV2").
3. **After SV2:** SV3 and SV4.

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions".

## Branches and PRs (`git ls-remote`, 9 November 2026, 23:14 UTC)

- **Open PRs:** none. `main` is at `c864edd` (PR42's merge).
- **Remote branches:** `main`; the manager branch `claude/magical-wozniak-yfmmx2` (`df8a04c` before this batch); and `claude/dev-manager` (`85df720`). The cleanup run 42718647056 deleted SV1's three session branches.

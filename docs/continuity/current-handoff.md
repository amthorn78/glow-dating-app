# Current handoff — App Manager 10 (10 November 2026; SV2's brief, revision 3, after DM-53; Stage A's prompt with Nathan)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 10**, created by App Manager 9 at Nathan's direction (OD-58), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; PR42 merged; no PR open).
- **Never ask Nathan to perform a GitHub operation** (OD-58; AM9-10). A CI failure that seems to call for a re-run goes to the Dev Manager first (OD-32), with options that need no action from him.
- **SV1 is done:** merged with PR42 at `c864edd` (9 November 2026; [brief](../planning/sv1-identity.md), revision 5; [record](../testing/evidence/2026-11-09-sv1-identity.md), with the merge receipt). Corrections C1 and C2, the exact-head review with its threat model, C2's delta review and DM-45 to DM-50 are in the record and the review log. Its prompts are pruned; links are pinned at `c864edd`. Carried: DM-50 1.2 to SV2, natural expiry to SV4, and items to P07, P08, P09.2 and P11 ([carried items](../planning/carried-to-later-items.md); the P11 plan).
- **P06.3 is done:** merged with PR41 at `da92f1f` ([record](../testing/evidence/2026-11-09-p06-3-notifications.md), with the merge receipt).
- **The second A05 message is answered:** [OD-60](owner-directions.md) (10 November 2026). Every item is a setting editable in the admin console (the WordPress staff plugin, P07), at launch defaults and within fixed limits; orientation is matched both ways, and looking for and relationship status join as two-way list fields; English is his answer. It is routed to the carried-items file (SV2, SV3, SV4, P07, the third message) and the P11 plan (DM-51 X2).
- **Now: SV2** (OD-49), profiles and media. [The brief](../planning/sv2-profiles-media.md), revision 3, applies [DM-52](dev-manager/reviews/2026-11-10-dm-52-sv2-brief.md)'s B1 to B55 and [DM-53](dev-manager/reviews/2026-11-10-dm-53-sv2-stage-a-paths.md)'s W1 to W10 as written, with Nathan's answers ([OD-61](owner-directions.md): the chart at once, a birth time, no staff review, automated ID and photo checks, staff approval without ID behind a setting). Two stages, each reviewed and merged on its own. **Stage A's [prompt](../ephemeral/2026-11-10-sv2-stage-a-implementation-prompt.md)** is with Nathan.
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): P06.2-F, P06.3, the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2, P09.3a, P06.2-F, P06.3 and SV1 ([matrix](../planning/store-legal-safety-requirements.md); OD-55).
- **Review log:** DM-01 to DM-53, with "Deferred conditions"; the next consultation confirms DM-53's conditions as applied. **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (10 November 2026, 02:43 UTC, App Manager 10)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 10 | Nathan, running Stage A's session | The session's report (prompt given to Nathan 10 November, 02:43 UTC) | Nothing is owed; the manager verifies the report against the pushed branch when it arrives |

## Next actions (App Manager 10)

1. **Stage A's report:** verify it against the pushed branch, then the PR, Codex's review and the exact-head review with its threat model (the brief's "Review plan").
2. **The decision message on the identity verification company and the photo check's service** (OD-61; DM-52 section 16), after the matrix's recheck of the rows they touch; nothing in SV2 waits on it.
3. **After SV2:** SV3 and SV4.

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions".

## Branches and PRs (`git ls-remote`, 10 November 2026, 02:43 UTC)

- **Open PRs:** none. `main` is at `c864edd` (PR42's merge).
- **Remote branches:** `main`; the manager branch `claude/magical-wozniak-yfmmx2` (`c2ee87a` before this batch); and `claude/dev-manager` (`f60cfda`, DM-53's report, merged at `c27006f`). The cleanup run 42718647056 deleted SV1's three session branches.

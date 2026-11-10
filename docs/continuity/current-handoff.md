# Current handoff — App Manager 10 (10 November 2026; SV2 Stage A corrected; its exact-head review with Nathan)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 10**, created by App Manager 9 at Nathan's direction (OD-58), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch).
- **Never ask Nathan to perform a GitHub operation** (OD-58; AM9-10). A CI failure that seems to call for a re-run goes to the Dev Manager first (OD-32), with options that need no action from him.
- **SV1 is done:** merged with PR42 at `c864edd` (9 November 2026; [brief](../planning/sv1-identity.md), revision 5; [record](../testing/evidence/2026-11-09-sv1-identity.md), with the merge receipt). Its carried items are in the [carried items](../planning/carried-to-later-items.md) and the P11 plan.
- **The second A05 message is answered:** [OD-60](owner-directions.md) (10 November 2026). Every item is a setting editable in the admin console (the WordPress staff plugin, P07), at launch defaults and within fixed limits; orientation is matched both ways, and looking for and relationship status join as two-way list fields; English is his answer. It is routed to the carried-items file (SV2, SV3, SV4, P07, the third message) and the P11 plan (DM-51 X2).
- **Now: SV2** (OD-49), profiles and media. [The brief](../planning/sv2-profiles-media.md), revision 4 (DM-52 to DM-54; [OD-61](owner-directions.md)). Two stages, each reviewed and merged on its own. **Stage A** is on [PR43](https://github.com/amthorn78/glow-dating-app/pull/43): built (`b97bc15`), corrected by C1 (code head `86a2156`, run of record 42769301337, every job passed), integrated at `6e5d0d1` with the manager's verification in the [evidence record](../testing/evidence/2026-11-10-sv2-profiles-media.md). **Its exact-head [review prompt](../ephemeral/2026-11-10-sv2-stage-a-review-prompt.md)**, revision 2 (Codex's P2 on C1-3 added), is with Nathan.
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): P06.2-F, P06.3, the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2, P09.3a, P06.2-F, P06.3 and SV1 ([matrix](../planning/store-legal-safety-requirements.md); OD-55).
- **Review log:** DM-01 to DM-54, with "Deferred conditions"; the next consultation confirms DM-53's and DM-54's conditions as applied. **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (10 November 2026, 13:19 UTC, App Manager 10)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 10 | Nathan, running the exact-head review | The review's report (revision 2, given after Codex's review of its commit) | Nothing is owed; the manager records and dispositions each finding when it arrives |

## Next actions (App Manager 10)

1. **The exact-head review's report:** record it with a disposition for each finding; then a correction if one is needed, the Dev Manager's pre-merge read (the CI policy's paragraph, the mapping texts, C1-1 and C1-3), the PR run and Codex on the final head, and the merge.
2. **The decision message on the identity verification company and the photo check's service** (OD-61; DM-52 section 16), after the matrix's recheck of the rows they touch; nothing in SV2 waits on it.
3. **After SV2:** SV3 and SV4.

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions".

## Branches and PRs (`git ls-remote`, 10 November 2026, 13:19 UTC)

- **Open PRs:** [PR43](https://github.com/amthorn78/glow-dating-app/pull/43), SV2 Stage A, from the manager branch. `main` is at `c864edd` (PR42's merge).
- **Remote branches:** `main`; the manager branch `claude/magical-wozniak-yfmmx2` (`40db2c2` before this batch); `claude/dev-manager` (`1271ca5`, DM-54's report, merged at `6aa8f53`); Stage A's session branch `claude/sv2-stage-a-impl-0qqzvj` (`f2635fa`, merged at `e0c0ffe`) and C1's `claude/funny-lamport-5f2s1u` (`f54545c`, merged at `6e5d0d1`), kept until the cleanup deletes them after the merge to `main`.

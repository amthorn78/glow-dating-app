# Current handoff — App Manager 10 (9 November 2026; SV1 implemented and verified; DM-47 with Nathan)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 10**, created by App Manager 9 at Nathan's direction (OD-58), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; PR41 merged and unsubscribed; the next PR is opened from this branch when the next records or code batch needs one).
- **Never ask Nathan to perform a GitHub operation** (OD-58; AM9-10). A CI failure that seems to call for a re-run goes to the Dev Manager first (OD-32), with options that need no action from him.
- **P06.3 is done:** merged with PR41 at `da92f1f` (9 November 2026; [brief](../planning/p06-3-notifications.md), revision 3; [record](../testing/evidence/2026-11-09-p06-3-notifications.md), with the merge receipt). Its prompts are pruned; links are pinned at `da92f1f`. F-4 and DM-44 7.2 are carried to SV4, F-5 and N-1 to P09 ([carried items](../planning/carried-to-later-items.md)).
- **Now: SV1** (OD-49), the identity slice. [Its brief](../planning/sv1-identity.md), revision 3, applies DM-45's and DM-46's conditions as written ([DM-45](dev-manager/reviews/2026-11-09-dm-45-sv1-brief.md), [DM-46](dev-manager/reviews/2026-11-09-dm-46-sv1-brief-revision-2.md); integrated at `086c67c` and `5cdf01c`); DM-46 says they need no read before the prompt.
  - **Implemented** on `claude/hopeful-cerf-kc91xx` (code head `269ac3b`) and **verified** by the manager ([record](../testing/evidence/2026-11-09-sv1-identity.md), "Manager verification"); integrated into the manager branch, and SV1's PR is opened from it after this batch's push.
  - **An email change needs no reauthentication** at `269ac3b` (AM10-06). [DM-47](../ephemeral/2026-11-09-dm-47-sv1-email-change-reauthentication.md) puts it to the Dev Manager, with correction C1's words, before the exact-head review; it also confirms N1 to N5 (DM-45 1.1's row).
  - **Before SV1's PR merges,** the Dev Manager reads the CI policy's paragraph and the two mapping texts at the final head (DM-45 14.1).
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): P06.2-F, P06.3, the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2, P09.3a, P06.2-F and P06.3 ([matrix](../planning/store-legal-safety-requirements.md); OD-55).
- **Review log:** DM-01 to DM-47, with "Deferred conditions". **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (9 November 2026, 12:52 UTC, App Manager 10)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 10 | Nathan, then Dev Manager 4 | DM-47's report | No correction or review prompt for SV1; the manager asks Nathan whether Dev Manager 4's session is still available |
| App Manager 10 | Codex | Its review of SV1's PR head | After 60 minutes with no result, the manager posts `@codex review` once (step 6) |

## Next actions (App Manager 10)

1. **DM-47's report:** dispose of it, apply its words, and write correction C1's prompt for the implementation session, with its TypeSafe reading, once Codex has read the head.
2. **Then** C1's run of record, Codex on C1's head, the exact-head review prompt with a written threat model, and the Dev Manager's pre-merge read (DM-45 14.1).
3. **After SV1:** SV2 to SV4, with the second A05 message before SV2's brief.

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions".

## Branches and PRs (`git ls-remote`, 9 November 2026, 12:51 UTC)

- **Open PRs:** none before this batch; SV1's PR is opened from the manager branch after its push. `main` is at `da92f1f` (PR41's merge).
- **Remote branches:** `main`; the manager branch `claude/magical-wozniak-yfmmx2` (`dc3e551` before this batch, which fast-forwards it to `157c1f6` and adds the records); `claude/dev-manager` (`778ee29`); and SV1's session branch `claude/hopeful-cerf-kc91xx` (`157c1f6`), which C1 continues.

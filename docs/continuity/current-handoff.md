# Current handoff — App Manager 10 (9 November 2026; DM-49 on runs lost to GitHub's Actions incident with Nathan)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 10**, created by App Manager 9 at Nathan's direction (OD-58), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; PR41 merged; SV1's PR42 open from it, subscribed).
- **Never ask Nathan to perform a GitHub operation** (OD-58; AM9-10). A CI failure that seems to call for a re-run goes to the Dev Manager first (OD-32), with options that need no action from him.
- **P06.3 is done:** merged with PR41 at `da92f1f` (9 November 2026; [brief](../planning/p06-3-notifications.md), revision 3; [record](../testing/evidence/2026-11-09-p06-3-notifications.md), with the merge receipt). Its prompts are pruned; links are pinned at `da92f1f`. F-4 and DM-44 7.2 are carried to SV4, F-5 and N-1 to P09 ([carried items](../planning/carried-to-later-items.md)).
- **Now: SV1** (OD-49), the identity slice. [Its brief](../planning/sv1-identity.md), revision 5, applies DM-45's to DM-48's conditions as written.
  - **Implemented** on `claude/hopeful-cerf-kc91xx` (code head `269ac3b`) and **verified** by the manager ([record](../testing/evidence/2026-11-09-sv1-identity.md), "Manager verification"); integrated; [PR42](https://github.com/amthorn78/glow-dating-app/pull/42) is open.
  - **Correction C1** ([DM-47](dev-manager/reviews/2026-11-09-dm-47-sv1-email-change.md)): reauthentication for an email change; the results upload checked first. Done at `bda299e` and verified; integrated.
  - **The exact-head review** of `bda299e`: changes required, with no blocking finding (the record, "Exact-head review of SV1").
  - **Correction C2** (the brief, "Correction C2"; [DM-48](dev-manager/reviews/2026-11-09-dm-48-sv1-review-c2.md)): `change_password` at `5/300s/user` (F-2), the no-link check (F-1), F-3 to F-7. Done at code head `6da8061` (run 42669825647) and verified; integrated. [Its delta review prompt](../ephemeral/2026-11-09-sv1-c2-delta-review-prompt.md) waits for [DM-49](../ephemeral/2026-11-09-dm-49-sv1-lost-runs.md) (runs lost to GitHub's Actions incident).
  - **Before SV1's PR merges,** the Dev Manager reads the CI policy's paragraph and the two mapping texts at the final head, and confirms C2.1 to C2.8 as applied (DM-45 14.1).
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): P06.2-F, P06.3, the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2, P09.3a, P06.2-F and P06.3 ([matrix](../planning/store-legal-safety-requirements.md); OD-55).
- **Review log:** DM-01 to DM-49, with "Deferred conditions". **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (9 November 2026, 18:40 UTC, App Manager 10)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 10 | Nathan, then Dev Manager 4 | DM-49's report | The delta review prompt is not given; the manager asks Nathan whether Dev Manager 4's session is still available |

## Next actions (App Manager 10)

1. **DM-49's report:** dispose of it; give Nathan the delta review prompt as it decides; dispose of that review.
2. **Then** Codex on the final head, and the Dev Manager's pre-merge read (DM-45 14.1, with C2.1 to C2.8 as applied); then the merge.
3. **After SV1:** SV2 to SV4, with the second A05 message before SV2's brief.

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions".

## Branches and PRs (`git ls-remote`, 9 November 2026, 18:25 UTC)

- **Open PRs:** [PR42](https://github.com/amthorn78/glow-dating-app/pull/42), SV1, from the manager branch. `main` is at `da92f1f` (PR41's merge).
- **Remote branches:** `main`; the manager branch `claude/magical-wozniak-yfmmx2` (`2f577f8` before this batch); `claude/dev-manager` (`c6bce37`); and the three SV1 session branches, `claude/hopeful-cerf-kc91xx` (`157c1f6`), C1's `claude/stoic-franklin-ief71e` (`96dc3e2`) and C2's `claude/trusting-goldberg-e4ogat` (`080c9a9`).

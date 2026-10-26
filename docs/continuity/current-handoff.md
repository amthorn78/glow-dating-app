# Current handoff — App Manager 8 (26 October 2026; M04 and M05 done; DM-34's pre-merge read of the records PR)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 8** (OD-46), in `Glow App - No Stream`, with the manager branch `claude/magical-wozniak-yfmmx2` as its outcome branch.
- **M05 is done** ([brief](../planning/m05-whole-project-review.md); [record](../testing/evidence/2026-10-25-m05-project-review.md)): PR34 (`4aa66e2`) and Nathan's three answers (OD-49, OD-50, OD-53).
- **M04 is done** (OD-39; M05 findings 10, 11, 12 and 14): PR36 merged at `4794d3e`; the first cleanup run deleted the three expected branches ([record](../testing/evidence/2026-10-26-m04-branch-hygiene.md), "M04's merge receipt"). Since then, every merge into `main` deletes the fully merged branches (the CI policy, "Branch cleanup").
- **Branch controls:** Nathan chose none, procedure only (OD-52), against [DM-33](dev-manager/reviews/2026-10-26-dm-33-pr36-pre-merge-read.md)'s recommended ruleset. The CI policy's three sentences that record it wait for the Dev Manager's read with the next PR.
- **OD-53:** S2 (delta re-reviews for small corrections), S5 (Notion's procedure as a summary), D1 (no pick asked or recorded) and `@codex review` after a 60-minute stall, all adopted.
- **Now:** the records PR since PR36 ([PR37](https://github.com/amthorn78/glow-dating-app/pull/37), docs only) waits for [DM-34](../ephemeral/2026-10-26-dm-34-od-52-od-53-pre-merge-read.md), the Dev Manager's read of OD-52's and OD-53's texts, and for Codex. Codex did not review it: at 18:12 UTC it answered "To use Codex here, create an environment for this repo" (it reviewed PR36 at 17:01 UTC).
- **The repository is public for now** (OD-51), for budget reasons; Nathan intends to make it private again. When he does, `'ccr-**'` comes out or its minutes are approved, and the costed list (M07) carries GitHub Actions; he tells the manager first.
- **The order after M04** (OD-49): M06, P09.3a, P06.2-F, P06.3, the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M04, P06.1, P06.DB and P06.2.
- **Dev Manager 3:** `session_01KVuPEpFRh9B22beZKTKb27` (OD-47); review log DM-01 to DM-33, with "Deferred conditions".
- **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (26 October 2026, App Manager 8)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 8 | Nathan (a relay to Dev Manager 3) | DM-34's report | The manager asks Nathan whether the session is available; the records PR does not merge without the read |
| App Manager 8 | Nathan | Codex's environment for this repository, or his direction | Step 7 merges only after Codex's review of the final head, and step 6 holds review prompts for it; PR37 and M06's review prompts wait |

## Next actions (App Manager 8)

1. **The records PR:** DM-34's read and Codex's review, then the merge with the checklist (docs only).
2. **M06's brief,** named to Nathan before it starts (OD-49).
3. **Then** P09.3a, P06.2-F, P06.3 and the slices, each named to Nathan before it starts (OD-49).

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions". The prompts' pruning is M05 finding 44, a manager batch with OD-45's D8 link pinned first.

## Branches and PRs (`git ls-remote`, 26 October 2026, 17:30 UTC)

- **Open:** PR37, the records since PR36, from the manager branch (head `8cffa1e` at 18:15 UTC; PR run 40376061139 passed as ordinary documentation).
- **Kept, by the cleanup's keep-list:** `main` (`4794d3e`), the manager branch (the records since PR36 on top of it), and `claude/dev-manager` (`8855163`, in `main`).
- **Deleted by the first cleanup run:** `claude/zen-thompson-5fdqqz`, `claude/laughing-meitner-ywjnk1` and `claude/blissful-volta-coypr6`.

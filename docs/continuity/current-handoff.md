# Current handoff — App Manager 8 (26 October 2026; PR34 merged; OD-49; M04 next)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 8** (OD-46), in `Glow App - No Stream`, with the manager branch `claude/magical-wozniak-yfmmx2` as its outcome branch.
- **M05, the whole-project review** ([brief](../planning/m05-whole-project-review.md); [record](../testing/evidence/2026-10-25-m05-project-review.md)): its records and DM-31's texts merged as PR34 (`4aa66e2`). **Nathan resumed the plan** (OD-49: N5 (b), N1 (a)), applied as PF01 1.14. M05 closes with his second and third decision messages: N4 and N2 (with C30 to C35 for information), then S2, S5 and D1.
- **Next item: M04** with the CI hardening (OD-39; M05 findings 10, 11 and 14). Its brief goes to the Dev Manager as DM-32, with OD-49's row and PF01 1.14 for their pre-merge read.
- **The order after M04** (OD-49): M06, P09.3a, P06.2-F, P06.3, the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them.
- **Done:** P00 to P05 (fixture scope), M01 to M03, P06.1, P06.DB and P06.2.
- **Dev Manager 3:** `session_01KVuPEpFRh9B22beZKTKb27` (OD-47); review log DM-01 to DM-31, with "Deferred conditions".
- **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (26 October 2026, App Manager 8)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 8 | Nathan (a decision) | N4 and N2, the second decision message | M04's brief and DM-32 proceed; P-3 and P-6 wait |

## Next actions (App Manager 8)

1. **The decisions:** on N4 and N2, record them and apply P-6 and P-3; then the third message (S2, S5, D1, and DM-29 2.3's optional direction).
2. **M04's brief**, then DM-32, the Dev Manager's read, with the governing changes since PR34. Starting points: push to `main` and manual dispatch only, never a pull-request event; `contents: write` for that job only, no secrets, pinned actions; delete only a branch whose head is in `main`, off a keep-list held on `main` (`main`, the manager branch, and `claude/dev-manager` by name, DM-13 item 10) and heading no open PR; dry-run mode and a job summary; selection tests and a run of record; the CI policy updated, classified with the pre-change policy, the whole workflow diff read; exact-head review, Codex and the Dev Manager's read. Also weigh adding the session harness's branch pattern to the push filter (AM7-02; the brief's B2-C2 point vi). M05 adds `!cancelled()` on the application jobs (finding 10), the Mobile job's margin (11) and the upload-artifact pin (14).
3. **Then** M06, P09.3a, P06.2-F, P06.3 and the slices, each named to Nathan before it starts (OD-49). The harness's carried fixes (the P11 plan) land before P11's live run.

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions". The prompts' pruning is M05 finding 44, a manager batch with OD-45's D8 link pinned first.

## Branches and PRs (`git ls-remote`, 26 October 2026, at PR34's merge)

- **Open PRs:** none. PR34 merged at `4aa66e2` on 26 October; the manager branch's next records open a new PR.
- **Kept:** `main` (`4aa66e2`), the manager branch, and `claude/dev-manager` (`8d51446`, in `main`).
- **For Nathan to delete, fully merged:** `claude/zen-thompson-5fdqqz` (M05, `e27f7c7`).

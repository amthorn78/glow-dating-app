# Current handoff — App Manager 9 (8 November 2026; P06.2-F, correction C4)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 9** (OD-56), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; PR40 stays; on the cleanup's keep-list), subscribed to PR40.
- **M04 to M06 are done** ([M06's record](../testing/evidence/2026-11-01-m06-sdk-58-upgrade.md), "M06's merge receipt"): Expo SDK 58.0.22; advisories accepted (OD-54); `noxcturnal` unloaded (DM-36). Merges into `main` delete fully merged branches; branch controls: none (OD-52).
- **P09.3a is done** ([brief](../planning/p09-3a-requirements-matrix.md); [matrix](../planning/store-legal-safety-requirements.md)): 320 rows, routed by [DM-37](dev-manager/reviews/2026-11-01-dm-37-p09-3a-gaps-and-a05.md) into the [carried-items file](../planning/carried-to-later-items.md); PF01 1.17's release gate. **OD-55:** a US legal entity; the US, all states, in English, for now; a self-entered birth date plus the stores' age signals, behind SV1's seam.
- **Now: P06.2-F**, the mobile hardening ([brief](../planning/p06-2-f-mobile-hardening.md); [record](../testing/evidence/2026-11-01-p06-2-f-mobile-hardening.md)), in PR40. Corrections C1 (`0881db5`), C2 (`816cd60`; DM-38) and C3 (`f87e8b1`; DM-39) are verified. C3's delta re-review asked for changes; **[DM-40](dev-manager/reviews/2026-11-08-dm-40-p06-2-f-c3-review-and-od-57.md)** approved narrowing the listed items to its section 4.2's words, approved OD-57's governing texts and confirmed DM-39 4.2. **Next: correction C4** ([prompt](../ephemeral/2026-11-08-p06-2-f-c4-correction-prompt.md); the brief, revision 4), then its bounded delta re-review (DM-40 3.1 to 3.4).
- **The repository is public for now** (OD-51); before it goes private, Nathan tells the manager (`'ccr-**'`, M07).
- **The order** (OD-49): P06.2-F, P06.3, the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2 and P09.3a.
- **Dev Manager 3:** `session_01KVuPEpFRh9B22beZKTKb27` (OD-47); review log DM-01 to DM-40, with "Deferred conditions".
- **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (8 November 2026, 07:52 UTC, App Manager 9)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 9 | GitHub (an external party): Codex on PR40's head, which holds C4's prompt | Codex complete, any finding handled before the prompt goes to Nathan (step 6) | Running with no result after 60 minutes: `@codex review` once (OD-53) |
| App Manager 9 | Nathan (a session running), once the prompt is given | C4's report, relayed | Nothing to chase; on the report, verify it first (OD-29) |

## Next actions (App Manager 9)

1. **P06.2-F:** give Nathan C4's prompt once Codex is clear; verify C4; its delta re-review, bounded to the changed items (DM-40 3.1 to 3.4; a form inside the narrowed words goes to the Dev Manager before any C5); then the pre-merge checklist, the merge and its receipt.
2. **Then** P06.3 and the slices, each named to Nathan before it starts (OD-49); the second A05 message before SV2's brief (the carried-items file).

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions". The prompts' pruning is M05 finding 44, a manager batch with OD-45's D8 link pinned first.

## Branches and PRs (`git ls-remote`, 8 November 2026, 07:52 UTC)

- **Open: PR40** (P06.2-F), from the manager branch. PR39 (P09.3a's records) merged at `bac3c19`.
- **Kept, by the cleanup's keep-list:** `main` (`bac3c19`), the manager branch, and `claude/dev-manager` (`497ba97`, merged into the manager branch).
- **Unmerged:** `claude/practical-wozniak-fg1e2i` (`02f1972`), `claude/trusting-cori-gxlila` (`0e98f25`), `claude/inspiring-ramanujan-tjpril` (`3c0acfe`) and `ccr-7506019b-5rfdfn` (`14e37a6`), P06.2-F's implementation and C1 to C3, all in PR40; the cleanup deletes them at the merge.

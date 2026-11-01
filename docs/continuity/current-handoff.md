# Current handoff — App Manager 8 (1 November 2026; M06 done; P09.3a next)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 8** (OD-46), in `Glow App - No Stream`, with the manager branch `claude/magical-wozniak-yfmmx2` as its outcome branch.
- **M06 is done** ([brief](../planning/m06-dependency-remediation.md); [record](../testing/evidence/2026-11-01-m06-sdk-58-upgrade.md), "M06's merge receipt"): PR38 merged at `fcd6ebc`, Expo SDK 58.0.22. Advisories left: `glob` and `minimatch` (moderate, tooling), accepted by Nathan (OD-54) and re-checked at each dependency change and before P09. `noxcturnal` stays unloaded: `apps/mobile/AGENTS.md`, "Dependency changes" 5 (DM-36).
- **M05 and M04 are done:** PR34 (`4aa66e2`) and PR36 (`4794d3e`); since M04, every merge into `main` deletes the fully merged branches (the CI policy, "Branch cleanup"). Branch controls: none, procedure only (OD-52).
- **Now: P09.3a**, the store, legal and safety requirements matrix ([brief](../planning/p09-3a-requirements-matrix.md); [prompt](../ephemeral/2026-11-01-p09-3a-matrix-prompt.md), revision 1, for `Glow App - No Stream`). Research only, for the US, the UK and the EU (OD-50); not legal advice.
- **The repository is public for now** (OD-51), for budget reasons; Nathan intends to make it private again. When he does, `'ccr-**'` comes out or its minutes are approved, and the costed list (M07) carries GitHub Actions; he tells the manager first.
- **The order** (OD-49): P09.3a, P06.2-F, P06.3, the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB and P06.2.
- **Dev Manager 3:** `session_01KVuPEpFRh9B22beZKTKb27` (OD-47); review log DM-01 to DM-36, with "Deferred conditions".
- **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (1 November 2026, App Manager 8)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 8 | Nathan (the P09.3a session) | The session's report | The manager asks Nathan whether the session ran; if the environment refused the sources, the CLI agent (OD-43) |

## Next actions (App Manager 8)

1. **P09.3a:** verify the matrix by the brief's review plan; route its gaps; the A05 questions to the Dev Manager, then to Nathan in OD-32's form, before P07's brief.
2. **Then** P06.2-F, P06.3 and the slices, each named to Nathan before it starts (OD-49).

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions". The prompts' pruning is M05 finding 44, a manager batch with OD-45's D8 link pinned first.

## Branches and PRs (`git ls-remote`, 1 November 2026, 18:20 UTC)

- **No open PR.** PR38 merged at `fcd6ebc`.
- **Kept, by the cleanup's keep-list:** `main` (`fcd6ebc`), the manager branch (on `6eaee35`, with the receipt and P09.3a's brief and prompt after it), and `claude/dev-manager` (`981d3ce`, in `main`).
- **The cleanup run** 41336047901 deleted `claude/gallant-einstein-rjyjdl` and `claude/magical-lovelace-s0akbt`.

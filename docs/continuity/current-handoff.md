# Current handoff — App Manager 8 (1 November 2026; P09.3a done; P06.2-F next)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 8** (OD-46), in `Glow App - No Stream`, with the manager branch `claude/magical-wozniak-yfmmx2` as its outcome branch.
- **M06 is done** ([brief](../planning/m06-dependency-remediation.md); [record](../testing/evidence/2026-11-01-m06-sdk-58-upgrade.md), "M06's merge receipt"): PR38 merged at `fcd6ebc`, Expo SDK 58.0.22. Advisories left: `glob` and `minimatch` (moderate, tooling), accepted by Nathan (OD-54) and re-checked at each dependency change and before P09. `noxcturnal` stays unloaded: `apps/mobile/AGENTS.md`, "Dependency changes" 5 (DM-36).
- **M05 and M04 are done:** PR34 (`4aa66e2`) and PR36 (`4794d3e`); since M04, every merge into `main` deletes the fully merged branches (the CI policy, "Branch cleanup"). Branch controls: none, procedure only (OD-52).
- **P09.3a is done** ([brief](../planning/p09-3a-requirements-matrix.md); [matrix](../planning/store-legal-safety-requirements.md)): 320 rows, routed by [DM-37](dev-manager/reviews/2026-11-01-dm-37-p09-3a-gaps-and-a05.md) into the [carried-items file](../planning/carried-to-later-items.md); PF01 1.17's release gate. Research, not legal advice. **OD-55:** a US legal entity; the US, all states, in English, for now; a self-entered birth date plus the stores' age signals, behind SV1's seam.
- **Now: P06.2-F**, the mobile hardening ([brief](../planning/p06-2-f-mobile-hardening.md); [prompt](../ephemeral/2026-11-01-p06-2-f-implementation-prompt.md), revision 1, for `Glow App - No Stream`): seven fixture-only items, each with a test and its reversal.
- **The repository is public for now** (OD-51), for budget reasons; Nathan intends to make it private again. When he does, `'ccr-**'` comes out or its minutes are approved, and the costed list (M07) carries GitHub Actions; he tells the manager first.
- **The order** (OD-49): P06.2-F, P06.3, the server slices SV1 to SV4, then P07 to P12; P06.2-T and P07.2a where the Work Register places them, and M07, the costed list (OD-50), before P09 and P11B.
- **Done:** P00 to P05 (fixture scope), M01 to M06, P06.1, P06.DB, P06.2 and P09.3a.
- **Dev Manager 3:** `session_01KVuPEpFRh9B22beZKTKb27` (OD-47); review log DM-01 to DM-37, with "Deferred conditions".
- **Linear (OD-29).** Every prompt names its environment (OD-36, OD-40, OD-43).

## Waiting checkpoint (1 November 2026, App Manager 8)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 8 | Nathan (the P06.2-F session) | The session's report | The manager asks Nathan whether the session ran |

## Next actions (App Manager 8)

1. **P06.2-F:** verify the report; the PR; Codex on its head; the exact-head code review prompt; the merge and its receipt.
2. **Then** P06.3 and the slices, each named to Nathan before it starts (OD-49); the second A05 message (the preference taxonomy, resurfacing and rematch, the history policy) before SV2's brief.

**Carried follow-ups** live in their owning homes: the P06.2 brief's "Carried to later changes", the M02 brief, the P11 plan, [`carried-to-later-items.md`](../planning/carried-to-later-items.md) and the review log's "Deferred conditions". The prompts' pruning is M05 finding 44, a manager batch with OD-45's D8 link pinned first.

## Branches and PRs (`git ls-remote`, 1 November 2026, 21:03 UTC)

- **No open PR.** PR39 (P09.3a's records) merged at `bac3c19`; PR38 (M06) at `fcd6ebc`.
- **Kept, by the cleanup's keep-list:** `main` (`bac3c19`), the manager branch (`05f4c3a`, with this receipt after it), and `claude/dev-manager` (`0db8c42`, in `main`).
- **The cleanup run** 41349863365 deleted `claude/stoic-pasteur-r24pz8`.

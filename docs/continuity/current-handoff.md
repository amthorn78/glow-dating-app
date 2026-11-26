# Current handoff — App Manager 13 (26 November 2026; DM-100 answered; PR59 to merge)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads [GAPP-PF02](../pf-canon/GAPP-PF02-Manager-Practice-Rules.md) before the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 13** (OD-83), in `Glow App - No Stream`, on `claude/magical-wozniak-yfmmx2` (on the keep-list).
- **Dev Manager 7** (`session_01Q789u3mBCcA1Fu21CMJKbS`; OD-84; start note `532e9d0`) holds `claude/dev-manager`; Nathan carries each consultation (OD-25). DM-100 answered (`0256d2c`); new condition labels start at AM.
- **Never ask Nathan to perform a GitHub operation** (OD-58); a failure that seems to need a re-run goes to the Dev Manager first (OD-32). Sessions read GitHub with the GitHub tools where they have them, otherwise `gh api` REST, read only: most sessions since 22 November have had no GitHub tools (C2's delta review's session had them).
- **`main`** is at `43e794a` (PR58, SV4 A1); before it `499ccbb` (PR57, SV4 A0). D-07: the Dev Manager reads a code item at its brief and before its merge; D-06: one Markdown-only item may run beside a code item.
- **Standing context:** OD-77 (no cost now; legal entity deferred), OD-78 (the whole system working together first), OD-79 (the app's database on HDE's PostgreSQL service; Railway components to analyze and retire), OD-80 (no HDE design decision now), OD-81 (`glow-frontend-v2` deprecated); the repository public for now (OD-51).
- **The order** (PF01 1.20): stage 1, the pre-integration build: SV4 (two stages), SV5, SV2-L, AC1 to AC3, then P07.2, P07.3, P08.1, P08.2, P09.1; stage 2, integration, which Nathan starts; stage 3, business set-up and release. The Railway analysis (once authorized) and M09-R may run beside a code item (D-06).
- **Done:** P00 to P05 (fixture scope), M01 to M09, A01-R, P06.1, P06.DB, P06.2, P09.3a, P06.2-F, P06.3, SV1 to SV3, SV2-R.
- **Owner directions:** OD-01 to OD-84. **Review log:** DM-01 to DM-100. **Linear (OD-29).** Every prompt names its environment (OD-36) and glow-docs as attached (OD-74).

## Waiting checkpoint (26 November 2026, App Manager 13)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 13 | PR59's run and Codex on this batch's head | DM-100's merge conditions | Nothing merges; a failure goes to the Dev Manager (OD-32) |

## Next actions (App Manager 13)

1. **SV4 A1 merged** with PR58 at `43e794a` (DM-98). **Now: SV4 A2** (D8 to D10, D15) in PR59: code head `26aa7ca`, merged at `0ff9c09`; its exact-head review asked for changes (A2R-1 to A2R-4); DM-99 chose the route-layer fix; the brief is at revision 10. A2-C1 (code head `ddb1386`, run of record 45778164243) verified and merged at `356ee8f`. Its delta review asked for words only (F1; AM13-08). DM-100 (`0256d2c`) carried F1 and approved the merge, with AL1 to AL8, applied as given. Next: the run and Codex on this head, the three threads resolved, the checklist filled, `ddb1386`'s non-Markdown paths equal to the head's; then the merge, its receipt (the P11 plan's line 105; the procedure summary's stamp), the branch cleanup and Stage B. The carried items: "Carried to SV4" (DM-98's AJ2 rule for any writer of either version field), "Carried to the next change to the Foundation workflow (DM-97)".
2. **Manager records:** PF02 1.9 (AM12-31 to AM12-49, AM13-01 to AM13-11; AM12-49's proposed rule: a prompt names both GitHub routes; DM-98's wording of the false-claim class); the manager workflow's next revision: DM-100's AL9 (the delta review's line count), for the Dev Manager's read; the status log's move (M09 (b)); R-07, R-10, R-26, R-28.

**Carried follow-ups** live in their owning homes: [`carried-to-later-items.md`](../planning/carried-to-later-items.md), the P11 plan, the review log's "Deferred conditions".

## Branches and PRs (26 November 2026)

- **Open PRs:** PR59 (SV4 A2), from the manager branch into `main`.
- **Remote branches, five** (26 November): `main` (`43e794a`); the manager branch; `claude/dev-manager` (`0256d2c`, merged); A2's `claude/dazzling-hamilton-ocxuu3` (`88d4ef3`, merged at `0ff9c09`) and A2-C1's `claude/affectionate-sagan-r916ba` (`2201c2d`, merged at `356ee8f`), which the branch cleanup deletes once A2's PR merges.

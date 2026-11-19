# Current handoff — App Manager 12 (19 November 2026; PR55 merged; M07 done; the first approvals with Nathan)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads [GAPP-PF02](../pf-canon/GAPP-PF02-Manager-Practice-Rules.md), the standing practice rules, before the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 12** ([OD-67](owner-directions.md)), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; on the cleanup's keep-list).
- **Dev Manager 5** (`session_01Q789u3CWg6s9pBGXerCQZt`; OD-65) holds `claude/dev-manager`. Nathan carries each consultation to it (OD-25). Its read of governing Markdown stays (OD-76).
- **Never ask Nathan to perform a GitHub operation** (OD-58). A failure that seems to need a re-run goes to the Dev Manager first (OD-32).
- **PR55 merged** at `d3273f3`: M09's record, PF01 1.19, PF02 1.8, and the D-06 and D-07 texts, now in force (DM-94). Under D-07 the Dev Manager reads a code item at its brief and before its merge; under D-06 one Markdown-only item may run beside a code item.
- **M07 is done** ([its record](../testing/evidence/2026-11-19-m07-costed-list.md)). **OD-77:** no cost now; the legal entity and what needs it deferred; Railway and WordPress hosting available; Stream's Maker account assumed. **OD-78:** the MVP prototype, the priority, is the whole system working together (app, server, database and HDE, integrated); business set-up waits for it. **OD-79:** the app's database on HDE's existing PostgreSQL service (OD-18); the existing Railway components analyzed and retired; HDE still under development.
- **A01-R is done** ([its record](../testing/evidence/2026-11-19-a01-r-hde-canon-read.md)): HDE's pair read is deployed, but HDE has no permitted way to create a real member's chart, no credential for the app and no test environment. **OD-80:** no design decision about HDE now; a later integration process handles it; the app does as much pre-integration work as possible.
- **The repository is public for now** (OD-51); before it goes private, an Actions line is approved (M07, Line 16).
- **The order** (PF01 1.19): A01-R next; SV4 (two stages), SV5, SV2-L, AC1 to AC3, then P07 to P12. M09-R, the record corrections, may run beside a code item (D-06).
- **Done:** P00 to P05 (fixture scope), M01 to M09, P06.1, P06.DB, P06.2, P09.3a, P06.2-F, P06.3, SV1 to SV3 and SV2-R.
- **Owner directions:** OD-01 to OD-80. **Review log:** DM-01 to DM-94. **Linear (OD-29).** Every prompt names its environment (OD-36) and glow-docs as attached (OD-74).

## Waiting checkpoint (19 November 2026, 02:21 UTC, App Manager 12)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| Nathan | App Manager 12 | PF01 1.20, the pre-integration plan, and DM-95 to carry | — |

## Next actions (App Manager 12)

1. **PF01 1.20, the pre-integration plan (OD-78 to OD-80):** every app-side item before integration (SV4 Stage A, SV5, AC1 to AC3, the birth-time refusal, the remaining server parts), then a later integration process that Nathan starts (the database on the existing service, the deployed server, HDE); the Railway analysis item; for the Dev Manager's read (DM-95). Then SV4's brief.
2. **Manager records:** PF02 1.9 (AM12-31, AM12-32); the status log's move (M09 (b)); R-07, R-10, R-26, R-28.

**Carried follow-ups** live in their owning homes: [`carried-to-later-items.md`](../planning/carried-to-later-items.md) (with "Routed by M09" and "Routed by A01-R"), the P11 plan, the review log's "Deferred conditions".

## Branches and PRs (19 November 2026, 01:34 UTC; listed with the GitHub tools before this time)

- **Open PRs:** none. `main` is at `d3273f3` (PR55).
- **Remote branches, four:** `main`; the manager branch; `claude/dev-manager` (`221da6d`, merged at `f9595b4`); M07's `claude/sharp-keller-j1uvsv` (`02b7a1f`, merged into the manager branch at `817ce5e`).

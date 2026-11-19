# Current handoff — App Manager 12 (19 November 2026; PF01 1.20 approved in DM-95; its pull request into `main`)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads [GAPP-PF02](../pf-canon/GAPP-PF02-Manager-Practice-Rules.md), the standing practice rules, before the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 12** ([OD-67](owner-directions.md)), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; on the cleanup's keep-list).
- **Dev Manager 5** (`session_01Q789u3CWg6s9pBGXerCQZt`; OD-65) holds `claude/dev-manager`. Nathan carries each consultation to it (OD-25). Its read of governing Markdown stays (OD-76).
- **Never ask Nathan to perform a GitHub operation** (OD-58). A failure that seems to need a re-run goes to the Dev Manager first (OD-32).
- **PR55 merged** at `d3273f3`: M09's record, PF01 1.19, PF02 1.8, and the D-06 and D-07 texts, now in force (DM-94). Under D-07 the Dev Manager reads a code item at its brief and before its merge; under D-06 one Markdown-only item may run beside a code item.
- **M07 is done** ([its record](../testing/evidence/2026-11-19-m07-costed-list.md)). **OD-77:** no cost now; the legal entity and what needs it deferred; Railway and WordPress hosting available; Stream's Maker account assumed. **OD-78:** the MVP prototype, the priority, is the whole system working together (app, server, database and HDE, integrated); business set-up waits for it. **OD-79:** the app's database on HDE's existing PostgreSQL service (OD-18); the existing Railway components analyzed and retired; HDE still under development.
- **A01-R is done** ([its record](../testing/evidence/2026-11-19-a01-r-hde-canon-read.md)): HDE's pair read is deployed, but HDE has no permitted way to create a real member's chart, no credential for the app and no test environment. **OD-80:** no design decision about HDE now; a later integration process handles it; the app does as much pre-integration work as possible.
- **OD-81:** `glow-frontend-v2` is deprecated (Dev Manager 5's note); the Railway analysis does not cover it, and its retirement and the domain `glowme.io` are not decided.
- **The repository is public for now** (OD-51); before it goes private, an Actions line is approved (M07, Line 16).
- **The order** (PF01 1.20, approved in DM-95; merging): stage 1, the pre-integration build, now: SV4 (two stages), SV5, SV2-L, AC1 to AC3, then P07.2, P07.3, P08.1, P08.2 and P09.1; stage 2, integration, a later process Nathan starts; stage 3, business set-up and release. The Railway analysis, once Nathan authorizes its read, and M09-R may each run beside a code item (D-06).
- **Done:** P00 to P05 (fixture scope), M01 to M09, A01-R, P06.1, P06.DB, P06.2, P09.3a, P06.2-F, P06.3, SV1 to SV3 and SV2-R.
- **Owner directions:** OD-01 to OD-81. **Review log:** DM-01 to DM-95. **Linear (OD-29).** Every prompt names its environment (OD-36) and glow-docs as attached (OD-74).

## Waiting checkpoint (19 November 2026, 02:58 UTC, App Manager 12)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 12 | GitHub | The manager branch's pull request into `main` (PF01 1.20, OD-81, the DM-95 batch): its docs-only gate line and any Codex comment | A scheduled wake-up reads it with the GitHub tools; no merge without the gate line |

## Next actions (App Manager 12)

1. **PF01 1.20's pull request:** merge once the gate line shows, PF01 at its final head equals `83e88b8`'s with AE1 to AE5, and the review log's disposition covers that head. Then the receipt (prune A01-R's prompt and DM-95's consultation), and Notion's plan rows follow the merged text.
2. **SV4 Stage A's brief,** for the Dev Manager's first read under D-07.
3. **Manager records:** PF02 1.9 (AM12-31 to AM12-35); the status log's move (M09 (b)); R-07, R-10, R-26, R-28.

**Carried follow-ups** live in their owning homes: [`carried-to-later-items.md`](../planning/carried-to-later-items.md) (with "Routed by M09" and "Routed by A01-R"), the P11 plan, the review log's "Deferred conditions".

## Branches and PRs (19 November 2026, 02:58 UTC; listed with `git ls-remote` at this time)

- **Open PRs:** the manager branch into `main`, opened after this batch. `main` is at `d3273f3` (PR55).
- **Remote branches, five:** `main`; the manager branch; `claude/dev-manager` (`6a3811b`, merged at `19a086d`); M07's `claude/sharp-keller-j1uvsv` (`02b7a1f`, merged at `817ce5e`); A01-R's `claude/fervent-sagan-afkke2` (`835d393`, merged at `44b48f4`).

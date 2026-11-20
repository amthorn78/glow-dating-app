# Current handoff — App Manager 12 (20 November 2026; SV4 A1 built, verified and in PR58; its exact-head review next)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads [GAPP-PF02](../pf-canon/GAPP-PF02-Manager-Practice-Rules.md), the standing practice rules, before the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 12** ([OD-67](owner-directions.md)), in `Glow App - No Stream`, on the manager branch `claude/magical-wozniak-yfmmx2` (its outcome branch; on the cleanup's keep-list).
- **Dev Manager 6** (`session_01Q789u2AYaBgUF8gPDLeJmV`; OD-82, from Dev Manager 5's handover) holds `claude/dev-manager`. Nathan carries each consultation to it (OD-25). Its read of governing Markdown stays (OD-76).
- **Never ask Nathan to perform a GitHub operation** (OD-58). A failure that seems to need a re-run goes to the Dev Manager first (OD-32).
- **PR57 merged** at `499ccbb`: SV4 A0 (the database job split by suite, the Chromium retry, the pin test), its corrections C1 and C2, and DM-97. Before it, PR56 (`c2cffbe`): PF01 1.20, M07's and A01-R's records, OD-77 to OD-81. Under D-07 the Dev Manager reads a code item at its brief and before its merge; under D-06 one Markdown-only item may run beside a code item.
- **M07 is done** ([its record](../testing/evidence/2026-11-19-m07-costed-list.md)). **OD-77:** no cost now; the legal entity and what needs it deferred; Railway and WordPress hosting available; Stream's Maker account assumed. **OD-78:** the MVP prototype, the priority, is the whole system working together (app, server, database and HDE, integrated); business set-up waits for it. **OD-79:** the app's database on HDE's existing PostgreSQL service (OD-18); the existing Railway components analyzed and retired; HDE still under development.
- **A01-R is done** ([its record](../testing/evidence/2026-11-19-a01-r-hde-canon-read.md)): HDE's pair read is deployed, but HDE has no permitted way to create a real member's chart, no credential for the app and no test environment. **OD-80:** no design decision about HDE now; a later integration process handles it; the app does as much pre-integration work as possible.
- **OD-81:** `glow-frontend-v2` is deprecated (Dev Manager 5's note); the Railway analysis does not cover it, and its retirement and the domain `glowme.io` are not decided.
- **The repository is public for now** (OD-51); before it goes private, an Actions line is approved (M07, Line 16).
- **The order** (PF01 1.20, in force since PR56): stage 1, the pre-integration build, now: SV4 (two stages), SV5, SV2-L, AC1 to AC3, then P07.2, P07.3, P08.1, P08.2 and P09.1; stage 2, integration, a later process Nathan starts; stage 3, business set-up and release. The Railway analysis, once Nathan authorizes its read, and M09-R may each run beside a code item (D-06).
- **Done:** P00 to P05 (fixture scope), M01 to M09, A01-R, P06.1, P06.DB, P06.2, P09.3a, P06.2-F, P06.3, SV1 to SV3 and SV2-R.
- **Owner directions:** OD-01 to OD-82. **Review log:** DM-01 to DM-97. **Linear (OD-29).** Every prompt names its environment (OD-36) and glow-docs as attached (OD-74).

## Waiting checkpoint (20 November 2026, 06:03 UTC, App Manager 12)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 12 | GitHub Actions and Codex, then Nathan | PR58's run and Codex on its head; then A1's exact-head review ([its prompt](../ephemeral/2026-11-20-sv4-a1-review-prompt.md)) | Nothing merges |

## Next actions (App Manager 12)

1. **SV4 A1** (the rules; built at `bc0675d`, run 44679608400 passed; verified and integrated at `a1651fb`; PR58): Codex on PR58's head, then the exact-head review (the prompt goes to Nathan once Codex has finished), the Dev Manager's pre-merge read and the merge; then A2's prompt.
2. **Manager records:** PF02 1.9 (AM12-31 to AM12-47); the status log's move (M09 (b)); R-07, R-10, R-26, R-28.

**Carried follow-ups** live in their owning homes: [`carried-to-later-items.md`](../planning/carried-to-later-items.md) (with "Routed by M09" and "Routed by A01-R"), the P11 plan, the review log's "Deferred conditions".

## Branches and PRs (20 November 2026, 06:03 UTC; listed with `git ls-remote` at this time)

- **Open PRs:** PR58, the manager branch into `main` (full scope; SV4 A1). `main` is at `499ccbb` (PR57).
- **Remote branches, four:** `main`; the manager branch; `claude/dev-manager` (`b505a8e`, merged); A1's `claude/sleepy-mendel-0kqgw9` (`a1651fb`, fast-forwarded).

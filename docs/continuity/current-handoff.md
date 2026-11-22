# Current handoff — App Manager 13 (22 November 2026; DM-98 answered; PR58 to merge)

This file only routes: the current item, what happens next and who waits on whom. Each fact lives in one home, listed in the [documentation map](../README.md); earlier handoffs are in `docs/continuity/history/`, the last as [P06.2 to its merge](history/p06-2-handoff.md).

- **Process:** Nathan's manual relay ([manager workflow](../planning/manager-workflow.md)), with the [Dev Manager](../planning/dev-manager.md) as second-layer reviewer (OD-25). Standing directions: the [owner-direction register](owner-directions.md). A new manager starts from the [start procedure](../planning/start-prompts/next-manager.md) and reads [GAPP-PF02](../pf-canon/GAPP-PF02-Manager-Practice-Rules.md) before the [mistakes log](manager-mistakes.md).

## Now

- **Manager: App Manager 13** (OD-83), in `Glow App - No Stream`, on `claude/magical-wozniak-yfmmx2` (on the keep-list).
- **Dev Manager 7** (`session_01Q789u3mBCcA1Fu21CMJKbS`; OD-84; start note `532e9d0`) holds `claude/dev-manager`; Nathan carries each consultation (OD-25). A1's pre-merge read (DM-98) goes to it; new condition labels start at AJ.
- **Never ask Nathan to perform a GitHub operation** (OD-58); a failure that seems to need a re-run goes to the Dev Manager first (OD-32). Sessions read GitHub with the GitHub tools where they have them, otherwise `gh api` REST, read only: most sessions since 22 November have had no GitHub tools (C2's delta review's session had them).
- **`main`** is at `499ccbb` (PR57, SV4 A0). D-07: the Dev Manager reads a code item at its brief and before its merge; D-06: one Markdown-only item may run beside a code item.
- **Standing context:** OD-77 (no cost now; legal entity deferred), OD-78 (the whole system working together first), OD-79 (the app's database on HDE's PostgreSQL service; Railway components to analyze and retire), OD-80 (no HDE design decision now), OD-81 (`glow-frontend-v2` deprecated); the repository public for now (OD-51).
- **The order** (PF01 1.20): stage 1, the pre-integration build: SV4 (two stages), SV5, SV2-L, AC1 to AC3, then P07.2, P07.3, P08.1, P08.2, P09.1; stage 2, integration, which Nathan starts; stage 3, business set-up and release. The Railway analysis (once authorized) and M09-R may run beside a code item (D-06).
- **Done:** P00 to P05 (fixture scope), M01 to M09, A01-R, P06.1, P06.DB, P06.2, P09.3a, P06.2-F, P06.3, SV1 to SV3, SV2-R.
- **Owner directions:** OD-01 to OD-84. **Review log:** DM-01 to DM-98. **Linear (OD-29).** Every prompt names its environment (OD-36) and glow-docs as attached (OD-74).

## Waiting checkpoint (22 November 2026, 10:30 UTC, App Manager 13)

| Who waits | On whom | For what | If nothing arrives |
|---|---|---|---|
| App Manager 13 | GitHub | PR58's run and Codex on the head that records DM-98; then the P1 thread resolved, the checklist filled, the merge | Nothing merges |

## Next actions (App Manager 13)

1. **SV4 A1** (PR58; the SV4 record): A1-C1 fixed AR-1 to AR-3 (code head `f69529c`, merged at `9947844`). Its delta review asked for one more docstring fix, D1-1 (with N1, N2); A1-C2 (the brief's revision 7) is done and verified (code head `934da48`, run 45006396587; merged at `860abe2`). C2's delta review (from `045014d`; PR58's run and Codex clean) found E-1 (the detector reads only the later of two `def`s with one name), which the rule does not decide; it goes to Dev Manager 7 with A1's pre-merge read, DM-98 (recommended: carry). DM-98 (Dev Manager 7, `8c587ac`) carried E-1 with AJ1 to AJ3 and approved A1 with AJ4; AJ1 to AJ5 applied. Next: PR58's run and Codex on this batch's head, the P1 thread resolved, the checklist, the merge and its receipt; then A2's prompt.
2. **Manager records:** PF02 1.9 (AM12-31 to AM12-49, AM13-01 to AM13-03; AM12-49's proposed rule: a prompt names both GitHub routes; DM-98's wording of the false-claim class); the status log's move (M09 (b)); R-07, R-10, R-26, R-28.

**Carried follow-ups** live in their owning homes: [`carried-to-later-items.md`](../planning/carried-to-later-items.md), the P11 plan, the review log's "Deferred conditions".

## Branches and PRs (22 November 2026, 10:30 UTC)

- **Open PRs:** PR58, the manager branch into `main` (full scope; SV4 A1).
- **Remote branches, six:** `main`; the manager branch; `claude/dev-manager` (`8c587ac`, merged at `75784af`); A1's `claude/sleepy-mendel-0kqgw9` (`a1651fb`) and A1-C1's `claude/beautiful-brahmagupta-13ncpo` (`7b194aa`) and A1-C2's `claude/affectionate-pasteur-ge2jra` (`02ebfc7`), all in the manager branch, which the branch cleanup deletes once PR58 merges.

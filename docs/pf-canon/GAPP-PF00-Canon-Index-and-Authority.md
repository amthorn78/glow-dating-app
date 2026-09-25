# Glow Dating App — Canon Index and Authority

**Identity:** GAPP-PF00 · **Revision:** 1.9 · **Recorded:** 25 September 2026
**Scope:** the separate Glow dating application. This index does not govern or modify the Glow HD engine's PF canon.

## Start here

1. Read [current handoff](../continuity/current-handoff.md), verify remote main/open PRs/worktree, and read applicable repository agent instructions.
2. Read [PF01](GAPP-PF01-A-to-Z-Implementation-Plan.md), the relevant persistent plan and code. [The documentation guide](../README.md) maps every durable home.
3. Reconcile task status with [Implementation Control](https://app.notion.com/p/3e44590a05eb8118bf02f0dc0c3ea57c) and the [Work Register](https://app.notion.com/p/71b769915b5b4e00830663770bc95f7e). A fresh session can understand and implement its assignment from repository Markdown alone; unavailable Notion access requires a later status sync, not a Drive dependency.

## Current session authority

Nathan's standing directions, including which feature work is paused or resumed, are in the [owner-direction register](../continuity/owner-directions.md). Current status is in the [current handoff](../continuity/current-handoff.md); this index does not restate it (DM-01 P3). Claude work runs as Nathan's manual relay. A manager session writes briefs and prompts. Nathan starts each implementation or review session himself and relays its report back. The manager reviews that evidence and maintains continuity. Nathan reinitiates managers manually. The manager never starts implementation or review work itself; those sessions may use whatever tools they need. The one exception is the Dev Manager (PF01 D10, 25 September 2026), a second-layer review session that the manager creates and relays to itself. App Planner 1 prepared the migration, and App Builder 1's earlier reports remain historical evidence; both are historical roles. [Manager workflow](../planning/manager-workflow.md) implements the owner's high-trust experiment without importing prompt libraries. PF01 D08's app-only authority and effect-based HDE protection remain; D09 records the documentation/environment transition.

## Canon registry

| ID | Stable title | Current authoritative home | State |
|---|---|---|---|
| GAPP-PF00 | Canon Index and Authority | This document in `amthorn78/glow-dating-app`, `docs/pf-canon/` | Established |
| GAPP-PF01 | A-to-Z Implementation Plan | [Governing plan](GAPP-PF01-A-to-Z-Implementation-Plan.md) | Established; live execution status in Notion |

The plan owns the initial governing direction, phase acceptance, architectural boundaries, decisions, assumptions, autonomy and documentation-transfer procedure. This index routes to that authority without restating its rules. Additional GAPP-PF documents are created only when a specific concept requires its own canonical home; no empty numbered canon is being generated in advance.

## Authority map

| Information | Owner |
|---|---|
| Current task, blocker, next action and execution status | Notion coordination plus repository current handoff; durable scope/evidence in Markdown |
| Nathan's standing directions, with dates and quotes | [Owner-direction register](../continuity/owner-directions.md); Notion carries a copy |
| Operational guidance: the relay, review paths, one item at a time, records | Repository Markdown: `AGENTS.md`, `CLAUDE.md`, the manager workflow, the Dev Manager charter and the CI policy. Notion's Implementation Control carries a matching copy (OD-26); where they differ, the repository wins and Notion is corrected (OD-27) |
| Governing implementation sequence and project-level constraints | Current GAPP-PF01 |
| Implementation contracts, code, runtime configuration definitions, tests and runbooks | Application repository after recorded establishment |
| Durable architectural rationale | Repository ADRs once established; initial decisions remain in GAPP-PF01 until transferred |
| HDE behavior and contracts | HDE's own canonical sources and supported release; referenced, never rewritten by app documentation |
| Original brief and dated research | [Repository source snapshots](../planning/sources/2026-09-23-original-research.md) |
| Temporary drafts, experiments and generated intermediates | [`docs/ephemeral/`](../ephemeral/README.md) or ignored local working directory; noncanonical |

## Repository authority transfer

**Repository selected and created:** `amthorn78/glow-dating-app`, private, default branch `main`, 23 September 2026. This publication initiates P01.2 authority transfer. Exact commit and pointer-verification evidence are recorded in [authority transfer](../continuity/authority-transfer.md). The transfer is effective after those external pointer updates are verified; no local copy alone transfers authority.

The P01 transfer was completed and verified as recorded in [authority transfer](../continuity/authority-transfer.md). It is not a procedure a new session must repeat. The current canon is repository Markdown. Historical Drive snapshots are provenance only; no further Drive read/write or pointer update is required. See [migration record](../planning/claude-code-migration.md) for the remaining source recovery and current documentation map.

## Evidence and revision record

The initial plan and this index were prepared under the owner's planning-only brief. Notion owns the verified publication/checkpoint status. These documents do not attest that application code, database integration, native builds or production readiness exist.

Use stable titles and document IDs for durable references. Record the concrete source revision/commit in the evidence record. When changing authority, record why, the prior home, new home, date, responsible work item and verification. Never create a second editable authority by copying a document.

**Revision history:** 1.0 — establishes the separate application canon and initial Drive-to-repository transfer boundary. No HDE PF document was changed.

1.1 — routes the named coordinator/builder roles and explicit owner authorization to GAPP-PF01 D08. Repository authority transfer remains unperformed at this handoff checkpoint.


1.2 — P01.2 repository publication in the verified private application repository; authority-transfer evidence and external pointers recorded separately to avoid a self-referential commit hash. Initial plan revision and source links preserved.

1.3 — repository-only Markdown operational authority; Claude manager workflow and feature pause; Drive references become historical provenance.

1.4 — records Nathan's manual-relay operating direction of 24 September 2026 (M02). Nathan starts and relays implementation and review sessions; the manager never spawns them.

1.5 — records that the migration (M01) and the Claude setup (M02) are complete while the feature pause continues (25 September 2026). No authority change.

1.6 — records Nathan's direction of 25 September 2026 resuming P06.1; other feature work stays paused. No authority change.

1.7 — records the Dev Manager (PF01 D10, Nathan, 25 September 2026) and its exception to the rule that the manager starts no sessions. No change to the authority map.

1.8 — status leaves the canon (DM-01 P3). This index points to the owner-direction register and the current handoff instead. The authority map adds the register, and App Planner 1 and App Builder 1 are named as historical roles (DM-03 E4). No change to authority.

1.9 — the authority map records that Notion carries a matching copy of the operational guidance and of the owner-direction register, and that the repository wins on any difference (OD-26, OD-27, 25 September 2026). No other change to authority.

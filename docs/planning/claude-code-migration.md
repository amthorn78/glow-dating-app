# M01 — Repository documentation migration and Claude handoff

Owner: Nathan Amthor. Coordinator: App Planner 1. Direction received 24 September 2026. Scope: app repository documentation/instructions/environment examples and CI/review policy; no feature, database, provider, Railway or HDE change. New feature work is paused. The receiving Claude Code session manages bounded one-off implementers and first optimizes its setup after reviewing the codebase.

## Durable locations

- `docs/ephemeral/`: newly established for disposable Markdown prompts/temporary handoffs, with promotion/pruning rules.
- `docs/planning/`: newly established for persistent plans/briefs, decisions and recovered source evidence.
- `docs/pf-canon/`: existing canonical PF00/PF01 confirmed and amended for D09; Markdown retained.
- `docs/README.md`: documentation map/naming/pruning and behavior classification.
- `docs/continuity/claude-code-handoff.md`: full receiving brief, code map, exact environment inventory, Stream setup and prioritized owner inputs.
- `docs/planning/claude-code-initiation.md`: persistent paste-ready initiation for this transition; `manager-workflow.md` defines bounded coordination.

## Material recovered

| Original surface / material | Repository Markdown home | Disposition |
|---|---|---|
| Drive original implementation brief, previously `.txt` | `docs/planning/sources/2026-09-23-original-brief.md` | Complete historical source; later owner direction supersedes its Drive-first setup |
| Drive dated implementation research | `docs/planning/sources/2026-09-23-original-research.md` | Complete dated source; old versions/prices/dependencies require verification when used |
| Drive AP1-DBA-001 audit plan/prompt | `docs/planning/sources/2026-09-23-database-audit-assignment.md` | Historical scope/provenance; not a new permission to connect |
| Drive last full P05.3 assignment | `docs/planning/sources/2026-09-24-p05-3-assignment.md` | Completed historical assignment; no active prompt-library authority |
| Notion completed database audit summary and catalog/model map | `docs/planning/database-audit-2026-09-23.md`, `database-catalog-2026-09-23.md` | Durable dated findings formerly requiring Notion reads |
| Notion AB1-R012 final feature closure | `docs/continuity/history/AB1-R012.md` | Full P05 closure/review/failure evidence; obsolete P06 next action explicitly superseded |
| Existing current P05.3 handoff | `docs/continuity/history/p05-3-handoff.md` | Historical evidence retained while current handoff routes to Claude |

Earlier completed session prompts remain historical provenance where referenced by old evidence; current phase semantics, decisions, failures and deferred obligations already live in repository architecture/testing/history. They are not fresh-session prerequisites and are not imported as a governing prompt library. The original PF transfer was completed in P01; no parallel Drive canon is maintained. Historical source headers explain supersession. No HDE attachment/canon/prompt library is copied into the app's governing system.

## Active references and configuration changes

PF00/PF01 now route to repository planning, source snapshots and handoff; PF01 D09 records the owner's transition. Obsolete “database audit issued, not executed” references in resource ownership, configuration, migration planning and ADR 0002 point to completed repository audit evidence. Root README reflects completed P05 fixture scope. Root/mobile `CLAUDE.md` import applicable AGENTS; root `AGENTS.md` owns documentation and AI review behavior. The Expo template license text is retained verbatim with `.md` extension. Machine-readable schemas, fixtures, workflows and dependency locks remain their native formats.

The API's new `.env.example` contains only safe fixture settings. Mobile's existing safe example is retained. No live credential variable or loader is invented. Full variable/provisioning/secrecy distinctions are in the handoff; future secret slots are explicitly absent from fixture environments.

## CI and reviews

Foundation adds a conservative whole-change classifier and an always-reported gate, retaining all four application job names. Ordinary docs skip those jobs; mixed code, instructions/PF/active prompts/handoffs, workflows, environment templates and unknown/missing comparisons receive normal checks. Tests cover Git history, renames, file modes, failure cases and candidate-policy/import substitution. Review found that the first candidate executed head-controlled tests before classification; the corrected workflow loads trusted base policy first in isolated Python and runs candidate tests only in the separate full-scope API job. The first candidate is not accepted as safe. Agent review behavior is governed by `AGENTS.md` per Nathan's explicit clarification. External Codex settings were read only: the service may launch a reviewer which must then classify and exit for ordinary docs. This is not a zero-invocation/cost guarantee, and no HDE/global review settings were changed.

## Acceptance and evidence

Verify Markdown homes, complete source recovery, active-link independence from Drive, secret-free templates, exact environment-name coverage, full-scope and docs-only classifier behavior, checked PR publication/reviews and actual merged state. Preserve the private-account branch enforcement limit. The [publication receipt](../continuity/migration-publication.md) records actual checks/PR/merge identities after execution; no pending check is represented here as passed.

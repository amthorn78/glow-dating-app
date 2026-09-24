# Repository documentation guide

All project documentation is Markdown (`.md`). The repository is the durable implementation authority; no assignment requires Google Drive. Notion coordinates status, ownership, blockers and evidence links. Keep decisions, specifications and evidence here even when first discussed in Notion or chat.

| Location | Keep here | Lifetime / naming |
|---|---|---|
| `docs/ephemeral/` | Single-use prompts and temporary handoff drafts | `YYYY-MM-DD-work-id-purpose.md`; record owner, scope and deletion condition. Promote unique decisions and evidence before pruning. |
| `docs/planning/` | Persistent plans, implementation briefs, dependency and decision summaries | Stable descriptive kebab-case filenames; dated observations use `YYYY-MM-DD`. Historical source snapshots live in `sources/` and are explicitly non-governing. |
| `docs/pf-canon/` | Existing application PF canon: GAPP-PF00 authority index and GAPP-PF01 sequence/constraints | Preserve document IDs, Markdown filenames and revision history. Separate from HDE canon. |
| `docs/adr/` | Focused architecture decisions | Existing numbered `NNNN-description.md` convention. State supersession instead of erasing history. |
| `docs/architecture/` | Component responsibilities, contracts and domain semantics | Stable descriptive names; distinguish implemented behavior from planned contracts. |
| `docs/operations/` | Setup, configuration, ownership, CI/review and runbooks | Current commands and exact names grounded in code. No secrets. |
| `docs/testing/` | Durable validation evidence and deferred acceptance | Phase/work-item names; identify commit, actual checks, failures and limits. |
| `docs/continuity/` | Current handoff, Claude handoff and publication receipts | Current handoff routes sessions; history is dated/superseded, never an active assignment. |

Start with [current handoff](continuity/current-handoff.md), [PF00](pf-canon/GAPP-PF00-Canon-Index-and-Authority.md), [PF01](pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md) and applicable `AGENTS.md` files. The [Claude manager brief](continuity/claude-code-handoff.md) is the complete receiving packet; the [initiation prompt](planning/claude-code-initiation.md) is intentionally persistent during this environment transition.

## Ephemeral promotion and pruning

Before deleting a temporary file, close its assignment, put every unique accepted decision/specification/evidence item in a persistent Markdown home, update incoming links and record the replacement in the relevant work record. Prune in a reviewed PR. Do not delete the only record of a failed check, unresolved risk or owner decision. Files still needed by an active session are not eligible. Ignored `.work/` holds reproducible local artifacts; it is never durable evidence or a documentation source of truth.

Machine-readable contracts, fixture data, locks, workflows and `.env.example` are executable/configuration artifacts, not prose documentation. Do not convert these to Markdown. Explanations of them belong in Markdown. Screenshots and logs may be CI artifacts; preserve their conclusions, identity and necessary evidence in Markdown without requiring expiring artifacts to understand the assignment.

## Behavior matters more than extension

Agent instructions (`AGENTS.md`, `CLAUDE.md`, `SKILL.md`, `*.instructions.md`), PF canon, all persistent planning/implementation briefs, active handoffs, manager instructions and active prompts affect agent behavior and receive full checks/review. Put new executable agent directions in those classified locations, not an ordinary notes file. Workflow, environment, schema, script and dependency changes also receive full checks. See [CI/review policy](operations/ci-and-branch-policy.md); mixed PRs never become documentation-only because their last commit changes prose.

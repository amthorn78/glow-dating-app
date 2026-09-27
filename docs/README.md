# Repository documentation guide

All project documentation is Markdown (`.md`). The repository is the durable implementation authority; no assignment requires Google Drive. Notion coordinates status, ownership, blockers and evidence links. It also carries a matching copy of the operational guidance and of the owner-direction register (OD-26); where they differ, the repository wins and Notion is corrected (OD-27). Keep decisions, specifications and evidence here even when first discussed in Notion or chat.

| Location | Keep here | Lifetime / naming |
|---|---|---|
| `docs/ephemeral/` | Single-use prompts and temporary handoff drafts | `YYYY-MM-DD-work-id-purpose.md`; record owner, scope and deletion condition. Promote unique decisions and evidence before pruning. Durable start procedures are not ephemeral; they live in `docs/planning/start-prompts/`. |
| `docs/planning/` | Persistent plans, implementation briefs, dependency and decision summaries, the manager workflow and the [Dev Manager charter](planning/dev-manager.md) | Stable descriptive kebab-case filenames; dated observations use `YYYY-MM-DD`. Historical source snapshots live in `sources/` and are explicitly non-governing. The start procedures for new managers and Dev Manager sessions live in `start-prompts/`; each is kept current and never pruned. |
| `docs/pf-canon/` | Existing application PF canon: GAPP-PF00 authority index and GAPP-PF01 sequence/constraints | Preserve document IDs, Markdown filenames and revision history. Separate from HDE canon. |
| `docs/adr/` | Focused architecture decisions | Existing numbered `NNNN-description.md` convention. State supersession instead of erasing history. |
| `docs/architecture/` | Component responsibilities, contracts and domain semantics | Stable descriptive names; distinguish implemented behavior from planned contracts. |
| `docs/operations/` | Setup, configuration, ownership, CI/review and runbooks | Current commands and exact names grounded in code. No secrets. |
| `docs/testing/` | Durable validation evidence and deferred acceptance | Phase/work-item names; identify commit, actual checks, failures and limits. |
| `docs/continuity/` | Current handoff, the frozen Claude handoff, publication receipts, the [owner-direction register](continuity/owner-directions.md), the [manager mistakes log](continuity/manager-mistakes.md), the [status and State of the App](continuity/state-of-the-app.md) and the [Dev Manager review log](continuity/dev-manager/README.md) with its reports | Current handoff routes sessions; `history/` is dated and superseded, never an active assignment. The register and the mistakes log are append-only. The State of the App is refreshed before each periodic Dev Manager review. The Dev Manager writes only its reports. |

Start with [current handoff](continuity/current-handoff.md), [PF00](pf-canon/GAPP-PF00-Canon-Index-and-Authority.md), [PF01](pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md) and applicable `AGENTS.md` files. A new manager starts from the [next-manager start procedure](planning/start-prompts/next-manager.md). The [Claude manager brief](continuity/claude-code-handoff.md) is the receiving packet of 24 September, frozen on 25 September; the [initiation prompt](planning/claude-code-initiation.md) records the executed first manager assignment.

## One home per fact (DM-01 P3)

Each kind of fact has one home. Other documents link to it rather than copy it.

| Fact | Its home |
|---|---|
| A work item's plan, results, decisions and open questions | Its brief in `docs/planning/` and its evidence record in `docs/testing/evidence/` |
| Routing: the current item, next actions, who waits on whom | The [current handoff](continuity/current-handoff.md), kept under 5 KB |
| Governing rules | `AGENTS.md` and `CLAUDE.md`, PF01, the manager workflow, the CI policy and the Dev Manager charter |
| Architecture decisions | `docs/adr/` |
| What the app asks of HDE's contract, and the delivered contract's receipt | The [HDE contract request](planning/hde-contract-request.md); the receipt goes in `docs/architecture/` when the contract arrives |
| Nathan's standing directions | The [owner-direction register](continuity/owner-directions.md) |
| The reasoning-strength matrix (models and levels), the TypeSafe rule, evidence and readings | The [reasoning-strength matrix](planning/reasoning-level-matrix.md); the request in force and the scoring script are the skill `.claude/skills/typesafe-scoring/`; Notion's usage log carries a copy and the uses table |
| Dev Manager consultations, verdicts and dispositions | The [review log](continuity/dev-manager/README.md) |
| Managers' mistakes | The [mistakes log](continuity/manager-mistakes.md) |
| The periodic status and State of the App | [A snapshot](continuity/state-of-the-app.md), refreshed only for a periodic review |
| Model and reasoning-level readings | The prompt's header and the Notion usage log |
| Live task state | The Notion Work Register row, which links here |
| Notion's copy of the operational guidance and the register | Implementation Control and its register page. They match the repository, which wins on any difference; every records batch checks them |
| History | `docs/continuity/history/` and Git |

## Ephemeral promotion and pruning

Before deleting a temporary file, close its assignment, put every unique accepted decision/specification/evidence item in a persistent Markdown home, update incoming links and record the replacement in the relevant work record. Prune in a reviewed PR. Do not delete the only record of a failed check, unresolved risk or owner decision. Files still needed by an active session are not eligible. Ignored `.work/` holds reproducible local artifacts; it is never durable evidence or a documentation source of truth.

Machine-readable contracts, fixture data, locks, workflows and `.env.example` are executable/configuration artifacts, not prose documentation. Do not convert these to Markdown. Explanations of them belong in Markdown. Screenshots and logs may be CI artifacts; preserve their conclusions, identity and necessary evidence in Markdown without requiring expiring artifacts to understand the assignment.

## Behavior matters more than extension

Agent instructions (`AGENTS.md`, `CLAUDE.md`, `SKILL.md`, `*.instructions.md`), PF canon, persistent planning and implementation briefs, active handoffs and active prompts affect agent behavior. Put new agent directions in those locations, not an ordinary notes file. Behavior-affecting Markdown is still documentation for CI and review: Nathan directed on 24 September 2026 that documentation runs neither application CI nor code/security review. The manager reads documentation changes when it integrates them, and the Dev Manager reads governing Markdown before its PR merges (DM-01 P1; [charter](planning/dev-manager.md)). Workflow, environment, schema, script and dependency changes receive full checks and review. See [CI/review policy](operations/ci-and-branch-policy.md); mixed PRs never become documentation-only because their last commit changes prose.

Any change made only of regular Markdown files is ordinary documentation, wherever it lives, except under a `.claude/` directory. Claude Code skills, commands, agents and rules can carry commands and permissions, so they stay full scope (Nathan, 24 September 2026). Documentation paths must not contain scripts or other executable content. A non-Markdown file, symlink or executable file anywhere makes the change full scope.

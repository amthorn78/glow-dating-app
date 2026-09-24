# Current handoff — Claude Code migration

**Owner direction:** pause new features; move implementation from ChatGPT web to Claude Code. The receiving session is the manager and first audits/optimizes its repository setup and documentation workflow. P06.1 is not currently dispatched. Nathan remains product/account owner.

1. Verify remote `amthorn78/glow-dating-app` main, open PRs and worktree. Read the [migration publication receipt](migration-publication.md) for the checked merged baseline. Never push synthetic snapshot history.
2. Read root and applicable nested `AGENTS.md` files, README files, [documentation map](../README.md), [PF00](../pf-canon/GAPP-PF00-Canon-Index-and-Authority.md) and [PF01](../pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md).
3. Read the **[full Claude handoff](claude-code-handoff.md)** and use the **[paste-ready initiation prompt](../planning/claude-code-initiation.md)**. Follow the [manager workflow](../planning/manager-workflow.md), not an imported prompt library.
4. Reconcile [Notion Control](https://app.notion.com/p/3e44590a05eb8118bf02f0dc0c3ea57c) / [Work Register](https://app.notion.com/p/71b769915b5b4e00830663770bc95f7e) status; repository Markdown contains durable assignment context. No Drive file is needed.

## Accepted application baseline

P01–P05 are complete at their recorded preparation/fixture scope. P05.3 PR14 merged as `ea394543533e99f611158b9026a2bd01de8d09b3`, tree `b1676a034b416bf459daf41405e3b12b5d782f6e`. [AB1-R012](history/AB1-R012.md) records exact candidate/main checks, review corrections and failure history. Its proposed P06 continuation is superseded by the migration direction. The earlier [P05.3 handoff](history/p05-3-handoff.md) is historical.

The app has fixture onboarding/profiles/media, eligibility/discovery and interactions, an API smoke runtime, contracts and static model/migration definitions. No real auth, persistence, Stream/HDE call, provider delivery, signed native build or release readiness is established. Readiness stays 503, provider sending is unavailable, database integration stays P11. The [completed dated database audit](../planning/database-audit-2026-09-23.md) is evidence, not permission to connect/mutate during this transition.

HDE and shared infrastructure remain protected by effect. Preferred future storage is clean app-owned schema/restricted roles in the same logical `railway` database, without legacy-user migration. Stream stays preferred; secret slots are future definitions, not working environment loaders. See the handoff inventory before asking for any credential.

## Next bounded assignment

Claude manager: review code, all applicable instructions and repository Markdown, CI and actual environment usage; propose and implement the smallest useful setup/instruction/template/documentation improvement using separate bounded implementation sessions. Keep feature work paused through that checkpoint, verify checks/reviews/merged state, preserve limits and update this handoff plus Notion pointers.

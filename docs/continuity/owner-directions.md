# Owner-direction register

Nathan Amthor's standing directions, one row each, in the order given. The Dev Manager recommended this register (DM-01 P3) so that no standing direction lives only in scattered tables and handoffs.

- **Append only.** A later direction that changes an earlier one gets its own row and marks the earlier row "Superseded by OD-nn". Rows are never deleted.
- **The quote is exact** where the words are known. Otherwise the row says "Recorded" and names where the direction was first written down.
- **The home** is the document that applies the direction. When a direction changes, its home changes too.

| ID | Date | Direction | State | Home |
|---|---|---|---|---|
| OD-01 | 23 Sep 2026 | Recorded in PF01 D08: App Builder 1 has full authority to create or modify application-owned objects across GitHub, Railway, Google Drive and Notion, except where the change affects the Glow HD Engine | In force as the app-only authority, protected by effect; the named sessions are historical | PF01 D08 |
| OD-02 | 23 Sep 2026 | *"the app should be in the same project as the HD Engine"* | In force | [ADR 0002](../adr/0002-same-project-application-services.md), PF01 §4 |
| OD-03 | 23 Sep 2026 | Recorded in Implementation Control: prefer the same logical PostgreSQL database as HDE, with app-owned schema and restricted roles; no legacy user information needs migration | In force; the database placement is open to Nathan's decision (DM-02 question 3) | PF01 §4, ADR 0002 |
| OD-04 | 24 Sep 2026 | Recorded (AP1-P05.1-002 revision 1.1): the application stays in one repository, `amthorn78/glow-dating-app` | In force | `docs/architecture/domain-and-data-boundaries.md` |
| OD-05 | 24 Sep 2026 | Recorded in PF01 D09: move from ChatGPT to Claude Code; repository Markdown is the operational authority; pause new features | In force; the feature pause is partly lifted by OD-12 | PF01 D09 |
| OD-06 | 24 Sep 2026 | *"this will be a manual relay. You give me prompts for the implementors, I relay back their findings and you follow up as needed. that is the process. I reinitiate you manually as needed."* and *"just make sure you don't restrict the implementor sessions, they can use whatever tools, subagents, wakeups, etc they need"* | In force; OD-15 adds the Dev Manager exception | [Manager workflow](../planning/manager-workflow.md) |
| OD-07 | 24 Sep 2026 | Recorded: a change made only of Markdown is ordinary documentation and skips application CI and code review; paths under `.claude/` stay full scope | In force; DM-01 P1 adds a Dev Manager read for governing Markdown | `AGENTS.md`, [CI policy](../operations/ci-and-branch-policy.md) |
| OD-08 | 24 Sep 2026 | *"I don't think we should start new tasks until CI and reviews are clear on a current one."* | In force; whether a known flake belongs to the current item awaits Nathan (DM-01 question 1) | Manager workflow |
| OD-09 | 24 Sep 2026 | *"I will trust you to manage the branches and PRs as you see fit."* | In force | Manager workflow |
| OD-10 | 24 Sep 2026 | Recorded: recommend a reasoning level with every prompt; TypeSafe scorer v4 as an advisory second reading | In force until Nathan decides the scorer's future after the pre-registered ten sessions (DM-01 question 3) | Manager workflow step 3; Notion usage log |
| OD-11 | 25 Sep 2026 | *"I also want you to track your mistakes."* | In force | [Mistakes log](manager-mistakes.md) |
| OD-12 | 25 Sep 2026 | *"3-5 recommendations accepted"*: a $0 budget; `STREAM_*` values on the server side only; after an unmatch or block neither person can send or see the conversation, with history kept out of sight only for safety reports. Then: *"resume P06.1, yes to reconfiguring the test app"* | In force; other feature work stays paused | [P06.1 brief](../planning/p06-1-chat-provider-proof.md) |
| OD-13 | 25 Sep 2026 | *"Proceed, leave it (Recommended)"*: the P06.1 proof leaves the Stream dashboard's administrator user untouched and accepts that its admin grants are emptied in the locked channel types | In force for P06.1 | P06.1 evidence record |
| OD-14 | 25 Sep 2026 | *"I accept your recommendation on S15. There should never be any indication that there is anything happening outside Glow."* | In force; conditional on the I1 review confirming S15; carve-outs await Nathan (DM-02 question 1) | [ADR 0003](../adr/0003-chat-display-rule.md), PF01 §7 |
| OD-15 | 25 Sep 2026 | *"I think this project has reached a level of complexity where a dedicated Dev Manager session would be valuable. Create that session now."* A second layer of oversight, run as a manual relay, with no scoring; a repeatable review mechanism | In force | [Dev Manager charter](../planning/dev-manager.md), PF01 D10 |

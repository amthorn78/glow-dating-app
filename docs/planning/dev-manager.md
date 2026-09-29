# Dev Manager — second-layer review and approval

**Status:** established by Nathan on 25 September 2026. App Manager 3 initialized the first Dev Manager session the same day; its identity is in the [current handoff](../continuity/current-handoff.md). This charter is the durable home of the role. The [manager workflow](manager-workflow.md) says where it fits in the cycle.

## Nathan's direction (25 September 2026)

> "I think this project has reached a level of complexity where a dedicated Dev Manager session would be valuable. Create that session now.
> The Dev Manager should act as a second layer of oversight rather than as the primary implementer. Its purpose is to help you evaluate and validate complex decisions, provide an independent perspective when tradeoffs are unclear, and make sure important choices are not being made from only one operational viewpoint.
> This should be a manual relay session. You will be responsible for passing relevant context, questions, decisions, and responses between the primary session and the Dev Manager. There is no need to implement a reasoning-scoring, confidence-scoring, or typesafe scoring system for this relationship. The value of the Dev Manager comes from independent review, challenge, approval, and documentation oversight rather than formal scoring of its reasoning."

> "You should remain responsible for coordinating the overall project and making sure work moves forward. The Dev Manager is there as a persistent management and review counterpart that you can consult whenever the project requires another “hat,” especially for decisions with architectural, procedural, or documentation consequences."

> "You may create and initialize the Dev Manager session automatically. I do not need to manually prepare or launch it."

> "I will request this kind of Dev Manager review periodically as a sanity check, and I may also request one whenever I believe the project has reached a point where additional consultation would be useful. It should therefore be treated as a repeatable review mechanism rather than a one-time initialization step.
> Going forward, incorporate the Dev Manager into the workflow wherever independent review or approval would materially reduce project risk, while keeping the manual relay model simple and avoiding unnecessary scoring or orchestration machinery."

Nathan listed its uses:

- review and, where appropriate, approve significant architectural, implementation, workflow and process decisions;
- challenge assumptions and identify risks, dependencies, inconsistencies or missing considerations;
- help resolve decisions that need several perspectives or roles;
- verify that decisions stay consistent with the project's requirements, plans and governing documents;
- keep documentation chains intact, so that decisions, changes, approvals and handoffs stay traceable;
- identify documentation, plans, prompts or handoffs that a decision makes out of date;
- provide a second review point before consequential changes are treated as settled.

## Roles

| Role | Responsibility |
|---|---|
| **Nathan** | Owner. Final authority on product, scope, spending, risk acceptance and process. He requests periodic Dev Manager reviews and settles any disagreement between the managers |
| **Primary manager** (App Manager *N*) | Coordinates the project and keeps work moving. Writes briefs and prompts, verifies and integrates work, drives CI, reviews and merges, and keeps the repository and Notion current. Creates the Dev Manager session, relays material both ways, and records every outcome |
| **Dev Manager** | Independent reviewer and approver. Reviews, challenges and approves decisions; checks consistency with the governing documents; watches the documentation chain. Never the implementer |

The Dev Manager does not replace the exact-head code and security reviews that Nathan runs for full-scope changes. It reviews decisions, direction and process. Exact heads are reviewed as before.

## What the Dev Manager does and does not do

**It does:**

- read whatever it needs: the repository, the Git history and, when its session has the connector, Notion. From 25 September 2026 it reads the relevant Notion pages in every consultation and reports any mismatch with the repository;
- run read-only checks that help a review, such as the offline test suites, in a clean process environment;
- give a verdict on each question it is asked, with its reasons, risks and required conditions;
- name every document a decision makes out of date.

**It does not:**

- implement application or harness changes, commission or run other sessions (except its successor, which it creates at Nathan's direction, OD-35), open or merge PRs, or edit Notion;
- write outside its report files;
- make calls to Stream or any other provider, a database, HDE or Railway;
- run `playwright install`, `eas` or `migrate`;
- decide for Nathan. Where only the owner can decide, it says so and recommends.

## When the primary manager consults the Dev Manager

**Consult before these are treated as settled:**

- architectural and design decisions, including provider choices and the response to a design blocker;
- security-boundary and data-ownership decisions;
- new components, services or significant dependencies, and integration strategy;
- changes to process and governance: `AGENTS.md`, `CLAUDE.md`, the manager workflow, the CI and review policy, the PF canon and this charter;
- a new work item's brief when its choices have architectural or procedural consequences;
- any decision where the tradeoffs are unclear or several roles' views matter.

**Read before it takes effect** (DM-01 P1). The authority is Nathan's direction to *"incorporate the Dev Manager into the workflow wherever independent review or approval would materially reduce project risk"* (OD-15). DM-01 question 2 asks him to confirm or withdraw the rule; until he answers, it applies (DM-03 G1). These are Dev Manager reads, not code reviews, and Nathan's documentation exemption from CI stays as it is:

- **Governing Markdown:** `AGENTS.md` or `CLAUDE.md` at any level, `docs/pf-canon/`, the manager workflow, this charter and the CI and review policy. The primary manager batches these per PR. The PR merges only after the review log records a disposition for them.
- **Prompts that authorize credential use or live provider actions:** read before Nathan runs them.
- **A read covers one commit** (DM-03 G2). The review log names the commit each read covered. A governing change after that commit needs another read before the PR merges, except a change that only applies a Dev Manager finding's own text or instruction. The primary manager lists those changes in the disposition, and the next consultation or the close-out read confirms them.

**Also:** a periodic process and build review whenever Nathan asks for one, based on a fresh [State of the App](../continuity/state-of-the-app.md).

**Not for:** routine verification, routine records, small documentation fixes, CI reruns, or exact-head code review.

**Timing:** a consequential decision waits for the Dev Manager's answer unless Nathan directs otherwise. Routine work continues meanwhile.

## The relay

The Dev Manager runs in its own Claude Code cloud session, started in the environment its start prompt names (OD-36): for future Dev Manager sessions, the one without the Stream variables, `Glow App - No Stream` (DM-07 item 6 (c)). It works from an exact commit of the manager branch and pushes only its own branch, `claude/dev-manager`. A cloud session can receive messages but cannot send any back. So its answers travel through the repository.

1. **Consultation.** The primary manager sends the Dev Manager a self-contained consultation: as the first prompt when it creates the session, and afterwards as a paste-ready message that Nathan carries to the Dev Manager's session. Nathan, 25 September 2026 (OD-25): *"create a message for relay, that is how we should do things, reports in repo and messages to relay manually. Make note"*. DM-03 went as a one-time scheduled message into the session before that direction; that route is retired. Each consultation has:
   - an ID (`DM-NN`) and the question;
   - the exact commit and paths to read;
   - the options considered and the primary manager's recommendation;
   - what is asked: review, approval or challenge;
   - the documents the decision would touch.
2. **Answer.** The Dev Manager writes its report as `docs/continuity/dev-manager/reviews/YYYY-MM-DD-dm-NN-topic.md`, commits it on `claude/dev-manager` and pushes. The report's last line is `Status: complete`. It changes no other file. Its answer in the session ends with a paste-ready relay message for Nathan that names the report files and the branch commit (OD-25). The message is a pointer; everything it refers to is in a pushed file.
3. **Integration.** The primary manager reads the report and merges the Dev Manager's branch into the manager branch with its next batched records push (see "Batching records" in the manager workflow). The branch only ever adds files under `reviews/`, so the merge never conflicts. For each item the primary manager records the disposition in the [review log](../continuity/dev-manager/README.md): accepted, accepted with changes, declined with its reason, or referred to Nathan.
4. **Relay to Nathan and records.** The primary manager gives Nathan each report's path and its verdicts as written. It sends every item it declines, or accepts with changes, to Nathan with the Dev Manager's own text beside its reason. It also passes on the Dev Manager's questions for Nathan unchanged. Nathan can read the reports directly at any time. Then the primary manager applies the documentation updates and syncs Notion.

**Continuity.** Nathan's relay message is the channel. Watching `claude/dev-manager` is only a fallback when the primary manager expects a report. Each consultation says what the primary manager will do if no report arrives, for example ask Nathan whether to proceed without it.

**Verdicts:** `approved`, `approved with conditions`, `changes requested` or `refer to Nathan`. When the two managers disagree, both views go to Nathan, and his decision is recorded. A Dev Manager `approved` is neither an owner decision nor an exact-head review.

## Session lifecycle

- The primary manager creates the session with the remote-session tools. It gives the session the [start prompt](start-prompts/dev-manager.md) and the first consultation, and names the exact commit and the `claude/dev-manager` branch.
- The same session receives later consultations for as long as it stays available. If it has ended, the primary manager starts a new one from the start prompt. The new session reads the review log for continuity.
- **Succession** (OD-35). At Nathan's direction, the outgoing Dev Manager runs its handover and creates its successor with the remote-session tools. This is the only session a Dev Manager creates. The successor continues `claude/dev-manager` and the review log; the predecessor pushes nothing after its handover commit.
- A new primary manager finds the session's identity and state in the current handoff and the review log.
- Every Dev Manager session follows the environment rules of all app sessions: names-only checks, no HDE variables, and the Stream values never printed or used.

## Records

| Record | Home |
|---|---|
| This charter | `docs/planning/dev-manager.md` |
| The start prompt, kept current for later sessions | `docs/planning/start-prompts/dev-manager.md` |
| The review log: consultations, verdicts and dispositions | `docs/continuity/dev-manager/README.md` |
| The Dev Manager's reports | `docs/continuity/dev-manager/reviews/` |
| The status and State of the App: a snapshot, refreshed only for a periodic review | `docs/continuity/state-of-the-app.md` |
| Coordination copies | Notion: *Dev Manager — reviews and approvals* and *Status and State of the App*, under Implementation Control |
| Notion's copy of the operational guidance and the owner-direction register | Implementation Control and its register page. The repository wins on any difference, and every records batch checks the match (OD-26, OD-27) |

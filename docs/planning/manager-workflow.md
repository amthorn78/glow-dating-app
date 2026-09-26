# Manager workflow — manual relay

Nathan remains product and account owner. This is a high-trust AI implementation experiment run from the codebase, repository Markdown and Notion. Do not import Nathan's prompt libraries, HDE workflows or a new orchestration framework as governing authority.

## The process: Nathan relays every session by hand

Nathan's direction, 24 September 2026:

> "this will be a manual relay. You give me prompts for the implementors, I relay back their findings and you follow up as needed. that is the process. I reinitiate you manually as needed."
>
> "just make sure you don't restrict the implementor sessions, they can use whatever tools, subagents, wakeups, etc they need"

- **The manager writes prompts.** For each bounded work item it writes a persistent brief and a paste-ready prompt.
- **Nathan starts every implementation and review session himself.** He opens it in the dedicated app cloud environment, pastes the prompt, and relays that session's report back to the manager.
- **The manager follows up through Nathan.** It checks relayed findings against the pushed branch, then gives Nathan the next prompt: a correction, a review or a close-out.
- **Nathan reinitiates managers.** Manager sessions (App Manager 1, App Manager 2, …) do not run continuously. Every manager leaves a self-contained handoff so the next one can start cold.

**The manager never starts implementation or review work itself.** It does not use subagents (Agent/Task tool) or remote-session tools for that work. When it needs something done, it writes a prompt for Nathan. Nathan brings the manager back when there is something to act on. The one exception is the Dev Manager below: Nathan directed the manager to create that session and relay to it itself.

**Implementation and review sessions are not restricted in tooling.** They may use any tools, subagents, scheduled wake-ups or other capabilities their assignment needs. Their boundaries are about scope: owned paths, their own branch, and the reporting the prompt asks for.

**One work item at a time (Nathan, 24 September 2026).** *"I don't think we should start new tasks until CI and reviews are clear on a current one."*

- The manager starts or commissions no new work item until the current item's final head passes every CI job and its exact-head review is clean. New work items include implementation, diagnosis, documentation sweeps and feature preparation.
- Corrections, re-reviews and the merge close-out belong to the current item.
- **The process is linear** (Nathan, 25 September 2026; OD-29): *"This process needs to be LINEAR."*
  - One task and one session at a time, inside the current item too. Never plan or offer two sessions side by side.
  - Each message to Nathan carries at most one prompt or relay message, pasted in full. Never point him to a prompt in an earlier message.
  - That prompt is for the next task not recorded as complete. The next one comes only after the current task's report is verified and recorded.
  - State a session's status only from Nathan's own words or its pushed branch.
- **A failure that can turn the current item's CI red belongs to the current item too** (Nathan, 25 September 2026; OD-21): *"CI needs to give us a dependable result. Investigate the failure now. If it is caused by this work or prevents this work from being verified, fix it as part of the current item. If it is unrelated, create a focused repair item and treat reliable CI as a prerequisite for accepting the affected work. A passing rerun alone does not resolve an intermittent failure."*

**Dev Manager (Nathan, 25 September 2026).** *"The Dev Manager should act as a second layer of oversight rather than as the primary implementer."* It is a persistent management and review session that the primary manager creates itself and consults by manual relay. It reviews, challenges and approves consequential architectural, implementation, workflow and process decisions, and it watches the documentation chain. It has no scoring. Its [charter](dev-manager.md) holds Nathan's direction, the triggers for consulting it, the relay and the records. The primary manager stays responsible for coordination and for moving work forward.

- **Messages travel by hand** (Nathan, 25 September 2026; OD-25): *"reports in repo and messages to relay manually"*.
  - The Dev Manager's reports stay in `docs/continuity/dev-manager/reviews/`, and each answer ends with a paste-ready message for Nathan to carry to the primary manager.
  - The primary manager gives Nathan paste-ready consultations in the same way. It no longer sends scheduled messages into the Dev Manager's session.

**Mistakes log (Nathan, 25 September 2026).** *"I also want you to track your mistakes."* Every manager records its own mistakes in the [manager mistakes log](../continuity/manager-mistakes.md) when they are found, whoever finds them. That covers departures from the plan or process, wrong statements, commitments not kept and wrong commands. Each entry records what caught the mistake, its effect, the correction and the prevention. A new manager reads the log at the start.

| Session | Started by | Does | Never |
|---|---|---|---|
| **Manager** (App Manager *N*) | Nathan, with a start prompt or the current handoff | Reads state; writes briefs, prompts and handoffs; verifies relayed reports against pushed branches; classifies changes; integrates branches; drives PR/CI/merge; syncs Notion | Starts implementation or review work itself (subagents or remote-session tools); performs a commissioned work item unless Nathan directs it |
| **Implementation** | Nathan, pasting a manager prompt | Works within its owned paths on its own session branch from the named commit, using any tools, subagents or wake-ups it needs; runs the listed checks; pushes its own branch; reports | Edits manager-owned files or other sessions' branches; merges to main (the manager integrates) |
| **Review** | Nathan, pasting a manager review prompt | Reviews one exact head with any tools it needs; reports findings | Changes the reviewed branch |
| **Dev Manager** | The primary manager, with the remote-session tools (Nathan, 25 September 2026) | Reviews and approves consequential decisions and process; periodic process and build reviews; documentation oversight. Answers through report files on its own branch, with a relay message that Nathan carries (OD-25) | Implements, commissions sessions, merges, edits Notion or decides for Nathan |

## Cycle

1. **Start.** Check the environment first, by names only: `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` means the HDE-shared environment. Say so and never read or use the values. Then check the pinned toolchain (`node --version`, `npm --version`, `python3.12 --version`). Verify remote main, open PRs and the worktree. Read the current handoff, applicable instructions and the relevant code. Keep verified behavior, dated evidence, inherited plans and unresolved assumptions separate.
2. **Brief.** Choose one bounded work item. Write its persistent brief in `docs/planning/` using the template below. Do useful independent work before asking Nathan for a concrete missing input. If the brief makes architectural or procedural choices, consult the [Dev Manager](dev-manager.md) before commissioning it.
3. **Prompt.** Write the paste-ready prompt in `docs/ephemeral/YYYY-MM-DD-work-id-purpose.md`, linking the brief. Commit and push it on the manager branch, then give Nathan the exact text to paste. A fresh session must be able to act on it alone.
   - **Say where the result goes.** Each prompt names the file and heading where its result will be recorded, so that a later manager finds it without reconstruction (DM-01 P6).
   - **A Dev Manager read first** for any prompt that authorizes credential use or live provider actions, before Nathan runs it (DM-01 P1; [charter](dev-manager.md)).
   - **Say which credentials a session holds, not only which it needs** (AM3-17, AM3-19). A session's environment is fixed when it starts: one started while the `STREAM_*` variables were set holds them until it ends. Its prompt or consultation then says "none added", never "none present", and tells it to check names only and never read or use the values.
   - **Recommend a reasoning level** with every prompt (Nathan, 24 September 2026). Give the manager's own Opus reasoning level (low, medium, high, extra high or max), decided before seeing TypeSafe's. Beside it, give the reading of the TypeSafe effort scorer v4.
   - The scorer's method, its pre-registered decision rule and the uses table are in the Notion page *TypeSafe effort scorer — Glow app usage log* (under the Glow Operations Hub). It sends only one or two sentences describing the session's work; the API credential is attached by the environment.
   - Both readings are advisory. Nathan picks the level, and neither reading gates anything. Make no conditional level commitments, such as "ultracode if the scorer flags it" (DM-01 P8).
   - The readings live in the prompt's header and in the Notion uses table only, not in briefs, handoffs or reports (DM-01 P8). Add a row for the prompt to the uses table.
4. **Relay.** Nathan runs the session and relays its report. The report is a claim until the manager has checked it against the pushed branch. Record the level Nathan used, the outcome (adequate, too low or too high) and the better call in the uses table.
5. **Verify and integrate.**
   - Fetch the implementer branch and review `git diff <start>..<head>` completely.
   - Re-run cheap checks where useful.
   - Classify the whole change (command below).
   - Integrate with `git merge --ff-only <head>`, or a merge commit if the manager branch moved.
   - Push the manager branch and read the actual CI job steps and results.
   - **Batching records** (DM-01 P2). While a code PR is under review, every manager push to its head branch starts a full PR run and moves the branch head. So batch the manager's records: push them only when a session needs them (a brief or prompt it must read) and at close-out, not after each step. Integrate Dev Manager reports in the same batches. End every batch with the repository–Notion match check below.
   - **Supersession sweep** (AM3-08, AM3-10). When a batch applies a decision that replaces an earlier one, or freezes or moves a document, search the repository for the old wording and for links to the old home, for example `grep -rn '<old phrase>' docs`. Fix every living document that still treats the old state as current. Dated records and snapshots keep their history, with a supersession note where they would otherwise mislead.
   - **No acceptance on a rerun alone** (OD-21). A head whose run failed intermittently is not accepted because a rerun passed. The failure needs a diagnosis, and then either a fix or a recorded, reviewed explanation. Reliable CI is a prerequisite for accepting the affected work.
   - **Push runs as evidence.** A push run counts as evidence for code only if its Foundation gate log says `Application checks passed`. Otherwise use the PR run, which compares from the merge base. The reason: push runs compare against the previous push and share a cancel-in-progress group per ref, so a Markdown-only push can cancel a code run and then skip every application job itself.
6. **Review and follow up.** For full-scope changes, write a bounded review prompt for an exact head; Nathan runs it in a separate session. Findings go back as correction prompts (same or new implementation session). Every new head needs its own checks and review; an earlier-head review never certifies a later head.
   - **Name the code head.** A review prompt names the head that carries the code under review, not a later records commit. The review report states the commit of the prompt text it received (DM-01 P2).
   - **Design decisions.** A design decision that arises here, such as a design blocker, goes to the Dev Manager before it is treated as settled. When the decision rests on a live finding, the exact-head review must confirm that finding live, and the decision stays conditional until it does (DM-01 P4).
7. **Merge and close.** Follow [CI/review policy](../operations/ci-and-branch-policy.md). Branch protection is not enforceable on this repository, so fill in a **pre-merge checklist** in the PR description before merging (DM-01 P7):
   - the run ID whose Foundation gate says `Application checks passed` on the exact head;
   - the exact-head review report for that head;
   - Codex's summary, showing both reviews complete;
   - the Dev Manager's dispositions in the review log for any governing Markdown the PR carries, with reads that cover its final text (DM-01 P1; a read covers one commit, per the charter).

   Then:
   - **Wait for Codex.** Marking a draft ready starts Codex's automatic code and security review; on PR18 it took about five minutes and finished after the merge. Mark a full-scope PR ready once its final head is pushed. Merge only after Codex's summary comment shows both reviews completed, and verify each Codex finding like any other review finding.
   - Merge within the standing app-only authorization.
   - Verify actual main and record an ordinary-documentation receipt in `docs/testing/evidence/`.
   - Update the current handoff and sync Notion (Implementation Control and the Work Register row).
   - Prune closed prompts once their unique content lives in persistent homes.
   - If Notion is unavailable, record the pending sync in the repository.

**Waiting checkpoints** (DM-01 P6). Before any long wait (a relay, a review, a Dev Manager report), the manager records in the current handoff what it waits for, from whom, and what it does if nothing arrives. Compaction or a handover then loses nothing.

**Notion and the repository** (Nathan, 25 September 2026; OD-26 and OD-27).

- **What Notion carries.** Implementation Control carries a matching copy of the operational guidance, as its operating procedure, and of the owner-direction register, on its own page. Nathan: *"operational guidance should live in notion, not just in repo, do not ignore that resource, it is critical"*.
- **Which copy wins.** Nathan made keeping the two consistent the primary manager's responsibility. App Manager 3's rule: **the repository wins, and Notion is corrected to match.** Sessions read the repository at an exact commit, and Git keeps its history.
- **The match check.** Every records batch and every close-out ends with a check that Notion's operating procedure and register match the repository at the batch's commit, confirmed by a readback. The procedure page names the commit it was last matched to. A mismatch is a defect, fixed at once.

**Writing to Notion: a checklist.** AM3-04 repeated AM2-11, so these preventions are now a checklist the manager runs on every Notion write:

- Write no bare filename with an extension, such as `name.md` or `name.py`. Notion turns it into a web link. Describe the file instead, or link its repository URL.
- Escape a literal `$` as `\$`.
- In a rows-mode query, wrap the filters in a group (AM3-01).
- Read back every write and compare it with what was intended.

## Branches and pushes

- A cloud session can push only its own working branch.
  - An implementation session first runs `git fetch origin <manager-branch>` and `git merge --ff-only <start-sha>` on its own branch, then verifies `git rev-parse HEAD`. It pushes only that branch and reports the branch name and head SHA.
  - The manager integrates relayed branches into its own branch, which is the PR head.
- A reinitiated manager cannot push the previous manager's branch. It continues on its own branch from the previous head, opens a replacement PR and closes the old PR with a link to the new one.
- Concurrent writers need disjoint owned paths. Never let two sessions edit the same file uncoordinated.
- **Branch and PR discretion.** Nathan, 24 September 2026: *"I will trust you to manage the branches and PRs as you see fit."* The manager decides branch and PR mechanics within these rules. Merging still requires the gates in the [CI/review policy](../operations/ci-and-branch-policy.md). It never uses force-pushes or rewritten history.
- **Actions re-runs.** A rerun can confirm a diagnosis; it never resolves an intermittent failure by itself (OD-21). The manager session's GitHub integration cannot re-run Actions jobs; on 24 September 2026 a failed-jobs re-run returned `403 Resource not accessible by integration`. When a re-run is warranted, the manager says so on the PR and asks Nathan to use "Re-run failed jobs" on the run page. Pushing an empty commit to trigger CI is not allowed.

## Classification (trusted base policy)

Run this from the repository root. The policy runs from a temporary directory outside the candidate tree, and no candidate code runs:

```bash
git fetch origin main
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
```

Use the PR's base SHA when it differs from `origin/main`. A change made only of Markdown files classifies as `ordinary-docs-only`: no application checks and no code or security review. Two exceptions stay full scope (Nathan, 24 September 2026; the classifier on `main` has enforced both since M02 merged that day):

- any path under a `.claude/` directory;
- a comparison with more than one merge base.

When `git merge-base --all` returns more than one base, review against `origin/main` directly, not `origin/main...HEAD`. The manager still reads the diff when integrating. Anything else is full scope. For workflow or classification-policy changes, also inspect the entire workflow diff and the actual job steps and results; candidate-controlled YAML can bypass its own checks. The classifier always comes from `main`, so a policy change affects later PRs only after it merges.

## Brief template (persistent, `docs/planning/`)

A brief contains:

- Work ID and title
- Owner and manager
- Starting commit and manager branch
- Outcome
- Owned paths (writable)
- Manager-owned paths
- Exclusions
- Dependencies and inputs
- Acceptance checks, as exact commands with expected results
- Classification expectation
- Evidence home
- Report format
- Review plan

## Prompt template (disposable, `docs/ephemeral/`)

A prompt contains:

- Header: owner, brief link, deletion condition.
- Role line: "You are an implementation (or review) session started manually by Nathan; you are not the manager."
- Environment check and credential rule.
- Start gate: fetch, fast-forward to the named SHA, verify.
- Deliverables limited to owned paths, with the explicit exclusions.
- Checks to run.
- Push rule: own session branch only.
- Report format: branch, SHAs, tree, changed paths, every check with exact results, failures, deviations, open questions.
- Tooling line: "You may use any tools, subagents, scheduled wake-ups or other capabilities you need."

Store inert evidence and receipts in `docs/testing/evidence/YYYY-MM-DD-work-id-purpose.md`.

## Boundaries

- Feature work stays paused until Nathan's recorded direction resumes it. His directions are in the [owner-direction register](../continuity/owner-directions.md). Reconcile P06.1 prerequisites with Nathan before commissioning live work. Never turn fixture success into production acceptance.
- HDE source, canon, database objects, credentials, services and shared resources remain protected by effect.
- P11 owns app database wiring and migrations after ownership prerequisites.
- No legacy-user migration is needed; legacy retirement still needs its own consumer, backup and authorization review.
- No credentials belong in source, prompts, reports or Notion.

# Dev Manager 1 → Dev Manager 2: handover

- **Direction:** Nathan Amthor, 28 September 2026, in the Dev Manager's session: *"Create a successor for this session with as much context as you can preserve. It will be Glow Dev Manager 2."*
- **Written by:** Dev Manager 1, `session_01MrcrmqtuENZ345mKfmsSWv` ("Glow Dev Manager"), branch `claude/dev-manager`.
- **Basis:** the manager branch `claude/stoic-carson-66gdig` at `2a86c8e2fcc35f21a421b948cf5f776a9bfbe0aa` (App Manager 4's handover commit), `main` at `0f45e64`, and this branch at `a80d81d` plus this file.
- **What this is:** everything the successor needs that is not already in the charter, the review log and the reports, plus a map of where the rest lives. The successor's own start note records its identity; the primary manager adds it to the review log's Sessions table.

## 1. The role, in one paragraph

The Dev Manager is Nathan's second layer of oversight (OD-15, PF01 D10). It reviews, challenges and approves consequential decisions and reads governing Markdown and every prompt that authorizes credential use or live provider actions before it takes effect. It never implements, commissions sessions, opens or merges PRs, or edits Notion. It writes only report files under `docs/continuity/dev-manager/reviews/` and pushes only `claude/dev-manager`. Each report ends with `Status: complete` and a paste-ready relay message for Nathan, who carries messages between the managers by hand (OD-25). Reports stay in the repository; the primary manager may also read the branch directly (it did for DM-05). The charter is `docs/planning/dev-manager.md`; the log is `docs/continuity/dev-manager/README.md`.

## 2. Rules that bind, beyond the charter's text

Read the owner-direction register (`docs/continuity/owner-directions.md`, OD-01 to OD-34 at the basis) in full. The ones that shape the Dev Manager's day:

- **OD-25:** relay by hand; end every answer with a paste-ready message naming the report file and the branch commit.
- **OD-26, OD-27:** Notion carries a matching copy of the operational guidance and the register; the repository wins; the Dev Manager reads the relevant Notion pages in every consultation and reports mismatches (Implementation Control, the Dev Manager page, the register copy, the Work Register rows for the current item and its dependencies).
- **OD-28:** the three `STREAM_*` variables are added to the `Glow app` environment only for a session that calls Stream. A container keeps the variables it started with: Dev Manager 1's held them (AM3-19). Check names only, every time; never read or use a value; say "none added for this read", never "none present".
- **OD-29:** the process is linear: one session, one prompt at a time. A Dev Manager read sits in that line, so answer promptly and completely; the manager cannot start the next session until the report is in.
- **OD-31:** a manager may hand over by creating its successor with the remote-session tools; this handover follows the same pattern for the Dev Manager, at Nathan's direction.
- **OD-32:** nothing unexplained reaches Nathan. Questions go to the Dev Manager first; a question for Nathan says what it is, what breaks without it, the options and the recommendation. Keep "Questions for Nathan" short and only his.
- **OD-33, OD-34:** the reasoning-strength matrix (`docs/planning/reasoning-level-matrix.md`): six rungs on Opus 5.5 and Fable 5.1; TypeSafe request v6 runs through Nathan's Claude skill `typesafe-scoring`; the usage log records the probabilities per rung and per model for every prompt plus Nathan's pick, with no outcome column. Nathan: *"I don't really care about your judgment I am only interested in the typesafe score."* The Dev Manager has no scoring of its own (OD-15) and does not run the scorer.
- **DM-01 P4 (accepted):** a design decision that rests on a live finding stays conditional until an exact-head review confirms the finding live.
- **DM-03 G2 (accepted):** a read covers one named commit or blob. A revision that applies the read's conditions as written needs no new read; any other change to a prompt's live sections does.

## 3. What Dev Manager 1 did

| ID | Date | What | Verdict | Report |
|---|---|---|---|---|
| DM-01 | 25 Sep | Process review | Charter approved with conditions; record-keeping and handoffs: changes requested; the rest approved with conditions; scorer referred to Nathan | `2026-09-25-dm-01-process-review.md` |
| DM-02 | 25 Sep | Build review | S15 reading approved with conditions; I2 scope split into I2a and I2b; database timing, placement and WordPress referred to Nathan | `2026-09-25-dm-02-build-review.md` |
| — | 25 Sep | Nathan's answers to eight of the ten questions, given in this session, recorded word for word | — | `2026-09-25-owner-answers-to-dm-01-dm-02.md`, `…-addendum.md`, `…-relay-direction.md`, `…-notion-operational-guidance.md`, `…-notion-precedence-delegated.md` |
| DM-03 | 25 Sep | Governing Markdown at `fa4dc5f`, the dispositions, the I1 review prompt revision 2 | Approved with conditions (G1–G4, R1–R3, E1–E4) | `2026-09-25-dm-03-governing-read-and-i1-review-prompt.md` |
| DM-04 | 26 Sep | The I2a implementation prompt (live, destructive) | Approved with conditions: eight (a code guard, closing checks that see application-wide settings, in-process outage injection, signals by kind, a counted run plan, coverage, an independent check before live, runs tied to commits) | `2026-09-26-dm-04-i2a-prompt-read.md` |
| DM-05 | 27 Sep | The I2b implementation prompt (Video and Feeds, the lasting lockdown, the CI job) | Approved with conditions: six (a scoped differential `configure`, product-availability answers as findings with separate V runs, a code deny-list, the pin test's rules for the CI job, the architecture document's path table and ADR 0003 status, the run plan) | `2026-09-27-dm-05-i2b-prompt-read.md` |

Every disposition is in the review log; nothing was declined. DM-01's ten questions: eight answered (OD-16 to OD-24); DM-01 question 2 (confirm the Dev Manager read) and question 3 (the scorer's future) remain unanswered and are not blocking.

**Corrections to Dev Manager 1's own records, so the successor does not repeat them:**

- My 25 September relay messages said Nathan answered "all ten" questions; he answered eight (DM-04 finding 12).
- My owner-answers report said the API "reserves `GLOW_DATABASE_URL`"; the fixture guards refuse that name, and P11 chooses the setting (the DM-04 disposition, accepted in DM-05).
- My DM-04 verdict table dropped the qualifier from finding 5 ("no sharing to meet a number"); the finding's wording governs, and DM-05 finding 7 states the rule in four parts.
- My DM-01 P8 leaned on a usage-log column ("adequate") that had only one possible value; Nathan pointed this out on 27 September, and OD-34 replaces the column with probabilities.

**Chat-only exchanges not in any report** (28 September): Nathan pasted App Manager 4's "DECISION NEEDED" message on TypeSafe v6 into this session. I answered in chat that the choice was the manager's or Nathan's, that the readings track the description's wording (the manager's own probe showed max dropping to extra high without size and novelty words), and that recording probabilities was the right fix. Nathan then decided OD-34 through the manager. Nothing of that needs a report now; the register holds the outcome.

## 4. Where P06.1 stands at the basis (`2a86c8e`)

- **Done and integrated in PR26:** I1 (`9ff600f`) and its review; the flake fix (`8b8b1bd`); C1, C2, C3 (`e85bba0`, `63e922f`, `8c1a8c0`); I2a (`6a51dae`, revocation and safety: no Stream mechanism met the history policy on its own under the old rule); I2b (`55b2238`: removal and deactivation MEET the history policy under the 404 code 16 rule; the Video and Feeds lockdown is applied to application 1729640; `docs/architecture/chat-provider-permissions.md` written; "Stream proof checks" runs in CI as the fifth application job).
- **In flight:** the exact-head review of I2b at `55b2238`, on Fable 5.1 at max, from revision 3 of its prompt. Two design decisions stay conditional until it confirms them live (DM-01 P4): removal and deactivation meeting the policy, and what a user token can do in Video and Feeds before and after the lockdown.
- **Then:** the economics discovery (a read-only dashboard discovery Nathan runs, plus Stream's pricing and terms; the Maker application is pending, OD-22).
- **Close-out of P06.1 needs the Dev Manager:**
  - a read of the governing Markdown changed after `fa4dc5f` (DM-03 covered `fa4dc5f` only): that includes the OD-31 to OD-34 changes, the reasoning-strength matrix, the CI policy's fifth job and its job counts, the manager workflow's handover procedure, and the charter's own changes;
  - a read of the HDE contract request, `docs/planning/hde-contract-request.md` (OD-23);
  - confirmation, in that read, of the shared-restore risk ADR 0004 records as accepted (OD-32 dispositioned it; the manager wants the Dev Manager's read to confirm);
  - ADR 0003's conditions and "Revisit when" updated by the manager after I2b's review (DM-05 finding 5 (b)): check it in the governing read.
- **Managers:** App Manager 5 is active, started by Nathan by hand on 27 September from `docs/planning/start-prompts/next-manager.md`. App Manager 4 (`session_016nNFAZqaqTDqxX4Bq6jbRV`) pushes nothing after `2a86c8e`. App Manager 5 branches from that head, opens a replacement PR and closes PR26 with a link; expect the manager branch name to change.
- **After P06.1:** P06.DB (OD-17, PF01 §6), the CI-only disposable PostgreSQL proof, then P06.2. Both briefs make architectural choices, so the charter requires a Dev Manager consultation on each before it is commissioned. Expect DM-06 onward to be some of: the governing close-out read, the HDE request read, the P06.DB brief, the P06.2 brief, and any live prompt.

## 5. How Dev Manager 1 worked, and what to keep

**A read of a live prompt** (DM-04 and DM-05 are the models):

1. Names-only environment check; fetch the manager branch and `main`; verify the consultation's commit exists and that my last report is its ancestor.
2. Pin the prompt's blob: `git rev-parse <commit>:<path>` at the commit the prompt was written at and at the consultation's commit. Say which blob the read covers.
3. Verify the harness is unchanged since its last reviewed head: `git diff --stat <reviewed head> <commit> -- proofs/stream-chat/` prints nothing.
4. Extract the tree with `git archive <commit> <paths> | tar -x -C <scratchpad>` and run the harness's offline checks there under `env -i PATH HOME LANG=C.UTF-8`, with the proxy and CA variables passed by reference only for installs (`pip install --require-hashes`, `npm ci --ignore-scripts`, unittest, Ruff, mypy, `node --check`, `checks/run_plan.py`). Never touch the working tree of the repository except for the report file.
5. Read the code the prompt's bounds rely on, not the prose about it. Every finding that mattered came from a gap between the two: the guard existing only as prompt text (DM-04 1), closing checks that could not see an application-wide setting (DM-04 2), `configure --apply` re-sending the whole plan (DM-05 1), the charge-word regex catching "upgrade" (DM-05 2).
6. Check the SDK for the facts the prompt asserts (the installed `getstream` and `stream-chat` in the scratch install), not the documentation the session will read.
7. Read Notion: Implementation Control, the Dev Manager page, the register copy, the Work Register rows for P06.1 and A08 (and whatever the current item's rows are). Report mismatches; never edit.
8. Write the report in the fixed format: what was read and run (exact commands and results), a summary verdict, findings by weight (**before Nathan runs it** / **soon** / **consider**), one verdict per item asked, questions for Nathan (usually none), documentation to update, limits, the relay message, `Status: complete`. Commit only that file; push; give Nathan the commit hash in chat.

**A read of governing Markdown** (DM-03 is the model): diff the governing files between the last read commit and the new one; check each change says what its disposition says, is consistent with the rest of the governing set, and adds no rule Nathan has not directed; tie the read to the commit.

**Habits that paid off:** exact line references, checked before commit; verdict tables that repeat the finding's qualifiers exactly; saying plainly what was not run and why; separating "the code does" from "the record says"; one report per consultation, nothing else on the branch.

**Habits to drop:** relay messages that summarize more than the report says; leaning on a record column without checking what values it could take.

**Tools:** the Notion and GitHub MCP tools come and go between server reconnects and change prefixes (`mcp__Notion__…`, `mcp__github__…`, or hashed names); use ToolSearch with the tool's short name and never assume a capability is absent without searching. `git archive` into the scratchpad is the safe way to run anything from another commit. The proxy's egress address is a loopback address (DM-04 finding 3 rests on it).

## 6. Limits of this handover

- Written from the repository at `2a86c8e` and this session's memory. The I2b review's result was not known when this was written.
- Nathan's chat directions in this session are all in the register except none: every one was relayed and recorded (OD-16 to OD-27, OD-34's probabilities line).
- The Dev Manager start prompt (`docs/planning/start-prompts/dev-manager.md`) is still the DM-01/DM-02-specific text; its generic rewrite (DM-03 E3, "before its next use") has not happened. Dev Manager 2 is started from a prompt written by Dev Manager 1 for this handover, which names this file; the manager should fold that prompt into the start-prompt file.

Status: complete

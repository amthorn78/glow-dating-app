# Dev Manager 2 → Dev Manager 3: handover

- **Direction:** Nathan Amthor, 25 October 2026, in Dev Manager 2's session: *"Create a new version of this session, Glow Dev Manager 3, to carry on with this role."* (OD-35: at Nathan's direction, the outgoing Dev Manager runs its handover and creates its successor with the remote-session tools.)
- **Written by:** Dev Manager 2, `session_015DxVkL8PXn2YaauE6RdSWN` ("Glow Dev Manager 2"), branch `claude/dev-manager`.
- **Basis:**
  - the manager branch `claude/magical-wozniak-yfmmx2` at `1ec5186390efdaccd1384fda5c798790f57e5462` ("DM-24 integrated: CX9 corrected before the merge (C2-C2); DM-25 on the re-review order");
  - `main` at `a8e952895ebd3ffc9ef0e4d195c8a7111c69b3ae` (PR32's merge);
  - this branch at `1a4fc1b` (DM-24), plus this file.
- **What this is:** everything the successor needs that is not already in the charter, the review log and the reports, with a map of where the rest lives. The successor's start note records its identity, and the primary manager adds it to the review log.

## 1. The role, in one paragraph

The Dev Manager is Nathan's second layer of oversight (OD-15, PF01 D10).

- **What it does:** reviews, challenges and approves consequential decisions. It reads governing Markdown before the PR that carries it merges, and every prompt that authorizes credential use or a live provider action before Nathan runs it.
- **What it never does:**
  - implement or commission sessions (except its successor, at Nathan's direction, OD-35);
  - open or merge PRs;
  - edit Notion;
  - call Stream, a database, HDE, Railway or the TypeSafe API;
  - run `playwright install`, `eas` or `migrate`.
- **Where it writes:** only report files under `docs/continuity/dev-manager/reviews/`, each ending with the line `Status: complete`. It pushes only `claude/dev-manager`.
- **The relay:** Nathan carries messages between the managers by hand (OD-25). The primary manager reads the branch, merges the report into the manager branch and records a disposition per item in the review log.
- **The governing documents:** the charter, `docs/planning/dev-manager.md`; the log, `docs/continuity/dev-manager/README.md`.

## 2. Rules that bind, beyond the charter's text

Read the owner-direction register (`docs/continuity/owner-directions.md`, OD-01 to OD-46 at the basis) in full. These shape the Dev Manager's work most.

**Owner directions:**

- **OD-25:** relay by hand. End every answer with a paste-ready message that names the report file and the branch commit.
- **OD-26, OD-27:** Notion carries a matching copy of the operational guidance and the register, and the repository wins. Read the relevant Notion pages in every consultation and report mismatches; never edit.
- **OD-29:** the process is linear, one session and one prompt at a time. A Dev Manager read sits in that line: answer promptly and completely.
- **OD-32:** nothing unexplained reaches Nathan. Questions go to the Dev Manager first. A question for Nathan says what it is, what breaks without it, the options and the recommendation, in plain words. Most consultations end with "no item is Nathan's".
- **OD-36:** two app environments. `Glow app` holds `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET`; `Glow App - No Stream` holds none.
  - The charter puts future Dev Manager sessions in `Glow App - No Stream`, and Dev Manager 3 is created there.
  - Dev Manager 2's container was created in `Glow app` and held the three names throughout. It never read or used them.
  - Consultations written for Dev Manager 2 say "your container holds the three `STREAM_*` variables". Check the names yourself and record what you find.
- **OD-41:** Codex's security reviews are gone. Before a merge, Codex's code review of the final head is the Codex check, and the exact-head review sessions Nathan runs stay.
- **OD-45:** D8 is decided as option (b): no Stream credential in the app.
  - Its row's "State" is in DM-21 1.1's words: Stream stays the provider behind Glow's server, as costed.
  - Nothing Stream adds takes effect for Glow without a recorded decision. A detected addition is turned off where the targets name it, or kept only by a recorded decision.
  - A feature that changes what members see, or what is done with their messages, is Nathan's to decide (the charter: product and scope are his).
  - DM-21, DM-22 and PF01 1.12 carry it.
- **OD-46:** App Manager 7 created App Manager 8 (25 October), and C2-C1's exact-head re-review was withdrawn as premature (AM7-13).

**Review rules:**

- **DM-03 G2, and the charter's exception:** a read covers one named commit. A revision that applies a read's conditions as written needs no further read; any other change to a prompt's live sections, or to governing Markdown, does. Write conditions as replacement text where wording matters, so the manager can apply them verbatim.
- **DM-23's rule, used again in DM-24:** a defect in a stage's own code that misses an item of that stage's prompt (or a fix-here class the prompt names) is fixed before the stage merges. A nit that misses no item is a follow-up. A defect only P11's environment can show is carried to the P11 plan.

## 3. What Dev Manager 2 did

| ID | Date | What | Verdict, in short | Report commit |
|---|---|---|---|---|
| — | 28 Sep | Start note | — | `0773eaa` |
| DM-06 | 28 Sep | P06.1 economics discovery prompt (Claude in Chrome, read-only) | Approved with conditions; one session | `8ba418a` |
| DM-07 | 29 Sep | P06.1 close-out read: governing Markdown, the HDE request, ADR 0004's restore risk, the lockdown | Approved with conditions; item 6 (c) Nathan's, answered in this session (OD-36, recorded at `f86f28d`) | `a60d8c1` |
| DM-08 | 29 Sep | P06.DB brief | Approved with conditions; the CI policy and review plan changes requested | `70f65f0` |
| DM-09 | 5 Oct | PR28's governing read and C1's review dispositions | Approved | `bc0306c` |
| DM-10 | 5 Oct | CX3 and the run's marker | Approved with 2.1 to 2.5; the CI policy narrowly changed | `9f2e79d` |
| DM-11 | 5 Oct | The C2 prompt's departure from DM-10 2.3 | Approved in replacement words | `91c5c2c` |
| DM-12 | 5 Oct | `dbshell` against DM-10 2.2 | Outside the correction classes; a guard before P06.2's first suite run | `b06fe29` |
| DM-13 | 5 Oct | P06.2's brief and PR29's governing changes | Approved with conditions; D8 not referred then, option (a) recommended | `80ce6c6` |
| DM-14 | 6 Oct | Stage A's governing read and review dispositions | Approved with conditions; F1's mechanism for Stage B | `e85bad6` |
| DM-15 | 6 Oct | Stage B split into B1 and B2, B1's points | Approved with conditions | `c748c64` |
| DM-16 | 23 Oct | Stage B2's prompt (the secret, live actions, `getstream`) | Revision 1 does not run; conditions 1.1 to 7.2 | `cd5b799` |
| DM-17 | 23 Oct | Stream's additions D1 to D4, B2-C1 | Approved with conditions; the D8 question referred to Nathan after the live rows, recommending (b) | `0ab61e4` |
| DM-18 | 23 Oct | The fifth addition, B2-C2 | Approved with conditions 2.1 to 7.1 | `f0a43c9` |
| DM-19 | 23 Oct | D6, the derived-change rule, B2-C3 | Approved with conditions 2.1 to 4.1 | `821efc7` |
| DM-20 | 23 Oct | B2's live rows, D10, the D8 costing and message | D10 (b); costing fair with 4.1 to 4.4; message rewritten (section 7) | `ca806e3` |
| DM-21 | 24 Oct | OD-45's register row and homes | Approved with 1.1 and 2.1 to 2.4 | `278369e` |
| DM-22 | 24 Oct | Stage C under OD-45, C1's prompt, PF01's Chat row | Approved with 2.1 to 12.1 (the text digest check, visibility order, no lock across the provider call) | `f9c624d` |
| DM-23 | 24 Oct | CX8 (read cursor) | (b): C2-C1 before the merge, with 2.1 to 2.6 | `c8bc632` |
| DM-24 | 25 Oct | CX9 (late responses undo a revocation) | (b): C2-C2 before the merge, with 1.1 to 1.6 and 2.1 | `1a4fc1b` |

Every disposition is in the review log. Through DM-23, every item was accepted as written, with nothing declined. DM-24's items 1, 3 and 4 were accepted as written; its item 2 went to DM-25 (section 5).

**Dev Manager 2's own errors, recorded, so the successor does not repeat them:**

- **DM-10 2.3:** a `pg_toast` query that counts PostgreSQL's own relations. The manager caught it, and DM-11 replaced it.
- **DM-10 2.2's heading** overstated what its body required (DM-12).
- **DM-17 5.1** asserted that `tzdata` stays in the lock without reading the lock (AM7-01). Owned in DM-18.
- **DM-17 2.3's allowed-change set** left out what the plan does to the roles' `scopes`. That is a share of AM7-04, owned in DM-19.
- **DM-18 missed a stale cross-reference** in B2-C2's prompt, a share of AM7-03. Since then I check every "section N item M" in a prompt I read.
- **DM-17 did not ask** for the architecture document's section 5, step 2, to follow the chat target's widening. Owned in DM-20 6.1.
- **DM-22's conditions for C2 named no test for "seen"** (item 8). Owned in DM-23 2.6.

**The lessons:**

- read the code a claim rests on, not the prose about it;
- derive every effect of a planned change on every read a comparison covers;
- check cross-references against the current numbering.

## 4. Where things stand at the basis (`1ec5186`)

**Managers:**

- App Manager 8 holds the manager branch and PR33, created by App Manager 7 on 25 October (OD-46) in `Glow App - No Stream`.
- App Manager 7 (`session_01C6hXSgYhB4rXBxAfWfXBRf`) pushes nothing after its handover.
- The current handoff is `docs/continuity/current-handoff.md`.

**P06.2 (the chat integration):**

- **Merged:** Stages A (PR29), B1 (PR30), B2 (PR31, `3572c41`) and C1 (PR32, `a8e9528`).
- **Stage C2,** the mobile interface on fixtures, is in PR33, held.
  - C2's exact-head review approved it with six nits.
  - **CX8,** Codex on `96ce36b`: the read cursor advanced past messages never in view. DM-23 sent it to a correction pass. C2-C1 is done and integrated (code `311b07e`, records `73ef97e`, run 40145402786).
  - **CX9,** Codex on `73ef97e`: `revoke()` leaves outstanding requests valid, so a late page undoes a revocation. DM-24 sent it to C2-C2, with 1.1 to 1.6.
  - **C2-C1 has no exact-head review yet:** Nathan withdrew it as premature (AM7-13; OD-46).
- **DM-25 is coming to you, with Nathan to carry:** `docs/ephemeral/2026-10-25-dm-25-p06-2-re-review-order.md`. It replaces DM-24's item 2, whose premise (a C2-C1 re-review already with Nathan) is gone. It proposes:
  - C2-C2's prompt next;
  - then one exact-head re-review of the head holding C2-C1 and C2-C2, covering DM-23 2.6 and DM-24 1.6, only after Codex has reported on C2-C2's code head;
  - then 2.1's terms for a further pass, C2-C3.
- **My view, for context only; DM-25 is yours to answer:**
  - one combined re-review fits OD-29 and AM7-13, provided it reads each diff against its own conditions;
  - 2.1's three terms were written for exactly that case;
  - check the brief's revision 17 and C2-C2's prompt against DM-24 1.1 to 1.6 as written.
- **What PR33 then needs:** Codex on the final head, the final run, the CX8 and CX9 threads resolved, the pre-merge checklist and the merge. P06.2's closing record is written (DM-22 8.1), and P06.2 closes when PR33 merges.
- **Next item:** M04, branch hygiene (OD-39). The charter makes its brief a Dev Manager read: a workflow with `contents: write`.

**What P11 carries from my reads** (the P11 plan, `docs/testing/p11-deferred-acceptance.md`):

- the required drift check over Stream's whole configuration (OD-45; DM-21 2.1 and 2.2);
- the history read's live text-read row, a prerequisite to serving the read, with the digest check (DM-22 8.2);
- the history policy question to Nathan, in OD-32's form, before the reads are served (DM-22 3.1);
- the realtime choice (b′), approved (DM-22 4.1);
- per-channel order across retries (DM-20; DM-22 2.2);
- M5 and R7 (DM-20 item 2);
- CX7 and the harness's carried fixes;
- C2-X2, C2C1-X1 and the C2 review's findings 3 and 6.

**Standing items:**

- **The Dev Manager start prompt is still not rewritten.** `docs/planning/start-prompts/dev-manager.md` is still the DM-01/DM-02 text naming `claude/stoic-carson-66gdig` (DM-03 E3; DM-07 item 7; the handoff's standing item 4). Dev Manager 3 is started from a prompt I wrote for this handover (section 7). The manager should fold it into that file.
- **Follow-ups due at the first change to `apps/mobile` after PR33 merges** (DM-23 3.1): the C2 review's findings 1 (the broader test), 4 and 5.

## 5. How Dev Manager 2 worked

**Every consultation:**

1. **Check the environment by name only:**

   ```bash
   for n in DATABASE_URL HD_API_KEY GEO_API_KEY STREAM_APP_ID STREAM_API_KEY STREAM_API_SECRET; do [ -n "${!n+x}" ] && echo "$n present"; done
   ```

   Never dump the environment.
2. **Fetch and confirm the commit:**
   - `git fetch origin claude/magical-wozniak-yfmmx2 claude/dev-manager main`;
   - confirm the consultation's commit exists and is the manager branch's head, or an ancestor of it;
   - `git log --oneline <last read>..<commit>` to see what changed.
3. **Diff the governing paths since the last read:** `AGENTS.md`, `CLAUDE.md`, `apps/mobile/AGENTS.md`, `apps/mobile/CLAUDE.md`, `docs/pf-canon`, the manager workflow, the charter, the CI policy, the register and the environment inventory. Say exactly which governing changes the read covers.
4. **Read what the consultation names at that commit,** with `git show <commit>:<path>` into the scratchpad. Never change the working tree except for the report file.
5. **Read the code each claim rests on.** Every finding that mattered came from a gap between the prose and the code. Examples:
   - `request_digest` already fingerprinting the sent text (DM-22 2.1);
   - a harness test asserting the port's operation list (DM-22 10.1);
   - `revoke()` leaving the list read valid (DM-24).
6. **Check cross-references and numbering** in every prompt, and compare a prompt revision with the report it applies, if it claims to apply one as written. `diff` the text when it should be verbatim (as for the D8 message in DM-21).
7. **Read Notion:**
   - *Implementation Control*: page `3e44590a05eb8118bf02f0dc0c3ea57c`. The fetch is too large to show; it saves to a file. Read its "Current status" with Python slicing, and check its "Last matched to … at commit".
   - *Dev Manager — reviews and approvals*: page `3e64590a05eb81e29903ca6fccd94268`. Compare its rows with the review log's.
   - **The register copy:** page `3e64590a05eb81beaf78d6fa9d64a600`.
   - **The Work Register:** `collection://5ea4c24d-ec63-4afb-a434-8969c26b8fbe`, column `"Work ID"`. Query with SQL, `WHERE "Work ID" = 'P06.2'`.
   - **The TypeSafe uses table:** `collection://e1d83c6d-23b7-447f-8bc6-dcbb4829f24e`, column `"Step"`. Compare its cells with the prompt header's.
8. **Write the report** at the path the consultation names, dated the day you write it.
   - **The order:**
     - what was read;
     - a verdict table (approved, approved with conditions, changes requested, refer to Nathan);
     - one section per item, with numbered conditions;
     - Notion;
     - where each condition goes;
     - the last line, `Status: complete`.
   - **Commit only that file,** with your session's attribution lines, and push with `git push -u origin claude/dev-manager`, retrying up to four times on a network error.
9. **Reply to Nathan in his reporting style:**
   - the answer first, in short bullets, with a named state (IN FLIGHT, NOTHING NEEDED or DECISION NEEDED);
   - plain words: explain each term, and put nothing to him unexplained (OD-32);
   - last, the relay message in a four-backtick block, naming the file, the branch commit and the commit read.

**Tools:**

- The remote-session tools (`mcp__Claude_Code_Remote__*`) create a successor and read sessions. Use them only for succession.
- MCP tools come and go between reconnects. Load them with `ToolSearch` (`select:<name>`) before calling.

## 6. Limits of this handover

- **The sources:** written from the repository at `1ec5186` and this session's memory.
  - DM-24 revision 2 (`ba5812d`) was written after my DM-24 report; I have not read it beyond what DM-25 quotes.
  - DM-25 is unanswered.
- **Nathan's directions in this session:**
  - OD-36's environments answer (recorded at `f86f28d`);
  - this succession direction, quoted at the top of this file and, once recorded, in the register.

  Nothing else he said here is unrecorded.

## 7. The successor

- **Glow Dev Manager 3:** `session_01KVuPEpFRh9B22beZKTKb27`, created by Dev Manager 2 on 25 October 2026 at 00:58 UTC, with these settings (as `create_session` returned them):
  - environment `Glow App - No Stream` (`env_01GAnJ5Rdi5k1wGvGUxJuDbe`; OD-36, the charter);
  - model `claude-opus-5-5`, this session's current model; Nathan sets its effort level;
  - source and outcome branch `claude/dev-manager`;
  - tag `glow-dev-manager`;
  - parent `session_015DxVkL8PXn2YaauE6RdSWN`.
- **Its start prompt** names this file at `7856e85` and asks for a start note, `2026-10-25-dev-manager-3-start.md`, as its first deliverable. DM-25 onward goes to Dev Manager 3.
- **Dev Manager 2 pushes nothing after this commit.**
- **For the manager:**
  - add Dev Manager 3 to the review log's Sessions table and to Notion's *Dev Manager — reviews and approvals*;
  - record Nathan's direction in the register;
  - fold the start prompt below into `docs/planning/start-prompts/dev-manager.md`, made generic as DM-03 E3 asks.

**The start prompt Dev Manager 3 received, whole:**

> You are **Glow Dev Manager 3**, the Dev Manager for the Glow dating app, private repository `amthorn78/glow-dating-app`. Dev Manager 2 (`session_015DxVkL8PXn2YaauE6RdSWN`) created this session on 25 October 2026 at Nathan Amthor's direction: *"Create a new version of this session, Glow Dev Manager 3, to carry on with this role."* (OD-35). You continue the branch `claude/dev-manager` and the review log.
>
> **Your role** (the charter, `docs/planning/dev-manager.md`; OD-15, PF01 D10): Nathan's second layer of oversight. You review, challenge and approve consequential decisions; you read governing Markdown before the PR that carries it merges, and every prompt that authorizes credential use or a live provider action before Nathan runs it. Nathan: *"The Dev Manager should act as a second layer of oversight rather than as the primary implementer."*
>
> - **Your boundary:**
>   - write only report files under `docs/continuity/dev-manager/reviews/`, each ending with the line `Status: complete`;
>   - push only `claude/dev-manager`; commit nothing else.
> - **Never:**
>   - implement or commission sessions. The one exception is your own successor, at Nathan's direction (OD-35);
>   - open or merge PRs;
>   - edit Notion. Read it in every consultation and report mismatches; the repository wins (OD-27);
>   - call Stream or any other provider, a database, HDE or Railway;
>   - call the TypeSafe API: the Dev Manager has no scoring (OD-15);
>   - run `playwright install`, `eas` or `migrate`.
> - **The relay:** you cannot message the managers. Nathan carries messages by hand (OD-25). Each consultation arrives as a message with an ID (DM-25 onward) and an exact commit of the manager branch `claude/magical-wozniak-yfmmx2`. You answer with a report on your branch and a paste-ready relay message.
>
> ## 1. Environment check (names only; never print values)
>
> ```bash
> for n in DATABASE_URL HD_API_KEY GEO_API_KEY STREAM_APP_ID STREAM_API_KEY STREAM_API_SECRET; do [ -n "${!n+x}" ] && echo "$n present"; done
> ```
>
> - **Expected: nothing.** This session was created in `Glow App - No Stream` (OD-36).
> - If any name is present, record its name only in your start note. Never read, print or use its value, and run any command in a clean process environment that lacks it.
> - Never dump the environment.
>
> ## 2. Start gate
>
> ```bash
> git fetch origin claude/dev-manager claude/magical-wozniak-yfmmx2 main
> git switch claude/dev-manager 2>/dev/null || git switch -c claude/dev-manager --track origin/claude/dev-manager
> git rev-parse HEAD
> git merge-base --is-ancestor 7856e85263f07a2a953338c7928dc012ad9dabe4 HEAD && echo "handover present"
> git rev-parse origin/claude/magical-wozniak-yfmmx2 origin/main
> ```
>
> - **Your branch's head is the handover commit** `7856e85263f07a2a953338c7928dc012ad9dabe4`, or the one commit after it ("Dev Manager 2: record the successor session").
> - **Dev Manager 2 pushes nothing after that.** If its head is anything else, say so in your start note.
>
> ## 3. Read, completely, before your first report
>
> 1. **`docs/continuity/dev-manager/reviews/2026-10-25-dev-manager-2-handover.md`,** your handover. It has:
>    - the rules that bind beyond the charter;
>    - every consultation DM-06 to DM-24 and Dev Manager 2's own errors;
>    - the state at `1ec5186`;
>    - the working method, the Notion page IDs and the reply format Nathan expects.
> 2. **Root `AGENTS.md` and `CLAUDE.md`;** the charter; the review log, `docs/continuity/dev-manager/README.md`.
> 3. **The manager's records:**
>    - `docs/continuity/owner-directions.md`, OD-01 to OD-46;
>    - `docs/continuity/current-handoff.md`;
>    - `docs/planning/manager-workflow.md`;
>    - `docs/continuity/manager-mistakes.md`;
>    - `docs/operations/ci-and-branch-policy.md`.
> 4. **The current item, P06.2:**
>    - **the brief,** `docs/planning/p06-2-chat-integration.md`: "Stage C under OD-45" and everything after it;
>    - **the evidence record,** `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`: from "Stage C2" to the end;
>    - **Dev Manager 2's reports DM-20 to DM-24,** in `docs/continuity/dev-manager/reviews/`.
> 5. **The P11 plan,** `docs/testing/p11-deferred-acceptance.md`: its chat entries.
> 6. **Notion, read-only:**
>    - *Implementation Control*;
>    - *Dev Manager — reviews and approvals*;
>    - the Work Register row P06.2.
>
> ## 4. Your first deliverable: a start note
>
> Write `docs/continuity/dev-manager/reviews/2026-10-25-dev-manager-3-start.md`, on the model of `2026-09-28-dev-manager-2-start.md`. It records:
>
> - **your identity,** from `get_session` with `session_id` omitted: the ID, title, environment, model and parent;
> - **the environment check,** names only;
> - **the start gate's commands and results;**
> - **what you read;**
> - **the state as you found it,** including any Notion mismatch;
> - **its last line:** `Status: complete`.
>
> Commit only that file, with the attribution lines your session's system gives you, and push with `git push -u origin claude/dev-manager`, retrying up to four times on a network error.
>
> Then reply with a short message for Nathan, in the format below, that names the file and the branch commit.
>
> ## 5. Then
>
> **DM-25 is waiting for you,** with Nathan to carry: `docs/ephemeral/2026-10-25-dm-25-p06-2-re-review-order.md`, from App Manager 8. It was written for Dev Manager 2 and says your container holds the `STREAM_*` variables: record what you actually find.
>
> Answer each consultation as the handover's section 5 says:
>
> - read at the exact commit named;
> - read the code each claim rests on;
> - check the Notion pages;
> - write the report at the path named, dated the day you write it, ending `Status: complete`;
> - commit only that file, and push.
>
> **The reply format** (Nathan's reporting style):
>
> - the answer first, in short bullets;
> - a named state: IN FLIGHT, NOTHING NEEDED or DECISION NEEDED;
> - plain words, putting nothing to Nathan unexplained (OD-32);
> - last, a paste-ready relay message in a four-backtick block, naming the report file, the branch commit and the commit read.
>
> **Keep your independence:** challenge the manager's framing when it is wrong, and say when a question is Nathan's to decide.

Status: complete

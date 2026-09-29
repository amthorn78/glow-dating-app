# DM-01 — Process review

- **Consultation:** DM-01, requested by Nathan through App Manager 3 on 25 September 2026.
- **Reviewer:** Dev Manager 1, session branch `claude/dev-manager`.
- **Commit reviewed:** `3888e8f635c4efdaf31cf074e1e423ff5f98de29`, verified as an ancestor of the manager branch `claude/stoic-carson-66gdig`. The manager branch later gained `68b4ab9`, which changes only the review log and one handoff line to record this session. I read it and it does not affect this review.
- **Companion report:** [DM-02 build review](2026-09-25-dm-02-build-review.md).

## 1. What I read and ran

**Read completely:**

- the instructions: root `AGENTS.md` and `CLAUDE.md`, and `apps/mobile/AGENTS.md`;
- the charter and review log: `docs/planning/dev-manager.md` and `docs/continuity/dev-manager/README.md`;
- the status and handoffs: `docs/continuity/state-of-the-app.md`, `docs/continuity/current-handoff.md` and `docs/continuity/manager-mistakes.md`;
- the canon: PF00 (revision 1.7) and PF01 (revision 1.8);
- the process documents: `docs/README.md`, `docs/planning/manager-workflow.md` and `docs/operations/ci-and-branch-policy.md`;
- the current work item: the P06.1 brief and the P06.1 evidence record;
- all four prompts in `docs/ephemeral/` (the first 60 lines of the I1 implementation prompt; the rest completely) and `docs/ephemeral/README.md`;
- the CI setup: `.github/workflows/foundation.yml`, `scripts/change_scope.py` and `services/api/tests/test_toolchain_pins.py` (I checked whether any check reads Markdown);
- the status line of `docs/continuity/claude-code-handoff.md`.

**Git and GitHub, read-only:**

- `git log` from `0f45e64` to `3888e8f` (11 commits, with times);
- a count of how many files repeat the same facts;
- `docs/` file sizes;
- the open PRs: only draft PR26, whose head is `68b4ab9`;
- the last 15 Foundation workflow runs, through the GitHub integration.

**Commands I ran:**

| Command | Result |
|---|---|
| `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done` | Printed nothing: no HDE variables |
| `git rev-parse HEAD` (start) | `3888e8f635c4efdaf31cf074e1e423ff5f98de29` |
| `git merge-base --is-ancestor 3888e8f… origin/claude/stoic-carson-66gdig` | `basis is on the manager branch` |
| `git switch -c claude/dev-manager`, then `git rev-parse HEAD` | `3888e8f635c4efdaf31cf074e1e423ff5f98de29` |
| `for s in S15 9ff600f ultracode "19 of 20" "one work item at a time"; do grep -rlE … docs AGENTS.md CLAUDE.md \| wc -l; done` | S15 in 8 files; `9ff600f` in 5; ultracode in 6; "19 of 20" in 3; the one-work-item rule in 6 |
| `git log --format='%h %ad %s' 0f45e64..3888e8f` | 5 I1 commits (03:11–03:39 UTC), then 6 manager record commits (08:01–08:57 UTC) |
| GitHub `list_workflow_runs` (15 most recent) | Pull-request runs 181, 183, 185 and 187 were **cancelled** by the next record commit. Run 191 on `3888e8f` was also cancelled, by `68b4ab9`. Each followed a Markdown-only commit, but the pull-request comparison includes the harness, so each was a full run (see finding P2) |

The offline test runs are listed in DM-02. I did not read Notion (see Limits).

## 2. Summary verdict

The process is disciplined and unusually traceable. Evidence names exact heads, claim levels are honest, the classifier fails closed, and mistakes are logged without softening.

Its main weaknesses come from one operational viewpoint doing too much:

- the manager writes, integrates and is the only reader of the governing Markdown that steers every session;
- manager record commits ride on the code PR, so they move review heads and re-run full CI;
- the same fact is maintained in up to eight places, which drives most of the logged mistakes.

**I approve the Dev Manager design, with conditions.** I recommend slimming the records and routing the manager's records around the code PR before P06.1-I2 is written.

## 3. Findings

### P1 — Governing Markdown has no second reader — *before the next implementation task*

- **Evidence:**
  - Under the 24 September exemption, `AGENTS.md`, `CLAUDE.md`, the PF canon, the manager workflow, the CI policy and every prompt skip review (`docs/operations/ci-and-branch-policy.md`, "Documentation is exempt"). The only control is that "the manager reads documentation changes when it integrates them" (`docs/README.md`). Those are mostly the manager's own changes.
  - Commit `3888e8f` changed `AGENTS.md`, `CLAUDE.md`, PF00, PF01, the manager workflow and two prompts in one self-integrated commit.
  - Prompts carry executable, credential-bearing instructions. The I1 review prompt, section 4, authorizes live runs against Stream with `STREAM_API_SECRET`. Commit `9819939` changed that prompt after its review head had been named.
  - The classifier cannot tell a prompt from a note, by design (`scripts/change_scope.py`, `ordinary_document`).
- **Risk:** one session can change the rules that bind every other session, including the rules on credentials and live provider actions, and no independent reader sees the change before it takes effect. The mistakes log shows that the manager's own prompts do carry errors (AM2-01, AM2-02, AM2-04, AM2-09).
- **Recommendation:** keep Nathan's exemption for CI and code review. Add a lightweight second read, which the charter already implies ("changes to process and governance … before they are treated as settled"). Make it concrete:
  - **(a)** Changes to `AGENTS.md` or `CLAUDE.md` at any level, to `docs/pf-canon/`, to the manager workflow, the charter or the CI policy go to the Dev Manager. Batch them per PR. The PR merges only after the review log records a disposition.
  - **(b)** Any prompt that authorizes credential use or live provider actions gets a Dev Manager read before Nathan runs it. This covers the P06.1-I2 prompt.
  - **(c)** Close-out step 7 of the workflow checks (a).
- **Documents:** `docs/planning/manager-workflow.md` (steps 3 and 7), `docs/planning/dev-manager.md` (triggers), `docs/operations/ci-and-branch-policy.md` (one sentence).

### P2 — Manager record commits ride on the code PR — *before the next implementation task*

- **Evidence:**
  - After I1's code head `9ff600f` (03:39), App Manager 3 pushed six Markdown-only commits to PR26's head branch (08:01–08:57). Each pull-request run compares the whole PR, which includes `proofs/stream-chat/**`, so each started a full run of about 6 to 11 minutes.
  - Runs 181, 183, 185, 187 and 191 were cancelled by the next commit.
  - The review head was set to `c0a34f8`, a record commit, not the code head.
  - The review prompt changed afterwards (`9819939`), so the text Nathan pastes is not the text at the review head.
  - Every future Dev Manager report merged "into the manager branch" (charter, relay step 3) will do the same.
- **Risk:**
  - CI minutes are wasted, and the push-run cancellation hazard recorded in the workflow grows.
  - Review heads no longer mean "the code under review".
  - Traceability suffers: which prompt revision did the reviewer receive?
  - The manager's time goes into re-reading green runs instead of the work.
- **Recommendation:**
  - While a code PR is under review, keep manager records off its head branch.
    - Use a separate records branch and PR, which classifies as ordinary documentation and merges without application CI.
    - Or batch the records into one commit at close-out.
  - The code PR carries only implementer commits, the evidence record and corrections.
  - Review prompts name the code head, and the review report records the commit of the prompt text actually pasted.
  - Dev Manager reports integrate through the records route, not PR26.
- **Documents:** the manager workflow ("Verify and integrate" and "Branches and pushes"), the charter (relay step 3), the current handoff.

### P3 — One fact is kept in many places — *soon*

- **Evidence:**
  - S15 appears in 8 files. I1's head appears in 5. The reasoning-level table is in the handoff, the brief, the State of the App and Notion.
  - The current handoff is 16 KB and mostly history: M02 details, the Setup-script paste, branch lists and the reasoning table.
  - The Claude handoff (40 KB) keeps a "status line current".
  - PF01's header "Current direction" and PF00's "Current session authority" restate status. PF01 went through revisions 1.4–1.8 and PF00 through 1.3–1.7 within about two days, mostly to record status.
  - State of the App 3.3 lists up to ten homes per event. Implementation Control is about 100,000 characters (recorded, not checked).
  - Of the 15 logged mistakes, 7 are record or tool slips in keeping these copies (AM2-04, AM2-05, AM2-07, AM2-11, AM3-01, AM3-02, AM3-04).
- **Risk:** R06 (duplicate authority and misleading progress). Every copy is a place to go stale. Record upkeep takes the manager's capacity away from verification, the one thing only the manager does.
- **Recommendation:** one home per kind of fact, with links elsewhere.

  | Fact | Single home | Stop keeping it in |
  |---|---|---|
  | Work-item results, decisions, open questions and levels | The brief and its evidence record | Handoff, State of the App, Claude handoff |
  | Routing: current item, its state in at most 10 lines, next actions, who is waiting on whom | The current handoff (target: under 5 KB) | — (move the history to `docs/continuity/history/`) |
  | Governing rules and decisions | PF01 §10 and the charter | PF01 and PF00 status lines (replace each with one pointer to the handoff; revise the canon only when a rule changes) |
  | Owner directions (dated quotes) | **New:** one append-only register, for example `docs/continuity/owner-directions.md`, with an ID (OD-nn), date, quote and the home it governs | Scattered tables (State of the App 1.5, the handoff's policy bullets) |
  | Live task state | The Notion Work Register row, holding state plus a link | Implementation Control's history (trim it to the status block and links) |
  | Periodic snapshot | State of the App, refreshed only for a review | — (do not maintain it between reviews) |
  | Historical packet | The Claude handoff, frozen | Its status line (replace with a pointer) |

  **What is missing:**

  - **(i)** The owner-direction register above. Today no single list holds Nathan's standing directions: the documentation exemption, one item at a time, the $0 budget, the S15 principle.
  - **(ii)** An ADR for the S15 display rule. It will constrain P06.2's code, and a brief is not a durable home once P06.1 closes.
  - **(iii)** A small index from PR to work item, evidence record and receipt.
- **Documents:** the current handoff, PF00, PF01 (header only), the Claude handoff, `docs/README.md` (the homes table), the manager workflow (step 7), a new register and a new ADR 0003.

### P4 — Design decisions are taken on unreviewed evidence — *before the next implementation task*

- **Evidence:** Nathan decided S15 on I1's own evidence, before the exact-head review that "may confirm S15" (review prompt, section 4, optional) had run. The brief records the decision as settled ("S15: decided"). The manager cannot verify live claims itself (State of the App 3.4).
- **Risk:** if the review finds a configuration that closes S15, or finds the finding misattributed, a recorded owner decision, a PF01 §7 amendment and I2's scope all rest on a wrong premise. More generally, when a design decision rests on live evidence, nobody independent has observed that evidence.
- **Recommendation:**
  - Record S15's decision as conditional on the review confirming the finding. If the review narrows or closes S15, it returns to Nathan.
  - Add a workflow rule: when a design decision rests on a live finding, the exact-head review's live confirmation of that finding is required, not optional.
- **Documents:** the P06.1 brief ("S15: decided"), the manager workflow (step 6), the I1 review prompt (section 4 wording, if not yet run).

### P5 — The one-item rule and the known flake — *soon (Nathan decides)*

- **Evidence:**
  - The rule: no new item until the current item's CI and review are clear (manager workflow).
  - The intermittent rendered failure (three occurrences) is filed as a follow-up that Nathan schedules only after P06.1 is clear (handoff, "Recorded follow-ups").
  - The manager cannot re-run jobs (403), so each flake costs Nathan a round trip.
- **Risk:** a known intermittent failure blocks the gate that the one-item rule depends on, while its fix is held behind that same gate. Each occurrence needs Nathan by hand.
- **Recommendation:** Nathan decides whether a failure that can turn the current item's CI red is part of the current item, as corrections are. If so, the flake diagnosis may run inside P06.1 without breaking the rule.
- **Documents:** the manager workflow ("One work item at a time"), the handoff.

### P6 — The relay's continuity and its bottleneck — *soon*

- **Evidence:**
  - Every session is started and relayed by Nathan. Managers are reinitiated by hand, and long sessions compact their context (State of the App 1.7).
  - The Dev Manager adds a hop: manager → Dev Manager → repository → manager → Nathan.
  - 24 PRs in three days, "often one per step" (State of the App 3.4).
  - The start prompt's required reading is about 2,400 lines before the Claude handoff.
- **Risk:**
  - Continuity depends on the manager's written records being complete at the moment of compaction or handover.
  - Nathan's time is the throughput limit, and each extra PR costs him attention.
  - A long reading list invites skimming, which is how AM2-09-type omissions happen.
- **Recommendation**, within Nathan's model:
  - **(a)** One documentation PR per work-item phase, not per step. P2's records branch gives this naturally.
  - **(b)** Keep P3's slim handoff, which shortens the start reading to the handoff, the charter, PF01 §7–§10 and the current brief.
  - **(c)** The manager writes a checkpoint in the handoff before any long operation: what it is waiting for and from whom. Compaction then loses nothing.
  - **(d)** Each relay prompt names the exact file and heading where the result should be recorded. The next manager then finds it without reconstruction.
- **Documents:** the manager workflow, the next-manager start prompt.

### P7 — The review paths: gaps and overlaps — *soon*

- **Evidence:**
  - The paths are an exact-head review session, Codex on "ready", the documentation exemption and now the Dev Manager.
  - Codex and the exact-head review overlap on code. That is acceptable defense in depth.
  - Gaps:
    - **Behavior-affecting Markdown:** see P1.
    - **Live behavior:** see P4.
    - **Merge enforcement is procedural only.** Branch protection cannot be enforced on this private personal repository (CI policy), and AM2-06 shows a merge before Codex finished.
    - **Proof-tooling tests are outside CI** (DM-02, B6).
- **Risk:** a single slip by the manager (merging early or on a red run) has no platform stop.
- **Recommendation:**
  - Close P1 and P4 as above.
  - Add a pre-merge checklist line to the PR description, which the manager fills in with run IDs: gate "Application checks passed" on the exact head; the review report ID for that head; Codex's summary present; Dev Manager dispositions recorded where required.
  - Nathan may decide whether enforceable protection (a GitHub Team organization) is worth its cost (Questions).
- **Documents:** the manager workflow (step 7), the CI policy.

### P8 — The mistakes log and the TypeSafe scorer — *consider*

- **Mistakes log. It earns part of its cost.**
  - **Evidence:** 15 entries. The process entries (AM2-06, AM2-08, AM2-10) taught real lessons, and their preventions were written into the workflow. Several entries are tool retries with no effect, caught by the tool itself (AM2-03, AM3-01, AM3-03). AM3-04 repeats AM2-11, so a prevention line alone did not prevent the repeat.
  - **Recommendation:**
    - Keep the log, as Nathan directed.
    - Limit full entries to mistakes that reached a record, a prompt, Nathan or `main`. Keep no-effect tool retries as one summary row.
    - When a prevention recurs, move it into a checklist the manager actually runs (the workflow or the start prompt), and note that in the entry.
- **TypeSafe reasoning-level scorer. It does not currently earn its cost.**
  - **Evidence:**
    - 5 of 10 planned outcomes are in. Every one is "adequate", and Nathan ran extra high every time.
    - It gates nothing (workflow step 3).
    - It generated AM2-05 and AM3-02. AM3-02 was a follow-through mistake that existed only because of the scorer commitment, and it produced an extra commit that became the review head.
    - Its readings are repeated in the handoff, the brief, the State of the App and Notion.
  - **Recommendation:**
    - Finish the pre-registered 10-session comparison, since it is half done and the rule was fixed in advance.
    - Keep its data only in its Notion log. Remove it from the handoff, the brief and the State of the App.
    - Then Nathan decides whether to keep or retire it.
    - Stop making conditional level commitments ("ultracode if flagged"). They create follow-through obligations with no gate behind them.
- **Documents:** the mistakes log (header rules), the manager workflow (step 3), the handoff, the brief.

### P9 — Durable prompts live in the ephemeral folder — *consider*

- **Evidence:** `docs/ephemeral/README.md` says the folder is for "single-use" prompts. But the next-manager start prompt ("each manager keeps this prompt current") and the Dev Manager start prompt ("kept current for later sessions", charter records table) are durable procedures.
- **Risk:** a routine prune of ephemeral prompts at close-out (workflow step 7) could delete the only start procedure.
- **Recommendation:** move both start prompts to `docs/planning/start-prompts/` (or say explicitly in the ephemeral README that they are exempt from pruning).
- **Documents:** `docs/ephemeral/README.md`, `docs/README.md`, the charter's records table, the handoff links.

### P10 — The relay's fidelity to Nathan — *soon*

- **Evidence:**
  - Under the charter, the primary manager frames each consultation, chooses what the Dev Manager reads, records the dispositions and relays the conclusions to Nathan.
  - Only disagreements are guaranteed to reach Nathan with both views.
- **Risk:** the second viewpoint reaches the owner only through the first viewpoint's paraphrase, which undercuts Nathan's purpose ("not … made from only one operational viewpoint").
- **Recommendation:**
  - The manager gives Nathan each report's path and its verdict list as written.
  - Any item it declines, or accepts with changes, goes to Nathan with the Dev Manager's own text next to the manager's reason.
  - Nathan can always read `docs/continuity/dev-manager/reviews/` directly.
- **Documents:** the charter (relay step 4), the review log header.

## 4. Approval items

| # | Item | Verdict | Reasons and conditions |
|---|---|---|---|
| 1 | Record-keeping load | **changes requested** | Adopt P3's one-home table; add the owner-direction register and the S15 ADR; freeze the Claude handoff's status line; stop status-only canon revisions. Traceability is kept, because every removed copy becomes a link to its single home |
| 2 | The manual relay | **approved with conditions** | The model is sound and Nathan's to set. Conditions: P2 (records off the code PR), P6 (a) and (c) (batched documentation PRs, checkpoints before long waits), and Nathan's answer on P5 |
| 3 | Review and approval paths | **approved with conditions** | Keep exact-head review, Codex and the documentation exemption. Conditions: P1 (a Dev Manager read for governing Markdown and for credential-bearing prompts), P4 (required live confirmation when a decision rests on a live finding), P7 (a pre-merge checklist in the PR) |
| 4 | Dev Manager charter and relay: `dev-manager.md`, the workflow lines, `CLAUDE.md`, `AGENTS.md`, PF01 D10, PF00 1.7 | **approved with conditions** | See below |
| 5 | Handoffs: start prompts, the current handoff, review heads, pruning | **changes requested** | Slim the handoff (P3). Review heads name the code head, and the record keeps the prompt revision actually pasted (P2). Move the durable start prompts out of `ephemeral/` (P9). Pruning after promotion is sound as written |
| 6 | Mistakes log and TypeSafe scorer | **approved with conditions** (mistakes log); **refer to Nathan** (scorer) | Mistakes log: keep it, with P8's narrower entry rule and checklist promotion. Scorer: finish the pre-registered 10 sessions, confine its records to Notion, then Nathan decides whether to keep it |

**Item 4, the charter, in detail.**

- **What I approve:**
  - the role split (the Dev Manager never implements, and Nathan settles disagreements);
  - the triggers list;
  - the four verdicts;
  - the report-through-the-repository relay with `Status: complete`;
  - the review log as the continuity record;
  - "not for routine verification or exact-head code review";
  - the rule that a consequential decision waits for the answer unless Nathan directs otherwise.
- **Conditions:**
  1. Add the P1 triggers: governing Markdown at merge, and credential-bearing or live-action prompts before they run.
  2. Relay step 3 integrates reports through the records route, not the code PR (P2).
  3. Relay step 4 applies P10's fidelity rule.
  4. **Continuity:** the manager fetches `claude/dev-manager` when it expects a report. A consultation says what the manager will do if no report arrives, for example proceed after Nathan's go-ahead. The Dev Manager's branch only ever adds files under `reviews/`, so merging it is always conflict-free.
  5. **State plainly** that a Dev Manager `approved` is neither an owner decision nor an exact-head review. It is in the spirit of the charter but not stated as a rule.
  6. **Environment:** the Dev Manager does not need the Stream variables. See DM-02, B8, on a separate environment.

## 5. Questions for Nathan

1. **P5:** is a known intermittent CI failure that can turn the current item red part of the current item, so that it can be diagnosed now without breaking the one-item rule?
2. **P1:** do you accept a Dev Manager read, not a code review, of governing Markdown and of credential-bearing prompts before they take effect? It does not change your documentation exemption from CI.
3. **P8:** after the pre-registered 10-session comparison, keep or retire the TypeSafe reasoning-level scorer?
4. **P7:** is enforceable branch protection worth a paid GitHub organization plan for this repository, or is the procedural gate with a pre-merge checklist enough?

## 6. Documentation to update

- `docs/planning/manager-workflow.md`:
  - steps 3, 5, 6 and 7 (P1, P2, P4, P7);
  - the one-item rule (P5, after Nathan answers);
  - step 3's scorer lines (P8).
- `docs/planning/dev-manager.md`:
  - the triggers (P1), relay steps 3 and 4 (P2, P10);
  - continuity and the meaning of approval (item 4, conditions 4 and 5);
  - the records table (P9).
- `docs/continuity/current-handoff.md`: slim it to routing, and move the history out (P3).
- `docs/continuity/claude-code-handoff.md`: replace the status line with a pointer (P3).
- PF01 header and PF00 "Current session authority": replace the status with pointers. Record in each revision history that status no longer lives in the canon (P3).
- New files:
  - `docs/continuity/owner-directions.md` (P3);
  - `docs/adr/0003-chat-display-rule.md` (P3, and DM-02).
- `docs/README.md`: the homes table (P3, P9). `docs/ephemeral/README.md` (P9).
- `docs/continuity/manager-mistakes.md`: the header's entry rule (P8).
- `docs/planning/p06-1-chat-provider-proof.md`: mark the S15 decision conditional on the review (P4).
- `docs/operations/ci-and-branch-policy.md`: one sentence on the governing-Markdown read (P1).

## 7. Limits

- I did not read Notion (Implementation Control, the Work Register, the TypeSafe usage log). Claims about Notion's size and contents are recorded, not verified.
- I did not read `docs/continuity/claude-code-handoff.md` in full, the M02 brief, or the history files, beyond the lines cited.
- I read the process as the records describe it. I did not observe a relay cycle.
- The CI-run observations cover the 15 most recent runs only.
- This review assesses process, not code. The code and build condition are in DM-02.

Status: complete

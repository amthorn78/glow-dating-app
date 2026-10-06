# Dev Manager review log

This is the index of every consultation with the Dev Manager, its verdicts and the primary manager's dispositions. The role, the relay and the triggers are in the [Dev Manager charter](../../planning/dev-manager.md).

- The Dev Manager writes its reports in [`reviews/`](reviews/) and changes nothing else.
- The primary manager keeps this log. It records each consultation when it is sent, and each disposition when the report is integrated.
- Nathan decides wherever the two managers disagree, and his decision is recorded here.

## Sessions

| Session | Created | By | Branch | Basis commit | State |
|---|---|---|---|---|---|
| Dev Manager 1, `session_01MrcrmqtuENZ345mKfmsSWv` ("Glow Dev Manager") | 25 September 2026, 09:00 UTC | App Manager 3, at Nathan's direction | `claude/dev-manager` | `3888e8f635c4efdaf31cf074e1e423ff5f98de29` | DM-01 and DM-02 answered at 09:09 UTC (`0f55891`); DM-03 answered at 09:36 UTC (`23951c4`); Nathan's answers and directions recorded (`574ee0e` to `d945478`); DM-04 answered at 17:21 UTC on 26 September (`51deb3d`), integrated at `d0c7ffd`; DM-05 given to Nathan to carry on 27 September; he sent it the same day, and the session ran it on Fable 5.1 at extra high; answered at about 01:40 UTC (`a80d81d`), read from the branch by App Manager 4 (OD-31) and integrated at its first records batch. DM-06 given to Nathan to carry on 28 September, from App Manager 5. Its container, started before OD-28, holds the three `STREAM_*` variables; it never reads or uses them (DM-04 finding 10, AM3-19). **Handed over** on 28 September at Nathan's direction: [handover](reviews/2026-09-28-dev-manager-1-handover.md) at `3ec0fac`, the successor recorded at `87b3c48`; it pushes nothing after `87b3c48` |
| Dev Manager 2, `session_015DxVkL8PXn2YaauE6RdSWN` ("Glow Dev Manager 2") | 28 September 2026, 16:16 UTC | Dev Manager 1, at Nathan's direction (the OD-31 pattern) | `claude/dev-manager` | `87b3c48c30aa8ed9388fa16d8ecad64609b76c8a`; manager branch read at `b729340` | [Start note](reviews/2026-09-28-dev-manager-2-start.md) at 16:25 UTC (`0773eaa`); DM-06, which Nathan carried to this session, answered at 17:19 UTC (`8ba418a`); both integrated at App Manager 5's merge `5704250`. DM-07, the close-out read, which Nathan carried to this session, answered at 00:57 UTC on 29 September (`a60d8c1`); Nathan's answer on the environments, given in this session, recorded at 01:14 UTC (`f86f28d`); both integrated at App Manager 5's merge `0704199`. DM-08, the P06.DB brief, which Nathan carried to this session, answered at 02:28 UTC on 29 September (`70f65f0`), integrated at App Manager 5's merge `145502e`. DM-09, PR28's governing read, which Nathan carried to this session, answered at 00:31 UTC on 5 October (`bc0306c`), integrated at App Manager 5's merge `c49175c`. DM-10, CX3 and the design of its correction, which Nathan carried to this session, answered at 01:50 UTC on 5 October (`9f2e79d`), integrated at App Manager 5's merge `2152463`. DM-11, the C2 prompt's departure from DM-10, which Nathan carried to this session, answered at 03:20 UTC on 5 October (`91c5c2c`), integrated at App Manager 5's merge `a9eae28`. DM-12, `dbshell` and condition 2.2, which Nathan carried to this session, answered on 5 October (`b06fe29`), integrated at App Manager 5's merge `8a94904`. DM-13, P06.2's brief and PR29's governing changes, from App Manager 6, which Nathan carried to this session, answered on 5 October (`80ce6c6`), integrated at App Manager 6's merge `589e595`; `claude/dev-manager`, deleted on GitHub on 5 October with the old branches (OD-39), was recreated by that push from its local branch at `b06fe29`. It runs in the `Glow app` environment; its container, started at 16:16 UTC on 28 September, holds the three `STREAM_*` variables, as OD-36 expects, and it never reads or uses them (start note, section 1) |

## Consultations

| ID | Sent | Requested by | Question | Report | Verdict | Disposition |
|---|---|---|---|---|---|---|
| DM-01 | 25 September 2026, 09:00 UTC, as the session's first prompt | Nathan, through App Manager 3 | **Process review:** how the project is managed and implemented | [DM-01 report](reviews/2026-09-25-dm-01-process-review.md) | Charter approved with conditions; record-keeping and handoffs: changes requested; relay, review paths and mistakes log approved with conditions; scorer referred to Nathan | Below |
| DM-02 | 25 September 2026, 09:00 UTC, as the session's first prompt | Nathan, through App Manager 3 | **Build review:** the state and direction of the application | [DM-02 report](reviews/2026-09-25-dm-02-build-review.md) | S15 reading approved with conditions; I2 scope: changes requested; database last, database placement and WordPress referred to Nathan; the rest approved with conditions | Below |
| DM-03 | 25 September 2026, 09:32 UTC, by a one-time Routine into the session | App Manager 3 | **Read before effect:** the governing Markdown in the batch at `fa4dc5f`, the DM-01 and DM-02 dispositions, and revision 2 of the P06.1-I1 review prompt | [DM-03 report](reviews/2026-09-25-dm-03-governing-read-and-i1-review-prompt.md) | Governing Markdown, the review prompt and the rest of the batch approved with conditions; the dispositions approved; no new questions for Nathan | Below |
| DM-04 | 26 September 2026, given to Nathan to carry (OD-25) | App Manager 3 | **Read before effect:** revision 1 of the P06.1-I2a implementation prompt, at `978ba19525f76c9aef9e326f973a739724ee3bb9` ([consultation](../../ephemeral/2026-09-26-dm-04-i2a-prompt-read.md)). It authorizes the Stream secret and live, destructive actions on the run's own data | [DM-04 report](reviews/2026-09-26-dm-04-i2a-prompt-read.md) | Approved with conditions: eight conditions for a revision 2 (findings 1 to 8), finding 9 optional; no questions for Nathan | Below |
| DM-05 | 27 September 2026, given to Nathan to carry (OD-25); he sent it the same day | App Manager 3 | **Read before effect:** revision 1 of the P06.1-I2b implementation prompt, written at `84715ec11eb5926e94f39d7e3369b1ebd515923b` ([consultation](../../ephemeral/2026-09-27-dm-05-i2b-prompt-read.md)). The consultation names the commit that adds this row, which holds the same prompt. It authorizes the Stream secret, live, destructive actions on the run's own data, user-token requests to Video and Feeds, a lasting lockdown of those two products, and a workflow change | [DM-05 report](reviews/2026-09-27-dm-05-i2b-prompt-read.md) | Approved with conditions: six conditions for a revision 2 (findings 1 to 6), finding 9 optional; items 2 and 4 option (a); no questions for Nathan | Below |
| DM-06 | 28 September 2026, given to Nathan to carry (OD-25); he carried it to Dev Manager 2 | App Manager 5 | **Read before effect:** revision 1 of the P06.1 economics discovery prompt ([consultation](../../ephemeral/2026-09-28-dm-06-economics-discovery-prompt-read.md)); the consultation names the commit that adds this row. It authorizes a Claude in Chrome session in Nathan's browser, signed in to the Stream dashboard: a read-only lookup of the plan, limits, usage, overage, region, attribution, the data-processing agreement and the Maker application, plus Stream's public pricing and terms | [DM-06 report](reviews/2026-09-28-dm-06-economics-discovery-prompt-read.md) | Approved with conditions; option (a), one session: three conditions for a revision 2 (findings 1 to 3), findings 4 and 5 (a) to (c) optional; Notion matches `b729340` apart from D10's two links; no questions for Nathan | Below |
| DM-07 | 28 September 2026, given to Nathan to carry to Dev Manager 2 (OD-25) | App Manager 5 | **Close-out read** ([consultation](../../ephemeral/2026-09-28-dm-07-p06-1-close-out-read.md)); the consultation names the commit that adds this row. The governing Markdown changed after `fa4dc5f` (seven files) and ADR 0003's update; the HDE contract request; ADR 0004's accepted restore risk; the live read and the open Video and Feeds items; the economics discovery's disposition; views on Nathan's three close-out decisions; the start prompt's text; Notion | [DM-07 report](reviews/2026-09-29-dm-07-p06-1-close-out-read.md); [Nathan's answer on the environments](reviews/2026-09-29-nathan-answer-environments.md) | Governing Markdown approved with conditions (findings 1.1 and 1.2), ADR 0003 approved; the HDE contract request approved and ADR 0004's restore risk confirmed, one *soon* item each; 4 (a) and 4 (b) option (i), neither Nathan's now; the economics disposition approved, one wording nit; item 6: agree on (a) and (b), (c) Nathan's, since answered (OD-36); Notion matches `89a8d01` apart from M03 and D10 | Below |
| DM-08 | 29 September 2026, given to Nathan to carry to Dev Manager 2 (OD-25) | App Manager 5 | **Brief read:** the P06.DB brief, revision 1 ([consultation](../../ephemeral/2026-09-29-dm-08-p06-db-brief-read.md)); the consultation names the commit it was sent at. The proof's isolation, its dependencies, the CI job, local runs, the transaction design and the proof's own honesty | [DM-08 report](reviews/2026-09-29-dm-08-p06-db-brief.md) | Approved with conditions: D1 approved; D2, D3 (1 to 4), D4 (1 to 4; within OD-17), D5 (5.1 to 5.6) and item 6 (6.1 to 6.3) approved with conditions; item 7 changes requested (7.1, the CI policy; 7.2, the review plan); Notion: a duplicate P06.DB row; no item is Nathan's | Below |
| DM-09 | 5 October 2026, given to Nathan to carry to Dev Manager 2 (OD-25) | App Manager 5 | **Governing read before PR28 merges** ([consultation](../../ephemeral/2026-10-05-dm-09-p06-db-governing-read.md)); the consultation names the commit it was sent at. The CI policy's and the manager workflow's changes in PR28, DM-07's carried items, and the dispositions of C1's exact-head review | [DM-09 report](reviews/2026-10-05-dm-09-p06-db-governing-read.md) | The CI policy and the manager workflow approved; DM-07's changes confirmed as applied and its three items as they stand; the dispositions of C1's exact-head review approved, with one *soon* wording change to DB09's mark and the guard carried to P06.2; Notion matched `ee25d1d`; nothing blocks PR28's merge, and no item is Nathan's | Considered by App Manager 5; every item accepted, the *consider* items included; nothing declined and nothing for Nathan. See "DM-09" below |
| DM-10 | 5 October 2026, given to Nathan to carry to Dev Manager 2 (OD-25) | App Manager 5 | **Design read before a correction** ([consultation](../../ephemeral/2026-10-05-dm-10-p06-db-cx3-design-read.md)); the consultation names the commit it was sent at. Codex's CX3 (a P1 in a correction class: the proof's host check accepts any database on loopback), the P06.DB brief's revision 3 (the run's marker in D1, D3 and D4), the dispositions of CX1 and CX2, and the CI policy's database sentence | [DM-10 report](reviews/2026-10-05-dm-10-p06-db-cx3-design-read.md) | CX3's classification and the correction before the merge approved; the run's marker approved with conditions 2.1 to 2.4 for the C2 prompt and 2.5 for C2's exact-head review; CX1 and CX2 approved as carried to P06.2; the CI policy: changes requested, narrowly (name the marker, in its words); Notion matched `cd9fa03`; no item is Nathan's | Considered by App Manager 5; every item accepted; nothing declined and nothing for Nathan. See "DM-10" below |
| DM-11 | 5 October 2026, given to Nathan to carry to Dev Manager 2 (OD-25) | App Manager 5 | **Read before a prompt runs** ([consultation](../../ephemeral/2026-10-05-dm-11-p06-db-c2-prompt-read.md)); the consultation names the commit it was sent at. The C2 prompt's one departure from DM-10's condition 2.3 (its query counts PostgreSQL's own `pg_toast` relations in a new database) and the rest of the prompt against DM-10 | [DM-11 report](reviews/2026-10-05-dm-11-p06-db-c2-prompt-read.md) | The departure approved with conditions, in words that replace its two bullets: a literal `pg_` prefix test, the query run in the proof's database, and each schema's count unchanged before and after the wrong-marker `migrate`; the rest of the prompt confirmed, with one note for C2's exact-head review; Notion matched `d50f334`; revision 1 does not run, and a revision 2 in these words needs no further read; no item is Nathan's | Considered by App Manager 5; every item accepted; nothing declined and nothing for Nathan. See "DM-11" below |
| DM-12 | 5 October 2026, given to Nathan to carry to Dev Manager 2 (OD-25) | App Manager 5 | **Read of a finding against a condition** ([consultation](../../ephemeral/2026-10-05-dm-12-p06-db-dbshell-read.md)); the consultation names the commit it was sent at. C2's exact-head review's F1 (Django's `dbshell` starts `psql` outside Django, so the marker is never checked for it) against DM-10's condition 2.2; its disposition (outside the correction classes, the README's rule, brief revision 6's note and an optional guard carried to P06.2); and the CI policy's sentence applied at C2's integration | [DM-12 report](reviews/2026-10-05-dm-12-p06-db-dbshell-read.md) | F1 approved as outside the correction classes, so no correction pass before the merge; the README's rule and the brief's note approved, with item 6 required before P06.2's first run of the suite on any database, in its words; the CI policy's sentence confirmed as DM-10 item 4 word for word; Notion matched `16c9450`; no item is Nathan's | Considered by App Manager 5; every item accepted; nothing declined and nothing for Nathan. See "DM-12" below |
| DM-13 | 5 October 2026, given to Nathan to carry to Dev Manager 2 (OD-25) | App Manager 6 | **Brief read and governing read** ([consultation](../../ephemeral/2026-10-05-dm-13-p06-2-brief-read.md)); the consultation names the commit it was sent at. P06.2's brief, revision 1: the three stages, the adapter and the suite's two subjects, the session-expiry rule (CX2), the send's extra checks, revocation and history, a new model and migration `0003`, and a challenge of what the client reads; the order of P06.DB's carried items; PR29's governing changes so far (the manager workflow's AM5-23 sentence and step 7's branch-state report); Notion. It also tells the Dev Manager that `claude/dev-manager` was deleted on 5 October (OD-39) and how to recreate it | [DM-13 report](reviews/2026-10-05-dm-13-p06-2-brief-read.md) | D1 approved; D2 and D3 approved with conditions 2.1 to 2.3; D4 confirmed; D5 approved with condition 4.1; D6 approved with condition 5.1; D7 approved; D8 not referred to Nathan, the recommendation standing with conditions 7.1 and 7.2 (option (a) recommended); the carried items' order confirmed; item 9 changes requested, narrowly (9.1 to 9.5); PR29's governing changes approved; Notion matched `a8db520` apart from Implementation Control's procedure stamp; no item is Nathan's | Considered by App Manager 6; every item accepted as written, 7.2 with option (a); nothing declined and nothing for Nathan. See "DM-13" below |
| DM-14 | 6 October 2026, given to Nathan to carry to Dev Manager 2 (OD-25) | App Manager 6 | **Governing read before Stage A merges** ([consultation](../../ephemeral/2026-10-06-dm-14-p06-2-stage-a-governing-read.md)); the consultation names the commit it was sent at. The manager workflow's two sentences after DM-13's read (step 3's OD-40 sentence, step 5's AM6-01 sentence); the dispositions of Stage A's exact-head review (F1, the token revocation's cut-off, with the mechanism for Stage B; F3, dead letters; the nits F2, F4, F5); Notion | [DM-14 report](reviews/2026-10-06-dm-14-p06-2-stage-a-governing-read.md) | Step 3's sentence approved, with a *consider* clause; step 5's approved with a condition (replacement words); F1's disposition approved, with a five-point mechanism for Stage B; F3 approved with a condition (a dead-lettered revocation marked for reconciliation); F2, F4, F5 approved; Stage A may merge once item 2 is applied, Codex's findings dispositioned, the final head's run passed and the checklist and branch-state report done; Notion matched `da9fac6`; no item is Nathan's | Considered by App Manager 6; every item accepted as written, the *consider* clause included; nothing declined and nothing for Nathan. See "DM-14" below |
| DM-15 | 6 October 2026, given to Nathan to carry to Dev Manager 2 (OD-25) | App Manager 6 | **Brief read** ([consultation](../../ephemeral/2026-10-06-dm-15-p06-2-stage-b-split-read.md)); the consultation names the commit it was sent at. P06.2 brief revision 3: Stage B split into B1, offline, and B2, live; B1's owned paths; B1's design points a to f for the carried items (provisioning before the channel, the reconciliation mark and its migration, the grant and the whole-second cut-off, activation's checks, the suite); Notion | [DM-15 report](reviews/2026-10-06-dm-15-p06-2-stage-b-split-read.md) | The split approved with conditions 1.1 to 1.3 (B1's prompt needs no read of its own; B2's comes to the Dev Manager); owned paths approved with 2.1 to 2.3; point a approved with 3.1 to 3.5 (a deterministic order key); point b approved with 4.1 to 4.5, amending `0003` allowed; points c and d confirmed, with 5.1 and 5.2 (`iat` truncated, strict next second); points e and f approved with 6.1 to 6.3; Notion matched `d12cc0d`, with two stale sentences; no item is Nathan's | Considered by App Manager 6; every item accepted as written; nothing declined and nothing for Nathan. See "DM-15" below |

Both reviews are based on the [status and State of the App](../state-of-the-app.md) of 25 September 2026, at the basis commit above. The consultation text is the Dev Manager start prompt as it stood at that commit (`docs/ephemeral/2026-09-25-dev-manager-start-prompt.md`), with the commit filled in. The prompt now lives at [`docs/planning/start-prompts/dev-manager.md`](../../planning/start-prompts/dev-manager.md). Per Nathan, no new implementation task is created until the Dev Manager has responded and its reviews have been considered.

## Dispositions

The primary manager records here, for each report, every finding and approval item with its disposition: accepted, accepted with changes, declined with the reason, or referred to Nathan.

### DM-01 and DM-02 (App Manager 3, 25 September 2026)

App Manager 3 checked the facts it could against the repository before deciding. The contracts corpus test does import mobile source (B10). The review prompt did change after its review head was named (P2). Where App Manager 3 changed or deferred a recommendation, the reason is given here and the Dev Manager's own text stays in its report (P10).

**DM-01, process:**

| Finding | Dev Manager's weight | Disposition | Action |
|---|---|---|---|
| P1 Governing Markdown has no second reader | Before the next implementation task | **Accepted** under Nathan's direction OD-15 (DM-03 G1). DM-01 question 2 asks him to confirm or withdraw it | The Dev Manager reads governing Markdown before its PR merges, and any prompt that authorizes credential use or live provider actions before Nathan runs it. Charter triggers, manager workflow, CI policy and `AGENTS.md` updated. The first such read is DM-03 |
| P2 Manager records ride on the code PR | Before the next implementation task | **Accepted with changes** | This session can push only its own branch, so there is no separate records branch. Instead: records are batched into one push per checkpoint (before a session needs them, and at close-out); review prompts name the code head; the review report states the prompt revision it received. Workflow and charter updated |
| P3 One fact in many places | Soon | **Accepted**; applied in part now | Now: the owner-direction register, ADR 0003, PF01 and PF00 status lines replaced by pointers, the Claude handoff's status line frozen, a slimmed current handoff, and the State of the App marked as a review snapshot. Later: trimming Implementation Control to a status block and links, and a PR-to-work-item index |
| P4 Design decisions on unreviewed evidence | Before the next implementation task | **Accepted** | S15's decision is recorded as conditional on the I1 review confirming the finding live. The revised I1 review prompt makes that confirmation required. The workflow gains the rule |
| P5 The one-item rule and the known flake | Soon; Nathan decides | **Referred to Nathan** (DM-01 question 1) | App Manager 3 recommends yes: a known failure that can turn the current item's CI red is part of the current item |
| P6 Relay continuity and bottleneck | Soon | **Accepted** | (a) documentation batched per checkpoint (see P2); (b) slim handoff (P3); (c) a waiting checkpoint in the handoff before any long wait; (d) every relay prompt names the file and heading where its result is recorded |
| P7 Review paths: gaps and overlaps | Soon | **Accepted**; branch protection referred to Nathan (DM-01 question 4) | A pre-merge checklist in the PR description, with run IDs, the review report, Codex's summary and the Dev Manager's dispositions |
| P8 Mistakes log and TypeSafe scorer | Consider | **Accepted with changes**; the scorer's future referred to Nathan (DM-01 question 3) | Every mistake still gets a summary row, because Nathan asked for all of them to be tracked; full sections only for mistakes that reached a record, a prompt, Nathan or `main`; a repeated prevention moves into a checklist. The scorer's readings live only in the Notion usage log and in each prompt's header; no conditional level commitments |
| P9 Durable prompts in the ephemeral folder | Consider | **Accepted** | Both start prompts moved to `docs/planning/start-prompts/` |
| P10 Relay fidelity to Nathan | Soon | **Accepted** | Nathan gets each report's path and its verdicts as written; every declined or changed item goes to him with the Dev Manager's text beside the reason. Charter relay step 4 updated |
| Charter conditions 1–6 | Approved with conditions | **1–5 accepted**; 6 referred to Nathan (DM-02 question 5) | Triggers, records route, fidelity, continuity (the manager fetches `claude/dev-manager` when it expects a report; a consultation says what happens if none arrives) and the meaning of `approved` added to the charter |

**DM-02, build:**

| Finding | Dev Manager's weight | Disposition | Action |
|---|---|---|---|
| B1 The S15 principle needs explicit limits | Before the next implementation task | **Accepted**; carve-outs referred to Nathan (DM-02 question 1) | ADR 0003 records the display rule, its scope, its reach to server and operator consumers, and the proposed carve-outs. PF01 section 7 now states the principle product-wide. The P06.1 brief updated |
| B2 I2 is too large and under-specified | Before the next implementation task | **Accepted** | P06.1-I2 split into I2a (revocation and safety, live) and I2b (Video and Feeds lockdown, the architecture document, the harness in CI). Economics becomes a read-only dashboard discovery Nathan runs. The restore run is removed. The Dev Manager reads each prompt before Nathan runs it. Brief updated |
| B3 Database last leaves the chat design's core unproven | Soon; Nathan decides | **Referred to Nathan** (DM-02 question 2) | App Manager 3 agrees with the recommendation: a CI-only disposable PostgreSQL proof before P06.2, as a plan amendment |
| B4 The shared logical database with HDE | Soon; Nathan decides | **Referred to Nathan** (DM-02 question 3) | App Manager 3 agrees with a separate logical database, with one refinement. Railway backs up volumes, so a platform restore covers every database on that PostgreSQL service; only a separate service fully separates platform restores. (Not re-checked against Railway's current documentation.) A separate logical database does separate ownership, grants, logical dumps and drops. **DM-03 D1:** the Dev Manager accepted the refinement as a correction to DM-02 and no longer recommends a separate logical database over a separate service outright; see DM-03 below |
| B5 WordPress as the operator surface | Consider; Nathan decides | **Referred to Nathan** (DM-02 question 4) | Decide before the P07 brief |
| B6 The proof harness is tested outside CI | Before PR26 merges | **Accepted** | A Foundation job for the harness's offline checks joins P06.1-I2b, as full-scope work under the CI policy's workflow rule |
| B7 Stream with a display rule | Approved with conditions | **Accepted** | Conditions (a)–(d) added to the brief and ADR 0003. Billing recorded as an open launch gate (A04) |
| B8 Credentials in the shared environment | Consider; Nathan decides | **Referred to Nathan** (DM-02 question 5) | App Manager 3 recommends the split and a rotation of the development secret at P06.1's close |
| B9 Dependency advisories | Consider | **Accepted** | A one-line `npm audit` result in each phase's evidence (CI policy). The State of the App's description of GHSA-vcc3-ghjq-m6fr (it is `decode-uri-component` denial of service) is corrected at its next refresh, so the reviewed snapshot stays as reviewed. Dependabot alerts are Nathan's option |
| B10 Build and CI gaps | Soon | **Accepted**; the flake referred to Nathan (DM-01 question 1); HDE timing referred to Nathan (DM-02 question 6) | The install-order note added to local development. No further mobile mirroring of domain logic: P06.2 takes chat state from API-served fixtures (brief). The pre-merge checklist (P7) covers the advisory gate |

**Questions for Nathan**, relayed as the Dev Manager wrote them in its reports: DM-01 questions 1–4 and DM-02 questions 1–6. Nathan's answers are recorded below, under "Nathan's answers and directions".

### DM-03 (App Manager 3, 25 September 2026)

**The read covered `fa4dc5f`** (DM-03 G2). The batch that applies DM-03 changes governing Markdown again. Each of those changes applies a DM-03 finding's own text or instruction, except one:

- the charter: G1 (OD-15 as the authority) and G2 (a read covers one commit);
- `AGENTS.md`, the CI policy and workflow step 7: G2's wording;
- PF01 1.9: G3 (the interim sentence on carve-outs) and E4 (historical roles);
- PF00 1.8: E4;
- **the exception, the primary manager's own change:** the charter's relay step 1 now says that a consultation can reach an idle Dev Manager session as a one-time Routine, as DM-03 did.

The close-out read before PR26 merges covers all of them.

| Finding | Dev Manager's weight | Disposition | Action |
|---|---|---|---|
| G1 The read is written as in force while its disposition said "pending Nathan" | Before PR26 merges | **Accepted**, option (a) | The charter cites OD-15 as the authority. P1's disposition now reads "accepted under OD-15", and DM-01 question 2 asks Nathan to confirm or withdraw the rule |
| G2 The read is not tied to a commit | Before PR26 merges | **Accepted** | The charter: a read covers one named commit; later governing changes need another read, except those that only apply a Dev Manager finding, which the disposition lists and the next consultation or the close-out read confirms. `AGENTS.md`, the CI policy and workflow step 7 point to it |
| G3 PF01 section 7 lacks ADR 0003's interim safeguard | Soon | **Accepted** | PF01 section 7's carve-outs bullet now carries the sentence |
| G4 Only the display rule is conditional, not the principle | Soon | **Accepted** | ADR 0003's status, register row OD-14 and the brief separate the two: the display rule as S15's answer is conditional; the principle is in force, with its carve-outs pending |
| D1 The dispositions are faithful; B4 refined | No action | **Accepted** | B4's row above records the Dev Manager's change. The refined trade-off goes to Nathan with DM-02 question 3: same database (least isolation); a separate logical database (logical isolation, shared platform restore); a separate service (full restore separation, one more service to run). If restore independence (DB13) is required, the Dev Manager recommends a separate service; otherwise a separate logical database is the minimum |
| R1 Nothing re-checks the configuration after the runs | Before Nathan runs the prompt | **Accepted** | Revision 3, section 4: `verify-clean` and the dry-run `configure` after the last run; differences are reported, not fixed |
| R2 `cleanup --apply` leaves Stream's system user | Before Nathan runs the prompt | **Accepted**, first option | Revision 3: report the `deleted-user-1729640-…` user and leave it; the manager arranges its removal through a later session |
| R3 The fixes' first live use | Consider | **Accepted** | Revision 3 asks whether cleanup and `verify-clean` behaved as intended |
| E1 The brief grants and excludes `.github/` | Before the I2b prompt | **Accepted** | The brief's exclusions except the one Foundation job I2b owns |
| E2 Local development cites the frozen handoff's inventory | Soon | **Accepted**, by moving it | The variable inventory moved verbatim to `docs/operations/environment-inventory.md`, its one living home. The frozen handoff keeps a pointer, and local development and the P06.1 brief link the new home |
| E3 The Dev Manager start prompt is specific to DM-01 and DM-02 | Consider | **Accepted**, deferred | Made generic before its next use. Its header says so |
| E4 Stale role names in the canon | Consider | **Accepted** | PF01's execution model and PF00's session authority name App Planner 1 and App Builder 1 as historical roles |
| E5 ADR 0003 binds P06.3 | No action; noted | **Noted** | P06.3's brief cites ADR 0003 |

**Verdicts, as the Dev Manager wrote them:**

1. Governing Markdown at `fa4dc5f`: approved with conditions (G1 to G4).
2. The dispositions: approved.
3. The revised I1 review prompt: approved with conditions (R1 and R2; R3 optional; `<RECORDS_COMMIT>` filled with the commit that holds the final text).
4. The rest of the batch: approved with conditions (E1 to E4).

It asked no new questions for Nathan.

### DM-04 (App Manager 3, 26 September 2026)

**The read covered** the I2a prompt's blob `7b319ea` at `d50b572`: revision 1, as written at `978ba19`. The consultation named `d50b572`, which holds the same prompt; the review log, the handoff and Notion named `978ba19`.

**Verdict: approved with conditions.** Findings 1 to 8 are conditions for a revision 2 before Nathan runs I2a; finding 9 is optional; there are no questions for Nathan. A revision 2 that applies findings 1 to 8 as written needs no further read (DM-03 G2); any other change to the prompt's sections 3 to 5 would need one.

Before deciding, the manager checked the findings' evidence at `d50b572`. `configuration.verify` compares only authentication, permissions, guest creation, the four required settings and the grants. `_delete_users` lists users without `include_deactivated_users`. `ServerApi` takes an `httpx` transport. CI on `d50b572` passed: push run 36257787443 (ordinary documentation) and PR run 36257790836 (all six jobs).

| Finding | Dev Manager's weight | Disposition | Action |
|---|---|---|---|
| 1 A guard in code for destructive calls | Before I2a | **Accepted** | Revision 2, section 3 and section 4's rule "Only the run's own data" |
| 2 Closing checks that see application-wide settings | Before I2a | **Accepted** | Revision 2, section 3. One fact for the session: the committed baseline records `revoke_tokens_issued_before` (null), `webhook_url` (empty), `event_hooks` (empty) and `custom_action_handler_url` (empty), but has no `before_message_send_hook_url` key, so that field's recorded value is its absence |
| 3 Outage inside the process | Before I2a | **Accepted** | Revision 2, section 4, item 5; the brief's I2a entry |
| 4 A rule for each kind of signal | Before I2a | **Accepted** | Revision 2, section 5, "Signals, by kind", and section 8's stop list. The manager's reading of the finding's word "only": a signal that is not only a rate limit, for example one that also carries quota wording, ends live work; section 8 says so |
| 5 A counted run plan | Before I2a | **Accepted** | Revision 2, section 5, "The run plan", replacing revision 1's fixed 10 users and 15 channels and its line that channel-scoped mechanisms may share users; the brief's I2a entry |
| 6 Undoing from the client; what each member is shown | Before I2a | **Accepted** | Revision 2, section 4, item 1; the brief's I2a entry |
| 7 An independent check before the first live call | Before I2a | **Accepted** | Revision 2, section 5, and its report and records |
| 8 Each live run tied to its commit | Before I2a | **Accepted** | Revision 2, sections 5, 6 and 8 |
| 9 (a) the server send after revocation as an observation; (b) each token's `iat`; (c) `include_deactivated_users` in cleanup's prefix scan; (d) the live-commands line as an outcome | Soon | **Accepted** | Revision 2, section 4, items 4 and 3; section 3; section 5 |
| 10 The Stream variables in the Dev Manager's container | Record | **Accepted** | AM3-19. The consultation's header, the brief, the handoff and Notion now say that none were added for the read, and that the Dev Manager's container, started before OD-28, holds them |
| 11 Notion | Mismatches | **Accepted** | A08's row and the P06.1 row's body brought up to date |
| 12 The Dev Manager's "all ten" | Its own records | **Noted** | This log already said eight; the note under "Nathan's answers and directions" points to the correction |

**Revision 2's changes,** for the close-out read: the header (the revision, the read, the Stream-variables line); the order of the work; section 2's reading list (DM-04 and this disposition); section 3 (the guard, the closing checks and finding 9(c)); section 4 (findings 3, 6 and 9(a) and 9(b), and the guard in the rule "Only the run's own data"); section 5 (findings 4, 5, 7 and 8, and item 5's wording); sections 6 and 8 (findings 7 and 8, and section 8's stop list for finding 4). Nothing is declined, so nothing goes to Nathan beside the Dev Manager's text (DM-01 P10).

### DM-05 (App Manager 4, 27 September 2026)

**The read covered** the I2b prompt's blob `e2b133ed`, the same at `84715ec`, where it was written, and at `9183763`, the head the Dev Manager fetched. The report is `a80d81d` on `claude/dev-manager`, merged into the manager branch at App Manager 4's first records batch. App Manager 4 read it from the branch (the charter's fallback) before Nathan's relay message arrived.

**Verdict: approved with conditions.** Findings 1 to 6 are conditions for a revision 2 before Nathan runs I2b; finding 9 is optional; there are no questions for Nathan. A revision 2 that applies findings 1 to 6 as written, and optionally finding 9, needs no further read (DM-03 G2); any other change to the prompt's sections 3 to 5 would need one.

Before deciding, the manager checked the findings' evidence at `642d1f8`, whose harness is I2a's code head `7ce93cc`. `cmd_configure` (`cli.py`) prints `configuration.apply_plan(before)` and, with `--apply`, sends every request of it; `apply_plan` (`configuration.py`) always returns the application `PATCH`, the five default types' `PUT`s and the `glow-match` `PUT`, so it is not a difference (finding 1). `_CHARGE_WORDS` (`usage.py`) matches `upgrade`, and `_BILLING_WORDS` makes such a match a charge signal (finding 2). `test_toolchain_pins.py` requires exactly one `python-version` per `setup-python` step, one `node-version` and one `npm install --global npm@…` per `setup-node` step, all equal to the pins; the manager ran it offline at `642d1f8`: 3 tests, OK (finding 4). The Foundation gate's Python loop lists `api`, `mobile`, `smoke` and `artifact` by name (finding 4 (c)).

| Finding | Dev Manager's weight | Disposition | Action |
|---|---|---|---|
| 1 `configure --apply` re-sends the whole chat plan; the "only Video and Feeds" condition needs code | Before Nathan runs I2b | **Accepted** | Revision 2, section 4, item 3, and section 5, "The lockdown": a scoped, differential `configure --products video,feeds`, whose `--apply` refuses in code any path outside the Video and Feeds configuration families and anything while chat does not verify, with tests and reversals; verification of chat and both products afterwards; the general `configure --apply` documented as the operator command and never run by the session. The "Never" list names it |
| 2 A "product not on the plan" answer with plan wording ends live work and leaves run 1's data behind | Before Nathan runs I2b | **Accepted**, (a) to (d) | Revision 2, section 5: run 1 is the chat reruns only; the availability probe, one read per product, before run V1; runs V1 and V2 for the Video and Feeds cases, each with only the users it needs; the product-finding rule under "Signals, by kind", in the harness, the README and the prompt, with 402, code 99 and charge, payment, overage or billing wording still charge signals; section 8's stop list says the same |
| 3 A code deny-list in the runner's new op and the guard's new scope | Before Nathan runs I2b | **Accepted** | Revision 2, section 4, items 1 and 2: the op's path allowlist and its refusals (`ring`, `notify`, `video: true`, `/join`, `go_live`, `start_*`, `stop_*`, broadcast, recording, transcription, caption), the guard's matching scope and deny-list, a test and a reversal per refusal, the independent check's confirmation, and deletability: a case whose object has no server-side delete is not made |
| 4 The Foundation job: three rules the prompt does not state | Before Nathan runs I2b | **Accepted**; (c) is the manager's | Revision 2, section 3, item 3, and section 7, check 6: the pin test's rules, in the form the other jobs use; `working-directory: proofs/stream-chat`; `timeout-minutes` 10; no `secrets.*` and no `env:` naming a `STREAM_*` variable; the pin test run offline before each push; the optional `npm audit` line. **(c), at integration:** the manager updates the CI policy's job names and counts and the "all six jobs" wording, and the I2b review prompt names the workflow diff and asks the reviewer to confirm from the PR run that the new job ran and that the gate's list includes it |
| 5 The architecture document: two additions to the outline | Before Nathan runs I2b | **Accepted**; (b)'s ADR update is the manager's | Revision 2, section 6: the table of every path a modified client has to the other member with its closure, and ADR 0003's four conditions with their status per mechanism; (a) is met for removal and per-user revocation only. The manager updates ADR 0003's conditions and "Revisit when" after I2b's review: done by App Manager 5 on 27 September, after the review approved I2b (the evidence record, "Exact-head review of I2b"); the close-out read covers it |
| 6 The run plan: a targeted run 1 is enough, with two conditions | Before Nathan runs I2b | **Accepted** | Revision 2, section 5: `checks/run_plan.py` extended to the `--only` sets counts run 1, V1, V2 and the largest rerun, and the reserve covers the largest of the three; S3a in run 1 as a live check of nit 4's rule, or, if the count does not allow it, the offline test drives the real `ServerApi` hook (section 3, nit 4) |
| 7 M1 and M2 shared by the channel-level mechanisms: the manager's reading is the one meant | No change | **Accepted**; the four-part wording adopted | Revision 2, section 5, "Sharing users or channels between mechanisms", states the rule in the report's four parts, which the report offers as equivalent to revision 1's wording |
| 8 Finding 1 of the I2a review: option (a) | Agreed | **Accepted** | As revision 1 had it: the fix, its reproducing test and reversal, and the independent check's confirmation before any live call |
| 9 (a) why the Video and Feeds lockdown spares `admin`; (b) preflight and `verify-clean` see the new objects; (c) a rate limit inside a V run; (d) the header's model claim | Soon | **(a) and (b) accepted; (c) nothing to add; (d) accepted** | Revision 2, section 4, items 2 and 3: preflight refuses a run when a call, feed or activity exists that the run did not create, and `verify-clean` lists them; the README and the architecture document say why the two lockdowns differ. The header now gives the Fable-level statement as the manager's judgement |
| 10 Notion matches `9183763` | Matches | **Noted** | No action |
| 11 Records: the `GLOW_DATABASE_URL` correction accepted; the reading list names a commit | For the log | **Accepted** | Revision 2, section 2: the report and this disposition are read at the commit the prompt names as its start |

**Revision 2's changes,** for the close-out read: the header (the owner, the revision and the read, the model and level with this revision's readings, the Stream-variables line); the intro and the order of the work; the "Never" list (the general `configure --apply`; the deny-list in code); section 2 (the pin test in the reading list; DM-05 and this disposition read at the start commit); section 3 (nit 4's live control or hook test; nit 5 includes the new op; item 3's job rules; check numbering); section 4 (the probe's request and the configuration paths in the research; deletability; the op's allowlist and deny-list; the guard's scope and deny-list; preflight and `verify-clean`; the scoped, differential `configure`; the general command left as is; why the lockdowns differ; the offline tests' list); section 5 (the independent check's focus; the expected preflight state; the count of four runs; run 1 targeted with S3a; the probe; runs V1 and V2; the scoped lockdown; the four-part sharing rule; both dry runs after the last live command; the product-finding rule); section 6 (the manager-owned follow-ups; the architecture document's table and conditions; the section's contents); sections 7 and 8 (the pin test as check 6; the differences from the report; the stop list). Nothing is declined, so nothing goes to Nathan beside the Dev Manager's text (DM-01 P10).

### DM-06 (App Manager 5, 28 September 2026)

**The read covered** the economics discovery prompt's blob `dd872d5` (revision 1), written at `b729340`, the head the Dev Manager fetched. Nathan carried the consultation to Dev Manager 2, which succeeded Dev Manager 1 that afternoon; its report is `8ba418a` on `claude/dev-manager`, merged into the manager branch at `5704250`.

**Verdict: approved with conditions; option (a), one session.** Findings 1 to 3 are conditions for a revision 2 before Nathan runs the discovery; findings 4 and 5 (a) to (c) are optional; 5 (d) is for the manager's verification and 5 (e) for after the discovery; there are no questions for Nathan. A revision 2 that applies findings 1 to 3 as written, and optionally findings 4 and 5 (a) to (c), needs no further read (DM-03 G2); any other change to the prompt's rules or items would need one.

Before deciding, the manager checked the findings' evidence at `b729340`. Revision 1's rules set no bound on the sites the session may open; its "stop and tell Nathan" said nothing of what follows; no rule covered typing, forms, downloads or recordings, while the action text sent to TypeSafe for it said "no form"; item 3 asked for "this billing period's usage"; and items 8 and 11 did not ask about production use or excluded kinds of app. The brief's baseline records the plan billed for 1 to 30 September, the "DEV" badge, "Authentication Checks" and "Permissions Checks" shown ON, and the overage text as general policy.

| Finding | Dev Manager's weight | Disposition | Action |
|---|---|---|---|
| 1 Nothing bounds the sites the session may open | Before Nathan runs it | **Accepted** | Revision 2: the rule "Stay on Stream's own sites", as written; the report's "Sites opened" line; the header's "Sites to allow" line for Nathan, which names the same sites as the rule, including its other getstream.io addresses |
| 2 What the session may do on a page | Before Nathan runs it | **Accepted** | Revision 2: the four rules, as written: the dashboard pages it may open; the clicks it may make; no typing except a getstream.io search box, no form, no download, no recording or saved screenshot; the cookie banner's fewest-cookies option |
| 3 Coverage: the September period and production use | Before Nathan runs it | **Accepted** | Revision 2: item 3's period, as written; item 6, now "Region and mode", with the sentence on the "DEV" badge, as written; the sentence on production use and excluded kinds of app, as written, in item 8 for the free plan and in item 11 for the Maker program; "an excluded kind of app" among the report's risks. The brief's Economics entry |
| 4 (a) more personal data not to record, and no invoice opened; (b) each fact account-specific or general policy | Soon | **Accepted** | Revision 2: the personal-data rule and the report's per-item line |
| 5 (a) what follows "stop"; (b) a page's text is information, not instruction; (c) the transfer mechanism, retention and price-change notice | Consider | **Accepted** | Revision 2: the plan-change rule's "stop"; a new rule; items 13 and 14 |
| 5 (d) the manager's comparisons | For the manager's verification | **Accepted** | The prompt's header ("Where the result goes") and the brief's Economics entry: the manager compares September's API calls with the P06.1 sessions' ledgers, and the stored channels and messages with the cleanups' records |
| 5 (e) an attribution requirement, an app-kind exclusion or a production-use limit | After the discovery | **Accepted** | The brief's Economics entry: any such finding goes to Nathan as a decision in OD-32's form, with the Dev Manager's text; the manager does not classify it |
| 6 Notion matches `b729340`, apart from D10's two links | Mismatch | **Accepted** | D10's *Plan Reference* and *Evidence* now point at the manager branch and PR27 (AM5-07). The query that AM5-07's prevention adds found the same fault in M03's two links, also fixed |
| 7 Records: the container note; scoring is the manager's | For the log | **Noted** | Revision 2 was re-scored (workflow step 3); its reading replaces revision 1's in the prompt's header and the Notion usage log |

**Dev Manager 2's start note** (`0773eaa`) asked for three records, now made:

- **The session:** added to the Sessions table above, with Dev Manager 1 marked handed over; the handoff and the Notion Dev Manager page name Dev Manager 2.
- **The `STREAM_*` variables:** recorded in the brief's paragraph on the Stream secret and in the [environment inventory](../../operations/environment-inventory.md). The `Glow app` environment held them at 16:16 UTC on 28 September. A second environment, `Glow App - No Stream`, created on 26 September, also exists; App Manager 5 runs in it, and its container, started at 19:41 UTC on 28 September, holds none of them. The start note asks whether Nathan deletes them before the discovery: the discovery runs in Nathan's own browser, in no cloud environment, so nothing in any environment reaches it, and the rotation of the development secret at P06.1's close covers every container that held them.
- **D10's two links:** fixed in Notion (AM5-07).

**Still open, from the handover:** Dev Manager 1's handover (section 7) asks the manager to fold the start prompt it wrote for Dev Manager 2 into [`docs/planning/start-prompts/dev-manager.md`](../../planning/start-prompts/dev-manager.md), whose rewrite for general use (DM-03 E3) is still deferred. That prompt's text is in Dev Manager 2's session, not the repository. The rewrite is done before the next Dev Manager session starts (the handoff's P06.1 close-out list).

**Revision 2's changes,** for the Dev Manager's next read: the header (the revision line; DM-06's additions to the brief line; finding 5 (d) under "Where the result goes"; revision 2's reading, with revision 1's marked superseded; the Dev Manager's read; "Sites to allow"); the intro's revision number; the rules (findings 1, 2, 4 (a), 5 (a) and (b)); items 3, 6, 8, 11, 13 and 14 (findings 3 and 5 (c)); the report (the revision, "Sites opened", account-specific or general policy, and an excluded kind of app among the risks). Nothing is declined, so nothing goes to Nathan beside the Dev Manager's text (DM-01 P10).

**After the discovery** (28 September): it ran from revision 2 and is recorded in the evidence record, "Economics discovery".

- Finding 5 (d): the dashboard's Chat count is within about 7% of the sessions' ledgers: at most 162 calls, 7.2% of the ledgers. This line said "within 7%" until DM-07 item 5 corrected it.
- Finding 5 (e): no attribution requirement, excluded kind of app or production-use restriction was found, so nothing went to Nathan.
- Section 6's documentation list: PF01's A04 row is not changed, because PF01 changes only when a rule does (DM-01 P3), and no rule changed. The facts are in the evidence record, the brief and Notion's A04 and A05 rows. DM-07 asks the Dev Manager to agree or not, and about two terms DM-06 did not name (sections 6.2 and 12.5).

### DM-07 (App Manager 5, 29 September 2026)

**The read covered** `89a8d018d6bdfba0fe41fa0b54964f33775ddaac`, the manager branch's head, which had not moved when the Dev Manager fetched it again at 00:55 UTC on 29 September. Nathan carried the consultation to Dev Manager 2; its report is `a60d8c1` on `claude/dev-manager`. Nathan then answered item 6 (c) in the Dev Manager's session, which recorded his words at `f86f28d`. Both were merged into the manager branch at `0704199`.

**Verdict: the governing Markdown approved with conditions (findings 1.1 and 1.2), before PR27 merges.** Five files and ADR 0003 are approved outright; no change adds a rule Nathan did not direct. A revision that applies findings 1.1 and 1.2 as written needs no further read (G2); any other change to the seven files would need one. The HDE contract request is approved and ADR 0004's restore risk confirmed, each with one *soon* item. Items 4 (a) and 4 (b): option (i), neither Nathan's now. The economics disposition is approved, with one wording nit. Item 6: Nathan decides (a), (b) is an action OD-28 already directs, and (c), since answered, was his.

Before deciding, the manager checked the cited passages at `89a8d01`: PF01 §7's *"conditional on the exact-head review confirming S15"*; PF01 §4's Operations row, *"never reads app or HDE tables (OD-19)"*; PF00's *"Nathan reinitiates managers manually."*; the charter's boundary and "Session lifecycle"; `CLAUDE.md`'s Dev Manager line; the HDE request's section 4, step 4; ADR 0004's consequences; and the arithmetic, 884 + 119 + 698 + 560 = 2,261 and 162 ÷ 2,261 = 7.2%. Each is as the report says. Dev Manager 1's handover holds Nathan's succession words, as the report quotes them.

| Item | Dev Manager's weight | Disposition | Action |
|---|---|---|---|
| 1.1 The Dev Manager succession is practised but not recorded as a rule | Before PR27 merges | **Accepted** | The register's OD-35, with Nathan's words from Dev Manager 1's handover and the Dev Manager's state text as written; the charter's "Session lifecycle" line and its boundary's exception; `CLAUDE.md`'s clause, in the finding's words, with OD-35 set off by a comma as the manager line sets off OD-31; Notion's register copy and D10 |
| 1.2 PF01 §7's stale sentence | Before PR27 merges | **Accepted** | PF01 1.11: the parenthesis keeps its ADR 0003 link and replaces the condition with "confirmed live by the I1 review on 25 September 2026". The slip is AM3-22 |
| 1.2 PF01 §4's "never reads" | Consider | **Accepted** | PF01 1.11: "never reads or writes app or HDE tables", as written |
| 1 PF00's sentence on reinitiating managers | Consider | **Accepted** | PF00 1.10: "or directs a manager to create its successor (OD-31)", as written |
| 1 The other files and ADR 0003 | Approved | **Noted** | None |
| 2 HDE contract request: the verbatim copy | Soon, before the receipt | **Accepted** | Section 4, step 4, and section 6: the non-governing copy under `docs/planning/sources/` is the default; if HDE's process forbids one, the receipt pins the exact HDE commit and path of each passage it cites |
| 3 ADR 0004: the other direction | Soon, before P11's runbooks | **Accepted** | ADR 0004's consequences: "A restore runs both ways", with the Dev Manager's text; its line on the accepted risk records the confirmation |
| 4 (a) No live read in P06.1 | Condition for P06.2's brief | **Accepted** | ADR 0003's condition (c); the brief's "Carried to P06.2", item 1; the evidence record's DM-07 section |
| 4 (b) The activities query and resource roles left open | Not Nathan's now; his before the production application is configured | **Accepted** | The brief's "Carried to P06.2", items 2 and 3: the P06.2 brief puts the question to him in OD-32's form |
| 5 The economics disposition | Approved; "within about 7%" | **Accepted** | "Within about 7%", with "at most 162 calls", in the brief, the evidence record, this log and Notion (AM5-08). Section 6.2 belongs to P07 (A05) and section 12.5 to A04, each read in Stream's exact words first; Notion's A04 and A05 rows say so, and that the addendum's PDF and the Trust Center stay unverified for A05 |
| 6 (a) The lockdown stays | Nathan's decision | **Referred to Nathan** | Put to him in OD-32's form, with both managers' recommendation. His answer (OD-37): *"Stop worrying so much about this secret. I want to move forward with dev"*, read as accepting the recommendation: the development application stays locked down |
| 6 (b) Replace the secret as soon as Nathan can | An action OD-28 directs | **Referred to Nathan** | Put to him as an action. His answer (OD-37) supersedes the replacement at P06.1's close: it is no longer a close-out item, and the manager stops raising it |
| 6 (c) The environments | Nathan's | **Answered by Nathan** (OD-36) | His words at `f86f28d`. The register's OD-36, with OD-28's mechanism marked superseded; the environment inventory; local setup; the brief; the next-manager start procedure; and the governing lines listed below. The Dev Manager withdrew its reading that the variables' presence in `Glow app` was a slip |
| 7 The start prompt | Before the next Dev Manager session | **Accepted** | The report's appendix is the source for the rewrite of [`docs/planning/start-prompts/dev-manager.md`](../../planning/start-prompts/dev-manager.md) (DM-03 E3), with the environment to start in and OD-35's succession line; the handoff lists it |
| 8 Notion: M03's and D10's texts | Mismatch | **Accepted** | M03's *Next Action* (AM3-23) and D10's (OD-35), corrected and read back |

**Changes to governing files after `89a8d01`** (the charter, "Read before it takes effect"). Each applies a Dev Manager finding's own text or instruction, so none needs another read before PR27 merges; the next consultation confirms them:

- **Findings 1.1 and 1.2, as written:** `CLAUDE.md`'s Dev Manager line; the charter's boundary and "Session lifecycle"; PF01 §7 and §4, with PF01's revision line and history entry 1.11; PF00's sentence, with its revision line and history entry 1.10.
- **Nathan's answer and the Dev Manager's instruction that every prompt names the environment to start in** (`f86f28d`), with DM-07 item 6 (c)'s own words for each environment's use:
  - the manager workflow: a new item in step 3, and the line on Nathan starting sessions, which now says he opens each in the environment the prompt names;
  - the charter's relay paragraph, which named `Glow app` for the Dev Manager: it now names the environment its start prompt names, and for future Dev Manager sessions `Glow App - No Stream` (item 6 (c): "Future Dev Manager sessions should start in the environment without the variables").

**Left as they are, for the next consultation to confirm or correct:**

- `AGENTS.md`, `CLAUDE.md`'s manager line, PF00 and PF01's execution-model line and D10 say that the manager creates the Dev Manager. That stays the usual path; the successor path is added only where finding 1.1 named it.
- `CLAUDE.md`'s "Environment" line says app sessions run in "the dedicated app cloud environment". Both app environments are dedicated, hold no HDE variables and have the pinned toolchain (observed in `Glow App - No Stream` on 29 September), so it is not wrong, but it reads as one environment.
- The workflow's step 3 item on credentials says that a prompt for a session started while the variables were set says "none added". Under OD-36, such a session is one started in `Glow app`.

**What went to Nathan:** only item 6 (a) and (b), in one message (OD-32). He answered the same day (OD-37). Items 4 (b), 6.2 and 12.5 come to him later: before the production application is configured, at P07 and at A04. Nothing is declined, so nothing goes to him beside the Dev Manager's text (DM-01 P10).

### DM-08 (App Manager 5, 29 September 2026)

**The read covered** `b75107c3ca135bd7b3a50943fbed4a1bd47d1247`, the manager branch's head when the Dev Manager fetched it. Nathan carried the consultation to Dev Manager 2; its report is `70f65f0` on `claude/dev-manager`, merged into the manager branch at `145502e`.

**Verdict: the brief approved with conditions.** D1 is approved; D2, D3, D4, D5 and item 6 are approved with conditions; item 7 asks for two narrow changes. D4 is within OD-17. No item is Nathan's. A brief revision 2 and a prompt that apply the conditions as written need no further read (G2); any other change to D3, D4 or D5 would need one. The CI policy's change is read before PR28 merges (7.1).

Before deciding, the manager checked the cited passages at `b75107c`: the data model's `auth_session_ref` paragraph (*"an adapter-provided **non-secret** library session identifier"*; *"does not revoke a credential"*) and its UOW table (the send row's *"Same revocation lock boundary, current two-party eligibility/contact version"*; the block, unmatch, suspend and delete row's *"deletion job+tombstone when deleting"*); the P11 plan's row 90 (*"unblock/resume must not resurrect a historical match"*) and row 138 (*"An identical retry by a currently authorized actor recovers the original immutable receipt"*); the gate's `needs` list and its loop over five jobs; the CI policy's *"five application jobs"*; `MessageSubmission.actor`'s `CASCADE`; and PF01 §6's WordPress sentence. Each is as the report says. The Notion duplicate was there: the Work Register held an older P06.DB row, "Planned", beside the one the manager created on 29 September.

| Item | Dev Manager's weight | Disposition | Action |
|---|---|---|---|
| D1 Isolation | Approved | **Accepted** | Brief revision 2, D1: explicit connection options with a `passfile` and no service name, so no libpq default applies; the refusal of any `PG*` name stays |
| D1 A Django pin test | Consider | **Accepted** | Brief D1 and the prompt: an offline test fails if the proof's Django differs from `services/api`'s |
| D1 `makemigrations --check --dry-run` | Consider | **Accepted** | Brief D1 and the prompt: run in the job against the disposable database |
| D2 The DB09 claim | Condition | **Accepted** | Brief D2 and D6: DB09 is partially evidenced only for the app-side session and epoch revocation ordering against sends, with a stand-in `auth_session_ref`, not for maintained authentication; the stand-in generator is not carried into the app |
| D3 1 to 4 | Conditions | **Accepted** | Brief D3, as written: the password generated under `set +x` and masked first, passed by a file; loopback, a unique name, `pg_isready` with a limit, `timeout-minutes`, `if: always()` removal, no `env:` of secrets, read-only permissions; `-c track_commit_timestamp=on` and `SELECT version()` with the digest; the gate's `needs` and required list |
| D3 A non-superuser role | Consider | **Accepted** | Brief D3 and the prompt: the proof connects as a role created in the job that owns the proof's database and is not a superuser |
| D4 1 to 4 | Conditions; within OD-17 | **Accepted** | Brief D4, as written: only the final-head CI run is evidence; the same recipe; a throwaway local cluster if Docker does not work; the report says which was used. Not put to Nathan (OD-32) |
| D5 5.1 to 5.6 | Conditions | **Accepted** | Brief D5, as written, with the two choices the conditions leave to the brief: the send locks its `AccountSession` row after the accounts and the match, and sign-out and an administrative expiry lock that row (5.1); suspension and deletion lock the account row and bump its session epoch, not each match (5.3). A paused or restricted profile and a withdrawn consent are recorded as excluded, because A05 has not set their effect on an existing conversation (5.6) |
| D5 Unblock does not resurrect | Soon or consider | **Accepted** | A case in brief D5 and the prompt |
| D5 `SERIALIZABLE` | Soon or consider | **Accepted** | `READ COMMITTED` with row locks is the design P06.2 takes; `SERIALIZABLE` runs, if at all, only as a recorded comparison with its own negative control |
| D5 The outbox | Consider | **Accepted** | The send's transaction inserts its `OutboxEvent`, so the proof shows it commits or rolls back with the authorization |
| 6 6.1 to 6.3, and what "partially" claims | Conditions | **Accepted** | Brief item 6 and D6, as written: the commit-order oracle over every row, each forced wait observed, the controls failing in the same final-head run, the stress run's seed, iterations and overlap count; the claims and non-claims in the report's words |
| 6 A race suite against a small interface | Consider | **Accepted** | Brief item 6 and the prompt: the suite drives send, block, unmatch, suspend, delete and sign-out through one interface, so P06.2 can run it against the app's adapter |
| 7.1 The CI policy | Changes requested | **Accepted** | `docs/operations/` joins the manager-owned paths. At integration the manager updates the CI policy's job list, "the five application jobs" and anything else that names the jobs; the Dev Manager reads that change before PR28 merges |
| 7.2 The review plan | Changes requested | **Accepted** | The brief says the prompt needs no Dev Manager read: the generated password is not credential use in the charter's sense and no provider action is taken. A prompt that departs from the brief and DM-08 on D3, D4 or D5 goes back to it. The exact-head review checks, from the job's logs, that no password appears, that each forced wait was observed and that the controls failed in the same run |
| 7 The stress run's size | Consider | **Accepted** | The prompt fixes iterations per race and a wall-clock cap under the job's timeout (OD-21) |
| 8 Notion: the duplicate P06.DB row | Mismatch | **Accepted** | The older "Planned" row now sits under the current row as a page, its text kept in its body, so the Work Register holds one P06.DB row (AM5-11). The Notion checklist now asks for a search by Work ID before a row is created, and the old-wording query looks for duplicate IDs too |

**Governing changes in this batch:** one line in the manager workflow's Notion checklist, applying the report's own sentence (*"The AM5-07 link query should also cover duplicate IDs"*) with the search before creating a row that AM5-11 adds. It goes to the Dev Manager's read before PR28 merges, with the CI policy's change (7.1) and the changes the DM-07 section above lists.

**What went to Nathan:** nothing. No item is his, and nothing is declined (DM-01 P10).

### DM-09 (App Manager 5, 5 October 2026)

**The read covered** `ee25d1d3deaef4b3d73b97f7f9012ed7208dbc3c`, the manager branch's head when the Dev Manager fetched it. Nathan carried the consultation to Dev Manager 2; its report is `bc0306c` on `claude/dev-manager`, merged into the manager branch at `c49175c`.

**Verdict: the CI policy and the manager workflow approved; nothing blocks PR28's merge.** DM-07's changes after `89a8d01` are confirmed as applied, and its three items as they stand. The dispositions of C1's exact-head review are approved: no correction pass, the guard carried to P06.2, and one *soon* wording change to DB09's mark. Notion matched `ee25d1d`. No item is Nathan's. The read covers `ee25d1d`: a later change to either governing file before the merge needs a new read, and a records-only change elsewhere does not.

Before deciding, the manager checked the cited passages at `ee25d1d`: the gate's `needs` list in `foundation.yml` (`[scope, api, mobile, smoke, artifact, proof, database]`), `CLAUDE.md`'s line 16 and the manager workflow's line 14. Each is as the report says.

| Item | Dev Manager's weight | Disposition | Action |
|---|---|---|---|
| 1 The CI policy | Approved | **Accepted** | None |
| 1 A newer upload-artifact pin | Consider | **Accepted** | The handoff's recorded follow-ups |
| 1 The manager workflow | Approved; no change adds a rule Nathan did not direct | **Accepted** | None |
| 2 (a) DM-07's changes after `89a8d01` | Confirmed as applied | **Noted** | None |
| 2 (b) The three items left as they are | Confirmed as they stand | **Noted** | None |
| 2 (b) `CLAUDE.md`'s environment phrase, the inventory's No Stream Setup script and a pointer to OD-35 in PF01's D10 | Consider, at the next change to those files | **Accepted** | The handoff's recorded follow-ups, for the next change to `CLAUDE.md`, the environment inventory and PF01 |
| 3 No correction pass after C1's review | Approved | **Accepted** | None |
| 3 DB09's lead wording | Soon | **Accepted** | The P11 plan's DB09 entry and the brief's D6, in the report's words: *"the app-side session revocation ordering against sends (sign-out, expiry, and account-state revocation, which bumps the epoch); the epoch's consistency is checked but not exercised as the deciding refusal"* |
| 3 The guard, carried | Approved, sharpened | **Accepted** | The brief's "Carried to P06.2", item 1: before P06.2's first run of the suite on any database, local or CI |
| 3 Tests for R3 and R4 | Consider, for P06.2's brief | **Accepted** | The brief's "Carried to P06.2", item 3 |
| 4 Notion | Matches `ee25d1d` | **Noted** | None |

**Governing changes in this batch:** none. DB09's new wording is in non-governing files and needs no read (the report, item 3).

**What went to Nathan:** nothing. No item is his, and nothing is declined (DM-01 P10).

### DM-10 (App Manager 5, 5 October 2026)

**The read covered** `cd9fa03fcb62ab5279b17665865d5222434183e6`, the manager branch's head when the Dev Manager fetched it. Nathan carried the consultation to Dev Manager 2; its report is `9f2e79d` on `claude/dev-manager`, merged into the manager branch at `2152463`.

**Verdict: CX3 is corrected before the merge, with the run's marker as revision 3 states it, on conditions.** The CI policy names the marker. CX1 and CX2 stay carried to P06.2. Notion matched `cd9fa03`. No item is Nathan's.

Before deciding, the manager checked the report's two claims about the code at `cd9fa03`. The package opens no connection outside Django: `psycopg.connect` and `connection_created` appear nowhere. Each worker thread keeps one Django connection across its tasks and closes it only when it stops (`concurrency.py:23` to `44`).

| Item | Dev Manager's weight | Disposition | Action |
|---|---|---|---|
| 1 CX3 in the correction class; correct before the merge | Approved | **Accepted** | None: the evidence record's disposition stands |
| 2 The run's marker | Approved with conditions | **Accepted** | Brief revision 4 quotes conditions 2.1 to 2.5 in D1 and applies them to D3 and D4. The C2 prompt applies 2.1 to 2.4 as written, so it needs no further read (DM-03 G2); C2's exact-head review checks 2.5 |
| 2 A departure on the marker's form, the hook, the CI step or the suite | Comes back to the Dev Manager | **Accepted** | The C2 prompt tells the session to stop and report any such departure |
| 3 CX1 and CX2 carried to P06.2 | Approved | **Accepted** | None: the brief's "Carried to P06.2", items 4 and 5 |
| 4 The CI policy's database sentence | Changes requested, narrowly | **Accepted** | The report's words, applied as written at C2's integration (its section 6), so that the policy describes the job as it then runs; no further read |
| 5 Notion | Matches `cd9fa03` | **Noted** | None |

**Governing changes in this batch:** none. The CI policy's sentence changes at C2's integration, in the report's words.

**Applied at C2's integration** (5 October, the records batch after the merge `369d03c`): the CI policy's sentence, in the report's words (item 4), so it needs no further read (DM-03 G2). It is the only governing change since `ee25d1d`, and the next consultation or the close-out read confirms it.

**After the disposition:** writing the C2 prompt, the manager found that condition 2.3's query cannot be met as written: every PostgreSQL database keeps the toast tables of its own catalogs in `pg_toast`. The prompt also excludes the `pg_`-prefixed system schemas, and DM-11 reads that departure before the prompt runs, as DM-10 asks. (It did, and replaced the departure with its own words: see "DM-11".)

**What went to Nathan:** nothing. No item is his, and nothing is declined (DM-01 P10).

### DM-11 (App Manager 5, 5 October 2026)

**The read covered** `d50f334b57a26c559ccf7fea541bafe35fc3b381`, the manager branch's head when the Dev Manager fetched it. Nathan carried the consultation to Dev Manager 2; its report is `91c5c2c` on `claude/dev-manager`, merged into the manager branch at `a9eae28`.

**Verdict: the C2 prompt runs as revision 2, with the departure in the report's words.** Revision 1 does not run. The rest of the prompt is confirmed. Notion matched `d50f334`. No item is Nathan's.

**Whose error.** DM-10's 2.3 query was the Dev Manager's error, caught by the manager while writing the C2 prompt; the report says so (item 1). The departure that replaced it was the manager's, and it had a gap of its own: it named no database for the query, so a step could have run it from another database and passed. It gave the prefix test in words ("starts with `pg_`"), not in SQL: the report's "its prefix test is a wildcard" describes the test written as `LIKE 'pg_%'`, which those words did not exclude. That is AM5-19.

| Item | Dev Manager's weight | Disposition | Action |
|---|---|---|---|
| 1 The departure from 2.3 | Approved with conditions | **Accepted** | C2 prompt revision 2 replaces the departure's two bullets with the report's words (section 3, item 1), as written. Brief revision 5: D1's note under 2.3 points to them, and D3's item 5 describes the check they give |
| 2 The rest of the prompt | Confirmed; one note for C2's exact-head review | **Accepted** | Revision 2 also quotes the note under 2.4, in the report's words, so that the session knows it, and brief revision 5 records it under 2.4; C2's exact-head review checks it in the workflow diff |
| 3 Notion | Matches `d50f334` | **Noted** | None |

**What revision 2 changes, besides the report's words** (each applies them; DM-03 G2):

- the header: its revision, why revision 1 did not run, the brief's revision, the work list, a new TypeSafe reading and the Dev Manager's read;
- the reading list: the DM-11 report, and brief revision 5, which records DM-11's words in D1 and D3;
- what the session reports and records from the wrong-marker step: the relation counts per schema, before and after, as the report's words require;
- what its record tells the exact-head review: DM-11's note on 2.4, beside DM-10's 2.5;
- its start line and its report: revision 2.

**Governing changes in this batch:** none. The CI policy's sentence still changes at C2's integration, in DM-10's words (item 4); the report's check leaves the proof's database without a table, so those words still describe the step.

**What went to Nathan:** nothing. No item is his, and nothing is declined (DM-01 P10).

### DM-12 (App Manager 5, 5 October 2026)

**The read covered** `16c94500eb6a008d7466f84a3dffa7f150dbdc9c`, the manager branch's head when the Dev Manager fetched it. Nathan carried the consultation to Dev Manager 2; its report is `b06fe29` on `claude/dev-manager`, merged into the manager branch at `8a94904`.

**Verdict: F1 needs no correction pass before the merge, and nothing blocks PR28 going ready for Codex.** The guard that refuses `dbshell` is required before P06.2's first run of the suite on any database, not optional. The CI policy's sentence is confirmed. Notion matched `16c9450`. No item is Nathan's.

**Whose words.** DM-10's 2.2 heading, "wired so no command can skip it", was the Dev Manager's, and the report says it overstated what the condition's body requires: the connection path through Django. It did not name `dbshell`, the one Django command that bypasses that path. C2's exact-head review tested the heading literally, as it should.

| Item | Dev Manager's weight | Disposition | Action |
|---|---|---|---|
| 1 F1's classification | Approved: outside the correction classes; no C3 | **Accepted** | None: the evidence record's disposition stands, with a note in place |
| 2 The README's rule, the brief's note and item 6 | Approved with conditions: item 6 required before P06.2's first run of the suite on any database, in its words | **Accepted** | Brief revision 7 replaces "Carried to P06.2" item 6 with the report's words, and replaces "carried to P06.2 as optional" in the F1 note under 2.2 and in "Sessions"; the README's "Limits" line takes the same words. Applied as written, so no further read (DM-03 G2). The report's design note (a proof-local command needs the package as an installed app, which it is not today) is under item 6, for P06.2's brief |
| 3 The CI policy's sentence | Confirmed, word for word | **Noted** | None: the only governing change since `ee25d1d` is confirmed |
| 4 Notion | Matches `16c9450` | **Noted** | The Work Register's P06.DB row and *Implementation Control* drop "optional" in this batch |

**Governing changes in this batch:** none.

**What went to Nathan:** nothing. No item is his, and nothing is declined (DM-01 P10).

### DM-13 (App Manager 6, 5 October 2026)

App Manager 6 checked the report against the brief at `a8db520` and the relayed message, which matches the report's section 8. Every item is accepted as written; brief revision 2 applies them, so it needs no further read (DM-03 G2). The Dev Manager's text is in its report.

| Item | Verdict | Disposition | Where applied |
|---|---|---|---|
| 1 D1, the stages | Approved; say P06.2 is done only when Stage C merges | **Accepted** | Brief, Status line and D1 |
| 2 D2 and D3 | Approved with conditions 2.1 to 2.3 | **Accepted**: no fault switches in the adapter; the job's budget stated in Stage A's prompt; a sealed-runtime test | Brief, D2 and D3; acceptance check 4 |
| 3 D4 | Confirmed | **Accepted** | Brief, D4 |
| 4 D5 | Approved with condition 4.1 | **Accepted**: each writer takes the account lock and bumps the checked row's version, with forced races, or is excluded by name; the consent is the onboarding consent (F02) | Brief, D5 |
| 5 D6 | Approved with condition 5.1 | **Accepted**: per-user revocation on every session-epoch bump; a one-hour token lifetime, with the single-device sign-out residual as a limit beside DB09; TD-expiry closed by removal and deactivation | Brief, item 4 and D6 |
| 6 D7 | Approved | **Accepted**, with its checks | Brief, D7 |
| 7 D8 | Not referred; conditions 7.1 and 7.2 | **Accepted**: the three triggers in the brief and ADR 0003's "Revisit when"; option (a), the client SDK behind a view-model adapter in Stage C, whose prompt the Dev Manager reads | Brief, item 5 and D8; ADR 0003 |
| 8 The carried items' order | Confirmed; Stage A's prompt chooses the `dbshell` mechanism | **Accepted** | Brief, D1 Stage A |
| 9 What the brief misses | Changes requested, 9.1 to 9.5 | **Accepted**: `getstream` 6.1.0 in the API's lock at Stage B; the client SDK per 7.2; unread from a server-side read cursor, with no grant change; no name, image or custom field, IDs committed before the call; each document assigned. Also the worker's runtime and Stage B's harness scope | Brief, items 2, 3 and 5, owned paths, "Documents each stage updates" |
| 10 PR29's governing changes | Approved; for M04, exclude `claude/dev-manager` by name | **Accepted**; the read covers `a8db520` for the AM5-23 sentence and step 7 | Handoff, M04's starting points |
| 11 Notion | Matches, apart from the procedure stamp | **Accepted**: the stamp corrected | Notion, Implementation Control |

### DM-14 (App Manager 6, 6 October 2026)

App Manager 6 checked the report (`e85bad6`) against the relayed message, which matches its section 8, and integrated it with the merge after `da9fac6`. Both governing changes apply the report's own words, so they need no further read (DM-03 G2); the read covers `da9fac6`.

| Item | Verdict | Disposition | Where applied |
|---|---|---|---|
| 1 Step 3's OD-40 sentence | Approved; *consider* a clause | **Accepted**, the clause appended as written | Manager workflow, step 3 |
| 2 Step 5's AM6-01 sentence | Approved with a condition | **Accepted**: the bullet replaced with the report's words | Manager workflow, step 5 |
| 3 F1 | Disposition approved; mechanism points 1 to 5 | **Accepted** as Stage B's requirements | Brief, "Carried to Stage B and P11", item 1 |
| 4 F3 | Approved with a condition | **Accepted**: a dead-lettered revocation is marked for reconciliation and shown in the conformance run | Brief, item 2 |
| 5 F2, F4, F5 | Approved; list them in Stage B's prompt | **Accepted** | Brief, item 3 |
| 6 Nothing else before the merge | Confirmed, with item 2 applied; a scratch-copy line for the next review prompt | **Accepted**; Codex's CX4 and CX5 dispositioned (the evidence record) | Brief, item 6; the pre-merge checklist |
| 7 Notion | Matches `da9fac6` | **Accepted** | — |

### DM-15 (App Manager 6, 6 October 2026)

App Manager 6 checked the report (`c748c64`) against the relayed message, which matches its section 8, and integrated it with the merge `e7cddd4`. Brief revision 3 and B1's prompt state its conditions as written, so neither needs a further read (DM-03 G2).

| Item | Verdict | Disposition | Where applied |
|---|---|---|---|
| 1 The split | Approved with conditions 1.1 to 1.3 | **Accepted** | Brief, D1 and the review plan; B1's prompt (header, section 1 item 2, "A departure") |
| 2 B1's owned paths | Approved with 2.1 to 2.3 | **Accepted** | Brief, owned paths; B1's prompt, section 5 and the rules |
| 3 Point a | Approved with 3.1 to 3.5 | **Accepted**, the identity column recommended | Brief, design point a; B1's prompt, item 1 |
| 4 Point b | Approved with 4.1 to 4.5; amending `0003` allowed | **Accepted**; the session chooses `0003` or `0004` and records why | Brief, design point b; B1's prompt, item 2 |
| 5 Points c and d | Confirmed, with 5.1 and 5.2 | **Accepted**; 5.2's truncation goes to B2's prompt | Brief, design points c and d, "Carried" item 1.6; B1's prompt, items 3 and 4 |
| 6 Points e and f | Approved with 6.1 to 6.3 | **Accepted** | Brief, design points e and f; B1's prompt, items 5 and 7 |
| 7 Notion | Matches `d12cc0d`; two stale sentences | **Accepted**: the evidence record's receipt "Next" pointed to revision 3; Implementation Control's sentence corrected | The evidence record; Notion |

## Nathan's answers and directions (25 September 2026)

Nathan answered the Dev Manager directly in its session, and the Dev Manager recorded his words and their consequences in five files. They arrived through Nathan's relay message and were integrated in the batch that follows `516bee2`.

- [Owner answers to DM-01 and DM-02](reviews/2026-09-25-owner-answers-to-dm-01-dm-02.md) (`574ee0e`), A1–A8
- [Addendum](reviews/2026-09-25-owner-answers-addendum.md) (`2beb86d`)
- [Relay direction](reviews/2026-09-25-relay-direction.md) (`82e53f9`)
- [Operational guidance in Notion](reviews/2026-09-25-notion-operational-guidance.md) (`e6af216`)
- [Notion precedence delegated](reviews/2026-09-25-notion-precedence-delegated.md) (`d945478`)

**Eight of the ten questions were answered.** The Dev Manager put eight points to Nathan, and its relay message says all ten were answered. Two were not among them:

- **DM-01 question 2** (the Dev Manager read). The read stays in force under OD-15, as DM-03 G1 set out, unless Nathan withdraws it.
- **DM-01 question 3** (the TypeSafe scorer). It is raised when the pre-registered ten-session comparison ends.

Neither blocks anything, so neither is put to Nathan again now. DM-04 finding 12 corrects the Dev Manager's own files, which said all ten were answered.

| Answer | Question | Register | Disposition | Where applied |
|---|---|---|---|---|
| A1 S15 exceptions | DM-02 q1 | OD-16 | **Recorded and applied** | ADR 0003 decision 4, PF01 §7, the brief. The Dev Manager's reading of "essential system screens" (screens the operating system or store requires and Glow cannot replace) is adopted |
| A2 Disposable PostgreSQL proof | DM-02 q2 | OD-17 | **Recorded and applied** | PF01 §6 and §8 (P06.DB after P06.1, before P06.2), the P11 deferred acceptance cases. The P06.DB brief is written when the item starts |
| A3 The app's own logical database | DM-02 q3 | OD-18; OD-03 superseded | **Recorded and applied**, with one correction | New ADR 0004; ADR 0002's supersession note; PF01 §4, §6, P11A, P11C and A02; the migration plan, resource ownership, the P11 cases (the move-out proof joins DB01), the domain boundaries, the fixture notes and provider conformance. The environments, configuration, runbook, data-model and reciprocal-eligibility documents followed in the next batch (AM3-10). **Correction:** the Dev Manager wrote that the API "reserves its own connection name, `GLOW_DATABASE_URL`". In fact the fixture guards refuse that name, like every database connection name; P11 chooses the app's own setting. ADR 0004 says so |
| A4 WordPress and Django | DM-02 q4 | OD-19 | **Recorded and applied**; the Dev Manager's safeguards go to the P07 brief | PF01 §1 and §4 |
| A5 The Stream secret | DM-02 q5 | OD-20, OD-28 | **Recorded.** The primary manager recommended one environment, with the three `STREAM_*` variables added for each session that calls Stream and deleted after it starts. Nathan agreed on 25 September (OD-28) | The brief; the environment inventory; the CI policy (no Stream secret in CI) |
| A6 The intermittent CI failure | DM-01 q1 | OD-21 | **Recorded and applied.** The flake diagnosis prompt is written; it runs inside P06.1 | Manager workflow (one item at a time; no acceptance on a rerun alone), the CI policy, the brief |
| A7 Stream Maker and the HDE contract | DM-02 q6 | OD-22, OD-23 | **Recorded and applied.** The [HDE contract request](../../planning/hde-contract-request.md) is written, and Nathan takes it into HDE's own process | PF01 A01, A04, A05, A07 and R05; the brief's economics |
| A8 No paid GitHub plan | DM-01 q4 | OD-24 | **Recorded and applied** | The CI policy lists what is not enforced and the procedural substitutes. Dependabot alerts are Nathan's option, not verified as free |
| Relay by hand | — | OD-25 | **Recorded and applied.** Scheduled messages into the Dev Manager's session are retired | The charter (relay, continuity), the manager workflow, the Dev Manager start prompt |
| Operational guidance in Notion | — | OD-26 | **Recorded and applied** | `AGENTS.md`, PF01 §2 and D04, PF00's authority map, `docs/README.md`, the manager workflow; in Notion, Implementation Control's operating procedure and a register page |
| Notion precedence delegated | — | OD-27 | **Decided by App Manager 3:** the repository wins, and Notion is corrected to match. Every records batch ends with a match check and a readback | Manager workflow ("Notion and the repository"), the charter's records table |

**The Dev Manager's Notion findings** (the operational-guidance note): all three gaps are accepted and fixed in Notion.

- The status block now records the answers.
- The operating procedure is rewritten to match the repository.
- The register has its own Notion page.

Implementation Control's history moves to a sub-page, as DM-01 P3 recommended.

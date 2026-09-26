# Dev Manager review log

This is the index of every consultation with the Dev Manager, its verdicts and the primary manager's dispositions. The role, the relay and the triggers are in the [Dev Manager charter](../../planning/dev-manager.md).

- The Dev Manager writes its reports in [`reviews/`](reviews/) and changes nothing else.
- The primary manager keeps this log. It records each consultation when it is sent, and each disposition when the report is integrated.
- Nathan decides wherever the two managers disagree, and his decision is recorded here.

## Sessions

| Session | Created | By | Branch | Basis commit | State |
|---|---|---|---|---|---|
| Dev Manager 1, `session_01MrcrmqtuENZ345mKfmsSWv` ("Glow Dev Manager") | 25 September 2026, 09:00 UTC | App Manager 3, at Nathan's direction | `claude/dev-manager` | `3888e8f635c4efdaf31cf074e1e423ff5f98de29` | DM-01 and DM-02 answered at 09:09 UTC (`0f55891`); DM-03 answered at 09:36 UTC (`23951c4`); Nathan's answers and directions recorded (`574ee0e` to `d945478`); idle since 25 September, 09:52 UTC, and available. DM-04 given to Nathan to carry on 26 September |

## Consultations

| ID | Sent | Requested by | Question | Report | Verdict | Disposition |
|---|---|---|---|---|---|---|
| DM-01 | 25 September 2026, 09:00 UTC, as the session's first prompt | Nathan, through App Manager 3 | **Process review:** how the project is managed and implemented | [DM-01 report](reviews/2026-09-25-dm-01-process-review.md) | Charter approved with conditions; record-keeping and handoffs: changes requested; relay, review paths and mistakes log approved with conditions; scorer referred to Nathan | Below |
| DM-02 | 25 September 2026, 09:00 UTC, as the session's first prompt | Nathan, through App Manager 3 | **Build review:** the state and direction of the application | [DM-02 report](reviews/2026-09-25-dm-02-build-review.md) | S15 reading approved with conditions; I2 scope: changes requested; database last, database placement and WordPress referred to Nathan; the rest approved with conditions | Below |
| DM-03 | 25 September 2026, 09:32 UTC, by a one-time Routine into the session | App Manager 3 | **Read before effect:** the governing Markdown in the batch at `fa4dc5f`, the DM-01 and DM-02 dispositions, and revision 2 of the P06.1-I1 review prompt | [DM-03 report](reviews/2026-09-25-dm-03-governing-read-and-i1-review-prompt.md) | Governing Markdown, the review prompt and the rest of the batch approved with conditions; the dispositions approved; no new questions for Nathan | Below |
| DM-04 | 26 September 2026, given to Nathan to carry (OD-25) | App Manager 3 | **Read before effect:** revision 1 of the P06.1-I2a implementation prompt, at `978ba19525f76c9aef9e326f973a739724ee3bb9` ([consultation](../../ephemeral/2026-09-26-dm-04-i2a-prompt-read.md)). It authorizes the Stream secret and live, destructive actions on the run's own data | Pending | Pending | Pending |

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

Neither blocks anything, so neither is put to Nathan again now.

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

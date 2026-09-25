# Dev Manager review log

This is the index of every consultation with the Dev Manager, its verdicts and the primary manager's dispositions. The role, the relay and the triggers are in the [Dev Manager charter](../../planning/dev-manager.md).

- The Dev Manager writes its reports in [`reviews/`](reviews/) and changes nothing else.
- The primary manager keeps this log. It records each consultation when it is sent, and each disposition when the report is integrated.
- Nathan decides wherever the two managers disagree, and his decision is recorded here.

## Sessions

| Session | Created | By | Branch | Basis commit | State |
|---|---|---|---|---|---|
| Dev Manager 1, `session_01MrcrmqtuENZ345mKfmsSWv` ("Glow Dev Manager") | 25 September 2026, 09:00 UTC | App Manager 3, at Nathan's direction | `claude/dev-manager` | `3888e8f635c4efdaf31cf074e1e423ff5f98de29` | DM-01 and DM-02 answered at 09:09 UTC (`0f55891`); available for DM-03 |

## Consultations

| ID | Sent | Requested by | Question | Report | Verdict | Disposition |
|---|---|---|---|---|---|---|
| DM-01 | 25 September 2026, 09:00 UTC, as the session's first prompt | Nathan, through App Manager 3 | **Process review:** how the project is managed and implemented | [DM-01 report](reviews/2026-09-25-dm-01-process-review.md) | Charter approved with conditions; record-keeping and handoffs: changes requested; relay, review paths and mistakes log approved with conditions; scorer referred to Nathan | Below |
| DM-02 | 25 September 2026, 09:00 UTC, as the session's first prompt | Nathan, through App Manager 3 | **Build review:** the state and direction of the application | [DM-02 report](reviews/2026-09-25-dm-02-build-review.md) | S15 reading approved with conditions; I2 scope: changes requested; database last, database placement and WordPress referred to Nathan; the rest approved with conditions | Below |

Both reviews are based on the [status and State of the App](../state-of-the-app.md) of 25 September 2026, at the basis commit above. The consultation text is the Dev Manager start prompt as it stood at that commit (`docs/ephemeral/2026-09-25-dev-manager-start-prompt.md`), with the commit filled in. The prompt now lives at [`docs/planning/start-prompts/dev-manager.md`](../../planning/start-prompts/dev-manager.md). Per Nathan, no new implementation task is created until the Dev Manager has responded and its reviews have been considered.

## Dispositions

The primary manager records here, for each report, every finding and approval item with its disposition: accepted, accepted with changes, declined with the reason, or referred to Nathan.

### DM-01 and DM-02 (App Manager 3, 25 September 2026)

App Manager 3 checked the facts it could against the repository before deciding. The contracts corpus test does import mobile source (B10). The review prompt did change after its review head was named (P2). Where App Manager 3 changed or deferred a recommendation, the reason is given here and the Dev Manager's own text stays in its report (P10).

**DM-01, process:**

| Finding | Dev Manager's weight | Disposition | Action |
|---|---|---|---|
| P1 Governing Markdown has no second reader | Before the next implementation task | **Accepted**, pending Nathan's answer to DM-01 question 2 | The Dev Manager reads governing Markdown before its PR merges, and any prompt that authorizes credential use or live provider actions before Nathan runs it. Charter triggers, manager workflow, CI policy and `AGENTS.md` updated. The first such read is DM-03 |
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
| B4 The shared logical database with HDE | Soon; Nathan decides | **Referred to Nathan** (DM-02 question 3) | App Manager 3 agrees with a separate logical database, with one refinement. Railway backs up volumes, so a platform restore covers every database on that PostgreSQL service; only a separate service fully separates platform restores. (Not re-checked against Railway's current documentation.) A separate logical database does separate ownership, grants, logical dumps and drops |
| B5 WordPress as the operator surface | Consider; Nathan decides | **Referred to Nathan** (DM-02 question 4) | Decide before the P07 brief |
| B6 The proof harness is tested outside CI | Before PR26 merges | **Accepted** | A Foundation job for the harness's offline checks joins P06.1-I2b, as full-scope work under the CI policy's workflow rule |
| B7 Stream with a display rule | Approved with conditions | **Accepted** | Conditions (a)–(d) added to the brief and ADR 0003. Billing recorded as an open launch gate (A04) |
| B8 Credentials in the shared environment | Consider; Nathan decides | **Referred to Nathan** (DM-02 question 5) | App Manager 3 recommends the split and a rotation of the development secret at P06.1's close |
| B9 Dependency advisories | Consider | **Accepted** | A one-line `npm audit` result in each phase's evidence (CI policy). The State of the App's description of GHSA-vcc3-ghjq-m6fr (it is `decode-uri-component` denial of service) is corrected at its next refresh, so the reviewed snapshot stays as reviewed. Dependabot alerts are Nathan's option |
| B10 Build and CI gaps | Soon | **Accepted**; the flake referred to Nathan (DM-01 question 1); HDE timing referred to Nathan (DM-02 question 6) | The install-order note added to local development. No further mobile mirroring of domain logic: P06.2 takes chat state from API-served fixtures (brief). The pre-merge checklist (P7) covers the advisory gate |

**Questions for Nathan**, relayed as the Dev Manager wrote them in its reports: DM-01 questions 1–4 and DM-02 questions 1–6. Their answers are recorded here when given.

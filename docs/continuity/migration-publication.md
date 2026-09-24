# M01 publication receipt

Prepared by App Planner 1 on 24 September 2026. This receipt records observed publication evidence for the Claude Code migration. It adds no feature assignment or operational permission. The [full handoff](claude-code-handoff.md) and [initiation prompt](../planning/claude-code-initiation.md) describe the verified code state in the migration tree below.

## Merged migration

| Identity | Verified value |
|---|---|
| Repository | Private `amthorn78/glow-dating-app` |
| Starting main / PR14 | `ea394543533e99f611158b9026a2bd01de8d09b3` |
| Starting tree | `b1676a034b416bf459daf41405e3b12b5d782f6e` |
| Migration PR | [PR15](https://github.com/amthorn78/glow-dating-app/pull/15) |
| Final reviewed candidate | `f0f5498ddf4ff614d11f03b627946196114d2d2f` |
| Candidate and merge tree | `d66288624de040eddcbe632fbd56e547f8f6beb2` |
| Actual merge/main | `dda09b3a05d725d93b5fe37d5364dfcd4ac212b1` |
| Merge UTC | 2026-09-24T14:17:13Z |
| Publication scope | 36 changed files; no application runtime/domain/contract source or dependency-lock changes |

The uploaded blobs and trees matched the local source snapshot. Publication used GitHub objects parented to the actual remote history; synthetic local snapshot history was never pushed. The merge's ordered parents are the starting main and final reviewed candidate above.

## Material and references

[The migration plan](../planning/claude-code-migration.md) contains the source-to-Markdown map. Established `docs/ephemeral/` for disposable prompts and `docs/planning/` for retained plans/briefs; retained `docs/pf-canon/`. [The documentation guide](../README.md) records naming, promotion and pruning rules.

Migrated complete dated copies of the Drive original brief/research, database-audit assignment and P05.3 assignment. Also captured the Notion database audit/catalog and final AB1-R012 closure in repository Markdown. Historical sources are provenance, not active instructions or imported prompt-library authority. PF00/PF01, README, current handoff, resource ownership, configuration, migration plan and ADR 0002 now point to current repository context. The Expo template license was renamed to `.md` with its bytes preserved. All repository prose documentation is Markdown; machine contracts, fixtures, locks and workflow/configuration files retain their required formats.

The full Claude handoff contains the codebase/data-flow map, exact environment inventory, Stream implementation facts and unresolved owner inputs. Safe API/mobile environment examples contain no credentials. `CLAUDE.md` entry points import applicable `AGENTS.md`; [the manager workflow](../planning/manager-workflow.md) specifies bounded one-off implementation sessions. Notion coordinates state and links; no Drive file is required to implement an assignment.

## CI and review acceptance

| Run | Exact source | Observed result |
|---|---|---|
| [Final PR 36010848051](https://github.com/amthorn78/glow-dating-app/actions/runs/36010848051) | `f0f5498ddf4ff614d11f03b627946196114d2d2f` | All six jobs succeeded |
| [Final push 36010840274](https://github.com/amthorn78/glow-dating-app/actions/runs/36010840274) | Same final candidate | All six jobs succeeded |
| [Merged main 36011687756](https://github.com/amthorn78/glow-dating-app/actions/runs/36011687756) | `dda09b3a05d725d93b5fe37d5364dfcd4ac212b1` | **Pending; do not treat main verification as complete** |

Candidate logs verified 83/83 browser cases, 516 mobile tests, 373 JavaScript contract cases, 250 API tests, 38 Python contract methods and eight scope-policy tests, plus development exports, lint/types, HTTP smoke and container checks. Merged-main completion will be recorded before this receipt is merged.

The four application jobs retain their names. `Change scope` and `Foundation gate` add classification and explicit final reporting. This migration changes behavior/workflows, so all six jobs ran. Skipped jobs in a later documentation-only change must not be described as test passes.

[The review summary](https://github.com/amthorn78/glow-dating-app/pull/15#issuecomment-5815214353) binds both final reviews to `f0f5498ddf4ff614d11f03b627946196114d2d2f`: code review completed at **2026-09-24T14:13:24.876617Z** and security at **2026-09-24T14:15:52.248983Z**. The [final security result](https://github.com/amthorn78/glow-dating-app/pull/15#issuecomment-5815838975) reports no security issues. No new final-head code findings were posted. All four review threads were resolved before merge: three implementation corrections and the documented enforcement-limit disposition below. The summary still displays the older runbook advisory; its linked thread is resolved and the final-head security result is the current evidence.

Review evidence is specific to the final candidate, not inherited from an earlier head. The external Codex service can still launch an agent; `AGENTS.md` requires it to classify before review and exit for ordinary documentation. No claim of zero invocations or zero cost is made. No personal/global/HDE review settings were changed. Branch protection retains the documented private-account limitation; the current branch-protection API read returned 403. Procedural checking is not platform enforcement.

## Corrections and earlier-run history

| Candidate | Outcome / disposition |
|---|---|
| `be733df96e152e950ffc65abcd2da9d630f0dac5` | [PR run 36007059155](https://github.com/amthorn78/glow-dating-app/actions/runs/36007059155) and [push run 36007010121](https://github.com/amthorn78/glow-dating-app/actions/runs/36007010121) succeeded. Code review found candidate Python executed before classification, allowing policy substitution. Green tests did not establish safe ordering. |
| `f75d8362c7f64cdb251ceebe7d6fe29e6096c621` | Moved classification to trusted base policy in isolated Python before candidate execution; moved candidate tests to the separate full-scope API job. [PR run 36007965450](https://github.com/amthorn78/glow-dating-app/actions/runs/36007965450) and [push run 36007957857](https://github.com/amthorn78/glow-dating-app/actions/runs/36007957857) were canceled after supersession. A no-major-issues code result covered only this intermediate head. One external review attempt returned “Unknown error”; it was not counted as acceptance. |
| `378052b317cb725d93f49477e0e73ad29f09f357` | Extended trusted-policy handling to AI review and feature pushes. [PR run 36008521291](https://github.com/amthorn78/glow-dating-app/actions/runs/36008521291) and [push run 36008513082](https://github.com/amthorn78/glow-dating-app/actions/runs/36008513082) succeeded. Code review found newly named implementation briefs could receive the documentation exemption. This candidate was not accepted. |
| `ff7ca9a1675e5f8cd12a297c272f3e0727536d46` | All planning became full scope. [PR run 36009518068](https://github.com/amthorn78/glow-dating-app/actions/runs/36009518068) and [push run 36009511962](https://github.com/amthorn78/glow-dating-app/actions/runs/36009511962) succeeded. Review identified the candidate-controlled workflow enforcement limit and the operational-runbook exemption. |
| `f0f5498ddf4ff614d11f03b627946196114d2d2f` | Replaced broad documentation exemption with explicit inert evidence/provenance. Recorded independent manager controls and the residual workflow/account enforcement limit. Final acceptance evidence is above. |

Three implementation corrections and one residual enforcement finding remain visible in PR15. The workflow-invocation finding is closed as a documented procedural-control/claim-boundary decision, not as a technically eliminated vulnerability. Candidate YAML can change its own gate; AGENTS requires the manager to independently classify, inspect the complete workflow diff and verify actual commands/steps/results before accepting full-scope changes. This migration introduces no immutable external gate. For this candidate the manager inspected the workflow and unchanged application commands and verified the actual full-scope job evidence. The first trusted policy is absent from the pre-migration base, which independently requires full checks. Trusted policy comes from PR base, preceding main for main pushes, or fetched main for feature pushes; a missing policy/comparison fails closed to full checks. No candidate Python/imports decide their own exemption. File modes, both sides of renamed paths, earlier code commits in mixed PRs, instructions and unknown paths are conservatively handled.

## Validation and limits

Local locked installs used Python 3.12.14, Node 24.19.0 and npm 11.9.0. Passed 250 API/domain/static tests, 38 Python contract methods, 516 mobile tests, 373 JavaScript contract cases, deterministic generation, API/mobile lint and types, actual HTTP smoke and port-ownership control. The eight classifier tests cover real Git histories, inert evidence/license add/edit/delete, operational/runbook/architecture/README/deferred-acceptance exclusions, code hidden behind a later docs commit, code-to-doc rename, behavior-changing Markdown/configuration, symlink/executable modes, invalid/empty bases, merge-base comparison and malicious candidate classifier/test/import substitution. A local first draft of the new regression contained a Python quoting syntax error; it was corrected before publication.

The verified environment inventory covers exact profile names, future secret slots, rejected connection names and explicit mobile/test/CI variables. The safe API example loads under the fixture guard. Markdown homes, active relative links, source recovery, template values and license-byte preservation were checked. Hosted evidence supplies browser, development JavaScript export and container validation; local Docker/native/device execution was not claimed. Test counts overlap.

No database connection, SQL/migration application, live Stream/HDE/provider call, Railway infrastructure mutation, deployment, paid activation or secret publication occurred. P01–P05 remain complete only at recorded preparation/fixture scope. P06–P12, live permissions/economics, persistence, native-device acceptance and release readiness remain open.

## Receipt publication

This receipt is an ordinary-documentation-only follow-up to the accepted migration. Its PR and merged-main workflow results provide the independent evidence for its own publication; a file cannot embed its own future commit identity. The expected path is two lightweight jobs succeeding and four application jobs explicitly skipped. Do not claim that expected result until observed in GitHub. The manager's completion comment and Notion coordination update link the actual follow-up checks without requiring another self-referential source update.

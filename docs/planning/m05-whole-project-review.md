# M05 — Whole-project review: an independent assessment toward completion

- **Work ID:** M05 (cross-cutting).
- **Owner:** Nathan Amthor, by his direction of 25 October 2026 (OD-48). **Manager:** App Manager 8. **Reviewer:** one review session, started by Nathan.
- **Revision 1, 25 October 2026.**
- **Starting point:** `main` at `5b9bcb1` (PR33's merge; P06.2 done), with the Markdown records of the manager branch `claude/magical-wozniak-yfmmx2` after it. The prompt names the exact commit the review reads.
- **Prompt:** [`docs/ephemeral/2026-10-25-m05-project-review-prompt.md`](../ephemeral/2026-10-25-m05-project-review-prompt.md).
- **Evidence home:** `docs/testing/evidence/2026-10-25-m05-project-review.md`, written by the review session on its own branch. The manager adds "Manager verification of M05", with a disposition for each finding.

## Why

Nathan, 25 October 2026, after PR33 merged (OD-48): *"I want you to submit a whole project review for independent assessment by a project reviewer session. It's job will be to make sure we are on track, correct any errors, and add anything that was missed to bring us to completion."*

The last whole picture is the [State of the App](../continuity/state-of-the-app.md), as of 25 September 2026. Since then, P06.1, P06.DB and P06.2 have run under the manual relay, through the Dev Manager's consultations DM-03 to DM-30 and many correction passes. No session has checked the project as a whole against PF01's completion since.

## Outcome

One review session reports, independent of the manager and of the Dev Manager:

1. **On track:** a verdict (on track, at risk or off track) against PF01's completion (P12), with its evidence, phase by phase.
2. **Errors:** every error found in code, tests, CI or records, numbered. An error inside the review's write scope is corrected on its branch and marked; any other gets an exact proposed correction or a recommended work item.
3. **What was missed:** everything completion needs that no plan, record or work item holds, each with a proposed home and owner. It is added directly where the write scope allows.
4. **The path to completion:** the ordered work items from now to P12, with their dependencies and external gates, Nathan's decisions in OD-32's form, and a recommendation for the next item.
5. **The process:** whether the manual relay, the Dev Manager, the review and correction cycles and the records are proportionate to what remains. This rests on measured facts, with proposed changes and no calendar promise (PF01 §11).

## Owned paths (the review session's)

- **It writes,** on its own session branch:
  - its evidence record;
  - corrections and additions in non-governing Markdown, each marked `[Corrected by M05, finding N: …]` or `[Added by M05, finding N]`, in:
    - `docs/architecture/`;
    - `docs/testing/`, including the [P11 plan](../testing/p11-deferred-acceptance.md); in `docs/testing/evidence/`, annotations only;
    - `docs/operations/`, except the CI policy;
    - `docs/planning/`, except the files listed under "It proposes only" and `sources/`.
- **It proposes only,** as exact text in its record, for:
  - governing Markdown: `AGENTS.md` and `CLAUDE.md` at any level, `docs/pf-canon/`, the manager workflow, the Dev Manager charter, the CI policy, the owner-direction register and `docs/planning/start-prompts/`;
  - `docs/README.md`, `docs/adr/` and the component READMEs;
  - the reasoning-strength matrix and its evidence, and the HDE contract request;
  - Notion, including new Work Register rows.
- **It never changes:**
  - any non-Markdown file;
  - anything under a `.claude/` directory;
  - `docs/continuity/` or `docs/ephemeral/`.

## Manager-owned

This brief; the handoff, the register, the mistakes log, the State of the App and the review log; Notion; every disposition.

## Exclusions

- **No code change.** A code defect is a finding with a recommended work item, so each code fix gets its own checks and exact-head review (the CI policy) and runs one item at a time (OD-29). Feature work stays paused (OD-05).
- **No live calls:** no call to Stream or any other provider, database, HDE or Railway; no `playwright install`, `eas` or `migrate`; no credential read or printed.
- **No external writes:** on GitHub, only its own branch's push (no PR, comment, re-run or dispatch); nothing written to Notion.

## Dependencies and inputs

PF00 and PF01; the repository at the prompt's commit; CI runs, read through the GitHub tools; Notion, read only, if the session has the connector. No credential is needed.

## Acceptance checks

- `git diff --name-only <prompt commit> <review head>` lists only the evidence record and paths inside the write scope.
- The trusted classifier, taken from `main`, prints `"reason": "ordinary-docs-only"` for that comparison.
- `git diff --check <prompt commit> <review head>` prints nothing.
- Each correction carries its marker and finding number, and the finding gives its evidence.
- The record holds the offline checks' exact results, and names any check not run with the reason.

## Classification expectation

The review's own change is ordinary documentation: Markdown only, with no `.claude/` path. So it runs no application CI and no code review. The manager reads every changed line when it integrates (workflow step 5). The Dev Manager reads any governing text before that text merges.

## Review plan

- **No Dev Manager read before it runs**, for three reasons:
  - the prompt authorizes no credential use and no live provider action, the charter's trigger;
  - the review's purpose and its authority to correct are Nathan's direction, not a choice of the manager's;
  - the review assesses the manager's and the Dev Manager's work, so neither shapes it before it reports.
- **After it reports:**
  - the manager verifies and integrates (workflow step 5) and records a disposition for each finding;
  - the governing proposals and the process recommendations go to the Dev Manager (OD-32; the charter), before anything governing merges;
  - Nathan's decisions go to him in OD-32's form, after the Dev Manager;
  - accepted work items enter the Work Register and run one at a time;
  - the manager refreshes the State of the App from the review.

## Sessions

- **Revision 1** (25 October 2026): the prompt is with Nathan, for `Glow App - No Stream`.

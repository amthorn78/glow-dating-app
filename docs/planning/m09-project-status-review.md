# M09 — Independent project status review: the app build's status and remaining work

- **Work ID:** M09 (cross-cutting).
- **Status:** the prompt is with Nathan.
- **Owner:** Nathan Amthor, by his direction of 18 November 2026 (OD-72). **Manager:** App Manager 12. **Reviewer:** one review session, started by Nathan.
- **Revision 1, 18 November 2026.**
- **Starting point:** `main` at `6edae78` (PR54's merge; SV2-R done), with the Markdown records of the manager branch `claude/magical-wozniak-yfmmx2` after it. The prompt names the exact commit the review reads.
- **Prompt:** [`docs/ephemeral/2026-11-18-m09-project-status-review-prompt.md`](../ephemeral/2026-11-18-m09-project-status-review-prompt.md).
- **Evidence home:** `docs/testing/evidence/<the session's date>-m09-project-status-review.md`, written by the review session on its own branch. The manager adds "Manager verification of M09", with a disposition for each finding.

## Why

Nathan, 18 November 2026, after SV2-R merged (OD-72): *"table those things, I want you to write an independent project review prompt. I need to know the status and remaining work for the app build."*

The last whole-project review was M05 (26 October 2026; [its record](../testing/evidence/2026-10-25-m05-project-review.md)), and the [State of the App](../continuity/state-of-the-app.md) is a snapshot from it. Since then SV1, SV2, SV3, P06.2-F, P06.3, M06 to M08, the A05 research items (A05-V to A05-V3, OD-68 to OD-71) and SV2-R have run. No session has measured the whole build since.

## Outcome

One review session reports, independent of the manager and of the Dev Manager:

1. **Status:** what is built and proven, part by part and phase by phase against PF01's plan, each claim checked against the code, the tests and the CI runs, and marked by how it was checked. It states plainly what a member could and could not do today, and what runs only on fixtures or a disposable database.
2. **Remaining work:** the ordered work items from now to PF01's completion (P12), each with its size in sessions or pull requests, its dependencies, its external gates (accounts, providers, legal advice, store rules) and Nathan's decisions still open. It names the critical path and a recommended next item. It gives no calendar promise (PF01 §11), but sizes each item and states its basis.
3. **Record accuracy:** every place where the handoff, the State of the App, PF01, the Work Register in Notion (read only, if the session has the connector), or a brief or record disagrees with the code or with another record, numbered, with the exact correction proposed.
4. **Risks:** what could stop or delay the launch, each with its likelihood, its effect and what would retire it.

## Owned paths (the review session's)

- **It writes,** on its own session branch, its evidence record only.
- **It proposes,** as exact text in its record, every correction to any other file or to Notion.
- **It never changes** any other file, anything in Notion, or anything on GitHub but its own branch's push.

## Manager-owned

This brief and the prompt; the handoff, the register, the mistakes log, the State of the App and the review log; Notion; every disposition.

## Exclusions

- **No change outside its record.** A defect or a stale record is a finding with a proposed correction; the manager disposes of each, and code fixes run as their own items, one at a time (OD-29).
- **No live calls:** no call to Stream or any other provider, database, HDE, Railway or Cloudflare; no `playwright install`, `eas` or `migrate`; no credential read or printed. Offline test suites may run in a scratch copy.
- **No external writes:** on GitHub, only its own branch's push (no pull request, comment, re-run or dispatch); nothing written to Notion.

## Dependencies and inputs

PF00, PF01 and PF02; the repository at the prompt's commit; CI runs, read through the GitHub tools; Notion, read only, if the session has the connector. No credential is needed.

## Acceptance checks

- `git diff --name-only <prompt commit> <review head>` lists only the evidence record.
- The trusted classifier, taken from `main`, prints `"reason": "ordinary-docs-only"` for that comparison.
- Every status claim says how it was checked (code read, test run, CI run, record only), and every remaining item gives its basis.

## Classification expectation

The review's own change is ordinary documentation: one Markdown file, outside any `.claude/` directory. It runs no application CI and no code review. The manager reads it whole when it integrates.

## Review plan

- **No Dev Manager read before it runs.** The prompt authorizes no credential use and no live provider action (the charter's trigger), the review is Nathan's direction, and it assesses the manager's and the Dev Manager's records, so neither shapes it first (as for M05).
- **After it reports:** the manager verifies its claims against the repository and integrates the record, with a disposition for each finding; proposed changes to governing text go to the Dev Manager before they merge (OD-32); Nathan's decisions go to him in OD-32's form; accepted work items enter the Work Register and run one at a time; the manager refreshes the State of the App from the review.
- **Tabled meanwhile** (OD-72): PF02's revision 1.8 and SV4's brief.

## Sessions

- **Revision 1** (18 November 2026): the prompt is with Nathan, for `Glow App - No Stream`.

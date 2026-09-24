# M02 — Claude setup and workflow optimization

Owner: Nathan Amthor. Managers: App Manager 1 (first Claude manager, 24 September 2026), handing over to App Manager 2. Starting main: `07b3b10720ddd333ada807a56595f369263714fe` (PR16), tree `fda515b624c4916dbb7d037beec8e276a62b2e3b`. Assignment: [initiation](claude-code-initiation.md) — review, then carry out the smallest useful app-only setup/instruction/workflow optimization. Feature work stays paused; P06.1 is not dispatched.

**Process:** manual relay ([manager workflow](manager-workflow.md)). The manager writes prompts. Nathan runs each implementation or review session himself and relays findings. The manager never starts that work itself, and implementation sessions may use any tools they need.

This file is the proposal and the persistent brief. Observed evidence is in [the M02 evidence record](../testing/evidence/2026-09-24-m02-claude-setup.md).

## Review result

**Verified by App Manager 1** (exact commands and results are in the evidence record):

- The documented checks pass on the pinned toolchain in a clean process environment: 250 API, 38 Python contract, 373 JavaScript contract, 516 mobile and 8 classifier tests, lint/types/format, static check, development export, both smoke harnesses and both `.env.example` templates. Root `CLAUDE.md` imports `AGENTS.md` correctly.
- The Claude cloud container does not provide the pinned toolchain. It has Python 3.11.15/3.12.3, Node 22.22.2 and npm 10.9.7, and no Docker daemon. Node 24.19.0 bundles npm 11.17.0, and `apps/mobile/.npmrc` sets `engine-strict`, so `npm ci` fails with `EBADENGINE` until npm 11.9.0 is installed. CI does this; `docs/operations/local-development.md` does not, and it cites a nonexistent `.node-version`.
- Under the default Trusted network level, `nodejs.org`, npm and PyPI are reachable, but `www.python.org` and `docs.expo.dev` are not. GitHub release assets from unattached repositories return 403. The preinstalled Chromium is revision 1194, while Playwright 1.62.1 expects 1234. The Playwright CDN is not on the Trusted list.
- App Manager 1's environment is shared with HDE work and injects `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` and `PORT` (names observed; values never read). The fixture API correctly refuses with `inherited_connection`. Nathan confirmed that a separate cloud environment needs only a new session.
- `apps/mobile/AGENTS.md` is Expo template guidance. It directs EAS build/submit/update and always using `npx expo install`, which conflicts with the release block, the authorization boundary and exact-pin discipline.
- Subagents receive project `CLAUDE.md`. `docs/planning/manager-workflow.md` had no templates, no exact classification command and no session mechanics.
- Accuracy defects: 21 broken relative links in `docs/continuity/history/p05-2-handoff.md`. The CI pin table omits `actions/upload-artifact`.
- Notion: 47 of 62 Work Register rows cite the historical Drive plan, D09 is not registered, A03 still shows Ready, and there is no M01/M02 row.

**Inherited plans (not re-proven):** P06.1 Stream proof, P11 persistence and live integration, and the A01/A07 HDE contract dependencies, as written in the Claude handoff and PF01.

**Unresolved:** The Setup script ran successfully as a manual run here (96 s fresh). Its first real run as an environment Setup script is verified by App Manager 2. Hosted CI for this change will exist only on its own PR heads. A broad sweep of the remaining architecture, testing and operations documents for stale statements was started as a read-only helper, then stopped before reporting; it produced no findings.

## Proposal — smallest useful optimization

1. **Dedicated app cloud environment** (owner setting): no variables; Custom network with the default list, `www.python.org` and `docs.expo.dev`; Setup script `scripts/bootstrap-toolchain.sh`. The HDE environment stays for HDE work.
2. **Pinned toolchain script:** Node 24.19.0 + npm 11.9.0 and CPython 3.12.14 from hash-verified downloads. It is idempotent and links into `$HOME/.local/bin` without replacing `python3`.
3. **Agent instructions:** the manual-relay process, roles, routing through the current handoff, the inherited-credential rule, the wrong-environment check, and repo-specific mobile commands with the release block.
4. **Setup documentation:** correct the pins and the npm and Python 3.12 steps. Add one Claude cloud section; no second setup guide.
5. **Manager workflow:** the manual relay, roles, templates, the exact classification command, and branch/integration mechanics.
6. **Continuity and accuracy:** handoffs, documentation map, initiation status, inventory pointer, CI pin row, repaired history links, evidence and the Notion sync.

Not proposed:

- A SessionStart hook to strip inherited variables. The dedicated environment makes it unnecessary.
- Editing the HDE environment. Its cache and time budget could affect HDE sessions.
- Pin or dependency changes, a Playwright browser download, Docker-extracted Python, or workflow and template changes. Both `.env.example` files were verified accurate.

## Owner action — dedicated environment settings

1. Create a cloud environment (suggested name `Glow app`).
2. Environment variables: only the Stream development application's `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET`, added at Nathan's direction on 24 September. These are recorded in the [environment inventory](../operations/environment-inventory.md); the secret is recorded by name only. Never copy HDE `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or `PORT` into it.
3. Set Network access to Custom: allowed domains `www.python.org`, `docs.expo.dev`, `*.stream-io-api.com` and `getstream.io`, with "Also include default list of common package managers" checked.
4. Paste the full `scripts/bootstrap-toolchain.sh` into Setup script, unchanged. It links by default. When its pins change, paste the new file again.
5. Start manager, implementation and review sessions for this repository in that environment.

## Completed directly by App Manager 1 (at Nathan's direction)

- `scripts/bootstrap-toolchain.sh`, needed to create the environment. The test is recorded in the evidence record.
- The manual relay: root `CLAUDE.md`, root `AGENTS.md`, `docs/planning/manager-workflow.md`, PF00 revision 1.4 (current session authority) and PF01 revision 1.5 (D09).
- The current handoff, this brief, the prompts and PR17.

- **Documentation exemption** (Nathan: "I do not want any docs paths checked for CI unless they contain scripts, which they should not", extended to the code review settings in `AGENTS.md`). `scripts/change_scope.py` now classifies any change made only of regular Markdown files as `ordinary-docs-only`: no application CI jobs, and no code/security review. Scripts, other non-Markdown files, symlinks, executable files and mixed changes stay full scope. The classifier tests, `AGENTS.md` Code Review Rules, CI policy, documentation guide, manager workflow and Claude handoff were updated to match. CI always loads the classifier from `main`, so later PRs gain the exemption only after M02 merges.

These edits are part of the M02 change and receive the same checks and exact-head review.

**Superseded attempt.** App Manager 1 first commissioned M02-I1 as a subagent in its own session. That session stopped at its start gate, because the harness based its worktree on `main`, and made no changes. Nathan then set the manual relay. No subagent implementation is part of M02.

## Implementation brief — M02-I1 (manual implementation session)

**Outcome:** the remaining repository items below, with evidence.

**Starting commit:** the head of the manager's branch named in the prompt's start gate.

**Owned paths (writable):**

- `scripts/bootstrap-toolchain.sh`: review and fix only. Report any change prominently, because Nathan must paste the new file into the environment.
- `services/api/tests/test_toolchain_pins.py` (new pin-drift test)
- `apps/mobile/AGENTS.md`
- `docs/operations/local-development.md`, `docs/operations/environment-inventory.md`, and the pin table in `docs/operations/ci-and-branch-policy.md`
- Environment, setup and inputs sections of `docs/continuity/claude-code-handoff.md`
- The initiation line of `docs/README.md` and a status header in `docs/planning/claude-code-initiation.md`
- Relative link paths only in `docs/continuity/history/p05-2-handoff.md`
- The implementer section of the evidence record

`README.md`, `services/api/README.md` and `apps/mobile/CLAUDE.md` may receive minimal accuracy or pointer edits only.

**Manager-owned (do not edit):**

- this brief, `docs/ephemeral/`, `docs/continuity/current-handoff.md`
- root `CLAUDE.md` and `AGENTS.md`, `docs/planning/manager-workflow.md`, PF canon
- Notion, PRs and merges

**Exclusions:**

- Application runtime, domain and contract code; mobile source; dependency manifests and locks
- `.env.example` files, workflows, `scripts/change_scope.py` and its tests, `Dockerfile`
- Anything affecting HDE; provider, database, Railway or deployment actions; credentials
- `playwright install`, `eas`, `migrate`

**Acceptance checks:**

1. **Setup-script result.** The environment's Setup script produced the linked toolchain with exact versions.
2. **Script checks.** `bash -n` passes. A fresh run into a temporary prefix and `HOME` works, and a rerun is idempotent. A wrong hash in a scratch copy fails before extraction.
3. **Pin-drift test.** It passes and demonstrably fails on a diverged pin.
4. **Full local suite.** It passes on the pinned toolchain; report the new API test count.
5. **Links and whitespace.** No broken relative links in changed Markdown, and `git diff --check` is clean.
6. **Classification.** Trusted-base classification reports full scope.

**Report:** branch, commit SHAs and tree, changed paths, exact commands with exit codes and counts, preserved failures, deviations and open questions. Durable results go in the evidence record's implementer section.

## Review and merge gates

1. Manager verification of the relayed report against the pushed branch.
2. Trusted-base classification (full scope).
3. An independent code and security review of the exact final head, in a review session Nathan runs from a manager prompt.
4. Hosted Foundation run on the PR head with all six jobs passing, plus manager inspection of the actual job steps.
5. Checked merge, verification of actual main, an ordinary-documentation receipt, the handoff and the Notion sync.

A new head needs its own review and checks.

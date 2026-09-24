# M02 — Claude setup and workflow optimization

Owner: Nathan Amthor. Manager: the first Claude Code manager session (24 September 2026). Starting main: `07b3b10720ddd333ada807a56595f369263714fe` (PR16), tree `fda515b624c4916dbb7d037beec8e276a62b2e3b`, no open PRs. Assignment: [initiation](claude-code-initiation.md) — review, then carry out the smallest useful app-only setup/instruction/workflow optimization. Feature work stays paused; P06.1 is not dispatched.

This file is the proposal and the persistent implementation brief. Observed evidence is in [the M02 evidence record](../testing/evidence/2026-09-24-m02-claude-setup.md).

## Review result

**Verified in this session** (exact commands and results are in the evidence record):

- The documented checks pass when they run on the pinned toolchain in a clean process environment: 250 API, 38 Python contract, 373 JavaScript contract, 516 mobile and 8 classifier tests, lint/types/format, static check, development export, both smoke harnesses and both `.env.example` templates. Root `CLAUDE.md` imports `AGENTS.md` correctly.
- The Claude cloud container does not provide the pinned toolchain. It has Python 3.11.15/3.12.3, Node 22.22.2 and npm 10.9.7, and no Docker daemon. Node 24.19.0 bundles npm 11.17.0, and `apps/mobile/.npmrc` sets `engine-strict`, so `npm ci` fails with `EBADENGINE` until npm 11.9.0 is installed. CI does this; `docs/operations/local-development.md` does not, and it cites a nonexistent `.node-version`.
- Under the default Trusted network level, `nodejs.org`, npm and PyPI are reachable, but `www.python.org` is not. GitHub release assets from unattached repositories return 403, so prebuilt Python distributions are unavailable; exact CPython 3.12.14 needs its signed source from `www.python.org`. The preinstalled Chromium is revision 1194, while Playwright 1.62.1 expects 1234. The Playwright CDN is not on the Trusted list.
- This session's environment is shared with HDE work. It injects `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` and `PORT` into every command (names observed; values never read). The fixture API correctly refuses with `inherited_connection`, and the root smoke harness exits 1. Nathan confirmed on 24 September that a separate cloud environment is possible; it requires starting a new session.
- `apps/mobile/AGENTS.md` is Expo template guidance. It directs EAS build/submit/update and always using `npx expo install`, which conflicts with the release block, the authorization boundary and exact-pin discipline.
- Subagents receive project `CLAUDE.md`. Its manager-only wording therefore reaches commissioned implementers.
- `docs/planning/manager-workflow.md` names the brief fields but has no template, no exact trusted-policy classification command and no Claude Code mechanics.
- Accuracy defects: 21 broken relative links in `docs/continuity/history/p05-2-handoff.md` (moved without path updates). The CI pin table omits `actions/upload-artifact`.
- Notion: 47 of 62 Work Register rows still cite the historical Drive plan, D09 is not registered, A03 still shows Ready, and there is no M01/M02 row.

**Inherited plans (not re-proven here):** the P06.1 Stream proof sequence, P11 persistence and live-integration obligations, and the A01/A07 HDE contract dependencies, as written in the Claude handoff and PF01.

**Unresolved assumptions:**

- Documentation does not say whether a cloud Setup script runs before the repository is cloned, so the setup content must be self-contained.
- The setup must fit the roughly five-minute budget. Here the Python build took about three minutes on four cores, and Node about 15 seconds.
- Hosted CI results for this change will exist only on its own PR head.

## Proposal — smallest useful optimization

1. **Dedicated app cloud environment** (owner setting; nothing in the repository enforces it). No environment variables. Network: Custom, with the default package-manager list plus `www.python.org`. Setup Script: the self-contained content of `scripts/bootstrap-toolchain.sh`, run with `--link`, to install the pinned toolchain once per cached environment. The HDE environment stays for HDE work.
2. **Pinned toolchain bootstrap script:** Node 24.19.0 + npm 11.9.0 and CPython 3.12.14, installed from SHA-256-pinned downloads (the pins come from signature-verified artifacts). The script is idempotent and Linux x86_64 only. Links go into `$HOME/.local/bin` only on request. The script never reads provider or database variables.
3. **Agent instructions:** role clarity for manager, implementer and reviewer; routing through the current handoff; an inherited-credential rule and a wrong-environment check; repo-specific mobile commands, dependency discipline and the release block.
4. **Setup documentation:** correct the pins, the npm step and the Python 3.12 venv step. Add one Claude cloud section covering the dedicated environment, the fallback for a wrong environment, and rendered-test limits. Keep existing files; add no second setup guide.
5. **Manager workflow:** session roles, brief and prompt templates, the exact classification command, commissioning mechanics (worktree agents, local branches, the manager pushes) and review/evidence homes.
6. **Continuity and accuracy:** handoffs, documentation map, initiation status, inventory pointer, CI pin row, repaired history links, the evidence record and the Notion sync.

Not proposed:

- A SessionStart hook that strips inherited variables. It is unnecessary once app sessions use their own environment, and it would add automatic behavior to every session. Keep it only as a fallback if environments cannot be separated.
- Editing the shared HDE environment. Its cache rebuild and time budget could affect HDE sessions.
- Changing pins or dependencies, downloading a Playwright browser, extracting Python from Docker, or changing workflows or templates. Both `.env.example` files were verified accurate and stay unchanged.

## Owner action — dedicated environment settings

1. Create a cloud environment (suggested name `Glow app`).
2. Leave Environment variables empty. Never copy HDE `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or `PORT` into it.
3. Set Network access to Custom: allowed domain `www.python.org`, with "Also include default list of common package managers" checked.
4. Paste the full content of `scripts/bootstrap-toolchain.sh` from merged main into Setup script, adding `--link` to its invocation line as the script's header instructs. When the script's pins change, paste it again.
5. Start app sessions in that environment. The first manager session verifies the result as described in the current handoff.

## Implementation brief — M02-I1

**Outcome:** items 2–6 in the repository, with evidence. The manager owns item 1's documentation text review and the Notion sync.

**Starting commit:** the manager commit on branch `claude/ecstatic-goodall-qajdh4` that publishes this brief. The exact SHA is given in the commissioning prompt and recorded in the evidence record.

**Owned paths (writable):**

- `CLAUDE.md`, `AGENTS.md`, `apps/mobile/AGENTS.md`
- `scripts/bootstrap-toolchain.sh` (new) and `services/api/tests/test_toolchain_pins.py` (new pin-drift test)
- `docs/operations/local-development.md`, `docs/operations/environment-inventory.md`, and the pin table in `docs/operations/ci-and-branch-policy.md`
- `docs/planning/manager-workflow.md`
- Environment, setup and inputs sections of `docs/continuity/claude-code-handoff.md`
- The initiation line of `docs/README.md` and a status header in `docs/planning/claude-code-initiation.md`
- Relative link paths only in `docs/continuity/history/p05-2-handoff.md`
- The implementer section of the evidence record

`README.md`, `services/api/README.md` and `apps/mobile/CLAUDE.md` may receive minimal accuracy or pointer edits only.

**Manager-owned (do not edit):** this brief, `docs/ephemeral/`, `docs/continuity/current-handoff.md`, Notion, the remote branch and the PR.

**Exclusions:**

- Application runtime, domain and contract code; mobile source; dependency manifests and locks
- `.env.example` files, `.github/workflows/`, `scripts/change_scope.py` and its tests, `Dockerfile`, PF canon
- Anything affecting HDE; provider, database, Railway or deployment actions; credentials
- `playwright install`, `eas`, `migrate`
- Pushes, PRs and Notion writes

**Acceptance checks:**

1. `bash -n` passes. A fresh install into a temporary prefix and `HOME` with `--link` yields exactly Node 24.19.0, npm 11.9.0 and Python 3.12.14. A rerun is idempotent. A deliberately wrong hash in a scratch copy fails before extraction. The script prints no environment values.
2. The pin-drift test passes and fails meaningfully when a pin diverges; show this with a scratch copy or a reasoned manual check.
3. The full local suite passes in a clean process environment with the bootstrapped toolchain, including the new test count.
4. No broken relative links in changed Markdown, and `git diff --check` is clean.
5. Trusted-base classification of the whole change reports full scope.

**Report:** changed paths, commit SHA/tree, exact commands with exit codes and counts, preserved failures, limitations and open questions. Durable results go in the evidence record's implementer section.

## Review and merge gates

1. Manager diff review.
2. Trusted-base classification (full scope expected).
3. An independent bounded code and security review of the exact final head.
4. Hosted Foundation run on the PR head with all six jobs passing, plus manager inspection of actual job steps.
5. Checked merge, verification of actual main, then an ordinary-documentation receipt.

Findings go back to the implementer, and a new head needs its own review and checks.

# M02-I1 commissioning prompt — Claude setup implementation

- **Owner:** Claude manager session (Nathan Amthor is product/account owner).
- **Durable brief:** [M02 brief](../planning/claude-setup-optimization.md). Evidence: [M02 evidence record](../testing/evidence/2026-09-24-m02-claude-setup.md).
- **Deletion condition:** prune after M02 closes and the brief and evidence record hold every accepted result.

---

You are **implementation session M02-I1** for the Glow dating app, private repository `amthorn78/glow-dating-app`. You are not the manager: do not commission sessions, push, open PRs, merge or write to Notion.

Work only in your assigned worktree. Start from the commit the manager names in the commissioning message; verify it with `git log -1` before editing. Commit locally on your worktree branch with clear messages. Read root `AGENTS.md`, `docs/README.md`, the M02 brief (above) and the evidence record before editing, and read `apps/mobile/AGENTS.md` before changing it.

## Environment rules (mandatory)

This session runs in a cloud environment shared with HDE work. Every process inherits `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` and `PORT`.

- Never read, print, echo, copy or use their values. Never run `env`, `printenv`, `set` or anything else that dumps the environment. Check names only if needed.
- Run every application command in a clean process environment, for example `env -i HOME="$HOME" PATH="<pinned bins>:/usr/bin:/bin" LANG=C.UTF-8 <command>`. Add only non-secret variables that the command needs (for example `GLOW_ENV=test`, `EXPO_OFFLINE=1`, `PYTHONPATH=.`, `GLOW_SMOKE_PYTHON=...`). Network installs through the proxy also need the proxy/CA variables (`HTTPS_PROXY`, `NODE_EXTRA_CA_CERTS`, `SSL_CERT_FILE`, `REQUESTS_CA_BUNDLE`); pass those through by name only when installing.
- The fixture API refusing with `inherited_connection` is correct behavior. Never weaken a guard.
- No database, provider, HDE, Railway or deployment access.
- Do not run `playwright install`, `eas` or `migrate`.
- The rendered browser suite is not required. Hosted CI provides it.

## Deliverables (owned paths only — see the brief)

1. **`scripts/bootstrap-toolchain.sh`** (new, executable, `set -euo pipefail`). Installs Node 24.19.0 with npm 11.9.0 and CPython 3.12.14 into `--prefix DIR`, defaulting to `$HOME/.local/share/glow-app-toolchain`.
   - **Downloads:** `https://nodejs.org/dist/v24.19.0/node-v24.19.0-linux-x64.tar.xz` (SHA-256 `14b342e71204f811bde6153be8e04b62aef63c236fef92b55f9c83154b409647`) and `https://www.python.org/ftp/python/3.12.14/Python-3.12.14.tgz` (SHA-256 `6c6df908d2c3fd24e6d76869e92542abd0f33aec9dfc18df8875f89660286d43`). Pin both hashes in the script, fetch over HTTPS with retries into a temporary directory, and verify before extracting.
   - **npm:** install `npm@11.9.0` with the new Node's npm.
   - **Python build:** `--with-ensurepip=install`, `make -j"$(nproc)"`. Then verify that `ssl`, `sqlite3`, `ctypes`, `lzma`, `bz2` and `zlib` import.
   - **Idempotence:** skip components already installed with exact versions.
   - **`--link` option:** creates `node`, `npm`, `npx` and `python3.12` symlinks in `$HOME/.local/bin`. Do not create or shadow `python3` or `python`.
   - **Platform:** refuse anything other than Linux x86_64, with a pointer to `docs/operations/local-development.md`.
   - **Pin check:** when the script runs from a repository checkout, compare its pins with `services/api/.python-version` and the `engines` in both `package.json` files. Skip the check silently when run from outside a checkout.
   - **Output:** final versions, plus PATH guidance when not linked. No GLOW_-prefixed or other environment-variable configuration. No environment output.
   - **Header comment:** usage, provenance (link to the evidence record's verification table), and setup-script usage. For the Setup script, paste the whole file and change its final line `main "$@"` to `main --link`. The whole run takes about 3–4 minutes, within the roughly five-minute Setup-script budget.
2. **`services/api/tests/test_toolchain_pins.py`** (new; must be discovered by `manage.py test tests`). Statically assert that the pins agree across the bootstrap script, `services/api/.python-version`, both `package.json` `engines`, `.github/workflows/foundation.yml` (`python-version`, `node-version`, `npm@...`) and the `Dockerfile` Python tag. Never execute the script.
3. **Instructions**
   - **Root `CLAUDE.md`** (keep `@AGENTS.md`, keep it short):
     - Current work is routed by `docs/continuity/current-handoff.md`.
     - Roles: the session Nathan starts is the manager; a session started from a `docs/ephemeral/` prompt is an implementation or review session bound to that prompt's owned paths, which never pushes, merges or commissions.
     - App sessions belong in the dedicated app cloud environment. If `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` names are present, the session is in the HDE-shared environment: say so, never read or use the values, and run app commands only in a clean process environment.
     - Pinned toolchain via `scripts/bootstrap-toolchain.sh`; the API venv uses `python3.12`.
   - **Root `AGENTS.md`:** add one inherited-credential rule for all agents (never read, print, copy or use inherited credentials or connection values; app processes run without them). Change "New features are paused for the migration/setup optimization" to "New feature work stays paused until Nathan's recorded direction in the current handoff resumes it". Leave Code Review Rules unchanged.
   - **`apps/mobile/AGENTS.md`:** keep the "Expo has changed" versioned-docs guidance and the routing/native-directory rules. Replace generic commands with this repository's commands:
     - `npm start` / `npm run android|ios` wrappers, `npm run check`, `EXPO_OFFLINE=1 npm run check:expo`, `EXPO_OFFLINE=1 npm run export:development`, `npm run test:rendered` (hosted CI in cloud sessions).
     - Dependency changes only when an assignment requires them: `npx expo install` to select SDK-compatible versions, then exact pins, `npm ci --ignore-scripts`, a reviewed lockfile and `dependency-inventory.json` update.
     - Replace the EAS section with the release block: no EAS project, signing, store submission or OTA update is configured or authorized; `app.config.ts` rejects non-development builds.
4. **`docs/operations/local-development.md`**
   - Correct the pin sources.
   - Add the explicit `npm install --global npm@11.9.0` step and explain why (`EBADENGINE`).
   - Create the API venv with `python3.12` after a version check.
   - Add one "Claude Code cloud sessions" section: the dedicated app environment settings from the brief's owner-action list (no variables; Custom network with the default list plus `www.python.org`; the Setup script from the bootstrap script with `main --link`), first-session verification (versions; no HDE variable names), wrong-environment fallback (`env -i` pattern and the rule never to print values), per-worktree installs, and rendered-test limits (preinstalled Chromium revision 1194 is not the pinned 1234; hosted CI is the evidence; never `playwright install` in the cloud container).
5. **Other docs**
   - **`docs/operations/environment-inventory.md`:** one pointer to the cloud-environment section.
   - **`docs/operations/ci-and-branch-policy.md`:** add the `actions/upload-artifact` row (`ea165f8d65b6e75b540449e92b4886f43607fa02`, workflow comment `v4`; exact patch release not verified).
   - **`docs/continuity/claude-code-handoff.md`:**
     - Local setup paragraph: mention the bootstrap script and the dedicated environment.
     - Environment inventory: add a short "Claude cloud environment" subsection covering observed shared-environment names, the dedicated-environment rule and the residual risk, and note that the tooling variables the bootstrap script reads are just `HOME` and `PATH`.
     - Prioritized input 1: Claude access is provided; the dedicated environment is an owner setting.
   - **`docs/README.md`:** the initiation line becomes "records the executed first manager assignment; new sessions start from the current handoff".
   - **`docs/planning/claude-code-initiation.md`:** add a status line under the title: executed 24 September 2026 by the first manager session (M02); retained as provenance; do not re-run.
   - **`docs/continuity/history/p05-2-handoff.md`:** fix relative link paths only.
6. **`docs/planning/manager-workflow.md`** (concise additions; keep existing rules):
   - Session roles.
   - Brief template fields: work ID, starting commit/branch, outcome, owned paths, manager-owned paths, exclusions, acceptance checks, classification expectation, evidence home, report format, dependencies.
   - Commissioning-prompt contents and deletion condition.
   - Claude Code mechanics: Agent tool with worktree isolation for writers; one writer per owned-path set; per-worktree installs; the implementer commits locally; the manager merges into its designated branch and pushes; reviewers are read-only at the exact head.
   - The exact trusted-policy classification command:

     ```bash
     git fetch origin main
     base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
     policy_dir=$(mktemp -d)
     git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
     python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
     ```

     Use the PR's base SHA when it differs.
   - Evidence homes: `docs/testing/evidence/` for inert records and receipts.
   - Close-out: handoff, Notion row/page and ephemeral pruning.
7. **Evidence:** fill "Implementation session" in the evidence record with exact commands, exit codes, counts, versions, timings, failures and limits. Observations only, no instructions.

## Checks (run all, report exact results)

1. `bash -n scripts/bootstrap-toolchain.sh`.
2. Bootstrap tests: a fresh run into a temporary prefix with a temporary `HOME` and `--link`; the versions through the links; an idempotent rerun with timing; a scratch copy with a corrupted expected hash failing before extraction; `grep` confirming that the script contains no `env`/`printenv` dumps.
3. The full suite in a clean environment using your freshly bootstrapped toolchain:
   - Classifier tests.
   - API: `pip install --require-hashes`, `pip check`, `manage.py check`, `manage.py test tests` (report the new count), ruff, format, mypy, contract tests, `static_check`, `smoke.py`.
   - `npm ci --ignore-scripts` for mobile and contracts; `npm run check` in both.
   - Mobile `EXPO_OFFLINE=1 npm run check:expo` and export.
   - Root `node scripts/smoke.mjs` and `node --test scripts/smoke.test.mjs`.
4. The pin-drift test fails when one pin is changed in a scratch copy of the tree or through an equivalent temporary edit that you revert. Show the failure message.
5. Relative-link check over every changed Markdown file; `git diff --check`.
6. The trusted-base classification command above (expect `full=true`).

## Report back (final message)

- Worktree path, branch, commit SHA(s) and final tree.
- Changed paths.
- Before/after behavior.
- Every check with its exact result.
- Failures and how they were resolved.
- Deviations from the brief and why.
- Open questions and limitations.

Keep evidence honest: skipped or unavailable checks are not passes.

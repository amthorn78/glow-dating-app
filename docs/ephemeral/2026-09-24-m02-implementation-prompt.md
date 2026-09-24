# M02-I1 implementation prompt — Claude setup implementation

- **Owner:** the current Claude manager (App Manager 2). Nathan starts this session manually and relays its report.
- **Durable brief:** [M02 brief](../planning/claude-setup-optimization.md), section "Implementation brief — M02-I1". Evidence: [M02 evidence record](../testing/evidence/2026-09-24-m02-claude-setup.md).
- **Deletion condition:** prune after M02 closes and the brief and evidence record hold every accepted result.

**Manager:** before giving this prompt to Nathan, replace `<MANAGER_BRANCH>` and `<START_SHA>` with your pushed branch and its head SHA.

**Revision:** App Manager 2, 24 September 2026. It adds the `main`-instructions note, the Node-tree ownership finding from the environment's first Setup-script run, the mobile-test exclusion, the intermittent rendered failure and the network fact for clean-environment runs.

---

You are **implementation session M02-I1** for the Glow dating app, private repository `amthorn78/glow-dating-app`.

- Nathan started you manually. He will relay your report to the manager (App Manager 2). You are not the manager.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- Your boundaries concern scope: stay within the owned paths, work on your own session branch, and report as below.
- The `CLAUDE.md` loaded when your session started comes from `main`. It is older and describes the first *manager* assignment. After the start gate, the branch versions of `CLAUDE.md` and `AGENTS.md` govern. Do not re-run `docs/planning/claude-code-initiation.md`. Do not take on manager duties: writing prompts for Nathan, opening or merging PRs, and updating Notion.

## 1. Environment check (names only; never print values)

1. Confirm that none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` is set. Check names only, for example `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, you are in the wrong environment: stop and report. The environment also sets `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` for Nathan's development Stream application (see `docs/operations/environment-inventory.md`). They are not used by M02; never print or copy the secret.
2. Confirm the Setup script's toolchain: `command -v node npm npx python3.12` should resolve to `$HOME/.local/bin`, with `node --version` = v24.19.0, `npm --version` = 11.9.0 and `python3.12 --version` = Python 3.12.14. Record the results.
3. Never run commands that dump the environment. Never connect to a database, provider, HDE or Railway. Never run `playwright install`, `eas` or `migrate`.

## 2. Start gate

```bash
git fetch origin <MANAGER_BRANCH>
git merge --ff-only <START_SHA>
git rev-parse HEAD   # must print <START_SHA>
```

If the fast-forward or the check fails, stop and report. Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`
- `docs/README.md`
- the M02 brief and evidence record
- `docs/planning/manager-workflow.md`
- `docs/operations/local-development.md` and `docs/operations/ci-and-branch-policy.md`
- `apps/mobile/AGENTS.md` and `apps/mobile/README.md`
- `docs/continuity/claude-code-handoff.md`
- `.github/workflows/foundation.yml`
- `scripts/bootstrap-toolchain.sh` and `scripts/change_scope.py`

## 3. Deliverables (owned paths only — see the brief)

1. **Validate `scripts/bootstrap-toolchain.sh`**, which the manager wrote and tested once. Review it for correctness, security and idempotence. Fix only real defects. Any change means Nathan must paste the new file into the environment's Setup script, so report changes prominently.

   **Known finding (App Manager 2, from the environment's first real Setup-script run).** Everything under `$HOME/.local/share/glow-app-toolchain/node-v24.19.0-linux-x64/`, including `bin/node`, is owned by uid:gid 1000:1000. That is the `ubuntu` account in this container. The cause is that `tar` running as root keeps the archive's numeric owners. Root executes those binaries, and a non-root account can replace them. The npm install and the Python install are root-owned. Treat this as a defect unless you show otherwise:

   - fix the extraction, for example with `tar --no-same-owner`;
   - decide whether the already-installed fast path must detect or repair a wrongly owned tree, because an existing install is otherwise kept as is;
   - check that nothing else the script installs keeps foreign ownership.
2. **`services/api/tests/test_toolchain_pins.py`** (new; must be discovered by `manage.py test tests`). Statically assert that the pins agree:
   - the Node, npm and Python pins in the script;
   - `services/api/.python-version`;
   - the `engines` in `apps/mobile/package.json` and `packages/contracts/package.json`;
   - `.github/workflows/foundation.yml` (`python-version`, `node-version`, `npm@...`);
   - the Python tag in the `Dockerfile`.

   Never execute the script. Make the failure message name the diverging file.
3. **`apps/mobile/AGENTS.md`.** Keep the "Expo has changed" versioned-docs guidance and the Router/native-directory rules. Replace the generic commands and EAS section:
   - **Commands:** `npm start` / `npm run android|ios` wrappers, `npm run check`, `EXPO_OFFLINE=1 npm run check:expo`, `EXPO_OFFLINE=1 npm run export:development`, and `npm run test:rendered`. In cloud sessions, the rendered suite's pinned-browser evidence comes from hosted CI.
   - **Dependency changes:** only when an assignment requires them. Use `npx expo install` to choose SDK-compatible versions, then exact pins, `npm ci --ignore-scripts`, a reviewed lockfile and a `dependency-inventory.json` update.
   - **Release block:** no EAS project, signing, store submission or OTA update is configured or authorized, and `app.config.ts` rejects non-development builds.
4. **`docs/operations/local-development.md`**
   - Correct the pin sources: `services/api/.python-version`, package `engines`, the workflow and the Dockerfile. There is no `.node-version`.
   - Add the explicit `npm install --global npm@11.9.0` step and explain `EBADENGINE`.
   - Create the API venv with `python3.12` after a version check.
   - Add one "Claude Code cloud sessions" section covering:
     - the dedicated environment settings (from the brief's owner action) and the Setup script;
     - first-session verification;
     - per-branch installs (`node_modules`, `.venv`);
     - the wrong-environment fallback: a clean process environment such as `env -i HOME="$HOME" PATH="$PATH" LANG=C.UTF-8 …`, never printing values, and the refusal is correct behavior;
     - rendered-test limits: the preinstalled Chromium is revision 1194, not the pinned 1234; hosted CI is the evidence; never `playwright install` in the cloud container.
5. **Other docs**
   - **`docs/operations/environment-inventory.md`:** it already records the `Glow app` environment and Stream development application (manager-written). Keep that section; link it from local-development instead of duplicating it.
   - **`docs/operations/ci-and-branch-policy.md`:** add the `actions/upload-artifact` row (`ea165f8d65b6e75b540449e92b4886f43607fa02`, workflow comment `v4`; exact patch release not verified).
   - **`docs/continuity/claude-code-handoff.md`:**
     - Local setup: the bootstrap script and the dedicated environment.
     - Environment inventory: add a short "Claude cloud environments" subsection — the HDE-shared environment's observed names, the dedicated-environment rule, and the residual risk that any command in an environment can read that environment's variables. The script reads only `HOME` and `PATH`.
     - Prioritized input 1: Claude access is provided; the dedicated environment is an owner setting.
   - **`docs/README.md`:** make the initiation line read "records the executed first manager assignment; new sessions start from the current handoff".
   - **`docs/planning/claude-code-initiation.md`:** add a status line under the title: executed 24 September 2026 by App Manager 1 (M02); retained as provenance; do not re-run.
   - **`docs/continuity/history/p05-2-handoff.md`:** fix relative link paths only.
6. **Evidence record:** fill the "Implementation session" section with environment check results, exact commands, exit codes, counts, versions, timings, failures and limits. Record observations only, never instructions.

Do not edit manager-owned files: the brief, `docs/ephemeral/`, `docs/continuity/current-handoff.md`, root `CLAUDE.md` and `AGENTS.md`, `docs/planning/manager-workflow.md` and PF canon. Do not edit application code, mobile tests (including `apps/mobile/rendered/`), dependency manifests or locks, `.env.example` files, workflows, `scripts/change_scope.py` or its tests, or the `Dockerfile`.

**Known intermittent failure (outside M02 scope).** Hosted CI has twice failed the rendered case `rendered/state-corrections.spec.ts:45` ("eligibility correction replaces an obsolete unsaved birth draft"). Each time the page stayed on eligibility with an alert visible.

- The occurrences were [PR run 36020836838](https://github.com/amthorn78/glow-dating-app/actions/runs/36020836838) on an M02 head and PR14's first PR attempt ([AB1-R012](../continuity/history/AB1-R012.md)). The root cause is unknown.
- Do not change tests or source to address it.
- The rendered suite is optional here and informational only, because the container's Chromium is not the pinned browser. If you run it, record the result as an observation.

## 4. Checks (report exact results)

1. `bash -n scripts/bootstrap-toolchain.sh`.
2. Script runs:
   - a fresh run into a temporary directory with a temporary `HOME` (`env -i HOME=<tmp> PATH=/usr/bin:/bin bash scripts/bootstrap-toolchain.sh`), recording versions and timing. In this environment, direct HTTPS to nodejs.org, www.python.org and registry.npmjs.org worked under `env -i` without proxy variables (App Manager 2, 24 September);
   - the owner and group of every installed tree after the fresh run (for example `stat -c '%u:%g %n'`), before and after your ownership fix;
   - an idempotent rerun;
   - a scratch copy with a wrong hash, which must fail before extraction.
3. The pin-drift test passes, then fails when a pin is changed through a temporary, reverted edit. Show the message.
4. The full suite on the pinned toolchain:
   - classifier tests;
   - API: `pip install --require-hashes`, `pip check`, `manage.py check`, `manage.py test tests` (report the new count), ruff, format, mypy, contract tests, `static_check`, `smoke.py`;
   - `npm ci --ignore-scripts` and `npm run check` for both packages;
   - mobile `EXPO_OFFLINE=1` `check:expo` and export;
   - root `node scripts/smoke.mjs` and `node --test scripts/smoke.test.mjs`.
5. A relative-link check over every changed Markdown file, and `git diff --check`.
6. Trusted-base classification (command in `docs/planning/manager-workflow.md`); expect full scope.

## 5. Finish and report

Commit with clear messages and push your own session branch. Do not open or merge PRs, and do not update Notion; the manager integrates.

Your final message is the report Nathan relays:

- branch, commit SHAs and final tree;
- changed paths;
- before/after behavior;
- every check with its exact result;
- failures and their resolution;
- whether `scripts/bootstrap-toolchain.sh` changed (re-paste needed), and how you handled the Node-tree ownership finding, including whether an existing install is repaired or re-extracted;
- deviations from the brief;
- open questions and limitations.

Skipped or unavailable checks are not passes.

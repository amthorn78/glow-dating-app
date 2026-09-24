# M02-C1 correction prompt — fix the review findings on PR18

- **Owner:** App Manager 2. Nathan starts this session manually and relays its report.
- **Durable brief:** [M02 brief](../planning/claude-setup-optimization.md), sections "Exact-head review of `ccebd1b` and its disposition" and "Correction brief — M02-C1". Evidence: [M02 evidence record](../testing/evidence/2026-09-24-m02-claude-setup.md).
- **Deletion condition:** prune after M02 closes and the brief and evidence record hold every accepted result.

**Manager:** before giving this prompt to Nathan, replace `<MANAGER_BRANCH>` and `<START_SHA>` with your pushed branch and its head SHA.

---

You are **implementation session M02-C1** for the Glow dating app, private repository `amthorn78/glow-dating-app`. You fix the findings of an independent review of PR18.

- Nathan started you manually and will relay your report to the manager (App Manager 2). You are not the manager.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- Your boundaries concern scope: stay within the owned paths, work on your own session branch, and report as below.
- The `CLAUDE.md` loaded when your session started comes from `main` and is older. After the start gate, the branch versions of `CLAUDE.md` and `AGENTS.md` govern.
- Do not re-run `docs/planning/claude-code-initiation.md`. Do not take on manager duties: writing prompts for Nathan, opening or merging PRs, and updating Notion.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` may be set. Check names only: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` are set for Nathan's development Stream application. They are not used here. Never print or copy the secret.
3. Record `command -v node npm npx python3.12` and their versions. Expected: v24.19.0, 11.9.0 and Python 3.12.14, from `$HOME/.local/bin`.
4. Never dump the environment. Never connect to a database, provider, HDE or Railway. Never run `playwright install`, `eas` or `migrate`.
5. For `npm` in a clean process environment, pass `HTTPS_PROXY` and `NODE_EXTRA_CA_CERTS` through by reference, never printed; see `docs/operations/local-development.md`.

## 2. Start gate

```bash
git fetch origin <MANAGER_BRANCH>
git merge --ff-only <START_SHA>
git rev-parse HEAD   # must print <START_SHA>
```

If the fast-forward or the check fails, stop and report. Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`;
- the M02 brief, `docs/planning/claude-setup-optimization.md`: the whole file, and especially the two sections named above;
- the evidence record, `docs/testing/evidence/2026-09-24-m02-claude-setup.md`, including the sections "Implementation session" and "App Manager 2 — exact-head review relay";
- `docs/operations/ci-and-branch-policy.md` and `docs/operations/local-development.md`;
- `.github/workflows/foundation.yml`;
- `scripts/bootstrap-toolchain.sh`, `scripts/change_scope.py`, `scripts/test_change_scope.py` and `services/api/tests/test_toolchain_pins.py`.

## 3. Deliverables (owned paths only)

Numbers refer to the review findings in the brief's disposition table.

### `scripts/bootstrap-toolchain.sh` (findings 1, 8, 9, 10 and the timing text of 13)

Keep the trust model the script states: everything installed belongs to the running account, nothing is group- or world-writable, no symlink leaves its tree, and nothing inside a tree runs before the tree passes that check. Pins, hashes and URLs stay unchanged.

1. **Symlinks (1).** `trusted_tree` must reject:
   - a tree root that is itself a symlink;
   - any symlink inside the tree that dangles or whose resolved target lies outside the tree's real path.

   The real trees must still pass:
   - The Node tree has 12 relative symlinks, such as `bin/corepack` and the `.bin/` entries under `lib/node_modules/npm/node_modules`.
   - The Python tree has 8, such as `bin/python3 -> python3.12`.
   - All of them resolve inside their tree.
2. **Isolated Python (8).** Run both standard-library checks with `python3.12 -I`, so `PYTHONPATH`, the working directory and user site-packages cannot satisfy them. That means the already-installed check and the post-build check.
3. **Directories (9).** Refuse, with a clear error, a prefix directory or a link directory (`$HOME/.local/bin`) that:
   - is not owned by the running account;
   - is writable by group or others;
   - is a symlink, where that matters.

   Decide, and explain in the report, whether parent directories need the same check. In this environment `/root` is mode 700, and `/root/.local`, `/root/.local/bin`, `/root/.local/share` and the default prefix are root-owned with mode 755.
4. **Robustness (10):**
   - Resolve the prefix without `CDPATH` effects, for example `CDPATH= cd -- "$prefix" && pwd -P`.
   - Make `curl` ignore `~/.curlrc` (`-q` must be its first option). Add a connection timeout and stall protection, and do not add a total time limit that could fail a slow but working download.
   - Make `SIGINT` and `SIGTERM` stop child processes and still remove the temporary directory. Report whether anything remains after a `SIGTERM` during the Python build.
   - Install npm through the tree's own `bin/npm`.
5. **Timing text (13):** the header and log lines should say the first run takes about two minutes. The measurements were 91–128 s.

**The script changes, so Nathan must paste it again.** That happens once, after M02 merges; the manager arranges it. Report it prominently.

### `scripts/change_scope.py` and `scripts/test_change_scope.py` (findings 3 and 7)

These rules apply to later PRs once M02 merges, because CI loads the classifier from `main`. Both must fail closed.

1. **Merge bases (3).** With `--merge-base`, use `git merge-base --all`. More than one base means full scope, with a reason naming it, such as `multiple-merge-bases`. Add a regression test that builds a criss-cross history in the test's scratch repository, and keep a test showing the single-base case still works.
2. **`.claude` (7, Nathan's decision).** Any path with a component named `.claude` is full scope. Examples: `.claude/agents/helper.md`, `.claude/skills/x/SKILL.md`, `docs/.claude/x.md`.
   - Ordinary Markdown, including `AGENTS.md` and `CLAUDE.md`, stays ordinary under Nathan's exemption.
   - Add tests for both.
   - Update the comment at the top of the classifier.
3. **Existing tests.** Keep every existing test passing: the symlink and executable cases, renamed and hidden code, trusted-policy substitution, fail-closed behavior, merge-base handling, and Markdown anywhere.

### `services/api/tests/test_toolchain_pins.py` (finding 6)

- **Patterns.** Accept single, double or no quotes, for example `python-version:\s*['"]?([^'"\s#]+)`. Accept the `npm install`/`npm i` and `--global`/`-g` spellings.
- **Counts.** Assert that the number of `python-version` matches equals the number of `actions/setup-python` uses, and that `node-version` matches equal `actions/setup-node` uses. For the npm install pins, assert an equally strict count and explain the invariant you chose.
- **Proof.** Show that the review's three false-pass edits now fail, each naming the diverging file:
  - an unquoted `python-version: 3.13.1`;
  - a double-quoted `node-version: "24.20.0"`;
  - `npm i -g npm@11.10.0`.

  Make each edit temporarily and revert it.

### `services/api/pyproject.toml` (finding 2)

Add `extend-exclude = ["*.md"]` under `[tool.ruff]`, and change nothing else. Show:

- `ruff format --check .` in `services/api` reports 57 files;
- `ruff check .` still passes;
- a temporary Markdown file containing an unformatted Python code block no longer fails the format check. Remove the file afterwards.

### `apps/mobile/AGENTS.md` (finding 11)

In "Rules", replace the bare `npx expo run:ios|android` with the wrapper form, `node scripts/development.mjs run:ios` or `run:android`. First read `apps/mobile/scripts/development.mjs` to confirm it forwards the arguments to the Expo CLI with the fixture environment. Do not run a native build. Keep the statement that native builds and device runs have not been performed.

### `docs/operations/local-development.md`

In "Claude Code cloud sessions", update only the Setup-script bullets so they state the final trust rules:

- symlinks may not leave their tree;
- the prefix and link directories must belong to the running account and must not be writable by group or others;
- the check runs before anything in a tree executes;
- the first run takes about two minutes.

### Evidence record

Add a new section, **"Correction session M02-C1"**, at the end of `docs/testing/evidence/2026-09-24-m02-claude-setup.md`. Record observations only: exact commands, exit codes, counts, versions, timings, failures and limits. Do not edit earlier sections.

**Do not edit manager-owned files:**

- the brief, `docs/ephemeral/`, `docs/continuity/`;
- root `AGENTS.md` and `CLAUDE.md`, `docs/planning/`, PF canon;
- `docs/README.md`, `docs/operations/ci-and-branch-policy.md`, `docs/operations/environment-inventory.md`.

**Do not edit:**

- application code, mobile tests or source;
- dependency manifests or locks, or any other `pyproject.toml` key;
- workflows, `.env.example` files, the `Dockerfile`.

**Known intermittent failures (outside scope):** the rendered cases `state-corrections.spec.ts:45` and `onboarding.spec.ts:103` sometimes fail in hosted CI when a form submit does not advance. Do not change tests or source to address them.

## 4. Checks (report exact results)

1. **Script.**
   - Run `bash -n`.
   - Run it fresh into a temporary `HOME` with a clean process environment, such as `env -i HOME=<tmp> PATH=/usr/bin:/bin LANG=C.UTF-8 bash scripts/bootstrap-toolchain.sh`. Record owners before and after, then run an idempotent rerun. The wrong Node, npm and Python hash cases must still fail closed.
   - Each review case must now fail safe, **without executing anything from the tree**:
     - a symlinked tree root;
     - an internal symlink to a foreign-owned file outside the tree;
     - a foreign-owned or group- or world-writable prefix;
     - a foreign-owned or writable link directory;
     - a fake `ssl` module on `PYTHONPATH`;
     - a module in the working directory;
     - a relative `--prefix` with `CDPATH` set;
     - `SIGTERM` during the Python build.
   - Use temporary directories only, and leave this session's `$HOME/.local` as you found it unless you restore it.
2. **Classifier tests:** `python3.12 -I -m unittest discover -s scripts -p 'test_change_scope.py' -v`. Report the new count.
3. **Pin test:** from `services/api`, `python3.12 -m unittest tests.test_toolchain_pins -v`, plus the three false-pass demonstrations.
4. **Ruff:** the checks in the `pyproject.toml` deliverable.
5. **API suite on the pinned toolchain,** in a clean process environment:
   - `pip install --require-hashes -r requirements-dev.lock`, `pip check`;
   - `GLOW_ENV=test manage.py check`, `manage.py test tests --verbosity 2` (report the count);
   - `ruff check .`, `ruff format --check .`, `mypy`;
   - the contract tests.
6. **Final checks:**
   - a relative-link check over every changed Markdown file;
   - `git diff --check`;
   - trusted-base classification (command in `docs/planning/manager-workflow.md`), where full scope is expected.

## 5. Finish and report

Commit with clear messages and push your own session branch. Do not open or merge PRs, and do not update Notion; the manager integrates.

Your final message is the report Nathan relays:

- branch, commit SHAs and final tree;
- changed paths;
- for each finding (1, 2, 3, 6, 7, 8, 9, 10, 11 and the script part of 13): the fix, and the behavior before and after with the test that shows it;
- every check with its exact result;
- failures and their resolution;
- a prominent note that `scripts/bootstrap-toolchain.sh` changed and must be pasted once after merge;
- deviations from the brief;
- open questions and limitations.

Skipped or unavailable checks are not passes.

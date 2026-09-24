# M02 delta review prompt — review of PR18's final head against the reviewed `ccebd1b`

- **Owner:** App Manager 2. Nathan starts this session manually and relays its report.
- **Durable brief:** [M02 brief](../planning/claude-setup-optimization.md), sections "Exact-head review of `ccebd1b` and its disposition" and "Correction brief — M02-C1". Evidence: [M02 evidence record](../testing/evidence/2026-09-24-m02-claude-setup.md).
- **Deletion condition:** prune after M02 closes and the evidence record holds the accepted review result.

**Manager:** before giving this prompt to Nathan, replace `<REVIEW_HEAD>` with the exact head SHA of `claude/fervent-darwin-idyko3` to be reviewed.

---

You are the **delta review session for M02** (PR18) of the Glow dating app, private repository `amthorn78/glow-dating-app`.

An earlier independent review covered head `ccebd1bf5eb23155fec17ef7670164e5431d3849` and approved it with findings. Since then, the manager recorded its own fixes, and correction session M02-C1 fixed the rest. You review everything that changed since `ccebd1b`, and confirm each finding is resolved.

- Nathan started you manually and will relay your report to the manager (App Manager 2). You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report. **Change nothing.**
  - Do not commit, push, open or comment on PRs, or edit Notion.
  - Keep scratch work outside the repository or uncommitted.
- The `CLAUDE.md` loaded when your session started comes from `main` and is older. After the start gate, the versions at the reviewed head govern. Do not re-run `docs/planning/claude-code-initiation.md`.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` may be set. Check names only: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` are set for Nathan's development Stream application. Never print or copy the secret.
3. Record `command -v node npm python3.12` and their versions. Expected: v24.19.0, 11.9.0 and Python 3.12.14, from `$HOME/.local/bin`.
4. Never dump the environment. Never connect to a database, provider, HDE or Railway. Never run `playwright install`, `eas` or `migrate`.

## 2. Start gate

```bash
git fetch origin claude/fervent-darwin-idyko3 main
git switch --detach <REVIEW_HEAD>
git rev-parse HEAD                                   # must print <REVIEW_HEAD>
git merge-base --is-ancestor ccebd1bf5eb23155fec17ef7670164e5431d3849 HEAD && echo "ccebd1b is an ancestor"
git merge-base --all origin/main HEAD                # expected exactly 07b3b10720ddd333ada807a56595f369263714fe
```

If any check fails, stop and report.

Classify with the trusted base policy, as root `AGENTS.md` requires:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
```

Expected: `"full": true`.

Then read, completely:

- root `AGENTS.md`;
- the brief's disposition table and the M02-C1 brief, in `docs/planning/claude-setup-optimization.md`;
- the evidence record's sections from "App Manager 2 — exact-head review relay" onwards;
- the whole of `git diff ccebd1bf5eb23155fec17ef7670164e5431d3849..HEAD`, which is the delta under review.

## 3. What to review

1. **Every finding is resolved.** For each of findings 1–13 in the brief's disposition table, state resolved, partly resolved or not resolved, with evidence from the code or a test.
   - Findings 4, 5 and 12, and parts of 2 and 13, were fixed by the manager in documentation; check the wording against the code and the workflow.
   - Finding 7 is Nathan's decision that `.claude` paths are full scope.
2. **The new code, as a security review.**
   - **`scripts/bootstrap-toolchain.sh`, the root-run Setup script:**
     - the symlink walk in `link_inside`, and whether any link can escape or be misjudged;
     - `trusted_tree`'s failure handling under `set -euo pipefail`;
     - `safe_dir`'s parent walk, including sticky directories;
     - the link-directory symlink test;
     - process-group signal handling (`run`, `stop_child`, `interrupted`, `set +m`, `setsid`) and whether any path leaves children running or files behind;
     - the `curl` options;
     - `NODE_DISABLE_COMPILE_CACHE`;
     - that nothing from an untrusted tree executes before the check.
   - **`scripts/change_scope.py` and its tests:** `.claude` matching; the multiple-merge-base rule; fail-closed behavior for zero bases and errors; and that the tests really fail against the previous classifier.
   - **`services/api/tests/test_toolchain_pins.py`:** pattern and count strictness; false passes and false failures.
   - **`services/api/pyproject.toml`:** only `extend-exclude = ["*.md"]` changed, and it affects nothing but Markdown.
3. **The implementer's deviations,** listed in the evidence record's "M02-C1 verification and integration" section: judge each one as acceptable or a finding.
4. **The policy and documentation edits in the delta:**
   - Nathan's one-work-item policy;
   - the `.claude` rule;
   - the push-run evidence rule;
   - the CI policy;
   - the documentation guide;
   - the handoffs;
   - the PF01 table fix;
   - the migration plan note;
   - the environment inventory.

   Check them for accuracy against the code, contradictions and unsafe instructions. This is a full-scope review: never skip a finding because the file ends in `.md`.
5. **Scope and secrets.**
   - Confirm the delta changes no application runtime code, dependency manifest or lock, workflow, `.env.example` or `Dockerfile`. The one `pyproject.toml` key is allowed.
   - Scan the delta for credential values. `STREAM_API_SECRET` must appear by name only.

**Out of scope:**

- anything unchanged since `ccebd1b` (the earlier review covered it), unless the delta makes it wrong;
- the known intermittent rendered-suite failures;
- feature work and P06.1;
- anything in HDE.

## 4. Checks to run

Report the exact commands and results.

1. `bash -n scripts/bootstrap-toolchain.sh`.
2. A fresh run of the script into a temporary `HOME` with a clean process environment, for example `env -i HOME=<tmp> PATH=/usr/bin:/bin LANG=C.UTF-8 bash scripts/bootstrap-toolchain.sh`, plus an idempotent rerun.
3. The adversarial cases you judge necessary. At least:
   - a symlinked tree root;
   - a symlink leaving the tree;
   - an unsafe prefix or link directory;
   - a fake module on `PYTHONPATH`;
   - `SIGTERM` during the Python build.

   Use temporary directories only, and never use this session's `$HOME/.local` unless you restore it.
4. The classifier tests, `python3.12 -I -m unittest discover -s scripts -p 'test_change_scope.py' -v`. Then run the same test file against the previous classifier, to show which tests fail there. The test file imports `change_scope` from its own directory, so copy the reviewed `scripts/test_change_scope.py` into a temporary directory beside `git show ccebd1bf5eb23155fec17ef7670164e5431d3849:scripts/change_scope.py`, and run `python3.12 -I -m unittest discover -s <tmp> -p 'test_change_scope.py' -v` there.
5. The pin test, from `services/api`: `python3.12 -m unittest tests.test_toolchain_pins -v`, plus at least one temporary, reverted false-pass edit.
6. `ruff format --check .` and `ruff check .` in `services/api`, with the pinned ruff from `requirements-dev.lock`.
7. `git diff --check ccebd1bf5eb23155fec17ef7670164e5431d3849..HEAD` and a relative-link check over the Markdown files the delta changes.
8. A secret scan over the delta.

The manager reads hosted CI on the reviewed head, so you need not wait for it.

## 5. Report

Your final message is the report Nathan relays:

- the head you reviewed and the classification output;
- **verdict:** "approve for merge" or "changes required";
- a table of findings 1–13, each marked resolved, partly resolved or not resolved, with evidence;
- **new findings**, most severe first. For each: severity (**blocking**, **should fix** or **nit**), `file:line`, the concrete failure scenario and a suggested fix;
- the deviations you judged, one by one;
- every check you ran, with its exact result;
- limits: anything you could not check, and why.

Skipped or unavailable checks are not passes. Change nothing in the repository or on GitHub.

# M02 review prompt — exact-head code and security review of PR18

- **Owner:** App Manager 2. Nathan starts this session manually and relays its report.
- **Durable brief:** [M02 brief](../planning/claude-setup-optimization.md), section "Review and merge gates". Evidence: [M02 evidence record](../testing/evidence/2026-09-24-m02-claude-setup.md).
- **Deletion condition:** prune after M02 closes and the evidence record holds the accepted review result.

**Manager:** before giving this prompt to Nathan, replace `<REVIEW_HEAD>` with the exact head SHA of `claude/fervent-darwin-idyko3` to be reviewed.

---

You are the **review session for M02** (PR18) of the Glow dating app, private repository `amthorn78/glow-dating-app`.

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
git rev-parse HEAD                # must print <REVIEW_HEAD>
git merge-base origin/main HEAD   # expected 07b3b10720ddd333ada807a56595f369263714fe
```

If any check fails, stop and report.

Classify first, as root `AGENTS.md` requires. The trusted base policy runs outside the candidate tree:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
```

Expected: `"full": true`. If it reports `ordinary-docs-only`, stop and report that.

Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`;
- `docs/planning/claude-setup-optimization.md` (the M02 brief);
- `docs/testing/evidence/2026-09-24-m02-claude-setup.md`;
- `docs/operations/ci-and-branch-policy.md`;
- `.github/workflows/foundation.yml`;
- the whole of `git diff origin/main...HEAD`.

## 3. What to review

Review the complete PR diff, `git diff origin/main...HEAD`. The focus areas are in order of risk.

1. **`scripts/bootstrap-toolchain.sh`, the environment's Setup script.** It runs as root before every session, downloads Node, npm and CPython, verifies them against pinned hashes, builds Python and links tools into `$HOME/.local/bin`. Check at least:
   - download integrity: hash and integrity pins, curl flags, TLS and redirects, and whether anything unverified is executed or installed;
   - the ownership and permission trust model (`trusted_tree`, `umask`, tar flags): symlinks, the prefix directory, `$HOME/.local/bin`, time-of-check to time-of-use gaps, and whether anything from an untrusted tree can run before the check;
   - idempotence, interrupted or partial installs, and failure modes. Every failure should stop with a clear error and leave no half-linked state;
   - argument handling (`--prefix`, `--no-link`), temporary files and clean-up, and influence from inherited variables (`PATH`, `TMPDIR`, `npm_config_*`, curl or pip configuration);
   - that it prints no environment values.
2. **`scripts/change_scope.py` and `scripts/test_change_scope.py`, the CI and review classification policy.** Nathan decided on 24 September 2026 that a change made only of regular Markdown files skips application CI and code/security review. Do not re-argue that decision; check that the implementation matches it and fails closed:
   - path normalization, file modes (symlinks, executables, submodules), renames, case, unusual filenames, empty or unavailable comparisons, and merge-base handling;
   - any concrete way a Markdown-only change could still change what CI, the build, the container or the app executes, such as a `.md` file read, imported, copied into an image or executed by a workflow step, test, `Dockerfile` or runtime;
   - instruction files the exemption now covers (for example `AGENTS.md`, `CLAUDE.md`, `.claude/**/*.md`, `.github/**/*.md`). Report these as residual risk, not as blockers, unless there is a concrete execution path;
   - that the PR does not change `.github/workflows/`.
3. **`services/api/tests/test_toolchain_pins.py`:** correctness, false passes (a pattern that could match the wrong line or miss a pin), read-only behavior and useful failure messages.
4. **Instruction and process Markdown.** This is a full-scope review: never skip a finding because the file ends in `.md`. It covers:
   - root `AGENTS.md` and `CLAUDE.md`, and `apps/mobile/AGENTS.md`;
   - the manager workflow, and the PF00 and PF01 edits;
   - the CI policy, local development (including the proxy and CA pass-through for clean environments) and the environment inventory;
   - the handoffs, the brief and the prompts.

   Look for:
   - instructions that are wrong against the code;
   - unsafe instructions: leaking or printing secrets, weakening fixture-only guards or the protected HDE boundary, running release tooling, connecting databases;
   - contradictions between documents;
   - claims the evidence does not support.
5. **Secrets and scope:**
   - Scan the whole diff for credentials or token-like values. `STREAM_APP_ID=1729640` and `STREAM_API_KEY=qdstwyevnyea` are documented non-secret identifiers. `STREAM_API_SECRET` must appear by name only.
   - Confirm there are no application runtime, dependency manifest or lock, `.env.example` or `Dockerfile` changes.

**Out of scope:**

- the known, pre-existing intermittent rendered-suite failures (`state-corrections.spec.ts:45`, `onboarding.spec.ts:103`);
- feature work and P06.1;
- anything in HDE.

## 4. Checks to run

Report the exact commands and results.

1. `bash -n scripts/bootstrap-toolchain.sh`.
2. At least one fresh run of the script into a temporary `HOME` with a clean process environment, for example `env -i HOME=<tmp> PATH=/usr/bin:/bin LANG=C.UTF-8 bash scripts/bootstrap-toolchain.sh`. Add an idempotent rerun and any adversarial case your review needs: a wrong hash, a planted foreign-owned tree, symlinked paths.
   - Use temporary directories only.
   - Do not run it against this session's `$HOME/.local` unless you restore it afterwards.
3. The classifier tests, `python3.12 -I -m unittest discover -s scripts -p 'test_change_scope.py' -v`, plus any classification cases you construct in a scratch repository.
4. The pin test, from `services/api`: `python3.12 -m unittest tests.test_toolchain_pins -v`.
5. A secret scan over `git diff origin/main...HEAD`.
6. Anything else you judge necessary.

The manager reads hosted CI on the reviewed head, so you need not wait for it.

## 5. Report

Your final message is the report Nathan relays:

- the head you reviewed (`git rev-parse HEAD`) and the classification output;
- **verdict:** "approve for merge" or "changes required";
- **findings**, most severe first. For each: severity (**blocking**, **should fix** or **nit**), `file:line`, the concrete failure scenario and a suggested fix;
- the areas you reviewed with no findings;
- every check you ran, with its exact result;
- limits: anything you could not check, and why.

Skipped or unavailable checks are not passes. Change nothing in the repository or on GitHub.

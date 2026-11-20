# SV4 A0 exact-head review prompt — the database job split by suite, the Chromium retry and the pin test, with a written threat model

- **Owner:** App Manager 12. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 19 November 2026.**
- **Durable brief:** [SV4 — the chat and notifications slice](../planning/sv4-chat-notifications.md), revision 3, "Review plan" (DM-96's AG21).
- **Where the result goes:** the report Nathan relays. The manager records it in the evidence record, "Exact-head review of A0", with a disposition for each finding (fix before the merge, or carry), and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 2.96 (confidence 0.91); rung probabilities low 0.00, medium 0.00, high 0.08, extra high 0.87, max 0.05, ultracode 0.00. Model probabilities Fable 5.1 0.14, Opus 5.5 0.86, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.81). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.011, Fable 5.1 at extra high 0.122, Fable 5.1 at max 0.007, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.000, Opus 5.5 at high 0.069, Opus 5.5 at extra high 0.748, Opus 5.5 at max 0.043, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-19T05:30:30Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action. The Dev Manager's pre-merge read of A0 follows this review.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of PR57's head (manager workflow, step 6). A full review of A0's code, not a delta review.
- **Deletion condition:** prune after A0's pull request (PR57) merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **exact-head review of SV4 A0**: the Foundation workflow's database job split by suite, the Chromium install's retry and the pin test's fixes, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one exact code head in full, with a written threat model. This prompt is revision 1, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **The database job** (`database`, in `.github/workflows/foundation.yml` at `c2cffbe`) ran four PostgreSQL proof suites in order on four databases in one PostgreSQL 17.11: P06.DB's ordering suite, then SV1's identity, SV2's profile and SV3's discovery suites. Each suite after the first showed that its database refuses the other suites' markers, and each of the last three checked its own log and results for every secret the job held before uploading them.
- **SV4's brief,** revision 3 (`docs/planning/sv4-chat-notifications.md`). Its D2 sets A0: one job per suite, each with its own PostgreSQL, credentials and marker and every check it ran before; one decoy database per job, carrying another suite's marker, that its suite must refuse (DM-96's AG1); each suite's secret scan following its job (revision 3, the manager's); the gate requiring each job. D7 adds the pin test's two fixes; D2 the Chromium retry, as carried (DM-59 item 7). DM-96's report is in `docs/continuity/dev-manager/reviews/2026-11-19-dm-96-sv4-stage-a-brief.md`.
- **The implementation** (branch `claude/affectionate-curie-hzo99y`, code head `3bf55de`, records head `c77646b`; the evidence record `docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`, section "A0"): run of record 44463105633, all eleven jobs passed. The manager verified it ("Manager verification of A0", which lists four points for you) and merged it into the manager branch at `4dfb0ac`. PR57 carries it into `main`.

**The code head under review is `3bf55de`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `3bf55de` (the start gate checks this).

**Your scope:**
- **The code:** `git diff c2cffbe6022637331d73e3558429ff70ab5aa5e3 3bf55de775de1f7aa8cace3f7bc780c97f0b2e98`, its eight non-Markdown paths, read in full at `3bf55de`:
  - `.github/workflows/foundation.yml`, whole, against the file at `c2cffbe`, step for step;
  - `proofs/postgres-ordering/glow_ordering_proof/identity_scan.py`, `profile_scan.py` and `discovery_scan.py`;
  - `proofs/postgres-ordering/tests/test_identity_offline.py`, `test_profile_offline.py` and `test_discovery_offline.py`;
  - `services/api/tests/test_toolchain_pins.py`.
- **The Markdown, as claims about the code:** `docs/operations/ci-and-branch-policy.md` (governing; the Dev Manager also reads it before the merge), `proofs/postgres-ordering/README.md`, and the evidence record's section "A0", whole.
- **The runs:** 44463105633 (the run of record) and the PR run on PR57's head (event `pull_request`), once it has finished.
- **Out of scope:** the suites' cases and the application code, which A0 does not change; SV4's later stages. Report only where A0's change affects them.

**The threat model.** Write it in your report:
- **Assets:**
  - each job's generated secrets: the PostgreSQL superuser's and the role's passwords, the markers, each suite's `SECRET_KEY` and JWT signing key;
  - the proof's integrity checks: the marker refusal (now with a decoy), `dbshell`'s refusal, the migrations from zero against the models, the used-database refusal, the commit-order and row-lock records;
  - the results JSON and the artifacts, uploaded only after a job's secret check passes;
  - the gate's verdict, and the routing that skips application jobs only for ordinary documentation;
  - the pin test, which keeps the workflow's Python, Node and npm pins in step with the repository's.
- **Actors:**
  - anyone who reads this public repository's CI logs and artifacts;
  - a pull request's author, whose workflow YAML can change its own routing (CI routing is not a security boundary; root `AGENTS.md`);
  - an unreliable network: Docker Hub (now four pulls of the image per run), apt mirrors, the Python download;
  - a later change that adds a suite's job "the same way" (A2).
- **Entry points:** each database job's steps; the gate's step; Mobile checks' Chromium steps; the three scans' file lists; the offline tests that read the workflow.

For each threat, give the step or code that stops it and the test or run that proves it. The focus:
1. **Nothing lost.** Every step and check the shared job ran for a suite is in that suite's job, with its checks and printed lines: list each old step beside its new place. Say whether any was weakened, reordered so that it proves less, or made conditional.
2. **The decoy** (AG1).
   - Each of the identity, profile and discovery jobs creates one more database whose marker is not its suite's, and shows its suite refuses it before any statement, with its own database unchanged.
   - Say whether the check could pass for the wrong reason: a missing decoy, an equal marker, an empty comment, a refusal for another cause.
   - The decoy's marker is one the job generates, in the earlier suite's form (for example `glow-ordering-proof:` for the identity job), not that suite's own marker, which only a shared PostgreSQL held. AG1's words are "carrying another suite's marker". Say whether this meets them, and whether a refusal of this marker proves what the shared job's refusal proved.
3. **The secrets.**
   - Each credentials step masks every value before anything prints, and no step prints a password, marker, key or connection value.
   - Each scan reads every secret file its own job writes, the decoy's marker included, and no other; a file its job writes and its scan omits would be a gap.
   - Each upload is gated on its job's check, and each job removes its database, container and credential files.
   - Artifact names stay distinct across jobs.
4. **The gate and the routing.**
   - Each database job keeps `needs: scope` and the old job's condition.
   - The gate needs each job, and fails a full-scope run unless each succeeded, and an ordinary-documentation run unless each was skipped.
   - Say what happens when a job is cancelled, times out or is skipped on a full-scope run.
5. **The Chromium retry,** against the carried text (the carried-items file, "Carried to the next change to the Foundation workflow").
   - The form: `id`, `continue-on-error`, the pause and the retry under `if: steps.chromium.outcome == 'failure'`, the retry without `continue-on-error`, each attempt's `timeout-minutes`, and the worst case inside the job's 25 minutes.
   - **The open question:** whether a step stopped by its own `timeout-minutes` has the outcome `failure`, so that the retry runs. Read GitHub's public documentation on step timeouts, `continue-on-error`, and `steps.<id>.outcome`, and say what it states, quoting it, or that it does not say.
6. **The pin test.** It strips YAML comments before counting pins, and reads `proofs/stream-chat/package.json`'s Node and npm pins. Say whether a pin could still escape it, for example a pin in a YAML block scalar or a quoted string.
7. **The offline tests.**
   - Each changed test is one the prompt's "Earlier tests" named, and asserts what it asserted, or more.
   - `test_the_suite_runs_after_the_profile_suite`'s replacement, and the new test that the gate requires each job, prove what they say.
   - The `JobDirectory` builders now read the workflow; say whether a scan could drift from its job without a test failing.
   - No test is vacuous: each reversal the record names fails its test.
8. **Cost and reliability.**
   - Four pulls of the PostgreSQL image per run where there was one: say whether GitHub-hosted runners risk Docker Hub's pull limit, from GitHub's or Docker's public documentation.
   - Each job repeats the install and the offline tests: say whether any job's timeout is at risk, from the run's durations.
9. **No dependency:** the action pins, the image's digest, the lock files and every requirement file are unchanged from `c2cffbe`; permissions and checkout credentials are as before.
10. **The records:** every claim in the CI policy's change, the proof's README and the record's section "A0" holds against the code and the runs. Note the three offline test files' module docstrings, which still describe the shared job (the manager's verification).

**Re-run, at least,** in a scratch copy of `3bf55de`:
- **The proof's checks:** its offline tests, `ruff` and the configured `mypy`, in a clean environment.
- **The API's pin test:** `services/api/tests/test_toolchain_pins.py`, with the API's test runner.
- **The workflow parses,** with a YAML reader, and each job's steps match your step-for-step list.
- **Four reversals, offline, on copies:**
  - one secret file left out of a scan's list: its scan test fails;
  - one database job left out of the gate's `needs` or its results loop: the gate test fails;
  - a step removed from a suite's job (its decoy refusal, or its gated upload's condition): a workflow test fails;
  - a pin moved into a YAML comment, and a changed pin in `proofs/stream-chat/package.json`: the pin test fails each way.
- **The database jobs, informational:** one or more jobs' steps on a throwaway PostgreSQL under P06.DB's D4, if Docker allows.

**What comes after this review: the correction classes.** Report every finding with its severity. A correction pass takes every blocking finding, and any should-fix finding that could do any of these:
- lose or weaken a check a suite's job ran before, or let it pass for the wrong reason;
- let a secret, a marker, a key or a connection value reach a log, an error or an artifact, or a scan miss a secret file its job writes;
- let the gate pass a full-scope run without each database job's success, or skip application jobs for a change that is not ordinary documentation;
- leave the Chromium retry unable to run when its first attempt fails, or let a second failure pass;
- let a pin escape the pin test;
- add an action, a pin, an image or a package;
- let a test pass where it should fail, or fail where the code is right;
- leave a Dev Manager condition unmet;
- make a record claim more than the code, the tests or the runs show.

Everything else goes into the records. For each finding, say whether it falls in one of these classes.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 12. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches. Read GitHub only through your GitHub tools; use `gh` for nothing but a search.
  - **Scratch work goes in a copy outside the repository,** never the checkout (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
- **Network:**
  - PyPI and the npm registry, for hash-locked installs in a scratch copy;
  - Docker Hub, only to pull the PostgreSQL image the workflow pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`);
  - GitHub, through your tools, to read runs, and GitHub's and Docker's public documentation pages, to read only.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions): a throwaway PostgreSQL in Docker, from that image, on loopback only; a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present; removed afterwards.
- **Never:**
  - dump the environment, or print a credential, password, marker, token, session key or key;
  - read, print or use the value of any `AWS_*` variable (section 1);
  - call any provider or HDE, or run any command in `proofs/stream-chat/` (you read its `package.json` only);
  - connect to any database but a throwaway one you started under D4's conditions, HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:** `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_|RAILWAY_)'` prints names only. If any is present, stop and report.
3. **AWS names may be present** (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_CA_BUNDLE`); the cloud container sets them (OD-76). `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
5. **The toolchain:** CPython 3.12.14 as `python3.12`; Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`; Docker if present. Record their versions.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables. No `AWS_*` name passes.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, c2cffbe6022637331d73e3558429ff70ab5aa5e3
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 3bf55de775de1f7aa8cace3f7bc780c97f0b2e98 HEAD -- . ':!*.md' && echo "the code head under review"
git diff --quiet 3bf55de775de1f7aa8cace3f7bc780c97f0b2e98 origin/claude/magical-wozniak-yfmmx2 -- . ':!*.md' && echo "no code on the live branch after 3bf55de"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-19-sv4-chat-notifications.md | grep -c -E '^#+ Exact-head review of A0'   # must print 0
```

If any check fails, stop and report. The prompt is stale if its commit is not on the live branch, a non-Markdown path changed there after `3bf55de`, or this review is already recorded.

**Classify the change** as root `AGENTS.md` requires, with the trusted base policy outside the candidate tree:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
```

Expected: `"full": true`. Anything else: stop and report.

**Then read, completely, at `HEAD`:**
- root `AGENTS.md` and `CLAUDE.md`; `proofs/postgres-ordering/README.md`;
- the brief, revision 3: D1, D2, D7, D11, "Owned paths" (A0), "Acceptance checks", "Review plan";
- DM-96's report, sections 3, 10 and 12;
- the carried entry "Carried to the next change to the Foundation workflow" in `docs/planning/carried-to-later-items.md`;
- the evidence record's section "A0", whole, with "Manager verification of A0";
- every file in the code diff, whole, and the workflow at `c2cffbe` beside it;
- the CI policy, `docs/operations/ci-and-branch-policy.md`, whole;
- P06.DB's brief, `docs/planning/p06-db-disposable-postgres-proof.md`, D1 to D4.

**The runs,** with your GitHub tools: 44463105633 and the PR run on PR57's head, if it has finished: every job's conclusion and duration, and the gate's line.

## 3. What to do

1. Write the threat model, then review the change against the focus, item by item.
2. In a scratch copy of `3bf55de`: re-run the checks and the four reversals above, and any you doubt; run a database job's steps locally under D4 if you can, informational.
3. For each finding: its severity (blocking, should fix, nit), its file and line, the evidence, and whether it falls in a correction class.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- the threat model, each threat with its stopping step or code and its test or run;
- the focus, item by item, with your verdict on each, the step-for-step list under item 1;
- every finding, with its severity, file and line, evidence and correction class;
- the checks and reversals you re-ran, each with its exact result, and any local run;
- your verdict: **approve**, **approve with nits** or **changes requested**;
- what you did not read or run, and why.

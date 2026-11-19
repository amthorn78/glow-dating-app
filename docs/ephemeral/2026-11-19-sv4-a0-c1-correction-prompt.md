# SV4 A0-C1 prompt — the correction: the offline tests that pin the decoy, `dbshell` and gate checks

- **Owner:** App Manager 12. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 19 November 2026.**
- **Durable brief:** [SV4 — the chat and notifications slice](../planning/sv4-chat-notifications.md), revision 3. **The findings:** the A0 record's section "Exact-head review of A0" (`docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`), with its disposition table.
- **Where the result goes:**
  - the session's changes to the three offline test files, and its section "A0-C1" in the same record, on its own branch;
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification to the record, and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 1.89 (confidence 0.87); rung probabilities low 0.00, medium 0.16, high 0.80, extra high 0.04, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 1.00, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 1.00). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.160, Opus 5.5 at high 0.800, Opus 5.5 at extra high 0.040, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-19T06:24:12Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. This prompt authorizes no credential use and no live provider action (the charter, "Read before it takes effect"). Under D-07 the correction goes on the list for Dev Manager 6's pre-merge read of A0.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Then, in order: the manager's verification; PR57's run and Codex's review of its new head; a delta review of C1 (the manager workflow, "A small correction gets a delta re-review"); Dev Manager 6's pre-merge read; the merge.
- **Deletion condition:** prune after A0's pull request (PR57) merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch (AM11-21).

---

You are the **correction session A0-C1** for SV4 A0, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **A0** (code head `3bf55de`; the record `docs/testing/evidence/2026-11-19-sv4-chat-notifications.md`, section "A0") split the Foundation workflow's database job into four per-suite jobs: "Database proof checks (ordering)", "(identity)", "(profile)" and "(discovery)". Each of the identity, profile and discovery jobs creates a decoy database with a marker of its own and shows its suite's database refusing that marker (DM-96's AG1), and shows `dbshell` refused under its suite's settings. The gate requires each job.
- **A0's exact-head review** (the record's section "Exact-head review of A0") asked for changes in tests only. The workflow is right at `3bf55de`; some of its new checks have no offline test, so a later edit could remove or weaken them with every test still passing. Its reversals D1a, D1b, D2a, D2c, D2d, D3a, D3b, D4a to D4d and D6a each passed every offline test.
- **The manager's disposition** (the same section's table): F1, F2 and F7's D6a are fixed now, by you; F6's test-module docstrings too, because you change those modules. Everything else is recorded or carried.

**This is a correction of tests only.** You add assertions to the offline tests so that each check below fails its test when it is removed or rebound. You change no workflow, scan, setting, README, policy or application file.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 12. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only these paths:
    - `proofs/postgres-ordering/tests/test_identity_offline.py`, `test_profile_offline.py` and `test_discovery_offline.py`: their tests of the workflow's steps, new tests of the same kind, and their module docstrings;
    - the record, section "A0-C1" only;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only, through your GitHub tools: no pull request, comment, review, re-run, workflow dispatch or setting. Use `gh` for nothing but a search. Change nothing in Notion.
- **The stop rule.** Stop and report, with no further change, if any of these holds:
  - **a path:** the work needs any path outside the list above: `.github/workflows/foundation.yml` above all, the scans, the proof's code or settings, the CI policy, the README, any `services/api/` or `apps/` path;
  - **the workflow is wrong:** an assertion below would fail against the workflow at `3bf55de`, which would mean a check is missing or misbound, not untested. Report the step and the line; do not change the workflow;
  - **an earlier test:** a test you did not add would have to change in what it asserts (adding assertions to the tests named below is allowed), or any test would be weakened or deleted;
  - **a reversal passes:** after your change, one of the reversals below still passes every offline test.
  - In each case, report it; do not narrow this prompt's words to pass it. A reversal's temporary edit is allowed, and must be undone.
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished. A newer push cancels the earlier run's application jobs, and the run of record is lost. Push your records commit only after the run of record has finished. The workflow runs on pushes to `claude/**` and `ccr-**`; if your branch is named otherwise, say so in the report, since no run starts.
  - **If GitHub never starts the run** (it stays `queued` with no jobs for 30 minutes), do not re-run it, dispatch it, push an empty commit, or ask anyone to re-run it (OD-58). Record it, push your records commit, and report.
  - **If the run fails,** stop and report the failing job and its log lines. Do not re-run it.
- **Network:** PyPI only, for `pip install --require-hashes` from the proof's existing lock. No database runs: every check here is offline.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, password, marker, token or key;
  - read, print or use the value of any `AWS_*` variable, or name one in a command (section 1);
  - call any provider or HDE, connect to any database, HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script;
  - weaken or delete a test to make the suite pass.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:** `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_|RAILWAY_)'` prints names only. If any is present, stop and report.
3. **AWS names may be present** (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_CA_BUNDLE`); the cloud container sets them (OD-76). `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values, and pass none to a command.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them.
5. **The toolchain:** CPython 3.12.14 as `python3.12`. Record `python3.12 --version`.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git merge-base --is-ancestor <START_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 3bf55de775de1f7aa8cace3f7bc780c97f0b2e98 HEAD -- . ':!*.md' && echo "A0's code head"
git diff --quiet 3bf55de775de1f7aa8cace3f7bc780c97f0b2e98 origin/claude/magical-wozniak-yfmmx2 -- . ':!*.md' && echo "no code on the live branch after 3bf55de"
grep -c -E '^#+ Exact-head review of A0' docs/testing/evidence/2026-11-19-sv4-chat-notifications.md   # must print 1
grep -c -E '^#+ A0-C1' docs/testing/evidence/2026-11-19-sv4-chat-notifications.md                     # must print 0
```

If a check fails, stop and report. The prompt is stale if its commit is not on the live branch, a non-Markdown path changed there after `3bf55de`, or a C1 section already exists.

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`; `proofs/postgres-ordering/README.md`;
- the record's sections "A0" and "Exact-head review of A0", whole;
- the brief, revision 3: D2, D11's A0 bullet, "Acceptance checks";
- the workflow, `.github/workflows/foundation.yml`: the four database jobs and the gate, whole;
- the three offline test files, whole: their workflow helpers (`workflow_job`, `workflow_steps`, `workflow_step`, `job_secret_files`, `job_databases`), `ProfileWorkflowTests` and `DiscoveryWorkflowTests`.

## 3. What to do

Each item names the reversals that must fail its test after your change. A reversal is a temporary edit to a copy of the workflow, or to the workflow followed by `git checkout -- .github/workflows/foundation.yml`; restore it byte for byte and check with `git status`.

1. **F1, the decoy's binding, in the identity, profile and discovery jobs.** In each job's credentials test:
   - assert the exact argument list of the `printf` that writes `create-role.sql`, so that the suite's own database's comment takes the suite's marker variable and the decoy database's comment takes the decoy's marker variable;
   - assert that the decoy's marker variable is the one written to the decoy's marker file;
   - and, in each job's decoy-step test, that the refused `migrate` reads that marker file.

   **Reversals,** in each of the three jobs: (a) the decoy's comment bound to another value (another variable, or the arguments swapped), as the review's D1a (profile) and D1b (identity) did; (b) the decoy's marker file written from another variable; (c) the refused `migrate` given another marker file. Each fails.
2. **F2, the identity job's new steps.** Add to `test_identity_offline.py` the identity counterparts of `ProfileWorkflowTests.test_the_credentials_step_makes_its_database_the_decoy_and_its_own_keys` and `test_the_migrations_step_refuses_the_decoys_marker_first`, for the identity job (its decoy database is `glow_proof`):
   - the credentials step: every value it masks (both passwords, the identity marker, the decoy's marker, the `SECRET_KEY`), each before any output; the markers' distinctness test; the decoy's creation with its own comment;
   - the decoy step: the decoy's existence and distinctness check and its failure line; the relation counts before and after and their `cmp`; the refusal's grep; the `test "$fail" = 0` line; the refused `migrate` before the suite's own `migrate`.

   **Reversals** (the review's): D2a, the line `test "$fail" = 0` removed; D2c, the counts' `cmp` removed; D2d, the decoy marker's `migrate` removed; D4a, one mask line removed; D4c, the distinctness test removed; D4d, the decoy not created. Each fails.
3. **F2, in all three jobs.**
   - Each job's `dbshell` step: its exit-status check (`if [ "$status" -eq 0 ]`) and its refusal check (the `grep` for `RefusedDatabase: refusing dbshell` and the failure when it is empty).
   - Each job's decoy step: its existence check (the `decoy` count and the failure when it is not 1).
   - Each job's credentials step: both password masks.

   **Reversals,** in each of the three jobs: D3a, the exit-status check removed; D3b, the refusal check removed; D6b, the existence check removed; D4b, a password mask removed. Each fails.
4. **F7's D6a, the gate's loop.** Extend the test that the gate requires each suite's job (`DiscoveryWorkflowTests.test_the_gate_requires_each_suites_job`) so that the loop checks every job in the tuple. **Reversal:** the loop over a slice (`for job in jobs[:5]:`) fails.
5. **F6, the module docstrings** of the three test files: say that their cases run in their own suite's job ("Database proof checks (identity)", "(profile)", "(discovery)"), each on its own disposable database, not "in the Database proof checks job, on the second (third, fourth) disposable database". Change no other wording.

Keep the tests' style: read the workflow through the existing helpers, and assert substrings and their order as the profile and discovery tests do. Add no dependency.

## 4. Checks, then the report

- **The trusted classifier,** from `main` (`c2cffbe`), extracted outside your checkout and run with `python3 -I` and full SHAs: `python3 -I <trusted copy>/change_scope.py --base c2cffbe6022637331d73e3558429ff70ab5aa5e3 --head <your code head> --merge-base` prints `"full": true` (reason `behavior-or-empty`).
- **The diff:** `git diff --name-only <START_SHA> <your head>` lists only the three test files and the record.
- **The proof's checks,** in a clean environment, after `pip install --require-hashes -r requirements-dev.lock` in `proofs/postgres-ordering`: `python -m unittest discover -s tests -t .`, `ruff check .`, `ruff format --check .` and `mypy` pass. Record the test count before and after.
- **Every reversal** in section 3 fails, each with its failing test's name and assertion line, and the workflow is restored byte for byte (`git status` clean, `git diff --quiet 3bf55de775de1f7aa8cace3f7bc780c97f0b2e98 HEAD -- .github` true).
- **The run of record,** on your last code commit: every job passed, the four database jobs among them, and the gate printed "Application checks passed".

**The record,** section "A0-C1": this prompt's revision and commit; the start gate's and the environment check's results; each test added or extended, by item; each reversal with its failing output; the counts; the run of record.

Your final message, which Nathan relays:
- your branch and head;
- the record's path;
- the run of record's link and result;
- what you changed, by item;
- every reversal's result;
- every stop, limit and deviation.

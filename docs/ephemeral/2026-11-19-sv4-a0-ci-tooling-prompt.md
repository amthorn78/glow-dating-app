# SV4 A0 prompt — the CI tooling: the database job split by suite, the Chromium retry, the pin test

- **Owner:** App Manager 12. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 19 November 2026.**
- **Durable brief:** [SV4 — the chat and notifications slice](../planning/sv4-chat-notifications.md), revision 3 (DM-96's AG1 to AG21 applied as given; revision 3, the manager's, adds the secret scans to A0).
- **Where the result goes:**
  - the session's changes in A0's owned paths, and its record, `docs/testing/evidence/<the session's date>-sv4-chat-notifications.md` (section "A0"), on its own branch;
  - the run of record: the Foundation run on its last code commit;
  - the manager adds its verification to the record, and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 2.59 (confidence 0.65); rung probabilities low 0.00, medium 0.04, high 0.38, extra high 0.54, max 0.02, ultracode 0.02. Model probabilities Fable 5.1 0.01, Opus 5.5 0.98, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.97). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.004, Fable 5.1 at extra high 0.005, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.039, Opus 5.5 at high 0.372, Opus 5.5 at extra high 0.529, Opus 5.5 at max 0.020, Opus 5.5 at ultracode 0.020, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.004, Sonnet 5.5 at extra high 0.005, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Flags: boundary between high and extra high. Sent 2026-11-19T04:11:34Z. Nathan picks the cell.
- **The Dev Manager's read:** done for the brief (DM-96; D-07's first read). This prompt authorizes no credential use and no live provider action, so it needs no read of its own (the charter, "Read before it takes effect"). The suites' keys and the database passwords are generated for one run and destroyed with it. The Dev Manager reads A0's change to the CI policy, with revision 3's additions, before A0 merges (AG21).
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Then, in order: the manager's verification; the pull request and Codex's review of its head; an exact-head review of the complete workflow diff, the scans, the pin test and the CI policy's change (AG21); corrections only for a defect D-07 names; the Dev Manager's pre-merge read; the merge after its run, Codex's summary on the final head and its checklist.
- **Deletion condition:** prune after A0's pull request merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision, and run its start gate against the live branch (AM11-21).

---

You are the **implementation session for SV4 A0**, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What A0 is.** The first of SV4 Stage A's three sessions: CI tooling, with no application code. SV4 then adds a fifth database suite (A2), and today's database job could not hold it. A0 covers:
- **the database job split by suite** (the brief's D2, with AG1): one job per suite, each with its own PostgreSQL from the pinned digest, its own credentials and marker, every check the shared job runs for that suite today, and one decoy database carrying another suite's marker that its suite must refuse; the Foundation gate requires each job;
- **each suite's secret scan follows its job** (D2, revision 3);
- **the Chromium install's one retry** (D2; DM-59 item 7, as carried);
- **the pin test's two fixes** (D7): YAML comments stripped before pins are counted (M02's N2), and `proofs/stream-chat/package.json`'s pins read (M05 finding 13);
- **the CI policy and the proof's README** brought to the new jobs.

There is no provider, deployed URL, real member, HDE call or stored credential.

**The brief, `docs/planning/sv4-chat-notifications.md`, revision 3, is the specification:** D1, D2, D7's pin-test and H-01 bullets, D11's A0 bullet, A0's owned paths, the acceptance checks and the review plan. Much of its text is the Dev Manager's words (DM-96, AG1 to AG21). Follow them exactly. Where this prompt summarizes the brief, the brief wins.

**What came before.**
- **The database job** (`database` in `.github/workflows/foundation.yml`, from line 228, `timeout-minutes: 30`) creates four databases in one PostgreSQL 17.11 and runs four suites in order: the ordering suite (P06.DB, P06.2), then SV1's identity, SV2's profile and SV3's discovery suites. On `main`'s run 44416436012 it took 16 minutes 32 seconds of its 30 (M09's C-17).
- **SV3's B0** (PR46) was a proof-tooling session like this one, merged on its own before its stage.
- **`main` is at `c2cffbe`** (PR56, Markdown only). The manager branch has changed only Markdown since.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 12. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only A0's owned paths (the brief):
    - `.github/workflows/foundation.yml`;
    - `docs/operations/ci-and-branch-policy.md` (its job list, its paragraph "Toolchain installs are retried once", and every sentence that describes the database job);
    - `services/api/tests/test_toolchain_pins.py`;
    - `proofs/postgres-ordering/README.md` (how the suites run in CI);
    - `proofs/postgres-ordering/glow_ordering_proof/identity_scan.py`, `profile_scan.py` and `discovery_scan.py` (each scan's list of its job's secret files, only);
    - `proofs/postgres-ordering/tests/test_identity_offline.py`, `test_profile_offline.py` and `test_discovery_offline.py` (their tests of the workflow's steps and of the scans' file lists, only);
    - the record;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only, through your GitHub tools: no pull request, comment, review, re-run, workflow dispatch or setting. Use `gh` for nothing but a search. Change nothing in Notion.
- **The stop rule.** Stop and report, with no further change, if any of these holds:
  - **an owned path:** the work needs a path outside the list above, including any other file under `services/api/`, `proofs/postgres-ordering/` or `packages/`, any `apps/` path, `scripts/` (`change_scope.py` above all), another workflow, the `Dockerfile`, an environment template or a `requirements` file;
  - **a check lost:** a step or check the shared job runs for a suite today cannot be kept in that suite's job: the wrong-marker refusal, `dbshell`'s refusal, the migrations from zero checked against the models, the server's facts, the used-database refusal, the secret check before any upload, the upload gated on that check, the removal of the database and its credential files;
  - **the routing:** a job's condition, the scope job, or the gate's rule for a documentation-only change would have to change in kind. Each new job takes today's `needs: scope` and condition; the gate requires each job's success on a full-scope change and its skip on a documentation-only one, as it does for today's jobs;
  - **a dependency:** a new action, a changed action pin, the PostgreSQL image's digest, a new Python or npm package, or a changed pin;
  - **the timeout:** a suite's job cannot stay within 30 minutes; it is not raised above that;
  - **an earlier test:** an earlier test that no longer passes and is not named in "Earlier tests" below. Report which and why; do not change or delete it.
  - In each case, report it; do not narrow the brief's words to pass it. A reversal's temporary edit is allowed, and must be undone.
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished. A newer push cancels the earlier run's application jobs, and the run of record is lost. Push your records commit only after the run of record has finished. The workflow runs on pushes to `claude/**` and `ccr-**`; if your branch is named otherwise, say so in the report, since no run starts.
  - **If GitHub never starts the run** (it stays `queued` with no jobs for 30 minutes), do not re-run it, dispatch it, push an empty commit, or ask anyone to re-run it (OD-58). Record it, push your records commit, and report. The manager's PR run is then the run of record.
  - **If the run fails,** stop and report the failing job and its log lines. Do not re-run it, and push no fix without saying so in the report.
- **Network:**
  - **PyPI and the npm registry:** for `pip install --require-hashes` and `npm ci --ignore-scripts` from the existing locks only;
  - **Docker Hub:** only to pull the PostgreSQL image the workflow pins (`postgres@sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`) for a local run (below).

  A page you cannot reach is named as unread, never filled from memory.
- **Local database runs** are allowed only as P06.DB's D4 allows them (`docs/planning/p06-db-disposable-postgres-proof.md`, D4, its four conditions): a throwaway PostgreSQL in Docker, from the pinned image, on loopback only; a generated password, the run's marker on each database, and none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name present; removed afterwards. Local passes are "iteration, not evidence"; the run of record is CI's.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, password, marker, token or key, in any form;
  - read, print or use the value of any `AWS_*` variable, or name one in a command (section 1);
  - call any provider or HDE, or run any command in `proofs/stream-chat/` (you read its `package.json` only);
  - connect to any database but a throwaway one you started under D4's conditions;
  - connect to HDE, Railway or any other external service;
  - run `playwright install`, `eas`, a native build or a package install script in your own environment (the workflow's own steps run in CI, as written);
  - weaken or delete a test to make the suite pass.

## 1. Environment check (names only; never print values)

1. **None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set:** `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name may be set:** `compgen -e | grep -E '^(STREAM_|PG|R2_|CLOUDFLARE_|CF_|RAILWAY_)'` prints names only. If any is present, stop and report.
3. **AWS names may be present** (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_CA_BUNDLE`); the cloud container sets them (OD-76). `compgen -e | grep -E '^AWS_'` prints names only. Record which are present. Never read, print or use their values, and pass none to a command.
4. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them.
5. **The toolchain:** CPython 3.12.14 as `python3.12`; Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, first on PATH (`scripts/bootstrap-toolchain.sh`). Record `python3.12 --version`, `node --version`, `npm --version` and `docker --version`.
6. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`docs/operations/local-development.md`).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git merge-base --is-ancestor <START_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git merge-base --is-ancestor c2cffbe6022637331d73e3558429ff70ab5aa5e3 HEAD && echo "PR56's merge present"
git diff --quiet c2cffbe6022637331d73e3558429ff70ab5aa5e3 HEAD -- . ':!*.md' && echo "main's code"
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- .github services/api proofs packages apps docs/operations docs/planning/sv4-chat-notifications.md   # must print nothing
ls docs/testing/evidence | grep -c 'sv4-'          # must print 0
```

If a check fails, stop and report. The prompt is stale if its commit is not on the live branch, the live branch has changed an owned path or the brief since it, or an SV4 record already exists.

**Then read, completely:**
- **The instructions:** root `AGENTS.md` and `CLAUDE.md`; `proofs/postgres-ordering/README.md`; `services/api/README.md`.
- **The brief,** revision 3: D1, D2, D7, D11 and "Owned paths", "Acceptance checks", "Review plan".
- **The Dev Manager's report** DM-96 (`docs/continuity/dev-manager/reviews/2026-11-19-dm-96-sv4-stage-a-brief.md`), sections 3, 10 and 12.
- **The carried entry** "Carried to the next change to the Foundation workflow" in `docs/planning/carried-to-later-items.md` (the Chromium retry's exact form).
- **The workflow,** `.github/workflows/foundation.yml`, whole, the `database` job and the gate above all.
- **The CI policy,** `docs/operations/ci-and-branch-policy.md`, whole.
- **P06.DB's brief,** `docs/planning/p06-db-disposable-postgres-proof.md`, D1 to D4 (the marker, the credentials, local runs).
- **The code you change:** the three scans, their offline tests (the classes "Earlier tests" names), and `services/api/tests/test_toolchain_pins.py`.
- **M02's record of N2:** `docs/planning/claude-setup-optimization.md`, its table's row N2.

## 3. What to do

1. **The split** (D2; AG1). Replace the `database` job with one job per suite: the ordering suite, SV1's identity suite, SV2's profile suite and SV3's discovery suite. In each job:
   - its own PostgreSQL 17.11 from the pinned digest, on loopback, with commit timestamps, as today;
   - its own generated credentials, masked before anything prints, and its own marker on its database's comment;
   - **the decoy** (AG1): one more database in that job's PostgreSQL, carrying another suite's marker, and the step showing its suite refuses it and leaves its own database unchanged, in the form today's "refuses the other markers" steps use. For the ordering suite, today's wrong-marker step already shows this; keep it;
   - every step it runs for that suite today, with each step's checks and printed lines kept;
   - its secret check, its upload gated on that check, and its removal step;
   - a name that says the suite (for example "Database proof checks (identity)"), `timeout-minutes` no more than 30, and today's `needs: scope` and condition.

   The gate's `needs` and its results check name each job. Record each job's duration on the run of record.
2. **The scans** (D2, revision 3). Each of `identity_scan.py`, `profile_scan.py` and `discovery_scan.py` lists exactly the secret files its own job writes: its keys, its marker, the decoy database's marker, the role's and the superuser's passwords. It reads no file its job does not write. Its offline test asserts the list, and a reversal (one file of the job left out of the list) fails it.
3. **The Chromium retry** (DM-59 item 7), exactly as carried:
   - the install step gets `id: chromium` and `continue-on-error: true`;
   - then a pause and one retry of the same command, each only `if: steps.chromium.outcome == 'failure'`;
   - the retry has no `continue-on-error`, so a second failure fails the job;
   - each attempt takes its own `timeout-minutes`, set so that both attempts, the pause and the rendered checks fit in the job's 25 minutes.
4. **The pin test** (D7):
   - **N2:** strip YAML comments before matching and counting pins, so a pin inside a comment is not counted;
   - **M05 finding 13:** read `proofs/stream-chat/package.json`'s Node and npm pins with the others.

   Each change comes with its reversal: a comment-only pin added to a copy of the workflow fails today's count and passes after; a changed pin in a copy of `proofs/stream-chat/package.json` fails the test. Run the reversals on copies or temporary edits, and undo them.
5. **The earlier tests** (below). Change each to the per-job shape, keeping what it guards. Replace `test_the_suite_runs_after_the_profile_suite` with a test of the new shape: each job's suite runs after its migrations and its decoy refusal, and its upload waits for its check. Record each changed test with its reason.
6. **The CI policy:** its job list, the gate's list, "Toolchain installs are retried once" naming the Chromium retry beside DM-41's, and every sentence that describes the database job. The proof's README: how the suites run in CI.
7. **The record,** `docs/testing/evidence/<your session's date>-sv4-chat-notifications.md`, section "A0":
   - this prompt's revision and commit;
   - the start gate's and the environment check's results;
   - what was built, by item;
   - each earlier test changed, with its reason;
   - each reversal with its failing output;
   - each job's duration on the run of record;
   - the limits: for example, that the Chromium retry cannot be exercised on a passing run, and how the YAML was checked instead.

**Earlier tests** (the brief's D11, A0's bullet; read at `ccc05ec`). These may change, and no others:
- `proofs/postgres-ordering/tests/test_identity_offline.py`: `JobDirectory`, `IdentityScanTests.test_the_values_are_the_job_files`, and `IdentityUploadGateTests` (its three tests);
- `proofs/postgres-ordering/tests/test_profile_offline.py`: `ProfileJobDirectory`, `ProfileScanTests.test_the_values_are_every_secret_file_of_the_job`, and `ProfileWorkflowTests` (its six tests);
- `proofs/postgres-ordering/tests/test_discovery_offline.py`: `DiscoveryJobDirectory`, `DiscoveryScanTests.test_the_values_are_every_secret_file_of_the_job`, and `DiscoveryWorkflowTests` (its seven tests, `test_the_suite_runs_after_the_profile_suite` among them);
- `services/api/tests/test_toolchain_pins.py`: its counts follow the file; its rule does not change.

Before you start, repeat the search at your own commit: every test that reads `foundation.yml`, `ci-and-branch-policy.md` or a scan's file list. If it finds one not named here, stop and report.

## 4. Checks, then the report

- **The trusted classifier,** from `main` (`c2cffbe`), extracted outside your checkout and run with `python3 -I` and full SHAs: `python3 -I <trusted copy>/change_scope.py --base c2cffbe6022637331d73e3558429ff70ab5aa5e3 --head <your code head> --merge-base` prints `"full": true` (reason `behavior-or-empty`).
- **The diff:** `git diff --name-only <START_SHA> <your head>` lists only A0's owned paths.
- **The workflow parses,** checked with a YAML reader from the repository's own locked modules (for example `js-yaml` from `apps/mobile`'s locked modules after `npm ci --ignore-scripts`), and each new job's steps are listed beside today's, step for step, in the record.
- **The run of record,** on your last code commit: each suite's job passed within its timeout, the gate passed and printed "Application checks passed", and the Mobile checks passed.
- **Every offline test** of `proofs/postgres-ordering` and `services/api` passes locally in a clean environment, and in the run.

Your final message, which Nathan relays:
- your branch and head;
- the record's path;
- the run of record's link and result, with each job's duration;
- what you built, by item;
- each earlier test changed;
- every stop, limit and deviation.

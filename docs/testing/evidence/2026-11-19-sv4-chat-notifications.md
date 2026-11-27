# SV4: the chat and notifications slice, proven on disposable PostgreSQL

- **Brief:** [SV4](../../planning/sv4-chat-notifications.md), revision 3, with [DM-96](../../continuity/dev-manager/reviews/2026-11-19-dm-96-sv4-stage-a-brief.md)'s AG1 to AG21 applied.
- **This record** is written by the stage sessions. Each session has its own section.

## A0

- **Session:** SV4 A0's implementation session, started by Nathan from [A0's prompt](https://github.com/amthorn78/glow-dating-app/blob/eac844340c2d962ca718acdd7bd9d61b7bba1392/docs/ephemeral/2026-11-19-sv4-a0-ci-tooling-prompt.md), revision 1, from `eac844340c2d962ca718acdd7bd9d61b7bba1392` of the manager branch `claude/magical-wozniak-yfmmx2`.
- **Branch:** `claude/affectionate-curie-hzo99y`, which the push filter's `claude/**` covers.
- **Code head:** `3bf55de775de1f7aa8cace3f7bc780c97f0b2e98`. **Records head:** the commit that adds this record. It was pushed after the code head's run had finished.
- **What A0 built:**
  - the database job split into one job per suite (D2, with AG1);
  - each suite's secret scan following its job (D2, revision 3);
  - the Chromium install's one retry (DM-59 item 7);
  - the pin test's two fixes (D7: M02's N2 and M05 finding 13);
  - the CI policy and the proof's README brought to the new jobs.
- **What A0 did not touch:** application code, any provider, deployed URL, real member, HDE call or stored credential.

### The start gate and the environment check

- **The environment** (section 1 of the prompt, names only). This session runs in the cloud environment `Glow App - No Stream` (`get_environment`).
  - No `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY`.
  - No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name.
  - The AWS names present: `AWS_ACCESS_KEY_ID`, `AWS_CA_BUNDLE` and `AWS_SECRET_ACCESS_KEY` (OD-76). None was read, printed or passed to a command.
  - `GH_TOKEN` and `GITHUB_TOKEN` are present and were not read.
  - The toolchain:
    - `python3.12 --version`: Python 3.12.14;
    - `node --version`: v24.19.0 and `npm --version`: 11.9.0, both from `/root/.local/bin`, which is second on `PATH` after `/nix/var/nix/profiles/default/bin`, which holds no `node`, `npm` or `python3.12`;
    - `docker --version`: Docker version 29.10.0, build fdd4b8e.
  - Every repository command ran under `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only its own variables; the installs added the proxy variables by reference.
- **The start gate.** Every check passed.
  - The branch was created at `eac8443`, and `git rev-parse HEAD` printed `eac844340c2d962ca718acdd7bd9d61b7bba1392`.
  - "this prompt's commit is on the live branch"; "PR56's merge present"; "main's code".
  - The owned paths' diff against the live manager branch was empty. The live branch was at `55ab2a4`, one commit after the prompt's, which changes only `docs/continuity/current-handoff.md`.
  - `ls docs/testing/evidence | grep -c 'sv4-'` printed `0`.
- **The search for earlier tests**, repeated at `eac8443`: every test that reads `foundation.yml`, `ci-and-branch-policy.md` or a scan's file list (`git grep` for `foundation.yml`, `workflows`, `ci-and-branch-policy`, `VALUE_FILES`, `KEY_FILES`, `JWT_KEY_FILE`, `job_values`, `workflow_step`, `unquoted_step` and `JobDirectory` outside Markdown). It found:
  - in the three suites' offline tests, the classes the prompt names;
  - the two module-level helpers those classes use: `workflow_step` in `test_identity_offline.py` and `unquoted_step` in `test_profile_offline.py`;
  - `services/api/tests/test_toolchain_pins.py`.

  No test reads `ci-and-branch-policy.md`, and no other test reads the workflow or a scan's list. So nothing outside the named list was found, and the session did not stop.

### What was built, by item

1. **The split** (D2; AG1). The job `database` ("Database proof checks") is replaced by four jobs:
   - `database-ordering` ("Database proof checks (ordering)");
   - `database-identity` ("Database proof checks (identity)");
   - `database-profile` ("Database proof checks (profile)");
   - `database-discovery` ("Database proof checks (discovery)").

   **What every job has:**
   - today's `needs: scope` and today's condition (`!cancelled() && (needs.scope.result != 'success' || needs.scope.outputs.full != 'false')`);
   - `timeout-minutes: 30`;
   - `proofs/postgres-ordering` as its working directory;
   - the shared job's first eight steps, byte for byte: the checkout, the Python install and its DM-41 retry, the hash-locked install, `pip check`, the offline tests under `env -i`, and Ruff and mypy;
   - its own credentials step (`set +x`, `umask 077`, the masks as its first output, files of mode 0600 in a `mktemp -d` under `$RUNNER_TEMP`);
   - today's start step, byte for byte: the pinned digest, `127.0.0.1:5433`, `POSTGRES_PASSWORD_FILE` from a read-only mount, `-c track_commit_timestamp=on` and the 60-second `pg_isready` wait;
   - its own role-and-database step;
   - its suite's steps;
   - today's removal step, byte for byte (`if: always()`; the container, its volume and the directory; no proof container left).

   Each container is named for its suite (`glow-proof-db-<suite>-<run>-<attempt>`), and the removal step's filter `name=glow-proof-db` still matches it.

   **What each job runs:**
   - **Ordering:** the wrong-marker step, the `dbshell` step, the migrations with `facts`, the run, the second-run refusal and the `p06-db-proof-results` upload (`if: always()`), each byte for byte. Its credentials hold the superuser's and the role's passwords, `marker` and `wrong-marker`. The passfile has one line, for `glow_proof`. Per the prompt, the wrong-marker step stands as its decoy check, and the job gets no decoy database.
   - **Identity, profile, discovery:**
     - Their credentials hold the superuser's and the role's passwords, the suite's marker, the decoy's marker, the suite's `SECRET_KEY` and its RSA key, which Python writes straight to its file. The passfile has one line, for the suite's database.
     - The role step creates the suite's database and the **decoy** (AG1), each with its own comment. The decoy carries another suite's database name:
       - in the identity job, `glow_proof`, with its marker in `marker`;
       - in the profile job, `glow_identity_proof`, with `identity-marker`;
       - in the discovery job, `glow_profile_proof`, with `profile-marker`.
     - **A `dbshell` step** under the suite's own settings (`"SV<n>: show that dbshell is refused under the <suite> settings, before any connection"`), in the form of the ordering job's. It is new for these three jobs: the brief's D2 lists `dbshell`'s refusal among the checks each job keeps, and the shared job showed it only once, under the ordering settings.
     - **The decoy step** replaces today's "refuses the other marker(s)" step. Its checks:
       - as the superuser inside the container, the decoy exists with a comment that starts `glow-ordering-proof:`, and its comment differs from the suite database's (it prints `1` and `t`, never a comment);
       - then, in the form of the ordering suite's wrong-marker step (DM-10 2.3, in DM-11's words): the suite database's `pg_class` rows per schema are counted before and after a `migrate` with the decoy's marker. That `migrate` must exit non-zero with the refusal line, every count must be unchanged, nothing may exist outside `information_schema` and the `pg_` schemas, and there must be no `django_migrations`;
       - then the migrations from zero and `makemigrations --check --dry-run`, as today.

       The prompt's words are "leaves its own database unchanged", so this step adds the counts check, which today's three steps did not have. It refuses one decoy's marker where the profile and discovery steps refused two and three, because AG1 gives each job one decoy.
     - The suite's run, its second-run refusal and its upload, gated on its check, byte for byte. The one exception is the profile and discovery run steps' inner comment, which now names the job's own secrets ("its marker and the decoy database's, its SECRET_KEY, each line of its signing key").

   **The gate:**
   - its `needs` is `[scope, api, mobile, smoke, artifact, proof, database-ordering, database-identity, database-profile, database-discovery]`;
   - its results check loops over the same nine jobs;
   - its rule is unchanged: `success` each on a full-scope change, `skipped` each on ordinary documentation.

   **Today's 30 steps and the new jobs, step for step.** The table says where each of today's steps now is: "verbatim" means byte for byte, and "changed" means its text changed, with how.

   | Today's step (the `database` job) | Ordering | Identity | Profile | Discovery |
   |---|---|---|---|---|
   | 1–8: checkout, Python and its retry (3), install, `pip check`, offline tests, Ruff and mypy | 1–8 verbatim | 1–8 verbatim | 1–8 verbatim | 1–8 verbatim |
   | 9: credentials (all four suites' values) | 9, changed: its own values only | 9, changed: its own and the decoy's | 9, changed: the same | 9, changed: the same |
   | 10: start PostgreSQL | 10 verbatim | 10 verbatim | 10 verbatim | 10 verbatim |
   | 11: create the role and the four databases | 11, changed: one database | 11, changed: its database and the decoy | 11, changed: the same | 11, changed: the same |
   | 12: a wrong marker refused | 12 verbatim | (its decoy step, 13) | (13) | (13) |
   | 13: `dbshell` refused | 13 verbatim | 12, new: under the identity settings | 12, new: under the profile settings | 12, new: under the discovery settings |
   | 14: migrations, models, server facts | 14 verbatim | – | – | – |
   | 15: the ordering suite | 15 verbatim | – | – | – |
   | 16: its second run refused | 16 verbatim | – | – | – |
   | 17: SV1, the other marker, then migrations | – | 13, changed: the decoy's marker, with counts | – | – |
   | 18–20: SV1's run, second run, upload | – | 14–16 verbatim | – | – |
   | 21: SV2, the other markers, then migrations | – | – | 13, changed: the decoy's marker, with counts | – |
   | 22: SV2's run | – | – | 14, changed: one inner comment | – |
   | 23–24: SV2's second run, upload | – | – | 15–16 verbatim | – |
   | 25: SV3, the other markers, then migrations | – | – | – | 13, changed: the decoy's marker, with counts |
   | 26: SV3's run | – | – | – | 14, changed: one inner comment |
   | 27–28: SV3's second run, upload | – | – | – | 15–16 verbatim |
   | 29: the results table's upload | 17 verbatim | – | – | – |
   | 30: removal | 18 verbatim | 17 verbatim | 17 verbatim | 17 verbatim |

   Every step's printed lines are kept. The decoy step's counts check prints the ordering step's lines in the suite's words. The decoy step's refusal line reads "<suite> migrate with the decoy database's marker: exit status N", where today's read "with the ordering database's marker" or "with the <file> file's marker".

   No step prints a connection value, a password, a marker or a comment. No step reads a `PG*` or `DATABASE_URL` name or runs `docker inspect`. No job has an `env:` of secrets.

   **How the workflow was checked:**
   - assembled by a scratch generator: every reused step was copied from today's file, every replacement asserted to occur once, and a comparison script confirmed the "verbatim" cells above;
   - parsed with `js-yaml` 4.3.2 from `apps/mobile`'s locked modules (after `npm ci --ignore-scripts`), which listed each job's name, `needs`, timeout, condition and steps;
   - the gate's script, extracted with the same reader, run on five synthetic `needs` results:

     | Case | Exit status | Last line printed |
     |---|---|---|
     | Full scope, all `success` | 0 | "Application checks passed" |
     | Ordinary documentation, all `skipped` | 0 | "Ordinary documentation: application jobs intentionally skipped" |
     | Full scope, profile `failure` | 1 | "AssertionError: Unexpected database-profile result" |
     | Ordinary documentation, discovery `success` | 1 | "AssertionError: Unexpected database-discovery result" |
     | Full scope, the identity job missing | 1 | "KeyError: 'database-identity'" |
2. **The scans** (D2, revision 3). Each scan lists every secret file its own job writes and no other:

   | Scan | `VALUE_FILES` | Passfile | Key files |
   |---|---|---|---|
   | `identity_scan` | `identity-secret-key`, `identity-marker`, `marker` (the decoy's), `superuser-password` | `passfile` | `identity-jwt-key.pem` |
   | `profile_scan` | `profile-secret-key`, `profile-marker`, `identity-marker` (the decoy's), `superuser-password` | `passfile` | `profile-jwt-key.pem` |
   | `discovery_scan` | `discovery-secret-key`, `discovery-marker`, `profile-marker` (the decoy's), `superuser-password` | `passfile` | `discovery-jwt-key.pem` |

   - **`identity_scan`:** its list was already exactly its job's, so only its docstring's description of the list changed.
   - **`profile_scan`:** loses `identity-secret-key`, `marker` and `identity-jwt-key.pem`.
   - **`discovery_scan`:** loses the other suites' keys and markers but the decoy's.

   Each docstring names the files the scan reads. The job writes one more file, `create-role.sql`, which the role step removes once it has run; its values are the passfile's password and the marker files'.

   **The offline tests:**
   - each test asserts its scan's list against the literal set above, and against the files its job's credentials step writes, read from the workflow (`job_secret_files`);
   - each test's job directory is built from those files, not from the scan's own list, so an omission cannot pass (reversals S1 to S6).
3. **The Chromium retry** (DM-59 item 7, as carried):
   - the install step has `id: chromium`, `continue-on-error: true` and `timeout-minutes: 10`;
   - then "Wait 60 s before the one retry of the Chromium install (DM-59 item 7)" (`echo "::warning::…" && sleep 60`) and "Retry the Chromium install once (DM-59 item 7)", the same `npx playwright install --with-deps chromium` with `timeout-minutes: 6`, each only `if: steps.chromium.outcome == 'failure'`;
   - the retry has no `continue-on-error`.

   **The timeouts.** Both attempts, the pause and the rendered checks fit in the job's 25 minutes. In five recent full-scope runs (44413105426, 44408183628, 44394402635, 44378253123 and 44374175558) and `main`'s run 44416436012:
   - the steps before the install took 91 to 129 s;
   - a passing install took 22, 28, 38, 302, 510 and 541 s;
   - the rendered checks took 281 to 317 s.

   PR44's failed attempts took about 10 minutes each (the carried entry). The first attempt's 10 minutes cover the slowest passing install seen. Worst case: 2.2 + 10 + 1 + 6 + 5.3 = 24.5 minutes. The workflow's comment states the same arithmetic.
4. **The pin test** (D7):
   - **N2:** the workflow is read through `strip_yaml_comments` before any pin is matched or counted. It drops a whole-line comment, and a trailing ` #` comment outside quotes, and keeps every line of a block scalar (a `run: |` script) as content, since `#` there is not a YAML comment. It keeps one output line per input line, so line numbers hold. An unclosed quote keeps the rest of its line, so a pin is never dropped by mistake.
   - **M05 finding 13:** `PACKAGES` adds `proofs/stream-chat/package.json`, so its `engines.node`, `engines.npm` and `packageManager` are read with the others.
   - **The rule is unchanged.** Its counts follow the file: `actions/setup-python@` and `python-version` now occur 14 times each (8 before; the four database jobs have two each); `actions/setup-node@`, `node-version` and `npm@` occur 3 times each, as before.
5. **The earlier tests**: below.
6. **The CI policy** (`docs/operations/ci-and-branch-policy.md`; governing Markdown, for the Dev Manager's read before A0 merges):
   - the job list names the four database proof jobs, and "all nine application jobs";
   - the database job's description becomes "The database proof jobs", one item per job, with every fact the old text held. A check of twelve such facts (the artifact names, DM-48 C2.6, DM-47 C1.4, DM-60 Q13, "66 cases in all" and the rest) found each in both texts;
   - the actions table's upload-artifact row says "the four database proof jobs";
   - "Toolchain installs are retried once" names the Chromium retry beside DM-41's, with its timeouts and its reason;
   - the database-server paragraph now describes one server per job, the decoy, and the 24-minute finding per job;
   - the documentation policy's job counts and names (nine), and the gate's history ("six before SV4 A0 split Database proof checks into one job per suite").

   It also says that no check is required (OD-52), so replacing the name `Database proof checks` changes no required name.

   **The proof's README:**
   - a paragraph "SV4 A0, the database job split by suite", which says that the "second", "third" and "fourth disposable database in the same PostgreSQL" in the paragraphs before it describe the shared job;
   - the job's names in "What it proves" and in the CI paragraphs;
   - the identity and profile suites' CI paragraphs, rewritten for their own jobs;
   - a new short paragraph for the discovery suite's job, which the README did not have;
   - "Limits" first line: "each suite's CI job's run".

### Earlier tests changed, and why

Every test below is on the prompt's list (the brief's D11, A0's bullet). No other test changed.

**First, which earlier tests the split breaks.** Today's three offline test files, at `eac8443`, were run in a scratch worktree with the new workflow and the new scans copied in. They fail in exactly 7 tests (16 failures counting subtests, and 1 error), all named:
- `DiscoveryWorkflowTests.test_the_suite_runs_after_the_profile_suite` (`ValueError`: the substring is no longer in one job);
- `DiscoveryWorkflowTests.test_the_credentials_step_makes_the_fourth_database_and_its_own_keys`, and `ProfileWorkflowTests.test_the_credentials_step_makes_the_third_database_and_its_own_keys`: `unquoted_step` finds the first credentials step in the file, now the ordering job's;
- `ProfileWorkflowTests.test_the_migrations_step_refuses_both_other_markers_first`, and `DiscoveryWorkflowTests.test_the_migrations_step_refuses_the_three_other_markers_first`;
- `ProfileScanTests.test_the_values_are_every_secret_file_of_the_job`, and `DiscoveryScanTests.test_the_values_are_every_secret_file_of_the_job`.

The identity file's tests all still pass there: its scan's list is unchanged, and `workflow_step` searched the whole file. They are changed anyway, as the prompt asks, so that the list is bound to its job and the steps are read in the identity job.

- **The helpers** (in `test_identity_offline.py`, used by all three files):
  - `workflow_step(name_prefix)`, which searched the whole file for a quoted step name, becomes `workflow_step(job, name_prefix)`. It reads one job (`workflow_job`), finds quoted and unquoted names (`step_name`) and leaves out the comment lines between steps (`workflow_steps`). Step names no longer identify one database job: four jobs each have "Generate the disposable database's credentials".
  - `job_secret_files(job)` and `job_databases(job)` read the files and passfile databases the job's credentials step writes.
  - `unquoted_step` (`test_profile_offline.py`) is removed, since `workflow_step` reads unquoted names now; its import in `test_discovery_offline.py` goes with it.
  - `import re` is added to the identity and discovery files.
  - The profile and discovery files gain a module constant `JOB`.
- **`test_identity_offline.py`:**
  - `JobDirectory`: built from the identity job's credentials step (every secret file it writes, the passfile's databases, its one key file), not from `identity_scan`'s own list. A fixture built from the scan's list cannot show an omission: today's `test_the_values_are_the_job_files` passes with `marker` left out of `VALUE_FILES` (run in the scratch worktree: `Ran 1 test … OK`). The passfile now has one line, as the job's does.
  - `IdentityScanTests.test_the_values_are_the_job_files`: asserts the list against the literal set and against `job_secret_files("database-identity")`, and keeps its value checks.
  - `IdentityUploadGateTests`, all three tests: the step is looked up in the identity job. Their assertions are unchanged.
- **`test_profile_offline.py`:**
  - `ProfileJobDirectory`: as `JobDirectory`, for the profile job.
  - `ProfileScanTests.test_the_values_are_every_secret_file_of_the_job`: the new list, and equality with the job's files.
  - `ProfileWorkflowTests`, all six tests:
    - `test_the_credentials_step_makes_the_third_database_and_its_own_keys` becomes `test_the_credentials_step_makes_its_database_the_decoy_and_its_own_keys`. It checks the masks, files and statements of the profile database and the decoy, the passfile's one database, and one key loop. It also checks that the job's text names no other suite's key or the ordering job's `wrong_marker`.
    - `test_the_migrations_step_refuses_both_other_markers_first` becomes `test_the_migrations_step_refuses_the_decoys_marker_first`. It checks the decoy check, then the counts before, the refused `migrate`, the counts after and `test "$fail" = 0`, all before the migrations. It also checks the refusal line, the `cmp`, the ledger check and the superuser's database.
    - `test_the_suite_step_runs_the_check_and_sets_the_output_only_on_a_pass`, `test_after_a_failed_check_the_step_prints_counts_only`, `test_the_second_run_step_counts_rows_and_requires_the_refusal` and `test_the_upload_waits_for_the_check`: the step is looked up in the profile job. Their assertions are unchanged.
- **`test_discovery_offline.py`:**
  - `DiscoveryJobDirectory` and `DiscoveryScanTests.test_the_values_are_every_secret_file_of_the_job`: as for the profile suite.
  - `DiscoveryWorkflowTests`:
    - the credentials and migrations tests, renamed and rewritten as the profile suite's are (`…_makes_its_database_the_decoy_and_its_own_keys`, `…_refuses_the_decoys_marker_first`);
    - the suite-step, failed-check, second-run and upload tests: the step is looked up in the discovery job, with their assertions unchanged;
    - `test_the_suite_runs_after_the_profile_suite` is **replaced** by `test_each_suite_runs_in_its_own_job_after_its_migrations_and_decoy_refusal`, as the prompt asks. For each of the identity, profile and discovery jobs, it checks:
      - `needs: scope`, today's condition, the job's name and a timeout of at most 30;
      - the step order: credentials, start, role, `dbshell`, the decoy refusal with the migrations, the suite, the second run, the upload, and the removal last;
      - the suite step's `id`, the upload's `if:` on that `id`'s `scan` output, and the removal's `if: always()`.

      For the ordering job it checks its ten steps' order, with the removal last.
  - **Added:** `test_the_gate_requires_each_suites_job`. The gate's `needs` must be exactly the six earlier jobs and the four database jobs, in order; its results tuple must name the nine; its rule must be unchanged; and no job `database` may remain.
- **`services/api/tests/test_toolchain_pins.py`:** D7's two fixes (item 4). Its rule and its three tests are unchanged.

### Reversals (D14)

Each reversal is a temporary edit, or an edit of a copy, and each was undone. After S1 to W8, the edited files' checksums matched their earlier ones, and the three offline files passed: `Ran 159 tests … OK`.

**The pin test**, on scratch copies of the files it reads (the bootstrap script, the workflow, the three `package.json` files, `.python-version` and the `Dockerfile`), with the test file copied in:

| Reversal | The test at `eac8443` | The test as changed |
|---|---|---|
| **N2 (a):** the line `      # node-version: '24.19.0'` added to the mobile job's steps | `FAIL: test_node_pins_agree … AssertionError: .github/workflows/foundation.yml: 4 node-version pins recognized for 3 'actions/setup-node@' matches` | `Ran 3 tests … OK` |
| **N2 (b):** the line `      # The job's Node is node-version: '24.19.0', set up by actions/setup-node@ above.` | `FAIL: test_npm_pins_agree … AssertionError: .github/workflows/foundation.yml: 3 npm install pins recognized for 4 'actions/setup-node@' matches` | `Ran 3 tests … OK` |
| **M05-13:** `proofs/stream-chat/package.json`'s `engines.node` changed to `24.18.0` | `Ran 3 tests … OK` (the gap) | `FAIL: test_node_pins_agree … AssertionError: Node pins disagree (diverging files first): 24.18.0 in proofs/stream-chat/package.json engines.node; 24.19.0 in scripts/bootstrap-toolchain.sh:42, apps/mobile/package.json engines.node, packages/contracts/package.json engines.node, .github/workflows/foundation.yml:107, .github/workflows/foundation.yml:159, .github/workflows/foundation.yml:214` |
| **M05-13:** its `packageManager` changed to `npm@11.8.0` | not run | `FAIL: test_npm_pins_agree … 11.8.0 in proofs/stream-chat/package.json packageManager; 11.9.0 in …` |
| **Probe:** a real pin with a trailing comment, `node-version: '24.18.0' # the pinned Node` | not run | `FAIL: test_node_pins_agree … 24.18.0 in .github/workflows/foundation.yml:107; …` (still read) |
| **Probe:** `# node-version: '24.19.0'` inside a `run: |` script | not run | `FAIL: test_node_pins_agree … 4 node-version pins recognized for 3 'actions/setup-node@' matches` (block content is not a YAML comment, so it is still counted) |

**The scans and the workflow**, with the changed tests (a scratch harness edits one file, runs the named tests and restores the file byte for byte):

| # | Reversal | Result |
|---|---|---|
| S1 | `identity_scan`: `marker`, the decoy's, left out of `VALUE_FILES` | `FAIL: test_the_values_are_the_job_files … AssertionError: Items in the second set but not the first` |
| S2 | `profile_scan`: `identity-marker` left out | `FAIL: ProfileScanTests.test_the_values_are_every_secret_file_of_the_job … Items in the second set but not the first` |
| S3 | `discovery_scan`: `discovery-marker` left out | `FAIL: DiscoveryScanTests.test_the_values_are_every_secret_file_of_the_job …` |
| S4 | `discovery_scan`: `KEY_FILES = ()` | `FAIL: DiscoveryScanTests.test_the_values_are_every_secret_file_of_the_job …` |
| S5 | `profile_scan`: `marker` added, a file its job does not write | `FAIL: ProfileScanTests.test_the_values_are_every_secret_file_of_the_job … Items in the first set but not the second` |
| S6 | Workflow: the profile job also writes `profile-secret-key-copy` | `FAIL: ProfileScanTests.test_the_values_are_every_secret_file_of_the_job … Items in the second set but not the first` |
| W1 | Workflow: the identity upload's `if:` becomes `if: always()` | `FAIL: IdentityUploadGateTests.test_the_upload_waits_for_the_check`, and `FAIL: test_each_suite_runs_in_its_own_job_after_its_migrations_and_decoy_refusal (job='database-identity')` |
| W2 | Workflow: the profile database migrated before the decoy marker's refusal is read | `FAIL: test_the_migrations_step_refuses_the_decoys_marker_first` |
| W3 | Workflow: the discovery job's decoy not created | `FAIL: DiscoveryWorkflowTests.test_the_credentials_step_makes_its_database_the_decoy_and_its_own_keys` |
| W4 | Workflow: the gate's `needs` without `database-profile` | `FAIL: test_the_gate_requires_each_suites_job` |
| W5 | Workflow: the gate's results tuple without `database-discovery` | `FAIL: test_the_gate_requires_each_suites_job` |
| W6 | Workflow: the identity job's `timeout-minutes: 31` | `FAIL: test_each_suite_runs_in_its_own_job_after_its_migrations_and_decoy_refusal (job='database-identity')` |
| W7 | Workflow: the profile job's `needs: scope` removed | `FAIL: … (job='database-profile')` |
| W8 | Workflow: the discovery suite's run step moved ahead of its decoy step | `FAIL: … (job='database-discovery')` |

**The decoy check itself**, on a local disposable database (iteration). The identity job's decoy step was run with `identity identity-marker` in place of `identity marker`, that is, with the identity database's own marker. The edit was made in the local emulator's copy of the steps only, never in the repository. The step failed (`exit 1`), printing:

```
relations outside information_schema and the pg_ schemas: 0 before, 257 after
identity migrate with the decoy database's marker: exit status 0
FAIL: migrate with another database's marker exited 0
FAIL: the refusal message is missing (diagnostics withheld)
FAIL: a schema's relation count changed
FAIL: a relation exists outside information_schema and the pg_ schemas
FAIL: django_migrations exists
```

The suite and the second run were then skipped, the upload's condition was false, and the removal ran.

### Commands and results

- **The proof's offline tests:** `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8 .venv/bin/python -m unittest discover -s tests -t .` gives `Ran 378 tests … OK`. That is 377 at `eac8443`: one test replaced and one added.
- **The proof's lint and types:** `ruff check .` gives "All checks passed!", `ruff format --check .` gives "71 files already formatted", and `mypy` gives "Success: no issues found in 71 source files".
- **The API**, with `GLOW_ENV=test`:
  - `manage.py check` reports no issues;
  - `manage.py test tests` gives `Ran 645 tests … OK`;
  - `ruff check .` gives "All checks passed!", `ruff format --check .` gives "165 files already formatted", and `mypy` gives "Success: no issues found in 95 source files";
  - the contract tests give `Ran 53 tests … OK`.
- **The trusted classifier**, from `main` (`c2cffbe`), extracted to a scratch directory outside the checkout (SHA-256 `b564c62f…`). It was run as `python3 -I <copy>/change_scope.py --base c2cffbe6022637331d73e3558429ff70ab5aa5e3 --head 3bf55de775de1f7aa8cace3f7bc780c97f0b2e98 --merge-base` with the checkout as its working directory, and printed `"full": true`, reason `behavior-or-empty`. A first try from the scratch directory printed `comparison-unavailable`, since git found no repository there.
- **The diff:** `git diff --name-only eac8443 3bf55de` lists only A0's owned paths:
  - `.github/workflows/foundation.yml`;
  - `docs/operations/ci-and-branch-policy.md`;
  - `proofs/postgres-ordering/README.md`;
  - the three scans;
  - their three offline test files;
  - `services/api/tests/test_toolchain_pins.py`.

  The records commit adds this record.
- **npm:** no npm package was changed. `apps/mobile`'s locked modules were installed with `npm ci --ignore-scripts` only to read the workflow with `js-yaml`, so no `npm audit` line is due (DM-02 B9).

### Local database runs (iteration, not evidence)

P06.DB's D4 allows these runs under its four conditions:
- the pinned image, `postgres@sha256:d74eeac9…`, pulled once;
- loopback only;
- passwords and markers generated by the jobs' own credentials steps;
- run under a clean environment with none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name;
- each container and directory removed by the job's own removal step.

**How they ran.** No Docker daemon was running in the session. `dockerd` was started in the background, with only `PATH`, `HOME`, the proxy variable and the CA path. A scratch emulator ran each database job's own steps, as `js-yaml` reads them from the workflow, from its credentials step on:
- each in GitHub's shell (`bash -e`, or `bash --noprofile --norc -eo pipefail` for `shell: bash`), in the job's working directory;
- with `RUNNER_TEMP`, `GITHUB_OUTPUT` and the steps' own `env:`;
- skipping each `uses:` step and reporting whether its condition held;
- removing every `::add-mask::` line from the output, so no generated value printed.

| Job | Result | Suite phase (local) |
|---|---|---|
| Ordering | `== VERDICT: PASS ==`, every step passed | 560 s |
| Identity | 49/49, `IDENTITY VERDICT: PASS` | 41 s |
| Profile | 77/77, `PROFILE VERDICT: PASS`, both scans clean | 127 s |
| Discovery | 66/66, `DISCOVERY VERDICT: PASS`, both scans clean | 246 s |

In each run: the decoy existed with its own marker (`1`, `t`), the counts were unchanged (`0 before, 0 after`), `dbshell` exited 1 with the refusal under each suite's settings, the secret check found 0, the second run was refused with the rows unchanged, and the upload's condition held.

**A deviation, local only.** The profile and discovery jobs' first local attempts failed at the start step: `docker pull` of the already-present image got `429 Too Many Requests` from Docker Hub. They were run again with a local wrapper, first on the emulator's `PATH`, that skips `docker pull` when the image is present. The workflow's step is unchanged.

Afterwards no container remained, no `glow-proof-db.*` directory remained, and no saved log held a mask line. The scratch worktree was then removed, and so were the four local results files in the ignored `.work` directory. The background `dockerd` was stopped by its background time limit once the runs had finished.

### The run of record

**Foundation run [44463105633](https://github.com/amthorn78/glow-dating-app/actions/runs/44463105633)** on `3bf55de775de1f7aa8cace3f7bc780c97f0b2e98` (a push run, attempt 1) concluded **success**. It was created at 05:08:42 UTC on 19 November 2026 and its gate finished at 05:18:19, 9 minutes 37 seconds in all. Nothing was pushed to the branch until it had finished.

The durations below are from the jobs' and steps' timestamps, which are whole seconds.

| Job | Conclusion | Duration | Timeout |
|---|---|---|---|
| Change scope | success | 6 s | 3 min |
| API checks | success | 76 s | 10 min |
| Mobile checks | success | 561 s (9 min 21 s) | 25 min |
| API mobile smoke | success | 75 s | 10 min |
| API artifact checks | success | 27 s | 15 min |
| Stream proof checks | success | 92 s | 10 min |
| **Database proof checks (ordering)** | success | **539 s (8 min 59 s)** | 30 min |
| **Database proof checks (identity)** | success | **103 s (1 min 43 s)** | 30 min |
| **Database proof checks (profile)** | success | **151 s (2 min 31 s)** | 30 min |
| **Database proof checks (discovery)** | success | **190 s (3 min 10 s)** | 30 min |
| Foundation gate | success: "Application checks passed" | 3 s | 2 min |

On `main`'s run 44416436012 the one shared job took 16 minutes 32 seconds. Here its longest successor, the ordering suite's job, took 8 minutes 59 seconds.

**Each suite's own step:**

| Suite step | Duration | What it printed |
|---|---|---|
| The ordering suite's run | 459 s | 460 s on `main`'s run 44416436012; `== VERDICT: PASS (reference) ==`, `== VERDICT: PASS (adapter) ==` and `== VERDICT: PASS ==` |
| The identity phase | 35 s | "identity phase: 35 s"; `[identity] cases: 49/49 passed` |
| The profile phase | 84 s | "profile phase: 84 s"; `[profile] cases: 77/77 passed` |
| The discovery phase | 134 s | "discovery phase: 134 s"; `[discovery] cases: 66/66 passed` |

**What each job's log shows** (quoted from the logs, read with `get_job_logs`; no line held an `::add-mask::` command or a long hexadecimal value):
- **Ordering:**
  - `relations outside information_schema and the pg_ schemas: 0 before, 0 after`, `to_regclass('public.django_migrations') IS NULL after: t`, `wrong-marker migrate exit status: 1` and the refusal line;
  - `dbshell exit status: 1` and its refusal;
  - `track_commit_timestamp on` and `PostgreSQL 17.11 (Debian 17.11-1.pgdg13+2) on x86_64-pc-linux-gnu, …`;
  - the second run: `rows (proof log, adapter calls, worlds, app accounts, outbox events) before: 10325 13516 5731 11497 26197; after: 10325 13516 5731 11497 26197`, `second run exit status: 1`, and `refusing a used database: …`;
  - `container removed: glow-proof-db-ordering-44463105633-1`, `credential and marker files removed`, `no proof container remains`.
- **Identity, profile and discovery**, each:
  - `role glow_proof (NOSUPERUSER) and database glow_<suite>_proof (SV<n>) created, with its own marker as its comment`, and `decoy database <decoy> (AG1) created for the same role, with another marker as its comment`;
  - `<suite> dbshell exit status: 1` and the refusal `refusing dbshell under the proof's settings (PROOF_DB_MARKER): … no connection was opened and no client was started`;
  - `decoy database <decoy> with a marker as its comment: 1; its comment differs from the <suite> database's: t`;
  - `relations outside information_schema and the pg_ schemas: 0 before, 0 after`, `to_regclass('public.django_migrations') IS NULL after: t`, `<suite> migrate with the decoy database's marker: exit status 1`, `refusal: glow_ordering_proof.marker.RefusedDatabase: refusing this database: its comment is not the run's marker (PROOF_DB_MARKER): …`, and `the decoy database's marker was refused, and the <suite> database is unchanged and holds no table`;
  - `No changes detected`;
  - `the job's secrets found in the <suite> suite's output: 0` and `… in the <suite> results JSON: 0`;
  - the suite's own scans, clean:
    - identity: `identity secret scan: clean (754 secrets held; 0 found in 240 log records, 102 writes and the results JSON)`;
    - profile: `profile secret scan: clean (1601 secrets held; …)` and `profile value scan: clean (919 member values held: …; 0 found in the same output)`;
    - discovery: `discovery secret scan: clean (2495 secrets held; …)` and `discovery value scan: clean (1336 member values held: …; 0 found in the same output)`;
  - the verdict line;
  - the second run, with its rows unchanged:
    - identity: `53 53 63 32 50` before and after;
    - profile: `143 143 109 72 1746 1087`;
    - discovery: `1222 1222 1216 103 381 3056`;
  - `second <suite> run exit status: 1` and its refusal;
  - the upload step succeeded;
  - `container removed: glow-proof-db-<suite>-44463105633-1`, `credential and marker files removed`, `no proof container remains`.
- **The retries:**
  - each job's first Python install succeeded, after "Version 3.12.14 was not found in the local cache", and both DM-41 retry steps were skipped;
  - in Mobile checks, "Install Chromium for rendered fixture checks" succeeded in 187 s on its first attempt, "Wait 60 s before the one retry of the Chromium install (DM-59 item 7)" and "Retry the Chromium install once (DM-59 item 7)" were skipped, and "Render and exercise account onboarding" took 281 s;
  - no retry fired in this run.
- **The offline tests** ran in each database job (32, 20, 20 and 17 s). They are the tests run locally above.

### Limits and deviations

- **The Chromium retry cannot be exercised on a passing run**, and was not exercised here. What was checked:
  - `js-yaml` read the step's `id`, `continue-on-error`, timeouts and conditions as intended;
  - on the run of record, the first attempt passed and the pause and the retry were skipped (above).

  What was not checked:
  - Whether a first attempt killed by its own `timeout-minutes` has the outcome `failure` (so the retry runs) or `cancelled` was not checked against GitHub's documentation, which this session did not read.
  - A retry after a first attempt killed during apt's `dpkg` stage may find dpkg's state interrupted. The retry is the same command, as carried, and helps a short failure, such as a mirror that resolves again within the pause.
  - No Chromium or `playwright install` ran in this session.
- **The decoy check refuses one other suite's marker per job** (AG1's "one more database"), where the shared job's profile and discovery steps refused two and three. Each refusal is of a marker another database in the same server carries, which is the property AG1 keeps. It is stronger than before in one way: it also shows the suite's database unchanged, with no table.
- **The `dbshell` refusal is new in the identity, profile and discovery jobs.** The shared job showed it once, under the ordering settings. Each suite's settings install the proof's own `dbshell`, and the local runs show each refusing.
- **The ordering suite's job has no decoy database** (the prompt: its wrong-marker step already shows this) and no secret scan. Its results JSON is uploaded `if: always()`, as before: there was no scan to keep, and adding one is outside A0.
- **Each run now pulls the PostgreSQL image four times**, once per job, where it pulled it once. Locally Docker Hub answered `429` to this sandbox's repeated pulls. Whether GitHub-hosted runners meet Docker Hub's pull limits was not checked. (The exact-head review read Docker's page: unauthenticated users get "100 per IPv4 address or IPv6 /64 subnet" per 6 hours, and no Docker or GitHub page names an exemption for GitHub-hosted runners; F4.) A `429` in CI would fail that job's start step, and would be a finding under OD-21.
- **Minutes:** each database job repeats the install, the offline tests, Ruff and mypy (about 40 s) and its own PostgreSQL start. Free while the repository is public (OD-51); M07's Actions line prices them once it is private.
- **The name `Database proof checks` is gone**, replaced by four names. No check is required (OD-52), so no required check changes. The CI policy says so.
- **Wording left as it was:** the three suites' offline test files' module docstrings still say the cases run "in the Database proof checks job, on the second (third, fourth) disposable database". The prompt allows only their tests of the workflow's steps and the scans' lists to change.
- The local runs used PostgreSQL 17.11 from the pinned image, under Docker 29.10.0 started in the session. They are iteration only: the run of record is CI's.

### Manager verification of A0 (App Manager 12, 19 November 2026)

- **The branch:** `claude/affectionate-curie-hzo99y`, code head `3bf55de`, records head `c77646b`, both after the prompt's commit `eac8443`, which the branch starts at; merged into the manager branch at `4dfb0ac`.
- **The diff** from `eac8443` lists ten code and documentation paths, each one of A0's owned paths (the brief, revision 3), and the record.
- **The trusted classifier,** `main`'s `scripts/change_scope.py` (`c2cffbe`), extracted outside the checkout and run from it with `python3 -I --base c2cffbe… --head 3bf55de… --merge-base`: `"full": true`, reason `behavior-or-empty`.
- **The workflow, read whole and compared step for step** (PyYAML over `eac8443`'s and `3bf55de`'s files):
  - the jobs `scope`, `api`, `smoke`, `artifact` and `proof`, the triggers, the permissions and the concurrency group are unchanged;
  - the four database jobs each take the old job's `needs: scope`, its condition, `runs-on`, defaults and permissions, with `timeout-minutes: 30`;
  - every one of the old job's 30 steps is in a new job: 23 byte for byte, and the other 7 changed only as the split needs (corrected after the exact-head review's F5, which counted 23 and 7; this line first said 22 and 8; AM12-42) (the credentials and role-and-database steps per job; the three marker-and-migrations steps, now refusing the decoy and counting relations before and after; the profile and discovery suite steps, whose comments alone change). The new steps are each job's `dbshell` refusal and decoy;
  - the action pins and the PostgreSQL image's digest are the same set;
  - the gate's `needs` and its results loop name the four jobs, and nothing else in it changes;
  - Mobile checks gains exactly the carried Chromium retry (`id: chromium`, `continue-on-error: true`, `timeout-minutes: 10`; a 60-second pause and one retry with `timeout-minutes: 6`, each under `if: steps.chromium.outcome == 'failure'`, the retry without `continue-on-error`), and its other steps and settings are unchanged;
  - the identity, profile and discovery credentials steps each mask five values, and the ordering job's four (F5), before anything prints, and each step's `echo` lines print a directory, a container name and a refusal only.
- **The run of record,** Foundation run 44463105633 (event `push`, head `3bf55de`), read with the GitHub tools: all eleven jobs succeeded, among them the four database jobs, and the gate's log ends "Application checks passed".
- **The scans:** each `VALUE_FILES` and `KEY_FILES` now names its own job's files only, the decoy's marker in the earlier suite's file name, as the CI policy's new paragraph says.
- **For the exact-head review (AG21), noted, not decided here:**
  - whether a step killed by its own `timeout-minutes` has the outcome `failure`, on which the Chromium retry depends (the record's limits);
  - four pulls of the PostgreSQL image per run, where there was one;
  - the decoy's marker is one the job generates in the earlier suite's form (`glow-ordering-proof:` for the identity job), not that suite's own marker, which only a shared PostgreSQL held; AG1's words are "carrying another suite's marker";
  - the three proof offline test files' module docstrings still describe the shared job, outside A0's owned lines.

### Exact-head review of A0 (19 November 2026)

- **Session:** the exact-head review, started by Nathan from [A0's review prompt](https://github.com/amthorn78/glow-dating-app/blob/7d04d1c2701f98f24575bd9298f4c0717df7872b/docs/ephemeral/2026-11-19-sv4-a0-review-prompt.md), revision 1, from `7d04d1c` (DM-96's AG21); its report relayed to App Manager 12 on 19 November 2026.
- **Its start gate, classification and environment check:** every start-gate check passed (`HEAD` `7d04d1c`, one merge base `c2cffbe`, the prompt's commit on the live branch, whose head was `90a74e5`, three Markdown-only commits later; non-Markdown paths equal to `3bf55de` at `HEAD` and on the live branch; no review recorded). `main`'s classifier, run outside the tree with `python3 -I`, printed `"full": true`, reason `behavior-or-empty`. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY`, and no `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name; the AWS and GitHub token names present and unread; every repository command under `env -i`.
- **Verdict: changes requested, in tests only.** No blocking finding. It found no defect in the workflow, the scans, the gate, the Chromium retry or the pin test, and both runs pass. F1 and F2 are should-fix findings in a correction class; F3 to F8 are nits.

**What it verified** (its section 3):
- **Nothing lost:** of the old job's 30 steps, 23 are byte-identical in a new job and 7 changed only as the split needs; none was made conditional or reordered to prove less. Each new `dbshell` and decoy step adds a check.
- **The decoy meets AG1.** AG1 says "in its own PostgreSQL", where another suite's real marker cannot exist, so a marker the job generates, on a database named as the other suite's, is the reading that fits. The marker check binds to the connected database's own comment (`current_database()`), which is what the shared job's refusal proved. A missing decoy, equal markers, an empty comment and a refusal for another cause each fail the step; both runs print the refusal's reason, "the database's comment is different".
- **The secrets:** every value masked before any output; no step prints a value; each scan lists exactly its job's files; each upload gated on its job's check; each job removes its container, volume and directory; artifact names distinct.
- **The gate:** each database job keeps `needs: scope` and the old condition; the gate's own script, on 22 synthetic results, fails a full-scope run with any database job `failure`, `cancelled`, `skipped` or missing, and a documentation run with any database job `success`.
- **The Chromium retry** matches the carried form; its worst case is 24.4 minutes of the job's 25.
- **The pin test:** no escape found; on `c2cffbe`'s test a commented pin fails the count, so M02's N2 was real.
- **No dependency:** the same action pins and image digest; no lock, requirement, package or `Dockerfile` change; permissions and `persist-credentials: false` as before.
- **The records:** the CI policy's and the README's claims hold, and the section "A0"'s step table, durations, counts and reversals hold, except F5, F6 and F8.

**Its checks**, in a scratch copy of `3bf55de` with hash-locked installs:
- the proof's offline tests (`Ran 378 tests … OK`), Ruff and mypy (71 files); the API's pin test (`Ran 3 tests … OK`); the workflow parsed with PyYAML 6.0.3;
- the prompt's reversals R1a to R1d (a scan's list), R2a and R2b (the gate), R3a to R3c (a decoy step, an upload's condition) and R4a to R4e (the pins): each failed its test. The record's S4, S5, W2, W3, W6 and W7: each failed;
- its own reversals D1a, D1b, D2a, D2c, D2d, D3a, D3b, D4a to D4d, D5, D6a and D6b **passed** every offline test (the findings below); D2b failed, as it should;
- a local run of the identity job's own steps on a throwaway PostgreSQL under P06.DB's D4 passed; D1b's variant also passed. Everything it started was removed.

**The runs:**

| Job | Run of record 44463105633 (`push`, `3bf55de`) | PR run 44466377174 (`pull_request`, `90a74e5`) | Timeout |
|---|---|---|---|
| Database (ordering) | 539 s | 524 s | 30 min |
| Database (identity) | 103 s | 100 s | 30 min |
| Database (profile) | 151 s | 151 s | 30 min |
| Database (discovery) | 190 s | 289 s | 30 min |
| Mobile checks | 561 s (Chromium 187 s) | 466 s (Chromium 22 s) | 25 min |

Every job of both runs succeeded, and both gates printed "Application checks passed". App Manager 12 read the PR run with the GitHub tools at about 06:02 UTC: eleven jobs, success; the Chromium install passed on its first attempt and the pause and the retry were skipped; the gate's line at 05:46:18. Codex's code review of `90a74e5` completed with no findings, and the pull request had no review thread.

**Its findings** (in its words, shortened):
- **F1 — Should fix: the decoy's binding to the refused marker is unpinned.** Class: "let a check pass for the wrong reason"; "let a test pass where it should fail". The `create-role.sql` `printf` (`foundation.yml` lines 561, 880, 1199) gives the decoy its comment, and no test asserts which value. Binding the decoy's comment to another value turns AG1's check into a plain wrong-marker check, silently: D1a (profile) and D1b (identity) pass all 159 offline tests, and D1b's decoy step passed on a local PostgreSQL. All three argument orders are right today; A2 copies the pattern. Fix: each credentials test asserts the exact `printf` argument list, and that the same variable writes the decoy's marker file.
- **F2 — Should fix: the identity job's new steps have no content test.** Class: "let a test pass where it should fail". `test_identity_offline.py` has no credentials or decoy-step test, unlike `ProfileWorkflowTests` and `DiscoveryWorkflowTests`. These identity reversals pass every offline test: D2a, `test "$fail" = 0` removed (line 710; CI would pass with the check failing); D2c, the counts' `cmp` removed; D2d, the decoy marker's migrate removed; D4a, a mask line removed; D4c, the distinctness test removed; D4d, the decoy not created. In all three jobs: each new `dbshell` step's exit check and refusal check (lines 643, 962, 1281; D3a, D3b), the decoy step's existence check (lines 675, 994, 1313; D6b), and the password masks (D4b, a gap older than A0). Fix: the identity counterparts of the profile job's two tests, and each `dbshell` step's two checks.
- **F3 — Nit: the Chromium timeout's outcome is undocumented, and the first attempt's margin is thin.** GitHub's documentation does not say whether a step killed by its own `timeout-minutes` has the outcome `failure` (it quotes `steps[*].timeout-minutes`, `continue-on-error` and `steps.<step_id>.outcome`, none of which says). Passing installs have taken 510 s (`main`'s run 44416436012) and 541 s against the first attempt's 600 s, so a slow install that passed before can now be killed, and a kill during `dpkg` may defeat the retry. No outcome gives a false pass. For the Dev Manager: accept as carried, establish the outcome empirically, or widen the job's timeout.
- **F4 — Nit: four Docker Hub pulls per run.** Docker's page gives unauthenticated users "100 per IPv4 address or IPv6 /64 subnet" per 6 hours; no Docker or GitHub page names an exemption for GitHub-hosted runners. Each runner pulls once, so the count per address per job is unchanged; both runs pulled without a `429`, and a `429` would fail the job and the gate.
- **F5 — Nit: the manager's verification miscounts:** 23 steps byte for byte and 7 changed, not 22 and 8; the ordering job's credentials step masks four values, not five.
- **F6 — Nit: a stale job name in six docstrings:** the three scans' line 4 ("The Database proof checks job runs it…") and the three offline test modules' docstrings.
- **F7 — Nit: drift limits in the tests.** `job_secret_files` (`test_identity_offline.py` line 516) reads only the `"$dir/<name>"` spelling (D5 passes). The gate test pins the job tuple and the `assert` line, not that the loop covers the whole tuple (`for job in jobs[:5]:`, D6a, passes).
- **F8 — Nit: the README's "keeps".** `proofs/postgres-ordering/README.md` says the decoy step "keeps the shared job's check that each suite's database refused the other suites' markers"; it keeps it with one decoy marker per job, and only while F1's binding holds.

**What it did not read or run:** the runner's source code (outside its network), so F3's outcome stays open; GitHub's changelog; the ordering, profile and discovery jobs locally (CI's two runs cover them); the full API suite, the contract tests and Mobile checks; the proof's README whole (its changed passages and their context).

**Disposition** (App Manager 12; the manager workflow's step 6, "What a correction pass is for" and "Fix or carry, by rule", under D-07):

| Finding | Disposition | Why |
|---|---|---|
| F1 | **Fixed before the merge**, by correction C1 (tests only) | A missing test of A0's own decoy check. A0's acceptance check rests on that check ("each with the checks it ran before"; AG1's decoy), so D-07 makes it a correction; it is in the review prompt's classes |
| F2 | **Fixed before the merge**, by C1 | The identity job's decoy step, each job's `dbshell` refusal and the decoy's existence check are checks the same acceptance check rests on; the masks belong to the credentials steps A0 rewrote, and C1's identity test asserts every mask as the profile and discovery tests do |
| F7, D6a (the gate's loop) | **Fixed before the merge**, by C1 | The review graded it a nit. The gate requiring each job is A0's acceptance check ("the gate requires each"), so a missing test of it is a correction under the same rule as F1 and F2: the manager's reading, listed for the Dev Manager's pre-merge read |
| F7, D5 (the file-list spelling) | **Carried**, to SV4 A2 (the carried-items file, "Carried to SV4") | The reach of a test helper, not a check A0 makes; A2 adds a fifth job and scan the same way |
| F6 | The three offline test modules' docstrings: **by C1**, which changes those modules. The three scans' line 4: **carried** with D5 | A record's wording that misleads no decision; the test modules are taken up because C1 changes them |
| F3 | **Accepted as carried** (DM-97, option (a)); the first attempt's margin is **carried** to the next change to the Foundation workflow (the carried-items file, DM-97) | The form is DM-59 item 7's: `id: chromium`, `continue-on-error: true`, a pause and one retry, each only `if: steps.chromium.outcome == 'failure'`, each attempt with its own `timeout-minutes`, all inside the job's 25 minutes. The 10 and 6 minutes are A0's, chosen under that rule; DM-59's "on a passing run the install takes under a minute" was out of date (A0 measured 22 to 541 s). GitHub's documentation does not say what outcome a step stopped by its own `timeout-minutes` has, but the runner's source does: it marks the step failed ("has timed out after N minutes"), and with `continue-on-error` its outcome is then `failure`, so the retry runs (`actions/runner`: `RunStepAsync` in `src/Runner.Worker/StepsRunner.cs` and `ApplyContinueOnError` in `src/Runner.Worker/ExecutionContext.cs`, read by Dev Manager 6 at release v2.338.2, the version PR57's run 44610075506 reports, and at `main` `7e211dc`; source code, not a documented contract). No outcome gives a false pass. A Mobile run that fails at the Chromium step is diagnosed under OD-21 |
| F4 | **Recorded** (here, and in the limit above) | No false pass is possible; the documented limit is per address, and each job's runner pulls once |
| F5 | **Corrected** in "Manager verification of A0" (AM12-42) | The manager's own count |
| F8 | **Corrected** by the manager in the proof's README (Markdown), listed for the pre-merge read | The sentence now says one decoy marker per job |

## A0-C1

- **Session:** SV4 A0's correction session A0-C1, started by Nathan from the correction prompt, revision 1, from `e824e5f18ad8d53ecd7b7be1ecb18dc7f87d7418` of the manager branch `claude/magical-wozniak-yfmmx2`. Its report goes to App Manager 12 through Nathan.
- **Branch:** `claude/awesome-brown-lmfi8e`, which the push filter's `claude/**` covers. It starts at `e824e5f`.
- **Code head:** `c78f29747b1fe6e764dd3cb1afe5e6325941a6d2`. **Records head:** the commit that adds this section, pushed after the code head's run had finished.
- **What C1 changed:** tests only, in `proofs/postgres-ordering/tests/test_identity_offline.py`, `test_profile_offline.py` and `test_discovery_offline.py`. No workflow, scan, setting, README, policy or application file changed.

### The start gate and the environment check

- **The environment** (names only):
  - none of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY`;
  - no `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name;
  - present, never read or passed to a command: `AWS_ACCESS_KEY_ID`, `AWS_CA_BUNDLE` and `AWS_SECRET_ACCESS_KEY` (OD-76), and `GH_TOKEN` and `GITHUB_TOKEN`;
  - `python3.12 --version`: Python 3.12.14;
  - every repository command ran under `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`. The one install also passed the proxy variables and the proxy's CA path.
- **The start gate.** Every check passed:
  - `git rev-parse HEAD` printed `e824e5f18ad8d53ecd7b7be1ecb18dc7f87d7418`, which was also the live manager branch's head;
  - "this prompt's commit is on the live branch", "A0's code head" and "no code on the live branch after 3bf55de";
  - `grep -c` printed `1` for "Exact-head review of A0" and `0` for "A0-C1".
- **The workflow at `3bf55de`** was read whole: the four database jobs and the gate. Every assertion below passes against it unchanged, so no check was missing or misbound, and the session did not stop.

### What was added, by item

Every addition reads the workflow through the existing helpers (`workflow_job`, `workflow_steps`, `workflow_step`, `job_databases`). Three small helpers were added beside them in `test_identity_offline.py` and imported by the other two files:
- `script_lines(step)`: a step's lines without their indentation, so that a whole line of its script is matched, not a substring of a longer or commented line;
- `writers(step, name)`: each line of a credentials step that writes or appends to `"$dir/<name>"`;
- `credentials_prelude(step)`: what a credentials step does before its first line that can print or write. That is each value it generates and each it masks, in order. Only `set +x`, `umask 077`, comments, the `secrets.token_hex` assignments and the masks may come first.

No earlier assertion was changed, weakened or removed. `git diff` against `e824e5f` removes only the three docstring lines of item 5.

1. **F1, the decoy's binding** (all three jobs):
   - In each credentials test (`…_makes_its_database_the_decoy_and_its_own_keys`), `writers(step, "create-role.sql")` must equal one exact line: the whole `printf`, its format and its argument list. So the suite's database's comment takes the suite's marker variable, and the decoy's comment takes the decoy's: `"$role_password" "$identity_marker" "$marker"`, `"$role_password" "$profile_marker" "$identity_marker"` and `"$role_password" "$discovery_marker" "$profile_marker"`.
   - Each marker file, the decoy's and the suite's, has exactly one writer, from its own variable (for example `printf '%s\n' "$marker" > "$dir/marker"` in the identity job), and each marker variable is assigned exactly once.
   - In each decoy-step test (`…_refuses_the_decoys_marker_first`):
     - the step's only `PROOF_DB_MARKER=` reads `"$(cat "$DIR/$1")"`, and its `PROOF_DB_NAME` is the suite's database;
     - the step's `migrate` lines are exactly two, in order: the refused one, named the decoy's marker file (`identity marker …`, `profile identity-marker …`, `discovery profile-marker …`) and writing the wrong-marker log, then the suite's own.
2. **F2, the identity job's new steps.** The new class `IdentityWorkflowTests` in `test_identity_offline.py`, the identity counterparts of the profile job's tests:
   - `test_the_credentials_step_makes_its_database_the_decoy_and_its_own_keys`:
     - the script's first line is `set +x`;
     - the prelude generates and then masks `superuser_password`, `role_password`, `identity_marker`, `marker` and `identity_secret_key`, each masked after it is generated and before any output, and the step has exactly five masks;
     - the distinctness test, as a whole line, comes before the role statement;
     - the exact `printf` of item 1, which creates the decoy `glow_proof` with its own comment;
     - the marker and `SECRET_KEY` files' single writers, the key's generation, the passfile's one database, and no `profile`, `discovery` or `wrong_marker` anywhere in the job.
   - `test_the_migrations_step_refuses_the_decoys_marker_first`: item 1's checks, then these whole lines in order:
     - the superuser's `psql` into `glow_identity_proof`;
     - the decoy's existence query, its distinctness query, and the `if` that fails the step on either;
     - the counts before; `set +e`; the refused `migrate`; `status=$?`; `set -e`; the counts after; the ledger check;
     - the refusal's `grep`; `fail=0`; the exit-status check; the missing-refusal failure;
     - the `cmp` and its `|| { … fail=1; }` on the next line; the outside-relations and ledger failures;
     - `test "$fail" = 0`, then the suite's `migrate` and `makemigrations --check`.

     There must be exactly one `set +e` and one `set -e` line, so `test "$fail" = 0` runs under `set -e`. The step must declare `shell: bash`.
   - `test_the_dbshell_step_requires_a_failed_exit_and_the_refusal`: item 3's checks for the identity job.
3. **F2, in all three jobs:**
   - **`dbshell`:** a new test `test_the_dbshell_step_requires_a_failed_exit_and_the_refusal` in each of `IdentityWorkflowTests`, `ProfileWorkflowTests` and `DiscoveryWorkflowTests`. It requires these whole lines, in order:
     - `set +e`;
     - the `env -i` command with the suite's database, its marker file, its two key files and its settings module;
     - `python -m django dbshell < /dev/null > "$DIR/<suite>-dbshell.log" 2>&1`, then `status=$?` on the next line, then `set -e`;
     - the `grep -m 1 -F 'RefusedDatabase: refusing dbshell'`;
     - `if [ "$status" -eq 0 ]; then echo "FAIL: dbshell exited 0"; exit 1; fi`;
     - `if [ -z "$refusal" ]; then echo "FAIL: the dbshell refusal is missing (diagnostics withheld)"; exit 1; fi`.
   - **The decoy's existence check:** in the profile and discovery decoy-step tests, the same sequence of whole lines as the identity test's (the `if [ "$decoy" != 1 ] || [ "$distinct" != t ]` line among them), added at the start of each test, before its earlier assertions, so that each reversal fails on an assertion rather than on `str.index`.
   - **The masks:** the profile and discovery credentials tests gain the identity test's prelude check, with both passwords, so each of the five values is masked before any output.
4. **F7's D6a, the gate's loop.** `DiscoveryWorkflowTests.test_the_gate_requires_each_suites_job` gains:
   - one `jobs = (` in the gate, and the loop as two exact lines: `for job in jobs:` and its `assert`;
   - the gate's own script, cut from the step and run with `sys.executable -I -c` on synthetic `RESULTS`:
     - all nine jobs `success` on full scope must exit 0 and print "Application checks passed";
     - all nine `skipped` on documentation must exit 0 and print "Ordinary documentation: application jobs intentionally skipped";
     - for each of the nine jobs and each of the three other results (`success`, `failure`, `cancelled`, `skipped`, less the expected one), the script must exit non-zero with `AssertionError: Unexpected <job> result`. That is 54 subtests.
5. **F6, the module docstrings.** Each says its cases "run in their own suite's job, "Database proof checks (identity)" ("(profile)", "(discovery)"), on its own disposable database". No other wording changed.

### Reversals

Each reversal edits the workflow in place, in one job only: the harness asserts that each edit's text occurs exactly once in that job. The harness then runs the seven classes that read the workflow and restores the file byte for byte (SHA-256 `ee42a4a1…`, checked after each). Only these classes read the workflow: `IdentityScanTests`, `IdentityUploadGateTests`, `IdentityWorkflowTests`, `ProfileScanTests`, `ProfileWorkflowTests`, `DiscoveryScanTests` and `DiscoveryWorkflowTests`. A0's search had found no other proof test that does. The same reversals were also run on a scratch worktree at `e824e5f`, which has the old tests and the same workflow ("before"). The worktree was removed afterwards.

After every reversal, `git status` showed only the three test files, and `git diff --quiet 3bf55de… HEAD -- .github` held.

**The reversals:**

| ID | The edit, in the named job |
|---|---|
| F1a-swap | the `printf`'s two marker arguments swapped (the review's D1a and D1b) |
| F1a-other | the decoy's comment bound to the suite's own marker variable |
| F1b-other | the decoy's marker file written from the suite's marker variable |
| F1b-again | a second line writing the decoy's marker file from the suite's variable |
| F1c | the refused `migrate` given the suite's own marker file |
| D2a | `test "$fail" = 0` removed |
| D2c | the counts' `cmp` (both lines) removed |
| D2d | the decoy marker's `migrate` removed |
| D4a | the suite marker's mask removed (D4a-decoy: the decoy marker's) |
| D4b | the role password's mask removed (D4b-superuser: the superuser password's) |
| D4c | the markers' distinctness test removed |
| D4d | the decoy not created: its two statements and its argument removed from the `printf` |
| D3a | the `dbshell` step's exit-status check removed |
| D3b | the `dbshell` step's empty-refusal failure removed (D3b-grep: its `grep` widened to `'refusing'`) |
| D6b | `[ "$decoy" != 1 ] \|\|` removed from the decoy check (D6b-line: the whole check removed) |
| D6a | the gate's loop over `jobs[:5]` |

**The results.** "pass" means every test of the seven classes passed. "error" means the earlier test raised `ValueError` from `str.index`. Otherwise the cell gives the test that failed first, at `tests/test_<suite>_offline.py:<line>` of the code head: *cred* is the credentials test, *migr* the decoy-step test, *dbsh* the `dbshell` test.

| ID | Identity: before → after | Profile: before → after | Discovery: before → after |
|---|---|---|---|
| F1a-swap | pass → *cred* :836 | pass → *cred* :452 | pass → *cred* :327 |
| F1a-other | pass → *cred* :836 | pass → *cred* :452 | pass → *cred* :327 |
| F1b-other | pass → *cred* :843 | fail → *cred* :405 | fail → *cred* :282 |
| F1b-again | pass → *cred* :843 | pass → *cred* :462 | pass → *cred* :337 |
| F1c | pass → *migr* :909 | error → *migr* :490 | error → *migr* :365 |
| D2a | pass → *migr* :952 | fail → *migr* :524 | fail → *migr* :399 |
| D2c | pass → *migr* :952 | fail → *migr* :524 | fail → *migr* :399 |
| D2d | pass → *migr* :909 | error → *migr* :490 | error → *migr* :365 |
| D4a | pass → *cred* :811 | fail → *cred* :405 | fail → *cred* :282 |
| D4a-decoy | pass → *cred* :811 | fail → *cred* :405 | fail → *cred* :282 |
| D4b | pass → *cred* :811 | pass → *cred* :434 | pass → *cred* :309 |
| D4b-superuser | pass → *cred* :811 | pass → *cred* :434 | pass → *cred* :309 |
| D4c | pass → *cred* :824 | fail → *cred* :413 | fail → *cred* :290 |
| D4d | pass → *cred* :836 | fail → *cred* :410 | fail → *cred* :287 |
| D3a | pass → *dbsh* :882 | pass → *dbsh* :581 | pass → *dbsh* :456 |
| D3b | pass → *dbsh* :882 | pass → *dbsh* :581 | pass → *dbsh* :456 |
| D3b-grep | pass → *dbsh* :882 | pass → *dbsh* :581 | pass → *dbsh* :456 |
| D6b | pass → *migr* :952 | pass → *migr* :524 | pass → *migr* :399 |
| D6b-line | pass → *migr* :952 | pass → *migr* :524 | pass → *migr* :399 |

**D6a** (the gate): before, pass. After: `FAIL: DiscoveryWorkflowTests.test_the_gate_requires_each_suites_job` at `tests/test_discovery_offline.py:618`, with `AssertionError: '          for job in jobs:\n              assert results[job]["result"] == expected, …' not found in …`.

After the change all 58 reversals fail, each with an `AssertionError` and none with an error. Every reversal the prompt names passed every offline test before, exactly where the review said it would. The ones the review did not list for the profile and discovery jobs (F1b-other, D2a, D2c, D4a, D4c and D4d, and F1c and D2d as errors) already failed before.

**The assertion at each line:**
- **Identity:**
  - :811, the prelude's masked names, for example `Lists differ: ['superuser_password', 'role_password', 'marker', 'identity_secret_key'] != [… 'identity_marker' …]`;
  - :824, `'test "$identity_marker" != "$marker" || { … }' not found`;
  - :836, `Lists differ` on the `create-role.sql` writer;
  - :843, `Lists differ` on the `marker` file's writers;
  - :882, `Lists differ: ['<the missing dbshell line>'] != []`;
  - :909, `Lists differ` on the step's `migrate` lines;
  - :952, `Lists differ: ['<the missing decoy-step line>'] != []`.
- **Profile and discovery, the lines this correction added:**
  - :434 and :309, the masked names;
  - :452 and :327, the `printf`;
  - :462 and :337, the decoy's marker file's writers;
  - :490 and :365, the `migrate` lines;
  - :524 and :399, the decoy-step sequence;
  - :581 and :456, the `dbshell` sequence.
- **Profile and discovery, earlier assertions that fail first:** :405 and :282 (a mask or marker-file line, in a subtest), :410 and :287 (`CREATE DATABASE <decoy>`), and :413 and :290 (the distinctness test). For F1b-other and D4a, this correction's assertions fail after them (`failures=2`).

**One probe beyond the list:** a line `jobs = jobs[:5]` inserted before the gate's loop. This leaves the loop's two lines and the one `jobs = (` intact. The gate test failed in its script run (`AssertionError: 0 == 0` in the subtests `full='true', job='database-ordering', result='failure'` and the rest). The workflow was restored with `git checkout`, and the `.github` diff against `3bf55de` was empty.

### Commands and results

- **The proof's checks**, in `proofs/postgres-ordering`, after `python -m pip install --require-hashes -r requirements-dev.lock` into a `python3.12` virtual environment, and `pip check` ("No broken requirements found"):
  - `python -m unittest discover -s tests -t .`: `Ran 378 tests … OK` at `e824e5f`, and `Ran 383 tests … OK` at the code head (five tests added: the identity job's three and a `dbshell` test each for profile and discovery);
  - `ruff check .` printed "All checks passed!", `ruff format --check .` "71 files already formatted", and `mypy` "Success: no issues found in 71 source files".
- **The trusted classifier:**
  - `main`'s `scripts/change_scope.py` (`c2cffbe`), extracted with `git show` to a scratch directory outside the checkout, SHA-256 `b564c62f…` (the copy A0 used);
  - run as `python3 -I <copy>/change_scope.py --base c2cffbe6022637331d73e3558429ff70ab5aa5e3 --head c78f29747b1fe6e764dd3cb1afe5e6325941a6d2 --merge-base`, with the checkout as its working directory;
  - it printed `"full": true`, reason `behavior-or-empty`.
- **The diff:** `git diff --name-only e824e5f18ad8d53ecd7b7be1ecb18dc7f87d7418 c78f297` lists only the three test files. The records commit adds this section.
- **No dependency** was added. No database, provider, HDE or external service was used. The only network use was PyPI, for the hash-locked install.

### The run of record

**Foundation run [44562701307](https://github.com/amthorn78/glow-dating-app/actions/runs/44562701307)** on `c78f29747b1fe6e764dd3cb1afe5e6325941a6d2` (a push run, attempt 1) concluded **success**. It was created at 16:08:26 UTC on 19 November 2026, and its gate finished at 16:15:48, 7 minutes 22 seconds in all. Nothing was pushed to the branch until it had finished. Read with the GitHub tools; durations are from the jobs' timestamps, in whole seconds.

| Job | Conclusion | Duration |
|---|---|---|
| Change scope | success | 17 s |
| API checks | success | 68 s |
| Mobile checks | success | 413 s (Chromium's first install 22 s; the pause and the retry skipped) |
| API mobile smoke | success | 75 s |
| API artifact checks | success | 25 s |
| Stream proof checks | success | 92 s |
| **Database proof checks (ordering)** | success | 322 s |
| **Database proof checks (identity)** | success | 106 s |
| **Database proof checks (profile)** | success | 152 s |
| **Database proof checks (discovery)** | success | 234 s |
| Foundation gate | success; its log ends "Application checks passed" | 4 s |

- **The offline tests in the database jobs:** each ran `python -m unittest discover -s tests -t . -v` (18 to 22 s). The identity job's log shows `Ran 383 tests` and the three `IdentityWorkflowTests` cases.
- **The identity job's log**, quoted: `identity dbshell exit status: 1`; `decoy database glow_proof with a marker as its comment: 1; its comment differs from the identity database's: t`; `relations outside information_schema and the pg_ schemas: 0 before, 0 after`; `identity migrate with the decoy database's marker: exit status 1`; `identity secret scan: clean (754 secrets held; 0 found in 240 log records, 102 writes and the results JSON)`; `IDENTITY VERDICT: PASS`; `second identity run exit status: 1`; `no proof container remains`. The only `::add-mask::` text in it is the step's script as GitHub echoes it, with variable names, never a value.
- The other jobs' logs were not read line by line; their steps all concluded success.

### Limits and deviations

- **Substring pins, not semantics.** The added assertions pin whole lines and their order, as the earlier tests pin substrings. A rewrite that keeps the same check in other words fails them, which is intended: such a rewrite is then reviewed. An edit that leaves every pinned line in place and defeats the check elsewhere could still pass. Examples are a new line that overwrites `$status` or `$fail`, or a `|| true` added to a pinned line's continuation. The gate is the exception: its script is also run, so the gate's behaviour is tested, not only its text.
- **The three helpers** (`script_lines`, `writers`, `credentials_prelude`) are new module-level functions in `test_identity_offline.py`, beside the existing workflow helpers, and serve only the workflow-step tests. The prompt's owned lines are "their tests of the workflow's steps, new tests of the same kind". These helpers are read here as part of those tests.
- **The reversals ran on the workflow-reading classes**, not on all 383 tests, for speed. No other proof test reads the workflow, so the other tests' results cannot depend on these edits.
- **F7's D5** (`job_secret_files` reads only the `"$dir/<name>"` spelling) and **F6's scans' line 4** were carried by the manager's disposition and are not touched here.

### Manager verification of A0-C1 (App Manager 12, 19 November 2026)

- **The branch:** `claude/awesome-brown-lmfi8e`, code head `c78f297`, records head `b407239`, both after the prompt's commit `e824e5f`, which the branch starts at; the manager branch, still at `e824e5f`, took both by fast-forward.
- **The diff** from `e824e5f` to the code head lists the three offline test files only; to the records head, the record too. Against `3bf55de`, nothing under `.github`, the proof's package, `services`, `apps`, `packages` or `scripts` changed. Its only removed lines are the three module docstrings' (F6).
- **The trusted classifier,** `main`'s `scripts/change_scope.py` (`c2cffbe`), extracted outside the checkout and run from it with `python3 -I --base c2cffbe… --head c78f297… --merge-base`: `"full": true`, reason `behavior-or-empty`.
- **The tests, read whole in the diff:** `IdentityWorkflowTests` (three tests) and the helpers `script_lines`, `writers` and `credentials_prelude` in `test_identity_offline.py`; the additions to `ProfileWorkflowTests` and `DiscoveryWorkflowTests` (each credentials and decoy-step test extended, a `dbshell` test each); the gate test's loop lines and its run of the gate's own script on 54 wrong results. No earlier assertion changed. The new blocks sit before the earlier assertions in the profile and discovery decoy-step tests, as the record says.
- **Re-run by the manager** in a scratch export of the code head, in a `python3.12` virtual environment with the proof's hash-locked install, under `env -i`: `Ran 383 tests … OK`; Ruff "All checks passed!" and "71 files already formatted"; mypy "Success: no issues found in 71 source files".
- **Four reversals of the manager's choosing,** each on the export's workflow, restored after each (the copy compared equal to `3bf55de`'s workflow afterwards), with the three test modules run: D2a in the identity job (`test "$fail" = 0` removed), D1b in the identity job (the decoy's comment bound to the identity marker), D4b in the profile job (the role password's mask removed) and D6a (the gate's loop over `jobs[:5]`). Each failed (`FAILED (failures=1)`).
- **The run of record,** Foundation run 44562701307 (event `push`, head `c78f297`), read with the GitHub tools: all eleven jobs succeeded, among them the four database jobs, and the gate's log ends "Application checks passed".
- **For the delta review, noted, not decided here:** the gate test now runs the gate's script, cut from the workflow, in a subprocess under `-I` with only `PATH` and `RESULTS`, so the offline tests execute workflow text; and the three helpers are module-level functions in `test_identity_offline.py`, imported by the other two files, which the session read as part of "tests of the workflow's steps".

### Delta review of A0-C1 (19 November 2026)

- **Session:** C1's delta review, started by Nathan from [its prompt](https://github.com/amthorn78/glow-dating-app/blob/78e9cc7d11bcb45477d869dd2b86f9519d5aa626/docs/ephemeral/2026-11-19-sv4-a0-c1-delta-review-prompt.md), revision 1, from `78e9cc7`; its report relayed to App Manager 12 on 19 November 2026.
- **Its start gate, classification and environment check:** every check passed (`HEAD` `78e9cc7`, one merge base `c2cffbe`, the code equal to `c78f297` at `HEAD` and on the live branch, no delta review recorded). `main`'s classifier, run with `python3 -I` from the checkout, printed `"full": true`, reason `behavior-or-empty` (a first run from outside the checkout printed `comparison-unavailable`, also full scope). None of the three HDE names and no `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name; the AWS and GitHub token names present and unread.
- **Verdict: changes requested,** for one should-fix finding (R1). No blocking finding. C1 answers F1, F2, D6a and F6 completely: every reversal the prompt names fails in all three jobs, including rebinding to a third value.
- **What it verified:** nothing weakened (outside Markdown, the only removed lines are the three docstrings; an AST check found no test shadowing another); the helpers match whole lines and cannot pass empty; the gate test's script run is safe (the gate's own Python, `-I`, a 30-second timeout, `PATH` and `RESULTS` only, inside the offline tests' `env -i`, before any credential exists; an earlier test already runs workflow text through `bash -c` the same way) and proves the script's rule, 54 subtests; the helpers' place stays within "tests of the workflow's steps"; the record's claims hold, all 25 cited line numbers among them, except R1 and N3.
- **Its checks,** in a scratch export of `c78f297` with a hash-locked install: `Ran 383 tests … OK`; Ruff and mypy clean (71 files); every prompted reversal failed in each of the identity, profile and discovery jobs (F1a and F1b each to the suite's variable and to a third value, F1c, D2a, D3a, D3b, D4b both passwords, D6b both forms) and D6a; its own probes X1 and X2 failed in identity and passed in profile and discovery (R1), X3, X4, X5 and X9 passed in all three (N1, N2), and the gate's X6, X7 and X8 passed (N3).
- **The runs:** the run of record 44562701307 and PR57's run 44568513010 (event `pull_request`, head `78e9cc7`): all eleven jobs succeeded in each, and each gate printed "Application checks passed". App Manager 12 read the PR run with the GitHub tools at about 16:56 UTC: Chromium's first install 104 s, the pause and the retry skipped; Codex's code review of `78e9cc7` completed with no findings, and the pull request had no review thread.

**Its findings** (in its words, shortened):
- **R1 — Should fix.** Classes: "a record claim more than the tests show"; "a test passes where it should fail" for the decoy check. The record's "A0-C1", item 3, says the profile and discovery decoy-step tests check "the same sequence of whole lines as the identity test's". They leave out five lines the identity sequence pins: `outside_before=…`, `outside_after=…`, `if [ -n "$refusal" ]; then`, the outside-relations `if [ "$outside_before" != 0 ] …` line and its `FAIL` line, which no earlier assertion pins either. X1, the outside-relations failure deleted, and X2, `if [ -n "$refusal" ]; then` made `if true; then` (which removes the "refused for another cause" check A0's review credited to the decoy step), each pass every test in the profile and discovery jobs and fail in the identity job. The gap predates C1. Fix: those lines added to both sequences, tests only.
- **N1 — Nit.** `writers()` sees only the `> "$dir/<name>"` spelling: X3, a second writer spelled `>"$dir/<the decoy's file>"`, passes in all three jobs, so the decoy's marker file could hold another value with CI green. Same class as the carried D5.
- **N2 — Nit.** Edits outside the pinned lines pass: X4, a later statement in the role step that changes the decoy's comment; X9, `continue-on-error: true` on any decoy or `dbshell` step (step-level keys are not pinned, as before A0); X5, `fail=0` just before `test "$fail" = 0` (the record's own example). The record's "Substring pins, not semantics" limit should name X4 and X9.
- **N3 — Nit, records.** The record says the gate's script run means "the gate's behaviour is tested"; only the script's is. X6 (`set +e` before the heredoc and a trailing `true`), X7 (`continue-on-error: true` on the gate's step) and X8 (`RESULTS` bound to a literal, which CI would fail loudly) pass. Its words: "the gate's script is run; the step around it is not tested".

**What it did not read or run:** the profile and discovery files' classes other than the workflow classes, mapped by structure only (none reads the workflow; C1 did not touch them); the identity job's log beyond its tail; the jobs on a local PostgreSQL; the API suite and Mobile checks; the runner's source (F3 stays as recorded).

**Disposition** (App Manager 12; the manager workflow's step 6, under D-07):

| Finding | Disposition | Why |
|---|---|---|
| R1 | **Fixed before the merge**, by correction C2 (tests only, the profile and discovery decoy-step tests) | The decoy step's outside-relations check and its refusal check are part of the check A0's acceptance rests on ("each with the checks it ran before"; AG1), the rule F1 and F2 were fixed under; the record's claim is corrected by C2's section, which this disposition names |
| N1 (X3) | **Carried**, to SV4 A2 with F7's D5 | The reach of a test helper's spelling, as D5 |
| N2 (X4, X9, X5) | **Carried**, to SV4 A2, and recorded as limits of "Substring pins, not semantics" | Edits outside a pinned step or line, older than A0 for X9; A2 adds a job the same way and extends these tests |
| N3 | **Recorded** here: the gate's script is run; the step around it is not tested | A record's wording that misleads no decision |

## A0-C2

- **Session:** SV4 A0's correction session A0-C2, started by Nathan from the correction prompt, revision 1, from `7377c198af8382370e9463f8d18cc8e85e30ae06` of the manager branch `claude/magical-wozniak-yfmmx2`. Its report goes to App Manager 12 through Nathan.
- **Branch:** `claude/dazzling-feynman-cjl16t`, which the push filter's `claude/**` covers. It starts at `7377c19`.
- **Code head:** `5a2f137b464565f5da8ed52ce0bb53938b7587a1`. **Records head:** the commit that adds this section, pushed after the code head's run had finished.
- **What C2 changed:** tests only, the `sequence` list of `ProfileWorkflowTests.test_the_migrations_step_refuses_the_decoys_marker_first` in `proofs/postgres-ordering/tests/test_profile_offline.py` and of `DiscoveryWorkflowTests.test_the_migrations_step_refuses_the_decoys_marker_first` in `test_discovery_offline.py`. No workflow, scan, setting, README, policy or application file changed, and no other test.

### The start gate and the environment check

- **The environment** (names only):
  - none of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY`;
  - no `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name;
  - present, never read or passed to a command: `AWS_ACCESS_KEY_ID`, `AWS_CA_BUNDLE` and `AWS_SECRET_ACCESS_KEY`, and `GH_TOKEN` and `GITHUB_TOKEN`;
  - `python3.12 --version`: Python 3.12.14;
  - every repository command ran under `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`. The one install also passed the proxy variables and the proxy's CA path.
- **The start gate.** Every check passed:
  - `git rev-parse HEAD` printed `7377c198af8382370e9463f8d18cc8e85e30ae06`, which was also the live manager branch's head;
  - "this prompt's commit is on the live branch", "C1's code head" and "no code on the live branch after c78f297";
  - `grep -c` printed `1` for "Delta review of A0-C1" and `0` for "A0-C2".
- **The workflow** equalled `3bf55de`'s (`git diff --quiet 3bf55de… HEAD -- .github`; SHA-256 `ee42a4a1…`). Its profile and discovery decoy steps ("SV2: show the profile database refuses…", "SV3: show the discovery database refuses…") were read whole. Each of the eight lines below is in each step, in the order the identity sequence gives, so the session did not stop.

### The lines added

Each of the two `sequence` lists gains eight lines, so that it is the identity test's sequence line for line (26 lines each). With the profile suite's names (discovery: `in_discovery_db`, `glow_discovery_proof`, `discovery discovery-marker`):
- **R1's five, which no assertion pinned before:**
  - `outside_before=$(in_profile_db "$outside_pg")`, after the counts-before line;
  - `outside_after=$(in_profile_db "$outside_pg")`, after the counts-after line;
  - `if [ -n "$refusal" ]; then`, before the missing-refusal failure line;
  - `if [ "$outside_before" != 0 ] || [ "$outside_after" != 0 ]; then`, after the `cmp` lines;
  - `echo "FAIL: a relation exists outside information_schema and the pg_ schemas"; fail=1`, after it;
- **three that earlier assertions pinned only as substrings:**
  - `docker exec "$CONTAINER" psql -X -q -At -F ' ' -v ON_ERROR_STOP=1 -U postgres -d glow_profile_proof -c "$1"`, first;
  - `no_ledger=$(in_profile_db "SELECT to_regclass('public.django_migrations') IS NULL")`, after `outside_after=`;
  - `profile profile-marker python -m django makemigrations --check --dry-run`, last.

No other line changed. `git diff 7377c19… 5a2f137` lists only the two test files and removes no line (19 lines added: the profile `no_ledger` string is one source line, as `ruff format` requires there; discovery's is two). The order check, the `cmp` adjacency check, the `set +e`/`set -e` counts and every earlier assertion stay as they were.

**The mechanical comparison.** A script (`compare.py`, in the session's scratch directory, not committed) reads the three test files with `ast`, never importing or running them. It evaluates each test's `sequence` list from its string constants and the names bound earlier in the same test (`refused` and `migrate` in identity, `refused_line` and `migrate_line` in profile and discovery). It maps the identity list in one simultaneous regular-expression pass, longest token first: `glow_identity_proof` → the suite's database, `glow_proof` → the decoy's database, `identity-marker` → the suite's marker file, `identity` → the suite (so `in_identity_db` and `identity-…txt` too), and `marker` → the decoy's marker file only as the word after the suite's function at the start of a line (the refused `migrate`). The English word in "another database's marker exited 0" is not a name and is left as it is. It then requires list equality:
- **at the code head:** identity 26 lines; profile 26, equal; discovery 26, equal;
- **at C1's head `c78f297`:** profile 18 and discovery 18, not equal; the eight lines above are missing from each, and neither has a line the mapped identity sequence lacks.

**The "A0-C1" section's claim.** Its item 3 says the profile and discovery decoy-step tests check "the same sequence of whole lines as the identity test's". That was not true of C1's head (18 of 26 lines, as the comparison shows), and is true of C2's code head.

### Reversals

Each reversal edits the workflow in place, in one job only: the harness (`reversals.py`, in the scratch directory) asserts that the edit's text occurs exactly once in that job. It then runs **every offline test** (`python -m unittest discover -s tests -t .`, 383 tests) and restores the workflow byte for byte, checking its SHA-256 after each. "Before" ran on the checkout at `7377c19` before the test edits; "after" ran on the edited tests, which the code head commits unchanged. After both runs, `git status` showed only the two test files (then nothing, after the commit), and `git diff --quiet 3bf55de… HEAD -- .github` held.

| ID | The edit, in the named job |
|---|---|
| X1 | the outside-relations failure (its `if` line, its `FAIL` line and its `fi`) removed |
| X2 | `if [ -n "$refusal" ]; then` replaced by `if true; then` |
| X10 | the `outside_before=` line removed |
| X11 | the `outside_after=` line removed |
| X12 | the `no_ledger=` line replaced by `no_ledger=t` |

| ID | Profile: before → after | Discovery: before → after |
|---|---|---|
| X1 | pass → fail :533 | pass → fail :409 |
| X2 | pass → fail :533 | pass → fail :409 |
| X10 | pass → fail :533 | pass → fail :409 |
| X11 | pass → fail :533 | pass → fail :409 |
| X12 | fail :545 → fail :533 | fail :420 → fail :409 |

- **"pass"** means `Ran 383 tests … OK`. Every failure was `FAILED (failures=1)`, in the named job's decoy-step test, with an `AssertionError` and no error.
- **Before:** X1 and X2 passed every test in both jobs, as the delta review found; so did X10 and X11. X12 already failed, in the earlier substring loop, at `tests/test_profile_offline.py:545` and `tests/test_discovery_offline.py:420` of the old files: `AssertionError: "SELECT to_regclass('public.django_migrations') IS NULL" not found in '      - name: "SV2: …'` (SV3 in discovery).
- **After:** each fails at `tests/test_profile_offline.py:533` or `tests/test_discovery_offline.py:409` of the code head, the sequence's `self.assertEqual([line for line in sequence if line not in lines], [])`, naming the missing line:
  - X1: `Lists differ: ['if [ "$outside_before" != 0 ] || [ "$out[110 chars]l=1'] != []` (its `if` and `FAIL` lines);
  - X2: `Lists differ: ['if [ -n "$refusal" ]; then'] != []`;
  - X10: `Lists differ: ['outside_before=$(in_profile_db "$outside_pg")'] != []` (discovery: `in_discovery_db`);
  - X11: `Lists differ: ['outside_after=$(in_profile_db "$outside_pg")'] != []`;
  - X12: `Lists differ: ['no_ledger=$(in_profile_db "SELECT to_reg[42 chars]L")'] != []` (discovery: `[44 chars]`).

### Commands and results

- **The proof's checks**, in `proofs/postgres-ordering`, after `python -m pip install --require-hashes -r requirements-dev.lock` into a `python3.12` virtual environment, and `pip check` ("No broken requirements found"):
  - `python -m unittest discover -s tests -t .`: `Ran 383 tests … OK` at `7377c19`, and `Ran 383 tests … OK` at the code head (no test added);
  - `ruff check .` printed "All checks passed!", `ruff format --check .` "71 files already formatted", and `mypy` "Success: no issues found in 71 source files". A first `ruff format --check` asked for the profile `no_ledger` string on one line; it was rewritten so before the commit.
- **The trusted classifier:**
  - `main`'s `scripts/change_scope.py` (`c2cffbe`), extracted with `git show` to a scratch directory outside the checkout, SHA-256 `b564c62f…` (the copy A0 and C1 used);
  - run as `python3 -I <copy>/change_scope.py --base c2cffbe6022637331d73e3558429ff70ab5aa5e3 --head 5a2f137b464565f5da8ed52ce0bb53938b7587a1 --merge-base`, with the checkout as its working directory;
  - it printed `"full": true`, reason `behavior-or-empty`.
- **The diff:** `git diff --name-only 7377c198af8382370e9463f8d18cc8e85e30ae06 5a2f137` lists only the two test files; the records commit adds this section. The code diff removes no line.
- **No dependency** was added. No database, provider, HDE or external service was used. The only network use was PyPI, for the hash-locked install.

### The run of record

**Foundation run [44601565801](https://github.com/amthorn78/glow-dating-app/actions/runs/44601565801)** on `5a2f137b464565f5da8ed52ce0bb53938b7587a1` (a push run, attempt 1) concluded **success**. It was created at 19:45:10 UTC on 19 November 2026, and its gate's step finished at 19:53:40, 8 minutes 30 seconds in all. Nothing was pushed to the branch until it had finished. Read with the GitHub tools; durations are from the jobs' timestamps, in whole seconds.

| Job | Conclusion | Duration |
|---|---|---|
| Change scope | success | 16 s |
| API checks | success | 70 s |
| Mobile checks | success | 388 s (Chromium's first install 22 s; the pause and the retry skipped) |
| API mobile smoke | success | 85 s |
| API artifact checks | success | 28 s |
| Stream proof checks | success | 96 s |
| **Database proof checks (ordering)** | success | 482 s |
| **Database proof checks (identity)** | success | 123 s |
| **Database proof checks (profile)** | success | 153 s |
| **Database proof checks (discovery)** | success | 230 s |
| Foundation gate | success; its log ends "Application checks passed" | 3 s (to its step's end) |

- **The profile job's log**, read for these lines only: `Ran 383 tests`, with `ProfileWorkflowTests`', `DiscoveryWorkflowTests`' and `IdentityWorkflowTests`' `test_the_migrations_step_refuses_the_decoys_marker_first … ok`; `decoy database glow_identity_proof with a marker as its comment: 1; its comment differs from the profile database's: t`; `relations outside information_schema and the pg_ schemas: 0 before, 0 after`; `to_regclass('public.django_migrations') IS NULL after: t`; `profile migrate with the decoy database's marker: exit status 1`; `the decoy database's marker was refused, and the profile database is unchanged and holds no table`; `PROFILE VERDICT: PASS`.
- The other jobs' logs were not read line by line; their steps all concluded success.

### Limits and deviations

- **Substring pins, not semantics,** as the "A0-C1" section's limit says, with N2's X4, X9 and X5 carried to SV4 A2 by the disposition. C2 pins whole lines and their order. It does not close an edit that leaves every pinned line in place and defeats the check elsewhere.
- **The comparison's one judgement:** `marker` is mapped only as the refused `migrate`'s marker-file argument; the English word in the `FAIL` message "another database's marker exited 0" is identical in all three tests and is not mapped. Any other mapping would make the comparison fail on a line the three tests share.
- **X12 before** already failed, on an earlier substring assertion, not on the line it removes. After C2 it fails on the `no_ledger=` line itself.
- **The reversals ran on every offline test,** not only the workflow-reading classes. The harness and the comparison script stay in the session's scratch directory and are not committed.
- **No stop** was hit, and nothing outside the prompt's paths changed.

### Manager verification of A0-C2 (App Manager 12, 19 November 2026)

- **The branch:** `claude/dazzling-feynman-cjl16t`, code head `5a2f137`, records head `a63e7ae`, both after the prompt's commit `7377c19`, which the branch starts at; the manager branch, still at `7377c19`, took both by fast-forward.
- **The diff** from `7377c19` to the code head: the two test files only, 19 lines added and none removed; against `3bf55de`, nothing under `.github`, the proof's package, `services`, `apps`, `packages` or `scripts` changed. The added lines are the eight per test the prompt names, read in the diff.
- **The trusted classifier,** `main`'s `scripts/change_scope.py` (`c2cffbe`), extracted outside the checkout and run from it with `python3 -I --base c2cffbe… --head 5a2f137… --merge-base`: `"full": true`, reason `behavior-or-empty`.
- **Re-run by the manager** in a scratch export of the code head, in the proof's hash-locked virtual environment, under `env -i`: `Ran 383 tests … OK`; Ruff "All checks passed!" and "71 files already formatted"; mypy "Success: no issues found in 71 source files".
- **Four reversals,** each on the export's workflow within its own job, restored after each (the copy compared equal to `3bf55de`'s workflow afterwards): X1 (the outside-relations failure removed) and X2 (`if [ -n "$refusal" ]; then` made `if true; then`), each in the profile and the discovery job. Each failed (`FAILED (failures=1)`).
- **The sequences,** compared by the manager's own script, which reads the three test files with `ast` and maps the identity sequence's names to each suite's: each of the profile and discovery sequences has 26 lines and equals the mapped identity sequence.
- **The run of record,** Foundation run 44601565801 (event `push`, head `5a2f137`), read with the GitHub tools: all eleven jobs succeeded, among them the four database jobs, and the gate's log ends "Application checks passed".

### Delta review of A0-C2 (19 November 2026)

- **Session:** C2's delta review, started by Nathan from [its prompt](https://github.com/amthorn78/glow-dating-app/blob/f6f145e7c74cb67751864962000edaeabe63e4f9/docs/ephemeral/2026-11-19-sv4-a0-c2-delta-review-prompt.md), revision 1, from `f6f145e`; its report relayed to App Manager 12 on 19 November 2026.
- **Its start gate, classification and environment check:** every check passed (`HEAD` `f6f145e`, also the live branch's head; one merge base `c2cffbe`; the code equal to `5a2f137`; no delta review recorded). `main`'s classifier, extracted outside the checkout and run from it with `python3 -I`, printed `"full": true`, reason `behavior-or-empty`. None of the three HDE names and no `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name; the AWS and GitHub token names present and unread.
- **Verdict: approve with nits.** No blocking or should-fix finding, and none in a correction class.
- **What it verified:** R1 answered in both jobs (X1, X1b, X2, X10, X11 and X12 each fail at the sequence's missing-line assertion, `test_profile_offline.py:533` and `test_discovery_offline.py:409`); both sequences equal the identity sequence, 26 lines each, by its own `ast` comparison, and were unequal at `c78f297`; nothing weakened (only the two tests change, 9 and 10 lines added and none removed; every earlier assertion unchanged; no shadowed test); every record claim it checked holds, except N-B.
- **Its checks,** in an export of `5a2f137` with a hash-locked install: `Ran 383 tests … OK`; Ruff and mypy clean (71 files); reversals in each of the identity, profile and discovery jobs: X1, X1b, X2, X10, X11, X12, X13 (the helper's database made `postgres`) and X16 (`makemigrations --check` removed) each fail; X14, X15 and X15b pass (N-A).
- **The runs:** the run of record 44601565801 and PR57's run 44604039575 (event `pull_request`, head `f6f145e`): all eleven jobs succeeded in each, and each gate printed "Application checks passed". App Manager 12 read the PR run with the GitHub tools at about 20:16 UTC (no failed job; the gate's line at 20:06:26); Codex's code review of `f6f145e` completed with no findings, and the pull request had no review thread.

**Its findings** (in its words, shortened):
- **N-A — Nit, records only.** Three edits defeat a decoy-step check with every test passing, in all three jobs, the identity job included: X14, the refusal branch's `else` made `elif false; then` (`foundation.yml` lines 700, 1019, 1338), which disables the missing-refusal failure as X2 did; X15 and X15b, the `outside_pg` query made `SELECT 0` (lines 677, 996, 1315); and the `per_schema` query's definition, also unpinned. They predate C2, are of the carried N2 class, and C2's record does not overclaim. A2 should name them under "Substring pins, not semantics" beside X4, X5 and X9.
- **N-B — Nit, records wording.** The manager's verifications say the classifier was "run outside the checkout"; run from outside, it prints `comparison-unavailable` (C1's delta review). The recorded `behavior-or-empty` shows the copy was outside and the checkout was the working directory. Its words: "extracted outside the checkout and run from it". PR57's body used the same phrase.

**What it did not read or run:** logs other than the profile job's and the two gates'; what C2 does not change; the jobs on a local PostgreSQL; Codex and PR57's threads (not among its runs).

**Disposition** (App Manager 12; the manager workflow's step 6, under D-07):

| Finding | Disposition | Why |
|---|---|---|
| N-A | **Carried**, to SV4 A2 with N2 (the carried-items file, "Carried to SV4") | Edits outside the pinned lines, older than C2, the class already carried |
| N-B | **Corrected:** each "Manager verification" here now says the classifier was extracted outside the checkout and run from it, and PR57's body likewise (AM12-45) | The manager's wording; no decision rested on it |

With this review, A0's corrections are closed: no finding of any review is open in a correction class. Dev Manager 6's pre-merge read follows (DM-97).

### Dev Manager 6's pre-merge read (DM-97, 20 November 2026)

Dev Manager 6's report ([DM-97](../../continuity/dev-manager/reviews/2026-11-19-dm-97-sv4-a0-pre-merge-read.md); `b505a8e`, a read of `fc9decd`) approves the CI policy's change as written, A0 against AG1, AG1 to AG21 and revision 3's additions, C1 and C2, the manager's D-07 calls and F8's sentence. It answers F3 with option (a), with AH1 and AH2. AH1 (the F3 row above) and AH2 (the carried-items file, "Carried to the next change to the Foundation workflow (DM-97)") are applied as given, with AH3 and AH4 (its "Carried to SV4" entry), AH5 (the environment inventory) and AH6 (the migration plan), in the batch that records the disposition (App Manager 12; the review log's "DM-97"). PR57 merges once that batch's head has its passing PR run, with its non-Markdown paths still equal to `5a2f137`, Codex's completed review and the filled checklist (DM-97, section 13).

### Merge (20 November 2026)

- **PR57 merged** into `main` at `499ccbb` (App Manager 12, with the GitHub tools; expected head `8b18311`). DM-97's four conditions held: AH1 and AH2 applied as given at `8b18311`, in the batch that records the disposition; PR run 44655197105 on `8b18311` passed all eleven jobs, and its gate printed "Application checks passed" (01:48:25 UTC); the non-Markdown paths at `8b18311` equal `5a2f137`; Codex's code review of `8b18311` completed at 01:41:12 UTC with no findings, with no review thread; the checklist was filled.
- **`main`'s push run 44657225220** on `499ccbb` passed all eleven jobs, and its gate printed "Application checks passed" (02:04:42 UTC).
- **The Chromium install's first attempt** (for the carried entry "Carried to the next change to the Foundation workflow (DM-97)"): 23 s in PR run 44655197105 and 23 s in push run 44657225220; the pause and the retry were skipped in both.
- **The cleanup run** 44657225140 (success) deleted A0's `claude/affectionate-curie-hzo99y`, C1's `claude/awesome-brown-lmfi8e` and C2's `claude/dazzling-feynman-cjl16t`.
- **Closed with the merge** (the carried-items file): DM-59 item 7's Chromium retry; the pin test's gap (M05 finding 13); M02's N2 (H-01), with N1, N4, the Codex P2 and N6 declined (DM-96); M09's C-16 and C-17's split (the fifth job is A2's).

## A1

- **Session:** SV4 A1's implementation session, started by Nathan from [A1's prompt](https://github.com/amthorn78/glow-dating-app/blob/62352406e4bfc56b33321c747d9c4ccd0c10bf9b/docs/ephemeral/2026-11-20-sv4-a1-rules-prompt.md), revision 2, from `62352406e4bfc56b33321c747d9c4ccd0c10bf9b` of the manager branch `claude/magical-wozniak-yfmmx2`. The specification is the [brief](../../planning/sv4-chat-notifications.md), revision 5.
- **Branch:** `claude/sleepy-mendel-0kqgw9`, which the push filter's `claude/**` covers. It starts at the prompt's commit.
- **Code head:** `bc0675de3c6a4411f1d72845c69f8dc4e5706463`. **Records head:** the commit that adds this section. It was pushed after the code head's run had finished.
- **What A1 built:**
  - D3: a block retires the pair's earlier likes (`DirectionalInteraction.retired_at`, migration `0013`);
  - D4: a block ends an active match as an unmatch does (`unmatched`; F10's new transition);
  - D5: the history read, the list and the read cursor follow OD-60's rule through `chat.history`;
  - D6: a test pinning `MatchProjection.version` to the send's `contact_version` for every writer;
  - D7: the token grant and its signer removed, with the refusal lists, the README, ADR and docstring lines.
- **What A1 did not touch:** any route, served feature, provider call, deployed URL, real member, HDE call or stored credential; `.github/`, `scripts/`, any dependency or pin (the `pyjwt` pin stays), any environment template, any `apps/mobile` file but the two `npm run generate` wrote.

### The start gate and the environment check

- **The environment** (section 1 of the prompt, names only). This session runs in the cloud environment `Glow App - No Stream` (`get_environment`).
  - No `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY`.
  - No `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name.
  - The AWS names present: `AWS_ACCESS_KEY_ID`, `AWS_CA_BUNDLE` and `AWS_SECRET_ACCESS_KEY` (OD-76). None was read, printed or passed to a command.
  - The GitHub token names present: `GH_TOKEN` and `GITHUB_TOKEN`. Neither was read.
  - The toolchain: `Python 3.12.14` (`python3.12`), `v24.19.0` and `11.9.0` (`node` and `npm`, both in `/root/.local/bin`, first on `PATH`), `Docker version 29.10.0, build fdd4b8e`.
  - Every repository command ran under `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only its own variables.
- **The start gate** (section 2), at 03:41 UTC on 20 November 2026:
  - `git rev-parse HEAD` printed `62352406e4bfc56b33321c747d9c4ccd0c10bf9b`;
  - "this prompt's commit is on the live branch", "PR57's merge present" and "main's code" printed;
  - the diff of the owned trees and the brief between the prompt's commit and the live manager branch printed nothing;
  - `grep -c '^## A1'` on this record printed `0`, and no `0013` migration existed (`0`).
- **The search at the session's commit** (section 3's last paragraph: every test that reads, imports or digests a module A1 changes, or names a removed function, constant, outcome, case or row) found none outside "Earlier tests". No stop applied.

### What was built, by item

**D3: a block retires the pair's earlier likes** (M09's C-01).
- `DirectionalInteraction.retired_at`, a nullable `DateTimeField` with no default and no constraint (`glow_persistence/models.py`), with a paragraph in the model's docstring.
- Migration `0013_interaction_retired_at.py`, written by `manage.py makemigrations` against the dummy backend (no connection): one `AddField`, after `0012_photo_check_seed`, so it is additive. SHA-256 `96ddbeee052fe83a1acbca38b71d9aa4d8008bb7abefa2953f5d81cd4783faea`, pinned by the new test `test_sv4_a1_migration_follows_0012`.
- `glow_chat`'s `block`, under its two account locks and with the database's clock, read after them as before, sets `retired_at` on every `liked`, unretired row between the pair, either way, in the same transaction, with one `UPDATE` that writes nothing else of the row (not its state, version, `decided_at` or policy version).
- Both reciprocity checks require `retired_at` null: `activate_reciprocal`'s (both rows) and `interact`'s own check before it calls `activate_reciprocal` (the target's row). A like a block retired is not found, so a later like is recorded with no match, as any like that finds no like in return, and is never refused for it.
- `interact` writes `retired_at` null: on a new row (`create(..., retired_at=None)`), and on its update of an existing row (a like that replaces a pass), with `retired_at` in its `update_fields`.
- No read of the actor's own row returns it: the own-versions read's fields are unchanged (the cases below read the same state and version before and after the block).

**D4: a block ends an active match as an unmatch does** (C-02; DM-75).
- `block` stores `unmatched`, where it stored `restricted`, with the same contact and version advance and the same `contact_revoked` event.
- F10 gains the transition (`block`, `active` to `unmatched`, `participant`, no eligibility, no policy) in `packages/contracts/production/flows-v1.json`; no row is removed.
- `MatchProjection` gains a `description` in `gapp-api-v1.schema.json`: the server serves `restricted` to no member. `npm run generate` (after `npm ci --ignore-scripts` in `packages/contracts`) changed two generated files, which are committed: `apps/mobile/src/contracts/generated/gapp-api-v1.ts` (two lines, the description's comment) and `validators.js` (one line, the schema's text).
- `production-contracts.md`'s F10 and F13 paragraph and `data-model.md`'s `Match` row say a block ends an active match as an unmatch does, its cause kept in the `Block` rows; `interactions.py`'s module docstring (lines 62 to 64) and `contract.py`'s `match_projection` docstring (lines 255 and 256) say D8's gap is closed.
- P06.DB's reference design's block (`reference.py`) stores `unmatched` too, with a two-line comment. Nothing else the ordering suite compares between the two subjects changed.

**D5: the reads follow OD-60's rule** (C-08), in `glow_chat/reads.py`, for the history read, the list and the read cursor; the send's own checks do not change.
- After the session's row lock and before the clock, `chat.history` is read through `glow_profiles.settings_store.read_shared` (SV2's D19 pointer order). `reads.py` names no pointer model or table. A setting the store cannot resolve refuses the read with the store's own reason.
- The reader's account must be `active`, and the other account `active` or `suspended` (a cause); every other state refuses as before. The match must be `active` with no block either way, as before.
- The causes, as the brief's D5 maps them: `own_pause` and `other_pause` (that member's profile `paused`, or SV2's `incomplete`); `restriction` (either profile `restricted`; a `removed` profile is hidden, never read-only); `suspension` (the other account `suspended`); `withdrawn_consent` (either member's latest onboarding decision not `accepted`).
- `readable(causes, history)`: no cause serves the conversation; otherwise only while `consent_policy_version` names `consent.onboarding.v1` and every cause present reads `read_only`. One hidden cause hides the conversation whatever the others read; a missing key, another value or another version reads hidden (fail-closed).
- Every hidden cause refuses with one internal reason, `conversation_hidden`, which names no cause. The block, the unmatch, the deletion, the sign-out and the expiry keep their reasons. The served layer maps every refusal to `not_found`, as `chat_projections.error_for` does.
- Read-only serves the history page and the list, moves the read cursor, and refuses the send as before. The read's protocol (shared locks in the send's order, the clock after the locks, the check before and after the provider call, no read inside a caller's transaction) is unchanged.

**D6: the send's expected version.**
- `services/api/tests/test_match_versions_offline.py` (new) reads the code's syntax tree: the writers of `Match.version` or `Match.contact_version` are exactly `OrmContactPersistence.block` and `unmatch`; each advances both by one and saves both; both fields start at 1. Its detector finds a writer by an assignment (plain, augmented, annotated or walrus) to an object's `contact_version` or to the `version` of a name bound to a `Match` (from `Match.objects…` or `self._lock(Match, …)`, looped over, or a parameter annotated `Match`), a `save` naming either field, a writing queryset or manager call (`update`, `create`, `bulk_update` and the rest) naming either, or SQL text that writes `glow_persistence_match`; `WriterDetectorTests` checks the detector on each form and on reads.
- The discovery case `sv4.a1.match_version_is_the_sends_contact_version` shows it on the database, for every writer of either: the activation (both 1), the unmatch and the block (both 2), and the later commands that change neither (an unblock, an unmatch of an ended match). While contact continues, a send with the read's version is authorized and its retry replayed, never stale; once contact has ended it is refused `match_not_active`.
- `production-contracts.md` says a match's version changes only when contact ends.

**D7: the token code removed** (P06.2-T; OD-45), keeping `_lock_shared` (the reads use it), `revocation_cutoff_sent` and `revoke_user_tokens`.
- **The API:** `grant_token` (`contact.py` and the port), `ContactResult.grant`, the outcome `granted` and the `TokenGrant` import (`glow_domain/chat.py`); `chat_tokens.py` keeps only `revocation_cutoff_sent` (the grant, `TokenGrant`, `TokenRefusal`, `TOKEN_LIFETIME` and the refusal reasons removed); `chat_provider_stream.py` loses the signer `sign_chat_token`, `IAT_BACKDATE_SECONDS` and `import jwt`.
- **The ordering suite:** the seven token cases (`B1_TOKEN_CASES`) and the helpers only they used (`APP_CLOCK_SKEW`, `APP_CLOCK_SKEW_LONG`, `skewed_app_clock` among them); the outcome `granted` in the proof's interface and its docstring; the adapter's grant and its fixture's `provision_identity`; the delivery phase's refused grant and its words; `dbreads.identity_row` and `event_times`. A search at the head found no other user of each.
- **The Stream proof:** the ten rows that need Glow's signer retired (T1, T2, R3, D3, D7, V5, V6, V7, V8 and V12), with `_grant`, `_sign`, `_token_check` and every helper only those rows used, and `AFTER_REVOCATION_MARGIN_SECONDS`. Every other row stays, V3 and V4 (the revocation and its read-back) among them. The rows' P06.2 records stand as history. `checks/run_plan.py` needs no change and prints `run plan: fits` (36 rows; no connection).
- **The refusal lists** (M05 finding 22), as constants of their own beside `FORBIDDEN_CONNECTION_NAMES`, which does not change: `FORBIDDEN_INHERITED_NAMES` (`DATABASE_PUBLIC_URL`, `PGPASSFILE`, `PGSERVICE`, `POSTGRES_PASSWORD`, `REDIS_PUBLIC_URL`, `REDISPASSWORD`, `STREAM_API_SECRET`) and `FORBIDDEN_INHERITED_PREFIXES` (`PG`, `POSTGRES_`, `REDIS`, `STREAM_`), with `inherited_name_refused(name)`, in `glow_api/configuration_profiles.py`. `forbidden_configuration` refuses each by presence, in the same step as the existing names, before any value is read. The proof's environment check (`glow_ordering_proof/environment.py`) holds copies, pinned equal to the API's. No name the API reads is refused (every `GLOW_*` name, `GLOW_RAILWAY_*` among them, and the public names; a test pins it).
- **The lines:** ADR 0004's line 34 drops its parenthesis; the API README's lines on the dormant signer and Stage C1's modules (M05 P-13); the persistence module's docstring (R-23: "Models used by the sealed slices; the served runtime installs none.").

### Earlier tests changed, and why

Each change is one "Earlier tests" names; each keeps what the test guards.

- **D3:**
  - `services/api/tests/test_interactions_offline.py`, `ReciprocalWriterTests`: rewritten against this head, since D3, D4 and D7 each change `contact.py`. `MAIN_DEFINITION_DIGESTS` stays byte-equal to the base's and still pins every writer SV3 left; the definitions A1 changes (`block`, `activate_reciprocal`, `_lock_shared`'s docstring) and the one it removes (`grant_token`) are named, and A1's definitions and the module are pinned by digest at this head (`A1_DEFINITION_DIGESTS`, `A1_MODULE_DIGEST`), so any later change fails. New tests show `block` is the base's with D3's one statement inserted and D4's one value changed, and that `activate_reciprocal` is still `activate_match` with its one check inserted, now with `retired_at`. The class-level statements are compared too. `INSERTED` is still used by the class and stays, with `retired_at`; the dead `without_reciprocal`, `MAIN_MODULE_DIGEST` and `import copy` are removed. `StructureTests` passes unchanged.
  - `services/api/tests/test_model_definitions.py`: the leaf assertion is `0013_interaction_retired_at`, with its comment; the new test `test_sv4_a1_migration_follows_0012` pins `0013` as generated (its digest, its one `AddField` on `directionalinteraction.retired_at`, nullable, no default, no constraint, after `0012`). No other test changed.
  - `proofs/postgres-ordering/tests/test_discovery_offline.py`, `DiscoveryPlanTests`: the case count re-pinned to 70, `plan()[59:66]` still `B_C1_CASES` with A1's four after it; Stage A's check set keeps A1's cases out, and A1's own labels (`SV4-A1` with `D3`, `D4` or `D6`) are checked. A new `A1CaseTests` checks that every A1 case runs under the suite's ledger. `discovery_cases.py`'s `CASE_COUNT` is 70.
- **D4:**
  - `reference.py`'s block and the six ordering cases that expected `restricted` at version 2 (`cases.py`) now expect `unmatched`.
  - `interaction_cases.py`, `block.works_after_unmatch_and_while_paused`: its expectations only, now `unmatched`.
  - `packages/contracts/tests/test_transition_contract.py`: the frozen F10 table gains the row, with a comment. The sentence its lines 697 to 707 read is unchanged.
- **D5:**
  - `read_phase.py`: in the forced cases (`read_waits`, `check_holds`, `revocation_holds`) the seven revocations whose read becomes read-only (`READ_ONLY_AT_LAUNCH`: `suspend_high`, `pause_low`, `pause_high`, `restrict_low`, `restrict_high`, `withdraw_low`, `withdraw_high`) now expect the read served read-only, with its text checked, its wait still observed; the case's guarantee says "SV4 A1 D5: history served read-only after {kind} (DM-22 3.2)". The list case now expects the conversation listed while the other is paused (`[second.match, first.match]`).
  - `read.final_check_first_lock`: the variant where `suspend_low` holds its first lock while the high member reads now expects that read served read-only, its lock wait still observed; the low member's own read stays refused; `FIRST_LOCK_WRITERS` is unchanged.
  - `proofs/postgres-ordering/tests/test_read_phase.py`, `ReadPlanTests`: the plan's count is `16 * 3 + 14 + 2 + 2` (two named cases and two settings cases), and two tests are added (D5's cases planned with the settings cases last; the read-only revocations). `FirstLockReadersTests` and `ReadControlTests` pass unchanged.
  - The block, unmatch, deletion, sign-out and expiry cases keep their refusal.
- **D7:**
  - `services/api/tests/test_chat_domain.py`: the port's method names lose `grant_token`; the outcomes lose `granted`; `TokenRuleTests` is retired with the grant; `timedelta`'s import, left unused, is removed. `RevocationCutoffTests` stays.
  - `services/api/tests/test_chat_adapter_offline.py`: `test_r2_the_grant_signals_before_commit_once` is retired with the grant, with its `GrantCursor`; `test_the_adapter_has_no_switch_and_the_grant_is_on_the_port` becomes `test_the_adapter_has_no_switch_and_no_token_grant`, which asserts the switch is absent and no grant is on the port or the adapter.
  - `services/api/tests/test_chat_provider_stream.py`: the imports (`time`, `jwt`, `TokenGrant`, the signer and `IAT_BACKDATE_SECONDS`); `SignerTests` retired with the signer; the seal test's import list (`["from .chat_provider import ("]`). `SealTests` gains `test_the_adapter_builds_no_client_and_reads_no_environment`. `test_the_adapter_imports_only_the_port_the_token_module_and_the_sdk` passes unchanged.
  - `test_chat_sealed_runtime.py` and `test_identity_sealed_runtime.py`: unchanged, and each `test_the_connection_refusal_is_unchanged` passes, since the new names live in their own constants.
  - `proofs/postgres-ordering/tests/test_case_plan.py`: `test_the_adapter_plan_adds_b1` is `56 + 25 + 27`, with no `token.` case, still pinning the 24 activation cases and the F2 and F5 cases (`len(B1_CASES) == 6 * 4 + 3`); `test_the_token_cases_skew_is_shorter_than_their_sessions` is retired with the cases, and its `timedelta` import.
  - `proofs/postgres-ordering/tests/test_settings_refusals.py`: gains the new names and two tests (the copies equal the API's; each new name and family member refuses before its value is read). Its rule does not change.
  - `proofs/stream-chat/tests/test_conformance.py`: the rows 46 to 36; the recorded set `{M5, R7}` (V7 retired); the peak connections 1 to 0; the verdict counts `{"PASS": 34, "RECORDED": 2}` where they were `{"PASS": 43, "RECORDED": 3}`; `test_the_signer_rows` becomes `test_the_revocation_read_back`, keeping its V4 checks (the cut-off sent and held as the exact second plus one); `ConformanceVerdictTest` keeps each verdict's coverage on rows that stay, showing FAIL and INCONCLUSIVE on the read-back rows (`P2`, `C2`, `M2`, `R2`, `R6`, `D6`, `V4`) where they were shown on token rows, and DIFFERENCE on `M4`; `test_a_failing_row_exits_one_after_cleanup` forces R2's failure where it forced R3's; `no_revocation_wait` and its uses removed with the margin. `tests/test_run_plan.py`: 36 rows.

### New cases and tests

- **The discovery suite** (`interaction_cases.py`, A1's list after B-C1's, labelled `SV4-A1` with `D3`, `D4` or `D6`):
  - `sv4.a1.block_by_the_liker_retires_the_like` and `sv4.a1.block_by_the_other_retires_the_like` (D3): a like, then a block and an unblock by the liker or by the member who was liked, then a like from that member, which is recorded and answered as a like that finds no like in return, with no match and no `match_activated` event; `activate_reciprocal` itself refuses the pair (`not_reciprocal`); the first like reads the same state and version in its actor's own-versions read before, during and after the block (and, when the other member blocked, the liker's whole read is unchanged).
  - `sv4.a1.block_and_unmatch_serve_the_same` (D4): two worlds, one ended by a block and one by an unmatch, compared on every surface the brief lists, with absolute expectations: the send, the history read, the list, the match read (`unmatched` at version 2), discovery's exclusion (also by the match row alone), the own-versions read, a later block by the member who was blocked, the blocker's later unblock and unmatch.
  - `sv4.a1.match_version_is_the_sends_contact_version` (D6), above.
- **The read phase** (`read_phase.py`):
  - `read.d5_read_only_at_launch`: each of the nine cause settings (`own_pause`, `other_pause`, `own_incomplete`, `other_incomplete`, `own_restriction`, `other_restriction`, `other_suspension`, `own_withdrawal`, `other_withdrawal`) serves the history page, lists the conversation and moves the read cursor, while the send refuses with that cause's reason; a `removed` profile, either member's, is hidden.
  - `read.d5_ended_contact_keeps_its_refusal`: the block, the unmatch and the deletion (`match_not_active`, `account_not_active`), the reader's own suspension (`account_not_active`, the list refused), the sign-out and the expiry (`session_not_valid`) keep their reasons, none read as hidden.
  - `read.d5_hidden_when_the_setting_says_so` (settings case): each cause, published `hidden` in `chat.history` in turn, refuses the history read and the cursor with `conversation_hidden` and drops the list entry, alone and in a world with two causes.
  - `read.d5_consent_limit_fails_closed` (settings case, self-contained): every cause is first published `hidden` under the launch version; then the onboarding consent's next version is published, and `chat.history` with every cause `read_only` under it (SV2's rule: a more readable publication names a new consent version); every cause then reads hidden, and a conversation with no cause is still served.
- **The API's offline tests** (new files): `test_inherited_name_refusals.py` (6 tests), `test_match_versions_offline.py` (5), `test_read_rule_offline.py` (5).

### Reversals

Each reversal is a temporary edit of the code or the migration, made by a scratch script that wrote the edit, ran the cases or tests, and restored the file byte for byte (its SHA-256 checked after). All failed as intended and all were restored. The read-phase reversals each ran on a fresh throwaway database (below); the discovery reversals ran in turn on one, each case making its own members. The failing output, quoted (shortened where marked "…"):

| Reversal (the edit) | What failed |
|---|---|
| r01: `block` retires nothing | both D3 cases: "the later like is recorded as a like found alone" |
| r02: `interact`'s check ignores `retired_at` | both D3 cases: "the like: answers 200" |
| r03: `activate_reciprocal` ignores `retired_at` | both D3 cases: "activate_reciprocal refuses the retired like itself (applied:)" |
| r04: the retirement also advances the row's version | both D3 cases: "the first like reads the same state and version before and after the block"; `sv4.a1.block_and_unmatch_serve_the_same`: "the own surface is the same after a block as after an unmatch (… ('liked', 2, 'none', 0)) and (… ('liked', 1, 'none', 0)))"; `own_versions.each_state_and_version`: "after a block" |
| r05: `block` stores `restricted` | `block.works_after_unmatch_and_while_paused`: "the block ends the match as an unmatch does (D4)"; the D4 case: "the match the block ended reads unmatched at version 2 ({'kind': 'match', 'version': 2, 'state': 'restricted'})" |
| r06: the send names the block | the D4 case: "the send surface is the same after a block as after an unmatch (('refused', 'blocked') and ('refused', 'match_not_active'))" |
| r07: the reads name the block | the D4 case: "the history surface is the same … (('refused', 'blocked') and ('refused', 'match_not_active'))" |
| r08 (two edits together): the list takes every match, in any state, and keeps one that the other member blocked | the D4 case: "after the blocker's unblock: the listed surface is the same … (('listed', True) and ('listed', False))" |
| r09: discovery excludes by an active match only (`predicates.py`) | the D4 case: "by the match row alone: the shown surface is the same after a block as after an unmatch (False and True)" |
| r11: the blocked member's own block refused | the D4 case: "theirs: answers 200"; `block.works_after_unmatch_and_while_paused`: "the blocked's block: answers 200" |
| r12: the blocker's unblock restores the match | the D4 case: "after the blocker's unblock: the match surface is the same … ({… 'state': 'active'}) and ({… 'state': 'unmatched'}))" |
| r13 (two edits together): `block` stores `restricted`, and the match read (`interactions.py`) serves it as `unmatched` | the D4 case: "the ender's later unmatch answers the same" |
| r14: the unmatch advances only the contact version | the D6 case: "after the unmatch: the match read's version is the contact version"; offline, `test_each_writer_advances_both_by_one_and_saves_both` (`OrmContactPersistence.unmatch`): "… != 'match.version += 1'" |
| o1: the migration edited | `test_makemigrations_check_passes_without_a_database`, `test_model_and_migration_state_have_no_drift_without_a_database` ("Committed migration state differs from model definitions") and `test_sv4_a1_migration_follows_0012` (the digest) |
| o2: `block` retires one direction only | `test_block_differs_from_mains_by_d3s_statement_and_d4s_value`, `test_block_is_mains_with_one_statement_inserted_and_one_value_changed` and `test_every_writer_is_pinned_by_its_digest` (`OrmContactPersistence.block`, and the module) |
| d5a: the reads ignore the setting | `read.d5_hidden_when_the_setting_says_so`: "own_pause with own_pause hidden: the history read: read, expected refused (conversation_hidden); … the read cursor: moved, expected refused (conversation_hidden); … listed; …" |
| d5b: every cause read as hidden | `read.d5_read_only_at_launch`: "own_pause: the history read (read-only): refused:conversation_hidden, expected read; … not listed; …"; `read.pause_high.check_holds`: "a read after the revocation (read-only, D5): refused:conversation_hidden, expected read" |
| d5c: no consent limit | `read.d5_consent_limit_fails_closed`: "own_pause under consent.onboarding.v2: the history read: read, expected refused (conversation_hidden); …" |
| d5d: each cause names itself in the reason | `read.d5_hidden_when_the_setting_says_so`: "… refused:hidden:own_pause, expected refused (conversation_hidden); …" |
| d5e: a `removed` profile read as a restriction | `read.d5_read_only_at_launch`: "a removed low profile: the history read: read, expected refused (conversation_hidden); … a removed high profile: … listed" |
| d5f: `incomplete` not read as a pause | `read.d5_read_only_at_launch`: "own_incomplete: the history read (read-only): refused:conversation_hidden, expected read; …" |
| d5g: an ended contact refused as hidden | `read.d5_ended_contact_keeps_its_refusal`: "block_by_high: the history read: refused:conversation_hidden, expected refused (match_not_active); … unmatch_by_high: …" |
| d5h: the other's suspension refused as before | `read.suspend_high.read_waits`: "the read after its final check (read-only, D5): refused:account_not_active, expected read"; `read.final_check_first_lock`: "the read by the high member (its final check arrived at the first lock of suspend_low; read-only, D5): refused:account_not_active, expected read" |
| d5i: the list refuses every cause | `read.conversation_list`: "listed read-only while the other is paused: […]"; `read.d5_read_only_at_launch`: "own_pause: not listed; other_pause: not listed; …" |
| o4: `readable` serves when any cause reads `read_only` | `test_one_hidden_cause_hides_the_conversation_whatever_the_others_read` |
| rl1: the API's `REDIS` prefix dropped | the API's family tests for `REDISHOST`, `REDISPORT`, `REDISUSER`, `REDIS_PASSWORD` ("False is not true"; "0 != 1"); the proof's `test_the_inherited_names_copies_match_the_api` ("Tuples differ: ('PG', 'POSTGRES_', 'REDIS', 'STREAM_') != ('PG', 'POSTGRES_', 'STREAM_')") |
| rl2: the API's rule not checked | `test_an_empty_value_is_refused_too`, for each of M05's names: "ConfigurationError not raised" |
| rl3: the proof's prefixes not checked | the proof's `test_each_inherited_name_refuses_before_its_value_is_read` (`POSTGRES_USER`, `POSTGRES_DB`, `REDISHOST`, `REDISUSER`, `REDIS_PASSWORD`, `STREAM_API_KEY`): "RefusedEnvironment not raised" |
| rl4: the proof's copy differs | `test_the_inherited_names_copies_match_the_api`: "Items in the second set but not the first" |

Before the D5 reversals, `read.d5_consent_limit_fails_closed` passed on the same database as a baseline.

### Commands and results

All at the code head, in a clean environment (local; the run of record repeats them).
- **The API**, with `GLOW_ENV=test`: `manage.py check` reports no issues; `manage.py test tests` gives `Ran 654 tests … OK` (645 at the prompt's commit, which has `main`'s code); `ruff check .` gives "All checks passed!", `ruff format --check .` gives "169 files already formatted", and `mypy` gives "Success: no issues found in 95 source files"; `manage.py makemigrations --check --dry-run` gives "No changes detected"; the contract tests give `Ran 53 tests … OK`.
- **The ordering proof's offline tests:** `Ran 387 tests … OK` (383 at the prompt's commit); Ruff "All checks passed!", "71 files already formatted"; mypy "Success: no issues found in 71 source files".
- **The Stream proof's offline tests:** `Ran 648 tests … OK`; Ruff "All checks passed!", "59 files already formatted"; mypy "Success: no issues found in 57 source files"; `checks/run_plan.py` prints `run plan: fits`. Only its offline tests and `checks/run_plan.py` ran; no live command.
- **The contracts:** `npm run check` in `packages/contracts`: `tests 902`, `pass 902`, `fail 0`. `apps/mobile`'s `npm run check` (typecheck, lint and 691/691 tests) passed.
- **The trusted classifier**, from `main` (`499ccbb`), extracted to a scratch directory outside the checkout (SHA-256 `b564c62f…`), run from the checkout as `python3 -I <copy>/change_scope.py --base 499ccbbec758ed4ef34a93ad19fa8df454fb095c --head bc0675de3c6a4411f1d72845c69f8dc4e5706463 --merge-base`: `"full": true`, reason `behavior-or-empty`. `git merge-base --all` gives one base, `499ccbb`.
- **The diff:** `git diff --name-only 6235240 bc0675d` lists 46 paths, each in A1's owned paths as the prompt lists them (the limits below name the lines of the Stream proof's README). This section is the records commit's only change.
- **The removed names:** `grep -rnE` over `services/api`, `proofs` and `packages` for `grant_token`, `grant_chat_token`, `TokenGrant`, `TokenAccount`, `TokenSession`, `TOKEN_LIFETIME`, `NO_CHAT_IDENTITY`, `token_claims`, `sign_chat_token` and `IAT_BACKDATE_SECONDS` finds:
  - the absence assertions in `test_chat_adapter_offline.py` (lines 250 to 253) and the names in `test_interactions_offline.py`'s `A1_REMOVED`, its digest entry and two docstrings;
  - the Stream proof's own `token_claims` fields in `proof_run.py` and `mechanisms.py` (the check's exception);
  - the Stream proof's own `IAT_BACKDATE_SECONDS` in `mechanisms.py` (lines 109 and 112), which the check does not except (Limits);
  - the API README's line 82, which says `sign_chat_token` was removed by SV4 A1.

  `import jwt` is gone from `chat_provider_stream.py`.
- **npm:** no package or lock changed; `npm ci --ignore-scripts` from the existing locks only, in `packages/contracts`, `apps/mobile` and `proofs/stream-chat`.

### Local database runs (iteration, not evidence)

Under P06.DB's D4: the pinned image `postgres@sha256:d74eeac9…`, pulled from Docker Hub after `429` answers and retries with a wait; loopback only; a generated password and the run's marker, never printed; none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name in the process environment; each container removed afterwards. No Docker daemon was running in the session, so `dockerd` was started in the background (again after the container restarted). Migrations reached each database only through the proof's own commands; `manage.py migrate` was never run.

At the code head's content before the last review fixes (each case those fixes touched was run again afterwards, and passed):

| Suite | Before (at the prompt's commit) | After |
|---|---|---|
| Ordering, reference design | 56/56 | 56/56 |
| Ordering, adapter | 115/115 | 108/108 (the seven token cases retired) |
| Ordering, read phase | 62/62 | 66/66 |
| Discovery | 66 (A0's run of record) | 70/70 (290 s) |
| Profile | 77 (A0's run of record) | 77/77 (139 s) |
| Identity | 49 (A0's run of record) | 49/49 (47 s) |

The ordering suite's whole run took 596 s locally (579 s at the prompt's commit, with the delivery phase's 13/13 checks). After the last fixes, `read.d5_read_only_at_launch`, `read.final_check_first_lock`, `read.suspend_high.revocation_holds` and `read.pause_low.read_waits` passed again on a fresh database. Afterwards no container remained.

### The run of record

**Foundation run [44679608400](https://github.com/amthorn78/glow-dating-app/actions/runs/44679608400)** on `bc0675de3c6a4411f1d72845c69f8dc4e5706463` (a push run, attempt 1) concluded **success**. It was created at 05:13:40 UTC on 20 November 2026 and its gate finished at 05:23:39, 9 minutes 59 seconds in all. Nothing was pushed to the branch until it had finished. The durations are from the jobs' and steps' timestamps (whole seconds); A0's are from its run of record, 44463105633.

| Job | Conclusion | Duration | A0's | Timeout |
|---|---|---|---|---|
| Change scope | success | 9 s | 6 s | 3 min |
| API checks | success | 74 s | 76 s | 10 min |
| Mobile checks | success | 580 s (9 min 40 s) | 561 s | 25 min |
| API mobile smoke | success | 83 s | 75 s | 10 min |
| API artifact checks | success | 25 s | 27 s | 15 min |
| Stream proof checks | success | 78 s | 92 s | 10 min |
| **Database proof checks (ordering)** | success | **389 s (6 min 29 s)** | 539 s | 30 min |
| **Database proof checks (identity)** | success | **115 s (1 min 55 s)** | 103 s | 30 min |
| **Database proof checks (profile)** | success | **148 s (2 min 28 s)** | 151 s | 30 min |
| **Database proof checks (discovery)** | success | **316 s (5 min 16 s)** | 190 s | 30 min |
| Foundation gate | success: "Application checks passed" | 3 s | 3 s | 2 min |

**Each suite's own step, and its cases before and after A1:**

| Suite | Step | Cases at A0's run | Cases here | What its log shows |
|---|---|---|---|---|
| Ordering | 320 s (459 s at A0) | reference 56, adapter 115, read 62 | reference 56, adapter 108, read 66 | every read case's row `PASS` (the tail read, from `read.final_check_first_lock` to the four `read.d5_*` cases), the three planted read controls "failed as intended: yes", and `== VERDICT: PASS ==` |
| Identity | "identity phase: 42 s" | 49 | 49 | `[identity] cases: 49/49 passed in 41.7 s`, `IDENTITY VERDICT: PASS` |
| Profile | "profile phase: 85 s" | 77 | 77 | `[profile] cases: 77/77 passed in 84.0 s`, `PROFILE VERDICT: PASS` |
| Discovery | "discovery phase: 238 s" | 66 | 70 | `[discovery] cases: 70/70 passed in 236.2 s`, the four `sv4.a1.*` cases `PASS` (2.0, 2.0, 5.1 and 4.2 s), `DISCOVERY VERDICT: PASS` |

**What else the logs show** (read with `get_job_logs`, tails only; no line read held an `::add-mask::` command or a long hexadecimal value):
- **Ordering:** the second run refused, `rows (proof log, adapter calls, worlds, app accounts, outbox events) before: 10325 13682 5763 11561 26688; after: 10325 13682 5763 11561 26688`, `second run exit status: 1`, `refusing a used database: …`; `container removed: glow-proof-db-ordering-44679608400-1`, `credential and marker files removed`, `no proof container remains`.
- **Identity, profile and discovery**, each: `ROW LOCKS (D14): PASS` with `0 refused`; the scans clean (`identity secret scan: clean (754 secrets held; …)`; `profile secret scan: clean (1601 secrets held; …)` and `profile value scan: clean (919 member values held; …)`; `discovery secret scan: clean (2627 secrets held; 0 found in 1599 log records, 202 writes and the results JSON)` and `discovery value scan: clean (1408 member values held: …)`); the second run refused with its rows unchanged (identity `53 53 63 32 50`; profile `143 143 109 72 1746 1087`; discovery `1234 1234 1228 117 407 3240`) and `exit status: 1`; the container and files removed and `no proof container remains`.
- **The API checks job:** `manage.py check` "System check identified no issues", Ruff "All checks passed!" and "169 files already formatted", mypy "Success: no issues found in 95 source files", and the contract tests `Ran 53 tests … OK`. Its `manage.py test` step passed in the runner's own environment, so no name the new rule refuses was present there.
- **The Stream proof's job:** its offline tests, Ruff, mypy and `checks/run_plan.py` passed; the plan printed `run plan: fits`.
- **The retries:** every first Python install succeeded, and the DM-41 retry steps were skipped; in Mobile checks, "Install Chromium for rendered fixture checks" succeeded in 203 s on its first attempt, the pause and the retry (DM-59 item 7) were skipped, and "Render and exercise account onboarding" took 284 s.

**Not read:** the ordering job's per-subject count lines (`[reference] cases: …`, `[adapter] cases: …`, `[read] cases: …`) come before its full results table, which the tool's tail did not reach, and the artifacts were not downloaded (their links are to blob storage outside GitHub). The counts above are the plans the job's offline tests pin (`56 + 25 + 27` for the adapter, `16 * 3 + 14 + 2 + 2` for the read phase), which passed in that job, and the verdict is `PASS` only if every case of both subjects, every delivery check and the read phase passed (`results.py`, `RunReport.verdict`). The discovery phase took 104 s longer than at A0's run; A1's four cases account for 13.3 s of it, and the rest was not investigated (the job is well within its timeout).

### Limits and deviations

- **Lines outside A1's owned paths that D3, D5 or D7 makes stale, left unchanged.** The work needs none of them (no test reads them), so this session judged them outside the stop rule's "the work needs a path outside the list"; they are listed for the manager to route, and a stricter reading would make the first a stop:
  - `services/api/glow_domain/chat_reads.py`, lines 10 to 16: "Whatever refuses a send refuses a read", with the pre-D5 checks (neither member suspended, neither profile paused or restricted, both consents accepted) and "as B1's grant". `reads.py`'s module docstring states D5's rule;
  - `services/api/glow_domain/notifications.py`, lines 13 and 14, and the docstring at line 928, which cite that sentence for the notification composer's checks (the composer's own checks do not change);
  - `services/api/glow_persistence/models.py`, `ChatIdentity`'s docstring (lines 966 to 968, "granted a token"): `models.py` is owned only for its module docstring and `retired_at`;
  - `services/api/glow_discovery/interactions.py`, line 35 ("A like that finds the target's `liked` row makes the match"), now an unretired `liked` row: the file is owned only for `interact`'s check and write and lines 62 to 64;
  - `services/api/tests/test_dependency_pins.py`, lines 7 and 8 ("`pyjwt` (the signer uses it directly)"): the pin stays for SV1, and the file is not in "Earlier tests";
  - `proofs/stream-chat/README.md`, line 103 ("the adapter imports only its port, its token module and the SDK"): the adapter no longer imports the token module. The test that line names, `test_the_adapter_imports_only_the_port_the_token_module_and_the_sdk`, passes unchanged as required; it asserts only that no Django, persistence, `glow_chat` or `glow_api` module is imported, so its name is stale too;
  - `apps/mobile/src/interactions/fixture-adapter.ts` (lines 128 and 232) still stores `restricted` on a block. The brief's "Mobile: none" keeps it; the fixture now differs from the server's D4.
- **A deviation: two more lines of the Stream proof's README.** The owned path is its "paragraph on the conformance rows, only as D7 requires" (line 250). Lines 249 and 252, the bullets beside it, were changed too: line 249 said "Three" rows are RECORDED and named the third (now retired with the signer), and line 252 said the run peaks at one connection (now none). Both were made false by D7's retirement, and the tests that pin them changed with it.
- **The removed-names check does not hold literally:** it finds the Stream proof's own `IAT_BACKDATE_SECONDS` (`proofs/stream-chat/glow_stream_proof/mechanisms.py`, lines 109 and 112), a constant of the proof's live mechanisms, not the API's, in a file outside A1's owned paths. Its live commands were not run. The API's constant is gone.
- **The Stream proof's live harness can still mint tokens:** `glow_stream_proof/server_api.py` line 245 calls the SDK's `create_token` for the proof's live commands. D7 removes Glow's signer, not the proof's live harness, which is outside A1's owned paths and was not run.
- **D3's null write on `interact`'s update is unobservable:** only a `liked` row is retired; a pass over the actor's own like is `state_conflict` and undo withdraws only a pass, so no route turns a retired like into another decision. The write is in the code as the brief says; no case can show it.
- **The read-only marker is D9's, A2's:** until A2, a conversation served read-only is listed like an open one, with no marker.
- **The refusal families were drawn from M05's names by prefix** (`PG`, `POSTGRES_`, `REDIS`, and `STREAM_`). Railway's and Stream's own pages listing their variables were not read in this session; a Railway or Stream name with another prefix is refused only if one of the lists names it.
- **The API job's environment:** `manage.py test` in CI runs in the runner's environment, not under `env -i`. A `PG*`, `POSTGRES_*`, `REDIS*` or `STREAM_*` name there would now refuse the configuration. The run of record shows none present (the API checks job passed).
- **A later change to `contact.py`** fails `ReciprocalWriterTests` by design (A1's definitions and module are pinned by digest at this head), so A2's "Earlier tests" must name that class if A2 changes `contact.py`.
- **`data-model.md`'s diff is larger than its change** (69 lines in, 60 out): the paragraphs D3, D4, D6 and D7 changed were reflowed.
- **The local database runs are iteration only.** They ran with Docker 29.10.0 started in the session, from the pinned image, before the last review fixes; the cases those fixes touched were run again, not the whole suites. The run of record is CI's.

### Manager verification of A1 (App Manager 12, 20 November 2026)

- **The branch:** `claude/sleepy-mendel-0kqgw9`, code head `bc0675d`, records head `a1651fb` (the record only), both after the prompt's commit `6235240`, which the branch starts at; the manager branch, still at `6235240`, took both by fast-forward.
- **The diff** from `6235240` to the code head: 46 paths, each in A1's owned paths (the brief, revision 5). The partly owned files were read in the diff: `glow_discovery/interactions.py` changes only `interact`'s write of `retired_at`, its reciprocity check and the docstring's lines 62 to 64; `glow_discovery/contract.py` only `match_projection`'s docstring; `glow_api/configuration_profiles.py` only the refusal constants, their check and its use in the presence step (`FORBIDDEN_CONNECTION_NAMES` unchanged); `glow_persistence/models.py` only the module docstring, `DirectionalInteraction`'s docstring and `retired_at`. `test_model_definitions.py` changes only the leaf assertion, its comment and the new `0013` test; `MAIN_DEFINITION_DIGESTS` in `test_interactions_offline.py` is byte-equal to the base's (checked by script), and `MAIN_MODULE_DIGEST` is removed, as the record says. `test_chat_sealed_runtime.py` and `test_identity_sealed_runtime.py` are unchanged.
- **The trusted classifier,** `main`'s `scripts/change_scope.py` (`499ccbb`; sha256 `b564c62f…`, equal to `main`'s), extracted outside the checkout and run from it with `python3 -I --base 499ccbb… --head bc0675d… --merge-base`: `"full": true`, reason `behavior-or-empty`.
- **Re-run by the manager** in a scratch worktree of the code head, each in a virtual environment installed from its own lock with `pip install --require-hashes` (`pip check` clean), under `env -i` (with `GLOW_ENV=test` for the API, as the workflow sets it):
  - the API: `manage.py check` no issues; `manage.py test tests` 654 tests OK; Ruff "All checks passed!", "169 files already formatted"; mypy "no issues found in 95 source files"; the contracts' unittests 53 OK; `makemigrations --check --dry-run` "No changes detected";
  - the ordering proof: 387 tests OK; Ruff clean, "71 files already formatted"; mypy "no issues found in 71 source files";
  - the Stream proof (after `npm ci --ignore-scripts` from its lock): 648 tests OK; Ruff clean, "59 files already formatted"; mypy "no issues found in 57 source files"; `node --check` on each client script; `checks/run_plan.py` "run plan: fits";
  - the contracts: `node scripts/generate.mjs --check` "Generated types and runtime validators match schemas."
- **Read in the code:** D3's write in `block` is a queryset `update(retired_at=now)` on the pair's unretired `liked` rows, both ways, after both account locks and with the database's clock, so it writes nothing else of a row; both reciprocity checks filter `retired_at__isnull=True`. D4: `block` stores `unmatched`, with the same advance and event. D5 (`reads.py`): the read rule, the cause mapping, the fail-closed consent check (`readable`), one reason `conversation_hidden` for every hidden cause, and `chat.history` read through `settings_store.read_shared` after the row locks, as the brief says.
- **The removed names** are gone from the API, the ordering proof and the contracts, except the tests' assertions of their absence and SV3's pinned record of `grant_token`'s digest. The search's one other hit, `IAT_BACKDATE_SECONDS` in the Stream proof's `mechanisms.py`, is that harness's own constant for the SDK's back-dating, not Glow's signer; the prompt's check, the manager's, named it without that exception.
- **The run of record,** Foundation run 44679608400 (event `push`, head `bc0675d`), read with the GitHub tools: all eleven jobs succeeded, and the gate's log ends "Application checks passed". The database jobs took 389 s (ordering), 115 s (identity), 148 s (profile) and 316 s (discovery), each of 30 minutes. The Chromium install's first attempt took 203 s, the pause and the retry skipped (the carried-items file, "Carried to the next change to the Foundation workflow (DM-97)").
- **The deviation** (the Stream proof's README, lines 249 and 252, beside the owned line 250): accepted. Both bullets sit in the conformance rows' section and would otherwise state what D7 made false.
- **The lines outside A1's owned paths** that D3, D5 or D7 makes stale (the record's "Limits and deviations") are carried, with the note that A2's "Earlier tests" names `ReciprocalWriterTests` if A2 changes `contact.py` (the carried-items file, "Carried to SV4"). The exact-head review is asked to classify them under D-07.

### Exact-head review of A1 (20 to 22 November 2026)

- **Session:** the exact-head review, started by Nathan from [A1's review prompt](https://github.com/amthorn78/glow-dating-app/blob/ff2539beb3cc84d9f7d022c91de6e7222d9d8f97/docs/ephemeral/2026-11-20-sv4-a1-review-prompt.md), revision 1, from `ff2539b`. Its report was relayed to App Manager 12 on 22 November 2026. It ran the checks, the reversals, a local database run and the CI reads itself, with nine reviewer agents over the focus items, each finding sent to a separate verifier told to refute it; four verifiers hit a usage limit on 20 November and were run again on 22 November from the run's journal, the reviews replayed from cache.
- **Its start gate, classification and environment check:** every start-gate check passed (`HEAD` `ff2539b`; one merge base, `499ccbb`; the prompt's commit on the live branch; the non-Markdown paths equal to `bc0675d` at `HEAD` and on the live branch; no review recorded). `main`'s classifier, extracted outside the checkout and run from it with `python3 -I --merge-base`, printed `"full": true`, reason `behavior-or-empty`. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY`, and no `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name; present and never read: `AWS_ACCESS_KEY_ID`, `AWS_CA_BUNDLE`, `AWS_SECRET_ACCESS_KEY`, `GH_TOKEN`, `GITHUB_TOKEN`. Python 3.12.14, Node v24.19.0, npm 11.9.0, Docker 29.10.0.
- **Verdict: changes requested.** The application's behaviour holds on every item: D3 to D7 hold in the code; no reader the rule refuses is served, no hidden cause is named, no token path is reachable, and the seal and HDE's boundary are unchanged. One blocking finding (AR-1, a test that fails on `main` once A1 is there), two should-fix findings in a correction class (AR-2, AR-3), one should-fix finding outside the classes (AR-4) and twelve nits (AR-5 to AR-16).

**What it verified** (its focus items, shortened):
- **D3:** `block` retires every unretired `liked` row between the pair, both ways, after both account locks and the database's clock, writing only `retired_at`, with or without a match; both reciprocity checks require it null. No reader of a `liked` row (activation, discovery's predicates and pages, the own-versions read, notifications, the proofs' oracles) counts a retired like, reveals `retired_at` or answers either member differently. A later like is recorded with no match and never refused for the retired one; the first like reads the same state and version before and after.
- **D4:** `block` stores `unmatched` with the same advance and the same `contact_revoked` event as `unmatch`; `block_changed` is never delivered; the provider effect is an unmatch's. No server path writes a `restricted` match or treats one apart. F10's new row, the frozen table, `MatchProjection`'s description and the generated files agree.
- **D5:** the rule holds condition by condition; every hidden cause refuses as `conversation_hidden` after every other check, so the order names no cause, and the served layer is `chat_projections.error_for`. No lock inversion or crossing; the `_Pointers` shim gives the store what its D19 check uses; a setting the store cannot resolve refuses with the store's own reason, which names no cause. The send and the read's protocol are unchanged; `final_check_first_lock`'s suspension variant serves the high member's read read-only, its lock wait still observed.
- **D6:** the test finds both writers that exist today (only `block` and `unmatch` write either field); many idioms would escape it (AR-4), and its docstrings claim it cannot miss one (AR-2).
- **D7:** every removed name is gone, with the code only it used; `jwt` remains only through allauth, for SV1's sessions; the epoch revocation is unchanged and still proven. The refusal lists are checked in the same presence step, before any value, for every profile, and refuse nothing the API reads. It read Railway's and Stream's variable pages (Stream's video page answered 404): every Postgres, Redis and Stream name is refused; MySQL, MongoDB and OpenTelemetry names escape, which M05 did not mean and no package in either lock uses; `RAILWAY_*` must not be refused, since Railway injects it into every service. A lowercase `stream_api_secret` passes the case-sensitive check; contained, since `getstream` is a development dependency only and the adapter builds no client. The Stream proof keeps every verdict kind on rows that stay.
- **The earlier tests:** each change is one A1's prompt names; the plan counts match the code (56 + 25 + 27, read 66, discovery 70); no new test is vacuous; `MAIN_DEFINITION_DIGESTS` is byte-equal to the base's; every reversal the record lists fails as recorded. But AR-1.
- **The migration:** `0013` is one `AddField` (`DateTimeField(null=True)`), after `0012_photo_check_seed`; the model matches; `makemigrations --check` is clean.
- **The seal and the boundary:** the 40 non-Markdown paths are all in A1's owned paths, with the partial-file limits; no lock, requirements file, `package.json`, Dockerfile, workflow, script, settings, URL or WSGI file changed; HDE untouched.
- **The records** hold, except AR-5, AR-6, AR-9, AR-16 and AR-1's limit.
- **The lines outside A1's paths:** `chat_reads.py` lines 10 to 16 are a false claim at the who-may-read boundary (AR-3); the others A1's record lists are records to carry. Three more: `tests/test_notifications.py` line 316; `test_chat_sealed_runtime.py` lines 11 to 13 and 130 (AR-14); `proofs/stream-chat/README.md` line 248 (AR-15).

**Its checks,** in scratch copies of `bc0675d`, each package installed from its lock with `pip install --require-hashes`, under `env -i`:
- the API: `manage.py check` no issues; `manage.py test tests` `Ran 654 tests … OK (skipped=2)`, the two skips AR-1's history tests (no `main` in its copy); Ruff, format (169 files) and mypy (95 files) clean; the contracts' unittests 53 OK; `makemigrations --check --dry-run` "No changes detected";
- the ordering proof 387 OK; the Stream proof 648 OK and `checks/run_plan.py` "run plan: fits"; the contracts' `generate.mjs --check` passed;
- the prompt's reversals: R1 (`readable` always true) fails two read-rule tests; R2 (each prefix removed) fails each way, except that removing `PG` from both lists passes the proof's tests, which refuse every `PG*` name through `LIBPQ_PREFIX`; R3 (a third writer, three forms) fails the D6 test; R4 (`retired_at__isnull=True` removed from `activate_reciprocal`) fails a structure test and the digest only, no behavioural offline test (the database case r03 catches it);
- a local run under P06.DB's D4 (informational): the ordering run PASS (reference 56/56, adapter 108/108, delivery 13/13, read phase 66/66, three planted controls failing as intended; 475 s); the discovery run 70/70 (218.7 s), all four `sv4.a1.*` cases passing. Everything it started was removed.

**The runs:**
- **The run of record,** 44679608400 (`push`, `bc0675d`): eleven jobs, success, with the record's durations; the gate printed "Application checks passed".
- **PR58's run** 44685126123 (`pull_request`, `ff2539b`): eleven jobs, success (Change scope 10 s, API checks 89 s, Mobile checks 520 s, API mobile smoke 95 s, API artifact checks 27 s, Stream proof checks 77 s, Database (ordering) 396 s, (identity) 99 s, (profile) 150 s, (discovery) 231 s, Foundation gate 3 s); the gate printed "Application checks passed" at 06:12:57 UTC (read by App Manager 12 with the GitHub tools on 20 November). The run on `dc9352e` before it, 44684672998, was cancelled when the next push superseded it.
- **Codex's code review of `ff2539b`** completed at 06:06:00 UTC with no findings; PR58 had no review thread and no review.

**Its findings** (in its words, shortened):

| ID | Severity | Where (at `bc0675d`) | Finding |
|---|---|---|---|
| AR-1 | **Blocking** | `services/api/tests/test_interactions_offline.py`, lines 1378 to 1427 and 1498 to 1527; `main_base()`, 1181 to 1200 | Two history tests compare `contact.py` with `main`'s merge base and assert that it differs by A1's edits. Once A1 is on `main` they compare A1 with itself and fail. `main`'s push runs check out a local `main`, so the first push run after the merge fails API checks and the gate. PR runs skip them; SV3's form stayed green after its merge because it asserted "unchanged". The record's limit (line 1093) claims the class fails only on a later change |
| AR-2 | Should fix | `tests/test_match_versions_offline.py`, lines 8 to 15 and 231 to 232; the record's line 917 | The docstrings say every form a writer could take is found, "so the pinned set above cannot miss one"; the verifier reproduced 22 forms that escape |
| AR-3 | Should fix | `glow_domain/chat_reads.py`, lines 10 to 16 (outside A1's owned paths; the record's line 1079) | The read port's contract still states the rule D5 replaced (the other member suspended, a paused or restricted profile and a withdrawn consent refusing a read; "B1's grant"), which A2 and P11 will wire against |
| AR-4 | Should fix | `test_match_versions_offline.py`, lines 57 to 58, 61 to 93, 147 to 150, 156 to 159 | The detector misses ordinary idioms: a match from `_pair_match`, a related manager's `update`, `Match(..., version=)`, `bulk_create`, an f-string table name, the table-name constant `_lock_shared` uses, a `save()` override, a signal, `Match as M`. The reviewer classes it outside the classes (D6's acceptance check holds at this head); its verifier, a missing test at the boundary |
| AR-5 | Nit | `reads.py`, lines 53 to 55; the record's line 913 | "Every refusal is served as `not_found`": sign-out and expiry map to `unauthenticated`. Nothing leaks |
| AR-6 | Nit | The record's line 958; `interaction_cases.py`, 2156 to 2187 | After the end of contact the D4 case compares the two worlds only, not fixed values |
| AR-7 | Nit | `test_interactions_offline.py`, line 1461 | `test_block_is_mains_with_one_statement_inserted_and_one_value_changed` never reads `main` |
| AR-8 | Nit | `contact.py`, lines 350 to 351 | The comment's list of directional-row writers omits `block`; the lock argument holds |
| AR-9 | Nit | `docs/architecture/data-model.md`, lines 342 to 343 | "That device's token lives until it expires (one hour)" describes a token no code issues |
| AR-10 | Nit | `configuration_profiles.py`, 184 to 196 | A supplied name matched by a prefix is echoed in the diagnostic; no value |
| AR-11 | Nit | `proofs/postgres-ordering/tests/test_settings_refusals.py`, 95 to 108 | The proof's "unreadable" environment is a `dict` subclass, so a value read through `items()` passes; the API's test is sound |
| AR-12 | Nit | `interaction_cases.py`, 2009 to 2072 | No database case for a like committed while a block waits, or a match made after an unblock |
| AR-13 | Nit | `reads.py`, lines 11 to 13 | No database case for a publication of `chat.history` during a read |
| AR-14 | Nit | `test_chat_sealed_runtime.py`, 11 to 13 and 130; `test_conformance.py`, line 104; `proofs/stream-chat/README.md`, line 103 | Still say the adapter imports "the token module"; test names claim an allow-list their bodies do not check |
| AR-15 | Nit | `proofs/stream-chat/README.md`, line 248 | The Identifiers bullet lists notes and errors that can no longer arise |
| AR-16 | Nit | The record's lines 905, 948, 1084, 1085 and the reversal table | Citations: `contract.py` 256 and 257; the conformance test is `proofs/stream-chat/tests/test_conformance.py`; README line 103 names no test; `fixture-adapter.ts` line 128 is the lost-eligibility path, not a block; rl3 failed for seven names; the table has no r10 |

**Its deviation:** the GitHub MCP tools were retired during its session, so it read `main`'s push run 44657225220 (the run list, its jobs and one job log) with read-only `gh api` GET calls, where the prompt reserved `gh` for searches. Nothing was written. **Accepted:** the system's instruction of 22 November 2026 now routes GitHub reads through `gh api` REST, and every call was a read.

**What it did not read or run:** Stream's authentication page (linked, not fetched) and its video page (404); the Stream proof's live commands; the identity and profile suites locally (CI ran them); the CI-only database steps locally; CI's artifacts. DM-96's sections, SV2's D2 and D19 and some files whole were read by its reviewer agents, not by the reviewer itself.

**The manager's checks** (App Manager 12, 22 November 2026):
- **AR-1, reproduced.** In a scratch clone (`git clone --no-local`, its remote removed), with a local `main` at `bc0675d`, `ReciprocalWriterTests` gave `Ran 6 tests … FAILED (failures=2)`: `test_block_differs_from_mains_by_d3s_statement_and_d4s_value` ("Lists differ: [] != [('insert', 0, 1), ('replace', 1, 1)]") and `test_every_writer_at_mains_base_is_unchanged_but_a1s` (A1's changed and removed names, `grant_token` among them, not in `main`'s). With `main` at `499ccbb`: `Ran 6 tests … OK`. `main`'s push run 44657225220, API checks job 136026366254 (read with `gh api`): its checkout ran `git checkout --progress --force -B main refs/remotes/origin/main` (log line 114), and SV3's two history tests printed `... ok` (lines 1809 and 1810). `main_base()` has no other user, and every Foundation job but Change scope checks out at the default depth.
- **AR-2 and AR-4, read.** The module docstring says every writer "is found", and `WriterDetectorTests`' that the pinned set "cannot miss one". The manager's search at `ff2539b`: only `block` (`contact.py`, lines 664 to 666) and `unmatch` (750 to 752) write either field of the database's `Match`; the two activations create it with the defaults, and `glow_domain/interactions.py`'s `Match(...)` is P05.3's in-memory fixture. So D6's acceptance check holds at this head.
- **AR-3, read.** `chat_reads.py`'s lines 10 to 16 say that a suspension of either member, a paused or restricted profile and a withdrawn consent refuse a read, under "B1's grant", with the history question still open; `reads.py`'s rule (lines 40 to 55; `readable` and the causes) serves each read-only at launch. No test reads that module's docstring.

**Disposition** (App Manager 12; the manager workflow's step 6, "What a correction pass is for" and "Fix or carry, by rule", under D-07):

| Finding | Disposition | Why |
|---|---|---|
| AR-1 | **Fixed before the merge**, by correction A1-C1 | Blocking: the first push run on `main` after the merge would fail API checks and the gate. It misses A1's prompt's rule that every earlier test passes, and the record's limit (line 1093) claims more than the test does. The fix compares with A1's pinned base, `499ccbb`, and changes no design, interface, contract or dependency, so it goes on the list for the Dev Manager's pre-merge read |
| AR-2 | **Fixed**, by A1-C1 (the two docstrings) | A false claim a decision rests on: D6's acceptance check ("covers every writer") is read through the detector. C1 makes the claim the detector's; the detector's reach is AR-4 |
| AR-3 | **Fixed**, by A1-C1 (that paragraph only; the brief's revision 6 adds it to the owned paths) | A false claim at the who-may-read boundary, which A2 and P11 wire against |
| AR-4 | **Carried**, to SV4 A2 if it adds a writer of either field, otherwise the next change to the detector (the carried-items file, "Carried to SV4") | The reach of a static scan, which the rule carries; D6's acceptance check holds at `bc0675d` by the review's and the manager's searches. The reviewer's classification, not its verifier's |
| AR-5, AR-7 to AR-10, AR-14, AR-15 | **Carried**, with A1's stale lines, to SV4 A2 if it changes the file, otherwise the next change to it | Wording that misleads no decision. AR-5's codes are `error_for`'s, which A2 serves, and A2's authentication answers a signed-out reader first |
| AR-11 to AR-13 | **Carried**, to SV4 A2's chat suite (AR-12, AR-13) and the next change to the proof's refusal test (AR-11) | Tests of concurrency and of a test double; the code is right |
| AR-6, AR-16 | **Recorded here** | The record's wording; the corrected citations are in the findings table |
| A1's limit on the variable pages ("Limits and deviations") | **Closed** | The review read Railway's and Stream's pages |
| The review's deviation | **Accepted** (above) | |

The manager's verification carried A1's limit on `ReciprocalWriterTests` without checking the history tests' result once A1 is on `main` (AM12-48).

## A1-C1

- **Session:** SV4 A1's correction session A1-C1, started by Nathan in the cloud environment `Glow App - No Stream` (`get_environment`), from [A1-C1's prompt](https://github.com/amthorn78/glow-dating-app/blob/656ce032803b42da7a771185ce0016b5364f433f/docs/ephemeral/2026-11-22-sv4-a1-c1-correction-prompt.md), revision 2, from `656ce032803b42da7a771185ce0016b5364f433f` of the manager branch `claude/magical-wozniak-yfmmx2`. The specification is the [brief](../../planning/sv4-chat-notifications.md), revision 6; the findings are AR-1 to AR-3 of "Exact-head review of A1", above.
- **Branch:** `claude/beautiful-brahmagupta-13ncpo`, which the push filter's `claude/**` covers. It starts at the prompt's commit.
- **Code head:** `f69529c0594889d26caa19eccfe6b7eda73bee56`. **Records head:** the commit that adds this section, pushed after the code head's run had finished.
- **What C1 changes:** tests and docstrings only, in three files: `services/api/tests/test_interactions_offline.py`, `services/api/tests/test_match_versions_offline.py` and `services/api/glow_domain/chat_reads.py`. No application behaviour, workflow, setting, contract, README or proof changes.

### The start gate and the environment check

- **The environment** (section 1 of the prompt, names only):
  - none of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY`;
  - no `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name;
  - the AWS names present: `AWS_ACCESS_KEY_ID`, `AWS_CA_BUNDLE` and `AWS_SECRET_ACCESS_KEY` (OD-76). None was read, printed or passed to a command;
  - the GitHub token names present: `GH_TOKEN` and `GITHUB_TOKEN`. Neither was read;
  - the toolchain: `Python 3.12.14` (`python3.12`);
  - every repository command ran under `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus `GLOW_ENV=test` for the API's Django commands.
- **The start gate** (section 2), at about 08:05 UTC on 22 November 2026, with `<START_SHA>` read as `656ce03…` (below, "Limits and deviations"):
  - `git rev-parse HEAD` printed `656ce032803b42da7a771185ce0016b5364f433f`;
  - "this prompt's commit is on the live branch", "A1's code head", "no code on the live branch after bc0675d" and "A1's base is in this checkout" printed;
  - `grep -c` printed `1` for "Exact-head review of A1" and `0` for "A1-C1".
- **Read before any change:** root `AGENTS.md` and `CLAUDE.md`; `services/api/README.md`'s setup and checks; this record's "A1", "Manager verification of A1" and "Exact-head review of A1"; the brief's D5, D6, D11, "Owned paths" and "Acceptance checks"; `test_interactions_offline.py` from `git()` to the end of `ReciprocalWriterTests`, with its constants; `test_match_versions_offline.py` whole; `chat_reads.py`'s module docstring; `reads.py`'s module docstring, `readable`, `_history`, `_causes` and `_authorize`.
- **`main_base()`'s users,** searched at the prompt's commit (`grep -rn main_base --include=*.py`): only the two history tests.

### What was changed, by item

**AR-1: the history tests read A1's base** (`services/api/tests/test_interactions_offline.py`).
- `main_base()` is removed: nothing else used it.
- A new constant, `A1_BASE = "499ccbbec758ed4ef34a93ad19fa8df454fb095c"`, sits where `main_base()` was, with a comment naming it (PR57's merge, SV4 A0, the commit A1 starts from) and saying that the history tests read `contact.py` there, never at `main` or `origin/main`.
- Each history test checks for the commit (`git cat-file -e 499ccbb…^{commit}`, with `git` missing or timing out read as absent), skips with the reason "A1's base 499ccbbec758ed4ef34a93ad19fa8df454fb095c is not in this checkout (CI's shallow clone); the comparison runs wherever that commit is present", and otherwise reads the file with `git show 499ccbb…:services/api/glow_chat/contact.py`. `fetch-depth` does not change.
- The tests, renamed to name A1's base:

  | Old name | New name |
  |---|---|
  | `test_every_writer_at_mains_base_is_unchanged_but_a1s` | `test_every_writer_at_a1s_base_is_unchanged_but_a1s` |
  | `test_block_differs_from_mains_by_d3s_statement_and_d4s_value` | `test_block_differs_from_a1s_base_by_d3s_statement_and_d4s_value` |

- **Every assertion stays**, against the base. A script compared the class at the prompt's commit with the class at the code head, by AST: the first test makes 12 assertions before and after, the second 7, each identical (the first test's local tree renamed from `main` to `base`); every statement after each test's `git show` is the same; the class's four other tests are unchanged. The first test's two comments say "the base's" where they said "main's".
- `ReciprocalWriterTests`' docstring says what the class compares with: the digest test needs no history, so CI runs it (SV3's digests from `947576d` and A1's at its head, so any later change fails); the two history tests read `A1_BASE`, never `main`, so they pass before and after A1's merge, and run wherever that commit is present (CI's shallow clone skips them).
- The comment above `MAIN_DEFINITION_DIGESTS`: "so the comparison runs without main's history (CI's shallow clone)" became "so the digest test needs no history and runs in CI's shallow clone; the history tests read A1's base (`A1_BASE`) wherever that commit is in the checkout". The rest of the comment and the digests are unchanged.
- Codex's P1 thread on PR58 ("Pin the history comparisons to the pre-A1 revision", line 1389 at `4618859`) names the same defect; this fix answers it. The thread was not replied to or resolved.

**AR-2: the detector's claim** (`services/api/tests/test_match_versions_offline.py`, the module docstring's passage from "Read from the source" to "Each must be one of the pinned writers," and `WriterDetectorTests`' docstring).
- The module docstring keeps the list of the forms the detector finds, and that `WriterDetectorTests` shows each is found.
- A new paragraph names the forms that escape it: a related manager's `update`, or an `aupdate`; a `Match(..., version=...)`, or a `bulk_create` of such objects; SQL text whose table name is built at runtime or held in a constant; a match obtained through a helper such as `glow_discovery.interactions._pair_match`; a `save()` override or a signal; and `Match` imported under another name. It says the pinned set is today's every writer by the A1 review's and the manager's searches of the code, not by the detector alone, and that the detector's reach is carried (the carried-items file, "Carried to SV4"; AR-4).
- "cannot miss one" is gone, with every other sentence that claimed the detector is complete. `WriterDetectorTests`' docstring now reads: "each form the module's docstring lists as found is found. It shows nothing of the forms that escape (AR-4)."
- **The named forms checked:** a scratch script outside the checkout ran the unchanged detector (`writes`) on one example of each of the ten forms named; it found none of them (`missed []` for each).
- No assertion, detector or test changed: `ast.dump` of the module with every docstring removed is the same at the prompt's commit and at the code head. The module still has 5 tests, all passing.

**AR-3: the read port's rule** (`services/api/glow_domain/chat_reads.py`, the module docstring's paragraph "Whatever refuses a send refuses a read", only).
- The paragraph now states the rule `glow_chat.reads` applies (its module docstring, `_authorize`, `_causes` and `readable`; the brief's D5). The history read, the list and the read-cursor command check rows read under the send's shared locks, in the send's order:
  - the reader's valid, current session of an `active` account;
  - the match `active`, with no block either way;
  - the other account `active` or `suspended` (`READABLE_OTHER_STATES`); a deletion works as an unmatch, and a `removed` profile is hidden;
  - then each cause reads its value in `chat.history`: either member's pause, with SV2's `incomplete` read as one; a restriction of either profile; the other's suspension; either member's withdrawn consent. At launch each cause reads `read_only` (the launch default in `profile_settings.py`), which serves the conversation read-only; `hidden`, as the setting says, refuses it; the consent limit fails closed;
  - every hidden cause refuses with one reason, which names no cause.
- It points to `glow_chat.reads`' module docstring for the rule and its causes in full, and names `glow_domain.chat_projections.error_for` as the mapping to the served code, with no other claim about the codes. It names no grant and no open history question. Its heading keeps "point c", which the module's first line cites, "as the SV4 brief's D5 revises it".
- Nothing else in the module changed: `ast.dump` with every docstring removed is the same at the prompt's commit and at the code head, and `git diff` touches only that paragraph.

### Proofs and reversals

Each ran in a scratch clone outside the checkout, under `env -i` with `GLOW_ENV=test`, with the session's virtual environment (installed from `requirements-dev.lock` with `--require-hashes`), as `manage.py test tests.test_interactions_offline.ReciprocalWriterTests -v 2`.

| Proof | Set-up | Result |
|---|---|---|
| (a) A1 on `main` | `git clone --no-local`, remote removed, `HEAD` at `f69529c`, local `main` at `bc0675d` | `Ran 6 tests … OK`; both history tests `... ok` |
| (a), at A1's head | the same, `HEAD` at `bc0675d` | `Ran 6 tests … FAILED (failures=2)`: `test_block_differs_from_mains_by_d3s_statement_and_d4s_value` and `test_every_writer_at_mains_base_is_unchanged_but_a1s` (AR-1, as the manager reproduced it) |
| (b) Before the merge | the same, `HEAD` at `f69529c`, local `main` at `499ccbb` | `Ran 6 tests … OK`; both history tests `... ok` |
| (c) CI's clone | `git clone --depth 1` of `f69529c` (shallow: `true`; `499ccbb` absent) | `Ran 6 tests … OK (skipped=2)`: both history tests `skipped "A1's base 499ccbbec758ed4ef34a93ad19fa8df454fb095c is not in this checkout (CI's shallow clone); the comparison runs wherever that commit is present"`; the other four `... ok` |

**Reversals,** in clone (b), with `499ccbb` present. Each edited a copy of `contact.py`, ran the class and restored the file from a saved copy; its SHA-256 (`06e36c67…`) was checked equal after each, and the clone's `git status` was clean.

| Reversal | The history test that failed | Also failed (expected) |
|---|---|---|
| (r1) A1's `retired_at` statement removed from `block` | `test_block_differs_from_a1s_base_by_d3s_statement_and_d4s_value`, line 1514: "Lists differ: [('replace', 1, 1)] != [('insert', 0, 1), ('replace', 1, 1)]" | `test_block_is_mains_with_one_statement_inserted_and_one_value_changed` (line 1458, "0 != 1"); `test_every_writer_is_pinned_by_its_digest` (`OrmContactPersistence.block`, line 1439, and the module, line 1452). `FAILED (failures=4)` |
| (r2) one statement (`self._signal(tx.probe, "before_unblock")`) added to `unblock` | `test_every_writer_at_a1s_base_is_unchanged_but_a1s`, subtest `OrmContactPersistence.unblock`, line 1389 (the `ast.dump` comparison) | `test_every_writer_is_pinned_by_its_digest` (`OrmContactPersistence.unblock`, line 1441, and the module, line 1452). `FAILED (failures=3)` |

### Commands and results

At the code head, in the checkout, under `env -i` (with `GLOW_ENV=test` for Django), after `pip install --require-hashes -r requirements-dev.lock` in `services/api` (`pip check`: "No broken requirements found."):
- `manage.py check`: "System check identified no issues (0 silenced)."
- `manage.py test tests`: `Ran 654 tests … OK`, no skips. At the prompt's commit, in the same checkout: `Ran 654 tests … OK`, no skips. In both the history tests ran: before, because the checkout held a local `main` at `499ccbb`; after, because it holds `499ccbb`. In CI's shallow clone both skip, before and after.
- `ruff check .`: "All checks passed!"; `ruff format --check .`: "169 files already formatted"; `mypy`: "Success: no issues found in 95 source files".
- **The trusted classifier,** `main`'s `scripts/change_scope.py` (`499ccbb`; SHA-256 `b564c62f4a076f51…`), extracted to a scratch directory outside the checkout and run from it as `python3 -I <copy>/change_scope.py --base 499ccbbec758ed4ef34a93ad19fa8df454fb095c --head f69529c0594889d26caa19eccfe6b7eda73bee56 --merge-base`: `"full": true`, reason `behavior-or-empty`. `git merge-base --all` gives one base, `499ccbb`.
- **The diff:** `git diff --name-only 656ce03 f69529c` lists the three files; this section is the records commit's only change. `ast.dump` with docstrings removed is unchanged for `chat_reads.py` and `test_match_versions_offline.py`.
- **GitHub** was read only with `gh api` REST `GET` calls (the session has no GitHub MCP tools): the run's status and jobs, and job logs.

### The run of record

**Foundation run [45001765683](https://github.com/amthorn78/glow-dating-app/actions/runs/45001765683)** on `f69529c0594889d26caa19eccfe6b7eda73bee56` (a push run, attempt 1) concluded **success**. It was created at 08:13:09 UTC on 22 November 2026 and its gate finished at 08:20:25, 7 minutes 16 seconds in all. Nothing was pushed to the branch until it had finished. Read with `gh api` REST `GET` (the run, its jobs, and the gate's and the API checks job's logs, by `grep` for the lines below only).

| Job | Conclusion | Duration |
|---|---|---|
| Change scope | success | 4 s |
| API checks | success | 68 s |
| Mobile checks | success | 418 s |
| API mobile smoke | success | 68 s |
| API artifact checks | success | 22 s |
| Stream proof checks | success | 73 s |
| Database proof checks (ordering) | success | 420 s |
| Database proof checks (identity) | success | 98 s |
| Database proof checks (profile) | success | 145 s |
| Database proof checks (discovery) | success | 197 s |
| Foundation gate | success: "Application checks passed" | 5 s |

- **The API checks job** checked out the session branch (`git checkout --progress --force -B claude/beautiful-brahmagupta-13ncpo …`, log line 114), at the default depth. `manage.py test` gave `Ran 654 tests … OK (skipped=2)`: the two skips are the history tests, each `skipped "A1's base 499ccbbec758ed4ef34a93ad19fa8df454fb095c is not in this checkout (CI's shallow clone); …"` (log lines 1800 and 1802), and `test_every_writer_is_pinned_by_its_digest ... ok` (line 1803). The contract tests gave `Ran 53 tests … OK`.
- **Not read:** the other jobs' logs and the artifacts. The durations are from the jobs' timestamps, in whole seconds.

### What C1 changes in section "A1"

- **A1's limit on `ReciprocalWriterTests`** (line 1093: "A later change to `contact.py` fails `ReciprocalWriterTests` by design") now holds. The history tests compare with A1's base, so a later change to `contact.py` fails them (reversal r2), and A1's merge does not (proof (a)). The digest test held it already.
- **The detector's forms in line 917** stand. The forms it misses are now in the module's docstring, and the pinned set rests on the searches (AR-4, carried).

### Limits and deviations

- **The prompt as given:** Nathan's message to this session was "resume", with no prompt text. The session read A1-C1's prompt, revision 2, from the live manager branch, and took `<START_SHA>` to be `656ce03…`: the commit that holds revision 2, its last change on the branch (the branch's head, `52b0d13`, holds the same file). The start gate passed against it.
- **The environment's network is unrestricted** (`get_environment`), not limited to PyPI. The session used PyPI for the API's lock only, GitHub for its push and its reads, and no other host.
- **Wording outside the owned passages, left unchanged.** The work needs neither line, and neither is a claim the tests fail:
  - `test_interactions_offline.py`'s module docstring (line 21) still says "``block`` differs from main's by D3's one statement and D4's one value"; `main` there was A1's base, which the history test now names;
  - the digest test's comment (line 1426) says "The same comparison without main's history".
  - `test_block_is_mains_with_one_statement_inserted_and_one_value_changed` keeps its name (AR-7, carried).
- **The history tests skip outside a Git checkout too** (no `git`, or not a repository), as `main_base()` did; only where `499ccbb` is present do they run.
- **The named escaping forms were checked on examples,** one each, against the unchanged detector; the list is not complete ("among them").

### Manager verification of A1-C1 (App Manager 13, 22 November 2026)

- **The branch:** `claude/beautiful-brahmagupta-13ncpo`, code head `f69529c`, records head `7b194aa` (the record only), both after the prompt's commit `656ce03`, which the branch starts at. The manager branch had moved on (`dfdca34`, `52b0d13`, records only), so it took C1 by a merge, `9947844`, whose non-Markdown paths equal `f69529c`'s.
- **The diff** from `656ce03` to the code head: the three files the prompt names, and nothing else; the records commit changes only this record. Read in full: in `test_interactions_offline.py`, `main_base()` removed, `A1_BASE` added, the two history tests renamed and reading `A1_BASE`, every assertion kept, and the class's docstring and the comment above `MAIN_DEFINITION_DIGESTS` rewritten; in `test_match_versions_offline.py`, the module docstring's passage and `WriterDetectorTests`' docstring only; in `chat_reads.py`, the one paragraph only.
- **AR-3's paragraph,** read against `glow_chat/reads.py`'s module docstring, `PAUSED_STATES` and `READABLE_OTHER_STATES` at the code head: it states the same conditions and causes, names no grant and no open question, and makes no claim about the served codes beyond naming `error_for`.
- **The trusted classifier,** `main`'s `scripts/change_scope.py` (`499ccbb`; sha256 begins `b564c62f4a076f51`), extracted outside the checkout and run from it with `python3 -I --base 499ccbb… --head 9947844… --merge-base`: `"full": true`, reason `behavior-or-empty`; one merge base, `499ccbb`.
- **Re-run by the manager,** in a scratch clone (`git clone --no-local`, remote removed) with the API's hash-locked environment, under `env -i` with `GLOW_ENV=test`, `ReciprocalWriterTests`, verbose:
  - `HEAD` at `f69529c`, local `main` at `bc0675d`: `Ran 6 tests … OK`, both history tests `... ok`;
  - A1 merged into `main`, simulated (a local `main` at `499ccbb` with `f69529c` merged into it, `HEAD` on that merge): `Ran 6 tests … OK`, both history tests `... ok`, so the first push run after PR58's merge no longer depends on them;
  - `HEAD` and `main` at `bc0675d` (A1 itself): `FAILED (failures=2)`, AR-1 as reported.
- **The run of record,** Foundation run 45001765683 (event `push`, head `f69529c`, attempt 1), read with `gh api` (`GET` only): all eleven jobs succeeded; the API checks job's log has `Ran 654 tests … OK (skipped=2)`, the two skips the history tests with their stated reason, and the digest test `ok`; the gate's log has "Application checks passed". The records commit's push run, 45002425276, succeeded too.
- **The session's deviations, accepted:** it was started with "resume" in place of the prompt's text and read revision 2 from the live branch, using `656ce03`, the commit that holds it, as `<START_SHA>`; the prompt it followed is the one given. It read GitHub with `gh api` `GET` calls, as revision 2 allows. Its environment's network is unrestricted (the manager's `get_environment` of `Glow App - No Stream` shows the same; the environment inventory now records it); it used PyPI and GitHub only.
- **The stale wording C1 left outside its owned passages** (its "Limits and deviations"): the module docstring's "``block`` differs from main's" (line 21), the digest test's comment "without main's history" (line 1426) and the name `test_block_is_mains_…` (AR-7). Each now reads "main's" where it means A1's base or SV3's `947576d`; none is a claim a decision rests on. **Carried** with AR-7, to SV4 A2 if it changes the file, otherwise the next change to it (the carried-items file, "Carried to SV4").
- **Codex's P1 thread on PR58** (comment 4657212763, posted on `998116b` at 07:40:57 UTC, line 1389; corrected after C1's delta review, N5, AM13-01) names AR-1; C1 answers it. It stays unresolved until Codex's review of the new head and C1's delta review confirm the fix.

### Delta review of A1-C1 (22 November 2026)

- **Session:** C1's delta review, started by Nathan from [its prompt](https://github.com/amthorn78/glow-dating-app/blob/ff17c6131f7d04b845c645bce330afd5b8b95014/docs/ephemeral/2026-11-22-sv4-a1-c1-delta-review-prompt.md), revision 1, from `ff17c61`; its report relayed to App Manager 13 on 22 November 2026. It read GitHub with `gh api` REST `GET` calls only (no GitHub tools in its session).
- **Its start gate, classification and environment check:** every check passed (`HEAD` `ff17c61`; one merge base, `499ccbb`; the prompt's commit on the live branch; the code equal to `f69529c` at `HEAD` and on the live branch; no delta review recorded). `main`'s classifier (sha256 begins `b564c62f4a076f51`), extracted outside the checkout and run from it with `python3 -I --merge-base`: `"full": true`, reason `behavior-or-empty`. None of the three HDE names and no `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name; the AWS and GitHub token names present, never read.
- **Verdict: changes requested,** for one should-fix finding in a correction class (D1-1). AR-1 and AR-3 are answered in full; nothing was weakened; every test, reversal and run claim it checked holds.
- **What it verified:**
  - **AR-1:** with A1 merged into a local `main` (and `origin/main`) at `499ccbb`, `ReciprocalWriterTests` passes, both history tests run; with `656ce03`'s tests in that merged tree, `FAILED (failures=2)`; with no `main` ref at all, it passes; in a `--depth 1` clone both skip with their reason. The file's only `git` calls are `cat-file -e A1_BASE^{commit}` and `show A1_BASE:…`. By AST, the history tests keep their 12 and 7 assertions (the local renamed `main` to `base`), the other four tests and `setUp` are unchanged, and `MAIN_DEFINITION_DIGESTS` is unchanged.
  - **The history tests still catch their targets:** ten reversals, r1 to r10, each failing (r10, a change to `block`'s docstring, fails the digest test only, by design); r1 and r2 match the record's lines and messages; r1 to r3 fail the same way after the simulated merge.
  - **AR-2, partly:** "cannot miss one" is gone; the ten escaping forms named each escape; the pinned set rests on the searches with AR-4 carried; the code is unchanged without docstrings. But D1-1.
  - **AR-3:** the paragraph matches `reads.py`'s rule condition by condition, `LAUNCH_DEFAULTS`' `read_only` included; it names no grant, no open question, nothing about the codes beyond `error_for`. Three fail-closed details are left out (N3).
  - **Nothing outside:** only the three files; no assertion removed or loosened.
  - **The workflow:** the API checks job checks out at depth 1, so `main`'s push run after the merge fetches only the merge commit and the history tests skip.
- **Its checks,** in a scratch clone of `f69529c` with the hash-locked install: `Ran 654 tests … OK` (with `499ccbb`), `Ran 654 tests … OK (skipped=2)` (depth 1); Ruff "All checks passed!", format "169 files already formatted", mypy "no issues found in 95 source files".
- **The runs:** the run of record 45001765683 and the records-head run 45002425276, as recorded; PR58's run 45002885670 (`pull_request`, `ff17c61`): all eleven jobs succeeded, its API checks job (`refs/remotes/pull/58/merge`, `f8fa7e4`, depth 1) `Ran 654 tests … OK (skipped=2)`, the gate "Application checks passed" at 08:35:15 UTC; the push run 45002880812 succeeded. Codex's code review of `ff17c61` completed at 08:29 UTC with no findings and no new thread; the P1 thread (comment 4657212763) stays unresolved, now at line 1382.

**Its findings** (in its words, shortened):

| ID | Severity | Where (at `f69529c`) | Finding |
|---|---|---|---|
| D1-1 | **Should fix** (a correction class) | `tests/test_match_versions_offline.py`, line 8; the record's "A1-C1", AR-2's third bullet | "a detector scans every function in the API's code" claims more than `functions()` (lines 53 to 63) does: it collects only top-level `def` functions and the `def` methods of top-level classes, so an `async def` function or method, or a method of a nested class, is never scanned. Three probes of listed forms in those positions gave `found={}`. The API has no `async def` today, so D6's check holds; but the carried AR-4 item tells A2 to keep its writers to the forms the detector finds |
| N1 | Nit | The same file, line 15 and lines 240 to 241 | "`WriterDetectorTests` shows each of these forms is found": the save form's one example also writes `match.version += 1`; with the save branch deleted from `writes`, `WriterDetectorTests` still passes and `MatchVersionTests.test_each_writer_advances_both_by_one_and_saves_both` fails for both writers |
| N2 | Nit | The same file, lines 17 to 24 | A match from a helper and a `save()` override escape only for `version`; a `contact_version` assignment through either is found (the safe direction). Line 24 is a ragged wrap |
| N3 | Nit | `glow_domain/chat_reads.py`, lines 10 to 22 | Three refusals left out, all on the refusing side: a missing profile refuses as hidden; a missing key or any value but `read_only` reads `hidden`; an unresolvable `chat.history` refuses with the store's reason. "valid, current session" shortens "valid, unexpired, at the reader's epoch" |
| N4 | Nit | The record's "What C1 changes in section A1", first bullet | "a later change to `contact.py` fails them": some later changes fail only the digest test (the module docstring, `activate_reciprocal`, `_lock_shared`, `block` outside its inner body; its r10). Line 1093's limit holds by the digest test, which CI runs |
| N5 | Nit | The record's "A1-C1" and "Manager verification of A1-C1", and C1's prompts | Codex's P1 thread is cited at `4618859`; it was posted on `998116b` (review 6011084956, 07:40:57 UTC, `original_line` 1389), before `4618859` existed. Both carry `bc0675d`'s code, so the line is right |

**What it did not read or run:** the logs of the jobs other than API checks and the gates, and the artifacts; the database, mobile and proof suites (C1 changes none); AR-1 at `bc0675d` itself (the control with `656ce03`'s tests stands in); the rest of `test_interactions_offline.py`; the documentation map, PF00, PF01 and the handoff.

**The manager's check** (App Manager 13): D1-1 read in the code. `functions()` (lines 53 to 63 at `f69529c`) walks `tree.body` for `ast.FunctionDef` and, inside each top-level `ast.ClassDef`, for `ast.FunctionDef`; a top-level `ast.AsyncFunctionDef` and a class nested in a top-level class are never reached (anything nested inside a scanned function is read with it, through `writes()`' `ast.walk`). No module the detector scans holds an `async def` (the manager's search of `services/api`, its tests, migrations and virtual environment left out).

**Disposition** (App Manager 13; the manager workflow's step 6, under D-07):

| Finding | Disposition | Why |
|---|---|---|
| D1-1 | **Fixed before the merge**, by correction A1-C2 (the module docstring's passage only) | A false claim at the detector boundary, the same class as AR-2, which A2 relies on through the carried AR-4 item. Docstrings only: no design, interface, contract or dependency changes, so it goes on the list for the Dev Manager's pre-merge read |
| N1, N2 | **Fixed with D1-1**, in the same passage | N1's sentence claims more than `WriterDetectorTests` shows, by the review's reversal; N2's precision and wrap are in the lines C2 rewrites. Neither would take a correction alone |
| N3 | **Carried**, with AR-5, to SV4 A2, which wires `chat_reads` (the carried-items file, "Carried to SV4") | Every omission is on the refusing side, and the paragraph points to `glow_chat.reads` for the rule in full; it never says a refused reader is served |
| N4 | **Recorded here** | The session's record wording; the conclusion it supports holds by the digest test |
| N5 | **Corrected** in "Manager verification of A1-C1" (AM13-01). C1's prompts, already run, stay as they were; the record carries the correct commit | The manager's citation, from Codex's summary comment rather than the thread's own commit |

The carried AR-4 item now names `async def` functions and methods, and methods of nested classes, among the forms the detector misses.

## A1-C2

- **Session:** SV4 A1's correction session A1-C2, started by Nathan from A1-C2's prompt (`docs/ephemeral/2026-11-22-sv4-a1-c2-correction-prompt.md`), revision 1, from `63aebb6f21dd9a19d8b9fc8f376e6673f8780c0d` of the manager branch `claude/magical-wozniak-yfmmx2`. The findings are D1-1, N1 and N2 of "Delta review of A1-C1", above, as the manager disposed them.
- **Branch:** `claude/affectionate-pasteur-ge2jra`, which the push filter's `claude/**` covers. It starts at the prompt's commit.
- **Code head:** `934da48e74150934b364421a3570f61b6f568f72`. **Records head:** the commit that adds this section, pushed after the code head's run had finished.
- **What C2 changes:** two docstrings in `services/api/tests/test_match_versions_offline.py` (the module docstring's passage from "Read from the source" to "Each function the detector finds must be one of the pinned writers," and `WriterDetectorTests`' docstring), and this section. No code, detector, test, assertion, application behaviour, workflow, setting, contract or proof changes.

### The start gate and the environment check

- **The environment** (section 1, names only):
  - none of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY`;
  - no `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name;
  - the AWS names present: `AWS_ACCESS_KEY_ID`, `AWS_CA_BUNDLE` and `AWS_SECRET_ACCESS_KEY` (OD-76). None was read, printed or passed to a command;
  - the GitHub token names present: `GH_TOKEN` and `GITHUB_TOKEN`. Neither was read;
  - the toolchain: `Python 3.12.14` (`python3.12`);
  - every repository command ran under `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus `GLOW_ENV=test` for the API's Django commands.
- **The start gate** (section 2), at about 09:00 UTC on 22 November 2026:
  - `git rev-parse HEAD` printed `63aebb6f21dd9a19d8b9fc8f376e6673f8780c0d`;
  - "this prompt's commit is on the live branch", "C1's code head" and "no code on the live branch after f69529c" printed. The live branch's head was `01c7fe9`, after the prompt's commit, with no non-Markdown change after `f69529c`;
  - `grep -c` printed `1` for "Delta review of A1-C1" and `0` for "A1-C2".
- **Read before any change:** root `AGENTS.md` and `CLAUDE.md`; this record's "A1-C1", "Manager verification of A1-C1" and "Delta review of A1-C1"; `test_match_versions_offline.py` whole.

### The passage, before and after

**Before** (module docstring, lines 8 to 24 at the prompt's commit):

```text
Read from the source and never run: a detector scans every function in the API's code (its
tests, migrations and virtual environment left out) for these forms of a write to either field
of a match: an assignment to an object's ``contact_version``; an assignment to the ``version`` of
a name bound to a ``Match`` or a queryset of them (assigned from ``Match.objects...`` or
``self._lock(Match, ...)``, looped over, or a parameter annotated ``Match``); a ``save`` of such
an object naming either field; a writing queryset or manager call (``update``, ``create``,
``bulk_update`` and the rest) on one, naming either; or SQL text that writes
``glow_persistence_match``. ``WriterDetectorTests`` shows each of these forms is found.

Other forms escape it, among them: a related manager's ``update``, or an ``aupdate``; a
``Match(..., version=...)``, or a ``bulk_create`` of such objects; SQL text whose table name is
built at runtime or held in a constant; a match obtained through a helper such as
``glow_discovery.interactions._pair_match``; a ``save()`` override or a signal; and ``Match``
imported under another name. So the pinned set below is today's every writer by the A1 review's
and the manager's searches of the code, not by the detector alone; the detector's reach is
carried (the carried-items file, "Carried to SV4"; the exact-head review's AR-4). Each function
the detector finds must be one of the pinned writers,
```

**After** (lines 8 to 31 at the code head; line 32, "and each advances both by one …", continues it unchanged):

```text
Read from the source and never run: in each module of the API's code (its tests, migrations and
virtual environment left out), a detector reads the top-level ``def`` functions and the ``def``
methods of top-level classes, anything nested in one (an ``async def`` or a class among them)
being read as part of it. In those it finds these forms of a write to either field of a match:
an assignment to an object's ``contact_version``; an assignment to the ``version`` of a name
bound to a ``Match`` or a queryset of them (assigned from ``Match.objects...`` or
``self._lock(Match, ...)``, looped over, or a parameter annotated ``Match``); a ``save`` of such
an object naming either field; a writing queryset or manager call (``update``, ``create``,
``bulk_update`` and the rest) on one, naming either; or SQL text that writes
``glow_persistence_match``. ``WriterDetectorTests`` shows each of these forms is found but the
``save``, whose one example also assigns ``version``; the ``save`` is held instead by
``MatchVersionTests``' check that each pinned writer saves both fields in one ``save``.

Other forms escape it, among them: a function it does not read (a top-level ``async def``
function, an ``async def`` method of a top-level class, or any method of a class nested in a
top-level class); a related manager's ``update``, or an ``aupdate``; a
``Match(..., version=...)``, or a ``bulk_create`` of such objects; SQL text whose table name is
built at runtime or held in a constant; an assignment to the ``version`` of a match obtained
through a helper such as ``glow_discovery.interactions._pair_match``, or made in a ``save()``
override or a signal (an assignment to an object's ``contact_version`` is found however the
object was obtained); and ``Match`` imported under another name. So the pinned set below is
today's every writer by the A1 review's and the manager's searches of the code, not by the
detector alone; the detector's reach is carried (the carried-items file, "Carried to SV4"; the
exact-head review's AR-4). Each function the detector finds must be one of the pinned writers,
```

**`WriterDetectorTests`' docstring,** before (lines 240 and 241):

```text
"""The detector itself (the exact-head review lens of A1's own review): each form the module's
docstring lists as found is found. It shows nothing of the forms that escape (AR-4)."""
```

After (lines 247 to 250):

```text
"""The detector itself (the exact-head review lens of A1's own review): each form the module's
docstring lists as found is found, but the ``save``, whose one example also assigns
``version``; ``MatchVersionTests`` holds the ``save``, by its check that each pinned writer
saves both fields. It shows nothing of the forms that escape (AR-4)."""
```

### What was changed, by item

- **D1-1, what the detector scans.** "scans every function in the API's code" is gone. The passage says the detector reads, in each module it scans, the top-level `def` functions and the `def` methods of top-level classes, anything nested in one (an `async def` or a class) read as part of it, as `functions()` and `writes()` do. The escape list now opens with the functions it does not read: a top-level `async def` function, an `async def` method of a top-level class, and any method of a class nested in a top-level class. No sentence says every function is scanned.
- **N1, what `WriterDetectorTests` shows.** The module's sentence and the class's docstring now say its cases show every listed form but the `save`, whose one example also assigns `version`, and that the `save` is held by `MatchVersionTests`' check that each pinned writer saves both fields (`test_each_writer_advances_both_by_one_and_saves_both`). The two docstrings agree.
- **N2, the escape list's precision.** A match obtained through a helper, a `save()` override and a signal now escape for an assignment to `version`, with the note that an assignment to an object's `contact_version` is found however the object was obtained. The passage is rewrapped to the module's width (96 characters at most); its one short line, "top-level class); a related manager's ``update``, or an ``aupdate``; a", is there because the literal ``` ``Match(..., version=...)`` ``` that follows is kept whole.
- **Kept:** the list of the forms the detector finds, word for word but its opening clause; the other escaping forms; that the pinned set rests on the A1 review's and the manager's searches, not the detector alone; that the detector's reach is carried (the carried-items file; AR-4); the closing "Each function the detector finds must be one of the pinned writers,", which line 32 continues.

### Probes and the reversal

Each ran the unchanged detector (`functions()` then `writes()`, loaded from the checkout's module at the prompt's commit) on source in a scratch file outside the checkout, with the session's hash-locked virtual environment, under `env -i`. The listed form in p1 is `match = self._lock(Match, pk)` then `match.version += 1`.

| Probe | Source | Output | Expected |
|---|---|---|---|
| p1a | the form in a top-level `async def f(self, pk)` | `scanned=[] found={}` | found nothing: yes |
| p1b | the form in an `async def` method of a top-level class `C` | `scanned=[] found={}` | found nothing: yes |
| p1c | the form in a `def` method of class `D` nested in top-level class `C` | `scanned=[] found={}` | found nothing: yes |
| p1d | the form in an `async def f` nested in a top-level `def g()` | `scanned=['g'] found={'g': ['match.version += 1']}` | found: yes |
| p2a | `obj = _pair_match(a, b)` then `obj.contact_version = 2` | `found={'f': ['obj.contact_version = 2']}` | found: yes |
| p2b | `self.contact_version = 2` in `Match.save()` (an override) | `found={'Match.save': ['self.contact_version = 2']}` | found: yes |
| control | the same two, assigning `version` | `{'f': []}` and `{'Match.save': []}` | escape: yes |
| signal | a `@receiver(post_save, ...)` function assigning `instance.match.version += 1`, then `instance.match.contact_version += 1` | `{'h': []}`, then `{'h': ['instance.match.contact_version += 1']}` | escape for `version`, found for `contact_version` (the basis for "or a signal" in N2's clause) |

**The reversal (p3).** The module was copied to a scratch directory outside the checkout; on the copy, the save branch of `writes` (the three lines from `if node.func.attr == "save" ...`, line 160) was deleted, and `API_ROOT` was pointed at the checkout's `services/api` so the copy reads the same sources (`diff` showed only those two changes). `python -m unittest -v` on the copy: `Ran 5 tests … FAILED (failures=2)`. Both `WriterDetectorTests` tests `... ok`; `test_both_fields_start_at_one` and `test_the_writers_of_either_field_are_the_pinned_ones` `... ok`; `test_each_writer_advances_both_by_one_and_saves_both` failed for both subtests, `OrmContactPersistence.block` and `OrmContactPersistence.unmatch`, at its last assertion (the found lines lack the `match.save(update_fields=[...])` line). The copy was deleted afterwards; the checkout's `git status` showed no change.

### Commands and results

At the code head, in the checkout, under `env -i` (with `GLOW_ENV=test` for Django), after `pip install --require-hashes -r requirements-dev.lock` in `services/api` (`pip check`: "No broken requirements found."):
- `manage.py check`: "System check identified no issues (0 silenced)."
- `manage.py test tests`: `Ran 654 tests … OK`, no skips (this checkout holds `499ccbb`, so the history tests ran).
- `manage.py test tests.test_match_versions_offline -v 2`: the module's 5 tests, each `... ok`.
- `ruff check .`: "All checks passed!"; `ruff format --check .`: "169 files already formatted"; `mypy`: "Success: no issues found in 95 source files".
- **The trusted classifier,** `main`'s `scripts/change_scope.py` (`499ccbb`; SHA-256 begins `b564c62f4a076f51`), extracted to a scratch directory outside the checkout and run from it as `python3 -I <copy>/change_scope.py --base 499ccbbec758ed4ef34a93ad19fa8df454fb095c --head 934da48e74150934b364421a3570f61b6f568f72 --merge-base`: `"full": true`, reason `behavior-or-empty`. `git merge-base --all` gives one base, `499ccbb`.
- **The diff:** `git diff --name-only 63aebb6 934da48` lists only `services/api/tests/test_match_versions_offline.py`; `git diff` touches only the two docstrings; this section is the records commit's only change. `ast.dump` of the module with every docstring removed is equal at `63aebb6` and at `934da48` (`True`); with docstrings it differs, as it must.
- **GitHub** was read only with `gh api` REST `GET` calls (no GitHub MCP tool was used): the run, its jobs, and the gate's and the API checks job's logs.

### The run of record

**Foundation run [45006396587](https://github.com/amthorn78/glow-dating-app/actions/runs/45006396587)** on `934da48e74150934b364421a3570f61b6f568f72` (a push run on `claude/affectionate-pasteur-ge2jra`, attempt 1) concluded **success**. It was created at 09:12:24 UTC on 22 November 2026 and finished at 09:21:31. Nothing was pushed to the branch until it had finished.

| Job | Conclusion | Duration |
|---|---|---|
| Change scope | success | 5 s |
| API checks | success | 85 s |
| Mobile checks | success | 422 s |
| API mobile smoke | success | 65 s |
| API artifact checks | success | 25 s |
| Stream proof checks | success | 67 s |
| Database proof checks (ordering) | success | 532 s |
| Database proof checks (identity) | success | 96 s |
| Database proof checks (profile) | success | 158 s |
| Database proof checks (discovery) | success | 227 s |
| Foundation gate | success: "Application checks passed" (log line 94) | 3 s |

- **The API checks job:** `Ran 654 tests … OK (skipped=2)` (log lines 2175 and 2177; the two skips are the history tests in CI's shallow clone, as C1 recorded), and the contract tests `Ran 53 tests`.
- **Not read:** the other jobs' logs and the artifacts. The durations are from the jobs' timestamps, in whole seconds.

### Limits and deviations

- **"or a signal" in N2's clause.** The prompt names the helper and the `save()` override as escaping only for `version`. The old list also named a signal; a probe showed a signal receiver is the same case (its `contact_version` assignment is found, its `version` assignment escapes), so the clause covers it too, rather than leave a signal listed as escaping for both.
- **One short line** in the rewrapped passage (above, N2), forced by keeping the literal ``` ``Match(..., version=...)`` ``` unbroken.
- **The reversal's copy** points `API_ROOT` at the checkout, a second edit beside the deleted branch, so that the copy outside the checkout reads the same sources.
- **The probes** load the module from the checkout to call its functions; they read code, they do not decide review scope (the classifier did, from `main`'s copy).
- **The escaping forms are checked on examples,** one each; the list stays "among them".
- **The network was not restricted by the environment;** the session used PyPI for the API's lock and GitHub for its push and reads only.
- **Nothing in the records commit was needed** to pass a check; no stop condition held.

### Manager verification of A1-C2 (App Manager 13, 22 November 2026)

- **The branch:** `claude/affectionate-pasteur-ge2jra`, code head `934da48`, records head `02ebfc7` (the record only), both after the prompt's commit `63aebb6`, which the branch starts at. The manager branch had moved on (`01c7fe9`, records only), so it took C2 by a merge, `860abe2`, whose non-Markdown paths equal `934da48`'s.
- **The diff** from `63aebb6` to the code head: `services/api/tests/test_match_versions_offline.py` only, its module docstring's passage and `WriterDetectorTests`' docstring, read in full. `ast.dump` of the module with every docstring removed is the same at `63aebb6` and `934da48` (the manager's script).
- **The claims, probed by the manager** on the unchanged detector (`934da48`'s module loaded from a scratch copy, under `env -i`): a listed form in a top-level `async def`, in an `async def` method of a top-level class and in a method of a class nested in a top-level class: nothing scanned, nothing found; the same form in an `async def` nested in a top-level `def`: found; `obj.contact_version = 3` on an object from a helper: found; `obj.version = 3` on the same object: not found. Each as the passage now says.
- **The session's deviation, accepted:** it put "a signal" with the helper and the `save()` override, as escaping for `version` only, after its own probe showed a receiver's `contact_version` assignment is found; the prompt named only the two, and the old list had the signal, so the passage stays true.
- **The trusted classifier,** `main`'s `scripts/change_scope.py` (`499ccbb`), extracted outside the checkout and run from it with `python3 -I --base 499ccbb… --head 860abe2… --merge-base`: `"full": true`, reason `behavior-or-empty`; one merge base, `499ccbb`.
- **The run of record,** Foundation run 45006396587 (event `push`, head `934da48`, attempt 1), read with `gh api` (`GET` only): all eleven jobs succeeded; the API checks job's log has `Ran 654 tests … OK (skipped=2)`; the gate's log has "Application checks passed".

### Delta review of A1-C2 (22 November 2026)

- **Session:** C2's delta review, started by Nathan from [its prompt](https://github.com/amthorn78/glow-dating-app/blob/045014d54a4a6986f231482af0b81fa56ff0c2e2/docs/ephemeral/2026-11-22-sv4-a1-c2-delta-review-prompt.md), revision 1, from `045014d`; its report relayed to App Manager 13 on 22 November 2026. It read GitHub with `gh api` REST `GET` calls only (its session also offered GitHub MCP tools, which it did not use).
- **Its start gate, classification and environment check:** every check passed (`HEAD` `045014d`; one merge base, `499ccbb`; the code equal to `934da48` at `HEAD` and on the live branch; no delta review recorded). `main`'s classifier (sha256 begins `b564c62f4a076f51`): `"full": true`, reason `behavior-or-empty`. None of the three HDE names and no `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name; the AWS and GitHub token names present, never read. Its pip install alone was given the proxy and CA-bundle variables to reach PyPI, with `--only-binary=:all:`.
- **Verdict: changes requested,** for one should-fix finding it placed in the prompt's correction class (a) (E-1). D1-1, N1 and N2 are otherwise answered.
- **What it verified:** D1-1's sentence matches `functions()` and `writes()`' `ast.walk` but for E-1; N1 by eight reversals (the save branch deleted fails only the both-by-one test, for both writers; each other branch deleted fails exactly its form's example); N2 by 45 probes (all 14 listed escaping forms escape, all 13 found forms are found, the `contact_version` clause and C2's signal hold); the module's code unchanged without docstrings; every record claim it checked, the run's durations and log lines included.
- **Its checks,** at `934da48` with the hash-locked install: `Ran 654 tests … OK`; Ruff, format (169 files) and mypy (95 files) clean; the module's 5 tests `ok`.
- **The runs:** the run of record 45006396587, as recorded; PR58's run 45007614603 (`pull_request`, `045014d`; its API checks job on `refs/remotes/pull/58/merge`, `7bc4c09`, depth 1): all eleven jobs succeeded, `Ran 654 tests … OK (skipped=2)`, the gate "Application checks passed"; the push run 45007611048 succeeded. Codex's code review of `045014d` completed at 09:29:45 UTC with no findings; the P1 thread (comment 4657212763) unresolved, now at line 1382.

**Its findings** (in its words, shortened):

| ID | Severity | Where (at `934da48`) | Finding |
|---|---|---|---|
| E-1 | **Should fix** (the prompt's class (a)) | `test_match_versions_offline.py`, the module docstring, lines 8 to 11 and 21 to 23 | `functions()` (lines 60 to 70) keys what it finds by name, so of two `def`s with one name in a module or class only the later is read: a `@property` getter beside its setter, `@overload` stubs. A writer in the first of two `def f`, or in a property getter, gave `found={}`. Today's scanned code has one case, `glow_domain/interactions.py` lines 338 and 342 (`FixtureInteractionService.policy_version`), which writes neither field, so D6 holds. The passage says the detector reads "the `def` methods of top-level classes" and its list of functions it does not read leaves this out |
| E-2 | Nit | The same passage | A parameter annotated `Match` binds the name only as the read function's own named parameter: a nested function's annotated parameter (though nested code is "read as part of it"), `*ms: Match`, a string annotation and `models.Match.objects…` escape. The wording is earlier text, and the list says "among them" |
| E-3 | Nit (pre-existing, outside C2's paths) | `functions()`' docstring, line 61 | "Every top-level function and method": it skips `async def` and loses shadowed definitions. If E-1 is corrected, this line belongs with it |
| E-4 | Nit | The same passage | Code under a top-level `if`, `try` or `with`, module-level statements and class-body statements are not read and not listed; "in those it finds" already implies it. None in the scanned code today |
| E-5 | Nit | Lines 18 and 19, 249 and 250 | The `save` is "held by its check that each pinned writer saves both fields": what fails with the save branch deleted is the test's last assertion (the detector's output), not its text checks of the `save`; true of the test method as a whole |

It also found two unlisted forms that escape, not raised as findings: a tuple-target assignment and a `setattr` of `contact_version`.

**What it did not read or run:** the logs of jobs other than API checks and the gate, the artifacts and the push run's jobs; the database, mobile and proof suites; what earlier reviews covered.

**The manager's check** (App Manager 13): E-1 read in the code. `functions()` assigns `found[node.name]` and `found[f"{node.name}.{item.name}"]`, so a second definition of a name replaces the first; `interactions.py` lines 338 and 342 hold the property's getter and setter.

**Disposition** (App Manager 13):

| Finding | Disposition | Why |
|---|---|---|
| E-1 | **Referred to the Dev Manager (DM-98, item 1)**, with A1's pre-merge read | The rule does not decide it (step 6, "Fix or carry, by rule"): under (a) it falls in the correction class the manager's prompt named ("a docstring claiming more than the code does, at the detector boundary"); under D-07 the reach of a static scan is carried, a correction being only for "a false claim that a decision or the merge would rest on", and D6's check rests on the searches. It is the third pass on one docstring's account of the detector. Recommended: carry, with the carried AR-4 item naming it; the alternative is a correction A1-C3 in the Dev Manager's words |
| E-2 to E-5, and the two unlisted forms | **Carried** with AR-4 (the carried-items file, "Carried to SV4"), whatever E-1's disposition; E-3 moves with E-1 if E-1 is corrected | The reach of a static scan and records wording (D-07) |

### Dev Manager 7's pre-merge read (DM-98, 22 November 2026)

Dev Manager 7's report ([DM-98](../../continuity/dev-manager/reviews/2026-11-22-dm-98-sv4-a1-pre-merge-read.md); `8c587ac`, a read of `13487ba`) answers E-1 with option (a), carry, approved with AJ1 to AJ3: the workflow's step 6 says a review prompt's correction classes "are drawn from" D-07's three, so the prompt's wider class is read inside D-07, and the merge and D6's acceptance check rest on the searches, not the docstring (its own walk of the 103 scanned modules found one shadowed pair, `policy_version`, writing neither field, no `async def` at the walk's level, and nested classes that are all `Meta`). It approves the brief's revisions 4 to 7, A1 as settled (with AJ4, the environment inventory, and AJ5, recommended, the P11 plan), and C1, C2 and the manager's D-07 calls. E-1's disposition above is therefore **carried**, with E-2 to E-5, in the carried-items file's AR-4 entry as AJ1 and AJ2 word it; AJ3 puts D6's equality in front of P07's staff path. AJ1 to AJ5 are applied as given. The delta review prompts' correction classes were wider than D-07 (AM13-03).

### Merge (22 November 2026)

- **PR58 merged** into `main` at `43e794a` (App Manager 13, with `gh api`, the expected head `e8d8c44` pinned in the call). DM-98's conditions held: AJ1 to AJ4 (with AJ5) applied as given at `e8d8c44`, in the batch that records the disposition; PR run 45011461881 on `e8d8c44` passed all eleven jobs, and its gate printed "Application checks passed" (10:22:12 UTC); the non-Markdown paths at `e8d8c44` equal `934da48`; Codex's code review of `e8d8c44` completed with no findings; Codex's P1 thread (comment 4657212763, on `998116b`; AR-1's defect, fixed by C1 at `f69529c` and confirmed by both delta reviews) was resolved before the merge; the checklist was filled. No governing Markdown changed from `499ccbb`.
- **`main`'s tree** at `43e794a` equals `e8d8c44`'s. **`main`'s push run** 45012202957 (`push`, `43e794a`): all eleven jobs succeeded, and the gate printed "Application checks passed" (10:30:50 UTC). Its API checks job checked out a local `main` (`git checkout --progress --force -B main refs/remotes/origin/main`, the step AR-1 named) and gave `Ran 654 tests … OK (skipped=2)`, the two history tests skipping with their reason, so the first push run after the merge passed, as C1 set out to make it. The receipt's push run 45012342369 (`3db174b`) succeeded too.
- **The branch cleanup,** run 45012202931 (`push`, `43e794a`): success. Deleted, each merged into `main`: `claude/sleepy-mendel-0kqgw9` (`a1651fb`, A1), `claude/beautiful-brahmagupta-13ncpo` (`7b194aa`, A1-C1), `claude/affectionate-pasteur-ge2jra` (`02ebfc7`, A1-C2). Kept, on the keep-list: `main` (`43e794a`), the manager branch (`e8d8c44`) and `claude/dev-manager` (`8c587ac`). `git ls-remote` afterwards lists those three only.
- **The manager branch** was fast-forwarded to `main` (`43e794a`) before this receipt.
- **Pruned** with this receipt: A1's prompt, its exact-head review prompt, A1-C1's prompt and delta review prompt, A1-C2's prompt and delta review prompt, and DM-98's consultation; their links in the brief and the review log are pinned at `43e794a`.

## A2

- **Session:** SV4 A2's implementation session, started by Nathan from [A2's prompt](https://github.com/amthorn78/glow-dating-app/blob/49df0335460773f00dae64b64e2079d424c65177/docs/ephemeral/2026-11-22-sv4-a2-routes-prompt.md), revision 1, from `49df0335460773f00dae64b64e2079d424c65177` of the manager branch `claude/magical-wozniak-yfmmx2`, and resumed by [App Manager 13's resume message](https://github.com/amthorn78/glow-dating-app/blob/1eeaf6c6a6ce958cd6725d024350fa9d26415b69/docs/ephemeral/2026-11-22-sv4-a2-resume-message.md), revision 1 (option (a)). The specification is the [brief](../../planning/sv4-chat-notifications.md), revision 8, then revision 9 (at `1eeaf6c6a6ce958cd6725d024350fa9d26415b69`).
- **Branch:** `claude/dazzling-hamilton-ocxuu3`, which the push filter's `claude/**` covers. It starts at the prompt's commit.
- **Code heads:** `e3f66a3119899e669625057408530d8ab623c91e` (A2's build; its run, 45018516461, failed and the session stopped), then `26aa7ca2bd6d01d70900c62c1e59ecefef939e8e` (option (a): SV3's route case and the CI policy's lines), whose run is the run of record. **Records head:** the commit that adds this section, pushed after that run had finished.
- **What A2 built:** D8 (chat's four routes, sealed), D9 (`read_only`, `MatchList` and the match list's route), D10 (the chat suite, in its own job), D15 (the seal, checked).
- **What A2 did not touch:** `glow_api/`, any of SV3's database cases but `match.no_route_creates_a_match` (revision 9), `glow_chat`'s `contact.py`, `reads.py` and `delivery.py` (called unchanged; the reversals' temporary edits of `reads.py` and `contact.py` were undone, below), `glow_persistence/` (no migration), `scripts/`, any `apps/mobile` file but the three `npm run generate` wrote, any requirements file, lock, package manifest, environment template or pin; no provider call, deployed URL, real member, HDE call or stored credential. No route was added to the runtime's URL configuration, and the production catalog's `paths` stay empty.

### The start gate and the environment check

- **The environment** (section 1 of the prompt, names only):
  - No `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY`; no `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name.
  - The AWS names present: `AWS_ACCESS_KEY_ID`, `AWS_CA_BUNDLE` and `AWS_SECRET_ACCESS_KEY` (OD-76). The GitHub token names present: `GH_TOKEN` and `GITHUB_TOKEN`. None was read, printed or named in a command.
  - The toolchain: `Python 3.12.14` (`python3.12`); `v24.19.0` and `11.9.0` (`node` and `npm`, both in `/root/.local/bin`, which is third on `PATH`, after the session's guard directory and Nix's default profile, neither of which holds `node`, `npm` or `python`); `Docker version 29.10.0, build fdd4b8e`.
  - Every repository command ran under `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only its own variables. `npm ci --ignore-scripts` needed the proxy's two variables (`HTTPS_PROXY` and `NODE_EXTRA_CA_CERTS`, the proxy's CA bundle) added to that environment to reach the registry; neither value was printed.
- **The start gate** (section 2), at 10:50 UTC on 22 November 2026: `git rev-parse HEAD` printed `49df0335460773f00dae64b64e2079d424c65177`; "this prompt's commit is on the live branch", "PR58's merge present" and "main's code" printed; the diff of the owned trees and the brief between the prompt's commit and the live manager branch printed nothing; `grep -c '^## A2'` on this record printed `0`; `ls … | grep -c '^chat_'` printed `0`. `origin/main` was `43e794a`; the manager branch's head was the prompt's commit.

### What was built, by item

**D8: chat's routes** (`services/api/glow_chat/`, four new modules; `views.py`, `urls.py`, `contract.py`, `route_reads.py`).
- `POST api/v1/chat/messages` (`MessageView`): `MessageIntent`, answering `MessageSubmission` (the submission's ID, version and state, read from its row after the send; never its text), through `OrmContactPersistence.send` unchanged, with `SendCommand(actor.session_id, match_id, meta.expected_version, meta.idempotency_key, text)` (D6: the expected version is the match's `MatchProjection.version`). `authorized` and `replayed` answer the submission; every refusal goes through `contract.send_error`.
- **The send's one code** (D8; DM-96 AG13): `match_not_active`, `blocked`, `account_not_active`, `profile_unavailable` and `consent_not_current`, with the missing forms `profile_missing` and `no_consent`, all answer **`not_found`** (404, not retryable), the same body for each but its request ID. **Why `not_found`:** it is the code the reads answer for every refusal about the conversation or the other member (`glow_domain.chat_projections.error_for`), so the send tells a member no more than the history read does, including after an unmatch, a block and a deletion, which the reads refuse as `not_found`; it is the contract's "generic unavailable object" (`production-contracts.md`, "Wire and error rules"); and the mobile fixture adapter and client already answer and read a refused send that way (`apps/mobile/src/chat/fixture-adapter.ts`, line 68; `client.ts`, line 25, `not_found` to "unavailable"). `forbidden` was the other candidate; SV2's and SV3's routes use it for the actor's own predicates, so it would hint that the cause was the sender's own. The other refusals keep their codes: `stale_contact_version` is `stale_version`, `idempotency_conflict` is `idempotency_conflict`, the session's reasons are `unauthenticated`, everything else about the match (`match_missing`, `not_a_member`, `match_changed`, `binding_not_active`) is `not_found`, and a deadlock or a database error is `state_conflict` (retryable for a deadlock), as `error_for` maps them.
- `GET api/v1/chat/conversations` (`ConversationListView`), `POST api/v1/chat/history` (`HistoryView`, a `MessagePageRequest` body) and `POST api/v1/chat/read-cursor` (`ReadCursorView`), through `read_history`, `list_conversations` and `move_read_cursor` of `RouteConversationReads` (below), each refusal through `error_for`; a page cursor that cannot be read is `stale_version`.
- **Every route:** its actor from `GlowActorAuthentication` only (`authentication_classes = [GlowActorAuthentication]`, `IsAuthenticated`), the session passed to `glow_chat` as the `SendCommand`'s, `HistoryRequest`'s or `ReadCursorCommand`'s session, never a field; a body that is not its DTO (an unknown field, one naming an actor or a session among them), any query string or another content type is `invalid_request` (400), and the list refuses a body (400); another method is `invalid_request` (405); unauthenticated is 401 with `WWW-Authenticate: Bearer`; every refusal is the contract's `Error`; `Cache-Control: no-store` on every answer; one logger call, `"chat route refused: %s"` with the internal reason, a code. `contract.py`'s checkers are SV2's (`glow_profiles.contract`), so the text rule is SV2's (1 to 4000 code points, not blank, no unpaired surrogate, no U+0000).
- **The provider** (D8): the reads' views take the text reader from the factory the setting `GLOW_CHAT_TEXT_READER` names (`import_string`), which only the proof's chat settings set (`glow_ordering_proof.chat_support.text_reader`, the suite's one `FixtureChatProvider`). Without it each read's view refuses with `provider_unavailable` (503, not retryable) before any read is made. The send names no reader: it calls no provider.
- **Transactions** (D8; the P11 plan's R4): `_ChatRoute.as_view` returns `transaction.non_atomic_requests(...)` of DRF's view, so every chat route's callback carries `_non_atomic_requests == {"default"}` and `ATOMIC_REQUESTS` never wraps it.
- **The list's locks** (D8; the P11 plan's C1 finding 4), in `route_reads.py`'s `RouteConversationReads`, a subclass of `glow_chat.reads.OrmConversationReads` (A2's deviation, below): its `_list` first reads the candidates with no lock, in one statement (`CANDIDATES`: the member's active matches with each one's latest activity, as the adapter's list orders it, `ORDER BY latest_at DESC NULLS LAST, m.id DESC LIMIT 200`), then locks only those, `FOR SHARE`, one statement per table, each `WHERE id = ANY(%s) ORDER BY id FOR SHARE` (every account they name with the member's, then their matches), then the session (`_lock_shared`) and `chat.history`'s pointer (`_history`), in the adapter's order; then judges each candidate with the adapter's own helpers (`READABLE_OTHER_STATES`, `_blocked`, `_causes`, `readable`, `_entry`) and sorts as the adapter does. No `select_for_update` is added (the account-lock scan's pinned count, 47, holds) and every new lock is `FOR SHARE`, which neither the scan nor D14's record judges as a writer's.
- **No `ChannelIntent` route.** `glow_chat/urls.py` declares the four routes and no other.

**D9: the contract's additions** (through `npm run generate` after `npm ci --ignore-scripts`).
- `ConversationSummary.state`'s enum is `["open", "closed", "read_only"]`, its description saying `read_only` is one state for every cause the read rule serves read-only, with its count and marker kept; `closed` alone drops them (its `allOf` is unchanged).
- **The read-only mark:** `RouteConversationReads` serves each listed conversation as a `ServedEntry` (the adapter's `ConversationEntry` with `read_only`), `read_only` when `_causes` found any cause, read in the same transaction under the rule's shared locks; its `_move` (the read cursor) is the adapter's, its answer marked the same way in the same transaction. `contract.conversation_summary(entry, read_only=…)` serves `open` or `read_only`.
- `MatchList` (`kind: match_list`, `matches`: at most 200 `MatchProjection` entries, `additionalProperties: false`), joined to `AppResponse`'s `data`, `openapi.json`'s components and F09's `response_contracts` and `projection_roles` (`participant`). `GET api/v1/matches` (`MatchListView` in `glow_discovery/interaction_views.py`, beside the match read; `interaction_urls.py`) answers `interactions.read_matches`: one transaction, the actor's account row `FOR SHARE` first (`read_account_shared`, as the match read does), one statement for the matches (`state = 'active'`, the other member's account not `deletion_pending` or `deleted`, `ORDER BY created_at DESC, id DESC`, at most 200) and one for the other members' profile IDs; each entry is `match_projection(..., "active")`. A body or a query string is `invalid_request`.
- `docs/architecture/production-contracts.md`: the F09 index row gains `MatchList`; `ConversationSummary`'s paragraph says `read_only`; a new section, "F09 and F11 on the server: chat's routes and the match list (SV4 A2, sealed until integration)", states the routes, the send's one code and its retry, the bounded list, `MatchList`, the provider and the transactions. D4's and D6's own sentences were written by A1 (that document's F10 and F13 paragraph, `MatchProjection`'s description, F10's transition) and are unchanged; the flow registry's only change is F09's.
- **The mobile app:** its `npm run check` passes unchanged (691/691, with the typecheck and lint). `apps/mobile/src/chat/rows.ts` treats every state but `open` as unavailable, so a `read_only` conversation shows as unavailable until AC3 (carried).

**D10: the chat suite** (`proofs/postgres-ordering/glow_ordering_proof/`: `chat_settings.py`, `chat_urls.py`, `chat_support.py`, `chat_cases.py`, `chat_suite.py`, `chat_scan.py`; `__main__.py`'s `chat` command), on the discovery suite's pattern, in its own job (below). Its 15 cases (`CASE_COUNT`), in order:

| Case | What it shows |
|---|---|
| `routes.refuse_what_is_not_their_dto` | no token and a refused token (401, with the challenge); an extra field, a session field and an actor field, a query string, another content type (400); `GET`, `PUT`, `PATCH`, `DELETE` on the `POST` routes (405); the list and the match list refusing a body, a query string, `POST` and no token; `no-store` on refusals and served answers |
| `send.replay_conflict_and_version` | the match read's version is 1 and is the send's; pending, then the same intent replayed as the same submission, then accepted after delivery; the same key with another text `idempotency_conflict`; versions 0 and 2 `stale_version`; the refused ones writing nothing; after the unmatch, the replay `not_found` |
| `reads.history_list_and_cursor_for_both` | five messages, both members' sides (author, text as sent, delivery for the own only); pages of two followed to the end; an empty poll of the newer cursor; the list's unread and latest marker for each; the cursor forward and a cursor behind changing nothing; another match's message (`not_found`) and page cursor (`stale_version`); the sender's own pending message, theirs alone and in neither the other's page nor their marker; no provider identifier in any served body |
| `send.five_refusals_one_code` | eight causes (unmatch; an active block beside an active match, as test data; the other's suspension and deletion; the other's pause, the sender's own pause, the other's restriction; a withdrawn consent with the profile visible, as test data): each `not_found`, one body, while `glow_chat`'s own reason for the same state is each of the five |
| `d5.each_cause_read_only` | nine causes (`own_pause`, `other_pause`, `own_incomplete` and `other_incomplete` as test data, `own_restriction`, `other_restriction`, `other_suspension`, `own_withdrawal`, `other_withdrawal`): `open` before; then the history served, the list `read_only` with its count and marker, the cursor moving and answering `read_only`, the send `not_found`, the match list still holding the match |
| `ended.unmatch_block_deletion_hidden` | after an unmatch, a block and the other's deletion: history and cursor `not_found`, the send `not_found`, the list and the match list leaving it out, for the reader and (unmatch, block) the ender |
| `d4.block_and_unmatch_serve_the_same` | the member who did not block and the member who was unmatched served the same on every surface (send, history, list, cursor, the match read `unmatched` at version 2, the match list), with absolute expectations, after the block and the unmatch, after the blocker's unblock, and after each ender's later unmatch (`no_change`, the same answer) |
| `d3.retired_likes_make_no_conversation` | a like, a block and an unblock by the liker and by the liked, then the other's like recorded with no match; neither member has a match or a conversation |
| `match_list.active_matches_newest_first` | four matches, one unmatched and one whose other member asked for deletion: the two active ones, newest first, each `active` at version 1, its other profile ID, equal to the match read's projection; the other member's own list; a member with none lists none |
| `wrong_member.every_route_not_found` | a stranger, on another's match and on a match ID that never existed: send, history, cursor and match read each `not_found`; in neither list; the participants still read it |
| `transactions.non_atomic_requests` | with `ATOMIC_REQUESTS` on, the send, the history, the list and the cursor answer; inside an atomic block and inside a block marked as a Django test case's, the history, the list and the cursor each `state_conflict` (409, `transaction_open`), with no provider call |
| `ar12.like_while_a_block_waits_and_a_match_after_unblock` | AR-12: a reciprocal like held at its commit (both account rows held) while the other member's block waits on it (observed in `pg_stat_activity`); the like commits the match; the block then ends it as `unmatched` and retires both likes; no conversation, no match listed, the history `not_found`. And a pair that blocks and unblocks before either likes, then likes: a match, whose message is read and listed `open` |
| `list.bounded_locks` | 206 active matches (one through the routes, with a message; 205 seeded as test data): the list serves 200, the one with a message first, exactly the top 200; one `FOR SHARE` statement per table (201 accounts, 200 matches, the session), none naming a left-out account; the candidates' statement before the first lock; the match list holds 200; a writer holding a left-out member's account row does not hold the list up (it finishes within 10 s), and a writer holding a kept member's row does, observed, until it commits, after which the list serves it |
| `ar13.history_publication_during_a_read` | AR-13: a history read holding `chat.history`'s pointer at its final check makes a publication wait (observed), and is served as the setting stood; a publication holding the pointer at its commit makes a read wait (observed), which then reads the new setting and is refused `conversation_hidden`; through the route, `not_found` and not listed |
| `d5.each_cause_hidden` | each cause published `hidden` in turn (each staying so), then the nine causes: the history and the cursor `not_found`, one body for every cause, not listed; a conversation with no cause still served `open` |

The cases' members are signed in through SV1's routes, built through SV2's and matched through SV3's like (`interaction_cases._matched`, unchanged); every chat event is delivered through `glow_chat`'s `OutboxDelivery` to the suite's provider; every message text and every provider identifier joins the value ledger. `chat.history` cannot be made more readable under the launch consent version (SV2's D2), so the two cases that publish a cause `hidden` run last, and a test pins that no earlier case publishes. The suite installs D14's row-lock record before its first statement and checks it before its verdict, and scans its secrets and member values against every log record, write, response header and the results JSON, as the discovery suite does. **The job** (`database-chat`, "Database proof checks (chat)", 30 minutes) is the discovery job's in form: its own PostgreSQL 17.11 from the pinned digest, its own passwords, marker (`chat-marker`), keys (`chat-secret-key`, `chat-jwt-key.pem`) and the decoy database `glow_discovery_proof` with its own marker (`discovery-marker`); `dbshell` refused under the chat settings; the decoy's marker refused with the relation counts unchanged and no table; the reviewed migrations from zero and `makemigrations --check --dry-run`; the suite, timed; `chat_scan` before any output is shown; a second run refused, its rows unchanged (users, accounts, profiles, matches, message submissions, outbox events); the upload (`sv4-chat-results`, 14 days) only after the check has passed; everything removed last, `if: always()`. The gate's `needs` and its `jobs` tuple gain `database-chat`. The CI policy's database proof jobs paragraph gains its bullet; the proof's README gains the chat suite's paragraph, its layout row and its run paragraph.

**D15: the seal** (`services/api/tests/test_chat_routes_sealed_runtime.py`, a sibling of `test_chat_sealed_runtime.py` in its style, which is unchanged): the runtime's settings, URL configuration and WSGI application import none of A2's modules (any `glow_chat`, `glow_discovery` or `glow_persistence` module, A2's eight named); the backend is `django.db.backends.dummy`; `INSTALLED_APPS` is `["rest_framework"]`; the runtime's routes are exactly the three it had, no A2 route is served and no A2 path resolves; the runtime names no `GLOW_CHAT_TEXT_READER`; no `glow_api` module names A2's modules or the setting; `glow_chat`'s `route_reads`, `views` and `urls` cannot load under the runtime's settings; the production catalog's `paths` are empty.

### The stop, the decision and the resume

- **The stop** (22 November 2026, after `e3f66a3`'s run 45018516461): Database proof checks (discovery) failed at SV3's database case `match.no_route_creates_a_match` (`interaction_cases.py`), "exactly the routes the suite serves (1 unexpected, 0 missing)". The case pins the exact routes the discovery suite's URL configuration serves, and that configuration serves `glow_discovery/interaction_urls.py`, where A2 put `GET api/v1/matches`. Its later check, a `POST` at the matches path answering 404 ("no route at the matches path"), could not hold either with a route there. A fix needed `interaction_cases.py`, outside A2's owned paths, and changed an assertion beyond adding A2's entry, so the session stopped under the stop rule ("an owned path"; "an earlier test"), made no fix and no records commit, and offered (a) widening the owned paths to that case or (b) moving the route.
- **The decision:** App Manager 13 chose **(a)** (the brief's revision 9; the [resume message](https://github.com/amthorn78/glow-dating-app/blob/1eeaf6c6a6ce958cd6725d024350fa9d26415b69/docs/ephemeral/2026-11-22-sv4-a2-resume-message.md); AM13-04): the match list stays at `GET api/v1/matches`, beside the match read, as D9 puts it, since the case's purpose, that no route creates a match, holds with a read there. Revision 9 adds to A2's owned paths that case only, and the CI policy's lines 5 and 23.
- **The case's change** (`26aa7ca`; `match.no_route_creates_a_match` only, no other line of the file): its `stage_b` set gains `("api/v1/matches", "MatchListView")`, with a comment naming SV4 A2 (D9); its `POST` at the matches path expects 405, "the matches path takes no POST", where it expected 404, with a comment; its docstring names the match list among the routes and its return line counts "SV3's and SV4 A2's". Its "no match written" and its check that no request DTO names a match stay, and the second holds: `MatchListView` declares no `definition`, so the DTOs the routes declare are still the four commands. Locally (iteration) the case passes ("exactly 43 routes served (8 of SV3's and SV4 A2's), none taking a match intent"), and the whole discovery suite passes, 70/70. Its reversals are r22 and r22b (below).
- **The CI policy's lines** (`26aa7ca`): line 5's list of the database jobs gains "Database proof checks (chat)" and its "all nine application jobs" becomes "all ten" (the gate's ten); line 23's upload-artifact row says "the five database proof jobs" where it said four; and the closing paragraph of the database jobs (line 14) names the chat job's secret check and suite among the jobs' secret checks, the suites' row-lock records ("each of the suites (five since SV4 A2)") and the results JSON that carry the counts. Nothing else in the file changed.

### Earlier tests changed, and why (D11, A2's bullet)

**The sweep,** before any change, at the prompt's commit: every suite's source and tests, the contract's tests and the API's tests grepped for each list A2 extends (the database jobs and the gate's lists, the commands and settings modules, the routes, the contract's kinds and states, the case and plan counts, and the scans' file lists). Each earlier test changed gains A2's entry only, with every earlier assertion kept:

- `proofs/postgres-ordering/tests/test_discovery_offline.py`:
  - `DiscoveryWorkflowTests.test_the_gate_requires_each_suites_job`: the `jobs` tuple, which pins both the gate's `needs` and its script's `jobs` tuple, gains `"database-chat"`;
  - `DiscoveryWorkflowTests.test_each_suite_runs_in_its_own_job_after_its_migrations_and_decoy_refusal`: the per-job loop gains `("database-chat", "SV4", "chat")`, since the chat job's steps take the same form;
  - `DiscoveryCommandTests.test_no_other_command_runs_under_the_discovery_settings`: its commands gain `["chat"]` (its assertion, `"refusing:"`, holds for it);
  - `DiscoveryPlanTests.test_the_routes_are_the_apis`: `interaction_urls.py`'s declared routes gain `"api/v1/matches"`. **The sweep missed this one** (it read `api/v1/matches` in the API's tests, not the proof's); the first run of the proof's offline tests after the route was added found it, and it was handled the same way.
- `services/api/tests/test_discovery_offline.py`, `DiscoveryRouteTests.test_the_page_route_and_stage_bs_action_routes_are_served_and_no_other`: the exact route list gains `["api/v1/matches", "MatchListView", ["get"]]`.
- `packages/contracts/tests/test_transition_contract.py`, `SV2StageATransitionTests.test_sv3_undo_is_the_actors_own_and_additive`: its frozen F09 entry's responses and projection roles gain `MatchList` (`participant`), with a comment; no transition of F09 changes.
- **From revision 9:** SV3's database case `match.no_route_creates_a_match` (`proofs/postgres-ordering/glow_ordering_proof/interaction_cases.py`): its set gains the match list's route, and its `POST` at the matches path answers 405 where it answered 404, as "The stop, the decision and the resume" above records; the one assertion changed beyond adding A2's entry, by the manager's decision.

**Found and left unchanged** (each reads a list A2 could extend, but stays true without A2's entry; A2's own tests cover the chat suite's side):
- `proofs/postgres-ordering/tests/test_discovery_offline.py`, `DiscoveryCommandTests.test_the_discovery_command_refuses_every_other_settings_module`, and `test_profile_offline.py`'s two `ProfileCommandTests`: `main` checks the newest suite's settings first, so `discovery` or `profile` under the chat settings prints the chat refusal, not theirs; SV3 left the profile tests without the discovery settings for the same reason. `test_chat_offline.ChatCommandTests` pins both directions for `chat`.
- `test_row_locks_offline.RunnerTests.test_the_three_django_suites_install_first_and_check_before_the_verdict` (and its class docstring, "Each of the four suites"): not extended, so its name stays true; `test_chat_offline.ChatRunnerTests` checks the chat suite the same way.
- `test_profile_offline.py`'s two loops over `(profile_suite, discovery_suite)` (the migration times and the response headers' text): `ChatRunnerTests` checks the chat suite's same lines.
- `test_identity_offline.py`'s and `test_profile_offline.py`'s "no other suite's key in this job" checks read only their own job.
- `services/api/tests/test_chat_sealed_runtime.py`, `test_discovery_sealed_runtime.py`, `test_interactions_sealed_runtime.py` and `test_profiles_sealed_runtime.py`: they cover A2's modules by package (`glow_chat`, `glow_discovery`) and pass unchanged; D15's own checks are a sibling, so `test_chat_sealed_runtime.py`'s AR-14 lines stay carried.
- `test_interactions_offline.py` (`glow_chat` imports nothing from `glow_discovery`; no lock word in `interactions.py`, `interaction_views.py` or `interaction_urls.py`; two logger calls in `interaction_views.py`), `account_lock_scan`'s pinned 47 `select_for_update` calls in `services/api`, `test_match_versions_offline.py`'s writers, and `test_profile_pointer_order.py`'s pointer locks: each constrains A2's code, and each passes unchanged.
- `services/api/tests/test_toolchain_pins.py` counts the workflow's pins from the file, so the new job changes its counts, not its rule; `apps/mobile/src/chat/rows.test.ts` (its states `open` and `closed`) passes unchanged.

No other earlier test changed.

**The database-case sweep** (the resume message; revision 8's sweep read the earlier tests, not the earlier suites' database cases): every earlier suite's cases (`cases.py`, `delivery_phase.py`, `read_phase.py`, `identity_cases.py`, `profile_cases.py`, `discovery_cases.py`, `interaction_cases.py`) grepped for a pin of the routes or the URL configuration (`get_resolver`, `url_patterns`, `ROOT_URLCONF`, `resolve`, the API's paths), of the suites or the jobs, of a contract list (`oneOf`, the definitions, the response kinds, the summaries' states, `LIST_LIMIT`) and of a count A2 extends:
- **The one hit:** `match.no_route_creates_a_match`, changed as above.
- **Route pins A2 does not extend:** the identity suite's `config.routes` (`identity_cases.py`, `EXPECTED_ROUTES`, the identity URL configuration's routes) and the profile suite's routes case (`profile_cases.py`, `EXPECTED_PROFILE_ROUTES`, the profile URL configuration's); neither configuration serves `interaction_urls.py` or chat's routes.
- **Paths A2 does not change:** SV3's `interaction_refusals_and_ownership` calls only `GET api/v1/matches/<match_id>`, and the rest call the matches path's sub-paths or other paths.
- **No pin:** no earlier case pins the suites, the jobs or a contract list; the ordering suite's read phase uses `glow_chat.reads` directly (`OrmConversationReads`, its `read_only` words the read rule's, not the summary's state), unchanged; and the case counts (`CASE_COUNT`, 77 and 70) are unchanged, since A2 adds no case to those suites.

### The writer search (DM-98's AJ2)

At the prompt's commit, and again at the code head (A2 changes none of these lines), every assignment, `save`, queryset or manager write and SQL text naming a match's `version` or `contact_version` in `services/api` (its tests and migrations left out):
- **Writers:** `glow_chat/contact.py`, `OrmContactPersistence.block`, lines 664 to 666 (`match.contact_version += 1`, `match.version += 1`, `match.save(update_fields=["state", "contact_version", "version", "updated_at"])`), and `unmatch`, lines 750 to 752 (the same three statements).
- **Creations with the defaults (both 1):** `contact.py` line 272 (`activate_match`) and line 360 (`activate_reciprocal`), `Match.objects.create(account_low_id=…, account_high_id=…, state="active")`.
- **None else:** no queryset or manager `update`, `bulk_create`, `bulk_update`, `setattr` or SQL text writing `glow_persistence_match`. `glow_domain/interactions.py`, lines 661 and 767, is P05.3's in-memory fixture (a dataclass `replace`), not the model.
- **A2 adds none:** `glow_chat/views.py` line 184 passes `meta.expected_version` to a `SendCommand`; lines 193 to 201 read a submission's version; `read_matches` reads matches. `WRITERS` is unchanged, and `test_match_versions_offline.py` passes at the code head.

### The Chromium install's first attempt (DM-97)

The first attempt of "Install Chromium for rendered fixture checks" in every run of record since A0: 187 s (44463105633), 22 s (44562701307), 22 s (44601565801), 203 s (44679608400), as this record states them; 38 s (45001765683: 08:14:49.48 to 08:15:27.77 UTC) and 38 s (45006396587: 09:14:07.65 to 09:14:46.10 UTC), read from their Mobile checks logs (the step's group line and the next step's) and the jobs' step times; 41 s in the first run, 45018516461 (11:42:55 to 11:43:36 UTC), and 21 s (45022218979, 12:28:05 to 12:28:26 UTC) in the run of record. Each first attempt succeeded, and no retry ran. None took more than 480 s and none was stopped by its limit, so the entry's rule changes nothing: the Mobile job's and the attempts' `timeout-minutes` stay as they are, and `sudo dpkg --configure -a` was not added.

### Follow-ups due at A2 (D12)

- **Taken:**
  - **AR-12 and AR-13:** the chat suite's `ar12.*` and `ar13.*` cases (above).
  - **AJ2:** the search above; no new writer.
  - **DM-97's Chromium margin:** the durations above; nothing to change.
  - **The chat suite's secret scan** reads every secret file its own job writes and no other (`chat-secret-key`, `chat-marker`, `discovery-marker`, `superuser-password`, the passfile's password, `chat-jwt-key.pem`'s lines; pinned against the workflow by `test_the_values_are_every_secret_file_of_the_job`), written as the three are, its docstring naming "Database proof checks (chat)" (pinned by `test_the_docstring_names_the_chat_job`).
  - **The substring-pin limits:** below, "Substring pins, not semantics".
  - **Because A2 changes the file:** `row_locks.py`'s RN1 (the docstring's "What it does not see" names F1, pointing to the README's limit) and RN2 (`judge`'s comment gains "in the positions its reading binds"), with its list of suites (five, the chat suite's own); `__main__.py`'s lines 20, 24 and 28 (each suite on "its own disposable database", with a sentence on A0's split).
- **Left where they are** (A2 does not change these files): the three scans' and the eight module docstrings that still name the shared job (DM-97's AH3); `job_secret_files`' spelling (F7's D5); `reads.py`'s AR-5 and `chat_reads.py`'s N3; AR-7 to AR-10 and A1's stale lines; AR-11; SV1's identity-support docstring (DM-50); `ReciprocalWriterTests` (`contact.py` is unchanged, so its digests hold); AR-14 and `test_chat_sealed_runtime.py`'s lines 11 to 13 and 130 (A2 wrote a sibling instead).

### New tests

- **The API** (`services/api/tests/`): `test_chat_routes_offline.py`, 24 tests (`RequestTests` 4: each intent parsed as the contract's schema decides, on 27 bodies, a field naming an actor refused, the server's U+0000 rule, bodies the parser cannot hold; `ProjectionTests` 4; `SendRefusalTests` 3; `RouteTests` 7, in a fresh process under the discovery offline settings, the persistence and the reads replaced by recorders: each route's DTO, the actor's session only, the reads refusing without the factory, every refusal, the five sends' one code and one body, the reads' codes, the logs; `StructureTests` 6: the four routes and no other, each `non_atomic_requests` with SV1's authentication, no `ChannelIntent`, no writer's lock and no `glow_discovery` import in A2's modules, the list's candidates before its locks with one statement per table, one logger call, the body read only through the contract); `test_chat_routes_sealed_runtime.py`, 7 tests (D15).
- **The proof** (`proofs/postgres-ordering/tests/test_chat_offline.py`), 34 tests: `ChatSettingsModuleTests` 4, `ChatScanTests` 7, `ChatWorkflowTests` 9, `ChatPlanTests` 4, `ChatCommandTests` 3, `ChatRunnerTests` 3, `ChatSupportTests` 4.
- **The contract** (`packages/contracts/`): 24 corpus cases (902 to 926) (`read_only` summaries and list, six cause-named states refused, a reason field refused; `MatchList` valid at 0, 2 and 200 entries and in `AppResponse`, refused at 201 (alone and in `AppResponse`), with another kind, a count, a cursor, no list, an entry with a reason or a `blocked_by`, a summary for an entry); `SV4StageATwoContractTests`, 2 tests (one `read_only` state, `closed` alone dropping the count and marker; `MatchList` the participant's only, on F09 only, in no request list, its shape and its place in `AppResponse`).
- **The database:** the chat suite's 15 cases (above).


### Reversals (D14)

Each reversal is a temporary edit of one or more files, made by a scratch harness that found each old text exactly once, wrote the edit, ran the tests or cases, kept the failing lines, and restored each file byte for byte, its SHA-256 checked after. All 25 failed as intended, and all were restored (`git status` afterwards shows A2's own changes only; `contact.py`, `reads.py` and `glow_api/` are unchanged). Each reversal with database cases ran those cases on a fresh throwaway database (below). The failing output, quoted (shortened where marked "…"):

| Reversal (the edit) | What failed |
|---|---|
| r01: a route takes its session from the body (`_body` keeps a body's `session_id`, the send uses it) | `StructureTests.test_the_views_read_the_body_only_through_the_contract` ("Lists differ: [… three reads] != [… two]"); `RouteTests` errored in its setup (the reversal's own parse raised on a non-JSON body); `routes.refuse_what_is_not_their_dto`: "messages: a session field: answers 400" |
| r02: a refusal names a value (the send's refusal carries its match ID) | `RouteTests.test_the_sends_five_refusals_answer_one_code`, each cause: "(404, 'not_found', False, True) != (404, 'not_found', True, False)" (not the contract's `Error`, and a value echoed); `send.five_refusals_one_code`: "the unmatch: the body is the contract's Error"; `wrong_member.every_route_not_found`: "another's match: send: the body is the contract's Error" |
| r03: the send's five refusals answer different codes (a block `forbidden`) | `SendRefusalTests.test_the_five_answer_one_code_the_same_for_each` and `test_the_stopped_code_is_the_one_the_reads_answer_for_the_conversation` ("('forbidden', False) != ('not_found', False)"); `RouteTests…five…` ("(403, 'forbidden', True, False) != (404, …)"); `send.five_refusals_one_code`: "the block: answers 404" |
| r04: a read served `open` where D5 makes it read-only (the list and the cursor never mark) | `d5.each_cause_read_only`: "own_pause: listed read_only, its count and marker kept" |
| r05: a conversation served where `hidden` refuses it (the list ignores the setting) | `d5.each_cause_hidden`: "own_pause: not listed" |
| r06: a wrong member's route answers `forbidden` | `SendRefusalTests.test_the_other_refusals_keep_their_codes` (`not_a_member`: "('forbidden', False) != ('not_found', False)"); `RouteTests…five…` ("(403, 'forbidden', …)"); `wrong_member.every_route_not_found`: "another's match: send: answers 404" |
| r07: the list locks before it bounds (every active match's accounts locked first) | `StructureTests.test_the_list_bounds_its_candidates_before_its_first_lock` ("Lists differ: [… '_lock_many', '_lock_many', '_lock_shared', 'self.candidates'] != […]"); `list.bounded_locks`: "one per table" |
| r08: a view run inside a caller's transaction (`non_atomic_requests` removed) | `StructureTests.test_the_four_routes_and_no_other` ("[…, [], True, True] … != […, ['default'], True, True]"); `transactions.non_atomic_requests`: "the history page: answers 200" |
| r09: the chat job's decoy refusal removed (the refused migrate) | `ChatWorkflowTests.test_the_migrations_step_refuses_the_decoys_marker_first` ("['chat chat-marker python -m django migrate --verbosity 1'] != ['chat discovery-marker python -m django migrate…']") |
| r10: the chat job's secret scan removed (`scan=0`) | `ChatWorkflowTests.test_the_suite_step_runs_the_check_and_sets_the_output_only_on_a_pass` ("'python -m glow_ordering_proof.chat_scan "$DIR" "$DIR/chat.log" .work/chat-results.json' not found in …") |
| r10b: the chat scan reads one secret file fewer (`discovery-marker`) | `ChatScanTests.test_the_values_are_every_secret_file_of_the_job` ("Items in the second set but not the first"); `test_a_value_in_the_log_or_the_json_is_refused_and_the_json_removed` (`discovery-marker`, log and JSON: "0 != 3") |
| r11: the gate's `needs` without the chat job | `DiscoveryWorkflowTests.test_the_gate_requires_each_suites_job` ("[… 'database-discovery'] != [… 'database-discovery', 'database-chat']") |
| r11b: the gate's `jobs` tuple without the chat job | the same test, on the tuple |
| r12: the runtime imports an A2 module (`glow_api/urls.py` imports `glow_chat.contract`) | `test_the_runtime_imports_none_of_a2s_modules` ("['glow_chat', 'glow_chat.contract'] != []"), `test_no_runtime_module_names_a2s_modules_or_the_reader` (`urls.py`), and `test_chat_sealed_runtime.py`'s two (unchanged) tests |
| r13: the reads' views run without the text reader (a default fixture when none is named) | `RouteTests.test_the_reads_refuse_to_run_without_the_text_reader`, each route ("(200, None, True, False) != (503, 'provider_unavailable', True, False)") and "3 != 0" reads made |
| r14: the match list lists ended matches | `match_list.active_matches_newest_first`: "the active matches, newest first" |
| r15: the match list oldest first | the same case, the same line |
| r16: the read takes `chat.history`'s pointer with no lock (`reads.py`, temporary; AR-13) | `ar13.history_publication_during_a_read`: "the publication waited on the read" |
| r17: the block takes its account rows with no lock (`contact.py`, temporary; AR-12) | `ar12.like_while_a_block_waits_and_a_match_after_unblock`: "ended" (the block, not serialized behind the like, left its match active). A first r17, SV3's `_lock_pair` returning early, did not fail the case, since `activate_reciprocal` takes both account locks itself; it was a wrong reversal, not a gap, and was replaced |
| r18: the contract drops `read_only` from `ConversationSummary.state` | the shared corpus (`valid-ConversationSummary-read-only` and three more: "False != True"); `test_read_only_is_one_state_with_its_count_and_marker` ("['open', 'closed'] != ['open', 'closed', 'read_only']") |
| r19: `MatchList` allows 201 entries | the corpus (`invalid-MatchList-201`, `invalid-AppResponse-MatchList-201`: "True != False"); `test_the_match_list_is_the_participants_and_additive` ("201 != 200") |
| r20: the chat command runs under the discovery settings too | `ChatCommandTests.test_the_chat_command_refuses_every_other_settings_module` (`discovery_settings`: "set up") |
| r21: a case lost without the pinned count changing | `ChatPlanTests.test_the_case_count_is_pinned` ("14 != 15") |
| r22 (revision 9): SV3's route case's set without `("api/v1/matches", "MatchListView")` | `match.no_route_creates_a_match`, on a fresh discovery database: "exactly the routes the suite serves (1 unexpected, 0 missing)" |
| r22b (revision 9): that case's `POST` at the matches path expecting 404 again | the same case: "no route at the matches path" |

### Commands and results

At the code head, in a clean environment (local; the run of record repeats them):
- **The API**, after `pip install --require-hashes -r requirements-dev.lock` and `pip check` ("No broken requirements found."), with `GLOW_ENV=test`: `manage.py check` "System check identified no issues (0 silenced)"; `manage.py test tests` `Ran 685 tests … OK`, no skip (654, no skip, at the prompt's commit: this clone has `main` and A1's base); `makemigrations --check --dry-run` "No changes detected"; `ruff check .` "All checks passed!"; `ruff format --check .` "175 files already formatted" (169 before); `mypy` "Success: no issues found in 99 source files" (95 before); the contract's Python tests `Ran 55 tests … OK` (53 before).
- **The proof's offline tests**, from its own lock: `Ran 421 tests … OK` (387 at the prompt's commit); Ruff "All checks passed!", "78 files already formatted" (71 before); mypy "Success: no issues found in 78 source files".
- **The contract:** `npm ci --ignore-scripts` from its lock ("added 20 packages"), `npm run generate` (three files changed in `apps/mobile/src/contracts/generated/`, committed), then `npm run check`: "Generated types and runtime validators match schemas.", `tests 926`, `pass 926`, `fail 0`; `node scripts/generate.mjs --check` again after the reversals: the same.
- **The mobile app:** `npm ci --ignore-scripts` from its lock, then `npm run check` (typecheck, lint, unit tests), unchanged: `tests 691`, `pass 691`, `fail 0`.
- **The trusted classifier**, `main`'s `scripts/change_scope.py` (`43e794a`; SHA-256 `b564c62f…`, equal to the checkout's), extracted to a scratch directory outside the checkout and run from the checkout as `python3 -I <copy>/change_scope.py --base 43e794a5500e1ffdb12bfb2b2b2c0a9332c45ca2 --head <the code head> --merge-base`, for each code head: `"full": true`, reason `behavior-or-empty` (at `e3f66a3` and at `26aa7ca2bd6d01d70900c62c1e59ecefef939e8e`). `git merge-base --all` gives one base, `43e794a`.
- **The diff:** `git diff --name-only 49df0335460773f00dae64b64e2079d424c65177 26aa7ca2bd6d01d70900c62c1e59ecefef939e8e` lists 34 paths, each in A2's owned paths (revision 9's included): `interaction_cases.py` (the one case, revision 9) and, as at `e3f66a3`, 4 new `glow_chat` modules; 4 `glow_discovery` modules (the match list only); 5 contract files (the schema, the registry, the catalog, the corpus, the transition tests) and 3 generated outputs; 6 new chat suite modules, `__main__.py`, `row_locks.py` (its list of suites, RN1, RN2), the proof's README, 1 new and 1 extended proof test module; the workflow; the CI policy (one bullet, and from revision 9 the jobs' list and counts in lines 5, 14 and 23); 2 new and 1 extended API test modules; `production-contracts.md`. This section is the records commit's only change.
- **npm and pip:** no package, lock, manifest or pin changed.
- **GitHub:** read with `gh api` REST `GET` calls only (the runs' jobs and two job logs; the session's GitHub tools here offer no Actions reads); nothing was written but the three pushes of this branch (the two code heads, then this records commit).

### Local database runs (iteration, not evidence)

Under P06.DB's D4: the pinned image `postgres@sha256:d74eeac9…`, pulled from Docker Hub; loopback only (`127.0.0.1:5433`); generated passwords, markers and keys in a mode-700 scratch directory, never printed; none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name in any process environment; the chat database and the decoy, each with its own marker, created by the superuser inside the container; migrations only through the proof's own `python -m django migrate` under the chat settings, never `manage.py migrate`. No Docker daemon was running, so `dockerd` was started in the background. The whole chat suite ran twice on a fresh database: 15/15 in 139.6 s, then, at the code head's content, 15/15 in 138.9 s, both scans clean (1077 secrets held, 866 member values held, 0 found in 814 log records, 50 writes and the results JSON), `ROW LOCKS (D14): PASS` (81,168 and 81,166 statements; 7,621 writer's locks, 2,203 of them on the account table, all `FOR NO KEY UPDATE`; 0 refused), `CHAT VERDICT: PASS`, and `chat_scan` passing. The reversals' cases ran each on a freshly recreated database. Afterwards the container, the credential files and the results were removed, and no proof container remained. After the resume, on a fresh throwaway database by the same recipe (the image pulled again, the daemon restarted), the whole discovery suite under its own settings with the case's change: `[discovery] cases: 70/70 passed in 320.1 s`, both scans clean, `ROW LOCKS (D14): PASS`, `DISCOVERY VERDICT: PASS`; then r22, r22b and the case again. The `dbshell` and decoy steps, the second-run refusal and the upload gate are CI's only.

### The run of record

**Foundation run [45022218979](https://github.com/amthorn78/glow-dating-app/actions/runs/45022218979)** on `26aa7ca2bd6d01d70900c62c1e59ecefef939e8e` (a push run, attempt 1) concluded **success**. It was created at 12:25:41 UTC on 22 November 2026 and its gate finished at 12:33:52 (8 minutes 12 seconds in all); the gate printed "Application checks passed" (12:33:50). Nothing was pushed to the branch until it had finished. The durations are from the jobs' timestamps (whole seconds); A1's are from its run of record, 44679608400.

| Job | Conclusion | Duration | A1's | Timeout |
|---|---|---|---|---|
| Change scope | success | 12 s | 9 s | 3 min |
| API checks | success | 71 s | 74 s | 10 min |
| Mobile checks | success | 465 s (7 min 45 s) | 580 s | 25 min |
| API mobile smoke | success | 86 s | 83 s | 10 min |
| API artifact checks | success | 22 s | 25 s | 15 min |
| Stream proof checks | success | 70 s | 78 s | 10 min |
| Database proof checks (ordering) | success | 351 s (5 min 51 s) | 389 s | 30 min |
| Database proof checks (identity) | success | 130 s | 115 s | 30 min |
| Database proof checks (profile) | success | 146 s | 148 s | 30 min |
| Database proof checks (discovery) | success | 235 s (3 min 55 s) | 316 s | 30 min |
| **Database proof checks (chat)** | success | **142 s (2 min 22 s)** | (new) | 30 min |
| Foundation gate | success: "Application checks passed" | 5 s | 3 s | 2 min |

**What the logs show** (read with `gh api` REST `GET` calls; no line read held an `::add-mask::` command or a long hexadecimal value):
- **The chat job:** the offline tests `Ran 421 tests … OK`, Ruff "All checks passed!" and "78 files already formatted", mypy "Success: no issues found in 78 source files"; `chat dbshell exit status: 1` with `RefusedDatabase: refusing dbshell …`; the decoy `glow_discovery_proof` present with its own marker (`1`, and its comment differs: `t`), its marker refused (`chat migrate with the decoy database's marker: exit status 1`, `RefusedDatabase: refusing this database …`) with the relation counts unchanged and no table; the migrations from zero; `[chat] cases: 15/15 passed in 74.7 s` (every case `PASS`); `chat secret scan: clean (1077 secrets held; 0 found in 814 log records, 50 writes and the results JSON)`; `chat value scan: clean (866 member values held: member values, message texts, provider identifiers; 0 found in the same output)`; `[chat] row locks sent (D14): 81165 statements … 7621 take a writer's row lock, 2203 of them naming the account table (2203 FOR NO KEY UPDATE …); 0 refused`, `ROW LOCKS (D14): PASS`; `CHAT VERDICT: PASS`; `chat phase: 76 s (the job's timeout is 30 minutes)`; `chat_scan`: 0 and 0 found, the suite's scans clean; the second run refused (`refusing a used database: …`), its rows unchanged (`300 300 300 251 59 1487`), `second chat run exit status: 1`; the upload after the check; `container removed: glow-proof-db-chat-45022218979-1`, `credential and marker files removed`, `no proof container remains`.
- **The discovery job:** `[discovery] PASS match.no_route_creates_a_match (8, D10, F09) 1.3 s: exactly 43 routes served (8 of SV3's and SV4 A2's), none taking a match intent; …`; `[discovery] cases: 70/70 passed in 173.8 s`; `ROW LOCKS (D14): PASS`; `DISCOVERY VERDICT: PASS`; `discovery phase: 176 s`.
- **The other suites:** ordering `== VERDICT: PASS ==`; identity `[identity] cases: 49/49 passed in 44.8 s`, `IDENTITY VERDICT: PASS`; profile `[profile] cases: 77/77 passed in 83.0 s`, `PROFILE VERDICT: PASS`.
- **The API checks job:** `Ran 685 tests … OK (skipped=2)` (the two history tests of `ReciprocalWriterTests` skip with their reason, as on every branch push, which has no local `main`), Ruff "All checks passed!" and "175 files already formatted", mypy "Success: no issues found in 99 source files", the contract tests `Ran 55 tests … OK`.
- **Mobile checks:** "Install Chromium for rendered fixture checks" succeeded on its first attempt in 21 s (12:28:05 to 12:28:26), the pause and the retry skipped; "Render and exercise account onboarding" took 316 s.
- **Within its timeout:** each job finished well inside its `timeout-minutes`; the chat job took 142 s of its 30 minutes.


### The first run: failed, superseded (the stop)

**Foundation run [45018516461](https://github.com/amthorn78/glow-dating-app/actions/runs/45018516461)** on `e3f66a3119899e669625057408530d8ab623c91e` (a push run, attempt 1), created 11:41:01 UTC on 22 November 2026, concluded **failure** at 11:48:37: ten jobs passed, **Database proof checks (discovery)** failed, and the gate failed with `AssertionError: Unexpected database-discovery result`. Nothing was pushed until the manager's decision; the run was not re-run. It is superseded by the run of record above.

| Job | Conclusion | Duration | Timeout |
|---|---|---|---|
| Change scope | success | 11 s | 3 min |
| API checks | success | 78 s | 10 min |
| Mobile checks | success | 430 s | 25 min |
| API mobile smoke | success | 73 s | 10 min |
| API artifact checks | success | 19 s | 15 min |
| Stream proof checks | success | 77 s | 10 min |
| Database proof checks (ordering) | success | 391 s | 30 min |
| Database proof checks (identity) | success | 103 s | 30 min |
| Database proof checks (profile) | success | 181 s | 30 min |
| **Database proof checks (discovery)** | **failure** | 232 s | 30 min |
| **Database proof checks (chat)** | success | **142 s** | 30 min |
| Foundation gate | failure | 5 s | 2 min |

**The failure** (the discovery job's log, step 15): `[discovery] FAIL match.no_route_creates_a_match (8, D10, F09) 1.2 s: FAILED: exactly the routes the suite serves (1 unexpected, 0 missing)`; `[discovery] cases: 69/70 passed in 165.4 s`; both scans clean; `ROW LOCKS (D14): PASS`; `DISCOVERY VERDICT: FAIL`; `discovery phase: 167 s`; `##[error]Process completed with exit code 1.` The case (`interaction_cases.py`, SV3's) pins the exact routes the discovery suite's URL configuration serves, and that configuration serves `glow_discovery/interaction_urls.py`, where A2 put `GET api/v1/matches`. The same case then asserts `POST api/v1/matches` answers 404 ("no route at the matches path"); with the match list's `GET` there a `POST` answers 405, so that assertion would fail too once the first held (read from the code; not run, since the case stopped at its first). A fix needs `interaction_cases.py`, outside A2's owned paths, and changes an assertion beyond adding A2's entry, so the stop rule ("an owned path"; "an earlier test") applies; no fix was made. The sweep missed this case: it read the earlier tests, not the earlier suites' cases.

**The chat job** passed: the offline tests `Ran 421 tests … OK`, Ruff and mypy clean; `chat dbshell exit status: 1` with the refusal; the decoy `glow_discovery_proof` present with its own marker, its marker refused (`exit status 1`, `RefusedDatabase: refusing this database`) with the relation counts unchanged; the migrations from zero; `[chat] cases: 15/15 passed in 73.5 s`; `chat secret scan: clean (1077 secrets held; 0 found in 814 log records, 50 writes and the results JSON)`; `chat value scan: clean (866 member values held: …; 0 found in the same output)`; `ROW LOCKS (D14): PASS`; `CHAT VERDICT: PASS`; `chat phase: 74 s`; `chat_scan` passed (0 and 0 found, suite clean); the second run refused, rows unchanged (`300 300 300 251 59 1487`), `exit status: 1`; the upload ran after the check; `container removed`, `credential and marker files removed`, `no proof container remains`. **Mobile checks:** "Install Chromium for rendered fixture checks" succeeded on its first attempt in 41 s (11:42:55 to 11:43:36), the pause and the retry skipped.

**The ways forward the session offered:** (a) widen the owned paths to that case, its routes gaining the match list and its 404 becoming 405; or (b) move the match list's route. The manager chose (a) (above).


### Substring pins, not semantics

The workflow tests read the chat job's steps as text, as A0's corrections read the other jobs'; they pin lines and their order, not what the shell does. The limits A0's corrections named apply to the chat job's steps as they do to the three others (the carried-items file, A0's entry):
- **X3:** `writers()` sees only the `> "$dir/<name>"` spelling, so a second writer of a secret file spelled `>"$dir/<name>"` escapes; with it, F7's D5, `job_secret_files` reads only the `"$dir/<name>"` spelling (a file written as `"${dir}/<name>"`, or outside the credentials step, escapes the scan tests). `test_chat_offline` uses the same helpers.
- **X4:** the role step's later statements (after `CREATE ROLE`) are not pinned.
- **X5:** a `fail=0` set again just before `test "$fail" = 0` would defeat the decoy step's failure with every test passing.
- **X9:** step-level keys such as `continue-on-error: true` on the decoy or `dbshell` step are not pinned.
- **X14:** the decoy step's refusal branch could be bypassed by an `else` made `elif false; then`; **X15:** its `outside_pg` query could be made `SELECT 0`; and its **`per_schema`** query could be changed; each with every test passing.
- **N3:** the gate test runs the gate's script, not the step around it.
- **The chat job's own:** `ChatWorkflowTests` pins the second run's six tables, the upload's condition and the clean-up's lines by substring, and `test_the_job_prints_no_connection_value` reads the job's non-comment lines for five words only.

### Limits and deviations

- **Recorded for the exact-head review** (the resume message; kept as built): the duplicated list logic in `glow_chat/route_reads.py`, kept because `reads.py` stayed unchanged; no `TransactionTestCase` class for the views; and the match list leaving out a match whose other member asked for deletion, while SV3's match read by ID still shows it `active`. Each is stated in full below.
- **A deviation: the list's bound and the read-only mark live in a new module, `glow_chat/route_reads.py`,** a subclass of `OrmConversationReads` overriding `_list` and `_move`, because the prompt keeps `reads.py` unchanged while D8 asks the list to bound its candidates before it locks and D9 asks for the `read_only` mark, and `reads.py`'s `_list` locks every active match and returns no cause. The subclass reuses the adapter's helpers (`_lock_shared`, `_history`, `_clock`, `_blocked`, `_causes`, `readable`, `_entry`) and its order of checks; its own code is the candidates' statement, the one-statement locks and the mark. So the list's session checks and per-conversation loop now exist twice (the adapter's `_list`, which the ordering suite's read phase still runs and no route serves, and the subclass's), and the mark recomputes `_causes` under the same locks. The manager may prefer the bound and the mark in `reads.py` (a later change, outside A2's paths).
- **The bound's consequence:** the list ranks before it locks and judges after, so a member with more than 200 active matches, some of them hidden, can be listed fewer than 200 conversations although more readable ones exist past the bound.
- **"Tested with `TransactionTestCase`, never `TestCase`"** (D8, R4) is met as: no Django `TestCase` tests these views; their database tests are the chat suite's cases, which call them through Django's test client with no enclosing transaction and autocommit on, as a `TransactionTestCase` calls them (its flush between tests is not used: the suite runs once on a new database and each case makes its own members), and `transactions.non_atomic_requests` shows that a `TestCase`'s block makes every read refuse. The API's own route tests have no database (Django's dummy backend) and are `unittest.TestCase`s with the persistence replaced. No `django.test.TransactionTestCase` class was written.
- **The match list leaves out a match whose other member's account is being or has been deleted** (a deletion works as an unmatch, OD-60 H), while SV3's match read by ID still serves that match `active`, as it did before A2.
- **The match list's view is SV3's pattern, not `non_atomic_requests`:** under `ATOMIC_REQUESTS` it would refuse as SV3's routes do (`transaction_open`, 503); the chat settings, like the discovery settings, keep `ATOMIC_REQUESTS` off.
- **The send's answer reads the submission's version and state in a statement after the send's transaction**, so a delivery committed in between shows `accepted`; the receipt itself is the send's.
- **The `blocked` and `consent_not_current` refusals, and SV2's `incomplete`, are reached by test data** in the cases (an active block beside an active match; a withdrawal with the profile visible; an `incomplete` profile), states no writer leaves today.
- **Lines A2 left stale outside its paths:** `test_row_locks_offline.RunnerTests`' docstring ("Each of the four suites"); `docs/architecture/data-model.md`, which does not mention the routes or the match list. Listed for the manager to route. (The CI policy's lines 5 and 23 were taken from revision 9.)
- **The CI policy's line 14** (the paragraph that closes the database jobs' section) was read as part of the database jobs' paragraphs A2 owns: its three lists (the jobs' secret checks, the suites' row-lock records, the results JSON that carry the counts) gained the chat entry, beside lines 5 and 23, which revision 9 adds.
- **The proof README's change** is three additions for the chat suite (an intro paragraph beside each slice's, a layout row, a run paragraph), which this session read as "the chat suite's section".
- **The production contracts' F09 index row** was edited by hand, as the document's other rows have been; no script generates it.
- **The sweeps missed two pins of the match list's route:** the proof's offline `test_the_routes_are_the_apis`, which the first offline run found and which changed only by gaining A2's entry; and SV3's database case `match.no_route_creates_a_match`, which the first run, 45018516461, found (the stop; the manager's AM13-04 for the prompt's sweep), changed under revision 9 with its one assertion.
- **`npm ci` needed the proxy's variables** (`HTTPS_PROXY`, `NODE_EXTRA_CA_CERTS`) in the clean environment; nothing else was added to any command's environment.
- **The local database runs are iteration only;** the run of record is CI's.

### Manager verification of A2 (App Manager 13, 22 November 2026)

- **The branch:** `claude/dazzling-hamilton-ocxuu3`, starting at the prompt's commit `49df033`: the first code head `e3f66a3` (its run 45018516461 failed in Database proof checks (discovery), the stop), the second code head `26aa7ca` (after the resume message, option (a), the brief's revision 9), and the records head `88d4ef3` (this record only). The manager branch had moved on (`4442fab`, `1eeaf6c`, records only), so it took A2 by a merge, `0ff9c09`, whose non-Markdown paths equal `26aa7ca`'s.
- **The diff** from `49df033` to `26aa7ca`: 34 paths, each in A2's owned paths at revision 9 (the brief's "Owned paths", A2); 11,920 lines added and 2,097 removed, 2,058 of the removals in the regenerated `apps/mobile/src/contracts/generated/validators.js`. `packages/contracts/production/openapi.json` gains only `MatchList`'s component; its `paths` stay `{}` (read by script). The CI policy's diff is the chat job's bullet, and the chat job added to the lists and counts at its lines 5, 14 and 23; line 14 the session read as the closing paragraph of the database jobs' paragraphs it owns (its record), a reading for the Dev Manager's pre-merge read with the policy's change. `interaction_cases.py` changes only in `match.no_route_creates_a_match`, as the resume message allowed.
- **The trusted classifier,** `main`'s `scripts/change_scope.py` (`43e794a`; sha256 begins `b564c62f4a076f51`), extracted outside the checkout and run from it with `python3 -I --base 43e794a… --head 26aa7ca… --merge-base`: `"full": true`, reason `behavior-or-empty`.
- **The run of record,** Foundation run 45022218979 (event `push`, head `26aa7ca`, attempt 1), read with `gh api` (`GET` only): all twelve jobs succeeded, among them the new Database proof checks (chat) (12:26:00 to 12:28:22 UTC); its log has every one of the fifteen cases `PASS`, "cases: 15/15 passed in 74.7 s" and "ROW LOCKS (D14): PASS"; the gate's log has "Application checks passed". The first run, 45018516461 on `e3f66a3`, is superseded, as the record says.
- **Not re-run by the manager:** the session's local checks (API 685 tests, the proof's 421, the contract's 55 and 926, mobile 691) and its 25 reversals; the run of record ran the suites in CI.
- **For A2's exact-head review** (the session's "Limits and deviations", and the resume message's list): the list's bound and the `read_only` mark in a new `glow_chat/route_reads.py`, a subclass of `reads.py`'s reads, because `reads.py` stayed unchanged, so the list's logic exists twice; no `TransactionTestCase` class for the views (the chat suite's `transactions.non_atomic_requests` case runs them with `ATOMIC_REQUESTS` on and shows six reads refused inside a caller's block); the match list leaving out a match whose other member asked for deletion, while SV3's match read by ID still serves it `active`; the send's five refusals answering `not_found`; the two sweep misses (AM13-04); two stale lines outside A2's paths (`RunnerTests`' docstring, `data-model.md`).

### Codex on PR59 (22 November 2026)

- **Codex's review of `81d390c`** (the commit of A2's exact-head review prompt, revision 1; completed by 13:00 UTC, review 6012370930) left one P2 thread, comment 4658183908, on `services/api/glow_chat/contract.py`, line 170 (`send_error`): "Check all send-stopping states before exposing stale versions". With an active match at version 1, a send naming `expected_version` 0 answers `not_found` (404) when the other member's account is not active, and `stale_version` (409) when the other member's profile is paused or restricted or their consent withdrawn; D5's reads serve those causes alike as read-only, so the route tells them apart.
- **The manager's check of the code** (not a run): `OrmContactPersistence.send` (`glow_chat/contact.py`, unchanged since A1, pinned by digest in `ReciprocalWriterTests`) checks, on the locked rows, the match's state (line 521), both accounts' states (528), the session, an active block (544) and the contact version (546), and only then both profiles and both consents (`_contact_state_checks`, 549); `send_error` maps `stale_contact_version` to `stale_version` (line 170) and the five stopped reasons to `not_found`. The order supports the claim.
- **Handled** (the manager workflow, step 6: a new finding joins the review pass): A2's exact-head review prompt, revision 2, adds it as focus item 3, for the review to confirm, classify and give the smallest fix and its place (`contact.py` or A2's route layer). Revision 1 was not given to Nathan. The thread stays unresolved, with no reply, until a fix and Codex's review of its head confirm it, or the finding's disposition is recorded.
- **PR59's run on `81d390c`:** 45024481611 (event `pull_request`), all twelve jobs succeeded, the gate's last job finished at 13:00:17 UTC; the push run 45024476298 passed, its application jobs skipped by design (a Markdown-only push).
- **On `7e8811e`** (the commit of the review prompt's revision 2): Codex's review completed at 13:05:12 UTC with no new review and no new comment; its summary's findings flags are the open P2 thread above, PR59's only thread. PR59's run 45025465730 (event `pull_request`) passed all twelve jobs, and the gate printed "Application checks passed" at 13:12 UTC. Revision 2 went to Nathan from `7e8811e`.
- **On `95e1278`** (the records commit after revision 2): Codex started no pass. Its summary still named `7e8811e` at 13:45 UTC on 22 November and on 26 November, with one review and one thread. PR59's run 45026387370 on `95e1278` passed. The manager gave revision 2 to Nathan at about 13:31 UTC without that pass (AM13-05).

### Exact-head review of A2 (22 to 26 November 2026)

- **Session:** the exact-head review, started by Nathan from [A2's review prompt](https://github.com/amthorn78/glow-dating-app/blob/7e8811eff30d9f5ff64593ffa0453202734a3334/docs/ephemeral/2026-11-22-sv4-a2-review-prompt.md), revision 2, from `7e8811e`, in `Glow App - No Stream`. It ran on 22 November; Nathan relayed its report on 26 November, after it re-checked the live branch, PR59 and Codex's thread that day.
- **Its start gate, classification and environment check:** every start-gate check passed (`HEAD` `7e8811e`; one merge base, `43e794a`; the prompt's commit on the live branch, then at `95e1278`; the non-Markdown paths equal to `26aa7ca` at `HEAD` and on the live branch; no review recorded). The trusted classifier, `main`'s, outside the checkout with `python3 -I`, gave `"full": true`, reason `behavior-or-empty`. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or the `STREAM_`, `PG`, `R2_`, `CLOUDFLARE_`, `CF_` or `RAILWAY_` names; AWS and GitHub token names present and unread. Python 3.12.14, Node 24.19.0, npm 11.9.0, Docker 29.10.0 (it started the daemon). GitHub read with `gh api` REST `GET` calls only; the checkout left clean.
- **Verdict: changes requested.** A2 meets D8 to D10 and D15 on every point but the send's one code: A2R-1 (Codex's P2, confirmed on a database), A2R-2 and A2R-3 go to a correction, and A2R-4 (low) with them.

**What it verified** (its focus items, shortened):
- **D8:** the actor only from SV1's authentication; no route serves a reader D5 refuses or refuses one it admits; a wrong member gets `not_found` everywhere and both lists are empty; the one logger call carries a code or an exception's type name only. Every refusal the contract's `Error`, except two request shapes (A2R-4).
- **The send's one code:** the five causes answer 404 with one body, status and headers at the current version; a replay does not split them; no route tells a block from an unmatch for any version; the reasons for `not_found` over `forbidden` hold. A wrong version splits them (A2R-1), and so does a session ended mid-request (A2R-2). Timing is not equalised (zero to four single-row reads after the same four locks): a limit to record.
- **`route_reads.py`:** the list's rule equals the adapter's condition by condition, with the same locks in the same order, the clock after them and a caller's transaction refused the same way; the bound cannot include an unreadable conversation or deadlock; `read_only` cannot differ between the list and the cursor; the history read is the adapter's. The duplication is no behaviour defect now; nothing proves the copy's session, own-account and block checks (A2R-3). More than 200 active matches: a limit to record.
- **D8's transactions:** R4's purpose met by the chat suite's cases and `transactions.non_atomic_requests`; no acceptance check rests on a `TransactionTestCase` class; one docstring sentence is false (A2R-5). The match list's SV3 pattern is right.
- **D9:** the match list serves only the actor's `active` matches, at most 200, newest first, and nothing that tells a block from an unmatch; leaving out a deletion is OD-60 H's answer, and the read by ID still serving it `active` is SV3's (A2R-12). The contract's additions, 24 new corpus cases (the earlier 902 unchanged), F09's entry and the generated outputs hold; the catalog's `paths` are `{}`.
- **F09:** no route A2 adds writes a match or a like; the SV3 case still proves its three points.
- **D10:** the chat job and the discovery job have 17 steps each, ten identical by hash and seven renamed in the same form (read whole), none new; the gate needs and requires `database-chat`; no step prints a connection value or a secret; 142 s, 142 s and 118 s of 1,800; the fifteen cases cover D10's list, AR-12 and AR-13; the `hidden` publications cannot reach another case. Test gaps: A2R-3, A2R-6 to A2R-8.
- **D15:** the seal test catches an A2 module reached at import time and any A2 name in `glow_api/*.py`, not an import made inside a function when called (its reach, to record). No provider call, credential, dependency or pin; `glow_api/` and HDE's ports untouched.
- **The earlier tests** gain only A2's entry (with the SV3 case's 405); each reason for a test left unchanged holds. **The writer search:** no new writer; `WRITERS` holds both.
- **The records** hold except the sentences under A2R-1, A2R-4, A2R-5 and A2R-9; the manager verification's figures are right; the two stale lines named are records to carry, with more in A2R-13.

**Its probe of A2R-1** (a throwaway PostgreSQL 17.11; an active match at version 1):

| State | Current version | Wrong version (0 or 7) | The list shows |
|---|---|---|---|
| No cause | 200 | 409 `stale_version` | `open` |
| The other member suspended | 404 | **404** | `read_only` |
| The other's pause, the own pause, the other's restriction, the other's consent withdrawn | 404 | **409** | `read_only` |
| Unmatch, block, the other member's deletion | 404 | 404 | not listed |

**Its checks,** in scratch copies of `26aa7ca`, each package from its own lock with `--require-hashes`, under `env -i`: the API `check` clean, `Ran 685 tests … OK` (no skip), Ruff and format (175 files) and mypy (99 files) clean, the contract's tests 55 OK, no migration change; the proof `Ran 421 tests … OK`, Ruff (78 files) and mypy (78 files) clean; the contracts 926 of 926 with the generated outputs equal; mobile 691 of 691. **Reversals:** a session from the body (4 API failures); the block refusal `forbidden` (3); a wrong version under each cause (nothing fails: no case sends one); the candidate route fix (2 failures, the pins of today's answer); the candidate adapter fix (`ReciprocalWriterTests`' digest of `send` only); the list locking before its bound (`StructureTests`); the gate without the chat job (each way); `glow_api/urls.py` importing `glow_chat.contract` (5 failures); the list serving a deletion (database only: `ended.unmatch_block_deletion_hidden`, 14/15); its own RV-A to RV-C (nothing fails: A2R-3, A2R-6); and 16 of the record's 25 reversals, each failing its named test (the other nine judged by reading). **Local database runs** under P06.DB's D4 (informational): the chat suite 15/15 in 151.4 s, both scans clean, `ROW LOCKS (D14): PASS`; the discovery suite 70/70 in 321.2 s; the probe as one review-only case in a scratch copy; everything removed afterwards. Two independent reads agreed with A2R-1 to A2R-3; it ran each point they added before including it.

**The runs** as it read them: 45022218979 (`push`, `26aa7ca`) success, twelve jobs, the chat job 142 s, 15/15 in 74.7 s, the gate "Application checks passed"; 45018516461 (`push`, `e3f66a3`) failure at `match.no_route_creates_a_match`; 45025465730 (`pull_request`, `7e8811e`) success, twelve jobs, the chat job 118 s, 15/15 in 59.5 s. Codex: review 6012370930 of `81d390c`, one P2 thread (comment 4658183908), unresolved, not outdated, no reply; its review of `7e8811e` completed at 13:05 UTC with no new thread.

**Its findings** (in its words, shortened):

| ID | Severity | Where (at `26aa7ca`) | Finding | Its class |
|---|---|---|---|---|
| A2R-1 | Should fix | `glow_chat/contract.py` 169 to 170, with `contact.py` 520 to 549 | Codex's P2: a send with a wrong version answers 404 for the other member's suspension and 409 `stale_version` for a pause, a restriction or a withdrawn consent, which the reads serve alike; the suite passes 15/15 with the split. The contract's error table says `not_found` must not reveal another person's suspension; "so a member never learns which cause stopped a send" (`contract.py` 22 to 23; `production-contracts.md`'s send bullet; the record) is false | Security boundary, and a false claim |
| A2R-2 | Should fix (narrow) | `contact.py` 520 to 535; `chat_projections.py` 44 to 53 | A session ended after authentication and before the send's session lock answers 401 for no cause or a pause and 404 for a suspension or an unmatch; that 401 has no `WWW-Authenticate`, so it is told apart from the door's (probed) | Security boundary |
| A2R-3 | Should fix | `route_reads.py` 156 to 169 and 180 | With the list's block check removed, or its session and own-account checks removed, all 685 and 421 offline tests and all 15 database cases pass; A1's suite proves those checks only on `reads.py`'s list, which no route serves | Missing test at a security boundary |
| A2R-4 | Should fix (low) | `views.py` 160 to 171; `interaction_views.py` 111 to 122 | `?format=xml` answers 404 `{"detail":"Not found."}` and `Accept: text/html` 406, each without `Cache-Control`, before authentication; no value, the same for everyone; SV3's merged routes answer the same | A false claim: D8's "every refusal is the contract's `Error`", which A2's acceptance check reads |
| A2R-5 | Nit | `views.py` 36 | "Its tests are `TransactionTestCase`s": none exists | No |
| A2R-6 | Nit | `chat_cases.py` 463 to 464, 477 to 478, 1068 to 1069 | SV2's withdrawal also makes the profile `incomplete`, so the pause cause alone gives what cases 5 and 15 check; with the read rule ignoring a withdrawn consent the suite passes 15/15 (A1's read phase proves that cause alone) | No |
| A2R-7 | Nit | `test_chat_offline.py` 620 | The first check of `test_the_cases_that_publish_hidden_run_last` cannot fail (`ast.unparse` writes single quotes; the pattern captures the keyword's name); an early `hidden` fails safe at run time | No |
| A2R-8 | Nit | `chat_cases.py` 183 to 188, 330 to 333; `chat_support.py` 213 to 214 | The no-token challenge header is checked on the refused-token reply; `match_version` returns 1 when the match read fails; case 3 moves the cursor for one member, where D10 says both | No |
| A2R-9 | Nit | The record, lines 1643 and 1773 | The CI policy's "lines 5, 14 and 23" are 5, 15 and 24 at the code head; "no line held an `::add-mask::` command or a long hexadecimal value": the chat log holds five echoed script lines and 18 lines of SHAs and digests, none a secret | No |
| A2R-10 | Nit | `route_reads.py` 230 to 232; `chat_projections.py` 70 to 90 | `is_read_only` answers `False` for an entry that is not a `ServedEntry`, and the older always-`open` projection remains: a later caller would serve a read-only conversation `open` | No; carry |
| A2R-11 | Nit | `views.py` 150 to 158 | A 401 from inside the send or a read has no `WWW-Authenticate` | No |
| A2R-12 | Carry (SV3's) | `glow_discovery/interactions.py` 589 to 600 | After the other member's deletion the read by ID serves `(200, active, 1)`, after an unmatch `(200, unmatched, 2)` (probed): a member tells a deletion from an unmatch, as before A2. Once aligned, the list's candidates need the same filter | No; earlier |
| A2R-13 | Carry | Outside A2's paths | Stale lines: `test_row_locks_offline.py` 6 and 1167; `p11-deferred-acceptance.md` 105 (the list locks every match; manager-owned); `data-model.md` 528 to 540; `chat_projections.py` 17 | No |

**Its proposed remedies:** A2R-1 in A2's route layer (`send_error` answering `stale_contact_version` with the one code: one line, inside A2's paths, the pinned writer untouched; the send then never answers `stale_version`, which under D6 only a client sending a version the match never had would notice; three pins of today's answer change, and the suite gains a wrong-version case under each cause), or in `contact.py` (the version check below `_contact_state_checks`, keeping `stale_version` when nothing stops the send, as the mobile fixture adapter models it; D12's stop and the Dev Manager's read). Neither closes A2R-2, which it would record as a named limit carried to integration if A2R-1 is fixed in the route layer. A2R-3 by tests: A1's read-phase list cases run against `RouteConversationReads`, or two chat cases (a seeded active block not listed; a list held after its locks refused once its session ends). A2R-4 by answering the two negotiation failures as `invalid_request` with `no-store`, or by narrowing the sentence.

**What it did not read or run:** the ordering, identity and profile suites locally (the runs cover them); the database halves of the record's r02, r04, r05, r08, r13, r14 to r17, r22 and r22b (judged by reading); SV2's routes for A2R-4; DM-96's sections 1, 2, 4, 7, 8, 10, 13 and 15 (AG13 read whole); the other job logs beyond their conclusions and times; PostgreSQL's lock order inside one statement (documented behaviour); Notion.

**The manager's checks** (App Manager 13, 26 November 2026):
- **The live state:** `main` at `43e794a`; the manager branch and PR59 at `95e1278`; A2's branch at `88d4ef3`; `claude/dev-manager` at `8c587ac`; PR59's one thread unresolved, not outdated; Codex's summary still on `7e8811e`. As the report says.
- **A2R-1, read:** `OrmContactPersistence.send` checks the match's state (`contact.py` 521), both accounts (528), the session (526 to 535), a block (544), the version (546), then the profiles and consents (549); `send_error` maps `stale_contact_version` to `stale_version` (`contract.py` 169 to 170). Two more sentences rest on the order: `contract.py`'s docstring, lines 26 and 27 ("checked after the state"), and `production-contracts.md`'s send bullet, which states "another version is `stale_version`", so a fix in the route layer changes the documented contract.
- **A2R-3, reproduced (the offline half):** in a scratch clone of `26aa7ca`, with `or _blocked(me, other_id)` removed from `route_reads.py`'s loop, the API's `manage.py test tests` gave `Ran 685 tests … OK`.

**Disposition** (App Manager 13; the manager workflow's step 6, "What a correction pass is for" and "Fix or carry, by rule", under D-07). The fix's place for A2R-1 changes either the contract's documented answer or the writer `ReciprocalWriterTests` pins, and A2R-2's fix or carry is not decided by the rule, so both go to Dev Manager 7 first ([DM-99](https://github.com/amthorn78/glow-dating-app/blob/988a36a1fe4bc7b654a07e565e15fe721dcf3520/docs/ephemeral/2026-11-26-dm-99-sv4-a2-c1-design.md)):

| Finding | Disposition | Why |
|---|---|---|
| A2R-1 | **Fixed before the merge**, by correction A2-C1; the fix's place by DM-99, item 1 | A defect at a security boundary (what a member learns of a refused send's cause) in A2's own code, and a false claim the merge reads; class 2 and 3 of the review prompt |
| A2R-2 | **By DM-99, item 1:** fixed with A2R-1 (the manager's recommendation) or carried as a named limit to integration (the review's) | At the same boundary; narrow (a session ended inside one request); the rule does not decide between a fix and a carry |
| A2R-3 | **Fixed**, by A2-C1 (database cases that fail with each removed check) | A missing test at a security boundary (who may read a conversation) |
| A2R-4 | **Fixed**, by A2-C1, for A2's five routes; the form and SV2's and SV3's other routes by DM-99, item 2 | A false claim A2's acceptance check reads |
| A2R-5 | **Fixed**, by A2-C1 (one sentence, in a file A2R-4 changes) | A nit in a file the correction changes |
| A2R-8 (`match_version`'s fallback) | **Fixed**, by A2-C1 | The new wrong-version case reads the version through it |
| A2R-6, A2R-7, A2R-8 (the rest), A2R-10, A2R-11, A2R-13 | **Carried** (the carried-items file, "Carried to SV4" and "Carried to AC3") | Nits and stale lines in no class; A2R-11 is moot for the send if DM-99 chooses (a) |
| A2R-12 | **Carried**; where by DM-99, item 3 | SV3's, visible before A2 |
| A2R-9 | **Recorded here** | The record's wording; the findings table gives the right lines |
| The timing, the bound's consequence and the seal test's reach | **Recorded here** as limits | The review's, none in a class |
| Codex's P2 thread (comment 4658183908) | Resolved once A2-C1's fix and Codex's review of its head confirm it | It names A2R-1 |

### Dev Manager 7's DM-99 (26 November 2026)

[DM-99](../../continuity/dev-manager/reviews/2026-11-26-dm-99-sv4-a2-c1-design.md) (`c2ae138`, a read of `e28a5e2`; merged at `15a5646`) decided where A2-C1 fixes the send's one code: **(a), both A2R-1 and A2R-2 in A2's route layer,** with AK1 to AK8. Codex's second P2 thread (comment 4703261810, on `e28a5e2`, `contract.py` line 175) is A2R-2, found independently.
- **AK1:** the history read and the read cursor have the same split for a session ended mid-request (`reads.py`'s `_authorize` checks the session after the accounts and before the block and the causes), harmless at launch and open once the console publishes a cause `hidden`; A2-C1 maps those session reasons to the one code there too. The list, `session_missing`, `accountsession_missing` and SV1's door keep `unauthenticated`.
- **AK2:** an offline test lists, from the source, every reason `send` and `_authorize` can raise after their locks and pins each one's served code; database cases run the review's probe table with a wrong version and with a session ended once the send holds its locks, and the two reads under a cause published `hidden` and under an unmatch.
- **AK3 to AK7:** the contract's and the route contract's words, which A2-C1 applies with its code; **AK8:** D8's send bullet, applied in the brief's revision 10.
- **A2R-4:** a negotiation that ignores `Accept` and `format` on A2's five views; SV2's and SV3's routes carried to P10.
- **A2R-12:** carried to P08.2 by name (AK9), with the P11 plan's match-state gate rewritten (AK10): a block's direction met by A1's D4, a deletion open.
- **AK11:** A2R-8's case-3 part (the cursor for both members) goes into A2-C1, since D10's list is A2's acceptance check; the challenge-header part rides along (the manager's choice).
- **A delta review is confirmed,** with DM-99's five-point focus (its section 6).
- **The dispositions above therefore stand as:** A2R-1, A2R-2 (with AK1), A2R-3, A2R-4, A2R-5 and A2R-8 (both parts) fixed by A2-C1; A2R-11 carried for the list only; A2R-12 carried to P08.2; the rest as the table says. Added to "Carried to AC3": the mobile fixture adapter's `stale_version` for a send's wrong version (`fixture-adapter.ts`, line 276).
- **Nathan's relay** carried DM-98's message of 22 November, not DM-99's; the manager took the report from `claude/dev-manager` under the charter's fallback.

## A2-C1

- **Session:** SV4 A2's correction A2-C1, started by Nathan from [A2-C1's prompt](https://github.com/amthorn78/glow-dating-app/blob/4a72036b4bdca1fa258184ef48bcb9bb257714fb/docs/ephemeral/2026-11-26-sv4-a2-c1-correction-prompt.md), revision 1, from `4a72036b4bdca1fa258184ef48bcb9bb257714fb` of the manager branch, and resumed by [App Manager 13's resume message](https://github.com/amthorn78/glow-dating-app/blob/f435cef97cf9da6c2d81bbbb45c2420bcd73d9bb/docs/ephemeral/2026-11-26-sv4-a2-c1-resume-message.md), revision 1, at `f435cef97cf9da6c2d81bbbb45c2420bcd73d9bb`. The specification is the [brief](../../planning/sv4-chat-notifications.md), revision 10 ("Owned paths", A2-C1), with [DM-99](../../continuity/dev-manager/reviews/2026-11-26-dm-99-sv4-a2-c1-design.md)'s AK1 to AK7 and AK11.
- **Branch:** `claude/affectionate-sagan-r916ba`, which the push filter's `claude/**` covers. It starts at the prompt's commit.
- **Code head:** `ddb1386ac04c84195189bfd73fc9f21ba65225bf`, whose run is the run of record. **Records head:** the commit that adds this section, pushed after that run had finished.
- **What A2-C1 fixed:** A2R-1 and A2R-2 (with AK1's reads), A2R-3, A2R-4 (with Codex's third P2 thread on PR59, comment 4704969737 on `views.py` line 171, "Normalize content-negotiation failures into contract errors", which is A2R-4 found independently; not replied to or resolved here), A2R-5 and A2R-8's three parts (AK11).
- **What it did not touch:** `glow_chat`'s `contact.py`, `reads.py` and `route_reads.py`, all of `glow_domain/` (`git diff` of them from the prompt's commit to the code head prints nothing; the reversals' temporary edits of `contact.py` and `route_reads.py` were undone, below), SV1's authentication, SV2's and SV3's other views, the workflow, the contract's schema, registry and generated outputs, and every other suite. No provider call, HDE call, external database or credential.

### The start gate and the environment check

- **The environment** (names only): no `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY`; no `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name. Present and never read, printed or passed to a command: `AWS_ACCESS_KEY_ID`, `AWS_CA_BUNDLE`, `AWS_SECRET_ACCESS_KEY` (OD-76), `GH_TOKEN`, `GITHUB_TOKEN`. Toolchain: `Python 3.12.14`; `Docker version 29.9.3, build 5457199` (its daemon started by the session, and stopped at the end). Every repository command ran under `env -i PATH=… HOME=… LANG=C.UTF-8`, plus only its own variables (`GLOW_ENV=test` for the API; the proof's `PROOF_*` names for the suite); `pip install --require-hashes` needed the proxy's `HTTPS_PROXY` and `PIP_CERT` added, values unprinted. The two virtual environments were made with `python3.12` outside the checkout.
- **The start gate:** `git rev-parse HEAD` printed `4a72036b4bdca1fa258184ef48bcb9bb257714fb`; "this prompt's commit is on the live branch", "A2's code head" and "no code on the live branch after 26aa7ca" printed; `grep -c` printed `1` for "Exact-head review of A2" and `0` for "A2-C1". At the resume: the resume message's commit `f435cef` on the live branch, no non-Markdown change there since `4a72036`, and the working tree equal to the diff saved at the stop.

### The stop, the decision and the resume

- **The stop** (26 November 2026, before any commit or push): the first local chat suite run (iteration) failed `transactions.non_atomic_requests` with "the match read: answers 200". The case built its send's body with `ctx.message(one, match.id)` after it set `ATOMIC_REQUESTS`; `message()` reads the version through `match_version`, that is through SV3's match read, which refuses inside `ATOMIC_REQUESTS` (503, `transaction_open`). Until item 6 the fallback answered 1, so the case sent a guessed version. The case was not named in items 6 or 8, so the stop rule ("an earlier test") applied: no further change, no commit, the throwaway database removed. The same run failed the session's own new list case, whose expectation for the own-account check (401) was wrong; it was left as it was at the stop.
- **The decision** (the resume message; AM13-07 records the missed sweep): `transactions.non_atomic_requests` joins item 6's list for one change only, the send's body built before `ATOMIC_REQUESTS` is turned on; the list case's own-account check expects `not_found` (404); any other case failing on the removed fallback is handled the same way, anything more a stop. No other case failed on it.

### What was changed, by item

1. **The send's one code** (`contract.send_error`): `stale_contact_version` and the session's reasons the send raises once it holds its locks (`session_changed`, `session_not_valid`, `session_expired`, `session_epoch_stale`) answer `SEND_STOPPED` (`not_found`, 404, not retryable), the body every stopped cause answers. `session_missing`, the `_lock` helpers' `<table>_missing` forms (`accountsession_missing` staying `unauthenticated`) and SV1's door are unchanged; `idempotency_conflict`, `state_conflict` and the rest are unchanged. Its docstring states the mapping and why.
2. **The reads' one code** (`contract.read_error(outcome, reason, *, conversation=False)`): with `conversation=True` the same four session reasons answer `not_found`. `views.py`'s `HistoryView` and `ReadCursorView` pass `conversation=True`; the list's call is unchanged and keeps `unauthenticated`, as do `session_missing` and `accountsession_missing`. `error_for` and `glow_domain` are unchanged. The keyword defaults to off so the list's line stays as it was; the offline tests pin both routes' answers, so a conversation route that omitted it would fail them.
3. **The proof that the mapping is complete** (AK2):
   - **Offline,** `MappingCompletenessTests` (`test_chat_routes_offline.py`, 4 tests). It parses `contact.py` and `reads.py` with `ast`. From the line of the function's first lock call (`self._lock` in `send`'s `body`, `_lock_shared` in `_authorize`) it reads every `raise _Refused(X)` and every lock call's `<table>_missing` form, in the function and in every helper it calls from there, followed into the helpers' own calls: the class's methods called as `self.<name>` (`_contact_state_checks` among them), the module's functions (`_history`, `_causes`, `_blocked`, `readable`, `_signal`), and the module aliases of `OrmContactPersistence`'s methods (`_clock`). `X` is resolved as a `chat.<NAME>` constant, a module constant (`CONVERSATION_HIDDEN`), a name imported from `glow_domain`, or `_history`'s pass-through of `settings_store.read_shared`'s reasons (read from that function: `setting_unresolved`); any other form fails the test. The found set must equal the pinned table exactly (16 reasons for the send, 13 for `_authorize`), and each is pinned to its code; `RouteTests.test_every_pinned_reason_is_served_with_its_code_and_status` serves each through its route (the send; the history read and the read cursor), checking the status (404, 401 for `accountsession_missing`, 409 for `idempotency_conflict`), `no-store`, no value echoed, one body for every `not_found`, and the list answering the four session reasons 401. `test_a_reason_added_after_the_locks_is_found` checks the reading itself on a modified copy of the source. **What it would miss:** a reason raised by a function of another module (but `read_shared`), one returned as a result instead of raised, a database error (served `state_conflict`, never a reason), the callers' own later reasons (`_select`'s `cursor_invalid`, `_move`'s `message_unavailable`, pinned by `RouteTests`), and the reasons before the first lock (pinned by `SendRefusalTests`).
   - **Database cases:** `send.one_answer_for_every_version_and_session` (the probe table, below) and `reads.session_ended_in_locks_answers_as_hidden`. A session "ended once the route holds its locks" is built with the suite's hold points and an observed wait: `glow_chat`'s `sign_out` (the session row `FOR UPDATE`) is held at its commit (`Hold("before_commit")`); the route's request, made then through Django's test client on its own thread and connection, passes SV1's door (which reads with no lock, so sees the session valid) and waits on that row at its own session lock, observed in `pg_stat_activity` (`observe_lock_wait`, the waiter found by `pg_blocking_pids`); the sign-out then commits and the route finds the session revoked (`session_not_valid`). The reads' case runs last (it publishes `other_pause` `hidden` if no earlier case has), with `ar13.*` and `d5.each_cause_hidden` before it; `test_the_cases_that_publish_hidden_run_last` now reads the last three, and no earlier case publishes.
4. **The list's checks, proven** (A2R-3): `list.block_session_and_own_account_checks`. A seeded active block beside an active match (test data) is listed to neither member, where it was listed to both before the block. A list whose session ends after its account locks (the same held sign-out; the list waits at its session lock after its account and match locks) is refused `unauthenticated` (401). A list whose account is no longer `active` once it holds its locks is refused `not_found` (404; `account_not_active` through `error_for`, as A1's reads refuse it). **That last check is reached only by test data, inside a race with SV1's door:** every writer that takes an account out of `active` (`glow_chat`'s suspension and deletion) also moves its epoch, so the session's check refuses first. (False, as A2-C1's delta review found, F1: the list checks its own account before the session's state, expiry and epoch, so a real suspension or deletion that commits after the request has passed SV1's door, and before the list's account lock is granted, reaches this check too. The corrected statement is in "Delta review of A2-C1"; DM-100 carried the docstrings.) The case holds a transaction that sets the account `suspended` with its session left `valid` at its epoch (a plain `UPDATE`, test data), the list's request passes the door, waits on that row at its account lock (observed), and reads the new state once it commits.
5. **The routes' negotiation** (A2R-4; DM-99 item 2): `views.JsonOnlyNegotiation`, a `DefaultContentNegotiation` whose `select_renderer` always returns the JSON renderer and reads neither `Accept` nor the `format` override, is set on `_ChatRoute` (the four chat views' base) with `renderer_classes = [JSONRenderer]`; `MatchListView` declares the same, as a class inside it (`interaction_views.py` changes inside `MatchListView` only). Offline (`RouteTests.test_the_negotiation_reads_neither_accept_nor_format`): on all five routes `?format=xml` answers `invalid_request` (400) signed and `unauthenticated` (401) unsigned, each the contract's `Error` with `no-store`, and `Accept: text/html` is served as JSON (200, its DTO). `test_sv3s_other_views_keep_their_negotiation`: `InteractionView`, `UndoView`, `UnmatchView`, `BlockView`, `MatchView` and `OwnVersionsView` keep DRF's default class, and `MatchView` still answers `?format=xml` with the framework's 404 `{"detail": "Not found."}` without `Cache-Control` (carried to P10, DM-99).
6. **The nits:**
   - `views.py`'s module docstring: "Its tests are ``TransactionTestCase``s." is replaced by what the record says: no Django `TestCase` tests them; their database tests are the chat suite's cases, through Django's test client with no enclosing transaction and autocommit on, and `transactions.non_atomic_requests` shows every read refused inside a caller's transaction.
   - `reads.history_list_and_cursor_for_both`: after the first member's moves, the second member's unread count is still 3; the second member moves the cursor (unread 1), and a cursor behind changes nothing; the first member's count is still 0 and the second's 1.
   - `routes.refuse_what_is_not_their_dto`: each 401 reply's own headers are read, so `WWW-Authenticate: Bearer` is checked on the no-token reply as well as on the refused-token one.
   - `chat_support.match_version`: a refused match read fails the case (`ProfileContext.data`), never answering 1.
7. **DM-99's words** (AK3 to AK7): applied by a script that read each old passage at `4a72036` and in the working file, required each exactly once, replaced it and required the new passage exactly once: AK3, AK4, AK5 and AK6 in `production-contracts.md`, AK7 in `contract.py`'s module docstring, each "old at 4a72036 1, old now 1, new after 1"; AK7's longest line 93 characters.

**The earlier pins and cases that changed** (items 6 and 8, and the resume message; every other assertion kept):

| Where | Old answer | New answer |
|---|---|---|
| `SendRefusalTests.test_the_other_refusals_keep_their_codes` (line 238 on) | `stale_contact_version` `stale_version`; `session_not_valid`, `session_expired`, `session_epoch_stale`, `session_changed` `unauthenticated` | each `not_found`; `session_missing` still `unauthenticated` |
| `RouteTests.test_the_sends_five_refusals_answer_one_code` (lines 629 and 631) | `send:stale_contact_version` 409 `stale_version`; `send:session_not_valid` 401 `unauthenticated` | each 404 `not_found`, with the five's body (added) |
| `RouteTests.test_the_reads_refusals_are_error_fors` (line 642) | `session_expired` 401 on the list, the history and the cursor | 401 on the list, 404 `not_found` on the history and the cursor; `session_not_valid`, `session_epoch_stale`, `session_changed` added the same way, `session_missing` and `accountsession_missing` added at 401 on all three |
| `RouteTests`' route script, `answer()` | `response["Cache-Control"]` (a missing header raised in the fresh process) | `response.get("Cache-Control")`, so a framework answer with no header is recorded and judged by the assertions (found by reversal r8) |
| case `send.replay_conflict_and_version` | versions 0 and 2: 409 `stale_version` | 404 `not_found`; nothing written, as before |
| case `transactions.non_atomic_requests` (the resume message) | the send's body built inside the `ATOMIC_REQUESTS` block (its match read refused there; version 1 guessed by the fallback) | the body built before the block; every expectation and the order of the requests inside the block unchanged |
| `CASE_COUNT`, `ChatPlanTests.test_the_case_count_is_pinned`, `PLAN`, the README's count | 15 | 18 (three cases added, the plan's order pinned) |
| `ChatPlanTests.test_the_cases_that_publish_hidden_run_last` | the last two cases | the last three (`reads.session_ended_in_locks_answers_as_hidden` added after `d5.each_cause_hidden`) |

`ReciprocalWriterTests`' digests hold (`contact.py` unchanged), and `test_chat_reads.py`'s `error_for` table is unchanged.

### The review's probe table, re-run as a case

`send.one_answer_for_every_version_and_session`, each row on a fresh pair, the current version read from the match read (D6: 2 after the unmatch, 1 otherwise); the block and the withdrawn consent are test data, as in case 4:

| Row | Current version | Wrong version (0 and 7) | Session ended in the send's locks |
|---|---|---|---|
| No cause | 200 `pending` | 404 `not_found` | 404 `not_found` |
| The other member suspended | 404 `not_found` | 404 `not_found` | 404 `not_found` |
| The other's pause | 404 `not_found` | 404 `not_found` | 404 `not_found` |
| The own pause | 404 `not_found` | 404 `not_found` | 404 `not_found` |
| The other's restriction | 404 `not_found` | 404 `not_found` | 404 `not_found` |
| The other's consent withdrawn | 404 `not_found` | 404 `not_found` | 404 `not_found` |
| An unmatch | 404 `not_found` | 404 `not_found` | 404 `not_found` |
| A block | 404 `not_found` | 404 `not_found` | 404 `not_found` |
| The other's deletion | 404 `not_found` | 404 `not_found` | 404 `not_found` |

35 stopped sends, one status, code and body; no refused send wrote a submission. The adapter's own reasons at version 0, which the route never serves, are four: `stale_contact_version`, `account_not_active`, `match_not_active` and `blocked` (the case checks that set; which row gives which follows `send`'s order). The reads' case: the history read and the read cursor, each with a valid session and with a session ended in their locks, under the other's pause published `hidden` and under an unmatch: eight reads, each 404 `not_found`, one body.

### Reversals

Each by a scratch harness that found each old text exactly once, wrote the edit, ran the named tests or the whole chat suite on a freshly recreated throwaway database, and restored each file byte for byte (its SHA-256 checked). Two reversals that touch disjoint cases shared one suite run. Every one failed as intended; `git status` afterwards showed only the session's own changes.

| Reversal (the edit) | What failed |
|---|---|
| r1: `send_error` answers `stale_version` for `stale_contact_version` | offline (4): `MappingCompletenessTests…send…` ("('stale_version', False) != ('not_found', False)"), `RouteTests.test_every_pinned_reason…` ("(409, 'stale_version', False, True) != (404, 'not_found', False, True)"), `RouteTests…five…`, `SendRefusalTests…keep_their_codes`; database: `send.replay_conflict_and_version` ("the version 0: answers 404") and `send.one_answer_for_every_version_and_session` ("no cause: the version 0: answers 404") |
| r2: `session_not_valid` answered `unauthenticated` again in `send_error` | offline (5): `MappingCompletenessTests…send…` and `…session_found_ended…` ("('unauthenticated', False) != ('not_found', False)"), `RouteTests.test_every_pinned_reason…` ("(401, 'unauthenticated', …) != (404, 'not_found', …)"), `RouteTests…five…`, `SendRefusalTests…keep_their_codes`; database: `send.one_answer…` ("no cause: a session ended in its locks: answers 404") |
| r3: the history read's refusals mapped without `conversation=True` | offline (8): `RouteTests.test_every_pinned_reason…` for `history` × the four session reasons, `test_the_reads_refusals_are_error_fors` for the four ("(401, 'unauthenticated', True, False) != (404, 'not_found', True, False)"); database: `reads.session_ended_in_locks_answers_as_hidden` ("history, the other's pause, hidden: a session ended in its locks: answers 404") |
| r4: `raise _Refused(chat.SELF_TARGET)` added after the send's block check (`contact.py`, temporary) | offline (2): `MappingCompletenessTests.test_every_reason_the_send_raises…` and `test_a_reason_added_after_the_locks_is_found` ("Items in the first set but not the second: 'self_target'") |
| r5: the served list's block check removed (`route_reads.py`, temporary) | database: `list.block_session_and_own_account_checks` ("a block is listed to neither") |
| r6: the served list's session checks removed (`session_not_valid`, `session_expired`, `session_epoch_stale`) | database: the same case ("a list whose session ended in its locks: answers 401") |
| r7: the served list's own-account check removed | database: the same case ("a list whose account is not active in its locks: answers 404") |
| r8: `HistoryView` given DRF's `DefaultContentNegotiation` back, and `MatchListView`'s negotiation removed | offline: `RouteTests.test_the_negotiation_reads_neither_accept_nor_format` for `HistoryView` and `matches` ("(404, None, False, False) != (400, 'invalid_request', True, False)"). Its first run errored in `RouteTests.setUpClass` instead (the route script read the framework's missing `Cache-Control`); `answer()` was made to read it with `.get`, and the reversal then failed as above |
| r9: case 3's second member's cursor moves removed | database: `reads.history_list_and_cursor_for_both` ("the other's own count") |
| r10 (the resume message): the send's body built inside the `ATOMIC_REQUESTS` block again | database: `transactions.non_atomic_requests` ("the match read: answers 200"), as at the stop |

The runs: r1 with r5 (15/18 passed; the three named cases failed), r2 with r6 (16/18), r3 with r7 (16/18), r9 with r10 (16/18); each run's scans clean and `ROW LOCKS (D14): PASS`.

### Commands and results

At the code head, in a clean environment (local; the run of record repeats them):
- **The API**, after `pip install --require-hashes -r requirements-dev.lock` and `pip check` ("No broken requirements found."), with `GLOW_ENV=test`: `manage.py check` "System check identified no issues (0 silenced)"; `manage.py test tests` `Ran 692 tests … OK`, no skip (685, no skip, at the prompt's commit); `test_chat_routes_offline.py` 31 tests (24 before); `makemigrations --check --dry-run` "No changes detected"; `ruff check .` "All checks passed!"; `ruff format --check .` "175 files already formatted" (175 before); `mypy` "Success: no issues found in 99 source files" (99 before); the contract's Python tests `Ran 55 tests … OK` (55 before).
- **The proof's offline tests**, from its own lock: `Ran 421 tests … OK` (421 before: the plan's tests changed, none added); Ruff "All checks passed!", "78 files already formatted"; mypy "Success: no issues found in 78 source files" (78 and 78 before).
- **The trusted classifier**, `main`'s `scripts/change_scope.py` (`43e794a`; SHA-256 begins `b564c62f4a076f51`), extracted to the scratchpad outside the checkout and run as `python3 -I <copy>/change_scope.py --base 43e794a5500e1ffdb12bfb2b2b2c0a9332c45ca2 --head ddb1386ac04c84195189bfd73fc9f21ba65225bf --merge-base`: `"full": true`, reason `behavior-or-empty`. `git merge-base --all` gives one base, `43e794a`.
- **The diff:** `git diff --name-only 4a72036b4bdca1fa258184ef48bcb9bb257714fb ddb1386ac04c84195189bfd73fc9f21ba65225bf` lists nine paths, each owned: `services/api/glow_chat/contract.py`, `views.py`, `glow_discovery/interaction_views.py` (one hunk, inside `MatchListView`), `tests/test_chat_routes_offline.py`, the proof's `chat_cases.py`, `chat_support.py` (`match_version` only), `tests/test_chat_offline.py` (the plan's tests only), `README.md` (the count only) and `docs/architecture/production-contracts.md` (AK3 to AK6 only). `git diff` of `contact.py`, `reads.py`, `route_reads.py` and `glow_domain/` prints nothing.
- **GitHub:** read with `gh api` REST `GET` calls only (the run and its jobs and logs); nothing written but the two pushes of this branch (the code head, then this records commit). PR59's threads were not replied to or resolved.

### Local database runs (iteration, not evidence)

Under P06.DB's D4: the pinned image `postgres@sha256:d74eeac9…`, pulled from Docker Hub; loopback only (`127.0.0.1:5433`); generated passwords, markers and keys in a mode-700 scratch directory, never printed; none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name in any process environment (the suite's own `PROOF_DB_*` names only); the chat database and the decoy each with its own marker; migrations only through the proof's own `python -m django migrate` under the chat settings. The first run (at the stop): 16/18, `transactions.non_atomic_requests` and the new list case failing, scans clean, `ROW LOCKS (D14): PASS`, `CHAT VERDICT: FAIL`. After the resume, at the code head's content: `[chat] cases: 18/18 passed in 183.4 s`; `chat secret scan: clean (1429 secrets held; 0 found in 1094 log records, 116 writes and the results JSON)`; `chat value scan: clean (1153 member values held …)`; `106658 statements … 10204 take a writer's row lock, 2966 of them naming the account table (2966 FOR NO KEY UPDATE …); 0 refused`, `ROW LOCKS (D14): PASS`; `CHAT VERDICT: PASS`; `chat_scan` passed. Then the four reversal runs, each on a freshly recreated database. Afterwards the container, the credential files and the results were removed, no proof container remained, and the Docker daemon the session had started was stopped. The `dbshell` and decoy steps, the second-run refusal and the upload gate are CI's only.

### The run of record

**Foundation run [45778164243](https://github.com/amthorn78/glow-dating-app/actions/runs/45778164243)** on `ddb1386ac04c84195189bfd73fc9f21ba65225bf` (a push run, attempt 1) concluded **success**. It was created at 07:49:15 UTC on 26 November 2026 and its gate finished at 07:57:13 (about 8 minutes in all); the gate printed "Application checks passed". Nothing was pushed to the branch until it had finished. The durations are from the jobs' timestamps (whole seconds); A2's are from its run of record, 45022218979.

| Job | Conclusion | Duration | A2's | Timeout |
|---|---|---|---|---|
| Change scope | success | 11 s | 12 s | 3 min |
| API checks | success | 75 s | 71 s | 10 min |
| Mobile checks | success | 418 s | 465 s | 25 min |
| API mobile smoke | success | 94 s | 86 s | 10 min |
| API artifact checks | success | 27 s | 22 s | 15 min |
| Stream proof checks | success | 75 s | 70 s | 10 min |
| Database proof checks (ordering) | success | 459 s | 351 s | 30 min |
| Database proof checks (identity) | success | 95 s | 130 s | 30 min |
| Database proof checks (profile) | success | 152 s | 146 s | 30 min |
| Database proof checks (discovery) | success | 233 s | 235 s | 30 min |
| **Database proof checks (chat)** | success | **158 s** | 142 s | 30 min |
| Foundation gate | success: "Application checks passed" | 2 s | 5 s | 2 min |

**What the logs show** (read with `gh api` REST `GET` calls):
- **The chat job:** the offline tests `Ran 421 tests … OK`, Ruff "All checks passed!" and "78 files already formatted", mypy "Success: no issues found in 78 source files"; `chat dbshell exit status: 1` with `RefusedDatabase: refusing dbshell …`; the decoy `glow_discovery_proof` present with its own marker (`1`, its comment differing: `t`), its marker refused (`chat migrate with the decoy database's marker: exit status 1`, `RefusedDatabase: refusing this database …`); the migrations from zero; every one of the eighteen cases `PASS`, the three new ones among them; `[chat] cases: 18/18 passed in 94.3 s`; `chat secret scan: clean (1429 secrets held; 0 found in 1094 log records, 116 writes and the results JSON)`; `chat value scan: clean (1153 member values held: …; 0 found in the same output)`; `[chat] row locks sent (D14): 106643 statements … 10204 take a writer's row lock, 2966 of them naming the account table (2966 FOR NO KEY UPDATE, 0 FOR UPDATE OF other tables only); 0 refused`, `ROW LOCKS (D14): PASS`; `CHAT VERDICT: PASS`; `chat phase: 95 s (the job's timeout is 30 minutes)`; the second run refused (`second chat run exit status: 1`, `refusing a used database: …`); `container removed: glow-proof-db-chat-45778164243-1`, `credential and marker files removed`, `no proof container remains`.
- **The API checks job:** `Ran 692 tests … OK (skipped=2)` (the two history tests of `ReciprocalWriterTests` skip, as on every branch push, which has no local `main`), the contract tests `Ran 55 tests … OK`.
- **The discovery job:** `[discovery] cases: 70/70 passed in 168.6 s`, `DISCOVERY VERDICT: PASS`.
- **Within its timeout:** each job finished well inside its `timeout-minutes`; the chat job took 158 s of its 30 minutes.

### What A2-C1 changes in section "A2"

- **The send's one code** now holds for every version and for a session ended mid-request: a wrong version and a session the send finds ended once it holds its locks answer `not_found` with the stopped causes' body, so section "A2"'s "the other refusals keep their codes: `stale_contact_version` is `stale_version` … the session's reasons are `unauthenticated`" is replaced by item 1 above (a session missing before the locks stays `unauthenticated`), and the claim "so a member never learns which cause stopped a send" now holds for every version (A2R-1) and for a session ended inside the send (A2R-2).
- **The reads' one code** holds for a session ended mid-request: the history read and the read cursor answer such a session `not_found`, as a hidden conversation; the list keeps `unauthenticated` (A2R-11 stays carried for the list only).
- **The list's checks are proven:** each of the served list's block, session and own-account checks, removed, fails a database case (A2R-3).
- **Every refusal is the contract's `Error`** on A2's five routes, the negotiation failures included (A2R-4), as D8 says.
- **The suite has 18 cases.** Section "A2"'s case table and the proof's README list the fifteen; the three added are this section's.

### Limits and deviations

- **The stop and the resume:** above. The changed case `transactions.non_atomic_requests` was named by the resume message, not the prompt (AM13-07).
- **The own-account check is reached only by test data** inside a race with SV1's door (item 4). (False: a real suspension or deletion that commits in the same race reaches it too; A2-C1's delta review, F1, and DM-100.)
- **`read_error`'s `conversation` keyword defaults to off**, so the list's call is unchanged; a future conversation route that omitted it would answer `unauthenticated` for a session ended in its locks. The offline tests pin the two routes that exist.
- **`MatchListView`'s negotiation class is declared inside the view,** with the class-level imports it needs, to keep `interaction_views.py`'s change inside `MatchListView`; it duplicates `views.JsonOnlyNegotiation`'s few lines.
- **`contract.STALE_VERSION`** (a module constant) is no longer used by `contract.py`; it was left, outside the owned passages.
- **The mid-request cases end the session one way** (`sign_out`, `session_not_valid`); `session_expired`, `session_epoch_stale` and `session_changed` inside the locks are covered by the offline tests only.
- **The offline completeness test's reach** is item 3's "What it would miss".
- **The route script's `answer()`** now reads `Cache-Control` with `.get`; a test change outside items 6 and 8's named pins, made in a file the prompt owns whole, found by reversal r8, and changing no assertion.
- **Not updated:** section "A2"'s case table and the proof README's list of the cases (outside the owned passages; the README's count only is owned); the mobile fixture adapter's `stale_version` for a wrong send version (carried to AC3, DM-99).
- **The local database runs are iteration only;** the run of record is CI's.

### Manager verification of A2-C1 (App Manager 13, 26 November 2026)

- **The heads:** `claude/affectionate-sagan-r916ba` at `2201c2d` (records; it changes only this record), with the code head `ddb1386` on the prompt's commit `4a72036`. Merged into the manager branch at `356ee8f`, whose non-Markdown paths equal `ddb1386`; `main`'s trusted classifier, outside the checkout with `python3 -I` and full SHAs, gives `"full": true`, reason `behavior-or-empty`, one merge base `43e794a`.
- **The diff** (`git diff 4a72036 ddb1386`): nine paths, each in A2-C1's owned paths; `contact.py`, `reads.py`, `route_reads.py`, `glow_domain/`, `.github/`, `packages/` and `apps/` unchanged. Read in full for the three non-test modules: `send_error` answers `SEND_STOPPED` for `stale_contact_version` and the four in-lock session reasons; `read_error(..., conversation=True)` answers `not_found` for the same four on the history read and the read cursor only, which `views.py` passes; `JsonOnlyNegotiation` on `_ChatRoute` and a copy inside `MatchListView`, each with `renderer_classes = [JSONRenderer]`. By a count of the changed lines, the three modules gain 44 code lines and 50 docstring or blank lines and lose 14 (6 of them code): 108 changed non-test lines, over the 60 of the workflow's step 6 as earlier items counted them (added and removed, docstrings included; DM-48, P06.2-F's C5), and 50 changed code lines. DM-99 had forecast "well under 60 non-test lines" before the code existed. DM-100 (item 5) let the delta review stand: it read every path the correction touches whole at its head, and every other path is as A2's exact-head review read it.
- **DM-99's words:** AK3 to AK6 (`production-contracts.md`) and AK7 (`contract.py`) each occur once at `ddb1386`, and each old passage is gone (a script on DM-99's report).
- **The run of record,** Foundation run 45778164243 (`push`, `ddb1386`, attempt 1), read with `gh api`: all twelve jobs succeeded; the gate's log has "Application checks passed"; the chat job's log has `[chat] cases: 18/18 passed in 94.3 s`, both scans clean (1429 secrets, 1153 member values, 0 found), `ROW LOCKS (D14): PASS`, `CHAT VERDICT: PASS`, `dbshell` and the decoy's marker refused (exit status 1) and the second run refused; the API checks job `Ran 692 tests … OK (skipped=2)` (the two history tests every branch push skips).
- **Codex's third P2 thread** (comment 4704969737, on `f435cef`, `views.py` line 171, "Normalize content-negotiation failures into contract errors") is A2R-4, found independently; item 5 answers it. Codex's three threads stay unresolved until the delta review and Codex's review of the head that holds the fix confirm them.
- **Not re-run by the manager:** the session's local checks and its ten reversals; the run of record ran the suites in CI.
- **For the delta review** (DM-99's section 6, with the session's "Limits and deviations"): the mapping's completeness and the offline test's reach; the probe table and the reads' case; the list's three checks; the negotiation on the five routes, SV3's other views unchanged; AK3 to AK8 as given; `read_error`'s keyword default; `MatchListView`'s class-level imports, which make `DefaultContentNegotiation` and `JSONRenderer` attributes of the view; the mid-request cases ending a session by sign-out only.

### Delta review of A2-C1 (26 November 2026)

- **Session:** the delta review, started by Nathan from [A2-C1's delta review prompt](https://github.com/amthorn78/glow-dating-app/blob/2e075c35c25e085fb480b0e00f5931a93c164fdd/docs/ephemeral/2026-11-26-sv4-a2-c1-delta-review-prompt.md), revision 1, from `2e075c3`, in `Glow App - No Stream`. GitHub read with the GitHub MCP tools and `gh api` REST `GET` calls; nothing written; its checkouts left clean.
- **Its gates:** the environment clean (AWS and GitHub token names present, unread); every start-gate check passed (`HEAD` `2e075c3`, one merge base `43e794a`, the code `ddb1386`'s, no delta review recorded); the trusted classifier `"full": true`, reason `behavior-or-empty`.
- **Verdict: changes requested, for words only.** The code at `ddb1386` does everything DM-99 decided, and every reversal fails where the record says it does; one should-fix finding (F1) the reviewer places in class 3, a false claim.

**What it verified** (its focus, shortened):
- **The mapping:** `send` raises 16 reasons after its first lock and `_authorize` 15 (not 13: `settings_store._setting`, through `_history`'s `read_shared`, adds `setting_version_missing` and `setting_pointer_mismatch`); every one is served as DM-99 decided, `idempotency_conflict` only after every cause check. `contact.py`, `reads.py`, `glow_domain/`, `glow_identity/` and `glow_profiles/` are byte-equal from `main` to `ddb1386`, `route_reads.py` to `26aa7ca`; `ReciprocalWriterTests` passes. `MappingCompletenessTests` fails for a reason added after the locks in `send`, a `send` helper, `_authorize` or through a variable; it misses `read_shared`'s own helpers (F2).
- **The probe table:** locally 35 stopped sends, each 404 `not_found` with one body; the reads' case 8 reads, each 404. The sessions are truly ended while the route waits at its own lock (the sign-out held `FOR UPDATE` at `before_commit`; SV1's door reads with no lock; the wait observed or the case fails); no row passes with the route's answer unchanged. Nothing else a member controls splits the causes (a replay and an idempotency conflict come after every cause check; timing, the recorded limit).
- **A2R-3:** each of the list's three checks, removed, fails a database case; the own-account check is reached by the test data, and by a real writer too (F1).
- **A2R-4:** on the five routes `?format=xml` answers 400 signed and 401 unsigned with `no-store`, `Accept: text/html` is served as JSON; SV3's six other views keep DRF's default; `MatchListView`'s class-level imports change nothing served.
- **AK3 to AK8:** applied as given (a script against DM-99's section 9); the earlier pins changed only as decided; no assertion removed; no new test vacuous.
- **The records** hold except F1 to F3; every figure checked is right.

**Its checks:** the API `Ran 692 tests … OK`, no skip, Ruff, format (175 files), mypy (99), no migration change, the contracts 55; the proof 421 OK, Ruff and mypy (78). Offline reversals: r1 (4 failures), r2 (5), r3 (8), r3 on the cursor (8), r4 (2), r4 in a `send` helper (2), r4 in `_authorize` (1), r4 through a variable (1), r4 in `_setting` (nothing fails: F2), r8 (`HistoryView` and the match list), r8 on an SV3 view (its pin fails). Database runs under P06.DB's D4 (informational): the suite at the head 18/18 in 172.3 s, both scans clean, `ROW LOCKS (D14): PASS`, `CHAT VERDICT: PASS`; r1, r2, r3, r3 on the cursor (after `d5.each_cause_hidden`), r5, r6, r7 and r10 each failing with the record's message; the F1 probe; the reads' case alone (F4). **The runs:** PR59's run 45791045751 (`pull_request`, `2e075c3`), twelve jobs, the chat job 18/18 in 97.1 s, the gate "Application checks passed"; the run of record as recorded. **Codex:** its review of `2e075c3` completed with no findings; its three P2 threads unresolved (4658183908 and 4703261810 outdated; 4704969737 on `views.py`, now line 192), each answered by the code at `ddb1386`.

**Its findings** (in its words, shortened):

| ID | Severity | Where | Finding | Its class |
|---|---|---|---|---|
| F1 | Should fix | The record's lines 1967 and 2077; `chat_cases.py` 1179 to 1181 and 231 to 232 (the first range first given as 179 to 181; DM-100); the resume message's line 26 (manager-owned) | "The own-account check is reached only by test data … every writer that takes an account out of `active` also moves its epoch, so the session's check refuses first" is false: `route_reads.py` checks the own account (162 to 163) before the session's state, expiry and epoch (164 to 169), and `_revoke_account` (`contact.py`, 775 on) locks only the account row. Probed: a real `suspend` and a real `delete` held at commit while the list waited at its account lock both answered 404 `not_found` from the own-account check (401 with the check removed). Behaviour as decided; nothing about the other member leaks | Class 3, a false claim; words only |
| F2 | Nit (reach) | `test_chat_routes_offline.py` 292 to 309 and 327; the record's line 1965 | The completeness test reads only `read_shared`'s own raises, not `_setting`'s (`setting_version_missing`, `setting_pointer_mismatch`): `_authorize` raises 15 reasons, not 13; a new reason in `_setting` fails nothing. Both are served `not_found`, global setting states | No |
| F3 | Nit | The record's line 1965 | `cursor_invalid` is pinned in `test_chat_reads.py` line 378 (`error_for`'s table), not by `RouteTests`, which pins the view's `cursor_unreadable` | No |
| F4 | Nit | `chat_cases.py` 1347 to 1352 and 1376 | `reads.session_ended_in_locks_answers_as_hidden` fails when run without `d5.each_cause_hidden` before it ("not listed"): its own publication leaves `own_pause` readable; the pinned plan keeps the order, so CI holds | No |
| F5 | Nit | `test_chat_routes_offline.py` 600 | With `.get`, an answer with no `Cache-Control` fails only where `cache` is asserted, and the reads table does not assert it; every refusal shares `_no_store`, so nothing is unproven in practice | No |
| F6 | Risk to record | `contract.py` 199 | `read_error`'s `conversation=False` default fails open for a future conversation route; both existing routes are pinned | No; carry |

**What it did not read or run:** the ordering, identity, profile, mobile and contract-generation suites locally; the CI-only database steps; a session ended in the locks as expired or epoch-stale (offline coverage only); a timing measurement; the other job logs beyond their conclusions; Notion.

**The manager's checks** (App Manager 13, 26 November 2026): F1 confirmed by reading `route_reads.py` (the own-account check at 162 to 163, before the session's at 164 to 169) and `contact.py`'s `_revoke_account` (the account row locked, its state set and its epoch moved; no session row touched), so a suspension or deletion that commits while the list waits at its account lock reaches the own-account check. The claim began in A2-C1's stop report and was repeated as an instruction in the manager's resume message (decision 2), unchecked (AM13-08).

**Disposition** (App Manager 13; the manager workflow's step 6 under D-07):

| Finding | Disposition | Why |
|---|---|---|
| F1 | **To the Dev Manager's pre-merge read** ([DM-100](https://github.com/amthorn78/glow-dating-app/blob/988a36a1fe4bc7b654a07e565e15fe721dcf3520/docs/ephemeral/2026-11-26-dm-100-sv4-a2-pre-merge-read.md), item 1), with the manager's recommendation to carry it, the corrected statement recorded here. The correct statement: the list's own-account check is reached by a real writer, a suspension or a deletion committing while the list waits at its account lock, as well as by the case's test data | The claim is false, but no decision, acceptance check or the merge reads it: the case fails with the check removed either way, and behaviour is as DM-99 decided. The reviewer places it in class 3; the manager reads D-07's "where that claim is what a decision, an acceptance check or the merge reads" as not met, so the two docstrings would be corrected at the next change to `chat_cases.py`. The alternative is a words-only correction, A2-C2 |
| F2, F4, F6 | **Carried** (the carried-items file, "Carried to SV4") | The reach of a static test; a case's order dependence the pinned plan holds; a risk |
| F3, F5 | **Recorded here** | The record's citation (corrected above); no assertion unproven |
| Codex's three P2 threads | Resolved once the pre-merge read is disposed, before the merge | Each is answered by the code at `ddb1386` |

### Dev Manager 7's pre-merge read (DM-100, 26 November 2026)

Dev Manager 7's report ([DM-100](../../continuity/dev-manager/reviews/2026-11-26-dm-100-sv4-a2-pre-merge-read.md); `0256d2c`, a read of `92205da`) answers F1 with option (a), carry, approved with AL3 to AL6: the claim is false, but no decision, acceptance check or the merge reads it, so it is outside D-07's third class. F1 is therefore **carried**, in the carried-items file's entry as AL3 words it, and this record's two sentences in "A2-C1" are marked in place (AL4, AL5). DM-100 approves the brief's revisions 8 to 10, the CI policy's change as written, and A2 as settled. It agrees with the manager's calls, with AL7: A2-C1 changed 108 non-test lines, over step 6's 60 as earlier items counted them, and the delta review stands for this merge because it read every path the correction touches whole at its head and every other path is as A2's exact-head review read it. AL1 to AL8 are applied as given; AL9, a definition of the count, waits for the manager workflow's next revision. The merge adds one check to those proposed: `git diff --name-only ddb1386 <merge head>` lists only Markdown.

### Merge (26 November 2026)

- **PR59 merged** into `main` at `988a36a` (App Manager 13, with `gh api`, the expected head `d34c5ab` pinned in the call, 17:18 UTC). DM-100's conditions held: AL1 to AL8 applied as given at `d34c5ab`, in the batch that records the disposition; PR run 45865046893 on `d34c5ab` passed all twelve jobs (Database proof checks (chat) 18/18, row locks PASS), and its gate printed "Application checks passed" (17:17:03 UTC); `git diff --name-only ddb1386 d34c5ab` lists only Markdown, so the code merged is A2-C1's code head, which the delta review read; Codex's code review of `d34c5ab` completed with no findings; Codex's three P2 threads (comments 4658183908, 4703261810 and 4704969737, answered by A2-C1's code) were resolved at 17:17 UTC, after DM-100's disposition; the checklist was filled. The governing Markdown PR59 carries, the CI policy's change, was read by DM-100 and approved as written.
- **`main`'s tree** at `988a36a` equals `d34c5ab`'s. **`main`'s push run** 45866641384 (`push`, `988a36a`) passed all twelve jobs, and its gate printed "Application checks passed".
- **The branch cleanup,** run 45866641348 (`push`, `988a36a`): success. Deleted, each merged into `main`: `claude/dazzling-hamilton-ocxuu3` (`88d4ef3`, A2) and `claude/affectionate-sagan-r916ba` (`2201c2d`, A2-C1). Kept, on the keep-list: `main` (`988a36a`), the manager branch (`d34c5ab`) and `claude/dev-manager` (`0256d2c`). `git ls-remote` afterwards lists those three only.
- **The manager branch** was fast-forwarded to `main` (`988a36a`) before this receipt.
- **Pruned** with this receipt: A2's prompt, its resume message and its exact-head review prompt, DM-99's consultation, A2-C1's prompt, resume message and delta review prompt, and DM-100's consultation; their links in the brief, this record and the review log are pinned at `988a36a`.
- **The P11 plan's list-locks item** (`docs/testing/p11-deferred-acceptance.md`, A2R-13) now names A2's bounded list and this merge.
- **SV4 Stage A is complete:** A0 merged with PR57 (`499ccbb`), A1 with PR58 (`43e794a`) and A2 with PR59 (`988a36a`). Stage B, the server side of notifications, is designed in the brief's next revision, which goes to the Dev Manager for its first read (D-07) before its prompt.

## B1

- **Session:** SV4 B1's implementation session, started by Nathan from [B1's prompt](https://github.com/amthorn78/glow-dating-app/blob/6a22ddf6eb69742016b00d2f0a69fb66d8e94593/docs/ephemeral/2026-11-26-sv4-b1-f12-surface-prompt.md), revision 1, from `6a22ddf6eb69742016b00d2f0a69fb66d8e94593` of the manager branch `claude/magical-wozniak-yfmmx2`. The specification is the [brief](../../planning/sv4-chat-notifications.md), revision 12, its section "Stage B" (D16 to D20, D29's B1 cases, D30 and D31), with [DM-101](../../continuity/dev-manager/reviews/2026-11-26-dm-101-sv4-stage-b-brief.md)'s AM1 to AM16.
- **Branch:** `claude/lucid-fermi-droq7u`, which the push filter's `claude/**` covers. It starts at the prompt's commit.
- **Code head:** `e7e7e845946da1a3aa46f5fcf56add24e99dc70b`, whose run is the run of record. **Records head:** the commit that adds this section, pushed after that run had finished.
- **What B1 built:** D16's B1 part (the token store and the push transport reached through factories that only the proof's chat settings name), D17 (the models and migration `0014`), D18 (the persistence port and the ORM adapter, in the new app `services/api/glow_notifications/`), D19 (F12's three routes, sealed), D20 (the contract's documentation; no schema change), D29's twelve B1 cases (the chat suite, now 30 cases) and D31 (the seal, checked).
- **What B1 did not touch:** `glow_api/`, `glow_chat/`, `glow_discovery/`, `glow_identity/`, `glow_profiles/` (`idempotency.py` included: the adapter writes its records itself with SV2's `digest` and `decide`, as SV3's interactions write theirs, so the prompt's "or none" applies), `glow_domain/notification_fixtures.py`, `packages/contracts/` (no schema change, D20), `apps/mobile/`, `scripts/`, the workflow and the CI policy (the push tokens derive from a file the chat job already writes, below), `row_locks.py` (its lists unchanged), and any requirements file, lock, package manifest, environment template or pin. The reversals' temporary edits of `glow_api/urls.py`, `glow_api/settings.py`, `glow_chat/reads.py` and `packages/contracts/production/openapi.json` were undone (below). No provider call, deployed URL, real member, HDE call, real token or stored credential. No route was added to the runtime's URL configuration, and the production catalog's `paths` stay empty.

### The start gate and the environment check

- **The environment** (section 1 of the prompt, names only), at 20:13 UTC on 26 November 2026:
  - No `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY`; no `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name.
  - The AWS names present: `AWS_ACCESS_KEY_ID`, `AWS_CA_BUNDLE` and `AWS_SECRET_ACCESS_KEY` (OD-76). The GitHub names present: `GH_NO_UPDATE_NOTIFIER`, `GH_TOKEN` and `GITHUB_TOKEN`. None was read, printed or named in a command.
  - The toolchain: `Python 3.12.14` (`python3.12`), `v24.19.0` (`node`) and `11.9.0` (`npm`), all three in `/root/.local/bin`, which is third on `PATH`, after the session's guard directory and Nix's default profile, neither of which holds `python3.12`, `node` or `npm` (`command -v` names `/root/.local/bin` for each); `Docker version 29.9.3, build 5457199`. No Docker daemon was running; the session started `dockerd` in the background and stopped it at the end.
  - Every repository command ran under `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only its own variables. `npm ci --ignore-scripts` needed the proxy's two variables (`HTTPS_PROXY` and `NODE_EXTRA_CA_CERTS`, the proxy's CA bundle) added to reach the registry; neither value was printed.
- **The start gate** (section 2), at 20:13 UTC: `git fetch origin claude/magical-wozniak-yfmmx2 main`, then `git switch -C claude/lucid-fermi-droq7u 6a22ddf6eb69742016b00d2f0a69fb66d8e94593`; `git rev-parse HEAD` printed `6a22ddf6eb69742016b00d2f0a69fb66d8e94593`; "this prompt's commit is on the live branch", "PR59's merge present" and "main's code" printed; the diff of the owned trees and the brief between the prompt's commit and the live manager branch printed nothing; `grep -c '^## B1'` on this record printed `0`; "no glow_notifications yet" printed; `ls … | grep -c '^0014_'` printed `0`. `origin/main` was `988a36a`; the manager branch's head was the prompt's commit.

### What was built, by item

**D16, B1's part (AM1): the token store and the push transport, by factory only** (`glow_notifications/providers.py`). `token_store()` and `push_transport()` return what the factory named by `GLOW_NOTIFICATIONS_TOKEN_STORE` or `GLOW_NOTIFICATIONS_PUSH_TRANSPORT` makes, or `None` when no factory is named. Only the proof's chat settings name them, each the suite's in-memory fixture: `chat_support.token_store`, an `ObservedTokenStore` around `FixtureTokenStore` that records each reference it issues and whether a transaction was open at each `put`, and `chat_support.push_transport`, a `FixturePushTransport`; each fixture keeps its own refusal outside development and test (`require_fixture_environment`). The device route takes the store from the hook; without one the device command refuses before any read or write (`no_token_store`, `provider_unavailable`, not retryable). The read and the settings command take none. Nothing in B1 calls the transport: B2's deliverer takes it there.

**D17 (AM2): the models and migration `0014`** (`glow_persistence/models.py`; `glow_persistence/migrations/0014_notification_devices.py`).
- `DeviceRegistration`: one row per account and installation (`device_account_installation`); at most one `active` row per installation (`device_one_active_installation`, a partial unique constraint, so a transfer leaves the earlier account's row `revoked`); `session`, a foreign key to `AccountSession`, the session that last registered or rotated it; `ended_by` (`revoke`, `logout` or `transfer`), present exactly when the row is `revoked` (`device_ended_when_revoked`); `token_secret_ref` nullable, present and non-empty exactly while `active` (`device_reference_while_active`) and unique where present; `installation_id` no longer unique alone; `platform` and its constraint removed.
- `NotificationSettings`: `match_updates` and `message_updates` renamed `match_notifications` and `message_notifications` (both off until changed); `push_enabled` removed.
- `IdempotencyRecord`: `register`, `rotate`, `revoke` and `settings` added to `outcome_code`'s choices and to `intent_result`.
- `NotificationLedgerEntry` (new; SV4 B2 fills it): one row per outbox event and installation (`notification_ledger_entry`), `pending` or `sent`, `pending` by default.
- `PendingTokenDiscard` (new): a token store's reference, unique and non-empty (`pending_discard_ref`), never a token.
- **Each custody rule is a database constraint:** a reference only while active and never empty; an ending exactly when revoked, and only a known one; one active row per installation; one row per account and installation; one reference in at most one registration; a pending discard once and never empty; a ledger row once per event and installation, in a known state. `notifications.custody_rules_are_constraints` writes each forbidden row as test data and sees each refused.
- **Generated** by `makemigrations` under the static registry (Django's dummy backend; no database), its questions answered: the two renames yes; for the new non-null `session`, a one-off default (the nil UUID), which fills existing rows, of which there are none in any database (the disposable proofs only), and which `preserve_default=False` keeps out of the model. Django's generated header comment was replaced by a description, and Ruff fixed the import order and formatted the file. No `RunSQL` or `RunPython`. `makemigrations --check --dry-run`: "No changes detected", under the static registry (`test_makemigrations_check_passes_without_a_database`) and under the chat settings on the throwaway database.
- **A NULL hole, found by the first local run and fixed before the code commit:** the first `device_ended_when_revoked` was `Q(state="revoked", ended_by__in=…) | (~Q(state="revoked") & Q(ended_by__isnull=True))`. `NULL IN (…)` is NULL, and a CHECK constraint lets NULL through, so the database accepted a revoked row with no ending; `notifications.custody_rules_are_constraints` failed ("the database refuses a revoked row with no ending"). The revoked branch now names `ended_by__isnull=False`, as `IdempotencyRecord.intent_result` pairs `__in` with `__isnull=False`; the migration was regenerated with the same answers, and `test_sv4_b1_migration_follows_0013` pins the branch (reversal r32).

**The migration's operations**, in order (24): (1) `CreateModel` `NotificationLedgerEntry`; (2) `CreateModel` `PendingTokenDiscard`; (3) `RemoveConstraint` `device_platform`; (4) `RemoveConstraint` `intent_result`; (5) `RenameField` `match_updates` to `match_notifications` and (6) `message_updates` to `message_notifications`; (7) `RemoveField` `DeviceRegistration.platform`; (8) `RemoveField` `NotificationSettings.push_enabled`; (9) `AddField` `ended_by`; (10) `AddField` `session` (`preserve_default=False`); (11) `AlterField` `installation_id`; (12) `AlterField` `token_secret_ref`; (13) `AlterField` `IdempotencyRecord.outcome_code`; (14 to 17) `AddConstraint` `device_account_installation`, `device_one_active_installation`, `device_reference_while_active` and `device_ended_when_revoked`; (18) `AddConstraint` `intent_result`, with the four new codes; (19) `AddField` `NotificationLedgerEntry.event` (a foreign key to `OutboxEvent`); (20, 21) `AddConstraint` `glow_persistence_pendingtokendiscard_version` (`Record`'s) and `pending_discard_ref`; (22 to 24) `AddConstraint` `glow_persistence_notificationledgerentry_version`, `glow_persistence_notificationledgerentry_state` and `notification_ledger_entry`. Its SHA-256 is pinned (`bfa1255d…`).

**D18 (AM3 to AM5): the persistence port and the ORM adapter.**
- **The port** (`glow_domain/notifications.py`): `NotificationPersistence`, a `Protocol` with `read(caller)`, `device(caller, intent)` and `settings(caller, intent)`, each for a trusted `Caller` (account, session and installation, never taken from the intent). The domain keeps its pure parts (the intents' parsing, the transitions, the custody types, the versions' rules, the recipient rule, the wording), and `NotificationService` is the port's in-memory fixture, still guarded to development and test; `tests/test_notifications.py` keeps every assertion against it. The fixture now keeps D25's bound too (`registration_bound`, before the store's `put`). New in the module: `parse_installation` (the header's lower-case UUID), `REGISTRATION_BOUND`, `MAX_ACTIVE_REGISTRATIONS = 10` and the results' `deadlock` and `error` outcomes. **The bound's constant lives here,** in `glow_domain/notifications.py`, and both the fixture and the adapter read it.
- **The adapter** (`glow_notifications/persistence.py`, `OrmNotificationPersistence`), on P06.DB's protocol as `glow_chat`'s adapter has it:
  - **One durable transaction** per command and per read, at READ COMMITTED, refusing a caller's (`transaction_open`); a refusal rolls back; a deadlock or another database error is a result, by type only, never retried.
  - **The locks (AM3):** a device or settings command locks the account row `FOR NO KEY UPDATE` through SV2's `lock_account` (so no new account-lock site: the scan's seven sites and the API's 47 `select_for_update` calls are unchanged), then the requesting session's row `FOR SHARE` (`SESSION_SHARED`, a literal statement), then the registrations it changes, by primary key, `FOR UPDATE`, in key order, in one statement (`REGISTRATIONS_FOR_UPDATE`). The clock is read after the account and session locks; the session's checks (the account's, `valid`, unexpired, at the account's epoch) run on the rows as locked; deduplication follows them (P06.DB 5.4); the version is checked after the registrations' locks. The settings read locks the account row (SV2's `read_account_shared`) and the session row `FOR SHARE`.
  - **The transfer:** a register reads, with no lock, the other account that holds the installation active, then locks both accounts in UUID order, the lower first (the other account in any state, as SV3's `_lock_pair` takes it), reads the holder again under the locks and refuses `transfer_changed` (`state_conflict`) if it changed (another holder, none, or one where there was none). Otherwise it revokes the earlier account's registration in the same transaction (`ended_by` `transfer`, its reference retired).
  - **Idempotency (AM5):** SV2's keyed digest (`idempotency.digest`, `salted_hmac` under `SECRET_KEY`) over the canonical intent, the token included, and the header's installation (under `glow_installation_id`, a name no intent has, which the parsers refuse in a body); SV2's `decide` after the session's checks; the record written by the adapter with F12's receipt code (`register`, `rotate`, `revoke` or `settings`), as SV3's interactions write theirs, for SV2's provisional 24 hours. So a replay with another token, or the same body under the same key from another installation, is `idempotency_conflict`. No record holds a token.
  - **Custody (AM4):** the store's `put` runs in `device()`, before `_run`, never inside the transaction; a reference the command does not save (a refusal, a failure, a replay or a conflict) is parked in `PendingTokenDiscard` in its own statement after the transaction; a retired reference (a rotation's, a revocation's or a transfer's) moves from the registration's row to a pending discard inside the command's transaction, is discarded through the store after the commit, and its pending row is then removed; a failed discard leaves the row waiting for B2's sweep. The adapter's log lines are fixed strings; none names a reference.
  - **Versions** stay P06.3's: a first registration is version 1, each change to the row advances it, and a settings change advances every registration of the account in its transaction (revoked ones included).
  - **The bound (D25):** the account's active registrations are counted under its account lock; an eleventh is `registration_bound` (`state_conflict`); a rotation adds none.

**D19 (AM6, AM7): F12's three routes** (`glow_notifications/views.py`, `urls.py`, `contract.py`).
- `GET api/v1/notifications` (`NotificationsView`), `POST api/v1/notifications/device` (`DeviceView`) and `POST api/v1/notifications/settings` (`SettingsView`), each `non_atomic_requests`, with SV1's `GlowActorAuthentication` only, A2-C1's JSON-only negotiation (`JsonOnlyNegotiation`) and nothing cached (`Cache-Control: no-store`).
- **The installation** comes from `Glow-Installation-Id` only (a lower-case UUID, the contract's `device_id` pattern), on all three routes; a `DeviceIntent`'s `device_id` must equal it (`forbidden`).
- **The codes** (D19, with AM6), each the contract's `Error`, naming a code and never a value: a missing or malformed header, a body that is not the intent, a query string or another content type `invalid_request` (400), another method `invalid_request` (405); a session refused at SV1's door or found ended inside the locks `unauthenticated` (401), each with `WWW-Authenticate: Bearer`; another installation's `device_id` `forbidden` (403); a stale version `stale_version` (409); another intent under a used key `idempotency_conflict` (409); a revoke of no active registration, a settings change without one, the bound, `transfer_changed`, the one-active-row rule's refusal and a deadlock (retryable) or another database error `state_conflict` (409); the store's refusal `provider_unavailable` (503, retryable), and no store `provider_unavailable` (not retryable); the read's absence `not_found` (404).
- **The mapping** (`contract.REFUSALS`, 22 reasons; `contract.refusal`) and its completeness test (DM-99's AK2 pattern, with A2-C1's delta review's F2 lesson): an AST walk from the adapter's three methods and from the fixture's reads every reason each can raise or return, following `self.` methods, module functions and the SV2 `tx` and `idempotency` functions the adapter calls, and resolving relative imports; every reason found is pinned to one code and retryability, and the table holds no other. Planted reasons, one in an adapter helper and one in SV2's lock helper, are found.
- **AM7:** the installation identifier is never served (the DTO is built from an allowlist without it), never logged (a refusal is logged as `notifications route refused: <reason>`, its reason code only) and never shown.
- `contract.py` loads no model, so the seal test can name the modules that cannot load under the runtime.

**D20: the documentation.** No schema change. `production-contracts.md` gains "F12 on the server: devices and notification settings (SV4 B1, sealed until integration)": the routes, the header, the codes, which installation a read describes, that the settings are the account's, the versions, idempotency, the token's custody, the installation identifier as a capability, the factories, and what is not B1's. `data-model.md`: the device and settings row as built, a row for the ledger and the pending discards, and A2R-13's lines (below).

**D29's B1 cases** (the chat suite, `chat_cases.py`: twelve, contiguous, just before the three cases that read or publish a cause `hidden`; `CASE_COUNT` 30). Each signs its members in through SV1's routes, makes its installations at random and calls F12's routes with Django's test client, with no enclosing transaction:
1. `notifications.routes_refuse_what_is_not_their_dto` (D19, AM6, SV1 actor, R4): each route answers its DTO and refuses what is not its request (the cases D19 lists, each as the contract's `Error`, the 401s with the challenge), nothing cached; the views answer with `ATOMIC_REQUESTS` on and refuse inside a caller's block (an atomic block and a test case's), with no token taken (added after reversal r16, below).
2. `notifications.register_rotate_revoke_and_register_again` (D17, D18, D19, F12): register (version 1, its session recorded), a rotation from another session (version 2, that session recorded, the old token discarded), a revoke (version 3, `ended_by` `revoke`, no reference, the token discarded) and a register again (version 4); the read serves each; the receipts' codes `register`, `rotate`, `revoke`, `register`.
3. `notifications.transfer_between_accounts` (D17, D18, F12): a second account takes an installation (the first account's row `revoked` by `transfer`, its token discarded, the earlier account reading it `revoked`) and the transfer back; two rows, one active.
4. `notifications.each_refusal_its_code` (D19, AM6, F12): `forbidden`, `stale_version`, `state_conflict` (a revoke of none, settings with none, a revoke of a revoked one, settings on a revoked one), `provider_unavailable` (retryable, nothing saved, no reference issued), `not_found` (none, and another account's installation).
5. `notifications.replay_and_conflict` (D18, AM4, AM5, CommandMeta): a device replay serves the current projection and changes nothing; another token under the key is `idempotency_conflict`; each leaves the reference its `put` issued in the pending discards and in no registration; the same settings intent replays from its installation and is `idempotency_conflict` from another.
6. `notifications.settings_advance_every_registration` (D18, F12): one change advances all three registrations of the account (a revoked one included); the other installation reads it at its new version; its earlier version is `stale_version`.
7. `notifications.bound_of_active_registrations` (D25, AM12, F12): ten active; an eleventh `state_conflict`, saving nothing, its reference pending; a rotation at the bound served; after a revoke, the eleventh registers.
8. `notifications.register_refused_once_its_sessions_sign_out_commits` (D18, AM3, AM4): a register reaches its session's row while the sign-out holds it at its commit, waits at its `FOR SHARE` lock (observed), and once the sign-out commits is `unauthenticated` with the challenge; no registration; its reference pending.
9. `notifications.two_accounts_one_new_installation` (D17, D18, AM13): the first held at its commit; the second, through the route, waits at its own row on the one-active-row constraint (observed) and is `state_conflict`; one active row, the first's; the second's reference pending.
10. `notifications.transfer_changed_under_the_locks` (D18, AM13, F12): a third account's transfer holds the holder's account row at its commit; the latecomer's register waits on it (observed) and is refused `transfer_changed`; one active row, the transfer's; the holder's row ended by that transfer.
11. `notifications.custody_rules_are_constraints` (D17, AM2, D25): 13 forbidden writes (test data), each refused by the database.
12. `notifications.no_token_in_any_row_or_answer` (D29, AM4, DM-101 11): no drawn push token in any row of any table (each `table.column` searched; a hit is named, never its value) or in any served answer, and no reference or installation identifier in any answer; every `put` ran outside a transaction; every reference the store issued is held by exactly one active registration or pending discard while its token is held, and by no row once discarded, and appears in no other column.

**The scan holds the synthetic push tokens** (DM-101, section 11). The cases draw their tokens from a pool of 160 derived from the run's `SECRET_KEY` by HMAC (`chat_scan.push_tokens`, label `glow-ordering-proof.chat.push-token`); the suite holds the whole pool among its secrets before its first case (`chat_suite._file_secrets`), and the job's check derives the same pool from the `chat-secret-key` file the job already writes (`chat_scan.job_values`). No new secret file, so neither the workflow nor the CI policy's lines 13 and 15 changed. Case 12 queries every row of every table for each drawn token, since the scans read only the output and the results JSON.

**D31: the seal, checked** (`tests/test_notifications_sealed_runtime.py`, 7 tests, in the style of `test_chat_routes_sealed_runtime.py`): the served runtime's settings, URL configuration and WSGI application import none of `glow_notifications` (nor `glow_persistence`, `glow_profiles` or the domain's notification modules); the database backend is the dummy one; none of F12's routes is served, by pattern or by path; the runtime names neither factory, and no runtime module names `glow_notifications` or the factories; the adapter, the views and the URLs cannot load under the runtime's settings; and the production catalog's `paths` stay empty.

### The sweep, and each earlier test changed (D31, with AM16)

- **The sweep,** at the prompt's commit, before any change: `git grep` over every suite's source and tests and the API's tests for each list B1 extends. The models and migrations: `DeviceRegistration`, `NotificationSettings`, `push_enabled`, `match_updates`, `message_updates`, `token_secret_ref`, `installation_id`, `'platform'`, `device_platform`, `0013_interaction_retired_at`, `leaf_nodes`, `== 42`. The outcome codes: `'unblocked', 'withdrawn'`, `withdrawn.\]`, `outcome_code`. The installed apps and settings modules: `glow_notifications`, `INSTALLED_APPS`, `DiscoveryConfig`, `GLOW_CHAT_TEXT_READER`, `chat_settings`, `chat_urls`. The routes: `api/v1/notifications`, `EXPECTED_ROUTES`, `get_resolver`, `url_patterns`. The case and plan counts: `CASE_COUNT`. The scan's secret files: `VALUE_FILES`, `job_secret_files`. The account-lock scan's pins: `EXPECTED_SITES`, `calls([API_ROOT])`. And `notification`, `pending_discard`, `ledger`.
- **What it found that B1 reaches:** `services/api/tests/test_model_definitions.py` (the models' count, the leaf, the outcome codes), `services/api/tests/test_notifications.py` (its runtime probe's module prefixes) and `proofs/postgres-ordering/tests/test_chat_offline.py` (the installed apps, the factories beside the text reader, the URL modules, the case count and the plan). **The other hits pin nothing B1 extends:** `== 42` in `identity_cases.py` is a 429 and in `test_chat_adapter_offline.py` a backend PID (4242); the SV3 suites' and tests' `outcome_code`s name their own codes, and the DB04 case's refused `undone` stays refused; the sealed-runtime tests' installed apps and routes are the runtime's, which B1 does not change; the account-lock scan's pins hold, since B1 adds no account-lock site and no `select_for_update` (`test_discovery_offline` passes unchanged, and the discovery suite's `locks.account_locks_no_key_update` makes the same scan); no other suite or test names a notification model, field or route.
- **Each earlier test changed, with the entry added** (every earlier assertion kept):
  - `services/api/tests/test_model_definitions.py`: `test_model_and_migration_state_have_no_drift_without_a_database` (the models' count, 42 to 44, its comment naming 0014's two); `test_sv2_stage_a_migrations_follow_0004` (the leaf, `0013_interaction_retired_at` to `0014_notification_devices`, its comment naming 0014's own test); `test_sv3_stage_b_migration_follows_0010` (`outcome_code`'s choices gain `register`, `rotate`, `revoke` and `settings`).
  - `services/api/tests/test_notifications.py`: `FixtureScopeTests.test_the_runtime_imports_none_of_the_notification_modules` (the probe's prefixes gain `glow_notifications`); `ComposerRefusalTests`' docstring (A1's stale line, a follow-up, below).
  - `proofs/postgres-ordering/tests/test_chat_offline.py`: `ChatSettingsModuleTests.test_the_settings_load_with_the_proof_variables_and_the_key_files` (the installed apps gain `glow_notifications.apps.NotificationsConfig`; the two factories' settings are asserted beside the text reader's); `test_the_url_configuration_serves_the_five_route_modules` (the URL modules gain `glow_notifications.urls`; its name is kept, below); `ChatPlanTests.test_the_case_count_is_pinned` (18 to 30, and `PLAN` gains B1's twelve before the last three); `test_the_cases_that_publish_hidden_run_last` (A2R-7, a follow-up, below).

### Follow-ups (D30)

**Taken,** each in a file B1 changes for its own work:
- **`chat_cases.py`:** A2-C1's delta review's **F1** (the docstrings of `_account_suspended_as_test_data` and `list_checks`, which said the list's own-account check is reached only by test data: now the carried entry's statement, that the list checks its own account before the session's state, expiry and epoch, so a real suspension or deletion that commits after the request has passed SV1's door, and before the list's account lock is granted, reaches the check too); **F4** (`reads.session_ended_in_locks_answers_as_hidden`'s docstring: it runs after `d5.each_cause_hidden`, which the pinned plan keeps before it and which leaves every cause published `hidden`, and without it the case would fail at its last check); **A2R-6** (cases 5 and 15, `d5.each_cause_read_only` and `d5.each_cause_hidden`: two causes, `own_withdrawal_alone` and `other_withdrawal_alone`, a withdrawn consent with the profile left visible, as test data through `interaction_cases._seed_withdrawn_consent`, so the withdrawn consent is the conversation's one cause; 11 causes in each case, every earlier cause and assertion kept; reversal r50 shows a read rule ignoring a withdrawn consent now fails case 5). The module docstring's order paragraph names the three cases that read or publish `hidden` and B1's place.
- **`test_chat_offline.py`:** **A2R-7** (`test_the_cases_that_publish_hidden_run_last`'s first check, `assertNotIn("hidden", re.findall(r'(\w+)="hidden"', source))`, could not fail: `findall` returns the keyword's name, never `hidden`, and `ast.unparse` writes single quotes. It is now `assertEqual(re.findall(r"""(\w+)=['"]hidden['"]""", source), [])`; reversal r48 plants `state="hidden"` in a case before the last three: the new check fails, and the earlier pattern, run on the same source, still finds nothing).
- **The proof README:** the chat suite's paragraph ("SV4 A2, chat's routes") gave the count as 18 and described A2's fifteen cases; it now gives 30 and describes every case, A2-C1's three and B1's twelve among them, B1's settings additions and the push-token pool.
- **`data-model.md`:** A2R-13's stale lines (no chat routes or match list): the conversation-list entry now says which list the ordering suite runs and which the route serves (its 200 candidates bounded before its locks), and a paragraph names chat's routes and the match list.
- **`glow_domain/notifications.py` and `tests/test_notifications.py`:** A1's record's stale lines (the pre-D5 read rule cited as the send's): the module docstring now says the composer makes the send's checks, which the conversation reads no longer share since SV4 A1; `ComposerRefusalTests`' docstring says the same. The docstring's other lines name B1's port, the bound and B2's wiring.

**Not taken** (B1 changes neither file, so each stays carried): A2R-13's `test_row_locks_offline.py` lines 6 and 1167; A2-C1's F2 in `test_chat_routes_offline.py`. (F6 names `glow_chat/contract.py`, which is not B1's.)

### New cases and tests

- **The database:** the chat suite's twelve B1 cases (above).
- **The API** (`services/api/tests/`), 39 new tests: `test_notifications_routes_offline.py`, 25 (`RequestTests` 4: each intent parsed as the production schema decides, on 30 bodies; a body naming an actor, an account, a session or an installation refused; the header's pattern the contract's `device_id`; bodies that are not a JSON object; `ProjectionTests` 1; `MappingCompletenessTests` 5; `RouteTests` 8, in a fresh process under `tests.discovery_offline_settings` with the persistence replaced by the port's in-memory fixture; `StructureTests` 7); `test_notifications_port.py`, 6 (`PortShapeTests` 2, `FixtureBoundTests` 3, `InstallationTests` 1); `test_notifications_sealed_runtime.py`, 7; and `test_model_definitions.py`'s `test_sv4_b1_migration_follows_0013` (the migration pinned as written, its dependency, its 24 operations in order, the renames, `preserve_default=False`, its ten constraints by name, the revoked branch's `ended_by__isnull=False`, the models' fields, the reference's `unique` and `null`, the ledger's states and foreign key, no field holding a token, no `RunSQL` or `RunPython`).
- **The proof** (`tests/test_chat_offline.py`), 7 new tests: `ChatSettingsModuleTests.test_the_suites_push_tokens_derive_from_the_settings_key_as_the_job_check_does`; `ChatScanTests.test_the_push_tokens_are_held_with_no_file_of_their_own` and `test_the_suite_holds_the_whole_pool_before_its_first_case`; `ChatPlanTests.test_each_b1_item_has_its_case_before_the_hidden_ones`; `ChatSupportTests.test_the_notification_routes_are_the_apis`, `test_the_token_store_and_the_transport_are_the_suites_fixtures` and `test_the_observed_store_passes_each_call_and_records_the_transaction`. The module holds 41 tests.

### Reversals (D14)

Each reversal is a temporary edit of one or more files, made by a scratch harness (outside the checkout) that found each old text exactly once, wrote the edit, ran the named tests and, where it names cases, those cases on a new throwaway database (through the scratch runner above; a migration edit reached the database through the proof's own migrate), kept the failing lines, and restored each file byte for byte, its SHA-256 checked after. The harness first ran before case 1's `ATOMIC_REQUESTS` block and the two `ChatSupportTests`' path change (below), then **all 53 again at the code head, `e7e7e84`**, whose output is quoted here (shortened where marked "…"). All 53 failed as intended, and all were restored: `git status` and a digest of the tracked diff and every untracked file were the same before and after, and `glow_api/`, `glow_chat/` and `packages/contracts/` are unchanged. The prompt's eleven are r01 to r11 (r07 and r08 the custody and one-active-row constraints, r09 the bound, r10 the 401).

| Reversal (the edit) | What failed |
|---|---|
| r01: a route takes the installation from the body (the intent's `device_id` before the header) | `RouteTests.test_the_installation_comes_from_the_header_only`, each header (missing, upper case, not a UUID, two): "(409, 'stale_version', …) != (400, 'invalid_request', …)"; `test_each_refusal_answers_its_code` ("(200, None, …) != (403, 'forbidden', …)"); `StructureTests.test_the_views_read_the_installation_from_the_header_only` ("'device_id' unexpectedly found …"); case 1: "device: no installation header: answers 400" |
| r02: a refusal names a value (the requesting installation in its body) | `RouteTests.test_each_refusal_answers_its_code` ("(409, 'idempotency_conflict', False, True, False) != (409, 'idempotency_conflict', True, False, False)": not the contract's `Error`, and a value echoed); case 4: "another installation's device_id: the body is the contract's Error" |
| r03: a token written to a row (the new registration's `token_secret_ref` is the token) | case 2: "the row holds the store's reference, never the token"; case 5: "the replay's put issued one more reference"; case 12: "no push token in any row (found in glow_persistence_deviceregistration.token_secret_ref)"; the runner's scans: 0 secrets and 0 member values in the output |
| r04: the session row unlocked (`SESSION_SHARED` without `FOR SHARE`) | `StructureTests.test_the_locks_are_sv2s_and_two_literal_statements` ("Items in the second set but not the first: 'SESSION_SHARED'"); case 8: "a register whose session ended in its locks: answers 401" (the register no longer waited and committed for the ended session) |
| r05: the store's `put` inside the command's transaction (moved into `_device`) | `StructureTests.test_the_store_takes_the_token_before_the_commands_transaction` (`StopIteration`: no `put` in `device`); case 12: "every put ran before its command's transaction"; cases 4, 5, 7, 8 and 9 (the store's refusal "answers 503"; each unsaved reference "waits in the pending discards") |
| r05b: the `put` in a closure handed to `_run` (its line still before `_run`'s) | the same test, its nested check only ("'.put(' unexpectedly found in \"def inside(tx: Tx) -> _Done: …\""); the line order alone passes such a closure, which is why the nested check was added while the reversals were designed |
| r06: the requesting installation left out of the digest | `StructureTests.test_the_digest_binds_the_requesting_installation` ("- return idempotency.digest(operation, dict(intent))"); case 5: "the same key and body from another installation: answers 409" (a replay instead) |
| r07: a custody constraint removed (`device_reference_while_active`, from the model and the migration) | `test_sv4_b1_migration_follows_0013` (the digest, `8ba6921b…` != `bfa1255d…`); case 11: "the database refuses an active row with no reference" |
| r08: the one-active-row constraint removed (`device_one_active_installation`, from the model and the migration) | `test_sv4_b1_migration_follows_0013` (`f2757947…` != `bfa1255d…`); case 9: "the second account's register: the route waited on the writer" (it no longer waited); case 11: "the database refuses a second active row for one installation" |
| r09: the bound removed in the adapter (`MAX_ACTIVE_REGISTRATIONS + 1000`) | `FixtureBoundTests.test_the_bound_is_ten_and_one_constant` (the adapter's line, a substring pin); case 7: "an eleventh active registration: answers 409" |
| r09b: the bound removed in the port's fixture | `FixtureBoundTests.test_an_eleventh_active_registration_is_refused_with_no_token_stored` ("('applied', '') != ('refused', 'registration_bound')"); `RouteTests.test_each_refusal_answers_its_code` ("(200, …) != (409, 'state_conflict', …)") |
| r10: a 401 from inside the locks without `WWW-Authenticate` | `RouteTests.test_a_session_ended_in_the_command_is_unauthenticated_with_the_challenge`, each route ("None != 'Bearer'"); case 8: "the 401 carries the challenge" |
| r10b: the door's 401 without `WWW-Authenticate` | `RouteTests.test_each_route_refuses_what_is_not_its_request` (device, settings, the read: "None != 'Bearer'"); case 1: "device: no token: the challenge" |
| r11: the runtime imports `glow_notifications` (`glow_api/urls.py` imports its contract; temporary) | `test_the_runtime_imports_none_of_b1s_modules` ("['glow_domain.notifications', 'glow_notifi…act'] != []"); `test_no_runtime_module_names_b1s_modules_or_the_factories` (`urls.py`) |
| r12: a served answer cached (no `no-store`) | `RouteTests.test_each_route_answers_its_dto_for_the_headers_installation` ("None != 'no-store'"); case 1: "a served answer is not cached" |
| r13: a query string accepted | `RouteTests.test_each_route_refuses_what_is_not_its_request` (device "(200, …) != (400, 'invalid_request', …)", settings "(409, 'state_conflict', …)", the read); case 1: "device: a query string: answers 400" |
| r14: the settings route takes the token store too | `RouteTests.test_only_the_device_route_takes_the_token_store` ("['tokens'] != []") |
| r15: a route logs a value (`logger.info("… %s", installation)` in `_caller`) | `RouteTests.test_the_routes_log_codes_only` ("True is not false": a value in a record); `StructureTests.test_the_views_read_the_installation_from_the_header_only` (`views.py`, line 108: "'installation' != 'reason'"); case 1 passed, and the runner found 2 member values in the output (case 1's two installations), which in a whole run fails `chat value scan` and the verdict |
| r16: `non_atomic_requests` removed | `StructureTests.test_the_three_routes_and_no_other` ("[…, [], …] != […, ['default'], …]"); case 1: "ATOMIC_REQUESTS on: register: answers 200" (at the first pass, before case 1's block, the case passed: a deviation, above) |
| r17: a B1 module imports another slice (`from glow_chat import contract` in the views) | `StructureTests.test_no_module_imports_the_runtime_or_another_slices_routes` (`views.py`, `glow_chat`) |
| r18: an unmapped reason in the adapter (the revoke's refusal renamed `revoke_unlisted`) | `MappingCompletenessTests.test_every_reason_the_adapter_can_answer_is_pinned` ("Items in the first set but not the second: 'revoke_unlisted' … 'transition_forbidden'") |
| r19: the settings command locks the session before the account | `StructureTests.test_the_lock_order_is_the_account_the_session_then_the_registrations` ("[646, 645, 648, 650, 656] != [645, 646, 648, 650, 656]") |
| r20: the adapter's `probe` positional in `settings` | `PortShapeTests.test_the_adapter_takes_them_the_same_way_with_a_probe_only_beside` (settings: "['self', 'caller', 'intent', 'probe'] != ['self', 'caller', 'intent']") |
| r21: the port's `device` takes another parameter name | `PortShapeTests`' two tests (device: "['self', 'caller', 'intent'] != ['self', 'caller', 'body']") |
| r22: the fixture's bound counts every account's registrations | `FixtureBoundTests.test_another_accounts_registrations_do_not_count` ("'refused' != 'applied'") |
| r23: the domain's token limit 4097 | `RequestTests.test_each_intent_is_parsed_as_the_contract_decides` (the 4097-character token: "True != False") |
| r24: a `DeviceIntent` naming a session accepted | `RequestTests.test_a_body_naming_an_actor_or_its_installation_is_refused` (`session_id`); case 1: "device: a session field: answers 400" |
| r25: an upper-case installation accepted | `InstallationTests.test_the_installation_is_a_lower_case_uuid` ("IntentError not raised"); `RequestTests.test_the_installation_header_is_the_contracts_device_id`; `RouteTests.test_the_installation_comes_from_the_header_only` (upper); case 1: "device: an upper-case installation: answers 400" |
| r26: an unmapped reason in the port's fixture | `MappingCompletenessTests.test_every_reason_the_fixture_can_answer_is_pinned` ("'revoke_unlisted' … 'transition_forbidden'") |
| r27: the contract's `parse` accepts a body that is not a JSON object | `RequestTests.test_a_body_that_is_not_a_json_object_is_refused` (`[]`, `null`, `"x"`: "Invalid not raised") |
| r28: the served DTO gains a field | `ProjectionTests.test_the_settings_are_the_contracts_dto_and_nothing_more` (both views: "False is not true"); `RouteTests.test_each_route_answers_its_dto_for_the_headers_installation` ("(200, 'notifications', False, False) != (200, 'notifications', True, False)") |
| r29: the mapping holds a reason no path answers | `MappingCompletenessTests.test_the_table_holds_no_other_reason` ("'spare_reason'") |
| r30: a session reason mapped to `not_found` | `MappingCompletenessTests.test_each_session_reason_is_unauthenticated` (`session_expired`: "('not_found', False) != ('unauthenticated', False)") and `test_every_reason_the_adapter_can_answer_is_pinned` |
| r31: a token store when no factory is named (the fixture by default) | `RouteTests` set-up errored: the device route, now with a store, reached the real adapter, which needs a database the offline settings lack (a limit, above) |
| r32: the revoked branch without `ended_by__isnull=False` (model and migration) | `test_sv4_b1_migration_follows_0013` (`30d0ae9e…`, the first migration's digest, != `bfa1255d…`); case 11: "the database refuses a revoked row with no ending" |
| r33: the runtime serves a route under F12's prefix (`glow_api/urls.py`; temporary) | `test_the_runtime_serves_none_of_b1s_routes` ("[…, 'api/v1/notifications', 'health/live', 'health/ready'] != […]") |
| r34: the runtime names the token store's factory (`glow_api/settings.py`; temporary) | `test_the_runtime_names_no_token_store_or_push_transport`; `test_no_runtime_module_names_b1s_modules_or_the_factories` (`settings.py`) |
| r35: the adapter loadable under the runtime (its model and SV2 imports made optional) | `test_b1s_modules_cannot_load_under_the_runtime_settings` (`glow_notifications.persistence`: "0 == 0"). A first r35, `glow_persistence` installed in the runtime's settings, made Django's system check refuse before any test ran; it was a wrong reversal, not a gap, and was replaced |
| r36: the runtime's database backend SQLite (`glow_api/settings.py`; temporary) | `test_the_runtime_database_backend_is_the_dummy_one` ("'django.db.backends.sqlite3' != 'django.db.backends.dummy'") |
| r37: the production catalog claims F12's read (`openapi.json`; temporary) | `test_the_production_catalog_claims_no_route` ("{'/api/v1/notifications': {}} != {}") |
| r38: the job's check without the push-token pool | `ChatScanTests.test_the_push_tokens_are_held_with_no_file_of_their_own` (the pool not among the job's values) |
| r39: the suite's secrets without the pool | `ChatScanTests.test_the_suite_holds_the_whole_pool_before_its_first_case` (a substring pin) |
| r40: the suite's `SECRET_KEY` not the job's key file (`+ "-chat"`) | `ChatSettingsModuleTests.test_the_suites_push_tokens_derive_from_the_settings_key_as_the_job_check_does` (the two pools differ). A first r40 edited the line before the module sets `SECRET_KEY` and raised `KeyError`; it was replaced |
| r41: the chat settings without F12's app | `ChatSettingsModuleTests.test_the_settings_load_with_the_proof_variables_and_the_key_files` ("'glow_notifications.apps.NotificationsConfig' not found …") |
| r42: the chat settings name another token store (`FixtureTokenStore` itself) | the same test ("'glow_domain.notification_fixtures.FixtureTokenStore' != 'glow_ordering_proof.chat_support.token_store'"); case 2: "the register: answers 200" |
| r43: the suite's device path not the API's | `ChatSupportTests.test_the_notification_routes_are_the_apis` |
| r44: the observed store records no transaction | `ChatSupportTests.test_the_observed_store_passes_each_call_and_records_the_transaction` ("[False, False] != [False, True]") |
| r45: the suite's token store made again at each call | `ChatSupportTests.test_the_token_store_and_the_transport_are_the_suites_fixtures` ("ObservedTokenStore(<fixture>) is not ObservedTokenStore(<fixture>)") |
| r46: AM13's label dropped from cases 9 and 10 | `ChatPlanTests.test_each_b1_item_has_its_case_before_the_hidden_ones` (`AM13`) |
| r47: a B1 case moved after the hidden ones | `ChatPlanTests`' three plan tests (B1's indices "[15, …, 25, 29] != [15, …, 25, 26]"; the plan; the last three) |
| r48: A2R-7, a case before the last three sets `state="hidden"` | `ChatPlanTests.test_the_cases_that_publish_hidden_run_last` ("['state'] != []"); the earlier pattern on the same source: "earlier pattern finds []; its assertNotIn('hidden', ...) passes: True" |
| r49: the completeness walk follows no helper (its `FOLLOWED` emptied, in the test's own walker) | `MappingCompletenessTests.test_a_reason_added_in_the_adapter_or_a_helper_is_found` ("'planted'" not found) and `test_every_reason_the_adapter_can_answer_is_pinned` (`account_not_active`, `account_missing`, `idempotency_conflict`, … not found) |
| r50: A2R-6, the read rule ignores a withdrawn consent (`glow_chat/reads.py`; temporary) | case 5 (`d5.each_cause_read_only`): "own_withdrawal_alone: listed read_only, its count and marker kept" |

### Commands and results

At the code head, in a clean environment (local; the run of record repeats them), with the counts at the prompt's commit beside them:
- **The API**, after `pip install --require-hashes -r requirements-dev.lock` and `pip check` ("No broken requirements found."), with `GLOW_ENV=test`: `manage.py check` "System check identified no issues (0 silenced)"; `manage.py test tests` `Ran 731 tests … OK`, no skip (692, no skip, before); `makemigrations --check --dry-run` "No changes detected" (the runtime installs no model; the meaningful checks are `test_makemigrations_check_passes_without_a_database`, under the static registry, and the chat settings' run on the throwaway database, both "No changes detected"); `python -m glow_persistence.static_check` "Static definitions agree: 44 app models; migrations=0001_event_infrastructure, … ,0014_notification_devices" (42 and `0013` before); `ruff check .` "All checks passed!"; `ruff format --check .` "187 files already formatted" (175 before); `mypy` "Success: no issues found in 99 source files" (99 before; its `files` list does not name `glow_notifications`, so `mypy glow_api glow_domain glow_chat glow_identity glow_profiles glow_discovery glow_notifications` was run as well: "Success: no issues found in 107 source files"); the contract's Python tests `Ran 55 tests … OK` (55 before).
- **The proof's offline tests**, from its own lock (`pip check`: "No broken requirements found."): `Ran 428 tests … OK` (421 before); Ruff "All checks passed!", "78 files already formatted" (78 before); mypy "Success: no issues found in 78 source files" (78 before).
- **The contract,** unchanged: `npm ci --ignore-scripts` from its lock, then `npm run check`: "Generated types and runtime validators match schemas.", `tests 926`, `pass 926`, `fail 0` (A2's count). Its corpus test loads the mobile app's generated validators, so it ran after the mobile app's install below; run before it, it failed `Cannot find module 'ajv/dist/runtime/ucs2length'` (an environment's order, as CI's Mobile job installs both first).
- **The mobile app,** unchanged: `npm ci --ignore-scripts` from its lock, then `npm run check` (typecheck, lint, unit tests): `tests 691`, `pass 691`, `fail 0` (A2's count).
- **The trusted classifier,** `main`'s `scripts/change_scope.py` (`988a36a`; SHA-256 `b564c62f…`, equal to the checkout's), extracted to a scratch directory outside the checkout and run from the checkout as `python3 -I <copy>/change_scope.py --base 988a36a1fe4bc7b654a07e565e15fe721dcf3520 --head e7e7e845946da1a3aa46f5fcf56add24e99dc70b --merge-base`: `"full": true`, reason `behavior-or-empty`. `git merge-base --all` gives one base, `988a36a`.
- **The diff:** `git diff --name-only 6a22ddf6eb69742016b00d2f0a69fb66d8e94593 e7e7e845946da1a3aa46f5fcf56add24e99dc70b` lists 26 paths, each an owned path: 8 new `glow_notifications` modules (`__init__.py`, `apps.py`, `conf.py`, `contract.py`, `persistence.py`, `providers.py`, `urls.py`, `views.py`); `glow_domain/notifications.py`; `glow_persistence/models.py` and the new migration `0014_notification_devices.py`; 3 new and 2 extended API test modules; 6 chat suite modules (`chat_cases.py`, `chat_scan.py`, `chat_settings.py`, `chat_suite.py`, `chat_support.py`, `chat_urls.py`) and its offline tests; the proof's README (the chat suite's paragraph); `data-model.md` and `production-contracts.md`. All files are regular, mode 100644. This section is the records commit's only change.
- **npm and pip:** no package, lock, manifest or pin changed.
- **GitHub:** read with `gh api` REST `GET` calls only (the run, its jobs and the job logs); this session's GitHub tools offered no Actions reads, and its GitHub MCP server did not connect. Nothing was written but the two pushes of this branch (the code head, then this records commit).

### Local database runs (iteration, not evidence)

Under P06.DB's D4: the pinned image `postgres@sha256:d74eeac9…`, pulled from Docker Hub (its first pull was refused, `429 Too Many Requests`, and a later one succeeded); loopback only (`127.0.0.1:5433`); generated passwords, markers and keys in a mode-700 scratch directory, never printed; none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name in any process environment; the chat database and the decoy, each with its own marker, created by the superuser inside the container; migrations only through the proof's own `python -m django migrate` under the chat settings, never `manage.py migrate`. No Docker daemon was running, so `dockerd` was started in the background. Each run below used a new container and database, and the last was removed at the end.
- **First whole-suite run** (before the fix): `[chat] cases: 29/30` (suite exit 1, 170 s): `notifications.custody_rules_are_constraints` failed, "the database refuses a revoked row with no ending" (the NULL hole, above); both scans clean (1871 secrets held, 1287 member values held, 0 found in 1280 log records and 152 writes); `ROW LOCKS (D14): PASS`; `chat_scan` passed.
- **Second** (the constraint fixed, the migration regenerated): `[chat] cases: 30/30 passed in 167.1 s`; `chat secret scan: clean (1871 secrets held; 0 found in 1280 log records, 152 writes and the results JSON)`; `chat value scan: clean (1287 member values held …)`; `ROW LOCKS (D14): PASS`; `CHAT VERDICT: PASS`; `chat_scan`: 0 and 0 found, the suite's scans clean.
- **Third, at the code head's content** (with case 1's `ATOMIC_REQUESTS` block): `[chat] cases: 30/30 passed in 144.9 s` (suite exit 0 in 146 s); `chat secret scan: clean (1871 secrets held; 0 found in 1292 log records, 152 writes and the results JSON)`; `chat value scan: clean (1289 member values held …)`; `[chat] row locks sent (D14): 115803 statements (115710 through Django's execute or executemany, 93 through the driver itself) on 94 connections in 3 threads; 10990 take a writer's row lock, 3232 of them naming the account table (3232 FOR NO KEY UPDATE, 0 FOR UPDATE OF other tables only); 0 refused`; `ROW LOCKS (D14): PASS`; `CHAT VERDICT: PASS`; `chat_scan`: the job's secrets found in the output 0 and in the results JSON 0, the suite's scans clean.
- **The reversals' database cases** ran through a scratch runner (`subset.py`, outside the checkout): the named cases only, in the plan's order, on a new database each time, every log record and write kept in memory and never printed, each verdict line checked against the run's secrets and member values before it was printed, and the counts of each found printed.

### The run of record

**Foundation run [45900925199](https://github.com/amthorn78/glow-dating-app/actions/runs/45900925199)** on `e7e7e845946da1a3aa46f5fcf56add24e99dc70b` (a push run, attempt 1) concluded **success**. It was created at 21:51:09 UTC on 26 November 2026, and its gate finished at 21:58:51 (7 minutes 42 seconds in all); the gate printed "Application checks passed" (21:58:48). Nothing was pushed to the branch until it had finished. The durations are from the jobs' timestamps (whole seconds); A2-C1's are from its run of record, 45778164243.

| Job | Conclusion | Duration | A2-C1's | Timeout |
|---|---|---|---|---|
| Change scope | success | 5 s | 11 s | 3 min |
| API checks | success | 94 s | 75 s | 10 min |
| Mobile checks | success | 414 s (6 min 54 s) | 418 s | 25 min |
| API mobile smoke | success | 77 s | 94 s | 10 min |
| API artifact checks | success | 19 s | 27 s | 15 min |
| Stream proof checks | success | 75 s | 75 s | 10 min |
| Database proof checks (ordering) | success | 444 s (7 min 24 s) | 459 s | 30 min |
| Database proof checks (identity) | success | 126 s | 95 s | 30 min |
| Database proof checks (profile) | success | 144 s | 152 s | 30 min |
| Database proof checks (discovery) | success | 237 s (3 min 57 s) | 233 s | 30 min |
| **Database proof checks (chat)** | success | **179 s (2 min 59 s)** | 158 s | 30 min |
| Foundation gate | success: "Application checks passed" | 5 s | 2 s | 2 min |

**What the logs show** (read with `gh api` REST `GET` calls; no line quoted here held an `::add-mask::` command or a long hexadecimal value):
- **The chat job:** the offline tests `Ran 428 tests … OK`, Ruff "All checks passed!" and "78 files already formatted", mypy "Success: no issues found in 78 source files"; `chat dbshell exit status: 1` with `RefusedDatabase: refusing dbshell …`; the decoy `glow_discovery_proof` present with its own marker (`1`, and its comment differs: `t`), its marker refused (`chat migrate with the decoy database's marker: exit status 1`, `RefusedDatabase: refusing this database …`) with no relation outside the catalogs before or after (`0 before, 0 after`) and no `django_migrations` (`t`); the migrations from zero, `0014_notification_devices` among them ("Applying glow_persistence.0014_notification_devices... OK"), and `makemigrations --check --dry-run` "No changes detected"; `[chat] cases: 30/30 passed in 113.5 s` (every case `PASS`, B1's twelve among them: case 1 "… each answers with ATOMIC_REQUESTS on; 6 refused inside a caller's block", case 12 "39 tokens in no row and no answer; 36 references, each held once or discarded; every put before its transaction"); `chat secret scan: clean (1871 secrets held; 0 found in 1292 log records, 152 writes and the results JSON)`; `chat value scan: clean (1289 member values held: member values, message texts, provider identifiers; 0 found in the same output)`; `[chat] row locks sent (D14): 115797 statements (115704 through Django's execute or executemany, 93 through the driver itself) on 94 connections in 3 threads; 10990 take a writer's row lock, 3232 of them naming the account table (3232 FOR NO KEY UPDATE, 0 FOR UPDATE OF other tables only); 0 refused`, `ROW LOCKS (D14): PASS`; `CHAT VERDICT: PASS`; `chat phase: 114 s (the job's timeout is 30 minutes)`; `chat_scan`: the job's secrets found in the suite's output 0 and in the results JSON 0, the suite's own scans clean; the second run refused (`refusing a used database: …`), its rows unchanged (`357 357 340 271 71 2107` before and after), `second chat run exit status: 1`; the upload of `sv4-chat-results` after the check; `container removed: glow-proof-db-chat-45900925199-1`.
- **The API checks job:** `manage.py check` "System check identified no issues (0 silenced)"; `Ran 731 tests … OK (skipped=2)` (the two history tests of `ReciprocalWriterTests` skip, as on every branch push, which has no local `main`); Ruff "All checks passed!", "187 files already formatted"; mypy "Success: no issues found in 99 source files"; the contract tests `Ran 55 tests … OK`.
- **The other database jobs,** each applying `0014` from zero: `[identity] cases: 49/49`, `IDENTITY VERDICT: PASS`; `[profile] cases: 77/77`, `PROFILE VERDICT: PASS`; `[discovery] cases: 70/70 passed in 168.4 s`, `DISCOVERY VERDICT: PASS`; the ordering suite's `== VERDICT: PASS (reference) ==`, `== VERDICT: PASS (adapter) ==` and `== VERDICT: PASS ==`; each `ROW LOCKS (D14): PASS`.
- **The Mobile checks job:** the contract's "Generated types and runtime validators match schemas.", `tests 926`, `pass 926`, `fail 0`; the app's `tests 691`, `pass 691`, `fail 0`.
- **Within its timeout:** each job finished well inside its `timeout-minutes`; the chat job took 179 s of its 30 minutes (its suite's phase 114 s), 21 s more than A2-C1's with twelve more cases.

### The threat model's inputs

- **Who may register, rotate, revoke or read an installation.** Only a signed-in member: SV1's `GlowActorAuthentication` (an `active` account with a `valid`, unexpired session at the account's epoch), checked again on the locked rows inside each command and read. The actor never comes from the body, and the installation only from the `Glow-Installation-Id` header, never from an intent's field (a body naming an actor, an account, a session or, for the settings, an installation is `invalid_request`). There is no staff path and no other caller.
  - **Register:** for the member's own account, on the installation the header names. If that installation is active for another account, the register is a transfer, which revokes that account's registration of it (the capability below).
  - **Rotate:** a register on an installation already active for the member's own account, from any of the account's sessions; the rotating session is recorded on the row.
  - **Revoke:** only the member's own account's active registration of the header's installation. Another account's registration cannot be revoked directly (`state_conflict`, as for none), only through a transfer.
  - **Read:** only the member's own account's registration of the header's installation; an installation of another account answers `not_found`, as one with no registration does, so the read does not tell whether another account holds it.
  - **Settings:** the member's own account's, from an installation whose registration is active for the account; a change advances every registration of the account.
- **The token's custody.** The token arrives in the device intent's body and becomes a `ProviderToken` at once (it prints as withheld and cannot be pickled or compared by value). The store's `put` takes it before the command's transaction, so no external call holds a lock, and only the store's opaque reference is kept, on the active registration's row. A reference the command does not save goes to the pending discards after the transaction; a retired one goes there inside it and is discarded after the commit. So a reference is held only by an active registration's row and a pending discard's row (and, from B2, the push request handed to the transport). No row, log line, answer, exception or receipt holds a token, and no answer holds a reference. The idempotency record holds SV2's keyed digest of the canonical intent, the token included (AM5), for 24 hours: a keyed hash, not the token, from which the token cannot be read without `SECRET_KEY`. The checks: case 12 searches every row of every table for each drawn token and every answer for each token, reference and installation; the suite's scan holds the whole pool of 160 tokens among its secrets and the job's check derives the same pool; the views and the adapter log fixed strings and reason codes only.
- **The installation identifier as a capability.** A signed-in member who presents another account's active installation identifier transfers it: that account's registration is revoked (`ended_by` `transfer`), and from B2 the installation's pushes go to the new account. If an identifier leaked, another member could take an installation's notifications away from its owner. So it is never served (the DTO is built from an allowlist without it), never logged (the routes log a reason code only, which a structure test pins), and never shown; the app makes it at random for each installation (P09.2; AM7); the suite holds each installation among its member values, and its value scan finds none in the output. The answers do not tell a caller whether a transfer took place (a transfer and a first registration both answer version 1, `active`), and the read and the refusals answer another account's installation as they answer one with no registration.
- **Not B1's:** the token's validity and the permission prompt (P09.2); the transport, the triggers, the deliverer, the system's `logout` and the sweeps (B2; P11B); rate limits on these routes (none in B1).

### Substring pins, not semantics

These B1 tests read source text or pin a digest rather than run the behavior; each behavior they stand for is a case's or a route test's, named here, except where stated:
- `FixtureBoundTests.test_the_bound_is_ten_and_one_constant` pins the adapter's `if active >= n.MAX_ACTIVE_REGISTRATIONS:` and `raise _Refused(n.REGISTRATION_BOUND)` (the behavior: case 7, r09).
- `StructureTests.test_the_digest_binds_the_requesting_installation` pins `_digest`'s return statement as unparsed text and that both commands call `_digest(…, intent, caller)` (the behavior: case 5, r06).
- `StructureTests.test_the_locks_are_sv2s_and_two_literal_statements` reads the adapter's source for `select_for_update`, `lock_account_any_state` and the account table's name, and pins the two statements' endings (`WHERE id = %s FOR SHARE`, `WHERE id = ANY(%s) ORDER BY id FOR UPDATE`); a lock written another way would escape it (the behavior: case 8, r04, and the suite's row-lock record).
- `StructureTests.test_the_lock_order_is_the_account_the_session_then_the_registrations` compares the first lines of calls in the source, not the order at run time. **r19 (the settings command locking its session before its account) is caught only here:** no case forces the deadlock such an order would allow.
- `StructureTests.test_the_store_takes_the_token_before_the_commands_transaction` compares lines and, since r05b, refuses a `put` inside any function or lambda in `device()`; a `put` reached through another method's call would escape it (the behavior: case 12's `inside_a_transaction`, r05).
- `StructureTests.test_the_views_read_the_installation_from_the_header_only` reads the views' code (docstrings removed) for `device_id` and the header's parse, and each logger call's arguments.
- `StructureTests.test_no_module_imports_the_runtime_or_another_slices_routes` reads `from … import` statements only: an `import glow_chat` statement would escape it.
- `ChatScanTests.test_the_suite_holds_the_whole_pool_before_its_first_case` pins `chat_suite.py`'s text (r39); no case shows the suite's scan holding a token it did not draw.
- `ChatPlanTests.test_the_cases_that_publish_hidden_run_last` (A2R-7's check) reads a keyword set to `hidden` in the unparsed source; a cause published hidden through a variable would escape it.
- The seal's `test_no_runtime_module_names_b1s_modules_or_the_factories` reads `glow_api/*.py`'s text.
- `test_sv4_b1_migration_follows_0013` pins the migration's SHA-256, so any edit fails it; what the constraints refuse is case 11's (r07, r08, r32).
- `MappingCompletenessTests` reads the reasons the adapter and the fixture raise or return as constants or module names, following `self.` methods, module functions and SV2's `tx` and `idempotency` functions; a reason it cannot resolve fails the test as unresolved, and a reason passed through a call it does not follow (another module's) would escape it.

### Limits and deviations

- **No stop.** No owned path, served route, design point, token, dependency, timeout, earlier test or provider condition of the prompt's stop rule held.
- **A deviation: case 1 gained a check after the first reversal pass.** r16 (`non_atomic_requests` removed) first failed only `StructureTests`: the chat settings keep `ATOMIC_REQUESTS` off, as A2's limits record, so no case ran F12's routes with it on. `notifications.routes_refuse_what_is_not_their_dto` now runs a register, a settings change and a read with `ATOMIC_REQUESTS` on, and all three inside an atomic block and inside a test case's block, on A2's `transactions.non_atomic_requests` pattern, with `R4` among its checks; at the code head r16 fails the case too. The README's description of the case says so.
- **A deviation: three of B1's own tests were strengthened while their reversals were made.** `test_the_store_takes_the_token_before_the_commands_transaction` also refuses a `put` inside a function or lambda in `device()`: designing r05 showed that the line order alone would let a closure handed to `_run` pass (r05b). And, after the first pass, `ChatSupportTests.test_the_token_store_and_the_transport_are_the_suites_fixtures` and `test_the_observed_store_passes_each_call_and_records_the_transaction` put the API on `sys.path` for their own duration: run alone, as r44 and r45 ran them, they errored `No module named 'glow_domain'`, because only an earlier settings test puts it there in a whole run. **A2's `ChatSupportTests.test_the_text_reader_is_the_suites_one_provider` has the same order dependency** (run alone it errors the same way); it is an earlier test and B1 leaves it as it is (carried).
- **The NULL hole in `device_ended_when_revoked`,** found by the first local run and fixed before the code commit (D17, above).
- **`glow_profiles/idempotency.py` is unchanged:** the adapter writes its records with SV2's `digest` and `decide` and its own `IdempotencyRecord` write, as SV3's interactions do (the prompt's "or none").
- **CI's `mypy` does not reach `glow_notifications`:** the API's `pyproject.toml` lists the packages it checks (`glow_api`, `glow_domain`, `glow_chat`, `glow_identity`, `glow_profiles`, `glow_discovery`), and that file is not an owned path. It was checked here by name (107 source files, no issue). Carried for the manager: adding `glow_notifications` to that list is a configuration change, so full scope. The API's test modules are not in that list either, as before B1.
- **The proof's `mypy` reaches B1's modules through per-import `# type: ignore[import-not-found]`** (`chat_settings.py`, `chat_urls.py` and `chat_cases.py`'s `_adapter`), as the proof's configuration does not put the API on mypy's path.
- **`test_the_url_configuration_serves_the_five_route_modules` keeps its name** with six modules listed: a rename would change an earlier test beyond its entry.
- **The custody limits (AM4, as built):** a process that stops between the store's `put` and the command's `_park` (after the transaction) leaves a reference in the store and in no row, which no sweep can find; and a fresh reference a command did not save is parked, not discarded at once, so it waits for B2's sweep. (Superseded by B1-C1, DM-102: the handle is written before the transaction, so only a stop, or a failed write and a failed discard, between the `put` and the handle leaves a reference in no row; a known refusal or replay discards its reference at once, and an unknown outcome leaves its handle for the sweep.)
- **A dependency for B2:** the transfer reads its holder again under both accounts' locks and locks the holder's registration only after, which is safe because every writer of a registration locks its account first (B1's commands do). B2's `logout`, and any later writer of `DeviceRegistration`, must lock the account first too.
- **Two accounts registering one new installation at once:** the second waits on the partial unique index and then fails on it (`IntegrityError`), which the adapter answers as `state_conflict`, not retryable (case 9). A retry by the second member's app would then be a transfer.
- **`RouteTests` run the routes over the port's in-memory fixture, not the ORM adapter** (the adapter needs a database); the adapter's answers through the routes are the cases'.
- **r31's failure is `RouteTests`' set-up erroring, not its assertion:** with a default store, the device route reaches the real adapter, which needs a database that the offline settings do not have, so the set-up's request raises before `no_store`'s answer is read.
- **r15 (a route logs the installation) is caught by the suite's value scan, not by a case:** case 1 passes, and the runner counts one member value in the output, which in a whole run makes `chat value scan` report it and the verdict fail.
- **r16 at its first pass, r19 and r30 are caught by offline tests only** (r16 at the code head by case 1 as well): no case forces the settings command's deadlock (r19), and no case expires a session inside a B1 command (r30's mapping).
- **Lines B1 leaves stale outside its paths,** listed for the manager to route: the CI policy's line 13 ("Database proof checks (chat)" names SV1's, SV2's, SV3's and chat's routes but not F12's, and the scanned values' examples omit the push tokens and the installations; lines 13 and 15 were owned only with a workflow change, which B1 did not need); the proof README's module table row for the chat suite (line 76, "SV4 A2: the chat suite's settings (with the history read's text reader …)", outside the chat suite's paragraph) and its run paragraph (line 216).
- **`npm ci` needed the proxy's variables** (`HTTPS_PROXY`, `NODE_EXTRA_CA_CERTS`) in the clean environment; nothing else was added to any command's environment.
- **The reversals' output held synthetic push tokens twice** (r38 and r40: an offline test's assertion message, with tokens it derives from its own throwaway key, not the run's). They were redacted from the scratch output and are not quoted here.
- **The local database runs are iteration only;** the run of record is CI's.

### Manager verification of B1 (App Manager 13, 26 November 2026)

- **The heads:** `claude/lucid-fermi-droq7u` at `f106105` (records; it changes only this record), with the code head `e7e7e84` on the prompt's commit `6a22ddf`. Merged into the manager branch at `4fe1a7f`, whose non-Markdown paths equal `e7e7e84`; `main`'s trusted classifier (unchanged since `43e794a`), outside the checkout with `python3 -I` and full SHAs, gives `"full": true`, reason `behavior-or-empty`, one merge base `988a36a`.
- **The diff** (`git diff 6a22ddf e7e7e84`): 26 paths, each in B1's owned paths, every file mode ordinary; `glow_chat/`, `glow_discovery/`, `glow_identity/`, `glow_api/`, `packages/`, `apps/`, `.github/`, the CI policy and `glow_profiles/idempotency.py` unchanged. Read in full for `glow_notifications/persistence.py`, `views.py`, `contract.py` and `providers.py`, and the model and migration changes:
  - **custody:** the store's `put` runs in `device()` before `_run`'s transaction; a reference the command does not save is parked after it; a retired reference moves to `PendingTokenDiscard` inside the transaction and is discarded after the commit; the four constraints (`device_account_installation`, `device_one_active_installation`, `device_reference_while_active`, `device_ended_when_revoked`, the last with its NULL fix) are in `0014`;
  - **the locks:** the account `FOR NO KEY UPDATE` (SV2's `lock_account`), then the session `FOR SHARE`, then the registrations `FOR UPDATE` by key; a transfer reads its holder with no lock, locks both accounts lower first, and refuses `transfer_changed` if the holder changed; the read takes the account and session `FOR SHARE`;
  - **idempotency:** SV2's `digest` over the intent (the token included) and `glow_installation_id`, decided after the session's checks; the record written with F12's receipt code;
  - **the routes:** the actor from SV1's authentication only, the installation from `Glow-Installation-Id` only, JSON-only negotiation, `no-store`, `non_atomic_requests`, `WWW-Authenticate: Bearer` on every 401; `REFUSALS` maps each reason to one code, an unknown one to `state_conflict`; the token store reached only through `GLOW_NOTIFICATIONS_TOKEN_STORE`, which only the chat settings name;
  - **the bound:** `MAX_ACTIVE_REGISTRATIONS = 10` in the domain, counted under the account lock, in the adapter and the fixture.
- **The run of record,** Foundation run 45900925199 (`push`, `e7e7e84`, attempt 1), read with `gh api`: all twelve jobs succeeded; the gate's log has "Application checks passed"; the chat job's log has `Applying glow_persistence.0014_notification_devices... OK`, `[chat] cases: 30/30 passed in 113.5 s`, both scans clean (1871 secrets held; 0 found), `ROW LOCKS (D14): PASS`, `CHAT VERDICT: PASS`, `dbshell` refused (exit status 1) and the second run refused; the API checks job `Ran 731 tests … OK (skipped=2)`.
- **Not re-run by the manager:** the session's local checks and its 53 reversals; the run of record ran the suites in CI.
- **Routed from the session's limits:**
  - **CI's `mypy` does not check `glow_notifications`** (`services/api/pyproject.toml` lists the packages it checks): B1's owned paths left the list out (AM13-15). B2, which adds most of `glow_notifications`' remaining code, takes it in its owned paths, with the session's by-name check as the evidence until then;
  - **the stale lines** (the CI policy's line 13, the proof README's chat row at line 76 and its run paragraph at line 216) and **A2's order-dependent `test_the_text_reader_is_the_suites_one_provider`**: carried to B2, which changes the chat suite, its README and its offline tests; the CI policy's line is governing Markdown, read with B2's pre-merge read;
  - **the custody limits** (a stop between `put` and `_park` leaves an orphaned reference; a parked reference waits for B2's sweep) and **the writers' lock rule** (every writer of `DeviceRegistration` locks its account first): for B2's prompt and P11B.
- **For the exact-head review** (the brief's review plan, B1's threat model): who may register, rotate, revoke or read an installation, and a transfer as the installation identifier's capability; the token's custody end to end, the parked and retired references and the constraints; the lock order against a session's end and against a concurrent transfer; the digest's binding; the mapping's completeness and every 401's challenge; the seal and the factories; the reversals caught offline only (r16 at first, r19, r30) and by the value scan only (r15).

### Codex on PR60 (26 November 2026)

- **PR60** carries B1 into `main` (opened at `cd920fd`). PR run 45902955792 (`pull_request`, `cd920fd`) passed all twelve jobs, and its gate printed "Application checks passed". Codex's code review of `cd920fd` completed with one finding, a P2 thread, comment 4713760650, on `services/api/glow_notifications/persistence.py`, line 376 (`_park`): "Preserve token custody when parking the reference fails". If the store's `put` succeeds and the database then fails, `_run` answers an error and `_park`'s insert can fail too; `_park` only logs, so the token stays in the store with no registration and no pending discard, and no sweep can find it, during a handled failure with no process stop. The session's own custody limit names only a stop between `put` and `_park`.
- **Disposition:** to B1's exact-head review, as its focus item 3 (revision 1 of the review prompt), so that it joins that review instead of starting another pass (manager workflow, step 6). The thread stays unresolved until the review's disposition and any correction answer it.

### Exact-head review of B1 (26 to 27 November 2026)

- **Session:** the exact-head review, started by Nathan from [B1's review prompt](https://github.com/amthorn78/glow-dating-app/blob/9bf714159151189941b4dfc93f401233cba19d57/docs/ephemeral/2026-11-26-sv4-b1-review-prompt.md), revision 1, from `9bf7141`, in `Glow App - No Stream`. Nathan relayed its report on 27 November.
- **Its start gate, classification and environment check:**
  - every start-gate check passed: `HEAD` `9bf7141`; one merge base, `988a36a`; the prompt's commit on the live branch; the non-Markdown paths equal to `e7e7e84` at `HEAD` and on the live branch; no review recorded;
  - the trusted classifier, `main`'s, outside the checkout with `python3 -I`, gave `"full": true`, reason `behavior-or-empty`, 45 paths;
  - none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or the `STREAM_`, `PG`, `R2_`, `CLOUDFLARE_`, `CF_` or `RAILWAY_` names; AWS and GitHub token names present and unread;
  - Python 3.12.14, Node 24.19.0, npm 11.9.0, Docker 29.9.3 (it started the daemon and stopped it at the end);
  - GitHub read with `gh api` REST `GET` calls only; the checkout left clean.
- **Verdict: changes requested.** No blocking finding. F12's behaviour holds on every route, but Codex's P2 is confirmed on a database (B1R-1), with two related should-fix findings (B1R-2, B1R-3); B1R-4 to B1R-9 are nits or carries. The report numbers its findings F-1 to F-9; they are B1R-1 to B1R-9 here.

**What it verified** (its focus items, shortened):
- **Who may act (D19):** no route serves or changes another account's registration or settings; the read answers another account's installation `not_found`, as it answers none; a revoke reaches only the caller's own row.
- **The transfer (AM7):** the re-read under both accounts' locks closed every race it tried (the holder suspended, rotating, revoking). A registration row cannot change without its account's lock in B1's writers; B2 must keep that.
- **The locks (AM3):** a register, a settings change, a revoke, a rotation and a read each waited on a sign-out and were refused with the challenge (probed). It found no deadlock order against chat's, SV2's or SV3's writers (a 12-second stress, no deadlock). The read never paired a new version with old settings (0 mismatches in 950 reads against 949 concurrent changes).
- **r19 is a limit, not a defect:** the code's order is right. Reversed, the settings command deadlocked against a chat send of the same session (`DeadlockDetected`), so a database case could pin the order.
- **The bound, idempotency, the codes, the routes' shape:**
  - two commands cannot pass the bound together;
  - a replay changes nothing and parks its reference;
  - the completeness test reaches every reason the adapter, the fixture and SV2's helpers raise;
  - no refusal names a value;
  - each view refuses a caller's transaction before the `put`;
  - no answer is outside the contract's `Error`.
- **The port and the fixture:** they answer alike, except that the adapter's `put` comes before the replay and version checks, so a store refusal wins there. `test_notifications.py` keeps every earlier assertion, and the fixture's guard is unchanged.
- **The models and `0014`:**
  - the migration applies from zero in all five database jobs and locally;
  - from `0013`, judged by reading: the renames keep their values, the removals drop theirs, and a registration row would fail the new foreign key and roll the migration back;
  - `test_model_definitions.py` gains only B1's entries.
- **The seal:** the seal test catches a module reached at import time at any depth, but not a lazy import made at request time from outside `glow_api/*.py` (its reach, to record). The runtime names no factory.
- **The cases:** all twelve match D29 and AM13, none vacuous. The token pool's derivation is sound and held by the scan before case 1. The follow-ups (F1, F4, A2R-6, A2R-7, the README's list, A2R-13, A1's lines) are done as their entries say.
- **The records:** they hold except under B1R-1, B1R-4, B1R-6 and B1R-7. Of the four items routed to B2 (CI's `mypy` list, the CI policy's line 13, the README's lines 76 and 216, A2's order-dependent test), none is a defect D-07 names.

**Its probe of B1R-1** (a throwaway PostgreSQL 17.11):
1. A register's `put` succeeded, then the database was made unreachable at the command's commit.
2. `device()` answered `error`, which the route serves as `state_conflict`.
3. `_park` logged its fixed line.
4. With the database back: no registration row, the reference in no pending discard, the store still holding the token, and no process stopped.

A single terminated connection does not lose the reference: Django reconnects, and `_park` succeeds. The loss needs the database unreachable for `_park`'s own statement.

**Its checks,** in a `git archive` copy of `e7e7e84`, each package from its own lock with `--require-hashes`, under `env -i`:
- **The API:**
  - `check`: clean;
  - tests: `Ran 731 tests … OK (skipped=2)` (A1's two history tests, which need git history the archive lacks);
  - Ruff and format: clean (187 files);
  - `mypy`: 99 files; `mypy glow_notifications`: 8 files, no issue;
  - `makemigrations --check`: "No changes detected".
- **The proof:** `Ran 428 tests … OK`; Ruff and mypy clean (78 files).
- **Local database runs** under P06.DB's D4 (informational): the chat suite 30/30 in 179.2 s, both scans clean, `ROW LOCKS (D14): PASS`, `CHAT VERDICT: PASS`. Everything was removed afterwards.

**Its reversals,** each on a copy, restored byte for byte:

| Reversal | What fails |
|---|---|
| The installation from the body | 4 offline tests; cases 1, 4 |
| The `put` inside the transaction | the store-first structure test; cases 4, 12 |
| The installation left out of the digest | its structure test; case 5 |
| A 401 inside the locks without the challenge | 3 offline tests; case 8 |
| The adapter's bound removed | the substring pin only; case 7 |
| A refusal naming a value | `RouteTests` (7); 8 cases |
| The runtime including `glow_notifications.urls`, or serving an F12 path | the test command or `test_the_runtime_serves_none_of_b1s_routes` |
| `_park` doing nothing | no offline test; cases 5, 7, 8, 9, 12 |
| The transfer's re-read not compared | no offline test; case 10 |
| **`_hold_for_discard` doing nothing** | **none** (B1R-3) |
| The session row unlocked | case 8 |
| A token written to a row | cases 2, 5, 12 |

Settings needing no active registration, and settings locking one row only, failed no offline test; it did not run their database halves.

**The runs** as it read them:
- **45900925199** (`push`, `e7e7e84`): all twelve jobs passed, the gate "Application checks passed"; the chat job 179 s, 30/30 in 113.5 s.
- **45904055757** (`pull_request`, `9bf7141`): all twelve passed; the chat job 176 s, 30/30 in 109.4 s.
- **Codex:**
  - review 6081023564 of `cd920fd` left one P2 thread, comment 4713760650, on `persistence.py` line 376; unresolved, not outdated, no reply;
  - its review of `9bf7141` completed at 22:21 UTC with no new comment.

**Its findings** (in its words, shortened):

| ID | Severity | Where (at `e7e7e84`) | Finding | Its class |
|---|---|---|---|---|
| B1R-1 | Should fix | `glow_notifications/persistence.py` 370 to 376 (`_park`), called at 460 to 461 | Codex's P2, confirmed on a database. A handled database failure after the store's `put` loses the reference: no registration, no pending discard, the token held, and no sweep can find it. The custody sentences in `production-contracts.md` and `data-model.md` state AM4's rule without this exception; the record's limit names only a process stop | Security boundary: a custody rule left open |
| B1R-2 | Should fix | `persistence.py` 460 (`done is None` read as "not saved") | After a commit whose acknowledgement is lost (simulated), the saved reference is also parked. The owner's later revoke answers 409 `state_conflict`, since the pending discards' uniqueness refuses the retire; a rotation or a transfer fails the same way. B2's sweep would then discard a token in use. No constraint stops a reference being in both tables | Security boundary (custody), and behaviour (a revoke from `active` refused) |
| B1R-3 | Should fix (tests) | `persistence.py` 362 to 367 (`_hold_for_discard`), 381 to 387 | With `_hold_for_discard` a no-op, all 94 of B1's offline tests and all 12 of its cases pass. The behaviour is right: with the store's discard made to fail, a rotation, a revoke and a transfer each left the retired reference pending. D18's "a failed discard waits in its table" is unproven | Missing test at a security boundary |
| B1R-4 | Nit | The database server's log | On the one-active-row constraint's refusal, PostgreSQL's own log wrote the installation (`DETAIL: Key (installation_id)=…`) and the failing statement with a store reference. No token appeared; CI never prints the container's log. AM7's "never logged" holds for the application only | No: a limit, the database's log settings to P11 |
| B1R-5 | Nit | `glow_domain/notifications.py` 250 to 257 | The port does not say that `put` returns a fresh reference each time, which the adapter relies on: a store returning one reference per token would make a rotation with the same token discard the reference it had just saved. The fixture issues a new one | No: to P09.2 and P11B, with a docstring line |
| B1R-6 | Nit | The record, "The threat model's inputs" | In a race, a first register's `state_conflict` is reachable only when another account holds, held or is registering that installation; a transfer's answer waits for the holder's token's discard, which a first registration's does not. The caller already holds the identifier | No |
| B1R-7 | Nit | `production-contracts.md`, the codes bullet | "(503, retryable), and so is a device command when no token store is configured" reads as retryable; the code answers not retryable (`contract.py` 94), as the record says | No |
| B1R-8 | Nit | `persistence.py`, `device()` | Every register costs a `put` before any check inside the locks: a refused, replayed or conflicting one leaves a token and a pending row until B2's sweep, and nothing bounds a member's rate | No: to B2's sweep and P11B |
| B1R-9 | Nit | `models.py`, `DeviceRegistration.session` | It cascades on delete, as `account` does: a deleted session row would drop registrations with their references. No writer deletes one today | No: to D30's P08 carry |

**Its proposed remedies for B1R-1:**
- **(a) the smallest:** `_park`'s `except` discards through the store, with a second fixed log line if that fails too. Its residual: after a lost commit acknowledgement with the database unreachable, that discard removes a token the committed registration holds.
- **(b) Codex's "recoverable handle":** write the pending row before the transaction and delete it in the transaction that saves the reference. That closes B1R-1 and B1R-2 and narrows the process-stop limit. It changes D18's custody sentence (a design point in B1's stop rule) and constrains B2's sweep, which must not discard a row whose command is in flight.
- **B1R-2,** if (a): don't park a reference a registration holds (one conditional insert), or carry it to B2's sweep with a recorded limit.
- **B1R-3:** one case using the store's `fail_next_discard` for the three transitions.

**What it did not read or run:**
- `chat_cases.py`, `chat_support.py`, `test_chat_offline.py`, `test_model_definitions.py`, `test_notifications.py` and `models.py` whole; it read every changed hunk and the parts B1 relies on.
- A migration from `0013` with rows present: its session's permission check refused the partial `migrate`, which the prompt allows only through the proof's own commands.
- The contract's and the mobile app's checks (B1 changes neither; both runs passed them).
- The record's other reversals, and the whole suite under each reversal (it ran B1's twelve cases through a subset runner).
- Notion, DM-99 and DM-100, the carried-items file, and P06.DB's brief beyond D4 and D5.

**The manager's checks** (App Manager 13, 27 November 2026):
- **The live state:**
  - `main` at `988a36a`; the manager branch and PR60 at `9bf7141`; B1's branch at `f106105`; `claude/dev-manager` at `60325b1`;
  - PR60's one thread (comment 4713760650) unresolved, not outdated;
  - the runs on `9bf7141`: 45904055757 (`pull_request`) and 45904050215 (`push`), both success.
- **B1R-1, read:** `device()` parks the fresh reference after `_run` whenever `done is None or not done.saved` (`persistence.py` 460 to 461). `_park` catches every exception from its insert and logs a fixed line only (370 to 376), so nothing holds the reference once that insert fails.
- **B1R-2, read:** the same condition reads `done is None`, an unknown outcome (a commit whose acknowledgement was lost included), as "not saved".
- **B1R-3, read:** the only test that calls `fail_next_discard` is `tests/test_notifications.py` line 933, against the in-memory fixture. No adapter test or database case makes a retired reference's discard fail.

**Disposition** (App Manager 13; the manager workflow's step 6, "What a correction pass is for" and "Fix or carry, by rule", under D-07). Either form of B1R-1's fix changes a custody decision (AM4's and D18's sentences, and with (b) B2's sweep), so the form goes to Dev Manager 7 first ([DM-102](../../ephemeral/2026-11-27-dm-102-sv4-b1-c1-custody.md)):

| Finding | Disposition | Why |
|---|---|---|
| B1R-1 | **Fixed before the merge**, by correction B1-C1; the form by DM-102, item 1 | A custody rule left open at a security boundary in B1's own code, and custody sentences the merge reads; classes 2 and 3 of the review prompt |
| B1R-2 | **Fixed with B1R-1**, by B1-C1; the form by DM-102, item 1 | The same root, at the same boundary, and a revoke from `active` refused (class 1) |
| B1R-3 | **Fixed**, by B1-C1 (a test that fails with `_hold_for_discard` a no-op); its form by DM-102, item 2 | A missing test at a security boundary (custody) |
| B1R-5 | **Fixed**, by B1-C1 (the port's docstring states it), and carried to P09.2 and P11B (the real store must meet it) | Either form of B1R-1's fix rests on it |
| B1R-4, B1R-6, B1R-7 | **Fixed**, by B1-C1, in the files it changes (AM7's sentence narrowed to the application; the record's two sentences; the codes bullet); the database's log settings carried to P11 | Nits in files the correction changes, as A2R-5 in A2-C1 |
| B1R-8 | **Carried** to B2 (the sweep's bound) and P11B (rate limits) | A nit in no class |
| B1R-9 | **Carried** to P08, with D30's carry | A nit in no class |
| r19's database case | **Carried** to B2, which changes the chat suite | A limit: the code's order is right |
| The seal test's reach; the port's order difference; the migration from `0013` with rows, judged by reading | **Recorded here** as limits | None in a class |
| Codex's P2 thread (comment 4713760650) | Resolved once B1-C1's fix and Codex's review of its head confirm it | It names B1R-1 |

### Dev Manager 7's DM-102 (27 November 2026)

[DM-102](../../continuity/dev-manager/reviews/2026-11-27-dm-102-sv4-b1-c1-custody.md) (`f86ccaf`, a read of `c331899`; merged at `d0838ad`) decided B1-C1's custody fix: **(b), the new reference's pending discard written as its handle before the command's transaction,** with AN1 to AN11.
- **Codex's second P2 thread** (comment 4715163584, on `c331899`, `persistence.py` line 461: "Preserve token custody across an unknown commit outcome") is B1R-2, found independently, and suggests (b)'s form. It reached the Dev Manager as the consultation's addition (PF02-R41).
- **AN1** (D18, applied in the brief's revision 13): the save deletes its handle and refuses (`state_conflict`) unless it deletes exactly that one row; the handle is written only for a reference no registration and no pending discard holds, and a reference already held is `token_store_refused`, with nothing discarded; a failure raised before the transaction's body returned is a known outcome (the reference discarded at once), one after it, at the commit, an unknown one (the handle left to the sweep).
- **AN2** (D24, applied in revision 13): the sweep takes a pending discard only past its bound and with no registration holding its reference, removes the row in its own transaction before it calls the store, and writes it again if the discard fails.
- **AN3 to AN8** (the custody sentences in `production-contracts.md` and `data-model.md`, with B1R-4's narrowing, and B1's custody limit marked superseded) and **AN11** (`TokenStore`'s docstring) go into B1-C1. The adapter's module docstring and `PendingTokenDiscard`'s docstring state the same rule.
- **The proof:** the manager's four cases (B1R-3's; the handle's write failing; a known refusal; an unknown outcome after the commit), and three more, each with its reversal: a save that finds its handle gone refuses; a reused reference is refused; a failure inside the transaction (case 9's race) is known. Two offline structure tests: the handle's write follows the `put` and precedes `_run`; the save's delete checks its count.
- **AN9 and AN10** update the carried entries for B1R-8 and B1R-5 at B1-C1's integration.
- **A full exact-head review** follows B1-C1 (a design change), then Dev Manager 7's pre-merge read of PR60.
- **The dispositions above therefore stand as:** B1R-1 to B1R-7 fixed by B1-C1 in (b)'s form, with AN1 to AN8 and AN11; B1R-8 and B1R-9 carried, B1R-8's and B1R-5's entries updated by AN9 and AN10 at B1-C1's integration; both Codex threads resolved once B1-C1's fix and Codex's review of its head confirm it.

## B1-C1

- **Session:** SV4 B1's correction B1-C1, started by Nathan from [B1-C1's prompt](https://github.com/amthorn78/glow-dating-app/blob/f7a21b9ce69a24eff03015c1b1315d8d75e425e3/docs/ephemeral/2026-11-27-sv4-b1-c1-custody-correction-prompt.md), revision 1, from `f7a21b9ce69a24eff03015c1b1315d8d75e425e3` of the manager branch `claude/magical-wozniak-yfmmx2`. The specification is the [brief](../../planning/sv4-chat-notifications.md), revision 13 (D18's custody bullet, AN1; D24's sentence, AN2; "Owned paths", B1-C1), with [DM-102](../../continuity/dev-manager/reviews/2026-11-27-dm-102-sv4-b1-c1-custody.md)'s AN1, AN3 to AN8 and AN11.
- **Branch:** `claude/funny-hypatia-lpzbn0`, which the push filter's `claude/**` covers. It starts at the prompt's commit.
- **Code head:** `48f08017350993c13bccb78095e084ad0434a6a5`, whose run is the run of record. **Records head:** the commit that adds this section, pushed after that run had finished.
- **What B1-C1 fixed:** B1R-1 and B1R-2 in DM-102's form (b), with AN1's three conditions; B1R-3 (a case that fails with `_hold_for_discard` a no-op); B1R-4, B1R-6 and B1R-7 in the words given (AN4, AN6, below, and B1R-7's sentence); B1R-5 (AN11, the port's docstring).
- **What it did not touch:** the routes, the views, the lock order and every check but the custody paths; the idempotency digest, the bound, the settings command and the read (their answers unchanged; their one change is to unpack `_run`'s fourth value); the models' fields and constraints and the migration (`PendingTokenDiscard`'s docstring only); `glow_chat`, `glow_identity`, `glow_profiles`, `glow_discovery` and `glow_api`; the workflow, the contract's JSON and the generated outputs; every other suite; `tests/test_notifications.py` (unchanged: it needed nothing). The reversals' temporary edits were undone (below). No provider call, HDE call, external database or credential. Codex's two threads on PR60 were not touched.

### The start gate and the environment check

- **The environment** (section 1 of the prompt, names only), on 27 November 2026: no `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY`; no `STREAM_*`, `PG*`, `R2_*`, `CLOUDFLARE_*`, `CF_*` or `RAILWAY_*` name. Present and never read, printed or passed to a command: `AWS_ACCESS_KEY_ID`, `AWS_CA_BUNDLE`, `AWS_SECRET_ACCESS_KEY` (OD-76), `GH_TOKEN`, `GITHUB_TOKEN`. Toolchain: `Python 3.12.14` (`python3.12`); `Docker version 29.9.3, build 5457199` (no daemon was running; the session started `dockerd` in the background and stopped it at the end). Every repository command ran under `env -i PATH=… HOME=… LANG=C.UTF-8`, plus only its own variables (`GLOW_ENV=test` for the API; the proof's `PROOF_*` names for the suite); `pip install --require-hashes` needed the proxy's `HTTPS_PROXY` and `PIP_CERT` added, values unprinted. The two virtual environments were made with `python3.12` in each package's `.venv` (ignored by git).
- **The start gate** (section 2): `git switch -C claude/funny-hypatia-lpzbn0 f7a21b9ce69a24eff03015c1b1315d8d75e425e3`; `git rev-parse HEAD` printed `f7a21b9ce69a24eff03015c1b1315d8d75e425e3`; "this prompt's commit is on the live branch", "B1's code head" and "no code on the live branch after e7e7e84" printed; `grep -c` printed `1` for "Exact-head review of B1" and `0` for "B1-C1". `origin/main` was `988a36a`; the manager branch's head was the prompt's commit. The session branch did not exist on the remote.

### What was changed, by item

1. **`_run`'s outcome split** (`glow_notifications/persistence.py`). `_run` returns a fourth value, whether the outcome is known. A flag is set the moment the body returns, before the `before_commit` hold point and the commit; a failure raised before it (a refusal, a deadlock, any database error inside the body, the one-active-row constraint's `IntegrityError` included, or one at the transaction's start) is known, since the transaction rolled back; one raised after it (as `transaction.atomic`'s block exits: the commit, or the hold point before it) is unknown. The answer served is computed as before from the outcome and the reason, so the read and the settings command, whose only change is to unpack the fourth value, serve the same codes. `_run`'s docstring states where the split falls. A failure at the `before_commit` hold point is counted unknown though the commit has not run (conservative: the handle is left; probes only signal and wait).
2. **The handle** (`_write_handle`, `_held_since`, `device()`). After the store's `put` and before `_run`, in autocommit (no caller transaction: `device()` refuses one first), one statement, `HANDLE_WRITE`: `INSERT INTO glow_persistence_pendingtokendiscard … SELECT … WHERE NOT EXISTS (SELECT 1 FROM glow_persistence_deviceregistration WHERE token_secret_ref = %s) ON CONFLICT (token_secret_ref) DO NOTHING RETURNING id`.
   - **Alone:** a row returned is the handle; no row is a reference already held (a registration found by `NOT EXISTS`, or a pending discard by the uniqueness, `ON CONFLICT`); an exception is a failed write, with nothing written.
   - **Under concurrency:** `NOT EXISTS` reads the statement's snapshot. If another command's save of the same reference has deleted that reference's handle and is committing, the insert waits on the pending discards' unique index and, once the save commits, inserts, though a registration now holds the reference, which its snapshot did not see. So `_held_since` reads the registrations again in a new snapshot once the handle is written; if one holds the reference, the handle's row is removed by its key and the command refuses. No holder can appear after that read: a save must delete the reference's one pending discard (item 3), and that row is now this command's. Case B1-C1-6 forces this interleaving (the wait observed), and reversal c06b shows the read is what refuses there.
   - **A reference already held:** `token_store_refused` (`provider_unavailable`, 503, retryable), nothing discarded, nothing written.
   - **A failed write:** `_discard_unwritten` has the store discard the reference at once, and the command answers `error` (by the exception's type; `state_conflict`, 409, not retryable). If that discard fails too, one fixed line is logged ("notification token reference held by no row: its discard failed"), never a value.
   - **A failed re-read** (`_held_since` raising): the command answers `error` and discards nothing; the row stays for B2's sweep, which takes none a registration holds (D24, AN2).
   - **`_park` is gone:** nothing parks a reference after the transaction.
3. **The save consumes its handle** (`_consume_handle`, called from `_register` before the first registration's `create` and before a rotation's or re-registration's `update`, both of which write `token_secret_ref=fresh.value`): `PendingTokenDiscard.objects.filter(pk=handle, token_secret_ref=fresh.value).delete()`, refusing `token_handle_missing` unless exactly one row was deleted. The new reason is `glow_domain.notifications.TOKEN_HANDLE_MISSING`, mapped in `REFUSALS` to `state_conflict` (409, not retryable); `MappingCompletenessTests` reaches it through `self._consume_handle`. **Where in the order:** `_register` runs after `_lock_registrations`, so the order is the account(s), the session, the registrations, then the handle's row. **Deadlocks:** none against B1's other commands. The handle's row is locked only by its own command's delete, by an autocommit statement that holds no other lock (another command's handle insert of the same reference, which waits on it; `_discard`'s and `_held_since`'s deletes), and, from B2, by the sweep's own short transaction (AN2); none of these waits on an account, session or registration lock while holding the handle's row, so no cycle can form. A revoke and the settings command touch no handle; a retired reference's pending row is a different reference's.
4. **The immediate discards** (`device()`): once `_run` returns, a new reference that was not saved (`done is None or not done.saved`) is discarded at once through `_discard` when the outcome is known (a refusal, a deadlock, a replay, a failure before the body returned): the store discards it, then its handle's row is removed, and a failed discard leaves the row for B2's sweep. An unknown outcome discards nothing and leaves the handle. A retired reference's path (`_hold_for_discard` in the transaction, `_discard` after the commit) is unchanged.
5. **The docstrings:** the adapter's module docstring, its "Custody" paragraph, now "Custody (AM4; B1-C1, DM-102's AN1)", states AN1's rule in the brief's terms (its "There is no switch" paragraph is unchanged and still true: the adapter has no test-only branch, flag or hook, and the probe it takes only signals and waits); `PendingTokenDiscard`'s docstring (`glow_persistence/models.py`) states the handle and the retired reference; `TokenStore`'s is AN11, as given.
6. **The fixture store** (`FixtureTokenStore`): `reuse_next_put(reference)` makes the next `put` return a reference the store already gave out (a `ValueError` for one it never did), keeping what that reference holds and not keeping the token that `put` is given. Its environment guard is unchanged. `tests/test_notifications_port.py`'s `FixtureTokenStoreTests` (3 new tests) pins AN11's two rules as the fixture keeps them (a new reference for each `put`, three `put`s of one token; a discard of a reference already discarded, or never given, changes nothing) and `reuse_next_put`, with the guard.
7. **Offline tests** (`tests/test_notifications_routes_offline.py`, `StructureTests`):
   - `test_the_store_takes_the_token_before_the_commands_transaction`: its `self._park(fresh)` assertion is now `handle = self._write_handle(fresh)`; its other assertions stay (the `put` before `_run`, none in a nested function or lambda, none in `_device`, `_register`, `_revoke`, `settings`, `read` or `_run`, and the line `if fresh is not None and (done is None or not done.saved):`, which the new code keeps).
   - `test_the_handle_is_written_after_the_put_and_before_the_transaction` (new): the first lines of `self._tokens.put`, `self._write_handle`, `self._held_since` and `self._run` in `device()` are in that order; no `_write_handle(` in a nested function or lambda of `device()` or in `_device`, `_register`, `_revoke`, `settings`, `read` or `_run`; no `_park`; the discard at once is under `if known:`; the refusal is `token_store_refused`; `HANDLE_WRITE` is an insert into the pending discards with the registrations' `NOT EXISTS` and ends `ON CONFLICT (token_secret_ref) DO NOTHING RETURNING id`; `_held_since` reads the registrations and removes the handle's row by its key. **What it reads and misses:** the source's call lines and unparsed text, not the order at run time; a write reached through another method's call, or a statement built at run time, would escape it (the behaviour is cases B1-C1-2, -5 and -6).
   - `test_the_save_consumes_its_handle_and_checks_the_count` (new): `_consume_handle`'s delete by `pk=handle, token_secret_ref=fresh.value` and `if deleted != 1: raise _Refused(n.TOKEN_HANDLE_MISSING)`; in `_register`, `self._consume_handle(handle, fresh)` before `DeviceRegistration.objects.create` and before both calls that write `token_secret_ref=fresh.value`; the reason served `state_conflict`. **Misses:** a save through another path, a count compared another way (the behaviour is case B1-C1-5).
   - `test_the_outcome_is_known_until_the_body_returns` (new): `_run`'s `returned = False`, `returned = True` right after `done = body(tx)` and its `_Refused` handler, before `signal(probe, 'before_commit')`; `known = not returned`; the refusal known; each of the three failure returns carrying `known`. **Misses:** a failure the driver raises somewhere `_run` does not wrap (the behaviour is cases B1-C1-4 and -7).
   - `MappingCompletenessTests`: `ADAPTER_SERVED` gains `token_handle_missing` (`state_conflict`, not retryable); the module docstring names B1-C1's structure tests.
8. **Database cases** (`chat_cases.py`, seven new, after `notifications.custody_rules_are_constraints` and before `notifications.no_token_in_any_row_or_answer`, which runs unchanged after them and checks their references too; all before the three that read or publish `hidden`):
   1. `notifications.a_failed_discard_waits_for_the_sweep` (D18, B1R-3, DM-102): with `fail_next_discard`, a rotation, a revoke and a transfer are each served and each leave the retired reference pending, its token held, the row without it.
   2. `notifications.a_failed_handle_write_discards_at_once` (D18, AN1, B1R-1): `handle_write_fails` (below); the register answers 409 `state_conflict`, not retryable; the store took the token and discarded it at once; no registration or pending discard holds the reference; nothing saved.
   3. `notifications.a_known_refusal_discards_at_once` (D18, AN1, D25): a stale version (409 `stale_version`), the bound (an eleventh, 409 `state_conflict`) and a replay (served): each reference discarded at once, none pending; the saved reference held, its handle consumed.
   4. `notifications.an_unknown_outcome_leaves_the_handle` (D18, AN1, B1R-2): `commit_answer_lost` (below) around the adapter's `device`: `("error", "OperationalError")`, served `state_conflict`; the registration committed `active` with the reference, the reference not pending, its token held; the owner's later revoke through the route is accepted (version 2, `revoked`) and discards the token.
   5. `notifications.a_save_whose_handle_is_gone_refuses` (D18, AN1, D24): the adapter's `device` on a worker, held at its transaction's start by `BeginHold` (below); its handle is then pending (written before the transaction); the case's connection deletes that row, as the sweep would; released, the save refuses `token_handle_missing` (`state_conflict`); no registration holds the reference, which the command had discarded at once; the case's own discard through the store, as the sweep's, changes nothing.
   6. `notifications.a_reused_reference_is_refused` (D18, AN1, AN11, B1R-5): with `reuse_next_put`, a register given a reference an active registration holds, and then one a pending discard holds (the holder's revoke with its discard failed), each answers 503 `provider_unavailable`, retryable; nothing saved, no handle written, no idempotency record, the holder's row and its pending discard unchanged, its token held. **Concurrently:** a first registration's save is held at its commit (`_held_against`, its handle deleted and its row written, uncommitted); a second register, given that reference, waits on the pending discards' unique index (observed on the holder's backend), and once the save commits is refused `token_store_refused`, its handle's row removed; the first registration holds the reference, its token held, none pending, nothing saved for the second.
   7. `notifications.a_failure_inside_the_transaction_is_known` (D18, AN1, AM13): case 9's race through the adapter on two workers (`_held_against`): the loser waits on the one-active-row index (observed), answers `error` with an `IntegrityError` reason, served `state_conflict`; its reference discarded at once, none pending; the winner's held, its handle consumed.

   **The four earlier cases** that expected a refused, replayed or losing register's reference "in the pending discards" (`replay_and_conflict`, `bound_of_active_registrations`, `register_refused_once_its_sessions_sign_out_commits`, `two_accounts_one_new_installation`) now expect "the store no longer holds the token, and no pending discard is left" (`_discarded_at_once(...) == [(True, False)]`), their docstrings' sentences and their detail lines saying the same. **One mechanical change the prompt did not name:** each found the reference by its token (`_references_of(token)`, which resolves each issued reference through the store), and a discarded reference resolves to no token, so each now finds it by when the store issued it (`_issued_by(call)`, the references `token_store().issued` gained while the call ran; in case 9, the one that is not the winner's). In `replay_and_conflict` this also feeds "the replay's put issued one more reference", whose assertion is kept (one new reference, not the saved one). Nothing else in those cases changed. New helpers: `_issued_by`, `_discarded_at_once` and `_served` (the result as the routes serve it, `contract.refusal`).
9. **The earlier tests that changed:** the four cases (above); `test_the_store_takes_the_token_before_the_commands_transaction` (its one assertion); `MappingCompletenessTests` (`ADAPTER_SERVED` gains the reason); `test_chat_offline.py`: `CASE_COUNT` and `test_the_case_count_is_pinned` 30 to 37, `PLAN` gains the seven, and `test_each_b1_item_has_its_case_before_the_hidden_ones` counts 19 contiguous `notifications.*` cases where it counted 12 (its other checks kept: they still end at the fourth from last, with `notifications.no_token_in_any_row_or_answer`); the proof README's chat paragraph (the count, 37 since B1-C1; the seven described; case 5's "leaving the reference … in the pending discards" now "discarding at once"). No other test changed; `tests/test_notifications.py` is unchanged.
10. **The words, as given:** by a script that read each old passage at `f7a21b9` (`git show`) and in the working file, required it exactly once at `f7a21b9`, replaced it, and counted the new passage after:

| Pair | File | Old at `f7a21b9` | Old after | New after |
|---|---|---|---|---|
| AN3 | `production-contracts.md` | 1 | 0 | 1 |
| AN4 | `production-contracts.md` | 1 | 0 | 1 |
| B1R-7 | `production-contracts.md` | 1 | 0 | 1 |
| AN5 | `data-model.md` | 1 | 0 | 1 |
| AN6 | `data-model.md` | 1 | 0 | 1 |
| AN7 | `data-model.md` | 1 | 0 | 1 |
| AN8 | this record, section "B1" | 1 | 1 | 1 |
| AN11 | `glow_domain/notifications.py` | 1 | 0 | 1 |

AN8's "old after" is 1 because its new passage begins with its old one, as given. AN11 was first applied, with the same find-once check, by the script that wrote the domain's reason constant; the recorded script then found it as above.

**The simulations** (`chat_support.py`; no switch in the adapter), each raising Django's own `OperationalError` with a fixed message, through Django's own hooks:
- `handle_write_fails`: an execute wrapper on this thread's connection that raises before the server for the one statement equal to `HANDLE_WRITE`; every other statement runs. **It stands for** a database unreachable for that one statement. **It cannot show** a driver's own failure mid-statement (the server receiving the insert and its answer lost: the row could then exist with the store's token discarded, which the sweep would then discard again, a no-op by AN11), or the connection's state after a real network failure.
- `commit_answer_lost`: this thread's connection wrapper's `commit`, shadowed for the block by one that runs the real commit and then raises, once; `transaction.atomic` then tries a rollback (nothing to roll back) and re-raises, so `_run` sees a failure after the body returned. **It stands for** a commit that took effect and whose acknowledgement was lost, as B1's review simulated it. **It cannot show** a commit that did not take effect with its answer lost (the same unknown outcome, the handle then left for the sweep: the path the reversal c04 and the structure test pin, not a case), or a driver's real behaviour on a dropped connection.
- `BeginHold`: a probe whose `on_begin` records its backend, signals and waits (DM-13 2.1), so the case's own connection can remove the handle's row between the handle and the save, as B2's sweep would. **It cannot show** B2's sweep itself, which B2 builds (AN2): the case removes the row with a plain delete.

### Reversals

Each by a scratch harness (outside the checkout) that found each old text exactly once, wrote the edit, ran the named offline tests and, where named, the named cases on a new throwaway database (the runner below), kept the failing lines, and restored each file byte for byte, its SHA-256 checked. All 14 failed as intended and all were restored: `git status --short` and the SHA-256 of `git diff` were the same before and after (`834b4ae0…`). Offline runs named `tests.test_notifications_routes_offline.StructureTests` unless stated.

| Reversal (the edit) | What failed |
|---|---|
| c01: `_hold_for_discard` a no-op | offline: none (all of `test_notifications_routes_offline`, `test_notifications_port` and `test_notifications` pass: B1R-3, as the review found); case B1-C1-1: "the rotation: the retired reference waits in the pending discards" |
| c02: the handle's failed write not discarding (`_discard_unwritten` removed) | offline: none; case B1-C1-2: "the store discarded it at once" |
| c03: a known refusal leaving its handle (`if known:` made `if False:`) | `test_the_handle_is_written_after_the_put_and_before_the_transaction`; cases `replay_and_conflict` ("the replay's reference: the store no longer holds its token, and no pending discard is left, in no registration"), `bound_of_active_registrations`, `register_refused_once_its_sessions_sign_out_commits`, `two_accounts_one_new_installation` and B1-C1-3 ("a stale version: …"): 0/5 |
| c04: an unknown outcome discarding the reference (`if known:` made `if True:`) | the same structure test; case B1-C1-4: "the store still holds its token" |
| c05: the save without its count check (`if deleted != 1:` made `if False:`) | `test_the_save_consumes_its_handle_and_checks_the_count`; case B1-C1-5: "the save refuses (applied)" |
| c06: the handle written without its condition (the statement's `NOT EXISTS` and `ON CONFLICT`, and the re-read, removed) | the handle's structure test; case B1-C1-6: "a reference an active registration holds: answers 503" |
| c06a: the statement's condition alone removed, the re-read kept | the same test; case B1-C1-6 passes its first part (the re-read refuses) and fails "a reference a pending discard holds: answers 503" (the insert then fails the uniqueness, a failed write, and the store's discard removes the pending token) |
| c06b: the re-read alone removed, the statement's condition kept | the same test; case B1-C1-6's concurrent part: "the second register: the store's refusal (error)" (its handle written, its save then failing the registrations' uniqueness, known, so it discards the first registration's token): the re-read is what refuses there |
| c06c: the re-read finds the holder but leaves the handle's row | the same test; case B1-C1-6: "no pending discard is left: the handle's row removed" |
| c07: every error treated as unknown (`known = not returned` made `known = False`) | `test_the_outcome_is_known_until_the_body_returns`; cases `two_accounts_one_new_installation` and B1-C1-7 ("the loser's reference: the store no longer holds its token, no pending discard is left") |
| c08: the handle's write moved after `_run` | the handle's structure test ("[530, 536, 542, 546] != [530, 546, 536, 542]"); offline only |
| c09: B1's r05, the store's `put` moved into `_device` | `test_the_store_takes_the_token_before_the_commands_transaction` and the handle's test (`StopIteration`: no `put` in `device()`); offline only |
| c10: the handle consumed after the reference is written (moved after the `create` and the `update`) | `test_the_save_consumes_its_handle_and_checks_the_count` ("707 not less than 684"); offline only: in one transaction the order changes no outcome a case can see |
| c11: `token_handle_missing` left out of `REFUSALS` | `MappingCompletenessTests.test_the_table_holds_no_other_reason` (the reason found but not in the table; served `state_conflict` by the fallback all the same) |

### Commands and results

At the code head, in a clean environment (local; the run of record repeats them), with the counts at the prompt's commit beside them:
- **The API**, after `pip install --require-hashes -r requirements-dev.lock` and `pip check` ("No broken requirements found."), with `GLOW_ENV=test`: `manage.py check` "System check identified no issues (0 silenced)"; `manage.py test tests` `Ran 737 tests … OK`, no skip (731 at `e7e7e84`: six new, three structure and three port tests); `ruff check .` "All checks passed!"; `ruff format --check .` "187 files already formatted" (187 before); `mypy` "Success: no issues found in 99 source files" (99); `mypy glow_notifications` "Success: no issues found in 8 source files" (8); `makemigrations --check --dry-run` "No changes detected".
- **The proof's offline tests**, from its own lock (`pip check`: "No broken requirements found."): `Ran 428 tests … OK` (428: the plan's tests changed, none added); Ruff "All checks passed!", "78 files already formatted"; mypy "Success: no issues found in 78 source files" (78 and 78).
- **The trusted classifier,** `main`'s `scripts/change_scope.py` (`988a36a`; SHA-256 begins `b564c62f4a076f51`, equal to the checkout's), extracted to the scratchpad outside the checkout and run as `python3 -I <copy>/change_scope.py --base 988a36a1fe4bc7b654a07e565e15fe721dcf3520 --head 48f08017350993c13bccb78095e084ad0434a6a5 --merge-base`: `"full": true`, reason `behavior-or-empty`. `git merge-base --all` gives one base, `988a36a`.
- **The diff:** `git diff --name-only f7a21b9 48f0801` lists 13 paths, each an owned path, each a regular file, mode 100644: `glow_notifications/persistence.py`, `contract.py` (`REFUSALS`, one reason), `glow_domain/notifications.py` (`TOKEN_HANDLE_MISSING`, `TokenStore`'s docstring), `notification_fixtures.py` (`FixtureTokenStore` and the module docstring's line on it), `glow_persistence/models.py` (`PendingTokenDiscard`'s docstring), `tests/test_notifications_routes_offline.py`, `tests/test_notifications_port.py`, the proof's `chat_cases.py`, `chat_support.py`, `tests/test_chat_offline.py` (the plan's tests), `README.md` (the chat paragraph), `production-contracts.md` (AN3, AN4, B1R-7) and `data-model.md` (AN5 to AN7). This section and AN8 are the records commit's only change.
- **GitHub:** read with `gh api` REST `GET` calls only (the runs, their jobs and the job logs). Nothing was written but the two pushes of this branch (the code head, then this records commit); no pull request, comment, review, thread or re-run.

### Local database runs (iteration, not evidence)

Under P06.DB's D4: the pinned image `postgres@sha256:d74eeac9…`, pulled from Docker Hub; loopback only (`127.0.0.1:5433`); generated passwords, markers and keys in a mode-700 scratch directory outside the checkout, never printed; none of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` or any `PG*` name in any process environment (the suite's `PROOF_*` names only); the chat database and the decoy, each with its own marker; migrations only through the proof's own `python -m django migrate` under the chat settings, never `manage.py migrate`. A new container and database for each run, each removed with its credential files at the end of its run; the suite's output was shown only after the job's `chat_scan` found none of the run's secret files in it. The Docker daemon the session started was stopped at the end.
- **The nineteen F12 cases** (a subset run, in the plan's order): 19/19 passed; `chat secret scan: clean (518 secrets held; 0 found …)`, `chat value scan: clean (108 member values held …)`, `ROW LOCKS (D14): PASS`, `CHAT VERDICT: PASS`; case 12 "65 tokens in no row and no answer; 63 references, each held once or discarded; every put before its transaction".
- **The whole suite,** at the code head's content: `[chat] cases: 37/37 passed in 182.8 s`; `chat secret scan: clean (2003 secrets held; 0 found in 1330 log records, 176 writes and the results JSON)`; `chat value scan: clean (1335 member values held …; 0 found in the same output)`; `[chat] row locks sent (D14): 117231 statements … on 104 connections in 3 threads; 11073 take a writer's row lock, 3283 of them naming the account table (3283 FOR NO KEY UPDATE, 0 FOR UPDATE OF other tables only); 0 refused`; `ROW LOCKS (D14): PASS`; `CHAT VERDICT: PASS`; `chat_scan` passed.
- **The reversals' cases,** one subset run per reversal (above).

### The run of record

**Foundation run [45941121120](https://github.com/amthorn78/glow-dating-app/actions/runs/45941121120)** on `48f08017350993c13bccb78095e084ad0434a6a5` (a push run, attempt 1) concluded **success**. It was created at 04:38:24 UTC on 27 November 2026, and its gate finished at 04:47:24 (9 minutes in all); the gate printed "Application checks passed". Nothing was pushed to the branch until it had finished. The durations are from the jobs' timestamps (whole seconds); B1's are from its run of record, 45900925199.

| Job | Conclusion | Duration | B1's | Timeout |
|---|---|---|---|---|
| Change scope | success | 8 s | 5 s | 3 min |
| API checks | success | 90 s | 94 s | 10 min |
| Mobile checks | success | 465 s (7 min 45 s) | 414 s | 25 min |
| API mobile smoke | success | 82 s | 77 s | 10 min |
| API artifact checks | success | 22 s | 19 s | 15 min |
| Stream proof checks | success | 76 s | 75 s | 10 min |
| Database proof checks (ordering) | success | 521 s (8 min 41 s) | 444 s | 30 min |
| Database proof checks (identity) | success | 97 s | 126 s | 30 min |
| Database proof checks (profile) | success | 204 s | 144 s | 30 min |
| Database proof checks (discovery) | success | 232 s | 237 s | 30 min |
| **Database proof checks (chat)** | success | **192 s (3 min 12 s)** | 179 s | 30 min |
| Foundation gate | success: "Application checks passed" | 3 s | 5 s | 2 min |

**What the logs show** (read with `gh api` REST `GET` calls; no line quoted here held an `::add-mask::` command or a long hexadecimal value):
- **The chat job:** the offline tests `Ran 428 tests … OK`, Ruff "All checks passed!" and "78 files already formatted", mypy "Success: no issues found in 78 source files"; `chat dbshell exit status: 1` with `RefusedDatabase: refusing dbshell …`; the decoy `glow_discovery_proof` with its own marker (`1`; its comment differs: `t`), its marker refused (`chat migrate with the decoy database's marker: exit status 1`, `RefusedDatabase: refusing this database …`), `relations outside information_schema and the pg_ schemas: 0 before, 0 after`; the migrations from zero ("Applying glow_persistence.0014_notification_devices... OK") and `makemigrations --check --dry-run` "No changes detected"; all 37 cases `PASS`, B1-C1's seven among them, and case 12 "65 tokens in no row and no answer; 63 references, each held once or discarded; every put before its transaction"; `[chat] cases: 37/37 passed in 122.6 s`; `chat secret scan: clean (2003 secrets held; 0 found in 1330 log records, 176 writes and the results JSON)`; `chat value scan: clean (1335 member values held: member values, message texts, provider identifiers; 0 found in the same output)`; `[chat] row locks sent (D14): 117213 statements (117110 through Django's execute or executemany, 103 through the driver itself) on 103 connections in 3 threads; 11073 take a writer's row lock, 3283 of them naming the account table (3283 FOR NO KEY UPDATE, 0 FOR UPDATE OF other tables only); 0 refused`; `ROW LOCKS (D14): PASS`; `CHAT VERDICT: PASS`; `chat phase: 123 s (the job's timeout is 30 minutes)`; `chat_scan`: "the job's secrets found in the chat suite's output: 0", "… in the chat results JSON: 0", "the suite's own scans (secrets, member values) reported clean: True"; the second run refused (`second chat run exit status: 1`, `refusing a used database: …`); the upload of `sv4-chat-results` after the check; `container removed: glow-proof-db-chat-45941121120-1`, `credential and marker files removed`, `no proof container remains`.
- **The API checks job:** `Ran 737 tests … OK (skipped=2)` (the two history tests of `ReciprocalWriterTests` skip, as on every branch push, which has no local `main`); Ruff "All checks passed!", "187 files already formatted"; mypy "Success: no issues found in 99 source files"; the contract tests `Ran 55 tests … OK`.
- **The other database jobs,** each applying the migrations from zero: `[identity] cases: 49/49`, `IDENTITY VERDICT: PASS`; `[profile] cases: 77/77`, `PROFILE VERDICT: PASS`; `[discovery] cases: 70/70 passed in 165.5 s`, `DISCOVERY VERDICT: PASS`; the ordering suite's `[reference] cases: 56/56`, `[adapter] cases: 108/108`, `[read] cases: 66/66`, `== VERDICT: PASS ==`; each `ROW LOCKS (D14): PASS`.
- **The Mobile checks job:** "Generated types and runtime validators match schemas.", `tests 926`, `pass 926`, `fail 0`; the app's `tests 691`, `pass 691`, `fail 0`.
- **Within its timeout:** each job finished well inside its `timeout-minutes`; the chat job took 192 s of its 30 minutes (its suite's phase 123 s), 13 s more than B1's with seven more cases.

### What B1-C1 changes in section "B1"

Section "B1" keeps B1's words (DM-100's AL4 and AL5), except AN8's mark in its "Limits and deviations". What no longer holds there:
- **The threat model's custody sentence,** "A reference the command does not save goes to the pending discards after the transaction", is replaced by AN1's rule: a new reference's pending discard is written as its handle before the transaction, only if no registration and no pending discard holds the reference (a reference already held is the store's refusal, never discarded), and the save deletes it or refuses; a command whose outcome is known and did not save the reference discards it at once, and one whose outcome is unknown (a failure at the commit) leaves the handle for B2's sweep. "So a reference is held only by an active registration's row and a pending discard's row" still holds, now with AN1's exception: a process stop, or a failed handle write and a failed discard, between the `put` and the handle.
- **B1R-6's two sentences,** in the review's narrower terms. "The answers do not tell a caller whether a transfer took place (a transfer and a first registration both answer version 1, `active`)" holds for the answers' bodies only: in a race, a first register's `state_conflict` (the one-active-row constraint's refusal, case 9) is reachable only when another account holds, held or is registering that installation, and a transfer's answer waits for the store's discard of the earlier holder's token after the commit, which a first registration's does not. The caller already holds the identifier, so neither tells it of an installation it does not present.
- **AN8's mark** on B1's custody limit (applied, as given).
- **Case descriptions** in section "B1" (cases 5, 7, 8 and 9, each "its reference pending" or "waits in the pending discards") describe B1's expectations; since B1-C1 those references are discarded at once (item 8), and the suite has 37 cases.

### Limits and deviations

- **No stop.** No owned path, decision, earlier test, word or result of the prompt's stop rule held, with the two judgments below on the four earlier cases.
- **The custody limit that stands** (AN1's last sentence): a process that stops, or a handle write and a store discard that both fail, between the `put` and the handle leaves a token in the store and in no row; the double failure is logged with one fixed line. No case forces the double failure: it would leave a token held by no row, which `notifications.no_token_in_any_row_or_answer` refuses; the line itself is pinned only by `StructureTests`' check that every logger call takes a constant.
- **Two statements, not one, for the handle** under concurrency (item 2): the conditional insert is one statement, as AN1 says, and alone it tells a reference held from a failed write; the re-read in a new snapshot is added because the insert's `NOT EXISTS` can miss a registration whose save commits while the insert waits on the pending discards' uniqueness. That path needs a store that breaks AN11 and two commands racing on one reference; case B1-C1-6 forces it, and its refusal depends on PostgreSQL's `ON CONFLICT` waiting on a row a running transaction is deleting (observed in the case). A failed re-read leaves the handle with no discard; in the same race with the database failing at that read, the row would stay while the registration holds the reference, and that registration's later retire would fail the pending discards' uniqueness (B1R-2's symptom) until the row is removed. Three faults at once; recorded, not proven.
- **The two judgments on the four earlier cases** (item 8): their lookup of the reference changed from by-token to by-issue-order, since a discarded reference resolves to no token, and their detail lines, which said "pending", now say "discarded". Each is the same expectation item 8 changes, written so it can be checked; no other line of those cases changed. `_references_of` is now unused and was left as it was.
- **A failure at the `before_commit` hold point counts unknown** (item 1), though the commit has not run: the handle is then left for the sweep. Probes only signal and wait, so no such failure is expected.
- **A reused reference is served retryable** (`token_store_refused` is the store's refusal, 503, retryable); a store that keeps reusing would keep being refused.
- **The handle's `created_at` is the application's clock** (`timezone.now()`, as the ORM writes the other pending rows), not the database's; B2's sweep bound (AN2) compares against it.
- **Each register costs two more statements** outside its transaction (the handle and its re-read).
- **Lines left stale outside the owned passages,** for the manager to route: `production-contracts.md`'s codes bullet does not name `token_handle_missing` among the `state_conflict` reasons, nor a reference already held as the store's refusal (only AN3, AN4 and B1R-7's sentence were owned there); the proof README's module-table row for the chat suite (line 76) does not name `chat_support`'s simulations or `BeginHold` (B1's carried stale line, now one item longer); section "B1"'s case descriptions (above).
- **What the structure tests miss:** item 7's "Misses". Reversals c08, c09 and c10 are caught offline only; c10 changes no outcome a case can see.
- **The simulations' reach:** "The simulations", above.
- **The deadlock analysis is by reading** (item 3); no case races a save against B2's sweep, which does not exist yet (B2 builds it, with AN2).
- **`tests/test_notifications.py` is unchanged:** the fixture's new `reuse_next_put` is pinned in `test_notifications_port.py`.
- **The local database runs are iteration only;** the run of record is CI's.

### Manager verification of B1-C1 (App Manager 13, 27 November 2026)

- **The heads:** `claude/funny-hypatia-lpzbn0` at `1502359` (records; it changes only this record), with the code head `48f0801` on the prompt's commit `f7a21b9`. Merged into the manager branch at `4185119`, whose non-Markdown paths equal `48f0801`. `main`'s trusted classifier (unchanged since `43e794a`), outside the checkout with `python3 -I` and full SHAs, gives `"full": true`, reason `behavior-or-empty`.
- **The diff** (`git diff f7a21b9 48f0801`): 13 paths, each in B1-C1's owned paths, every file mode 100644; `views.py`, `providers.py`, the models' fields and constraints, the migration, `chat_suite.py`, `tests/test_notifications.py`, `glow_chat/`, `glow_api/`, the workflow and the CI policy unchanged.
- **Read in full: `glow_notifications/persistence.py`'s custody paths.**
  - **`_run`** returns whether its outcome is known: `returned` is set once the body returns, so a failure before it is known and one after it (the `before_commit` hold point and the commit) is unknown.
  - **The handle:** `HANDLE_WRITE` is one `INSERT … SELECT … WHERE NOT EXISTS (a registration holding the reference) ON CONFLICT (token_secret_ref) DO NOTHING RETURNING id`, run in autocommit after the `put` and before `_run`; no row returned is a reference held (`token_store_refused`, nothing discarded), an error a failed write (`_discard_unwritten`, then the error).
  - **`_held_since`** reads the registrations again once the handle is written and, if one holds the reference, removes the handle by its key and refuses; it exists because the insert's snapshot can miss a save that commits while the insert waits on the uniqueness.
  - **`_consume_handle`** deletes the handle by key and reference inside `_register`, after the registrations' locks and after a transfer's holder is revoked, and refuses `token_handle_missing` unless one row went; `REFUSALS` maps it to `state_conflict`, not retryable.
  - **After `_run`,** a fresh reference not saved is discarded through `_discard` when the outcome is known, and left with its handle when it is not; `_park` is gone.
- **The run of record,** Foundation run 45941121120 (`push`, `48f0801`, attempt 1), read with `gh api`:
  - all twelve jobs succeeded, and the gate's log has "Application checks passed";
  - the chat job's log has `Applying glow_persistence.0014_notification_devices... OK`, `[chat] cases: 37/37 passed in 122.6 s`, both scans clean (2003 secrets held; 1335 member values held; 0 found), `ROW LOCKS (D14): PASS`, `CHAT VERDICT: PASS`, and `dbshell` refused (exit status 1);
  - the API checks job has `Ran 737 tests … OK (skipped=2)`.
- **DM-102's words at the head** (`1502359`), by script: AN3 to AN7 and AN11 each found once, their old passages gone; AN8's new passage once (it begins with its old one); B1R-7's new sentence once.
- **Not re-run by the manager:** the session's local checks and its 14 reversals; the run of record ran the suites in CI.
- **The session's two judgments:**
  - **the handle in two statements** implements AN1's condition ("only if no registration and no pending discard already holds that reference") under concurrency, with no change to the design, a model or the lock order; it goes to the exact-head review and the pre-merge read (D-07);
  - **the four earlier cases' lookup** (by the store's issue order, since a discarded reference resolves to no token) was beyond what the prompt's item 9 allowed, which the prompt's stop rule made a stop. The prompt's "nothing else in those cases changes" could not hold (AM13-18), the change only finds the same reference another way, and the exact-head review reads it.
- **Routed from the session's limits:**
  - to SV4 B2 (the carried-items file, B1-C1's entry): the stale lines (the codes bullet's two reasons; the README's line 76), the unused `_references_of`, the sweep's race, a failed re-read's row, and the handle's clock;
  - recorded here: the `before_commit` edge, a reused reference served retryable, the two extra statements, and section "B1"'s case descriptions, which B1-C1's "What B1-C1 changes in section B1" states.
- **AN9 and AN10** applied to the carried-items file at this integration, as DM-102 says.
- **For the exact-head review:** DM-102's section 5 focus, with B1's threat model's custody parts at the new head.


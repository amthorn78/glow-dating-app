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
- **The trusted classifier,** `main`'s `scripts/change_scope.py` (`c2cffbe`), run outside the checkout with `python3 -I --base c2cffbe… --head 3bf55de… --merge-base`: `"full": true`, reason `behavior-or-empty`.
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
| F3 | **For Dev Manager 6's pre-merge read** | The Chromium form, its timeouts included, is the carried text of DM-59 item 7, the Dev Manager's; no outcome gives a false pass. The manager recommends accepting it as carried, with the documentation's silence recorded here, and treating a Mobile run that fails at the Chromium step under OD-21 |
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
- **The trusted classifier,** `main`'s `scripts/change_scope.py` (`c2cffbe`), run outside the checkout with `python3 -I --base c2cffbe… --head c78f297… --merge-base`: `"full": true`, reason `behavior-or-empty`.
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

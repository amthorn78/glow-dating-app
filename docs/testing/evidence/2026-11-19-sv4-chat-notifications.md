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
- **Each run now pulls the PostgreSQL image four times**, once per job, where it pulled it once. Locally Docker Hub answered `429` to this sandbox's repeated pulls. Whether GitHub-hosted runners meet Docker Hub's pull limits was not checked. A `429` in CI would fail that job's start step, and would be a finding under OD-21.
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
  - every one of the old job's 30 steps is in a new job: 22 byte for byte, and the other 8 changed only as the split needs (the credentials and role-and-database steps per job; the three marker-and-migrations steps, now refusing the decoy and counting relations before and after; the profile and discovery suite steps, whose comments alone change). The new steps are each job's `dbshell` refusal and decoy;
  - the action pins and the PostgreSQL image's digest are the same set;
  - the gate's `needs` and its results loop name the four jobs, and nothing else in it changes;
  - Mobile checks gains exactly the carried Chromium retry (`id: chromium`, `continue-on-error: true`, `timeout-minutes: 10`; a 60-second pause and one retry with `timeout-minutes: 6`, each under `if: steps.chromium.outcome == 'failure'`, the retry without `continue-on-error`), and its other steps and settings are unchanged;
  - each credentials step masks five values before anything prints, and its `echo` lines print a directory, a container name and a refusal only.
- **The run of record,** Foundation run 44463105633 (event `push`, head `3bf55de`), read with the GitHub tools: all eleven jobs succeeded, among them the four database jobs, and the gate's log ends "Application checks passed".
- **The scans:** each `VALUE_FILES` and `KEY_FILES` now names its own job's files only, the decoy's marker in the earlier suite's file name, as the CI policy's new paragraph says.
- **For the exact-head review (AG21), noted, not decided here:**
  - whether a step killed by its own `timeout-minutes` has the outcome `failure`, on which the Chromium retry depends (the record's limits);
  - four pulls of the PostgreSQL image per run, where there was one;
  - the decoy's marker is one the job generates in the earlier suite's form (`glow-ordering-proof:` for the identity job), not that suite's own marker, which only a shared PostgreSQL held; AG1's words are "carrying another suite's marker";
  - the three proof offline test files' module docstrings still describe the shared job, outside A0's owned lines.

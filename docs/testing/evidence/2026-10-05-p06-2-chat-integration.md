# P06.2 evidence: chat integration

This is the evidence record for [P06.2](../../planning/p06-2-chat-integration.md), the chat integration (brief revision 2; OD-38). It records observations only and is not an instruction source. One section per stage.

- **Work item:** P06.2, chat integration, brief revision 2 (5 October 2026, App Manager 6).
- **Stage A prompt:** revision 1, from commit `2f982aebc6cdc9bc4d5dc69a343ec3d364834cf8` (`docs/ephemeral/2026-10-05-p06-2-stage-a-implementation-prompt.md`).

## Stage A

The server and database stage, offline (`Glow App - No Stream`): P06.DB's carried items 1 to 6, the contact port and the app's persistence adapter, migration `0003`, the suite on two subjects, the outbox with a fixture chat provider, the token rules and the sealed runtime. No provider was called, no database but a disposable one was opened, and no dependency was added.

- **Start:** `2f982aebc6cdc9bc4d5dc69a343ec3d364834cf8` (the manager branch `claude/magical-wozniak-yfmmx2`'s head when the session began; `main` was `3afffb30205563932ebd05d5d41cca6d569663a3`).
- **Session branch:** `claude/dazzling-lovelace-f2mtts`, fast-forwarded to the start.
- **Code head:** `3b9212236127638f9cd913927b3d382f1dca8202` (tree `f3b46e4728ab5356c53399750d453c33a08f961b`), 49 paths, +5,945 and −179.
- **Run of record:** none yet. Foundation push run 467 (run 37372546600) on the code head: the four application jobs that got a runner succeeded, the database job included, but Change scope, API mobile smoke and Stream proof checks never got a runner and were cancelled after 15 minutes queued, so the gate failed (`AssertionError: Change classification failed`), not `Application checks passed`. See the run's section and "Deviations, findings and limits".
- **Records commit:** the commit that adds this record. It changes only Markdown, so its push run skips the application jobs by the CI policy's design; the evidence of record is the push run of the code head. I pushed it only after that run had finished (AM5-14).
- **Times:** 5 October 2026, UTC.

### Environment check (names only)

| Check | Result |
|---|---|
| `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` | none present (the loop printed nothing) |
| `PG*`, `PROOF_DB_*`, `STREAM_*` names | none (`compgen -e \| grep -E '^(PG\|PROOF_DB_\|STREAM_)'` printed nothing, exit 1) |
| `command -v python3.12` | `/root/.local/bin/python3.12`, Python 3.12.14 (`$HOME/.local/bin` first on PATH); Node 24.19.0, npm 11.9.0 |
| `docker info` | exit status 1 (the CLI exists; no daemon) |
| `command -v initdb pg_ctl postgres pg_isready psql` | `pg_isready` and `psql` at `/usr/bin`; `initdb`, `pg_ctl`, `postgres` not on PATH, present in `/usr/lib/postgresql/16/bin/` (PostgreSQL 16.14) |

### Start gate

`git merge --ff-only 2f982ae…` fast-forwarded; `git rev-parse HEAD` printed `2f982aebc6cdc9bc4d5dc69a343ec3d364834cf8`; `git diff --stat 2f982ae… origin/claude/magical-wozniak-yfmmx2 -- services/ proofs/ .github/ docs/architecture/` printed nothing; `git cat-file -e origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md` exited 128 (absent). The prompt was current.

### Items 1 to 11

Paths are under `proofs/postgres-ordering/` (the proof) or `services/api/` (the API) unless given whole.

| Item | Done where | Test |
|---|---|---|
| **1. A used database is refused** | `glow_ordering_proof/observe.py:97` `used_database_reasons`: a proof table (`proof_writer_log`, `proof_adapter_call`, `proof_world`) that holds a row, or any `glow_persistence_appaccount` row, is a reason. `__main__.py:43` `refuse_used_database`, called by `run` (`:144`) after the server checks and before anything is written; it prints `refusing a used database: …` and exits 1. CI: a new step runs `run` a second time on the used database and requires a non-zero exit, the refusal line, and the same row counts before and after | `tests/test_p06_2_suite.py`, `UsedDatabaseTests`: a new database passes; each proof table with a row, and an app account, refuse; `run` returns 1 with the refusal and never reaches the suite |
| **2. `dbshell` is refused** | The proof package is now an installed app (`glow_ordering_proof/apps.py`, `settings.py:47`) whose `management/commands/dbshell.py:21` replaces Django's: `handle` raises the marker's `RefusedDatabase` (`marker.py:69` `refuse_dbshell`, `DBSHELL_REFUSAL` `:38`), naming `PROOF_DB_MARKER` and no value, before any connection. CI: a new step before the migrations runs `python -m django dbshell < /dev/null` and requires a non-zero exit and the refusal line | `tests/test_marker_commands.py`, `DbshellRefusalTests`: through Django's real command path with the fake server, `dbshell` (with and without psql arguments) exits non-zero with the refusal for the run's marker, another marker and no row; no statement ran, no connection was kept, and psql's `runshell` was never reached; `get_commands()['dbshell']` is `glow_ordering_proof` |
| **3. The oracle checks who sent (CX1)** | `oracle.py:681` and `:683`, rule O9: a submission's actor is its session's account and a member of its match. Two planted controls, `oracle.misattributed_actor` (the other member, with the sender's session) and `oracle.non_member_actor` (`planted.py`), run on both subjects | `tests/test_oracle_p06_2.py`, `SenderRuleO9Tests`; `tests/test_p06_2_suite.py`, `PlantedPlanTests`; in the job, both planted controls flagged O9 on both subjects |
| **4. The session-expiry rule (CX2)** | P06.DB 5.2 kept: the check at a time read after the locks. O5 narrowed (`oracle.py:485` `_o5`, `:668`): a submission committed at or after its session's expiry is a violation only when its checks must have run after the expiry, because its transaction began at or after it, or a writer of a row it locks ended inside its transaction at or after it. The forced case `named.session_expires_after_check` (`cases.py:1018`, both subjects) holds the send between its checks and its commit (the adapter's `before_commit` probe; for the reference design the proof log's hook just before its send row, `observe.py`, so `reference.py` is unchanged) until the database clock passes the expiry | `tests/test_oracle_p06_2.py`, `NarrowedO5Tests`: checked before and committed after is clean; began after, or waited past the expiry on a writer of its rows (the `transaction_start_time` control's shape), is O5; other writers are not. In the job: the boundary case authorized and committed after the expiry with no violation, and the `transaction_start_time` control still met O5 |
| **5. The domain port and the persistence adapter** | The port: `glow_domain/chat.py:125` `ContactPersistence` (send, block, unblock, unmatch, suspend, delete, sign-out, administrative expiry, pause, resume, restriction, consent withdrawal and acceptance, match activation, session opening). The adapter: `glow_chat/contact.py:95` `OrmContactPersistence`, P06.DB D5 as written (`_run` `:118`, `_lock` by key `:155`, `send` `:316`, `block` `:444`, `unmatch` `:549`, `_revoke_account` `:597`, `_end_session` `:284`); D5's writers `_set_profile` `:672` and `_decide_consent` `:721` lock the account row first and bump the profile's version or append the next consent decision; the send reads both under its account locks | The adapter's run in the job: every case, the races and the oracle (below). `tests/test_model_definitions.py`, `test_the_chat_adapter_loads_without_a_connection_and_has_no_switch`; `tests/test_chat_domain.py`, `ContactPortTests` |
| **6. New models and migration `0003`** | `glow_persistence/models.py:570` `ChatIdentity` (account, provider, `user_ref` from `secrets.token_hex(16)`, state, token cut-off) and `:596` `ChatReadCursor` (match, member, last read submission); `migrations/0003_chat_identity_read_cursor.py`, two `CreateModel` operations; `0001` and `0002` byte-identical | `tests/test_model_definitions.py`: 34 models, no drift; `test_migration_0003_is_additive_and_0001_0002_are_unchanged` (pinned SHA-256 of `0001` and `0002`, `0003`'s operations, constraints and fields); `test_makemigrations_check_passes_without_a_database`. In the job: the migrations apply from zero with `0003`, and `makemigrations --check --dry-run` finds no change |
| **7. The suite on two subjects** | `__main__.py` `run_subject` and `run_suite`: the reference design, then the adapter (`adapter.py` `AdapterSubject`, `AdapterFixtures`), each with its own evidence reader (`evidence.py`), its own report and verdict; the reference keeps its ten controls; both get the planted oracle controls; the adapter adds D5's 24 forced cases, `named.d5_restored` and three D5 races. Per-order counts (`stress.py:189` `commit_order`, `:354`) and the seeded delay in the session races (`:320` to `:324`, up to 8 ms on about half the iterations). The budget is unchanged: 200 iterations or 30 s per race; the timeout stays 20 minutes | `tests/test_p06_2_suite.py`: `PerIterationCallSiteTests` (R3), `EmptySignalTests` and `SignInExclusionTests` for both readers (R4), `CommitOrderTests`, `SeededDelayTests`, `RunVerdictTests`; `tests/test_case_plan.py`, `test_the_adapter_plan_adds_d5`; `tests/test_budget.py` |
| **8. Outbox and delivery against a fixture provider** | The provider port `glow_domain/chat_provider.py:77` (five operations, identifiers and members only, Glow codes only); the fixture adapter `chat_provider_fixtures.py:69`; match activation (`contact.py:193`) commits the binding, the random channel and user IDs and `match_activated` together; the events (`glow_chat/events.py`) and the delivery (`glow_chat/delivery.py:100`: `_deliver` `:273` leases one event by key, makes one call and records the receipt; `deliver_due` `:355` in order, stopping at a retry) | `tests/test_chat_domain.py`, `ProviderPortTests`, `FixtureProviderTests`; in the job, the delivery phase (below) |
| **9. The token rules** | `glow_domain/chat_tokens.py:52` `grant_chat_token`: one hour (`:21`), only for a `valid`, unexpired, current-epoch session of an `active` account with an active chat identity | `tests/test_chat_domain.py`, `TokenRuleTests` |
| **10. The runtime stays sealed** | No runtime module changed | `tests/test_chat_sealed_runtime.py`: in a clean subprocess, the runtime settings, URL configuration and WSGI application load no `glow_chat`, `glow_persistence` or `psycopg` module; the engine is `django.db.backends.dummy`; `ensure_connection()` raises `ImproperlyConfigured`; `FORBIDDEN_CONNECTION_NAMES` equals the set pinned at P06.2's start and each name refuses without echoing its value; a process with `DATABASE_URL` does not start |
| **11. The documents** | `docs/architecture/data-model.md` (the two models, the consent purpose `onboarding`, the adapter, the event table and the delivery flow, the token rules) and `docs/architecture/interactions-fixtures.md` (what P06 and P11 now hold); also the proof's README and the API's README | Documentation |

**The choices the prompt asks to record.**

- **Item 1: the refusal, not run tags.** A refused database leaves the fixed run tags readable in the log and the oracle's "every row" meaning every row of this run; per-run tags would still let the final oracle read an earlier run's rows. App accounts count as well as the proof tables, because the adapter's evidence is in app tables. The CI job always gets a new database; the refusal makes the same true for local runs.
- **Item 2: the proof package as an installed app.** Django resolves a command name to an installed app's command before its own, so every route to `dbshell` under the proof's settings loads the proof's, and nothing in Django is patched. It refuses before any connection rather than checking the marker first: `psql` would open its own connection outside Django even after a passed check, so no form of `dbshell` is safe under these settings.
- **Item 5: a new package, `glow_chat`, not `glow_persistence`.** The model registry stays definitions only (its static check still forbids every connection), and the sealed runtime test names one package the runtime must never load. The adapter detects a deadlock by its SQLSTATE (`40P01`) rather than importing the driver, which the API does not install.
- **Item 6: the consent purpose is `onboarding`** (`glow_domain.chat.ONBOARDING_CONSENT_PURPOSE`), F02's `ConsentIntent`, which carries no purpose of its own. The identity's account FK is PROTECT, so the mapping outlives the account row until the provider deletion step that needs it.

### The Foundation run on the code head: run 37372546600 (not a run of record)

Push run 467, `https://github.com/amthorn78/glow-dating-app/actions/runs/37372546600`, created 20:53:46 UTC on `3b92122…`. I pushed nothing while it ran.

| Job | Conclusion |
|---|---|
| Change scope | **cancelled** (job 111973021192): created 20:53:47, cancelled 21:08:48; the API lists no runner and no step, so it never ran |
| API checks | success (job 111978034140; 21:09:04 to 21:09:25) |
| Mobile checks | success (job 111978034189; 21:13:58 to 21:18:04) |
| API mobile smoke | **cancelled** (job 111978034130): created 21:08:48, cancelled 21:23:50; no runner, no step |
| API artifact checks | success (job 111978034240; 21:19:06 to 21:19:33) |
| Stream proof checks | **cancelled** (job 111978034235): created 21:08:48, cancelled 21:23:50; no runner, no step |
| Database proof checks | success (job 111978034228; created 21:08:48, started 21:19:00, finished 21:25:14; the suite step 21:19:51 to 21:25:11, 5 min 20 s) |
| Foundation gate | **failure** (job 111983886702, 21:25:22 to 21:25:25). Its `RESULTS` gave `scope`, `smoke` and `proof` as `abandoned` and the other four as `success`; its first assertion failed: `AssertionError: Change classification failed` |

**The run-level conclusion is `failure`, and the gate did not print `Application checks passed`.** The three cancelled jobs never started: each waited about 15 minutes for a runner and was cancelled with no step run. The other jobs waited too (the database job 10 minutes). Because `scope` did not succeed, the workflow's fail-closed condition (`needs.scope.result != 'success'`) released all six application jobs as full scope, which is the classification the trusted policy gives this change (Checks, below); four of the six got a runner. The manager branch's push run 37366154754, earlier the same evening, ended the same way (its gate queued 15 minutes, then cancelled). I re-ran and dispatched nothing (the prompt forbids it), and I pushed no code commit only to trigger CI. A run of record needs a re-run of this run's failed jobs by Nathan or the manager, or the pull-request run after integration; see "Deviations, findings and limits".

The database job, which carries this stage's evidence, completed every step with `success`. **From its log** (1,289 lines, read whole):

- **The offline checks in the job.** `pip install --require-hashes` and `pip check` (`No broken requirements found.`); the offline tests under `env -i`: `Ran 142 tests`, `OK`; Ruff `All checks passed!`, `42 files already formatted`; mypy `Success: no issues found in 42 source files`.
- **The credentials and the role.** The credential step printed one line (`credentials generated into a directory readable only by this job's user`), the role step one line (`role glow_proof (NOSUPERUSER) and database glow_proof created, with the run's marker as its comment`).
- **The image and the server.** `Digest: sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`, the pinned digest; container `glow-proof-db-37372546600-1`; `127.0.0.1:5432 - accepting connections` inside the container. `SELECT version()`: `PostgreSQL 17.11 (Debian 17.11-1.pgdg13+2) on x86_64-pc-linux-gnu, compiled by gcc (Debian 14.2.0-19) 14.2.0, 64-bit`. `track_commit_timestamp` `on`; `default_transaction_isolation` `read committed`, and `read committed` inside a writer's transaction; `deadlock_timeout` `1s`; `current_user` `glow_proof`, `superuser` `false`, `current_database` `glow_proof`. Each subject's report prints the same facts.
- **The wrong-marker step** (unchanged from C2): relations per schema before and after the `migrate` with a well-formed other marker, `information_schema` 69, `pg_catalog` 266, `pg_toast` 80, `public` 0 both times; `relations outside information_schema and the pg_ schemas: 0 before, 0 after`; `to_regclass('public.django_migrations') IS NULL after: t`; exit status 1; the refusal `glow_ordering_proof.marker.RefusedDatabase: refusing this database: its comment is not the run's marker (PROOF_DB_MARKER): the database's comment is different. …`.
- **The new `dbshell` step** (item 2), before the migrations: `dbshell exit status: 1`; `refusal: glow_ordering_proof.marker.RefusedDatabase: refusing dbshell under the proof's settings (PROOF_DB_MARKER): it starts psql outside Django, where the run's marker is never checked; no …` (the line is cut at the log's width).
- **The migrations** (item 6). `migrate` applied all seventeen from zero, `glow_persistence.0003_chat_identity_read_cursor... OK` last; the ledger shows `0001_event_infrastructure` 21:19:48.189689, `0002_app_domain` 21:19:50.473577, `0003_chat_identity_read_cursor` 21:19:50.533938. `makemigrations --check --dry-run`: `No changes detected`.
- **The marker on every connection.** `database marker verified on a new connection` once for `migrate` (backend pid 129), once for `makemigrations` (130), once for `facts` (131), and five times for `run`: the main thread (132) and `proof-writer-0` to `proof-writer-3` (133, 134, 136, 135), all before `[reference] cases: 56/56 passed`. No such line follows, so neither subject, no case, race, control or planted control, and not the delivery phase opened another connection.

#### The reference design (`== VERDICT: PASS (reference) ==`)

- **The cases:** `cases: 56/56 passed`: P06.DB's 55, unchanged, and the CX2 boundary case. **Observed waits with their blocking backends:** each of the 25 held cases (the twenty `send_holds` and `revocation_holds` cases, `racing_duplicates`, `session_expires_during_wait` and the three pairwise opposing-writer cases) shows `pid 134 wait_event_type=Lock wait_event=transactionid pg_locks not granted: transactionid/ShareLock pg_blocking_pids=[133] (holder pid 133)`, after 1 poll (9 cases), 2 (14) or 3 (2), the same distribution as C2's run. In each `send_holds` case the commit timestamps put the send before the revocation. `named.session_expires_after_check` (CX2): `short-lived sign-in: applied; released after the database clock passed the session's expiry; the send whose checks ran before the expiry: authorized; committed …`. The case passes only if the send's transaction began before the expiry, the send was held at its hold point until the database clock passed the expiry, it was authorized, and its commit timestamp is at or after the expiry (`cases.py:1047` to `:1066`).
- **The stress run** (seed 20260929; budget 200 iterations or 30 s per race; floors 50 iterations and 10 overlaps), every race with 0 violations and 0 harness failures and its floors met, against C2's run of record (37262466651):

| Race | Iterations | Overlaps (C2 → now) | Seconds (C2 → now) | Commit order now | Outcomes now |
|---|---|---|---|---|---|
| `race.block_by_low` | 200 | 200 → 200 | 5.2 → 5.5 | revocation first 165, send first 35 | send authorized 35, refused `match_not_active` 165; block applied 200 |
| `race.block_by_high` | 200 | 200 → 200 | 5.2 → 5.4 | 161, 39 | authorized 39, refused 161 |
| `race.unmatch_by_low` | 200 | 200 → 200 | 4.9 → 5.1 | 145, 55 | authorized 55, refused 145 |
| `race.unmatch_by_high` | 200 | 200 → 200 | 5.0 → 5.0 | 151, 49 | authorized 49, refused 151 |
| `race.suspend_low` | 200 | 199 → 199 | 4.4 → 4.5 | 165, 35 | authorized 35, refused `account_not_active` 165 |
| `race.suspend_high` | 200 | 199 → 199 | 4.3 → 4.4 | 187, 13 | authorized 13, refused 187 |
| `race.delete_low` | 200 | 200 → 200 | 4.7 → 4.7 | 162, 38 | authorized 38, refused 162 |
| `race.delete_high` | 200 | 200 → 200 | 4.5 → 4.7 | 183, 17 | authorized 17, refused 183 |
| `race.sign_out_sender` | 200 | 197 → 199 | 4.2 → 4.7 | 146, 54 | authorized 54 (C2: 0), refused `session_not_valid` 146 |
| `race.expire_sender` | 200 | 199 → 199 | 4.3 → 4.7 | 145, 55 | authorized 55 (C2: 1), refused 145 |
| `race.racing_duplicates` | 200 | 200 → 200 | 6.3 → 6.5 | `send_a` first 128, `send_b` first 72 | one authorized and one replayed in every iteration |
| `race.opposing_writers` | 200 | 200 → 200 | 7.1 → 7.6 | revocation first 199, send first 1 | send authorized 1, refused `match_not_active` 192, `account_not_active` 7; both blocks and the suspension applied 200 |

  In every race the commit-order counts equal the outcome counts: each send that committed first was authorized and each that committed after its revocation was refused. The seeded revocation delay (carried item 2) now gives both session races send-first iterations: 54 and 55, where C2 had 0 and 1 (R1).
- **The ten negative controls,** unchanged, each `failed as intended` by its declared signal:

| Control | Declared signal | Signal in the run |
|---|---|---|
| `no_locks.forced` (`unmatch_by_high.send_holds`) | `commit_after_revocation` + `wait_not_observed` + oracle O2/O6 | not observed waiting on the holder; the send committed 21:21:02.951752 after the revocation at 21:21:02.945348; oracle 2 violations (O2, O6) |
| `no_locks.stress` (`race.block_by_high`) | oracle O2/O6 | first failing iteration 1: the block (v2) committed 21:21:03.233915, the send at v1 21:21:03.234227; O2, O6 |
| `no_version_check` (`named.stale_contact_version`) | `refusal_missing` | the sends at versions ahead and behind were authorized; oracle 0 |
| `no_session_lock` (`sign_out_sender.send_holds`) | `commit_after_revocation` + `wait_not_observed` + oracle O3 | not observed waiting; the send committed 21:21:03.761367 after the sign-out at 21:21:03.755221; oracle 1 (O3) |
| `transaction_start_time` (`named.session_expires_during_wait`) | `refusal_missing` + oracle O5 | the send whose session expired while it waited was authorized; oracle 1 (O5), under the narrowed O5 |
| `dedup_before_authorize` (`named.retry_after_revocation`) | `refusal_missing` | the retry after the revocation was `replayed` with the old receipt |
| `inverted_lock_order` (`named.opposing_first_lock_block_high_vs_send`) | `deadlock` | `deadlock:DeadlockDetected` for the send |
| `no_account_lock.forced` (`suspend_high.send_holds`) | `commit_after_revocation` + `wait_not_observed` + oracle O4 | not observed waiting; the send committed 21:21:08.957628 after the suspension at 21:21:08.951439; oracle 1 (O4) |
| `no_account_lock.stress` (`race.suspend_high`) | oracle O4 | first failing iteration 1: the suspension committed 21:21:09.231641, the send 21:21:09.237400; O4 |
| `filter_state_in_lock` (`unmatch_by_high.revocation_holds`) | `refusal_missing` + oracle O2/O6 | the send that arrived while the unmatch held was authorized and committed; oracle 2 (O2, O6) |

- **The planted oracle controls** (subject-independent, `planted.py`), each `flagged as intended`: `oracle.misattributed_actor` O9 (1 violation), `oracle.non_member_actor` O9 (2), `oracle.send_after_contact_revocation` O2 (2: O2, O6), `oracle.send_after_session_end` O3 (1), `oracle.send_after_account_revocation` O4 (1), `oracle.send_after_expiry` O5 (1), `oracle.wrong_contact_version` O6 (1), `oracle.witness_in_another_transaction` O1 (1), `oracle.unwitnessed_revocation` O0 (1).
- **The oracle over every row:** 643 submissions (C2: 526) and 2,697 revocation rows (C2: 2,694) examined; `design:forced` 33 (C2: 32; the boundary case adds one), `design:stress` 591 (C2: 483, the count of authorized sends, which the races decide), the controls 1 or 2 each; **violations in the design's rows: 0**. Violations only under control tags: the ten controls' as in C2 (`no_locks.forced` 2, `no_locks.stress` 2, `filter_state_in_lock` 2, `no_session_lock` 1, `no_account_lock.forced` 1, `no_account_lock.stress` 1, `transaction_start_time` 1), and each planted control's as above.

#### The app's adapter (`== VERDICT: PASS (adapter) ==`)

- **The cases:** `cases: 81/81 passed`: the 55, the CX2 boundary case, D5's 24 (a pause, a restriction and a consent withdrawal, each of the sender's and of the other member's, in the four interleavings) and `named.d5_restored`. **Observed waits:** each of the 37 held cases (the 25 above and the twelve D5 `send_holds` and `revocation_holds` cases) shows `pid 134 … pg_blocking_pids=[133] (holder pid 133)`, after 1 poll (15 cases), 2 (20) or 3 (2). Each D5 `revocation_holds` case refused the waiting send (`profile_unavailable` for pause and restriction, `consent_not_current` for withdrawal); each D5 `send_holds` case committed the send before the writer. `named.session_expires_after_check` passed as on the reference, held at the adapter's `before_commit` probe. `named.d5_restored`: `pause the other member's profile: applied; repeated pause: no_change:already_paused; send while paused: refused:profile_unavailable; resume: applied; send after …` (cut at the table's width).
- **The stress run** (the same seed, budget and floors), every race with 0 violations, 0 harness failures and its floors met:

| Race | Iterations | Overlaps | Seconds | Commit order | Outcomes |
|---|---|---|---|---|---|
| `race.block_by_low` | 200 | 200 | 9.2 | revocation first 166, send first 34 | send authorized 34, refused `match_not_active` 166 |
| `race.block_by_high` | 200 | 200 | 9.2 | 162, 38 | authorized 38, refused 162 |
| `race.unmatch_by_low` | 200 | 200 | 8.8 | 147, 53 | authorized 53, refused 147 |
| `race.unmatch_by_high` | 200 | 200 | 8.8 | 151, 49 | authorized 49, refused 151 |
| `race.suspend_low` | 200 | 200 | 8.4 | 168, 32 | authorized 32, refused `account_not_active` 168 |
| `race.suspend_high` | 200 | 200 | 8.5 | 185, 15 | authorized 15, refused 185 |
| `race.delete_low` | 200 | 200 | 8.8 | 164, 36 | authorized 36, refused 164 |
| `race.delete_high` | 200 | 200 | 8.6 | 183, 17 | authorized 17, refused 183 |
| `race.sign_out_sender` | 200 | 199 | 8.7 | 146, 54 | authorized 54, refused `session_not_valid` 146 |
| `race.expire_sender` | 200 | 199 | 8.9 | 148, 52 | authorized 52, refused 148 |
| `race.racing_duplicates` | 200 | 200 | 11.5 | `send_a` first 128, `send_b` first 72 | one authorized and one replayed in every iteration |
| `race.opposing_writers` | 200 | 200 | 11.5 | revocation first 199, send first 1 | send authorized 1, refused `match_not_active` 193, `account_not_active` 6; no deadlock |
| `race.pause_high` | 200 | 200 | 9.3 | 178, 22 | authorized 22, refused `profile_unavailable` 178; pause applied 200 |
| `race.restrict_low` | 200 | 200 | 9.2 | 168, 32 | authorized 32, refused `profile_unavailable` 168 |
| `race.withdraw_high` | 200 | 200 | 9.3 | 182, 18 | authorized 18, refused `consent_not_current` 182 |

  The adapter's races run slower than the reference's (8.4 to 11.5 s against 4.4 to 7.6 s); none approached the 30-second cap. As on the reference, the commit-order counts equal the outcome counts in every race.
- **No fault switches, so no reference controls** (D3 2.1). **The planted oracle controls on the adapter's rows,** each `flagged as intended`: the nine above with the same rules and counts, and D5's two, `oracle.send_while_paused` O10 (1) and `oracle.send_after_consent_withdrawn` O10 (1).
- **The oracle over every row:** 710 submissions and 10,341 revocation witnesses examined; `design:forced` 47, `design:stress` 653, each planted control 1; **violations in the design's rows: 0**. Violations only under the planted controls' tags, as above.

#### The delivery phase (`== VERDICT: PASS ==`, the run's own)

- **The drain:** `drained 6906 events in 59.1 s; outcomes: access_revoked=delivered:1031, contact_revoked=delivered:1033, match_activated=delivered:3101, message_submitted=dead_letter:2, message_submitted=delivered:708, session_epoch_bumped=delivered:1031`; `dead letters (the planted controls' worlds only): message_submitted:channel_unavailable:1, message_submitted:member_unavailable:1`.
- **The seven checks,** each `PASS`:

| Check | Detail as printed |
|---|---|
| drain | 6906 events in 59.1 s; 0 chat events left; 0 stalled passes |
| end state of every design world | 3090 worlds, 6180 accounts (1030 deactivated), 700 messages; as the database says |
| identifiers and members only | 6904 provider calls, operations `create_channel`, `deactivate_user`, `remove_members`, `revoke_user_tokens`, `send_message`; no name, image or custom field, and no invite, call, feed or activity |
| delivery of each event kind | channel created with exactly the two members, message sent with its committed ID, both members removed on a block with the history kept, user deactivated and its tokens revoked at the epoch bump's time |
| a retry after a fixture failure | a failed channel creation retried with the same channel ID (one channel); a lost answer to a send retried with the committed message ID (one message, the retry found it); provider text mapped to `provider_unavailable` and kept nowhere |
| a revocation after the authorization, before the delivery | the authorization committed first, so its message was delivered into the history, then both members were removed; it stays accepted in Glow's record, no member can read the channel, and nothing re-sends it |
| a dead letter after the last attempt | after 5 failed attempts the event is dead-lettered and the binding failed; a send to it is refused |

- The counts agree with each other: 3,101 activations are the 3,090 design worlds and the 11 planted worlds; 710 submitted messages (708 delivered, 2 dead letters) are the adapter oracle's 710 submissions.

#### After the suite

- **The used-database step** (item 1): `rows (proof log, adapter calls, worlds, app accounts, outbox events) before: 10325 12891 5590 11182 18968; after: 10325 12891 5590 11182 18968`; `second run exit status: 1`; `refusal: refusing a used database: proof_writer_log already holds rows; proof_adapter_call already holds rows; proof_world already holds rows; glow_persistence_appaccount already holds rows. The proof runs once per new disposable database.`
- **The results JSON:** artifact `p06-db-proof-results`, ID 11371136745, 14,771 bytes. I did not download it.
- **Disposal:** `container removed: glow-proof-db-37372546600-1`, `credential and marker files removed`, `no proof container remains`.
- **No password, no marker, and no mask where either would be.** The log's only `***` are on lines 38 and 152 (the `token` inputs of `actions/checkout` and `actions/setup-python`) and line 94 (checkout's git `AUTHORIZATION: basic ***` header), all before the credential step. The only long hexadecimal runs are 40 characters (the head commit and action commits, 15) and 64 (the image digest 5 times, the container's ID once, the artifact's digest once): no standalone 32- or 48-character run. The words "password", "passfile" and "marker" appear only in the workflow's own script text, the offline tests' names, the steps' fixed messages and the refusal and verification lines, none with a value. The second run's and `dbshell`'s output went to files in the job's directory, which the steps grep and remove.

#### The API checks job

`Ran 13 tests`, `OK` (the candidate scope policy's tests); `pip check`: `No broken requirements found.`; `System check identified no issues (0 silenced).`; `Ran 277 tests`, `OK`, among them `test_chat_sealed_runtime` (four tests), `test_migration_0003_is_additive_and_0001_0002_are_unchanged`, `test_makemigrations_check_passes_without_a_database` and `test_the_chat_adapter_loads_without_a_connection_and_has_no_switch`; Ruff `All checks passed!`, `68 files already formatted`; mypy `Success: no issues found in 37 source files`; the contracts' `Ran 38 tests`, `OK`. The log (709 lines) has three `***` (the same token inputs and header) and no hexadecimal run longer than 40 characters.

### Local runs (iteration, not evidence)

Docker does not work in the sandbox, so I used a throwaway cluster, as P06.DB-C2 did. It ran PostgreSQL 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1, `/usr/lib/postgresql/16/bin`), not CI's 17.11:

- run as the `postgres` OS user in a `mktemp -d` directory under `/tmp`;
- listening only on a Unix socket (`listen_addresses = ''`), port 5433, with `track_commit_timestamp = on`. `log_statement` was not set.

The superuser's and the role's passwords and both markers were generated with `secrets` into files readable only by their owner. The superuser's password went in through `--pwfile`, which was removed after `initdb`. The role, its database and the comment came from one SQL file, removed after use. `pg_hba` allowed `peer` for `postgres` and `scram-sha-256` for everyone else. The proof read a passfile from the same directory, and every proof command ran under `env -i PATH HOME LANG=C.UTF-8` with only the `PROOF_DB_*` names and `DJANGO_SETTINGS_MODULE`.

| Run | Result |
|---|---|
| Wrong marker, `dbshell`, migrations | `migrate` with the other marker exited 1 with the refusal; `dbshell` exited 1 with its refusal; `migrate` applied the seventeen migrations, `0003` last; `makemigrations --check --dry-run` printed `No changes detected` |
| Run 1 (before the delivery read the outbox's heads in batches) | PASS, 7 min 21 s. Reference: 56/56 cases; twelve races at 200 iterations with 199 to 200 overlaps, 5.0 to 10.6 s; ten controls failed as intended; nine planted controls flagged; 671 submissions, 2,697 revocation rows, zero design violations. Adapter: 81/81; fifteen races at 200 iterations with 196 to 200 overlaps, 9.4 to 14.7 s; eleven planted controls flagged; 767 submissions, 10,341 witnesses, zero design violations. Delivery: 6,963 events in 125.7 s; 7/7 checks |
| Run 2 (the pushed code) | PASS, 6 min 52 s. Reference: 56/56; overlaps 198 to 200, 5.4 to 10.1 s; ten controls and nine planted as intended; 667 submissions, zero design violations. Adapter: 81/81; overlaps 199 to 200, 11.2 to 15.2 s; eleven planted flagged; 720 submissions, zero design violations. Delivery: 6,916 events in 78.8 s; 7/7 checks |
| Second run on run 2's database | exit 1, `refusing a used database: …`, the row counts unchanged |
| D5 writers without the account lock (a scratch reversal on a new database, not pushed) | `pause_high.revocation_holds` and `withdraw_low.revocation_holds` failed (`refusal_missing`, `wait_not_observed`); both `send_holds` cases still passed (the writer's later account update waits behind the send), and the oracle found no violation, because in those shapes the send committed first. The forced cases are what catch a D5 writer that skips the account lock |

No marker or password appeared in any run's output, the results JSON or the refused commands' output; I counted with `grep -c -F -f` against the files and never printed the values (0 each). After each use the cluster was stopped (`pg_ctl stop -m fast`) and its directory removed. At the end, no postgres process, cluster directory or `.work/` remained.

**Fix reversals (offline, in a scratch worktree of the code head, each undone after its run).** Each of 21 reversals made its tests fail:

- the used-database refusal not called, and the check ignoring app accounts;
- the proof app not installed (so Django's `dbshell` returns);
- O9's session-account check, and O9's membership check;
- O5 back to "committed before the expiry", and O5 ignoring the writers a send waited on;
- O10 removed; O0 removed;
- R3: the race dropping `case_id` at the per-iteration call site;
- R4: the empty-signal guard removed, and each reader's sign-in exclusion removed;
- the seeded delay removed;
- the CX2 case dropped from the plan;
- the runtime settings importing `glow_chat`;
- a two-hour token, and a token for a suspended account;
- the fixture provider creating a second channel on a retry;
- an edit to `0002`;
- a switch attribute on the adapter.

With no reversal applied, the same copy passed: proof `Ran 142 tests`, API `Ran 277 tests`.

### Checks

| Check | Command | Result |
|---|---|---|
| 1 | `git diff --check 2f982ae… 3b92122…` | clean |
| 1 | `git diff --name-status 2f982ae… 3b92122…` | 49 paths, +5,945, −179. `.github/workflows/foundation.yml` (the `database` job only). `docs/architecture/data-model.md`, `interactions-fixtures.md`. `proofs/postgres-ordering/`: `README.md`, `pyproject.toml`; in `glow_ordering_proof/`, modified `__main__.py`, `cases.py`, `controls.py`, `dbreads.py`, `interface.py`, `marker.py`, `observe.py`, `oracle.py`, `results.py`, `settings.py`, `stress.py`, and new `adapter.py`, `apps.py`, `delivery_phase.py`, `evidence.py`, `planted.py`, `management/__init__.py`, `management/commands/__init__.py`, `management/commands/dbshell.py`; in `tests/`, modified `command_harness.py`, `test_budget.py`, `test_case_plan.py`, `test_control_signals.py`, `test_marker_commands.py`, `test_oracle_rules.py`, `test_settings_refusals.py`, `test_stress_overlap.py`, and new `test_oracle_p06_2.py`, `test_p06_2_suite.py`. `services/api/`: `README.md`, `pyproject.toml`, `glow_persistence/models.py`, `tests/test_model_definitions.py`; new `glow_chat/__init__.py`, `contact.py`, `delivery.py`, `events.py`, `glow_domain/chat.py`, `chat_provider.py`, `chat_provider_fixtures.py`, `chat_tokens.py`, `glow_persistence/migrations/0003_chat_identity_read_cursor.py`, `tests/test_chat_domain.py`, `tests/test_chat_sealed_runtime.py`. No dependency file, no runtime module (`glow_api/settings.py`, `urls.py`, `configuration*.py`, `runtime.py`), no other job, no `reference.py`. Every file mode `100644`, no symlink |
| 2 | the trusted policy from `main` (`3afffb3…`, `scripts/change_scope.py` sha256 `dec69a2696ec261a…`) written by `git show` to a scratch directory outside the tree, then `python3 -I <dir>/change_scope.py --base 2f982ae… --head 3b92122… --merge-base` from the repository root | `{"full": true, "reason": "behavior-or-empty", …}`, 49 paths: full scope. One merge base (`2f982ae`) |
| 3 | the existing `.venv`s (`python3.12 -m venv`), `pip install --require-hashes -r requirements-dev.lock` in each with the proxy and CA variables by reference; `pip check` | installed; `No broken requirements found.` (both) |
| 4 | proof: `env -i PATH HOME LANG=C.UTF-8 .venv/bin/python -m unittest discover -s tests -t .` | `Ran 98 tests` at the start (C2's count), `Ran 142 tests`, `OK` at the head |
| 4 | API: `env -i PATH HOME LANG=C.UTF-8 GLOW_ENV=test .venv/bin/python manage.py test tests` | `Ran 253 tests` at the start, `Ran 277 tests`, `OK` at the head; `manage.py check`: no issues |
| 4 | Ruff (`ruff check .`; `ruff format --check .`) | proof `All checks passed!`, `42 files already formatted`; API `All checks passed!`, `68 files already formatted` |
| 4 | mypy | proof `Success: no issues found in 42 source files`; API `Success: no issues found in 37 source files` |
| 4 | the Django pin test (`env -i … .venv/bin/python -m unittest tests.test_django_pin`, the proof) | `Ran 4 tests`, `OK` |
| 4 | the toolchain pin test (`cd services/api && env -i … python3.12 -m unittest tests.test_toolchain_pins`) | `Ran 3 tests`, `OK` |
| 4 | the API static check (`env -i … GLOW_ENV=test .venv/bin/python -m glow_persistence.static_check`), and `makemigrations --check --dry-run` | `Static definitions agree: 34 app models; migrations=0001_event_infrastructure,0002_app_domain,0003_chat_identity_read_cursor`; `test_makemigrations_check_passes_without_a_database` runs `makemigrations --check --dry-run` under the no-database guard and passes (in CI too); the proof's job runs it against the migrated database: `No changes detected` |
| 4 | the sealed runtime test (`env -i … GLOW_ENV=test .venv/bin/python manage.py test tests.test_chat_sealed_runtime`) | `Ran 4 tests`, `OK` |
| 5 | local runs | above, iteration, not evidence |
| 6 | the Foundation run on the code head | run 37372546600 above: the database job passed with both subjects; the gate failed because three jobs never got a runner |
| 7 | secret scan over the diff's added lines (`git diff 2f982ae… 3b92122…`, 5,187 non-empty): password, secret, token, API key, private-key headers and known key prefixes, connection strings, email addresses, hexadecimal runs of 32 or more | no secret, password, marker value, key or email address. The only runs of 32 or more are the two pinned SHA-256 digests of `0001` and `0002` in `test_model_definitions.py`; the one connection string is the sealed test's synthetic `postgres://synthetic.invalid/not-a-real-database`. The other matches are names (`token_hex`, `revoke_user_tokens`, `tokens_revoked_before`, and the forbidden names the sealed test pins: `PGPASSWORD`, `HD_API_KEY`, `GEO_API_KEY`, `HDE_API_TOKEN`, `GLOW_HDE_API_TOKEN`), the sealed test's value `synthetic-connection-value-not-a-secret`, the fixture test's provider text `provider says secret detail`, and comments |

### Deviations, findings and limits

- **No run of record (infrastructure, not code).** Run 37372546600's gate failed because Change scope, API mobile smoke and Stream proof checks never got a runner; their code never ran on this head. Every application job that ran passed. The database job, which carries this stage's evidence, met the brief's Stage A acceptance criterion 4 in that run. A gate that prints `Application checks passed` needs either a re-run of this run's failed jobs or the pull-request run after integration. GitHub's "Re-run failed jobs" also re-runs the jobs that depend on those it re-runs, so a re-run of `scope` would bring the database job with it, as attempt 2. I did neither: the prompt forbids re-runs and dispatches, and a code push made only to trigger CI is not a change. A records push after the code run finished is allowed, so I pushed this record. The branch's concurrency group cancels in progress: if a re-run starts while this record's push run is still running, one of the two will be cancelled, so the re-run is best started after the records run has finished.
- **I did not run the API mobile smoke or the Stream proof checks locally.** This session's permission policy refused the attempt to install and run the Stream proof's checks, and I did not pursue it. Neither job's paths changed (`proofs/stream-chat/`, `apps/mobile/`, `scripts/smoke*.mjs`), and the smoke starts the runtime that the sealed test shows loads no `glow_chat` or `glow_persistence` module.
- **The reference's plan gains one case and nine planted controls.** P06.DB's 55 forced cases and ten controls are unchanged (`reference.py` is not in the diff; `controls.py` changes only to pass the reference's evidence reader). The CX2 boundary case (item 4) runs on both subjects, so the reference runs 56. The new rules O0 and O9 and the narrowed O5 judge the reference's rows too, and the ten controls still fail by their declared signals.
- **The seeded delay changes the session races' commit orders on both subjects.** In `race.sign_out_sender` and `race.expire_sender` the send now commits first in about a quarter of the iterations (C2: 0 and 1). This is carried item 2's purpose: the stress run now shows both orders there. The forced cases still cover each order.
- **The adapter's submission rows do not store their session.** The oracle takes the session, the transaction's start and the run tag of each adapter submission from the harness's call row (`proof_adapter_call`, joined by submission ID). The start is the clock the adapter read inside its transaction. The submission and its commit come from the app's rows; O3, O5, O7 and O9 rely on the harness's record of which session was used. A submission with no call row fails closed: the oracle flags it (O5, `the send's session is unknown`).
- **The oracle alone does not catch a D5 writer that skips the account lock** in the held shapes (local reversal above): the send commits first, which is a legal order. The forced `revocation_holds` cases catch it. In a stress interleaving where the send read the profile or consent before the writer committed and committed after it, O10 would flag it.
- **O5's lock sets are over-approximated.** A writer counts as one the send waited on if it locks any row the send locks (the accounts, the match, the session) and ended inside the send's transaction at or after the expiry. This can only add O5 violations, never hide one.
- **The delivery phase's limits.** One in-process deliverer, so no run had two deliverers competing for a lease (`data-model.md`: one deliverer at a time is assumed until P11). A failed attempt's Glow code is returned to the caller and not stored: no column holds the last error code in Stage A, and no provider text is stored, logged or shown. An accepted submission keeps its spooled text: the model defers the spool's removal to an approved retention policy, which Stage A does not set. Nothing in Stage A lifts a restriction (P07). A pause, a resume, a restriction and a consent change make no provider call: the channel stays open at the provider, and only Glow's send path refuses. Per-user token revocation runs at every session-epoch bump (today suspension and deletion); a single-device sign-out bumps no epoch, so that device's token lives until it expires (one hour), the residual `data-model.md` records beside DB09.
- **Local iteration ran on PostgreSQL 16.14,** not 17.11 (D4 condition 3), and no job runs the delivery phase against a second deliverer or a real provider.
- **The races ran slower than in C2's run** on the reference (4.4 to 7.6 s against 4.2 to 7.1 s), and the adapter's are slower still (8.4 to 11.5 s). The 30-second cap was not approached, and the suite step took 5 min 20 s of the job's 20-minute timeout.
- **Findings in the prompt's "fix here only if" classes:** none found.

### What the exact-head review must know

- The code to review is `3b9212236127638f9cd913927b3d382f1dca8202` (tree `f3b46e4728ab5356c53399750d453c33a08f961b`). Its push run is 37372546600: the database job's log is job 111978034228 and the API checks' log is job 111978034140. The run's gate failed only because three jobs never got a runner (above). The later commit changes only this record.
- **The evidence split.** The reference design's evidence is P06.DB's proof-log rows, read as before (`ReferenceEvidence`). The adapter writes no proof-log row: its evidence is its `MessageSubmission`s with their same-transaction `message_submitted` events (O1 compares the two rows' `xmin`), its outbox events (schema `glow-chat-1`) and its `ConsentDecision`s. Each subject's oracle reads only its own bindings: provider `proof` for the reference, `fixture` for the adapter. The harness's call rows supply only context (above).
- **D5's extra writers** (`_set_profile`, `_decide_consent` in `glow_chat/contact.py`) lock the account row first, then bump the profile's version or append a consent decision. The send reads both under its account locks. The forced races both ways are the D5 cases' `send_holds` and `revocation_holds`; the stress races are `pause_high`, `restrict_low` and `withdraw_high`.
- **No fault switch in the app** (D3 2.1): `test_the_chat_adapter_loads_without_a_connection_and_has_no_switch`; the ten reference controls inject their faults only into `reference.py`'s design object.
- **The workflow diff** touches only the `database` job: one step before the migrations (`dbshell`), the run step's name, and one step after the run (the used database). No marker or password moves to `$GITHUB_ENV` or `$GITHUB_OUTPUT`; the new steps read the marker from the job's directory exactly as C2's do.
- **The delivery phase runs after both subjects, on the same database,** and drains every deliverable chat event (the five kinds in `glow_chat/events.py`'s `DELIVERED`) the suite left, so its counts are the whole run's.

### Manager verification of Stage A (App Manager 6, 5 October 2026)

- **Branch and integration.** `claude/dazzling-lovelace-f2mtts`, code head `3b92122`, final head `1a7fd9a` (this record only). Integrated into the manager branch with the merge commit `e8eb5d3`, because the manager branch had moved by records commits since `2f982ae`. The trusted classifier on `3afffb3..e8eb5d3` (full SHAs, policy from `main`, `python3 -I`) reports `full: true`.
- **Owned paths: confirmed.** The 50 changed paths are all within the prompt's section 5. `glow_api/` and every dependency file are unchanged; `reference.py`, `0001_event_infrastructure.py` and `0002_app_domain.py` are unchanged. The two `pyproject.toml` changes are mypy configuration only: `glow_chat` joins the API's checked files, `glow_persistence` is skipped for imports (its untyped model declarations), and the proof ignores missing imports of `glow_chat` and `glow_domain`.
- **The workflow diff: read whole.** It touches only the `database` job: a `dbshell` refusal step before the migrations, the run step's name, and a used-database refusal step after the run. Each new step reads the marker from the job's protected directory, as C2's steps do, and none writes to `$GITHUB_ENV` or `$GITHUB_OUTPUT`. No other job and not the gate.
- **The adapter (`glow_chat/contact.py`): read whole.** It follows P06.DB D5 as written: every writer in one `transaction.atomic()`, accounts locked lower then higher by primary key, then the match and the session; every check in code on the locked rows, the time from `clock_timestamp()` after the locks; authorize, then deduplicate; a missing locked row is a refusal; deletion as the lifecycle transition with its job and tombstone. The D5 writers lock the account row before the profile or the consent decision. Before the locks the send reads only a match's pair and a session's account, which never change. No branch or flag changes a lock, a check or a write; the probe only signals.
- **Delivery (`glow_chat/delivery.py`): read whole.** One provider call per event, outside any transaction, with the identifiers committed with the event; first in, first out by `(available_at, created_at, id)`, and a retry stays at the head. A message whose channel's members were removed is dead-lettered, never delivered. A message authorized before a revocation committed is delivered first and its channel's members removed after it, which is D6's rule (history kept, contact ended).
- **The run: confirmed from GitHub.** Run 37372546600 on `3b92122`: API checks, Mobile checks, API artifact checks and Database proof checks concluded `success`, the database job with every step; Change scope, API mobile smoke and Stream proof checks concluded `cancelled` with no runner assigned and no step run; the gate failed. The manager branch's own runs at the same hour (37366161793 and 37366154754 on `2cb2713`) ended the same way, a job waiting with no runner for 15 minutes. It is a runner outage, not the change.
- **The run of record stays with the Stage A session** (AM6-01). Its candidates are PR29's runs on `8bbad57`, which hold the code at `3b92122` unchanged (PR run 37383940454, push run 37383936513), or a re-run of 37372546600. The session reports which it takes, and its figures, through Nathan.
- **For the exact-head review, besides the session's list above:**
  1. the pre-lock reads in `send` and `unmatch` (a match's pair, a session's account): confirm they are immutable and that nothing a check uses is read before the locks;
  2. the delivery order for a message authorized before a revocation: delivered, then the members removed;
  3. the `dbshell` refusal relies on Django resolving a command to the installed proof app before `django.core`; the CI step shows it refuses;
  4. the session's own limit: the oracle alone does not catch a D5 writer that skips the account lock; the forced cases do;
  5. `glow_persistence` is skipped by the API's mypy (`follow_imports = "skip"`), so the adapter's use of the models is not type-checked.

### Stage A run of record

Written by the Stage A session at App Manager 6's direction (5 October 2026), after both runs on the integrated head `8bbad57741708e4767406d54a5592d38d6f7880d` had finished. I read both runs and changed, re-ran or dispatched nothing.

**The run of record is PR29's pull-request run 37383940454** (run 470, `https://github.com/amthorn78/glow-dating-app/actions/runs/37383940454`). Its gate printed `Application checks passed`, which is the condition the direction sets. The manager branch's push run 37383936513 on the same head also concluded `success` with all eight jobs `success`, and its gate printed `Application checks passed` too. I read only its job list and its gate line, not its database job's log.

**What the run tested.** The run checked out GitHub's merge ref `refs/remotes/pull/29/merge` at `0d774c9325a0a332d6f1f1812ce59e7f240f8ffa` (`Merge 8bbad57… into 3afffb30205563932ebd05d5d41cca6d569663a3`).
- `main` (`3afffb3`) is an ancestor of `8bbad57`.
- `git diff --quiet 0d774c9 8bbad57` succeeds: the tested tree is `8bbad57`'s.
- `git diff --quiet 3b92122 8bbad57 -- services proofs .github` succeeds.

So the run tested Stage A's code exactly as it stood at `3b92122`.

| Job | Conclusion |
|---|---|
| Change scope | success (job 112012480811, 22:40:20 to 22:40:26). `COMPARE_BASE` `3afffb3…`, `COMPARE_HEAD` `8bbad57…`, `IS_PULL_REQUEST` `true`; the trusted policy printed `{"full": true, "reason": "behavior-or-empty", …}` with 65 paths, 47 of them under `services/`, `proofs/` and `.github/` |
| API checks | success (job 112012530069, 22:40:28 to 22:40:55) |
| Mobile checks | success (job 112012530003, 22:40:28 to 22:45:31) |
| API mobile smoke | success (job 112012529981, 22:40:29 to 22:41:16) |
| API artifact checks | success (job 112012529965, 22:40:29 to 22:40:52) |
| Stream proof checks | success (job 112012529857, 22:40:28 to 22:41:41) |
| Database proof checks | success (job 112012530140, 22:40:28 to 22:44:18; the suite step 22:40:57 to 22:44:13, 3 min 16 s) |
| Foundation gate | success (job 112014267191, 22:45:34 to 22:45:37). Its `RESULTS` gave `scope` `success` with `full` `"true"` and the six application jobs `success`. Its log line: **`Application checks passed`** |

The run-level conclusion is `success` (created 22:40:17, last updated 22:45:38 UTC). The jobs got runners within seconds.

#### From the database job's log (1,302 lines, read whole)

- **The offline checks.** `pip install --require-hashes` and `pip check` (`No broken requirements found.`); the offline tests under `env -i`: `Ran 142 tests`, `OK`; Ruff `All checks passed!`, `42 files already formatted`; mypy `Success: no issues found in 42 source files`.
- **The credentials and the role.** The credential step printed one line (`credentials generated into a directory readable only by this job's user`), the role step one line (`role glow_proof (NOSUPERUSER) and database glow_proof created, with the run's marker as its comment`).
- **The image and the server.**
  - `Digest: sha256:d74eeac9a635390a49bc21bd49fccd973de707e2a53a76ac49b552b8712ec46f`, the pinned digest.
  - Container `glow-proof-db-37383940454-1`; `127.0.0.1:5432 - accepting connections` inside it.
  - `SELECT version()`: `PostgreSQL 17.11 (Debian 17.11-1.pgdg13+2) on x86_64-pc-linux-gnu, compiled by gcc (Debian 14.2.0-19) 14.2.0, 64-bit`.
  - `track_commit_timestamp` `on`; `default_transaction_isolation` `read committed`, and `read committed` inside a writer's transaction; `deadlock_timeout` `1s`; `current_user` `glow_proof`, `superuser` `false`, `current_database` `glow_proof`. Each subject's report prints the same facts.
- **The wrong-marker step.**
  - Relations per schema before and after the `migrate` with the other well-formed marker: `information_schema` 69, `pg_catalog` 266, `pg_toast` 80, `public` 0, both times.
  - `relations outside information_schema and the pg_ schemas: 0 before, 0 after`; `to_regclass('public.django_migrations') IS NULL after: t`.
  - `wrong-marker migrate exit status: 1`, with the refusal `glow_ordering_proof.marker.RefusedDatabase: refusing this database: its comment is not the run's marker (PROOF_DB_MARKER): the database's comment is different. …`.
- **The `dbshell` step.** `dbshell exit status: 1`; `refusal: glow_ordering_proof.marker.RefusedDatabase: refusing dbshell under the proof's settings (PROOF_DB_MARKER): it starts psql outside Django, where the run's marker is never checked; no connection was opened and no client …` (cut at the log's width).
- **The migrations.** `migrate` applied all seventeen from zero, `glow_persistence.0003_chat_identity_read_cursor... OK` last. The ledger shows `0001_event_infrastructure` 22:40:55.850037, `0002_app_domain` 22:40:57.077418 and `0003_chat_identity_read_cursor` 22:40:57.108284. `makemigrations --check --dry-run`: `No changes detected`.
- **The marker on every connection.** `database marker verified on a new connection` appears once each for `migrate` (backend pid 129), `makemigrations` (130) and `facts` (131), then five times for `run`: the main thread (132) and `proof-writer-0` to `proof-writer-3` (133, 134, 136, 135). All five come before `[reference] cases: 56/56 passed`, and none comes after.

**The reference design** (`== VERDICT: PASS (reference) ==`; about 54 s, 22:40:57.9 to 22:41:51.9):

- **Cases:** `cases: 56/56 passed`. The 25 held cases are the twenty `send_holds` and `revocation_holds` cases, `racing_duplicates`, `session_expires_during_wait` and the three pairwise opposing-writer cases.
  - Each shows `pid 134 wait_event_type=Lock wait_event=transactionid pg_locks not granted: transactionid/ShareLock pg_blocking_pids=[133] (holder pid 133)`, after 1 poll (9 cases) or 2 (16).
  - In each `send_holds` case the commit timestamps put the send before the revocation.
  - `named.session_expires_after_check` passed: `short-lived sign-in: applied; released after the database clock passed the session's expiry; the send whose checks ran before the expiry: authorized; committed …`.
- **The ten negative controls,** each `failed as intended` by its declared signal:

| Control | Signal in the run of record |
|---|---|
| `no_locks.forced` (`unmatch_by_high.send_holds`) | not observed waiting on the holder; the send committed 22:41:43.518821 after the revocation at 22:41:43.513096; oracle 2 (O2, O6) |
| `no_locks.stress` (`race.block_by_high`) | first failing iteration 1: the block (v2) committed 22:41:43.681331, the send at v1 22:41:43.681593; O2, O6 |
| `no_version_check` (`named.stale_contact_version`) | the sends at versions ahead and behind were authorized; oracle 0 |
| `no_session_lock` (`sign_out_sender.send_holds`) | not observed waiting; the send committed 22:41:43.984808 after the sign-out at 22:41:43.980274; oracle 1 (O3) |
| `transaction_start_time` (`named.session_expires_during_wait`) | the send whose session expired while it waited was authorized (expected `session_expired`); oracle 1 (O5) |
| `dedup_before_authorize` (`named.retry_after_revocation`) | the retry after the revocation was `replayed` with the old receipt |
| `inverted_lock_order` (`named.opposing_first_lock_block_high_vs_send`) | `deadlock:DeadlockDetected` for the send |
| `no_account_lock.forced` (`suspend_high.send_holds`) | not observed waiting; the send committed 22:41:48.666976 after the suspension at 22:41:48.663058; oracle 1 (O4) |
| `no_account_lock.stress` (`race.suspend_high`) | first failing iteration 1: the suspension committed 22:41:48.819998, the send 22:41:48.823672; O4 |
| `filter_state_in_lock` (`unmatch_by_high.revocation_holds`) | the send that arrived while the unmatch held was authorized and committed; oracle 2 (O2, O6) |

- **The planted oracle controls,** each `flagged as intended`: `oracle.misattributed_actor` O9 (1 violation), `oracle.non_member_actor` O9 (2), `oracle.send_after_contact_revocation` O2 (2: O2, O6), `oracle.send_after_session_end` O3 (1), `oracle.send_after_account_revocation` O4 (1), `oracle.send_after_expiry` O5 (1), `oracle.wrong_contact_version` O6 (1), `oracle.witness_in_another_transaction` O1 (1), `oracle.unwitnessed_revocation` O0 (1).
- **The oracle over every row:** 748 submissions and 2,697 revocation rows examined; `design:forced` 33, `design:stress` 696, the controls 1 or 2 each.
  - **Violations in the design's rows: 0.**
  - Violations under control tags only: `no_locks.forced` 2, `no_locks.stress` 2, `filter_state_in_lock` 2, `no_session_lock` 1, `no_account_lock.forced` 1, `no_account_lock.stress` 1, `transaction_start_time` 1, and each planted control's as above.

**The app's adapter** (`== VERDICT: PASS (adapter) ==`; about 103 s, 22:41:51.9 to 22:43:34.4):

- **Cases:** `cases: 81/81 passed`. The 37 held cases are the 25 above and the twelve D5 `send_holds` and `revocation_holds` cases.
  - Each shows `pid 134 … pg_blocking_pids=[133] (holder pid 133)`, after 1 poll (15 cases) or 2 (22).
  - Each D5 `revocation_holds` case refused the waiting send: `profile_unavailable` for a pause or a restriction, `consent_not_current` for a withdrawal.
  - Each D5 `send_holds` case committed the send before the writer.
  - `named.session_expires_after_check` and `named.d5_restored` passed.
- **No reference controls on the adapter** (it has no fault switches, D3 2.1).
- **The planted oracle controls,** each `flagged as intended`: the nine above with the same rules and counts, plus `oracle.send_while_paused` O10 (1) and `oracle.send_after_consent_withdrawn` O10 (1).
- **The oracle over every row:** 831 submissions and 10,341 revocation witnesses examined; `design:forced` 47, `design:stress` 774, each planted control 1; **violations in the design's rows: 0**. Violations appear under the planted controls' tags only.

**The stress runs** (seed 20260929; budget 200 iterations or 30 s per race; floors 50 iterations and 10 overlaps). Every race on both subjects ran 200 iterations with 0 violations and 0 harness failures, and met its floors. Each pair gives push run 37372546600 → run of record 37383940454; the commit-order column gives (revocation first, send first):

| Race | Reference overlaps | Reference seconds | Reference commit order | Adapter overlaps | Adapter seconds | Adapter commit order |
|---|---|---|---|---|---|---|
| `race.block_by_low` | 200 → 200 | 5.5 → 3.4 | (165, 35) → (156, 44) | 200 → 200 | 9.2 → 5.4 | (166, 34) → (159, 41) |
| `race.block_by_high` | 200 → 200 | 5.4 → 3.3 | (161, 39) → (151, 49) | 200 → 200 | 9.2 → 5.4 | (162, 38) → (153, 47) |
| `race.unmatch_by_low` | 200 → 200 | 5.1 → 3.2 | (145, 55) → (144, 56) | 200 → 199 | 8.8 → 5.2 | (147, 53) → (145, 55) |
| `race.unmatch_by_high` | 200 → 199 | 5.0 → 3.1 | (151, 49) → (149, 51) | 200 → 199 | 8.8 → 5.2 | (151, 49) → (147, 53) |
| `race.suspend_low` | 199 → 181 | 4.5 → 2.9 | (165, 35) → (162, 38) | 200 → 181 | 8.4 → 4.9 | (168, 32) → (162, 38) |
| `race.suspend_high` | 199 → 182 | 4.4 → 2.7 | (187, 13) → (177, 23) | 200 → 183 | 8.5 → 4.9 | (185, 15) → (179, 21) |
| `race.delete_low` | 200 → 189 | 4.7 → 2.8 | (162, 38) → (151, 49) | 200 → 195 | 8.8 → 5.3 | (164, 36) → (157, 43) |
| `race.delete_high` | 200 → 190 | 4.7 → 2.8 | (183, 17) → (174, 26) | 200 → 196 | 8.6 → 5.3 | (183, 17) → (175, 25) |
| `race.sign_out_sender` | 199 → 155 | 4.7 → 2.8 | (146, 54) → (121, 79) | 199 → 167 | 8.7 → 5.1 | (146, 54) → (127, 73) |
| `race.expire_sender` | 199 → 164 | 4.7 → 2.8 | (145, 55) → (120, 80) | 199 → 173 | 8.9 → 5.0 | (148, 52) → (121, 79) |
| `race.racing_duplicates` | 200 → 200 | 6.5 → 3.8 | `send_a` first (128, 72) → (119, 81) | 200 → 200 | 11.5 → 6.8 | (128, 72) → (130, 70) |
| `race.opposing_writers` | 200 → 200 | 7.6 → 4.4 | (199, 1) → (199, 1) | 200 → 200 | 11.5 → 6.7 | (199, 1) → (199, 1) |
| `race.pause_high` | | | | 200 → 196 | 9.3 → 5.5 | (178, 22) → (169, 31) |
| `race.restrict_low` | | | | 200 → 195 | 9.2 → 5.7 | (168, 32) → (165, 35) |
| `race.withdraw_high` | | | | 200 → 190 | 9.3 → 5.9 | (182, 18) → (168, 32) |

The run of record's outcomes:
- In every race the writer applied 200 times, and each send that committed first was authorized while each that committed after its revocation was refused: the outcome counts equal the commit-order counts.
- The refusal codes:
  - `match_not_active` for blocks and unmatches;
  - `account_not_active` for suspensions and deletions;
  - `session_not_valid` for the session races;
  - `profile_unavailable` for pause and restriction;
  - `consent_not_current` for withdrawal.
- `race.racing_duplicates`: one authorized and one replayed in every iteration (`send_a` authorized 119, replayed 81).
- `race.opposing_writers`: send authorized 1; refused `match_not_active` 192 and `account_not_active` 7 on the reference, 193 and 6 on the adapter (as in 37372546600); no deadlock.

**The delivery phase** (`== VERDICT: PASS ==`; 22:43:34.4 to 22:44:13.7):
- `drained 7027 events in 33.8 s; outcomes: access_revoked=delivered:1031, contact_revoked=delivered:1033, match_activated=delivered:3101, message_submitted=dead_letter:2, message_submitted=delivered:829, session_epoch_bumped=delivered:1031`.
- `dead letters (the planted controls' worlds only): message_submitted:channel_unavailable:1, message_submitted:member_unavailable:1`.
- The seven checks each `PASS`:
  - drain: `7027 events in 33.8 s; 0 chat events left; 0 stalled passes`;
  - end state of every design world: `3090 worlds, 6180 accounts (1030 deactivated), 821 messages; as the database says`;
  - identifiers and members only: `7025 provider calls`, the five operations, no name, image or custom field, and no invite, call, feed or activity;
  - delivery of each event kind; a retry after a fixture failure; a revocation after the authorization, before the delivery; and a dead letter after the last attempt, each with the same detail text as in 37372546600.
- 829 delivered and 2 dead-lettered messages are the adapter oracle's 831 submissions; 821 design messages are those less the 10 planted submissions.

**After the suite:**
- **The used-database step:** `rows (proof log, adapter calls, worlds, app accounts, outbox events) before: 10325 12891 5590 11182 19194; after: 10325 12891 5590 11182 19194`; `second run exit status: 1`; `refusal: refusing a used database: proof_writer_log already holds rows; proof_adapter_call already holds rows; proof_world already holds rows; glow_persistence_appaccount already holds rows. The proof runs once per new disposable database.`
- **The results JSON:** artifact `p06-db-proof-results`, ID 11375654737, 14,755 bytes. I did not download it.
- **Disposal:** `container removed: glow-proof-db-37383940454-1`, `credential and marker files removed`, `no proof container remains`.
- **No password, no marker, and no mask where either would be.**
  - The log's only `***` are on lines 38 and 164 (the `token` inputs of `actions/checkout` and `actions/setup-python`) and line 94 (checkout's git `AUTHORIZATION: basic ***` header), all before the credential step.
  - The only long hexadecimal runs are 40 characters (16: the merge ref 3 times, `3afffb3` and `8bbad57` once each, the action commits 10 times, the runner image's commit once) and 64 (7: the image digest 5 times, the container's ID once, the artifact's digest once). There is no standalone 32- or 48-character run.
  - The only `glow-ordering-proof:` in the log is the credential step's script template (`glow-ordering-proof:%s`).
  - The words "password", "passfile" and "marker" appear only in the workflow's script text, the offline tests' names, the steps' fixed messages and the refusal and verification lines, none with a value.

#### Compared with push run 37372546600 on `3b92122`

**The same in both runs.** Both ran the same code: `3b92122` under `services/`, `proofs/` and `.github/`.

- **The plan:**
  - seed 20260929; budget 200 iterations or 30 s per race; floors 50 and 10;
  - 56 reference and 81 adapter cases, 12 and 15 races;
  - the ten reference controls, and nine and eleven planted controls.
- **The outcome:**
  - every case passed on both subjects, and every held case's waiter was blocked by its holder (pid 134 by pid 133);
  - every race ran its 200 iterations and met its floors, with 0 violations and 0 harness failures;
  - every control failed by its declared signal, and every planted control was flagged with the same violation counts;
  - 0 violations in the design's rows on both subjects;
  - the delivery phase's seven checks passed;
  - the wrong-marker, `dbshell` and used-database steps refused, and the container was removed;
  - no password, marker or mask appeared where either would be.
- **Counts the plan fixes, equal in both runs:**
  - revocation rows 2,697 (reference) and witnesses 10,341 (adapter);
  - `design:forced` 33 and 47;
  - the delivery's 3,101 activations, 1,033 contact revocations, 1,031 deactivations, 1,031 epoch bumps and 2 dead letters in planted worlds;
  - the end state's 3,090 worlds and 6,180 accounts (1,030 deactivated);
  - the used database's proof-log, adapter-call, world and account rows (10,325, 12,891, 5,590, 11,182);
  - `race.opposing_writers`' outcomes on each subject.

**Different, because the races decide them** (each run's own numbers):

| | Push run 37372546600 | Run of record 37383940454 |
|---|---|---|
| Runner region (database job) | eastus | centralus |
| Suite step | 5 min 20 s (reference about 83 s, adapter about 168 s, delivery about 70 s) | 3 min 16 s (about 54 s, 103 s, 39 s) |
| Reference races | 4.4 to 7.6 s; overlaps 199 to 200 | 2.7 to 4.4 s; overlaps 155 to 200 |
| Adapter races | 8.4 to 11.5 s; overlaps 199 to 200 | 4.9 to 6.8 s; overlaps 167 to 200 |
| Reference submissions (`design:stress`) | 643 (591) | 748 (696) |
| Adapter submissions (`design:stress`) | 710 (653) | 831 (774) |
| Session races, send first (reference; adapter) | sign-out 54, expiry 55; 54, 52 | 79, 80; 73, 79 |
| Held-case polls (reference; adapter) | 1, 2 or 3 polls: 9/14/2; 15/20/2 | 1 or 2 polls: 9/16; 15/22 |
| Delivery | 6,906 events in 59.1 s; 708 messages delivered; 700 design messages; 6,904 provider calls | 7,027 events in 33.8 s; 829 delivered; 821; 7,025 |
| Outbox rows after the run | 18,968 | 19,194 |

- The outbox rows differ by 226, which is the extra authorized sends: 105 on the reference (748 − 643) and 121 on the adapter (831 − 710). Each authorized send writes one `message_submitted` event (`reference.py:262`, and the adapter's send).
- The run of record's runner was faster and measured fewer overlaps, lowest in the session races (155 and 164 on the reference). Every count is far above the 10-overlap floor. The same pattern appeared between P06.DB-C1's run of record (174 to 200) and C2's (197 to 200).
- More iterations committed the send first in the run of record. The authorized-send counts and the submissions follow from that.

#### Limits and open points

- I read the run of record's database job log whole, its gate's and Change scope's logs, and every job's conclusion. I did not read the other jobs' logs in this run; their conclusions are `success`. For push run 37383936513 I read only the job list and the gate line.
- The run of record tested the merge ref `0d774c9`, whose tree equals `8bbad57`'s. The comparison above rests on `git diff --quiet 3b92122 8bbad57 -- services proofs .github`; outside those paths the two runs' trees differ only in Markdown.
- Nothing in this run changes the limits recorded in "Deviations, findings and limits" above, or the manager's points for the exact-head review.

## Exact-head review of Stage A (6 October 2026)

Relayed by Nathan to App Manager 6 on 6 October. The review session ran the [review prompt](../../ephemeral/2026-10-06-p06-2-stage-a-review-prompt.md), revision 1, from `ec87eacdb28613a6f8481c85755ffc7e9d7212aa` (Nathan's pick: Fable 5.1 at max, TypeSafe's reading), in `Glow App - No Stream`, offline.

- **Head reviewed:** `e8eb5d370fe41e27658e5fa30eb857f05f514be0` (`HEAD^2` `1a7fd9a`, code head `3b92122`), the whole of `git diff HEAD^1 HEAD`, with the records at `ec87eac` and the run of record's logs (database job 112012530140, 1,302 lines, and the gate's).
- **Verdict: approve.** No blocking finding and none in a correction class. One should-fix finding for the records and for later design (F1), and four nits (F2 to F5).
- **Start gate and classifications:** every check passed. The trusted policy from `main` (`python3 -I`, full SHAs, its SHA-256 equal to the copy at `HEAD`): the head against `main` `full: true` (65 paths); `HEAD^1` against `main` and `ec87eac` against the head `ordinary-docs-only`.
- **Environment (names only):** no HDE, `PG*`, `PROOF_DB_*` or `STREAM_*` name set; Python 3.12.14 from `$HOME/.local/bin`. No database started or connected, no provider called, no `migrate`, no proof `facts` or `run`.
- **Offline checks** (under `env -i`, hash-pinned installs, `pip check` clean): the proof's 142 tests, Ruff and mypy (42 files) and the Django pin test (4); the API's `manage.py check`, 277 tests, Ruff (68 files) and mypy (37 files), the static check (34 app models; migrations `0001`, `0002`, `0003`), the toolchain pin test (3) and the sealed test (4); `git diff --check` clean, every mode `100644`. Seven of the session's reversals, re-run in a scratch copy, each made its test fail.
- **Focus areas 1 to 10:** each confirmed; the review's figures from the database job's log match the records (reference 56/56 cases, 748 submissions; adapter 81/81, 831 submissions, 167 to 200 overlaps per race, 0 violations; delivery 7,027 events drained, seven checks passed). It agrees with the manager's five points; on point 1, the immutability of a match's pair and a session's account is a code invariant, not a schema rule, and the send re-checks only the pair (F2).

**Findings**

| ID | Severity | Finding | Disposition (App Manager 6) |
|---|---|---|---|
| F1 | should fix, records | The per-user token revocation's cut-off is the epoch bump's pre-commit clock: `delivery.py:240` takes `event.available_at`, which the bump's transaction read with `clock_timestamp()` after the account lock (`contact.py:604`, `_revoke_account`). A token endpoint that reads the account without that lock can grant a token at the old epoch between that reading and the commit; its issue time is after the cut-off, so the revocation leaves it valid for up to an hour. Clock skew between the app server and the database widens the window. | **Accepted.** No token endpoint exists yet (`grant_chat_token` signs nothing; P11 serves the endpoint and Stage B's adapter signs). Recorded now in the data model's token rules and beside DB09 in the P11 plan. The mechanism (the grant under the account row lock, or a cut-off at or after the bump's commit) is carried to Stage B (the brief, "Carried to Stage B and P11") and goes to the Dev Manager in DM-14. |
| F2 | nit | The send re-checks the locked match's pair but not the locked session's account against its pre-lock read; `unmatch` re-checks neither. No writer changes either key, so there is no gap today. | Carried to the next code change to `glow_chat/contact.py` (Stage B or P11): a one-line refusal for each. |
| F3 | nit; design input | A dead-lettered `contact_revoked`, `access_revoked` or `session_epoch_bumped` marks nothing and the binding stays `active`; at a live provider, five failed removals would leave both members reading a restricted match's channel with no reconciliation path. | Carried to Stage B: its prompt names the reconciliation path before the adapter runs live. P11 owns dead-letter reconciliation (the data model). |
| F4 | nit | The deadlock mapping by SQLSTATE (`contact.py:147`) has no offline test and no run exercised it; a wrong mapping would surface as `error`, which the suite fails. | Carried with F2: an offline test of the mapping. |
| F5 | nit | A self-block (actor equal to target) hits the `nonself_check` constraint and returns `error`, not a refusal. No caller does this. | Carried with F2 (a refusal before the write); P11's route also refuses a self-block. |

**Incident in the review session.** During its first reversal attempt the session's working directory was inside the repository's `services/api`, so two commands ran against its own working tree: one appended an import to `glow_api/settings.py`, one rewrote `chat_tokens.py` with its `HEAD` content. It restored both from `HEAD` at once and reports `git status` empty and nothing committed or pushed. Checked: the remote holds no new branch (`git ls-remote --heads`: `main`, the manager branch, `claude/dev-manager`, `claude/dazzling-lovelace-f2mtts`), and the manager branch's head is the manager's own `96efc28`.

**Manager verification (App Manager 6, 6 October 2026).** The report states the prompt's commit and the head as the prompt names them. F1 reproduced from the code: `_revoke_account` writes `session_epoch_bumped` with `available_at=now`, `now` read by `self._clock` after the account lock and before the commit, and `delivery.py:240` sets `cutoff = event.available_at`. F2's pre-lock reads (`contact.py:320-337`) and the pair-only re-check (`:350`), F3's `_nothing` dead-letter plans (`delivery.py:200-249`) and F4's mapping (`contact.py:147`) read as the review says. Nothing in the findings changes a recorded result.

**Next:** Codex's review of PR29, the Dev Manager's DM-14 (the governing sentences and these dispositions), the pre-merge checklist, then Stage A's merge. (Codex and DM-14 done the same day, below.)

## Codex's review of PR29 (6 October 2026)

App Manager 6 marked PR29 ready at about 01:22 UTC, at `da9fac6a13a815eb08e3c3cd9e71b9e1e626e19b`. Codex's summary comment shows both reviews completed on `da9fac6`: the security review at 01:29:06 UTC with no comment, the code review at 01:29:32 UTC with two inline comments, each marked P1. The labels CX4 and CX5 are the manager's (CX1 to CX3 were PR28's).

### The findings, as posted

> **CX4. P1, `services/api/glow_domain/chat_provider_fixtures.py:145-149`: "Provision provider users before creating their channel."** For a pair's first match, the only provider operation is `create_channel`, while this fixture silently creates both provider users as a side effect. Stream's server guidance says both users must already be present before starting a conversation and provisions them through `upsert_users` ([Stream backend documentation](https://getstream.io/chat/docs/python/backend/)); a real adapter implementing this five-operation port will therefore fail channel creation for new identities or hide extra, partially completed calls inside the claimed single call. Model idempotent user provisioning explicitly and deliver it before the channel event.

> **CX5. P1, `services/api/glow_chat/contact.py:204-208`: "Recheck current pair eligibility before activating a match."** When either profile is paused/restricted, consent has been withdrawn, or reciprocal likes are absent/stale, `activate_match` still creates an active `Match`, provider identities, and a channel-creation event because this transaction checks only account state and blocks. The F09 contract requires reciprocal likes and current two-person eligibility, and checking those in a caller before entering this transaction would leave a race with the account-locked pause/consent writers; recheck the interaction and eligibility inputs under these locks before creating the entitlement.

### Manager verification (App Manager 6, 6 October 2026)

- **CX4: confirmed.** The port (`glow_domain/chat_provider.py:77-93`) has five operations and none creates a user. The fixture's `create_channel` creates each unknown member with `self.users.setdefault(...)` (`chat_provider_fixtures.py:145`), so the delivery path never provisions a user and the fixture cannot show the gap. A Stream adapter on this port must provision users inside `create_channel`, which is the hidden extra call Codex names, or fail. Nothing reaches a live provider before Stage B.
- **CX5: confirmed.** `activate_match` (`contact.py:192-236`) locks both accounts, then refuses only a non-active account, an active block or an existing pair; it reads no like, profile or consent. The send refuses a paused or restricted profile and a withdrawn consent under the same locks (D5), so such a match cannot carry a message, but its channel is created. No runtime path calls the adapter (the sealed test), and the proof's fixture factory is its only caller; the records call it "match activation" without saying it is not F09's.
- **Against the correction classes** of the review prompt: neither lets a send commit after a revocation without the suite failing, touches a credential or a connection, makes DB06's or DB09's mark claim more, or sends a name, image, custom field or provider text. Both are design gaps for the live adapter and for P11's activation.

### Disposition

- **No correction pass before the merge**, as for PR28's CX1 and CX2: neither is blocking or in a correction class.
- **CX4** is carried to Stage B (the brief, "Carried to Stage B and P11", item 4): an idempotent user provisioning operation on the port, delivered before the channel's creation, and a fixture that refuses a channel for an unknown user.
- **CX5** is carried to Stage B and P11 (item 5): Stage B adds the profile and consent checks under the account locks and says the method is not F09's activation; P11's activation checks reciprocal likes and two-person eligibility under the same locks. The data model records the limit.
- **The threads:** each gets a reply with this disposition. The Dev Manager reads both with Stage B's prompt.

### Codex's second code review, of `9f6f6ab` (6 October 2026)

The push of `9f6f6ab`, the records of CX4, CX5 and DM-14, started a second Codex code review at 01:39 UTC. It completed at 01:43 UTC with one inline comment, marked P1. The security review did not run again (its last is of `da9fac6`).

> **CX6. P1, `services/api/glow_chat/delivery.py:202-204`: "Revoke channels after uncertain creation failures."** When `create_channel` succeeds at the provider but its response is lost on every retry, the activation event is dead-lettered and marks the binding `failed`, even though the channel and memberships still exist. A later block or unmatch then takes this branch and records the revocation as delivered without calling `remove_members`, leaving both users able to access the conversation; treat a failed binding as an uncertain external effect and still attempt idempotent removal or reconciliation.

- **Manager verification: confirmed.** A dead-lettered `match_activated` runs `failed_binding`, which sets a `pending` binding to `failed` (`delivery.py:144-145`, `:159`); a provider call whose response was lost may have created the channel. `contact_revoked` then returns a plan with no provider call for a `failed` binding (`:202-204`), and the event is marked delivered. At a live provider, both members would stay in a channel whose match Glow has blocked or unmatched. Sends into a `failed` binding are refused (`:173-175`), so no message reaches it. The fixture runs only in-process under the proof; nothing reaches a live provider before Stage B.
- **Against the correction classes:** it does not let a send commit after a revocation, touch a credential or a connection, change DB06's or DB09's mark, or send a name, image, custom field or provider text. It is a gap in revocation's delivery to a provider, the area of F3.
- **Disposition:** no correction pass before the merge; carried to Stage B with F3 (the brief, "Carried to Stage B and P11", item 2): a revocation of a `failed` binding still makes the idempotent removal (a channel the provider does not have counts as removed), and the conformance run shows it after a creation whose response is lost. The thread gets a reply with this disposition, and the Dev Manager reads it with Stage B's prompt.

## DM-14 (6 October 2026)

Dev Manager 2's [report](../../continuity/dev-manager/reviews/2026-10-06-dm-14-p06-2-stage-a-governing-read.md) (`e85bad6`, read covering `da9fac6`) approved the governing sentences (item 2 with replacement words, applied as written; item 1's *consider* clause taken as written), approved the dispositions of F1 to F5 with conditions for Stage B (the brief, items 1 to 3), and confirmed that Stage A may merge once item 2 is applied, Codex's findings are dispositioned, the final head's run passes and the checklist and branch-state report are done. Notion matched `da9fac6`. No item is Nathan's. The disposition is in the review log, "DM-14".

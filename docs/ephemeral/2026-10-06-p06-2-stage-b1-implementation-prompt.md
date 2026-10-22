# P06.2 Stage B1 prompt — the carried items, offline, on the fixture provider and a disposable PostgreSQL

- **Owner:** App Manager 6. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 6 October 2026.**
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 3: D1 (Stage B, B1), the owned paths, acceptance check 5, "Carried to Stage B and P11" items 1 to 5 with CX6, and "B1's design points" a to f. Revision 3 applies the Dev Manager's DM-15 as written.
  - Inputs: the P06.2 evidence record's "Exact-head review of Stage A" (F1 to F5), "Codex's review of PR29" and "Codex's second code review, of `9f6f6ab`" (CX4 to CX6); the DM-14 and DM-15 reports; the P06.1 evidence record's "Exact-head review of C5" (its nits 2 and 3).
- **Where the result goes:**
  - the session's code and tests, its section "Stage B1" in the evidence record `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`, and its updates to the data model and the migration plan;
  - the Foundation run on the session's last code commit becomes the run of record;
  - the manager adds its verification to that record, records the outcome in the brief's "Sessions", and updates the P11 plan's DB06 and DB09 entries.
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v6: Fable 5.1, extra high.** Effort score 3.08 (confidence 0.90); rung probabilities low 0.00, medium 0.00, high 0.03, extra high 0.86, max 0.11, ultracode 0.00. Model probabilities Fable 5.1 0.50, Opus 5.5 0.50 (confidence 0.00). Flags: model near tie. Sent 2026-10-06T02:28:37Z. Nathan picks the cell.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** DM-15 approved the split and B1's design points with conditions, which revision 3 and this prompt state as written. This prompt authorizes no credential, no provider call and no dependency, so it needs no read of its own (DM-15 item 1).
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and the session calls no provider.
- **It runs alone** (OD-29, the linear process). Its exact-head review follows.
- **Deletion condition:** prune after Stage B1's PR merges and the evidence record holds the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **implementation session for P06.2 Stage B1**, the offline half of Stage B of P06.2, the chat integration of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<START_SHA>`.

**What exists.** Stage A merged on 6 October (`02072f4`). The app has a chat contact port (`services/api/glow_domain/chat.py`) and its persistence adapter (`services/api/glow_chat/contact.py`), which carry P06.DB's transaction design: `READ COMMITTED`, row locks in one order (lower account, higher account, match, session), every check on the locked rows, time from `clock_timestamp()` after the locks, authorize then deduplicate. Outbox events go to a chat provider port with a fixture adapter only (`glow_chat/delivery.py`, `glow_domain/chat_provider.py`, `chat_provider_fixtures.py`). The token rule is the pure function `glow_domain/chat_tokens.py`'s `grant_chat_token`. Migration `0003` (chat identity, read cursor) is unapplied anywhere but disposable databases. P06.DB's race suite (`proofs/postgres-ordering/`) runs the reference design and the app's adapter in the Foundation job "Database proof checks". The API runtime imports none of it.

**What B1 does.** Stage A's reviews found eight things to change before the adapter meets Stream (F1 to F5, CX4 to CX6). You make all of them, offline, against the fixture provider and a disposable PostgreSQL, and you apply two old nits in the Stream harness, offline. B2 later adds `getstream` and the Stream adapter on the port you leave. **No app runtime gains a database, real authentication or a live provider**, and nothing calls Stream.

- Nathan started you manually and will relay your report to the manager (App Manager 6). You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- Your boundary is scope:
  - write only your owned paths (section 5);
  - push only your own session branch. Each push runs the Foundation workflow on your branch; read those runs if your tools can. On GitHub do nothing else: no pull request, no PR comments, no re-runs, no workflow dispatches. Change nothing in Notion.
- **Never:**
  - dump the environment, or print, echo or log the proof database's passwords or the run's marker, in any form;
  - connect to any database other than a disposable one that you or the job start for this proof (P06.DB brief, D4), or set a comment on any other database. Never connect to Stream, HDE, Railway or any other provider, and never run a harness command in `proofs/stream-chat/` that sends a request;
  - run `playwright install` or `eas`;
  - run Django's `migrate` anywhere but against a disposable proof database, from the proof's own settings;
  - add a dependency anywhere, or import `getstream`.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set** (DM-15 1.2): `compgen -e | grep -E '^STREAM_'` prints names only. If any is present, **stop and report to Nathan**: this session must start in `Glow App - No Stream`.
3. No `PG*` or `PROOF_DB_*` name should be set: `compgen -e | grep -E '^(PG|PROOF_DB_)'`. If any is present, report its name first in your report, never read or use its value, and run every proof command in a clean process environment that lacks it.
4. The pinned toolchain is in `$HOME/.local/bin`: Node 24.19.0, npm 11.9.0 and Python 3.12.14. Put `$HOME/.local/bin` first on PATH, then record `command -v python3.12` and its version. Create any virtual environment with `python3.12`.
5. Run the API's, the proof's and the harness's commands in a clean process environment, as `docs/operations/local-development.md` and each README show: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8` plus only the proof's own variables. Installs get the proxy and CA variables by reference, never printed.
6. **What a local database can use** (P06.DB brief, D4): record whether `docker info` succeeds (its exit status only), and `command -v initdb pg_ctl postgres pg_isready psql`.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git merge --ff-only <START_SHA>          # on your own session branch
git rev-parse HEAD                       # must print <START_SHA>
git diff --stat <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/ proofs/ .github/ docs/architecture/ docs/operations/migration-plan.md   # must print nothing
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md | grep -c '^## Stage B1'   # must print 0
```

- The fourth and fifth commands check the live manager branch. If code or this stage's section has already landed there, this prompt is stale: stop and report (the manager workflow, step 3, AM5-15).
- If any check fails, stop and report.

Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`, `services/api/README.md`, `proofs/postgres-ordering/README.md` and `proofs/stream-chat/README.md`;
- the P06.2 brief, `docs/planning/p06-2-chat-integration.md`, revision 3: D1 to D7, the owned paths, "Carried to Stage B and P11" and "B1's design points";
- the DM-14 and DM-15 reports, `docs/continuity/dev-manager/reviews/2026-10-06-dm-14-p06-2-stage-a-governing-read.md` and `2026-10-06-dm-15-p06-2-stage-b-split-read.md`;
- the P06.2 evidence record, `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`, whole: Stage A's section and its run of record, and the review and Codex sections;
- the P06.1 evidence record, `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md`, "Exact-head review of C5", whole;
- `docs/architecture/data-model.md`, "Chat contact and the outbox", and `docs/operations/migration-plan.md`;
- `services/api/glow_chat/`, `services/api/glow_domain/chat*.py`, `services/api/glow_persistence/models.py` and its migrations, and their tests;
- `proofs/postgres-ordering/` whole;
- in `proofs/stream-chat/`: `glow_stream_proof/cli.py`, `client/runner.cjs` and their tests;
- `.github/workflows/foundation.yml`, the `database` job and the gate.

## 3. The work

Each item names its source. Where DM-15 set a condition, it is quoted as the brief holds it; meet it as written.

**The provider port and delivery**

1. **Provisioning before the channel** (CX4; design point a, DM-15 3.1 to 3.5).
   - Each `ChatIdentity` that activation creates gets its own outbox event, whose delivery is one idempotent provisioning call with `user_id` only. `OPERATIONS` and `events.DELIVERED` gain the operation and the event. The fixture's `create_channel` refuses an unknown member, and provisioning a user it already holds returns `already=True`.
   - **3.1 A deterministic order key.** Events of one transaction are delivered in the order that transaction wrote them, with neither the app's clock nor a random value deciding. Recommended: a database-assigned, monotonically increasing column on `OutboxEvent` (an identity column), used in place of `created_at, id` after `available_at`. Another mechanism is acceptable if you show it is equally deterministic and record why. A test writes the channel event and the provisioning events in one transaction and shows the order over repeated runs, not resting on clock values.
   - **3.2** The identity gains a state meaning "not yet provisioned", and becomes provisioned only on the provider's receipt. A channel event that reaches the head while either member is not provisioned does not retry or wait: it dead-letters with `member_unavailable`, and its binding takes item 2's mark.
   - **3.3** A provisioning event dead-lettered after a call whose response may have been lost marks the identity with item 2's mark. A later `access_revoked` or `session_epoch_bumped` for that identity still makes its call; a user the provider does not have counts as deactivated, or as revoked.
   - **3.5** An identity that already exists from an earlier match gets no second provisioning event. A test covers a second match for an already-provisioned account.
2. **The reconciliation mark** (F3, CX6; design point b, DM-15 4.1 to 4.5).
   - A state or field meaning "needs reconciliation", with the Glow code that caused it (a code from `ERROR_CODES` or a named Glow reason, never provider text), on the binding and on the chat identity. A dead-lettered `contact_revoked`, `access_revoked` or `session_epoch_bumped` marks its row.
   - **The schema:** amend the unapplied `0003`, or add `0004`; choose and record why.
     - **4.1** The mark on `ChatBinding`, and any order column on `OutboxEvent`, are new operations (`AddField` or `AlterField`); `0001` and `0002` stay byte-identical, and their hash test stays as it is.
     - **4.2** Generate the migration with the pinned autodetector and review it as source; no `RunSQL` or `RunPython`.
     - **4.3** `test_migration_0003_is_additive_and_0001_0002_are_unchanged` (and a `0004` test, if you add one) asserts the exact operation list. `makemigrations --check --dry-run` passes, and the proof's run applies the result from zero.
     - **4.4** Record in `docs/operations/migration-plan.md`'s "Committed schema order" `0003`'s row (and `0004`'s), and the rule: an unapplied migration may be amended until it is first applied to a database that is not disposable; from P11's first such application it is frozen, and changes go into a new migration. Your report states that `0003` has been applied only to disposable databases, and how you established it.
   - **4.5** A message is never delivered into a marked binding. A revocation of a marked or `failed` binding still makes its removal (CX6), and a channel the provider does not have counts as removed: the delivery maps the fixture's `channel_unavailable` to "removed" for that plan only and records the binding `revoked`, keeping the mark's reason.
   - Name P11's reconciliation path in the data model; reconciliation itself stays with P11.
3. **The cut-off at whole seconds** (F1 point 3; design point d, DM-15 5.2). The delivery rounds the revocation's cut-off up to the next whole second, strictly, before it calls the port: a cut-off of exactly 10.000000 s is sent as 11. The stored `tokens_revoked_before` keeps the exact time. A test covers a cut-off with zero microseconds. The cut-off itself stays the bump's pre-commit time, read after the account lock (`event.available_at`).

**The persistence adapter**

4. **The grant's transaction** (F1 points 1, 2, 4 and 5; design point c, DM-15 5.1).
   - The adapter gains the grant: in one transaction, the account row `SELECT ... FOR SHARE`, then the session row `FOR SHARE`, in the send's order; `clock_timestamp()` read under those locks; every check of `grant_chat_token` run on the locked rows, with that time passed as `now`. It returns the rule's grant with its issue time. `grant_chat_token` stays the pure rule. It signs nothing; B2's adapter signs, and P11 serves the endpoint.
   - **5.1** "Identity active" means provisioned and not deactivated: a grant for an identity not yet provisioned is refused with `no_chat_identity`.
   - **Tests** (forced cases on the adapter's subject): a grant forced to wait on an epoch bump that holds the lock refuses after it; a grant that commits just before a bump has an issue time before the bump's cut-off; each with the app's clock deliberately skewed ahead, to show that the app's clock plays no part.
5. **Activation's checks** (CX5; design point e, DM-15 6.1 and 6.3).
   - `activate_match` makes the send's profile and consent checks on the rows read under its account locks: a paused or restricted profile, or a withdrawn onboarding consent, of either member refuses it.
   - **6.1** Forced cases both ways: a pause commits first, so activation refuses; activation commits first, so the pause follows and the send refuses afterwards. The same both ways for a consent withdrawal. Restriction shares the pause's writer (`_set_profile`) at `02072f4`; the pause case covers it only if you show the code path is shared, otherwise restriction gets its own case. Each forced wait is observed, as for the send.
   - **6.3** `activate_match`'s docstring says it is the proof's and the conformance run's way to make a match, not F09's activation. Reciprocal likes and two-person eligibility stay with P11's activation.
6. **The nits** (F2, F4, F5; DM-14 item 5), each with its test:
   - **F2:** the send refuses when the locked session's account differs from its pre-lock read; `unmatch` refuses when the locked match's pair or session's account differs from its pre-lock read;
   - **F4:** an offline test of the deadlock mapping by SQLSTATE (`contact.py`'s `_run`);
   - **F5:** a self-block (actor equal to target) is refused before the write, not left to the `nonself_check` constraint.

**The suite** (design point f, DM-15 6.2 and 6.3)

7. The new paths join the adapter's subject as forced cases (items 1, 2, 4 and 5).
   - **6.2** A new oracle rule says that no activation commits after a committed pause, restriction or withdrawal of either member that it would have read, with a planted control that fails in the same run. The same applies to any other new rule you add, for example provisioning before the channel if you state it as an oracle rule rather than an offline test.
   - **The delivery cases** (offline or in the database job) cover provisioning before the channel, a lost provisioning response, a lost creation response followed by a revocation (CX6), and each dead-lettered revocation marking its row (F3).
   - **6.3** `reference.py` is byte-identical to `02072f4`, and its 56 cases and ten controls are unchanged; your report shows the hash or an empty diff.
   - The job's timeout stays 20 minutes and both subjects keep their stress budgets. If a measured run shows the job no longer fits, report the numbers; do not raise the timeout or shrink the adapter's run.

**The harness, offline** (the C5 review's nits 2 and 3; DM-15 2.3)

8. In `proofs/stream-chat/`, with offline tests only and no command that sends a request:
   - **nit 2:** a test in which the re-read after a refused step meets a budget `GuardrailStop` (not one from `stop_at_once`) that must reach `main`, and a reversal that removes only the `isinstance(later, GuardrailStop)` clause of `_Applied.stop` (`glow_stream_proof/cli.py`);
   - **nit 3:** `finish()` chains only a signal's stop to what replaced it, so an apply failure keeps its own cause; with its test;
   - **the header names:** reconsider an allowlist of request-header names in `client/runner.cjs`, as the review advised. Either add it, with tests, or record why the existing refusal of request-rewriting headers suffices. Record the choice.
   - The harness's guard, budget, deny-lists and cleanup are otherwise unchanged.

**The documents**

9. `docs/architecture/data-model.md`, "Chat contact and the outbox": the provisioning event and order, the identity's and the binding's new states and the mark, the grant's transaction, the whole-second cut-off, activation's checks, and P11's reconciliation path; and `docs/operations/migration-plan.md` (item 2).

**Not in B1:** `getstream`, the Stream adapter, the signer and any live call (B2); any API route or served feature; the mobile app (Stage C); push (P06.3); allauth.

**Rules for every change:**

- **A test for each change.** Each code item gets a test that fails without it and passes with it. Say which test covers which item.
- **Reversals in a scratch copy, never the checkout** (DM-14 item 6). Make each fix reversal in a copy outside the repository, with absolute paths, and confirm afterwards that `git status` is clean.
- **Evidence comes from the database.** Every guarantee is judged by what PostgreSQL recorded, never by what the test code believes it did.
- **No weakened check.** Never loosen a case, the oracle, a control's signal or a floor to make a run pass. A flaky case is a finding (OD-21), not a retry.
- **No password or marker anywhere:** not in the diff, a log line, the evidence record or your report.
- **No dependency change** (DM-15 2.1): `services/api/requirements*.in`, `requirements*.lock`, `pyproject.toml`'s dependencies and `dependency-inventory.json` unchanged, and the same for the proof's and the harness's dependency files; no `getstream` import and no Stream adapter module.

**Findings outside this work:** report each with its class. Fix it here only if it could do one of these, and then with a test:

- let a send authorization commit after a revocation that invalidates it without the suite failing;
- let a password, the marker or a connection value reach a log, an artifact or a file outside the job's temporary directory;
- let the job, the proof or the adapter connect to anything but its own disposable database, or let the API runtime load the adapter or connect to any database;
- make DB06's or DB09's mark claim more than the run shows;
- let the provider receive a channel, member or user name, image or custom field, an invite, a call, a feed or an activity, or let provider text reach a stored row, a log or a user.

**A departure** from any condition above that you find necessary: stop before making it, record it and the reason, and report it. It goes back to the Dev Manager (DM-15 1.3).

**Local runs** (P06.DB brief, D4): a disposable database in your own sandbox, with `docker run` and the job's recipe if Docker works, otherwise a throwaway cluster from local binaries, otherwise CI. The same rules hold: a generated password and a new marker, loopback or a socket only, removed afterwards, and no forbidden or `PG*` name present. Local runs are iteration, not evidence. Your report says which you used.

## 4. Checks

Report the exact commands and results.

1. `git diff --check <START_SHA> HEAD`, and `git diff --name-only <START_SHA> HEAD`: only owned paths changed.
2. Classification with the trusted policy from `main`, run outside the tree, as root `AGENTS.md` requires. Expected: full scope.

   ```bash
   base=$(git rev-parse origin/main); policy_dir=$(mktemp -d)
   git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
   python3 -I "$policy_dir/change_scope.py" --base <START_SHA> --head "$(git rev-parse HEAD)" --merge-base
   ```

3. The installs from the locks, with `pip install --require-hashes` (and the harness's `npm ci`), and `pip check`, in a clean process, for the API, the proof and the harness.
4. The offline checks, with each component's documented commands: the unit tests with counts at the start and at your head (at `02072f4`: the API 277, the proof 142, the harness 570); Ruff check and format; mypy with its file count; the Django pin test; the toolchain pin test (`cd services/api && python3.12 -m unittest tests.test_toolchain_pins`); the API's static model check with `makemigrations --check --dry-run`; the sealed-runtime test; the harness's `node --check` and its run-plan count.
5. `reference.py` unchanged: `git diff --quiet 02072f4dcb0c20dd45dee9bc02e75323d0a2aec7 HEAD -- proofs/postgres-ordering/glow_ordering_proof/reference.py` and its SHA-256; and `0001`, `0002` unchanged by their hash test.
6. Your local runs, if any: which database, its version, and the results, marked "iteration, not evidence".
7. **The Foundation run on your last code commit:** its run ID, each job's conclusion (eight jobs), and the gate's log line, which must be `Application checks passed`.
   - **Wait before pushing again.** After pushing your last code commit, push nothing more to your branch until that commit's Foundation run has finished. Runs of the same branch cancel each other (the CI policy), so an early records push can cancel the code run or leave it marked `cancelled` (the manager workflow, step 3; AM5-14).
   - A push that changes only Markdown skips the application jobs by the CI policy's design. If your last commit changes only the record, the evidence of record is the push run of your last code commit, and your record says so.
   - From the database job's log, **per subject:** the refusals; the image digest and `SELECT version()`; `makemigrations --check` and the applied ledger; each case with its observed waits and blocking backends (the new cases named); the oracle's result over every row, with the new rule; each race's seed, iterations, measured overlaps, seconds and count per commit order; each control's declared signal and whether it was met, the new planted control among them; the delivery phase's checks; the container's removal.
   - Confirm that the log shows no password and no marker, and no `***` mask where either would be. If your tools cannot read the run, say so; re-run or dispatch nothing.
8. A secret scan over your whole diff: no secret, token, API key, password, marker value or email address.

## 5. Owned paths, push and records

- **You may change:**
  - `services/api/**`, except its dependency files (`requirements*.in`, `requirements*.lock`, the dependency lists in `pyproject.toml`, `dependency-inventory.json`) and its runtime settings, URL configuration and configuration guards (`glow_api/settings.py`, `glow_api/urls.py`, `glow_api/configuration*.py`, `glow_api/runtime.py`);
  - `proofs/postgres-ordering/**`, except its dependency files and `glow_ordering_proof/reference.py`;
  - `proofs/stream-chat/**`, for item 8 only, except its dependency files (`requirements*`, `package.json`, `package-lock.json`);
  - `docs/architecture/data-model.md` and `docs/operations/migration-plan.md`;
  - the evidence record `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`: a new section "Stage B1" only, after the existing sections, which stay byte-identical.
- **Nothing else,** including the briefs, the CI policy, the P11 acceptance plan, `.github/` (report it if the database job must change), `apps/`, `packages/`, `scripts/`, the root `.gitignore`, any `.claude/` path and every other document. Report any other change you think is needed.
- **Commit and push** your session branch. Don't open a pull request.
- **Your section "Stage B1"** in the evidence record:
  - the prompt's revision and start SHA, your head, your branch and the run of record;
  - for items 1 to 9 of section 3: done (`file:line` and its test) or left (the reason), with the choices items 1, 2 and 8 ask you to record, and how you established that `0003` was applied only to disposable databases;
  - the run of record's results per subject, against Stage A's run of record (37383940454);
  - local runs, marked "iteration, not evidence";
  - every check, with its exact results;
  - deviations and limits;
  - what the exact-head review must know.

## 6. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<START_SHA>`);
- the environment check, and what a local database could use;
- your branch, head SHA and tree, and the changed paths;
- for items 1 to 9 of section 3: done or left, with the recorded choices;
- every check, with its exact results, and the run of record's details from section 4 item 7, per subject;
- which local database you used, if any;
- deviations, departures you stopped at, findings outside the work with their class, open questions and limits.

# P06.2 Stage A prompt — the send and revocation path in the app, on a disposable PostgreSQL

- **Owner:** App Manager 6. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 5 October 2026.**
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 2: items 1, 2 and 4, D1 (Stage A), D2 to D7, the owned paths and "Documents each stage updates". It applies the Dev Manager's read (DM-13) as written.
  - Carried work: the [P06.DB brief](../planning/p06-db-disposable-postgres-proof.md), "Carried to P06.2", items 1 to 6, with the design it carries (its D1 to D6).
- **Where the result goes:**
  - the session's code and tests, its new evidence record `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`, section "Stage A", and its updates to two architecture documents;
  - the Foundation run on the session's last code commit becomes the run of record;
  - the manager adds its verification to that record, records the outcome in the brief's "Sessions", and updates the P11 plan's DB06 and DB09 entries.
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v6: Opus 5.5, extra high.** Effort score 3.45 (confidence 0.66); rung probabilities low 0.00, medium 0.00, high 0.02, extra high 0.51, max 0.47, ultracode 0.00. Model probabilities Fable 5.1 0.48, Opus 5.5 0.52 (confidence 0.05). Flags: boundary between max and extra high; model near tie. Sent 2026-10-05T19:43:23Z. Nathan picks the cell.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** DM-13 approved the brief with conditions, which revision 2 applies as written, so this prompt needs no further read (DM-03 G2). It authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and the session calls no provider.
- **It runs alone** (OD-29, the linear process). Its exact-head review follows.
- **Deletion condition:** prune after Stage A's PR merges and the evidence record holds the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **implementation session for P06.2 Stage A**, the first of three stages of P06.2, the chat integration of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<START_SHA>`.

**What exists.** The app is built at fixture scope: a Django API with no database at runtime (a dummy backend, and a guard that refuses every connection name), a mobile app on fixture adapters, and 32 unapplied model definitions in `services/api/glow_persistence`. P06.1 proved Stream Chat's permission model. P06.DB built `proofs/postgres-ordering/`: a reference design that orders message-send authorizations against every revocation of contact, proven on a disposable PostgreSQL 17 database by the Foundation job "Database proof checks", with forced races, a stress run, a commit-order oracle and ten negative controls.

**What Stage A does.** You carry that reference design into the app as a persistence adapter behind a domain port, and run P06.DB's suite against the adapter in the same job. You also add the outbox path that turns each authorization and revocation into a provider call, against a fixture provider only. **No app runtime gains a database, real authentication or a live provider**: the API's settings, connection refusal and dummy backend do not change, and P11 wires the runtime.

- Nathan started you manually and will relay your report to the manager (App Manager 6). You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- Your boundary is scope:
  - write only your owned paths (section 5);
  - push only your own session branch. Each push runs the Foundation workflow on your branch; read those runs if your tools can. On GitHub do nothing else: no pull request, no PR comments, no re-runs, no workflow dispatches. Change nothing in Notion.
- **Never:**
  - dump the environment, or print, echo or log the proof database's passwords or the run's marker, in any form;
  - connect to any database other than a disposable one that you or the job start for this proof (P06.DB brief, D4), or set a comment on any other database. Never connect to Stream, HDE, Railway or any other provider;
  - run `playwright install` or `eas`;
  - run Django's `migrate` anywhere but against a disposable proof database, from the proof's own settings;
  - add a dependency anywhere.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. No `PG*`, `PROOF_DB_*` or `STREAM_*` name should be set: `compgen -e | grep -E '^(PG|PROOF_DB_|STREAM_)'` prints names only. If any is present, report its name first in your report, never read or use its value, and run every proof command in a clean process environment that lacks it.
3. The pinned toolchain is in `$HOME/.local/bin`: Node 24.19.0, npm 11.9.0 and Python 3.12.14. Put `$HOME/.local/bin` first on PATH, then record `command -v python3.12` and its version. Create any virtual environment with `python3.12`.
4. Run the API's and the proof's commands in a clean process environment, as `docs/operations/local-development.md` and the proof's README show: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8` plus only the proof's own variables. Installs get the proxy and CA variables by reference, never printed.
5. **What a local database can use** (P06.DB brief, D4): record whether `docker info` succeeds (its exit status only), and `command -v initdb pg_ctl postgres pg_isready psql`.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git merge --ff-only <START_SHA>          # on your own session branch
git rev-parse HEAD                       # must print <START_SHA>
git diff --stat <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/ proofs/ .github/ docs/architecture/   # must print nothing
git cat-file -e origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md 2>/dev/null; echo $?   # must print a non-zero status
```

- The fourth and fifth commands check the live manager branch. If code or the evidence record for this stage has already landed there, this prompt is stale: stop and report (the manager workflow, step 3, AM5-15).
- If any check fails, stop and report.

Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`, and `services/api/README.md`;
- the P06.2 brief, `docs/planning/p06-2-chat-integration.md`, revision 2;
- the P06.DB brief, `docs/planning/p06-db-disposable-postgres-proof.md`: D1 to D6, item 6 and "Carried to P06.2";
- the DM-13 report, `docs/continuity/dev-manager/reviews/2026-10-05-dm-13-p06-2-brief-read.md`, and the DM-12 report, `docs/continuity/dev-manager/reviews/2026-10-05-dm-12-p06-db-dbshell-read.md`;
- the P06.DB evidence record, `docs/testing/evidence/2026-09-29-p06-db-disposable-postgres-proof.md`: "P06.DB-C2 corrections" (the run of record your reference subject must match), "Codex's review of PR28's final head" (CX1, CX2) and "Exact-head review of P06.DB-C1" (R1 to R4);
- ADR 0003 and the chat-provider architecture document, `docs/architecture/chat-provider-permissions.md`, section 8;
- `docs/architecture/data-model.md` and `docs/architecture/interactions-fixtures.md`;
- `proofs/postgres-ordering/` whole, and `services/api/glow_persistence/models.py`, `services/api/glow_domain/interactions.py` and `services/api/glow_domain/ports.py`;
- `.github/workflows/foundation.yml`, the `database` job and the gate.

## 3. The work

Work in this order. Items 1 to 4 come before the suite's first run on **any** database, local or CI (DM-09, DM-12).

**Before the first run**

1. **A used database is refused** (P06.DB's carried item 1). The proof's `run` refuses a database whose proof log already holds rows, with an offline test, or each run gets its own run tags. Choose one and record why.
2. **`dbshell` is refused** (carried item 6, in DM-12's words): `dbshell` under the proof's settings refuses with the marker's refusal, with an offline test, so that no command under the proof's settings reaches a database unchecked.
   - **Choose the mechanism and record why** (DM-12's note; DM-13 item 8). A proof-local management command needs the proof package to be an installed app, which it is not today (`INSTALLED_APPS` lists `contenttypes`, `auth` and `glow_persistence`). Making it one, or another refusal that every command loads, are both acceptable; leaving it unrecorded is not.
3. **The oracle checks who sent** (carried item 4, CX1): a rule that each submission's actor is its session's account and a member of its match, and a control that writes a misattributed row and must fail. This control is subject-independent, so it also runs against the adapter's rows (item 7).
4. **The session-expiry rule** (carried item 5, CX2; brief D4, confirmed by DM-13): keep P06.DB 5.2's check at a time read after the locks; narrow O5 to match, keeping its detection of the `transaction_start_time` control; and force the boundary with a delay between the check and the commit, as a forced case.

**The app's path**

5. **The domain port and the persistence adapter** (brief items 1 and 2, D2). A port in `glow_domain` for send, block, unblock, unmatch, suspend, delete, sign-out and administrative expiry, and the pause, profile restriction and consent withdrawal of D5. An ORM adapter that implements it on `glow_persistence`'s models, in `glow_persistence` or a new module that imports the models; record which and why.
   - **The transaction design is P06.DB D5's, carried as written:** `READ COMMITTED`; row locks by primary key with `SELECT ... FOR UPDATE` in one canonical order (lower account, higher account, match, the sending session); every check under the locks, time read after them (5.2); authorize first, then deduplicate (5.4); a locked read that finds no qualifying row is a refusal (5.5); deletion as the lifecycle transition, never a hard row delete (5.6). The send writes its `MessageSubmission` and `OutboxEvent` in the same transaction.
   - **The send's extra checks** (D5, DM-13 4.1): a paused or restricted profile and a withdrawn onboarding consent (F02's `ConsentIntent`, held as `ConsentDecision`; record the `purpose` value you use) refuse a send. Each of those three writers takes the account row lock in the canonical order (P06.DB 5.3) and bumps the version of the row the send checks, and the send reads that state under its account locks. Each gets forced race cases both ways, as sign-out has (P06.DB 5.1). If a writer cannot join, exclude it by name from DB06's claim, with the reason, and report it.
   - **No fault switches in the adapter** (DM-13 2.1). No test-only branch, flag or hook that changes the adapter's behavior. Hooks the suite needs to force an interleaving (the `Hooks` of `glow_ordering_proof/interface.py`) may be passed in, as the reference design takes them, but they only signal and wait; they never skip a lock, a check or a write.
6. **The new models and migration `0003`** (D7). A model that maps an account to a random, opaque Stream user ID (`secrets.token_hex`), never derived from an account ID, name or email, never shown or logged; and the read cursor per member and match that unread will use (brief item 5). Migration `0003` is additive and unapplied anywhere but a disposable proof database; `0001` and `0002` stay byte-identical. `makemigrations --check --dry-run` passes in the API's static check and in the proof, and the proof's run applies `0003` from zero.
7. **The suite on two subjects** (D3). The race suite runs the reference design and the app's adapter through the same interface, in the same job, each reported separately. A guarantee is claimed for the app only from the adapter's own run.
   - **The adapter's run:** every case, with each forced wait observed and its holder; the stress run with its floors and **per-order counts** (carried item 2: a seeded delay for the revocation in the session races, and each race's count per commit order printed with its results); the oracle over every row; and the subject-independent oracle controls, CX1's misattributed row among them.
   - **The reference's run:** its forced cases and all ten negative controls, unchanged, and its stress run. Do not change the reference design.
   - **The budget** (DM-13 2.2): both subjects keep P06.DB's stress budget, 200 iterations or 30 seconds per race (`budget.py`), and the job's timeout stays 20 minutes. C2's suite step took 72 seconds, so both fit. If a measured run shows they do not, the reference's stress run (never the adapter's) shrinks to what its stress controls need, and you report the numbers; do not raise the timeout without reporting why.
   - **Tests for R3 and R4** (carried item 3): a test that fails without each of the per-iteration oracle check's `case_id` at its call site, the empty-signal guard, and the sign-in exclusion.
8. **Outbox and delivery against a fixture provider** (brief items 2 and 3). A provider port for chat, with a fixture adapter only (Stage B adds Stream's).
   - Match activation creates the `ChatBinding` with a random channel ID and both members' Stream user IDs, generated and committed with the `OutboxEvent` in the same transaction, before any provider call (DM-13 9.4). The proof's fixture factory calls that path when it creates a match.
   - The events: channel creation with exactly the two members; an authorized message sent on the member's behalf; on unmatch or block, removal of **both** members; on suspension or deletion, deactivation of the provider user and a per-user token revocation, which every session-epoch bump triggers (D6, DM-13 5.1). No event names a channel, member or user `name`, `image` or custom field. No event creates an invite, call, feed or activity.
   - Delivery logic runs in-process under the proof's settings: it leases an event, makes one provider call, records the receipt (`ChatBinding.channel_ref` state, `MessageSubmission.provider_message_ref`) and marks the event delivered. A retry reuses the committed IDs and never creates a second channel, message or member. Every provider error maps to a Glow error code; no provider text is stored or surfaced.
   - Tests on the disposable database: delivery of each event kind; a retry after a fixture failure; a revocation committed after a send was authorized but before its delivery (the message is delivered into history and never re-sent; record what the app does with it).
9. **The token rules** (brief item 4, D6). A domain function that issues a token grant for a valid, current-epoch session of an `active` account only, with a one-hour lifetime, and refuses after suspension or deletion. Tests offline. It issues no real token and calls no provider.
10. **The runtime stays sealed** (D2, DM-13 2.3). An API test shows that the runtime settings and URL configuration import none of the adapter's modules, that the database backend is still the dummy one, and that the connection refusal is unchanged.
11. **The documents** (the brief, "Documents each stage updates"): `docs/architecture/data-model.md` for the new models, the consent purpose and the outbox flow, and `docs/architecture/interactions-fixtures.md` for what P06 and P11 now hold.

**Not in Stage A:** the Stream adapter and the `getstream` dependency (Stage B); any API route or served feature; the mobile app (Stage C); push (P06.3); allauth.

**Rules for every change:**

- **A test for each change.** Each code item gets a test that fails without it and passes with it. Say which test covers which item.
- **Evidence comes from the database.** Every guarantee is judged by what PostgreSQL recorded, never by what the test code believes it did.
- **No weakened check.** Never loosen a case, the oracle, a control's signal or a floor to make a run pass. A flaky case is a finding (OD-21), not a retry.
- **No password or marker anywhere:** not in the diff, a log line, the evidence record or your report.
- **No dependency change** in any lock, `requirements*.in` or `pyproject.toml` dependency list.

**Findings outside this work:** report each with its class. Fix it here only if it could do one of these, and then with a test:

- let a send authorization commit after a revocation that invalidates it without the suite failing;
- let a password, the marker or a connection value reach a log, an artifact or a file outside the job's temporary directory;
- let the job, the proof or the adapter connect to anything but its own disposable database, or let the API runtime connect to any database;
- make DB06's or DB09's mark claim more than the run shows.

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

3. The installs from the locks, with `pip install --require-hashes`, and `pip check`, in a clean process, for the API and the proof.
4. The offline checks, with the API's and the proof's documented commands: the unit tests with counts at the start and at your head (the proof's C2 count was 98); Ruff check and format; mypy with its file count; the Django pin test; the toolchain pin test (`cd services/api && python3.12 -m unittest tests.test_toolchain_pins`); the API's static model check with `makemigrations --check --dry-run`; and the sealed-runtime test.
5. Your local runs, if any: which database, its version, and the results, marked "iteration, not evidence".
6. **The Foundation run on your last code commit:** its run ID, each job's conclusion (eight jobs, "Database proof checks" included), and the gate's log line, which must be `Application checks passed`.
   - **Wait before pushing again.** After pushing your last code commit, push nothing more to your branch until that commit's Foundation run has finished. Runs of the same branch cancel each other (the CI policy), so an early records push can cancel the code run or leave it marked `cancelled` (the manager workflow, step 3; AM5-14).
   - A push that changes only Markdown skips the application jobs by the CI policy's design. If your last commit changes only the record, the evidence of record is the push run of your last code commit, and your record says so.
   - From the database job's log, **per subject:** the wrong-marker step and the new refusals; the image digest and `SELECT version()`; `makemigrations --check` and the applied ledger with `0003`; each case with its observed waits and blocking backends; the oracle's result over every row; each race's seed, iterations, measured overlaps, seconds and count per commit order; each control's declared signal and whether it was met; the container's removal.
   - Confirm that the log shows no password and no marker, and no `***` mask where either would be. If your tools cannot read the run, say so; re-run or dispatch nothing.
7. A secret scan over your whole diff: no secret, token, API key, password, marker value or email address.

## 5. Owned paths, push and records

- **You may change:**
  - `services/api/**`, except its dependency files (`requirements*.in`, `requirements*.lock`, the dependency lists in `pyproject.toml`) and its runtime settings, URL configuration and configuration guards (`glow_api/settings.py`, `glow_api/urls.py`, `glow_api/configuration*.py`, `glow_api/runtime.py`);
  - `proofs/postgres-ordering/**`, except its dependency files;
  - `.github/workflows/foundation.yml`: the `database` job only;
  - `docs/architecture/data-model.md` and `docs/architecture/interactions-fixtures.md`;
  - the new evidence record `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`, section "Stage A".
- **Nothing else,** including the briefs, the CI policy, the P11 acceptance plan, `apps/`, `packages/`, `scripts/`, the other workflow jobs and the gate, the root `.gitignore`, any `.claude/` path and every other document. Report any other change you think is needed.
- **Commit and push** your session branch. Don't open a pull request.
- **Your evidence record**, `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`, with a short header (work item, brief revision 2, this prompt's revision and start SHA) and one section, "Stage A":
  - the start SHA, your head, your branch and the run of record;
  - for items 1 to 11 of section 3: done (`file:line` and its test) or left (the reason), with the choices items 1, 2, 5 and 6 ask you to record;
  - the run of record's results per subject, against C2's run of record for the reference;
  - local runs, marked "iteration, not evidence";
  - every check, with its exact results;
  - deviations and limits, including any writer excluded from DB06's claim;
  - what the exact-head review must know.

## 6. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<START_SHA>`);
- the environment check, and what a local database could use;
- your branch, head SHA and tree, and the changed paths;
- for items 1 to 11 of section 3: done or left, with the recorded choices;
- every check, with its exact results, and the run of record's details from section 4 item 6, per subject;
- which local database you used, if any;
- deviations, findings outside the work with their class, open questions and limits.

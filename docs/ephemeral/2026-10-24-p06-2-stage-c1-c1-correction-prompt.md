# P06.2 Stage C1-C1 prompt — correction pass on C1's exact-head review

- **Owner:** App Manager 7. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 24 October 2026.**
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 14: "C1's exact-head review, and C1-C1", and "Stage C under OD-45" with DM-22's conditions.
  - Inputs:
    - the evidence record's "Exact-head review of Stage C1", findings 1 to 12 with the manager's dispositions;
    - the [DM-22 report](../continuity/dev-manager/reviews/2026-10-24-dm-22-p06-2-stage-c-read.md), item 3.2.
- **Where the result goes:** the session's code and tests, its record changes, and its section "Stage C1-C1" in the evidence record. The run of record is the Foundation run on its last code commit, if its branch is under the workflow's push filter. The manager adds its verification and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.09 (confidence 0.87); rung probabilities low 0.00, medium 0.05, high 0.81, extra high 0.14, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 1.00, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 1.00). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.050, Opus 5.5 at high 0.810, Opus 5.5 at extra high 0.140, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-10-24T15:36:16Z. Nathan picks the cell.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** none needed. The pass authorizes no credential use, provider call, dependency or design change. Each fix hardens or tests a DM-22 condition as written.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and the session calls no provider.
- **It runs alone** (OD-29). An exact-head re-review of the corrected head follows, then Codex's code review of the final head (OD-41).
- **Deletion condition:** prune after Stage C1's PR merges and the evidence record holds the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **correction session P06.2 Stage C1-C1**, an offline pass on Stage C1 of P06.2, the chat integration of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<START_SHA>`.

**What exists.** Stage C1 is the draft PR32, from the manager branch `claude/magical-wozniak-yfmmx2` into `main`.

- **What C1 added,** under Nathan's D8 decision (OD-45: the app holds no Stream credential, and Glow's API serves history and new messages):
  - the provider port's text read;
  - the history read, the conversation list and the read-cursor command (`services/api/glow_chat/reads.py`);
  - the server's projections;
  - the proof's read phase (`proofs/postgres-ordering/glow_ordering_proof/read_phase.py`, 58 cases);
  - the production contracts.
- **Its exact-head review** (the evidence record, "Exact-head review of Stage C1") found the safety order, the checks, the text rule, the contracts and the sealed runtime holding. It asked for one hardening in a correction class (finding 1) and two record sentences (finding 2). The manager sends you those and six smaller items.
- **The code at your start** is byte-identical to `91c3945`'s, the code of the run of record, Foundation run 40064952123.

**How you work:**
- Nathan started you manually and will relay your report to the manager (App Manager 7). You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- Your boundary is scope:
  - write only your owned paths (section 5);
  - push only your own session branch. If your branch is under the workflow's push filter (`claude/**`), each push runs the Foundation workflow on it; read those runs if your tools can. On GitHub do nothing else: no pull request, no PR comments, no re-runs, no workflow dispatches. Change nothing in Notion.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, token, password or marker, in any form;
  - call Stream, or run any harness command in `proofs/stream-chat/` that sends a request;
  - connect to any database other than a disposable one that you or the job start for this proof (P06.DB brief, D4), and never to HDE, Railway or any other provider;
  - run `playwright install` or `eas`, or Django's `migrate` against anything but a disposable proof database, from the proof's own settings;
  - add or change a dependency, a version, a lock file, a migration or a contract shape.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If any is present, stop and report: this session must start in `Glow App - No Stream`.
3. **No `PG*` or `PROOF_DB_*` name should be set** (`compgen -e | grep -E '^(PG|PROOF_DB_)'`). If one is present, report its name first, never read or use its value, and run every proof command in a clean process environment that lacks it.
4. **No `.env` file:** `ls -a . services/api proofs/postgres-ordering | grep -x '\.env'` must print nothing. If one exists, report it without reading it, and stop.
5. **The toolchain.** The pinned toolchain is in `$HOME/.local/bin`: Python 3.12.14, Node 24.19.0 and npm 11.9.0.
   - Put `$HOME/.local/bin` first on PATH in every process you run.
   - Record `command -v python3.12` and its version.
   - Create any virtual environment with `python3.12`, outside the checkout.
6. **A clean process environment.** Run each component's commands in one, as `docs/operations/local-development.md` and the READMEs show: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only that component's own variables. Installs get the proxy and CA variables by reference, never printed.
7. **What a local database can use** (P06.DB brief, D4). Record whether `docker info` succeeds (its exit status only), and the output of `command -v initdb pg_ctl postgres pg_isready psql`.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git merge --ff-only <START_SHA>          # on your own session branch
git rev-parse HEAD                       # must print <START_SHA>
git diff --stat <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/ proofs/ packages/ apps/ .github/ docs/architecture/   # must print nothing
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md | grep -c '^## Stage C1-C1'   # must print 0
git diff --quiet 91c39457a9657cc8c4bf8b1964ec822fb6506491 HEAD -- proofs .github services scripts apps packages && echo "the code of the run of record"
```

- The fourth and fifth commands check the live manager branch. If code or this pass's section has already landed there, this prompt is stale: stop and report (AM5-15).
- If any check fails, stop and report.

**Then read, completely:**

- root `AGENTS.md` and `CLAUDE.md`, `services/api/README.md` and `proofs/postgres-ordering/README.md`;
- the P06.2 brief, `docs/planning/p06-2-chat-integration.md`: "Stage C under OD-45" and "C1's exact-head review, and C1-C1";
- the DM-22 report's item 3.2, in `docs/continuity/dev-manager/reviews/2026-10-24-dm-22-p06-2-stage-c-read.md`;
- the evidence record, `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`: "Stage C1", "Manager verification of Stage C1" and "Exact-head review of Stage C1", whole;
- **in `services/api`:**
  - `glow_chat/reads.py` and `glow_chat/contact.py`;
  - `glow_domain/chat_projections.py`;
  - their tests;
- **in the proof:** `glow_ordering_proof/read_phase.py` and its tests, with `cases.py`, `results.py` and `interface.py` for how a case and a control are declared;
- `docs/architecture/production-contracts.md`, "Pagination, idempotency and stale state" and "F11 under OD-45", and `docs/architecture/data-model.md`, "Chat contact and the outbox".

## 3. The work

**For each code item:**
- write a test that fails without the change and passes with it;
- show the failure with a reversal in a scratch copy outside the repository.

Items 5 and 6 are records.

1. **Finding 1: the reads' transactions are durable** (DM-22 3.2, "A safety action must never wait on the provider").
   - **The change:** `_run` (`reads.py:133`) opens `transaction.atomic(durable=True)`. Django 5.2.17, as pinned, raises `RuntimeError` for a durable block inside an open atomic block. `_run` must turn that into an `error` result, never a page.
   - **The savepoint at `reads.py:615`** (the cursor move's insert) stays as it is, inside the durable block.
   - **Before the provider call,** `read_history` asserts that no atomic block is open (`connection.in_atomic_block` is false). If one is open, it returns an `error` result and makes no provider call.
   - **A read-phase case** calls the read inside an open transaction. It expects `error`, and the fixture provider records no call.
   - **An API test, if one fits without a database,** shows the assertion's refusal.
   - **Unchanged:** `contact.py`'s `_run`, Stage A's single-transaction design (the review calls its change optional). Record that.
2. **Finding 5: the final check's lock order is tested.**
   - **The case:** a read-phase case holds the read at `after_first_lock` of its final check, against the suspend writer and against the block writer, both ways. Each forced wait is observed, as for the send's `opposing_*` cases.
   - **The planted variant:** a variant whose final check locks the session, then the match, then the accounts must fail that case by a declared signal, in the same run. Build it from the adapter's own steps or helpers, as the existing read controls are, with no switch in the adapter.
   - **Name the case and the control,** and give the read phase's new count.
3. **Finding 8: `read_waits` releases its hold first** when it observes a wait, as `read.block_during_provider_call` does. A broken adapter that held locks across the call then fails the case by its clean signal, not by a 60-second harness error. Show it with a reversal: an adapter variant that holds its first check's transaction across the call.
4. **Finding 10: `accountsession_missing` from one place.** Either the projection and `_lock_shared` share one constant, or a test ties the projection's mapping to the reason `_lock_shared` produces. `_lock_shared` is in `contact.py`, outside your owned paths, so prefer the test unless the constant can live in a module you own.
5. **Finding 2 and C1-X1, the production contracts.** In "Pagination, idempotency and stale state":
   - **line 41's rule:** every mutating intent carries an idempotency key and an expected version. Name `ReadCursorIntent`'s exception and point to "F11 under OD-45";
   - **line 45's sentence** "The selected provider must prevent direct SDK bypass; A08 remains a required capability proof": mark it as P02's baseline, superseded by OD-45 (the app holds no provider SDK or credential).
6. **Findings 6, 7 and 9, the records:**
   - **6:** in "F11 under OD-45", `ConversationSummary.state`'s `closed` and its intended producer: a later push of the same summary (the brief's point d). The contract is unchanged.
   - **7:** in the production contracts, `ConversationMessage.at` is the acceptance time for accepted messages and the submission time for the member's own pending and failed ones. A client keys on `submission_id`, never on `at`.
   - **9:** in the data model, the reads make no `BINDING_NOT_ACTIVE` check. A `failed` binding under an active match is listed and serves the member's own unsent rows; no accepted message can exist for it.

**Not in C1-C1:**
- findings 3, 4, 11 and 12, which the P11 plan carries;
- any contract shape, the corpus or the generated outputs;
- `contact.py` and `delivery.py`;
- the provider adapters;
- `reference.py` and its ten controls;
- every dependency, lock file and migration;
- the workflow.

**A finding outside this work:** report it with its class. Fix it here only if it could do one of these, and then with a test:
- let a read succeed after a revocation committed before its final check;
- let a safety action wait on the provider;
- let provider text, a provider ID or any other provider field reach a DTO, a log or a user.

**Rules:**
- reversals in a scratch copy outside the repository, never the checkout, with `git status` clean afterwards (DM-14 item 6);
- evidence from the database, never from what the test code believes it did;
- no weakened case, control, signal or floor;
- no password or marker anywhere.

**A departure** from any of the above that you find necessary: stop before making it, and report it.

**Local runs** (P06.DB brief, D4). Use a disposable database in your own sandbox:
- with `docker run` and the job's recipe, if Docker works;
- otherwise a throwaway cluster from local binaries;
- otherwise CI.

The same rules hold: a generated password and a new marker, loopback or a socket only, the database removed afterwards. Local runs are iteration, not evidence.

## 4. Checks

Report the exact commands and results.

1. **The diff:** `git diff --check <START_SHA> HEAD` and `git diff --name-only <START_SHA> HEAD`. Only owned paths changed.
2. **Classification,** with the trusted policy from `main`, outside the tree. Expected: full scope.

   ```bash
   base=$(git rev-parse origin/main); d=$(mktemp -d)
   git show "$base:scripts/change_scope.py" > "$d/change_scope.py"
   python3 -I "$d/change_scope.py" --base <START_SHA> --head "$(git rev-parse HEAD)" --merge-base
   ```
3. **Installs:** hash-locked installs and `pip check` for the API and the proof.
4. **The offline checks:**
   - the API's tests (361 at the start) and the proof's tests (157 at the start), with their counts;
   - Ruff check and format, and mypy, for both;
   - the static check, with `makemigrations --check --dry-run`;
   - the sealed-runtime test.
5. **Unchanged:** an empty `git diff <START_SHA> HEAD` over `packages/`, `apps/`, `.github/`, `proofs/stream-chat/`, every dependency file, the migrations, `contact.py`, `delivery.py`, the provider adapters and `reference.py`.
6. **Your local runs, if any:** which database, its version, the read phase's result, and the reversals' results, marked "iteration, not evidence".
7. **The run of record:**
   - **If your branch is under the workflow's push filter:** the Foundation run on your last code commit, with:
     - its run ID and each job's conclusion (eight jobs);
     - the database job's duration;
     - from its log, the read phase's count and verdict, the new cases' observed waits, and each read control's declared signal;
     - the gate's line, `Application checks passed`.

     Push nothing more until it has finished (AM5-14).
   - **Otherwise:** say that no run started, and why.
8. **A secret scan** over your whole diff and your record.

## 5. Owned paths, push and records

- **You may change:**
  - `services/api/glow_chat/reads.py`, `services/api/glow_domain/chat_projections.py`, and the tests under `services/api/tests/` that cover them;
  - `proofs/postgres-ordering/glow_ordering_proof/read_phase.py`, its tests, and `proofs/postgres-ordering/README.md`'s read-phase paragraph, if a count or a case name in it changes;
  - `docs/architecture/production-contracts.md` and `docs/architecture/data-model.md`, for items 5 and 6 only;
  - the evidence record: a new section "Stage C1-C1" after the existing sections, which stay byte-identical.
- **Nothing else.** Report any other change you think is needed, before making it.
- **Commit and push** your session branch. Don't open a pull request.
- **Your section "Stage C1-C1"** records:
  - the prompt's revision and start SHA, your head, your branch and the run of record;
  - items 1 to 6, each done (with `file:line`, its test and its reversal) or left (with the reason);
  - every check with its exact results;
  - deviations and limits;
  - what the exact-head re-review must know.

## 6. Report

Your final message is the report Nathan relays. It covers:
- the prompt revision (revision 1, from `<START_SHA>`);
- the environment check (names only, the `.env` check included) and what a local database could use;
- your branch, head SHA and changed paths;
- items 1 to 6, done or left;
- every check with its exact results, and the run of record's details;
- deviations, departures you stopped at, findings outside the work with their class, and limits.

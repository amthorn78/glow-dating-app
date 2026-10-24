# P06.2 Stage C1-C2 prompt — correction pass on C1-C1's re-review

- **Owner:** App Manager 7. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 24 October 2026.**
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 15: "C1-C1's re-review, and C1-C2", with "C1's exact-head review, and C1-C1" and "Stage C under OD-45".
  - Input: the evidence record's "Exact-head review of Stage C1-C1", findings R1 to R5 with the manager's dispositions.
- **Where the result goes:**
  - the session's code and tests, its record changes, and its section "Stage C1-C2" in the evidence record;
  - the run of record: the Foundation run on its last code commit, if its branch is under the workflow's push filter;
  - the manager adds its verification and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.10 (confidence 0.85); rung probabilities low 0.00, medium 0.07, high 0.77, extra high 0.16, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.99, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.99). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.069, Opus 5.5 at high 0.762, Opus 5.5 at extra high 0.158, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.001, Sonnet 5.5 at high 0.008, Sonnet 5.5 at extra high 0.002, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-10-24T17:10:02Z. Nathan picks the cell.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** none needed. The pass authorizes no credential use, provider call, dependency or design change; each fix completes DM-22 3.2 or a review finding as written.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and the session calls no provider.
- **It runs alone** (OD-29). An exact-head re-review of the corrected head follows, then Codex's code review of the final head (OD-41).
- **Deletion condition:** prune after Stage C1's PR merges and the evidence record holds the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **correction session P06.2 Stage C1-C2**, the second offline pass on Stage C1 of P06.2, the chat integration of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<START_SHA>`.

**What exists.** Stage C1 and its first correction pass C1-C1 are the draft PR32, from the manager branch `claude/magical-wozniak-yfmmx2` into `main`.

- **What C1 added,** under Nathan's D8 decision (OD-45): the history read, the conversation list and the read-cursor command (`services/api/glow_chat/reads.py`), the proof's read phase (`proofs/postgres-ordering/glow_ordering_proof/read_phase.py`), and the contracts.
- **What C1-C1 added** (code `f4749ee`):
  - the reads' transactions are durable (`transaction.atomic(durable=True)`);
  - the history read refuses an open atomic block before the provider call (`connection.in_atomic_block`);
  - `read.inside_open_transaction`;
  - `read.final_check_first_lock`, with the planted control `read.final_check_lock_order_inverted`.

  The read phase has 60 cases and three read controls.
- **C1-C1's exact-head re-review** (the evidence record, "Exact-head review of Stage C1-C1") confirmed those. It found two gaps in correction classes, which the manager sends you with two nits:
  - **R1:** a transaction opened by Django's `transaction.set_autocommit(False)` is not an atomic block, so it passes both guards. In the reviewer's scratch experiment, the provider call ran while the reader held the first check's locks, and a block waited on the reader.
  - **R2:** the lock-order case only ever uses the lower member as the reader.
- **The code at your start** is byte-identical to `f4749ee`'s, the code of the run of record, Foundation run 40109633125.

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
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md | grep -c '^## Stage C1-C2'   # must print 0
git diff --quiet f4749ee71d4db470d8d470354a54e3030c73d455 HEAD -- proofs .github services scripts apps packages && echo "the code of the run of record"
```

- The fourth and fifth commands check the live manager branch. If code or this pass's section has already landed there, this prompt is stale: stop and report (AM5-15).
- If any check fails, stop and report.

**Then read, completely:**

- root `AGENTS.md` and `CLAUDE.md`, `services/api/README.md` and `proofs/postgres-ordering/README.md`;
- the P06.2 brief, `docs/planning/p06-2-chat-integration.md`: "Stage C under OD-45", "C1's exact-head review, and C1-C1" and "C1-C1's re-review, and C1-C2";
- the DM-22 report's item 3.2, in `docs/continuity/dev-manager/reviews/2026-10-24-dm-22-p06-2-stage-c-read.md`;
- the evidence record, `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`, whole:
  - "Stage C1-C1";
  - "Manager verification of Stage C1-C1";
  - "Exact-head review of Stage C1-C1";
- `services/api/glow_chat/reads.py`, with `glow_chat/contact.py` for the writers' lock order, and the reads' tests;
- in the proof: `glow_ordering_proof/read_phase.py` and its tests, with `cases.py`, `results.py` and `interface.py`;
- `docs/architecture/production-contracts.md`, "F11 under OD-45";
- the P11 plan's "The reads' limits from P06.2 Stage C1" (`docs/testing/p11-deferred-acceptance.md`), as the manager has corrected it.

## 3. The work

**For each code item:**
- write a test that fails without the change and passes with it;
- show the failure with a reversal in a scratch copy outside the repository.

Item 5 is a record.

1. **R1: the guard also refuses when autocommit is off** (DM-22 3.2, "A safety action must never wait on the provider").
   - **The change:** the history read's guard before the provider call (`reads.py:495`) refuses when `connection.in_atomic_block or not connection.get_autocommit()`, with an `error` result and no provider call.
     - You may also add a database-side check, for example that `pg_current_xact_id_if_assigned()` is null just before the call. If you do, record why, and give it its own test.
     - The durable flag in `_run` stays.
   - **A read-phase case** runs the read on a connection with `transaction.set_autocommit(False)`, then restores autocommit. It expects `error`, and three things are shown:
     - the fixture provider records no call;
     - no transaction ID is assigned;
     - a block by the other member is not held up by the read.
   - **The reversal:** the guard back to `in_atomic_block` alone. That must fail the case, as the reviewer's experiment did.
   - **The wording.** "Inside an open transaction" becomes the exact conditions in three places: the proof README, `read_phase.py`'s docstring and the case title of `read.inside_open_transaction`. The exact conditions are an atomic block, a test case's atomic block, or autocommit off.
2. **R2: the lock-order case runs for both readers.**
   - **The change:** `read.final_check_first_lock` runs its holds for each reader, the lower member and the higher member, against `block_by_high` and `suspend_low`, both ways. Each forced wait is observed.
   - **The reversals:** two wrong final checks, built from the adapter's own helpers in a scratch copy. One locks the reader's own account first. The other locks the lower account, the match, then the higher account, then the session. Show which of them now fails the case.
     - If the second still passes, record why. The order after the first lock is not pinned by the case, and it is deadlock-free against today's writers: each writer that locks both accounts takes the lower first, and none locks the higher account and the match without the lower. Check that reading against `contact.py`, and say so in your record.
   - **Unchanged:** the planted control `read.final_check_lock_order_inverted` and its declared signals.
3. **R3: the test-case atomic block in the database.** A read-phase variant runs the read under an outer atomic block marked as a Django test case's, as `TestCase` marks it. It expects `error`, `atomic_block_open`, and no provider call.
   - **The reversal:** the `in_atomic_block` half of the guard removed must fail it.
4. **The read phase's count:** name the new cases and give the new count. The three read controls stay.
5. **R5, the production contracts.** In "F11 under OD-45", the sentence on `ConversationMessage.at` for the member's own pending and failed messages: it is the event's `available_at`, the submission time under today's deliverer, which leaves `available_at` unchanged on a retry (`delivery.py:470`). The P11 plan carries the dependency.

**Not in C1-C2:**
- R4, which the P11 plan carries;
- any contract shape, the corpus or the generated outputs;
- `contact.py` and `delivery.py`;
- the provider adapters and the projections;
- `reference.py` and its ten controls;
- the other read cases and controls, except `read.inside_open_transaction`'s title and `read.final_check_first_lock`;
- every dependency, lock file and migration;
- the workflow;
- C1's and C1-C1's sections of the evidence record, which stay byte-identical. Correct their claims in your own section.

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
   - the API's tests (364 at the start) and the proof's tests (159 at the start), with their counts;
   - Ruff check and format, and mypy, for both;
   - the static check, with `makemigrations --check --dry-run`;
   - the sealed-runtime test.
5. **Unchanged:** an empty `git diff <START_SHA> HEAD` over:
   - `packages/`, `apps/`, `.github/` and `proofs/stream-chat/`;
   - every dependency file and the migrations;
   - `contact.py`, `delivery.py`, `glow_domain/` and `glow_persistence/`;
   - `reference.py`, `cases.py`, `controls.py`, `results.py` and `interface.py`.
6. **Your local runs, if any:** which database, its version, the read phase's result, and the reversals' results, marked "iteration, not evidence".
7. **The run of record:**
   - **If your branch is under the workflow's push filter:** the Foundation run on your last code commit, with:
     - its run ID and each job's conclusion (eight jobs);
     - the database job's duration;
     - from its log, the read phase's count and verdict, the new cases' observations, and each read control's declared signal;
     - the gate's line, `Application checks passed`.

     Push nothing more until it has finished (AM5-14).
   - **Otherwise:** say that no run started, and why.
8. **A secret scan** over your whole diff and your record.

## 5. Owned paths, push and records

- **You may change:**
  - `services/api/glow_chat/reads.py`, and the tests under `services/api/tests/` that cover it;
  - `proofs/postgres-ordering/glow_ordering_proof/read_phase.py`, its tests, and `proofs/postgres-ordering/README.md`'s read-phase lines;
  - `docs/architecture/production-contracts.md`, for item 5 only;
  - the evidence record: a new section "Stage C1-C2" after the existing sections, which stay byte-identical.
- **Nothing else.** Report any other change you think is needed, before making it.
- **Commit and push** your session branch. Don't open a pull request.
- **Your section "Stage C1-C2"** records:
  - the prompt's revision and start SHA, your head, your branch and the run of record;
  - items 1 to 5, each done (with `file:line`, its test and its reversal) or left (with the reason);
  - R2's reading of the order after the first lock;
  - the correction of C1C1-X1's claim;
  - every check with its exact results;
  - deviations and limits;
  - what the exact-head re-review must know.

## 6. Report

Your final message is the report Nathan relays. It covers:
- the prompt revision (revision 1, from `<START_SHA>`);
- the environment check (names only, the `.env` check included) and what a local database could use;
- your branch, head SHA and changed paths;
- items 1 to 5, done or left;
- every check with its exact results, and the run of record's details;
- deviations, departures you stopped at, findings outside the work with their class, and limits.

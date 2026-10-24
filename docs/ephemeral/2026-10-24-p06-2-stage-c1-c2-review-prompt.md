# P06.2 Stage C1-C2 review prompt — the exact-head re-review after C1-C2

- **Owner:** App Manager 7. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 24 October 2026.**
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 15: "C1-C1's re-review, and C1-C2", with the manager's direction during C1-C2, and "Stage C under OD-45".
- **Where the result goes:** the reviewer reports to Nathan. The manager records the re-review and its disposition in the [P06.2 evidence record](../testing/evidence/2026-10-05-p06-2-chat-integration.md), "Exact-head review of Stage C1-C2", and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 2.72 (confidence 0.79); rung probabilities low 0.00, medium 0.01, high 0.28, extra high 0.70, max 0.01, ultracode 0.00. Model probabilities Fable 5.1 0.01, Opus 5.5 0.99, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.99). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.003, Fable 5.1 at extra high 0.007, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.010, Opus 5.5 at high 0.277, Opus 5.5 at extra high 0.693, Opus 5.5 at max 0.010, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-10-24T20:12:39Z. Nathan picks the cell.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** none needed. The prompt authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Codex's code review of PR32's final head follows (OD-41).
- **Deletion condition:** prune after Stage C1's PR merges and the evidence record holds the review.

**Manager:** before giving this prompt to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **review session for P06.2 Stage C1-C2**, the second correction pass on Stage C1, in P06.2, the chat integration of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<RECORDS_COMMIT>`.

**What came before.**
- **PR32:** Stage C1 and its correction passes are the draft PR32, from the manager branch `claude/magical-wozniak-yfmmx2` into `main`. Under Nathan's D8 decision (OD-45), C1 adds:
  - the history read, the conversation list and the read-cursor command (`services/api/glow_chat/reads.py`);
  - the proof's read phase (`proofs/postgres-ordering/glow_ordering_proof/read_phase.py`);
  - the provider port's text read and the contracts.
- **C1-C1** (code `f4749ee`) made the reads' transactions durable, and added a guard before the provider call, a case and a lock-order case with a planted control.
- **C1-C1's exact-head re-review** (the evidence record, "Exact-head review of Stage C1-C1") asked for changes, in correction classes:
  - **R1:** a transaction opened by Django's `transaction.set_autocommit(False)` passed both guards. The first check's locks were held across the provider call, and a block waited on the reader.
  - **R2:** the lock-order case used only the lower member as reader.

  It also gave three nits (R3 to R5).

**What C1-C2 changed** (code commit `4a6a81a`; 5 code files, 338 lines added, 55 removed):

- **R1, with the manager's direction during the session** (an approved departure; the brief, revision 15, `09d8fe4`):
  - `_run` refuses before any statement, and before its durable block, whenever the caller has a transaction open: `_caller_transaction_open()`, which is `connection.in_atomic_block or not connection.get_autocommit()`. It returns `error`, `transaction_open`, for all three reads;
  - the check sits inside `_run`'s `try`, because reading autocommit can open the connection;
  - the durable flag stays, and so does the guard before the provider call, now on the same condition;
  - a new read-phase case, `read.autocommit_off`;
  - new offline tests.
- **R2:** `read.final_check_first_lock` runs both holds against both writers for the lower and the higher reader: eight forced waits.
- **R3:** a new case, `read.inside_test_case_block`. It now meets `_run`'s refusal first: `error`, `transaction_open`, no provider call, no transaction ID. The guard before the provider call is reached only through the offline tests.
- **R5:** a sentence in the production contracts.
- **The wording** "inside an open transaction", corrected in the README, the docstring and a case title.

The read phase now has 62 cases and three read controls.

**The run of record** is the session's push run 40127834532 on `4a6a81a`. All eight jobs passed, and the database job took 7 min 29 s.

- **You review one exact head:** `<RECORDS_COMMIT>`. Its code is byte-identical to `4a6a81a`'s.
- **The base is `d662319`,** C1-C2's start. Its code is byte-identical to `f4749ee`'s, the code C1-C1's re-review reviewed.
- **Your scope is C1-C2's change:** `git diff d662319 HEAD` over every non-Markdown path, read against the code at `HEAD`. Re-read C1's and C1-C1's code where C1-C2's changes depend on it. Read the Markdown changes for their claims.
- **The review is offline:** the code, the offline tests, a disposable database you start yourself if your sandbox allows one, and the run's logs. You call no provider.
- **What comes after this review.** Report every finding with its severity. Another correction pass comes before PR32 merges for any blocking finding. It also comes for any should-fix finding that could do any of these:
  - let a history read, the list or a cursor move succeed after a revocation committed before its final check;
  - let a safety action wait on the provider, or let a read take a lock inside a transaction its caller has open;
  - let provider text, a provider ID or any other provider field reach a DTO, a log, a stored row or a user;
  - let a forced case or a planted control pass where it should fail;
  - let the API runtime import the reads, the projections or the adapter, or connect to any database;
  - make a record claim more than the code, the tests or the runs show;
  - leave a finding sent to C1-C2, or the manager's direction, unmet.

  Everything else goes into the records. For each finding, say whether it falls in one of those classes.

**How you work:**
- Nathan started you manually and will relay your report to the manager (App Manager 7). You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - **Reversals and scratch work go in a copy outside the repository, never the checkout** (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
- **Never:**
  - dump the environment, or print a password, a marker or a connection value;
  - call Stream, or run any harness command that reaches it;
  - connect to any database other than a disposable one you start for this review (P06.DB brief, D4), and never to HDE, Railway or any other provider;
  - run `playwright install` or `eas`, or Django's `migrate` against anything but your own disposable database.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. No `PG*`, `PROOF_DB_*` or `STREAM_*` name should be set: `compgen -e | grep -E '^(PG|PROOF_DB_|STREAM_)'` prints names only.
   - If a `STREAM_*` name is present, stop and report: this session must start in `Glow App - No Stream`.
   - If another is present, report its name first, never read or use its value, and continue.
3. **The toolchain.** The pinned toolchain is in `$HOME/.local/bin`: Python 3.12.14, Node 24.19.0 and npm 11.9.0.
   - Put `$HOME/.local/bin` first on PATH in every process you run.
   - Record `command -v python3.12` and its version.
   - Create any virtual environment with `python3.12`, outside the checkout.
4. **A clean process environment.** Run each component's commands in one, as `docs/operations/local-development.md` and the READMEs show: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only that component's own variables. Installs get the proxy and CA variables by reference, never printed. Run the classification commands from the repository root.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <RECORDS_COMMIT>
git rev-parse HEAD                      # must print <RECORDS_COMMIT>
git merge-base --all origin/main HEAD   # expected: one line, 3572c41d8c401cc0c54430a9e364c2c1c58b5963
git merge-base --is-ancestor d66231987f45de013cbea8ffb90544c3356417b2 HEAD && echo "the base is an ancestor"
git merge-base --is-ancestor <RECORDS_COMMIT> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet <RECORDS_COMMIT> origin/claude/magical-wozniak-yfmmx2 -- proofs .github services scripts apps packages && echo "no code after this prompt's commit"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md | grep -c -E '^#+ Exact-head review of Stage C1-C2'   # must print 0
git diff --quiet 4a6a81a60b8c47bd569bec8d70294c0a4251cc1e HEAD -- proofs .github services scripts apps packages && echo "the code of the run of record"
git diff --quiet f4749ee71d4db470d8d470354a54e3030c73d455 d66231987f45de013cbea8ffb90544c3356417b2 -- proofs .github services scripts apps packages && echo "the base's code is the code C1-C1's re-review reviewed"
git diff --shortstat d66231987f45de013cbea8ffb90544c3356417b2 HEAD -- proofs .github services scripts apps packages   # expected: 5 files changed, 338 insertions(+), 55 deletions(-)
```

If any check fails, stop and report. The checks on `origin/claude/magical-wozniak-yfmmx2` read the live manager branch. The prompt is stale if:
- this prompt's commit is not on that branch;
- code landed after it;
- or this review is already recorded.

**Classify** with the trusted base policy outside the candidate tree and full SHAs, from the repository root:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base d66231987f45de013cbea8ffb90544c3356417b2 --head "$head" --merge-base
git diff --name-only d66231987f45de013cbea8ffb90544c3356417b2 HEAD | grep -v '\.md$' | grep -v -E '^(services/api/glow_chat/reads\.py|services/api/tests/test_chat_reads_offline\.py|proofs/postgres-ordering/glow_ordering_proof/read_phase\.py|proofs/postgres-ordering/tests/test_read_phase\.py)$'
```

- **Expected:** `"full": true`.
- **The last command must print nothing:** every non-Markdown change is in C1-C2's owned code paths. Anything else is code this review would not cover: stop and report it.

**Then read, completely, at `HEAD`:**

- root `AGENTS.md` and `CLAUDE.md`, `services/api/README.md` and `proofs/postgres-ordering/README.md`;
- the P06.2 brief, `docs/planning/p06-2-chat-integration.md`:
  - "Stage C under OD-45";
  - "C1-C1's re-review, and C1-C2", with the manager's direction during C1-C2;
- the DM-22 report's item 3.2;
- C1-C2's prompt, `docs/ephemeral/2026-10-24-p06-2-stage-c1-c2-correction-prompt.md`;
- the evidence record, `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`, whole:
  - "Exact-head review of Stage C1-C1";
  - "Stage C1-C2";
  - "Manager verification of Stage C1-C2";
- the whole of `git diff d66231987f45de013cbea8ffb90544c3356417b2 HEAD`;
- whole: `services/api/glow_chat/reads.py` and `proofs/postgres-ordering/glow_ordering_proof/read_phase.py`, with `glow_chat/contact.py` for the writers' lock order;
- the P11 plan's "The reads' limits from P06.2 Stage C1" (`docs/testing/p11-deferred-acceptance.md`).

**The run of record's logs:** run 40127834532's database job (the read phase's lines, the new cases' observations, the eight forced waits of the lock-order case, the three controls and the verdict), its API job and its gate. Read enough to confirm the counts (API 366, proof 160, reads 62/62), and say what you read.

## 3. What to review

1. **R1 and the direction.**
   - **The refusal's reach:** does `_run`'s refusal come before any statement in all three reads, so that no lock is ever taken inside a caller's transaction? Check every path through `_run` and every caller of it.
   - **The two Django modes:** is the condition right in both? That is, an atomic block (a test case's included), where autocommit is off by design, and manual mode, `set_autocommit(False)`.
   - **Inside the `try`:** is an unreachable database still an `error` result, never an exception?
   - **Any other path:** can any reach the provider call, or take a lock, with a caller's transaction open?
   - **`read.autocommit_off`:** does it show `error` with no provider call, no transaction ID assigned, and a block by the other member not held up? Does each reversal fail as the session reports?
   - **The P11 plan's corrected line** and the serving rule: are they right now?
2. **R2:** does `read.final_check_first_lock` hold the read at the final check's first lock for both readers, against both writers, both ways, with all eight waits observed?
   - **The wrong orders:** does the "reader's own account first" order now fail it?
   - **The session's reading:** is it right that the order after the first lock is not pinned, and is deadlock-free against today's writers? Check that against `contact.py`.
3. **R3:** does `read.inside_test_case_block` show `error`, `transaction_open`, no provider call and no transaction ID? Is the guard before the provider call covered by the offline tests?
4. **R5 and the wording:** the production contracts' sentence on `at`; the corrected "open transaction" wording; the session's correction of C1C1-X1.
5. **The records:** does any statement in the evidence record's "Stage C1-C2", the brief's direction or the README claim more than the code, the tests or the runs show?
6. **Nothing else changed:** `contact.py`, `delivery.py`, the provider adapters, the projections, the contracts, `reference.py` and its ten controls, and the other read cases and controls. Check that each is as C1-C1's re-review left it.
7. **The offline checks,** run at `HEAD` in a clean environment:
   - **the API:** hash-locked installs and `pip check`; `manage.py check` and its tests (366); Ruff; mypy; the static check with `makemigrations --check --dry-run`; the sealed-runtime test;
   - **the proof:** its tests (160); Ruff; mypy;
   - **the database:** if your sandbox can run a disposable database (P06.DB brief, D4), the read phase, or the whole run, and say which database and version. If it cannot, say so; the run's logs then carry the database evidence.

## 4. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<RECORDS_COMMIT>`), and the start gate's and the classification's results;
- the environment check;
- a verdict: **approve**, or **changes required**, with the findings that require them;
- every finding, numbered, with:
  - its severity (blocking, should fix, nit);
  - its file and line;
  - what is wrong, why it matters, and a suggested fix;
  - whether it falls in one of the correction classes above;
- for each focus area, what you checked and what you found;
- the offline checks you ran, with their exact results;
- limits of the review, and open questions.

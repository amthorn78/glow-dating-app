# P06.2 Stage C1-C1 review prompt — the exact-head re-review after C1-C1

- **Owner:** App Manager 7. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 24 October 2026.**
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 14: "C1's exact-head review, and C1-C1", and "Stage C under OD-45" with DM-22's conditions.
- **Where the result goes:** the reviewer reports to Nathan. The manager records the re-review and its disposition in the [P06.2 evidence record](../testing/evidence/2026-10-05-p06-2-chat-integration.md), "Exact-head review of Stage C1-C1", and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 2.68 (confidence 0.77); rung probabilities low 0.00, medium 0.01, high 0.31, extra high 0.67, max 0.01, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 1.00, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 1.00). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.010, Opus 5.5 at high 0.310, Opus 5.5 at extra high 0.670, Opus 5.5 at max 0.010, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-10-24T16:19:21Z. Nathan picks the cell.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** none needed. The prompt authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Codex's code review of PR32's final head follows (OD-41).
- **Deletion condition:** prune after Stage C1's PR merges and the evidence record holds the review.

**Manager:** before giving this prompt to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **review session for P06.2 Stage C1-C1**, the correction pass after Stage C1's exact-head review, in P06.2, the chat integration of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<RECORDS_COMMIT>`.

**What came before.**
- **PR32:** Stage C1 is the draft PR32, from the manager branch `claude/magical-wozniak-yfmmx2` into `main`. Under Nathan's D8 decision (OD-45), it adds:
  - the provider port's text read;
  - the history read, the conversation list and the read-cursor command (`services/api/glow_chat/reads.py`);
  - the proof's read phase;
  - the production contracts.
- **C1's exact-head review** (the evidence record, "Exact-head review of Stage C1") reviewed `ee3ce7e`, whose code is `91c3945`'s. It found the safety order, the checks, the text rule, the contracts and the sealed runtime holding. **Verdict: changes required,** for:
  - **finding 1** (a correction class): the reads' transactions were not durable. An enclosing transaction would hold the first check's locks across the provider call (DM-22 3.2);
  - **finding 2:** two record sentences in the production contracts.
- **The manager sent C1-C1** findings 1, 2, 5, 6, 7, 8, 9 and 10, and the session's C1-X1. Findings 3, 4, 11 and 12 went to the P11 plan.

**What C1-C1 changed** (code commit `f4749ee`; 5 code files, 473 lines added, 17 removed):

- **Finding 1:**
  - `_run` opens `transaction.atomic(durable=True)`;
  - `read_history` returns `error`, `atomic_block_open`, before the provider call when an atomic block is open;
  - a read-phase case, `read.inside_open_transaction`;
  - two offline API tests.
- **Finding 5:** a read-phase case, `read.final_check_first_lock` (`block_by_high` and `suspend_low`, both ways), and a planted control, `read.final_check_lock_order_inverted`, declared to fail by `deadlock` and `wait_not_observed`.
- **Finding 8:** `read_waits` releases the read first when it observes a wait.
- **Finding 10:** a test that ties `_lock_shared`'s reason to the projection's mapping. `chat_projections.py` is unchanged.
- **Findings 2, 6, 7 and 9, and C1-X1:** sentences in the production contracts and the data model.
- **The proof README's** read-phase paragraph and module-table row (the manager accepted the row as an interpretation).

The read phase now has 60 cases and three read controls.

**The run of record** is the session's push run 40109633125 on `f4749ee`. All eight jobs passed, and the database job took 5 min 18 s.

- **You review one exact head:** `<RECORDS_COMMIT>`. Its code is byte-identical to `f4749ee`'s.
- **The base is `95494fc`,** C1-C1's start. Its code is byte-identical to `91c3945`'s, the code C1's review reviewed.
- **Your scope is C1-C1's change:** `git diff 95494fc HEAD` over every non-Markdown path, read against the code at `HEAD`. Re-read C1's code where C1-C1's changes depend on it. Read the Markdown changes for their claims.
- **The review is offline:** the code, the offline tests, a disposable database you start yourself if your sandbox allows one, and the run's logs. You call no provider.
- **What comes after this review.** Report every finding with its severity. Another correction pass comes before PR32 merges for any blocking finding. It also comes for any should-fix finding that could do any of these:
  - let a history read, the list or a cursor move succeed after a revocation committed before its final check;
  - let a safety action wait on the provider;
  - let provider text, a provider ID or any other provider field reach a DTO, a log, a stored row or a user;
  - show a text Glow did not send;
  - let a message accepted late never reach the reader, or never count as unread;
  - let a forced case or a planted control pass where it should fail;
  - let the API runtime import the reads, the projections or the adapter, or connect to any database;
  - make a record claim more than the code, the tests or the runs show;
  - leave a DM-22 condition or a C1 review finding sent to C1-C1 unmet.

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
git merge-base --is-ancestor 95494fc0991808a03e8e1c8783516f832550a973 HEAD && echo "the base is an ancestor"
git merge-base --is-ancestor <RECORDS_COMMIT> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet <RECORDS_COMMIT> origin/claude/magical-wozniak-yfmmx2 -- proofs .github services scripts apps packages && echo "no code after this prompt's commit"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md | grep -c -E '^#+ Exact-head review of Stage C1-C1'   # must print 0
git diff --quiet f4749ee71d4db470d8d470354a54e3030c73d455 HEAD -- proofs .github services scripts apps packages && echo "the code of the run of record"
git diff --quiet 91c39457a9657cc8c4bf8b1964ec822fb6506491 95494fc0991808a03e8e1c8783516f832550a973 -- proofs .github services scripts apps packages && echo "the base's code is the code C1's review reviewed"
git diff --shortstat 95494fc0991808a03e8e1c8783516f832550a973 HEAD -- proofs .github services scripts apps packages   # expected: 5 files changed, 473 insertions(+), 17 deletions(-)
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
python3 -I "$policy_dir/change_scope.py" --base 95494fc0991808a03e8e1c8783516f832550a973 --head "$head" --merge-base
git diff --name-only 95494fc0991808a03e8e1c8783516f832550a973 HEAD | grep -v '\.md$' | grep -v -E '^(services/api/glow_chat/reads\.py|services/api/tests/test_chat_reads_offline\.py|proofs/postgres-ordering/glow_ordering_proof/read_phase\.py|proofs/postgres-ordering/tests/test_read_phase\.py)$'
```

- **Expected:** `"full": true`.
- **The last command must print nothing:** every non-Markdown change is in C1-C1's owned code paths. Anything else is code this review would not cover: stop and report it.

**Then read, completely, at `HEAD`:**

- root `AGENTS.md` and `CLAUDE.md`, `services/api/README.md` and `proofs/postgres-ordering/README.md`;
- the P06.2 brief, `docs/planning/p06-2-chat-integration.md`: "Stage C under OD-45" and "C1's exact-head review, and C1-C1";
- the DM-22 report's item 3.2;
- C1-C1's prompt, `docs/ephemeral/2026-10-24-p06-2-stage-c1-c1-correction-prompt.md`;
- the evidence record, `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`, whole:
  - "Exact-head review of Stage C1";
  - "Stage C1-C1";
  - "Manager verification of Stage C1-C1";
- the whole of `git diff 95494fc0991808a03e8e1c8783516f832550a973 HEAD`;
- whole: `services/api/glow_chat/reads.py` and `proofs/postgres-ordering/glow_ordering_proof/read_phase.py`, with `cases.py`, `results.py` and `interface.py` for how a case and a control are declared;
- the P11 plan's "The reads' limits from P06.2 Stage C1" (`docs/testing/p11-deferred-acceptance.md`).

**The run of record's logs:** run 40109633125's database job (the read phase's lines, the new cases' waits, the three controls and the verdict), its API job and its gate. Read enough to confirm the counts (API 364, proof 159, reads 60/60), and say what you read.

## 3. What to review

1. **Finding 1, the durable reads.**
   - **The durable block:** inside an open atomic block, does `_run`'s `durable=True` always give an `error` result, before any statement and never a page? Check this against the pinned Django 5.2.17.
   - **The assertion in `read_history`:** does it cover the case the durable flag lets through, a Django test case's own atomic block? Is it placed before every provider call?
   - **Every path to a provider call:** does any reach one without passing both guards?
   - **The list and the cursor move:** do they also run durable? Is the savepoint inside the cursor move still correct?
   - **`read.inside_open_transaction`:** does it show `error` with no provider call and no lock taken? Would it fail if the guard were removed?
   - **C1C1-X1:** the raw `BEGIN` limit. Is the P11 plan's line on it right?
2. **Finding 5, the final check's lock order.**
   - **`read.final_check_first_lock`:** does it hold the read at the final check's first lock against `block_by_high` and `suspend_low`, both ways, with each wait observed?
   - **The planted control:** does `read.final_check_lock_order_inverted` lock session, match, accounts, and does it fail the case by its declared signals (`deadlock`, `wait_not_observed`) in the run? Is it built from the adapter's own helpers, with no switch in the adapter?
   - **Coverage:** would a final check locking in any other wrong order also fail?
3. **Finding 8:** does `read_waits` now release the read first when a wait is observed, so a broken adapter fails by the case's own signal?
4. **Finding 10:** does the test tie the projection's mapping to `_lock_shared`'s actual reason, so that a rename fails it?
5. **The records** (findings 2, 6, 7 and 9; C1-X1):
   - **the production contracts:** the rule sentence's exception for `ReadCursorIntent`; the superseded SDK-bypass sentence; `closed`'s intended producer; `at`'s two meanings;
   - **the data model:** the `failed` binding note;
   - **the proof README:** the paragraph and the table row;
   - **the evidence record's "Stage C1-C1".**

   Does any statement claim more than the code, the tests or the runs show?
6. **Nothing else changed:** `contact.py`, `delivery.py`, the provider adapters, the projections, the contracts, `reference.py` and its ten controls, and the other read cases and controls. Check that each is as C1's review left it.
7. **The offline checks,** run at `HEAD` in a clean environment:
   - **the API:** hash-locked installs and `pip check`; `manage.py check` and its tests (364); Ruff; mypy; the static check with `makemigrations --check --dry-run`; the sealed-runtime test;
   - **the proof:** its tests (159); Ruff; mypy;
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

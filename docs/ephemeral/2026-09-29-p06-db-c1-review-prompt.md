# P06.DB-C1 review prompt — exact-head review of the correction pass

- **Owner:** App Manager 5. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 2, 4 October 2026.** Revision 1 (29 September, from `fcc4992`) never ran: the session Nathan started on 4 October from its pick had been given the C1 correction prompt instead (the evidence record, "A second run of the C1 correction prompt"; AM5-15). Revision 2 adds focus area 10, the two points that second run raised, and a start-gate check that stops a stale prompt.
- **Durable brief:** [P06.DB brief](../planning/p06-db-disposable-postgres-proof.md), revision 2, and its "Sessions".
  - Evidence: the [P06.DB evidence record](../testing/evidence/2026-09-29-p06-db-disposable-postgres-proof.md): "P06.DB-C1 corrections" (the session's own record), the manager's verification under it, and "A second run of the C1 correction prompt".
- **Where the result goes:** the manager records the verified review in the evidence record, under a new heading "Exact-head review of P06.DB-C1". The outcome goes into the brief's "Sessions" and decides whether the P11 plan's DB06 entry stands as settled.
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v6: Opus 5.5, extra high.** Effort score 2.82 (confidence 0.86); rung probabilities low 0.00, medium 0.01, high 0.18, extra high 0.80, max 0.01, ultracode 0.00. Model probabilities Fable 5.1 0.01, Opus 5.5 0.99 (confidence 0.98). Sent 2026-10-04T16:40:48Z. Nathan picks the cell.
  - Revision 1's reading, sent 2026-09-29T16:37:14Z, was the same cell (score 2.81). The pick reported for it on 4 October, Opus 5.5 at extra high, went to the second run of the C1 correction prompt, not to this review.
  - **Nathan's pick for revision 2: Opus 5.5 at extra high**, reported on 4 October. This line was added after the prompt was given; the body Nathan pasted is unchanged.
- **No Dev Manager read is needed:** the prompt authorizes no credential use and no live provider action, and the session starts no database.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and the session calls no provider.
- **It runs alone** (OD-29, the linear process). After it: a correction, if any, with its own review; then the Dev Manager's read of PR28's governing changes, Codex's review and the merge.
- **Deletion condition:** prune after P06.DB's PR merges and the evidence record holds the result.

**Manager:** before giving this prompt to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **review session for P06.DB-C1**, the correction pass on P06.DB, the early disposable-PostgreSQL proof of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 2, from commit `<RECORDS_COMMIT>`.

P06.DB built two things:

- `proofs/postgres-ordering/`, a proof package that orders message-send authorizations against every revocation of contact on a real PostgreSQL 17 database;
- the Foundation job "Database proof checks". It starts that database inside the job, on loopback, with passwords the job generates and masks, runs the proof and removes the database.

The first exact-head review, of `6f5866d`, confirmed the design, the job and its credential handling, and asked for changes, narrowly. The correction session started from `4511bbc` and fixed four findings:

- **F1, in a correction class:** the stress run read every race's rows at the same iteration number, so only the first race's overlap count was established. Each race now reads its own rows (run tag, `case_id` and iteration), and the duplicates race counts its two sends' intervals;
- **F2:** the commit-order oracle's rule O2 now flags any block or unmatch of the send's match that committed before or with the send, whatever its version;
- **F3:** a negative control counts as failed as intended only when its declared signal is present, and never beside a harness error, a database error or a stress harness failure;
- **F4:** a forced wait counts as observed only when `pg_blocking_pids` of the waiting backend names the holder's backend.

It added 42 offline tests and corrected the README and the evidence record in place. It then reran the job: Foundation run 36534514283 on the code head `4280770` is the run of record. Every job in it passed, but the run-level status reads `cancelled`. The session's records push started a second run on the same branch, and the workflow's concurrency group marked the first run cancelled after its jobs had finished. The manager accepted the job results as the run of record and recorded the label as a limit. It verified the branch and integrated it with a merge commit.

On 4 October a second session was started from the C1 correction prompt, in place of this review, and made the whole pass again on its own branch, `claude/magical-goldberg-ie0j16` (Foundation run 37209125365). The manager recorded it and did not integrate it. It is not under review, and nothing on that branch is evidence for PR28. Its report raised two points that hold for PR28's code too; they are focus area 10.

- **You review one exact head:** `ea21ac8577b83158be1f941b93dbef411bece41f`, that merge commit.
  - Its first parent, `82c3883`, is the manager branch before the merge. Its second parent, `24e716b`, is the session's head.
  - The code head is `42807705d374a4d532b1c4fb203d3f4be1cef438`, and the merge's proof package and workflow are byte-identical to it. The session's two later commits changed only the evidence record.
  - The merge brought 15 files: 14 under `proofs/postgres-ordering/` and the evidence record.
- **Your scope is C1's change:** the whole of `git diff HEAD^1 HEAD`. Read it against the package as it stands at `HEAD`, because a fix can break code it did not touch.
  - The first review covered the rest of the package at `6f5866d`. Re-read that code where a fix depends on it.
  - Later commits are Markdown-only manager records, which you read at `<RECORDS_COMMIT>`.
- **The database run is not repeated here.** You start no database. The review is offline and reads the job's log. You check that the corrected code could not produce a false pass and that each fix does what its finding needed, and you classify the two points in focus area 10.
- **What comes after this review.** Report every finding with its severity, as usual. Some findings get another correction pass before PR28 merges: any blocking finding, and any should-fix finding that could:
  - let a send authorization commit after a revocation that invalidates it without the suite failing;
  - let a password or connection value reach a log, an artifact or a file outside the job's temporary directory;
  - let the job or the proof connect to anything but its own disposable database;
  - make DB06's or DB09's mark claim more than the run shows.

  Everything else goes into the records. For each finding, say whether it falls in one of those classes.
- Nathan started you manually and will relay your report to the manager (App Manager 5). You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - Keep scratch work outside the repository, or in its ignored paths (`.venv/`, `.work/`).
- **Never:**
  - dump the environment;
  - start or connect to any database, whether a local cluster, a container, or the proof's settings pointed at anything. Never connect to Stream, HDE, Railway or any other provider;
  - run `playwright install`, `eas` or `migrate`, or the proof's `facts` and `run` commands.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. No `PG*`, `PROOF_DB_*` or `STREAM_*` name should be set: `compgen -e | grep -E '^(PG|PROOF_DB_|STREAM_)'` prints names only. If any is present, report its name first in your report, never read or use its value, and continue.
3. The pinned toolchain is in `$HOME/.local/bin`, including Python 3.12.14. Put `$HOME/.local/bin` first on PATH in every process you run the proof in, then record `command -v python3.12` and its version.
4. Run the proof's commands in a clean process environment, as its README's "Install" and "Checks (offline)" sections show. Installs get the proxy and CA variables by reference, never printed.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach ea21ac8577b83158be1f941b93dbef411bece41f
git rev-parse HEAD                      # must print ea21ac8577b83158be1f941b93dbef411bece41f
git rev-parse HEAD^2                    # must print 24e716b643b0ad0bd3f969d5c0351862a4a66321
git merge-base --all origin/main HEAD   # expected: one line, 47db18dfec3f62626f4e09f65f52c7a2e10c9e3e
git merge-base --is-ancestor HEAD <RECORDS_COMMIT> && echo "records build on the head"
git merge-base --is-ancestor <RECORDS_COMMIT> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet <RECORDS_COMMIT> origin/claude/magical-wozniak-yfmmx2 -- proofs .github services scripts apps packages && echo "no code after this prompt's commit"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-09-29-p06-db-disposable-postgres-proof.md | grep -c -E '^#+ Exact-head review of P06\.DB-C1'   # must print 0: this review is not yet recorded
git diff --stat HEAD^1 HEAD             # expected: 15 files, 1250 insertions, 122 deletions
git diff --quiet 42807705d374a4d532b1c4fb203d3f4be1cef438 HEAD -- proofs .github services scripts apps packages && echo "the code of run 36534514283"
```

If any check fails, stop and report. The three checks on `origin/claude/magical-wozniak-yfmmx2` read the live manager branch: if this prompt's commit is not on it, code landed after that commit, or this review is already recorded, the prompt is stale.

Classify three times, as root `AGENTS.md` requires. The trusted base policy runs outside the candidate tree, every run uses the same policy file, and every SHA is a full one (a short SHA fails closed):

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
python3 -I "$policy_dir/change_scope.py" --base 6f5866d505c5fd94ad9224ab9b23ba4e3bafaef5 --head "$(git rev-parse HEAD^1)" --merge-base
python3 -I "$policy_dir/change_scope.py" --base "$head" --head <RECORDS_COMMIT> --merge-base
git diff --name-only "$base" "$head" | grep -v '\.md$' | grep -v '^proofs/postgres-ordering/' | grep -v '^\.github/workflows/foundation\.yml$'
```

- **The first run** is the head against `main`. Expected: `"full": true`. The last command must print nothing: every non-Markdown change in PR28 is under `proofs/postgres-ordering/` or is the workflow. Anything else is code this review would not cover: stop and report it.
- **The second run** covers everything from the first review's head to the manager branch just before this merge. Expected: `ordinary-docs-only`, so the only code since the first review is C1's.
- **The third run** is everything after the head. Expected: `ordinary-docs-only`. Anything else means a non-Markdown change landed after the head: stop and report it.

Then read, completely.

**At `HEAD`:**

- root `AGENTS.md` and `CLAUDE.md`;
- the C1 prompt, `docs/ephemeral/2026-09-29-p06-db-c1-correction-prompt.md` (revision 1): what the session was asked to do, the requirements for each fix, its owned paths, its rules and its report format;
- the P06.DB brief, `docs/planning/p06-db-disposable-postgres-proof.md` (revision 2): "What P06.DB proves", D5, D6 with item 6, and "Sessions";
- the evidence record, `docs/testing/evidence/2026-09-29-p06-db-disposable-postgres-proof.md`:
  - "Exact-head review of P06.DB (29 September 2026)": the findings F1 to F6, each with its scenario, and the "Disposition";
  - "P06.DB-C1 corrections", the session's section, and the in-place corrections it names in "P06.DB implementation";
- `proofs/postgres-ordering/README.md` and the whole of `git diff HEAD^1 HEAD`;
- whole, the package files the diff touches and those its fixes depend on: `reference.py`, `design.py`, `budget.py` and `interface.py`;
- the `database` job of `.github/workflows/foundation.yml`, which C1 did not change.

**At `<RECORDS_COMMIT>`,** with `git show <RECORDS_COMMIT>:<path>`:

- the evidence record's "Manager verification of P06.DB-C1": its identity checks, its reversal table, the section on the run-level `cancelled` status with the manager's decision, its three observations and its dispositions;
- the evidence record's "A second run of the C1 correction prompt": its checks, the two points about PR28's code with the commit-order table, the correction to C1's local run 2 and its dispositions;
- the brief's "Sessions";
- `docs/testing/p11-deferred-acceptance.md`: "Early partial evidence", with the DB06 and DB09 entries.

## 3. What to review

The focus areas are in order of risk.

1. **F1: each race's overlap count is its own, and means contention** (`stress.py`).
   - `_intervals` selects only the race's own rows. Does any other per-iteration read still span races?
   - The per-iteration oracle check passes `case_id`. The manager's observation 1: no test fails when it is removed at its call site, and today the change is behavior-neutral. Agree or not, and say whether a test is needed.
   - `_overlapped` intersects the send against the revocation in a two-writer race, the two sends in `race.racing_duplicates`, and the send against any revocation in `race.opposing_writers`. Is an intersection of two database intervals real contention for each race kind? Or can it count by construction, through the head start, an attempt row's `clock_timestamp()` end or the sign-in rows?
   - The counts now differ between races, 174 to 200 of 200. Are they plausible for each race's construction?
   - The floors (50 iterations and 10 overlaps) and the budget are unchanged, and a race below its floor still fails the job.
2. **F2: O2 catches any send after a contact revocation** (`oracle.py`).
   - The rules moved into `judge`, and `evaluate` now calls it. Does `evaluate` still read every row it did before? Could the refactor drop a row, a rule or a tie? Ties must still count as violations.
   - The stronger rule must hold for every row the design writes, because a block or unmatch is never undone for its match in P06.DB. Is that true of `reference.py`, including unblock, a repeated unmatch and `named.unblock_no_resurrect`?
   - O6 is unchanged, and the row classes are renamed `SubmissionRow` and `RevocationRow`.
3. **F3: a control counts only by its declared signal** (`controls.py`, `cases.py`).
   - Is each control's declared signal the one its broken switch must produce?
   - Could a signal appear for another cause and let a control count falsely? Check `outcome_signal`'s mapping, the `other` signal, `DISQUALIFYING`, and that every declared case signal is required.
   - `no_version_check` declares only `refusal_missing`, because the oracle cannot see a stale client version (observation 3 of the first verification). Is that enough for DB06's version-check guarantee?
   - A control whose declared signal is absent fails the job (`results.py`, `__main__.py`).
4. **F4: a forced wait counts only when the holder blocks it** (`observe.py`; `cases.py`, `forced`).
   - Is the captured holder pid, taken through `on_begin` on the holder's connection, the backend that holds the contended lock in every forced case? Could it come from another connection or transaction?
   - The waits in the log are `transactionid`/`ShareLock`. Does "the holder is among the blockers" prove the forced interleaving, or should the holder be the only blocker?
   - The observer's loop: after a wait on another backend it keeps polling until the arriver finishes or the timeout passes. Can it time out falsely, or miss the holder's wait?
5. **No check was weakened, and the tests are real** (`tests/`).
   - Compare each changed check with the version the first review read: no case, oracle rule, control or floor may be looser.
   - The offline tests use stand-ins (`tests/fakes.py`). The filtering cursor applies the query's own conditions. Do the tests exercise the code's behavior, or restate it? The manager undid each fix in turn, and six of seven reversals were caught.
6. **The run of record** (run 36534514283; job 109295439073's log, read whole).
   - From the jobs' timestamps, confirm that every job completed with `success` before the run was marked `cancelled`. Assess the manager's decision: the job results are the run of record, and the label is recorded as a limit. Say whether you agree, and why.
   - DM-08 7.2's three checks, again:
     - no password in the log. Look for strings shaped like the generated passwords, 48 hexadecimal characters. The three `***` are the checkout and setup-python tokens;
     - each forced wait observed, now with its blocking backend;
     - the ten controls met their declared signals, and the two stress controls failed at their first failing iteration.
   - The session's section agrees with the log: its per-race counts, the controls' signals and the oracle's figures.
   - PR28's latest pull-request run on a head that contains `ea21ac8`: confirm from its jobs that "Database proof checks" ran, not skipped, and passed, and read its per-race counts.
7. **DB06 and DB09 claim no more than the runs show** (D6). The P11 plan's DB06 entry now rests on run 36534514283. Is it accurate as worded? Give your wording if it is not.
8. **Records.** This is a full-scope review: never skip a finding because its file ends in `.md`.
   - The in-place corrections in "P06.DB implementation": each is marked, and each says three things: what run 36520940933 established (the first race's 200 of 200), what it did not, and where the corrected counts are.
   - The README describes the corrected code.
   - "Manager verification of P06.DB" and "Exact-head review of P06.DB" are unchanged from `4511bbc`.
   - The manager's verification of C1 at `<RECORDS_COMMIT>`: assess its decision, observations and dispositions, and say where you disagree and why.
9. **Scope and dependencies.**
   - Only the 15 paths named changed. No dependency file, workflow, `services/`, `scripts/`, `apps/`, `packages/` or `.gitignore` path changed.
   - Every file has mode 100644, there are no symlinks, and the locks are unchanged.
10. **The two points the second run raised** (the evidence record, "A second run of the C1 correction prompt"). Classify each, with its severity and whether it falls in a correction class.
    - **Commit orders.** The stress floors count iterations and measured overlaps, not which writer committed first. In PR run 36599961669, on `fcc4992` with C1's code, the send never committed first in `race.sign_out_sender` or `race.expire_sender`; in `race.opposing_writers` it committed first at most once in any run. Check the counts in the logs of the runs the record's table lists, and read the head start in `run_race`.
      - The brief's "What P06.DB proves", item 2, "Forced and random", asks for each interleaving forced and a randomized stress run with zero violations; DB06's entry says "under forced and randomized races".
      - Given the forced cases, is a recorded limit enough? Or does the stress run need a floor on each commit order, or a different head start?
    - **One run per database.** The run tag `design:stress` is fixed (`__main__.py:75` to `77`), so `_intervals`, the per-iteration oracle check and the final oracle would read an earlier run's rows in the same database. Confirm that the job's database is new in each run. Is a recorded limit enough, or should the proof refuse a database that already holds proof rows? Assess the manager's correction to C1's local run 2.

**Out of scope:**

- running any database;
- `services/api`;
- governing Markdown (the CI policy and the manager workflow), which the Dev Manager reads;
- P06.2, and anything in HDE;
- the parts of the package C1 did not change, except where a fix depends on them or focus area 10 asks;
- the branch `claude/magical-goldberg-ie0j16`, the second run, except its run's log as focus area 10 cites it.

## 4. Checks to run

Report the exact commands and results.

1. `git diff --check HEAD^1 HEAD`.
2. The three classifications above.
3. The install from the proof's locks, with the README's commands, in a clean process: `pip install --require-hashes -r requirements-dev.lock` and `pip check`.
4. The offline checks, with the README's commands:
   - the unit tests under `env -i` (the session reported 82);
   - `ruff check .`, `ruff format --check .` and mypy;
   - `services/api`'s `python3.12 -m unittest tests.test_toolchain_pins`.
5. A secret scan over the whole of `git diff HEAD^1 HEAD`: no secret, token, password, connection string or email address. Confirm that each long hexadecimal string is a commit SHA or the image digest.
6. Hosted CI, as focus area 6 says.
7. Anything else you judge necessary, offline only. You may write throwaway tests or scripts outside the repository that exercise the package without a database, such as undoing a fix to see its test fail, or the oracle's rules against constructed rows. Nothing may open a connection.

## 5. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 2, from commit `<RECORDS_COMMIT>`);
- the environment check's result (names only);
- the head you reviewed (`git rev-parse HEAD`) and the three classification outputs;
- **verdict:** "approve" (C1's corrections, the run of record and the records are sound, and PR28 can go on to the Dev Manager's read and the merge) or "changes required";
- **findings,** most severe first. For each: severity (**blocking**, **should fix** or **nit**), `file:line`, the concrete failure scenario, a suggested fix, and whether it falls in one of the classes that need a correction before PR28 merges;
- DM-08 7.2's three checks from the log, each confirmed or not;
- the manager's decision on the run of record: agree or not, with the reason;
- for each of the manager's observations and dispositions in its verification of C1: agree, or disagree with the reason;
- the DB06 and DB09 entries: accurate as worded, or your wording;
- focus area 10's two points, each with its severity and class, and your view of the correction to C1's local run 2;
- PR28's latest pull-request run: the result of "Database proof checks" and its per-race counts;
- the areas you reviewed with no findings;
- every check you ran, with its exact result;
- limits: anything you could not check, and why.

Skipped or unavailable checks are not passes. Change nothing in the repository, on GitHub or in Notion.

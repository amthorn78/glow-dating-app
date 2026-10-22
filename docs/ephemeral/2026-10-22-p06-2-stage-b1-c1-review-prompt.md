# P06.2 Stage B1-C1 review prompt — exact-head review of the corrected head

- **Owner:** App Manager 6. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 22 October 2026.**
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 3, and its "Sessions"; the [B1-C1 prompt](2026-10-06-p06-2-stage-b1-c1-correction-prompt.md), revision 1.
- **Where the result goes:** the reviewer reports to Nathan; the manager records the review and its disposition in the [P06.2 evidence record](../testing/evidence/2026-10-05-p06-2-chat-integration.md), "Exact-head review of Stage B1-C1", and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.44 (confidence 0.63); rung probabilities low 0.00, medium 0.06, high 0.44, extra high 0.50, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 1.00, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 1.00). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.060, Opus 5.5 at high 0.440, Opus 5.5 at extra high 0.500, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Flags: boundary between high and extra high. Sent 2026-10-22T13:39:45Z. Nathan picks the cell.
  - **The scorer's version:** the `typesafe-scoring` skill now sends request v8.2 (four models); the earlier P06.2 readings were v6. The manager workflow's step 3 still names v6 (a recorded follow-up).
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** none needed; the prompt authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29).
- **Deletion condition:** prune after Stage B1's PR merges and the evidence record holds the review.

**Manager:** before giving this prompt to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **review session for P06.2 Stage B1-C1**, the correction pass on Stage B1 of P06.2, the chat integration of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<RECORDS_COMMIT>`.

**What came before.** Stage B1 (code head `cab71b9`, integrated at `e614d8a`) made the eight changes Stage A's reviews carried to Stage B: provisioning before the channel by a database-assigned outbox order key, a reconciliation mark, the grant's transaction, activation's checks, three nits, and new race-suite cases. Its exact-head review of `e614d8a` approved it with one should-fix finding, R1 (a test the Dev Manager's DM-15 condition 3.5 requires was missing), and four nits, R2 to R5. Because R1 is a Dev Manager condition, it was corrected before the merge, with the nits: the evidence record, "Exact-head review of Stage B1".

**What B1-C1 changed** (7 code paths, +420 −46):

- **R1:** a delivery-phase case, "a second match for an already-provisioned account" (`delivery_phase.py`);
- **R2:** the grant signals `before_commit` once (`contact.py`);
- **R3:** four dead-letter branches in `delivery.py` now mark their row; four others with no row to mark are left, with the reason;
- **R4:** one sentence in B1's record;
- **R5:** the token cases' app clock 2 minutes ahead instead of an hour, and a new case `token.sequential_grant_first_long_skew` keeping the hour (`cases.py`).

**The run of record** is the session's push run 37465172088 on `2c91fbb`: all eight jobs passed, and the gate printed `Application checks passed`. Its database job is job 112274335803.

- **You review one exact head:** `b1ffb45ab5e61292c4a29ac02c89fe69287584b9`, the merge that integrated B1-C1.
  - Its first parent, `37ce600`, is the manager branch before the merge, which holds B1 (reviewed at `e614d8a`) and records only since. Its second parent, `c562867`, is the session's head. The code head is `2c91fbbcc6ff386540428419aca6da047dceabaa`, and the merge's code is byte-identical to it.
- **Your scope is B1-C1's change:** the whole of `git diff HEAD^1 HEAD`, read against the code at `HEAD`. B1's code was reviewed at `e614d8a`; re-read it where C1's changes depend on it. Later commits are Markdown-only records, which you read at `<RECORDS_COMMIT>`.
- **The database run is not repeated here.** You start no database. The review is offline: the code, the offline tests, and the run of record's logs.
- **What comes after this review.** Report every finding with its severity. A correction pass comes before Stage B1 merges for any blocking finding, and for any should-fix finding that could:
  - let a send authorization, an activation or a grant commit after a revocation that invalidates it without the suite failing;
  - let a channel be created before both members are provisioned, or a revocation be recorded without its provider call;
  - let a password, the marker or a connection value reach a log, an artifact or a file outside the job's temporary directory;
  - let the job, the proof or the adapter connect to anything but its own disposable database, or let the API runtime load the adapter or connect to any database;
  - make DB06's or DB09's mark claim more than the run shows;
  - leave a DM-15 condition unmet.

  Everything else goes into the records. For each finding, say whether it falls in one of those classes.
- Nathan started you manually and will relay your report to the manager (App Manager 6). You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - **Reversals and scratch work in a copy outside the repository, never the checkout** (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
- **Never:**
  - dump the environment;
  - start or connect to any database, and never set a database's comment. Never connect to Stream, HDE, Railway or any other provider;
  - run `playwright install` or `eas`;
  - run `migrate` or the proof's `facts` and `run` commands yourself. The offline tests run commands only through `tests/command_harness.py`, whose fake server opens no connection; running the tests is allowed.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. No `PG*`, `PROOF_DB_*` or `STREAM_*` name should be set: `compgen -e | grep -E '^(PG|PROOF_DB_|STREAM_)'` prints names only. If a `STREAM_*` name is present, stop and report: this session must start in `Glow App - No Stream`. If another is present, report its name first, never read or use its value, and continue.
3. The pinned toolchain is in `$HOME/.local/bin`, including Python 3.12.14. Put `$HOME/.local/bin` first on PATH in every process you run, then record `command -v python3.12` and its version. Create any virtual environment with `python3.12`.
4. Run the API's and the proof's commands in a clean process environment, as `docs/operations/local-development.md` and the proof's README show. Installs get the proxy and CA variables by reference, never printed.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach b1ffb45ab5e61292c4a29ac02c89fe69287584b9
git rev-parse HEAD                      # must print b1ffb45ab5e61292c4a29ac02c89fe69287584b9
git rev-parse HEAD^2                    # must print c562867b1de1598f005be773e392c059326a7671
git merge-base --all origin/main HEAD   # expected: one line, 02072f4dcb0c20dd45dee9bc02e75323d0a2aec7
git merge-base --is-ancestor HEAD <RECORDS_COMMIT> && echo "records build on the head"
git merge-base --is-ancestor <RECORDS_COMMIT> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet <RECORDS_COMMIT> origin/claude/magical-wozniak-yfmmx2 -- proofs .github services scripts apps packages && echo "no code after this prompt's commit"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md | grep -c -E '^#+ Exact-head review of Stage B1-C1'   # must print 0: this review is not yet recorded
git diff --shortstat HEAD^1 HEAD        # expected: 8 files changed, 533 insertions(+), 47 deletions(-)
git diff --quiet 2c91fbbcc6ff386540428419aca6da047dceabaa HEAD -- proofs .github services scripts apps packages && echo "the code of the run of record"
git diff --quiet e614d8a12c39884045023dbb71c615ea40899674 HEAD^1 -- proofs .github services scripts apps packages && echo "the first parent's code is B1's reviewed code"
```

If any check fails, stop and report. The three checks on `origin/claude/magical-wozniak-yfmmx2` read the live manager branch: if this prompt's commit is not on it, if code landed after that commit, or if this review is already recorded, the prompt is stale.

Classify, as root `AGENTS.md` requires, with the trusted base policy outside the candidate tree and full SHAs:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$(git rev-parse HEAD^1)" --head "$head" --merge-base
python3 -I "$policy_dir/change_scope.py" --base "$head" --head <RECORDS_COMMIT> --merge-base
git diff --name-only HEAD^1 HEAD | grep -v '\.md$' | grep -v -E '^(services/api/glow_chat/|services/api/tests/|proofs/postgres-ordering/)'
```

- **The first run** is C1's change. Expected: `"full": true`. The last command must print nothing: every non-Markdown change is under `services/api/glow_chat/`, `services/api/tests/` or `proofs/postgres-ordering/`. Anything else is code this review would not cover: stop and report it.
- **The second run** is everything after the head. Expected: `ordinary-docs-only`.

Then read, completely.

**At `HEAD`:**

- root `AGENTS.md` and `CLAUDE.md`, `services/api/README.md` and `proofs/postgres-ordering/README.md`;
- the P06.2 brief, `docs/planning/p06-2-chat-integration.md`, "B1's design points";
- the B1-C1 prompt, `docs/ephemeral/2026-10-06-p06-2-stage-b1-c1-correction-prompt.md`;
- the DM-15 report, `docs/continuity/dev-manager/reviews/2026-10-06-dm-15-p06-2-stage-b-split-read.md`, items 3 and 4;
- the evidence record: "Exact-head review of Stage B1" and "Stage B1-C1", whole;
- the whole of `git diff HEAD^1 HEAD`, and, whole, `services/api/glow_chat/delivery.py` and `contact.py`'s `grant_token`.

**At `<RECORDS_COMMIT>`:** the evidence record's "Manager verification of Stage B1-C1" (its five points for this review), and the brief's "Sessions".

**The run of record's logs:** the database job 112274335803, whole, and the gate's log line.

## 3. What to review

1. **R1, the second match** (DM-15 3.5). Does the case meet the condition as written: exactly one `identity_created` for the provisioned account over both activations, the second activation provisioning only the newcomer, the new channel's delivery preceded only by the newcomer's provisioning and succeeding? The manager's point 4: does it read the second activation's transaction, and no other, through the shared `xmin`? Does its reversal fail it for the right reason?
2. **R3, the marks.** For each of the four branches now marked: is marking that row right, and is the mark a Glow code? The manager's point 1: two branches mark a binding or identity under another provider's name; is that the right row to mark? For the four branches left: is there truly no row? Does any reachable path now mark a row that should stay clean, or stop a call that should be made? The offline test and the delivery case: does each reach the branch it names?
3. **R2, the single signal.** Granted paths signal once. The manager's point 2: a refused grant now signals no `before_commit`; does any case hold or count it there?
4. **R5, the skew.** With a 2-minute app clock, does the reversal now fail on the issue-time comparison, as the report says? Does `token.sequential_grant_first_long_skew` add what the report claims? The manager's point 3: is the judge's verdict logic unchanged apart from the note it prints?
5. **R4 and the records.** The one changed sentence in "Stage B1", and the session's "Stage B1-C1" section: does any statement claim more than the code and the log show? Check the figures against the log.
6. **Nothing else changed:** `reference.py`, the models, migrations `0001` to `0003`, the harness, the workflow and every dependency file are unchanged against `HEAD^1`.
7. **The log.** From job 112274335803: the new cases with their results; 115 adapter cases and 56 reference cases, each held case with its holder; the controls; the oracle's figures; the delivery phase's 13 checks; the refusals; the container's removal; no password or marker (say what each `***` is). The manager's point 5: per race and for the drain, compare the times with B1's run of record (37410705342, database job 112098441694); does anything C1 adds explain the suite step taking 11½ minutes against 5?
8. **The manager's five points** in "Manager verification of Stage B1-C1": agree or not with each.

## 4. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<RECORDS_COMMIT>`), the start gate's and the classifications' results;
- the environment check;
- a verdict: **approve**, or **changes required**, with the findings that require them;
- every finding, numbered, with its severity (blocking, should fix, nit), its file and line, what is wrong, why it matters, a suggested fix, and whether it falls in one of the correction classes above;
- for each focus area, what you checked and what you found;
- the offline checks you ran, with their exact results;
- limits of the review, and open questions.

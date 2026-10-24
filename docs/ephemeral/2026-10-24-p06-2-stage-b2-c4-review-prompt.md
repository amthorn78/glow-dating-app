# P06.2 Stage B2-C4 review prompt — the exact-head re-review of the correction pass

- **Owner:** App Manager 7. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 24 October 2026.**
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 10, "B2's exact-head review, and B2-C4"; the [B2-C4 prompt](2026-10-24-p06-2-stage-b2-c4-correction-prompt.md), revision 1.
- **Where the result goes:** the reviewer reports to Nathan. The manager records the review and its disposition in the [P06.2 evidence record](../testing/evidence/2026-10-05-p06-2-chat-integration.md), "Exact-head review of Stage B2-C4", and in the brief's "Sessions". Codex's code review of the final head follows (OD-41).
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 1.97 (confidence 0.88); rung probabilities low 0.00, medium 0.11, high 0.82, extra high 0.07, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.99, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.99). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.109, Opus 5.5 at high 0.812, Opus 5.5 at extra high 0.069, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.001, Sonnet 5.5 at high 0.008, Sonnet 5.5 at extra high 0.001, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-10-24T01:44:33Z. Nathan picks the cell.
  - **Nathan's pick:** Opus 5.5 at high, TypeSafe's reading (24 October).
- **The Dev Manager's read:** none needed. The prompt authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29).
- **Deletion condition:** prune after Stage B2's PR merges and the evidence record holds the review.

**Manager:** before giving this prompt to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **review session for P06.2 Stage B2-C4**, the correction pass after Stage B2's exact-head review, in P06.2, the chat integration of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<RECORDS_COMMIT>`.

**What came before.**
- **PR31:** Stage B2 and its correction passes B2-C1 to B2-C3 are the draft PR31, from the manager branch `claude/magical-wozniak-yfmmx2` into `main`. Together they add:
  - the Stream adapter, `services/api/glow_domain/chat_provider_stream.py`;
  - the client token's signer;
  - the harness's `conformance` command, with 46 rows, in `proofs/stream-chat/glow_stream_proof/conformance.py`.
- **The live rows:** B2-C3 ran the 46 rows live on 23 October.
- **The Dev Manager's conditions (DM-20).** Rows C4, M5, D10 and V13 shared one identifier, and M5's accepted send left that user at Stream. So D10 and V13 did not exercise "a user Stream does not have" live.
  - **1.2:** the rows get distinct identifiers.
  - **1.3:** M5 becomes a recorded row.
- **The exact-head review of B2 to B2-C3,** at `51844a5`, approved, with one should-fix finding (B2R1) and eight nits (the evidence record, "Exact-head review of Stage B2"). The manager sent B2R1 to B2R4 and B2R7 to B2-C4 with DM-20 1.2 and 1.3.

**What B2-C4 changed** (code commit `42e6231`; 5 code and test files, plus 2 READMEs):

- **DM-20 1.2:** the keys `U5` (C4), `U6` (M5), `U7` (D10) and `U8` (V13); `U9` is retired. C4's, D10's and V13's users go through `_id` only.
- **DM-20 1.3 with B2R3:** M5 is `recorded=True`, and its sender goes through `_new_user("U6")`, so it is reserved in the ledger and recorded as a run user. `checks/run_plan.py` measures 5 users, and 10 with the reserve.
- **B2R1:** `_guarded` and `send_message` raise the mapped error after the `except` block, so that neither its `__cause__` nor its `__context__` holds the SDK's error.
- **B2R2:** `results()` replaces every identifier of the run with `{key}`, at any depth (`_without_ids`).
- **B2R4:** a docstring sentence and a test: a short non-2xx body raises the SDK's own `KeyError`, unmapped.
- **B2R7:** the API README's development-lock command names the harness's lock as a constraint.
- **The session's finding outside the work, B2C4-X1:** cleanup's poll listing now also lists as M5's sender. It could report a false "not verified" (exit 4) if that user was never created and Stream refused the listing.
- **Its limit, B2C4-X2:** `cmd_conformance`'s `stop_reason` and console lines are not generalized.
- **The manager carried both to P11's plan,** for the harness's next live run (the evidence record, "Manager verification of Stage B2-C4").

**The run of record** is the session's push run 40049721647 on `42e6231`: all eight jobs passed, and the gate printed `Application checks passed`.

- **You review one exact head:** `da3c0ff65ffb25e5ea4f7562a7f819ff006d648d`, the merge that integrated B2-C4.
  - Its first parent, `abf2c9b`, is the manager branch before the merge. Its code is byte-identical to `51844a5`'s, the head the B2 review approved.
  - Its second parent, `0fdc54d`, is the session's head. The merge's code is byte-identical to `42e6231`'s.
- **Your scope is B2-C4's change:** the whole of `git diff HEAD^1 HEAD`, read against the code at `HEAD`. B2's code was reviewed at `51844a5`; re-read it where B2-C4's changes depend on it. Later commits are Markdown-only records, which you read at `<RECORDS_COMMIT>`.
- **The review is offline:** the code, the offline tests, and the run's logs. You start no database and call no provider.
- **What comes after this review.** Report every finding with its severity. Another correction pass comes before PR31 merges for any blocking finding, and for any should-fix finding that could:
  - let a credential, token, signature or other secret reach a log line, a record, a test recording, an artifact or a file outside git-ignored working directories;
  - let a request reach Stream outside the harness's guard, or let a command change the configuration beyond its planned scopes;
  - let the API runtime import the adapter, the SDK or `pyjwt`, or load a Stream credential;
  - let a provider write undo a removal, a deactivation or a revocation, lower a held cut-off, or add a member to a channel Stream already has;
  - let provider text, or a provider field other than an identifier, reach a Glow code or a user;
  - make a record claim more than the code, the tests or the runs show;
  - leave a DM-16 to DM-20 condition unmet.

  Everything else goes into the records. For each finding, say whether it falls in one of those classes.
- Nathan started you manually and will relay your report to the manager (App Manager 7). You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - **Reversals and scratch work in a copy outside the repository, never the checkout** (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
- **Never:**
  - dump the environment;
  - call Stream, or run any harness command that reaches it (`baseline`, `full-view`, `configure`, `restore`, `verify-clean`, `cleanup`, `run`, `conformance`). The harness's offline tests use fakes and are allowed;
  - start or connect to any database; connect to HDE, Railway or any other provider;
  - run `playwright install`, `eas` or `migrate`.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. No `PG*`, `PROOF_DB_*` or `STREAM_*` name should be set: `compgen -e | grep -E '^(PG|PROOF_DB_|STREAM_)'` prints names only.
   - If a `STREAM_*` name is present, stop and report: this session must start in `Glow App - No Stream`.
   - If another is present, report its name first, never read or use its value, and continue.
3. The pinned toolchain is in `$HOME/.local/bin`, including Python 3.12.14, Node 24.19.0 and npm 11.9.0. Put `$HOME/.local/bin` first on PATH in every process you run, then record `command -v python3.12` and its version. Create any virtual environment with `python3.12`, outside the checkout.
4. Run the API's and the harness's commands in a clean process environment (`env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus `GLOW_ENV=test` for the API), as `docs/operations/local-development.md` and the READMEs show. Installs get the proxy and CA variables by reference, never printed.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach da3c0ff65ffb25e5ea4f7562a7f819ff006d648d
git rev-parse HEAD                      # must print da3c0ff65ffb25e5ea4f7562a7f819ff006d648d
git rev-parse HEAD^2                    # must print 0fdc54d4b1a87991da1595760cefe80259051ed1
git merge-base --all origin/main HEAD   # expected: one line, 3272eed3d6b07d3215c6c667000082b6254eea69
git merge-base --is-ancestor HEAD <RECORDS_COMMIT> && echo "records build on the head"
git merge-base --is-ancestor <RECORDS_COMMIT> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet <RECORDS_COMMIT> origin/claude/magical-wozniak-yfmmx2 -- proofs .github services scripts apps packages && echo "no code after this prompt's commit"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md | grep -c -E '^#+ Exact-head review of Stage B2-C4'   # must print 0: this review is not yet recorded
git diff --shortstat HEAD^1 HEAD -- proofs .github services scripts apps packages   # expected: 7 files changed, 371 insertions(+), 35 deletions(-)
git diff --quiet 42e623197cb341a3e4188a5fba918639c133ae4b HEAD -- proofs .github services scripts apps packages && echo "the code of the run of record"
git diff --quiet 51844a5bd9a5f38ca31b5b4e39e4cb6d4f41aca8 HEAD^1 -- proofs .github services scripts apps packages && echo "the first parent's code is B2's reviewed code"
```

If any check fails, stop and report. The three checks on `origin/claude/magical-wozniak-yfmmx2` read the live manager branch. The prompt is stale if this prompt's commit is not on it, if code landed after that commit, or if this review is already recorded.

Classify, as root `AGENTS.md` requires, with the trusted base policy outside the candidate tree and full SHAs:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$(git rev-parse HEAD^1)" --head "$head" --merge-base
python3 -I "$policy_dir/change_scope.py" --base "$head" --head <RECORDS_COMMIT> --merge-base
git diff --name-only HEAD^1 HEAD | grep -v '\.md$' | grep -v -E '^(services/api/glow_domain/chat_provider_stream\.py|services/api/tests/test_chat_provider_stream\.py|proofs/stream-chat/glow_stream_proof/conformance\.py|proofs/stream-chat/tests/)'
```

- **The first run** classifies B2-C4's change. Expected: `"full": true`. The last command must print nothing: every non-Markdown change is in B2-C4's owned code paths. Anything else is code this review would not cover: stop and report it.
- **The second run** classifies everything after the head. Expected: `ordinary-docs-only`.

Then read, completely.

**At `HEAD`:**

- root `AGENTS.md` and `CLAUDE.md`, `services/api/README.md` and `proofs/stream-chat/README.md`;
- the P06.2 brief, `docs/planning/p06-2-chat-integration.md`:
  - "B2's design points";
  - point i of "B2's live rows, and what they leave";
  - "B2's exact-head review, and B2-C4";
- the B2-C4 prompt, `docs/ephemeral/2026-10-24-p06-2-stage-b2-c4-correction-prompt.md`;
- the DM-16 report's items 4.1, 4.4, 4.7 and 5.2, and the DM-20 report's items 1 and 3, in `docs/continuity/dev-manager/reviews/`;
- the evidence record: "Exact-head review of Stage B2" and "Stage B2-C4", whole;
- the whole of `git diff HEAD^1 HEAD`;
- whole: `services/api/glow_domain/chat_provider_stream.py` and `proofs/stream-chat/glow_stream_proof/conformance.py`;
- in `proofs/stream-chat/glow_stream_proof/proof_run.py`: `_generic`, `results`, `cleanup`, `_verify_polls` and `_delete_users`;
- `cmd_conformance` in `cli.py`.

**At `<RECORDS_COMMIT>`:** the evidence record's "Manager verification of Stage B2-C4", the P11 plan's bullet on the harness's next live conformance run (`docs/testing/p11-deferred-acceptance.md`), and the brief's "Sessions".

**The run of record's logs:** run 40049721647's API checks job, Stream proof checks job and gate. Read enough to confirm the test counts and `run plan: fits`; say what you read.

## 3. What to review

1. **B2R1, the exception context.**
   - **The main question:** can any part of a mapped Glow error, or its traceback, reach the SDK's error or Stream's text? That includes `__cause__`, `__context__`, its attributes, and the locals of its traceback's frames.
   - Is `send_message`'s move of the success path into `else` behaviour-preserving?
   - Do the tests assert the property for every operation and both hooks, and does the reversal fail them for the right reason?
   - Is the docstring's caveat right: when the caller is itself handling an exception, Python sets `__context__` to the caller's exception, never the SDK's?
2. **DM-20 1.2 and 1.3, with B2R3.**
   - Do C4, D10 and V13 now name users the run never creates, each its own?
   - Is M5 RECORDED whatever Stream answers, with the fixture's expectation kept?
   - Is M5's sender reserved and recorded before the send?
   - Are the blocking rows still C4, R8, D10 and V13?
   - Is any other row's identifier, verdict or order changed?
   - Does each test fail without its change?
   - Does `run_plan`'s measured count (5 users, 10 with the reserve, 95 calls) follow from the code?
3. **B2R2, the results' identifiers.**
   - Does `_without_ids` reach every part of the results that is written to a record?
   - Can it alter anything but an identifier, for example a key that is a prefix of another, or a structure it rebuilds?
   - Does running it before `_generic` and the redactor change what either does?
   - Is the test's search for the 32 hexadecimal characters strong enough?
4. **B2R4 and B2R7:**
   - the docstring sentence and its test against the SDK's behaviour;
   - the README's command and sentence against B2-C1's record of how the lock was made.
5. **B2C4-X1 and B2C4-X2, and the manager's disposition.**
   - Is the session's analysis of `_verify_polls` right?
   - Does M5's new reservation change anything else in cleanup, `verify-clean` or the guard?
   - Is carrying both to the harness's next live run (P11) right, or should either be fixed in PR31? Give the reason.
6. **Nothing else changed.** The signer, `delivery.py`, the guard, the deny-lists, the budget's caps, cleanup's rules, `proof_run.py`, the baselines, the workflow and every dependency and lock file are unchanged against `HEAD^1`.
7. **The records.** Does any statement in "Stage B2-C4" or "Manager verification of Stage B2-C4" claim more than the code, the tests or the run show?
8. **The offline checks,** run at `HEAD` in a clean environment:
   - the API: hash-locked installs and `pip check`; `manage.py check` and its tests (331); Ruff; mypy; the static check with `makemigrations --check --dry-run`; the sealed-runtime and pin tests;
   - the harness: hash-locked install and `pip check`; its tests (646); Ruff; mypy; `node --check` on its client files; `checks/run_plan.py`.

## 4. Report

Your final message is the report Nathan relays. It covers:
- the prompt revision you received (revision 1, from commit `<RECORDS_COMMIT>`), the start gate's and the classifications' results;
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

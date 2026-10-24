# P06.2 Stage B2-C5 review prompt — the exact-head re-review of the second correction pass

- **Owner:** App Manager 7. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 24 October 2026.**
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 11, "B2-C4's re-review, and B2-C5"; the [B2-C5 prompt](2026-10-24-p06-2-stage-b2-c5-correction-prompt.md), revision 1.
- **Where the result goes:** the reviewer reports to Nathan. The manager records the review and its disposition in the [P06.2 evidence record](../testing/evidence/2026-10-05-p06-2-chat-integration.md), "Exact-head review of Stage B2-C5", and in the brief's "Sessions". Codex's code review of the final head follows (OD-41).
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 1.89 (confidence 0.85); rung probabilities low 0.00, medium 0.17, high 0.78, extra high 0.05, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.99, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.99). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.168, Opus 5.5 at high 0.772, Opus 5.5 at extra high 0.050, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.002, Sonnet 5.5 at high 0.008, Sonnet 5.5 at extra high 0.001, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-10-24T02:42:39Z. Nathan picks the cell.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** none needed. The prompt authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29).
- **Deletion condition:** prune after Stage B2's PR merges and the evidence record holds the review.

**Manager:** before giving this prompt to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **review session for P06.2 Stage B2-C5**, the second correction pass after Stage B2's exact-head review, in P06.2, the chat integration of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<RECORDS_COMMIT>`.

**What came before.**
- **PR31:** Stage B2 and its correction passes B2-C1 to B2-C4 are the draft PR31, from the manager branch `claude/magical-wozniak-yfmmx2` into `main`. Together they add:
  - the Stream adapter, `services/api/glow_domain/chat_provider_stream.py`;
  - the client token's signer;
  - the harness's `conformance` command, with 46 rows, in `proofs/stream-chat/glow_stream_proof/conformance.py`.
- **B2-C4** (code commit `42e6231`, merged at `da3c0ff`) applied the Dev Manager's conditions DM-20 1.2 and 1.3 and the B2 review's findings. Among them, it added `_without_ids`, which replaces every identifier of the run with `{key}` in the conformance results.
- **B2-C4's exact-head re-review** (the evidence record, "Exact-head review of Stage B2-C4") found everything else correct, with two findings:
  - **C4R1** (should fix, the record-claim class): `_without_ids` matched each identifier only in full. Strings that `proof_run._generic` had already rewritten held `{prefix}<32 hex>` and kept their random part. Those include the connect, read and client notes, checks, async errors and deferred stops.
  - **C4R2** (nit): a boundary test's write case did not assert that its refusal reached the write.
- **The manager added `cmd_conformance`'s `stop_reason`**, which was written to the results after only the redactor.

**What B2-C5 changed** (code commit `a1e92eb`; 5 files, +172 −16):

- **C4R1:** `_without_ids` also replaces the form `_generic` leaves: `{prefix}` plus each identifier's part after the run's prefix, sorted with the whole identifiers, longest first.
- **`stop_reason`:** `cmd_conformance` passes it through `run._without_ids` in the early and the final results.
  - The console lines are unchanged, including the closing line, which prints the raw `stop_reason`. They stay carried to P11.
- **C4R2:** the write case asserts the recording's growth and the last request's method and path.
- **The claims:** the module docstring, `_without_ids`' docstring and the harness README state what the code does.
- **The tests:** two new harness tests, one strengthened API test, and reversals for each.

**The run of record** is the session's push run 40054102314 on `a1e92eb`: all eight jobs passed, and the gate printed `Application checks passed`.

- **You review one exact head:** `93caa4b7815fb351584b2db43b7fd229c31c14e7`, the session's records commit, to which the manager branch was fast-forwarded.
  - Its parent is the code commit `a1e92eb`. Its code is byte-identical to `a1e92eb`'s.
  - The base, `4c70db8`, is the manager branch before B2-C5. Its code is byte-identical to `da3c0ff`'s, the head B2-C4's re-review reviewed.
- **Your scope is B2-C5's change:** the whole of `git diff 4c70db890b476f63ce96ff5e18fe3ea5fbea777a HEAD`, read against the code at `HEAD`. Re-read B2-C4's code where B2-C5's changes depend on it. Later commits are Markdown-only records, which you read at `<RECORDS_COMMIT>`.
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
3. The pinned toolchain is in `$HOME/.local/bin`, including Python 3.12.14, Node 24.19.0 and npm 11.9.0. Put `$HOME/.local/bin` first on PATH in every process you run, then record `command -v python3.12` and its version. Create any virtual environment with `python3.12`, outside the checkout. The harness's tests need its client's `node_modules`: run `npm ci --ignore-scripts` in `proofs/stream-chat` (the directory is git-ignored).
4. Run the API's and the harness's commands in a clean process environment (`env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus `GLOW_ENV=test` for the API), as `docs/operations/local-development.md` and the READMEs show. Installs get the proxy and CA variables by reference, never printed. Run the classification commands from the repository root.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach 93caa4b7815fb351584b2db43b7fd229c31c14e7
git rev-parse HEAD                      # must print 93caa4b7815fb351584b2db43b7fd229c31c14e7
git merge-base --all origin/main HEAD   # expected: one line, 3272eed3d6b07d3215c6c667000082b6254eea69
git merge-base --is-ancestor 4c70db890b476f63ce96ff5e18fe3ea5fbea777a HEAD && echo "the base is an ancestor"
git merge-base --is-ancestor HEAD <RECORDS_COMMIT> && echo "records build on the head"
git merge-base --is-ancestor <RECORDS_COMMIT> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet <RECORDS_COMMIT> origin/claude/magical-wozniak-yfmmx2 -- proofs .github services scripts apps packages && echo "no code after this prompt's commit"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md | grep -c -E '^#+ Exact-head review of Stage B2-C5'   # must print 0: this review is not yet recorded
git diff --shortstat 4c70db890b476f63ce96ff5e18fe3ea5fbea777a HEAD -- proofs .github services scripts apps packages   # expected: 5 files changed, 172 insertions(+), 16 deletions(-)
git diff --quiet a1e92eb0d42b183dd33a7991deef30abf8d6e5fc HEAD -- proofs .github services scripts apps packages && echo "the code of the run of record"
git diff --quiet da3c0ff65ffb25e5ea4f7562a7f819ff006d648d 4c70db890b476f63ce96ff5e18fe3ea5fbea777a -- proofs .github services scripts apps packages && echo "the base's code is the code B2-C4's re-review reviewed"
```

If any check fails, stop and report. The three checks on `origin/claude/magical-wozniak-yfmmx2` read the live manager branch. The prompt is stale if this prompt's commit is not on it, if code landed after that commit, or if this review is already recorded.

Classify, as root `AGENTS.md` requires, with the trusted base policy outside the candidate tree and full SHAs, from the repository root:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base 4c70db890b476f63ce96ff5e18fe3ea5fbea777a --head "$head" --merge-base
python3 -I "$policy_dir/change_scope.py" --base "$head" --head <RECORDS_COMMIT> --merge-base
git diff --name-only 4c70db890b476f63ce96ff5e18fe3ea5fbea777a HEAD | grep -v '\.md$' | grep -v -E '^(proofs/stream-chat/glow_stream_proof/conformance\.py|proofs/stream-chat/glow_stream_proof/cli\.py|proofs/stream-chat/tests/|services/api/tests/test_chat_provider_stream\.py)'
```

- **The first run** classifies B2-C5's change. Expected: `"full": true`. The last command must print nothing: every non-Markdown change is in B2-C5's owned code paths. Anything else is code this review would not cover: stop and report it.
- **The second run** classifies everything after the head. Expected: `ordinary-docs-only`.

Then read, completely.

**At `HEAD`:**

- root `AGENTS.md` and `CLAUDE.md`, and `proofs/stream-chat/README.md`;
- the P06.2 brief, `docs/planning/p06-2-chat-integration.md`: "B2's exact-head review, and B2-C4" and "B2-C4's re-review, and B2-C5";
- the B2-C5 prompt, `docs/ephemeral/2026-10-24-p06-2-stage-b2-c5-correction-prompt.md`;
- the evidence record, whole:
  - "Exact-head review of Stage B2-C4";
  - "Stage B2-C5";
- the whole of `git diff 4c70db890b476f63ce96ff5e18fe3ea5fbea777a HEAD`;
- whole: `proofs/stream-chat/glow_stream_proof/conformance.py` and `cmd_conformance` in `cli.py`;
- in `proofs/stream-chat/glow_stream_proof/proof_run.py`: `_generic`, `_TABLE_NAMES`, `_check`, `_text`, `_client_note`, `_send`, `_request_line`, `_defer_stop` and `results`.

**At `<RECORDS_COMMIT>`:** the evidence record's "Manager verification of Stage B2-C5", the P11 plan's bullet on the harness's next live conformance run (`docs/testing/p11-deferred-acceptance.md`), and the brief's "Sessions".

**The run of record's logs:** run 40054102314's API checks job, Stream proof checks job and gate. Read enough to confirm the test counts (331 and 648) and `run plan: fits`; say what you read.

## 3. What to review

1. **C4R1, the form `_generic` leaves.**
   - Does `_without_ids` now reach every form in which an identifier of the run can appear in the results, the progress file, the final JSON and the Markdown? Look at the paths that build strings from identifiers: `_generic`, `_request_line`, the guard's and the redactor's output, the client notes, and Stream's guest IDs (`guest-<uuid>-<id>`).
   - Name any form left. Say whether it can occur.
   - Can the new pairs replace anything but an identifier?
   - Is the order of the whole and the `{prefix}` forms right?
   - Is the empty-prefix guard right?
   - Does the test cover the five paths it names, and do D3 and D7 read with the user's key? Does its reversal fail for the right reason?
2. **`stop_reason`.**
   - Is it generalized in both writes, the early results and the final results?
   - Is a `None` `stop_reason` unchanged?
   - Does the exit-code logic still read the raw value?
   - Is anything else written to a record outside `results()`?
   - Is carrying the console lines, the closing line included, to P11 right?
3. **C4R2.** Does the write case now fail when the refusal reaches a read? Does its reversal fail for the right reason?
4. **Nothing else changed** against `4c70db8`: the adapter's code, `proof_run.py`, the rows and their identifiers, verdicts and order, the guard, the deny-lists, the budget, cleanup's rules, the baselines, the workflow, and every dependency and lock file. `cli.py` changed only in `cmd_conformance`'s `stop_reason`.
5. **The records.** Does any statement in the docstrings, the harness README, "Stage B2-C5" or "Manager verification of Stage B2-C5" claim more than the code, the tests or the run show?
6. **What is still open** from the reviews of B2, B2-C4 and B2-C5: list any finding that is neither fixed nor recorded with a disposition.
7. **The offline checks,** run at `HEAD` in a clean environment:
   - the API: hash-locked installs and `pip check`; `manage.py check` and its tests (331); Ruff; mypy; the static check with `makemigrations --check --dry-run`; the sealed-runtime and pin tests;
   - the harness: hash-locked install and `pip check`; its tests (648); Ruff; mypy; `node --check` on its client files; `checks/run_plan.py`.

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

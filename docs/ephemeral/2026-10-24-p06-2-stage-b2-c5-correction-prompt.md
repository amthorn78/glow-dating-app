# P06.2 Stage B2-C5 prompt — correction pass on B2-C4's exact-head re-review

- **Owner:** App Manager 7. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 24 October 2026.**
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 11, "B2-C4's re-review, and B2-C5".
  - Input: the evidence record's "Exact-head review of Stage B2-C4", findings C4R1 and C4R2 with the manager's dispositions.
- **Where the result goes:** the session's code and tests, and its section "Stage B2-C5" in the evidence record. The run of record is the Foundation run on its last code commit if its branch is under the workflow's push filter; otherwise it is PR31's run on the manager-branch head that integrates it (AM7-02). The manager adds its verification and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 1.69 (confidence 0.77); rung probabilities low 0.00, medium 0.32, high 0.66, extra high 0.02, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.93, Sonnet 5.5 0.07, Haiku 5.5 0.00 (confidence 0.91). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.298, Opus 5.5 at high 0.614, Opus 5.5 at extra high 0.019, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.022, Sonnet 5.5 at high 0.046, Sonnet 5.5 at extra high 0.001, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-10-24T02:09:48Z. Nathan picks the cell.
  - **Nathan's pick:** not recorded (the relay did not name it).
- **The Dev Manager's read:** none needed. The pass corrects a re-review's findings and authorizes no credential use, provider call, dependency or design change.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and the session calls no provider.
- **It runs alone** (OD-29). An exact-head re-review of the corrected head follows, then Codex's code review of the final head (OD-41).
- **Deletion condition:** prune after Stage B2's PR merges and the evidence record holds the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **correction session P06.2 Stage B2-C5**, a small offline pass on Stage B2 of P06.2, the chat integration of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<START_SHA>`.

**What exists.** Stage B2 and its correction passes B2-C1 to B2-C4 are the draft PR31, from the manager branch `claude/magical-wozniak-yfmmx2` into `main`.

- **B2-C4** (code commit `42e6231`, integrated at the merge `da3c0ff`) gave the conformance rows C4, M5, D10 and V13 their own users and made M5 a recorded row. It also:
  - raised the adapter's mapped errors after their `except` block;
  - added `_without_ids` to `proofs/stream-chat/glow_stream_proof/conformance.py`, which replaces every identifier of the run with `{key}` in the conformance results.
- **Its exact-head re-review** (the evidence record, "Exact-head review of Stage B2-C4") found everything else correct, with one should-fix finding and one nit:
  - **C4R1:** `_without_ids` matches each identifier only in full. Strings that `proof_run._generic` has already rewritten hold `{prefix}<32 hex>`, so they keep their random part. Those are the connect, read and client notes, checks and async errors, which include D3's and D7's connect notes. Four statements claim more than the code does.
  - **C4R2:** a boundary test's write case does not assert that its refusal reached the write.
- **The manager's verification** adds `cmd_conformance`'s `stop_reason`: it is written to the results after only the redactor, so a stop whose exception names a run identifier writes that identifier whole.
- **The code at your start** is byte-identical to `42e6231`'s, the code of the run of record, Foundation run 40049721647.

**How you work:**
- Nathan started you manually and will relay your report to the manager (App Manager 7). You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- Your boundary is scope:
  - write only your owned paths (section 5);
  - push only your own session branch. If your branch is under the workflow's push filter (`claude/**`), each push runs the Foundation workflow on it; read those runs if your tools can. On GitHub do nothing else: no pull request, no PR comments, no re-runs, no workflow dispatches. Change nothing in Notion.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, token, signature or marker, in any form;
  - call Stream, or run any harness command that reaches it (`baseline`, `full-view`, `configure`, `restore`, `verify-clean`, `cleanup`, `run`, `conformance`). The harness's offline tests use fakes and are allowed;
  - start or connect to any database; connect to HDE, Railway or any other provider;
  - run `playwright install`, `eas` or `migrate`;
  - add or change a dependency, a version or a lock file.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If any is present, stop and report: this session must start in `Glow App - No Stream`.
3. No `PG*` or `PROOF_DB_*` name should be set (`compgen -e | grep -E '^(PG|PROOF_DB_)'`). If one is present, report its name, never read or use its value, and continue.
4. **No `.env` file:** `ls -a . services/api proofs/stream-chat | grep -x '\.env'` must print nothing. If one exists, report it without reading it, and stop.
5. **The toolchain:** the pinned toolchain is in `$HOME/.local/bin`: Python 3.12.14, Node 24.19.0 and npm 11.9.0. Put `$HOME/.local/bin` first on PATH in every process you run, then record `command -v python3.12` and its version. Create any virtual environment with `python3.12`, outside the checkout. The harness's tests need its client's `node_modules`: run `npm ci --ignore-scripts` in `proofs/stream-chat` (the directory is git-ignored).
6. Run the API's and the harness's commands in a clean process environment: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus `GLOW_ENV=test` for the API, as `docs/operations/local-development.md` and the READMEs show. Installs get the proxy and CA variables by reference, never printed. Run the classification commands from the repository root.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git merge --ff-only <START_SHA>          # on your own session branch
git rev-parse HEAD                       # must print <START_SHA>
git diff --stat <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- services/ proofs/ .github/   # must print nothing
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md | grep -c '^## Stage B2-C5'   # must print 0
git diff --quiet 42e623197cb341a3e4188a5fba918639c133ae4b HEAD -- proofs .github services scripts apps packages && echo "the code of the run of record"
```

If code or this pass's section has already landed on the live manager branch, this prompt is stale: stop and report (AM5-15). If any check fails, stop and report.

Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`, and `proofs/stream-chat/README.md`;
- the P06.2 brief, `docs/planning/p06-2-chat-integration.md`: "B2's exact-head review, and B2-C4" and "B2-C4's re-review, and B2-C5";
- the evidence record, `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`, whole:
  - "Stage B2-C4";
  - "Manager verification of Stage B2-C4";
  - "Exact-head review of Stage B2-C4";
- `proofs/stream-chat/glow_stream_proof/conformance.py`;
- in `proofs/stream-chat/glow_stream_proof/proof_run.py`: `_generic`, `_TABLE_NAMES`, `_check`, `_text`, `_client_note`, `_send`, `_defer_stop` and `results`;
- `cmd_conformance` in `proofs/stream-chat/glow_stream_proof/cli.py`;
- `proofs/stream-chat/tests/test_conformance.py`, with the fakes it uses;
- `services/api/tests/test_chat_provider_stream.py`'s `test_streams_error_answer_is_mapped_with_no_cause_or_context` and the recorded transport it uses.

## 3. The work

**For each item:**
- write a test that fails without the change and passes with it;
- show the failure with a reversal in a scratch copy outside the repository.

1. **C4R1, the form `_generic` leaves.**
   - **The change:** in `_without_ids` (`conformance.py:867-883`), also replace `"{prefix}"` followed by each identifier's part after the run's prefix, with `{key}`, longest first. This is the re-review's suggested change. With it, a string that `_generic` already rewrote loses the random part too.
   - **What stays unchanged:** `proof_run.py`, and every other command's records.
   - **The test:** a fake run in which identifiers of the run reach the results through `_text` (as `_token_check`'s connect note does), through `_client_note` and through a check's evidence. Include a connect refusal that names the user, as Stream's did for D3 and D7 in B2-C3 (`user "<id>" does not exist`). Assert:
     - no part of the results, and nothing in `render`'s Markdown, contains the random part of any of the run's identifiers;
     - D3's note reads with the user's key.
2. **`stop_reason`, B2C4-X2's part that reaches a record.**
   - **The change:** in `cmd_conformance` (`cli.py:658` onward), pass `stop_reason` through the run's `_without_ids` before it is added to the early results (`:708-717`) and to the final results (`:740-742`).
   - **What stays unchanged:** the console lines (`cleanup:`, `stop recorded:`, `after the run:`), which stay carried to P11, and `cmd_run`.
   - **The test:** a conformance run stopped by an exception whose text names a run identifier. Neither the written JSON nor the Markdown keeps the identifier's random part.
3. **C4R2, the write case.** In `test_streams_error_answer_is_mapped_with_no_cause_or_context` (`services/api/tests/test_chat_provider_stream.py:803-833`), the `at_write=True` case asserts that the scripted refusal reached the write: the last recorded request's method and path, or the recording's length. The test's reversal is a wrong read count that sends the refusal to a read.
4. **The claims.**
   - `_without_ids`'s docstring and the harness README's conformance description state what the code now does:
     - every identifier of the run, whole or as `_generic` leaves it;
     - in every part of the results and in `stop_reason`;
     - not in the console lines.
   - The B2-C4 section of the evidence record stays byte-identical. Your section says which of B2-C4's statements your change makes true: its item 4 and its "What the exact-head re-review must know".

**Not in B2-C5:**
- B2C4-X1 and the console lines, which are carried to P11;
- the adapter's code;
- the rows, their identifiers, verdicts and order;
- `proof_run.py`, the guard, the deny-lists, the budget and cleanup's rules;
- the baselines, the workflow, and every dependency and lock file.

**A finding outside this work:** report it with its class. Fix it here only if it could:
- let a credential, token or signature reach a log line, a record, a test recording or a file outside the git-ignored working directories;
- let a request reach Stream outside the guard;
- let provider text reach a Glow code or a user.

**Rules:**
- reversals in a scratch copy outside the repository, never the checkout, with `git status` clean afterwards (DM-14 item 6);
- no weakened check, guard, deny-list or budget;
- no credential anywhere;
- no live command.

**A departure** from any of the above that you find necessary: stop before making it, and report it.

## 4. Checks

Report the exact commands and results.

1. `git diff --check <START_SHA> HEAD` and `git diff --name-only <START_SHA> HEAD`: only owned paths changed.
2. **Classification,** from the repository root, with the trusted policy from `main`, outside the tree. Expected: full scope.

   ```bash
   base=$(git rev-parse origin/main); d=$(mktemp -d)
   git show "$base:scripts/change_scope.py" > "$d/change_scope.py"
   python3 -I "$d/change_scope.py" --base <START_SHA> --head "$(git rev-parse HEAD)" --merge-base
   ```
3. **Installs:** hash-locked installs and `pip check` for the API and the harness; `npm ci --ignore-scripts` for the harness's client, with `npm audit`'s advisory named (package, severity, advisory ID; no change).
4. **The offline checks:**
   - the API's tests (331 at the start) and the harness's tests (646 at the start), with their counts;
   - Ruff check and format, and mypy;
   - the static check, with `makemigrations --check --dry-run`;
   - the sealed-runtime and pin tests;
   - `node --check` on the harness's client files;
   - `checks/run_plan.py`'s result.
5. **The run of record:**
   - **If your branch is under the workflow's push filter:** the Foundation run on your last code commit, with its run ID, each job's conclusion (eight jobs), the database job's duration, and the gate's line `Application checks passed`. Push nothing more until it has finished (AM5-14).
   - **Otherwise:** say that no run started, and why.
6. A secret scan over your whole diff and your record.

## 5. Owned paths, push and records

- **You may change:**
  - in `proofs/stream-chat/`:
    - `glow_stream_proof/conformance.py`;
    - `glow_stream_proof/cli.py`: `cmd_conformance`'s `stop_reason` only;
    - `tests/**`;
    - `README.md`: the conformance description only;
  - `services/api/tests/test_chat_provider_stream.py`: item 3 only;
  - the evidence record: a new section "Stage B2-C5" after the existing sections, which stay byte-identical.
- **Nothing else.** Report any other change you think is needed, before making it.
- **Commit and push** your session branch. Don't open a pull request.
- **Your section "Stage B2-C5"** records:
  - the prompt's revision and start SHA, your head, your branch and the run of record;
  - items 1 to 4, each done (with `file:line`, its test and its reversal) or left (with the reason);
  - every check with its exact results;
  - deviations and limits;
  - what the exact-head re-review must know.

## 6. Report

Your final message is the report Nathan relays. It covers:
- the prompt revision (revision 1, from `<START_SHA>`);
- the environment check (names only, the `.env` check included);
- your branch, head SHA and changed paths;
- items 1 to 4, done or left;
- every check with its exact results, and the run of record's details;
- deviations, departures you stopped at, findings outside the work with their class, and limits.

# P06.1-C5 prompt — fifth correction pass: the C4 review's findings

- **Owner:** App Manager 5. Nathan starts this session manually and relays its report.
- **Revision 1, 27 September 2026.**
- **Durable brief:** [P06.1 brief](../planning/p06-1-chat-provider-proof.md), "Brief — P06.1" (owned paths, credential rules, matrix quality rule) and "Sessions" (P06.1-C5).
  - Work list: the [P06.1 evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md), "Exact-head review of C4 (27 September 2026)": the review's report, verbatim; the manager's verification; and the "Disposition", which adds one requirement to finding 1.
- **Where the result goes:**
  - the session brings the harness README into line with each change, corrects one bullet of C4's section in place, and adds a section at the end of the evidence record, "P06.1-C5 corrections";
  - the manager adds its verification there and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v6: Opus 5.5, high.** Effort score 2.01 (confidence 0.90); rung probabilities low 0.00, medium 0.07, high 0.86, extra high 0.07, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 1.00 (confidence 1.00). Sent 2026-09-27T21:27:30Z. Nathan picks the cell.
  - **Nathan's pick: Opus 5.5 at high**, started 27 September. This line was added after the prompt was given; the body Nathan pasted is unchanged.
- **Result:** verified by the manager and integrated by fast-forward at `1a5f58a` (code head `11b5771`) on 28 September; see the evidence record, "P06.1-C5 corrections" and the manager's verification under it.
- **No Dev Manager read is needed:** the prompt authorizes no credential use and no live provider action.
- **Stream variables** (OD-28): none are needed, and Nathan adds none. This session never calls Stream. The environment check reports any it finds by name.
- **It runs alone** (OD-29, the linear process). Its exact-head review follows and is P06.1's final delta review; the economics discovery comes after it.
- **Deletion condition:** prune after P06.1 closes and the evidence record and brief hold the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **implementation session for P06.1-C5**, the fifth correction pass on the P06.1 chat-provider proof harness of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<START_SHA>`.

P06.1 tests Stream's permission model against Nathan's development Stream application 1729640, with synthetic users only, using the sandbox harness in `proofs/stream-chat/`. P06.1-C4, the last correction pass, made the runner apply the product op's check to every request to Video or Feeds, whatever op sends it, and made `matrix.validate` refuse a matrix step that names one of the client's URL-taking methods. Its exact-head review, of `c83bedf` (code head `b2b9a0b`), asked for changes:

- **one should-fix finding,** in the class that gets another correction pass: `validate` does not refuse every stream-chat method whose arguments reach a request's configuration or path, and the README's recorded limits rest on it doing so;
- **four nits,** numbered 2 to 5. Nit 3 is the manager's, and is done.

**You fix finding 1 and nits 2, 4 and 5, offline.** You make no Stream call. The harness is not used live again until after your change and its review.

- Nathan started you manually and will relay your report to the manager (App Manager 5). You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- Your boundary is scope:
  - write only your owned paths (section 5);
  - push only your own session branch. On GitHub do nothing else: no pull request, no PR comments, no re-runs, no workflow dispatches. Change nothing in Notion.
- **Never:**
  - dump the environment;
  - connect to Stream, a database, HDE, Railway or any other provider. Run none of the harness's live commands: `baseline`, `probe-products`, `configure` (even as a dry run, with or without `--products`), `run`, `verify-clean`, `cleanup` or `restore`;
  - run `playwright install`, `eas` or `migrate`.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` should be absent (OD-28): `for n in STREAM_APP_ID STREAM_API_KEY STREAM_API_SECRET; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, report its name first in your report, never read or use its value, and continue. The harness's offline checks must pass without them.
3. The pinned toolchain is in `$HOME/.local/bin`: node v24.19.0, npm 11.9.0 and Python 3.12.14. The default PATH may find another node first (the C4 review's found `/opt/node22`). Put `$HOME/.local/bin` first on PATH in every process you run the harness in, then record `command -v node npm npx python3.12` and their versions. Say what the default PATH finds if it differs.
4. Run the harness's commands in a clean process environment, as its README's "Install" and "Checks (offline)" sections show. Installs get the proxy and CA variables by reference, never printed.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2
git merge --ff-only <START_SHA>          # on your own session branch
git rev-parse HEAD                       # must print <START_SHA>
git diff --stat c83bedf1f812cf454d4f16b5dc741c5d944749d9 HEAD -- proofs/stream-chat/ .github/   # must print nothing
```

The last command shows that the harness and the workflow are unchanged since the reviewed head, so the review's line numbers still apply. If any check fails, stop and report.

Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`;
- the P06.1 brief, `docs/planning/p06-1-chat-provider-proof.md`: "Brief — P06.1" (owned paths, credential rules, the matrix quality rule and the acceptance checks) and "Sessions" (P06.1-C4, its review and P06.1-C5);
- the evidence record, `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md`:
  - "Exact-head review of C4 (27 September 2026)" is your work list: the report, verbatim, the manager's verification and the "Disposition";
  - "P06.1-C4 corrections" is the section with the bullet you correct, and it records the rules C4's fixes set;
  - the earlier sections record the rules your fixes must keep;
- `proofs/stream-chat/README.md` and the whole harness under `proofs/stream-chat/`;
- in stream-chat 9.53.0 as installed (`node_modules/stream-chat/dist/cjs/index.node.js`), the methods finding 1 names, and `get`, `doAxiosRequest` and `_enrichAxiosOptions`, which carry a request-options argument into the request's configuration.

## 3. The work

The review's findings are in the evidence record, under "Exact-head review of C4", "Findings, most severe first", numbered 1 to 5. Each gives its `file:line`, a scenario and a suggested fix. Use the suggested fix unless you find a better one, and say why if you do. The requirements below are the manager's disposition, and they stand either way.

1. **Finding 1: no matrix step can pass a request option, and no request carries a rewriting header.** Do this first.
   - **`validate`** in `glow_stream_proof/matrix.py` refuses every `call` step outside an explicit allowlist of (target, method, maximum positional arguments), on both the client and the channel targets.
     - The allowlist holds exactly what the current matrix's `call` steps use, and every current case still validates.
     - Outside it: any other method; any other target; more positional arguments than listed, so that no request-options position is reachable (the client's `queryUsers` and `search` and the channel's `queryMembers` take request options as their fourth argument, the channel's `sendFile` and `sendImage` as their fifth); and the reminder methods, which put a caller value into the path unencoded.
     - The client's URL-taking methods stay refused, and the rule for a `get` of a product path stays.
   - **The manager's addition: the runner refuses the request-rewriting headers.** In `client/runner.cjs`'s request interceptor, refuse a request carrying `X-HTTP-Method-Override`, `X-HTTP-Method`, `X-Method-Override`, `X-Original-URL` or `X-Rewrite-URL`, in any letter case. Do it as it refuses the forwarding headers: before the request is counted or sent, with the error kind `refused`, whatever op sent it.
     - `validate` sees only the matrix, and the harness's own code also sends `call` ops, so this closes the residual for every caller.
     - Show, from the installed packages, that neither stream-chat 9.53.0 nor axios 1.20.0 sends any of these headers, so that no chat case is affected.
   - **Tests:**
     - `validate` reports each kind: an unlisted method on the client, an unlisted method on the channel, a listed method with one positional argument too many, and a reminder method. Every current case still validates;
     - the real runner refuses a request carrying each rewriting header, one of them in another letter case, with the error kind `refused`. Use a zero budget and an unreachable proxy, as C4's runner tests do, so that nothing can leave the machine;
     - a reversal for the allowlist and one for the header refusal.
   - **The records.** Correct `README.md:398`, and the bullet of "P06.1-C4 corrections" (under "C4's own review", the re-check of `112011f`) that says "only a `call` of a client URL method, which `validate` refuses, could set them", in place. Mark each "(corrected in P06.1-C5; the C4 review's finding 1)". They must say:
     - what `validate` now covers: the matrix's steps;
     - what the runner now refuses: the rewriting headers, for every caller;
     - what remains: a per-request `proxy`, `socketPath` or adapter, none of which gets past the runner's host and path checks.

     Keep the WebSocket-host and fetch-adapter statements, which the review confirmed. Bring any other README sentence about `validate` or the headers into line.
2. **Nit 2: `maxRedirects` has a test.** Load `runner.cjs` with a stub `stream-chat` in `require.cache`, as the runner already does for `isomorphic-ws`. Capture the request interceptor it registers, call it with a chat request's config, and require `maxRedirects` to be 0. Add a reversal, and correct `README.md:397`, which says the setting has no offline test.
3. **Nit 4: a failed record write after a signal keeps the stop.** In both `configure --apply` paths (`glow_stream_proof/cli.py:335` and `:421`), a record write that raises after a charge or limit signal must not hide the signal. That covers the leak check refusing the record and the write failing.
   - The command still exits 3, and a line names the signal.
   - The write's error is reported too, chained or printed, and never lost.
   - Nothing is sent either way.

   Test: a signal mid-plan and a record write that raises, for each path. Add a reversal.
4. **Nit 5: the ledger rule has a test of its own.** Add a variant of `test_the_signal_is_read_from_the_ledger_not_the_exception` in which an ordinary error, not a Ctrl-C, replaces the stop. It checks two things: no re-read is sent, and the record says a signal was met. Add this test to the ledger rule's reversal, which must fail it on the requests sent.

**Not in this pass:** anything else. If you find more, report it with its class. Fix it here only if it could do one of these, and then with a test and a reversal:

- create a false HOLDS, MEETS or "ended";
- lose an observed FAIL or DOES NOT MEET;
- send a request after a charge or limit signal;
- let a request or a change escape the runner's check, the guard or the deny-lists;
- let the scoped `configure` apply anything outside the two products.

**Rules for every fix:**

- **A test for each fix.** Each item you fix in code gets an offline test that fails without the fix and passes with it. Say which test covers which item. Add a reversal to `checks/fix_reversals.py` for each.
- **Every reversal fails for the right reason.** Report, for every new reversal, whether its tests fail on the expected assertion or error, or by Ctrl-C by design. A reversal whose edited file does not compile or import is not demonstrated.
- **No live calls.** Tests use fakes or the harness's offline simulation.
- **The credential rules stand.** The secret never reaches a client process or any output. Keep the client environment's allowlist, the runner's refusal, redaction and the leak checks.
- **The matrix quality rule stands.** Never weaken a verdict rule to make a test pass.
- **The guard, the deny-lists, the runner's check and the configure gates stand.** No fix widens what the harness may send. The two deny-list tables stay in agreement.
- **No dependency change.** `requirements.in`, `requirements-dev.in`, both `.lock` files, `package.json`, `package-lock.json`, `.npmrc` and the dependencies in `pyproject.toml` stay as they are. If a fix seems to need a change, leave that item and report why.

## 4. Checks

Report the exact commands and results.

1. `git diff --check <START_SHA> HEAD`, and `git diff --name-only <START_SHA> HEAD`: only owned paths changed.
2. Classification with the trusted policy from `main`, run outside the tree, as root `AGENTS.md` requires. Expected: full scope.

   ```bash
   base=$(git rev-parse origin/main); policy_dir=$(mktemp -d)
   git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
   python3 -I "$policy_dir/change_scope.py" --base <START_SHA> --head "$(git rev-parse HEAD)" --merge-base
   ```

3. The installs from the locks, with the README's commands, in clean processes.
4. The offline checks, with the README's commands:
   - the unit tests, with the counts at the start and at your head (C4 left 543);
   - Ruff check and format;
   - mypy, with its file count;
   - `node --check` on each `client/*.cjs`;
   - `checks/run_plan.py` with an empty ledger.
5. `checks/fix_reversals.py`, in a scratch copy outside the tree: its counts at the start (378) and at your head, with none "not demonstrated", and each new reversal's failure reason.
6. A secret scan over your whole diff: no secret, token, API key or email address, and no JWT-shaped string other than the redaction test's fabricated input.
7. The Foundation run on your final head, if your tools can read it: each job's conclusion, "Stream proof checks" included. If they cannot, say so. Re-run or dispatch nothing.

## 5. Owned paths, push and records

- **You may change:**
  - `proofs/stream-chat/**`, except the dependency files above and the two committed baselines, `baseline/application-1729640-2026-09-25.json` and `baseline/video-feeds-1729640-2026-09-27.json`;
  - `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md`: your new section at its end, and the one in-place correction in "P06.1-C4 corrections" that section 3 names. Every other part stays byte-identical, in particular "Manager verification of C4 (App Manager 5, 27 September 2026)" and "Exact-head review of C4 (27 September 2026)", each with everything under it, and every earlier review and verification.
- **Nothing else,** including the architecture document, which states no request-options limit, the brief, the ADRs, `.github/`, `apps/`, `services/` and every other document. Report any other change you think is needed.
- **Commit and push** your session branch. Don't open a pull request.
- **Your section of the evidence record,** "P06.1-C5 corrections", at its end:
  - the start SHA, your head and your branch;
  - for finding 1 and nits 2, 4 and 5: fixed (`file:line` and its test) or left (the reason);
  - the records you corrected;
  - every check, with its exact results;
  - deviations and limits;
  - what the final delta review must know: the rules that changed, and the fixes not yet exercised live.

## 6. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<START_SHA>`);
- the environment check;
- your branch, head SHA and tree, and the changed paths;
- for finding 1 and nits 2, 4 and 5: fixed (`file:line` and the test) or left (the reason);
- the records corrections;
- every check, with its exact results;
- deviations, limits, and what the final delta review must know.

Skipped or unavailable checks are not passes.

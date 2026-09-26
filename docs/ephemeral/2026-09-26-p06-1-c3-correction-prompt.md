# P06.1-C3 prompt — third correction pass on the harness

- **Owner:** App Manager 3. Nathan starts this session manually and relays its report.
- **Revision 1, 26 September 2026.**
- **Durable brief:** [P06.1 brief](../planning/p06-1-chat-provider-proof.md), "Brief — P06.1" (owned paths, credential rules, matrix quality rule) and "Sessions" (P06.1-C3).
  - Work list: the [P06.1 evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md), "Exact-head review of C2": its findings, verbatim, and the manager's "Disposition"; and "Manager verification of C2", for the RT2 and RT3 decision.
- **Where the result goes:**
  - the session brings the harness README into line with each rule it changes, and adds a section at the end of the evidence record, "P06.1-C3 corrections";
  - the manager adds its verification there and records the outcome in the brief's "Sessions".
- **Reasoning level.** Neither reading gates anything, and Nathan picks.
  - Manager: high.
  - TypeSafe v4: high (score 2.22, P(high) 0.70, P(extra high) 0.26), with no ultracode flag (P(single session) 0.93).
  - **Used: high.** Nathan started this session on 26 September. This line was added after the prompt was given; the body Nathan pasted is unchanged.
- **No Dev Manager read is needed:** the prompt authorizes no credential use and no live provider action.
- **No Stream variables** (OD-28): this session never calls Stream.
- **It runs alone** (OD-29, the linear process). Its exact-head review follows it, and I2a comes after that review.
- **Deletion condition:** prune after P06.1 closes and the evidence record and brief hold the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **implementation session for P06.1-C3**, the third correction pass on the P06.1 chat-provider proof harness of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<START_SHA>`.

P06.1-I1 built a sandbox harness in `proofs/stream-chat/` that tests Stream Chat's permission model against Nathan's development Stream application 1729640, with synthetic users only. Two offline correction passes followed, C1 and C2. C2's exact-head review, of the merge commit `63e922f`, approved it, and left:

- **two should-fix findings:**
  - a feature-gated case's observed FAIL becomes INCONCLUSIVE when its enabling request was not 2xx;
  - a charge or rate-limit signal first met during the end of the run does not stop the cleanup;
- **eight nits,** numbered 3 to 10.

The manager also decided a change to RT2 and RT3 on C2, which you make here.

**You make that change and fix all ten items, offline.** You make no Stream call. The first live use of your fixes, and of C1's and C2's, comes later, in P06.1-I2a.

- Nathan started you manually and will relay your report to the manager (App Manager 3). You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- Your boundary is scope:
  - write only your owned paths (section 5);
  - push only your own session branch. On GitHub do nothing else: no pull request, no PR comments, no re-runs, no workflow dispatches. Change nothing in Notion.
- **Never:**
  - dump the environment;
  - connect to Stream, a database, HDE, Railway or any other provider. Run none of the harness's live commands: `baseline`, `configure` (even as a dry run), `run`, `verify-clean`, `cleanup` or `restore`;
  - run `playwright install`, `eas` or `migrate`.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` should be absent (OD-28): `for n in STREAM_APP_ID STREAM_API_KEY STREAM_API_SECRET; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, report its name first in your report, never read or use its value, and continue. The harness's offline checks must pass without them.
3. Record `command -v node npm npx python3.12` and their versions. Expected: v24.19.0, 11.9.0 and Python 3.12.14, from `$HOME/.local/bin`.
4. Run the harness's commands in a clean process environment, as its README's "Install" and "Checks (offline)" sections show. Installs get the proxy and CA variables by reference, never printed.

## 2. Start gate

```bash
git fetch origin claude/stoic-carson-66gdig
git merge --ff-only <START_SHA>          # on your own session branch
git rev-parse HEAD                       # must print <START_SHA>
git diff --stat 63e922fb86f214b99627748cbb53387baa6dd748 HEAD -- proofs/stream-chat/   # must print nothing
```

The last command shows that the harness is unchanged since the reviewed head, so the review's line numbers still apply. If any check fails, stop and report.

Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`;
- the P06.1 brief, `docs/planning/p06-1-chat-provider-proof.md`: "Brief — P06.1" (owned paths, credential rules, the matrix quality rule and the acceptance checks) and "Sessions" (P06.1-C3 and I2a);
- the evidence record, `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md`, whole. Its section "Exact-head review of C2 (26 September 2026)" is your work list; "Manager verification of C2" holds the RT2 and RT3 decision; "P06.1-C1 corrections" and "P06.1-C2 corrections" record the fixes you build on;
- the C2 prompt, `docs/ephemeral/2026-09-26-p06-1-c2-correction-prompt.md`, section 3: the rules the earlier fixes follow, which still stand;
- `proofs/stream-chat/README.md` and the whole harness under `proofs/stream-chat/`.

## 3. The work

The review's findings are in the evidence record, under "Exact-head review of C2", "Findings, most severe first", numbered 1 to 10. Each gives its `file:line`, a failure scenario and a suggested fix. Use the suggested fix unless you find a better one, and say why if you do.

1. **RT2 and RT3, the manager's decision.**
   - A `feature` refusal gets the matrix's "REFUSED (feature off; not a permission error)" verdict, not HOLDS.
   - An `auth` or `permission` refusal gives HOLDS only when a control of the same request, by a member allowed to make it, succeeded. That is the brief's matrix quality rule.
     - For RT3, the control is B's own `markRead` with the same body. Keep the control's own events out of the windows searched for the marker.
     - For RT2, no such control exists while typing is off, so an `auth` or `permission` refusal is INCONCLUSIVE, "no positive control".
   - An `input`, `not-found` or `other` refusal stays INCONCLUSIVE.
   - Update the README's RT2 and RT3 rule. I1's recorded RT2 result stays as recorded.
2. **Finding 1: an observed FAIL survives a failed enabling request.** The "could not enable" verdict applies only when the feature-on phase has not already observed a FAIL.
3. **Finding 2: a charge or limit signal met anywhere in the run stops the cleanup.**
   - The run records that it has met a signal that stops it at once (HTTP 402 or 429, Stream code 9 or 99, or the charge wording), wherever it is met, including during the end-of-run restores and when `_temporary` keeps another stop as the run's stop.
   - `finish()` then still restores and re-reads the configuration, as the README says, but skips the cleanup, with the problem "cleanup skipped: …".
   - `cmd_run` uses the same record, not only the type of the run's own stop.
   - State the rule in the README.
4. **Nits 3 to 10,** as the review suggests:
   - **nit 3:** repair C1's reversal "F2 end of run". Anchor every reversal pattern at a line start. Make the script compile each edited file and count an edit that does not compile, or does not import, as "not demonstrated". Correct C2's record, which says two of the aborting reversals were C1's Ctrl-C ones;
   - **nit 4:** a test for each of the seven mutations that survived;
   - **nit 5:** when a command records more than one request, keep each request's method, generic path and status in the row's detail, and owe the undo when any of them got a 2xx;
   - **nit 6:** keep B's probe stop in `stops`, and record its signal as in finding 2;
   - **nit 7:** after a guardrail stop, S15 sends no unset of A's member field; cleanup, or `cleanup --apply` after a charge signal, deletes A. State it in the README;
   - **nit 8:** in E5 and S14, a failed read of A's stored user makes the case INCONCLUSIVE and defers a stop;
   - **nit 9:** write the usage ledger through the same atomic write as the other `.work` files;
   - **nit 10:** redact the early-write failure note.

   Fix each nit, or give a one-line reason for leaving it.
5. **The records.**
   - The README states each rule as the code now applies it.
   - In the evidence record, correct in place only a claim that was already false at C2's head, and mark it "(corrected in P06.1-C3)". Keep every recorded result as it was.

**Rules for every fix:**

- **A test for each fix.** Each change and nit you fix gets an offline test that fails without the fix and passes with it. Say which test covers which item. Add a reversal to `checks/fix_reversals.py` for each.
- **Every reversal fails for the right reason.** Report, for every reversal, whether its tests fail on the expected assertion or error, or by Ctrl-C by design. A reversal whose edited file does not compile is not demonstrated.
- **No live calls.** Tests use fakes or the harness's offline simulation.
- **The credential rules stand.** The secret never reaches a client process or any output. Keep the client environment's allowlist, the runner's refusal, redaction and the leak checks.
- **The matrix quality rule stands.** Never weaken a verdict rule to make a test pass. Where a fix changes a verdict rule, state the new rule in the README.
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
4. The offline checks, with the README's commands: the unit tests (the counts at the start and at your head; C2 left 202), Ruff check and format, mypy, and `node --check` on `client/runner.cjs` and `client/error-info.cjs`.
5. `checks/fix_reversals.py`: its counts at the start and at your head, with none "not demonstrated", and each reversal's failure reason.
6. A secret scan over your whole diff: no secret, token, JWT-shaped string, API key or email address.

## 5. Owned paths, push and records

- **You may change:**
  - `proofs/stream-chat/**`, except the dependency files above and the committed baseline, `baseline/application-1729640-2026-09-25.json`;
  - `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md`, except these sections, each with everything under it: "Manager verification (App Manager 3, 25 September 2026)", "Exact-head review of I1 (25 September 2026)", "Manager verification (App Manager 3, 26 September 2026)", "Exact-head review of C1 (26 September 2026)", "Manager verification of C2 (App Manager 3, 26 September 2026)" and "Exact-head review of C2 (26 September 2026)".
- **Nothing else**, including the brief, the ADRs, `apps/`, `services/`, `.github/` and every other document. Report any other change you think is needed.
- **Commit and push** your session branch. Don't open a pull request.
- **Your section of the evidence record,** "P06.1-C3 corrections", at its end:
  - the start SHA, your head and your branch;
  - for the RT2 and RT3 change, findings 1 and 2 and nits 3 to 10: fixed (`file:line` and its test) or left (the reason);
  - the records you corrected;
  - every check, with its exact results;
  - deviations and limits;
  - what I2a must know, in addition to C1's and C2's lists: the rules that changed, and the fixes not yet exercised live.

## 6. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<START_SHA>`);
- your branch, head SHA and tree, and the changed paths;
- for the RT2 and RT3 change, findings 1 and 2 and nits 3 to 10: fixed (`file:line` and the test) or left (the reason);
- the records corrections;
- every check, with its exact results;
- deviations, limits, and what I2a must know.

Skipped or unavailable checks are not passes.

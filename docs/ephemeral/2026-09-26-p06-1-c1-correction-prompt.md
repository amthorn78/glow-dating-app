# P06.1-C1 prompt — correction pass on the I1 harness

- **Owner:** App Manager 3. Nathan starts this session manually and relays its report.
- **Revision 1, 26 September 2026.**
- **Durable brief:** [P06.1 brief](../planning/p06-1-chat-provider-proof.md), "Brief — P06.1" (owned paths, credential rules, matrix quality rule) and "Sessions" (P06.1-C1).
  - Work list: the [P06.1 evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md), "Exact-head review of I1": its findings, verbatim, and the manager's "Disposition".
- **Where the result goes:**
  - the session corrects the evidence record's claims in place and adds a section at its end, "P06.1-C1 corrections";
  - the manager adds its verification there and records the outcome in the brief's "Sessions".
- **Reasoning level.** Neither reading gates anything, and Nathan picks.
  - Manager: extra high.
  - TypeSafe v4: high (score 2.20, P(high) 0.67, P(extra high) 0.27), with no ultracode flag (P(single session) 0.91).
  - **Used: extra high.** Nathan started this session on 26 September. This line was added after the prompt was given; the body Nathan pasted is unchanged.
- **Result:** the manager verified the branch and integrated it at `e85bba0` on 26 September; see the evidence record, "P06.1-C1 corrections" and the manager's verification under it.
- **No Dev Manager read is needed:** the prompt authorizes no credential use and no live provider action.
- **No Stream variables** (OD-28): this session never calls Stream.
- **It runs alone** (OD-29, the linear process). Its exact-head review follows it.
- **Deletion condition:** prune after P06.1 closes and the evidence record and brief hold the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **implementation session for P06.1-C1**, the correction pass on the P06.1 chat-provider proof harness of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<START_SHA>`.

P06.1-I1 built a sandbox harness in `proofs/stream-chat/` that tests Stream Chat's permission model against Nathan's development Stream application 1729640, with synthetic users only. Its exact-head review, of code head `9ff600f`, required changes:

- **two blocking findings:** the harness can record a pass for a request Stream never refused, and a failed restore of a temporary setting change does not stop the run;
- seven more findings, and 17 nits.

**You fix findings 1 to 8 and the nits, offline.** You make no Stream call. The first live use of your fixes comes later, in P06.1-I2a. Finding 9, the endpoints the matrix never tried, and finding 6's new G2 and S10 setups belong to I2a too.

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
git diff --stat 9ff600fea99cd17e6410b773a618281cc1a79b6b HEAD -- proofs/stream-chat/   # must print nothing
```

The last command shows that the harness is unchanged since the reviewed head, so the review's line numbers still apply. If any check fails, stop and report.

Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`;
- the P06.1 brief, `docs/planning/p06-1-chat-provider-proof.md`: "Brief — P06.1" (owned paths, credential rules, the matrix quality rule and the acceptance checks), "Sessions" (P06.1-C1 and I2a) and "S15: decided";
- the evidence record, `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md`, whole. Its section "Exact-head review of I1" is your work list;
- the I1 prompt, `docs/ephemeral/2026-09-25-p06-1-i1-implementation-prompt.md`: the harness's design rules;
- `proofs/stream-chat/README.md` and the whole harness under `proofs/stream-chat/`.

## 3. The work

The findings are in the evidence record, under "Exact-head review of I1", "Findings, most severe first". Each gives its `file:line`, a failure scenario and a suggested fix. Use the suggested fix unless you find a better one, and say why if you do.

1. **Finding 1 (blocking): verdicts come from the request under test.**
   - Take each verdict's status and code from the recorded HTTP response of the command under test. If that request recorded no response, the case is INCONCLUSIVE, never HOLDS.
   - G1 FAILs whenever the client's own request created a guest, whatever the connect then did.
   - G3 is INCONCLUSIVE unless the anonymous connect succeeded.
   - For RT2 and RT3, a local SDK throw, or a `null` return with no request, is INCONCLUSIVE.
2. **Finding 2 (blocking): temporary changes are always restored, and a failed restore stops the run.**
   - `RunStopped` is re-raised, as `GuardrailStop` is. A restore failure raised in a `finally` must not hide a `GuardrailStop` already in flight: record both, and stop.
   - Each `try` opens before its enabling request.
   - Keep a journal of temporary changes. `cmd_run`'s `finally` restores and verifies every journalled change, including after a timeout or Ctrl-C.
   - Every run ends with `configuration.verify()`. Any difference makes the run exit non-zero and says what differs.
   - Check the results of undos and override removals, and re-read each removal (nit 4).
3. **Finding 3: preflight accepts exactly one dashboard user.** Stop unless exactly one user has role `admin` and `custom.dashboard_user` true. You may also check that user's `created_at` against the value in the evidence. Record no identifier.
4. **Finding 4: the events view.** Exclude the SDK's local event types, such as `channels.queried`, `capabilities.changed`, `connection.changed` and `message.read_locally`, and record which event type carried the marker. Apply the same exclusion to RT2 and RT3, and search every event window they collect (nit 1).
5. **Finding 5: replies are matched to commands.** Check each reply's `id` against its command's. On a mismatch or a timeout, end that client session and mark the affected cases INCONCLUSIVE. A line the reader has already buffered must not be missed or cause a false timeout.
6. **Finding 6, your part.** Make the offline simulation behave like the live lockdown for guests: `setGuestUser`'s connect is refused, so the simulation shows G2 as "not run", as the live runs did. The new G2 and S10 setups are I2a's work; don't build them.
7. **Finding 7: leak terms.** Add the terms the review lists for `read-ab` and `message`.
8. **Finding 8 and the other records.** Correct, in the evidence record and the README:
   - every claim finding 8 lists, and the missing items in "Limits";
   - the `member.updated` claims (finding 4, evidence lines 26 and 352–354): B's channel query carries S15's text; the realtime event path is unproven, and I2a maps it;
   - the claim that the offline simulation covers G2 and S10 (finding 6, line 480);
   - evidence line 91 and README line 103, once finding 3 is fixed.

   Edit each claim in place and mark it "(corrected in P06.1-C1)". Keep I1's recorded results as they were: a correction changes a claim about them, never a result.
9. **The nits.** Fix every nit that lies within your owned paths, or give a one-line reason for leaving it. The review numbers them 1 to 17.

**Rules for every fix:**

- **A test for each fix.** Each finding and nit you fix gets an offline test that fails without the fix and passes with it. Say which test covers which item.
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
4. The offline checks, with the README's commands: the unit tests (give the counts before and after your changes), Ruff check and format, mypy, and `node --check client/runner.cjs`.
5. For each finding and nit you fixed: its test failing without the fix and passing with it.
6. A secret scan over your whole diff: no secret, token, JWT-shaped string, API key or email address.

## 5. Owned paths, push and records

- **You may change:**
  - `proofs/stream-chat/**`, except the dependency files above and the committed baseline, `baseline/application-1729640-2026-09-25.json`;
  - `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md`, except the manager's sections: "Manager verification" and "Exact-head review of I1" with everything under it.
- **Nothing else**, including the brief, the ADRs, `apps/`, `services/`, `.github/` and every other document. Report any other change you think is needed.
- **Commit and push** your session branch. Don't open a pull request.
- **Your section of the evidence record,** "P06.1-C1 corrections", at its end:
  - the start SHA, your head and your branch;
  - for each finding 1 to 8 and each nit: fixed (`file:line` and its test) or left (the reason);
  - the records you corrected;
  - every check, with its exact results;
  - deviations and limits;
  - what I2a must know, including the fixes not yet exercised live.

## 6. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<START_SHA>`);
- your branch, head SHA and tree, and the changed paths;
- for each finding 1 to 8 and each nit: fixed (`file:line` and the test) or left (the reason);
- the records corrections;
- every check, with its exact results;
- deviations, limits, and what I2a must know.

Skipped or unavailable checks are not passes.

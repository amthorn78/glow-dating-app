# P06.1-C2 prompt — second correction pass on the harness

- **Owner:** App Manager 3. Nathan starts this session manually and relays its report.
- **Revision 1, 26 September 2026.**
- **Durable brief:** [P06.1 brief](../planning/p06-1-chat-provider-proof.md), "Brief — P06.1" (owned paths, credential rules, matrix quality rule) and "Sessions" (P06.1-C2).
  - Work list: the [P06.1 evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md), "Exact-head review of C1": its findings, verbatim, and the manager's "Disposition".
- **Where the result goes:**
  - the session brings the harness README into line with each rule it changes, and adds a section at the end of the evidence record, "P06.1-C2 corrections";
  - the manager adds its verification there and records the outcome in the brief's "Sessions".
- **Reasoning level.** Neither reading gates anything, and Nathan picks.
  - Manager: high.
  - TypeSafe v4: high (score 2.19, P(high) 0.68, P(extra high) 0.25), with no ultracode flag (P(single session) 0.77).
  - **Used: high.** Nathan ran the session on 26 September. This line was added after the prompt was given; the body Nathan pasted is unchanged.
- **Result:** the manager verified the branch and integrated it at `63e922f` on 26 September; see the evidence record, "P06.1-C2 corrections" and the manager's verification under it. Finding 3's direction for a `feature` refusal was the manager's mistake (AM3-16), and the manager changed it.
- **No Dev Manager read is needed:** the prompt authorizes no credential use and no live provider action.
- **No Stream variables** (OD-28): this session never calls Stream.
- **It runs alone** (OD-29, the linear process). Its exact-head review follows it, and I2a comes after that review.
- **Deletion condition:** prune after P06.1 closes and the evidence record and brief hold the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **implementation session for P06.1-C2**, the second correction pass on the P06.1 chat-provider proof harness of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<START_SHA>`.

P06.1-I1 built a sandbox harness in `proofs/stream-chat/` that tests Stream Chat's permission model against Nathan's development Stream application 1729640, with synthetic users only. P06.1-C1 corrected it offline after I1's review. C1's exact-head review, of the merge commit `e85bba0`, approved it, and left:

- **three should-fix findings:**
  - a FAIL observed in a case is lost when a later step of that case is interrupted;
  - T4-rest-unread can record HOLDS with A's own control failed;
  - RT2 and RT3 record HOLDS on any refusal, including input errors and outages;
- **seven nits,** numbered 4 to 10.

**You fix all ten, offline.** You make no Stream call. The first live use of your fixes, and of C1's, comes later, in P06.1-I2a.

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
git diff --stat e85bba0f054908a801b43e6f9d514b04f5fdbf78 HEAD -- proofs/stream-chat/   # must print nothing
```

The last command shows that the harness is unchanged since the reviewed head, so the review's line numbers still apply. If any check fails, stop and report.

Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`;
- the P06.1 brief, `docs/planning/p06-1-chat-provider-proof.md`: "Brief — P06.1" (owned paths, credential rules, the matrix quality rule and the acceptance checks) and "Sessions" (P06.1-C2 and I2a);
- the evidence record, `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md`, whole. Its section "Exact-head review of C1" is your work list, and "P06.1-C1 corrections" records the fixes you build on;
- the C1 prompt, `docs/ephemeral/2026-09-26-p06-1-c1-correction-prompt.md`, section 3: the rules C1's fixes follow, which still stand;
- `proofs/stream-chat/README.md` and the whole harness under `proofs/stream-chat/`.

## 3. The work

The work list is in the evidence record, under "Exact-head review of C1", "Findings, most severe first", numbered 1 to 10. Each item gives its `file:line`, a failure scenario and, for most, a suggested fix. Use the suggested fix unless you find a better one, and say why if you do.

1. **Finding 1: what a case observed survives an interruption.**
   - Every way a case can end records its row: a `GuardrailStop`, a `ClientSessionEnded` or any other exception, as a `RunStopped` already does through `_keep_case`. For a `GuardrailStop`, record the row, then re-raise.
   - The row keeps what the case observed before the interruption. A FAIL stays a FAIL; anything else becomes INCONCLUSIVE, with the interruption as its reason.
   - Each of the review's three scenarios gets a test: S2, S15, and the server replay in `_evaluate_case`.
   - In the third, a client success must not vanish with the stop. Either its undo is made, or the row records that it was not made, and why. Follow the README's rule on what may still run after each kind of stop, and say which you chose.
2. **Finding 2: T4-rest-unread.** Neither kind of HOLDS unless A's and B's own requests succeeded (`controls_ok`). "HOLDS (accepted, not applied)" also needs all three totals present. Otherwise the case is INCONCLUSIVE. Update README line 150.
3. **Finding 3: RT2 and RT3.** A refusal gives HOLDS only when it is attributable: an `auth`, `permission` or `feature` outcome. I1's recorded RT2 was `feature` (`400` code 18). An `input`, `not-found` or `other` refusal is INCONCLUSIVE, "refusal not attributable". Update README line 147.
4. **Nits 4 to 10,** as the review suggests:
   - **nit 4:** among the stop signals, a restore is retried only after a rate limit (HTTP 429 or Stream code 9). Correct the README's count of calls per journalled change;
   - **nit 5:** a feature-gated case whose production-phase request has no recorded answer is INCONCLUSIVE;
   - **nit 6:** where a command must send exactly one request, a reply with any other number of recorded requests has no answer. Check every caller of `_http_answer`;
   - **nit 7:** E5 is INCONCLUSIVE when A's stored user cannot be read;
   - **nit 8:** a second Ctrl-C inside `finish()` must not lose the results file;
   - **nit 9:** a restore whose removal was accepted but could not be verified is reported "not verified", not "not restored";
   - **nit 10:** the key-pattern redaction also covers `firebase_server_key`, `sqs_key` and `sns_key`, and any other credential key name in `getstream` 6.1.0's app settings model that the patterns miss.

   Fix each nit, or give a one-line reason for leaving it.
5. **The records.**
   - The README states each rule as the code now applies it: the verdict rules, the stop and restore rules, and the call counts.
   - In the evidence record, correct in place only a claim that was already false at C1's head, and mark it "(corrected in P06.1-C2)". Keep every recorded result as it was: a correction changes a claim about a result, never the result.

**Rules for every fix:**

- **A test for each fix.** Each finding and nit you fix gets an offline test that fails without the fix and passes with it. Say which test covers which item. Extend `checks/fix_reversals.py` so that it demonstrates your fixes as well as C1's 51.
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
4. The offline checks, with the README's commands: the unit tests (the counts at the start and at your head; C1 left 142), Ruff check and format, mypy, and `node --check` on `client/runner.cjs` and `client/error-info.cjs`.
5. `checks/fix_reversals.py`: its counts at the start (51 reversals) and at your head, with none "not demonstrated".
6. A secret scan over your whole diff: no secret, token, JWT-shaped string, API key or email address.

## 5. Owned paths, push and records

- **You may change:**
  - `proofs/stream-chat/**`, except the dependency files above and the committed baseline, `baseline/application-1729640-2026-09-25.json`;
  - `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md`, except these sections, each with everything under it: "Manager verification (App Manager 3, 25 September 2026)", "Exact-head review of I1 (25 September 2026)", "Manager verification (App Manager 3, 26 September 2026)" and "Exact-head review of C1 (26 September 2026)".
- **Nothing else**, including the brief, the ADRs, `apps/`, `services/`, `.github/` and every other document. Report any other change you think is needed.
- **Commit and push** your session branch. Don't open a pull request.
- **Your section of the evidence record,** "P06.1-C2 corrections", at its end:
  - the start SHA, your head and your branch;
  - for findings 1 to 3 and nits 4 to 10: fixed (`file:line` and its test) or left (the reason);
  - the records you corrected;
  - every check, with its exact results;
  - deviations and limits;
  - what I2a must know, in addition to C1's list: the rules that changed, and the fixes not yet exercised live.

## 6. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<START_SHA>`);
- your branch, head SHA and tree, and the changed paths;
- for findings 1 to 3 and nits 4 to 10: fixed (`file:line` and the test) or left (the reason);
- the records corrections;
- every check, with its exact results;
- deviations, limits, and what I2a must know.

Skipped or unavailable checks are not passes.

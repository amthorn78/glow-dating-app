# P06.1-C4 prompt — fourth correction pass: the I2b review's findings

- **Owner:** App Manager 5. Nathan starts this session manually and relays its report.
- **Revision 1, 27 September 2026.**
- **Durable brief:** [P06.1 brief](../planning/p06-1-chat-provider-proof.md), "Brief — P06.1" (owned paths, credential rules, matrix quality rule) and "Sessions" (P06.1-C4).
  - Work list: the [P06.1 evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md), "Exact-head review of I2b (27 September 2026)": the review's findings, verbatim; the manager's verification, which adds one requirement to nit 8; and the "Disposition".
- **Where the result goes:**
  - the session brings the harness README and the [architecture document](../architecture/chat-provider-permissions.md) into line with each change, and adds a section at the end of the evidence record, "P06.1-C4 corrections";
  - the manager adds its verification there and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v6: Opus 5.5, high.** Effort score 2.13 (confidence 0.85); rung probabilities low 0.00, medium 0.05, high 0.78, extra high 0.16, max 0.01, ultracode 0.00. Model probabilities Fable 5.1 0.01, Opus 5.5 0.99 (confidence 0.98). Sent 2026-09-27T13:37:56Z. Nathan picks the cell.
  - **Nathan's pick: Opus 5.5 at high**, started 27 September. This line was added after the prompt was given; the body Nathan pasted is unchanged.
- **Result:** verified by the manager and integrated by fast-forward at `c83bedf` (code head `b2b9a0b`) on 27 September; see the evidence record, "P06.1-C4 corrections" and the manager's verification under it.
- **No Dev Manager read is needed:** the prompt authorizes no credential use and no live provider action.
- **Stream variables** (OD-28): none are needed, and Nathan adds none. This session never calls Stream. The environment check reports any it finds by name.
- **It runs alone** (OD-29, the linear process). Its exact-head review follows and is P06.1's final delta review; the economics discovery comes after it.
- **Deletion condition:** prune after P06.1 closes and the evidence record and brief hold the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **implementation session for P06.1-C4**, the fourth correction pass on the P06.1 chat-provider proof harness of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<START_SHA>`.

P06.1 tests Stream's permission model against Nathan's development Stream application 1729640, with synthetic users only, using the sandbox harness in `proofs/stream-chat/`. P06.1-I2b, the last live session, added Stream Video and Feeds to it:

- a runner op through which a modified client sends a product request, with a path allowlist and a deny-list in code;
- the same scope in the server-side guard, and 18 cases;
- a scoped `configure --products video,feeds`, whose apply made the Video and Feeds lockdown, the proof's one lasting change.

Its exact-head review, of the merge commit `55b2238` (code head `ad89753`), approved it and left:

- **two should-fix findings:**
  - the runner's generic `call` op reaches Video and Feeds endpoints without the product op's allowlist or deny-list;
  - the lockdown's verification and its record cover only the client roles' grants;
- **eight nits,** numbered 3 to 10.

**You fix all ten, offline.** You make no Stream call. No live run remains in P06.1, so your fixes are first used live in a later phase.

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
3. Record `command -v node npm npx python3.12` and their versions. Expected: v24.19.0, 11.9.0 and Python 3.12.14, from `$HOME/.local/bin`.
4. Run the harness's commands in a clean process environment, as its README's "Install" and "Checks (offline)" sections show. Installs get the proxy and CA variables by reference, never printed.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2
git merge --ff-only <START_SHA>          # on your own session branch
git rev-parse HEAD                       # must print <START_SHA>
git diff --stat 55b22387e6478e4b7c8d58480108e4c7341c4564 HEAD -- proofs/stream-chat/ .github/   # must print nothing
```

The last command shows that the harness and the workflow are unchanged since the reviewed head, so the review's line numbers still apply. If any check fails, stop and report.

Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`;
- the P06.1 brief, `docs/planning/p06-1-chat-provider-proof.md`: "Brief — P06.1" (owned paths, credential rules, the matrix quality rule and the acceptance checks) and "Sessions" (P06.1-I2b, its review and P06.1-C4);
- the evidence record, `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md`:
  - "Exact-head review of I2b (27 September 2026)" is your work list: the findings, verbatim, the manager's verification and the "Disposition";
  - "P06.1-I2b" is the section whose claims you correct; its "Checks", "Deviations and limits" and "What P06.2 and the delta review must know" hold nits 5, 6, 9 and 10;
  - the earlier sections record the rules your fixes must keep;
- the I2b prompt, `docs/ephemeral/2026-09-27-p06-1-i2b-implementation-prompt.md`, section 5, for nit 6's count;
- `docs/architecture/chat-provider-permissions.md`, whole, and ADR 0003's "Consequences" (`docs/adr/0003-chat-display-rule.md`), for nit 7;
- `proofs/stream-chat/README.md` and the whole harness under `proofs/stream-chat/`.

## 3. The work

The review's findings are in the evidence record, under "Exact-head review of I2b", "Findings, most severe first", numbered 1 to 10. Each gives its `file:line`, a scenario and a suggested fix. Use the suggested fix unless you find a better one, and say why if you do. The requirements below are the manager's disposition, and they stand either way.

1. **Finding 1: nothing reaches Video or Feeds except through the product op's check.** Do this first.
   - In `client/runner.cjs`'s request interceptor, before the request is counted or sent, apply `productRefusal` to the request's method, path as sent, body and query whenever:
     - its host is the Video or the Feeds host (`PRODUCT_HOSTS.video`, `PRODUCT_HOSTS.feeds`); or
     - its path is under `/api/v2/video` or `/api/v2/feeds` once letter case, percent-encoding and dot segments are normalized. Resolve the URL as axios will send it, against `config.baseURL` when it is relative.

     This applies whatever op sent the request. A product path whose form as sent differs from its normalized form is refused outright; otherwise the product op's check decides. A refused request is neither sent nor counted, and the reply's error kind is `refused`, as for the product op.
   - `validate` in `glow_stream_proof/matrix.py` refuses a step that could reach a product path through any op but `product`:
     - a `call` on the client naming one of its generic request methods (`get`, `post`, `put`, `patch`, `delete`, or any other that takes a URL);
     - a `get` op whose path is under a product prefix.
   - Tests:
     - one that drives the real runner through the review's scenario and requires the error kind `refused`, not `budget`. The scenario: a REST user set, then a `call` on the client's `post` to `/api/v2/video/call/default/x/join` with `ring: true`, with a zero budget and an unreachable proxy so that nothing can leave the machine;
     - the same for a non-canonical product path, a product host and the `get` op;
     - one that sends each of the 18 product cases' steps through the real runner and shows that the new check refuses none of them;
     - a reversal for the interceptor check and one for the `validate` rule.
2. **Finding 2: the lockdown's verification and its record cover every role and setting.**
   - `products.verify` also compares, for each available product, every role's grants other than the client roles' with the committed products baseline, `baseline/video-feeds-1729640-2026-09-27.json`. It also compares each call type's settings and notification settings, and each feed group's recorded fields, as the chat check compares the application settings with its own baseline.
     - Compare what `baseline_record` keeps, field by field. If a kept field is volatile, such as a timestamp, leave it out and say which.
     - A role or a scope present on one side only is a difference. The client roles must still read `[]`.
   - The scoped `configure --apply` record keeps the full after-state, in `baseline_record`'s shape, scanned like every other record.
   - The fake products model the baseline's other roles and settings, so that preflight, the end of a run and the dry-run `configure` still verify offline with no difference. A test shows that a changed `call_member` grant, a changed call-type setting and a changed feed group are each reported.
   - **The records.** Correct the README sentence "that Stream changes only the roles named is documented and verified by the re-read after the apply, not assumed", and any sentence in the architecture document's section 5 that says or implies the same. They must say:
     - the re-read of 27 September compared the client roles' grants only;
     - that the other roles and the settings are unchanged rests on Stream's documentation, not on that re-read;
     - the corrected verification compares them at the next live use.
3. **Nit 3: the deny-list ignores letter case.** In both tables, `client/product-op.cjs` and `glow_stream_proof/products.py`:
   - a denied key matches in any letter case;
   - a denied-true key's value matches `true` in any letter case (`"True"`, `"TRUE"`), as well as the boolean.

   The test that drives both tables with node covers the new rows and requires the same reason from each.
4. **Nit 4: nothing scanned is not a HOLDS.**
   - When the request of a no-leak case carried every one of its leak terms, nothing is left to scan. A success (2xx) is then INCONCLUSIVE, with a reason that says so, never HOLDS (filtered). A refusal keeps its own rule.
   - Show, from the case definitions, that no current case has every leak term carried by its own request, as the review found. No recorded verdict changes.
5. **Nit 8: a failed configuration write still leaves its record, and nothing is sent after a signal.**
   - When a `PUT` in the scoped `configure --apply` fails mid-plan, the command still writes its record: the steps applied so far, the failure and the after-state. The general `configure --apply` shares `_apply`; give it the same treatment.
   - **The manager's addition to the review's fix:** a charge or limit signal is raised inside `ServerApi.raw`, and the ledger refuses no later request.
     - So the re-read runs only when no charge or limit signal was met. Decide that from the ledger's recorded signals, not only from the exception's type.
     - After a signal, write the record from what is known, marked "after-state not read: a charge or limit signal was met", and send no request.
     - The command exits non-zero either way.
   - Tests:
     - a mid-plan non-2xx without a signal: the record holds the re-read;
     - a mid-plan 402 and a mid-plan 429: the fake counts no request after the signal, and the record is still written.
6. **Nit 7: the architecture document's existence-oracle row.**
   - In section 3, "Stream channel and message IDs are random and opaque, never derived from Glow's account IDs or names, and never shown to users (ADR 0003's consequences for P06.2)" becomes the document's own design constraint (DM-05 finding 5 (a) allows one). Mark it open for P06.2, as channel naming is.
   - ADR 0003 says this of user IDs only. Section 8's bullet already states the constraint without the attribution.
7. **Nits 5, 6, 9 and 10: the record.** Correct each in place, in I2b's own subsections of "P06.1-I2b" (from "Environment" to "What P06.2 and the delta review must know"), and mark each "(corrected in P06.1-C4; the I2b review's nit N)":
   - **nit 5:** in "Checks" item 4, mypy checked 53 source files, not 55;
   - **nit 6:** in "Deviations and limits", "Fourteen live commands against the plan's eleven" is not derivable.
     - The live table has 15 rows. Section 5 of the I2b prompt names thirteen commands, the reserve rerun included; check that count against the prompt yourself.
     - The two beyond them are command 3, a scoped dry run before run 1 besides the one before the apply, and command 8, `record-products-baseline`, which made no network call.
     - The rerun and the closing checks are in the plan;
   - **nit 9:** the deviation bullet on `93390ce` also says that the commit changed FD-feed's step body. Its custom note no longer carries the Feeds marker (`{fd_text}` became `feed of {A}`), so FD-read's disclosure question stays about A's activity;
   - **nit 10:** EO-channel's row and "What P06.2 and the delta review must know" say that no record holds the `sync` pair's two normalized answers. They stayed in I2b's local results file, which was not kept. Do not reconstruct them. The architecture document's section 3 says that "`sync` is an oracle too" rests on that one recorded observation.

   Keep every recorded result as it was.
8. **Optional:** one README sentence saying that the existence-oracle cases, not the disclosure rule, hold the question of whether an echoed identifier signals existence (the review's assessment note).

**Not in this pass:** `checks/run_plan.py`'s mid-session reading, a recorded limit; no live run remains in P06.1. If you find anything else, report it with its class. Fix it here only if it could do one of these, and then with a test and a reversal:

- create a false HOLDS, MEETS or "ended";
- lose an observed FAIL or DOES NOT MEET;
- send a request after a charge or limit signal;
- let a change escape the guard or the deny-lists;
- let the scoped `configure` apply anything outside the two products.

**Rules for every fix:**

- **A test for each fix.** Each finding and nit you fix in code gets an offline test that fails without the fix and passes with it. Say which test covers which item. Add a reversal to `checks/fix_reversals.py` for each.
- **Every reversal fails for the right reason.** Report, for every new reversal, whether its tests fail on the expected assertion or error, or by Ctrl-C by design. A reversal whose edited file does not compile or import is not demonstrated.
- **No live calls.** Tests use fakes or the harness's offline simulation.
- **The credential rules stand.** The secret never reaches a client process or any output. Keep the client environment's allowlist, the runner's refusal, redaction and the leak checks.
- **The matrix quality rule stands.** Never weaken a verdict rule to make a test pass. Where a fix changes a verdict rule, state the new rule in the README.
- **The guard, the deny-lists and the configure gates stand.** No fix widens what the harness may send. The two tables stay in agreement, with the deny-list checked first.
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
   - the unit tests, with the counts at the start and at your head (I2b left 503);
   - Ruff check and format;
   - mypy, with its file count;
   - `node --check` on each `client/*.cjs`;
   - `checks/run_plan.py` with an empty ledger.
5. `checks/fix_reversals.py`, in a scratch copy outside the tree: its counts at the start (342) and at your head, with none "not demonstrated", and each new reversal's failure reason.
6. A secret scan over your whole diff: no secret, token, API key or email address, and no JWT-shaped string other than the redaction test's fabricated input.
7. The Foundation run on your final head, if your tools can read it: each job's conclusion, "Stream proof checks" included. If they cannot, say so. Re-run or dispatch nothing.

## 5. Owned paths, push and records

- **You may change:**
  - `proofs/stream-chat/**`, except the dependency files above and the two committed baselines, `baseline/application-1729640-2026-09-25.json` and `baseline/video-feeds-1729640-2026-09-27.json`;
  - `docs/architecture/chat-provider-permissions.md`: the passages this prompt's section 3 names (the document's sections 3 and 5, and any sentence finding 2 makes inaccurate). Leave its status line and its "Review" columns as the manager set them;
  - `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md`: your new section at its end, and the in-place corrections this prompt's section 3 lists. Every other part stays byte-identical, in particular "Manager verification of I2b (App Manager 4, 27 September 2026)" and "Exact-head review of I2b (27 September 2026)", each with everything under it, and every earlier review and verification.
- **Nothing else,** including the brief, the ADRs, `.github/`, `apps/`, `services/` and every other document. Report any other change you think is needed.
- **Commit and push** your session branch. Don't open a pull request.
- **Your section of the evidence record,** "P06.1-C4 corrections", at its end:
  - the start SHA, your head and your branch;
  - for findings 1 and 2 and nits 3 to 10: fixed (`file:line` and its test) or left (the reason);
  - the records you corrected;
  - every check, with its exact results;
  - deviations and limits;
  - what the final delta review and P06.2 must know: the rules that changed, and the fixes not yet exercised live.

## 6. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<START_SHA>`);
- the environment check;
- your branch, head SHA and tree, and the changed paths;
- for findings 1 and 2 and nits 3 to 10: fixed (`file:line` and the test) or left (the reason);
- the records corrections;
- every check, with its exact results;
- deviations, limits, and what the final delta review must know.

Skipped or unavailable checks are not passes.

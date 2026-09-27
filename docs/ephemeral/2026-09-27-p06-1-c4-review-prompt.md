# P06.1-C4 review prompt — exact-head review of the fourth correction pass, P06.1's final delta review

- **Owner:** App Manager 5. Nathan starts this session manually and relays its report.
- **Revision 1, 27 September 2026.**
- **Durable brief:** [P06.1 brief](../planning/p06-1-chat-provider-proof.md), "Sessions" (P06.1-C4 and its review).
  - Evidence: the [P06.1 evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md): "Exact-head review of I2b (27 September 2026)" with the manager's verification and disposition (C4's work list), "P06.1-C4 corrections" (C4's own record) and the manager's verification of C4 under it; the [architecture document](../architecture/chat-provider-permissions.md).
- **Where the result goes:** the manager records the verified review in the evidence record, under a new heading "Exact-head review of C4". The outcome goes into the brief's "Sessions". It is P06.1's final delta review (the brief's review plan); the economics discovery and the close-out follow it.
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v6: Opus 5.5, extra high.** Effort score 3.11 (confidence 0.86); rung probabilities low 0.00, medium 0.00, high 0.05, extra high 0.79, max 0.16, ultracode 0.00. Model probabilities Fable 5.1 0.19, Opus 5.5 0.81 (confidence 0.63). Sent 2026-09-27T19:29:19Z. Nathan picks the cell.
- **Result:** changes required, with one should-fix finding in the correction class and four nits; recorded in the evidence record, "Exact-head review of C4", with the manager's verification and disposition. P06.1-C5 follows. The relay did not name Nathan's pick. This line was added after the prompt was given; the body Nathan pasted is unchanged.
- **No Dev Manager read is needed:** the prompt authorizes no credential use and no live provider action.
- **Stream variables** (OD-28): none are needed, and Nathan adds none. This session never calls Stream. The environment check reports any it finds by name.
- **It runs alone** (OD-29, the linear process). The economics discovery comes after it.
- **Deletion condition:** prune after P06.1 closes and the evidence record and brief hold the result.

**Manager:** before giving this prompt to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **review session for P06.1-C4** of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<RECORDS_COMMIT>`. Your review is P06.1's final delta review: the last review of the proof's code before its pull request merges.

P06.1 tests Stream's permission model against Nathan's development Stream application 1729640, with synthetic users only, using the sandbox harness in `proofs/stream-chat/`. Its last live session, P06.1-I2b, added Stream Video and Feeds. I2b's exact-head review, of the merge commit `55b2238`, approved it and left two should-fix findings and eight nits. P06.1-C4, an offline correction pass, then did this:

- **the ten items:**
  - finding 1: a request check in the runner's request interceptor, so that nothing reaches Video or Feeds except through the product op's allowlist and deny-list, whatever op sends the request, with path normalization (letter case, percent-encoding, dot segments) and a `validate` rule;
  - finding 2: every non-client role's grants, each call type's settings and each feed group's recorded fields compared with the committed products baseline, and the full before- and after-state in the scoped `configure` record;
  - nit 3: deny-lists that ignore letter case; nit 4: a no-leak success with nothing left to scan is INCONCLUSIVE; nit 8: a `configure --apply` record that is always written, with nothing sent after a charge or limit signal (with the manager's addition: the signal is read from the ledger);
  - nits 5, 6, 7, 9 and 10: record corrections;
- **what its own review sub-agent found** in its first fix: a blocking gap (a percent-escape that is not UTF-8 switched the new check off), a should-fix in nit 8's fix, and ten further items (Stream's three hosts only, `https:` only, no `Host` or forwarding header, no redirect, JSON inside a query value read, and others);
- **one test change** (`b2b9a0b`) that keeps an I2b reversal demonstrable.

The unit tests went from 503 to 543 and the fix reversals from 342 to 378. C4 made no Stream call.

- **You review one exact head:** `c83bedf1f812cf454d4f16b5dc741c5d944749d9`, C4's head, which the manager integrated by fast-forward. Its code head is `b2b9a0b`: C4's code commits are `634dc56`, `919a383`, `112011f` and `b2b9a0b` (the last changes a test only), and its other commits change only Markdown.
- **Your scope is C4's change:** the whole of `git diff 2c2d450883937191c55905bd49fe7b0af0a186e8 HEAD`, and the harness where C4's change depends on it. The harness before C4 was reviewed at `55b2238`; between `55b2238` and `2c2d450` the manager changed only Markdown records. The manager's later records are Markdown too, and you read them at `<RECORDS_COMMIT>`.
- **What comes after this review.** Report every finding with its severity, as usual. A blocking finding, or a should-fix finding that could create a false HOLDS, MEETS or "ended", lose an observed FAIL or DOES NOT MEET, send a request after a charge or limit signal, let a request or a change escape the runner's new check, the guard or the deny-lists, or let the scoped `configure` apply anything outside the two products, gets another offline correction pass before P06.1 closes. Everything else goes into the records. For each finding, say whether it falls in one of those classes.
- Nathan started you manually and will relay your report to the manager (App Manager 5). You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - Keep scratch work outside the repository, or in its ignored paths (`.venv/`, `node_modules/`, `.work/`).
- **Never:**
  - dump the environment;
  - connect to Stream, a database, HDE, Railway or any other provider. Run none of the harness's live commands: `baseline`, `probe-products`, `configure` (even as a dry run, with or without `--products`), `run`, `verify-clean`, `cleanup` or `restore`;
  - run `playwright install`, `eas` or `migrate`.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` should be absent (OD-28): `for n in STREAM_APP_ID STREAM_API_KEY STREAM_API_SECRET; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, report its name first in your report, never read or use its value, and continue.
3. Record `command -v node npm npx python3.12` and their versions. Expected: v24.19.0, 11.9.0 and Python 3.12.14, from `$HOME/.local/bin`.
4. Run the harness's commands in a clean process environment, as its README's "Install" and "Checks (offline)" sections show. Installs get the proxy and CA variables by reference, never printed.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach c83bedf1f812cf454d4f16b5dc741c5d944749d9
git rev-parse HEAD                      # must print c83bedf1f812cf454d4f16b5dc741c5d944749d9
git merge-base --all origin/main HEAD   # expected: one line, 0f45e648099b415217938c25d7369164c0101def
git merge-base --is-ancestor HEAD <RECORDS_COMMIT> && echo "records build on the head"
git diff --stat 2c2d450883937191c55905bd49fe7b0af0a186e8 HEAD   # expected: 17 files, 2381 insertions, 204 deletions
```

If any check fails, stop and report.

Classify three times, as root `AGENTS.md` requires. The trusted base policy runs outside the candidate tree, every run uses the same policy file, and every SHA is a full one (a short SHA fails closed):

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
python3 -I "$policy_dir/change_scope.py" --base 55b22387e6478e4b7c8d58480108e4c7341c4564 --head "$head" --merge-base
python3 -I "$policy_dir/change_scope.py" --base "$head" --head <RECORDS_COMMIT> --merge-base
git diff --name-only 55b22387e6478e4b7c8d58480108e4c7341c4564 "$head" | grep -v '\.md$' | grep -v '^proofs/stream-chat/'
```

- **The first run** is the head against `main`. Expected: `"full": true`.
- **The second run** is everything after the last reviewed code head, I2b's merge commit. Expected: `"full": true`. The last command must print nothing: every non-Markdown change since then is under `proofs/stream-chat/`. Anything else is code this review would not cover: stop and report it.
- **The third run** is everything after the head. Expected: `ordinary-docs-only`. Anything else means a non-Markdown change landed after the head: stop and report it.

Then read, completely.

**At `HEAD`:**

- root `AGENTS.md` and `CLAUDE.md`;
- the C4 prompt, `docs/ephemeral/2026-09-27-p06-1-c4-correction-prompt.md` (revision 1): what the session was asked to do, including its owned paths, the parts of the evidence record it had to leave byte-identical, and its rules for every fix;
- the evidence record, `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md`:
  - "Exact-head review of I2b (27 September 2026)": the review's findings, the manager's verification (its addition to nit 8's fix) and the disposition, C4's work list;
  - "P06.1-C4 corrections", C4's own record;
  - the five sentences C4 corrected in place in I2b's section, each marked "(corrected in P06.1-C4; the I2b review's …)";
- `docs/architecture/chat-provider-permissions.md`, whole;
- `docs/adr/0003-chat-display-rule.md`, its "Conditions (DM-02 B7)" and "Revisit when";
- `proofs/stream-chat/README.md`, including "Verdict rules", "The guard", "The Video and Feeds lockdown", "What this proof does not show" and "Limits";
- the whole of `git diff 2c2d450883937191c55905bd49fe7b0af0a186e8 HEAD`, and the parts of the harness it depends on.

**At `<RECORDS_COMMIT>`,** with `git show <RECORDS_COMMIT>:<path>`:

- the P06.1 brief's "Brief — P06.1" (owned paths, credential rules, the matrix quality rule) and "Sessions" (P06.1-C4 and its review), in `docs/planning/p06-1-chat-provider-proof.md`;
- the evidence record's last section: the manager's verification of C4 and its dispositions.

## 3. What to review

The focus areas are in order of risk.

1. **Nothing reaches Video or Feeds except through the product op's check** (finding 1 and C4's own review).
   - The runner's request check (`client/runner.cjs`: `productRequestRefusal`, `sentURL`, `readableBody`, `headerNames`, and its place in the request interceptor, before the budget). Can any request an op can make reach a Video or Feeds endpoint without passing `productRefusal`? Consider:
     - the URL's form: letter case, percent-encoding (invalid UTF-8, double encoding, an encoded slash), backslashes, dot and empty segments;
     - the host: a product host, an alias, a trailing dot, a port, user information;
     - headers: `Host`, forwarding headers, method or URL overrides;
     - a redirect, a per-request adapter, `proxy` or `socketPath`, a relative URL, or a changed base URL.
   - The normalization (`client/product-op.cjs` `normalizedPath` and `isProductPath`; the Python mirror `products.normalized_path` and `is_product_path`): do the two agree on every input, and does the test that compares them cover the inputs that matter?
   - **Letter case, a deliberate difference from the prompt's wording** (C4's record, finding 1): case is folded to find a product path but kept in the comparison with the normalized form, so an ID may hold capitals and a miscased fixed segment is refused by the allowlist. Is that sound: could a miscased path reach an endpoint Stream would route?
   - `matrix.validate` (`_product_reach`, `CLIENT_URL_METHODS`): is the list of the client's URL-taking methods complete for stream-chat 9.53.0, so that no matrix step can send an arbitrary URL through another method?
   - **The residuals C4 recorded as README limits:** the WebSocket's host, a per-request `proxy` or `socketPath`, the fetch adapter, two-level nested JSON in a query value, and the headers `X-HTTP-Method-Override` and `X-Original-URL`. Is each unreachable by every matrix step and harness op, as recorded?
   - **Chat requests:** could the new check refuse a request a chat case needs, which would give a false INCONCLUSIVE at the next live use? What does `maxRedirects: 0` on every request change? It is the one C4 change without a test (C4's deviation): is an offline test feasible?
2. **Nothing is sent after a charge or limit signal** (nit 8, with the manager's addition). In `cli.py` (`_apply`, `_Applied`, `_apply_recorded`, `_read_after`) and both `configure --apply` paths, after a 402, a code 99, a 429, a code 9 or charge wording on any step or on the re-read itself, and after a Ctrl-C:
   - is no further request sent?
   - is the record always written, and scanned?
   - does the stop reach `main` with the right exit?
   - is the signal decided from the ledger's recorded signals, as the manager required?
3. **No false HOLDS, MEETS or "ended."** Nit 4's rule (`proof_run.py` `_disclosure`, `matrix.no_leak_verdict`): a success with nothing left to scan is INCONCLUSIVE, a refusal keeps its own rule, and no current case changes verdict. Could any verdict path now read HOLDS where it should not?
4. **The baseline comparison** (finding 2): `products.verify`, `baseline_differences`, `_changed_paths`, `recorded_products`.
   - Does it compare everything the committed baseline records about the configuration, and nothing volatile?
   - At the harness's next live use, could it pass a changed role or setting, or stop preflight on a difference that is not the configuration's?
   - Does the scoped `configure` record keep the full before- and after-state?
5. **The fake products and the tests.** The fake now models the committed baseline (`tests/fake_products.py`), and tests that asserted the old, guessed plan now assert the live nine-`PUT` plan. Does that weaken any test, a verdict test above all? Do the new tests test what they claim, and would they fail if the fix were broken another way?
6. **Nit 3:** both deny-list tables agree, in any letter case, with the same reasons.
7. **The fix reversals.** Run `checks/fix_reversals.py` (C4 and the manager reported 378, none "not demonstrated"). Does each of the 36 C4 entries really remove its fix and fail for the right reason? Check also the I2b entry that `b2b9a0b` keeps demonstrable.
8. **Records.** This is a full-scope review: never skip a finding because its file ends in `.md`.
   - C4's section of the evidence record agrees with the code and its commits. So do the five in-place corrections in I2b's section. Every other part of the record at `HEAD` is byte-identical to `2c2d450`.
   - The architecture document: its sections 3 and 5 as C4 corrected them, and its section 4 against ADR 0003's conditions, both as the manager updated them at `47fe797`. Are they consistent, and do they claim anything the runs did not show?
   - The README's rules and limits match the code.
9. **The manager's dispositions,** in its verification of C4 at `<RECORDS_COMMIT>`. Assess each, and say where you disagree and why.
10. **Scope.** Only the 17 paths C4 names changed. No dependency file, lock, `.npmrc`, `pyproject.toml` dependency, committed baseline or workflow changed. Every file has mode 100644, and there are no symlinks.

**Out of scope:**

- re-running anything live;
- the rest of the harness, except where C4's change depends on it;
- governing Markdown, which the Dev Manager reads;
- the economics discovery, which follows this review;
- the app outside the harness, and anything in HDE.

## 4. Checks to run

Report the exact commands and results.

1. `git diff --check 2c2d450883937191c55905bd49fe7b0af0a186e8 HEAD`.
2. The three classifications above.
3. The installs from the locks, with the README's commands, in clean processes.
4. The offline checks, with the README's commands: the unit tests (C4 reported 543), Ruff check and format, mypy, `node --check` on the four `.cjs` files, and `checks/run_plan.py` with an empty ledger ("run plan: fits").
5. `checks/fix_reversals.py` (C4 reported 378, none "not demonstrated"): each C4 entry's failure reason, and anything more you need to test a fix's test.
6. A secret scan over the whole of `git diff 2c2d450883937191c55905bd49fe7b0af0a186e8 HEAD`: no secret, token, API key or email address.
7. Hosted CI:
   - push run 356 ([36336214481](https://github.com/amthorn78/glow-dating-app/actions/runs/36336214481)) on the code head `b2b9a0b`;
   - the latest pull-request run of PR27 on a manager-branch commit that contains the head.

   Confirm from each run's jobs that "Stream proof checks" ran, not skipped, and passed.
8. Anything else you judge necessary, offline only.

## 5. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<RECORDS_COMMIT>`);
- the head you reviewed (`git rev-parse HEAD`) and the three classification outputs;
- **verdict:** "approve" (C4's change and its records are sound, and P06.1 can close on them) or "changes required";
- **findings,** most severe first. For each: severity (**blocking**, **should fix** or **nit**), `file:line`, the concrete failure scenario, a suggested fix, and whether it falls in one of the classes that need another correction pass before P06.1 closes;
- for the I2b review's ten items and the items C4's own review found: confirmed fixed, or not, with the reason;
- for each of the manager's dispositions: agree, or disagree with the reason;
- the areas you reviewed with no findings;
- every check you ran, with its exact result;
- limits: anything you could not check, and why.

Skipped or unavailable checks are not passes. Change nothing in the repository, on GitHub or in Notion.

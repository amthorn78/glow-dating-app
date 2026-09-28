# P06.1-C5 review prompt — exact-head review of the fifth correction pass, P06.1's final delta review

- **Owner:** App Manager 5. Nathan starts this session manually and relays its report.
- **Revision 1, 28 September 2026.**
- **Durable brief:** [P06.1 brief](../planning/p06-1-chat-provider-proof.md), "Sessions" (P06.1-C5 and its review).
  - Evidence: the [P06.1 evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md): "Exact-head review of C4 (27 September 2026)" with the manager's verification and disposition (C5's work list), "P06.1-C5 corrections" (C5's own record) and the manager's verification of C5 under it.
- **Where the result goes:** the manager records the verified review in the evidence record, under a new heading "Exact-head review of C5". The outcome goes into the brief's "Sessions". It is P06.1's final delta review; the economics discovery and the close-out follow it.
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v6: Opus 5.5, extra high.** Effort score 2.95 (confidence 0.84); rung probabilities low 0.00, medium 0.00, high 0.13, extra high 0.78, max 0.09, ultracode 0.00. Model probabilities Fable 5.1 0.06, Opus 5.5 0.94 (confidence 0.88). Sent 2026-09-28T00:47:02Z. Nathan picks the cell.
- **No Dev Manager read is needed:** the prompt authorizes no credential use and no live provider action.
- **Stream variables** (OD-28): none are needed, and Nathan adds none. This session never calls Stream. The environment check reports any it finds by name.
- **It runs alone** (OD-29, the linear process). The economics discovery comes after it.
- **Deletion condition:** prune after P06.1 closes and the evidence record and brief hold the result.

**Manager:** before giving this prompt to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **review session for P06.1-C5** of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<RECORDS_COMMIT>`. Your review is P06.1's final delta review: the last review of the proof's code before its pull request merges.

P06.1 tests Stream's permission model against Nathan's development Stream application 1729640, with synthetic users only, using the sandbox harness in `proofs/stream-chat/`. P06.1-C4, the fourth correction pass, made the runner apply the product op's check to every request to Video or Feeds, whatever op sends it. C4's exact-head review, of `c83bedf`, asked for changes:

- **one should-fix finding,** in the correction class: `matrix.validate` did not refuse every stream-chat method whose arguments reach a request's configuration or path, and the README's recorded limits rested on it doing so;
- **four nits:** `maxRedirects: 0` had no test; an ADR's wording (the manager's, done); a failed record write after a signal lost the stop's exit code; one test of the ledger rule showed less than its name.

P06.1-C5, an offline correction pass, then did this:

- **finding 1:** `validate` refuses every `call` step outside an explicit allowlist of (target, method, maximum positional arguments), and the reminder methods always; and, **the manager's addition,** the runner refuses five request-rewriting headers on every request, whatever op sent it;
- **nits 2, 4 and 5:** an offline test of `maxRedirects: 0`; a failed record write after a signal keeps the signal's stop (exit 3); two variants of the ledger test in which an ordinary error replaces the stop;
- **what it found itself, or its own review found:** header names are now read as they are sent (trimmed, lower-cased, an underscore as a hyphen); `validate` refuses a method that is not a name and arguments that are not a list; and, after a signal, the ledger's signal decides the exit (3) whatever replaced its stop, except a Ctrl-C.

The unit tests went from 543 to 570 and the fix reversals from 378 to 391. C5 made no Stream call.

- **You review one exact head:** `1a5f58aec87cacfdd1dc32c893467f8f00e9ac7e`, C5's head, which the manager integrated by fast-forward. Its code head is `11b5771`: C5's code commits are `1e65ace`, `fc489d9` and `11b5771`, and its other commits change only Markdown.
- **Your scope is C5's change:** the whole of `git diff 438d047046e275e2a781937cc7f8e51f2b1a0bf6 HEAD`, and the harness where C5's change depends on it. The harness before C5 was reviewed at `c83bedf`; between `c83bedf` and `438d047` the manager changed only Markdown records. The manager's later records are Markdown too, and you read them at `<RECORDS_COMMIT>`.
- **What comes after this review.** Report every finding with its severity, as usual. A blocking finding, or a should-fix finding that could create a false HOLDS, MEETS or "ended", lose an observed FAIL or DOES NOT MEET, send a request after a charge or limit signal, let a request or a change escape the runner's check, the guard or the deny-lists, or let the scoped `configure` apply anything outside the two products, gets another offline correction pass before P06.1 closes. Everything else goes into the records. For each finding, say whether it falls in one of those classes.
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
3. The pinned toolchain is in `$HOME/.local/bin`: node v24.19.0, npm 11.9.0 and Python 3.12.14. The default PATH may find another node first. Put `$HOME/.local/bin` first on PATH in every process you run the harness in, then record `command -v node npm npx python3.12` and their versions. Say what the default PATH finds if it differs.
4. Run the harness's commands in a clean process environment, as its README's "Install" and "Checks (offline)" sections show. Installs get the proxy and CA variables by reference, never printed.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach 1a5f58aec87cacfdd1dc32c893467f8f00e9ac7e
git rev-parse HEAD                      # must print 1a5f58aec87cacfdd1dc32c893467f8f00e9ac7e
git merge-base --all origin/main HEAD   # expected: one line, 0f45e648099b415217938c25d7369164c0101def
git merge-base --is-ancestor HEAD <RECORDS_COMMIT> && echo "records build on the head"
git diff --stat 438d047046e275e2a781937cc7f8e51f2b1a0bf6 HEAD   # expected: 9 files, 1260 insertions, 37 deletions
```

If any check fails, stop and report.

Classify three times, as root `AGENTS.md` requires. The trusted base policy runs outside the candidate tree, every run uses the same policy file, and every SHA is a full one (a short SHA fails closed):

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
python3 -I "$policy_dir/change_scope.py" --base c83bedf1f812cf454d4f16b5dc741c5d944749d9 --head "$head" --merge-base
python3 -I "$policy_dir/change_scope.py" --base "$head" --head <RECORDS_COMMIT> --merge-base
git diff --name-only c83bedf1f812cf454d4f16b5dc741c5d944749d9 "$head" | grep -v '\.md$' | grep -v '^proofs/stream-chat/'
```

- **The first run** is the head against `main`. Expected: `"full": true`.
- **The second run** is everything after the last reviewed code head, C4's head. Expected: `"full": true`. The last command must print nothing: every non-Markdown change since then is under `proofs/stream-chat/`. Anything else is code this review would not cover: stop and report it.
- **The third run** is everything after the head. Expected: `ordinary-docs-only`. Anything else means a non-Markdown change landed after the head: stop and report it.

Then read, completely.

**At `HEAD`:**

- root `AGENTS.md` and `CLAUDE.md`;
- the C5 prompt, `docs/ephemeral/2026-09-27-p06-1-c5-correction-prompt.md` (revision 1): what the session was asked to do, including its owned paths, the parts of the evidence record it had to leave byte-identical, and its rules for every fix;
- the evidence record, `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md`:
  - "Exact-head review of C4 (27 September 2026)": the review's report, the manager's verification and the disposition, C5's work list;
  - "P06.1-C5 corrections", C5's own record;
  - the one bullet C5 corrected in place in "P06.1-C4 corrections", marked "(corrected in P06.1-C5; the C4 review's finding 1 …)";
- `proofs/stream-chat/README.md`, including "The guard", "Nothing else reaches Video or Feeds", the scoped `configure --apply` bullets and "Limits" with "Added in P06.1-C5";
- the whole of `git diff 438d047046e275e2a781937cc7f8e51f2b1a0bf6 HEAD`, and the parts of the harness it depends on;
- in stream-chat 9.53.0 and axios 1.20.0 as installed (`node_modules/`), what you need to test the allowlist and the header reading.

**At `<RECORDS_COMMIT>`,** with `git show <RECORDS_COMMIT>:<path>`:

- the P06.1 brief's "Brief — P06.1" (owned paths, credential rules, the matrix quality rule) and "Sessions" (P06.1-C5 and its review), in `docs/planning/p06-1-chat-provider-proof.md`;
- the evidence record's last section: the manager's verification of C5 and its dispositions.

## 3. What to review

The focus areas are in order of risk.

1. **No matrix step can pass a request option or steer a path** (finding 1: `glow_stream_proof/matrix.py`, `CALL_ALLOWLIST`, `REMINDER_METHODS`, `_call_refusal`, and their place in `validate`).
   - Is the allowlist exactly what the matrix uses, and does its test keep it so?
   - For every allowlisted (target, method) at its count, does each argument reach only the request's body, payload or an encoded path segment in stream-chat 9.53.0? Could any reach the request's configuration, or put an unencoded caller value into a path? Check `queryChannels` at three arguments, whose fourth is state options.
   - Are the reminder methods the only directly callable methods that put a caller value into a path unencoded?
   - The harness's own code also sends `call` ops, which `validate` does not see (`proof_run.py`, `mechanisms.py`, `i2a.py`). Does any of them pass a request option or an unencoded path value?
2. **The runner's header refusal and header-name reading** (`client/runner.cjs`: `REWRITING_HEADERS`, `sentHeaderName`, `headerNames`, `productRequestRefusal`).
   - Can a refused header reach the wire in a form the check does not see: a spelling, a non-string key, an `AxiosHeaders` instance, a per-method or `common` section, a header merged after the interceptor, or a value that smuggles a header?
   - Does the new reading refuse any header a chat case sends? That would give a false INCONCLUSIVE at the next live use.
   - **The residuals C5 recorded:** other routing headers (`X-Forwarded-Prefix`, `X-Forwarded-Proto`, `X-Original-Method`), and the non-header options (a per-request `proxy` or `socketPath`, the fetch adapter or HTTP/2, JSON nested two levels deep). Is each unreachable by every matrix step and harness op, as recorded?
3. **What reaches `main` after a signal, and the record** (nit 4 and C5's own review: `glow_stream_proof/cli.py`, `_Applied.stop`, `ended_on`, `finish` and `_write_record`, in both `configure --apply` paths).
   - After a 402, a code 99, a 429, a code 9 or charge wording, is no further request sent, whatever replaced the stop, and does the command exit 3 unless a Ctrl-C replaced it?
   - Without a signal, is the exit what it was before C5 (1 for a step Stream refused, the error's own path otherwise)? Could any ordinary failure now exit 3, or a signal exit otherwise? The ledger's signals are kept in memory per process: confirm.
   - When the record's write raises, is the record's failure reported and never lost, with the stop kept? The manager noticed that a Ctrl-C during the write itself, after a signal, leaves as the signal's stop (exit 3) with the Ctrl-C chained. Is that sound?
4. **The tests.** `CallAllowlistValidationTest`, `RequestHeaderTest`, `MaxRedirectsTest` (does it test the runner's real interceptor?), `RecordWriteAfterASignalTest` and the two nit 5 variants in `ConfigureRecordTest`. Do they test what they claim, and would they fail if the fix were broken another way?
5. **The fix reversals.** Run `checks/fix_reversals.py` (C5 and the manager reported 391, none "not demonstrated"). Does each of the 13 C5 entries really remove its fix and fail for the right reason? "C4 re-check 1" now fails only its Ctrl-C test: is the signal case it used to show still demonstrated by another reversal?
6. **Records.** This is a full-scope review: never skip a finding because its file ends in `.md`.
   - C5's section of the evidence record agrees with the code and its commits. So does the one in-place correction in C4's section. Every other part of the record at `HEAD` is byte-identical to `438d047`.
   - The README's rules and limits match the code.
7. **The manager's dispositions,** in its verification of C5 at `<RECORDS_COMMIT>`, including the two proposals it did not take (an allowlist of header names in the runner, and the argument counts enforced in the runner at run time). Assess each, and say where you disagree and why.
8. **Scope.** Only the 9 paths C5 names changed. No dependency file, lock, `.npmrc`, `pyproject.toml` dependency, committed baseline or workflow changed. Every file has mode 100644, and there are no symlinks.

**Out of scope:**

- re-running anything live;
- the rest of the harness, except where C5's change depends on it;
- governing Markdown, which the Dev Manager reads;
- the economics discovery, which follows this review;
- the app outside the harness, and anything in HDE.

## 4. Checks to run

Report the exact commands and results.

1. `git diff --check 438d047046e275e2a781937cc7f8e51f2b1a0bf6 HEAD`.
2. The three classifications above.
3. The installs from the locks, with the README's commands, in clean processes.
4. The offline checks, with the README's commands: the unit tests (C5 reported 570), Ruff check and format, mypy, `node --check` on the four `.cjs` files, and `checks/run_plan.py` with an empty ledger ("run plan: fits").
5. `checks/fix_reversals.py` (C5 reported 391, none "not demonstrated"): each C5 entry's failure reason, and anything more you need to test a fix's test.
6. A secret scan over the whole of `git diff 438d047046e275e2a781937cc7f8e51f2b1a0bf6 HEAD`: no secret, token, API key or email address.
7. Hosted CI:
   - push run 371 ([36360951436](https://github.com/amthorn78/glow-dating-app/actions/runs/36360951436)) on the code head `11b5771`;
   - the latest pull-request run of PR27 on a manager-branch commit that contains the head.

   Confirm from each run's jobs that "Stream proof checks" ran, not skipped, and passed.
8. Anything else you judge necessary, offline only.

## 5. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<RECORDS_COMMIT>`);
- the head you reviewed (`git rev-parse HEAD`) and the three classification outputs;
- **verdict:** "approve" (C5's change and its records are sound, and P06.1 can close on them) or "changes required";
- **findings,** most severe first. For each: severity (**blocking**, **should fix** or **nit**), `file:line`, the concrete failure scenario, a suggested fix, and whether it falls in one of the classes that need another correction pass before P06.1 closes;
- for the C4 review's items and the items C5 found itself or its own review found: confirmed fixed, or not, with the reason;
- for each of the manager's dispositions: agree, or disagree with the reason;
- the areas you reviewed with no findings;
- every check you ran, with its exact result;
- limits: anything you could not check, and why.

Skipped or unavailable checks are not passes. Change nothing in the repository, on GitHub or in Notion.

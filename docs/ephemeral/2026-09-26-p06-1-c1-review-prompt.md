# P06.1-C1 review prompt — exact-head review of the correction pass

- **Owner:** App Manager 3. Nathan starts this session manually and relays its report.
- **Revision 1, 26 September 2026.**
- **Durable brief:** [P06.1 brief](../planning/p06-1-chat-provider-proof.md), "Sessions" (P06.1-C1, its review, and I2a).
  - Evidence: the [P06.1 evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md): "Exact-head review of I1" (the findings C1 had to fix), "P06.1-C1 corrections" (C1's own record) and the manager's verification under it.
- **Where the result goes:** the manager records the verified review in the evidence record, under a new heading "Exact-head review of C1". The outcome goes into the brief's "Sessions".
- **Reasoning level.** Neither reading gates anything, and Nathan picks.
  - Manager: extra high.
  - TypeSafe v4: high (score 2.29, P(high) 0.71, P(extra high) 0.29), with no ultracode flag (P(single session) 0.52).
- **No Dev Manager read is needed:** the prompt authorizes no credential use and no live provider action.
- **No Stream variables** (OD-28): this session never calls Stream.
- **It runs alone** (OD-29, the linear process).
- **Deletion condition:** prune after P06.1 closes and the evidence record and brief hold the result.

**Manager:** before giving this prompt to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **review session for P06.1-C1** of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<RECORDS_COMMIT>`.

P06.1-I1 built a sandbox harness in `proofs/stream-chat/` that tests Stream Chat's permission model against Nathan's development Stream application 1729640, with synthetic users only. Its exact-head review required changes: two blocking findings, seven more and 17 nits. P06.1-C1 corrected the harness offline:

- it reports findings 1 to 8 and 15 of the 17 nits fixed, each with an offline test, and nits 14 and 17 left with reasons;
- it corrected I1's evidence claims in place;
- the unit tests went from 49 to 142, and a script shows that 51 fixes each have a test that fails without them;
- finding 9 and finding 6's new G2 and S10 setups belong to P06.1-I2a, a later live session.

The manager verified C1's branch and integrated it with a merge commit.

- **You review one exact head:** `e85bba0f054908a801b43e6f9d514b04f5fdbf78`, that merge commit.
  - Its first parent, `93781c8`, is the manager branch before the merge. Its second parent, `9e018c6`, is C1's head; C1's code head is `be46319`.
  - The merge brought C1's 29 files: 28 under `proofs/stream-chat/` and the evidence record.
- **Your scope is C1's change:** the whole of `git diff HEAD^1 HEAD`, and the harness as it now stands.
  - The rest of PR26's code is out of scope: I1's harness as reviewed at `9ff600f`, except where C1 changed it, and the flake fix at `8b8b1bd`, reviewed separately.
  - Later commits are Markdown-only manager records, which you read at `<RECORDS_COMMIT>`.
- Nathan started you manually and will relay your report to the manager (App Manager 3). You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - Keep scratch work outside the repository, or in its ignored paths (`.venv/`, `node_modules/`, `.work/`).
- **Never:**
  - dump the environment;
  - connect to Stream, a database, HDE, Railway or any other provider. Run none of the harness's live commands: `baseline`, `configure` (even as a dry run), `run`, `verify-clean`, `cleanup` or `restore`;
  - run `playwright install`, `eas` or `migrate`.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY`, `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. `STREAM_APP_ID`, `STREAM_API_KEY` and `STREAM_API_SECRET` should be absent (OD-28): `for n in STREAM_APP_ID STREAM_API_KEY STREAM_API_SECRET; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, report its name first in your report, never read or use its value, and continue.
3. Record `command -v node npm npx python3.12` and their versions. Expected: v24.19.0, 11.9.0 and Python 3.12.14, from `$HOME/.local/bin`.
4. Run the harness's commands in a clean process environment, as its README's "Install" and "Checks (offline)" sections show. Installs get the proxy and CA variables by reference, never printed.

## 2. Start gate

```bash
git fetch origin claude/stoic-carson-66gdig main
git switch --detach e85bba0f054908a801b43e6f9d514b04f5fdbf78
git rev-parse HEAD                      # must print e85bba0f054908a801b43e6f9d514b04f5fdbf78
git rev-parse HEAD^2                    # must print 9e018c67858ccafa5f84dd75bcef51dcc3dfb49a
git merge-base --all origin/main HEAD   # expected: one line, 0f45e648099b415217938c25d7369164c0101def
git merge-base --is-ancestor HEAD <RECORDS_COMMIT> && echo "records build on the head"
git diff --stat HEAD^1 HEAD             # expected: 29 files, 4674 insertions, 591 deletions
```

If any check fails, stop and report.

Classify three times, as root `AGENTS.md` requires. The trusted base policy runs outside the candidate tree, and every run uses the same policy file:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
python3 -I "$policy_dir/change_scope.py" --base 8b8b1bdfe5c403686efb44070807dd003a466964 --head "$head" --merge-base
python3 -I "$policy_dir/change_scope.py" --base "$head" --head <RECORDS_COMMIT> --merge-base
git diff --name-only 8b8b1bdfe5c403686efb44070807dd003a466964 "$head" | grep -v '\.md$' | grep -v '^proofs/stream-chat/'
```

- **The first run** is the head against `main`. Expected: `"full": true`.
- **The second run** is everything after the last reviewed code head, the flake fix. Expected: `"full": true`. The last command must print nothing: every non-Markdown change since then is under `proofs/stream-chat/`. Anything else is code this review would not cover: stop and report it.
- **The third run** is everything after the head. Expected: `ordinary-docs-only`. Anything else means a non-Markdown change landed after the head: stop and report it.

Then read, completely.

**At `HEAD`:**

- root `AGENTS.md` and `CLAUDE.md`;
- the C1 prompt, `docs/ephemeral/2026-09-26-p06-1-c1-correction-prompt.md`: what the session was asked to do;
- the evidence record, `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md`, whole. Its section "Exact-head review of I1" defines each finding. Its section "P06.1-C1 corrections" is C1's own record;
- `proofs/stream-chat/README.md`, including its new "Verdict rules";
- the whole of `git diff HEAD^1 HEAD`, and the harness as a whole.

**At `<RECORDS_COMMIT>`,** with `git show <RECORDS_COMMIT>:<path>`:

- the P06.1 brief's "Brief — P06.1" (owned paths, credential rules, the matrix quality rule) and "Sessions" (P06.1-C1 and I2a), in `docs/planning/p06-1-chat-provider-proof.md`;
- the evidence record's last section, the manager's verification of C1.

## 3. What to review

The focus areas are in order of risk.

1. **No silent pass.** A verdict may HOLD only on Stream's attributable refusal, with a successful control, under the matrix quality rule.
   - Check how each verdict gets its status and code (`_answer_of`, `_http_answer`, `_ws_answer`) and every verdict function and procedure case in `proof_run.py` and `matrix.py`.
   - Can any path still reach HOLDS on an SDK error, a local throw, a missing response, the wrong request's response or a stale reply? The "request under test is the last HTTP request" rule: does any command send more than one request, so that the last is not the one under test?
   - Findings 1, 4, 5 and 7 as the I1 review defined them: is each fully fixed?
2. **Temporary changes and cleanup (finding 2 and nits 4, 5, 12, 13).**
   - The journal, the order of enable and `try`, `finish()`, the retries, the exit codes and the handling of `RunStopped`, `GuardrailStop` and Ctrl-C. Could any path leave a temporary change in place without a non-zero exit and a clear message? Could a restore failure hide a guardrail stop, or the reverse?
   - After a charge-signal stop, the run still restores and re-reads (C1's choice). Is that safe within the guardrails?
   - Could restore or cleanup touch data the run did not create, including the polls and user groups listed at preflight and the `deleted-user-…` system user?
   - Is the cleanup reserve right for the worst case?
3. **The new server calls,** first used live in I2a: the channel re-read by `cid` (`POST /api/v2/chat/channels`), `POST /api/v2/polls/query` and `GET /api/v2/usergroups`.
   - Do their request shapes match Stream's documentation and the installed `getstream` 6.1.0 source?
   - If the live answer differs from the fakes, does the harness fail closed ("not verified", exit 4), never open?
   - The override-removal re-read rule: a removal counts as proven only for keys the re-read showed while the override was set. Is it sound?
4. **Reply matching (finding 5).** The reader thread, buffering, timeouts, session termination and the INCONCLUSIVE marking: races, deadlocks, lost or misattributed lines.
5. **Preflight (finding 3).** Exactly one dashboard administrator, created in the recorded minute. Does it fail closed in every case, and record no identifier?
6. **Credentials.** The protections stand: the client environment's allowlist, the runner's refusal, redaction and the leak checks. Check the new `client/error-info.cjs`, every new output path, and the key-pattern redaction (nit 8) for misses.
7. **The tests.** Do they test the harness's logic rather than the fakes' behavior? Run `checks/fix_reversals.py`: does each reversal really remove its fix, and does each test fail for the right reason? Name any fix whose test would still pass with the fix broken in another way.
8. **The nits left.** Are the reasons for leaving nits 14 and 17 sound?
9. **Records.** The in-place corrections are accurate and marked "(corrected in P06.1-C1)". I1's recorded results are unchanged, and the manager's sections are byte-identical to `93781c8`. The README's verdict rules match the code. This is a full-scope review: never skip a finding because its file ends in `.md`.
10. **Scope.** Only `proofs/stream-chat/**` and the evidence record changed. No dependency file, `pyproject.toml` dependency, `.npmrc` or committed baseline changed. Every file has mode 100644, and there are no symlinks.

**Out of scope:**

- live behavior, which I2a exercises first;
- finding 9 and finding 6's new G2 and S10 setups, which belong to I2a;
- the flake fix and the rest of the app;
- anything in HDE.

## 4. Checks to run

Report the exact commands and results.

1. `git diff --check HEAD^1 HEAD`.
2. The three classifications above.
3. The installs from the locks, with the README's commands, in clean processes.
4. The offline checks, with the README's commands: the unit tests (C1 reported 142), Ruff check and format, mypy, and `node --check` on both `.cjs` files.
5. `checks/fix_reversals.py` (C1 reported 51 of 51), and anything more you need to test a fix's test.
6. A secret scan over the whole of `git diff HEAD^1 HEAD`.
7. Anything else you judge necessary, offline only.

The manager reads hosted CI on the reviewed head, so you need not wait for it.

## 5. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<RECORDS_COMMIT>`);
- the head you reviewed (`git rev-parse HEAD`) and the three classification outputs;
- **verdict:** "approve" (the corrected harness is a sound base for P06.1-I2a's live runs) or "changes required";
- **findings,** most severe first. For each: severity (**blocking**, **should fix** or **nit**), `file:line`, the concrete failure scenario and a suggested fix;
- for each of the I1 review's findings 1 to 8, and each nit C1 claims fixed: confirmed, or not, with the reason;
- the areas you reviewed with no findings;
- every check you ran, with its exact result;
- limits: anything you could not check, and why.

Skipped or unavailable checks are not passes. Change nothing in the repository, on GitHub or in Notion.

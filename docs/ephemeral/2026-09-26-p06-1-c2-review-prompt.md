# P06.1-C2 review prompt — exact-head review of the second correction pass

- **Owner:** App Manager 3. Nathan starts this session manually and relays its report.
- **Revision 1, 26 September 2026.**
- **Durable brief:** [P06.1 brief](../planning/p06-1-chat-provider-proof.md), "Sessions" (P06.1-C2, its review, and I2a).
  - Evidence: the [P06.1 evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md): "Exact-head review of C1 (26 September 2026)" (the work C2 had to do), "P06.1-C2 corrections" (C2's own record) and the manager's verification and decisions under it.
- **Where the result goes:** the manager records the verified review in the evidence record, under a new heading "Exact-head review of C2". The outcome goes into the brief's "Sessions".
- **Reasoning level.** Neither reading gates anything, and Nathan picks.
  - Manager: extra high, without ultracode. The change is one bounded diff, and the session may use subagents as it needs.
  - TypeSafe v4: extra high (score 2.70, P(extra high) 0.60, P(high) 0.35, P(max) 0.05), with an ultracode flag: P(single session) 0.40.
  - **Used: extra high,** without ultracode. Nathan started this session on 26 September. This line was added after the prompt was given; the body Nathan pasted is unchanged.
- **No Dev Manager read is needed:** the prompt authorizes no credential use and no live provider action.
- **No Stream variables** (OD-28): this session never calls Stream.
- **It runs alone** (OD-29, the linear process). I2a comes after it.
- **Deletion condition:** prune after P06.1 closes and the evidence record and brief hold the result.

**Manager:** before giving this prompt to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **review session for P06.1-C2** of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<RECORDS_COMMIT>`.

P06.1-I1 built a sandbox harness in `proofs/stream-chat/` that tests Stream Chat's permission model against Nathan's development Stream application 1729640, with synthetic users only. Two offline correction passes followed. C1's exact-head review approved C1, and left three should-fix findings and seven nits, numbered 1 to 10. P06.1-C2 fixed them offline:

- it reports all ten fixed, each with an offline test that fails without its fix;
- its own review sub-agent found four more problems, which it also fixed;
- the unit tests went from 142 to 202, and `checks/fix_reversals.py` now demonstrates 99 fixes: C1's 51 and C2's 48;
- it corrected three earlier claims in the evidence record, and the README's rules.

The manager verified C2's branch and integrated it with a merge commit.

- **You review one exact head:** `63e922fb86f214b99627748cbb53387baa6dd748`, that merge commit.
  - Its first parent, `5fc3bea`, is the manager branch before the merge. Its second parent, `ba36311`, is C2's head; C2's code head is `f1c670b`.
  - The merge brought C2's 18 files: 17 under `proofs/stream-chat/` and the evidence record.
- **Your scope is C2's change:** the whole of `git diff HEAD^1 HEAD`, and the harness as it now stands.
  - The rest of PR26's code is out of scope: the harness as C1's review saw it at `e85bba0`, except where C2 changed it, and the flake fix at `8b8b1bd`.
  - Later commits are Markdown-only manager records, which you read at `<RECORDS_COMMIT>`.
- **Two manager decisions** are recorded under the manager's verification of C2:
  - C2's rule for the undo of a client success after an interrupted control stands.
  - In RT2 and RT3, a `feature` refusal will get the matrix's "REFUSED (feature off; not a permission error)" verdict, not HOLDS. The next session that changes the harness makes that change, before any live run. Don't report the current HOLDS as a finding. If you disagree with the decision, say so under limits, with your reason. Review the rest of finding 3's change as usual.
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
git switch --detach 63e922fb86f214b99627748cbb53387baa6dd748
git rev-parse HEAD                      # must print 63e922fb86f214b99627748cbb53387baa6dd748
git rev-parse HEAD^2                    # must print ba36311ae86e7c9ded4f6d6c5ae66acdfb517150
git merge-base --all origin/main HEAD   # expected: one line, 0f45e648099b415217938c25d7369164c0101def
git merge-base --is-ancestor HEAD <RECORDS_COMMIT> && echo "records build on the head"
git diff --stat HEAD^1 HEAD             # expected: 18 files, 2490 insertions, 198 deletions
```

If any check fails, stop and report.

Classify three times, as root `AGENTS.md` requires. The trusted base policy runs outside the candidate tree, and every run uses the same policy file:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
python3 -I "$policy_dir/change_scope.py" --base e85bba0f054908a801b43e6f9d514b04f5fdbf78 --head "$head" --merge-base
python3 -I "$policy_dir/change_scope.py" --base "$head" --head <RECORDS_COMMIT> --merge-base
git diff --name-only e85bba0f054908a801b43e6f9d514b04f5fdbf78 "$head" | grep -v '\.md$' | grep -v '^proofs/stream-chat/'
```

- **The first run** is the head against `main`. Expected: `"full": true`.
- **The second run** is everything after the last reviewed code head, C1's merge commit. Expected: `"full": true`. The last command must print nothing: every non-Markdown change since then is under `proofs/stream-chat/`. Anything else is code this review would not cover: stop and report it.
- **The third run** is everything after the head. Expected: `ordinary-docs-only`. Anything else means a non-Markdown change landed after the head: stop and report it.

Then read, completely.

**At `HEAD`:**

- root `AGENTS.md` and `CLAUDE.md`;
- the C2 prompt, `docs/ephemeral/2026-09-26-p06-1-c2-correction-prompt.md`: what the session was asked to do;
- the evidence record, `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md`, whole. Its section "Exact-head review of C1 (26 September 2026)" defines each finding and nit. Its section "P06.1-C2 corrections" is C2's own record;
- `proofs/stream-chat/README.md`, including "Verdict rules" and the end-of-run rules;
- the whole of `git diff HEAD^1 HEAD`, and the harness as a whole.

**At `<RECORDS_COMMIT>`,** with `git show <RECORDS_COMMIT>:<path>`:

- the P06.1 brief's "Brief — P06.1" (owned paths, credential rules, the matrix quality rule) and "Sessions" (P06.1-C2 and I2a), in `docs/planning/p06-1-chat-provider-proof.md`;
- the evidence record's last section: the manager's verification of C2 and its decisions.

## 3. What to review

The focus areas are in order of risk.

1. **No silent pass.** A verdict may HOLD only on Stream's attributable refusal, with a successful control, under the matrix quality rule, and an observed FAIL is never lost.
   - Every verdict rule C2 changed: the one-request rule in `_http_answer`, T4-rest-unread, RT2 and RT3 (apart from the decided feature label), the feature-gated cases' production phase, S10, E5 and S14 with an unreadable stored user, and G1.
   - Can any path reach HOLDS without an attributable refusal and a successful control? Can any path turn an observed FAIL into anything else?
2. **Interrupted cases (finding 1).** `_observe`, `_interrupted_row`, `run_matrix`'s branches and every place a procedure keeps what it has observed.
   - Is each observation kept at the right point? Can a row kept by one case reach another case, or be recorded twice, or be lost?
   - Does a FAIL survive every kind of interruption: a guardrail stop, a failed restore, an ended client session, a harness error and Ctrl-C?
   - The undo of a client success after an interruption: does it follow the README's rule, and can it send a request after a charge signal?
3. **The end of the run.** `finish()`'s retry rule and `is_rate_limit`; the "not verified" removal (nit 9, and C2's own review point 3); the early results write and the second Ctrl-C in `cli.py`; the atomic `.work` writes; `_progress_quietly`; E5's restore of A's role.
   - Could any path leave a temporary change in place without a non-zero exit and a clear message?
   - Could a restore failure, a progress failure or a write failure hide a guardrail stop, or the reverse, so that cleanup runs after a charge signal?
   - Are the README's call counts right for the worst case, and does the cleanup reserve still cover it?
4. **Credentials.** The protections stand: the client environment's allowlist, the runner's refusal, redaction and the leak checks.
   - The new `_key` suffix: does it hide a value the leak checks must see, including a marker a client could place under such a key?
   - Every new output path, including the early results write and the notes it adds: does each go through the same redaction as the final results?
5. **The tests.** Do they test the harness's logic rather than the fakes' behavior? Run `checks/fix_reversals.py`: does each reversal really remove its fix, and does each test fail for the right reason? Name any fix whose test would still pass with the fix broken in another way.
6. **Records.** The three in-place corrections are accurate and marked "(corrected in P06.1-C2)". No recorded result changed, and the four sections the C2 prompt protects are byte-identical to `5fc3bea`. The README's rules match the code. This is a full-scope review: never skip a finding because its file ends in `.md`.
7. **Scope.** Only `proofs/stream-chat/**` and the evidence record changed. No dependency file, `pyproject.toml` dependency, `.npmrc` or committed baseline changed. Every file has mode 100644, and there are no symlinks.

**Out of scope:**

- live behavior, which I2a exercises first;
- finding 9 of the I1 review and finding 6's new G2 and S10 setups, which belong to I2a;
- the RT2 and RT3 feature label, which the manager has decided;
- the flake fix and the rest of the app;
- anything in HDE.

## 4. Checks to run

Report the exact commands and results.

1. `git diff --check HEAD^1 HEAD`.
2. The three classifications above.
3. The installs from the locks, with the README's commands, in clean processes.
4. The offline checks, with the README's commands: the unit tests (C2 reported 202), Ruff check and format, mypy, and `node --check` on both `.cjs` files.
5. `checks/fix_reversals.py` (C2 reported 99 of 99), and anything more you need to test a fix's test.
6. A secret scan over the whole of `git diff HEAD^1 HEAD`.
7. Anything else you judge necessary, offline only.

The manager reads hosted CI on the reviewed head, so you need not wait for it.

## 5. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<RECORDS_COMMIT>`);
- the head you reviewed (`git rev-parse HEAD`) and the three classification outputs;
- **verdict:** "approve" (the corrected harness is a sound base for P06.1-I2a's live runs) or "changes required";
- **findings,** most severe first. For each: severity (**blocking**, **should fix** or **nit**), `file:line`, the concrete failure scenario and a suggested fix;
- for each of the C1 review's findings 1 to 3 and nits 4 to 10, and each of the four points C2's own review raised: confirmed, or not, with the reason;
- the areas you reviewed with no findings;
- every check you ran, with its exact result;
- limits: anything you could not check, and why, and any disagreement with the manager's decisions.

Skipped or unavailable checks are not passes. Change nothing in the repository, on GitHub or in Notion.

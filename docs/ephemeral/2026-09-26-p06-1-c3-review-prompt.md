# P06.1-C3 review prompt — exact-head review of the third correction pass

- **Owner:** App Manager 3. Nathan starts this session manually and relays its report.
- **Revision 1, 26 September 2026.**
- **Durable brief:** [P06.1 brief](../planning/p06-1-chat-provider-proof.md), "Sessions" (P06.1-C3, its review, and I2a).
  - Evidence: the [P06.1 evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md): "Exact-head review of C2 (26 September 2026)" (the work C3 had to do, and the manager's disposition), "P06.1-C3 corrections" (C3's own record) and the manager's verification and decisions under it.
- **Where the result goes:** the manager records the verified review in the evidence record, under a new heading "Exact-head review of C3". The outcome goes into the brief's "Sessions".
- **Reasoning level.** Neither reading gates anything, and Nathan picks.
  - Manager: extra high.
  - TypeSafe v4: extra high (score 2.54, P(extra high) 0.50, P(high) 0.48, P(max) 0.02), with no ultracode flag, narrowly (P(single session) 0.53).
- **No Dev Manager read is needed:** the prompt authorizes no credential use and no live provider action.
- **No Stream variables** (OD-28): this session never calls Stream.
- **It runs alone** (OD-29, the linear process). I2a comes after it.
- **Deletion condition:** prune after P06.1 closes and the evidence record and brief hold the result.

**Manager:** before giving this prompt to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **review session for P06.1-C3** of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<RECORDS_COMMIT>`.

P06.1-I1 built a sandbox harness in `proofs/stream-chat/` that tests Stream Chat's permission model against Nathan's development Stream application 1729640, with synthetic users only. Three offline correction passes followed. C2's exact-head review approved C2, and left two should-fix findings and eight nits, numbered 1 to 10. The manager also decided a change to the RT2 and RT3 verdicts. P06.1-C3 made that change and fixed all ten offline:

- it reports each item fixed, with an offline test that fails without its fix;
- its own review sub-agent found four more problems, which it also fixed. The largest: a charge or limit signal is now recorded where its stop is raised, in the ledger the server client and every client session share, so no later exception can hide it from the end of the run;
- the unit tests went from 202 to 252, and `checks/fix_reversals.py` now demonstrates 147 fixes, printing each one's failure reason, and counts an edit that does not compile as not demonstrated;
- it corrected five earlier claims in the evidence record, and the README's rules.

The manager verified C3's branch and integrated it with a merge commit.

- **You review one exact head:** `8c1a8c08d77052a86cfc70fc38cb830eb641438a`, that merge commit.
  - Its first parent, `8881339`, is the manager branch before the merge. Its second parent, `b40acd7`, is C3's head; C3's code head is `a5e2221`.
  - The merge brought C3's 19 files: 18 under `proofs/stream-chat/` and the evidence record.
- **Your scope is C3's change:** the whole of `git diff HEAD^1 HEAD`, and the harness where C3's change depends on it. The rest of the harness was reviewed at `63e922f`; the flake fix at `8b8b1bd` is out of scope. Later commits are Markdown-only manager records, which you read at `<RECORDS_COMMIT>`.
- **What delays I2a.** Report every finding with its severity, as usual. The manager has decided that after this review only a blocking finding, or a should-fix finding that could create a false HOLDS, lose an observed FAIL or send a request after a charge or limit signal, delays I2a's live runs; everything else goes into I2a's offline first step or the final delta review. For each finding, say whether it falls in one of those three classes.
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
git switch --detach 8c1a8c08d77052a86cfc70fc38cb830eb641438a
git rev-parse HEAD                      # must print 8c1a8c08d77052a86cfc70fc38cb830eb641438a
git rev-parse HEAD^2                    # must print b40acd7f8c4198f8205040ca1bc3119addc6093a
git merge-base --all origin/main HEAD   # expected: one line, 0f45e648099b415217938c25d7369164c0101def
git merge-base --is-ancestor HEAD <RECORDS_COMMIT> && echo "records build on the head"
git diff --stat HEAD^1 HEAD             # expected: 19 files, 2723 insertions, 175 deletions
```

If any check fails, stop and report.

Classify three times, as root `AGENTS.md` requires. The trusted base policy runs outside the candidate tree, and every run uses the same policy file:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
python3 -I "$policy_dir/change_scope.py" --base 63e922fb86f214b99627748cbb53387baa6dd748 --head "$head" --merge-base
python3 -I "$policy_dir/change_scope.py" --base "$head" --head <RECORDS_COMMIT> --merge-base
git diff --name-only 63e922fb86f214b99627748cbb53387baa6dd748 "$head" | grep -v '\.md$' | grep -v '^proofs/stream-chat/'
```

- **The first run** is the head against `main`. Expected: `"full": true`.
- **The second run** is everything after the last reviewed code head, C2's merge commit. Expected: `"full": true`. The last command must print nothing: every non-Markdown change since then is under `proofs/stream-chat/`. Anything else is code this review would not cover: stop and report it.
- **The third run** is everything after the head. Expected: `ordinary-docs-only`. Anything else means a non-Markdown change landed after the head: stop and report it.

Then read, completely.

**At `HEAD`:**

- root `AGENTS.md` and `CLAUDE.md`;
- the C3 prompt, `docs/ephemeral/2026-09-26-p06-1-c3-correction-prompt.md`: what the session was asked to do;
- the evidence record, `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md`: its section "Exact-head review of C2 (26 September 2026)", which defines each item and holds the manager's disposition, and "Manager verification of C2", which holds the RT2 and RT3 decision; its section "P06.1-C3 corrections", C3's own record; and every claim C3 corrected in place, marked "(corrected in P06.1-C3)";
- `proofs/stream-chat/README.md`, including "Verdict rules", the budget guardrails and the end-of-run rules;
- the whole of `git diff HEAD^1 HEAD`, and the parts of the harness it depends on.

**At `<RECORDS_COMMIT>`,** with `git show <RECORDS_COMMIT>:<path>`:

- the P06.1 brief's "Brief — P06.1" (owned paths, credential rules, the matrix quality rule) and "Sessions" (P06.1-C3 and I2a), in `docs/planning/p06-1-chat-provider-proof.md`;
- the evidence record's last section: the manager's verification of C3 and its decisions.

## 3. What to review

The focus areas are in order of risk.

1. **Nothing is sent after a charge or limit signal** (finding 2 and C3's own review point 1).
   - The signal record: each place a charge or limit signal can be met, and whether each records it before its stop is raised. Does any production code path build a stop for such a signal without recording it?
   - Every path from a recorded signal to the end of the run: the next case, the undo of a client success, S15's unset, the cleanup and the configuration re-read. Can any request other than the journal's restores and the configuration re-read follow a signal?
   - Can an exception, a second stop, a Ctrl-C or a failed write lose the signal, or make `cmd_run` or `finish()` miss it?
2. **No silent pass.** A verdict may HOLD only on Stream's attributable refusal, with a successful control of the same request, under the matrix quality rule.
   - RT2 and RT3: the `feature` verdict; the control, which must be the same request by a member allowed to make it; and how its own events are kept out of the windows searched for the marker.
   - Nit 5: a command that records more than one request, in the feature-on and production phases.
   - Nit 8: E5 and S14 when A's stored user cannot be read.
3. **An observed FAIL is never lost.** Finding 1, and the row RT3 keeps before its control. Can any C3 change turn an observed FAIL into anything else?
4. **The fix reversals.** The anchored patterns, the compile and import check, the check that every test the table names exists, and the failure reasons it prints. Run `checks/fix_reversals.py`: does each C3 reversal really remove its fix, and fail for the right reason? Name any fix whose test would still pass with the fix broken in another way.
5. **Records.** The five in-place corrections are accurate and marked. No recorded result changed, and the six sections the C3 prompt protects are byte-identical to `e5180ab`. The README's rules match the code. This is a full-scope review: never skip a finding because its file ends in `.md`.
6. **Scope.** Only `proofs/stream-chat/**` and the evidence record changed. No dependency file, `pyproject.toml` dependency, `.npmrc` or committed baseline changed. Every file has mode 100644, and there are no symlinks.

**Out of scope:**

- live behavior, which I2a exercises first;
- finding 9 of the I1 review and finding 6's new G2 and S10 setups, which belong to I2a;
- the rest of the harness, except where C3's change depends on it;
- the flake fix and the rest of the app;
- anything in HDE.

## 4. Checks to run

Report the exact commands and results.

1. `git diff --check HEAD^1 HEAD`.
2. The three classifications above.
3. The installs from the locks, with the README's commands, in clean processes.
4. The offline checks, with the README's commands: the unit tests (C3 reported 252), Ruff check and format, mypy, and `node --check` on both `.cjs` files.
5. `checks/fix_reversals.py` (C3 reported 147, none "not demonstrated"), each C3 reversal's failure reason, and anything more you need to test a fix's test.
6. A secret scan over the whole of `git diff HEAD^1 HEAD`.
7. Anything else you judge necessary, offline only.

The manager reads hosted CI on the reviewed head, so you need not wait for it.

## 5. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<RECORDS_COMMIT>`);
- the head you reviewed (`git rev-parse HEAD`) and the three classification outputs;
- **verdict:** "approve" (the corrected harness is a sound base for P06.1-I2a's live runs) or "changes required";
- **findings,** most severe first. For each: severity (**blocking**, **should fix** or **nit**), `file:line`, the concrete failure scenario, a suggested fix, and whether it could create a false HOLDS, lose an observed FAIL or send a request after a charge or limit signal;
- for the RT2 and RT3 change, the C2 review's findings 1 and 2 and nits 3 to 10, and the four points C3's own review raised: confirmed, or not, with the reason;
- the areas you reviewed with no findings;
- every check you ran, with its exact result;
- limits: anything you could not check, and why, and any disagreement with the manager's decisions.

Skipped or unavailable checks are not passes. Change nothing in the repository, on GitHub or in Notion.

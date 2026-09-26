# P06.1-I2a review prompt — exact-head review of the revocation and safety slice

- **Owner:** App Manager 3. Nathan starts this session manually and relays its report.
- **Revision 1, 26 September 2026.**
- **Durable brief:** [P06.1 brief](../planning/p06-1-chat-provider-proof.md), "Sessions" (P06.1-I2a, its review, and I2b).
  - Evidence: the [P06.1 evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md): "Exact-head review of C3 (26 September 2026)" (the items I2a's first step had to fix, and the manager's disposition), "P06.1-I2a" (I2a's own record) and the manager's verification and decisions under it.
- **Where the result goes:** the manager records the verified review in the evidence record, under a new heading "Exact-head review of I2a". The outcome goes into the brief's "Sessions".
- **Model and reasoning level** (OD-10, OD-30). Neither reading gates anything, and Nathan picks.
  - **Manager: Fable 5.1, extra high,** decided before TypeSafe's readings. The review covers about 8,800 new lines of harness code: a guard for destructive provider calls, new stop and cleanup paths, seven revocation families, an existence oracle and the S15 mapping. Its verdicts become product decisions, and I2b will use its guard live. That is a review of a large new system whose soundness is not yet established, where the most capable model is most likely to change the outcome. Extra high rather than max: on Fable a lower level often matches a higher one on Opus, and the review is offline. The closest precedent, the I1 review, ran at max on Opus.
  - **TypeSafe v4:** extra high (score 2.75, P(extra high) 0.71, P(high) 0.27, P(max) 0.02). It raises its ultracode flag (P(single session) 0.16; shape `broad_verification`, 0.64). The manager does not recommend ultracode: it is one change, and the session can split the review across subagents itself.
  - **TypeSafe m1:** Fable 5.1, by the narrowest margin (P(most capable) 0.51, confidence 0.02).
- **No Dev Manager read is needed:** the prompt authorizes no credential use and no live provider action.
- **No Stream variables** (OD-28): this session never calls Stream.
- **It runs alone** (OD-29, the linear process). I2b comes after it.
- **Deletion condition:** prune after P06.1 closes and the evidence record and brief hold the result.

**Manager:** before giving this prompt to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **review session for P06.1-I2a** of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<RECORDS_COMMIT>`.

P06.1 tests Stream Chat's permission model against Nathan's development Stream application 1729640, with synthetic users only, using the sandbox harness in `proofs/stream-chat/`. Three offline correction passes, each with its exact-head review, made the harness ready for live use. P06.1-I2a then added the revocation and safety cases and ran them live:

- **step 1, offline:** the C3 review's six nits and one gap; a guard, in code, that confines every change the harness asks of Stream to the run's own data; closing checks that see application-wide settings; and signals handled by kind;
- **step 2, offline:** seven mechanisms (member removal, a channel ban, hide, freeze, per-user token revocation, deactivation and a hard delete), each judged on reads, the open subscription, token reuse and the member's own writes, and several more case groups: tokens on two devices, an outage injected in the process, the S15 mapping, pin and archive, invites, a dozen client endpoints the I1 matrix never tried, an existence oracle, and new setups for G2 and S10;
- **an independent check,** by a fresh sub-agent, before the first live call: 2 blocking findings, 7 more and 7 nits, all fixed;
- **two live runs.** Run 1 stopped before any case: C1's reply matching, at its first live use, ended a client session, because a channel command's `id` replaced the command's own. The session fixed that offline and used its one reserve rerun for all 114 cases;
- the unit tests went from 252 to 393, and `checks/fix_reversals.py` now demonstrates 242 fixes.

The manager verified I2a's branch and integrated it with a merge commit. It also decided three questions I2a left open, two of them as proposed rules for I2b's runs that you assess (section 3).

- **You review one exact head:** `6a51dae3e0f2b7a69097151fb5e5dcfe4414b61d`, that merge commit.
  - Its first parent, `82d0dd4`, is the manager branch before the merge. Its second parent, `761fa28`, is I2a's head, a commit that adds only I2a's record. I2a's code head, which run 2 used, is `7ce93cc`.
  - The merge brought I2a's 41 files: 40 under `proofs/stream-chat/` and the evidence record.
- **Your scope is I2a's change:** the whole of `git diff HEAD^1 HEAD`, and the harness where I2a's change depends on it. The harness before I2a was reviewed at `8c1a8c0`; the flake fix at `8b8b1bd` is out of scope. Later commits are Markdown-only manager records, which you read at `<RECORDS_COMMIT>`.
- **The live results cannot be re-run here.** They exist only as I2a's record: its outputs stayed in its own session. You check that the record agrees with the code that produced it, and that the code could not have produced a false HOLDS or a false "ended".
- **What delays I2b.** Report every finding with its severity, as usual. After this review, only these delay I2b's live runs: a blocking finding, or a should-fix finding that could create a false HOLDS or a false "ended", lose an observed FAIL or DOES NOT MEET, send a request after a charge or limit signal, or let a change escape the guard. Everything else goes into I2b's offline first step or the final delta review. For each finding, say whether it falls in one of those classes.
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
git switch --detach 6a51dae3e0f2b7a69097151fb5e5dcfe4414b61d
git rev-parse HEAD                      # must print 6a51dae3e0f2b7a69097151fb5e5dcfe4414b61d
git rev-parse HEAD^2                    # must print 761fa289f1dacd13b8d48b78db6b220d07c079e3
git merge-base --all origin/main HEAD   # expected: one line, 0f45e648099b415217938c25d7369164c0101def
git merge-base --is-ancestor HEAD <RECORDS_COMMIT> && echo "records build on the head"
git diff --stat HEAD^1 HEAD             # expected: 41 files, 9442 insertions, 246 deletions
```

If any check fails, stop and report.

Classify three times, as root `AGENTS.md` requires. The trusted base policy runs outside the candidate tree, and every run uses the same policy file:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
python3 -I "$policy_dir/change_scope.py" --base 8c1a8c08d77052a86cfc70fc38cb830eb641438a --head "$head" --merge-base
python3 -I "$policy_dir/change_scope.py" --base "$head" --head <RECORDS_COMMIT> --merge-base
git diff --name-only 8c1a8c08d77052a86cfc70fc38cb830eb641438a "$head" | grep -v '\.md$' | grep -v '^proofs/stream-chat/'
```

- **The first run** is the head against `main`. Expected: `"full": true`.
- **The second run** is everything after the last reviewed code head, C3's merge commit. Expected: `"full": true`. The last command must print nothing: every non-Markdown change since then is under `proofs/stream-chat/`. Anything else is code this review would not cover: stop and report it.
- **The third run** is everything after the head. Expected: `ordinary-docs-only`. Anything else means a non-Markdown change landed after the head: stop and report it.

Then read, completely.

**At `HEAD`:**

- root `AGENTS.md` and `CLAUDE.md`;
- the I2a prompt, `docs/ephemeral/2026-09-26-p06-1-i2a-implementation-prompt.md` (revision 2): what the session was asked to do, including its owned paths, protected sections and live-run rules;
- the Dev Manager's read of that prompt, `docs/continuity/dev-manager/reviews/2026-09-26-dm-04-i2a-prompt-read.md`, and the manager's disposition in `docs/continuity/dev-manager/README.md`, "DM-04";
- the evidence record, `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md`: "Exact-head review of C3 (26 September 2026)", with its disposition; the three "What P06.1-I2a must know" lists, in C1's, C2's and C3's sections; the section "P06.1-I2a", I2a's own record; and the two claims I2a corrected in place, marked "(corrected in P06.1-I2a)";
- `proofs/stream-chat/README.md`, including "Verdict rules" and its "P06.1-I2a cases", the budget guardrails, "Signals, by kind" and the end-of-run rules;
- the whole of `git diff HEAD^1 HEAD`, and the parts of the harness it depends on.

**At `<RECORDS_COMMIT>`,** with `git show <RECORDS_COMMIT>:<path>`:

- the P06.1 brief's "Brief — P06.1" (owned paths, credential rules, the matrix quality rule) and "Sessions" (P06.1-I2a, its review and I2b), in `docs/planning/p06-1-chat-provider-proof.md`;
- the evidence record's last section: the manager's verification of I2a and its decisions.

## 3. What to review

The focus areas are in order of risk.

1. **The guard confines every change to the run's own data** (DM-04 finding 1).
   - Does every server request that changes anything pass `guard.refusal` before it is counted or sent, the SDK's typed calls included? Name any path that reaches Stream without it.
   - What it lets through: the run's recorded IDs, IDs that contain the run's prefix, journalled application settings, the `glow-match` type toggles, and the kinds of change it lists. Could it pass a change to a user, channel, member, message, poll, group, channel type or application setting that the run did not create?
   - `cleanup --apply`, scoped to the proof's prefix.
2. **Nothing is sent after a charge or limit signal.** The new paths: requests the SDK sends between commands or after a command's reply, asynchronous SDK errors, a session's exit reply, and the end of the run, which now closes the sessions before it decides the cleanup. Signals by kind: a charge signal against only a rate limit.
3. **No false HOLDS and no false "ended".**
   - The families: a dimension is `ended` only on Stream's authentication or permission error after the same request by the same member succeeded before; the subscription is `ended` only when a listener received the probe and the member did not, in two windows, with no connection change that could explain it; the token-lifetime margins; `token_issued_after`; MEETS only when every dimension is ended, the member's own client cannot undo it and the history is retained.
   - The existence oracle's pair verdicts; the S15 mapping; pin and archive (HOLDS only with the reads the rules require); TD-expiry; OUT-send; G2's and S10's new setups; and the rules of the finding-9 cases.
4. **Every temporary or destructive change is undone or cleaned up.** The S15 mapping's and pin and archive's restores; the ban, hide, freeze, deactivation and hard delete, including a user that a connect re-creates after the hard delete; the journal's type toggles and guest creation; and the closing checks, `configuration.verify` against every setting the committed baseline records, except guest creation.
5. **The run-1 fix.** Every command parameter named `id` now travels as `channel_id`. Is that right for every command the Python side sends, or does any command use `id` for something else? Do the two tests that drive the real runner cover the protocol, and could the fakes still hide another mismatch?
6. **An observed FAIL or DOES NOT MEET is never lost,** when a case, a family or a session is interrupted.
7. **The fix reversals.** Run `checks/fix_reversals.py`: does each of I2a's 95 reversals really remove its fix, and fail for the right reason? Name any fix whose test would still pass with the fix broken in another way.
8. **Records.**
   - I2a's section agrees with the code: its verdict rules, its counts and its comparison of the I1 matrix with I1's final run. The two in-place corrections are accurate and marked. The eight sections the I2a prompt protects are byte-identical to `6e67fd6`. The README's rules match the code. This is a full-scope review: never skip a finding because its file ends in `.md`.
   - **The product findings** in "What I2b and P06.2 must know": for each, say whether the code that produced it could have produced it falsely. A false HOLDS or a false "ended" matters most, because a design could rest on it.
9. **The manager's decisions,** in its verification of I2a: the proposed disclosure rule, the proposed rule for 404 code 16, the approach to the poll listing, and the three deviations it accepted, including M1 and M2 shared by the four channel-level mechanisms. Assess each, and say where you disagree and why.
10. **Scope.** Only `proofs/stream-chat/**` and the evidence record changed. No dependency file, `pyproject.toml` dependency, `.npmrc` or committed baseline changed. Every file has mode 100644, and there are no symlinks.

**Out of scope:**

- re-running anything live; the live results rest on I2a's record;
- the rest of the harness, except where I2a's change depends on it;
- Video and Feeds, the architecture document and the Foundation job, which belong to I2b;
- the flake fix and the rest of the app;
- anything in HDE.

## 4. Checks to run

Report the exact commands and results.

1. `git diff --check HEAD^1 HEAD`.
2. The three classifications above.
3. The installs from the locks, with the README's commands, in clean processes.
4. The offline checks, with the README's commands: the unit tests (I2a reported 393), Ruff check and format, mypy, and `node --check` on the three `.cjs` files.
5. `checks/fix_reversals.py` (I2a reported 242, none "not demonstrated"), each of I2a's reversals' failure reasons, and anything more you need to test a fix's test.
6. A secret scan over the whole of `git diff HEAD^1 HEAD`.
7. Anything else you judge necessary, offline only.

The manager reads hosted CI on the reviewed head, so you need not wait for it.

## 5. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 1, from commit `<RECORDS_COMMIT>`);
- the head you reviewed (`git rev-parse HEAD`) and the three classification outputs;
- **verdict:** "approve" (I2a's harness and record are a sound base for I2b's live runs) or "changes required";
- **findings,** most severe first. For each: severity (**blocking**, **should fix** or **nit**), `file:line`, the concrete failure scenario, a suggested fix, and whether it falls in one of the classes that delay I2b;
- for the C3 review's six nits and its gap, DM-04's conditions, and the independent check's findings: confirmed fixed, or not, with the reason;
- for each product finding in "What I2b and P06.2 must know": sound, or could have been produced falsely, with the reason;
- for each of the manager's decisions: agree, or disagree with the reason;
- the areas you reviewed with no findings;
- every check you ran, with its exact result;
- limits: anything you could not check, and why.

Skipped or unavailable checks are not passes. Change nothing in the repository, on GitHub or in Notion.

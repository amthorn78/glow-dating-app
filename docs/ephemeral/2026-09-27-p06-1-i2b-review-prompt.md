# P06.1-I2b review prompt — exact-head review of other products, the architecture document and CI

- **Owner:** App Manager 4. Nathan starts this session manually and relays its report.
- **Revision 3, 27 September 2026:** header only, after OD-34: the TypeSafe v6 reading below is the recommendation; the manager's call stays as a record only. **Revision 2, 27 September 2026:** header only, after OD-33. TypeSafe's reading was retaken with the request v5 ([reasoning-strength matrix](../planning/reasoning-level-matrix.md)); the body is unchanged apart from its revision line. Revision 1 was given to Nathan at `d94173f` and not started.
- **Durable brief:** [P06.1 brief](../planning/p06-1-chat-provider-proof.md), "Sessions" (P06.1-I2b and its review).
  - Evidence: the [P06.1 evidence record](../testing/evidence/2026-09-25-p06-1-chat-provider-proof.md): "Exact-head review of I2a (27 September 2026)" with its disposition (I2b's offline work list), "P06.1-I2b" (I2b's own record) and the manager's verification under it; the new [architecture document](../architecture/chat-provider-permissions.md).
- **Where the result goes:** the manager records the verified review in the evidence record, under a new heading "Exact-head review of I2b". The outcome goes into the brief's "Sessions". After it the manager updates ADR 0003's conditions (DM-05 finding 5 (b)).
- **Model and reasoning level** (OD-10, OD-30). Neither reading gates anything, and Nathan picks.
  - **Manager: Fable 5.1, extra high,** decided at 07:58 UTC, before TypeSafe's readings. The review covers about 11,700 new lines of harness code and tests, a workflow change and the architecture document P06.2 designs from: a new client op and a guard scope for two products with a deny-list in code, a scoped configuration command that made the proof's one lasting change, new verdict rules, and two fixes made between live runs. Its live results exist only as I2b's record. That is a review of a large new system whose soundness is not yet established, the class where the most capable model is most likely to change the outcome; the I2a review, the same class, was adequate on Fable 5.1 at extra high. Extra high rather than max, in the manager's judgement: the review is offline, and on Fable a lower level often matches a higher one on Opus.
  - **TypeSafe v4** (sent 07:58:36 UTC): extra high (score 2.77, P(extra high) 0.75, P(high) 0.24, P(max) 0.01). It raises its ultracode flag (shape `broad_verification` 0.83; P(single session) 0.12). The manager does not recommend ultracode: one change, and the session can split the review across subagents itself.
  - **TypeSafe m1** (sent 07:58:37 UTC): Opus 5.5 (P(most capable) 0.29, confidence 0.42). The calls differ on the model. The manager keeps Fable 5.1: m1's criteria class a review of a bounded change against named findings as Opus work, but this review's object is a new system, not a correction pass, and its verdicts become the basis of P06.2's design.
  - **TypeSafe v6** (the reading in force, OD-34; sent 2026-09-27T11:40:32Z; the same action text): **Fable 5.1, max.** Effort score 3.79 (confidence 0.86); rung probabilities low 0.00, medium 0.00, high 0.01, extra high 0.19, max 0.80, ultracode 0.00. Model probabilities Fable 5.1 0.53, Opus 5.5 0.47 (confidence 0.06); flag: model near tie. **Nathan's pick: Fable 5.1 at max**, started 27 September.
  - **TypeSafe v5** (sent 09:35:48 UTC, after the call above; the same action text): **Opus 5.5, extra high, no ultracode.** Effort score 2.73 (extra high 0.72, high 0.27, max 0.01; confidence 0.76); many-agent workflow 0.03 (confidence 0.93); most capable model 0.18 (confidence 0.65). The informed request agrees on the level and on no ultracode, and disagrees on the model more firmly than m1. The manager's call stands as recorded, for the reasons above; Nathan picks.
- **No Dev Manager read is needed:** the prompt authorizes no credential use and no live provider action.
- **Stream variables** (OD-28): none are needed, and Nathan adds none. This session never calls Stream. If Nathan has not yet deleted the three `STREAM_*` variables after I2b, this session's container holds them; the prompt tells it to report their names and never read or use them.
- **It runs alone** (OD-29, the linear process). The economics discovery comes after it.
- **Deletion condition:** prune after P06.1 closes and the evidence record and brief hold the result.

**Manager:** before giving this prompt to Nathan, replace every `<RECORDS_COMMIT>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **review session for P06.1-I2b** of the Glow dating app, private repository `amthorn78/glow-dating-app`. This prompt is revision 3, from commit `<RECORDS_COMMIT>`; revisions 2 and 3 changed only the manager's header.

P06.1 tests Stream's permission model against Nathan's development Stream application 1729640, with synthetic users only, using the sandbox harness in `proofs/stream-chat/`. P06.1-I1 locked the chat down and ran the bypass matrix; three offline correction passes and P06.1-I2a (revocation and safety, live) followed, each with its exact-head review. P06.1-I2b, the last live session, then did this, from the manager branch at `b04306d`:

- **step 1, offline** (`bca64eb`): the I2a review's two should-fix findings and four nits, two new verdict rules (the disclosure rule and the rule under which a 404 code 16 counts as an ended access), a `sync` pair in the existence oracle, the API key removed from free text, the poll listing, and a new Foundation job, "Stream proof checks", that runs the harness's offline checks in CI;
- **step 2, offline** (`a1880fb`): Stream Video and Feeds. A runner op through which a modified client sends a product request with its own token, with a path allowlist and a deny-list in code; the same scope and deny-list in the server-side guard; 18 cases; a scoped, differential `configure --products video,feeds` whose `--apply` refuses in code anything outside the two products' configuration families and anything while chat does not verify; an availability probe; a rule under which an answer that a product is not available is a finding, not a charge signal; preflight, `verify-clean` and cleanup covering calls, feeds and activities; a fake model of both products for the offline tests;
- **an independent check,** by a fresh sub-agent, before the first live call: six findings, fixed at `2ff6807`, and three remarks recorded as README limits;
- **live** (15 commands, one at a time, each from a committed and pushed head): run 1 (the chat reruns: RV-remove and SD-deactivate MEET the history policy under the 404 code 16 rule; the oracles; F9-sync HOLDS filtered; F9-thread INCONCLUSIVE; S3a); the probe (both products available); run V1 (a harness defect left eight Feeds cases INCONCLUSIVE: Stream never recreates a deleted feed ID); the products baseline, committed (`1137786`); the fix (`93390ce`) and the reserve rerun of V1 (16 FAIL, 2 HOLDS: the `user` role could do almost everything tested); the one lasting change, `configure --products video,feeds --apply` (nine `PUT`s, each 201, re-read verified); the stamp commit (`ad89753`, which also moves the fake products' default configuration to the lockdown target); run V2 (9 HOLDS, 7 FAIL, 2 INCONCLUSIVE: what remains is held by a call's member or creator and a feed's creator, and the activities query still returns another user's activities); the closing checks;
- **records** (`0a0512c`): the architecture document and the evidence section. The unit tests went from 393 to 503, and `checks/fix_reversals.py` from 242 to 342 entries.

The manager verified I2b's branch and integrated it with a merge commit.

- **You review one exact head:** `55b22387e6478e4b7c8d58480108e4c7341c4564`, that merge commit.
  - Its first parent, `c6e9bf4`, is the manager branch before the merge. Its second parent, `0a0512c`, is I2b's head, a commit that adds only Markdown. I2b's code head, which run V2 used, is `ad89753`; run 1, the probe and the first run V1 used `2ff6807`; the V1 rerun and the apply used `93390ce`.
  - The merge brought I2b's 41 files: 38 under `proofs/stream-chat/`, `.github/workflows/foundation.yml`, `docs/architecture/chat-provider-permissions.md` and the evidence record.
- **Your scope is I2b's change:** the whole of `git diff HEAD^1 HEAD`, and the harness where I2b's change depends on it. The harness before I2b was reviewed at `6a51dae`. Later commits are Markdown-only manager records, which you read at `<RECORDS_COMMIT>`.
- **The live results cannot be re-run here.** They exist only as I2b's record: its outputs stayed in its own session. You check that the record agrees with the code that produced it, and that the code could not have produced a false HOLDS, a false MEETS or a false "ended". Two design decisions rest on I2b's live results and stay conditional until you confirm them (DM-01 P4): that removal and deactivation MEET the history policy under the 404 code 16 rule, and what a user token can and cannot do in Video and Feeds before and after the lockdown.
- **What comes after this review.** Report every finding with its severity, as usual. A blocking finding, or a should-fix finding that could create a false HOLDS, MEETS or "ended", lose an observed FAIL or DOES NOT MEET, send a request after a charge or limit signal, let a change escape the guard or the deny-lists, or let the scoped `configure` apply anything outside the two products, gets an offline correction pass before P06.1 closes. Everything else goes into the final delta review or the records. For each finding, say whether it falls in one of those classes.
- Nathan started you manually and will relay your report to the manager (App Manager 4). You are neither the manager nor an implementer.
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
git fetch origin claude/stoic-carson-66gdig main
git switch --detach 55b22387e6478e4b7c8d58480108e4c7341c4564
git rev-parse HEAD                      # must print 55b22387e6478e4b7c8d58480108e4c7341c4564
git rev-parse HEAD^2                    # must print 0a0512c1fa95c1c55546eff57ba4d68f79325b3a
git merge-base --all origin/main HEAD   # expected: one line, 0f45e648099b415217938c25d7369164c0101def
git merge-base --is-ancestor HEAD <RECORDS_COMMIT> && echo "records build on the head"
git diff --stat HEAD^1 HEAD             # expected: 41 files, 11719 insertions, 175 deletions
```

If any check fails, stop and report.

Classify three times, as root `AGENTS.md` requires. The trusted base policy runs outside the candidate tree, and every run uses the same policy file:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
python3 -I "$policy_dir/change_scope.py" --base 6a51dae3e0f2b7a69097151fb5e5dcfe4414b61d --head "$head" --merge-base
python3 -I "$policy_dir/change_scope.py" --base "$head" --head <RECORDS_COMMIT> --merge-base
git diff --name-only 6a51dae3e0f2b7a69097151fb5e5dcfe4414b61d "$head" | grep -v '\.md$' | grep -v '^proofs/stream-chat/' | grep -v '^\.github/workflows/foundation\.yml$'
```

- **The first run** is the head against `main`. Expected: `"full": true`.
- **The second run** is everything after the last reviewed code head, I2a's merge commit. Expected: `"full": true`. The last command must print nothing: every non-Markdown change since then is under `proofs/stream-chat/` or is the workflow. Anything else is code this review would not cover: stop and report it.
- **The third run** is everything after the head. Expected: `ordinary-docs-only`. Anything else means a non-Markdown change landed after the head: stop and report it.

Then read, completely.

**At `HEAD`:**

- root `AGENTS.md` and `CLAUDE.md`;
- the I2b prompt, `docs/ephemeral/2026-09-27-p06-1-i2b-implementation-prompt.md` (revision 2): what the session was asked to do, including its owned paths, protected sections, run plan and live-run rules;
- the Dev Manager's read of that prompt's revision 1, `docs/continuity/dev-manager/reviews/2026-09-27-dm-05-i2b-prompt-read.md`, and the manager's disposition in `docs/continuity/dev-manager/README.md`, "DM-05";
- the evidence record, `docs/testing/evidence/2026-09-25-p06-1-chat-provider-proof.md`: "Exact-head review of I2a (27 September 2026)" with its disposition (I2b's offline work list and the two rules as the review left them); the manager's verification of I2a and its decisions; the section "P06.1-I2b", I2b's own record; and the two sentences I2b corrected in place, marked "(corrected in P06.1-I2b; the I2a review's nit 6)";
- `docs/architecture/chat-provider-permissions.md`, whole;
- `docs/adr/0003-chat-display-rule.md`, its "Conditions (DM-02 B7)";
- `.github/workflows/foundation.yml` and `services/api/tests/test_toolchain_pins.py`;
- `proofs/stream-chat/README.md`, including "Verdict rules" with its "P06.1-I2b cases", "Budget guardrails" and "Signals, by kind", "The guard", "The Video and Feeds lockdown", "What this proof does not show" and "Limits";
- the whole of `git diff HEAD^1 HEAD`, and the parts of the harness it depends on.

**At `<RECORDS_COMMIT>`,** with `git show <RECORDS_COMMIT>:<path>`:

- the P06.1 brief's "Brief — P06.1" (owned paths, credential rules, the matrix quality rule) and "Sessions" (P06.1-I2b and its review), in `docs/planning/p06-1-chat-provider-proof.md`;
- the evidence record's last section: the manager's verification of I2b and its dispositions of the deviations.

## 3. What to review

The focus areas are in order of risk.

1. **Nothing outside the allowlists can be sent, and every change stays the run's own** (DM-05 finding 3; DM-04 finding 1).
   - The runner's `product` op (`client/product-op.cjs`): its allowlist and deny-list. Could a request that rings, notifies, joins, records, broadcasts or starts media pass it, by a path, a query or a body field the tables miss (a nested field, a non-boolean value, a different casing, a path with a prefix)? The op is the only way a client session sends a product request: is that so?
   - The guard's Video and Feeds scope (`glow_stream_proof/products.py`, `guard.py`): the same families, deletes only of run-owned objects, a configuration write only inside `guard.ConfigureScope`. Does every server request that changes anything, the SDK's typed calls included, pass the guard before it is counted or sent? Could a product configuration write, or a delete of an object the run did not create, pass during `run`?
   - The test that compares the JS and Python tables: does it cover every row, and could the two drift apart unnoticed?
2. **The scoped `configure` and the one lasting change** (DM-05 finding 1).
   - `configure --products video,feeds`: is its plan a difference (nothing sent for a scope already at the target), does it name only `user`, `guest` and `anonymous` with `[]`, and does `--apply` refuse, in code, while chat does not verify, for any path outside the two configuration families, and for an unknown product? Are the refusals tested, and do the reversals show them?
   - The applied plan's record (the evidence record, command 11; the architecture document, section 5) against the committed baseline `baseline/video-feeds-1729640-2026-09-27.json`: are the nine `PUT`s exactly the scopes where a client role held a grant, and nothing else? Could the apply have changed a setting, a resource role or a scope the record does not show?
   - `products.LOCKDOWN_APPLIED` and `configuration.verify`: from `ad89753` on the products are compared; before, they were not. Could a drift in the products go unseen, and could the general `configure --apply` or `restore` touch them?
3. **No false HOLDS, MEETS or "ended".**
   - The 404 code 16 rule (`mechanisms.py`, `missing_404` and its callers): ended only after RV-remove and SD-deactivate, only with the member's earlier success, the other member's identical request succeeding after it, and Stream's message naming the missing membership or user, kept in the row. Could a 404 for a missing channel, a malformed request or a harness error count as ended? Is run 1's MEETS for RV-remove and SD-deactivate what the code, given the recorded answers, must produce?
   - The disclosure rule (`proof_run.py` `_disclosure`, `matrix.carried_terms`): could a real disclosure be filtered because a term happens to appear in the request, and could a filtered term hide a leak of a different value? F9-sync's HOLDS (filtered).
   - The existence oracle by shape (`i2a.py` `shape`, `pair_verdict`): could two answers of the same shape hide an oracle, and could a shape difference that is not an oracle give a false FAIL? EO-channel's `sync` pair.
   - Finding 1's fix (`mechanisms.py`, `stepping` and the `finally`) and the independent check's findings 1 and 2: could a stop inside a step still lose an observation, or record one wrongly?
   - The product cases' verdicts (`matrix._products`, the README's "P06.1-I2b cases"): before the lockdown a FAIL is a capability; after it every case must HOLD, and a FAIL is a remaining capability. Could a HOLDS after the lockdown rest on anything but Stream's attributable refusal with a successful control? The two INCONCLUSIVE rows of run V2 (VD-query, code 102; FD-read, no successful control) and the quality rule.
   - The product-finding rule (`usage.product_unavailable_wording`, `products.availability`, `unavailable_answer`; the `upgrade`-only exemption in `usage.charge_signal`): could a real charge signal be read as a product finding and let live work continue, or cleanup send after a charge? Could an input error be read as "not available"?
4. **Nothing is sent after a charge or limit signal.** The new paths: the product op's requests, the probe, the scoped `configure`'s requests, the product deletes in cleanup, the fixtures' requests, and a stop inside a product case.
5. **Every object a case creates is deleted, and preflight sees leftovers.** The fixtures' calls, feeds, activities, follows, comments and reactions; `Control.undo_once`; the FD-feed change at `93390ce` (the replay makes no undo, A's feed stays for cleanup); each run user's Feeds data delete; the listings in preflight and `verify-clean` (a listing that is not 2xx: "not available" only by the product's own configuration read, else "not verified" and preflight refuses). Could an object survive a run, or a leftover go unseen?
6. **The two fixes made between live commands.**
   - `93390ce`: the tombstone model in the fake and the FD-feed change. Does the failing test fail for the defect the live run showed, and does the fix change nothing else?
   - `ad89753`: the stamp, and the fake products' default configuration moved to the lockdown target. Does that move weaken any test? The before-lockdown verdict tests rely on the fake's `allowed` knob, not its grants: is that so, and do the tests of the plan and of drift still test the pre-lockdown state?
7. **The Foundation job** (DM-05 finding 4). `git diff HEAD^1 HEAD -- .github/` is exactly the new job `proof` and the gate's two references. Is the job's condition the same as the other application jobs', its pins and `persist-credentials: false` the same, its toolchain the pinned one with one `npm install --global npm@11.9.0`, its timeout bounded, and does it reference no secret and set no `env:`? Does it run what the README's "Checks (offline)" names? Then read hosted CI: the PR run the manager names in its verification at `<RECORDS_COMMIT>` (run 36305061337, on `84b2d6f`, a Markdown-only records commit whose code is the head's). Confirm from the run's jobs that "Stream proof checks" ran (not skipped) and passed, and that the gate's Python list includes `proof`. The pin test (`services/api`, `python3.12 -m unittest tests.test_toolchain_pins`) must pass at the head.
8. **The fix reversals.** Run `checks/fix_reversals.py` (I2b reported 342, none "not demonstrated"): does each of I2b's 100 entries really remove its fix, and fail for the right reason? Name any fix whose test would still pass with the fix broken in another way.
9. **Records.** This is a full-scope review: never skip a finding because its file ends in `.md`.
   - I2b's section agrees with the code and with its commits: the verdict rules, the counts (503 tests, 342 reversals, 15 live commands, the usage figures), the results tables against the rules, and the two in-place corrections. The ten sections the I2b prompt protects are byte-identical to `b04306d`. The README's rules match the code.
   - **The architecture document.** Every claim names the run that showed it and is marked "not yet" for I2b's runs; the table of every path a modified client has to the other member, with its closure; ADR 0003's conditions (a) to (d) with their status per mechanism; the applied plan (section 5) against the baseline and the record; the Video and Feeds tables (section 6) against the evidence record's rows; sections 8 and 9. Does it claim anything the runs did not show, or decide anything for P06.2?
   - **The design decisions that rest on I2b's results:** removal and deactivation MEET under the 404 code 16 rule; what a user token could do before the lockdown and what remains after it; the activities query left open. For each, say whether the code that produced the result could have produced it falsely.
10. **The manager's dispositions,** in its verification of I2b: the reserve rerun spent on run V1 (so run V2 had none); the two fix commits between live commands, each followed by the full reversal run; `checks/run_plan.py` reading "DOES NOT FIT" mid-session because it adds the ledger to the whole plan again; F9-thread INCONCLUSIVE with replies off; VD-query and FD-read INCONCLUSIVE after the lockdown; and the activities query recorded as open rather than decided. Assess each, and say where you disagree and why.
11. **Scope.** Only `proofs/stream-chat/**`, the workflow, the architecture document and the evidence record changed. No dependency file, `pyproject.toml` dependency, `.npmrc` or committed chat baseline changed. Every file has mode 100644, and there are no symlinks.

**Out of scope:**

- re-running anything live; the live results rest on I2b's record;
- the rest of the harness, except where I2b's change depends on it;
- the economics discovery, which follows this review;
- the app outside the harness, and anything in HDE.

## 4. Checks to run

Report the exact commands and results.

1. `git diff --check HEAD^1 HEAD`.
2. The three classifications above.
3. The installs from the locks, with the README's commands, in clean processes.
4. The offline checks, with the README's commands: the unit tests (I2b reported 503), Ruff check and format, mypy, `node --check` on the four `.cjs` files, `checks/run_plan.py` (with an empty ledger: "run plan: fits"), and the pin test.
5. `checks/fix_reversals.py` (I2b reported 342, none "not demonstrated"), each of I2b's reversals' failure reasons, and anything more you need to test a fix's test.
6. A secret scan over the whole of `git diff HEAD^1 HEAD` (I2b's one JWT-shaped string is a fabricated redaction-test input) and over the committed baseline file: no secret, token, API key or email address.
7. Hosted CI on the head, as focus area 7 says.
8. Anything else you judge necessary, offline only.

## 5. Report

Your final message is the report Nathan relays:

- the prompt revision you received (revision 3, from commit `<RECORDS_COMMIT>`);
- the head you reviewed (`git rev-parse HEAD`) and the three classification outputs;
- **verdict:** "approve" (I2b's harness, records and architecture document are sound, and P06.1 can close on them) or "changes required";
- **findings,** most severe first. For each: severity (**blocking**, **should fix** or **nit**), `file:line`, the concrete failure scenario, a suggested fix, and whether it falls in one of the classes that need a correction pass before P06.1 closes;
- for the I2a review's items, DM-05's conditions, and the independent check's findings: confirmed fixed or applied, or not, with the reason;
- for each design decision that rests on I2b's results: sound, or could have been produced falsely, with the reason;
- for each of the manager's dispositions: agree, or disagree with the reason;
- the workflow: confirmed as exactly the one job, and the job's result in the PR run on the head;
- the areas you reviewed with no findings;
- every check you ran, with its exact result;
- limits: anything you could not check, and why.

Skipped or unavailable checks are not passes. Change nothing in the repository, on GitHub or in Notion.

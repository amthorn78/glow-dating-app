# P06.2 Stage C2-C3 prompt — correction pass: the cursor position is known only while `lastRead` is in the window (the re-review's F1)

- **Owner:** App Manager 8. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 25 October 2026.**
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 18: "The re-review's F1, and C2-C3", with "Codex's CX9 and CX10, and C2-C2" and the owned paths for C2-C3.
  - Inputs:
    - the [DM-27 report](../continuity/dev-manager/reviews/2026-10-25-dm-27-p06-2-re-review-f1.md) (`a9513a5`), whose conditions 1.1 to 1.4 are quoted below as written;
    - the evidence record's "Exact-head review of Stages C2-C1 and C2-C2" (F1), "Stage C2-C2" and its verification;
    - the DM-25 report, 3.1 to 3.4, and the DM-23 report, 2.1 to 2.3, the cursor rule this pass amends.
- **Where the result goes:**
  - the session's code and tests, and its section "Stage C2-C3" in the evidence record `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`;
  - the run of record: the Foundation run on its last code commit.

  The manager adds its verification and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 1.56 (confidence 0.70); rung probabilities low 0.00, medium 0.44, high 0.55, extra high 0.01, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.91, Sonnet 5.5 0.09, Haiku 5.5 0.00 (confidence 0.88). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.400, Opus 5.5 at high 0.501, Opus 5.5 at extra high 0.009, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.040, Sonnet 5.5 at high 0.050, Sonnet 5.5 at extra high 0.001, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Flags: boundary between medium and high. Sent 2026-10-25T03:41:48Z. Nathan picks the cell.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** none, on DM-27 3.1's terms: this prompt quotes 1.1 to 1.4 as written; the cursor rule is as DM-23 2.1 to 2.3, DM-25 3.1 to 3.3 and DM-27 1.1 set it; `apps/mobile` only, no dependency or contract change, the revocation rule unchanged; it starts in `Glow App - No Stream`, checks that no `STREAM_*` name is present, and authorizes no credential and no provider call. A departure found while it runs goes back to the Dev Manager first.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and the session calls no provider.
- **It runs alone** (OD-29). Codex's review of its code head follows, with any finding handled; then its own exact-head re-review (DM-27 1.4).
- **Deletion condition:** prune after Stage C2's PR merges and the evidence record holds the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **correction session P06.2 Stage C2-C3**, a correction pass on Stage C2 of P06.2, the chat integration of the Glow dating app, in the private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<START_SHA>`.

**What exists.** Stage C1 merged on 24 October (PR32, `a8e9528`). **Stage C2,** the mobile chat interface on fixtures, is PR33, from the manager branch `claude/magical-wozniak-yfmmx2` into `main`.

- **Stage C2** (code `cb3a6a6`) added `apps/mobile/src/chat/` (a `ChatTransport` interface, an in-process fixture adapter, a validating client, a polling store, the screens and their tests). **C2-C1** (code `311b07e`) made the read cursor move only to the newest accepted message that has been in view (DM-23 2.1 to 2.3). **C2-C2** (code `27999c7`, unchanged since; the commits after it are Markdown records) made a revocation invalidate every outstanding request (DM-24) and, until a cursor command has succeeded, stopped treating the unknown server position as known (DM-25 3.1 to 3.3, with the flag `cursorKnown`). Its run of record 40152538074 passed all eight jobs.
- **The exact-head re-review of C2-C1 and C2-C2** closed CX8 and CX9, and CX10 for the case raised, and asked for changes for **F1** (should fix): once a command has succeeded, `cursorKnown` stays true even when `lastRead` is no longer in the loaded messages. A head read answered `stale` makes `readHead` clear `newerCursor` and queue a read with no cursor, whose page goes through `mergeHead`'s newest branch and replaces `accepted`. `lastRead` can then lie before the window: `from` is −1, `passesOther` reads only the new page, and `cursorKnown` suppresses DM-25 3.1's fallback (`store.ts:315`). With the member's own messages filling that page and an unviewed incoming message before it, viewing the newest sends nothing, and the count stays above zero until an incoming message comes back into the window.
- **Why it is corrected now:** it misses C2's item 8 ("the app moves the member's own cursor forward … when the member has seen newer messages") on that path, it is in a correction class the re-review named, and a unit test shows it offline. The Dev Manager chose a correction pass before PR33 merges (DM-27), and amended DM-25 3.1's "Once a command has succeeded, DM-23 2.3 holds as written" to "While `lastRead` is among the loaded accepted messages, DM-23 2.3 holds as written".
- **Its reach is narrow:** C1's server answers `stale_version` to a newer cursor only when the cursor cannot be read, or its match or boundary cannot be placed (`services/api/glow_chat/reads.py:389-411`); the fixture never answers `stale`, so the tests answer one head read `stale` through a test transport.

**How you work:**
- Nathan started you manually and will relay your report to the manager (App Manager 8). You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs, including reading Expo's and React Native's versioned documentation as `apps/mobile/AGENTS.md` asks.
- Your boundary is scope:
  - write only your owned paths (section 5);
  - push only your own session branch. The Foundation workflow runs on a push only for `main`, `app-builder-1/**`, `app-planner-1/**` and `claude/**`. If your branch is under that filter, each push runs it, and you read those runs if your tools can; if it is not, say so in your report, and the manager takes the run of record from the PR run on the head that integrates your code (the manager workflow, step 5). On GitHub do nothing else: no pull request, no PR comments, no re-runs, no workflow dispatches. Change nothing in Notion.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, token or password, in any form;
  - call Stream or any other provider, or run any harness command in `proofs/stream-chat/` that sends a request;
  - connect to any database, HDE, Railway or any other provider;
  - run `playwright install`, `eas` or `migrate`;
  - add or change a dependency, a version or a lock file, in any component.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If any is present, stop and report to Nathan: this session must start in `Glow App - No Stream`.
3. **No `.env` file:** `ls -a . apps/mobile packages/contracts | grep -x '\.env'` must print nothing. If one exists, report it without reading it, and stop.
4. **The toolchain:** the pinned toolchain is in `$HOME/.local/bin`: Node 24.19.0 and npm 11.9.0 (and Python 3.12.14). Put `$HOME/.local/bin` first on PATH in every process you run, then record `node --version` and `npm --version`.
5. **A clean process environment.** Run the mobile app's and the contracts' commands in one, as `docs/operations/local-development.md` and each README show: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`EXPO_OFFLINE=1` where the mobile README uses it). Installs get the proxy and CA variables by reference, never printed.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git merge --ff-only <START_SHA>          # on your own session branch
git rev-parse HEAD                       # must print <START_SHA>
git merge-base --is-ancestor a8e952895ebd3ffc9ef0e4d195c8a7111c69b3ae HEAD && echo "C1 present"   # must print "C1 present"
git diff --quiet 27999c7bd9b79fd1a1c68136b3de62b14bd32a34 HEAD -- proofs .github services scripts apps packages && echo "C2-C2's code"   # must print "C2-C2's code"
git diff --stat <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- apps/ packages/ services/ proofs/ .github/   # must print nothing
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md | grep -c '^## Stage C2-C3'   # must print 0
```

- The last two commands check the live manager branch. If code or this stage's section has already landed there, this prompt is stale: stop and report (the manager workflow, step 3, AM5-15).
- If any check fails, stop and report.

Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md` and `apps/mobile/README.md`;
- the P06.2 brief, `docs/planning/p06-2-chat-integration.md`, revision 18: "The re-review's F1, and C2-C3", "Codex's CX9 and CX10, and C2-C2", and the owned paths for C2-C3;
- the DM-27 report, `docs/continuity/dev-manager/reviews/2026-10-25-dm-27-p06-2-re-review-f1.md`; the DM-25 report's 3.1 to 3.4 (`2026-10-25-dm-25-p06-2-re-review-order.md`); the DM-23 report's 2.1 to 2.3;
- C2's prompt, `docs/ephemeral/2026-10-24-p06-2-stage-c2-implementation-prompt.md`, item 8;
- the evidence record's "Stage C2-C2", "Manager verification of Stage C2-C2" and "Exact-head review of Stages C2-C1 and C2-C2";
- `apps/mobile/src/chat/` whole, chiefly `store.ts` (`readHead`, `mergeHead`, `loadOlder`, `moveReadCursor`, `revoke`, `resetConversation`, the command's success) and `store.test.ts` (the CX9 and CX10 tests and `:193`, `:210`).

## 3. The work

DM-27's conditions are quoted at their items, with their numbers. Meet each as written.

**DM-27's conditions 1.1 to 1.4, as written:**

> - **1.1 The position is known only while `lastRead` is among the loaded accepted messages** (replaces d.1).
>   - **Why one test suffices:** `lastRead` is set only by a successful command and cleared wherever the store forgets the position. So this one test covers both "a command has succeeded in this opening" and "the window still holds it".
>   - **While it holds,** DM-23 2.3 holds as written. **Otherwise,** DM-25 3.1's three grounds apply.
>   - **`cursorKnown` is removed,** since it would add nothing. The record says so, and why.
>   - **The amendment:** DM-25 3.1's "Once a command has succeeded, DM-23 2.3 holds as written" reads "While `lastRead` is among the loaded accepted messages, DM-23 2.3 holds as written".
> - **1.2 Tests** (replaces d.2). Each has its reversal in a scratch copy outside the checkout, showing that the test fails without the fix. The test transport answers one head read `stale`, as the reviewer's did.
>   - **(a) The reviewer's sequence, with no summary held.**
>     - Jules sends A; it is viewed, and the command succeeds.
>     - Jules sends B; then a full page of the member's own messages is accepted.
>     - The next head read is answered `stale`.
>     - After the reload, viewing the newest sends one command, to `seen`, and the count clears.
>   - **(b) The same, with a summary held at 0.** The list was read before, and the earlier command's response left the summary at 0.
>     - Viewing the newest sends nothing (DM-25 3.4 (c)'s rule).
>     - The next list read sends one command, to `seen`, and the count clears.
>   - **(c) A `stale` reload that keeps `lastRead` within the newest page,** with no summary held, so that only the known position holds the move back: the member's own newer messages in view send nothing (DM-23 2.3).
>   - **The reversals:**
>     - the position treated as known once a command has succeeded, whatever the window holds (today's code), fails (a) and (b);
>     - the position treated as unknown even with `lastRead` in the window fails (c) or `store.test.ts:193`.
>   - **The existing tests:** every one passes unchanged, the CX9 and CX10 tests included. Any change is named in the record, with the rule that makes it.
>   - **F2:** it needs no test, since 1.1 removes the flag.
> - **1.3 Scope** (replaces d.3).
>   - **The paths:**
>     - `apps/mobile/src/chat/store.ts` and `store.test.ts`;
>     - `src/chat/testing.ts`, only if a test needs a helper;
>     - the README's cursor sentence, which states 1.1. It now ties the fallback to "until a command has succeeded", and 1.1 changes that;
>     - the evidence record's new section "Stage C2-C3".
>   - **Unchanged:**
>     - DM-23 2.5's unchanged list, and the fixture adapter;
>     - the revocation path (DM-24 1.1 to 1.3);
>     - DM-25 3.2's triggers.
> - **1.4 What follows** (replaces d.4).
>   - **First,** Codex's review of C2-C3's code head, with each finding handled, as DM-25 1.2 sets it.
>   - **Then C2-C3's exact-head re-review,** of its delta from `27999c7` (DM-25 2.2). It:
>     - names F1, CX10 and C2's item 8;
>     - reads 1.1 at the head;
>     - searches every assignment to `accepted` and `lastRead` (`mergeHead`'s newest branch, `loadOlder`, `revoke`, `resetConversation`, the command's success) for any path that leaves the position treated as known while `lastRead` is outside the window.
>   - **Its prompt names:**
>     - its correction classes (DM-25 2.1);
>     - its security focus: the revocation path and the client boundary unchanged, and no provider package, socket or network client added.
>   - **Then,** Codex on the final head, the final run, the CX8, CX9 and CX10 threads resolved, the pre-merge checklist and the merge.

1. **The rule** (1.1): the position is known only while `lastRead` is among the loaded accepted messages; while it holds, DM-23 2.3 holds as written; otherwise DM-25 3.1's three grounds apply. `cursorKnown` is removed. Record the change and why one test suffices.
2. **The tests** (1.2): cases (a), (b) and (c), with a test transport answering one head read `stale`, and the two reversals 1.2 names, in a scratch copy outside the checkout. Every existing test passes unchanged; name any change and the rule that makes it.
3. **The README** (1.3): its cursor sentence states 1.1.
4. **The record:** a new section "Stage C2-C3" in the evidence record, with what the re-review of 1.4 must know.

**Not in C2-C3:**
- any change to the revocation path (DM-24 1.1 to 1.3) or to DM-25 3.2's triggers (1.3);
- any change to the fixture adapter (1.3): the test transport answers `stale`;
- the re-review's F3 (a P11 limit) and F4 (a record annotation the manager made);
- the cursor position in a contract (C2C1-X1 stays for P11), or any other contract or dependency change (stop and report);
- a network client, an API URL, a socket or any realtime service;
- any change to `packages/`, `services/`, `proofs/` or `.github/`.

**Rules for every change:**
- **A test for each change.** Each code item gets a test that fails without the change and passes with it. Say which test covers which condition.
- **Reversals in a scratch copy, never the checkout.** Make each fix reversal in a copy outside the repository, with absolute paths. Confirm afterwards that `git status` is clean.
- **No weakened check.** Never loosen a validator, a guard, a lint rule or a test to make a run pass. A flaky test is a finding (OD-21), not a retry.
- **The release block and the fixture-only guards stay unchanged:** `app.config.ts` and `scripts/development.mjs`.
- **No dependency change:** `apps/mobile/package.json`, `package-lock.json`, `.npmrc` and `dependency-inventory.json` stay unchanged, and so does every dependency file in `packages/contracts/`.

**Findings outside this work:** report each with its class. Fix one here only if it could do one of the following, and then with a test:
- let a provider field, provider ID or provider text reach a render, a stored client state or a log;
- let a revoked member see a conversation's history or send in it;
- let the app make a network call, load a provider package, or run outside the development fixture mode.

**A departure** from any condition above that you find necessary: stop before making it, record it and the reason, and report it. It goes back to the Dev Manager (DM-27 item 3).

## 4. Checks

Report the exact commands and results.

1. **The diff:** `git diff --check <START_SHA> HEAD`, and `git diff --name-only <START_SHA> HEAD`. Only owned paths changed.
2. **Classification** with the trusted policy from `main`, run outside the tree, as root `AGENTS.md` requires. Expected: full scope. Pass full SHAs, not `HEAD`.

   ```bash
   base=$(git rev-parse origin/main); policy_dir=$(mktemp -d)
   git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
   python3 -I "$policy_dir/change_scope.py" --base <START_SHA> --head "$(git rev-parse HEAD)" --merge-base
   ```

3. **The installs** from the locks, in a clean process: `npm ci --ignore-scripts` for `packages/contracts` and `apps/mobile`. Install the mobile app first: the contracts' corpus test loads its generated validators.
4. **The offline checks,** with counts at the start and at your head:
   - **the contracts:** `npm run generate`, with no diff after it, and `npm run check`;
   - **the mobile app:** `npm run check`, `EXPO_OFFLINE=1 npm run check:expo` and `EXPO_OFFLINE=1 npm run export:development`;
   - `npm run test:rendered` only if it can run without `playwright install`, marked "informational, not the pinned browser".
5. **What stays unchanged:** an empty `git diff <START_SHA> HEAD` over:
   - `apps/mobile/package.json`, `package-lock.json`, `.npmrc` and `dependency-inventory.json`;
   - `apps/mobile/src/contracts/generated/`;
   - `apps/mobile/src/chat/fixture-adapter.ts`;
   - `apps/mobile/app.config.ts` and `apps/mobile/scripts/development.mjs`;
   - `packages/`, `services/`, `proofs/` and `.github/`.
6. **The reversals** of DM-27 1.2, each with the test's output.
7. **The Foundation run on your last code commit:** its run ID, each job's conclusion (eight jobs), and the gate's log line, which must be `Application checks passed`.
   - **Wait before pushing again.** After pushing your last code commit, push nothing more to your branch until that commit's Foundation run has finished. Runs of the same branch cancel each other (the CI policy), so an early records push can cancel the code run (AM5-14).
   - A push that changes only Markdown skips the application jobs. If your last commit changes only the record, the run of record is the push run of your last code commit, and your record says so.
   - **From the Mobile job's log:** `npm run check`'s test counts; the rendered tests' count, with the long-conversation test named and passing; the job's time and the rendered step's time, against the 15-minute timeout.
   - **The API mobile smoke** job's conclusion.
   - If your tools cannot read the run, or your branch is outside the push filter, say so; re-run or dispatch nothing.
8. **A secret scan over your whole diff:** no secret, token, API key, password or email address.

## 5. Owned paths, push and records

- **You may change:**
  - `apps/mobile/src/chat/store.ts` and `apps/mobile/src/chat/store.test.ts`;
  - `apps/mobile/src/chat/testing.ts`, only if a test needs a helper;
  - `apps/mobile/README.md`: its cursor sentence (DM-27 1.3);
  - the evidence record `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`: a new section "Stage C2-C3" only, after the existing sections, which stay byte-identical.
- **Nothing else.** That includes the fixture adapter, the screens, `packages/`, `services/`, `proofs/`, `.github/`, `scripts/`, any `.claude/` path, the briefs, the P11 plan and every other document. Report any other change you think is needed.
- **Commit and push** your session branch. Don't open a pull request.
- **Your section "Stage C2-C3"** in the evidence record:
  - the prompt's revision and start SHA, your head, your branch and the run of record;
  - for items 1 to 4 of section 3: done (`file:line` and its test) or left (the reason), and which test covers each of DM-27 1.1 and 1.2's cases;
  - why one test suffices, and every place `cursorKnown` was removed;
  - any change to an existing test and the rule that makes it;
  - every check, with its exact results;
  - deviations and limits;
  - what the exact-head re-review must know (DM-27 1.4): every assignment to `accepted` and `lastRead`.

## 6. Report

Your final message is the report Nathan relays:

- the prompt revision you received, and the commit it came from;
- the environment check;
- your branch, head SHA and tree, and the changed paths;
- for items 1 to 4 of section 3: done or left, with the recorded choices;
- every check, with its exact results, and the run of record's details from section 4 item 7;
- deviations, departures you stopped at, findings outside the work with their class, open questions and limits.

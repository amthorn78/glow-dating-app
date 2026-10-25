# P06.2 Stage C2-C1 prompt — correction pass: the read cursor moves only through viewed messages (CX8)

- **Owner:** App Manager 7. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 24 October 2026.**
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 16: "Codex's CX8, and C2-C1", with "Stage C under OD-45" (points e and g) and the owned paths for C2-C1.
  - Inputs:
    - the [DM-23 report](../continuity/dev-manager/reviews/2026-10-24-dm-23-p06-2-cx8.md) (`c8bc632`), whose conditions 2.1 to 2.6 and 3.1 are quoted below as written;
    - the evidence record's "Stage C2", "Exact-head review of Stage C2" and "Codex's code review of PR33's final head";
    - C2's prompt, item 8.
- **Where the result goes:**
  - the session's code and tests, and its section "Stage C2-C1" in the evidence record `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`;
  - the run of record: the Foundation run on its last code commit.

  The manager adds its verification and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 1.92 (confidence 0.81); rung probabilities low 0.00, medium 0.19, high 0.71, extra high 0.10, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.93, Sonnet 5.5 0.07, Haiku 5.5 0.00 (confidence 0.91). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.177, Opus 5.5 at high 0.660, Opus 5.5 at extra high 0.093, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.013, Sonnet 5.5 at high 0.050, Sonnet 5.5 at extra high 0.007, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-10-24T23:32:01Z. Nathan picks the cell.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** none, on DM-23 item 2's terms (DM-22 9.1's): this prompt quotes 2.1 to 2.6 as written; it changes no dependency and no contract; it starts in `Glow App - No Stream`, checks that no `STREAM_*` name is present, and authorizes no credential and no provider call. A departure found while it runs goes back to the Dev Manager first.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and the session calls no provider.
- **It runs alone** (OD-29). Its exact-head re-review follows (DM-23 2.6), then Codex's code review of the new final head (OD-41).
- **Deletion condition:** prune after Stage C2's PR merges and the evidence record holds the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **correction session P06.2 Stage C2-C1**, a correction pass on Stage C2 of P06.2, the chat integration of the Glow dating app, in the private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<START_SHA>`.

**What exists.** Stage C1 merged on 24 October (PR32, `a8e9528`). **Stage C2,** the mobile chat interface on fixtures, is PR33, from the manager branch `claude/magical-wozniak-yfmmx2` into `main`. Its code is `cb3a6a6`, unchanged since; the commits after it are Markdown records.

- **What C2 added,** under `apps/mobile/`: `src/chat/` (a `ChatTransport` interface, an in-process fixture adapter, a validating client, a polling store, the screens and their tests), the routes `/conversations` and `/conversation`, and `rendered/chat.spec.ts`.
- **C2's exact-head review** approved it, with six nits, none in a correction class.
- **Codex's code review of PR33's final head found CX8** (P2), which the manager verified:

  > When a conversation contains more messages than fit on screen, opening it immediately advances the read cursor to the last fetched message, even if that message is below the viewport. `ConversationScreen` renders the messages inside `Page`'s ordinary `ScrollView`, with neither visibility tracking nor scrolling to the newest message, so a member can open a long conversation and leave without seeing its latest messages while their unread count has already been cleared. Pass the last actually viewed accepted message from the screen to the store instead of treating a foreground fetch as evidence that the entire page was read.

- **Where it is:** `moveReadCursor` (`apps/mobile/src/chat/store.ts:243-259`) targets the newest fetched accepted message after every head read while the conversation is shown in the foreground. `Page` (`apps/mobile/src/components/ui.tsx:13-19`) is a plain `ScrollView` shared by every screen. `store.test.ts:141` asserts the defect: 25 messages, 13 unread, and unread 0 as soon as the conversation opens.
- **Why it is corrected now:** C2's prompt, item 8, asked for the cursor to move "when the member has seen newer messages". The Dev Manager read it in DM-23 and chose a correction pass before PR33 merges, with conditions.

**How you work:**
- Nathan started you manually and will relay your report to the manager (App Manager 7). You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs, including reading Expo's and React Native's versioned documentation as `apps/mobile/AGENTS.md` asks.
- Your boundary is scope:
  - write only your owned paths (section 5);
  - push only your own session branch. If your branch is under the workflow's push filter (`claude/**`), each push runs the Foundation workflow on it; read those runs if your tools can. On GitHub do nothing else: no pull request, no PR comments, no re-runs, no workflow dispatches. Change nothing in Notion.
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
git diff --quiet cb3a6a6dae0f3ad629a1cbd92ea299fcd5cab03a HEAD -- apps packages services proofs .github scripts && echo "C2's code"   # must print "C2's code"
git diff --stat <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- apps/ packages/ services/ proofs/ .github/   # must print nothing
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md | grep -c '^## Stage C2-C1'   # must print 0
```

- The last two commands check the live manager branch. If code or this stage's section has already landed there, this prompt is stale: stop and report (the manager workflow, step 3, AM5-15).
- If any check fails, stop and report.

Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md` and `apps/mobile/README.md`;
- the P06.2 brief, `docs/planning/p06-2-chat-integration.md`, revision 16: "Codex's CX8, and C2-C1", points e and g of "Stage C under OD-45", and the owned paths for C2-C1;
- the DM-23 report, `docs/continuity/dev-manager/reviews/2026-10-24-dm-23-p06-2-cx8.md`;
- C2's prompt, `docs/ephemeral/2026-10-24-p06-2-stage-c2-implementation-prompt.md`, item 8;
- the evidence record's "Stage C2", "Exact-head review of Stage C2" and "Codex's code review of PR33's final head";
- `apps/mobile/src/chat/` whole, `apps/mobile/src/components/ui.tsx`, and `apps/mobile/rendered/chat.spec.ts`.

## 3. The work

DM-23's conditions are quoted at their items, with their numbers. Meet each as written.

**DM-23's conditions 2.1 to 2.6, as written:**

> - **2.1 The rule.** The cursor moves forward only to the newest accepted message that has been inside the conversation's visible area, while the conversation was shown and the app was in the foreground.
>   - A page arriving never moves it by itself.
>   - The evidence that a message was viewed is the rendered layout: either visibility tracking on the message list, or the measured scroll position after scrolling to the message. It is never the fact that a fetch returned.
> - **2.2 Opening and new messages.**
>   - The screen may open at the newest message by scrolling to it. If it does, the cursor moves only once the scroll has placed that message in view (a measured position or a visibility callback), not when the scroll is requested.
>   - A message that arrives while the member is scrolled away from the newest does not move the screen and is not marked read. It is marked read when it is scrolled into view.
> - **2.3 The command.**
>   - At most one cursor command is in flight, as today.
>   - A command is sent only when the viewed position moves forward past a message from the other member, never on each scroll event.
>   - The existing rules hold: never backward, never to an unsent message, never for older pages.
> - **2.4 Tests,** each with its reversal in a scratch copy outside the checkout, showing the test fails without the fix:
>   - **The store's tests:**
>     - a page that arrives in the foreground while the conversation is shown, with nothing reported as viewed, sends no cursor command;
>     - reporting a viewed message moves the cursor to it and no further;
>     - reporting an older message moves nothing;
>     - `store.test.ts:141` is replaced: with 25 messages and 13 unread, only the viewed messages clear.
>   - **A rendered test** (hosted CI), with a conversation longer than the viewport:
>     - the unread count does not clear until the newest message is in view;
>     - with the member scrolled up, a new message from the other member leaves one unread until it is scrolled into view.
> - **2.5 Scope.**
>   - `apps/mobile` only, using React Native's own list or scroll interfaces.
>   - No dependency or contract change: `package.json`, `package-lock.json`, `dependency-inventory.json` and `src/contracts/generated/` unchanged.
>   - `Page`'s behaviour on every other screen is unchanged. If the conversation needs its own scroll container, it is the conversation's, and every other screen's rendered tests pass unchanged.
>   - The README's cursor sentence is corrected, with finding 1's sentence (3.1).
>   - The evidence record gains "Stage C2-C1".
> - **2.6 The re-review.** Its prompt names item 8 and CX8, and has the reviewer read the store's cursor path, the replaced unit test and the long-conversation rendered test. Codex's review of the new final head follows.
>   - C2's exact-head review confirmed DM-22 6.1 to 7.2 but not item 8's "seen".
>   - My DM-22 conditions for C2 named no test for "seen" either. The re-review closes that gap; nothing else changes.

**DM-23 3.1, as written:**

> **3.1 The change:**
>
> - C2-C1 corrects finding 1's README sentence, because C2-C1 edits the README anyway and a README must not claim more than its test checks. The README says the test fails on "any socket or event-stream construction"; it fails on the forms DM-22 7.1 names.
> - The rest stays a recorded follow-up, now due at the first change to `apps/mobile` after PR33 merges:
>   - finding 1's broader test;
>   - finding 4, restoring the draft on a final refusal;
>   - finding 5, the restricted-match assertions.

1. **The read cursor** (2.1 to 2.3): it moves forward only to the newest accepted message that has been in the conversation's visible area, as the rendered layout shows, while the conversation is shown and the app is in the foreground. You choose visibility tracking on the message list or a measured scroll position, and record the choice and why.
2. **The tests** (2.4): the store's four tests, with `store.test.ts:141` replaced, and the rendered long-conversation test's two cases, each with its reversal in a scratch copy outside the checkout.
3. **The scope** (2.5): `apps/mobile` only, through React Native's own list or scroll interfaces. If the conversation needs its own scroll container, it is the conversation's, and `Page` is unchanged on every other screen.
4. **The README** (2.5, 3.1): its read-cursor sentence states the rule of 2.1, and finding 1's sentence names the forms the no-provider test catches (the forms DM-22 7.1 names), not "any socket or event-stream construction".
5. **The record:** a new section "Stage C2-C1" in the evidence record.

**Not in C2-C1:**
- finding 3 of C2's review (it stays in the P11 plan);
- finding 1's broader test, finding 4 and finding 5 (follow-ups due at the first change to `apps/mobile` after PR33 merges, DM-23 3.1);
- any contract or dependency change (stop and report);
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

**A departure** from any condition above that you find necessary: stop before making it, record it and the reason, and report it. It goes back to the Dev Manager (DM-23 item 2; DM-22 9.1).

## 4. Checks

Report the exact commands and results.

1. **The diff:** `git diff --check <START_SHA> HEAD`, and `git diff --name-only <START_SHA> HEAD`. Only owned paths changed.
2. **Classification** with the trusted policy from `main`, run outside the tree, as root `AGENTS.md` requires. Expected: full scope.

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
   - `apps/mobile/app.config.ts` and `apps/mobile/scripts/development.mjs`;
   - `packages/`, `services/`, `proofs/` and `.github/`.
6. **The reversals** of 2.4, each with the test's output.
7. **The Foundation run on your last code commit:** its run ID, each job's conclusion (eight jobs), and the gate's log line, which must be `Application checks passed`.
   - **Wait before pushing again.** After pushing your last code commit, push nothing more to your branch until that commit's Foundation run has finished. Runs of the same branch cancel each other (the CI policy), so an early records push can cancel the code run (AM5-14).
   - A push that changes only Markdown skips the application jobs. If your last commit changes only the record, the run of record is the push run of your last code commit, and your record says so.
   - **From the Mobile job's log:**
     - `npm run check`'s test counts;
     - the rendered tests' count, with the long-conversation test named and passing;
     - the job's time and the rendered step's time, against the 15-minute timeout.
   - **The API mobile smoke** job's conclusion.
   - If your tools cannot read the run, say so; re-run or dispatch nothing.
8. **A secret scan over your whole diff:** no secret, token, API key, password or email address.

## 5. Owned paths, push and records

- **You may change:**
  - `apps/mobile/**`, except:
    - its dependency files (`package.json`, `package-lock.json`, `.npmrc`, `dependency-inventory.json`);
    - its generated contracts (`src/contracts/generated/**`);
    - `app.config.ts` and `scripts/development.mjs`;
  - the evidence record `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`: a new section "Stage C2-C1" only, after the existing sections, which stay byte-identical.
- **Nothing else.** That includes `packages/`, `services/`, `proofs/`, `.github/`, `scripts/`, any `.claude/` path, the briefs, the P11 plan and every other document. Report any other change you think is needed.
- **Commit and push** your session branch. Don't open a pull request.
- **Your section "Stage C2-C1"** in the evidence record:
  - the prompt's revision and start SHA, your head, your branch and the run of record;
  - for items 1 to 5 of section 3: done (`file:line` and its test) or left (the reason), and which test covers each of DM-23's 2.1 to 2.5;
  - the visibility mechanism you chose, and why;
  - every check, with its exact results;
  - deviations and limits;
  - what the exact-head re-review must know.

## 6. Report

Your final message is the report Nathan relays:

- the prompt revision you received, and the commit it came from;
- the environment check;
- your branch, head SHA and tree, and the changed paths;
- for items 1 to 5 of section 3: done or left, with the recorded choices;
- every check, with its exact results, and the run of record's details from section 4 item 7;
- deviations, departures you stopped at, findings outside the work with their class, open questions and limits.

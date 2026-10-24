# P06.2 Stage C2 prompt — the mobile chat interface on fixtures, offline

- **Owner:** App Manager 7. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 24 October 2026.**
- **Durable brief:** [P06.2 brief](../planning/p06-2-chat-integration.md), revision 15: "Stage C under OD-45", point g with DM-22 7.1 and 7.2, and the points it consumes (d, e and f with 6.1 to 6.4); item 5; Stage C2's owned paths; acceptance check 6.
  - Inputs:
    - [ADR 0003](../adr/0003-chat-display-rule.md);
    - the production contracts' "F11 under OD-45";
    - the evidence record's sections for Stage C1, C1-C1 and C1-C2, and "Stage C1's merge receipt";
    - the [DM-22 report](../continuity/dev-manager/reviews/2026-10-24-dm-22-p06-2-stage-c-read.md).
- **Where the result goes:**
  - the session's code and tests, and its section "Stage C2" in the evidence record `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`;
  - the run of record: the Foundation run on its last code commit.

  The manager adds its verification and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.40 (confidence 0.57); rung probabilities low 0.01, medium 0.11, high 0.38, extra high 0.48, max 0.02, ultracode 0.00. Model probabilities Fable 5.1 0.01, Opus 5.5 0.80, Sonnet 5.5 0.19, Haiku 5.5 0.00 (confidence 0.73). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.001, Fable 5.1 at high 0.004, Fable 5.1 at extra high 0.005, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.008, Opus 5.5 at medium 0.088, Opus 5.5 at high 0.304, Opus 5.5 at extra high 0.384, Opus 5.5 at max 0.016, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.002, Sonnet 5.5 at medium 0.021, Sonnet 5.5 at high 0.072, Sonnet 5.5 at extra high 0.091, Sonnet 5.5 at max 0.004, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Flags: boundary between high and extra high. Sent 2026-10-24T20:51:53Z. Nathan picks the cell.
  - **Nathan's pick:** recorded when he gives it.
- **The Dev Manager's read:** none, on DM-22 9.1's terms (B1's terms, DM-15 1.1 to 1.3):
  - this prompt states point g with 7.1 and 7.2 as written;
  - it changes no dependency file and no contract; a needed contract change stops the session;
  - it starts in `Glow App - No Stream`, checks at start that no `STREAM_*` name is present, and authorizes no credential and no network call to any provider;
  - no departure was found while it was written. A departure the session finds goes back to the Dev Manager first.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed, and the session calls no provider.
- **It runs alone** (OD-29). Its exact-head review follows, then Codex's code review of the final head (OD-41). P06.2 is done when C2 merges.
- **Deletion condition:** prune after Stage C2's PR merges and the evidence record holds the result.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **implementation session for P06.2 Stage C2**. C2 is the second and last part of Stage C of P06.2, the chat integration of the Glow dating app, in the private repository `amthorn78/glow-dating-app`. This prompt is revision 1, from commit `<START_SHA>`.

**What exists.** Stages A, B1, B2 and C1 are merged. C1 merged on 24 October as PR32, at `a8e9528`.

- **C1's contracts** are in `packages/contracts/production/gapp-api-v1.schema.json`, with the generated TypeScript and validators in `apps/mobile/src/contracts/generated/`:
  - `ConversationList`, of `ConversationSummary` items, each with a `LatestMessageMarker`;
  - `MessagePage`, of `ConversationMessage` items, with `older_cursor` and `newer_cursor`;
  - `MessagePageRequest`;
  - `ReadCursorIntent`, in the `AppIntent` union;
  - P02's `MessageIntent` and `MessageSubmission`, and `ChannelEntitlement` without `channel_ref`.

  Their rules are in `docs/architecture/production-contracts.md`, "F11 under OD-45".
- **C1's reads and projections** are in `services/api` (`glow_chat/reads.py`, `glow_domain/chat_reads.py`). Nothing is served: P11 serves them.
- **The mobile app** is a development-only fixture preview (Expo). P05's matches screens (`src/app/matches.tsx`, `src/app/match.tsx`) run on an in-process fixture adapter (`src/interactions/fixture-adapter.ts`), guarded in `src/app/_layout.tsx`. They validate what they accept with the generated validators and `src/contracts/production.ts`.
- **No app runtime has a network API, a database, real authentication or a live provider.**

**Why C2 exists.** On 24 October Nathan decided D8 as option (b) (OD-45): *"b, and I do think the stream architecture is still better than building our own, but I don't want features "snuck" in for sure"*.

- The app holds no Stream credential and no provider package.
- Glow's API serves history and new messages.

C1 built the server half and the contracts. C2 builds the mobile interface on those merged contracts, offline, on fixtures.

**How you work:**
- Nathan started you manually and will relay your report to the manager (App Manager 7). You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs, including reading Expo's versioned documentation as `apps/mobile/AGENTS.md` asks.
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
4. **The toolchain:** the pinned toolchain is in `$HOME/.local/bin`: Node 24.19.0 and npm 11.9.0 (and Python 3.12.14).
   - Put `$HOME/.local/bin` first on PATH in every process you run, then record `node --version` and `npm --version`.
5. **A clean process environment.** Run the mobile app's and the contracts' commands in a clean process environment, as `docs/operations/local-development.md` and each README show: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`EXPO_OFFLINE=1` where the mobile README uses it). Installs get the proxy and CA variables by reference, never printed.

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git merge --ff-only <START_SHA>          # on your own session branch
git rev-parse HEAD                       # must print <START_SHA>
git merge-base --is-ancestor a8e952895ebd3ffc9ef0e4d195c8a7111c69b3ae HEAD && echo "C1 present"   # must print "C1 present"
git diff --stat <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- apps/ packages/ services/ proofs/ .github/   # must print nothing
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-10-05-p06-2-chat-integration.md | grep -c '^## Stage C2'   # must print 0
```

- The fifth and sixth commands check the live manager branch. If code or this stage's section has already landed there, this prompt is stale: stop and report (the manager workflow, step 3, AM5-15).
- If any check fails, stop and report.

Then read, completely:

- root `AGENTS.md` and `CLAUDE.md`;
- `apps/mobile/AGENTS.md` and `apps/mobile/README.md`, and `packages/contracts/README.md`;
- `docs/operations/local-development.md`, on the mobile commands and the rendered tests in cloud sessions;
- the P06.2 brief, `docs/planning/p06-2-chat-integration.md`, revision 15: "What P06.2 delivers" (item 5), D1 to D8, the owned paths and "Stage C under OD-45" whole. Your design is point g; it consumes points d, e and f;
- ADR 0003, `docs/adr/0003-chat-display-rule.md`;
- the DM-22 report (`docs/continuity/dev-manager/reviews/2026-10-24-dm-22-p06-2-stage-c-read.md`). Its conditions on point g are quoted below;
- `docs/architecture/production-contracts.md`, F09 to F13 and "F11 under OD-45";
- the P06.2 evidence record's sections for Stage C1, C1-C1 and C1-C2, and "Stage C1's merge receipt";
- `apps/mobile/src/` whole, especially `app/`, `interactions/`, `contracts/` and `components/`, and `apps/mobile/rendered/` whole;
- `packages/contracts/production/` (the chat DTOs and the flow registry's chat entries) and `packages/contracts/fixtures/`;
- `.github/workflows/foundation.yml`: the `mobile` and `smoke` jobs, and the gate.

## 3. The work

Each item names its design point in "Stage C under OD-45". DM-22's conditions are quoted at their items, with their numbers. Meet each as written.

**Point g, as written in the brief** (with DM-22 7.1 and 7.2):

> **g. The mobile interface (C2).** Item 5 on fixture adapters, against C1's contracts.
> - **The screens:** the conversation list, a conversation and its composer, with unread, older pages, point d's polling, retry and the revoked state.
> - **Built as P05's matches screens are.** The app accepts a response only if the generated validator accepts it.
> - **No provider in the app.** No Stream package, no provider SDK and no new dependency: `package.json` and `package-lock.json` are unchanged. `fetch` only, and no WebSocket.
> - **The display-rule test** (ADR 0003; item 5).
>   - A fixture response that carries any provider field is refused by the validator and shows Glow's own error state. Provider fields include a member or user object, custom data, `member.updated`, `ai_indicator.*`, a channel name or image, and a provider ID or error text.
>   - The render shows only Glow API data.
>   - A test asserts that the app's source and lock name no provider package.
> - **Point d's intervals** are constants in code, with tests on fixture time.
> - **DM-22's conditions on point g** (as written):
>   - **7.1 The no-provider test names what it looks for:**
>     - any package whose name contains `stream-chat`, `getstream` or `@stream-io/`, in `package.json`, `package-lock.json` and any import under `apps/mobile/src`;
>     - any construction of `WebSocket` or `EventSource` in the app's source, since point g says "`fetch` only, and no WebSocket".
>   - **7.2 Polling stops in the background.** A test on fixture time with the app state in the background shows no request. "Unavailable" renders in Glow's own wording, with no reason (6.2).

**The chat fixture adapter** (point g: "on fixture adapters"; "Built as P05's matches screens are")

1. Add an in-process chat fixture adapter under `apps/mobile/src/` (you name the module). It answers what Glow's API will answer:
   - the conversation list;
   - a page of messages, older and newer;
   - a send (`MessageIntent`, answered with `MessageSubmission`);
   - the read-cursor command (`ReadCursorIntent`).

   **Its semantics are C1's** (F11 under OD-45; points b, e and f with 6.1 to 6.4):
   - messages in acceptance order;
   - the member's own pending or failed submissions appear only to that member, and the other member's never appear (F11);
   - "unavailable" is one state with no reason field (6.2);
   - the latest-message marker is computed only over rows the member may see, and carries no text (6.1);
   - the unread count counts only the other member's accepted messages after the member's cursor (6.3);
   - the cursor moves only forward, and only to an accepted message of that match (point e);
   - the page cursor is opaque and bound to its match; a cursor from another match is refused (6.4).
2. **Validation at the boundary.** Every response the screens use passes the generated validator for its DTO, and `assertUniqueKeys` where `src/contracts/` applies it, before the screens see it. Every intent the app builds passes `parseAppIntent`. A response the validator refuses gives Glow's own error state, never a partial render.
3. **A conversation follows its match.** A conversation exists only for a match the interactions fixture holds. An unmatch or a block in that fixture gives the conversation's revoked state, for each member the fixture can show, by point c's rule: whatever refuses a send refuses a read.
   - The refusal is one of Glow's codes. It tells a member no more about why the conversation ended than the match's projection already shows (F10, F13).
   - The fixture applies point c's interim rule (DM-22 3.1). If the fixture already models a pause, restriction, suspension or consent withdrawal, it refuses for those too. Add no new member-state model for this.
4. **Retry and lost responses**, as P05's interaction scenarios model them (normal, offline, lost response, delayed). A retried send reuses the same idempotency key and payload (the production contracts' idempotency rule), and the conversation shows one message for it, keyed on `submission_id`.
5. **Keys and order.** The app keys messages on `submission_id`, never on `at`. It shows them in the order the page gives (the production contracts' note on `ConversationMessage.at`). It asks for newer messages with the page's opaque `newer_cursor`, and for older ones with `older_cursor`. It never computes a position from `at`.
   - **A test:** a message the fixture accepts after a later one reaches the reader's next poll and counts as unread (C1's DM-22 2.2 order, consumed).
6. **No transport in C2.** The screens read through an adapter interface, and C2's implementation of it is the in-process fixture, as P05's is.
   - C2 adds no network client, no API URL and no route to a server: Glow's API serves nothing before P11, which connects the adapter to it.
   - If you find the app needs a transport now, stop and report.
   - Fixture data lives under `apps/mobile/src/`. `packages/contracts/**`, including its fixtures and corpus, stays unchanged. If you need a shared fixture or corpus case there, that is a contract change: stop and report.

**The screens** (point g; item 5)

7. **The conversation list, a conversation and its composer:**
   - with unread, older pages, point d's polling, retry and the revoked state;
   - as routes in `src/app/`, guarded as `/matches` is, and reachable from a match;
   - with Glow's own wording for every state, including "unavailable" with no reason (7.2, 6.2);
   - with no other member's read state anywhere. Read receipts are not built (point e).
8. **The read cursor** (point e): the app moves the member's own cursor forward with `ReadCursorIntent` when the member has seen newer messages, and never backward.

**Polling** (point d, with 7.2)

9. **The intervals are constants in code**, each with tests on fixture time:
   - in an open conversation, a request for newer messages every 3 seconds while the app is in the foreground;
   - the conversation list read when shown, and every 30 seconds while it stays shown;
   - nothing in the background (7.2): a test with the app state in the background shows no request;
   - polling stops when the screen is left, and resumes on return to the foreground.

**The display-rule test** (point g, with 7.1)

10. **A fixture response carrying a provider field.** For each provider field point g lists, a fixture response carrying it is refused by the validator and shows Glow's own error state. The render shows only Glow API data. Provider fields include:
    - a member or user object;
    - custom data;
    - `member.updated` and `ai_indicator.*`;
    - a channel name or image;
    - a provider ID or error text.
11. **The no-provider test (7.1).** It fails on:
    - any package whose name contains `stream-chat`, `getstream` or `@stream-io/`, in `package.json`, `package-lock.json` and any import under `apps/mobile/src`;
    - any construction of `WebSocket` or `EventSource` in the app's source.

    Show, in a scratch copy, that a planted import of each kind and a planted `new WebSocket(` each make it fail.

**The rendered journeys** (acceptance check 6: `test:rendered` in hosted CI)

12. Add rendered specs under `apps/mobile/rendered/` for:
    - the list, opening a conversation, a send and its retry, an older page and the revoked state;
    - the provider-field fixture's error state.

    A local run against a browser that is not the pinned revision is informational only. The pinned-browser evidence comes from hosted CI (`apps/mobile/AGENTS.md`).
    - **The Mobile job has a 15-minute timeout.** At `737a7af` the job took 5 min 36 s, and its rendered step 3 min 30 s (run 40130871253).
    - Report both times on your run of record. If the job comes within 3 minutes of its timeout, say so: the workflow is not yours.

**The documents**

13. Update `apps/mobile/README.md` with the chat screens' walkthrough and their verified limits.

**Not in C2:**
- any contract change (stop and report);
- any dependency;
- a network client, an API URL, a WebSocket, `EventSource` or any realtime service;
- push and notifications (P06.3);
- read receipts;
- removing the dormant token code (point h);
- any live call;
- any change to `services/`, `proofs/`, `packages/` or `.github/`.

**Rules for every change:**
- **A test for each change.** Each code item gets a test that fails without the change and passes with it. Say which test covers which item and which DM-22 condition.
- **Reversals in a scratch copy, never the checkout.** Make each fix reversal in a copy outside the repository, with absolute paths. Confirm afterwards that `git status` is clean.
- **No weakened check.** Never loosen a validator, a guard, a lint rule or a test to make a run pass. A flaky test is a finding (OD-21), not a retry.
- **The release block and the fixture-only guards stay unchanged:** `app.config.ts` and `scripts/development.mjs`.
- **No dependency change:** `apps/mobile/package.json`, `package-lock.json`, `.npmrc` and `dependency-inventory.json` stay unchanged. Every dependency file in `packages/contracts/` stays unchanged too.

**Findings outside this work:** report each with its class. Fix one here only if it could do one of the following, and then with a test:
- let a provider field, provider ID or provider text reach a render, a stored client state or a log;
- let a revoked member see a conversation's history or send in it;
- let the app make a network call, load a provider package, or run outside the development fixture mode.

**A departure** from any point above that you find necessary: stop before making it, record it and the reason, and report it. It goes back to the Dev Manager (DM-22 9.1; DM-15 1.3).

## 4. Checks

Report the exact commands and results.

1. **The diff:** `git diff --check <START_SHA> HEAD`, and `git diff --name-only <START_SHA> HEAD`. Only owned paths changed.
2. **Classification** with the trusted policy from `main`, run outside the tree, as root `AGENTS.md` requires. Expected: full scope.

   ```bash
   base=$(git rev-parse origin/main); policy_dir=$(mktemp -d)
   git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
   python3 -I "$policy_dir/change_scope.py" --base <START_SHA> --head "$(git rev-parse HEAD)" --merge-base
   ```

3. **The installs** from the locks, in a clean process: `npm ci --ignore-scripts` for `packages/contracts` and `apps/mobile`.
4. **The offline checks,** with each component's documented commands. Give counts at the start and at your head.
   - **The contracts:** `npm run generate`, with no diff after it, and `npm run check`.
   - **The mobile app:**
     - `npm run check`;
     - `EXPO_OFFLINE=1 npm run check:expo`;
     - `EXPO_OFFLINE=1 npm run export:development`;
     - `npm run test:rendered` only if it can run without `playwright install`, marked "informational, not the pinned browser".
5. **What stays unchanged:** an empty `git diff <START_SHA> HEAD` over:
   - `apps/mobile/package.json`, `package-lock.json`, `.npmrc` and `dependency-inventory.json`;
   - `apps/mobile/src/contracts/generated/`;
   - `apps/mobile/app.config.ts` and `apps/mobile/scripts/development.mjs`;
   - `packages/`, `services/`, `proofs/` and `.github/`.
6. **7.1's planted failures** (item 11), each with the test's output.
7. **The Foundation run on your last code commit:** its run ID, each job's conclusion (eight jobs), and the gate's log line, which must be `Application checks passed`.
   - **Wait before pushing again.** After pushing your last code commit, push nothing more to your branch until that commit's Foundation run has finished. Runs of the same branch cancel each other (the CI policy), so an early records push can cancel the code run (AM5-14).
   - A push that changes only Markdown skips the application jobs. If your last commit changes only the record, the run of record is the push run of your last code commit, and your record says so.
   - **From the Mobile job's log:**
     - `npm run check`'s test counts;
     - the rendered tests' count, with your new specs named and passing;
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
  - the evidence record `docs/testing/evidence/2026-10-05-p06-2-chat-integration.md`: a new section "Stage C2" only, after the existing sections, which stay byte-identical.
- **Nothing else.** That includes `packages/`, `services/`, `proofs/`, `.github/`, `scripts/`, any `.claude/` path, the briefs, the production contracts, the P11 plan and every other document. Report any other change you think is needed.
- **Commit and push** your session branch. Don't open a pull request.
- **Your section "Stage C2"** in the evidence record:
  - the prompt's revision and start SHA, your head, your branch and the run of record;
  - for items 1 to 13 of section 3: done (`file:line` and its test) or left (the reason), and which test covers each DM-22 condition (6.1 to 6.4, 7.1, 7.2);
  - the screens' routes, the adapter's module, and the choices you made;
  - every check, with its exact results;
  - deviations and limits;
  - what the exact-head review must know.

## 6. Report

Your final message is the report Nathan relays:

- the prompt revision you received, and the commit it came from;
- the environment check;
- your branch, head SHA and tree, and the changed paths;
- for items 1 to 13 of section 3: done or left, with the recorded choices;
- every check, with its exact results, and the run of record's details from section 4 item 7;
- deviations, departures you stopped at, findings outside the work with their class, open questions and limits.

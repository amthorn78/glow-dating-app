# P06.3 exact-head review prompt — privacy-safe notifications at fixture scope

- **Owner:** App Manager 10. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 9 November 2026. Revision 2, 9 November 2026:** adds Codex's finding on `1dc1b0b` (F-C1), which the manager reproduced, to "What came before" and the focus (item 8). Revision 1 was not given.
- **Durable brief:** [P06.3 — Privacy-safe notifications at fixture scope](../planning/p06-3-notifications.md), revision 2, "Review plan" (DM-44 9.1).
- **Where the result goes:** the report Nathan relays. The manager records it in the P06.3 record, "Exact-head review of P06.3", with a disposition for each finding (fix before the merge, or carry), and in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Fable 5.1 at extra high.** Effort score 3.33 (confidence 0.77); rung probabilities low 0.00, medium 0.00, high 0.01, extra high 0.65, max 0.34, ultracode 0.00. Model probabilities Fable 5.1 0.86, Opus 5.5 0.14, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.81). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.009, Fable 5.1 at extra high 0.559, Fable 5.1 at max 0.292, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.000, Opus 5.5 at high 0.001, Opus 5.5 at extra high 0.091, Opus 5.5 at max 0.048, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-09T00:44:13Z. Nathan picks the cell. This is revision 1's reading. Revision 2 adds one focus item and changes none of the facts the action text states (the uses table's row).
- **The Dev Manager's read:** none before it runs. The review authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29), after Codex's review of P06.3's PR head and of this prompt's commit (manager workflow, step 6).
- **Deletion condition:** prune after P06.3's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<PROMPT_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **exact-head code review of P06.3**, privacy-safe notifications at fixture scope, for the Glow dating app, in the public repository `amthorn78/glow-dating-app` (public for now; OD-51). You review one exact code head, with a written threat model. This prompt is revision 2, from commit `<PROMPT_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What came before.**
- **The brief,** `docs/planning/p06-3-notifications.md`, revision 2. Its Outcome items 1 to 5 and D1 to D12 apply the Dev Manager's conditions word for word (DM-44, `docs/continuity/dev-manager/reviews/2026-11-08-dm-44-p06-3-brief.md`):
  - a server composer in `glow_domain`;
  - F12's devices and settings per installation, with token custody;
  - a mobile settings screen whose permission request comes only from turning a kind on;
  - one route-guard entry and one `Stack.Protected` line;
  - no native module, provider, network client, credential, dependency, contract or model change.
- **The implementation** (branch `claude/gallant-lovelace-vwgu69`, code head `9c4fef5`, records `7775bba`; record `docs/testing/evidence/2026-11-09-p06-3-notifications.md`): Outcomes 1 to 5, with 26 reversals (16 server, 10 mobile), each failing its test. Nothing met the stop rule. Its fixture-scope decisions where the contract is silent are recorded in the record:
  - `NotificationSettings.version` is the installation's view revision;
  - the mobile adapter keeps its own record of current sessions;
  - the store waits one microtask before acting on an account change.
- **Its run of record,** push run 42540179430 on `9c4fef5`:
  - all eight jobs passed, and the gate printed `Application checks passed`;
  - API `Ran 421 tests`, mobile 680 unit tests, and rendered `104 passed (4.7m)`;
  - no retry fired.
- **The manager verified it** (the record, "Manager verification"):
  - the diff within the owned paths;
  - a search for clients, providers and native modules;
  - six reversals re-run, each failing.

  The manager then integrated it, so the manager branch fast-forwarded to `7775bba`.
- **Codex's review of `1dc1b0b`** (PR41's head, whose code is `9c4fef5`'s) found one thing, **F-C1** (P2, `apps/mobile/src/notifications/fixture-adapter.ts:111`):
  - **The claim:** `device`, `settings` and `notifications` each take the session's account (`capture`) before `await this.gate()`, and act on it after. So a request that starts while its session is current, and whose session's `ended()` runs before the gate resolves, still acts for the ended session.
  - **The manager's reproduction** (a scratch probe at `1dc1b0b`, Node's test runner): start `device(session, …, register)`, call `ended(session)`, then await the request. The answer is a success with `device_state: 'active'`; the registration is `active`, bound to the ended session; `heldTokens` is 1.
  - **Not affected:** the Python domain, which is authoritative, checks the session inside each command, synchronously.
  - The manager replied on its thread. **Under step 6 it joins this review's pass:** its fix goes in the correction pass after this review, with any findings of yours.

**The code head under review is `9c4fef5`.** You work at `<PROMPT_SHA>`, whose non-Markdown paths are byte-identical to `9c4fef5` (the start gate checks this).

**Your scope:**
- `git diff f9253bd9b0356c95a491df553b17b595105935fd 9c4fef54c71829dea2820a3f9fb66f32ddad57d2`: 24 paths, under `services/api/glow_domain/`, `services/api/tests/`, `apps/mobile/src/notifications/`, `apps/mobile/src/app/` (`notifications.tsx`, one line each in `_layout.tsx` and `profile.tsx`), `apps/mobile/src/onboarding/routes.ts` and `apps/mobile/rendered/`.
- **The P06.3 record,** with its "Manager verification", against the code and the runs.
- **The runs:** run 42540179430, and the PR run on P06.3's PR head (event `pull_request`) once it has finished.
- **Out of scope:** code this item does not change. A finding there is reported as pre-existing, not as a defect of this item.

**The threat model** (DM-44 9.1). Write it in your report: assets, actors, entry points, and for each threat the code that stops it and the test that proves it. It covers:
1. **The device and token path:**
   - custody: the token reaches the store before its reference is saved, and a refused store saves nothing;
   - the discard on revoke, logout, transfer and rotate, and a failed discard kept for retry;
   - the reference, never the token, at the transport;
   - logs, receipts, exceptions and `repr`/`str`: no token anywhere, and no reference in a read, log or refusal.
2. **The route's enforcement:** the layout's `Stack.Protected` line, its rendered test and that test's reversal. Also `sanitizeDestination` keeping `/notifications` as a destination, while `canAccessRoute` decides access.
3. **The composer's content and recipients:**
   - no body, name, identifier or count in a push;
   - a message never notifies its sender, and a match never notifies the member who completed it;
   - the read rule's refusals (`chat_reads.py`: whatever refuses a send refuses a read), read on each delivery, never from the trigger;
   - the fixed routes.
4. **Redelivery:**
   - the first delivery fixes the devices;
   - a retry sends only to a fixed device not yet accepted and still active;
   - the ledger records a send only on the transport's acceptance, and the transport's idempotency key is the ledger key.
5. **The session binding:**
   - stale-session commands refused;
   - each registration records its session;
   - logout revokes only the ending session's registrations;
   - a transfer revokes the earlier account first;
   - on mobile, the revoke is sent while the session is current, then the screen is cleared.
6. **The fixture-only guards:** no provider, network client, native module, config plugin or credential. The served runtime does not import the new modules.

**The focus:**
1. **The threat model above,** each threat with its stopping code and its test.
2. **DM-44's conditions met in code:**
   - 1.1 and 1.2 (F12 per installation; the session binding);
   - 2.1 and 2.2 (recipients; refusals);
   - 3.1 to 3.3 (custody; the custody test; redelivery);
   - 4.1 to 4.3 (the denied path saves nothing; the context sentence; revoke before logout);
   - 6.1 to 6.3 (the guard line and its tests).

   Name any condition the code does not meet.
3. **No guard allows anything new** beyond D7: `SAFE_ROUTES`, `canAccessRoute` and `_layout.tsx` change only as D7 says. The release guard, `app.config.ts` and the layout's development check are unchanged.
4. **No test is weakened or vacuous:**
   - each new test fails under the reversal the record names;
   - none could pass while the behavior it guards is wrong;
   - the source-reading tests (`fixture-scope.test.ts`, `copy.test.ts`, the server's `FixtureScopeTests`) are not defeated by a plausible edit, and do not fail on harmless code;
   - no existing test changed.
5. **The session's fixture-scope decisions** (the version as the installation's view revision; the adapter's own session record; the one-microtask wait): each is correct at fixture scope, harmless, and recorded for SV4. Does any hide a race, such as a revoke lost or sent after the session ends?
6. **The display rule and the copy** (ADR 0003, decision 3): no provider, platform or push-service name in member-visible copy. The push wording is D4's exactly.
7. **The records:** every claim in the record, and in its "Manager verification", holds against the code and the runs.
8. **Codex's F-C1:**
   - confirm or refute it, and give its severity and correction class;
   - say whether the store's own flows can reach it (for example, a register in flight when the member logs out or the account changes, given the one-microtask wait);
   - name every other place with the same pattern of checking before an `await` and acting after, in the adapter, the store or the client;
   - say what a fix and its test should cover. The correction pass makes the fix, not you.

**Re-run, at least** (DM-44 9.1), in a scratch copy of `9c4fef5`:
- **the custody test's reversal:** the register path's log line given the token. `CustodyCaptureTests` must fail;
- **the layout line's reversal:** the `Stack.Protected` line for `/notifications` removed. `rendered/notifications.spec.ts`'s signed-out, suspended and deletion-pending tests must fail. Run it against the container's preinstalled Chromium, with a scratch config outside the checkout, as the record describes. It is informational, and you name it so;
- any other reversal you doubt.

**What comes after this review: the correction classes.** Report every finding with its severity. A correction pass takes every blocking finding, and any should-fix finding that could do any of these:
- let a push token, a reference, a name, a message body, an identifier or a provider detail reach a log, a read, a refusal, the transport or member-visible output;
- let a member be notified where the read rule refuses, or twice for one trigger on one device;
- let a stale session act, or leave a registration active after its session's logout;
- let a guard allow what it did not allow at `f9253bd`, beyond D7;
- let a test pass where it should fail, or weaken what a test proves;
- leave a DM-44 condition unmet;
- add a dependency, change a lock, a contract, a model or a migration, or make the served runtime load the new modules;
- make a record claim more than the code, the tests or the runs show.

Everything else goes into the records. For each finding, say whether it falls in one of these classes.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 10. You are neither the manager nor an implementer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the review needs, including Claude Code's code-review and security-review capabilities.
- Your boundary is scope: review one exact head and report.
  - **Change nothing** in the repository, on GitHub or in Notion: no commits, pushes, PR comments, re-runs or workflow dispatches.
  - **Scratch work goes in a copy outside the repository,** never the checkout (DM-14 item 6). Use absolute paths, and confirm afterwards that `git status` is clean.
- **Network:**
  - the npm registry, for `npm ci --ignore-scripts` in a scratch copy;
  - PyPI, for `pip install --require-hashes -r requirements-dev.lock` in a scratch copy;
  - `docs.expo.dev`, for the SDK 58 pages;
  - GitHub, through your tools, to read runs.
- **Rendered tests:** CI's run is the evidence. Local runs against the container's preinstalled Chromium are informational. Never run `playwright install`.
- **Never:**
  - dump the environment, or print a credential, token or password;
  - call Stream, Expo's push service or any other provider, or run any command in `proofs/stream-chat/`;
  - connect to any database, HDE, Railway or other external service;
  - run `playwright install`, `eas` or `migrate`, a native build, or a package install script.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If any is present, stop and report: this session must start in `Glow App - No Stream`.
3. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
4. **The toolchain:**
   - Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, first on PATH;
   - CPython 3.12.14 as `python3.12`.

   Record their versions.
5. **A clean process environment** for every repository command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (`GLOW_ENV=test` for the API).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch --detach <PROMPT_SHA>
git rev-parse HEAD                                    # must print <PROMPT_SHA>
git merge-base --all origin/main HEAD                 # expected: one line, 7feba0dbc3813ab71629b3f5e0f390a64d31289f
git merge-base --is-ancestor <PROMPT_SHA> origin/claude/magical-wozniak-yfmmx2 && echo "this prompt's commit is on the live branch"
git diff --quiet 9c4fef54c71829dea2820a3f9fb66f32ddad57d2 HEAD -- .github scripts services apps packages proofs && echo "the code head under review"
git diff --quiet 9c4fef54c71829dea2820a3f9fb66f32ddad57d2 origin/claude/magical-wozniak-yfmmx2 -- .github scripts services apps packages proofs && echo "no code on the live branch after 9c4fef5"
git show origin/claude/magical-wozniak-yfmmx2:docs/testing/evidence/2026-11-09-p06-3-notifications.md | grep -c -E '^#+ Exact-head review of P06.3'   # must print 0
```

If any check fails, stop and report. The prompt is stale if its commit is not on the live branch, if a non-Markdown path changed there after `9c4fef5`, or if this review is already recorded.

**Classify the change** as root `AGENTS.md` requires, with the trusted base policy outside the candidate tree:

```bash
base=$(git rev-parse origin/main); head=$(git rev-parse HEAD)
policy_dir=$(mktemp -d)
git show "$base:scripts/change_scope.py" > "$policy_dir/change_scope.py"
python3 -I "$policy_dir/change_scope.py" --base "$base" --head "$head" --merge-base
```

Expected: `"full": true`. Anything else: stop and report.

**Then read, completely, at `HEAD`:**
- root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md`; `services/api/README.md`;
- the brief, revision 2, and DM-44's report;
- the P06.3 record, whole;
- ADR 0003 (`docs/adr/0003-chat-display-rule.md`);
- F12 (`packages/contracts/production/flows-v1.json`) and the `NotificationSettings`, `NotificationIntent`, `DeviceIntent` and `CommandMeta` schemas;
- `services/api/glow_domain/chat_reads.py` and `glow_chat/contact.py`'s send checks, for the read rule;
- every file in the diff, whole: `glow_domain/notifications.py`, `notification_fixtures.py`, `src/notifications/store.ts` and `fixture-adapter.ts` above all.

**The runs,** with your GitHub tools:
- run 42540179430: every job's conclusion, the gate's line, the API test count, the Mobile job's rendered result and its duration;
- the PR run on P06.3's PR head, if it has finished.

## 3. What to do

1. Write the threat model, then review the diff against the focus, item by item.
2. In a scratch copy of `9c4fef5`, re-run:
   - the API's checks (`manage.py check`, `manage.py test tests`, `ruff`, `mypy`) and the mobile app's `npm ci --ignore-scripts` and `npm run check`;
   - the two required reversals, and any you doubt.
3. For each finding: its severity (blocking, should fix, nit), its file and line, the evidence, and whether it falls in a correction class.

## 4. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 2, from `<PROMPT_SHA>`), and the start gate's, the classification's and the environment check's results;
- **the verdict:** approve, approve with nits, or changes required;
- the threat model;
- the findings, in a table: number, severity, correction class or not, file and line, what is wrong, and the evidence;
- the answer to each focus point (1 to 8), one or two lines each;
- the reversals you re-ran, with their results, the local rendered ones named informational;
- what you ran, and what you could not run or read.

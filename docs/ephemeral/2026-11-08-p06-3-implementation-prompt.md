# P06.3 prompt — privacy-safe notifications at fixture scope

- **Owner:** App Manager 10. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 8 November 2026.**
- **Durable brief:** [P06.3 — Privacy-safe notifications at fixture scope](../planning/p06-3-notifications.md), revision 2.
- **Where the result goes:**
  - the session's changes in `services/api` and `apps/mobile`, and its record, `docs/testing/evidence/<date>-p06-3-notifications.md`, on its own branch;
  - the run of record: the Foundation run on its last code commit, with the rendered suite;
  - the manager adds its verification to the record and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 3.39 (confidence 0.59); rung probabilities low 0.00, medium 0.01, high 0.11, extra high 0.35, max 0.52, ultracode 0.01. Model probabilities Fable 5.1 0.15, Opus 5.5 0.80, Sonnet 5.5 0.05, Haiku 5.5 0.00 (confidence 0.73). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.002, Fable 5.1 at high 0.017, Fable 5.1 at extra high 0.052, Fable 5.1 at max 0.078, Fable 5.1 at ultracode 0.002, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.008, Opus 5.5 at high 0.088, Opus 5.5 at extra high 0.280, Opus 5.5 at max 0.416, Opus 5.5 at ultracode 0.008, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.001, Sonnet 5.5 at high 0.006, Sonnet 5.5 at extra high 0.017, Sonnet 5.5 at max 0.026, Sonnet 5.5 at ultracode 0.001, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Flags: boundary between extra high and max. Sent 2026-11-08T23:20:43Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The brief's revision 2 applies DM-44's conditions as written, so it needs no read before the prompt (DM-44 1.3). This prompt authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Then come the manager's verification, the PR, Codex's review of its head, and an exact-head code review with a written threat model (the brief's review plan).
- **Deletion condition:** prune after P06.3's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **implementation session for P06.3**, privacy-safe notifications at fixture scope, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What P06.3 is.** You build three things, with stand-in implementations only:
- **the server's notification composer** (`services/api/glow_domain`), which turns a match activation or an accepted message into a privacy-safe push: Glow's fixed wording and a fixed route, with no name, message text, birth data, compatibility data, identifier or provider detail;
- **F12's devices and settings,** with the push token held only as a reference;
- **the mobile app's notification settings screen** (`apps/mobile`), whose permission request comes only from the member turning a kind on.

There is no real push transport, push credential, network client or native module. **The brief, `docs/planning/p06-3-notifications.md`, revision 2, is the specification:** its Outcome items 1 to 5 and D1 to D12. Its words are the Dev Manager's (DM-44), applied as written, so follow them exactly. Where this prompt summarizes the brief, the brief wins.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 10. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only the brief's "Owned paths (the session)";
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule.** Stop and report, with no further change, if any of these holds:
  - **a guard's allowance:** the work would change what any guard allows beyond D7's own changes, which are one entry in `SAFE_ROUTES` and `canAccessRoute` with `/profile`'s rule, and one `Stack.Protected` line in `src/app/_layout.tsx`; or it would change `_layout.tsx` in any other way. This covers the route guard, `app.config.ts`'s environment or public-name checks, and the layout's development check;
  - **a dependency:** the work seems to need a dependency or a lock change, mobile or Python, `expo-notifications` included (D6);
  - **a contract or model:** it seems to need a change to a contract, a model or a migration (D9);
  - **an owned path:** it would need a path outside the owned paths. This includes anything under `apps/mobile/src/chat/` (D10; option (c)'s trigger), `services/api/glow_chat/`, `glow_persistence/`, `glow_api/` or `packages/`;
  - **the read rule:** reusing it (`glow_domain/chat_reads.py`) would need a change to that file. You may import from it, or read the same facts through a port with a fixture implementation.
- **The push rule** (AM5-04). After you push a code commit, push nothing more to your branch until that commit's Foundation run has finished. A newer push cancels the earlier run's application jobs, and the run of record is lost. Push your records commit only after the run of record has finished.
- **Network:**
  - the npm registry, for `npm ci --ignore-scripts`;
  - PyPI, for `pip install --require-hashes -r requirements-dev.lock`;
  - `docs.expo.dev`, to read the versioned SDK 58 pages before any Expo claim (`apps/mobile/AGENTS.md`, "Expo has changed").

  A page you cannot reach is named as unread, never filled from memory.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, token or password, in any form. The synthetic push tokens you make are test data; make them obviously synthetic;
  - call Stream, Expo's push service or any other provider, or run any command in `proofs/stream-chat/`;
  - connect to any database, HDE, Railway or other external service;
  - run `playwright install`, `eas`, `eas-cli`, `migrate`, or a native build (`run:ios`, `run:android`, `prebuild`);
  - run package install scripts: always `npm ci --ignore-scripts`;
  - weaken or delete a test to make the suite pass.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If any is present, stop and report: this session must start in `Glow App - No Stream`.
3. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`). Never read them; every command below runs without them.
4. **The toolchain:**
   - Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, first on PATH in every process;
   - CPython 3.12.14 as `python3.12` (`services/api/.python-version`).

   Record `node --version`, `npm --version` and `python3.12 --version`.
5. **A clean process environment** for every npm, Expo and API command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables (for the API, `GLOW_ENV=test` where its README sets it). The proxy and CA variables pass by reference, never printed (`docs/operations/local-development.md`).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git merge-base --is-ancestor 803136196ed68161aca55d46bd6fb8305954bdef HEAD && echo "PR40 present"   # main's merge of P06.2-F; must print "PR40 present"
git diff --name-only 803136196ed68161aca55d46bd6fb8305954bdef HEAD | grep -v -E '\.md$'             # against main: must print nothing
git diff --name-only <START_SHA> origin/claude/magical-wozniak-yfmmx2 -- apps/mobile services/api 'docs/testing/evidence/*p06-3-notifications*'   # must print nothing
grep -E '"(expo|expo-router|react-native)":' apps/mobile/package.json                              # expected: expo 58.0.22, expo-router 58.0.29, react-native 0.88.1
for f in services/api/glow_domain/notifications.py apps/mobile/src/notifications apps/mobile/src/app/notifications.tsx; do test -e "$f" && echo "$f exists"; done   # must print nothing
grep -c "canAccessRoute('/notifications'" apps/mobile/src/app/_layout.tsx                          # must print 0
```

If a check fails, stop and report. The prompt is stale if `<START_SHA>` is not on the live manager branch, if the live branch has changed an owned path since it, or if the brief's "Sessions" already records an implementation session.

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md`, `apps/mobile/CLAUDE.md` and `apps/mobile/README.md`; `services/api/README.md`;
- the brief, revision 2, whole;
- DM-44's report, whole: `docs/continuity/dev-manager/reviews/2026-11-08-dm-44-p06-3-brief.md`. Its "Tried" tables are cases your tests should cover;
- ADR 0003 (`docs/adr/0003-chat-display-rule.md`), decisions 2 and 3;
- **F12:**
  - in `packages/contracts/production/flows-v1.json` (transitions, forbidden list, read roles, projections) and in `docs/architecture/production-contracts.md`;
  - the `NotificationSettings`, `NotificationIntent`, `DeviceIntent` and `CommandMeta` schemas in `packages/contracts/production/gapp-api-v1.schema.json`;
- `docs/architecture/data-model.md` (the device row, the unit-of-work table, the idempotency and replay rule) and `docs/architecture/domain-and-data-boundaries.md`;
- **the code you build beside (read only):**
  - `services/api/glow_domain/` (`chat_reads.py`'s read rule, `chat_provider.py`'s port pattern, `interactions.py`'s `Match`);
  - `services/api/glow_chat/contact.py`'s send checks and `delivery.py`'s acceptance step;
  - `apps/mobile/src/chat/` as the module pattern (store, client, fixture adapter, fixture controls);
  - `apps/mobile/src/contracts/production.ts` (`parseAppIntent`);
  - `apps/mobile/src/onboarding/routes.ts`;
  - `apps/mobile/src/app/_layout.tsx` (its `Stack.Protected` lines);
  - `apps/mobile/rendered/profile-preferences.spec.ts`, the test "new private profile routes deny signed-out entry and discard private URL data";
- the Foundation workflow's API and Mobile jobs (`.github/workflows/foundation.yml`), with the rendered suite and the Mobile job's timeout.

## 3. What to do

1. **Re-locate every line** the brief and DM-44 cite, at `<START_SHA>`, and record where each now is.
2. **Outcome items 1 to 5,** in the brief's order. For each: the change, the test, and the reversal, a temporary edit that must make the test fail, run and then undone. Record the reversal's edit and the failing output. Make at least these reversals, each named in the record:
   - **Outcome 1:**
     - the composer notifies a message's sender;
     - it ignores a block, an inactive account, a paused or restricted profile, or a withdrawn consent;
     - it takes a refusal fact from the trigger instead of reading it on delivery;
     - it sends a second time to a device whose send the transport accepted;
     - its payload carries an identifier, a name or text;
   - **Outcome 2:**
     - a stale-session command is accepted;
     - the reference is saved before the token store accepts;
     - a discard is skipped on revoke, logout, transfer or rotate;
     - a settings intent is accepted without an active registration;
     - **the custody test's** own reversal: the token logged in one path;
   - **Outcome 3:**
     - a denial saves the setting;
     - the permission is asked at launch;
     - logout clears before it revokes;
     - an intent bypasses `parseAppIntent`;
     - a provider term appears in the new copy;
   - **Outcome 4:**
     - **the layout's `Stack.Protected` line removed:** the rendered test fails;
     - the `canAccessRoute` rule widened: the unit test fails.
3. **Glow's wording** for the push (D4) is fixed by the brief. Write the screen's sentence for each kind (Outcome 3, DM-44 4.2) in the same plain style, with no name, photo, message text or provider term. Nathan may change any of it later.
4. **The local checks:**
   - **API,** in `services/api`, as its README lists them:
     - `python3.12 -m venv .venv`, then `.venv/bin/python -m pip install --require-hashes -r requirements-dev.lock`;
     - then, in the clean environment with `GLOW_ENV=test`: `manage.py check`, `manage.py test tests --verbosity 2`, `smoke.py`, `ruff check .`, `ruff format --check .`, `mypy`, and `python -m glow_persistence.static_check`;
   - **mobile,** in `apps/mobile`: `npm ci --ignore-scripts`, `npm run check`, `EXPO_OFFLINE=1 npm run check:expo` and `EXPO_OFFLINE=1 npm run export:development`.
5. **Rendered tests locally are informational.** Run the new rendered spec and the layout line's reversal against this container's preinstalled Chromium, as repair pass C5 did: an uncommitted config outside the checkout or under the ignored `.work/`, differing only in `launchOptions.executablePath` (the P06.2-F record, "Repair pass C5"). Name every such result informational. Never run `playwright install`. CI's pinned-browser run is the run of record.
6. **The run of record.**
   - Commit and push your code. The Foundation workflow runs on your branch's pushes. Wait for the run to finish (the push rule above).
   - Read it with your GitHub tools: every job's conclusion; the gate's line (`Application checks passed`); the API test count; the rendered suite's count in the Mobile job; the Mobile job's duration against its timeout; and whether a toolchain retry fired.
   - The run of record is the one on your last code commit. If it fails, stop and report the failing job and its log lines. Do not re-run it, and push no fix without saying so in the report.

## 4. The record

Write `docs/testing/evidence/<today's date>-p06-3-notifications.md`:
- the start gate's results, the environment check (names only) and the toolchain versions;
- where each cited line now is;
- a table with one row per Outcome bullet: the item, the files, the test, the reversal and its failing output;
- the field mismatch and what waits, as the brief's D9 states them (Outcome 5);
- every command you ran, with its result line;
- the run of record's ID, each job's result, the API test count, the rendered count, the Mobile job's duration and whether a retry fired;
- what you could not run, and why; every informational result named as such.

Commit each logical step with a clear message ending in the session's attribution lines. Push your records commit only after the run of record has finished. Confirm that `git status` is clean, and that `git diff --name-only <START_SHA> HEAD` lists only your owned paths.

## 5. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch, your code head and records head;
- the start gate's and the environment check's results;
- for each of Outcome items 1 to 5: what changed, its tests, and each reversal's result;
- each local check's result, with the informational rendered results named as such;
- the run of record: its ID, every job, the gate's line, the API test count, the rendered count, the Mobile job's duration and whether a retry fired;
- anything that met the stop rule, every deviation from the brief, and what you could not run.

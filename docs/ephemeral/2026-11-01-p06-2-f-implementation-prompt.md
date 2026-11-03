# P06.2-F prompt — mobile hardening and P06.2's carried follow-ups

- **Owner:** App Manager 8. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 1 November 2026.**
- **Durable brief:** [P06.2-F — Mobile hardening and P06.2's carried follow-ups](../planning/p06-2-f-mobile-hardening.md), revision 1.
- **Where the result goes:** the session's changes in `apps/mobile` and its record, `docs/testing/evidence/<date>-p06-2-f-mobile-hardening.md`, on its own branch; the run of record, the Foundation run on its last code commit, with the rendered suite. The manager adds its verification and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.03 (confidence 0.71); rung probabilities low 0.00, medium 0.21, high 0.56, extra high 0.23, max 0.00, ultracode 0.00. Model probabilities Fable 5.1 0.00, Opus 5.5 0.99, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.99). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.000, Fable 5.1 at high 0.000, Fable 5.1 at extra high 0.000, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.208, Opus 5.5 at high 0.554, Opus 5.5 at extra high 0.228, Opus 5.5 at max 0.000, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.002, Sonnet 5.5 at high 0.006, Sonnet 5.5 at extra high 0.002, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-01T21:21:00Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The brief makes no architectural or procedural choice and applies the conditions it carries as written (DM-29 1.1, DM-30 2.1 and 2.2, DM-36 section 6). This prompt authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Codex's review of its code head follows, then an exact-head code review.
- **Deletion condition:** prune after P06.2-F's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **implementation session for P06.2-F**, the mobile hardening, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What P06.2-F is.** The mobile app, `apps/mobile` (Expo SDK 58, fixture-only), has a set of small follow-ups recorded by earlier reviews: release guards no test covers, gaps in the chat display rule's client tests, provider wording on member screens, dead code and stale README lines, three findings from the chat interface's review, the window-replacement tests the Dev Manager set, and the landing after a failed password reset. You close each one **with a test and the reversal that fails it**. The brief, `docs/planning/p06-2-f-mobile-hardening.md`, is the specification: its "Outcome" items 1 to 7 and D1 to D6; follow them.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 8. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only the brief's "Owned paths (the session)";
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule.** Stop and report, with no further change, if any of these holds:
  - an item would change what any guard allows (D2), whether a route guard, `app.config.ts`'s environment or public-name checks, or the layout's development check;
  - an item seems to need a dependency or a lock change (D3);
  - an item would need a path outside the owned paths.
- **Network:** none beyond the npm registry for `npm ci`. Read `apps/mobile/AGENTS.md` first, its "Expo has changed" section before any Expo claim; a page you cannot reach is named as unread, never filled from memory.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, token or password, in any form;
  - call Stream or any other provider, or run any command in `proofs/stream-chat/`;
  - connect to any database, HDE, Railway or other external service;
  - run `playwright install`, `eas`, `eas-cli` or `migrate`;
  - run package install scripts: always `npm ci --ignore-scripts`;
  - weaken or delete a test to make the suite pass.

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If any is present, stop and report: this session must start in `Glow App - No Stream`.
3. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`; the environment inventory). Never read them; every command below runs without them.
4. **The toolchain:** Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, first on PATH in every process. Record `node --version` and `npm --version`.
5. **A clean process environment** for every npm and Expo command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables. The proxy and CA variables pass by reference, never printed (`docs/operations/local-development.md`).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git merge-base --is-ancestor 05f4c3a0f78e72a5782fef62db4ef186a8558ac3 HEAD && echo "PR39 present"   # PR39's head; main's merge bac3c19 has the same tree. Must print "PR39 present"
git diff --name-only bac3c1983134f4e977f867ac30b3086b5318216f HEAD | grep -v -E '\.md$'               # against main: must print nothing
grep -E '"(expo|expo-router|react-native)":' apps/mobile/package.json                                # expected: expo 58.0.22, expo-router 58.0.29, react-native 0.88.1
test -e apps/mobile/src/hooks/use-recommendations.ts && echo "dead hook present"                     # must print "dead hook present"
```

If a check fails, stop and report. The prompt is stale if `<START_SHA>` is not on the live manager branch, or if the brief's "Sessions" already records a session.

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md`, `apps/mobile/CLAUDE.md` and `apps/mobile/README.md`;
- the brief;
- the P06.2 brief's "Carried to later changes" (`docs/planning/p06-2-chat-integration.md`), whose first bullet specifies items 5 and 6;
- M05's findings 17 to 20 and P-13 (`docs/testing/evidence/2026-10-25-m05-project-review.md`);
- the carried-items file's "Carried to P06.2-F" (`docs/planning/carried-to-later-items.md`);
- ADR 0003 (`docs/adr/0003-chat-display-rule.md`), decision 3 above all;
- the Foundation workflow's Mobile job (`.github/workflows/foundation.yml`), with its rendered suite and 25-minute timeout.

## 3. What to do

1. **Re-locate every line** the brief and its sources cite, at `<START_SHA>`, and record where each now is.
2. **Items 1 to 7,** in the brief's order. For each: the change, the test, and the reversal, a temporary edit that must make the test fail, run and then undone. Record the reversal's edit and the failing output.
3. **Item 7's landing** is account entry with the reset's generic error. Add finding 5's two assertions to `rendered/onboarding.spec.ts`; change no navigation. The reversal for each assertion is recorded from CI's run if it cannot run locally, as the next step explains.
4. **The local checks,** in `apps/mobile`: `npm ci --ignore-scripts`, `npm run check`, `EXPO_OFFLINE=1 npm run check:expo` and `EXPO_OFFLINE=1 npm run export:development`. `npm run test:rendered` needs CI's pinned Chromium; never run `playwright install`. A rendered reversal that cannot run locally is shown by reasoning from the test's selector and the screen's markup, and named as such.
5. **The run of record.** Commit and push. The Foundation workflow runs on your branch's pushes. Read your push run with your GitHub tools: every job's conclusion, the gate's line (`Application checks passed`), the rendered suite's count in the Mobile job, and the Mobile job's duration against its 25 minutes. The run of record is the one on your last code commit.

## 4. The record

Write `docs/testing/evidence/<today's date>-p06-2-f-mobile-hardening.md`:
- the start gate's results, the environment check (names only) and the toolchain versions;
- a table with one row per change: the item, the files, the test, the reversal and its failing output;
- every command you ran, with its result line;
- the run of record's ID, each job's result, the rendered count and the Mobile job's duration;
- what you could not run, and why.

Commit each logical step with a clear message ending in the session's attribution lines, and push your branch. Confirm that `git status` is clean, and that `git diff --name-only <START_SHA> HEAD` lists only your owned paths.

## 5. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch, your code head and records head;
- the start gate's and the environment check's results;
- for each of items 1 to 7: what changed, its test and its reversal's result, and which optional entries you did;
- each local check's result, and the run of record: its ID, every job, the gate's line, the rendered count and the Mobile job's duration;
- anything that met the stop rule, and what you could not run.

# M06 assessment prompt — the npm advisories and the Expo SDK decision

- **Owner:** App Manager 8. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 26 October 2026.**
- **Durable brief:** [M06 — Dependency remediation and the Expo SDK assessment](../planning/m06-dependency-remediation.md), revision 1, which follows DM-31 item 4's shape for E8: research first, the upgrade decided after it.
- **Where the result goes:** the session's evidence record, `docs/testing/evidence/2026-10-26-m06-dependency-assessment.md`, on its own branch. The manager adds its verification and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at high.** Effort score 2.25 (confidence 0.77); rung probabilities low 0.00, medium 0.05, high 0.67, extra high 0.27, max 0.01, ultracode 0.00. Model probabilities Fable 5.1 0.01, Opus 5.5 0.98, Sonnet 5.5 0.01, Haiku 5.5 0.00 (confidence 0.97). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.001, Fable 5.1 at high 0.007, Fable 5.1 at extra high 0.003, Fable 5.1 at max 0.000, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.049, Opus 5.5 at high 0.657, Opus 5.5 at extra high 0.265, Opus 5.5 at max 0.010, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.001, Sonnet 5.5 at high 0.007, Sonnet 5.5 at extra high 0.003, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-10-26T20:15:12Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. The session authorizes no credential use and no live provider action, and changes no dependency in the repository. The Dev Manager reads its recommendation before any dependency change.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Its change is Markdown only, so no code review follows; the manager verifies it.
- **Deletion condition:** prune after the record is integrated and the brief's "Sessions" holds the outcome.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **M06 assessment session** for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What M06 is.** The whole-project review M05 found that `npm audit` reports 1 critical, 6 high and 7 moderate vulnerable packages in the mobile app, `apps/mobile`, which no record said (finding 29), and that npm's fixes imply moving from Expo SDK 57 to 58. Your job is research: find out exactly what each advisory is, whether it reaches the app at runtime, and what fixing it costs on SDK 57 and on SDK 58, and recommend one path. **You change no dependency in the repository.** If remediation is chosen, a later session does it, with its own review. The brief's "Outcome" and D1 to D7 are the specification; follow them.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 8. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only your evidence record, `docs/testing/evidence/2026-10-26-m06-dependency-assessment.md`;
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **Every install, update and upgrade runs in a scratch copy outside the checkout** (D2), never in it. Before you finish, `git status` in the checkout shows only your record.
- **Network** (D3): the npm registry for installs and audits, and `docs.expo.dev` for Expo's documentation. Nothing else. If a page you need is unreachable, name it as unread; never fill the gap from memory. Expo changes every SDK; read `apps/mobile/AGENTS.md` first, and its "Expo has changed" section before any Expo claim.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, token or password, in any form;
  - call Stream or any other provider, or run any command in `proofs/stream-chat/` that sends a request;
  - connect to any database, HDE, Railway or other external service;
  - run `playwright install`, `eas`, `eas-cli` or `migrate`;
  - run package install scripts: always `npm ci --ignore-scripts`, and `npm_config_ignore_scripts=true` for Expo's installer;
  - run `npm audit fix --force`, or `npx expo install` outside the wrapper (it fails the config guard).

## 1. Environment check (names only; never print values)

1. None of `DATABASE_URL`, `HD_API_KEY` or `GEO_API_KEY` may be set: `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done`. If any is present, stop and report.
2. **No `STREAM_*` name may be set:** `compgen -e | grep -E '^STREAM_'` prints names only. If any is present, stop and report: this session must start in `Glow App - No Stream`.
3. **GitHub token names** may be present (`GITHUB_TOKEN`, `GH_TOKEN`; the environment inventory). Never read them; every command below runs without them.
4. **The toolchain:** Node 24.19.0 and npm 11.9.0 in `$HOME/.local/bin`, first on PATH in every process; record `node --version` and `npm --version`. `apps/mobile/.npmrc` sets `engine-strict`, so another npm fails with `EBADENGINE`.
5. **A clean process environment** for every npm and Expo command: `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8`, plus only the command's own variables. The proxy and CA variables pass by reference, never printed (`docs/operations/local-development.md`).

## 2. Start gate

```bash
git fetch origin claude/magical-wozniak-yfmmx2 main
git switch -C <your session branch> <START_SHA>   # your branch starts at this prompt's commit
git rev-parse HEAD                                  # must print <START_SHA>
git merge-base --is-ancestor 35a582716910d51d464e9fe51701873042999ec4 HEAD && echo "PR37 present"   # must print "PR37 present"
git diff --name-only 35a582716910d51d464e9fe51701873042999ec4 HEAD | grep -v -E '\.md$'               # must print nothing
git show origin/claude/magical-wozniak-yfmmx2:docs/planning/m06-dependency-remediation.md | grep -c '^- \*\*The assessment\*\* ('   # must print 0: no assessment recorded yet
grep -E '"(expo|expo-router|react-native)":' apps/mobile/package.json   # expected: expo 57.0.24, expo-router 57.0.22, react-native 0.86.3
```

If a check fails, stop and report. The prompt is stale if `<START_SHA>` is not on the live manager branch, or if the brief's "Sessions" already records an assessment.

**Then read, completely:** root `AGENTS.md` and `CLAUDE.md`; `apps/mobile/AGENTS.md` and `apps/mobile/README.md`; the brief; M05 finding 29 in `docs/testing/evidence/2026-10-25-m05-project-review.md`; the CI policy's "Dependency drift" paragraph; the Foundation workflow's Mobile, contracts and Stream proof install steps (`.github/workflows/foundation.yml`).

## 3. What to do

1. **The counts** (Outcome 1). In a scratch copy of each of `apps/mobile`, `packages/contracts` and `proofs/stream-chat`, run `npm audit --package-lock-only --json` and record one line per package: critical, high, moderate, low and total. Expected, from the manager's run at `35a5827`: 1 critical, 6 high, 7 moderate (14) in `apps/mobile`; 1 moderate in `packages/contracts`; 1 high in `proofs/stream-chat`. Report any difference.
2. **One row per advisory** (Outcome 2): each GHSA, with severity, package and version, the path from the lock, runtime or tooling (D5) with the evidence, reach (does the app's code or build call the vulnerable function?), and the fix path. For D5, run `EXPO_OFFLINE=1 npm run export:development` once on the unchanged baseline copy and search its output for each package.
3. **Trial (a), SDK 57 in range.** Apply the in-range updates in a fresh copy: Expo's installer with `--fix` through the wrapper, and then the in-range updates npm names, through `npm update <package>` or `overrides` in the copy's `package.json`. Use whichever is smaller, and say which. Then `npm ci --ignore-scripts` and D4's checks. Record the advisories left, the lock change (packages added, removed and changed; any new `install`, `preinstall` or `postinstall` script), each check's result, and what broke.
4. **Trial (b), SDK 58.** In a fresh copy, upgrade by Expo's upgrade guide for SDK 58 on `docs.expo.dev`, through the wrapper with `npm_config_ignore_scripts=true`. Then `npm ci --ignore-scripts` and D4's checks. Record the same as for (a), and for each failure the files and the rough lines a fix would take. Read SDK 58's breaking changes for the APIs this app uses (`expo-router`, `expo-image-picker`, `expo-constants`, `expo-linking`, the splash screen, `react-native-reanimated` and `react-native-worklets`), and name each that touches the app's code.
5. **`packages/contracts` and `proofs/stream-chat`** (D6): whether an in-range fix exists for `fast-uri` and `follow-redirects`, and whether the Foundation workflow still installs `proofs/stream-chat`.
6. **The recommendation** (Outcome 4): (A), (B) or (C), with the advisories each would leave and why each is or is not acceptable, the cost of each in files, lines and lock changes, and which E11 and P06.3 should be built on.

## 4. The record

Write `docs/testing/evidence/2026-10-26-m06-dependency-assessment.md`:
- the start gate's results, the environment check (names only) and the toolchain versions;
- sections for steps 1 to 6, with tables for the counts and the advisory rows;
- every command you ran, in a scratch copy or not, with its result line;
- what you could not read or run, and why;
- one line saying the Python side is out of scope (D7).

Commit it with a clear message ending in the session's attribution lines, and push your branch. Confirm `git status` is clean and that `git diff --name-only <START_SHA> HEAD` prints only the record.

## 5. Report

Your final message is the report Nathan relays:
- the prompt revision you received (revision 1, from `<START_SHA>`), your branch and head commit;
- the start gate's and the environment check's results;
- the counts, and any difference from the expected;
- the advisory table, or its summary by severity with the critical and high rows in full;
- both trials' results: the advisories left, the lock change, each check, what broke;
- the recommendation, with its cost and the advisories it leaves;
- what you could not read or run, and the limits of the assessment.

# M06 stage two prompt — the Expo SDK 58 upgrade

- **Owner:** App Manager 8. Nathan starts this session manually, in the `Glow App - No Stream` environment (OD-36), and relays its report.
- **Revision 1, 1 November 2026.**
- **Durable brief:** [M06 — Dependency remediation and the Expo SDK assessment](../planning/m06-dependency-remediation.md), revision 2, "Stage two", which applies DM-35's conditions 3.1 to 3.11 and its new-package review as written, and Nathan's OD-54.
- **Where the result goes:**
  - the session's dependency, lock, inventory and type-only source changes, and its record, `docs/testing/evidence/2026-11-01-m06-sdk-58-upgrade.md`, on its own branch;
  - the run of record: the Foundation run on its last code commit, with the rendered suite.

  The manager adds its verification, and records the outcome in the brief's "Sessions".
- **Model and reasoning setting** (OD-10, OD-30, OD-33, OD-34, OD-42). The reading is the recommendation; it gates nothing, and Nathan picks.
  - **TypeSafe v8.2: Opus 5.5 at extra high.** Effort score 2.66 (confidence 0.73); rung probabilities low 0.00, medium 0.02, high 0.33, extra high 0.62, max 0.03, ultracode 0.00. Model probabilities Fable 5.1 0.06, Opus 5.5 0.94, Sonnet 5.5 0.00, Haiku 5.5 0.00 (confidence 0.92). Twenty-four cells, computed from the two answers: Fable 5.1 at low 0.000, Fable 5.1 at medium 0.001, Fable 5.1 at high 0.020, Fable 5.1 at extra high 0.037, Fable 5.1 at max 0.002, Fable 5.1 at ultracode 0.000, Opus 5.5 at low 0.000, Opus 5.5 at medium 0.019, Opus 5.5 at high 0.310, Opus 5.5 at extra high 0.583, Opus 5.5 at max 0.028, Opus 5.5 at ultracode 0.000, Sonnet 5.5 at low 0.000, Sonnet 5.5 at medium 0.000, Sonnet 5.5 at high 0.000, Sonnet 5.5 at extra high 0.000, Sonnet 5.5 at max 0.000, Sonnet 5.5 at ultracode 0.000, Haiku 5.5 at low 0.000, Haiku 5.5 at medium 0.000, Haiku 5.5 at high 0.000, Haiku 5.5 at extra high 0.000, Haiku 5.5 at max 0.000, Haiku 5.5 at ultracode 0.000. Sent 2026-11-01T12:32:31Z. Nathan picks the cell.
- **The Dev Manager's read:** none before it runs. DM-35 read the design, and the brief applies its conditions as written (DM-03 G2). This prompt authorizes no credential use and no live provider action.
- **Environment** (OD-36): `Glow App - No Stream`. No Stream variable is needed.
- **It runs alone** (OD-29). Codex's review of its code head follows, then an exact-head code and security review (3.11).
- **Deletion condition:** prune after M06's PR merges and its merge receipt is recorded.

**Manager:** before giving this prompt to Nathan, replace every `<START_SHA>` with the full SHA of the manager-branch commit that holds this revision.

---

You are the **implementation session for M06's stage two**, the Expo SDK 58 upgrade, for the Glow dating app, in the public repository `amthorn78/glow-dating-app`. Nathan Amthor, its owner, started you manually. This prompt is revision 1, from commit `<START_SHA>` of the manager branch `claude/magical-wozniak-yfmmx2`.

**What stage two is.** Stage one assessed the npm advisories (`docs/testing/evidence/2026-10-26-m06-dependency-assessment.md`, with its "Manager verification" of 1 November). The Dev Manager chose path (B), SDK 58 now (DM-35). You upgrade the mobile app from Expo SDK 57 to the current SDK 58 release, and apply every in-range fix. You also fix one lock entry each in `packages/contracts` and the Stream proof, and prove the result in CI, with the rendered suite on your exact head. Nathan has accepted the advisories that cannot be fixed (OD-54): `zod` (expected to clear in range), `glob` and `minimatch`, all in tooling. The brief's "Stage two" section, conditions 3.1 to 3.11 and "The new-package review", is the specification. Follow it as written; this prompt does not restate every word.

**How you work:**
- Nathan started you and will relay your report to the manager, App Manager 8. You are neither the manager nor a reviewer.
- You may use any tools, subagents, scheduled wake-ups or other capabilities the work needs.
- **Your boundary is scope:**
  - write only the brief's "Owned paths (stage two's session)";
  - push only your own session branch, with `git push -u origin <branch>`. Never push `main`, the manager branch or `claude/dev-manager`, and never delete a branch;
  - on GitHub, read only: no pull request, comment, review, re-run, workflow dispatch or setting. Change nothing in Notion.
- **The stop rule (3.7).** Stop and report, with no further change, if any of these holds:
  - the rendered suite needs a fix that changes what any guard allows;
  - a fix needs more than `_layout.tsx` and `src/onboarding/routes.ts`;
  - a source fix would be more than type annotations and imports (3.4);
  - a fact in the new-package review differs from the brief's (another maintainer or publisher, a new install script, a source other than the registry, a missing integrity hash, or a native package no Expo package requires).
- **Network:** the npm registry, for installs, audits, `npm view` and `npm audit signatures`, and `docs.expo.dev`. Nothing else. A page you cannot reach is named as unread, never filled from memory. Read `apps/mobile/AGENTS.md` first, its "Expo has changed" and "Dependency changes" sections above all.
- **Never:**
  - dump the environment, or print, echo, log, copy or commit any credential, token or password, in any form;
  - call Stream or any other provider, or run any command in `proofs/stream-chat/` that sends a request;
  - connect to any database, HDE, Railway or other external service;
  - run `playwright install`, `eas`, `eas-cli` or `migrate`;
  - run package install scripts: always `npm ci --ignore-scripts`, and `npm_config_ignore_scripts=true` for Expo's installer;
  - run `npm audit fix --force`, `npx expo install` outside the wrapper, or an unpinned `npx` package (so `expo-doctor` is not run; 3.10);
  - add an `overrides` entry that forces a version outside a parent's declared range (OD-54 chose acceptance, not overrides);
  - weaken a test to make it pass (3.6).

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
git merge-base --is-ancestor 1ce2fcbe1c1b81db5c4f0a8a9e513c806bb4d932 HEAD && echo "PR37 present"   # must print "PR37 present"
git diff --name-only 35a582716910d51d464e9fe51701873042999ec4 HEAD | grep -v -E '\.md$'               # against main: must print nothing
grep -c '^- \*\*Revision 2, 1 November 2026' docs/planning/m06-dependency-remediation.md            # must print 1
git show origin/claude/magical-wozniak-yfmmx2:docs/planning/m06-dependency-remediation.md | grep -c '^- \*\*Stage two\*\* ('   # must print 0: no stage two recorded yet
grep -c '^| OD-54 |' docs/continuity/owner-directions.md                                            # must print 1
grep -E '"(expo|expo-router|react-native)":' apps/mobile/package.json                                # expected: expo 57.0.24, expo-router 57.0.22, react-native 0.86.3
```

If a check fails, stop and report. The prompt is stale if `<START_SHA>` is not on the live manager branch, or if the brief's "Sessions" already records a stage two.

**Then read, completely:**
- root `AGENTS.md` and `CLAUDE.md`;
- `apps/mobile/AGENTS.md` and `apps/mobile/README.md`;
- the brief, its "Stage two" section above all;
- the stage-one record, with its "Manager verification";
- DM-35, `docs/continuity/dev-manager/reviews/2026-11-01-dm-35-m06-recommendation.md`;
- OD-54 in `docs/continuity/owner-directions.md`;
- the CI policy's "Dependency drift" paragraph;
- the Foundation workflow's Mobile job (`.github/workflows/foundation.yml`), with its rendered suite and 25-minute timeout.

## 3. What to do

1. **The counts at the start** (DM-02 B9): `npm audit --package-lock-only --json` in `apps/mobile`, `packages/contracts` and `proofs/stream-chat`. Record them; expect the manager's figures of 1 November (the stage-one record's "Manager verification").
2. **The upgrade (3.1),** in the checkout's `apps/mobile`:
   - record `npm view expo dist-tags` and use `latest` (58.0.22 on 1 November);
   - run `npm_config_ignore_scripts=true node scripts/development.mjs install expo@<that version> --fix` in a clean environment;
   - do the `expo-router` uninstall and reinstall if npm's `ERESOLVE` on `expo-symbols` appears, as stage one's trial (b) did;
   - pin every range the installer writes to the exact version in the lock (`save-exact`);
   - then `npm ci --ignore-scripts`.

   The installer may ask for an `app.config.ts` change. That file is outside your owned paths, so record the request and stop if the upgrade cannot proceed without it.
3. **In range (3.2):** `npm update --ignore-scripts` for `shell-quote`, `fast-uri`, `node-forge` and `zod`, and for `glob`, `minimatch` and `deepmerge` where a parent's range allows. `zod` is expected to move to 4.x, since `@expo/cli` 58.1.18 no longer depends on it. Name each package that cannot move, with the range that holds it. Then `npm ci --ignore-scripts`.
4. **`packages/contracts` and the proof (3.3):**
   - `npm update --ignore-scripts fast-uri` in `packages/contracts`, one lock entry;
   - `npm update --package-lock-only --ignore-scripts follow-redirects` in `proofs/stream-chat`, one lock entry. Install nothing there.
5. **`dependency-inventory.json`,** in `apps/mobile` and in `packages/contracts`. Each is a projection of its lock: one entry for each non-root `packages` entry, sorted by `path`, with `path`, `version`, `license`, `development` (the lock's `dev` flag, `false` when absent) and `integrity`, under the existing `generated_from` and `scope` keys. Regenerate each with a throwaway script outside the checkout. Keep the files' formatting, and check that each lists exactly its lock's entries.
6. **The type-only fix (3.4):** the ref types in `src/chat/screen.tsx`, `src/components/ui.tsx` and `src/interactions/controls.tsx` (stage one: `HostInstance`, about 11 lines). Every changed source line is a type annotation or an import; list them.
7. **The local checks:**
   - in `apps/mobile`: `npm run check`, `EXPO_OFFLINE=1 npm run check:expo` and `EXPO_OFFLINE=1 npm run export:development`;
   - in `packages/contracts`: `npm run check`.

   Record each result. `npm run test:rendered` needs CI's pinned Chromium; never run `playwright install`.
8. **The Router 58 items (3.8),** each checked against Expo's Router 57→58 migration guide on `docs.expo.dev`, and recorded:
   - the `Stack.Protected` guards in `src/app/_layout.tsx`;
   - the module-level `router` before the first render, `_layout.tsx:32` above all;
   - `useRootNavigationState()`'s `key`;
   - on web, `SafeAreaView` and async routes, against the 320px layout cases.
9. **The run of record (3.6).** Commit and push. The Foundation workflow runs on your branch's pushes.
   - Read your push run with your GitHub tools: every job's conclusion, the gate's line (`Application checks passed`), the rendered suite's result in the Mobile job, and the Mobile job's duration against its 25 minutes.
   - If a rendered test fails because Router 58 changes a mechanism it asserts, change the test only so that it still asserts the same outcome for the member: the protected screen stays unreachable. List each such change with its reason. A fix inside `_layout.tsx` or `src/onboarding/routes.ts` that keeps what every guard allows is in scope; anything more meets the stop rule.
   - Push again, and read the new run. The run of record is the one on your last code commit.
10. **The new-package review (3.9):** for every package new to `apps/mobile`'s lock, the brief's four points: its source and integrity hash, its scripts and `bin`s, its native binaries, and its publisher. The publisher point includes `npm audit signatures` on the installed tree. Compare `noxcturnal`'s facts with the brief's; any difference meets the stop rule.
11. **The counts at the head (3.5):** one row per advisory left in each package, with D5's evidence from the head's `export:development` bundles. The list must be OD-54's or smaller. Name anything new, more severe, or in the bundle.
12. **The limits (3.10):** no native build, so React Native 0.88, Hermes, gesture-handler 3, Reanimated 4.7, worklets 0.13 and the new native binaries are untested natively; Expo's release notes, if unreachable; `expo-doctor`, not run.

## 4. The record

Write `docs/testing/evidence/2026-11-01-m06-sdk-58-upgrade.md`:
- the start gate's results, the environment check (names only) and the toolchain versions;
- sections for steps 1 to 12, with every command and its result line;
- the `package.json` and lock changes in numbers: packages added, removed and changed, and any install script;
- the run of record's ID and each job's result;
- the advisory table at the head;
- what you could not read or run, and why.

Commit each logical step with a clear message ending in the session's attribution lines, and push your branch. Confirm that `git status` is clean, and that `git diff --name-only <START_SHA> HEAD` lists only your owned paths.

## 5. Report

Your final message is the report Nathan relays:
- the prompt revision (revision 1, from `<START_SHA>`), your branch, your code head and records head;
- the start gate's and the environment check's results;
- the SDK version and tag used, and the `package.json`, lock and inventory changes in numbers;
- the source change, line by line, and any test change with its reason;
- each local check's result, and the run of record: its ID, every job, the gate's line, the rendered suite and the Mobile job's duration;
- the Router 58 items' results;
- the new-package review, and any difference from the brief's facts;
- the advisories at the head against OD-54's list;
- whether the stop rule was met, and the limits.

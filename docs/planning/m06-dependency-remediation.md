# M06 — Dependency remediation and the Expo SDK assessment

- **Work ID:** M06 (cross-cutting).
- **Status: the assessment is commissioned.** Remediation, if the assessment recommends any, follows it as M06's second stage, with its own brief revision, prompt and review.
- **Owner:** Nathan Amthor, by the order he resumed on 26 October (OD-49): M06 just after M04 (DM-31 item 4, which moved E8's assessment up). **Manager:** App Manager 8. **Assessment:** one research session, started by Nathan.
- **Revision 1, 26 October 2026.**
- **Starting point:** `main` at `35a5827` (PR37), with the manager branch's Markdown records after it. The prompt names the exact commit.
- **Prompt:** [`docs/ephemeral/2026-10-26-m06-assessment-prompt.md`](../ephemeral/2026-10-26-m06-assessment-prompt.md), revision 1, for `Glow App - No Stream`.
- **Evidence home:** `docs/testing/evidence/2026-10-26-m06-dependency-assessment.md`, written by the session.

## Why

- **M05 finding 29 (major):** the advisory picture is worse than any record said. The State of the App said "14 moderate … none high or critical"; C2's record gave no counts, against DM-02 B9 (the CI policy, "Dependency drift").
- **E8, as DM-31 item 4 placed it:** the app is on Expo SDK 57 (`expo` 57.0.24, `react-native` 0.86.3), and npm's fixes imply SDK 58. The assessment decides whether E11 (P06.2-F, the mobile hardening) and P06.3 are built on 57 or 58. It is research: the audit counts recorded and the upgrade's cost. If it says upgrade, the upgrade comes before E11.
- **The manager's audit at `35a5827`** (26 October; `npm audit --package-lock-only`, the same locks as M05's `f669f37`):
  - `apps/mobile`: 14 vulnerable packages: 1 critical (`shell-quote`), 6 high (`expo`, `@expo/cli`, `@expo/code-signing-certificates`, `node-forge`, `source-map-js`, `zod`) and 7 moderate (`@expo/config-plugins`, `decode-uri-component`, `expo-router`, `fast-uri`, `query-string`, `uuid`, `xcode`);
  - `packages/contracts`: 1 moderate (`fast-uri`, through `ajv`);
  - `proofs/stream-chat`: 1 high (`follow-redirects`, recorded).
- **What npm offers:**
  - a fix within the current versions for `shell-quote`, `@expo/code-signing-certificates`, `source-map-js`, `@expo/config-plugins`, `fast-uri`, `uuid` and `xcode`;
  - `expo-router` 58 for `expo-router`, `decode-uri-component` and `query-string`;
  - `expo` 44.0.6 for `expo`, `@expo/cli`, `node-forge` and `zod`. That is a downgrade across thirteen SDKs, not a fix.

## Outcome

The assessment is done when its record holds all of these:

1. **The counts,** one `npm audit` line per npm package (DM-02 B9), on the starting commit's locks.
2. **One row per advisory** (each GHSA, not only each package):
   - severity, package and version;
   - the dependency path from the lock;
   - **runtime or tooling:** whether the package reaches the app's JavaScript bundle (D5), or only the development server, the CLI or the build;
   - **reach:** whether the app's own code or build calls the vulnerable function, with the evidence;
   - **the fix path:** in range on SDK 57, SDK 58 only, or no fix yet.
3. **Two trials,** each in a scratch copy outside the repository (D2):
   - **(a) SDK 57, in range:** the in-range updates applied, then the checks (D4);
   - **(b) SDK 58:** the upgrade by Expo's versioned upgrade guide, then the checks.

   For each: the advisories left; the lock change (packages added, removed and changed, and any new install script); each check's result; what broke, and what fixing it would take, in files and lines.
4. **A recommendation, with its cost:**
   - (A) stay on 57 with the in-range fixes;
   - (B) upgrade to 58 before E11;
   - (C) a stated mix.

   Under each: the advisories that would remain, and why each is acceptable or not.

Then the manager verifies the record, and the Dev Manager reads the recommendation before any dependency change (the review plan). An advisory left unfixed is risk acceptance, which is Nathan's (the charter, "Roles").

## Design

- **D1 — Research only.** The session changes no dependency, version or lock in the repository. Its one repository write is its evidence record, so its change is ordinary documentation: no application CI and no code review (`AGENTS.md`). The manager verifies it by re-running the audits and checking its claims.
- **D2 — Trials in scratch copies.** The session copies `apps/mobile` (and, for `fast-uri`, `packages/contracts`) to a temporary directory outside the checkout, and runs every install and upgrade there. The checkout's `git status` stays clean apart from the record (DM-14 item 6).
  - Installs never run package scripts: `npm ci --ignore-scripts`, and `npm_config_ignore_scripts=true` for the installer.
  - Expo's installer runs through the wrapper, as `apps/mobile/AGENTS.md` says: `npm_config_ignore_scripts=true node scripts/development.mjs install …`.
- **D3 — Network:** the npm registry (installs and audits) and `docs.expo.dev` (the versioned docs, `llms.txt` and the upgrade guide) only. `Glow App - No Stream` allows both (the environment inventory). A page it cannot reach is named as unread, never guessed, and never read from memory (`apps/mobile/AGENTS.md`: "Expo has changed — do not trust your training data").
- **D4 — The checks in each trial,** from the copy's own directory: `npm run check`, `EXPO_OFFLINE=1 npm run check:expo` and `EXPO_OFFLINE=1 npm run export:development`. The rendered suite needs the Chromium revision `@playwright/test` pins, which only CI has (`playwright install` is forbidden here), so it is "not run" in both trials and named as a gap for the second stage's CI.
- **D5 — Runtime or tooling, by evidence:** a package counts as runtime only if its modules appear in the trial's or the baseline's `export:development` output, or the app's source imports it. A path through the development server, the CLI, the config plugins or the build alone is tooling. Each row names the evidence it rests on.
- **D6 — `proofs/stream-chat`'s `follow-redirects`:** the record says whether an in-range fix exists and whether the proof's CI job still installs the package. It runs no proof command that sends a request.
- **D7 — The Python side is out of scope:** finding 29 is about npm. The record says so in one line.
- **Considered and not chosen:**
  - the upgrade in the same session: DM-31 made this research first, and a dependency change is full scope, with its own review;
  - `npm audit fix --force`: it would move `expo` to 44.0.6.

## Owned paths (the session's)

- **New:** `docs/testing/evidence/2026-10-26-m06-dependency-assessment.md`.
- Nothing else.

## Manager-owned

- This brief and its "Sessions"; the prompt; the Work Register's M06 row; Notion; the handoff.

## Exclusions

- No change to any dependency, version, lock, `.npmrc` or `dependency-inventory.json` in the repository, and no change under `apps/`, `services/`, `packages/`, `proofs/`, `scripts/` or `.github/`.
- No `eas`, `playwright install` or `migrate`.
- No provider call, and no connection to a database, HDE or Railway.

## Acceptance checks

- The record holds each part of "Outcome" 1 to 4.
- Its counts match the manager's re-run on the same locks.
- The session branch changes only the record (`git diff --name-only <start> <head>`).
- The trusted classifier reads the change as `ordinary-docs-only`.

## Review plan

- **No code review and no application CI:** the change is Markdown only (`AGENTS.md`).
- **The manager verifies the report** against the pushed branch: it re-runs the three audits, checks the runtime or tooling evidence for the critical and high rows, and re-runs a trial's key step in its own scratch copy where that is cheap.
- **Then the Dev Manager** reads the recommendation and, if remediation is recommended, this brief's next revision with the second stage (the charter: significant dependencies).
- **Then Nathan,** in OD-32's form, for any advisory left unfixed (risk acceptance).

## Sessions

- **Revision 1** (26 October 2026): the assessment prompt, revision 1 (its TypeSafe reading is in its header and the uses table), given to Nathan.

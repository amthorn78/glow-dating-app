# M06 — Dependency remediation and the Expo SDK assessment

- **Work ID:** M06 (cross-cutting).
- **Status: stage one (the assessment) is done.** Stage two, the SDK 58 upgrade, is designed in this revision, which applies DM-35 ([report](../continuity/dev-manager/reviews/2026-11-01-dm-35-m06-recommendation.md)). It runs after Nathan's risk acceptance of the advisories it cannot fix (DM-35 item 5).
- **Owner:** Nathan Amthor, by the order he resumed on 26 October (OD-49): M06 just after M04 (DM-31 item 4, which moved E8's assessment up). **Manager:** App Manager 8. **Stage one:** one research session, started by Nathan. **Stage two:** one implementation session, started by Nathan.
- **Revision 2, 1 November 2026:** stage two under DM-35's path (B), with its conditions 3.1 to 3.11 and section 8 applied as written, so it needs no further read (the charter's exception). Revision 1 (26 October) designed stage one.
- **Starting point:** `main` at `35a5827` (PR37), with the manager branch's Markdown records after it. The prompt names the exact commit.
- **Prompt** (pruned once the assessment was integrated): [`docs/ephemeral/2026-10-26-m06-assessment-prompt.md`](https://github.com/amthorn78/glow-dating-app/blob/671d1a52632c6d015b22b6c70c78d7ee26f8367f/docs/ephemeral/2026-10-26-m06-assessment-prompt.md), revision 1, for `Glow App - No Stream`.
- **Evidence homes:** stage one, `docs/testing/evidence/2026-10-26-m06-dependency-assessment.md`; stage two, `docs/testing/evidence/2026-11-01-m06-sdk-58-upgrade.md`, written by its session.
- **Stage two's prompt:** [`docs/ephemeral/2026-11-01-m06-stage-two-prompt.md`](../ephemeral/2026-11-01-m06-stage-two-prompt.md), revision 1, for `Glow App - No Stream`.

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

## Outcome (stage one)

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

## Design (stage one)

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

## Owned paths (stage one's session)

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

## Stage two: the SDK 58 upgrade (revision 2; DM-35)

**The path is (B):** SDK 58 now, as M06's second stage, before E11 (DM-35 item 2). (C) is declined on the facts of 1 November. On SDK 57 the one package in the app's bundle, `decode-uri-component`, carries a high advisory with no clean fix; SDK 58 removes it; and E11 then works once, on the final base, in the files Router 58 changes.

**The conditions** (DM-35 section 5, as written):

- **3.1 — The version:** the current SDK 58 release at the session's start, recorded with its tag (`latest` was 58.0.22 on 1 November). Pinned exactly (`save-exact`), through the wrapper with scripts off (`apps/mobile/AGENTS.md`), with the `expo-router` uninstall and reinstall the trial needed.
- **3.2 — Every advisory left is tried in range,** as trial (a) did: `shell-quote`, `fast-uri`, `node-forge` 1.4.2, and `glob`, `minimatch` and `deepmerge` where a parent's range allows. Each that cannot move is named with the range that holds it (for example, `glob` held at `^13.0.0` by `@expo/cli` 58 and fixed only from 14.0.2; `zod` held at `^3.25.76` and fixed only from 4.6.6).
- **3.3 —** `fast-uri` 3.1.9 in `packages/contracts` and `follow-redirects` 1.16.2 in the proof's lock, one lock entry each. `dependency-inventory.json` changes to match.
- **3.4 — The source fix stays type-only:** the exact-head review checks that every changed source line is a type annotation or an import.
- **3.5 — The counts at the exact head** (DM-02 B9): one row per advisory left, with D5's evidence from that head's `export:development` bundles. The list is the one Nathan accepted (DM-35 item 5), or smaller.
- **3.6 — The rendered suite on the exact head,** in the run of record, with the Mobile job's duration against its 25-minute timeout (finding 11). **No test is weakened to pass.** Where Router 58 changes a mechanism a test asserts, for example "removed from the tree" against "renders a redirect", the test still asserts the same outcome for the member: the protected screen stays unreachable. Each such change is listed with its reason, for the exact-head review.
- **3.7 — A stop rule.** The session stops and reports if the rendered suite needs a fix that changes what any guard allows, or a fix that needs more than `_layout.tsx` and `src/onboarding/routes.ts`. The manager brings the design to the Dev Manager, since it changes a component's interface (the fix-or-carry rule's limits). The fallback is (A), trial (a)'s SDK 57 path, with Nathan asked to accept `decode-uri-component` until SDK 58 lands.
- **3.8 — The Router 58 items the record names, each checked and recorded:** the `Stack.Protected` guards; the module-level `router` before the first render, `_layout.tsx:32` above all; `useRootNavigationState()`'s `key`; on web, `SafeAreaView` and async routes, against the 320px layout cases.
- **3.9 — The new-package review** (below), in the record before the exact-head review.
- **3.10 — The limits named:** no native build, so React Native 0.88, Hermes, gesture-handler 3, Reanimated 4.7, worklets 0.13 and the new native binaries are untested natively, carried to the first native build; Expo's release notes, if they are still outside the session's network; `expo-doctor`, not run unless it is pinned.
- **3.11 — Full scope:** the run of record and Codex; an exact-head code and security review, whose security focus covers the lock's sources and integrity hashes, install scripts and `bin`s, the new packages and 3.4. Anything beyond 3.1 to 3.11 and the new-package review comes back to the Dev Manager.

**The new-package review** (DM-35 section 8), for every package new to the lock, in the stage-two record before the exact-head review:
- **its source:** every `resolved` URL is `registry.npmjs.org`, and every entry has an `integrity` hash; no git or tarball URLs;
- **its scripts and `bin`s:** none run, since installs use `--ignore-scripts`; any `install`, `preinstall` or `postinstall` script is named, and every `bin` is listed (`2g` has one);
- **its native binaries:** which platform packages arrive, and which one CI and a session would execute;
- **its publisher:** the npm maintainers and the repository URL; the provenance, from `npm audit signatures` in the scratch install; and which package requires it.

`noxcturnal` is acceptable on the facts of 1 November (one maintainer, `philpl`; repository `github.com/expo/noxcturnal`; no provenance; required by `@expo/metro-config` 58; no install script), as a recorded limit. If any of these differs at the head (another maintainer or publisher, a new install script, a source other than the registry or a missing integrity hash, a native package no Expo package requires), it goes to the Dev Manager before the exact-head review.

**Nathan's risk acceptance** (DM-35 item 5), before stage two runs, in OD-32's form: the advisories stage two cannot fix. **Accepted** on 1 November (OD-54: *"a"*), until their parents' ranges move. Expected, all in tooling and none in the bundle: `zod` GHSA-mrhx-c7xc-m3w5 (high), `glob` GHSA-3g3m-2fjr-6pw4 (moderate) and `minimatch` GHSA-g3hv-75wg-m249 (moderate). **Since DM-35** (the manager, 1 November, on the locks alone): `@expo/cli` 58.1.18 no longer depends on `zod`, and its two remaining dependents (`eslint-plugin-react-hooks` and `zod-validation-error`, both development-only) accept `^4.0.0`, so `zod` moves in range to 4.6.7 and its high clears, leaving `glob` and `minimatch`. Stage two confirms it under 3.2. At the final head the manager confirms that the list is the same or smaller; any new advisory, any higher severity, or anything that reaches the bundle goes back to him before the merge.

**Owned paths (stage two's session):**
- `apps/mobile/package.json`, `apps/mobile/package-lock.json` and `apps/mobile/dependency-inventory.json`;
- `packages/contracts/package-lock.json` and `packages/contracts/dependency-inventory.json` (3.3);
- `proofs/stream-chat/package-lock.json` (3.3);
- the type-only fix (3.4): `apps/mobile/src/chat/screen.tsx`, `src/components/ui.tsx` and `src/interactions/controls.tsx`;
- within 3.7's limit only: `apps/mobile/src/app/_layout.tsx`, `src/onboarding/routes.ts`, and `apps/mobile/rendered/` under 3.6;
- the stage-two record.

**Exclusions:** any other path; any change to what a guard allows; `.github/`, `scripts/`, `services/`; `eas`, `playwright install`, `migrate`; any provider call or connection to a database, HDE or Railway.

## Sessions

- **Revision 1** (26 October 2026): the assessment prompt, revision 1 (its TypeSafe reading is in its header and the uses table), given to Nathan.
- **The assessment** (26 October 2026; branch `claude/gallant-einstein-rjyjdl`, head `359d73d`; Nathan's pick: not recorded): every part of "Outcome" done, with only the record changed. It found 10 advisories in the mobile app's 14 flagged packages, only `decode-uri-component` in the bundle, and the two trials passing D4's checks, SDK 58 after an 11-line type-only fix. It recommends (C): in-range fixes on SDK 57 now, E11 on 57, and SDK 58 as its own item before P06.3's UI. The manager verified it and fast-forwarded the manager branch to it. On 1 November its re-audit found the picture moved: `node-forge` fixable in range (1.4.2), a new high on the bundled `decode-uri-component` that only SDK 58 clears, and three new tooling advisories (the record's "Manager verification"). Next: [DM-35](../ephemeral/2026-11-01-dm-35-m06-recommendation.md), the Dev Manager's read of the path, the second stage's scope and the advisories left for Nathan.
- **DM-35** (1 November 2026; report `dfc138e`, a read of `0139b10`, merged at `0c31b01`): the record and its verification approved, with the dated note 1.1; **path (B)**, SDK 58 now as stage two, before E11, with conditions 3.1 to 3.11 and section 8's new-package review; (C) declined on today's facts. The advisories stage two cannot fix go to Nathan before it runs. Applied as **revision 2**, which needs no further read.
- **OD-54** (1 November 2026): Nathan accepted `zod`, `glob` and `minimatch` until their parents' ranges move (*"a"*). **Stage two's prompt, revision 1** (its TypeSafe reading is in its header and the uses table): given to Nathan.
- **Stage two** (1 November 2026; branch `claude/magical-lovelace-s0akbt`, code head `524d42f`, records `5103063`; Nathan's pick: not recorded): Expo SDK 58.0.22 (`latest`), every range exact. The fix is type-only (11 lines), and six rendered-test changes, five waits and one landing screen, are listed with their reasons (3.6). Run of record 41310128518 on `524d42f`: all eight jobs passed, `Application checks passed`, the rendered suite 97 of 97, Mobile 7 min 13 s of 25. The advisories left are `glob` and `minimatch` (moderate, tooling), smaller than OD-54's list, since `zod` cleared at 4.6.7. The new-package review is recorded; `noxcturnal` matches the brief's facts. The stop rule was not met. The manager verified it, the stage-two record's "Manager verification", and fast-forwarded the manager branch. Next: the PR, Codex, and the exact-head review with 3.11's focus and the landing-screen change.
- **PR38** (1 November 2026): M06's full-scope PR from the manager branch. **The exact-head review prompt, revision 1** ([prompt](../ephemeral/2026-11-01-m06-review-prompt.md); its TypeSafe reading is in its header and the uses table) goes to Nathan once Codex's review has completed on the code head and on the commit that holds it (step 6).

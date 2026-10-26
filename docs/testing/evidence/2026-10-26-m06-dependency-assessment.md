# M06 — Dependency assessment and the Expo SDK 58 trial

- **Work ID:** M06, first stage (the assessment). Brief: [`docs/planning/m06-dependency-remediation.md`](../../planning/m06-dependency-remediation.md), revision 1.
- **Prompt:** revision 1, from commit `671d1a52632c6d015b22b6c70c78d7ee26f8367f` of the manager branch `claude/magical-wozniak-yfmmx2`.
- **Session branch:** `claude/gallant-einstein-rjyjdl`, started at `671d1a52632c6d015b22b6c70c78d7ee26f8367f`.
- **Date:** 26 October 2026 (UTC).
- **Change:** this record only. No dependency, version, lock or source file in the repository was changed. Every install, update and upgrade ran in scratch copies outside the checkout (D2).
- **Python:** out of scope (D7). Finding 29 is about npm, and this record covers only the npm packages.

## Summary

- **Counts at the starting locks** match the manager's run exactly:
  - `apps/mobile`: 1 critical, 6 high, 7 moderate, 0 low (14 packages);
  - `packages/contracts`: 1 moderate (1);
  - `proofs/stream-chat`: 1 high (1).
- **Ten advisories reach those 14 mobile packages** (GHSA IDs, below). Seven of the packages carry their own advisory; the other seven are flagged only because they depend on one of those.
- **Runtime:** only `decode-uri-component` (moderate) and its parent `query-string` have modules in the app's JavaScript bundles. Every critical and high advisory is in tooling: the Expo CLI, the development server, Metro, ESLint or the config plugins. None of them appears in the bundles.
- **Trial (a), SDK 57 in range:**
  - **Advisories:** 8 packages left (5 high, 3 moderate), from 3 advisories.
  - **Checks:** every D4 check passes.
  - **Cost:** 6 version lines in `package.json` and no source change. The lock adds 12 entries, removes 6 and changes 42.
- **Trial (b), SDK 58** (with the same in-range updates):
  - **Advisories:** 5 packages left (all high), from 2 advisories.
  - **Checks:** `npm run check` fails typecheck with 11 errors in 3 files. An 11-line type-only fix in the copy made every D4 check pass.
  - **Cost:** 18 version lines in `package.json`. The lock adds 59 entries, removes 68 and changes 105. That includes React Native 0.86.3 → 0.88.0 and React 19.2.3 → 19.3.0.
  - **Install:** npm needed an extra uninstall and reinstall step.
  - **Not known:** the rendered suite's result, because SDK 58 changes Expo Router's protected-route behaviour.
- **No fix exists, on either SDK, for the two high advisories that remain:**
  - `node-forge` GHSA-86w9-cpqp-85rv: no patched version is published;
  - `zod` GHSA-mrhx-c7xc-m3w5: `@expo/cli` 57 and 58 both require `zod` `^3.25.76`, and the fix is 4.6.6.
- **Recommendation: (C), a stated mix.**
  - Run trial (a) now as M06's second stage. Add `fast-uri` in `packages/contracts` and `follow-redirects` in the Stream proof's lock.
  - Build E11 on SDK 57.
  - Make the SDK 58 upgrade its own work item, before P06.3's UI.
  - Details are in step 6.

## Environment check and start gate

| Check | Result |
| --- | --- |
| `for n in DATABASE_URL HD_API_KEY GEO_API_KEY; do [ -n "${!n+x}" ] && echo "$n present"; done` | Nothing printed: none set |
| `compgen -e \| grep -E '^STREAM_'` | Nothing printed: no `STREAM_*` name, so this is `Glow App - No Stream` |
| GitHub token names (`compgen -e`, names only) | `GH_TOKEN` and `GITHUB_TOKEN` present. Never read; every command ran without them |
| Proxy and CA names present (names only) | `HTTPS_PROXY`, `NO_PROXY`, `NODE_EXTRA_CA_CERTS` and others. Passed by reference only |
| `node --version` / `npm --version` (both `/root/.local/bin`, first on PATH) | `v24.19.0` / `11.9.0` |
| `git fetch origin claude/magical-wozniak-yfmmx2 main` | Fetched |
| `git switch -C claude/gallant-einstein-rjyjdl 671d1a5…`, then `git rev-parse HEAD` | `671d1a52632c6d015b22b6c70c78d7ee26f8367f` |
| `git merge-base --is-ancestor 1ce2fcb… HEAD` | `PR37 present` |
| `git diff --name-only 35a5827… HEAD \| grep -v -E '\.md$'` | Nothing printed: only Markdown since `main` |
| The brief's "Sessions" on the live manager branch: `grep -c '^- \*\*The assessment\*\* ('` | `0`: no assessment recorded yet |
| `671d1a5…` is an ancestor of `origin/claude/magical-wozniak-yfmmx2` | Yes; the live head is `671d1a5…` itself |
| `grep -E '"(expo\|expo-router\|react-native)":' apps/mobile/package.json` | `expo` 57.0.24, `expo-router` 57.0.22, `react-native` 0.86.3 |

**Read completely before the work:**
- the root `AGENTS.md` and `CLAUDE.md`;
- `apps/mobile/AGENTS.md`, including "Expo has changed", and `apps/mobile/README.md`;
- the brief;
- M05 finding 29;
- the CI policy's "Dependency drift" paragraph;
- the Foundation workflow's Mobile, API mobile smoke and Stream proof install steps (`.github/workflows/foundation.yml:83-196`);
- `docs/operations/local-development.md` on the proxy variables in a clean environment.

**How every npm and Expo command ran:**
- through one helper, `cleanenv.sh` in the scratch tools directory;
- the helper runs `env -i PATH="$PATH" HOME="$HOME" LANG=C.UTF-8 HTTPS_PROXY="$HTTPS_PROXY" NODE_EXTRA_CA_CERTS="$NODE_EXTRA_CA_CERTS" NO_PROXY="$NO_PROXY"`, plus the command's own variables (`EXPO_OFFLINE=1`, `EXPO_NO_TELEMETRY=1`, `npm_config_ignore_scripts=true`);
- no value was printed.

**Where the work ran:** three scratch copies of the starting commit's tree, each made with `git archive 671d1a5… | tar -x`, under the session scratchpad (`/tmp/claude-0/…/scratchpad/m06/`): `baseline`, `trial-a` and `trial-b`.

**Network:** only the npm registry (installs, audits, `npm view`) and `docs.expo.dev` (`llms.txt`, the upgrade walkthrough, the Router 57→58 migration guide, and the v58.0.0 reference pages). Expo's installer ran with `EXPO_OFFLINE=1`, so it never called the Expo API.

## 1. The counts (Outcome 1)

Each count is `npm audit --package-lock-only --json` on the starting commit's lock, in `baseline` (DM-02 B9). npm counts vulnerable packages, not advisories.

| npm package | Critical | High | Moderate | Low | Total | Expected (manager, `35a5827`) |
| --- | --- | --- | --- | --- | --- | --- |
| `apps/mobile` | 1 | 6 | 7 | 0 | 14 | 1 / 6 / 7 (14): **same** |
| `packages/contracts` | 0 | 0 | 1 | 0 | 1 | 1 moderate: **same** |
| `proofs/stream-chat` | 0 | 1 | 0 | 0 | 1 | 1 high: **same** |

No difference from the expected counts.

## 2. One row per advisory (Outcome 2)

### Method

- **Paths:**
  - from each `package-lock.json`, with a lock walker in the scratch tools: one shortest path from the root, and every dependent;
  - confirmed with `npm explain` after `npm ci --ignore-scripts` in `baseline`.
- **D5, runtime or tooling:**
  - `EXPO_OFFLINE=1 npm run export:development` ran once in `baseline` and exited 0. It wrote an iOS bundle of 8.1 MB and an Android bundle of 8.7 MB;
  - the development bundles name each module by its path (`"node_modules/<pkg>/…"`, 1,341 module definitions in iOS). I counted the module paths of each package, and also searched each bundle for the package's name as text;
  - I searched the app's own source for imports: `src`, `scripts`, `rendered` and the config files. Its only imports of a listed package are `ajv/dist/runtime/ucs2length` and `ajv-formats/dist/formats`, both in the generated validators.
- **Reach:** I read the vulnerable package's callers in the installed tree (`node_modules`) and checked whether the app's code, config or build calls the vulnerable function.
- **Fix path:** from npm's `fixAvailable`, the trials and `npm view`.

**Packages with modules in the baseline bundles** (identical counts on iOS and Android):

| Package | Modules |
| --- | --- |
| `decode-uri-component` | 1 |
| `query-string` | 1 |
| `expo` | 70 (iOS) / 67 (Android) |
| `expo-router` | 389 / 472 |
| `ajv` | 1 (`dist/runtime/ucs2length.js`) |
| `react-devtools-core` | 1 (`dist/backend.js`) |

`shell-quote`, `node-forge`, `zod`, `source-map-js`, `fast-uri`, `uuid`, `xcode`, `@expo/cli`, `@expo/config-plugins`, `@expo/code-signing-certificates` and `postcss` have **0 modules**, and their names do not appear as text in either bundle.

### The advisories

| GHSA | Severity (CVSS) | Package and version | Path from the lock | Runtime or tooling (D5) | Reach | Fix path |
| --- | --- | --- | --- | --- | --- | --- |
| GHSA-pqg4-j6r4-53mv: `quote()` command injection through a line terminator after a `{ comment }` token | **Critical** (8.1) | `shell-quote` 1.10.0 (affected ≥1.8.4 <1.11.0) | `react-native` 0.86.3 > `react-devtools-core` 6.1.5 > `shell-quote`; only dependent `react-devtools-core` | **Tooling.** 0 modules in either bundle. `react-devtools-core/dist/backend.js` is bundled, but its source map lists no `shell-quote` source | **Not reached.** No installed `.js`/`.cjs`/`.mjs` file requires the installed `shell-quote`. `react-devtools-core/dist/standalone.js`, the desktop DevTools server, bundles its own copy, and its source `src/editor.js` imports only `parse`, never `quote`. The app never calls it | **In range on SDK 57:** `npm update shell-quote` → 1.12.0, within `react-devtools-core`'s `^1.6.1` (trial a). Not fixed by SDK 58 alone |
| GHSA-86w9-cpqp-85rv: RSA PKCS#1 v1.5 signature verification accepts extra nested DigestAlgorithm elements | **High** (7.5) | `node-forge` 1.4.0 (affected ≤1.4.0) | `expo` > `@expo/cli` 57.0.26 > `node-forge`; also `@expo/cli` > `@expo/code-signing-certificates` 0.0.6 > `node-forge` | **Tooling** (the Expo CLI). 0 modules | **Not reached in this project.** `verify` is called only in `@expo/code-signing-certificates` (self-signed check and sign-then-verify), from `@expo/cli`'s `utils/codesigning.js`. That runs only when a client sends an `expo-expect-signature` header, and then returns `null` without an EAS `extra.eas.projectId` or `updates.codeSigningCertificate`. `app.config.ts` has neither. Its `verify` calls check keys the developer holds, not signatures from outside | **No fix anywhere.** 1.4.0 is the latest published version. `@expo/cli` 58.1.15 still requires `^1.4.0`. npm's `expo@44.0.6` is a 13-SDK downgrade, not a fix |
| GHSA-68fv-2mgg-jv7q: event-loop DoS through indexed source-map section offsets | **High** (7.5) | `source-map-js` 1.2.1 (affected ≥1.0.0 <1.2.2) | `expo` > `@expo/metro-config` 57.0.12 > `postcss` 8.5.28 > `source-map-js` | **Tooling** (Metro's CSS transform). 0 modules | **Not reached.** Only `postcss` depends on it, and the app has no CSS file (`find src rendered -name '*.css'` found none) | **In range on SDK 57:** 1.2.2, through `postcss` 8.5.32 (trial a). Also in SDK 58 |
| GHSA-mrhx-c7xc-m3w5: memory exhaustion when validating oversized constrained collections | **High** (7.5) | `zod` 3.25.76 (affected <4.6.6) | `eslint-plugin-react-hooks` 7.1.1 > `zod`; also `@expo/cli` > `zod` and `zod-validation-error` 4.0.2 (a peer) | **Tooling** (ESLint and the Expo CLI). 0 modules | **Not reached by untrusted input.** The ESLint plugin validates its own rule options from `eslint.config.mjs`. `@expo/cli` validates DevTools plugin schemas (`start/server/DevToolsPlugin.schema.js`, `createMCPDevToolsExtensionSchema.js`) read from installed packages | **No fix on either SDK.** `@expo/cli` 57.0.32 and 58.1.15 both require `zod` `^3.25.76`. The last 3.x is 3.25.76, and the fix is in 4.x. An `overrides` to 4.x would break `@expo/cli`'s declared range; not tried |
| GHSA-vcc3-ghjq-m6fr: DoS through exponential decoding of malformed percent-encoded input | Moderate (no CVSS given) | `decode-uri-component` 0.2.2 (affected ≤0.4.2) | `expo-router` 57.0.22 > `query-string` 7.1.3 > `decode-uri-component` | **Runtime:** 1 module in each platform bundle | **Not established.** `query-string.parse` (which decodes) is called only by the inherited React Navigation fallback `react-navigation/core/getStateFromPath.js`. That file is bundled, but Expo Router passes its own `getStateFromPath` (`link/linking.js` → `fork/getStateFromPath-forks.js`), which parses queries with `URLSearchParams`. The router's own calls are `queryString.stringify` (encoding). The app's routes are fixed and query-free, and its root layout replaces any URL with a query. Not tested at runtime; the worst case is a client-side DoS from a crafted deep link | **SDK 58 only:** `expo-router` 58.0.26 drops `query-string` (trial b: 0 modules). No in-range fix on 57: `expo-router` 57.0.29 still uses `query-string` 7.1.3 |
| GHSA-w74x-v6f9-j3xg: URI scheme spoofing through percent-encoded scheme decoding | Moderate (6.1) | `fast-uri` 3.1.8 (affected ≥3.0.0 <3.1.9) | `ajv` 8.20.0 > `fast-uri` (a direct dependency of the app, and a dev dependency in `packages/contracts`) | **Tooling.** 0 modules; the bundles hold only `ajv/dist/runtime/ucs2length.js` | **Not reached by untrusted input.** `fast-uri` is used by Ajv's schema compiler (resolving `$id`/`$ref`). In `packages/contracts` it compiles the repository's own schemas (`generate`, `check`). The app's generated validators do not import it | **In range:** 3.1.9 in both `apps/mobile` and `packages/contracts` (`npm update fast-uri`). Not fixed by SDK 58 alone |
| GHSA-wjr9-j795-jxcr: host confusion through unchecked WHATWG host canonicalization | Moderate (4.8) | `fast-uri` 3.1.8 (affected ≥3.1.3 <3.1.9) | As above | As above | As above | As above |
| GHSA-xhq7-xmqj-769h: improper path equivalence in relative-reference normalization | Low (3.7) | `fast-uri` 3.1.8 | As above | As above | As above | As above |
| GHSA-333x-w4r6-6crp: scheme injection through an unescaped first-segment colon | Low (3.7) | `fast-uri` 3.1.8 | As above | As above | As above | As above |
| GHSA-w5hq-g745-h8pq: missing buffer bounds check in v3/v5/v6 when `buf` is given | Moderate (7.5) | `uuid` 7.0.3 (affected <11.1.1) | `expo` > `@expo/config-plugins` 57.0.9 > `xcode` 3.0.1 > `uuid` | **Tooling** (iOS project editing in prebuild). 0 modules | **Not reached.** `xcode/lib/pbxProject.js` calls only `uuid.v4()`, with no buffer | **In range on SDK 57:** `@expo/config-plugins` 57.0.11 → `xcode` 4.0.0, which no longer depends on `uuid` (trial a). Also in SDK 58 |
| GHSA-q3jh-wrc6-jgq8: array-form headers bypass cross-origin credential stripping | High (no CVSS given) | `follow-redirects` 1.16.0 (affected ≥1.16.0 <1.16.1), `proofs/stream-chat` | `stream-chat` 9.53.0 > `axios` 1.20.0 > `follow-redirects` | **Tooling** (the P06.1 sandbox proof client); not part of the app | **Not reached in CI.** The Foundation job installs it (`npm ci --ignore-scripts`) but runs only `node --check client/*.cjs` and offline Python tests with fakes (`checks/run_plan.py` imports `tests.fake_world`). It would be reached only in a live proof run (`client/runner.cjs` requires `stream-chat`), and only if Stream's API redirected cross-origin with the user token | **In range:** 1.16.2 within `axios`'s `^1.16.0` (lock-only `npm update`, one entry) |
| GHSA-8r9p-f939-6h3c: `sensitiveHeaders` regex escaping can expose credential headers | High (no CVSS given) | `follow-redirects` 1.16.0 | As above | As above | As above | As above |

### Packages flagged only through a dependency

These carry no GHSA of their own.

| Package (severity npm inherits) | Version | Flagged through | Runtime or tooling | Fix path |
| --- | --- | --- | --- | --- |
| `expo` (high) | 57.0.24 | `@expo/cli` | Its modules are bundled, but the flag comes from `@expo/cli` (tooling, 0 modules) | No fix while `node-forge` and `zod` remain. npm's suggested fix is `expo@44.0.6` |
| `@expo/cli` (high) | 57.0.26 | `node-forge`, `zod`, `@expo/code-signing-certificates` | Tooling | As above |
| `@expo/code-signing-certificates` (high) | 0.0.6 | `node-forge` | Tooling | npm says "in range", but 0.0.7 still requires `node-forge` `^1.4.0`, so it cannot clear the advisory |
| `expo-router` (moderate) | 57.0.22 | `query-string` | Runtime package; the flag is the `decode-uri-component` row | SDK 58 (`expo-router` ≥58.0.13; 58.0.26 tested) |
| `query-string` (moderate) | 7.1.3 | `decode-uri-component` | Runtime (1 module) | SDK 58 (removed) |
| `@expo/config-plugins` (moderate) | 57.0.9 | `xcode` | Tooling | In range: 57.0.11 |
| `xcode` (moderate) | 3.0.1 | `uuid` | Tooling | In range: 4.0.0 |

**By severity** (mobile and contracts):
- **1 critical:** `shell-quote`. Tooling, not reached, fixed in range.
- **3 high:**
  - `node-forge`: tooling, not reached, no fix;
  - `source-map-js`: tooling, not reached, fixed in range;
  - `zod`: tooling, no fix on either SDK.
- **4 moderate:**
  - `decode-uri-component`: runtime, reach not established, fixed only by SDK 58;
  - two `fast-uri` advisories: tooling, fixed in range;
  - `uuid`: tooling, not reached, fixed in range.
- **2 low:** two `fast-uri` advisories, fixed in range.
- That is 10 advisories in all; `packages/contracts` shares the four `fast-uri` ones.

**Proof:** `follow-redirects` has 2 high advisories, both fixed in range.

## 3. Trial (a): SDK 57, in range

All of this ran in `trial-a/apps/mobile`.

| Step | Command (clean environment) | Result |
| --- | --- | --- |
| a0 | `npm ci --ignore-scripts` | Installed from the starting lock |
| a1 | `EXPO_OFFLINE=1 EXPO_NO_TELEMETRY=1 npm_config_ignore_scripts=true node scripts/development.mjs install --fix` | "Dependency validation is unreliable in offline-mode / Dependencies are up to date"; exit 0, no change. Offline, the map is the installed `expo` 57.0.24's own |
| a2 (first attempt, discarded) | `… install 'expo@^57.0.0' --fix` | Exit 0; npm was "up to date" (57.0.24 satisfies the range), and `package.json` was rewritten to `"expo": "^57.0.0"`. Reset from the saved original |
| a2 | `… install expo@57.0.31 --fix` (57.0.31 is the `sdk-57` dist-tag) | `expo` 57.0.31 installed. The re-run under the new CLI updated 5 modules to `~` ranges: `expo-constants` 57.0.22, `expo-image-picker` 57.0.20, `expo-linking` 57.0.13, `expo-router` 57.0.29, `expo-splash-screen` 57.0.10. **Exit 1:** "Cannot automatically write to dynamic config at: app.config.ts. Add … `\"plugins\": [\"expo-splash-screen\"]`". The packages were installed. Audit: 10 (1 critical, 5 high, 4 moderate) |
| a3 | `npm update --ignore-scripts shell-quote fast-uri @expo/code-signing-certificates` | "changed 2 packages": `shell-quote` 1.12.0, `fast-uri` 3.1.9. `@expo/code-signing-certificates` stayed 0.0.6; 0.0.7 would not clear the advisory. `package.json` unchanged |
| a4 | The five `~57.0.x` ranges pinned exactly (the repository's `save-exact`), then `npm install --ignore-scripts` | "up to date"; lock versions unchanged |
| a5 | `rm -rf node_modules && npm ci --ignore-scripts` | 676 packages added. Audit: 8 (5 high, 3 moderate) |
| a6 | `packages/contracts`: `npm ci --ignore-scripts` (needed by Metro's watch folders and the generated validators) | 20 packages |

**Smaller of the two methods:** `npm update`. Every in-range advisory left after the installer step was a transitive package that `npm update <package>` could move within its parent's range. `overrides` would have added a `package.json` block; `npm update` changed only the lock.

**Advisories left** (`npm audit --package-lock-only`): **8 packages, 0 critical, 5 high, 3 moderate.**
- **High:** `expo`, `@expo/cli`, `@expo/code-signing-certificates`, `node-forge` (GHSA-86w9-cpqp-85rv) and `zod` (GHSA-mrhx-c7xc-m3w5).
- **Moderate:** `expo-router`, `query-string` and `decode-uri-component` (GHSA-vcc3-ghjq-m6fr).
- That is **3 advisories**.

**Lock change** against the starting lock (686 entries against 680):
- **Added 12:**
  - `@expo/metro-config` 57.0.13, `@expo/metro-runtime` 57.0.17, `@expo/ui` 57.0.26, `babel-preset-expo` 57.0.16 and `expo-asset` 57.0.20. These were hoisted, and their nested 57.0.12–57.0.19 copies removed;
  - nested `picomatch` 4.0.7;
  - nested `@expo/json-file` 11.2.1;
  - five nested `@radix-ui/*` under `vaul`.
- **Removed 6:** `uuid` 7.0.3, plus the five nested copies above.
- **Changed 42:** `expo` 57.0.24 → 57.0.31, `@expo/cli` 57.0.26 → 57.0.32, `expo-router` 57.0.22 → 57.0.29, `expo-modules-core` 57.0.18 → 57.0.24, `@expo/config-plugins` 57.0.9 → 57.0.11, `xcode` 3.0.1 → 4.0.0, `postcss` 8.5.28 → 8.5.32, `source-map-js` 1.2.1 → 1.2.2, `shell-quote` 1.10.0 → 1.12.0, `fast-uri` 3.1.8 → 3.1.9, and other `@expo/*`, `expo-*` and `@radix-ui/*` patch versions.
- **Install scripts:** no new `install`, `preinstall` or `postinstall` script. The only install script in the lock is `fsevents` 2.3.2, unchanged from the start.
- **`package.json`:** 6 version lines (`expo`, `expo-constants`, `expo-image-picker`, `expo-linking`, `expo-router`, `expo-splash-screen`).
  - The installer also moved `ajv` and `ajv-formats` to alphabetical order. The second stage can keep or undo that.
  - `dependency-inventory.json` would need its matching update (`apps/mobile/AGENTS.md`, "Dependency changes" step 3); not done here.

**Checks (D4)**, from `trial-a/apps/mobile`:

| Check | Result |
| --- | --- |
| `npm run check` | Exit 0: `tsc --noEmit` clean, `eslint .` clean, 621 tests, 621 pass, 0 fail. Baseline: the same 621/621 |
| `EXPO_OFFLINE=1 npm run check:expo` | Exit 0, "Dependencies are up to date" (the offline map of the installed 57.0.31) |
| `EXPO_OFFLINE=1 npm run export:development` | Exit 0: iOS 8.1 MB, Android 8.7 MB. `decode-uri-component` and `query-string` still bundled (1 module each); the others still 0 |
| `npm run test:rendered` | **Not run** (D4): it needs the Chromium revision `@playwright/test` pins, which only CI has. A gap for the second stage's CI |
| `packages/contracts`, `npm run check` (after `npm update fast-uri`) | Exit 0, 586/586. Baseline: the same |

**What broke:** nothing in the checks.
- **One manual step:** Expo's installer exits 1 because it cannot add `'expo-splash-screen'` to the dynamic `app.config.ts`. In the copy, adding it is 1 line in `plugins`, after `'expo-router'`. With it, the following all passed again with the lock unchanged:
  - `install --fix`: up to date;
  - `npm run check`: 621/621;
  - `check:expo`;
  - `export:development`.
- **Pins:** the installer writes `~57.0.x` ranges in spite of `.npmrc`'s `save-exact`. The second stage must pin them exactly (5 lines), as here.

## 4. Trial (b): SDK 58

### Expo's upgrade guide

- **Read on `docs.expo.dev`:** `workflow/upgrading-expo-sdk-walkthrough.md` (modified 16 October 2026). Its steps are:
  1. `npm install expo@^58.0.0`;
  2. `npx expo install --fix`;
  3. `npx expo-doctor`;
  4. with Continuous Native Generation, delete `android`/`ios` (none exist here);
  5. read the SDK 58 release notes.
- **Release notes not read:** they are at `expo.dev/changelog/sdk-58`, which is not `docs.expo.dev`, so they are outside D3 (see "Not read or not run").
- **Also read:**
  - `router/migrate/sdk-57-to-58.md` (modified 23 October 2026);
  - `versions/v58.0.0.md`: SDK 58 targets React Native 0.88, React 19.3.0 and minimum Node 22.13.x;
  - the v58.0.0 reference pages for `imagepicker`, `constants`, `linking`, `splash-screen`, `reanimated` and `router`, and v57.0.0 `imagepicker` for comparison.

### Steps

All of this ran in `trial-b/apps/mobile`. The guide's steps 1 and 2 went through the wrapper in one command, as `apps/mobile/AGENTS.md` requires.

| Step | Command (clean environment) | Result |
| --- | --- | --- |
| b0 | `npm ci --ignore-scripts`, and in `packages/contracts` | 670 and 20 packages |
| b1 | `EXPO_OFFLINE=1 EXPO_NO_TELEMETRY=1 npm_config_ignore_scripts=true node scripts/development.mjs install expo@58.0.19 --fix` (58.0.19 is `latest`) | `expo` 58.0.19 installed. The `--fix` re-run listed 17 modules to update and wrote their versions to `package.json`, then **failed** in `npm install` with `ERESOLVE … Conflicting peer dependency: expo-symbols@58.0.4` (`peerOptional expo-symbols@"^58.0.4"` from `expo-router` 58.0.26). The cause: the old `expo-router` 57.0.22 holds `expo-symbols` 57.0.3 at the top level as a regular dependency. Exit 1 |
| b2 | `npm install --ignore-scripts` | The same `ERESOLVE`; exit 1 |
| b3 | `npm uninstall --ignore-scripts expo-router` (prunes the old router and its `expo-symbols` 57) | Exit 0; added 15, removed 147, changed 60 |
| b4 | `… node scripts/development.mjs install expo-router` | Exit 0; `expo-router` 58.0.26 installed, added 34, removed 2 |
| b5 | `… node scripts/development.mjs install --fix` | "Dependencies are up to date"; exit 0 |
| b6 | 12 `~` ranges pinned exactly to the lock's versions, then `npm install --ignore-scripts` | "up to date". Audit (guide only): **7** packages (1 critical `shell-quote`, 5 high, 1 moderate `fast-uri`) |
| b7 | `npm update --ignore-scripts shell-quote fast-uri`, then `rm -rf node_modules && npm ci --ignore-scripts` | Changed 2; 652 packages. Audit: **5** |

**Not run:** `npx expo-doctor`, the guide's third step. It would fetch an unpinned package through `npx` and query services outside D3.

**Advisories left** (after b7): **5 packages, all high:** `expo`, `@expo/cli`, `@expo/code-signing-certificates`, `node-forge` (GHSA-86w9-cpqp-85rv) and `zod` (GHSA-mrhx-c7xc-m3w5). That is **2 advisories**, both tooling and neither fixable. `decode-uri-component` and `query-string` leave the lock and the bundles.

### Lock change

Against the starting lock (671 entries against 680): **added 59, removed 68, changed 105.** 71 of the changes cross a major version (or a 0.x minor).

- **Key changes:**
  - `expo` 57.0.24 → 58.0.19;
  - `@expo/cli` → 58.1.15;
  - `expo-router` → 58.0.26;
  - `react-native` 0.86.3 → 0.88.0, with all `@react-native/*` packages → 0.88.0;
  - `react` and `react-dom` 19.2.3 → 19.3.0;
  - `metro` 0.84.5 → 0.87.2;
  - `hermes-compiler` 250829098.0.17 → 260318099.0.4;
  - `react-native-gesture-handler` **2.32.0 → 3.3.0**;
  - `react-native-reanimated` 4.5.1 → 4.7.1;
  - `react-native-worklets` 0.10.1 → 0.13.0;
  - `react-native-screens` 4.26.0 → 4.30.0;
  - `react-native-safe-area-context` 5.7.0 → 5.10.1;
  - `react-native-web` 0.21.0 → 0.21.4;
  - every `expo-*` module → 58.
- **New top-level packages** for the second stage's lock review:
  - **`2g` 1.0.1:** "Low-overhead structured event logs for agents and developers". It has a `bin`. Required by `@expo/cli` 58, `@expo/metro-config` 58 and `@expo/metro-file-map` 58. One npm maintainer; repository `github.com/kitten/2g`;
  - **`noxcturnal` 0.1.10:** "Native-backed JavaScript transform runtime", required by `@expo/metro-config` 58. It has 8 optional platform-binary packages, `@noxcturnal/noxcturnal-*`, and `@oxc-project/types`. One npm maintainer; repository `github.com/expo/noxcturnal`;
  - **`expo-modules-macros` 0.22.0** (Swift macro plugin), with 4 optional platform binaries, `@expo/modules-macros-*`;
  - **`expo-modules-cli`** 0.3.2 and **`@expo/platforms`** 58.0.1;
  - **`flow-parser` / `flow-estree`** 0.331.0.

  I recorded these packages' registry metadata only; I did not review their contents.
- **Removed:** `query-string`, `decode-uri-component`, `uuid`, `vaul`, `expo-symbols` 57, `@egjs/hammerjs`, `react-remove-scroll` and others.
- **Install scripts:** no new `install`, `preinstall` or `postinstall` script; still only `fsevents` 2.3.2.
- **`package.json`:** 18 version lines (every Expo module, `react`, `react-dom`, `react-native` and the five React Native libraries).

### Checks (D4)

All from `trial-b/apps/mobile`.

| Check | Result |
| --- | --- |
| `npm run typecheck` | **Exit 2, 11 errors in 3 files.** In React Native 0.88's generated types, `View` and `Text` are function components, so `useRef<View>`, `useRef<Text>` and `View \| null` are no longer instance types. Errors at `src/chat/screen.tsx:63,109,138` (`measureLayout` missing on the ref type, plus 4 implicit `any`s from it), `src/components/ui.tsx:42,51,64` and `src/interactions/controls.tsx:22` |
| `npm run lint` | Exit 0 |
| `npm test` | Exit 0, 621/621 |
| The fix, tried in the copy | Typing those refs as `HostInstance` (exported by `react-native` 0.88) |
| `npm run check` after the fix | Exit 0: typecheck clean, lint clean, 621/621 |
| `EXPO_OFFLINE=1 npm run check:expo` | Exit 0, "Dependencies are up to date" (the offline map of 58.0.19) |
| `EXPO_OFFLINE=1 npm run export:development` | Exit 0: iOS 8.2 MB, Android 8.1 MB. 0 modules of `decode-uri-component`, `query-string`, `shell-quote`, `zod`, `node-forge` and `fast-uri` |
| `npm run test:rendered` | **Not run** (D4); a gap for the second stage's CI |

**The ref-type fix,** 11 lines in 3 files, each line a type annotation or import:
- `src/chat/screen.tsx`, 5 lines: the import, and lines 60, 97, 98 and 115;
- `src/components/ui.tsx`, 4 lines: the import, and lines 30, 46 and 55;
- `src/interactions/controls.tsx`, 2 lines: the import, and line 12.

### What broke, and what fixing it takes

1. **The installer cannot finish in one step.** npm's `ERESOLVE` on `expo-symbols` needs `npm uninstall expo-router`, then `install expo-router` through the wrapper. That is two extra commands and no file edit beyond the installer's own.
2. **The typecheck.** 11 lines in 3 files (above). Type-only; the runtime code is unchanged.
3. **Pins.** The installer's 12 `~` ranges must be pinned exactly.
4. **Not known until CI's rendered suite runs**, from the Router migration guide applied to this app's code. Each item below touches the app:
   - **Protected routes:** "A route whose guard fails renders a redirect instead of being removed from the route tree."
     - This touches every guard in `src/app/_layout.tsx:36-49` (14 `Stack.Protected` blocks).
     - The rendered suite tests these guards and the query/hash rejection, so its result on 58 is unknown.
     - A fix, if needed, is in `_layout.tsx` (possibly `redirectTo`) and `src/onboarding/routes.ts`. Size unknown.
   - **The module-level `router`:** "still available, but it throws before the first router render".
     - The app imports `router` in 20 files (about 50 `router.push`/`replace` calls, mostly in handlers).
     - The root layout's `router.replace('/')` in `src/app/_layout.tsx:32` runs in an effect gated on `useRootNavigationState()?.key`, so it should run after the first render. Not tested.
     - The guide prefers `useRouter()`; moving to it is optional, about 20 files.
   - **`useRootNavigationState`:** navigation state is "an implementation detail" in 58. The app reads only `.key`, in `_layout.tsx:14,24,33`. Low risk, not tested.
   - **Web only** (the rendered harness, not a product platform):
     - `SafeAreaView` spacing moves to CSS safe-area insets. Used in `src/components/ui.tsx` and `src/chat/screen.tsx`;
     - async routes are now on by default on web.

     Either could change the 320px layout cases.
   - **Not used by the app:** `initialRouteName`, `redirect`/`initialParams` on `Screen`, tabs or drawers, `freezeOnBlur`, `navigation.dispatch`, `beforeRemove`, `expo-router/react-navigation`, `expo-router/head`, `+html.tsx`, Router testing helpers. iOS 26 header appearance does not apply either (`headerShown: false`).

### Breaking changes for the APIs this app uses

| API | Source read | What touches the app's code |
| --- | --- | --- |
| `expo-router` | Router 57→58 migration guide; v58 `router` reference. The full changelog (github.com) is unread | The items in point 4 above. Also, `expo-symbols` and `@expo/ui` become optional peers; the app needs neither, and both left the lock |
| `expo-image-picker` (`launchImageLibraryAsync` with `mediaTypes: ['images']`, `allowsMultipleSelection`, `allowsEditing`, `quality`, `base64`, `exif`; config plugin `photosPermission`, `cameraPermission`, `microphonePermission`) | `CHANGELOG.md` in the 58.0.10 tarball, 58.0.0–58.0.10: no "Breaking changes" section. The v57 and v58 reference pages name each option the same number of times | **None found.** `src/media/picker.ts` is unchanged |
| `expo-constants` | 58.0.13 changelog: no breaking section. v58 reference: deprecations of fields the app does not use | **None:** the app's source does not import it |
| `expo-linking` | 58.0.14 changelog: no breaking section; "Create development deep links from the bundle URL's authority". v58 reference deprecates `useURL` for `useLinkingURL` | **None:** the app's source does not import it |
| Splash screen (`expo-splash-screen`) | 58.0.11 changelog: no breaking section. v58 reference: "Using the config plugin … is the recommended method … other methods are now considered legacy and will be removed" | **None in code:** the app neither imports it nor configures a splash. The plugin entry Expo's 57 installer asked for (trial a) is the recommended form on 58 too |
| `react-native-reanimated` 4.5.1 → 4.7.1, `react-native-worklets` 0.10.1 → 0.13.0 | v58 `reanimated` reference page (overview only). No changelog in the npm tarballs; the upstream docs (`docs.swmansion.com`) are outside D3 and unread | **None in code:** the app's source imports neither. They are Router peers. Their native-side changes are unverified (no native build) |
| Also: `expo-font` (installed, not imported) | 58.0.0 changelog, "Breaking changes": `getLoadedFonts()` no longer reports PostScript names on iOS | None: the app does not import `expo-font` |
| Also: `react-native-gesture-handler` 2 → 3 (major) | No changelog read (outside D3) | The app's source does not import it; it is a Router peer. Unverified |

## 5. `packages/contracts` and `proofs/stream-chat` (D6)

**`packages/contracts`, `fast-uri`:**
- an in-range fix exists;
- in a scratch copy, `npm update --ignore-scripts fast-uri` changed one lock entry (3.1.8 → 3.1.9; no package added or removed; no install script);
- `npm audit --package-lock-only` then found 0 vulnerabilities;
- `npm run check` passed, 586/586, as on the baseline.

**`proofs/stream-chat`, `follow-redirects`:**
- an in-range fix exists;
- in a scratch copy, `npm update --package-lock-only --ignore-scripts follow-redirects` changed one lock entry (1.16.0 → 1.16.2, within `axios` 1.20.0's `^1.16.0`);
- the audit then found 0 vulnerabilities;
- no proof command was run, and nothing was installed in the proof's copy.

**Does the Foundation workflow still install `proofs/stream-chat`?** Yes. The `proof` job ("Stream proof checks", `.github/workflows/foundation.yml:169-196`) runs `npm ci --ignore-scripts` in `proofs/stream-chat`, then:
- the offline Python tests in a clean environment;
- ruff and mypy;
- `node --check` on `client/*.cjs`;
- `python checks/run_plan.py`, which uses the fake world.

It installs `follow-redirects` but never executes it. The lock's one install script there, `stream-chat` 9.53.0, does not run under `--ignore-scripts`.

## 6. The recommendation (Outcome 4)

### The three paths

| Path | Advisories left | Cost |
| --- | --- | --- |
| **(A) Stay on 57, in range**, plus `fast-uri` in contracts and `follow-redirects` in the proof | **8** mobile packages (5 high, 3 moderate), from 3 advisories: GHSA-86w9-cpqp-85rv (`node-forge`), GHSA-mrhx-c7xc-m3w5 (`zod`), GHSA-vcc3-ghjq-m6fr (`decode-uri-component`). Contracts and proof: 0 | `apps/mobile/package.json` 6 version lines; `app.config.ts` 1 line (optional, the splash plugin); `package-lock.json` +12 −6 ~42; `dependency-inventory.json` to match. Contracts lock 1 entry; proof lock 1 entry. No source change. All D4 checks pass |
| **(B) Upgrade to 58 before E11**, with the same in-range updates | **5** mobile packages (all high), from 2 advisories: GHSA-86w9-cpqp-85rv and GHSA-mrhx-c7xc-m3w5. Contracts and proof: 0 (if included) | `package.json` 18 version lines; `package-lock.json` +59 −68 ~105 (71 across a major); `dependency-inventory.json`; 11 source lines in 3 files; two extra installer steps. Native modules change (React Native 0.88, Hermes, gesture-handler 3). New single-maintainer packages to review (`2g`, `noxcturnal` and its binaries). The rendered suite's result is unknown (Router 58 protected-route and web changes), so the real cost may grow by the fixes it finds |
| **(C) The recommended mix** | As (A) until the SDK 58 item lands, then as (B) | The (A) cost now; the (B) cost later, as its own item before P06.3 |

### Why each remaining advisory is or is not acceptable

- **`node-forge` GHSA-86w9-cpqp-85rv (high):** left by every path. No patched version exists.
  - It is tooling (Expo CLI code signing), and the vulnerable `verify` is not reached in this project: no EAS project and no `updates.codeSigningCertificate`.
  - Acceptable as recorded risk, by Nathan, until a patched release or an `@expo/cli` that drops it.
- **`zod` GHSA-mrhx-c7xc-m3w5 (high):** left by every path. `@expo/cli` 57 and 58 pin `^3.25.76`.
  - It is tooling. Its inputs are the repository's ESLint config and installed packages' DevTools schemas, not untrusted data.
  - Acceptable as recorded risk, by Nathan, until `@expo/cli` moves to `zod` 4.6.6 or later.
- **`decode-uri-component` GHSA-vcc3-ghjq-m6fr (moderate):** left by (A), and by (C) until the upgrade.
  - It is the only advisory in the app's bundle. Its reach is not established: Expo Router's own parser uses `URLSearchParams`, and the routes are query-free.
  - The worst case is a client-side denial of service from a crafted deep link, in a fixture-only development preview with no release build.
  - Acceptable for the time until SDK 58; Nathan's decision.
- **The other 7 packages** (`expo`, `@expo/cli`, `@expo/code-signing-certificates`, `expo-router`, `query-string`, `@expo/config-plugins` and `xcode`) carry no advisory of their own. They clear or remain with the rows above.
- **(A) clears the critical** (`shell-quote`) **and every in-range high and moderate**, and changes no source.
- **(B) clears one further moderate** than (A), at several times the lock change. It adds a native-module major upgrade, new unreviewed packages and an unknown rendered-suite result.

### Which SDK to build E11 and P06.3 on

- **E11 on SDK 57**, after (A). E11 is release-guard, lint and copy tests and the recorded follow-ups. Nothing in it depends on SDK 58, and all its checks pass on 57.0.31.
- **P06.3 on SDK 58.** Make the upgrade its own work item, between E11 and P06.3's UI, for three reasons:
  - P06.3 adds push, a native dependency chosen against an SDK. Choosing it on 57 would mean redoing it on 58.
  - Its new navigation should be written once against Router 58's protected-route and `useRouter` behaviour.
  - Expo's own guidance is to upgrade one SDK at a time.

  That item needs its own review of the new packages, and CI's rendered suite on its exact head.

**If the manager or the Dev Manager prefers one dependency change, not two:** (B) before E11 is viable on this evidence. Every check that can run here passes after an 11-line type fix. Its open risk is the rendered suite, which only CI can answer.

## Commands run, with their result lines

- **Checkout:** only the environment check, the start-gate commands and read-only commands (`cat`, `grep`, `sed -n`, `git status`, `git rev-parse`) ran in the checkout, plus this record's commit and push.
- **Scratch copies:** every `npm`, `node scripts/development.mjs`, `npx` and `curl` command ran there or in the scratch documents directory. Each table above gives its command and result.

| Where | Command | Result line |
| --- | --- | --- |
| scratch | `git archive 671d1a5… \| tar -x -C <copy>`, three times | `baseline`, `trial-a`, `trial-b` |
| `baseline` | `git init -q`, then `rm -rf .git` (a mistaken init, undone; the scratch copy only) | — |
| `baseline/{apps/mobile,packages/contracts,proofs/stream-chat}` | `npm audit --package-lock-only --json` | Exit 1 each. `{"moderate":7,"high":6,"critical":1,"total":14}`, `{"moderate":1,"total":1}`, `{"high":1,"total":1}` |
| `baseline/apps/mobile`, `baseline/packages/contracts` | `npm ci --ignore-scripts` | Installed; npm's audit summary as above |
| scratch | `npm view <pkg> dist-tags.latest` for the 11 flagged packages; `npm view expo dist-tags`, `expo-router dist-tags`, `react-native dist-tags.latest` | `node-forge` 1.4.0 latest; `shell-quote` 1.12.0; `source-map-js` 1.2.2; `zod` 4.6.7; `fast-uri` 4.2.3; `follow-redirects` 1.16.2. `expo` `sdk-57` 57.0.31, `latest` 58.0.19; `expo-router` `sdk-57` 57.0.29, `latest` 58.0.26; `react-native` 0.88.0 |
| `baseline/apps/mobile` | `npm explain <pkg>` for 12 packages | Paths as in step 2 |
| `baseline/apps/mobile` | `EXPO_OFFLINE=1 npm run export:development` | Exit 0; `Exported: .work/native-export` |
| `baseline/apps/mobile` | `npm run check`; `EXPO_OFFLINE=1 npm run check:expo` | Exit 0, 621/621; exit 0, "Dependencies are up to date" |
| `baseline/packages/contracts` | `npm run check` | Exit 0, 586/586 |
| scratch | `npm view zod versions` (3.x), `npm view expo@57 version`, `npm view @expo/code-signing-certificates@0.0.7 dependencies`, `npm view expo-symbols@58.0.4 …`, `npm view expo-router@58.0.26 peerDependencies …`, `npm view follow-redirects@1.16 version`, `npm view @expo/cli dist-tags`, `npm view <2g, noxcturnal, expo-modules-macros, expo-modules-cli> description repository.url maintainers` | As cited in the rows above |
| `trial-a/apps/mobile` | Steps a0 to a6, then the D4 checks; the splash-plugin re-run | As in step 3 |
| `trial-b/apps/mobile` | Steps b0 to b7, then the D4 checks before and after the ref-type fix | As in step 4 |
| `trial-a/packages/contracts` | `npm ci --ignore-scripts`; `npm update --ignore-scripts fast-uri`; `npm audit --package-lock-only`; `npm run check` | Changed 1; 0 vulnerabilities; exit 0, 586/586 |
| `trial-a/proofs/stream-chat` | `npm update --package-lock-only --ignore-scripts follow-redirects`; `npm audit --package-lock-only` | Changed 1 entry; 0 vulnerabilities |
| scratch documents | `curl -sS https://docs.expo.dev/llms.txt` and the 9 pages named in step 4 | All HTTP 200 |

## Not read or not run, and the limits

**Not read:**
- **The SDK 58 release notes,** `expo.dev/changelog/sdk-58`. The upgrade guide sends readers there, but the host is `expo.dev`, not `docs.expo.dev`, so it is outside D3. Any breaking change listed only there is unknown to this record.
- **On `github.com`:**
  - the Expo Router `CHANGELOG.md`, which the migration guide links;
  - the `expo-upgrade` skill;
  - the GHSA advisory pages. Each advisory's detail comes from `npm audit`'s JSON (title, CVSS, affected range).
- **Upstream documentation and changelogs** for `react-native` 0.87–0.88, `react-native-reanimated`, `react-native-worklets`, `react-native-gesture-handler` 3 and `react-native-screens`. They are outside D3, and their npm tarballs ship no changelog.

**Not run:**
- **`npm run test:rendered`,** in both trials (D4): the pinned Chromium is only in CI. This is the main open risk for (B).
- **`npx expo-doctor`** (the guide's third step): it would fetch an unpinned package and call services outside D3.
- **No native build, simulator, emulator or device run.** Native-module changes (React Native 0.88, Hermes, gesture-handler 3, Reanimated 4.7, worklets 0.13, the new Swift macro and transform binaries) are untested beyond JavaScript bundling.
- **No `eas`, `playwright install`, `migrate`, provider call or database connection.**

**Limits:**
- **Offline installer map.** Expo's installer and `check:expo` ran offline (`EXPO_OFFLINE=1`), against the installed `expo` package's own version map. Expo warns that offline validation "is unreliable". The online map from the Expo API was not consulted (outside D3).
- **Reach was read, not tested.** Reach rests on reading the installed packages' code paths, not on runtime instrumentation. It is a code-path analysis, not a proof that no path exists. In particular, the `decode-uri-component` fallback path was traced, not exercised.
- **New packages unreviewed.** The SDK 58 lock adds packages (`2g`, `noxcturnal` and their platform binaries, `expo-modules-macros`) whose contents I did not review. I recorded their registry metadata only.
- **Point in time.** The counts are as of 26 October 2026. The npm advisory database and the registry's dist-tags change over time, so a re-run later may differ.

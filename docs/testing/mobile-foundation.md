# P01.3 native mobile foundation evidence

Recorded 23 September 2026. New app-owned implementation under `apps/mobile/`. Repository governance: GAPP-PF01 D01/D02/D03/D06/D08. This evidence describes isolated development only. No protected HDE resource, database, external provider, deployment, signing identity, store record or external user was touched by this work.

## What exists

Official Expo scaffold narrowed to native iOS/Android, Expo Router routes, strict TypeScript, exact package pins and npm lockfile, supported lint/type tools, and a recommended-first development screen. All identities are explicitly fictional; compatibility remains pending with fixture provenance. `Next fictional profile` is local navigation, not a pass. `Explore more` opens the broader layout with the same declared fixtures. No auth, likes, matches, chat, permissions, photos or persistence are implemented. Screens use native controls, scalable text, scrollable content, safe areas, labels and non-gesture actions; accessibility acceptance remains untested on devices.

Bundled fixtures can run without any endpoint. An explicitly configured development API origin instead exercises a credential-free GET to `/api/v1/development/recommendations`. The client accepts only the closed `gapp-dev-v1` fixture projection. Unknown/private keys, numeric scores, ready HDE results, duplicate identities, invalid/underage ages and invalid versions are rejected. Network and contract failures show retry state without changing data source. Requests have a five-second timeout and caller cancellation. No birth data is requested or sent.

Build configuration permits only explicit development fixture mode and a development EAS profile, if any. The route root also requires React Native `__DEV__`. Production/preview builds are rejected; no production deployment/signing config exists. The fixture shell cannot be considered production ready by changing an environment label.

## Reproducible baseline and sources

Observed runtime: Linux container, Node **24.19.0**, npm **11.9.0**. Both exact versions are declared in `apps/mobile/package.json`. Selected stable framework pins: Expo **57.0.24**, React Native **0.86.3**, React **19.2.3**, Expo Router **57.0.22**, TypeScript **6.0.3**. Complete direct and transitive pins/integrities belong to `package.json` and `package-lock.json`.

Scaffold actually executed:

```sh
CI=1 npx --yes create-expo-app@5.0.0 /workspace/scratch/be03f90e714e/glow-dating-app/apps/mobile --template expo-template-default@57.0.26 --no-install
```

The template was generated successfully, then tutorial screens, sample assets and web output configuration were replaced. The upstream MIT notice is preserved in `EXPO-TEMPLATE-LICENSE.md`. `dependency-inventory.json` records all 669 lockfile package entries and their declared licenses; all entries declare license metadata. This is a metadata inventory, not a legal review or a complete supply-chain security certification.

Official sources checked before pinning:

- [Expo SDK 57 release](https://expo.dev/changelog/sdk-57): stable release with React Native 0.86.
- [Expo SDK 57 reference](https://docs.expo.dev/versions/v57.0.0/): framework/runtime compatibility table. React 19.2.3 and Node minimum 22.13.x match the selected baseline.
- [Official project setup](https://docs.expo.dev/get-started/create-a-project/): recommended default scaffold.
- [SDK 57 Expo Router](https://docs.expo.dev/versions/v57.0.0/sdk/router/), [Safe Area Context](https://docs.expo.dev/versions/v57.0.0/sdk/safe-area-context/), [StatusBar](https://docs.expo.dev/versions/v57.0.0/sdk/status-bar/): actual native APIs used.
- [ESLint supported versions](https://eslint.org/version-support/) and [typescript-eslint setup](https://typescript-eslint.io/getting-started/): maintained lint stack.

Actual npm registry checks returned `expo` latest/sdk-57 **57.0.24**, create-expo-app **5.0.0**, and expo-template-default sdk-57 **57.0.26**. SDK 58 preview/canary tags were not selected. The bundled Expo SDK compatibility map also accepted the final direct dependency versions.

Lint uses ESLint **10.11.0**, typescript-eslint **8.70.1**, @eslint/js **10.0.1**, and eslint-plugin-react-hooks **7.1.1**. Registry peer declarations support ESLint 10 and TypeScript 6.0. Expo's current lint configuration transitively selected plugins without declared ESLint 10 compatibility; that attempted setup was removed. ESLint 9 is already end of life, so it was not retained to satisfy those old peers. The maintained standard TypeScript recommended rules plus React hook rules are used instead.

Transitive caveats: Babel's `gensync@1.0.0-beta.2` is present in the official stable toolchain. This is an upstream transitive prerelease-labeled dependency, not an Expo/RN preview selection. Installation also warns that transitive `uuid@7.0.3` is deprecated. No speculative overrides were applied. Reassess upstream dependency updates during P09; these observations do not establish an exploited vulnerability or a clean vulnerability audit.

## Commands actually run and results

Commands below ran from `apps/mobile` unless specified. No output claims signed native execution.

| Command | Result | What it establishes |
|---|---|---|
| Official scaffold command above | Exit 0 | Exact official template generated |
| `npm ci --no-audit --no-fund` | Exit 0; 660 installed packages reported | Clean reinstall from final lockfile in observed Linux/runtime environment |
| `npm run typecheck` | Exit 0 | Strict TypeScript checks for app, config and tests |
| `npm run lint` | Exit 0 | Current supported ESLint/TypeScript/React hook checks |
| `npm test` | Exit 0; 11 tests pass, 0 fail | Fixture/release refusal, origin validation, closed projection/privacy refusal, endpoint request, failures, timeout and caller cancellation |
| `npm run check` after clean install | Exit 0 | Combined type/lint/test replay on the lockfile installation |
| `npm ls --depth=0` | Exit 0 | Installed direct versions match package pins |
| `EXPO_OFFLINE=1 npm run check:expo` | Exit 0; dependencies up to date | Local Expo SDK bundled-version compatibility check |
| `EXPO_OFFLINE=1 npm run export:development` | Exit 0 | Development JavaScript bundle/assets produced for iOS and Android |

The export reported 1,244 iOS modules and 1,410 Android modules, with development bundles approximately 5.6 MB and 6.3 MB. These are unoptimized development JS sizes, not release size/performance measurements. Outputs remain ignored in `.work/native-export/`.

The first online `expo install` compatibility fetch failed with an HTTP proxy timeout; it was retried in Expo's supported offline mode using the SDK's bundled compatibility data while npm performed registry installation. Offline check explicitly warns that remote dependency validation is unavailable. No React Native Directory online-health result is claimed. The initial type check exposed missing explicit Node type inclusion for tests; this was corrected. Initial lint-package resolution and stale template README were also corrected before the final successful checks.

A narrow independent source review ran the 10 tests, typecheck and direct dependency consistency checks, and found no remaining actionable scoped privacy, fabricated-HDE, cancellation-cleanup or production-display defect. It identified the stale template README, which was replaced with actual commands and limits. This is not a complete security or native UX review.

## Remaining evidence

No emulator, simulator, signed native build or physical device was run. VoiceOver/TalkBack, dynamic text layout, rotation/tablet layout, keyboard behavior, native transport/cleartext policy, offline/reconnect UX and real-device performance remain unproven. Physical-device loopback/networking is not implied by container HTTP success. No EAS identity, app-store identifiers, production auth/token storage, provider permission enforcement, live HDE result, database durability/concurrency or production readiness exists. P04 onward and the governed P11/P12 stages retain those requirements.

The root repository smoke command integrates this client's fetch/parser with the actual isolated Django HTTP process. Its separately recorded result is owned by the coordinator's root evidence; the tests here alone do not claim an actual HTTP connection.


## Bounded client-error correction

A later review identified that the exported fetch function could propagate a raw JSON parser or transport exception containing response text or a configured URL, even though the screen discarded that error. The client now creates safe public errors at its exported boundary without preserving the unsafe cause. HTTP/network failures and malformed/schema-invalid responses have fixed generic messages. Timeout and cancellation reject with a newly created `AbortError` and fixed cancellation message; aborted work cannot return a parsed result.

Validation after this correction: `npm run check` exited 0 (strict typecheck, lint, **11 tests**, 0 failures). The added test supplies a private marker through malformed JSON, a transport exception URL and an HTTP error body, and verifies that neither message/stack nor cause expose it. Existing timeout/caller-cancellation tests also assert safe `AbortError` behavior. Native bundle export evidence above predates this bounded TypeScript-only error correction and was not repeated; no new device/native execution is claimed.

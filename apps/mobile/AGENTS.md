This is an Expo/React Native mobile application. Prioritize mobile-first patterns, performance, and cross-platform compatibility.

Also follow the repository-root `AGENTS.md`. This app is a development-only fixture preview; this directory's `README.md` has the walkthroughs and verified limits.

## Expo has changed — do not trust your training data

Expo ships breaking changes every SDK release. APIs you remember are likely renamed, moved, or removed. Before writing any code that touches an Expo, EAS, or React Native API:

1. Read the major version of the `expo` package in `package.json`.
2. Fetch the matching versioned docs: `https://docs.expo.dev/versions/v<major>.0.0/`
3. For anything else, fetch https://docs.expo.dev/llms.txt — an index of all Expo docs with corrections to common LLM misconceptions. Follow its links to the specific page you need; never answer from memory.

## Commands

Run these from this directory on the pinned toolchain: Node 24.19.0 and npm 11.9.0. `.npmrc` sets `engine-strict`, so any other npm fails with `EBADENGINE`. Use npm only.

```bash
npm ci --ignore-scripts                    # install exactly from package-lock.json
npm start                                  # Expo dev server through the fixture-only wrapper
npm run android                            # the same wrapper; opens an installed Android emulator
npm run ios                                # the same wrapper; opens an installed iOS simulator
npm run check                              # typecheck, lint and unit tests
EXPO_OFFLINE=1 npm run check:expo          # SDK compatibility against the installed map
EXPO_OFFLINE=1 npm run export:development  # development JS bundles in .work/native-export
npm run test:rendered                      # fixture journeys rendered in Chromium (Playwright)
```

- `start`, `android`, `ios`, `check:expo` and `export:development` run `scripts/development.mjs`. It supplies `GLOW_APP_ENV=development` and `EXPO_PUBLIC_GLOW_MODE=fixture` and refuses any other value. `app.config.ts` rejects Expo CLI runs without them, so use the npm scripts rather than calling Expo directly.
- Run `npm run check` before declaring a mobile change done. Add `check:expo`, `export:development` and `test:rendered` when the assignment needs rendering or export proof.
- `test:rendered` needs the Chromium revision pinned by `@playwright/test`. In Claude Code cloud sessions, the preinstalled Chromium is a different revision, and `playwright install` must not be run there. The pinned-browser evidence therefore comes from hosted CI (Foundation, Mobile checks). A local run against another browser is informational only. See `docs/operations/local-development.md`.

## Dependency changes

Change dependencies only when an assignment requires it.

1. Choose the SDK-compatible version with Expo's installer, never `npm install <package>` or another package manager. Run it through the wrapper so `app.config.ts` accepts the environment: `npm_config_ignore_scripts=true node scripts/development.mjs install <package>` is `npx expo install <package>` with the fixture environment and without package install scripts. A bare `npx expo install` fails the config guard. `.npmrc` sets `save-exact`; the result must be an exact version in `package.json`.
2. Reinstall with `npm ci --ignore-scripts` and review the complete `package-lock.json` diff, including new transitive packages and install scripts.
3. Update `dependency-inventory.json` (lockfile package entries with license metadata) to match the lockfile.
4. Run the checks above. A dependency change is full scope for CI and review.

## Navigation & Routing

- Use **Expo Router** for all navigation. Routes live in `src/app/` — every file there is a screen, `_layout.tsx` files define navigators. Keep non-route code (components, hooks, utils) outside `src/app/`.
- Import `Link`, `router`, and `useLocalSearchParams` from `expo-router`.
- Docs: https://docs.expo.dev/router/introduction.md

## Release block

No EAS project, signing identity, store submission or over-the-air update is configured or authorized.

- `app.config.ts` rejects any environment other than `GLOW_APP_ENV=development` with `EXPO_PUBLIC_GLOW_MODE=fixture`, and any EAS build profile other than `development`.
- The runtime refuses to render routes when `__DEV__` is false.
- Do not run `eas` or `eas-cli` (build, submit, update), create an EAS project, add signing credentials or weaken these guards unless Nathan explicitly authorizes release work.
- `export:development` produces development JavaScript bundles, not signed builds.

## Rules

- If `ios/` and `android/` directories do not exist, they are generated (Continuous Native Generation). Never create or edit them by hand — configure native behavior in `app.config.ts` and config plugins.
- Expo Go only includes its bundled native modules. After adding a library with native code, the app needs a development build (`npx expo run:ios|android` on an equipped workstation). Native builds and device runs have not been performed for this foundation.
- Prefer recommended Expo modules over third-party libraries, and follow "Dependency changes" above before adding one.

# Glow native development foundation

A new iOS/Android Expo Router application for P01.3. This is an isolated fixture preview, not a usable dating service. All people are fictional, compatibility is pending, and the displayed order has no compatibility meaning. No login, like, match, messaging, photo upload, persistence or HDE connection exists.

## Reproduce

Use Node **24.19.0** and npm **11.9.0** (both declared in `package.json`), then from this directory:

```sh
npm ci
npm run check
npm run check:expo
npm start
```

The `start`, `android`, and `ios` scripts explicitly select development fixture mode when unset. They reject any request for a different mode. On a suitably equipped workstation, `npm run android` or `npm run ios` opens the installed emulator/simulator. Native runtime and device acceptance have not yet been performed. Consumer web delivery is outside scope; only iOS/Android are configured. React DOM/web packages are pinned Router peers, not a web product.

To exercise the nonpersistent API vertical smoke flow, first start the isolated application API using the repository setup instructions, then:

```sh
EXPO_PUBLIC_GLOW_API_BASE_URL=http://127.0.0.1:8000 npm start
```

Use `http://10.0.2.2:8000` for the Android emulator's host loopback. A physical device requires a deliberately configured reachable development origin; loopback would point at the phone itself. This code does not change native cleartext networking policies: device HTTP transport must be verified separately. Set no origin to use bundled fixtures. A configured API failure shows an error and a retry action; it never silently falls back to bundled data.

`EXPO_PUBLIC_*` variables are public application configuration, never secrets. `.env.example` lists names and purposes. No production/HDE origin or secret belongs in this preview. `app.config.ts` rejects every `EXPO_PUBLIC_*` name except `EXPO_PUBLIC_GLOW_MODE` and `EXPO_PUBLIC_GLOW_API_BASE_URL`, without echoing rejected names or values. This checks names, not the semantic contents of the allowed values; the API-origin validator still rejects credentials. Official [Expo environment guidance](https://docs.expo.dev/guides/environment-variables/) confirms these values are embedded in client code. Reopen/reload Metro after changing environment configuration.

## Implementation boundary

- `src/app`: recommended-first screen and broader discovery layout preview using the same synthetic dataset.
- `src/contracts/recommendations.ts`: closed `gapp-dev-v1` response projection using generated TypeScript and standalone runtime schema validators. Rejects private/unrecognized fields, HDE scores/ready results, duplicate IDs and underage records. These checks are defense in depth; real eligibility must be enforced by the API in later phases.
- `src/data/recommendations.ts`: credential-free, bounded GET to `/api/v1/development/recommendations`, with cancellation and response validation. No writes.
- `src/config/development.ts`: explicit fixture configuration and origin validation.
- `app.config.ts` and `src/app/_layout.tsx`: build-config and runtime development guards.

`Next fictional profile` only changes the locally displayed item. `Explore more` navigates to a list of the same fixtures. Both have non-gesture controls. There are no deceptive inactive like/chat buttons. Portraits are abstract initials, not real people or approved brand assets. Typography and color are provisional implementation styling, not a brand lock.

## Release exclusion and verification

`app.config.ts` rejects any environment except `GLOW_APP_ENV=development` with `EXPO_PUBLIC_GLOW_MODE=fixture`; it also rejects EAS profiles other than `development`. The runtime refuses to render routes when React Native `__DEV__` is false. No EAS project, signing identity, application bundle ID, production profile or store distribution is configured. These are guardrails in this foundation, not a certification of a future release pipeline.

```sh
npm run export:development
```

This creates **development JavaScript bundles/assets** for iOS and Android in ignored `.work/native-export/`. It does not compile native code, sign a package, run an emulator/device or prove accessibility and native transport behavior. Do not deploy or distribute this output to real users.

Official scaffold: `create-expo-app@5.0.0` with `expo-template-default@57.0.26`, narrowed to mobile. The upstream MIT notice is preserved in `EXPO-TEMPLATE-LICENSE.txt`. Exact dependencies and integrity values are in `package.json` and `package-lock.json`. See `../../docs/testing/mobile-foundation.md` for actual commands, results, sources and remaining evidence.

## P02 contract artifacts

`src/contracts/generated/` is generated from `packages/contracts` schemas. Do not edit it directly. The development parser consumes generated validation and a key-uniqueness check; `production.ts` adds parsers for the P02 logical design without an HTTP client or activated production route. Use the repository contract generation/check commands in `../../packages/contracts/README.md`. All current screen data remains synthetic and pending. No native dependency/API was changed for contract validation.

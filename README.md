# Glow dating application

Private, isolated Expo/React Native and Django/DRF application foundation. App Builder 1 implements; App Planner 1 coordinates. Nathan Amthor owns the project.

Start with [the canon index](docs/pf-canon/GAPP-PF00-Canon-Index-and-Authority.md), [governing plan](docs/pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md), and [current handoff](docs/continuity/current-handoff.md).

The current milestone is a database-independent development foundation. Synthetic preview data is never genuine Human Design compatibility. Live authentication, database persistence, providers, native signed builds and release acceptance require their planned evidence. The Glow HD Engine and shared legacy resources remain protected.

## Evidence and decisions

- [Fresh foundation decision](docs/adr/0001-isolated-application-foundation.md)
- [Resource ownership and protected boundary](docs/operations/resource-ownership.md)
- [Notion work register](https://app.notion.com/p/71b769915b5b4e00830663770bc95f7e)
- [Progress reports](https://app.notion.com/p/3e44590a05eb81d58971ee4cd870774f)

## Run the development foundation

Use Python 3.12.14, Node 24.19.0 and npm 11.9.0. Install the API's hash-locked development dependencies as described in [API setup](services/api/README.md), and use `npm ci --ignore-scripts` in `apps/mobile/` as described in [mobile setup](apps/mobile/README.md).

From the repository root, `node scripts/smoke.mjs` starts a temporary loopback Django process and tests the actual mobile TypeScript HTTP client against it. No database, account, provider, real Human Design result or production endpoint is involved. API liveness is 200; readiness deliberately remains 503. `npm run export:development` in the mobile directory produces iOS/Android development JavaScript bundles only.

[Foundation CI](.github/workflows/foundation.yml) repeats API, mobile and HTTP-client checks from checkout. [Branch policy](docs/operations/ci-and-branch-policy.md) records the account's enforcement limitation. No deployment or production connection is established by this repository.

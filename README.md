# Glow dating application

Private, isolated Expo/React Native and Django/DRF application foundation. App Builder 1 implements; App Planner 1 coordinates. Nathan Amthor owns the project.

Start with [the canon index](docs/pf-canon/GAPP-PF00-Canon-Index-and-Authority.md), [governing plan](docs/pf-canon/GAPP-PF01-A-to-Z-Implementation-Plan.md), and [current handoff](docs/continuity/current-handoff.md).

The current milestone adds the P04.1 native shell and synthetic account/onboarding journey to the P03 operational preparation and database-independent P02 foundation. Registration/sign-in, verification/recovery, adult/consent and private birth screens use controlled development fixtures; ordinary onboarding ends with the profile still incomplete. Production API routes remain unimplemented. Synthetic preview data is never genuine Human Design compatibility. Live authentication, database persistence, providers, native signed builds and release acceptance require their planned evidence. The Glow HD Engine and shared legacy resources remain protected.

## Evidence and decisions

- [Fresh foundation decision](docs/adr/0001-isolated-application-foundation.md)
- [Resource ownership and protected boundary](docs/operations/resource-ownership.md)
- [Same-project Railway placement](docs/adr/0002-same-project-application-services.md) and [environment/service map](docs/operations/environments.md)
- [Build/deploy preparation](docs/operations/build-and-deploy.md), [configuration catalog](docs/operations/configuration.md), [telemetry/workers](docs/operations/observability-and-workers.md) and [provider boundaries](docs/operations/providers-and-webhooks.md)
- [Secret, incident and recovery runbooks](docs/operations/operational-runbooks.md)
- [Notion work register](https://app.notion.com/p/71b769915b5b4e00830663770bc95f7e)
- [Progress reports](https://app.notion.com/p/3e44590a05eb81d58971ee4cd870774f)
- [Versioned contracts and generation](packages/contracts/README.md)
- [Static data definitions](docs/architecture/data-model.md) and [migration plan](docs/operations/migration-plan.md)
- [Trusted eligibility acquisition](docs/architecture/trusted-eligibility.md)
- [Fixture account/onboarding architecture](docs/architecture/onboarding-fixtures.md) and [P04.1 evidence](docs/testing/p04-1-checkpoint.md)
- [Provisional provider conformance](docs/architecture/provider-conformance.md)
- [Initial privacy and safety rules](docs/architecture/privacy-and-safety-rules.md)
- [Deferred database/provider/native acceptance](docs/testing/p11-deferred-acceptance.md)

## Run the development foundation

Use Python 3.12.14, Node 24.19.0 and npm 11.9.0. Install the API's hash-locked development dependencies as described in [API setup](services/api/README.md), and use `npm ci --ignore-scripts` in `apps/mobile/` as described in [mobile setup](apps/mobile/README.md).

From the repository root, `GLOW_SMOKE_PYTHON="$PWD/services/api/.venv/bin/python" node scripts/smoke.mjs` starts a temporary loopback Django process and tests the actual mobile TypeScript HTTP client against it. No database, account, provider, real Human Design result or production endpoint is involved. API liveness is 200; readiness deliberately remains 503. `npm run export:development` in the mobile directory produces iOS/Android development JavaScript bundles only.

[Foundation CI](.github/workflows/foundation.yml) repeats API, mobile and HTTP-client checks from checkout. [Branch policy](docs/operations/ci-and-branch-policy.md) records the account's enforcement limitation. No deployment or production connection is established by this repository.

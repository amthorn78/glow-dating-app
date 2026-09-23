# P01.3 foundation checkpoint

Observed 23 September 2026 in the isolated Linux work environment. This is the first implementation increment for the new private `amthorn78/glow-dating-app` repository. The authority-transfer commit is `ac38e58651e5578ee8503b6423e4884203b42278`; its evidence commit is `0bfdbf5db34531af38fec3f29c828e9a1acb16c7`. Code publication uses `app-builder-1/foundation`; exact published candidate and CI evidence are recorded in the subsequent handoff/report.

## Implemented scope

Pinned Django/DRF API, pinned Expo/React Native/TypeScript native shell, dependency and license inventories, closed development JSON Schema/OpenAPI, setup commands, deterministic synthetic fixtures, and CI definition. The root HTTP smoke runs the actual mobile fetcher/parser against the actual Django process. Candidate screens present recommendations first and an Explore route, with explicit fictional identities and pending compatibility. This is not onboarding, matching or a functioning dating service.

The process accepts only development/test fixture configuration. It refuses final database and live HDE configuration. Liveness is 200; readiness deliberately remains 503. No auth endpoint, database driver, model/migration, production provider, secret, deployment or signed native build is supplied. No legacy code was imported or executed.

## Validation evidence

| Check | Actual evidence |
|---|---|
| API reproducibility | Hash-enforced 16-package development lock installed into two fresh virtual environments; pip consistency, Django checks, 15 original tests, Ruff format/lint and mypy passed. See `api-foundation.md`. |
| Mobile reproducibility | Clean npm lockfile install; typecheck/lint and 11 current tests pass. Offline Expo SDK compatibility check and development iOS/Android JS export passed before the final bounded error-message correction. See `mobile-foundation.md`. |
| Shared development contract | Six tests validate the real three GET projections and reject extra/private fields, numeric compatibility and invalid states. |
| Independent review | Reproduced fixed-port false acceptance in the original smoke script, Android emulator Host refusal, and raw JSON error text propagation. These required correction before publication; the public client now normalizes errors and has marker-exclusion regression coverage. The smoke now consumes a bound-port/PID handshake from its child and validates the complete readiness body; the explicit Android emulator alias is accepted while neighboring/spoofed hosts remain rejected. Final API tests: 16 pass; Ruff and mypy pass. Root HTTP smoke and occupied-old-port/startup-failure regression pass. The decoy server receives zero requests. |
| GitHub CI | Workflow is prepared; no hosted-run success is claimed at this initial checkpoint. Results require actual run/job links after publication. |

Commands for repeatable checks are in the root, API and mobile READMEs. API mypy's framework inheritance exception is explicit; no third-party internal type-safety claim is made. Expo offline validation does not establish online React Native Directory health. Dependency metadata is not a legal or vulnerability clearance.

## Review and enforcement limits

The authenticated GitHub branch-protection form reports that rules are not enforced for this private repository under the current account arrangement. No ineffective rule, account upgrade or public visibility change was made. Follow the procedural scoped-PR and exact-candidate CI policy in `../operations/ci-and-branch-policy.md`.

No physical device, emulator, native signing/build, accessibility acceptance, PostgreSQL behavior, real authentication, provider enforcement or live HDE result has been demonstrated. P02 production contracts and all later feature/integration requirements remain open. P11 owns final database integration. A01/A07 final HDE contract/throughput and A02 logical database ownership remain unresolved; no protected HDE or shared Railway resource was changed.

## First hosted run and correction

Candidate `75ca2c9ba00d8ef22d25f75100660b7f67859885` was published in [PR 1](https://github.com/amthorn78/glow-dating-app/pull/1). All 70 remote Git blob hashes matched the local publication snapshot. [Push run 35856098855](https://github.com/amthorn78/glow-dating-app/actions/runs/35856098855) passed API checks and API mobile smoke; Mobile checks failed at install because the GitHub Node 24.19.0 distribution bundled npm 11.17.0 while the tested project explicitly requires npm 11.9.0. The workflow now installs the declared npm 11.9.0 before `npm ci`; project engine enforcement was retained. A subsequent full run must establish acceptance.

## Accepted hosted foundation

Corrected candidate `ca2abecceb1e8c532efdce8af949c110b03f7429` passed [pull-request run 35856228910](https://github.com/amthorn78/glow-dating-app/actions/runs/35856228910). API checks, Mobile checks and API mobile smoke all succeeded on clean GitHub-hosted Ubuntu 24.04 checkouts. Mobile now installed the declared npm before the lockfile, and checked/exported the final client-error correction for both iOS/Android development JS targets. This supplies the clean-checkout evidence required by P01.3; it is not native signing/device evidence.

Exact head/base and successful run were checked before authorized merge. PR 1 merged at `2785bb59f692468acf058845396607be9ac5a058`; main was read back. P01.3 is Done in Notion; P02.1 is the active task. The procedural branch-policy limitation remains.

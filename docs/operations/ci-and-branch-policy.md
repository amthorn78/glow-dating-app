# Foundation CI and branch policy

P01.3 establishes repeatable checks; P03 production environment/deployment work remains open. Only the new private application repository is in scope.

`.github/workflows/foundation.yml` runs API checks, Mobile checks, and API mobile smoke on pull requests and selected pushes. Jobs use read-only contents permissions, disable persisted checkout credentials, have bounded timeouts, and use exact official action commit pins resolved from their current releases on 23 September 2026:

| Action | Release | Commit |
|---|---|---|
| actions/checkout | v7.0.1 | 3d3c42e5aac5ba805825da76410c181273ba90b1 |
| actions/setup-python | v7.0.0 | 5fda3b95a4ea91299a34e894583c3862153e4b97 |
| actions/setup-node | v7.0.0 | 820762786026740c76f36085b0efc47a31fe5020 |

API dependencies install with required artifact hashes; mobile uses npm's committed lock/integrity values and `npm ci --ignore-scripts`. Python 3.12.14, Node 24.19.0 and npm 11.9.0 are the tested runtime baseline. The GitHub-hosted ubuntu-24.04 image is managed by GitHub and is not an immutable image digest; each job records its actual runner environment. The repository does not claim fully hermetic execution.

Mobile SDK checks and JavaScript exports use Expo offline mode against the installed SDK compatibility map; this does not test remote React Native Directory health. No service credentials, database services, HDE calls or deployments are configured in CI. Native JS bundle export is development-only and is not signed iOS/Android build or device acceptance. The smoke script starts a loopback-only fixture API, consumes it through the actual mobile TypeScript client and shuts it down.

## Branch enforcement limitation

On 23 September 2026 the authenticated GitHub branch-protection form at `https://github.com/amthorn78/glow-dating-app/settings/branch_protection_rules/new` reported: "Your rules won't be enforced on this private repository until you move to a GitHub Team or Enterprise organization account." No ineffective rule is represented as protection. No account subscription, ownership transfer or public-visibility change was performed.

Until enforceable branch controls are available, App Builder 1 uses scoped branches/PRs and checks the exact candidate's actual CI results before an authorized merge. This procedural discipline is not equivalent to platform-enforced checks. Do not force-push or bypass failing checks. Any account-level protection solution is a later concrete owner/account decision; local implementation remains available.

## Results

The foundation passed hosted run 35856228910 for candidate `ca2abecceb1e8c532efdce8af949c110b03f7429` and merged through PR 1 at `2785bb59f692468acf058845396607be9ac5a058`. See `docs/testing/foundation-checkpoint.md` for the actual install/runtime correction, scope and limits. Later candidates require their own passing run.

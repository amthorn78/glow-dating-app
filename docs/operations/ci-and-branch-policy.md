# Foundation CI and branch policy

P01.3 establishes repeatable checks; P03 adds guarded API build/operational preparation. Live deployment and production activation remain pending. Only the new private application repository is in scope.

`.github/workflows/foundation.yml` runs API checks, Mobile checks, API mobile smoke, API artifact checks and, since P06.1-I2b (27 September 2026), Stream proof checks on pull requests and selected pushes. P02 extends Mobile checks with a locked contract-tool install and deterministic generation/runtime-corpus checks; the smoke job installs the mobile validator's locked dependencies. API checks include database-independent model/migration and Python contract tests. P03's artifact job builds the digest-pinned API image and exercises unsafe-mode refusal, loopback HTTP and graceful shutdown without network access or published ports; see [build and deployment preparation](build-and-deploy.md). For full-scope changes all five application jobs must pass on the actual candidate. Stream proof checks runs the offline checks of the P06.1 harness under `proofs/stream-chat/` (its hash-locked installs, its unit tests under `env -i`, Ruff, mypy, `node --check` and its run-plan count) with the pinned toolchain, in a bounded time and with no secret; the fix-reversal check stays out of CI and is run by sessions and reviews. Ordinary documentation uses the explicit exemption below; skipped jobs are not application test passes. Jobs use read-only contents permissions, disable persisted checkout credentials, have bounded timeouts, and use exact official action commit pins resolved from their current releases on 23 September 2026:

| Action | Release | Commit |
|---|---|---|
| actions/checkout | v7.0.1 | 3d3c42e5aac5ba805825da76410c181273ba90b1 |
| actions/setup-python | v7.0.0 | 5fda3b95a4ea91299a34e894583c3862153e4b97 |
| actions/setup-node | v7.0.0 | 820762786026740c76f36085b0efc47a31fe5020 |
| actions/upload-artifact | v4 (workflow comment; exact patch release not verified) | ea165f8d65b6e75b540449e92b4886f43607fa02 |

API dependencies install with required artifact hashes; mobile uses npm's committed lock/integrity values and `npm ci --ignore-scripts`. Python 3.12.14, Node 24.19.0 and npm 11.9.0 are the tested runtime baseline. The GitHub-hosted ubuntu-24.04 image is managed by GitHub and is not an immutable image digest; each job records its actual runner environment. The repository does not claim fully hermetic execution.

Mobile SDK checks and JavaScript exports use Expo offline mode against the installed SDK compatibility map; this does not test remote React Native Directory health. No service credentials, database services, HDE calls or deployments are configured in CI. Native JS bundle export is development-only and is not signed iOS/Android build or device acceptance. The smoke script starts a loopback-only fixture API, consumes it through the actual mobile TypeScript client and shuts it down.

## Branch enforcement limitation

On 23 September 2026 the authenticated GitHub branch-protection form at `https://github.com/amthorn78/glow-dating-app/settings/branch_protection_rules/new` reported: "Your rules won't be enforced on this private repository until you move to a GitHub Team or Enterprise organization account." No ineffective rule is represented as protection. No account subscription, ownership transfer or public-visibility change was performed.

Until enforceable branch controls are available, App Builder 1 uses scoped branches/PRs and checks the exact candidate's actual CI results before an authorized merge. This procedural discipline is not equivalent to platform-enforced checks. Do not force-push or bypass failing checks. Any account-level protection solution is a later concrete owner/account decision; local implementation remains available.

**No paid plan** (Nathan, 25 September 2026; OD-24): *"No paid plan at this time; there is no budget for it. Use the review and branch controls available at no additional cost, document any protection we cannot enforce, and revisit a paid plan when there is a budget."*

- **Not enforced on this private personal repository:**
  - required status checks;
  - required reviews;
  - blocking direct pushes to `main`;
  - blocking force-pushes;
  - code-owner review.
- **The procedural substitutes in force:**
  - the Foundation gate on the exact head;
  - the exact-head review;
  - waiting for Codex's review;
  - the pre-merge checklist in the PR description (manager workflow, step 7);
  - the Dev Manager's read of governing Markdown;
  - never force-pushing.
- **A no-cost option:** Dependabot alerts, which only Nathan can turn on in the repository's settings. Whether they are free for this private repository was not verified from a session.
- **Revisit** a paid plan when there is a budget, and at P09 (release preparation) at the latest.

**No Stream secret in CI** (OD-20). No Foundation job needs or receives a Stream credential. The harness job P06.1-I2b added, Stream proof checks, runs offline, references no secret and sets no `env:`, and its tests assert that no `STREAM_*` variable is present. If a future job ever needs a secret, it is a repository secret referenced only by that step, and adding it is full scope.

**Intermittent failures** (OD-21). A passing rerun alone does not resolve an intermittent failure. A head whose run failed intermittently needs a diagnosis, and then a fix or a recorded, reviewed explanation, before its work is accepted. See the manager workflow, step 5.

## Results

The foundation passed hosted run 35856228910 for candidate `ca2abecceb1e8c532efdce8af949c110b03f7429` and merged through PR 1 at `2785bb59f692468acf058845396607be9ac5a058`. See `docs/testing/foundation-checkpoint.md` for the actual install/runtime correction, scope and limits. Later candidates require their own passing run.

## Documentation and agent-review policy — 24 September 2026

`Change scope` runs on every PR and relevant push. `scripts/change_scope.py` compares the entire PR from its merge base, or the push's before/after SHAs.

**Documentation is exempt (Nathan, 24 September 2026).** A change made only of regular Markdown (`.md`) files is ordinary documentation. It skips the five application jobs and code/security review. This covers every documentation path: `docs/`, READMEs, `AGENTS.md`/`CLAUDE.md`, plans, handoffs, prompts and canon.

**A Dev Manager read for governing Markdown** (DM-01 P1, 25 September 2026). Governing Markdown still skips CI and code review, but it is read by the Dev Manager before its PR merges. Each read covers one named commit; the charter says when a later change needs another read. That covers `AGENTS.md` or `CLAUDE.md` at any level, `docs/pf-canon/`, the manager workflow, the Dev Manager charter and this policy. Prompts that authorize credential use or live provider actions are read before Nathan runs them. That read is not a code review. See the [Dev Manager charter](../planning/dev-manager.md).

**Dependency drift** (DM-02 B9). Each phase's evidence records one `npm audit` result line per npm package it touched, so a change in the advisory picture is visible.

- **Exception:** paths under a `.claude/` directory stay full scope (Nathan, 24 September 2026). Claude Code skills, commands, agents and rules can carry shell commands, pre-approved tools and permission modes, as `.claude/settings.json` can.
- **No application check reads Markdown content.** Ruff 0.16.8 also formats Python code blocks inside Markdown, so the API's ruff configuration excludes `*.md` (`services/api/pyproject.toml`). Otherwise an exempt Markdown change could break a later API job. The pattern also matches a directory named `*.md`, so ruff skips any Python file inside one. None exists, and adding one is a non-Markdown change, so it runs the full checks and review.

A script or any other non-Markdown file, a workflow, configuration or environment template, a mixed change, executable or symlinked documentation, or an unavailable or empty comparison requires full checks. Documentation paths must not contain scripts. The classifier never reads file contents, so the manager enforces that rule by reading every documentation change it integrates.

A comparison with more than one merge base (criss-cross history) is full scope, because a single base can hide code changes.

A push run compares against the previous push, and runs of the same ref cancel each other. A Markdown-only push can therefore cancel an in-progress code run and skip every application job itself. The manager counts a push run as evidence for code only if its gate reports `Application checks passed`; otherwise it uses the PR run. Before this direction, only an inert evidence/provenance allowlist was exempt. Rename detection is disabled so moving code into documentation cannot hide its old path. New-branch zero-base pushes conservatively run full checks.

Classification loads the standard-library-only script from trusted policy (PR base, preceding main for main pushes, fetched main for feature pushes) into a runner temporary directory and executes it with Python isolated mode before any candidate Python. An earlier feature-branch commit is not a policy authority. If the trusted revision has no policy (including this first adoption), full checks run. Candidate policy tests run only in the full-scope API job, on a different runner, and cannot alter the classification output. The five application job names (`API checks`, `Mobile checks`, `API mobile smoke`, `API artifact checks`, `Stream proof checks`) remain present but are intentionally skipped for a proven ordinary-documentation change. GitHub treats condition-skipped jobs as successful for required-check purposes; the workflow itself is never path-filtered away. `Foundation gate` always reports and succeeds only for five successful application jobs or five explicitly exempt skipped jobs after successful classification (four before P06.1-I2b added the fifth). A classifier failure cannot silently exempt application checks. Preserve existing required check names; require the gate as well when enforceable repository controls become available. Current API access to branch-protection settings returned 403, so this migration does not claim newly configured enforcement.

**Trust limit and manager control.** The classifier script is loaded from reviewed history, but the `pull_request` workflow YAML and output wiring are candidate-controlled. A PR that edits that workflow can bypass its own routing/gate; this migration does not establish an immutable security boundary. Before accepting workflow or classification-policy changes, the manager independently classifies using the pre-change policy (or full scope when absent), reviews the entire workflow diff and verifies the actual commands/job steps and results. Full checks are required; green status or skipped jobs alone do not establish acceptance. This is a procedural control in the owner's high-trust agent workflow, not equivalent to an externally required workflow or enforced ruleset. A protected external/base-owned gate is a future account/control option, not silently provisioned by this migration. Do not introduce `pull_request_target` execution of candidate code just to claim stronger enforcement; see [GitHub security guidance](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target).

**AI review is governed by root `AGENTS.md`, per Nathan's direction.** The manager must classify before commissioning any code/security reviewer. Ordinary documentation: no review request or application job; an automatically launched reviewer performs only classification then reports “Review not required: ordinary documentation only.” Full scope: retain normal code/security review, correct findings and verify evidence against the exact final head before merge. A documentation-only last commit does not exempt a code PR. An unavailable classifier requires review.

The external Codex dashboard was inspected for this app on 24 September: code/security review follow personal preferences; personal code trigger is Smart detect; security trigger is Whenever code review runs. The exposed repository menus have no path exclusion or per-repository Off selection. No personal/global/HDE setting was changed. `AGENTS.md` controls reviewer work, not the external scheduler: an agent may still be launched to classify a documentation-only PR. This is not a claim of zero invocations or zero cost. Do not pretend a prose rule disables the service's trigger. If a future account-level setting supports deterministic path filtering, mirror the conservative classifier without weakening code/instruction review or changing HDE settings.

For a full-scope PR, the manager writes a bounded review prompt for its exact head, and Nathan runs it in a separate session under the manual relay ([manager workflow](../planning/manager-workflow.md)); the scope and evidence of that review are preserved. A missing reviewer capability is an explicit unresolved gate, not a passing check. Classification and test checks do not substitute for review.

Sources: [GitHub job conditions](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-jobs-with-conditions), [workflow path-filter behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax), [Codex GitHub review and AGENTS rules](https://learn.chatgpt.com/docs/third-party/github). Actual hosted evidence is in the migration publication receipt.

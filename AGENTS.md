# Glow application work

Read applicable `AGENTS.md` files, `docs/README.md`, `docs/pf-canon/GAPP-PF00-Canon-Index-and-Authority.md`, the current GAPP-PF01 plan, and `docs/continuity/current-handoff.md` before changes. Repository Markdown owns durable implementation context. Notion coordinates task state and links; Google Drive is not an operational dependency. Verify the latest remote branch/head and open PRs and preserve unrelated work.

This application is separate from the protected Glow HD Engine. Follow GAPP-PF01 D08 for authority and its effect-based protected boundary. Do not execute legacy application imports, copy secrets, connect production databases early, or treat fixtures as real Human Design results. P11 owns database integration. Record actual checks and limitations with each meaningful change.

The receiving Claude Code session is the manager and commissions separate bounded implementation sessions under `docs/planning/manager-workflow.md`. New features are paused for the migration/setup optimization. Do not import external prompt libraries as the workflow. All documentation must be `.md`; ephemeral prompts belong in `docs/ephemeral/`, persistent planning in `docs/planning/`, and existing canon in `docs/pf-canon/`.

## Code Review Rules

- Before commissioning or performing a review, classify the complete PR diff with the **trusted base revision** of `scripts/change_scope.py`, extracted outside the candidate worktree and run with `python3 -I` and `--base <base-sha> --head <head-sha> --merge-base`. Do not execute or import candidate code/tests to decide whether it needs review. A missing trusted policy, unavailable comparison or ambiguous classification requires full review. For an `ordinary-docs-only` result, do not start code/security review or application build/test jobs. If an external trigger already started you, stop after classification and report **Review not required: ordinary documentation only**. Do not inspect application code or create review findings for that exempt change.
- Preserve fixture-only runtime guards, private projections, eligibility freshness and the protected HDE boundary. A planned provider slot is not an active secret loader or a verified permission mechanism.
- Follow `docs/operations/ci-and-branch-policy.md`. Classify the full PR: ordinary documentation skips application checks and review requests; code, mixed changes, agent instructions, PF canon, workflow/configuration and environment templates require normal checks and exact-head review evidence. Never suppress a finding merely because its file ends in `.md`.
- Preserve failures and claim limits. Check the current head after corrections; earlier-head reviews do not certify later changes.

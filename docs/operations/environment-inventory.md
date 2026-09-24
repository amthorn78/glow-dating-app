# Environment inventory

The complete verified inventory is maintained in the [Claude handoff — environment-variable inventory](../continuity/claude-code-handoff.md#environment-variable-inventory), including exact code names, purpose, local/CI/deployment requirements, provisioning location and secret classification. This page is a stable entry point, not a duplicate table.

Safe local templates: [`services/api/.env.example`](../../services/api/.env.example) and [`apps/mobile/.env.example`](../../apps/mobile/.env.example). See [local setup](local-development.md) for their different loading behavior. The [configuration catalog](configuration.md) retains the detailed validator contract. Future provider slots are not active environment loaders; do not populate them until separately reviewed integration work introduces that behavior.
